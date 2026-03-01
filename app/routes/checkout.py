"""POST /api/checkout — Create Stripe Checkout session and return redirect URL."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from urllib.parse import urlparse
import validators

from app.database import get_db
from app.models import AuditJob
from app.schemas import CheckoutRequest, CheckoutResponse
from app.services.stripe_service import create_checkout_session

router = APIRouter()


@router.post("/api/checkout", response_model=CheckoutResponse)
def create_checkout(request: CheckoutRequest, db: Session = Depends(get_db)):
    # Validate URL
    url = request.url.strip()
    if not url.startswith("http"):
        url = f"https://{url}"

    if not validators.url(url):
        raise HTTPException(status_code=400, detail="Please enter a valid URL")

    # Validate email
    if not validators.email(request.email):
        raise HTTPException(status_code=400, detail="Please enter a valid email address")

    # Create job record (pending payment)
    job = AuditJob(url=url, email=request.email, status="awaiting_payment")
    db.add(job)
    db.commit()
    db.refresh(job)

    # Create Stripe session
    try:
        checkout_url, stripe_session_id = create_checkout_session(url, request.email, job.id)
        job.stripe_session_id = stripe_session_id
        db.commit()
    except Exception as e:
        db.delete(job)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Payment setup failed: {str(e)}")

    return CheckoutResponse(checkout_url=checkout_url, job_id=job.id)

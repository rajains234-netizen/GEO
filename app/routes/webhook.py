"""POST /api/webhook — Handle Stripe webhook events."""

from fastapi import APIRouter, Request, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.services.stripe_service import verify_webhook
from app.models import AuditJob
from app.tasks.audit import run_geo_audit

router = APIRouter()


@router.post("/api/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    try:
        event = verify_webhook(payload, sig_header)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        job_id = session.get("metadata", {}).get("job_id")

        if not job_id:
            return {"status": "ignored", "reason": "no job_id in metadata"}

        db = SessionLocal()
        try:
            job = db.query(AuditJob).filter(AuditJob.id == job_id).first()
            if job and job.status == "awaiting_payment":
                job.status = "pending"
                job.progress_message = "Payment confirmed. Queued for processing..."
                db.commit()

                # Dispatch background audit task
                run_geo_audit.delay(job_id)
        finally:
            db.close()

    return {"status": "ok"}

"""GET /api/download/{job_id}/{token} — Serve the generated PDF report."""

import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AuditJob

router = APIRouter()


@router.get("/api/download/{job_id}/{token}")
def download_report(job_id: str, token: str, db: Session = Depends(get_db)):
    job = db.query(AuditJob).filter(AuditJob.id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Report not found")

    if job.download_token != token:
        raise HTTPException(status_code=403, detail="Invalid download link")

    if job.status != "completed" or not job.pdf_path:
        raise HTTPException(status_code=400, detail="Report is not ready yet")

    if not os.path.exists(job.pdf_path):
        raise HTTPException(status_code=404, detail="Report file not found")

    filename = f"GEO-Report-{job.url.replace('https://', '').replace('http://', '').replace('/', '-').strip('-')}.pdf"

    return FileResponse(
        path=job.pdf_path,
        filename=filename,
        media_type="application/pdf",
    )

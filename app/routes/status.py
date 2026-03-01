"""GET /api/status/{job_id} — Poll job status for the frontend."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AuditJob
from app.schemas import JobStatusResponse
from app.config import get_settings

router = APIRouter()
settings = get_settings()


@router.get("/api/status/{job_id}", response_model=JobStatusResponse)
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    job = db.query(AuditJob).filter(AuditJob.id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    download_url = None
    if job.status == "completed" and job.download_token:
        download_url = f"{settings.api_url}/api/download/{job.id}/{job.download_token}"

    return JobStatusResponse(
        id=job.id,
        url=job.url,
        status=job.status,
        geo_score=job.geo_score,
        progress_message=job.progress_message,
        download_url=download_url,
        created_at=job.created_at,
        completed_at=job.completed_at,
        error_message=job.error_message,
    )

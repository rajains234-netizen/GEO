"""Celery background task for running GEO audits."""

import os
from datetime import datetime, timezone

from app.celery_app import celery_app
from app.database import SessionLocal
from app.models import AuditJob
from app.services.audit_runner import run_full_audit
from app.services.email_sender import send_report_email
from app.config import get_settings

settings = get_settings()


@celery_app.task(bind=True, max_retries=1)
def run_geo_audit(self, job_id: str):
    """Run a complete GEO audit as a background task."""
    db = SessionLocal()

    try:
        job = db.query(AuditJob).filter(AuditJob.id == job_id).first()
        if not job:
            return {"error": "Job not found"}

        # Update status to processing
        job.status = "processing"
        job.progress_message = "Starting GEO audit..."
        db.commit()

        # Progress callback to update DB
        def update_progress(message: str):
            job.progress_message = message
            db.commit()

        # Run the audit pipeline
        output_dir = os.path.join(settings.reports_dir, job_id)
        result = run_full_audit(job.url, output_dir, progress_callback=update_progress)

        # Update job with results
        job.status = "completed"
        job.pdf_path = result["pdf_path"]
        job.geo_score = result["geo_score"]
        job.progress_message = "Report complete!"
        job.completed_at = datetime.now(timezone.utc)
        db.commit()

        # Send email with report
        download_url = f"{settings.api_url}/api/download/{job.id}/{job.download_token}"
        brand_name = result.get("audit_json", {}).get("brand_name", "Your Site")

        send_report_email(
            to_email=job.email,
            brand_name=brand_name,
            geo_score=result["geo_score"],
            pdf_path=result["pdf_path"],
            download_url=download_url,
        )

        return {"status": "completed", "geo_score": result["geo_score"]}

    except Exception as e:
        # Mark job as failed
        if job:
            job.status = "failed"
            job.error_message = str(e)
            job.progress_message = "Audit failed. We'll retry or contact you."
            db.commit()

        # Retry once
        raise self.retry(exc=e, countdown=30)

    finally:
        db.close()

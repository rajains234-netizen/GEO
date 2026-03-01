import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Integer, DateTime, Text
from app.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class AuditJob(Base):
    __tablename__ = "audit_jobs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    url = Column(String(2048), nullable=False)
    email = Column(String(320), nullable=False)
    status = Column(String(20), nullable=False, default="pending")  # pending, processing, completed, failed
    stripe_session_id = Column(String(255), nullable=True)
    pdf_path = Column(String(512), nullable=True)
    download_token = Column(String(36), default=generate_uuid, nullable=False)
    geo_score = Column(Integer, nullable=True)
    progress_message = Column(String(255), nullable=True, default="Queued for processing")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)

from pydantic import BaseModel, HttpUrl, Field, ConfigDict
from typing import Optional
from datetime import datetime


class CheckoutRequest(BaseModel):
    url: str
    email: str


class CheckoutResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    checkout_url: str
    job_id: str = Field(serialization_alias='jobId')


class JobStatusResponse(BaseModel):
    id: str
    url: str
    status: str
    geo_score: Optional[int] = None
    progress_message: Optional[str] = None
    download_url: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

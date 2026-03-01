"""FastAPI application — GEO Score SaaS API."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.database import init_db
from app.config import get_settings
from app.routes import checkout, webhook, status, download

settings = get_settings()

app = FastAPI(
    title="GEO Score API",
    description="AI Search Visibility Audit — Pay-per-report SaaS",
    version="1.0.0",
)

# CORS — allow React frontend in dev and production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.base_url,
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(checkout.router, tags=["checkout"])
app.include_router(webhook.router, tags=["webhook"])
app.include_router(status.router, tags=["status"])
app.include_router(download.router, tags=["download"])


@app.on_event("startup")
def startup():
    init_db()
    os.makedirs(settings.reports_dir, exist_ok=True)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "geo-score-api"}


@app.get("/api/config")
def public_config():
    """Return non-secret config for the frontend."""
    return {
        "price_cents": settings.report_price_cents,
        "price_display": f"${settings.report_price_cents / 100:.0f}",
    }

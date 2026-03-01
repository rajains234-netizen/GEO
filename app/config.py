from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    # Stripe
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_price_id: str = ""
    report_price_cents: int = 4900  # $49.00

    # Redis & Celery
    redis_url: str = "redis://localhost:6379/0"

    # Database
    database_url: str = "sqlite:///./geo_saas.db"

    # Email (SendGrid)
    sendgrid_api_key: str = ""
    from_email: str = "reports@geoscore.ai"

    # Claude AI (Anthropic) — for deep analysis
    anthropic_api_key: str = ""

    # App
    base_url: str = "http://localhost:5173"
    api_url: str = "http://localhost:8000"
    reports_dir: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")
    scripts_dir: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache()
def get_settings() -> Settings:
    return Settings()

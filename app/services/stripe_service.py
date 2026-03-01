"""Stripe Checkout integration for pay-per-report."""

import stripe
from app.config import get_settings

settings = get_settings()
stripe.api_key = settings.stripe_secret_key


def create_checkout_session(url: str, email: str, job_id: str) -> str:
    """
    Create a Stripe Checkout session for a GEO report purchase.
    Returns the checkout URL to redirect the customer to.
    """
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        customer_email=email,
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "unit_amount": settings.report_price_cents,
                    "product_data": {
                        "name": "GEO Audit Report",
                        "description": f"Comprehensive AI Search Visibility Report for {url}",
                    },
                },
                "quantity": 1,
            }
        ],
        metadata={
            "url": url,
            "email": email,
            "job_id": job_id,
        },
        success_url=f"{settings.base_url}/status/{job_id}?payment=success",
        cancel_url=f"{settings.base_url}/?cancelled=true",
    )
    return session.url, session.id


def verify_webhook(payload: bytes, sig_header: str) -> dict:
    """Verify and parse a Stripe webhook event."""
    event = stripe.Webhook.construct_event(
        payload, sig_header, settings.stripe_webhook_secret
    )
    return event

"""Billing service — Stripe integration (stub-ready)."""

from __future__ import annotations

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger("billing_service")

PLAN_LIMITS = {
    "free": {"matches_per_hour": 10, "rewrites_per_hour": 5},
    "pro": {"matches_per_hour": 100, "rewrites_per_hour": 50},
    "enterprise": {"matches_per_hour": 1000, "rewrites_per_hour": 500},
}


async def check_usage_limit(tenant_id: str, plan: str, event_type: str) -> bool:
    """Check if the tenant has exceeded their usage limit. Returns True if OK."""
    # Stub — always allows in dev mode
    if not settings.is_production:
        return True
    return True


async def create_checkout_session(plan: str, tenant_id: str) -> str | None:
    """Create a Stripe checkout session (stub)."""
    if not settings.STRIPE_SECRET_KEY:
        logger.info("billing.checkout_stub", plan=plan)
        return None
    return "https://checkout.stripe.com/stub"

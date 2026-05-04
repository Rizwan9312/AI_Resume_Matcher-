"""Billing API routes — Stripe checkout, portal, status, webhook (stub-ready)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db_session
from app.dependencies import get_current_user
from app.models.user import User
from app.utils.logger import get_logger

logger = get_logger("billing_api")

router = APIRouter(prefix="/billing", tags=["Billing"])


@router.post("/checkout")
async def create_checkout(
    body: dict,
    current_user: User = Depends(get_current_user),
):
    """Create a Stripe checkout session (stub)."""
    if not settings.STRIPE_SECRET_KEY:
        return {"checkout_url": None, "message": "Billing not configured — running in free mode"}
    # Stripe integration would go here
    return {"checkout_url": "https://checkout.stripe.com/stub"}


@router.get("/portal")
async def get_portal(current_user: User = Depends(get_current_user)):
    """Get Stripe customer portal URL (stub)."""
    if not settings.STRIPE_SECRET_KEY:
        return {"portal_url": None, "message": "Billing not configured"}
    return {"portal_url": "https://billing.stripe.com/stub"}


@router.get("/status")
async def billing_status(current_user: User = Depends(get_current_user)):
    """Get current plan status."""
    return {
        "plan": "free",
        "status": "active",
        "current_period_end": None,
        "usage": {"matches_used": 0, "matches_limit": 10},
    }


@router.post("/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events (stub)."""
    if not settings.STRIPE_WEBHOOK_SECRET:
        return {"received": True, "message": "Webhook handler not configured"}
    logger.info("billing.webhook_received")
    return {"received": True}

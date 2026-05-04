"""Notification service — email sending abstraction (stub-ready)."""

from __future__ import annotations

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger("notification_service")


async def send_match_complete_notification(user_email: str, match_id: str, score: float) -> None:
    """Send match completion notification."""
    try:
        from app.workers.notification_tasks import send_match_complete_email
        send_match_complete_email.delay(user_email, match_id, score)
    except Exception as exc:
        logger.warning("notification.dispatch_failed", error=str(exc))

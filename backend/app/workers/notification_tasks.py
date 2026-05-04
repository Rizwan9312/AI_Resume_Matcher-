"""Notification tasks — email sending via SendGrid (stub-ready)."""

from __future__ import annotations

from app.workers.celery_app import celery_app
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger("notification_tasks")


@celery_app.task(name="notification.send_email")
def send_email_task(to_email: str, subject: str, html_content: str) -> dict:
    """Send an email via SendGrid (stub if not configured)."""
    if not settings.SENDGRID_API_KEY:
        logger.info("notification.email_stub", to=to_email, subject=subject)
        return {"status": "stub", "message": "SendGrid not configured"}

    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail

        message = Mail(
            from_email=settings.FROM_EMAIL,
            to_emails=to_email,
            subject=subject,
            html_content=html_content,
        )
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
        logger.info("notification.email_sent", to=to_email, status=response.status_code)
        return {"status": "sent", "status_code": response.status_code}
    except Exception as exc:
        logger.error("notification.email_failed", to=to_email, error=str(exc))
        return {"status": "failed", "error": str(exc)}


@celery_app.task(name="notification.match_complete")
def send_match_complete_email(user_email: str, match_id: str, final_score: float) -> dict:
    """Send a match-complete notification email."""
    subject = f"Your Resume Match is Ready — Score: {final_score}"
    html = f"""
    <h2>Your resume match analysis is complete!</h2>
    <p>Final Score: <strong>{final_score}/100</strong></p>
    <p><a href="{settings.FRONTEND_URL}/match/{match_id}">View Full Results →</a></p>
    """
    return send_email_task(user_email, subject, html)

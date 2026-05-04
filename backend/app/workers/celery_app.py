"""Celery application configuration."""

import sys

from celery import Celery

from app.config import settings

celery_app = Celery(
    "resume_matcher",
    broker=settings.celery_broker,
    backend=settings.celery_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    # ── Windows fix: prefork doesn't work on Windows/Python 3.13 ──
    worker_pool="solo" if sys.platform == "win32" else "prefork",
    # ── Task routing ─────────────────────────────────────────────
    task_routes={
        "app.workers.match_tasks.*": {"queue": "matches"},
        "app.workers.rewrite_tasks.*": {"queue": "rewrites"},
        "app.workers.notification_tasks.*": {"queue": "notifications"},
    },
)

celery_app.autodiscover_tasks([
    "app.workers.match_tasks",
    "app.workers.rewrite_tasks",
    "app.workers.notification_tasks",
])
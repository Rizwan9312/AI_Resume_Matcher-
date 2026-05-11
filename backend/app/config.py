"""Application configuration — pydantic-settings with env var validation."""

from __future__ import annotations

import secrets
from enum import Enum
from typing import Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """All configuration loaded from environment variables.

    Application refuses to start if required secrets are missing.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── App ──────────────────────────────────────────────────────
    APP_NAME: str = "AI Resume Matcher"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    LOG_LEVEL: str = "info"
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ADMIN_EMAIL: str = "admin@resumematcher.com"
    ADMIN_PASSWORD: str = "admin123"

    # ── Database ─────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/resume_matcher"
    DATABASE_ECHO: bool = False

    # ── Redis ────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── JWT ──────────────────────────────────────────────────────
    JWT_SECRET_KEY: str = "dev-jwt-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # ── AI / ML ──────────────────────────────────────────────────
    OPENROUTER_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    LLM_MODEL: str = "qwen/qwen-2.5-coder-32b-instruct"
    BERT_MODEL_NAME: str = "all-MiniLM-L6-v2"

    # ── JSearch (LinkedIn Jobs) ──────────────────────────────────
    JSEARCH_API_KEY: str = ""

    # ── File Storage ─────────────────────────────────────────────
    STORAGE_BACKEND: str = "local"  # "local" or "s3"
    LOCAL_UPLOAD_DIR: str = "uploads"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: Optional[str] = None
    MAX_FILE_SIZE_MB: int = 10

    # ── Email (SendGrid) — stub-ready ────────────────────────────
    SENDGRID_API_KEY: Optional[str] = None
    FROM_EMAIL: str = "noreply@resumematcher.com"

    # ── Stripe — stub-ready ──────────────────────────────────────
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    STRIPE_PRO_PRICE_ID: Optional[str] = None
    STRIPE_ENTERPRISE_PRICE_ID: Optional[str] = None

    # ── CORS ─────────────────────────────────────────────────────
    FRONTEND_URL: str = "http://localhost:3000"

    # ── Celery ───────────────────────────────────────────────────
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None

    # ── Sentry ───────────────────────────────────────────────────
    SENTRY_DSN: Optional[str] = None

    @property
    def celery_broker(self) -> str:
        return self.CELERY_BROKER_URL or self.REDIS_URL

    @property
    def celery_backend(self) -> str:
        return self.CELERY_RESULT_BACKEND or self.REDIS_URL

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == Environment.PRODUCTION

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        allowed = {"debug", "info", "warning", "error", "critical"}
        if v.lower() not in allowed:
            msg = f"LOG_LEVEL must be one of {allowed}"
            raise ValueError(msg)
        return v.lower()


# Module-level singleton — import `settings` anywhere
settings = Settings()

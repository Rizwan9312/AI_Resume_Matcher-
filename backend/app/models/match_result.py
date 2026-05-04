"""MatchResult model — stores scores and analysis from the ML pipeline."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, TimestampMixin, generate_uuid


class MatchStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETE = "complete"
    FAILED = "failed"


class MatchResult(Base, TimestampMixin):
    """Match result — full pipeline output with all scoring dimensions."""

    __tablename__ = "match_results"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=generate_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    resume_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("resumes.id"), nullable=False)
    job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("job_descriptions.id"), nullable=False)

    status: Mapped[MatchStatus] = mapped_column(
        Enum(MatchStatus, name="match_status"),
        default=MatchStatus.PENDING,
    )
    celery_task_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Scores
    bert_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    tfidf_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    keyword_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    llm_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    final_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)

    # Role detection
    role_detected: Mapped[str | None] = mapped_column(String(50), nullable=True)
    weights_used: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    score_breakdown: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Keywords
    matched_keywords: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    missing_keywords: Mapped[list | None] = mapped_column(JSONB, nullable=True)

    # Section scores and LLM verdict
    section_scores: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    llm_verdict: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    feedback_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timing
    processing_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),    # ← FIXED
        nullable=True,
    )

    # Relationships
    user = relationship("User", back_populates="match_results")
    resume = relationship("Resume", back_populates="match_results")
    job_description = relationship("JobDescription", back_populates="match_results")
    rewrite_sessions = relationship("RewriteSession", back_populates="match_result")
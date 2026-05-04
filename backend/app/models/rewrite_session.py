"""RewriteSession model — AI bullet rewrite sessions."""

from __future__ import annotations

import enum
import uuid

from sqlalchemy import Enum, ForeignKey, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, TimestampMixin, generate_uuid


class RewriteStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETE = "complete"
    FAILED = "failed"


class RewriteSession(Base, TimestampMixin):
    """Bullet rewrite session — stores original + rewritten bullet variants."""

    __tablename__ = "rewrite_sessions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=generate_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    match_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("match_results.id"), nullable=True
    )
    resume_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("resumes.id"), nullable=False)
    jd_text: Mapped[str] = mapped_column(Text, nullable=False)

    status: Mapped[RewriteStatus] = mapped_column(
        Enum(RewriteStatus, name="rewrite_status"),
        default=RewriteStatus.PENDING,
    )
    celery_task_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    bullet_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    weak_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rewrites: Mapped[dict | list | None] = mapped_column(JSONB, nullable=True)

    # Relationships
    match_result = relationship("MatchResult", back_populates="rewrite_sessions")

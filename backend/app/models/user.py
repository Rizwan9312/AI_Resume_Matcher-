"""User model — authentication and profile."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, SoftDeleteMixin, TimestampMixin, generate_uuid


class UserRole(str, enum.Enum):
    JOB_SEEKER = "job_seeker"
    RECRUITER = "recruiter"
    ADMIN = "admin"


class User(Base, TimestampMixin, SoftDeleteMixin):
    """Platform user — belongs to a tenant."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=generate_uuid)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role"),
        default=UserRole.JOB_SEEKER,
    )
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    is_verified: Mapped[bool] = mapped_column(default=False, server_default="false")
    google_id: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True)
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),         # ← FIXED
        nullable=True,
    )

    # Relationships
    tenant = relationship("Tenant", back_populates="users", lazy="selectin")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    resumes = relationship("Resume", back_populates="user", lazy="selectin")
    job_descriptions = relationship("JobDescription", back_populates="user", lazy="selectin")
    match_results = relationship("MatchResult", back_populates="user", lazy="selectin")


class RefreshToken(Base, TimestampMixin):
    """Refresh token storage — hashed, with revocation support."""

    __tablename__ = "refresh_tokens"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=generate_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    token_hash: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),         # ← FIXED
        nullable=False,
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),         # ← FIXED
        nullable=True,
    )

    # Relationships
    user = relationship("User", back_populates="refresh_tokens")
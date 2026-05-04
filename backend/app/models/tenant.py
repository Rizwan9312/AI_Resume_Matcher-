"""Tenant model — multi-tenant organization."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import Enum, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, SoftDeleteMixin, TimestampMixin, generate_uuid


class PlanType(str, enum.Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class Tenant(Base, TimestampMixin, SoftDeleteMixin):
    """Organization / workspace — row-level isolation."""

    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    plan: Mapped[PlanType] = mapped_column(
        Enum(PlanType, name="plan_type"),
        default=PlanType.FREE,
    )
    api_key_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relationships
    users = relationship("User", back_populates="tenant", lazy="selectin")
    subscription = relationship("Subscription", back_populates="tenant", uselist=False)

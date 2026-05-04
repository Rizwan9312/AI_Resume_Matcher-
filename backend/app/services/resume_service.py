"""Resume service — business logic for resume management."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.resume import Resume
from app.utils.logger import get_logger

logger = get_logger("resume_service")


async def get_resume_by_id(session: AsyncSession, resume_id: uuid.UUID) -> Resume | None:
    """Fetch a resume by ID."""
    result = await session.execute(
        select(Resume).where(Resume.id == resume_id, Resume.deleted_at.is_(None))
    )
    return result.scalar_one_or_none()


async def get_resumes_for_user(session: AsyncSession, user_id: uuid.UUID) -> list[Resume]:
    """Get all resumes for a user."""
    result = await session.execute(
        select(Resume)
        .where(Resume.user_id == user_id, Resume.deleted_at.is_(None))
        .order_by(Resume.created_at.desc())
    )
    return list(result.scalars().all())

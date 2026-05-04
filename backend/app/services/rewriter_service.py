"""Rewriter service — business logic for rewrite sessions."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rewrite_session import RewriteSession
from app.utils.logger import get_logger

logger = get_logger("rewriter_service")


async def get_session_by_id(session: AsyncSession, session_id: uuid.UUID) -> RewriteSession | None:
    result = await session.execute(select(RewriteSession).where(RewriteSession.id == session_id))
    return result.scalar_one_or_none()

"""Match service — business logic for match operations."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.match_result import MatchResult
from app.utils.logger import get_logger

logger = get_logger("match_service")


async def get_match_by_id(session: AsyncSession, match_id: uuid.UUID) -> MatchResult | None:
    result = await session.execute(select(MatchResult).where(MatchResult.id == match_id))
    return result.scalar_one_or_none()

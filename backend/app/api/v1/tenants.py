"""Admin API routes — platform management (admin role required)."""

from __future__ import annotations

import uuid as uuid_mod
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_session
from app.dependencies import require_role
from app.models.match_result import MatchResult, MatchStatus
from app.models.tenant import Tenant
from app.models.user import User
from app.utils.logger import get_logger

logger = get_logger("admin_api")

router = APIRouter(prefix="/admin", tags=["Admin"])

admin_required = require_role("admin")


@router.get("/users")
async def list_users(
    current_user: User = Depends(admin_required),
    session: AsyncSession = Depends(get_db_session),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    tenant_id: Optional[str] = None,
):
    """List all users (admin only)."""
    query = select(User).where(User.deleted_at.is_(None))
    if tenant_id:
        query = query.where(User.tenant_id == uuid_mod.UUID(tenant_id))
    count_q = select(func.count()).select_from(query.subquery())
    total = (await session.execute(count_q)).scalar() or 0
    query = query.offset((page - 1) * limit).limit(limit)
    result = await session.execute(query)
    users = result.scalars().all()
    return {
        "users": [{"id": str(u.id), "email": u.email, "role": u.role.value, "full_name": u.full_name} for u in users],
        "total": total,
    }


@router.patch("/users/{user_id}")
async def update_user_role(
    user_id: str,
    body: dict,
    current_user: User = Depends(admin_required),
    session: AsyncSession = Depends(get_db_session),
):
    """Update a user's role (admin only)."""
    result = await session.execute(select(User).where(User.id == uuid_mod.UUID(user_id)))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(404, detail={"code": "not_found", "message": "User not found"})
    if "role" in body:
        user.role = body["role"]
    return {"id": str(user.id), "email": user.email, "role": user.role.value}


@router.get("/tenants")
async def list_tenants(
    current_user: User = Depends(admin_required),
    session: AsyncSession = Depends(get_db_session),
):
    """List all tenants (admin only)."""
    result = await session.execute(select(Tenant).where(Tenant.deleted_at.is_(None)))
    tenants = result.scalars().all()
    return {"tenants": [{"id": str(t.id), "name": t.name, "slug": t.slug, "plan": t.plan.value} for t in tenants]}


@router.get("/stats")
async def platform_stats(
    current_user: User = Depends(admin_required),
    session: AsyncSession = Depends(get_db_session),
):
    """Get platform analytics (admin only)."""
    from datetime import datetime, timezone, timedelta
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    total_users = (await session.execute(select(func.count()).select_from(User).where(User.deleted_at.is_(None)))).scalar() or 0
    total_matches = (await session.execute(select(func.count()).select_from(MatchResult))).scalar() or 0
    matches_today = (await session.execute(
        select(func.count()).select_from(MatchResult).where(MatchResult.created_at >= today)
    )).scalar() or 0
    avg_result = await session.execute(
        select(func.avg(MatchResult.final_score)).where(MatchResult.status == MatchStatus.COMPLETE)
    )
    avg_score = round(float(avg_result.scalar() or 0), 1)

    return {"total_users": total_users, "total_matches": total_matches, "matches_today": matches_today, "avg_score": avg_score}

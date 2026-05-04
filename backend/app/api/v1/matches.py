"""Match API routes — create, status poll, get result, list."""

from __future__ import annotations

import uuid as uuid_mod
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_session
from app.dependencies import get_current_user
from app.models.match_result import MatchResult, MatchStatus
from app.models.resume import Resume
from app.models.job_description import JobDescription
from app.models.user import User
from app.schemas.match import MatchCreateRequest, MatchListResponse, MatchResponse
from app.utils.logger import get_logger

logger = get_logger("matches_api")

router = APIRouter(prefix="/matches", tags=["Matches"])


@router.post("", status_code=status.HTTP_202_ACCEPTED)
async def create_match(
    body: MatchCreateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """Start a new match analysis (async via Celery)."""

    logger.info(
        "match.create_attempt",
        resume_id=str(body.resume_id),
        job_id=str(body.job_id),
        current_user_id=str(current_user.id),
    )

    # Verify resume exists and belongs to user
    resume_result = await session.execute(
        select(Resume).where(
            Resume.id == body.resume_id,
            Resume.user_id == current_user.id,
            Resume.deleted_at.is_(None),
        )
    )
    resume = resume_result.scalar_one_or_none()
    if not resume:
        # Debug: check if resume exists at all regardless of owner
        any_resume_result = await session.execute(
            select(Resume).where(Resume.id == body.resume_id)
        )
        found = any_resume_result.scalar_one_or_none()
        logger.error(
            "match.resume_not_found",
            resume_id=str(body.resume_id),
            current_user_id=str(current_user.id),
            resume_exists_in_db=found is not None,
            resume_owner_id=str(found.user_id) if found else None,
            resume_deleted=str(found.deleted_at) if found else None,
        )
        raise HTTPException(404, detail={"code": "resume_not_found", "message": "Resume not found"})

    # Verify JD exists and belongs to user
    job_result = await session.execute(
        select(JobDescription).where(
            JobDescription.id == body.job_id,
            JobDescription.user_id == current_user.id,
        )
    )
    job = job_result.scalar_one_or_none()
    if not job:
        # Debug: check if job exists at all
        any_job_result = await session.execute(
            select(JobDescription).where(JobDescription.id == body.job_id)
        )
        found_job = any_job_result.scalar_one_or_none()
        logger.error(
            "match.job_not_found",
            job_id=str(body.job_id),
            current_user_id=str(current_user.id),
            job_exists_in_db=found_job is not None,
            job_owner_id=str(found_job.user_id) if found_job else None,
        )
        raise HTTPException(404, detail={"code": "job_not_found", "message": "Job description not found"})

    # Create match record
    match = MatchResult(
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        resume_id=body.resume_id,
        job_id=body.job_id,
        status=MatchStatus.PENDING,
    )
    session.add(match)
    await session.flush()

    # Dispatch Celery task
    try:
        from app.workers.match_tasks import run_match_pipeline
        task = run_match_pipeline.delay(str(match.id))
        match.celery_task_id = task.id
    except Exception as exc:
        logger.warning("celery.dispatch_failed", error=str(exc))

    logger.info("match.created", match_id=str(match.id))
    return {"match_id": str(match.id), "status": "pending"}


@router.get("/{match_id}", response_model=MatchResponse)
async def get_match(
    match_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """Get match result (used for polling)."""
    try:
        mid = uuid_mod.UUID(match_id)
    except ValueError:
        raise HTTPException(404, detail={"code": "not_found", "message": "Match not found"})

    result = await session.execute(
        select(MatchResult).where(MatchResult.id == mid)
    )
    match = result.scalar_one_or_none()

    if not match:
        raise HTTPException(404, detail={"code": "not_found", "message": "Match not found"})
    if match.user_id != current_user.id:
        raise HTTPException(403, detail={"code": "forbidden", "message": "Access denied"})

    return MatchResponse.model_validate(match)


@router.get("", response_model=MatchListResponse)
async def list_matches(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    match_status: Optional[str] = Query(None, alias="status"),
):
    """List all matches for the current user with pagination."""
    query = select(MatchResult).where(MatchResult.user_id == current_user.id)

    if match_status:
        query = query.where(MatchResult.status == match_status)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await session.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(MatchResult.created_at.desc()).offset((page - 1) * limit).limit(limit)
    result = await session.execute(query)
    matches = result.scalars().all()

    return MatchListResponse(
        matches=[MatchResponse.model_validate(m) for m in matches],
        total=total,
        page=page,
        limit=limit,
    )
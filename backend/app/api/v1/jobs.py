"""Job Description API routes — create, list, get."""

from __future__ import annotations

import re
import uuid as uuid_mod

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_session
from app.dependencies import get_current_user
from app.models.job_description import JobDescription
from app.models.user import User
from app.schemas.job import JobCreateRequest, JobListResponse, JobResponse
from app.utils.logger import get_logger

logger = get_logger("jobs_api")

router = APIRouter(prefix="/jobs", tags=["Job Descriptions"])


def _strip_html(text: str) -> str:
    """Strip HTML tags from text."""
    return re.sub(r"<[^>]+>", "", text)


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    body: JobCreateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """Save a job description."""
    clean_text = _strip_html(body.raw_text)

    job = JobDescription(
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        title=body.title,
        company=body.company,
        raw_text=clean_text,
        source_url=body.source_url,
    )
    session.add(job)
    await session.commit()      # ← changed from flush() to commit()
    await session.refresh(job)  # ← reload DB-generated fields

    logger.info("job.created", job_id=str(job.id))
    return JobResponse.model_validate(job)


@router.get("", response_model=JobListResponse)
async def list_jobs(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """List all saved job descriptions for the current user."""
    result = await session.execute(
        select(JobDescription)
        .where(JobDescription.user_id == current_user.id)
        .order_by(JobDescription.created_at.desc())
    )
    jobs = result.scalars().all()
    return JobListResponse(jobs=[JobResponse.model_validate(j) for j in jobs])


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """Get a specific job description by ID."""
    try:
        jid = uuid_mod.UUID(job_id)
    except ValueError:
        raise HTTPException(404, detail={"code": "not_found", "message": "Job not found"})

    result = await session.execute(
        select(JobDescription).where(JobDescription.id == jid)
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(404, detail={"code": "not_found", "message": "Job not found"})
    if job.user_id != current_user.id:
        raise HTTPException(403, detail={"code": "forbidden", "message": "Access denied"})

    return JobResponse.model_validate(job)
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
from app.models.match_result import MatchResult
from app.schemas.job import (
    JobCreateRequest,
    JobListResponse,
    JobResponse,
    JobUpdateTagsRequest,
    JobLibraryItem,
    JobLibraryResponse,
    KeywordExtractRequest,
    KeywordExtractResponse
)
from app.ml.keyword_extractor import extract_all_keywords
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
        industry_tag=body.industry_tag,
        role_tag=body.role_tag,
    )
    session.add(job)
    await session.commit()
    await session.refresh(job)

    logger.info("job.created", job_id=str(job.id))
    return JobResponse.model_validate(job)


@router.get("/library", response_model=JobLibraryResponse)
async def list_job_library(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """List all saved job descriptions with their best match scores."""
    result = await session.execute(
        select(JobDescription)
        .where(JobDescription.user_id == current_user.id)
        .order_by(JobDescription.created_at.desc())
    )
    jobs = result.scalars().all()

    if not jobs:
        return JobLibraryResponse(jobs=[])

    # Fetch all matches for these jobs
    job_ids = [j.id for j in jobs]
    matches_result = await session.execute(
        select(MatchResult.job_id, MatchResult.resume_id, MatchResult.final_score)
        .where(
            MatchResult.job_id.in_(job_ids),
            MatchResult.user_id == current_user.id,
            MatchResult.status == "complete"
        )
    )
    matches = matches_result.all()

    # Calculate best score and best resume id per job
    best_matches = {}
    for job_id, resume_id, score in matches:
        if job_id not in best_matches or (score is not None and score > best_matches[job_id]["score"]):
            best_matches[job_id] = {"score": score, "resume_id": resume_id}

    items = []
    for j in jobs:
        item = JobLibraryItem.model_validate(j)
        if j.id in best_matches:
            item.best_score = best_matches[j.id]["score"]
            item.best_resume_id = best_matches[j.id]["resume_id"]
        items.append(item)

    return JobLibraryResponse(jobs=items)


@router.patch("/{job_id}/tags", response_model=JobResponse)
async def update_job_tags(
    job_id: str,
    body: JobUpdateTagsRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """Update industry and role tags for a job description."""
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

    if body.industry_tag is not None:
        job.industry_tag = body.industry_tag
    if body.role_tag is not None:
        job.role_tag = body.role_tag

    await session.commit()
    await session.refresh(job)

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


@router.post("/extract-keywords", response_model=KeywordExtractResponse)
async def extract_keywords(
    body: KeywordExtractRequest,
    current_user: User = Depends(get_current_user),
):
    """Extract keywords synchronously from job description text."""
    try:
        result = extract_all_keywords(body.raw_text)
        return KeywordExtractResponse(keywords=result.get("all_keywords", []))
    except Exception as exc:
        logger.error("jobs.extract_keywords_failed", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to extract keywords",
        )
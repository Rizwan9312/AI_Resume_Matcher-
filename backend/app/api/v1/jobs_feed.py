"""Jobs Feed API — serves job recommendations and triggers background fetches."""

import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.database import get_db_session
from app.models.job_recommendation import JobRecommendation
from app.models.resume import Resume
from app.models.match_result import MatchResult
from app.models.job_description import JobDescription
from app.dependencies import get_current_user
from app.workers.linkedin_tasks import fetch_linkedin_jobs

router = APIRouter(prefix="/jobs-feed", tags=["jobs-feed"])


@router.get("/")
async def get_job_recommendations(
    resume_id: str = Query(None),
    match_result_id: str = Query(None),
    limit: int = Query(10, le=20),
    db: AsyncSession = Depends(get_db_session),
    current_user=Depends(get_current_user),
):
    """Returns cached job recommendations ordered by relevance score."""
    q = (
        select(JobRecommendation)
        .where(
            JobRecommendation.user_id == current_user.id,
            JobRecommendation.is_dismissed == False,
        )
        .order_by(JobRecommendation.relevance_score.desc())
        .limit(limit)
    )

    if match_result_id:
        q = q.where(JobRecommendation.match_result_id == uuid.UUID(match_result_id))
    elif resume_id:
        q = q.where(JobRecommendation.resume_id == uuid.UUID(resume_id))

    result = await db.execute(q)
    rows = result.scalars().all()

    # Serialize to dicts for JSON response
    return [
        {
            "id": str(r.id),
            "job_id": r.job_id,
            "job_title": r.job_title,
            "employer_name": r.employer_name,
            "employer_logo": r.employer_logo,
            "job_publisher": r.job_publisher,
            "job_employment_type": r.job_employment_type,
            "job_location": r.job_location,
            "job_apply_link": r.job_apply_link,
            "job_posted_at": r.job_posted_at.isoformat() if r.job_posted_at else None,
            "job_salary_min": r.job_salary_min,
            "job_salary_max": r.job_salary_max,
            "job_salary_currency": r.job_salary_currency,
            "relevance_score": r.relevance_score,
            "is_dismissed": r.is_dismissed,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "expires_at": r.expires_at.isoformat() if r.expires_at else None,
            "resume_id": str(r.resume_id),
            "match_result_id": str(r.match_result_id) if r.match_result_id else None,
        }
        for r in rows
    ]


@router.post("/trigger")
async def trigger_job_fetch(
    resume_id: str,
    match_result_id: str = None,
    db: AsyncSession = Depends(get_db_session),
    current_user=Depends(get_current_user),
):
    """
    Queues a background job fetch for the given resume.
    Called automatically from pipeline hooks and also from the frontend on mount.
    """
    resume = await db.get(Resume, uuid.UUID(resume_id))
    if not resume:
        return {"status": "error", "message": "Resume not found"}

    job_desc_text = None
    match_data = None

    if match_result_id:
        mr = await db.get(MatchResult, uuid.UUID(match_result_id))
        if mr:
            jd = await db.get(JobDescription, mr.job_id)
            job_desc_text = jd.raw_text if jd else None
            match_data = {
                "missing_keywords": mr.missing_keywords or [],
                "final_score": float(mr.final_score) if mr.final_score else None,
            }

    fetch_linkedin_jobs.delay(
        user_id=str(current_user.id),
        resume_id=resume_id,
        resume_text=resume.parsed_text or "",
        job_description_text=job_desc_text,
        match_result_id=match_result_id,
        match_data=match_data,
    )
    return {"status": "queued"}


@router.patch("/{recommendation_id}/dismiss")
async def dismiss_recommendation(
    recommendation_id: str,
    db: AsyncSession = Depends(get_db_session),
    current_user=Depends(get_current_user),
):
    await db.execute(
        update(JobRecommendation)
        .where(JobRecommendation.id == uuid.UUID(recommendation_id))
        .where(JobRecommendation.user_id == current_user.id)
        .values(is_dismissed=True)
    )
    await db.commit()
    return {"status": "dismissed"}

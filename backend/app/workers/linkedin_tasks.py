"""LinkedIn job fetch Celery task — triggered after match or rewrite completion."""

import asyncio
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, delete

from app.workers.celery_app import celery_app
from app.database import async_session_factory
from app.models.job_recommendation import JobRecommendation
from app.services.job_query_extractor import extract_job_queries
from app.services.jsearch_client import search_jobs
from app.services.job_relevance_scorer import score_jobs_against_resume
from app.utils.logger import get_logger

logger = get_logger("linkedin_tasks")


@celery_app.task(name="tasks.fetch_linkedin_jobs", bind=True, max_retries=2)
def fetch_linkedin_jobs(
    self,
    user_id: str,
    resume_id: str,
    resume_text: str,
    job_description_text: str = None,
    match_result_id: str = None,
    match_data: dict = None,
):
    """
    Background task triggered after match analysis or rewrite completion.
    Fetches live job postings, scores them, and stores top 20 in the DB.
    """
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(_run(
                user_id, resume_id, resume_text,
                job_description_text, match_result_id, match_data
            ))
        finally:
            loop.run_until_complete(asyncio.sleep(0))
            loop.close()
            asyncio.set_event_loop(None)
    except Exception as exc:
        logger.error("linkedin_tasks.failed", error=str(exc))
        raise self.retry(exc=exc, countdown=30)


async def _run(
    user_id, resume_id, resume_text,
    job_description_text, match_result_id, match_data
):
    # 1. Ask LLM to extract search terms from the resume
    query_params = await extract_job_queries(resume_text, job_description_text, match_data)
    logger.info("linkedin_tasks.query_extracted", query=query_params.get("primary_job_title"))

    # 2. Fetch live jobs from JSearch
    raw_jobs = await search_jobs(query_params, num_pages=2)
    if not raw_jobs:
        logger.info("linkedin_tasks.no_jobs_found")
        return

    # 3. Score each job against the resume
    scored_jobs = score_jobs_against_resume(resume_text, raw_jobs)
    logger.info("linkedin_tasks.scored", count=len(scored_jobs))

    # 4. Persist top 20, deduplicating by job_id
    async with async_session_factory() as session:

        # Remove expired recommendations for this user
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        await session.execute(
            delete(JobRecommendation).where(
                JobRecommendation.user_id == uuid.UUID(user_id),
                JobRecommendation.expires_at < now,
            )
        )

        expires = now + timedelta(hours=6)

        for job in scored_jobs[:20]:
            existing = await session.execute(
                select(JobRecommendation).where(
                    JobRecommendation.job_id == job["job_id"]
                )
            )
            if existing.scalar_one_or_none():
                continue

            rec = JobRecommendation(
                user_id=uuid.UUID(user_id),
                resume_id=uuid.UUID(resume_id),
                match_result_id=uuid.UUID(match_result_id) if match_result_id else None,
                expires_at=expires,
                job_id=job["job_id"],
                job_title=job["job_title"],
                employer_name=job["employer_name"],
                employer_logo=job["employer_logo"],
                job_publisher=job["job_publisher"],
                job_employment_type=job["job_employment_type"],
                job_location=job["job_location"],
                job_description=job["job_description"],
                job_apply_link=job["job_apply_link"],
                job_posted_at=job["job_posted_at"].replace(tzinfo=None) if job.get("job_posted_at") and hasattr(job["job_posted_at"], 'replace') else job.get("job_posted_at"),
                job_salary_min=job["job_salary_min"],
                job_salary_max=job["job_salary_max"],
                job_salary_currency=job["job_salary_currency"],
                relevance_score=job["relevance_score"],
                raw_data=job["raw_data"],
            )
            session.add(rec)

        await session.commit()
        logger.info("linkedin_tasks.saved", user_id=user_id)

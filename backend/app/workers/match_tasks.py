"""Match pipeline Celery task — full async scoring pipeline."""

from __future__ import annotations

import asyncio
import time
from datetime import datetime, timezone

from app.workers.celery_app import celery_app
from app.utils.logger import get_logger

logger = get_logger("match_tasks")


@celery_app.task(name="match.run_pipeline", bind=True, max_retries=2)
def run_match_pipeline(self, match_id: str) -> dict:
    """Execute the full match scoring pipeline."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_run_pipeline(match_id))
    finally:
        loop.run_until_complete(_cleanup())
        loop.close()
        asyncio.set_event_loop(None)


async def _cleanup():
    """Allow pending async tasks to complete before closing loop."""
    await asyncio.sleep(0)


async def _run_pipeline(match_id: str) -> dict:
    """Async pipeline execution with a fresh engine per task."""
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
    from sqlalchemy import select

    from app.config import settings
    from app.models.match_result import MatchResult, MatchStatus
    from app.models.resume import Resume
    from app.models.job_description import JobDescription
    from app.ml.section_parser import parse_resume
    from app.ml.keyword_extractor import extract_all_keywords
    from app.ml.bert_encoder import compute_bert_score
    from app.ml.tfidf_scorer import compute_tfidf_score
    from app.ml.role_detector import apply_role_weights
    from app.ml.llm_scorer import call_llm_scorer
    from app.utils.file_utils import download_file
    import uuid

    # ── Create a fresh engine for this task (avoids closed event loop issues)
    engine = create_async_engine(
        settings.DATABASE_URL,
        pool_pre_ping=False,   # skip ping — fresh engine has no stale connections
        pool_size=2,
        max_overflow=0,
    )
    session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    start_time = time.perf_counter()

    try:
        async with session_factory() as session:
            # Load match record
            result = await session.execute(
                select(MatchResult).where(MatchResult.id == uuid.UUID(match_id))
            )
            match = result.scalar_one_or_none()
            if not match:
                logger.error("match.not_found", match_id=match_id)
                return {"error": "match_not_found"}

            match.status = MatchStatus.PROCESSING

            try:
                # Load resume and JD
                resume_result = await session.execute(
                    select(Resume).where(Resume.id == match.resume_id)
                )
                resume = resume_result.scalar_one()

                jd_result = await session.execute(
                    select(JobDescription).where(JobDescription.id == match.job_id)
                )
                jd = jd_result.scalar_one()

                # Get resume text
                if resume.parsed_text:
                    resume_text = resume.parsed_text
                else:
                    file_content = await download_file(resume.s3_key)
                    if file_content:
                        import tempfile, os
                        ext = os.path.splitext(resume.filename)[1]
                        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
                            tmp.write(file_content)
                            tmp_path = tmp.name
                        parsed = parse_resume(tmp_path, ext)
                        os.unlink(tmp_path)
                        resume_text = parsed["full_text"]
                        resume.parsed_text = resume_text
                        resume.parsed_sections = parsed["sections"]
                        resume.parse_status = "done"
                    else:
                        raise ValueError("Could not download resume file")

                jd_text = jd.raw_text

                # Extract keywords
                resume_kw = extract_all_keywords(resume_text)
                jd_kw = extract_all_keywords(jd_text)

                # Compute scores
                bert_score = await compute_bert_score(resume_text, jd_text)
                tfidf_score = compute_tfidf_score(resume_text, jd_text)

                # Keyword matching
                resume_set = {k.lower() for k in resume_kw["all_keywords"]}
                jd_set = {k.lower() for k in jd_kw["all_keywords"]}
                matched = sorted(resume_set & jd_set)
                missing = sorted(jd_set - resume_set)
                keyword_score = round((len(matched) / len(jd_set) * 100) if jd_set else 0.0, 2)

                # LLM scoring
                llm_result = await call_llm_scorer(resume_text, jd_text)
                llm_score_val = float(llm_result["overall_fit"]) if llm_result else None

                # Role detection + final score
                role_data = apply_role_weights(
                    bert_score, tfidf_score, keyword_score, jd_text, llm_score_val
                )

                # Generate feedback
                final = role_data["final_score"]
                if final >= 80:
                    feedback = "Strong match! Your resume aligns well with this role."
                elif final >= 60:
                    feedback = "Good match. A few improvements can help."
                elif final >= 40:
                    feedback = "Moderate match. Tailor your resume more."
                else:
                    feedback = "Low match. Significant improvements needed."
                if missing:
                    feedback += " Missing skills: " + ", ".join(missing[:5])

                # Update match record
                match.bert_score = bert_score
                match.tfidf_score = tfidf_score
                match.keyword_score = keyword_score
                match.llm_score = llm_score_val
                match.final_score = final
                match.role_detected = role_data["role_key"]
                match.weights_used = role_data["weights_used"]
                match.score_breakdown = role_data["score_breakdown"]
                match.matched_keywords = matched
                match.missing_keywords = missing
                match.llm_verdict = llm_result
                match.feedback_text = feedback
                match.processing_ms = round((time.perf_counter() - start_time) * 1000)
                match.completed_at = datetime.now(timezone.utc)
                match.status = MatchStatus.COMPLETE

                await session.commit()

                logger.info("match.complete", match_id=match_id, final_score=final,
                            processing_ms=match.processing_ms)
                return {"match_id": match_id, "status": "complete", "final_score": final}

            except Exception as exc:
                await session.rollback()
                match.status = MatchStatus.FAILED
                match.error_message = str(exc)[:500]
                await session.commit()
                logger.error("match.failed", match_id=match_id, error=str(exc))
                return {"match_id": match_id, "status": "failed", "error": str(exc)}

    finally:
        # Always dispose the engine to cleanly close all connections
        await engine.dispose()
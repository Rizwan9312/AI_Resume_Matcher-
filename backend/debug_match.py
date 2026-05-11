import asyncio
import time
import uuid
import traceback
from app.database import async_session_factory
from app.models.match_result import MatchResult, MatchStatus
from app.models.resume import Resume
from app.models.job_description import JobDescription
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.config import settings
from app.ml.section_parser import parse_resume
from app.ml.keyword_extractor import extract_all_keywords
from app.ml.bert_encoder import compute_bert_score
from app.ml.tfidf_scorer import compute_tfidf_score
from app.ml.role_detector import apply_role_weights
from app.ml.llm_scorer import call_llm_scorer

async def debug_match():
    async with async_session_factory() as session:
        result = await session.execute(
            select(MatchResult).order_by(MatchResult.created_at.desc()).limit(1)
        )
        match = result.scalar_one_or_none()
        if not match: return
        match_id = str(match.id)
        
    print(f"Testing match ID: {match_id}")

    print("Imports done.")
    engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=False, pool_size=2, max_overflow=0)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    try:
        async with session_factory() as session:
            print("Querying DB...")
            result = await session.execute(select(MatchResult).where(MatchResult.id == uuid.UUID(match_id)))
            match = result.scalar_one()
            
            resume_result = await session.execute(select(Resume).where(Resume.id == match.resume_id))
            resume = resume_result.scalar_one()

            jd_result = await session.execute(select(JobDescription).where(JobDescription.id == match.job_id))
            jd = jd_result.scalar_one()

            resume_text = resume.parsed_text or "fallback text"
            jd_text = jd.raw_text

            print("Extracting keywords...")
            resume_kw = extract_all_keywords(resume_text)
            print("Extracted resume keywords")
            jd_kw = extract_all_keywords(jd_text)
            print("Extracted jd keywords")

            print("Computing BERT...")
            bert_score = await compute_bert_score(resume_text, jd_text)
            print("Computing TF-IDF...")
            tfidf_score = compute_tfidf_score(resume_text, jd_text)

            print("Calling LLM...")
            llm_result = await call_llm_scorer(resume_text, jd_text)
            
            print(f"LLM Output: {llm_result}")

            print("Done!")
    except Exception as e:
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_match())

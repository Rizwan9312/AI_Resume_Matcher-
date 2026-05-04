"""Rewrite pipeline Celery task — bullet extraction + LLM rewriting."""

from __future__ import annotations

import re

from app.workers.celery_app import celery_app
from app.utils.logger import get_logger

logger = get_logger("rewrite_tasks")


def extract_bullets(text: str) -> list[str]:
    """Extract bullet-point lines from resume text."""
    lines = text.splitlines()
    bullets = []
    bullet_pattern = re.compile(r"^[-•*\u2013\u2022]\s+")
    for line in lines:
        line = line.strip()
        if bullet_pattern.match(line):
            cleaned = bullet_pattern.sub("", line).strip()
            if len(cleaned) > 10:
                bullets.append(cleaned)
    return bullets


def score_bullet_strength(bullet: str) -> dict:
    """Analyze bullet and flag if it needs rewriting."""
    weak_starters = [
        "responsible for", "helped", "assisted", "worked on",
        "was involved", "participated", "supported", "did",
    ]
    quantified = bool(re.search(r"\d+", bullet))
    lower = bullet.lower()
    is_weak = any(lower.startswith(w) for w in weak_starters)
    needs_rewrite = is_weak or not quantified
    reasons = []
    if is_weak:
        reasons.append("starts with a weak/passive phrase")
    if not quantified:
        reasons.append("lacks quantifiable metrics")
    return {
        "bullet": bullet,
        "needs_rewrite": needs_rewrite,
        "reason": "; ".join(reasons) if reasons else "looks strong",
    }


@celery_app.task(name="rewrite.run_pipeline", bind=True, max_retries=2)
def run_rewrite_pipeline(self, session_id: str) -> dict:
    """Execute the bullet rewrite pipeline."""
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_run_rewrite(session_id))
    finally:
        loop.close()


async def _run_rewrite(session_id: str) -> dict:
    """Async rewrite execution."""
    import uuid
    import json
    import httpx
    from sqlalchemy import select
    from app.database import async_session_factory
    from app.models.rewrite_session import RewriteSession, RewriteStatus
    from app.models.resume import Resume
    from app.config import settings

    async with async_session_factory() as session:
        result = await session.execute(
            select(RewriteSession).where(RewriteSession.id == uuid.UUID(session_id))
        )
        rw = result.scalar_one_or_none()
        if not rw:
            return {"error": "session_not_found"}

        try:
            # Get resume text
            resume_result = await session.execute(
                select(Resume).where(Resume.id == rw.resume_id)
            )
            resume = resume_result.scalar_one()
            resume_text = resume.parsed_text or ""

            if not resume_text:
                rw.status = RewriteStatus.FAILED
                await session.commit()
                return {"error": "no_resume_text"}

            bullets = extract_bullets(resume_text)
            if not bullets:
                rw.status = RewriteStatus.FAILED
                await session.commit()
                return {"error": "no_bullets_found"}

            strength_flags = [score_bullet_strength(b) for b in bullets]
            weak_count = sum(1 for f in strength_flags if f["needs_rewrite"])

            # Call LLM for rewrites
            bullets_text = "\n".join(f"{i+1}. {b}" for i, b in enumerate(bullets))
            prompt = f"""You are an expert resume coach.

JOB DESCRIPTION:
{rw.jd_text[:1500]}

RESUME BULLETS:
{bullets_text}

Rewrite each bullet to be stronger, quantified, and ATS optimized.
For each bullet, provide 3 rewrite variants.

Return ONLY valid JSON:
[
  {{
    "original": "...",
    "rewritten_variants": ["variant1", "variant2", "variant3"],
    "reason": "..."
  }}
]"""

            rewrites = None
            if settings.OPENROUTER_API_KEY:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    resp = await client.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                            "Content-Type": "application/json",
                        },
                        json={
                            "model": settings.LLM_MODEL,
                            "messages": [{"role": "user", "content": prompt}],
                            "temperature": 0.3,
                        },
                    )
                    api_result = resp.json()
                    if "choices" in api_result:
                        raw = api_result["choices"][0]["message"]["content"]
                        import re as re_mod
                        raw = re_mod.sub(r"^```json\s*", "", raw, flags=re_mod.MULTILINE)
                        raw = re_mod.sub(r"\s*```$", "", raw, flags=re_mod.MULTILINE)
                        rewrites = json.loads(raw.strip())

            rw.bullet_count = len(bullets)
            rw.weak_count = weak_count
            rw.rewrites = rewrites or [{"original": b, "rewritten_variants": [], "reason": "LLM unavailable"} for b in bullets]
            rw.status = RewriteStatus.COMPLETE
            await session.commit()

            logger.info("rewrite.complete", session_id=session_id, bullets=len(bullets))
            return {"session_id": session_id, "status": "complete"}

        except Exception as exc:
            rw.status = RewriteStatus.FAILED
            await session.commit()
            logger.error("rewrite.failed", session_id=session_id, error=str(exc))
            return {"error": str(exc)}

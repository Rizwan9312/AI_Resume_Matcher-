"""Job query extractor — uses OpenRouter LLM to extract structured job search parameters."""

import json
import httpx

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger("job_query_extractor")


async def extract_job_queries(
    resume_text: str,
    job_description_text: str = None,
    match_data: dict = None
) -> dict:
    """
    Calls the LLM to extract structured job search parameters from resume data.
    Returns a dict used to build the JSearch API query.
    """
    context = f"Resume:\n{resume_text[:3000]}"

    if job_description_text:
        context += f"\n\nTarget Job Description:\n{job_description_text[:1500]}"

    if match_data and match_data.get("missing_keywords"):
        missing = ", ".join(str(k) for k in match_data["missing_keywords"][:10])
        context += f"\n\nSkills missing from resume vs job: {missing}"

    prompt = f"""Analyze this resume and extract job search parameters.
Return ONLY valid JSON with no markdown fences, no preamble, no explanation.

{context}

Return exactly this JSON structure:
{{
  "primary_job_title": "the single most fitting job title to search for",
  "alternative_titles": ["one alternative title", "another alternative title"],
  "key_skills": ["skill1", "skill2", "skill3"],
  "seniority": "entry|mid|senior|lead|manager",
  "preferred_location": "city name or Remote if unclear",
  "industry": "tech|finance|marketing|healthcare|other"
}}"""

    # Call OpenRouter directly (same pattern used in llm_scorer.py)
    if not settings.OPENROUTER_API_KEY:
        logger.warning("job_query_extractor.no_api_key")
        return _fallback()

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.LLM_MODEL,
                    "messages": [
                        {"role": "system", "content": "You are a job search expert. Respond ONLY with valid JSON."},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.1,
                    "max_tokens": 500,
                },
            )
            result = response.json()

        if "choices" not in result:
            logger.warning("job_query_extractor.no_choices", response=str(result)[:200])
            return _fallback()

        raw = result["choices"][0]["message"]["content"]
        # Strip markdown fences and think tags
        import re
        raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL)
        raw = re.sub(r"```json\s*", "", raw)
        raw = re.sub(r"```\s*", "", raw)
        match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
        if match:
            return json.loads(match.group(0).strip())
        return json.loads(raw.strip())

    except (json.JSONDecodeError, AttributeError, Exception) as exc:
        logger.warning("job_query_extractor.failed", error=str(exc))
        return _fallback()


def _fallback() -> dict:
    """Safe fallback so the pipeline never crashes on a bad LLM response."""
    return {
        "primary_job_title": "Software Engineer",
        "alternative_titles": [],
        "key_skills": [],
        "seniority": "mid",
        "preferred_location": "Remote",
        "industry": "tech"
    }

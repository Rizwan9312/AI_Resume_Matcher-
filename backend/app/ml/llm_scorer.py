"""LLM scorer — uses OpenRouter API for structured resume evaluation."""

from __future__ import annotations

import json
import re

import httpx

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger("llm_scorer")

SYSTEM_PROMPT = """You are an expert technical recruiter and resume evaluator.
You MUST respond with ONLY a valid complete JSON object.
Do NOT truncate or cut off the JSON.
Do NOT include any text before or after the JSON.
Do NOT use markdown code fences.
Do NOT include <think> tags.
Complete the entire JSON object fully before stopping."""

USER_PROMPT_TEMPLATE = """
RESUME:
{resume_text}

JOB DESCRIPTION:
{jd_text}

Return this exact JSON structure with no other text:
{{
  "overall_fit": <integer 0-100>,
  "experience_match": <integer 0-100>,
  "skills_match": <integer 0-100>,
  "soft_skills_match": <integer 0-100>,
  "seniority_match": <integer 0-100>,
  "strengths": ["<string>", "<string>", "<string>"],
  "gaps": ["<string>", "<string>", "<string>"],
  "recommendation": "<strong_match|good_match|partial_match|weak_match>",
  "one_line_summary": "<string max 200 chars>"
}}"""


def _extract_json(raw: str) -> str:
    """Aggressively extract JSON from messy LLM output."""
    # 1. Strip <think>...</think> blocks (Qwen thinking models)
    raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL)

    # 2. Strip markdown code fences
    raw = re.sub(r"```json\s*", "", raw)
    raw = re.sub(r"```\s*", "", raw)

    # 3. Extract the first complete { ... } block
    match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
    if match:
        return match.group(0).strip()

    return raw.strip()


async def call_llm_scorer(resume_text: str, jd_text: str) -> dict | None:
    """Call the LLM API for structured resume evaluation.

    Uses OpenRouter API. Retries once on JSON parse failure.
    Returns parsed dict or None on failure.
    """
    if not settings.OPENROUTER_API_KEY:
        logger.warning("ml.llm.no_api_key")
        return None

    prompt = USER_PROMPT_TEMPLATE.format(
        resume_text=resume_text[:4000],
        jd_text=jd_text[:2000],
    )

    for attempt in range(2):
        raw = None
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
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": prompt},
                        ],
                        "temperature": 0.1,
                        "max_tokens": 1000,  # ← ensures full JSON is returned
                        # response_format removed — not supported by this model
                    },
                )
                result = response.json()

            if "choices" not in result:
                logger.warning("ml.llm.no_choices", response=str(result)[:200])
                return None

            raw = result["choices"][0]["message"]["content"]
            logger.debug("ml.llm.raw_response", attempt=attempt + 1, raw=raw[:300])

            cleaned = _extract_json(raw)
            parsed = json.loads(cleaned)

            logger.info("ml.llm.called", attempt=attempt + 1, score=parsed.get("overall_fit"))
            return parsed

        except json.JSONDecodeError as exc:
            logger.warning(
                "ml.llm.json_parse_failed",
                attempt=attempt + 1,
                error=str(exc),
                raw=raw[:200] if raw else "no_raw",
            )
            if attempt == 0:
                prompt += "\n\nCRITICAL: Return ONLY the complete JSON object. No truncation. No explanation. No markdown."
                continue
            logger.error("ml.llm.failed", reason="json_parse_failed_twice")
            return None

        except Exception as exc:
            logger.error("ml.llm.error", error=str(exc), attempt=attempt + 1)
            return None

    return None
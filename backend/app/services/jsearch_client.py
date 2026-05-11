"""JSearch API client — fetches live job postings from LinkedIn, Indeed, etc."""

import httpx
from datetime import datetime
from typing import List, Dict
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger("jsearch_client")

JSEARCH_BASE = "https://jsearch.p.rapidapi.com"


def _get_headers() -> dict:
    return {
        "X-RapidAPI-Key": settings.JSEARCH_API_KEY,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
    }


def _map_seniority(seniority: str) -> str:
    mapping = {
        "entry":   "no_experience",
        "mid":     "under_3_years_experience",
        "senior":  "more_than_3_years_experience",
        "lead":    "more_than_3_years_experience",
        "manager": "more_than_3_years_experience",
    }
    return mapping.get(seniority, "under_3_years_experience")


def _normalize_job(raw: dict) -> dict:
    """Converts the raw JSearch response dict into our internal format."""
    posted_at = None
    if raw.get("job_posted_at_datetime_utc"):
        try:
            posted_at = datetime.fromisoformat(
                raw["job_posted_at_datetime_utc"].replace("Z", "+00:00")
            )
        except Exception:
            pass

    city    = raw.get("job_city", "") or ""
    state   = raw.get("job_state", "") or ""
    country = raw.get("job_country", "") or ""
    location = ", ".join(p for p in [city, state, country] if p)

    return {
        "job_id":               raw.get("job_id", ""),
        "job_title":            raw.get("job_title", ""),
        "employer_name":        raw.get("employer_name", ""),
        "employer_logo":        raw.get("employer_logo", ""),
        "job_publisher":        raw.get("job_publisher", ""),
        "job_employment_type":  raw.get("job_employment_type", ""),
        "job_location":         location,
        "job_description":      (raw.get("job_description", "") or "")[:2000],
        "job_apply_link":       raw.get("job_apply_link", ""),
        "job_posted_at":        posted_at,
        "job_salary_min":       raw.get("job_min_salary"),
        "job_salary_max":       raw.get("job_max_salary"),
        "job_salary_currency":  raw.get("job_salary_currency"),
        "raw_data":             raw,
    }


async def _fetch_page(client: httpx.AsyncClient, query: str, params: dict) -> List[dict]:
    """Execute a single JSearch API call with retry on 429 rate-limit."""
    import asyncio

    max_retries = 3
    for attempt in range(max_retries):
        try:
            logger.info("jsearch.request", query=query, params=params, attempt=attempt + 1)
            resp = await client.get(
                f"{JSEARCH_BASE}/search",
                headers=_get_headers(),
                params=params,
            )
            body = resp.json()

            # Handle rate limiting with exponential backoff
            if resp.status_code == 429:
                wait_secs = 5 * (2 ** attempt)  # 5s, 10s, 20s
                logger.warning(
                    "jsearch.rate_limited",
                    query=query,
                    attempt=attempt + 1,
                    retry_in_secs=wait_secs,
                )
                await asyncio.sleep(wait_secs)
                continue

            if resp.status_code != 200:
                logger.error(
                    "jsearch.api_error",
                    status=resp.status_code,
                    body=str(body)[:300],
                    query=query,
                )
                return []

            raw_list = body.get("data") or []
            logger.info("jsearch.response", query=query, results=len(raw_list), status=resp.status_code)
            return raw_list

        except httpx.HTTPError as exc:
            logger.error("jsearch.http_error", query=query, error=str(exc))
            return []
        except Exception as exc:
            logger.error("jsearch.unexpected_error", query=query, error=str(exc))
            return []

    logger.error("jsearch.max_retries_exceeded", query=query)
    return []


async def search_jobs(query_params: dict, num_pages: int = 1) -> List[Dict]:
    """
    Calls JSearch with the primary job title and skills.
    Also runs a second call with the first alternative title for variety.
    Falls back to a broader search if the first attempt returns nothing.
    Returns a deduplicated list of normalised job dicts.
    """
    if not settings.JSEARCH_API_KEY:
        logger.warning("jsearch.no_api_key")
        return []

    title    = query_params.get("primary_job_title", "")
    skills   = " ".join(query_params.get("key_skills", [])[:3])
    location = query_params.get("preferred_location", "Remote")

    primary_query = f"{title} {skills}".strip()
    seen_ids: set = set()
    all_jobs: List[Dict] = []

    queries_to_run = [primary_query]
    alt_titles = query_params.get("alternative_titles", [])
    if alt_titles:
        queries_to_run.append(f"{alt_titles[0]} {location}")

    def _collect(raw_list: List[dict]):
        for raw in raw_list:
            jid = raw.get("job_id", "")
            if jid and jid not in seen_ids:
                seen_ids.add(jid)
                all_jobs.append(_normalize_job(raw))

    async with httpx.AsyncClient(timeout=30.0) as client:
        # ── Pass 1: broader search (no seniority filter, month window) ──
        for q in queries_to_run:
            raw_list = await _fetch_page(client, q, {
                "query":            q,
                "page":             "1",
                "num_pages":        str(num_pages),
                "date_posted":      "month",
            })
            _collect(raw_list)

        # ── Pass 2: fallback with just the job title if still empty ──
        if not all_jobs and title:
            logger.info("jsearch.fallback", reason="no_results_from_primary", title=title)
            raw_list = await _fetch_page(client, title, {
                "query":      title,
                "page":       "1",
                "num_pages":  "1",
            })
            _collect(raw_list)

    logger.info("jsearch.total_results", count=len(all_jobs))
    return all_jobs

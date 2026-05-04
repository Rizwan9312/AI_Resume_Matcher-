import requests
import json
import re
import os
from dotenv import load_dotenv
from typing import Union

# load .env
load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")

if not API_KEY:
    raise ValueError("❌ OPENROUTER_API_KEY not found in .env file")


def extract_bullets(text: str) -> list[str]:
    """
    Extract bullet-point lines from resume text.
    Lines starting with common bullet markers or action words are included.
    """
    lines = text.splitlines()
    bullets = []
    bullet_pattern = re.compile(r'^[\-\•\*\u2013\u2022]\s+')
    for line in lines:
        line = line.strip()
        if bullet_pattern.match(line):
            cleaned = bullet_pattern.sub('', line).strip()
            if len(cleaned) > 10:  # ignore very short/empty lines
                bullets.append(cleaned)
    return bullets


def score_bullet_strength(bullet: str) -> dict:
    """
    Analyse a single bullet and flag whether it needs a rewrite.
    Returns a dict with 'bullet', 'needs_rewrite', and 'reason'.
    """
    weak_starters = [
        "responsible for", "helped", "assisted", "worked on",
        "was involved", "participated", "supported", "did"
    ]
    quantified = bool(re.search(r'\d+', bullet))  # contains a number
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
        "reason": "; ".join(reasons) if reasons else "looks strong"
    }


def rewrite_bullets(bullets: list[str], job_description: str) -> Union[list[dict], dict]:

    if not bullets:
        return []

    bullets_text = "\n".join(f"{i+1}. {b}" for i, b in enumerate(bullets))

    prompt = f"""
You are an expert resume coach.

JOB DESCRIPTION:
{job_description[:1500]}

RESUME BULLETS:
{bullets_text}

Rewrite each bullet to be stronger, quantified, and ATS optimized.

Return ONLY valid JSON:
[
  {{
    "original": "...",
    "rewritten": "...",
    "reason": "..."
  }}
]
"""

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "qwen/qwen-2.5-coder-32b-instruct",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }

    raw = ""  # initialise before try so it's always in scope
    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)
        result = response.json()

        print("DEBUG:", result)

        if "choices" not in result:
            return [{"error": str(result)}]

        raw = result["choices"][0]["message"]["content"]

        # clean markdown
        raw = re.sub(r'^```json\s*', '', raw, flags=re.MULTILINE)
        raw = re.sub(r'\s*```$', '', raw, flags=re.MULTILINE)

        return json.loads(raw.strip())

    except json.JSONDecodeError:
        return [{"error": "Invalid JSON from model", "raw": raw}]

    except Exception as e:
        return [{"error": str(e)}]
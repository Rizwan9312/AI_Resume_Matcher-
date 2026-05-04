"""Role detector — 10 role profiles with auto-weight detection and final score computation."""

from __future__ import annotations

from app.utils.logger import get_logger

logger = get_logger("role_detector")

ROLE_PROFILES: dict[str, dict] = {
    "tech": {
        "label": "Technology / Engineering", "icon": "💻",
        "weights": {"bert": 0.45, "tfidf": 0.35, "keyword": 0.20},
        "keywords": ["software", "engineer", "developer", "python", "javascript", "java", "backend",
            "frontend", "fullstack", "devops", "cloud", "aws", "azure", "kubernetes", "docker",
            "api", "database", "machine learning", "data science", "ml", "react", "node",
            "typescript", "golang", "rust", "microservices", "ci/cd", "git", "agile", "scrum",
            "sql", "nosql", "mongodb", "postgresql"],
    },
    "marketing": {
        "label": "Marketing / Growth", "icon": "📣",
        "weights": {"bert": 0.50, "tfidf": 0.25, "keyword": 0.25},
        "keywords": ["marketing", "brand", "campaign", "seo", "sem", "content", "social media",
            "growth", "acquisition", "retention", "email marketing", "copywriting", "analytics",
            "google ads", "facebook ads", "digital marketing", "performance marketing"],
    },
    "finance": {
        "label": "Finance / Accounting", "icon": "📊",
        "weights": {"bert": 0.40, "tfidf": 0.30, "keyword": 0.30},
        "keywords": ["finance", "accounting", "financial", "analyst", "investment", "banking",
            "portfolio", "equity", "valuation", "budget", "forecasting", "audit", "cpa", "cfa",
            "financial modeling", "gaap", "ifrs", "tax", "treasury", "risk", "compliance"],
    },
    "product": {
        "label": "Product Management", "icon": "🗺️",
        "weights": {"bert": 0.55, "tfidf": 0.25, "keyword": 0.20},
        "keywords": ["product manager", "product owner", "roadmap", "backlog", "user story",
            "sprint", "agile", "stakeholder", "prioritization", "kpi", "okr", "user research",
            "a/b test", "wireframe", "go-to-market", "product strategy"],
    },
    "design": {
        "label": "Design / UX", "icon": "🎨",
        "weights": {"bert": 0.55, "tfidf": 0.20, "keyword": 0.25},
        "keywords": ["designer", "ux", "ui", "user experience", "user interface", "figma",
            "sketch", "adobe", "prototyping", "wireframe", "visual design", "branding",
            "design system", "accessibility", "usability testing"],
    },
    "sales": {
        "label": "Sales / Business Development", "icon": "🤝",
        "weights": {"bert": 0.45, "tfidf": 0.25, "keyword": 0.30},
        "keywords": ["sales", "business development", "account executive", "quota", "pipeline",
            "crm", "salesforce", "prospecting", "closing", "b2b", "b2c", "revenue",
            "enterprise sales", "saas", "lead generation"],
    },
    "hr": {
        "label": "Human Resources", "icon": "👥",
        "weights": {"bert": 0.50, "tfidf": 0.25, "keyword": 0.25},
        "keywords": ["hr", "human resources", "recruiting", "talent acquisition", "onboarding",
            "employee relations", "performance management", "compensation", "benefits",
            "training", "dei", "payroll"],
    },
    "data": {
        "label": "Data / Analytics", "icon": "📈",
        "weights": {"bert": 0.40, "tfidf": 0.35, "keyword": 0.25},
        "keywords": ["data analyst", "data engineer", "data scientist", "sql", "python", "r",
            "tableau", "power bi", "spark", "etl", "statistics", "machine learning",
            "visualization", "big data", "warehouse", "snowflake", "dbt", "airflow"],
    },
    "legal": {
        "label": "Legal / Compliance", "icon": "⚖️",
        "weights": {"bert": 0.45, "tfidf": 0.30, "keyword": 0.25},
        "keywords": ["attorney", "counsel", "litigation", "compliance", "regulatory",
            "contract", "legal", "paralegal", "gdpr", "hipaa", "soc2", "arbitration",
            "intellectual property", "corporate law"],
    },
    "operations": {
        "label": "Operations / Supply Chain", "icon": "🔧",
        "weights": {"bert": 0.40, "tfidf": 0.35, "keyword": 0.25},
        "keywords": ["operations", "supply chain", "logistics", "procurement",
            "inventory", "vendor", "process improvement", "six sigma", "lean",
            "warehouse", "manufacturing", "quality assurance"],
    },
}

DEFAULT_WEIGHTS = {"bert": 0.50, "tfidf": 0.30, "keyword": 0.20}


def detect_role(job_description: str) -> tuple[str, dict]:
    """Detect the best-matching role from JD text. Requires >= 2 keyword hits."""
    jd_lower = job_description.lower()
    scores = {}
    for role_key, profile in ROLE_PROFILES.items():
        hit_count = sum(1 for kw in profile["keywords"] if kw in jd_lower)
        scores[role_key] = hit_count

    best_role = max(scores, key=scores.get)
    if scores[best_role] < 2:
        return "general", {"label": "General", "icon": "📄", "weights": DEFAULT_WEIGHTS, "keywords": []}
    return best_role, ROLE_PROFILES[best_role]


def compute_final_score(
    bert: float, tfidf: float, keyword: float,
    llm: float | None, weights: dict,
) -> float:
    """Compute role-weighted final score.

    If LLM score available: blend 4 scores (LLM gets 15%, others reduced proportionally).
    If LLM unavailable: use 3-score formula from role weights.
    Returns float 0.0-100.0, rounded to 1 decimal.
    """
    if llm is not None and llm > 0:
        llm_weight = 0.15
        remaining = 1.0 - llm_weight
        final = (
            bert * weights["bert"] * remaining
            + tfidf * weights["tfidf"] * remaining
            + keyword * weights["keyword"] * remaining
            + llm * llm_weight
        )
    else:
        final = (
            bert * weights["bert"]
            + tfidf * weights["tfidf"]
            + keyword * weights["keyword"]
        )
    return round(max(0.0, min(100.0, final)), 1)


def apply_role_weights(
    bert_score: float, tfidf_score: float, keyword_score: float,
    job_description: str, llm_score: float | None = None,
) -> dict:
    """Detect role, compute final score, return full breakdown."""
    role_key, profile = detect_role(job_description)
    w = profile["weights"]
    final = compute_final_score(bert_score, tfidf_score, keyword_score, llm_score, w)

    return {
        "final_score": final,
        "role_key": role_key,
        "role_label": profile["label"],
        "role_icon": profile["icon"],
        "weights_used": w,
        "score_breakdown": {
            "bert_contribution": round(bert_score * w["bert"], 1),
            "tfidf_contribution": round(tfidf_score * w["tfidf"], 1),
            "keyword_contribution": round(keyword_score * w["keyword"], 1),
        },
    }

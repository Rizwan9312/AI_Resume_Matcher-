"""
role_scorer.py — Role-specific scoring weights & keyword profiles
Phase 9, Step 2: Role-Specific Scoring

Drop this file in: backend/role_scorer.py
"""

import re

# ─── Role Profiles ────────────────────────────────────────────────────────────
# Each profile defines:
#   weights   : how much each scorer contributes to final score
#   keywords  : seed keywords that help detect this role from JD text
#   label     : human-friendly display name
#   icon      : emoji shown in UI
# ─────────────────────────────────────────────────────────────────────────────

ROLE_PROFILES = {
    "tech": {
        "label": "Technology / Engineering",
        "icon": "💻",
        "weights": {"bert": 0.45, "tfidf": 0.35, "keyword": 0.20},
        "keywords": [
            "software", "engineer", "developer", "python", "javascript", "java", "backend",
            "frontend", "fullstack", "devops", "cloud", "aws", "azure", "kubernetes",
            "docker", "api", "database", "machine learning", "data science", "ml",
            "react", "node", "typescript", "golang", "rust", "microservices", "ci/cd",
            "git", "agile", "scrum", "sql", "nosql", "mongodb", "postgresql"
        ]
    },
    "marketing": {
        "label": "Marketing / Growth",
        "icon": "📣",
        "weights": {"bert": 0.50, "tfidf": 0.25, "keyword": 0.25},
        "keywords": [
            "marketing", "brand", "campaign", "seo", "sem", "content", "social media",
            "growth", "acquisition", "retention", "email marketing", "copywriting",
            "analytics", "google ads", "facebook ads", "influencer", "pr", "public relations",
            "market research", "conversion", "funnel", "crm", "hubspot", "salesforce",
            "digital marketing", "performance marketing", "storytelling", "engagement"
        ]
    },
    "finance": {
        "label": "Finance / Accounting",
        "icon": "📊",
        "weights": {"bert": 0.40, "tfidf": 0.30, "keyword": 0.30},
        "keywords": [
            "finance", "accounting", "financial", "analyst", "investment", "banking",
            "portfolio", "equity", "valuation", "budget", "forecasting", "audit",
            "cpa", "cfa", "excel", "financial modeling", "gaap", "ifrs", "tax",
            "treasury", "risk", "compliance", "derivatives", "fixed income", "p&l",
            "balance sheet", "cash flow", "private equity", "venture capital"
        ]
    },
    "product": {
        "label": "Product Management",
        "icon": "🗺️",
        "weights": {"bert": 0.55, "tfidf": 0.25, "keyword": 0.20},
        "keywords": [
            "product manager", "product owner", "roadmap", "backlog", "user story",
            "sprint", "agile", "stakeholder", "prioritization", "kpi", "okr",
            "user research", "a/b test", "wireframe", "figma", "go-to-market",
            "launch", "cross-functional", "discovery", "metrics", "retention",
            "feature", "mvp", "product strategy", "jira", "confluence"
        ]
    },
    "design": {
        "label": "Design / UX",
        "icon": "🎨",
        "weights": {"bert": 0.55, "tfidf": 0.20, "keyword": 0.25},
        "keywords": [
            "designer", "ux", "ui", "user experience", "user interface", "figma",
            "sketch", "adobe", "prototyping", "wireframe", "visual design", "branding",
            "typography", "color theory", "design system", "accessibility", "wcag",
            "usability testing", "information architecture", "interaction design",
            "motion design", "illustration", "photoshop", "illustrator", "after effects"
        ]
    },
    "sales": {
        "label": "Sales / Business Development",
        "icon": "🤝",
        "weights": {"bert": 0.45, "tfidf": 0.25, "keyword": 0.30},
        "keywords": [
            "sales", "business development", "account executive", "quota", "pipeline",
            "crm", "salesforce", "prospecting", "cold calling", "closing", "b2b", "b2c",
            "revenue", "targets", "negotiation", "client", "customer success",
            "enterprise sales", "saas", "lead generation", "outbound", "inbound",
            "partnerships", "channel sales", "solution selling", "deal"
        ]
    },
    "hr": {
        "label": "Human Resources",
        "icon": "👥",
        "weights": {"bert": 0.50, "tfidf": 0.25, "keyword": 0.25},
        "keywords": [
            "hr", "human resources", "recruiting", "talent acquisition", "onboarding",
            "employee relations", "performance management", "compensation", "benefits",
            "hris", "workday", "bamboohr", "culture", "engagement", "training",
            "learning & development", "organizational development", "succession planning",
            "labor law", "diversity", "inclusion", "equity", "dei", "payroll"
        ]
    },
    "data": {
        "label": "Data / Analytics",
        "icon": "📈",
        "weights": {"bert": 0.40, "tfidf": 0.35, "keyword": 0.25},
        "keywords": [
            "data analyst", "data engineer", "data scientist", "sql", "python", "r",
            "tableau", "power bi", "looker", "spark", "hadoop", "etl", "pipeline",
            "statistics", "machine learning", "deep learning", "visualization",
            "big data", "warehouse", "snowflake", "redshift", "dbt", "airflow",
            "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "nlp"
        ]
    }
}

DEFAULT_WEIGHTS = {"bert": 0.50, "tfidf": 0.30, "keyword": 0.20}


def detect_role(job_description: str) -> tuple[str, dict]:
    """
    Analyze the JD text and return the best-matching role key + its profile.
    Falls back to a balanced 'general' profile if no role is detected.
    """
    jd_lower = job_description.lower()
    scores = {}

    for role_key, profile in ROLE_PROFILES.items():
        hit_count = sum(1 for kw in profile["keywords"] if kw in jd_lower)
        scores[role_key] = hit_count

    best_role = max(scores, key=scores.get)
    best_score = scores[best_role]

    # Require at least 2 keyword hits to claim a role
    if best_score < 2:
        return "general", {
            "label": "General",
            "icon": "📄",
            "weights": DEFAULT_WEIGHTS,
            "keywords": []
        }

    return best_role, ROLE_PROFILES[best_role]


def apply_role_weights(bert_score: float, tfidf_score: float, keyword_score: float,
                       job_description: str) -> dict:
    """
    Given raw scores and a JD, detect role and compute role-weighted final score.

    Returns:
        {
          "final_score"   : float,
          "role_key"      : str,
          "role_label"    : str,
          "role_icon"     : str,
          "weights_used"  : dict,
          "score_breakdown": dict
        }
    """
    role_key, profile = detect_role(job_description)
    w = profile["weights"]

    final = round(
        bert_score    * w["bert"]    +
        tfidf_score   * w["tfidf"]   +
        keyword_score * w["keyword"],
        1
    )

    return {
        "final_score"   : final,
        "role_key"      : role_key,
        "role_label"    : profile["label"],
        "role_icon"     : profile["icon"],
        "weights_used"  : w,
        "score_breakdown": {
            "bert_contribution"   : round(bert_score    * w["bert"],    1),
            "tfidf_contribution"  : round(tfidf_score   * w["tfidf"],   1),
            "keyword_contribution": round(keyword_score * w["keyword"], 1)
        }
    }
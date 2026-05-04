"""Keyword extractor — hard/soft skill matching with spaCy NLP and alias resolution."""

from __future__ import annotations

import re
from app.ml.skill_graph import expand_skills, normalize_skill
from app.utils.logger import get_logger

logger = get_logger("keyword_extractor")

# ── Master Skills Lists (ported + extended from original keywords.py) ─────────

HARD_SKILLS: set[str] = {
    "python", "java", "javascript", "typescript", "c++", "c#", "r", "sql",
    "html", "css", "bash", "scala", "kotlin", "swift", "go", "rust", "ruby", "php", "perl",
    "machine learning", "deep learning", "nlp", "computer vision",
    "neural network", "reinforcement learning", "feature engineering",
    "model training", "fine-tuning", "transfer learning", "large language models",
    "tensorflow", "pytorch", "keras", "scikit-learn", "xgboost",
    "lightgbm", "hugging face", "transformers", "spacy", "nltk",
    "opencv", "mediapipe", "pandas", "numpy", "matplotlib", "seaborn",
    "flask", "django", "fastapi", "react", "node.js", "express",
    "next.js", "vue", "angular", "svelte",
    "mysql", "postgresql", "mongodb", "sqlite", "redis", "firebase",
    "elasticsearch", "cassandra", "dynamodb",
    "aws", "azure", "gcp", "docker", "kubernetes", "git", "github",
    "ci/cd", "github actions", "linux", "rest api", "graphql",
    "terraform", "ansible", "jenkins",
    "data analysis", "data visualization", "etl", "big data",
    "tableau", "power bi", "excel", "spark", "hadoop",
    "figma", "sketch", "adobe", "photoshop",
    "jira", "confluence", "slack", "notion",
}

SOFT_SKILLS: set[str] = {
    "communication", "teamwork", "leadership", "problem solving",
    "critical thinking", "time management", "collaboration",
    "adaptability", "creativity", "attention to detail",
    "project management", "analytical thinking", "decision making",
    "mentoring", "negotiation", "presentation", "stakeholder management",
    "conflict resolution", "strategic thinking", "emotional intelligence",
}


def extract_hard_skills(text: str) -> set[str]:
    """Match text against the hard skills master list with alias resolution."""
    text_lower = text.lower()
    found: set[str] = set()
    for skill in HARD_SKILLS:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text_lower):
            found.add(normalize_skill(skill))
    return found


def extract_soft_skills(text: str) -> set[str]:
    """Match text against the soft skills master list."""
    text_lower = text.lower()
    found: set[str] = set()
    for skill in SOFT_SKILLS:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text_lower):
            found.add(skill)
    return found


def extract_keywords_spacy(text: str) -> set[str]:
    """Use spaCy NLP to extract entities and noun chunks."""
    try:
        import spacy
        nlp = spacy.load("en_core_web_md")
        doc = nlp(text.lower()[:50000])  # Limit input size
        keywords: set[str] = set()
        for ent in doc.ents:
            if ent.label_ in ("ORG", "PRODUCT", "GPE", "WORK_OF_ART"):
                keywords.add(ent.text.strip())
        for chunk in doc.noun_chunks:
            token = chunk.text.strip()
            if 2 <= len(token.split()) <= 4:
                keywords.add(token)
        return keywords
    except Exception as exc:
        logger.warning("keywords.spacy_failed", error=str(exc))
        return set()


def extract_all_keywords(text: str) -> dict:
    """Master extractor — runs all methods and returns structured results."""
    hard = extract_hard_skills(text)
    soft = extract_soft_skills(text)
    nlp_kw = extract_keywords_spacy(text)

    # Expand with implied skills
    expanded_hard = expand_skills(hard)

    return {
        "hard_skills": sorted(expanded_hard),
        "soft_skills": sorted(soft),
        "nlp_keywords": sorted(nlp_kw),
        "all_keywords": sorted(expanded_hard | soft),
    }

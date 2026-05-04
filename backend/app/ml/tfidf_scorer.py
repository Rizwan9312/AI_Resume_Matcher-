"""TF-IDF scorer — cosine similarity between resume and JD using TF-IDF vectors."""

from __future__ import annotations

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.utils.logger import get_logger

logger = get_logger("tfidf_scorer")


def compute_tfidf_score(resume_text: str, jd_text: str) -> float:
    """Compute TF-IDF cosine similarity between resume and JD.

    Returns float 0.0-100.0.
    """
    if not resume_text or not jd_text:
        return 0.0

    try:
        vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
        tfidf_matrix = vectorizer.fit_transform([resume_text, jd_text])
        score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return round(float(score) * 100, 2)
    except Exception as exc:
        logger.error("ml.tfidf.failed", error=str(exc))
        return 0.0

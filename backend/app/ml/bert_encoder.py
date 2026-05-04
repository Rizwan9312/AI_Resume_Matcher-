"""BERT encoder — singleton model, Redis cache, cosine similarity scoring."""

from __future__ import annotations

import hashlib
from typing import Optional

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger("bert_encoder")

_model = None


def get_model():
    """Lazy-loaded singleton — model loaded once on first call."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        logger.info("ml.bert.loading", model=settings.BERT_MODEL_NAME)
        _model = SentenceTransformer(settings.BERT_MODEL_NAME)
        logger.info("ml.bert.loaded")
    return _model


def encode_text(text: str) -> list[float]:
    """Encode text to embedding vector."""
    model = get_model()
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.tolist()


def _content_hash(text: str) -> str:
    """SHA-256 hash of text content for cache keying."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


async def compute_bert_score(
    resume_text: str,
    jd_text: str,
    redis_client=None,
) -> float:
    """Compute BERT cosine similarity with Redis caching.

    1. Hash both texts concatenated
    2. Check Redis cache
    3. If miss: encode + compute + cache (TTL 24h)
    4. Return float 0.0-100.0
    """
    if not resume_text or not jd_text:
        return 0.0

    cache_key = f"bert:{_content_hash(resume_text + jd_text)}"

    # Check cache
    if redis_client:
        try:
            cached = await redis_client.get(cache_key)
            if cached is not None:
                logger.debug("ml.bert.cache_hit", key=cache_key)
                return float(cached)
        except Exception:
            pass

    logger.debug("ml.bert.cache_miss", key=cache_key)

    try:
        from sentence_transformers import util
        model = get_model()
        resume_emb = model.encode(resume_text, convert_to_tensor=True)
        jd_emb = model.encode(jd_text, convert_to_tensor=True)
        similarity = util.cos_sim(resume_emb, jd_emb)
        score = round(float(similarity[0][0]) * 100, 2)
    except Exception as exc:
        logger.error("ml.bert.failed", error=str(exc))
        return 0.0

    # Cache result
    if redis_client:
        try:
            await redis_client.setex(cache_key, 86400, str(score))
        except Exception:
            pass

    return score

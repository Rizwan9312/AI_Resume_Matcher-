"""Redis client wrapper and cache decorators."""

from __future__ import annotations

import json
from typing import Any, Optional

import redis.asyncio as aioredis

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger("cache")

_redis_client: Optional[aioredis.Redis] = None


async def get_redis() -> aioredis.Redis:
    """Get or create the Redis client singleton."""
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis_client


async def close_redis() -> None:
    """Close the Redis connection."""
    global _redis_client
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None


async def cache_get(key: str) -> Any | None:
    """Get a value from Redis cache."""
    try:
        client = await get_redis()
        value = await client.get(key)
        if value is not None:
            return json.loads(value)
    except Exception as exc:
        logger.warning("cache.get_failed", key=key, error=str(exc))
    return None


async def cache_set(key: str, value: Any, ttl_seconds: int = 3600) -> bool:
    """Set a value in Redis cache with TTL."""
    try:
        client = await get_redis()
        serialized = json.dumps(value)
        await client.setex(key, ttl_seconds, serialized)
        return True
    except Exception as exc:
        logger.warning("cache.set_failed", key=key, error=str(exc))
        return False


async def cache_delete(key: str) -> bool:
    """Delete a key from Redis cache."""
    try:
        client = await get_redis()
        await client.delete(key)
        return True
    except Exception as exc:
        logger.warning("cache.delete_failed", key=key, error=str(exc))
        return False


async def redis_health_check() -> bool:
    """Check if Redis is reachable."""
    try:
        client = await get_redis()
        await client.ping()
        return True
    except Exception:
        return False

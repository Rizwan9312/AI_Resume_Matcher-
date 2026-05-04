"""Security utilities — JWT (HS256) and bcrypt password hashing."""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger("security")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ── Password Hashing ─────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    """Hash a password using bcrypt, truncating to 72 bytes (bcrypt limit)."""
    return pwd_context.hash(password[:72])


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plain password against a bcrypt hash."""
    return pwd_context.verify(plain[:72], hashed)

# ── JWT Tokens ────────────────────────────────────────────────────────────

def create_access_token(
    user_id: str,
    role: str,
    tenant_id: str,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a JWT access token (HS256, short-lived)."""
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload = {
        "sub": str(user_id),
        "role": role,
        "tenant_id": str(tenant_id),
        "exp": expire,
        "type": "access",
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token() -> str:
    """Create an opaque refresh token (random 32-byte hex)."""
    return secrets.token_hex(32)


def hash_refresh_token(token: str) -> str:
    """Hash a refresh token with SHA-256 for storage."""
    return hashlib.sha256(token.encode()).hexdigest()


def decode_access_token(token: str) -> dict | None:
    """Decode and validate a JWT access token.

    Returns the payload dict or None if invalid/expired.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        if payload.get("type") != "access":
            return None
        return payload
    except JWTError as exc:
        logger.warning("jwt.decode_failed", error=str(exc))
        return None

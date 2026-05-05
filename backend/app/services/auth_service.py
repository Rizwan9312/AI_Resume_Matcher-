"""Auth service — business logic for authentication and user management."""

from __future__ import annotations

import re
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tenant import Tenant
from app.models.user import RefreshToken, User, UserRole
from app.utils.logger import get_logger
from app.utils.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
    create_verification_token,
)
from app.config import settings

logger = get_logger("auth_service")


def _slugify(name: str) -> str:
    """Convert a name to a URL-safe slug."""
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug[:100]

async def send_verification_email(email: str, token: str):
    """Send verification email using SendGrid HTTP API."""
    if not settings.SENDGRID_API_KEY:
        logger.info("sendgrid_skipped", reason="no_api_key", email=email, token=token)
        return

    import httpx
    # Using backend port for API endpoint route
    verify_url = f"http://localhost:8000/api/v1/auth/verify-email?token={token}"

    payload = {
        "personalizations": [{"to": [{"email": email}]}],
        "from": {"email": settings.FROM_EMAIL, "name": settings.APP_NAME},
        "subject": "Verify your email address",
        "content": [{"type": "text/html", "value": f"<p>Please click the link below to verify your email:</p><p><a href='{verify_url}'>{verify_url}</a></p>"}]
    }

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.sendgrid.com/v3/mail/send",
                headers={"Authorization": f"Bearer {settings.SENDGRID_API_KEY}", "Content-Type": "application/json"},
                json=payload,
            )
            if resp.status_code >= 400:
                logger.error("sendgrid_failed", status=resp.status_code, body=resp.text)
    except Exception as exc:
        logger.error("sendgrid_error", error=str(exc))


async def send_password_reset_email(email: str, token: str):
    """Send password reset email using SendGrid HTTP API."""
    if not settings.SENDGRID_API_KEY:
        logger.info("sendgrid_skipped", reason="no_api_key", email=email, token=token)
        return

    import httpx
    # Using frontend URL for password reset (since it's a frontend page)
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"

    payload = {
        "personalizations": [{"to": [{"email": email}]}],
        "from": {"email": settings.FROM_EMAIL, "name": settings.APP_NAME},
        "subject": "Reset your password",
        "content": [{"type": "text/html", "value": f"<p>Please click the link below to reset your password:</p><p><a href='{reset_url}'>{reset_url}</a></p><p>This link will expire in 1 hour.</p>"}]
    }

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.sendgrid.com/v3/mail/send",
                headers={"Authorization": f"Bearer {settings.SENDGRID_API_KEY}", "Content-Type": "application/json"},
                json=payload,
            )
            if resp.status_code >= 400:
                logger.error("sendgrid_failed", status=resp.status_code, body=resp.text)
    except Exception as exc:
        logger.error("sendgrid_error", error=str(exc))


async def register_user(
    session: AsyncSession,
    email: str,
    password: str,
    full_name: str,
    tenant_slug: str | None = None,
) -> tuple[User, str, str]:
    """Register a new user. Creates a default tenant if none specified.

    Returns (user, access_token, refresh_token).
    Raises ValueError if email already taken.
    """
    # Check existing user
    existing = await session.execute(
        select(User).where(User.email == email, User.deleted_at.is_(None))
    )
    if existing.scalar_one_or_none():
        raise ValueError("email_taken")

    # Get or create tenant
    if tenant_slug:
        tenant_result = await session.execute(
            select(Tenant).where(Tenant.slug == tenant_slug, Tenant.deleted_at.is_(None))
        )
        tenant = tenant_result.scalar_one_or_none()
        if not tenant:
            raise ValueError("tenant_not_found")
    else:
        slug = _slugify(full_name) + "-" + uuid.uuid4().hex[:6]
        tenant = Tenant(name=f"{full_name}'s Workspace", slug=slug)
        session.add(tenant)
        await session.flush()

    # Create user
    user = User(
        tenant_id=tenant.id,
        email=email,
        password_hash=hash_password(password),
        full_name=full_name,
        role=UserRole.JOB_SEEKER,
        is_verified=False,
    )
    session.add(user)
    await session.flush()

    # Generate tokens
    access_token = create_access_token(
        user_id=str(user.id),
        role=user.role.value,
        tenant_id=str(user.tenant_id),
    )
    refresh_token = create_refresh_token()

    # Store refresh token hash
    rt = RefreshToken(
        user_id=user.id,
        token_hash=hash_refresh_token(refresh_token),
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
    )
    session.add(rt)

    # Generate and send verification email
    v_token = create_verification_token(str(user.id))
    await send_verification_email(email, v_token)

    logger.info("user.register", user_id=str(user.id), email=email)
    return user, access_token, refresh_token


async def login_user(
    session: AsyncSession,
    email: str,
    password: str,
) -> tuple[User, str, str]:
    """Authenticate a user by email and password.

    Returns (user, access_token, refresh_token).
    Raises ValueError if credentials are invalid.
    """
    result = await session.execute(
        select(User).where(User.email == email, User.deleted_at.is_(None))
    )
    user = result.scalar_one_or_none()

    if not user or not user.password_hash:
        logger.warning("user.login_failed", email=email, reason="user_not_found")
        raise ValueError("invalid_credentials")

    if not verify_password(password, user.password_hash):
        logger.warning("user.login_failed", email=email, reason="bad_password")
        raise ValueError("invalid_credentials")

    # Update last login
    user.last_login_at = datetime.now(timezone.utc)

    # Generate tokens
    access_token = create_access_token(
        user_id=str(user.id),
        role=user.role.value,
        tenant_id=str(user.tenant_id),
    )
    refresh_token = create_refresh_token()

    # Store refresh token hash
    rt = RefreshToken(
        user_id=user.id,
        token_hash=hash_refresh_token(refresh_token),
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
    )
    session.add(rt)

    logger.info("user.login", user_id=str(user.id))
    return user, access_token, refresh_token


async def refresh_tokens(
    session: AsyncSession,
    refresh_token: str,
) -> tuple[User, str, str]:
    """Rotate refresh token and issue new access token.

    Returns (user, new_access_token, new_refresh_token).
    Raises ValueError if token is invalid/expired/revoked.
    """
    token_hash = hash_refresh_token(refresh_token)

    result = await session.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked_at.is_(None),
        )
    )
    rt = result.scalar_one_or_none()

    if not rt:
        raise ValueError("token_invalid")

    if rt.expires_at < datetime.now(timezone.utc):
        raise ValueError("token_expired")

    # Revoke old token
    rt.revoked_at = datetime.now(timezone.utc)

    # Get user
    user_result = await session.execute(
        select(User).where(User.id == rt.user_id, User.deleted_at.is_(None))
    )
    user = user_result.scalar_one_or_none()
    if not user:
        raise ValueError("user_not_found")

    # Issue new tokens
    new_access = create_access_token(
        user_id=str(user.id),
        role=user.role.value,
        tenant_id=str(user.tenant_id),
    )
    new_refresh = create_refresh_token()
    new_rt = RefreshToken(
        user_id=user.id,
        token_hash=hash_refresh_token(new_refresh),
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
    )
    session.add(new_rt)

    return user, new_access, new_refresh


async def logout_user(session: AsyncSession, refresh_token: str) -> bool:
    """Revoke a refresh token on logout."""
    token_hash = hash_refresh_token(refresh_token)
    result = await session.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked_at.is_(None),
        )
    )
    rt = result.scalar_one_or_none()
    if rt:
        rt.revoked_at = datetime.now(timezone.utc)
        return True
    return False


async def get_user_by_id(session: AsyncSession, user_id: uuid.UUID) -> User | None:
    """Fetch a user by ID (non-deleted only)."""
    result = await session.execute(
        select(User).where(User.id == user_id, User.deleted_at.is_(None))
    )
    return result.scalar_one_or_none()

async def request_password_reset(session: AsyncSession, email: str) -> None:
    """Generate a reset token and send reset email if user exists."""
    import secrets
    import hashlib

    result = await session.execute(
        select(User).where(User.email == email, User.deleted_at.is_(None))
    )
    user = result.scalar_one_or_none()

    if not user:
        # Do not throw error to prevent email enumeration
        return

    raw_token = secrets.token_hex(32)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

    user.reset_token_hash = token_hash
    user.reset_token_expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    await session.commit()

    await send_password_reset_email(email, raw_token)


async def reset_password(session: AsyncSession, token: str, new_password: str) -> None:
    """Reset user password using token."""
    import hashlib

    token_hash = hashlib.sha256(token.encode()).hexdigest()

    result = await session.execute(
        select(User).where(
            User.reset_token_hash == token_hash,
            User.deleted_at.is_(None)
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        raise ValueError("invalid_token")

    if not user.reset_token_expires_at or user.reset_token_expires_at < datetime.now(timezone.utc):
        raise ValueError("token_expired")

    user.password_hash = hash_password(new_password)
    user.reset_token_hash = None
    user.reset_token_expires_at = None
    await session.commit()

"""Auth API routes — register, login, refresh, logout, me."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_session
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    MessageResponse,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth_service import (
    login_user,
    logout_user,
    refresh_tokens,
    register_user,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    body: RegisterRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
):
    """Register a new user account."""
    try:
        user, access_token, refresh_token = await register_user(
            session=session,
            email=body.email,
            password=body.password,
            full_name=body.full_name,
            tenant_slug=body.tenant_slug,
        )
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserResponse.model_validate(user),
        )
    except ValueError as exc:
        error_code = str(exc)
        if error_code == "email_taken":
            raise HTTPException(status_code=409, detail={"code": "email_taken", "message": "Email already registered"})
        if error_code == "tenant_not_found":
            raise HTTPException(status_code=404, detail={"code": "tenant_not_found", "message": "Tenant not found"})
        raise HTTPException(status_code=422, detail={"code": "validation_error", "message": str(exc)})


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
):
    """Authenticate with email and password."""
    try:
        user, access_token, refresh_token = await login_user(
            session=session,
            email=body.email,
            password=body.password,
        )
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserResponse.model_validate(user),
        )
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail={"code": "invalid_credentials", "message": "Invalid email or password"},
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    body: RefreshRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
):
    """Exchange a refresh token for a new token pair."""
    try:
        user, access_token, new_refresh = await refresh_tokens(
            session=session,
            refresh_token=body.refresh_token,
        )
        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh,
            user=UserResponse.model_validate(user),
        )
    except ValueError as exc:
        error_code = str(exc)
        raise HTTPException(
            status_code=401,
            detail={"code": error_code, "message": f"Refresh failed: {error_code}"},
        )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    body: LogoutRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
):
    """Revoke a refresh token."""
    await logout_user(session, body.refresh_token)
    return MessageResponse(success=True, message="Logged out")


@router.get("/me", response_model=UserResponse)
async def me(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Get the currently authenticated user."""
    return UserResponse.model_validate(current_user)

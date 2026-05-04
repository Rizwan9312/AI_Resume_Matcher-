"""User API routes — profile management."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_session
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import ChangePasswordRequest, MessageResponse, UpdateProfileRequest, UserResponse
from app.utils.security import hash_password, verify_password

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile."""
    return UserResponse.model_validate(current_user)


@router.patch("/me", response_model=UserResponse)
async def update_profile(
    body: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """Update current user profile."""
    if body.full_name is not None:
        current_user.full_name = body.full_name
    if body.email is not None:
        current_user.email = body.email
    return UserResponse.model_validate(current_user)


@router.patch("/me/password", response_model=MessageResponse)
async def change_password(
    body: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """Change password for current user."""
    if not current_user.password_hash or not verify_password(
        body.current_password, current_user.password_hash
    ):
        raise HTTPException(
            401, detail={"code": "wrong_current_password", "message": "Current password is incorrect"}
        )
    current_user.password_hash = hash_password(body.new_password)
    return MessageResponse(success=True, message="Password updated")

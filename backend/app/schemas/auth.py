"""Auth schemas — request/response models for authentication endpoints."""

from __future__ import annotations

import uuid
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# ── Request Schemas ───────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=1, max_length=150)
    tenant_slug: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)


class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = Field(None, max_length=150)
    email: Optional[EmailStr] = None


# ── Response Schemas ──────────────────────────────────────────────────────

class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    role: str
    full_name: str
    tenant_id: uuid.UUID
    is_verified: bool

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class MessageResponse(BaseModel):
    success: bool = True
    message: str = "OK"


# ── API Envelope ──────────────────────────────────────────────────────────

class APIResponse(BaseModel):
    """Standard API response envelope."""
    data: Optional[dict] = None
    error: Optional[dict] = None


class ErrorDetail(BaseModel):
    code: str
    message: str

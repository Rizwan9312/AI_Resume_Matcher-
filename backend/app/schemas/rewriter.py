"""Rewriter schemas — request/response models for bullet rewrite endpoints."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class RewriteCreateRequest(BaseModel):
    resume_id: uuid.UUID
    jd_text: str
    match_id: Optional[uuid.UUID] = None


class RewriteResponse(BaseModel):
    id: uuid.UUID
    status: str
    bullet_count: Optional[int] = None
    weak_count: Optional[int] = None
    rewrites: Optional[list] = None
    created_at: datetime

    model_config = {"from_attributes": True}

"""Job description schemas — request/response models."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class JobCreateRequest(BaseModel):
    raw_text: str = Field(..., max_length=50000)
    title: Optional[str] = Field(None, max_length=255)
    company: Optional[str] = Field(None, max_length=255)
    source_url: Optional[str] = Field(None, max_length=500)


class JobResponse(BaseModel):
    id: uuid.UUID
    title: Optional[str]
    company: Optional[str]
    raw_text: str
    parsed_data: Optional[dict] = None
    source_url: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class JobListResponse(BaseModel):
    jobs: list[JobResponse]

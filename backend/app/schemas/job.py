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
    industry_tag: Optional[str] = Field(None, max_length=255)
    role_tag: Optional[str] = Field(None, max_length=255)

class JobResponse(BaseModel):
    id: uuid.UUID
    title: Optional[str]
    company: Optional[str]
    raw_text: str
    parsed_data: Optional[dict] = None
    source_url: Optional[str] = None
    industry_tag: Optional[str] = None
    role_tag: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}

class JobListResponse(BaseModel):
    jobs: list[JobResponse]

class JobUpdateTagsRequest(BaseModel):
    industry_tag: Optional[str] = Field(None, max_length=255)
    role_tag: Optional[str] = Field(None, max_length=255)

class JobLibraryItem(JobResponse):
    best_score: Optional[float] = None
    best_resume_id: Optional[uuid.UUID] = None

class JobLibraryResponse(BaseModel):
    jobs: list[JobLibraryItem]

class KeywordExtractRequest(BaseModel):
    raw_text: str = Field(..., max_length=50000)

class KeywordExtractResponse(BaseModel):
    keywords: list[str]

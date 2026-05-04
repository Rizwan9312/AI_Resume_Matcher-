"""Match schemas — request/response models for match endpoints."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class MatchCreateRequest(BaseModel):
    resume_id: uuid.UUID
    job_id: uuid.UUID


class MatchResponse(BaseModel):
    id: uuid.UUID
    status: str
    resume_id: uuid.UUID
    job_id: uuid.UUID
    final_score: Optional[float] = None
    bert_score: Optional[float] = None
    tfidf_score: Optional[float] = None
    keyword_score: Optional[float] = None
    llm_score: Optional[float] = None
    role_detected: Optional[str] = None
    weights_used: Optional[dict] = None
    score_breakdown: Optional[dict] = None
    matched_keywords: Optional[list] = None
    missing_keywords: Optional[list] = None
    section_scores: Optional[dict] = None
    llm_verdict: Optional[dict] = None
    feedback_text: Optional[str] = None
    processing_ms: Optional[int] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class MatchListResponse(BaseModel):
    matches: list[MatchResponse]
    total: int
    page: int
    limit: int

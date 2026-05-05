"""Resume schemas — request/response models for resume endpoints."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ResumeResponse(BaseModel):
    id: uuid.UUID
    filename: str
    file_size_bytes: int
    mime_type: str
    parse_status: str
    parsed_sections: Optional[dict] = None
    created_at: datetime
    version_number: int = 1
    parent_resume_id: Optional[uuid.UUID] = None
    is_active: bool = True

    model_config = {"from_attributes": True}


class ResumeListResponse(BaseModel):
    resumes: list[ResumeResponse]

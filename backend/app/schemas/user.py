"""User schemas — profile-related request/response models."""

from __future__ import annotations

import uuid
from typing import Optional

from pydantic import BaseModel


class UserProfileResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    role: str
    subscription_plan: str = "free"

    model_config = {"from_attributes": True}

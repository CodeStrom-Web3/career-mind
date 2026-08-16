"""Pydantic schemas for career profile endpoints."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ProfileUpdate(BaseModel):
    """Request body for creating or updating a career profile."""
    dream_role: Optional[str] = None
    preferred_role: Optional[str] = None
    experience_level: Optional[str] = None
    education: Optional[str] = None
    industry: Optional[str] = None
    timeline: Optional[str] = None
    bio: Optional[str] = None


class ProfileResponse(BaseModel):
    """Career profile response."""
    id: uuid.UUID
    user_id: uuid.UUID
    dream_role: str = ""
    preferred_role: str = ""
    experience_level: str = ""
    education: str = ""
    industry: str = ""
    timeline: str = ""
    bio: str = ""
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

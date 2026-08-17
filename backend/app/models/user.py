"""Pydantic schemas for user registration, login, and token responses."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# ── Request Schemas ───────────────────────────────────────────────────────


class UserCreate(BaseModel):
    """Registration request body."""
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    """Login request body."""
    email: EmailStr
    password: str


# ── Response Schemas ──────────────────────────────────────────────────────


class UserResponse(BaseModel):
    """Public user representation (never includes password_hash)."""
    id: uuid.UUID
    email: str
    full_name: Optional[str] = ""
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """JWT access-token response."""
    access_token: str
    token_type: str = "bearer"

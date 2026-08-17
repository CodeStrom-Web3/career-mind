"""Pydantic schemas for the memory system."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


from typing import Optional, Self
from pydantic import BaseModel, Field, model_validator


class MemoryType(str, Enum):
    """Allowed memory type values."""
    CAREER_GOAL = "career_goal"
    SKILL = "skill"
    PROJECT = "project"
    COURSE = "course"
    LEARNING_GAP = "learning_gap"
    PREFERENCE = "preference"
    ACHIEVEMENT = "achievement"
    EXPERIENCE = "experience"
    GENERAL = "general"


class MemoryCreate(BaseModel):
    """Request body for manually creating a memory."""
    memory_type: Optional[str] = None
    category: Optional[str] = None
    content: str = Field(..., min_length=1, max_length=5000)
    importance: float = Field(default=0.5, ge=0.0, le=1.0)
    confidence: Optional[float] = None
    source: str = Field(default="manual", max_length=100)

    @model_validator(mode="after")
    def normalize_fields(self) -> Self:
        if not self.memory_type and self.category:
            self.memory_type = self.category
        if not self.memory_type:
            self.memory_type = "general"
        if self.confidence is not None and self.importance == 0.5:
            self.importance = self.confidence
        return self


from pydantic import BaseModel, Field, computed_field


class MemoryResponse(BaseModel):
    """Memory response representation."""
    id: uuid.UUID
    user_id: uuid.UUID
    memory_type: str
    content: str
    importance: float
    source: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

    @computed_field
    @property
    def category(self) -> str:
        return self.memory_type

    @computed_field
    @property
    def confidence(self) -> float:
        return self.importance


class ExtractedMemory(BaseModel):
    """A single memory fact extracted by the LLM."""
    type: str = "general"
    content: str = Field(..., min_length=1)
    importance: float = Field(default=0.5, ge=0.0, le=1.0)


class ExtractedMemories(BaseModel):
    """Wrapper for the list of memories extracted from a conversation."""
    memories: list[ExtractedMemory] = Field(default_factory=list)

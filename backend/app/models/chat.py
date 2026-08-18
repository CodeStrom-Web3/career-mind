"""Pydantic schemas for the chat endpoint."""

from __future__ import annotations

import uuid
from typing import Any, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request body for ``POST /api/chat``."""
    message: str = Field(..., min_length=1, max_length=10_000)
    conversation_id: Optional[uuid.UUID] = None
    user_context: Optional[dict[str, Any]] = None


class ChatResponse(BaseModel):
    """Response body returned by the chat endpoint."""
    response: str
    role: str = "ai"
    conversation_id: uuid.UUID
    memories_used: int = 0
    reasoning_steps: int = 0
    suggestions: list[str] = []
    confidence: float = 0.0

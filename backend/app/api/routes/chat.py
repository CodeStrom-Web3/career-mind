"""
Chat route — thin endpoint delegating to the agent service.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db
from app.db.models import User
from app.models.chat import ChatRequest, ChatResponse
from app.services.agent_service import get_agent_service
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api", tags=["Chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    body: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Process a chat message through the agentic pipeline.

    The route is intentionally thin — all orchestration logic lives in
    ``agent_service.process_chat``.
    """
    try:
        result = await get_agent_service().process_chat(
            db=db,
            user_id=current_user.id,
            message=body.message,
            conversation_id=body.conversation_id,
            user_context=body.user_context,
        )
        return ChatResponse(
            response=result["response"],
            role=result["role"],
            conversation_id=uuid.UUID(result["conversation_id"]),
            memories_used=result["memories_used"],
            reasoning_steps=result.get("reasoning_steps", 0),
            suggestions=result.get("suggestions", []),
            confidence=result.get("confidence", 0.0),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except RuntimeError as exc:
        logger.error("Chat processing failed", exc_info=exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service temporarily unavailable",
        )

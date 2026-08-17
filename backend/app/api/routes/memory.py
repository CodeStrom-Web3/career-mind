"""
Memory routes — list, create, and delete persistent memories.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db
from app.db.models import User
from app.models.memory import MemoryCreate, MemoryResponse
from app.services.memory_service import get_memory_service

router = APIRouter(prefix="/api/memory", tags=["Memory"])


@router.get("", response_model=list[MemoryResponse])
async def list_memories(
    memory_type: str | None = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List the authenticated user's memories, optionally filtered by type."""
    memories = await get_memory_service().list_memories(
        db, current_user.id, memory_type=memory_type, limit=limit,
    )
    return memories


@router.post(
    "",
    response_model=MemoryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_memory(
    body: MemoryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Manually create a new memory with automatic embedding and dedup."""
    memory = await get_memory_service().create_memory(
        db=db,
        user_id=current_user.id,
        memory_type=body.memory_type or "general",
        content=body.content,
        importance=body.importance,
        source=body.source,
    )
    return memory


@router.delete("/{memory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_memory(
    memory_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a memory owned by the authenticated user."""
    deleted = await get_memory_service().delete_memory(
        db, memory_id, current_user.id,
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Memory not found",
        )

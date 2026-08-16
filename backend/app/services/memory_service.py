"""
Memory service — create, update, delete, list, extract, and deduplicate
persistent memories in CockroachDB.

Implements the full memory lifecycle:
  Raw fact → classify → embed → search duplicates → upsert
"""

from __future__ import annotations

import uuid
from typing import Any, Optional, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import get_settings
from app.db import queries
from app.db.models import Memory
from app.services.embedding_service import get_embedding_service
from app.utils.helpers import cosine_similarity
from app.utils.logger import get_logger

logger = get_logger(__name__)

VALID_MEMORY_TYPES = {
    "career_goal", "skill", "project", "course",
    "learning_gap", "preference", "achievement",
    "experience", "general",
}


class MemoryService:
    """Business logic for the persistent memory system."""

    def __init__(self) -> None:
        self._settings = get_settings()
        self._embedding = get_embedding_service()

    # ── Public CRUD ───────────────────────────────────────────────────────

    async def create_memory(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        memory_type: str,
        content: str,
        importance: float = 0.5,
        source: str = "conversation",
    ) -> Memory:
        """
        Create a new memory with embedding and deduplication.

        If a near-duplicate is found above the configured threshold the
        existing memory is updated instead.
        """
        memory_type = self._normalise_type(memory_type)

        # Generate embedding
        try:
            embedding = await self._embedding.generate_embedding(content)
        except Exception as exc:
            logger.warning(
                "Embedding generation failed; storing memory without vector",
                exc_info=exc,
                extra={"service": "memory"},
            )
            embedding = None

        # Deduplication check
        if embedding:
            existing = await self._find_duplicate(db, user_id, embedding)
            if existing:
                logger.info(
                    "Near-duplicate memory found — updating",
                    extra={
                        "service": "memory",
                        "existing_id": existing["id"],
                    },
                )
                mem = await queries.update_memory(
                    db,
                    uuid.UUID(existing["id"]),
                    user_id,
                    {
                        "content": content,
                        "embedding": embedding,
                        "importance": max(importance, existing.get("importance", 0.5)),
                        "memory_type": memory_type,
                    },
                )
                if mem:
                    return mem

        return await queries.create_memory(
            db,
            user_id=user_id,
            memory_type=memory_type,
            content=content,
            embedding=embedding,
            importance=importance,
            source=source,
        )

    async def update_memory(
        self,
        db: AsyncSession,
        memory_id: uuid.UUID,
        user_id: uuid.UUID,
        data: dict[str, Any],
    ) -> Memory | None:
        """Update an existing memory (user-scoped)."""
        # Re-embed if content changed
        if "content" in data and data["content"]:
            try:
                data["embedding"] = await self._embedding.generate_embedding(data["content"])
            except Exception:
                pass  # keep old embedding
        return await queries.update_memory(db, memory_id, user_id, data)

    async def delete_memory(
        self,
        db: AsyncSession,
        memory_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> bool:
        """Delete a memory (user-scoped)."""
        return await queries.delete_memory(db, memory_id, user_id)

    async def list_memories(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        memory_type: Optional[str] = None,
        limit: int = 50,
    ) -> Sequence[Memory]:
        """List memories for a user."""
        return await queries.get_user_memories(db, user_id, memory_type, limit)

    # ── Extraction & Deduplication ────────────────────────────────────────

    async def process_extracted_memories(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        raw_memories: list[dict[str, Any]],
        source: str = "conversation",
    ) -> list[Memory]:
        """
        Take a list of raw extracted memory dicts from the LLM, embed,
        deduplicate, and persist them.
        """
        created: list[Memory] = []
        for raw in raw_memories:
            content = raw.get("content", "").strip()
            if not content:
                continue
            mem_type = raw.get("type", "general")
            importance = float(raw.get("importance", 0.5))
            try:
                mem = await self.create_memory(
                    db, user_id, mem_type, content, importance, source,
                )
                created.append(mem)
            except Exception as exc:
                logger.error(
                    "Failed to process extracted memory",
                    exc_info=exc,
                    extra={"service": "memory"},
                )
        return created

    # ── Internal helpers ──────────────────────────────────────────────────

    async def _find_duplicate(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        embedding: list[float],
    ) -> dict[str, Any] | None:
        """
        Search existing memories and return the first match whose
        similarity exceeds ``MEMORY_DEDUP_THRESHOLD``.
        """
        results = await queries.vector_search_memories(
            db, user_id, embedding, limit=3,
        )
        threshold = self._settings.memory_dedup_threshold
        for result in results:
            if result.get("similarity", 0) >= threshold:
                return result
        return None

    @staticmethod
    def _normalise_type(memory_type: str) -> str:
        """Normalise and validate a memory type string."""
        mt = memory_type.strip().lower()
        return mt if mt in VALID_MEMORY_TYPES else "general"


# ── Module-level singleton accessor ───────────────────────────────────────

_instance: MemoryService | None = None


def get_memory_service() -> MemoryService:
    """Return a lazily-initialised singleton."""
    global _instance
    if _instance is None:
        _instance = MemoryService()
    return _instance

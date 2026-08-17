"""
Semantic memory retrieval service.

Flow:
  User Message → Generate Query Embedding → CockroachDB Vector Search
  → Similarity Ranking → Top-K Memories

Uses weighted scoring combining semantic similarity, importance, and recency.
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import get_settings
from app.db import queries
from app.services.embedding_service import get_embedding_service
from app.utils.logger import get_logger, Timer

logger = get_logger(__name__)


class RetrievalService:
    """Semantic memory retrieval using vector embeddings."""

    def __init__(self) -> None:
        self._settings = get_settings()
        self._embedding = get_embedding_service()

    async def retrieve_relevant_memories(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        query_text: str,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        Retrieve the most relevant memories for a user given a query.

        Steps:
        1. Generate query embedding via Titan Embed.
        2. Perform vector similarity search in CockroachDB.
        3. Return top-K results ranked by weighted score.

        User isolation is enforced at the query layer.

        Args:
            db: Async database session.
            user_id: The authenticated user's ID.
            query_text: The user's current message or search query.
            limit: Maximum number of results (defaults to config TOP_K_MEMORIES).

        Returns:
            A list of memory dicts sorted by weighted relevance score.
        """
        if limit is None:
            limit = self._settings.top_k_memories

        with Timer() as t:
            try:
                # Step 1 — Embed the query
                query_embedding = await self._embedding.generate_embedding(query_text)

                # Step 2 + 3 — Vector search with ranking
                results = await queries.vector_search_memories(
                    db,
                    user_id=user_id,
                    query_embedding=query_embedding,
                    limit=limit,
                )

                logger.info(
                    "Memory retrieval completed",
                    extra={
                        "service": "retrieval",
                        "user_id": str(user_id),
                        "results": len(results),
                        "duration_ms": t.elapsed_ms,
                    },
                )
                return results

            except Exception as exc:
                logger.error(
                    "Memory retrieval failed",
                    exc_info=exc,
                    extra={
                        "service": "retrieval",
                        "user_id": str(user_id),
                        "duration_ms": t.elapsed_ms,
                    },
                )
                return []


# ── Module-level singleton accessor ───────────────────────────────────────

_instance: RetrievalService | None = None


def get_retrieval_service() -> RetrievalService:
    """Return a lazily-initialised singleton."""
    global _instance
    if _instance is None:
        _instance = RetrievalService()
    return _instance

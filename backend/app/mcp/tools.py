"""
MCP-compatible database-backed tools.

Each tool is exposed as a callable that the MCP client / agent can
invoke.  Tools delegate to the retrieval service rather than
implementing their own DB/vector-search logic.
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.retrieval_service import get_retrieval_service
from app.utils.logger import get_logger

logger = get_logger(__name__)


# ── Tool definitions (MCP-compatible schema) ─────────────────────────────

TOOL_DEFINITIONS: list[dict[str, Any]] = [
    {
        "name": "search_user_memory",
        "description": (
            "Search the user's persistent career memories using semantic "
            "similarity.  Returns the most relevant memories ranked by a "
            "weighted score combining similarity, importance, and recency."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "UUID of the user whose memories to search.",
                },
                "query": {
                    "type": "string",
                    "description": "Natural-language query to match against memories.",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default 5).",
                    "default": 5,
                },
            },
            "required": ["user_id", "query"],
        },
    },
]


# ── Tool implementations ─────────────────────────────────────────────────


async def search_user_memory(
    db: AsyncSession,
    user_id: str,
    query: str,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """
    Search a user's persistent memories via semantic similarity.

    This is the MCP-callable entry point that delegates entirely to the
    retrieval service.

    Args:
        db: Active database session.
        user_id: UUID string of the target user.
        query: Natural-language search query.
        limit: Max results to return.

    Returns:
        A list of memory dicts sorted by relevance.
    """
    retrieval = get_retrieval_service()
    try:
        uid = uuid.UUID(user_id)
    except ValueError:
        logger.warning("Invalid user_id for MCP tool", extra={"user_id": user_id})
        return []

    results = await retrieval.retrieve_relevant_memories(
        db, uid, query, limit=limit,
    )
    logger.info(
        "MCP search_user_memory executed",
        extra={
            "service": "mcp",
            "user_id": user_id,
            "results": len(results),
        },
    )
    return results


# ── Tool registry (name → callable) ──────────────────────────────────────

TOOL_REGISTRY: dict[str, Any] = {
    "search_user_memory": search_user_memory,
}

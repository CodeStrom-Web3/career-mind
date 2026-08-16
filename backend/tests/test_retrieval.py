"""
Tests for the retrieval service — embedding generation, vector search,
top-K behaviour, ranking, and user isolation.

All external services (Bedrock, database) are mocked.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.retrieval_service import RetrievalService


@pytest.fixture
def user_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def other_user_id() -> uuid.UUID:
    return uuid.uuid4()


def _fake_memory(uid, content, similarity=0.9, importance=0.7):
    return {
        "id": str(uuid.uuid4()),
        "user_id": str(uid),
        "memory_type": "general",
        "content": content,
        "importance": importance,
        "similarity": similarity,
        "weighted_score": round(similarity * 0.6 + importance * 0.25 + 0.1, 4),
        "source": "test",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


@pytest.mark.asyncio
async def test_embedding_generation_mocked(user_id):
    """Retrieval service calls the embedding service to vectorise the query."""
    fake_embedding = [0.1] * 1024

    with patch(
        "app.services.retrieval_service.get_embedding_service"
    ) as mock_emb:
        mock_emb.return_value.generate_embedding = AsyncMock(return_value=fake_embedding)

        with patch("app.services.retrieval_service.queries") as mock_q:
            mock_q.vector_search_memories = AsyncMock(return_value=[])

            svc = RetrievalService()
            svc._embedding = mock_emb.return_value

            db = AsyncMock()
            results = await svc.retrieve_relevant_memories(db, user_id, "test query")

            mock_emb.return_value.generate_embedding.assert_awaited_once_with("test query")
            assert results == []


@pytest.mark.asyncio
async def test_vector_retrieval(user_id):
    """Retrieval service returns memories from vector search."""
    fake_embedding = [0.1] * 1024
    memories = [
        _fake_memory(user_id, "User wants to learn Python", 0.95),
        _fake_memory(user_id, "User is a beginner", 0.80),
    ]

    with patch(
        "app.services.retrieval_service.get_embedding_service"
    ) as mock_emb:
        mock_emb.return_value.generate_embedding = AsyncMock(return_value=fake_embedding)

        with patch("app.services.retrieval_service.queries") as mock_q:
            mock_q.vector_search_memories = AsyncMock(return_value=memories)

            svc = RetrievalService()
            svc._embedding = mock_emb.return_value

            db = AsyncMock()
            results = await svc.retrieve_relevant_memories(db, user_id, "Python learning")

    assert len(results) == 2
    assert results[0]["content"] == "User wants to learn Python"


@pytest.mark.asyncio
async def test_top_k_behaviour(user_id):
    """Retrieval respects the limit parameter."""
    fake_embedding = [0.1] * 1024
    many_memories = [
        _fake_memory(user_id, f"Memory {i}", 0.9 - i * 0.05)
        for i in range(10)
    ]

    with patch(
        "app.services.retrieval_service.get_embedding_service"
    ) as mock_emb:
        mock_emb.return_value.generate_embedding = AsyncMock(return_value=fake_embedding)

        with patch("app.services.retrieval_service.queries") as mock_q:
            # Simulate the DB returning only top-3
            mock_q.vector_search_memories = AsyncMock(return_value=many_memories[:3])

            svc = RetrievalService()
            svc._embedding = mock_emb.return_value

            db = AsyncMock()
            results = await svc.retrieve_relevant_memories(db, user_id, "test", limit=3)

    assert len(results) == 3


@pytest.mark.asyncio
async def test_user_isolation(user_id, other_user_id):
    """Retrieval must not return another user's memories."""
    fake_embedding = [0.1] * 1024

    user_a_mem = _fake_memory(user_id, "User A memory", 0.95)

    with patch(
        "app.services.retrieval_service.get_embedding_service"
    ) as mock_emb:
        mock_emb.return_value.generate_embedding = AsyncMock(return_value=fake_embedding)

        with patch("app.services.retrieval_service.queries") as mock_q:
            # The query layer only returns memories for the requested user_id
            async def _scoped_search(db, user_id=None, query_embedding=None, limit=5):
                if user_id == user_id_val:
                    return [user_a_mem]
                return []

            user_id_val = user_id
            mock_q.vector_search_memories = _scoped_search

            svc = RetrievalService()
            svc._embedding = mock_emb.return_value

            db = AsyncMock()

            # User A gets their memory
            results_a = await svc.retrieve_relevant_memories(db, user_id, "test")
            assert len(results_a) == 1

            # User B gets nothing
            results_b = await svc.retrieve_relevant_memories(db, other_user_id, "test")
            assert len(results_b) == 0

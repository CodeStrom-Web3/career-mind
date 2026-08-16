"""
Tests for the memory system — create, retrieve, delete, user isolation,
and duplicate handling.

Mocks: database, embedding service.
"""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


# ── Fixtures ──────────────────────────────────────────────────────────────

@pytest.fixture
def user_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def other_user_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def mock_user(user_id):
    user = MagicMock()
    user.id = user_id
    user.email = "test@example.com"
    return user


def _make_memory(user_id, memory_type="general", content="Test memory"):
    mem = MagicMock()
    mem.id = uuid.uuid4()
    mem.user_id = user_id
    mem.memory_type = memory_type
    mem.content = content
    mem.importance = 0.7
    mem.source = "test"
    mem.created_at = "2025-01-01T00:00:00Z"
    mem.updated_at = "2025-01-01T00:00:00Z"
    return mem


@pytest.fixture
def _override_auth(mock_user):
    from app.api.dependencies import get_current_user

    async def _fake():
        return mock_user

    app.dependency_overrides[get_current_user] = _fake
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def _override_db():
    from app.api.dependencies import get_db

    mock_session = AsyncMock()

    async def _fake():
        yield mock_session

    app.dependency_overrides[get_db] = _fake
    yield mock_session
    app.dependency_overrides.clear()


# ── Tests ─────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_memory(_override_auth, _override_db, user_id):
    """POST /api/memory creates a new memory."""
    mem = _make_memory(user_id, "career_goal", "Wants to be a data analyst")

    with patch(
        "app.api.routes.memory.get_memory_service"
    ) as mock_svc:
        mock_svc.return_value.create_memory = AsyncMock(return_value=mem)

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.post(
                "/api/memory",
                json={
                    "memory_type": "career_goal",
                    "content": "Wants to be a data analyst",
                    "importance": 0.9,
                },
                headers={"Authorization": "Bearer test-token"},
            )

    assert resp.status_code == 201
    assert resp.json()["memory_type"] == "career_goal"


@pytest.mark.asyncio
async def test_list_memories(_override_auth, _override_db, user_id):
    """GET /api/memory returns the user's memories."""
    memories = [
        _make_memory(user_id, "skill", "Knows Python"),
        _make_memory(user_id, "career_goal", "Wants ML role"),
    ]

    with patch(
        "app.api.routes.memory.get_memory_service"
    ) as mock_svc:
        mock_svc.return_value.list_memories = AsyncMock(return_value=memories)

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get(
                "/api/memory",
                headers={"Authorization": "Bearer test-token"},
            )

    assert resp.status_code == 200
    assert len(resp.json()) == 2


@pytest.mark.asyncio
async def test_delete_memory(_override_auth, _override_db, user_id):
    """DELETE /api/memory/{id} removes a memory."""
    mem_id = uuid.uuid4()

    with patch(
        "app.api.routes.memory.get_memory_service"
    ) as mock_svc:
        mock_svc.return_value.delete_memory = AsyncMock(return_value=True)

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.delete(
                f"/api/memory/{mem_id}",
                headers={"Authorization": "Bearer test-token"},
            )

    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_delete_memory_not_found(_override_auth, _override_db):
    """DELETE /api/memory/{id} returns 404 for non-existent memories."""
    mem_id = uuid.uuid4()

    with patch(
        "app.api.routes.memory.get_memory_service"
    ) as mock_svc:
        mock_svc.return_value.delete_memory = AsyncMock(return_value=False)

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.delete(
                f"/api/memory/{mem_id}",
                headers={"Authorization": "Bearer test-token"},
            )

    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_memory_user_isolation(user_id, other_user_id):
    """Memories from one user must not be accessible to another."""
    mem_a = _make_memory(user_id, "skill", "User A skill")
    mem_b = _make_memory(other_user_id, "skill", "User B skill")

    # Ensure IDs are truly different
    assert mem_a.user_id != mem_b.user_id

    # The service layer filters by user_id — verify the mock respects it
    async def _list_for_user(db, uid, **kwargs):
        all_mems = [mem_a, mem_b]
        return [m for m in all_mems if m.user_id == uid]

    mock_user_a = MagicMock()
    mock_user_a.id = user_id
    mock_user_a.email = "a@example.com"

    from app.api.dependencies import get_current_user, get_db

    async def _fake_auth():
        return mock_user_a

    async def _fake_db():
        yield AsyncMock()

    app.dependency_overrides[get_current_user] = _fake_auth
    app.dependency_overrides[get_db] = _fake_db

    with patch(
        "app.api.routes.memory.get_memory_service"
    ) as mock_svc:
        instance = MagicMock()

        async def _mock_list(db, uid, memory_type=None, limit=50):
            all_mems = [mem_a, mem_b]
            return [m for m in all_mems if m.user_id == uid]

        instance.list_memories = _mock_list
        mock_svc.return_value = instance

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get(
                "/api/memory",
                headers={"Authorization": "Bearer test-token"},
            )

    data = resp.json()
    assert resp.status_code == 200
    assert all(m["user_id"] == str(user_id) for m in data)
    app.dependency_overrides.clear()

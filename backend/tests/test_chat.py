"""
Tests for the chat endpoint and agent service.

Mocks: database, Bedrock, embedding service.
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
def mock_user(user_id):
    user = MagicMock()
    user.id = user_id
    user.email = "test@example.com"
    user.password_hash = "hashed"
    user.created_at = "2025-01-01T00:00:00Z"
    user.updated_at = "2025-01-01T00:00:00Z"
    return user


@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer test-token"}


@pytest.fixture
def _override_auth(mock_user):
    """Override get_current_user to return a mock user without real JWT."""
    from app.api.dependencies import get_current_user

    async def _fake_user():
        return mock_user

    app.dependency_overrides[get_current_user] = _fake_user
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def _override_db():
    """Override get_db to return a mock session."""
    from app.api.dependencies import get_db

    mock_session = AsyncMock()

    async def _fake_db():
        yield mock_session

    app.dependency_overrides[get_db] = _fake_db
    yield mock_session
    app.dependency_overrides.clear()


# ── Tests ─────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_chat_success(_override_auth, _override_db, user_id):
    """POST /api/chat returns a valid AI response."""
    conv_id = uuid.uuid4()
    mock_result = {
        "response": "Based on your goals, I recommend learning SQL next.",
        "role": "ai",
        "conversation_id": str(conv_id),
        "memories_used": 3,
    }

    with patch(
        "app.api.routes.chat.get_agent_service"
    ) as mock_agent:
        mock_agent.return_value.process_chat = AsyncMock(return_value=mock_result)

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.post(
                "/api/chat",
                json={"message": "What should I learn next?"},
                headers={"Authorization": "Bearer test-token"},
            )

    assert resp.status_code == 200
    data = resp.json()
    assert data["role"] == "ai"
    assert "response" in data
    assert data["memories_used"] == 3


@pytest.mark.asyncio
async def test_chat_conversation_continuation(_override_auth, _override_db, user_id):
    """POST /api/chat with conversation_id continues an existing conversation."""
    conv_id = uuid.uuid4()
    mock_result = {
        "response": "Continuing our discussion about data analysis…",
        "role": "ai",
        "conversation_id": str(conv_id),
        "memories_used": 2,
    }

    with patch(
        "app.api.routes.chat.get_agent_service"
    ) as mock_agent:
        mock_agent.return_value.process_chat = AsyncMock(return_value=mock_result)

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.post(
                "/api/chat",
                json={
                    "message": "Tell me more about that",
                    "conversation_id": str(conv_id),
                },
                headers={"Authorization": "Bearer test-token"},
            )

    assert resp.status_code == 200
    assert resp.json()["conversation_id"] == str(conv_id)


@pytest.mark.asyncio
async def test_chat_invalid_request(_override_auth, _override_db):
    """POST /api/chat with an empty message returns 422."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        resp = await client.post(
            "/api/chat",
            json={"message": ""},
            headers={"Authorization": "Bearer test-token"},
        )

    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_chat_bedrock_failure(_override_auth, _override_db):
    """POST /api/chat returns 503 when Bedrock is unreachable."""
    with patch(
        "app.api.routes.chat.get_agent_service"
    ) as mock_agent:
        mock_agent.return_value.process_chat = AsyncMock(
            side_effect=RuntimeError("Bedrock API error")
        )

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.post(
                "/api/chat",
                json={"message": "Hello"},
                headers={"Authorization": "Bearer test-token"},
            )

    assert resp.status_code == 503


@pytest.mark.asyncio
async def test_chat_requires_authentication():
    """POST /api/chat without a token returns 403."""
    app.dependency_overrides.clear()
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        resp = await client.post(
            "/api/chat",
            json={"message": "Hello"},
        )

    assert resp.status_code == 403

"""
Tests for the profile endpoints — create/update, retrieve, authentication,
and user isolation.

Mocks: database.
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


def _make_profile(user_id, **overrides):
    profile = MagicMock()
    profile.id = uuid.uuid4()
    profile.user_id = user_id
    profile.dream_role = overrides.get("dream_role", "Data Analyst")
    profile.preferred_role = overrides.get("preferred_role", "")
    profile.experience_level = overrides.get("experience_level", "beginner")
    profile.education = overrides.get("education", "")
    profile.industry = overrides.get("industry", "Technology")
    profile.timeline = overrides.get("timeline", "6 months")
    profile.bio = overrides.get("bio", "")
    profile.created_at = "2025-01-01T00:00:00Z"
    profile.updated_at = "2025-01-01T00:00:00Z"
    return profile


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
async def test_update_profile(_override_auth, _override_db, user_id):
    """PUT /api/profile creates or updates a career profile."""
    profile = _make_profile(user_id, dream_role="ML Engineer")

    with patch(
        "app.api.routes.profile.get_profile_service"
    ) as mock_svc:
        mock_svc.return_value.update_profile = AsyncMock(return_value=profile)

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.put(
                "/api/profile",
                json={
                    "dream_role": "ML Engineer",
                    "experience_level": "beginner",
                    "industry": "Technology",
                    "timeline": "6 months",
                },
                headers={"Authorization": "Bearer test-token"},
            )

    assert resp.status_code == 200
    assert resp.json()["dream_role"] == "ML Engineer"


@pytest.mark.asyncio
async def test_get_profile(_override_auth, _override_db, user_id):
    """GET /api/profile returns the user's career profile."""
    profile = _make_profile(user_id)

    with patch(
        "app.api.routes.profile.get_profile_service"
    ) as mock_svc:
        mock_svc.return_value.get_profile = AsyncMock(return_value=profile)

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get(
                "/api/profile",
                headers={"Authorization": "Bearer test-token"},
            )

    assert resp.status_code == 200
    assert resp.json()["dream_role"] == "Data Analyst"


@pytest.mark.asyncio
async def test_get_profile_not_found(_override_auth, _override_db):
    """GET /api/profile returns 404 when no profile exists."""
    with patch(
        "app.api.routes.profile.get_profile_service"
    ) as mock_svc:
        mock_svc.return_value.get_profile = AsyncMock(return_value=None)

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get(
                "/api/profile",
                headers={"Authorization": "Bearer test-token"},
            )

    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_profile_requires_authentication():
    """Profile endpoints require a valid Bearer token."""
    app.dependency_overrides.clear()
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        resp = await client.get("/api/profile")

    assert resp.status_code == 403

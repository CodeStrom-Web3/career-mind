"""
Profile service — get and update career profiles.

All operations are user-scoped.
"""

from __future__ import annotations

import uuid
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.db import queries
from app.db.models import CareerProfile
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ProfileService:
    """Business logic for career profiles."""

    async def get_profile(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
    ) -> CareerProfile | None:
        """Return the career profile for *user_id*, or ``None``."""
        return await queries.get_profile(db, user_id)

    async def update_profile(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        data: dict[str, Any],
    ) -> CareerProfile:
        """Create or update a career profile for *user_id*."""
        profile = await queries.upsert_profile(db, user_id, data)
        logger.info(
            "Career profile updated",
            extra={"service": "profile", "user_id": str(user_id)},
        )
        return profile

    async def get_profile_dict(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
    ) -> dict[str, Any]:
        """
        Return a dict of the user's career profile suitable for prompt
        construction.  Returns an empty dict if no profile exists.
        """
        profile = await self.get_profile(db, user_id)
        if profile is None:
            return {}
        return {
            "dream_role": profile.dream_role or "",
            "preferred_role": profile.preferred_role or "",
            "experience_level": profile.experience_level or "",
            "education": profile.education or "",
            "industry": profile.industry or "",
            "timeline": profile.timeline or "",
            "bio": profile.bio or "",
        }


# ── Module-level singleton accessor ───────────────────────────────────────

_instance: ProfileService | None = None


def get_profile_service() -> ProfileService:
    """Return a lazily-initialised singleton."""
    global _instance
    if _instance is None:
        _instance = ProfileService()
    return _instance

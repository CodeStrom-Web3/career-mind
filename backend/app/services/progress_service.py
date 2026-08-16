"""
Progress service — CRUD for skills, projects, courses, and learning progress.

All operations are user-scoped.
"""

from __future__ import annotations

import uuid
from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.db import queries
from app.db.models import Course, LearningProgress, Project, Skill
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ProgressService:
    """Manages skills, projects, courses, and learning progress."""

    # ── Skills ────────────────────────────────────────────────────────────

    async def get_skills(self, db: AsyncSession, user_id: uuid.UUID) -> Sequence[Skill]:
        return await queries.get_user_skills(db, user_id)

    async def upsert_skill(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        name: str,
        level: str = "beginner",
        status: str = "learning",
    ) -> Skill:
        return await queries.upsert_skill(db, user_id, name, level, status)

    # ── Projects ──────────────────────────────────────────────────────────

    async def get_projects(self, db: AsyncSession, user_id: uuid.UUID) -> Sequence[Project]:
        return await queries.get_user_projects(db, user_id)

    async def upsert_project(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        name: str,
        description: str = "",
        technology: str = "",
        status: str = "planned",
    ) -> Project:
        return await queries.upsert_project(db, user_id, name, description, technology, status)

    # ── Courses ───────────────────────────────────────────────────────────

    async def get_courses(self, db: AsyncSession, user_id: uuid.UUID) -> Sequence[Course]:
        return await queries.get_user_courses(db, user_id)

    async def upsert_course(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        name: str,
        provider: str = "",
        status: str = "not_started",
        progress: float = 0.0,
    ) -> Course:
        return await queries.upsert_course(db, user_id, name, provider, status, progress)

    # ── Learning Progress ─────────────────────────────────────────────────

    async def get_progress(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
    ) -> LearningProgress | None:
        return await queries.get_learning_progress(db, user_id)

    async def update_progress(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        data: dict[str, Any],
    ) -> LearningProgress:
        return await queries.upsert_learning_progress(db, user_id, data)

    # ── Aggregated dashboard ──────────────────────────────────────────────

    async def get_dashboard(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
    ) -> dict[str, Any]:
        """Return a combined progress dashboard."""
        skills = await self.get_skills(db, user_id)
        projects = await self.get_projects(db, user_id)
        courses = await self.get_courses(db, user_id)
        progress = await self.get_progress(db, user_id)

        return {
            "skills": [
                {"name": s.name, "level": s.level, "status": s.status}
                for s in skills
            ],
            "projects": [
                {
                    "name": p.name,
                    "description": p.description,
                    "technology": p.technology,
                    "status": p.status,
                }
                for p in projects
            ],
            "courses": [
                {
                    "name": c.name,
                    "provider": c.provider,
                    "status": c.status,
                    "progress": c.progress,
                }
                for c in courses
            ],
            "learning_progress": {
                "streak": progress.streak if progress else 0,
                "hours": progress.hours if progress else 0.0,
                "level": progress.level if progress else "beginner",
            },
        }


# ── Module-level singleton accessor ───────────────────────────────────────

_instance: ProgressService | None = None


def get_progress_service() -> ProgressService:
    """Return a lazily-initialised singleton."""
    global _instance
    if _instance is None:
        _instance = ProgressService()
    return _instance

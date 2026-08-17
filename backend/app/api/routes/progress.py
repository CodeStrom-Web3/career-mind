"""
Progress routes — skills, projects, courses, and learning progress.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db
from app.db.models import User
from app.services.progress_service import get_progress_service

router = APIRouter(prefix="/api/progress", tags=["Progress"])


# ── Request schemas (local to this route) ─────────────────────────────────

class ProgressUpdate(BaseModel):
    streak: int | None = None
    hours: float | None = None
    level: str | None = None


class SkillItem(BaseModel):
    name: str
    level: str = "beginner"
    status: str = "learning"


class ProjectItem(BaseModel):
    name: str
    description: str = ""
    technology: str = ""
    status: str = "planned"


class CourseItem(BaseModel):
    name: str
    provider: str = ""
    status: str = "not_started"
    progress: float = 0.0


# ── Response schemas ──────────────────────────────────────────────────────

class SkillResponse(BaseModel):
    name: str
    level: str
    status: str
    model_config = {"from_attributes": True}


class ProjectResponse(BaseModel):
    name: str
    description: str
    technology: str
    status: str
    model_config = {"from_attributes": True}


class CourseResponse(BaseModel):
    name: str
    provider: str
    status: str
    progress: float
    model_config = {"from_attributes": True}


# ── Endpoints ─────────────────────────────────────────────────────────────

@router.get("")
async def get_progress(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Return the aggregated progress dashboard."""
    return await get_progress_service().get_dashboard(db, current_user.id)


@router.put("")
async def update_progress(
    body: ProgressUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Update learning progress (streak, hours, level)."""
    data = body.model_dump(exclude_unset=True)
    progress = await get_progress_service().update_progress(db, current_user.id, data)
    return {
        "streak": progress.streak,
        "hours": progress.hours,
        "level": progress.level,
    }


@router.get("/skills", response_model=list[SkillResponse])
async def get_skills(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all skills for the authenticated user."""
    return await get_progress_service().get_skills(db, current_user.id)


@router.post("/skills", response_model=SkillResponse, status_code=201)
async def add_skill(
    body: SkillItem,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add or update a skill."""
    return await get_progress_service().upsert_skill(
        db, current_user.id, body.name, body.level, body.status,
    )


@router.get("/projects", response_model=list[ProjectResponse])
async def get_projects(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all projects for the authenticated user."""
    return await get_progress_service().get_projects(db, current_user.id)


@router.post("/projects", response_model=ProjectResponse, status_code=201)
async def add_project(
    body: ProjectItem,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add or update a project."""
    return await get_progress_service().upsert_project(
        db, current_user.id, body.name, body.description, body.technology, body.status,
    )


@router.get("/courses", response_model=list[CourseResponse])
async def get_courses(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all courses for the authenticated user."""
    return await get_progress_service().get_courses(db, current_user.id)


@router.post("/courses", response_model=CourseResponse, status_code=201)
async def add_course(
    body: CourseItem,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add or update a course."""
    return await get_progress_service().upsert_course(
        db, current_user.id, body.name, body.provider, body.status, body.progress,
    )

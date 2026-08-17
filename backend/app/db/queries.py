"""
Centralised database query functions for every table.

All SQL lives here — service layers call these functions instead of
writing inline queries.  Every query that touches user-owned data
requires a ``user_id`` parameter to enforce user isolation.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Optional, Sequence

from sqlalchemy import delete, select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    CareerProfile,
    Conversation,
    Course,
    LearningProgress,
    Memory,
    Message,
    Project,
    Skill,
    User,
)
from app.utils.helpers import cosine_similarity


# ═══════════════════════════════════════════════════════════════════════════
#  USER QUERIES
# ═══════════════════════════════════════════════════════════════════════════


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Fetch a user by email address."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> User | None:
    """Fetch a user by primary key."""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def create_user(
    db: AsyncSession,
    email: str,
    password_hash: str,
    full_name: str = "",
) -> User:
    """Insert a new user and return the ORM instance."""
    user = User(email=email, password_hash=password_hash, full_name=full_name)
    db.add(user)
    await db.flush()
    return user


# ═══════════════════════════════════════════════════════════════════════════
#  PROFILE QUERIES
# ═══════════════════════════════════════════════════════════════════════════


async def get_profile(db: AsyncSession, user_id: uuid.UUID) -> CareerProfile | None:
    """Return the career profile for *user_id*, or ``None``."""
    result = await db.execute(
        select(CareerProfile).where(CareerProfile.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def upsert_profile(
    db: AsyncSession,
    user_id: uuid.UUID,
    data: dict[str, Any],
) -> CareerProfile:
    """Create or update a career profile for *user_id*."""
    profile = await get_profile(db, user_id)
    if profile is None:
        profile = CareerProfile(user_id=user_id, **data)
        db.add(profile)
    else:
        for key, value in data.items():
            if hasattr(profile, key) and value is not None:
                setattr(profile, key, value)
        profile.updated_at = datetime.now(timezone.utc)
    await db.flush()
    return profile


# ═══════════════════════════════════════════════════════════════════════════
#  CONVERSATION QUERIES
# ═══════════════════════════════════════════════════════════════════════════


async def create_conversation(
    db: AsyncSession,
    user_id: uuid.UUID,
    title: str = "New Conversation",
) -> Conversation:
    """Create a new conversation."""
    conv = Conversation(user_id=user_id, title=title)
    db.add(conv)
    await db.flush()
    return conv


async def get_conversation(
    db: AsyncSession,
    conversation_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Conversation | None:
    """Fetch a conversation scoped to *user_id*."""
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        )
    )
    return result.scalar_one_or_none()


async def get_user_conversations(
    db: AsyncSession,
    user_id: uuid.UUID,
    limit: int = 20,
) -> Sequence[Conversation]:
    """Return the most recent conversations for *user_id*."""
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
        .limit(limit)
    )
    return result.scalars().all()


# ═══════════════════════════════════════════════════════════════════════════
#  MESSAGE QUERIES
# ═══════════════════════════════════════════════════════════════════════════


async def add_message(
    db: AsyncSession,
    conversation_id: uuid.UUID,
    role: str,
    content: str,
) -> Message:
    """Append a message to a conversation."""
    msg = Message(conversation_id=conversation_id, role=role, content=content)
    db.add(msg)
    await db.flush()
    return msg


async def get_recent_messages(
    db: AsyncSession,
    conversation_id: uuid.UUID,
    limit: int = 20,
) -> Sequence[Message]:
    """Return the most recent messages in a conversation (oldest first)."""
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    messages = list(result.scalars().all())
    messages.reverse()  # oldest first
    return messages


# ═══════════════════════════════════════════════════════════════════════════
#  MEMORY QUERIES
# ═══════════════════════════════════════════════════════════════════════════


async def create_memory(
    db: AsyncSession,
    user_id: uuid.UUID,
    memory_type: str,
    content: str,
    embedding: list[float] | None = None,
    importance: float = 0.5,
    source: str = "conversation",
) -> Memory:
    """Insert a new memory record."""
    mem = Memory(
        user_id=user_id,
        memory_type=memory_type,
        content=content,
        embedding=embedding,
        importance=importance,
        source=source,
    )
    db.add(mem)
    await db.flush()
    return mem


async def update_memory(
    db: AsyncSession,
    memory_id: uuid.UUID,
    user_id: uuid.UUID,
    data: dict[str, Any],
) -> Memory | None:
    """Update fields on an existing memory (user-scoped)."""
    result = await db.execute(
        select(Memory).where(Memory.id == memory_id, Memory.user_id == user_id)
    )
    mem = result.scalar_one_or_none()
    if mem is None:
        return None
    for key, value in data.items():
        if hasattr(mem, key) and value is not None:
            setattr(mem, key, value)
    mem.updated_at = datetime.now(timezone.utc)
    await db.flush()
    return mem


async def delete_memory(
    db: AsyncSession,
    memory_id: uuid.UUID,
    user_id: uuid.UUID,
) -> bool:
    """Delete a memory (user-scoped). Returns True if deleted."""
    result = await db.execute(
        delete(Memory).where(Memory.id == memory_id, Memory.user_id == user_id)
    )
    return result.rowcount > 0


async def get_user_memories(
    db: AsyncSession,
    user_id: uuid.UUID,
    memory_type: Optional[str] = None,
    limit: int = 50,
) -> Sequence[Memory]:
    """List memories for a user, optionally filtered by type."""
    stmt = select(Memory).where(Memory.user_id == user_id)
    if memory_type:
        stmt = stmt.where(Memory.memory_type == memory_type)
    stmt = stmt.order_by(Memory.updated_at.desc()).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_memory_by_id(
    db: AsyncSession,
    memory_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Memory | None:
    """Fetch a single memory by ID (user-scoped)."""
    result = await db.execute(
        select(Memory).where(Memory.id == memory_id, Memory.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def vector_search_memories(
    db: AsyncSession,
    user_id: uuid.UUID,
    query_embedding: list[float],
    limit: int = 5,
) -> list[dict[str, Any]]:
    """
    Perform vector similarity search against user memories.

    Loads all user memories that have embeddings, computes cosine
    similarity in Python, and returns the top-K results ranked by a
    weighted score combining similarity, importance, and recency.

    NOTE: For production at scale, consider using CockroachDB's
    built-in vector index or pgvector.  This approach works well for
    moderate memory counts per user.
    """
    result = await db.execute(
        select(Memory).where(
            Memory.user_id == user_id,
            Memory.embedding.isnot(None),
        )
    )
    memories = result.scalars().all()

    scored: list[dict[str, Any]] = []
    now = datetime.now(timezone.utc)

    for mem in memories:
        emb = mem.embedding
        if emb is None:
            continue
        if isinstance(emb, str):
            try:
                import json
                emb = json.loads(emb)
            except Exception:
                continue
        if not isinstance(emb, (list, tuple)):
            continue
        sim = cosine_similarity(query_embedding, emb)

        # Recency bonus: memories updated recently get a small boost
        age_hours = max((now - mem.updated_at).total_seconds() / 3600, 1)
        recency_score = 1.0 / (1.0 + age_hours / 168)  # half-life ≈ 1 week

        # Weighted score
        weighted = (sim * 0.6) + (mem.importance * 0.25) + (recency_score * 0.15)

        scored.append({
            "id": str(mem.id),
            "memory_type": mem.memory_type,
            "content": mem.content,
            "importance": mem.importance,
            "similarity": round(sim, 4),
            "weighted_score": round(weighted, 4),
            "source": mem.source,
            "created_at": mem.created_at.isoformat() if mem.created_at else None,
            "updated_at": mem.updated_at.isoformat() if mem.updated_at else None,
        })

    scored.sort(key=lambda x: x["weighted_score"], reverse=True)
    return scored[:limit]


# ═══════════════════════════════════════════════════════════════════════════
#  SKILL QUERIES
# ═══════════════════════════════════════════════════════════════════════════


async def get_user_skills(db: AsyncSession, user_id: uuid.UUID) -> Sequence[Skill]:
    """List all skills for a user."""
    result = await db.execute(
        select(Skill).where(Skill.user_id == user_id).order_by(Skill.name)
    )
    return result.scalars().all()


async def upsert_skill(
    db: AsyncSession,
    user_id: uuid.UUID,
    name: str,
    level: str = "beginner",
    status: str = "learning",
) -> Skill:
    """Create or update a skill by name (user-scoped)."""
    result = await db.execute(
        select(Skill).where(Skill.user_id == user_id, Skill.name == name)
    )
    skill = result.scalar_one_or_none()
    if skill is None:
        skill = Skill(user_id=user_id, name=name, level=level, status=status)
        db.add(skill)
    else:
        skill.level = level
        skill.status = status
        skill.updated_at = datetime.now(timezone.utc)
    await db.flush()
    return skill


# ═══════════════════════════════════════════════════════════════════════════
#  PROJECT QUERIES
# ═══════════════════════════════════════════════════════════════════════════


async def get_user_projects(db: AsyncSession, user_id: uuid.UUID) -> Sequence[Project]:
    """List all projects for a user."""
    result = await db.execute(
        select(Project).where(Project.user_id == user_id).order_by(Project.created_at.desc())
    )
    return result.scalars().all()


async def upsert_project(
    db: AsyncSession,
    user_id: uuid.UUID,
    name: str,
    description: str = "",
    technology: str = "",
    status: str = "planned",
) -> Project:
    """Create or update a project by name (user-scoped)."""
    result = await db.execute(
        select(Project).where(Project.user_id == user_id, Project.name == name)
    )
    project = result.scalar_one_or_none()
    if project is None:
        project = Project(
            user_id=user_id, name=name, description=description,
            technology=technology, status=status,
        )
        db.add(project)
    else:
        project.description = description or project.description
        project.technology = technology or project.technology
        project.status = status
        project.updated_at = datetime.now(timezone.utc)
    await db.flush()
    return project


# ═══════════════════════════════════════════════════════════════════════════
#  COURSE QUERIES
# ═══════════════════════════════════════════════════════════════════════════


async def get_user_courses(db: AsyncSession, user_id: uuid.UUID) -> Sequence[Course]:
    """List all courses for a user."""
    result = await db.execute(
        select(Course).where(Course.user_id == user_id).order_by(Course.created_at.desc())
    )
    return result.scalars().all()


async def upsert_course(
    db: AsyncSession,
    user_id: uuid.UUID,
    name: str,
    provider: str = "",
    status: str = "not_started",
    progress: float = 0.0,
) -> Course:
    """Create or update a course by name (user-scoped)."""
    result = await db.execute(
        select(Course).where(Course.user_id == user_id, Course.name == name)
    )
    course = result.scalar_one_or_none()
    if course is None:
        course = Course(
            user_id=user_id, name=name, provider=provider,
            status=status, progress=progress,
        )
        db.add(course)
    else:
        course.provider = provider or course.provider
        course.status = status
        course.progress = progress
        course.updated_at = datetime.now(timezone.utc)
    await db.flush()
    return course


# ═══════════════════════════════════════════════════════════════════════════
#  LEARNING PROGRESS QUERIES
# ═══════════════════════════════════════════════════════════════════════════


async def get_learning_progress(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> LearningProgress | None:
    """Return learning progress for *user_id*."""
    result = await db.execute(
        select(LearningProgress).where(LearningProgress.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def upsert_learning_progress(
    db: AsyncSession,
    user_id: uuid.UUID,
    data: dict[str, Any],
) -> LearningProgress:
    """Create or update learning progress."""
    progress = await get_learning_progress(db, user_id)
    if progress is None:
        progress = LearningProgress(user_id=user_id, **data)
        db.add(progress)
    else:
        for key, value in data.items():
            if hasattr(progress, key) and value is not None:
                setattr(progress, key, value)
        progress.updated_at = datetime.now(timezone.utc)
    await db.flush()
    return progress

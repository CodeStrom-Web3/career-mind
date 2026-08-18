"""
Async SQLAlchemy engine, session factory, and health-check for CockroachDB.

All database connections flow through this module.  Route handlers
obtain sessions via the ``get_db`` async generator (see dependencies.py).

Supports both CockroachDB (via asyncpg) and SQLite (via aiosqlite)
for local development.
"""

from __future__ import annotations

import asyncio
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy import text

from app.config.settings import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def _get_engine() -> AsyncEngine:
    """Create or return the singleton async engine."""
    global _engine
    if _engine is None:
        settings = get_settings()
        engine_kwargs: dict = {
            "echo": False,
            "pool_pre_ping": True,
        }

        if settings.is_sqlite:
            # SQLite-specific: no pooling options, use NullPool implicitly
            # aiosqlite handles concurrency differently
            pass
        else:
            # CockroachDB / PostgreSQL pool settings
            engine_kwargs.update({
                "pool_size": settings.database_pool_size,
                "max_overflow": settings.database_max_overflow,
                "pool_recycle": 3600,
            })

            # SSL for CockroachDB Cloud (sslmode in the URL)
            if "cockroachlabs.cloud" in settings.database_url:
                engine_kwargs["connect_args"] = {"ssl": "require"}

        _engine = create_async_engine(
            settings.database_url,
            **engine_kwargs,
        )

        db_type = "SQLite" if settings.is_sqlite else (
            "CockroachDB" if settings.is_cockroachdb else "PostgreSQL"
        )
        logger.info(
            f"Database engine created ({db_type})",
            extra={"service": "database"},
        )
    return _engine


async def init_db() -> None:
    """Verify and initialize database tables with retry logic."""
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            engine = _get_engine()
            from app.db.models import Base
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info(
                "Database schema initialized successfully",
                extra={"service": "database"},
            )
            return
        except Exception as exc:
            if attempt < max_retries:
                wait_time = attempt * 2
                logger.warning(
                    f"Database init attempt {attempt}/{max_retries} failed: {exc}. "
                    f"Retrying in {wait_time}s...",
                    extra={"service": "database"},
                )
                await asyncio.sleep(wait_time)
            else:
                logger.warning(
                    f"Database auto-creation failed after {max_retries} attempts: {exc}. "
                    "The application will continue but some features may not work.",
                    extra={"service": "database"},
                )


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Create or return the singleton session factory."""
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            bind=_get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Async generator that yields a database session.

    Used as a FastAPI dependency::

        @router.get("/")
        async def handler(db: AsyncSession = Depends(get_db)):
            ...
    """
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def check_db_health() -> bool:
    """
    Return ``True`` if the database is reachable, ``False`` otherwise.

    Executes a lightweight ``SELECT 1`` query.
    """
    try:
        engine = _get_engine()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as exc:
        logger.error(
            "Database health check failed",
            exc_info=exc,
            extra={"service": "database"},
        )
        return False


async def dispose_engine() -> None:
    """Gracefully dispose of the engine connection pool."""
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _session_factory = None
        logger.info("Database engine disposed", extra={"service": "database"})

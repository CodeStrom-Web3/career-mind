"""
Health-check route.

Verifies CockroachDB connectivity and returns a status response.
"""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.db.database import check_db_health

router = APIRouter(prefix="/api", tags=["Health"])


@router.get("/health")
async def health_check():
    """
    Check system health including database connectivity.

    Returns ``200`` with ``{"status": "healthy"}`` when the database is
    reachable, or ``503`` with ``{"status": "unhealthy", ...}``
    otherwise.
    """
    db_ok = await check_db_health()

    if db_ok:
        return {"status": "healthy", "database": "connected"}

    return JSONResponse(
        status_code=503,
        content={
            "status": "unhealthy",
            "database": "disconnected",
            "detail": "Unable to reach CockroachDB",
        },
    )

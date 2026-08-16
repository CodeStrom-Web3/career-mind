"""
CareerMind AI Backend — FastAPI Application Entrypoint.

Configures:
  - CORS
  - Router registration
  - Startup / shutdown lifecycle
  - Global exception handling
  - Structured logging
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import auth, chat, health, memory, profile, progress
from app.db.database import dispose_engine, init_db
from app.utils.logger import get_logger

logger = get_logger(__name__)


# ── Lifecycle ─────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Startup and shutdown lifecycle events."""
    logger.info("CareerMind AI backend starting up")
    await init_db()
    yield
    logger.info("CareerMind AI backend shutting down")
    await dispose_engine()


# ── Application ───────────────────────────────────────────────────────────

app = FastAPI(
    title="CareerMind AI",
    description=(
        "AI-powered career planning platform with persistent agentic memory, "
        "semantic retrieval, and Amazon Bedrock integration."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite dev server
        "http://localhost:3000",   # Alternate dev port
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(profile.router)
app.include_router(memory.router)
app.include_router(progress.router)


# ── Global Exception Handler ─────────────────────────────────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Catch-all handler that returns a 500 without exposing internal traces.
    """
    logger.error(
        "Unhandled exception",
        exc_info=exc,
        extra={
            "endpoint": str(request.url),
            "method": request.method,
        },
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


# ── Root redirect ─────────────────────────────────────────────────────────

@app.get("/", include_in_schema=False)
async def root():
    """Redirect root to API docs."""
    return {"message": "CareerMind AI API — visit /docs for documentation"}

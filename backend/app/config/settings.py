"""
Application configuration using Pydantic Settings.

Loads values from environment variables and .env files.
Never hard-codes credentials or secrets.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for the CareerMind AI backend."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Database ──────────────────────────────────────────────────────────
    database_url: str = "postgresql+asyncpg://root:@localhost:26257/careermind"
    database_pool_size: int = 20
    database_max_overflow: int = 10

    # ── JWT Authentication ────────────────────────────────────────────────
    secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # ── AWS / Amazon Bedrock ──────────────────────────────────────────────
    aws_region: str = "us-east-1"
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None

    # ── Bedrock Model IDs ─────────────────────────────────────────────────
    bedrock_model_id: str = "anthropic.claude-3-5-sonnet-20241022-v2:0"
    bedrock_embedding_model_id: str = "amazon.titan-embed-text-v2:0"

    # ── Embedding Configuration ───────────────────────────────────────────
    embedding_dimensions: int = 1024

    # ── Memory Retrieval ──────────────────────────────────────────────────
    top_k_memories: int = 5
    memory_dedup_threshold: float = 0.92

    @property
    def is_cockroachdb(self) -> bool:
        """Return True if the database URL points to CockroachDB."""
        url = self.database_url.lower()
        return "cockroach" in url or "26257" in url

    @property
    def is_sqlite(self) -> bool:
        """Return True if the database URL points to SQLite."""
        return self.database_url.lower().startswith("sqlite")


@lru_cache()
def get_settings() -> Settings:
    """Return a cached singleton of application settings."""
    return Settings()

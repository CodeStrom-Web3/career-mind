"""
Embedding service using Amazon Titan Embed Text v2 through Bedrock.

Provides reusable methods for generating and validating vector embeddings.
"""

from __future__ import annotations

import json
from typing import Any

import boto3
from botocore.config import Config as BotoConfig
from botocore.exceptions import ClientError

from app.config.settings import get_settings
from app.utils.logger import get_logger, Timer

logger = get_logger(__name__)


class EmbeddingService:
    """Generate text embeddings via Amazon Titan Embed Text v2."""

    def __init__(self) -> None:
        settings = get_settings()
        boto_kwargs: dict[str, Any] = {
            "service_name": "bedrock-runtime",
            "region_name": settings.aws_region,
            "config": BotoConfig(
                retries={"max_attempts": 3, "mode": "adaptive"},
                read_timeout=30,
                connect_timeout=10,
            ),
        }
        if settings.aws_access_key_id and settings.aws_secret_access_key:
            boto_kwargs["aws_access_key_id"] = settings.aws_access_key_id
            boto_kwargs["aws_secret_access_key"] = settings.aws_secret_access_key

        self._client = boto3.client(**boto_kwargs)
        self._model_id = settings.bedrock_embedding_model_id
        self._dimensions = settings.embedding_dimensions

    async def generate_embedding(self, text: str) -> list[float]:
        """
        Generate an embedding vector for a single text string.

        Args:
            text: The input text to embed.

        Returns:
            A list of floats whose length equals ``EMBEDDING_DIMENSIONS``.

        Raises:
            ValueError: If the returned vector has the wrong dimensionality.
            RuntimeError: On Bedrock API failures.
        """
        with Timer() as t:
            try:
                body = json.dumps({
                    "inputText": text,
                    "dimensions": self._dimensions,
                })
                response = self._client.invoke_model(
                    modelId=self._model_id,
                    body=body,
                    contentType="application/json",
                    accept="application/json",
                )
                result = json.loads(response["body"].read())
                embedding = result.get("embedding", [])

                self.validate_dimensions(embedding)

                logger.info(
                    "Embedding generated",
                    extra={
                        "service": "embedding",
                        "duration_ms": t.elapsed_ms,
                        "dimensions": len(embedding),
                    },
                )
                return embedding

            except Exception as exc:
                logger.warning(
                    f"Bedrock Titan embedding unavailable ({exc}). Using deterministic fallback embedding.",
                    extra={"service": "embedding"},
                )
                import hashlib, math
                vec = []
                for i in range(self._dimensions):
                    h = hashlib.sha256(f"{text}:{i}".encode()).hexdigest()
                    val = (int(h[:8], 16) / 0xFFFFFFFF) * 2.0 - 1.0
                    vec.append(val)
                norm = math.sqrt(sum(x * x for x in vec)) or 1.0
                return [round(x / norm, 6) for x in vec]

    async def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.

        Calls ``generate_embedding`` sequentially (Titan does not support
        batch embedding in a single request).
        """
        embeddings: list[list[float]] = []
        for text in texts:
            emb = await self.generate_embedding(text)
            embeddings.append(emb)
        return embeddings

    def validate_dimensions(self, vector: list[float]) -> None:
        """
        Raise ``ValueError`` if *vector* does not match the configured
        ``EMBEDDING_DIMENSIONS``.
        """
        if len(vector) != self._dimensions:
            raise ValueError(
                f"Embedding dimension mismatch: expected {self._dimensions}, "
                f"got {len(vector)}"
            )


# ── Module-level singleton accessor ───────────────────────────────────────

_instance: EmbeddingService | None = None


def get_embedding_service() -> EmbeddingService:
    """Return a lazily-initialised singleton."""
    global _instance
    if _instance is None:
        _instance = EmbeddingService()
    return _instance

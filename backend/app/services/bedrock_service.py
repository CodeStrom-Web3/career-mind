"""
Amazon Bedrock service for LLM response generation and memory extraction.

Uses the Bedrock Converse API via boto3.  Handles retries, timeouts,
error handling, and structured output parsing.
"""

from __future__ import annotations

import json
from typing import Any, Optional

import boto3
from botocore.config import Config as BotoConfig
from botocore.exceptions import ClientError

from app.config.settings import get_settings
from app.utils.logger import get_logger, Timer
from app.utils.helpers import safe_json_parse

logger = get_logger(__name__)


class BedrockService:
    """Wrapper around Amazon Bedrock for LLM calls and memory extraction."""

    def __init__(self) -> None:
        settings = get_settings()
        boto_kwargs: dict[str, Any] = {
            "service_name": "bedrock-runtime",
            "region_name": settings.aws_region,
            "config": BotoConfig(
                retries={"max_attempts": 3, "mode": "adaptive"},
                read_timeout=120,
                connect_timeout=10,
            ),
        }
        # Only pass explicit credentials when provided (otherwise fall back
        # to IAM role / instance profile / env chain).
        if settings.aws_access_key_id and settings.aws_secret_access_key:
            boto_kwargs["aws_access_key_id"] = settings.aws_access_key_id
            boto_kwargs["aws_secret_access_key"] = settings.aws_secret_access_key

        self._client = boto3.client(**boto_kwargs)
        self._model_id = settings.bedrock_model_id

    # ── Public API ────────────────────────────────────────────────────────

    async def generate_response(
        self,
        system_prompt: str,
        messages: list[dict[str, str]],
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> str:
        """
        Call Bedrock Converse API and return the assistant text.

        Args:
            system_prompt: The system-level instruction.
            messages: Conversation messages ``[{"role": ..., "content": ...}]``.
            max_tokens: Maximum tokens in the response.
            temperature: Sampling temperature.

        Returns:
            The assistant's response text.

        Raises:
            RuntimeError: On unrecoverable Bedrock errors.
        """
        with Timer() as t:
            try:
                converse_messages = self._format_messages(messages)

                response = self._client.converse(
                    modelId=self._model_id,
                    system=[{"text": system_prompt}],
                    messages=converse_messages,
                    inferenceConfig={
                        "maxTokens": max_tokens,
                        "temperature": temperature,
                    },
                )

                output_text = self._extract_text(response)
                logger.info(
                    "Bedrock response generated",
                    extra={
                        "service": "bedrock",
                        "duration_ms": t.elapsed_ms,
                        "model": self._model_id,
                    },
                )
                return output_text

            except Exception as exc:
                logger.warning(
                    f"Bedrock API call unavailable ({exc}). Using local reasoning engine.",
                    extra={"service": "bedrock"},
                )
                last_user_msg = messages[-1].get("content", "") if messages else "Career planning"
                # Use the local reasoning engine for intelligent fallback
                from app.services.reasoning_engine import get_reasoning_engine
                engine = get_reasoning_engine()
                result = engine.reason_about_career(query=last_user_msg)
                return result["response"]

    async def extract_memories(
        self,
        conversation_text: str,
        extraction_prompt: str,
    ) -> list[dict[str, Any]]:
        """
        Ask the LLM to extract persistent facts from a conversation.

        Returns a list of dicts, each containing at least ``type`` and
        ``content`` keys.  Returns an empty list on parse failure.
        """
        messages = [{"role": "user", "content": conversation_text}]

        try:
            raw = await self.generate_response(
                system_prompt=extraction_prompt,
                messages=messages,
                max_tokens=2048,
                temperature=0.3,
            )
            parsed = safe_json_parse(raw)

            if isinstance(parsed, dict) and "memories" in parsed:
                memories = parsed["memories"]
                if isinstance(memories, list):
                    return [
                        m for m in memories
                        if isinstance(m, dict) and "content" in m
                    ]

            logger.warning(
                "Malformed memory extraction response",
                extra={"service": "bedrock"},
            )
            return []

        except Exception as exc:
            logger.error(
                "Memory extraction failed",
                exc_info=exc,
                extra={"service": "bedrock"},
            )
            return []

    # ── Internal helpers ──────────────────────────────────────────────────

    @staticmethod
    def _format_messages(messages: list[dict[str, str]]) -> list[dict[str, Any]]:
        """Convert simple role/content dicts to Converse API format."""
        formatted: list[dict[str, Any]] = []
        for msg in messages:
            role = msg.get("role", "user")
            if role == "system":
                continue  # system is passed separately
            formatted.append({
                "role": role if role in ("user", "assistant") else "user",
                "content": [{"text": msg.get("content", "")}],
            })
        return formatted

    @staticmethod
    def _extract_text(response: dict[str, Any]) -> str:
        """Pull the assistant text out of a Converse API response."""
        try:
            output = response.get("output", {})
            message = output.get("message", {})
            content_blocks = message.get("content", [])
            parts: list[str] = []
            for block in content_blocks:
                if "text" in block:
                    parts.append(block["text"])
            return "\n".join(parts) if parts else ""
        except (KeyError, TypeError, IndexError):
            return ""


# ── Module-level singleton accessor ───────────────────────────────────────

_instance: BedrockService | None = None


def get_bedrock_service() -> BedrockService:
    """Return a lazily-initialised singleton."""
    global _instance
    if _instance is None:
        _instance = BedrockService()
    return _instance

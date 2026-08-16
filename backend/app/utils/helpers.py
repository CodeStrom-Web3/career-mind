"""
Reusable helper utilities for the CareerMind AI backend.

Provides UUID generation, timestamp helpers, safe JSON parsing,
input sanitisation, and common validation functions.
"""

from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Optional


def generate_uuid() -> str:
    """Return a new UUID4 string."""
    return str(uuid.uuid4())


def utc_now() -> datetime:
    """Return the current UTC datetime (timezone-aware)."""
    return datetime.now(timezone.utc)


def safe_json_parse(text: str, default: Any = None) -> Any:
    """
    Attempt to parse *text* as JSON, returning *default* on failure.

    If the text contains a JSON block fenced by ```json ... ```, the
    inner content is extracted first.
    """
    if not text:
        return default

    # Try to extract a fenced JSON block first
    match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
    if match:
        text = match.group(1)

    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return default


def sanitize_string(value: str, max_length: int = 10_000) -> str:
    """
    Sanitise a user-supplied string.

    * Strips leading/trailing whitespace.
    * Truncates to *max_length* characters.
    """
    if not isinstance(value, str):
        return ""
    return value.strip()[:max_length]


def validate_email(email: str) -> bool:
    """Basic email format validation."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def truncate(text: str, length: int = 200) -> str:
    """Truncate *text* to *length* characters, appending '…' if trimmed."""
    if len(text) <= length:
        return text
    return text[:length] + "…"


def cosine_similarity(vec_a: Any, vec_b: Any) -> float:
    """
    Compute cosine similarity between two vectors.

    Returns a float in [-1, 1].  Returns 0.0 if either vector is None or length mismatch.
    """
    if vec_a is None or vec_b is None:
        return 0.0
    if not isinstance(vec_a, (list, tuple)) or not isinstance(vec_b, (list, tuple)):
        return 0.0
    try:
        len_a = len(vec_a)
        len_b = len(vec_b)
    except Exception:
        return 0.0
    if len_a == 0 or len_b == 0 or len_a != len_b:
        return 0.0

    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    mag_a = sum(a * a for a in vec_a) ** 0.5
    mag_b = sum(b * b for b in vec_b) ** 0.5

    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def format_memories_for_prompt(memories: list[dict[str, Any]]) -> str:
    """
    Format a list of memory dicts into a numbered, human-readable string
    suitable for inclusion in an LLM prompt.
    """
    if not memories:
        return "No relevant memories found."

    lines: list[str] = []
    for idx, mem in enumerate(memories, 1):
        mem_type = mem.get("memory_type", "general")
        content = mem.get("content", "")
        lines.append(f"{idx}. [{mem_type}] {content}")
    return "\n".join(lines)


def clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    """Clamp *value* to the range [lo, hi]."""
    return max(lo, min(hi, value))

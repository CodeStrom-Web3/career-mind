"""
Structured logging for the CareerMind AI backend.

Provides JSON-formatted log output with contextual fields (request ID,
user ID, endpoint, service, execution time) while filtering sensitive
data (passwords, tokens, AWS keys).
"""

from __future__ import annotations

import logging
import json
import sys
import time
from typing import Any


# Fields that must never appear in logs
_SENSITIVE_FIELDS = frozenset({
    "password",
    "password_hash",
    "secret_key",
    "aws_access_key_id",
    "aws_secret_access_key",
    "authorization",
    "token",
    "access_token",
})


class SensitiveFilter(logging.Filter):
    """Strip sensitive key-value pairs from log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        if hasattr(record, "extra_data") and isinstance(record.extra_data, dict):
            record.extra_data = {
                k: "***REDACTED***" if k.lower() in _SENSITIVE_FIELDS else v
                for k, v in record.extra_data.items()
            }
        return True


class JSONFormatter(logging.Formatter):
    """Emit each log record as a single JSON line."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Merge optional contextual fields
        for attr in ("request_id", "user_id", "endpoint", "service", "duration_ms"):
            value = getattr(record, attr, None)
            if value is not None:
                log_entry[attr] = value

        if hasattr(record, "extra_data") and record.extra_data:
            log_entry["data"] = record.extra_data

        if record.exc_info and record.exc_info[1]:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, default=str)


def get_logger(name: str) -> logging.Logger:
    """
    Return a configured logger instance.

    Args:
        name: Logger name, typically ``__name__`` of the calling module.
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        handler.addFilter(SensitiveFilter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False

    return logger


class Timer:
    """
    Simple context-manager timer for measuring execution duration.

    Usage::

        with Timer() as t:
            do_work()
        logger.info("done", extra={"duration_ms": t.elapsed_ms})
    """

    def __init__(self) -> None:
        self._start: float = 0.0
        self.elapsed_ms: float = 0.0

    def __enter__(self) -> "Timer":
        self._start = time.perf_counter()
        return self

    def __exit__(self, *_: Any) -> None:
        self.elapsed_ms = round((time.perf_counter() - self._start) * 1000, 2)

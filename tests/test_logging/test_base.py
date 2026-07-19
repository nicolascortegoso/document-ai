from __future__ import annotations

from typing import Any

from backends.logging.base import Logger
from backends.logging.models import LogLevel


class _SpyLogger(Logger):
    """Implements only the abstract log() method, recording every call —
    used to verify the concrete convenience methods delegate correctly.
    """

    def __init__(self) -> None:
        self.calls: list[tuple[LogLevel, str, dict[str, Any]]] = []

    def log(self, level: LogLevel, message: str, **context: Any) -> None:
        self.calls.append((level, message, context))


def test_debug_delegates_to_log_with_debug_level() -> None:
    logger = _SpyLogger()

    logger.debug("a debug message", key="value")

    assert logger.calls == [(LogLevel.DEBUG, "a debug message", {"key": "value"})]


def test_info_delegates_to_log_with_info_level() -> None:
    logger = _SpyLogger()

    logger.info("an info message")

    assert logger.calls == [(LogLevel.INFO, "an info message", {})]


def test_warning_delegates_to_log_with_warning_level() -> None:
    logger = _SpyLogger()

    logger.warning("a warning message")

    assert logger.calls == [(LogLevel.WARNING, "a warning message", {})]


def test_error_delegates_to_log_with_error_level() -> None:
    logger = _SpyLogger()

    logger.error("an error message")

    assert logger.calls == [(LogLevel.ERROR, "an error message", {})]


def test_critical_delegates_to_log_with_critical_level() -> None:
    logger = _SpyLogger()

    logger.critical("a critical message")

    assert logger.calls == [(LogLevel.CRITICAL, "a critical message", {})]


def test_context_kwargs_pass_through() -> None:
    logger = _SpyLogger()

    logger.info("message", document_id="abc-123", chunk_count=5)

    assert logger.calls == [
        (LogLevel.INFO, "message", {"document_id": "abc-123", "chunk_count": 5})
    ]

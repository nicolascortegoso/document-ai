from __future__ import annotations

from typing import Any

from backends.logging.base import Logger
from backends.logging.models import LogLevel


class DummyLogger(Logger):
    """Discards every call. The default when no Logger is injected."""

    def log(self, level: LogLevel, message: str, **context: Any) -> None:
        pass

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from backends.logging.models import LogLevel


class Logger(ABC):
    """Abstract base for all logger implementations.

    log() is the only abstract method — every concrete Logger implements
    just that one. debug/info/warning/error/critical are concrete methods
    on the ABC itself, each a thin wrapper calling log(), keeping
    implementations minimal while keeping call sites ergonomic.
    """

    @abstractmethod
    def log(self, level: LogLevel, message: str, **context: Any) -> None:
        """Emit a log record. Never raises."""

    def debug(self, message: str, **context: Any) -> None:
        self.log(LogLevel.DEBUG, message, **context)

    def info(self, message: str, **context: Any) -> None:
        self.log(LogLevel.INFO, message, **context)

    def warning(self, message: str, **context: Any) -> None:
        self.log(LogLevel.WARNING, message, **context)

    def error(self, message: str, **context: Any) -> None:
        self.log(LogLevel.ERROR, message, **context)

    def critical(self, message: str, **context: Any) -> None:
        self.log(LogLevel.CRITICAL, message, **context)

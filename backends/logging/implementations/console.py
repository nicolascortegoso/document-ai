from __future__ import annotations

from typing import Any

from backends.logging.base import Logger
from backends.logging.models import LogLevel


class ConsoleLogger(Logger):
    """Prints to stdout, one line per call. Human-readable, for local
    development — not machine-parseable, not for log aggregation.
    """

    def log(self, level: LogLevel, message: str, **context: Any) -> None:
        try:
            line = f"[{level.value.upper()}] {message}"
            if context:
                formatted = " ".join(f"{key}={value!r}" for key, value in context.items())
                line += f" ({formatted})"
            print(line)
        except Exception:
            # print() can genuinely fail (e.g. BrokenPipeError on a closed
            # stdout) — log() must never raise regardless.
            pass

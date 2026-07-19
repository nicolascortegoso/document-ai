from __future__ import annotations

from backends.logging.implementations.dummy import DummyLogger
from backends.logging.models import LogLevel


def test_log_discards_everything_and_never_raises() -> None:
    logger = DummyLogger()

    # Should not raise, and has no observable effect to assert against —
    # that's the entire point of a dummy implementation.
    logger.log(LogLevel.CRITICAL, "this goes nowhere", key="value")


def test_convenience_methods_also_discard_silently() -> None:
    logger = DummyLogger()

    logger.debug("x")
    logger.info("x")
    logger.warning("x")
    logger.error("x")
    logger.critical("x")

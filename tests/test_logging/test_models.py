from __future__ import annotations

from backends.logging.models import LogLevel


def test_log_level_values_are_lowercase_strings() -> None:
    assert LogLevel.DEBUG == "debug"
    assert LogLevel.INFO == "info"
    assert LogLevel.WARNING == "warning"
    assert LogLevel.ERROR == "error"
    assert LogLevel.CRITICAL == "critical"

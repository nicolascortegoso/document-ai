from __future__ import annotations

import builtins

import pytest

from backends.logging.implementations.console import ConsoleLogger
from backends.logging.models import LogLevel


def test_log_prints_level_and_message(capsys: pytest.CaptureFixture[str]) -> None:
    logger = ConsoleLogger()

    logger.log(LogLevel.INFO, "hello world")

    captured = capsys.readouterr()
    assert "[INFO]" in captured.out
    assert "hello world" in captured.out


def test_log_includes_context_key_value_pairs(
    capsys: pytest.CaptureFixture[str],
) -> None:
    logger = ConsoleLogger()

    logger.log(LogLevel.ERROR, "something failed", document_id="abc-123", retries=3)

    captured = capsys.readouterr()
    assert "document_id='abc-123'" in captured.out
    assert "retries=3" in captured.out


def test_log_with_no_context_omits_parentheses(
    capsys: pytest.CaptureFixture[str],
) -> None:
    logger = ConsoleLogger()

    logger.log(LogLevel.DEBUG, "plain message")

    captured = capsys.readouterr()
    assert captured.out.strip() == "[DEBUG] plain message"


def test_convenience_methods_use_correct_level(
    capsys: pytest.CaptureFixture[str],
) -> None:
    logger = ConsoleLogger()

    logger.warning("careful")

    captured = capsys.readouterr()
    assert "[WARNING]" in captured.out
    assert "careful" in captured.out


def test_log_never_raises_even_if_print_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    logger = ConsoleLogger()

    def _broken_print(*args: object, **kwargs: object) -> None:
        raise BrokenPipeError("simulated closed stdout")

    monkeypatch.setattr(builtins, "print", _broken_print)

    # Should not raise, despite print() always failing.
    logger.log(LogLevel.INFO, "this would normally print")

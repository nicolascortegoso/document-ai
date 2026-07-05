from __future__ import annotations

from unittest.mock import patch

from common.enums import FileType
from libs.profiler.detector.implementations.default import DefaultDetector


def test_detect_mime_returns_plain_text_for_text_file() -> None:
    detector = DefaultDetector()

    result = detector.detect_mime(b"Hello, this is a plain text document.")

    assert result == FileType.PLAIN_TEXT


def test_detect_mime_returns_unknown_for_unrecognised_input() -> None:
    detector = DefaultDetector()

    # Random binary bytes with no recognisable magic-byte signature.
    result = detector.detect_mime(b"\x00\x01\x02\x03\xff\xfe\xfd\xfc" * 4)

    assert result == FileType.UNKNOWN


def test_detect_mime_returns_unknown_for_empty_input() -> None:
    detector = DefaultDetector()

    result = detector.detect_mime(b"")

    assert result == FileType.UNKNOWN


def test_detect_mime_never_raises_on_malformed_input() -> None:
    detector = DefaultDetector()

    # Should not raise, regardless of how malformed the input is.
    result = detector.detect_mime(b"\xff" * 1000)

    assert isinstance(result, FileType)


def test_detect_mime_returns_unknown_when_python_magic_raises_internally() -> None:
    detector = DefaultDetector()

    with patch("magic.from_buffer", side_effect=RuntimeError("libmagic failure")):
        result = detector.detect_mime(b"anything")

    assert result == FileType.UNKNOWN
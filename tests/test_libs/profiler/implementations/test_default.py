from __future__ import annotations

from common.enums import FileType
from libs.profiler.implementations.default import DefaultProfiler


def test_supported_mime_types_covers_every_file_type_including_unknown() -> None:
    profiler = DefaultProfiler()

    assert set(profiler.supported_mime_types) == set(FileType)
    assert FileType.UNKNOWN in profiler.supported_mime_types


def test_can_handle_always_returns_true() -> None:
    profiler = DefaultProfiler()

    assert profiler.can_handle(b"") is True
    assert profiler.can_handle(b"\xff\xfe\x00\x01") is True


def test_get_priority_always_returns_one() -> None:
    profiler = DefaultProfiler()

    assert profiler.get_priority() == 1


def test_profile_reports_the_passed_through_mime_type_not_hardcoded_unknown() -> None:
    profiler = DefaultProfiler()

    result = profiler.profile(b"some bytes", FileType.PLAIN_TEXT)

    assert result.mime_type == FileType.PLAIN_TEXT
    assert result.page_count == 0
    assert result.pages == []


def test_profile_still_reports_unknown_when_that_is_what_was_detected() -> None:
    profiler = DefaultProfiler()

    result = profiler.profile(b"some bytes", FileType.UNKNOWN)

    assert result.mime_type == FileType.UNKNOWN
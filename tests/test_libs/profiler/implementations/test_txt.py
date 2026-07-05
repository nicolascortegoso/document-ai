from __future__ import annotations

from common.enums import FileType
from libs.profiler.implementations.txt import TxtProfiler


def test_supported_mime_types_is_plain_text_only() -> None:
    profiler = TxtProfiler()

    assert profiler.supported_mime_types == [FileType.PLAIN_TEXT]


def test_get_priority_returns_fifty() -> None:
    profiler = TxtProfiler()

    assert profiler.get_priority() == 50


def test_can_handle_returns_true_for_valid_utf8() -> None:
    profiler = TxtProfiler()

    assert profiler.can_handle("Привет, мир!".encode("utf-8")) is True


def test_can_handle_returns_false_for_invalid_utf8() -> None:
    profiler = TxtProfiler()

    assert profiler.can_handle(b"\xff\xfe\x00\x01") is False


def test_profile_returns_single_synthetic_page_with_no_capabilities() -> None:
    profiler = TxtProfiler()

    result = profiler.profile(b"Some plain text.", FileType.PLAIN_TEXT)

    assert result.mime_type == FileType.PLAIN_TEXT
    assert result.page_count == 1
    assert len(result.pages) == 1

    page = result.pages[0]
    assert page.page_number == 1
    assert page.has_text is True
    assert page.has_images is False
    assert page.has_tables is False
    assert page.languages == []
    assert page._capabilities == {}
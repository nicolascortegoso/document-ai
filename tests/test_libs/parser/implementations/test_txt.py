from __future__ import annotations

from common.enums import FileType
from common.models.document import PageProfile
from libs.parser.implementations.txt import TxtPageExtractionStrategy


def test_supported_mime_types_is_plain_text_only() -> None:
    strategy = TxtPageExtractionStrategy()

    assert strategy.supported_mime_types == [FileType.PLAIN_TEXT]


def test_get_priority_returns_fifty() -> None:
    strategy = TxtPageExtractionStrategy()

    assert strategy.get_priority() == 50


def test_can_handle_always_returns_true() -> None:
    strategy = TxtPageExtractionStrategy()
    page = PageProfile(page_number=1, has_text=True, has_images=False, has_tables=False)

    assert strategy.can_handle(page) is True


def test_extract_decodes_utf8_bytes_directly() -> None:
    strategy = TxtPageExtractionStrategy()
    page = PageProfile(page_number=1, has_text=True, has_images=False, has_tables=False)

    result = strategy.extract("Привет, мир!".encode("utf-8"), page)

    assert result == "Привет, мир!"

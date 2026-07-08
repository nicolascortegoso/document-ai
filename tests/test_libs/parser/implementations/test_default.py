from __future__ import annotations

import pytest

from common.enums import FileType
from common.models.document import PageProfile
from libs.parser.base import NoExtractionAvailableError
from libs.parser.implementations.default import DefaultPageExtractionStrategy


def test_supported_mime_types_covers_every_file_type_including_unknown() -> None:
    strategy = DefaultPageExtractionStrategy()

    assert set(strategy.supported_mime_types) == set(FileType)
    assert FileType.UNKNOWN in strategy.supported_mime_types


def test_can_handle_always_returns_true() -> None:
    strategy = DefaultPageExtractionStrategy()
    page = PageProfile(page_number=1, has_text=True, has_images=False, has_tables=False)

    assert strategy.can_handle(page) is True


def test_get_priority_always_returns_one() -> None:
    strategy = DefaultPageExtractionStrategy()

    assert strategy.get_priority() == 1


def test_extract_raises_no_extraction_available_error() -> None:
    strategy = DefaultPageExtractionStrategy()
    page = PageProfile(page_number=1, has_text=True, has_images=False, has_tables=False)

    with pytest.raises(NoExtractionAvailableError):
        strategy.extract(b"some bytes", page)

from __future__ import annotations

import pytest

from common.enums import FileType
from common.models.document import PageProfile
from libs.parser.base import BasePageExtractionStrategy, NoExtractionAvailableError
from libs.parser.implementations.default import DefaultPageExtractionStrategy
from libs.parser.implementations.txt import TxtPageExtractionStrategy
from libs.parser.postprocessor.base import Postprocessor
from libs.parser.registry import (
    NoStrategyFoundError,
    ParserPriorityConflictError,
    ParserRegistry,
)

_PAGE = PageProfile(page_number=1, has_text=True, has_images=False, has_tables=False)


class _FakeStrategy(BasePageExtractionStrategy):
    """Minimal configurable BasePageExtractionStrategy for exercising the
    registry's dispatch logic without depending on Txt/Default specifics.
    """

    def __init__(
        self,
        mime_types: list[FileType],
        priority: int,
        can_handle_result: bool = True,
        extracted_text: str = "extracted",
    ) -> None:
        self._mime_types = mime_types
        self._priority = priority
        self._can_handle_result = can_handle_result
        self._extracted_text = extracted_text

    @property
    def supported_mime_types(self) -> list[FileType]:
        return self._mime_types

    def can_handle(self, page_profile: PageProfile) -> bool:
        return self._can_handle_result

    def get_priority(self) -> int:
        return self._priority

    def extract(self, file_bytes: bytes, page_profile: PageProfile) -> str:
        return self._extracted_text


class _UppercasePostprocessor(Postprocessor):
    def process(self, text: str) -> str:
        return text.upper()


def test_startup_conflict_detection_same_priority_same_filetype() -> None:
    strategy_a = _FakeStrategy([FileType.PLAIN_TEXT], priority=50)
    strategy_b = _FakeStrategy([FileType.PLAIN_TEXT], priority=50)

    with pytest.raises(ParserPriorityConflictError):
        ParserRegistry([strategy_a, strategy_b])


def test_startup_rejects_priority_outside_valid_range() -> None:
    with pytest.raises(ParserPriorityConflictError):
        ParserRegistry([_FakeStrategy([FileType.PLAIN_TEXT], priority=0)])

    with pytest.raises(ParserPriorityConflictError):
        ParserRegistry([_FakeStrategy([FileType.PLAIN_TEXT], priority=101)])


def test_priority_resolution_higher_priority_wins() -> None:
    low = _FakeStrategy([FileType.PLAIN_TEXT], priority=10, extracted_text="low")
    high = _FakeStrategy([FileType.PLAIN_TEXT], priority=90, extracted_text="high")
    registry = ParserRegistry([low, high])

    result = registry.parse_page(b"irrelevant", FileType.PLAIN_TEXT, _PAGE)

    assert result == "high"


def test_can_handle_filters_out_non_matching_candidates() -> None:
    rejects = _FakeStrategy(
        [FileType.PLAIN_TEXT], priority=90, can_handle_result=False, extracted_text="rejected"
    )
    accepts = _FakeStrategy(
        [FileType.PLAIN_TEXT], priority=10, can_handle_result=True, extracted_text="accepted"
    )
    registry = ParserRegistry([rejects, accepts])

    result = registry.parse_page(b"irrelevant", FileType.PLAIN_TEXT, _PAGE)

    assert result == "accepted"


def test_default_strategy_is_last_resort() -> None:
    default = DefaultPageExtractionStrategy()
    txt = TxtPageExtractionStrategy()
    registry = ParserRegistry([default, txt])

    result = registry.parse_page(
        "hello".encode("utf-8"), FileType.PLAIN_TEXT, _PAGE
    )

    # TxtPageExtractionStrategy (priority 50) wins over
    # DefaultPageExtractionStrategy (priority 1) — evidenced by getting the
    # actual decoded text, not raising NoExtractionAvailableError (Default's
    # behavior).
    assert result == "hello"


def test_no_extraction_available_error_propagates_when_default_wins() -> None:
    default = DefaultPageExtractionStrategy()
    registry = ParserRegistry([default])

    # Only DefaultPageExtractionStrategy is registered, so it wins by
    # elimination — its extract() raises rather than returning "".
    with pytest.raises(NoExtractionAvailableError):
        registry.parse_page(b"anything", FileType.UNKNOWN, _PAGE)


def test_no_strategy_found_error_when_default_omitted() -> None:
    txt_only = _FakeStrategy([FileType.PLAIN_TEXT], priority=50)
    registry = ParserRegistry([txt_only])

    with pytest.raises(NoStrategyFoundError):
        registry.parse_page(b"irrelevant", FileType.UNKNOWN, _PAGE)


def test_postprocessor_is_applied_to_extracted_text() -> None:
    strategy = _FakeStrategy([FileType.PLAIN_TEXT], priority=50, extracted_text="hello")
    registry = ParserRegistry([strategy], postprocessor=_UppercasePostprocessor())

    result = registry.parse_page(b"irrelevant", FileType.PLAIN_TEXT, _PAGE)

    assert result == "HELLO"


def test_default_postprocessor_used_when_none_provided() -> None:
    strategy = _FakeStrategy([FileType.PLAIN_TEXT], priority=50, extracted_text="hello")
    registry = ParserRegistry([strategy])

    result = registry.parse_page(b"irrelevant", FileType.PLAIN_TEXT, _PAGE)

    assert result == "hello"


def test_mime_type_is_passed_in_not_detected() -> None:
    # The registry never touches a Detector — mime_type comes from the caller.
    txt_only = _FakeStrategy([FileType.PLAIN_TEXT], priority=50, extracted_text="ok")
    registry = ParserRegistry([txt_only])

    result = registry.parse_page(b"anything at all", FileType.PLAIN_TEXT, _PAGE)

    assert result == "ok"

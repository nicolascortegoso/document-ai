from __future__ import annotations

import pytest

from common.enums import FileType
from common.models.chunk import DocumentChunk, SourceReference
from common.models.document import DocumentProfile
from common.models.parse import ParsedDocument
from libs.chunker.base import BaseChunkingStrategy
from libs.chunker.registry import (
    ChunkerPriorityConflictError,
    ChunkerRegistry,
    NoChunkingStrategyFoundError,
)

_DOCUMENT_PROFILE = DocumentProfile(mime_type=FileType.PLAIN_TEXT, page_count=1)
_PARSED_DOCUMENT = ParsedDocument(pages=[])


class _FakeStrategy(BaseChunkingStrategy):
    """Minimal configurable BaseChunkingStrategy for exercising the
    registry's dispatch logic without depending on SlidingWindowChunkingStrategy
    specifics.
    """

    def __init__(
        self,
        priority: int,
        can_handle_result: bool = True,
        marker: str = "fake",
    ) -> None:
        self._priority = priority
        self._can_handle_result = can_handle_result
        self._marker = marker

    def can_handle(
        self, document_profile: DocumentProfile, parsed_document: ParsedDocument
    ) -> bool:
        return self._can_handle_result

    def get_priority(self) -> int:
        return self._priority

    def chunk(
        self, document_profile: DocumentProfile, parsed_document: ParsedDocument
    ) -> list[DocumentChunk]:
        return [
            DocumentChunk(
                content=self._marker,
                source_reference=SourceReference(page_start=1, page_end=1),
                mime_type=document_profile.mime_type,
                strategy=self._marker,
            )
        ]


def test_startup_conflict_detection_same_priority() -> None:
    strategy_a = _FakeStrategy(priority=50, marker="a")
    strategy_b = _FakeStrategy(priority=50, marker="b")

    with pytest.raises(ChunkerPriorityConflictError):
        ChunkerRegistry([strategy_a, strategy_b])


def test_startup_rejects_priority_outside_valid_range() -> None:
    with pytest.raises(ChunkerPriorityConflictError):
        ChunkerRegistry([_FakeStrategy(priority=0)])

    with pytest.raises(ChunkerPriorityConflictError):
        ChunkerRegistry([_FakeStrategy(priority=101)])


def test_priority_resolution_higher_priority_wins() -> None:
    low = _FakeStrategy(priority=10, marker="low")
    high = _FakeStrategy(priority=90, marker="high")
    registry = ChunkerRegistry([low, high])

    result = registry.chunk_document(_DOCUMENT_PROFILE, _PARSED_DOCUMENT)

    assert result[0].content == "high"


def test_can_handle_filters_out_non_matching_candidates() -> None:
    rejects = _FakeStrategy(priority=90, can_handle_result=False, marker="rejects")
    accepts = _FakeStrategy(priority=10, can_handle_result=True, marker="accepts")
    registry = ChunkerRegistry([rejects, accepts])

    result = registry.chunk_document(_DOCUMENT_PROFILE, _PARSED_DOCUMENT)

    assert result[0].content == "accepts"


def test_no_chunking_strategy_found_error_when_nothing_matches() -> None:
    rejects_everything = _FakeStrategy(priority=50, can_handle_result=False)
    registry = ChunkerRegistry([rejects_everything])

    with pytest.raises(NoChunkingStrategyFoundError):
        registry.chunk_document(_DOCUMENT_PROFILE, _PARSED_DOCUMENT)
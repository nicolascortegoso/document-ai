from __future__ import annotations

import pytest

from common.enums import FileType
from common.models.chunk import DocumentChunk, SourceReference
from common.models.indexed import IndexedChunk
from libs.indexer.base import BaseIndexingStrategy
from libs.indexer.registry import (
    IndexerPriorityConflictError,
    IndexerRegistry,
    NoIndexingStrategyFoundError,
)


def _chunk() -> DocumentChunk:
    return DocumentChunk(
        content="text",
        source_reference=SourceReference(page_start=1, page_end=1),
        mime_type=FileType.PLAIN_TEXT,
        strategy="test",
    )


class _FakeStrategy(BaseIndexingStrategy):
    def __init__(
        self, priority: int, can_handle_result: bool = True, marker: str = "fake"
    ) -> None:
        self._priority = priority
        self._can_handle_result = can_handle_result
        self._marker = marker

    def can_handle(self, chunks: list[DocumentChunk]) -> bool:
        return self._can_handle_result

    def get_priority(self) -> int:
        return self._priority

    def index(self, chunks: list[DocumentChunk]) -> list[IndexedChunk]:
        # Embedding encodes the marker's length as a simple, distinguishable
        # proxy for "which strategy actually ran" — real embeddings aren't
        # meaningful here, only which fake instance produced the result.
        return [
            IndexedChunk(chunk=chunk, embedding=[float(len(self._marker))])
            for chunk in chunks
        ]


def test_startup_conflict_detection_same_priority() -> None:
    with pytest.raises(IndexerPriorityConflictError):
        IndexerRegistry([_FakeStrategy(priority=50), _FakeStrategy(priority=50)])


def test_startup_rejects_priority_outside_valid_range() -> None:
    with pytest.raises(IndexerPriorityConflictError):
        IndexerRegistry([_FakeStrategy(priority=0)])

    with pytest.raises(IndexerPriorityConflictError):
        IndexerRegistry([_FakeStrategy(priority=101)])


def test_priority_resolution_higher_priority_wins() -> None:
    low = _FakeStrategy(priority=10, marker="lo")
    high = _FakeStrategy(priority=90, marker="high-priority")
    registry = IndexerRegistry([low, high])

    result = registry.index_chunks([_chunk()])

    assert result[0].embedding == [float(len("high-priority"))]


def test_can_handle_filters_out_non_matching_candidates() -> None:
    rejects = _FakeStrategy(priority=90, can_handle_result=False, marker="rejected")
    accepts = _FakeStrategy(priority=10, can_handle_result=True, marker="ok")
    registry = IndexerRegistry([rejects, accepts])

    result = registry.index_chunks([_chunk()])

    assert result[0].embedding == [float(len("ok"))]


def test_no_indexing_strategy_found_error_when_nothing_matches() -> None:
    rejects_everything = _FakeStrategy(priority=50, can_handle_result=False)
    registry = IndexerRegistry([rejects_everything])

    with pytest.raises(NoIndexingStrategyFoundError):
        registry.index_chunks([_chunk()])

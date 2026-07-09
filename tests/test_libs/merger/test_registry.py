from __future__ import annotations

import pytest

from common.enums import FileType
from common.models.chunk import DocumentChunk, SourceReference
from common.models.tree import DocumentTree, SummaryNode
from libs.merger.base import BaseMergingStrategy
from libs.merger.registry import (
    MergerPriorityConflictError,
    MergerRegistry,
    NoMergingStrategyFoundError,
)


def _chunk() -> DocumentChunk:
    return DocumentChunk(
        content="text",
        source_reference=SourceReference(page_start=1, page_end=1),
        mime_type=FileType.PLAIN_TEXT,
        strategy="test",
    )


class _FakeStrategy(BaseMergingStrategy):
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

    def merge(self, chunks: list[DocumentChunk]) -> DocumentTree:
        return DocumentTree(
            root=SummaryNode(content=self._marker, children=[chunks[0]], level=0),
            mime_type=chunks[0].mime_type,
        )


def test_startup_conflict_detection_same_priority() -> None:
    with pytest.raises(MergerPriorityConflictError):
        MergerRegistry([_FakeStrategy(priority=50), _FakeStrategy(priority=50)])


def test_startup_rejects_priority_outside_valid_range() -> None:
    with pytest.raises(MergerPriorityConflictError):
        MergerRegistry([_FakeStrategy(priority=0)])

    with pytest.raises(MergerPriorityConflictError):
        MergerRegistry([_FakeStrategy(priority=101)])


def test_priority_resolution_higher_priority_wins() -> None:
    low = _FakeStrategy(priority=10, marker="low")
    high = _FakeStrategy(priority=90, marker="high")
    registry = MergerRegistry([low, high])

    result = registry.merge_chunks([_chunk()])

    assert result.root.content == "high"


def test_can_handle_filters_out_non_matching_candidates() -> None:
    rejects = _FakeStrategy(priority=90, can_handle_result=False, marker="rejects")
    accepts = _FakeStrategy(priority=10, can_handle_result=True, marker="accepts")
    registry = MergerRegistry([rejects, accepts])

    result = registry.merge_chunks([_chunk()])

    assert result.root.content == "accepts"


def test_no_merging_strategy_found_error_when_nothing_matches() -> None:
    rejects_everything = _FakeStrategy(priority=50, can_handle_result=False)
    registry = MergerRegistry([rejects_everything])

    with pytest.raises(NoMergingStrategyFoundError):
        registry.merge_chunks([_chunk()])
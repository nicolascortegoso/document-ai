from __future__ import annotations

from uuid import uuid4

import pytest

from common.enums import FileType
from common.models.chunk import DocumentChunk, SourceReference
from common.models.tree import SummaryNode
from libs.merger.implementations.bottom_up import (
    BottomUpMergingStrategy,
    InvalidGroupingConfigurationError,
)
from libs.merger.reducer.base import Reducer
from libs.merger.reducer.models import ReducerInput


def _chunks(n: int) -> list[DocumentChunk]:
    return [
        DocumentChunk(
            content=f"chunk{i}",
            source_reference=SourceReference(page_start=i, page_end=i),
            mime_type=FileType.PLAIN_TEXT,
            strategy="test",
        )
        for i in range(n)
    ]


def _collect_levels(node: SummaryNode) -> list[int]:
    levels = [node.level]
    for child in node.children:
        if isinstance(child, SummaryNode):
            levels.extend(_collect_levels(child))
    return levels


class _JoiningReducer(Reducer):
    """Deterministic, easy-to-assert-against reducer: joins texts with '|'."""

    def reduce(self, reducer_input: ReducerInput) -> str:
        return "|".join(reducer_input.texts)


def test_can_handle_always_returns_true() -> None:
    strategy = BottomUpMergingStrategy()

    assert strategy.can_handle(_chunks(1)) is True


def test_get_priority_always_returns_one() -> None:
    strategy = BottomUpMergingStrategy()

    assert strategy.get_priority() == 1


def test_both_group_size_and_max_depth_raises() -> None:
    with pytest.raises(InvalidGroupingConfigurationError):
        BottomUpMergingStrategy(group_size=5, max_depth=2)


def test_max_depth_less_than_one_raises() -> None:
    with pytest.raises(InvalidGroupingConfigurationError):
        BottomUpMergingStrategy(max_depth=0)


def test_merge_with_no_chunks_raises_value_error() -> None:
    strategy = BottomUpMergingStrategy()

    with pytest.raises(ValueError):
        strategy.merge([])


def test_single_chunk_document_wraps_in_a_root_summary_node() -> None:
    strategy = BottomUpMergingStrategy(reducer=_JoiningReducer())
    chunk = _chunks(1)[0]

    tree = strategy.merge([chunk])

    assert isinstance(tree.root, SummaryNode)
    assert tree.root.children == [chunk]
    assert tree.root.content == "chunk0"  # reduced (joined) even for one input
    assert tree.root.level == 0


def test_document_id_and_mime_type_threaded_through() -> None:
    strategy = BottomUpMergingStrategy(reducer=_JoiningReducer())
    document_id = uuid4()
    chunk = DocumentChunk(
        content="text",
        source_reference=SourceReference(page_start=1, page_end=1),
        mime_type=FileType.PLAIN_TEXT,
        strategy="test",
        document_id=document_id,
    )

    tree = strategy.merge([chunk])

    assert tree.document_id == document_id
    assert tree.mime_type == FileType.PLAIN_TEXT


def test_evenly_divisible_grouping_produces_expected_structure() -> None:
    # 4 chunks, group_size=2: level 0 -> two 2-child SummaryNodes; level 1 ->
    # one root grouping those two.
    strategy = BottomUpMergingStrategy(group_size=2, reducer=_JoiningReducer())
    chunks = _chunks(4)

    tree = strategy.merge(chunks)

    assert len(tree.root.children) == 2
    assert all(isinstance(c, SummaryNode) for c in tree.root.children)
    left, right = tree.root.children
    assert left.children == chunks[0:2]
    assert right.children == chunks[2:4]
    assert left.content == "chunk0|chunk1"
    assert right.content == "chunk2|chunk3"
    assert tree.root.content == "chunk0|chunk1|chunk2|chunk3"


def test_uneven_final_group_merges_into_previous_not_reduced_alone() -> None:
    # 6 chunks, group_size=5: naive grouping would be [5, 1] — the lonely
    # final group must instead merge into the previous one, producing a
    # single group of 6 and therefore a one-level tree (root's children
    # are the 6 chunks directly, not an intermediate lonely node).
    strategy = BottomUpMergingStrategy(group_size=5, reducer=_JoiningReducer())
    chunks = _chunks(6)

    tree = strategy.merge(chunks)

    assert tree.root.children == chunks
    assert len(tree.root.children) == 6


def test_sequential_ordering_preserved() -> None:
    strategy = BottomUpMergingStrategy(group_size=3, reducer=_JoiningReducer())
    chunks = _chunks(9)

    tree = strategy.merge(chunks)

    # Flatten all leaf chunks left-to-right and confirm original order.
    def _leaves(node: SummaryNode) -> list[DocumentChunk]:
        result: list[DocumentChunk] = []
        for child in node.children:
            if isinstance(child, DocumentChunk):
                result.append(child)
            else:
                result.extend(_leaves(child))
        return result

    assert _leaves(tree.root) == chunks


def test_root_level_is_always_zero_and_increases_toward_leaves() -> None:
    # 4 chunks, group_size=2 -> two levels of SummaryNode: root (level 0)
    # and its two children (level 1).
    strategy = BottomUpMergingStrategy(group_size=2, reducer=_JoiningReducer())
    tree = strategy.merge(_chunks(4))

    assert tree.root.level == 0
    assert all(child.level == 1 for child in tree.root.children)


def test_max_depth_bounds_tree_height() -> None:
    # 100 chunks, max_depth=2 -> group_size = ceil(100 ** 0.5) = 10.
    # Two reduction passes: 100 -> 10 -> 1. Levels present: {0, 1} — never
    # exceeds max_depth.
    strategy = BottomUpMergingStrategy(max_depth=2, reducer=_JoiningReducer())
    tree = strategy.merge(_chunks(100))

    levels = _collect_levels(tree.root)
    assert max(levels) + 1 <= 2
    assert tree.root.level == 0


def test_max_depth_one_collapses_to_a_single_reduction_pass() -> None:
    strategy = BottomUpMergingStrategy(max_depth=1, reducer=_JoiningReducer())
    chunks = _chunks(7)

    tree = strategy.merge(chunks)

    # Every chunk becomes a direct child of the root — one reduction pass.
    assert tree.root.children == chunks
    assert tree.root.level == 0


def test_default_group_size_is_five_when_neither_supplied() -> None:
    strategy = BottomUpMergingStrategy(reducer=_JoiningReducer())
    chunks = _chunks(5)

    tree = strategy.merge(chunks)

    # 5 chunks with default group_size=5 should collapse in a single pass.
    assert tree.root.children == chunks


def test_default_reducer_used_when_none_provided() -> None:
    strategy = BottomUpMergingStrategy()
    chunk = _chunks(1)[0]

    tree = strategy.merge([chunk])

    # DefaultReducer truncates+joins — for one short text under the char
    # limit, the result equals the original content.
    assert tree.root.content == chunk.content
from __future__ import annotations

import math

from common.models.chunk import DocumentChunk
from common.models.tree import DocumentTree, SummaryNode
from libs.merger.base import BaseMergingStrategy
from libs.merger.reducer.base import Reducer
from libs.merger.reducer.implementations.default import DefaultReducer
from libs.merger.reducer.models import ReducerInput

_DEFAULT_GROUP_SIZE = 5
_MIN_COMPUTED_GROUP_SIZE = 2


class InvalidGroupingConfigurationError(Exception):
    """Raised when both group_size and max_depth are supplied to
    BottomUpMergingStrategy, or when max_depth < 1.
    """


class BottomUpMergingStrategy(BaseMergingStrategy):
    """Universal fallback merging strategy: recursively groups chunks (and
    then summary nodes) into fixed-size batches, reducing each batch into
    one parent SummaryNode, until a single root remains.
    """

    def __init__(
        self,
        group_size: int | None = None,
        max_depth: int | None = None,
        reducer: Reducer | None = None,
    ) -> None:
        if group_size is not None and max_depth is not None:
            raise InvalidGroupingConfigurationError(
                "group_size and max_depth are mutually exclusive; supply at most one."
            )
        if max_depth is not None and max_depth < 1:
            raise InvalidGroupingConfigurationError(
                f"max_depth must be >= 1, got {max_depth}."
            )
        self._group_size = group_size
        self._max_depth = max_depth
        self._reducer = reducer or DefaultReducer()

    def can_handle(self, chunks: list[DocumentChunk]) -> bool:
        return True

    def get_priority(self) -> int:
        return 1

    def merge(self, chunks: list[DocumentChunk]) -> DocumentTree:
        if not chunks:
            raise ValueError("merge() requires at least one chunk.")

        group_size = self._resolve_group_size(len(chunks))

        current_level: list[DocumentChunk | SummaryNode] = list(chunks)
        level_counter = 0

        while len(current_level) > 1:
            groups = self._group_nodes(current_level, group_size)
            next_level: list[DocumentChunk | SummaryNode] = []
            for group in groups:
                reduced = self._reduce_group(group)
                next_level.append(
                    SummaryNode(content=reduced, children=group, level=level_counter)
                )
            current_level = next_level
            level_counter += 1

        root_candidate = current_level[0]

        if isinstance(root_candidate, DocumentChunk):
            reduced = self._reduce_group([root_candidate])
            root = SummaryNode(content=reduced, children=[root_candidate], level=0)
        else:
            root = root_candidate
            self._invert_levels(root, max_level=root.level)

        return DocumentTree(
            root=root,
            mime_type=chunks[0].mime_type,
            document_id=chunks[0].document_id,
        )

    def _resolve_group_size(self, n_chunks: int) -> int:
        if self._group_size is not None:
            return self._group_size
        if self._max_depth is not None:
            computed = math.ceil(n_chunks ** (1 / self._max_depth))
            return max(computed, _MIN_COMPUTED_GROUP_SIZE)
        return _DEFAULT_GROUP_SIZE

    @staticmethod
    def _group_nodes(
        nodes: list[DocumentChunk | SummaryNode], group_size: int
    ) -> list[list[DocumentChunk | SummaryNode]]:
        groups = [nodes[i : i + group_size] for i in range(0, len(nodes), group_size)]
        if len(groups) > 1 and len(groups[-1]) == 1:
            lonely = groups.pop()
            groups[-1] = groups[-1] + lonely
        return groups

    def _reduce_group(self, group: list[DocumentChunk | SummaryNode]) -> str:
        texts = [node.content for node in group]
        return self._reducer.reduce(ReducerInput(texts=texts))

    @staticmethod
    def _invert_levels(node: SummaryNode, max_level: int) -> None:
        node.level = max_level - node.level
        for child in node.children:
            if isinstance(child, SummaryNode):
                BottomUpMergingStrategy._invert_levels(child, max_level)

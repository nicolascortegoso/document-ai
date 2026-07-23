from __future__ import annotations

from common.models.chunk import DocumentChunk
from common.models.indexed import IndexedChunk
from libs.indexer.base import BaseIndexingStrategy

_MIN_PRIORITY = 1
_MAX_PRIORITY = 100


class IndexerPriorityConflictError(Exception):
    """Raised at startup when two registered strategies share the same priority,
    or when a strategy declares a priority outside the documented [1, 100]
    range. Indicates a misconfiguration that must be resolved before any
    documents are processed.
    """


class NoIndexingStrategyFoundError(Exception):
    """Raised at runtime when no registered strategy's can_handle() returns
    True. Under normal operation this should never occur — it signals that
    BatchIndexer was omitted from the registered strategy list.
    """


class IndexerRegistry:
    """Dispatches a list of chunks to the highest-priority matching
    indexing strategy.

    Accepts a list of strategies as its only constructor argument — no
    injected dependency at the registry level; strategies configure their
    own dependencies (e.g. an Embedder) directly.

    Startup validation:
        Raises IndexerPriorityConflictError if any two strategies share the
        same get_priority() value, or if any strategy declares a priority
        outside [1, 100].

    Dispatch flow:
        1. Call can_handle on every registered strategy
        2. Sort surviving candidates by get_priority() descending, dispatch to winner
    """

    def __init__(self, strategies: list[BaseIndexingStrategy]) -> None:
        self._strategies = strategies
        self._validate_priorities()

    def _validate_priorities(self) -> None:
        seen: dict[int, type[BaseIndexingStrategy]] = {}
        for strategy in self._strategies:
            priority = strategy.get_priority()
            if not (_MIN_PRIORITY <= priority <= _MAX_PRIORITY):
                raise IndexerPriorityConflictError(
                    f"{type(strategy).__name__} declares priority {priority}, "
                    f"outside the allowed range [{_MIN_PRIORITY}, {_MAX_PRIORITY}]."
                )
            if priority in seen:
                raise IndexerPriorityConflictError(
                    f"Priority conflict: {type(strategy).__name__} and "
                    f"{seen[priority].__name__} both declare priority {priority}."
                )
            seen[priority] = type(strategy)

    def index_chunks(self, chunks: list[DocumentChunk]) -> list[IndexedChunk]:
        survivors = [s for s in self._strategies if s.can_handle(chunks)]

        if not survivors:
            raise NoIndexingStrategyFoundError(
                "No indexing strategy found for these chunks. Ensure "
                "BatchIndexer is registered."
            )

        winner = max(survivors, key=lambda s: s.get_priority())
        return winner.index(chunks)

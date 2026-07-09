from __future__ import annotations

from common.models.chunk import DocumentChunk
from common.models.tree import DocumentTree
from libs.merger.base import BaseMergingStrategy

_MIN_PRIORITY = 1
_MAX_PRIORITY = 100


class MergerPriorityConflictError(Exception):
    """Raised at startup when two registered strategies share the same priority,
    or when a strategy declares a priority outside the documented [1, 100]
    range. Indicates a misconfiguration that must be resolved before any
    documents are processed.
    """


class NoMergingStrategyFoundError(Exception):
    """Raised at runtime when no registered strategy's can_handle() returns
    True. Under normal operation this should never occur — it signals that
    BottomUpMergingStrategy was omitted from the registered strategy list.
    """


class MergerRegistry:
    """Dispatches a list of chunks to the highest-priority matching merging
    strategy.

    Accepts a list of strategies as its only constructor argument — no
    injected dependency at the registry level; strategies configure their
    own dependencies (e.g. a Reducer) directly.

    Startup validation:
        Raises MergerPriorityConflictError if any two strategies share the
        same get_priority() value, or if any strategy declares a priority
        outside [1, 100].

    Dispatch flow:
        1. Call can_handle on every registered strategy
        2. Sort surviving candidates by get_priority() descending, dispatch to winner
    """

    def __init__(self, strategies: list[BaseMergingStrategy]) -> None:
        self._strategies = strategies
        self._validate_priorities()

    def _validate_priorities(self) -> None:
        seen: dict[int, type[BaseMergingStrategy]] = {}
        for strategy in self._strategies:
            priority = strategy.get_priority()
            if not (_MIN_PRIORITY <= priority <= _MAX_PRIORITY):
                raise MergerPriorityConflictError(
                    f"{type(strategy).__name__} declares priority {priority}, "
                    f"outside the allowed range [{_MIN_PRIORITY}, {_MAX_PRIORITY}]."
                )
            if priority in seen:
                raise MergerPriorityConflictError(
                    f"Priority conflict: {type(strategy).__name__} and "
                    f"{seen[priority].__name__} both declare priority {priority}."
                )
            seen[priority] = type(strategy)

    def merge_chunks(self, chunks: list[DocumentChunk]) -> DocumentTree:
        survivors = [s for s in self._strategies if s.can_handle(chunks)]

        if not survivors:
            raise NoMergingStrategyFoundError(
                "No merging strategy found for these chunks. Ensure "
                "BottomUpMergingStrategy is registered."
            )

        winner = max(survivors, key=lambda s: s.get_priority())
        return winner.merge(chunks)

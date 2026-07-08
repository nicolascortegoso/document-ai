from __future__ import annotations

from common.models.chunk import DocumentChunk
from common.models.document import DocumentProfile
from common.models.parse import ParsedDocument
from libs.chunker.base import BaseChunkingStrategy

_MIN_PRIORITY = 1
_MAX_PRIORITY = 100


class ChunkerPriorityConflictError(Exception):
    """Raised at startup when two registered strategies share the same priority,
    or when a strategy declares a priority outside the documented [1, 100]
    range. Indicates a misconfiguration that must be resolved before any
    documents are processed.

    Priority conflicts here are global, not partitioned per FileType — see
    CHUNKER_SPEC.md for why BaseChunkingStrategy has no MIME prefilter.
    """


class NoChunkingStrategyFoundError(Exception):
    """Raised at runtime when no registered strategy's can_handle() returns
    True. Under normal operation this should never occur — it signals that
    SlidingWindowChunkingStrategy (which always returns True) was omitted
    from the registered strategy list.
    """


class ChunkerRegistry:
    """Dispatches a parsed document to the highest-priority matching
    chunking strategy.

    Accepts a list of strategies as its only constructor argument. Unlike
    ProfilerRegistry/ParserRegistry, there is no injected dependency here —
    chunking strategies configure their own dependencies (e.g. a Splitter)
    directly, rather than the registry wiring one in.

    Startup validation:
        Raises ChunkerPriorityConflictError if any two strategies share the
        same get_priority() value, or if any strategy declares a priority
        outside [1, 100].

    Dispatch flow:
        1. Call can_handle on every registered strategy
        2. Sort surviving candidates by get_priority() descending, dispatch to winner
    """

    def __init__(self, strategies: list[BaseChunkingStrategy]) -> None:
        self._strategies = strategies
        self._validate_priorities()

    def _validate_priorities(self) -> None:
        seen: dict[int, type[BaseChunkingStrategy]] = {}
        for strategy in self._strategies:
            priority = strategy.get_priority()
            if not (_MIN_PRIORITY <= priority <= _MAX_PRIORITY):
                raise ChunkerPriorityConflictError(
                    f"{type(strategy).__name__} declares priority {priority}, "
                    f"outside the allowed range [{_MIN_PRIORITY}, {_MAX_PRIORITY}]."
                )
            if priority in seen:
                raise ChunkerPriorityConflictError(
                    f"Priority conflict: {type(strategy).__name__} and "
                    f"{seen[priority].__name__} both declare priority {priority}."
                )
            seen[priority] = type(strategy)

    def chunk_document(
        self, document_profile: DocumentProfile, parsed_document: ParsedDocument
    ) -> list[DocumentChunk]:
        survivors = [
            s
            for s in self._strategies
            if s.can_handle(document_profile, parsed_document)
        ]

        if not survivors:
            raise NoChunkingStrategyFoundError(
                "No chunking strategy found for this document. Ensure "
                "SlidingWindowChunkingStrategy is registered."
            )

        winner = max(survivors, key=lambda s: s.get_priority())
        return winner.chunk(document_profile, parsed_document)
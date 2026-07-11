from __future__ import annotations

from typing import Generic, TypeVar
from uuid import UUID

from common.models.entry import Entry
from common.models.parse import ParsedDocument
from libs.distiller.base import BaseDistillerStrategy

T = TypeVar("T", bound=Entry)

_MIN_PRIORITY = 1
_MAX_PRIORITY = 100


class DistillerPriorityConflictError(Exception):
    """Raised at startup when two registered strategies share the same priority,
    or when a strategy declares a priority outside the documented [1, 100]
    range. Indicates a misconfiguration that must be resolved before any
    documents are processed.
    """


class NoDistillingStrategyFoundError(Exception):
    """Raised at runtime when no registered strategy's can_handle() returns
    True. Under normal operation this should never occur — it signals that
    GlossaryDistillerStrategy (or an equivalent fallback for this Entry
    family) was omitted from the registered strategy list.
    """


class DistillerRegistry(Generic[T]):
    """Dispatches a document to the highest-priority matching distiller
    strategy.

    Generic over T (bound to Entry) — a single instance is scoped to one
    Entry family; strategies producing a different Entry subtype belong in
    a separate registry instance.

    Accepts a list of strategies as its only constructor argument — no
    injected dependency at the registry level; strategies configure their
    own dependencies (e.g. an Analyzer, a Composer) directly.

    Startup validation:
        Raises DistillerPriorityConflictError if any two strategies share
        the same get_priority() value, or if any strategy declares a
        priority outside [1, 100].

    Dispatch flow:
        1. Call can_handle on every registered strategy
        2. Sort surviving candidates by get_priority() descending, dispatch to winner
    """

    def __init__(self, strategies: list[BaseDistillerStrategy[T]]) -> None:
        self._strategies = strategies
        self._validate_priorities()

    def _validate_priorities(self) -> None:
        seen: dict[int, type[BaseDistillerStrategy[T]]] = {}
        for strategy in self._strategies:
            priority = strategy.get_priority()
            if not (_MIN_PRIORITY <= priority <= _MAX_PRIORITY):
                raise DistillerPriorityConflictError(
                    f"{type(strategy).__name__} declares priority {priority}, "
                    f"outside the allowed range [{_MIN_PRIORITY}, {_MAX_PRIORITY}]."
                )
            if priority in seen:
                raise DistillerPriorityConflictError(
                    f"Priority conflict: {type(strategy).__name__} and "
                    f"{seen[priority].__name__} both declare priority {priority}."
                )
            seen[priority] = type(strategy)

    def distill_document(
        self, document: ParsedDocument, document_id: UUID
    ) -> list[T]:
        survivors = [s for s in self._strategies if s.can_handle(document)]

        if not survivors:
            raise NoDistillingStrategyFoundError(
                "No distiller strategy found for this document. Ensure a "
                "fallback strategy for this Entry family is registered."
            )

        winner = max(survivors, key=lambda s: s.get_priority())
        return winner.distill(document, document_id)

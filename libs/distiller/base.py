from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from uuid import UUID

from common.models.entry import Entry
from common.models.parse import ParsedDocument

T = TypeVar("T", bound=Entry)


class BaseDistillerStrategy(ABC, Generic[T]):
    """Abstract base for all distiller strategies.

    Priority contract:
        get_priority() must return an integer in the range [1, 100].
        Higher values take precedence. GlossaryDistillerStrategy always
        declares 1, making it the last resort when no higher-priority
        strategy matches.
    """

    @abstractmethod
    def can_handle(self, document: ParsedDocument) -> bool:
        """Inspect the document to decide suitability."""

    @abstractmethod
    def get_priority(self) -> int:
        """Returns an integer priority in the range [1, 100].

        Higher value wins when multiple strategies match.
        """

    @abstractmethod
    def distill(self, document: ParsedDocument, document_id: UUID) -> list[T]:
        """Produce entries from the document.

        document_id is required, not optional — distillation presupposes
        the document has already been fully ingested.
        """
from __future__ import annotations

from abc import ABC, abstractmethod

from common.models.chunk import DocumentChunk
from common.models.indexed import IndexedChunk


class BaseIndexingStrategy(ABC):
    """Abstract base for all indexing strategies.

    Priority contract:
        get_priority() must return an integer in the range [1, 100].
        Higher values take precedence. BatchIndexer always declares 1,
        making it the last resort when no higher-priority strategy matches.
    """

    @abstractmethod
    def can_handle(self, chunks: list[DocumentChunk]) -> bool:
        """Inspect the chunks to decide suitability."""

    @abstractmethod
    def get_priority(self) -> int:
        """Returns an integer priority in the range [1, 100].

        Higher value wins when multiple strategies match.
        """

    @abstractmethod
    def index(self, chunks: list[DocumentChunk]) -> list[IndexedChunk]:
        """Produce a list of IndexedChunk from the given chunks.

        Returns an empty list if chunks is empty.
        """

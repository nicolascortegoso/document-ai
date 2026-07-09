from __future__ import annotations

from abc import ABC, abstractmethod

from common.models.chunk import DocumentChunk
from common.models.tree import DocumentTree


class BaseMergingStrategy(ABC):
    """Abstract base for all merging strategies.

    Priority contract:
        get_priority() must return an integer in the range [1, 100].
        Higher values take precedence.
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
    def merge(self, chunks: list[DocumentChunk]) -> DocumentTree:
        """Produce a DocumentTree from the given chunks."""

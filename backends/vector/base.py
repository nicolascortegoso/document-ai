from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from backends.vector.models import SearchResult, VectorRecord


class VectorNotFoundError(Exception):
    """Raised by get() when no vector exists for the given id."""


class VectorStore(ABC):
    """Abstract base for vector store implementations.

    Stores embeddings with associated metadata and supports similarity
    search. Domain-agnostic — the store has no knowledge of what id refers
    to (a DocumentChunk, a SummaryNode, a GlossaryEntry, or anything else);
    that mapping is the caller's responsibility.

    Scoped to a single collection per instance, set at construction by each
    concrete implementation — not passed per method call.
    """

    @abstractmethod
    def upsert(
        self, id: UUID, embedding: list[float], metadata: dict | None = None
    ) -> None:
        """Store or update a vector with its metadata."""

    @abstractmethod
    def get(self, id: UUID) -> VectorRecord:
        """Retrieve a stored vector by id.

        Raises VectorNotFoundError if no vector exists for id.
        """

    @abstractmethod
    def search(
        self,
        query_vector: list[float],
        top_k: int,
        filters: dict | None = None,
    ) -> list[SearchResult]:
        """Find the most similar vectors to the query vector.

        Returns up to top_k results sorted by score descending. Filters
        are implementation-specific — pass None to disable filtering.
        """

    @abstractmethod
    def delete(self, id: UUID) -> None:
        """Remove a vector by id. No-op if not found."""

    @abstractmethod
    def exists(self, id: UUID) -> bool:
        """Returns True if a vector exists for id, False otherwise."""

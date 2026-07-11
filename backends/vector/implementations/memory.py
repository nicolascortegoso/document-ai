from __future__ import annotations

import math
from uuid import UUID

from backends.vector.base import VectorNotFoundError, VectorStore
from backends.vector.models import SearchResult, VectorRecord


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    # Dimension mismatches between a and b are not validated — zip()
    # silently truncates to the shorter vector. Acceptable for a test
    # double; callers are expected to store consistently-dimensioned
    # embeddings.
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def _matches_filters(metadata: dict | None, filters: dict | None) -> bool:
    if filters is None:
        return True
    if metadata is None:
        return False
    return all(metadata.get(key) == value for key, value in filters.items())


class InMemoryVectorStore(VectorStore):
    """Dict-backed, in-process. Not thread-safe, not persisted across
    restarts — for testing and local development only.

    Brute-force linear scan over all stored vectors for search() —
    correct, not fast. Cosine similarity.
    """

    def __init__(self, collection_name: str) -> None:
        self._collection_name = collection_name
        self._records: dict[UUID, VectorRecord] = {}

    def upsert(
        self, id: UUID, embedding: list[float], metadata: dict | None = None
    ) -> None:
        self._records[id] = VectorRecord(
            id=id, embedding=embedding, metadata=metadata
        )

    def get(self, id: UUID) -> VectorRecord:
        try:
            return self._records[id]
        except KeyError:
            raise VectorNotFoundError(
                f"No vector found for id {id!r} in collection "
                f"{self._collection_name!r}."
            ) from None

    def search(
        self,
        query_vector: list[float],
        top_k: int,
        filters: dict | None = None,
    ) -> list[SearchResult]:
        if top_k <= 0:
            return []

        candidates = [
            SearchResult(
                id=record.id,
                score=_cosine_similarity(query_vector, record.embedding),
                metadata=record.metadata,
            )
            for record in self._records.values()
            if _matches_filters(record.metadata, filters)
        ]
        candidates.sort(key=lambda r: r.score, reverse=True)
        return candidates[:top_k]

    def delete(self, id: UUID) -> None:
        self._records.pop(id, None)

    def exists(self, id: UUID) -> bool:
        return id in self._records

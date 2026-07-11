from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass
class SearchResult:
    id: UUID
    score: float
    metadata: dict | None = None


@dataclass
class VectorRecord:
    id: UUID
    embedding: list[float]
    metadata: dict | None = None

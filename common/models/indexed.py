from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from common.models.chunk import DocumentChunk


@dataclass
class IndexedChunk:
    chunk: DocumentChunk
    embedding: list[float]

    def to_dict(self) -> dict[str, Any]:
        return {
            "chunk": self.chunk.to_dict(),
            "embedding": self.embedding,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> IndexedChunk:
        return cls(
            chunk=DocumentChunk.from_dict(data["chunk"]),
            embedding=data["embedding"],
        )

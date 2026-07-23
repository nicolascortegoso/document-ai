from __future__ import annotations

from common.models.chunk import DocumentChunk
from common.models.indexed import IndexedChunk
from libs.indexer.base import BaseIndexingStrategy
from libs.indexer.embedder.base import Embedder
from libs.indexer.embedder.implementations.dummy import DummyEmbedder


class BatchIndexer(BaseIndexingStrategy):
    """Universal fallback indexing strategy: embeds every chunk's content
    in a single batch call to the injected Embedder.
    """

    def __init__(self, embedder: Embedder | None = None) -> None:
        self._embedder = embedder or DummyEmbedder()

    def can_handle(self, chunks: list[DocumentChunk]) -> bool:
        return True

    def get_priority(self) -> int:
        return 1

    def index(self, chunks: list[DocumentChunk]) -> list[IndexedChunk]:
        if not chunks:
            return []

        embeddings = self._embedder.embed([chunk.content for chunk in chunks])
        return [
            IndexedChunk(chunk=chunk, embedding=embedding)
            for chunk, embedding in zip(chunks, embeddings)
        ]

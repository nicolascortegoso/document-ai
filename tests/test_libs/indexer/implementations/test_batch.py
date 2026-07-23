from __future__ import annotations

from common.enums import FileType
from common.models.chunk import DocumentChunk, SourceReference
from libs.indexer.embedder.base import Embedder
from libs.indexer.implementations.batch import BatchIndexer


def _chunk(content: str, page: int = 1) -> DocumentChunk:
    return DocumentChunk(
        content=content,
        source_reference=SourceReference(page_start=page, page_end=page),
        mime_type=FileType.PLAIN_TEXT,
        strategy="test",
    )


class _SpyEmbedder(Embedder):
    """Records every call, returns a deterministic embedding per text."""

    def __init__(self) -> None:
        self.calls: list[list[str]] = []

    def embed(self, texts: list[str]) -> list[list[float]]:
        self.calls.append(texts)
        return [[float(len(t))] for t in texts]


def test_can_handle_always_returns_true() -> None:
    indexer = BatchIndexer()

    assert indexer.can_handle([_chunk("text")]) is True


def test_get_priority_always_returns_one() -> None:
    indexer = BatchIndexer()

    assert indexer.get_priority() == 1


def test_empty_chunks_list_returns_empty_list_without_calling_embedder() -> None:
    spy = _SpyEmbedder()
    indexer = BatchIndexer(embedder=spy)

    result = indexer.index([])

    assert result == []
    assert spy.calls == []


def test_calls_embedder_once_with_every_chunk_content_in_one_batch() -> None:
    spy = _SpyEmbedder()
    indexer = BatchIndexer(embedder=spy)
    chunks = [_chunk("first"), _chunk("second"), _chunk("third")]

    indexer.index(chunks)

    assert len(spy.calls) == 1  # one batch call, not one per chunk
    assert spy.calls[0] == ["first", "second", "third"]


def test_pairs_each_chunk_with_its_corresponding_embedding_in_order() -> None:
    spy = _SpyEmbedder()
    indexer = BatchIndexer(embedder=spy)
    chunks = [_chunk("a"), _chunk("bb"), _chunk("ccc")]

    result = indexer.index(chunks)

    assert [r.chunk.content for r in result] == ["a", "bb", "ccc"]
    assert [r.embedding for r in result] == [[1.0], [2.0], [3.0]]


def test_default_embedder_used_when_none_provided() -> None:
    indexer = BatchIndexer()

    result = indexer.index([_chunk("some text")])

    # DummyEmbedder produces a real (if meaningless) vector — confirms the
    # default is actually wired in, not left unset.
    assert len(result) == 1
    assert len(result[0].embedding) == 8

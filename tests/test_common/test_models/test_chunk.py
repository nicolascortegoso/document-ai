from __future__ import annotations

from uuid import uuid4

from common.enums import FileType
from common.models.chunk import DocumentChunk, SourceReference


def test_document_chunk_roundtrip_with_document_id() -> None:
    document_id = uuid4()
    chunk = DocumentChunk(
        content="some extracted text",
        source_reference=SourceReference(page_start=1, page_end=1),
        mime_type=FileType.PLAIN_TEXT,
        strategy="SlidingWindowChunkingStrategy",
        document_id=document_id,
    )

    restored = DocumentChunk.from_dict(chunk.to_dict())

    assert restored == chunk
    assert restored.document_id == document_id


def test_document_chunk_id_is_auto_generated_and_unique() -> None:
    chunk_a = DocumentChunk(
        content="a",
        source_reference=SourceReference(page_start=1, page_end=1),
        mime_type=FileType.PLAIN_TEXT,
        strategy="test",
    )
    chunk_b = DocumentChunk(
        content="b",
        source_reference=SourceReference(page_start=1, page_end=1),
        mime_type=FileType.PLAIN_TEXT,
        strategy="test",
    )

    assert chunk_a.id != chunk_b.id


def test_document_chunk_document_id_defaults_to_none() -> None:
    chunk = DocumentChunk(
        content="a",
        source_reference=SourceReference(page_start=1, page_end=1),
        mime_type=FileType.PLAIN_TEXT,
        strategy="test",
    )

    assert chunk.document_id is None
    assert chunk.to_dict()["document_id"] is None

    restored = DocumentChunk.from_dict(chunk.to_dict())
    assert restored.document_id is None


def test_source_reference_roundtrip() -> None:
    ref = SourceReference(page_start=2, page_end=4)

    restored = SourceReference.from_dict(ref.to_dict())

    assert restored == ref
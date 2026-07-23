from __future__ import annotations

from collections.abc import Callable
from typing import Any

from backends.vector.base import VectorStore
from common.models.indexed import IndexedChunk


def make_store_chunks_job(
    vector_store: VectorStore,
) -> Callable[[list[dict[str, Any]]], list[str]]:
    """Build the plain, framework-free job function for the
    "store_chunks" job.

    Takes IndexedChunks as a plain list[dict], not dataclasses — job
    arguments must stay serializable across any Queue implementation.
    Depends only on vector_store — no pipeline, since storing is a
    backends/ operation with no libs/ orchestration involved.

    Returns the stored ids, not the full IndexedChunks — the caller
    already has the embeddings it passed in.
    """

    def store_chunks(indexed_chunks: list[dict[str, Any]]) -> list[str]:
        stored_ids: list[str] = []
        for data in indexed_chunks:
            indexed_chunk = IndexedChunk.from_dict(data)
            document_id = indexed_chunk.chunk.document_id
            vector_store.upsert(
                id=indexed_chunk.chunk.id,
                embedding=indexed_chunk.embedding,
                metadata={
                    "document_id": str(document_id) if document_id else None,
                    "mime_type": indexed_chunk.chunk.mime_type.value,
                },
            )
            stored_ids.append(str(indexed_chunk.chunk.id))
        return stored_ids

    return store_chunks

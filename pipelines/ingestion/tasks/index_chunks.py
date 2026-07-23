from __future__ import annotations

from collections.abc import Callable
from typing import Any

from common.models.chunk import DocumentChunk
from pipelines.ingestion.base import BaseIngestionPipeline


def make_index_chunks_job(
    pipeline: BaseIngestionPipeline,
) -> Callable[[list[dict[str, Any]]], list[dict[str, Any]]]:
    """Build the plain, framework-free job function for the
    "index_chunks" job.

    Takes chunks as a plain list[dict], not DocumentChunk dataclasses — job
    arguments must stay serializable across any Queue implementation.
    Depends only on the pipeline — no VectorStore, matching
    profile_document/parse_document/chunk_document's shape.
    """

    def index_chunks(chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        reconstructed = [DocumentChunk.from_dict(c) for c in chunks]
        indexed_chunks = pipeline.index(reconstructed)
        return [indexed_chunk.to_dict() for indexed_chunk in indexed_chunks]

    return index_chunks

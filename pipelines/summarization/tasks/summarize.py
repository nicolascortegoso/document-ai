from __future__ import annotations

from collections.abc import Callable
from typing import Any

from common.models.chunk import DocumentChunk
from pipelines.summarization.base import BaseSummarizationPipeline


def make_summarize_chunks_job(
    pipeline: BaseSummarizationPipeline,
) -> Callable[[list[dict[str, Any]]], dict[str, Any]]:
    """Build the plain, framework-free job function for the
    "summarize_chunks" job.

    Takes chunks as a plain list[dict], not DocumentChunk dataclasses — job
    arguments must stay serializable across any Queue implementation, not
    just DummyQueue's in-process one. Needs no mime_type or document_id
    parameter — both already travel on each DocumentChunk.
    """

    def summarize_chunks(chunks: list[dict[str, Any]]) -> dict[str, Any]:
        reconstructed = [DocumentChunk.from_dict(c) for c in chunks]
        tree = pipeline.summarize(reconstructed)
        return tree.to_dict()

    return summarize_chunks

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from common.models.document import DocumentProfile
from common.models.parse import ParsedDocument
from pipelines.ingestion.base import BaseIngestionPipeline


def make_chunk_document_job(
    pipeline: BaseIngestionPipeline,
) -> Callable[[dict[str, Any], dict[str, Any]], list[dict[str, Any]]]:
    """Build the plain, framework-free job function for the
    "chunk_document" job.

    Takes DocumentProfile and ParsedDocument as plain dicts, not the
    dataclasses — job arguments must stay serializable across any Queue
    implementation, not just DummyQueue's in-process one. Unlike
    profile_document/parse_document, this job needs no file_bytes at all:
    chunking operates entirely on already-profiled, already-parsed content.
    """

    def chunk_document(
        document_profile: dict[str, Any], parsed_document: dict[str, Any]
    ) -> list[dict[str, Any]]:
        profile = DocumentProfile.from_dict(document_profile)
        parsed = ParsedDocument.from_dict(parsed_document)
        chunks = pipeline.chunk(profile, parsed)
        return [c.to_dict() for c in chunks]

    return chunk_document

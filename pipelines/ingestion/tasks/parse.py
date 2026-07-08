from __future__ import annotations

from collections.abc import Callable
from typing import Any

from common.models.document import DocumentProfile
from pipelines.ingestion.base import BaseIngestionPipeline


def make_parse_document_job(
    pipeline: BaseIngestionPipeline,
) -> Callable[[bytes, dict[str, Any]], dict[str, Any]]:
    """Build the plain, framework-free job function for the
    "parse_document" job.

    Takes the DocumentProfile as a plain dict, not the dataclass — job
    arguments must stay serializable across any Queue implementation, not
    just DummyQueue's in-process one. The dict is reconstructed into a
    DocumentProfile internally before being passed to the pipeline.
    """

    def parse_document(file_bytes: bytes, document_profile: dict[str, Any]) -> dict[str, Any]:
        profile = DocumentProfile.from_dict(document_profile)
        result = pipeline.parse(file_bytes, profile)
        return result.to_dict()

    return parse_document

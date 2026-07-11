from __future__ import annotations

from collections.abc import Callable
from typing import Any
from uuid import UUID

from common.models.parse import ParsedDocument
from pipelines.distillation.base import BaseDistillationPipeline


def make_distill_document_job(
    pipeline: BaseDistillationPipeline,
) -> Callable[[dict[str, Any], str], list[dict[str, Any]]]:
    """Build the plain, framework-free job function for the
    "distill_document" job.

    Takes the parsed document as a plain dict and document_id as a plain
    str, not ParsedDocument/UUID — job arguments must stay serializable
    across any Queue implementation, not just DummyQueue's in-process one.
    """

    def distill_document(
        document: dict[str, Any], document_id: str
    ) -> list[dict[str, Any]]:
        parsed_document = ParsedDocument.from_dict(document)
        entries = pipeline.distill(parsed_document, UUID(document_id))
        return [entry.to_dict() for entry in entries]

    return distill_document

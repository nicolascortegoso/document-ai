from __future__ import annotations

from typing import TypeVar
from uuid import UUID

from common.models.entry import Entry
from common.models.parse import ParsedDocument
from libs.distiller.registry import DistillerRegistry
from pipelines.distillation.base import BaseDistillationPipeline

T = TypeVar("T", bound=Entry)


class DistillationPipeline(BaseDistillationPipeline[T]):
    """Concrete distillation pipeline, composing libs/distiller/ behind the
    BaseDistillationPipeline contract.
    """

    def __init__(self, distiller_registry: DistillerRegistry[T]) -> None:
        self._distiller_registry = distiller_registry

    def distill(self, document: ParsedDocument, document_id: UUID) -> list[T]:
        return self._distiller_registry.distill_document(document, document_id)

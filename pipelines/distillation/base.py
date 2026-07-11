from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from uuid import UUID

from common.models.entry import Entry
from common.models.parse import ParsedDocument

T = TypeVar("T", bound=Entry)


class BaseDistillationPipeline(ABC, Generic[T]):
    """Abstract contract for the distillation pipeline.

    Defines the stage contract, not the execution strategy (per
    PIPELINES_SPEC.md) — a concrete implementation composes the actual
    libs/ domain logic behind it. Split from BaseIngestionPipeline into its
    own pipeline for the same reason BaseSummarizationPipeline was: a
    different computational profile once Analyzer/Composer are LLM-backed.

    Generic over T (bound to Entry), mirroring libs/distiller/ — a given
    pipeline instance is scoped to one Entry family.
    """

    @abstractmethod
    def distill(self, document: ParsedDocument, document_id: UUID) -> list[T]:
        """Produce entries from the given document."""

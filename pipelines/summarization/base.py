from __future__ import annotations

from abc import ABC, abstractmethod

from common.models.chunk import DocumentChunk
from common.models.tree import DocumentTree


class BaseSummarizationPipeline(ABC):
    """Abstract contract for the summarization pipeline.

    Defines the stage contract, not the execution strategy (per
    PIPELINES_SPEC.md) — a concrete implementation composes the actual
    libs/ domain logic behind it. Split from BaseIngestionPipeline into its
    own pipeline: merging has a different computational profile once its
    Reducer is LLM-backed, needing different retry/timeout/scaling behavior
    than the fast, local profile/parse/chunk stages.
    """

    @abstractmethod
    def summarize(self, chunks: list[DocumentChunk]) -> DocumentTree:
        """Produce a DocumentTree from the given chunks."""

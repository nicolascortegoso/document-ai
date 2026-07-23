from __future__ import annotations

from common.models.chunk import DocumentChunk
from common.models.tree import DocumentTree
from libs.merger.registry import MergerRegistry
from pipelines.summarization.base import BaseSummarizationPipeline


class SummarizationPipeline(BaseSummarizationPipeline):
    """Concrete summarization pipeline, composing libs/merger/ behind the
    BaseSummarizationPipeline contract.
    """

    def __init__(self, merger_registry: MergerRegistry) -> None:
        self._merger_registry = merger_registry

    def summarize(self, chunks: list[DocumentChunk]) -> DocumentTree:
        return self._merger_registry.merge_chunks(chunks)

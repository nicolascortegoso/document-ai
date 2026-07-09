from __future__ import annotations

from common.enums import FileType
from common.models.chunk import DocumentChunk, SourceReference
from common.models.tree import DocumentTree
from libs.merger.implementations.bottom_up import BottomUpMergingStrategy
from libs.merger.registry import MergerRegistry
from pipelines.summarization.implementations.summarization import SummarizationPipeline


def _chunk(page: int, content: str) -> DocumentChunk:
    return DocumentChunk(
        content=content,
        source_reference=SourceReference(page_start=page, page_end=page),
        mime_type=FileType.PLAIN_TEXT,
        strategy="test",
    )


def test_summarize_delegates_to_the_injected_merger_registry() -> None:
    merger_registry = MergerRegistry([BottomUpMergingStrategy()])
    pipeline = SummarizationPipeline(merger_registry)
    chunks = [_chunk(1, "hello"), _chunk(2, "world")]

    result = pipeline.summarize(chunks)

    assert isinstance(result, DocumentTree)
    assert result.root.children == chunks

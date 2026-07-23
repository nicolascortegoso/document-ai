from __future__ import annotations

from backends.queue.implementations.dummy import DummyQueue
from backends.queue.models import JobStatus
from libs.chunker.implementations.sliding_window import SlidingWindowChunkingStrategy
from libs.chunker.registry import ChunkerRegistry
from libs.indexer.implementations.batch import BatchIndexer
from libs.indexer.registry import IndexerRegistry
from libs.parser.implementations.default import DefaultPageExtractionStrategy
from libs.parser.implementations.txt import TxtPageExtractionStrategy
from libs.parser.registry import ParserRegistry
from libs.profiler.implementations.default import DefaultProfiler
from libs.profiler.implementations.txt import TxtProfiler
from libs.profiler.registry import ProfilerRegistry
from pipelines.ingestion.implementations.ingestion import IngestionPipeline
from pipelines.ingestion.tasks.index_chunks import make_index_chunks_job


def _make_pipeline() -> IngestionPipeline:
    profiler_registry = ProfilerRegistry([DefaultProfiler(), TxtProfiler()])
    parser_registry = ParserRegistry(
        [DefaultPageExtractionStrategy(), TxtPageExtractionStrategy()]
    )
    chunker_registry = ChunkerRegistry([SlidingWindowChunkingStrategy()])
    indexer_registry = IndexerRegistry([BatchIndexer()])
    return IngestionPipeline(
        profiler_registry, parser_registry, chunker_registry, indexer_registry
    )


def _chunk_dict() -> dict:
    return {
        "content": "hello world",
        "source_reference": {"page_start": 1, "page_end": 1},
        "mime_type": "text/plain",
        "strategy": "test",
        "id": "11111111-1111-1111-1111-111111111111",
        "document_id": None,
    }


def test_job_returns_a_list_of_serializable_indexed_chunk_dicts() -> None:
    pipeline = _make_pipeline()
    job = make_index_chunks_job(pipeline)

    result = job([_chunk_dict()])

    assert isinstance(result, list)
    assert result[0]["chunk"]["content"] == "hello world"
    assert len(result[0]["embedding"]) == 8


def test_job_does_not_touch_any_vector_store() -> None:
    # index_chunks has no VectorStore dependency at all — this is really
    # confirmed by its factory signature (make_index_chunks_job(pipeline)
    # takes no vector_store param), but exercising it end-to-end confirms
    # the job runs to completion with nothing beyond the pipeline.
    pipeline = _make_pipeline()
    job = make_index_chunks_job(pipeline)

    result = job([_chunk_dict(), _chunk_dict()])

    assert len(result) == 2


def test_job_dispatched_through_dummy_queue_end_to_end() -> None:
    pipeline = _make_pipeline()
    job = make_index_chunks_job(pipeline)
    queue = DummyQueue(jobs={"index_chunks": job})

    handle = queue.dispatch("index_chunks", [_chunk_dict()])

    assert handle.status == JobStatus.SUCCESS
    assert handle.result[0]["chunk"]["content"] == "hello world"

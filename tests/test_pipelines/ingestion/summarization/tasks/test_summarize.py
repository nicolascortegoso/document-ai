from __future__ import annotations

from backends.queue.implementations.dummy import DummyQueue
from backends.queue.models import JobStatus
from libs.chunker.implementations.sliding_window import SlidingWindowChunkingStrategy
from libs.chunker.registry import ChunkerRegistry
from libs.merger.implementations.bottom_up import BottomUpMergingStrategy
from libs.merger.registry import MergerRegistry
from libs.parser.implementations.default import DefaultPageExtractionStrategy
from libs.parser.implementations.txt import TxtPageExtractionStrategy
from libs.parser.registry import ParserRegistry
from libs.profiler.implementations.default import DefaultProfiler
from libs.profiler.implementations.txt import TxtProfiler
from libs.profiler.registry import ProfilerRegistry
from pipelines.ingestion.implementations.pipeline import IngestionPipeline
from pipelines.ingestion.tasks.chunk import make_chunk_document_job
from pipelines.ingestion.tasks.parse import make_parse_document_job
from pipelines.ingestion.tasks.profile import make_profile_document_job
from pipelines.summarization.implementations.summarization import SummarizationPipeline
from pipelines.summarization.tasks.summarize import make_summarize_chunks_job


def _make_ingestion_pipeline() -> IngestionPipeline:
    profiler_registry = ProfilerRegistry([DefaultProfiler(), TxtProfiler()])
    parser_registry = ParserRegistry(
        [DefaultPageExtractionStrategy(), TxtPageExtractionStrategy()]
    )
    chunker_registry = ChunkerRegistry([SlidingWindowChunkingStrategy()])
    return IngestionPipeline(profiler_registry, parser_registry, chunker_registry)


def _make_summarization_pipeline() -> SummarizationPipeline:
    merger_registry = MergerRegistry([BottomUpMergingStrategy()])
    return SummarizationPipeline(merger_registry)


def test_job_accepts_a_list_of_chunk_dicts_and_returns_a_serializable_tree() -> None:
    pipeline = _make_summarization_pipeline()
    chunks_dicts = [
        {
            "content": "hello",
            "source_reference": {"page_start": 1, "page_end": 1},
            "mime_type": "text/plain",
            "strategy": "test",
            "id": "11111111-1111-1111-1111-111111111111",
            "document_id": None,
        }
    ]

    job = make_summarize_chunks_job(pipeline)
    result = job(chunks_dicts)

    assert isinstance(result, dict)
    assert result["root"]["children"][0]["content"] == "hello"


def test_job_dispatched_through_dummy_queue_end_to_end() -> None:
    pipeline = _make_summarization_pipeline()
    chunks_dicts = [
        {
            "content": "hello",
            "source_reference": {"page_start": 1, "page_end": 1},
            "mime_type": "text/plain",
            "strategy": "test",
            "id": "11111111-1111-1111-1111-111111111111",
            "document_id": None,
        }
    ]

    job = make_summarize_chunks_job(pipeline)
    queue = DummyQueue(jobs={"summarize_chunks": job})

    handle = queue.dispatch("summarize_chunks", chunks_dicts)

    assert handle.status == JobStatus.SUCCESS
    assert handle.result["root"]["children"][0]["content"] == "hello"


def test_full_chain_profile_parse_chunk_summarize_across_both_pipelines() -> None:
    # The realistic flow: dispatch through pipelines/ingestion/'s three
    # jobs, then feed chunk_document's result directly into
    # pipelines/summarization/'s job — two independently-built pipelines,
    # connected only through Queue dispatch, never through direct imports
    # between the two pipeline packages.
    ingestion_pipeline = _make_ingestion_pipeline()
    summarization_pipeline = _make_summarization_pipeline()
    file_bytes = "Привет, мир! Это тестовый документ.".encode("utf-8")

    queue = DummyQueue(
        jobs={
            "profile_document": make_profile_document_job(ingestion_pipeline),
            "parse_document": make_parse_document_job(ingestion_pipeline),
            "chunk_document": make_chunk_document_job(ingestion_pipeline),
            "summarize_chunks": make_summarize_chunks_job(summarization_pipeline),
        }
    )

    profile_handle = queue.dispatch("profile_document", file_bytes)
    assert profile_handle.status == JobStatus.SUCCESS

    parse_handle = queue.dispatch(
        "parse_document", file_bytes, profile_handle.result
    )
    assert parse_handle.status == JobStatus.SUCCESS

    chunk_handle = queue.dispatch(
        "chunk_document", profile_handle.result, parse_handle.result
    )
    assert chunk_handle.status == JobStatus.SUCCESS

    summarize_handle = queue.dispatch("summarize_chunks", chunk_handle.result)
    assert summarize_handle.status == JobStatus.SUCCESS

    assert summarize_handle.result["root"]["children"][0]["content"] == (
        "Привет, мир! Это тестовый документ."
    )

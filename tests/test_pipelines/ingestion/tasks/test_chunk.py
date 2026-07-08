from __future__ import annotations

from backends.queue.implementations.dummy import DummyQueue
from backends.queue.models import JobStatus
from libs.chunker.implementations.sliding_window import SlidingWindowChunkingStrategy
from libs.chunker.registry import ChunkerRegistry
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


def _make_pipeline() -> IngestionPipeline:
    profiler_registry = ProfilerRegistry([DefaultProfiler(), TxtProfiler()])
    parser_registry = ParserRegistry(
        [DefaultPageExtractionStrategy(), TxtPageExtractionStrategy()]
    )
    chunker_registry = ChunkerRegistry([SlidingWindowChunkingStrategy()])
    return IngestionPipeline(profiler_registry, parser_registry, chunker_registry)


def test_job_takes_no_file_bytes_and_returns_a_list_of_serializable_dicts() -> None:
    pipeline = _make_pipeline()
    file_bytes = "hello world".encode("utf-8")
    document_profile_dict = pipeline.profile(file_bytes).to_dict()
    parsed_document_dict = pipeline.parse(
        file_bytes, pipeline.profile(file_bytes)
    ).to_dict()

    job = make_chunk_document_job(pipeline)
    result = job(document_profile_dict, parsed_document_dict)

    assert isinstance(result, list)
    assert result[0]["content"] == "hello world"
    assert result[0]["mime_type"] == "text/plain"


def test_job_dispatched_through_dummy_queue_end_to_end() -> None:
    pipeline = _make_pipeline()
    file_bytes = "hello world".encode("utf-8")
    document_profile = pipeline.profile(file_bytes)
    document_profile_dict = document_profile.to_dict()
    parsed_document_dict = pipeline.parse(file_bytes, document_profile).to_dict()

    job = make_chunk_document_job(pipeline)
    queue = DummyQueue(jobs={"chunk_document": job})

    handle = queue.dispatch("chunk_document", document_profile_dict, parsed_document_dict)

    assert handle.status == JobStatus.SUCCESS
    assert handle.result[0]["content"] == "hello world"


def test_profile_parse_chunk_chained_through_the_same_queue() -> None:
    # The realistic flow: profile -> parse -> chunk, each dispatch feeding
    # its (serialized) result into the next.
    pipeline = _make_pipeline()
    file_bytes = "Привет, мир! Это тестовый документ.".encode("utf-8")

    queue = DummyQueue(
        jobs={
            "profile_document": make_profile_document_job(pipeline),
            "parse_document": make_parse_document_job(pipeline),
            "chunk_document": make_chunk_document_job(pipeline),
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

    assert len(chunk_handle.result) == 1
    assert chunk_handle.result[0]["content"] == "Привет, мир! Это тестовый документ."
    assert chunk_handle.result[0]["strategy"] == "SlidingWindowChunkingStrategy"
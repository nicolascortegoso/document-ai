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
from pipelines.ingestion.tasks.parse import make_parse_document_job
from pipelines.ingestion.tasks.profile import make_profile_document_job


def _make_pipeline() -> IngestionPipeline:
    profiler_registry = ProfilerRegistry([DefaultProfiler(), TxtProfiler()])
    parser_registry = ParserRegistry(
        [DefaultPageExtractionStrategy(), TxtPageExtractionStrategy()]
    )
    chunker_registry = ChunkerRegistry([SlidingWindowChunkingStrategy()])
    return IngestionPipeline(profiler_registry, parser_registry, chunker_registry)


def test_job_accepts_a_document_profile_dict_and_returns_a_serializable_dict() -> None:
    pipeline = _make_pipeline()
    file_bytes = "hello world".encode("utf-8")
    document_profile_dict = pipeline.profile(file_bytes).to_dict()

    job = make_parse_document_job(pipeline)
    result = job(file_bytes, document_profile_dict)

    assert isinstance(result, dict)
    assert result["pages"] == [{"page_number": 1, "text": "hello world"}]


def test_job_dispatched_through_dummy_queue_end_to_end() -> None:
    pipeline = _make_pipeline()
    file_bytes = "hello world".encode("utf-8")
    document_profile_dict = pipeline.profile(file_bytes).to_dict()

    job = make_parse_document_job(pipeline)
    queue = DummyQueue(jobs={"parse_document": job})

    handle = queue.dispatch("parse_document", file_bytes, document_profile_dict)

    assert handle.status == JobStatus.SUCCESS
    assert handle.result["pages"][0]["text"] == "hello world"


def test_profile_then_parse_chained_through_the_same_queue() -> None:
    # The realistic flow: dispatch "profile_document" first, feed its
    # (serialized) result into "parse_document" as the next dispatch.
    pipeline = _make_pipeline()
    file_bytes = "Привет, мир!".encode("utf-8")

    queue = DummyQueue(
        jobs={
            "profile_document": make_profile_document_job(pipeline),
            "parse_document": make_parse_document_job(pipeline),
        }
    )

    profile_handle = queue.dispatch("profile_document", file_bytes)
    assert profile_handle.status == JobStatus.SUCCESS

    parse_handle = queue.dispatch(
        "parse_document", file_bytes, profile_handle.result
    )

    assert parse_handle.status == JobStatus.SUCCESS
    assert parse_handle.result["pages"][0]["text"] == "Привет, мир!"

from __future__ import annotations

from backends.queue.implementations.dummy import DummyQueue
from backends.queue.models import JobStatus
from libs.chunker.implementations.sliding_window import SlidingWindowChunkingStrategy
from libs.chunker.registry import ChunkerRegistry
from libs.distiller.implementations.glossary import GlossaryDistillerStrategy
from libs.distiller.registry import DistillerRegistry
from libs.parser.implementations.default import DefaultPageExtractionStrategy
from libs.parser.implementations.txt import TxtPageExtractionStrategy
from libs.parser.registry import ParserRegistry
from libs.profiler.implementations.default import DefaultProfiler
from libs.profiler.implementations.txt import TxtProfiler
from libs.profiler.registry import ProfilerRegistry
from pipelines.distillation.implementations.distillation import DistillationPipeline
from pipelines.distillation.tasks.distill import make_distill_document_job
from pipelines.ingestion.implementations.pipeline import IngestionPipeline
from pipelines.ingestion.tasks.parse import make_parse_document_job
from pipelines.ingestion.tasks.profile import make_profile_document_job


def _make_ingestion_pipeline() -> IngestionPipeline:
    profiler_registry = ProfilerRegistry([DefaultProfiler(), TxtProfiler()])
    parser_registry = ParserRegistry(
        [DefaultPageExtractionStrategy(), TxtPageExtractionStrategy()]
    )
    chunker_registry = ChunkerRegistry([SlidingWindowChunkingStrategy()])
    return IngestionPipeline(profiler_registry, parser_registry, chunker_registry)


def _make_distillation_pipeline() -> DistillationPipeline:
    distiller_registry = DistillerRegistry([GlossaryDistillerStrategy()])
    return DistillationPipeline(distiller_registry)


def test_job_accepts_a_document_dict_and_document_id_string() -> None:
    pipeline = _make_distillation_pipeline()
    document_dict = {
        "pages": [{"page_number": 1, "text": "compressor compressor turbine"}]
    }

    job = make_distill_document_job(pipeline)
    result = job(document_dict, "11111111-1111-1111-1111-111111111111")

    assert isinstance(result, list)
    terms = {entry["term"] for entry in result}
    assert "compressor" in terms


def test_job_dispatched_through_dummy_queue_end_to_end() -> None:
    pipeline = _make_distillation_pipeline()
    document_dict = {
        "pages": [{"page_number": 1, "text": "compressor compressor turbine"}]
    }

    job = make_distill_document_job(pipeline)
    queue = DummyQueue(jobs={"distill_document": job})

    handle = queue.dispatch(
        "distill_document", document_dict, "11111111-1111-1111-1111-111111111111"
    )

    assert handle.status == JobStatus.SUCCESS
    terms = {entry["term"] for entry in handle.result}
    assert "compressor" in terms


def test_full_chain_profile_parse_then_distill_across_both_pipelines() -> None:
    # The realistic flow: dispatch through pipelines/ingestion/'s
    # profile_document + parse_document jobs, then feed parse_document's
    # result directly into pipelines/distillation/'s job — two
    # independently-built pipelines, connected only through Queue
    # dispatch, never through direct imports between the two packages.
    ingestion_pipeline = _make_ingestion_pipeline()
    distillation_pipeline = _make_distillation_pipeline()
    file_bytes = "compressor compressor turbine valve gas pressure".encode("utf-8")

    queue = DummyQueue(
        jobs={
            "profile_document": make_profile_document_job(ingestion_pipeline),
            "parse_document": make_parse_document_job(ingestion_pipeline),
            "distill_document": make_distill_document_job(distillation_pipeline),
        }
    )

    profile_handle = queue.dispatch("profile_document", file_bytes)
    assert profile_handle.status == JobStatus.SUCCESS

    parse_handle = queue.dispatch(
        "parse_document", file_bytes, profile_handle.result
    )
    assert parse_handle.status == JobStatus.SUCCESS

    distill_handle = queue.dispatch(
        "distill_document",
        parse_handle.result,
        "11111111-1111-1111-1111-111111111111",
    )
    assert distill_handle.status == JobStatus.SUCCESS

    terms = {entry["term"] for entry in distill_handle.result}
    assert "compressor" in terms

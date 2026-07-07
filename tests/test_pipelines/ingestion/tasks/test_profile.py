from __future__ import annotations

from backends.queue.implementations.dummy import DummyQueue
from backends.queue.models import JobStatus
from libs.profiler.implementations.default import DefaultProfiler
from libs.profiler.implementations.txt import TxtProfiler
from libs.profiler.registry import ProfilerRegistry
from pipelines.ingestion.pipeline import IngestionPipeline
from pipelines.ingestion.tasks.profile import make_profile_document_job


def _make_pipeline() -> IngestionPipeline:
    registry = ProfilerRegistry([DefaultProfiler(), TxtProfiler()])
    return IngestionPipeline(registry)


def test_job_returns_a_serializable_dict_not_a_document_profile() -> None:
    job = make_profile_document_job(_make_pipeline())

    result = job("hello world".encode("utf-8"))

    assert isinstance(result, dict)
    assert result["mime_type"] == "text/plain"
    assert result["page_count"] == 1
    assert result["pages"][0]["has_text"] is True


def test_job_dispatched_through_dummy_queue_end_to_end() -> None:
    job = make_profile_document_job(_make_pipeline())
    queue = DummyQueue(jobs={"profile_document": job})

    handle = queue.dispatch("profile_document", "hello world".encode("utf-8"))

    assert handle.status == JobStatus.SUCCESS
    assert handle.result["mime_type"] == "text/plain"
    assert handle.result["page_count"] == 1
from __future__ import annotations

from common.enums import FileType
from common.models.document import DocumentProfile
from libs.profiler.implementations.default import DefaultProfiler
from libs.profiler.implementations.txt import TxtProfiler
from libs.profiler.registry import ProfilerRegistry
from pipelines.ingestion.pipeline import IngestionPipeline


def test_profile_delegates_to_the_injected_profiler_registry() -> None:
    registry = ProfilerRegistry([DefaultProfiler(), TxtProfiler()])
    pipeline = IngestionPipeline(registry)

    result = pipeline.profile("hello world".encode("utf-8"))

    assert isinstance(result, DocumentProfile)
    assert result.mime_type == FileType.PLAIN_TEXT
    assert result.page_count == 1


def test_profile_falls_back_to_default_profiler_for_unrecognised_bytes() -> None:
    registry = ProfilerRegistry([DefaultProfiler(), TxtProfiler()])
    pipeline = IngestionPipeline(registry)

    # High-entropy binary with no recognisable magic-byte signature — not
    # a UTF-16 BOM or anything else python-magic would classify as text.
    unrecognisable = bytes([0x93, 0x27, 0x5A, 0xC1, 0x08, 0x44, 0x91, 0xDE, 0x00, 0x77] * 5)

    result = pipeline.profile(unrecognisable)

    # DefaultProfiler wins (TxtProfiler's can_handle rejects non-UTF-8
    # input), and correctly reports the actual detected type rather than
    # hardcoding one.
    assert result.mime_type == FileType.UNKNOWN
    assert result.page_count == 0
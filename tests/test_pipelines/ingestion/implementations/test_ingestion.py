from __future__ import annotations

from common.enums import FileType
from common.models.document import DocumentProfile, PageProfile
from libs.parser.implementations.default import DefaultPageExtractionStrategy
from libs.parser.implementations.txt import TxtPageExtractionStrategy
from libs.parser.registry import ParserRegistry
from libs.profiler.implementations.default import DefaultProfiler
from libs.profiler.implementations.txt import TxtProfiler
from libs.profiler.registry import ProfilerRegistry
from pipelines.ingestion.implementations.pipeline import IngestionPipeline


def _make_pipeline() -> IngestionPipeline:
    profiler_registry = ProfilerRegistry([DefaultProfiler(), TxtProfiler()])
    parser_registry = ParserRegistry(
        [DefaultPageExtractionStrategy(), TxtPageExtractionStrategy()]
    )
    return IngestionPipeline(profiler_registry, parser_registry)


def test_profile_delegates_to_the_injected_profiler_registry() -> None:
    pipeline = _make_pipeline()

    result = pipeline.profile("hello world".encode("utf-8"))

    assert isinstance(result, DocumentProfile)
    assert result.mime_type == FileType.PLAIN_TEXT
    assert result.page_count == 1


def test_profile_falls_back_to_default_profiler_for_unrecognised_bytes() -> None:
    pipeline = _make_pipeline()

    # High-entropy binary with no recognisable magic-byte signature — not
    # a UTF-16 BOM or anything else python-magic would classify as text.
    unrecognisable = bytes([0x93, 0x27, 0x5A, 0xC1, 0x08, 0x44, 0x91, 0xDE, 0x00, 0x77] * 5)

    result = pipeline.profile(unrecognisable)

    # DefaultProfiler wins (TxtProfiler's can_handle rejects non-UTF-8
    # input), and correctly reports the actual detected type rather than
    # hardcoding one.
    assert result.mime_type == FileType.UNKNOWN
    assert result.page_count == 0


def test_parse_extracts_text_for_every_page_in_the_document_profile() -> None:
    pipeline = _make_pipeline()
    file_bytes = "Привет, мир!".encode("utf-8")
    document_profile = pipeline.profile(file_bytes)

    result = pipeline.parse(file_bytes, document_profile)

    assert len(result.pages) == 1
    assert result.pages[0].page_number == 1
    assert result.pages[0].text == "Привет, мир!"


def test_parse_preserves_page_numbers_across_multiple_pages() -> None:
    # Plain text only ever produces one synthetic page today, but parse()
    # is written to iterate document_profile.pages generically — construct
    # a DocumentProfile with more than one page directly to prove the
    # iteration itself is correct, independent of what profiling produces.
    pipeline = _make_pipeline()
    file_bytes = "irrelevant for this test".encode("utf-8")

    document_profile = DocumentProfile(
        mime_type=FileType.PLAIN_TEXT,
        page_count=2,
        pages=[
            PageProfile(page_number=1, has_text=True, has_images=False, has_tables=False),
            PageProfile(page_number=2, has_text=True, has_images=False, has_tables=False),
        ],
    )

    result = pipeline.parse(file_bytes, document_profile)

    assert [p.page_number for p in result.pages] == [1, 2]
    assert all(p.text == "irrelevant for this test" for p in result.pages)

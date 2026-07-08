from __future__ import annotations

from uuid import uuid4

from common.enums import FileType
from common.models.document import DocumentProfile
from common.models.parse import ParsedDocument, ParsedPage
from libs.chunker.implementations.sliding_window import SlidingWindowChunkingStrategy
from libs.chunker.splitter.base import Splitter


def _document_profile(document_id=None) -> DocumentProfile:
    return DocumentProfile(
        mime_type=FileType.PLAIN_TEXT, page_count=1, document_id=document_id
    )


def test_can_handle_always_returns_true() -> None:
    strategy = SlidingWindowChunkingStrategy()

    assert strategy.can_handle(_document_profile(), ParsedDocument(pages=[])) is True


def test_get_priority_always_returns_one() -> None:
    strategy = SlidingWindowChunkingStrategy()

    assert strategy.get_priority() == 1


def test_empty_page_produces_no_chunks() -> None:
    strategy = SlidingWindowChunkingStrategy()
    parsed = ParsedDocument(pages=[ParsedPage(page_number=1, text="")])

    result = strategy.chunk(_document_profile(), parsed)

    assert result == []


def test_whitespace_only_page_produces_no_chunks() -> None:
    strategy = SlidingWindowChunkingStrategy()
    parsed = ParsedDocument(pages=[ParsedPage(page_number=1, text="   \n\t  ")])

    result = strategy.chunk(_document_profile(), parsed)

    assert result == []


def test_short_page_produces_a_single_chunk_with_full_text() -> None:
    strategy = SlidingWindowChunkingStrategy(window_size=200)
    text = "just a few words here"
    parsed = ParsedDocument(pages=[ParsedPage(page_number=1, text=text)])

    result = strategy.chunk(_document_profile(), parsed)

    assert len(result) == 1
    assert result[0].content == text


def test_default_overlap_is_ten_percent_of_window_size() -> None:
    strategy = SlidingWindowChunkingStrategy(window_size=200)

    assert strategy._overlap == 20


def test_sliding_window_with_overlap_produces_expected_chunks() -> None:
    text = " ".join(f"word{i}" for i in range(12))
    parsed = ParsedDocument(pages=[ParsedPage(page_number=1, text=text)])

    strategy = SlidingWindowChunkingStrategy(window_size=5, overlap=2)
    result = strategy.chunk(_document_profile(), parsed)

    contents = [c.content for c in result]
    # Overlap of 2 words between consecutive chunks, advancing 3 words per
    # window; each chunk's tail should reappear as the next chunk's head.
    for content in contents:
        assert content  # every chunk has real content
    assert contents[0].startswith("word0")
    assert contents[-1].endswith(f"word{11}")
    # Consecutive chunks overlap: the last 2 words of one chunk are the
    # first 2 words of the next.
    for earlier, later in zip(contents, contents[1:]):
        earlier_tail = " ".join(earlier.split()[-2:])
        later_head = " ".join(later.split()[:2])
        assert earlier_tail == later_head


def test_document_id_and_mime_type_are_threaded_through() -> None:
    document_id = uuid4()
    strategy = SlidingWindowChunkingStrategy()
    parsed = ParsedDocument(pages=[ParsedPage(page_number=1, text="some text here")])

    result = strategy.chunk(_document_profile(document_id=document_id), parsed)

    assert result[0].document_id == document_id
    assert result[0].mime_type == FileType.PLAIN_TEXT
    assert result[0].strategy == "SlidingWindowChunkingStrategy"


def test_source_reference_page_start_equals_page_end() -> None:
    strategy = SlidingWindowChunkingStrategy()
    parsed = ParsedDocument(pages=[ParsedPage(page_number=3, text="some text here")])

    result = strategy.chunk(_document_profile(), parsed)

    assert result[0].source_reference.page_start == 3
    assert result[0].source_reference.page_end == 3


def test_multi_page_document_chunks_each_page_independently() -> None:
    strategy = SlidingWindowChunkingStrategy()
    parsed = ParsedDocument(
        pages=[
            ParsedPage(page_number=1, text="first page content"),
            ParsedPage(page_number=2, text="second page content"),
        ]
    )

    result = strategy.chunk(_document_profile(), parsed)

    assert len(result) == 2
    assert result[0].content == "first page content"
    assert result[0].source_reference.page_start == 1
    assert result[1].content == "second page content"
    assert result[1].source_reference.page_start == 2


class _SpySplitter(Splitter):
    def __init__(self) -> None:
        self.calls: list[tuple[str, int]] = []

    def find_split(self, text: str, position: int) -> int:
        self.calls.append((text, position))
        return position


def test_custom_splitter_is_actually_used() -> None:
    spy = _SpySplitter()
    text = " ".join(f"word{i}" for i in range(10))
    strategy = SlidingWindowChunkingStrategy(splitter=spy, window_size=3, overlap=1)
    parsed = ParsedDocument(pages=[ParsedPage(page_number=1, text=text)])

    strategy.chunk(_document_profile(), parsed)

    assert len(spy.calls) > 0
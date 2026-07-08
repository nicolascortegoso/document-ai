from __future__ import annotations

import re

from common.models.chunk import DocumentChunk, SourceReference
from common.models.document import DocumentProfile
from common.models.parse import ParsedDocument, ParsedPage
from libs.chunker.base import BaseChunkingStrategy
from libs.chunker.splitter.base import Splitter
from libs.chunker.splitter.implementations.default import DefaultSplitter

_STRATEGY_NAME = "SlidingWindowChunkingStrategy"
_DEFAULT_WINDOW_SIZE = 200
_WORD_PATTERN = re.compile(r"\S+")


class SlidingWindowChunkingStrategy(BaseChunkingStrategy):
    """Universal fallback chunking strategy: fixed-size, overlapping windows
    of words, aligned to natural text boundaries via an injected Splitter.

    Unlike DefaultProfiler / DefaultPageExtractionStrategy, this is not a
    no-op — chunking has no sensible "give up and return nothing useful"
    behavior, so this is a real, working general-purpose strategy that
    happens to also serve as the last resort (get_priority() -> 1).

    Processes each page independently — never merges content across page
    boundaries into a single chunk. Every chunk's SourceReference therefore
    has page_start == page_end.
    """

    def __init__(
        self,
        splitter: Splitter | None = None,
        window_size: int = _DEFAULT_WINDOW_SIZE,
        overlap: int | None = None,
    ) -> None:
        self._splitter = splitter or DefaultSplitter()
        self._window_size = window_size
        self._overlap = overlap if overlap is not None else max(1, window_size // 10)

    def can_handle(
        self, document_profile: DocumentProfile, parsed_document: ParsedDocument
    ) -> bool:
        return True

    def get_priority(self) -> int:
        return 1

    def chunk(
        self, document_profile: DocumentProfile, parsed_document: ParsedDocument
    ) -> list[DocumentChunk]:
        chunks: list[DocumentChunk] = []
        for page in parsed_document.pages:
            chunks.extend(self._chunk_page(page, document_profile))
        return chunks

    def _chunk_page(
        self, page: ParsedPage, document_profile: DocumentProfile
    ) -> list[DocumentChunk]:
        text = page.text
        if not text.strip():
            return []

        words = list(_WORD_PATTERN.finditer(text))

        chunks: list[DocumentChunk] = []
        n_words = len(words)
        start_word_idx = 0

        # Advance by at least 1 word every iteration, regardless of window
        # size / overlap configuration, to guarantee loop termination even
        # if overlap >= window_size.
        advance = max(self._window_size - self._overlap, 1)

        while start_word_idx < n_words:
            end_word_idx = min(start_word_idx + self._window_size, n_words) - 1
            is_last_window = end_word_idx >= n_words - 1

            char_start = words[start_word_idx].start()
            char_end = (
                len(text)
                if is_last_window
                else self._splitter.find_split(text, words[end_word_idx].end())
            )

            content = text[char_start:char_end].strip()
            if content:
                chunks.append(
                    DocumentChunk(
                        content=content,
                        source_reference=SourceReference(
                            page_start=page.page_number, page_end=page.page_number
                        ),
                        mime_type=document_profile.mime_type,
                        strategy=_STRATEGY_NAME,
                        document_id=document_profile.document_id,
                    )
                )

            if is_last_window:
                break

            start_word_idx += advance

        return chunks
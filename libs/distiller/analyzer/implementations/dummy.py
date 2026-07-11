from __future__ import annotations

import json
import re
from collections import defaultdict

from common.models.parse import ParsedDocument
from libs.distiller.analyzer.base import Analyzer

_WORD_PATTERN = re.compile(r"\w+")
_DEFAULT_MIN_WORD_LENGTH = 4


class DummyAnalyzer(Analyzer):
    """Word-frequency counting. A non-LLM-backed placeholder with no real
    practical application, not a production-quality analysis technique.
    """

    def __init__(self, min_word_length: int = _DEFAULT_MIN_WORD_LENGTH) -> None:
        self._min_word_length = min_word_length

    def analyze(self, document: ParsedDocument) -> str:
        counts: dict[str, int] = defaultdict(int)
        pages: dict[str, set[int]] = defaultdict(set)

        for page in document.pages:
            for match in _WORD_PATTERN.finditer(page.text.lower()):
                word = match.group()
                if len(word) < self._min_word_length:
                    continue
                counts[word] += 1
                pages[word].add(page.page_number)

        result = {
            word: {"count": count, "pages": sorted(pages[word])}
            for word, count in counts.items()
        }
        return json.dumps(result)
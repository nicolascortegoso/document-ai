from __future__ import annotations

import json
from uuid import UUID

from libs.distiller.composer.base import BaseComposer
from libs.distiller.models import GlossaryEntry

_DEFAULT_TOP_N = 20


class DummyComposer(BaseComposer[GlossaryEntry]):
    """Selects the top_n most frequent words from DummyAnalyzer's output.
    A non-LLM-backed placeholder with no real practical application, not a
    production-quality composition technique.
    """

    def __init__(self, top_n: int = _DEFAULT_TOP_N) -> None:
        self._top_n = top_n

    def compose(self, analyzed: str, document_id: UUID) -> list[GlossaryEntry]:
        data = json.loads(analyzed)  # raises on malformed input, not absorbed

        total_count = sum(entry["count"] for entry in data.values())

        sorted_words = sorted(
            data.items(), key=lambda item: item[1]["count"], reverse=True
        )
        top_words = sorted_words[: self._top_n]

        return [
            GlossaryEntry(
                document_id=document_id,
                term=word,
                pages=info["pages"],
                confidence=info["count"] / total_count,
            )
            for word, info in top_words
        ]
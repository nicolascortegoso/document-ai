from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from common.models.entry import Entry


@dataclass(kw_only=True)
class GlossaryEntry(Entry):
    term: str
    pages: list[int]
    confidence: float
    aliases: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data.update(
            {
                "term": self.term,
                "pages": self.pages,
                "confidence": self.confidence,
                "aliases": self.aliases,
            }
        )
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GlossaryEntry:
        return cls(
            document_id=UUID(data["document_id"]),
            id=UUID(data["id"]),
            term=data["term"],
            pages=data["pages"],
            confidence=data["confidence"],
            aliases=data.get("aliases", []),
        )

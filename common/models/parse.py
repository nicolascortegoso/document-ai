from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ParsedPage:
    page_number: int
    text: str

    def to_dict(self) -> dict[str, Any]:
        return {"page_number": self.page_number, "text": self.text}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ParsedPage:
        return cls(page_number=data["page_number"], text=data["text"])


@dataclass
class ParsedDocument:
    pages: list[ParsedPage]

    def to_dict(self) -> dict[str, Any]:
        return {"pages": [p.to_dict() for p in self.pages]}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ParsedDocument:
        return cls(pages=[ParsedPage.from_dict(p) for p in data["pages"]])

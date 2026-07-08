from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID, uuid4

from common.enums import FileType


@dataclass
class SourceReference:
    page_start: int
    page_end: int

    def to_dict(self) -> dict[str, Any]:
        return {"page_start": self.page_start, "page_end": self.page_end}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SourceReference:
        return cls(page_start=data["page_start"], page_end=data["page_end"])


@dataclass
class DocumentChunk:
    content: str
    source_reference: SourceReference
    mime_type: FileType
    strategy: str
    id: UUID = field(default_factory=uuid4)
    document_id: UUID | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "content": self.content,
            "source_reference": self.source_reference.to_dict(),
            "mime_type": self.mime_type.value,
            "strategy": self.strategy,
            "id": str(self.id),
            "document_id": str(self.document_id) if self.document_id else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DocumentChunk:
        return cls(
            content=data["content"],
            source_reference=SourceReference.from_dict(data["source_reference"]),
            mime_type=FileType(data["mime_type"]),
            strategy=data["strategy"],
            id=UUID(data["id"]),
            document_id=UUID(data["document_id"]) if data.get("document_id") else None,
        )
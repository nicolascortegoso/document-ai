from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID, uuid4

from common.enums import FileType
from common.models.chunk import DocumentChunk, SourceReference


class InvalidTreeNodeError(Exception):
    """Raised by SummaryNode.__post_init__ when children is empty.

    A SummaryNode with no children can't compute source_reference (there's
    nothing to derive a page range from) and doesn't represent anything
    reduced.

    Deliberately not validated here: that children are in sequential
    document order. Whether that ordering matters, and how it's upheld, is
    a property of how a given merging strategy groups its inputs — common/
    doesn't bake one strategy's assumption into a model every strategy has
    to produce.
    """


@dataclass
class SummaryNode:
    content: str
    children: list[DocumentChunk | SummaryNode]
    level: int
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not self.children:
            raise InvalidTreeNodeError("SummaryNode.children must not be empty.")

    @property
    def source_reference(self) -> SourceReference:
        return SourceReference(
            page_start=self.children[0].source_reference.page_start,
            page_end=self.children[-1].source_reference.page_end,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "content": self.content,
            "children": [child.to_dict() for child in self.children],
            "level": self.level,
            "id": str(self.id),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SummaryNode:
        children: list[DocumentChunk | SummaryNode] = []
        for child_data in data["children"]:
            if "children" in child_data:
                children.append(cls.from_dict(child_data))
            else:
                children.append(DocumentChunk.from_dict(child_data))
        return cls(
            content=data["content"],
            children=children,
            level=data["level"],
            id=UUID(data["id"]),
        )


@dataclass
class DocumentTree:
    root: SummaryNode
    mime_type: FileType
    document_id: UUID | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "root": self.root.to_dict(),
            "mime_type": self.mime_type.value,
            "document_id": str(self.document_id) if self.document_id else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DocumentTree:
        return cls(
            root=SummaryNode.from_dict(data["root"]),
            mime_type=FileType(data["mime_type"]),
            document_id=UUID(data["document_id"]) if data.get("document_id") else None,
        )

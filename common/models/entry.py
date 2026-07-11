from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID, uuid4


@dataclass(kw_only=True)
class Entry:
    document_id: UUID
    id: UUID = field(default_factory=uuid4)

    def to_dict(self) -> dict[str, Any]:
        return {
            "document_id": str(self.document_id),
            "id": str(self.id),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Entry:
        return cls(document_id=UUID(data["document_id"]), id=UUID(data["id"]))
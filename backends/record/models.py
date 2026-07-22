from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID


@dataclass
class DocumentRecord:
    document_id: UUID
    external_id: str
    checksum: str
    pipeline_statuses: dict[str, str] = field(default_factory=dict)

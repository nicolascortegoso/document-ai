from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, ClassVar, TypeVar
from uuid import UUID

from common.enums import FileType
from common.models.capability_registry import CAPABILITY_REGISTRY

T = TypeVar("T")


@dataclass
class PageProfile:
    page_number: int
    has_text: bool
    has_images: bool
    has_tables: bool
    languages: list[str] = field(default_factory=list)
    _capabilities: dict[type, object] = field(default_factory=dict, repr=False)

    _CORE_FIELDS: ClassVar[set[str]] = {
        "page_number", "has_text", "has_images", "has_tables", "languages",
    }

    def add(self, capability: object) -> PageProfile:
        self._capabilities[type(capability)] = capability
        return self

    def get(self, capability_type: type[T]) -> T | None:
        return self._capabilities.get(capability_type)  # type: ignore[return-value]

    def has(self, capability_type: type) -> bool:
        return capability_type in self._capabilities

    def to_dict(self) -> dict[str, Any]:
        data = {name: getattr(self, name) for name in self._CORE_FIELDS}
        data["capabilities"] = {
            type(c).__name__: asdict(c) for c in self._capabilities.values()
        }
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PageProfile:
        core = {k: v for k, v in data.items() if k in cls._CORE_FIELDS}
        profile = cls(**core)
        for name, payload in data.get("capabilities", {}).items():
            capability_cls = CAPABILITY_REGISTRY.get(name)
            if capability_cls is None:
                continue  # unknown capability; skip rather than fail
            profile.add(capability_cls(**payload))
        return profile


@dataclass
class DocumentProfile:
    mime_type: FileType
    page_count: int
    pages: list[PageProfile] = field(default_factory=list)
    document_id: UUID | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "mime_type": self.mime_type.value,
            "page_count": self.page_count,
            "pages": [p.to_dict() for p in self.pages],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DocumentProfile:
        return cls(
            mime_type=FileType(data["mime_type"]),
            page_count=data["page_count"],
            pages=[PageProfile.from_dict(p) for p in data.get("pages", [])],
        )
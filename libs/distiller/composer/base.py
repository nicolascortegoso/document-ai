from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from uuid import UUID

from common.models.entry import Entry

T = TypeVar("T", bound=Entry)


class BaseComposer(ABC, Generic[T]):
    @abstractmethod
    def compose(self, analyzed: str, document_id: UUID) -> list[T]:
        """Build structured entries from an Analyzer's extracted text.

        Does not carry a "never raises" contract — a failure to compose
        entries from malformed or unusable analyzed text should surface
        rather than be silently absorbed into an empty list.
        """
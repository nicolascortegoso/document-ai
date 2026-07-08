from __future__ import annotations

from abc import ABC, abstractmethod

from common.models.document import DocumentProfile
from common.models.parsed import ParsedDocument


class BaseIngestionPipeline(ABC):
    """Abstract contract for the document ingestion pipeline.

    Defines stage contracts, not execution strategies (per PIPELINES_SPEC.md)
    — a concrete implementation composes the actual libs/ domain logic
    behind each method. Scoped to profiling and parsing in this release;
    further stages (chunk, merge, index) are added as methods once their
    underlying libs/ modules exist.
    """

    @abstractmethod
    def profile(self, file_bytes: bytes) -> DocumentProfile:
        """Produce a DocumentProfile for the given raw document bytes."""

    @abstractmethod
    def parse(self, file_bytes: bytes, document_profile: DocumentProfile) -> ParsedDocument:
        """Extract text for every page in document_profile, given the same
        raw document bytes profiling was run on.
        """

from __future__ import annotations

from abc import ABC, abstractmethod

from common.models.chunk import DocumentChunk
from common.models.document import DocumentProfile
from common.models.parse import ParsedDocument


class BaseIngestionPipeline(ABC):
    """Abstract contract for the document ingestion pipeline.

    Defines stage contracts, not execution strategies (per PIPELINES_SPEC.md)
    — a concrete implementation composes the actual libs/ domain logic
    behind each method. Scoped to profiling, parsing, and chunking in this
    release; further stages (merge, index) are added as methods once their
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

    @abstractmethod
    def chunk(
        self, document_profile: DocumentProfile, parsed_document: ParsedDocument
    ) -> list[DocumentChunk]:
        """Produce chunks from parsed_document, using document_profile for
        chunking-strategy-relevant context. Needs no raw bytes — chunking
        operates entirely on already-profiled, already-parsed content.
        """
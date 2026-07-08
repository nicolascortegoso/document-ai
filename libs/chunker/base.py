from __future__ import annotations

from abc import ABC, abstractmethod

from common.models.chunk import DocumentChunk
from common.models.document import DocumentProfile
from common.models.parse import ParsedDocument


class BaseChunkingStrategy(ABC):
    """Abstract base for all chunking strategies.

    Priority contract:
        get_priority() must return an integer in the range [1, 100].
        Higher values take precedence. SlidingWindowChunkingStrategy always
        declares 1, as it is the universal fallback.

    Unlike BaseDocumentProfiler / BasePageExtractionStrategy, there is no
    supported_mime_types / MIME prefilter here — see CHUNKER_SPEC.md for
    why. Chunking suitability depends on the shape of the parsed content
    (e.g. PageProfile.has_tables, an attached capability), not the original
    file format, which no longer reliably predicts the right approach once
    text has already been extracted.
    """

    @abstractmethod
    def can_handle(
        self, document_profile: DocumentProfile, parsed_document: ParsedDocument
    ) -> bool:
        """Inspect the profile and parsed content to decide suitability.

        Returns True if this strategy can process the given document.
        """

    @abstractmethod
    def get_priority(self) -> int:
        """Returns an integer priority in the range [1, 100].

        Higher value wins when multiple strategies match.
        SlidingWindowChunkingStrategy always returns 1.
        """

    @abstractmethod
    def chunk(
        self, document_profile: DocumentProfile, parsed_document: ParsedDocument
    ) -> list[DocumentChunk]:
        """Produce a list of DocumentChunk from the parsed document.

        Returns an empty list if the document has no content.
        """
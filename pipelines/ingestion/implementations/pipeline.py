from __future__ import annotations

from common.models.chunk import DocumentChunk
from common.models.document import DocumentProfile
from common.models.parse import ParsedDocument, ParsedPage
from libs.chunker.registry import ChunkerRegistry
from libs.parser.registry import ParserRegistry
from libs.profiler.registry import ProfilerRegistry
from pipelines.ingestion.base import BaseIngestionPipeline


class IngestionPipeline(BaseIngestionPipeline):
    """Concrete ingestion pipeline, composing libs/ domain logic behind the
    BaseIngestionPipeline contract.
    """

    def __init__(
        self,
        profiler_registry: ProfilerRegistry,
        parser_registry: ParserRegistry,
        chunker_registry: ChunkerRegistry,
    ) -> None:
        self._profiler_registry = profiler_registry
        self._parser_registry = parser_registry
        self._chunker_registry = chunker_registry

    def profile(self, file_bytes: bytes) -> DocumentProfile:
        return self._profiler_registry.profile(file_bytes)

    def parse(self, file_bytes: bytes, document_profile: DocumentProfile) -> ParsedDocument:
        pages = [
            ParsedPage(
                page_number=page_profile.page_number,
                text=self._parser_registry.parse_page(
                    file_bytes, document_profile.mime_type, page_profile
                ),
            )
            for page_profile in document_profile.pages
        ]
        return ParsedDocument(pages=pages)

    def chunk(
        self, document_profile: DocumentProfile, parsed_document: ParsedDocument
    ) -> list[DocumentChunk]:
        return self._chunker_registry.chunk_document(document_profile, parsed_document)
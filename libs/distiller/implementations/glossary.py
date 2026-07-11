from __future__ import annotations

from uuid import UUID

from common.models.parse import ParsedDocument
from libs.distiller.analyzer.base import Analyzer
from libs.distiller.analyzer.implementations.dummy import DummyAnalyzer
from libs.distiller.base import BaseDistillerStrategy
from libs.distiller.composer.base import BaseComposer
from libs.distiller.composer.implementations.dummy import DummyComposer
from libs.distiller.models import GlossaryEntry


class GlossaryDistillerStrategy(BaseDistillerStrategy[GlossaryEntry]):
    """Universal fallback distiller strategy for the GlossaryEntry family.

    Composes an injected Analyzer and Composer: analyze() extracts
    unstructured signal from the document, compose() structures that
    signal into GlossaryEntry objects.
    """

    def __init__(
        self,
        analyzer: Analyzer | None = None,
        composer: BaseComposer[GlossaryEntry] | None = None,
    ) -> None:
        self._analyzer = analyzer or DummyAnalyzer()
        self._composer = composer or DummyComposer()

    def can_handle(self, document: ParsedDocument) -> bool:
        return True

    def get_priority(self) -> int:
        return 1

    def distill(self, document: ParsedDocument, document_id: UUID) -> list[GlossaryEntry]:
        analyzed = self._analyzer.analyze(document)
        return self._composer.compose(analyzed, document_id)
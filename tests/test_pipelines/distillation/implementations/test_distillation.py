from __future__ import annotations

from uuid import uuid4

from common.models.parse import ParsedDocument, ParsedPage
from libs.distiller.implementations.glossary import GlossaryDistillerStrategy
from libs.distiller.registry import DistillerRegistry
from pipelines.distillation.implementations.standard import DistillationPipeline


def test_distill_delegates_to_the_injected_distiller_registry() -> None:
    distiller_registry = DistillerRegistry([GlossaryDistillerStrategy()])
    pipeline = DistillationPipeline(distiller_registry)
    document = ParsedDocument(
        pages=[ParsedPage(page_number=1, text="compressor compressor turbine")]
    )

    result = pipeline.distill(document, uuid4())

    terms = {entry.term for entry in result}
    assert "compressor" in terms

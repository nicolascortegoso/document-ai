from __future__ import annotations

from libs.parser.postprocessor.base import Postprocessor
from libs.parser.postprocessor.implementations.steps.base import PostprocessingStep


class ChainedPostprocessor(Postprocessor):
    """Applies a sequence of PostprocessingStep instances in order, feeding
    each step's output into the next.

    No concrete PostprocessingStep implementations ship yet — this class
    exists as a tested chaining mechanism so future steps (e.g. whitespace
    normalization, OCR artifact correction) can be added without any change
    to ParserRegistry or this class.
    """

    def __init__(self, steps: list[PostprocessingStep]) -> None:
        self._steps = steps

    def process(self, text: str) -> str:
        for step in self._steps:
            text = step.apply(text)
        return text

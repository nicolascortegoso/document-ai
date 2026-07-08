from __future__ import annotations

from libs.parser.postprocessor.implementations.chained import ChainedPostprocessor
from libs.parser.postprocessor.implementations.steps.base import PostprocessingStep


class _UppercaseStep(PostprocessingStep):
    def apply(self, text: str) -> str:
        return text.upper()


class _StripStep(PostprocessingStep):
    def apply(self, text: str) -> str:
        return text.strip()


class _AppendExclamationStep(PostprocessingStep):
    def apply(self, text: str) -> str:
        return text + "!"


def test_applies_a_single_step() -> None:
    postprocessor = ChainedPostprocessor(steps=[_UppercaseStep()])

    assert postprocessor.process("hello") == "HELLO"


def test_applies_multiple_steps_in_order() -> None:
    postprocessor = ChainedPostprocessor(
        steps=[_StripStep(), _UppercaseStep(), _AppendExclamationStep()]
    )

    result = postprocessor.process("  hello  ")

    # Order matters: strip first (removes padding), then uppercase, then
    # append "!" last. A different order would produce a different result
    # (e.g. appending before stripping would leave trailing whitespace
    # before the "!").
    assert result == "HELLO!"


def test_empty_step_list_returns_input_unchanged() -> None:
    postprocessor = ChainedPostprocessor(steps=[])

    assert postprocessor.process("unchanged") == "unchanged"

from __future__ import annotations

from libs.parser.postprocessor.implementations.default import DefaultPostprocessor


def test_process_returns_input_unchanged() -> None:
    postprocessor = DefaultPostprocessor()

    assert postprocessor.process("hello world") == "hello world"
    assert postprocessor.process("") == ""

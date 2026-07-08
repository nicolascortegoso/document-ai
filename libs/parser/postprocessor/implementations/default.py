from __future__ import annotations

from libs.parser.postprocessor.base import Postprocessor


class DefaultPostprocessor(Postprocessor):
    """No-op pass-through. Returns the input text unchanged.

    The safe default when no postprocessing steps are configured — mirrors
    DefaultProfiler/DefaultDetector's role as the always-available fallback.
    """

    def process(self, text: str) -> str:
        return text

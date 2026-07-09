from __future__ import annotations

from libs.merger.reducer.base import Reducer
from libs.merger.reducer.models import ReducerInput

_DEFAULT_MAX_CHARS_PER_TEXT = 200


class DefaultReducer(Reducer):
    """Truncates each text to max_chars_per_text characters and joins with
    a space. Produces a genuinely reduced output without requiring an LLM.
    """

    def __init__(self, max_chars_per_text: int = _DEFAULT_MAX_CHARS_PER_TEXT) -> None:
        self._max_chars = max_chars_per_text

    def reduce(self, reducer_input: ReducerInput) -> str:
        return " ".join(text[: self._max_chars] for text in reducer_input.texts)

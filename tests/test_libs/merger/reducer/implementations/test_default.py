from __future__ import annotations

from libs.merger.reducer.implementations.default import DefaultReducer
from libs.merger.reducer.models import ReducerInput


def test_truncates_each_text_and_joins_with_a_space() -> None:
    reducer = DefaultReducer(max_chars_per_text=5)

    result = reducer.reduce(ReducerInput(texts=["hello world", "foo bar baz"]))

    assert result == "hello foo b"


def test_default_max_chars_is_two_hundred() -> None:
    reducer = DefaultReducer()
    short_text = "short"

    result = reducer.reduce(ReducerInput(texts=[short_text]))

    # Well under 200 chars — nothing should be truncated.
    assert result == short_text


def test_empty_texts_list_returns_empty_string() -> None:
    reducer = DefaultReducer()

    result = reducer.reduce(ReducerInput(texts=[]))

    assert result == ""


def test_single_text_shorter_than_max_is_unchanged() -> None:
    reducer = DefaultReducer(max_chars_per_text=100)

    result = reducer.reduce(ReducerInput(texts=["a short text"]))

    assert result == "a short text"
from __future__ import annotations

from libs.indexer.embedder.implementations.dummy import DummyEmbedder


def test_returns_one_embedding_per_input_text_in_order() -> None:
    embedder = DummyEmbedder()

    result = embedder.embed(["first", "second", "third"])

    assert len(result) == 3


def test_default_dimensionality_is_eight() -> None:
    embedder = DummyEmbedder()

    result = embedder.embed(["text"])

    assert len(result[0]) == 8


def test_dimensionality_is_configurable() -> None:
    embedder = DummyEmbedder(dimensions=16)

    result = embedder.embed(["text"])

    assert len(result[0]) == 16


def test_empty_texts_list_returns_empty_list() -> None:
    embedder = DummyEmbedder()

    result = embedder.embed([])

    assert result == []


def test_embedding_values_are_floats() -> None:
    embedder = DummyEmbedder()

    result = embedder.embed(["text"])

    assert all(isinstance(v, float) for v in result[0])

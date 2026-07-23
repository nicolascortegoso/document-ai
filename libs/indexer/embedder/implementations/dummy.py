from __future__ import annotations

import random

from libs.indexer.embedder.base import Embedder

_DEFAULT_DIMENSIONS = 8


class DummyEmbedder(Embedder):
    """Produces a random vector for each input text. No real semantic
    meaning — a non-LLM-backed placeholder with no real practical
    application.
    """

    def __init__(self, dimensions: int = _DEFAULT_DIMENSIONS) -> None:
        self._dimensions = dimensions

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [[random.random() for _ in range(self._dimensions)] for _ in texts]

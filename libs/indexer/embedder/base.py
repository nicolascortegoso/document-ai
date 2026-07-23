from abc import ABC, abstractmethod


class Embedder(ABC):
    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        """Returns one embedding per input text, in the same order as texts."""

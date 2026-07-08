from abc import ABC, abstractmethod


class Postprocessor(ABC):
    @abstractmethod
    def process(self, text: str) -> str:
        """Transform the given text.

        Returns the processed string. Never raises.
        """

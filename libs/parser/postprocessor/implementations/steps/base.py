from abc import ABC, abstractmethod


class PostprocessingStep(ABC):
    """A single, focused text normalization step in an OCR postprocessing chain.

    Each step takes a string and returns a transformed string. Steps are
    designed to be composed in sequence via ChainedPostprocessor.
    """

    @abstractmethod
    def apply(self, text: str) -> str:
        """Apply this normalization step to the given text.

        Args:
            text: The input text to normalize.

        Returns:
            str: The normalized text.
        """

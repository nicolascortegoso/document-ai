from __future__ import annotations

from abc import ABC, abstractmethod

from common.models.parse import ParsedDocument


class Analyzer(ABC):
    @abstractmethod
    def analyze(self, document: ParsedDocument) -> str:
        """Extract unstructured signal from the document as a plain string.

        Never raises.
        """
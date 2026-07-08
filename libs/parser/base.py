from __future__ import annotations

from abc import ABC, abstractmethod

from common.enums import FileType
from common.models.document import PageProfile


class NoExtractionAvailableError(Exception):
    """Raised by extract() when a strategy has no real capability to
    extract anything from the given page — not "ran and found zero
    characters" (that's a legitimate "" return), but "no genuine extraction
    capability exists here at all."

    Defined here, alongside the ABC, rather than per-implementation: any
    BasePageExtractionStrategy could hit this, not just
    DefaultPageExtractionStrategy (the only one that currently does), and
    callers should be able to catch one stable type regardless of which
    strategy is behind the interface.
    """


class BasePageExtractionStrategy(ABC):
    """Abstract base for all page extraction strategies.

    Priority contract:
        get_priority() must return an integer in the range [1, 100].
        Higher values take precedence. DefaultPageExtractionStrategy always
        declares 1, making it the last resort when no higher-priority
        strategy matches.
    """

    @property
    @abstractmethod
    def supported_mime_types(self) -> list[FileType]:
        """Declares which FileType values this strategy handles.

        Used by the registry for startup conflict detection and MIME filtering.
        """

    @abstractmethod
    def can_handle(self, page_profile: PageProfile) -> bool:
        """Inspect the page profile to decide suitability.

        Called only after MIME filtering. Returns True if this strategy
        can process the given page (e.g. page has extractable text,
        is not scanned, etc.).
        """

    @abstractmethod
    def get_priority(self) -> int:
        """Returns an integer priority in the range [1, 100].

        Higher value wins when multiple strategies match. DefaultPageExtractionStrategy
        always returns 1 to ensure it is the last resort.
        """

    @abstractmethod
    def extract(self, file_bytes: bytes, page_profile: PageProfile) -> str:
        """Extract text content from the given page.

        Returns the extracted text for the page. May return an empty
        string if the page was genuinely processed but has no content
        (e.g. a whitespace-only page). Raises NoExtractionAvailableError
        if this strategy has no real capability to extract anything at
        all — see DefaultPageExtractionStrategy.
        """
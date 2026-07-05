from __future__ import annotations

from abc import ABC, abstractmethod

from common.enums import FileType
from common.models.document import DocumentProfile


class BaseDocumentProfiler(ABC):
    """Abstract base for all document profilers.

    Priority contract:
        get_priority() must return an integer in the range [1, 100].
        Higher values take precedence. DefaultProfiler always declares 1,
        making it the last resort when no higher-priority profiler matches.
    """

    @property
    @abstractmethod
    def supported_mime_types(self) -> list[FileType]:
        """Declares which FileType values this profiler handles.

        Used by the registry for startup conflict detection and MIME filtering.
        """

    @abstractmethod
    def can_handle(self, file_bytes: bytes) -> bool:
        """Deep inspection of file content.

        Called only after MIME filtering. Returns True if this profiler
        can process the given bytes (e.g. file is not encrypted, version
        is supported, internal structure is intact).
        """

    @abstractmethod
    def get_priority(self) -> int:
        """Returns an integer priority in the range [1, 100].

        Higher value wins when multiple profilers match. DefaultProfiler
        always returns 1 to ensure it is the last resort.
        """

    @abstractmethod
    def profile(self, file_bytes: bytes, mime_type: FileType) -> DocumentProfile:
        """Execute the profile and return a populated DocumentProfile.

        Receives the already-detected mime_type from the registry rather
        than re-deriving it, so DocumentProfile.mime_type is always
        accurate regardless of which profiler wins dispatch.
        """
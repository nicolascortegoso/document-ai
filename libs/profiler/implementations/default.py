from __future__ import annotations

from typing import ClassVar

from common.enums import FileType
from common.models.document import DocumentProfile
from libs.profiler.base import BaseDocumentProfiler


class DefaultProfiler(BaseDocumentProfiler):
    """Baseline profiler that matches every file type.

    Always registered explicitly by the consuming project. Declares all
    FileType values (including UNKNOWN) in supported_mime_types, always
    returns True from can_handle, and always declares priority 1 — ensuring
    it is the last resort when no higher-priority profiler matches.

    Does not require a Detector — no MIME or content detection is performed
    by the profiler itself (MIME detection already happened upstream, in
    the registry).
    """

    _SUPPORTED_MIME_TYPES: ClassVar[list[FileType]] = list(FileType)

    @property
    def supported_mime_types(self) -> list[FileType]:
        return self._SUPPORTED_MIME_TYPES

    def can_handle(self, file_bytes: bytes) -> bool:
        return True

    def get_priority(self) -> int:
        return 1

    def profile(self, file_bytes: bytes, mime_type: FileType) -> DocumentProfile:
        # mime_type is whatever the registry actually detected — never
        # hardcoded to FileType.UNKNOWN — so DocumentProfile.mime_type stays
        # accurate even when this fallback profiler is the one that runs.
        return DocumentProfile(
            mime_type=mime_type,
            page_count=0,
            pages=[],
        )
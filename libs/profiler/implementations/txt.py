from __future__ import annotations

from typing import ClassVar

from common.enums import FileType
from common.models.document import DocumentProfile, PageProfile
from libs.profiler.base import BaseDocumentProfiler


class TxtProfiler(BaseDocumentProfiler):
    """Profiles plain-text documents.

    Does not require a Detector — no MIME or content inspection beyond
    decoding is needed once the registry has already resolved the file as
    FileType.PLAIN_TEXT.
    """

    _SUPPORTED_MIME_TYPES: ClassVar[list[FileType]] = [FileType.PLAIN_TEXT]

    @property
    def supported_mime_types(self) -> list[FileType]:
        return self._SUPPORTED_MIME_TYPES

    def can_handle(self, file_bytes: bytes) -> bool:
        try:
            file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            return False
        return True

    def get_priority(self) -> int:
        return 50

    def profile(self, file_bytes: bytes, mime_type: FileType) -> DocumentProfile:
        # Plain text has no physical pagination — modeled as a single
        # synthetic page, per the "unpaginated formats" convention.
        page = PageProfile(
            page_number=1,
            has_text=True,
            has_images=False,
            has_tables=False,
        )
        return DocumentProfile(
            mime_type=mime_type,
            page_count=1,
            pages=[page],
        )
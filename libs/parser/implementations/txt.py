from __future__ import annotations

from typing import ClassVar

from common.enums import FileType
from common.models.document import PageProfile
from libs.parser.base import BasePageExtractionStrategy


class TxtPageExtractionStrategy(BasePageExtractionStrategy):
    """Extracts text for plain-text documents.

    Plain text has exactly one synthetic page (per the "unpaginated
    formats" convention) and nothing page-specific to check, so can_handle
    always returns True.
    """

    _SUPPORTED_MIME_TYPES: ClassVar[list[FileType]] = [FileType.PLAIN_TEXT]

    @property
    def supported_mime_types(self) -> list[FileType]:
        return self._SUPPORTED_MIME_TYPES

    def can_handle(self, page_profile: PageProfile) -> bool:
        return True

    def get_priority(self) -> int:
        return 50

    def extract(self, file_bytes: bytes, page_profile: PageProfile) -> str:
        return file_bytes.decode("utf-8")

from __future__ import annotations

from typing import ClassVar

from common.enums import FileType
from common.models.document import PageProfile
from libs.parser.base import BasePageExtractionStrategy, NoExtractionAvailableError


class DefaultPageExtractionStrategy(BasePageExtractionStrategy):
    """Baseline strategy that matches every file type.

    Always registered explicitly by the consuming project. Declares all
    FileType values (including UNKNOWN) in supported_mime_types, always
    returns True from can_handle, and always declares priority 1 — ensuring
    it is the last resort when no higher-priority strategy matches.

    Unlike DefaultProfiler (which returns a valid, if empty, DocumentProfile
    when nothing else matches), extract() raises rather than returning "" —
    see NoExtractionAvailableError in base.py.
    """

    _SUPPORTED_MIME_TYPES: ClassVar[list[FileType]] = list(FileType)

    @property
    def supported_mime_types(self) -> list[FileType]:
        return self._SUPPORTED_MIME_TYPES

    def can_handle(self, page_profile: PageProfile) -> bool:
        return True

    def get_priority(self) -> int:
        return 1

    def extract(self, file_bytes: bytes, page_profile: PageProfile) -> str:
        raise NoExtractionAvailableError(
            "No extraction strategy is available for this page's format. "
            "DefaultPageExtractionStrategy matched only because nothing "
            "else could handle it."
        )

from __future__ import annotations

import magic

from common.enums import FileType
from libs.profiler.detector.base import Detector


class DefaultDetector(Detector):
    """Default detector implementation.

    detect_mime: Magic-byte inspection via python-magic. Returns
        FileType.UNKNOWN for unrecognised signatures — never raises.
    """

    # Explicit mapping rather than a comprehension over FileType: python-magic's
    # MIME strings don't always map 1:1 with FileType members (e.g. a future
    # DOCX member may need to accept more than one detected MIME string), so
    # this stays a manually maintained table rather than a derived one.
    _MIME_TO_FILE_TYPE: dict[str, FileType] = {
        "text/plain": FileType.PLAIN_TEXT,
    }

    def detect_mime(self, file_bytes: bytes) -> FileType:
        try:
            mime_str = magic.from_buffer(file_bytes, mime=True)
        except Exception:
            return FileType.UNKNOWN
        return self._MIME_TO_FILE_TYPE.get(mime_str, FileType.UNKNOWN)
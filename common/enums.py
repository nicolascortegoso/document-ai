from __future__ import annotations

from enum import Enum


class FileType(str, Enum):
    PLAIN_TEXT = "text/plain"
    UNKNOWN = "unknown"
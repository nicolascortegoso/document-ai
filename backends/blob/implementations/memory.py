from __future__ import annotations

from backends.blob.base import BlobNotFoundError, BlobStore


class InMemoryBlobStore(BlobStore):
    """Dict-backed, in-process blob store.

    Not thread-safe, not persisted across restarts — for testing and local
    development only.
    """

    def __init__(self) -> None:
        self._data: dict[str, bytes] = {}

    def save(self, key: str, data: bytes) -> None:
        self._data[key] = data

    def get(self, key: str) -> bytes:
        try:
            return self._data[key]
        except KeyError:
            raise BlobNotFoundError(f"No blob stored under key {key!r}.") from None

    def delete(self, key: str) -> None:
        self._data.pop(key, None)

    def exists(self, key: str) -> bool:
        return key in self._data
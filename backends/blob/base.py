from __future__ import annotations

from abc import ABC, abstractmethod


class BlobNotFoundError(Exception):
    """Raised by get() when no value is stored under the given key.

    Defined here, alongside the ABC, rather than per-implementation: every
    BlobStore must raise this same error type for a missing key, so callers
    can catch it uniformly regardless of which implementation is behind
    the interface.
    """


class BlobStore(ABC):
    @abstractmethod
    def save(self, key: str, data: bytes) -> None:
        """Store data under key, overwriting any existing value."""

    @abstractmethod
    def get(self, key: str) -> bytes:
        """Retrieve the bytes stored under key.

        Raises BlobNotFoundError if key has no stored value.
        """

    @abstractmethod
    def delete(self, key: str) -> None:
        """Remove the value stored under key, if any.

        Idempotent — does not raise if key has no stored value.
        """

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Return whether key currently has a stored value."""
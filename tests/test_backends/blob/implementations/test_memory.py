from __future__ import annotations

import pytest

from backends.blob.base import BlobNotFoundError
from backends.blob.implementations.memory import InMemoryBlobStore


def test_save_then_get_returns_the_same_bytes() -> None:
    store = InMemoryBlobStore()

    store.save("uploads/doc-1", b"hello world")

    assert store.get("uploads/doc-1") == b"hello world"


def test_save_overwrites_an_existing_value_under_the_same_key() -> None:
    store = InMemoryBlobStore()

    store.save("uploads/doc-1", b"first version")
    store.save("uploads/doc-1", b"second version")

    assert store.get("uploads/doc-1") == b"second version"


def test_get_raises_blob_not_found_error_for_a_missing_key() -> None:
    store = InMemoryBlobStore()

    with pytest.raises(BlobNotFoundError):
        store.get("does/not/exist")


def test_delete_removes_the_value_and_subsequent_get_raises() -> None:
    store = InMemoryBlobStore()
    store.save("uploads/doc-1", b"hello world")

    store.delete("uploads/doc-1")

    with pytest.raises(BlobNotFoundError):
        store.get("uploads/doc-1")


def test_delete_on_a_missing_key_does_not_raise() -> None:
    store = InMemoryBlobStore()

    # Idempotent — deleting a key that was never saved is not an error.
    store.delete("never/saved")


def test_exists_reflects_save_and_delete() -> None:
    store = InMemoryBlobStore()

    assert store.exists("uploads/doc-1") is False

    store.save("uploads/doc-1", b"hello world")
    assert store.exists("uploads/doc-1") is True

    store.delete("uploads/doc-1")
    assert store.exists("uploads/doc-1") is False
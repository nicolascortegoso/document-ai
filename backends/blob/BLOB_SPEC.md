[← BACKENDS_SPEC](../BACKENDS_SPEC.md)

# Blob Paradigm

## Overview

Abstracts binary object storage — raw bytes, keyed by string — so calling
code never depends on a specific storage technology (e.g. S3, MinIO,
filesystem). `InMemoryBlobStore` ships as the default.

## Interface Contract

### `BlobStore` ABC

| Method | Signature | Description |
|---|---|---|
| `save` | `(key: str, data: bytes) -> None` | Store `data` under `key`, overwriting any existing value. |
| `get` | `(key: str) -> bytes` | Retrieve the bytes stored under `key`. Raises `BlobNotFoundError` if `key` has no stored value. |
| `delete` | `(key: str) -> None` | Remove the value stored under `key`, if any. Idempotent — does not raise if `key` has no stored value. |
| `exists` | `(key: str) -> bool` | Return whether `key` currently has a stored value. |

`BlobNotFoundError` is defined alongside the ABC in `base.py`, not left to
each implementation to define separately — every `BlobStore` must raise the
same error type for a missing key, so callers can catch it uniformly
regardless of which implementation is behind the interface.

## `InMemoryBlobStore`

- Dict-backed, in-process. Not thread-safe, not persisted across restarts —
  for testing and local development only.

## Folder Structure

```
backends/
└── blob/
    ├── __init__.py
    ├── base.py                # BlobStore ABC, BlobNotFoundError
    └── implementations/
        ├── __init__.py
        └── memory.py            # InMemoryBlobStore
```
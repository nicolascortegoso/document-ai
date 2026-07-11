[← BACKENDS_SPEC](../BACKENDS_SPEC.md)

# Vector Paradigm

## Overview

Abstracts vector storage and similarity search so that calling code never
depends on a specific vector database technology (e.g. Qdrant, pgvector,
FAISS). `InMemoryVectorStore` ships as the default.

Domain-agnostic — the store has no knowledge of what `id`
refers to (a `DocumentChunk`, a `SummaryNode`, a `GlossaryEntry`, or
anything else); that mapping is the caller's responsibility. Scoped to a
single collection per instance, set at construction by each concrete
implementation, not passed per method call.

## Interface Contract

### `VectorStore` ABC

| Method | Signature | Description |
|---|---|---|
| `upsert` | `(id: UUID, embedding: list[float], metadata: dict \| None = None) -> None` | Store or update a vector with its metadata. |
| `get` | `(id: UUID) -> VectorRecord` | Retrieve a stored vector by `id`. Raises `VectorNotFoundError` if `id` has no stored value. |
| `search` | `(query_vector: list[float], top_k: int, filters: dict \| None = None) -> list[SearchResult]` | Returns up to `top_k` results sorted by score descending. `filters` is implementation-specific — pass `None` to disable filtering. |
| `delete` | `(id: UUID) -> None` | Remove a vector by `id`. Idempotent — does not raise if `id` has no stored value. |
| `exists` | `(id: UUID) -> bool` | Return whether `id` currently has a stored value. |

`VectorNotFoundError` is defined alongside the ABC in `base.py`, not left to
each implementation to define separately — every `VectorStore` must raise
the same error type for a missing `id`, so callers can catch it uniformly
regardless of which implementation is behind the interface.

### `SearchResult`

Defined in `backends/vector/models.py`.

| Field | Type | Description |
|---|---|---|
| `id` | `UUID` | The matched vector's id. |
| `score` | `float` | Similarity score, higher is more similar. |
| `metadata` | `dict \| None` | The metadata stored alongside this vector, if any. |

### `VectorRecord`

Defined in `backends/vector/models.py`. Returned by `get()`, distinct from
`SearchResult` — a direct lookup has no query to score against, but does
return the `embedding` itself, which `search()` results omit.

| Field | Type | Description |
|---|---|---|
| `id` | `UUID` | The vector's id. |
| `embedding` | `list[float]` | The stored vector. |
| `metadata` | `dict \| None` | The metadata stored alongside this vector, if any. |

## `InMemoryVectorStore`

- Dict-backed, in-process. Not thread-safe, not persisted across restarts —
  for testing and local development only.
- `InMemoryVectorStore(collection_name: str)` — one instance per collection.
- Similarity metric: cosine.
- Brute-force linear scan over all stored vectors for `search()` — correct,
  not fast. Acceptable for a test double; a production implementation
  would use its underlying technology's indexing.

## Folder Structure

```
backends/
└── vector/
    ├── __init__.py
    ├── base.py                # VectorStore ABC, VectorNotFoundError
    ├── models.py               # SearchResult, VectorRecord
    └── implementations/
        ├── __init__.py
        └── memory.py            # InMemoryVectorStore
```
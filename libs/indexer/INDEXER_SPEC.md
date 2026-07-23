[← LIBS_SPEC](../LIBS_SPEC.md)

# Indexer Module

## Overview

Produces `IndexedChunk`s — `DocumentChunk`s paired with their embeddings —
from a list of `DocumentChunk`s. Designed around an ABC and a
priority-based registry. `BatchIndexer` ships as the only concrete
implementation and serves as the default last resort.

This module depends on `common/` for `DocumentChunk` and `IndexedChunk`,
per the layering rules in `LIBS_SPEC.md`.

## Interface Contract

### `BaseIndexingStrategy` (`base.py`)

| Method | Signature | Description |
|---|---|---|
| `can_handle` | `(chunks: list[DocumentChunk]) -> bool` | Inspects the chunks to decide suitability. |
| `get_priority` | `() -> int` | Integer priority in `[1, 100]`. Higher wins. `BatchIndexer` always returns `1`. |
| `index` | `(chunks: list[DocumentChunk]) -> list[IndexedChunk]` | Produces indexed chunks. Returns an empty list if `chunks` is empty. |

No `supported_mime_types` — matches `BaseChunkingStrategy`/
`BaseMergingStrategy`/`BaseDistillerStrategy`.

## Indexer Registry

An `IndexerRegistry` is instantiated by the consuming project and receives
its strategy list as a constructor argument — no injected dependency at
the registry level; strategies configure their own dependencies (e.g. an
`Embedder`) directly.

**Startup validation:** raises `IndexerPriorityConflictError` if two
strategies share the same priority, or if any strategy declares a priority
outside `[1, 100]`.

### Dispatch Flow

| Step | Responsibility |
|---|---|
| 1. `can_handle` | Every registered strategy inspects `chunks` |
| 2. Sort & dispatch | Highest-priority survivor's `index()` is called |

Raises `NoIndexingStrategyFoundError` if no strategy's `can_handle` returns
`True`.

## `BatchIndexer`

The universal fallback (`get_priority() -> 1`, `can_handle` always `True`)
— and, in this release, the only strategy. Composes an injected `Embedder`
(defaults to `DummyEmbedder`).

- Calls `embedder.embed([chunk.content for chunk in chunks])` once —
  a single batch call across every chunk.
- Pairs each `DocumentChunk` with its corresponding embedding, in order,
  into an `IndexedChunk`.

## Folder Structure

```
libs/
└── indexer/
    ├── __init__.py
    ├── base.py                           # BaseIndexingStrategy ABC
    ├── registry.py                       # IndexerRegistry, errors
    ├── embedder/
    │   ├── __init__.py
    │   ├── base.py                       # Embedder ABC
    │   ├── EMBEDDER_SPEC.md
    │   └── implementations/
    │       ├── __init__.py
    │       └── dummy.py                  # DummyEmbedder
    └── implementations/
        ├── __init__.py
        └── batch.py                       # BatchIndexer
```

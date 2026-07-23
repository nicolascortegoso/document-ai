[← INDEXER_SPEC](../INDEXER_SPEC.md)

# Embedder Module

## Overview

Provides an `Embedder` ABC for producing vector embeddings from text.
Injected into an indexing strategy at construction time.

`DummyEmbedder` ships as the only concrete implementation — produces
random vectors, no real semantic meaning.

## Interface Contract

### `Embedder` ABC

| Method | Signature | Description |
|---|---|---|
| `embed` | `(texts: list[str]) -> list[list[float]]` | Returns one embedding per input text, in the same order as `texts`. |

Batch-shaped — takes and returns lists, not a single text at a time.

## `DummyEmbedder`

Produces a random vector for each input text. Constant, configurable
dimensionality (default `8`).

## Folder Structure

See `INDEXER_SPEC.md`'s Folder Structure — `embedder/` nests under
`libs/indexer/` exactly as depicted there.

[← DISTILLER_SPEC](../DISTILLER_SPEC.md)

# Composer Module

## Overview

Provides a `BaseComposer` ABC, generic over `T` (bound to `Entry`), for
structuring an `Analyzer`'s extracted text into a list of entries — the
second of two stages a distiller strategy composes. Injected into a
distiller strategy at construction time.

`DummyComposer` ships as the only concrete implementation, producing
`list[GlossaryEntry]` — a non-LLM-backed placeholder with no real practical
application, not a production-quality composition technique. A real,
LLM-backed `Composer` is expected later.

## Interface Contract

### `BaseComposer` ABC

| Method | Signature | Description |
|---|---|---|
| `compose` | `(analyzed: str, document_id: UUID) -> list[T]` | Builds entries from an `Analyzer`'s output. Does not carry a "never raises" contract — a failure to compose entries from malformed or unusable analyzed text should surface, not be silently absorbed into an empty list. |

## `DummyComposer`

Selects the `top_n` (default `20`) most frequent words from `DummyAnalyzer`'s
output as `GlossaryEntry` objects.

## Folder Structure

See `DISTILLER_SPEC.md`'s Folder Structure — `composer/` nests under
`libs/distiller/` exactly as depicted there.

## Acceptance Criteria

- [ ] `BaseComposer` ABC defined with a single method: `compose`, generic over `T`, no "never raises" contract
- [ ] `DummyComposer` accepts `top_n` (default `20`) at construction
- [ ] `DummyComposer.compose` selects the `top_n` most frequent words from `DummyAnalyzer`'s output
- [ ] Each produced `GlossaryEntry`'s `confidence` equals its word's count divided by the total count across all words
- [ ] `DummyComposer.compose` raises on malformed input (does not silently return `[]`)
- [ ] Unit tests cover: `top_n` selection, `confidence` calculation, `pages` correctly carried through from `Analyzer`'s output, malformed input raising rather than being absorbed
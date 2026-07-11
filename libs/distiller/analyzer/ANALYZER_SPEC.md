[← DISTILLER_SPEC](../DISTILLER_SPEC.md)

# Analyzer Module

## Overview

Provides an `Analyzer` ABC for extracting unstructured signal from a parsed
document, as a plain string — the first of two stages a distiller strategy
composes (the second being a `Composer`, which structures that signal into
`Entry` objects). Injected into a distiller strategy at construction time.

`DummyAnalyzer` ships as the only concrete implementation — a
non-LLM-backed placeholder with no real practical application, not a
production-quality analysis technique. A real, LLM-backed `Analyzer` is
expected later.

## Interface Contract

### `Analyzer` ABC

| Method | Signature | Description |
|---|---|---|
| `analyze` | `(document: ParsedDocument) -> str` | Extracts signal from the document. Never raises. |

## `DummyAnalyzer`

Word-frequency counting, configurable via `min_word_length` (default `4`).

## Folder Structure

See `DISTILLER_SPEC.md`'s Folder Structure — `analyzer/` nests under
`libs/distiller/` exactly as depicted there.

## Acceptance Criteria

- [ ] `Analyzer` ABC defined with a single method: `analyze`, carrying a "never raises" contract
- [ ] `DummyAnalyzer` accepts `min_word_length` (default `4`) at construction
- [ ] `DummyAnalyzer.analyze` discards words shorter than `min_word_length`
- [ ] `DummyAnalyzer.analyze` returns valid JSON encoding, per word, its count and the pages it appeared on
- [ ] Unit tests cover: word filtering by length, per-word page tracking across multiple pages, output is valid JSON, empty document produces valid (empty) output
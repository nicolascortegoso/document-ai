[← LIBS_SPEC](../LIBS_SPEC.md)

# Chunker Module

## Overview

Produces `DocumentChunk`s from a fully profiled and parsed document. Designed
around an ABC and a priority-based registry — but with one deliberate
deviation, explained below.

`SlidingWindowChunkingStrategy` ships as the only concrete implementation in
this release, and doubles as the universal fallback (see below) — there is
no separate no-op `Default` strategy, unlike some other modules in this
project.

This module depends on `common/` for `DocumentProfile`, `ParsedDocument`,
`DocumentChunk`, and `FileType`, per the layering rules in `LIBS_SPEC.md`.

## MIME Prefilter

`BaseChunkingStrategy` has no `supported_mime_types`. `can_handle`
inspects `document_profile`/`parsed_document` content directly instead
(e.g. `PageProfile.has_tables`, an attached capability). `DocumentChunk.mime_type`
remains available if a strategy needs it, just not as a formal prefilter
stage. Priority conflicts are therefore global, not partitioned per
`FileType`.

## Interface Contract

### `BaseChunkingStrategy` (`base.py`)

| Method | Signature | Description |
|---|---|---|
| `can_handle` | `(document_profile: DocumentProfile, parsed_document: ParsedDocument) -> bool` | Inspects both to decide suitability. No MIME prefilter — see above. |
| `get_priority` | `() -> int` | Integer priority in `[1, 100]`. Higher wins. `SlidingWindowChunkingStrategy` always returns `1`. |
| `chunk` | `(document_profile: DocumentProfile, parsed_document: ParsedDocument) -> list[DocumentChunk]` | Produces chunks. Returns an empty list if the document has no content. |

## Chunker Registry

A `ChunkerRegistry` is instantiated by the consuming project and receives
its strategy list as a constructor argument — no injected dependency at the
registry level; chunking strategies configure their own dependencies (e.g.
a `Splitter`) directly.

**Startup validation:** raises `ChunkerPriorityConflictError` if two
strategies share the same priority (global, not per-`FileType` — see
above), or if any strategy declares a priority outside `[1, 100]`.

### Dispatch Flow

| Step | Responsibility |
|---|---|
| 1. `can_handle` | Every registered strategy inspects `document_profile`/`parsed_document` |
| 2. Sort & dispatch | Highest-priority survivor's `chunk()` is called |

Raises `NoChunkingStrategyFoundError` if no strategy's `can_handle` returns
`True`. Under normal operation this should never occur —
`SlidingWindowChunkingStrategy` always returns `True`, so its absence from
the registered list is what this signals.

## `SlidingWindowChunkingStrategy`

The universal fallback (`get_priority() -> 1`, `can_handle` always `True`) —
and, in this release, the *only* strategy. This is a real, working
general-purpose strategy, not a stub: chunking has no sensible "give up and
return nothing useful" behavior.

- **Window:** `200` words by default, configurable via constructor
- **Overlap:** `10%` of window size by default (`20` words for the default
  window), configurable via constructor
- **Splitter:** injected `Splitter` (defaults to `DefaultSplitter`), used to
  align each window's end to a natural text boundary rather than a raw word
  count cutoff
- **Scope:** processes each page independently — does not merge content
  across page boundaries into a single chunk. Every chunk's
  `SourceReference` therefore has `page_start == page_end`. Cross-page
  chunking is a plausible future strategy, not something this one attempts.
- Threads `document_profile.document_id` and `document_profile.mime_type`
  through to every `DocumentChunk` it produces
- Empty or whitespace-only pages produce no chunks

## Folder Structure

```
libs/
└── chunker/
    ├── __init__.py
    ├── base.py                           # BaseChunkingStrategy ABC
    ├── registry.py                       # ChunkerRegistry, errors
    ├── splitter/
    │   ├── __init__.py
    │   ├── base.py                       # Splitter ABC
    │   ├── SPLITTER_SPEC.md
    │   └── implementations/
    │       ├── __init__.py
    │       └── default.py               # DefaultSplitter
    └── implementations/
        ├── __init__.py
        └── sliding_window.py             # SlidingWindowChunkingStrategy
```

## Acceptance Criteria

- [ ] `BaseChunkingStrategy` ABC defined with no defaults: `can_handle`, `get_priority`, `chunk` all abstract — no `supported_mime_types`
- [ ] `ChunkerRegistry` accepts a strategy list; no injected dependency
- [ ] `ChunkerPriorityConflictError` raised at startup on any global priority collision, or a priority outside `[1, 100]`
- [ ] `NoChunkingStrategyFoundError` raised at runtime when no strategy's `can_handle` returns `True`
- [ ] `SlidingWindowChunkingStrategy.can_handle` always returns `True`, `get_priority` always returns `1`
- [ ] `SlidingWindowChunkingStrategy` accepts `window_size` (default `200`) and `overlap` (default `10%` of `window_size`) at construction
- [ ] `SlidingWindowChunkingStrategy` accepts an injected `Splitter`, defaulting to `DefaultSplitter`
- [ ] Chunks carry `document_profile.document_id` and `document_profile.mime_type` through
- [ ] Each chunk's `SourceReference.page_start == page_end` (single-page scope)
- [ ] Empty/whitespace-only pages produce no chunks
- [ ] Unit tests cover: registry conflict detection at startup, dispatch when multiple strategies match, `NoChunkingStrategyFoundError` when nothing matches, window/overlap behavior, splitter injection, multi-page documents
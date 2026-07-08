[← CHUNKER_SPEC](../CHUNKER_SPEC.md)

# Splitter Module

## Overview

Provides a `Splitter` ABC for finding the actual position to cut text at,
given a desired split position — aligning to a natural boundary (e.g. a
word boundary) rather than cutting mid-word. Injected into a chunking
strategy at construction time (currently only `SlidingWindowChunkingStrategy`
uses one).

`DefaultSplitter` ships as the only concrete implementation.

## Interface Contract

### `Splitter` ABC

| Method | Signature | Description |
|---|---|---|
| `find_split` | `(text: str, position: int) -> int` | Returns the actual position to cut at, adjusted from the desired `position` to a natural boundary. Result is always in `[0, len(text)]`. Never raises. |

## `DefaultSplitter`

Seeks the nearest whitespace to `position`:

1. If `position` already sits at a natural boundary (immediately before or
   after whitespace), it's returned unchanged — searching further back
   would needlessly shrink the window.
2. Otherwise, searches backward from `position` first, so chunks stay at
   or under their target size.
3. Falls back to a forward search if no whitespace exists before
   `position`.
4. Returns `position` unchanged if no whitespace exists at all nearby (e.g.
   one long unbroken token) — never raises, per the ABC contract.

## Folder Structure

See `CHUNKER_SPEC.md`'s Folder Structure — `splitter/` nests under
`libs/chunker/` exactly as depicted there.

## Acceptance Criteria

- [ ] `Splitter` ABC defined with a single method: `find_split`
- [ ] `DefaultSplitter.find_split` returns `0` for `position <= 0`
- [ ] `DefaultSplitter.find_split` returns `len(text)` for `position >= len(text)`
- [ ] `DefaultSplitter.find_split` returns `position` unchanged if it already sits at a natural boundary
- [ ] `DefaultSplitter.find_split` prefers the nearest whitespace at or before `position`
- [ ] `DefaultSplitter.find_split` falls back to the nearest whitespace after `position` if none exists before it
- [ ] `DefaultSplitter.find_split` returns `position` unchanged if no whitespace exists anywhere in `text`
- [ ] Unit tests cover all of the above cases
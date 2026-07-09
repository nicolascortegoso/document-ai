[← LIBS_SPEC](../LIBS_SPEC.md)

# Merger Module

## Overview

Aggregates `DocumentChunk`s into a `DocumentTree` of increasingly general
representations — the inverse of chunking. Designed around an ABC and a
priority-based registry.

`BottomUpMergingStrategy` ships as the only concrete implementation in this
release, and doubles as the universal fallback. There is no separate no-op
`Default` strategy; merging has no sensible "give up" behavior.

This module depends on `common/` for `DocumentChunk`, `SummaryNode`,
`DocumentTree`, per the layering rules in `LIBS_SPEC.md`.

## MIME Prefilter

`BaseMergingStrategy` has no `supported_mime_types`. `can_handle(chunks)`
inspects the chunks directly. `DocumentChunk.mime_type` remains available
if a strategy needs it, just not as a formal prefilter stage.

## Interface Contract

### `BaseMergingStrategy` (`base.py`)

| Method | Signature | Description |
|---|---|---|
| `can_handle` | `(chunks: list[DocumentChunk]) -> bool` | Inspects the chunks to decide suitability. |
| `get_priority` | `() -> int` | Integer priority in `[1, 100]`. Higher wins. `BottomUpMergingStrategy` always returns `1`. |
| `merge` | `(chunks: list[DocumentChunk]) -> DocumentTree` | Produces the full tree in one call. |

## Merger Registry

A `MergerRegistry` is instantiated by the consuming project and receives its
strategy list as a constructor argument — no injected dependency at the
registry level, mirroring `ChunkerRegistry`. Strategies configure their own
dependencies (e.g. a `Reducer`) directly.

**Startup validation:** raises `MergerPriorityConflictError` if two
strategies share the same priority (global, not per-`FileType`), or if any
strategy declares a priority outside `[1, 100]`.

### Dispatch Flow

| Step | Responsibility |
|---|---|
| 1. `can_handle` | Every registered strategy inspects `chunks` |
| 2. Sort & dispatch | Highest-priority survivor's `merge()` is called |

Raises `NoMergingStrategyFoundError` if no strategy's `can_handle` returns
`True` — signals `BottomUpMergingStrategy` was omitted from the registered
list.

## `BottomUpMergingStrategy`

The universal fallback (`get_priority() -> 1`, `can_handle` always `True`) —
and, in this release, the only strategy.

- **Grouping:** `group_size` (fixed, default `5`) or `max_depth`
  (`group_size = ceil(n_chunks ** (1 / max_depth))`, computed per document,
  clamped to a minimum of `2`) — mutually exclusive constructor arguments;
  supplying both, or `max_depth < 1`, raises `InvalidGroupingConfigurationError`.
- **Uneven final group** at a level is merged into the previous group
  rather than reduced alone — `reduce()` is never called with a
  single-item `texts` list at an intermediate level.
- **Sequential ordering:** chunks are grouped in their given order, so
  every `SummaryNode`'s `children` come out in document order by
  construction — not validated by `SummaryNode` itself (see
  `COMMON_SPEC.md`).
- **Termination:** recursion stops once a level produces exactly one node,
  which becomes `DocumentTree.root`.
- **Root** is always a `SummaryNode`, even for a single-chunk document —
  `reduce()` still runs on that one chunk, so `SummaryNode.content` is
  always reducer output, never a raw copy of chunk content.
- **Levels:** root is `0`, increasing with distance from root. Chunks
  (leaves) carry no `level` at all.
- **Reducer:** injected, defaults to `DefaultReducer`. Not level-aware —
  if a `Reducer` needs to behave differently by depth,
  `BottomUpMergingStrategy` selects what to pass in (e.g. `prompt_template`).

## Folder Structure

```
libs/
└── merger/
    ├── __init__.py
    ├── base.py                           # BaseMergingStrategy ABC
    ├── registry.py                       # MergerRegistry, errors
    ├── reducer/
    │   ├── __init__.py
    │   ├── base.py                       # Reducer ABC
    │   ├── models.py                     # ReducerInput
    │   ├── REDUCER_SPEC.md
    │   └── implementations/
    │       ├── __init__.py
    │       └── default.py               # DefaultReducer
    └── implementations/
        ├── __init__.py
        └── bottom_up.py                   # BottomUpMergingStrategy
```

## Acceptance Criteria

- [ ] `BaseMergingStrategy` ABC defined with no defaults: `can_handle`, `get_priority`, `merge` all abstract — no `supported_mime_types`
- [ ] `MergerRegistry` accepts a strategy list; no injected dependency
- [ ] `MergerPriorityConflictError` raised at startup on any global priority collision, or a priority outside `[1, 100]`
- [ ] `NoMergingStrategyFoundError` raised at runtime when no strategy's `can_handle` returns `True`
- [ ] `BottomUpMergingStrategy.can_handle` always returns `True`, `get_priority` always returns `1`
- [ ] `BottomUpMergingStrategy` accepts `group_size: int | None`, `max_depth: int | None` (mutually exclusive), and an injected `Reducer` (default `DefaultReducer`) at construction
- [ ] Supplying both `group_size` and `max_depth` raises `InvalidGroupingConfigurationError`
- [ ] Neither supplied defaults to `group_size = 5`
- [ ] `max_depth` computes `group_size = ceil(n_chunks ** (1 / max_depth))` fresh per `merge()` call, clamped to a minimum of `2`
- [ ] `max_depth < 1` raises `InvalidGroupingConfigurationError`
- [ ] A tree built with `max_depth` never exceeds that many levels
- [ ] A lonely final group of 1 at an intermediate level is merged into the previous group, never passed to `reduce()` alone
- [ ] `DocumentTree.root` is always a `SummaryNode`, even for a single-chunk document
- [ ] Root `SummaryNode.level == 0`; levels increase with distance from root
- [ ] `SummaryNode.content` is always `Reducer` output, never a raw copy of chunk content, including the single-chunk case
- [ ] Unit tests cover: registry conflict detection at startup, dispatch when multiple strategies match, `NoMergingStrategyFoundError` when nothing matches, grouping with an evenly-divisible chunk count, grouping with a leftover merged into the previous group, single-chunk-document root wrapping, level numbering across an unbalanced tree, `InvalidGroupingConfigurationError` when both `group_size` and `max_depth` are supplied, `max_depth`-derived `group_size` bounding tree height correctly across several `n_chunks`/`max_depth` combinations

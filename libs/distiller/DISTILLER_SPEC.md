[← LIBS_SPEC](../LIBS_SPEC.md)

# Distiller Module

## Overview

Produces structured `Entry` objects from a fully profiled and parsed
document. Designed around a generic ABC and a priority-based registry, both
parameterized by the specific `Entry` subtype a given strategy family
produces.

`GlossaryDistillerStrategy` ships as the only concrete implementation in
this release, producing `list[GlossaryEntry]`, and doubles as its family's
fallback — there is no separate no-op `Default` strategy; this is a real,
working strategy, not a stub.

This module depends on `common/` for `Entry` and `ParsedDocument`, per the
layering rules in `LIBS_SPEC.md`. `GlossaryEntry` itself lives here, in
`models.py` — it's one strategy family's particular choice of `T`, not
something the `BaseDistillerStrategy` ABC itself requires, the same way a
capability dataclass (`ScanProfile`) doesn't have to live in `common/`
either. Only `Entry` — the shared bound every `T` is generic over — is
genuinely universal enough to belong in `common/`.

## Output type varies by strategy family

Not every distiller strategy produces the same output type — one might
produce `GlossaryEntry`, a different one might produce an entirely
different `Entry` subtype. `BaseDistillerStrategy`, `BaseComposer`, and
`DistillerRegistry` are therefore generic over `T` (bound to `Entry`), and
a single `DistillerRegistry` instance is scoped to one `Entry` family at a
time — strategies producing a different `Entry` subtype belong in a
separate registry instance, not mixed into the same one.

## MIME Prefilter

`BaseDistillerStrategy` has no `supported_mime_types`. `can_handle(document)`
inspects the `ParsedDocument` directly.

## Interface Contract

### `BaseDistillerStrategy` (`base.py`)

Generic over `T`, bound to `Entry`.

| Method | Signature | Description |
|---|---|---|
| `can_handle` | `(document: ParsedDocument) -> bool` | Inspects the document to decide suitability. |
| `get_priority` | `() -> int` | Integer priority in `[1, 100]`. Higher wins. |
| `distill` | `(document: ParsedDocument, document_id: UUID) -> list[T]` | Produces entries for the given document. `document_id` is required, not optional — distillation presupposes the document has already been fully ingested. |

## Distiller Registry

A `DistillerRegistry`, generic over `T`, is instantiated by the consuming
project and receives its strategy list as a constructor argument — no
injected dependency at the registry level; strategies configure their own
`Analyzer`/`Composer` directly.

**Startup validation:** raises `DistillerPriorityConflictError` if two
strategies share the same priority, or if any strategy declares a priority
outside `[1, 100]`.

### Dispatch Flow

| Step | Responsibility |
|---|---|
| 1. `can_handle` | Every registered strategy inspects `document` |
| 2. Sort & dispatch | Highest-priority survivor's `distill()` is called |

Raises `NoDistillingStrategyFoundError` if no strategy's `can_handle`
returns `True`.

## `GlossaryDistillerStrategy`

Composes an injected `Analyzer` and `BaseComposer[GlossaryEntry]` (both
default to their `Dummy*` implementations — see `ANALYZER_SPEC.md` /
`COMPOSER_SPEC.md`). `distill()` calls `analyzer.analyze(document)`, then
`composer.compose(analyzed, document_id)`.

## Folder Structure

```
libs/
└── distiller/
    ├── __init__.py
    ├── base.py                           # BaseDistillerStrategy ABC
    ├── registry.py                       # DistillerRegistry, errors
    ├── models.py                          # GlossaryEntry
    ├── analyzer/
    │   ├── __init__.py
    │   ├── base.py                       # Analyzer ABC
    │   ├── ANALYZER_SPEC.md
    │   └── implementations/
    │       ├── __init__.py
    │       └── dummy.py                  # DummyAnalyzer
    ├── composer/
    │   ├── __init__.py
    │   ├── base.py                       # BaseComposer ABC
    │   ├── COMPOSER_SPEC.md
    │   └── implementations/
    │       ├── __init__.py
    │       └── dummy.py                  # DummyComposer
    └── implementations/
        ├── __init__.py
        └── glossary.py                    # GlossaryDistillerStrategy
```

## Acceptance Criteria

- [ ] `BaseDistillerStrategy` is generic over `T` (bound to `Entry`); no `supported_mime_types`
- [ ] `DistillerRegistry` is generic over `T`; accepts a strategy list, no injected dependency
- [ ] `DistillerPriorityConflictError` raised at startup on priority collision, or a priority outside `[1, 100]`
- [ ] `NoDistillingStrategyFoundError` raised at runtime when no strategy's `can_handle` returns `True`
- [ ] `GlossaryDistillerStrategy.can_handle` always returns `True`, `get_priority` always returns `1`
- [ ] `GlossaryDistillerStrategy` accepts an injected `Analyzer` and `BaseComposer[GlossaryEntry]`, both defaulting to their `Dummy*` implementations
- [ ] `GlossaryDistillerStrategy.distill` calls `analyzer.analyze` then `composer.compose`, passing `document_id` through to the latter
- [ ] Unit tests cover: registry conflict detection at startup, dispatch when multiple strategies match, `NoDistillingStrategyFoundError` when nothing matches, `GlossaryDistillerStrategy` composing `Analyzer`+`Composer` correctly
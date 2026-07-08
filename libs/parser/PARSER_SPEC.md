[← LIBS_SPEC](../LIBS_SPEC.md)

# Parser Module

## Overview

Produces extracted text for a single page, given raw document bytes, an
already-known MIME type, and that page's `PageProfile`. Designed around an
ABC and a priority-based registry, mirroring `libs/profiler/`'s pattern, so
format-specific extraction strategies can be added incrementally without
modifying the core module.

`DefaultPageExtractionStrategy` and `TxtPageExtractionStrategy` ship as the
only concrete implementations in this release. All other formats are out of
scope, for the same reasons as `PROFILER_SPEC.md`.

This module depends on `common/` for `FileType` and `PageProfile`, per the
layering rules in `LIBS_SPEC.md`.

## Interface Contract

- **Input:** `file_bytes: bytes`, `mime_type: FileType`, `page_profile: PageProfile`
- **Output:** `str` — extracted, postprocessed text for that page

Unlike `ProfilerRegistry`, this module does not detect `mime_type` itself —
it's already known from the profiling stage that runs before parsing, and is
passed in by the caller.

## Abstract Base: `BasePageExtractionStrategy`

`NoExtractionAvailableError` is defined alongside the ABC in `base.py`, not
per-implementation — any strategy could raise it, not only
`DefaultPageExtractionStrategy` (the only one that currently does), so
callers catch one stable type regardless of which strategy is behind the
interface. It signals "no real extraction capability exists here," distinct
from `extract()` legitimately returning `""` for a page that was properly
processed but genuinely has no content.

| Method/Attribute | Type | Description |
|---|---|---|
| `supported_mime_types` | `list[FileType]` | Declares which file types this strategy handles. Used for startup conflict detection and MIME filtering. |
| `can_handle` | `(page_profile: PageProfile) -> bool` | Deep inspection of the page profile. Called only after MIME filtering. |
| `get_priority` | `() -> int` | Integer priority in `[1, 100]`. Higher wins. `DefaultPageExtractionStrategy` always returns `1`. |
| `extract` | `(file_bytes: bytes, page_profile: PageProfile) -> str` | Extracts text for the page. May return `""` for a genuinely empty page. Raises `NoExtractionAvailableError` if no real extraction capability exists. |

## Parser Registry

A `ParserRegistry` is instantiated by the consuming project and receives its
strategy list and a `Postprocessor` instance directly as constructor
arguments (`Postprocessor` defaults to `DefaultPostprocessor` if none is
provided — see `postprocessor/POSTPROCESSOR_SPEC.md`).

**Startup validation:** raises `ParserPriorityConflictError` if two
strategies share the same priority for the same `FileType`, or if any
strategy declares a priority outside `[1, 100]` — mirrors `ProfilerRegistry`.

### Dispatch Flow

| Step | Responsibility |
|---|---|
| 1. Filter by MIME | Narrow candidates to strategies whose `supported_mime_types` includes the given `mime_type` |
| 2. `can_handle` | Each candidate inspects the `page_profile` |
| 3. Sort & dispatch | Highest-priority survivor's `extract()` is called |
| 4. Postprocess | The extracted text is passed through the injected `Postprocessor` before being returned |

Raises `NoStrategyFoundError` if no candidate survives steps 1–2 — signals
`DefaultPageExtractionStrategy` was omitted from the registered list.

## `DefaultPageExtractionStrategy`

Matches every `FileType` (including `UNKNOWN`), `can_handle` always `True`,
priority `1`. `extract()` raises `NoExtractionAvailableError` rather than
returning `""` — see the Abstract Base section above.

## `TxtPageExtractionStrategy`

| Attribute | Value |
|---|---|
| `supported_mime_types` | `[FileType.PLAIN_TEXT]` |
| `get_priority()` | `50` |
| `can_handle` | Always `True` — plain text has exactly one synthetic page with nothing page-specific to check |
| `extract` | Decodes `file_bytes` as UTF-8 and returns it directly |

## Folder Structure

```
libs/
└── parser/
    ├── __init__.py
    ├── base.py                           # BasePageExtractionStrategy ABC
    ├── registry.py                       # ParserRegistry, errors
    ├── postprocessor/
    │   ├── __init__.py
    │   ├── base.py                       # Postprocessor ABC
    │   ├── POSTPROCESSOR_SPEC.md
    │   └── implementations/
    │       ├── __init__.py
    │       ├── default.py               # DefaultPostprocessor
    │       ├── chained.py                # ChainedPostprocessor
    │       └── steps/
    │           ├── __init__.py
    │           └── base.py               # PostprocessingStep ABC
    └── implementations/
        ├── __init__.py
        ├── default.py                    # DefaultPageExtractionStrategy
        └── txt.py                        # TxtPageExtractionStrategy
```

## Acceptance Criteria

- [ ] `BasePageExtractionStrategy` ABC defined with no defaults: `supported_mime_types`, `can_handle`, `get_priority`, `extract` all abstract
- [ ] `ParserRegistry` accepts a strategy list and a `Postprocessor` as constructor arguments
- [ ] `ParserPriorityConflictError` raised at startup on priority collision for the same `FileType`, or a priority outside `[1, 100]`
- [ ] `NoStrategyFoundError` raised at runtime when no strategy survives MIME filtering + `can_handle`
- [ ] `ParserRegistry.parse_page` accepts `mime_type` as a parameter — does not detect it itself
- [ ] Extracted text is passed through the injected `Postprocessor` before being returned
- [ ] `NoExtractionAvailableError` defined in `base.py`, not in `implementations/default.py` — importable independent of which strategy raises it
- [ ] `DefaultPageExtractionStrategy` covers every `FileType`, `can_handle` always `True`, priority `1`, `extract` raises `NoExtractionAvailableError`
- [ ] `TxtPageExtractionStrategy` covers `[FileType.PLAIN_TEXT]`, priority `50`, `extract` decodes UTF-8 directly
- [ ] Unit tests cover: registry conflict detection at startup, priority resolution, `can_handle` dispatch, `DefaultPageExtractionStrategy` as last resort, `NoStrategyFoundError` when omitted, postprocessor applied to extracted text, `TxtPageExtractionStrategy` extraction

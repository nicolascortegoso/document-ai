[← LIBS_SPEC](../LIBS_SPEC.md)

# Profiler Module

## Overview

Produces a structured `DocumentProfile` from raw document bytes. Designed around an ABC
and a priority-based registry so that format-specific profilers can be added incrementally
without modifying the core module.

`DefaultProfiler` and `TxtProfiler` ship as the only concrete implementations in this
release. All other formats (PDF, scanned documents, spreadsheets, DOCX) are explicitly
out of scope.

This module depends on `common/` for `FileType`, `PageProfile`, and `DocumentProfile`,
per the layering rules in `LIBS_SPEC.md`.

---

## Interface Contract

- **Input:** `bytes` — raw file content
- **Output:** `DocumentProfile` — dataclass carrying document-level and page-level structural metadata

---

## Detection

MIME-type detection is delegated to an injected `Detector` instance, defaulting to
`DefaultDetector` when none is provided.

See [DETECTOR_SPEC.md](detector/DETECTOR_SPEC.md) for the full interface contract.

---

## Abstract Base: `BaseDocumentProfiler`

All profiler implementations must extend this ABC. No defaults are provided — every subclass
must explicitly declare all of the following:

| Method/Attribute | Type | Description |
|---|---|---|
| `supported_mime_types` | `ClassVar[list[FileType]]` | Declares which file types this profiler handles. Used for startup conflict detection and MIME filtering |
| `can_handle` | `(file_bytes: bytes) -> bool` | Deep inspection of file content (encoding validity, internal structure, etc.). Called only after MIME filtering |
| `get_priority` | `() -> int` | Returns an integer priority between 1 and 100 (higher = higher priority). `DefaultProfiler` always declares `1` |
| `profile` | `(file_bytes: bytes, mime_type: FileType) -> DocumentProfile` | Executes the profile and returns a populated `DocumentProfile`. Receives the already-detected `mime_type` from the registry rather than re-deriving it, so `DocumentProfile.mime_type` is always accurate regardless of which profiler wins dispatch |

---

## Profiler Registry

A `ProfilerRegistry` is instantiated by the consuming project and receives its profiler
list and a `Detector` instance directly as constructor arguments.

**At startup**, the registry validates that no two registered profilers share the same
`get_priority()` for the same `FileType` — raises `ProfilerPriorityConflictError`, failing
fast before any document is processed.

### Dispatch Flow

| Step | Responsibility |
|---|---|
| 1. Detect MIME | Registry calls `detector.detect_mime(file_bytes)`, returns a `FileType` |
| 2. Filter by MIME | Registry narrows candidates to profilers whose `supported_mime_types` includes the detected `FileType` |
| 3. `can_handle` | Each candidate performs deep inspection of `file_bytes` |
| 4. Sort & dispatch | Registry sorts surviving candidates by `get_priority()` descending, dispatches to the winner, passing the detected `mime_type` through to `winner.profile(file_bytes, mime_type)` |

Raises `NoProfilerFoundError` if no candidate survives steps 2–3. Under normal operation
this should never occur — it indicates a misconfiguration where `DefaultProfiler` was
omitted from the registered profiler list.

---

## `DefaultProfiler`

Must be explicitly registered by the consuming project like any other profiler. Declares
all `FileType` values including `FileType.UNKNOWN` in `supported_mime_types`, always
returns `True` from `can_handle`, and always declares priority `1` — ensuring it is always
the last resort when no higher-priority profiler matches.

Returns:

```python
DocumentProfile(
    mime_type=mime_type,   # the FileType detected by the registry, passed through as-is
    page_count=0,
    pages=[],
)
```

`mime_type` is the value the registry detected and passed in — **not** hardcoded to
`FileType.UNKNOWN`. `DefaultProfiler` matches every type precisely because it's the
fallback for types no other profiler claims; it must still report the file's real detected
type rather than overwriting it, since callers rely on `DocumentProfile.mime_type` being
accurate even when profiling itself was a no-op.

Does not require a `Detector` — no MIME or content detection is performed by the profiler
itself (MIME detection already happened upstream, in the registry).

---

## `TxtProfiler`

Profiles plain-text documents. Does not require a `Detector` — no MIME or content
inspection beyond decoding is needed once the registry has already resolved the file as
`FileType.PLAIN_TEXT`.

| Attribute | Value |
|---|---|
| `supported_mime_types` | `[FileType.PLAIN_TEXT]` |
| `get_priority()` | `50` |
| `can_handle` | Returns `True` if `file_bytes` decodes as valid UTF-8 text, `False` otherwise |

Per-page profiling:

Plain text has no physical pagination. The entire file is modeled as a single synthetic
page, per the "unpaginated formats" convention documented in
[COMMON_SPEC.md](../../common/COMMON_SPEC.md).

| Field | Logic |
|---|---|
| `page_number` | Always `1` |
| `has_text` | Always `True` |
| `has_images` | Always `False` |
| `has_tables` | Always `False` |
| `languages` | Left at default (`[]`) |
| capabilities | None attached — plain text has no scan, layout, or tabular structure to describe |

---

## Folder Structure

```
libs/
└── profiler/
    ├── __init__.py
    ├── base.py                           # BaseDocumentProfiler ABC
    ├── registry.py                       # ProfilerRegistry, errors
    ├── detector/
    │   ├── __init__.py
    │   ├── base.py                       # Detector ABC (detect_mime only)
    │   └── implementations/
    │       ├── __init__.py
    │       └── default.py               # DefaultDetector
    └── implementations/
        ├── __init__.py
        ├── default.py                    # DefaultProfiler
        └── txt.py                        # TxtProfiler
tests/
└── test_libs/
    └── profiler/
        ├── test_registry.py
        ├── detector/
        │   └── implementations/
        │       └── test_default.py
        └── implementations/
            ├── test_default.py
            └── test_txt.py
```

---

## Implementation Order

1. `Detector` ABC + `DefaultDetector`
2. `BaseDocumentProfiler` ABC
3. `ProfilerRegistry` + errors
4. `DefaultProfiler`
5. `TxtProfiler`
6. Tests at each stage

---

## Acceptance Criteria

Detector and `DefaultDetector` acceptance criteria are covered in `DETECTOR_SPEC.md`; the
items below are specific to this module.

- [ ] `BaseDocumentProfiler` ABC defined with no defaults: `supported_mime_types`, `can_handle`, `get_priority`, `profile` all abstract
- [ ] `profile` signature is `(file_bytes: bytes, mime_type: FileType) -> DocumentProfile` — accepts the registry-detected `mime_type`, does not re-derive it
- [ ] `get_priority` contract documented: valid range is 1–100, higher value wins
- [ ] `ProfilerRegistry` accepts profiler list and `Detector` as constructor arguments
- [ ] `ProfilerRegistry` calls `detector.detect_mime` for MIME detection and passes the result into `winner.profile(file_bytes, mime_type)`
- [ ] `ProfilerPriorityConflictError` raised at startup on priority collision for the same `FileType`
- [ ] `NoProfilerFoundError` raised at runtime when no profiler survives MIME filtering + `can_handle`; documented as a misconfiguration signal
- [ ] `DefaultProfiler` declared with `supported_mime_types` covering all `FileType` values including `UNKNOWN`, `can_handle` always returns `True`, `get_priority` always returns `1`
- [ ] `DefaultProfiler` returns `DocumentProfile(mime_type=mime_type, page_count=0, pages=[])` using the `mime_type` passed into `profile`, **not** a hardcoded `FileType.UNKNOWN`
- [ ] `DefaultProfiler` does not require a `Detector`
- [ ] `DefaultProfiler` registered explicitly by the consuming project — no auto-registration logic in the registry
- [ ] `TxtProfiler` declared with `supported_mime_types = [FileType.PLAIN_TEXT]`, `get_priority` returns `50`
- [ ] `TxtProfiler.can_handle` returns `False` for bytes that fail UTF-8 decoding
- [ ] `TxtProfiler.profile` returns a single-page `DocumentProfile` with `has_text=True`, `has_images=False`, `has_tables=False`, `languages=[]`, no capabilities attached
- [ ] `TxtProfiler` does not require a `Detector`
- [ ] Unit tests cover: registry conflict detection at startup, priority resolution, `can_handle` dispatch, `DefaultProfiler` as last resort, `DefaultProfiler` reporting the correct passed-through `mime_type`, `NoProfilerFoundError` when `DefaultProfiler` is omitted, `TxtProfiler` single-page profiling, `TxtProfiler.can_handle` rejecting invalid UTF-8
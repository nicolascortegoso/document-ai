[← PROFILER_SPEC](../PROFILER_SPEC.md)

# Detector Module

## Overview

Provides a `Detector` ABC for MIME-type detection, consumed by `libs/profiler/`.

`DefaultDetector` ships as the only concrete implementation.

---

## Interface Contract

### `Detector` ABC

Defined in `libs/profiler/detector/base.py`.

| Method | Signature | Description |
|---|---|---|
| `detect_mime` | `(file_bytes: bytes) -> FileType` | Returns a `FileType` resolved from magic bytes. Returns `FileType.UNKNOWN` for unrecognised signatures. Never raises. |

---

## `DefaultDetector`

Defined in `libs/profiler/detector/implementations/default.py`.

- `detect_mime` — uses `python-magic` to resolve MIME type from magic bytes; returns
  `FileType.UNKNOWN` on any unrecognised signature or internal error, never raises

---

## Notes

Folder layout is shown in full in `PROFILER_SPEC.md`'s Folder Structure —
`detector/` nests under `libs/profiler/` exactly as depicted there. The one
addition specific to this module is the `python-magic` dependency used by
`DefaultDetector`.

---

## Acceptance Criteria

- [ ] `Detector` ABC defined with a single method: `detect_mime`
- [ ] `detect_mime` returns a `FileType`, never raises
- [ ] `DefaultDetector.detect_mime` uses `python-magic`
- [ ] `DefaultDetector.detect_mime` returns `FileType.UNKNOWN` for unrecognised signatures and never raises, including on internal `python-magic` errors
- [ ] Unit tests cover: `detect_mime` returns the correct `FileType` for a known plain-text file, `detect_mime` returns `FileType.UNKNOWN` for an unrecognised/malformed input, `detect_mime` never raises
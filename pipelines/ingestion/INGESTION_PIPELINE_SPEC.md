[← PIPELINES_SPEC](../PIPELINES_SPEC.md)

# Ingestion Pipeline

## Overview

Orchestrates document ingestion. This release implements **profiling and
parsing**. `register`, `update`, `delete`, `chunk`, `merge`, and `index` are
explicitly out of scope, since they depend on `backends/blob/`,
`backends/record/`, `libs/chunker/`, `libs/merger/`, and `libs/indexer/`,
none of which are wired into this pipeline yet. Adding a stage later means
adding one method to `BaseIngestionPipeline` and one job in `tasks/` — not a
redesign of what's here.

## Interface Contract

### `BaseIngestionPipeline` (`base.py`)

| Method | Signature | Description |
|---|---|---|
| `profile` | `(file_bytes: bytes) -> DocumentProfile` | Produce a `DocumentProfile` for the given raw document bytes. |
| `parse` | `(file_bytes: bytes, document_profile: DocumentProfile) -> ParsedDocument` | Extract text for every page in `document_profile`, given the same raw bytes profiling was run on. |

Pure ABC — no concrete logic, consistent with `base.py`'s meaning everywhere
else in the project.

### `IngestionPipeline` (`implementations/ingestion.py`)

The one concrete implementation. Composes `libs/profiler/`'s
`ProfilerRegistry` and `libs/parser/`'s `ParserRegistry`, both required at
construction:

```python
IngestionPipeline(profiler_registry: ProfilerRegistry, parser_registry: ParserRegistry)
```

- `profile(file_bytes)` delegates directly to `profiler_registry.profile(file_bytes)`.
- `parse(file_bytes, document_profile)` iterates `document_profile.pages`,
  calling `parser_registry.parse_page(file_bytes, document_profile.mime_type, page_profile)`
  for each, and collects the results into a `ParsedDocument`.

Both registries are required, not optional — a partially-constructed
pipeline that can only profile (and raises confusingly if `parse()` is
called) is worse than requiring both dependencies upfront.

## Models

`ParsedPage`/`ParsedDocument` live in `common/models/parsed.py`, not here —
see `COMMON_SPEC.md`. They're document content (text extracted per page),
the same category as `PageProfile`/`DocumentProfile`, so they follow those
models to `common/` rather than staying pipeline-local. This also avoids a
real layering risk: a future `libs/chunker/` consuming parsed text could
never import from `pipelines/ingestion/` (per `LIBS_SPEC.md`'s rules), so
keeping them in `common/` now avoids having to move them under pressure
later.

## Jobs (`tasks/`)

Both are plain, framework-free callables, per `PIPELINES_SPEC.md`'s `tasks/`
convention — dispatched by `services/` via an injected `Queue`
(`backends/queue/`), never called directly by pipeline code. Each exposes a
factory, not a bare function, since the job needs an already-constructed
`BaseIngestionPipeline` (dependency injection happens where the job
registry is built, not inside the job itself).

### `profile_document` (`tasks/profile.py`)

```python
make_profile_document_job(pipeline: BaseIngestionPipeline) -> Callable[[bytes], dict[str, Any]]
```

Calls `pipeline.profile(file_bytes)`, returns `result.to_dict()`.

### `parse_document` (`tasks/parse.py`)

```python
make_parse_document_job(pipeline: BaseIngestionPipeline) -> Callable[[bytes, dict[str, Any]], dict[str, Any]]
```

Takes the `DocumentProfile` as a plain dict, not the dataclass — job
arguments must stay serializable across any `Queue` implementation, not
just `DummyQueue`'s in-process one. Reconstructs it via `DocumentProfile.from_dict()`
internally, calls `pipeline.parse(file_bytes, profile)`, returns
`result.to_dict()`.

Both jobs' results are plain dicts, never the raw dataclasses, for the same
serialization reason.

## Folder Structure

```
pipelines/
└── ingestion/
    ├── __init__.py
    ├── base.py                     # BaseIngestionPipeline ABC
    ├── implementations/
    │   ├── __init__.py
    │   └── ingestion.py              # IngestionPipeline (concrete)
    └── tasks/
        ├── __init__.py
        ├── profile.py                # make_profile_document_job
        └── parse.py                   # make_parse_document_job
tests/
└── test_pipelines/
    └── ingestion/
        ├── implementations/
        │   └── test_ingestion.py
        └── tasks/
            ├── test_profile.py
            └── test_parse.py
```

No `serializers.py` in this release — `to_dict()`/`from_dict()` on the
dataclasses themselves are sufficient.

## Deferred

`register`, `update`, `delete`, `chunk`, `merge`, `index`, and any resumable
status-tracking model — each depends on a `backends/` or `libs/` module not
yet wired into this pipeline.

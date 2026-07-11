[← PIPELINES_SPEC](../PIPELINES_SPEC.md)

# Distillation Pipeline

## Overview

Extracts structured entries from a parsed document. Split out from
`pipelines/ingestion/` into its own pipeline for the same reason
`pipelines/summarization/` was: distillation has a different computational
profile once its `Analyzer`/`Composer` are LLM-backed — a different
retry/timeout policy, worker concurrency, and scaling needs than the fast,
local `profile`/`parse`/`chunk` stages. Per `PIPELINES_SPEC.md`'s Rules,
this pipeline never imports from `pipelines/ingestion/` — it receives a
parsed document as plain data, produced by dispatching `parse_document` and
feeding its result into this pipeline's own job.

Generic over `T` (bound to `Entry`), mirroring `libs/distiller/` — a given
pipeline instance is scoped to one `Entry` family, the same way a
`DistillerRegistry` instance is.

## Interface Contract

### `BaseDistillationPipeline[T]` (`base.py`)

| Method | Signature | Description |
|---|---|---|
| `distill` | `(document: ParsedDocument, document_id: UUID) -> list[T]` | Produce entries from the given document. |

Pure ABC — no concrete logic, consistent with `base.py`'s meaning everywhere
else in the project.

### `DistillationPipeline[T]` (`implementations/distillation.py`)

The one concrete implementation. Composes `libs/distiller/`'s
`DistillerRegistry[T]`, required at construction:

```python
DistillationPipeline(distiller_registry: DistillerRegistry[T])
```

`distill(document, document_id)` delegates directly to
`distiller_registry.distill_document(document, document_id)`.

## Job: `distill_document` (`tasks/distill.py`)

A plain, framework-free callable, per `PIPELINES_SPEC.md`'s `tasks/`
convention — dispatched by `services/` via an injected `Queue`
(`backends/queue/`), never called directly by pipeline code.

```python
make_distill_document_job(pipeline: BaseDistillationPipeline) -> Callable[[dict[str, Any], str], list[dict[str, Any]]]
```

Takes the parsed document as a plain `dict`, not a `ParsedDocument`
dataclass, and `document_id` as a plain `str`, not a `UUID` — job arguments
must stay serializable across any `Queue` implementation. Reconstructs both
(`ParsedDocument.from_dict()`, `UUID(document_id)`), calls
`pipeline.distill(document, document_id)`, returns
`[entry.to_dict() for entry in entries]`.

## Folder Structure

```
pipelines/
└── distillation/
    ├── __init__.py
    ├── base.py                     # BaseDistillationPipeline[T] ABC
    ├── implementations/
    │   ├── __init__.py
    │   └── distillation.py           # DistillationPipeline[T] (concrete)
    └── tasks/
        ├── __init__.py
        └── distill.py                 # make_distill_document_job
tests/
└── test_pipelines/
    └── distillation/
        ├── implementations/
        │   └── test_distillation.py
        └── tasks/
            └── test_distill.py
```

No `serializers.py` in this release — `to_dict()`/`from_dict()` on the
dataclasses themselves are sufficient. No `models.py` — this pipeline
introduces no new types of its own.

## Acceptance Criteria

- [ ] `BaseDistillationPipeline` is `Generic[T]`, `T` bound to `Entry`
- [ ] `DistillationPipeline` requires a `DistillerRegistry[T]` at construction
- [ ] `DistillationPipeline.distill` delegates directly to `distiller_registry.distill_document`
- [ ] `distill_document` job takes the document as `dict` and `document_id` as `str`, not `ParsedDocument`/`UUID`
- [ ] `distill_document` job returns `list[dict]`, not a list of `Entry` objects
- [ ] No import from `pipelines/ingestion/` anywhere in `pipelines/distillation/` itself — a test demonstrating the two pipelines chained via `Queue` dispatch is not a violation of this; only the package's own implementation code is constrained
- [ ] Unit tests cover: `DistillationPipeline` delegation, the job's serialization contract, dispatch through a `Queue`, chaining `parse_document`'s output into `distill_document`'s input

[← PIPELINES_SPEC](../PIPELINES_SPEC.md)

# Summarization Pipeline

## Overview

Aggregates chunks into a `DocumentTree` of increasingly general summaries.
Split out from `pipelines/ingestion/` into its own pipeline because merging
has a fundamentally different computational profile once its `Reducer` is
LLM-backed — a different retry/timeout policy, worker concurrency, and
scaling needs than the fast, local `profile`/`parse`/`chunk` stages. Per
`PIPELINES_SPEC.md`'s Rules, this pipeline never imports from
`pipelines/ingestion/` — it receives chunks as plain data, produced by
dispatching `chunk_document` and feeding its result into this pipeline's
own job.

## Interface Contract

### `BaseSummarizationPipeline` (`base.py`)

| Method | Signature | Description |
|---|---|---|
| `summarize` | `(chunks: list[DocumentChunk]) -> DocumentTree` | Produce a `DocumentTree` from the given chunks. |

Pure ABC — no concrete logic, consistent with `base.py`'s meaning everywhere
else in the project.

### `SummarizationPipeline` (`implementations/summarization.py`)

The one concrete implementation. Composes `libs/merger/`'s `MergerRegistry`,
required at construction:

```python
SummarizationPipeline(merger_registry: MergerRegistry)
```

`summarize(chunks)` delegates directly to
`merger_registry.merge_chunks(chunks)`.

## Job: `summarize_chunks` (`tasks/summarize.py`)

A plain, framework-free callable, per `PIPELINES_SPEC.md`'s `tasks/`
convention — dispatched by `services/` via an injected `Queue`
(`backends/queue/`), never called directly by pipeline code.

```python
make_summarize_chunks_job(pipeline: BaseSummarizationPipeline) -> Callable[[list[dict[str, Any]]], dict[str, Any]]
```

Takes chunks as a plain `list[dict]`, not `DocumentChunk` dataclasses —
job arguments must stay serializable across any `Queue` implementation.
Reconstructs each via `DocumentChunk.from_dict()`, calls
`pipeline.summarize(chunks)`, returns `tree.to_dict()`. Needs no
`mime_type` or `document_id` parameter — both already travel on each
`DocumentChunk`.

## Folder Structure

```
pipelines/
└── summarization/
    ├── __init__.py
    ├── base.py                     # BaseSummarizationPipeline ABC
    ├── implementations/
    │   ├── __init__.py
    │   └── summarization.py          # SummarizationPipeline (concrete)
    └── tasks/
        ├── __init__.py
        └── summarize.py               # make_summarize_chunks_job
tests/
└── test_pipelines/
    └── summarization/
        ├── implementations/
        │   └── test_summarization.py
        └── tasks/
            └── test_summarize.py
```

No `serializers.py` in this release — `to_dict()`/`from_dict()` on the
dataclasses themselves are sufficient.

## Acceptance Criteria

- [ ] `BaseSummarizationPipeline` ABC defined with a single abstract method: `summarize`
- [ ] `SummarizationPipeline` requires a `MergerRegistry` at construction
- [ ] `SummarizationPipeline.summarize` delegates directly to `merger_registry.merge_chunks`
- [ ] `summarize_chunks` job takes `list[dict]`, not `DocumentChunk` objects
- [ ] `summarize_chunks` job returns a plain `dict`, not a `DocumentTree`
- [ ] `summarize_chunks` job needs no `file_bytes`, `mime_type`, or `document_id` parameter
- [ ] No import from `pipelines/ingestion/` anywhere in `pipelines/summarization/` itself — a test demonstrating the two pipelines chained via `Queue` dispatch is not a violation of this; only the package's own implementation code is constrained
- [ ] Unit tests cover: `SummarizationPipeline` delegation, the job's serialization contract, dispatch through a `Queue`, chaining `chunk_document`'s output into `summarize_chunks`'s input

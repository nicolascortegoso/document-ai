[← PIPELINES_SPEC](../PIPELINES_SPEC.md)

# Ingestion Pipeline

## Overview

Orchestrates document ingestion. This release implements **profiling,
parsing, chunking, indexing, and storing** — the full automatic chain,
ending at vector storage. `register`, `update`, and `delete` are explicitly
out of scope, since they depend on `backends/record/` not being wired into
this pipeline yet. `merge`/`distill` are never part of this pipeline at
all — summarization and distillation are separate, manually-triggered
pipelines (`pipelines/summarization/`, `pipelines/distillation/`), not
automatic continuations of ingestion.

## Interface Contract

### `BaseIngestionPipeline` (`base.py`)

| Method | Signature | Description |
|---|---|---|
| `profile` | `(file_bytes: bytes) -> DocumentProfile` | Produce a `DocumentProfile` for the given raw document bytes. |
| `parse` | `(file_bytes: bytes, document_profile: DocumentProfile) -> ParsedDocument` | Extract text for every page in `document_profile`, given the same raw bytes profiling was run on. |
| `chunk` | `(document_profile: DocumentProfile, parsed_document: ParsedDocument) -> list[DocumentChunk]` | Produce chunks from `parsed_document`. Needs no raw bytes — chunking operates entirely on already-profiled, already-parsed content. |
| `index` | `(chunks: list[DocumentChunk]) -> list[IndexedChunk]` | Produce embeddings for chunks. Does not store the result — storing into a vector store is the caller's responsibility. |

Pure ABC — no concrete logic, consistent with `base.py`'s meaning everywhere
else in the project.

### `IngestionPipeline` (`implementations/ingestion.py`)

The one concrete implementation. Composes `libs/profiler/`'s
`ProfilerRegistry`, `libs/parser/`'s `ParserRegistry`, `libs/chunker/`'s
`ChunkerRegistry`, and `libs/indexer/`'s `IndexerRegistry`, all required at
construction:

```python
IngestionPipeline(
    profiler_registry: ProfilerRegistry,
    parser_registry: ParserRegistry,
    chunker_registry: ChunkerRegistry,
    indexer_registry: IndexerRegistry,
)
```

- `profile(file_bytes)` delegates directly to `profiler_registry.profile(file_bytes)`.
- `parse(file_bytes, document_profile)` iterates `document_profile.pages`,
  calling `parser_registry.parse_page(file_bytes, document_profile.mime_type, page_profile)`
  for each, and collects the results into a `ParsedDocument`.
- `chunk(document_profile, parsed_document)` delegates directly to
  `chunker_registry.chunk_document(document_profile, parsed_document)`.
- `index(chunks)` delegates directly to `indexer_registry.index_chunks(chunks)`.
  No `VectorStore` dependency on the pipeline itself — storing lives at
  the job level (`tasks/embed_and_store.py`), keeping `IngestionPipeline`'s
  own dependencies limited to `libs/` registries.

All four registries are required, not optional — a partially-constructed
pipeline that raises confusingly if one method is called is worse than
requiring every dependency upfront.

## Models

`ParsedPage`/`ParsedDocument`/`SourceReference`/`DocumentChunk`/`IndexedChunk`
all live in `common/models/`, not here — see `COMMON_SPEC.md`. They're
document content, the same category as `PageProfile`/`DocumentProfile`, so
they follow those models to `common/` rather than staying pipeline-local.
This also avoids a real layering risk: `libs/chunker/`/`libs/indexer/`
consuming or producing these types could never import from
`pipelines/ingestion/` (per `LIBS_SPEC.md`'s rules), so keeping them in
`common/` avoids ever having to move them under pressure later.

## Jobs (`tasks/`)

All four are plain, framework-free callables, per `PIPELINES_SPEC.md`'s
`tasks/` convention — dispatched by `services/` via an injected `Queue`
(`backends/queue/`), never called directly by pipeline code. Each exposes a
factory, not a bare function, since the job needs an already-constructed
`BaseIngestionPipeline` (dependency injection happens where the job
registry is built, not inside the job itself). Every job's result is a
plain dict (or list of dicts), never the raw dataclass, since job arguments
and results must stay serializable across any `Queue` implementation, not
just `DummyQueue`'s in-process one.

### `profile_document` (`tasks/profile.py`)

```python
make_profile_document_job(pipeline: BaseIngestionPipeline) -> Callable[[bytes], dict[str, Any]]
```

Calls `pipeline.profile(file_bytes)`, returns `result.to_dict()`.

### `parse_document` (`tasks/parse.py`)

```python
make_parse_document_job(pipeline: BaseIngestionPipeline) -> Callable[[bytes, dict[str, Any]], dict[str, Any]]
```

Takes the `DocumentProfile` as a plain dict, reconstructs it via
`DocumentProfile.from_dict()`, calls `pipeline.parse(file_bytes, profile)`,
returns `result.to_dict()`.

### `chunk_document` (`tasks/chunk.py`)

```python
make_chunk_document_job(pipeline: BaseIngestionPipeline) -> Callable[[dict[str, Any], dict[str, Any]], list[dict[str, Any]]]
```

Takes both `DocumentProfile` and `ParsedDocument` as plain dicts,
reconstructs both, calls `pipeline.chunk(profile, parsed)`, returns
`[c.to_dict() for c in chunks]`. Unlike the other three jobs, takes no
`file_bytes` — chunking never needs the raw document.

### `index_chunks` (`tasks/index_chunks.py`)

```python
make_index_chunks_job(pipeline: BaseIngestionPipeline) -> Callable[[list[dict[str, Any]]], list[dict[str, Any]]]
```

Takes chunks as a plain list of dicts, reconstructs them, calls
`pipeline.index(chunks)`, returns `[c.to_dict() for c in indexed_chunks]`.
Depends only on the pipeline — matching `profile_document`/
`parse_document`/`chunk_document`'s shape exactly, no `backends/`
dependency here.

### `store_chunks` (`tasks/store_chunks.py`)

```python
make_store_chunks_job(vector_store: VectorStore) -> Callable[[list[dict[str, Any]]], list[str]]
```

Takes `IndexedChunk`s as a plain list of dicts, reconstructs them, calls
`vector_store.upsert(...)` for each — `id`/`embedding` directly,
`document_id`/`mime_type` as metadata. Returns the stored ids, not the
full `IndexedChunk`s — the caller already has the embeddings it passed in,
so echoing them back would be pure waste. Depends only on `vector_store` —
no pipeline at all, since storing is purely a `backends/` operation with
no `libs/` orchestration involved.

`index_chunks` and `store_chunks` are two separate jobs, not one combined
job — embedding (potentially slow/costly, once `Embedder` is backed by a
real model) and storing (a fast, separate write) have different retry
profiles. A failed store shouldn't force recomputing every embedding just
to retry the write.

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
        ├── parse.py                   # make_parse_document_job
        ├── chunk.py                    # make_chunk_document_job
        ├── index_chunks.py              # make_index_chunks_job
        └── store_chunks.py               # make_store_chunks_job
tests/
└── test_pipelines/
    └── ingestion/
        ├── implementations/
        │   └── test_ingestion.py
        └── tasks/
            ├── test_profile.py
            ├── test_parse.py
            ├── test_chunk.py
            ├── test_index_chunks.py
            └── test_store_chunks.py
```

No `serializers.py` in this release — `to_dict()`/`from_dict()` on the
dataclasses themselves are sufficient.

## Deferred

`register`, `update`, `delete`, and any resumable status-tracking model —
each depends on `backends/record/` not being wired into this pipeline yet.

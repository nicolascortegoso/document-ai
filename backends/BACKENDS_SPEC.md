[← README](../README.md)

# backends/ — External Systems Abstraction Layer

## Principles

`backends/` contains abstractions for external systems the application depends
on — storage, task queues, LLM inference, embeddings, observability, and
similarly-shaped integrations, with room for more paradigms as they come up.
Every module defines an ABC for a specific paradigm and ships a default
test-double implementation for testing and local development. Concrete
production implementations live in the
[infrastructure layer](../infrastructure/INFRASTRUCTURE_SPEC.md).

## Rules

- No imports from `pipelines/`
- May import domain models from `common/` — they are passed in by the consuming layer
- Every module ships a default test-double implementation, not for production use:
  - **`InMemory*`** for storage paradigms (e.g. `InMemoryDocumentStore`)
  - **`Dummy*`** for everything else (e.g. `DummyLLMClient`, `DummyEmbedder`,
    `DummyObservabilityClient`)
  - Neither is thread-safe; both exist for testing and local development only
- Concrete production implementations belong in the infrastructure layer

## Pattern

Every module follows the same structure:

```
backends/<paradigm>/
    base.py              # ABC
    models.py            # Backend-specific models (where needed)
    implementations/
        memory.py        # InMemory implementation (storage paradigms)
        dummy.py          # Dummy implementation (non-storage paradigms)
```

A given module ships whichever default fits its paradigm — a storage module
ships `memory.py`, an LLM inference or embedding module ships `dummy.py`. Not
both.

## Paradigms

| Paradigm | Category | ABC | Spec |
|---|---|---|---|
| `queue/` | Task queue | `Queue` | [QUEUE_SPEC.md](queue/QUEUE_SPEC.md) |
[← README](../../README.md)

# `backends/llm/` Module Spec

## Purpose

Houses concrete implementations of the `LLMBackend` ABC — each adapting a
specific model provider's API to the shared `complete` interface.

**Hard constraint:** `backends/` may import from `common/` and `libs/`, but
not from `pipelines/`, `services/`, or `infrastructure/`.

## Scope

No implementation started. This spec captures what any implementation
placed here is responsible for.

## File Layout

```
backends/llm/
  implementations/
```

Populated per provider as implementations are added — no fixed shape
assumed in advance.

## Responsibilities

Any implementation in this module must:
- Adapt a provider's request/response format to/from `Message`.
- Translate provider-specific parameters passed via `**kwargs`.

## Open Decisions
1. Whether a streaming completion method is needed, and its shape.
2. Whether provider-specific parameters stay in `**kwargs` or need
   dedicated fields once patterns across providers stabilize.
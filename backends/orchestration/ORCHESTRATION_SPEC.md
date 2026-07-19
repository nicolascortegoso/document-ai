[← README](../../README.md)

# `backends/orchestration/` Module Spec

## Purpose

Houses concrete implementations of the `Orchestrator` ABC — each binding
the framework's conversation-state/event vocabulary to a specific
execution engine.

**Hard constraint:** `backends/` may import from `common/` and `libs/`, but
not from `pipelines/`, `services/`, or `infrastructure/`.

## Scope

No implementation started. This spec captures what any implementation
placed here is responsible for.

## File Layout

```
backends/orchestration/
  implementations/
```

Populated per engine as implementations are added — no fixed shape assumed
in advance.

## Responsibilities

Any implementation in this module must:
- Translate its engine's native state/execution model into
  `ConversationState`.
- Translate its engine's native event/streaming output into `AgentEvent`.
- Own session/state persistence.
- Own its tool-calling integration (see Open Decisions).
- Own composition of any `LLMBackend`/`Tool` instances it needs — not part
  of the `Orchestrator` contract itself.

## Open Decisions
1. Tool-calling integration style: use an engine's own tool-calling
   scaffolding, or drive tool calls directly through `Tool.execute()`.
2. State persistence strategy: rely on the engine's native mechanism, or
   implement one independently.
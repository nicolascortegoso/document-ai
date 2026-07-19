[← README](../../README.md)

# `backends/tooling/` Module Spec

## Purpose

Houses concrete implementations of the `Tool` ABC — each wrapping a
specific transport behind the shared `execute` interface.

**Hard constraint:** `backends/` may import from `common/` and `libs/`, but
not from `pipelines/`, `services/`, or `infrastructure/`.

## Scope

No implementation started. This spec captures what any implementation
placed here is responsible for.

## File Layout

```
backends/tooling/
  implementations/
```

Populated per transport as implementations are added — no fixed shape
assumed in advance.

## Responsibilities

Any implementation in this module must:
- Wrap a specific transport (remote call, in-process callable, etc.)
  behind `execute`.
- Translate transport-specific errors into a returnable result rather than
  letting them propagate as uncaught exceptions.

## Open Decisions
1. Whether tool discovery/registration is handled per-backend or by a
   shared registry outside this spec's scope.
[← README](../README.md)

# infrastructure/ — Concrete Implementations Layer

## Principles

`infrastructure/` contains concrete, technology-specific implementations of
the ABCs defined in `backends/`, plus any framework-specific wiring referenced
by `pipelines/` (e.g. registering plain job functions with a real task-queue
technology). This is the only place vendor SDKs, database drivers, and
similar dependencies are imported directly.

## Rules

- May import from `common/`, `libs/`, `backends/`, and `pipelines/` — to
  implement their ABCs and wrap their job functions
- Implements existing ABCs; never defines new domain contracts. A capability
  that doesn't fit an existing `backends/` ABC belongs in `backends/`, not here
- Not imported by `common/`, `libs/`, `backends/`, `pipelines/`, or
  `services/` — those layers only know their own ABCs, never a concrete
  implementation
- Wired into `services/` at construction time by the application entrypoint,
  not by `services/` itself

## Pattern

```
infrastructure/<paradigm>/
    <technology>.py       # Concrete implementation of the matching backends/ ABC
```

e.g. `infrastructure/queue/celery_queue.py` implements `backends.queue.base.Queue`.

## Dependency Direction

```
infrastructure/ → common/ + libs/ + backends/ + pipelines/
```

Nothing in those layers depends on `infrastructure/`; it's wired in only at
the application entrypoint.

## Scope

This spec covers implementation classes only. Where and how those classes
get constructed and injected into `services/` (the application entrypoint /
composition root) is not covered here.

## Implementations

| Paradigm | ABC | Implementation | Spec |
|---|---|---|---|
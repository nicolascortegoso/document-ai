[← README](../README.md)

# services/ — Orchestration Facade Layer

## Principles

`services/` contains facade classes consumed by callers such as CLI scripts and
API routes. Each Service composes injected backend abstractions (from
`backends/`) with pipeline stage dispatch (from `pipelines/`), so that callers
never need to know about storage specifics or execution mechanics directly.

This is the top of the layer chain: `common/` → `libs/` → `backends/` →
`pipelines/` → `services/`. Nothing in the layers below may import from
`services/`. With task dispatch abstracted behind `backends/queue/`,
this layer — like every layer below it — has no direct dependency on the
task-queue technology in use; that dependency is confined to a concrete
`Queue` implementation in the infrastructure layer.

## Rules

- May import from `common/`, `libs/`, `backends/` (including
  `backends/queue/`), and `pipelines/` (including pipeline task modules,
  e.g. `pipelines/<pipeline>/tasks/`)
- Never instantiates concrete backend implementations — always receives them
  via constructor injection, including the `Queue`. Concrete backends
  are constructed and wired outside this layer, at the application entrypoint
- Dispatches asynchronous work via an injected `Queue`, never directly
  against a specific task-queue technology. Dispatch is always non-blocking:
  it enqueues via `Queue.dispatch()` and returns a `JobHandle`
  immediately. Whether and how long to wait is left to the caller, since
  that decision depends on the calling context (a CLI script may block; an
  HTTP request handler usually should not)
- Synchronous methods are reserved for direct, cheap backend reads (e.g.
  status/record lookups) that don't require pipeline dispatch
- A Service has no knowledge of HTTP or CLI specifics — a route handler or
  CLI command constructs it (with concrete backends already wired in) and
  calls its methods; no FastAPI- or Click-specific code lives inside a Service

## Pattern

```
services/<service>/
    service.py            # Service class (e.g. DocumentService)
    models.py             # Service-specific request/response models (where needed)
```

## Dependency Direction

```
services/ → common/ + libs/ + backends/ + pipelines/
```

## Testing Convention

Mirrors `pipelines/`'s convention:

```
tests/
└── test_services/
    └── document/
        └── test_service.py
```

## Service Specs

| Service | Spec |
|---|---|
| `document/` | [DOCUMENT_SERVICE_SPEC.md](document/DOCUMENT_SERVICE_SPEC.md) |
[← README](../README.md)

# pipelines/ — Orchestration Layer

## Principles

`pipelines/` contains orchestration abstractions. Every module defines an ABC
for a specific pipeline concern. Concrete implementations live in the
[infrastructure layer](../infrastructure/INFRASTRUCTURE_SPEC.md).

## Rules

- No imports from the infrastructure layer or any framework
- May import from `common/`, `libs/` and `backends/`
- Defines stage contracts, not execution strategies

## Pattern

```
pipelines/<pipeline>/
    base.py              # Pipeline ABC
    serializers.py       # Pipeline output serialisers (where needed)
    models.py            # Pipeline-specific models (where needed)
    tasks/                # Plain, framework-free job functions
```

No `registry.py` — unlike `libs/`, pipelines don't need priority-based
implementation selection; each stage has a single ABC.

`tasks/` functions are plain callables with no task-queue-specific code,
dispatched by `services/` via an injected `Queue`
(see [QUEUE_SPEC.md](../backends/queue/QUEUE_SPEC.md)).

## Dependency Direction

```
pipelines/ → common/ + libs/ + backends/
```

## Testing Convention

Test directories are prefixed with `test_` to avoid shadowing top-level
package names:

```
tests/
└── test_pipelines/
    └── ingestion/
        ├── test_base.py
        └── test_serializers.py
```

## Pipeline Specs

| Pipeline | Spec |
|---|---|
| `ingestion/` | [INGESTION_PIPELINE_SPEC.md](ingestion/INGESTION_PIPELINE_SPEC.md) |
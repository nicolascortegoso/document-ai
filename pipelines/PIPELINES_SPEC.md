[← README](../README.md)

# pipelines/ — Orchestration Layer

## Principles

`pipelines/` contains orchestration abstractions. Every module defines an ABC
for a specific pipeline concern, plus the one concrete implementation of that
ABC (in `implementations/`), composed from `libs/` and `backends/` registries.
This is the only implementation of the Pipeline ABC — nothing downstream
implements it again.

## Rules

- No imports from the infrastructure layer or any framework
- May import from `common/`, `libs/` and `backends/`
- No imports from another pipeline's package — chained pipelines connect
  through job dispatch (one pipeline's job result feeding the next
  dispatch), never through direct Python imports between
  `pipelines/<a>/` and `pipelines/<b>/`. This keeps pipelines
  independently deployable, which is the reason to split them in the
  first place.
- Defines stage contracts, not execution strategies

## Pattern

```
pipelines/<pipeline>/
    base.py               # Pipeline ABC
    serializers.py        # Pipeline output serialisers (where needed)
    implementations/
        <name>.py           # The pipeline's one concrete implementation
    tasks/
        <job>.py             # Plain, framework-free job functions
```

No `registry.py` — unlike `libs/`, pipelines don't need priority-based
implementation selection; each stage has a single ABC and a single
implementation.

`models.py` (where needed) is for genuinely pipeline-internal state — not
document content. Content extracted, profiled, or otherwise produced from a
document belongs in `common/models/`, the same way `PageProfile`/
`DocumentProfile`/`ParsedDocument` do, since other layers may need to
consume it and `libs/` can never import from `pipelines/` to get it back.

`tasks/` functions are plain callables with no task-queue-specific code,
dispatched by `services/` via an injected `Queue`
(see [QUEUE_SPEC.md](../backends/queue/QUEUE_SPEC.md)).

## Dependency Direction

```
pipelines/ → common/ + libs/ + backends/
```

## Testing Convention

Test directories are prefixed with `test_` to avoid shadowing top-level
package names, mirroring the source tree:

```
tests/
└── test_pipelines/
    └── ingestion/
        ├── implementations/
        │   └── test_ingestion.py
        └── tasks/
            └── test_profile.py
```

## Pipeline Specs

| Pipeline | Spec |
|---|---|
| `ingestion/` | [INGESTION_PIPELINE_SPEC.md](ingestion/INGESTION_PIPELINE_SPEC.md) |
| `summarization/` | [SUMMARIZATION_PIPELINE_SPEC.md](summarization/SUMMARIZATION_PIPELINE_SPEC.md) |
| `distillation/` | [DISTILLATION_PIPELINE_SPEC.md](distillation/DISTILLATION_PIPELINE_SPEC.md) |
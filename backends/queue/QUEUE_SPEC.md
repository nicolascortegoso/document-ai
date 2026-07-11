[← BACKENDS_SPEC](../BACKENDS_SPEC.md)

# Queue Paradigm

## Overview

Abstracts asynchronous job dispatch so that calling code never depends on a
specific task-queue technology. `DummyQueue` ships as the default — it
executes jobs synchronously, in-process, with no broker.

## Interface Contract

### `Queue` ABC

| Method | Signature | Description |
|---|---|---|
| `dispatch` | `(job_name: str, *args, **kwargs) -> JobHandle` | Enqueues the named job for execution and returns immediately with a handle. Never blocks. |

Jobs are referenced by name, not by direct function reference. Each `Queue`
implementation is responsible for resolving a name to the callable that
runs it.

### `JobHandle`

Defined in `backends/queue/models.py`. A generic wrapper for whatever handle
the underlying implementation returns.

| Method/Attribute | Description |
|---|---|
| `status` | Current job status (`PENDING`, `STARTED`, `SUCCESS`, `FAILURE`) |
| `result` | The job's return value once available; `None` before completion |
| `wait(timeout: float \| None = None)` | Blocks until the job completes or the timeout elapses |

## `DummyQueue`

- Executes the named job synchronously, in the calling process, the moment
  `dispatch()` is called
- Takes a `dict[str, Callable]` job registry at construction, mapping
  `job_name` to the callable that implements it
- `JobHandle.status` is always `SUCCESS` (or `FAILURE`, if the job raised)
  immediately after `dispatch()` returns
- Not for production use — no retries, no process isolation, no persistence
  across restarts

## Job Registration

Job functions are plain callables with no task-queue-specific code. Each
`Queue` implementation handles its own registration:

- `DummyQueue` takes its job registry directly, as a constructor argument
- A production implementation registers callables with its underlying
  technology at startup

## Folder Structure

```
backends/
└── queue/
    ├── __init__.py
    ├── base.py                # Queue ABC
    ├── models.py               # JobHandle
    └── implementations/
        ├── __init__.py
        └── dummy.py            # DummyQueue
```
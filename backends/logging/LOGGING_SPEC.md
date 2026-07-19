[← BACKENDS_SPEC](../BACKENDS_SPEC.md)

# Logging Paradigm

## Overview

Abstracts log emission so that calling code never depends on a specific
logging technology. `DummyLogger` ships as the default — it discards
everything. `ConsoleLogger` ships alongside it as a real, working
implementation for local development.

## Interface Contract

### `Logger` ABC

| Method | Signature | Description |
|---|---|---|
| `log` | `(level: LogLevel, message: str, **context: Any) -> None` | Emit a log record. Never raises. |
| `debug` | `(message: str, **context: Any) -> None` | Concrete convenience method — calls `log(LogLevel.DEBUG, message, **context)`. |
| `info` | `(message: str, **context: Any) -> None` | Calls `log(LogLevel.INFO, message, **context)`. |
| `warning` | `(message: str, **context: Any) -> None` | Calls `log(LogLevel.WARNING, message, **context)`. |
| `error` | `(message: str, **context: Any) -> None` | Calls `log(LogLevel.ERROR, message, **context)`. |
| `critical` | `(message: str, **context: Any) -> None` | Calls `log(LogLevel.CRITICAL, message, **context)`. |

`log` is the only abstract method — every concrete `Logger` implements just
that one; `debug`/`info`/`warning`/`error`/`critical` are concrete methods
on the ABC itself, each a thin wrapper calling `log`.

`log` never raises.

### `LogLevel`

Defined in `backends/logging/models.py`. `LogLevel(str, Enum)`, matching
`JobStatus`'s convention: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
(lowercase string values).

## `DummyLogger`

Discards every call. The default when no `Logger` is injected.

## `ConsoleLogger`

Prints to stdout, one line per call: level, message, and any `context`
key-value pairs, in a human-readable (not machine-parseable/JSON) format —
for local development, not log aggregation.

## Folder Structure

```
backends/
└── logging/
    ├── __init__.py
    ├── base.py                # Logger ABC
    ├── models.py               # LogLevel
    └── implementations/
        ├── __init__.py
        ├── dummy.py             # DummyLogger
        └── console.py           # ConsoleLogger
```
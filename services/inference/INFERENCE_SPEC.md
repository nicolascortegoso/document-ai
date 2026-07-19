[← README](../../README.md)

# `services/inference/` Module Spec

## Purpose

Composes an `Orchestrator` implementation to serve a single conversation
turn, scoped per request and long-running per session.

An implementation may be a plain retrieve-then-generate flow with no
tool-calling loop, or a fully agentic one. This module holds and serves
either unmodified.

## Scope

No implementation started. This spec captures what this module is
responsible for once one exists.

## File Layout

```
services/inference/
  inference_service.py
```

## Responsibilities

`InferenceService` (or equivalent):
- Holds an `Orchestrator` implementation, injected at construction —
  composition detail, not part of any ABC.
- Exposes a per-request entry point (turn-based, not batch) to whatever
  calls it (API route, etc.).
- Does not itself implement conversation logic — delegates entirely to the
  `Orchestrator` it holds.

## Open Questions
1. Whether this module also owns session lifecycle concerns (creating a new
   `session_id`, expiring old sessions) or whether that's the caller's
   responsibility.
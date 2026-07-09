[← MERGER_SPEC](../MERGER_SPEC.md)

# Reducer Module

## Overview

Provides a `Reducer` ABC for combining multiple texts into one reduced
representation. Injected into a merging strategy at construction time.

`DefaultReducer` ships as the only concrete implementation — a
non-LLM-backed fallback that produces a genuinely reduced output without
requiring an external service. A real, LLM-backed `Reducer` is expected
later, but is not part of this release.

## Interface Contract

### `Reducer` ABC

| Method | Signature | Description |
|---|---|---|
| `reduce` | `(reducer_input: ReducerInput) -> str` | Combines `reducer_input.texts` into a single reduced string. |

**Does not carry a "never raises" contract**, unlike some other
injected-dependency ABCs in this project. Failures propagate rather than
being silently absorbed.

### `ReducerInput` (`models.py`)

| Field | Type | Description |
|---|---|---|
| `texts` | `list[str]` | The texts to combine. Whether this is ever length `1` is the calling strategy's decision, not `Reducer`'s. |
| `prompt_template` | `str \| None` | Optional, for prompt-driven (e.g. LLM-backed) implementations. |

No `level` field — level-awareness stays with the calling strategy. No
`context` field.

## `DefaultReducer`

Truncates each text to `max_chars_per_text` characters (default `200`) and
joins with a space:

```python
" ".join(text[:max_chars_per_text] for text in reducer_input.texts)
```

Hard truncation, not boundary-aware.

No exception handling.

## Folder Structure

See `MERGER_SPEC.md`'s Folder Structure — `reducer/` nests under
`libs/merger/` exactly as depicted there.

## Acceptance Criteria

- [ ] `Reducer` ABC defined with a single method: `reduce`, taking `ReducerInput`
- [ ] `Reducer.reduce` contract does not claim "never raises" — failures propagate
- [ ] `ReducerInput` has `texts: list[str]` and `prompt_template: str | None = None` only — no `level`, no `context`
- [ ] `DefaultReducer` accepts `max_chars_per_text` (default `200`) at construction
- [ ] `DefaultReducer.reduce` truncates each text and joins with a space, no exception handling
- [ ] Unit tests cover: `DefaultReducer` truncation and joining behavior, empty `texts` list, `max_chars_per_text` boundary behavior

[← PARSER_SPEC](../PARSER_SPEC.md)

# Postprocessor Module

## Overview

Provides a `Postprocessor` ABC for transforming extracted text after a
`BasePageExtractionStrategy.extract()` call, before `ParserRegistry` returns
the final result. Injected into `ParserRegistry` at construction time.

`DefaultPostprocessor` (no-op pass-through) and `ChainedPostprocessor`
(applies a sequence of `PostprocessingStep`s) ship as the concrete
implementations.

## Interface Contract

### `Postprocessor` ABC

| Method | Signature | Description |
|---|---|---|
| `process` | `(text: str) -> str` | Transform the given text. Never raises. |

## `DefaultPostprocessor`

Returns `text` unchanged.

## `ChainedPostprocessor`

Takes `steps: list[PostprocessingStep]` at construction. `process(text)`
applies each step's `apply(text)` in order, feeding each step's output into
the next.

No concrete `PostprocessingStep` implementations ship in this release —
plain text needs no OCR-style cleanup. `ChainedPostprocessor` ships now as a
tested chaining mechanism so future steps (e.g. whitespace normalization,
OCR artifact correction) can be added without any change to `ParserRegistry`
or `ChainedPostprocessor` itself.

### `PostprocessingStep` ABC (`implementations/steps/base.py`)

| Method | Signature | Description |
|---|---|---|
| `apply` | `(text: str) -> str` | Apply this normalization step to the given text. |

## Folder Structure

See `PARSER_SPEC.md`'s Folder Structure — `postprocessor/` nests under
`libs/parser/` exactly as depicted there.

## Acceptance Criteria

- [ ] `Postprocessor` ABC defined with a single method: `process`
- [ ] `DefaultPostprocessor.process` returns its input unchanged
- [ ] `PostprocessingStep` ABC defined with a single method: `apply`
- [ ] `ChainedPostprocessor` accepts `steps: list[PostprocessingStep]` at construction
- [ ] `ChainedPostprocessor.process` applies each step in order, chaining outputs
- [ ] `ChainedPostprocessor.process` with an empty step list returns its input unchanged
- [ ] Unit tests cover: `DefaultPostprocessor` pass-through, `ChainedPostprocessor` applying multiple stub steps in the correct order, empty-list behavior

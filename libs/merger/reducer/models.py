from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ReducerInput:
    texts: list[str]
    prompt_template: str | None = None

"""Shared contracts between the three stages. THE ONLY file every teammate depends on.

Change it only with a PR that all three owners approve (see AGENTS.md).
Run `python -m contracts.schemas` to regenerate contracts/presentation.schema.json,
which non-Python tools and other AI assistants can read.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


class Fact(BaseModel):
    """One figure taken from the Sherpas diagnostic. Narration may only quote facts."""

    id: str = Field(description="Stable slug, e.g. 'savings_rate'")
    label: str
    value: float | str
    unit: str = ""
    source: str = Field(description="MCP tool and field the value came from")


class Visual(BaseModel):
    kind: Literal["title", "score", "kpi", "bar", "line", "text"]
    data: dict = Field(default_factory=dict)


class Scene(BaseModel):
    id: str
    title: str
    narration: str = Field(description="What the presenter says, in `Presentation.language`")
    visual: Visual
    fact_ids: list[str] = Field(default_factory=list, description="Facts quoted in the narration")
    audio_path: str | None = Field(default=None, description="Filled by the voice stage")
    duration_s: float | None = Field(default=None, description="Filled by the voice stage")


class Presentation(BaseModel):
    client_name: str
    language: Literal["es", "en"] = "es"
    facts: list[Fact]
    scenes: list[Scene]


if __name__ == "__main__":
    out = Path(__file__).with_name("presentation.schema.json")
    out.write_text(json.dumps(Presentation.model_json_schema(), indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {out}")

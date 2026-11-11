"""Cross-cutting check (owner: A). Every number the presenter says must be a Fact.

Runs between brain and voice: a hallucinated figure never reaches the audio.
"""
import re

from contracts.schemas import Presentation

NUMBER = re.compile(r"\d+(?:[.,]\d+)?")


def _normalise(text: str) -> float:
    return float(text.replace(",", "."))


def unsupported_numbers(presentation: Presentation) -> list[tuple[str, str]]:
    """Return (scene_id, number) for each spoken number not backed by the scene's facts."""
    facts = {f.id: f for f in presentation.facts}
    problems = []
    for scene in presentation.scenes:
        allowed = set()
        for fact_id in scene.fact_ids:
            fact = facts[fact_id]  # KeyError = scene quotes a fact that does not exist
            allowed.update(_normalise(n) for n in NUMBER.findall(f"{fact.value} {fact.unit}"))
        for spoken in NUMBER.findall(scene.narration):
            if _normalise(spoken) not in allowed:
                problems.append((scene.id, spoken))
    return problems

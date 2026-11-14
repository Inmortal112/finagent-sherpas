"""Stage 1 (owner: A). Sherpas diagnostic -> Presentation with facts and narration.

Input: the `financial-health.json` of one family in `cases/`.
Still template sentences (no LLM yet): the score, its five pillars and the plan's top moves.
"""
import re

from contracts.schemas import Fact, Presentation, Scene, Visual

SOURCE = "financial-health.json"


def build(diagnostic: dict, language: str = "en") -> Presentation:
    score = diagnostic["score"]
    name = _client_name(diagnostic["case"]["household"])

    facts = [
        Fact(id="score", label="Financial health score", value=score["published_score"], unit="/100",
             source=f"{SOURCE}:score.published_score"),
        Fact(id="band", label="Score band", value=score["band"], source=f"{SOURCE}:score.band"),
    ]
    scenes = [
        Scene(
            id="intro",
            title="Your financial health",
            narration=(
                f"Hello, {name}. Your financial health score is {score['published_score']} out of 100. "
                f"Sherpas calls that {score['band']}."
            ),
            visual=Visual(kind="score", data={"fact_id": "score"}),
            fact_ids=["score", "band"],
        )
    ]

    for i, pillar in enumerate(score["pillars"]):
        earned, available = pillar["points_shown_in_app"].split("/")
        fact_id = f"pillar_{_slug(pillar['pillar'])}"
        facts.append(Fact(id=fact_id, label=pillar["pillar"], value=int(earned), unit=f"/{available}",
                          source=f"{SOURCE}:score.pillars[{i}].points_shown_in_app"))
        scenes.append(
            Scene(
                id=fact_id,
                title=pillar["pillar"],
                narration=f"{pillar['pillar']}: {earned} out of {available} points.",
                visual=Visual(kind="kpi", data={"fact_id": fact_id}),
                fact_ids=[fact_id],
            )
        )

    for i, move in enumerate(score["top_moves"]):
        before_id, after_id = f"move_{i + 1}_score_before", f"move_{i + 1}_score_after"
        facts.append(Fact(id=before_id, label=f"{move['title']}: score before", value=move["score_before"],
                          unit="/100", source=f"{SOURCE}:score.top_moves[{i}].score_before"))
        facts.append(Fact(id=after_id, label=f"{move['title']}: score after", value=move["score_after"],
                          unit="/100", source=f"{SOURCE}:score.top_moves[{i}].score_after"))
        if move["score_after"] > move["score_before"]:
            effect = f"It takes your score from {move['score_before']} to {move['score_after']}."
        else:
            effect = f"On its own, your score stays at {move['score_before']}."
        scenes.append(
            Scene(
                id=f"move_{i + 1}",
                title=move["title"],
                narration=f"A step your plan already worked out: {move['title']}. {effect}",
                visual=Visual(kind="kpi", data={"fact_id": after_id}),
                fact_ids=[before_id, after_id],
            )
        )

    return Presentation(client_name=name, language=language, facts=facts, scenes=scenes)


def _client_name(household: list[dict]) -> str:
    """First names of the adults the plan belongs to, e.g. 'Timothy and Melanie'."""
    return " and ".join(p["first_name"] for p in household if p["role"] in ("client", "co-client"))


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")

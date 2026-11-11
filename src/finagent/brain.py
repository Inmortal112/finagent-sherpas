"""Stage 1 (owner: A). Sherpas diagnostic -> Presentation with facts and narration.

MOCK: template sentences over the placeholder fixture. Replace the body with the
MCP client + LLM; keep the signature.
"""
from contracts.schemas import Fact, Presentation, Scene, Visual


def build(diagnostic: dict, language: str = "es") -> Presentation:
    facts = [Fact(id="score", label="Salud financiera", value=diagnostic["score"], unit="/100", source="fixture:score")]
    facts += [
        Fact(id=key, label=m["label"], value=m["value"], unit=m["unit"], source=f"fixture:metrics.{key}")
        for key, m in diagnostic["metrics"].items()
    ]
    name = diagnostic["client"]["name"]
    scenes = [
        Scene(
            id="intro",
            title="Tu diagnóstico",
            narration=f"Hola, {name}. Tu salud financiera es de {diagnostic['score']} sobre 100.",
            visual=Visual(kind="score", data={"fact_id": "score"}),
            fact_ids=["score"],
        )
    ]
    for fact in facts[1:]:
        scenes.append(
            Scene(
                id=fact.id,
                title=fact.label,
                narration=f"{fact.label}: {fact.value} {fact.unit}.",
                visual=Visual(kind="kpi", data={"fact_id": fact.id}),
                fact_ids=[fact.id],
            )
        )
    return Presentation(client_name=name, language=language, facts=facts, scenes=scenes)

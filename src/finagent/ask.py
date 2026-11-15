"""Live questions (owner: A). A family's question -> the part of the home it is about and an answer.

A workflow, not an agent: the model picks one scene from the family's closed list and answers
with that scene's facts; `guard` checks the answer before anyone hears it. If the answer quotes
a number that is not in those facts, the model gets one more try, and after that the family
hears the narration already approved for that scene. Questions the plan does not cover get a
fixed sentence and are kept for the advisor.
"""
import json
import os
from dataclasses import asdict, dataclass, field
from typing import Callable

from contracts.schemas import Presentation
from finagent import narrator

# Measured on 2026-11-15 with real questions: deepseek-flash answers in 2-5 s and routes best, but had one
# 31 s reply; gemini-3.5-flash-lite takes 1-3 s; gpt-5-mini takes 11-28 s, too slow for a live answer.
DEFAULT_MODEL = "deepseek-flash"
FALLBACK_MODEL = "gemini-3.5-flash-lite"
TIMEOUT_S = 8.0
OFF_PLAN = "off_plan"
OFF_PLAN_ANSWER = (
    "Your plan does not cover that, so I would rather not guess. "
    "I have kept your question so your advisor can go through it with you."
)
UNAVAILABLE_ANSWER = "I could not work out an answer just now. Please ask me again in a moment."

SYSTEM_PROMPT = """\
You are the calm, warm voice of a family's financial plan, drawn as their own home. The family has
stopped the tour to ask a question. The plan was made by Sherpas, their financial planner.

The home: foundations = emergency fund and cash, roof = insurance and protection, walls = debt,
plumbing = savings and monthly cash flow, garden = investments growing for the future.

You get the question and the scenes of the tour, each with its facts. Do two things:
1. Choose the one scene whose facts answer the question. If the question is not about this family's
   plan, or asks for a prediction, a product, or advice the plan does not contain, choose "off_plan".
   Questions about the future, retirement, how long the money lasts or the garden drying up belong to
   the "timeline" scene. Questions about what to do first belong to a step scene ("move_...").
2. Answer the question using only that scene's facts.

Rules for numbers (a checker rejects the answer if you break them):
- Use only numbers that appear in the chosen scene's own facts, written as digits exactly as they
  appear there (money like $80,000, percentages like 24%). No other digits anywhere.
- Never spell a number out in words, and never round, add, subtract, average or compare figures yourself.
- Say "a year", never "/year". Say a shortfall in words, never with a minus sign.

Rules for the words:
- Answer the question first, directly. Spoken English, plain and short: 2 or 3 sentences, 50 words at most.
- Speak to the family as "you". No jargon; explain a needed term in a few words.
- You explain the plan that exists. Steps are things the plan already worked out, never your own advice.
- Be honest and kind: hard news plainly, without alarm and without blame.
- Never mention a negative balance or call running out of savings a debt: say the age when savings run out.
- No markdown, no lists, no emojis, no quotation marks, no dashes.

Answer with JSON only: {"scene": "<scene id or off_plan>", "answer": "<text, empty for off_plan>"}
"""


@dataclass
class Answer:
    question: str
    text: str
    scene_id: str | None = None      # the scene the home turns to, None when the plan does not cover it
    house_part: str | None = None
    fact_ids: list[str] = field(default_factory=list)
    source: str = "model"            # model | approved_narration | off_plan | unavailable

    def as_dict(self) -> dict:
        return asdict(self)


def answer(presentation: Presentation, diagnostic: dict, question: str,
           complete: Callable[[str, str], str] | None = None) -> Answer:
    """Answer one question about `presentation`. `complete(system, user) -> str` is the model call."""
    question = " ".join(question.split())
    if not question:
        return Answer(question, UNAVAILABLE_ANSWER, source="unavailable")
    complete = complete or _complete
    scenes = {scene.id: scene for scene in presentation.scenes}
    brief = dict(narrator._brief(presentation, diagnostic), question=question)

    scene_id, rejected_because = None, None
    for _ in range(2):
        if rejected_because:
            brief["rejected_because"] = f"your answer for scene {scene_id} was rejected: {rejected_because}"
        try:
            reply = json.loads(complete(SYSTEM_PROMPT, json.dumps(brief, ensure_ascii=False)))
            scene_id, text = reply.get("scene"), reply.get("answer") or ""
        except Exception:  # no key, no network, bad JSON: the family still gets a sentence
            return Answer(question, UNAVAILABLE_ANSWER, source="unavailable")
        if scene_id == OFF_PLAN or scene_id not in scenes:
            return Answer(question, OFF_PLAN_ANSWER, source="off_plan")
        accepted, rejected = narrator.check(presentation, {scene_id: text})
        if scene_id in accepted:
            return _for_scene(question, accepted[scene_id], scenes[scene_id], "model")
        rejected_because = rejected.get(scene_id, "the answer was empty")

    return _for_scene(question, scenes[scene_id].narration, scenes[scene_id], "approved_narration")


def _for_scene(question: str, text: str, scene, source: str) -> Answer:
    return Answer(question, text, scene_id=scene.id, house_part=scene.visual.data.get("house_part"),
                  fact_ids=list(scene.fact_ids), source=source)


def _complete(system: str, user: str) -> str:
    """Ask the fast model; if it is slow or fails, ask the fallback one. Raises when both fail."""
    client = narrator._client()
    models = [os.getenv("ASK_MODEL") or DEFAULT_MODEL, os.getenv("ASK_FALLBACK_MODEL") or FALLBACK_MODEL]
    error: Exception | None = None
    for model in dict.fromkeys(models):
        try:
            reply = client.with_options(timeout=TIMEOUT_S, max_retries=0).chat.completions.create(
                model=model,
                messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
                response_format={"type": "json_object"},
            )
            return reply.choices[0].message.content or "{}"
        except Exception as exc:
            error = exc
    raise error

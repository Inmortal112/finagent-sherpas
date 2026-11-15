"""Narration written by a text model, checked by `guard` (owner: A).

Generated once per family and saved in `narrations/<family>.json`, so the pipeline and the
demo never call the model, cost nothing and always say the same thing:

    python -m finagent.narrator samantha-lewis      # one family
    python -m finagent.narrator --all               # the four of them

`brain.build` applies the saved text. A scene whose text quotes a number that is not in its
facts falls back to the template sentence, so narration can never break the pipeline.
"""
import json
import logging
import os
import re
import sys
from pathlib import Path

from contracts.schemas import Presentation
from finagent import guard

log = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
NARRATIONS_DIR = ROOT / "narrations"
DEFAULT_MODEL = "deepseek-flash"

SYSTEM_PROMPT = """\
You write what a calm, warm voice says while a family looks at their financial plan drawn as their own home.
The plan was made by Sherpas, their financial planner. You explain the plan that exists; you never add advice.

The home: foundations = emergency fund and cash, roof = insurance and protection, walls = debt,
plumbing = savings and monthly cash flow, garden = investments growing for the future.
Each part is "solid", "cracked" or "broken".

You get the scenes of one family, in order, and you write the text of every scene. Each scene has an
"outline" (what it must cover, not wording to keep) and its "facts", each with a label and how to say it.
A fact labelled "Sherpas' observations" or "Sherpas' summary" is the planner's own explanation of that area:
use it to say, in everyday words, why that part of the home is in the state it is in and what it means for
this family. It is background for you: do not keep saying "Sherpas notes" or "Sherpas says".

Rules for numbers (a checker rejects any scene that breaks them):
- Use only numbers that appear in that scene's own facts, written as digits exactly as they appear there
  (money like $80,000, percentages like 24%). No other digits anywhere.
- Say "a year", never "/year" or "/yr". Say a shortfall in words (about $6,418 a year short), never with a minus sign.
- Never spell a number out in words, and never round, add, subtract, average or compare figures yourself.
- Keep each figure with the meaning its fact gives it. A part's score is said as "22 out of 30 points",
  never as 22/30 or 22.0.
- Choose the one or two figures that matter most in each scene. Do not list figures.

Rules for the words:
- Spoken English, plain and short: 2 to 4 sentences per scene, 60 words at most. No jargon: say it the way
  you would to a friend, and if a term is needed (umbrella cover, for example) explain it in a few words.
- Speak to the family as "you". The intro greets them by first name and tells them what they are about to see.
- Each part's scene names the part of the home and its state. Each step's scene says what the step is,
  which part of the home it repairs, and what it does to the score.
- Step titles and actions are written in planner language. Do not read them out: say what they mean
  ("spread out the money you hold in one single fund", not "reduce single-name concentration"). Never say
  investable, glide, horizon, band, gate, ratio, anchor, book, effort, mortality, allocation, revolving,
  exposure, shield, posture or liquidity. The scene that puts the steps together describes them in plain
  words too, without their titles.
- Steps are things the plan already worked out, not new ideas. Never present anything as your own advice.
- The timeline scene looks ahead through the years of the current plan.
- After the figures, close each part's scene with what it means in daily life for this family, concretely
  (what it protects them from, or what it leaves them open to). No abstract closing sentences.
- If a part's state is solid but the observations show a weak spot in it, say both, honestly.
- Be honest and kind. Hard news is said plainly, without alarm and without blame; good news without flattery.
- Never mention a negative balance or call running out of savings a debt: say the age when savings run out.
- Vary how sentences begin and end. Do not repeat the same closing phrase across scenes.
- No markdown, no lists, no emojis, no quotation marks, no dashes and no brackets.

Answer with JSON only: {"scenes": {"<scene id>": "<text>", ...}} with every scene id you were given.
"""


def apply_saved(presentation: Presentation, slug: str, directory: Path | None = None) -> Presentation:
    """Replace template sentences with the saved narration of `slug`, scene by scene, where `guard` accepts it."""
    path = (directory or NARRATIONS_DIR) / f"{slug}.json"
    if not path.exists():
        return presentation
    saved = json.loads(path.read_text(encoding="utf-8"))["scenes"]
    accepted, rejected = check(presentation, saved)
    for scene_id, reason in rejected.items():
        log.warning("Saved narration for %s/%s rejected (%s); using the template", slug, scene_id, reason)
    return _with_narration(presentation, accepted)


def check(presentation: Presentation, texts: dict[str, str]) -> tuple[dict[str, str], dict[str, str]]:
    """Split `texts` into (accepted, rejected with the reason). Unknown scene ids are ignored."""
    known = {scene.id for scene in presentation.scenes}
    texts = {scene_id: _tidy(text) for scene_id, text in texts.items()
             if scene_id in known and isinstance(text, str) and text.strip()}
    problems: dict[str, list[str]] = {}
    for scene_id, number in guard.unsupported_numbers(_with_narration(presentation, texts)):
        if scene_id in texts:
            problems.setdefault(scene_id, []).append(f"number {number} is not in the scene's facts")
    for scene_id, text in texts.items():
        for word in guard.spelled_numbers(text):
            problems.setdefault(scene_id, []).append(f"number written in words: {word}")
    accepted = {scene_id: text for scene_id, text in texts.items() if scene_id not in problems}
    return accepted, {scene_id: "; ".join(reasons) for scene_id, reasons in problems.items()}


def generate(presentation: Presentation, diagnostic: dict, model: str | None = None) -> dict:
    """Ask the model for every scene, retry the rejected ones once, and return what `guard` accepted."""
    model = model or os.getenv("BRAIN_MODEL") or DEFAULT_MODEL
    client = _client()
    brief = _brief(presentation, diagnostic)
    usage = {"prompt_tokens": 0, "completion_tokens": 0}

    accepted, rejected = check(presentation, _ask(client, model, brief, usage))
    missing = [scene["id"] for scene in brief["scenes"] if scene["id"] not in accepted]
    if missing:
        retry = dict(brief, scenes=[
            dict(scene, rejected_because=rejected.get(scene["id"], "no text was returned"))
            for scene in brief["scenes"] if scene["id"] in missing
        ])
        again, rejected = check(presentation, _ask(client, model, retry, usage))
        accepted.update(again)

    order = [scene.id for scene in presentation.scenes]
    return {
        "model": model,
        "scenes": {scene_id: accepted[scene_id] for scene_id in order if scene_id in accepted},
        "template_kept": [scene_id for scene_id in order if scene_id not in accepted],
        "usage": usage,
    }


def _tidy(text: str) -> str:
    """One line, no dashes between clauses (a voice reads them badly) and plain apostrophes."""
    text = re.sub(r"\s*[—–]\s*", ", ", text).replace("’", "'")
    return " ".join(text.split())


def _with_narration(presentation: Presentation, texts: dict[str, str]) -> Presentation:
    result = presentation.model_copy(deep=True)
    for scene in result.scenes:
        if scene.id in texts:
            scene.narration = texts[scene.id]
    return result


def _brief(presentation: Presentation, diagnostic: dict) -> dict:
    """What the model sees: the family and, per scene, only the facts that scene may quote."""
    facts = {fact.id: fact for fact in presentation.facts}
    scenes = []
    for scene in presentation.scenes:
        data = scene.visual.data
        entry = {
            "id": scene.id,
            "title": scene.title,
            "outline": scene.narration,
            "facts": [{"label": facts[i].label, "say_as": _say_as(facts[i])} for i in scene.fact_ids],
        }
        for key in ("house_part", "state", "effort", "house"):
            if data.get(key):
                entry[key] = data[key]
        if scene.id == "timeline":
            entry["events"] = [{k: v for k, v in event.items() if k in ("kind", "person")}
                               for event in data.get("events", [])]
        scenes.append(entry)
    return {
        "family": presentation.client_name,
        "people": [{"first_name": p["first_name"], "role": p["role"]} for p in diagnostic["case"]["household"]],
        "scenes": scenes,
    }


def _say_as(fact) -> str:
    """The fact the way it is written in a sentence: '22 out of 30', '$1,448,672.53', or its text."""
    value = fact.value
    if isinstance(value, str):
        return value
    number = f"{value:,.2f}".removesuffix(".00")
    if fact.unit.startswith("/"):
        return f"{number} out of {fact.unit[1:]}"
    if fact.unit == "USD":
        return f"${number}"
    if not fact.unit:
        return number.replace(",", "")  # ages and years: 2059, not 2,059
    return f"{number} {fact.unit}"


def _client():
    from dotenv import load_dotenv
    from openai import OpenAI

    load_dotenv(ROOT / ".env")
    return OpenAI(base_url=f"{os.environ['LLM_PROXY_URL'].rstrip('/')}/v1", api_key=os.environ["TEAM_KEY"])


def _ask(client, model: str, brief: dict, usage: dict) -> dict[str, str]:
    reply = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(brief, ensure_ascii=False)},
        ],
        response_format={"type": "json_object"},
    )
    if reply.usage:
        usage["prompt_tokens"] += reply.usage.prompt_tokens
        usage["completion_tokens"] += reply.usage.completion_tokens
    try:
        scenes = json.loads(reply.choices[0].message.content or "{}").get("scenes", {})
    except json.JSONDecodeError:
        return {}
    return scenes if isinstance(scenes, dict) else {}


def main(families: list[str]) -> int:
    from finagent import brain  # here, not at the top: brain imports this module

    if families == ["--all"]:
        families = sorted(p.parent.name for p in (ROOT / "cases").glob("*/financial-health.json"))
    NARRATIONS_DIR.mkdir(exist_ok=True)
    kept = 0
    for family in families:
        diagnostic = json.loads((ROOT / "cases" / family / "financial-health.json").read_text(encoding="utf-8"))
        result = generate(brain.build_template(diagnostic), diagnostic)
        path = NARRATIONS_DIR / f"{family}.json"
        path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        kept += len(result["template_kept"])
        print(f"{family}: {len(result['scenes'])} scenes written, template kept for {result['template_kept']}, "
              f"tokens {result['usage']} -> {path.relative_to(ROOT)}")
    return 1 if kept else 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("usage: python -m finagent.narrator <family> [<family> ...] | --all")
    raise SystemExit(main(sys.argv[1:]))

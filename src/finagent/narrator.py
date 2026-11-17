"""Narration written by a text model, checked by `guard` (owner: A).

Generated once per family and saved in `narrations/<family>.json`, so the pipeline and the
demo never call the model, cost nothing and always say the same thing:

    python -m finagent.narrator samantha-lewis      # one family
    python -m finagent.narrator --all               # the four of them
    python -m finagent.narrator --all --simple      # the simple mode (shorter, one figure at most)
    python -m finagent.narrator --all --missing     # only the scenes that have no accepted text yet
    python -m finagent.narrator --all --style numbers   # another way of explaining the same scenes (STYLES)

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
- A scene with a "person" is that one adult's own part of the home: speak to them by first name, about what
  is in their name (their cover, their accounts, their debts), and what it means for the other people at home.
- After the figures, close each part's scene with what it means in daily life for this family, concretely
  (what it protects them from, or what it leaves them open to). No abstract closing sentences.
- If a part's state is solid but the observations show a weak spot in it, say both, honestly.
- Be honest and kind. Hard news is said plainly, without alarm and without blame; good news without flattery.
- Never mention a negative balance or call running out of savings a debt: say the age when savings run out.
- Vary how sentences begin and end. Do not repeat the same closing phrase across scenes.
- No markdown, no lists, no emojis, no quotation marks, no dashes and no brackets.

Answer with JSON only: {"scenes": {"<scene id>": "<text>", ...}} with every scene id you were given.
"""


SIMPLE_MODE = """
Simple mode. This person rarely uses apps or reads financial papers, and may be elderly. Override the length
rule above: 1 or 2 short sentences per scene, 28 words at most, with one figure at most (the most important one;
a part's score counts as that figure). Everyday words only, one idea per sentence, nothing to work out.
"""

MODE_KEY = {"complete": "scenes", "simple": "simple"}  # where each mode lives in narrations/<family>.json

# Other ways of explaining the same scenes, for the person who asks for one: a paragraph added to the prompt, and
# the text saved under its own key. The narration itself is the "story" style (the plan told as the family's home).
STYLES = {
    "numbers": """
Numbers first. This person asked to hear the figure before the explanation. Where the rules for the words above
say otherwise, these win (the rules for numbers stay exactly as they are):
- The first sentence of each scene carries its most important figure and what it measures, in the order people
  speak ("Your debt scores 15 out of 20 points", not "15 out of 20 points is your debt score"). Then say what
  that figure means for this family in daily life, and stop.
- Use two or three figures in a scene when its facts hold them and they matter, each with what it measures.
  Still never a list.
- A step's scene opens with what the step does to the score, then says in everyday words what the family would
  actually do and which part of the home it repairs. Never its title or planner wording (withdrawal rate, growth
  mix, liability): "take less out of your savings each year once you retire", not "lower the withdrawal rate".
- The home is only where to look: name the part of the home and its state once, in a few words. Build no image on
  it: nothing about storms, leaks, shelter, cracks spreading or things growing.
- No warm-up, no reassurance and no closing thought. Short, direct sentences, 55 words at most per scene.
- The intro greets them by first name in two or three words and goes straight to the score.
""",
}


def text_key(mode: str = "complete", style: str | None = None) -> str:
    """Where a text lives in narrations/<family>.json: each mode has its entry, and each style one per mode."""
    if not style:
        return MODE_KEY[mode]
    if style not in STYLES:
        raise ValueError(f"style must be one of {sorted(STYLES)}, not {style!r}")
    return style if mode == "complete" else f"{style}_{mode}"


def saved_texts(slug: str, mode: str = "complete", directory: Path | None = None,
                style: str | None = None) -> dict[str, str]:
    path = (directory or NARRATIONS_DIR) / f"{slug}.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8")).get(text_key(mode, style)) or {}


def styled(presentation: Presentation, slug: str, style: str, mode: str = "complete",
           directory: Path | None = None) -> dict[str, str]:
    """The saved texts of `style` that `guard` accepts for this presentation; a scene without one keeps its narration."""
    accepted, rejected = check(presentation, saved_texts(slug, mode, directory, style))
    for scene_id, reason in rejected.items():
        log.warning("Saved %s text for %s/%s rejected (%s); the narration stays", style, slug, scene_id, reason)
    return accepted


def apply_saved(presentation: Presentation, slug: str, directory: Path | None = None,
                mode: str = "complete") -> Presentation:
    """Replace template sentences with the saved narration of `slug`, scene by scene, where `guard` accepts it."""
    saved = saved_texts(slug, mode, directory)
    if not saved:
        return presentation
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
        for phrase in guard.part_scored_out_of_100(text):
            problems.setdefault(scene_id, []).append(
                f"only the overall score is out of 100, not a part of the home: {phrase}")
    pays_part = {scene.id for scene in presentation.scenes if scene.visual.data.get("pays_part_of_debt")}
    for scene_id in pays_part & texts.keys():
        for phrase in guard.claims_debt_cleared(texts[scene_id]):
            problems.setdefault(scene_id, []).append(
                f"this step pays only part of the debt, so it is not cleared or paid off: {phrase}")
    accepted = {scene_id: text for scene_id, text in texts.items() if scene_id not in problems}
    return accepted, {scene_id: "; ".join(reasons) for scene_id, reasons in problems.items()}


def generate(presentation: Presentation, diagnostic: dict, model: str | None = None, mode: str = "complete",
             only: set[str] | None = None, style: str | None = None) -> dict:
    """Ask the model for every scene (or just `only`), retry the rejected ones once, and return what `guard` accepted."""
    model = model or os.getenv("BRAIN_MODEL") or DEFAULT_MODEL
    client = _client()
    brief = _brief(presentation, diagnostic)
    if only is not None:
        brief["scenes"] = [scene for scene in brief["scenes"] if scene["id"] in only]
    system = SYSTEM_PROMPT + (SIMPLE_MODE if mode == "simple" else "") + (STYLES[style] if style else "")
    usage = {"prompt_tokens": 0, "completion_tokens": 0}

    accepted, rejected = check(presentation, _ask(client, model, brief, usage, system))
    missing = [scene["id"] for scene in brief["scenes"] if scene["id"] not in accepted]
    if missing:
        retry = dict(brief, scenes=[
            dict(scene, rejected_because=rejected.get(scene["id"], "no text was returned"))
            for scene in brief["scenes"] if scene["id"] in missing
        ])
        again, rejected = check(presentation, _ask(client, model, retry, usage, system))
        accepted.update(again)

    order = [scene.id for scene in presentation.scenes]
    return {
        "model": model,
        "scenes": {scene_id: accepted[scene_id] for scene_id in order if scene_id in accepted},
        "template_kept": [scene["id"] for scene in brief["scenes"] if scene["id"] not in accepted],
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
        if data.get("pays_part_of_debt"):
            entry["note"] = "This step pays part of the debt. The rest is still owed: never say it is cleared or paid off."
        for key in ("house_part", "state", "effort", "house", "person"):
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


def _ask(client, model: str, brief: dict, usage: dict, system: str = SYSTEM_PROMPT) -> dict[str, str]:
    reply = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
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


def main(args: list[str]) -> int:
    """`<family>... | --all`, plus `--simple` (the simple mode), `--style <name>` (one of STYLES) and `--missing`
    (only the scenes with no accepted text)."""
    from finagent import brain  # here, not at the top: brain imports this module

    mode = "simple" if "--simple" in args else "complete"
    missing_only = "--missing" in args
    style = None
    if "--style" in args:
        at = args.index("--style")
        style = args[at + 1] if at + 1 < len(args) else ""
        args = args[:at] + args[at + 2:]
    key = text_key(mode, style)
    label = f"{mode}, {style}" if style else mode
    families = [a for a in args if not a.startswith("--")]
    if "--all" in args:
        families = sorted(p.parent.name for p in (ROOT / "cases").glob("*/financial-health.json"))
    NARRATIONS_DIR.mkdir(exist_ok=True)
    kept = 0
    for family in families:
        diagnostic = json.loads((ROOT / "cases" / family / "financial-health.json").read_text(encoding="utf-8"))
        template = brain.build_template(diagnostic)
        path = NARRATIONS_DIR / f"{family}.json"
        saved = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        already, _ = check(template, saved.get(key) or {}) if missing_only else ({}, {})
        only = {scene.id for scene in template.scenes} - set(already)
        if not only:
            print(f"{family} ({label}): nothing missing")
            continue
        result = generate(template, diagnostic, mode=mode, only=only, style=style)
        texts = {**already, **result["scenes"]}
        saved[key] = {scene.id: texts[scene.id] for scene in template.scenes if scene.id in texts}
        if missing_only or style:
            saved.setdefault("model", result["model"])  # a top-up or a style keeps the name of the narration's model
        else:
            saved["model"] = result["model"]            # everything in this mode was rewritten
        saved.pop("template_kept", None), saved.pop("usage", None)
        path.write_text(json.dumps(saved, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        kept += len(result["template_kept"])
        print(f"{family} ({label}): {len(result['scenes'])} scenes written, template kept for "
              f"{result['template_kept']}, tokens {result['usage']} -> {path.relative_to(ROOT)}")
    return 1 if kept else 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("usage: python -m finagent.narrator <family>... | --all  [--simple] [--style <name>] [--missing]")
    raise SystemExit(main(sys.argv[1:]))

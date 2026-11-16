"""The family's home explained to the children, out loud: about thirty seconds, by name, with no figures.

A plan belongs to the whole household, but nobody explains it to the children. Here the home does, in their words:

    "Oliver, Sophia, this is your family's home. Each part of it is a piece of the family's money plan.
     The walls and the foundations are strong. The roof keeps everyone safe if something goes wrong, like an
     accident or someone getting sick. Right now it needs real work. ..."

Two tones: one for young children, one for teenagers (all of them 13 or older). It never says "mom" or "dad"
(the data does not say who is who): it speaks of "your family". Fixed sentences from the parts' states, which
the plan already holds: no model, no figures, so the same text (and the same audio) every time.
"""
from __future__ import annotations

from contracts.schemas import Presentation

TEEN_FROM = 13
ORDER = ("foundations", "walls", "roof", "plumbing", "garden")
NAMES = {"foundations": "the foundations", "walls": "the walls", "roof": "the roof", "plumbing": "the plumbing",
         "garden": "the garden"}
WHAT_IT_IS = {
    "young": {
        "foundations": "The foundations are the money saved for a rainy day, so a surprise never knocks the house over.",
        "walls": "The walls are about what the family owes. Strong walls mean borrowed money is under control.",
        "roof": "The roof keeps everyone safe if something goes wrong, like an accident or someone getting sick.",
        "plumbing": "The plumbing is the money that comes in and goes out every month.",
        "garden": "The garden is what the family is growing for later, like school one day, and a calm old age.",
    },
    "teen": {
        "foundations": "The foundations are the emergency savings: what keeps a surprise bill from becoming a crisis.",
        "walls": "The walls are the family's debts, and how well they are under control.",
        "roof": "The roof is the insurance that protects everyone if something goes wrong.",
        "plumbing": "The plumbing is the monthly cash flow: what comes in, and what goes out.",
        "garden": "The garden is the money growing for the future: college, and retirement one day.",
    },
}
HOW_IT_IS = {"cracked": "has a few cracks to fix", "broken": "needs real work"}
PLURAL = ("foundations", "walls")
MOST_TO_TELL = 2   # the two parts that need it most: about thirty seconds
CLOSING = {
    "young": ("Your family has a plan to fix it, one step at a time, and every step makes the home stronger. "
              "The best way to help is to ask about it, and to cheer them on."),
    "teen": ("Your family has a plan to fix it, one step at a time. It is worth understanding: one day this will be "
             "your own plan. Ask about it."),
    "fine": ("Your family is looking after it, so it stays this way. One day you will have a home like this of your "
             "own. Ask how it works."),
}


def children(plan: Presentation) -> list[dict]:
    intro = next((scene for scene in plan.scenes if scene.id == "intro"), None)
    people = (intro.visual.data.get("people") if intro else None) or []
    return [p for p in people if p.get("role") == "child" and p.get("first_name")]


def build(plan: Presentation) -> dict:
    """{"available", "to": [names], "text"} for this plan's children, or available False when there are none."""
    kids = children(plan)
    if not kids:
        return {"available": False, "reason": "This plan has no children."}
    intro = next(scene for scene in plan.scenes if scene.id == "intro")
    states = intro.visual.data.get("house") or {}
    tone = "teen" if all((p.get("age") or 0) >= TEEN_FROM for p in kids) else "young"
    names = [p["first_name"] for p in kids]

    said = [f"{_join(names)}, this is your family's home.", "Each part of it is a piece of the family's money plan."]
    strong = [NAMES[part] for part in ORDER if states.get(part) == "solid"]
    to_fix = sorted((part for part in ORDER if states.get(part) in HOW_IT_IS), key=lambda part: states[part] != "broken")
    if strong and to_fix:
        said.append(f"{_capital(_join(strong))} {'is' if len(strong) == 1 else 'are'} strong.")
    elif strong:
        said.append("Every part of it is strong.")
    for part in to_fix[:MOST_TO_TELL]:
        said += [WHAT_IT_IS[tone][part], f"Right now {'they' if part in PLURAL else 'it'} {_verb(states[part], part)}."]
    if len(to_fix) > MOST_TO_TELL:
        rest = [NAMES[part] for part in to_fix[MOST_TO_TELL:]]
        said.append(f"{_capital(_join(rest))} could use some care too.")
    said.append(CLOSING[tone] if to_fix else CLOSING["fine"])
    return {"available": True, "to": names, "text": " ".join(said)}


def _join(items: list[str]) -> str:
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def _verb(state: str, part: str) -> str:
    phrase = HOW_IT_IS[state]
    return phrase.replace("has ", "have ").replace("needs ", "need ") if part in PLURAL else phrase


def _capital(text: str) -> str:
    return text[:1].upper() + text[1:]

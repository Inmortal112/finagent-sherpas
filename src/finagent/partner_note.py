"""A short voice note for the other half of a couple (owner: B, voice).

    note = partner_note.build(session, plan)
    note["text"]  # "Emily, Daniel just went through your family plan. Daniel's biggest worry: paying for college.
                  #  The first step Daniel chose: add more life insurance. It takes your score from 52 to 57. ..."

When one adult goes through the plan, nothing carries it to the other one. This note does: about twenty seconds
the visitor can send like a voice message (`GET /partner-note`, and its audio at `/partner-note/{session}.mp3`).

Fixed sentences filled from the session and the plan, like the day-3 reminders: no model, free and instant.
Its only figures are the chosen step's score before and after, both facts of the plan. The worry is the family's
own words, so it goes in without any number (and is left out if it spells one in words).
"""
from __future__ import annotations

from contracts.schemas import Presentation
from finagent import guard
from finagent.sessions import FIGURE

ADULT_ROLES = ("client", "co-client")
MAX_WORRY_CHARS = 120


def adults(plan: Presentation) -> list[str]:
    """First names of the adults the plan belongs to: two for a couple, one otherwise."""
    intro = next((scene for scene in plan.scenes if scene.id == "intro"), None)
    people = intro.visual.data.get("people", []) if intro else []
    return [person["first_name"] for person in people if person.get("role") in ADULT_ROLES]


def build(session: dict, plan: Presentation, person: str | None = None) -> dict:
    """The note from the visitor to their partner, or why there is none (`available` False and a `reason`).

    `person` is who is sending it, when the session does not know yet (the page can always tell).
    """
    names = adults(plan)
    if len(names) < 2:
        return _none("This plan belongs to one person: there is no partner to send a note to.")
    sender = _match(person or session.get("person"), names)
    if sender is None:
        return _none(f"Say who is sending the note: {' or '.join(names)}.")
    decision = session.get("decision")
    if not decision:
        return _none("Choose a first step before sending a note.")
    step = next((scene for scene in plan.scenes if scene.id == decision["scene_id"]), None)
    if step is None:
        return _none("The chosen step is not part of this plan.")

    partner = next(name for name in names if name != sender)
    sentences = [f"{partner}, {sender} just went through your family plan."]
    worry = _worry(session)
    if worry:
        sentences.append(f"{sender}'s biggest worry: {worry}.")
    data = step.visual.data
    title = data.get("plain_title") or decision.get("plain_title") or decision["title"]
    sentences.append(f"The first step {sender} chose: {_lower_first(title).rstrip('.')}.")
    if data.get("score_before") is not None and data.get("score_after") is not None:
        sentences.append(f"It takes your score from {data['score_before']} to {data['score_after']}.")
    if (session.get("follow_up") or {}).get("done"):
        sentences.append(f"{sender} has already started it.")
    sentences.append("Have a look at your part of the home when you have a moment. It's a plan for the two of you.")
    return {"available": True, "from": sender, "to": partner, "scene_id": step.id, "text": " ".join(sentences)}


def _worry(session: dict) -> str | None:
    """Their latest worry, ready to go inside a sentence, or None. Never carries a figure."""
    worries = session.get("worries") or []
    if not worries:
        return None
    text = " ".join(worries[-1]["text"].split()).rstrip(" .!?")
    if not text or guard.spelled_numbers(text):
        return None
    text = " ".join(FIGURE.sub(" ", text).split())
    if len(text) > MAX_WORRY_CHARS:
        text = text[:MAX_WORRY_CHARS].rsplit(" ", 1)[0]
    return _lower_first(text) if text else None


def _lower_first(text: str) -> str:
    """'Paying for college' -> 'paying for college', but 'I am afraid' and 'IRA' stay as they are."""
    first = text.split(" ", 1)[0]
    if first in ("I", "I'm", "I've", "I'd", "I'll") or first.isupper():
        return text
    return text[:1].lower() + text[1:]


def _match(person: str | None, names: list[str]) -> str | None:
    if not person:
        return None
    return next((name for name in names if name.lower() == person.strip().lower()), None)


def _none(reason: str) -> dict:
    return {"available": False, "reason": reason}

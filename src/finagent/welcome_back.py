"""What the home says, out loud, when the family comes back (day 3 and after).

The check-in already exists as text (`sessions.reminders`). This puts a greeting in front of it and picks what is
worth saying aloud, so the home speaks first instead of waiting to be read: "Welcome back, Daniel. A few days ago
you chose a first step: add more life insurance. Have you been able to start it?"

Fixed sentences, the family's own step and the plan's own dates: no model and no new figures.
"""
from __future__ import annotations

SPOKEN_KINDS = ("check_in", "no_step_yet", "plan_date")  # in the order they are said


def text(session: dict, reminders: dict) -> str | None:
    """The sentence to speak for these reminders, or None when nothing is waiting for the family."""
    due = reminders.get("due") or []
    if not due:
        return None
    said = []
    for kind in SPOKEN_KINDS:   # the question about their step first; then one date of the plan at most
        match = next((item["text"] for item in due if item["kind"] == kind), None)
        if match and not (kind == "no_step_yet" and said):
            said.append(match)
    person = session.get("person")
    greeting = f"Welcome back, {person}." if person else "Welcome back."
    return " ".join([greeting, *said])

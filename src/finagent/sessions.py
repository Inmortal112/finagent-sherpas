"""Conversation history (owner: A). One JSON file per session: what was asked, what was answered, what was chosen.

A session is one person on one device going through their plan. The page keeps the session id
and sends it with every question, so the family can look back at their earlier questions and the
advisor gets a note of what they asked and decided. No accounts and no database: files are enough
for a demo, and `data/` is git-ignored.
"""
import json
import os
import re
import secrets
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from finagent import house

ROOT = Path(__file__).resolve().parents[2]
SESSION_ID = re.compile(r"^[A-Za-z0-9_-]{8,64}$")  # also keeps a session id from being a path
MONTHS = ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December")
FIGURE = re.compile(r"[$€£]?\s?\d[\d,.]*\s?%?")  # any number someone typed, with its currency sign or percent
CONTEXT_ITEMS = 3     # worries and parts of the home kept in the summary: its size never grows with the session
CONTEXT_CHARS = 300   # longest text kept from one question, answer or worry
CHECK_IN_AFTER_DAYS = 3     # the idea note: "checks in with them on day 3"
PLAN_DATE_WINDOW_DAYS = 90  # a plan date is announced this long before it arrives


def max_turns() -> int:
    """Questions one session may ask (ASK_MAX_TURNS): keeps a shared link from spending the team's credits."""
    return int(os.getenv("ASK_MAX_TURNS") or 40)


def directory() -> Path:
    return Path(os.getenv("SESSIONS_DIR") or ROOT / "data" / "sessions")


def new_id() -> str:
    return secrets.token_urlsafe(12)


def is_valid(session_id: str | None) -> bool:
    return bool(session_id and SESSION_ID.match(session_id))


def load(session_id: str) -> dict | None:
    path = directory() / f"{session_id}.json"
    if not is_valid(session_id) or not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def start(family: str, session_id: str | None = None, person: str | None = None,
          mode: str | None = None) -> dict:
    """The stored session, or a new one for `family` (with a new id when `session_id` is missing or not valid).

    `person` (who is using it) and `mode` ("simple" / "complete") are remembered when given.
    """
    session = load(session_id) if session_id else None
    if not session or session["family"] != family:
        session = {"session_id": session_id if is_valid(session_id) and not session else new_id(),
                   "family": family, "started": _now(), "turns": [], "decision": None}
    for key, default in (("person", None), ("mode", None), ("worries", []), ("follow_up", None)):
        session.setdefault(key, default)
    if person:
        session["person"] = person
    if mode:
        session["mode"] = mode
    return session


def add_worry(session: dict, text: str, house_part: str | None) -> dict:
    """What worries them, in their own words: none of the plans records this today."""
    worry = {"text": text, "house_part": house_part, "said_at": _now()}
    session["worries"].append(worry)
    save(session)
    return worry


def follow_up(session: dict, done: bool, note: str | None = None) -> dict:
    """Their answer to the day-3 check-in: did they take the step they chose?"""
    session["follow_up"] = {"done": done, "note": note, "answered_at": _now()}
    save(session)
    return session["follow_up"]


def month_year(iso_date: str) -> str:
    """'2027-01-01' -> 'January 2027' (the case rules: a date is said as month and year)."""
    return f"{MONTHS[int(iso_date[5:7]) - 1]} {iso_date[:4]}"


def reminders(session: dict, diagnostic: dict, today: date) -> dict:
    """What the page should say when the family comes back on `today`. Nothing is sent: the page asks.

    Fixed sentences with the step's title and the plan's own dates; no model and no new figures.
    `today` is a parameter so the demo can travel in time.
    """
    due = []
    decision, answered = session.get("decision"), session.get("follow_up")
    if decision and not answered and today >= _day(decision["decided_at"]) + timedelta(days=CHECK_IN_AFTER_DAYS):
        due.append({"kind": "check_in", "scene_id": decision["scene_id"],
                    "text": f"A few days ago you chose a first step: {decision['title']}. "
                            "Have you been able to start it?"})
    elif not decision and today >= _day(session["started"]) + timedelta(days=CHECK_IN_AFTER_DAYS):
        due.append({"kind": "no_step_yet", "scene_id": None,
                    "text": "You looked at your home a few days ago and have not chosen a first step yet. "
                            "Would you like to see the steps again?"})

    upcoming = []
    for plan_date in house.plan_dates(diagnostic):
        when = date.fromisoformat(plan_date["date"])
        if when < today:
            continue
        entry = {**plan_date, "label": month_year(plan_date["date"])}
        upcoming.append(entry)
        if (when - today).days <= PLAN_DATE_WINDOW_DAYS:
            due.append({"kind": "plan_date", "scene_id": "timeline", "date": plan_date["date"],
                        "text": f"Your plan has this coming up in {entry['label']}: {plan_date['name']}. "
                                "It is a good moment to look at your home again."})
    return {"today": today.isoformat(), "due": due, "upcoming": upcoming}


def _day(timestamp: str) -> date:
    return datetime.fromisoformat(timestamp).date()


def add_turn(session: dict, turn: dict) -> dict:
    """Append one question and its answer, save the session and return the stored turn (with id and time)."""
    stored = {"turn_id": f"t{len(session['turns']) + 1}", "asked_at": _now(), **turn}
    session["turns"].append(stored)
    save(session)
    return stored


def decide(session: dict, scene_id: str, title: str) -> dict:
    """Record the step the family chose to take."""
    session["decision"] = {"scene_id": scene_id, "title": title, "decided_at": _now()}
    save(session)
    return session["decision"]


def save(session: dict) -> None:
    path = directory() / f"{session['session_id']}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(session, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def audio_path(session_id: str, turn_id: str) -> Path:
    return directory() / "audio" / f"{session_id}-{turn_id}.mp3"


def advisor_note(session: dict) -> dict:
    """What the advisor needs before the next conversation: what they asked about, what the plan could not
    answer, and the step they chose."""
    turns = session["turns"]
    parts: dict[str, int] = {}
    for turn in turns:
        if turn.get("house_part"):
            parts[turn["house_part"]] = parts.get(turn["house_part"], 0) + 1
    return {
        "session_id": session["session_id"],
        "family": session["family"],
        "person": session.get("person"),
        "mode": session.get("mode"),
        "started": session["started"],
        "worries": [worry["text"] for worry in session.get("worries", [])],
        "questions": [turn["question"] for turn in turns if turn.get("kind") != "worry"],
        "asked_most_about": sorted(parts, key=parts.get, reverse=True),
        "questions_by_part": parts,
        "not_covered_by_the_plan": [turn["question"] for turn in turns if turn.get("source") == "off_plan"],
        "decision": session["decision"],
        "follow_up": session.get("follow_up"),
    }


def context_for(session: dict) -> dict | None:
    """What the model should know about this conversation before the next question, or None at the start.

    A summary made by code, the same size however long the session is (see escalabilidad.md): what worries
    them, the parts of the home they asked about most and the step they chose, all without figures, plus
    the last question and its answer word for word so that "that" or "it" can be understood.
    Set ASK_HISTORY=off to answer every question on its own, as before.
    """
    if (os.getenv("ASK_HISTORY") or "on").lower() in ("off", "0", "false", "no"):
        return None
    turns = session.get("turns") or []
    if not turns:
        return None
    note = advisor_note(session)
    context: dict = {}
    if note["worries"]:
        context["worries"] = [_no_figures(text) for text in note["worries"][-CONTEXT_ITEMS:]]
    if note["asked_most_about"]:
        context["asked_most_about"] = note["asked_most_about"][:CONTEXT_ITEMS]
    if note["decision"]:
        context["chosen_step"] = _no_figures(note["decision"]["title"])
    last = turns[-1]
    previous = {"question": _short(last.get("question") or "")}
    if last.get("source") in ("model", "approved_narration"):
        previous["answer"] = _short(last.get("text") or "")
        previous["scene"] = last.get("scene_id")
        if last.get("house_part"):
            previous["house_part"] = last["house_part"]
    context["previous"] = previous
    return context


def _short(text: str) -> str:
    text = " ".join(text.split())
    return text if len(text) <= CONTEXT_CHARS else text[:CONTEXT_CHARS].rsplit(" ", 1)[0] + "…"


def _no_figures(text: str) -> str:
    """The same sentence without its numbers: a summary must not carry a figure into a scene that lacks it."""
    return _short(FIGURE.sub(" an amount ", text))


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

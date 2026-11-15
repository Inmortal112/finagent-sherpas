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
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SESSION_ID = re.compile(r"^[A-Za-z0-9_-]{8,64}$")  # also keeps a session id from being a path


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


def start(family: str, session_id: str | None = None) -> dict:
    """The stored session, or a new one for `family` (with a new id when `session_id` is missing or not valid)."""
    session = load(session_id) if session_id else None
    if session and session["family"] == family:
        return session
    return {"session_id": session_id if is_valid(session_id) and not session else new_id(), "family": family,
            "started": _now(), "turns": [], "decision": None}


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
        "started": session["started"],
        "questions": [turn["question"] for turn in turns],
        "asked_most_about": sorted(parts, key=parts.get, reverse=True),
        "questions_by_part": parts,
        "not_covered_by_the_plan": [turn["question"] for turn in turns if turn.get("source") == "off_plan"],
        "decision": session["decision"],
    }


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

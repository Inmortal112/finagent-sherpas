"""The chosen step as two calendar events (.ics). No network."""
import json
import re
from datetime import date

import pytest
from fastapi.testclient import TestClient

from finagent import ask, calendar_invite, server, voice

JOHNSON = "daniel-emily-johnson"
SESSION = {"session_id": "abc123", "decision": {"scene_id": "move_1", "title": "Add more life insurance",
                                                "plain_title": "Add more life insurance"}}


def _unfold(text: str) -> str:
    return text.replace("\r\n ", "")


def test_two_events_tomorrow_and_on_day_3():
    ics = calendar_invite.build(SESSION, date(2026, 11, 17), "https://example.test/families/x/complete/")
    assert ics.startswith("BEGIN:VCALENDAR\r\n") and ics.endswith("END:VCALENDAR\r\n")
    lines = _unfold(ics).split("\r\n")
    assert lines.count("BEGIN:VEVENT") == 2 and lines.count("END:VEVENT") == 2
    assert "DTSTART:20261117T100000" in lines          # tomorrow at 10:00, wherever they are
    assert "DTSTART:20261119T100000" in lines          # day 3 (chosen on the 16th)
    assert "SUMMARY:First step: add more life insurance" in lines
    assert "SUMMARY:Look at your home again" in lines
    assert "URL:https://example.test/families/x/complete/" in lines


def test_the_file_follows_the_standard():
    ics = calendar_invite.build(SESSION, date(2026, 11, 17), "https://example.test/" + "a" * 120)
    assert all(len(line.encode("utf-8")) <= 75 for line in ics.split("\r\n"))   # long lines are folded
    assert "\n" not in ics.replace("\r\n", "")                                 # only CRLF line ends
    description = next(line for line in _unfold(ics).split("\r\n") if line.startswith("DESCRIPTION:A few days"))
    assert "\\," in description or "," not in description.replace("\\,", "")   # commas escaped


def test_no_figures_and_no_step_no_file():
    ics = calendar_invite.build(SESSION, date(2026, 11, 17))
    text = " ".join(line for line in _unfold(ics).split("\r\n") if line.startswith(("SUMMARY", "DESCRIPTION")))
    assert not re.search(r"\d", text)
    assert calendar_invite.build({"session_id": "x", "decision": None}, date(2026, 11, 17)) is None


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("SESSIONS_DIR", str(tmp_path))
    server._recent_questions.clear()
    monkeypatch.setattr(ask, "_complete", lambda system, user: json.dumps({"scene": "intro", "answer": "Hello."}))

    async def speak(text, language="en"):
        return voice.SpokenAudio(b"mp3", 1.0, "test")

    monkeypatch.setattr(voice, "speak_async", speak)
    return TestClient(server.app)


def test_the_page_gets_the_calendar_once_a_step_is_chosen(client):
    session_id = client.post("/worry", json={"family": JOHNSON, "worry": "College", "mode": "simple"}).json()["session_id"]
    assert client.get(f"/calendar/{session_id}.ics").status_code == 404
    client.post("/decision", json={"family": JOHNSON, "scene_id": "move_1", "session_id": session_id})
    reply = client.get(f"/calendar/{session_id}.ics", params={"day": "2026-11-17"})
    assert reply.status_code == 200 and reply.headers["content-type"].startswith("text/calendar")
    body = _unfold(reply.text)
    assert "DTSTART:20261117T100000" in body and "First step: " in body
    assert f"/families/{JOHNSON}/simple/" in body
    assert client.get(f"/calendar/{session_id}.ics", params={"day": "tomorrow"}).status_code == 422
    assert client.get("/calendar/no-such-session.ics").status_code == 404


def test_the_link_back_opens_the_mode_the_family_is_using(client):
    session_id = client.post("/decision", json={"family": JOHNSON, "scene_id": "move_1"}).json()["session_id"]
    body = _unfold(client.get(f"/calendar/{session_id}.ics", params={"mode": "simple"}).text)
    assert f"/families/{JOHNSON}/simple/" in body
    assert client.get(f"/calendar/{session_id}.ics", params={"mode": "loud"}).status_code == 422

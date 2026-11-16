"""The home greets the family aloud when they come back. No network: the voice is faked."""
import json
import re
from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from finagent import ask, server, voice, welcome_back

JOHNSON = "daniel-emily-johnson"


def test_the_greeting_names_the_person_and_asks_about_their_step():
    due = {"due": [{"kind": "plan_date", "text": "Your plan has this coming up in June 2027: College."},
                   {"kind": "check_in", "text": "A few days ago you chose a first step: add more life insurance. "
                                                "Have you been able to start it?"}]}
    said = welcome_back.text({"person": "Emily"}, due)
    assert said.startswith("Welcome back, Emily. A few days ago you chose a first step: add more life insurance.")
    assert said.endswith("Your plan has this coming up in June 2027: College.")
    assert welcome_back.text({"person": None}, due).startswith("Welcome back. A few days ago")


def test_nothing_waiting_means_nothing_is_said():
    assert welcome_back.text({"person": "Emily"}, {"due": []}) is None


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("SESSIONS_DIR", str(tmp_path))
    server._recent_questions.clear()
    monkeypatch.setattr(ask, "_complete", lambda system, user: json.dumps(
        {"scene": "pillar_savings_and_cash_flow", "answer": "Your plumbing is cracked."}))
    spoken = []

    async def speak(text, language="en"):
        spoken.append(text)
        return voice.SpokenAudio(b"mp3", 1.0, "test")

    monkeypatch.setattr(voice, "speak_async", speak)
    test_client = TestClient(server.app)
    test_client.spoken = spoken
    return test_client


def test_the_page_gets_the_welcome_back_and_its_audio(client):
    session_id = client.post("/worry", json={"family": JOHNSON, "worry": "Paying for college",
                                             "person": "Emily"}).json()["session_id"]
    client.post("/decision", json={"family": JOHNSON, "scene_id": "move_1", "session_id": session_id})

    today = client.get("/reminders", params={"session_id": session_id}).json()
    assert "audio_url" not in today or not any(d["kind"] == "check_in" for d in today["due"])

    day = (date.today() + timedelta(days=4)).isoformat()
    back = client.get("/reminders", params={"session_id": session_id, "today": day}).json()
    assert back["spoken"].startswith("Welcome back, Emily. A few days ago you chose a first step: ")
    check_in = next(d["text"] for d in back["due"] if d["kind"] == "check_in")
    assert check_in in back["spoken"]
    # Nothing new is said: every figure spoken is already in the written reminders.
    written = " ".join(d["text"] for d in back["due"])
    assert set(re.findall(r"\d+", back["spoken"])) <= set(re.findall(r"\d+", written))

    audio = client.get(back["audio_url"])
    assert audio.status_code == 200 and audio.content == b"mp3" and audio.headers["content-type"] == "audio/mpeg"
    client.get(back["audio_url"])
    assert client.spoken == [back["spoken"]], "the second time it is played from the saved file"


def test_no_audio_without_a_session_or_without_reminders(client):
    assert client.get("/reminders/no-such-session.mp3").status_code == 404
    session_id = client.post("/worry", json={"family": "samantha-lewis", "worry": "College"}).json()["session_id"]
    quiet = client.get("/reminders", params={"session_id": session_id, "today": "2020-01-01"}).json()
    if not quiet["due"]:
        assert client.get(f"/reminders/{session_id}.mp3", params={"today": "2020-01-01"}).status_code == 404


def test_the_page_can_say_who_is_back_when_the_session_does_not_know(client):
    session_id = client.post("/decision", json={"family": JOHNSON, "scene_id": "move_1"}).json()["session_id"]
    day = (date.today() + timedelta(days=4)).isoformat()
    plain = client.get("/reminders", params={"session_id": session_id, "today": day}).json()
    assert plain["spoken"].startswith("Welcome back. ")
    named = client.get("/reminders", params={"session_id": session_id, "today": day, "person": "Daniel"}).json()
    assert named["spoken"].startswith("Welcome back, Daniel. ") and "person=Daniel" in named["audio_url"]
    assert client.get(named["audio_url"]).status_code == 200
    assert client.get("/reminders", params={"session_id": session_id, "person": "Nobody"}).status_code == 422

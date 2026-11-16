"""The voice note for the other half of a couple. No network: the model and the voice are replaced."""
import json
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from finagent import ask, brain, partner_note, server, voice

ROOT = Path(__file__).resolve().parents[1]
JOHNSON, WEAH, SAMANTHA, MICHAEL = "daniel-emily-johnson", "timothy-melanie-weah", "samantha-lewis", "michael-carter"


def _plan(family: str):
    return brain.build(json.loads((ROOT / "cases" / family / "financial-health.json").read_text(encoding="utf-8")))


def _session(**extra) -> dict:
    return {"session_id": "test-session", "family": JOHNSON, "person": "Daniel", "turns": [], "worries": [],
            "decision": {"scene_id": "move_1", "title": "Raise mortality coverage",
                         "plain_title": "Add more life insurance"},
            "follow_up": None, **extra}


def test_the_note_carries_the_worry_and_the_chosen_step_with_its_scores():
    note = partner_note.build(_session(worries=[{"text": "Paying for college"}]), _plan(JOHNSON))
    assert note["available"] and (note["from"], note["to"]) == ("Daniel", "Emily")
    assert note["text"] == (
        "Emily, Daniel just went through your family plan. Daniel's biggest worry: paying for college. "
        "The first step Daniel chose: add more life insurance. It takes your score from 52 to 57. "
        "Have a look at your part of the home when you have a moment. It's a plan for the two of you.")


def test_its_only_figures_are_the_steps_scores_from_the_plan():
    plan = _plan(JOHNSON)
    step = next(s for s in plan.scenes if s.id == "move_1")
    note = partner_note.build(_session(worries=[{"text": "We owe $18,000 at 24.9% and I can't sleep"}]), plan)
    figures = set(re.findall(r"\d+(?:[.,]\d+)*", note["text"]))
    assert figures == {str(step.visual.data["score_before"]), str(step.visual.data["score_after"])}
    assert "I can't sleep" in note["text"], "the worry stays, without its numbers"


def test_a_worry_with_a_number_in_words_is_left_out():
    note = partner_note.build(_session(worries=[{"text": "Losing fifty thousand in the market"}]), _plan(JOHNSON))
    assert "worry" not in note["text"] and "fifty" not in note["text"]


def test_each_adult_sends_it_to_the_other_one():
    session = _session(family=WEAH, person="melanie", decision={"scene_id": "move_1", "title": "x"})
    note = partner_note.build(session, _plan(WEAH))
    assert (note["from"], note["to"]) == ("Melanie", "Timothy")
    assert "pay down the credit card" in note["text"].lower()


def test_it_says_when_the_step_was_already_started():
    note = partner_note.build(_session(follow_up={"done": True}), _plan(JOHNSON))
    assert "Daniel has already started it." in note["text"]


@pytest.mark.parametrize("family", [SAMANTHA, MICHAEL])
def test_a_plan_for_one_person_has_no_note(family):
    note = partner_note.build(_session(family=family, person=None), _plan(family))
    assert not note["available"] and "one person" in note["reason"]


def test_no_note_without_a_step_or_without_knowing_who_sends_it():
    assert "first step" in partner_note.build(_session(decision=None), _plan(JOHNSON))["reason"]
    unknown = partner_note.build(_session(person=None), _plan(JOHNSON))
    assert not unknown["available"] and "Daniel or Emily" in unknown["reason"]
    assert partner_note.build(_session(person=None), _plan(JOHNSON), person="Emily")["to"] == "Daniel"


# --- server ----------------------------------------------------------------------------------------------------

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


def test_the_page_gets_the_note_and_its_audio(client):
    session_id = client.post("/worry", json={"family": JOHNSON, "worry": "Paying for college",
                                             "person": "Emily"}).json()["session_id"]
    first = client.get("/partner-note", params={"session_id": session_id}).json()
    assert not first["available"] and "first step" in first["reason"]

    client.post("/decision", json={"family": JOHNSON, "scene_id": "move_1", "session_id": session_id})
    note = client.get("/partner-note", params={"session_id": session_id}).json()
    assert note["available"] and note["text"].startswith("Daniel, Emily just went through your family plan.")
    audio = client.get(note["audio_url"])
    assert audio.status_code == 200 and audio.content == b"mp3"
    assert audio.headers["content-type"] == "audio/mpeg"
    client.get(note["audio_url"])
    assert client.spoken == [note["text"]], "the second time it is played from the saved file"


def test_the_audio_is_refused_when_there_is_no_note(client):
    session_id = client.post("/decision", json={"family": SAMANTHA, "scene_id": "move_1"}).json()["session_id"]
    assert client.get(f"/partner-note/{session_id}.mp3").status_code == 404
    assert client.get("/partner-note", params={"session_id": "no-such-session"}).status_code == 404

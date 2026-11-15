"""Live questions: the model only picks a scene and words; `guard` decides what the family hears. No network."""
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from finagent import ask, brain, server, sessions, voice

ROOT = Path(__file__).resolve().parents[1]
FAMILY = "samantha-lewis"


def _plan():
    diagnostic = json.loads((ROOT / "cases" / FAMILY / "financial-health.json").read_text(encoding="utf-8"))
    return brain.build(diagnostic), diagnostic


def _model(*replies):
    """A fake model that gives `replies` in order and remembers what it was sent."""
    calls, queue = [], list(replies)

    def complete(system, user):
        calls.append(json.loads(user))
        reply = queue.pop(0)
        if isinstance(reply, Exception):
            raise reply
        return json.dumps(reply)

    complete.calls = calls
    return complete


def test_an_answer_with_the_scene_facts_is_accepted():
    plan, diagnostic = _plan()
    model = _model({"scene": "timeline", "answer": "You plan to retire at 65 and your savings run out at age 73."})
    answer = ask.answer(plan, diagnostic, "  Why does my   garden dry up? ", model)
    assert (answer.source, answer.scene_id, answer.house_part) == ("model", "timeline", "garden")
    assert answer.question == "Why does my garden dry up?"
    assert "savings_run_out_age" in answer.fact_ids
    assert model.calls[0]["question"] == "Why does my garden dry up?"


def test_an_invented_number_gets_one_retry_and_then_the_approved_narration():
    plan, diagnostic = _plan()
    bad = {"scene": "pillar_debt", "answer": "You owe 123,456 dollars."}
    model = _model(bad, bad)
    answer = ask.answer(plan, diagnostic, "How much do I owe?", model)
    assert answer.source == "approved_narration"
    assert answer.text == next(s.narration for s in plan.scenes if s.id == "pillar_debt")
    assert "123,456" in model.calls[1]["rejected_because"]

    fixed = _model(bad, {"scene": "pillar_debt", "answer": "You have no debt: your balance is $0."})
    assert ask.answer(plan, diagnostic, "How much do I owe?", fixed).source == "model"


def test_a_figure_from_another_part_of_the_home_is_rejected():
    plan, diagnostic = _plan()
    wrong_part = {"scene": "pillar_debt", "answer": "Your $80,000 of cash covers 7.9 months."}
    assert ask.answer(plan, diagnostic, "Am I safe?", _model(wrong_part, wrong_part)).source == "approved_narration"


@pytest.mark.parametrize("reply", [{"scene": "off_plan", "answer": ""}, {"scene": "bitcoin", "answer": "Buy 3."}])
def test_what_the_plan_does_not_cover_gets_the_fixed_sentence(reply):
    plan, diagnostic = _plan()
    answer = ask.answer(plan, diagnostic, "Should I buy Bitcoin?", _model(reply))
    assert (answer.source, answer.scene_id, answer.text) == ("off_plan", None, ask.OFF_PLAN_ANSWER)


def test_a_model_failure_never_raises():
    plan, diagnostic = _plan()
    assert ask.answer(plan, diagnostic, "Hello?", _model(RuntimeError("no network"))).source == "unavailable"
    assert ask.answer(plan, diagnostic, "   ", _model()).source == "unavailable"


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("SESSIONS_DIR", str(tmp_path))
    server._recent_questions.clear()
    replies = iter([
        {"scene": "timeline", "answer": "Your savings run out at age 73."},
        {"scene": "off_plan", "answer": ""},
    ])
    monkeypatch.setattr(ask, "_complete", lambda system, user: json.dumps(next(replies)))

    spoken = []

    async def speak(text, language="en"):
        spoken.append(text)
        return voice.SpokenAudio(b"mp3-bytes" if "Bitcoin" not in text and text != ask.OFF_PLAN_ANSWER else None,
                                 2.5, "test")

    monkeypatch.setattr(voice, "speak_async", speak)
    test_client = TestClient(server.app)
    test_client.spoken = spoken
    return test_client


def test_ask_keeps_a_history_the_family_can_read_again(client):
    first = client.post("/ask", data={"family": FAMILY, "question": "Why does my garden dry up?"}).json()
    assert (first["scene_id"], first["house_part"], first["source"]) == ("timeline", "garden", "model")
    assert first["turn_id"] == "t1" and first["heard_from"] == "text"
    assert client.spoken == [], "the answer does not wait for the voice"
    assert client.get(first["audio_url"]).content == b"mp3-bytes"
    assert client.get(first["audio_url"]).content == b"mp3-bytes"
    assert client.spoken == ["Your savings run out at age 73."], "spoken once, then replayed from the file"

    session_id = first["session_id"]
    second = client.post("/ask", data={"family": FAMILY, "question": "Should I buy Bitcoin?",
                                       "session_id": session_id}).json()
    assert (second["session_id"], second["turn_id"], second["source"]) == (session_id, "t2", "off_plan")

    assert client.get(second["audio_url"]).status_code == 503, "no voice: the page shows the text"

    history = client.get("/history", params={"session_id": session_id}).json()
    assert [t["question"] for t in history["turns"]] == ["Why does my garden dry up?", "Should I buy Bitcoin?"]
    assert history["turns"][0]["text"] == "Your savings run out at age 73."
    assert history["turns"][0]["audio_url"] == first["audio_url"]

    chosen = client.post("/decision", json={"family": FAMILY, "scene_id": "move_1", "session_id": session_id})
    assert chosen.json()["decision"]["title"] == "Close a coverage gap"

    note = client.get("/advisor-note", params={"session_id": session_id}).json()
    assert note["asked_most_about"] == ["garden"]
    assert note["not_covered_by_the_plan"] == ["Should I buy Bitcoin?"]
    assert note["decision"]["scene_id"] == "move_1"


def test_a_spoken_question_is_transcribed_first(client, monkeypatch):
    async def transcribe(audio, filename="question.webm", language="en"):
        return voice.Transcript("Why does my garden dry up?" if audio == b"voice" else None, "test")

    monkeypatch.setattr(voice, "transcribe_async", transcribe)
    heard = client.post("/ask", data={"family": FAMILY}, files={"file": ("q.webm", b"voice", "audio/webm")}).json()
    assert (heard["question"], heard["heard_from"]) == ("Why does my garden dry up?", "voice")
    silence = client.post("/ask", data={"family": FAMILY}, files={"file": ("q.webm", b"...", "audio/webm")})
    assert silence.status_code == 422 and silence.json()["detail"] == server.NOT_HEARD


def test_bad_requests_are_refused(client):
    assert client.post("/ask", data={"family": "../etc", "question": "hi"}).status_code == 404
    assert client.get("/history", params={"session_id": "../../etc/passwd"}).status_code == 404
    assert client.get("/history", params={"session_id": "does-not-exist"}).status_code == 404
    assert client.post("/decision", json={"family": FAMILY, "scene_id": "intro"}).status_code == 422
    assert client.get("/answers/unknown-session/t1.mp3").status_code == 404


def test_the_team_test_page_is_served(client):
    page = client.get("/try")
    assert page.status_code == 200 and "/ask" in page.text and "/history" in page.text


def test_families_and_presentation(client):
    families = client.get("/families").json()
    assert len(families) == 4 and {"family", "client_name", "score", "band"} <= set(families[0])
    scenes = client.get(f"/presentation/{FAMILY}").json()["scenes"]
    assert scenes[0]["id"] == "intro" and scenes[0]["visual"]["data"]["house"]["garden"] == "cracked"


def test_a_session_id_from_another_family_starts_a_new_session(tmp_path, monkeypatch):
    monkeypatch.setenv("SESSIONS_DIR", str(tmp_path))
    first = sessions.start(FAMILY)
    sessions.add_turn(first, {"question": "q", "text": "a"})
    assert sessions.start(FAMILY, first["session_id"])["turns"][0]["question"] == "q"
    assert sessions.start("michael-carter", first["session_id"])["session_id"] != first["session_id"]
    assert sessions.start(FAMILY, "chosen-by-the-page")["session_id"] == "chosen-by-the-page"

"""Per person, two modes, the worry, reminders and the answer written little by little. No network."""
import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from finagent import ask, brain, guard, house, narrator, server, sessions, voice

ROOT = Path(__file__).resolve().parents[1]
CASES = sorted((ROOT / "cases").glob("*/financial-health.json"))
WEAH, SAMANTHA = "timothy-melanie-weah", "samantha-lewis"


def _load(family: str) -> dict:
    return json.loads((ROOT / "cases" / family / "financial-health.json").read_text(encoding="utf-8"))


# --- 5 · per person -------------------------------------------------------------------------------------------

def test_each_adult_of_a_couple_gets_their_own_part_of_the_home():
    plan = brain.build_template(_load(WEAH))
    facts = {f.id: f.value for f in plan.facts}
    assert [s.id for s in plan.scenes if s.id.startswith("person_")] == ["person_timothy", "person_melanie"]
    assert (facts["person_timothy_life_cover"], facts["person_timothy_life_shortfall"]) == (140000, 610000)
    assert (facts["person_melanie_life_cover"], facts["person_melanie_life_shortfall"]) == (110000, 490000)
    assert "Chase CC ($18,000 at 18%)" in facts["person_timothy_debts"]
    assert "person_melanie_debts" not in facts, "nothing is owed in Melanie's name"
    assert guard.unsupported_numbers(plan) == []


def test_one_adult_has_no_separate_part():
    assert not [s for s in brain.build_template(_load(SAMANTHA)).scenes if s.id.startswith("person_")]


def test_a_person_cannot_be_told_the_other_ones_figures():
    plan = brain.build_template(_load(WEAH))
    accepted, rejected = narrator.check(plan, {
        "person_melanie": "Melanie, you hold $110,000 of life insurance.",
        "person_timothy": "Timothy, you hold $110,000 of life insurance.",
    })
    assert list(accepted) == ["person_melanie"] and "110,000" in rejected["person_timothy"]


def test_the_question_says_who_is_asking_and_in_which_mode():
    seen = {}

    def model(system, user):
        seen.update(system=system, brief=json.loads(user))
        return json.dumps({"scene": "person_melanie", "answer": "Melanie, you hold $110,000 of life insurance."})

    diagnostic = _load(WEAH)
    answer = ask.answer(brain.build(diagnostic), diagnostic, "Is my insurance enough?", model,
                        mode="simple", person="Melanie")
    assert (answer.scene_id, answer.source) == ("person_melanie", "model")
    assert seen["brief"]["asked_by"] == "Melanie" and "Simple mode" in seen["system"]


# --- 6 · two modes --------------------------------------------------------------------------------------------

def test_simple_mode_uses_its_own_saved_narration(tmp_path):
    (tmp_path / f"{SAMANTHA}.json").write_text(json.dumps({
        "scenes": {"intro": "Hello Samantha. Your score is 82 out of 100, and Sherpas calls that strong."},
        "simple": {"intro": "Hello Samantha. Your home is strong: 82 out of 100."},
    }), encoding="utf-8")
    template = brain.build_template(_load(SAMANTHA))
    complete = narrator.apply_saved(template, SAMANTHA, tmp_path)
    simple = narrator.apply_saved(template, SAMANTHA, tmp_path, mode="simple")
    assert simple.scenes[0].narration == "Hello Samantha. Your home is strong: 82 out of 100."
    assert complete.scenes[0].narration != simple.scenes[0].narration
    assert [f.id for f in simple.facts] == [f.id for f in complete.facts], "same facts, other words"
    with pytest.raises(ValueError):
        brain.build(_load(SAMANTHA), mode="tiny")


@pytest.mark.parametrize("path", CASES, ids=lambda p: p.parent.name)
def test_every_family_has_an_accepted_simple_narration_that_is_shorter(path):
    diagnostic = json.loads(path.read_text(encoding="utf-8"))
    template = brain.build_template(diagnostic)
    saved = narrator.saved_texts(path.parent.name, "simple")
    accepted, rejected = narrator.check(template, saved)
    assert rejected == {} and set(accepted) == {s.id for s in template.scenes}
    simple, complete = brain.build(diagnostic, mode="simple"), brain.build(diagnostic)
    words = lambda plan: sum(len(s.narration.split()) for s in plan.scenes)  # noqa: E731
    assert words(simple) < 0.75 * words(complete)


# --- server: worry, reminders, stream, limits -----------------------------------------------------------------

@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("SESSIONS_DIR", str(tmp_path))
    server._recent_questions.clear()
    calls = []

    def model(system, user):
        brief = json.loads(user)
        calls.append({"system": system, "brief": brief})
        if "college" in brief["question"].lower():
            return json.dumps({"scene": "pillar_savings_and_cash_flow", "answer": "Your plumbing is solid."})
        return json.dumps({"scene": "timeline", "answer": "Timothy plans to retire at 62 and Melanie at 60."})

    monkeypatch.setattr(ask, "_complete", model)

    async def speak(text, language="en"):
        return voice.SpokenAudio(b"mp3", 1.0, "test")

    monkeypatch.setattr(voice, "speak_async", speak)
    test_client = TestClient(server.app)
    test_client.calls = calls
    return test_client


def _events(text: str) -> list[tuple[str, dict]]:
    # A block that starts with ":" is a comment (the padding that makes Safari show the first event at once).
    blocks = [block for block in text.split("\n\n") if block.strip() and not block.startswith(":")]
    return [(block.split("\n")[0].removeprefix("event: "), json.loads(block.split("\n")[1].removeprefix("data: ")))
            for block in blocks]


def test_the_answer_is_written_little_by_little_and_stays_in_the_history(client):
    reply = client.post("/ask/stream", data={"family": WEAH, "question": "When do we retire?", "pace_ms": 0})
    assert reply.headers["content-type"].startswith("text/event-stream")
    assert reply.text.startswith(":") and reply.text.index("event: thinking") > 1024, "padding first, for Safari"
    events = _events(reply.text)
    names = [name for name, _ in events]
    assert names[0] == "thinking" and names[1] == "turn" and names[-1] == "done"
    pieces = [data["text"] for name, data in events if name == "delta"]
    assert len(pieces) == 10, "one piece per word"
    done = events[-1][1]
    assert "".join(pieces) == done["text"] == "Timothy plans to retire at 62 and Melanie at 60."
    assert events[1][1]["scene_id"] == "timeline" and "text" not in events[1][1]
    history = client.get("/history", params={"session_id": done["session_id"]}).json()
    assert history["turns"][0]["text"] == done["text"], "they can read it again after it was spoken"


def test_the_worry_is_asked_first_and_reaches_the_advisor(client):
    turn = client.post("/worry", json={"family": WEAH, "worry": "  I am afraid we cannot pay for college ",
                                       "person": "Melanie", "mode": "simple"}).json()
    assert (turn["kind"], turn["house_part"]) == ("worry", "plumbing")
    assert client.calls[-1]["brief"]["asked_by"] == "Melanie" and "Simple mode" in client.calls[-1]["system"]
    session_id = turn["session_id"]
    client.post("/ask", data={"family": WEAH, "question": "When do we retire?", "session_id": session_id})
    assert "Simple mode" in client.calls[-1]["system"], "the session remembers the mode and the person"
    note = client.get("/advisor-note", params={"session_id": session_id}).json()
    assert note["worries"] == ["I am afraid we cannot pay for college"]
    assert note["questions"] == ["When do we retire?"]
    assert (note["person"], note["mode"]) == ("Melanie", "simple")
    assert client.post("/worry", json={"family": WEAH, "worry": "   "}).status_code == 422


def test_reminders_check_in_on_day_3_and_announce_the_plan_dates(client):
    session_id = client.post("/decision", json={"family": WEAH, "scene_id": "move_1"}).json()["session_id"]
    today = datetime.now(timezone.utc).date()

    def due(day):  # plan dates depend on the day the test runs: they are checked below with fixed dates
        reply = client.get("/reminders", params={"session_id": session_id, "today": day.isoformat()}).json()
        return {**reply, "due": [d for d in reply["due"] if d["kind"] != "plan_date"]}

    assert [d["kind"] for d in due(today + timedelta(days=2))["due"]] == []
    check_in = due(today + timedelta(days=3))["due"]
    assert [d["kind"] for d in check_in] == ["check_in"]
    assert "Pay down the credit card" in check_in[0]["text"] and check_in[0]["scene_id"] == "move_1"

    done = client.post("/follow-up", json={"session_id": session_id, "done": True}).json()
    assert done["repaired_house_part"] == "walls"
    assert due(today + timedelta(days=5))["due"] == [], "answered: no more check-ins"
    assert client.get("/advisor-note", params={"session_id": session_id}).json()["follow_up"]["done"] is True

    near = client.get("/reminders", params={"session_id": session_id, "today": "2029-11-15"}).json()
    assert [(d["kind"], d["date"]) for d in near["due"] if d["kind"] == "plan_date"] == [("plan_date", "2030-01-01")]
    assert "January 2030: Purchase a home" in near["due"][-1]["text"]
    assert near["upcoming"][0]["label"] == "January 2030"
    assert all(u["date"] >= "2029-11-15" for u in near["upcoming"])
    assert client.get("/reminders", params={"session_id": session_id, "today": "soon"}).status_code == 422


def test_not_yet_with_what_got_in_the_way_reaches_the_advisor(client):
    session_id = client.post("/decision", json={"family": WEAH, "scene_id": "move_3"}).json()["session_id"]
    reply = client.post("/follow-up", json={"session_id": session_id, "done": False,
                                            "note": "We haven't agreed yet"}).json()
    assert reply["repaired_house_part"] is None
    note = client.get("/advisor-note", params={"session_id": session_id}).json()
    assert note["follow_up"] == {**note["follow_up"], "done": False, "note": "We haven't agreed yet"}
    assert note["decision"]["title"] == "Add umbrella cover"            # Sherpas' words for the advisor
    assert note["decision"]["plain_title"] == "Add umbrella insurance"  # the family's words


def test_a_visit_without_a_step_gets_a_nudge_and_no_follow_up(client):
    session_id = client.post("/ask", data={"family": WEAH, "question": "When do we retire?"}).json()["session_id"]
    later = (datetime.now(timezone.utc).date() + timedelta(days=4)).isoformat()
    due = client.get("/reminders", params={"session_id": session_id, "today": later}).json()["due"]
    assert [d["kind"] for d in due if d["kind"] != "plan_date"] == ["no_step_yet"]
    assert client.post("/follow-up", json={"session_id": session_id, "done": True}).status_code == 422


def test_plan_dates_never_show_engine_markers():
    names = [d["name"] for d in house.plan_dates(_load(SAMANTHA))]
    assert names == ["Take a vacation", "College Ava", "Purchase a home", "Samantha's Retirement"]
    assert sessions.month_year("2028-08-01") == "August 2028"


def test_usage_caps_protect_the_team_credits(client, monkeypatch):
    monkeypatch.setenv("ASK_MAX_TURNS", "2")
    data = {"family": SAMANTHA, "question": "When do I retire?"}
    session_id = client.post("/ask", data=data).json()["session_id"]
    assert client.post("/ask", data={**data, "session_id": session_id}).status_code == 200
    refused = client.post("/ask", data={**data, "session_id": session_id})
    assert (refused.status_code, refused.json()["detail"]) == (429, server.TOO_MANY)

    monkeypatch.setenv("ASK_MAX_PER_MINUTE", "1")
    server._recent_questions.clear()
    assert client.post("/ask", data=data).status_code == 200
    busy = client.post("/ask/stream", data=data)
    assert (busy.status_code, busy.json()["detail"]) == (429, server.BUSY)


def test_mode_and_person_are_checked(client):
    assert client.get(f"/presentation/{SAMANTHA}", params={"mode": "tiny"}).status_code == 422
    assert client.post("/ask", data={"family": WEAH, "question": "hi", "person": "Samantha"}).status_code == 422
    people = {f["family"]: f["people"] for f in client.get("/families").json()}
    assert people[WEAH] == ["Timothy", "Melanie"] and people[SAMANTHA] == ["Samantha"]
    assert client.get("/chat").status_code == 200 and "/ask/stream" in client.get("/try").text

"""The conversation summary sent with each live question (escalabilidad.md). No network."""
import json
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from finagent import ask, brain, server, sessions

ROOT = Path(__file__).resolve().parents[1]
FAMILY = "samantha-lewis"
GARDEN = {"question": "Why does my garden dry up?", "text": "Your savings run out at age 73.",
          "scene_id": "timeline", "house_part": "garden", "source": "model", "kind": "question"}


def _plan():
    diagnostic = json.loads((ROOT / "cases" / FAMILY / "financial-health.json").read_text(encoding="utf-8"))
    return brain.build(diagnostic), diagnostic


def _model(*replies):
    """A fake model that gives `replies` in order and remembers the instructions and the message it got."""
    calls, queue = [], list(replies)

    def complete(system, user):
        calls.append((system, json.loads(user)))
        return json.dumps(queue.pop(0))

    complete.calls = calls
    return complete


@pytest.fixture
def session(tmp_path, monkeypatch):
    monkeypatch.setenv("SESSIONS_DIR", str(tmp_path))
    monkeypatch.delenv("ASK_HISTORY", raising=False)
    return sessions.start(FAMILY)


def test_a_new_session_has_no_context(session):
    assert sessions.context_for(session) is None


def test_the_context_keeps_the_last_turn_word_for_word_and_a_summary_without_figures(session):
    sessions.add_turn(session, {"question": "We owe $18,000 on a card at 18%, is that bad?", "text": "…",
                                "scene_id": "pillar_debt", "house_part": "walls", "source": "model",
                                "kind": "worry"})
    sessions.add_worry(session, "We owe $18,000 on a card at 18%, is that bad?", "walls")
    sessions.add_turn(session, dict(GARDEN))
    sessions.add_turn(session, dict(GARDEN, question="And when exactly?"))
    sessions.decide(session, "move_1", "Pay $6,800 on the card")

    context = sessions.context_for(session)
    assert context["previous"] == {"question": "And when exactly?", "answer": "Your savings run out at age 73.",
                                   "scene": "timeline", "house_part": "garden"}
    assert context["asked_most_about"] == ["garden", "walls"]
    summary = json.dumps({key: value for key, value in context.items() if key != "previous"})
    assert not re.search(r"\d", summary), "the summary carries no figures"
    assert "an amount" in context["worries"][0] and "an amount" in context["chosen_step"]


def test_the_context_does_not_grow_with_the_session(session):
    for number in range(30):
        sessions.add_turn(session, dict(GARDEN, question=f"Question {number}? " + "word " * 200))
        sessions.add_worry(session, f"Worry {number}", "garden")
    short = sessions.start(FAMILY)
    sessions.add_turn(short, dict(GARDEN))
    long_size, short_size = (len(json.dumps(sessions.context_for(s))) for s in (session, short))
    assert long_size < short_size + 3 * 40 + sessions.CONTEXT_CHARS
    assert len(sessions.context_for(session)["worries"]) == sessions.CONTEXT_ITEMS


def test_an_answer_that_was_not_given_is_not_repeated_as_context(session):
    sessions.add_turn(session, {"question": "Should I buy Bitcoin?", "text": ask.OFF_PLAN_ANSWER,
                                "scene_id": None, "house_part": None, "source": "off_plan"})
    assert sessions.context_for(session)["previous"] == {"question": "Should I buy Bitcoin?"}


def test_history_can_be_switched_off(session, monkeypatch):
    sessions.add_turn(session, dict(GARDEN))
    monkeypatch.setenv("ASK_HISTORY", "off")
    assert sessions.context_for(session) is None


def test_the_first_question_is_sent_exactly_as_before():
    plan, diagnostic = _plan()
    model = _model({"scene": "timeline", "answer": "Your savings run out at age 73."})
    ask.answer(plan, diagnostic, "Why does my garden dry up?", model)
    system, message = model.calls[0]
    assert system == ask.SYSTEM_PROMPT and "conversation" not in message


def test_a_follow_up_question_carries_the_conversation(session):
    plan, diagnostic = _plan()
    sessions.add_turn(session, dict(GARDEN))
    model = _model({"scene": "timeline", "answer": "You plan to retire at 65."})
    answer = ask.answer(plan, diagnostic, "and when do I stop working?", model,
                        context=sessions.context_for(session))
    system, message = model.calls[0]
    assert answer.source == "model"
    assert message["conversation"]["previous"]["question"] == "Why does my garden dry up?"
    assert system.endswith(ask.CONVERSATION) and "never a source" in system


def test_a_figure_from_the_previous_answer_is_still_rejected_in_another_scene(session):
    plan, diagnostic = _plan()
    sessions.add_turn(session, dict(GARDEN))
    echo = {"scene": "pillar_debt", "answer": "As I said, your savings run out at age 73."}
    answer = ask.answer(plan, diagnostic, "and my debt?", _model(echo, echo), context=sessions.context_for(session))
    assert answer.source == "approved_narration", "guard still decides, with or without context"


def test_two_questions_in_one_session_reach_the_model_with_the_first_one(tmp_path, monkeypatch):
    monkeypatch.setenv("SESSIONS_DIR", str(tmp_path))
    monkeypatch.delenv("ASK_HISTORY", raising=False)
    server._recent_questions.clear()
    sent = []
    replies = iter([{"scene": "timeline", "answer": "Your savings run out at age 73."},
                    {"scene": "move_1", "answer": "Your plan's first step closes a coverage gap."}])

    def complete(system, user):
        sent.append(json.loads(user))
        return json.dumps(next(replies))

    monkeypatch.setattr(ask, "_complete", complete)
    client = TestClient(server.app)
    first = client.post("/ask", data={"family": FAMILY, "question": "Why does my garden dry up?"}).json()
    second = client.post("/ask", data={"family": FAMILY, "question": "and what can I do about it?",
                                       "session_id": first["session_id"]}).json()
    assert "conversation" not in sent[0]
    assert sent[1]["conversation"]["previous"] == {"question": "Why does my garden dry up?",
                                                   "answer": "Your savings run out at age 73.", "scene": "timeline",
                                                   "house_part": "garden"}
    assert sent[1]["conversation"]["asked_most_about"] == ["garden"]
    assert (second["turn_id"], second["scene_id"]) == ("t2", "move_1")

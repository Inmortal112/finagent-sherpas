"""Backend (owner: A). Live questions, their history, reminders and the advisor's note. Keys stay here.

    PYTHONPATH=src:. .venv/bin/uvicorn finagent.server:app --host 0.0.0.0 --port 8000

    GET  /families                      the families that can be opened, with the adults of each
    GET  /presentation/{family}?mode=   facts and scenes of one family (the contract's Presentation)
    POST /ask                           one question, typed (`question`) or spoken (`file`) -> the answer, at once
    POST /ask/stream                    the same, but the answer arrives piece by piece (server-sent events)
    POST /worry                         what worries them, asked before the tour starts
    GET  /history?session_id=...        every question and answer of one session, oldest first
    POST /decision                      the step the family chose
    GET  /reminders?session_id=&today=  what to say when they come back: day-3 check-in and the plan's dates
    GET  /reminders/{session}.mp3       the same, spoken: "Welcome back, Daniel. A few days ago you chose..."
    POST /follow-up                     their answer to the check-in: did they take the step?
    GET  /advisor-note?session_id=...   what worries them, what they asked, what they chose
    GET  /answers/{session}/{turn}.mp3  that answer spoken (made on the first request, then kept)
    GET  /partner-note?session_id=&person=  a short note for the other half of a couple: worry and chosen step
    GET  /partner-note/{session}.mp3?person=  that note spoken, to send like a voice message
    GET  /chat                          a plain chat page for the team (also /try)
    /                                   the page in out/, when it exists

`mode` is "complete" or "simple"; `person` is the adult using it when the plan belongs to a couple.
"""
import asyncio
import hashlib
import json
import os
import re
import time
from collections import deque
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import quote

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from contracts.schemas import Presentation
from finagent import ask, brain, house, partner_note, sessions, voice, welcome_back

ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "cases"
NOT_HEARD = "I could not hear the question. Please try again, or type it."
TOO_MANY = "That is a lot of questions for one visit. Your advisor can take it from here."
BUSY = "Many people are asking right now. Please try again in a minute."
WORD = re.compile(r"\S+\s*")

app = FastAPI(title="Under One Roof")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
_recent_questions: deque[float] = deque()  # times of the last model calls, for the per-minute cap


class Decision(BaseModel):
    family: str
    scene_id: str
    session_id: str | None = None


class Worry(BaseModel):
    family: str
    worry: str
    session_id: str | None = None
    person: str | None = None
    mode: str | None = None


class FollowUp(BaseModel):
    session_id: str
    done: bool
    note: str | None = None


def _diagnostic(family: str) -> dict:
    path = CASES / family / "financial-health.json"
    if not family.replace("-", "").isalnum() or not path.exists():
        raise HTTPException(404, f"Unknown family: {family}")
    return json.loads(path.read_text(encoding="utf-8"))


def _mode(mode: str | None) -> str:
    if mode in (None, ""):
        return "complete"
    if mode not in brain.MODES:
        raise HTTPException(422, f"mode must be one of {list(brain.MODES)}")
    return mode


def _person(diagnostic: dict, person: str | None) -> str | None:
    if not person:
        return None
    names = [p["first_name"] for p in house.adults(diagnostic)]
    if person not in names:
        raise HTTPException(422, f"person must be one of {names}")
    return person


def _session(session_id: str | None) -> dict:
    session = sessions.load(session_id) if session_id else None
    if session is None:
        raise HTTPException(404, "Unknown session")
    return session


def _allow_question(session: dict) -> None:
    """Caps on model calls, so a shared link cannot spend the team's credits."""
    if len(session["turns"]) >= sessions.max_turns():
        raise HTTPException(429, TOO_MANY)
    now, per_minute = time.monotonic(), int(os.getenv("ASK_MAX_PER_MINUTE") or 30)
    while _recent_questions and now - _recent_questions[0] > 60:
        _recent_questions.popleft()
    if len(_recent_questions) >= per_minute:
        raise HTTPException(429, BUSY)
    _recent_questions.append(now)


async def _prepare(family: str, question: str | None, session_id: str | None, file: UploadFile | None,
                   mode: str | None, person: str | None) -> tuple[dict, Presentation, dict, str, str]:
    """Everything that can refuse a question, before any model call: (diagnostic, plan, session, question, heard_from)."""
    diagnostic = _diagnostic(family)
    person = _person(diagnostic, person)
    session = sessions.start(family, session_id, person, mode and _mode(mode))
    plan = brain.build(diagnostic, mode=_mode(session["mode"]))
    heard_from = "text"
    if not (question or "").strip() and file is not None:
        heard = await voice.transcribe_async(await file.read(), file.filename or "question.webm")
        question, heard_from = heard.text, "voice"
    if not (question or "").strip():
        raise HTTPException(422, NOT_HEARD)
    _allow_question(session)
    return diagnostic, plan, session, question, heard_from


async def _answer(diagnostic: dict, plan: Presentation, session: dict, question: str, heard_from: str,
                  kind: str = "question") -> dict:
    """Ask the model, keep the turn in the history and return it. The audio is made later, on request."""
    answer = await asyncio.to_thread(ask.answer, plan, diagnostic, question, None,
                                     _mode(session["mode"]), session["person"], sessions.context_for(session))
    turn = sessions.add_turn(session, {**answer.as_dict(), "kind": kind, "heard_from": heard_from,
                                       "language": plan.language})
    turn["audio_url"] = f"/answers/{session['session_id']}/{turn['turn_id']}.mp3"
    sessions.save(session)
    return {"session_id": session["session_id"], **turn}


# Safari (every browser on an iPhone) holds back the start of a streamed reply until about 1 KB has arrived, so
# the first small event would only show up together with the answer, seconds later. A comment line of that size,
# which the page ignores, makes it hand over what follows straight away.
STREAM_PADDING = ":" + " " * 2048 + "\n\n"


def _event(name: str, data: dict) -> str:
    return f"event: {name}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@app.get("/healthz", include_in_schema=False)
def healthz() -> dict:
    return {"ok": True}


@app.get("/families")
def families() -> list[dict]:
    result = []
    for path in sorted(CASES.glob("*/financial-health.json")):
        diagnostic = json.loads(path.read_text(encoding="utf-8"))
        result.append({"family": path.parent.name,
                       "client_name": brain._client_name(diagnostic["case"]["household"]),
                       "people": [p["first_name"] for p in house.adults(diagnostic)],
                       "score": diagnostic["score"]["published_score"], "band": diagnostic["score"]["band"]})
    return result


@app.get("/presentation/{family}")
def presentation(family: str, mode: str | None = None) -> dict:
    return brain.build(_diagnostic(family), mode=_mode(mode)).model_dump()


@app.post("/ask")
async def ask_question(family: str = Form(...), question: str | None = Form(None),
                       session_id: str | None = Form(None), file: UploadFile | None = File(None),
                       mode: str | None = Form(None), person: str | None = Form(None)) -> dict:
    return await _answer(*await _prepare(family, question, session_id, file, mode, person))


@app.post("/ask/stream")
async def ask_stream(family: str = Form(...), question: str | None = Form(None),
                     session_id: str | None = Form(None), file: UploadFile | None = File(None),
                     mode: str | None = Form(None), person: str | None = Form(None),
                     pace_ms: int = Form(90)) -> StreamingResponse:
    """The answer, written little by little. Events: `thinking`, `turn` (where the home turns), `delta`
    (a few words each), `done` (the whole turn, as /ask returns it).

    Only text that `guard` has already accepted is streamed: the model's words are never shown as they
    come out, because an invented figure would be on screen before it could be stopped.
    """
    prepared = await _prepare(family, question, session_id, file, mode, person)
    pace = min(max(pace_ms, 0), 400) / 1000

    async def events():
        yield STREAM_PADDING
        yield _event("thinking", {"session_id": prepared[2]["session_id"], "question": prepared[3]})
        turn = await _answer(*prepared)
        yield _event("turn", {key: value for key, value in turn.items() if key != "text"})
        for piece in WORD.findall(turn["text"]):
            yield _event("delta", {"text": piece})
            if pace:
                await asyncio.sleep(pace)
        yield _event("done", turn)

    return StreamingResponse(events(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.post("/worry")
async def worry(body: Worry) -> dict:
    """What worries them, before the tour. The home turns to the part of the plan that speaks to it."""
    text = " ".join(body.worry.split())
    if not text:
        raise HTTPException(422, "Tell us what worries you, in your own words.")
    diagnostic, plan, session, text, heard_from = await _prepare(
        body.family, text, body.session_id, None, body.mode, body.person)
    turn = await _answer(diagnostic, plan, session, text, heard_from, kind="worry")
    sessions.add_worry(session, text, turn["house_part"])
    return turn


@app.get("/history")
def history(session_id: str) -> dict:
    session = _session(session_id)
    return {"session_id": session["session_id"], "family": session["family"], "person": session.get("person"),
            "mode": session.get("mode"), "started": session["started"], "worries": session.get("worries", []),
            "turns": session["turns"], "decision": session["decision"], "follow_up": session.get("follow_up")}


@app.post("/decision")
def decision(body: Decision) -> dict:
    plan = brain.build(_diagnostic(body.family))
    scene = next((s for s in plan.scenes if s.id == body.scene_id and s.id.startswith("move_")), None)
    if scene is None:
        raise HTTPException(422, f"{body.scene_id} is not a step of this plan")
    session = sessions.start(body.family, body.session_id)
    session["follow_up"] = None  # a new choice gets its own check-in
    return {"session_id": session["session_id"], "decision": sessions.decide(session, scene.id, scene.title,
                                                                                 scene.visual.data.get("plain_title")),
            "house_part": scene.visual.data.get("house_part")}


@app.get("/reminders")
def reminders(session_id: str, today: str | None = None, person: str | None = None) -> dict:
    """What to say when the family comes back. `today` (YYYY-MM-DD) lets the demo travel in time.
    `person` is who is on the page, for the greeting, when the session does not know it yet."""
    session = _session(session_id)
    name = session.get("person") or _person(_diagnostic(session["family"]), person)
    try:
        day = date.fromisoformat(today) if today else datetime.now(timezone.utc).date()
    except ValueError:
        raise HTTPException(422, "today must look like 2026-11-18") from None
    due = sessions.reminders(session, _diagnostic(session["family"]), day)
    spoken = welcome_back.text({"person": name}, due)
    if spoken:  # the same reminders, said aloud by the home: GET /reminders/{session}.mp3
        due["spoken"] = spoken
        due["audio_url"] = (f"/reminders/{session['session_id']}.mp3?today={day.isoformat()}"
                            + (f"&person={quote(name)}" if name else ""))
    return due


@app.get("/reminders/{session_id}.mp3")
async def reminders_audio(session_id: str, today: str | None = None, person: str | None = None) -> FileResponse:
    """The welcome back, spoken. It only ever says this session's own reminders, and each text is made once."""
    due = reminders(session_id, today, person)
    if "spoken" not in due:
        raise HTTPException(404, "Nothing is waiting for this family yet")
    digest = hashlib.sha256(due["spoken"].encode("utf-8")).hexdigest()[:12]
    path = sessions.directory() / "audio" / f"{session_id}-back-{digest}.mp3"
    if not path.exists():
        spoken = await voice.speak_async(due["spoken"])
        if not spoken.audio:
            raise HTTPException(503, "The voice is not available right now; show the text")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(spoken.audio)
    return FileResponse(path, media_type="audio/mpeg")


@app.post("/follow-up")
def follow_up(body: FollowUp) -> dict:
    session = _session(body.session_id)
    if not session["decision"]:
        raise HTTPException(422, "No step has been chosen in this session yet")
    plan = brain.build(_diagnostic(session["family"]))
    scene = next(s for s in plan.scenes if s.id == session["decision"]["scene_id"])
    return {"session_id": session["session_id"], "follow_up": sessions.follow_up(session, body.done, body.note),
            # the part of the home the page can now draw as repaired
            "repaired_house_part": scene.visual.data.get("house_part") if body.done else None}


@app.get("/advisor-note")
def advisor_note(session_id: str) -> dict:
    return sessions.advisor_note(_session(session_id))


@app.get("/partner-note")
def partner_note_text(session_id: str, person: str | None = None) -> dict:
    """The note from the visitor to their partner. `available` is False, with a `reason`, when there is none:
    a plan for one person, no step chosen yet, or no way to tell who is sending it."""
    session = _session(session_id)
    note = partner_note.build(session, brain.build(_diagnostic(session["family"])), person)
    if note["available"]:
        query = f"?person={note['from']}"
        note["audio_url"] = f"/partner-note/{session['session_id']}.mp3{query}"
    return {"session_id": session["session_id"], **note}


@app.get("/partner-note/{session_id}.mp3")
async def partner_note_audio(session_id: str, person: str | None = None) -> FileResponse:
    """The partner note spoken. Kept per text, so a new step or a new answer to the check-in makes a new one."""
    session = _session(session_id)
    note = partner_note.build(session, brain.build(_diagnostic(session["family"])), person)
    if not note["available"]:
        raise HTTPException(404, note["reason"])
    digest = hashlib.sha256(note["text"].encode("utf-8")).hexdigest()[:12]
    path = sessions.directory() / "audio" / f"{session['session_id']}-partner-{digest}.mp3"
    if not path.exists():
        spoken = await voice.speak_async(note["text"])
        if not spoken.audio:
            raise HTTPException(503, "The voice is not available right now; send the text instead")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(spoken.audio)
    return FileResponse(path, media_type="audio/mpeg", filename=f"note-for-{note['to'].lower()}.mp3")


@app.get("/answers/{session_id}/{turn_id}.mp3")
async def spoken_answer(session_id: str, turn_id: str) -> FileResponse:
    """The answer of one turn, spoken. Made on the first request and kept, so the history can replay it."""
    session = sessions.load(session_id)
    turn = next((t for t in session["turns"] if t["turn_id"] == turn_id), None) if session else None
    if turn is None:
        raise HTTPException(404, "No such answer")
    path = sessions.audio_path(session_id, turn_id)
    if not path.exists():
        spoken = await voice.speak_async(turn["text"], turn.get("language", "en"))
        if not spoken.audio:
            raise HTTPException(503, "The voice is not available right now; show the text")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(spoken.audio)
    return FileResponse(path, media_type="audio/mpeg")


@app.get("/chat", include_in_schema=False)
@app.get("/try", include_in_schema=False)
def chat_page() -> FileResponse:
    """A plain chat page to try the backend by hand. Not the product: that is the stage's page."""
    return FileResponse(Path(__file__).with_name("chat_page.html"), media_type="text/html")


# What the page loads when asked for the home in 3D (?house=3d): house3d.js and three.js, kept in the repo.
app.mount("/web", StaticFiles(directory=Path(__file__).with_name("web")), name="web")

if (ROOT / "out").is_dir():  # last, so it never hides the routes above
    app.mount("/", StaticFiles(directory=ROOT / "out", html=True), name="page")

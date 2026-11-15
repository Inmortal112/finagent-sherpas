"""Backend (owner: A). Live questions, their history and the advisor's note. Keys stay here, never in the page.

    PYTHONPATH=src:. .venv/bin/uvicorn finagent.server:app --port 8000

    GET  /families                      the families that can be opened
    GET  /presentation/{family}         facts and scenes of one family (the contract's Presentation)
    POST /ask                           one question, typed (`question`) or spoken (`file`) -> the answer, at once
    GET  /history?session_id=...        every question and answer of one session, oldest first
    POST /decision                      the step the family chose
    GET  /advisor-note?session_id=...   what they asked, what the plan did not cover, what they chose
    GET  /answers/{session}/{turn}.mp3  that answer spoken (made on the first request, then kept)
    /                                   the page in out/, when it exists
"""
import asyncio
import json
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from finagent import ask, brain, sessions, voice

ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "cases"
NOT_HEARD = "I could not hear the question. Please try again, or type it."

app = FastAPI(title="Under One Roof")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class Decision(BaseModel):
    family: str
    scene_id: str
    session_id: str | None = None


def _family(family: str) -> tuple[dict, "brain.Presentation"]:
    path = CASES / family / "financial-health.json"
    if not family.replace("-", "").isalnum() or not path.exists():
        raise HTTPException(404, f"Unknown family: {family}")
    diagnostic = json.loads(path.read_text(encoding="utf-8"))
    return diagnostic, brain.build(diagnostic)


def _session(session_id: str | None) -> dict:
    session = sessions.load(session_id) if session_id else None
    if session is None:
        raise HTTPException(404, "Unknown session")
    return session


@app.get("/families")
def families() -> list[dict]:
    result = []
    for path in sorted(CASES.glob("*/financial-health.json")):
        diagnostic = json.loads(path.read_text(encoding="utf-8"))
        result.append({"family": path.parent.name,
                       "client_name": brain._client_name(diagnostic["case"]["household"]),
                       "score": diagnostic["score"]["published_score"], "band": diagnostic["score"]["band"]})
    return result


@app.get("/presentation/{family}")
def presentation(family: str) -> dict:
    return _family(family)[1].model_dump()


@app.post("/ask")
async def ask_question(family: str = Form(...), question: str | None = Form(None),
                       session_id: str | None = Form(None), file: UploadFile | None = File(None)) -> dict:
    diagnostic, plan = _family(family)
    heard_from = "text"
    if not (question or "").strip() and file is not None:
        heard = await voice.transcribe_async(await file.read(), file.filename or "question.webm")
        question, heard_from = heard.text, "voice"
    if not (question or "").strip():
        raise HTTPException(422, NOT_HEARD)

    answer = await asyncio.to_thread(ask.answer, plan, diagnostic, question)
    session = sessions.start(family, session_id)
    turn = sessions.add_turn(session, {**answer.as_dict(), "heard_from": heard_from, "language": plan.language})
    # The text goes back at once; the audio is made when the page asks for it (see spoken_answer).
    turn["audio_url"] = f"/answers/{session['session_id']}/{turn['turn_id']}.mp3"
    sessions.save(session)
    return {"session_id": session["session_id"], **turn}


@app.get("/history")
def history(session_id: str) -> dict:
    session = _session(session_id)
    return {"session_id": session["session_id"], "family": session["family"], "started": session["started"],
            "turns": session["turns"], "decision": session["decision"]}


@app.post("/decision")
def decision(body: Decision) -> dict:
    _, plan = _family(body.family)
    scene = next((s for s in plan.scenes if s.id == body.scene_id and s.id.startswith("move_")), None)
    if scene is None:
        raise HTTPException(422, f"{body.scene_id} is not a step of this plan")
    session = sessions.start(body.family, body.session_id)
    return {"session_id": session["session_id"], "decision": sessions.decide(session, scene.id, scene.title)}


@app.get("/advisor-note")
def advisor_note(session_id: str) -> dict:
    return sessions.advisor_note(_session(session_id))


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


if (ROOT / "out").is_dir():  # last, so it never hides the routes above
    app.mount("/", StaticFiles(directory=ROOT / "out", html=True), name="page")

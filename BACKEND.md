# Backend: live questions, history, reminders and the advisor's note

The part of Under One Roof that runs on a server (`src/finagent/server.py`, FastAPI). It keeps the keys, answers
the family's questions with the facts of their own plan, remembers the conversation and tells the advisor what
happened. The page (the stage) only calls these routes.

```
question (typed or spoken) ─▶ transcribe ─▶ model picks a scene and answers ─▶ guard ─▶ text, then voice
                                                                                └─▶ history ─▶ advisor's note
```

## Run it

```bash
pip install -r requirements.txt
scripts/serve.sh            # http://localhost:8000/chat, and the address for a phone on the same Wi-Fi
scripts/share.sh            # a temporary public https link (cloudflared if installed, else localhost.run; no account)
```

`/chat` is a plain page for the team: it asks the worry first, writes each answer little by little, plays it,
keeps the earlier questions, and has the steps, the "come back in 3 days" check-in and the advisor's note.
A phone's microphone only works over https, so use the `share.sh` link for hold-to-talk.

To host it for longer, the `Dockerfile` runs the same server on any host that takes a container (Render, Fly,
Railway): set `TEAM_KEY`, `LLM_PROXY_URL` and the voice keys in the host's settings, never in the image.
Sessions are files in `data/sessions/`, so a host without a disk forgets them on restart.

## Routes

| Route | What it does |
|---|---|
| `GET /families` | The four families: name, adults, score and band |
| `GET /presentation/{family}?mode=` | Facts and scenes (the contract's `Presentation`) in `complete` or `simple` mode |
| `POST /ask` | Form: `family`, `question` or `file` (a recording), `session_id`, `mode`, `person` → the answer |
| `POST /ask/stream` | Same form (+ `pace_ms`) → the answer piece by piece, as server-sent events |
| `POST /worry` | JSON `{family, worry, session_id?, person?, mode?}`: what worries them, before the tour |
| `GET /history?session_id=` | Every question and answer of the session, oldest first, to read them again |
| `POST /decision` | JSON `{family, scene_id, session_id?}`: the step they chose (`move_N`) |
| `GET /reminders?session_id=&today=` | What to say when they come back; `today` (YYYY-MM-DD) travels in time |
| `POST /follow-up` | JSON `{session_id, done, note?}`: did they take the step? → the part of the home to repair |
| `GET /advisor-note?session_id=` | Worries, questions, most asked parts, what the plan did not cover, the step, the follow-up |
| `GET /answers/{session}/{turn}.mp3` | That answer spoken; made on the first request, then kept (503: show the text) |

An answer (`/ask`, `/worry`, and the `done` event of `/ask/stream`):

```json
{"session_id": "…", "turn_id": "t1", "asked_at": "2026-11-15T10:44:42+00:00", "kind": "question",
 "question": "Why does my garden dry up?", "text": "Your savings and investments run out at age 73…",
 "scene_id": "timeline", "house_part": "garden", "fact_ids": ["savings_run_out_age", "…"],
 "source": "model", "heard_from": "text", "audio_url": "/answers/…/t1.mp3"}
```

`scene_id` and `house_part` say where the home turns. `source` is `model`, `approved_narration` (the model's answer
was rejected twice, so the family hears the narration already approved for that scene), `off_plan` (the plan does
not cover it: a fixed sentence, and the question is kept for the advisor) or `unavailable`.

`/ask/stream` sends `thinking` (at once, with the question as it was heard), `turn` (the answer without its text:
turn the home now), one `delta` per word, and `done` (the whole answer). Keep the `session_id` and send it every time.

## What keeps the answers honest

- **Only the plan's figures.** The model chooses one scene and may only use numbers that appear in that scene's
  facts. `guard` checks the answer; numbers written in words are rejected too. One retry, then the approved narration.
- **Nothing is shown before it is checked.** The text written little by little is the text `guard` already accepted,
  sent word by word. The model's own stream never reaches the page.
- **A figure stays in its part of the home.** Cash figures cannot be quoted in the debt scene, and one adult's
  cover cannot be said to the other.
- **Outside the plan** (crypto, predictions, new advice): a fixed sentence without figures.

## It remembers the conversation

The model has no memory, so from the second question on the server sends a short summary of the session with
each question (`sessions.context_for`): what worries them, the parts of the home they asked about most, the
step they chose (all without figures), and the previous question and answer word for word. So "and what can I
do about it?" stays on the part of the home they were asking about. The summary is the same size however long
the conversation is, so a long session does not cost more per question. It is background, never a source:
`guard` still rejects a figure that is not in the chosen scene's facts. `ASK_HISTORY=off` turns it off.

## Per person and per mode

- In a couple, each adult has their own scene (`person_<name>`): salary, the accounts and debts in their name and
  their life cover against the recommended range. Send `person` and the answers speak to them by name.
- `mode=simple` gives shorter sentences with one figure at most, both in the narration (saved in `narrations/`)
  and in the answers. The session remembers the mode and the person.

## Reminders

Nothing is sent. The page asks `/reminders` when the family comes back, and gets fixed sentences (no model):
a check-in three days after they chose a step, a nudge if they chose none, and the plan's own dates when they are
within 90 days, said as month and year. `today` lets a demo jump ahead.

## Limits and costs

- `ASK_MAX_TURNS` (40 per session) and `ASK_MAX_PER_MINUTE` (30 for everyone) refuse with 429 and a kind sentence.
- Models: `ASK_MODEL=deepseek-flash`, fallback `ASK_FALLBACK_MODEL=gemini-3.5-flash-lite` after 8 s. Measured:
  an answer in 2.6 to 4.4 s, well under a cent each. `gpt-5-mini` took 11 to 28 s, so it only writes the narration.
- The answer does not wait for the voice: the mp3 is made when the page asks for it.
- Spoken questions: ElevenLabs Scribe first; if it fails, `gemini-3.5-flash-lite` listens to the recording through
  the proxy (`voice_stt_model.py`, 1.3 to 2.4 s). A whole spoken question was answered in 4.9 s.

## Files and tests

| File | What |
|---|---|
| `src/finagent/server.py` | the routes |
| `src/finagent/ask.py` | question → scene and answer, checked by `guard` |
| `src/finagent/sessions.py` | history, worries, decision, follow-up, reminders, advisor's note |
| `src/finagent/chat_page.html` | the `/chat` page |
| `tests/test_ask.py`, `tests/test_family_experience.py`, `tests/test_ask_context.py` | all of the above, with a fake model: no network, no cost |

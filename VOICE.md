# Voice — how the house speaks and listens

The voice stage turns the plan into speech and the family's spoken questions into text.
It works **out of the box with no key** (free voices); add an ElevenLabs key for the demo voice.

```
brain ─▶ guard ─▶ VOICE ─▶ stage                       presentation: one MP3 per scene
                    ▲
/ask:  question (mic) ─▶ transcribe ─▶ LLM ─▶ guard ─▶ speak ─▶ MP3 back to the page
```

| What | Function | In | Out |
|---|---|---|---|
| Narrate the presentation | `voice.synthesize(presentation, out_dir)` | `Presentation` | the same, with `audio_path` and `duration_s` per scene |
| Say one answer (`/ask`) | `await voice.speak_async(text)` | text | `SpokenAudio(audio, duration_s, engine)`: MP3 bytes |
| Hear one question (`/ask`) | `await voice.transcribe_async(audio, filename)` | browser recording | `Transcript(text, engine)` |

`narration` is never changed: the engines read a spoken copy of it (see *Reading numbers aloud*).
None of these functions raises on a voice failure: the presentation falls back to estimated durations,
`speak` returns `audio=None` and `transcribe` returns `text=None`, so the page can show or ask for text.

## Run it

**No key needed** (free Microsoft Edge voices, needs internet):

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
PYTHONPATH=src:. .venv/bin/python -m finagent.run cases/samantha-lewis/financial-health.json
```

Windows (PowerShell):

```powershell
python -m venv .venv; .venv\Scripts\pip install -r requirements.txt
$env:PYTHONPATH="src;."; .venv\Scripts\python -m finagent.run cases\samantha-lewis\financial-health.json
```

Open `out/index.html`. The audio is in `out/audio/<scene>.mp3`. Any of the four `cases/<family>/financial-health.json`
works. Without internet the pipeline still runs, with estimated durations and no audio.

**Demo voice (ElevenLabs).** Copy `.env.example` to `.env` and set:

```bash
VOICE_ENGINE=eleven
ELEVENLABS_API_KEY=sk_...   # a personal ElevenLabs key, or leave empty to use TEAM_KEY through the Sherpas proxy
```

then run the same command. The key needs **Text to Speech** (to speak) and **Speech to Text** (to hear questions);
**Voices: read** and **User: read** help to pick voices and check the remaining characters.

## Engines and fallbacks

| `VOICE_ENGINE` | Voice | Cost | Use it for |
|---|---|---|---|
| `edge` (default) | `en-US-EmmaMultilingualNeural` (edge-tts) | free | everyday runs, `./check.sh` |
| `eleven` | ElevenLabs **Matilda**, model `eleven_flash_v2_5` | per character | the demo and rehearsals |
| `mock` | none (durations estimated from text length) | free | offline work |

If an engine fails (no key, no internet, over budget, service error) the voice falls back
**eleven → edge → mock**, logging a warning. The pipeline never breaks because of the voice.

Two routes reach ElevenLabs, chosen from `.env`:
- `ELEVENLABS_API_KEY` set → straight to `api.elevenlabs.io` (our team uses a free ElevenLabs student plan).
- otherwise `TEAM_KEY` + `LLM_PROXY_URL` → the Sherpas proxy (`/v1/audio/speech`, `/v1/audio/transcriptions`),
  which shares the team's **$1.40 ElevenLabs allowance**: keep it for emergencies.

## Spending guards (ElevenLabs bills per character)

- **Cache.** Every ElevenLabs audio is stored in `out/voice_cache/`, keyed by route, model, voice and text. The same
  sentence with the same voice is never paid for twice; a repeated answer comes back in milliseconds.
- **Cap.** `ELEVEN_MAX_CHARS` (default 6000) limits the characters sent in one run, counting only text not cached.
  Over the cap nothing is sent and the run uses edge. One family is about 1,000 characters.
- **Daily cap.** `ELEVEN_MAX_CHARS_PER_DAY` (default 20000, about 80 live answers) limits the characters sent in one
  day, adding up every run and every live answer. This is what protects the account while a public link is open:
  over the cap, new answers are spoken by edge, and audio already cached still plays. The count is kept in
  `out/voice_cache/usage.json` and starts again each day.
- **Default is free.** `./check.sh` uses edge unless you set `VOICE_ENGINE=eleven`; the tests never call any service.

## Settings (`.env`)

| Variable | Default | What it does |
|---|---|---|
| `VOICE_ENGINE` | `edge` | `edge`, `eleven` or `mock` |
| `VOICE_NAME` | `en-US-EmmaMultilingualNeural` | edge-tts voice |
| `VOICE_RATE` | `+0%` | edge-tts speed, e.g. `-5%` slower, `+10%` faster |
| `ELEVENLABS_API_KEY` | — | personal ElevenLabs key (direct route) |
| `TEAM_KEY`, `LLM_PROXY_URL` | — | Sherpas proxy route, used when there is no personal key |
| `ELEVEN_VOICE_ID` | `XrExE9yKIg1WjnnlVkGX` (Matilda) | any ElevenLabs `voice_id` |
| `ELEVEN_MODEL` | `eleven_flash_v2_5` | also `eleven_multilingual_v2`, `eleven_v3` (either spelling: `eleven-flash-v2.5`) |
| `ELEVEN_MAX_CHARS` | `6000` | characters sent per run |
| `ELEVEN_MAX_CHARS_PER_DAY` | `20000` | characters sent per day, all runs and live answers together |
| `ELEVEN_STT_MODEL` | `scribe_v2` | speech-to-text model |
| `VOICE_CACHE_DIR` | `out/voice_cache` | where ElevenLabs audio is cached |

## Reading numbers aloud

Before any engine speaks, `speech_text.to_speech` rewrites a copy of the text the way an advisor would say it.
Rules are plain regular expressions (no LLM): they change how a number is *said*, never its value.

| Written | Said |
|---|---|
| `**Title** — You hold` / `- item` / `## Heading` | "Title. You hold" / "item." / "Heading." |
| `$15,032/yr`, `$500/mo` | "$15,032 a year", "$500 a month" |
| `-$8,336`, `-2.1%` | "minus $8,336", "minus 2.1%" |
| `$1M`, `$200K` | "1 million dollars", "200 thousand dollars" |
| `5–6 months`, `2025–2038` | "5 to 6 months", "2025 to 2038" |
| `22/30` | "22 out of 30" |
| `2034-01`, `2025-04-11` | "January 2034", "April 11, 2025" |
| `~3%`, `25bp`, `&`, `vs.` | "about 3%", "25 basis points", "and", "versus" |
| `401(k)s`, `529 plan`, `IRA`, `NAV` | "four-oh-one-K plans", "five-twenty-nine plan", "I-R-A", "net asset value" |
| `VTI`, `VOO`, `UPRO`, `SPDR` | "V-T-I", "V-double-O", "U-P-R-O", "Spider" |

**Long figures in words, for ElevenLabs only.** Its fast model misread some long amounts written as digits: on
2026-11-16, transcribing Matilda's audio back with Whisper, `$1,166,000` and `$19,900` came out as other amounts.
`spell_big_numbers` now sends every number that has a thousands comma in words ("one million one hundred sixty-six
thousand dollars"); checked again with Whisper, all figures are heard right. The value never changes, and the page
still shows the digits (the captions light `$1,166,000` while the words are said).

The acronym table (`SPOKEN_TERMS`) was checked by transcribing the audio back with Whisper: each entry is what a
listener actually understood. Tested over all 312 texts of the four cases: no number changes, no markdown left.
To hear the rules, `scripts/voice_listen_test.py` writes `out/listen/before.mp3` and `after.mp3` (free, edge-tts).

## Using it from the backend (`/ask`, FastAPI)

```python
from fastapi import FastAPI, UploadFile
from fastapi.responses import Response
from finagent import voice

app = FastAPI()

@app.post("/ask")
async def ask(file: UploadFile):
    heard = await voice.transcribe_async(await file.read(), file.filename)
    if heard.text is None:
        ...                                   # ask the family to type the question
    answer = ...                              # LLM -> guard (the answer only quotes the plan's facts)
    spoken = await voice.speak_async(answer)
    return Response(spoken.audio, media_type="audio/mpeg")   # if spoken.audio is None: send the text only
```

The page can record with the browser's `MediaRecorder` (webm by default) and send the file as it is
(`multipart/form-data`, field `file`): Scribe accepts webm, ogg, mp3, wav and m4a. Use the `async` functions inside
FastAPI; `voice.speak` / `voice.transcribe` are for scripts.

Measured on the real cases (2026-11-15): a new 196-character answer with ElevenLabs is ready in 0.78 s
(12.8 s of audio); a cached one in 0.005 s; a question is transcribed in 0.6–0.8 s.

## A voice note for the partner

In a couple, often only one adult goes through the plan. When they choose a first step, the page can offer
*"Send to Emily"*: a note of about fifteen seconds, sent like a voice message, that tells the other one what worried
the visitor and which step they chose.

> *"Daniel, Emily just went through your family plan. The first step Emily chose: add more life insurance. It takes
> your score from 52 to 57. Have a look at your part of the home when you have a moment. It's a plan for the two of
> you."* (the Johnsons' case, heard back word for word with Whisper on 2026-11-16)

- `GET /partner-note?session_id=…&person=…` → `{available, from, to, text, audio_url}`, or `available: false` with
  a `reason` (a plan for one person, no step chosen yet, or no way to tell who is sending it). `person` is only
  needed when the session does not know who is using it yet.
- `GET /partner-note/{session}.mp3?person=…` → the note spoken with the same voice as the tour. Made once per text
  and kept, so a new step or a "yes, I started it" makes a new one.
- Fixed sentences (`src/finagent/partner_note.py`), no model: free and instant. Its only figures are the step's
  score before and after. The worry is the family's own words, so it goes in without numbers.
- On the page (`web/partner_share.js`): once a first step is chosen, a couple sees the note's text with *Send to
  Daniel* and *Hear it first*. On a phone the MP3 goes to the share sheet (`navigator.share({files: [...]})`), which
  sends it to WhatsApp or Messages as audio; on a computer it is saved as a file. A plan for one person shows nothing.

## The welcome back, spoken

When the family comes back a few days later, the home speaks first instead of waiting to be read:

> *"Welcome back, Emily. A few days ago you chose a first step: Add more life insurance. Have you been able to
> start it?"*

- `GET /reminders?session_id=…&today=…&person=…` now also returns `spoken` and `audio_url`;
  `GET /reminders/{session}.mp3` is that text in the tour's voice, made once per text and kept.
- Fixed sentences (`src/finagent/welcome_back.py`): the greeting, the question about their own step, and at most
  one date of their plan. No model, no new figures. The route only ever speaks that session's own reminders, so a
  public link cannot be used to make the voice say anything else.

## The home explained to the children

Nobody explains the plan to the children. The home does, by name, in about thirty seconds:

> *"Oliver and Sophia, this is your family's home. Each part of it is a piece of the family's money plan. The
> foundations and the walls are strong. The roof keeps everyone safe if something goes wrong, like an accident or
> someone getting sick. Right now it needs real work. ..."*

- `GET /kids-note?family=…` → `{available, to, text, audio_url}`; `GET /kids-note/{family}.mp3` speaks it. The text
  is fixed per family (from the parts' states), so each family's audio is made once.
- Fixed sentences (`src/finagent/kids_note.py`): two tones (young children; teenagers, all 13 or older), the two
  parts that need it most, no figures, and never "mom" or "dad" (the data does not say who is who).
- On the page: *For the children · Explain it to Oliver and Sophia*, in both modes, only in families with children.

## The sound of the home

Under the voice, the home has its own quiet sound (`src/finagent/web/house_sound.js`): soft rain while the score is
low, fading out as it climbs (made of drops, not hiss: hundreds of tiny ticks a second, a clearer "plink" now and
then, different drops in each ear), a bird now and then once the plan is healthy, a short chime when the family marks
a step as done, and a quicker, softer sparkle when they only preview a change (so "look" and "done" never sound
the same). It follows the same scale as the 3D sky, so the picture and the sound change together.

- **Always far below the voice.** Measured in the browser against a real narration (2026-11-16): the loudest rain
  is about 30 dB below the voice, the chime peaks about 20 dB under the voice's peaks.
- **Ducking:** while the narration or an answer plays, the rain and the birds drop about 9 dB more, and come back
  slowly when the voice stops. The chime and the sparkle answer a tap, so they are never lowered (sparkle about 23 dB
  under the voice's peaks).
- The page's sound button turns voice and background off together. Nothing plays before the first tap (browsers
  require it) or while the tab is hidden. Works in both modes and with the 2D or 3D home.
- Made with the Web Audio API: no sound files, nothing to download or license. Levels are constants at the top of
  the file.

## Captions that follow the voice

Each word of the narration lights up on the page as it is said, so the family can read along: for people who hear
badly, a noisy room, or anyone who follows better with both.

- Both engines tell when each word is said: edge-tts with its word boundaries, ElevenLabs with its
  `with-timestamps` route (same price, the timings come with the audio and are cached with it). With neither (the
  Sherpas proxy), the audio's length is shared between the words by their length.
- The voice reads a spoken copy of the text, the page shows the text as written. `captions.align` maps one onto the
  other: while the voice says "fifteen thousand and thirty-two dollars a year", the written `$15,032/yr` is lit.
  The text on the page is never changed.
- One small file per scene next to its MP3, `audio/<scene>.words.json`; the page side is `web/captions.js`.
  No file, no captions, and everything else works the same.

## Files and tests

| File | What |
|---|---|
| `src/finagent/voice.py` | the stage: engines, fallbacks, `synthesize`, `speak_async`, `transcribe_async` |
| `src/finagent/voice_eleven.py` | ElevenLabs: speech, Scribe, cache, cap, MP3 duration (standard library only) |
| `src/finagent/speech_text.py` | `to_speech`: written text → spoken text |
| `src/finagent/partner_note.py` | the voice note for the other half of a couple |
| `src/finagent/kids_note.py` | the home explained to the children |
| `src/finagent/welcome_back.py` | what the home says aloud when the family comes back |
| `src/finagent/captions.py`, `web/captions.js` | when each word is said, and lighting it on the page |
| `tests/test_speech_text.py`, `test_voice_eleven.py`, `test_voice_speak.py`, `test_voice_stt.py`, `test_partner_note.py`, `test_captions.py`, `test_welcome_back.py`, `test_kids_note.py` | all HTTP faked, nothing spent |

Design notes (Spanish, for the team): `02-DOCS/ftd/voz-*.md`.

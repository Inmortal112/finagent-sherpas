# Under One Roof

*One plan. One home. Everyone in it.*

Our entry for the hackathon **"Bring the plan to life"** (Sigma Data Club UPV × Sherpas Wealth, November 2026),
by Samuel ([`Inmortal112`](https://github.com/Inmortal112)), David ([`daviid-sc`](https://github.com/daviid-sc)) and
Raúl ([`rgramonupv`](https://github.com/rgramonupv)).

A family's financial plan is full of numbers that are hard to feel. Under One Roof turns the plan Sherpas
already calculated into something anyone understands at a glance: **their own home**. A calm voice walks the
family through it, they can stop it at any moment and ask a question, and it ends with one first step to take.

## What it is based on

Sherpas gives each family a diagnostic: a financial health score from 0 to 100, five pillars, a list of
recommended steps and a projection of the years ahead. We map each pillar to a part of a house:

| Pillar of the plan | Part of the home | What it means |
|---|---|---|
| Liquidity | Foundations | The emergency fund |
| Insurance | Roof | Protection if something goes wrong |
| Debt | Walls | What they owe |
| Savings | Plumbing | The monthly cash flow |
| Investments | Garden | What is growing for the future |

Each part is drawn **solid**, **cracked** or **broken** from its pillar score (70 and above, 40 to 69, below 40).
A cracked wall needs no explanation.

Three ideas hold the project together:

- **Everything comes from the plan.** No figure is invented. Every number said or shown is a fact read from the
  family's diagnostic, and a check (`guard`) stops anything else before it reaches the screen or the voice.
- **Anyone can follow it.** An opening screen asks three things, one tap each: who is here, how much detail
  (*Simply*: short sentences, big buttons, the voice leads; or *In full*: every figure) and how to explain it
  (*As a story*, the plan told as their home, or *Numbers first*, the figure and then what it means). Nothing is
  locked: *Change*, in the top bar, brings the screen back from any chapter. In a couple, each adult sees their own
  part and keeps their own way of hearing it.
- **It ends in an action.** Every repair is a step Sherpas already calculated, with the score before and after.

It runs on a phone, from a link: nothing to install and no account to create.

## What the family does

1. **Opens their plan** and sees their score, picks who they are and how they want to be guided.
2. **Says what worries them most** about money. The home turns to the part of the plan that answers it.
3. **Walks through the home**: the five parts, then the years ahead. Samantha scores 82, "strong", and her home
   looks fine, until the years move forward to age 73 and her garden dries up: her savings run out.
4. **Sees the repairs**: each step of the plan fixes its part of the home. Its buttons sit on the 3D home, on that
   part: preview the change, or mark the step done.
5. **Asks anything, at any moment**, typed or spoken. The answer uses only the figures of their own plan.
6. **Chooses a first step.** A few days later the page checks in: *have you been able to start it?*
7. **The advisor gets a short note**: what worried them, what they asked, what the plan did not cover and
   what they decided.

## How it works

```
Sherpas diagnostic ─▶ brain ─▶ guard ─▶ voice ─▶ stage ─▶ the page the family opens
                        └────── Presentation (contracts/schemas.py) ──────┘

a question (typed or spoken) ─▶ server ─▶ model answers from one scene's facts ─▶ guard ─▶ text and voice
```

| Stage | Code | What it does |
|---|---|---|
| Brain | [`brain.py`](src/finagent/brain.py), [`house.py`](src/finagent/house.py), [`narrator.py`](src/finagent/narrator.py) | Reads a family's `financial-health.json` and builds a `Presentation`: the facts, and one scene per part of the home, per step and for the years ahead. The narration was written once per family by a text model and saved in [`narrations/`](narrations/) |
| Guard | [`guard.py`](src/finagent/guard.py) | Rejects any narration or answer that quotes a number that is not in the scene's facts, also when it is written in words |
| Voice | [`voice.py`](src/finagent/voice.py), [`voice_eleven.py`](src/finagent/voice_eleven.py) | One MP3 per scene, speaks the live answers and transcribes spoken questions. Free Edge voices by default, ElevenLabs for the demo |
| Stage | [`stage.py`](src/finagent/stage.py), [`stage_page.html`](src/finagent/stage_page.html) | One self-contained page: the home in 3D (a Blender villa drawn with three.js, kept in the repo) or as SVG in the simple mode, scroll by chapters, the chat. No framework and no build step |
| Backend | [`server.py`](src/finagent/server.py), [`ask.py`](src/finagent/ask.py), [`sessions.py`](src/finagent/sessions.py) | FastAPI. Live questions, the conversation history, the check-in and the advisor's note. Keeps the keys |

The three stages share one contract, [`contracts/schemas.py`](contracts/schemas.py): a `Presentation` is a list
of facts (each with its source in the diagnostic) and a list of scenes (narration, visual data and the ids of
the facts it quotes).

The guided tour is prepared in advance, so it costs nothing to play and never waits for a model. Only the
family's own questions go to a model, through Sherpas' proxy, and the answer is checked before a single word is
shown. If it fails the check twice, the family hears the narration already approved for that part of the home;
if the plan does not cover the question, they are told so and the question is kept for the advisor.

The four families come from Sherpas' cases in [`cases/`](cases/): Samantha Lewis (82, strong), Timothy and
Melanie Weah (60, stable), Daniel and Emily Johnson (52, vulnerable) and Michael Carter (26, critical).

More detail: [`STAGE.md`](STAGE.md) (the page), [`BACKEND.md`](BACKEND.md) (routes and how answers stay honest),
[`VOICE.md`](VOICE.md) (voices, cost and the microphone).

## Run it

Python 3.10 or later (we use 3.13). Linux and macOS:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
./check.sh                                                # tests and the whole pipeline
PYTHONPATH=src:. .venv/bin/python -m finagent.run --all   # the four families in both modes, with voice (about 2 min)
scripts/serve.sh                                          # http://localhost:8000
```

Windows (PowerShell; `check.sh` and `scripts/serve.sh` from Git Bash):

```powershell
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
$env:PYTHONPATH="src;."; .venv\Scripts\python -m pytest -q tests; .venv\Scripts\python -m finagent.run --all
```

The tour and its voice work with no key. Live questions need the team key: copy `.env.example` to `.env` and
fill in `TEAM_KEY`. To open it on a phone with the microphone (it needs https), `scripts/share.sh` gives a
temporary public link.

## What comes from Sherpas' starting repo

This repo starts from [`SherpasEngineering/hackathon-upv-2026`](https://github.com/SherpasEngineering/hackathon-upv-2026)
(remote `upstream`).

- [`02-DOCS/brief.md`](02-DOCS/brief.md): the official brief (challenge, cases, criteria, access to the MCP and the proxy, prices).
- [`cases/`](cases/): the four families (`financial-health.json`, `investment-analysis.json`, `persona.md`, PDF).

Their real-time voice example (`examples/voice/`, Node 22) is not kept: our voice is in `src/finagent/voice.py`.
To bring in changes from Sherpas: `git remote add upstream git@github.com:SherpasEngineering/hackathon-upv-2026.git`
(once) and `git pull upstream main`. If they change their `README.md`, the change goes to `02-DOCS/brief.md`; ours stays.

## How we work

Three people, three stages, one contract. [`AGENTS.md`](AGENTS.md) has the rules (for us and for our AI tools):
who knows each stage best, how the contract changes and how work is merged. [`visitas/`](visitas/) is the shared
log between sessions, and [`02-DOCS/`](02-DOCS/) keeps the challenge and one short note per task.

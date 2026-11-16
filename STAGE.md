# Stage: the page the family sees

`src/finagent/stage.py` turns a `Presentation` into one self-contained page (`stage_page.html` with the data
inside it). No build step, no framework: HTML, CSS and JavaScript in one file, drawn as SVG.

## Run it

```bash
PYTHONPATH=src:. .venv/bin/python -m finagent.run --all   # every family, both modes, with its voice (about 2 min)
scripts/serve.sh                                          # http://localhost:8000
```

Without `--all` only `out/index.html` (Samantha) is made; the other families still open, without narration voice.
Opened as a plain file the page works too, except for what needs the backend (questions, worry, reminders).

## What the family does

1. **The score**: who they are (in a couple, each adult picks their name) and how to be guided, simply or in full.
2. **The home today**: the five parts of the plan in their state, who lives there, and one question first:
   *what worries you most about money?* The home turns to the part of the plan that answers it.
3. **Scroll**: a walk through the five parts, the years of the plan as it stands (the garden follows savings and
   investments year by year), then each step of the plan repairing its part, with Sherpas' score before and after.
4. **Every step done**: the combined score when Sherpas published one, and *which one do you start with?*
5. **A few days later**: the check-in ("have you been able to start it?"). Saying yes repairs that part for good.
6. **The advisor's note**: worries, questions, what the plan did not cover, the step chosen, the follow-up.
7. **"?" at any moment**: a chat on the side, typed or spoken. Every answer stays in the list and can be heard
   again; the speaker button stops the voice at once and keeps it off.

## What keeps it honest

- The years show the plan **as it is today**. Sherpas publishes no projection with the repairs made, so the page
  never draws one, and says so.
- A part touched by a step is drawn "repaired", not "solid": we do not claim a pillar score we do not have.
- With no published combination of steps there is no combined score; each step shows its own.
- Every figure on screen comes from `Presentation` (facts and `visual.data`) or from an answer `guard` accepted.

## How it works

| Piece | Where |
|---|---|
| The home | one SVG, a group per part with `data-state` (solid, cracked, broken, repaired); CSS shows cracks and damage |
| The home in 3D | `web/house3d.js` and `web/coastal-home.js` (three.js, kept in `web/vendor/`): a villa modelled in Blender (`web/coast/`), with a solid, a cracked and a broken version of each part; light, sky and rain follow the score; drag to turn it. The default in the full mode. The SVG takes over in *Simply*, without WebGL, with "reduce motion" or on a phone that cannot keep up |
| The steps on the home | with the 3D home, a numbered mark on the part each step repairs and a card beside it with *Preview this change* and *I've completed this step* (`buildHomeActions` in `stage_page.html`); with the SVG they stay in the text |
| Scroll | a sticky stage and tall chapters; the chapter crossing the middle of the screen is the state (`update()`) |
| The years | a 340vh chapter with a sticky card: scroll progress picks the year; `--lush` (0 to 1) dries the garden |
| Voice | one `Audio` player for narration (`audio_path`) and answers (`audio_url`); `data-sound` buttons mute it |
| Backend | `/families`, `/presentation`, `/ask/stream`, `/worry`, `/decision`, `/reminders`, `/follow-up`, `/advisor-note`, `/history` (see `BACKEND.md`) |
| Memory | the session id, the person and the sound choice stay in the browser, so a reload brings the visit back |

Look and type follow sherpaswealth.com: Poppins, Fragment Mono labels, near-black ink, one blue, a violet gradient.

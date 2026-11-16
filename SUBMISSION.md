# /entregar — Under One Roof

> Draft of the final hand-in, for the three of us to review. Due **Wed 18 Nov, 23:59**, on Discord.
> The brief asks for four things (BRIEF.md, "18 Nov, 23:59"):
>
> 1. Repo link (public): https://github.com/Inmortal112/finagent-sherpas
> 2. Working MVP: a link they can open, or run steps in the README ("Run it" section). **Link: TODO**
> 3. 2-minute video, YouTube unlisted or Google Drive. **Link: TODO**
> 4. Half a page to one page on what we built and why: the text below the line.
>
> Keep it true to what the demo shows on the day: if a feature is cut, cut its sentence too.

---

**Under One Roof** — Samuel, David and Raúl
*One plan. One home. Everyone in it.*

**What we built**

A family's financial plan is full of numbers that are hard to feel. Under One Roof turns the plan Sherpas already
calculated into something anyone understands at a glance: **their own home**. The foundations are the emergency
fund, the roof is their protection, the walls are their debt, the plumbing is their monthly cash flow and the garden
is what they are growing for the future. Each part is solid, cracked or broken depending on its pillar score, so
one look tells them what is fine and what needs work.

The family opens it from a link on their phone, with nothing to install. They pick who they are and how they want to
be guided, and say what worries them most; the home turns to the part of the plan that answers it. A calm voice
walks them through the five parts and then through the years ahead. **They can stop it at any moment and ask**,
typing or tapping to talk, and the answer uses only the figures of their own plan. Each step Sherpas recommends is a
repair, and its buttons sit on the home itself, on the part it fixes: they can preview it and watch that part heal
and the score move to the figure Sherpas calculated, then mark it done once they have really taken it. The home can
be heard too: soft rain while the score is low, birds once it is healthy, a chime when a step is done. It ends with
one first step, which they can put in their own calendar for tomorrow, a check-in a few days later that asks what
got in the way, and a short note for their advisor with what worried them, what they asked and what they decided.

**Why we built it this way**

- **It grabs you in seconds.** A cracked wall needs no explanation. Samantha scores 82, "strong", and her home looks
  fine, until the years move forward to age 73 and her garden dries up. That is the problem a good score can hide.
- **Anyone can follow it.** Each person chooses a mode: *Simply* (a flat 2D home, short sentences, big buttons, the
  voice leads) for people who rarely use apps, or *In full* (a 3D home they can turn around with a finger, and every
  figure). Each word lights up as
  the voice says it, for anyone who hears badly or reads along. In a couple, each adult sees their own part, and
  the one who went through the plan can send the other a fifteen-second voice note with the step they chose. The
  children are not left out: the home explains itself to them by name, in their own words and with no figures.
  And a family that speaks Spanish at home can listen to the whole tour in Spanish, with the same figures.
- **It is really theirs.** Each family gets its own home, its own words and the worries their own plan points to.
  None of the four plans records what the family is worried about, so we start by asking.
- **It moves people to act.** Every repair is a step Sherpas already calculated, with the score before and after,
  and when they come back the home greets them by name, aloud, and asks whether they started.
- **It is honest.** No number is invented. Every figure said or shown is read from the family's diagnostic, and a
  check (`guard`) blocks any narration or answer that quotes a number that is not there. If the plan does not cover
  a question, the family is told so and the question goes to the advisor. A preview never claims the plan was
  recalculated, and steps Sherpas did not score together are never added up.
- **It is cheap to run.** The guided tour and its voice are prepared in advance, so playing it costs nothing and
  never waits for a model. Only the family's own questions go to a model and to the voice in real time.

**What we said no to**

A TV-style series of the plan (too passive), a world to explore (it would lose older users, so it became the house),
two AI advisors debating (too close to the chat Sherpas already has), a live voice conversation for everything (too
expensive and slow with shared credits) and reading emotions by camera or cloning family voices (invasive).

**How it works**

Python and FastAPI. A pipeline reads each case's `financial-health.json` and builds the facts and the scenes (brain),
checks every number (guard), turns each scene into speech (voice: ElevenLabs for the demo, free Edge voices as a
fallback, ElevenLabs Scribe to understand spoken questions) and renders one self-contained page (stage). The 3D home
is a villa modelled in Blender and drawn with three.js: each part has a solid, a cracked and a broken version, and
the light, the sky and the rain follow the score. The live questions go through Sherpas' proxy, and the keys stay on
the server.

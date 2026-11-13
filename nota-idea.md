# /idea — The House That Listens

> DRAFT for the team (David, 13 Nov). Due Fri 13 Nov, 22:00, via `/idea`. One page max.
> Edit freely; once Samuel and Raúl agree, paste the text below the line into Discord.

---

**The House That Listens** — Samuel, David and Raúl

**What we will build**
- A mobile web experience that turns a family's Sherpas plan into **their own home**: each part of the house is one
  pillar of their score (foundations = emergency fund, roof = protection, structure = debt, utilities = cash flow,
  garden = investments). Cracks and missing parts show at a glance what is solid and what is not.
- A calm voice walks them through the house and through the years of their plan. **They can stop it at any time**,
  by speaking or tapping, and the house turns to the part they asked about and answers with their plan's own data.
- It ends in **one first step** with a date, returns on day 3 and on the plan's own dates, and gives the advisor a
  one-page brief: what the family asked, what worries them and what they chose.

**Why**
- **Captivating:** a cracked house reads in three seconds. Samantha scores 82, "strong", and her house looks
  perfect, until the timeline reaches 73 and her garden dries out: the problem a good score hides.
- **Understanding:** the metaphor needs no finance. **Simple mode by default** for non-digital or older users (one
  thing per screen, the voice leads, one big Next button, hold-to-talk like a voice note, questions as buttons).
  **Explore mode** for experts: scroll through the years, every figure and its source.
- **Motivation to act:** each repair is a step the plan already computes (`top_moves`, `combined_moves`), with the
  score before and after. They commit with a date and watch that part get repaired.
- **Personal:** not one template with a new name. Michael rents, with his 2027 house under construction next door;
  Samantha's house is paid off and Ethan's room goes quiet when college starts. Each partner sees their own part
  (Timothy's and Melanie's life-cover gaps). It starts with what worries them, a section that is empty in all four
  plans, and their own words come back on day 3 and 30.
- **Creativity:** not a tour and not a chat. The plan listens, and what you ask changes what you see.
- **Honest data:** every figure comes from the case files. There is no projection for "if you take the step", so a
  repair changes the score, never an invented future.

**What we considered and ruled out**
- **The plan as a TV series** (trailer and episodes unlocked by actions): captivating, but watching videos is
  passive and the tone is not serious enough for a family's finances.
- **The plan as a village to explore:** strong visuals, but navigating a world is hard for older or non-digital
  users. It became the house: one image everyone understands.
- **Two AI advisors debating the family's dilemma:** explains trade-offs well, but too close to the chat Sherpas
  already has.
- **A game to split the family's spare cash:** great for a first step, but covers only part of the challenge, and
  two of the four families have no combined scenarios.
- **A voice message from your future self:** very captivating, but one-off and weak on action; the plan only
  projects the current path, so the "good ending" would need invented numbers.
- **Sixty seconds a day by message:** best for the days after, but closest to a chat and hard to show in two minutes.
- **A setup screen where each person picks how to be told:** good for "personal", but starting with settings adds
  friction. We kept the idea as two modes and three formats (look, read, listen) always one tap away.

**Risks and how we handle them**
- 3D is costly: the simple mode is 2D first; 3D only for explore mode, if a phone prototype works on day one.
- We will test the simple mode with 3–5 people outside the team, including an older, non-digital user.

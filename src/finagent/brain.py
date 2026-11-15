"""Stage 1 (owner: A). Sherpas diagnostic -> Presentation with facts and narration.

Input: the `financial-health.json` of one family in `cases/`.
The score, its five pillars as parts of a house, the plan's top moves as repairs, and the plan
through the years. `build_template` writes template sentences; `build` swaps in the narration a
text model wrote once per family (`narrations/`, see narrator.py), scene by scene, if `guard` accepts it.

What the stage needs to draw the house travels in `visual.data` (the contract does not change):
- intro:     `house` {part: state}, `people`, `band`, `colour`, `home` (owned or rented, and the cars)
- pillar_*:  `house_part`, `state`, `state_fact_id`
- move_*:    `house_part`, `action`, `effort`, `score_before`, `score_after`
- all_moves: `moves`, `score_before`, `score_after` (only when the plan combines moves)
- person_*:  one per adult when the plan belongs to a couple: `person`, `salary`, `accounts`, `debts`, life cover
- timeline:  `points` (one per year), `events` (retirement, debt_free, savings_run_out / savings_last)
             and `dates` (the plan's dated goals: college, a purchase, a vacation)
"""
import re

from contracts.schemas import Fact, Presentation, Scene, Visual
from finagent import house, narrator

SOURCE = "financial-health.json"


MODES = ("complete", "simple")


def build(diagnostic: dict, language: str = "en", mode: str = "complete") -> Presentation:
    """The family's presentation, with the saved narration of `narrations/` where `guard` accepts it.

    `mode` is the one each person picks on opening: "complete" (every figure) or "simple" (shorter
    sentences, one figure at most). Facts and scenes are the same; only the narration changes.
    """
    if mode not in MODES:
        raise ValueError(f"mode must be one of {MODES}, not {mode!r}")
    return narrator.apply_saved(build_template(diagnostic, language), diagnostic["case"]["slug"], mode=mode)


def build_template(diagnostic: dict, language: str = "en") -> Presentation:
    """Facts and scenes with template sentences: what the narrator starts from, and its fallback."""
    score = diagnostic["score"]
    name = _client_name(diagnostic["case"]["household"])

    facts = [
        Fact(id="score", label="Financial health score", value=score["published_score"], unit="/100",
             source=f"{SOURCE}:score.published_score"),
        Fact(id="band", label="Score band", value=score["band"], source=f"{SOURCE}:score.band"),
    ]
    facts += _context("summary", "Sherpas' summary of the plan", diagnostic, ("summary_main",))
    scenes = [
        Scene(
            id="intro",
            title="Your financial health",
            narration=(
                f"Hello, {name}. Your financial health score is {score['published_score']} out of 100. "
                f"Sherpas calls that {score['band']}."
            ),
            visual=Visual(kind="score", data={
                "fact_id": "score",
                "band": score["band"],
                "colour": score["colour"],
                "house": {house.part_for_pillar(p["pillar"]): house.state(p["score"]) for p in score["pillars"]},
                "people": [{"first_name": p["first_name"], "role": p["role"], "age": p["age"]}
                           for p in diagnostic["case"]["household"]],
                "home": house.home(diagnostic),
            }),
            fact_ids=["score", "band"] + [f.id for f in facts if f.id == "context_summary"],
        )
    ]

    for i, pillar in enumerate(score["pillars"]):
        earned, available = pillar["points_shown_in_app"].split("/")
        fact_id = f"pillar_{_slug(pillar['pillar'])}"
        facts.append(Fact(id=fact_id, label=pillar["pillar"], value=int(earned), unit=f"/{available}",
                          source=f"{SOURCE}:score.pillars[{i}].points_shown_in_app"))
        part, state = house.part_for_pillar(pillar["pillar"]), house.state(pillar["score"])
        state_id = f"house_{part}_state"
        facts.append(Fact(id=state_id, label=f"State of the {part}", value=state,
                          source=f"derived from {SOURCE}:score.pillars[{i}].score (thresholds in house.py)"))
        context = _context(part, f"Sherpas' observations on the {part} ({pillar['pillar'].lower()})", diagnostic,
                           house.PART_NARRATIVE[part])
        facts += context
        scenes.append(
            Scene(
                id=fact_id,
                title=pillar["pillar"],
                narration=(
                    f"Your {part} {_verb(part)} {state}. "
                    f"{pillar['pillar']}: {earned} out of {available} points."
                ),
                visual=Visual(kind="kpi", data={"fact_id": fact_id, "house_part": part, "state": state,
                                                "state_fact_id": state_id}),
                fact_ids=[fact_id, state_id] + [f.id for f in context],
            )
        )

    people = house.adults(diagnostic)
    if len(people) > 1:  # with one adult, their part is the whole home
        for person in people:
            person_facts, person_scene = _person(diagnostic, person["first_name"])
            facts.extend(person_facts)
            scenes.append(person_scene)

    for i, move in enumerate(score["top_moves"]):
        before_id, after_id = f"move_{i + 1}_score_before", f"move_{i + 1}_score_after"
        facts.append(Fact(id=before_id, label=f"{move['title']}: score before", value=move["score_before"],
                          unit="/100", source=f"{SOURCE}:score.top_moves[{i}].score_before"))
        facts.append(Fact(id=after_id, label=f"{move['title']}: score after", value=move["score_after"],
                          unit="/100", source=f"{SOURCE}:score.top_moves[{i}].score_after"))
        action_id = f"move_{i + 1}_action"
        facts.append(Fact(id=action_id, label=f"{move['title']}: what to do", value=move["action"],
                          source=f"{SOURCE}:score.top_moves[{i}].action"))
        if move["score_after"] > move["score_before"]:
            effect = f"It takes your score from {move['score_before']} to {move['score_after']}."
        else:
            effect = f"On its own, your score stays at {move['score_before']}."
        part = house.part_for_move(move["title"])
        repair = f" This repair is for your {part}." if part else ""
        scenes.append(
            Scene(
                id=f"move_{i + 1}",
                title=move["title"],
                narration=f"A step your plan already worked out: {move['title']}. {effect}{repair}",
                visual=Visual(kind="kpi", data={
                    "fact_id": after_id, "house_part": part, "action": move["action"], "effort": move["effort"],
                    "score_before": move["score_before"], "score_after": move["score_after"],
                }),
                fact_ids=[before_id, after_id, action_id],
            )
        )

    best = house.best_combination(score)
    if best:
        facts.append(Fact(id="all_moves_score_after", label="Score after the combined moves",
                          value=best["score_after"], unit="/100",
                          source=f"{SOURCE}:score.combined_moves[].score_after"))
        scenes.append(
            Scene(
                id="all_moves",
                title="Your house, repaired",
                narration=(
                    f"Done together, {_join(best['moves'])} take your score "
                    f"from {score['published_score']} to {best['score_after']}."
                ),
                visual=Visual(kind="score", data={
                    "fact_id": "all_moves_score_after", "moves": best["moves"],
                    "score_before": score["published_score"], "score_after": best["score_after"],
                }),
                fact_ids=["score", "all_moves_score_after"],
            )
        )

    timeline_facts, timeline_scene = _timeline(diagnostic)
    timeline_context = _context("retirement", "Sherpas' observations on retirement", diagnostic,
                                ("retirement_short_observations",))
    timeline_facts += timeline_context
    timeline_scene.fact_ids += [f.id for f in timeline_context]
    facts.extend(timeline_facts)
    scenes.append(timeline_scene)

    return Presentation(client_name=name, language=language, facts=facts, scenes=scenes)


def _timeline(diagnostic: dict) -> tuple[list[Fact], Scene]:
    """Facts and scene for the plan through the years. Sentences quote ages and years only."""
    data = house.timeline(diagnostic)
    facts, sentences, retiring = [], [], []
    for event in data["events"]:
        if event["kind"] == "retirement":
            fact_id = f"retirement_age_{_slug(event['person'])}"
            facts.append(Fact(id=fact_id, label=f"{event['person']}'s planned retirement age", value=event["age"],
                              source=f"{SOURCE}:case.household[].retirement_age"))
            retiring.append(event)
        elif event["kind"] == "debt_free":
            facts.append(Fact(id="debt_free_year", label="First year with no debt in the plan", value=event["year"],
                              source=f"{SOURCE}:projections.yearly[].total_debts"))
            sentences.append(f"The plan has your debts paid off by {event['year']}.")
        elif event["kind"] == "savings_run_out":
            facts.append(Fact(id="savings_run_out_age", label="Age when savings and investments run out",
                              value=event["age"], source=f"{SOURCE}:key_metrics.facts.retirement.savingsRunOut.label"))
            facts.append(Fact(id="unpaid_spending", label="Planned spending left unpaid by the end of the plan",
                              value=round(event["unpaid_spending"]), unit="USD",
                              source=f"{SOURCE}:key_metrics.facts.retirement.savingsRunOut.value (whole dollars)"))
            sentences.append(f"On the current plan, your savings and investments run out at age {event['age']}.")
        elif event["kind"] == "savings_last":
            facts.append(Fact(id="savings_left_at_plan_end",
                              label="Savings and investments left at the end of the plan",
                              value=round(event["savings_left"]), unit="USD",
                              source=f"{SOURCE}:key_metrics.facts.retirement.savingsLeftAtPlanEnd.value (whole dollars)"))
            sentences.append("On the current plan, your savings and investments last to the end of the plan.")

    if len(retiring) == 1:
        sentences.insert(0, f"You plan to retire at {retiring[0]['age']}.")
    elif retiring:
        plans = [f"{retiring[0]['person']} plans to retire at {retiring[0]['age']}"]
        plans += [f"{event['person']} at {event['age']}" for event in retiring[1:]]
        sentences.insert(0, f"{_join(plans)}.")

    main_fact = next((f.id for f in facts if f.id in ("savings_run_out_age", "savings_left_at_plan_end")), None)
    scene = Scene(
        id="timeline",
        title="Your house through the years",
        narration=" ".join(["Now look ahead."] + sentences),
        visual=Visual(kind="line", data={"fact_id": main_fact, "house_part": "garden", **data,
                                         "dates": house.plan_dates(diagnostic)}),
        fact_ids=[f.id for f in facts],
    )
    return facts, scene


def _money(amount: float) -> str:
    return f"${amount:,.2f}".removesuffix(".00")


def _person(diagnostic: dict, first_name: str) -> tuple[list[Fact], Scene]:
    """One adult's own part of the home: what is in their name. Used when the plan belongs to a couple."""
    view = house.person_view(diagnostic, first_name)
    slug = _slug(first_name)
    facts, sentences = [], [f"{first_name}, this is your part of the home."]

    def add(key: str, label: str, value, source: str, unit: str = "") -> str:
        facts.append(Fact(id=f"person_{slug}_{key}", label=f"{first_name}: {label}", value=value, unit=unit,
                          source=f"{SOURCE}:{source}"))
        return facts[-1].id

    if view["salary"]:
        add("salary", "yearly salary", view["salary"], "profile.incomes[].yearly", "USD")
        sentences.append(f"Your salary is {_money(view['salary'])} a year.")
    if view["accounts"]:
        listed = _join([f"{a['name']} ({_money(a['balance'])})" for a in view["accounts"]])
        add("accounts", "accounts in their name", listed, "profile.accounts[]")
    if view["debts"]:
        listed = _join([f"{d['name']} ({_money(d['balance'])} at {d['rate_percent']:g}%)" for d in view["debts"]])
        add("debts", "debts in their name", listed, "profile.liabilities[]")
    if view["life_cover"] is not None:
        add("life_cover", "life insurance", view["life_cover"],
            "key_metrics.protection.lifeInsurance.lifeInsuranceCoverageBasics", "USD")
        sentence = f"You hold {_money(view['life_cover'])} of life insurance"
        if view["life_recommended_min"] is not None:
            add("life_recommended_min", "recommended life insurance, minimum", view["life_recommended_min"],
                "key_metrics.protection.lifeInsurance.lifeInsuranceCoverageRecommendations", "USD")
            add("life_recommended_max", "recommended life insurance, maximum", view["life_recommended_max"],
                "key_metrics.protection.lifeInsurance.lifeInsuranceCoverageRecommendations", "USD")
        if view["life_shortfall"]:
            add("life_shortfall", "life insurance shortfall", view["life_shortfall"],
                "key_metrics.protection.lifeInsurance.lifeInsuranceCoverageGapsAndExcess", "USD")
            sentence += f", {_money(view['life_shortfall'])} short of the recommended minimum"
        sentences.append(sentence + ".")

    scene = Scene(
        id=f"person_{slug}",
        title=f"{first_name}'s part of the home",
        narration=" ".join(sentences),
        # no single `house_part`: a person's part runs through the whole home (their cover, accounts, debts)
        visual=Visual(kind="text", data={"person": first_name, "fact_id": f"person_{slug}_life_cover", **view}),
        fact_ids=[f.id for f in facts],
    )
    return facts, scene


def _context(name: str, label: str, diagnostic: dict, sections: tuple[str, ...]) -> list[Fact]:
    """Sherpas' own plain-words text about one area, as a fact: the narration may quote its figures."""
    narrative = diagnostic.get("narrative") or {}
    found = [key for key in sections if narrative.get(key)]
    if not found:
        return []
    return [Fact(id=f"context_{name}", label=label, value="\n".join(str(narrative[key]) for key in found),
                 source=f"{SOURCE}:narrative.{' + '.join(found)}")]


def _verb(part: str) -> str:
    return "are" if part.endswith("s") else "is"


def _join(items: list[str]) -> str:
    """'a', 'a and b' or 'a, b and c'."""
    return items[0] if len(items) == 1 else f"{', '.join(items[:-1])} and {items[-1]}"


def _client_name(household: list[dict]) -> str:
    """First names of the adults the plan belongs to, e.g. 'Timothy and Melanie'."""
    return " and ".join(p["first_name"] for p in household if p["role"] in ("client", "co-client"))


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")

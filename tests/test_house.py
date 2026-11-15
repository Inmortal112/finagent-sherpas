"""House facts: parts, states, repairs and the plan through the years, for the four real cases."""
import json
from pathlib import Path

import pytest

from finagent import brain, guard, house

ROOT = Path(__file__).resolve().parents[1]
CASES = sorted((ROOT / "cases").glob("*/financial-health.json"))


def _load(family: str) -> dict:
    return json.loads((ROOT / "cases" / family / "financial-health.json").read_text(encoding="utf-8"))


def _house(family: str) -> dict:
    return brain.build(_load(family)).scenes[0].visual.data["house"]


def _events(family: str) -> dict:
    return {e["kind"]: e for e in house.timeline(_load(family))["events"]}


@pytest.mark.parametrize("pillar_score, expected", [(100, "solid"), (70, "solid"), (69, "cracked"),
                                                    (40, "cracked"), (39, "broken"), (0, "broken")])
def test_state_thresholds(pillar_score, expected):
    assert house.state(pillar_score) == expected


@pytest.mark.parametrize("path", CASES, ids=lambda p: p.parent.name)
def test_every_family_gets_the_five_parts_with_a_state(path):
    presentation = brain.build(json.loads(path.read_text(encoding="utf-8")))
    facts = {f.id: f for f in presentation.facts}
    assert set(presentation.scenes[0].visual.data["house"]) == set(house.PARTS)
    for part in house.PARTS:
        assert facts[f"house_{part}_state"].value in ("solid", "cracked", "broken")
    pillar_scenes = [s for s in presentation.scenes if s.id.startswith("pillar_")]
    assert sorted(s.visual.data["house_part"] for s in pillar_scenes) == sorted(house.PARTS)
    assert all(s.visual.data["state"] == facts[s.visual.data["state_fact_id"]].value for s in pillar_scenes)


def test_states_match_the_examples_in_the_idea():
    assert _house("daniel-emily-johnson")["roof"] == "broken"        # protection 0/20: no roof
    assert _house("timothy-melanie-weah")["walls"] == "cracked"      # the card cracks the structure
    michael = _house("michael-carter")
    assert (michael["plumbing"], michael["roof"], michael["walls"]) == ("broken", "broken", "solid")
    samantha = _house("samantha-lewis")
    assert "broken" not in samantha.values()
    assert (samantha["foundations"], samantha["walls"]) == ("solid", "solid")


@pytest.mark.parametrize("path", CASES, ids=lambda p: p.parent.name)
def test_every_move_repairs_a_part(path):
    diagnostic = json.loads(path.read_text(encoding="utf-8"))
    for move in diagnostic["score"]["top_moves"]:
        assert house.part_for_move(move["title"]) in house.PARTS, move["title"]


@pytest.mark.parametrize("path", CASES, ids=lambda p: p.parent.name)
def test_every_move_has_a_plain_title_without_figures(path):
    diagnostic = json.loads(path.read_text(encoding="utf-8"))
    for move in diagnostic["score"]["top_moves"]:
        plain = house.plain_title(move["title"])
        assert plain != move["title"], f"no plain title for {move['title']!r}"
        assert not any(ch.isdigit() for ch in plain), plain


def test_plain_title_keeps_an_unknown_title_and_reaches_the_page():
    assert house.plain_title("Something nobody has seen") == "Something nobody has seen"
    plan = brain.build(_load("daniel-emily-johnson"))
    move = next(s for s in plan.scenes if s.id == "move_1")
    assert move.title == "Raise mortality coverage"  # Sherpas' title stays for the advisor
    assert move.visual.data["plain_title"] == "Add more life insurance"


@pytest.mark.parametrize("title, part", [
    ("Add umbrella cover", "roof"), ("Raise mortality coverage", "roof"), ("Pay down revolving card", "walls"),
    ("Raise annual savings", "plumbing"), ("Lower the withdrawal rate", "plumbing"),
    ("Reduce single-name concentration", "garden"), ("Raise growth allocation toward glide", "garden"),
    ("Something nobody has seen", None),
])
def test_move_titles_map_to_the_part_they_repair(title, part):
    assert house.part_for_move(title) == part


def test_timeline_savings_run_out_only_where_the_plan_says_so():
    assert _events("samantha-lewis")["savings_run_out"]["age"] == 73
    assert _events("michael-carter")["savings_run_out"]["age"] == 85
    for family in ("timothy-melanie-weah", "daniel-emily-johnson"):
        events = _events(family)
        assert "savings_run_out" not in events and "savings_last" in events


@pytest.mark.parametrize("path", CASES, ids=lambda p: p.parent.name)
def test_timeline_scene_is_backed_by_the_plan(path):
    diagnostic = json.loads(path.read_text(encoding="utf-8"))
    presentation = brain.build(diagnostic)
    scene = presentation.scenes[-1]
    assert scene.id == "timeline"
    points = scene.visual.data["points"]
    assert [p["year"] for p in points] == [row["year"] for row in diagnostic["projections"]["yearly"]]
    assert min(p["investable_assets"] for p in points) >= 0, "never show a negative balance"
    adults = [p for p in diagnostic["case"]["household"] if p.get("retirement_age") is not None]
    retirements = [e for e in scene.visual.data["events"] if e["kind"] == "retirement"]
    assert sorted(e["age"] for e in retirements) == sorted(p["retirement_age"] for p in adults)
    assert all(e["year"] for e in scene.visual.data["events"])
    assert guard.unsupported_numbers(presentation) == []


def test_repaired_house_uses_the_best_combination_of_moves():
    presentation = brain.build(_load("timothy-melanie-weah"))
    facts = {f.id: f for f in presentation.facts}
    assert facts["all_moves_score_after"].value == 78
    assert "all_moves" in [s.id for s in presentation.scenes]
    assert "all_moves" not in [s.id for s in brain.build(_load("samantha-lewis")).scenes]


def test_tied_combinations_keep_the_shortest_one():
    best = house.best_combination(_load("daniel-emily-johnson")["score"])
    assert (best["score_after"], len(best["moves"])) == (60, 2)

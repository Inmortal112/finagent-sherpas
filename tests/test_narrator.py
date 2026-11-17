"""Narration written by the model: only what `guard` accepts is ever said. No test calls the model."""
import json
from pathlib import Path

import pytest

from finagent import brain, guard, narrator

ROOT = Path(__file__).resolve().parents[1]
CASES = sorted((ROOT / "cases").glob("*/financial-health.json"))


def _load(family: str = "samantha-lewis") -> dict:
    return json.loads((ROOT / "cases" / family / "financial-health.json").read_text(encoding="utf-8"))


def _save(tmp_path: Path, scenes: dict) -> Path:
    (tmp_path / "samantha-lewis.json").write_text(json.dumps({"scenes": scenes}), encoding="utf-8")
    return tmp_path


def test_saved_narration_replaces_the_template(tmp_path):
    template = brain.build_template(_load())
    text = "Samantha, your home scores 82 out of 100. Sherpas calls that strong."
    result = narrator.apply_saved(template, "samantha-lewis", _save(tmp_path, {"intro": text}))
    assert result.scenes[0].narration == text
    assert [s.narration for s in result.scenes[1:]] == [s.narration for s in template.scenes[1:]]
    assert template.scenes[0].narration != text, "the template presentation is not modified"


def test_a_saved_number_that_is_not_in_the_facts_falls_back_to_the_template(tmp_path):
    template = brain.build_template(_load())
    saved = {"intro": "Your score is 82 out of 100, and you save 9,999 dollars a month.",
             "pillar_debt": "Your walls are solid: 20 out of 20 points."}
    result = narrator.apply_saved(template, "samantha-lewis", _save(tmp_path, saved))
    scenes = {s.id: s.narration for s in result.scenes}
    assert scenes["intro"] == template.scenes[0].narration
    assert scenes["pillar_debt"] == saved["pillar_debt"]
    assert guard.unsupported_numbers(result) == []


def test_numbers_written_in_words_are_rejected():
    template = brain.build_template(_load())
    accepted, rejected = narrator.check(template, {
        "timeline": "You plan to retire at 65, and your savings run out at seventy-three.",
        "pillar_debt": "Your walls are solid, with 20 out of 20 points. The two of you owe nothing.",
        "not_a_scene": "ignored",
    })
    assert list(accepted) == ["pillar_debt"]
    assert "seventy" in rejected["timeline"]


def test_without_saved_narration_the_template_is_used(tmp_path):
    template = brain.build_template(_load())
    assert narrator.apply_saved(template, "samantha-lewis", tmp_path) == template


def test_the_narration_may_quote_sherpas_own_observations():
    template = brain.build_template(_load())
    accepted, rejected = narrator.check(template, {
        "pillar_liquidity_and_emergency_fund": "Your foundations are solid. Your $80,000 in cash covers 7.9 months.",
        "pillar_debt": "Your walls are solid, and your $80,000 in cash covers 7.9 months.",
    })
    assert list(accepted) == ["pillar_liquidity_and_emergency_fund"], "a figure belongs to its own part of the home"
    assert "pillar_debt" in rejected


@pytest.mark.parametrize("path", CASES, ids=lambda p: p.parent.name)
def test_every_saved_scene_in_the_repo_is_accepted(path):
    diagnostic = json.loads(path.read_text(encoding="utf-8"))
    saved_path = narrator.NARRATIONS_DIR / f"{path.parent.name}.json"
    assert saved_path.exists(), "run: python -m finagent.narrator --all"
    saved = json.loads(saved_path.read_text(encoding="utf-8"))["scenes"]
    template = brain.build_template(diagnostic)
    accepted, rejected = narrator.check(template, saved)
    assert rejected == {}
    assert set(accepted) == {s.id for s in template.scenes}, "every scene has its own narration"
    built = brain.build(diagnostic)
    assert {s.id: s.narration for s in built.scenes} == accepted


def test_a_part_of_the_home_cannot_score_out_of_100():
    diagnostic = json.loads((ROOT / "cases" / "michael-carter" / "financial-health.json").read_text(encoding="utf-8"))
    template = brain.build_template(diagnostic)
    wrong = "Your plan adds umbrella cover. It lifts your roof score to 31 out of 100."
    right = "Your plan adds umbrella cover. It repairs your roof and lifts your score to 31 out of 100."
    accepted, rejected = narrator.check(template, {"move_1": wrong})
    assert not accepted and "only the overall score is out of 100" in rejected["move_1"]
    assert narrator.check(template, {"move_1": right})[0] == {"move_1": right}


def test_a_step_that_pays_part_of_a_debt_is_never_said_to_clear_it():
    weah = json.loads((ROOT / "cases" / "timothy-melanie-weah" / "financial-health.json").read_text(encoding="utf-8"))
    template = brain.build_template(weah)
    step = next(scene for scene in template.scenes if scene.id == "move_1")
    assert step.visual.data["pays_part_of_debt"] and "move_1_card_balance" in step.fact_ids
    for wrong in ("Pay $6,800 on the card. That clears your costliest debt.",
                  "Paying $6,800 pays off the card and lifts your score to 62.",
                  "With $6,800 you wipe out the 18% card."):
        accepted, rejected = narrator.check(template, {"move_1": wrong})
        assert not accepted and "pays only part of the debt" in rejected["move_1"], wrong
    for right in ("Pay $6,800 off the 18% card, using cash you already have. It lifts your score from 60 to 62.",
                  "It pays $6,800 of the $18,000 card, so the debt isn't cleared yet.",
                  "Pay $6,800 on the 18% card. The rest is still owed, and it will take longer to clear.",
                  "It pays $6,800 on the card to clear the gate that holds your score down."):
        assert narrator.check(template, {"move_1": right})[0] == {"move_1": right}, right
    # the same words are fine where no step pays part of a debt
    assert narrator.check(template, {"pillar_debt": "At today's payment it takes years to clear."})[0]
    for case in sorted((ROOT / "cases").glob("*/financial-health.json")):  # every saved text still passes
        diagnostic = json.loads(case.read_text(encoding="utf-8"))
        for mode in brain.MODES:
            built = brain.build(diagnostic, mode=mode)
            texts = {scene.id: scene.narration for scene in built.scenes}
            assert narrator.check(built, texts)[1] == {}, (case.parent.name, mode)


@pytest.mark.parametrize("path", CASES, ids=lambda p: p.parent.name)
def test_every_style_has_an_accepted_text_for_every_scene(path):
    """Another way of explaining (narrator.STYLES) covers the whole full mode, with text that `guard` accepts."""
    diagnostic = json.loads(path.read_text(encoding="utf-8"))
    built = brain.build(diagnostic)
    for style in narrator.STYLES:
        saved = narrator.saved_texts(path.parent.name, style=style)
        assert saved, f"run: python -m finagent.narrator --all --style {style}"
        accepted, rejected = narrator.check(built, saved)
        assert rejected == {}
        assert set(accepted) == {s.id for s in built.scenes}, f"every scene has its {style} text"
        assert narrator.styled(built, path.parent.name, style) == accepted
        assert all(accepted[s.id] != s.narration for s in built.scenes), "a style says it in other words"


def test_a_style_is_saved_apart_from_the_narration(tmp_path):
    story = "Samantha, your home scores 82 out of 100."
    (tmp_path / "samantha-lewis.json").write_text(json.dumps({
        "scenes": {"intro": story},
        "numbers": {"intro": "Your score is 82 out of 100.", "pillar_debt": "Your debt scores 9,999 points."},
    }), encoding="utf-8")
    template = brain.build_template(_load())
    assert narrator.saved_texts("samantha-lewis", directory=tmp_path) == {"intro": story}
    assert narrator.styled(template, "samantha-lewis", "numbers", directory=tmp_path) == {
        "intro": "Your score is 82 out of 100."}, "a figure that is not in the scene's facts drops that scene's text"
    assert narrator.apply_saved(template, "samantha-lewis", tmp_path).scenes[0].narration == story


def test_where_each_text_is_saved():
    assert narrator.text_key() == "scenes" and narrator.text_key("simple") == "simple"
    assert narrator.text_key("complete", "numbers") == "numbers"
    assert narrator.text_key("simple", "numbers") == "numbers_simple"
    with pytest.raises(ValueError):
        narrator.text_key("complete", "poetry")

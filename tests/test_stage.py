"""The stage: one page with the presentation inside it, for every family."""
import json
import re
from pathlib import Path

import pytest

from contracts.schemas import Presentation
from finagent import brain, house, run, stage

ROOT = Path(__file__).resolve().parents[1]
CASES = sorted((ROOT / "cases").glob("*/financial-health.json"))


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _embedded(page: str) -> dict:
    return json.loads(re.search(r'<script id="presentation" type="application/json">(.*?)</script>', page, re.S).group(1))


@pytest.mark.parametrize("path", CASES, ids=lambda p: p.parent.name)
def test_the_page_carries_the_whole_presentation(path, tmp_path):
    presentation = brain.build(_load(path))
    page = stage.render(presentation, tmp_path).read_text(encoding="utf-8")
    assert Presentation.model_validate(_embedded(page)) == presentation
    assert "__" not in re.sub(r"<script.*?</script>", "", page, flags=re.S), "a placeholder was left unfilled"
    for part in house.PARTS:
        assert f'id="p-{part}"' in page, f"the drawing has no {part}"


def test_text_from_the_plan_cannot_close_the_script_tag():
    presentation = brain.build(_load(CASES[0]))
    presentation.scenes[0].narration = "</script><script>alert(1)</script>"
    page = stage.page(presentation)
    assert "<script>alert(1)" not in page
    assert _embedded(page)["scenes"][0]["narration"] == presentation.scenes[0].narration


def test_the_home_is_owned_or_rented_as_the_plan_says():
    by_family = {path.parent.name: house.home(_load(path)) for path in CASES}
    assert by_family["samantha-lewis"] == {"kind": "owned", "value": 900000, "cars": ["Porsche Cayenne"]}
    assert by_family["michael-carter"]["kind"] == "rented"


def test_the_timeline_carries_the_plan_dates_without_engine_markers():
    scene = next(s for s in brain.build(_load(ROOT / "cases" / "samantha-lewis" / "financial-health.json")).scenes
                 if s.id == "timeline")
    names = [d["name"] for d in scene.visual.data["dates"]]
    assert "College Ava" in names and None not in names


def test_the_pipeline_builds_a_page_per_mode(tmp_path, monkeypatch):
    monkeypatch.setenv("VOICE_ENGINE", "mock")
    case = ROOT / "cases" / "timothy-melanie-weah" / "financial-health.json"
    simple = _embedded(run.main(case, tmp_path / "simple", "simple").read_text(encoding="utf-8"))
    complete = _embedded(run.main(case, tmp_path / "complete").read_text(encoding="utf-8"))
    assert [s["id"] for s in simple["scenes"]] == [s["id"] for s in complete["scenes"]]
    assert simple["scenes"][1]["narration"] != complete["scenes"][1]["narration"], "the simple mode has its own words"


def test_the_page_offers_what_the_backend_can_do():
    page = stage.page(brain.build(_load(CASES[0])))
    for route in ("/ask/stream", "/worry", "/decision", "/reminders", "/follow-up", "/advisor-note", "/history"):
        assert route in page, f"the page never calls {route}"

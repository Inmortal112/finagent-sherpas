"""Integration gate: run before every merge to main (`./check.sh`)."""
import json
from pathlib import Path

import pytest

from contracts.schemas import Fact, Presentation, Scene, Visual
from finagent import brain, guard, run, voice

ROOT = Path(__file__).resolve().parents[1]
CASES = sorted((ROOT / "cases").glob("*/financial-health.json"))
CASE = ROOT / "cases" / "samantha-lewis" / "financial-health.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_pipeline_runs_end_to_end(tmp_path):
    page = run.main(CASE, tmp_path)
    assert page.exists()
    presentation = Presentation.model_validate_json((tmp_path / "presentation.json").read_text(encoding="utf-8"))
    assert presentation.scenes
    assert all(scene.duration_s for scene in presentation.scenes), "voice must set duration_s"
    assert presentation.client_name in page.read_text(encoding="utf-8")


def test_there_are_four_real_cases():
    assert len(CASES) == 4


@pytest.mark.parametrize("path", CASES, ids=lambda p: p.parent.name)
def test_brain_reads_every_real_case(path):
    diagnostic = _load(path)
    presentation = brain.build(diagnostic)
    facts = {f.id: f for f in presentation.facts}
    assert facts["score"].value == diagnostic["score"]["published_score"]
    assert len([f for f in facts if f.startswith("pillar_")]) == len(diagnostic["score"]["pillars"])
    assert presentation.language == "en"
    assert len({s.id for s in presentation.scenes}) == len(presentation.scenes), "scene ids name the audio files"
    assert guard.unsupported_numbers(presentation) == []


def test_guard_blocks_a_number_that_is_not_in_the_diagnostic():
    presentation = brain.build(_load(CASE))
    presentation.scenes[0].narration += " You save 9999 dollars a month."
    assert guard.unsupported_numbers(presentation) == [("intro", "9999")]


def test_guard_reads_point_as_decimal_and_comma_as_thousands():
    presentation = Presentation(
        client_name="Test",
        language="en",
        facts=[
            Fact(id="card", label="Card payment", value=6800, unit="$", source="test"),
            Fact(id="apr", label="Card APR", value=17.5, unit="%", source="test"),
        ],
        scenes=[
            Scene(id="ok", title="t", narration="Pay $6,800 on the 17.5% card, then 6800 is gone.",
                  visual=Visual(kind="text"), fact_ids=["card", "apr"]),
            Scene(id="bad", title="t", narration="Pay 6.8 dollars, or 6,801.",
                  visual=Visual(kind="text"), fact_ids=["card", "apr"]),
        ],
    )
    assert guard.unsupported_numbers(presentation) == [("bad", "6.8"), ("bad", "6,801")]


def test_voice_does_not_change_what_is_said(tmp_path):
    before = brain.build(_load(CASE))
    after = voice.synthesize(before, tmp_path)
    assert [s.narration for s in after.scenes] == [s.narration for s in before.scenes]


def test_published_schema_matches_the_code():
    published = json.loads((ROOT / "contracts" / "presentation.schema.json").read_text(encoding="utf-8"))
    assert published == Presentation.model_json_schema(), "run: python -m contracts.schemas"

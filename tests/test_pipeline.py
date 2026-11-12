"""Integration gate: run before every merge to main (`./check.sh`)."""
import json
from pathlib import Path

from contracts.schemas import Presentation
from finagent import brain, guard, run, voice

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "diagnostic_sample.json"


def test_pipeline_runs_end_to_end(tmp_path):
    page = run.main(FIXTURE, tmp_path)
    assert page.exists()
    presentation = Presentation.model_validate_json((tmp_path / "presentation.json").read_text(encoding="utf-8"))
    assert presentation.scenes
    assert all(scene.duration_s for scene in presentation.scenes), "voice must set duration_s"
    assert presentation.client_name in page.read_text(encoding="utf-8")


def test_guard_blocks_a_number_that_is_not_in_the_diagnostic():
    presentation = brain.build(json.loads(FIXTURE.read_text(encoding="utf-8")))
    presentation.scenes[0].narration += " Ahorras 9999 euros al mes."
    assert guard.unsupported_numbers(presentation) == [("intro", "9999")]


def test_voice_does_not_change_what_is_said(tmp_path):
    before = brain.build(json.loads(FIXTURE.read_text(encoding="utf-8")))
    after = voice.synthesize(before, tmp_path)
    assert [s.narration for s in after.scenes] == [s.narration for s in before.scenes]


def test_published_schema_matches_the_code():
    published = json.loads((ROOT / "contracts" / "presentation.schema.json").read_text(encoding="utf-8"))
    assert published == Presentation.model_json_schema(), "run: python -m contracts.schemas"

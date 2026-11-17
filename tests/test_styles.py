"""Explanation styles: the same scenes told another way, as a second track inside each page. No network."""
import json
from pathlib import Path

import pytest

from finagent import brain, narrator, run, stage, styles, voice

ROOT = Path(__file__).resolve().parents[1]
CASES = sorted((ROOT / "cases").glob("*/financial-health.json"))
WEAH = ROOT / "cases" / "timothy-melanie-weah" / "financial-health.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _track(out_dir: Path) -> dict:
    return json.loads((out_dir / styles.FILE).read_text(encoding="utf-8"))


def test_every_style_has_the_words_the_family_reads():
    assert styles.names() == ["story", *narrator.STYLES]
    for name in styles.names():
        assert styles.LABELS[name]["label"] and styles.LABELS[name]["hint"], name


@pytest.mark.parametrize("path", CASES, ids=lambda p: p.parent.name)
def test_the_full_page_carries_the_other_style_scene_by_scene(path, tmp_path, monkeypatch):
    monkeypatch.setenv("VOICE_ENGINE", "mock")
    presentation = brain.build(_load(path))
    assert styles.add_tracks(presentation, path.parent.name, "complete", tmp_path) == ["numbers"]
    track = _track(tmp_path)
    assert track["default"] == {"name": "story", **styles.LABELS["story"]}
    numbers = track["styles"]["numbers"]
    assert numbers["label"] == "Numbers first"
    assert set(numbers["scenes"]) == {scene.id for scene in presentation.scenes}
    saved = narrator.saved_texts(path.parent.name, style="numbers")
    for scene in presentation.scenes:
        entry = numbers["scenes"][scene.id]
        assert entry["text"] == saved[scene.id] != scene.narration
        assert entry["audio"] is None and entry["duration_s"] > 0, "the mock voice has no audio, only a duration"
    assert [scene.narration for scene in presentation.scenes] == [s.narration for s in brain.build(_load(path)).scenes], \
        "the narration itself is never touched"


def test_the_simple_mode_has_one_way_of_explaining(tmp_path, monkeypatch):
    monkeypatch.setenv("VOICE_ENGINE", "mock")
    (tmp_path / styles.FILE).write_text("{}", encoding="utf-8")   # left by an older run
    presentation = brain.build(_load(WEAH), mode="simple")
    assert styles.add_tracks(presentation, WEAH.parent.name, "simple", tmp_path) == []
    assert not (tmp_path / styles.FILE).exists()


def test_the_other_voice_sits_next_to_the_page(tmp_path, monkeypatch):
    """With a real engine each scene of the style has its own MP3 under styles/<style>/audio/."""
    def fake(presentation, out_dir):
        (out_dir / voice.AUDIO_DIR).mkdir(parents=True, exist_ok=True)
        for scene in presentation.scenes:
            scene.audio_path, scene.duration_s = f"{voice.AUDIO_DIR}/{scene.id}.mp3", 3.0
            (out_dir / scene.audio_path).write_bytes(scene.narration.encode("utf-8"))
        return presentation

    monkeypatch.setattr(voice, "synthesize", fake)
    presentation = brain.build(_load(WEAH))
    styles.add_tracks(presentation, WEAH.parent.name, "complete", tmp_path)
    scenes = _track(tmp_path)["styles"]["numbers"]["scenes"]
    assert scenes["intro"]["audio"] == "styles/numbers/audio/intro.mp3"
    for scene_id, entry in scenes.items():
        assert (tmp_path / entry["audio"]).read_text(encoding="utf-8") == entry["text"], scene_id
    assert not (tmp_path / "audio").exists(), "the story's own audio folder is the voice stage's, not this one's"


def test_a_failure_never_breaks_the_page(tmp_path, monkeypatch):
    def broken(*args, **kwargs):
        raise RuntimeError("no voice today")

    monkeypatch.setattr(voice, "synthesize", broken)
    assert styles.add_tracks(brain.build(_load(WEAH)), WEAH.parent.name, "complete", tmp_path) == []
    assert not (tmp_path / styles.FILE).exists()


def test_the_pipeline_writes_the_track_and_the_page_loads_it(tmp_path, monkeypatch):
    monkeypatch.setenv("VOICE_ENGINE", "mock")
    page = run.main(WEAH, tmp_path / "complete").read_text(encoding="utf-8")
    run.main(WEAH, tmp_path / "simple", "simple")
    assert "numbers" in _track(tmp_path / "complete")["styles"]
    assert not (tmp_path / "simple" / styles.FILE).exists()
    assert 'import(SITE + "web/styles.js")' in page and "styles.forPerson(name)" in page
    assert stage.TEMPLATE.with_name("web").joinpath("styles.js").exists()


def test_the_switch_is_served_from_the_repo():
    from fastapi.testclient import TestClient
    from finagent import server

    module = TestClient(server.app).get("/web/styles.js")
    assert module.status_code == 200 and "javascript" in module.headers["content-type"]
    assert 'fetch("styles.json")' in module.text
    assert "http://" not in module.text and "https://" not in module.text

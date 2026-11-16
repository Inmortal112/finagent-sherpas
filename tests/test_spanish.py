"""Listen in Spanish: checked translations, the Spanish spoken copy and the second audio track. No network."""
import json
from pathlib import Path

import pytest

from contracts.schemas import Presentation, Scene, Visual
from finagent import brain, spanish, voice

ENGLISH = "[FICTIONAL EXAMPLE] Your card of $18,000 at 24.9% costs you. Your score goes from 52 to 57."
GOOD = "[EJEMPLO FICTICIO] Tu tarjeta de $18,000 al 24.9% te cuesta. Tu puntuación pasa de 52 a 57."


def _store(directory: Path, slug: str, scenes: dict) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / f"{slug}.json").write_text(json.dumps({"scenes": scenes}, ensure_ascii=False), encoding="utf-8")


def test_a_translation_must_keep_every_figure():
    assert spanish.same_figures(ENGLISH, GOOD)
    assert not spanish.same_figures(ENGLISH, GOOD.replace("$18,000", "$18.000"))      # reformatted
    assert not spanish.same_figures(ENGLISH, GOOD.replace("24.9%", "25%"))            # rounded
    assert not spanish.same_figures(ENGLISH, GOOD.replace("de 52 a 57", "cinco puntos"))  # dropped


def test_only_valid_translations_are_used(tmp_path):
    english = {"a": ENGLISH, "b": ENGLISH, "c": ENGLISH, "d": ENGLISH}
    _store(tmp_path, "fam", {
        "a": {"from": spanish.fingerprint(ENGLISH), "es": GOOD},
        "b": {"from": spanish.fingerprint("an older English text"), "es": GOOD},          # the English changed
        "c": {"from": spanish.fingerprint(ENGLISH), "es": GOOD.replace("57", "58")},      # a figure differs
    })
    assert spanish.saved("fam", "complete", english, tmp_path) == {"a": GOOD}
    assert spanish.saved("nobody", "complete", english, tmp_path) == {}


def test_the_saved_translations_match_today_s_narrations():
    """Every scene of the four families has a Spanish text with the same figures as its English."""
    for case in sorted((spanish.ROOT / "cases").glob("*/financial-health.json")):
        diagnostic = json.loads(case.read_text(encoding="utf-8"))
        for mode in brain.MODES:
            english = {scene.id: scene.narration for scene in brain.build(diagnostic, mode=mode).scenes}
            valid = spanish.saved(case.parent.name, mode, english)
            missing = sorted(set(english) - set(valid))
            assert not missing, f"{case.parent.name}/{mode}: run `python -m finagent.spanish` (stale: {missing})"


def test_numbers_in_spanish_words():
    n = spanish.numero_en_palabras
    assert n(0) == "cero" and n(16) == "dieciséis" and n(100) == "cien" and n(101) == "ciento uno"
    assert n(1000) == "mil" and n(21000) == "veintiún mil" and n(31000) == "treinta y un mil"
    assert n(1166000) == "un millón ciento sesenta y seis mil"
    assert n(2371901) == "dos millones trescientos setenta y un mil novecientos uno"
    assert n(21, before_noun=True) == "veintiún" and n(1, before_noun=True) == "un"


def test_the_spanish_spoken_copy():
    said = spanish.to_speech_es("Tu cobertura es de $200,000, que son $1,000,000 menos. La tarjeta, al 24.9%; "
                                "y $1M más. Sube de 52 a 57 en 2027.")
    assert said == ("Tu cobertura es de doscientos mil dólares, que son un millón de dólares menos. La tarjeta, "
                    "al 24 punto nueve por ciento; y un millón de dólares más. Sube de 52 a 57 en 2027.")
    assert spanish.to_speech_es("Salen -$8,336 al año y $21.") == "Salen menos ocho mil trescientos treinta y seis dólares al año y veintiún dólares."


def _presentation():
    scene = Scene(id="intro", title="Intro", narration=ENGLISH, visual=Visual(kind="title"))
    return Presentation(client_name="Example", language="en", facts=[], scenes=[scene])


def test_the_spanish_track_is_written_next_to_the_page(monkeypatch, tmp_path):
    monkeypatch.setenv("VOICE_ENGINE", "edge")
    _store(tmp_path / "es", "fam", {"intro": {"from": spanish.fingerprint(ENGLISH), "es": GOOD}})
    monkeypatch.setattr(spanish, "ES_DIR", tmp_path / "es")
    sent = []

    async def fake_edge(text, voice_name):
        sent.append((text, voice_name))
        return b"\x00" * 12000, []

    monkeypatch.setattr(voice, "_edge_speech", fake_edge)
    out = tmp_path / "out"
    out.mkdir()
    assert spanish.add_audio(_presentation(), "fam", "complete", out) == 1
    assert sent == [(spanish.to_speech_es(GOOD), spanish.EDGE_VOICE)]          # the spoken copy, a Spanish voice
    assert (out / "audio" / "es" / "intro.mp3").exists()
    assert json.loads((out / "es.json").read_text(encoding="utf-8")) == {"intro": GOOD}
    words = json.loads((out / "audio" / "es" / "intro.words.json").read_text(encoding="utf-8"))["words"]
    assert [GOOD[a:b] for a, b, _, _ in words] == GOOD.split()               # captions follow the Spanish text


@pytest.mark.parametrize("engine, slug", [("mock", "fam"), ("edge", "no-translations")])
def test_no_track_without_a_voice_or_without_translations(monkeypatch, tmp_path, engine, slug):
    monkeypatch.setenv("VOICE_ENGINE", engine)
    _store(tmp_path / "es", "fam", {"intro": {"from": spanish.fingerprint(ENGLISH), "es": GOOD}})
    monkeypatch.setattr(spanish, "ES_DIR", tmp_path / "es")
    assert spanish.add_audio(_presentation(), slug, "complete", tmp_path) == 0
    assert not (tmp_path / "es.json").exists()


def test_translating_keeps_only_what_passes_the_check(monkeypatch, tmp_path):
    class Reply:
        def __init__(self, scenes):
            self.choices = [type("C", (), {"message": type("M", (), {"content": json.dumps({"scenes": scenes})})()})()]

    class Client:
        calls = 0

        @property
        def chat(self):
            return self

        @property
        def completions(self):
            return self

        def create(self, model, messages, response_format):
            Client.calls += 1
            asked = json.loads(messages[1]["content"])["scenes"]
            # Every scene comes back with one figure changed: all must be refused, twice.
            return Reply({scene_id: "Texto con 999999 inventado." for scene_id in asked})

    done, refused = spanish.translate_family("michael-carter", Client(), "test-model", tmp_path)
    assert done == 0 and refused and Client.calls == 4          # two modes, one retry each
    stored = json.loads((tmp_path / "michael-carter.json").read_text(encoding="utf-8"))
    assert stored["scenes"] == {} and stored["simple"] == {}

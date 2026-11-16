"""Captions that follow the voice. No network: the engines are faked."""
import base64
import json

import pytest

from contracts.schemas import Presentation, Scene, Visual
from finagent import captions, voice, voice_eleven
from finagent.speech_text import to_speech

NARRATION = "[FICTIONAL EXAMPLE] You save $1,200/yr — about 3% — in your 401(k)."


def _words(narration, timed):
    return [(narration[a:b], start, end) for a, b, start, end in captions.align(narration, timed)]


def test_same_words_keep_their_times():
    timed = [("Hello", 0.1, 0.4), ("there", 0.5, 0.9)]
    assert _words("Hello there.", timed) == [("Hello", 0.1, 0.4), ("there.", 0.5, 0.9)]


def test_a_written_figure_is_lit_while_its_spoken_form_is_said():
    timed = [("You", 0.0, 0.2), ("save", 0.2, 0.5), ("$1,200", 0.5, 1.4), ("a", 1.4, 1.5), ("year", 1.5, 1.9),
             ("now", 2.0, 2.3)]
    words = _words("You save $1,200/yr now", timed)
    assert words[2] == ("$1,200/yr", 0.5, 1.9)      # from the start of "$1,200" to the end of "year"
    assert words[3] == ("now", 2.0, 2.3)


def test_every_written_word_gets_a_time_in_order_and_the_text_is_untouched():
    spoken = to_speech(NARRATION)
    words = captions.align(NARRATION, captions.estimate(spoken, 8.0))
    assert [NARRATION[a:b] for a, b, _, _ in words] == NARRATION.split()
    starts = [start for _, _, start, _ in words]
    assert starts == sorted(starts) and all(end >= start for _, _, start, end in words)
    assert words[-1][3] <= 8.01


def test_estimate_shares_the_duration_by_length():
    timed = captions.estimate("a bbb", 6.0)
    assert timed[0][1] == 0.0 and timed[0][2] == pytest.approx(2.0) and timed[1][2] == pytest.approx(6.0)


def test_characters_become_words():
    timed = captions.from_characters(list("Hi you"), [0, .1, .2, .3, .4, .5], [.1, .2, .3, .4, .5, .6])
    assert timed == [("Hi", 0, .2), ("you", .3, .6)]


def test_nothing_to_align_gives_no_words():
    assert captions.align("", [("a", 0, 1)]) == [] and captions.align("Hello", []) == []


def _presentation():
    scene = Scene(id="intro", title="Intro", narration=NARRATION, visual=Visual(kind="title"))
    return Presentation(client_name="Example", language="en", facts=[], scenes=[scene])


def test_edge_writes_the_words_next_to_the_audio(monkeypatch, tmp_path):
    monkeypatch.setenv("VOICE_ENGINE", "edge")

    async def fake_edge(text, voice_name):
        return b"\x00" * 12000, captions.estimate(text, 2.0)   # 2 seconds of "audio" with word times

    monkeypatch.setattr(voice, "_edge_speech", fake_edge)
    after = voice.synthesize(_presentation(), tmp_path)
    saved = json.loads((tmp_path / "audio" / "intro.words.json").read_text(encoding="utf-8"))["words"]
    assert [NARRATION[a:b] for a, b, _, _ in saved] == NARRATION.split()
    assert after.scenes[0].narration == NARRATION and after.scenes[0].audio_path == "audio/intro.mp3"


def test_eleven_keeps_the_timings_it_is_sent(monkeypatch, tmp_path):
    for name, value in {"VOICE_ENGINE": "eleven", "ELEVENLABS_API_KEY": "test-key", "TEAM_KEY": "", "LLM_PROXY_URL": "",
                        "ELEVEN_VOICE_ID": "", "ELEVEN_MODEL": "", "ELEVEN_MAX_CHARS": "", "ELEVEN_MAX_CHARS_PER_DAY": "",
                        "VOICE_CACHE_DIR": str(tmp_path / "cache")}.items():
        monkeypatch.setenv(name, value)
    mp3 = b"\xff\xfb\x90\x00" + b"\x00" * 16000   # one second at 128 kbit/s

    def fake_post(request):
        assert "/with-timestamps" in request.full_url
        text = json.loads(request.data)["text"]
        times = [round(i * 0.05, 2) for i in range(len(text) + 1)]
        return json.dumps({"audio_base64": base64.b64encode(mp3).decode(),
                           "alignment": {"characters": list(text), "character_start_times_seconds": times[:-1],
                                         "character_end_times_seconds": times[1:]}}).encode()

    monkeypatch.setattr(voice_eleven, "_post", fake_post)
    voice.synthesize(_presentation(), tmp_path / "out")
    assert (tmp_path / "out" / "audio" / "intro.mp3").read_bytes() == mp3
    saved = json.loads((tmp_path / "out" / "audio" / "intro.words.json").read_text(encoding="utf-8"))["words"]
    assert [NARRATION[a:b] for a, b, _, _ in saved] == NARRATION.split()
    assert saved[0][2] == 0.0 and saved[1][2] > saved[0][2]   # real times, not all zero

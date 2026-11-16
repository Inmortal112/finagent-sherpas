"""ElevenLabs engine, with the HTTP call faked: these tests never send anything or spend credits."""
import json
import urllib.error

import pytest

from contracts.schemas import Presentation, Scene, Visual
from finagent import voice, voice_eleven

# One MPEG-1 layer III frame header at 128 kbit/s; 16,000 bytes of it last exactly one second.
ONE_SECOND_MP3 = b"\xff\xfb\x90\x64" + bytes(16_000 - 4)


def _presentation() -> Presentation:
    scenes = [
        Scene(id="intro", title="Intro", narration="[FICTIONAL EXAMPLE] Hello. You save $1,200/yr.", visual=Visual(kind="title")),
        Scene(id="move_1", title="Move", narration="[FICTIONAL EXAMPLE] Open an IRA.", visual=Visual(kind="title")),
    ]
    return Presentation(client_name="Example", language="en", facts=[], scenes=scenes)


@pytest.fixture
def eleven(monkeypatch, tmp_path):
    """VOICE_ENGINE=eleven with a fake key, a temporary cache and a recorded, fake HTTP call."""
    for name, value in {"VOICE_ENGINE": "eleven", "ELEVENLABS_API_KEY": "test-key", "TEAM_KEY": "",
                        "LLM_PROXY_URL": "", "ELEVEN_VOICE_ID": "", "ELEVEN_MODEL": "",
                        "ELEVEN_MAX_CHARS": "", "ELEVEN_MAX_CHARS_PER_DAY": "", "VOICE_CACHE_DIR": str(tmp_path / "cache")}.items():
        monkeypatch.setenv(name, value)  # set even when empty, so the real .env cannot fill them in
    calls = []

    def fake_post(request):
        calls.append(request)
        return ONE_SECOND_MP3

    monkeypatch.setattr(voice_eleven, "_post", fake_post)
    edge_runs = []

    async def fake_edge(scenes, out_dir, voice_name, language):
        edge_runs.append(len(scenes))
        for scene in scenes:
            scene.audio_path, scene.duration_s = f"audio/{scene.id}.mp3", 9.9

    monkeypatch.setattr(voice, "_edge_all", fake_edge)
    return calls, edge_runs


def test_direct_route_writes_audio_and_measures_it(eleven, tmp_path):
    calls, edge_runs = eleven
    before = _presentation()
    after = voice.synthesize(before, tmp_path / "out")

    assert len(calls) == 2 and not edge_runs
    request = calls[0]
    assert request.full_url.startswith("https://api.elevenlabs.io/v1/text-to-speech/XrExE9yKIg1WjnnlVkGX")
    assert request.get_header("Xi-api-key") == "test-key"
    bodies = [json.loads(call.data) for call in calls]
    assert {body["model_id"] for body in bodies} == {"eleven_flash_v2_5"}
    # The spoken copy, not narration; and for ElevenLabs the long figure goes in words.
    assert "one thousand two hundred dollars a year" in " ".join(body["text"] for body in bodies)
    for scene in after.scenes:
        assert (tmp_path / "out" / scene.audio_path).read_bytes() == ONE_SECOND_MP3
        assert scene.duration_s == 1.0
    assert [s.narration for s in after.scenes] == [s.narration for s in before.scenes]


def test_cached_text_is_never_paid_twice(eleven, tmp_path):
    calls, _ = eleven
    voice.synthesize(_presentation(), tmp_path / "first")
    voice.synthesize(_presentation(), tmp_path / "second")
    assert len(calls) == 2  # the second run only reads the cache
    assert (tmp_path / "second" / "audio" / "intro.mp3").exists()


def test_over_budget_sends_nothing_and_uses_edge(eleven, tmp_path, monkeypatch):
    calls, edge_runs = eleven
    monkeypatch.setenv("ELEVEN_MAX_CHARS", "10")
    after = voice.synthesize(_presentation(), tmp_path)
    assert not calls and edge_runs == [2]
    assert all(scene.duration_s == 9.9 for scene in after.scenes)


def test_daily_cap_adds_up_across_runs(eleven, monkeypatch):
    calls, _ = eleven
    monkeypatch.setenv("ELEVEN_MAX_CHARS_PER_DAY", "60")
    first = voice.speak("[FICTIONAL EXAMPLE] Open an IRA this year.")
    assert first.engine == "eleven" and len(calls) == 1
    assert voice_eleven.chars_sent_today() == len(json.loads(calls[0].data)["text"])

    monkeypatch.setattr(voice, "_edge_bytes", _no_edge_audio)
    second = voice.speak("[FICTIONAL EXAMPLE] Then look at your savings account.")
    assert second.engine != "eleven" and len(calls) == 1  # over today's cap: nothing more is sent

    again = voice.speak("[FICTIONAL EXAMPLE] Open an IRA this year.")
    assert again.engine == "eleven" and len(calls) == 1   # cached audio is free, so it still plays


def test_daily_count_starts_again_the_next_day(eleven, tmp_path):
    usage = tmp_path / "cache" / "usage.json"
    usage.parent.mkdir(parents=True)
    usage.write_text(json.dumps({"date": "2026-01-01", "chars": 999_999}), encoding="utf-8")
    assert voice_eleven.chars_sent_today() == 0
    usage.write_text("not json", encoding="utf-8")
    assert voice_eleven.chars_sent_today() == 0


async def _no_edge_audio(text, voice_name):
    return b""


def test_no_key_uses_edge(eleven, tmp_path, monkeypatch):
    calls, edge_runs = eleven
    monkeypatch.setenv("ELEVENLABS_API_KEY", "")
    voice.synthesize(_presentation(), tmp_path)
    assert not calls and edge_runs == [2]


def test_service_error_uses_edge(eleven, tmp_path, monkeypatch):
    _, edge_runs = eleven

    def refuse(request):
        raise urllib.error.HTTPError(request.full_url, 401, "quota_exceeded", {}, None)

    monkeypatch.setattr(voice_eleven, "_post", refuse)
    voice.synthesize(_presentation(), tmp_path)
    assert edge_runs == [2]


def test_without_personal_key_goes_through_the_sherpas_proxy(eleven, tmp_path, monkeypatch):
    calls, _ = eleven
    monkeypatch.setenv("ELEVENLABS_API_KEY", "")
    monkeypatch.setenv("TEAM_KEY", "team-test-key")
    monkeypatch.setenv("LLM_PROXY_URL", "https://proxy.example/")
    voice.synthesize(_presentation(), tmp_path)
    request = calls[0]
    assert request.full_url == "https://proxy.example/v1/audio/speech"
    assert request.get_header("Authorization") == "Bearer team-test-key"
    body = json.loads(request.data)
    assert body["model"] == "eleven-flash-v2.5" and body["voice"] == "XrExE9yKIg1WjnnlVkGX"


def test_model_accepts_either_spelling(monkeypatch):
    monkeypatch.setenv("ELEVENLABS_API_KEY", "test-key")
    monkeypatch.setenv("ELEVEN_MODEL", "eleven-multilingual-v2")
    assert voice_eleven.route_from_env().model == "eleven_multilingual_v2"


def test_mp3_duration_skips_an_id3_tag():
    tag = b"ID3\x04\x00\x00\x00\x00\x00\x0a" + bytes(10)  # 10-byte header + 10 bytes of tag
    assert voice_eleven.mp3_duration_s(tag + ONE_SECOND_MP3) == 1.0

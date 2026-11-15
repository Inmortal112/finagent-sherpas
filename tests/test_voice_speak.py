"""voice.speak: one live answer (the /ask route) to MP3. HTTP and edge-tts are faked: nothing is spent."""
import asyncio
import json

import pytest

from finagent import voice, voice_eleven

ONE_SECOND_MP3 = b"\xff\xfb\x90\x64" + bytes(16_000 - 4)  # 128 kbit/s, 16,000 bytes = 1 s
ANSWER = "[FICTIONAL EXAMPLE] Your **roof** needs $1,200/yr."


@pytest.fixture
def engines(monkeypatch, tmp_path):
    for name, value in {"VOICE_ENGINE": "eleven", "ELEVENLABS_API_KEY": "test-key", "TEAM_KEY": "",
                        "LLM_PROXY_URL": "", "ELEVEN_VOICE_ID": "", "ELEVEN_MODEL": "",
                        "ELEVEN_MAX_CHARS": "", "ELEVEN_MAX_CHARS_PER_DAY": "", "VOICE_CACHE_DIR": str(tmp_path / "cache"),
                        "VOICE_NAME": ""}.items():
        monkeypatch.setenv(name, value)  # set even when empty, so the real .env cannot fill them in
    sent = {"eleven": [], "edge": []}

    def fake_post(request):
        sent["eleven"].append(json.loads(request.data)["text"])
        return ONE_SECOND_MP3

    async def fake_edge(text, voice_name):
        sent["edge"].append(text)
        return bytes(6_000)  # edge: 48 kbit/s, 6,000 bytes = 1 s

    monkeypatch.setattr(voice_eleven, "_post", fake_post)
    monkeypatch.setattr(voice, "_edge_bytes", fake_edge)
    return sent


def test_eleven_speaks_the_spoken_copy(engines):
    spoken = voice.speak(ANSWER)
    assert spoken.engine == "eleven" and spoken.audio == ONE_SECOND_MP3 and spoken.duration_s == 1.0
    assert engines["eleven"] == ["[FICTIONAL EXAMPLE] Your roof needs $1,200 a year."]


def test_same_answer_twice_is_paid_once(engines):
    voice.speak(ANSWER)
    voice.speak(ANSWER)
    assert len(engines["eleven"]) == 1


def test_falls_back_to_edge(engines, monkeypatch):
    monkeypatch.setenv("ELEVENLABS_API_KEY", "")
    spoken = voice.speak(ANSWER)
    assert spoken.engine == "edge" and spoken.duration_s == 1.0 and not engines["eleven"]


def test_never_raises_when_no_engine_can_speak(engines, monkeypatch):
    monkeypatch.setenv("VOICE_ENGINE", "edge")

    async def broken_edge(text, voice_name):
        raise ConnectionError("no internet")

    monkeypatch.setattr(voice, "_edge_bytes", broken_edge)
    spoken = voice.speak(ANSWER)
    assert spoken.engine == "mock" and spoken.audio is None and spoken.duration_s >= 2.0


def test_can_be_awaited_inside_a_running_event_loop(engines):
    async def route():  # what a FastAPI route does: await it inside the server's event loop
        return await voice.speak_async(ANSWER)

    assert asyncio.run(route()).engine == "eleven"

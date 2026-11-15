"""voice.transcribe: the family's spoken question -> text. HTTP is faked: nothing is sent or spent."""
import asyncio
import json
import urllib.error

import pytest

from finagent import voice, voice_eleven

RECORDING = b"\x1aE\xdf\xa3" + bytes(2_000)  # starts like a browser webm recording; content does not matter


@pytest.fixture
def scribe(monkeypatch):
    for name, value in {"ELEVENLABS_API_KEY": "test-key", "TEAM_KEY": "", "LLM_PROXY_URL": "",
                        "ELEVEN_STT_MODEL": ""}.items():
        monkeypatch.setenv(name, value)  # set even when empty, so the real .env cannot fill them in
    calls = []

    def fake_post(request):
        calls.append(request)
        return json.dumps({"language_code": "en", "text": "  What does my roof mean?  "}).encode()

    monkeypatch.setattr(voice_eleven, "_post", fake_post)
    return calls


def _fields(request) -> str:
    return request.data.decode("latin-1")


def test_direct_route_sends_the_recording_and_returns_clean_text(scribe):
    heard = voice.transcribe(RECORDING, "question.webm")
    assert heard.text == "What does my roof mean?" and heard.engine == "eleven"
    request = scribe[0]
    assert request.full_url == "https://api.elevenlabs.io/v1/speech-to-text"
    assert request.get_header("Xi-api-key") == "test-key"
    assert request.get_header("Content-type").startswith("multipart/form-data; boundary=")
    body = _fields(request)
    assert 'name="model_id"\r\n\r\nscribe_v2' in body
    assert 'name="language_code"\r\n\r\nen' in body
    assert 'filename="question.webm"' in body
    assert RECORDING in request.data


def test_without_personal_key_goes_through_the_sherpas_proxy(scribe, monkeypatch):
    monkeypatch.setenv("ELEVENLABS_API_KEY", "")
    monkeypatch.setenv("TEAM_KEY", "team-test-key")
    monkeypatch.setenv("LLM_PROXY_URL", "https://proxy.example")
    voice.transcribe(RECORDING, "question.ogg")
    request = scribe[0]
    assert request.full_url == "https://proxy.example/v1/audio/transcriptions"
    assert request.get_header("Authorization") == "Bearer team-test-key"
    assert 'name="model"\r\n\r\nscribe-v2' in _fields(request)


def test_filename_cannot_break_the_upload(scribe):
    voice.transcribe(RECORDING, '../../evil".webm')
    assert 'filename="evil.webm"' in _fields(scribe[0])


@pytest.mark.parametrize("audio", [b"", bytes(voice_eleven.MAX_AUDIO_BYTES + 1)])
def test_empty_or_huge_audio_is_not_sent(scribe, audio):
    heard = voice.transcribe(audio)
    assert heard.text is None and not scribe


def test_never_raises_on_a_service_error(scribe, monkeypatch):
    def refuse(request):
        raise urllib.error.HTTPError(request.full_url, 401, "missing_permissions", {}, None)

    monkeypatch.setattr(voice_eleven, "_post", refuse)
    assert voice.transcribe(RECORDING) == voice.Transcript(None, "none")


def test_silence_gives_no_text(scribe, monkeypatch):
    monkeypatch.setattr(voice_eleven, "_post", lambda request: b'{"text": "   "}')
    assert voice.transcribe(RECORDING).text is None


def test_no_key_gives_no_text(scribe, monkeypatch):
    monkeypatch.setenv("ELEVENLABS_API_KEY", "")
    assert voice.transcribe(RECORDING).text is None and not scribe


def test_can_be_awaited_inside_a_running_event_loop(scribe):
    async def route():  # what a FastAPI route does
        return await voice.transcribe_async(RECORDING)

    assert asyncio.run(route()).text == "What does my roof mean?"

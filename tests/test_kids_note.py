"""The home explained to the children: by name, no figures, two tones. No network: the voice is faked."""
import json
import re

import pytest
from fastapi.testclient import TestClient

from finagent import brain, kids_note, server, voice


def _plan(family):
    return brain.build(json.loads((server.CASES / family / "financial-health.json").read_text(encoding="utf-8")))


def test_young_children_by_name_with_the_parts_that_need_work():
    note = kids_note.build(_plan("daniel-emily-johnson"))
    assert note["available"] and note["to"] == ["Oliver", "Sophia"]
    text = note["text"]
    assert text.startswith("Oliver and Sophia, this is your family's home.")
    assert "The roof keeps everyone safe" in text and "Right now it needs real work." in text   # the roof is broken
    assert text.endswith("cheer them on.")


def test_teenagers_get_the_grown_up_tone():
    text = kids_note.build(_plan("samantha-lewis"))["text"]
    assert text.startswith("Ethan and Ava, ") and "college" in text and "one day this will be your own plan" in text


@pytest.mark.parametrize("family", ["daniel-emily-johnson", "samantha-lewis", "timothy-melanie-weah"])
def test_no_figures_no_mom_or_dad_and_short(family):
    text = kids_note.build(_plan(family))["text"]
    assert not re.search(r"\d", text)
    assert not re.search(r"\b(mom|mum|dad|mother|father|he|she|his|her)\b", text, re.I)
    assert len(text.split()) <= 125          # about forty seconds


def test_no_children_no_note():
    assert not kids_note.build(_plan("michael-carter"))["available"]


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("SESSIONS_DIR", str(tmp_path))
    spoken = []

    async def speak(text, language="en"):
        spoken.append(text)
        return voice.SpokenAudio(b"mp3", 1.0, "test")

    monkeypatch.setattr(voice, "speak_async", speak)
    test_client = TestClient(server.app)
    test_client.spoken = spoken
    return test_client


def test_the_page_gets_the_note_and_its_audio_once(client):
    note = client.get("/kids-note", params={"family": "timothy-melanie-weah"}).json()
    assert note["available"] and note["to"] == ["Liam", "Josh"]
    audio = client.get(note["audio_url"])
    assert audio.status_code == 200 and audio.content == b"mp3" and audio.headers["content-type"] == "audio/mpeg"
    client.get(note["audio_url"])
    assert client.spoken == [note["text"]]
    assert client.get("/kids-note/michael-carter.mp3").status_code == 404
    assert client.get("/kids-note", params={"family": "nobody"}).status_code == 404

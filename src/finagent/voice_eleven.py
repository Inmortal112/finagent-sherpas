"""ElevenLabs for `voice`: speech (VOICE_ENGINE=eleven) and speech to text (Scribe, for spoken questions).
Only the standard library: no new dependency.

Two ways to reach ElevenLabs, picked from .env:
- ELEVENLABS_API_KEY set -> straight to api.elevenlabs.io with that (personal, student) account.
- otherwise TEAM_KEY + LLM_PROXY_URL -> the Sherpas proxy (OpenAI-compatible /v1/audio/speech).
  It shares the team's $1.40 ElevenLabs allowance, so it is the fallback, not the default.

Spending guards (ElevenLabs bills per character):
- Cache: each audio is stored under a hash of (route, model, voice, text). The same text with the same
  voice is never paid for twice. Folder: VOICE_CACHE_DIR, default out/voice_cache (git-ignored).
- Budget: ELEVEN_MAX_CHARS (default 6000) caps the characters sent in one run, counting only the
  scenes not already cached. Over the cap, nothing is sent and `voice` falls back to edge-tts.
- Daily budget: ELEVEN_MAX_CHARS_PER_DAY (default 20000) caps the characters sent in one day, adding up
  every run and every live answer. It is what protects the account while a public link is open. The count
  is kept in <cache folder>/usage.json and starts again each day; over the cap, `voice` falls back to edge-tts.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import threading
import urllib.request
from dataclasses import dataclass
from datetime import date
from pathlib import Path

log = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
DIRECT_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}?output_format=mp3_44100_128"
DEFAULT_VOICE_ID = "XrExE9yKIg1WjnnlVkGX"  # Matilda: American, "knowledgeable, professional" (premade)
DEFAULT_MODEL = "eleven_flash_v2_5"         # cheapest and fastest
DEFAULT_MAX_CHARS = 6000                    # one family is about 1,000 characters
DEFAULT_MAX_CHARS_PER_DAY = 20000           # about 80 live answers; the student plan gives ~130,000 a month
TIMEOUT_S = 60
# The same three models have different names on each route.
PROXY_MODEL_NAMES = {
    "eleven_flash_v2_5": "eleven-flash-v2.5",
    "eleven_multilingual_v2": "eleven-multilingual-v2",
    "eleven_v3": "eleven-v3",
}


class BudgetExceeded(RuntimeError):
    pass


@dataclass(frozen=True)
class Route:
    name: str      # "direct" or "proxy"
    url: str
    headers: dict
    model: str
    voice_id: str

    def request(self, text: str) -> urllib.request.Request:
        if self.name == "direct":
            body = {"text": text, "model_id": self.model}
        else:
            body = {"model": self.model, "input": text, "voice": self.voice_id, "response_format": "mp3"}
        headers = {**self.headers, "Content-Type": "application/json", "Accept": "audio/mpeg"}
        return urllib.request.Request(self.url, data=json.dumps(body).encode(), headers=headers, method="POST")


def route_from_env() -> Route:
    voice_id = os.getenv("ELEVEN_VOICE_ID") or DEFAULT_VOICE_ID
    model = _canonical_model(os.getenv("ELEVEN_MODEL") or DEFAULT_MODEL)
    if key := (os.getenv("ELEVENLABS_API_KEY") or "").strip():
        return Route("direct", DIRECT_URL.format(voice_id=voice_id), {"xi-api-key": key}, model, voice_id)
    team_key = (os.getenv("TEAM_KEY") or "").strip()
    proxy = (os.getenv("LLM_PROXY_URL") or "").strip().rstrip("/")
    if team_key and proxy:
        base = proxy if proxy.endswith("/v1") else f"{proxy}/v1"
        return Route("proxy", f"{base}/audio/speech", {"Authorization": f"Bearer {team_key}"},
                     PROXY_MODEL_NAMES.get(model, model), voice_id)
    raise RuntimeError("no ElevenLabs key: set ELEVENLABS_API_KEY, or TEAM_KEY and LLM_PROXY_URL, in .env")


def _canonical_model(name: str) -> str:
    """Accept either spelling ("eleven-flash-v2.5" or "eleven_flash_v2_5")."""
    name = name.strip()
    for canonical, proxy_name in PROXY_MODEL_NAMES.items():
        if name == proxy_name:
            return canonical
    return name


def cache_dir() -> Path:
    return Path(os.getenv("VOICE_CACHE_DIR") or ROOT / "out" / "voice_cache")


def cache_path(route: Route, text: str) -> Path:
    digest = hashlib.sha256("\n".join([route.name, route.model, route.voice_id, text]).encode()).hexdigest()
    return cache_dir() / f"{digest[:24]}.mp3"


def max_chars() -> int:
    return int(os.getenv("ELEVEN_MAX_CHARS") or DEFAULT_MAX_CHARS)


def max_chars_per_day() -> int:
    return int(os.getenv("ELEVEN_MAX_CHARS_PER_DAY") or DEFAULT_MAX_CHARS_PER_DAY)


_usage_lock = threading.Lock()


def _usage_path() -> Path:
    return cache_dir() / "usage.json"


def chars_sent_today() -> int:
    """Characters sent to ElevenLabs today (cached audio is not counted: it was not sent)."""
    try:
        usage = json.loads(_usage_path().read_text(encoding="utf-8"))
        return int(usage["chars"]) if usage.get("date") == date.today().isoformat() else 0
    except (OSError, ValueError, KeyError, TypeError, AttributeError):  # no file yet, or a damaged one
        return 0


def _count_sent(chars: int) -> None:
    with _usage_lock:
        total = chars_sent_today() + chars
        _usage_path().parent.mkdir(parents=True, exist_ok=True)
        _usage_path().write_text(json.dumps({"date": date.today().isoformat(), "chars": total}), encoding="utf-8")


async def synthesize_all(texts: dict[str, str], parallel: int) -> dict[str, bytes]:
    """Audio for every {scene_id: spoken text}, from the cache or from ElevenLabs."""
    route = route_from_env()
    paths = {scene_id: cache_path(route, text) for scene_id, text in texts.items()}
    missing = {scene_id: text for scene_id, text in texts.items() if not paths[scene_id].exists()}
    to_pay = sum(len(text) for text in missing.values())
    if to_pay > max_chars():
        raise BudgetExceeded(f"{to_pay} characters to send, ELEVEN_MAX_CHARS is {max_chars()}")
    if missing and chars_sent_today() + to_pay > max_chars_per_day():
        raise BudgetExceeded(f"{to_pay} characters to send and {chars_sent_today()} already sent today, "
                             f"ELEVEN_MAX_CHARS_PER_DAY is {max_chars_per_day()}")
    if missing:
        log.info("ElevenLabs (%s, %s): sending %d characters, %d scenes cached",
                 route.name, route.model, to_pay, len(texts) - len(missing))

    limit = asyncio.Semaphore(parallel)

    async def fetch(scene_id: str, text: str) -> None:
        async with limit:
            audio = await asyncio.to_thread(_post, route.request(text))
        if not audio:
            raise RuntimeError(f"ElevenLabs returned no audio for scene {scene_id!r}")
        paths[scene_id].parent.mkdir(parents=True, exist_ok=True)
        paths[scene_id].write_bytes(audio)
        _count_sent(len(text))

    await asyncio.gather(*(fetch(scene_id, text) for scene_id, text in missing.items()))
    return {scene_id: path.read_bytes() for scene_id, path in paths.items()}


def _post(request: urllib.request.Request) -> bytes:
    with urllib.request.urlopen(request, timeout=TIMEOUT_S) as response:
        return response.read()


# --- Speech to text (Scribe) --------------------------------------------------------------------
# The family's spoken question -> text. Same two routes as speech: personal key, else Sherpas proxy.
DIRECT_STT_URL = "https://api.elevenlabs.io/v1/speech-to-text"
DEFAULT_STT_MODEL = "scribe_v2"
PROXY_STT_MODEL_NAMES = {"scribe_v2": "scribe-v2", "scribe_v1": "scribe-v1"}
MAX_AUDIO_BYTES = 10 * 1024 * 1024  # a held-down mic button is seconds of audio, never this much


def transcribe(audio: bytes, filename: str, language: str = "en") -> str:
    """Text of one recorded question. Raises on any failure; `voice.transcribe_async` catches it."""
    if not audio:
        raise ValueError("empty audio")
    if len(audio) > MAX_AUDIO_BYTES:
        raise ValueError(f"audio is {len(audio)} bytes, the limit is {MAX_AUDIO_BYTES}")
    model = (os.getenv("ELEVEN_STT_MODEL") or DEFAULT_STT_MODEL).strip().replace("-", "_")
    if key := (os.getenv("ELEVENLABS_API_KEY") or "").strip():
        fields = {"model_id": model, "language_code": language, "tag_audio_events": "false"}
        request = _multipart(DIRECT_STT_URL, {"xi-api-key": key}, fields, audio, filename)
    else:
        team_key = (os.getenv("TEAM_KEY") or "").strip()
        proxy = (os.getenv("LLM_PROXY_URL") or "").strip().rstrip("/")
        if not (team_key and proxy):
            raise RuntimeError("no ElevenLabs key: set ELEVENLABS_API_KEY, or TEAM_KEY and LLM_PROXY_URL, in .env")
        base = proxy if proxy.endswith("/v1") else f"{proxy}/v1"
        fields = {"model": PROXY_STT_MODEL_NAMES.get(model, model), "language": language}
        request = _multipart(f"{base}/audio/transcriptions", {"Authorization": f"Bearer {team_key}"},
                             fields, audio, filename)
    return json.loads(_post(request))["text"].strip()


def _multipart(url: str, headers: dict, fields: dict, audio: bytes, filename: str) -> urllib.request.Request:
    """A multipart/form-data upload (what a browser form sends), built by hand: no extra library."""
    boundary = "----finagent" + hashlib.sha256(audio[:4096] + filename.encode()).hexdigest()[:24]
    parts = []
    for name, value in fields.items():
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode())
    safe_name = os.path.basename(filename).replace('"', "") or "question.webm"
    parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{safe_name}"\r\n'
                 f"Content-Type: application/octet-stream\r\n\r\n".encode() + audio + b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode())
    headers = {**headers, "Content-Type": f"multipart/form-data; boundary={boundary}"}
    return urllib.request.Request(url, data=b"".join(parts), headers=headers, method="POST")


# --- MP3 duration -------------------------------------------------------------------------------
# ElevenLabs answers with constant-bitrate MP3; the bitrate in the first frame header gives the length.
_BITRATES_KBPS = {  # MPEG-1 and MPEG-2/2.5, layer III
    1: [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320],
    2: [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160],
}


def mp3_duration_s(data: bytes) -> float:
    start = 0
    if data[:3] == b"ID3":  # skip an ID3v2 tag (its size is stored as four 7-bit bytes)
        size = (data[6] << 21) | (data[7] << 14) | (data[8] << 7) | data[9]
        start = 10 + size
    for i in range(start, len(data) - 4):
        if data[i] == 0xFF and data[i + 1] & 0xE0 == 0xE0:
            version_bits, layer_bits = (data[i + 1] >> 3) & 0b11, (data[i + 1] >> 1) & 0b11
            bitrate_index = data[i + 2] >> 4
            if layer_bits != 0b01 or version_bits == 0b01 or not 0 < bitrate_index < 15:
                continue  # not a layer III frame header
            table = 1 if version_bits == 0b11 else 2
            kbps = _BITRATES_KBPS[table][bitrate_index]
            return (len(data) - i) * 8 / (kbps * 1000)
    raise ValueError("no MP3 frame found")

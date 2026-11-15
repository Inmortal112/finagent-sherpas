"""ElevenLabs engine for `voice` (VOICE_ENGINE=eleven). Only the standard library: no new dependency.

Two ways to reach ElevenLabs, picked from .env:
- ELEVENLABS_API_KEY set -> straight to api.elevenlabs.io with that (personal, student) account.
- otherwise TEAM_KEY + LLM_PROXY_URL -> the Sherpas proxy (OpenAI-compatible /v1/audio/speech).
  It shares the team's $1.40 ElevenLabs allowance, so it is the fallback, not the default.

Spending guards (ElevenLabs bills per character):
- Cache: each audio is stored under a hash of (route, model, voice, text). The same text with the same
  voice is never paid for twice. Folder: VOICE_CACHE_DIR, default out/voice_cache (git-ignored).
- Budget: ELEVEN_MAX_CHARS (default 6000) caps the characters sent in one run, counting only the
  scenes not already cached. Over the cap, nothing is sent and `voice` falls back to edge-tts.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import urllib.request
from dataclasses import dataclass
from pathlib import Path

log = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
DIRECT_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}?output_format=mp3_44100_128"
DEFAULT_VOICE_ID = "XrExE9yKIg1WjnnlVkGX"  # Matilda: American, "knowledgeable, professional" (premade)
DEFAULT_MODEL = "eleven_flash_v2_5"         # cheapest and fastest
DEFAULT_MAX_CHARS = 6000                    # one family is about 1,000 characters
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


async def synthesize_all(texts: dict[str, str], parallel: int) -> dict[str, bytes]:
    """Audio for every {scene_id: spoken text}, from the cache or from ElevenLabs."""
    route = route_from_env()
    paths = {scene_id: cache_path(route, text) for scene_id, text in texts.items()}
    missing = {scene_id: text for scene_id, text in texts.items() if not paths[scene_id].exists()}
    to_pay = sum(len(text) for text in missing.values())
    if to_pay > max_chars():
        raise BudgetExceeded(f"{to_pay} characters to send, ELEVEN_MAX_CHARS is {max_chars()}")
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

    await asyncio.gather(*(fetch(scene_id, text) for scene_id, text in missing.items()))
    return {scene_id: path.read_bytes() for scene_id, path in paths.items()}


def _post(request: urllib.request.Request) -> bytes:
    with urllib.request.urlopen(request, timeout=TIMEOUT_S) as response:
        return response.read()


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

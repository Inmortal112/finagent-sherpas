"""Stage 2 (owner: B, David / daviid-sc). Fill audio_path and duration_s for every scene.

Engines, chosen with VOICE_ENGINE in .env:
- "edge" (default): free Microsoft Edge neural voices via edge-tts. Needs internet, no key.
- "mock": no audio, duration estimated from the text length.

If the real engine fails (no internet, service down), the stage falls back to "mock"
so the pipeline never breaks. `narration` is never modified: the engine receives
`speech_text.to_speech(narration)`, a copy rewritten the way a person says it ("$15,032/yr" ->
"$15,032 a year").

audio_path is relative to out_dir (e.g. "audio/intro.mp3"), so the stage page can
load it from next to index.html.
"""
from __future__ import annotations

import asyncio
import logging
import os
from pathlib import Path

from contracts.schemas import Presentation, Scene
from finagent.speech_text import to_speech

log = logging.getLogger(__name__)

AUDIO_DIR = "audio"
DEFAULT_VOICES = {"es": "es-ES-ElviraNeural", "en": "en-US-EmmaMultilingualNeural"}
# edge-tts always returns 24 kHz mono MP3 at a constant 48 kbit/s, so the file size gives the duration.
EDGE_MP3_BYTES_PER_SECOND = 48_000 / 8
MAX_PARALLEL_REQUESTS = 4
# The voice's natural pace. -5% was tried (2026-11-14) and David preferred the natural one.
DEFAULT_RATE = "+0%"


def speaking_rate() -> str:
    """edge-tts rate, e.g. "-5%" (slower) or "+10%" (faster). Override with VOICE_RATE in .env."""
    rate = (os.getenv("VOICE_RATE") or DEFAULT_RATE).strip()
    return rate if rate[:1] in "+-" else f"+{rate}"


def synthesize(presentation: Presentation, out_dir: Path) -> Presentation:
    _load_env()
    result = presentation.model_copy(deep=True)
    engine = os.getenv("VOICE_ENGINE", "edge").strip().lower()

    if engine == "edge":
        voice = os.getenv("VOICE_NAME") or DEFAULT_VOICES[result.language]
        try:
            asyncio.run(_edge_all(result.scenes, Path(out_dir), voice, result.language))
            return result
        except Exception as exc:  # any failure must not break the pipeline
            log.warning("edge-tts failed (%s: %s); using estimated durations", type(exc).__name__, exc)
    elif engine != "mock":
        log.warning("Unknown VOICE_ENGINE=%r; using estimated durations", engine)

    _mock_all(result.scenes)
    return result


def _load_env() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv()


def _mock_all(scenes: list[Scene]) -> None:
    for scene in scenes:
        scene.audio_path = None
        scene.duration_s = round(max(2.0, len(scene.narration) / 15), 1)


async def _edge_all(scenes: list[Scene], out_dir: Path, voice: str, language: str) -> None:
    import edge_tts  # imported here so a missing package falls back to mock

    audio_dir = out_dir / AUDIO_DIR
    audio_dir.mkdir(parents=True, exist_ok=True)
    limit = asyncio.Semaphore(MAX_PARALLEL_REQUESTS)

    async def one(scene: Scene) -> None:
        async with limit:
            audio = bytearray()
            spoken = to_speech(scene.narration, language)
            async for chunk in edge_tts.Communicate(spoken, voice, rate=speaking_rate()).stream():
                if chunk["type"] == "audio":
                    audio.extend(chunk["data"])
        if not audio:
            raise RuntimeError(f"no audio returned for scene {scene.id!r}")
        (audio_dir / f"{scene.id}.mp3").write_bytes(audio)
        scene.audio_path = f"{AUDIO_DIR}/{scene.id}.mp3"
        scene.duration_s = round(len(audio) / EDGE_MP3_BYTES_PER_SECOND, 1)

    await asyncio.gather(*(one(scene) for scene in scenes))

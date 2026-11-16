"""Stage 2 (owner: B, David / daviid-sc). Fill audio_path and duration_s for every scene.

Engines, chosen with VOICE_ENGINE in .env:
- "edge" (default): free Microsoft Edge neural voices via edge-tts. Needs internet, no key.
- "eleven": ElevenLabs, better voice, billed per character (see voice_eleven.py). For the demo.
- "mock": no audio, duration estimated from the text length.

If an engine fails (no key, no internet, over budget), the stage falls back: eleven -> edge -> mock,
so the pipeline never breaks. `narration` is never modified: the engine receives
`speech_text.to_speech(narration)`, a copy rewritten the way a person says it ("$15,032/yr" ->
"$15,032 a year").

For live answers (the /ask route of the backend) use `speak_async(text)` / `speak(text)`: one text in,
MP3 bytes out, with the same engines and fallbacks.

audio_path is relative to out_dir (e.g. "audio/intro.mp3"), so the stage page can
load it from next to index.html.
"""
from __future__ import annotations

import asyncio
import logging
import os
from dataclasses import dataclass
from pathlib import Path

from contracts.schemas import Presentation, Scene
from finagent import captions
from finagent.speech_text import spell_big_numbers, to_speech

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

    if engine == "eleven":
        try:
            asyncio.run(_eleven_all(result.scenes, Path(out_dir), result.language))
            return result
        except Exception as exc:  # any failure must not break the pipeline
            log.warning("ElevenLabs failed (%s: %s); falling back to edge-tts", type(exc).__name__, exc)
            engine = "edge"

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


@dataclass(frozen=True)
class SpokenAudio:
    """One spoken answer. `audio` is MP3 bytes, or None when no engine could speak (show the text)."""
    audio: bytes | None
    duration_s: float
    engine: str  # "eleven", "edge" or "mock"


async def speak_async(text: str, language: str = "en") -> SpokenAudio:
    """Speak one short text, e.g. a live answer from /ask. Never raises: the answer is shown anyway.

    Same engines and fallbacks as `synthesize` (eleven -> edge -> mock), same spoken rewrite
    (`to_speech`), and with ElevenLabs the same cache and character cap. Inside FastAPI:
        spoken = await voice.speak_async(answer_text)
        return Response(spoken.audio, media_type="audio/mpeg")
    """
    _load_env()
    spoken = to_speech(text, language)
    engine = os.getenv("VOICE_ENGINE", "edge").strip().lower()

    if engine == "eleven":
        from finagent import voice_eleven
        try:
            audio = (await voice_eleven.synthesize_all({"answer": spell_big_numbers(spoken)}, 1))["answer"]
            return SpokenAudio(audio, round(voice_eleven.mp3_duration_s(audio), 1), "eleven")
        except Exception as exc:
            log.warning("ElevenLabs failed (%s: %s); falling back to edge-tts", type(exc).__name__, exc)
            engine = "edge"

    if engine == "edge":
        try:
            audio = await _edge_bytes(spoken, os.getenv("VOICE_NAME") or DEFAULT_VOICES[language])
            if audio:
                return SpokenAudio(audio, round(len(audio) / EDGE_MP3_BYTES_PER_SECOND, 1), "edge")
            log.warning("edge-tts returned no audio; answer will be text only")
        except Exception as exc:
            log.warning("edge-tts failed (%s: %s); answer will be text only", type(exc).__name__, exc)

    return SpokenAudio(None, round(max(2.0, len(text) / 15), 1), "mock")


def speak(text: str, language: str = "en") -> SpokenAudio:
    """`speak_async` for code that is not async (scripts, tests). Inside FastAPI use `speak_async`."""
    return asyncio.run(speak_async(text, language))


@dataclass(frozen=True)
class Transcript:
    """What the family said. `text` is None when it could not be transcribed (ask them to type it)."""
    text: str | None
    engine: str  # "eleven", "model" (the proxy's listening model, when Scribe fails) or "none"


async def transcribe_async(audio: bytes, filename: str = "question.webm", language: str = "en") -> Transcript:
    """The family's spoken question (any browser recording: webm, ogg, mp3, wav, m4a...) -> text.

    Uses ElevenLabs Scribe with the same keys as the voice (ELEVENLABS_API_KEY, else TEAM_KEY via the
    proxy). If Scribe fails, a model that listens (voice_stt_model, through the proxy) tries. Never raises: on any failure, or if nothing was said, `text` is None. Inside FastAPI:
        heard = await voice.transcribe_async(await file.read(), file.filename)
    """
    _load_env()
    from finagent import voice_eleven, voice_stt_model
    try:
        text = await asyncio.to_thread(voice_eleven.transcribe, audio, filename, language)
        return Transcript(text or None, "eleven")
    except ValueError as exc:  # empty or huge recording: nothing to send anywhere
        log.warning("speech to text refused the recording (%s); ask the family to type", exc)
        return Transcript(None, "none")
    except Exception as exc:
        log.warning("Scribe failed (%s: %s); trying the proxy's listening model", type(exc).__name__, exc)
    if voice_stt_model.available():  # fallback: a model that listens, through the Sherpas proxy
        try:
            text = await asyncio.to_thread(voice_stt_model.transcribe, audio, filename, language)
            return Transcript(text or None, "model")
        except Exception as exc:
            log.warning("speech to text failed (%s: %s); ask the family to type", type(exc).__name__, exc)
    return Transcript(None, "none")


def transcribe(audio: bytes, filename: str = "question.webm", language: str = "en") -> Transcript:
    """`transcribe_async` for code that is not async (scripts, tests)."""
    return asyncio.run(transcribe_async(audio, filename, language))


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


async def _eleven_all(scenes: list[Scene], out_dir: Path, language: str) -> None:
    from finagent import voice_eleven

    # Long figures go in words: the fast model misreads some of them as digits (see speech_text.spell_big_numbers).
    texts = {scene.id: spell_big_numbers(to_speech(scene.narration, language)) for scene in scenes}
    audios = await voice_eleven.synthesize_all(texts, MAX_PARALLEL_REQUESTS)
    audio_dir = out_dir / AUDIO_DIR
    audio_dir.mkdir(parents=True, exist_ok=True)
    for scene in scenes:
        (audio_dir / f"{scene.id}.mp3").write_bytes(audios[scene.id])
        scene.audio_path = f"{AUDIO_DIR}/{scene.id}.mp3"
        scene.duration_s = round(voice_eleven.mp3_duration_s(audios[scene.id]), 1)
        timed = voice_eleven.word_times(texts[scene.id]) or captions.estimate(texts[scene.id], scene.duration_s)
        captions.save(audio_dir / f"{scene.id}.mp3", scene.narration, timed)


async def _edge_bytes(text: str, voice: str) -> bytes:
    return (await _edge_speech(text, voice))[0]


async def _edge_speech(text: str, voice: str) -> tuple[bytes, list[captions.Timed]]:
    """The MP3 and when each word is said (edge-tts reports times in units of 100 nanoseconds)."""
    import edge_tts  # imported here so a missing package falls back to mock

    audio, timed = bytearray(), []
    async for chunk in edge_tts.Communicate(text, voice, rate=speaking_rate(), boundary="WordBoundary").stream():
        if chunk["type"] == "audio":
            audio.extend(chunk["data"])
        elif chunk["type"] == "WordBoundary":
            start = chunk["offset"] / 1e7
            timed.append((chunk["text"], start, start + chunk["duration"] / 1e7))
    return bytes(audio), timed


async def _edge_all(scenes: list[Scene], out_dir: Path, voice: str, language: str) -> None:
    audio_dir = out_dir / AUDIO_DIR
    audio_dir.mkdir(parents=True, exist_ok=True)
    limit = asyncio.Semaphore(MAX_PARALLEL_REQUESTS)

    async def one(scene: Scene) -> None:
        spoken = to_speech(scene.narration, language)
        async with limit:
            audio, timed = await _edge_speech(spoken, voice)
        if not audio:
            raise RuntimeError(f"no audio returned for scene {scene.id!r}")
        (audio_dir / f"{scene.id}.mp3").write_bytes(audio)
        scene.audio_path = f"{AUDIO_DIR}/{scene.id}.mp3"
        scene.duration_s = round(len(audio) / EDGE_MP3_BYTES_PER_SECOND, 1)
        captions.save(audio_dir / f"{scene.id}.mp3", scene.narration, timed or captions.estimate(spoken, scene.duration_s))

    await asyncio.gather(*(one(scene) for scene in scenes))

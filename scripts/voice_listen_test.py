"""Listening test for speech_text: hear the hard formats before and after the rules.

    PYTHONPATH=src:. .venv/bin/python scripts/voice_listen_test.py   # Windows: src;.

Picks one real sentence per hard format from cases/*/*.json (public data) plus every term in
SPOKEN_TERMS, and writes to out/listen/ (ignored by git):
  before.mp3   the text as it is today
  after.mp3    the same text after to_speech
  samples.txt  what each numbered sample says, to follow while listening
Uses edge-tts (free). No ElevenLabs credit is spent.
"""
from __future__ import annotations

import asyncio
import json
import os
import re
from pathlib import Path

import edge_tts

from finagent.speech_text import SPOKEN_TERMS, to_speech
from finagent.voice import DEFAULT_VOICES

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out" / "listen"
FORMATS = {
    "markdown and dash": r"\*\*[^*]+\*\* —",
    "money per year": r"\$[\d,]+/(?:year|yr)",
    "negative money": r"-\$\d",
    "money with K/M": r"\$\d+(?:\.\d+)?[KM]\b",
    "money with cents": r"\$[\d,]+\.\d\d\b",
    "range": r"\d\s?–\s?\d",
    "about": r"~\d",
    "basis points": r"\d+bp\b",
    "401(k) and 529": r"401\(k\)|529",
    "tickers": r"\b(?:VTI|SCHD|UPRO|SPDR|JNK)\b",
}


def _texts() -> list[str]:
    texts: list[str] = []

    def walk(node):
        if isinstance(node, dict):
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)
        elif isinstance(node, str) and len(node) > 40:  # skip labels like "JNK" or "401(k) - Daniel"
            texts.append(node)

    for path in sorted(ROOT.glob("cases/*/*.json")):
        walk(json.loads(path.read_text(encoding="utf-8")))
    return texts


def _samples() -> list[tuple[str, str]]:
    texts = _texts()
    samples = []
    for name, pattern in FORMATS.items():
        for text in texts:
            match = re.search(pattern, text)
            if match:
                # Keep only the sentence around the match, so each sample is short.
                before = max(text.rfind(". ", 0, match.start()), text.rfind("\n", 0, match.start()))
                start = before + 1 if before != -1 else 0
                ends = [i for i in (text.find(". ", match.end()), text.find("\n", match.end())) if i != -1]
                end = min(ends) + 1 if ends else len(text)
                samples.append((name, text[start:end].strip()))
                break
    samples.append(("terms", ". ".join(SPOKEN_TERMS) + "."))
    return samples


async def _speak(lines: list[str], path: Path, voice: str) -> None:
    audio = bytearray()
    async for chunk in edge_tts.Communicate(" ".join(lines), voice).stream():
        if chunk["type"] == "audio":
            audio.extend(chunk["data"])
    path.write_bytes(audio)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    voice = os.getenv("VOICE_NAME") or DEFAULT_VOICES["en"]
    samples = _samples()
    before = [f"Sample {i}. {text}" for i, (_, text) in enumerate(samples, 1)]
    after = [f"Sample {i}. {to_speech(text)}" for i, (_, text) in enumerate(samples, 1)]
    report = []
    for i, (name, text) in enumerate(samples, 1):
        report += [f"{i}. {name}", f"   before: {text}", f"   after:  {to_speech(text)}", ""]
    (OUT / "samples.txt").write_text("\n".join(report), encoding="utf-8")
    asyncio.run(_speak(before, OUT / "before.mp3", voice))
    asyncio.run(_speak(after, OUT / "after.mp3", voice))
    print(f"OK -> {OUT} ({len(samples)} samples, voice {voice})")


if __name__ == "__main__":
    main()

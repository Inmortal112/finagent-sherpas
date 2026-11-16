"""Captions that follow the voice: when each word of a scene's narration is said.

The engines speak `to_speech(narration)` (a spoken copy: "$15,032/yr" is said "$15,032 a year") and tell us when
each spoken word starts and ends. The page shows the narration as written, so `align` maps the spoken words back
onto the written ones: while the voice says "a year", the written "$15,032/yr" is lit. Nothing is rewritten.

One small file per scene, next to its MP3: audio/<scene>.words.json
    {"words": [[char_start, char_end, start_s, end_s], ...]}   # character positions in `narration`
The page (web/captions.js) reads it and lights each word in time. No file, no captions: the page works the same.
"""
from __future__ import annotations

import json
import re
from difflib import SequenceMatcher
from pathlib import Path

Timed = tuple[str, float, float]  # (spoken word, start in seconds, end in seconds)


def _norm(word: str) -> str:
    return re.sub(r"[^a-z0-9]", "", word.lower())


def align(narration: str, timed: list[Timed]) -> list[list]:
    """[[char_start, char_end, start_s, end_s]] for every written word of `narration`, in order."""
    written = [(m.start(), m.end(), m.group()) for m in re.finditer(r"\S+", narration)]
    if not written or not timed:
        return []
    matcher = SequenceMatcher(a=[_norm(w[2]) for w in written], b=[_norm(t[0]) for t in timed], autojunk=False)
    times: list[tuple[float, float] | None] = [None] * len(written)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                times[i1 + k] = (timed[j1 + k][1], timed[j1 + k][2])
        elif i2 > i1:
            # Written words said differently ("$1M" -> "1 million dollars") or not said at all: they share the
            # time of the spoken words in the same place, or the pause between their neighbours.
            if j2 > j1:
                start, end = timed[j1][1], timed[j2 - 1][2]
            else:
                start = timed[j1 - 1][2] if j1 else 0.0
                end = timed[j1][1] if j1 < len(timed) else start
            total = sum(len(written[i][2]) for i in range(i1, i2))
            at = start
            for i in range(i1, i2):
                share = (end - start) * len(written[i][2]) / total
                times[i] = (at, at + share)
                at += share
    words, last = [], 0.0
    for (char_start, char_end, _), (start, end) in zip(written, times):
        start = max(start, last)          # never go back in time
        end = max(end, start)
        last = start
        words.append([char_start, char_end, round(start, 2), round(end, 2)])
    return words


def estimate(spoken: str, duration_s: float) -> list[Timed]:
    """When the engine gives no timings: share the audio's length between the words, by their length."""
    tokens = spoken.split()
    total = sum(len(token) + 1 for token in tokens)
    timed, at = [], 0.0
    for token in tokens:
        share = duration_s * (len(token) + 1) / total
        timed.append((token, at, at + share))
        at += share
    return timed


def from_characters(characters: list[str], starts: list[float], ends: list[float]) -> list[Timed]:
    """ElevenLabs tells when each character is said: group them into words."""
    timed, word, begin, finish = [], "", 0.0, 0.0
    for char, start, end in zip(characters, starts, ends):
        if char.isspace():
            if word:
                timed.append((word, begin, finish))
            word = ""
            continue
        if not word:
            begin = start
        word, finish = word + char, end
    if word:
        timed.append((word, begin, finish))
    return timed


def save(audio_file: Path, narration: str, timed: list[Timed]) -> None:
    """Write <audio_file>.words.json next to the MP3. Never raises: captions are an extra."""
    try:
        words = align(narration, timed)
        if words:
            audio_file.with_suffix(".words.json").write_text(json.dumps({"words": words}), encoding="utf-8")
    except Exception:  # noqa: BLE001 - a caption problem must not cost the audio
        pass

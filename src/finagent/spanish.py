"""Listen in Spanish: the same tour, spoken (and captioned) in Spanish for families who speak it at home.

The product stays in English; this adds a second audio track. Three steps, each safe on its own:

1. Translate once, keep in the repo.  `python -m finagent.spanish`  translates the narrations that are missing or
   whose English changed (model TRANSLATE_MODEL, default deepseek-flash, through the Sherpas proxy: a few cents)
   and saves them in narrations/es/<family>.json next to a fingerprint of the English they come from.
2. Check every figure.  A translation is only used if it holds exactly the same numbers as its English scene
   (`same_figures`), and only while that English has not changed. Otherwise the scene simply has no Spanish.
3. Speak it.  `add_audio` (called by finagent.run) writes audio/es/<scene>.mp3, its word timings for the captions,
   and es.json (the Spanish text of each scene) next to the page. No translations, nothing is written.

`to_speech_es` is the Spanish spoken copy: figures are written in US format ("$1,166,000", "24.9%"), which a Spanish
voice can misread (a comma is the decimal sign in Spanish), so amounts and decimals are spelled in words.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import re
import sys
from pathlib import Path

from contracts.schemas import Presentation

log = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
ES_DIR = ROOT / "narrations" / "es"
MODE_KEY = {"complete": "scenes", "simple": "simple"}   # same keys as narrations/<family>.json
DEFAULT_MODEL = "deepseek-flash"
EDGE_VOICE = "es-US-PalomaNeural"                        # Spanish as spoken in the US
AUDIO_DIR = "audio/es"

SYSTEM_PROMPT = """\
You translate the narration of a family's financial plan from English into Spanish, for Hispanic families in the
United States. It will be read aloud by a warm, calm voice.

Rules:
- Natural, simple Latin American Spanish. Address the family as "tú" (or "ustedes" for a couple). Short sentences.
- Keep EVERY number exactly as written, with the same digits and signs: "$1,166,000", "24.9%", "62", "2027", "$1M".
  Never write a number in words, never round, never convert, never add or drop one.
- Keep people's names as they are. "Sherpas" stays "Sherpas".
- The plan is a home. Always use: foundations = cimientos, walls = paredes, roof = techo, plumbing = tuberías,
  garden = jardín, score = puntuación, step = paso, emergency cash = fondo de emergencia.
- Translate only. Do not explain, add advice or change the meaning.

You receive {"scenes": {"<id>": "<English>"}}. Reply with JSON {"scenes": {"<id>": "<Spanish>"}}, same ids.
"""

_NUMBER = re.compile(r"\d+(?:[.,]\d+)*")


def figures(text: str) -> list[str]:
    """Every number in the text, as written, sorted: what a translation must keep."""
    return sorted(_NUMBER.findall(text))


def same_figures(english: str, spanish: str) -> bool:
    return figures(english) == figures(spanish)


def fingerprint(english: str) -> str:
    return hashlib.sha256(english.encode("utf-8")).hexdigest()[:16]


def saved(slug: str, mode: str, english: dict[str, str], directory: Path | None = None) -> dict[str, str]:
    """{scene_id: Spanish} for the scenes whose translation is still valid for this English text."""
    path = (directory or ES_DIR) / f"{slug}.json"
    if not path.exists():
        return {}
    stored = (json.loads(path.read_text(encoding="utf-8")).get(MODE_KEY[mode]) or {})
    valid = {}
    for scene_id, text in english.items():
        entry = stored.get(scene_id)
        if entry and entry.get("from") == fingerprint(text) and same_figures(text, entry.get("es", "")):
            valid[scene_id] = entry["es"]
    return valid


# --- the Spanish spoken copy --------------------------------------------------------------------------------------
_UNITS = ("cero uno dos tres cuatro cinco seis siete ocho nueve diez once doce trece catorce quince dieciséis "
          "diecisiete dieciocho diecinueve veinte veintiuno veintidós veintitrés veinticuatro veinticinco veintiséis "
          "veintisiete veintiocho veintinueve").split()
_TENS = "_ _ _ treinta cuarenta cincuenta sesenta setenta ochenta noventa".split()
_HUNDREDS = ("_ ciento doscientos trescientos cuatrocientos quinientos seiscientos setecientos ochocientos "
             "novecientos").split()


def _below_thousand(n: int) -> str:
    if n == 100:
        return "cien"
    words = []
    if n >= 100:
        words.append(_HUNDREDS[n // 100])
        n %= 100
    if n >= 30:
        words.append(_TENS[n // 10] + (f" y {_UNITS[n % 10]}" if n % 10 else ""))
    elif n or not words:
        words.append(_UNITS[n])
    return " ".join(words)


def _short(words: str) -> str:
    """"uno" loses its "o" before a noun: "veintiún mil", "un millón", "treinta y un dólares"."""
    if words.endswith("veintiuno"):
        return words[:-len("veintiuno")] + "veintiún"
    return words[:-1] if words.endswith("uno") else words


def numero_en_palabras(n: int, before_noun: bool = False) -> str:
    """1166000 -> "un millón ciento sesenta y seis mil"."""
    if n == 0:
        return "cero"
    millions, rest = divmod(n, 1_000_000)
    thousands, units = divmod(rest, 1000)
    words = []
    if millions:
        words.append("un millón" if millions == 1 else f"{_short(numero_en_palabras(millions))} millones")
    if thousands:
        words.append("mil" if thousands == 1 else f"{_short(_below_thousand(thousands))} mil")
    if units:
        words.append(_short(_below_thousand(units)) if before_noun else _below_thousand(units))
    return " ".join(words)


def _dollars(match: re.Match) -> str:
    minus, digits, cents, scale = match.groups()
    amount = int(digits.replace(",", ""))
    if scale:
        amount *= {"K": 1000, "M": 1_000_000}[scale.upper()]
    words = numero_en_palabras(amount, before_noun=True)
    # "un millón de dólares", "dos millones de dólares"; but "un millón cien mil dólares"
    noun = "dólar" if amount == 1 else "dólares"
    text = f"{words} de {noun}" if amount and amount % 1_000_000 == 0 else f"{words} {noun}"
    if cents and int(cents):
        text += f" con {numero_en_palabras(int(cents), before_noun=True)} centavos"
    return ("menos " if minus else "") + text


_ES_RULES = [
    (re.compile(r"(-)?\$(\d{1,3}(?:,\d{3})+|\d+)(?:\.(\d{2})(?!\d))?([KkMm])?\b(?!,\d)"), _dollars),
    (re.compile(r"(?<![\d,.])(\d{1,3}(?:,\d{3})+)(?!\d|,\d)"),
     lambda m: numero_en_palabras(int(m.group(1).replace(",", "")))),
    (re.compile(r"(?<![\d,.])-(\d)"), r"menos \1"),
    (re.compile(r"(\d+)\.(\d+)"), lambda m: f"{m.group(1)} punto {' '.join(_UNITS[int(d)] for d in m.group(2))}"),
    (re.compile(r"\s*%"), " por ciento"),
    (re.compile(r"(\d)\s*[–-]\s*(?=\d)"), r"\1 a "),
    (re.compile(r"\s*[—–]\s*"), ", "),
    (re.compile(r"\s+&\s+"), " y "),
]


def to_speech_es(text: str) -> str:
    """The Spanish text the way it is said: amounts and decimals in words, the value never changed."""
    from finagent.speech_text import _strip_markdown, _tidy
    text = _strip_markdown(text)
    for pattern, replacement in _ES_RULES:
        text = pattern.sub(replacement, text)
    return _tidy(text)


# --- audio --------------------------------------------------------------------------------------------------------
def add_audio(presentation: Presentation, slug: str, mode: str, out_dir: Path) -> int:
    """Write the Spanish track of this page (audio/es/*.mp3, word timings, es.json). Returns the scenes spoken.

    Never raises: Spanish is an extra, the English page must come out the same without it.
    """
    try:
        texts = saved(slug, mode, {scene.id: scene.narration for scene in presentation.scenes})
        engine = os.getenv("VOICE_ENGINE", "edge").strip().lower()
        if not texts or engine == "mock":
            return 0
        spoken = asyncio.run(_speak_all(texts, Path(out_dir), engine))
        (Path(out_dir) / "es.json").write_text(
            json.dumps({scene_id: texts[scene_id] for scene_id in spoken}, ensure_ascii=False), encoding="utf-8")
        return len(spoken)
    except Exception as exc:  # noqa: BLE001
        log.warning("Spanish audio skipped (%s: %s)", type(exc).__name__, exc)
        return 0


async def _speak_all(texts: dict[str, str], out_dir: Path, engine: str) -> list[str]:
    from finagent import captions, voice, voice_eleven

    said = {scene_id: to_speech_es(text) for scene_id, text in texts.items()}
    audio_dir = out_dir / AUDIO_DIR
    audio_dir.mkdir(parents=True, exist_ok=True)
    audios: dict[str, tuple[bytes, list]] = {}

    if engine == "eleven":
        try:
            raw = await voice_eleven.synthesize_all(said, voice.MAX_PARALLEL_REQUESTS)
            audios = {scene_id: (audio, voice_eleven.word_times(said[scene_id]) or []) for scene_id, audio in raw.items()}
        except Exception as exc:  # noqa: BLE001
            log.warning("ElevenLabs failed for Spanish (%s: %s); using edge-tts", type(exc).__name__, exc)
    if not audios:
        limit = asyncio.Semaphore(voice.MAX_PARALLEL_REQUESTS)

        async def one(scene_id: str) -> None:
            async with limit:
                audio, timed = await voice._edge_speech(said[scene_id], os.getenv("VOICE_NAME_ES") or EDGE_VOICE)
            if audio:
                audios[scene_id] = (audio, timed)

        await asyncio.gather(*(one(scene_id) for scene_id in said))

    for scene_id, (audio, timed) in audios.items():
        path = audio_dir / f"{scene_id}.mp3"
        path.write_bytes(audio)
        if not timed:
            try:
                seconds = voice_eleven.mp3_duration_s(audio)
            except ValueError:
                seconds = len(audio) / voice.EDGE_MP3_BYTES_PER_SECOND
            timed = captions.estimate(said[scene_id], seconds)
        captions.save(path, texts[scene_id], timed)
    return sorted(audios)


# --- translate (run by hand, once) --------------------------------------------------------------------------------
def translate_family(slug: str, client, model: str, directory: Path | None = None) -> tuple[int, list[str]]:
    """Translate what is missing or out of date for one family. Returns (scenes translated, scene ids refused)."""
    from finagent import brain

    directory = directory or ES_DIR
    diagnostic = json.loads((ROOT / "cases" / slug / "financial-health.json").read_text(encoding="utf-8"))
    path = directory / f"{slug}.json"
    stored = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    done, refused = 0, []
    for mode, key in MODE_KEY.items():
        english = {scene.id: scene.narration for scene in brain.build(diagnostic, mode=mode).scenes}
        kept = saved(slug, mode, english, directory)
        entries = {scene_id: {"from": fingerprint(english[scene_id]), "es": text} for scene_id, text in kept.items()}
        missing = {scene_id: text for scene_id, text in english.items() if scene_id not in kept}
        for _ in range(2):   # one retry for the scenes whose figures did not come back the same
            if not missing:
                break
            for scene_id, text in _ask(client, model, missing).items():
                if scene_id in missing and isinstance(text, str) and same_figures(missing[scene_id], text):
                    entries[scene_id] = {"from": fingerprint(missing[scene_id]), "es": " ".join(text.split())}
                    del missing[scene_id]
                    done += 1
        refused += [f"{mode}/{scene_id}" for scene_id in missing]
        stored[key] = {scene_id: entries[scene_id] for scene_id in english if scene_id in entries}
    stored["model"] = model
    directory.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(stored, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return done, refused


def _ask(client, model: str, scenes: dict[str, str]) -> dict[str, str]:
    reply = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": SYSTEM_PROMPT},
                  {"role": "user", "content": json.dumps({"scenes": scenes}, ensure_ascii=False)}],
        response_format={"type": "json_object"},
    )
    try:
        result = json.loads(reply.choices[0].message.content or "{}").get("scenes", {})
    except json.JSONDecodeError:
        return {}
    return result if isinstance(result, dict) else {}


def main(args: list[str]) -> int:
    from finagent import narrator

    client, model = narrator._client(), os.getenv("TRANSLATE_MODEL") or DEFAULT_MODEL
    slugs = args or sorted(case.parent.name for case in (ROOT / "cases").glob("*/financial-health.json"))
    for slug in slugs:
        done, refused = translate_family(slug, client, model)
        print(f"{slug}: {done} translated" + (f", refused (figures differ): {refused}" if refused else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

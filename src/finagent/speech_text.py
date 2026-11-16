"""Rewrite a narration so a text-to-speech voice reads it the way a person would say it.

    to_speech("**Pay** $15,032/yr — about 22/30") -> "Pay $15,032 a year, about 22 out of 30"

Used by `voice` right before sending text to the TTS engine. `Scene.narration` itself is never
changed (it is what `guard` checks and what the stage shows as subtitles); only the audio uses this.

Rules are plain regular expressions, applied in order, with no LLM: free, deterministic, and they
can only change how a number is *said*, never its value (no rounding). Every rule targets a format
found in the Sherpas case texts (`cases/*/*.json`). Acronyms and tickers live in `SPOKEN_TERMS`, an
editable table, checked by transcribing the audio back with Whisper (2026-11-14); to re-check after
a change, run `python scripts/voice_listen_test.py` and listen to out/listen/after.mp3.

Only English has rules (the product is in English); other languages only lose the markdown.
"""
from __future__ import annotations

import re

MONTHS = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]
MAGNITUDES = {"K": "thousand", "M": "million", "B": "billion"}

# How each acronym or ticker is said. Letters joined by hyphens are spelled out one by one.
# Unknown all-caps words are left to the voice. Doubtful entries are marked "check by ear".
SPOKEN_TERMS = {
    "401(k)s": "four-oh-one-K plans",  # "four-oh-one-Ks" is heard as "four-one cast"
    "401(k)": "four-oh-one-K",
    "403(b)": "four-oh-three-B",
    "IRAs": "I-R-As",
    "IRA": "I-R-A",
    "ETFs": "E-T-Fs",
    "ETF": "E-T-F",
    "HSA": "H-S-A",
    "DTI": "D-T-I",
    "APR": "A-P-R",
    "ESPP": "E-S-P-P",
    "NAV": "net asset value",  # "N-A-V" is heard as "and A-V"
    "LTCG": "long-term capital gains",
    "NIIT": "net investment income tax",
    "MAGI": "modified adjusted gross income",
    "TTM": "trailing twelve months",
    "USD": "US dollars",
    "REIT": "reet",
    "SPDR": "Spider",        # how the fund family says it
    "FTSE": "Footsie",
    # Tickers: spelled letter by letter, as advisors usually say them.
    "VTI": "V-T-I",
    "VOO": "V-double-O",     # "V-O-O" is heard as "Vio"
    "VWO": "V-W-O",
    "SCHD": "S-C-H-D",
    "SCHP": "S-C-H-P",
    "TBIL": "T-bill",
    "JNK": "J-N-K",          # still heard as "J and K" in every spelling tried
    "LQD": "L-Q-D",
    "UPRO": "U-P-R-O",       # "U-PRO" is heard as "you pro"
}

_TERMS = re.compile(
    "|".join(rf"(?<![\w-]){re.escape(term)}(?![\w-])"
             for term in sorted(SPOKEN_TERMS, key=len, reverse=True))
)


def to_speech(text: str, language: str = "en") -> str:
    text = _strip_markdown(text)
    if language == "en":
        for pattern, replacement in _RULES:
            text = pattern.sub(replacement, text)
        text = _TERMS.sub(lambda m: SPOKEN_TERMS[m.group(0)], text)
    return _tidy(text)


def _strip_markdown(text: str) -> str:
    lines = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        is_block = bool(re.match(r"(#+\s|[-*•]\s)", line))
        line = re.sub(r"^(#+|[-*•])\s+", "", line)
        line = re.sub(r"(\*\*|__|\*|`)", "", line)
        # Headings and list items become sentences, so the voice pauses between them.
        if is_block and line and line[-1] not in ".!?:;,":
            line += "."
        lines.append(line)
    return " ".join(lines)


def _iso_date(match: re.Match) -> str:
    year, month, day = match.group(1), int(match.group(2)), match.group(3)
    if not 1 <= month <= 12:
        return match.group(0)
    if day:
        return f"{MONTHS[month - 1]} {int(day)}, {year}"
    return f"{MONTHS[month - 1]} {year}"


def _money_magnitude(match: re.Match) -> str:
    return f"{match.group(1)} {MAGNITUDES[match.group(2).upper()]} dollars"


_NUM = r"\d[\d,]*(?:\.\d+)?"

_RULES: list[tuple[re.Pattern, object]] = [
    # 2025-04 -> April 2025; 2025-04-11 -> April 11, 2025 (before ranges, which also use "-").
    (re.compile(r"\b((?:19|20)\d\d)-(\d\d)(?:-(\d\d))?\b"), _iso_date),
    # $1M, $200K, $589B -> 1 million dollars ...
    (re.compile(r"\$(\d+(?:\.\d+)?)\s?([KMB])\b"), _money_magnitude),
    # 5–6, 2025-2038 -> 5 to 6 (the dash between two numbers is a range).
    (re.compile(rf"(?<![\w.,])({_NUM}%?)\s?[–-]\s?(\$?{_NUM})(?![\w-])"), r"\1 to \2"),
    # -$8,336, -2.1% -> minus ... (a dash glued to a number, not after a word).
    (re.compile(r"(?<![\w$%)])-(?=\$?\d)"), "minus "),
    # 22/30 -> 22 out of 30 (only bare numbers: not dates like 11/14/2026).
    (re.compile(r"(?<![\d/])(\d+)/(\d+)(?![\d/])"), r"\1 out of \2"),
    # $15,032/year, /yr, /mo -> a year, a month.
    (re.compile(r"\s?/\s?(?:year|yr)\b"), " a year"),
    (re.compile(r"\s?/\s?(?:month|mo)\b"), " a month"),
    # The 529 college savings plan is said "five-twenty-nine", not "five hundred twenty-nine".
    (re.compile(r"\b529(s?)\b(?=s?\s+(?:college|plan|account|savings|fund))|\b529s\b"),
     lambda m: "five-twenty-nine" + ("s" if m.group(0).endswith("s") else "")),
    (re.compile(r"(\d)\s?bps?\b"), r"\1 basis points"),
    (re.compile(r"~\s?(?=\$?\d)"), "about "),
    (re.compile(r"\s&\s"), " and "),
    (re.compile(r"\bvs\.?(?=\s)"), "versus"),
    # Long dashes become a pause: a full stop when a new sentence starts ("**Title** — You hold"),
    # a comma otherwise.
    (re.compile(r"\s*[—–]\s*(?=[A-Z])"), ". "),
    (re.compile(r"\s*[—–]\s*"), ", "),
]


def _tidy(text: str) -> str:
    text = re.sub(r"[®™©]", "", text)  # some voices read them as "registered", "trademark"
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    text = re.sub(r",\s*,", ",", text)
    text = re.sub(r"([.!?:;]),", r"\1", text)
    return text.strip()


# --- Big numbers in words (for ElevenLabs) ------------------------------------------------------------------------
# ElevenLabs' fast model sometimes misreads a long figure: on 2026-11-16, transcribing its audio back with Whisper,
# "$1,166,000" and "$19,900" came out as other amounts. Spelled in words they cannot be misread. Only numbers
# written with a thousands comma are spelled; the value never changes. The free Edge voices read digits correctly.
_ONES = ("zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen "
         "seventeen eighteen nineteen").split()
_TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()
_SCALES = ("", " thousand", " million", " billion", " trillion")
_COMMA_NUMBER = re.compile(r"(\$)?(?<![\d,.])(\d{1,3}(?:,\d{3})+)(?:\.(\d{2})(?!\d))?(?!\d|,\d)")


def _below_thousand(n: int) -> str:
    words = []
    if n >= 100:
        words.append(f"{_ONES[n // 100]} hundred")
        n %= 100
    if n >= 20:
        words.append(_TENS[n // 10] + (f"-{_ONES[n % 10]}" if n % 10 else ""))
    elif n or not words:
        words.append(_ONES[n])
    return " ".join(words)


def number_in_words(n: int) -> str:
    """1166000 -> "one million one hundred sixty-six thousand" (American English, no "and")."""
    if n == 0:
        return "zero"
    groups, scale = [], 0
    while n:
        n, group = divmod(n, 1000)
        if group:
            groups.append(_below_thousand(group) + _SCALES[scale])
        scale += 1
    return " ".join(reversed(groups))


def spell_big_numbers(text: str) -> str:
    """"$1,166,000" -> "one million one hundred sixty-six thousand dollars"; "2,500" -> "two thousand five hundred"."""
    def spell(match: re.Match) -> str:
        dollars, digits, cents = match.groups()
        if len(digits.replace(",", "")) > 15:
            return match.group(0)
        words = number_in_words(int(digits.replace(",", "")))
        if dollars:
            words += " dollars"
            if cents and int(cents):
                words += f" and {number_in_words(int(cents))} cents"
        elif cents:
            words += " point " + " ".join(_ONES[int(d)] for d in cents)
        return words
    return _COMMA_NUMBER.sub(spell, text)

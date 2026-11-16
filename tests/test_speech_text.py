"""speech_text: how the voice says the narration. Inputs are formats found in cases/*/*.json."""
import json
import re
from pathlib import Path

import pytest

from finagent.speech_text import SPOKEN_TERMS, to_speech

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("text, spoken", [
    ("**We should look into**: the emergency reserve.", "We should look into: the emergency reserve."),
    ("## Summary\n- First item\n- Second item.", "Summary. First item. Second item."),
    ("Redirect $15,032/year into savings", "Redirect $15,032 a year into savings"),
    ("$6,418/yr and $500/mo", "$6,418 a year and $500 a month"),
    ("Cash flow is -$8,336.", "Cash flow is minus $8,336."),
    ("A drop of -2.1% this year", "A drop of minus 2.1% this year"),
    ("Savings: 22/30 points", "Savings: 22 out of 30 points"),
    ("Paid off by 2034-01.", "Paid off by January 2034."),
    ("Bought on 2025-04-11.", "Bought on April 11, 2025."),
    ("From 2025–2038, about 5–6 months", "From 2025 to 2038, about 5 to 6 months"),
    ("$1M goal and $200K saved", "1 million dollars goal and 200 thousand dollars saved"),
    ("roughly ~3% or 25bp", "roughly about 3% or 25 basis points"),
    ("stocks & bonds vs. cash", "stocks and bonds versus cash"),
    ("Save first — then invest", "Save first, then invest"),
    ("- **Rebuild a cushion** — Your $30,000 covers it", "Rebuild a cushion. Your $30,000 covers it."),
    ("the two 401(k)s and an IRA", "the two four-oh-one-K plans and an I-R-A"),
    ("the 529 college plan", "the five-twenty-nine college plan"),
    ("Sell VTI and SCHD ETFs", "Sell V-T-I and S-C-H-D E-T-Fs"),
    ("State Street® SPDR® Portfolio", "State Street Spider Portfolio"),
])
def test_rules(text, spoken):
    assert to_speech(text) == spoken


@pytest.mark.parametrize("text", [
    "A 30-year mortgage at age 58.",          # hyphenated words are not ranges or minus signs
    "A 20% drop on 11/14/2026.",              # full dates are left to the voice
    "Your score is 82 out of 100.",           # already spoken text stays the same
    "Retire at 58 with $1,177,586.50 saved.", # long amounts are kept whole, never rounded
])
def test_leaves_alone(text):
    assert to_speech(text) == text


def test_other_languages_only_lose_markdown():
    assert to_speech("**Ahorro**: 22/30 — bien", language="es") == "Ahorro: 22/30 — bien"


def _case_texts() -> list[str]:
    texts = []

    def walk(node):
        if isinstance(node, dict):
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)
        elif isinstance(node, str) and len(node) > 40:
            texts.append(node)

    for path in sorted(ROOT.glob("cases/*/*.json")):
        walk(json.loads(path.read_text(encoding="utf-8")))
    return texts


def _digits(text: str) -> list[str]:
    # Formats whose digits are said as words on purpose: ISO dates, 401(k)/403(b), 529.
    text = re.sub(r"\b(?:19|20)\d\d-\d\d(?:-\d\d)?\b", "", text)
    text = re.sub(r"\b(?:January|February|March|April|May|June|July|August|September|October|"
                  r"November|December)( \d+,)? \d{4}\b", "", text)
    text = re.sub(r"\b(?:401\(k\)|403\(b\)|529)s?", "", text)
    return re.findall(r"\d+", text)


def test_never_changes_a_number_in_the_real_cases():
    texts = _case_texts()
    assert texts, "no case texts found"
    for text in texts:
        assert _digits(to_speech(text)) == _digits(text), text


def test_no_markdown_left_in_the_real_cases():
    for text in _case_texts():
        assert not re.search(r"\*\*|^#|`", to_speech(text)), text


def test_every_spoken_term_is_used_by_a_rule():
    for term in SPOKEN_TERMS:
        assert to_speech(f"the {term} here") != f"the {term} here", term


# --- big numbers in words (ElevenLabs) ----------------------------------------------------------------------------
from finagent.speech_text import number_in_words, spell_big_numbers  # noqa: E402


def test_numbers_in_words():
    assert number_in_words(0) == "zero" and number_in_words(13) == "thirteen" and number_in_words(101) == "one hundred one"
    assert number_in_words(19900) == "nineteen thousand nine hundred"
    assert number_in_words(1166000) == "one million one hundred sixty-six thousand"
    assert number_in_words(2371901) == "two million three hundred seventy-one thousand nine hundred one"


def test_big_figures_are_spelled_and_small_ones_left_alone():
    said = spell_big_numbers("Your cover is $200,000, which is $1,000,000 short. In 2027, at 24.9%, your score is 52.")
    assert said == ("Your cover is two hundred thousand dollars, which is one million dollars short. "
                    "In 2027, at 24.9%, your score is 52.")
    assert spell_big_numbers("minus $8,336 and 1,200 units") == "minus eight thousand three hundred thirty-six dollars and one thousand two hundred units"
    assert spell_big_numbers("$1,234.50") == "one thousand two hundred thirty-four dollars and fifty cents"


def test_spelling_keeps_every_value():
    """Words back to digits give the same numbers: nothing is rounded or lost."""
    units = {w: i for i, w in enumerate("zero one two three four five six seven eight nine ten eleven twelve thirteen "
                                        "fourteen fifteen sixteen seventeen eighteen nineteen".split())}
    tens = {w: 10 * i for i, w in enumerate("_ _ twenty thirty forty fifty sixty seventy eighty ninety".split())}

    def back(words: str) -> int:
        total = group = 0
        for word in words.replace("-", " ").split():
            if word in units: group += units[word]
            elif word in tens: group += tens[word]
            elif word == "hundred": group *= 100
            else:
                total += group * {"thousand": 10**3, "million": 10**6, "billion": 10**9}[word]; group = 0
        return total + group

    for n in (1000, 1001, 16530, 19900, 110015, 999999, 1000000, 1166000, 2371901, 20000000, 1234567890):
        assert back(number_in_words(n)) == n

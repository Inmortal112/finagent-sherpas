"""Cross-cutting check (owner: A). Every number the presenter says must be a Fact.

Runs between brain and voice: a hallucinated figure never reaches the audio.
"""
import re

from contracts.schemas import Presentation

# English number format (the product is in English): the point is the decimal separator and
# commas only group thousands, so "6,800" is 6800 and "2.5" is two and a half.
NUMBER = re.compile(r"\d+(?:,\d{3})*(?:\.\d+)?")
# Numbers written in words that NUMBER cannot see. Small ones ("one step", "the two of you") are
# everyday English and stay allowed; "million" too, because the plan itself writes "$1M".
SPELLED = re.compile(
    r"\b(?:twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand)\b", re.IGNORECASE
)


# "It lifts your roof score to 31 out of 100": 31 is the family's overall score, not the roof's. Only the
# overall score is out of 100 (a part scores out of 10 to 30), so a part "scoring" out of 100 is always wrong.
PART_OUT_OF_100 = re.compile(
    r"\b(?:roof|walls?|plumbing|foundations?|garden)(?:'s)? scores?\b[^.!?]*?\bout of 100\b", re.IGNORECASE
)


def part_scored_out_of_100(text: str) -> list[str]:
    """Phrases that give a part of the home a score out of 100: a real number used with the wrong meaning."""
    return [match.group(0) for match in PART_OUT_OF_100.finditer(text)]


# "That clears your costliest debt", said of a step that pays only part of it. Not a figure, so the number
# check cannot see it. "Clear the gate" is Sherpas' own wording for the score cap, and "pay $6,800 off the
# card" (an amount in between) is a part payment: neither is a claim that the debt is gone.
CLEARED = re.compile(
    r"\bclear(?:s|ed|ing)?\b(?! (?:the|a|that) gate)"
    r"|\bpa(?:y|ys|ying|id) (?:(?:it|that|this|them|(?:the|your|that|this) \w+) )?off\b(?! \$)"
    r"|\bwip(?:e|es|ed|ing) out\b|\beliminat(?:e|es|ed|ing)\b|\bget(?:s|ting)? rid of\b|\bdebt[- ]free\b",
    re.IGNORECASE,
)
NOT_CLEARED = re.compile(r"\b(?:not|never|without|rest|remaining|left)\b|n't\b|n’t\b", re.IGNORECASE)


def claims_debt_cleared(text: str) -> list[str]:
    """Phrases saying a debt is gone. Only wrong where a step pays part of it: the caller decides where to look.

    A sentence that also says "not", "the rest" or "what is left" is describing the part payment, so it passes.
    """
    found = []
    for sentence in re.split(r"(?<=[.!?])\s+", text):
        match = CLEARED.search(sentence)
        if match and not NOT_CLEARED.search(sentence):
            found.append(match.group(0))
    return found


def spelled_numbers(text: str) -> list[str]:
    """Numbers written in words ('seventy-three'), which `unsupported_numbers` cannot check."""
    return SPELLED.findall(text)


def _normalise(text: str) -> float:
    return float(text.replace(",", ""))


def unsupported_numbers(presentation: Presentation) -> list[tuple[str, str]]:
    """Return (scene_id, number) for each spoken number not backed by the scene's facts."""
    facts = {f.id: f for f in presentation.facts}
    problems = []
    for scene in presentation.scenes:
        allowed = set()
        for fact_id in scene.fact_ids:
            fact = facts[fact_id]  # KeyError = scene quotes a fact that does not exist
            allowed.update(_normalise(n) for n in NUMBER.findall(f"{fact.value} {fact.unit}"))
        for spoken in NUMBER.findall(scene.narration):
            if _normalise(spoken) not in allowed:
                problems.append((scene.id, spoken))
    return problems

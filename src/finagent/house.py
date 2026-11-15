"""The house behind Under One Roof: which part each Sherpas pillar is, and what state it is in.

Pure functions over one family's `financial-health.json`. No LLM and no invented figures:
every value is read from the diagnostic, except the three states, which are our own reading
of a pillar's 0-100 score (Sherpas publishes no bands per pillar).
"""
import re

# Pillar keyword -> house part (table agreed in idea-david.md, English names from nota-idea.md).
PILLAR_PARTS = {
    "liquidity": "foundations",
    "insurance": "roof",
    "debt": "walls",
    "savings": "plumbing",
    "investments": "garden",
}
PARTS = tuple(PILLAR_PARTS.values())

# House part -> sections of the diagnostic's `narrative` where Sherpas explains that area in plain words.
PART_NARRATIVE = {
    "foundations": ("protection_emergency_fund_short_observations",),
    "roof": ("protection_life_insurance_short_observations", "protection_umbrella_short_observations"),
    "walls": ("debt_short_observations",),
    "plumbing": ("savings_short_observations",),
    "garden": ("assets_short_observations",),
}

# Our thresholds on `score.pillars[].score` (0-100). Change them here, nowhere else.
SOLID_FROM = 70
CRACKED_FROM = 40

# Sherpas' step title (lower case) -> the same step in words a family uses. No figures here.
PLAIN_MOVE_TITLES = {
    "raise mortality coverage": "Add more life insurance",
    "add life cover": "Add more life insurance",
    "add umbrella cover": "Add umbrella insurance",
    "close a coverage gap": "Close a gap in your insurance",
    "pay down revolving card": "Pay down the credit card",
    "raise annual savings": "Save what is left over each year",
    "lower the withdrawal rate": "Plan to spend less from savings in retirement",
    "raise growth allocation toward glide": "Put more of your investments in stocks",
    "reduce growth allocation toward glide": "Put a little less of your investments in stocks",
    "reduce single-name concentration": "Spread out money held in one investment",
}

# Sherpas' step title (lower case) -> how to get started tomorrow, in plain words. Practical actions only:
# no figures, no product or company names, nothing the family must decide alone. Always ends with the advisor.
FIRST_MOVES = {
    "raise mortality coverage": (
        "Find the life insurance papers you already have, from work or your own.",
        "Ask your insurer or your advisor for a quote for more cover.",
    ),
    "add life cover": (
        "Find the life insurance papers you already have, from work or your own.",
        "Ask your insurer or your advisor for a quote for more cover.",
    ),
    "add umbrella cover": (
        "Call the company that insures your home or your car and ask about umbrella cover.",
        "Have your current policies at hand when you call.",
    ),
    "close a coverage gap": (
        "Find the insurance papers for your home and check what they cover.",
        "Call your insurer, or your advisor, and ask what is missing.",
    ),
    "pay down revolving card": (
        "Log in to your card account and look at the balance.",
        "Choose the day this week you will make the payment from the cash you already hold.",
    ),
    "raise annual savings": (
        "Look at where your money goes in a normal month.",
        "Ask your advisor which account the money left over each year should go to.",
    ),
    "lower the withdrawal rate": (
        "This one is about later, so there is nothing to pay or sign tomorrow.",
        "Write down what you hope to spend each year once you retire.",
    ),
    "raise growth allocation toward glide": (
        "Log in to your retirement and investment accounts and look at how they are invested.",
        "Ask your advisor how to move toward the mix your plan suggests.",
    ),
    "reduce growth allocation toward glide": (
        "Log in to your investment accounts and look at how they are invested.",
        "Ask your advisor how to move toward the mix your plan suggests.",
    ),
    "reduce single-name concentration": (
        "Log in to your investment accounts and find the fund that holds the largest share.",
        "Ask your advisor how to spread it out without a surprise tax bill.",
    ),
}
FIRST_MOVE_FALLBACK = ("Send this step to your advisor and ask what the first move is.",)

# Word in a move's title -> house part it repairs. First match wins, so the order matters.
MOVE_PARTS = (
    (("cover", "insurance", "umbrella"), "roof"),
    (("card", "debt", "loan", "mortgage"), "walls"),
    (("allocation", "concentration", "glide"), "garden"),
    (("savings", "withdrawal", "cash flow"), "plumbing"),
    (("emergency", "reserve", "cash"), "foundations"),
)

RUN_OUT_AGE = re.compile(r"run out at age (\d+)")


def part_for_pillar(pillar_name: str) -> str:
    name = pillar_name.lower()
    for keyword, part in PILLAR_PARTS.items():
        if keyword in name:
            return part
    raise ValueError(f"No house part for pillar {pillar_name!r}")


def state(pillar_score: float) -> str:
    """'solid', 'cracked' or 'broken' for a pillar's 0-100 score."""
    if pillar_score >= SOLID_FROM:
        return "solid"
    return "cracked" if pillar_score >= CRACKED_FROM else "broken"


def plain_title(title: str) -> str:
    """A step's name in everyday words, for the family. Sherpas' own title stays for the advisor.

    Words only, never a figure. A title not in the table is shown as Sherpas wrote it.
    """
    return PLAIN_MOVE_TITLES.get(title.strip().lower(), title)


def first_moves(title: str) -> list[str]:
    """How to start a step tomorrow: one or two practical actions, never a figure."""
    return list(FIRST_MOVES.get(title.strip().lower(), FIRST_MOVE_FALLBACK))


def part_for_move(title: str) -> str | None:
    """House part a plan move repairs, or None when the title matches no known word."""
    text = title.lower()
    for keywords, part in MOVE_PARTS:
        if any(keyword in text for keyword in keywords):
            return part
    return None


def best_combination(score: dict) -> dict | None:
    """The `combined_moves` entry with the highest score, or None when the plan has none.

    On a tie the shortest combination wins: a move that adds no points is not part of the promise.
    """
    combined = score.get("combined_moves") or []
    return max(combined, key=lambda c: (c["score_after"], -len(c["moves"]))) if combined else None


def timeline(diagnostic: dict) -> dict:
    """The current plan through the years: one point per year plus the events worth stopping at.

    Only what the plan holds: there is no "if you make the repair" projection.
    Investable assets are floored at 0 (the diagnostic forbids quoting a negative balance).
    """
    yearly = diagnostic["projections"]["yearly"]
    points = [
        {
            "year": row["year"],
            "age_client": row["age_client"],
            "age_co_client": row["age_co_client"],
            "net_worth": row["net_worth"],
            "total_debts": row["total_debts"],
            "investable_assets": max(row["investable_assets"], 0),
        }
        for row in yearly
    ]

    events = []
    for person in diagnostic["case"]["household"]:
        if person.get("retirement_age") is None:
            continue
        age_key = "age_client" if person["role"] == "client" else "age_co_client"
        events.append({
            "kind": "retirement",
            "person": person["first_name"],
            "age": person["retirement_age"],
            "year": _year_at(yearly, age_key, person["retirement_age"]),
        })

    debt_years = [row["year"] for row in yearly if row["total_debts"] > 0]
    if debt_years and debt_years[-1] < yearly[-1]["year"]:
        events.append({"kind": "debt_free", "year": debt_years[-1] + 1})

    retirement = diagnostic["key_metrics"]["facts"].get("retirement", {})
    run_out = retirement.get("savingsRunOut")
    match = RUN_OUT_AGE.search(run_out["label"]) if run_out else None
    if match:
        age = int(match.group(1))
        events.append({"kind": "savings_run_out", "age": age, "year": _year_at(yearly, "age_client", age),
                       "unpaid_spending": run_out["value"]})
    elif "savingsLeftAtPlanEnd" in retirement:
        events.append({"kind": "savings_last", "year": yearly[-1]["year"],
                       "savings_left": retirement["savingsLeftAtPlanEnd"]["value"]})

    return {"points": points, "events": sorted(events, key=lambda e: e["year"] or 0)}


def _year_at(yearly: list[dict], age_key: str, age: int) -> int | None:
    return next((row["year"] for row in yearly if row[age_key] == age), None)


def adults(diagnostic: dict) -> list[dict]:
    """The people the plan belongs to (client and co-client), in that order."""
    return [p for p in diagnostic["case"]["household"] if p["role"] in ("client", "co-client")]


def person_view(diagnostic: dict, first_name: str) -> dict:
    """What the plan holds in one adult's own name: income, accounts, debts and life cover.

    Shared items (two owners) are left out: they belong to the home, not to one person.
    """
    profile = diagnostic["profile"]
    role = next(p["role"] for p in adults(diagnostic) if p["first_name"] == first_name)
    side = "client" if role == "client" else "coClient"

    def own(items: list[dict]) -> list[dict]:
        return [item for item in items if item.get("owner") == [first_name]]

    life = (diagnostic["key_metrics"].get("protection") or {}).get("lifeInsurance") or {}
    basics = life.get("lifeInsuranceCoverageBasics") or {}
    gaps = life.get("lifeInsuranceCoverageGapsAndExcess") or {}
    recommended = life.get("lifeInsuranceCoverageRecommendations") or {}
    return {
        "first_name": first_name,
        "role": role,
        "salary": sum(i["yearly"] for i in own(profile["incomes"]) if i["type"] == "SALARY_AND_WAGES"),
        "accounts": [{"name": a["name"], "balance": a["balance"]} for a in own(profile["accounts"])],
        "debts": [{"name": d["name"], "balance": d["balance"], "rate_percent": round(d["interest_rate"] * 100, 2)}
                  for d in own(profile["liabilities"]) if d["balance"] > 0],
        "life_cover": basics.get(f"lifeInsuranceAmount{side[0].upper()}{side[1:]}"),
        "life_shortfall": gaps.get(f"{side}Shortfall"),
        "life_recommended_min": recommended.get(f"{side}MinRecommendedCoverage"),
        "life_recommended_max": recommended.get(f"{side}MaxRecommendedCoverage"),
    }


def home(diagnostic: dict) -> dict:
    """Where the family lives, for the drawing: a home they own, or one they rent, and their cars."""
    profile = diagnostic["profile"]
    owned = next((a for a in profile["other_assets"] if a["type"] == "PRIMARY_HOME"), None)
    rents = any(e.get("type") == "RENT" for e in profile["expenses"])
    return {
        "kind": "owned" if owned else "rented" if rents else "unknown",
        "value": owned["value"] if owned else None,
        "cars": [a["name"] for a in profile["other_assets"] if a["type"] == "CAR"],
    }


def plan_dates(diagnostic: dict) -> list[dict]:
    """The dated goals of the plan (first payment of a repeating one), oldest first. No engine-only markers."""
    dates = []
    for goal in diagnostic["goals"]["chartGoals"]:
        if not goal.get("name"):
            continue  # markers such as BANKRUPTCY_ZEROCASH: never shown to a family
        dates.append({"kind": goal["goalType"].lower(), "name": goal["name"], "date": goal["date"][:10],
                      "repeats": bool(goal.get("termDate")) and goal["termDate"][:10] != goal["date"][:10]
                      and goal["goalType"] == "VACATION"})
    return sorted(dates, key=lambda d: d["date"])

"""Write pitch/data.js: the real figures the pitch page shows, read from the cases and narrations.

The page (pitch/index.html) walks the jury through one session in two minutes. Nothing on it is typed by hand:
scores, pillars, steps and narration come from `cases/` and `narrations/`, and the token count of a live question
is measured by building the real prompt `ask.answer` would send (with a fake model, so it costs nothing).

    PYTHONPATH=src:. .venv/bin/python scripts/build_pitch.py
"""
import json
from pathlib import Path

from finagent import ask, brain, house, spanish

ROOT = Path(__file__).resolve().parent.parent
PRICE_IN, PRICE_OUT = 0.30, 1.20          # deepseek-flash, $ per 1M tokens (02-DOCS/brief.md, "Models and usage prices")
OUT_TOKENS = 140                          # a short JSON answer: {"scene": ..., "answer": two or three sentences}

# One question per family and the scene of the plan that answers it.
QUESTIONS = {
    "michael-carter": ("Can I still buy the home in 2027?", "pillar_liquidity_and_emergency_fund"),
    "samantha-lewis": ("Will my savings last once I retire?", "timeline"),
    "daniel-emily-johnson": ("What happens to the kids if something happens to us?", "pillar_insurance_and_protection"),
    "timothy-melanie-weah": ("Where is every dollar going?", "pillar_debt"),
}
QUESTIONS_ES = {
    "michael-carter": "¿Todavía puedo comprar la casa en 2027?",
    "samantha-lewis": "¿Me alcanzarán los ahorros cuando me jubile?",
    "daniel-emily-johnson": "¿Qué pasa con los niños si nos pasa algo?",
    "timothy-melanie-weah": "¿A dónde va cada dólar?",
}
# The steps' plain titles (house.plain_title) in Spanish, for the pitch only. No figures in them.
STEPS_ES = {
    "Plan to spend less from savings in retirement": "Gastar menos de tus ahorros al jubilarte",
    "Close a gap in your insurance": "Cerrar un hueco en tu seguro",
    "Add more life insurance": "Ampliar el seguro de vida",
    "Add umbrella insurance": "Añadir un seguro paraguas",
    "Pay down the credit card": "Pagar la tarjeta de crédito",
}
BANDS_ES = {"critical": "crítica", "vulnerable": "vulnerable", "stable": "estable", "strong": "sólida"}
PILLARS_ES = {"Savings and cash flow": "ahorro y flujo de caja", "Debt": "deuda", "Investments": "inversiones",
              "Liquidity and emergency fund": "liquidez y fondo de emergencia",
              "Insurance and protection": "seguros y protección"}
TOUR = ("intro", "pillar_savings_and_cash_flow", "pillar_liquidity_and_emergency_fund",
        "pillar_insurance_and_protection", "pillar_investments", "pillar_debt")


def prompt_tokens(presentation, diagnostic, question: str) -> int:
    seen = {}

    def fake(system: str, user: str) -> str:
        seen["chars"] = len(system) + len(user)
        return json.dumps({"scene": "intro", "answer": ""})

    ask.answer(presentation, diagnostic, question, complete=fake)
    return round(seen["chars"] / 4)       # ~4 characters per token for English and JSON


def family(slug: str) -> dict:
    diagnostic = json.loads((ROOT / "cases" / slug / "financial-health.json").read_text())
    narration = json.loads((ROOT / "narrations" / f"{slug}.json").read_text())
    score = diagnostic["score"]
    question, scene = QUESTIONS[slug]
    pillars = [{"name": p["pillar"], "score": p["score"], "part": house.part_for_pillar(p["pillar"]),
                "state": house.state(p["score"])} for p in score["pillars"]]
    moves = [{"title": house.plain_title(m["title"]), "part": house.part_for_move(m["title"]),
              "before": m["score_before"], "after": m["score_after"], "effort": m["effort"]}
             for m in score["top_moves"]]
    combo = house.best_combination(score)
    best = max(moves, key=lambda m: m["after"])
    if combo and combo["score_after"] > best["after"]:
        chosen = [m for m, raw in zip(moves, score["top_moves"]) if raw["title"] in combo["moves"]]
        final = combo["score_after"]
    else:
        chosen, final = [best], best["after"]
    presentation = brain.build(diagnostic)
    tokens_in = prompt_tokens(presentation, diagnostic, question)
    styles = {"story": "scenes", "numbers": "numbers", "simple": "simple"}
    # Spanish: only translations still valid for today's English and with the same figures (spanish.saved).
    # There is no "numbers first" in Spanish, so it uses the story.
    es = {mode: spanish.saved(slug, mode, narration[key]) for mode, key in (("complete", "scenes"), ("simple", "simple"))}
    es_styles = {"story": es["complete"], "numbers": es["complete"], "simple": es["simple"]}
    missing = [s for s in TOUR[:3] + (scene,) for d in es_styles.values() if s not in d]
    if missing:
        raise SystemExit(f"{slug}: no valid Spanish for {sorted(set(missing))}; run python -m finagent.spanish")
    tokens_in_es = prompt_tokens(presentation, diagnostic, QUESTIONS_ES[slug])
    return {
        "slug": slug,
        "names": [p["first_name"] for p in house.adults(diagnostic)],
        "household": [p["first_name"] for p in diagnostic["case"]["household"]],
        "score": score["published_score"], "band": score["band"],
        "pillars": pillars, "moves": moves,
        "chosen": [m["title"] for m in chosen], "chosen_parts": [m["part"] for m in chosen], "final": final,
        "question": question, "answer_scene": scene,
        "tour": {style: [narration[key][s] for s in TOUR if s in narration[key]][:3] for style, key in styles.items()},
        "answer": {style: narration[key][scene] for style, key in styles.items()},
        "tokens_in": tokens_in, "tokens_out": OUT_TOKENS,
        "cost": round(tokens_in * PRICE_IN / 1e6 + OUT_TOKENS * PRICE_OUT / 1e6, 6),
        "es": {
            "band": BANDS_ES[score["band"]],
            "pillars": [PILLARS_ES[p["name"]] for p in pillars],
            "chosen": [STEPS_ES.get(t, t) for t in (m["title"] for m in chosen)],
            "question": QUESTIONS_ES[slug],
            "tour": {style: [d[s] for s in TOUR if s in d][:3] for style, d in es_styles.items()},
            "answer": {style: d[scene] for style, d in es_styles.items()},
            "timeline": es["complete"].get("timeline", ""),
            "tokens_in": tokens_in_es,
            "cost": round(tokens_in_es * PRICE_IN / 1e6 + OUT_TOKENS * PRICE_OUT / 1e6, 6),
        },
    }


def main() -> None:
    data = {"price_in": PRICE_IN, "price_out": PRICE_OUT, "model": ask.DEFAULT_MODEL,
            "families": [family(slug) for slug in QUESTIONS]}
    out = ROOT / "pitch" / "data.js"
    out.parent.mkdir(exist_ok=True)
    out.write_text("// Generated by scripts/build_pitch.py from cases/ and narrations/. Do not edit by hand.\n"
                   f"window.PITCH = {json.dumps(data, indent=1, ensure_ascii=False)};\n")
    print(f"{out.relative_to(ROOT)}: {len(data['families'])} families")


if __name__ == "__main__":
    main()

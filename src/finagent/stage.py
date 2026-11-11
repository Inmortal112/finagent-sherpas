"""Stage 3 (owner: C). Presentation -> something the jury watches.

MOCK: one static HTML page. Replace the body with the real player (slides synced
to audio, avatar, questions); keep the signature.
"""
from html import escape
from pathlib import Path

from contracts.schemas import Presentation


def render(presentation: Presentation, out_dir: Path) -> Path:
    facts = {f.id: f for f in presentation.facts}
    blocks = []
    for scene in presentation.scenes:
        fact = facts.get(scene.visual.data.get("fact_id", ""))
        figure = f"<p class='n'>{escape(str(fact.value))} {escape(fact.unit)}</p>" if fact else ""
        blocks.append(
            f"<section><h2>{escape(scene.title)}</h2>{figure}"
            f"<p>{escape(scene.narration)}</p><small>{scene.duration_s} s</small></section>"
        )
    html = (
        f"<!doctype html><html lang='{presentation.language}'><meta charset='utf-8'>"
        f"<title>{escape(presentation.client_name)}</title>"
        "<style>body{font-family:system-ui;max-width:640px;margin:2rem auto;padding:0 1rem}"
        "section{border:1px solid #ccc;border-radius:8px;padding:1rem;margin:1rem 0}"
        ".n{font-size:2.5rem;margin:0}</style>"
        f"<h1>{escape(presentation.client_name)}</h1>{''.join(blocks)}</html>"
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "index.html"
    path.write_text(html, encoding="utf-8")
    return path

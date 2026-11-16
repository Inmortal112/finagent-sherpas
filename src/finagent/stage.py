"""Stage 3 (owner: C). Presentation -> the page the family (and the jury) sees.

One self-contained page (`stage_page.html`) with the `Presentation` inside it: the score first, then the
family's home, which changes as they scroll (a walk through its five parts, the years of the plan, each
step of the plan repairing its part). A "?" button opens a chat that asks the backend (`/ask/stream`);
opened as a plain file, everything but the chat still works.
"""
import json
from html import escape
from pathlib import Path

from contracts.schemas import Presentation

TEMPLATE = Path(__file__).with_name("stage_page.html")


def page(presentation: Presentation) -> str:
    """The whole page as text. The data travels as JSON that cannot close its own <script> tag."""
    data = json.dumps(presentation.model_dump(), ensure_ascii=False).replace("<", "\\u003c")
    return (
        TEMPLATE.read_text(encoding="utf-8")
        .replace("__LANG__", presentation.language)
        .replace("__CLIENT_NAME__", escape(presentation.client_name))
        .replace("__PLAN_STATE_JS__", TEMPLATE.with_name("web").joinpath("plan-state.js").read_text(encoding="utf-8"))
        .replace("__ARCHITECTURAL_CSS__", TEMPLATE.with_name("web").joinpath("architectural.css").read_text(encoding="utf-8"))
        .replace("__PRESENTATION_JSON__", data)
    )


def render(presentation: Presentation, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "index.html"
    path.write_text(page(presentation), encoding="utf-8")
    return path

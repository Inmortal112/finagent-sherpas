"""Another way of hearing the plan: each explanation style is a second track inside the page (owner: B).

The narration is the "story" style. For every other style in `narrator.STYLES` that has a saved text for this
family and mode (narrations/<family>.json, checked by `guard`), the pipeline writes next to index.html:

    styles/<style>/audio/<scene>.mp3 (+ .words.json)   the same voice stage, speaking the other text
    styles.json                                        what the page needs to switch: labels, and text and audio per scene

The page (web/styles.js) swaps the text and the voice in place, so changing style never reloads it and the family
stays in the chapter they were reading. `narration` and the contract are not touched.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

from contracts.schemas import Presentation
from finagent import narrator, voice

log = logging.getLogger(__name__)

FILE = "styles.json"
STORY = "story"   # the narration itself: the plan told as the family's home
# What the family reads when choosing. Every style of narrator.STYLES needs its words here.
LABELS = {
    STORY: {"label": "As a story", "hint": "Your plan told as your home: what stands and what needs repair."},
    "numbers": {"label": "Numbers first", "hint": "The figure first, then what it means for you."},
}


def names() -> list[str]:
    """Every way of explaining, the story first."""
    return [STORY, *narrator.STYLES]


def add_tracks(presentation: Presentation, slug: str, mode: str, out_dir: Path) -> list[str]:
    """Write the other styles of this page (styles/<style>/audio/, styles.json). Returns the styles written.

    Never raises: a style is an extra, the page must come out the same without it.
    """
    target = Path(out_dir) / FILE
    try:
        tracks = {}
        for style in narrator.STYLES:
            texts = narrator.styled(presentation, slug, style, mode)
            if not texts:
                continue
            spoken = voice.synthesize(_only(presentation, texts), Path(out_dir) / "styles" / style)
            tracks[style] = {**LABELS[style], "scenes": {
                scene.id: {"text": scene.narration, "duration_s": scene.duration_s,
                           "audio": f"styles/{style}/{scene.audio_path}" if scene.audio_path else None}
                for scene in spoken.scenes}}
        if not tracks:
            target.unlink(missing_ok=True)   # a page made again without styles must not keep an old track
            return []
        target.write_text(json.dumps({"default": {"name": STORY, **LABELS[STORY]}, "styles": tracks},
                                     ensure_ascii=False), encoding="utf-8")
        return sorted(tracks)
    except Exception as exc:  # noqa: BLE001
        log.warning("Explanation styles skipped (%s: %s)", type(exc).__name__, exc)
        return []


def _only(presentation: Presentation, texts: dict[str, str]) -> Presentation:
    """The same presentation with just the scenes that have another text, saying that text and with no audio yet."""
    result = presentation.model_copy(deep=True)
    result.scenes = [scene for scene in result.scenes if scene.id in texts]
    for scene in result.scenes:
        scene.narration, scene.audio_path, scene.duration_s = texts[scene.id], None, None
    return result

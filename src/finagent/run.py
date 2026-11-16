"""End-to-end pipeline: diagnostic -> brain -> guard -> voice -> stage.

    python -m finagent.run [cases/<family>/financial-health.json]   # one family -> out/index.html
    python -m finagent.run --all    # also every family in both modes -> out/families/<family>/<mode>/

This must work on `main` at all times, with mocks or with real stages.
"""
import json
import sys
from pathlib import Path

from finagent import brain, guard, spanish, stage, voice

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CASE = ROOT / "cases" / "samantha-lewis" / "financial-health.json"


def main(diagnostic_path: Path, out_dir: Path, mode: str = "complete") -> Path:
    diagnostic = json.loads(diagnostic_path.read_text(encoding="utf-8"))
    presentation = brain.build(diagnostic, mode=mode)
    problems = guard.unsupported_numbers(presentation)
    if problems:
        raise SystemExit(f"Narration quotes numbers that are not in the diagnostic: {problems}")
    out_dir.mkdir(parents=True, exist_ok=True)
    presentation = voice.synthesize(presentation, out_dir)
    # A second audio track in Spanish, where a checked translation exists (narrations/es/). Never fails the run.
    spanish.add_audio(presentation, diagnostic_path.parent.name, mode, out_dir)
    (out_dir / "presentation.json").write_text(presentation.model_dump_json(indent=2), encoding="utf-8")
    return stage.render(presentation, out_dir)


def every_family(out_dir: Path) -> list[Path]:
    """One page per family and mode, each with its own voice, where the stage's family switch looks for them."""
    pages = []
    for case in sorted((ROOT / "cases").glob("*/financial-health.json")):
        for mode in brain.MODES:
            pages.append(main(case, out_dir / "families" / case.parent.name / mode, mode))
    return pages


if __name__ == "__main__":
    arguments = [a for a in sys.argv[1:] if a != "--all"]
    source = Path(arguments[0]) if arguments else DEFAULT_CASE
    target = ROOT / "out"
    target.mkdir(exist_ok=True)
    print(f"OK -> {main(source, target)}")
    if "--all" in sys.argv:
        for page in every_family(target):
            print(f"OK -> {page}")

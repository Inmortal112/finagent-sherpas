"""End-to-end pipeline: diagnostic -> brain -> guard -> voice -> stage.

    python -m finagent.run [diagnostic.json]

This must work on `main` at all times, with mocks or with real stages.
"""
import json
import sys
from pathlib import Path

from finagent import brain, guard, stage, voice

ROOT = Path(__file__).resolve().parents[2]


def main(diagnostic_path: Path, out_dir: Path) -> Path:
    diagnostic = json.loads(diagnostic_path.read_text(encoding="utf-8"))
    presentation = brain.build(diagnostic)
    problems = guard.unsupported_numbers(presentation)
    if problems:
        raise SystemExit(f"Narration quotes numbers that are not in the diagnostic: {problems}")
    presentation = voice.synthesize(presentation, out_dir)
    (out_dir / "presentation.json").write_text(presentation.model_dump_json(indent=2), encoding="utf-8")
    return stage.render(presentation, out_dir)


if __name__ == "__main__":
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "fixtures" / "diagnostic_sample.json"
    target = ROOT / "out"
    target.mkdir(exist_ok=True)
    print(f"OK -> {main(source, target)}")

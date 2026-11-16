"""Execute the page's actual scenario logic against all four families (no browser or model calls)."""
import json
from pathlib import Path
import shutil
import subprocess

import pytest

from finagent import brain

ROOT = Path(__file__).resolve().parents[1]
NODE = shutil.which("node")


@pytest.mark.skipif(not NODE, reason="Node is needed to execute the browser's scenario logic")
@pytest.mark.parametrize("case", sorted((ROOT / "cases").glob("*/financial-health.json")), ids=lambda p: p.parent.name)
def test_preview_completion_and_unavailable_combined_scores(case):
    plan = brain.build(json.loads(case.read_text(encoding="utf-8")))
    data = plan.model_dump()
    source = (ROOT / "src/finagent/web/plan-state.js").read_text(encoding="utf-8")
    program = source + r'''
const assert = require("node:assert/strict");
const plan = JSON.parse(require("node:fs").readFileSync(0, "utf8"));
const base = Number(plan.facts.find(f => f.id === "score").value);
const moves = plan.scenes.filter(s => s.id.startsWith("move_"));
const combined = plan.scenes.find(s => s.id === "all_moves");
const ids = moves.map(s => s.id);
const run = (completed = [], preview = null) => planScenario({ base, moves, combined, completed, preview });
assert.equal(run().score, base);
assert.deepEqual(run().selected, []);
assert.equal(run(["not-a-step"]).score, base);
for (const move of moves) {
  const completed = [];
  const preview = run(completed, move.id);
  assert.equal(preview.score, move.visual.data.score_after);
  assert.equal(preview.isPreview, true);
  assert.deepEqual(completed, [], "preview must not mutate completion");
  assert.deepEqual(run().selected, [], "closing preview restores the original plan");
  assert.equal(run([move.id]).score, move.visual.data.score_after);
  assert.equal(run([move.id]).isPreview, false);
}
if (ids.length > 2) assert.equal(run(ids.slice(0, 2)).score, null, "partial combinations have no score");
assert.equal(run(ids).score, combined ? combined.visual.data.score_after : null);
assert.equal(run([], "all").score, combined ? combined.visual.data.score_after : null);
assert.deepEqual(run([], "all").selected, ids);
const baseline = plan.scenes.find(s => s.id === "intro").visual.data.house;
for (const [part, state] of Object.entries(baseline)) {
  assert.equal(repairState(part, state, moves, []), state);
  const related = moves.filter(m => m.visual.data.house_part === part);
  if (related.some(m => m.visual.data.pays_part_of_debt)) assert.equal(repairState(part, state, moves, ids), state, "partial payment cannot repair all debt");
  if (related.length > 1) assert.equal(repairState(part, state, moves, [related[0].id]), state, "one change is not all changes to this part");
}
'''
    result = subprocess.run([NODE, "-e", program], input=json.dumps(data), capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, result.stderr

// Shared with the offline page by stage.py. No DOM, storage, or inferred financial calculations.
function planScenario({ base, moves, combined, completed = [], preview = null }) {
  const known = new Set(moves.map((move) => move.id));
  const confirmed = new Set(completed.filter((id) => known.has(id)));
  const selected = preview === "all" ? moves : preview ? moves.filter((move) => move.id === preview) : moves.filter((move) => confirmed.has(move.id));
  const isPreview = preview !== null;
  let score = base;
  let label = "Original plan";
  let detail = "The score in your original Sherpas plan.";
  if (selected.length === 1) {
    score = selected[0].visual.data.score_after;
    label = isPreview ? "This step alone · preview" : "This step alone · reported done";
    detail = "Sherpas scored this step on its own. Your plan has not been recalculated.";
  } else if (moves.length && selected.length === moves.length && combined) {
    score = combined.visual.data.score_after;
    label = isPreview ? "All steps · preview" : "All steps · reported done";
    detail = "The combined scenario supplied by Sherpas. Your plan has not been recalculated.";
  } else if (selected.length > 1) {
    score = null;
    label = isPreview ? "All steps · preview" : "Selected steps · reported done";
    detail = "Sherpas has not scored these steps together. See each step's individual result below.";
  }
  return { score, label, detail, selected: selected.map((move) => move.id), isPreview };
}

function repairState(part, baseline, moves, selected) {
  const selectedIds = new Set(selected);
  const related = moves.filter((move) => move.visual.data.house_part === part);
  // A partial debt payment and a subset of the planned changes never depict a fully repaired part.
  return related.length && related.every((move) => selectedIds.has(move.id)) && !related.some((move) => move.visual.data.pays_part_of_debt)
    ? "repaired" : baseline;
}

// Choose how the plan is explained: the same scenes told another way ("numbers first"), without leaving the page.
// Each adult of a household keeps their own choice.
//
//   const styles = await create({ scenes, household, onChange })   null when this page has one way only (no styles.json)
//   styles.list                 [{ name, label, hint }], the story (the page's own narration) first
//   styles.wanted               the style this person chose
//   styles.current              the style on the page now (the story while paused)
//   styles.use(name)            switch, and remember it for the person using the page
//   styles.forPerson(who)       that adult's own choice, applied (null: the household's)
//   styles.pause(true)          hold the story while Spanish is on: the other styles exist in English only
//   styles.mount(opts, after)   add the "Explain it: As a story | Numbers first" switch to the intro options
//
// The track is made by the pipeline (src/finagent/styles.py): styles.json holds each style's text and audio per scene.
// Switching rewrites each narration paragraph and points the scene at the other audio, so the voice, the "Hear this"
// buttons and the captions follow without knowing about styles.

const KEY = "uor-style-";
const STYLE = `
.seg.style-switch.held button { opacity: .45; pointer-events: none; }
`;

export async function create({ scenes = () => [], household = () => "", onChange = () => {} } = {}) {
  let data = null;
  try {
    const reply = await fetch("styles.json");
    data = reply.ok ? await reply.json() : null;
  } catch (e) { data = null; }
  if (!data || !data.styles || !Object.keys(data.styles).length) return null;

  const style = document.createElement("style"); style.textContent = STYLE; document.head.append(style);
  const story = data.default || { name: "story", label: "As a story", hint: "" };
  const list = [story, ...Object.entries(data.styles).map(([name, s]) => ({ name, label: s.label || name, hint: s.hint || "" }))];
  const known = (name) => list.some((s) => s.name === name);
  const built = new WeakMap();   // scene -> the words and voice the page was built with (the story)
  let wanted = story.name, paused = false, who = null, switches = [];

  const keyFor = (person) => KEY + household() + (person ? "-" + person : "");
  const saved = (person) => {
    try { const name = localStorage.getItem(keyFor(person)); return known(name) ? name : null; } catch (e) { return null; }
  };
  const current = () => (paused ? story.name : wanted);

  // Put the words and the voice of the current style on the page. Returns whether anything changed.
  function apply() {
    const track = (data.styles[current()] || {}).scenes || {};
    let changed = false;
    scenes().forEach((scene) => {
      if (!built.has(scene)) built.set(scene, { narration: scene.narration, audio_path: scene.audio_path, duration_s: scene.duration_s });
      const first = built.get(scene), entry = track[scene.id];
      const next = entry ? { narration: entry.text, audio_path: entry.audio || null, duration_s: entry.duration_s ?? first.duration_s } : first;
      if (next.narration !== scene.narration) {
        document.querySelectorAll("p").forEach((p) => {
          if (p.dataset.es || p.textContent !== scene.narration) return;   // p[data-es] is the Spanish line under it
          p.textContent = next.narration;
          delete p.dataset.captions;   // web/captions.js wraps the new words when they are first spoken
        });
        changed = true;
      }
      Object.assign(scene, next);
    });
    switches = switches.filter((box) => box.isConnected);
    switches.forEach((box) => {
      box.classList.toggle("held", paused);
      box.title = paused ? "The other ways of explaining are in English only" : "";
      box.querySelector("span").textContent = paused ? "Explain it · English only" : "Explain it";
      [...box.querySelectorAll("button")].forEach((b) => {
        b.classList.toggle("on", b.dataset.style === current());
        b.setAttribute("aria-pressed", String(b.dataset.style === current()));
      });
    });
    return changed;
  }

  function use(name) {
    if (!known(name)) return;
    wanted = name;
    try { localStorage.setItem(keyFor(who), name); } catch (e) { /* private window */ }
    if (apply()) onChange(current());
  }

  return {
    list,
    get wanted() { return wanted; },
    get current() { return current(); },
    get paused() { return paused; },
    use,
    forPerson(person) {
      who = person || null;
      wanted = saved(who) || saved(null) || story.name;
      if (apply()) onChange(current());
    },
    pause(on) {
      paused = Boolean(on);
      if (apply()) onChange(current());
    },
    mount(opts, after) {
      if (!opts || opts.querySelector(".style-switch")) { apply(); return; }
      const box = document.createElement("div"); box.className = "seg style-switch";
      const label = document.createElement("span"); label.className = "mono"; label.textContent = "Explain it"; box.append(label);
      list.forEach(({ name, label: text, hint }) => {
        const b = document.createElement("button"); b.type = "button"; b.textContent = text; b.title = hint; b.dataset.style = name;
        b.addEventListener("click", () => use(name));
        box.append(b);
      });
      if (after && after.parentNode === opts) after.after(box); else opts.append(box);
      switches.push(box);
      apply();
    },
  };
}

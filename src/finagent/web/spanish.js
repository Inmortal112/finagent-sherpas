// Listen in Spanish: a second audio track for families who speak Spanish at home. The page stays in English; with
// "Español" on, the voice speaks Spanish and each narration shows its Spanish text underneath (the captions light it).
//
//   const spanish = await create({ scenes, onChange })   null when this page has no Spanish track (no es.json)
//   spanish.mount(opts)      add the "Listen in: English | Español" switch to the intro options
//   spanish.audioFor(src)    the Spanish audio of a scene's MP3 while Spanish is on; otherwise the same address
//
// The track is made by the pipeline (src/finagent/spanish.py): es.json holds the Spanish text of each scene, and
// audio/es/<scene>.mp3 its voice. Every translation was checked to hold exactly the same figures as the English.

const KEY = "uor-lang";
const STYLE = `
p.es-line { margin-top: .6rem; padding-left: .8rem; border-left: 3px solid rgba(119, 75, 229, .35); font-size: .95em; opacity: .92; }
`;

export async function create({ scenes = () => [], onChange = () => {} } = {}) {
  let texts = null;
  try {
    const reply = await fetch("es.json");
    texts = reply.ok ? await reply.json() : null;
  } catch (e) { texts = null; }
  if (!texts || !Object.keys(texts).length) return null;

  const style = document.createElement("style"); style.textContent = STYLE; document.head.append(style);
  let on = false;
  try { on = localStorage.getItem(KEY) === "es"; } catch (e) { /* private window */ }

  // Under each narration paragraph, its Spanish text (only while Spanish is on).
  function show() {
    document.querySelectorAll("p.es-line").forEach((p) => p.remove());
    if (!on) return;
    scenes().forEach((scene) => {
      if (!texts[scene.id]) return;
      document.querySelectorAll("p").forEach((p) => {
        if (p.classList.contains("es-line") || p.textContent !== scene.narration) return;
        const line = document.createElement("p");
        line.className = "es-line"; line.lang = "es"; line.dataset.es = scene.id; line.textContent = texts[scene.id];
        p.after(line);
      });
    });
  }

  return {
    get on() { return on; },
    audioFor(src) {
      if (!on || !src) return src;
      const match = /(^|\/)audio\/([^/?#]+)\.mp3$/.exec(src);
      return match && texts[decodeURIComponent(match[2])] ? src.replace(/audio\/([^/?#]+\.mp3)$/, "audio/es/$1") : src;
    },
    mount(opts) {
      if (!opts || opts.querySelector(".lang-switch")) { setTimeout(show, 0); return; }
      const box = document.createElement("div"); box.className = "seg lang-switch";
      const label = document.createElement("span"); label.className = "mono"; label.textContent = "Listen in"; box.append(label);
      [["en", "English"], ["es", "Español"]].forEach(([value, text]) => {
        const b = document.createElement("button"); b.textContent = text; b.lang = value;
        b.className = (value === "es") === on ? "on" : "";
        b.addEventListener("click", () => {
          if ((value === "es") === on) return;
          on = value === "es";
          try { localStorage.setItem(KEY, on ? "es" : "en"); } catch (e) { /* private window */ }
          [...box.querySelectorAll("button")].forEach((x) => x.classList.toggle("on", x === b));
          show(); onChange(on);
        });
        box.append(b);
      });
      opts.append(box);
      setTimeout(show, 0);   // the chapters are built right after the options
    },
  };
}

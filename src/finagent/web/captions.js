// Captions that follow the voice: each word of the narration lights up as it is said, so the family can read along
// (hard of hearing, a noisy room, or simply easier to follow). The text on the page is not changed: its words are
// only wrapped, one by one, the first time the scene is spoken.
//
//   create({ voice, scenes })   voice: the page's <audio> for the narration; scenes: the presentation's scenes
//
// The timings come from the voice stage: audio/<scene>.words.json next to each MP3 (src/finagent/captions.py).
// No file (an old build, the mock voice), no captions: the page works the same.

const STYLE = `
.cap-word { border-radius: .28em; transition: background-color .12s ease, box-shadow .12s ease; }
.cap-word.cap-now { background: rgba(119, 75, 229, .2); box-shadow: 0 0 0 .14em rgba(119, 75, 229, .2); }
@media (prefers-reduced-motion: reduce) { .cap-word { transition: none; } }
`;

export function create({ voice, scenes = [], root = document } = {}) {
  if (!voice) return;
  const style = document.createElement("style"); style.textContent = STYLE; document.head.append(style);

  const timings = new Map();   // words file address -> Promise of its words (or null)
  let spans = [], words = [], current = -1, frame = 0, playing = "";

  const sceneOf = (src) => {
    const match = /\/audio\/([^/?#]+)\.mp3(?:[?#].*)?$/.exec(src || "");
    return match ? scenes.find((scene) => scene.id === decodeURIComponent(match[1])) : null;
  };
  const load = (src) => {
    const address = src.replace(/\.mp3(?:[?#].*)?$/, ".words.json");
    if (!timings.has(address)) {
      timings.set(address, fetch(address).then((r) => (r.ok ? r.json() : null)).then((d) => (d && d.words) || null).catch(() => null));
    }
    return timings.get(address);
  };

  // Wrap each word of the paragraph that shows this narration. Done once per paragraph; the text stays the same.
  function wrap(scene, list) {
    const found = [];
    root.querySelectorAll("p").forEach((p) => {
      if (p.textContent !== scene.narration) return;
      if (!p.dataset.captions) {
        const text = scene.narration, pieces = document.createDocumentFragment();
        let at = 0;
        list.forEach(([start, end]) => {
          if (start > at) pieces.append(text.slice(at, start));
          const span = document.createElement("span"); span.className = "cap-word"; span.textContent = text.slice(start, end);
          pieces.append(span); at = end;
        });
        if (at < text.length) pieces.append(text.slice(at));
        p.replaceChildren(pieces); p.dataset.captions = "on";
      }
      found.push([...p.querySelectorAll(".cap-word")]);
    });
    return found;
  }

  function light(index) {
    if (index === current) return;
    spans.forEach((line) => {
      if (line[current]) line[current].classList.remove("cap-now");
      if (line[index]) line[index].classList.add("cap-now");
    });
    current = index;
  }

  function tick() {
    const t = voice.currentTime;
    let index = -1;
    for (let i = 0; i < words.length && words[i][2] <= t; i++) index = i;
    // Between two words the last one stays lit; after a long pause (over a second) nothing is.
    if (index >= 0 && t > words[index][3] + 1) index = -1;
    light(index);
  }

  function stop() {
    clearInterval(frame); frame = 0;
    light(-1);
    spans = []; words = []; playing = "";
  }

  async function start() {
    const src = voice.currentSrc || voice.src, scene = sceneOf(src);
    if (!scene) { stop(); return; }
    if (playing === src && frame) return;
    stop(); playing = src;
    const list = await load(src);
    if (!list || playing !== src || voice.paused) return;
    words = list; spans = wrap(scene, list);
    if (spans.length) { tick(); frame = setInterval(tick, 40); }   // 25 times a second is plenty for words
  }

  voice.addEventListener("playing", start);
  ["pause", "ended", "emptied", "error"].forEach((name) => voice.addEventListener(name, stop));
}

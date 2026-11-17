// The opening screen: before the walk through the home, each person says who is here, how much detail they want and
// how they like things explained. One tap each, with a choice already made, so "Step inside" works straight away.
// Nothing is locked: "Change" in the top bar opens it again from any chapter.
//
//   const welcome = create({ site, household, family, adults, person, mode, styles, families, ready, apply })
//     site: the address the pages hang from; household(): the family's name; family(): its folder name, or null
//     adults(): first names of the adults; person(): who is using the page, or null; mode(): "simple" | "complete"
//     styles(): this page's own ways of explaining (web/styles.js), or null
//     families: the bar's <select> with the other families (the demo's switch); ready: resolves when it is filled
//     apply({ person, mode, style }): the page takes the choices (it may leave for the other mode's page)
//   welcome.offer()      show it on a first visit (?welcome=1 always shows it, ?welcome=0 never)
//   welcome.open(first)  show it now; first: with the welcome, otherwise as "Your choices"
//
// The order is who, how much, how: the other ways of explaining exist in the full mode only, so that question is
// asked once "In full" is chosen.

import { listOf, load, remember, remembered } from "./styles.js";

const DONE = "uor-setup-";
const MODES = [
  ["simple", "Simply", "Short sentences and big buttons. The voice leads."],
  ["complete", "In full", "Every figure, and a home you can turn around."],
];
const STYLE = `
.wl { position: fixed; inset: 0; z-index: 28; display: grid; place-items: center; padding: 5.2rem 1rem 1.2rem; overflow: auto;
  background: rgba(10,12,24,.62); -webkit-backdrop-filter: blur(10px); backdrop-filter: blur(10px); }
.wl[hidden] { display: none; }
.wl-card { width: 100%; max-width: 35rem; background: #fff; color: var(--ink, #141419); border-radius: 24px; padding: 1.5rem 1.5rem 1.2rem;
  box-shadow: 0 40px 100px -30px rgba(10,12,20,.6); outline: none; }
.wl-card h2 { font-weight: 500; font-size: clamp(1.45rem, 4.6vw, 1.95rem); line-height: 1.15; letter-spacing: -.02em; margin: .35rem 0 .3rem; }
.wl-kicker { color: var(--violet-2, #774be5); }
.wl-lede { color: var(--ink-2, #44445d); margin: 0; font-size: .96rem; }
.wl-family { display: flex; align-items: center; gap: .6rem; margin-top: .8rem; color: var(--ink-3, #717390); }
.wl-family select { flex: 1; min-width: 0; border: 1px solid var(--line, #dfe0e8); border-radius: 999px; padding: .4rem .8rem; background: #fff; font-size: .88rem; }
.wl-row { margin-top: 1rem; }
.wl-row > span { display: block; color: var(--ink-3, #717390); margin-bottom: .4rem; }
.wl-opts { display: grid; grid-template-columns: repeat(auto-fit, minmax(8rem, 1fr)); gap: .5rem; }
.wl-opt { text-align: left; border: 1.5px solid var(--line, #dfe0e8); background: #fff; border-radius: 14px; padding: .6rem .8rem;
  display: grid; align-content: center; gap: .1rem; min-height: 3.3rem; transition: border-color .15s, background .15s; }
.wl-opt b { font-weight: 500; font-size: 1rem; }
.wl-opt small { color: var(--ink-3, #717390); font-size: .78rem; line-height: 1.3; }
.wl-opt[aria-pressed="true"] { border-color: var(--blue, #4565d6); background: #eef1ff; box-shadow: 0 0 0 1px var(--blue, #4565d6) inset; }
.wl-go { margin-top: 1.2rem; width: 100%; justify-content: center; font-size: 1.05rem; }
.wl-note { color: var(--ink-3, #717390); font-size: .8rem; margin: .7rem 0 0; text-align: center; }
.change-btn { display: inline-flex; align-items: center; gap: .4rem; flex: none; border: 1px solid currentColor; background: transparent;
  border-radius: 999px; padding: .45rem .9rem; font-size: .82rem; opacity: .85; }
.change-btn:hover { opacity: 1; }
.change-btn svg { width: 17px; height: 17px; }
body.welcoming { overflow: hidden; }
body.welcoming .ask-fab { display: none; }
@media (max-width: 860px) {
  .wl { padding: 4.4rem .8rem 1rem; place-items: start center; }
  .wl-card { padding: 1.2rem 1.1rem 1rem; border-radius: 20px; }
  .change-btn { width: 36px; height: 36px; padding: 0; justify-content: center; }
  .change-btn span { display: none; }
  .bar.has-change select { max-width: 46vw; }
}
@media (prefers-reduced-motion: reduce) { .wl-opt { transition: none; } }
`;
const SLIDERS = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><path d="M4 7h9M17 7h3M4 17h3M11 17h9"/><circle cx="15" cy="7" r="2"/><circle cx="9" cy="17" r="2"/></svg>';

const el = (tag, cls, text) => { const n = document.createElement(tag); if (cls) n.className = cls; if (text != null) n.textContent = text; return n; };

export function create({ site = "", household = () => "", family = () => null, adults = () => [], person = () => null,
                         mode = () => "complete", styles = () => null, families = null, ready = null, apply = () => {} } = {}) {
  const style = el("style"); style.textContent = STYLE; document.head.append(style);
  const layer = el("div", "wl"); layer.hidden = true;
  const card = el("div", "wl-card"); card.tabIndex = -1;
  card.setAttribute("role", "dialog"); card.setAttribute("aria-modal", "true"); card.setAttribute("aria-labelledby", "wlTitle");
  layer.append(card);
  document.body.append(layer);

  let state = { person: null, mode: "complete", style: null }, first = true, offered = null, touchedStyle = false;

  const done = () => { try { return localStorage.getItem(DONE + household()) === "1"; } catch (e) { return false; } };
  const markDone = () => { try { localStorage.setItem(DONE + household(), "1"); } catch (e) { /* private window */ } };

  // The ways of explaining on offer: this page's own, or (from the simple page) the full page's.
  async function findStyles() {
    const own = styles();
    if (own) return own.list;
    if (!family()) return null;
    const data = await load(`${site}families/${family()}/complete/styles.json`);
    return data ? listOf(data) : null;
  }
  const styleFor = (who) => {
    const name = remembered(household(), who);
    return offered && offered.some((s) => s.name === name) ? name : offered ? offered[0].name : null;
  };

  function row(key, title, options, value, pick) {
    const box = el("div", "wl-row"), label = el("span", "mono", title), list = el("div", "wl-opts");
    list.setAttribute("role", "group"); list.setAttribute("aria-label", title);
    options.forEach(([name, text, hint]) => {
      const b = el("button", "wl-opt"); b.type = "button"; b.dataset.row = key; b.dataset.name = name;
      b.append(el("b", "", text));
      if (hint) b.append(el("small", "", hint));
      b.setAttribute("aria-pressed", String(name === value));
      b.addEventListener("click", () => {
        pick(name);
        draw();   // the card is drawn again (a row may come or go), so put the keyboard back where it was
        const again = [...card.querySelectorAll(".wl-opt")].find((x) => x.dataset.row === key && x.dataset.name === name);
        if (again) again.focus({ preventScroll: true });
      });
      list.append(b);
    });
    box.append(label, list);
    return box;
  }

  function draw() {
    const people = adults(), rows = [], hasStyles = Boolean(offered && offered.length > 1);
    if (people.length > 1) {
      rows.push(["person", "Who is here?", [...people.map((name) => [name, name, ""]), ["", people.length === 2 ? "Both of us" : "All of us", ""]],
        state.person || "", (name) => { state.person = name || null; if (!touchedStyle) state.style = styleFor(state.person); }]);
    }
    rows.push(["mode", "How much detail?", MODES, state.mode, (name) => { state.mode = name; }]);
    if (hasStyles && state.mode === "complete") {
      rows.push(["style", "How should we explain it?", offered.map((s) => [s.name, s.label, s.hint]), state.style,
        (name) => { state.style = name; touchedStyle = true; }]);
    }
    const choices = (people.length > 1 ? 1 : 0) + 1 + (hasStyles ? 1 : 0);   // the same count whatever is picked

    card.replaceChildren();
    card.append(el("div", "mono wl-kicker", "Under One Roof"));
    const title = el("h2", "", first ? `Welcome home, ${household()}.` : "Your choices"); title.id = "wlTitle";
    card.append(title);
    card.append(el("p", "wl-lede", first
      ? `${choices > 1 ? "A few quick choices" : "One quick choice"}, so your plan is explained your way. You can change ${choices > 1 ? "them" : "it"} whenever you like.`
      : "Change anything here. You stay in the chapter you were reading."));

    // The demo's family switch, when the backend offers more than one plan.
    if (families && !families.hidden && families.options.length > 1) {
      const line = el("label", "wl-family"), text = el("span", "mono", "Family"), select = el("select");
      select.setAttribute("aria-label", "Family");
      [...families.options].forEach((o) => select.append(new Option(o.textContent, o.value)));
      select.value = families.value;
      select.addEventListener("change", () => { families.value = select.value; families.dispatchEvent(new Event("change")); });
      line.append(text, select);
      card.append(line);
    }

    rows.forEach(([key, name, options, value, pick], i) =>
      card.append(row(key, choices > 1 ? `${i + 1} · ${name}` : name, options, value, pick)));
    const go = el("button", "pill dark wl-go", first ? "Step inside" : "Done"); go.type = "button";
    go.addEventListener("click", finish);
    card.append(go);
    if (first) card.append(el("p", "wl-note", "Nothing is locked: “Change”, at the top, brings this back."));
  }

  function finish() {
    const picked = { ...state };
    if (!(offered && offered.length > 1) || picked.mode !== "complete") picked.style = null;
    if (picked.style) remember(household(), picked.person, picked.style);
    markDone();
    close();
    apply(picked);
  }

  function close() {
    layer.hidden = true;
    document.body.classList.remove("welcoming");
  }

  async function open(asFirst = false) {
    first = asFirst; touchedStyle = false;
    const own = styles();
    if (own) offered = own.list;   // known at once on a full page; the simple page has to ask for the full page's
    state = { person: person() || null, mode: mode(), style: own ? own.wanted : styleFor(person() || null) };
    layer.hidden = false;
    document.body.classList.add("welcoming");
    draw();
    card.focus({ preventScroll: true });
    if (offered === null) {
      offered = (await findStyles()) || [];
      if (!touchedStyle) state.style = styleFor(state.person);
      if (!layer.hidden) draw();
    }
  }

  // Leaving it without choosing keeps what was there, and it is not offered again.
  layer.addEventListener("click", (event) => { if (event.target === layer) { markDone(); close(); } });
  addEventListener("keydown", (event) => { if (event.key === "Escape" && !layer.hidden) { markDone(); close(); } });
  if (ready && ready.then) ready.then(() => { if (!layer.hidden) draw(); });

  // "Change" in the top bar, next to the voice button.
  const bar = document.getElementById("bar");
  if (bar && !bar.querySelector(".change-btn")) {
    const b = el("button", "change-btn"); b.type = "button"; b.title = "Change who is here, the detail and how it is explained";
    b.setAttribute("aria-label", b.title);
    b.innerHTML = SLIDERS + "<span>Change</span>";
    b.addEventListener("click", () => open(false));
    bar.insertBefore(b, bar.querySelector("[data-sound]"));
    bar.classList.add("has-change");
  }

  return {
    open, close,
    get isOpen() { return !layer.hidden; },
    offer() {
      const asked = new URLSearchParams(location.search).get("welcome");
      if (asked === "0" || (asked !== "1" && done())) return false;
      open(true);
      return true;
    },
  };
}

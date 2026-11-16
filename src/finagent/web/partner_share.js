// "Send a voice note to Emily": in a couple, the one who went through the plan sends the other a short voice
// message with what worried them and the step they chose. The backend writes and speaks it (GET /partner-note,
// src/finagent/partner_note.py); this file shows it under the chosen step and hands the MP3 to the phone's share
// sheet (WhatsApp, Messages...). Where the browser cannot share a file, it plays the note and offers to save it.
//
//   offer({ base, session, person, people, after })
//     base: the backend's address; session: the session id; person: who is using the page (or null)
//     people: the family's people from the intro scene; after: the element to put the box after
//
// A plan for one person, or no step chosen yet: nothing is shown.

const BOX_ID = "partnerNote";

export async function offer({ base, session, person = null, people = [], after } = {}) {
  if (base == null || !session || !after) return;   // base is "" when the page and the backend share an address
  const adults = people.filter((p) => p.role !== "child").map((p) => p.first_name);
  if (adults.length < 2) return;

  if (!document.getElementById(BOX_ID + "Style")) {
    const style = document.createElement("style"); style.id = BOX_ID + "Style";
    style.textContent = `#${BOX_ID} .row { display: flex; gap: .5rem; margin-top: .7rem; flex-wrap: wrap; } #${BOX_ID} p { margin: .5rem 0 0; font-style: italic; }`;
    document.head.append(style);
  }
  let box = document.getElementById(BOX_ID);
  if (!box) { box = document.createElement("div"); box.id = BOX_ID; box.className = "first-move"; after.after(box); }

  let note;
  try {
    const query = `session_id=${encodeURIComponent(session)}${person ? `&person=${encodeURIComponent(person)}` : ""}`;
    note = await (await fetch(`${base}/partner-note?${query}`)).json();
  } catch (e) { box.remove(); return; }

  box.replaceChildren();
  if (!note.available) {
    // The page does not know who is using it yet: ask, then try again.
    if (person || !/who is sending/i.test(note.reason || "")) { box.remove(); return; }
    box.append(el("div", "eyebrow mono", "A voice note for your partner"), el("div", "small", "Who is sending it?"));
    const row = el("div", "row");
    adults.forEach((name) => {
      const b = el("button", "pill ghost", name);
      b.addEventListener("click", () => offer({ base, session, person: name, people, after }));
      row.append(b);
    });
    box.append(row);
    return;
  }

  const address = base + note.audio_url, name = `note-for-${note.to}.mp3`;
  box.append(el("div", "eyebrow mono", `A voice note for ${note.to}`), el("p", "small", `“${note.text}”`));
  const row = el("div", "row"), send = el("button", "pill dark", `Send to ${note.to}`), hear = el("button", "pill ghost", "Hear it first");
  const status = el("div", "small"); status.setAttribute("aria-live", "polite");
  row.append(send, hear); box.append(row, status);

  // Fetch the audio now: an iPhone only opens the share sheet if nothing slow happens between the tap and the call.
  let file = null;
  const ready = fetch(address).then((r) => (r.ok ? r.blob() : null))
    .then((blob) => { if (blob) file = new File([blob], name, { type: "audio/mpeg" }); }).catch(() => {});

  const player = new Audio();
  hear.addEventListener("click", () => {
    if (!player.paused) { player.pause(); hear.textContent = "Hear it first"; return; }
    player.src = file ? URL.createObjectURL(file) : address;
    player.play().then(() => { hear.textContent = "Stop"; }).catch(() => { status.textContent = "The note could not be played."; });
  });
  player.addEventListener("ended", () => { hear.textContent = "Hear it first"; });

  send.addEventListener("click", async () => {
    if (file && navigator.canShare && navigator.canShare({ files: [file] })) {
      try { await navigator.share({ files: [file], title: `A note for ${note.to}` }); status.textContent = `Sent to ${note.to}.`; }
      catch (e) { if (e.name !== "AbortError") status.textContent = "Sharing did not work. You can save the note instead."; else return; }
      if (status.textContent.startsWith("Sent")) return;
    }
    await ready;
    if (!file) { status.textContent = "The note is not ready. Please try again in a moment."; return; }
    const link = document.createElement("a");   // no share sheet here (a computer): save the MP3 instead
    link.href = URL.createObjectURL(file); link.download = name; link.click();
    status.textContent = `Saved as ${name}. Send it to ${note.to} from your messages.`;
  });
}

function el(tag, className, text) {
  const node = document.createElement(tag);
  node.className = className;
  if (text != null) node.textContent = text;
  return node;
}

// The sound of the family's home: soft rain while parts are broken, a bird now and then once the plan is healthy,
// and a short chime when a step is done. Always far below the voice, and lower still while the voice speaks
// (ducking), so every word stays clear. Made with the Web Audio API: no sound files, nothing to download or license.
//
//   const sound = create({ voice, enabled })  voice: the page's <audio> for the narration; enabled: the sound switch
//   sound.setWeather(health)   0 = a low score (rain) ... 1 = a high score (birds). Same scale as the 3D sky
//   sound.repaired()           a step was done: a soft chime and a couple of birds
//   sound.previewed()          the family previews a change: a quieter, quicker sparkle (not the "done" chime)
//   sound.setEnabled(on)       the page's sound button (voice and background go on and off together)
//
// Browsers only let a page make sound after a tap, so nothing plays until the first one. It goes quiet while the
// tab is hidden. Plan: 02-DOCS/ftd/voz-casa-suena.md.

// Levels, as the gain of each sound (1 = full scale; the narration plays at full scale). Measured in the browser on
// 2026-11-16 against a real narration: the loudest rain is about 30 dB below the voice (its loudest drops 21 to
// 25 dB under the voice's peaks), and about 39 dB below while the voice speaks; the chime peaks about 20 dB under
// the voice's peaks, the preview sparkle about 23 dB under them; those two are not lowered while the voice speaks.
const RAIN_MAX = 0.022;     // the loudest rain (see RAIN_FULL)
const BIRD_LEVEL = 0.012;   // one chirp
const CHIME_LEVEL = 0.035;  // the "done" chime (never ducked: it answers a tap, so it must always be heard)
const SPARKLE_LEVEL = 0.03; // the "preview" sparkle, softer than the chime (never ducked either)
const DUCKED = 0.35;        // background level while the voice speaks
const FADE_S = 1.2;         // how long the background takes to come back after the voice
// health is score / 100 (healthOf in stage_page.html). These follow the 3D home (house3d.js), so the family hears
// rain only while they see it, and birds only while they see them fly.
const RAIN_UNTIL = 0.38;    // no rain from this health up: where the rain stops falling in the 3D home
const RAIN_FULL = 0.26;     // the loudest rain from this health down (the picture keeps getting heavier below it)
const BIRDS_FROM = 0.45;    // birds from this health up: where they start to fly in the 3D home
const NOOP = { setWeather() {}, repaired() {}, previewed() {}, setEnabled() {} };

export function create({ voice = null, enabled = true } = {}) {
  const Context = window.AudioContext || window.webkitAudioContext;
  if (!Context) return NOOP;

  let ctx = null, master, bed, rain, health = 0.5, on = enabled, birdTimer = 0;

  function start() {
    if (ctx) return;
    ctx = new Context();
    master = ctx.createGain(); master.gain.value = on ? 1 : 0; master.connect(ctx.destination);
    bed = ctx.createGain(); bed.gain.value = voice && !voice.paused ? DUCKED : 1; bed.connect(master);
    scheduleBirds();
    // Drawing the rain takes a moment: do it just after the tap, so the tap itself never waits for it.
    setTimeout(() => { rain = makeRain(ctx, bed); applyWeather(0); }, 0);
  }

  // The first tap anywhere unlocks the sound (iPhone needs it inside the tap itself).
  const unlock = () => {
    start();
    if (ctx.state !== "running" && on && !document.hidden) ctx.resume().catch(() => {});
  };
  ["pointerdown", "touchend", "keydown"].forEach((name) => addEventListener(name, unlock, { capture: true, passive: true }));

  document.addEventListener("visibilitychange", () => {
    if (!ctx) return;
    if (document.hidden) ctx.suspend().catch(() => {});
    else if (on) ctx.resume().catch(() => {});
  });

  // Ducking: the background steps back while the narration or an answer is playing.
  if (voice) {
    const duck = (down) => {
      if (!ctx) return;
      const now = ctx.currentTime;
      bed.gain.cancelScheduledValues(now);
      bed.gain.setValueAtTime(bed.gain.value, now);
      bed.gain.linearRampToValueAtTime(down ? DUCKED : 1, now + (down ? 0.25 : FADE_S));
    };
    voice.addEventListener("playing", () => duck(true));
    ["pause", "ended", "emptied", "error"].forEach((name) => voice.addEventListener(name, () => duck(false)));
  }

  function applyWeather(seconds = 2) {
    if (!rain) return;
    const amount = Math.min(1, Math.max(0, (RAIN_UNTIL - health) / (RAIN_UNTIL - RAIN_FULL)));   // 1 up to RAIN_FULL, 0 from RAIN_UNTIL
    const now = ctx.currentTime;
    rain.gain.cancelScheduledValues(now);
    rain.gain.setValueAtTime(rain.gain.value, now);
    rain.gain.linearRampToValueAtTime(RAIN_MAX * amount, now + seconds);
  }

  function scheduleBirds() {
    clearTimeout(birdTimer);
    birdTimer = setTimeout(() => {
      if (ctx && on && !document.hidden && health >= BIRDS_FROM) chirp(ctx, bed, BIRD_LEVEL * (0.6 + 0.4 * health));
      scheduleBirds();
    }, 7000 + Math.random() * 9000);
  }

  return {
    setWeather(value) {
      const next = Math.min(1, Math.max(0, Number(value) || 0));
      if (Math.abs(next - health) < 0.001) return;
      health = next;
      applyWeather();
    },
    repaired() {
      if (!ctx || !on) return;
      chime(ctx, master, CHIME_LEVEL);
      setTimeout(() => chirp(ctx, bed, BIRD_LEVEL), 700);
      setTimeout(() => chirp(ctx, bed, BIRD_LEVEL * 0.8), 1500);
    },
    previewed() {
      if (!ctx || !on) return;
      sparkle(ctx, master, SPARKLE_LEVEL);
    },
    setEnabled(value) {
      on = Boolean(value);
      if (!ctx) return;
      const now = ctx.currentTime;
      master.gain.cancelScheduledValues(now);
      master.gain.setValueAtTime(master.gain.value, now);
      master.gain.linearRampToValueAtTime(on ? 1 : 0, now + 0.4);
      if (on && !document.hidden) ctx.resume().catch(() => {});
    },
  };
}

// Rain. What makes the ear say "rain" is not a hiss but the drops: hundreds of tiny ticks a second at random,
// a clearer "plink" now and then, and different drops in each ear. All of it is drawn once into an 8-second stereo
// loop (cheap to play), over a light wash of noise, then filtered like rain heard from inside a house.
const RAIN_SECONDS = 8;
const PATTER_PER_S = 320;   // tiny ticks per second, per ear
const PLINKS_PER_S = 5;     // clearer drops per second, per ear

export function makeRainBuffer(ctx) {
  const rate = ctx.sampleRate, length = Math.floor(rate * RAIN_SECONDS);
  const buffer = ctx.createBuffer(2, length, rate);
  for (let channel = 0; channel < 2; channel++) {
    const data = buffer.getChannelData(channel);
    let prev = 0;
    for (let i = 0; i < length; i++) {   // the wash: white noise, made brighter (a simple high-pass)
      const white = Math.random() * 2 - 1;
      data[i] = (white - prev) * 0.05; prev = white;
    }
    const drop = (at, size, tick) => {   // add one drop, wrapping round the end so the loop has no seam
      for (let k = 0; k < tick.length; k++) data[(at + k) % length] += size * tick[k];
    };
    for (let n = 0; n < PATTER_PER_S * RAIN_SECONDS; n++) {   // patter: a short burst of noise that dies away
      const size = 0.05 + 0.5 * Math.random() ** 3, decay = rate * (0.0008 + Math.random() * 0.002);
      const tick = new Float32Array(Math.floor(decay * 5)), fall = Math.exp(-1 / decay);
      for (let k = 0, env = 1; k < tick.length; k++, env *= fall) tick[k] = (Math.random() * 2 - 1) * env;
      drop(Math.floor(Math.random() * length), size, tick);
    }
    for (let n = 0; n < PLINKS_PER_S * RAIN_SECONDS; n++) {   // plink: a tiny tone that rises, like a drop in water
      const size = 0.15 + 0.35 * Math.random(), f0 = 1400 + Math.random() * 2600, decay = rate * (0.006 + Math.random() * 0.008);
      const tick = new Float32Array(Math.floor(decay * 5)), fall = Math.exp(-1 / decay);
      let phase = 0;
      for (let k = 0, env = 1; k < tick.length; k++, env *= fall) {
        phase += (2 * Math.PI * f0 * (1 + 0.8 * (k / tick.length))) / rate;
        tick[k] = Math.sin(phase) * env * Math.min(1, k / (rate * 0.0005));
      }
      drop(Math.floor(Math.random() * length), size, tick);
    }
    let power = 0;   // the same average loudness (RMS 0.25) whatever the random draw
    for (let i = 0; i < length; i++) power += data[i] * data[i];
    const scale = 0.25 / Math.sqrt(power / length);
    for (let i = 0; i < length; i++) data[i] *= scale;
  }
  return buffer;
}

function makeRain(ctx, out) {
  const source = ctx.createBufferSource(); source.buffer = makeRainBuffer(ctx); source.loop = true;
  const low = ctx.createBiquadFilter(); low.type = "lowpass"; low.frequency.value = 7000;
  const high = ctx.createBiquadFilter(); high.type = "highpass"; high.frequency.value = 500;
  const swell = ctx.createGain(); swell.gain.value = 0.85;
  const lfo = ctx.createOscillator(); lfo.frequency.value = 0.07;
  const depth = ctx.createGain(); depth.gain.value = 0.15;
  lfo.connect(depth).connect(swell.gain);
  const level = ctx.createGain(); level.gain.value = 0;
  source.connect(high).connect(low).connect(swell).connect(level).connect(out);
  source.start(); lfo.start();
  return level;
}

// A small bird: two to four quick notes that rise in pitch.
function chirp(ctx, out, level) {
  const notes = 2 + Math.floor(Math.random() * 3), base = 2600 + Math.random() * 1200;
  let t = ctx.currentTime + 0.02;
  for (let n = 0; n < notes; n++) {
    const osc = ctx.createOscillator(), gain = ctx.createGain(), length = 0.07 + Math.random() * 0.05;
    osc.type = "sine";
    osc.frequency.setValueAtTime(base * (0.9 + 0.05 * n), t);
    osc.frequency.exponentialRampToValueAtTime(base * (1.25 + 0.05 * n), t + length);
    gain.gain.setValueAtTime(0.0001, t);
    gain.gain.exponentialRampToValueAtTime(level, t + 0.015);
    gain.gain.exponentialRampToValueAtTime(0.0001, t + length);
    osc.connect(gain).connect(out);
    osc.start(t); osc.stop(t + length + 0.02);
    t += length + 0.04 + Math.random() * 0.05;
  }
}

// The "preview" sparkle: four quick, high notes going up (E, G, B, E), short and airy. It says "look", while the
// chime says "done": faster, higher, quieter and shorter, so the two are never confused.
export function sparkle(ctx, out, level) {
  [659.25, 783.99, 987.77, 1318.51].forEach((frequency, i) => {
    const t = ctx.currentTime + 0.02 + i * 0.055;
    const osc = ctx.createOscillator(), gain = ctx.createGain();
    osc.type = "sine"; osc.frequency.value = frequency;
    gain.gain.setValueAtTime(0.0001, t);
    gain.gain.exponentialRampToValueAtTime(level * (1 - 0.15 * i), t + 0.01);
    gain.gain.exponentialRampToValueAtTime(0.0001, t + 0.5);
    osc.connect(gain).connect(out);
    osc.start(t); osc.stop(t + 0.55);
  });
}

// The "done" chime: three soft bell notes going up (C, E, G), each fading out slowly.
export function chime(ctx, out, level) {
  [523.25, 659.25, 783.99].forEach((frequency, i) => {
    const t = ctx.currentTime + 0.02 + i * 0.12;
    const osc = ctx.createOscillator(), gain = ctx.createGain();
    osc.type = "sine"; osc.frequency.value = frequency;
    gain.gain.setValueAtTime(0.0001, t);
    gain.gain.exponentialRampToValueAtTime(level, t + 0.02);
    gain.gain.exponentialRampToValueAtTime(0.0001, t + 1.4);
    osc.connect(gain).connect(out);
    osc.start(t); osc.stop(t + 1.5);
  });
}

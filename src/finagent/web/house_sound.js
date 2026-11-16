// The sound of the family's home: soft rain while parts are broken, a bird now and then once the plan is healthy,
// and a short chime when a step is done. Always far below the voice, and lower still while the voice speaks
// (ducking), so every word stays clear. Made with the Web Audio API: no sound files, nothing to download or license.
//
//   const sound = create({ voice, enabled })  voice: the page's <audio> for the narration; enabled: the sound switch
//   sound.setWeather(health)   0 = a low score (rain) ... 1 = a high score (birds). Same scale as the 3D sky
//   sound.repaired()           a step was done: a soft chime and a couple of birds
//   sound.setEnabled(on)       the page's sound button (voice and background go on and off together)
//
// Browsers only let a page make sound after a tap, so nothing plays until the first one. It goes quiet while the
// tab is hidden. Plan: 02-DOCS/ftd/voz-casa-suena.md.

// Levels, as the gain of each sound (1 = full scale; the narration plays at full scale). Measured in the browser on
// 2026-11-16 against a real narration: the loudest rain is about 30 dB below the voice, and about 39 dB below
// while the voice speaks; the chime peaks about 20 dB under the voice's peaks.
const RAIN_MAX = 0.018;     // rain at the lowest score
const BIRD_LEVEL = 0.012;   // one chirp
const CHIME_LEVEL = 0.035;  // the "done" chime
const DUCKED = 0.35;        // background level while the voice speaks
const FADE_S = 1.2;         // how long the background takes to come back after the voice
const RAIN_UNTIL = 0.6;     // no rain from this health up (about a score of 61)
const BIRDS_FROM = 0.55;    // birds from this health up
const NOOP = { setWeather() {}, repaired() {}, setEnabled() {} };

export function create({ voice = null, enabled = true } = {}) {
  const Context = window.AudioContext || window.webkitAudioContext;
  if (!Context) return NOOP;

  let ctx = null, master, bed, rain, health = 0.5, on = enabled, birdTimer = 0;

  function start() {
    if (ctx) return;
    ctx = new Context();
    master = ctx.createGain(); master.gain.value = on ? 1 : 0; master.connect(ctx.destination);
    bed = ctx.createGain(); bed.gain.value = voice && !voice.paused ? DUCKED : 1; bed.connect(master);
    rain = makeRain(ctx, bed);
    applyWeather(0);
    scheduleBirds();
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
    if (!ctx) return;
    const amount = Math.max(0, (RAIN_UNTIL - health) / RAIN_UNTIL);   // 1 at the lowest score, 0 from RAIN_UNTIL
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
      chime(ctx, bed, CHIME_LEVEL);
      setTimeout(() => chirp(ctx, bed, BIRD_LEVEL), 700);
      setTimeout(() => chirp(ctx, bed, BIRD_LEVEL * 0.8), 1500);
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

// Rain: a loop of soft noise, filtered so it sounds like rain on a roof rather than hiss, with a slow swell.
function makeRain(ctx, out) {
  const seconds = 4, buffer = ctx.createBuffer(1, ctx.sampleRate * seconds, ctx.sampleRate);
  const data = buffer.getChannelData(0);
  let b0 = 0, b1 = 0, b2 = 0;
  for (let i = 0; i < data.length; i++) {   // pink-ish noise: deeper than white noise, easier on the ear
    const white = Math.random() * 2 - 1;
    b0 = 0.99765 * b0 + white * 0.099046;
    b1 = 0.963 * b1 + white * 0.2965164;
    b2 = 0.57 * b2 + white * 1.0526913;
    data[i] = (b0 + b1 + b2 + white * 0.1848) * 0.2;
  }
  const fade = Math.floor(ctx.sampleRate * 0.05);   // join the loop without a click
  for (let i = 0; i < fade; i++) data[data.length - fade + i] = data[data.length - fade + i] * (1 - i / fade) + data[i] * (i / fade);

  const source = ctx.createBufferSource(); source.buffer = buffer; source.loop = true;
  const low = ctx.createBiquadFilter(); low.type = "lowpass"; low.frequency.value = 2400;
  const high = ctx.createBiquadFilter(); high.type = "highpass"; high.frequency.value = 350;
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

// The "done" chime: three soft bell notes going up (C, E, G), each fading out slowly.
function chime(ctx, out, level) {
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

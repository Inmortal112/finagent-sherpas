// The family's home in 3D. The page loads this file only with ?house=3d (see stage_page.html); the drawn
// home (the SVG) stays as the fallback. Built from plain shapes and flat colours: no models, no image files.
//
//   const home = mount(host, { onFail, onPick })   -> throws when the browser has no WebGL
//   home.update({ states, focus, lush })
//        states: { roof: "solid" | "cracked" | "broken" | "repaired" | null (the family has no such part), ... }
//        focus:  the part being talked about (the others fade), or null
//        lush:   1 = a green garden, 0 = a dry one
//   home.dispose()
//
// It shows the same four things as paint() in the page: each part's state, the part in focus, the garden
// drying up and the glow of what was repaired. Plan and what is left out: 02-DOCS/ftd/stage-casa-3d.md.
// The camera does not move yet.
import * as THREE from "./vendor/three.module.min.js";

const INK = 0x23232e, WALL = 0xffffff, STONE = 0xbfc1d0, PIPE = 0x6586fc, JOINT = 0x4565d6, CRACK = 0x44445d;
const WOOD = 0x8a6f57, GLASS = 0xcfe0ff, GROUND = 0xe9ebf3, DRY = 0xb9a58a;
const LEAF = [new THREE.Color(0x2f9e77), new THREE.Color(0xc4b59d)];         // green, dry
const LEAF_LIGHT = [new THREE.Color(0x57bf93), new THREE.Color(0xd6cab6)];
const FADED = new THREE.Color(0xeceef5), FADE = 0.78;                        // a part out of focus goes pale
const REPAIRED_TINT = new THREE.Color(0x5a4fd0);
const GLYPH = { solid: "✓", cracked: "!", broken: "✕", repaired: "✓" };
const STATE_COLOR = { solid: "#4565d6", cracked: "#c9871f", broken: "#d6455d", repaired: "#774be5" };  // if the page has no --solid…

const TARGET = new THREE.Vector3(0, 1.6, 0);                  // the camera looks at the middle of the home
const FROM = new THREE.Vector3(0.55, 0.32, 0.77).normalize(); // from the front, a little to the right and above
const HALF_WIDTH = 5.4, HALF_HEIGHT = 3.1, DEPTH = 2.5;       // the room the home and its garden need around TARGET
const FOV = 32;

function mesh(geometry, color, x = 0, y = 0, z = 0) {
  const m = new THREE.Mesh(geometry, new THREE.MeshLambertMaterial({ color, flatShading: true }));
  m.position.set(x, y, z);
  m.userData.color = new THREE.Color(color);   // its own colour, before fading or drying
  return m;
}
const box = (w, h, d, color, x, y, z) => mesh(new THREE.BoxGeometry(w, h, d), color, x, y, z);
const ball = (r, color, x, y, z) => mesh(new THREE.IcosahedronGeometry(r, 1), color, x, y, z);
// A pipe, a trunk or a stroke from one point to another.
function rod(r, color, from, to) {
  const a = new THREE.Vector3(...from), b = new THREE.Vector3(...to);
  const m = mesh(new THREE.CylinderGeometry(r, r, a.distanceTo(b), 8), color);
  m.position.copy(a).add(b).multiplyScalar(0.5);
  m.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), b.clone().sub(a).normalize());
  return m;
}
// A crack: a broken line through these points.
const crack = (points, color = CRACK, r = 0.028) => points.slice(1).map((p, i) => rod(r, color, points[i], p));
function group(name, ...children) {
  const g = new THREE.Group();
  g.name = name;
  g.add(...children.flat());
  return g;
}
// A point on the right-hand slope of the roof: t goes from the eaves (0) to the ridge (1), z along the home.
const onSlope = (t, z, lift = 0.03) => [2.5 - 2.5 * t + lift * 0.56, 2.8 + 1.7 * t + lift * 0.83, z];

// Every part: its body, what shows when it is cracked ("crk"), what is added when it is broken ("dmg"),
// where its mark goes ("pin") and where its glow sits ("halo": centre and size).
function foundations() {
  const z = 1.77;
  return {
    body: [box(4.5, 0.4, 3.5, STONE, 0, 0.2, 0)],
    crk: crack([[-0.9, 0.4, z], [-0.8, 0.27, z], [-0.92, 0.16, z], [-0.8, 0.0, z]]),
    dmg: [box(0.62, 0.3, 0.05, CRACK, 1.0, 0.24, z - 0.01), ...crack([[-1.9, 0.02, z], [-1.76, 0.18, z], [-1.86, 0.28, z], [-1.74, 0.4, z]]),
      ...crack([[2.27, 0.4, 0.9], [2.27, 0.25, 0.8], [2.27, 0.15, 0.95], [2.27, 0.0, 0.85]])],
    pin: [-0.2, 0.2, 1.85], halo: [0, 0.2, 0, 7.4, 2.2],
  };
}

function walls() {
  const z = 1.52;
  const win = (x) => [box(0.92, 0.82, 0.04, INK, x, 1.8, 1.5), box(0.8, 0.7, 0.06, GLASS, x, 1.8, 1.51)];
  return {
    body: [box(4, 2.4, 3, WALL, 0, 1.6, 0), box(0.7, 1.25, 0.06, INK, 0, 1.025, 1.51), ball(0.04, 0xafbff8, 0.22, 1.0, 1.56),
      ...win(-1.2), ...win(1.2)],
    crk: [...crack([[1.85, 2.75, z], [1.7, 2.4, z], [1.82, 2.2, z]]), ...crack([[1.75, 1.3, z], [1.88, 1.05, z], [1.76, 0.8, z], [1.9, 0.45, z]])],
    dmg: [...crack([[-1.85, 1.35, z], [-1.62, 1.15, z], [-1.74, 0.9, z], [-1.55, 0.5, z]], CRACK, 0.034),
      box(0.62, 0.2, 0.04, 0xe9c9bd, -0.62, 2.62, z - 0.01), box(0.32, 0.2, 0.04, 0xe9c9bd, -0.77, 2.42, z - 0.01),
      ...crack([[2.02, 2.6, -0.4], [2.02, 2.2, -0.55], [2.02, 1.9, -0.4], [2.02, 1.5, -0.6]], CRACK, 0.034)],
    pin: [0, 2.38, 1.6], halo: [0, 1.6, 0, 7, 4.6],
  };
}

function roof() {
  const shape = new THREE.Shape();
  shape.moveTo(-2.5, 0); shape.lineTo(2.5, 0); shape.lineTo(0, 1.7); shape.closePath();
  const gable = mesh(new THREE.ExtrudeGeometry(shape, { depth: 3.6, bevelEnabled: false }), INK, 0, 2.8, -1.8);
  const hole = box(0.95, 0.04, 0.9, 0xf6fbff, ...onSlope(0.52, 0.55, 0.02));   // the roof is open to the sky here
  hole.rotation.z = Math.atan2(1.7, -2.5) + Math.PI;                          // lying on the slope
  const z = 1.82;
  return {
    body: [gable, box(0.42, 1.1, 0.42, 0x44445d, 1.25, 3.75, -0.3)],
    crk: [...crack([[-0.95, 2.95, z], [-0.7, 3.3, z], [-0.85, 3.5, z], [-0.55, 3.85, z]], 0xfcfcfc),
      ...crack([onSlope(0.1, -0.6), onSlope(0.3, -0.75), onSlope(0.45, -0.55), onSlope(0.7, -0.7)], 0xfcfcfc)],
    dmg: [hole, rod(0.035, WOOD, onSlope(0.36, 0.35, 0.06), onSlope(0.68, 0.35, 0.06)), rod(0.035, WOOD, onSlope(0.36, 0.75, 0.06), onSlope(0.68, 0.75, 0.06)),
      ...crack([[0.45, 2.95, z], [0.7, 3.25, z], [0.55, 3.45, z]], 0xfcfcfc)],
    pin: [0, 3.55, 1.9], halo: [0, 3.5, 0, 7.6, 3.6],
  };
}

function plumbing() {
  const x = 2.28, z = 0.5, tap = z + 0.32;   // on the right-hand wall, where the camera sees it
  const puddle = mesh(new THREE.CircleGeometry(0.42, 20), PIPE, x + 0.1, 0.012, tap + 0.1);
  puddle.rotation.x = -Math.PI / 2;
  return {
    body: [rod(0.07, PIPE, [x, 0.8, z], [x, 2.4, z]), rod(0.07, PIPE, [2, 0.8, z], [x, 0.8, z]), rod(0.07, PIPE, [2, 2.4, z], [x, 2.4, z]),
      rod(0.055, PIPE, [x, 1.35, z], [x, 1.35, tap]), rod(0.055, PIPE, [x, 1.35, tap], [x, 1.2, tap]),
      ball(0.11, JOINT, x, 0.8, z), ball(0.11, JOINT, x, 2.4, z)],
    crk: [ball(0.06, PIPE, x, 1.02, tap)],                                       // one drop under the tap
    dmg: [ball(0.065, PIPE, x, 0.74, tap), ball(0.06, PIPE, x + 0.1, 1.72, z + 0.02), ball(0.055, PIPE, x + 0.12, 1.5, z + 0.03), puddle,
      rod(0.03, INK, [x + 0.09, 1.78, z - 0.11], [x + 0.09, 1.98, z + 0.11]), rod(0.03, INK, [x + 0.09, 1.98, z - 0.11], [x + 0.09, 1.78, z + 0.11])],
    pin: [2.55, 2.15, 0.75], halo: [2.3, 1.5, 0.6, 2.8, 3.6],
  };
}

function garden() {
  const leaf = (r, x, y, z, light) => { const m = ball(r, 0, x, y, z); m.userData.leaf = light ? LEAF_LIGHT : LEAF; return m; };
  const flower = (x, z, h, color) => group("flower", rod(0.02, 0x57bf93, [x, 0, z], [x, h, z]), ball(0.09, color, x, h, z));
  // The tree and the bush shrink towards the ground as the garden dries, like the drawn ones.
  const tree = group("canopy", leaf(0.95, 0, 0.65, 0), leaf(0.6, -0.6, 0.15, 0.2, true), leaf(0.62, 0.6, 0.2, -0.1, true));
  tree.position.set(-3.6, 1.7, 0.5);
  const bush = group("canopy", leaf(0.45, 0, 0.38, 0), leaf(0.35, 0.5, 0.3, 0.2, true), leaf(0.22, 0.9, 0.2, 0.35));
  bush.position.set(3.5, 0, 1.4);
  const bloom = group("bloom", flower(-2.7, 2.0, 0.42, 0xdf7afe), flower(-2.4, 2.2, 0.32, 0x948df7), flower(3.2, 2.1, 0.3, 0xdf7afe));
  const y = 0.02;
  return {
    body: [rod(0.13, WOOD, [-3.6, 0, 0.5], [-3.6, 1.75, 0.5]), tree, bush, bloom],
    crk: [...crack([[-4.4, y, 1.6], [-4.1, y, 1.9], [-4.2, y, 2.2]], DRY), ...crack([[-3.2, y, 1.7], [-3.0, y, 2.0], [-3.2, y, 2.3]], DRY)],
    dmg: [rod(0.045, DRY, [-3.6, 1.5, 0.5], [-4.25, 2.0, 0.75]), rod(0.045, DRY, [-3.6, 1.6, 0.5], [-3.0, 2.15, 0.6]), rod(0.04, DRY, [-3.6, 1.7, 0.5], [-3.7, 2.5, 0.9]),
      ...crack([[3.0, y, 2.2], [3.3, y, 2.45], [3.2, y, 2.7]], DRY)],
    pin: [-3.6, 2.5, 1.5], halo: [-3.6, 2.0, 0.5, 4.4, 4.4],
    canopies: [tree, bush], bloom,
  };
}

// A soft round glow and the round marks, drawn here on a small canvas: no image is downloaded.
function drawn(size, paint) {
  const canvas = document.createElement("canvas");
  canvas.width = canvas.height = size;
  paint(canvas.getContext("2d"), size);
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  return texture;
}
const glowTexture = () => drawn(128, (g, s) => {
  const fill = g.createRadialGradient(s / 2, s / 2, 0, s / 2, s / 2, s / 2);
  fill.addColorStop(0, "rgba(120,110,247,.85)"); fill.addColorStop(0.55, "rgba(105,125,250,.4)"); fill.addColorStop(1, "rgba(105,125,250,0)");
  g.fillStyle = fill; g.fillRect(0, 0, s, s);
});
const pinTexture = (color, glyph) => drawn(96, (g, s) => {
  g.fillStyle = "#fff"; g.beginPath(); g.arc(s / 2, s / 2, s / 2 - 2, 0, 7); g.fill();      // a white rim, to stand out on any part
  g.fillStyle = color; g.beginPath(); g.arc(s / 2, s / 2, s / 2 - 8, 0, 7); g.fill();
  g.fillStyle = "#fff"; g.font = `600 ${s * 0.5}px system-ui, sans-serif`; g.textAlign = "center"; g.textBaseline = "middle";
  g.fillText(glyph, s / 2, s / 2 + 2);
});

export function mount(host, { onFail = () => {}, onPick = () => {} } = {}) {
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });   // throws without WebGL
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));           // sharper than 2x only costs battery
  const canvas = renderer.domElement;
  canvas.setAttribute("role", "img");
  canvas.setAttribute("aria-label", "Your plan drawn as a home");
  canvas.style.cursor = "pointer";
  host.appendChild(canvas);

  const scene = new THREE.Scene();
  scene.add(new THREE.HemisphereLight(0xffffff, 0xc9cbd8, 1.9));
  const sun = new THREE.DirectionalLight(0xffffff, 1.6);
  sun.position.set(4, 8, 6);
  scene.add(sun);
  const ground = mesh(new THREE.CircleGeometry(5, 48), GROUND);
  ground.rotation.x = -Math.PI / 2;
  scene.add(ground);

  // The page's own state colours, so the marks match the legend.
  const css = getComputedStyle(host);
  const pins = {};
  for (const state in GLYPH) pins[state] = pinTexture(css.getPropertyValue("--" + state).trim() || STATE_COLOR[state], GLYPH[state]);
  const glow = glowTexture();

  const parts = {};
  for (const [name, make] of Object.entries({ foundations, walls, roof, plumbing, garden })) {
    const made = make();
    const crk = group("crk", made.crk), dmg = group("dmg", made.dmg);
    const halo = new THREE.Sprite(new THREE.SpriteMaterial({ map: glow, transparent: true, depthWrite: false }));
    halo.position.set(made.halo[0], made.halo[1], made.halo[2]);
    halo.scale.set(made.halo[3], made.halo[4], 1);
    const pin = new THREE.Sprite(new THREE.SpriteMaterial({ map: pins.solid, transparent: true, depthTest: false }));
    pin.position.set(...made.pin);
    pin.renderOrder = 10;   // on top of the home, like a label
    const whole = group(name, made.body, crk, dmg, halo, pin);
    scene.add(whole);
    parts[name] = { whole, crk, dmg, halo, pin, canopies: made.canopies || [], bloom: made.bloom || null };
  }

  const camera = new THREE.PerspectiveCamera(FOV, 1, 0.1, 100);
  let alive = true, queued = 0;

  // Drawn only when something changes: a home that stands still costs no battery.
  function draw() {
    if (!alive || queued) return;
    queued = requestAnimationFrame(() => { queued = 0; if (alive) renderer.render(scene, camera); });
  }
  function resize() {
    const w = host.clientWidth, h = host.clientHeight;
    if (!w || !h) return;
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    // As close as the home allows: its height decides on a wide screen, its width on a phone held upright.
    const slope = Math.tan(THREE.MathUtils.degToRad(FOV) / 2);
    const distance = Math.max(HALF_HEIGHT / slope, HALF_WIDTH / (slope * camera.aspect)) + DEPTH;
    camera.position.copy(TARGET).addScaledVector(FROM, distance);
    camera.lookAt(TARGET);
    camera.updateProjectionMatrix();
    draw();
  }
  const watcher = new ResizeObserver(resize);
  watcher.observe(host);
  resize();

  function update({ states = {}, focus = null, lush = 1 } = {}) {
    const green = Math.min(1, Math.max(0, lush));
    for (const name in parts) {
      const part = parts[name], state = states[name];
      part.whole.visible = Boolean(state);
      if (!state) continue;
      const faded = Boolean(focus) && focus !== name;
      part.crk.visible = state === "cracked" || state === "broken";
      part.dmg.visible = state === "broken";
      part.halo.visible = state === "repaired" && !faded;
      part.pin.material.map = pins[state] || pins.solid;
      part.pin.material.opacity = faded ? 0.35 : 1;
      const size = focus === name ? 0.78 : 0.62;
      part.pin.scale.set(size, size, 1);
      part.canopies.forEach((canopy) => canopy.scale.setScalar(0.72 + 0.28 * green));
      if (part.bloom) part.bloom.visible = green > 0.3;
      part.whole.traverse((node) => {
        if (!node.isMesh) return;
        const color = node.material.color;
        if (node.userData.leaf) color.copy(node.userData.leaf[1]).lerp(node.userData.leaf[0], green);
        else color.copy(node.userData.color);
        if (state === "repaired") color.lerp(REPAIRED_TINT, 0.1);
        if (faded) color.lerp(FADED, FADE);
      });
    }
    draw();
  }

  // A tap on a part of the home goes to that part, like on the drawn one.
  const ray = new THREE.Raycaster(), point = new THREE.Vector2();
  canvas.addEventListener("click", (event) => {
    const box = canvas.getBoundingClientRect();
    point.set(((event.clientX - box.left) / box.width) * 2 - 1, -((event.clientY - box.top) / box.height) * 2 + 1);
    ray.setFromCamera(point, camera);
    const shown = Object.values(parts).filter((part) => part.whole.visible).map((part) => part.whole);
    for (const hit of ray.intersectObjects(shown, true)) {
      let node = hit.object;
      while (node && !parts[node.name]) node = node.parent;
      if (node) { onPick(node.name); return; }
    }
  });

  function dispose() {
    if (!alive) return;
    alive = false;
    cancelAnimationFrame(queued);
    watcher.disconnect();
    scene.traverse((node) => { if (node.isMesh || node.isSprite) { node.geometry.dispose(); node.material.dispose(); } });
    Object.values(pins).forEach((texture) => texture.dispose());
    glow.dispose();
    renderer.dispose();
    canvas.remove();
  }
  // The phone took the graphics memory back (another app, a locked screen): the drawn home takes over.
  canvas.addEventListener("webglcontextlost", (event) => { event.preventDefault(); if (alive) onFail(); });

  return { update, dispose };
}

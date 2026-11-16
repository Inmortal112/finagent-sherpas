// The family's home in 3D. The page loads this file only with ?house=3d (see stage_page.html); the drawn
// home (the SVG) stays as the fallback. Built from plain shapes, a painted sky and drifting clouds: no models,
// no image files.
//
//   const home = mount(host, { onFail, onPick })   -> throws when the browser has no WebGL
//   home.update({ states, focus, lush, health })
//        states: { roof: "solid" | "cracked" | "broken" | "repaired" | null (the family has no such part), ... }
//        focus:  the part being talked about (the others fade), or null
//        lush:   1 = a green garden, 0 = a dry one
//        health: 0 = a grey, rainy day (a low score) ... 1 = a golden evening (a high score)
//   home.setFrame({ x, y, w, h })   the box of the canvas the home must sit in (the page's scene), in pixels
//   home.setIntro(p)                 0 = high above the clouds, 1 = at the home: the hero's scroll drives it
//   home.dispose()
//
// What it shows: each part's state, the part in focus, the garden drying up, the glow of what was repaired, and
// the weather of the plan. A part that becomes repaired heals in front of the family: its cracks close up and
// sparks rise. The sky follows the score, so doing the steps turns rain into a golden evening.
// Plans: 02-DOCS/ftd/stage-casa-3d.md and 02-DOCS/ftd/stage-casa-que-mejora.md.
import * as THREE from "./vendor/three.module.min.js";

const INK = 0x23232e, WALL = 0xffffff, STONE = 0xbfc1d0, PIPE = 0x6586fc, JOINT = 0x4565d6, CRACK = 0x44445d;
const WOOD = 0x8a6f57, GLASS = 0xcfe0ff, YARD = 0xe9ebf3, DRY = 0xb9a58a;
const LEAF = [new THREE.Color(0x2f9e77), new THREE.Color(0xc4b59d)];         // green, dry
const LEAF_LIGHT = [new THREE.Color(0x57bf93), new THREE.Color(0xd6cab6)];
const FADED = new THREE.Color(0xeceef5), FADE = 0.6;                         // a part out of focus goes pale
const REPAIRED_TINT = new THREE.Color(0x5a4fd0);
const LAMP = new THREE.Color(0xffc977), WHITE = new THREE.Color(0xffffff);                                      // the windows at night
const GLYPH = { solid: "✓", cracked: "!", broken: "✕", repaired: "✓" };
const STATE_COLOR = { solid: "#4565d6", cracked: "#c9871f", broken: "#d6455d", repaired: "#774be5" };  // if the page has no --solid…

// The weather of the plan: a grey, rainy day; a clear day; a golden evening. health 0 → 0.5 → 1.
const WEATHER = [
  { top: 0x353b4b, mid: 0x5d6373, horizon: 0x8d919c, sun: 0xd7dbe4, sunPower: 0.05, cloud: 0x868a96, shade: 0x5a5e6a,
    light: 0xc4ccdc, lightPower: 0.9, sky: 0x9aa3b6, ground: 0x5d6168, grass: 0x7d866f, hills: 0x5f6a62, exposure: 0.92 },
  { top: 0x2d5fc0, mid: 0x7aa2de, horizon: 0xd8e6f6, sun: 0xfff3dc, sunPower: 0.55, cloud: 0xffffff, shade: 0xc6d2e6,
    light: 0xfff2de, lightPower: 1.7, sky: 0xd6e4ff, ground: 0x93a07f, grass: 0x78ab62, hills: 0x6b9a6f, exposure: 1.0 },
  { top: 0x1f2e66, mid: 0x8a6fb0, horizon: 0xffae73, sun: 0xffdca0, sunPower: 1.0, cloud: 0xffdcc8, shade: 0xc98694,
    light: 0xffcf9a, lightPower: 1.9, sky: 0xffd6c0, ground: 0x8b7a6c, grass: 0x84a85c, hills: 0x6d7a68, exposure: 1.05 },
].map((w) => Object.fromEntries(Object.entries(w).map(([k, v]) => [k, typeof v === "number" && k !== "sunPower" && k !== "lightPower" && k !== "exposure" ? new THREE.Color(v) : v])));
const SUN_DIR = new THREE.Vector3(-0.32, 0.075, -1).normalize();   // low, behind the home: the camera looks into it

// Where the camera stands for the whole home and for each part: the point it looks at ("at"), the side it
// looks from ("from": right, up, front) and the room that must fit on the screen around that point.
const VIEWS = {
  home: { at: [0, 1.6, 0], from: [0.55, 0.3, 0.78], halfWidth: 5.6, halfHeight: 3.3, depth: 2.5 },
  roof: { at: [0.2, 3.1, 0], from: [0.6, 0.5, 0.72], halfWidth: 3.8, halfHeight: 2.5, depth: 2.2 },
  walls: { at: [0, 1.6, 0.6], from: [0.3, 0.16, 0.94], halfWidth: 3.2, halfHeight: 2.1, depth: 2.2 },
  plumbing: { at: [1.9, 1.5, 0.7], from: [0.86, 0.2, 0.47], halfWidth: 2.3, halfHeight: 1.9, depth: 1.8 },
  foundations: { at: [0, 0.7, 1.0], from: [0.36, 0.14, 0.92], halfWidth: 3.3, halfHeight: 1.7, depth: 2.2 },
  garden: { at: [-2.5, 1.5, 0.8], from: [-0.12, 0.26, 0.96], halfWidth: 3.0, halfHeight: 2.2, depth: 2.0 },
};
// High above the clouds, looking at the sun: where the visit starts (setIntro(0)).
const INTRO = { position: new THREE.Vector3(10, 34, 46), at: new THREE.Vector3(-26, 22, -120) };
const FOV = 32;
const GLIDE_MS = 900;        // short and slow: nobody should feel the room move
const HEAL_MS = 1400;
const SLOW_FRAME_MS = 45;    // a glide that averages worse than this (about 22 frames a second) is a jerky one
const HOPELESS_FRAME_MS = 150;

// A small seeded random, so the clouds and trees are the same on every visit.
let seed = 7;
const rand = () => ((seed = (seed * 16807) % 2147483647) - 1) / 2147483646;
const between = (a, b) => a + (b - a) * rand();

function mesh(geometry, color, x = 0, y = 0, z = 0) {
  const m = new THREE.Mesh(geometry, new THREE.MeshLambertMaterial({ color, flatShading: true }));
  m.position.set(x, y, z);
  m.castShadow = m.receiveShadow = true;
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
  const glass = [];
  const win = (x) => { const pane = box(0.8, 0.7, 0.06, GLASS, x, 1.8, 1.51); glass.push(pane); return [box(0.92, 0.82, 0.04, INK, x, 1.8, 1.5), pane]; };
  return {
    body: [box(4, 2.4, 3, WALL, 0, 1.6, 0), box(0.7, 1.25, 0.06, INK, 0, 1.025, 1.51), ball(0.04, 0xafbff8, 0.22, 1.0, 1.56),
      ...win(-1.2), ...win(1.2)],
    crk: [...crack([[1.85, 2.75, z], [1.7, 2.4, z], [1.82, 2.2, z]]), ...crack([[1.75, 1.3, z], [1.88, 1.05, z], [1.76, 0.8, z], [1.9, 0.45, z]])],
    dmg: [...crack([[-1.85, 1.35, z], [-1.62, 1.15, z], [-1.74, 0.9, z], [-1.55, 0.5, z]], CRACK, 0.034),
      box(0.62, 0.2, 0.04, 0xe9c9bd, -0.62, 2.62, z - 0.01), box(0.32, 0.2, 0.04, 0xe9c9bd, -0.77, 2.42, z - 0.01),
      ...crack([[2.02, 2.6, -0.4], [2.02, 2.2, -0.55], [2.02, 1.9, -0.4], [2.02, 1.5, -0.6]], CRACK, 0.034)],
    pin: [0, 2.38, 1.6], halo: [0, 1.6, 0, 7, 4.6], glass,
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

// Soft round shapes drawn here on a small canvas: no image is downloaded.
function drawn(size, paint) {
  const canvas = document.createElement("canvas");
  canvas.width = canvas.height = size;
  paint(canvas.getContext("2d"), size);
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  return texture;
}
const glowTexture = (inner = "rgba(120,110,247,.85)", middle = "rgba(105,125,250,.4)") => drawn(128, (g, s) => {
  const fill = g.createRadialGradient(s / 2, s / 2, 0, s / 2, s / 2, s / 2);
  fill.addColorStop(0, inner); fill.addColorStop(0.55, middle); fill.addColorStop(1, "rgba(105,125,250,0)");
  g.fillStyle = fill; g.fillRect(0, 0, s, s);
});
const pinTexture = (color, glyph) => drawn(96, (g, s) => {
  g.fillStyle = "#fff"; g.beginPath(); g.arc(s / 2, s / 2, s / 2 - 2, 0, 7); g.fill();      // a white rim, to stand out on any part
  g.fillStyle = color; g.beginPath(); g.arc(s / 2, s / 2, s / 2 - 8, 0, 7); g.fill();
  g.fillStyle = "#fff"; g.font = `600 ${s * 0.5}px system-ui, sans-serif`; g.textAlign = "center"; g.textBaseline = "middle";
  g.fillText(glyph, s / 2, s / 2 + 2);
});
// A cloud: a dozen soft white puffs, flatter at the bottom.
const cloudTexture = () => drawn(256, (g, s) => {
  for (let i = 0; i < 14; i++) {
    const x = s * between(0.22, 0.78), y = s * between(0.4, 0.62) - (i % 3) * s * 0.05, r = s * between(0.12, 0.24);
    const puff = g.createRadialGradient(x, y, 0, x, y, r);
    puff.addColorStop(0, "rgba(255,255,255,.55)"); puff.addColorStop(0.6, "rgba(255,255,255,.22)"); puff.addColorStop(1, "rgba(255,255,255,0)");
    g.fillStyle = puff; g.fillRect(0, 0, s, s);
  }
});

// The sky: a dome painted from the horizon up, with the sun's glow. It always stands around the camera.
function skyDome() {
  const uniforms = {
    top: { value: new THREE.Color() }, mid: { value: new THREE.Color() }, horizon: { value: new THREE.Color() },
    sunColor: { value: new THREE.Color() }, sunPower: { value: 1 }, sunDir: { value: SUN_DIR.clone() },
  };
  const material = new THREE.ShaderMaterial({
    uniforms, side: THREE.BackSide, depthWrite: false, fog: false,
    vertexShader: "varying vec3 vDir; void main() { vDir = position; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }",
    fragmentShader: `uniform vec3 top; uniform vec3 mid; uniform vec3 horizon; uniform vec3 sunColor; uniform float sunPower; uniform vec3 sunDir;
      varying vec3 vDir;
      void main() {
        vec3 d = normalize(vDir);
        float y = max(d.y, 0.0);
        vec3 c = mix(horizon, mid, smoothstep(0.0, 0.22, y));
        c = mix(c, top, smoothstep(0.22, 0.85, y));
        float s = max(dot(d, sunDir), 0.0);
        c += sunColor * sunPower * (pow(s, 900.0) * 2.2 + pow(s, 40.0) * 0.45 + pow(s, 6.0) * 0.22);
        gl_FragColor = vec4(c, 1.0);
        #include <tonemapping_fragment>
        #include <colorspace_fragment>
      }`,
  });
  const dome = new THREE.Mesh(new THREE.SphereGeometry(400, 40, 20), material);
  dome.renderOrder = -1;
  return { dome, uniforms };
}

export function mount(host, { onFail = () => {}, onPick = () => {} } = {}) {
  seed = 7;
  const renderer = new THREE.WebGLRenderer({ antialias: true });   // throws without WebGL
  let ratio = Math.min(window.devicePixelRatio || 1, 1.75);       // sharper only costs battery on a full screen
  renderer.setPixelRatio(ratio);
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  const canvas = renderer.domElement;
  canvas.setAttribute("role", "img");
  canvas.setAttribute("aria-label", "Your plan drawn as a home");
  canvas.style.cursor = "pointer";
  host.appendChild(canvas);

  const scene = new THREE.Scene();
  scene.fog = new THREE.Fog(0xffffff, 40, 190);
  const sky = skyDome();
  scene.add(sky.dome);
  const hemi = new THREE.HemisphereLight(0xffffff, 0xc9cbd8, 1.6);
  scene.add(hemi);
  const sun = new THREE.DirectionalLight(0xffffff, 1.6);   // the key light, from the camera's side so the front reads
  sun.position.set(6, 11, 8);
  sun.castShadow = true;
  sun.shadow.mapSize.set(1024, 1024);
  Object.assign(sun.shadow.camera, { left: -8, right: 8, top: 8, bottom: -8, near: 1, far: 40 });
  sun.shadow.bias = -0.0006;
  sun.shadow.normalBias = 0.02;
  scene.add(sun);
  const rim = new THREE.DirectionalLight(0xffffff, 0.5);   // the evening light from behind, along the edges
  rim.position.copy(SUN_DIR).multiplyScalar(30);
  scene.add(rim);

  // The land: a wide field, the yard the home stands on, a path to the door, hills and trees far off.
  const field = mesh(new THREE.CircleGeometry(220, 64), 0x78ab62);
  field.rotation.x = -Math.PI / 2; field.position.y = -0.02; field.castShadow = false;
  const yard = mesh(new THREE.CircleGeometry(5.6, 48), YARD);
  yard.rotation.x = -Math.PI / 2; yard.position.y = 0.0; yard.castShadow = false;
  const path = box(0.9, 0.02, 3.2, 0xd9dbe5, 0, 0.005, 3.3);
  path.castShadow = false;
  scene.add(field, yard, path);
  const scenery = [];   // hills and far trees: they take the weather's colours
  for (let i = 0; i < 12; i++) {
    const angle = Math.PI * (0.7 + 1.6 * (i / 11)) + between(-0.1, 0.1), far = between(60, 120);
    const hill = mesh(new THREE.IcosahedronGeometry(1, 2), 0x6b9a6f, Math.cos(angle) * far, -2, Math.sin(angle) * far - 30);
    hill.scale.set(between(18, 34), between(5, 12), between(14, 24));
    hill.castShadow = false;
    hill.userData.tone = "hills";
    scenery.push(hill);
  }
  for (let i = 0; i < 26; i++) {
    const angle = between(0, Math.PI * 2), far = between(9, 26);
    const x = Math.cos(angle) * far, z = Math.sin(angle) * far - 4;
    if (z > 2) continue;                                           // the cameras stand in front: keep that side open
    const h = between(1.4, 2.6);
    const top = mesh(new THREE.ConeGeometry(h * 0.42, h, 7), 0x3f7f5d, x, h * 0.5 + 0.5, z);
    top.userData.tone = "trees";
    scenery.push(top, mesh(new THREE.CylinderGeometry(0.08, 0.1, 0.6, 6), WOOD, x, 0.3, z));
  }
  scene.add(...scenery);

  // The clouds: a deck the camera comes down through at the start, and a bank along the horizon.
  const puff = cloudTexture();
  const clouds = [];
  const addCloud = (x, y, z, size, drift) => {
    const material = new THREE.SpriteMaterial({ map: puff, transparent: true, depthWrite: false, fog: false });
    const sprite = new THREE.Sprite(material);
    sprite.position.set(x, y, z);
    sprite.scale.set(size, size * 0.55, 1);
    sprite.userData = { drift, shade: rand(), base: between(0.75, 1) };
    clouds.push(sprite);
    scene.add(sprite);
  };
  for (let i = 0; i < 26; i++) addCloud(between(-50, 50), between(13, 24), between(-60, 40), between(14, 26), between(0.25, 0.6));
  for (let i = 0; i < 16; i++) { const a = between(-2.6, -0.5); addCloud(Math.cos(a) * 150, between(6, 24), Math.sin(a) * 150, between(45, 80), between(0.4, 0.9)); }

  // Rain: short streaks falling around the home. It only shows on a low score.
  const DROPS = 700;
  const rainPositions = new Float32Array(DROPS * 6);
  for (let i = 0; i < DROPS; i++) {
    const x = between(-14, 14), y = between(0, 16), z = between(-10, 14);
    rainPositions.set([x, y, z, x - 0.04, y - 0.38, z], i * 6);
  }
  const rainGeometry = new THREE.BufferGeometry();
  rainGeometry.setAttribute("position", new THREE.BufferAttribute(rainPositions, 3));
  const rain = new THREE.LineSegments(rainGeometry, new THREE.LineBasicMaterial({ color: 0xc3cbdb, transparent: true, opacity: 0 }));
  rain.frustumCulled = false;
  scene.add(rain);

  // Sparks that rise from a part as it heals.
  const SPARKS = 160;
  const sparkPositions = new Float32Array(SPARKS * 3), sparkColors = new Float32Array(SPARKS * 3);
  const sparkLife = new Float32Array(SPARKS), sparkSpeed = new Float32Array(SPARKS * 3);
  const sparkGeometry = new THREE.BufferGeometry();
  sparkGeometry.setAttribute("position", new THREE.BufferAttribute(sparkPositions, 3));
  sparkGeometry.setAttribute("color", new THREE.BufferAttribute(sparkColors, 3));
  const sparkTexture = glowTexture("rgba(255,255,255,1)", "rgba(255,240,210,.5)");
  const sparks = new THREE.Points(sparkGeometry, new THREE.PointsMaterial({ size: 0.32, map: sparkTexture, vertexColors: true, transparent: true,
    depthWrite: false, blending: THREE.AdditiveBlending, sizeAttenuation: true }));
  sparks.frustumCulled = false;
  scene.add(sparks);
  let nextSpark = 0, sparking = 0;
  const SPARK_TONES = [new THREE.Color(0xffd27a), new THREE.Color(0xc9b8ff), new THREE.Color(0xffffff), new THREE.Color(0xdf7afe)];
  function burst(at, size) {
    for (let n = 0; n < 70; n++) {
      const i = nextSpark; nextSpark = (nextSpark + 1) % SPARKS;
      sparkPositions.set([at.x + between(-size, size) * 0.5, at.y + between(-0.6, 0.6), at.z + between(-0.4, 0.9)], i * 3);
      sparkSpeed.set([between(-0.6, 0.6), between(1.2, 3.2), between(-0.3, 0.8)], i * 3);
      const tone = SPARK_TONES[n % SPARK_TONES.length];
      sparkColors.set([tone.r, tone.g, tone.b], i * 3);
      sparkLife[i] = between(0.9, 1.6);
    }
    sparking = 1.8;
  }

  // The page's own state colours, so the marks match the legend.
  const css = getComputedStyle(host);
  const pins = {};
  for (const state in GLYPH) pins[state] = pinTexture(css.getPropertyValue("--" + state).trim() || STATE_COLOR[state], GLYPH[state]);
  const glow = glowTexture();

  const parts = {};
  const windows = [];
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
    windows.push(...(made.glass || []));
    parts[name] = { whole, crk, dmg, halo, pin, canopies: made.canopies || [], bloom: made.bloom || null,
      size: made.halo[3], state: null, heal: null };
  }

  const camera = new THREE.PerspectiveCamera(FOV, 1, 0.1, 900);
  let alive = true, queued = 0, last = 0, clock = 0;
  let view = "home", glide = null, slowGlides = 0, still = false, placed = false;
  let intro = 1;
  let frameBox = null;   // the scene's box on the canvas; null = the whole canvas
  let width = 1, height = 1;
  let health = -1, healthWanted = 0.5, rainAmount = 0;
  let perf = { spent: 0, frames: 0, lowered: false };

  // The box the home sits in, in canvas pixels.
  const room = () => frameBox && frameBox.w > 10 && frameBox.h > 10 ? frameBox : { x: 0, y: 0, w: width, h: height };

  // Where the camera must be to show that view inside the scene's box.
  function pose(name) {
    const v = VIEWS[name] || VIEWS.home, r = room();
    const slope = Math.tan(THREE.MathUtils.degToRad(FOV) / 2);
    // As close as the view allows: its height decides on a wide box, its width on a narrow one.
    return {
      at: new THREE.Vector3(...v.at), from: new THREE.Vector3(...v.from).normalize(),
      distance: Math.max((v.halfHeight * height) / (slope * r.h), (v.halfWidth * height) / (slope * r.w)) + v.depth,
    };
  }
  let now = pose(view);

  // The lens is shifted so the middle of the picture is the middle of the scene's box, not of the canvas.
  function project() {
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    const r = room(), e = camera.projectionMatrix.elements;
    const shift = 1 - intro * intro * (3 - 2 * intro);   // high in the sky the picture is centred on the whole screen
    e[8] = -(((r.x + r.w / 2) / width) * 2 - 1) * (1 - shift);
    e[9] = -(1 - ((r.y + r.h / 2) / height) * 2) * (1 - shift);
    camera.projectionMatrixInverse.copy(camera.projectionMatrix).invert();
  }

  const lookAt = new THREE.Vector3(), position = new THREE.Vector3();
  function place() {
    // A slow sway, so the picture breathes like a film. Small enough not to be felt.
    const sway = Math.sin(clock * 0.21) * 0.025, from = now.from.clone().applyAxisAngle(new THREE.Vector3(0, 1, 0), sway);
    position.copy(now.at).addScaledVector(from, now.distance);
    lookAt.copy(now.at);
    if (intro < 1) {
      const t = intro * intro * (3 - 2 * intro);
      position.lerpVectors(INTRO.position, position, t);
      lookAt.lerpVectors(INTRO.at, lookAt, Math.pow(t, 0.7));
    }
    camera.position.copy(position);
    camera.lookAt(lookAt);
    sky.dome.position.copy(position);
  }

  // The weather for this health: the sky, the light, the land, the clouds and the rain.
  const mixed = {};
  function weather(h) {
    const [a, b, t] = h < 0.5 ? [WEATHER[0], WEATHER[1], h / 0.5] : [WEATHER[1], WEATHER[2], (h - 0.5) / 0.5];
    for (const key in a) mixed[key] = typeof a[key] === "number" ? a[key] + (b[key] - a[key]) * t : (mixed[key] || new THREE.Color()).copy(a[key]).lerp(b[key], t);
    sky.uniforms.top.value.copy(mixed.top);
    sky.uniforms.mid.value.copy(mixed.mid);
    sky.uniforms.horizon.value.copy(mixed.horizon);
    sky.uniforms.sunColor.value.copy(mixed.sun);
    sky.uniforms.sunPower.value = mixed.sunPower;
    scene.fog.color.copy(mixed.horizon);
    sun.color.copy(mixed.light); sun.intensity = mixed.lightPower;
    rim.color.copy(mixed.sun); rim.intensity = 0.25 + 0.9 * Math.max(0, h - 0.4);
    hemi.color.copy(mixed.sky); hemi.groundColor.copy(mixed.ground);
    renderer.toneMappingExposure = mixed.exposure;
    field.material.color.copy(mixed.grass);
    yard.material.color.copy(mixed.grass).lerp(WHITE, 0.18);
    for (const node of scenery) {
      if (node.userData.tone === "hills") node.material.color.copy(mixed.hills);
      else if (node.userData.tone === "trees") node.material.color.copy(node.userData.color).lerp(mixed.hills, 0.35);
    }
    for (const cloud of clouds) cloud.material.color.copy(mixed.shade).lerp(mixed.cloud, 0.45 + 0.55 * cloud.userData.shade);
    rainAmount = Math.min(1, Math.max(0, (0.38 - h) / 0.3));
    // Lights on inside: a home that is looked after, at golden hour.
    for (const pane of windows) pane.material.emissive.copy(LAMP).multiplyScalar(Math.max(0, h - 0.45) * 1.4);
  }

  // Always drawing now (the clouds drift), but only while the tab is visible: the browser pauses it otherwise.
  function draw() {
    if (!alive || queued) return;
    queued = requestAnimationFrame(frame);
  }
  function frame(time) {
    queued = 0;
    if (!alive) return;
    const gap = last ? time - last : 16;
    last = time;
    const dt = Math.min(gap, 100) / 1000;
    clock += dt;
    if (gap > 0 && gap < 500) watch(gap);

    if (glide) {
      if (glide.start == null) glide.start = glide.last = time;
      const g = time - glide.last;
      if (g > 0 && g < 500) { glide.spent += g; glide.frames += 1; }   // a longer gap is a hidden tab, not a slow phone
      glide.last = time;
      const t = Math.min(1, (time - glide.start) / GLIDE_MS);
      const eased = t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;   // starts and stops gently
      now.at.lerpVectors(glide.from.at, glide.to.at, eased);
      now.from.lerpVectors(glide.from.from, glide.to.from, eased).normalize();
      now.distance = glide.from.distance + (glide.to.distance - glide.from.distance) * eased;
      if (t >= 1) { const done = glide; glide = null; if (judge(done)) return; }
    }
    place();

    // The weather drifts towards the score's, over about a second and a half.
    if (health < 0) health = healthWanted;
    if (Math.abs(health - healthWanted) > 0.001) { health += (healthWanted - health) * Math.min(1, dt * 1.8); weather(health); }

    for (const cloud of clouds) {
      cloud.position.x += cloud.userData.drift * dt;
      if (cloud.position.x > 160) cloud.position.x = -160;
      // A cloud close to the camera thins out, so coming down through the deck feels like mist, not a wall.
      const near = cloud.position.distanceTo(camera.position);
      cloud.material.opacity = cloud.userData.base * Math.min(1, Math.max(0, (near - 4) / 14)) * (0.85 + 0.15 * (1 - rainAmount));
    }

    rain.visible = rainAmount > 0.01;
    if (rain.visible) {
      rain.material.opacity = 0.5 * rainAmount;
      for (let i = 0; i < DROPS; i++) {
        const k = i * 6;
        let y = rainPositions[k + 1] - 16 * dt;
        if (y < 0) y += 16;
        rainPositions[k + 1] = y; rainPositions[k + 4] = y - 0.38;
      }
      rainGeometry.attributes.position.needsUpdate = true;
    }

    if (sparking > 0) {
      sparking -= dt;
      for (let i = 0; i < SPARKS; i++) {
        if (sparkLife[i] <= 0) { sparkPositions[i * 3 + 1] = -50; continue; }
        sparkLife[i] -= dt;
        sparkSpeed[i * 3 + 1] -= 1.1 * dt;   // they float up and slow down
        for (let a = 0; a < 3; a++) sparkPositions[i * 3 + a] += sparkSpeed[i * 3 + a] * dt;
        const fade = Math.max(0, Math.min(1, sparkLife[i]));
        for (let a = 0; a < 3; a++) sparkColors[i * 3 + a] *= 0.985 + 0.015 * fade;
      }
      sparkGeometry.attributes.position.needsUpdate = true;
      sparkGeometry.attributes.color.needsUpdate = true;
    }
    sparks.visible = sparking > 0;

    for (const name in parts) heal(parts[name], time);

    renderer.render(scene, camera);
    draw();
  }

  // A part that has just been repaired: its cracks close up, its glow swells and settles.
  function heal(part, time) {
    if (!part.heal) return;
    if (part.heal.start == null) part.heal.start = time;
    const t = Math.min(1, (time - part.heal.start) / HEAL_MS), close = 1 - Math.min(1, t * 1.6);
    for (const marks of [part.crk, part.dmg]) {
      if (!marks.visible) continue;
      marks.children.forEach((node) => node.scale.setScalar(Math.max(0.001, close)));
    }
    const swell = 1 + 0.45 * Math.sin(Math.PI * t);
    part.halo.scale.set(part.halo.userData.w * swell, part.halo.userData.h * swell, 1);
    if (t >= 1) {
      for (const marks of [part.crk, part.dmg]) { marks.visible = false; marks.children.forEach((node) => node.scale.setScalar(1)); }
      part.halo.scale.set(part.halo.userData.w, part.halo.userData.h, 1);
      part.heal = null;
    }
  }

  // Is the phone keeping up? Too slow and the home gets simpler (no shadows, fewer pixels); hopeless and the
  // drawn home takes over.
  function watch(gap) {
    perf.spent += gap; perf.frames += 1;
    if (perf.frames < 90) return;
    const average = perf.spent / perf.frames;
    perf.spent = 0; perf.frames = 0;
    if (average > HOPELESS_FRAME_MS && perf.lowered) { onFail(); return; }
    if (average > SLOW_FRAME_MS && !perf.lowered) {
      perf.lowered = true;
      renderer.shadowMap.enabled = false;
      scene.traverse((node) => { if (node.material) node.material.needsUpdate = true; });
      ratio = 1;
      renderer.setPixelRatio(ratio);
      resize();
    }
  }
  // After each glide: was it smooth? Twice jerky and the camera stops gliding (it jumps instead); hopeless and
  // the drawn home takes over. True when the 3D home has been given up.
  function judge(done) {
    if (done.frames < 5) return false;
    const average = done.spent / done.frames;
    if (average > HOPELESS_FRAME_MS) { onFail(); return true; }
    if (average > SLOW_FRAME_MS && ++slowGlides >= 2) still = true;
    return false;
  }
  function aim(name) {
    if (!VIEWS[name]) name = "home";
    if (name === view && placed) return;
    view = name;
    if (!placed || still) { glide = null; now = pose(name); placed = true; return; }
    glide = { from: { at: now.at.clone(), from: now.from.clone(), distance: now.distance }, to: pose(name), start: null, last: 0, spent: 0, frames: 0 };
  }
  function resize() {
    const w = host.clientWidth, h = host.clientHeight;
    if (!w || !h) return;
    width = w; height = h;
    renderer.setSize(w, h, false);
    project();
    if (glide) glide.to = pose(view); else now = pose(view);
  }
  const watcher = new ResizeObserver(resize);
  watcher.observe(host);
  resize();

  function setFrame(box) {
    const next = box ? { x: Math.round(box.x), y: Math.round(box.y), w: Math.round(box.w), h: Math.round(box.h) } : null;
    if (JSON.stringify(next) === JSON.stringify(frameBox)) return;
    frameBox = next;
    project();
    if (glide) glide.to = pose(view); else now = pose(view);
  }
  function setIntro(p) {
    const next = Math.min(1, Math.max(0, p));
    if (Math.abs(next - intro) < 0.0005) return;
    intro = next;
    project();
  }

  let first = true;
  function update({ states = {}, focus = null, lush = 1, health: wanted = 0.5 } = {}) {
    healthWanted = Math.min(1, Math.max(0, wanted));
    if (first) weather(health = healthWanted);
    const green = Math.min(1, Math.max(0, lush));
    for (const name in parts) {
      const part = parts[name], state = states[name];
      part.whole.visible = Boolean(state);
      if (!state) { part.state = null; continue; }
      const faded = Boolean(focus) && focus !== name;
      const healing = !first && state === "repaired" && (part.state === "cracked" || part.state === "broken");
      if (healing) {
        // Keep the old cracks on screen for the heal to close them.
        part.crk.visible = true;
        part.dmg.visible = part.state === "broken";
        part.halo.userData.w ??= part.halo.scale.x; part.halo.userData.h ??= part.halo.scale.y;
        part.heal = { start: null };
        burst(part.halo.position, part.size);
      } else if (!part.heal || state !== "repaired") {
        if (part.heal) { part.heal = null; [part.crk, part.dmg].forEach((g) => g.children.forEach((node) => node.scale.setScalar(1))); }
        part.crk.visible = state === "cracked" || state === "broken";
        part.dmg.visible = state === "broken";
      }
      part.state = state;
      part.halo.userData.w ??= part.halo.scale.x; part.halo.userData.h ??= part.halo.scale.y;
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
    first = false;
    aim(focus && states[focus] ? focus : "home");
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
    scene.traverse((node) => { if (node.geometry) node.geometry.dispose(); if (node.material) node.material.dispose(); });
    Object.values(pins).forEach((texture) => texture.dispose());
    [glow, puff, sparkTexture].forEach((texture) => texture.dispose());
    renderer.dispose();
    canvas.remove();
  }
  // The phone took the graphics memory back (another app, a locked screen): the drawn home takes over.
  canvas.addEventListener("webglcontextlost", (event) => { event.preventDefault(); if (alive) onFail(); });

  return { update, setFrame, setIntro, dispose };
}

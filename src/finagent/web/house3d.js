// The family's architectural home in 3D. Full mode loads it by default (see stage_page.html); the drawn
// home (the SVG) stays as the fallback. Bevelled architecture, local textures and studio reflections: no models,
// no image files.
//
//   const home = mount(host, { onFail, onPick })   -> throws when the browser has no WebGL
//   home.update({ states, focus, lush, health })
//        states: { roof: "solid" | "cracked" | "broken" | "repaired" | null (the family has no such part), ... }
//        focus:  the part being talked about (the others fade), or null
//        lush:   1 = a green garden, 0 = a dry one
//        health: 0..1, the selected scenario's score (used only for subtle window lighting)
//   home.setFrame({ x, y, w, h })   the box of the canvas the home must sit in (the page's scene), in pixels
//   home.setIntro(p)                 0 = high above the clouds, 1 = at the home: the hero's scroll drives it
//   home.dispose()
//
// What it shows: each part's state, the part in focus, the garden drying up and a subtle glow for selected
// improvements. The calm studio light remains consistent across families and scores.
// Plans: 02-DOCS/ftd/stage-casa-3d.md and 02-DOCS/ftd/stage-casa-que-mejora.md.
import * as THREE from "./vendor/three.module.min.js";

const INK = 0x23232e, WALL = 0xeee8db, PIPE = 0x538878, JOINT = 0x336456, CRACK = 0x5d5142;
const WOOD = 0x94765b, GLASS = 0x36535a, FRAME = 0x303e3a, ROOF = 0x4b514d, PAVING = 0xd6ceba, DRY = 0xb9a58a;
const WATER = 0x7caeb0, POOL = 0x9aa4ae;   // the pool floor is bare concrete: empty, it reads as empty
const LEAF = [new THREE.Color(0x48664c), new THREE.Color(0xa99e7a)];
const LEAF_LIGHT = [new THREE.Color(0x78865a), new THREE.Color(0xc3b48c)];
const GRASS = [new THREE.Color(0x8c9c72), new THREE.Color(0xc9b994)];
const FADED = new THREE.Color(0xe3dfd2), FADE = 0.16;
const REPAIRED_TINT = new THREE.Color(0x7ba782);
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
  home: { at: [0, 1.25, 0.2], from: [0.62, 0.43, 0.72], halfWidth: 6.3, halfHeight: 3.5, depth: 1.0 },
  roof: { at: [-0.3, 3.1, -0.4], from: [0.5, 0.68, 0.6], halfWidth: 4.7, halfHeight: 2.5, depth: 0.9 },
  walls: { at: [-0.2, 2.0, 0.9], from: [0.36, 0.23, 0.91], halfWidth: 4.3, halfHeight: 2.25, depth: 0.9 },
  plumbing: { at: [2.9, 0.6, 2.8], from: [0.42, 0.58, 0.72], halfWidth: 2.45, halfHeight: 1.6, depth: 0.9 },
  foundations: { at: [0, 0.55, 1.5], from: [0.42, 0.25, 0.88], halfWidth: 5.6, halfHeight: 2.4, depth: 0.9 },
  garden: { at: [-2.8, 1.15, 1.3], from: [-0.25, 0.42, 0.87], halfWidth: 3.5, halfHeight: 2.2, depth: 0.9 },
};
// High above the clouds, looking at the sun: where the visit starts (setIntro(0)).
const INTRO = { position: new THREE.Vector3(12, 46, 52), at: new THREE.Vector3(-26, 30, -120) };
const FOV = 32;
const GLIDE_MS = 900;        // short and slow: nobody should feel the room move
const HEAL_MS = 1400;
const SLOW_FRAME_MS = 45;    // a glide that averages worse than this (about 22 frames a second) is a jerky one
const HOPELESS_FRAME_MS = 150;

// A small seeded random, so the clouds and trees are the same on every visit.
let seed = 7;
const rand = () => ((seed = (seed * 16807) % 2147483647) - 1) / 2147483646;
const between = (a, b) => a + (b - a) * rand();

let finishes = null;
function mesh(geometry, color, x = 0, y = 0, z = 0) {
  const finish = color === WALL || color === PAVING ? finishes?.stone : color === WOOD ? finishes?.wood : null;
  const m = new THREE.Mesh(geometry, new THREE.MeshStandardMaterial({ color, roughness: .82, metalness: .02,
    ...(finish ? { map: finish, bumpMap: finish, bumpScale: .025 } : {}) }));
  m.position.set(x, y, z);
  m.castShadow = m.receiveShadow = true;
  m.userData.color = new THREE.Color(color);   // its own colour, before fading or drying
  return m;
}
const box = (w, h, d, color, x, y, z) => {
  // Tiny chamfers catch the light along the architecture's edges, without heavy postprocessing.
  const b = Math.min(.025, w * .07, h * .07, d * .07);
  if (Math.min(w, h, d) < .12) return mesh(new THREE.BoxGeometry(w, h, d), color, x, y, z);
  const shape = new THREE.Shape();
  shape.moveTo(-w / 2 + b, -h / 2 + b); shape.lineTo(w / 2 - b, -h / 2 + b);
  shape.lineTo(w / 2 - b, h / 2 - b); shape.lineTo(-w / 2 + b, h / 2 - b); shape.closePath();
  const geometry = new THREE.ExtrudeGeometry(shape, { depth: d - 2 * b, bevelEnabled: true, bevelSize: b, bevelThickness: b, bevelSegments: 2, steps: 1 });
  geometry.translate(0, 0, -(d - 2 * b) / 2);
  return mesh(geometry, color, x, y, z);
};
const ball = (r, color, x, y, z) => mesh(new THREE.IcosahedronGeometry(r, 2), color, x, y, z);
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

// A modern home on a plinth: white volumes, a cantilevered upper floor, flat dark roofs, wide glazing with black
// frames, a pool and round trees on the lawn. The plinth's top (the lawn) is at y = 0.46; the front faces +z.
const LAWN_TOP = 0.46;
const glassPanes = [];   // every window, to light them up on a good evening
function pane(w, h, d, x, y, z) {
  const m = box(w, h, d, GLASS, x, y, z);
  m.material.roughness = .14;
  m.material.metalness = .38;
  m.material.envMapIntensity = 1.6;
  m.castShadow = false;
  glassPanes.push(m);
  return m;
}
const frame = (w, h, d, x, y, z) => box(w, h, d, FRAME, x, y, z);

// Every part: its body, what shows when it is cracked ("crk"), what is added when it is broken ("dmg"),
// where its mark goes ("pin") and where its glow sits ("halo": centre and size). "onState" is for a part
// whose body itself changes with its state (the pool's water).
function foundations() {
  const z = 4.015, x = 5.015;
  return {
    body: [box(10, 0.4, 8, PAVING, 0, 0.2, 0), box(10.1, 0.07, 8.1, FRAME, 0, 0.09, 0),
      box(3.6, 0.03, 2.1, PAVING, -0.9, LAWN_TOP + 0.015, 2.05), box(1.3, 0.03, 1.0, PAVING, -0.9, LAWN_TOP + 0.015, 3.5),
      ...[-2.1, -.9, .3].map((x) => box(.012, .006, 2.08, 0xb4ae9d, x, LAWN_TOP + .034, 2.05)),
      ...[1.4, 2.1, 2.8].map((z) => box(3.58, .006, .012, 0xb4ae9d, -.9, LAWN_TOP + .034, z)),
      box(1.5, .12, .5, PAVING, -.9, .24, 4.15), box(1.7, .1, .55, PAVING, -.9, .1, 4.5)],
    crk: [...crack([[-2.2, 0.39, z], [-2.0, 0.27, z], [-2.15, 0.14, z], [-1.95, 0.02, z]]), ...crack([[x, 0.39, -1.0], [x, 0.24, -1.2], [x, 0.1, -0.95]])],
    dmg: [box(0.9, 0.22, 0.05, 0x7d808c, 2.6, 0.25, z + 0.01), ...crack([[0.5, 0.39, z], [0.72, 0.22, z], [0.6, 0.02, z]], CRACK, 0.034),
      ...crack([[x, 0.39, 1.5], [x, 0.2, 1.8], [x, 0.05, 1.6]], CRACK, 0.034)],
    pin: [-3.4, 0.24, 4.2], halo: [0, 0.3, 0, 12, 2.4],
  };
}

function walls() {
  const front = 0.83, upper = 1.21, wing = 1.71;
  const mullions = [-2.9, -1.9, -0.9, 0.1, 1.1].map((x) => frame(0.05, 1.3, 0.07, x, 1.15, front + 0.02));
  const ribbon = [-3.2, -2.0, -0.8, 0.4].map((x) => frame(0.05, 0.75, 0.07, x, 2.85, upper + 0.02));
  return {
    body: [
      box(5.0, 1.6, 3.2, WALL, -0.9, LAWN_TOP + 0.8, -0.8),                                   // the ground floor
      pane(4.2, 1.3, 0.05, -0.9, 1.15, front), ...mullions, frame(4.25, 0.07, 0.08, -0.9, 1.8, front + 0.02), frame(4.25, 0.07, 0.08, -0.9, 0.5, front + 0.02),
      box(6.4, 1.5, 3.6, WALL, -0.5, 2.81, -0.6),                                              // the upper floor, reaching out over the glass
      pane(3.6, 0.75, 0.05, -1.4, 2.85, upper), ...ribbon, frame(3.65, 0.06, 0.08, -1.4, 3.24, upper + 0.02), frame(3.65, 0.06, 0.08, -1.4, 2.46, upper + 0.02),
      pane(0.9, 1.1, 0.05, 1.6, 2.8, upper), frame(0.05, 1.1, 0.07, 1.6, 2.8, upper + 0.02),
      pane(0.05, 0.7, 1.8, 2.72, 2.85, -0.8),
      box(2.6, 0.1, 1.2, WALL, -2.4, 2.07, 1.8), box(2.6, 0.45, 0.03, 0xbcd6ea, -2.4, 2.35, 2.39),   // a terrace with a glass rail
      box(2.8, 1.3, 2.8, WALL, 3.3, LAWN_TOP + 0.65, 0.3),                                      // the side wing
      pane(1.9, 1.0, 0.05, 3.3, 1.02, wing), frame(2.0, 0.06, 0.08, 3.3, 1.55, wing + 0.02), frame(0.05, 1.0, 0.07, 3.3, 1.02, wing + 0.02),
      ...Array.from({ length: 13 }, (_, i) => box(.045, 1.24, .065, WOOD, .72 + i * .065, 2.83, upper + .045)),
      ...Array.from({ length: 18 }, (_, i) => box(.045, 1.14, .065, WOOD, 2.0 + i * .055, 1.08, wing + .045)),
      box(1.9, .035, .035, 0xc9ad7f, 3.3, 1.5, wing + .1),
      // Shaded entry and quiet terrace furniture give scale without cluttering the five parts.
      box(.65, .2, .7, WOOD, -1.7, .66, 2.02), box(.68, .1, .72, 0xe5dfcf, -1.7, .81, 2.02), box(.68, .38, .12, WOOD, -1.7, 1, 1.72),
      box(.65, .2, .7, WOOD, -.5, .66, 2.02), box(.68, .1, .72, 0xe5dfcf, -.5, .81, 2.02), box(.68, .38, .12, WOOD, -.5, 1, 1.72),
      box(.4, .34, .45, FRAME, -1.1, .68, 2.8),
    ],
    crk: [...crack([[0.72, 3.5, upper + 0.01], [0.86, 3.2, upper + 0.01], [0.72, 2.95, upper + 0.01], [0.9, 2.6, upper + 0.01], [0.78, 2.2, upper + 0.01]]),
      ...crack([[2.1, 1.72, wing + 0.01], [2.24, 1.4, wing + 0.01], [2.1, 1.1, wing + 0.01], [2.22, 0.7, wing + 0.01]])],
    dmg: [box(0.95, 0.7, 0.06, 0x9fb3c8, -2.6, 2.85, upper + 0.02),
      ...crack([[-3.0, 3.12, upper + 0.06], [-2.6, 2.85, upper + 0.06], [-2.2, 3.15, upper + 0.06]], 0xffffff, 0.018),
      ...crack([[-2.95, 2.55, upper + 0.06], [-2.6, 2.85, upper + 0.06], [-2.25, 2.55, upper + 0.06]], 0xffffff, 0.018),
      box(0.6, 0.3, 0.04, 0xc9b2a6, 2.3, 3.3, upper + 0.01),
      ...crack([[2.715, 3.5, 0.2], [2.715, 3.1, -0.2], [2.715, 2.8, 0.15], [2.715, 2.3, -0.25]], CRACK, 0.034)],
    pin: [-0.4, 3.05, 1.45], halo: [-0.2, 2.0, 0, 9.5, 5.2],
  };
}

function roof() {
  const y = 3.585, parapet = (w, d, x, z) => box(w, 0.14, d, WALL, x, 3.63, z);
  return {
    body: [box(6.1, 0.05, 3.3, ROOF, -0.5, y, -0.6),
      parapet(6.4, 0.12, -0.5, 1.14), parapet(6.4, 0.12, -0.5, -2.34), parapet(0.12, 3.6, -3.64, -0.6), parapet(0.12, 3.6, 2.64, -0.6),
      box(0.26, 0.5, 0.26, ROOF, 0.7, 3.85, -1.5), box(0.22, 0.4, 0.22, ROOF, 1.15, 3.8, -1.7),
      box(2.6, 0.05, 2.6, ROOF, 3.3, 1.8, 0.3)],
    crk: [...crack([[-2.8, y + 0.03, -1.6], [-2.3, y + 0.03, -1.0], [-2.5, y + 0.03, -0.4], [-2.0, y + 0.03, 0.3]], 0xc8ccd6),
      ...crack([[2.4, 1.83, -0.6], [2.9, 1.83, -0.2], [2.7, 1.83, 0.5]], 0xc8ccd6)],
    dmg: [box(1.1, 0.02, 0.9, 0x0c0d10, 0.0, y + 0.03, -0.2),
      rod(0.035, WOOD, [-0.45, y + 0.06, -0.55], [0.4, y + 0.06, 0.15]), rod(0.035, WOOD, [-0.4, y + 0.06, 0.15], [0.35, y + 0.06, -0.6]),
      ...crack([[1.2, y + 0.03, -2.0], [1.6, y + 0.03, -1.4], [1.4, y + 0.03, -0.8]], 0xc8ccd6)],
    pin: [-0.5, 4.15, 0.3], halo: [-0.5, 3.7, -0.5, 8.2, 3.4],
  };
}

function plumbing() {
  // The pool: water is cash flowing in. Lower when it is cracked, gone (a puddle by the pool) when broken.
  const cx = 2.9, cz = 2.9, rim = (w, d, x, z) => box(w, 0.12, d, PAVING, x, LAWN_TOP + 0.06, z);
  const water = box(2.55, 0.05, 1.35, WATER, cx, LAWN_TOP + 0.085, cz);
  water.material.roughness = .18; water.material.metalness = .28; water.material.envMapIntensity = 1.4;
  water.castShadow = false;
  water.userData.water = true;
  const puddle = mesh(new THREE.CircleGeometry(0.5, 20), WATER, 4.55, LAWN_TOP + 0.005, 3.0);
  puddle.rotation.x = -Math.PI / 2;
  return {
    body: [box(2.55, 0.02, 1.35, POOL, cx, LAWN_TOP + 0.012, cz), water,
      rim(2.85, 0.15, cx, cz + 0.75), rim(2.85, 0.15, cx, cz - 0.75), rim(0.15, 1.5, cx - 1.35, cz), rim(0.15, 1.5, cx + 1.35, cz),
      rod(0.05, PIPE, [3.6, LAWN_TOP + 0.05, 1.72], [3.6, LAWN_TOP + 0.05, 2.15]), rod(0.05, PIPE, [3.6, LAWN_TOP + 0.05, 1.73], [3.6, 0.9, 1.73]),
      ball(0.08, JOINT, 3.6, 0.9, 1.75)],
    crk: [...crack([[2.3, LAWN_TOP + 0.12, cz + 0.83], [2.42, LAWN_TOP + 0.06, cz + 0.83], [2.32, LAWN_TOP, cz + 0.83]])],
    dmg: [puddle, ...crack([[3.3, LAWN_TOP + 0.12, cz - 0.83], [3.45, LAWN_TOP + 0.05, cz - 0.83], [3.35, LAWN_TOP, cz - 0.83]]),
      rod(0.03, INK, [3.53, 0.75, 1.8], [3.67, 0.6, 1.8]), rod(0.03, INK, [3.53, 0.6, 1.8], [3.67, 0.75, 1.8])],
    onState(state) {
      water.visible = state !== "broken";
      const full = state === "cracked" ? 0.45 : 1;
      water.scale.y = full;
      water.position.y = LAWN_TOP + 0.012 + 0.075 * full;
    },
    pin: [cx, 1.35, cz], halo: [cx, 0.7, cz, 3.9, 2.6],
  };
}

function garden() {
  const leaf = (r, x, y, z, light) => { const m = ball(r, 0, x, y, z); m.userData.leaf = light ? LEAF_LIGHT : LEAF; return m; };
  // A round tree (or a bush) that sways from its foot and shrinks as the garden dries.
  const tree = (x, z, size = 1) => {
    const g = group("canopy", rod(0.05 * size, WOOD, [0, 0, 0], [0, 0.8 * size, 0]), leaf(0.42 * size, 0, 1.0 * size, 0), leaf(0.26 * size, 0.18 * size, 0.78 * size, 0.12 * size, true));
    g.position.set(x, LAWN_TOP, z);
    g.userData.sway = rand() * 6;
    return g;
  };
  const bush = (x, z, r = 0.2) => { const g = group("canopy", leaf(r, 0, r * 0.8, 0, rand() > 0.5)); g.position.set(x, LAWN_TOP, z); return g; };
  const lawn = box(9.7, 0.06, 7.7, 0, 0, LAWN_TOP - 0.03, 0);
  lawn.userData.leaf = GRASS;
  lawn.castShadow = false;
  const trees = [tree(-4.4, -3.3), tree(-4.4, -1.4, 0.85), tree(-4.3, 0.9, 1.1), tree(-4.25, 3.4, 0.8), tree(4.5, -3.3, 1.1), tree(1.6, -3.4, 0.9),
    tree(-1.9, -3.5), tree(4.6, -1.7, 0.75)];
  const bushes = [bush(-3.9, 3.75), bush(-3.2, 3.8, 0.17), bush(-2.5, 3.75, 0.22), bush(0.6, 3.8), bush(1.2, 3.75, 0.16), bush(4.6, 1.2, 0.24), bush(4.55, 0.5, 0.18)];
  const flower = (x, z, color) => group("flower", rod(0.015, 0x57bf93, [x, LAWN_TOP, z], [x, LAWN_TOP + 0.25, z]), ball(0.07, color, x, LAWN_TOP + 0.25, z));
  const bloom = group("bloom", flower(-3.55, 3.5, 0xdf7afe), flower(-2.85, 3.55, 0x948df7), flower(0.9, 3.55, 0xdf7afe), flower(4.3, 0.85, 0xffd27a));
  return {
    body: [lawn, ...trees, ...bushes, bloom],
    crk: [box(1.3, 0.01, 0.8, DRY, -3.3, LAWN_TOP + 0.004, 2.3), box(0.8, 0.01, 0.6, DRY, 4.0, LAWN_TOP + 0.004, -2.6)],
    dmg: [box(1.6, 0.01, 1.0, DRY, 1.0, LAWN_TOP + 0.004, -2.9), box(1.0, 0.01, 0.9, DRY, -4.0, LAWN_TOP + 0.004, -0.2),
      rod(0.035, DRY, [-4.3, 1.4, 0.9], [-4.8, 1.9, 1.1]), rod(0.035, DRY, [-4.3, 1.5, 0.9], [-3.9, 2.0, 0.8])],
    pin: [-4.3, 2.35, 0.9], halo: [-3.6, 1.2, 1.4, 5.4, 4.2],
    canopies: [...trees, ...bushes], bloom,
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
const glowTexture = (inner = "rgba(136,180,147,.35)", middle = "rgba(136,180,147,.1)") => drawn(128, (g, s) => {
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
  glassPanes.length = 0;
  // Small locally painted textures; no external images, services, or model downloads.
  const stone = drawn(128, (g, s) => {
    g.fillStyle = "#f3f0e8"; g.fillRect(0, 0, s, s);
    for (let i = 0; i < 4500; i++) { const v = Math.floor(between(190, 245)); g.fillStyle = `rgba(${v},${v},${v},.2)`; g.fillRect(rand() * s, rand() * s, 1, 1); }
  });
  const wood = drawn(128, (g, s) => {
    g.fillStyle = "#ded0b1"; g.fillRect(0, 0, s, s);
    for (let i = 0; i < 160; i++) { g.fillStyle = `rgba(80,53,27,${between(.04, .2)})`; g.fillRect(rand() * s, 0, between(.3, 1.2), s); }
  });
  for (const texture of [stone, wood]) { texture.wrapS = texture.wrapT = THREE.RepeatWrapping; texture.repeat.set(2, 2); }
  finishes = { stone, wood };
  const renderer = new THREE.WebGLRenderer({ antialias: true });   // throws without WebGL
  let ratio = Math.min(window.devicePixelRatio || 1, 1.75);       // sharper only costs battery on a full screen
  renderer.setPixelRatio(ratio);
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  const canvas = renderer.domElement;
  canvas.setAttribute("role", "img");
  canvas.setAttribute("aria-label", "Your plan drawn as a home");
  canvas.style.cursor = "pointer";
  host.appendChild(canvas);

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0xf4f1e9);
  // A compact studio reflection map adds readable highlights to the glass and water.
  const studio = drawn(256, (g, s) => {
    const fill = g.createLinearGradient(0, 0, 0, s);
    fill.addColorStop(0, "#d2dcd9"); fill.addColorStop(.48, "#fff9e9"); fill.addColorStop(.52, "#bcbcad"); fill.addColorStop(1, "#646d60");
    g.fillStyle = fill; g.fillRect(0, 0, s, s);
    g.fillStyle = "#fffdf3"; g.fillRect(s * .12, s * .25, s * .16, s * .2);
    g.fillStyle = "#e7e7da"; g.fillRect(s * .65, s * .2, s * .22, s * .25);
  });
  studio.mapping = THREE.EquirectangularReflectionMapping;
  const pmrem = new THREE.PMREMGenerator(renderer);
  const environment = pmrem.fromEquirectangular(studio);
  scene.environment = environment.texture;
  studio.dispose(); pmrem.dispose();
  scene.fog = new THREE.Fog(0xffffff, 40, 190);
  const sky = skyDome();
  sky.dome.visible = false; // A continuous studio backdrop keeps text and the home in one visual space.
  scene.add(sky.dome);
  const hemi = new THREE.HemisphereLight(0xffffff, 0xc9cbd8, 1.6);
  scene.add(hemi);
  const sun = new THREE.DirectionalLight(0xffffff, 1.6);   // the key light, from the camera's side so the front reads
  sun.position.set(6, 11, 8);
  sun.castShadow = true;
  sun.shadow.mapSize.set(innerWidth > 860 ? 2048 : 1024, innerWidth > 860 ? 2048 : 1024);
  Object.assign(sun.shadow.camera, { left: -10, right: 10, top: 10, bottom: -10, near: 1, far: 50 });
  sun.shadow.bias = -0.0006;
  sun.shadow.normalBias = 0.02;
  sun.shadow.radius = 3;
  scene.add(sun);
  const rim = new THREE.DirectionalLight(0xffffff, 0.5);   // the evening light from behind, along the edges
  rim.position.copy(SUN_DIR).multiplyScalar(30);
  scene.add(rim);

  // The land: a wide field around the plinth, hills and trees far off.
  const field = mesh(new THREE.CircleGeometry(220, 64), 0x78ab62);
  field.material.dispose();
  field.material = new THREE.ShadowMaterial({ color: 0x28332c, opacity: .12 });
  field.rotation.x = -Math.PI / 2; field.position.y = -0.02; field.castShadow = false;
  scene.add(field);
  const contact = glowTexture("rgba(45,47,35,.28)", "rgba(45,47,35,.12)");
  const contactPlane = new THREE.Mesh(new THREE.PlaneGeometry(16, 12), new THREE.MeshBasicMaterial({ map: contact, transparent: true, depthWrite: false }));
  contactPlane.rotation.x = -Math.PI / 2; contactPlane.position.y = -.01;
  scene.add(contactPlane);
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

  // Rain: short streaks falling around the home. It only shows on a low score.
  const DROPS = 180;
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
  const SPARK_TONES = [new THREE.Color(0xd6c69d), new THREE.Color(0xa8c5ad), new THREE.Color(0xffffff), new THREE.Color(0x8daf8c)];
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
    ring.position.set(at.x, LAWN_TOP + 0.02, at.z);
    ringTime = 0;
  }

  // A ring of light that runs over the ground from a part as it heals.
  const ring = new THREE.Mesh(new THREE.RingGeometry(0.85, 1, 64), new THREE.MeshBasicMaterial({ color: 0x8daf8c, transparent: true, opacity: 0,
    depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide, fog: false }));
  ring.rotation.x = -Math.PI / 2;
  ring.visible = false;
  scene.add(ring);
  let ringTime = -1;

  // Birds over a home that is doing well: a few dark wings wheeling high up.
  const birds = [];
  // The page's own state colours, so the marks match the legend.
  const css = getComputedStyle(host);
  const pins = {};
  for (const state in GLYPH) pins[state] = pinTexture(css.getPropertyValue("--" + state).trim() || STATE_COLOR[state], GLYPH[state]);
  const glow = glowTexture();

  const parts = {};
  const windows = glassPanes;
  for (const [name, make] of Object.entries({ foundations, walls, roof, plumbing, garden })) {
    const made = make();
    const crk = group("crk", made.crk), dmg = group("dmg", made.dmg);
    const halo = new THREE.Sprite(new THREE.SpriteMaterial({ map: glow, transparent: true, depthWrite: false, depthTest: false, blending: THREE.AdditiveBlending, opacity: .45 }));
    halo.position.set(made.halo[0], made.halo[1], made.halo[2]);
    halo.scale.set(made.halo[3], made.halo[4], 1);
    const pin = new THREE.Sprite(new THREE.SpriteMaterial({ map: pins.solid, transparent: true, depthTest: false }));
    pin.position.set(...made.pin);
    pin.renderOrder = 10;   // on top of the home, like a label
    const whole = group(name, made.body, crk, dmg, halo, pin);
    scene.add(whole);
    parts[name] = { whole, crk, dmg, halo, pin, canopies: made.canopies || [], bloom: made.bloom || null,
      size: made.halo[3], state: null, heal: null, onState: made.onState || null, pinY: made.pin[1] };
  }

  let water = null;
  parts.plumbing.whole.traverse((node) => { if (node.userData.water) water = node; });

  // The picture follows the pointer a little, so the home feels within reach.
  const pointer = { x: 0, y: 0, nowX: 0, nowY: 0 };
  const follow = (event) => { pointer.x = (event.clientX / innerWidth) * 2 - 1; pointer.y = (event.clientY / innerHeight) * 2 - 1; };
  addEventListener("pointermove", follow, { passive: true });

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
    // The camera drifts slowly around the home, like a film, and leans towards the pointer.
    pointer.nowX += (pointer.x - pointer.nowX) * 0.05; pointer.nowY += (pointer.y - pointer.nowY) * 0.05;
    const orbit = (view === "home" ? 0.035 : 0.01) * Math.sin(clock * 0.13);
    const from = now.from.clone().applyAxisAngle(new THREE.Vector3(0, 1, 0), orbit - pointer.nowX * 0.025);
    from.y += pointer.nowY * 0.015;
    from.normalize();
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
    sky.uniforms.top.value.set(0xd5dfd7);
    sky.uniforms.mid.value.set(0xe9e9df);
    sky.uniforms.horizon.value.set(0xf4f1e9);
    sky.uniforms.sunColor.value.copy(mixed.sun);
    sky.uniforms.sunPower.value = .1;
    scene.fog.color.set(0xf4f1e9);
    sun.color.set(0xffefd3); sun.intensity = 3;
    rim.color.set(0xe2eee9); rim.intensity = 1.3;
    hemi.color.set(0xf0f2e9); hemi.groundColor.set(0x9a9d89); hemi.intensity = 1.15;
    renderer.toneMappingExposure = 1;
    for (const cloud of clouds) cloud.material.color.copy(mixed.shade).lerp(mixed.cloud, 0.45 + 0.55 * cloud.userData.shade);
    rainAmount = 0; // Diagnosis is carried by labelled states, rather than punishing a low score with a storm.
    // Lights on inside: a home that is looked after, at golden hour.
    for (const pane of windows) pane.material.emissive.copy(LAMP).multiplyScalar(.035 + Math.max(0, h - .45) * .12);
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
      cloud.material.opacity = cloud.userData.base * Math.min(1, Math.max(0, (near - 8) / 18)) * (0.85 + 0.15 * (1 - rainAmount));
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

    // Life around the home: the trees sway (more in the rain), the marks float, the water shimmers, birds fly.
    const wind = 0.035 + 0.05 * rainAmount;
    for (const canopy of parts.garden.canopies) {
      if (canopy.userData.sway == null) continue;
      canopy.rotation.z = Math.sin(clock * 1.3 + canopy.userData.sway) * wind;
      canopy.rotation.x = Math.sin(clock * 0.9 + canopy.userData.sway * 2) * wind * 0.6;
    }
    let i = 0;
    for (const name in parts) parts[name].pin.position.y = parts[name].pinY + Math.sin(clock * 1.8 + i++) * 0.07;
    if (water) water.material.emissive.setRGB(0.04, 0.1, 0.16).multiplyScalar(1.2 + Math.sin(clock * 2.2));
    const flying = health > 0.45;
    for (const bird of birds) {
      bird.visible = flying;
      if (!flying) continue;
      const b = bird.userData, a = clock * b.speed + b.phase;
      bird.position.set(Math.cos(a) * b.radius, b.height + Math.sin(a * 3) * 0.6, Math.sin(a) * b.radius - 2);
      bird.rotation.y = -a;
      const flap = Math.sin(clock * b.flap + b.phase) * 0.6;
      b.leftHinge.rotation.z = flap; b.rightHinge.rotation.z = -flap;
    }
    if (ringTime >= 0) {
      ringTime += dt;
      const t = Math.min(1, ringTime / 1.4);
      ring.visible = t < 1;
      ring.scale.setScalar(0.5 + 7 * t);
      ring.material.opacity = 0.9 * (1 - t);
      if (t >= 1) ringTime = -1;
    }

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
      if (part.onState) part.onState(state);
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
    removeEventListener("pointermove", follow);
    scene.traverse((node) => { if (node.geometry) node.geometry.dispose(); if (node.material) node.material.dispose(); });
    Object.values(pins).forEach((texture) => texture.dispose());
    [glow, puff, sparkTexture, stone, wood, contact].forEach((texture) => texture.dispose());
    environment.dispose();
    renderer.dispose();
    canvas.remove();
  }
  // The phone took the graphics memory back (another app, a locked screen): the drawn home takes over.
  canvas.addEventListener("webglcontextlost", (event) => { event.preventDefault(); if (alive) onFail(); });

  return { update, setFrame, setIntro, dispose };
}

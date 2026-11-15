// The family's home in 3D. The page loads this file only with ?house=3d (see stage_page.html); the drawn
// home (the SVG) stays as the fallback. Built from plain shapes and flat colours: no models, no textures.
//
//   const home = mount(host, onFail)   -> throws when the browser has no WebGL
//   home.update({ states, focus, lush })   states: { roof: "solid" | "cracked" | "broken" | "repaired" | null, ... }
//   home.dispose()
//
// Plan and what is left out: 02-DOCS/ftd/stage-casa-3d.md. This first version only shows the five parts;
// their states, the focus and the camera come in the next PRs.
import * as THREE from "./vendor/three.module.min.js";

const INK = 0x23232e, WALL = 0xffffff, STONE = 0xbfc1d0, PIPE = 0x6586fc, JOINT = 0x4565d6;
const LEAF = 0x2f9e77, LEAF_LIGHT = 0x57bf93, WOOD = 0x8a6f57, GLASS = 0xcfe0ff, GROUND = 0xe9ebf3;

const TARGET = new THREE.Vector3(0, 1.6, 0);                  // the camera looks at the middle of the home
const FROM = new THREE.Vector3(0.55, 0.32, 0.77).normalize(); // from the front, a little to the right and above
const HALF_WIDTH = 5.4, HALF_HEIGHT = 3.1, DEPTH = 2.5;       // the room the home and its garden need around TARGET
const FOV = 32;

const material = (color) => new THREE.MeshLambertMaterial({ color, flatShading: true });

function mesh(geometry, color, x = 0, y = 0, z = 0) {
  const m = new THREE.Mesh(geometry, material(color));
  m.position.set(x, y, z);
  return m;
}
const box = (w, h, d, color, x, y, z) => mesh(new THREE.BoxGeometry(w, h, d), color, x, y, z);
const ball = (r, color, x, y, z) => mesh(new THREE.IcosahedronGeometry(r, 1), color, x, y, z);
// A pipe or a trunk from one point to another.
function rod(r, color, from, to) {
  const a = new THREE.Vector3(...from), b = new THREE.Vector3(...to);
  const m = mesh(new THREE.CylinderGeometry(r, r, a.distanceTo(b), 10), color);
  m.position.copy(a).add(b).multiplyScalar(0.5);
  m.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), b.clone().sub(a).normalize());
  return m;
}
function group(name, ...children) {
  const g = new THREE.Group();
  g.name = name;
  g.add(...children);
  return g;
}

function foundations() {
  return group("foundations", box(4.5, 0.4, 3.5, STONE, 0, 0.2, 0));
}

function walls() {
  const win = (x) => [box(0.92, 0.82, 0.04, INK, x, 1.8, 1.5), box(0.8, 0.7, 0.06, GLASS, x, 1.8, 1.51)];
  return group("walls",
    box(4, 2.4, 3, WALL, 0, 1.6, 0),
    box(0.7, 1.25, 0.06, INK, 0, 1.025, 1.51),            // the door
    ball(0.04, 0xafbff8, 0.22, 1.0, 1.56),
    ...win(-1.2), ...win(1.2));
}

function roof() {
  const shape = new THREE.Shape();
  shape.moveTo(-2.5, 0); shape.lineTo(2.5, 0); shape.lineTo(0, 1.7); shape.closePath();
  const gable = mesh(new THREE.ExtrudeGeometry(shape, { depth: 3.6, bevelEnabled: false }), INK, 0, 2.8, -1.8);
  return group("roof", gable, box(0.42, 1.1, 0.42, 0x44445d, 1.25, 3.75, -0.3));
}

function plumbing() {
  const x = 2.28, z = 0.5;   // on the right-hand wall, where the camera sees it
  return group("plumbing",
    rod(0.07, PIPE, [x, 0.8, z], [x, 2.4, z]),
    rod(0.07, PIPE, [2, 0.8, z], [x, 0.8, z]),
    rod(0.07, PIPE, [2, 2.4, z], [x, 2.4, z]),
    rod(0.055, PIPE, [x, 1.35, z], [x, 1.35, z + 0.32]),  // the tap
    rod(0.055, PIPE, [x, 1.35, z + 0.32], [x, 1.2, z + 0.32]),
    ball(0.11, JOINT, x, 0.8, z), ball(0.11, JOINT, x, 2.4, z));
}

function garden() {
  const flower = (x, z, h, color) => [rod(0.02, LEAF_LIGHT, [x, 0, z], [x, h, z]), ball(0.09, color, x, h, z)];
  return group("garden",
    rod(0.13, WOOD, [-3.6, 0, 0.5], [-3.6, 1.7, 0.5]),
    ball(0.95, LEAF, -3.6, 2.35, 0.5), ball(0.6, LEAF_LIGHT, -4.2, 1.85, 0.7), ball(0.62, LEAF_LIGHT, -3.0, 1.9, 0.4),
    ball(0.45, LEAF, 3.5, 0.38, 1.4), ball(0.35, LEAF_LIGHT, 4.0, 0.3, 1.6), ball(0.22, LEAF, 4.4, 0.2, 1.75),
    ...flower(-2.7, 2.0, 0.42, 0xdf7afe), ...flower(-2.4, 2.2, 0.32, 0x948df7), ...flower(3.2, 2.1, 0.3, 0xdf7afe));
}

export function mount(host, onFail = () => {}) {
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });   // throws without WebGL
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));           // sharper than 2x only costs battery
  const canvas = renderer.domElement;
  canvas.setAttribute("role", "img");
  canvas.setAttribute("aria-label", "Your plan drawn as a home");
  host.appendChild(canvas);

  const scene = new THREE.Scene();
  scene.add(new THREE.HemisphereLight(0xffffff, 0xc9cbd8, 1.9));
  const sun = new THREE.DirectionalLight(0xffffff, 1.6);
  sun.position.set(4, 8, 6);
  scene.add(sun);
  const ground = mesh(new THREE.CircleGeometry(5, 48), GROUND);
  ground.rotation.x = -Math.PI / 2;
  scene.add(ground);

  const parts = {};
  for (const part of [foundations(), walls(), roof(), plumbing(), garden()]) { parts[part.name] = part; scene.add(part); }

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

  function dispose() {
    if (!alive) return;
    alive = false;
    cancelAnimationFrame(queued);
    watcher.disconnect();
    scene.traverse((node) => { if (node.isMesh) { node.geometry.dispose(); node.material.dispose(); } });
    renderer.dispose();
    canvas.remove();
  }
  // The phone took the graphics memory back (another app, a locked screen): the drawn home takes over.
  canvas.addEventListener("webglcontextlost", (event) => { event.preventDefault(); if (alive) onFail(); });

  return {
    update(view) {
      const states = view.states || {};
      for (const name in parts) parts[name].visible = Boolean(states[name]);   // a family without that part
      draw();
    },
    dispose,
  };
}

// The family's architectural home in 3D. Full mode loads it by default (see stage_page.html); the drawn
// home (the SVG) stays as the fallback. The home itself is the Blender villa in coast/, built by coastal-home.js;
// this file is the camera, the weather, the marks on each part and the healing.
//
//   const home = mount(host, { onFail, onPick, onAnchors })   -> throws when the browser has no WebGL
//        onAnchors({ part: { x, y, shown } }): where each part's mark is on the picture, in the host's pixels,
//        whenever it moves. The page hangs its own buttons there (a step's "Preview" and "Completed").
//   home.update({ states, focus, lush, health })
//        states: { roof: "solid" | "cracked" | "broken" | "repaired" | null (the family has no such part), ... }
//        focus:  the part being talked about (the others fade), or null
//        lush:   1 = a green garden, 0 = a dry one
//        health: 0..1, the selected scenario's score; original rain/day/sunset weather mapping
//   home.setFrame({ x, y, w, h })   the box of the canvas the home must sit in (the page's scene), in pixels
//   home.setIntro(p)                 0 = high above the clouds, 1 = at the home: the hero's scroll drives it
//   home.dispose()
//
// What it shows: each part's state, the part in focus, the garden drying up and a subtle glow for selected
// improvements. The team's rain, clear day and sunset follow the displayed scenario's score.
// Plans: 02-DOCS/ftd/stage-casa-3d.md and 02-DOCS/ftd/stage-casa-que-mejora.md.
import { loadCoast, coastalHome } from "./coastal-home.js";
import * as THREE from "./vendor/three.module.min.js";

const FADED = new THREE.Color(0xdbe5ed), FADE = 0.12;
const REPAIRED_TINT = new THREE.Color(0x7ba782);
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
  home: { at: [0, 1.65, 0.2], from: [0.62, 0.26, 0.76], halfWidth: 6.0, halfHeight: 3.9, depth: 1.0 },
  roof: { at: [-.5, 3.1, -.5], from: [-.48, .86, .58], halfWidth: 4.5, halfHeight: 3.0, depth: .7 },
  walls: { at: [.2, 1.9, .8], from: [.85, .19, .7], halfWidth: 4.7, halfHeight: 3.0, depth: .8 },
  plumbing: { at: [1.9, .8, 2.3], from: [.55, .85, .7], halfWidth: 3.6, halfHeight: 2.6, depth: .7 },
  foundations: { at: [-.8, .6, 4.4], from: [-.28, .36, .89], halfWidth: 3.4, halfHeight: 1.8, depth: .5 },
  garden: { at: [-2.2, .8, 3.6], from: [-.85, .48, .6], halfWidth: 4.6, halfHeight: 3.1, depth: .8 },
};
// High above the clouds, looking at the sun: where the visit starts (setIntro(0)).
const FOV = 32;
const GLIDE_MS = 1550;
const HEAL_MS = 1400;
const SLOW_FRAME_MS = 45;    // a glide that averages worse than this (about 22 frames a second) is a jerky one
const HOPELESS_FRAME_MS = 150;

// A small seeded random, so the clouds and trees are the same on every visit.
let seed = 7;
const rand = () => ((seed = (seed * 16807) % 2147483647) - 1) / 2147483646;
const between = (a, b) => a + (b - a) * rand();

function mesh(geometry, color, x = 0, y = 0, z = 0) {
  const m = new THREE.Mesh(geometry, new THREE.MeshStandardMaterial({ color, roughness: .82, metalness: .02 }));
  m.position.set(x, y, z);
  m.castShadow = m.receiveShadow = true;
  m.userData.color = new THREE.Color(color);   // its own colour, before fading
  return m;
}
function group(name, ...children) {
  const g = new THREE.Group();
  g.name = name;
  g.add(...children.flat());
  return g;
}
const LAWN_TOP = 0.46;   // the ground the healing ring runs over

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
  // Tint only the existing cloud alpha: illuminated crowns and a cooler, shaded underside.
  const shade = g.createLinearGradient(0, s * .35, 0, s * .75);
  shade.addColorStop(0, "rgba(255,255,255,0)");
  shade.addColorStop(1, "rgba(89,108,137,.24)");
  g.globalCompositeOperation = "source-atop";
  g.fillStyle = shade; g.fillRect(0,0,s,s);
  g.globalCompositeOperation = "source-over";
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
        vec3 c = mix(horizon, mid, smoothstep(0.0, 0.35, y));
        c = mix(c, top, smoothstep(0.25, 0.95, y));
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

export async function mount(host, { onFail = () => {}, onPick = () => {}, onAnchors = null } = {}) {
  const assets = await loadCoast();
  seed = 7;
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
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
  renderer.setClearColor(0xeaf2ff, 0);
  // A compact studio reflection map adds readable highlights to the glass and water.
  const studio = drawn(256, (g, s) => {
    const fill = g.createLinearGradient(0, 0, 0, s);
    fill.addColorStop(0, "#4a83c7"); fill.addColorStop(.4, "#bcdcf0"); fill.addColorStop(.49, "#fff4d8"); fill.addColorStop(.55, "#a1b59b"); fill.addColorStop(1, "#3c6054");
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
  sky.dome.visible = true; // The team's score-driven weather stays inside the home's viewing area.
  scene.add(sky.dome);
  const hemi = new THREE.HemisphereLight(0xffffff, 0xc9cbd8, 1.6);
  scene.add(hemi);
  const sun = new THREE.DirectionalLight(0xffffff, 1.6);   // the key light, from the camera's side so the front reads
  sun.position.set(-8, 7, 5);
  sun.castShadow = true;
  sun.shadow.mapSize.set(innerWidth > 860 ? 2048 : 1024, innerWidth > 860 ? 2048 : 1024);
  Object.assign(sun.shadow.camera, { left: -10, right: 10, top: 10, bottom: -10, near: 1, far: 50 });
  sun.shadow.bias = -0.0006;
  sun.shadow.normalBias = 0.012;
  sun.shadow.radius = 3;
  scene.add(sun);
  const rim = new THREE.DirectionalLight(0xffffff, 0.5);   // the evening light from behind, along the edges
  rim.position.set(7, 6, -8);
  scene.add(rim);

  // Three continuous ridgelines: distant blue peaks, a middle valley and wooded foothills.
  // Vertex colours describe the slopes; the palette still follows the family's score.
  const scenery = [];
  for (let layer = 0; layer < 3; layer++) {
    const terrain = new THREE.PlaneGeometry(210,32,100,12);
    terrain.rotateX(-Math.PI/2);
    const points=terrain.attributes.position,colors=[];
    for(let v=0;v<points.count;v++) {
      const x=points.getX(v),z=points.getZ(v),across=(z+16)/32;
      const ridge=6+Math.sin(x*.063+layer*2)*3+Math.sin(x*.145+layer)*1.8+Math.sin(x*.31+layer)*.65;
      const height=ridge*Math.sin(across*Math.PI)* (layer===0?1.5:layer===1?1:.6);
      points.setY(v,height-.7);
      const shade=.74+.22*across+.04*Math.sin(x*.3);
      colors.push(shade,shade,shade);
    }
    terrain.computeVertexNormals();
    terrain.setAttribute('color',new THREE.Float32BufferAttribute(colors,3));
    const ridge=mesh(terrain,0x6b9a6f,0,0,-78+layer*24);
    ridge.material.vertexColors=true;ridge.castShadow=false;
    ridge.userData.tone='hills';ridge.userData.layer=layer;scenery.push(ridge);
  }
  // Distant headlands continue around the west and south sides of the bay.
  for(const angle of [Math.PI*.58,Math.PI,Math.PI*1.51]) {
    const ridge=scenery[0].clone();ridge.rotation.y=angle;
    ridge.position.set(-84*Math.sin(angle),-2,-84*Math.cos(angle));
    scenery.push(ridge);
  }
  scene.add(...scenery);
  const coast = coastalHome(assets, environment.texture);
  scene.add(coast.root);
  scene.fog.near = 23; scene.fog.far = 122;
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

  // A restrained cloud layer, using the team's locally drawn puffs.
  for (let i = 0; i < 8; i++) addCloud(-24 + i * 7, 5 + (i % 3) * 2, -18 - (i % 2) * 8, 8 + (i % 3) * 3, .15);
  // The original high cloud deck. The camera starts above it and passes through it on descent.
  for (let i = 0; i < 26; i++) addCloud(between(-60, 60), between(26, 38), between(-70, 40), between(14, 26), between(.25, .6));

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
  const wingShape = new THREE.Shape();
  wingShape.moveTo(0, .06);
  wingShape.bezierCurveTo(.22, .12, .55, -.02, .82, -.28);
  wingShape.quadraticCurveTo(.58, -.25, .32, -.13);
  wingShape.quadraticCurveTo(.15, -.13, 0, -.07);
  wingShape.closePath();
  const wingGeometry = new THREE.ShapeGeometry(wingShape, 16);
  wingGeometry.rotateX(-Math.PI / 2);
  const feather = new THREE.MeshStandardMaterial({ color: 0x344250, roughness: .85, side: THREE.DoubleSide });
  for (let i = 0; i < 3; i++) {
    const bird = new THREE.Group(), leftHinge = new THREE.Group(), rightHinge = new THREE.Group();
    const left = new THREE.Mesh(wingGeometry, feather), right = new THREE.Mesh(wingGeometry, feather);
    right.scale.x = -1;
    leftHinge.add(left); rightHinge.add(right);
    const body = new THREE.Mesh(new THREE.SphereGeometry(1, 16, 10), feather);
    body.scale.set(.07, .08, .24);
    const head = new THREE.Mesh(new THREE.SphereGeometry(.065, 12, 8), feather);
    head.position.set(0, .035, .22);
    const tail = new THREE.Mesh(new THREE.ConeGeometry(.075, .22, 3), feather);
    tail.rotation.x = -Math.PI / 2; tail.position.z = -.25;
    bird.add(body, head, tail, leftHinge, rightHinge);
    bird.userData = { leftHinge, rightHinge, speed: .15, height: 4.8 + i * .22, phase: i * 1.3, flap: 5.3 + i * .2 };
    bird.scale.setScalar(.40); birds.push(bird); scene.add(bird);
  }
  // The page's own state colours, so the marks match the legend.
  const css = getComputedStyle(host);
  const pins = {};
  for (const state in GLYPH) pins[state] = pinTexture(css.getPropertyValue("--" + state).trim() || STATE_COLOR[state], GLYPH[state]);
  const glow = glowTexture();

  const parts = {};
  for (const name of ["foundations", "walls", "roof", "plumbing", "garden"]) {
    const anchor = {
      foundations:[.65,.87,4.35], walls:[-.6,2.85,1.24], roof:[-.8,3.82,-.4],
      plumbing:[3.0,.85,2.85],garden:[-3.4,1.1,4.2]
    }[name];
    const made = {body:[],pin:anchor,halo:[...anchor,2.6,1.7]};
    const crk = new THREE.Group(), dmg = new THREE.Group();
    const halo = new THREE.Sprite(new THREE.SpriteMaterial({ map: glow, transparent: true, depthWrite: false, depthTest: false, blending: THREE.AdditiveBlending, opacity: .45 }));
    halo.position.set(made.halo[0], made.halo[1], made.halo[2]);
    halo.scale.set(made.halo[3], made.halo[4], 1);
    const pin = new THREE.Sprite(new THREE.SpriteMaterial({ map: pins.solid, transparent: true, depthTest: false }));
    pin.position.set(...made.pin);
    pin.renderOrder = 10;   // on top of the home, like a label
    const whole = group(name, made.body, crk, dmg, halo, pin);
    scene.add(whole);
    parts[name] = { whole, crk, dmg, halo, pin, size: made.halo[3], state: null, heal: null, pinY: made.pin[1] };
  }

  // The picture follows the pointer a little, so the home feels within reach.
  const pointer = { x: 0, y: 0, nowX: 0, nowY: 0 };
  const follow = (event) => { pointer.x = (event.clientX / innerWidth) * 2 - 1; pointer.y = (event.clientY / innerHeight) * 2 - 1; };
  addEventListener("pointermove", follow, { passive: true });

  const camera = new THREE.PerspectiveCamera(FOV, 1, 0.1, 900);
  let alive = true, queued = 0, last = 0, clock = 0;
  let view = "home", glide = null, slowGlides = 0, still = false, placed = false;
  let intro = 1, route = 0, routeWanted = 0, arrival = 0;
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
  let yawOffset = 0, pitchOffset = 0, manualOrbit = false, drag = null;
  let now = pose(view);
  canvas.tabIndex = 0;
  canvas.setAttribute("aria-label","Explore the coastal home. Drag or use arrow keys to rotate. Home resets the view.");
  const tools = document.createElement("div");
  tools.className = "orbit-tools";
  for (const [label,glyph,turn] of [["Rotate left","↶",-.5],["Reset view","⌂",0],["Rotate right","↷",.5]]) {
    const b=document.createElement("button"); b.type="button"; b.textContent=glyph;b.title=label;b.setAttribute("aria-label",label);
    b.addEventListener("click",()=>turn ? rotate(turn,0) : resetOrbit()); tools.appendChild(b);
  }
  host.appendChild(tools);
  function rotate(dx,dy) {
    manualOrbit=true;yawOffset=THREE.MathUtils.euclideanModulo(yawOffset+dx+Math.PI,2*Math.PI)-Math.PI;
    pitchOffset=THREE.MathUtils.clamp(pitchOffset+dy,-1,1);draw();
  }
  function resetOrbit(){manualOrbit=false;yawOffset=0;pitchOffset=0;draw();}
  canvas.addEventListener("keydown",e=>{
    const keys={ArrowLeft:[-.19,0],ArrowRight:[.19,0],ArrowUp:[0,.09],ArrowDown:[0,-.09]};
    if(keys[e.key]){e.preventDefault();rotate(...keys[e.key]);}
    else if(e.key==="Home"){e.preventDefault();resetOrbit();}
  });
  canvas.addEventListener("pointerdown",e=>{
    if(!e.isPrimary||e.button!==0)return;
    if(e.pointerType==="mouse") { e.preventDefault(); canvas.focus({preventScroll:true}); } drag={id:e.pointerId,x:e.clientX,y:e.clientY,active:false};canvas.setPointerCapture(e.pointerId);
  });
  canvas.addEventListener("pointermove",e=>{
    if(!drag||drag.id!==e.pointerId)return;
    const dx=e.clientX-drag.x,dy=e.clientY-drag.y;
    if(!drag.active && Math.hypot(dx,dy)<5)return;
    drag.active=true;canvas.classList.add("orbit-dragging");rotate(-dx*.009,dy*.006);drag.x=e.clientX;drag.y=e.clientY;
  });
  function release(e){if(drag?.id===e.pointerId){drag=null;canvas.classList.remove("orbit-dragging");}}
  canvas.addEventListener("pointerup",e=>{const tap=drag && drag.id===e.pointerId && !drag.active && Math.hypot(e.clientX-drag.x,e.clientY-drag.y)<5;release(e);if(tap)pickPart(e);});canvas.addEventListener("lostpointercapture",release);canvas.addEventListener("pointercancel",release);

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
    const arrivalEase = arrival * arrival * (3 - 2 * arrival);
    const from = now.from.clone().applyAxisAngle(new THREE.Vector3(0, 1, 0), yawOffset + orbit - pointer.nowX * .025 + route * .24 - arrivalEase * .48);
    from.y += pointer.nowY * .015 + arrivalEase * .1;
    from.normalize();
    const azimuth = Math.atan2(from.x, from.z);
    const elevation = THREE.MathUtils.clamp(Math.asin(from.y) + pitchOffset, .16, 1.13);
    from.set(Math.sin(azimuth)*Math.cos(elevation),Math.sin(elevation),Math.cos(azimuth)*Math.cos(elevation));
    position.copy(now.at).addScaledVector(from, now.distance * (1 + .10*(1-intro) + .15*arrivalEase));
    lookAt.copy(now.at);
    position.y = Math.max(1.45, position.y);
    if (manualOrbit) {
      const radius = Math.hypot(position.x,position.z);
      if (radius < 7.6) { position.x *= 7.6/Math.max(.001,radius); position.z *= 7.6/Math.max(.001,radius); }
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
    coast.weather(h);
    sky.uniforms.top.value.copy(mixed.top);
    sky.uniforms.mid.value.copy(mixed.mid);
    sky.uniforms.horizon.value.copy(mixed.horizon);
    sky.uniforms.sunColor.value.copy(mixed.sun);
    sky.uniforms.sunPower.value = mixed.sunPower;
    scene.fog.color.copy(mixed.horizon);
    sun.color.copy(mixed.light); sun.intensity = .55 + 2.55 * h;
    rim.color.copy(mixed.sun); rim.intensity = .18 + .72 * h;
    hemi.color.copy(mixed.sky); hemi.groundColor.copy(mixed.ground); hemi.intensity = 1.25 + .45*h;
    renderer.toneMappingExposure = .66 + .32*h;
    for (const node of scenery) {
      if (node.userData.tone === "hills") node.material.color.copy(mixed.hills).lerp(mixed.mid, .55-node.userData.layer*.2);
      if (node.userData.tone === "trees") node.material.color.copy(node.userData.color).lerp(mixed.hills, .25);
    }
    for (const cloud of clouds) cloud.material.color.copy(mixed.shade).lerp(mixed.cloud, .45 + .55 * cloud.userData.shade);
    rainAmount = Math.min(1, Math.max(0, (.38 - h) / .3));
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
    route += (routeWanted - route) * Math.min(1, dt * 4);
    arrival = Math.max(0, arrival - dt / 1.6);
    if (gap > 0 && gap < 500) watch(gap);

    if (glide) {
      if (glide.start == null) glide.start = glide.last = time;
      const g = time - glide.last;
      if (g > 0 && g < 500) { glide.spent += g; glide.frames += 1; }   // a longer gap is a hidden tab, not a slow phone
      glide.last = time;
      const t = Math.min(1, (time - glide.start) / glide.duration);
      const eased = t*t*t*(10+t*(-15+6*t));
      // Orbit around the subject instead of cutting a straight chord through the building.
      // A slight pull-back and lift make the journey visible before settling into the detail.
      const arc = Math.pow(Math.sin(Math.PI * eased), 2);
      const yaw = glide.yaw + glide.turn * eased;
      const pitch = glide.pitch + (glide.toPitch - glide.pitch) * eased + .07 * arc;
      now.at.lerpVectors(glide.from.at, glide.to.at, eased);
      now.from.set(Math.sin(yaw)*Math.cos(pitch),Math.sin(pitch),Math.cos(yaw)*Math.cos(pitch));
      now.distance = glide.from.distance + (glide.to.distance - glide.from.distance) * eased + 1.3 * arc;
      if (t >= 1) { const done = glide; glide = null; if (judge(done)) return; }
    }
    coast.animate(clock);
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

    // Life around the home: the marks float and birds fly.
    let i = 0;
    for (const name in parts) parts[name].pin.position.y = parts[name].pinY + Math.sin(clock * 1.8 + i++) * 0.07;
    const flying = health > 0.45;
    for (const bird of birds) {
      bird.visible = flying;
      if (!flying) continue;
      const b = bird.userData, a = clock * b.speed + b.phase;
      bird.position.set(-7 + Math.sin(a) * 6, b.height + Math.sin(a * 2) * .25, -9 + Math.cos(a) * 2);
      bird.rotation.y = Math.atan2(6 * Math.cos(a), -2 * Math.sin(a));
      bird.rotation.z = Math.sin(a) * .06;
      const flap = Math.sin(clock * b.flap + b.phase) * (.12 + .3 * Math.max(0, Math.sin(clock * .7 + b.phase)));
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
    if (onAnchors) reportAnchors();
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
    yawOffset=0;pitchOffset=0;manualOrbit=false;
    view = name;
    coast.focus(name);
    if (!placed || still) { glide = null; now = pose(name); placed = true; return; }
    const to=pose(name),yaw=Math.atan2(now.from.x,now.from.z);
    const turn=THREE.MathUtils.euclideanModulo(Math.atan2(to.from.x,to.from.z)-yaw+Math.PI,Math.PI*2)-Math.PI;
    glide = { from: { at: now.at.clone(), from: now.from.clone(), distance: now.distance }, to,
      yaw, turn, pitch:Math.asin(now.from.y),toPitch:Math.asin(to.from.y),
      duration:GLIDE_MS+Math.abs(turn)*220,start: null, last: 0, spent: 0, frames: 0 };
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
      const healing = !first && state === "repaired" && part.state !== "repaired";
      if (healing) {
        // Keep the old cracks on screen for the heal to close them.
        part.crk.visible = part.state === "cracked" || part.state === "broken";
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
      part.pin.visible = Boolean(focus) && focus === name;
      part.pin.material.opacity = 1;
      const size = focus === name ? 0.78 : 0.62;
      part.pin.scale.set(size, size, 1);
      part.whole.traverse((node) => {
        if (!node.isMesh) return;
        const color = node.material.color;
        if (node.userData.leaf) color.copy(node.userData.leaf[1]).lerp(node.userData.leaf[0], green);
        else color.copy(node.userData.color);
        if (state === "repaired") color.lerp(REPAIRED_TINT, 0.1);
        if (faded) color.lerp(FADED, FADE);
      });
    }
    coast.update(states); coast.weather(health < 0 ? healthWanted : health);
    first = false;
    aim(focus && states[focus] ? focus : "home");
    draw();
  }

  // Where each part's mark is on the picture, for the page's own buttons. Only told when something moved.
  const anchorPoint = new THREE.Vector3();
  let anchorKey = "";
  function reportAnchors() {
    const spots = {};
    let key = "";
    for (const name in parts) {
      parts[name].pin.getWorldPosition(anchorPoint).project(camera);
      const x = Math.round((anchorPoint.x * 0.5 + 0.5) * width), y = Math.round((-anchorPoint.y * 0.5 + 0.5) * height);
      const shown = parts[name].whole.visible && anchorPoint.z < 1 && x >= 0 && x <= width && y >= 0 && y <= height;
      spots[name] = { x, y, shown };
      key += `${x},${y},${shown};`;
    }
    if (key === anchorKey) return;
    anchorKey = key;
    onAnchors(spots);
  }

  // A tap on a part of the home goes to that part, like on the drawn one.
  const ray = new THREE.Raycaster(), point = new THREE.Vector2();
  function pickPart(event) {

    const box = canvas.getBoundingClientRect();
    point.set(((event.clientX - box.left) / box.width) * 2 - 1, -((event.clientY - box.top) / box.height) * 2 + 1);
    ray.setFromCamera(point, camera);
    const hit = ray.intersectObjects(coast.surfaces.filter(m=>m.visible && m.userData.part!=="land"),false)[0];
    if(hit && parts[hit.object.userData.part])onPick(hit.object.userData.part);
  }

  function dispose() {
    if (!alive) return;
    alive = false;
    cancelAnimationFrame(queued);
    watcher.disconnect();
    removeEventListener("pointermove", follow);
    scene.traverse((node) => { if (node.geometry) node.geometry.dispose(); if (node.material) node.material.dispose(); });
    Object.values(pins).forEach((texture) => texture.dispose());
    [glow, puff, sparkTexture].forEach((texture) => texture.dispose());
    environment.dispose();
    renderer.dispose();
    coast.dispose();tools.remove();canvas.remove();
  }
  // The phone took the graphics memory back (another app, a locked screen): the drawn home takes over.
  canvas.addEventListener("webglcontextlost", (event) => { event.preventDefault(); if (alive) onFail(); });

  function snapshot() {
    if (!alive) return null;
    try { place(); renderer.render(scene, camera); return canvas.toDataURL("image/webp", .9); }
    catch (error) { return null; }
  }
  function setTravel(progress, entering = false) {
    routeWanted = Math.min(1, Math.max(0, progress));
    if (entering && !still) arrival = 1;
    draw();
  }
  return { update, setFrame, setIntro, setTravel, snapshot, dispose };
}

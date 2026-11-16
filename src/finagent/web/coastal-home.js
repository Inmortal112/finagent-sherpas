import * as THREE from "./vendor/three.module.min.js";

const directory = new URL("./coast/", import.meta.url);
async function fetchAsset(name) {
  const response = await fetch(new URL(name, directory));
  if (!response.ok) throw new Error("Coastal home asset unavailable: " + name);
  return response;
}

// The export groups evaluated Blender surfaces by pillar, damage state and finish.
export async function loadCoast() {
  const [manifest, packed] = await Promise.all([
    fetchAsset("villa.json").then(r => r.json()),
    fetchAsset("villa.bin.gz").then(r => new Response(r.body.pipeThrough(new DecompressionStream("gzip"))).arrayBuffer()),
  ]);
  const loader = new THREE.TextureLoader();
  const plants = await Promise.all(manifest.sizes.map((_, i) => loader.loadAsync(new URL("plant-" + i + ".png", directory).href)));
  return { manifest, packed, plants };
}

export function coastalHome({ manifest, packed, plants }, environment) {
  const root = new THREE.Group(), surfaces = [], vegetation = [], materials = new Map();
  const source = new DataView(packed);
  const linear = Array.from({length:256}, (_, i) => THREE.ColorManagement.toWorkingColorSpace(new THREE.Color(i / 255, 0, 0), THREE.SRGBColorSpace).r);
  const waterTime={value:0};
  function material(finish) {
    if (materials.has(finish)) return materials.get(finish);
    const glass = finish === "glass", water = finish === "water";
    const mat = new THREE.MeshStandardMaterial({
      vertexColors: true, roughness: glass ? .09 : water ? .13 : finish === "metal" ? .38 : .83,
      metalness: glass || water ? .27 : finish === "metal" ? .55 : .015,
      transparent: glass || water, opacity: glass ? .37 : water ? .81 : 1,
      depthWrite: !glass && !water, side: THREE.DoubleSide, envMapIntensity: glass || water ? 1.35 : .32,
    });
    if (glass) mat.color.set(0xb0e0ed);
    if (water) mat.color.set(0x85f9ea);
    if (finish === "lamp") mat.emissive.set(0xffcc88);
    if (finish==="earth" || finish==="stone" || finish==="water") {
      mat.onBeforeCompile=shader=>{
        shader.uniforms.waterTime=waterTime;
        shader.vertexShader="varying vec3 vSite;\n"+shader.vertexShader;
        shader.vertexShader=shader.vertexShader.replace("#include <begin_vertex>","#include <begin_vertex>\n vSite=position;");
        shader.fragmentShader="varying vec3 vSite; uniform float waterTime;\n"+shader.fragmentShader;
        const pattern=finish==="water"
          ? "float wave=sin(vSite.x*13.+vSite.z*19.+waterTime*1.3+sin(vSite.z*6.-waterTime)); diffuseColor.rgb*=.87+.13*wave; diffuseColor.rgb+=.067*pow(max(0.,wave),15.);"
          : finish==="earth"
          ? "float groundVariation=sin(vSite.x*1.8+sin(vSite.z*2.1))*cos(vSite.z*1.15+sin(vSite.x*.7)); float grain=fract(sin(dot(floor(vSite.xz*85.),vec2(12.9898,78.233)))*43758.5453); diffuseColor.rgb*=.89+.055*groundVariation+.085*grain;"
          : "float grain=fract(sin(dot(floor(vSite*180.),vec3(12.98,78.23,38.31)))*43758.54);diffuseColor.rgb*=.958+.065*grain;";
        shader.fragmentShader=shader.fragmentShader.replace("#include <color_fragment>","#include <color_fragment>\n"+pattern);
      };
      mat.customProgramCacheKey=()=>finish;
    }
    materials.set(finish, mat); return mat;
  }
  let cursor = 0;
  for (const [part, state, finish, count] of manifest.batches) {
    const p = new Float32Array(count * 3), normals = new Int8Array(count * 3), colors = new Uint8Array(count * 3);
    for (let i = 0; i < count; i++, cursor += 12) {
      const j=i*3;
      p[j]=source.getInt16(cursor,true)/400; p[j+1]=.46+source.getInt16(cursor+4,true)/400; p[j+2]=-source.getInt16(cursor+2,true)/400;
      normals[j]=source.getInt8(cursor+6); normals[j+1]=source.getInt8(cursor+8); normals[j+2]=-source.getInt8(cursor+7);
      for(let a=0;a<3;a++) colors[j+a]=Math.round(255*linear[source.getUint8(cursor+9+a)]);
    }
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute("position",new THREE.BufferAttribute(p,3)); geometry.setAttribute("normal",new THREE.BufferAttribute(normals,3,true));
    geometry.setAttribute("color",new THREE.BufferAttribute(colors,3,true));
    const mesh = new THREE.Mesh(geometry,material(finish));
    mesh.userData={part,state,finish}; mesh.castShadow=!["glass","water","earth"].includes(finish); mesh.receiveShadow=true;
    if (finish==="water") mesh.renderOrder=1;
    root.add(mesh); surfaces.push(mesh);
  }
  if(cursor !== packed.byteLength) throw new Error("Incomplete coastal home mesh");
  // A single camera-facing quad per plant, painted from the original Cycles cutout.
  const groups = new Map();
  for (const plant of manifest.plants) {
    const [type,x,y,z,scale,states]=plant, key=type+":"+states.join(",");
    if(!groups.has(key)) groups.set(key,{type,states,positions:[],sizes:[]});
    const g=groups.get(key), [width,center]=manifest.sizes[type];
    g.positions.push(x/2,.46+(z+center*scale)/2,-y/2); g.sizes.push(width*scale/2);
  }
  const breeze={value:0}, gust={value:.4};
  // Looking at the foundations, the shrubs along the front of the terrace bow out so its wall can be seen.
  const clearing={value:0}; let clearWanted=0, lastTime=0;
  for(const {type,states,positions,sizes} of groups.values()) {
    const texture=plants[type]; texture.colorSpace=THREE.SRGBColorSpace;
    const geometry=new THREE.InstancedBufferGeometry().copy(new THREE.PlaneGeometry(1,1));
    geometry.setAttribute("plantCenter",new THREE.InstancedBufferAttribute(new Float32Array(positions),3));
    geometry.setAttribute("plantWidth",new THREE.InstancedBufferAttribute(new Float32Array(sizes),1)); geometry.instanceCount=sizes.length;
    const mat=new THREE.MeshBasicMaterial({map:texture,alphaTest:.32,side:THREE.DoubleSide});
    mat.onBeforeCompile=shader=>{
      shader.uniforms.breeze=breeze;shader.uniforms.gust=gust;shader.uniforms.clearing=clearing;
      shader.vertexShader="attribute vec3 plantCenter; attribute float plantWidth; uniform float breeze; uniform float gust; uniform float clearing;\n"+shader.vertexShader;
      shader.vertexShader=shader.vertexShader.replace("#include <begin_vertex>",`
        vec2 side = normalize(vec2(cameraPosition.z-plantCenter.z,plantCenter.x-cameraPosition.x)+vec2(.00001));
        float sway = sin(breeze*1.4+plantCenter.x*.7+plantCenter.z)*gust*.012*uv.y*uv.y;
        vec2 horizontal = side * ((position.x+sway)*plantWidth);
        vec2 front=normalize(cameraPosition.xz+vec2(.0001));
        float betweenEyeAndHouse = step(1.7,dot(plantCenter.xz,front))*step(dot(plantCenter.xz,front),length(cameraPosition.xz)+2.);
        float clearView=1.-step(2.4,plantWidth)*betweenEyeAndHouse*(1.-smoothstep(2.8,6.3,abs(dot(plantCenter.xz,vec2(front.y,-front.x)))));
        float terraceFront=step(-6.8,plantCenter.x)*step(plantCenter.x,6.6)*step(3.3,plantCenter.z)*step(plantCenter.z,6.6);
        vec3 transformed=plantCenter+vec3(horizontal.x,position.y*plantWidth,horizontal.y)*clearView*(1.-clearing*terraceFront);
      `);
    };
    const mesh=new THREE.Mesh(geometry,mat);mesh.frustumCulled=false;root.add(mesh);vegetation.push({mesh,states});
  }
  // Rear terrace and pergola finish the originally unseen elevation.
  const cube=new THREE.BoxGeometry(1,1,1), wood=new THREE.MeshStandardMaterial({color:0x946346,roughness:.72}),
        paving=new THREE.MeshStandardMaterial({color:0xd9cdb9}), fabric=new THREE.MeshStandardMaterial({color:0xffe7bd});
  function block(x,y,z,w,h,d,m) {
    const o=new THREE.Mesh(cube,m);o.position.set(x,y,z);o.scale.set(w,h,d);o.castShadow=true;o.receiveShadow=true;root.add(o);
  }
  block(-.65,.50,-3.42,4.65,.13,1.9,paving);
  for(const x of [-2.8,1.47])for(const z of [-2.7,-4.23])block(x,1.32,z,.09,1.55,.09,wood);
  for(const z of [-2.69,-4.23])block(-.66,2.11,z,4.55,.13,.12,wood);
  for(let i=0;i<21;i++)block(-2.84+i*.218,2.20,-3.46,.075,.10,1.82,wood);
  block(-.66,1.01,-3.48,1.70,.10,.58,wood);
  for(const x of [-1.35,.02])block(x,.77,-3.48,.12,.48,.44,wood);
  for(const z of [-3.98,-2.99]) {block(-.66,.72,z,1.74,.12,.31,wood);block(-.66,.811,z,1.71,.065,.29,fabric);}
  // The rear glazing faces the bay. Recessed frames, timber screens and
  // planters give the back elevation detail at the same scale as the front.
  const bronze=new THREE.MeshStandardMaterial({color:0x303b39,metalness:.52,roughness:.31});
  const reflection=new THREE.MeshStandardMaterial({color:0x537a80,metalness:.68,roughness:.18,envMapIntensity:1.15});
  function rearWindow(x,y,z,w,h) {
    block(x,y,z,w+.10,h+.10,.055,bronze);
    block(x,y,z-.045,w,h,.032,reflection);
    const panels=Math.ceil(w/.78);
    for(let i=1;i<panels;i++)block(x-w/2+i*w/panels,y,z-.078,.034,h,.055,bronze);
    block(x,y-h/2-.03,z-.067,w+.19,.075,.14,paving);
  }
  rearWindow(-.78,2.80,-2.424,4.52,.74);
  rearWindow(-.86,1.24,-2.425,3.54,1.35);
  rearWindow(3.32,1.23,-1.112,1.87,.73);
  for(let i=0;i<11;i++)block(1.68+i*.062,2.80,-2.45,.046,1.30,.070,wood);
  // The west elevation is also visible during the full orbit.
  block(-3.719,2.74,-.50,.045,.79,1.9,bronze);
  block(-3.747,2.74,-.50,.026,.70,1.82,reflection);
  for(const x of [-3.28,1.75]){
    block(x,.76,-3.93,.69,.56,.66,paving);
    for(let j=0;j<8;j++) {
      const leaf=new THREE.Mesh(new THREE.ConeGeometry(.09,.55,5),new THREE.MeshStandardMaterial({color:j%2?0x73865f:0x56795d}));
      leaf.position.set(x+.15*Math.cos(j),1.14,-3.93+.15*Math.sin(j));leaf.rotation.set(.52*Math.sin(j),0,.52*Math.cos(j));root.add(leaf);
    }
  }
  const ocean=new THREE.Mesh(new THREE.CircleGeometry(280,84),new THREE.MeshStandardMaterial({color:0x538e96,envMap:environment,roughness:.35,metalness:.24}));ocean.rotation.x=-Math.PI/2;ocean.position.y=-3.6;root.add(ocean);
  function update(states) {
    for(const mesh of surfaces) {
      const {part,state}=mesh.userData, actual=states[part]==="repaired"?"solid":states[part];
      mesh.visible=part==="land" || Boolean(actual)&&(state==="always"||state===actual);
    }
    for(const v of vegetation) {
      const state=states.garden==="repaired"?"solid":states.garden;
      v.mesh.visible=!v.states.length || Boolean(state)&&(v.states.includes(state)||v.states.includes("olive"));
      v.mesh.userData.dry=v.states.includes("olive") && state!=="solid";
    }
  }
  function weather(h) {
    for(const {mesh} of vegetation)mesh.material.color.set(mesh.userData.dry?0xb1a078:0xffffff).multiplyScalar(.65+.40*h);
    const lamp=materials.get("lamp");if(lamp)lamp.emissiveIntensity=.15+1.55*h;
    gust.value=1.45-h;
  }
  return {root,surfaces,update,weather,animate(t){breeze.value=t;waterTime.value=t;clearing.value+=(clearWanted-clearing.value)*Math.min(1,Math.max(0,t-lastTime)*3);lastTime=t;},
    focus(name){clearWanted=name==="foundations"?1:0;},dispose(){plants.forEach(t=>t.dispose());}};
}


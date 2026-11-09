// Indiana Bridges 3D – interactive viewer for the Blender-built bridge scenes (GLB exports of blender/bridge_gen.py).
// World (glTF): X = along the bridge (station, ft), Y = up, Z = right (Blender -Y). Deck riding surface at Y = 0.
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';
import { Sky } from 'three/addons/objects/Sky.js';

const params = new URLSearchParams(location.search);
const SHOT = params.get('shot');                       // headless test: ?shot=<view>&bridge=<id>
const CFG_URL = window.CFG_URL || 'bridges.json';

// ------------------------------------------------------------------ renderer / scene
const canvas = document.getElementById('c');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: !!SHOT, powerPreference: 'high-performance' });
renderer.setPixelRatio(SHOT ? 1 : Math.min(devicePixelRatio, 1.5));
renderer.setSize(innerWidth, innerHeight);
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.AgXToneMapping; renderer.toneMappingExposure = 0.95;
renderer.outputColorSpace = THREE.SRGBColorSpace;
const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0xd7e3ee, 0.00035);
const camera = new THREE.PerspectiveCamera(50, innerWidth / innerHeight, 0.3, 20000);
const controls = new OrbitControls(camera, canvas);
controls.enableDamping = true; controls.dampingFactor = 0.08; controls.maxPolarAngle = Math.PI * 0.495; controls.minDistance = 3; controls.maxDistance = 2500;

// ------------------------------------------------------------------ sky + sun (matches the Cycles Nishita setup: sun_rotation 200°, elevation per season)
let SKY = null, SUN = null, HEMI = null;
function setupSky(sun) {
  if (!SKY) { SKY = new Sky(); SKY.scale.setScalar(30000); scene.add(SKY); }
  const el = THREE.MathUtils.degToRad(sun.elev), rot = THREE.MathUtils.degToRad(sun.rot);
  // Blender direction toward the sun: (-sin rot, cos rot) in XY was checked against the render shadows -> (+x, -y); glTF: (x, z, -y)
  const dirB = new THREE.Vector3(-Math.sin(rot) * Math.cos(el), Math.cos(rot) * Math.cos(el), Math.sin(el));
  const d = new THREE.Vector3(dirB.x, dirB.z, -dirB.y).normalize();
  const u = SKY.material.uniforms; u.sunPosition.value.copy(d); u.turbidity.value = 3.5; u.rayleigh.value = 1.6; u.mieCoefficient.value = 0.004; u.mieDirectionalG.value = 0.85;
  const pmrem = new THREE.PMREMGenerator(renderer); if (scene.environment) scene.environment.dispose();
  scene.environment = pmrem.fromScene(SKY, 0.02).texture; scene.environmentIntensity = 0.45;
  if (!SUN) {
    SUN = new THREE.DirectionalLight(0xfff1dc, 2.4); SUN.castShadow = true; SUN.shadow.mapSize.set(4096, 4096);
    SUN.shadow.bias = -0.00025; SUN.shadow.normalBias = 0.35; SUN.shadow.radius = 2; scene.add(SUN); scene.add(SUN.target);
    HEMI = new THREE.HemisphereLight(0xbfd4ee, 0x546436, 0.32); scene.add(HEMI);
  }
  SUN.position.copy(d).multiplyScalar(1500);
}
function fitShadow(len, width) {
  const sc = SUN.shadow.camera; const r = Math.max(len * 0.6 + 60, 160);
  sc.left = -r; sc.right = r; sc.top = r; sc.bottom = -r; sc.near = 500; sc.far = 3200; sc.updateProjectionMatrix();
  SUN.target.position.set(len / 2, -5, 0); SUN.position.copy(SUN.target.position).add(SUN.position.clone().normalize().multiplyScalar(1500));
}

// ------------------------------------------------------------------ model helpers
function instanceSharedMeshes(root) {
  const groups = new Map(); root.updateMatrixWorld(true);
  root.traverse(o => { if (!o.isMesh) return; const k = o.geometry.uuid + '|' + o.material.uuid; if (!groups.has(k)) groups.set(k, []); groups.get(k).push(o); });
  const out = new THREE.Group(); out.name = 'instanced'; let n = 0;
  for (const [, list] of groups) {
    if (list.length < 6) continue;
    const p = list[0]; const im = new THREE.InstancedMesh(p.geometry, p.material, list.length);
    for (let i = 0; i < list.length; i++) im.setMatrixAt(i, list[i].matrixWorld);
    im.castShadow = true; im.receiveShadow = true; im.frustumCulled = false; im.name = p.name.replace(/[._]\d+$/, '') + '_instanced';
    if (p.material.alphaTest > 0) im.customDepthMaterial = new THREE.MeshDepthMaterial({ depthPacking: THREE.RGBADepthPacking, map: p.material.map, alphaTest: p.material.alphaTest, side: THREE.DoubleSide });
    out.add(im); n += list.length; for (const o of list) o.removeFromParent();
  }
  const empties = []; root.traverse(o => { if (!o.isMesh && o !== root && o.children.length === 0 && !o.isLight && !o.isCamera) empties.push(o); });
  for (const e of empties) e.removeFromParent();
  root.add(out); return n;
}
const texLoader = new THREE.TextureLoader();
let WATER_N = null;
function tuneMaterials(root) {
  if (!WATER_N) { WATER_N = texLoader.load('assets/water_n.jpg'); WATER_N.wrapS = WATER_N.wrapT = THREE.RepeatWrapping; WATER_N.repeat.set(40, 40); }
  const seen = new Set();
  root.traverse(o => {
    if (!o.isMesh) return; o.castShadow = true; o.receiveShadow = true;
    const m = o.material; if (!m || seen.has(m.uuid)) return; seen.add(m.uuid);
    const n = m.name || '';
    if (/^Leaves|^GrassClump|^ChainLink/.test(n)) { m.transparent = false; m.alphaTest = 0.45; m.side = THREE.DoubleSide; m.depthWrite = true; if (/^Leaves/.test(n)) { m.roughness = 0.7; } if (n === 'ChainLink') { m.metalness = 0.8; m.roughness = 0.45; } }
    else if (n === 'Water') { m.color.setRGB(0.07, 0.1, 0.08); m.roughness = 0.25; m.metalness = 0; m.normalMap = WATER_N; m.normalScale = new THREE.Vector2(0.3, 0.3); m.envMapIntensity = 1.0; m.userData.water = true; }
    else if (/^(Grass|DryGrass)$/.test(n)) { m.roughness = 1; m.envMapIntensity = 0.25; }
    else if (/^Concrete/.test(n)) { m.roughness = 0.85; m.envMapIntensity = 0.35; }
    else if (/^Steel|^Galvanized|^RailSteel/.test(n)) { m.envMapIntensity = 0.9; }
    m.needsUpdate = true;
  });
  root.traverse(o => { if (o.isMesh && /^(Water|FarGround)/.test(o.name)) o.castShadow = false; });
}

// ------------------------------------------------------------------ bridge loading
let CFG = null, CUR = null, ROOT = null; const ray = new THREE.Raycaster(); const DOWN = new THREE.Vector3(0, -1, 0);
function groundY(x, z) {
  if (!ROOT) return -20; ray.set(new THREE.Vector3(x, 500, z), DOWN); ray.far = 2000;
  const hits = ray.intersectObjects(ROOT.children.filter(o => /^Terrain|^FarGround/.test(o.name)), true);
  return hits.length ? hits[0].point.y : -20;
}
const say = t => { const s = document.getElementById('status'); if (s) s.textContent = t; };
async function loadBridge(id) {
  const B = CFG[id]; if (!B) throw new Error('unknown bridge ' + id);
  const loaderEl = document.getElementById('loader'); if (loaderEl) loaderEl.style.display = '';
  if (ROOT) { scene.remove(ROOT); ROOT.traverse(o => { if (o.isMesh && o.geometry) o.geometry.dispose(); }); ROOT = null; }
  say('Loading model…');
  const loader = new GLTFLoader(); loader.setMeshoptDecoder(MeshoptDecoder);
  const url = params.get('full') === '1' ? B.model_full : B.model;
  const gltf = await new Promise((res, rej) => loader.load(url, res, xhr => { if (xhr.total) say(`Loading model… ${(xhr.loaded / 1e6).toFixed(1)} / ${(xhr.total / 1e6).toFixed(1)} MB`); }, rej));
  ROOT = gltf.scene; ROOT.traverse(o => { if (o.isCamera) o.visible = false; });
  tuneMaterials(ROOT); const n = instanceSharedMeshes(ROOT); console.log('instanced', n);
  scene.add(ROOT); CUR = B;
  setupSky(B.sun); fitShadow(B.length, B.width);
  // HUD
  document.getElementById('title').textContent = B.name;
  document.getElementById('subtitle').textContent = `${B.asset} · ${B.county} County, Indiana · built from the NBI inspection report`;
  const vr = document.getElementById('viewRow'); vr.innerHTML = '';
  for (const v of Object.keys(B.cameras)) { const b = document.createElement('button'); b.textContent = v; b.dataset.view = v; b.addEventListener('click', () => { applyView(v); window.__hudMinOnPick && window.__hudMinOnPick(); }); vr.appendChild(b); }
  const lk = document.getElementById('links'); lk.innerHTML = '';
  for (const [t, h] of [['Cycles renders', B.renders], ['Download GLB', B.model_full], ['Report text', B.report], ['Gallery', '../index.html']]) { const a = document.createElement('a'); a.textContent = t; a.href = h; lk.appendChild(a); }
  const pl = document.getElementById('photoList'); pl.innerHTML = '';
  for (const p of B.photos) { const im = document.createElement('img'); im.src = p.file; im.alt = p.caption; im.loading = 'lazy'; pl.appendChild(im); const c = document.createElement('div'); c.className = 'cap'; c.textContent = `${p.caption} (compare: ${p.view} view)`; pl.appendChild(c); }
  const f = document.getElementById('facts'); f.innerHTML = `<b>${B.name}</b><ul>${B.facts.map(x => `<li>${x}</li>`).join('')}</ul>`;
  document.querySelectorAll('#bridgeRow button').forEach(b => b.classList.toggle('on', b.dataset.bridge === id));
  applyToggles();
  if (loaderEl) loaderEl.style.display = 'none'; say('');
  try { history.replaceState(null, '', '?bridge=' + id + (SHOT ? '&shot=' + SHOT : '')); } catch (e) {}
}
function applyView(name) {
  const c = CUR.cameras[name] || Object.values(CUR.cameras)[0];
  camera.position.set(...c.pos); camera.position.y = Math.max(camera.position.y, groundY(c.pos[0], c.pos[2]) + 5.5);
  camera.fov = 2 * Math.atan(18 / c.lens) * 180 / Math.PI; camera.updateProjectionMatrix();
  controls.target.set(...c.tgt); controls.update();
}
function applyToggles() {
  const trees = document.getElementById('tgTrees').checked, grass = document.getElementById('tgGrass').checked, twin = document.getElementById('tgTwin').checked;
  scene.traverse(o => {
    if (/^Tree(Leaves|Wood)/.test(o.name)) o.visible = trees;
    else if (/^GrassClump/.test(o.name)) o.visible = grass;
    else if (/^TwinBridge/.test(o.name) || /^Twin/.test(o.name)) o.visible = twin;
  });
  renderer.shadowMap.enabled = document.getElementById('tgShadows').checked; scene.traverse(o => { if (o.material) o.material.needsUpdate = true; });
}

// ------------------------------------------------------------------ main
async function main() {
  CFG = await (await fetch(CFG_URL)).json();
  const br = document.getElementById('bridgeRow');
  for (const [id, B] of Object.entries(CFG)) { const b = document.createElement('button'); b.textContent = B.name.replace(/ over .*| \(.*\)/, '').replace('WB Sagamore Parkway (US 52)', 'Sagamore Pkwy'); b.title = B.name; b.dataset.bridge = id; b.addEventListener('click', () => loadBridge(id).then(() => applyView(Object.keys(CFG[id].cameras)[0]))); br.appendChild(b); }
  for (const id of ['tgTrees', 'tgGrass', 'tgTwin', 'tgShadows']) document.getElementById(id).addEventListener('change', applyToggles);
  const photos = document.getElementById('photos'); photos.addEventListener('click', () => photos.classList.toggle('open'));
  const first = params.get('bridge') || Object.keys(CFG)[0];
  await loadBridge(first); applyView(SHOT || params.get('view') || Object.keys(CFG[first].cameras)[0]);
  window.__scene = scene; window.__camera = camera;
  const clock = new THREE.Clock(); let frames = 0; const waters = []; scene.traverse(o => { if (o.isMesh && o.material && o.material.userData.water) waters.push(o.material); });
  function animate() {
    const t = clock.getElapsedTime(); for (const w of waters) if (w.normalMap) w.normalMap.offset.set(t * 0.004, t * 0.002);
    controls.update();
    const gy = groundY(camera.position.x, camera.position.z) + 2.0; if (camera.position.y < gy) camera.position.y = gy;
    renderer.render(scene, camera); frames++; if (frames === 3) window.__ready = true;
    if (!SHOT || frames < 6) requestAnimationFrame(animate);
  }
  if (SHOT) await new Promise(r => setTimeout(r, 1500));
  animate();
}
addEventListener('resize', () => { camera.aspect = innerWidth / innerHeight; camera.updateProjectionMatrix(); renderer.setSize(innerWidth, innerHeight); });
main().catch(e => { console.error(e); say('Error: ' + e.message); });

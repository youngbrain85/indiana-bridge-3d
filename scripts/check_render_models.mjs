// Verify that every display model shows exactly the geometry of its source model.
//   node scripts/check_render_models.mjs [bridge-id ...]      (default: every registry entry with render_glb)
// For each bridge: the render_source stamp names the current model.glb (SHA-256), the mesh node names match
// one-to-one, every mesh has the same number of triangles, and every source triangle has its own display
// triangle whose corners lie within the 16-bit quantization step of that mesh (world space, any corner order).
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { MeshoptDecoder } from 'meshoptimizer';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const registry = JSON.parse(readFileSync(join(root, 'data/registry.json'), 'utf8')).bridges;
const wanted = process.argv.slice(2);
// Named bridges that are not registered yet (a fresh build) are checked at the default paths.
const bridges = wanted.length
  ? wanted.map(id => registry.find(b => b.id === id && b.model.render_glb)
      || { id, model: { glb: `bridges/${id}/model.glb`, render_glb: `bridges/${id}/model_render.glb` } })
  : registry.filter(b => b.model.render_glb);
await MeshoptDecoder.ready;
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({ 'meshopt.decoder': MeshoptDecoder });

function transform(m, x, y, z) {  // column-major 4x4
  return [m[0] * x + m[4] * y + m[8] * z + m[12], m[1] * x + m[5] * y + m[9] * z + m[13], m[2] * x + m[6] * y + m[10] * z + m[14]];
}

// name -> {tris: Float64Array (9 per triangle, world space), step: largest quantization step in metres}
async function meshes(path) {
  const doc = await io.read(path);
  const out = new Map();
  for (const node of doc.getRoot().listNodes()) {
    const mesh = node.getMesh();
    if (!mesh) continue;
    const m = node.getWorldMatrix();
    const scale = Math.max(Math.hypot(m[0], m[1], m[2]), Math.hypot(m[4], m[5], m[6]), Math.hypot(m[8], m[9], m[10]));
    const values = [];
    let step = 0;
    for (const prim of mesh.listPrimitives()) {
      const pos = prim.getAttribute('POSITION');
      const idx = prim.getIndices();
      if (pos.getNormalized()) step = Math.max(step, scale / (pos.getComponentSize() === 2 ? 32767 : 127));
      const count = idx ? idx.getCount() : pos.getCount();
      const p = [0, 0, 0];
      for (let i = 0; i < count; i++) {
        pos.getElement(idx ? idx.getScalar(i) : i, p);
        values.push(...transform(m, p[0], p[1], p[2]));
      }
    }
    out.set(node.getName(), { tris: Float64Array.from(values), step });
  }
  return { doc, out };
}

// Every source triangle must have a display triangle with all corners within the tolerance, and every display
// triangle a source triangle (both directions, so near-duplicate slivers cannot hide a missing or extra one).
function unmatched(from, to, tol) {
  const cell = Math.max(4 * tol, 0.01);
  const key = (t, i) => [0, 1, 2].map(a => Math.floor((t[i * 9 + a] + t[i * 9 + 3 + a] + t[i * 9 + 6 + a]) / 3 / cell));
  const grid = new Map();
  for (let i = 0; i < to.length / 9; i++) {
    const k = key(to, i).join(',');
    if (!grid.has(k)) grid.set(k, []);
    grid.get(k).push(i);
  }
  const near = (i, j) => Math.hypot(from[i] - to[j], from[i + 1] - to[j + 1], from[i + 2] - to[j + 2]) <= tol;
  const same = (i, j) => [0, 3, 6].every(c => [0, 3, 6].some(d => near(i * 9 + c, j * 9 + d)));
  let missing = 0;
  for (let i = 0; i < from.length / 9; i++) {
    const [x, y, z] = key(from, i);
    let found = false;
    for (let dx = -1; dx <= 1 && !found; dx++) for (let dy = -1; dy <= 1 && !found; dy++) for (let dz = -1; dz <= 1 && !found; dz++)
      found = (grid.get(`${x + dx},${y + dy},${z + dz}`) || []).some(j => same(i, j));
    if (!found) missing++;
  }
  return missing;
}

function compare(name, source, display) {
  const n = source.tris.length / 9;
  if (display.tris.length / 9 !== n) return `${name}: ${display.tris.length / 9} triangles instead of ${n}`;
  const tol = display.step + 1e-5;
  const lost = unmatched(source.tris, display.tris, tol), extra = unmatched(display.tris, source.tris, tol);
  return lost || extra ? `${name}: ${lost} source and ${extra} display triangles of ${n} have no counterpart within ${(tol * 1000).toFixed(2)} mm` : null;
}

let failures = 0;
for (const bridge of bridges) {
  const sourcePath = join(root, 'data', bridge.model.glb);
  const renderPath = join(root, 'data', bridge.model.render_glb);
  const problems = [];
  const [{ out: source }, { doc, out: display }] = await Promise.all([meshes(sourcePath), meshes(renderPath)]);
  const stamp = JSON.parse(doc.getRoot().listScenes()[0].getExtras().render_source || '{}');
  if (stamp.sha256 !== createHash('sha256').update(readFileSync(sourcePath)).digest('hex')) problems.push('stale: rebuild the display model');
  const names = [...source.keys()].sort(), shown = [...display.keys()].sort();
  if (names.join('\n') !== shown.join('\n')) problems.push('mesh names differ from model.glb');
  let triangles = 0, worst = 0;
  for (const [name, mesh] of source) {
    if (!display.has(name)) continue;
    const problem = compare(name, mesh, display.get(name));
    if (problem) problems.push(problem);
    triangles += mesh.tris.length / 9;
    worst = Math.max(worst, display.get(name).step);
  }
  failures += problems.length;
  console.log(`${problems.length ? 'FAIL' : 'ok  '} ${bridge.id}: ${source.size} meshes, ${triangles} triangles, quantization step <= ${(worst * 1000).toFixed(2)} mm`);
  for (const p of problems.slice(0, 10)) console.log('     ' + p);
}
process.exit(failures ? 1 : 0);

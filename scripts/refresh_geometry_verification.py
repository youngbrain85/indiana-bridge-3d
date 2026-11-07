"""Re-run the generic geometry checks of a bridge's geometry_verification.json after a drawing-review correction.

    python scripts/refresh_geometry_verification.py us35-deer [more bridge ids]

The original build scripts write geometry_verification.json with the SHA-256 of the GLB they exported and a set of
checks. A later correction script (scripts/correct_*.py) changes model.glb, so this re-reads the corrected GLB and
re-runs the checks that do not depend on the generator: component count, watertight meshes (each body of a mesh,
welded within 10 um), positive volumes and mesh names against the manifest. It records the new GLB hash and the
model revision, and keeps the generator's own bridge-specific checks under `checks_at_build` (they describe the
model before correction).

Requires numpy and trimesh.
"""
import hashlib
import json
import struct
import sys
from pathlib import Path

import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[1]


def meshes(path):
    data = path.read_bytes()
    length = struct.unpack_from('<I', data, 12)[0]
    gltf = json.loads(data[20:20 + length])
    blob = data[28 + length:]

    def read(i):
        a = gltf['accessors'][i]
        v = gltf['bufferViews'][a['bufferView']]
        dtype = {5126: '<f4', 5125: '<u4', 5123: '<u2', 5121: 'u1'}[a['componentType']]
        width = {'SCALAR': 1, 'VEC3': 3, 'VEC4': 4}[a['type']]
        return np.frombuffer(blob, dtype=dtype, count=a['count'] * width,
                             offset=v.get('byteOffset', 0) + a.get('byteOffset', 0)).reshape(-1, width)

    for mesh in gltf['meshes']:
        verts, faces = [], []
        for prim in mesh['primitives']:
            p = read(prim['attributes']['POSITION']).astype(np.float64)
            f = read(prim['indices']).reshape(-1, 3) if 'indices' in prim else np.arange(len(p)).reshape(-1, 3)
            faces.append(f + sum(len(x) for x in verts))
            verts.append(p)
        yield mesh['name'], np.concatenate(verts), np.concatenate(faces)


def bodies(verts, faces):
    """Split a mesh into the bodies its index buffer connects (faces sharing a vertex index), so that separate
    plates that touch face to face are checked as separate closed solids, as the build scripts made them."""
    parent = np.arange(len(verts))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for a, b, c in faces:
        ra, rb, rc = find(a), find(b), find(c)
        parent[rb] = ra
        parent[find(rc)] = ra
    roots = np.array([find(i) for i in faces[:, 0]])
    for root in np.unique(roots):
        mesh = trimesh.Trimesh(verts, faces[roots == root], process=False)
        mesh.remove_unreferenced_vertices()
        mesh.merge_vertices(digits_vertex=5)      # float32 storage: weld within 10 um
        yield mesh


def refresh(bid):
    base = ROOT / 'data/bridges' / bid
    path = base / 'geometry_verification.json'
    if not path.is_file():
        print(f'{bid}: no geometry_verification.json')
        return
    report = json.loads(path.read_text(encoding='utf-8'))
    manifest = json.loads((base / 'model_manifest.json').read_text(encoding='utf-8'))
    glb = base / 'model.glb'
    sha = hashlib.sha256(glb.read_bytes()).hexdigest()
    if report.get('glb_sha256') == sha:
        print(f'{bid}: already current')
        return
    names, watertight, positive = [], [], []
    for name, verts, faces in meshes(glb):
        names.append(name)
        parts = list(bodies(verts, faces))
        watertight.append(all(b.is_watertight for b in parts))
        positive.append(watertight[-1] and all(b.volume > 0 for b in parts))
    manifest_ids = sorted(p['id'] for p in manifest['parts'])
    if 'checks' in report and 'checks_at_build' not in report:
        report['checks_at_build'] = report.pop('checks')
    report.update(
        component_count=len(names),
        all_meshes_watertight=all(watertight),
        all_volumes_positive=all(positive),
        exported_glb_reopened=True,
        mesh_names_match_manifest=sorted(names) == manifest_ids,
        glb_sha256=sha,
        model_revision=manifest.get('revision'),
        refreshed_after_correction='Generic checks re-run on the corrected GLB by scripts/refresh_geometry_verification.py; '
                                   'checks_at_build describe the model as first built.')
    if not all(watertight):
        report['meshes_not_watertight'] = [n for n, w in zip(names, watertight) if not w]
    path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(f'{bid}: {len(names)} meshes, watertight {sum(watertight)}/{len(names)}, names match '
          f'{report["mesh_names_match_manifest"]}')


if __name__ == '__main__':
    for bid in sys.argv[1:]:
        refresh(bid)

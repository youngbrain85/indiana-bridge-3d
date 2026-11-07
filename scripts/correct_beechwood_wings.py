"""One-time, drawing-confirmed correction of the end-bent wing tops, preserving unrelated GLB buffers.

    python scripts/correct_beechwood_wings.py

Printed sheet 35 (PDF 36), WING A and WING C elevations: each wing is one 1 ft thick wall, 12 ft long at End Bent 1
and 11 ft at End Bent 4, from its approach-end tip to the span face of the bent, with a straight top:
El. 431.94 -> 431.43 (Wings A and B) and El. 420.56 -> 420.92 (Wings C and D); bottom El. 424.34 / 413.64.

The model builds each wing from a separate 9 ft / 8 ft return and the outer 1 ft strip of the 3 ft bent body. It put
the whole fall (or rise) of the top on the return, and left that strip of the bent body at deck-soffit level over its
span-side 2 ft, about 8 in below the wing top. This script moves the inner end of each return onto the straight
profile and raises the strip of the integral end-bent concrete (Pour B) to the profile by a boolean union with a
block bounded by the strip. The bent body keeps everything else (beam pockets, ledge, seats).

The end-bent bearing top plates are left as modelled (1 in at the centre against about 1 1/8 in on sheet 33): the
bearing stack is closed between the seat (El. 427.34 / 416.64) and the beam sole plate, both set from plan
elevations, and the plates are encased in Pour B. The manifest records this as a known deviation.

Requires numpy, trimesh and manifold3d.
"""
import hashlib
import json
import struct
from pathlib import Path

import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'data/bridges/beechwood'
FT = 0.3048
DECK_EDGE_FT = 16.5                       # deck and bent body meet at the deck edge; the strip lies outside it
TAG = 'wing-profile-straight-12ft-11ft'

# Bent centre line (ft from the model origin), span direction, tip and span-end top elevations, tip offset from the
# centre line, and the level below which the strip is already solid concrete.
BENTS = {1: dict(cx=0.0, span=1, tip_el=431.94, end_el=431.43, length=12.0, floor_el=430.0),
         4: dict(cx=250.0, span=-1, tip_el=420.56, end_el=420.92, length=11.0, floor_el=419.3)}


def profile(b, x_ft):
    """Top elevation (ft) of the wing at station offset x_ft (ft from the model origin)."""
    k = BENTS[b]
    span_end = k['cx'] + k['span'] * 1.5
    tip = span_end - k['span'] * k['length']
    return k['tip_el'] + (k['end_el'] - k['tip_el']) * (x_ft - tip) / (span_end - tip)


def z_m(el):
    return (el - 390.0) * FT


def correct():
    mp = BASE / 'model_manifest.json'
    manifest = json.loads(mp.read_text(encoding='utf-8'))
    if manifest.get('wing_profile_correction') == TAG:
        print('Already corrected.')
        return
    path = BASE / 'model.glb'
    original = path.read_bytes()
    length = struct.unpack_from('<I', original, 12)[0]
    gltf = json.loads(original[20:20 + length])
    binary = bytearray(original[28 + length:])
    before = hashlib.sha256(original).hexdigest()
    parts = {p['id']: p for p in manifest['parts']}
    meshes = {m['name']: m for m in gltf['meshes']}

    def read(ai):
        a = gltf['accessors'][ai]
        view = gltf['bufferViews'][a['bufferView']]
        dtype = {5126: '<f4', 5125: '<u4', 5123: '<u2', 5121: 'u1'}[a['componentType']]
        count = {'SCALAR': 1, 'VEC3': 3, 'VEC4': 4}[a['type']]
        return np.frombuffer(binary, dtype=dtype, count=a['count'] * count,
                             offset=view.get('byteOffset', 0) + a.get('byteOffset', 0)).copy().reshape(-1, count)

    def append(array, kind, component):
        while len(binary) % 4:
            binary.append(0)
        data = array.tobytes()
        view = len(gltf['bufferViews'])
        gltf['bufferViews'].append(dict(buffer=0, byteOffset=len(binary), byteLength=len(data)))
        binary.extend(data)
        a = dict(bufferView=view, componentType=component, count=len(array), type=kind)
        if kind == 'VEC3':
            a.update(min=array.min(axis=0).tolist(), max=array.max(axis=0).tolist())
        gltf['accessors'].append(a)
        return len(gltf['accessors']) - 1

    changes = []
    for b, k in BENTS.items():
        # Wing returns: the top corners at the bent end go onto the straight profile.
        for side in ('L', 'R'):
            pid = f'b{b}_wing_{side}'
            prim = meshes[pid]['primitives'][0]
            v = read(prim['attributes']['POSITION']).astype(np.float64)
            inner_x = v[:, 0].max() if k['span'] == 1 else v[:, 0].min()
            top = v[:, 2] > v[:, 2].min() + 1.0
            at_inner = top & np.isclose(v[:, 0], inner_x, atol=1e-4)
            if at_inner.sum() != 2 or not np.allclose(v[at_inner, 2], z_m(k['end_el']), atol=2e-3):
                raise ValueError(f'{pid}: unexpected original wing top at the bent end')
            v[at_inner, 2] = z_m(profile(b, inner_x / FT))
            solid = trimesh.Trimesh(vertices=v, faces=read(prim['indices']).reshape(-1, 3), process=False)
            if not solid.is_watertight or solid.volume <= 0:
                raise ValueError(f'{pid}: invalid corrected wing')
            prim['attributes']['POSITION'] = append(v.astype('<f4'), 'VEC3', 5126)
            p = parts[pid]
            p['bounds_m'] = solid.bounds.round(6).tolist()
            p['volume_m3'] = round(float(solid.volume), 6)
            p['dimensions'].update(top_el_at_tip_ft=k['tip_el'], top_el_at_bent_end_ft=round(profile(b, inner_x / FT), 3))
            p['note'] = (p.get('note', '') + f' Top corrected to the straight {k["length"]:.0f} ft wing profile, '
                         f'El. {k["tip_el"]} to {k["end_el"]}, sheet 35.').strip()
            meshes[pid]['extras'].update(p)
            changes.append(pid)
        # Bent body: the outer 1 ft strip on each side rises to the wing profile.
        pid = f'b{b}_integral'
        prim = meshes[pid]['primitives'][0]
        body = trimesh.Trimesh(vertices=read(prim['attributes']['POSITION']).astype(np.float64),
                               faces=read(prim['indices']).reshape(-1, 3), process=False)
        if not body.is_watertight:
            raise ValueError(f'{pid}: not watertight')
        half = body.bounds[1][1]
        x0, x1 = (k['cx'] - 1.5) * FT, (k['cx'] + 1.5) * FT
        blocks = []
        for sign in (1, -1):
            y_in, y_out = sign * DECK_EDGE_FT * FT, sign * half
            ya, yb = sorted((y_in, y_out))
            zb = z_m(k['floor_el'])
            corners = [(x0, ya, zb), (x1, ya, zb), (x1, yb, zb), (x0, yb, zb),
                       (x0, ya, z_m(profile(b, x0 / FT))), (x1, ya, z_m(profile(b, x1 / FT))),
                       (x1, yb, z_m(profile(b, x1 / FT))), (x0, yb, z_m(profile(b, x0 / FT)))]
            faces = [(0, 2, 1), (0, 3, 2), (4, 5, 6), (4, 6, 7), (0, 1, 5), (0, 5, 4),
                     (3, 7, 6), (3, 6, 2), (0, 4, 7), (0, 7, 3), (1, 2, 6), (1, 6, 5)]
            block = trimesh.Trimesh(vertices=np.array(corners), faces=np.array(faces), process=False)
            if block.volume < 0:
                block.invert()
            blocks.append(block)
        merged = trimesh.boolean.union([body] + blocks, engine='manifold')
        if not merged.is_watertight or merged.volume <= body.volume:
            raise ValueError(f'{pid}: invalid union')
        color = read(prim['attributes']['COLOR_0'])[0]
        prim['attributes'] = {'POSITION': append(merged.vertices.astype('<f4'), 'VEC3', 5126),
                              'COLOR_0': append(np.tile(color, (len(merged.vertices), 1)).astype('u1'), 'VEC4', 5121)}
        gltf['accessors'][prim['attributes']['COLOR_0']]['normalized'] = True
        prim['indices'] = append(merged.faces.reshape(-1, 1).astype('<u4'), 'SCALAR', 5125)
        p = parts[pid]
        added = merged.volume - body.volume
        p['bounds_m'] = merged.bounds.round(6).tolist()
        p['volume_m3'] = round(float(merged.volume), 6)
        p['note'] = (p.get('note', '') + f' Outer 1 ft strips raised to the wing top profile (+{added:.3f} m3), '
                     'sheets 32-35.').strip()
        meshes[pid]['extras'].update(p)
        changes.append(pid)
        print(f'{pid}: strips raised, +{added:.3f} m3')

    gltf['buffers'][0]['byteLength'] = len(binary)
    while len(binary) % 4:
        binary.append(0)
    encoded = json.dumps(gltf, ensure_ascii=True, separators=(',', ':')).encode()
    encoded += b' ' * ((-len(encoded)) % 4)
    out = (struct.pack('<III', 0x46546c67, 2, 28 + len(encoded) + len(binary)) +
           struct.pack('<II', len(encoded), 0x4e4f534a) + encoded + struct.pack('<II', len(binary), 0x004e4942) + binary)
    backup = ROOT / 'data/fem_research'
    backup.mkdir(exist_ok=True)
    (backup / 'beechwood_before_wing_correction.glb').write_bytes(original)
    (backup / 'manifest_before_wing_correction.json').write_bytes(mp.read_bytes())
    path.write_bytes(out)
    manifest['wing_profile_correction'] = TAG
    manifest['revision'] = '2.2-wing-profile'
    manifest['wing_profile_correction_record'] = dict(
        source_pdf_pages=[33, 34, 36], printed_sheets=[32, 33, 35], changed_parts=changes,
        profiles={'End Bent 1, Wings A and B': 'El. 431.94 at the approach tip to 431.43 at the span face, 12 ft',
                  'End Bent 4, Wings C and D': 'El. 420.56 at the approach tip to 420.92 at the span face, 11 ft'},
        before_glb_sha256=before, after_glb_sha256=hashlib.sha256(out).hexdigest())
    deviations = [d for d in manifest.get('known_deviations', []) if d.get('id') != 'end-bent-bearing-top-plate']
    deviations.append(dict(
        id='end-bent-bearing-top-plate', parts='b1_bearing_*_top, b4_bearing_*_top', source='sheet 33 (PDF 34)',
        deviation='Tapered top plate is 1 in thick at its centre (about 0.88-1.13 in at its ends); the plan gives 1 in '
                  'to 1 1/4 in, about 1 1/8 in at the centre.',
        reason='The bearing stack is closed between the seat (El. 427.34 / 416.64) and the beam sole plate, both set '
               'from plan elevations; the plates are encased in Pour B and are not inspectable.'))
    manifest['known_deviations'] = deviations
    mp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(manifest['wing_profile_correction_record']))


if __name__ == '__main__':
    correct()

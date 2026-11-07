"""One-time, drawing-confirmed correction of the clear roadway and the deck overlay limits, preserving unrelated GLB
buffers.

    python scripts/correct_sr1_six_mile_review.py

Drawing evidence (contract B-44532, drawings.pdf; printed sheet numbers equal PDF page numbers):

- Sheet 4, Bridge Location Information Table: bridge width out to out 47 ft 1 1/2 in, roadway width curb-to-curb
  44 ft.
- Sheet 7, Typical Section: 44'-0" Clear Roadway (10 + 12 + 12 + 10 ft), a 1'-6" barrier on each side and
  47'-1 1/2" out to out of copings; the polymeric overlay is drawn between the barrier toes. Plan: the warranted
  polymer overlay (bridge deck) and the polymer overlay on the RCBAs cover the 10 + 12 ft lanes on each side of the
  S.R. 1 line, i.e. the 44 ft roadway, and "Clean & install new silicone sealant in exist. Type 1-A joints" is called
  at both bridge/approach interfaces.
- Sheet 8, quantities: 352 SYS warranted polymer overlay on the deck = 44 ft x 72 ft / 9; 279 SYS polymer overlay
  on the approaches = 2 x 44 ft x 28.5 ft (mean of the 20.5 and 36.5 ft edges) / 9 = 278.7.
- Sheet 3, general notes: new thin deck overlay 3/8 in of warranted polymer; approaches overlaid with non-warranted
  polymer; Type 1-A existing joint work.

The model built each barrier 50 mm inside the deck edge (a generic offset of the geometry library), so the traffic
faces were at Y = +/-6.67465 m and the clear roadway was 13.3493 m (43 ft 9.6 in) instead of 44 ft (13.4112 m). The
six barrier panels move 30.95 mm outward so that the toe of each traffic face is 22 ft (6.7056 m) from the
centreline and the back face is 23.5 ft (7.1628 m) from it, 3/4 in inside the coping edge; this closes the sheet 7
chain 44' + 2 x 1'-6" + 2 x 3/4" = 47'-1 1/2". The move is a rigid translation along the skewed panel end lines and
down the 1.56 % crossfall, so each panel keeps its skewed ends and stays seated on the slab.

The overlay ran across the full 47'-1 1/2" deck, through the barrier bases, and over the bridge-side half of each
joint-seal envelope (seal top 8.5 mm inside the overlay). It is rebuilt with the same 3/8 in thickness, crown and
crossfall between the barrier toes (|Y| <= 22 ft) and stopped at the edge of each seal envelope, so that the resealed
Type 1-A joints stay exposed. The 15 mm cut-back is the half-width of the existing 30 mm seal envelope (a display
assumption of the model), not a new dimension.

The approach (RCBA) polymer overlay is recorded in the approach notes but not modelled: its thickness is not given
on any sheet. Barrier height and profile, the joint seals, the deck and the approach slabs are unchanged.

Requires numpy and trimesh.
"""
import hashlib
import json
import struct
from pathlib import Path

import numpy as np
import trimesh

FT, IN = .3048, .0254

ROOT = Path(__file__).resolve().parents[1]
BID = 'sr1-six-mile'
BASE = ROOT / 'data/bridges' / BID
TAG = 'clear-roadway-44ft-overlay-limits'
REVISION = '1.1-clear-roadway-overlay-limits'

LENGTH = (72 + 7.25 / 12) * FT            # sheet 4, out to out (as built by build_sr1_six_mile.py)
WIDTH = (47 + 1.5 / 12) * FT              # sheets 4 and 7, out to out of copings
SKEW, CROSSFALL, GRADE = 20, .0156, 6.0   # model skew (NBI), sheet 7 crossfall, assumed local elevation
OVERLAY_T = 3 / 8 * IN                    # sheet 3
BARRIER_BASE = 1.5 * FT                   # sheet 7, 1'-6"
OLD_EDGE = WIDTH / 2 - .05                # library offset used by Model.barriers
TOE = 22 * FT                             # sheet 4 and 7: 44 ft clear roadway
BACK = TOE + BARRIER_BASE                 # 23.5 ft; 3/4 in inside the 23 ft 6 3/4 in coping edge
RAILS = ['rail_-1_0', 'rail_-1_1', 'rail_-1_2', 'rail_1_0', 'rail_1_1', 'rail_1_2']
TOL = 2e-5


def to_native(v):
    """glTF Y-up vertices (as stored, no node matrix) -> native X station, Y transverse, Z up."""
    return np.column_stack([v[:, 0], -v[:, 2], v[:, 1]])


def to_gltf(v):
    return np.column_stack([v[:, 0], v[:, 2], -v[:, 1]])


def slab(u0, u1, y0, y1, thick, offset, k):
    """Watertight crowned slab, as bridge_geometry.Model.slab: skewed ends u = X - k*Y, top at surface + offset."""
    yy = [y0, 0.0, y1]
    profile = [(y, -thick) for y in yy] + [(y, 0.0) for y in reversed(yy)]
    n = len(profile)
    stations = np.linspace(u0, u1, max(2, int((u1 - u0) / .6) + 1))
    v = [(u + k * y, y, GRADE - CROSSFALL * abs(y) + offset + z) for u in stations for y, z in profile]
    f = []
    for s in range(len(stations) - 1):
        for j in range(n):
            a, b = s * n + j, s * n + (j + 1) % n
            f.extend([(a, b, b + n), (a, b + n, a + n)])
    cap = [(0, 1, 4), (0, 4, 5), (1, 2, 3), (1, 3, 4)]
    last = (len(stations) - 1) * n
    f.extend(t[::-1] for t in cap)
    f.extend(tuple(i + last for i in t) for t in cap)
    mesh = trimesh.Trimesh(np.array(v, dtype=np.float64), np.array(f), process=False)
    if not mesh.is_winding_consistent:
        raise ValueError('slab winding is inconsistent')
    if mesh.volume < 0:
        mesh.invert()
    return mesh


def correct():
    mp = BASE / 'model_manifest.json'
    raw_manifest = mp.read_bytes()
    manifest = json.loads(raw_manifest)
    if manifest.get('clear_roadway_correction') == TAG:
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
    if any('matrix' in n or 'rotation' in n or 'translation' in n or 'scale' in n for n in gltf['nodes']):
        raise ValueError('Unexpected node transform; this model stores glTF-axis vertices without node matrices.')

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

    def native_mesh(pid):
        prim = meshes[pid]['primitives'][0]
        v = to_native(read(prim['attributes']['POSITION']).astype(np.float64))
        return trimesh.Trimesh(vertices=v, faces=read(prim['indices']).reshape(-1, 3), process=False)

    k = -np.tan(np.radians(SKEW))           # station u = X - k*Y, as in bridge_geometry.Model.sx

    def surface(y):
        return GRADE - CROSSFALL * np.abs(y)

    changes = []

    # 1. Barriers: rigid move outward to the 44 ft clear roadway (sheets 4 and 7).
    dy = TOE - (OLD_EDGE - BARRIER_BASE)
    for pid in RAILS:
        side = 1 if pid.startswith('rail_1_') else -1
        solid = native_mesh(pid)
        v = solid.vertices
        inner, outer = np.abs(v[:, 1]).min(), np.abs(v[:, 1]).max()
        if (not solid.is_watertight or abs(inner - (OLD_EDGE - BARRIER_BASE)) > TOL or abs(outer - OLD_EDGE) > TOL
                or np.sign(v[:, 1]).min() != np.sign(v[:, 1]).max() or np.sign(v[0, 1]) != side
                or abs((v[:, 2] - surface(v[:, 1])).min()) > TOL):
            raise ValueError(f'{pid}: unexpected original barrier position')
        shift = np.array([k * side * dy, side * dy, -CROSSFALL * dy])
        moved = v + shift
        new = trimesh.Trimesh(vertices=moved, faces=solid.faces, process=False)
        if (abs(np.abs(moved[:, 1]).min() - TOE) > TOL or abs(np.abs(moved[:, 1]).max() - BACK) > TOL
                or abs((moved[:, 2] - surface(moved[:, 1])).min()) > TOL or not new.is_watertight):
            raise ValueError(f'{pid}: invalid moved barrier')
        prim = meshes[pid]['primitives'][0]
        prim['attributes']['POSITION'] = append(to_gltf(moved).astype('<f4'), 'VEC3', 5126)
        p = parts[pid]
        p['bounds_m'] = new.bounds.round(6).tolist()      # volume unchanged by a rigid move
        p['pdf_pages'] = sorted(set(p['pdf_pages']) | {4, 7})
        p['dimensions'].update(traffic_face_toe_offset_m=round(TOE, 6), back_face_offset_m=round(BACK, 6),
                               clear_roadway_m=round(2 * TOE, 6), clear_roadway_ft=44)
        p['note'] = (p.get('note', '') + ' Moved 30.95 mm outward: traffic-face toe 22 ft from the centreline (44 ft '
                     'clear roadway) and back face 3/4 in inside the coping edge, sheets 4 and 7.').strip()
        meshes[pid]['extras'].update(p)
        changes.append(pid)

    # 2. Deck overlay: between the barrier toes and clear of the joint-seal envelopes (sheets 3, 7 and 8).
    pid = 'overlay'
    old = native_mesh(pid)
    ov = old.vertices
    u = ov[:, 0] - k * ov[:, 1]
    dz = ov[:, 2] - surface(ov[:, 1])
    if (not old.is_watertight or abs(np.abs(ov[:, 1]).max() - WIDTH / 2) > TOL
            or abs(u.min() + LENGTH / 2) > TOL or abs(u.max() - LENGTH / 2) > TOL
            or abs(dz.min()) > TOL or abs(dz.max() - OVERLAY_T) > TOL):
        raise ValueError('overlay: unexpected original overlay')
    seal_half = []
    for jid, sign in (('joint_0', -1), ('joint_1', 1)):
        jv = native_mesh(jid).vertices
        ju = jv[:, 0] - k * jv[:, 1]
        if abs((ju.min() + ju.max()) / 2 - sign * LENGTH / 2) > TOL:
            raise ValueError(f'{jid}: joint not centred on the deck end line')
        seal_half.append((ju.max() - ju.min()) / 2)
    if not np.allclose(seal_half, .015, atol=TOL):
        raise ValueError('joint seal envelope is not the expected 30 mm display width')
    cut = .015
    overlay = slab(-LENGTH / 2 + cut, LENGTH / 2 - cut, -TOE, TOE, OVERLAY_T, OVERLAY_T, k)
    if not overlay.is_watertight or overlay.volume <= 0:
        raise ValueError('overlay: invalid rebuilt overlay')
    prim = meshes[pid]['primitives'][0]
    color = read(prim['attributes']['COLOR_0'])[0]
    prim['attributes'] = {'POSITION': append(to_gltf(overlay.vertices).astype('<f4'), 'VEC3', 5126),
                          'COLOR_0': append(np.tile(color, (len(overlay.vertices), 1)).astype('u1'), 'VEC4', 5121)}
    gltf['accessors'][prim['attributes']['COLOR_0']]['normalized'] = True
    prim['indices'] = append(overlay.faces.reshape(-1, 1).astype('<u4'), 'SCALAR', 5125)
    p = parts[pid]
    plan_area = 2 * TOE * (LENGTH - 2 * cut)
    p['bounds_m'] = overlay.bounds.round(6).tolist()
    p['volume_m3'] = round(float(overlay.volume), 9)
    p['pdf_pages'] = sorted(set(p['pdf_pages']) | {3, 7, 8})
    p['dimensions'].update(width_m=round(2 * TOE, 6), width_ft=44, length_along_station_m=round(LENGTH - 2 * cut, 6),
                           plan_area_m2=round(plan_area, 3))
    p['note'] = ('Existing overlay is removed before the proposed layer; no duplicated old layer. Limited to the 44 ft '
                 'roadway between the barrier toes (sheet 7 section and plan; sheet 8: 352 SYS = 44 ft x 72 ft) and '
                 'stopped at the edge of each Type 1-A joint-seal envelope so the resealed joints stay exposed '
                 '(sheets 3 and 7).')
    meshes[pid]['extras'].update(p)
    changes.append(pid)
    removed = WIDTH * LENGTH - plan_area
    print(f'overlay: {WIDTH * LENGTH:.3f} -> {plan_area:.3f} m2 plan, {old.volume:.6f} -> {overlay.volume:.6f} m3')

    # 3. Approaches: record the drawn polymer overlay (no geometry: its thickness is not given).
    annotated = []
    for pid in ('approach_0', 'approach_1'):
        p = parts[pid]
        p['pdf_pages'] = sorted(set(p['pdf_pages']) | {3, 7, 8})
        p['dimensions'].update(polymer_overlay='non-warranted polymer, thickness not given', polymer_overlay_width_ft=44,
                               polymer_overlay_both_approaches_sys=279)
        p['note'] = (p.get('note', '') + ' The top within the 44 ft roadway receives a non-warranted polymer overlay '
                     '(sheets 3 and 7; sheet 8: 279 SYS for both approaches); not modelled as a layer because its '
                     'thickness is not given.').strip()
        meshes[pid]['extras'].update(p)
        annotated.append(pid)

    for d in manifest.get('detail_coverage', []):
        if d.get('feature') == 'Drawing envelope and proposed overlay':
            d['detail'] = (d['detail'] + ' The deck overlay covers the 44 ft roadway between the barrier toes and stops '
                           'at the joint-seal envelopes; the approach polymer overlay is recorded in the approach notes, '
                           'not modelled (thickness not given).')
            for s in ('Primary PDF p.8',):
                if s not in d['sources']:
                    d['sources'].append(s)

    gltf['buffers'][0]['byteLength'] = len(binary)
    while len(binary) % 4:
        binary.append(0)
    encoded = json.dumps(gltf, ensure_ascii=True, separators=(',', ':')).encode()
    encoded += b' ' * ((-len(encoded)) % 4)
    out = (struct.pack('<III', 0x46546c67, 2, 28 + len(encoded) + len(binary)) +
           struct.pack('<II', len(encoded), 0x4e4f534a) + encoded + struct.pack('<II', len(binary), 0x004e4942) + binary)
    backup = ROOT / 'data/fem_research'
    backup.mkdir(exist_ok=True)
    (backup / f'{BID}_before_review_correction.glb').write_bytes(original)
    (backup / f'{BID}_manifest_before_review_correction.json').write_bytes(raw_manifest)
    path.write_bytes(out)
    manifest['clear_roadway_correction'] = TAG
    previous = manifest.get('revision')
    manifest['revision'] = REVISION
    manifest['clear_roadway_correction_record'] = dict(
        source_pdf_pages=[3, 4, 7, 8], printed_sheets=[3, 4, 7, 8], previous_revision=previous,
        changed_parts=changes, annotated_parts=annotated,
        values={'clear roadway (sheets 4, 7)': '44 ft 0 in = 13.4112 m; was 13.3493 m',
                'barrier traffic-face toe / back face from centreline': '6.7056 / 7.1628 m; was 6.67465 / 7.13185 m',
                'barrier move': 'rigid, 30.95 mm outward along the skewed end lines and down the 1.56 % crossfall',
                'deck overlay width (sheets 7, 8)': f'44 ft = 13.4112 m; was {WIDTH:.4f} m (full deck)',
                'deck overlay ends': 'stopped 15 mm short of each joint centre line, at the edge of the 30 mm seal '
                                     'envelope (seal top was 8.5 mm inside the overlay)',
                'overlay plan area removed m2': round(removed, 3),
                'approach polymer overlay (sheets 3, 7, 8)': '44 ft wide, 279 SYS for both; recorded, not modelled'},
        before_glb_sha256=before, after_glb_sha256=hashlib.sha256(out).hexdigest())
    text = json.dumps(manifest, indent=2)
    if b'\r\n' in raw_manifest:
        text = text.replace('\n', '\r\n')
    if raw_manifest.endswith(b'\n'):
        text += '\r\n' if b'\r\n' in raw_manifest else '\n'
    mp.write_bytes(text.encode('utf-8'))
    print(json.dumps(manifest['clear_roadway_correction_record']))


if __name__ == '__main__':
    correct()

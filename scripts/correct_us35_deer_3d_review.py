"""Fourth correction of US 35 over Deer Creek (us35-deer), from the 3D placement review: the wing roots no longer
duplicate the end-bent concrete. Runs after scripts/correct_us35_deer_review.py, _review_2.py and _review_3.py and
keeps every GLB buffer it does not replace.

    python scripts/correct_us35_deer_3d_review.py [--base DIR] [--backup DIR]

Source: drawings.pdf (INDOT B-45063 / Des 1900048, document 9721578); printed sheet numbers equal PDF page numbers.
Native axes (revision 1.2 on): X along increasing station (east, X = 0 at Sta. 1271+60), Y positive to the left of
increasing station (north), Z up from El. 837.11; bent lines q = X - tan(15 deg) Y. Each 3'-10" bent spans
q = u -/+ 0.604808 m along X (u = -/+17.526 m), the deck ends are at q = -/+17.8943 m.

Finding US35-S01 (minor, structure), RESOLVED.
- Measured on revision 1.3: each of the four 12 ft wing prisms started at the span face of the bent, so its first
  1.209616 m (along X) lay inside the end bent: 0.4394-0.4409 m3 inside cap_1 / cap_2, 0.4234-0.4507 m3 inside the
  outer closure bay (integral_infill_*_0 / _8) and 0.1034-0.1100 m3 inside backwall_0 / backwall_1, 0.968-1.000 m3
  per wing, 3.939 m3 counted twice. The wing's outer face lay on the cap end face over 1.44 m2 per wing, which
  rendered striped.
- How the sheets divide the concrete:
  * Sheet 17 (WINGWALL DETAILS, bill of materials "for two wingwalls"): 5.7 CY of Class C concrete. A 1 ft wall from
    the back face of the bent to the tip, 12'-0" less 3'-10"/cos 15 = 8.0315 ft along the roadway, bottom El. 841.88
    / 844.59 (level) to the T/El. at the bent centre line on the +2.35 % grade, gives 5.703 CY for Wings C + D
    (Bent 2) and 5.538 CY for Wings A + B; the full 12 ft would be 8.3-8.5 CY. The billed wingwall is therefore the
    projection beyond the back face of the bent.
  * Sheet 13 (plan, Bent 1 shown, Bent 2 similar): the bent is 43'-0" x 3'-10"; the wings are 1'-0" thick, 12'-0"
    from the tip to the span-face corner, their outer face continuing the bent end; inside the bent the wing's inner
    face is a hidden line.
  * Sheet 14 (bent elevations): the end-bent outline runs from El. 841.88 / 844.59 up to the wing T/El. at both bent
    ends (Wing A / D 851.21 / 854.16, Wing B / C 851.45 / 853.91), so the root of each wing inside the 3'-10" bent,
    including the part above the deck soffit, is drawn as end-bent concrete. Sheet 17's elevation draws the back
    face of the bent (with its pavement-ledge step) through the wing as a hidden line.
- Fix: each wing part is trimmed to the back face of the bent: it runs from q = u -/+ 0.604808 m to the unchanged tip,
  2.447984 m (8'-0 3/8") along the roadway, with the same thickness, outer face, bottom and top plane (positions
  only, same topology). The root inside the bent belongs to the bent parts that already held most of it: cap_N up to
  the seat, the outer closure bay from the seat to the deck soffit (span face to deck end) and backwall_N from the
  seat to its top (deck end to back face). The only root volume no bent part held, the 1 ft x 1.2096 m column from
  the deck soffit (and the back-strip top) up to the wing top, is added to the outer closure bay (span face to deck
  end) and to backwall_N (deck end to back face): inside the 1 ft wing column their top is now the wing top (T/El.
  at the bent centre line, +2.35 % along the roadway, level across the wall), elsewhere unchanged. No dimension is
  new: the wing top, thickness, outer face, back-face line and deck-end line are the existing drawn values.
- Result: no volume is shared, the total concrete of these parts equals the former union, the wing outer face
  continues the bent end face edge to edge (no coplanar overlap), and each wing bears against the back face of its
  bent over its full height (cap back face below the seat, back strip above).

Rebuilt (6): integral_infill_0_0, integral_infill_0_8, integral_infill_1_0, integral_infill_1_8, backwall_0,
backwall_1 (new POSITION, COLOR_0 and index accessors). Moved vertices (4): wing_0_-1, wing_0_1, wing_1_-1, wing_1_1
(new POSITION accessor; indices and colours kept). Added / removed: none. Every other mesh, accessor and the
original binary data are kept byte for byte. source_ledger.json records no value that changes ("12 ft wings" is still
the drawn wall); FEM does not use the changed parts (cap_1 / cap_2 are unchanged).

Requires numpy and trimesh (manifold3d for the boolean checks), plus the three earlier us35_deer correction scripts.
"""
import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

import manifold3d
import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import correct_us35_deer_review as first  # noqa: E402
import correct_us35_deer_review_2 as second  # noqa: E402
import correct_us35_deer_review_3 as third  # noqa: E402

BID = first.BID
BASE = ROOT / 'data/bridges' / BID
BACKUP = ROOT / 'data/fem_research'
TAG_KEY = 'review_correction_3d'
TAG = 'wing-roots-partitioned-into-end-bent'
RECORD_KEY = 'review_correction_record_3d'
REVISION = '1.4-3d-review'
PREVIOUS_TAG_KEY, PREVIOUS_TAG, PREVIOUS_REVISION = 'review_correction_3', third.TAG, third.REVISION
EXPECTED_GLB_SHA256 = '06f820f3b5d218041452ccec46e335a3b3385ca6a10f53efd74b71cf45741db3'   # revision 1.3 output
FT, IN, TAN, TOL, SLAB = first.FT, first.IN, first.TAN, first.TOL, first.SLAB
HT = first.HALF_THICK                      # half of the 3'-10" bent along X, 0.604808 m (sheets 13, 15)
HALF = third.HALF                          # deck end, q = 17.8943 m (sheet 11)
WING_LEN, WING_T = first.WING_LEN, first.WING_T          # 12'-0" tip to span-face corner, 1'-0" (sheets 13, 17)
GRADE, DATUM_EL = second.GRADE, second.DATUM_EL
CY = (3 * FT) ** 3
SHEET17_CY = 5.7                           # sheet 17 bill of materials, Class C concrete for two wingwalls
OUTER_BAYS = (0, 8)                        # integral_infill_{b}_0 (north end) and _8 (south end)
ORIENT_NOTE = second.ORIENT_NOTE


def surface(x, y):
    return first.surface(x, y)


def q_of(v):
    return v[:, 0] - TAN * v[:, 1]


def sx(q, y):
    return q + TAN * np.asarray(y)


def wing_top(spec):
    """Wing top: T/El. at the bent centre line, +2.35 % along the roadway, level across the wall (rev. 1.2 rule)."""
    z_cl, x_cl = spec['z_cl'], spec['x_cl']
    return lambda x: z_cl + GRADE * (np.asarray(x) - x_cl)


def build_bay(q_span, q_de, y_in, y_end, seat, spec):
    """Outer closure bay: seat to deck soffit between the beam flange edge y_in and the bent end y_end, and seat to the
    wing top inside the 1 ft wing column (y between the wing's inner face and the bent end)."""
    top = wing_top(spec)
    yi = spec['y_inner']
    if y_end > y_in:          # north end: wing column at high Y
        profile = [(y_in, 0), (y_end, 0), (y_end, 2), (yi, 2), (yi, 1), (y_in, 1)]
        caps = [(1, 2, 3), (1, 3, 4), (1, 4, 5), (1, 5, 0)]
    else:                     # south end: wing column at low Y
        profile = [(y_end, 0), (y_in, 0), (y_in, 1), (yi, 1), (yi, 2), (y_end, 2)]
        caps = [(0, 1, 2), (0, 2, 3), (0, 3, 4), (0, 4, 5)]

    def point(s, y, lev):
        x = float(sx(s, y))
        return x, y, (seat, float(surface(x, y)) - SLAB, float(top(x)))[lev]

    return first.prism(sorted([q_span, q_de]), profile, point, caps=caps)


def build_backwall(b, y0, y1, seat, south, north):
    """Back strip over the 9 in ledge (third.build_backwall) with the wing columns at both bent ends raised to the
    wing tops. Levels: 0 seat, 1 deck soffit, 2 slab soffit (ledge), 3 south wing top, 4 north wing top."""
    u, end = first.BENTS[b]['u'], first.BENTS[b]['end']
    qq = sorted([u + end * HT, end * HALF])
    lo, hi = third.ledge_zone(b)
    ys, yn = south['y_inner'], north['y_inner']
    if not (y0 < ys < lo < 0.0 < hi < yn < y1):
        raise ValueError(f'backwall_{b}: unexpected wing columns {ys}, {yn} against the ledge zone {lo}, {hi}')
    profile = [(y0, 0), (ys, 0), (lo, 0), (0.0, 0), (hi, 0), (yn, 0), (y1, 0), (y1, 4), (yn, 4), (yn, 1), (hi, 1),
               (hi, 2), (0.0, 2), (lo, 2), (lo, 1), (ys, 1), (ys, 3), (y0, 3)]
    caps = [(0, 1, 15), (0, 15, 16), (0, 16, 17),          # south wing column
            (1, 2, 13), (1, 13, 14), (1, 14, 15),          # south of the ledge zone, deck-soffit top
            (2, 3, 12), (2, 12, 13), (3, 4, 11), (3, 11, 12),   # ledge, crowned
            (5, 9, 10), (5, 10, 11), (5, 11, 4),           # north of the ledge zone, deck-soffit top
            (6, 7, 8), (6, 8, 9), (6, 9, 5)]               # north wing column
    ts, tn = wing_top(south), wing_top(north)

    def point(s, y, lev):
        x = float(sx(s, y))
        z = float(surface(x, y))
        return x, y, (seat, z - SLAB, z - third.THICK, float(ts(x)), float(tn(x)))[lev]

    return first.prism(qq, profile, point, caps=caps)


def correct(base=BASE, backup=BACKUP):
    mp = base / 'model_manifest.json'
    raw_manifest = mp.read_bytes()
    manifest = json.loads(raw_manifest)
    if manifest.get(TAG_KEY) == TAG:
        print('Already corrected.')
        return
    path = base / 'model.glb'
    original = path.read_bytes()
    before = hashlib.sha256(original).hexdigest()

    def expect(ok, what):
        if not ok:
            raise ValueError(f'{BID}: unexpected starting model ({what})')

    expect(manifest.get(PREVIOUS_TAG_KEY) == PREVIOUS_TAG and manifest.get('revision') == PREVIOUS_REVISION,
           f'run scripts/correct_us35_deer_review_3.py first (revision {manifest.get("revision")})')
    expect(TAG_KEY not in manifest, f'{TAG_KEY} already holds {manifest.get(TAG_KEY)}')
    expect(before == EXPECTED_GLB_SHA256 == manifest['review_correction_record_3']['after_glb_sha256'],
           f'model.glb SHA-256 {before} is not the revision 1.3 output')

    length = struct.unpack_from('<I', original, 12)[0]
    gltf = json.loads(original[20:20 + length])
    binary = bytearray(original[28 + length:])
    parts = {p['id']: p for p in manifest['parts']}
    meshes = {m['name']: m for m in gltf['meshes']}
    expect(set(parts) == set(meshes) and len(meshes) == 72, 'part list')
    expect(not any(k in n for n in gltf['nodes'] for k in ('matrix', 'rotation', 'translation', 'scale')),
           'node transforms')

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

    def native(pid):
        m = meshes[pid]
        expect(len(m['primitives']) == 1, f'{pid} primitive')
        prim = m['primitives'][0]
        mesh = trimesh.Trimesh(vertices=first.to_native(read(prim['attributes']['POSITION']).astype(np.float64)),
                               faces=read(prim['indices']).reshape(-1, 3), process=False)
        expect(mesh.is_watertight and mesh.volume > 0, f'{pid} not a closed solid')
        return mesh

    # ---- Starting state (revision 1.3). ----
    old, new, values, specs = {}, {}, {}, {}
    for pid, (plan, b, side) in second.WINGS.items():
        k = first.BENTS[b]
        u, end, span, bottom = k['u'], k['end'], k['span'], k['bottom']
        cap = old.setdefault(f'cap_{b + 1}', native(f'cap_{b + 1}'))
        cv = cap.vertices
        y_end = cv[:, 1].max() if side > 0 else cv[:, 1].min()
        m = old[pid] = native(pid)
        v, q = m.vertices, q_of(m.vertices)
        q_span, q_tip = u + span * HT, u + span * HT + end * WING_LEN
        root = np.abs(q - q_span) < TOL
        y_inner = v[:, 1].min() if side > 0 else v[:, 1].max()
        yc = (v[:, 1].min() + v[:, 1].max()) / 2
        spec = dict(plan=plan, b=b, side=side, y_inner=float(y_inner), y_end=float(y_end), bottom=bottom,
                    z_cl=(second.WING_TOP_EL[plan] - DATUM_EL) * FT, x_cl=float(sx(u, yc)))
        top = v[:, 2] > bottom + .5
        expect(len(v) == 8 and root.sum() == 4 and (np.abs(q - q_tip) < TOL).sum() == 4, f'{pid}: not the 12 ft prism')
        expect(abs(np.abs(v[:, 1] - y_end).max() - WING_T) < TOL and np.abs(v[:, 1] - y_end).min() < TOL,
               f'{pid}: outer face not on the bent end')
        expect(np.abs(v[~top, 2] - bottom).max() < TOL and np.abs(v[top, 2] - wing_top(spec)(v[top, 0])).max() < TOL,
               f'{pid}: bottom / top not the revision 1.2 rule')
        expect(abs(cv[:, 2].min() - bottom) < TOL and abs(q_of(cv).min() - (u - HT)) < TOL
               and abs(q_of(cv).max() - (u + HT)) < TOL, f'cap_{b + 1} limits')
        specs[pid] = spec

    seats = {b: old[f'cap_{b + 1}'].vertices[:, 2].max() for b in (0, 1)}
    for b, k in first.BENTS.items():
        u, end, span = k['u'], k['end'], k['span']
        cv = old[f'cap_{b + 1}'].vertices
        y0, y1, seat = cv[:, 1].min(), cv[:, 1].max(), seats[b]
        pid = f'backwall_{b}'
        m = old[pid] = native(pid)
        ref = third.build_backwall(b, y0, y1, seat)
        expect(len(m.vertices) == len(ref.vertices) == 24
               and max(np.abs(ref.vertices - p).max(axis=1).min() for p in m.vertices) < 2e-5,
               f'{pid}: not the revision 1.3 ledge strip')
        for j in OUTER_BAYS:
            pid = f'integral_infill_{b}_{j}'
            m = old[pid] = native(pid)
            v, q = m.vertices, q_of(m.vertices)
            topv = v[:, 2] > seat + .1
            expect(len(v) == 8 and np.abs(np.abs(q - u) - np.where(np.abs(q - (u + span * HT)) < TOL, HT,
                                                                    abs(end * HALF - u))).max() < TOL
                   and np.abs(v[~topv, 2] - seat).max() < TOL
                   and np.abs(v[topv, 2] - surface(v[topv, 0], v[topv, 1]) + SLAB).max() < TOL,
                   f'{pid}: not the span-face-to-deck-end bay with its top at the deck soffit')
            wing = [w for w, s in specs.items() if s['b'] == b and min(v[:, 1]) - TOL < s['y_inner'] < max(v[:, 1])
                    + TOL]
            expect(len(wing) == 1, f'{pid}: wing column')
            specs[wing[0]]['bay'] = pid

    # ---- Rebuild. ----
    for pid, s in specs.items():
        k = first.BENTS[s['b']]
        u, end, span = k['u'], k['end'], k['span']
        q_back = u + end * HT
        v = old[pid].vertices.copy()
        root = np.abs(q_of(v) - (u + span * HT)) < TOL
        top = v[:, 2] > s['bottom'] + .5
        v[root, 0] = sx(q_back, v[root, 1])
        v[root & top, 2] = wing_top(s)(v[root & top, 0])
        new[pid] = trimesh.Trimesh(vertices=v, faces=old[pid].faces, process=False)
        tip_x = v[~root, 0]
        values[pid] = dict(plan_name=s['plan'], q_m=sorted([round(q_back, 6), round(q_back + end * (WING_LEN - 2 * HT),
                                                                                       6)]),
                           length_along_roadway_m=round(WING_LEN - 2 * HT, 6),
                           root_q_was_m=round(u + span * HT, 6), tip_x_m=[round(float(tip_x.min()), 6),
                                                                        round(float(tip_x.max()), 6)],
                           y_m=[round(float(v[:, 1].min()), 6), round(float(v[:, 1].max()), 6)])

        bay = s['bay']
        b = s['b']
        ov = old[bay].vertices
        y_in = ov[:, 1].min() if s['side'] > 0 else ov[:, 1].max()
        new[bay] = build_bay(u + span * HT, end * HALF, float(y_in), s['y_end'], seats[b], s)
        values[bay] = dict(wing_column_y_m=sorted([round(s['y_inner'], 6), round(s['y_end'], 6)]),
                           wing_column_top=f'{s["plan"]} top, El. {second.WING_TOP_EL[s["plan"]]} at the bent centre '
                                           'line, +2.35 %', added_m3=round(float(new[bay].volume - old[bay].volume), 6))
    for b in (0, 1):
        cv = old[f'cap_{b + 1}'].vertices
        south = next(s for s in specs.values() if s['b'] == b and s['side'] < 0)
        north = next(s for s in specs.values() if s['b'] == b and s['side'] > 0)
        pid = f'backwall_{b}'
        new[pid] = build_backwall(b, cv[:, 1].min(), cv[:, 1].max(), seats[b], south, north)
        values[pid] = dict(wing_columns_y_m=[sorted([round(s['y_inner'], 6), round(s['y_end'], 6)])
                                             for s in (south, north)],
                           added_m3=round(float(new[pid].volume - old[pid].volume), 6))

    # ---- Checks: closed solids; no shared volume; the former union is kept; contacts. ----
    def solid(m):
        w = m.copy()
        w.merge_vertices(digits_vertex=7)
        return manifold3d.Manifold(manifold3d.Mesh64(vert_properties=np.asarray(w.vertices, dtype=np.float64),
                                                     tri_verts=np.asarray(w.faces, dtype=np.uint64)))

    def inter(a, b):
        return float((solid(a) ^ solid(b)).volume())

    def union(ms):
        out = solid(ms[0])
        for m in ms[1:]:
            out = out + solid(m)
        return out

    for pid, m in new.items():
        expect(m.is_watertight and m.is_winding_consistent and m.volume > 0, f'{pid} rebuilt solid')
        # Check what will be stored: float32 glTF positions.
        new[pid] = trimesh.Trimesh(vertices=first.to_native(first.to_gltf(m.vertices).astype('<f4').astype(np.float64)),
                                   faces=m.faces, process=False)
        expect(new[pid].is_watertight and new[pid].volume > 0, f'{pid} stored solid')
    totals = {}
    for pid, s in specs.items():
        b, bay = s['b'], s['bay']
        bent_old = [old[f'cap_{b + 1}'], old[bay], old[f'backwall_{b}']]
        shared = [inter(old[pid], m) for m in bent_old]
        removed = float(old[pid].volume - new[pid].volume)
        column = removed - sum(shared)
        values[pid].update(shared_before_m3=dict(zip([f'cap_{b + 1}', bay, f'backwall_{b}'],
                                                     [round(x, 6) for x in shared])),
                           shared_before_total_m3=round(sum(shared), 6), removed_root_m3=round(removed, 6),
                           root_above_bent_top_m3=round(column, 6),
                           volume_m3=[round(float(old[pid].volume), 6), round(float(new[pid].volume), 6)])
        for other in (f'cap_{b + 1}', bay, f'backwall_{b}'):
            ov = inter(new[pid], new.get(other, old[other]))
            expect(ov < 2e-5, f'{pid} still overlaps {other} by {ov:.6f} m3')
        totals[pid] = (sum(shared), column)
        # The wing root face (q = back face) bears on the cap back face below the seat and the back strip above.
        k = first.BENTS[b]
        q_back = k['u'] + k['end'] * HT
        face = new[pid].vertices[np.abs(q_of(new[pid].vertices) - q_back) < 1e-6]
        expect(len(face) == 4, f'{pid}: root face')
    for b in (0, 1):
        ids = [f'cap_{b + 1}', f'backwall_{b}'] + [f'integral_infill_{b}_{j}' for j in OUTER_BAYS] + \
              [p for p, s in specs.items() if s['b'] == b]
        before_union = union([old[i] for i in ids])
        after_union = union([new.get(i, old[i]) for i in ids])
        after = sum(float(new.get(i, old[i]).volume) for i in ids)
        expect(abs(before_union.volume() - after) < 2e-5 and (before_union - after_union).volume() < 2e-5
               and (after_union - before_union).volume() < 2e-5,
               f'bent {b + 1}: volume {after:.6f} or region differs from the former union {before_union.volume():.6f}')
        for i in ids:
            for j in ids:
                if i < j:
                    ov = inter(new.get(i, old[i]), new.get(j, old[j]))
                    expect(ov < 2e-5, f'{i} / {j} overlap {ov:.6f} m3')
        values[f'bent_{b + 1}'] = dict(union_before_m3=round(float(before_union.volume()), 6), sum_after_m3=round(after, 6),
                                       sum_before_m3=round(sum(float(old[i].volume) for i in ids), 6))
    for b in (0, 1):
        ws = [p for p, s in specs.items() if s['b'] == b]
        proj = sum(float(new[p].volume) for p in ws)
        values[f'bent_{b + 1}'].update(wings_beyond_back_face_m3=round(proj, 6), wings_beyond_back_face_cy=round(
            proj / CY, 3), sheet17_two_wingwalls_cy=SHEET17_CY)

    # ---- Write accessors. ----
    def store(pid, mesh, positions_only):
        prim = meshes[pid]['primitives'][0]
        if positions_only:
            expect(len(mesh.vertices) == read(prim['attributes']['POSITION']).shape[0], f'{pid} vertex count')
            prim['attributes']['POSITION'] = append(first.to_gltf(mesh.vertices).astype('<f4'), 'VEC3', 5126)
        else:
            color = read(prim['attributes']['COLOR_0'])[0]
            prim['attributes'] = {
                'POSITION': append(first.to_gltf(mesh.vertices).astype('<f4'), 'VEC3', 5126),
                'COLOR_0': append(np.tile(color, (len(mesh.vertices), 1)).astype('u1'), 'VEC4', 5121)}
            gltf['accessors'][prim['attributes']['COLOR_0']]['normalized'] = True
            prim['indices'] = append(mesh.faces.reshape(-1, 1).astype('<u4'), 'SCALAR', 5125)
        p = parts[pid]
        p['bounds_m'] = mesh.bounds.round(6).tolist()
        p['volume_m3'] = round(float(mesh.volume), 9)

    for pid in sorted(new):
        store(pid, new[pid], positions_only=pid.startswith('wing_'))

    # ---- Manifest. ----
    def pages(pid, extra):
        parts[pid]['pdf_pages'] = sorted(set(parts[pid]['pdf_pages']) | set(extra))

    for pid, s in specs.items():
        b = s['b']
        k = first.BENTS[b]
        q_back = k['u'] + k['end'] * HT
        val = values[pid]
        p = parts[pid]
        p['note'] += (
            f' Rev. 1.4 (3D review S01): the part now runs from the back face of the bent (q = {q_back:+.6f} m) to the '
            f'unchanged tip, {WING_LEN - 2 * HT:.4f} m (8\'-0 3/8") along the roadway: the projection that sheet 17 '
            'bills as wingwall concrete (5.7 CY for two wingwalls; this projection gives '
            f'{values["bent_2"]["wings_beyond_back_face_cy"]:.2f} CY for Wings C and D and '
            f'{values["bent_1"]["wings_beyond_back_face_cy"]:.2f} CY for Wings A and B). The drawn wall is still '
            '12\'-0" from the tip to the span-face corner of the bent (sheets 13, 17); its root inside the 3\'-10" '
            'bent is end-bent concrete (sheet 14 draws the bent up to the wing T/El. at its ends) and is modelled by '
            f'cap_{b + 1}, {s["bay"]} and backwall_{b}. Before, the root ({val["removed_root_m3"]:.4f} m3) shared '
            f'{val["shared_before_total_m3"]:.4f} m3 with them and its outer face lay on the cap end face.')
        p['dimensions'].update(length_m=round(WING_LEN - 2 * HT, 6),
                               length_basis='modelled part: back face of the bent to the tip, parallel to the '
                                            'roadway (the projection billed on sheet 17)',
                               drawn_length_m=round(WING_LEN, 6),
                               drawn_length_basis='tip to span-face corner of the bent, parallel to the roadway '
                                                  '(sheets 13, 17); the root inside the bent is modelled with the bent',
                               root_parts=[f'cap_{b + 1}', s['bay'], f'backwall_{b}'])
        pages(pid, [13, 14, 17])
        bay = s['bay']
        parts[bay]['note'] += (
            f' Rev. 1.4 (3D review S01): inside the 1 ft column of {s["plan"]} (Y = '
            f'{min(s["y_inner"], s["y_end"]):.4f} to {max(s["y_inner"], s["y_end"]):.4f} m) the bay rises from the '
            f'deck soffit to the wing top (El. {second.WING_TOP_EL[s["plan"]]} at the bent centre line, +2.35 %), '
            f'taking over the root of the wing above the deck soffit ({values[bay]["added_m3"]:.4f} m3); the wing '
            'part now starts at the back face of the bent. Sheet 14 draws the bent up to the wing T/El. at its ends; '
            'sheet 17 bills only the projection as wingwall.')
        parts[bay]['dimensions'] = dict(parts[bay].get('dimensions', {}), wing_column_y_m=values[bay]['wing_column_y_m'],
                                        wing_column_top_el_at_bent_cl_ft=second.WING_TOP_EL[s['plan']])
        pages(bay, [14, 17])
    for b in (0, 1):
        pid = f'backwall_{b}'
        parts[pid]['note'] += (
            ' Rev. 1.4 (3D review S01): inside the 1 ft wing columns at both bent ends (Y = '
            + ' and '.join(f'{lo:.4f} to {hi:.4f}' for lo, hi in values[pid]['wing_columns_y_m'])
            + ' m) the strip rises to the wing tops, taking over the root of the wings above its former top '
            f'({values[pid]["added_m3"]:.4f} m3); the wing parts now start at the back face of the bent and bear on '
            'it (sheets 14, 17).')
        parts[pid]['dimensions'].update(wing_columns_y_m=values[pid]['wing_columns_y_m'])
        pages(pid, [14, 17])
    for pid in new:
        meshes[pid]['extras'].update(parts[pid])
    for item in manifest.get('detail_coverage', []):
        if item.get('feature') == 'Integral support topology':
            item['detail'] += (' Wing roots inside the 3\'-10" bent are end-bent concrete: cap, outer closure bays and '
                               'back strips, which rise to the wing top in the 1 ft wing column; the wing parts run '
                               'from the back face of the bent to the tip, the projection billed on sheet 17, so no '
                               'volume is counted twice (sheets 13, 14, 17; revision 1.4).')
            if 'Primary PDF p.16' not in item['sources']:
                item['sources'].append('Primary PDF p.16')
    expect(set(parts) == set(meshes) == {p['id'] for p in manifest['parts']} and len(parts) == 72, 'final part list')
    for pid, m in new.items():
        expect(np.abs(np.array(parts[pid]['bounds_m']) - m.bounds).max() < 1e-6, f'{pid} bounds')

    while len(binary) % 4:
        binary.append(0)
    gltf['buffers'][0]['byteLength'] = len(binary)
    encoded = json.dumps(gltf, ensure_ascii=True, separators=(',', ':')).encode()
    encoded += b' ' * ((-len(encoded)) % 4)
    out = (struct.pack('<III', 0x46546c67, 2, 28 + len(encoded) + len(binary)) +
           struct.pack('<II', len(encoded), 0x4e4f534a) + encoded + struct.pack('<II', len(binary), 0x004e4942) + binary)
    backup.mkdir(parents=True, exist_ok=True)
    (backup / f'{BID}_before_3d_review.glb').write_bytes(original)
    (backup / f'{BID}_manifest_before_3d_review.json').write_bytes(raw_manifest)
    path.write_bytes(out)

    manifest[TAG_KEY] = TAG
    manifest['revision'] = REVISION
    changed = sorted(new)
    shared = {p: round(t[0], 6) for p, t in totals.items()}
    manifest[RECORD_KEY] = dict(
        review='3D placement review, round 4',
        source_pdf_pages=[13, 14, 15, 16, 17], printed_sheets=[13, 14, 15, 16, 17],
        previous_revision=PREVIOUS_REVISION,
        native_axes='as revision 1.2: X along increasing station (east, X = 0 at Sta. 1271+60), Y positive to the left '
                    'of increasing station (north), Z up from El. 837.11; q = X - tan(15 deg) Y',
        findings=[dict(
            id='US35-S01', verdict='resolve',
            summary='the four wing roots duplicated the end-bent concrete: 0.968-1.000 m3 per wing inside cap, outer '
                    'closure bay and back strip (3.939 m3 counted twice), and 1.44 m2 of wing outer face on each cap '
                    'end face; the wings are trimmed to the back face of the bent and their root above the deck '
                    'soffit is part of the outer closure bay and back strip',
            basis='sheet 17 bills 5.7 CY for two wingwalls = the projection beyond the back face of the bent (5.703 CY '
                  'Wings C+D, 5.538 CY Wings A+B; the full 12 ft would be 8.3-8.5 CY); sheet 13 draws the 43\'-0" x '
                  '3\'-10" bent with the wing inner face hidden inside it; sheet 14 draws the bent outline up to the '
                  'wing T/El. at its ends; sheet 17 draws the back face of the bent through the wing as a hidden line',
            shared_before_m3=shared, shared_before_total_m3=round(sum(shared.values()), 6))],
        changed_parts=changed, moved_vertex_parts=sorted(specs), rebuilt_parts=sorted(set(new) - set(specs)),
        added_parts=[], removed_parts=[], decisions=[], kept_deviations=[],
        values=values, before_glb_sha256=before, after_glb_sha256=hashlib.sha256(out).hexdigest())
    text = json.dumps(manifest, indent=2)
    if b'\r\n' in raw_manifest:
        text = text.replace('\n', '\r\n')
    if raw_manifest.endswith(b'\n'):
        text += '\r\n' if b'\r\n' in raw_manifest else '\n'
    mp.write_bytes(text.encode('utf-8'))
    print(json.dumps({k: v for k, v in manifest[RECORD_KEY].items() if k != 'values'}, indent=1))
    for k in sorted(values):
        print(k, json.dumps(values[k]))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--base', type=Path, default=BASE, help='bridge folder (default: the repository copy)')
    parser.add_argument('--backup', type=Path, default=BACKUP, help='backup folder')
    args = parser.parse_args()
    correct(args.base, args.backup)

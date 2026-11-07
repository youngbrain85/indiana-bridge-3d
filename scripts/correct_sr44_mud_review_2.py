"""Second drawing-confirmed correction of the SR 44 / Mud Creek model, run after correct_sr44_mud_review.py.

    python scripts/correct_sr44_mud_review_2.py

All sheets are INDOT B-38321 (data/bridges/sr44-mud/drawings.pdf); printed sheet number = PDF page number. Native axes:
X station from 617+95, Y toward beam 1 (north, left of increasing station; sheet 17), Z = elevation - 885 ft (metres).

Regular diaphragm connections, sheet 20 TYPICAL DIAPHRAGM DETAIL. The PL 1/2 x 7 1/4 in connection plate is welded to the
beam web; the dimension chain 1 1/2 in + 3 in + 1 3/4 in runs from the channel end through the two bolt columns to the
plate edge, so the C15x33.9 stops 1 in off each web face and the bolt columns are 2 1/2 and 5 1/2 in off the web face
(vector check on the sheet: web face, channel end, columns and plate edge at 0, 1.01, 2.51, 5.50 and 7.24 in). The model
ran the channels web face to web face, started the plates at the beam centre line (inside the web), put the columns
1.255 and 4.255 in off the web face, and centred the 1/2 in plate on the back of the channel web (6.35 mm overlap). The
plates keep their sheet 17 station (their mid-plane is the diaphragm line located by correct_sr44_mud_review.py) and now
start at the web face; each channel is shortened 1 in at both ends and moves 1/4 in up-station so that its web bears on
the plate face; the 16 bolts are rebuilt at the dimensioned columns with their grip through plate and channel web.

End diaphragm underside, sheet 24 SECTIONS A-A and B-B ("1/2 in EXPANDED POLYSTYRENE HORIZONTAL FACE") and sheet 23
ELEVATION (diaphragm cast on the stepped existing cap): the semi-integral diaphragm sits 1/2 in above the cap top. The
builder's profile had only two underside vertices, so the underside ran straight between the outer bearing seats and
cut up to 0.089 m into the stepped cap at mid-width. The underside now follows the five model cap steps + 1/2 in.

Pavement ledge, sheet 24 SECTIONS A-A/B-B ("6 in PAVEMENT LEDGE", approach slab 1'-2" deep over it), sheet 23 PLAN
("6 in PVMT. LEDGE" along the rear face) and sheet 33 PAVEMENT LEDGE DETAIL (6 in ledge; approach slab 2 in deeper for
2'-0" from the joint, then a 45 deg taper to the 1'-0" slab). The ledge is added to each end diaphragm mesh (no new part
id): 6 in beyond the deck end, top 1'-2" below the road surface, the full 46'-6" width. The approach slab soffits are
lowered 2 in over the first 2'-0" with the 45 deg return. Horizontal offsets are measured along the roadway like the
builder's deck end and diaphragm faces; the ledge rear face then lies within 1 mm of the cap rear face (1'-3" from the
bent centre line, sheet 24).

Requires numpy, trimesh and manifold3d.
"""
import hashlib
import json
import math
import struct
from pathlib import Path

import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'data/bridges/sr44-mud'
FT, IN = .3048, .0254
K = math.tan(math.radians(15))
C, S = math.cos(math.radians(15)), math.sin(math.radians(15))
PREVIOUS_TAG = 'review-2026-11-diaphragms-caps-coping-wings'
TAG = 'review-2026-11-second-check-connections-end-bents'
TOL = 3e-5                                   # float32 vertex tolerance (m)

# Builder constants (scripts/build_sr44_mud.py) and the station shift of correct_sr44_mud_review.py.
HALF = (151 + 1 / 12) / 2 * FT
YS = np.array([21, 14, 7, 0, -7, -14, -21]) * FT
TW = .490 * IN
SEAT = np.array([[904.36, 904.36, 904.51, 904.65, 904.46, 904.27, 904.27],
                 [904.61, 904.61, 904.79, 904.97, 904.82, 904.67, 904.67],
                 [904.79, 904.79, 904.96, 905.13, 904.97, 904.81, 904.81],
                 [904.79, 904.79, 904.96, 905.13, 904.97, 904.81, 904.81]])
BEARINGS = np.array([-74.75, -25, 25, 74.75]) * FT
STEPS = [(-24, -12.5, 6), (-12.5, -1.75, 4), (-1.75, 1.75, 3), (1.75, 12.5, 2), (12.5, 24, 0)]  # cap steps (ft, seat)
REGULAR_ROWS = [-65, -44.75, -7.5, 7.5, 44.75, 65]
BOLT_R = .4375 * IN

# Sheet 20 typical diaphragm detail.
PLATE_T, PLATE_W = .5 * IN, 7.25 * IN
END_GAP = 1.0 * IN                                  # channel end to web face
COLUMNS = (2.5 * IN, 5.5 * IN)                      # bolt columns from the web face
CHANNEL_WEB = .4 * IN
# Sheets 23, 24 and 33.
POLY = .5 * IN                                      # horizontal expanded polystyrene under the end diaphragm
LEDGE = 6 * IN                                      # pavement ledge width
LEDGE_TOP = 14 * IN                                 # approach slab depth over the ledge (1'-2")
THICK_LEN, THICK_DROP = 2 * FT, 2 * IN              # thickened approach end (sheet 33)


def el(feet):
    return (np.asarray(feet) - 885) * FT


def grade(x):
    t = np.asarray(x) / FT + 100
    inside = 908.00 + .0082 * t + (-.0029 - .0082) * t * t / 400
    return el(np.where(t < 0, 908.00 + .0082 * t, np.where(t > 200, 908.53 - .0029 * (t - 200), inside)))


def surface(x, y):
    return grade(x) - .02 * np.abs(y)


def rod(a, b, r, sections=12):
    a, b = np.asarray(a, float), np.asarray(b, float)
    m = trimesh.creation.cylinder(r, np.linalg.norm(b - a), sections=sections)
    m.apply_transform(trimesh.geometry.align_vectors([0, 0, 1], b - a))
    m.apply_translation((a + b) / 2)
    return m


def hexbolt(a, b, r):
    """Shank, hex head beyond a and nut beyond b, as in the builder."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    v = (b - a) / np.linalg.norm(b - a)
    return trimesh.util.concatenate([rod(a, b, r), rod(a - v * .012, a, r * 1.55, 6), rod(b, b + v * .017, r * 1.55, 6)])


def solid(v, f):
    return trimesh.Trimesh(vertices=v, faces=f, process=False)


def sweep(stations, profile_tris, point):
    """Closed solid: profile vertex k at station s is point(s, k); profile_tris triangulate the profile polygon."""
    n = len(point(stations[0], None))
    v = np.array([p for s in stations for p in point(s, None)], float)
    f = []
    for i in range(len(stations) - 1):
        for k in range(n):
            a, b = i * n + k, i * n + (k + 1) % n
            f += [(a, b, b + n), (a, b + n, a + n)]
    f += [tuple(t[::-1]) for t in profile_tris] + [tuple(np.asarray(t) + (len(stations) - 1) * n) for t in profile_tris]
    m = solid(v, np.array(f))
    if m.volume < 0:
        m.invert()
    return m


def box(x0, x1, y0, y1, z0, z1):
    m = trimesh.creation.box([x1 - x0, y1 - y0, z1 - z0])
    m.apply_translation([(x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2])
    return m


def correct():
    mp = BASE / 'model_manifest.json'
    raw_manifest = mp.read_bytes()
    manifest = json.loads(raw_manifest.decode('utf-8'))
    if manifest.get('geometry_review_correction_2') == TAG:
        print('Already corrected.')
        return
    if manifest.get('geometry_review_correction') != PREVIOUS_TAG:
        raise ValueError('Run scripts/correct_sr44_mud_review.py first.')
    path = BASE / 'model.glb'
    original = path.read_bytes()
    if manifest['geometry_review_correction_record']['after_glb_sha256'] != hashlib.sha256(original).hexdigest():
        raise ValueError('model.glb is not the output of the first review correction.')
    length = struct.unpack_from('<I', original, 12)[0]
    gltf = json.loads(original[20:20 + length])
    binary = bytearray(original[28 + length:])
    before = hashlib.sha256(original).hexdigest()
    parts = {p['id']: p for p in manifest['parts']}
    meshes = {m['name']: m for m in gltf['meshes']}
    changes = []

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

    def get(pid):
        """Native vertices (float64) and faces; the GLB stores (X, Z, -Y)."""
        prim = meshes[pid]['primitives'][0]
        g = read(prim['attributes']['POSITION']).astype(np.float64)
        return np.c_[g[:, 0], -g[:, 2], g[:, 1]], read(prim['indices']).reshape(-1, 3).astype(np.int64)

    def gl(v):
        v = np.asarray(v, dtype=np.float64)
        return np.c_[v[:, 0], v[:, 2], -v[:, 1]].astype('<f4')

    def put(pid, v, f=None):
        """Store new positions (same topology when f is None, otherwise a new mesh); return the solid."""
        prim = meshes[pid]['primitives'][0]
        if f is None:
            prim['attributes']['POSITION'] = append(gl(v), 'VEC3', 5126)
            return solid(v, read(prim['indices']).reshape(-1, 3))
        color = read(prim['attributes']['COLOR_0'])[0]
        prim['attributes'] = {'POSITION': append(gl(v), 'VEC3', 5126),
                              'COLOR_0': append(np.tile(color, (len(v), 1)).astype('u1'), 'VEC4', 5121)}
        gltf['accessors'][prim['attributes']['COLOR_0']]['normalized'] = True
        prim['indices'] = append(np.asarray(f).reshape(-1, 1).astype('<u4'), 'SCALAR', 5125)
        return solid(v, f)

    def record(pid, mesh, note=None, append_note=None, dims=None, **fields):
        if not mesh.is_watertight or mesh.volume <= 0:
            raise ValueError(f'{pid}: corrected mesh is not a closed positive solid')
        p = parts[pid]
        p['bounds_m'] = np.round(mesh.bounds, 6).tolist()
        if 'volume_m3' in p:
            p['volume_m3'] = round(float(mesh.volume), 9)
        if dims:
            p['dimensions'].update(dims)
        if note is not None:
            p['note'] = note
        if append_note:
            p['note'] = (p.get('note', '') + ' ' + append_note).strip()
        p.update(fields)
        extras = meshes[pid]['extras']
        for k in ('name', 'basis', 'note', 'dimensions', 'bounds_m', 'volume_m3'):
            if k in extras:
                extras[k] = p[k]
        changes.append(pid)

    def check(ok, message):
        if not ok:
            raise ValueError(f'Model is not in the expected state: {message}')

    # 1. Regular diaphragm connections (rows 1-6), sheet 20 typical diaphragm detail.
    bolt_verts = len(hexbolt([0, 0, 0], [1, 0, 0], BOLT_R).vertices)
    lengths = []
    for row, uf in enumerate(REGULAR_ROWS, 1):
        u = uf * FT
        for j in range(6):
            y0, y1 = YS[j + 1], YS[j]                  # beam j+2 (lower Y) and beam j+1
            xs = u + K * y0                            # sheet 17 station = connection-plate mid-plane
            cid, pid, bid = f'diaphragm_{row}_{j + 1}', f'diaphragm_plates_{row}_{j + 1}', f'diaphragm_bolts_{row}_{j + 1}'

            v, f = get(cid)
            check(abs(v[:, 0].min() - xs) < TOL and abs(v[:, 0].max() - xs - 3.4 * IN) < TOL, f'{cid} station')
            lo, hi = np.abs(v[:, 1] - y0 - TW / 2) < TOL, np.abs(v[:, 1] - y1 + TW / 2) < TOL
            check((lo | hi).all() and lo.sum() == hi.sum() == len(v) // 2, f'{cid} runs web face to web face')
            z_top = v[:, 2].max()
            v[lo, 1] += END_GAP
            v[hi, 1] -= END_GAP
            v[:, 0] += PLATE_T / 2
            lengths.append(v[:, 1].max() - v[:, 1].min())
            record(cid, put(cid, v), dims=dict(length_in=round(lengths[-1] / IN, 3), end_clearance_in=1),
                   append_note='Channel ends stop 1 in off the beam webs and the web bears on the up-station face of '
                               'the connection plates, 1/4 in up-station of the diaphragm line (sheet 20 typical '
                               'diaphragm detail).')

            v, f = get(pid)
            check(len(v) == 16 and abs(v[:, 0].min() - xs + PLATE_T / 2) < TOL and
                  abs(v[:, 0].max() - xs - PLATE_T / 2) < TOL, f'{pid} plate thickness and station')
            for yb, sg in ((y0, 1), (y1, -1)):
                sel = np.abs(v[:, 1] - (yb + sg * PLATE_W / 2)) < PLATE_W / 2 + TOL
                check(sel.sum() == 8 and abs(np.abs(v[sel, 1] - yb).min()) < TOL and
                      abs(np.abs(v[sel, 1] - yb).max() - PLATE_W) < TOL, f'{pid} plate starts at the beam centre line')
                v[sel, 1] += sg * TW / 2
            record(pid, put(pid, v), dims=dict(plate_in=[0.5, 7.25], count=2),
                   append_note='Plates start at the web face (welded to the web), 7 1/4 in wide (sheet 20); corner '
                               'clips omitted.')

            v, f = get(bid)
            check(len(v) == 16 * bolt_verts, f'{bid} 16 bolts')
            centres = np.sort(np.unique(np.round(v.reshape(16, bolt_verts, 3).mean(axis=1)[:, 1], 6)))
            expected = np.sort([y0 + 1.5 * IN, y0 + 4.5 * IN, y1 - 4.5 * IN, y1 - 1.5 * IN])
            check(len(centres) == 4 and np.abs(centres - expected).max() < TOL, f'{bid} columns from beam centre line')
            check(abs(v[:, 0].min() - (xs - .25 * IN - .012)) < TOL and abs(v[:, 0].max() - (xs + .4 * IN + .017)) < TOL,
                  f'{bid} grip')
            bolts = []
            for yb, sg in ((y0, 1), (y1, -1)):
                for h in (3, 6, 9, 12):
                    for off in COLUMNS:
                        yy, zz = yb + sg * (TW / 2 + off), z_top - h * IN
                        bolts.append(hexbolt([xs - PLATE_T / 2, yy, zz], [xs + PLATE_T / 2 + CHANNEL_WEB, yy, zz], BOLT_R))
            bolts = trimesh.util.concatenate(bolts)
            record(bid, put(bid, bolts.vertices, bolts.faces), dims=dict(count=16, column_offsets_in=[2.5, 5.5]),
                   note='Threads and holes omitted. Two columns per plate, 2 1/2 and 5 1/2 in off the web face, four '
                        'rows at 3 in (sheet 20 typical diaphragm detail); grip through the 1/2 in plate and the channel '
                        'web. Station from sheet 17.')
    print(f'Regular diaphragms: 36 connections rebuilt; channel length {min(lengths) / IN:.3f}-{max(lengths) / IN:.3f} in')

    # 2./3. End diaphragms: underside on the stepped cap + 1/2 in, 6 in pavement ledge; thickened approach ends.
    for si, cap_id, dia_id, app_id in ((0, 'cap_1', 'end_diaphragm_1', 'approach_west'),
                                       (3, 'cap_4', 'end_diaphragm_4', 'approach_east')):
        u, out = BEARINGS[si], (-1 if si == 0 else 1)     # out: direction away from the bridge
        t_end, t_front = out * HALF, u - out * 1.25 * FT
        y_edge = 23.25 * FT
        v, f = get(dia_id)
        check(len(v) == 10, f'{dia_id} single-sweep envelope')
        tv = v[:, 0] - K * v[:, 1]
        check(np.all((np.abs(tv - t_end) < TOL) | (np.abs(tv - t_front) < TOL)), f'{dia_id} faces')
        bottom = v[:, 2] < v[:, 2].min() + .1
        expect = np.where(v[bottom, 1] > 0, el(SEAT[si, 0]), el(SEAT[si, 6])) + POLY
        check(bottom.sum() == 4 and np.abs(v[bottom, 2] - expect).max() < TOL, f'{dia_id} straight underside')
        check(np.abs(v[~bottom, 2] - (surface(v[~bottom, 0], v[~bottom, 1]) - 8 * IN)).max() < TOL, f'{dia_id} top')
        cv, _ = get(cap_id)
        check(abs(cv[:, 2].max() - el(SEAT[si].max())) < TOL, f'{cap_id} step tops')

        # Body before cutting: L-shaped profile (rear ledge + main diaphragm), swept across the width.
        z_low = float(el(SEAT[si].min())) - .1
        t_ledge = t_end + out * LEDGE

        def body_point(y, _):
            pts = [(t_ledge, None), (t_end, None), (t_front, None), (t_front, 'soffit'), (t_end, 'soffit'),
                   (t_end, 'ledge'), (t_ledge, 'ledge')]
            res = []
            for t, level in pts:
                x = t + K * y
                z = z_low if level is None else float(surface(x, y)) - (8 * IN if level == 'soffit' else LEDGE_TOP)
                res.append((x, y, z))
            return res
        body = sweep([-y_edge, 0.0, y_edge], [(0, 1, 5), (0, 5, 6), (5, 1, 2), (5, 2, 3), (5, 3, 4)], body_point)
        cutters = []
        tops = [float(el(SEAT[si, jj])) + POLY for _, _, jj in STEPS]
        for k, (a, b, _) in enumerate(STEPS):
            a, b = a * FT, b * FT
            a = -40 * FT if k == 0 else a - (.1 * FT if tops[k - 1] >= tops[k] else 0)
            b = 40 * FT if k == 4 else b + (.1 * FT if tops[k + 1] >= tops[k] else 0)
            m = box(-3 * FT, 3 * FT, a, b, z_low - .5, tops[k])
            t = np.eye(4)
            t[:2, :2] = [[C, S], [-S, C]]
            t[0, 3] = u
            m.apply_transform(t)
            cutters.append(m)
        dia = trimesh.boolean.difference([body] + cutters, engine='manifold')
        old_volume = parts[dia_id]['volume_m3']
        record(dia_id, put(dia_id, dia.vertices, dia.faces), basis='Dimensioned envelope; embedded interfaces simplified',
               dims=dict(isolation_joint_in=0.5, pavement_ledge_in=6, ledge_depth_below_surface_in=14),
               note='Concrete envelope includes embedded beam ends and bearing pads; the 1/2 in clearance pockets around '
                    'the pads, reinforcement, sleeves and internal voids are excluded. Underside follows the stepped '
                    'cap top with the 1/2 in expanded polystyrene horizontal joint (sheet 24 Sections A-A/B-B, sheet 23 '
                    'elevation). 6 in pavement ledge on the rear face, its top 1 ft 2 in below the road surface '
                    '(sheets 23, 24, 33).')
        print(f'{dia_id}: stepped underside and pavement ledge, volume {old_volume:.4f} -> {dia.volume:.4f} m3')

        # Approach slab: 2 in deeper for 2'-0" from the joint, 45 deg return (sheet 33 pavement ledge detail).
        v, f = get(app_id)
        d = out * (v[:, 0] - K * v[:, 1]) - HALF
        rel = v[:, 2] - surface(v[:, 0], v[:, 1])
        check(abs(d.min()) < TOL and abs(np.abs(v[:, 1]).max() - 21.75 * FT) < TOL, f'{app_id} inner edge')
        check(np.all((np.abs(rel) < TOL) | (np.abs(rel + 12 * IN) < TOL)), f'{app_id} 12 in slab')
        w = 21.75 * FT
        prof = [(0, -LEDGE_TOP), (THICK_LEN, -LEDGE_TOP), (THICK_LEN + THICK_DROP + IN, -11 * IN), (0, -11 * IN)]

        def block_point(y, _):
            return [((out * (HALF + dd) + K * y), y, float(surface(out * (HALF + dd) + K * y, y)) + zz)
                    for dd, zz in prof]
        block = sweep([-w, 0.0, w], [(0, 1, 2), (0, 2, 3)], block_point)
        old_volume = parts[app_id]['volume_m3']
        app = trimesh.boolean.union([solid(v, f), block], engine='manifold')
        record(app_id, put(app_id, app.vertices, app.faces),
               dims=dict(end_thickness_in=14, thickened_length_ft=2),
               note='12 in slab; 2 in deeper (1 ft 2 in) for 2 ft 0 in from the bridge joint where it rests on the '
                    'end-diaphragm pavement ledge, returning at 45 deg (sheet 33 pavement ledge detail; sheet 24). '
                    'Subbase, polyethylene and polystyrene strips are not modelled.')
        print(f'{app_id}: thickened end, volume {old_volume:.4f} -> {app.volume:.4f} m3')

    gltf['buffers'][0]['byteLength'] = len(binary)
    while len(binary) % 4:
        binary.append(0)
    gltf['buffers'][0]['byteLength'] = len(binary)
    encoded = json.dumps(gltf, ensure_ascii=True, separators=(',', ':')).encode()
    encoded += b' ' * ((-len(encoded)) % 4)
    out_bytes = (struct.pack('<III', 0x46546c67, 2, 28 + len(encoded) + len(binary)) +
                 struct.pack('<II', len(encoded), 0x4e4f534a) + encoded +
                 struct.pack('<II', len(binary), 0x004e4942) + binary)
    backup = ROOT / 'data/fem_research'
    backup.mkdir(exist_ok=True)
    (backup / 'sr44-mud_before_review_correction_2.glb').write_bytes(original)
    (backup / 'sr44-mud_manifest_before_review_correction_2.json').write_bytes(raw_manifest)
    path.write_bytes(out_bytes)

    for c in manifest['detail_coverage']:
        if c['feature'] == 'Diaphragms':
            c['detail'] = ('48 channel diaphragms in six regular and two skew support rows; connection plates and bolts. '
                           'Regular rows: channels 1 in off the webs on 1/2 x 7 1/4 in plates, 16 bolts each. Pier rows: '
                           '5 ft 11 in channels on bent plates with 32 bolts each. Channel taper simplified.')
    manifest['geometry_review_correction_2'] = TAG
    manifest['revision'] = '1.2-drawing-review-2'
    manifest['geometry_review_correction_2_record'] = dict(
        source='Independent second check of the corrected model (2026-11), items verified against the drawings',
        source_pdf_pages=[20, 23, 24, 33], printed_sheets=[20, 23, 24, 33],
        corrections={
            'Regular diaphragm connections rows 1-6 (36 channels, plates, bolts)':
                'channels web face to web face -> 1 in clear of each web, web on the plate face (+1/4 in X); plates '
                'from the beam centre line -> from the web face; bolt columns 1.255/4.255 in -> 2 1/2 and 5 1/2 in '
                'off the web face (sheet 20 typical diaphragm detail)',
            'End diaphragms end_diaphragm_1, end_diaphragm_4':
                'straight underside up to 0.089 m inside the cap -> stepped cap top + 1/2 in polystyrene joint '
                '(sheets 23, 24); 6 in pavement ledge, top 1\'-2" below the surface, added (sheets 23, 24, 33)',
            'Approach slabs approach_west, approach_east':
                '12 in to the joint -> 14 in for 2\'-0" with a 45 deg return (sheet 33 pavement ledge detail)'},
        changed_parts=changes, before_glb_sha256=before, after_glb_sha256=hashlib.sha256(out_bytes).hexdigest())
    deviations = [d for d in manifest.get('known_deviations', []) if d.get('id') != 'approach-extension-ledge']
    deviations.append(dict(
        id='approach-extension-ledge', parts='extension_-1_-1, extension_-1_1, extension_1_-1, extension_1_1',
        source='sheet 33 note 2; standard drawing E609-TBAE-01 (not in the set)',
        deviation='The RCBA extensions under the TFC transitions keep a 12 in depth to the bridge joint, so a 2 in gap '
                  'remains between them and the pavement ledge over the outer 1 ft 6 in of each end.',
        reason='The extension end detail is on a standard drawing that is not in the drawing set.'))
    manifest['known_deviations'] = deviations
    text = json.dumps(manifest, indent=2) + ('\n' if raw_manifest.endswith(b'\n') else '')
    mp.write_text(text, encoding='utf-8', newline='\r\n' if b'\r\n' in raw_manifest else '\n')
    print(json.dumps({k: v for k, v in manifest['geometry_review_correction_2_record'].items() if k != 'changed_parts'}))
    print(f'{len(changes)} parts changed')


if __name__ == '__main__':
    correct()

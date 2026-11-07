"""One-time, drawing-confirmed corrections from the external model review, preserving unrelated GLB buffers.

    python scripts/correct_sr44_mud_review.py

All sheets are INDOT B-38321 (data/bridges/sr44-mud/drawings.pdf); in this set the printed sheet number equals the PDF
page number. Native axes: X station from 617+95, Y toward beam 1, Z = elevation - 885 ft (metres).

Regular diaphragm stations, sheet 17 FRAMING PLAN. The DIAPHRAGM SPACING (TYP.) chain is drawn along beam 7 from the
centre line of bearing of Bent 1: 9'-9", 20'-3", 37'-3", 15'-0", 37'-3", 20'-3", 9'-9" (= 149'-6"). The diaphragms are
staggered 1'-10 1/2" (7 ft x tan 15 deg) from bay to bay, so in every bay the chain is measured along the higher-numbered
beam (the beam at the lower Y), as the vector geometry of the sheet confirms (9.74 ft both at beam 7 and at beam 2). The
model measured it at the bay centre line, so all 36 regular assemblies (channel, connection plates, bolts) sat
3.5 ft x tan 15 deg = 0.285848 m up-station. They move -0.285848 m in X; the two connection plates of each assembly are
re-fitted between the beam flanges at the new station (they follow the loaded beam profile, at most a few mm).

Pier diaphragms, sheet 20 PLAN and ELEVATION - PIER DIAPHRAGM and BENT PLATE DETAILS. Each is a C15x33.9 5'-11" long.
At each end a PL 11/16 x 13 1/2 x 15 in bent plate (two 6 3/4 in legs) joins it to the PL 11/16 x 7 1/4 in bearing
stiffener: the stiffener leg starts 1 in from the beam web (1 1/2 in to the first hole, 3 in hole spacing, 1 3/4 in from
the second hole to the stiffener edge), so it folds 7 3/4 in from the web; the other leg lies on the back of the channel
web with holes 1 1/2 and 4 1/2 in from its free end. Four hole rows at 3 in; 16 bolts per plate, 32 per diaphragm. The
plan places the two stiffener legs on opposite faces of their stiffeners (the up-station face at the beam with the higher
Y), so the channel runs between the two folds, about 19 deg to the beam normal as drawn to scale on sheet 20 rather than
along the 15 deg pier line. The model had channels running web face to web face (2.196 m along the skew), two straight
1/2 in plates and 16 bolts. The channel keeps its elevation; the channel flanges keep facing up-station, a side the
detail does not fix.

Pier cap ends, sheet 16 CAP PLAN (1'-6" + 22'-6" + 22'-6" + 1'-6" = 48'-0") and original 1980 plans sheet 11 CAP PLAN
("1'-6 Radius"): the 48 x 3 ft caps end in semicircles. The model had square ends.

Coping depth, sheet 27 TYPICAL SECTION: 9 1/8 in (TYP.) at the deck edge. The model's edge is the 8 in deck plus the
separate thickened fascia part, 1 5/8 in below it (9 5/8 in); the fascia soffit is raised 1/2 in. Sheet 31 Section A-A
shows 9 1/4 in; the deck-specific typical section is used and the difference is recorded as a known deviation.

Wing isolation joint, sheet 14 plan ("1" EXP. JOINT MATERIAL (TYP.)") and Section C-C (1 in expanded polystyrene and
11 in concrete = 1'-0"), also sheet 23 plan. The wings stood 1/2 in off the 46'-6" coping line; they move 1/2 in outward.

Requires numpy, trimesh, shapely and manifold3d.
"""
import hashlib
import json
import math
import struct
from pathlib import Path

import numpy as np
import trimesh
from shapely.geometry import LineString, Polygon

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'data/bridges/sr44-mud'
FT, IN = .3048, .0254
K = math.tan(math.radians(15))
C, S = math.cos(math.radians(15)), math.sin(math.radians(15))
TAG = 'review-2026-11-diaphragms-caps-coping-wings'
TOL = 3e-5                                   # float32 vertex tolerance (m)

# Builder constants and support geometry, as in scripts/build_sr44_mud.py.
YS = np.array([21, 14, 7, 0, -7, -14, -21]) * FT
D, BF, TW, TF = np.array([26.92, 9.990, .490, .745]) * IN
SEAT = np.array([[904.36, 904.36, 904.51, 904.65, 904.46, 904.27, 904.27],
                 [904.61, 904.61, 904.79, 904.97, 904.82, 904.67, 904.67],
                 [904.79, 904.79, 904.96, 905.13, 904.97, 904.81, 904.81],
                 [904.79, 904.79, 904.96, 905.13, 904.97, 904.81, 904.81]])
SHIM = np.array([[.75, 2.375, 2.125, 2, 2.375, 2.75, 1], [.125, 1.75, 1.5, 1.375, 1.625, 2, .25],
                 [0, 1.5, 1.25, 1, 1.25, 1.625, 0], [0, 1.5, 1.25, 1, 1.25, 1.5, 0]]) * IN
PAD, LOAD = 3.03125 * IN, 1.75 * IN
BEARINGS = np.array([-74.75, -25, 25, 74.75]) * FT
REGULAR_ROWS = [-65, -44.75, -7.5, 7.5, 44.75, 65]       # square stations (ft) of rows 1-6
D_X = -3.5 * FT * K                                      # sheet 17 chain measured at the bay edge, not its centre

# Sheet 20 pier diaphragm details.
T_STIFF = T_PLATE = 11 / 16 * IN
STIFF_W = 7.25 * IN
FREE_END, LEG = 1.0 * IN, 6.75 * IN                      # stiffener-leg free end from the web face; leg length
CHANNEL = 71 * IN                                        # 5'-11"
BOLT_R = .4375 * IN                                      # 7/8 in A325
CAP_R = 1.5 * FT


def el(feet):
    return (np.asarray(feet) - 885) * FT


def grade(x):
    t = np.asarray(x) / FT + 100
    inside = 908.00 + .0082 * t + (-.0029 - .0082) * t * t / 400
    return el(np.where(t < 0, 908.00 + .0082 * t, np.where(t > 200, 908.53 - .0029 * (t - 200), inside)))


def surface(x, y):
    return grade(x) - .02 * np.abs(y)


SUPPORT_TOP = el(SEAT) + SHIM + PAD + LOAD + D


def top(j, u):
    """Top of beam j (0-based) at square station u, as built by scripts/build_sr44_mud.py."""
    g = surface(u + K * YS[j], YS[j]) - 8 * IN
    correction = SUPPORT_TOP[:, j] - (surface(BEARINGS + K * YS[j], YS[j]) - 8 * IN)
    return float(g + np.interp(u, BEARINGS, correction))


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


def correct():
    mp = BASE / 'model_manifest.json'
    raw_manifest = mp.read_bytes()
    manifest = json.loads(raw_manifest.decode('utf-8'))
    if manifest.get('geometry_review_correction') == TAG:
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

    def record(pid, mesh, note=None, append_note=None, dims=None, moved=False, **fields):
        if not mesh.is_watertight or mesh.volume <= 0:
            raise ValueError(f'{pid}: corrected mesh is not a closed positive solid')
        p = parts[pid]
        p['bounds_m'] = np.round(mesh.bounds, 6).tolist()
        if 'volume_m3' in p and not moved:           # a rigid move keeps the recorded volume
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

    # 1. Regular diaphragms (rows 1-6): sheet 17 stations.
    plate_dz = []
    for row, uf in enumerate(REGULAR_ROWS, 1):
        u = uf * FT
        for j in range(6):
            y0, y1 = YS[j + 1], YS[j]
            x_old, x_new = u + K * (y0 + y1) / 2, u + K * y0
            cid, pid, bid = f'diaphragm_{row}_{j + 1}', f'diaphragm_plates_{row}_{j + 1}', f'diaphragm_bolts_{row}_{j + 1}'
            v, f = get(cid)
            check(abs(v[:, 0].min() - x_old) < TOL and abs(v[:, 0].max() - x_old - 3.4 * IN) < TOL, f'{cid} station')
            v[:, 0] += D_X
            record(cid, put(cid, v), moved=True,
                   note=parts[cid]['note'].replace('flange taper, root fillets and skew bent-plate fold simplified',
                                                   'flange taper and root fillets simplified'),
                   append_note='Moved -0.286 m in X to the sheet 17 diaphragm spacing, which is measured along the '
                               'higher-numbered beam of each bay.')
            v, f = get(pid)
            check(abs(v[:, 0].min() - x_old + .25 * IN) < TOL and abs(v[:, 0].max() - x_old - .25 * IN) < TOL,
                  f'{pid} station')
            for yy, sg, jj in [(y0, 1, j + 1), (y1, -1, j)]:
                sel = np.abs(v[:, 1] - (yy + sg * 3.625 * IN)) < 3.625 * IN + TOL
                bt_old, bt_new = top(jj, x_old - K * yy) - D, top(jj, x_new - K * yy) - D
                z = v[sel, 2]
                lo, hi = np.abs(z - bt_old - TF) < TOL, np.abs(z - bt_old - D + TF) < TOL
                check(sel.sum() == 8 and lo.sum() == 4 and hi.sum() == 4, f'{pid} plate between beam flanges')
                z[lo], z[hi] = bt_new + TF, bt_new + D - TF
                v[sel, 2] = z
                plate_dz.append(bt_new - bt_old)
            v[:, 0] += D_X
            record(pid, put(pid, v),
                   note=parts[pid]['note'].replace(' Pier bent-plate fold is represented by its connection envelope.', ''),
                   append_note='Moved -0.286 m in X with its diaphragm (sheet 17) and refitted between the beam flanges '
                               'there.')
            v, f = get(bid)
            check(abs(v[:, 0].min() - (x_old - .25 * IN - .012)) < TOL and
                  abs(v[:, 0].max() - (x_old + .4 * IN + .017)) < TOL, f'{bid} station')
            v[:, 0] += D_X
            record(bid, put(bid, v), moved=True, append_note='Moved -0.286 m in X with its diaphragm (sheet 17).')
    print(f'Regular diaphragms: 36 assemblies moved {D_X:.6f} m in X; plate refit dz '
          f'{min(plate_dz) * 1000:.2f} to {max(plate_dz) * 1000:.2f} mm')

    # 2. Pier diaphragms (rows 7-8): sheet 20 channel, bent plates and 32 bolts.
    profile = Polygon(np.array([(0, 0), (3.4, 0), (3.4, .65), (.4, .65), (.4, 14.35), (3.4, 14.35), (3.4, 15),
                                (0, 15)]) * IN)
    fold_angles = []
    BOLT_VERTS = len(hexbolt([0, 0, 0], [1, 0, 0], BOLT_R).vertices)
    for row, si in [(7, 1), (8, 2)]:
        u = BEARINGS[si]
        for j in range(6):
            y0, y1 = YS[j + 1], YS[j]
            cid, pid, bid = f'diaphragm_{row}_{j + 1}', f'diaphragm_plates_{row}_{j + 1}', f'diaphragm_bolts_{row}_{j + 1}'
            v, f = get(cid)
            check(abs(v[:, 1].min() - y0 - TW / 2) < TOL and abs(v[:, 1].max() - y1 + TW / 2) < TOL,
                  f'{cid} runs web face to web face')
            z_top, z_bot = v[:, 2].max(), v[:, 2].min()
            check(abs(z_top - (min(top(j, u), top(j + 1, u)) - 5 * IN)) < TOL and abs(z_top - z_bot - 15 * IN) < TOL,
                  f'{cid} elevation')
            check(len(get(bid)[0]) == 16 * BOLT_VERTS and len(get(pid)[0]) == 16, f'{bid}/{pid} 16 bolts, 2 plates')
            for jj in (j, j + 1):
                sv, _ = get(f'stiffeners_{si + 1}_{jj + 1}')
                xb = u + K * YS[jj]
                check(abs(sv[:, 0].min() - xb + T_STIFF / 2) < TOL and abs(sv[:, 0].max() - xb - T_STIFF / 2) < TOL and
                      abs(sv[:, 1].max() - YS[jj] - TW / 2 - STIFF_W) < TOL, f'stiffeners_{si + 1}_{jj + 1}')
            # Ends: (beam Y, direction into the bay, face of the stiffener carrying the plate).
            ends = []
            for yb, sigma, rho in [(y0, 1, -1), (y1, -1, 1)]:
                xb = u + K * yb
                xc = xb + rho * (T_STIFF + T_PLATE) / 2
                ends.append(dict(xb=xb, yb=yb, sigma=sigma, rho=rho,
                                 p0=np.array([xc, yb + sigma * (TW / 2 + FREE_END)]),
                                 fold=np.array([xc, yb + sigma * (TW / 2 + FREE_END + LEG)])))
            span = ends[1]['fold'] - ends[0]['fold']
            a = span / np.linalg.norm(span)
            n = np.array([a[1], -a[0]])                      # up-station normal: channel side of the legs
            fold_angles.append(math.degrees(math.atan2(a[0], a[1])))
            middle = (ends[0]['fold'] + ends[1]['fold']) / 2
            channel = trimesh.creation.extrude_polygon(profile, CHANNEL, engine='manifold')
            origin = middle + n * T_PLATE / 2 - a * CHANNEL / 2
            t = np.eye(4)
            t[:3, 0], t[:3, 1], t[:3, 2] = [n[0], n[1], 0], [0, 0, 1], [a[0], a[1], 0]
            t[:3, 3] = [origin[0], origin[1], z_bot]
            channel.apply_transform(t)
            if channel.volume < 0:
                channel.invert()
            plates, bolts = [], []
            for e, leg_dir in zip(ends, (a, -a)):
                p2 = e['fold'] + leg_dir * LEG
                outline = LineString([e['p0'], e['fold'], p2]).buffer(T_PLATE / 2, cap_style='flat', join_style='mitre')
                plate = trimesh.creation.extrude_polygon(outline, 15 * IN, engine='manifold')
                plate.apply_translation([0, 0, z_bot])
                plates.append(plate)
                for h in (3, 6, 9, 12):
                    zz = z_top - h * IN
                    for off in (FREE_END + 1.5 * IN, FREE_END + 4.5 * IN):       # stiffener leg, through the stiffener
                        yy = e['yb'] + e['sigma'] * (TW / 2 + off)
                        bolts.append(hexbolt([e['xb'] + e['rho'] * (T_STIFF / 2 + T_PLATE), yy, zz],
                                             [e['xb'] - e['rho'] * T_STIFF / 2, yy, zz], BOLT_R))
                    for off in (LEG - 4.5 * IN, LEG - 1.5 * IN):                 # channel leg, through the web
                        q = e['fold'] + leg_dir * off
                        bolts.append(hexbolt([*(q - n * T_PLATE / 2), zz], [*(q + n * (T_PLATE / 2 + .4 * IN)), zz],
                                             BOLT_R))
            plates = trimesh.util.concatenate(plates)
            bolts = trimesh.util.concatenate(bolts)
            if len(bolts.vertices) != 32 * BOLT_VERTS:
                raise ValueError(f'{bid}: expected 32 bolts')
            label = f'{"Pier 2" if row == 7 else "Pier 3"}'
            record(cid, put(cid, channel.vertices, channel.faces), dims=dict(length_in=71),
                   note='Nominal section dimensions from Nucor p.47; flange taper and root fillets omitted. 5 ft 11 in '
                        'channel between the two bent-plate folds, square-cut and about '
                        f'{fold_angles[-1]:.1f} deg to the beam normal in plan, as drawn on sheet 20; elevation unchanged.')
            record(pid, put(pid, plates.vertices, plates.faces), basis='Dimensioned bent plates',
                   dims=dict(plate_in=[0.6875, 13.5, 15], leg_in=6.75, count=2),
                   note='Two PL 11/16 x 13 1/2 x 15 in bent plates (sheet 20): one 6 3/4 in leg on the face of the '
                        'bearing stiffener, from 1 in off the web, folded 3/4 in beyond it so the other leg lies on '
                        'the back of the channel web. Welds and holes omitted.')
            record(bid, put(bid, bolts.vertices, bolts.faces), dims=dict(count=32),
                   note='Threads and holes omitted. Per bent plate, 8 bolts through the bearing stiffener (2.5 and '
                        '5.5 in from the web) and 8 through the channel web (1 1/2 and 4 1/2 in from the leg end), '
                        'four rows at 3 in; 32 per diaphragm, sheet 20.')
            print(f'{label} {cid}: channel 71 in at {fold_angles[-1]:.2f} deg, 2 bent plates, 32 bolts')

    # 3. Pier caps: 1'-6" radius semicircular ends.
    def footprint(sign):
        """Local cap footprint of an end step: across x, along the pier line y (m); sign gives the end."""
        arc = [(CAP_R * math.cos(t), sign * (22.5 * FT + CAP_R * math.sin(t))) for t in np.linspace(math.pi, 0, 25)]
        return Polygon([(-CAP_R, sign * 12.5 * FT)] + arc + [(CAP_R, sign * 12.5 * FT)])

    for cid, si in (('cap_2', 1), ('cap_3', 2)):
        u = BEARINGS[si]
        v, f = get(cid)
        check(len(v) == 40 and len(f) == 60, f'{cid} is five step boxes')
        blocks = []
        for k in range(5):
            bv, bf = v[8 * k:8 * k + 8], f[12 * k:12 * k + 12] - 8 * k
            check(bf.min() == 0 and bf.max() == 7, f'{cid} block {k}')
            x = C * (bv[:, 0] - u) - S * bv[:, 1]
            y = S * (bv[:, 0] - u) + C * bv[:, 1]
            if k in (0, 4):
                sign = -1 if k == 0 else 1
                check(np.allclose(np.abs(x), CAP_R, atol=TOL) and abs(np.abs(y).max() - 24 * FT) < TOL and
                      abs(np.abs(y).min() - 12.5 * FT) < TOL, f'{cid} square end step')
                z0, z1 = bv[:, 2].min(), bv[:, 2].max()
                end = trimesh.creation.extrude_polygon(footprint(sign), z1 - z0, engine='manifold')
                t = np.eye(4)
                t[:2, :2] = [[C, S], [-S, C]]
                t[:3, 3] = [u, 0, z0]
                end.apply_transform(t)
                blocks.append(end)
            else:
                blocks.append(solid(bv, bf))
        cap = trimesh.util.concatenate(blocks)
        # Bearings, load plates and side retainers of beams 1 and 7 must stay on the rounded ends.
        for jj in (1, 7):
            for name in (f'bearing_{si + 1}_{jj}', f'bearing_steel_{si + 1}_{jj}'):
                bv, _ = get(name)
                bv = bv[bv[:, 2] < float(el(SEAT[si, jj - 1])) + .02]
                x = C * (bv[:, 0] - u) - S * bv[:, 1]
                y = S * (bv[:, 0] - u) + C * bv[:, 1]
                r = np.hypot(x, np.maximum(np.abs(y) - 22.5 * FT, 0))
                if r.max() > CAP_R:
                    raise ValueError(f'{name} would overhang the rounded end of {cid}')
        record(cid, put(cid, cap.vertices, cap.faces), dims=dict(end_radius_ft=1.5),
               note='Cap ends are 1 ft 6 in radius semicircles (sheet 16 cap plan; original 1980 sheet 11 "1\'-6 '
                    'Radius"); step boundaries are simplified. Primary plans explicitly call existing concrete '
                    'dimensions approximate.')
        print(f'{cid}: rounded ends, volume {parts[cid]["volume_m3"]:.4f} m3')

    # 4. Coping depth 9 1/8 in at the deck edge (8 in deck + fascia part).
    for side in (1, -1):
        pid = f'fascia_{side}'
        v, f = get(pid)
        d = v[:, 2] - surface(v[:, 0], v[:, 1])
        upper, lower = np.abs(d + 8 * IN) < TOL, np.abs(d + 9.625 * IN) < TOL
        check((upper | lower).all() and lower.any(), f'{pid} 9 5/8 in edge depth')
        v[lower, 2] = surface(v[lower, 0], v[lower, 1]) - 9.125 * IN
        record(pid, put(pid, v), dims=dict(edge_depth_in=9.125),
               append_note='Edge depth corrected from 9 5/8 in to the 9 1/8 in coping of the sheet 27 typical section '
                           '(sheet 31 shows 9 1/4 in).')
        print(f'{pid}: coping 9 5/8 -> 9 1/8 in')

    # 5. Wings: 1 in isolation joint outside the 46'-6" coping line.
    for b in (1, 4):
        for side in (-1, 1):
            pid = f'wing_{b}_{side}'
            v, f = get(pid)
            check(abs(np.abs(v[:, 1]).min() - 23.25 * FT - .5 * IN) < TOL and
                  abs(np.abs(v[:, 1]).max() - 23.25 * FT - 11.5 * IN) < TOL, f'{pid} transverse faces')
            v[:, 1] += side * .5 * IN
            record(pid, put(pid, v), moved=True, dims=dict(isolation_joint_in=1),
                   note='Wing station offsets and retained lower joint are simplified. Moved 1/2 in outward: 1 in '
                        'expansion joint material between the wing and the end diaphragm (sheet 14 plan and Section '
                        'C-C; sheet 23).')
    print('Wings: moved 1/2 in outward')

    gltf['buffers'][0]['byteLength'] = len(binary)
    while len(binary) % 4:
        binary.append(0)
    encoded = json.dumps(gltf, ensure_ascii=True, separators=(',', ':')).encode()
    encoded += b' ' * ((-len(encoded)) % 4)
    out = (struct.pack('<III', 0x46546c67, 2, 28 + len(encoded) + len(binary)) +
           struct.pack('<II', len(encoded), 0x4e4f534a) + encoded + struct.pack('<II', len(binary), 0x004e4942) + binary)
    backup = ROOT / 'data/fem_research'
    backup.mkdir(exist_ok=True)
    (backup / 'sr44-mud_before_review_correction.glb').write_bytes(original)
    (backup / 'sr44-mud_manifest_before_review_correction.json').write_bytes(raw_manifest)
    path.write_bytes(out)

    for c in manifest['detail_coverage']:
        if c['feature'] == 'Diaphragms':
            c['detail'] = ('48 channel diaphragms in six regular and two skew support rows; connection plates and bolts. '
                           'Pier rows: 5 ft 11 in channels on bent plates with 32 bolts each. Channel taper simplified.')
    manifest['geometry_review_correction'] = TAG
    manifest['revision'] = '1.1-drawing-review'
    manifest['geometry_review_correction_record'] = dict(
        source='External model review (2026-11), findings verified against the drawings',
        source_pdf_pages=[14, 16, 17, 20, 23, 27, 31], printed_sheets=[14, 16, 17, 20, 23, 27, 31],
        historical_source='original_1980_plans.pdf page 11 (pier cap plan, 1 ft 6 in radius)',
        corrections={
            'Regular diaphragms rows 1-6 (36 channels, plates, bolts)':
                'X -0.285848 m: sheet 17 spacing 9\'-9", 20\'-3", 37\'-3", 15\'-0" ... measured along the '
                'higher-numbered beam of each bay; connection plates refitted to the beam at the new station',
            'Pier diaphragms rows 7-8 (12 channels, plates, bolts)':
                'channel 2.196 m along the skew -> 5\'-11" (1.8034 m) between bent-plate folds; two 1/2 in straight '
                'plates -> two PL 11/16 x 13 1/2 x 15 in bent plates; 16 -> 32 bolts (sheet 20)',
            'Pier caps cap_2, cap_3': 'square ends -> 1\'-6" radius semicircles (sheet 16; 1980 sheet 11)',
            'Fascia fascia_1, fascia_-1': 'coping depth 9 5/8 in -> 9 1/8 in (sheet 27)',
            'Wings wing_1_-1, wing_1_1, wing_4_-1, wing_4_1':
                'isolation gap 1/2 in -> 1 in; inner faces |Y| 7.0993 -> 7.1120 m (sheets 14, 23)'},
        changed_parts=changes, before_glb_sha256=before, after_glb_sha256=hashlib.sha256(out).hexdigest())
    deviations = [d for d in manifest.get('known_deviations', [])
                  if d.get('id') not in ('coping-depth-sheet-31', 'pier-diaphragm-arrangement')]
    deviations.append(dict(
        id='coping-depth-sheet-31', parts='fascia_1, fascia_-1', source='sheets 27 and 31',
        deviation='Coping modelled 9 1/8 in deep over an 8 in wide strip; sheet 31 Section A-A shows 9 1/4 in and a '
                  'wider thickened strip, sheet 27 a level overhang soffit out to the exterior beam haunch.',
        reason='The deck typical section (sheet 27) is used for the depth; the thickened width is not dimensioned.'))
    deviations.append(dict(
        id='pier-diaphragm-arrangement', parts='diaphragm_7_*, diaphragm_8_* and their plates and bolts',
        source='sheet 20',
        deviation=f'Channels run between the bent-plate folds at about {np.mean(fold_angles):.1f} deg to the beam '
                  'normal, as drawn in the pier diaphragm plan; the bent plate detail (6 9/16 in and 2 1/4 in) '
                  'implies a smaller fold. Channel flanges face up-station; the plan does not fix the side. The '
                  'stiffener is 7 1/4 in as in the elevation (the plan label reads 7 1/2 in).',
        reason='Fabrication fit-up detail; the dimensioned channel length, plates and bolt pattern are modelled.'))
    manifest['known_deviations'] = deviations
    text = json.dumps(manifest, indent=2) + ('\n' if raw_manifest.endswith(b'\n') else '')
    mp.write_text(text, encoding='utf-8', newline='\r\n' if b'\r\n' in raw_manifest else '\n')
    print(json.dumps({k: v for k, v in manifest['geometry_review_correction_record'].items() if k != 'changed_parts'}))
    print(f'{len(changes)} parts changed')


if __name__ == '__main__':
    correct()

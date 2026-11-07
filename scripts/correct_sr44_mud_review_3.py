"""Third drawing-confirmed correction of the SR 44 / Mud Creek model: the known deviations left by the first two rounds.

    python scripts/correct_sr44_mud_review_3.py

Runs after correct_sr44_mud_review.py and correct_sr44_mud_review_2.py. All sheets are INDOT B-38321
(data/bridges/sr44-mud/drawings.pdf); printed sheet number = PDF page number. Native axes: X station from 617+95, Y toward
beam 1 (north, left of increasing station; sheet 17), Z = elevation - 885 ft (metres).

Coping / overhang thickening (known deviation coping-depth-sheet-31). Sheet 27 TYPICAL SECTION (1/2" = 1'-0", deck
geometry with the beams drawn): the overhang soffit is drawn level from the deck edge to the outer tip of the exterior
beam's top flange (vector check: edge 9.13 in deep, soffit level over 22.0 in, 8 in slab soffit at 2% inboard of the
flange); "9 1/8 (TYP.)" at the edge. Sheet 31 SECTION A-A is a railing detail that draws the deck without its crossfall
and without the beam (9 1/4 in, 27 in wide strip). DECISION: sheet 27 governs the deck. The fascia parts run from the
deck edge (23'-3") to the flange tip (21'-0" + bf/2 = 4.995 in) with a level soffit 9 1/8 in below the edge surface
(9.57 in at the flange tip, where the 2% top is 0.44 in higher). The top is the deck soffit as meshed. The thickening
stops at the front faces of the semi-integral end diaphragms, which are poured first (sheet 23 note 5) and fill the deck
underside there, and is cut around the pier bearing stiffeners that project 2 1/2 in beyond the exterior flange.

Pier diaphragms (known deviation pier-diaphragm-arrangement), sheet 20 PLAN - PIER DIAPHRAGM, BENT PLATE DETAILS,
ELEVATION; sheet 22 PIER BEARING DETAILS.
- Fold angle. The bent plate detail's 6 9/16 in and 2 1/4 in are the horizontal and vertical offsets of the outer-face
  corner at the end of the bent leg (vector check of the extension lines), i.e. atan(2.25 / 6.5625) = 18.9 deg; the detail
  itself is drawn at 19.1 deg. The written 7'-0" beam spacing, 15 deg skew, 7 1/4 in stiffeners and the legs on opposite
  stiffener faces close only at 19.35 deg, which the model already has. DECISION: keep 19.35 deg (no change).
- Channel side. The plan has no north arrow; it is drawn with the beams horizontal and the CL PIER skew in the sense of the
  sheet 17 framing plan, while the rotated detail plans of this set (sheets 16 and 23) carry their own north arrows. Read
  in the framing-plan orientation the plan shows the plate legs on the up-station face of the stiffener at the north
  beam and on the down-station face at the south beam (as modelled) and the C15x33.9 web on the down-station face of both
  bent legs. DECISION: the 12 channels are reflected across the bent-leg centre plane and the 8 channel-leg bolts of each
  diaphragm with them (heads on the bent leg, nuts inside the channel). Bent plates and stiffener-leg bolts unchanged.
- Stiffener width. Sheet 22 (PL 11/16 x 7 1/4 x 25 7/16) and the sheet 20 elevation give 7 1/4 in; the sheet 20 plan
  label reads 7 1/2 in. DECISION: 7 1/4 in (no change).

Square coping zone at the end bents (sheet 23 PLAN, "1'-6" (TYP.)" at Wings A-D; sheet 31 RAILING PLAN; sheet 32). Over
the outer 1'-6" at each coping (|Y| 21'-9" to 23'-3", the barrier and coping width) the end-diaphragm front and rear
faces, the pavement ledge and so the bridge joint turn square to the roadway, through the point where the skew joint
meets |Y| = 21'-9"; the railing plan draws the joint and the FC/TFC end square across the barrier, and the RCBA extensions
end square there (sheet 32). The model ran all of them on the skew to the coping. Changed consistently:
- end_diaphragm_1/4 rebuilt with the second-round recipe (L profile with the 6 in ledge, underside = stepped cap + 1/2 in)
  and square faces in the zone;
- retained caps cap_1/4: their end steps stopped at yl = +/-24 ft along the skew with square corners. Original 1980 plans
  page 9 (PLAN - BENT No 1, "1'-0 (Typical)" twice at Wing B, "1'-0 1'-3 (Typical)" at Wing A) and page 10 (piling plan)
  with the 2017 sheet 12 removal plan (vector check) give the existing ends: the bent ends at the wing inner faces
  (|Y| = 23'-3"), the front face splays into each wing 1'-0" from the wing face to 1'-0" along it, and the rear face
  turns square to the roadway over the last 1'-3". The end steps are rebuilt to that outline (other steps unchanged), so
  the square-zone diaphragm corners sit on the cap except for <= 1.1 in where the 1'-0"/1'-3" ends are shorter than the
  1'-6" zone;
- deck: the skew corner beyond the square joint is removed at the corners where the joint turns toward the bridge and a
  wedge added where it turns toward the approach;
- rail_1/-1 and the four TFC transitions: the FC/TFC end moves from the skew point at the barrier back face to the square
  joint (-/+ 0.1089 m in X, re-seated on the profile); the barrier delineators move with the barrier;
- the overhang thickening ends on the kinked end-diaphragm front faces.

RCBA extensions (known deviation approach-extension-ledge). Sheet 33 note 2: the extension thickness "shall match approach
slab thickness"; sheet 33 PAVEMENT LEDGE DETAIL: 2 in deeper (1'-2") for 2'-0" from the joint with a 45 deg return,
bearing on the 6 in ledge; sheet 31 ELEVATION (north rail shown, south rail same) draws the slab under each TFC
transition with the 2'-0" thickened end and 45 deg return at both bridge ends. RESOLVED: each extension is 14 in deep for
2'-0" from its square end (the joint in the coping zone), returning at 45 deg, so it bears on the ledge.

Bearing stiffener clips (independent check, sheet 22 END VIEW and SECTION VIEW: "CLIP CORNERS 2 1/2" x 1 1/4" TOP AND
BOTTOM (TYP.)", drawn 2 1/2 in along the web and 1 1/4 in along the flange). The builder clipped only the top web corner,
2 1/2 in along the flange and 1 1/4 in down the web. All 28 stiffener pairs are rebuilt with 1 1/4 x 2 1/2 in clips at the
top and bottom web corners; widths, thicknesses, heights and stations unchanged. The sloped outer corners of the
projecting pier stiffeners are drawn but not dimensioned and stay square (known deviation).

Requires numpy, trimesh, shapely and manifold3d.
"""
import hashlib
import json
import math
import struct
from pathlib import Path

import numpy as np
import trimesh
from shapely.geometry import Polygon

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'data/bridges/sr44-mud'
FT, IN = .3048, .0254
K = math.tan(math.radians(15))
C, S = math.cos(math.radians(15)), math.sin(math.radians(15))
PREVIOUS_TAG = 'review-2026-11-second-check-connections-end-bents'
PREVIOUS_REVISION = '1.2-drawing-review-2'
TAG = 'review-2026-11-third-round-known-deviations'
REVISION = '1.3-deviations'
TOL = 3e-5                                   # float32 vertex tolerance (m)

# Builder constants (scripts/build_sr44_mud.py).
HALF = (151 + 1 / 12) / 2 * FT
BEARINGS = np.array([-74.75, -25, 25, 74.75]) * FT
YS = np.array([21, 14, 7, 0, -7, -14, -21]) * FT
D, BF, TW, TF = np.array([26.92, 9.990, .490, .745]) * IN
SEAT = np.array([[904.36, 904.36, 904.51, 904.65, 904.46, 904.27, 904.27],
                 [904.61, 904.61, 904.79, 904.97, 904.82, 904.67, 904.67],
                 [904.79, 904.79, 904.96, 905.13, 904.97, 904.81, 904.81],
                 [904.79, 904.79, 904.96, 905.13, 904.97, 904.81, 904.81]])
SHIM = np.array([[.75, 2.375, 2.125, 2, 2.375, 2.75, 1], [.125, 1.75, 1.5, 1.375, 1.625, 2, .25],
                 [0, 1.5, 1.25, 1, 1.25, 1.625, 0], [0, 1.5, 1.25, 1, 1.25, 1.5, 0]]) * IN
PAD, LOAD = 3.03125 * IN, 1.75 * IN
STEPS = [(-24, -12.5, 6), (-12.5, -1.75, 4), (-1.75, 1.75, 3), (1.75, 12.5, 2), (12.5, 24, 0)]  # cap steps (ft, seat)
Y_EDGE = 23.25 * FT                                  # 46'-6" out-to-out coping
Y_SQ = 21.75 * FT                                    # square coping zone beyond this (sheet 23, 1'-6" (TYP.))
RAIL_EDGE = Y_EDGE - 2 * IN                          # FC back face line used by the builder
BOLT_R = .4375 * IN
# Sheet 27 coping.
EDGE_DEPTH = 9.125 * IN
DECK_T = 8 * IN
# Sheet 20 pier diaphragm (as placed by correct_sr44_mud_review.py).
T_STIFF = T_PLATE = 11 / 16 * IN
FREE_END, LEG, CHANNEL, FLANGE = 1.0 * IN, 6.75 * IN, 71 * IN, 3.4 * IN
# Sheets 23, 24 and 33 end diaphragm, ledge and approach end.
POLY, LEDGE = .5 * IN, 6 * IN
LEDGE_TOP, THICK_LEN, THICK_DROP = 14 * IN, 2 * FT, 2 * IN
# Sheet 22 bearing stiffener clips (along the flange, along the web).
CLIP_H, CLIP_V = 1.25 * IN, 2.5 * IN


def el(feet):
    return (np.asarray(feet) - 885) * FT


def grade(x):
    t = np.asarray(x) / FT + 100
    inside = 908.00 + .0082 * t + (-.0029 - .0082) * t * t / 400
    return el(np.where(t < 0, 908.00 + .0082 * t, np.where(t > 200, 908.53 - .0029 * (t - 200), inside)))


def surface(x, y):
    return grade(x) - .02 * np.abs(y)


def xface(t, y):
    """Plan X of an end-bent face whose skew line is t = X - K*Y: skew inside the barrier zone, square beyond |Y| = 21'-9"."""
    return t + K * np.clip(y, -Y_SQ, Y_SQ)


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
    """Closed solid: profile vertex k at station s is point(s)[k]; profile_tris triangulate the profile polygon."""
    n = len(point(stations[0]))
    v = np.array([p for s in stations for p in point(s)], float)
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


def prism(points, z0, z1):
    """Vertical prism over a plan polygon."""
    m = trimesh.creation.extrude_polygon(Polygon(points), z1 - z0, engine='manifold')
    m.apply_translation([0, 0, z0])
    return m


def end_diaphragm_body(si, stations, square=True):
    """Second-round end diaphragm (L profile with the rear pavement ledge, underside on the stepped cap + 1/2 in) with
    its faces at xface(t, y) (square=False: on the skew everywhere, as built in round 2); stations are the Y values of the
    sweep."""
    u, out = BEARINGS[si], (-1 if si == 0 else 1)
    t_end, t_front = out * HALF, u - out * 1.25 * FT
    t_ledge = t_end + out * LEDGE
    z_low = float(el(SEAT[si].min())) - .1

    def body_point(y):
        res = []
        for t, level in [(t_ledge, None), (t_end, None), (t_front, None), (t_front, 'soffit'), (t_end, 'soffit'),
                         (t_end, 'ledge'), (t_ledge, 'ledge')]:
            x = float(xface(t, y)) if square else t + K * y
            z = z_low if level is None else float(surface(x, y)) - (DECK_T if level == 'soffit' else LEDGE_TOP)
            res.append((x, y, z))
        return res
    body = sweep(stations, [(0, 1, 5), (0, 5, 6), (5, 1, 2), (5, 2, 3), (5, 3, 4)], body_point)
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
    return trimesh.boolean.difference([body] + cutters, engine='manifold')


def stiffener_pair(si, j, profile):
    """Bearing stiffeners either side of the web of beam j at support si, as in the builder, for a (v, h) profile measured
    from the web face and from the top of the bottom flange."""
    u, y = BEARINGS[si], YS[j]
    x = u + K * y
    zt = float(el(SEAT[si, j])) + PAD + LOAD + SHIM[si, j]
    th = (.5 if si in (0, 3) else .6875) * IN
    n = len(profile)
    tris = [(0, k, k + 1) for k in range(1, n - 1)]
    pieces = []
    for side in (-1, 1):
        pieces.append(sweep([-th / 2, th / 2], tris,
                            lambda t: [(x + t, y + side * (TW / 2 + a), zt + TF + b) for a, b in profile]))
    return trimesh.util.concatenate(pieces)



def correct():
    mp = BASE / 'model_manifest.json'
    raw_manifest = mp.read_bytes()
    manifest = json.loads(raw_manifest.decode('utf-8'))
    if manifest.get('geometry_review_correction_3') == TAG:
        print('Already corrected.')
        return
    if manifest.get('geometry_review_correction_2') != PREVIOUS_TAG or manifest.get('revision') != PREVIOUS_REVISION:
        raise ValueError('Run scripts/correct_sr44_mud_review.py and correct_sr44_mud_review_2.py first.')
    path = BASE / 'model.glb'
    original = path.read_bytes()
    before = hashlib.sha256(original).hexdigest()
    if manifest['geometry_review_correction_2_record']['after_glb_sha256'] != before:
        raise ValueError('model.glb is not the output of the second review correction.')
    length = struct.unpack_from('<I', original, 12)[0]
    gltf = json.loads(original[20:20 + length])
    binary = bytearray(original[28 + length:])
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

    def put(pid, v, f):
        """Store a new mesh (positions, colours and indices); return the solid."""
        prim = meshes[pid]['primitives'][0]
        color = read(prim['attributes']['COLOR_0'])[0]
        prim['attributes'] = {'POSITION': append(gl(v), 'VEC3', 5126),
                              'COLOR_0': append(np.tile(color, (len(v), 1)).astype('u1'), 'VEC4', 5121)}
        gltf['accessors'][prim['attributes']['COLOR_0']]['normalized'] = True
        prim['indices'] = append(np.asarray(f).reshape(-1, 1).astype('<u4'), 'SCALAR', 5125)
        return solid(np.asarray(v, float), np.asarray(f))

    def record(pid, mesh, note=None, dims=None, **fields):
        if not mesh.is_watertight or not mesh.is_winding_consistent or mesh.volume <= 0:
            raise ValueError(f'{pid}: corrected mesh is not a closed positive solid')
        p = parts[pid]
        p['bounds_m'] = np.round(mesh.bounds, 6).tolist()
        if 'volume_m3' in p:
            p['volume_m3'] = round(float(mesh.volume), 9)
        if dims:
            p['dimensions'].update(dims)
        if note is not None:
            p['note'] = note
        p.update(fields)
        extras = meshes[pid]['extras']
        for k in ('name', 'basis', 'note', 'dimensions', 'bounds_m', 'volume_m3', 'pdf_pages'):
            if k in extras:
                extras[k] = p[k]
        changes.append(pid)

    def check(ok, message):
        if not ok:
            raise ValueError(f'Model is not in the expected state: {message}')

    # 1. Bearing stiffeners: 1 1/4 x 2 1/2 in clips at the top and bottom web corners (sheet 22).
    new_stiff = {}
    for si in range(4):
        wid = (4.75 if si in (0, 3) else 7.25) * IN
        hs = D - 2 * TF
        old_prof = [(0, 0), (wid, 0), (wid, hs), (2.5 * IN, hs), (0, hs - 1.25 * IN)]
        new_prof = [(0, CLIP_V), (CLIP_H, 0), (wid, 0), (wid, hs), (CLIP_H, hs), (0, hs - CLIP_V)]
        for j in range(7):
            pid = f'stiffeners_{si + 1}_{j + 1}'
            v, f = get(pid)
            ref = stiffener_pair(si, j, old_prof).vertices
            d = np.linalg.norm(v[:, None, :] - ref[None, :, :], axis=2)
            check(len(v) == len(ref) == 20 and d.min(axis=1).max() < TOL and d.min(axis=0).max() < TOL,
                  f'{pid} builder clip (2 1/2 in along the flange, 1 1/4 in down the web, top only)')
            m = stiffener_pair(si, j, new_prof)
            new_stiff[pid] = put(pid, m.vertices, m.faces)
            record(pid, new_stiff[pid], basis='Dimensioned plate; clipped corners',
                                    dims=dict(width_in=wid / IN, clip_in=[1.25, 2.5], clips='top and bottom web corners'),
                                    note='Bearing stiffeners either side of the web (sheet 22): corners at the web clipped '
                                         '1 1/4 in along the flange by 2 1/2 in along the web, top and bottom ("CLIP '
                                         'CORNERS 2 1/2" x 1 1/4" TOP AND BOTTOM (TYP.)"). Welds omitted.' +
                                         (' The sloped outer corners drawn beyond the flange tip are not dimensioned and '
                                          'are kept square.' if si in (1, 2) else ''))
    print('Bearing stiffeners: 28 pairs rebuilt with 1 1/4 x 2 1/2 in clips at the top and bottom web corners')

    # 2. End diaphragms: square faces over the outer 1'-6" (sheet 23 plan, sheet 31 railing plan).
    for si, dia_id in ((0, 'end_diaphragm_1'), (3, 'end_diaphragm_4')):
        v, f = get(dia_id)
        old = end_diaphragm_body(si, [-Y_EDGE, 0.0, Y_EDGE], square=False)    # the second-round recipe
        cur = solid(v, f)
        common = trimesh.boolean.intersection([cur, old], engine='manifold').volume
        check(abs(cur.volume - old.volume) < 1e-6 and abs(common - cur.volume) < 1e-6 and
              np.abs(cur.bounds - old.bounds).max() < TOL, f'{dia_id} second-round geometry')
        dia = end_diaphragm_body(si, [-Y_EDGE, -Y_SQ, 0.0, Y_SQ, Y_EDGE])
        old_volume = parts[dia_id]['volume_m3']
        record(dia_id, put(dia_id, dia.vertices, dia.faces), dims=dict(square_coping_zone_ft=1.5),
               pdf_pages=sorted(set(parts[dia_id]['pdf_pages']) | {31}),
               note=parts[dia_id]['note'] + ' Front and rear faces and the ledge turn square to the roadway over the '
                    'outer 1 ft 6 in at each coping (sheet 23 plan; sheet 31 railing plan); the underside there stays on '
                    'the retained cap steps + 1/2 in.')
        print(f'{dia_id}: square coping zone, volume {old_volume:.4f} -> {dia.volume:.4f} m3')

    # 2b. Retained end-bent caps: ends at the wing inner faces, front face splayed 1'-0" x 1'-0" into each wing, rear
    #     face square to the roadway over the last 1'-3" (original 1980 plans pages 9-10; sheet 12).
    face_dx = 1.25 * FT / C                                         # cap face offset from the bent line in X at fixed Y
    for si, cap_id in ((0, 'cap_1'), (3, 'cap_4')):
        u, out = BEARINGS[si], (-1 if si == 0 else 1)               # front face (span side) at local x = -out * 1'-3"
        v, f = get(cap_id)
        check(len(v) == 40 and len(f) == 60, f'{cap_id} is five step boxes')

        def face(front, yy):
            return u + (-out if front else out) * face_dx + K * yy

        def local(xx, yy):
            return (u + C * xx + S * yy, -S * xx + C * yy)
        blocks = []
        for k in range(5):
            bv, bf = v[8 * k:8 * k + 8], f[12 * k:12 * k + 12] - 8 * k
            check(bf.min() == 0 and bf.max() == 7, f'{cap_id} block {k}')
            xl = C * (bv[:, 0] - u) - S * bv[:, 1]
            yl = S * (bv[:, 0] - u) + C * bv[:, 1]
            if k in (0, 4):
                sg = -1 if k == 0 else 1
                check(np.allclose(np.abs(xl), 1.25 * FT, atol=TOL) and abs(np.abs(yl).max() - 24 * FT) < TOL and
                      abs(np.abs(yl).min() - 12.5 * FT) < TOL, f'{cap_id} square end step')
                z0, z1 = float(bv[:, 2].min()), float(bv[:, 2].max())
                pts = [local(-out * 1.25 * FT, sg * 12.5 * FT),
                       (face(True, sg * (Y_EDGE - 1.0 * FT)), sg * (Y_EDGE - 1.0 * FT)),      # splay start
                       (face(True, sg * Y_EDGE) - out * 1.0 * FT, sg * Y_EDGE),              # splay end on the wing
                       (face(False, sg * (Y_EDGE - 1.25 * FT)), sg * Y_EDGE),                # square rear end
                       (face(False, sg * (Y_EDGE - 1.25 * FT)), sg * (Y_EDGE - 1.25 * FT)),
                       local(out * 1.25 * FT, sg * 12.5 * FT)]
                check(Polygon(pts).is_valid, f'{cap_id} end outline')
                blocks.append(prism(pts, z0, z1))
            else:
                blocks.append(solid(bv, bf))
        cap = trimesh.util.concatenate(blocks)
        old_volume = parts[cap_id]['volume_m3']
        record(cap_id, put(cap_id, cap.vertices, cap.faces),
               dimensions=dict(width_ft=2.5, end_at_wing_face_y_ft=23.25, front_splay_ft=[1.0, 1.0],
                               rear_square_end_ft=1.25, historical_pdf_pages=[9, 10]),
               note='Step boundaries are simplified. Ends at the existing wing inner faces (|Y| = 23 ft 3 in): the front '
                    'face splays into each wing 1 ft 0 in from the wing face to 1 ft 0 in along it, the rear face turns '
                    'square to the roadway over the last 1 ft 3 in (original 1980 plans pages 9-10, "1\'-0 (Typical)", '
                    '"1\'-3 (Typical)"; sheet 12 plan). Primary plans explicitly call existing concrete dimensions '
                    'approximate.')
        print(f'{cap_id}: wing-face ends with front splays and square rear ends, volume {old_volume:.4f} -> '
              f'{cap.volume:.4f} m3')

    # 3. Deck: square ends over the outer 1'-6" (sheets 23, 31); the soffit rows feed the overhang thickening below.
    dv, df = get('deck')
    soffit = dv[np.abs(dv[:, 2] - (surface(dv[:, 0], dv[:, 1]) - DECK_T)) < TOL]
    rows = {}
    for yk in (-Y_EDGE, 0.0, Y_EDGE):
        r = soffit[np.abs(soffit[:, 1] - yk) < TOL]
        rows[yk] = r[np.argsort(r[:, 0] - K * r[:, 1])]
    check(all(len(r) == len(rows[0.0]) for r in rows.values()) and len(rows[0.0]) > 100, 'deck soffit rows')
    for yk in (-Y_EDGE, Y_EDGE):
        check(np.abs((rows[yk][:, 0] - K * rows[yk][:, 1]) - rows[0.0][:, 0]).max() < TOL, 'deck stations')
    tv = dv[:, 0] - K * dv[:, 1]
    check(abs(tv.min() + HALF) < TOL and abs(tv.max() - HALF) < TOL, 'deck skew ends')
    adds, cuts = [], []
    zlo, zhi = dv[:, 2].min() - 1, dv[:, 2].max() + 1
    for out in (-1, 1):
        for side in (-1, 1):
            x0 = out * HALF + K * side * Y_SQ
            if out * side > 0:                                       # joint turns toward the bridge: cut the corner
                xa, xb = sorted([x0, x0 + out * 1.0])
                ya, yb = sorted([side * Y_SQ, side * (Y_EDGE + .5)])
                cuts.append(box(xa, xb, ya, yb, zlo, zhi))
            else:                                                    # joint turns toward the approach: add a wedge
                end = dv[np.abs(tv - out * HALF) < TOL]
                e0, e1 = end[np.abs(end[:, 1]) < TOL], end[np.abs(end[:, 1] - side * Y_EDGE) < TOL]
                check(len(e0) == 2 and len(e1) == 2, 'deck end-face vertices')
                e0, e1 = e0[np.argsort(e0[:, 2])], e1[np.argsort(e1[:, 2])]   # bottom, top
                a_ = e0 + (e1 - e0) * (Y_SQ / Y_EDGE)                # on the end-face edges at |Y| = 21'-9"
                c_top = np.array([x0, side * Y_EDGE, float(surface(x0, side * Y_EDGE))])
                c_ = np.array([c_top - [0, 0, DECK_T], c_top])
                wv = np.array([a_[0], e1[0], c_[0], a_[1], e1[1], c_[1]])
                wf = np.array([(0, 2, 1), (3, 4, 5), (0, 1, 4), (0, 4, 3), (1, 2, 5), (1, 5, 4), (2, 0, 3), (2, 3, 5)])
                wedge = solid(wv, wf)
                if wedge.volume < 0:
                    wedge.invert()
                adds.append(wedge)
    deck = trimesh.boolean.union([solid(dv, df)] + adds, engine='manifold')
    deck = trimesh.boolean.difference([deck] + cuts, engine='manifold')
    old_volume = parts['deck']['volume_m3']
    record('deck', put('deck', deck.vertices, deck.faces), dims=dict(square_end_zone_ft=1.5),
           pdf_pages=sorted(set(parts['deck']['pdf_pages']) | {23, 31}),
           note=parts['deck']['note'] + ' Deck ends follow the skew joint except over the outer 1 ft 6 in at each coping, '
                'where the joint is square to the roadway (sheet 23 plan; sheet 31 railing plan).')
    print(f'deck: square ends in the coping zones, volume {old_volume:.4f} -> {deck.volume:.4f} m3')

    # 4. FC barriers, TFC transitions and delineators: the FC/TFC end moves to the square joint (sheet 31 railing plan).
    def reseat(v, dx):
        out = v.copy()
        out[:, 0] += dx
        out[:, 2] += surface(out[:, 0], v[:, 1]) - surface(v[:, 0], v[:, 1])
        return out

    fc_levels = np.array([0, 3, 10, 33]) * IN
    for side in (1, -1):
        dx = K * side * (Y_SQ - RAIL_EDGE)
        pid = f'rail_{side}'
        v, f = get(pid)
        uu, rel = v[:, 0] - K * side * RAIL_EDGE, v[:, 2] - surface(v[:, 0], v[:, 1])
        check(abs(uu.min() + HALF) < TOL and abs(uu.max() - HALF) < TOL and
              np.abs(rel[:, None] - fc_levels[None, :]).min(axis=1).max() < TOL, f'{pid} ends at the skew back-face point')
        record(pid, put(pid, reseat(v, dx), f), pdf_pages=sorted(set(parts[pid]['pdf_pages']) | {23}),
               note=parts[pid]['note'] + f' Ends on the square bridge joint across the barrier zone (sheet 31 railing '
                    f'plan; sheet 23): moved {dx:+.4f} m in X from the skew point at the back face.')
        for end in (-1, 1):
            pid = f'tfc_{end}_{side}'
            v, f = get(pid)
            start = end * HALF + K * side * RAIL_EDGE
            check(abs((v[:, 0].min() if end > 0 else v[:, 0].max()) - start) < TOL, f'{pid} start')
            record(pid, put(pid, reseat(v, dx), f), pdf_pages=sorted(set(parts[pid]['pdf_pages']) | {23}),
                   note=parts[pid]['note'] + f' Starts at the square bridge joint (sheet 31 railing plan): moved '
                        f'{dx:+.4f} m in X.')
        for k in range(1, 7):
            pid = f'delineator_{side}_{k}'
            v, f = get(pid)
            centre = v.mean(axis=0)
            check(len(v) == 8 and abs(centre[0] - (np.linspace(-HALF, HALF, 6)[k - 1] + K * side * RAIL_EDGE)) < TOL,
                  f'{pid} station')
            moved = v + [dx, 0, float(surface(centre[0] + dx, side * RAIL_EDGE) - surface(centre[0], side * RAIL_EDGE))]
            record(pid, put(pid, moved, f), note=parts[pid]['note'] + f' Moved {dx:+.4f} m in X with the barrier.')
    print(f'Barriers, transitions and delineators: moved {K * (Y_SQ - RAIL_EDGE):+.4f} m (north) / '
          f'{-K * (Y_SQ - RAIL_EDGE):+.4f} m (south) in X to the square joint')

    # 5. Overhang thickening (fascia_1, fascia_-1): level soffit from the deck edge to the exterior flange tip, sheet 27.
    t_stop = BEARINGS[[0, 3]] + np.array([1.25, -1.25]) * FT      # end-diaphragm front faces (sheet 24)
    reach = np.array([t_stop[0] - .2, t_stop[1] + .2])              # body overrun, cut back on the kinked front faces
    big = 30.0
    front_cut = []
    for ts, out in ((t_stop[0], -1), (t_stop[1], 1)):
        pts = [(float(xface(ts, -big)), -big), (float(xface(ts, -Y_SQ)), -Y_SQ), (float(xface(ts, Y_SQ)), Y_SQ),
               (float(xface(ts, big)), big), (ts + out * big, big), (ts + out * big, -big)]
        front_cut.append(prism(pts, -20.0, 40.0))
    steel_cut = {1: ('stiffeners_2_1', 'stiffeners_3_1'), -1: ('stiffeners_2_7', 'stiffeners_3_7')}
    for side in (1, -1):
        pid = f'fascia_{side}'
        v, f = get(pid)
        rel = v[:, 2] - surface(v[:, 0], v[:, 1])
        check(len(v) == 720 and np.all((np.abs(np.abs(v[:, 1]) - Y_EDGE) < TOL) |
                                        (np.abs(np.abs(v[:, 1]) - Y_EDGE + 8 * IN) < TOL)), f'{pid} 8 in strip')
        check(np.all((np.abs(rel + DECK_T) < TOL) | (np.abs(rel + EDGE_DEPTH) < TOL)), f'{pid} 9 1/8 in parallel strip')
        y_out, y_in = side * Y_EDGE, side * (YS[0] + BF / 2)
        w = y_in / y_out
        u_deck = rows[0.0][:, 0]
        inside = (u_deck > reach[0] + .01) & (u_deck < reach[1] - .01)
        p0, p1 = [], []
        for row, lst in ((rows[0.0], p0), (rows[y_out], p1)):
            ends = [np.array([np.interp(ts, u_deck, row[:, c]) for c in range(3)]) for ts in reach]
            lst.extend([ends[0]] + list(row[inside]) + [ends[1]])
        p0, p1 = np.array(p0), np.array(p1)

        def point(i):
            top_in = p0[i] + (p1[i] - p0[i]) * w                    # on the deck soffit as meshed
            x_in, x_out = top_in[0], p1[i][0]
            return [(x_in, y_in, float(surface(x_in, y_out)) - EDGE_DEPTH),      # level soffit
                    (x_out, y_out, float(p1[i][2]) - (EDGE_DEPTH - DECK_T)),
                    tuple(p1[i]), tuple(top_in)]
        body = sweep(list(range(len(p0))), [(0, 1, 2), (0, 2, 3)], point)
        old_volume = parts[pid]['volume_m3']
        fascia = trimesh.boolean.difference([body] + front_cut + [new_stiff[s] for s in steel_cut[side]],
                                            engine='manifold')
        tip_depth = (EDGE_DEPTH + .02 * (Y_EDGE - abs(y_in))) / IN
        record(pid, put(pid, fascia.vertices, fascia.faces),
               basis='Dimensioned edge depth; level soffit to the exterior beam flange as drawn',
               dims=dict(edge_depth_in=9.125, flange_tip_depth_in=round(tip_depth, 3),
                         width_in=round((Y_EDGE - abs(y_in)) / IN, 3), soffit='level'),
               note='Overhang thickening below the 8 in deck: from the deck edge to the outer tip of the exterior beam '
                    'top flange, 9 1/8 in deep at the edge with a level soffit (9.57 in at the flange tip), as in the '
                    'sheet 27 typical section, which governs the deck; the sheet 31 railing Section A-A (9 1/4 in, deck '
                    'drawn without crossfall or beam) is not used. Ends at the end-diaphragm front faces (the diaphragms '
                    'are cast first, sheet 23 note 5), square over the outer 1 ft 6 in (sheet 23); cut around the '
                    'projecting pier bearing stiffeners. Drip bead recess not cut.')
        print(f'{pid}: 8 in strip -> {(Y_EDGE - abs(y_in)) / IN:.3f} in level-soffit overhang, '
              f'volume {old_volume:.4f} -> {fascia.volume:.4f} m3')

    # 6. Pier diaphragms (rows 7-8): channel web on the down-station face of the bent legs, sheet 20 plan.
    probe = hexbolt([0, 0, 0], [1, 0, 0], BOLT_R)
    bv_n, bf_n = len(probe.vertices), len(probe.faces)
    for row, si in [(7, 1), (8, 2)]:
        u = BEARINGS[si]
        for j in range(6):
            y0, y1 = YS[j + 1], YS[j]
            folds = []
            for yb, sigma, rho in [(y0, 1, -1), (y1, -1, 1)]:
                folds.append(np.array([u + K * yb + rho * (T_STIFF + T_PLATE) / 2,
                                       yb + sigma * (TW / 2 + FREE_END + LEG)]))
            a = (folds[1] - folds[0]) / np.linalg.norm(folds[1] - folds[0])
            n = np.array([a[1], -a[0]])                             # up-station normal of the bent-leg plane
            middle = (folds[0] + folds[1]) / 2

            def reflect(vv):
                out = vv.copy()
                s = (vv[:, :2] - middle) @ n
                out[:, :2] -= 2 * s[:, None] * n
                return out

            cid, bid = f'diaphragm_{row}_{j + 1}', f'diaphragm_bolts_{row}_{j + 1}'
            v, f = get(cid)
            s, t = (v[:, :2] - middle) @ n, (v[:, :2] - middle) @ a
            check(len(v) == 16 and abs(s.min() - T_PLATE / 2) < TOL and abs(s.max() - T_PLATE / 2 - FLANGE) < TOL and
                  abs(np.abs(t).max() - CHANNEL / 2) < TOL, f'{cid} channel on the up-station side of the bent legs')
            channel = put(cid, reflect(v), f[:, ::-1])
            record(cid, channel,
                   note='Nominal section dimensions from Nucor p.47; flange taper and root fillets omitted. 5 ft 11 in '
                        'channel between the two bent-plate folds, square-cut and about 19.3 deg to the beam normal in '
                        'plan, as drawn on sheet 20; elevation unchanged. Web on the down-station face of the bent legs, '
                        'flanges toward down-station, as in the sheet 20 plan read in the framing-plan orientation '
                        '(sheet 17).')

            v, f = get(bid)
            check(len(v) == 32 * bv_n and len(f) == 32 * bf_n, f'{bid} 32 bolts')
            v2, f2 = v.copy(), f.copy()
            for k in range(32):
                vs, fs = slice(k * bv_n, (k + 1) * bv_n), slice(k * bf_n, (k + 1) * bf_n)
                check(f[fs].min() >= k * bv_n and f[fs].max() < (k + 1) * bv_n, f'{bid} bolt {k} block')
                block = v[vs]
                axis = np.linalg.eigh(np.cov((block - block.mean(axis=0)).T))[1][:, -1]
                channel_leg = (k % 16) % 4 >= 2                      # per row: 2 stiffener-leg, then 2 channel-leg bolts
                if channel_leg:
                    sb = (block[:, :2] - middle) @ n
                    check(abs(abs(axis[:2] @ n) - 1) < 1e-6 and abs(sb.min() + T_PLATE / 2 + .012) < TOL and
                          abs(sb.max() - T_PLATE / 2 - .4 * IN - .017) < TOL, f'{bid} channel-leg bolt {k}')
                    v2[vs] = reflect(block)
                    f2[fs] = f[fs][:, ::-1]
                else:
                    check(abs(abs(axis[0]) - 1) < 1e-6, f'{bid} stiffener-leg bolt {k}')
            record(bid, put(bid, v2, f2),
                   note='Threads and holes omitted. Per bent plate, 8 bolts through the bearing stiffener (2.5 and 5.5 in '
                        'from the web) and 8 through the channel web (1 1/2 and 4 1/2 in from the leg end, heads on the '
                        'up-station face of the bent leg, nuts inside the channel), four rows at 3 in; 32 per diaphragm, '
                        'sheet 20.')
    print('Pier diaphragms: 12 channels moved to the down-station face of the bent legs; 96 channel-leg bolts reflected')

    # 7. RCBA extensions: 2 in deeper for 2'-0" from the square joint, 45 deg return, on the pavement ledge (sheets 31, 33).
    prof = [(0, -LEDGE_TOP), (THICK_LEN, -LEDGE_TOP), (THICK_LEN + THICK_DROP + IN, -11 * IN), (0, -11 * IN)]
    for end in (-1, 1):
        for side in (-1, 1):
            pid = f'extension_{end}_{side}'
            yy = side * 22.5 * FT
            x0 = end * HALF + K * side * Y_SQ                       # square end = square joint (sheets 23, 32)
            v, f = get(pid)
            rel = v[:, 2] - surface(v[:, 0], v[:, 1])
            check(len(v) == 120 and np.all((np.abs(np.abs(v[:, 1]) - Y_SQ) < TOL) |
                                            (np.abs(np.abs(v[:, 1]) - Y_EDGE) < TOL)), f'{pid} width')
            check(np.all((np.abs(rel) < TOL) | (np.abs(rel + 12 * IN) < TOL)), f'{pid} 12 in')
            inner = v[:, 0].max() if end < 0 else v[:, 0].min()
            check(abs(inner - x0) < TOL, f'{pid} square end at the skew corner')
            ya, yb = sorted([yy - .75 * FT, yy + .75 * FT])

            def block_point(y):
                return [(x0 + end * dd, y, float(surface(x0 + end * dd, y)) + zz) for dd, zz in prof]
            block = sweep([ya, yb], [(0, 1, 2), (0, 2, 3)], block_point)
            old_volume = parts[pid]['volume_m3']
            ext = trimesh.boolean.union([solid(v, f), block], engine='manifold')
            record(pid, put(pid, ext.vertices, ext.faces), basis='Dimensioned',
                   pdf_pages=sorted(set(parts[pid]['pdf_pages']) | {23, 31}),
                   dims=dict(thickness_in=12, end_thickness_in=14, thickened_length_ft=2),
                   note='RCBA extension for the TFC transition, 12 in like the approach slab (sheet 33 note 2); 2 in '
                        'deeper (1 ft 2 in) for 2 ft 0 in from its square end at the bridge joint, where it bears on the '
                        'end-diaphragm pavement ledge, returning at 45 deg (sheet 33 pavement ledge detail; sheet 31 '
                        'railing elevation). Square end on the joint, which is square over the coping zone (sheets 23, '
                        '32). Reinforcement (E609-TBAE-01) not modelled.')
            print(f'{pid}: thickened end, volume {old_volume:.4f} -> {ext.volume:.4f} m3')

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
    (backup / 'sr44-mud_before_review_correction_3.glb').write_bytes(original)
    (backup / 'sr44-mud_manifest_before_review_correction_3.json').write_bytes(raw_manifest)
    path.write_bytes(out_bytes)

    manifest['geometry_review_correction_3'] = TAG
    manifest['revision'] = REVISION
    manifest['geometry_review_correction_3_record'] = dict(
        source='Third round (2026-11): the known deviations of revision 1.2 and the findings of the independent check of '
               'that round, each re-read on the drawings',
        source_pdf_pages=[12, 13, 16, 17, 20, 22, 23, 27, 31, 32, 33],
        printed_sheets=[12, 13, 16, 17, 20, 22, 23, 27, 31, 32, 33],
        historical_source='original_1980_plans.pdf pages 9-10 (end bents: retained cap ends)',
        corrections={
            'Overhang thickening fascia_1, fascia_-1':
                '8 in wide strip, 9 1/8 in parallel to the 2% top -> deck edge to the exterior flange tip (22.005 in), '
                'level soffit 9 1/8 in below the edge (9.57 in at the flange tip); ends at the end-diaphragm front faces '
                '(square over the outer 1\'-6") instead of running through them; cut around the projecting pier bearing '
                'stiffeners (sheet 27 typical section; sheet 23)',
            'Pier diaphragm channels diaphragm_7_*, diaphragm_8_* (12)':
                'web on the up-station face of the bent legs, flanges up-station -> web on the down-station face, '
                'flanges down-station (sheet 20 plan in the framing-plan orientation)',
            'Pier diaphragm bolts diaphragm_bolts_7_*, diaphragm_bolts_8_* (12)':
                '8 channel-leg bolts per diaphragm reflected with the channel (heads on the bent leg, nuts inside the '
                'channel); stiffener-leg bolts unchanged',
            'End diaphragms end_diaphragm_1, end_diaphragm_4':
                'front face, rear face and pavement ledge on the skew to the coping -> square to the roadway over the '
                'outer 1\'-6" at each coping (sheet 23 plan; sheet 31 railing plan)',
            'Deck deck':
                'skew ends to the coping -> square over the outer 1\'-6": corner cut back where the square joint turns '
                'toward the bridge, wedge added where it turns toward the approach (sheets 23, 31)',
            'Barriers rail_1, rail_-1; transitions tfc_*; delineators delineator_*':
                'FC/TFC end at the skew point on the barrier back face -> on the square joint, -/+ 0.1089 m in X '
                '(sheet 31 railing plan)',
            'RCBA extensions extension_-1_-1, extension_-1_1, extension_1_-1, extension_1_1':
                '12 in to the joint (2 in above the pavement ledge) -> 14 in for 2\'-0" from the square joint with a '
                '45 deg return (sheet 33 note 2 and pavement ledge detail; sheet 31 elevation)',
            'Retained end-bent caps cap_1, cap_4':
                'end steps square-ended at 24 ft along the skew -> end at the wing inner faces with the 1\'-0" x 1\'-0" '
                'front splay and the 1\'-3" square rear end (original 1980 plans pages 9-10; sheet 12)',
            'Bearing stiffeners stiffeners_* (28 pairs)':
                'top web-corner clip 2 1/2 in along the flange x 1 1/4 in down the web, no bottom clip -> 1 1/4 in along '
                'the flange x 2 1/2 in along the web at the top and bottom web corners (sheet 22)'},
        decisions={
            'coping-depth-sheet-31':
                'Sheet 27 (superstructure typical section, drawn with the beams and the 2% crossfall) governs the deck: '
                '9 1/8 in at the edge, soffit level to the outer tip of the exterior beam top flange. Sheet 31 Section '
                'A-A is a railing reinforcement detail that draws the deck level and without the beam (9 1/4 in over '
                'a 27 in strip); it is not used for the deck geometry.',
            'pier-diaphragm-arrangement':
                'Fold angle kept at 19.35 deg: the bent plate detail offsets 6 9/16 in and 2 1/4 in locate the outer-face '
                'corner of the bent leg (18.9 deg; drawn at 19.1 deg), and the written beam spacing, skew, stiffener '
                'width and opposite-face legs close only at 19.35 deg. Channel side from the sheet 20 plan read in the '
                'sheet 17 framing-plan orientation (beams horizontal, same skew sense, no north arrow, whereas the rotated '
                'detail plans on sheets 16 and 23 carry north arrows): web on the down-station face of both bent legs. '
                'Stiffener 7 1/4 in from sheet 22 and the sheet 20 elevation over the 7 1/2 in plan label.',
            'end-bent-square-coping-zone':
                'The end-bent faces, deck ends and barrier ends are made square over the outer 1\'-6" (sheets 23, 31, '
                '32); the new diaphragm underside stays at the cap step top + 1/2 in.',
            'end-bent-cap-ends':
                'Retained cap ends from original 1980 page 9 ("1\'-0 (Typical)" front splay, "1\'-3 (Typical)" rear '
                'square end, wing inner face 24.07 ft along the bent = 23\'-3" transverse) with page 10 and sheet 12; '
                'the 1\'-0" x 1\'-0" splay is applied at all four front corners as "Typical", although the sheet 12 '
                'CAD draws it about 1\'-3" x 1\'-4" at Wings A/D. Existing dimensions are approximate (sheet 12 note '
                '2).'},
        resolved_deviations=['approach-extension-ledge', 'end-bent-square-coping-zone', 'end-bent-cap-ends'],
        decided_deviations=['coping-depth-sheet-31', 'pier-diaphragm-arrangement'],
        added_deviations=['pier-stiffener-outer-corners'],
        changed_parts=changes, added_parts=[], removed_parts=[],
        before_glb_sha256=before, after_glb_sha256=hashlib.sha256(out_bytes).hexdigest())
    closed = {'coping-depth-sheet-31', 'pier-diaphragm-arrangement', 'approach-extension-ledge',
              'end-bent-square-coping-zone', 'pier-stiffener-outer-corners', 'end-bent-cap-ends'}
    deviations = [d for d in manifest.get('known_deviations', []) if d.get('id') not in closed]
    deviations.append(dict(
        id='pier-stiffener-outer-corners',
        parts='stiffeners_2_*, stiffeners_3_*',
        source='sheet 22 PIER BEARING DETAILS, SECTION VIEW; standard drawing E 726-BEBP-04/05 (sheet 22 note 9, not in '
               'the set)',
        deviation='The 7 1/4 in pier bearing stiffeners project 2 1/2 in beyond the top and bottom flange tips. The '
                  'section view draws these outer corners sloped, about 2 1/2 in by 1 3/8 in when scaled; the model '
                  'keeps them square.',
        reason='The slope is drawn but not dimensioned; only the web-corner clips are (2 1/2 in x 1 1/4 in). The '
               'standard bearing drawing or the shop drawings would give it.'))
    manifest['known_deviations'] = deviations
    for c in manifest['detail_coverage']:
        if c['feature'] == 'Retained substructure':
            c['detail'] = ('Both wall piers and end bents. Stepped caps and wings are approximate existing envelopes, as '
                           'stated on the plans; end-bent caps end at the wing faces with the 1980 front splays and '
                           'square rear ends. Semi-integral end diaphragms with the 6 in pavement ledge, square to the '
                           'roadway over the outer 1 ft 6 in at each coping.')
    text = json.dumps(manifest, indent=2) + ('\n' if raw_manifest.endswith(b'\n') else '')
    mp.write_text(text, encoding='utf-8', newline='\r\n' if b'\r\n' in raw_manifest else '\n')
    print(json.dumps({k: v for k, v in manifest['geometry_review_correction_3_record'].items()
                      if k in ('before_glb_sha256', 'after_glb_sha256')}))
    print(f'{len(changes)} parts changed; known deviations left: {len(manifest["known_deviations"])}')


if __name__ == '__main__':
    correct()

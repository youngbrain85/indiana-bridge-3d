"""Second drawing-confirmed correction of SR 8 over Yellow River (sr8-yellow); runs after correct_sr8_yellow_review.py.

    python scripts/correct_sr8_yellow_review.py      # first correction (revision 1.1)
    python scripts/correct_sr8_yellow_review_2.py    # this one (revision 1.2)

Source: INDOT B-23076 (1997), data/bridges/sr8-yellow/drawings.pdf. PDF pages 1-20 are printed sheets 1-20; PDF 25 is
shop sheet M1. Native axes: X station (east), Y transverse (north positive: sheet 5 north arrow; sheet 8 north arrow,
Wing "A"/"B" elevations and the 49/41 deg tooth handedness put Wing "A" on the south side of Bent 1), Z = El. - 210.000.
Support lines X = u - tan(49 deg) Y; deck top D(X, Y) = 8.257 - X^2/15240 - 0.02|Y| (as in the first correction).

1. Sawtooth approach face of the integral end bents (sheet 8 Plan and Piling Plan - Bent No. 1, sheet 9 Detail "D" and
   Section "E-E"). The approach face of the 760 mm bent carries triangular projections 755 mm deep (Section E-E: 755 +
   760 = 1515 at the projection; 10M05bE bar 1524 / 1150 / 1000). Their sides are 1150 mm parallel to the roadway
   (41 deg to the bent) and 1000 mm square to it (49 deg), at a pitch of 1.000 m across the roadway. The first face
   parallel to the roadway is 557 mm from the inner face of Wing "A" (plan) and the last full tooth ends 313 mm from
   Wing "B" (piling plan): 0.557 + 11 x 1.000 + 0.313 = 11.870 m between the wings (plan "11870"). Beside Wing "A" a
   557 mm face square to the roadway closes the face; beside Wing "B" a sloped face closes it, ending on the wing about
   0.83 m (measured parallel to the roadway) beyond the last valley (not dimensioned; scaled from both sheet 8 plans).
   The projections run from Bottom of Bent El. 216.100 to the approach-slab bearing level, deck - 0.300 (Section E-E:
   the slab is 300 mm thick over 905 = 755 + 150 mm). Bent 6 is the same by 180 deg rotation.
2. Wing walls (sheet 8 plans, sheet 9 Wing "A"/"B" elevations). The wings stand outside the 5.910 m coping: 25 mm
   expanded polystyrene, then 300 mm of wall, so |Y| = 5.935..6.235 (sheet 8: 1838 + 2245 + 4 @ 2710 + 2245 + 1839 =
   19007 out to out along the bent line; 1206 = 881 + 325 from the exterior beam). Along the roadway they straddle the
   bent line where it crosses the outer face: Wing "A" 2.144 m west / 1.606 m east (plan 1407 / 1054 normal to the
   bent), Wing "B" 1.454 m west / 2.296 m east (954 / 1506). Tops El. 218.056 -> 218.072 (A) and 217.985 -> 218.008
   (B), west to east, linear (sheet 9; plan El. 218.066 / 217.994 at the bent line agree). Bottom El. 216.100.
   The model had the wings inside the coping (|Y| = 5.61..5.91, overlapping the approach slab), wholly on the
   approach side and about 0.1 m low. The bent body now runs to the wing inner faces (|Y| = 5.935; sheet 8 Elevation,
   Type "A" construction joint in the wingwall).
3. Approach slab thickness (sheet 18 Sections A-A and B-B, sheet 19 Section C-C and bill "Cement Conc. Pvmt, Reinf.,
   260 mm"; sheet 9 Sections A-A and E-E). The R.C. approach is 260 mm thick; it thickens to 300 mm only where it
   bears on the end bent (pavement ledge and sawtooth projections). The first correction made it 300 mm throughout.
4. End-span MC460 diaphragms (shop sheet M1: M1H MC460 x 63.5 x 1748 for the 1778 bays, M1J x 1433 for the 1473 bays,
   with two L102 x 102 x 9.5 x 400 angles M1H1, F/F 1763 / 1458 between beam webs; sheet 12 Detail "B": angles on the
   web back of the channel against the beam webs, channel erected so that dimension "A" top and bottom are equal).
   The channels were 1.478 / 1.173 m long, stopped 143 mm short of the webs, had no angles and sat 0.100 m above the
   beams' mid-depth. They are rebuilt at their stations with the M1 lengths, centred in the bay, mid-depth on the
   beams' mid-depth (deck - 0.290 - 0.420) at each end, with the two 400 mm angles centred on the channel depth. The
   channel section envelope of the model is kept; each part mesh holds three closed shells (channel and two angles).

Deferred (unchanged, known_deviations `bent-2-5-seat-steps`): Bent 2 / 5 seat steps (sheet 10).

32 parts change (cap_0, cap_5, four wings, two approach slabs, 24 end-span diaphragms); none is added or removed. The
end bents and approach slabs are built as single closed solids over plan regions (no booleans between touching solids);
only the beam-end pockets are cut with manifold3d, as in the first correction.

Requires numpy, trimesh, shapely and manifold3d, and correct_sr8_yellow_review.py (same folder).
"""
import hashlib
import json
import struct
import sys
from pathlib import Path

import numpy as np
import trimesh
from shapely.geometry import Polygon, box
from shapely.geometry.polygon import orient

sys.path.insert(0, str(Path(__file__).resolve().parent))
from correct_sr8_yellow_review import (APPROACH_START_U, BASE, BENT_BOTTOM_Z, BS, COS, DECK_END_U,  # noqa: E402
                                       PAVEMENT_END_X, ROOT, TAN, YS, deck, sweep, sx)
from correct_sr8_yellow_review import TAG as FIRST_TAG  # noqa: E402

TAG = 'sr8-yellow-review-2-2026-11'
REVISION_BEFORE = '1.1-drawing-review'
REVISION = '1.2-drawing-review-2'
BEFORE_SHA = 'd5b253f0e43c7dd92a6376361fb6e5fa60d45319c43e916974c7e5e53e692b7e'   # after the first correction

HALF_T = 0.38 / COS                    # X offset of the 760 mm bent faces from the bent line (sheet 9 A-A)
DECK_T = DECK_END_U - BS[5]            # X offset of the deck end / Type 1A joint (0.230 normal)
COPING_Y = 5.91                        # 11820 out to out of copings (sheets 5, 8)
WING_IN, WING_OUT = 5.935, 6.235       # 25 mm EPS + 300 mm wing (sheet 8)
TOOTH_Y0 = -WING_IN + 0.557            # first face parallel to the roadway, 557 from Wing "A" (sheet 8 plan)
TOOTH_N = 11                           # 0.557 + 11 x 1.000 + 0.313 = 11.870 (sheet 8)
NORTH_CLOSE_DX = 0.83                  # sloped closure at Wing "B": scaled from sheet 8 (not dimensioned)
BENT_SEAT = 0.30                       # slab bearing level below the deck surface (sheet 9 A-A, E-E)
SLAB_T = 0.26                          # sheets 18, 19
# Wings at Bent 1 (sheet 8 piling plan along the wing, sheet 9 tops): (id, side, west, east, top west, top east, label)
WINGS = [('wing_0_-1', -1, 2.144, 1.606, 218.056, 218.072, 'A'),
         ('wing_0_1', 1, 1.454, 2.296, 217.985, 218.008, 'B')]
BAY_CHANNEL = {1.473: (1.433, 'M1J'), 1.778: (1.748, 'M1H')}   # shop sheet M1
WEB_HALF = 0.00735                     # W840x193 web 14.7 mm (M1: F/F = c/c - 2 x 7.35)
ANGLE_LEG, ANGLE_T, ANGLE_L = 0.102, 0.0095, 0.400               # L102 x 102 x 9.5 x 400 (M1, sheet 12)
BEAM_MID_BELOW_DECK = 0.290 + 0.420    # model girder top at deck - 0.290 (measured); W840 half depth


def rot(poly):
    """Bent 6 = Bent 1 by 180 deg rotation about the structure centre."""
    return Polygon([(-x, -y) for x, y in poly.exterior.coords])


def split_crown(poly):
    """Pieces of a plan polygon on either side of the crown line Y = 0 (the deck crossfall kinks there)."""
    out = []
    for half in (box(-1e3, -1e3, 1e3, 0), box(-1e3, 0, 1e3, 1e3)):
        piece = poly.intersection(half)
        for p in getattr(piece, 'geoms', [piece]):
            if isinstance(p, Polygon) and p.area > 1e-9:
                out.append(p)
    return out


def densify(poly, step=0.5):
    ring = np.asarray(orient(poly, 1.0).exterior.coords)
    pts = []
    for a, b in zip(ring[:-1], ring[1:]):
        n = max(1, int(np.ceil(np.linalg.norm(b - a) / step)))
        pts.extend(a + (b - a) * t for t in np.arange(n) / n)
    return np.asarray(pts)


def terraced(regions, step=0.5):
    """One closed solid over plan regions that tile its footprint, built without booleans.

    regions: (polygon, (bottom key, z(x, y)), (top key, z(x, y))). Neighbouring regions share their boundary
    vertices; vertical walls close the outer boundary, and step faces join neighbours whose bottom or top levels
    differ (levels must not cross along a shared edge)."""
    def key(p):
        return (round(float(p[0]), 7), round(float(p[1]), 7))

    rings = [densify(poly, step) for poly, _, _ in regions]
    canon = {}
    for r in rings:
        for q in r:
            canon.setdefault(key(q), (float(q[0]), float(q[1])))
    pts = np.array(list(canon.values()))
    levels, verts, vid, faces, owner, fixed = {}, [], {}, [], {}, []
    for r, (_, bot, top) in zip(rings, regions):
        out = []
        for i in range(len(r)):
            a, b = np.asarray(canon[key(r[i])]), np.asarray(canon[key(r[(i + 1) % len(r)])])
            out.append(key(a))
            d = b - a
            t = (pts - a) @ d / (d @ d)
            off = np.abs(d[0] * (pts[:, 1] - a[1]) - d[1] * (pts[:, 0] - a[0])) / np.linalg.norm(d)
            on = (t > 1e-9) & (t < 1 - 1e-9) & (off < 1e-7)
            out.extend(key(q) for q in pts[on][np.argsort(t[on])])
        fixed.append(out)
        for k in out:
            for name, fn in (bot, top):
                if (k, name) not in vid:
                    vid[(k, name)] = len(verts)
                    verts.append((canon[k][0], canon[k][1], fn(*canon[k])))
                    levels.setdefault(k, []).append(name)
    for n, out in enumerate(fixed):
        for i in range(len(out)):
            owner[(out[i], out[(i + 1) % len(out)])] = n

    def z(k, name):
        return verts[vid[(k, name)]][2]

    def chain(k, lo, hi):
        z0, z1 = z(k, lo), z(k, hi)
        return sorted((vid[(k, m)] for m in levels[k] if z0 - 1e-9 <= z(k, m) <= z1 + 1e-9), key=lambda v: verts[v][2])

    def wall(a, b):
        """Vertical face between vertex chains a and b (ascending), solid on the left of a -> b."""
        za = [(verts[v][2] - verts[a[0]][2]) / (verts[a[-1]][2] - verts[a[0]][2]) for v in a]
        zb = [(verts[v][2] - verts[b[0]][2]) / (verts[b[-1]][2] - verts[b[0]][2]) for v in b]
        i = j = 0
        while i < len(a) - 1 or j < len(b) - 1:
            if j < len(b) - 1 and (i == len(a) - 1 or zb[j + 1] <= za[i + 1]):
                faces.append((a[i], b[j], b[j + 1]))
                j += 1
            else:
                faces.append((a[i], b[j], a[i + 1]))
                i += 1

    for n, ((poly, bot, top), out) in enumerate(zip(regions, fixed)):
        ring = np.array([canon[k] for k in out])
        vv, ff = trimesh.creation.triangulate_polygon(Polygon(ring), engine='manifold')
        if len(vv) != len(ring) or not np.allclose(vv, ring):
            raise ValueError('triangulation changed the ring')
        ff = np.asarray(ff)
        e1, e2 = vv[ff[:, 1]] - vv[ff[:, 0]], vv[ff[:, 2]] - vv[ff[:, 0]]
        ff = np.where((e1[:, 0] * e2[:, 1] - e1[:, 1] * e2[:, 0] < 0)[:, None], ff[:, ::-1], ff)
        faces.extend(tuple(vid[(out[q], top[0])] for q in tri) for tri in ff)
        faces.extend(tuple(vid[(out[q], bot[0])] for q in tri[::-1]) for tri in ff)
        for i in range(len(out)):
            a, b = out[i], out[(i + 1) % len(out)]
            other = owner.get((b, a))
            if other is None:                                   # outer boundary
                wall(chain(a, bot[0], top[0]), chain(b, bot[0], top[0]))
                continue
            if other < n:
                continue
            obot, otop = regions[other][1][0], regions[other][2][0]
            if obot != bot[0]:
                lo, hi = (bot[0], obot) if z(a, bot[0]) < z(a, obot) else (obot, bot[0])
                if lo == bot[0]:
                    wall(chain(a, lo, hi), chain(b, lo, hi))    # only this region is solid there
                else:
                    wall(chain(b, lo, hi), chain(a, lo, hi))
            if otop != top[0]:
                lo, hi = (otop, top[0]) if z(a, otop) < z(a, top[0]) else (top[0], otop)
                if hi == top[0]:
                    wall(chain(a, lo, hi), chain(b, lo, hi))
                else:
                    wall(chain(b, lo, hi), chain(a, lo, hi))
    m = trimesh.Trimesh(np.asarray(verts), np.asarray(faces), process=False)
    if not (m.is_watertight and m.is_winding_consistent):
        raise ValueError('terraced solid is not closed')
    if m.volume < 0:
        m.invert()
    return m


def strips(poly, width=1.0):
    """A plan polygon cut by lines X = const into strips (keeps planar top facets short) and at the crown."""
    x0, _, x1, _ = poly.bounds
    out = []
    for xa in np.arange(np.floor(x0), x1, width):
        piece = poly.intersection(box(xa, -1e3, xa + width, 1e3))
        for p in getattr(piece, 'geoms', [piece]):
            if isinstance(p, Polygon) and p.area > 1e-9:
                out += split_crown(p)
    return out


def bodies(mesh):
    """Number of connected shells (trimesh's body_count needs scipy)."""
    m = mesh.copy()
    m.merge_vertices()
    parent = np.arange(len(m.vertices))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    for a, b, c in m.faces:
        for q in (b, c):
            ra, rq = find(a), find(q)
            if ra != rq:
                parent[rq] = ra
    return len({find(v) for v in np.unique(m.faces)})


def bent_plan(b):
    """Plan of an integral end bent: (low, high). low = pavement ledge plus sawtooth projections (top at the slab
    bearing level), high = the rest of the 760 mm wall up to the deck soffit. Bent 6 is Bent 1 rotated 180 deg."""
    xf = lambda y: sx(BS[0] - HALF_T, y)          # Bent 1 approach face (west)
    xj = lambda y: sx(BS[0] - DECK_T, y)          # deck end / Type 1A joint line
    xs = lambda y: sx(BS[0] + HALF_T, y)          # span face
    w = WING_IN
    y_last = TOOTH_Y0 + TOOTH_N                   # last valley, 313 from Wing B
    low = [(xj(-w), -w), (xj(w), w), (xf(y_last) - NORTH_CLOSE_DX, w), (xf(y_last), y_last)]
    for k in range(TOOTH_N - 1, -1, -1):          # 1150 face parallel, 1000 face square to the roadway
        y = TOOTH_Y0 + k
        low += [(xf(y + 1), y), (xf(y), y)]
    low += [(xf(TOOTH_Y0), -w)]                   # 557 face square to the roadway beside Wing A
    low, high = Polygon(low), Polygon([(xj(-w), -w), (xs(-w), -w), (xs(w), w), (xj(w), w)])
    if not (low.is_valid and high.is_valid):
        raise ValueError('invalid bent plan')
    return (rot(low), rot(high)) if b == 5 else (low, high)


def correct():
    mp = BASE / 'model_manifest.json'
    manifest = json.loads(mp.read_text(encoding='utf-8'))
    if manifest.get('review_correction_2') == TAG:
        print('Already corrected.')
        return
    if manifest.get('review_correction') != FIRST_TAG or manifest.get('revision') != REVISION_BEFORE:
        raise ValueError('run scripts/correct_sr8_yellow_review.py first (revision 1.1 expected)')
    path = BASE / 'model.glb'
    original = path.read_bytes()
    before = hashlib.sha256(original).hexdigest()
    if before != BEFORE_SHA or manifest['review_correction_record']['after_glb_sha256'] != BEFORE_SHA:
        raise ValueError('model.glb is not the output of the first correction')
    length = struct.unpack_from('<I', original, 12)[0]
    gltf = json.loads(original[20:20 + length])
    binary = bytearray(original[28 + length:])
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

    def native(pid):
        """Mesh of a part in native axes; GLB stores (X, Z, -Y)."""
        prim = meshes[pid]['primitives'][0]
        s = read(prim['attributes']['POSITION']).astype(np.float64)
        return trimesh.Trimesh(np.c_[s[:, 0], -s[:, 2], s[:, 1]], read(prim['indices']).reshape(-1, 3), process=False)

    changes = []

    def store(pid, solid, note, name=None, **dims):
        if not solid.is_watertight or solid.volume <= 0:
            raise ValueError(f'{pid}: invalid corrected solid')
        prim = meshes[pid]['primitives'][0]
        color = read(prim['attributes']['COLOR_0'])[0]
        v = np.asarray(solid.vertices, dtype=np.float64)
        prim['attributes'] = {'POSITION': append(np.c_[v[:, 0], v[:, 2], -v[:, 1]].astype('<f4'), 'VEC3', 5126),
                              'COLOR_0': append(np.tile(color, (len(v), 1)).astype('u1'), 'VEC4', 5121)}
        gltf['accessors'][prim['attributes']['COLOR_0']]['normalized'] = True
        prim['indices'] = append(np.asarray(solid.faces).reshape(-1, 1).astype('<u4'), 'SCALAR', 5125)
        p = parts[pid]
        p['bounds_m'] = np.round(solid.bounds, 6).tolist()
        p['volume_m3'] = round(float(solid.volume), 9)
        p['dimensions'].update(dims)
        if name:
            p['name'] = name
        p['note'] = (p.get('note', '') + ' ' + note).strip()
        changes.append(pid)

    def expect(cond, what):
        if not cond:
            raise ValueError('Model is not in the expected state after the first correction: ' + what)

    # ---- Starting-state checks ------------------------------------------------------------------------------
    for b in (0, 5):
        c = native(f'cap_{b}')
        expect(np.allclose(c.bounds[:, 1], [-COPING_Y, COPING_Y], atol=1e-5) and abs(c.bounds[0, 2] - 6.1) < 1e-5,
               f'cap_{b}')
        for side in (-1, 1):
            w = native(f'wing_{b}_{side}').bounds
            expect(np.allclose(np.sort(np.abs(w[:, 1])), [5.61, 5.91], atol=1e-5) and abs(w[0, 2] - 6.1) < 1e-5,
                   f'wing_{b}_{side}')
    for s in (-1, 1):
        a = native(f'approach_{s}')
        expect(abs(a.bounds[0 if s < 0 else 1, 0] - s * PAVEMENT_END_X) < 1e-4 and
               abs(parts[f'approach_{s}']['dimensions'].get('thickness_m', 0) - 0.3) < 1e-9, f'approach_{s}')
    for i in (0, 4):
        for row in (0, 2):
            for j in range(6):
                d = native(f'diaphragm_{i}_{row}_{j}').bounds
                expect(np.allclose(d[:, 1], [YS[j] + 0.15, YS[j + 1] - 0.15], atol=1e-4) and
                       abs(d[1, 2] - d[0, 2] - 0.46) < 1e-4, f'diaphragm_{i}_{row}_{j}')

    # ---- 1 + 2: end bents with sawtooth projections, wings ----------------------------------------------------
    bottom = ('bottom', lambda x, y: BENT_BOTTOM_Z)
    seat = ('seat', lambda x, y: deck(x, y) - BENT_SEAT)
    soffit = ('soffit', lambda x, y: deck(x, y) - 0.2)
    for b in (0, 5):
        low, high = bent_plan(b)
        solid = terraced([(q, bottom, seat) for q in split_crown(low)] +
                         [(q, bottom, soffit) for q in split_crown(high)])
        if bodies(solid) != 1:
            raise ValueError(f'cap_{b}: invalid solid')
        span = 0 if b == 0 else 4
        bent = trimesh.boolean.difference([solid] + [native(f'beam_{span}_{j}') for j in range(7)], engine='manifold')
        old = native(f'cap_{b}').volume
        if not bent.is_watertight or not solid.volume - 0.2 < bent.volume < solid.volume:
            raise ValueError(f'cap_{b}: invalid beam-end cut')
        store(f'cap_{b}', bent,
              'Second correction: sawtooth approach face of sheet 8 (Plan and Piling Plan) and sheet 9 (Detail D, '
              'Section E-E): triangular projections 755 mm deep with 1150 mm sides parallel and 1000 mm sides square '
              'to the roadway, first face 557 mm from Wing A, last tooth 313 mm from Wing B, from El. 216.100 to the '
              'approach-slab bearing level (deck - 0.300); the sloped closure at Wing B is scaled (not dimensioned). '
              'Bent ends extended to the wing inner faces (|Y| = 5.935).',
              approach_face='sawtooth: 11 projections 1.150 x 1.000 m (755 mm deep) plus end closures',
              projection_depth_m=0.755, end_y_m=WING_IN)
        print(f'cap_{b}: {old:.3f} -> {bent.volume:.3f} m3')

    for pid, side, west, east, top_w, top_e, label in WINGS:
        for b in (0, 5):
            yi, yo = side * WING_IN, side * WING_OUT
            xc = sx(BS[0], side * WING_OUT)       # bent line on the wing's outer face, Bent 1
            xw, xe, zw, ze = xc - west, xc + east, top_w - 210, top_e - 210
            if b == 5:                            # 180 deg rotation
                yi, yo, xw, xe, zw, ze = -yi, -yo, -xe, -xw, ze, zw
            wid = f'wing_5_{-side}' if b == 5 else pid
            ztop = lambda x, xw=xw, xe=xe, zw=zw, ze=ze: zw + (ze - zw) * (x - xw) / (xe - xw)
            wing = sweep([(yi, 0), (yo, 0), (yo, 1), (yi, 1)], [xw, xe],
                         lambda x, y, c, ztop=ztop: (x, y, BENT_BOTTOM_Z if c == 0 else ztop(x)))
            where = 'south' if yi < 0 else 'north'
            store(wid, wing,
                  f'Second correction: Wing "{label}" relocated to sheet 8 (outside the coping: 25 mm EPS + 300 mm, '
                  f'|Y| = 5.935-6.235; {west if b == 0 else east:.3f} m west / {east if b == 0 else west:.3f} m east of '
                  f'the bent line on the outer face) with the sheet 9 top El. {top_w:.3f} -> {top_e:.3f} '
                  f'(west -> east at Bent 1; Bent 6 by 180 deg rotation).',
                  name=f'Bent {b + 1} | Wing "{label}" ({where})',
                  length_m=3.75, thickness_m=0.3, bottom_el_m=216.1, inner_face_y_m=round(yi, 3),
                  top_el_m=[round(zw + 210, 3), round(ze + 210, 3)])
            parts[wid]['pdf_pages'] = [8, 9]
            parts[wid]['basis'] = 'Dimensioned wing position, length, thickness and top elevations; reinforcement omitted'

    # ---- 3: approach slabs 260 mm, 300 mm over the end bent ---------------------------------------------------
    for s in (-1, 1):
        pid = f'approach_{s}'
        x_end = s * PAVEMENT_END_X

        core = Polygon([(sx(s * APPROACH_START_U, -5.46), -5.46), (x_end, -5.46), (x_end, 5.46),
                        (sx(s * APPROACH_START_U, 5.46), 5.46)])
        plan = core
        for g in (-1, 1):                              # 450 mm curb strips, 5.030 m from the core-edge deck end
            xc = s * DECK_END_U - TAN * g * 5.31 + s * 5.03
            y0, y1 = sorted((g * 5.46, g * COPING_Y))
            plan = plan.union(Polygon([(sx(s * APPROACH_START_U, y0), y0), (xc, y0), (xc, y1),
                                       (sx(s * APPROACH_START_U, y1), y1)]))
        low, _ = bent_plan(0 if s < 0 else 5)
        on_bent, rest = plan.intersection(low), plan.difference(low)
        surface = ('surface', lambda x, y: deck(x, y))
        regions = [(q, seat, surface) for q in strips(on_bent)] + \
                  [(q, ('base', lambda x, y: deck(x, y) - SLAB_T), surface) for q in strips(rest)]
        merged = terraced(regions)
        expected = plan.area * SLAB_T + on_bent.area * (BENT_SEAT - SLAB_T)
        if bodies(merged) != 1 or abs(merged.volume - expected) > 1e-6:
            raise ValueError(pid + ': invalid slab')
        old = native(pid).volume
        store(pid, merged,
              'Second correction: 260 mm thick (sheets 18-19 sections and bill "Cement Conc. Pvmt, Reinf., 260 mm"), '
              'thickened to 300 mm where it bears on the end-bent ledge and sawtooth projections (sheet 9 A-A, E-E).',
              thickness_m=SLAB_T, thickness_over_end_bent_m=BENT_SEAT)
        parts[pid]['pdf_pages'] = [7, 9, 18, 19]
        parts[pid]['basis'] = ('Dimensioned plan outline and thickness; bottom chamfer at the bent and pavement '
                               'support simplified')
        print(f'{pid}: {old:.3f} -> {merged.volume:.3f} m3 (plan {plan.area:.3f} m2, on the bent {on_bent.area:.3f} m2)')

    # ---- 4: end-span MC460 diaphragms with connection angles --------------------------------------------------
    for i in (0, 4):
        for row in (0, 2):
            for j in range(6):
                pid = f'diaphragm_{i}_{row}_{j}'
                d = native(pid)
                (x0, _, z0), (x1, _, z1) = d.bounds
                xs = (x0 + x1) / 2
                vx = np.round(d.vertices[:, 0] - x0, 4)
                vz = np.round(d.vertices[:, 2] - z0, 4)
                depth, bf = round(z1 - z0, 4), round(x1 - x0, 4)
                tw = float(np.unique(vx)[1])
                tf = float(np.unique(vz)[1])
                web_min = bool(((vx == round(tw, 4)) & (vz == round(tf, 4))).any())
                expect(depth == 0.46 and np.isclose(bf, 0.13) and np.isclose(tw, 0.014) and np.isclose(tf, 0.014)
                       and web_min, pid + ' section (web on the -X side)')
                bay = round(YS[j + 1] - YS[j], 3)
                length, mark = BAY_CHANNEL[bay]
                yc = (YS[j] + YS[j + 1]) / 2
                mids = [deck(xs, YS[j]) - BEAM_MID_BELOW_DECK, deck(xs, YS[j + 1]) - BEAM_MID_BELOW_DECK]
                zmid = lambda y, mids=mids, j=j: mids[0] + (mids[1] - mids[0]) * (y - YS[j]) / (YS[j + 1] - YS[j])
                # Web on the -X side, flanges toward +X (all 24); the angles sit on the web back (sheet 12 plan).
                sec = [(x0, 0), (x1, 0), (x1, tf), (x0 + tw, tf), (x0 + tw, depth - tf), (x1, depth - tf),
                       (x1, depth), (x0, depth)]
                xw, dx = x0, -1
                ya, yb = yc - length / 2, yc + length / 2
                channel = sweep(sec, [ya, yb], lambda y, x, zr, zmid=zmid: (x, y, zmid(y) - depth / 2 + zr))
                angles = []
                for yweb, dy in ((YS[j] + WEB_HALF, 1), (YS[j + 1] - WEB_HALF, -1)):
                    leg = Polygon([(xw, yweb), (xw, yweb + dy * ANGLE_LEG), (xw + dx * ANGLE_T, yweb + dy * ANGLE_LEG),
                                   (xw + dx * ANGLE_T, yweb + dy * ANGLE_T), (xw + dx * ANGLE_LEG, yweb + dy * ANGLE_T),
                                   (xw + dx * ANGLE_LEG, yweb)])
                    zc = zmid(yweb)
                    angles.append(terraced([(leg, ('b', lambda x, y, zc=zc: zc - ANGLE_L / 2),
                                                   ('t', lambda x, y, zc=zc: zc + ANGLE_L / 2))]))
                # Three closed shells (channel and two angles bearing on its web), as the model's bearings and splices.
                assembly = trimesh.util.concatenate([channel] + angles)
                if (not assembly.is_watertight or bodies(assembly) != 3 or
                        abs(assembly.volume - channel.volume - sum(a.volume for a in angles)) > 1e-9):
                    raise ValueError(pid + ': invalid assembly')
                old_mid = (z0 + z1) / 2
                store(pid, assembly,
                      f'Second correction: shop sheet M1 {mark} MC460 x 63.5 x {length * 1000:.0f} (was '
                      f'{d.bounds[1, 1] - d.bounds[0, 1]:.3f} m, 143 mm short of each web), centred in the bay with '
                      f'two L102 x 102 x 9.5 x 400 connection angles (M1H1) on the web back against the beam webs; '
                      f'mid-depth on the beams\' mid-depth at each end (sheet 12 Detail B, "A" equal top and bottom; '
                      f'was {old_mid - np.mean(mids):+.3f} m).',
                      name=parts[pid]['name'].replace('MC460 channel diaphragm', f'MC460 channel diaphragm {mark}'),
                      length_m=length, shop_mark=mark, connection_angles='2 x L102x102x9.5 x 400 (M1H1)')
                parts[pid]['pdf_pages'] = [11, 12, 25]
                parts[pid]['basis'] = ('Shop-sheet channel length and connection angles at dimensioned framing-plan '
                                       'station; channel section envelope and bolts simplified')

    for pid in changes:
        meshes[pid]['extras'].update(parts[pid])

    # ---- Write ---------------------------------------------------------------------------------------------------
    gltf['buffers'][0]['byteLength'] = len(binary)
    while len(binary) % 4:
        binary.append(0)
    encoded = json.dumps(gltf, ensure_ascii=True, separators=(',', ':')).encode()
    encoded += b' ' * ((-len(encoded)) % 4)
    out = (struct.pack('<III', 0x46546c67, 2, 28 + len(encoded) + len(binary)) +
           struct.pack('<II', len(encoded), 0x4e4f534a) + encoded + struct.pack('<II', len(binary), 0x004e4942) + binary)
    backup = ROOT / 'data/fem_research'
    backup.mkdir(exist_ok=True)
    (backup / 'sr8_yellow_before_review_correction_2.glb').write_bytes(original)
    (backup / 'sr8_yellow_manifest_before_review_correction_2.json').write_bytes(mp.read_bytes())
    path.write_bytes(out)
    manifest['review_correction_2'] = TAG
    manifest['revision'] = REVISION
    manifest['review_correction_2_record'] = dict(
        source_pdf_pages=[8, 9, 11, 12, 18, 19, 25],
        printed_sheets='PDF pages 1-20 are printed sheets 1-20; PDF 25 is shop sheet M1',
        findings={
            'F1': 'End bents 1/6: sawtooth approach-face projections 755 mm deep, El. 216.100 to deck - 0.300; bent '
                  'ends to the wing inner faces (sheet 8 plans, sheet 9 Detail D and Section E-E)',
            'N1': 'Wings outside the coping (|Y| 5.935-6.235), straddling the bent line 2.144/1.606 (A) and 1.454/2.296 '
                  '(B) m, tops El. 218.056-218.072 (A) and 217.985-218.008 (B) (sheets 8, 9)',
            'N3/F3': 'Approach slabs 260 mm, 300 mm over the end-bent ledge and projections (sheets 9, 18, 19)',
            'N2/F4': 'End-span MC460 diaphragms 1748 (M1H) / 1433 (M1J) with two L102x102x9.5x400 angles, centred on '
                     'the beam mid-depth (M1, sheet 12 Detail B)'},
        deferred={'F5': 'Bent 2 / 5 seat steps: unchanged, known_deviations bent-2-5-seat-steps'},
        changed_parts=changes, removed_parts=[], added_parts=[],
        before_glb_sha256=before, after_glb_sha256=hashlib.sha256(out).hexdigest())
    mp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in manifest['review_correction_2_record'].items() if k != 'changed_parts'}))
    print(len(changes), 'parts changed')


if __name__ == '__main__':
    correct()

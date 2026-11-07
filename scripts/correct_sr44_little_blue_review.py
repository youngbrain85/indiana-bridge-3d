"""One-time, drawing-confirmed correction of SR 44 over the Branch of Little Blue River after an external model
review, preserving unrelated GLB buffers.

    python scripts/correct_sr44_little_blue_review.py

Drawing evidence (INDOT B-44483, drawings.pdf; printed sheet numbers equal PDF page numbers). Lengths not written as
a dimension were scaled from the vector geometry of sheet 18 (1/4 in = 1 ft, 18 PDF points per foot) and agree with
the written dimensions to about 1 mm.

- Sheet 11, profile: P.V.I. 507+10.00, El. 879.00, 170 ft vertical curve, +0.730 % / -0.622 %, so the curve ends at
  507+95 and the -0.622 % tangent continues east of it. Paving exception 507+38.56 to 508+11.44 (the approach slab
  ends on the centreline); railing pay limits 507+23.99 to 507+69.74 (north) and 507+63.99 to 508+26.00 (south).
- Sheet 12, general plan: C/L Bent 1 Sta. 507+60.00 P.G. El. 878.64, C/L Bent 2 Sta. 507+90.00 P.G. El. 878.50;
  "20'-6" Min. Reinf. Conc. Br. Appr. (Typ.)"; the skewed approach ends cross the roadway faces at +18.56/+58.56 and
  507+91.44/508+31.44, i.e. at 20'-6" from the slab ends; bent bottoms El. 870.97 / 870.83.
- Sheet 16, Bent 2: Wing D is a 12'-0" wall, 1'-0" thick, set 2'-9" outside the coping with a 90 degree corner, joined
  to the bent end by a 4'-1 1/8" by 3'-8" block (1" outside the coping); Section D-D top El. 878.12 at the bent end,
  Wing D elevation El. 878.06 at the tip, bottom El. 870.83.
- Sheet 17, End Bent Detail: the bridge floor is cast on the bent (integral); the bent top is the slab soffit.
- Sheet 18, Railing Plan / North and South Railing Elevations / Railing Typical Section: north rail 15'-8" TFC +
  15'-7 3/8" FC + 15'-8" TFC, the FC starting at the west deck joint on the roadway face and the east TFC stopping 2"
  short of the slab end; south rail 15'-8" TFC + 31'-10 5/8" FC + 15'-8" TFC; all end planes square to the roadway,
  and the slab and approach joints are square under them in the rail zone. "Top of Railing" is level at 2'-9" over
  every TFC; inside the TFC the knee falls from 10" to 3" over 7'-2" and the 3" toe ends 11'-5" from the FC, where the
  plan width has tapered from 1'-4" to 9". The approach extension under each TFC ends 2" beyond it; elsewhere the
  approach slab lies between the roadway faces. FC section: 2'-9" high, 1'-4" base, 9" top, 3" vertical toe, knee
  11" from the back at 10" height.

Model changes (review findings F1-F7):
- F7: one vertical datum, Z = 3 m + 0.3048 (El. ft - 878.64), the datum already used for the bent bottoms and pile
  tips. The as-built grade put Z = 3 m at 507+75 (P.G. 878.58), so everything set from the profile was 18.35 mm
  high, and it continued the parabola past 507+95 (up to 17 mm low at the east approach end). The deck, approaches,
  rails, joints, guardrail runs, bent tops and the tops of Wings A-C follow the corrected surface; bent bottoms, pile
  envelopes and wing bottoms are unchanged.
- F3: both integral bents rebuilt with their tops on the crowned slab soffit (S - 20 in); the 138 mm wedge of air at
  the crown is closed.
- F1: approach slabs rebuilt with skewed outer ends 20'-6" beyond the slab ends, between the roadway faces, plus the
  TFC extension under each TFC (2" beyond its end).
- F5/F2/F6: the six concrete railing parts rebuilt with square ends on the sheet 18 chains, the FC section of the
  typical section, and full-height TFC transitions; the slab ends in the rail zone are made square as drawn (north
  coping 31'-5 3/8", south 31'-10 5/8"). The four representative guardrail runs move with the TFC ends.
- F4: Wing D rebuilt to the sheet 16 outline and top elevations.

Requires numpy, trimesh, shapely and manifold3d (polygon triangulation).
"""
import hashlib
import json
import struct
import sys
from pathlib import Path

import numpy as np
import trimesh
from shapely.geometry import LineString, MultiLineString, Polygon
from shapely.geometry.polygon import orient
from shapely.ops import split

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from bridge_geometry import box, concat, rectangular_bar  # noqa: E402

BID = 'sr44-little-blue'
BASE = ROOT / 'data/bridges' / BID
BACKUP = ROOT / 'data/fem_research'
TAG = 'drawing-review-datum-rails-approaches-wing-d'
REVISION = '1.1-drawing-review'
FT, IN = .3048, .0254

# Sheet 11 profile and the local datum (Z = 3 m at El. 878.64, as for the bent bottoms).
STA0 = 50775.0                                   # X = 0 at 507+75, C/L structure (sheet 12)
BVC, EVC, E_BVC = 50625.0, 50795.0, 879.00 - .0073 * 85
E_EVC = 879.00 - .00622 * 85
DATUM_EL = 878.64

# Plan geometry (sheets 12, 16, 18).
HALF_DECK = (31 + 10.625 / 12) * FT / 2          # 4.859338 m, half of 31'-10 5/8" along the roadway
U_APPROACH = HALF_DECK + 20.5 * FT               # 11.107738 m, approach outer end
COPING, FACE, RAIL_BACK = 21.5 * FT, 20 * FT, (21.5 - 2 / 12) * FT
BENT_U, BENT_HALF = 15 * FT, (2 + 10 / 12) * FT / 2 / np.cos(np.radians(45))
SLAB, APPROACH_T, JOINT_T = 20 * IN, 12 * IN, .06
TFC_L, FC_N, FC_S = (15 + 8 / 12) * FT, (15 + 7.375 / 12) * FT, (31 + 10.625 / 12) * FT
NW_FC = -HALF_DECK - FACE                        # north FC starts at the west joint on the roadway face
SW_FC = -HALF_DECK + FACE
CHAINS = {1: [NW_FC - TFC_L, NW_FC, NW_FC + FC_N, NW_FC + FC_N + TFC_L],
          -1: [SW_FC - TFC_L, SW_FC, SW_FC + FC_S, SW_FC + FC_S + TFC_L]}
NE_SLAB_END = CHAINS[1][3] + 2 * IN               # "2"" between the east TFC and the square slab end
EXTENSION = 2 * IN                                # approach extension beyond each TFC (sheet 18 elevations)
FC_SECTION = [(0, 0), (16, 0), (16, 3), (11, 10), (9, 33), (0, 33)]   # inches, q from the back face
TFC_KNEE, TFC_TOE = 7 + 2 / 12, 11 + 5 / 12      # ft from the FC end (sheet 18 elevation, plan)
WING_D = dict(length=12 * FT, block=(4 + 1.125 / 12) * FT, wall=1 * FT, offset=(2 + 9 / 12) * FT,
              top_bent_el=878.12, top_tip_el=878.06, bottom_el=870.83)   # sheet 16; offset = coping to wall


def pg_ft(x):
    """Profile grade (ft) at native X (m) from the sheet 11 vertical curve and its tangents."""
    sta = STA0 + np.asarray(x, float) / FT
    t = sta - BVC
    curve = E_BVC + .0073 * t + (-.00622 - .0073) * t * t / (2 * 170)
    return np.where(sta <= EVC, curve, E_EVC - .00622 * (sta - EVC))


def z_el(el):
    return 3 + FT * (np.asarray(el, float) - DATUM_EL)


def grade(x):
    return z_el(pg_ft(x))


def surface(x, y):
    return grade(x) - .02 * np.abs(np.asarray(y, float))


def old_grade(x):
    """The as-built grade of build_remaining_virginia_slab.py: Z = 3 m at X = 0, parabola everywhere."""
    t = 150 + np.asarray(x, float) / FT
    f = .0073 * t + (-.00622 - .0073) * t * t / (2 * 170)
    return 3 + (f - (.0073 * 150 + (-.00622 - .0073) * 150 * 150 / 340)) * FT


def old_surface(x, y):
    return old_grade(x) - .02 * np.abs(np.asarray(y, float))


def drape(points, top, bottom, step=.5, ylines=(0.0,)):
    """Closed solid over a plan polygon; top and bottom follow callables of (x, y), sampled on a plan grid."""
    poly = orient(Polygon(points), 1.0)
    if not poly.is_valid or poly.area <= 0:
        raise ValueError('invalid plan polygon')
    x0, y0, x1, y1 = poly.bounds
    cuts = [LineString([(x, y0 - 1), (x, y1 + 1)]) for x in np.arange(np.ceil(x0 / step) * step, x1, step)
            if x0 + 1e-6 < x < x1 - 1e-6]
    cuts += [LineString([(x0 - 1, y), (x1 + 1, y)]) for y in ylines if y0 + 1e-6 < y < y1 - 1e-6]
    pieces = list(split(poly, MultiLineString(cuts)).geoms) if cuts else [poly]
    key, xy, tris = {}, [], []

    def vid(p):
        k = (round(float(p[0]), 7), round(float(p[1]), 7))
        if k not in key:
            key[k] = len(xy)
            xy.append(k)
        return key[k]

    for piece in pieces:
        vv, ff = trimesh.creation.triangulate_polygon(orient(piece, 1.0), engine='manifold')
        for f in ff:
            ids = [vid(vv[i]) for i in f]
            if len(set(ids)) < 3:
                continue
            a, b, c = (np.array(xy[i]) for i in ids)
            area = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
            if abs(area) < 1e-12:
                continue
            tris.append(ids if area > 0 else ids[::-1])
    xy = np.array(xy)
    n = len(xy)
    top_z, bottom_z = top(xy[:, 0], xy[:, 1]), bottom(xy[:, 0], xy[:, 1])
    if np.any(top_z - bottom_z <= 0):
        raise ValueError('non-positive depth')
    vertices = np.vstack([np.c_[xy, top_z], np.c_[xy, bottom_z]])
    faces = [list(t) for t in tris] + [[c + n, b + n, a + n] for a, b, c in tris]
    count = {}
    for t in tris:
        for a, b in zip(t, t[1:] + t[:1]):
            count[frozenset((a, b))] = count.get(frozenset((a, b)), 0) + 1
    for t in tris:
        for a, b in zip(t, t[1:] + t[:1]):
            if count[frozenset((a, b))] == 1:
                faces += [[a, a + n, b + n], [a, b + n, b]]
    solid = trimesh.Trimesh(vertices, np.array(faces), process=False)
    if not solid.is_watertight or not solid.is_winding_consistent or solid.volume <= 0:
        raise ValueError('drape produced an invalid solid')
    return solid


def loft(sections, side):
    """Rail solid from (X, [(q, h) inches]) sections; q from the back face at Y = side * RAIL_BACK, Z = S + h."""
    n = len(sections[0][1])
    vertices = []
    for x, section in sections:
        for q, h in section:
            y = side * (RAIL_BACK - q * IN)
            vertices.append((x, y, float(surface(x, y)) + h * IN))
    faces = []
    for k in range(len(sections) - 1):
        for j in range(n):
            a, b = k * n + j, k * n + (j + 1) % n
            faces += [[a, b, b + n], [a, b + n, a + n]]
    # Every FC/TFC section is star-shaped from its back-bottom corner (vertex 0): fan the end caps from it,
    # wound opposite to the adjoining side faces.
    last = (len(sections) - 1) * n
    faces += [[0, j + 1, j] for j in range(1, n - 1)] + [[last, last + j, last + j + 1] for j in range(1, n - 1)]
    solid = trimesh.Trimesh(np.array(vertices), np.array(faces), process=False)
    if solid.volume < 0:
        solid.invert()
    if not solid.is_watertight or not solid.is_winding_consistent or solid.volume <= 0:
        raise ValueError('loft produced an invalid solid')
    return solid


def stations(a, b, step=.3, breaks=()):
    pts = set(np.linspace(a, b, max(2, int(np.ceil(abs(b - a) / step)) + 1)).round(9).tolist())
    pts |= {round(p, 9) for p in breaks if min(a, b) < p < max(a, b)}
    return sorted(pts, reverse=a > b)


def tfc_section(s_ft):
    """TFC section at s_ft from the FC end: base 16 in -> 9 in over 11'-5", knee 10 in -> 3 in over 7'-2"."""
    w = 16 - 7 * min(s_ft, TFC_TOE) / TFC_TOE
    toe, top = np.array([w, 3.0]), np.array([9.0, 33.0])
    if s_ft <= TFC_KNEE:
        end_toe = np.array([16 - 7 * TFC_KNEE / TFC_TOE, 3.0])
        end_knee = end_toe + (top - end_toe) / 300
        knee = np.array([11.0, 10.0]) + (end_knee - np.array([11.0, 10.0])) * s_ft / TFC_KNEE
    else:
        knee = toe + (top - toe) / 300           # the knee has reached the toe: face runs from the toe to the top
    return [(0, 0), (w, 0), (w, 3), tuple(knee), (9, 33), (0, 33)]


def tfc(side, end):
    chain = CHAINS[side]
    joint, outer = (chain[1], chain[0]) if end < 0 else (chain[2], chain[3])
    sign = 1 if outer > joint else -1
    s_breaks = [joint + sign * TFC_KNEE * FT, joint + sign * TFC_TOE * FT]
    return loft([(x, tfc_section(abs(x - joint) / FT)) for x in stations(joint, outer, breaks=s_breaks)], side)


def fc(side):
    chain = CHAINS[side]
    return loft([(x, FC_SECTION) for x in stations(chain[1], chain[2])], side)


def skew_x(u, y):
    return u - y


def plans():
    j = HALF_DECK
    deck = [(skew_x(-j, FACE), FACE), (skew_x(-j, -FACE), -FACE), (SW_FC, -COPING), (CHAINS[-1][2], -COPING),
            (skew_x(j, -FACE), -FACE), (NE_SLAB_END, j - NE_SLAB_END), (NE_SLAB_END, COPING), (NW_FC, COPING)]
    approach_1 = [(skew_x(-U_APPROACH, FACE), FACE), (CHAINS[1][0] - EXTENSION, FACE),
                  (CHAINS[1][0] - EXTENSION, COPING), (NW_FC, COPING), (skew_x(-j, FACE), FACE),
                  (skew_x(-j, -FACE), -FACE), (SW_FC, -COPING), (CHAINS[-1][0] - EXTENSION, -COPING),
                  (CHAINS[-1][0] - EXTENSION, -FACE), (skew_x(-U_APPROACH, -FACE), -FACE)]
    approach_2 = [(skew_x(j, FACE), FACE), (skew_x(U_APPROACH, FACE), FACE), (skew_x(U_APPROACH, -FACE), -FACE),
                  (CHAINS[-1][3] + EXTENSION, -FACE), (CHAINS[-1][3] + EXTENSION, -COPING),
                  (CHAINS[-1][2], -COPING), (skew_x(j, -FACE), -FACE)]
    return deck, approach_1, approach_2


def parallelogram(u0, u1, y0, y1):
    return [(skew_x(u0, y0), y0), (skew_x(u1, y0), y0), (skew_x(u1, y1), y1), (skew_x(u0, y1), y1)]


def wing_d_plan():
    d = WING_D
    x_east = skew_x(BENT_U + BENT_HALF, COPING)   # block east face = bent 2 outer face at the coping
    x_west = x_east - d['block']
    x_tip = x_west + d['length']
    inner = COPING + d['offset']
    outer = inner + d['wall']                     # 3'-9" = 1" + 3'-8" outside the coping
    corner = skew_x(BENT_U - BENT_HALF, COPING)   # bent 2 inner face at the coping; 1 in chamfer to the block
    return [(corner, COPING), (x_east, COPING), (x_east, inner), (x_tip, inner), (x_tip, outer),
            (x_west, outer), (x_west, COPING + 1 * IN)], x_west, x_tip


def guardrail(side, end):
    """Representative 2 m run (four posts and a flat strip, as built) starting at the slab end beyond the TFC."""
    chain = CHAINS[side]
    start = (chain[0] - EXTENSION) if end < 0 else (chain[3] + EXTENSION)
    edge = side * (COPING - .20)
    first = start + end * .055
    members = []
    for x in np.linspace(first, first + end * 2.0, 4):
        z = float(surface(x, edge))
        members.append(box(x - .055, x + .055, edge - .05, edge + .05, z - .25, z + .7))
    xs = [first, first + end * 2.0]
    members.append(rectangular_bar([xs[0], edge, float(surface(xs[0], edge)) + .65],
                                   [xs[1], edge, float(surface(xs[1], edge)) + .65], .06, .30))
    m = concat(members)                          # trimesh boxes: closed and outward-wound, as in the build
    m.remove_unreferenced_vertices()
    if not m.is_watertight or not m.is_winding_consistent or m.volume <= 0:
        raise ValueError('invalid guardrail run')
    return m


def correct():
    mp = BASE / 'model_manifest.json'
    raw_manifest = mp.read_bytes().decode('utf-8')
    newline = '\r\n' if '\r\n' in raw_manifest else '\n'
    final_newline = raw_manifest.endswith('\n')
    manifest = json.loads(raw_manifest)
    if manifest.get('review_correction') == TAG:
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

    def native(pid):
        prim = meshes[pid]['primitives'][0]
        v = read(prim['attributes']['POSITION']).astype(np.float64)
        return trimesh.Trimesh(np.c_[v[:, 0], -v[:, 2], v[:, 1]], read(prim['indices']).reshape(-1, 3), process=False)

    # --- The model must be in the reviewed (as-built) state. ---
    def expect(ok, what):
        if not ok:
            raise ValueError(f'{BID}: unexpected original model ({what})')

    deck0 = native('deck')
    d = deck0.vertices
    expect(np.allclose(np.minimum(abs(d[:, 2] - old_surface(d[:, 0], d[:, 1])),
                                  abs(d[:, 2] - old_surface(d[:, 0], d[:, 1]) + SLAB)), 0, atol=2e-5),
           'deck not on the as-built grade')
    for pid, xb in (('approach_1', -17.660938), ('approach_2', 17.660938)):
        b = native(pid).bounds
        expect(abs((b[0, 0] if xb < 0 else b[1, 0]) - xb) < 1e-5, f'{pid} square outer end')
    t = native('TFC_1_-1').vertices
    h = t[:, 2] - old_surface(t[:, 0], t[:, 1])
    expect(abs(h.max() - 33 * IN) < 1e-4 and abs(h[h > .01].min() - (33 * IN - .55)) < 1e-4, 'TFC height taper')
    expect(np.allclose(native('FC_rail_1').bounds[:, 0], [-8.882062, -3.716338], atol=1e-5), 'north FC position')
    f = native('FC_rail_-1').vertices
    expect(np.isclose(f[:, 2] - old_surface(f[:, 0], f[:, 1]), 10 * IN, atol=1e-4).any(), 'FC 10 in toe')
    for pid, top in (('integral_bent_1', 2.397298), ('integral_bent_2', 2.372058)):
        m = native(pid)
        expect(len(m.vertices) == 8 and abs(m.bounds[1, 2] - top) < 1e-5, f'{pid} flat top')
    expect(np.allclose(native('wing_2_1').bounds, [[-1.9812, 6.5532, .619512], [1.6764, 6.858, 2.877596]],
                       atol=1e-5), 'Wing D rectangle')

    # --- New geometry. ---
    deck_plan, approach_1, approach_2 = plans()
    solids, notes = {}, {}
    solids['deck'] = drape(deck_plan, surface, lambda x, y: surface(x, y) - SLAB)
    solids['approach_1'] = drape(approach_1, surface, lambda x, y: surface(x, y) - APPROACH_T)
    solids['approach_2'] = drape(approach_2, surface, lambda x, y: surface(x, y) - APPROACH_T)
    for i, u in ((1, -BENT_U), (2, BENT_U)):
        bottom = float(z_el(870.97 if i == 1 else 870.83))
        expect(abs(native(f'integral_bent_{i}').bounds[0, 2] - bottom) < 1e-5, f'bent {i} bottom')
        solids[f'integral_bent_{i}'] = drape(parallelogram(u - BENT_HALF, u + BENT_HALF, -COPING, COPING),
                                             lambda x, y: surface(x, y) - SLAB, lambda x, y, b=bottom: b + 0 * x)
        solids[f'joint_{i}'] = drape(parallelogram(u / BENT_U * HALF_DECK - .012, u / BENT_U * HALF_DECK + .012,
                                                   -FACE, FACE), surface, lambda x, y: surface(x, y) - JOINT_T)
    for side in (-1, 1):
        solids[f'FC_rail_{side}'] = fc(side)
        for end in (-1, 1):
            solids[f'TFC_{side}_{end}'] = tfc(side, end)
            solids[f'guardrail_{side}_{end}'] = guardrail(side, end)
    plan_d, x_west, x_tip = wing_d_plan()
    top_d = lambda x, y: z_el(WING_D['top_bent_el'] + (WING_D['top_tip_el'] - WING_D['top_bent_el'])  # noqa: E731
                              * (x - x_west) / (x_tip - x_west))
    solids['wing_2_1'] = drape(plan_d, top_d, lambda x, y: z_el(WING_D['bottom_el']) + 0 * x, step=4.0)
    # Wings A-C keep their plan and level top; the top moves with the datum at the bent C/L on the coping.
    wing_shift = {}
    for pid, u, side in (('wing_1_1', -BENT_U, 1), ('wing_1_-1', -BENT_U, -1), ('wing_2_-1', BENT_U, -1)):
        m = native(pid)
        x_ref = skew_x(u, side * COPING)
        old_top = float(old_surface(x_ref, COPING))
        top = m.vertices[:, 2] > m.bounds[0, 2] + 1
        expect(top.sum() == 4 and np.allclose(m.vertices[top, 2], old_top, atol=2e-5), f'{pid} top')
        v = m.vertices.copy()
        v[top, 2] = float(surface(x_ref, COPING))
        wing_shift[pid] = float(surface(x_ref, COPING)) - old_top
        solids[pid] = trimesh.Trimesh(v, m.faces, process=False)

    # --- Manifest text and dimensions. ---
    el = lambda z: round(DATUM_EL + (float(z) - 3) / FT, 2)  # noqa: E731
    deck_note = ('19.5 in structural depth plus 0.5 in integral wearing surface. Old 1941 bridge is excluded. '
                 'Review correction: top on the sheet 11 profile with the local datum Z = 3 m at El. 878.64 '
                 '(was 18 mm high) and the -0.622 % tangent east of 507+95; slab ends square to the roadway in '
                 'the rail zones as drawn on sheet 18 (north coping 31\'-5 3/8", south 31\'-10 5/8").')
    notes['deck'] = (deck_note, dict(north_coping_length_m=round(NE_SLAB_END - NW_FC, 6),
                                     south_coping_length_m=round(CHAINS[-1][2] - SW_FC, 6),
                                     pg_el_ft_at_bent_centrelines=[878.64, 878.50]), [11, 12, 13, 14, 18])
    for i in (1, 2):
        notes[f'integral_bent_{i}'] = (
            'Integral slab-to-bent connection. No discrete bearings exist. Upper pavement ledge and local fillet are '
            'simplified. Review correction: top rebuilt on the crowned slab soffit (S - 20 in) along the whole bent; '
            'the 138 mm gap at the crown is closed (sheet 17 End Bent Detail).',
            dict(top='slab soffit, profile grade - 0.02 |y| - 20 in'), [14, 14 + i, 17])
        notes[f'joint_{i}'] = ('Schematic Type IA joint strip across the roadway between the roadway faces; under '
                               'the rails the slab joint is square to the roadway (sheet 18).', {}, [12, 17, 18])
    for i, end in ((1, 'west'), (2, 'east')):
        notes[f'approach_{i}'] = (
            f'Review correction: outer end skewed 45 degrees, parallel to the bents, 20\'-6" beyond the {end} slab end '
            '(sheet 12 stations, sheet 11 paving exception); slab between the roadway faces, with the Type TFC '
            'extension under each TFC ending 2" beyond it (sheet 18). Terminal asphalt joints are not modelled.',
            dict(length_along_roadway_m=round(20.5 * FT, 6), core_width_m=round(2 * FACE, 6),
                 tfc_extension_beyond_tfc_m=EXTENSION), [11, 12, 17, 18])
    for side, name in ((1, 'North'), (-1, 'South')):
        c = CHAINS[side]
        notes[f'FC_rail_{side}'] = (
            f'{name} rail, square ends at X = {c[1]:.4f} and {c[2]:.4f} m (sheet 18 railing plan; sheet 11 railing '
            'limits). Section per the sheet 18 typical section: 3 in vertical toe, knee 11 in from the back at '
            '10 in, 9 in top. Top-corner fillets simplified.',
            dict(length_m=round(c[2] - c[1], 6), section_q_h_in=FC_SECTION, x_start_m=round(c[1], 6),
                 x_end_m=round(c[2], 6)), [11, 18])
        for end in (-1, 1):
            a, b = (c[0], c[1]) if end < 0 else (c[2], c[3])
            notes[f'TFC_{side}_{end}'] = (
                f'Square ends at X = {a:.4f} and {b:.4f} m; top level at 2\'-9" over the whole transition (sheet 18 '
                'north and south railing elevations). Face from the FC section to a 9 in vertical end: base 1\'-4" '
                'to 9" over 11\'-5", knee 10" to 3" over 7\'-2" (scaled from sheet 18). Guardrail end plate and '
                'bolts are not modelled.',
                dict(length_m=round(TFC_L, 6), height_m=round(33 * IN, 6), base_width_at_fc_m=round(16 * IN, 6),
                     end_width_m=round(9 * IN, 6), x_start_m=round(min(a, b), 6), x_end_m=round(max(a, b), 6)),
                [11, 18])
            notes[f'guardrail_{side}_{end}'] = (
                'North-east TGB alignment and curved terminal are not fully reconstructed. Flat strip stands in for W '
                'profile. Representative 2 m run moved to start at the slab end beyond the corrected TFC end.', {},
                [11, 12, 18])
    notes['wing_2_1'] = (
        'Review correction: Wing D per sheet 16 - a 12 ft, 1 ft wall 2\'-9" outside the coping, joined to the bent '
        'end by a 4\'-1 1/8" by 3\'-8" block with a 90 degree corner; top El. 878.12 at the bent end (Section D-D) to '
        '878.06 at the tip (Wing D elevation), bottom El. 870.83. Rear batter and joints simplified.',
        dict(length_m=round(WING_D['length'], 6), top_thickness_m=FT, block_length_m=round(WING_D['block'], 6),
             outer_face_y_m=round(COPING + WING_D['offset'] + WING_D['wall'], 6), top_el_at_bent_end_ft=WING_D['top_bent_el'],
             top_el_at_tip_ft=WING_D['top_tip_el'], bottom_el_ft=WING_D['bottom_el']), [12, 16, 18])
    for pid in ('wing_1_1', 'wing_1_-1', 'wing_2_-1'):
        notes[pid] = (f'Wing A-D top elevations, 1:4 rear batter and local joints are approximate. Level top moved '
                      f'{wing_shift[pid] * 1000:+.1f} mm with the corrected vertical datum (El. '
                      f'{el(solids[pid].bounds[1, 2])}).', {}, None)

    changes = []
    for pid, solid in solids.items():
        if not solid.is_watertight or solid.volume <= 0:
            raise ValueError(f'{pid}: invalid corrected solid')
        prim = meshes[pid]['primitives'][0]
        color = read(prim['attributes']['COLOR_0'])[0]
        v = np.asarray(solid.vertices, np.float64)
        glb = np.c_[v[:, 0], v[:, 2], -v[:, 1]].astype('<f4')
        prim['attributes'] = {'POSITION': append(glb, 'VEC3', 5126),
                              'COLOR_0': append(np.tile(color, (len(v), 1)).astype('u1'), 'VEC4', 5121)}
        gltf['accessors'][prim['attributes']['COLOR_0']]['normalized'] = True
        prim['indices'] = append(np.asarray(solid.faces).reshape(-1, 1).astype('<u4'), 'SCALAR', 5125)
        p = parts[pid]
        note, dims, pages = notes[pid]
        p['bounds_m'] = np.round(solid.bounds, 6).tolist()
        p['volume_m3'] = round(float(solid.volume), 9)
        p['note'] = note
        p['dimensions'].update(dims)
        if pages:
            p['pdf_pages'] = pages
            for ref in p.get('source_refs', []):
                if ref.get('source_id') == '9683606':
                    ref['pdf_pages'] = pages
        meshes[pid]['extras'].update(p)
        changes.append(pid)
    parts['approach_1']['basis'] = parts['approach_2']['basis'] = (
        'Source 20 ft 6 in length along the roadway; skewed outer end and TFC extensions per sheets 12 and 18')
    for side in (-1, 1):
        for end in (-1, 1):
            parts[f'TFC_{side}_{end}']['basis'] = 'Source 15 ft 8 in transition, 2 ft 9 in level top, sheet 18 plan taper'
    parts['wing_2_1']['basis'] = 'Sheet 16 Wing D plan, Section D-D and Wing D elevation'
    for pid in ('approach_1', 'approach_2', 'wing_2_1') + tuple(f'TFC_{s}_{e}' for s in (-1, 1) for e in (-1, 1)):
        meshes[pid]['extras'].update(parts[pid])

    gltf['buffers'][0]['byteLength'] = len(binary)
    while len(binary) % 4:
        binary.append(0)
    encoded = json.dumps(gltf, ensure_ascii=True, separators=(',', ':')).encode()
    encoded += b' ' * ((-len(encoded)) % 4)
    out = (struct.pack('<III', 0x46546c67, 2, 28 + len(encoded) + len(binary)) +
           struct.pack('<II', len(encoded), 0x4e4f534a) + encoded + struct.pack('<II', len(binary), 0x004e4942) + binary)
    BACKUP.mkdir(exist_ok=True)
    (BACKUP / f'{BID}_before_review_correction.glb').write_bytes(original)
    (BACKUP / f'{BID}_manifest_before_review_correction.json').write_bytes(mp.read_bytes())
    path.write_bytes(out)

    manifest['assumptions'] = [
        a if not a.startswith('Vertical curve uses') else
        'Vertical curve uses the sheet 11 170 ft curve, P.V.I. 507+10 El. 879.00, +0.730 %/-0.622 %, with the '
        '-0.622 % tangent east of 507+95; local datum Z = 3 m + 0.3048 (El. ft - 878.64) for every part.'
        for a in manifest['assumptions']]
    for c in manifest.get('detail_coverage', []):
        if c['feature'] == 'Unresolved geometry':
            c['detail'] = c['detail'].replace('local slab notch, ', '')
    manifest['vertical_datum'] = 'Z (m) = 3 + 0.3048 (El. ft - 878.64); X = 0 at Sta. 507+75 "PR-PR"'
    manifest['review_correction'] = TAG
    manifest['revision'] = REVISION
    manifest['review_correction_record'] = dict(
        source_pdf_pages=[11, 12, 16, 17, 18], printed_sheets=[11, 12, 16, 17, 18],
        findings={'F1': 'confirmed - approach slabs', 'F2': 'confirmed - TFC level 2 ft 9 in top',
                  'F3': 'confirmed - bent tops on the crowned soffit', 'F4': 'confirmed - Wing D outline and top',
                  'F5': 'confirmed - railing chains and square ends', 'F6': 'confirmed - FC section',
                  'F7': 'confirmed - single vertical datum and east tangent'},
        vertical_datum=manifest['vertical_datum'], datum_shift_m=round(float(grade(0) - old_grade(0)), 6),
        railing_chains_x_m={'north': [round(x, 6) for x in CHAINS[1]], 'south': [round(x, 6) for x in CHAINS[-1]]},
        approach_outer_end_u_m=round(U_APPROACH, 6), wing_d_plan_xy_m=[[round(a, 6), round(b, 6)] for a, b in plan_d],
        changed_parts=changes, before_glb_sha256=before, after_glb_sha256=hashlib.sha256(out).hexdigest())
    deviations = [d for d in manifest.get('known_deviations', [])
                  if d.get('id') not in ('wings-a-b-c-plan', 'bent-pavement-ledge')]
    deviations += [
        dict(id='wings-a-b-c-plan', parts='wing_1_1, wing_1_-1, wing_2_-1', source='sheets 15, 16 and 18',
             deviation='Wings A, B and C keep the as-built level-topped 12 ft walls measured from the bent centre line '
                       'at the coping; on sheet 18 the walls are 1 in outside the coping and end 0.15-0.28 m from '
                       'the modelled tips, with sloping tops.',
             reason='Not part of the external review; left for a separate drawing check.'),
        dict(id='bent-pavement-ledge', parts='integral_bent_1, integral_bent_2', source='sheet 17 (End Bent Detail)',
             deviation='The 9 in pavement ledge under each approach slab is modelled at slab-soffit level, about '
                       '0.2 m below the approach slab.',
             reason='Ledge and fillet details are a stated simplification of the exterior model.')]
    manifest['known_deviations'] = deviations
    # Keep the file's own conventions (CRLF, no final newline) so that only the changed values differ.
    text = json.dumps(manifest, ensure_ascii=False, indent=2)
    mp.write_bytes(text.replace('\n', newline).encode('utf-8') + (newline.encode() if final_newline else b''))
    print(json.dumps({k: v for k, v in manifest['review_correction_record'].items()
                      if k not in ('wing_d_plan_xy_m', 'findings')}))


if __name__ == '__main__':
    correct()

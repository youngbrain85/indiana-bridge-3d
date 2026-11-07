"""One-time, drawing-confirmed corrections from the external model review of US 224 over Eight Mile Creek, preserving
unrelated GLB buffers.

    python scripts/correct_us224_eight_mile_review.py

Primary set: INDOT B-44532 / Des 2200957 (drawings.pdf, document 9683628); the printed sheet number equals the PDF
page number. Supplementary: 1985 plans B-16317 (sources/existing_plans_9548292.pdf), cited as "1985 sheet N"
(its PDF page N). Native axes: X east (station), Y south, Z up; Z = 0 is El. 817.00; u = X - Y tan 30 deg.

F5, sheet 9 (existing and proposed typical sections): 1 ft 4 in barrier + 44 ft 0 in clear roadway + 1 ft 4 in barrier
= 46 ft 8 in out-to-out coping; the back face of each barrier is flush with the coping edge. The generator inset both
barrier lines 50 mm (back 7.062 m, toe 6.6556 m, clear roadway 13.311 m). The two retained rails and the three TFC
transitions are re-swept with the back face at +-7.112 m and the toe at +-6.7056 m (22 ft from Line A) on the same
stations and on the same seating surfaces (coping top 1 1/2 in below the finished surface; finished surface).

F4 (height only), sheet 12 Railing Elevations and Sections C-C to F-F: the TFC is 2 ft 7 1/2 in high over the 7 ft 2 in
and 11 in nearest the bridge (C-C, D-D), rises to 2 ft 9 in over the next 3 ft 4 in (E-E, "varies 2'-7 1/2" to
2'-9"") and stays 2 ft 9 in over the last 4 ft 3 in (F-F); the elevation's top line has its kinks at 8 ft 1 in and
11 ft 5 in from the bridge end. The model tapered the top down to 0.700 m at the far end. The three transitions get
that height profile; the 7 in toe break of Section C-C is kept along the length (cross-section shape is the
manifest's declared nominal envelope).

F6, sheets 13 (east) and 14 (west), approach slab plans: 44 ft 4 in wide, but not centred: the west slab is 22 ft 0 in
north / 22 ft 4 in south of Line A, the east slab 22 ft 4 in north / 22 ft 0 in south; each is 20 ft 6 in long on its
22 ft 0 in edge. Under the northeast RCBA extension the east slab edge stays at 22 ft 0 in (4 in step on sheet 13), so
its north edge measures 45 ft 10 7/8 in from the skew corner (west south edge 46 ft 1 1/8 in), which both plans show.
The model centred both slabs at 22 ft 2 in. The slabs are rebuilt with those edges (skew end line unchanged, far end
20 ft 6 in from the 22 ft 0 in corner); the three RCBA extensions keep their stations and outer edge and get their
inner edge on the 22 ft 0 in slab edge.

F3 (approach slabs), sheet 15 Typical Section Through Approach and sheet 11 Section C-C: the 1 ft RCBA top is flush
with the bridge deck overlay surface at the joint; sheet 3 carries the 1.56 % crown "at bridge". The generator swept
the slabs with a flat top at the edge elevation, 105 mm below the crowned bridge floor at Line A. The rebuilt slabs
continue the bridge-floor surface (-0.20 % grade, 3/16 in/ft = 1.5625 % each side of Line A), 1 ft thick.

F2 and F1 for Wings B and C, 1985 sheets 5-7: the obtuse-corner wings (B, southwest, Abutment 1 = wing_0_1; C,
northeast, Abutment 2 = wing_1_-1) are straight walls at 60 deg to the abutment, i.e. on the bisector of the 120 deg
corner (the acute-corner wings A and D are at 30 deg, which the model has). Elevation C-C: 11 ft 7 3/8 in long, top
level for 1 ft 1 3/8 in at El. 831.54 (Abut. 1) / 831.50 (Abut. 2), then falling over 10 ft 6 in to El. 826.58 /
826.50 at the tip. The model had them at 90.7 deg to the abutment, 4.70 m long, top about El. 831.1. Both are rebuilt
from the model's own root point on the abutment end with that direction, length and top profile; the 0.40 m nominal
thickness and the bottom at Z = 0.05 m are kept.

Not changed, recorded in known_deviations: F1 for Wings A and D (kinked 23 ft 10 1/2 in outline of 1985 Elevation F-F
and the 2026 partial removal on sheet 10 need a rebuild of the wing outline); the new 5 ft 9 5/8 in FC railings and
the NW/SE TFC and extension stations (sheet 12; F4 apart from the height); and the floor end over the reconstructed
mudwall (sheets 10-11; the review's F3 mudwall item: the mudwall top is concealed inside the modelled deck end, so
raising it would only make it coincide with the overlay surface).

The script first rebuilds every affected part with the generator's formulas (scripts/build_remaining_concrete.py,
eight()) and refuses to run unless they reproduce the current GLB vertices. Requires numpy, trimesh and manifold3d.
"""
import hashlib
import json
import struct
from pathlib import Path

import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[1]
BID = 'us224-eight-mile'
BASE = ROOT / 'data/bridges' / BID
BACKUP = ROOT / 'data/fem_research'
TAG = 'review-barrier-line-tfc-height-approach-crown-offsets-obtuse-wings'
REVISION = '1.1-drawing-review'
FT, IN = .3048, .0254

# Generator geometry (scripts/build_remaining_concrete.py, eight()).
LENGTH, WIDTH, SPAN = (45 + .5 / 12) * FT, (46 + 8 / 12) * FT, 41 * FT
K = np.tan(np.radians(30))                 # X = u + K * Y (30 deg left skew)
APPROACH_W, APPROACH_L = (44 + 4 / 12) * FT, 20.5 * FT
TFC_LEN = 15.667 * FT
CAP_Y = WIDTH / 2 + .15


def surface(x, y):
    """Finished bridge-floor surface: proposed grade (old grade + 1 1/2 in), -0.20 %, 3/16 in/ft crown at Line A."""
    return (831.91 - 817) * FT + 1.5 * IN - .002 * np.asarray(x) - .015625 * np.abs(y)


def sx(u, y):
    return u + K * y


def z_el(el_ft):
    return (el_ft - 817) * FT


# Drawing values.
BARRIER_BACK = WIDTH / 2                   # 23 ft 4 in, sheet 9
TOE = 22 * FT                              # 44 ft clear roadway, sheet 9
TFC_LOW, TFC_HIGH = 31.5 * IN, 33 * IN     # sheet 12, Sections C-C/D-D and F-F
TFC_RISE = (97 * IN, 137 * IN)             # 8 ft 1 in and 11 ft 5 in from the bridge end, sheet 12 elevations
EDGE_22_0, EDGE_22_4 = 22 * FT, (22 + 4 / 12) * FT     # sheets 13-14
WING_LEN, WING_LEVEL = (11 + 7.375 / 12) * FT, (1 + 1.375 / 12) * FT   # 1985 sheet 7, Elevation C-C
WING_TOP = {'wing_0_1': (831.54, 826.58), 'wing_1_-1': (831.50, 826.50)}  # 1985 sheet 7, End Elevation B-B


def triangulate(poly):
    """Ear clipping of a small simple polygon; collinear vertices are kept and never become ear tips."""
    p = np.asarray(poly, float)
    idx = list(range(len(p)))
    clockwise = sum(p[i, 0] * p[(i + 1) % len(p), 1] - p[(i + 1) % len(p), 0] * p[i, 1] for i in idx) < 0
    if clockwise:
        idx.reverse()

    def cross(a, b, c):
        return (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])

    def inside(q, a, b, c):
        return min(cross(a, b, q), cross(b, c, q), cross(c, a, q)) >= -1e-12

    tris = []
    while len(idx) > 3:
        for k in range(len(idx)):
            i0, i1, i2 = idx[k - 1], idx[k], idx[(k + 1) % len(idx)]
            if cross(p[i0], p[i1], p[i2]) <= 1e-12:
                continue
            if any(inside(p[j], p[i0], p[i1], p[i2]) for j in idx if j not in (i0, i1, i2)):
                continue
            tris.append((i0, i1, i2))
            idx.pop(k)
            break
        else:
            raise ValueError('polygon could not be triangulated')
    tris.append(tuple(idx))
    tris = np.array(tris)
    return tris[:, ::-1] if clockwise else tris     # same turning sense as the polygon's own vertex order


def sweep(profile, xs, fn):
    """bridge_geometry.sweep with a local triangulation (same vertices, same side faces)."""
    n = len(profile)
    v = [fn(float(x), float(a), float(b)) for x in xs for a, b in profile]
    f = []
    for k in range(len(xs) - 1):
        for j in range(n):
            a, b = k * n + j, k * n + (j + 1) % n
            f.extend([(a, b, b + n), (a, b + n, a + n)])
    cap = triangulate(profile)
    f.extend(tuple(q[::-1]) for q in cap)
    f.extend(tuple(q + (len(xs) - 1) * n) for q in cap)
    m = trimesh.Trimesh(np.array(v, float), np.array(f), process=True)
    if m.volume < 0:                                 # consistent winding by construction; make it outward
        m.invert()
    if not m.is_watertight or not m.is_winding_consistent or m.volume <= 0:
        raise ValueError('invalid swept solid')
    return m


def rail_mesh(a, b, side, height, top, base=16 * IN, offset=0., edge=None, height_at=None, breaks=(),
              scale_toe=True):
    """Generator rail(): five-point barrier section swept along u. The generator scales the whole section with
    height_at(u) / height; with scale_toe=False only the top follows height_at and the 7 in toe break is kept."""
    edge = side * (WIDTH / 2 - .05) if edge is None else edge
    xs = np.linspace(a, b, max(3, int((b - a) / .5)))
    xs = np.unique(np.r_[xs, [u for u in breaks if a < u < b]])
    profile = [(0, 0), (base, 0), (base, .1778), (top, 1.), (0, 1.)]

    def xyz(u, v, z):
        y = edge - side * v
        h = height if height_at is None else height_at(u)
        rise = h if z == 1. else (z * h / height if scale_toe else z)
        return sx(u, y), y, surface(sx(u, y), y) + offset + rise
    return sweep(profile, xs, xyz)


def slab_mesh(u0, u1, y0, y1, thick):
    """Generator Model.slab() for a strip on one side of Line A."""
    profile = [(y0, -thick), (y1, -thick), (y1, 0), (y0, 0)]
    return sweep(profile, np.linspace(u0, u1, max(2, int((u1 - u0) / .6) + 1)),
                 lambda u, y, z: (sx(u, y), y, surface(sx(u, y), y) + z))


def approach_mesh(end, y_north, y_south, near, far, slices, crown):
    """Generator approach(): skew near end to square far end, 1 ft thick, top on the floor surface."""
    ys = [y_north, 0., y_south] if crown else [y_north, y_south]
    profile = [(y, 0.) for y in ys] + [(y, 1.) for y in reversed(ys)]
    return sweep(profile, np.linspace(0, 1, slices), lambda t, y, h: (
        (1 - t) * sx(near, y) + t * far, y, surface((1 - t) * sx(near, y) + t * far, y) - FT + h * FT))


class Profile:
    """TFC top height along u: 2 ft 7 1/2 in, rising over 3 ft 4 in to 2 ft 9 in (sheet 12)."""

    def __init__(self, end):
        self.end = end
        self.breaks = [end * (LENGTH / 2 + t) for t in TFC_RISE]

    def __call__(self, u):
        t = abs(u - self.end * LENGTH / 2)
        return float(np.interp(t, TFC_RISE, [TFC_LOW, TFC_HIGH]))


def same_vertices(mesh, vertices, tol=2e-4):
    a, b = np.asarray(mesh.vertices), np.asarray(vertices)
    if len(a) != len(b):
        return False
    d = np.linalg.norm(a[:, None, :] - b[None, :, :], axis=2)
    return d.min(axis=1).max() < tol and d.min(axis=0).max() < tol


def correct():
    mp = BASE / 'model_manifest.json'
    raw_manifest = mp.read_bytes()
    manifest = json.loads(raw_manifest)
    if manifest.get('drawing_review_correction') == TAG:
        print('Already corrected.')
        return
    if 'revision' in manifest:
        raise ValueError('Manifest is not the original generator revision.')
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
        if kind in ('VEC3', 'SCALAR'):
            a.update(min=array.min(axis=0).tolist(), max=array.max(axis=0).tolist())
        gltf['accessors'].append(a)
        return len(gltf['accessors']) - 1

    def native(pid):
        # POSITION holds glTF Y-up coordinates (native X, native Z, -native Y); no node transform.
        prim = meshes[pid]['primitives'][0]
        v = read(prim['attributes']['POSITION']).astype(np.float64)
        return np.column_stack([v[:, 0], -v[:, 2], v[:, 1]])

    def check(pid, expected):
        if not same_vertices(expected, native(pid)):
            raise ValueError(f'{pid}: the GLB is not in the expected original state')

    changes = []

    def replace(pid, mesh, dims, note):
        if not mesh.is_watertight or mesh.volume <= 0:
            raise ValueError(f'{pid}: invalid corrected solid')
        prim = meshes[pid]['primitives'][0]
        color = read(prim['attributes']['COLOR_0'])[0]
        v = np.asarray(mesh.vertices)
        prim['attributes'] = {
            'POSITION': append(np.column_stack([v[:, 0], v[:, 2], -v[:, 1]]).astype('<f4'), 'VEC3', 5126),
            'COLOR_0': append(np.tile(color, (len(v), 1)).astype('u1'), 'VEC4', 5121)}
        gltf['accessors'][prim['attributes']['COLOR_0']]['normalized'] = True
        prim['indices'] = append(np.asarray(mesh.faces).reshape(-1, 1).astype('<u4'), 'SCALAR', 5125)
        p = parts[pid]
        p['bounds_m'] = np.round(mesh.bounds, 6).tolist()
        p['volume_m3'] = round(float(mesh.volume), 9)
        p['dimensions'].update(dims)
        p['note'] = (p.get('note', '') + ' ' + note).strip()
        meshes[pid]['extras'].update(p)
        changes.append(pid)

    # F5: retained barriers, back face flush with the coping edge.
    for side in (-1, 1):
        pid = f'retained_rail_{side}'
        kw = dict(height=33 * IN, top=9 * IN, offset=-1.5 * IN)
        check(pid, rail_mesh(-LENGTH / 2, LENGTH / 2, side, **kw))
        replace(pid, rail_mesh(-LENGTH / 2, LENGTH / 2, side, edge=side * BARRIER_BACK, **kw),
                dict(back_face_offset_m=round(BARRIER_BACK, 6), traffic_toe_offset_m=round(TOE, 6)),
                'Barrier line moved 50 mm outward: back face flush with the 46 ft 8 in coping, toe 22 ft 0 in from '
                'Line A (44 ft 0 in clear roadway), sheet 9.')

    # F5 + F4 height: TFC transitions on the corrected barrier line with the sheet 12 height profile.
    for end, side in ((-1, -1), (1, -1), (1, 1)):
        pid = f'TFC_transition_{end}_{side}'
        a, b = sorted([end * LENGTH / 2, end * (LENGTH / 2 + TFC_LEN)])
        h0, h1 = (.70, TFC_LOW) if end < 0 else (TFC_LOW, .70)
        check(pid, rail_mesh(a, b, side, TFC_LOW, .2286, base=.4064,
                             height_at=lambda u: h0 + (h1 - h0) * (u - a) / (b - a)))
        profile = Profile(end)
        replace(pid, rail_mesh(a, b, side, TFC_LOW, .2286, base=.4064, edge=side * BARRIER_BACK, height_at=profile,
                               breaks=profile.breaks, scale_toe=False),
                dict(far_end_height_m=round(TFC_HIGH, 6), height_profile='2 ft 7 1/2 in for 8 ft 1 in from the bridge '
                     'end, rising to 2 ft 9 in at 11 ft 5 in, 2 ft 9 in to the 15 ft 8 in end',
                     back_face_offset_m=round(BARRIER_BACK, 6), traffic_toe_offset_m=round(TOE, 6)),
                'Height corrected to sheet 12 (Sections C-C to F-F: 2 ft 7 1/2 in rising to 2 ft 9 in, was tapered '
                'down to 0.70 m) and barrier line moved 50 mm outward with the bridge rail (sheet 9). Stations are '
                'unchanged; see known_deviations.')

    # F6: RCBA extensions keep stations and outer edge; inner edge on the 22 ft 0 in slab edge.
    for end, side in ((-1, -1), (1, -1), (1, 1)):
        pid = f'extension_{end}_{side}'
        a, b = sorted([end * LENGTH / 2, end * (LENGTH / 2 + TFC_LEN)])
        y0, y1 = sorted([side * APPROACH_W / 2, side * WIDTH / 2])
        check(pid, slab_mesh(a, b, y0, y1, FT))
        y0, y1 = sorted([side * EDGE_22_0, side * WIDTH / 2])
        replace(pid, slab_mesh(a, b, y0, y1, FT), dict(inner_edge_offset_m=round(EDGE_22_0, 6)),
                'Inner edge on the 22 ft 0 in approach-slab edge, sheets 13-14 (was 22 ft 2 in).')

    # F6 + F3: approach slabs with the plan offsets and the bridge-floor crown.
    for end in (-1, 1):
        pid = f'approach_{end}'
        near = end * (LENGTH / 2 + .025)
        check(pid, approach_mesh(end, -APPROACH_W / 2, APPROACH_W / 2, near,
                                 end * (LENGTH / 2 + .025 + K * APPROACH_W / 2 + APPROACH_L), 24, crown=False))
        north, south = (-EDGE_22_0, EDGE_22_4) if end < 0 else (-EDGE_22_4, EDGE_22_0)
        short_edge = south if end > 0 else north           # the 22 ft 0 in edge carries the 20 ft 6 in length
        far = sx(near, short_edge) + end * APPROACH_L
        if end < 0:
            slab = approach_mesh(end, north, south, near, far, 2, crown=True)
        else:
            # Sheet 13: under the NE extension the slab edge stays at 22 ft 0 in; 22 ft 4 in beyond it.
            main = approach_mesh(end, -EDGE_22_0, south, near, far, 2, crown=True)
            notch_u = LENGTH / 2 + TFC_LEN
            strip = sweep([(-EDGE_22_4, 0.), (-EDGE_22_0, 0.), (-EDGE_22_0, 1.), (-EDGE_22_4, 1.)], [0., 1.],
                          lambda t, y, h: ((1 - t) * sx(notch_u, y) + t * far, y,
                                           surface((1 - t) * sx(notch_u, y) + t * far, y) - FT + h * FT))
            slab = trimesh.boolean.union([main, strip], engine='manifold')
            if abs(slab.volume - main.volume - strip.volume) > 1e-4:   # manifold works in float32
                raise ValueError(f'{pid}: union lost volume')
        replace(pid, slab, dict(north_edge_offset_m=round(-north, 6), south_edge_offset_m=round(south, 6),
                                crossfall=.015625, grade=-.002,
                                **({'edge_under_ne_extension_offset_m': round(EDGE_22_0, 6)} if end > 0 else {})),
                ('West slab 22 ft 0 in north / 22 ft 4 in south of Line A (sheet 14)' if end < 0 else
                 'East slab 22 ft 4 in north / 22 ft 0 in south of Line A, 22 ft 0 in under the NE extension (sheet 13)')
                + '; top crowned 1.5625 % each side of Line A and flush with the bridge floor at the joint '
                  '(sheets 3, 11, 15), was flat and 105 mm low at Line A.')

    # F2 + F1: obtuse-corner wings B (wing_0_1) and C (wing_1_-1).
    for bi, side in ((0, 1), (1, -1)):
        pid = f'wing_{bi}_{side}'
        end = -1 if bi == 0 else 1
        u = end * SPAN / 2
        root = np.array([sx(u, side * CAP_Y), side * CAP_Y])
        v = np.array([end * 4.1, side * 2.3])
        normal = np.array([-v[1], v[0]]) / np.linalg.norm(v) * .20
        xy = [root - normal, root + v - normal, root + v + normal, root + normal]
        check(pid, sweep([(float(px), float(py)) for px, py in xy], [0, 1],
                         lambda h, px, py: (px, py, .05 * (1 - h) + (surface(px, py) - .15) * h)))
        along = np.array([K * side, side]) / np.hypot(K, 1) + np.array([end, 0.])   # abutment line + approach
        along /= np.linalg.norm(along)                       # bisector of the 120 deg corner: 60 deg to each
        across = np.array([-along[1], along[0]])
        el_root, el_tip = WING_TOP[pid]
        outline = [(0., .05), (WING_LEN, .05), (WING_LEN, z_el(el_tip)), (WING_LEVEL, z_el(el_root)), (0., z_el(el_root))]
        wing = sweep(outline, [-.20, .20], lambda o, s, z: (*(root + s * along + o * across), z))
        letter = 'B (southwest)' if bi == 0 else 'C (northeast)'
        replace(pid, wing, dict(length_m=round(WING_LEN, 6), angle_to_abutment_deg=60,
                                top_el_at_abutment_ft=el_root, top_el_at_tip_ft=el_tip,
                                level_top_length_m=round(WING_LEVEL, 6), nominal_thickness_m=.4),
                f'Wing {letter}: rebuilt to 1985 sheets 5-7 (B-16317): 60 deg to the abutment, 11 ft 7 3/8 in long, '
                f'top El. {el_root} for 1 ft 1 3/8 in, falling to El. {el_tip} at the tip (was 90.7 deg, 4.70 m, '
                f'about El. 831.1). Root point, 0.40 m nominal thickness and bottom unchanged.')

    deviations = [d for d in manifest.get('known_deviations', [])
                  if d.get('id') not in ('acute-corner-wings', 'transition-railing-stations', 'floor-end-over-mudwall')]
    deviations += [
        dict(id='acute-corner-wings', parts='wing_0_-1, wing_1_1',
             source='1985 sheets 5-7 (B-16317, existing_plans_9548292.pdf); primary sheets 10, 12',
             deviation='Wings A (northwest) and D (southeast) remain straight 4.70 m walls at 30 deg to the abutment '
                       'with the top about El. 831.1-831.3 at the tip. Elevation F-F gives 23 ft 10 1/2 in: level '
                       'El. 831.65 (Abut. 1) / 831.47 (Abut. 2) for 4 ft 10 3/4 in, then falling over 18 ft 11 3/4 in '
                       'to El. 827.38 / 827.30, with a root leg along the railing; sheet 10 removes part of the wing '
                       'top under the new RCBA extension.',
             reason='Needs a rebuild of the kinked historical outline reconciled with the 2026 removals, beyond a '
                    'correction.'),
        dict(id='transition-railing-stations', parts='TFC_transition_-1_-1, TFC_transition_1_1, extension_-1_-1, '
                                                     'extension_1_1, retained_rail_-1',
             source='sheets 10, 12, 13, 14',
             deviation='At the NW and SE corners sheet 12 has a new 5 ft 9 5/8 in Type FC railing on the existing '
                       'wingwall from the PCF joint, a 1/4 in open joint, then the 15 ft 8 in TFC, so those TFCs and '
                       'their RCBA extensions (the outer about 15 ft 10 in of the 20 ft 6 in slab edge, sheets 13-14) '
                       'lie about 1.4 m farther from the bridge than modelled, and the 5 ft 9 5/8 in railings are '
                       'missing. At the NE corner the new 7 ft 10 5/8 in railing replaces the last 6 ft 9 in of the '
                       'existing railing on the deck (sheet 10) and the modelled TFC start is within a few cm.',
             reason='Requires new railing components and shortened retained rails, beyond a correction.'),
        dict(id='floor-end-over-mudwall', parts='deck, overlay, retained_coping_-1, retained_coping_1, mudwall_1, '
                                                'mudwall_2, PCF_joint_-1, PCF_joint_1',
             source='sheet 10 Section E-E, sheet 11 Section C-C, sheet 15',
             deviation='The deck, overlay and copings run to the 45 ft 0 1/2 in floor end over the 1 ft reconstructed '
                       'mudwall, and the PCF joint is drawn at the mudwall back face; the drawings put the joint at '
                       'the span face of the mudwall, whose top is flush with the overlay and the RCBA. The concealed '
                       'mudwall top is flat (111 mm below the crown at Line A).',
             reason='The visible floor surface is at the correct crowned elevation; correcting the arrangement means '
                    'shortening the deck, overlay and copings and moving the joints, beyond a correction.')]
    manifest['known_deviations'] = deviations

    gltf['buffers'][0]['byteLength'] = len(binary)
    while len(binary) % 4:
        binary.append(0)
    encoded = json.dumps(gltf, ensure_ascii=True, separators=(',', ':')).encode()
    encoded += b' ' * ((-len(encoded)) % 4)
    out = (struct.pack('<III', 0x46546c67, 2, 28 + len(encoded) + len(binary)) +
           struct.pack('<II', len(encoded), 0x4e4f534a) + encoded + struct.pack('<II', len(binary), 0x004e4942) + binary)
    BACKUP.mkdir(exist_ok=True)
    (BACKUP / f'{BID}_before_review_correction.glb').write_bytes(original)
    (BACKUP / f'{BID}_manifest_before_review_correction.json').write_bytes(raw_manifest)
    path.write_bytes(out)
    manifest['drawing_review_correction'] = TAG
    manifest['revision'] = REVISION
    manifest['drawing_review_correction_record'] = dict(
        source_pdf_pages=[3, 9, 11, 12, 13, 14, 15], printed_sheets=[3, 9, 11, 12, 13, 14, 15],
        supplementary_source=dict(document_id='9548292', local_file='sources/existing_plans_9548292.pdf',
                                  pdf_pages=[5, 6, 7]),
        changed_parts=changes,
        values={'barrier back face / toe from Line A (sheet 9)': '7.112 / 6.7056 m; was 7.062 / 6.6556 m',
                'clear roadway (sheet 9)': '13.4112 m (44 ft 0 in); was 13.3112 m',
                'TFC height (sheet 12)': '0.8001 m to 2.4638 m from the bridge end, 0.8382 m from 3.4798 m to the '
                                         'end; was 0.8001 m tapering to 0.700 m',
                'approach slab edges from Line A (sheets 13-14)': 'west 6.7056 N / 6.8072 S, east 6.8072 N / '
                                                                  '6.7056 S (6.7056 under the NE extension); was '
                                                                  '6.7564 both',
                'approach slab top (sheets 3, 11, 15)': 'crowned 1.5625 % at Line A, flush with the bridge floor; '
                                                        'was flat, 105 mm low at Line A',
                'RCBA extension inner edge (sheets 13-14)': '6.7056 m; was 6.7564 m',
                'Wings B / C (1985 sheets 5-7)': '60 deg to the abutment, 3.540 m, top El. 831.54 / 831.50 to '
                                                 '826.58 / 826.50; was 90.7 deg, 4.701 m, top about El. 831.1'},
        not_changed=['acute-corner-wings', 'transition-railing-stations', 'floor-end-over-mudwall'],
        before_glb_sha256=before, after_glb_sha256=hashlib.sha256(out).hexdigest())
    text = json.dumps(manifest, indent=2)
    if b'\r\n' in raw_manifest:
        text = text.replace('\n', '\r\n')
    if raw_manifest.endswith(b'\n'):
        text += '\r\n' if b'\r\n' in raw_manifest else '\n'
    mp.write_bytes(text.encode('utf-8'))
    print(json.dumps({k: v for k, v in manifest['drawing_review_correction_record'].items() if k != 'values'}))


if __name__ == '__main__':
    correct()

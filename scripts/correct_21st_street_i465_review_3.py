"""Third drawing review (runs after correct_21st_street_i465_review_2.py): settle the last known deviation and
rebuild the end-bent bearing stack (caps, pads, beam ends, end diaphragms), preserving unrelated GLB buffers.

    python scripts/correct_21st_street_i465_review_3.py [--dry-run]

Drawing evidence (contract IB-30026, drawings.pdf; printed sheets 41-62 are PDF pages 41-62):

1. Known deviation `bent2-diaphragm-edge-setback` (diaphragm_pier) -> DECIDE, flush faces kept, geometry unchanged.
   - Sheet 54 (PDF 54), BEAM END DETAIL AT BENT #2 (3/4 in = 1 ft): the "Edge of Diaphragm and Preformed Expansion
     Joint Material" line is drawn 3.0 in inside each "Face of Bent Cap" (PDF vectors) but carries no dimension;
     the detail is drawn at 78 deg although it labels the 72 deg beam angle.
   - Sheet 57 (PDF 57), SECTION V-V: each diaphragm face is one line with the 4 ft cap face (2'-0" + 2'-0" from CL
     Bent No. 2); the 1 in joint material runs the full 4'-0"; the 505a stirrups are drawn 2 in inside the faces.
   - Sheet 58 (PDF 58): bar 505a is a U bar 3'-8" wide and the cover note asks 2 in in all other parts:
     3'-8" + 2 x 2 in = 4'-0". Sheet 45: the cap is 4'-0".

2. End-bent caps (independent round-3 checks) -> RESOLVE.
   - Sheet 42 (PDF 42) ELEVATION: level top terraces El. 761.53 / 761.82 / 761.36 (Bent 1, south / centre / north)
     and 761.04 / 761.51 / 761.23 (Bent 3), vertical steps 9'-7 3/4" either side of CL Structure & CL Bent (the
     plan gives the same, 2'-5 1/8" + 6'-8 3/4" from CL Structure on the back face; the left-half step is drawn at
     the same distance in the elevation). The model had ridges interpolated between the beam centrelines.
   - Sheet 42 PLAN: the cap ends are parallel to CL Structure (Line M, native X), 25'-5 1/4" from it along CL Bent,
     i.e. Y = +/-7.373874 m (50'-10 1/2" along each face, 11 3/4" offset between the faces). The model had square
     ends. Bottoms El. 758.87 / 758.55 and the 3'-0" width are unchanged.
3. End-bent pads -> RESOLVE.
   - Sheet 54 END BENT BEARING PAD DIMENSIONS: T = 13/16 in (2 x 3/16 covers, 3/16 inner layer, 2 x 1/8 shims),
     11 x 19 in. The model had 1 3/16 in. Pads stay on the cap terraces; their tops drop 3/8 in.
   - Sheet 42 PLAN: CL bearing pads 1'-1 1/2" either side of CL Beam along the bent (pair spacing 2'-3"). The model
     had 2'-3" normal to the beam (2'-4 3/8" along the bent). Each pad moves 0.017647 m along the bent.
4. Beams and everything they carry -> lowered with the pads.
   - With 13/16 in pads on the sheet 42 seats the beams bear 3/8 in (9.525 mm) lower at Bents 1 and 3. Each span
     beam, its two end blocks, five steel cross frames (15 angles), two access doors with frame, hinges, grab and
     hasp, and the bottom of its two haunches get z += f(x): f = -9.525 mm x (x_k - x) / (x_k - x_bearing), from the
     end-bent bearing (CL Bent at CL Beam) to x_k, where the Bent 2 diaphragm face crosses the beam edge nearest the
     span, and 0 beyond, so the Bent 2 seats, pads and diaphragm_pier are untouched (the 0.3 m between x_k and the
     Bent 2 bearing changes the slope by 1 %, i.e. < 0.1 mm). Haunch tops stay at the deck underside; the deck and
     the approach slabs do not move.
5. End diaphragms diaphragm_west / diaphragm_east -> rebuilt around the new stack.
   - Sheet 58 sections C-C and D-D: 3'-0" wide, faces flush with the cap faces (1'-6" either side of CL Bearing &
     CL Bent). The model had 2'-10 1/4" (faces 0.022377 m inside the cap faces).
   - Sheet 42 (keyway construction joint) and sheet 58 C-C: the diaphragm sits on the cap top; under each beam only
     the pads and the 7/8 in preformed joint material (sheet 42 hatched limits; not modelled, as at Bent 2). The
     approach slab bears on the back of the diaphragm (pavement ledge, C-C). The model had a flat underside 80-220 mm
     inside the caps, encased all 12 pads and overlapped the approach slabs, haunches and end blocks.
   - Rebuild: the diaphragm's vertices on the beam voids move down with the beams, its face vertices move out to
     n = +/-1'-6" along X, and the new cap (extended past its ends so the diaphragm corners sit at terrace level),
     deck, approach slab and walks, joint, new beams, end blocks, haunches, pads and the open pad layer under each
     beam bottom are subtracted. Moved face vertices are snapped back onto the deck soffit and the beam surfaces.
     The result keeps a few separate wedges (0.3-0.4 L per bent) between haunch, beam and deck as extra shells.

Part ids and mesh names are unchanged; moved parts get new POSITION accessors (indices and colours reused), caps
and end diaphragms are re-meshed. Requires numpy, trimesh, manifold3d and shapely.
"""
import hashlib
import json
import re
import struct
import sys
from pathlib import Path

import manifold3d as mf
import numpy as np
import trimesh
from shapely.geometry import Polygon
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[1]
BID = '21st-street-i465'
BASE = ROOT / 'data/bridges' / BID
FT = 0.3048
IN = FT / 12
TAG = 'known-deviations-decided-end-bent-stack-rebuilt'
REVISION = '1.3-deviations'
PREVIOUS_TAG = 'bent2-diaphragm-4ft-normal-to-bent'        # correct_21st_street_i465_review_2.py
PREVIOUS_REVISION = '1.2-review-corrections-2'
DEVIATION = 'bent2-diaphragm-edge-setback'

SKEW = np.radians(18.0)
C, S = float(np.cos(SKEW)), float(np.sin(SKEW))
N = np.array([C, S, 0.0])                        # normal to the bents (native X along Line M, Y north)
T = np.array([-S, C, 0.0])                       # along the bents, north positive
HALF = 2.0 * FT                                  # sheet 57 V-V, sheet 45: 2'-0" either side of CL Bent 2
CAP_JOINT = 1.0 * IN                             # sheet 57 V-V: 1 in preformed expansion joint material
STIRRUP_505A = 3.0 * FT + 8.0 * IN               # sheet 58: 505a x 16'-4", 3'-8" wide
COVER = 2.0 * IN                                 # sheet 58 note: 2 in min. in all other parts
PLAN_SETBACK = 3.0 * IN                          # sheet 54 plan line (scaled, undimensioned)

SPAN = 116.0 * FT                                # CL Bent 1 / CL Bent 3 at X = -/+ 35.3568 m
STEP = (9 * 12 + 7.75) * IN                      # sheet 42: step 9'-7 3/4" either side of CL Structure & CL Bent
CAP_HALF_N = 1.5 * FT                            # sheet 42 / sheet 58 C-C, D-D: 3'-0" cap and diaphragm
CAP_HALF_T = (25 * 12 + 5.25) * IN               # sheet 42: 25'-5 1/4" either side of CL Structure
CAP_END_Y = CAP_HALF_T * C                       # ends parallel to Line M through 25'-5 1/4" on CL Bent: 7.373874 m
PAD_T_OLD = (1 + 3 / 16) * IN                    # as modelled
PAD_T = 13 / 16 * IN                             # sheet 54: end-bent pads T = 13/16 in
DROP = PAD_T_OLD - PAD_T                         # 3/8 in = 9.525 mm
PAD_OFFSET = 13.5 * IN                           # sheet 42: CL bearing pad 1'-1 1/2" from CL Beam along the bent
END_BENTS = {
    # terrace elevations (south of the step, centre, north of the step) and bottom, sheet 42 ELEVATION
    1: dict(cap='bent_1_cap', dia='diaphragm_west', x0=-SPAN, el=(761.53, 761.82, 761.36), bottom=758.87,
            span='A', end=1, side=-1, approach=['approach_west', 'approach_walk_west_1', 'approach_walk_west_-1'],
            joint='joint_west'),
    3: dict(cap='bent_3_cap', dia='diaphragm_east', x0=SPAN, el=(761.04, 761.51, 761.23), bottom=758.55,
            span='B', end=2, side=1, approach=['approach_east', 'approach_walk_east_1', 'approach_walk_east_-1'],
            joint='joint_east'),
}
TOL = 1e-5
CLASH = 1e-7                                     # m3
FIT = 1e-6                                       # m3, float32 residue of the manifold booleans


def z_of(el):
    return (el - 730.0) * FT                     # native Z datum El. 730 ft


def boolean(op, meshes):
    return getattr(trimesh.boolean, op)(meshes, engine='manifold')


def to_mf(m):
    return mf.Manifold(mf.Mesh(vert_properties=np.asarray(m.vertices, np.float32),
                               tri_verts=np.asarray(m.faces, np.uint32)))


def from_mf(man):
    mm = man.to_mesh()
    return trimesh.Trimesh(np.asarray(mm.vert_properties)[:, :3].astype(np.float64), np.asarray(mm.tri_verts),
                           process=False)


def solid_parts(mesh, residue=1e-6):
    """Boolean result without its zero-volume slivers and float32 void shells. Small separate solids that touch the
    neighbouring parts (e.g. concrete wedges between a haunch, the beam and the deck) are kept as extra shells."""
    comps = sorted(to_mf(mesh).decompose(), key=lambda c: -c.volume())
    voids = [c.volume() for c in comps if c.volume() < 0]
    if voids and -min(voids) > residue:
        raise ValueError(f'boolean result has an internal void of {-min(voids):.2e} m3')
    keep = [from_mf(c) for c in comps if c.volume() > 1e-7]
    out = trimesh.util.concatenate(keep) if len(keep) > 1 else keep[0]
    return out, dict(shells=len(keep), extra_shell_volume_m3=round(float(sum(k.volume for k in keep[1:])), 7))


def fit_limit(a, b):
    """Overlap allowed between two fitted parts: 1 cm3 plus 10 micrometres over the smaller surface (float32)."""
    return FIT + 1e-5 * min(a.area, b.area) / 2


def bent_box(x0, n0, n1, t0, t1, z0, z1):
    """Box in (n, t, z) coordinates of the bent through X = x0, returned in native coordinates."""
    box = trimesh.creation.box(bounds=[[n0, t0, z0], [n1, t1, z1]])
    m = np.eye(4)
    m[:3, 0], m[:3, 1], m[:3, 2], m[:3, 3] = N, T, (0.0, 0.0, 1.0), (x0, 0.0, 0.0)
    box.apply_transform(m)
    return box


def bent_nt(v, x0):
    d = np.asarray(v, dtype=np.float64)[:, :2] - (x0, 0.0)
    return d @ N[:2], d @ T[:2]


def stepped_cap(x0, levels, z_bottom, half_n, half_t, end_y=None):
    """Cap with three level terraces and vertical steps at t = +/-STEP, extruded across n = +/-half_n. With end_y
    the ends are moved onto the planes Y = +/-end_y (parallel to Line M); otherwise they are square at +/-half_t."""
    zs, zc, zn = levels
    profile = Polygon([(-half_t, z_bottom), (half_t, z_bottom), (half_t, zn), (STEP, zn), (STEP, zc),
                       (-STEP, zc), (-STEP, zs), (-half_t, zs)])                 # (t, z)
    cap = trimesh.creation.extrude_polygon(profile, 2 * half_n)                  # local (t, z, n + half_n)
    v = cap.vertices.copy()
    if end_y is not None:
        n = v[:, 2] - half_n
        for sign in (1, -1):
            sel = np.abs(v[:, 0] - sign * half_t) < 1e-9
            v[sel, 0] = (sign * end_y - n[sel] * S) / C
    cap = trimesh.Trimesh(v, cap.faces, process=False)
    m = np.eye(4)                                # local (t, z, n + half_n) -> native; T x Z = N
    m[:3, 0], m[:3, 1], m[:3, 2] = T, (0.0, 0.0, 1.0), N
    m[:3, 3] = np.array([x0, 0.0, 0.0]) - half_n * N
    cap.apply_transform(m)
    return cap


def surface_hits(mesh, x, y):
    """All Z where a vertical line through (x, y) crosses the mesh (brute force)."""
    tri = mesh.triangles
    a, b, c = tri[:, 0], tri[:, 1], tri[:, 2]
    d = (b[:, 1] - c[:, 1]) * (a[:, 0] - c[:, 0]) + (c[:, 0] - b[:, 0]) * (a[:, 1] - c[:, 1])
    ok = np.abs(d) > 1e-12
    dd = np.where(ok, d, 1.0)
    l1 = ((b[:, 1] - c[:, 1]) * (x - c[:, 0]) + (c[:, 0] - b[:, 0]) * (y - c[:, 1])) / dd
    l2 = ((c[:, 1] - a[:, 1]) * (x - c[:, 0]) + (a[:, 0] - c[:, 0]) * (y - c[:, 1])) / dd
    l3 = 1 - l1 - l2
    hit = ok & (l1 >= -1e-9) & (l2 >= -1e-9) & (l3 >= -1e-9)
    return (l1 * a[:, 2] + l2 * b[:, 2] + l3 * c[:, 2])[hit]


def surface_z(mesh, xy, top=True):
    """Z of the upper (top=True) or lower surface of a mesh on vertical lines through xy (brute force)."""
    tri = mesh.triangles
    a, b, c = tri[:, 0], tri[:, 1], tri[:, 2]
    d = (b[:, 1] - c[:, 1]) * (a[:, 0] - c[:, 0]) + (c[:, 0] - b[:, 0]) * (a[:, 1] - c[:, 1])
    ok = np.abs(d) > 1e-12
    dd = np.where(ok, d, 1.0)
    out = []
    for x, y in np.atleast_2d(xy):
        l1 = ((b[:, 1] - c[:, 1]) * (x - c[:, 0]) + (c[:, 0] - b[:, 0]) * (y - c[:, 1])) / dd
        l2 = ((c[:, 1] - a[:, 1]) * (x - c[:, 0]) + (a[:, 0] - c[:, 0]) * (y - c[:, 1])) / dd
        l3 = 1 - l1 - l2
        hit = ok & (l1 >= -1e-9) & (l2 >= -1e-9) & (l3 >= -1e-9)
        zs = (l1 * a[:, 2] + l2 * b[:, 2] + l3 * c[:, 2])[hit]
        out.append(np.nan if len(zs) == 0 else (zs.max() if top else zs.min()))
    return np.array(out)


def on_surface(points, mesh, tol=2e-5):
    """True for points lying on a triangle of mesh (within tol of its plane and inside it); brute force."""
    tri = mesh.triangles
    a, e1, e2 = tri[:, 0], tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]
    nrm = np.cross(e1, e2)
    size = np.linalg.norm(nrm, axis=1)
    ok = size > 1e-12
    nrm = nrm / np.where(ok, size, 1.0)[:, None]
    d00, d01, d11 = (e1 * e1).sum(1), (e1 * e2).sum(1), (e2 * e2).sum(1)
    den = np.where(ok, d00 * d11 - d01 * d01, 1.0)
    out = np.zeros(len(points), bool)
    for i, p in enumerate(np.asarray(points, dtype=np.float64)):
        w = p - a
        dist = np.abs((w * nrm).sum(1))
        d20, d21 = (w * e1).sum(1), (w * e2).sum(1)
        bv = (d11 * d20 - d01 * d21) / den
        bw = (d00 * d21 - d01 * d20) / den
        out[i] = bool(np.any(ok & (dist < tol) & (bv >= -1e-6) & (bw >= -1e-6) & (bv + bw <= 1 + 1e-6)))
    return out


def correct(dry_run=False):
    mp = BASE / 'model_manifest.json'
    raw_manifest = mp.read_bytes()
    manifest = json.loads(raw_manifest)
    if manifest.get('review_geometry_correction_3') == TAG:
        print('Already corrected.')
        return
    if (manifest.get('review_geometry_correction_2') != PREVIOUS_TAG
            or manifest.get('revision') != PREVIOUS_REVISION):
        raise ValueError('Run scripts/correct_21st_street_i465_review_2.py first (expected revision '
                         f'{PREVIOUS_REVISION}, found {manifest.get("revision")}).')
    path = BASE / 'model.glb'
    original = path.read_bytes()
    before = hashlib.sha256(original).hexdigest()
    if before != manifest['review_geometry_correction_2_record']['after_glb_sha256']:
        raise ValueError('model.glb differs from the output of the second correction')
    if [d.get('id') for d in manifest.get('known_deviations', [])] != [DEVIATION]:
        raise ValueError(f'known_deviations: expected only {DEVIATION}')
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

    def prim(pid):
        ps = meshes[pid]['primitives']
        if len(ps) != 1:
            raise ValueError(f'{pid}: expected one primitive')
        return ps[0]

    def solid(pid):
        p = prim(pid)
        return trimesh.Trimesh(vertices=read(p['attributes']['POSITION']).astype(np.float64),
                               faces=read(p['indices']).reshape(-1, 3), process=False)

    def overlap(a, b):
        return float(boolean('intersection', [a, b]).volume)

    def near_ids(box_lo, box_hi, exclude=(), pad=0.02):
        return [p['id'] for p in manifest['parts'] if p['id'] not in exclude
                and np.all(np.array(p['bounds_m'])[0] <= np.asarray(box_hi) + pad)
                and np.all(np.array(p['bounds_m'])[1] >= np.asarray(box_lo) - pad)]

    r6 = lambda v: round(float(v), 6)

    # ================================================================ 1. DECIDE: Bent 2 diaphragm stays flush
    cap2, dia2 = solid('pier_cap'), solid('diaphragm_pier')
    cn, dn = cap2.vertices @ N, dia2.vertices @ N
    cap2_top = float(cap2.bounds[1][2])
    if abs(cn.min() + HALF) > TOL or abs(cn.max() - HALF) > TOL or abs(cap2_top - 9.6012) > TOL:
        raise ValueError('pier_cap: expected the 4 ft cap (n = +/-0.6096 m) with its top at El. 761.50')
    if (not dia2.is_watertight or dia2.volume <= 0 or abs(dn.min() + HALF) > TOL or abs(dn.max() - HALF) > TOL
            or abs(dia2.bounds[0][2] - (cap2_top + CAP_JOINT)) > TOL):
        raise ValueError('diaphragm_pier: expected faces flush with the cap faces (n = +/-0.6096 m) and the '
                         'underside on 1 in joint material above the cap')
    tri_n = dia2.triangles @ N
    face_area = [round(float(dia2.area_faces[np.all(np.abs(tri_n - s * HALF) < TOL, axis=1)].sum()), 4)
                 for s in (1, -1)]
    if min(face_area) <= 1.0:
        raise ValueError('diaphragm_pier: no face area in the cap face planes')
    if abs(STIRRUP_505A + 2 * COVER - 2 * HALF) > 1e-9:
        raise ValueError('505a stirrup with 2 in cover should be exactly the 4 ft diaphragm width')
    plan_cover = round((2 * HALF - 2 * PLAN_SETBACK - STIRRUP_505A) / 2 / IN, 3)   # -1 in: bar outside
    print(f'diaphragm_pier: faces n = {dn.min():+.6f} / {dn.max():+.6f} m (cap {cn.min():+.6f} / '
          f'{cn.max():+.6f}), face area {face_area} m2; 505a cover {COVER / IN:.1f} in at 4\'-0", '
          f'{plan_cover:+.1f} in at the sheet 54 plan line')
    decision = dict(
        id=DEVIATION, verdict='DECIDE', parts=['diaphragm_pier'],
        decision='Diaphragm faces flush with the cap faces, 2\'-0" either side of CL Bent 2 (4\'-0" normal to the '
                 'bent), on 1 in preformed expansion joint material across the full width. Geometry unchanged '
                 'from revision 1.2.',
        reasoning='Sheet 57 section V-V draws each diaphragm face as one line with the cap face and the 1 in joint '
                  'material across the full 4\'-0"; its 505a stirrups are 2 in inside each face. Sheet 58 gives '
                  'bar 505a 3\'-8" wide and 2 in minimum cover in all other parts, which needs exactly 4\'-0". '
                  'Sheet 45 gives the 4\'-0" cap. The sheet 54 plan line 3 in inside the cap face (3\'-6" between '
                  'edges) is undimensioned, would leave the 505a stirrups 1 in outside the concrete, and sits on a '
                  'detail drawn at 78 deg although it labels the 72 deg beam angle.',
        rejected_reading='Sheet 54 BEAM END DETAIL AT BENT #2: edge of diaphragm and joint material 3 in inside '
                         'the face of bent cap, scaled at 3/4 in = 1 ft.',
        sources='sheet 45 (PDF 45) plan of cap; sheet 54 (PDF 54) BEAM END DETAIL AT BENT #2; sheet 57 (PDF 57) '
                'section V-V and typical section @ Bent #2 diaphragm (11-505a); sheet 58 (PDF 58) bar 505a x '
                '16\'-4" and reinforcing cover note',
        verification=dict(diaphragm_faces_n_m=[r6(dn.min()), r6(dn.max())], cap_faces_n_m=[r6(cn.min()), r6(cn.max())],
                          face_area_in_cap_face_planes_m2=face_area, underside_z_m=r6(dia2.bounds[0][2]),
                          stirrup_505a_cover_in={'flush_4ft': COVER / IN, 'sheet54_plan_line': plan_cover}))

    # ================================================================ 2. end bents: starting state, new caps
    old, new = {}, {}                            # trimesh solids before / after, by part id
    positions = {}                               # new float32 vertices for parts keeping their faces
    remeshed = {}                                # caps and end diaphragms: new vertices and faces
    beam_info = {}
    for bent, cfg in END_BENTS.items():
        x0 = cfg['x0']
        levels = [z_of(e) for e in cfg['el']]
        z_bottom = z_of(cfg['bottom'])
        cap = old[cfg['cap']] = solid(cfg['cap'])
        n, t = bent_nt(cap.vertices, x0)
        z = cap.vertices[:, 2]
        if (len(cap.vertices) != 18 or not cap.is_watertight or abs(np.abs(n).max() - CAP_HALF_N) > TOL
                or abs(np.abs(t).max() - CAP_HALF_T) > TOL or abs(z.min() - z_bottom) > TOL):
            raise ValueError(f'{cfg["cap"]}: expected the square-ended 3 ft x 50\'-10 1/2" cap, bottom El. '
                             f'{cfg["bottom"]}')
        top = z > z_bottom + 0.1
        for sel, level in zip([top & (t < -5.9), top & (np.abs(t) < 1e-4), top & (t > 5.9)], levels):
            if not sel.any() or np.abs(z[sel] - level).max() > TOL:
                raise ValueError(f'{cfg["cap"]}: expected the interpolated top at El. {cfg["el"]}')
        new[cfg['cap']] = stepped_cap(x0, levels, z_bottom, CAP_HALF_N, CAP_HALF_T, end_y=CAP_END_Y)
        expected = 2 * CAP_HALF_N * sum((t1 - t0) * (zt - z_bottom) for (t0, t1), zt in zip(
            [(-CAP_HALF_T, -STEP), (-STEP, STEP), (STEP, CAP_HALF_T)], levels))
        nc = new[cfg['cap']]
        if (not nc.is_watertight or abs(nc.volume - expected) > 1e-9
                or abs(np.abs(nc.vertices[:, 1]).max() - CAP_END_Y) > 1e-9
                or abs(np.abs(bent_nt(nc.vertices, x0)[0]).max() - CAP_HALF_N) > 1e-9):
            raise ValueError(f'{cfg["cap"]}: invalid stepped cap')

        # ---- pads: level, 1 3/16 in, on the terrace of their beam, 2'-4 3/8" apart along the bent
        for i in (1, 2, 3):
            k = f'{cfg["span"]}{i}'
            beam = old[f'beam_{k}'] = solid(f'beam_{k}')
            yk = float(beam.bounds[:, 1].mean())
            pair = []
            for j in (1, 2):
                pid = f'pad_{k}_{cfg["end"]}_{j}'
                pad = old[pid] = solid(pid)
                pn, pt = bent_nt(pad.vertices, x0)
                ok = [pt.max() < -STEP - 0.05, np.abs(pt).max() < STEP - 0.05, pt.min() > STEP + 0.05][i - 1]
                if (len(pad.vertices) != 8 or abs(pad.bounds[0][2] - levels[i - 1]) > TOL or not ok
                        or abs(np.ptp(pad.vertices[:, 2]) - PAD_T_OLD) > TOL or abs(pn.mean()) > TOL):
                    raise ValueError(f'{pid}: expected a level 1 3/16 in pad on CL Bent on its terrace')
                pair.append((pid, float(pt.mean())))
            if abs(pair[1][1] - pair[0][1] - PAD_OFFSET / C * 2) > TOL or abs(sum(p[1] for p in pair) / 2 - yk / C) > TOL:
                raise ValueError(f'beam_{k}: expected the pad pair 2\'-3" apart normal to the beam about CL Beam')
            for (pid, tc), sign in zip(pair, (-1, 1)):
                v = old[pid].vertices.copy()
                v[:, :2] += ((yk / C + sign * PAD_OFFSET) - tc) * T[:2]
                v[v[:, 2] > v[:, 2].min() + 1e-6, 2] = v[:, 2].min() + PAD_T
                positions[pid] = v.astype('<f4')
            w = float(np.abs(beam.vertices[:, 1] - yk).max()) + 0.05      # beam half width + 50 mm
            beam_info[k] = dict(bent=bent, yk=yk, x_bearing=x0 - yk * np.tan(SKEW),
                                # Bent 2 diaphragm face on the span side, at the beam edge nearest the span
                                x_pivot=(cfg['side'] * HALF - (yk - cfg['side'] * w) * S) / C,
                                along=-cfg['side'])                              # +X from Bent 1, -X from Bent 3

    # ================================================================ 3. beams lowered with the pads
    groups = {}
    for k, info in beam_info.items():
        xb, xk = info['x_bearing'], info['x_pivot']

        def f(x, xb=xb, xk=xk):
            r = (xk - np.asarray(x)) / (xk - xb)         # 1 at the end-bent bearing, 0 at the Bent 2 diaphragm face
            return -DROP * np.clip(r, 0.0, None)

        info['f'] = f
        ids = [pid for pid in parts if pid == f'beam_{k}' or pid.startswith(f'beam_{k}_endblock_')
               or pid.startswith(f'brace_{k}_') or re.match(rf'door(_frame|_hinge|_grab|_hasp)?_{k}_', pid)]
        if len(ids) != 30:
            raise ValueError(f'beam_{k}: expected 30 carried parts, found {len(ids)}')
        groups[k] = ids
        for pid in ids:
            m = old.setdefault(pid, solid(pid))
            v = m.vertices.copy()
            v[:, 2] += f(v[:, 0])
            positions[pid] = v.astype('<f4')
        for h in (1, 2):                         # haunches: bottom follows the beam, top stays at the deck
            pid = f'haunch_{k}_{h}'
            m = old[pid] = solid(pid)
            v = m.vertices.copy()
            keys = np.round(v[:, :2], 6)
            _, inv, cnt = np.unique(keys, axis=0, return_inverse=True, return_counts=True)
            if np.any(cnt != 2):
                raise ValueError(f'{pid}: expected bottom/top vertex pairs')
            low = np.ones(len(v), bool)
            for g in range(cnt.size):
                a, b = np.nonzero(inv.ravel() == g)[0]
                low[b if v[b, 2] > v[a, 2] else a] = False
            v[low, 2] += f(v[low, 0])
            positions[pid] = v.astype('<f4')
            groups[k].append(pid)
    for q in [q for q, v in positions.items() if np.array_equal(v, old[q].vertices.astype('<f4'))]:
        del positions[q]                        # inside the Bent 2 diaphragm: nothing moves
    groups = {k: [pid for pid in ids if pid in positions] for k, ids in groups.items()}
    for pid, v in positions.items():
        new[pid] = trimesh.Trimesh(v.astype(np.float64), old[pid].faces, process=False)
        if not new[pid].is_watertight or new[pid].volume <= 0:
            raise ValueError(f'{pid}: invalid after the move')

    # ================================================================ 4. end diaphragms rebuilt
    interfaces = {}
    for bent, cfg in END_BENTS.items():
        x0 = cfg['x0']
        levels = [z_of(e) for e in cfg['el']]
        z_bottom = z_of(cfg['bottom'])
        dia = old[cfg['dia']] = solid(cfg['dia'])
        dn0, _ = bent_nt(dia.vertices, x0)
        n_lo, n_hi = float(dn0.min()), float(dn0.max())
        if not dia.is_watertight or abs(n_hi - 0.434823) > 1e-4 or abs(n_lo + 0.434823) > 1e-4:
            raise ValueError(f'{cfg["dia"]}: expected the 2\'-10 1/4" diaphragm of revision 1.2')
        ks = [f'{cfg["span"]}{i}' for i in (1, 2, 3)]
        # Carry the diaphragm with the beams: its vertices on the old beam / end-block surfaces (the beam voids)
        # take the same z += f(x) as the beams; then its face vertices move out to the cap faces along X (the
        # beams, haunches, deck soffit and the skewed ends are all prismatic along X here).
        v = dia.vertices.copy()
        carried = np.zeros(len(v), bool)
        owner = np.full(len(v), '', dtype=object)
        for k in ks:
            on = (on_surface(v, old[f'beam_{k}']) | on_surface(v, old[f'beam_{k}_endblock_{cfg["end"]}'])) & ~carried
            v[on, 2] += beam_info[k]['f'](v[on, 0])
            carried |= on
            owner[on] = k
        deck = solid('deck')
        on_deck = on_surface(dia.vertices, deck)
        vn, _ = bent_nt(v, x0)
        front, back = np.abs(vn - n_hi) < 1e-5, np.abs(vn - n_lo) < 1e-5
        v[front, 0] += (CAP_HALF_N - n_hi) / C
        v[back, 0] += (-CAP_HALF_N - n_lo) / C
        # moved face vertices back onto the deck soffit and the (lowered) beam surfaces at their new positions
        snapped = 0
        for i in np.nonzero(front | back)[0]:
            if on_deck[i]:
                v[i, 2] = surface_z(deck, v[i:i + 1, :2], top=False)[0]
                snapped += 1
            elif carried[i]:
                zs = surface_hits(new[f'beam_{owner[i]}'], v[i, 0], v[i, 1])
                if len(zs) and np.abs(zs - v[i, 2]).min() < 0.002:
                    v[i, 2] = zs[np.abs(zs - v[i, 2]).argmin()]
                    snapped += 1
        widened = trimesh.Trimesh(v, dia.faces, process=False)
        if not widened.is_watertight or widened.volume <= dia.volume:
            raise ValueError(f'{cfg["dia"]}: invalid carried/widened diaphragm')
        counts = dict(carried_vertices=int(carried.sum()), face_vertices_moved=int(front.sum() + back.sum()),
                      face_vertices_snapped=snapped,
                      vertices=len(v))
        # pad layer under each new beam bottom over the cap
        clip = Polygon([(x0 + nq * C - tq * S, nq * S + tq * C) for nq, tq in
                        [(-CAP_HALF_N - 0.01, -CAP_HALF_T - 0.3), (CAP_HALF_N + 0.01, -CAP_HALF_T - 0.3),
                         (CAP_HALF_N + 0.01, CAP_HALF_T + 0.3), (-CAP_HALF_N - 0.01, CAP_HALF_T + 0.3)]])
        layer, soffits = [], {}
        for k in ks:
            beam = new[f'beam_{k}']
            fz = beam.triangles[:, :, 2]
            bottom = (beam.face_normals[:, 2] < -0.999) & (fz.max(axis=1) < beam.bounds[0][2] + 0.05)
            foot = unary_union([Polygon(tri[:, :2]).buffer(0) for tri in beam.triangles[bottom]]).intersection(clip)
            if foot.geom_type != 'Polygon' or foot.area < 0.5:
                raise ValueError(f'beam_{k}: could not find its bottom face over {cfg["cap"]}')
            soffit = surface_z(beam, np.array(foot.buffer(-0.005).exterior.coords), top=False)
            soffits[f'beam_{k}'] = [r6(np.nanmin(soffit)), r6(np.nanmax(soffit))]
            cut = trimesh.creation.extrude_polygon(foot, float(np.nanmax(soffit)) + 0.002 - (z_bottom - 0.1))
            cut.apply_translation([0.0, 0.0, z_bottom - 0.1])
            layer.append(cut)
        cap_cut = stepped_cap(x0, levels, z_bottom - 0.1, CAP_HALF_N + 0.05, CAP_HALF_T + 0.5)
        others = [solid(pid) for pid in ['deck', cfg['joint']] + cfg['approach']]
        haunches = [new[f'haunch_{k}_{h}'] for k in ks for h in (1, 2)]
        pads = [new[f'pad_{k}_{cfg["end"]}_{j}'] for k in ks for j in (1, 2)]
        blocks = [new[f'beam_{k}_endblock_{cfg["end"]}'] for k in ks]
        beams = [new[f'beam_{k}'] for k in ks]
        rebuilt, shells = solid_parts(boolean('difference', [widened, cap_cut] + others + beams + haunches + pads
                                                    + blocks + layer))
        new[cfg['dia']] = rebuilt
        rn, _ = bent_nt(rebuilt.vertices, x0)
        if (not rebuilt.is_watertight or rebuilt.volume <= 0 or abs(rn.min() + CAP_HALF_N) > TOL
                or abs(rn.max() - CAP_HALF_N) > TOL):
            raise ValueError(f'{cfg["dia"]}: invalid rebuilt diaphragm')
        interfaces[f'bent_{bent}'] = dict(beam_soffit_over_cap_m=soffits, diaphragm_vertex_moves=counts,
                                          diaphragm_shells=shells,
                                          diaphragm_faces_n_m_before_after=[[r6(n_lo), r6(n_hi)],
                                                                            [r6(rn.min()), r6(rn.max())]])

    # ================================================================ 5. contacts on the new geometry
    changed_ids = list(new)
    for bent, cfg in END_BENTS.items():
        x0, rec = cfg['x0'], interfaces[f'bent_{bent}']
        cap_new, dia_new = new[cfg['cap']], new[cfg['dia']]
        ks = [f'{cfg["span"]}{i}' for i in (1, 2, 3)]
        pads = [f'pad_{k}_{cfg["end"]}_{j}' for k in ks for j in (1, 2)]
        seat, beam_fit = {}, {}
        for pid in pads:
            pad = new[pid]
            bot = pad.vertices[pad.vertices[:, 2] < pad.bounds[0][2] + 1e-6]
            pts = np.vstack([bot[:, :2], bot[:, :2].mean(axis=0)])
            seat[pid] = float(np.max(np.abs(surface_z(cap_new, pts) - pad.bounds[0][2])))
            topv = pad.vertices[pad.vertices[:, 2] > pad.bounds[1][2] - 1e-6]
            d = surface_z(new[f'beam_{pid[4:6]}'], topv[:, :2], top=False) - pad.bounds[1][2]
            beam_fit[pid] = [r6(d.min()), r6(d.max())]
            if seat[pid] > 2e-6 or np.abs(d).max() > 0.001:
                raise ValueError(f'{pid}: not seated (cap {seat[pid]:.2e} m, beam {d.min():.2e}..{d.max():.2e} m)')
            for other in (cfg['cap'], cfg['dia']):
                if overlap(pad, new[other]) > FIT:
                    raise ValueError(f'{pid}: overlaps {other}')
        # every part touching the new cap or diaphragm, old against new
        lo = np.minimum(cap_new.bounds[0], dia_new.bounds[0])
        hi = np.maximum(cap_new.bounds[1], dia_new.bounds[1])
        olds = {pid: old[pid] if pid in old else solid(pid)
                for pid in near_ids(lo, hi, exclude=(cfg['cap'], cfg['dia']))}
        rows = {}
        for pid, m_old in olds.items():
            if not m_old.is_watertight:
                continue
            m_new = new.get(pid, m_old)
            for host in (cfg['cap'], cfg['dia']):
                b, a = overlap(old[host], m_old), overlap(new[host], m_new)
                if max(a, b) > CLASH:
                    rows[f'{host}_x_{pid}'] = [r6(b), r6(a)]
                allowed = b if (host == cfg['cap'] and pid.startswith('b') and '_pile_' in pid) else 0.0
                if a > allowed + fit_limit(new[host], m_new):
                    raise ValueError(f'{host} overlaps {pid}: {a:.3e} m3')
        rows[f'{cfg["dia"]}_x_{cfg["cap"]}'] = [r6(overlap(old[cfg['dia']], old[cfg['cap']])),
                                               r6(overlap(dia_new, cap_new))]
        if rows[f'{cfg["dia"]}_x_{cfg["cap"]}'][1] > 1e-6:
            raise ValueError(f'{cfg["dia"]}: overlaps the cap')
        probe = []
        for tq in np.linspace(-7.6, 7.6, 77):
            for nq in (-0.45, -0.3, 0.0, 0.3, 0.45):
                xy = np.array([[x0 + nq * C - tq * S, nq * S + tq * C]])
                zd = surface_z(dia_new, xy, top=False)[0]
                zc = surface_z(stepped_cap(x0, [z_of(e) for e in cfg['el']], z_of(cfg['bottom']), CAP_HALF_N,
                                           CAP_HALF_T + 0.5), xy, top=True)[0]
                if not np.isnan(zd) and zd < zc + 0.05:
                    probe.append(zd - zc)
        if not probe or max(abs(v) for v in probe) > 1e-5:
            raise ValueError(f'{cfg["dia"]}: underside not on the cap terraces')
        rec.update(pad_seat_mismatch_max_m=r6(max(seat.values())), pad_top_minus_beam_soffit_m=beam_fit,
                   diaphragm_underside_on_terrace_probes=len(probe), overlaps_m3_before_after=rows)
        print(f'bent {bent}: pads seated (max {max(seat.values()) * 1000:.4f} mm); {cfg["cap"]} '
              f'{old[cfg["cap"]].volume:.4f} -> {cap_new.volume:.4f} m3; {cfg["dia"]} '
              f'{old[cfg["dia"]].volume:.4f} -> {dia_new.volume:.4f} m3; overlaps {rows}')
    # beams and carried parts against everything that did not move (deck, Bent 2, approaches)
    moved = [pid for k in groups for pid in groups[k]]
    fixed_checked = {}
    for pid in sorted({p for p in moved if p.startswith(('haunch_', 'beam_'))}):
        m_old, m_new = old[pid], new[pid]
        lo = np.minimum(m_old.bounds[0], m_new.bounds[0])
        hi = np.maximum(m_old.bounds[1], m_new.bounds[1])
        for qid in near_ids(lo, hi, exclude=set(new) | {pid}):
            q = solid(qid)
            if not q.is_watertight:
                continue
            b, a = overlap(m_old, q), overlap(m_new, q)
            if a > b + 1e-6:
                raise ValueError(f'{pid} x {qid}: overlap grew {b:.3e} -> {a:.3e} m3')
            if max(a, b) > CLASH:
                fixed_checked[f'{pid}_x_{qid}'] = [r6(b), r6(a)]

    # ---------------------------------------------------------------- write meshes
    for pid in changed_ids:
        p = prim(pid)
        if pid in positions:
            p['attributes']['POSITION'] = append(positions[pid], 'VEC3', 5126)
            stored = new[pid]
        else:
            mesh = new[pid]
            color = read(p['attributes']['COLOR_0'])[0]
            vertices = mesh.vertices.astype('<f4')
            p['attributes'] = {'POSITION': append(vertices, 'VEC3', 5126),
                               'COLOR_0': append(np.tile(color, (len(vertices), 1)).astype('u1'), 'VEC4', 5121)}
            gltf['accessors'][p['attributes']['COLOR_0']]['normalized'] = True
            p['indices'] = append(mesh.faces.reshape(-1, 1).astype('<u4'), 'SCALAR', 5125)
            stored = trimesh.Trimesh(vertices=vertices.astype(np.float64), faces=mesh.faces, process=False)
        if not stored.is_watertight or stored.volume <= 0:
            raise ValueError(f'{pid}: not watertight after float32 storage')
        parts[pid]['bounds_m'] = stored.bounds.round(6).tolist()
        parts[pid]['volume_m3'] = round(float(stored.volume), 8)
        new[pid] = stored

    # ---------------------------------------------------------------- manifest entries
    vol = {pid: (old[pid].volume, new[pid].volume) for pid in changed_ids}
    for bent, cfg in END_BENTS.items():
        s_el, c_el, n_el = cfg['el']
        cap, dia = parts[cfg['cap']], parts[cfg['dia']]
        cap['basis'] = 'Dimensioned envelope; stepped top at source elevations'
        cap['pdf_pages'] = sorted(set(cap['pdf_pages']) | {42})
        cap['dimensions'].update(top_el_ft={'south': s_el, 'centre': c_el, 'north': n_el},
                                 step_from_cl_structure_ft=round(STEP / FT, 6), end_y_m=round(CAP_END_Y, 6))
        a, b = vol[cfg['cap']]
        cap['note'] += (f' Top rebuilt as the three level terraces of sheet 42 (El. {s_el} south / {c_el} centre / '
                        f'{n_el} north) with vertical steps square to the bent 9\'-7 3/4" either side of CL '
                        'Structure, and the ends set parallel to Line M as drawn on the sheet 42 plan (Y = +/-'
                        f'{CAP_END_Y:.6f} m); previously a ridge interpolated between the beam centrelines and '
                        f'square ends ({b - a:+.3f} m3).')
        a, b = vol[cfg['dia']]
        dia['pdf_pages'] = sorted(set(dia['pdf_pages']) | {42})
        dia['dimensions']['width_ft'] = 3.0
        dia['basis'] = 'Dimensioned width; fitted to cap, beams, deck and approach slab'
        dia['note'] += (' Rebuilt: faces moved out to the cap faces, 1\'-6" either side of CL Bent (sheet 58 '
                        'sections C-C and D-D; previously 2\'-10 1/4" wide); seated on the stepped cap top (sheet 42 '
                        'keyway construction joint) where it had run 80-220 mm into the cap; the layer between the '
                        'cap and each beam soffit left open over the beam bottom (pads and 7/8 in preformed joint '
                        'material, sheet 42); refitted around the lowered beams, haunches and end blocks; approach '
                        f'slab ledge cut where the slab bears on it (sheet 58 C-C) ({b - a:+.3f} m3).')
        for k in [f'{cfg["span"]}{i}' for i in (1, 2, 3)]:
            for j in (1, 2):
                pad = parts[f'pad_{k}_{cfg["end"]}_{j}']
                pad['dimensions']['thickness_in'] = 0.8125
                pad['pdf_pages'] = sorted(set(pad['pdf_pages']) | {42})
                pad['note'] += (' Thickness corrected from 1 3/16 in to 13/16 in (sheet 54 end bent pad table) and '
                                'CL pad moved to 1\'-1 1/2" from CL Beam along the bent (sheet 42 plan); bottom '
                                'unchanged on the cap terrace.')
                ex = meshes[pad['id']].setdefault('extras', {})
                if 'extents' in ex:
                    ex['extents'][2] = PAD_T
    for k, info in beam_info.items():
        for pid in groups[k]:
            parts[pid]['note'] = (parts[pid].get('note', '') + f' Lowered with beam_{k}: 3/8 in at the end-bent '
                                  'bearing (13/16 in pads, sheet 54), tapering to 0 at the Bent 2 diaphragm face'
                                  + ('; top kept at the deck underside.' if pid.startswith('haunch_') else '.')).strip()
    for pid in changed_ids:
        meshes[pid].setdefault('extras', {}).update(parts[pid])

    b = np.array([q['bounds_m'] for q in manifest['parts']])
    lo, hi = b[:, 0].min(axis=0), b[:, 1].max(axis=0)
    manifest['bounds_m'] = [lo.round(6).tolist(), hi.round(6).tolist()]
    manifest['glb_bounds_m'] = [[round(lo[0], 6), round(lo[2], 6), round(-hi[1], 6)],
                                [round(hi[0], 6), round(hi[2], 6), round(-lo[1], 6)]]
    for d in manifest['detail_coverage']:
        if d['feature'] == 'Beam end blocks and concrete diaphragms':
            d['detail'] += (' The sheet 54 plan line 3 in inside the Bent 2 cap face is not modelled: the 3\'-8" 505a '
                            'stirrups with 2 in cover (sheet 58) need the 4 ft flush width of section V-V. End-bent '
                            'diaphragms are 3 ft wide, flush with the caps (sheet 58 C-C, D-D), seated on the '
                            'stepped cap tops with the pad layer under each beam open and the approach-slab ledge '
                            'cut.')
            d['sources'] = sorted(set(d['sources']) | {42, 45})
        elif d['feature'] == 'Integral end bents and piles':
            d['detail'] += (' Cap tops are the three level terraces of sheet 42 with steps 9\'-7 3/4" either side '
                            'of CL Structure; cap ends parallel to Line M (sheet 42 plan).')
        elif d['feature'] == 'Paired elastomeric bearings':
            d['detail'] = d['detail'].replace('11x19x1-3/16 in at end bents', '11x19x13/16 in at end bents')
            d['detail'] += (' End-bent pads 13/16 in (sheet 54) with CL pads 1 ft 1-1/2 in from CL Beam along the '
                            'bent (sheet 42); beams bear 3/8 in lower there than before.')
            d['sources'] = sorted(set(d.get('sources', [])) | {42, 54})
        elif d['feature'] == 'Beam longitudinal elevation and haunches':
            d['detail'] += (' End-bent bearing levels are cap El. + 13/16 in (sheet 54); beam ends there lowered '
                            '3/8 in, haunches thickened accordingly.')
    manifest['known_deviations'] = []
    manifest['review_geometry_correction_3'] = TAG
    manifest['revision'] = REVISION

    gltf['buffers'][0]['byteLength'] = len(binary)
    while len(binary) % 4:
        binary.append(0)
    encoded = json.dumps(gltf, ensure_ascii=True, separators=(',', ':')).encode()
    encoded += b' ' * ((-len(encoded)) % 4)
    out = (struct.pack('<III', 0x46546c67, 2, 28 + len(encoded) + len(binary)) +
           struct.pack('<II', len(encoded), 0x4e4f534a) + encoded + struct.pack('<II', len(binary), 0x004e4942) + binary)
    manifest['review_correction_record_3'] = dict(
        source_pdf_pages=[42, 45, 54, 57, 58], printed_sheets=[42, 45, 54, 57, 58],
        previous_revision=PREVIOUS_REVISION,
        decisions=[decision],
        decided_deviations=[DEVIATION],
        resolved=[
            dict(id='end-bent-cap-terraces', parts=[c['cap'] for c in END_BENTS.values()],
                 correction='Cap tops rebuilt as the three level terraces of sheet 42 (Bent 1 El. 761.53 / 761.82 / '
                            '761.36, Bent 3 El. 761.04 / 761.51 / 761.23, south / centre / north) with vertical '
                            'steps square to the bent 9\'-7 3/4" either side of CL Structure.',
                 step_decision='The step is dimensioned 9\'-7 3/4" in the sheet 42 elevation (right half) and plan '
                               '(2\'-5 1/8" + 6\'-8 3/4" from CL Structure on the back face); the left-half step is '
                               'undimensioned, drawn at 9\'-7 3/4" in the elevation and about 9\'-3" in the plan. '
                               'The symmetric 9\'-7 3/4" is used; no part bears within 2 m of either line.',
                 sources='sheet 42 (PDF 42) PLAN and ELEVATION'),
            dict(id='end-bent-cap-square-ends', parts=[c['cap'] for c in END_BENTS.values()],
                 correction=f'Cap ends set parallel to Line M at Y = +/-{CAP_END_Y:.6f} m (25\'-5 1/4" from CL '
                            'Structure along CL Bent; 11 3/4" offset between the faces); previously square to the '
                            'bent. The monument_A / monument_D cap overlaps (0.022 m3 each) are gone.',
                 sources='sheet 42 (PDF 42) PLAN (50\'-10 1/2", 25\'-5 1/4" + 25\'-5 1/4", 11 3/4")'),
            dict(id='end-bent-pad-thickness', parts=[f'pad_{c["span"]}{i}_{c["end"]}_{j}' for c in END_BENTS.values()
                                                     for i in (1, 2, 3) for j in (1, 2)] + sorted(moved),
                 correction='End-bent pads 1 3/16 in -> 13/16 in, bottoms on the cap terraces; the six span beams '
                            'and their end blocks, steel cross frames, access doors and haunch bottoms lowered 3/8 '
                            'in (9.525 mm) at the end-bent bearing, tapering linearly to 0 at the Bent 2 diaphragm '
                            'face; haunch tops and deck unchanged.',
                 sources='sheet 54 (PDF 54) END BENT BEARING PAD DIMENSIONS, END BENT ELASTOMERIC BEARING PAD'),
            dict(id='end-bent-pad-spacing', parts=[f'pad_{c["span"]}{i}_{c["end"]}_{j}' for c in END_BENTS.values()
                                                   for i in (1, 2, 3) for j in (1, 2)],
                 correction='CL bearing pads 1\'-1 1/2" either side of CL Beam along the bent (pair spacing '
                            '0.685800 m, previously 0.721093 m = 2\'-3" normal to the beam); each pad moved '
                            f'{PAD_OFFSET / C - PAD_OFFSET:.6f} m along the bent towards CL Beam.',
                 sources='sheet 42 (PDF 42) PLAN, 1\'-1 1/2" + 1\'-1 1/2" between CL Bearing Pad and CL Beam'),
            dict(id='end-diaphragm-width-and-fit', parts=[c['dia'] for c in END_BENTS.values()],
                 correction='Faces moved from n = +/-0.434823 to +/-0.457200 m (3\'-0", flush with the caps); '
                            'underside on the cap terraces (corners included); open pad layer under each beam; '
                            'refitted around the lowered beams, haunches and end blocks; approach-slab ledge cut.',
                 sources='sheet 58 (PDF 58) sections C-C and D-D; sheet 42 (PDF 42) keyway construction joint and '
                         'hatched 7/8 in preformed joint material limits'),
        ],
        kept_deviations=[],
        interfaces=interfaces, fixed_neighbour_overlaps_m3_before_after=fixed_checked,
        changed_parts=sorted(changed_ids), added_parts=[], removed_parts=[],
        before_glb_sha256=before, after_glb_sha256=hashlib.sha256(out).hexdigest(),
        before_manifest_sha256=hashlib.sha256(raw_manifest).hexdigest())
    record = manifest['review_correction_record_3']
    print(f'{len(changed_ids)} parts changed')
    if dry_run:
        print(json.dumps({k: v for k, v in record.items() if k != 'changed_parts'}, indent=1)[:6000])
        print('Dry run, nothing written.')
        return
    backup = ROOT / 'data/fem_research'
    backup.mkdir(exist_ok=True)
    (backup / f'{BID}_before_review_correction_3.glb').write_bytes(original)
    (backup / f'{BID}_manifest_before_review_correction_3.json').write_bytes(raw_manifest)
    path.write_bytes(out)
    text = json.dumps(manifest, ensure_ascii=False, indent=2) + '\n'
    if b'\r\n' in raw_manifest:                    # keep the file's existing CRLF line endings
        text = text.replace('\n', '\r\n')
    mp.write_bytes(text.encode('utf-8'))
    print(json.dumps({k: v for k, v in record.items() if k not in ('interfaces', 'fixed_neighbour_overlaps_m3_before_after')}))


if __name__ == '__main__':
    correct(dry_run='--dry-run' in sys.argv)

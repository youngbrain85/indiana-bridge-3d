"""Third drawing-confirmed correction of SR 1 over the Wabash River (sr1-wabash): the known deviations left by the
first two passes. Runs after correct_sr1_wabash_review.py and correct_sr1_wabash_review_2.py; it preserves
unrelated GLB buffers and appends new accessors, meshes and nodes.

    python scripts/correct_sr1_wabash_review.py      # first pass
    python scripts/correct_sr1_wabash_review_2.py    # second pass
    python scripts/correct_sr1_wabash_review_3.py    # this pass

Source: drawings.pdf (2004 B-25747 roadway reconstruction of the 1933 arches); printed sheets 6-15 are PDF pages
23-32, sheet 15-1 is PDF 33 and sheets 16-18 are PDF 34-36. Native axes as before: X along the centre line from the
Pier 3 centre line, +Y = west (left of increasing station), Z = El. - 240 m; the GLB stores (X, Z, -Y).

1. Curb unit, wall cut and fill top (known deviation `deck-soffit-in-fill-envelope`). Sheet 15 section A-A and the
   sheet 14 bracket elevations (revised 4-6-04): the sidewalk casting includes a curb unit that runs 779 mm from the
   curb face to the expansion joint against the roadway slab (|Y| 6.121; the roadway slab is 6271 + 5971 mm between
   the joints), is 230 mm deep at that joint and falls 165 mm more over the 585 mm to the spandrel inner face. The
   existing spandrel walls were cut down to 610 mm below the sidewalk soffit ("Cut, Clean and Straighten 600 of
   Exist. Reinf.") and the curb unit is cast on the cut top across the 381 mm wall; at the pier and abutment
   pilasters the cut is 838 mm below the soffit under the 610 mm bracket stem (sheet 14, bracket at pilasters). The
   "Existing Fill Material" lies directly under the new 300 mm slab. The 2004 sheets give the longitudinal "Expansion
   Joint Sealing System" but no width; the 2026 reference (sheet 15, note 4) records the existing deck joint opening
   as 0.5 in., which is used. The model had the roadway slab to the curb faces (|Y| 6.9), the curb unit only above
   the old wall-top envelope (old surface less 200 mm) and the fill and wall envelopes 51 mm into the slab soffit.
   Now: `deck` ends 6.35 mm short of the joint centre lines and `walk_*` start 6.35 mm beyond them (12.7 mm open
   joints); `walk_*` carry the drawn curb unit; the spandrel and end-floor walls and the spandrel pilasters are cut
   to the 610 mm level, the pilasters with a 610 mm wide seat at the 838 mm level under each bracket stem. Sheet 14
   also places the pilaster face 1421 mm inside the local coping (|Y| 7.315) with 610 mm of pilaster and wall to the
   spandrel inner face, so the pilaster envelopes (|Y| 6.880-7.360) now span 6.706-7.315, and the spandrel-wall ends
   are kept 13 mm from them across the whole wall thickness (sheet 18). The fill
   tops follow the slab soffit and the curb-unit soffit. Where the model's approximate arch ring rises above the cut
   level near the crowns (sheet 14 note "Where Bracket overlaps Arch Ring"), the walls end and the curb unit and
   brackets stop on the ring.
2. Sidewalk brackets (known deviation `sidewalk-brackets-not-modelled`). Sheets 11-12 plan-sections: in each span
   and on each side ten typical brackets, centres 305 mm from the pilaster faces and then 3 @ 2400, 3 @ 2388,
   3 @ 2400 (22 174 mm between pilaster faces); sheet 14 typical bracket: 300 mm wide, outer face 75 mm inside the
   coping, 203 mm deep there, 114 x 75 notch, R 1778 soffit over 966 mm, 114 mm flat, 75 mm step and 305 mm flat to
   the spandrel face at 610 mm below the sidewalk soffit. Sheet 14 bracket at abutment and pier pilasters, centred
   on the pilaster (sheet 11): 838 mm wide upper tier 203 mm deep from 75 mm inside the local coping, 610 mm wide
   stem (section 2-2) stepping in 191 mm, 203 mm, 114 x 75 notch, R 775 soffit over 622 mm, 114 mm flat, 75 mm step,
   flat to the spandrel inner face at 838 mm below the soffit. 80 typical and 10 pilaster brackets are added.
   The end brackets (sheet 14) and brackets B1-B3 (sheet 13) of the four floor-end zones stay out: beyond the P.C.
   lines the sidewalks, rails and end-floor walls flare (R 27 819 at Abutment 1, sheet 9; R 22 504 / 24 265 at
   Abutment 5, sheet 10), the bracket faces follow that curvature and the end brackets bear on the concrete end walls
   and gauge-well wall of sheet 15-1 under the wing-end pilasters of sheet 18; none of that end-zone geometry is
   modelled, so they stay a known deviation.
3. Sidewalk joints (known deviation `sidewalk-joints-not-modelled`). Sheet 18 elevation "13 Open Joint in Rail and
   Sidewalk (One side only at Abutment)" and plan-section: the joint is in line with the rail joint (13 mm on the
   span side of the pilaster face) up to the rail face line 75 mm inside the coping, then runs at 45 degrees across
   the 75 mm coping band to the end of the 75 mm local coping projection, which forms the projection's plan
   chamfer; the opening is 13 mm normal to its faces on both legs. Sheet 9: the "Curb & Sidewalk Reinf." of each span panel stops 87 mm (top) / 137 mm (bottom) short of the
   pilaster face and the pilaster panel has its own bars from 133 / 83 mm inside it, so the joint is taken through
   the whole curb unit to the roadway expansion joint. Each sidewalk becomes nine bodies (one part id).

Every stored mesh is checked as scripts/refresh_geometry_verification.py does: each index-connected body, welded at
10 um, must be a watertight solid with positive volume.

Requires numpy, trimesh, manifold3d and the two earlier scripts (imported for their geometry helpers).
"""
import hashlib
import json
import struct
import sys
from pathlib import Path

import manifold3d
import numpy as np
import trimesh

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import correct_sr1_wabash_review as r1  # noqa: E402
import correct_sr1_wabash_review_2 as r2  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'data/bridges/sr1-wabash'
BACKUP = ROOT / 'data/fem_research'
TAG = 'review-3-2026-11-curb-unit-wall-cut-brackets-sidewalk-joints'
REVISION_BEFORE, REVISION = r2.REVISION, '1.3-deviations'
GLB_BEFORE = 'a8de7b12edb2dcc7fe63f4a4a5252fb8a7fbcd0773afae5aa97dddb7b4ebd730'

T15 = r1.T15
U = np.array([1.0, T15, 0.0])
CURB_Y, SPANDREL_Y, COPING_Y = r1.CURB_Y, r1.SPANDREL_Y, r1.COPING_Y   # 6.900 / 7.087 / 8.661
LOCAL_COPING_Y = r2.LOCAL_COPING_Y                                    # 8.736
JOINT_Y = CURB_Y - 0.779          # 6.121: centre line of the expansion joint curb unit / roadway slab (sheets 14, 15)
JOINT_OPEN = 0.0127               # 0.5 in. existing opening (2026 reference sheet 15, note 4)
DECK_EDGE_Y = JOINT_Y - JOINT_OPEN / 2    # 6.11465
CURB_IN_Y = JOINT_Y + JOINT_OPEN / 2      # 6.12735
INNER_Y = SPANDREL_Y - 0.381      # 6.706: spandrel inner face (sheet 15)
PIL_FACE_Y = LOCAL_COPING_Y - 1.421   # 7.315: spandrel pilaster face, 1421 mm inside the local coping (sheet 14)
CURB_JOINT_DEPTH, CURB_SLOPE_DROP = 0.230, 0.165                      # sheets 14, 15
WALL_CUT, PILASTER_CUT = 0.610, 0.838                                 # below the sidewalk soffit (sheets 14, 15)
JOINT, RAIL_LINE, CHAMFER = r2.JOINT, COPING_Y - 0.075, 0.075          # 13 mm; 8.586; 75 x 75 (sheet 18)
# Typical bracket (sheet 14): (inset from the coping, depth below the soffit at the outer face ...), metres.
BRACKET_W, BRACKET_R = 0.300, 1.778
BRACKET_OUT = COPING_Y - 0.075    # 8.586
SPACING = [0.0, 2.400, 2.400, 2.400, 2.388, 2.388, 2.388, 2.400, 2.400, 2.400]   # sheets 11-12, after 305 mm
FIRST_CENTRE = 0.305
# Bracket at pier and abutment pilasters (sheet 14).
PIL_FLANGE_W, PIL_STEM_W, PIL_R = 0.838, 0.610, 0.775
PIL_OUT = LOCAL_COPING_Y - 0.075  # 8.661
SUPPORT_NAMES = ['Abutment 1', 'Pier 2', 'Pier 3', 'Pier 4', 'Abutment 5']
SIDEWALK_COLOR = '#c9c8b8'
SOURCE_PAGES = [24, 26, 27, 28, 29, 30, 31, 32, 33, 36]   # PDF 33 = sheet 15-1
PRINTED_SHEETS = [7, 9, 10, 11, 12, 13, 14, 15, 18]


# ---- profiles ---------------------------------------------------------------------------------------------------
def soffit(x, r):
    """Sidewalk slab soffit at |Y| = r (190 mm under the 2 % sidewalk top, first pass)."""
    return r1.walk_top(x, r) - r1.WALK_SLAB


def wall_cut(x):
    """Cut top of the spandrel and end-floor walls = curb-unit soffit over the wall: 610 below the sidewalk soffit
    at the spandrel face."""
    return soffit(x, SPANDREL_Y) - WALL_CUT


def pilaster_cut(x):
    """Cut top of the spandrel pilasters = soffit of the pilaster brackets: 838 below the sidewalk soffit."""
    return soffit(x, SPANDREL_Y) - PILASTER_CUT


def gutter(x, r):
    """Roadway / gutter top at |Y| = r: 2 % crossfall from the centre line (first pass)."""
    return r1.grade(x) - 0.02 * r


def curb_soffit(x, r):
    """Curb-unit soffit between the expansion joint and the spandrel inner face: 230 below the gutter at the joint,
    falling 165 more over the 585 to the wall (sheets 14, 15)."""
    return gutter(x, JOINT_Y) - CURB_JOINT_DEPTH - CURB_SLOPE_DROP * (r - JOINT_Y) / (INNER_Y - JOINT_Y)


def arc(p, q, radius, n=16):
    """Points after p up to q on the circle of `radius` through both, centre on the lower (air) side."""
    (ra, za), (rb, zb) = p, q
    dr, dz = rb - ra, zb - za
    chord = np.hypot(dr, dz)
    h = np.sqrt(radius ** 2 - (chord / 2) ** 2)
    nr, nz = -dz / chord, dr / chord
    if nz > 0:
        nr, nz = -nr, -nz
    cr, cz = (ra + rb) / 2 + h * nr, (za + zb) / 2 + h * nz
    a0, a1 = np.arctan2(za - cz, ra - cr), np.arctan2(zb - cz, rb - cr)
    return [(cr + radius * np.cos(t), cz + radius * np.sin(t)) for t in np.linspace(a0, a1, n + 1)[1:]]


def walk_profile(x):
    """Sidewalk casting at station x as (|Y|, Z): curb unit from the expansion joint, curb, 2 % sidewalk, 190 mm
    fascia, soffit back to the spandrel face, down to the wall cut, across the wall, curb-unit soffit to the joint."""
    c = wall_cut(x)
    return [(CURB_IN_Y, gutter(x, CURB_IN_Y)), (CURB_Y, gutter(x, CURB_Y)), (CURB_Y, r1.walk_top(x, CURB_Y)),
            (COPING_Y, r1.walk_top(x, COPING_Y)), (COPING_Y, soffit(x, COPING_Y)),
            (SPANDREL_Y, soffit(x, SPANDREL_Y)), (SPANDREL_Y, c), (INNER_Y, c), (INNER_Y, curb_soffit(x, INNER_Y)),
            (CURB_IN_Y, curb_soffit(x, CURB_IN_Y))]


def bracket_profile(x):
    """Typical bracket in spans A-D (sheet 14), from the spandrel face out to 75 mm inside the coping."""
    top = soffit(x, BRACKET_OUT)
    bottom = wall_cut(x)
    p = (BRACKET_OUT - 0.114, top - 0.203 - 0.075)
    q = (BRACKET_OUT - 0.114 - 0.966, bottom + 0.075)
    return ([(SPANDREL_Y, soffit(x, SPANDREL_Y)), (BRACKET_OUT, top), (BRACKET_OUT, top - 0.203),
             (BRACKET_OUT - 0.114, top - 0.203), p] + arc(p, q, BRACKET_R, 32) +
            [(q[0] - 0.114, bottom + 0.075), (q[0] - 0.114, bottom), (SPANDREL_Y, bottom)])


def pilaster_stem_profile(x):
    """Bracket at pier and abutment pilasters (sheet 14), 610 mm stem: from 75 mm inside the local coping to the
    spandrel inner face, bottom 838 mm below the soffit across the pilaster and wall, under the curb unit."""
    top = soffit(x, PIL_OUT)
    bottom, cut = pilaster_cut(x), wall_cut(x)
    p = (PIL_OUT - 0.191 - 0.114, top - 0.203 - 0.203 - 0.075)
    q = (p[0] - 0.622, bottom + 0.075)
    return ([(SPANDREL_Y, soffit(x, SPANDREL_Y)), (PIL_OUT, top), (PIL_OUT, top - 0.203),
             (PIL_OUT - 0.191, top - 0.203), (PIL_OUT - 0.191, top - 0.406), (PIL_OUT - 0.305, top - 0.406), p] +
            arc(p, q, PIL_R, 24) +
            [(q[0] - 0.114, bottom + 0.075), (q[0] - 0.114, bottom), (INNER_Y, bottom), (INNER_Y, cut),
             (SPANDREL_Y, cut)])


def pilaster_flange_profile(x):
    """838 mm upper tier of the pilaster bracket: the first 203 mm below the soffit (sheet 14 elevation, section 2-2)."""
    top = soffit(x, PIL_OUT)
    return [(SPANDREL_Y, soffit(x, SPANDREL_Y)), (PIL_OUT, top), (PIL_OUT, top - 0.203), (SPANDREL_Y, top - 0.203)]


# ---- solids -----------------------------------------------------------------------------------------------------
def refresh_bodies_ok(mesh):
    """The check of scripts/refresh_geometry_verification.py: each index-connected body, welded at 10 um, is a
    watertight solid with positive volume."""
    v = r1.to_native(r1.to_gltf(mesh.vertices).astype('<f4').astype(np.float64))
    f = np.asarray(mesh.faces)
    parent = np.arange(len(v))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    for a, b, c in f:
        ra = find(a)
        parent[find(b)] = ra
        parent[find(c)] = ra
    roots = np.array([find(i) for i in f[:, 0]])
    for root in np.unique(roots):
        body = trimesh.Trimesh(v, f[roots == root], process=False)
        body.remove_unreferenced_vertices()
        body.merge_vertices(digits_vertex=5)
        if not (body.is_watertight and body.volume > 0):
            return False
    return True


def mf(mesh):
    return r2.mf(mesh)


def to_trimesh(manifold):
    if manifold.status() != manifold3d.Error.NoError:
        raise ValueError(f'boolean failed: {manifold.status()}')
    m = manifold.to_mesh64()
    v = np.asarray(m.vert_properties)[:, :3].astype(np.float32).astype(np.float64)
    mesh = trimesh.Trimesh(vertices=v, faces=np.asarray(m.tri_verts).astype(np.int64), process=False)
    if not (mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0):
        raise ValueError('boolean produced an invalid solid')
    return mesh


def boolean(base, add=(), sub=()):
    out = mf(base)
    for a in add:
        out = out + mf(a)
    for s in sub:
        out = out - mf(s)
    return to_trimesh(out)


def bodies(mesh):
    return len(mf(mesh).decompose())


def side_loft(xs, profile, s):
    return r1.loft(xs, lambda x: [(s * r, z) for r, z in profile(x)])


def span_stations(a, b, xs_walk):
    """a, b and the walk-loft stations between them, so that touching surfaces share their stations."""
    return np.unique(np.r_[a, xs_walk[(xs_walk > a) & (xs_walk < b)], b])


def level_cutter(level, x0, x1, y0, y1, xs_inside):
    """Solid above Z = level(x) over x0..x1, y0..y1, through the given stations (so it matches the walk loft)."""
    xs = np.unique(np.r_[x0, [x for x in xs_inside if x0 < x < x1], x1])
    return r1.loft(xs, lambda x: [(y0, level(x)), (y1, level(x)), (y1, 12.0), (y0, 12.0)])


def fill_cutter(x0, x1, xs_inside):
    """Solid above the slab soffit (to the slab edge) and the curb-unit soffit (beyond), across both sides; under
    the open expansion joint the fill stops at the curb-unit soffit line."""
    xs = np.unique(np.r_[x0, [x for x in xs_inside if x0 < x < x1], x1])
    y2 = CURB_Y

    def loop(x):
        g = r1.grade(x)
        ds = lambda r: g - 0.02 * r - r1.DECK_SLAB
        e = DECK_EDGE_Y
        return [(-y2, curb_soffit(x, y2)), (-e, curb_soffit(x, e)), (-e, ds(e)), (0.0, ds(0.0)),
                (e, ds(e)), (e, curb_soffit(x, e)), (y2, curb_soffit(x, y2)), (y2, 12.0),
                (-y2, 12.0)]
    return r1.loft(xs, loop)


def joint_cutter(face, d, s):
    """13 mm open joint on the span side (d = +1 toward increasing X) of the pilaster face X = face: square to the
    centre line up to the rail face line, then 45 degrees across the 75 mm coping band to the end of the 75 mm local
    coping projection (sheet 18 plan-section), 13 mm wide normal to its faces throughout (13 * sqrt 2 along X on the
    45-degree leg)."""
    diag = JOINT * np.sqrt(2.0)
    rs = [(0.0, 6.0), (JOINT, 6.0), (JOINT, RAIL_LINE - (diag - JOINT)), (CHAMFER + diag, COPING_Y),
          (CHAMFER, COPING_Y), (0.0, RAIL_LINE)]
    pts = np.array([(face + d * a, s * r) for a, r in rs], dtype=np.float64)
    return plan_prism(pts, 6.0, 11.0)


def plan_prism(pts, z0, z1):
    """Vertical prism over the simple plan polygon pts [(x, y)], built directly so the corners keep their exact
    float64 positions (manifold's CrossSection rounds them to 1e-8 m, which left 2e-8 m slivers against the coping
    projection ends)."""
    area = np.sum(pts[:, 0] * np.roll(pts[:, 1], -1) - np.roll(pts[:, 0], -1) * pts[:, 1])
    if area < 0:
        pts = pts[::-1]
    k = len(pts)
    vertices = np.r_[np.c_[pts, np.full(k, z0)], np.c_[pts, np.full(k, z1)]]
    tri = np.asarray(manifold3d.triangulate([pts]))
    sides = [(i, (i + 1) % k, k + (i + 1) % k) for i in range(k)] + [(i, k + (i + 1) % k, k + i) for i in range(k)]
    mesh = trimesh.Trimesh(vertices=vertices, faces=np.r_[tri[:, ::-1], tri + k, np.array(sides)], process=False)
    if not (mesh.is_watertight and mesh.is_winding_consistent):
        raise ValueError('invalid plan prism')
    if mesh.volume < 0:
        mesh.invert()
    return mesh


def correct(base=BASE, backup=BACKUP):
    mp = base / 'model_manifest.json'
    manifest = json.loads(mp.read_text(encoding='utf-8'))
    if manifest.get('review_correction_3') == TAG:
        print('Already corrected.')
        return
    if (manifest.get('review_correction') != r1.TAG or manifest.get('review_correction_2') != r2.TAG
            or manifest.get('revision') != REVISION_BEFORE):
        raise ValueError('Run the first two correction scripts first: expected revision 1.2-drawing-review-2.')
    path = base / 'model.glb'
    original = path.read_bytes()
    before = hashlib.sha256(original).hexdigest()
    if before != GLB_BEFORE:
        raise ValueError(f'Unexpected model.glb (SHA-256 {before}); expected the revision 1.2 model.')
    manifest_before = hashlib.sha256(mp.read_bytes()).hexdigest()
    length = struct.unpack_from('<I', original, 12)[0]
    gltf = json.loads(original[20:20 + length])
    binary = bytearray(original[28 + length:])
    parts = {p['id']: p for p in manifest['parts']}
    meshes = {m['name']: m for m in gltf['meshes']}
    if any('matrix' in n or 'rotation' in n for n in gltf['nodes']):
        raise ValueError('Unexpected node transforms: this script expects baked Y-up vertices.')
    known = {d['id'] for d in manifest.get('known_deviations', [])}
    if not {'sidewalk-brackets-not-modelled', 'deck-soffit-in-fill-envelope', 'sidewalk-joints-not-modelled'} <= known:
        raise ValueError('Expected the three known deviations of revision 1.2.')

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
        return trimesh.Trimesh(vertices=r1.to_native(read(prim['attributes']['POSITION']).astype(np.float64)),
                               faces=read(prim['indices']).reshape(-1, 3), process=False)

    def check(mesh, pid):
        if not (mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0 and refresh_bodies_ok(mesh)):
            raise ValueError(f'{pid}: not a valid solid')

    changed, added = [], []

    def store(pid, mesh, dims, note, pages, drop_extras=()):
        check(mesh, pid)
        prim = meshes[pid]['primitives'][0]
        old_faces = read(prim['indices']).reshape(-1, 3)
        attributes = {'POSITION': append(r1.to_gltf(mesh.vertices).astype('<f4'), 'VEC3', 5126)}
        if len(mesh.faces) == len(old_faces) and np.array_equal(mesh.faces, old_faces):
            attributes['COLOR_0'] = prim['attributes']['COLOR_0']
        else:
            color = read(prim['attributes']['COLOR_0'])[0]
            attributes['COLOR_0'] = append(np.tile(color, (len(mesh.vertices), 1)).astype('u1'), 'VEC4', 5121)
            gltf['accessors'][attributes['COLOR_0']]['normalized'] = True
            prim['indices'] = append(mesh.faces.reshape(-1, 1).astype('<u4'), 'SCALAR', 5125)
        prim['attributes'] = attributes
        p = parts[pid]
        p['bounds_m'] = mesh.bounds.round(6).tolist()
        p['volume_m3'] = round(float(mesh.volume), 6)
        p['dimensions'].update(dims)
        p['note'] = (p.get('note', '') + ' ' + note).strip()
        p['pdf_pages'] = sorted(set(p['pdf_pages']) | set(pages))
        extras = meshes[pid]['extras']
        for key in drop_extras:
            extras.pop(key, None)
        extras.update(p)
        changed.append(pid)

    def add(pid, name, mesh, basis, note, pages, dims):
        if pid in parts or pid in meshes:
            raise ValueError(f'{pid}: id already used')
        check(mesh, pid)
        color = [int(SIDEWALK_COLOR[j:j + 2], 16) for j in (1, 3, 5)] + [255]
        prim = dict(attributes=dict(POSITION=append(r1.to_gltf(mesh.vertices).astype('<f4'), 'VEC3', 5126),
                                    COLOR_0=append(np.tile(color, (len(mesh.vertices), 1)).astype('u1'), 'VEC4', 5121)),
                    indices=append(mesh.faces.reshape(-1, 1).astype('<u4'), 'SCALAR', 5125), mode=4)
        gltf['accessors'][prim['attributes']['COLOR_0']]['normalized'] = True
        p = dict(id=pid, name=name, layer='sidewalks', color=SIDEWALK_COLOR, pdf_pages=sorted(pages), basis=basis,
                 note=note, dimensions=dims, bounds_m=mesh.bounds.round(6).tolist(),
                 volume_m3=round(float(mesh.volume), 6))
        gltf['meshes'].append(dict(name=pid, extras=dict(p), primitives=[prim]))
        gltf['nodes'].append(dict(name=pid, mesh=len(gltf['meshes']) - 1))
        gltf['nodes'][0]['children'].append(len(gltf['nodes']) - 1)
        manifest['parts'].append(p)
        parts[pid] = p
        meshes[pid] = gltf['meshes'][-1]
        added.append(pid)

    M = {pid: native(pid) for pid in meshes}
    arches = [M[f'arch_{i}'] for i in range(4)]

    # ---- Expected starting state (second pass applied, nothing else) ------------------------------------------
    deck = M['deck']
    if not np.allclose(np.abs(deck.bounds[:, 1]), CURB_Y, atol=1e-5):
        raise ValueError('deck: expected the roadway slab out to the curb faces')
    for s in (1, -1):
        b = M[f'walk_{s}'].bounds
        if not (np.isclose(np.abs(b[:, 1]).min(), CURB_Y, atol=1e-5) and np.isclose(b[0, 2], 8.48726, atol=1e-4)
                and np.isclose(np.abs(b[:, 1]).max(), LOCAL_COPING_Y, atol=1e-5) and bodies(M[f'walk_{s}']) == 1):
            raise ValueError(f'walk_{s}: unexpected second-pass sidewalk')
    for pid in [f'spandrel_{i}_{s}' for i in range(4) for s in (-1, 1)] + [f'fill_{i}' for i in range(4)]:
        if not np.isclose(M[pid].bounds[1, 2], 8.49488, atol=1e-4):
            raise ValueError(f'{pid}: unexpected top envelope')
    for i in range(5):
        for s in (-1, 1):
            if not np.isclose(M[f'pilaster_{i}_{s}'].bounds[1, 2], 8.5, atol=1e-6) or len(M[f'pilaster_{i}_{s}'].vertices) != 8:
                raise ValueError(f'pilaster_{i}_{s}: unexpected top')
    if any(pid.startswith(('bracket_', 'pilbracket_')) for pid in parts):
        raise ValueError('brackets already present')

    xs_walk = r1.stations(r1.X0, r1.X1)
    sides = {1: 'west', -1: 'east'}
    faces = {s: [(r1.post_x(i, s) - r1.POST_HALF, r1.post_x(i, s) + r1.POST_HALF) for i in range(5)] for s in (1, -1)}

    # ---- 1. Roadway slab between the expansion joints -------------------------------------------------------
    def deck_loop(x):
        g = r1.grade(x)
        e = DECK_EDGE_Y
        return [(-e, g - 0.02 * e), (0.0, g), (e, g - 0.02 * e), (e, g - 0.02 * e - r1.DECK_SLAB),
                (0.0, g - r1.DECK_SLAB), (-e, g - 0.02 * e - r1.DECK_SLAB)]
    store('deck', r1.loft(xs_walk, deck_loop),
          dict(width_m=round(2 * DECK_EDGE_Y, 4), edge_abs_y_m=round(DECK_EDGE_Y, 5), clear_roadway_m=13.8,
               expansion_joint_centre_abs_y_m=round(JOINT_Y, 3), expansion_joint_opening_m=JOINT_OPEN),
          'Third drawing review 2026-11: the 300 mm slab ends at the longitudinal expansion joints against the curb '
          'units, whose centre lines are 779 mm inside the curb faces (|Y| 6.121; 6271 + 5971 mm, sheet 15 section '
          'A-A); the joints are left open 12.7 mm (0.5 in. existing opening, 2026 reference sheet 15 note 4; the 2004 '
          'sheets give the sealing system but no width), so the slab edges are at |Y| 6.1147. The 779 mm gutter '
          'strips belong to the sidewalk casting (walk_*). Clear roadway between curb faces still 13.8 m. Sealing '
          'system not modelled.',
          [31, 32])

    # ---- 1, 3. Sidewalk casting: curb unit, coping projections, joints ---------------------------------------
    for s in (1, -1):
        base_walk = side_loft(xs_walk, walk_profile, s)
        blocks = []
        for i in range(5):
            cx = r1.post_x(i, s)
            a, b = cx - r1.POST_HALF - r2.COPING_RUN, cx + r1.POST_HALF + r2.COPING_RUN
            st = np.unique(np.r_[a, xs_walk[(xs_walk > a) & (xs_walk < b)], b])

            def loop(x):
                # interpolate between the walk stations so the projection top is coplanar with the loft facets
                zt = float(np.interp(x, xs_walk, r1.walk_top(xs_walk, COPING_Y)))
                rise = 0.02 * (LOCAL_COPING_Y - COPING_Y)
                return [(s * COPING_Y, zt), (s * LOCAL_COPING_Y, zt + rise),
                        (s * LOCAL_COPING_Y, zt + rise - r1.WALK_SLAB), (s * COPING_Y, zt - r1.WALK_SLAB)]
            blocks.append(r1.loft(st, loop))
        cuts = []
        for i, (fl, fr) in enumerate(faces[s]):
            if i > 0:
                cuts.append(joint_cutter(fl, -1, s))
            if i < 4:
                cuts.append(joint_cutter(fr, 1, s))
        walk = boolean(base_walk, add=blocks, sub=cuts + arches)
        n = bodies(walk)
        if n != 9:
            raise ValueError(f'walk_{s}: expected nine bodies between the joints, got {n}')
        store(f'walk_{s}', walk,
              dict(curb_unit_from_abs_y_m=round(CURB_IN_Y, 5), curb_unit_depth_at_joint_m=CURB_JOINT_DEPTH,
                   wall_cut_below_soffit_m=WALL_CUT, open_joint_m=JOINT, bodies_between_joints=n),
              f'Third drawing review 2026-11: sidewalk casting with the curb unit of sheets 14-15 (779 mm gutter strip '
              f'from the expansion joint centred at |Y| 6.121, face 6.35 mm beyond it at the 12.7 mm opening, 230 mm '
              f'deep there, soffit falling 165 mm to the spandrel inner '
              f'face, then on the wall cut 610 mm below the sidewalk soffit across the 381 mm wall); 13 mm open joints '
              f'in line with the rail joints at both pier pilaster faces and the span side of the abutment '
              f'pilasters, square to the centre line up to the rail face line and at 45 degrees across the 75 mm '
              f'coping band, forming the plan chamfers of the local coping projections (sheet 18 elevation and '
              f'plan-section; sheet 9 curb and sidewalk bars stop short of each joint), so the {sides[s]} sidewalk is '
              f'nine bodies; stops on the approximate arch ring where it rises above the wall cut near the crowns '
              f'(sheet 14 note). Plan flare and curb rounding are not modelled.',
              [26, 27, 31, 32, 36])
        parts[f'walk_{s}']['basis'] = ('Dimensioned curb unit, curb, sidewalk slope, fascia, coping projections and open '
                                       'joints, sheets 9, 14, 15 and 18; brackets are separate parts; end flare '
                                       'omitted')
        meshes[f'walk_{s}']['extras']['basis'] = parts[f'walk_{s}']['basis']

    # ---- 1. Wall cut, pilaster cut, fill top ------------------------------------------------------------------
    for s in (-1, 1):
        y0, y1 = sorted((s * 6.0, s * 7.6))
        for i in range(4):
            pid = f'spandrel_{i}_{s}'
            wall = M[pid]
            cutter = level_cutter(wall_cut, wall.bounds[0, 0] - 0.5, wall.bounds[1, 0] + 0.5, y0, y1, xs_walk)
            # The pilasters now reach the spandrel inner face (|Y| 6.706), so the skew wall-end corners that the
            # second pass left inside the joint line at the inner face (6.6 mm from the pilaster) are trimmed to
            # the 13 mm joint (sheet 18).
            def joint_x(target):
                """The second-pass joint line as stored (float32) in the wall, so the trim is exactly coplanar."""
                near = wall.vertices[np.abs(wall.vertices[:, 0] - target) < 2e-5, 0]
                if len(near) and np.ptp(near) > 1e-9:
                    raise ValueError(f'{pid}: ragged joint line')
                return float(near[0]) if len(near) else target
            joints = [r1.block(joint_x(M[f'pilaster_{j}_{s}'].bounds[0, 0] - JOINT),
                               joint_x(M[f'pilaster_{j}_{s}'].bounds[1, 0] + JOINT), y0, y1, 3.0, 9.0)
                      for j in (i, i + 1)]
            # The second pass left its triangular closure prisms as separate bodies touching the wall; cut each body
            # on its own and keep them index-disjoint, so coincident faces are not fused into slivers.
            pieces = []
            for body in mf(wall).decompose():
                out = body - mf(cutter)
                for j in joints:
                    out = out - mf(j)
                if not out.is_empty():
                    pieces.append(to_trimesh(out))
            new = trimesh.util.concatenate(pieces)
            store(pid, new, dict(top_cut_below_sidewalk_soffit_m=WALL_CUT),
                  'Third drawing review 2026-11: top cut to the 2004 wall cut, 610 mm below the sidewalk soffit at '
                  'the spandrel face (sheets 14, 15; was the old surface less 200 mm, 0.27 m higher); where the '
                  'approximate arch ring rises above the cut near the crown the wall ends, so the wall is now in two '
                  'pieces either side of the crown. Wall ends kept 13 mm from the spandrel pilasters across the whole '
                  'wall thickness now that the pilasters reach the inner face (sheet 18).', [31, 32, 36])
        for end in (-1, 1):
            pid = f'endwall_{end}_{s}'
            wall = M[pid]
            cutter = level_cutter(wall_cut, wall.bounds[0, 0] - 0.5, wall.bounds[1, 0] + 0.5, y0, y1, xs_walk)
            store(pid, boolean(wall, sub=[cutter]), dict(top_cut_below_sidewalk_soffit_m=WALL_CUT),
                  'Third drawing review 2026-11: top cut to the 2004 wall cut 610 mm below the sidewalk soffit (sheets '
                  '13-15), under the curb unit; the sheet 15-1 concrete end walls and end brackets are not modelled.',
                  [30, 31, 32], drop_extras=('shape', 'extents'))
        for i in range(5):
            pid = f'pilaster_{i}_{s}'
            m = M[pid]
            cx = r1.post_x(i, s)
            v = m.vertices.copy()
            top = np.isclose(v[:, 2], m.bounds[1, 2], atol=1e-6)
            if top.sum() != 4 or not (m.bounds[0, 0] < cx - PIL_STEM_W / 2 and cx + PIL_STEM_W / 2 < m.bounds[1, 0]):
                raise ValueError(f'{pid}: unexpected envelope')
            if not np.allclose(sorted(np.unique(np.round(np.abs(v[:, 1]), 6))), [6.88, 7.36], atol=1e-6):
                raise ValueError(f'{pid}: unexpected transverse envelope')
            # Sheet 14 (bracket at pilasters): the pilaster face is 1421 mm inside the local coping (|Y| 7.315) and
            # the cut pilaster and wall under the bracket run 610 mm from it to the spandrel inner face (|Y| 6.706).
            # The envelope stood at 6.880-7.360. Its lower part keeps 6.880 inside the pier; the inner strip is added
            # from the pier / abutment top up, so the existing embedment in the support is unchanged.
            x0, x1 = m.bounds[:, 0]
            z0, ztop, support_top = m.bounds[0, 2], wall_cut(cx), M[f'pier_{i}'].bounds[1, 2]
            body = r1.block(x0, x1, s * 6.88, s * PIL_FACE_Y, z0, ztop)
            inner = r1.block(x0, x1, s * INNER_Y, s * 6.88, support_top, ztop)
            seat = r1.block(cx - PIL_STEM_W / 2, cx + PIL_STEM_W / 2, s * 6.6, s * 7.45, pilaster_cut(cx), ztop + 0.5)
            new = boolean(body, add=[inner], sub=[seat])
            store(pid, new, dict(top_cut_below_sidewalk_soffit_m=WALL_CUT, seat_below_sidewalk_soffit_m=PILASTER_CUT,
                                 seat_width_m=PIL_STEM_W, abs_y_m=[INNER_Y, PIL_FACE_Y]),
                  'Third drawing review 2026-11: transverse extent from the spandrel inner face to the pilaster face, '
                  '|Y| 6.706-7.315 (sheet 14: 1421 mm inside the local coping, 610 mm across pilaster and wall; was '
                  '6.880-7.360); top cut to the general wall cut 610 mm below the sidewalk soffit, under the curb unit '
                  'like the spandrel walls (sheets 14, 15), with a 610 mm wide seat 838 mm below the soffit under the '
                  'stem of the pilaster bracket (sheet 14, bracket at abutment and pier pilasters); the cut beside the '
                  'bracket is not drawn (known deviation).', [31, 32],
                  drop_extras=('shape', 'extents'))
    for i in range(4):
        pid = f'fill_{i}'
        fill = M[pid]
        # The old envelope top is flat at the old surface less 200 mm at |Y| 6.706 (El. 248.495): up to 51 mm into
        # the slab near the curbs but 83 mm under it at the centre line. Extend it up over its own skew footprint
        # (above the arch crown) and cut it to the slab and curb-unit soffits.
        u = fill.vertices @ U
        ua, ub = u.min(), u.max()
        foot = np.array([(ua + T15 * INNER_Y, -INNER_Y), (ub + T15 * INNER_Y, -INNER_Y),
                         (ub - T15 * INNER_Y, INNER_Y), (ua - T15 * INNER_Y, INNER_Y)])
        top_old = fill.bounds[1, 2]
        if not (np.isclose(np.abs(fill.vertices[:, 1]).max(), INNER_Y, atol=1e-5)
                and M[f'arch_{i}'].bounds[1, 2] < top_old - 0.04):
            raise ValueError(f'{pid}: unexpected envelope')
        upper = to_trimesh(manifold3d.Manifold.extrude(manifold3d.CrossSection([foot]), 9.2 - (top_old - 0.03))
                           .translate([0.0, 0.0, top_old - 0.03]))
        new = boolean(fill, add=[upper],
                      sub=[fill_cutter(fill.bounds[0, 0] - 0.5, fill.bounds[1, 0] + 0.5, xs_walk)])
        store(pid, new, dict(top='slab soffit, curb-unit soffit beyond the expansion joints'),
              'Third drawing review 2026-11: top set to the 300 mm slab soffit and, beyond the expansion joints, to '
              'the curb-unit soffit ("Existing Fill Material" directly under the new slab, sheets 7, 14, 15); the old '
              'flat top at El. 248.495 ran up to 51 mm into the slab near the curbs and stood 83 mm under it at the '
              'centre line.', [24, 31, 32])

    # ---- 2. Brackets ------------------------------------------------------------------------------------------
    for s in (-1, 1):
        for i in range(4):
            left, right = faces[s][i][1], faces[s][i + 1][0]
            centres = left + FIRST_CENTRE + np.cumsum(SPACING)
            if not np.isclose(right - centres[-1], FIRST_CENTRE, atol=2e-3):
                raise ValueError('bracket chain does not close')
            for k, cx in enumerate(centres):
                solid = side_loft(span_stations(cx - BRACKET_W / 2, cx + BRACKET_W / 2, xs_walk), bracket_profile, s)
                solid = boolean(solid, sub=[arches[i]])
                add(f'bracket_{i}_{s}_{k}', f'Span {chr(65 + i)} | sidewalk bracket {s}, no. {k + 1}', solid,
                    'Dimensioned sheet-14 typical bracket at the sheet 11-12 spacing',
                    f'Third drawing review 2026-11: typical concrete bracket under the {sides[s]} sidewalk (sheet 14), '
                    f'300 mm wide, centred {round(cx - left, 3)} m from the span-side pilaster face (sheets 11-12: 305, '
                    f'3 @ 2400, 3 @ 2388, 3 @ 2400); from the spandrel face to 75 mm inside the coping, 203 mm deep '
                    f'at the outer face, 114 x 75 notch, R 1778 soffit, 114 mm flat, 75 mm step, 305 mm flat at 610 '
                    f'mm below the sidewalk soffit. Its tail over the counterfort is part of the curb unit (walk_*). '
                    f'Doweling and reinforcement not modelled.',
                    [28, 29, 31, 32],
                    dict(width_m=BRACKET_W, center_x_m=round(float(cx), 4), projection_from_spandrel_face_m=1.499,
                         depth_at_outer_face_m=0.203, depth_at_wall_below_soffit_m=WALL_CUT,
                         soffit_radius_m=BRACKET_R))
        for i in range(5):
            cx = r1.post_x(i, s)
            stem = side_loft(span_stations(cx - PIL_STEM_W / 2, cx + PIL_STEM_W / 2, xs_walk), pilaster_stem_profile, s)
            flange = side_loft(span_stations(cx - PIL_FLANGE_W / 2, cx + PIL_FLANGE_W / 2, xs_walk),
                               pilaster_flange_profile, s)
            solid = boolean(stem, add=[flange], sub=arches)
            add(f'pilbracket_{i}_{s}', f'{SUPPORT_NAMES[i]} | pilaster sidewalk bracket {s}', solid,
                'Dimensioned sheet-14 bracket at abutment and pier pilasters, centred on the pilaster (sheet 11)',
                f'Third drawing review 2026-11: concrete bracket under the local coping at the {SUPPORT_NAMES[i]} rail '
                f'pilaster, {sides[s]} side (sheet 14): 838 mm wide upper tier 203 mm deep from 75 mm inside the local '
                f'coping, 610 mm stem stepping in 191 mm and 203 mm deeper, 114 x 75 notch, R 775 soffit over 622 mm, '
                f'114 mm flat, 75 mm step, flat at 838 mm below the sidewalk soffit across the pilaster and the wall '
                f'to the spandrel inner face, under the curb unit. Centred on the support line at the arch-ring face '
                f'(sheet 11). Doweling and reinforcement not modelled.',
                [28, 29, 31, 36],
                dict(stem_width_m=PIL_STEM_W, upper_tier_width_m=PIL_FLANGE_W, center_x_m=round(float(cx), 4),
                     depth_at_wall_below_soffit_m=PILASTER_CUT, soffit_radius_m=PIL_R))

    # ---- Write ------------------------------------------------------------------------------------------------
    while len(binary) % 4:
        binary.append(0)
    gltf['buffers'][0]['byteLength'] = len(binary)
    encoded = json.dumps(gltf, ensure_ascii=True, separators=(',', ':')).encode()
    encoded += b' ' * ((-len(encoded)) % 4)
    out = (struct.pack('<III', 0x46546c67, 2, 28 + len(encoded) + len(binary)) +
           struct.pack('<II', len(encoded), 0x4e4f534a) + encoded + struct.pack('<II', len(binary), 0x004e4942) + binary)
    backup.mkdir(parents=True, exist_ok=True)
    (backup / 'sr1-wabash_before_review_correction_3.glb').write_bytes(original)
    (backup / 'sr1-wabash_manifest_before_review_correction_3.json').write_bytes(mp.read_bytes())
    path.write_bytes(out)

    bracket_ids = [p for p in added]
    for item in manifest.get('detail_coverage', []):
        if item.get('feature') == '2004 deck and sidewalks':
            item['detail'] = ('12.229 m roadway slab, 300 mm (top at original P.G. + 49 mm, 2 % crossfall, 30.48 m '
                              'vertical curve at the Abutment 1 end) between the 12.7 mm longitudinal expansion '
                              'joints; sidewalk castings with '
                              'the 779 mm curb unit, 280 mm curbs, sidewalks falling 2 % to the roadway, 13.8 m clear '
                              'roadway and 17.322 m out to out; 13 mm open joints at the pilasters; 80 typical and 10 '
                              'pilaster concrete brackets (sheets 11-14). End-zone brackets (end brackets, B1-B3), plan '
                              'flare and drains are not modelled.')
            item['sources'] = sorted(set(item['sources']) | {'Primary PDF p.28', 'Primary PDF p.29', 'Primary PDF p.30',
                                                             'Primary PDF p.36'})
            item['part_ids'] = item['part_ids'] + [p for p in bracket_ids if p not in item['part_ids']]
        elif item.get('feature') == 'Four concrete arches':
            item['detail'] = ('Four whole arch barrels, spandrel walls cut to the 2004 level 610 mm below the sidewalk '
                              'soffit and closed to 13 mm joints at the spandrel pilasters, and hidden fill envelopes '
                              'under the new slab. Exact original multi-radius curve and spring haunch thickness remain '
                              'unresolved.')
            item['sources'] = sorted(set(item['sources']) | {'Primary PDF p.31', 'Primary PDF p.32'})
        elif item.get('feature') == 'Architectural parapets':
            item['detail'] = item['detail'].replace('Rail end flare, wing-end pilasters, pilaster caps and the sidewalk '
                                                    'joints are omitted.',
                                                    'Rail end flare, wing-end pilasters and pilaster caps are omitted.')
        elif item.get('feature') == 'Remaining exterior features':
            item['detail'] = item['detail'].replace(
                'sidewalk concrete brackets (sheets 11-14),',
                'end-zone sidewalk brackets (end brackets and B1-B3, sheets 13-14), the sheet 15-1 concrete end walls '
                'and gauge-well wall, sidewalk end flare,')
    manifest['review_correction_3'] = TAG
    manifest['revision'] = REVISION
    manifest['review_correction_record_3'] = dict(
        source_pdf_pages=SOURCE_PAGES, printed_sheets=PRINTED_SHEETS, reference_2026_sheets=[15],
        resolved_deviations=['deck-soffit-in-fill-envelope', 'sidewalk-joints-not-modelled'],
        partly_resolved_deviations=['sidewalk-brackets-not-modelled'],
        corrections={
            'roadway_slab': 'deck ends at the longitudinal expansion joints, centre lines |Y| 6.121 (sheet 15), with a '
                            '12.7 mm opening: slab edges |Y| 6.11465, curb-unit faces 6.12735 (was 6.9 at the curb '
                            'faces)',
            'curb_unit': 'walk_* carry the curb unit from the expansion joint: 230 mm deep at the joint, soffit falling '
                         '165 mm to the spandrel inner face, on the wall cut across the 381 mm wall (sheets 14, 15)',
            'wall_cut': 'spandrel_*, endwall_* and pilaster_* tops cut to 610 mm below the sidewalk soffit, with a 610 '
                        'mm wide seat 838 mm below it in each pilaster under the bracket stem (sheets 14, 15); were '
                        'the old surface less 200 mm / El. 248.5',
            'pilaster_footprint': 'pilaster_* span |Y| 6.706-7.315 (sheet 14: face 1421 mm inside the local coping, 610 '
                                  'mm to the spandrel inner face; were 6.880-7.360), the inner strip from the support '
                                  'top up; spandrel-wall ends trimmed to 13 mm from them over the whole wall thickness '
                                  '(sheet 18)',
            'fill_top': 'fill_* tops at the slab soffit and the curb-unit soffit (sheets 7, 14, 15); were 51 mm into '
                        'the slab',
            'brackets': '80 typical brackets bracket_{span}_{side}_{k} at 305 + 3 @ 2400 + 3 @ 2388 + 3 @ 2400 from the '
                        'pilaster faces (sheets 11-12) with the sheet-14 section; 10 pilaster brackets '
                        'pilbracket_{support}_{side} (sheet 14)',
            'sidewalk_joints': '13 mm open joints through walk_* at both pier pilaster faces and the span side of the '
                               'abutment pilasters, 45-degree path across the 75 mm coping band, 13 mm normal to the '
                               'faces on both legs (sheet 18); nine bodies per sidewalk'},
        decisions={
            'cut_reference': 'The 610 and 838 mm depths are read from the sidewalk soffit at the spandrel face: the '
                             'dimension lines hang from the extended 2 % soffit line, and with that reference the '
                             'sheet-14 chains (203 + 75 + R 1778 arc + 75; 203 + 203 + 75 + R 775 arc + 75) close '
                             'within 2 mm.',
            'pilaster_bracket_tier': 'The 838 mm upper tier (section 2-2, depth not dimensioned) is taken as the first '
                                     '203 mm tier of the elevation, which is the only part outside the 610 mm stem.',
            'joint_through_curb_unit': 'The sidewalk joints run through the whole casting to the roadway expansion '
                                       'joint: sheet 9 stops the "Curb & Sidewalk Reinf." of each span 87 mm (top) / '
                                       '137 mm (bottom) short of the pilaster face, and the pilaster panel has its own '
                                       'bars.',
            'arch_overlap': 'Near the crowns the model\'s approximate arch ring rises above the 610 mm cut; the walls '
                            'end there and the curb unit and brackets stop on the ring, as the sheet-14 note "Where '
                            'Bracket overlaps Arch Ring" provides for.',
            'expansion_joint_opening': 'The 2004 sheets 9 and 15 show the longitudinal "Expansion Joint Sealing System" '
                                       'but no opening; the 2026 reference, sheet 15 note 4, records the existing '
                                       'deck joints (transverse and longitudinal edge joints) as 0.5 in. open, so a '
                                       '12.7 mm opening centred on the 779 mm line is used. The seal is not '
                                       'modelled.',
            'pilaster_cut': 'Sheet 14 shows the 838 mm cut only on the pilaster-bracket centre line; elsewhere the '
                            'pilasters are cut to the general 610 mm wall cut under the curb unit, with the 838 mm '
                            'seat 610 mm wide under the bracket stem (recorded as a known deviation).'},
        kept={'end_zone_brackets': 'End brackets (sheet 14) and brackets B1-B3 (sheet 13) of the four floor-end zones: '
                                   'they need the end-zone flare (sheets 9-10), the sheet 15-1 end and gauge-well '
                                   'walls and the sheet 18 wing-end pilasters, none of which is modelled',
              'pilaster_cut_beside_brackets': 'Top of the spandrel pilasters beside the bracket stems is not drawn'},
        changed_parts=changed, added_parts=added, removed_parts=[],
        before_glb_sha256=before, after_glb_sha256=hashlib.sha256(out).hexdigest(),
        before_manifest_sha256=manifest_before)
    deviations = [d for d in manifest.get('known_deviations', [])
                  if d.get('id') not in ('sidewalk-brackets-not-modelled', 'deck-soffit-in-fill-envelope',
                                         'sidewalk-joints-not-modelled')]
    deviations.append(dict(
        id='sidewalk-brackets-not-modelled', parts='walk_-1, walk_1, endwall_*, parapet_*_0, parapet_*_5',
        source='sheets 9-10, 11-14, 15-1, 18 (PDF 26-31, 33, 36)',
        deviation='The 90 brackets in the spans and under the rail pilasters are modelled. Not modelled: the brackets '
                  'of the four floor-end zones beyond the abutment pilasters, i.e. the concrete end brackets of sheet '
                  '14 (838 mm wide, 305 mm from the end of each sidewalk structure) and brackets B1, B2 and B3 of '
                  'sheet 13 (381 mm wide, at the 1410 / 2172 mm chains of sheets 11-12). The sidewalk there is a '
                  'plain 190 mm slab on the curb unit.',
        reason='The brackets are dimensioned, but they cannot be placed as drawn on the modelled end zones. Beyond '
               'the P.C. lines at the abutment pilasters the sidewalks, rails and end-floor wall faces flare on '
               'R 27 819 (Abutment 1, sheet 9) and R 22 504 / 24 265 (Abutment 5, sheet 10), and the bracket faces '
               '"follow curvature of Sidewalk" (sheets 13-14); the end brackets bear on the concrete end walls and '
               'gauge-well wall of sheet 15-1 under the wing-end rail pilasters of sheet 18. The model keeps '
               'straight sidewalks, rails and end-floor wall envelopes there and has none of those walls or '
               'pilasters, so the brackets would miss their drawn faces and supports by up to several hundred '
               'millimetres. Settling it needs an end-zone reconstruction from sheets 9-10, 15-1 and 18 (flared '
               'walk_*, parapet_*_0/_5, panels_*_0/_5 and endwall_*, the end and gauge-well walls, the wing-end '
               'pilasters), after which the sheet 13-14 brackets can be added.'))
    deviations.append(dict(
        id='pilaster-cut-beside-brackets', parts='pilaster_*',
        source='sheet 14 (PDF 31); sheets 7, 15 (PDF 24, 32)',
        deviation='Beside the 610 mm bracket stems the spandrel pilasters are cut to the general 610 mm wall-cut level '
                  'under the curb unit, so their projection beyond the spandrel face shows a step about 0.61 m below '
                  'the sidewalk soffit on either side of each pilaster bracket.',
        reason='Sheet 14 gives the 838 mm cut only in the section on the pilaster-bracket centre line, and sheets 7 '
               'and 15 give the 610 mm wall cut only between pilasters; no sheet shows the top of the existing '
               'pilaster beside the bracket. A section through the pilaster off the bracket centre line, or a '
               'survey of the existing pilasters, would settle it.'))
    manifest['known_deviations'] = deviations
    mp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in manifest['review_correction_record_3'].items()
                      if k in ('before_glb_sha256', 'after_glb_sha256')}))
    print(f'{len(changed)} parts changed, {len(added)} parts added')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        correct(Path(sys.argv[1]), Path(sys.argv[2]) if len(sys.argv) > 2 else Path(sys.argv[1]) / 'backup')
    else:
        correct()

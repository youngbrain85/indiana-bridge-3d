"""One-time, drawing-confirmed corrections of Fletcher Avenue over I-65 / I-70 (fletcher-avenue) from the external
model review, preserving unrelated GLB buffers.

    python scripts/correct_fletcher_avenue_review.py [--dry-run]

Source: drawings.pdf, the local review binder. PDF pages 33-73 are the 2026 B-44576 contract sheets (printed sheet n =
PDF page n); PDF pages 74-111 are the 1971 I-65-3(106)111 plans (S7 = PDF 98, S8 = PDF 99, S9 = PDF 100, S10 = PDF 101,
S12 = PDF 103). Local Z = (El. - 698.59 ft) x 0.3048 (old Pier 2 footing bottom); native X = 0 at Sta. 14+85.98.

1. Side and girder identification (sheets 52, 55, 59, 60, 65; S8). Sheet 55: the north arrow points to the lower
   right of the plan, so the plan's lower edge (native -Y) is the north side. Sheet 52 locates TBM #2 on the "South
   Curb ... 29.72' Lt." of Line "Fletcher", and the S8 framing plan and the sheet 59 fillet detail number Girder 1 at
   the upper (+Y) edge. Sheet 65 puts the 4'-6" Modified TX railing (1'-4" base) on the SOUTH coping and the 3'-6"
   TX railing (4" base) on the NORTH coping; sheets 55/60 draw the modified railing on the left of the typical
   section, and sheet 60 the 0 % deck under the right (north) walk. The model had the 4'-6" railing and the "South"
   labels at -Y and numbered girders 1-8 from -Y. The railings are rebuilt with the correct section on each side
   (north 3'-6", south 4'-6" with the 1 ft taller base) and every name that carries a side or a girder number now uses
   the plan numbering (model line j = plan girder 8 - j), the S8 shoe table marks and the sheet 55 wing letters.
   Part ids are unchanged.
2. Girder sections at Pier 2 (S9, S10). Web 60" x 5/8" (both segments), typical haunch detail on S10: web 6'-8" (80")
   from the pier centre line to 6", then a 57'-7 1/2" radius and a reverse 57'-5 1/2" radius back to 5'-0" at 20'-0"
   (ordinates 6'-6 3/4", 6'-3 9/16", 5'-10", 5'-3 3/4", 5'-0 15/16" are reproduced within 0.03 in). Pier segment
   flanges (40'-0" each side of the pier): girders 1 and 8 26" x 2 3/4", girders 2-7 24" x 2 1/4"; field flanges
   1 3/4". The model had a 72" web, a 3/8" web and 2 1/2" exterior pier flanges. The girder tops are kept; the
   bottoms at the pier drop 203.2 mm (interior) / 215.9 mm (exterior). Haunch stiffeners, the Pier 2 cross-frame row
   and the field splices follow the new web.
3. Pier 2 bridge seat (S7, S8, S12). Cap plan riser spacing (south to north) 8'-8", 10'-4", 30'-8", 10'-4", 10'-4",
   8'-8" on the 79'-0" cap; elevation seats El. 718.310, 718.435, 718.690, 718.565, 718.255 and 718.090 (bridge
   seat, north end). The model's wall top was El. 719.12 with isolated risers up to El. 719.67. The wall now stops at
   the lowest seat (El. 718.090) and the seven B2 seat parts are the raised seat steps (risers square to the pier
   axis); the 30'-8" step carries girders 3-5 and is divided between their three seat parts midway between the
   girder lines (a part boundary only). The Pier 2 shoe envelopes span from their seat step to the new girder bottom
   (385-430 mm, against 16" ES3 / 18" ES1-ES2 expansion shoes on S12; see known deviations).
4. Approach slab square ends (sheets 55, 66, 71). Sheet 66 dimensions each R.C. bridge approach 54'-2" from the square
   pavement end to the long (acute) coping corner and 16'-6" at the short corner (68'-6" coping width, 37'-7 2/3"
   skew offset); the sheet 55 "20'-6" R.C. Br. Approach" is measured at the south curb line, not on the centre line,
   and the sheet 71 quantities (277 / 266 SY) match the longer slabs. The square ends move from X = -51.835 / +51.664
   to X = -56.361 / +56.189 (centre-line length 35'-4.2"); the approach walks end on the same lines. The TTX railing
   transitions and RCBA slab extensions at the four corners are not added (deferred, see the record).
5. Roadway and sidewalk cross slopes (sheets 52, 55, 60). 2 % roadway crossfall from the crown to the gutters (27 ft),
   0 % deck under the north walk, the south deck continuing at 2 %, walks 1.5 % rising outward, 8" curb. The model had
   1.5 % with no break at the north curb line (1.18 % effective) and 2 % walks. Deck, walks, joint strips, approach
   slabs and walks are rebuilt on the sheet 52 profile (including the 90 ft vertical curve PVI 12+95 west of 13+40,
   which the original profile function had extrapolated wrongly); railings stand on the new walk tops, haunch tops
   follow the new deck soffit over the unchanged girders, the drains and backwall tops follow the new surface.

Requires numpy, trimesh, shapely and manifold3d; uses box/concat/bolt/rectangular_bar from scripts/bridge_geometry.py.
"""
import hashlib
import json
import struct
import sys
from pathlib import Path

import manifold3d
import numpy as np
import shapely
import trimesh

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from bridge_geometry import bolt, box, concat, rectangular_bar  # noqa: E402

BID = 'fletcher-avenue'
BASE = ROOT / 'data/bridges' / BID
TAG = 'sides-girders-pier-haunch-seat-steps-approach-ends-crossfall'
REVISION = '1.1-review-corrections'

FT, IN = .3048, .0254
SKEW = 28 + 47 / 60 + 15 / 3600
K, COS, SIN = np.tan(np.radians(SKEW)), np.cos(np.radians(SKEW)), np.sin(np.radians(SKEW))
SPAN = 147 * FT
U0, U1 = -SPAN - (2 + 6.75 / 12) * FT, SPAN + 2 * FT          # deck ends (sheet 55, 298'-6 3/4" floor)
WIDTH = 68.5 * FT
HALF = WIDTH / 2
SLAB, CLEAR, ROAD = 8 * IN, .09, 27 * FT                       # as built by build_indiana_batch3.fletcher
YS = (np.arange(8) - 3.5) * 9 * FT                             # model girder lines j = 0..7 (-Y to +Y)
DATUM = 698.59
APPROACH_W = 66.5 * FT                                         # model approach width (unchanged)


def plan_girder(j):
    return 8 - j                                               # S8 / sheet 59: Girder 1 at +Y (south)


def z_el(el):
    return (el - DATUM) * FT


def sx(u, y):
    return u - K * y


# ------------------------------------------------------------------------------------------ profile and surfaces
def grade_old(x):
    """Profile function of the original model (feet evaluated, metres returned)."""
    s = 1485.98 + np.asarray(x) / FT
    t = s - 1340
    e = 727.61 + .0142 * t + (.0009 - .0142) * t * t / (2 * 90)
    t = s - 1430
    e = np.where(s >= 1430, 728.29 + .0009 * t + (-.02 - .0009) * t * t / (2 * 140), e)
    e = np.where(s >= 1570, 726.95 - .02 * (s - 1570), e)
    t = s - 1620
    e = np.where(s >= 1620, 725.95 - .02 * t + .0154 * t * t / (2 * 50), e)
    return (e - DATUM) * FT


def grade(x):
    """Sheet 52 profile: VC 90' PVI 12+95 (0.99 % / 1.42 %), VC 90' PVI 13+85, VC 140' PVI 15+00, -2.00 %,
    VC 50' PVI 16+45, -0.46 %. Identical to grade_old between 13+40 and 16+70."""
    s = 1485.98 + np.asarray(x, dtype=np.float64) / FT
    if np.any(s < 1250):
        raise ValueError('station before the PVC 12+50')
    d = 1340 - s
    e = 727.61 - .0142 * d + (.0142 - .0099) * d * d / (2 * 90)
    t = s - 1340
    e = np.where(s >= 1340, 727.61 + .0142 * t + (.0009 - .0142) * t * t / (2 * 90), e)
    t = s - 1430
    e = np.where(s >= 1430, 728.29 + .0009 * t + (-.02 - .0009) * t * t / (2 * 140), e)
    e = np.where(s >= 1570, 726.95 - .02 * (s - 1570), e)
    t = s - 1620
    e = np.where(s >= 1620, 725.95 - .02 * t + .0154 * t * t / (2 * 50), e)
    e = np.where(s >= 1670, 725.95 - 1.0 + .0154 * 25 - .0046 * (s - 1670), e)
    return (e - DATUM) * FT


def surface_old(x, y):
    y = np.asarray(y)
    return grade_old(x) - .015 * np.minimum(np.abs(y), ROAD) - .015 * np.maximum(y - ROAD, 0)


def walk_old(x, y):
    return grade_old(x) - .015 * ROAD + 8 * IN + .02 * (np.abs(y) - ROAD)


def surface(x, y):
    """Sheets 55/60: 2 % from the crown; north (-Y) deck level under the walk, south (+Y) deck continuing at 2 %."""
    y = np.asarray(y)
    return grade(x) - .02 * np.minimum(np.abs(y), ROAD) - .02 * np.maximum(y - ROAD, 0)


def walk(x, y):
    """Walk top: 8 in curb above the gutter, 1.5 % rising toward the coping."""
    return grade(x) - .02 * ROAD + 8 * IN + .015 * (np.abs(y) - ROAD)


# ------------------------------------------------------------------------------------------ girder sections
TW_OLD, TW = .375 * IN, .625 * IN
TF_FIELD = 1.75 * IN


def exterior(j):
    return j in (0, 7)


def tf_old(u, j):
    return ((2.5 if exterior(j) else 2.25) if abs(u) <= 40 * FT else 1.75) * IN


def tf_pier(j):
    return (2.75 if exterior(j) else 2.25) * IN                  # S9: 26" x 2 3/4"; S10: 24" x 2 1/4"


def tf_new(u, j):
    return tf_pier(j) if abs(u) <= 40 * FT else TF_FIELD


def web_old(u):
    t = np.clip(1 - abs(u) / (19.5 * FT), 0, 1)
    return (60 + 12 * t * t * (3 - 2 * t)) * IN


R1, R2 = (57 + 7.5 / 12) * FT, (57 + 5.5 / 12) * FT            # S10 typical haunch detail radii
FLAT, HAUNCH_END = .5 * FT, 20 * FT


def _arc1(a):
    return 80 * IN - (R1 - np.sqrt(R1 * R1 - (a - FLAT) ** 2))


def _arc2(a):
    return 60 * IN + (R2 - np.sqrt(R2 * R2 - (HAUNCH_END - a) ** 2))


def _reverse_point():
    lo, hi = 9 * FT, 11.5 * FT
    for _ in range(80):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if _arc1(mid) > _arc2(mid) else (lo, mid)
    return (lo + hi) / 2


PRC = _reverse_point()                                          # about 10'-3.1" from the pier (5'-10" printed)


def web(u):
    a = abs(u)
    if a <= FLAT:
        return 80 * IN
    if a <= PRC:
        return float(_arc1(a))
    if a < HAUNCH_END:
        return float(_arc2(a))
    return 60 * IN


def depth_old(u, j):
    return web_old(u) + 2 * tf_old(u, j)


def depth_new(u, j):
    return web(u) + 2 * tf_new(u, j)


def girder_top(u, j):
    y = YS[j]
    return float(surface_old(sx(u, y), y)) - SLAB - CLEAR       # retained girders: tops unchanged


# ------------------------------------------------------------------------------------------ Pier 2 (S7, S8, S12)
RISERS = np.array([8 + 8 / 12, 10 + 4 / 12, 30 + 8 / 12, 10 + 4 / 12, 10 + 4 / 12, 8 + 8 / 12]) * FT   # south->north
SEATS = [718.310, 718.435, 718.690, 718.565, 718.255, 718.090]                                     # south->north
BOUNDS_S = 39.5 * FT - np.r_[0, np.cumsum(RISERS)]               # along-axis s (+ toward +Y / south), m
SHOES = {1: ['FS1', 'FS2', 'FS3', 'FS3', 'FS3', 'FS3', 'FS2', 'FS1'],                 # S8 shoe table, girders 1..8
         2: ['ES1', 'ES2', 'ES3', 'ES3', 'ES3', 'ES3', 'ES2', 'ES1']}
SHOE_H = {'ES1': 18 * IN, 'ES2': 18 * IN, 'ES3': 16 * IN}       # S12 expansion shoes 1'-6" / 1'-4"


def axis_s(x, y):
    return -SIN * np.asarray(x) + COS * np.asarray(y)


def axis_n(x, y):
    return COS * np.asarray(x) + SIN * np.asarray(y)


def band_of(j):
    s = YS[j] / COS
    for b in range(6):
        if BOUNDS_S[b] >= s >= BOUNDS_S[b + 1]:
            return b
    raise ValueError('girder outside the pier')


# ------------------------------------------------------------------------------------------ approaches (sheet 66)
LONG_EDGE = (54 + 2 / 12) * FT
SQUARE_END = {-1: U0 + K * HALF - LONG_EDGE, 1: U1 - K * HALF + LONG_EDGE}
OLD_OUTER = {-1: U0 - 20.5 * FT, 1: U1 + 20.5 * FT}


# ------------------------------------------------------------------------------------------ mesh helpers
def sweep(profile, stations, fn):
    """Closed prism through `stations` (like bridge_geometry.sweep, caps triangulated by manifold3d)."""
    pts = np.array(profile, dtype=np.float64)
    area = .5 * np.sum(pts[:, 0] * np.roll(pts[:, 1], -1) - np.roll(pts[:, 0], -1) * pts[:, 1])
    if area == 0:
        raise ValueError('degenerate profile')
    order = np.arange(len(pts)) if area > 0 else np.arange(len(pts))[::-1]
    caps = order[np.asarray(manifold3d.triangulate([pts[order]]))]
    n, m = len(pts), len(stations)
    vertices = np.array([fn(float(s), float(a), float(b)) for s in stations for a, b in pts], dtype=np.float64)
    sides = []
    for k in range(m - 1):
        for j in range(n):
            a, b = k * n + j, k * n + (j + 1) % n
            sides += [(a, b, b + n), (a, b + n, a + n)]
    for c in (caps, caps[:, ::-1]):
        mesh = trimesh.Trimesh(vertices, np.vstack([sides, c[:, ::-1], c + (m - 1) * n]), process=False)
        if mesh.is_winding_consistent:
            break
    if mesh.volume < 0:
        mesh.invert()
    if not (mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0):
        raise ValueError('sweep did not produce a closed solid')
    return mesh


def from_manifold(man):
    out = man.to_mesh64()
    mesh = trimesh.Trimesh(np.asarray(out.vert_properties)[:, :3], np.asarray(out.tri_verts), process=False)
    if not (mesh.is_watertight and mesh.volume > 0):
        raise ValueError('manifold result is not a closed solid')
    return mesh


def extrude(polygon, z0, z1):
    """Plan polygon (shapely) extruded vertically from z0 to z1."""
    ring = np.array(shapely.geometry.polygon.orient(polygon, 1).exterior.coords)[:-1]
    man = manifold3d.Manifold.extrude(manifold3d.CrossSection([ring]), z1 - z0).translate((0, 0, z0))
    return from_manifold(man)


def same_points(a, b, tol=2e-5):
    """True if two vertex sets coincide (order-free)."""
    a = np.unique(np.round(np.asarray(a, dtype=np.float64) / tol).astype(np.int64), axis=0)
    b = np.unique(np.round(np.asarray(b, dtype=np.float64) / tol).astype(np.int64), axis=0)
    if len(a) != len(b):
        return False
    return int(np.abs(a - b).max()) <= 2


def tx_panel(a, b, side, y, h, plinth, walk_fn):
    """Generator TX panel (18 open windows) through manifold3d, mapped onto the walk top."""
    lo, hi = a + FT, b - FT
    holes = []
    for c in (lo + hi) / 2 + (np.arange(18) - 8.5) * 1.5 * FT:
        zb, zt, hw = plinth + .30, plinth + .30 + 16 * IN, 3 * IN
        holes.append(np.array([(c - hw, zb), (c + hw, zb), (c + hw, zt - .055), (c + .035, zt + .005), (c, zt + .025),
                               (c - .035, zt + .005), (c - hw, zt - .055)]))
    outer = np.array([(lo, 0), (hi, 0), (hi, h), (lo, h)])
    section = manifold3d.CrossSection([outer] + holes, manifold3d.FillRule.EvenOdd)
    rail = from_manifold(manifold3d.Manifold.extrude(section, FT))
    v = rail.vertices
    yy = y + v[:, 2] - FT / 2
    x = sx(v[:, 0], yy)
    rail.vertices = np.c_[x, yy, walk_fn(x, yy) + v[:, 1]]
    if rail.volume < 0:
        rail.invert()
    return rail


def splice_meshes(u, j, depth, tw):
    """build_indiana_batch3.splices (webw 1.2, webh 1.37, plate 15.9 mm, flange plates 1.53 m, 12 x 10 bolts)."""
    y, b = YS[j], (26 if exterior(j) else 24) * IN
    webw, webh, plate, flangew = 1.2, 1.37, .0159, 1.53
    top = girder_top(u, j)
    x, z = sx(u, y), top - depth / 2
    plates = [box(x - webw / 2, x + webw / 2, y + s * (tw / 2 + plate / 2) - plate / 2,
                  y + s * (tw / 2 + plate / 2) + plate / 2, z - webh / 2, z + webh / 2) for s in [-1, 1]]
    plates += [box(x - flangew / 2, x + flangew / 2, y - b / 2, y + b / 2, zz, zz + plate)
               for zz in [top - depth - plate, top]]
    fast = []
    for dx in np.linspace(-webw / 2 + .05, webw / 2 - .05, 12):
        for dz in np.linspace(-webh / 2 + .05, webh / 2 - .05, 10):
            fast.append(bolt([x + dx, y - tw / 2 - plate, z + dz], [x + dx, y + tw / 2 + plate, z + dz], .011))
    return concat(plates), concat(fast)


CF_ROWS = -SPAN + (8 + 10.875 / 12) * FT + np.arange(13) * (22 + 9 / 12) * FT    # S8: 8'-0 5/16" + 12 @ 22'-9"


def crossframe_mesh(i, j, depth_fn):
    u = CF_ROWS[i]
    ya, yb = YS[j] + .33, YS[j + 1] - .33
    x = sx(u, (ya + yb) / 2)
    za = float(surface_old(x, ya)) - SLAB - CLEAR - .16
    zb = float(surface_old(x, yb)) - SLAB - CLEAR - .16
    d = min(depth_fn(x + K * ya, j), depth_fn(x + K * yb, j + 1)) - .32
    return concat([rectangular_bar([x, ya, za], [x, yb, zb - d], .10, .012),
                   rectangular_bar([x, ya, za - d], [x, yb, zb], .10, .012)])


# ------------------------------------------------------------------------------------------ correction
def correct(base=BASE, backup=ROOT / 'data/fem_research', dry_run=False):
    mp = base / 'model_manifest.json'
    manifest = json.loads(mp.read_text(encoding='utf-8'))
    if manifest.get('review_geometry_correction') == TAG:
        print('Already corrected.')
        return None
    path = base / 'model.glb'
    original = path.read_bytes()
    length = struct.unpack_from('<I', original, 12)[0]
    gltf = json.loads(original[20:20 + length])
    binary = bytearray(original[28 + length:])
    before = hashlib.sha256(original).hexdigest()
    parts = {p['id']: p for p in manifest['parts']}
    meshes = {m['name']: m for m in gltf['meshes']}
    geometry, renamed = [], {}

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
        f = read(prim['indices']).reshape(-1, 3)
        return trimesh.Trimesh(np.c_[v[:, 0], -v[:, 2], v[:, 1]], f, process=False)

    def store(pid, mesh, note=None, dims=None, name=None, new_topology=False, replace=False, basis=None):
        """Write a corrected native-axes mesh and update the manifest part and mesh extras."""
        prim = meshes[pid]['primitives'][0]
        old = native(pid)
        if old.is_watertight and not mesh.is_watertight:
            raise ValueError(f'{pid}: corrected mesh is not watertight')
        if mesh.volume <= 0:
            raise ValueError(f'{pid}: corrected mesh has no positive volume')
        v = mesh.vertices
        glb = np.c_[v[:, 0], v[:, 2], -v[:, 1]].astype('<f4')
        if new_topology:
            color = read(prim['attributes']['COLOR_0'])[0]
            prim['attributes'] = {'POSITION': append(glb, 'VEC3', 5126),
                                  'COLOR_0': append(np.tile(color, (len(v), 1)).astype('u1'), 'VEC4', 5121)}
            gltf['accessors'][prim['attributes']['COLOR_0']]['normalized'] = True
            prim['indices'] = append(np.asarray(mesh.faces).reshape(-1, 1).astype('<u4'), 'SCALAR', 5125)
        else:
            if len(v) != len(old.vertices) or not np.array_equal(np.asarray(mesh.faces), np.asarray(old.faces)):
                raise ValueError(f'{pid}: topology changed without new_topology')
            prim['attributes']['POSITION'] = append(glb, 'VEC3', 5126)
        p = parts[pid]
        p['bounds_m'] = np.round(mesh.bounds, 6).tolist()
        if 'volume_m3' in p:
            p['volume_m3'] = round(float(mesh.volume), 9)
        if dims:
            p.setdefault('dimensions', {}).update(dims)
        if note:
            p['note'] = note if replace else (p.get('note', '') + ' ' + note).strip()
        if basis:
            p['basis'] = basis
        if name:
            rename(pid, name)
        meshes[pid]['extras'].update(p)
        if pid not in geometry:
            geometry.append(pid)

    def rename(pid, name):
        p = parts[pid]
        if p['name'] != name:
            renamed.setdefault(pid, dict(before=p['name']))['after'] = name
            p['name'] = name
        meshes[pid]['extras'].update(p)

    span = lambda i: 'AB'[i]                                                            # noqa: E731

    # ------------------------------------------------------------------ expected original state
    if not np.isclose(native('pier_2_wall').bounds[1, 2], 6.25802, atol=2e-5):
        raise ValueError('pier_2_wall: unexpected wall top')
    deck = native('deck')
    if sorted(np.unique(deck.vertices[:, 1].round(4)).tolist()) != [-10.4394, 0.0, 10.4394] or \
            np.abs(deck.vertices[:, 2] - surface_old(deck.vertices[:, 0], deck.vertices[:, 1])).min() > 1e-5:
        raise ValueError('deck: not the original 1.5 % three-line deck')
    if not np.isclose(parts['tx_-1_0_0']['dimensions']['height_m'], 4.5 * FT):
        raise ValueError('tx_-1_0_0: unexpected railing height')

    # ------------------------------------------------------------------ 2. girders (S9, S10)
    pier_bottom = {}
    for j, y in enumerate(YS):
        for i in range(2):
            pid = f'girder_{i}_{j}'
            mesh = native(pid)
            v = mesh.vertices.copy()
            for x in np.unique(v[:, 0]):
                ring = np.flatnonzero(v[:, 0] == x)
                if len(ring) != 12:
                    raise ValueError(f'{pid}: unexpected ring at X={x}')
                z = v[ring, 2]
                levels = np.unique(np.round(z, 5))
                if len(levels) != 4:
                    raise ValueError(f'{pid}: unexpected section levels')
                lv = np.searchsorted(levels, np.round(z, 5))
                u = x + K * y
                tf_bot, web0, tf_top = np.diff(levels)
                if not (np.isclose(web0, web_old(u), atol=2e-5) and np.isclose(tf_top, tf_bot, atol=2e-5)
                        and (np.isclose(tf_top, TF_FIELD, atol=2e-5) or np.isclose(tf_top, tf_old(0, j), atol=2e-5))):
                    raise ValueError(f'{pid}: unexpected original section at u={u:.4f}')
                pier = not np.isclose(tf_top, TF_FIELD, atol=2e-5)
                f = tf_pier(j) if pier else TF_FIELD
                top = z.max()
                new = np.array([top - 2 * f - web(u), top - f - web(u), top - f, top])
                v[ring, 2] = new[lv]
                dy = v[ring, 1] - y
                webface = np.abs(dy) < .05
                if not np.allclose(np.abs(dy[webface]), TW_OLD / 2, atol=2e-6):
                    raise ValueError(f'{pid}: unexpected web thickness')
                v[ring[webface], 1] = y + np.sign(dy[webface]) * TW / 2
                if abs(u) < 1e-4:
                    pier_bottom[j] = float(new[0])
            b = (26 if exterior(j) else 24) * IN
            store(pid, trimesh.Trimesh(v, mesh.faces, process=False),
                  note='S9/S10 plate schedule: 60 in x 5/8 in web, 80 in at Pier 2 on the S10 typical haunch '
                       '(57 ft 7 1/2 in and 57 ft 5 1/2 in radii to 20 ft from the pier); pier-segment flanges '
                       f'{b / IN:.0f} in x {"2 3/4" if exterior(j) else "2 1/4"} in to the splices 40 ft from the '
                       'pier, field flanges 1 3/4 in. Top of steel follows the proposed grade less the deck and a '
                       'nominal haunch; camber and cross-girder top elevations are not reconciled.', replace=True,
                  basis='S9/S10 plate schedule and typical haunch detail; reconstructed top profile',
                  dims=dict(web_thickness_m=TW, web_depth_span_m=60 * IN, web_depth_pier_m=80 * IN,
                            haunch_length_m=HAUNCH_END, pier_flange_thickness_m=tf_pier(j),
                            field_flange_thickness_m=TF_FIELD, plan_girder=plan_girder(j)),
                  name=f'Span {span(i)} | retained plate girder {plan_girder(j)}')
    print('girders: pier bottoms ' + ', '.join(f'G{plan_girder(j)} {pier_bottom[j]:.4f}' for j in range(8)))

    # stiffeners: haunch stations 5 ft apart follow the new web (S10); end bearing stiffeners unchanged
    stations = [-SPAN, -15 * FT, -10 * FT, -5 * FT, 0, 5 * FT, 10 * FT, 15 * FT, SPAN]
    for j in range(8):
        for si, u in enumerate(stations):
            pid = f'stiffener_{j}_{si}'
            name = f'Girder {plan_girder(j)} | bearing or haunch stiffener {si + 1}'
            top = girder_top(u, j)
            new_top, new_bot = top - tf_new(u, j), top - tf_new(u, j) - web(u)
            mesh = native(pid)
            v = mesh.vertices.copy()
            zt, zb = top - tf_old(u, j), top - depth_old(u, j) + tf_old(u, j)
            hi, lo = np.isclose(v[:, 2], zt, atol=2e-5), np.isclose(v[:, 2], zb, atol=2e-5)
            if not (hi | lo).all():
                raise ValueError(f'{pid}: unexpected original stiffener')
            if np.isclose(new_top, zt, atol=1e-6) and np.isclose(new_bot, zb, atol=1e-6):
                rename(pid, name)
                continue
            v[hi, 2], v[lo, 2] = new_top, new_bot
            store(pid, trimesh.Trimesh(v, mesh.faces, process=False), name=name,
                  note='Extended to the corrected S10 web depth.')

    # field splices A/B at 40 ft from the pier (S9/S10): new web thickness and exterior pier flange
    for j in range(8):
        for si, u in enumerate([-40 * FT, 40 * FT]):
            pid = f'girder_{j + 1}_splice_{si + 1}'
            old_plates, old_bolts = splice_meshes(u, j, depth_old(u, j), TW_OLD)
            if not (same_points(old_plates.vertices, native(pid).vertices) and
                    same_points(old_bolts.vertices, native(pid + '_bolts').vertices)):
                raise ValueError(f'{pid}: original splice not reproduced')
            plates, bolts = splice_meshes(u, j, depth_new(u, j), TW)
            label = f'Girder {plan_girder(j)} | field splice {"AB"[si]}'
            store(pid, plates, name=label, new_topology=True,
                  note='Web plates on the 5/8 in web; flange plates on the corrected pier-segment flanges (S9/S10).')
            # same bolts, grip lengthened by the thicker web and moved with the web plates (no new topology)
            old = native(pid + '_bolts')
            v = old.vertices.copy()
            v[:, 1] += np.sign(v[:, 1] - YS[j]) * (TW - TW_OLD) / 2
            v[:, 2] -= (depth_new(u, j) - depth_old(u, j)) / 2
            if not same_points(v, bolts.vertices):
                raise ValueError(f'{pid}_bolts: moved bolts differ from the regenerated pattern')
            store(pid + '_bolts', trimesh.Trimesh(v, old.faces, process=False),
                  name=label + ' | visible web fasteners', note='Bolt grip through the 5/8 in web.')

    # cross frames: the Pier 2 row follows the deeper girders; all rows renamed by plan bays
    for i in range(13):
        for j in range(7):
            pid = f'crossframe_{i}_{j}'
            name = f'Cross frame row {i + 1} | bay between girders {plan_girder(j + 1)} and {plan_girder(j)}'
            old = crossframe_mesh(i, j, depth_old)
            if not same_points(old.vertices, native(pid).vertices):
                raise ValueError(f'{pid}: original cross frame not reproduced')
            new = crossframe_mesh(i, j, depth_new)
            if same_points(old.vertices, new.vertices, tol=1e-6):
                rename(pid, name)
                continue
            store(pid, new, name=name, new_topology=True,
                  note='Diagonals extended with the corrected S10 girder depth at Pier 2.')
    for bay in (0, 3, 6):
        for i in range(12):
            rename(f'lateral_{bay}_{i}', f'Top lateral bracing | bay between girders {plan_girder(bay + 1)} and '
                                         f'{plan_girder(bay)}, panel {i + 1}')

    # ------------------------------------------------------------------ 3. Pier 2 seat (S7, S8, S12)
    wall = native('pier_2_wall')
    v = wall.vertices.copy()
    low = z_el(SEATS[-1])
    v[np.isclose(v[:, 2], 6.25802, atol=2e-5), 2] = low
    wall_new = trimesh.Trimesh(v, wall.faces, process=False)
    store('pier_2_wall', wall_new, dims=dict(top_el_ft=SEATS[-1], seat_els_south_to_north_ft=SEATS,
                                             riser_spacing_south_to_north_ft=[round(r / FT, 4) for r in RISERS]),
          note='The source has a wall pier, not a row of columns; rounded ends are simplified. Top at the lowest '
               'bridge seat, El. 718.090 at the north end (S7); the raised seat steps (El. 718.255-718.690) are the '
               'B2 seat parts. Riser spacing 8 ft 8 in, 10 ft 4 in, 30 ft 8 in, 10 ft 4 in, 10 ft 4 in, 8 ft 8 in '
               '(S7 cap plan).', replace=True)
    top_ring = wall.vertices[np.isclose(wall.vertices[:, 2], 6.25802, atol=2e-5)]
    footprint = shapely.MultiPoint([tuple(p) for p in top_ring[:, :2]]).convex_hull
    groups = {}
    for j in range(8):
        groups.setdefault(band_of(j), []).append(j)
    if band_of(0) != 5 or groups[5] != [0]:
        raise ValueError('lowest seat is not under model line 0')
    seat_top, regions = {}, {}
    for b, js in groups.items():
        # the south end step runs out to the (constant-Y) end of the modelled wall
        cuts = [BOUNDS_S[b] if b else 100.0] + \
               [(YS[js[k]] + YS[js[k + 1]]) / 2 / COS for k in range(len(js) - 1)][::-1] + [BOUNDS_S[b + 1]]
        for j, (s_hi, s_lo) in zip(sorted(js, reverse=True), zip(cuts[:-1], cuts[1:])):
            seat_top[j] = z_el(SEATS[b])
            if j == 0:
                continue
            strip = shapely.Polygon([(-SIN * s_lo + COS * n, COS * s_lo + SIN * n) for n in (-5, 5)] +
                                    [(-SIN * s_hi + COS * n, COS * s_hi + SIN * n) for n in (5, -5)])
            region = footprint.intersection(strip)
            regions[j] = region
            s_region = axis_s(*np.array(region.exterior.coords).T)
            block = extrude(region, low, z_el(SEATS[b]))
            pid = f'B2_seat_{j}'
            old = native(pid)
            if not np.isclose(old.bounds[0, 2], 6.25802, atol=2e-5):
                raise ValueError(f'{pid}: unexpected original riser')
            store(pid, block, new_topology=True,
                  name=f'Pier 2 | bridge seat step, girder {plan_girder(j)} (El. {SEATS[b]:.3f})',
                  dims=dict(seat_el_ft=SEATS[b], step_height_m=round(z_el(SEATS[b]) - low, 6),
                            along_axis_limits_ft=[round(float(s_region.min()) / FT, 3),
                                                  round(float(s_region.max()) / FT, 3)]),
                  basis='S7 bridge seat elevations and cap-plan riser spacing',
                  note=f'Continuous S7 seat step at El. {SEATS[b]:.3f} above the El. 718.090 wall top, between '
                       'risers square to the pier axis' +
                       (' (the 30 ft 8 in step is divided between girders 3-5 midway between their lines; part '
                        'boundary only).' if len(js) > 1 else '.'), replace=True)
    # Pier 2 shoe envelopes: seat step to the corrected girder bottom (S8 shoe table, S12)
    stacks = {}
    for j in range(8):
        pid = f'B2_bearing_{j + 1}'
        mesh = native(pid)
        v = mesh.vertices.copy()
        old_bottom = girder_top(0, j) - depth_old(0, j)
        levels = [old_bottom - .32, old_bottom - .22, old_bottom]
        masks = [np.isclose(v[:, 2], z, atol=2e-5) for z in levels]
        if not np.logical_or.reduce(masks).all():
            raise ValueError(f'{pid}: unexpected original bearing stack')
        bottom = girder_top(0, j) - depth_new(0, j)
        if not np.isclose(bottom, pier_bottom[j], atol=2e-5):
            raise ValueError(f'{pid}: girder bottom mismatch')
        v[masks[0], 2], v[masks[1], 2], v[masks[2], 2] = seat_top[j], bottom - .22, bottom
        mark = SHOES[2][plan_girder(j) - 1]
        stacks[pid] = round(bottom - seat_top[j], 4)
        store(pid, trimesh.Trimesh(v, mesh.faces, process=False),
              name=f'Pier 2 | girder {plan_girder(j)} expansion shoe {mark} envelope',
              dims=dict(pad_thickness_m=round(bottom - .22 - seat_top[j], 6), shoe_mark=mark,
                        drawn_shoe_height_m=SHOE_H[mark], derived_stack_m=stacks[pid],
                        seat_el_ft=round(seat_top[j] / FT + DATUM, 3)),
              note=f'Retained 1971 {mark} expansion shoe (S8 shoe table; S12: {SHOE_H[mark] / IN:.0f} in plus shims as '
                   'required). Simplified two-block envelope from the S7 seat step to the corrected girder bottom '
                   f'({stacks[pid]:.3f} m); rocker, plates and anchors are not modelled.', replace=True,
              basis='S8 shoe table, S12 shoe details; envelope between plan seat and girder')
    for bi in (1, 3):
        for j in range(8):
            pid = f'B{bi}_bearing_{j + 1}'
            rename(pid, f'Abutment {bi} | girder {plan_girder(j)} ' +
                   (f'fixed shoe {SHOES[1][plan_girder(j) - 1]} envelope' if bi == 1 else 'bearing assembly'))
            sid = f'B{bi}_seat_{j}'
            if sid in parts:
                rename(sid, f'Abutment {bi} | seat riser, girder {plan_girder(j)}')

    # ------------------------------------------------------------------ 5. deck and walks (sheets 52, 55, 60)
    deck_profile = [(-HALF, -SLAB), (-ROAD, -SLAB), (0, -SLAB), (HALF, -SLAB), (HALF, 0), (0, 0), (-ROAD, 0), (-HALF, 0)]
    stations = np.linspace(U0, U1, max(2, int((U1 - U0) / .6) + 1))
    store('deck', sweep(deck_profile, stations, lambda u, y, z: (sx(u, y), y, surface(sx(u, y), y) + z)),
          new_topology=True, dims=dict(roadway_crossfall=.02, north_deck_under_walk_crossfall=0.0,
                                       south_deck_under_walk_crossfall=.02),
          note='Top corrected to the sheet 55/60 section: 2 % from the crown to the 27 ft gutter lines, level under '
               'the north walk, 2 % continuing under the south walk; sheet 52 profile.')
    for side in (-1, 1):
        pid = f'walk_{side}'
        mesh = native(pid)
        v = mesh.vertices.copy()
        s_old, w_old = surface_old(v[:, 0], v[:, 1]), walk_old(v[:, 0], v[:, 1])
        bot, top = np.abs(v[:, 2] - s_old) < 2e-5, np.abs(v[:, 2] - w_old) < 2e-5
        if not (bot | top).all():
            raise ValueError(f'{pid}: unexpected original walk')
        v[bot, 2] = surface(v[bot, 0], v[bot, 1])
        v[top, 2] = walk(v[top, 0], v[top, 1])
        store(pid, trimesh.Trimesh(v, mesh.faces, process=False),
              name=f'{"North" if side < 0 else "South"} sidewalk | 6 ft 1 in clear',
              dims=dict(walk_crossfall=.015),
              note='Walk 1.5 % rising toward the coping above an 8 in curb (sheets 55/60) on ' +
                   ('the level north deck (sheet 60); -Y is north (sheet 55 north arrow).' if side < 0 else
                    'the south deck continuing at 2 %; +Y is south (sheet 55 north arrow).'), replace=True)
    haunch_range = []
    for j, y in enumerate(YS):
        for i in range(2):
            pid = f'haunch_{i}_{j}'
            mesh = native(pid)
            v = mesh.vertices.copy()
            top = np.abs(v[:, 2] - (surface_old(v[:, 0], v[:, 1]) - SLAB)) < 2e-5
            bot = np.abs(v[:, 2] - (surface_old(v[:, 0], y) - SLAB - CLEAR)) < 2e-5
            if not (top ^ bot).all():
                raise ValueError(f'{pid}: unexpected original haunch')
            v[top, 2] = surface(v[top, 0], v[top, 1]) - SLAB
            thick = v[top, 2] - (surface_old(v[top, 0], y) - SLAB - CLEAR)
            if thick.min() < .02:
                raise ValueError(f'{pid}: corrected haunch thinner than 20 mm')
            haunch_range.append((thick.min(), thick.max()))
            store(pid, trimesh.Trimesh(v, mesh.faces, process=False),
                  name=f'Span {span(i)} | deck haunch, girder {plan_girder(j)}',
                  dims=dict(minimum_thickness_m=round(float(thick.min()), 4),
                            maximum_thickness_m=round(float(thick.max()), 4)),
                  note='Top refitted to the corrected 2 % deck soffit; the retained girder top is unchanged.')
    for end in (-1, 1):
        u = U0 if end < 0 else U1
        pid = f'joint_{end}'
        prof = [(-HALF, -.06), (-ROAD, -.06), (0, -.06), (HALF, -.06), (HALF, 0), (0, 0), (-ROAD, 0), (-HALF, 0)]
        store(pid, sweep(prof, [u - .009, u + .009], lambda q, y, z: (sx(q, y), y, surface(sx(q, y), y) + z)),
              new_topology=True, note='Follows the corrected 2 % deck section.')
        pid = f'abut_{1 if end < 0 else 3}_backwall'
        mesh = native(pid)
        v = mesh.vertices.copy()
        top = np.abs(v[:, 2] - (surface_old(v[:, 0], v[:, 1]) - SLAB)) < 2e-5
        if top.sum() != len(v) // 2:
            raise ValueError(f'{pid}: unexpected original backwall top')
        v[top, 2] = surface(v[top, 0], v[top, 1]) - SLAB
        store(pid, trimesh.Trimesh(v, mesh.faces, process=False),
              note='Top corners follow the corrected deck soffit at the copings.')
    for side in (-1, 1):
        for end in (-1, 1):
            pid = f'OS_drain_{side}_{end}'
            u, y = end * (SPAN - 8 * FT), side * (ROAD - .20)
            x = sx(u, y)
            mesh = native(pid)
            if not np.isclose(mesh.vertices[:, 2].max(), surface_old(x, y) + .031, atol=2e-5):
                raise ValueError(f'{pid}: unexpected original drain')
            mesh.vertices[:, 2] += float(surface(x, y) - surface_old(x, y))
            store(pid, trimesh.Trimesh(mesh.vertices, mesh.faces, process=False),
                  name=f'{"North" if side < 0 else "South"} Type OS roadway drain | span {"AB"[end > 0]}',
                  note='Lowered onto the corrected 2 % gutter.')

    # ------------------------------------------------------------------ 1. railings on the correct sides (sheet 65)
    for side in (-1, 1):
        y = side * (HALF - 8 * IN)
        h_old, plinth_old = ((4.5, FT) if side < 0 else (3.5, 0))
        h_new, plinth_new = ((3.5, 0) if side < 0 else (4.5, FT))
        label = 'North TX rail' if side < 0 else 'South modified TX rail'
        for si, (aa, bb) in enumerate([(U0, 0), (0, U1)]):
            cuts = np.linspace(aa, bb, 6)
            for panel, (a, b) in enumerate(zip(cuts[:-1], cuts[1:])):
                pid = f'tx_{side}_{si}_{panel}'
                old = tx_panel(a, b, side, y, h_old * FT, plinth_old, walk_old)
                if not same_points(old.vertices, native(pid).vertices):
                    raise ValueError(f'{pid}: original railing panel not reproduced')
                new = tx_panel(a, b, side, y, h_new * FT, plinth_new, walk)
                store(pid, new, new_topology=True, name=f'{label} | span {span(si)}, panel {panel + 1}',
                      dims=dict(height_m=h_new * FT),
                      note=('Corrected to the sheet 65 north-coping TX railing, 3 ft 6 in' if side < 0 else
                            'Corrected to the sheet 65 south-coping modified TX railing, 4 ft 6 in, base 1 ft taller '
                            '(1 ft 4 in against 4 in)') + '; stands on the corrected 1.5 % walk.')
            for k, uc in enumerate(cuts):
                pid = f'txpost_{side}_{si}_{k}'
                mesh = native(pid)
                v = mesh.vertices.copy()
                rel = v[:, 2] - walk_old(v[:, 0], v[:, 1])
                lo, hi = np.abs(rel) < 2e-5, np.abs(rel - h_old * FT) < 2e-5
                if not (lo | hi).all():
                    raise ValueError(f'{pid}: unexpected original pilaster')
                v[:, 2] = walk(v[:, 0], v[:, 1]) + np.where(hi, h_new * FT, 0)
                store(pid, trimesh.Trimesh(v, mesh.faces, process=False),
                      name=f'{label.split(" TX")[0].replace(" modified", "")} TX rail | span {span(si)} pilaster {k + 1}',
                      dims=dict(height_m=h_new * FT),
                      note=f'Solid pilaster envelope, {"3 ft 6 in" if side < 0 else "4 ft 6 in"} as the '
                           f'{"north" if side < 0 else "south"} coping railing (sheet 65); on the corrected walk.')

    # ------------------------------------------------------------------ 4. approach slabs and walks (sheet 66)
    approach_record = {}
    for end in (-1, 1):
        u = U0 if end < 0 else U1
        abut = 1 if end < 0 else 3
        pid = f'approach_{end}'
        old = native(pid)
        if not np.isclose(old.bounds[0 if end < 0 else 1, 0], OLD_OUTER[end], atol=2e-5):
            raise ValueError(f'{pid}: unexpected original square end')
        outer = SQUARE_END[end]

        def at(t, y, outer=outer, u=u):
            return (1 - t) * sx(u, y) + t * outer

        prof = [(-APPROACH_W / 2, 0), (-ROAD, 0), (0, 0), (APPROACH_W / 2, 0), (APPROACH_W / 2, 1), (0, 1), (-ROAD, 1),
                (-APPROACH_W / 2, 1)]
        slab = sweep(prof, np.linspace(0, 1, 45), lambda t, y, h: (at(t, y), y, surface(at(t, y), y) - (1 - h) * FT))
        centre = abs(outer - u)
        store(pid, slab, new_topology=True,
              dims=dict(centerline_length_m=round(centre, 6), long_edge_at_coping_m=LONG_EDGE,
                        square_end_x_m=round(outer, 6)),
              note=f'Square end corrected to sheet 66: 54 ft 2 in from the square end to the long coping corner, '
                   f'{centre / FT:.2f} ft on the centre line (the sheet 55 20 ft 6 in is at the south curb line); '
                   '2 % crown and level north walk zone as the deck.')
        parts[pid]['note'] = parts[pid]['note'].replace(
            'Square roadway end and skew bridge end; centerline length 20 ft 6 in.',
            'Square roadway end and skew bridge end.')
        meshes[pid]['extras'].update(parts[pid])
        approach_record[pid] = round(outer, 5)
        for side in (-1, 1):
            pid = f'approach_walk_{end}_{side}'
            y0, y1 = sorted([side * ROAD, side * APPROACH_W / 2])
            mesh = sweep([(y0, 0), (y1, 0), (y1, 1), (y0, 1)], np.linspace(0, 1, 25),
                         lambda t, y, h: (at(t, y), y, (1 - h) * surface(at(t, y), y) + h * walk(at(t, y), y)))
            store(pid, mesh, new_topology=True,
                  name=f'Abutment {abut} | {"north" if side < 0 else "south"} approach sidewalk',
                  note='Extended to the corrected square end; 1.5 % walk on the corrected slab.')

    # ------------------------------------------------------------------ 1. remaining side names
    for bi, letters in ((1, {-1: 'A', 1: 'B'}), (3, {-1: 'C', 1: 'D'})):
        for side in (-1, 1):
            rename(f'wing_{bi}_{side}', f'Abutment {bi} | retained Wing {letters[side]} '
                                        f'({"north" if side < 0 else "south"})')

    # ------------------------------------------------------------------ checks across parts
    for j in range(8):
        for i in range(2):
            g = native(f'girder_{i}_{j}').vertices
            gap = surface(g[:, 0], g[:, 1]) - SLAB - g[:, 2]
            if gap.min() <= 0:
                raise ValueError(f'girder_{i}_{j} penetrates the corrected deck')
    for j in range(8):
        bearing = native(f'B2_bearing_{j + 1}')
        foot = shapely.MultiPoint([tuple(p) for p in bearing.vertices[:, :2]]).convex_hull
        under = native(f'B2_seat_{j}') if j else native('pier_2_wall')
        inside = regions[j].contains(foot) if j else \
            (footprint.contains(foot) and not any(r.intersects(foot) for r in regions.values()))
        if not (inside and np.isclose(under.bounds[1, 2], bearing.bounds[0, 2], atol=1e-5)):
            raise ValueError(f'B2_bearing_{j + 1}: not seated on its step')

    # ------------------------------------------------------------------ manifest bookkeeping
    for d in manifest['detail_coverage']:
        if d['feature'] == 'Whole two-span structure':
            d['detail'] += (' Girders numbered 1 (south, +Y) to 8 (north, -Y) as on S8; Pier 2 seat steps per S7.')
        elif d['feature'] == 'Retained steel details':
            d['detail'] += ' Web 5/8 in; 80 in web at Pier 2 on the S10 typical haunch; S9/S10 pier flanges.'
        elif d['feature'] == 'Proposed architectural rails and walks':
            d['detail'] = ('North (-Y) 3 ft 6 in TX rail and south (+Y) 4 ft 6 in modified TX rail with the 1 ft taller '
                           'base, 360 actual window openings, walks 1.5 % above an 8 in curb on a 2 % deck. Molded '
                           'window splays and recesses remain simplified.')
        elif d['feature'] == 'Approaches, drainage and interfaces':
            d['detail'] = ('Both skew-to-square approach slabs (54 ft 2 in long edge, sheet 66) with their walks and '
                           'four drain envelopes. TTX transitions, RCBA slab extensions, drain routing, slab '
                           'penetrations, roadside terminals and traffic equipment are not reconstructed.')
    deviations = [d for d in manifest.get('known_deviations', []) if d.get('id') not in
                  ('pier2-shoe-stack', 'haunch-thickness', 'ttx-transitions')]
    residual = [stacks[f'B2_bearing_{j + 1}'] - SHOE_H[SHOES[2][plan_girder(j) - 1]] for j in range(8)]
    hmin, hmax = min(a for a, _ in haunch_range), max(b for _, b in haunch_range)
    xs = np.linspace(U0 - K * HALF, U1 + K * HALF, 2001)
    lift = float(np.max(grade(xs) - grade_old(xs)))
    deviations += [
        dict(id='pier2-shoe-stack', parts='B2_bearing_1..8', source='S7, S8, S12 (PDF 98, 99, 103)',
             deviation='Envelopes span ' + ', '.join(f'{k} {v:.3f} m' for k, v in stacks.items()) +
                       ' from the S7 seat steps to the girder bottoms; the drawn ES1/ES2 shoes are 18 in (0.457 m) and '
                       'ES3 16 in (0.406 m) plus shims as required.',
             reason='Retained girder tops are derived from the proposed 2026 grade less a nominal deck and haunch, '
                    'not from a survey or the 1971 seat elevations; the residual is '
                    f'{min(residual) * 1000:+.0f} to {max(residual) * 1000:+.0f} mm.'),
        dict(id='haunch-thickness', parts='haunch_*', source='sheets 52, 55, 60',
             deviation=f'With the 2 % deck over the unchanged girder tops the haunches are {hmin * 1000:.0f}-'
                       f'{hmax * 1000:.0f} mm thick (the model had a nominal 90 mm); near Abutment 1 the sheet 52 '
                       f'vertical curve west of Sta. 13+40 raises the deck by up to {lift * 1000:.0f} mm over the '
                       'original profile function.',
             reason='Girder elevations are retained; no screed or camber table is reconstructed.'),
        dict(id='ttx-transitions', parts='(not modelled)', source='sheets 66, 68, 69',
             deviation='The four Type TTX modified railing transitions (Wings A-D) and the RCBA slab extensions '
                       'under them are not modelled.',
             reason='New components with their own window, section D-D to G-G and end pilaster geometry; deferred '
                    'to a generator rebuild.')]
    manifest['known_deviations'] = deviations

    gltf['buffers'][0]['byteLength'] = len(binary)
    while len(binary) % 4:
        binary.append(0)
    encoded = json.dumps(gltf, ensure_ascii=True, separators=(',', ':')).encode()
    encoded += b' ' * ((-len(encoded)) % 4)
    out = (struct.pack('<III', 0x46546c67, 2, 28 + len(encoded) + len(binary)) +
           struct.pack('<II', len(encoded), 0x4e4f534a) + encoded + struct.pack('<II', len(binary), 0x004e4942) + binary)
    manifest['review_geometry_correction'] = TAG
    previous_revision = manifest.get('revision')
    manifest['revision'] = REVISION
    manifest['review_geometry_correction_record'] = dict(
        source_pdf_pages=[52, 55, 59, 60, 65, 66, 71, 98, 99, 100, 101, 103],
        printed_sheets=['52', '55', '59', '60', '65', '66', '71', 'S7', 'S8', 'S9', 'S10', 'S12'],
        previous_revision=previous_revision,
        corrections={
            'sides_and_numbering': 'North = -Y (sheet 55 north arrow, sheet 52 TBM #2 "South Curb ... Lt."); Girder 1 '
                                   'at +Y (S8, sheet 59): model line j = plan girder 8 - j. North TX 3 ft 6 in, south '
                                   'modified TX 4 ft 6 in (sheet 65). Names only; ids unchanged.',
            'girders': 'S9/S10: web 5/8 in, 80 in at Pier 2 (S10 typical haunch, radii 57 ft 7 1/2 in / 57 ft 5 1/2 in, '
                       'reverse point %.4f m), pier flanges 2 3/4 in (girders 1, 8) / 2 1/4 in; tops unchanged, pier '
                       'bottoms ' % PRC + ', '.join(f'G{plan_girder(j)} {pier_bottom[j]:.4f} m' for j in range(8)) + '.',
            'pier2_seat': 'S7: wall top El. 718.090 (Z %.4f); seat steps El. ' % z_el(SEATS[-1]) +
                          ', '.join(f'{e:.3f}' for e in SEATS) + ' south to north between risers 8-8, 10-4, 30-8, '
                          '10-4, 10-4, 8-8 ft-in.',
            'approach_square_ends': 'Sheet 66: 54 ft 2 in long edge; square ends X = ' +
                                    ', '.join(f'{k} {v:+.5f} m' for k, v in approach_record.items()) + '.',
            'cross_slopes': 'Sheets 55/60: roadway 2 %, north deck level under the walk, south 2 % continuing, walks '
                            '1.5 %, 8 in curb; sheet 52 profile incl. VC PVI 12+95.'},
        deferred={'F4 TTX transitions': 'Sheets 66, 68, 69: four modified TTX transitions (Wing A 30 ft 2 in and '
                                        'Wing C 17 ft 2 in pay limits on sheet 68; Wings B and D on sheet 69) and their '
                                        'RCBA slab extensions; new parts for a generator rebuild.'},
        changed_parts=geometry, renamed_parts=renamed,
        before_glb_sha256=before, after_glb_sha256=hashlib.sha256(out).hexdigest())
    record = manifest['review_geometry_correction_record']
    print(json.dumps({k: (v if k not in ('changed_parts', 'renamed_parts') else f'{len(v)} parts')
                      for k, v in record.items()}, indent=1))
    if dry_run:
        print('Dry run, nothing written.')
        return out, manifest
    backup.mkdir(exist_ok=True)
    (backup / f'{BID}_before_review_correction.glb').write_bytes(original)
    (backup / f'{BID}_manifest_before_review_correction.json').write_bytes(mp.read_bytes())
    path.write_bytes(out)
    mp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return out, manifest


if __name__ == '__main__':
    correct(dry_run='--dry-run' in sys.argv)

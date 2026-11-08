"""Fourth review (3D placement review; runs after correct_21st_street_i465_review_3.py): seat the concrete railings
on the deck and set the ornamental railing posts on their sheet 60 stations, preserving unrelated GLB buffers.

    python scripts/correct_21st_street_i465_3d_review.py [--dry-run]

Drawing evidence (contract IB-30026, drawings.pdf; printed sheets 41-62 are PDF pages 41-62, printed sheet 73 is
PDF page 72):

S01. parapet_1 / parapet_-1 floated 36.65-45.23 mm above the deck top along their whole 71.355 m -> RESOLVE.
   - Sheet 59 (PDF 59) TYPICAL SECTION BARRIER DETAILS: the railing is one concrete mass with the deck coping. The
     8 in head and 2'-2" stem stand on the level construction joint at the sidewalk surface; below the joint the
     concrete runs down to the slab top, 11 1/4" below the joint at the exterior face; the stem face on the sidewalk
     side is 1 in behind the head (1 in step and 1 in chamfer) and meets the sidewalk surface.
   - The model kept the original base (36.65 mm above the deck at the sidewalk face, 45.22 mm at the stem's outer
     face) when an earlier correction lengthened the stem, and its sidewalk-side face sloped from the head chamfer to
     that base, leaving a 7 mm wedge of air between it and the sidewalk's outer face at the sidewalk surface.
   - Rebuild of each 8-vertex section as 10 vertices: the two base vertices move down onto the deck top (2 % cross
     fall, local profile); two vertices are added at the sidewalk surface (the level construction joint), so the face
     below the joint is the sidewalk's outer face (Y = +/-24'-0") and the face above it is vertical 1 in behind the
     head (Y = +/-24'-1", the head chamfer vertex), as drawn. Head, top, exterior face and recess indication unchanged:
     34 in above the sidewalk; 45.2 in above the deck at the stem's exterior face (sheet 59: 34 + 11 1/4 = 45 1/4 in).
S02. Terminal ornamental-railing posts stood on the parapet ends (half of each base plate and two anchor nuts over
     air) -> DECIDE, posts on the sheet 60 stations.
   - Sheet 60 (PDF 60) NORTH / SOUTH RAILING ELEVATION gives every bridge post station. North: 11+77.44 | 4'-1 1/2"
     | 11+81.57 | 15 spa. @ 7'-4 1/8" = 110'-2 3/4" | 12+91.79 (CL Bent 2) | 15 spa. @ 7'-4 3/8" = 110'-6" | 14+02.29 |
     4'-1 1/2" | 14+06.42. South: 11+93.74 | 4'-1 1/2" | 11+97.62 | 15 spa. @ 7'-4 3/8" = 110'-6" | 13+08.37 (CL
     Bent 2) | 15 spa. @ 7'-4 1/8" = 110'-2 3/4" | 14+18.59 | 4'-1 1/2" | 14+22.72. Beyond the outer star posts the
     railing continues on the approach barriers (2 spa. @ 9'-0" ...), which are not part of this model.
   - The stations are Line M stations (x = (sta - 13+00.08) ft, the model's origin); the pier dashed lines 12+91.79 /
     13+08.37 average exactly 13+00.08 and are CL Bent 2 at the coping faces (Y = +/-25'-6").
   - The chain is taken from the CL Bent 2 post with the dimensioned totals: 15 x 7'-4 1/8" is 110'-1 7/8" and 15 x
     7'-4 3/8" is 110'-5 5/8", not the printed 110'-2 3/4" / 110'-6"; the totals close on the station labels, so the
     bays are total / 15 (7'-4.18" and 7'-4.40", the printed spacings rounded to 1/8"). The chain reproduces every
     label within 0.01 ft except south 11+97.62, which both the 4'-1 1/2" bay and the 110'-6" chain put at 11+97.87
     (label read as a typo). Sheet 61's "Center on Monument at End Bents" note would place the star bays 0.13-0.16 m
     from the sheet 60 stations (monument E/F stations, sheet 73) and break the dimensioned chain, so sheet 60
     controls.
   - The model had the outer star posts on the parapet ends and 30 equal 7'-6 3/8" bays. Now the outer posts are
     0.75-0.82 m inside the parapet ends (base plates and nuts wholly on concrete), the star bays stay 4'-1 1/2"
     and the 30 bays are 2.2399 / 2.2454 m as dimensioned. Posts, caps, base plates, nuts, rings, star rings,
     stars and pickets move rigidly (pickets keep 15 per bay, equally spaced); pipe and tube rails are re-spanned
     post to post; the flowing graphics follow their ring posts (rigid near the rings, smooth stretch between). All
     parts keep their height above the railing top (the profile grade is re-applied at the new stations).

Part ids and mesh names are unchanged; no part is added or removed. Moved railing parts get new POSITION accessors
(indices and colours reused); the two railings are re-meshed. Requires numpy, trimesh, manifold3d and shapely.
"""
import hashlib
import json
import re
import struct
import sys
from pathlib import Path

import numpy as np
import trimesh
from shapely.geometry import Polygon

ROOT = Path(__file__).resolve().parents[1]
BID = '21st-street-i465'
BASE = ROOT / 'data/bridges' / BID
FT = 0.3048
IN = FT / 12
TAG = 'parapet-on-deck-railing-posts-sheet60'
TAG_KEY = 'review_geometry_correction_3d'
RECORD_KEY = 'review_correction_record_3d'
REVISION = '1.4-3d-review'
PREVIOUS_TAG = 'known-deviations-decided-end-bent-stack-rebuilt'      # correct_21st_street_i465_review_3.py
PREVIOUS_REVISION = '1.3-deviations'

SKEW = np.radians(18.0)
TAN = float(np.tan(SKEW))
HALF_FLOOR = (117 * 12 + 0.625) * IN            # sheet 59: 117'-0 5/8" CL Bent 2 to end of bridge floor (Line M)
Y_WALK = 24.0 * FT                               # sheet 56: 36 ft roadway + 6 ft sidewalk -> railing face at 24'-0"
Y_HEAD_IN = Y_WALK + 1.0 * IN                    # sheet 59: stem face 1 in behind the head on the sidewalk side
Y_STEM_OUT = 7.747                               # as modelled: stem exterior face (recess indication outside it)
Y_COPING = 25.5 * FT                             # sheet 56: 51'-0" out to out of coping
STA0 = 1300.08                                   # Line M station of CL Bent 2 = model X origin (manifest assumptions)
BAY_STAR = (4 * 12 + 1.5) * IN                   # sheets 60, 61, 62: 4'-1 1/2"
# sheet 60: "15 Spa. @ 7'-4 1/8" = 110'-2 3/4"" and "15 Spa. @ 7'-4 3/8" = 110'-6"". The spacings are rounded (15 x
# 7'-4 1/8" = 110'-1 7/8", 15 x 7'-4 3/8" = 110'-5 5/8"); the totals close on the station labels, so bay = total / 15.
BAY_A = (110 * 12 + 2.75) * IN / 15              # 7'-4.183"
BAY_B = (110 * 12 + 6.0) * IN / 15               # 7'-4.400"
# sheet 60: station of the post on CL Bent 2 and the 15-bay spacings west / east of it
SIDES = {1: dict(name='north', pier_sta=1291.79, west=BAY_A, east=BAY_B,
                 labels={0: 1177.44, 1: 1181.57, 16: 1291.79, 31: 1402.29, 32: 1406.42}),
         -1: dict(name='south', pier_sta=1308.37, west=BAY_B, east=BAY_A,
                  labels={0: 1193.74, 1: 1197.62, 16: 1308.37, 31: 1418.59, 32: 1422.72})}
LABEL_TYPO = {(-1, 1): 1197.87}                  # south 11+97.62: chain and 4'-1 1/2" bay give 11+97.87
MONUMENT_EF_CENTRE = {(1, 0): 1178.98, (-1, 0): 1196.24, (1, 1): 1403.92, (-1, 1): 1421.18}   # sheet 73 table
N_POSTS = 33
ORNAMENT = re.compile(r'(railpost|railbase|railcap|railbolt|railpipe|railtube|picket|railarch|railring|starring|star)_')
TOL = 1e-5
FIT = 1e-6                                       # m3, float32 residue of the manifold booleans


def boolean(op, meshes):
    return getattr(trimesh.boolean, op)(meshes, engine='manifold')


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


def on_plane_area(points, mesh, y0, tol=2e-5):
    """True for points (in the plane Y = y0) covered by a triangle of mesh lying in that plane."""
    tri = mesh.triangles
    flat = np.all(np.abs(tri[:, :, 1] - y0) < tol, axis=1)
    out = np.zeros(len(points), bool)
    for t in tri[flat]:
        a, b, c = t[:, [0, 2]]
        v0, v1 = c - a, b - a
        d00, d01, d11 = v0 @ v0, v0 @ v1, v1 @ v1
        den = d00 * d11 - d01 * d01
        if abs(den) < 1e-18:
            continue
        w = points - a
        d02, d12 = w @ v0, w @ v1
        u = (d11 * d02 - d01 * d12) / den
        v = (d00 * d12 - d01 * d02) / den
        out |= (u >= -1e-7) & (v >= -1e-7) & (u + v <= 1 + 1e-7)
    return out


def ear_clip(poly):
    """Triangulate a simple 2D polygon (counter-clockwise) by ear clipping; returns index triples."""
    idx = list(range(len(poly)))
    out = []

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    guard = 0
    while len(idx) > 3:
        guard += 1
        if guard > 1000:
            raise ValueError('ear clipping failed')
        for k in range(len(idx)):
            i0, i1, i2 = idx[k - 1], idx[k], idx[(k + 1) % len(idx)]
            a, b, c = poly[i0], poly[i1], poly[i2]
            if cross(a, b, c) <= 1e-14:
                continue
            inside = False
            for j in idx:
                if j in (i0, i1, i2):
                    continue
                p = poly[j]
                if cross(a, b, p) >= -1e-14 and cross(b, c, p) >= -1e-14 and cross(c, a, p) >= -1e-14:
                    inside = True
                    break
            if not inside:
                out.append((i0, i1, i2))
                idx.pop(k)
                break
    out.append(tuple(idx))
    return out


def loft(rings):
    """Closed solid through planar rings (n_sections, n, 3): side quads plus ear-clipped end caps, outward faces."""
    ns, n = rings.shape[:2]
    v = rings.reshape(-1, 3)
    side = []
    for i in range(ns - 1):
        for j in range(n):
            a, b = i * n + j, i * n + (j + 1) % n
            c, d = (i + 1) * n + (j + 1) % n, (i + 1) * n + j
            side += [(a, b, c), (a, c, d)]
    side = np.array(side)
    if trimesh.Trimesh(v, side, process=False).volume < 0:             # open tube: sign still tells the winding
        side = side[:, ::-1]
    caps = []
    for i, other in ((0, 1), (ns - 1, ns - 2)):
        ring = rings[i]
        poly = ring[:, 1:]                                              # (y, z): the section planes are skewed in X
        area = 0.5 * np.sum(poly[:, 0] * np.roll(poly[:, 1], -1) - np.roll(poly[:, 0], -1) * poly[:, 1])
        order = list(range(n)) if area > 0 else list(range(n))[::-1]
        tris = [tuple(order[t] for t in tri) for tri in ear_clip(poly[order])]
        out_dir = ring.mean(axis=0) - rings[other].mean(axis=0)
        for tri in tris:
            p = ring[list(tri)]
            if np.cross(p[1] - p[0], p[2] - p[0]) @ out_dir < 0:
                tri = tri[::-1]
            caps.append(tuple(i * n + t for t in tri))
    mesh = trimesh.Trimesh(v, np.vstack([side, np.array(caps)]), process=False)
    if not mesh.is_watertight or not mesh.is_winding_consistent or mesh.volume <= 0:
        raise ValueError('loft: invalid solid')
    return mesh


def fit_limit(a, b):
    """Overlap allowed between two fitted parts: 1 cm3 plus 10 micrometres over the smaller surface (float32 and the
    faceted deck top; as in correct_21st_street_i465_review_3.py)."""
    return FIT + 1e-5 * min(a.area, b.area) / 2


def smoothstep(t):
    t = np.clip(t, 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def correct(dry_run=False):
    mp = BASE / 'model_manifest.json'
    raw_manifest = mp.read_bytes()
    manifest = json.loads(raw_manifest)
    if manifest.get(TAG_KEY) == TAG:
        print('Already corrected.')
        return
    if manifest.get('review_geometry_correction_3') != PREVIOUS_TAG or manifest.get('revision') != PREVIOUS_REVISION:
        raise ValueError('Run scripts/correct_21st_street_i465_review_3.py first (expected revision '
                         f'{PREVIOUS_REVISION}, found {manifest.get("revision")}).')
    path = BASE / 'model.glb'
    original = path.read_bytes()
    before = hashlib.sha256(original).hexdigest()
    if before != manifest['review_correction_record_3']['after_glb_sha256']:
        raise ValueError('model.glb differs from the output of the third correction')
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

    cache = {}

    def solid(pid):
        if pid not in cache:
            p = prim(pid)
            cache[pid] = trimesh.Trimesh(vertices=read(p['attributes']['POSITION']).astype(np.float64),
                                         faces=read(p['indices']).reshape(-1, 3), process=False)
        return cache[pid]

    def overlap(a, b):
        return float(boolean('intersection', [a, b]).volume)

    def near_ids(lo, hi, exclude=(), pad=0.002):
        return [p['id'] for p in manifest['parts'] if p['id'] not in exclude
                and np.all(np.array(p['bounds_m'])[0] <= np.asarray(hi) + pad)
                and np.all(np.array(p['bounds_m'])[1] >= np.asarray(lo) - pad)]

    r6 = lambda v: round(float(v), 6)
    old, new = {}, {}
    positions = {}                               # new float32 vertices for parts keeping their faces
    remeshed = {}                                # parapets: new vertices and faces
    deck = solid('deck')

    # ================================================================ S01: railings seated on the deck
    s01 = {}
    for side in (1, -1):
        rid, wid = f'parapet_{side}', f'sidewalk_{side}'
        rail, walk = old[rid], old[wid] = solid(rid), solid(wid)
        if len(rail.vertices) != 145 * 8 or len(walk.vertices) != 145 * 4 or not rail.is_watertight:
            raise ValueError(f'{rid}: expected 145 sections of 8 vertices (sidewalk 145 x 4)')
        r = rail.vertices.reshape(-1, 8, 3)
        w = walk.vertices.reshape(-1, 4, 3)
        ys = side * np.array([Y_WALK, Y_STEM_OUT, Y_STEM_OUT, Y_COPING, Y_COPING, Y_WALK, Y_WALK, Y_HEAD_IN])
        if np.abs(r[:, :, 1] - ys).max() > TOL:
            raise ValueError(f'{rid}: unexpected section (vertex Y)')
        face = np.abs(np.abs(w[:, :, 1]) - Y_WALK) < TOL
        if not np.all(face.sum(axis=1) == 2):
            raise ValueError(f'{wid}: expected two vertices per section on the railing face')
        wt = np.where(face, w[:, :, 2], -np.inf).max(axis=1)
        wb = np.where(face, w[:, :, 2], np.inf).min(axis=1)
        wx = np.array([w[i, face[i], 0].mean() for i in range(len(w))])
        if np.abs(wx - r[:, 0, 0]).max() > TOL:
            raise ValueError(f'{rid}: railing and sidewalk sections differ')
        if np.abs(r[:, 5, 2] - wt - 34 * IN).max() > 1e-4:
            raise ValueError(f'{rid}: expected the top 34 in above the sidewalk')
        step = np.sign(r[-1, 0, 0] - r[0, 0, 0])

        def deck_top(pts):
            q = pts[:, :2].copy()
            q[0, 0] += step * 1e-5                # end sections lie on the deck end edge
            q[-1, 0] -= step * 1e-5
            z = surface_z(deck, q)
            if np.isnan(z).any():
                raise ValueError(f'{rid}: base outside the deck')
            return z

        z0, z1 = deck_top(r[:, 0]), deck_top(r[:, 1])
        gap0, gap1 = r[:, 0, 2] - z0, r[:, 1, 2] - z1
        if not (0.03 < gap0.min() and gap1.max() < 0.05):
            raise ValueError(f'{rid}: expected the floating base (36.6-45.2 mm above the deck)')
        # the sidewalk follows the analytic profile, the deck mesh is faceted: 0.07-0.11 mm at the railing face
        if np.abs(wb - deck_top(np.c_[wx, np.full(len(wx), side * Y_WALK)])).max() > 5e-4:
            raise ValueError(f'{wid}: expected the sidewalk on the deck top')
        nr = np.zeros((len(r), 10, 3))
        nr[:, :8] = r
        nr[:, 0, 2], nr[:, 1, 2] = z0, z1
        nr[:, 8] = np.c_[r[:, 7, 0], r[:, 7, 1], wt]          # stem face 1 in behind the head, at the joint
        nr[:, 9] = np.c_[r[:, 0, 0], r[:, 0, 1], wt]          # sidewalk outer top edge (level construction joint)
        mesh = loft(nr)
        remeshed[rid] = mesh
        new[rid] = mesh
        # inner wedge before: where the sloped face meets the sidewalk surface
        t = (wt - r[:, 0, 2]) / (r[:, 7, 2] - r[:, 0, 2])
        wedge = np.abs(r[:, 0, 1] + t * (r[:, 7, 1] - r[:, 0, 1])) - Y_WALK
        s01[rid] = dict(base_gap_to_deck_mm_before=dict(sidewalk_face=[round(gap0.min() * 1e3, 3),
                                                                        round(gap0.max() * 1e3, 3)],
                                                         stem_exterior_face=[round(gap1.min() * 1e3, 3),
                                                                             round(gap1.max() * 1e3, 3)]),
                        sidewalk_face_air_wedge_mm_before=[round(wedge.min() * 1e3, 3), round(wedge.max() * 1e3, 3)],
                        height_above_sidewalk_in=round(float(np.mean(r[:, 5, 2] - wt)) / IN, 3),
                        joint_above_slab_top_at_exterior_face_in=None,
                        head_top_above_deck_at_stem_exterior_face_in=[
                            round(float((r[:, 4, 2] - z1).min()) / IN, 3), round(float((r[:, 4, 2] - z1).max()) / IN, 3)])
        zc = deck_top(np.c_[r[:, 3, 0], r[:, 3, 1] - side * 1e-6])
        s01[rid]['joint_above_slab_top_at_exterior_face_in'] = [round(float((wt - zc).min()) / IN, 3),
                                                                round(float((wt - zc).max()) / IN, 3)]
        print(f'{rid}: base {gap0.min() * 1e3:.2f}-{gap1.max() * 1e3:.2f} mm above the deck -> on it; '
              f'{rail.volume:.4f} -> {mesh.volume:.4f} m3')

    # ================================================================ S02: ornamental railing on sheet 60 stations
    s02 = {}
    ornaments = [pid for pid in parts if ORNAMENT.match(pid)]
    if len(ornaments) != 1656:
        raise ValueError(f'expected 1656 ornamental-railing parts, found {len(ornaments)}')
    for side, cfg in SIDES.items():
        rail = old[f'parapet_{side}']
        r = rail.vertices.reshape(-1, 8, 3)
        y_c = side * 7.5438                      # post / picket centre line (as modelled)
        tt = (abs(y_c) - Y_WALK) / (Y_COPING - Y_WALK)
        xt = r[:, 5, 0] + tt * (r[:, 4, 0] - r[:, 5, 0])
        zt = r[:, 5, 2] + tt * (r[:, 4, 2] - r[:, 5, 2])
        order = np.argsort(xt)
        top = lambda x, xt=xt[order], zt=zt[order]: np.interp(x, xt, zt)     # railing top on the post line
        x_old = np.array([solid(f'railpost_{side}_{k:02d}').bounds[:, 0].mean() for k in range(N_POSTS)])
        bays_old = np.diff(x_old)
        if not (np.allclose(bays_old[[0, -1]], BAY_STAR, atol=TOL) and np.allclose(bays_old[1:-1], bays_old[1], atol=TOL)):
            raise ValueError(f'{side}: expected 4\'-1 1/2" star bays and 30 equal bays')
        # parapet end planes on the post line (sheet 59: 117'-0 5/8" from CL Bent 2 along Line M)
        x_end = np.array([-HALF_FLOOR - TAN * y_c, HALF_FLOOR - TAN * y_c])
        if abs(x_old[0] - x_end[0]) > 1e-4 or abs(x_old[-1] - x_end[1]) > 1e-4:
            raise ValueError(f'{side}: expected the outer posts on the parapet ends')
        sta = np.zeros(N_POSTS)
        sta[16] = cfg['pier_sta']
        for k in range(1, 16):
            sta[16 - k] = sta[16] - k * cfg['west'] / FT
            sta[16 + k] = sta[16] + k * cfg['east'] / FT
        sta[0] = sta[1] - BAY_STAR / FT
        sta[32] = sta[31] + BAY_STAR / FT
        for k, label in cfg['labels'].items():
            label = LABEL_TYPO.get((side, k), label)
            if abs(sta[k] - label) > 0.0101:
                raise ValueError(f'{side}: post {k} at {sta[k]:.3f} does not reproduce the sheet 60 label {label}')
        x_new = (sta - STA0) * FT
        shift = x_new - x_old
        bays_new = np.diff(x_new)

        def put(pid, v):
            positions[pid] = v.astype('<f4')

        def rigid(pid, dx, x_ref):
            m = old.setdefault(pid, solid(pid))
            v = m.vertices.copy()
            v[:, 0] += dx
            v[:, 2] += top(x_ref + dx) - top(x_ref)
            put(pid, v)

        def stretch(pid, fmap):
            m = old.setdefault(pid, solid(pid))
            v = m.vertices.copy()
            xn = fmap(v[:, 0])
            v[:, 2] += top(xn) - top(v[:, 0])
            v[:, 0] = xn
            put(pid, v)

        counts = dict(posts=0, caps=0, base_plates=0, nuts=0, pickets=0, pipes=0, tubes=0, rings=0, arches=0,
                      star_rings=0, stars=0)
        for k in range(N_POSTS):
            rigid(f'railpost_{side}_{k:02d}', shift[k], x_old[k])
            rigid(f'railcap_{side}_{k:02d}', shift[k], x_old[k])
            rigid(f'railbase_{side}_{k:02d}', shift[k], x_old[k])
            counts['posts'] += 1
            counts['caps'] += 1
            counts['base_plates'] += 1
            for j in (1, 2, 3, 4):
                rigid(f'railbolt_{side}_{k:02d}_{j}', shift[k], x_old[k])
                counts['nuts'] += 1
            ring = f'railring_{side}_{k}'
            if ring in parts:
                rigid(ring, shift[k], x_old[k])
                counts['rings'] += 1
        for b in range(N_POSTS - 1):
            xa, xb, xa2, xb2 = x_old[b], x_old[b + 1], x_new[b], x_new[b + 1]
            lin = lambda x, xa=xa, xb=xb, xa2=xa2, xb2=xb2: xa2 + (x - xa) * (xb2 - xa2) / (xb - xa)
            for pid in (f'railpipe_{side}_{b:02d}', f'railtube_{side}_{b:02d}_lower', f'railtube_{side}_{b:02d}_upper'):
                stretch(pid, lin)
                counts['pipes' if 'pipe' in pid else 'tubes'] += 1
            pickets = sorted([pid for pid in parts if pid.startswith(f'picket_{side}_{b:02d}_')])
            n = len(pickets)
            for i, pid in enumerate(pickets, start=1):
                xc = solid(pid).bounds[:, 0].mean()
                if abs(xc - (xa + i * (xb - xa) / (n + 1))) > 1e-4:
                    raise ValueError(f'{pid}: expected equal picket spacing in its bay')
                xc_new = xa2 + i * (xb2 - xa2) / (n + 1)
                rigid(pid, xc_new - xc, xc)
                counts['pickets'] += 1
        for j, b in ((1, 0), (2, N_POSTS - 2)):              # star bays (outer bay at each end)
            mid_old, mid_new = (x_old[b] + x_old[b + 1]) / 2, (x_new[b] + x_new[b + 1]) / 2
            for pid in (f'starring_{side}_{j}', f'star_{side}_{j}'):
                c = solid(pid).bounds[:, 0].mean()
                if abs(c - mid_old) > 2e-3:
                    raise ValueError(f'{pid}: expected it centred in the star bay')
                rigid(pid, mid_new - mid_old, mid_old)
                counts['star_rings' if pid.startswith('starring') else 'stars'] += 1
        for pid in [p for p in parts if p.startswith(f'railarch_{side}_')]:
            a = int(pid.split('_')[2])
            b = a + 3
            lo_, hi_ = solid(pid).bounds[:, 0]
            if abs(lo_ - x_old[a]) > 0.03 or abs(hi_ - x_old[b]) > 0.03:
                raise ValueError(f'{pid}: expected a graphic spanning ring posts {a} and {b}')
            # rigid with the ring posts at both ends (zero slope there), smooth stretch in between
            fmap = lambda x, a=a, b=b: x + shift[a] + (shift[b] - shift[a]) * smoothstep(
                (x - x_old[a]) / (x_old[b] - x_old[a]))
            stretch(pid, fmap)
            counts['arches'] += 1
        # base plates and nuts against the parapet ends
        plates = {}
        for k in (0, N_POSTS - 1):
            pid = f'railbase_{side}_{k:02d}'
            res = {}
            for label, v in (('before', old[pid].vertices), ('after', positions[pid].astype(np.float64))):
                lo, hi = v.min(axis=0), v.max(axis=0)
                plate = Polygon([(lo[0], lo[1]), (hi[0], lo[1]), (hi[0], hi[1]), (lo[0], hi[1])])
                ends = Polygon([(-HALF_FLOOR - TAN * y, y) for y in side * np.array([Y_WALK, Y_COPING])]
                               + [(HALF_FLOOR - TAN * y, y) for y in side * np.array([Y_COPING, Y_WALK])])
                nuts = []
                for j in (1, 2, 3, 4):
                    q = f'railbolt_{side}_{k:02d}_{j}'
                    nv = old[q].vertices if label == 'before' else positions[q].astype(np.float64)
                    cx, cy = nv[:, 0].mean(), nv[:, 1].mean()
                    xe = (-HALF_FLOOR if k == 0 else HALF_FLOOR) - TAN * cy
                    nuts.append(round(float((cx - xe) * (1 if k == 0 else -1) * np.cos(SKEW)), 4))
                corners = [(-HALF_FLOOR if k == 0 else HALF_FLOOR) - TAN * yy for yy in (lo[1], hi[1])]
                edge = [lo[0] - corners[0], lo[0] - corners[1]] if k == 0 else [corners[0] - hi[0], corners[1] - hi[0]]
                res[label] = dict(plate_area_on_concrete_pct=round(100 * plate.intersection(ends).area / plate.area, 3),
                                  plate_edge_to_parapet_end_along_x_m=round(float(min(edge)), 4),
                                  nut_centres_inside_end_normal_m=nuts)
            if res['after']['plate_area_on_concrete_pct'] < 100 - 1e-6 or min(res['after']['nut_centres_inside_end_normal_m']) < 0.5:
                raise ValueError(f'{pid}: not on the concrete')
            plates[pid] = res
        s02[cfg['name']] = dict(
            post_stations_ft={str(k): round(float(sta[k]), 3) for k in (0, 1, 16, 31, 32)},
            post_x_m_before_after={str(k): [r6(x_old[k]), r6(x_new[k])] for k in (0, 1, 16, 31, 32)},
            bays_m_before=[r6(bays_old[0]), r6(bays_old[1]), r6(bays_old[-1])],
            bays_m_after=dict(star=r6(bays_new[0]), west=r6(bays_new[1]), east=r6(bays_new[-2]), star_east=r6(bays_new[-1])),
            outer_post_setback_from_parapet_end_on_post_line_m=[r6(x_new[0] - x_end[0]), r6(x_end[1] - x_new[-1])],
            star_bay_centre_minus_monument_EF_centre_ft=[round(float((sta[0] + sta[1]) / 2 - MONUMENT_EF_CENTRE[(side, 0)]), 3),
                                                         round(float((sta[31] + sta[32]) / 2 - MONUMENT_EF_CENTRE[(side, 1)]), 3)],
            terminal_plates=plates, moved=counts)
        print(f'{cfg["name"]}: posts {x_old[0]:.4f}/{x_old[-1]:.4f} -> {x_new[0]:.4f}/{x_new[-1]:.4f} m, bays '
              f'{bays_old[1]:.5f} -> {bays_new[1]:.5f}/{bays_new[-2]:.5f} m; {counts}')
    missing = set(ornaments) - set(positions)
    if missing:
        raise ValueError(f'ornamental parts not refitted: {sorted(missing)[:5]}')
    for pid, v in positions.items():
        new[pid] = trimesh.Trimesh(v.astype(np.float64), old[pid].faces, process=False)
        if not new[pid].is_watertight or new[pid].volume <= 0:
            raise ValueError(f'{pid}: invalid after the move')

    # ================================================================ verification on the new geometry
    verify = {}
    for side in (1, -1):
        rid, wid = f'parapet_{side}', f'sidewalk_{side}'
        rail, walk = new[rid], old[wid]
        nr = rail.vertices.reshape(-1, 10, 3)
        # (a) underside on the deck: dense samples across the stem, between and on the sections
        xs, ys = [], []
        for i in range(len(nr) - 1):
            for f in np.linspace(0.02, 0.98, 7):
                for g in np.linspace(0.02, 0.98, 7):
                    p0 = nr[i, 0] + g * (nr[i, 1] - nr[i, 0])
                    p1 = nr[i + 1, 0] + g * (nr[i + 1, 1] - nr[i + 1, 0])
                    q = p0 + f * (p1 - p0)
                    xs.append(q[0])
                    ys.append(q[1])
        xy = np.c_[xs, ys]
        gap = surface_z(rail, xy, top=False) - surface_z(deck, xy, top=True)
        if np.isnan(gap).any() or np.abs(gap).max() > 2e-4:
            raise ValueError(f'{rid}: underside not on the deck ({np.nanmin(gap):.2e}..{np.nanmax(gap):.2e} m)')
        # (b) sidewalk-side face below the joint covers the sidewalk's outer face
        w = walk.vertices.reshape(-1, 4, 3)
        face = np.abs(np.abs(w[:, :, 1]) - Y_WALK) < TOL
        pts = []
        for i in range(len(w) - 1):
            zb0, zt0 = np.sort(w[i, face[i], 2])
            zb1, zt1 = np.sort(w[i + 1, face[i + 1], 2])
            x0, x1 = w[i, face[i], 0].mean(), w[i + 1, face[i + 1], 0].mean()
            for f in np.linspace(0.05, 0.95, 5):
                for g in np.linspace(0.05, 0.95, 5):
                    zb, zt = zb0 + f * (zb1 - zb0), zt0 + f * (zt1 - zt0)
                    pts.append((x0 + f * (x1 - x0), zb + g * (zt - zb)))
        pts = np.array(pts)
        covered = on_plane_area(pts, rail, side * Y_WALK)
        if not covered.all():
            raise ValueError(f'{rid}: sidewalk face not closed ({(~covered).sum()} of {len(pts)} samples open)')
        # (c) overlaps with the deck, the sidewalk and every other neighbour, old against new
        rows = {}
        lo = np.minimum(old[rid].bounds[0], rail.bounds[0])
        hi = np.maximum(old[rid].bounds[1], rail.bounds[1])
        for qid in near_ids(lo, hi, exclude={rid} | set(ornaments)):
            q = solid(qid)
            if not q.is_watertight:
                continue
            b_, a_ = overlap(old[rid], q), overlap(rail, q)
            rows[f'{rid}_x_{qid}'] = [r6(b_), r6(a_)]
            if a_ > b_ + fit_limit(rail, q):
                raise ValueError(f'{rid} x {qid}: overlap {b_:.2e} -> {a_:.2e} m3')
        nr_old = old[rid].vertices.reshape(-1, 8, 3)
        verify[rid] = dict(underside_minus_deck_top_m=[r6(gap.min()), r6(gap.max())], underside_samples=len(gap),
                           sidewalk_face_samples_closed=f'{int(covered.sum())}/{len(pts)}',
                           head_and_top_unchanged=bool(np.array_equal(nr[:, 2:8], nr_old[:, 2:8])),
                           overlaps_m3_before_after=rows)
        print(f'{rid}: underside - deck {gap.min() * 1e3:+.4f}..{gap.max() * 1e3:+.4f} mm ({len(gap)} samples); '
              f'sidewalk face closed {covered.sum()}/{len(pts)}; overlaps {rows}')

    # moved railing parts against their neighbours (old pairs against new pairs), parapets included. Base plate
    # against railing top is checked separately: the level 16 x 9 in plates sit on the local grade at the post centre.
    ids = [p['id'] for p in manifest['parts']]
    box = np.array([p['bounds_m'] for p in manifest['parts']], dtype=np.float64)
    for i, pid in enumerate(ids):
        if pid in new:
            box[i, 0] = np.minimum(box[i, 0], new[pid].bounds[0])
            box[i, 1] = np.maximum(box[i, 1], new[pid].bounds[1])
    pairs = set()
    for i, pid in enumerate(ids):
        if pid not in positions:
            continue
        hit = np.all(box[:, 0] <= box[i, 1] + 0.002, axis=1) & np.all(box[:, 1] >= box[i, 0] - 0.002, axis=1)
        for j in np.nonzero(hit)[0]:
            if j != i:
                pairs.add(tuple(sorted((pid, ids[j]))))
    grown, clashes, worst = {}, {}, (0.0, None)
    for pid, qid in sorted(pairs):
        if (pid.startswith('railbase_') and qid in ('parapet_1', 'parapet_-1')) or \
                (qid.startswith('railbase_') and pid in ('parapet_1', 'parapet_-1')):
            continue
        p_old = old[pid] if pid in old else solid(pid)
        q_old = old[qid] if qid in old else solid(qid)
        p_new, q_new = new.get(pid, p_old), new.get(qid, q_old)
        b_, a_ = overlap(p_old, q_old), overlap(p_new, q_new)
        if a_ - b_ > worst[0]:
            worst = (a_ - b_, f'{pid}_x_{qid}', b_, a_)
        if b_ < 1e-9 and a_ > 1e-7:
            clashes[f'{pid}_x_{qid}'] = [b_, a_]
        elif a_ > b_ + max(FIT, 0.25 * b_):
            grown[f'{pid}_x_{qid}'] = [b_, a_]
    if grown or clashes:
        raise ValueError(f'overlaps grew: {dict(list(grown.items())[:10])}; new clashes {dict(list(clashes.items())[:10])}')
    seats = {}
    for side in (1, -1):
        rail = new[f'parapet_{side}']
        for k in range(N_POSTS):
            pid = f'railbase_{side}_{k:02d}'
            v = new[pid].vertices
            lo, hi = v.min(axis=0), v.max(axis=0)
            xc, yc = (lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2
            pts = np.array([(xc, yc), (lo[0], lo[1]), (lo[0], hi[1]), (hi[0], lo[1]), (hi[0], hi[1])])
            d = lo[2] - surface_z(rail, pts)
            if abs(d[0]) > 2e-4 or np.abs(d).max() > 0.004:
                raise ValueError(f'{pid}: not seated on the railing top ({d})')
            seats[pid] = [r6(d[0]), r6(np.abs(d[1:]).max())]
    seat_max = max(v[1] for v in seats.values())
    print(f'{len(pairs)} railing neighbour pairs checked; largest overlap growth {worst[0]:.2e} m3 ({worst[1]}); '
          f'plates seated at centre within {max(abs(v[0]) for v in seats.values()) * 1e3:.3f} mm, corners within '
          f'{seat_max * 1e3:.2f} mm of the sloped top')
    railing_checks = dict(neighbour_pairs_checked=len(pairs), largest_overlap_growth_m3=[r6(worst[0]), worst[1]],
                          plate_bottom_minus_railing_top_at_centre_max_mm=round(max(abs(v[0]) for v in seats.values()) * 1e3, 4),
                          plate_corner_to_sloped_top_max_mm=round(seat_max * 1e3, 3))

    # ---------------------------------------------------------------- write meshes
    changed_ids = sorted(new)
    for pid in changed_ids:
        p = prim(pid)
        if pid in positions:
            p['attributes']['POSITION'] = append(positions[pid], 'VEC3', 5126)
            stored = new[pid]
        else:
            mesh = remeshed[pid]
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
    for side in (1, -1):
        rid = f'parapet_{side}'
        p = parts[rid]
        nr = new[rid].vertices.reshape(-1, 10, 3)
        a, b = old[rid].volume, new[rid].volume
        p['basis'] = 'Dimensioned main profile; seated on the deck; simplified recess'
        p['dimensions'].update(overall_height_in=round(float(np.mean(nr[:, 5, 2] - nr[:, 0, 2])) / IN, 2),
                               height_above_deck_at_stem_exterior_face_in=round(
                                   float(np.mean(nr[:, 4, 2] - nr[:, 1, 2])) / IN, 2),
                               stem_face_behind_head_in=1.0,
                               construction_joint='level, at the sidewalk surface')
        p['note'] += (' Base extended down onto the deck top (2 % cross fall; it had floated 36.6-45.2 mm above it) '
                      'and the sidewalk-side face rebuilt as drawn on sheet 59: flush with the sidewalk\'s outer face '
                      'below the level construction joint at the sidewalk surface, vertical 1 in behind the head above '
                      f'it ({b - a:+.3f} m3). Head, top and exterior face unchanged.')
    for pid in sorted(positions):
        p = parts[pid]
        if pid.startswith('railpost_'):
            p['basis'] = 'Dimensioned section; post stations from sheet 60'
        p['pdf_pages'] = sorted(set(p.get('pdf_pages', [])) | {60})
        p['note'] = (p.get('note', '') + ' Refitted to the sheet 60 post stations (outer star posts 0.75-0.82 m '
                     'inside the parapet ends; bays 110\'-2 3/4" / 15 and 110\'-6" / 15 either side of the CL Bent 2 '
                     'post); height above the railing top kept.').strip()
    for pid in changed_ids:
        meshes[pid].setdefault('extras', {}).update(parts[pid])

    b = np.array([q['bounds_m'] for q in manifest['parts']])
    lo, hi = b[:, 0].min(axis=0), b[:, 1].max(axis=0)
    manifest['bounds_m'] = [lo.round(6).tolist(), hi.round(6).tolist()]
    manifest['glb_bounds_m'] = [[round(lo[0], 6), round(lo[2], 6), round(-hi[1], 6)],
                                [round(hi[0], 6), round(hi[2], 6), round(-lo[1], 6)]]
    for d in manifest['detail_coverage']:
        if d['feature'] == 'Sidewalks and concrete parapets':
            d['detail'] += (' Parapets seated on the deck top; sidewalk-side face flush with the sidewalk below the '
                            'level construction joint and 1 in behind the head above it (sheet 59).')
        elif d['feature'] == 'Ornamental railings':
            d['detail'] = d['detail'].replace('Shop bay positions/arc radii simplified.', 'Graphic arc radii simplified.')
            d['detail'] += (' Bridge posts on the sheet 60 stations: outer star posts 0.75-0.82 m inside the parapet '
                            'ends, 4 ft 1-1/2 in star bays, 15 bays totalling 110 ft 2-3/4 in and 15 totalling 110 ft 6 '
                            'in either side of the CL Bent 2 post. The approach-barrier bays beyond the star posts are outside '
                            'the model; the rails end capped at the outer star posts.')
            d['sources'] = sorted(set(d['sources']) | {60})
    manifest[TAG_KEY] = TAG
    manifest['revision'] = REVISION

    gltf['buffers'][0]['byteLength'] = len(binary)
    while len(binary) % 4:
        binary.append(0)
    encoded = json.dumps(gltf, ensure_ascii=True, separators=(',', ':')).encode()
    encoded += b' ' * ((-len(encoded)) % 4)
    out = (struct.pack('<III', 0x46546c67, 2, 28 + len(encoded) + len(binary)) +
           struct.pack('<II', len(encoded), 0x4e4f534a) + encoded + struct.pack('<II', len(binary), 0x004e4942) + binary)
    manifest[RECORD_KEY] = dict(
        source_pdf_pages=[56, 59, 60, 61, 62, 72], printed_sheets=[56, 59, 60, 61, 62, 73],
        previous_revision=PREVIOUS_REVISION,
        resolved=[
            dict(id='S01', finding='Both concrete railings floated 36.65-45.23 mm above the deck top along 71.355 m.',
                 verdict='RESOLVE', parts=['parapet_1', 'parapet_-1'],
                 correction='Each section rebuilt with 10 vertices: base on the deck top (2 % cross fall, local '
                            'profile); sidewalk-side face flush with the sidewalk outer face (Y = +/-24 ft) up to the '
                            'level construction joint at the sidewalk surface, then vertical 1 in behind the head up '
                            'to the head chamfer. Head, top (34 in above the sidewalk) and exterior face unchanged; '
                            'the former 7 mm air wedge between railing and sidewalk is closed.',
                 sources='sheet 59 (PDF 59) TYPICAL SECTION BARRIER DETAILS (8 in + 2\'-2" above the level '
                         'construction joint, 11 1/4" below it to the slab top at the exterior face, 1 in head step); '
                         'sheet 56 (PDF 56) 36 ft roadway, 6 ft sidewalks, 51 ft out to out',
                 measurements=s01, verification=verify),
        ],
        decisions=[
            dict(id='S02', finding='The four terminal ornamental-railing base plates were centred on the parapet end '
                                   'planes (50 % of each plate and two anchor nuts over air).',
                 verdict='DECIDE', parts=sorted(positions),
                 decision='All 33 bridge posts per side on the sheet 60 stations, chained from the CL Bent 2 post with '
                          'the dimensioned totals 110\'-2 3/4" (15 bays of 2.239857 m) and 110\'-6" (15 bays of '
                          '2.245360 m) and the 4\'-1 1/2" star bays. Outer star posts 0.75-0.82 m inside the parapet '
                          'ends; every base plate and nut on concrete.',
                 reasoning='Sheet 60 dimensions every post. Its printed spacings are rounded to 1/8 in (15 x 7\'-4 1/8" '
                           '= 110\'-1 7/8" and 15 x 7\'-4 3/8" = 110\'-5 5/8", against the printed totals 110\'-2 3/4" '
                           'and 110\'-6"); the totals close on the station labels within 0.01 ft, so bay = total / 15. '
                           'The south '
                           '11+97.62 label contradicts both its 4\'-1 1/2" bay from 11+93.74 and the 110\'-6" chain '
                           'from 13+08.37 (both give 11+97.87) and is read as a typo. Sheet 61 notes the 4\'-1 1/2" '
                           'bay "Center on Monument at End Bents"; the sheet 73 monument E/F stations put the '
                           'monument centres 0.43-0.53 ft from the sheet 60 star-bay centres, and centring on them '
                           'would break the dimensioned bay chain, so the explicit sheet 60 stations control. The '
                           'pier post stations 12+91.79 / 13+08.37 are CL Bent 2 at the coping faces (their mean is '
                           'the CL Bent 2 station 13+00.08), so the pier post sits 0.076 m from where CL Bent 2 '
                           'crosses the post line.',
                 rejected_reading='Outer star posts on the parapet ends with 30 equal 7\'-6 3/8" bays (previous model); '
                                  'star bays centred on the sheet 73 monument E/F stations.',
                 sources='sheet 60 (PDF 60) NORTH / SOUTH RAILING ELEVATION; sheet 61 (PDF 61) SIDEWALK ELEVATION OF '
                         'RAILING, BASE PLATE AND ANCHOR BOLT DETAILS (16 x 9 in plate, nuts 5 1/2 in either side of '
                         'the post); sheet 62 (PDF 62) END BENT MONUMENT ORNAMENTAL DETAIL; sheet 73 (PDF 72) table '
                         'of monument stations; sheet 59 (PDF 59) 117\'-0 5/8" CL Bent 2 to end of bridge floor',
                 method='Posts, caps, base plates, nuts, rings, star rings, stars and pickets moved rigidly (15 '
                        'pickets per bay, equally spaced as before); pipe and tube rails re-spanned post to post; '
                        'flowing graphics moved with their ring posts (rigid at the rings, smooth stretch between). '
                        'Each part keeps its height above the railing top at its new station.',
                 measurements=s02, verification=railing_checks),
        ],
        kept_deviations=[],
        changed_parts=changed_ids, added_parts=[], removed_parts=[],
        before_glb_sha256=before, after_glb_sha256=hashlib.sha256(out).hexdigest(),
        before_manifest_sha256=hashlib.sha256(raw_manifest).hexdigest())
    record = manifest[RECORD_KEY]
    print(f'{len(changed_ids)} parts changed')
    if dry_run:
        print(json.dumps(dict(s01=s01, s02=s02, verify={k: {kk: vv for kk, vv in v.items()
                                                             if kk != 'overlaps_m3_before_after'}
                                                         for k, v in verify.items()}), indent=1)[:8000])
        print('Dry run, nothing written.')
        return
    backup = ROOT / 'data/fem_research'
    backup.mkdir(exist_ok=True)
    (backup / f'{BID}_before_3d_review.glb').write_bytes(original)
    (backup / f'{BID}_manifest_before_3d_review.json').write_bytes(raw_manifest)
    path.write_bytes(out)
    text = json.dumps(manifest, ensure_ascii=False, indent=2) + '\n'
    if b'\r\n' in raw_manifest:                    # keep the file's existing CRLF line endings
        text = text.replace('\n', '\r\n')
    mp.write_bytes(text.encode('utf-8'))
    print(json.dumps({k: v for k, v in record.items() if k not in ('resolved', 'decisions', 'changed_parts')}))


if __name__ == '__main__':
    correct(dry_run='--dry-run' in sys.argv)

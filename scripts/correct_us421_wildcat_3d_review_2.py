"""Fifth correction of US 421 over South Fork Wildcat Creek (us421-wildcat), from the second 3D placement review:
the stringer end framing (S05). Runs after scripts/correct_us421_wildcat_3d_review.py and keeps every GLB buffer it does
not replace.

    python scripts/correct_us421_wildcat_3d_review_2.py [--base DIR] [--backup DIR]

Source: drawings.pdf (INDOT 2020 rehabilitation plans, 30 sheets); printed sheet numbers equal PDF page numbers.
Native axes: X = station from Sta. 42+54.00, Y = transverse (+Y = left of increasing station = X-truss side), Z =
elevation - 778 ft; GLB (X, Z, -Y).

S05 (minor) RESOLVED - stringer end framing cleats. Every stringer ended at the floor-beam flange tips, 5 11/16 in short
  of the floor-beam web, and its 'cleats' were two copies of one 3 1/2 x 3 1/2 x 3/8 in angle, 14 in long, translated
  6 in apart (not mirrored): the outstanding legs stood in the flange-tip plane, the other legs lay 61 mm and 72 mm off
  the stringer web, and the top was 26.8-27.0 mm (lines 1 and 9) / 4.7-4.9 mm (lines 2 and 8) below the floor-beam
  flange or only touched its tip edge (inner lines). 12 bolts (3/4 in) per stringer ran through single angle legs, 16-60
  mm from the floor beams on lines 1, 2, 3, 7, 8 and 9. No cleat reached the floor-beam web.
  The plans draw the existing stringer framing twice, at 1 1/2 in = 1 ft: sheet 17 Section A-A (FB0) and the sheet 18
  temporary truss support retrofit detail (FB1). Both show two angles back to back on the stringer web with their
  outstanding legs on the floor-beam web, 9 in long (81 pt), outstanding legs 4 in (36 pt), 3/8 in thick (3.4 pt),
  three fasteners per outstanding leg at 3 in pitch with 1 1/2 in end distances, 2 3/4 in from the heel (24.6-24.9 pt),
  drawn with the 7/8 in fastener symbol (7.9 pt circles, as the 7/8 in bolts beside them); the angle top is 0.91 in
  (sheet 17) and 1.10 in (sheet 18) below the floor-beam top-flange underside (1 in used). The sheet 16 plan marks the
  angles on both faces of each floor-beam web. Each stringer end is refitted to that detail:
  - stringer web carried from its bottom flange to the floor-beam top-flange underside and run to the floor-beam web
    (fitted: the end setback and cope are not drawn); both flanges stay cut back at the floor-beam flange tips;
  - two L 4 x 4 x 3/8 x 9 in angles (web leg taken equal to the drawn 4 in outstanding leg, since the sheets show it
    only edge-on), web legs on the two faces of the stringer web, outstanding legs on the floor-beam web face;
  - fasteners: 7/8 in, three per outstanding leg through the floor-beam web (common to the two stringers framing into
    an intermediate floor beam, so each is modelled once), and three through both web legs and the stringer web, in
    the same rows and at the drawn 2 3/4 in gauge (the web-leg fasteners are not drawn).
  At FB0 and FB9 the outer stringer lines (1 and 9) keep only the inside angle: the outside angle's 4 in outstanding
  leg would lie on the 5 in web leg of the floor-beam end connection angle and its nuts (known deviation
  outer-stringer-end-framing-fb0-fb9).
  The 90 'floor beam transverse web stiffeners' FB*_stiff* are removed. They were inferred plates (no sheet shows
  them), each two overlapping 4 in boxes straddling the floor-beam web in the plane of a stringer web, i.e. exactly where
  the drawn framing puts the stringer web and its angles; sheets 17 (Section A-A) and 18 draw the floor-beam web at the
  stringer lines with the framing angles only.

Changed (243): 81 stringer_j_i, 81 stringer_j_i_cleats, 81 stringer_j_i_bolts. Removed (90): FB0_stiff0 .. FB9_stiff8.
Added: none. Other meshes, accessors and the original binary data are kept byte for byte (replaced accessors stay
unreferenced).

Requires numpy, trimesh and manifold3d, plus the four earlier us421_wildcat correction scripts.
"""
import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import correct_us421_wildcat_3d_review as fourth  # noqa: E402

third = fourth.third
BID = 'us421-wildcat'
BASE = ROOT / 'data/bridges' / BID
BACKUP = ROOT / 'data/fem_research'
TAG_KEY = 'review_correction_3d_2'
TAG = 'stringer-framing-angles-on-floor-beam-web'
RECORD_KEY = 'review_correction_record_3d_2'
REVISION = '1.5-3d-review-2'
PREVIOUS_TAG_KEY, PREVIOUS_TAG, PREVIOUS_REVISION = fourth.TAG_KEY, fourth.TAG, fourth.REVISION
EXPECTED_GLB_SHA256 = '2e7874eec8dbc87bead1576d01b34923ce148103ffd6310d5decae5d6b4d6c72'   # revision 1.4 output
IN = third.IN
FB_WEB_T = 0.625 * IN          # 36WF150 web (model)
STRINGER_WEB_T = 0.375 * IN    # stringer web (model)
ANGLE_T = 0.375 * IN           # sheets 17 Section A-A / 18: 3.4 pt at 9 pt/in
ANGLE_LEG = 4 * IN             # outstanding leg 36 pt (sheets 17, 18); web leg taken equal
ANGLE_LEN = 9 * IN             # 81 pt (sheets 17, 18)
ANGLE_TOP_DROP = 1 * IN        # below the floor-beam top-flange underside: 0.91 in (sheet 17), 1.10 in (sheet 18)
ROW_END, ROW_PITCH, ROWS = 1.5 * IN, 3 * IN, 3   # 13.5 pt end distances, 27 pt pitch (sheets 17, 18)
GAUGE = 2.75 * IN              # fastener line from the heel, 24.6-24.9 pt (sheets 17, 18)
OUTER_LINES = {0: -1, 8: 1}    # stringer line -> side of its truss (-Y: Y truss, +Y: X truss)
SINGLE_ANGLE = {(0, 0, 0), (8, 0, 0), (0, 8, 9), (8, 8, 9)}      # (line, panel, floor beam): outside angle omitted
TOL = 2e-6


def box_overlaps(a, b, pad=1e-6):
    return not (np.any(a.bounds[0] > b.bounds[1] + pad) or np.any(b.bounds[0] > a.bounds[1] + pad))


def solid_from_polygons(polygons):
    """Closed solid from planar convex polygons (fan triangulated from their first vertex; vertices shared exactly)."""
    index, verts, faces = {}, [], []
    for poly in polygons:
        ids = []
        for p in poly:
            key = tuple(float(c) for c in p)
            if key not in index:
                index[key] = len(verts)
                verts.append(key)
            ids.append(index[key])
        for k in range(1, len(ids) - 1):
            faces.append((ids[0], ids[k], ids[k + 1]))
    mesh = trimesh.Trimesh(np.array(verts), np.array(faces), process=False)
    trimesh.repair.fix_winding(mesh)
    trimesh.repair.fix_inversion(mesh)
    return mesh


def angle_solid(face, into, heel_y, s, z0, z1):
    """L 4 x 4 x 3/8: heel at (face, heel_y); outstanding leg on the plane x = face, web leg on y = heel_y."""
    X = lambda u: face + into * u
    Y = lambda w: heel_y + s * w
    poly = [(X(0), Y(0)), (X(ANGLE_LEG), Y(0)), (X(ANGLE_LEG), Y(ANGLE_T)), (X(ANGLE_T), Y(ANGLE_T)),
            (X(ANGLE_T), Y(ANGLE_LEG)), (X(0), Y(ANGLE_LEG))]
    bottom = [(x, y, z0) for x, y in poly]
    top = [(x, y, z1) for x, y in poly]
    polys = [[bottom[0], bottom[1], bottom[2], bottom[3]], [bottom[0], bottom[3], bottom[4], bottom[5]],
             [top[0], top[1], top[2], top[3]], [top[0], top[3], top[4], top[5]]]
    for k in range(6):
        polys.append([bottom[k], bottom[(k + 1) % 6], top[(k + 1) % 6], top[k]])
    m = solid_from_polygons(polys)
    return m


def rotation_to(direction):
    """Rotation about Z taking +X to the given +-X / +-Y unit direction (determinant +1)."""
    c, s = {(1, 0): (1, 0), (-1, 0): (-1, 0), (0, 1): (0, 1), (0, -1): (0, -1)}[tuple(int(v) for v in direction[:2])]
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]], float)


def correct(base=BASE, backup=BACKUP):
    mp = base / 'model_manifest.json'
    raw_manifest = mp.read_bytes()
    manifest = json.loads(raw_manifest)
    if manifest.get(TAG_KEY) == TAG:
        print('Already corrected.')
        return
    path = base / 'model.glb'
    original = path.read_bytes()
    before = hashlib.sha256(original).hexdigest()

    def expect(ok, what):
        if not ok:
            raise ValueError(f'{BID}: unexpected starting model ({what})')

    expect(manifest.get(PREVIOUS_TAG_KEY) == PREVIOUS_TAG and manifest.get('revision') == PREVIOUS_REVISION,
           f'run scripts/correct_us421_wildcat_3d_review.py first (revision {manifest.get("revision")})')
    expect(TAG_KEY not in manifest, f'{TAG_KEY} already holds {manifest.get(TAG_KEY)}')
    expect(before == EXPECTED_GLB_SHA256 == manifest['review_correction_record_3d']['after_glb_sha256'],
           f'model.glb SHA-256 {before} is not the revision 1.4 output')
    expect([d['id'] for d in manifest.get('known_deviations', [])] == ['tfc-transition-envelope'], 'known deviations')

    length = struct.unpack_from('<I', original, 12)[0]
    gltf = json.loads(original[20:20 + length])
    binary = bytearray(original[28 + length:])
    parts = {p['id']: p for p in manifest['parts']}
    meshes = {m['name']: m for m in gltf['meshes']}
    world = gltf['nodes'][0]
    expect(set(parts) == set(meshes) and len(meshes) == 1052, 'part list')
    expect(world.get('name') == 'world' and len(world['children']) == 1052 and gltf['scenes'] == [{'nodes': [0]}],
           'scene nodes')
    expect(not any(k in n for n in gltf['nodes'] for k in ('matrix', 'rotation', 'translation', 'scale')),
           'node transforms')
    expect(all(len(m['primitives']) == 1 for m in gltf['meshes']), 'one primitive per mesh')

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

    cache = {}

    def native(pid):
        if pid not in cache:
            prim = meshes[pid]['primitives'][0]
            v = third.to_native(read(prim['attributes']['POSITION']).astype(np.float64))
            cache[pid] = trimesh.Trimesh(v, read(prim['indices']).reshape(-1, 3), process=False)
        return cache[pid]

    def stored(mesh):
        """The solid as the GLB stores it (float32 positions)."""
        return trimesh.Trimesh(third.to_native(third.to_glb(mesh.vertices).astype('<f4').astype(np.float64)),
                               mesh.faces, process=False)

    new = {}

    def write_solid(pid, mesh):
        prim = meshes[pid]['primitives'][0]
        color = read(prim['attributes']['COLOR_0'])[0]
        prim['attributes'] = {'POSITION': append(third.to_glb(mesh.vertices).astype('<f4'), 'VEC3', 5126),
                              'COLOR_0': append(np.tile(color, (len(mesh.vertices), 1)).astype('u1'), 'VEC4', 5121)}
        gltf['accessors'][prim['attributes']['COLOR_0']]['normalized'] = True
        prim['indices'] = append(mesh.faces.reshape(-1, 1).astype('<u4'), 'SCALAR', 5125)
        new[pid] = stored(mesh)

    def check_bodies(pid, mesh, count=None):
        bs = fourth.bodies(mesh)
        for b in bs:
            w = b.copy()
            w.merge_vertices(digits_vertex=5)
            expect(w.is_watertight and w.is_winding_consistent and b.volume > 0, f'{pid}: body not a closed solid')
        if count is not None:
            expect(len(bs) == count, f'{pid}: {len(bs)} bodies, expected {count}')

    def edge_points(mesh, step=0.002):
        """Vertices plus points every 2 mm along every edge (so edge-on-face contacts are found)."""
        e = mesh.vertices[mesh.edges_unique]
        n = np.maximum(1, np.ceil(np.linalg.norm(e[:, 1] - e[:, 0], axis=1) / step).astype(int))
        pts = [mesh.vertices]
        for (a, b), k in zip(e, n):
            t = np.linspace(0, 1, k + 1)[1:-1, None]
            if len(t):
                pts.append(a + t * (b - a))
        return np.vstack(pts)

    def min_distance(a, b, margin=0.25):
        """Smallest distance between two meshes, from vertices and edge points of each (near the other) to the
        other's surface."""
        best = np.inf
        for p, q in ((a, b), (b, a)):
            pts = edge_points(p)
            pts = pts[np.all((pts > q.bounds[0] - margin) & (pts < q.bounds[1] + margin), axis=1)]
            for chunk in np.array_split(pts, max(1, len(pts) // 2000)):
                if len(chunk):
                    best = min(best, float(trimesh.proximity.closest_point(q, chunk)[1].min()))
        expect(np.isfinite(best), 'meshes more than 0.25 m apart')
        return best

    values = {}

    # ---------------------------------------------------------------- floor beams.
    fbs = {}
    for k in range(10):
        fb = native(f'floorbeam{k}')
        fx = np.unique(fb.vertices[:, 0])
        fz = np.unique(fb.vertices[:, 2])
        expect(len(fb.vertices) == 24 and len(fx) == 4 and len(fz) == 4, f'floorbeam{k}: not a level I prism')
        expect(abs(fx[2] - fx[1] - FB_WEB_T) < 2e-5 and abs(fx[3] - fx[0] - 12 * IN) < 2e-5, f'floorbeam{k}: section')
        fbs[k] = dict(f0=float(fx[0]), w0=float(fx[1]), w1=float(fx[2]), f1=float(fx[3]), zc=float(fz[2]),
                      zbf=float(fz[1]))

    # ---------------------------------------------------------------- template 7/8 in bolt (FB connection bolts).
    comps = fourth.bodies(native('FB1_connection_X_bolts'))
    z_low = min(c.bounds.mean(axis=0)[2] for c in comps)
    first = [c for c in comps if abs(c.bounds.mean(axis=0)[2] - z_low) < 1e-3]
    shank = [c for c in first if len(c.vertices) == 26]
    washer = [c for c in first if len(c.vertices) == 34]
    hexes = sorted([c for c in first if len(c.vertices) == 14], key=lambda c: c.bounds[0][0])
    expect(len(shank) == 1 and len(washer) == 1 and len(hexes) == 2, 'FB1_connection_X_bolts: template bolt')
    shank, washer, head, nut = shank[0], washer[0], hexes[0], hexes[1]
    expect(abs(shank.extents[1] - 0.875 * IN) < 1e-4, 'template bolt is not 7/8 in')
    axis = shank.bounds.mean(axis=0)
    u0, L0 = shank.bounds[0][0], shank.extents[0]
    expect(abs(head.bounds[1][0] - u0) < 1e-6 and abs(washer.bounds[0][0] - u0 - L0) < 1e-6 and
           abs(nut.bounds[0][0] - washer.bounds[1][0]) < 1e-6, 'template bolt layout')

    def local(c):
        return c.vertices - np.array([u0, axis[1], axis[2]])
    t_head, t_shank, t_washer, t_nut = local(head), local(shank), local(washer), local(nut)
    t_washer[:, 0] -= L0
    t_nut[:, 0] -= L0

    def bolt(start, direction, grip):
        """Head outside the ply face at `start`, shank over the grip along `direction`, washer and nut beyond."""
        rot = rotation_to(np.asarray(direction, float))
        out = []
        for tv, src, kind in ((t_head, head, 'head'), (t_shank, shank, 'shank'), (t_washer, washer, 'washer'),
                              (t_nut, nut, 'nut')):
            v = tv.copy()
            if kind == 'shank':
                v[:, 0] = v[:, 0] * grip / L0
            elif kind in ('washer', 'nut'):
                v[:, 0] += grip
            out.append(trimesh.Trimesh(v @ rot.T + start, src.faces, process=False))
        return out

    # ---------------------------------------------------------------- before: cleat / bolt gaps.
    gaps_before = {}
    for j in range(9):
        for i in range(9):
            c, b = native(f'stringer_{j}_{i}_cleats'), native(f'stringer_{j}_{i}_bolts')
            gaps_before[(j, i)] = dict(
                cleats_mm=[round(min_distance(c, native(f'floorbeam{k}')) * 1000, 3) for k in (i, i + 1)],
                bolts_mm=[round(min_distance(b, native(f'floorbeam{k}')) * 1000, 3) for k in (i, i + 1)])

    # ---------------------------------------------------------------- S05: stringers, cleats, bolts.
    profile_ids = {(0, 0): 0, (3, 0): 1, (3, 1): 2, (2, 1): 3, (2, 2): 4, (3, 2): 5, (3, 3): 6, (0, 3): 7,
                   (0, 2): 8, (1, 2): 9, (1, 1): 10, (0, 1): 11}          # (y class, z class) -> I-profile point
    s05, single = {}, []
    for j in range(9):
        for i in range(9):
            sid = f'stringer_{j}_{i}'
            S = native(sid)
            v = S.vertices
            expect(len(v) == 24 and len(S.faces) == 44, f'{sid}: not the I prism')
            ys = np.unique(v[:, 1])
            expect(len(ys) == 4 and abs(ys[2] - ys[1] - STRINGER_WEB_T) < 2e-5 and abs(ys[3] - ys[0] - 7.5 * IN) < 2e-5,
                   f'{sid}: section')
            yj = float((ys[1] + ys[2]) / 2)
            mid = v[:, 0].mean()
            P = {}
            for end, sel in (('s', v[:, 0] < mid), ('e', v[:, 0] > mid)):
                pts = v[sel]
                zs = np.unique(np.round(pts[:, 2], 7))
                expect(len(pts) == 12 and len(zs) == 4, f'{sid}: end profile')
                prof = [None] * 12
                for p in pts:
                    yc = int(np.argmin(np.abs(ys - p[1])))
                    zc_ = int(np.argmin(np.abs(zs - p[2])))
                    prof[profile_ids[(yc, zc_)]] = p.copy()
                expect(all(p is not None for p in prof), f'{sid}: profile points')
                P[end] = prof
            fs, fe = fbs[i], fbs[i + 1]
            expect(abs(P['s'][3][0] - fs['f1']) < 2e-4 and abs(P['e'][3][0] - fe['f0']) < 2e-4,   # ends square to the grade
                   f'{sid}: ends not at the floor-beam flange tips')
            ends = {'s': dict(fb=i, face=fs['w1'], zc=fs['zc'], into=1.0),
                    'e': dict(fb=i + 1, face=fe['w0'], zc=fe['zc'], into=-1.0)}

            # stringer: web carried from the bottom flange to the floor-beam top-flange underside, run to the web
            polys = []
            Ps, Pe = P['s'], P['e']
            for a, b in ((0, 1), (1, 2), (2, 3), (4, 5), (5, 6), (6, 7), (7, 8), (8, 9), (10, 11), (11, 0)):
                polys.append([Ps[a], Ps[b], Pe[b], Pe[a]])
            ext = {}
            for end, info in ends.items():
                Pp, Qq = P[end], P['e' if end == 's' else 's']
                zc = info['zc']
                e = {}
                for k_bot, k_top in ((3, 4), (10, 9)):
                    expect(Pp[k_bot][2] + 0.05 < zc < Pp[k_top][2] - 1e-3, f'{sid}: cope height')
                    t = (info['face'] - Pp[k_bot][0]) / (Qq[k_bot][0] - Pp[k_bot][0])
                    e[('F', k_bot)] = Pp[k_bot] + t * (Qq[k_bot] - Pp[k_bot])
                    e[('F', k_bot)][0] = info['face']
                    e[('Fc', k_bot)] = np.array([info['face'], Pp[k_bot][1], zc])
                    r = (zc - Pp[k_bot][2]) / (Pp[k_top][2] - Pp[k_bot][2])
                    e[('Pc', k_bot)] = Pp[k_bot] + r * (Pp[k_top] - Pp[k_bot])
                    e[('Pc', k_bot)][2] = zc
                ext[end] = e
                F3, F10, Fc3, Fc10, Pc3, Pc10 = (e[('F', 3)], e[('F', 10)], e[('Fc', 3)], e[('Fc', 10)], e[('Pc', 3)],
                                                 e[('Pc', 10)])
                polys += [[Pp[0], Pp[1], Pp[2], Pp[3], Pp[10], Pp[11]],          # bottom flange end (cut back)
                          [Pp[7], Pp[8], Pp[9], Pp[4], Pp[5], Pp[6]],            # top flange end (cut back)
                          [Pc10, Pc3, Pp[4], Pp[9]],                             # cope face of the web
                          [F10, F3, Pp[3], Pp[10]],                              # web extension underside
                          [Fc10, Fc3, Pc3, Pc10],                                # under the floor-beam flange
                          [F3, F10, Fc10, Fc3]]                                  # web end at the floor-beam web
            for k_bot, k_top in ((3, 4), (10, 9)):
                es, ee = ext['s'], ext['e']
                polys += [[es[('F', k_bot)], Ps[k_bot], es[('Pc', k_bot)], es[('Fc', k_bot)]],
                          [Ps[k_bot], Pe[k_bot], ee[('Pc', k_bot)], es[('Pc', k_bot)]],
                          [es[('Pc', k_bot)], ee[('Pc', k_bot)], Pe[k_top], Ps[k_top]],
                          [Pe[k_bot], ee[('F', k_bot)], ee[('Fc', k_bot)], ee[('Pc', k_bot)]]]
            stringer = solid_from_polygons(polys)
            expect(stringer.is_watertight and stringer.is_winding_consistent and stringer.volume > 0,
                   f'{sid}: extended stringer not closed')
            added = 0.0
            for end, info in ends.items():
                e = ext[end]
                L = abs(P[end][3][0] - info['face'])
                h = info['zc'] - (e[('F', 3)][2] + P[end][3][2]) / 2
                added += STRINGER_WEB_T * h * L
            expect(abs(stringer.volume - S.volume - added) < 1e-7, f'{sid}: volume {stringer.volume} vs {S.volume + added}')
            write_solid(sid, stringer)
            check_bodies(sid, new[sid], 1)

            # cleats: two L 4 x 4 x 3/8 x 9 in per end on the floor-beam web and the stringer web
            angles, bolts, rec = [], [], {}
            for end, info in ends.items():
                k, face, into = info['fb'], info['face'], info['into']
                zt = info['zc'] - ANGLE_TOP_DROP
                zb = zt - ANGLE_LEN
                expect(zb > max(P[end][3][2], P[end][10][2]) + 0.01, f'{sid}: angle below the web')
                sides = [-1, 1]
                if j in OUTER_LINES and k in (0, 9):
                    side = 'Y' if OUTER_LINES[j] < 0 else 'X'
                    probe = angle_solid(face, into, yj + OUTER_LINES[j] * STRINGER_WEB_T / 2, OUTER_LINES[j], zb, zt)
                    clash = fourth.overlap(probe, native(f'FB{k}_connection_{side}'))
                    expect(clash > 1e-6 and (j, i, k) in SINGLE_ANGLE, f'{sid}: outside angle at FB{k}')
                    sides = [-OUTER_LINES[j]]
                    single.append(dict(stringer=sid, floor_beam=f'floorbeam{k}', end_angle=f'FB{k}_connection_{side}',
                                       outside_angle_overlap_m3=round(clash, 9)))
                else:
                    expect((j, i, k) not in SINGLE_ANGLE, f'{sid}: single angle expected at FB{k}')
                for s in sides:
                    angles.append(angle_solid(face, into, yj + s * STRINGER_WEB_T / 2, s, zb, zt))
                rows = [zt - ROW_END - r * ROW_PITCH for r in range(ROWS)]
                # web-leg fasteners: through both web legs and the stringer web (head on the -Y / outside face)
                xw = face + into * GAUGE
                for z in rows:
                    if len(sides) == 2:
                        y0 = yj - STRINGER_WEB_T / 2 - ANGLE_T
                        bolts += bolt([xw, y0, z], [0, 1, 0], STRINGER_WEB_T + 2 * ANGLE_T)
                    else:
                        out = OUTER_LINES[j]
                        y0 = yj + out * STRINGER_WEB_T / 2
                        bolts += bolt([xw, y0, z], [0, -out, 0], STRINGER_WEB_T + ANGLE_T)
                # outstanding-leg fasteners through the floor-beam web: modelled with the stringer that starts at the
                # floor beam (k = i), or with the panel 8 stringer at FB9
                if end == 's' or k == 9:
                    fb = fbs[k]
                    has_west = k >= 1          # an angle on the west face (stringer of panel k-1)
                    has_east = k <= 8          # an angle on the east face (stringer of panel k)
                    xa = fb['w0'] - (ANGLE_T if has_west else 0.0)
                    xb = fb['w1'] + (ANGLE_T if has_east else 0.0)
                    for s in sides:
                        yb = yj + s * (STRINGER_WEB_T / 2 + GAUGE)
                        for z in rows:
                            if has_east:
                                bolts += bolt([xb, yb, z], [-1, 0, 0], xb - xa)
                            else:
                                bolts += bolt([xa, yb, z], [1, 0, 0], xb - xa)
                rec[end] = dict(floor_beam=f'floorbeam{k}', web_face_x_m=round(face, 6),
                                floor_beam_flange_underside_z_m=round(info['zc'], 6),
                                angle_top_z_m=round(zt, 6), angles=len(sides),
                                web_extension_mm=round(abs(P[end][3][0] - face) * 1000, 3),
                                web_top_cope_below_top_flange_mm=round(min(P[end][4][2], P[end][9][2]) * 1000 -
                                                                       info['zc'] * 1000, 3))
            cid, bid = f'{sid}_cleats', f'{sid}_bolts'
            write_solid(cid, fourth.concat(angles))
            check_bodies(cid, new[cid], len(angles))
            write_solid(bid, fourth.concat([third.oriented(b) for b in bolts]))
            check_bodies(bid, new[bid], len(bolts))
            rec.update(gap_before=gaps_before[(j, i)], cleat_angles=len(angles), fasteners=len(bolts) // 4)
            s05[sid] = rec
    expect({(int(d['stringer'].split('_')[1]), int(d['stringer'].split('_')[2]), int(d['floor_beam'][9:]))
            for d in single} == SINGLE_ANGLE, 'single-angle ends')
    values['S05'] = s05
    values['S05_single_angle_ends'] = single

    # ---------------------------------------------------------------- stiffeners in the stringer web planes.
    stiffeners = sorted(n for n in parts if n.startswith('FB') and '_stiff' in n)
    expect(len(stiffeners) == 90, 'stiffener count')
    s_removed = {}
    for n in stiffeners:
        k, line = int(n[2:n.index('_')]), int(n.split('stiff')[1])
        st = native(n)
        yj = float(new[f'stringer_{line}_0'].bounds.mean(axis=0)[1])
        expect(abs(st.bounds.mean(axis=0)[1] - yj) < 1e-4, f'{n}: not in the stringer web plane')
        hits = {}
        for i in (k - 1, k):
            if 0 <= i <= 8:
                hits[f'stringer_{line}_{i}'] = round(fourth.overlap(st, new[f'stringer_{line}_{i}']), 9)
        expect(all(h > 1e-6 for h in hits.values()), f'{n}: does not reach the extended stringer web {hits}')
        s_removed[n] = dict(volume_m3=round(float(st.volume), 9), overlaps_extended_stringer_web_m3=hits)
    values['S05_removed_stiffeners'] = s_removed
    removed = stiffeners
    remove_names = set(removed)
    remove_mesh = {i for i, m in enumerate(gltf['meshes']) if m['name'] in remove_names}
    mesh_map, kept_meshes = {}, []
    for i, m in enumerate(gltf['meshes']):
        if i not in remove_mesh:
            mesh_map[i] = len(kept_meshes)
            kept_meshes.append(m)
    node_map, kept_nodes = {}, []
    for i, n in enumerate(gltf['nodes']):
        if 'mesh' in n and n['mesh'] in remove_mesh:
            expect(n['name'] in remove_names, f'node {n["name"]}')
            continue
        node_map[i] = len(kept_nodes)
        kept_nodes.append(n)
    for n in kept_nodes:
        if 'mesh' in n:
            n['mesh'] = mesh_map[n['mesh']]
        if 'children' in n:
            n['children'] = [node_map[c] for c in n['children'] if c in node_map]
    gltf['meshes'], gltf['nodes'] = kept_meshes, kept_nodes
    gltf['scenes'] = [{'nodes': [node_map[i] for i in s['nodes']]} for s in gltf['scenes']]
    expect(len(gltf['nodes'][0]['children']) == 962 and all(gltf['nodes'][c].get('mesh') is not None
                                                           for c in gltf['nodes'][0]['children']), 'scene after removal')
    expect(all(n.get('name') == gltf['meshes'][n['mesh']]['name'] for n in gltf['nodes'] if 'mesh' in n), 'node names')
    meshes = {m['name']: m for m in gltf['meshes']}
    manifest['parts'] = [p for p in manifest['parts'] if p['id'] not in remove_names]
    for n in removed:
        del parts[n]
    manifest['layers']['floor_system']['count'] -= len(removed)

    # ---------------------------------------------------------------- interfaces after the change.
    fastener = {n for n, p in parts.items() if p['layer'] == 'fasteners'}
    allowed, unchanged, checked = {}, {}, 0
    for pid in sorted(new):
        for n in parts:
            if n == pid or (n in new and n < pid):
                continue
            m_after = new.get(n, native(n))
            if not box_overlaps(new[pid], m_after):
                continue
            checked += 1
            after = fourth.overlap(new[pid], m_after)
            if after <= 1e-9:
                continue
            key = f'{pid} / {n}'
            if pid in fastener or n in fastener:
                bolt_id, other = (pid, n) if pid in fastener else (n, pid)
                expect(bolt_id.startswith('stringer_') and
                       (other.startswith(('stringer_', 'floorbeam')) and not other.endswith('_bolts')),
                       f'{key}: fastener in an unrelated part ({after:.3e} m3)')
                allowed[key] = dict(kind='fastener through plies (holes not modelled)', m3=round(after, 9))
            else:
                pre = fourth.overlap(native(pid), native(n))
                if after > pre + 1e-9:
                    raise ValueError(f'{key}: corrected part overlaps {after:.3e} m3 (before {pre:.3e})')
                unchanged[key] = dict(m3=round(after, 10), before_m3=round(pre, 10))
    values['fastener_overlaps'] = allowed
    values['unchanged_preexisting_overlaps'] = unchanged
    values['interface_pairs_checked'] = checked

    # contacts: angles on the floor-beam web and the stringer web, stringer web on the floor-beam web and flange
    contacts = {}
    for sid, rec in s05.items():
        st, cl = new[sid], new[f'{sid}_cleats']
        yj = float(st.bounds.mean(axis=0)[1])
        for end in ('s', 'e'):
            info = rec[end]
            face, zc = info['web_face_x_m'], info['floor_beam_flange_underside_z_m']
            cv = cl.vertices
            on_face = np.abs(cv[:, 0] - face) < TOL
            on_web = np.abs(np.abs(cv[:, 1] - yj) - STRINGER_WEB_T / 2) < TOL
            expect(on_face.sum() >= 4 * info['angles'] and (on_web & (np.abs(cv[:, 0] - face) < 0.11)).sum() >=
                   4 * info['angles'], f'{sid}: angles off the floor-beam web or the stringer web ({end})')
            sv = st.vertices
            expect((np.abs(sv[:, 0] - face) < TOL).sum() == 4 and (np.abs(sv[:, 2] - zc) < TOL).sum() >= 4,
                   f'{sid}: web end off the floor-beam web / flange ({end})')
        fbm = [new.get(f'floorbeam{k}', native(f'floorbeam{k}')) for k in (int(rec['s']['floor_beam'][9:]),
                                                                            int(rec['e']['floor_beam'][9:]))]
        i = int(sid.split('_')[2])
        through = [i] + ([9] if i == 8 else [])          # floor beams whose web fasteners this stringer carries
        contacts[sid] = dict(cleats_to_floor_beams_mm=[round(min_distance(cl, f) * 1000, 4) for f in fbm],
                             stringer_to_floor_beams_mm=[round(min_distance(st, f) * 1000, 4) for f in fbm],
                             web_fasteners_overlap_floor_beam_m3={
                                 f'floorbeam{k}': values['fastener_overlaps'][f'{sid}_bolts / floorbeam{k}']['m3']
                                 for k in through})
        expect(max(contacts[sid]['cleats_to_floor_beams_mm'] + contacts[sid]['stringer_to_floor_beams_mm']) < 1e-3,
               f'{sid}: contact {contacts[sid]}')
    values['S05_contacts_after'] = contacts

    # ---------------------------------------------------------------- manifest entries.
    def update(pid, note, dims=None, pages=None, basis=None, name=None, replace_dims=False):
        p = parts[pid]
        m = new[pid]
        p['bounds_m'] = m.bounds.round(6).tolist()
        p['volume_m3'] = round(float(m.volume), 7)
        if dims is not None:
            p['dimensions'] = dict(dims) if replace_dims else dict(p.get('dimensions') or {}, **dims)
        if pages:
            p['pdf_pages'] = sorted(set(p['pdf_pages']) | set(pages))
            p['sheets'] = sorted(set(p.get('sheets', [])) | set(pages))
        if basis:
            p['basis'] = basis
        if name:
            p['name'] = name
        p['note'] = (p.get('note', '') + ' ' + note).strip()
        meshes[pid]['extras'].update(name=p['name'], note=p['note'], basis=p['basis'], pdf_pages=p['pdf_pages'],
                                     bounds_m=p['bounds_m'], volume_m3=p['volume_m3'], dimensions=p['dimensions'])
        meshes[pid]['extras'].pop('extents', None)

    def gap_text(gaps):
        g = min(gaps)
        return f'{g:.2f} mm from the floor beams' if g > 0 else 'touching the floor beams only at their flange tips'

    for sid, rec in s05.items():
        ext = [rec[e]['web_extension_mm'] for e in ('s', 'e')]
        update(sid, 'Rev. 1.5 (3D review S05): the web is carried from the bottom flange to the floor-beam top-flange '
                    f'underside and run {ext[0]:.1f} / {ext[1]:.1f} mm to the floor-beam webs, where the two framing '
                    'angles hold it (sheets 17 Section A-A, 18); both flanges stay cut back at the floor-beam flange '
                    'tips. End setback and cope fitted (not drawn).',
               dims=dict(end_framing='web to floor-beam web, flanges cut back at the flange tips (fitted)'),
               pages=[16, 17, 18])
        n_ang = rec['cleat_angles']
        single_note = ''
        if n_ang == 3:
            fbk = rec['s']['floor_beam'] if rec['s']['angles'] == 1 else rec['e']['floor_beam']
            single_note = (f' At {fbk} only the inside angle is modelled: the outside one would lie on the floor-beam '
                           'end connection angle (known deviation outer-stringer-end-framing-fb0-fb9).')
        update(f'{sid}_cleats', 'Rev. 1.5 (3D review S05): refitted to the drawn stringer framing (sheet 17 Section A-A '
                                'at FB0, sheet 18 retrofit detail at FB1): at each end two angles back to back on the '
                                'stringer web with their outstanding legs on the floor-beam web, top 1 in below the '
                                'floor-beam top-flange underside (scaled 0.91 / 1.10 in). Before, two translated copies '
                                'of one 3 1/2 x 3 1/2 x 3/8 x 14 in angle stood in the flange-tip plane, 61-72 mm off the '
                                'stringer web and ' + gap_text(rec['gap_before']['cleats_mm']) + '.' +
                                single_note,
               dims=dict(angle='L 4 x 4 x 3/8', length_in=9.0, outstanding_leg_in=4.0, web_leg_in=4.0,
                         thickness_in=0.375, angles=n_ang, top_below_floor_beam_flange_in=1.0), replace_dims=True,
               pages=[16, 17, 18], basis='Drawn detail (sheets 17, 18; scaled); web leg taken equal')
        update(f'{sid}_bolts', 'Rev. 1.5 (3D review S05): 7/8 in fasteners (drawn symbol, sheets 17, 18) in three rows '
                               'at 3 in pitch, 2 3/4 in from the heel: three per outstanding leg through the floor-beam '
                               'web (at an intermediate floor beam common to both stringers and modelled with the one '
                               'that starts there; the panel 9 stringer also carries those at FB9) and three per end '
                               'through both web legs and the stringer web (not drawn; same rows and gauge). Before, 12 '
                               '3/4 in bolts ran through single angle legs, ' + gap_text(rec['gap_before']['bolts_mm']) +
                               '. Holes are not modelled, as for the other fasteners.',
               dims=dict(fasteners=rec['fasteners'], diameter_in=0.875, pitch_in=3.0, gauge_in=2.75), replace_dims=True,
               pages=[16, 17, 18], basis='Drawn detail (sheets 17, 18; scaled); web-leg fasteners inferred')
    for pid in new:
        check_bodies(pid, new[pid])
        expect(np.abs(np.array(parts[pid]['bounds_m']) - new[pid].bounds).max() < 1e-6, f'{pid} bounds')
    for item in manifest.get('detail_coverage', []):
        if item.get('feature') == 'Verticials, diagonals and floor system':
            item['detail'] += (' Stringers frame into the floor-beam webs with two L 4 x 4 x 3/8 x 9 in angles and 7/8 '
                               'in fasteners at 3 in pitch, as drawn at FB0 and FB1 (pp17, 18); no web stiffeners at the '
                               'stringer lines.')
    manifest['known_deviations'].append(dict(
        id='outer-stringer-end-framing-fb0-fb9',
        parts='stringer_0_0_cleats, stringer_8_0_cleats, stringer_0_8_cleats, stringer_8_8_cleats (and their bolts)',
        source='sheets 7, 17, 18',
        deviation='At FB0 and FB9 the outer stringer lines carry only the inside framing angle. The outside angle\'s '
                  '4 in outstanding leg would lie on the 5 in web leg of the floor-beam end connection angle '
                  '(FB0/FB9_connection_X/Y) and on its nuts, which the model fits to the inner end gusset 5 11/16 in '
                  'from the stringer web.',
        reason='Sheet 7 dimensions the outer stringers 6 in inside the coping, 1 ft 3 in from the truss centre line, '
               'which the model follows. Sheets 17 (Section A-A, FB0) and 18 (FB1) draw two angles, but at about 21 in '
               'from the truss centre line and 7.7 in clear of the end connection angles; the two cannot both hold. '
               'The original framing (archived standard 1532, referenced on sheet 16 but not supplied) or a field '
               'measurement of the FB0/FB9 stringer connections would settle it.'))
    expect(set(parts) == set(meshes) == {p['id'] for p in manifest['parts']} and len(parts) == 962, 'final part list')
    expect(sum(1 for p in manifest['parts'] if p['layer'] == 'floor_system') == manifest['layers']['floor_system']['count']
           == 192, 'floor_system layer count')

    while len(binary) % 4:
        binary.append(0)
    gltf['buffers'][0]['byteLength'] = len(binary)
    encoded = json.dumps(gltf, ensure_ascii=True, separators=(',', ':')).encode()
    encoded += b' ' * ((-len(encoded)) % 4)
    out = (struct.pack('<III', 0x46546c67, 2, 28 + len(encoded) + len(binary)) +
           struct.pack('<II', len(encoded), 0x4e4f534a) + encoded + struct.pack('<II', len(binary), 0x004e4942) + binary)
    backup.mkdir(parents=True, exist_ok=True)
    (backup / f'{BID}_before_3d_review_2.glb').write_bytes(original)
    (backup / f'{BID}_manifest_before_3d_review_2.json').write_bytes(raw_manifest)
    path.write_bytes(out)

    changed = sorted(new)
    manifest[TAG_KEY] = TAG
    manifest['revision'] = REVISION
    manifest[RECORD_KEY] = dict(
        review='3D placement review, round 5 (second review)', follows=PREVIOUS_TAG, previous_revision=PREVIOUS_REVISION,
        source_pdf_pages=[7, 16, 17, 18], printed_sheets=[7, 16, 17, 18],
        native_axes='X = station from Sta. 42+54.00, Y = transverse (+Y = X-truss side, left looking up-station), '
                    'Z = elevation - 778 ft; GLB (X, Z, -Y)',
        findings=[
            dict(id='S05', verdict='resolve',
                 summary='81 stringer cleat assemblies (36 cited, all 81 alike) stood in the floor-beam flange-tip '
                         'plane: translated copies of one 3 1/2 x 3 1/2 x 3/8 x 14 in angle, off the stringer web and '
                         '4.7-27 mm below the floor-beam flange (outer lines) or touching only its tip edge (inner '
                         'lines); no cleat reached the floor-beam web. Now two L 4 x 4 x 3/8 x 9 in angles per end on '
                         'the stringer web and the floor-beam web, 7/8 in fasteners through the connected plies, the '
                         'stringer web run to the floor-beam web; the 90 inferred web stiffeners in the stringer web '
                         'planes are removed',
                 basis='sheet 17 Section A-A (FB0) and sheet 18 temporary truss support retrofit detail (FB1), 1 1/2 in '
                       '= 1 ft: framing angles, fastener rows, gauge and symbol scaled; sheet 16 plan marks the angles '
                       'on both faces of each floor-beam web')],
        decisions=[
            'Angle sizes, rows, gauge and top level are scaled from sheets 17 and 18 (no dimension is written on the '
            'framing); the web leg, seen only edge-on, is taken equal to the drawn 4 in outstanding leg, and the '
            'web-leg fasteners use the same rows and gauge.',
            'The stringer web is run to the floor-beam web and up to the floor-beam top-flange underside (fitted); '
            'both flanges stay cut back at the flange tips as before. The setback and cope are not drawn.',
            'FB*_stiff* (90) removed: inferred plates in the stringer web planes, where the drawn framing puts the '
            'stringer web and its angles; sheets 17 and 18 draw no stiffener at the stringer lines.',
            'Outstanding-leg fasteners at an intermediate floor beam pass through both stringers\' angles and the web '
            'and are modelled once, in the bolts of the stringer that starts at that floor beam.'],
        kept_deviations=['outer-stringer-end-framing-fb0-fb9'],
        changed_parts=changed, added_parts=[], removed_parts=removed,
        values=values, before_glb_sha256=before, after_glb_sha256=hashlib.sha256(out).hexdigest())
    text = json.dumps(manifest, ensure_ascii=False, indent=2) + '\n'
    if b'\r\n' in raw_manifest:
        text = text.replace('\n', '\r\n')
    mp.write_bytes(text.encode('utf-8'))
    print(json.dumps({k: v for k, v in manifest[RECORD_KEY].items()
                      if k not in ('values', 'findings', 'changed_parts', 'removed_parts')}, indent=1))
    print(f'{len(changed)} parts changed, {len(removed)} removed')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--base', type=Path, default=BASE, help='bridge folder (default: the repository copy)')
    parser.add_argument('--backup', type=Path, default=BACKUP, help='backup folder')
    args = parser.parse_args()
    correct(args.base, args.backup)

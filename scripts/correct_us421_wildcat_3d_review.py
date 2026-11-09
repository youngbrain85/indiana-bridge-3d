"""Fourth correction of US 421 over South Fork Wildcat Creek (us421-wildcat), from the 3D placement review: rail posts,
floor-beam end angles, drain-pipe brackets and duplicate lateral gussets. Runs after scripts/correct_us421_wildcat_review.py,
_review_2.py and _review_3.py and keeps every GLB buffer it does not replace.

    python scripts/correct_us421_wildcat_3d_review.py [--base DIR] [--backup DIR]

Source: drawings.pdf (INDOT 2020 rehabilitation plans, 30 sheets); printed sheet numbers equal PDF page numbers.
Native axes: X = station from Sta. 42+54.00, Y = transverse (+Y = left of increasing station = X-truss side), Z =
elevation - 778 ft; GLB (X, Z, -Y).

S01 (major) RESOLVED - intermediate metal-rail posts. Each of the 16 posts (a 4 in x 6 in I-section between the rail
  and the truss vertical) stopped 57.28 mm short of the vertical web, with no bracket, and 15.24 mm off the curb.
  Sheet 7 (typical sections, Span "B") draws the retained rail fastened at the inner face of each truss vertical and
  clear of the 6 in curb, so the curb gap is as drawn and the post must reach the vertical. The model's 10WF33
  verticals present their web to the roadway between the flanges (8.86 in clear; the post is 4 in wide), so the post's
  rear flange is moved onto the roadway face of the web: 4 rear-flange vertex pairs move 57.28 mm, rail, front flange
  and bolts unchanged. The post depth becomes 8.25 in (fitted, was 6 in).
S02 (minor) RESOLVED - floor-beam end connection angles. The 20 angle pairs (L 5 x 5 x 7/16, 30 in) were 7 in either
  side of the floor-beam centre line: the first angle's toe 42.86 mm off the 5/8 in web, the second angle outside the
  12 in flange, the outstanding legs on the truss centre line inside the truss member (X truss: web legs outside it;
  the Y-truss pairs were translated, not mirrored), with 10 bolts through one leg only. Sheet 18 (temporary
  truss support retrofit detail and Section F-F, FB1) and sheet 17 (Section A-A, FB0) draw a back-to-back pair on the
  floor-beam web, outstanding legs on the roadway face of the truss member (the vertical; at FB0/FB9 the inner end
  gusset). Each angle now has its web leg on one face of the FB web and its outstanding leg on the roadway face of the
  truss: the inner new end gusset at FB0/FB9 (whose drilled 7/8 in bolt columns 2 3/4 in each side of the FB centre
  line pass through the legs; the roadway-side heads (Y truss: washers and nuts) of those 20 bolts, and on the Y truss
  one more washer at the angle toe, would sit in the leg and are moved onto it) and
  the vertical web at FB1-FB8, fitted between the vertical flanges (outstanding leg 4.12 in; Section F-F draws about
  4 in). Where the modelled lower-chord top flange or diagonal ends reach into the connection the angles are trimmed
  to them, so no plate steel is counted twice (bolt heads / nuts are left whole, like the model's other fasteners). Thickness, 5 in web leg, 30 in length and elevation unchanged. The 10 bolts
  become five 7/8 in through-bolts (same 6 in pitch and 2.4 in gauge from the heel) through both angles and the web;
  holes are not modelled, as for the model's other fasteners.
S03 (minor) RESOLVED - drain pipe clamps. The 12 clamp brackets were a 6 in flat bar running from the pipe centre AWAY
  from the pier, so the assemblies stopped 17.78 mm short of the cap and 195.58 mm short of the stem. The sheet 26
  pipe connection detail draws a 1/4 x 2 in U-bracket standing off the concrete, its feet anchored by 1/2 x 1 1/2 in
  bolts in standard 1/2 in concrete inserts 4 3/4 in each side of the pipe centre line, with the pipe strap bolted to
  it; Section X-X puts the upper clamp on the cap and the lower on the stem. Each bracket is replaced by that U-bracket
  fitted to the modelled strap ring: cross bar against the ring on the pier side, legs in line with the ring, feet on
  the cap face (clamp0) or the stem face 7 in behind it (clamp1, clamp2), and the two anchors embedded 1 1/4 in
  (1 1/2 in less the 1/4 in foot). Foot ends 5 1/2 in from the pipe centre line (scaled on the 4 3/4 in dimension of
  the no-scale detail; the foot ends at the washer). Strap ring, clamp elevations and pipe routes unchanged.
S04 (minor) RESOLVED - lateral_gusset_i_1 (i = 0..4) were exact copies of lateral_gusset_i_-1 (same vertices and
  faces): one central plate per lower-lateral crossing (sheet 16 plan). The five _1 copies are removed; both laterals of
  each crossing sit on the remaining plate.

Changed (72): 16 metal_rail_post_*, 20 FB*_connection_X/Y, 20 FB*_connection_X/Y_bolts, 4 inner repair_gusset_*_bolts,
12 drain*_clamp*. Removed (5): lateral_gusset_0_1 .. lateral_gusset_4_1. Added: none. Other meshes, accessors and the
original binary data are kept byte for byte (replaced accessors stay unreferenced).

Requires numpy, trimesh and manifold3d, plus the three earlier us421_wildcat correction scripts.
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
import correct_us421_wildcat_review_3 as third  # noqa: E402

BID = 'us421-wildcat'
BASE = ROOT / 'data/bridges' / BID
BACKUP = ROOT / 'data/fem_research'
TAG_KEY = 'review_correction_3d'
TAG = 'rail-posts-fb-angles-drain-brackets-lateral-gussets'
RECORD_KEY = 'review_correction_record_3d'
REVISION = '1.4-3d-review'
PREVIOUS_TAG_KEY, PREVIOUS_TAG, PREVIOUS_REVISION = 'review_correction_3', third.TAG, third.REVISION
EXPECTED_GLB_SHA256 = '97e5b4f348ab213da4be8e2279dc2dddbfb9d34c9418ef1266d12689746e5cbd'   # revision 1.3 output
FT, IN = third.FT, third.IN
TOL = 1e-5
ANGLE_T = 7 / 16 * IN          # connection angle thickness (model, L 5 x 5 x 7/16)
ANGLE_LEG = 5 * IN             # connection angle legs (model)
BOLT_GAUGE = 0.06096           # 2.4 in, FB connection bolt line from the angle heel (model)
BAR_T, BAR_W = 0.25 * IN, 2 * IN               # 1/4 x 2 in bar (sheet 26 pipe connection detail)
ANCHOR_R, ANCHOR_L = 0.25 * IN, 1.5 * IN       # 1/2 x 1 1/2 in bolt (sheet 26)
ANCHOR_OFFSET = 4.75 * IN                      # bolts 4 3/4 in each side of the pipe centre line (sheet 26)
FOOT_END = 5.5 * IN                            # foot end, scaled on the 4 3/4 in dimension (detail not to scale)
CAP_OVERHANG = 7 * IN                          # pier cap face 7 in in front of the stem face (model, pier caps)
END_GUSSETS = {(0, 'X'): 'repair_gusset_X_west_-1', (0, 'Y'): 'repair_gusset_Y_west_1',
               (9, 'X'): 'repair_gusset_X_east_-1', (9, 'Y'): 'repair_gusset_Y_east_1'}
DUPLICATES = {f'lateral_gusset_{i}_1': f'lateral_gusset_{i}_-1' for i in range(5)}
PIERS = {0: ('pier2', -1), 4: ('pier3', 1)}    # drain index: pier, direction from the pipe toward the pier (X)


def to_native(v):
    return third.to_native(v)


def to_glb(v):
    return third.to_glb(v)


def box(x0, x1, y0, y1, z0, z1):
    return third.box(min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1), min(z0, z1), max(z0, z1))


def boolean(op, meshes):
    """Manifold boolean evaluated near the origin (float precision), result moved back."""
    shift = meshes[0].bounds.mean(axis=0)
    local = [trimesh.Trimesh(m.vertices - shift, m.faces, process=False) for m in meshes]
    r = {'union': trimesh.boolean.union, 'difference': trimesh.boolean.difference,
         'intersection': trimesh.boolean.intersection}[op](local, engine='manifold')
    return trimesh.Trimesh(r.vertices + shift, r.faces, process=False)


def overlap(a, b):
    if np.any(a.bounds[0] > b.bounds[1] + 1e-6) or np.any(b.bounds[0] > a.bounds[1] + 1e-6):
        return 0.0
    total = 0.0
    for sa in bodies(a):
        for sb in bodies(b):
            if np.any(sa.bounds[0] > sb.bounds[1] + 1e-6) or np.any(sb.bounds[0] > sa.bounds[1] + 1e-6):
                continue
            with np.errstate(divide='ignore', invalid='ignore'):
                i = boolean('intersection', [sa, sb])
                total += float(i.volume) if len(i.faces) else 0.0
    return total


def bodies(mesh):
    out = []
    for idx in third.shells(mesh):
        s = trimesh.Trimesh(mesh.vertices, mesh.faces[idx], process=False)
        s.remove_unreferenced_vertices()
        out.append(s)
    return out


def concat(meshes):
    v, f, n = [], [], 0
    for m in meshes:
        v.append(m.vertices)
        f.append(m.faces + n)
        n += len(m.vertices)
    return trimesh.Trimesh(np.vstack(v), np.vstack(f), process=False)


def x_cylinder(x0, x1, y, z, r, sections=12):
    c = trimesh.creation.cylinder(radius=r, height=abs(x1 - x0), sections=sections)
    c.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [0, 1, 0]))
    c.apply_translation([(x0 + x1) / 2, y, z])
    return third.oriented(c)


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
           f'run scripts/correct_us421_wildcat_review_3.py first (revision {manifest.get("revision")})')
    expect(TAG_KEY not in manifest, f'{TAG_KEY} already holds {manifest.get(TAG_KEY)}')
    expect(before == EXPECTED_GLB_SHA256 == manifest['review_correction_3_record']['after_glb_sha256'],
           f'model.glb SHA-256 {before} is not the revision 1.3 output')
    expect([d['id'] for d in manifest.get('known_deviations', [])] == ['tfc-transition-envelope'], 'known deviations')

    length = struct.unpack_from('<I', original, 12)[0]
    gltf = json.loads(original[20:20 + length])
    binary = bytearray(original[28 + length:])
    parts = {p['id']: p for p in manifest['parts']}
    meshes = {m['name']: m for m in gltf['meshes']}
    world = gltf['nodes'][0]
    expect(set(parts) == set(meshes) and len(meshes) == 1057, 'part list')
    expect(world.get('name') == 'world' and len(world['children']) == 1057 and gltf['scenes'] == [{'nodes': [0]}],
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
            v = to_native(read(prim['attributes']['POSITION']).astype(np.float64))
            cache[pid] = trimesh.Trimesh(v, read(prim['indices']).reshape(-1, 3), process=False)
        return cache[pid]

    def stored(mesh):
        """The solid as the GLB stores it (float32 positions)."""
        return trimesh.Trimesh(to_native(to_glb(mesh.vertices).astype('<f4').astype(np.float64)), mesh.faces,
                               process=False)

    new, notes = {}, {}

    def write_solid(pid, mesh):
        prim = meshes[pid]['primitives'][0]
        color = read(prim['attributes']['COLOR_0'])[0]
        prim['attributes'] = {'POSITION': append(to_glb(mesh.vertices).astype('<f4'), 'VEC3', 5126),
                              'COLOR_0': append(np.tile(color, (len(mesh.vertices), 1)).astype('u1'), 'VEC4', 5121)}
        gltf['accessors'][prim['attributes']['COLOR_0']]['normalized'] = True
        prim['indices'] = append(mesh.faces.reshape(-1, 1).astype('<u4'), 'SCALAR', 5125)
        new[pid] = stored(mesh)

    def write_positions(pid, vertices):
        prim = meshes[pid]['primitives'][0]
        prim['attributes']['POSITION'] = append(to_glb(vertices).astype('<f4'), 'VEC3', 5126)
        new[pid] = stored(trimesh.Trimesh(vertices, native(pid).faces, process=False))

    def check_bodies(pid, mesh, count=None):
        bs = bodies(mesh)
        for b in bs:
            w = b.copy()
            w.merge_vertices(digits_vertex=5)
            expect(w.is_watertight and w.is_winding_consistent and b.volume > 0, f'{pid}: body not a closed solid')
        if count is not None:
            expect(len(bs) == count, f'{pid}: {len(bs)} bodies, expected {count}')

    values = {}

    # ---------------------------------------------------------------- S01: rail posts onto the vertical web.
    s01 = {}
    for side, sgn in (('X', 1), ('Y', -1)):
        for k in range(1, 9):
            pid = f'metal_rail_post_{side}_{k}'
            post = native(pid)
            v = post.vertices.copy()
            ay = np.abs(v[:, 1])
            expect(len(v) == 24 and np.allclose(sorted(set(np.round(ay, 5))), [4.43484, 4.44437, 4.57771, 4.58724]),
                   f'{pid}: not the 4 x 6 in post')
            cx = post.bounds.mean(axis=0)[0]
            vert = [n for n in (f'{side}_V{j}' for j in range(1, 9))
                    if native(n).bounds[0][0] < cx < native(n).bounds[1][0]]
            expect(len(vert) == 1, f'{pid}: vertical')
            vv = native(vert[0]).vertices
            xs = np.unique(np.round(vv[:, 0], 6))
            ys = np.unique(np.round(np.abs(vv[:, 1]), 6))
            expect(len(xs) == 4 and len(ys) == 4, f'{vert[0]}: not the 10WF33 envelope')
            web_face = ys[1]                                 # roadway face of the web, |Y| = 4.64452
            expect(xs[1] < post.bounds[0][0] and post.bounds[1][0] < xs[2], f'{pid}: wider than the flange gap')
            expect(post.bounds[0][2] > vv[:, 2].min() and post.bounds[1][2] < vv[:, 2].max(), f'{pid}: height')
            gap = web_face - ay.max()
            expect(abs(gap - 0.057277) < 2e-5, f'{pid}: gap {gap}')
            rear = ay > 4.57
            v[rear, 1] += sgn * gap
            write_positions(pid, v)
            check_bodies(pid, new[pid], 1)
            s01[pid] = dict(vertical=vert[0], gap_before_mm=round(gap * 1000, 3), web_face_abs_y=round(float(web_face), 6),
                            depth_in=round((web_face - 4.43484) / IN, 3))
    values['S01'] = s01

    # ---------------------------------------------------------------- S02: floor-beam end connection angles.
    s02 = {}
    gusset_bolt_changes = {}
    truss_layers = {'truss_chords', 'truss_web', 'lacing', 'gussets', 'repairs'}
    for k in range(10):
        fb = native(f'floorbeam{k}')
        fx = np.unique(np.round(fb.vertices[:, 0], 6))
        expect(len(fx) == 4 and abs(fx[2] - fx[1] - 0.625 * IN) < 2e-5, f'floorbeam{k}: web')
        w0, w1 = float(fx[1]), float(fx[2])
        for side, sgn in (('X', 1), ('Y', -1)):
            pid, bid = f'FB{k}_connection_{side}', f'FB{k}_connection_{side}_bolts'
            old = native(pid)
            z0, z1 = float(old.bounds[0][2]), float(old.bounds[1][2])
            expect(abs(z1 - z0 - 30 * IN) < 2e-5 and len(old.vertices) == 24, f'{pid}: not the 30 in angle pair')
            first_gap = w0 - (old.bounds[0][0] + ANGLE_LEG)
            expect(abs(first_gap - 0.042863) < 2e-5, f'{pid}: toe gap {first_gap}')
            if k in (0, 9):
                gid = END_GUSSETS[(k, side)]
                gb = native(gid).bounds
                face = float(gb[0][1] if sgn > 0 else gb[1][1])
                expect(abs(abs(face) - 4.4115) < 1e-4, f'{gid}: roadway face')
                lout_a = lout_b = ANGLE_LEG
                support = gid
            else:
                vert = [n for n in (f'{side}_V{j}' for j in range(1, 9))
                        if native(n).bounds[0][0] < (w0 + w1) / 2 < native(n).bounds[1][0]]
                expect(len(vert) == 1, f'{pid}: vertical')
                vv = native(vert[0]).vertices
                xs = np.unique(np.round(vv[:, 0], 6))
                face = sgn * float(np.unique(np.round(np.abs(vv[:, 1]), 6))[1])
                lout_a, lout_b = w0 - float(xs[1]), float(xs[2]) - w1
                expect(0.09 < lout_a < ANGLE_LEG and 0.09 < lout_b < ANGLE_LEG, f'{pid}: flange gap')
                support = vert[0]
            yl = (face - sgn * ANGLE_T, face)                 # outstanding legs, on the roadway face
            yw = (face - sgn * ANGLE_LEG, face)               # web legs, toward the roadway
            pieces = []
            for leg_x, web_x in (((w0 - lout_a, w0), (w0 - ANGLE_T, w0)), ((w1, w1 + lout_b), (w1, w1 + ANGLE_T))):
                pieces.append(boolean('union', [box(*leg_x, *yl, z0, z1), box(*web_x, *yw, z0, z1)]))
            trimmed, hits = [], []
            for p in pieces:
                cut = []
                for n, part in parts.items():
                    if part['layer'] not in truss_layers or n == support:
                        continue
                    m = native(n)
                    if np.any(m.bounds[0] > p.bounds[1]) or np.any(p.bounds[0] > m.bounds[1]):
                        continue
                    if overlap(p, m) > 1e-10:
                        cut.append(n)
                expect(all(n.startswith((f'{side}_LC', f'{side}_D')) for n in cut), f'{pid}: unexpected clash {cut}')
                t = boolean('difference', [p] + [native(n) for n in cut]) if cut else p
                expect(len(bodies(t)) == 1, f'{pid}: trimmed angle split')
                trimmed.append(t)
                hits.append(dict(parts=cut, trimmed_m3=round(float(p.volume - t.volume), 8)))
            angles = concat(trimmed)
            write_solid(pid, angles)
            check_bodies(pid, new[pid], 2)

            # bolts: 10 bolts through one leg -> 5 through-bolts (head, shank, washer, nut) through both web legs
            ob = native(bid)
            comps = bodies(ob)
            expect(len(comps) == 40, f'{bid}: 10 bolts')
            zc = sorted({round(float(c.bounds.mean(axis=0)[2]), 4) for c in comps})
            expect(len(zc) == 5, f'{bid}: rows')
            first = [c for c in comps if abs(c.bounds.mean(axis=0)[2] - zc[0]) < 1e-3 and
                     c.bounds.mean(axis=0)[0] < (w0 + w1) / 2]
            shank = [c for c in first if len(c.vertices) == 26]
            washer = [c for c in first if len(c.vertices) == 34]
            hexes = sorted([c for c in first if len(c.vertices) == 14], key=lambda c: c.bounds[0][0])
            expect(len(shank) == 1 and len(washer) == 1 and len(hexes) == 2, f'{bid}: bolt parts')
            shank, washer, head, nut = shank[0], washer[0], hexes[0], hexes[1]
            axis = shank.bounds.mean(axis=0)
            expect(abs(abs(axis[1] - sgn * 4.6482) - BOLT_GAUGE) < 1e-4, f'{bid}: gauge')
            yb = face - sgn * BOLT_GAUGE
            xa, xb = w0 - ANGLE_T, w1 + ANGLE_T
            tw, tn = washer.extents[0], nut.extents[0]
            bolts = []
            for z in zc:
                d = np.array([0.0, yb - axis[1], 0.0])
                d[2] = z - zc[0]
                h = head.vertices + d
                h[:, 0] += xa - head.bounds[1][0]
                s = shank.vertices + d
                s[:, 0] = xa + (s[:, 0] - shank.bounds[0][0]) * (xb - xa) / shank.extents[0]
                w = washer.vertices + d
                w[:, 0] += xb - washer.bounds[0][0]
                nn = nut.vertices + d
                nn[:, 0] += xb + tw - nut.bounds[0][0]
                for vtx, src in ((h, head), (s, shank), (w, washer), (nn, nut)):
                    bolts.append(trimesh.Trimesh(vtx, src.faces, process=False))
            # bolt z rows must lie on the web legs
            expect(min(zc) - z0 > 0.03 and z1 - max(zc) > 0.03, f'{bid}: rows outside the angles')
            # heads / nuts that reach into the modelled diagonal ends (node envelopes running past the floor-beam
            # web) are left whole, like every other fastener in the model; the overlap is recorded
            write_solid(bid, concat(bolts))
            check_bodies(bid, new[bid], 20)
            bolt_clash = {}
            for n, part in parts.items():
                if part['layer'] in truss_layers and not (np.any(native(n).bounds[0] > new[bid].bounds[1]) or
                                                          np.any(new[bid].bounds[0] > native(n).bounds[1])):
                    ov = overlap(new[bid], native(n))
                    if ov > 1e-10:
                        expect(n.startswith((f'{side}_LC', f'{side}_D')) and ov < 1e-5, f'{bid}: clash {n} {ov}')
                        bolt_clash[n] = round(ov, 9)

            # FB0/FB9: roadway-side heads / nuts of the end-gusset bolts in the angle footprint bear on the angle leg
            if k in (0, 9):
                gbid = END_GUSSETS[(k, side)] + '_bolts'
                comps = bodies(native(gbid))
                groups = {}
                for c in comps:
                    cc = c.bounds.mean(axis=0)
                    groups.setdefault((round(float(cc[0]), 3), round(float(cc[2]), 3)), []).append(c)
                leg_boxes = [(w0 - lout_a, w0), (w1, w1 + lout_b)]
                out, moved = [], 0
                deltas = set()
                for key, grp in groups.items():
                    hw = [c for c in grp if len(c.vertices) != 26 and
                          (c.bounds.mean(axis=0)[1] - face) * sgn < 0]            # roadway side of the gusset
                    sh = [c for c in grp if len(c.vertices) == 26]
                    hw_ids, sh_ids = {id(c) for c in hw}, {id(c) for c in sh}
                    hit = any(c.bounds[0][2] < z1 and c.bounds[1][2] > z0 and
                              any(c.bounds[0][0] < x1_ and c.bounds[1][0] > x0_ for x0_, x1_ in leg_boxes)
                              for c in hw)
                    if not hit:
                        out += grp
                        continue
                    expect(len(sh) == 1 and len(grp) == 4 and 1 <= len(hw) <= 2, f'{gbid}: bolt {key}')
                    near = max(c.bounds[1][1] for c in hw) if sgn > 0 else min(c.bounds[0][1] for c in hw)
                    dy = (face - sgn * ANGLE_T) - near
                    expect(sgn * dy < 0 and abs(dy) < 0.006, f'{gbid}: head move {dy}')
                    deltas.add(round(dy * 1000, 3))
                    for c in grp:
                        vtx = c.vertices.copy()
                        if id(c) in hw_ids:
                            vtx[:, 1] += dy
                        elif id(c) in sh_ids:
                            end = vtx[:, 1] < c.bounds.mean(axis=0)[1] if sgn > 0 else \
                                vtx[:, 1] > c.bounds.mean(axis=0)[1]
                            vtx[end, 1] += dy
                        out.append(trimesh.Trimesh(vtx, c.faces, process=False))
                    moved += 1
                expect(moved in (20, 21), f'{gbid}: {moved} bolts in the angle footprint')
                gusset_bolt_changes[gbid] = concat(out)
                values.setdefault('S02_end_gusset_bolts', {})[gbid] = dict(
                    bolts_moved=moved, head_or_nut_move_mm=sorted(deltas))
            s02[pid] = dict(support=support, toe_gap_before_mm=round(first_gap * 1000, 3),
                            second_angle_heel_before_m=round(float(old.bounds[1][0] - ANGLE_LEG), 6),
                            fb_web_faces_m=[round(w0, 6), round(w1, 6)], bearing_face_y_m=round(face, 6),
                            outstanding_leg_in=[round(lout_a / IN, 3), round(lout_b / IN, 3)], trimmed=hits,
                            bolt_rows_z_m=zc, bolt_hardware_in_member_ends_m3=bolt_clash)
    for gbid, mesh in gusset_bolt_changes.items():
        orig_faces = native(gbid).faces
        expect(len(mesh.faces) == len(orig_faces), f'{gbid}: topology')
        # same components in a new order: write as a new solid
        write_solid(gbid, mesh)
        check_bodies(gbid, new[gbid], len(bodies(native(gbid))))
    values['S02'] = s02

    # ---------------------------------------------------------------- S03: drain clamp brackets to the pier face.
    s03 = {}
    for d, (pier, s) in PIERS.items():
        cap, stem = native(f'{pier}_cap'), native(f'{pier}_stem')
        for side in ('X', 'Y'):
            for c in range(3):
                pid = f'drain{d}_{side}_clamp{c}'
                comps = bodies(native(pid))
                rings = [b for b in comps if len(b.vertices) == 96]
                bars = [b for b in comps if len(b.vertices) == 8]
                expect(len(comps) == 2 and len(rings) == 1 and len(bars) == 1, f'{pid}: ring and bar')
                ring, bar = rings[0], bars[0]
                rv = ring.vertices
                xc = (rv[:, 0].max() + rv[:, 0].min()) / 2
                yc = (rv[:, 1].max() + rv[:, 1].min()) / 2
                rr = np.linalg.norm(rv[:, :2] - [xc, yc], axis=1)
                r_i, r_o = float(rr.min()), float(rr.max())
                za, zb = float(rv[:, 2].min()), float(rv[:, 2].max())
                expect(abs(zb - za - BAR_W) < 1e-5 and abs(r_o - r_i - BAR_T) < 1e-5, f'{pid}: strap ring')
                # old bar: 6 in from the pipe centre AWAY from the pier
                far = bar.bounds[1][0] if s < 0 else bar.bounds[0][0]
                expect(abs(abs(far - xc) - 6 * IN) < 1e-5 and (far - xc) * s < 0, f'{pid}: old bar direction')
                if cap.bounds[0][2] < za and zb < cap.bounds[1][2]:
                    concrete, face_part = cap, f'{pier}_cap'
                elif stem.bounds[0][2] < za and zb < stem.bounds[1][2]:
                    concrete, face_part = stem, f'{pier}_stem'
                else:
                    raise ValueError(f'{pid}: band not on the cap or the stem')
                xf = concrete.bounds[1][0] if s < 0 else concrete.bounds[0][0]
                for y in (yc - FOOT_END, yc, yc + FOOT_END):
                    for z in (za + 1e-3, zb - 1e-3):
                        hit, _, _ = concrete.ray.intersects_location([[xc, y, z]], [[s, 0, 0]])
                        near = hit[np.argmin(np.abs(hit[:, 0] - xc))][0]
                        expect(abs(near - xf) < 1e-5, f'{pid}: {face_part} face not plane at the bracket')
                gap_before = abs(xf - xc) - r_o
                uf = abs(xf - xc)
                expect(uf > r_o + 2 * BAR_T, f'{pid}: no room for the bracket')

                def X(u):
                    return xc + s * u
                zm = (za + zb) / 2
                pieces = [box(X(r_o), X(r_o + BAR_T), yc - r_o, yc + r_o, za, zb)]          # cross bar
                for sv in (-1, 1):
                    pieces.append(box(X(r_o), X(uf), yc + sv * r_i, yc + sv * r_o, za, zb))   # leg
                    pieces.append(box(X(uf - BAR_T), X(uf), yc + sv * r_i, yc + sv * FOOT_END, za, zb))  # foot
                    pieces.append(x_cylinder(X(uf - BAR_T), X(uf - BAR_T + ANCHOR_L), yc + sv * ANCHOR_OFFSET, zm,
                                             ANCHOR_R))                                        # anchor in insert
                bracket = boolean('union', pieces)
                expect(len(bodies(bracket)) == 1, f'{pid}: bracket not one solid')
                write_solid(pid, concat([ring, bracket]))
                check_bodies(pid, new[pid], 2)
                s03[pid] = dict(concrete=face_part, face_x_m=round(float(xf), 6), pipe_cl_x_m=round(float(xc), 6),
                                gap_before_mm=round(gap_before * 1000, 3), standoff_in=round(uf / IN, 3),
                                leg_in=round((uf - r_o - 2 * BAR_T) / IN, 3), anchor_embedment_in=1.25)
    values['S03'] = s03

    # ---------------------------------------------------------------- S04: duplicate lateral gussets.
    s04 = {}
    for dup, keep in DUPLICATES.items():
        pd, pk = meshes[dup]['primitives'][0], meshes[keep]['primitives'][0]
        expect(np.array_equal(read(pd['attributes']['POSITION']), read(pk['attributes']['POSITION'])) and
               np.array_equal(read(pd['indices']), read(pk['indices'])), f'{dup}: not an exact copy of {keep}')
        expect(parts[dup]['name'] == parts[keep]['name'], f'{dup}: name')
        lats = [n for n in parts if n.startswith(f'lateral_{dup.split("_")[2]}_')]
        kb = native(keep).bounds
        cx, cy = kb.mean(axis=0)[:2]
        for n in lats:
            hits = np.concatenate([third.vertical_hits(native(n), cx + dx, cy + dy)
                                   for dx, dy in ((0.004, 0.003), (-0.004, -0.003), (0.004, -0.003))])
            expect(len(hits) >= 2 and abs(hits.min() - kb[1][2]) < 1e-3, f'{n}: does not sit on {keep}')
        s04[dup] = dict(kept=keep, volume_m3=round(float(native(dup).volume), 9), laterals_on_plate=sorted(lats))
    values['S04'] = s04
    removed = sorted(DUPLICATES)
    remove_mesh = {i for i, m in enumerate(gltf['meshes']) if m['name'] in DUPLICATES}
    mesh_map, kept_meshes = {}, []
    for i, m in enumerate(gltf['meshes']):
        if i not in remove_mesh:
            mesh_map[i] = len(kept_meshes)
            kept_meshes.append(m)
    node_map, kept_nodes = {}, []
    for i, n in enumerate(gltf['nodes']):
        if 'mesh' in n and n['mesh'] in remove_mesh:
            expect(n['name'] in DUPLICATES, f'node {n["name"]}')
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
    expect(len(gltf['nodes'][0]['children']) == 1052 and all(gltf['nodes'][c]['mesh'] is not None
                                                            for c in gltf['nodes'][0]['children']), 'scene after removal')
    expect(all(n.get('name') == gltf['meshes'][n['mesh']]['name'] for n in gltf['nodes'] if 'mesh' in n), 'node names')
    meshes = {m['name']: m for m in gltf['meshes']}
    manifest['parts'] = [p for p in manifest['parts'] if p['id'] not in DUPLICATES]
    for dup in DUPLICATES:
        del parts[dup]
    manifest['layers']['gussets']['count'] -= len(DUPLICATES)

    # ---------------------------------------------------------------- interfaces after the change.
    fastener = {n for n, p in parts.items() if p['layer'] == 'fasteners'}
    allowed = {}
    for pid in sorted(new):
        for n in parts:
            if n == pid:
                continue
            m_after = new.get(n, native(n))
            if np.any(m_after.bounds[0] > new[pid].bounds[1] + 1e-6) or \
                    np.any(new[pid].bounds[0] > m_after.bounds[1] + 1e-6):
                continue
            after = overlap(new[pid], m_after)
            if after <= 1e-9:
                continue
            if n in new and n < pid:
                continue
            bolt_pair = pid in fastener or n in fastener
            anchor = pid.startswith('drain') and n.startswith('pier')
            pre = overlap(native(pid), native(n))
            key = f'{pid} / {n}'
            if anchor:
                expected_anchor = 2 * 3 * ANCHOR_R ** 2 * (ANCHOR_L - BAR_T)      # two 12-gon shanks, 1 1/4 in
                expect(abs(after - expected_anchor) < 0.01 * expected_anchor, f'{key}: anchor embedment {after}')
                allowed[key] = dict(kind='anchor bolts in concrete inserts (1 1/4 in)', m3=round(after, 9))
            elif bolt_pair or (pid.startswith('metal_rail_post') and n.startswith(('metal_rail_attach', 'metal_rail_'))):
                expect(after <= max(pre, 0.0) + 1e-6 or bolt_pair, f'{key}: {after}')
                allowed[key] = dict(kind='fastener through plies (holes not modelled)' if bolt_pair else
                                    'rail through post front flange (unchanged)', m3=round(after, 9),
                                    before_m3=round(pre, 9))
            else:
                raise ValueError(f'{key}: corrected part overlaps {after:.3e} m3 (before {pre:.3e})')
    values['fastener_and_anchor_overlaps'] = allowed

    # contacts: posts on the web, angles on web and truss face, brackets on the concrete
    for pid, info in s01.items():
        m = new[pid]
        face_y = info['web_face_abs_y'] * (1 if '_X_' in pid else -1)
        rear = m.vertices[np.abs(np.abs(m.vertices[:, 1]) - info['web_face_abs_y']) < 2e-6]
        expect(len(rear) == 4 and abs(rear[:, 1].mean() - face_y) < 2e-6, f'{pid}: rear face not on the web')
    for pid, info in s02.items():
        m = new[pid]
        expect(abs(m.bounds[0][1] - info['bearing_face_y_m']) < 2e-6 or abs(m.bounds[1][1] - info['bearing_face_y_m'])
               < 2e-6, f'{pid}: not on the truss face')
        xs = m.vertices[:, 0]
        w0, w1 = info['fb_web_faces_m']
        expect(np.isclose(xs, w0, atol=2e-6).sum() >= 4 and np.isclose(xs, w1, atol=2e-6).sum() >= 4,
               f'{pid}: web legs not on the floor-beam web')
    for pid, info in s03.items():
        expect(np.isclose(new[pid].vertices[:, 0], info['face_x_m'], atol=2e-6).sum() >= 8, f'{pid}: feet off the face')

    # ---------------------------------------------------------------- manifest entries.
    def update(pid, note, dims=None, pages=None, basis=None, name=None):
        p = parts[pid]
        m = new[pid]
        p['bounds_m'] = m.bounds.round(6).tolist()
        p['volume_m3'] = round(float(m.volume), 7)
        if dims:
            p['dimensions'] = dict(p.get('dimensions') or {}, **dims)
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

    for pid, info in s01.items():
        update(pid, f'Rev. 1.4 (3D review S01): the rear flange is moved {info["gap_before_mm"]:.2f} mm onto the roadway '
                    f'face of the web of {info["vertical"]}, between its flanges, so the post bears on the truss '
                    'vertical over its full height; it stopped short with no bracket. Sheet 7 draws the retained rail '
                    'fastened at the inner face of each truss vertical and clear of the 6 in curb (the 15 mm curb gap '
                    'is as drawn). Rail, front flange and bolts unchanged; depth fitted.',
               dims=dict(flange_width_in=4.0, depth_in=info['depth_in']), pages=[7])
    for k in range(10):
        for side in ('X', 'Y'):
            pid = f'FB{k}_connection_{side}'
            info = s02[pid]
            if k in (0, 9):
                where = (f'the roadway face of the inner new end gusset {info["support"]} (sheet 17 Section A-A); its '
                         'drilled 7/8 in bolt columns 2 3/4 in each side of the floor-beam centre line pass through '
                         'the outstanding legs')
            else:
                where = (f'the roadway face of the web of {info["support"]}, fitted between its flanges (outstanding '
                         f'legs {info["outstanding_leg_in"][0]:.2f} in; sheet 18 Section F-F draws about 4 in)')
            cut = sorted({n for h in info['trimmed'] for n in h['parts']})
            trim = (' Trimmed to the modelled ' + ', '.join(cut) + ' where they reach into the connection.') if cut else ''
            update(pid, 'Rev. 1.4 (3D review S02): refitted as a back-to-back pair on the floor-beam web (sheet 18 '
                        'temporary truss support retrofit detail and Section F-F; sheet 17 Section A-A): each web leg '
                        f'lies on one face of the 5/8 in web and the outstanding legs bear on {where}. Before, the '
                        f'first toe was {info["toe_gap_before_mm"]:.2f} mm off the web, the second angle outside the '
                        'flange and the outstanding legs on the truss centre line inside the truss member' +
                        (', web legs outside it.' if side == 'X' else '.') + trim +
                        ' 7/16 in thickness, 5 in web leg, 30 in length and elevation unchanged.',
                   dims=dict(thickness_in=0.4375, web_leg_in=5.0, outstanding_leg_in=info['outstanding_leg_in'],
                             length_in=30.0), pages=[17, 18])
            update(f'{pid}_bolts', 'Rev. 1.4 (3D review S02): five 7/8 in through-bolts (6 in pitch, 2.4 in from the '
                                   'angle heel as before) through both web legs and the floor-beam web, head and nut '
                                   'on the outer leg faces; they were 10 bolts through one leg only, off the web. '
                                   'Holes are not modelled, as for the other fasteners.' +
                                   (' The lowest heads / nuts reach into the modelled ' +
                                    ', '.join(sorted(info['bolt_hardware_in_member_ends_m3'])) + ' end envelope.'
                                    if info['bolt_hardware_in_member_ends_m3'] else ''),
                   dims=dict(bolts=5, diameter_in=0.875, grip_in=1.5), pages=[17, 18])
    for gbid, info in values['S02_end_gusset_bolts'].items():
        extra = ', and one washer and nut at the angle toe' if info['bolts_moved'] == 21 else ''
        update(gbid, f'Rev. 1.4 (3D review S02): the roadway-side heads (Y truss: washers and nuts) of the 20 bolts '
                     f'in the two floor-beam connection columns{extra} now bear on the reinstalled connection angles '
                     f'laid on the gusset (moved {", ".join(f"{abs(x):.2f}" for x in info["head_or_nut_move_mm"])} mm, '
                     'shanks lengthened to them; sheet 17 Section A-A).', pages=[17])
    for pid, info in s03.items():
        where = 'pier cap face' if info['concrete'].endswith('cap') else 'pier stem face (7 in behind the cap face)'
        update(pid, 'Rev. 1.4 (3D review S03): the bracket is refitted to the sheet 26 pipe connection detail: a 1/4 x '
                    '2 in U-bracket with its cross bar against the strap ring on the pier side, legs in line with the '
                    f'ring and feet on the {where}, anchored by two 1/2 x 1 1/2 in bolts in standard 1/2 in concrete '
                    'inserts 4 3/4 in each side of the pipe centre line (1 1/4 in embedment; heads not modelled). '
                    f'The old 6 in bar ran away from the pier and the assembly stopped {info["gap_before_mm"]:.2f} mm '
                    'short of the concrete. Foot ends 5 1/2 in from the pipe centre line (scaled on the 4 3/4 in '
                    'dimension of the no-scale detail); strap ring, elevation and pipe route unchanged.',
               dims=dict(anchor_bolt='1/2 x 1 1/2 in', anchor_offset_in=4.75,
                         standoff_in=info['standoff_in']), pages=[26],
               basis='Dimensioned bar and anchor sizes (sheet 26); fitted lengths')
    for pid in new:
        check_bodies(pid, new[pid])
        expect(np.abs(np.array(parts[pid]['bounds_m']) - new[pid].bounds).max() < 1e-6, f'{pid} bounds')
    for item in manifest.get('detail_coverage', []):
        if item.get('feature') == 'Drainage':
            item['detail'] += (' Pipe clamps on 1/4 x 2 in U-brackets anchored to the pier cap and stem faces with '
                               '1/2 in bolts in concrete inserts (p26 pipe connection detail).')
        elif item.get('feature') == 'Verticials, diagonals and floor system':
            item['detail'] += (' Floor-beam end angles are back-to-back pairs on the floor-beam web bearing on the '
                               'roadway face of the truss (pp17, 18); retained rail posts bear on the verticals (p7).')
            item['sources'] = sorted(set(item['sources']) | {17})
    expect(set(parts) == set(meshes) == {p['id'] for p in manifest['parts']} and len(parts) == 1052, 'final part list')
    expect(sum(1 for p in manifest['parts'] if p['layer'] == 'gussets') == manifest['layers']['gussets']['count'] == 89,
           'gusset layer count')

    while len(binary) % 4:
        binary.append(0)
    gltf['buffers'][0]['byteLength'] = len(binary)
    encoded = json.dumps(gltf, ensure_ascii=True, separators=(',', ':')).encode()
    encoded += b' ' * ((-len(encoded)) % 4)
    out = (struct.pack('<III', 0x46546c67, 2, 28 + len(encoded) + len(binary)) +
           struct.pack('<II', len(encoded), 0x4e4f534a) + encoded + struct.pack('<II', len(binary), 0x004e4942) + binary)
    backup.mkdir(parents=True, exist_ok=True)
    (backup / f'{BID}_before_3d_review.glb').write_bytes(original)
    (backup / f'{BID}_manifest_before_3d_review.json').write_bytes(raw_manifest)
    path.write_bytes(out)

    changed = sorted(new)
    manifest[TAG_KEY] = TAG
    manifest['revision'] = REVISION
    manifest[RECORD_KEY] = dict(
        review='3D placement review, round 4', follows=PREVIOUS_TAG, previous_revision=PREVIOUS_REVISION,
        source_pdf_pages=[7, 16, 17, 18, 26], printed_sheets=[7, 16, 17, 18, 26],
        native_axes='X = station from Sta. 42+54.00, Y = transverse (+Y = X-truss side, left looking up-station), '
                    'Z = elevation - 778 ft; GLB (X, Z, -Y)',
        findings=[
            dict(id='S01', verdict='resolve',
                 summary='16 intermediate metal-rail posts stopped 57.28 mm short of the truss vertical web with no '
                         'bracket; the rear flange now bears on the roadway face of the vertical web',
                 basis='sheet 7 typical sections draw the retained rail fastened at the inner face of each truss '
                       'vertical, clear of the 6 in curb; the 15.24 mm rail/curb gap is as drawn'),
            dict(id='S02', verdict='resolve',
                 summary='20 floor-beam end angle pairs were 42.86 mm off the web (second angle outside the flange) '
                         'with the outstanding legs on the truss centre line; now back-to-back on the floor-beam web, outstanding legs on the '
                         'roadway face of the vertical web (FB1-FB8, 4.12 in legs between the flanges) or of the inner '
                         'end gusset (FB0, FB9); bolts refitted as five through-bolts; end-gusset bolt heads/nuts in '
                         'the angle footprint moved onto the angle; angles trimmed to the modelled chord/diagonal '
                         'ends',
                 basis='sheet 18 temporary truss support retrofit detail and Section F-F (FB1: pair on the web, '
                       'outstanding legs about 4 in on the vertical); sheet 17 Section A-A (FB0 on the inner gusset); '
                       'sheet 18 gusset detail bolt columns'),
            dict(id='S03', verdict='resolve',
                 summary='12 drain clamp brackets (6 in bar pointing away from the pier) stopped 17.78 mm short of the '
                         'cap and 195.58 mm short of the stem; now 1/4 x 2 in U-brackets with feet on the cap / stem '
                         'face and two 1/2 x 1 1/2 in anchors in concrete inserts',
                 basis='sheet 26 pipe connection detail (bar size, anchors, 4 3/4 in offset; no scale) and Section '
                       'X-X / elevation (clamps on the cap and on the stem)'),
            dict(id='S04', verdict='resolve',
                 summary='lateral_gusset_i_1 (i = 0..4) were exact copies of lateral_gusset_i_-1; the copies are '
                         'removed (0.004424569 m3 counted twice)',
                 basis='sheet 16 plan: one central connection per lower-lateral crossing')],
        decisions=[
            'S03 foot length: the sheet 26 detail is not to scale; the foot ends 5 1/2 in from the pipe centre line, '
            'the washer edge scaled on the dimensioned 4 3/4 in bolt offset.',
            'S02 at FB1-FB8: the model turns the 10WF33 verticals 90 degrees from sheets 7 and 18 (web in the truss '
            'plane); the angles are fitted to the modelled vertical (roadway face of its web, between the flanges) '
            'rather than re-orienting the verticals, which no finding asked for.'],
        kept_deviations=[],
        changed_parts=changed, added_parts=[], removed_parts=removed,
        values=values, before_glb_sha256=before, after_glb_sha256=hashlib.sha256(out).hexdigest())
    text = json.dumps(manifest, ensure_ascii=False, indent=2) + '\n'
    if b'\r\n' in raw_manifest:
        text = text.replace('\n', '\r\n')
    mp.write_bytes(text.encode('utf-8'))
    print(json.dumps({k: v for k, v in manifest[RECORD_KEY].items() if k not in ('values', 'findings')}, indent=1))
    print(f'{len(changed)} parts changed, {len(removed)} removed')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--base', type=Path, default=BASE, help='bridge folder (default: the repository copy)')
    parser.add_argument('--backup', type=Path, default=BACKUP, help='backup folder')
    args = parser.parse_args()
    correct(args.base, args.backup)

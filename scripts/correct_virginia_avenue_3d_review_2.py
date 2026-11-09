"""Fifth round (second 3D review) of Virginia Avenue over I-65 NB / I-70 EB (virginia-avenue): the four retained 1971
wing walls as drawn. Runs after scripts/correct_virginia_avenue_3d_review.py (manifest review_correction_3d
'bay1-intermediate-frames-conn-plates', revision 1.4-3d-review). Every GLB buffer it does not replace is kept: the four
wing meshes get new accessors and four wing footing meshes (and nodes) are added. No part is removed.

    python scripts/correct_virginia_avenue_3d_review_2.py [--dry-run] [--base DIR] [--backup DIR]

Finding (second 3D review): the wings wing_1_-1, wing_1_1, wing_2_-1 and wing_2_1 were 'approximate 20 ft parallel
envelopes', 0.36 m slabs along the coping lines with a flat top at Z 5.75 / 5.73, below the bridge seat and about 2.5 m
below the approach slabs, so the approach fill stood above them with nothing retaining it.

Sources. Existing plans 9548460 (1971 plans, drawings S-2 to S-6 = PDF 60 to 64; the abutments and wings are retained):
- S-2 general plan (PDF 60): Wing A and Wing B at Abutment 1, Wing C and Wing D at Abutment 2; A and C at plan top,
  which is the left side looking up-station (+Y, south), B and D at plan bottom (-Y, north).
- S-3 / S-5 Abutment 1 / 2 details (PDF 61 / 63): cap plans with the splay of each wing from the abutment line (Wing A
  and Wing D 24 deg 30 min 00 sec, Wing B and Wing C 65 deg 30 min 00 sec), the C/L of the 1 in expansion joint in the
  wall 2 ft 6 3/4 in from the W.P. (C/L top shoes on the roadway centre line), toward Wing A / Wing D; wing footing
  plans (16 ft 0 in wide, as long as the wing); elevations with the wing footings stacked on the abutment footing.
- S-4 / S-6 sections (PDF 62 / 64): Elevations Wing A to D (length from the C/L 1 in open joint, top elevation at the
  joint end, a 1 ft 0 in level top, top elevation at the tip, wing footing top); Section B-B (wing: 1 ft 2 in top,
  front face plumb, back face plumb down to 10 ft 0 in above the footing and battered to 2 ft 6 in at the footing;
  footing 16 ft 0 in x 2 ft 0 in, toe 2 ft 6 in, heel 11 ft 0 in); Section A-A (stem and cap front face 1 ft 4 1/2 in
  ahead of the C/L of the anchor plates, i.e. the bearing line; footing levels); Section E-E (plan of the stem: front
  face 46 ft 9 1/4 in and 41 ft 4 3/4 in from the middle joint to the corners toward Wings B / C and A / D, then 1 ft 0 in
  returns along the wing lines, 4 ft 11 1/4 in and 8 ft 3 1/2 in along the front face, to the C/L of the 1 in joints).
Primary set 9683637 (drawings.pdf): sheet 31 profile grade (P.G. El. 732.06 at C/L brg. Abut. No. 1, 731.52 at No. 2);
sheet 32 removal details plan, which draws the existing wings outside the removal limits, and sheet 38 abutment
elevations, which draw them in the background: the 2026 contract leaves the wings as they are (no removal, no new
work on sheets 32, 38, 41 to 47).

Datum. The model's linear profile grade passes through the sheet 31 P.G. elevations at both bearing lines, so
Z = 0.3048 El - 214.6496 m. Checks (1971 values): Abutment 2 footing top El. 706.30 -> Z 0.631 and bottom 704.30 -> 0.021
(footing_2 envelope 0.65 / 0.0); bridge seats El. 724.225 / 724.295 -> 6.094 / 6.116 (model seat datum 6.003 / 5.979,
taken from nominal bearing stacks); Abutment 1 footing El. 707.23 / 705.23 -> 0.914 / 0.305 (footing_1 envelope 0.65 /
0.0). Plan: the reconstructed wing faces lie within about 0.2 m of the existing wings drawn on the 2026 sheet 32 plan.

What is modelled (per wing; Abutment 2 is the 180 deg point image of Abutment 1, as S-5 / S-6 mirror S-3 / S-4):
- wing wall from the C/L of the 1 in open joint (+1/2 in) to the tip, outer (front) face plumb on the drawn wing line,
  1 ft 2 in top, back face battered below the drawn construction joint to 2 ft 6 in at the wing footing top; top level
  at the joint-end elevation for 1 ft 0 in, then straight to the tip elevation; square tip;
- abutment return (S-4 / S-6 Section E-E), 1 ft 0 in thick on the same outer face line, from the end face of the
  abutment envelope (coping line, where the abutment_1 / abutment_2 envelopes end) to the C/L of the joint (-1/2 in),
  top at the wing's joint-end elevation (S-3 / S-5 elevations), bottom at the abutment footing top; it is in the wing
  part so that the wing meets the abutment wall;
- wing footing (new part, layer foundations, hidden by default like footing_1 / footing_2): 16 ft 0 in wide (toe
  2 ft 6 in outside the outer face), from the C/L of the joint to the tip, top at the drawn wing footing top, bottom at
  the drawn abutment footing top, raised to the top of the footing_2 envelope at Abutment 2 (19 mm).
Rebar, keyways, drains, joint fillers and chamfers are not modelled.

Requires numpy, trimesh, shapely and manifold3d, plus the four earlier Virginia Avenue correction scripts.
"""
import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

import numpy as np
import trimesh as tm
from shapely.geometry import Polygon
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import correct_virginia_avenue_3d_review as fourth  # noqa: E402  (imports the earlier rounds and their fallbacks)
from refresh_geometry_verification import bodies  # noqa: E402  (its closed-mesh test, read only)

first = fourth.first
BID = first.BID
BASE = ROOT / 'data/bridges' / BID
BACKUP = ROOT / 'data/fem_research'
TAG_KEY = 'review_correction_3d_2'
RECORD_KEY = 'review_correction_record_3d_2'
TAG = 'wings-a-to-d-as-drawn-1971'
REVISION = '1.5-3d-review-2'
PREVIOUS_TAG_KEY, PREVIOUS_TAG, PREVIOUS_REVISION = fourth.TAG_KEY, fourth.TAG, fourth.REVISION
EXPECTED_GLB_SHA256 = '61d74bf6721c2ce4946d12c1a0a0ddb7570a4b0e937d091dca3d292ccbce0552'   # revision 1.4 output
EXPECTED_DEVIATIONS = {'jacking-frame-end-connections', 'bay1-intermediate-frame-gussets'}
SOURCE_ID = '9548460'
DEV_ID = 'wing-footing-levels'

FT, IN = 0.3048, 0.0254
SPAN, HALF_W = first.SPAN, first.WIDTH / 2
T = np.tan(np.radians(first.SKEW))
D = np.array([-T, 1.0]) / np.hypot(T, 1.0)          # along the Abutment 1 bearing line toward +Y
N_FILL = np.array([-1.0, -T]) / np.hypot(T, 1.0)    # normal to it toward the Abutment 1 fill (down-station)
PG = {1: 732.06, 2: 731.52}                         # sheet 31: P.G. El. at C/L brg. Abut. No. 1 / No. 2 (Line "Vir")
ENVELOPE_FOOTING_TOP = .65                          # footing_1 / footing_2 envelopes: Z 0 to 0.65 m

# 1971 abutments (S-3 to S-6): bridge seat (lowest, at the wall end), abutment footing bottom / top, wing footing top
# (= wing stem base), wing construction joint (10 ft 0 in above it, where the back-face batter starts).
ABUT = {1: dict(sheets='S-3, S-4', pdf_pages=[60, 61, 62], seat=724.225, footing=(705.23, 707.23), stem_base=709.23,
                batter=719.23),
        2: dict(sheets='S-5, S-6', pdf_pages=[60, 63, 64], seat=724.295, footing=(704.30, 706.30), stem_base=708.30,
                batter=718.30)}
# Wings: part id -> 1971 wing. root / tip: top elevation at the joint end / tip (S-4, S-6 elevations); ground: proposed
# ground line on the front face at the joint end / tip (same elevations, used for the record only).
WINGS = {'wing_1_-1': dict(abut=1, label='A', kind='long', side='south', root=732.78, tip=725.85, ground=(712.97, 724.85)),
         'wing_1_1': dict(abut=1, label='B', kind='short', side='north', root=732.72, tip=722.65, ground=(712.02, 721.65)),
         'wing_2_-1': dict(abut=2, label='C', kind='short', side='south', root=732.48, tip=723.05, ground=(712.27, 722.05)),
         'wing_2_1': dict(abut=2, label='D', kind='long', side='north', root=732.10, tip=722.30, ground=(711.37, 721.51))}
# Long wings (A, D) and short wings (B, C): splay from the abutment line toward the fill (S-3 / S-5), length from the C/L
# of the 1 in open joint (S-4 / S-6 elevations), stem front face from the middle joint to the corner and return along
# the front face from the corner to the C/L of the joint (Section E-E).
KIND = {'long': dict(splay=24.5, length=(48 + 6.5 / 12) * FT, front=(41 + 4.75 / 12) * FT, ret=(8 + 3.5 / 12) * FT,
                     splay_text='24 deg 30 min', length_text='48 ft 6 1/2 in', ret_text='8 ft 3 1/2 in'),
        'short': dict(splay=65.5, length=(19 + 6.75 / 12) * FT, front=(46 + 9.25 / 12) * FT, ret=(4 + 11.25 / 12) * FT,
                      splay_text='65 deg 30 min', length_text='19 ft 6 3/4 in', ret_text='4 ft 11 1/4 in')}
JOINT_FROM_WP = (2 + 6.75 / 12) * FT      # S-3 / S-5: C/L 1 in exp. jt. in the wall from the W.P., toward Wing A / D
STEM_FRONT = (1 + 4.5 / 12) * FT          # Section A-A: stem / cap front face ahead of the C/L of the anchor plates
TOP_T, BASE_T = 14 * IN, 30 * IN          # Section B-B: 1 ft 2 in top, 2 ft 6 in at the wing footing
RETURN_T = 12 * IN                        # Section E-E: 1 ft 0 in returns
LEVEL = 1 * FT                            # wing elevations: 1 ft 0 in level top from the C/L of the joint
JOINT = 1 * IN                            # 1 in open joint between the abutment return and the wing
TOE, FOOT_W = 30 * IN, 16 * FT            # Section B-B / wing footing plans: toe 2 ft 6 in, 16 ft 0 in wide
TOUCH = 2e-5                              # contact tolerance on float32 storage (about 4 um at X = 43 m)
NO_OVERLAP_CM3 = .05                      # float32 slack on touching faces


def datum():
    """Offset of Z = 0.3048 El - offset: the model grade passes through the sheet 31 P.G. at both bearing lines."""
    o1 = FT * PG[1] - float(first.grade(-SPAN / 2))
    o2 = FT * PG[2] - float(first.grade(SPAN / 2))
    if abs(o1 - o2) > 1e-6:
        raise ValueError(f'profile grade does not pass through both P.G. elevations ({o1}, {o2})')
    return (o1 + o2) / 2


OFFSET = datum()


def z_of(el):
    return FT * el - OFFSET


def rot(v, deg):
    r = np.radians(deg)
    return np.array([np.cos(r) * v[0] - np.sin(r) * v[1], np.sin(r) * v[0] + np.cos(r) * v[1]])


def plan(pid):
    """Plan of one wing: joint point J on the outer face, wing direction, inward normal (toward the fill), stem corner
    and the coping line the abutment envelope ends on. Abutment 1 from S-3 / S-4; Abutment 2 is its point image."""
    w = WINGS[pid]
    k = KIND[w['kind']]
    wp = np.array([-SPAN / 2, 0.0])
    if w['kind'] == 'long':           # Abutment 1 Wing A at +Y: turns 24 deg 30 min from the abutment line to the fill
        s, direction = JOINT_FROM_WP + k['front'], rot(D, k['splay'])
        inward = np.array([-direction[1], direction[0]])
    else:                             # Abutment 1 Wing B at -Y: turns 65 deg 30 min
        s, direction = JOINT_FROM_WP - k['front'], rot(-D, -k['splay'])
        inward = np.array([direction[1], -direction[0]])
    corner = wp + s * D - STEM_FRONT * N_FILL
    joint = corner + k['ret'] * direction
    y_end = HALF_W if w['kind'] == 'long' else -HALF_W
    if w['abut'] == 2:
        corner, joint, direction, inward, y_end = -corner, -joint, -direction, -inward, -y_end
    if np.sign(inward[1]) != -np.sign(y_end):
        raise ValueError(f'{pid}: inward normal does not point to the roadway')
    return dict(joint=joint, dir=direction, inward=inward, corner=corner, y_end=y_end)


def solid(sections, cap):
    """Closed solid from cross-sections with the same vertex count (consecutive sections joined by planar quads);
    `cap` triangulates one section (indices into it)."""
    n = len(sections[0])
    verts = np.array([p for sec in sections for p in sec], float)
    faces = []
    for k in range(len(sections) - 1):
        for j in range(n):
            a, b = k * n + j, k * n + (j + 1) % n
            faces += [(a, b, b + n), (a, b + n, a + n)]
    faces += [tuple(t[::-1]) for t in cap]
    faces += [tuple(np.array(t) + (len(sections) - 1) * n) for t in cap]
    mesh = tm.Trimesh(verts, np.array(faces), process=False)
    tm.repair.fix_winding(mesh)
    tm.repair.fix_inversion(mesh)
    if not mesh.is_watertight or not mesh.is_winding_consistent or mesh.volume <= 0:
        raise ValueError('invalid solid')
    return mesh


def build(pid):
    """Wing part (abutment return + wing wall) and wing footing of one wing, with the facts the record keeps."""
    w = WINGS[pid]
    k, a = KIND[w['kind']], ABUT[w['abut']]
    p = plan(pid)
    J, d, n = p['joint'], p['dir'], p['inward']

    def at(s, off, z):
        q = J + s * d + off * n
        return (q[0], q[1], z)

    z_root, z_tip = z_of(w['root']), z_of(w['tip'])
    z_base, z_batter = z_of(a['stem_base']), z_of(a['batter'])
    z_low = max(z_of(a['footing'][1]), ENVELOPE_FOOTING_TOP)       # drawn abutment footing top, not into footing_2
    L = k['length']

    def top(s):
        return z_root if s <= LEVEL else z_root + (z_tip - z_root) * (s - LEVEL) / (L - LEVEL)

    # wing wall: sections across the wing at the joint face, the end of the level top and the tip
    wall = solid([[at(s, 0, z_base), at(s, BASE_T, z_base), at(s, TOP_T, z_batter), at(s, TOP_T, top(s)), at(s, 0, top(s))]
                  for s in (JOINT / 2, LEVEL, L)], [(0, 1, 2), (0, 2, 3), (0, 3, 4)])

    # abutment return: from the coping-line end face of the abutment envelope (plane Y = y_end) to the joint face
    def s_end(off):
        return (p['y_end'] - J[1] - off * n[1]) / d[1]
    s0, s1 = s_end(0.0), s_end(RETURN_T)
    if max(s0, s1) >= -JOINT / 2 - .1:
        raise ValueError(f'{pid}: return too short')
    ret = solid([[at(s0, 0, z_low), at(s1, RETURN_T, z_low), at(s1, RETURN_T, z_root), at(s0, 0, z_root)],
                 [at(-JOINT / 2, 0, z_low), at(-JOINT / 2, RETURN_T, z_low), at(-JOINT / 2, RETURN_T, z_root),
                  at(-JOINT / 2, 0, z_root)]], [(0, 1, 2), (0, 2, 3)])
    if np.count_nonzero(np.abs(ret.vertices[:, 1] - p['y_end']) < 1e-9) != 4:
        raise ValueError(f'{pid}: return end not on the coping line')

    # wing footing: toe 2 ft 6 in outside the outer face, 16 ft 0 in wide, from the C/L of the joint to the tip
    footing = solid([[at(s, -TOE, z_low), at(s, FOOT_W - TOE, z_low), at(s, FOOT_W - TOE, z_base), at(s, -TOE, z_base)]
                     for s in (0.0, L)], [(0, 1, 2), (0, 2, 3)])
    info = dict(joint_outer_xy_m=[round(float(v), 6) for v in J], direction_deg=round(float(np.degrees(np.arctan2(d[1], d[0]))), 6),
                stem_front_corner_xy_m=[round(float(v), 6) for v in p['corner']],
                tip_outer_xy_m=[round(float(v), 6) for v in J + L * d],
                return_outer_face_m=round(float(-JOINT / 2 - s0), 6), return_inner_face_m=round(float(-JOINT / 2 - s1), 6),
                z=dict(root_top=round(z_root, 6), tip_top=round(z_tip, 6), stem_base=round(z_base, 6),
                       batter_start=round(z_batter, 6), return_and_footing_bottom=round(z_low, 6)),
                y_end=p['y_end'])
    return tm.util.concatenate([ret, wall]), footing, info


# ------------------------------------------------------------------------------------------------- checks
def overlap_cm3(a, b):
    return round(fourth.overlap_m3(a, b) * 1e6, 4) + 0.0


def end_face(mesh, y):
    """Union (X, Z) of the faces of a mesh lying in the plane Y = y."""
    keep = (np.abs(mesh.face_normals[:, 1]) > .999) & (np.abs(mesh.triangles[:, :, 1] - y).max(axis=1) < TOUCH)
    polys = [Polygon(t[:, [0, 2]]) for t in mesh.triangles[keep]]
    return unary_union([q for q in polys if q.area > 1e-12])


def ray_top(mesh, x, y):
    z = fourth.second.z_hits(mesh, x, y)
    return float(z.max()) if len(z) else None


def measure(mesh_of, wing_ids, part_ids, new=None):
    """Overlaps of each wing (and its footing, if built) with every part whose bounds meet it; for rebuilt wings, the
    contact with the abutment envelope and the wing footing, and the deck / sidewalk / approach top beside the root."""
    out = {}
    for pid in wing_ids:
        names = [pid] + ([f'wing_footing_{pid[5:]}'] if new else [])
        rec = {}
        for name in names:
            f = mesh_of(name)
            ov = {}
            for q in part_ids:
                if q == name or q in names:
                    continue
                g = mesh_of(q)
                if fourth.boxes_meet(f, g):
                    vol = overlap_cm3(f, g)
                    if vol > 1e-4 or q.split('_')[0] in ('abutment', 'mudwall', 'footing', 'approach', 'walk', 'deck'):
                        ov[q] = vol
            rec[name] = ov
        r = dict(overlaps_cm3=rec, bounds_m=np.round(mesh_of(pid).bounds, 6).tolist(),
                 top_z_m=round(float(mesh_of(pid).bounds[1][2]), 6))
        if new:
            info = new[pid]
            wing, foot = mesh_of(pid), mesh_of(f'wing_footing_{pid[5:]}')
            abut = mesh_of(f'abutment_{pid[5]}')
            y = info['y_end']
            contact = end_face(wing, y).intersection(end_face(abut, y))
            r['abutment_contact_m2'] = round(float(contact.area), 4)
            pieces = sorted(wing.split(only_watertight=False), key=lambda m: m.volume)   # return, wall
            wall = pieces[-1]
            r['wall_on_footing_gap_m'] = round(float(wall.bounds[0][2] - foot.bounds[1][2]), 7) + 0.0
            r['wing_into_own_footing_cm3'] = overlap_cm3(wing, foot)
            r['joint_gap_m'] = round(float(np.linalg.norm(
                pieces[0].vertices[:, None, :2] - wall.vertices[None, :, :2], axis=2).min()), 6)
            J, d = np.array(info['joint_outer_xy_m']), np.radians(info['direction_deg'])
            s_root = -(info['return_outer_face_m'] + JOINT / 2)
            q = J + s_root * np.array([np.cos(d), np.sin(d)])
            inside = q + np.array([0.0, -np.sign(y) * .01])
            tops = [ray_top(mesh_of(name), inside[0], inside[1])
                    for name in ('deck', 'walk_-1', 'walk_1', 'trail_pavers', 'approach_1', 'approach_2')]
            tops = [t for t in tops if t is not None]
            r['beside_root'] = dict(point_xy_m=[round(float(v), 4) for v in inside], top_of_deck_path_or_approach_m=round(max(tops), 4),
                                    wing_top_above_it_m=round(info['z']['root_top'] - max(tops), 4))
            r['footing_bounds_m'] = np.round(foot.bounds, 6).tolist()
        else:
            m = mesh_of(pid)
            x0, x1 = m.bounds[:, 0]
            yc = float(m.bounds[:, 1].mean())
            yy = yc - np.sign(yc) * .25
            tops = []
            for name in ('deck', 'walk_-1', 'walk_1', 'trail_pavers', 'approach_1', 'approach_2'):
                for x in np.linspace(x0, x1, 9):
                    t = ray_top(mesh_of(name), x, yy)
                    if t is not None:
                        tops.append(t)
            r['deck_path_or_approach_top_beside_m'] = [round(min(tops), 4), round(max(tops), 4)]
            r['below_it_m'] = [round(min(tops) - r['top_z_m'], 4), round(max(tops) - r['top_z_m'], 4)]
        out[pid] = r
    return out


# ------------------------------------------------------------------------------------------------- correction
def correct(base=BASE, backup=BACKUP, dry_run=False):
    mp = base / 'model_manifest.json'
    raw_manifest = mp.read_bytes()
    manifest = json.loads(raw_manifest.decode('utf-8'))
    if manifest.get(TAG_KEY) == TAG:
        print('Already corrected.')
        return None
    path = base / 'model.glb'
    original = path.read_bytes()
    before = hashlib.sha256(original).hexdigest()

    def expect(ok, what):
        if not ok:
            raise ValueError(f'{BID}: unexpected starting model ({what})')

    expect(manifest.get(PREVIOUS_TAG_KEY) == PREVIOUS_TAG and manifest.get('revision') == PREVIOUS_REVISION,
           f'run scripts/correct_virginia_avenue_3d_review.py first (revision {manifest.get("revision")})')
    expect(TAG_KEY not in manifest and RECORD_KEY not in manifest, f'{TAG_KEY} already holds {manifest.get(TAG_KEY)}')
    expect(before == EXPECTED_GLB_SHA256 == manifest['review_correction_record_3d']['after_glb_sha256'],
           f'model.glb SHA-256 {before} is not the revision 1.4 output')
    expect({d.get('id') for d in manifest.get('known_deviations', [])} == EXPECTED_DEVIATIONS, 'known deviations')

    length = struct.unpack_from('<I', original, 12)[0]
    gltf = json.loads(original[20:20 + length])
    binary = bytearray(original[28 + length:])
    parts = {p['id']: p for p in manifest['parts']}
    meshes = {m['name']: m for m in gltf['meshes']}
    world = gltf['nodes'][0]
    expect(set(parts) == set(meshes) and len(parts) == 162, 'part list')
    expect(world.get('name') == 'world' and len(world['children']) == 162 and gltf['scenes'] == [{'nodes': [0]}],
           'scene nodes')
    expect(not any(k in nd for nd in gltf['nodes'] for k in ('matrix', 'rotation', 'translation', 'scale')),
           'node transforms')
    expect(all(len(m['primitives']) == 1 for m in gltf['meshes']) and not gltf.get('materials'), 'primitives')
    for pid in WINGS:
        expect(pid in parts and f'wing_footing_{pid[5:]}' not in parts, f'{pid} / wing footing ids')

    def read(ai):
        a = gltf['accessors'][ai]
        view = gltf['bufferViews'][a['bufferView']]
        dtype = {5126: '<f4', 5125: '<u4', 5123: '<u2', 5121: 'u1'}[a['componentType']]
        count = {'SCALAR': 1, 'VEC3': 3, 'VEC4': 4}[a['type']]
        return np.frombuffer(binary, dtype=dtype, count=a['count'] * count,
                             offset=view.get('byteOffset', 0) + a.get('byteOffset', 0)).copy().reshape(-1, count)

    cache = {}

    def glb_mesh(pid):
        if pid not in cache:
            prim = meshes[pid]['primitives'][0]
            v = read(prim['attributes']['POSITION']).astype(np.float64)
            cache[pid] = tm.Trimesh(np.column_stack([v[:, 0], -v[:, 2], v[:, 1]]), read(prim['indices']).reshape(-1, 3),
                                    process=False)
        return cache[pid]

    # ---------------------------------------------------------------- the starting wings: 0.36 m parallel boxes
    old_meta = {}
    for pid, w in WINGS.items():
        m, p = glb_mesh(pid), parts[pid]
        seat = parts[f'abutment_{w["abut"]}']['bounds_m'][1][2]
        y = HALF_W if pid.endswith('_-1') else -HALF_W
        expect(len(m.vertices) == 8 and abs(m.volume - p['volume_m3']) < 1e-4 and
               np.abs(m.bounds - np.array(p['bounds_m'])).max() < 1e-5 and
               abs(m.bounds[0][1] - (y - .18)) < 1e-5 and abs(m.bounds[1][1] - (y + .18)) < 1e-5 and
               abs(m.bounds[0][2] - .65) < 1e-5 and abs(m.bounds[1][2] - (seat - .25)) < 1e-5 and
               abs(m.extents[0] - 20 * FT) < 1e-5 and p['basis'] == 'Historical wing presence; approximate 20 ft parallel envelope',
               f'{pid} is not the 20 ft parallel envelope')
        old_meta[pid] = dict(name=p['name'], bounds_m=p['bounds_m'], volume_m3=p['volume_m3'])
    part_ids = sorted(parts)
    measured_before = measure(glb_mesh, list(WINGS), part_ids)

    # ---------------------------------------------------------------- new wings and wing footings
    new, infos = {}, {}
    for pid in WINGS:
        wing, footing, info = build(pid)
        new[pid], new[f'wing_footing_{pid[5:]}'], infos[pid] = wing, footing, info
    for pid, mesh in new.items():
        parts_of = list(bodies(np.asarray(mesh.vertices, np.float32).astype(np.float64), np.asarray(mesh.faces)))
        expect(all(b.is_watertight and b.volume > 0 for b in parts_of) and len(parts_of) == (2 if pid in WINGS else 1),
               f'{pid}: bodies not closed as stored')

    def out_mesh(pid):
        return fourth.stored(new[pid]) if pid in new else glb_mesh(pid)
    all_ids = sorted(set(part_ids) | set(new))
    measured_after = measure(out_mesh, list(WINGS), all_ids, infos)
    for pid, r in measured_after.items():
        worst = max([0.0] + [v for ov in r['overlaps_cm3'].values() for v in ov.values()])
        expect(worst <= NO_OVERLAP_CM3, f'{pid}: overlap {worst} cm3 {r["overlaps_cm3"]}')
        expect(r['abutment_contact_m2'] > 1.0, f'{pid}: does not meet the abutment wall ({r["abutment_contact_m2"]} m2)')
        expect(abs(r['wall_on_footing_gap_m']) <= TOUCH and r['wing_into_own_footing_cm3'] <= NO_OVERLAP_CM3,
               f'{pid}: wall not on its footing')
        expect(abs(r['joint_gap_m'] - JOINT) < 1e-4, f'{pid}: joint {r["joint_gap_m"]}')
        expect(abs(r['top_z_m'] - infos[pid]['z']['root_top']) < 1e-5, f'{pid}: top')
        expect(-.05 < r['beside_root']['wing_top_above_it_m'] < .25, f'{pid}: wing top beside the root {r["beside_root"]}')

    # ---------------------------------------------------------------- write the GLB
    acc_cache = {}

    def append(array, kind, component):
        data = array.tobytes()
        key = (kind, component, len(array), hashlib.sha256(data).hexdigest())
        if key in acc_cache:
            return acc_cache[key]
        while len(binary) % 4:
            binary.append(0)
        view = len(gltf['bufferViews'])
        gltf['bufferViews'].append(dict(buffer=0, byteOffset=len(binary), byteLength=len(data)))
        binary.extend(data)
        a = dict(bufferView=view, componentType=component, count=len(array), type=kind)
        if kind == 'VEC3':
            a.update(min=array.min(axis=0).tolist(), max=array.max(axis=0).tolist())
        gltf['accessors'].append(a)
        acc_cache[key] = len(gltf['accessors']) - 1
        return acc_cache[key]

    for ai, a in enumerate(gltf['accessors']):      # reuse identical colour / index arrays
        if a['type'] in ('SCALAR', 'VEC4'):
            arr = read(ai)
            acc_cache.setdefault((a['type'], a['componentType'], len(arr), hashlib.sha256(arr.tobytes()).hexdigest()), ai)

    def primitive(mesh, color):
        rgb = [int(color[i:i + 2], 16) for i in (1, 3, 5)] + [255]
        prim = dict(attributes=dict(POSITION=append(fourth.to_gltf(mesh.vertices).astype('<f4'), 'VEC3', 5126),
                                    COLOR_0=append(np.tile(np.array(rgb, 'u1'), (len(mesh.vertices), 1)), 'VEC4', 5121)),
                    indices=append(mesh.faces.reshape(-1, 1).astype('<u4'), 'SCALAR', 5125), mode=4)
        gltf['accessors'][prim['attributes']['COLOR_0']]['normalized'] = True
        return prim

    # ---------------------------------------------------------------- manifest entries
    meta_keys = ('id', 'name', 'layer', 'color', 'pdf_pages', 'basis', 'note', 'dimensions')
    footing_color = parts['footing_1']['color']
    old_note = ('Source wings are splayed and battered. Their exact plan and top profile remain incomplete. ')
    added = []
    for pid, w in WINGS.items():
        k, a, info, p = KIND[w['kind']], ABUT[w['abut']], infos[pid], parts[pid]
        expect(p['note'].startswith(old_note), f'{pid}: note')
        fid = f'wing_footing_{pid[5:]}'
        refs = [dict(source_id='9683637', pdf_pages=[31, 32, 38]), dict(source_id=SOURCE_ID, pdf_pages=a['pdf_pages'])]
        z = info['z']
        p['name'] = f'Abutment {w["abut"]} | retained {w["side"]} wing (1971 Wing {w["label"]}) with abutment return'
        p['pdf_pages'] = [31, 32, 38]
        p['basis'] = (f'Existing plans 9548460 {a["sheets"]} and S-2 (PDF {", ".join(map(str, a["pdf_pages"]))}): '
                      f'Wing {w["label"]} plan, section and top elevations; retained unchanged by the 2026 contract '
                      '(sheets 32, 38)')
        p['note'] = (p['note'][len(old_note):] + ' 3D review correction 1.5: rebuilt as the 1971 plans draw Wing '
                     f'{w["label"]} ({a["sheets"]}). Splayed {k["splay_text"]} from the abutment line toward the fill, '
                     f'{k["length_text"]} long from the C/L of the 1 in open joint; outer face plumb, 1 ft 2 in top, back '
                     f'face battered from El. {a["batter"]:.2f} to 2 ft 6 in at the wing footing top El. '
                     f'{a["stem_base"]:.2f}; top El. {w["root"]:.2f} at the joint end, level for 1 ft 0 in, falling '
                     f'straight to El. {w["tip"]:.2f} at the tip (Z {z["root_top"]:.3f} to {z["tip_top"]:.3f}; the '
                     'envelope was flat at Z ' f'{old_meta[pid]["bounds_m"][1][2]:.3f}). Includes the 1 ft 0 in '
                     f'abutment return (Section E-E: {k["ret_text"]} along the front face from the stem corner to the '
                     'joint) from the coping-line end of the abutment envelope, top at the joint-end elevation '
                     f'({a["sheets"][:3]} elevation; not dimensioned), bottom at the abutment footing top El. '
                     f'{a["footing"][1]:.2f}; the 1 in joint is a gap. '
                     'Elevations by Z = 0.3048 El - 214.6496 m (sheet 31 P.G. at both bearing lines). Rebar, keyways, '
                     'drains and chamfers omitted.')
        p['dimensions'] = dict(
            wing=f'1971 Wing {w["label"]}', splay_from_abutment_line_deg=k['splay'],
            direction_deg=info['direction_deg'], length_from_joint_m=round(k['length'], 6),
            top_thickness_m=round(TOP_T, 6), base_thickness_m=round(BASE_T, 6),
            batter='back face, from the construction joint to the wing footing top',
            top_el_ft=dict(joint_end=w['root'], tip=w['tip']), level_top_from_joint_m=round(LEVEL, 6),
            top_z_m=dict(joint_end=z['root_top'], tip=z['tip_top']),
            stem_base_el_ft=a['stem_base'], batter_start_el_ft=a['batter'], stem_base_z_m=z['stem_base'],
            joint_outer_xy_m=info['joint_outer_xy_m'], tip_outer_xy_m=info['tip_outer_xy_m'],
            open_joint_m=round(JOINT, 6),
            abutment_return=dict(thickness_m=round(RETURN_T, 6), outer_face_m=info['return_outer_face_m'],
                                 inner_face_m=info['return_inner_face_m'], drawn_from_stem_corner_m=round(k['ret'], 6),
                                 bottom_z_m=z['return_and_footing_bottom']),
            front_ground_el_ft=dict(joint_end=w['ground'][0], tip=w['ground'][1]),
            datum='Z = 0.3048 El - 214.6496 m')
        p['source_refs'] = refs
        mesh = new[pid]
        p['bounds_m'] = np.round(mesh.bounds, 6).tolist()
        p['volume_m3'] = round(float(mesh.volume), 9)
        meshes[pid]['primitives'] = [primitive(mesh, p['color'])]
        ex = meshes[pid].setdefault('extras', {})
        ex.pop('shape', None)
        ex.pop('extents', None)
        ex.update({key: p[key] for key in meta_keys})

        fm = new[fid]
        f = dict(id=fid, name=f'Abutment {w["abut"]} | hidden {w["side"]} wing footing (1971 Wing {w["label"]})',
                 layer='foundations', color=footing_color, pdf_pages=[31, 32],
                 basis=f'Existing plans 9548460 {a["sheets"]} (PDF {", ".join(map(str, a["pdf_pages"][1:]))}): Wing '
                       f'{w["label"]} footing plan and Section B-B',
                 note=(f'Added in 3D review correction 1.5. 16 ft 0 in wide, {k["length_text"]} long from the C/L of '
                       'the 1 in open joint to the tip, toe 2 ft 6 in outside the outer face of the wing, heel 11 ft '
                       f'0 in behind its 2 ft 6 in base; top El. {a["stem_base"]:.2f} (Z {z["stem_base"]:.3f}). Bottom '
                       f'at the abutment footing top El. {a["footing"][1]:.2f}, on which {a["sheets"][:3]} stacks it'
                       + (' (Z 0.914; 0.264 m above the nominal footing_1 envelope, see known_deviations).'
                          if w['abut'] == 1 else
                          ', raised 19 mm to the top of the footing_2 envelope (Z 0.650; see known_deviations).')
                       + ' Rebar and keyway omitted.'),
                 dimensions=dict(width_m=round(FOOT_W, 6), length_m=round(k['length'], 6), toe_m=round(TOE, 6),
                                 heel_m=round(FOOT_W - TOE - BASE_T, 6),
                                 thickness_m=round(z['stem_base'] - z['return_and_footing_bottom'], 6),
                                 top_el_ft=a['stem_base'], bottom_el_ft=a['footing'][1],
                                 top_z_m=z['stem_base'], bottom_z_m=z['return_and_footing_bottom']),
                 bounds_m=np.round(fm.bounds, 6).tolist(), volume_m3=round(float(fm.volume), 9),
                 source_refs=[dict(source_id='9683637', pdf_pages=[31, 32]), dict(source_id=SOURCE_ID, pdf_pages=a['pdf_pages'])])
        manifest['parts'].append(f)
        parts[fid] = f
        gltf['meshes'].append(dict(name=fid, extras={key: f[key] for key in meta_keys}, primitives=[primitive(fm, f['color'])]))
        gltf['nodes'].append(dict(name=fid, mesh=len(gltf['meshes']) - 1))
        world['children'].append(len(gltf['nodes']) - 1)
        added.append(fid)
    meshes = {m['name']: m for m in gltf['meshes']}
    expect(set(parts) == set(meshes) == {p['id'] for p in manifest['parts']} and len(parts) == 166, 'final part list')
    expect(all(nd.get('name') == gltf['meshes'][nd['mesh']]['name'] for nd in gltf['nodes'] if 'mesh' in nd) and
           len(world['children']) == 166, 'node names')

    # ---------------------------------------------------------------- coverage and deviations
    by_feature = {c['feature']: c for c in manifest.get('detail_coverage', [])}
    whole, unresolved = by_feature.get('Whole single-span steel crossing'), by_feature.get('Unresolved geometry')
    expect(whole is not None and set(WINGS) <= set(whole['part_ids']) and unresolved is not None and
           'splayed wings and local abutment batter' in unresolved['detail'], 'detail_coverage')
    whole['part_ids'] += added
    whole['detail'] += (' Retained 1971 wings A to D splayed and battered as drawn, with their abutment returns and '
                        'footings (existing S-2 to S-6).')
    unresolved['detail'] = unresolved['detail'].replace('splayed wings and local abutment batter', 'local abutment batter')
    deviation = dict(
        id=DEV_ID, parts=', '.join(list(WINGS) + added),
        source='existing plans 9548460 S-3 to S-6 (PDF 61 to 64): elevations Abutment 1 / 2, Section A-A, Section B-B',
        deviation='The wing footings and the abutment returns in the wing parts are founded at the drawn abutment '
                  'footing top (El. 707.23 at Abutment 1, 706.30 at Abutment 2), on which the S-3 / S-5 elevations '
                  'stack the wing footings, but the retained footing_1 / footing_2 envelopes are nominal (Z 0 to 0.65 m '
                  'at both abutments). At Abutment 1 the drawn level is Z 0.914, so the Abutment 1 wing footings and '
                  'returns stand 0.264 m clear of footing_1 where they lie over it. At Abutment 2 it is Z 0.631, 19 mm '
                  'below the footing_2 top, so they start at its top (Z 0.650) and the Abutment 2 wing footings are '
                  '1 ft 11 1/4 in thick instead of 2 ft 0 in.',
        reason='Re-founding the abutment footing envelopes is outside this correction: footing_1 / footing_2 are '
               'nominal 17 ft envelopes (drawn: 109 ft 7 1/2 in along the skew, toe 5 ft 0 in, heel 10 ft 0 in, bottom '
               'El. 705.23 / 704.30, i.e. Z 0.305 / 0.021).')
    manifest['known_deviations'].append(deviation)

    # ---------------------------------------------------------------- finish the GLB
    while len(binary) % 4:
        binary.append(0)
    gltf['buffers'][0]['byteLength'] = len(binary)
    encoded = json.dumps(gltf, ensure_ascii=True, separators=(',', ':')).encode()
    encoded += b' ' * ((-len(encoded)) % 4)
    out = (struct.pack('<III', 0x46546c67, 2, 28 + len(encoded) + len(binary)) +
           struct.pack('<II', len(encoded), 0x4e4f534a) + encoded + struct.pack('<II', len(binary), 0x004e4942) + binary)

    # ---------------------------------------------------------------- the record
    checks = dict(
        datum_offset_m=round(OFFSET, 7),
        profile_grade=dict(abutment_1=dict(pg_el=PG[1], z=round(z_of(PG[1]), 6), model=round(float(first.grade(-SPAN / 2)), 6)),
                           abutment_2=dict(pg_el=PG[2], z=round(z_of(PG[2]), 6), model=round(float(first.grade(SPAN / 2)), 6))),
        abutment_2_footing=dict(top_el=706.30, z=round(z_of(706.30), 4), envelope=.65,
                                bottom_el=704.30, z_bottom=round(z_of(704.30), 4), envelope_bottom=0.0),
        abutment_1_footing=dict(top_el=707.23, z=round(z_of(707.23), 4), envelope=.65,
                                bottom_el=705.23, z_bottom=round(z_of(705.23), 4), envelope_bottom=0.0),
        bridge_seats=dict(abutment_1=dict(el=ABUT[1]['seat'], z=round(z_of(ABUT[1]['seat']), 4),
                                          model_seat_datum=parts['abutment_1']['bounds_m'][1][2]),
                          abutment_2=dict(el=ABUT[2]['seat'], z=round(z_of(ABUT[2]['seat']), 4),
                                          model_seat_datum=parts['abutment_2']['bounds_m'][1][2])),
        plan='The reconstructed outer faces lie within about 0.2 m of the existing wings drawn on the 2026 sheet 32 '
             'removal plan (vector linework), which also confirms which wing is which.')
    previous_revision = manifest.get('revision')
    manifest[TAG_KEY] = TAG
    manifest['revision'] = REVISION
    worst = max(v for r in measured_after.values() for ov in r['overlaps_cm3'].values() for v in ov.values())
    tops = {pid: (r['top_z_m'], measured_after[pid]['top_z_m']) for pid, r in measured_before.items()}
    below = [b for r in measured_before.values() for b in r['below_it_m']]
    root = [i['z']['root_top'] for i in infos.values()]
    tip = [i['z']['tip_top'] for i in infos.values()]
    above = [r['beside_root']['wing_top_above_it_m'] for r in measured_after.values()]
    inside = [r['overlaps_cm3'][pid].get(f'abutment_{pid[5]}', 0) / 1e6 for pid, r in measured_before.items()]
    manifest[RECORD_KEY] = dict(
        source='Second 3D review of revision 1.4 (wing envelopes), re-measured on the GLB and re-read against the '
               'drawings',
        follows=PREVIOUS_TAG, previous_revision=previous_revision,
        source_pdf_pages=[31, 32, 38], printed_sheets=[31, 32, 38],
        historical_source=dict(source_id=SOURCE_ID, pdf_pages=[60, 61, 62, 63, 64],
                               printed_sheets=['S-2', 'S-3', 'S-4', 'S-5', 'S-6']),
        native_axes='X increasing station (X = 0 at 13+48.31 "Vir"), Y positive to the left looking up-station (south), '
                    'Z up; GLB (X, Z, -Y)',
        findings={
            'Wing envelopes': 'Resolved. The four wings were 20 ft x 0.36 m slabs along the coping lines with a flat '
                              f'top at Z {tops["wing_1_-1"][0]:.3f} / {tops["wing_2_-1"][0]:.3f}, '
                              f'{min(below):.2f}-{max(below):.2f} m below the deck, path and approach-slab top beside '
                              f'them, so the approach fill stood above them; {min(inside):.2f}-{max(inside):.2f} m3 of '
                              'each lay inside the abutment envelope. They are rebuilt as the 1971 plans draw '
                              'Wings A to D: splayed 24 deg 30 min (A, D, 48 ft 6 1/2 in) and 65 deg 30 min (B, C, 19 ft '
                              '6 3/4 in) from the abutment line, 1 ft 2 in top, back face battered to 2 ft 6 in, top '
                              f'falling from the joint-end elevation (Z {min(root):.3f}-{max(root):.3f}, '
                              f'{min(above):.2f}-{max(above):.2f} m above the path or sidewalk beside the root) to the '
                              f'tip (Z {min(tip):.3f}-{max(tip):.3f}), each with its 1 ft 0 in abutment return '
                              'against the abutment envelope and a 16 ft x 2 ft footing (new parts). Largest overlap '
                              f'with any part {worst:.4f} cm3 (float32 rounding of touching faces).'},
        datum_checks=checks,
        decisions={
            'Wing identities': 'By the drawn geometry, not the ids: S-2 puts Wings A / C at plan top, the left side '
                               'looking up-station (+Y, south), B / D at plan bottom (-Y); A and B at Abutment 1. So '
                               'wing_1_-1 = A, wing_1_1 = B, wing_2_-1 = C, wing_2_1 = D (the long wings A and D are at '
                               'the obtuse corners). The 2026 sheet 32 plan draws them where they are rebuilt.',
            'Plan': 'S-3 / S-5 give the splay from the abutment line (24 deg 30 min, 65 deg 30 min; they sum to 90 deg) '
                    'and the middle wall joint 2 ft 6 3/4 in from the W.P.; Section E-E gives the stem front face to '
                    'its corners (46 ft 9 1/4 in, 41 ft 4 3/4 in) and the returns to the wing joints (4 ft 11 1/4 in, '
                    '8 ft 3 1/2 in); Section A-A puts the stem front face 1 ft 4 1/2 in ahead of the bearing line. '
                    'Abutment 2 is the point image of Abutment 1 (S-5 / S-6 repeat every plan dimension).',
            'Datum': 'Z = 0.3048 El - 214.6496 m: the model grade passes through the sheet 31 P.G. at both bearing '
                     'lines. It matches the drawn Abutment 2 footing to 2 cm; the model seat datum (bearing stacks) is '
                     '9 / 14 cm below the drawn seats and the footing_1 envelope 0.26 / 0.30 m below the drawn '
                     'Abutment 1 footing (both envelopes are unchanged).',
            'Top thickness': 'Section B-B dimensions the top 1 ft 2 in overall (2 in + 1 ft 0 in); 1 ft 2 in is used.',
            'Tip elevations': 'The drawn tip elevations are used (Wing A El. 725.85, Wing B El. 722.65); the height '
                              'dimensions above the wing footing (16 ft 7 1/8 in, 13 ft 4 5/8 in) give 0.03 ft less.',
            'Abutment returns': 'Section E-E draws 1 ft 0 in returns from the stem corners along the wing lines to the '
                                'C/L of the 1 in joints. The abutment_1 / abutment_2 envelopes end at the coping lines, '
                                'so each return is modelled in the wing part from that end face to the joint; its top '
                                'is the wing\'s joint-end elevation (the S-3 / S-5 elevations draw the wall end rising '
                                'to it; not dimensioned) and its bottom the abutment footing top.',
            'Wing footings': 'S-3 / S-5 wing footing plans: 16 ft 0 in x the wing length; Section B-B: 2 ft 0 in, toe '
                             '2 ft 6 in, heel 11 ft 0 in. Modelled from the C/L of the joint to the tip as new parts in '
                             f'the foundations layer (hidden by default, like footing_1 / footing_2); levels: '
                             f'known_deviations {DEV_ID}.',
            '2026 contract': 'No wing work: sheet 32 draws the wings outside the removal limits, sheet 38 draws them '
                             'in the background of the abutment elevations, and the approach sheets 41 to 47 end at the '
                             'coping lines.'},
        changed_parts=list(WINGS), added_parts=added, removed_parts=[],
        before=dict(old_meta, interfaces=measured_before),
        after=dict({pid: dict(bounds_m=parts[pid]['bounds_m'], volume_m3=parts[pid]['volume_m3']) for pid in list(WINGS) + added},
                   interfaces=measured_after, wings=infos),
        before_glb_sha256=before, after_glb_sha256=hashlib.sha256(out).hexdigest())
    for v in manifest[RECORD_KEY]['after']['wings'].values():
        v.pop('y_end', None)
    record = manifest[RECORD_KEY]
    print(json.dumps(dict(changed=list(WINGS), added=added, before=before, after=record['after_glb_sha256'],
                          tops_before_after=tops, interfaces_after=measured_after), indent=1))
    if dry_run:
        print('Dry run, nothing written.')
        return out, manifest
    backup.mkdir(parents=True, exist_ok=True)
    (backup / f'{BID}_before_3d_review_2.glb').write_bytes(original)
    (backup / f'{BID}_manifest_before_3d_review_2.json').write_bytes(raw_manifest)
    path.write_bytes(out)
    text = json.dumps(manifest, ensure_ascii=False, indent=2) + '\n'
    if b'\r\n' in raw_manifest:
        text = text.replace('\n', '\r\n')
    mp.write_bytes(text.encode('utf-8'))
    return out, manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--base', type=Path, default=BASE, help='bridge folder (default: the repository copy)')
    parser.add_argument('--backup', type=Path, default=BACKUP, help='backup folder')
    parser.add_argument('--dry-run', action='store_true', help='measure and report, write nothing')
    args = parser.parse_args()
    correct(args.base, args.backup, args.dry_run)

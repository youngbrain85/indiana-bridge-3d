"""Second drawing-confirmed correction of US 224 over Eight Mile Creek (us224-eight-mile): handedness, TFC transition
sections and the mid-span drain cores. Runs after scripts/correct_us224_eight_mile_review.py and keeps the GLB buffers
it does not replace.

    python scripts/correct_us224_eight_mile_review_2.py [--base DIR] [--backup DIR]

Primary set: INDOT B-44532 / Des 2200957 (drawings.pdf, document 9683628); printed sheet number = PDF page number.
Supplementary: 1985 plans B-16317 (sources/existing_plans_9548292.pdf), cited as "1985 sheet N" (its PDF page N).
Native axes after this correction: X along increasing station (east), Y positive to the LEFT of increasing station
(north), Z up, Z = 0 at El. 817.00. This is the right-handed frame that the manifest's glb_axes mapping (native X,
native Z, -native Y) assumes. The bearing lines are X = u - tan(30 deg) Y.

1. Handedness. Sheet 7 (erosion control plan) and sheet 8 (general plan): the north arrow points up the sheet and the
   stations increase to the right (Begin Project 702+89.28 at the left, End Project 704+20.72 at the right; Line "A"
   bearing N 88 deg 27 min E), so north is left of increasing station (+Y). The abutment lines run from upper left to
   lower right: the north end of each abutment is at the lower station ("30 deg Lt. skew"). Wings A (NW) and C (NE),
   the NW and NE TFC transitions are on the north side; Wings B (SW) and D (SE), the SE transition and the retained SW
   guardrail are on the south side (sheet 8, sheet 12 "Northwest / Northeast Transition Looking North"). The model was
   built with north at Y < 0 and bearing lines X = u + tan30 Y, so in the right-handed frame it was the exact mirror
   image of the drawings: transverse layout and skew sense both reversed. Every vertex is reflected,
   (X, Y, Z) -> (X, -Y, Z), and every triangle's winding is reversed. Stations, grade, crown, elevations and all
   dimensions are unchanged. Part ids keep their geographic meaning: suffix -1 still names the north member
   (retained_rail_-1, TFC_transition_*_-1, extension_*_-1, midspan_drain_-1, wing_0_-1 = Wing A, wing_1_-1 = Wing C)
   and suffix 1 the south member; beam_0_0 / B*_bearing_1 stay the north beam line.

2. TFC transition sections, sheet 12 (Sections C-C, D-D, E-E, F-F and both railing elevations, dimensioned from the
   bridge end in 7 ft 2 in, 11 in, 3 ft 4 in and 4 ft 3 in segments). The model swept one section over the whole
   15 ft 8 in: 1 ft 4 in base, 7 in vertical toe and a single slope to the 9 in top. The drawings give:
   C-C, the first 7 ft 2 in: 1 ft 4 in base, 2 1/2 in vertical toe, 5 in over 7 in to the knee 11 in from the back
   face, then 2 in over the upper 1 ft 10 in to the 9 in top, 2 ft 7 1/2 in high;
   D-D (11 in segment): 11 5/8 in base, 2 1/2 in toe, the upper face continued down (2 5/8 in over 2 ft 5 in);
   E-E (3 ft 4 in segment, "varies 2'-7 1/2" to 2'-9""): 11 in base at the cut, 2 ft 5 in from the top to the toe;
   F-F, the last 4 ft 3 in: 9 in wide with vertical faces, 2 ft 9 in high.
   Sheet 12 gives the sections, not the surface between them; the model holds C-C to 7 ft 2 in, tapers the lower
   (safety-shape) bulge out over the 11 in segment to D-D at 8 ft 1 in, tapers D-D to F-F over the 3 ft 4 in segment
   (where the height also rises, so E-E's 11 in base falls 9 1/2 in into it with the 2 ft 5 in face kept), and holds
   F-F to the end. The height profile of revision 1.1, the back face on the barrier line (7.112 m), the stations and
   the seat on the finished surface are unchanged.

3. Mid-span drains, sheet 9 (proposed typical section "Ex. 2" Cored Deck Drain (To Remain Open At Mid-Span)", Overlay
   at Deck Drain Details, Section D-D): the drains are 2 in cores straight down through the remaining slab at the
   face of rail, left open through the overlay. The model had a closed 2 in rod starting 16 mm below the slab soffit
   and sloping 0.35 m outward, with no opening in the slab (no outlet pipe is drawn). Each drain is now a vertical
   2 in core cut through the deck and the overlay at the same plan position (mid-span, 30 mm inside the face of rail),
   and midspan_drain_* is a 3 mm display skin lining that core from the slab soffit to the finished surface (the
   display convention of the beam-end wraps).

Deferred (known_deviations): the overlay taper to the drain edge (sheet 9: 1 ft each way, depth not dimensioned);
the obtuse-corner wing roots (Wings B and C start at the generator's cap end and stand 50 mm clear of the deck edge;
1985 sheet 5 puts the wing's inner face at the coping corner). The acute-corner-wings entry is corrected to the
measured tip elevations. Not changed: everything else.

Requires numpy, trimesh and manifold3d, plus scripts/correct_us224_eight_mile_review.py (constants and helpers) and
scripts/bridge_geometry.py (rod, for the starting-state check).
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
import correct_us224_eight_mile_review as first  # noqa: E402
from bridge_geometry import rod  # noqa: E402

BID = first.BID
BASE = ROOT / 'data/bridges' / BID
BACKUP = ROOT / 'data/fem_research'
TAG = 'review-2-handedness-tfc-sections-midspan-drain-cores'
PREVIOUS_REVISION = first.REVISION
REVISION = '1.2-drawing-review-2'
FT, IN, K = first.FT, first.IN, first.K
LENGTH, WIDTH = first.LENGTH, first.WIDTH
REMAINING, OVERLAY = 7.5 * IN, 2 * IN          # sheet 9: 7 1/2 in remaining slab, 2 in minimum overlay

# Sheet 12 TFC sections as (inward offset from the back face, height above the finished surface), inches.
# Point order as the generator's rail profile: back-bottom, toe-bottom, toe-top, knee, top-front, top-back.
D_KNEE = 11.625 - 2.625 * 7 / 29                # D-D face (11 5/8 in at 2 1/2 in, 9 in at the top) at the C-C knee level
SECTION_C = [(0, 0), (16, 0), (16, 2.5), (11, 9.5), (9, 31.5), (0, 31.5)]
SECTION_D = [(0, 0), (11.625, 0), (11.625, 2.5), (D_KNEE, 9.5), (9, 31.5), (0, 31.5)]
SECTION_F = [(0, 0), (9, 0), (9, 4), (9, 11), (9, 33), (0, 33)]
# Anchor distances from the bridge end (inches): 7'-2", 8'-1", 11'-5", 15'-8" (sheet 12 railing elevations).
ANCHORS = [(0, SECTION_C), (86, SECTION_C), (97, SECTION_D), (137, SECTION_F), (188, SECTION_F)]
TFC_IDS = (('TFC_transition_-1_-1', -1, -1), ('TFC_transition_1_-1', 1, -1), ('TFC_transition_1_1', 1, 1))

DRAIN_R, SKIN, SEGMENTS = IN, .003, 16           # 2 in core (sheet 9); 3 mm display skin
ORIENT_NOTE = ('Rev. 1.2: reflected to the drawn side, north = +Y, left of increasing station (sheets 7, 8: '
               'north arrow up, stations increasing to the east).')


def section_at(t_in):
    """Sheet 12 section (metres) at t inches from the bridge end, linear between the anchors."""
    for (t0, s0), (t1, s1) in zip(ANCHORS[:-1], ANCHORS[1:]):
        if t0 - 1e-9 <= t_in <= t1 + 1e-9:
            w = 0. if t1 == t0 else (t_in - t0) / (t1 - t0)
            return [(((1 - w) * a0 + w * a1) * IN, ((1 - w) * b0 + w * b1) * IN) for (a0, b0), (a1, b1) in zip(s0, s1)]
    raise ValueError(t_in)


def variable_sweep(stations, sections, fn):
    """first.sweep with a different (same-size) profile at every station; caps triangulated per end."""
    n = len(sections[0])
    v = [fn(float(x), float(a), float(b)) for x, sec in zip(stations, sections) for a, b in sec]
    f = []
    for k in range(len(stations) - 1):
        for j in range(n):
            a, b = k * n + j, k * n + (j + 1) % n
            f.extend([(a, b, b + n), (a, b + n, a + n)])
    f.extend(tuple(q[::-1]) for q in first.triangulate(sections[0]))
    f.extend(tuple(q + (len(stations) - 1) * n) for q in first.triangulate(sections[-1]))
    m = trimesh.Trimesh(np.array(v, float), np.array(f), process=True)
    if m.volume < 0:
        m.invert()
    if not m.is_watertight or not m.is_winding_consistent or m.volume <= 0:
        raise ValueError('invalid swept solid')
    return m


def tfc_mesh(end, side):
    """Old (generator) frame: TFC from the deck end outward, back face on the barrier line, seated on the surface."""
    a, b = sorted([end * LENGTH / 2, end * (LENGTH / 2 + first.TFC_LEN)])
    breaks = [end * (LENGTH / 2 + t * IN) for t, _ in ANCHORS[1:-1]]
    us = np.unique(np.r_[np.linspace(a, b, 9), [u for u in breaks if a - 1e-9 <= u <= b + 1e-9]].round(9))
    ts = np.minimum(np.abs(us - end * LENGTH / 2) / IN, 188.)
    edge = side * first.BARRIER_BACK

    def xyz(u, v, z):
        y = edge - side * v
        x = first.sx(u, y)
        return x, y, first.surface(x, y) + z
    return variable_sweep(us, [section_at(t) for t in ts], xyz), us, ts


def drain_axis(side):
    """Old frame: the generator's drain position, mid-span (u = 0), 30 mm inside the face of rail."""
    y = side * (22 * FT - .03)
    return first.sx(0., y), y


def ring(cx, cy, r):
    ang = np.arange(SEGMENTS) * 2 * np.pi / SEGMENTS
    return np.column_stack([cx + r * np.cos(ang), cy + r * np.sin(ang)])


def core_cutter(side):
    cx, cy = drain_axis(side)
    z_top = first.surface(cx, cy)
    poly = [tuple(p) for p in ring(cx, cy, DRAIN_R)]
    return first.sweep(poly, [z_top - OVERLAY - REMAINING - .1, z_top + .1], lambda z, px, py: (px, py, z))


def drain_skin(side):
    """3 mm skin lining the 2 in core, from the slab soffit to the finished surface (both planar here)."""
    cx, cy = drain_axis(side)
    outer, inner = ring(cx, cy, DRAIN_R), ring(cx, cy, DRAIN_R - SKIN)
    v = []
    for (ox, oy), (ix, iy) in zip(outer, inner):
        for px, py, top in ((ix, iy, False), (ox, oy, False), (ox, oy, True), (ix, iy, True)):
            s = first.surface(px, py)
            v.append((px, py, s if top else s - OVERLAY - REMAINING))
    f = []
    for k in range(SEGMENTS):
        i, j = 4 * k, 4 * ((k + 1) % SEGMENTS)
        ib, ob, ot, it = i, i + 1, i + 2, i + 3
        jb, pb, pt, jt = j, j + 1, j + 2, j + 3
        f += [(ob, pb, pt), (ob, pt, ot), (ib, jt, jb), (ib, it, jt),
              (ot, pt, jt), (ot, jt, it), (ob, jb, pb), (ob, ib, jb)]
    m = trimesh.Trimesh(np.array(v), np.array(f), process=True)
    if m.volume < 0:
        m.invert()
    if not m.is_watertight or not m.is_winding_consistent or m.volume <= 0:
        raise ValueError('invalid drain skin')
    return m


def slab_vertices(u0, u1, y0, y1, thick, offset):
    """Vertex set of the generator's Model.slab (crown vertex at Y = 0)."""
    ys = sorted(set([y0, y1] + ([0.] if y0 < 0 < y1 else [])))
    v = []
    for u in np.linspace(u0, u1, max(2, int((u1 - u0) / .6) + 1)):
        for y in ys:
            x = first.sx(u, y)
            v += [(x, y, first.surface(x, y) + offset - thick), (x, y, first.surface(x, y) + offset)]
    return trimesh.PointCloud(np.array(v))


def covers(mesh, x, y):
    """True if any triangle of the mesh lies over the plan point (x, y), i.e. a vertical line there hits it."""
    t = mesh.triangles[:, :, :2]
    a, b, c = t[:, 0], t[:, 1], t[:, 2]
    det = (b[:, 1] - c[:, 1]) * (a[:, 0] - c[:, 0]) + (c[:, 0] - b[:, 0]) * (a[:, 1] - c[:, 1])
    ok = np.abs(det) > 1e-12
    l1 = ((b[:, 1] - c[:, 1]) * (x - c[:, 0]) + (c[:, 0] - b[:, 0]) * (y - c[:, 1]))[ok] / det[ok]
    l2 = ((c[:, 1] - a[:, 1]) * (x - c[:, 0]) + (a[:, 0] - c[:, 0]) * (y - c[:, 1]))[ok] / det[ok]
    return bool(((l1 >= 0) & (l2 >= 0) & (1 - l1 - l2 >= 0)).any())


def correct(base=BASE, backup=BACKUP):
    mp = base / 'model_manifest.json'
    raw_manifest = mp.read_bytes()
    manifest = json.loads(raw_manifest)
    if manifest.get('drawing_review_correction_2') == TAG:
        print('Already corrected.')
        return
    path = base / 'model.glb'
    original = path.read_bytes()
    before = hashlib.sha256(original).hexdigest()

    def expect(ok, what):
        if not ok:
            raise ValueError(f'{BID}: unexpected starting model ({what})')

    expect(manifest.get('drawing_review_correction') == first.TAG and manifest.get('revision') == PREVIOUS_REVISION,
           'first review correction not applied')
    expect(before == manifest['drawing_review_correction_record']['after_glb_sha256'], 'GLB differs from revision 1.1')
    length = struct.unpack_from('<I', original, 12)[0]
    gltf = json.loads(original[20:20 + length])
    binary = bytearray(original[28 + length:])
    parts = {p['id']: p for p in manifest['parts']}
    meshes = {m['name']: m for m in gltf['meshes']}
    expect(set(parts) == set(meshes) and len(meshes) == 91, 'part list')
    expect(not any(k in n for n in gltf['nodes'] for k in ('matrix', 'rotation', 'translation', 'scale')),
           'node transforms')

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

    # ---- Read every part in the old (mirrored) frame and check the starting state. ----
    old = {}
    for pid, m in meshes.items():
        prim = m['primitives'][0]
        expect(len(m['primitives']) == 1 and set(prim['attributes']) == {'POSITION', 'COLOR_0'}
               and prim.get('mode', 4) == 4, f'{pid} primitive')
        g = read(prim['attributes']['POSITION']).astype(np.float64)
        mesh = trimesh.Trimesh(np.column_stack([g[:, 0], -g[:, 2], g[:, 1]]), read(prim['indices']).reshape(-1, 3),
                               process=False)
        expect(mesh.is_watertight and mesh.volume > 0, f'{pid} not a closed solid')
        old[pid] = mesh

    def centre(pid):
        return old[pid].bounds.mean(axis=0)

    def west_end_x(mesh, y):
        v = mesh.vertices
        return v[np.abs(v[:, 1] - y) < 1e-6, 0].min()

    expect(west_end_x(old['deck'], -WIDTH / 2) < west_end_x(old['deck'], WIDTH / 2) - 8,
           'deck ends not on X = u + tan30 Y (old frame)')
    expect(abs(centre('beam_0_0')[1] + 19.375 * FT) < 1e-3 and abs(centre('beam_0_5')[1] - 19.375 * FT) < 1e-3,
           'beam lines (old frame)')
    for pid, side in (('TFC_transition_-1_-1', -1), ('TFC_transition_1_-1', -1), ('TFC_transition_1_1', 1),
                      ('wing_0_-1', -1), ('wing_1_-1', -1), ('wing_0_1', 1), ('wing_1_1', 1),
                      ('midspan_drain_-1', -1), ('midspan_drain_1', 1)):
        expect(np.sign(centre(pid)[1]) == side, f'{pid} side (old frame)')
    expect('TFC_transition_-1_1' not in parts, 'SW transition present')
    for pid, end, side in TFC_IDS:                    # revision 1.1 TFC envelopes (first script, exactly)
        a, b = sorted([end * LENGTH / 2, end * (LENGTH / 2 + first.TFC_LEN)])
        profile = first.Profile(end)
        expect(first.same_vertices(first.rail_mesh(a, b, side, first.TFC_LOW, .2286, base=.4064,
                                                   edge=side * first.BARRIER_BACK, height_at=profile,
                                                   breaks=profile.breaks, scale_toe=False), old[pid].vertices),
               f'{pid} not the revision 1.1 envelope')
    for side in (-1, 1):                              # generator drain rod
        x, y = drain_axis(side)
        z = first.surface(x, y)
        expect(first.same_vertices(rod([x, y, z - .28], [x, y + side * .35, z - .45], IN), old[f'midspan_drain_{side}'].vertices),
               f'midspan_drain_{side} not the generator rod')
    expect(first.same_vertices(slab_vertices(-LENGTH / 2, LENGTH / 2, -WIDTH / 2, WIDTH / 2, REMAINING, -OVERLAY),
                               old['deck'].vertices), 'deck')
    expect(first.same_vertices(slab_vertices(-LENGTH / 2, LENGTH / 2, -22 * FT, 22 * FT, OVERLAY, 0.),
                               old['overlay'].vertices), 'overlay')

    # ---- 2. TFC sections (sheet 12), built in the old frame. ----
    rebuilt, records = {}, {}
    for pid, end, side in TFC_IDS:
        mesh, us, ts = tfc_mesh(end, side)
        rebuilt[pid] = mesh
        records[pid] = dict(volume_before_m3=round(float(old[pid].volume), 6), volume_after_m3=round(float(mesh.volume), 6))

    # ---- 3. Drain cores (sheet 9): cut deck and overlay, skins lining the cores. ----
    cutters = [core_cutter(s) for s in (-1, 1)]
    for pid, thick in (('deck', REMAINING), ('overlay', OVERLAY)):
        cut = trimesh.boolean.difference([old[pid]] + cutters, engine='manifold')
        removed = float(old[pid].volume - cut.volume)
        area = .5 * SEGMENTS * DRAIN_R ** 2 * np.sin(2 * np.pi / SEGMENTS)
        expect(cut.is_watertight and cut.is_winding_consistent and abs(removed - 2 * area * thick) < 2e-6,
               f'{pid} core cut (removed {removed:.7f} m3, expected {2 * area * thick:.7f})')
        kept = np.abs(old[pid].vertices[:, None, :] - cut.vertices[None, :, :]).max(axis=2).min(axis=1)
        expect(kept.max() < 1e-5, f'{pid} perimeter not kept')
        rebuilt[pid] = cut
        records[pid] = dict(removed_m3=round(removed, 7))
    for side in (-1, 1):
        pid = f'midspan_drain_{side}'
        rebuilt[pid] = drain_skin(side)
        x, y = drain_axis(side)
        records[pid] = dict(axis_xy_m=[round(x, 6), round(-y, 6)], core_diameter_m=round(2 * DRAIN_R, 6),
                            top_el_ft=round(817 + first.surface(x, y) / FT, 3),
                            soffit_el_ft=round(817 + (first.surface(x, y) - OVERLAY - REMAINING) / FT, 3))

    # ---- 1. Reflect every part: (X, Y, Z) -> (X, -Y, Z), winding reversed. ----
    final = {}
    for pid, m in {**old, **rebuilt}.items():
        r = trimesh.Trimesh(m.vertices * [1, -1, 1], np.asarray(m.faces)[:, [0, 2, 1]], process=False)
        expect(r.is_watertight and r.is_winding_consistent and abs(r.volume - m.volume) < 1e-9, f'{pid} reflection')
        final[pid] = r

    # ---- Checks in the corrected frame. ----
    expect(west_end_x(final['deck'], WIDTH / 2) < west_end_x(final['deck'], -WIDTH / 2) - 8,
           'north (+Y) deck end not down-station')
    for pid, side in (('TFC_transition_-1_-1', 1), ('TFC_transition_1_-1', 1), ('TFC_transition_1_1', -1),
                      ('wing_0_-1', 1), ('wing_1_-1', 1), ('beam_0_0', 1), ('retained_rail_-1', 1)):
        expect(np.sign(final[pid].bounds.mean(axis=0)[1]) == side, f'{pid} not on the drawn side')
    measured = {}
    for pid, end, side in TFC_IDS:
        ns = -side                                     # new-frame side
        v = final[pid].vertices
        uu = v[:, 0] + K * v[:, 1]                     # new frame: X = u - tan30 Y
        rows = []
        for t in (0, 86, 97, 117.5, 137, 188):         # stations of the sweep (117.5 in: 5th of 9 equal stations)
            sel = np.abs(uu - end * (LENGTH / 2 + min(t * IN, first.TFC_LEN))) < 2e-4
            expect(sel.sum() == 6, f'{pid} station {t} in')
            s = v[sel]
            h = s[:, 2] - first.surface(s[:, 0], s[:, 1])
            off = first.BARRIER_BACK - ns * s[:, 1]
            toe = off[np.abs(h) < 1e-6].max()
            toe_top = h[(np.abs(off - toe) < 1e-6) & (h > 1e-6)].min()
            rows.append(dict(t_in=t, base_width_m=round(float(toe), 4), toe_height_m=round(float(toe_top), 4),
                             height_m=round(float(h.max()), 4)))
            want = section_at(min(t, 188))
            expect(abs(toe - want[1][0]) < 1e-4 and abs(h.max() - want[4][1]) < 1e-4 and abs(toe_top - want[2][1]) < 1e-4,
                   f'{pid} section at {t} in: {rows[-1]}')
        measured[pid] = rows
        expect(np.sign(final[pid].bounds.mean(axis=0)[1]) == ns, f'{pid} side')
    for side in (-1, 1):
        pid = f'midspan_drain_{side}'
        x, y = drain_axis(side)
        ny = -y
        for host in ('deck', 'overlay'):
            expect(not covers(final[host], x, ny), f'{host} not open at {pid}')
            expect(covers(old[host], x, y), f'{host} was already open at {pid}')
        lo, hi = final[pid].bounds
        expect(abs(hi[2] - first.surface(x, y)) < 1e-3 and abs(lo[2] - (first.surface(x, y) - OVERLAY - REMAINING)) < 1e-3,
               f'{pid} does not span soffit to surface')
    for pid, m in final.items():
        expect(m.is_watertight and m.is_winding_consistent and m.volume > 0, f'{pid} final solid')

    # ---- Write: reflected positions and reversed indices for every part, rebuilt parts in full. ----
    pos_map, idx_map = {}, {}
    for pid, m in final.items():
        prim = meshes[pid]['primitives'][0]
        a_pos, a_idx, a_col = prim['attributes']['POSITION'], prim['indices'], prim['attributes']['COLOR_0']
        if pid in rebuilt:
            v = np.asarray(m.vertices)
            prim['attributes']['POSITION'] = append(np.column_stack([v[:, 0], v[:, 2], -v[:, 1]]).astype('<f4'),
                                                    'VEC3', 5126)
            color = read(a_col)[0]
            prim['attributes']['COLOR_0'] = append(np.tile(color, (len(v), 1)).astype('u1'), 'VEC4', 5121)
            gltf['accessors'][prim['attributes']['COLOR_0']]['normalized'] = True
            prim['indices'] = append(np.asarray(m.faces).reshape(-1, 1).astype('<u4'), 'SCALAR', 5125)
        else:
            if a_pos not in pos_map:                  # float32 negation is exact
                pos_map[a_pos] = append((read(a_pos) * np.array([1, 1, -1], dtype='<f4')).astype('<f4'), 'VEC3', 5126)
            if a_idx not in idx_map:
                idx_map[a_idx] = append(read(a_idx).reshape(-1, 3)[:, [0, 2, 1]].reshape(-1, 1).astype('<u4'),
                                        'SCALAR', 5125)
            prim['attributes']['POSITION'], prim['indices'] = pos_map[a_pos], idx_map[a_idx]
        p = parts[pid]
        if pid in rebuilt:
            p['bounds_m'] = np.round(m.bounds, 6).tolist()
            p['volume_m3'] = round(float(m.volume), 9)
        else:
            (x0, y0, z0), (x1, y1, z1) = p['bounds_m']
            p['bounds_m'] = [[x0, round(-y1, 6) + 0.0, z0], [x1, round(-y0, 6) + 0.0, z1]]
            expect(np.abs(np.array(p['bounds_m']) - m.bounds).max() < 2e-5, f'{pid} manifest bounds')

    for pid, end, side in TFC_IDS:
        p = parts[pid]
        p['dimensions'].update(base_width_m=round(16 * IN, 6), far_end_width_m=round(9 * IN, 6),
                               near_end_toe_height_m=round(2.5 * IN, 6),
                               section_profile='C-C (1 ft 4 in base, 2 1/2 in toe, knee 11 in from the back at 9 1/2 in) '
                                               'to 7 ft 2 in; bulge tapered out to D-D (11 5/8 in base) at 8 ft 1 in; '
                                               'D-D to F-F (9 in, vertical faces) at 11 ft 5 in; F-F to 15 ft 8 in')
        p['note'] += (' Sections to sheet 12 (C-C, D-D, E-E, F-F; was one 1 ft 4 in section with a 7 in toe over the '
                      'whole length): C-C to 7 ft 2 in, tapering through D-D at 8 ft 1 in to the 9 in F-F wall at '
                      '11 ft 5 in; the shape between the drawn sections is interpolated linearly.')
        p['pdf_pages'] = sorted(set(p['pdf_pages']) | {12})
    for side in (-1, 1):
        p = parts[f'midspan_drain_{side}']
        p['name'] = f'Retained midspan cored drain {side}'
        p['dimensions'].update(core_length_m=round(OVERLAY + REMAINING, 6), display_skin_thickness_m=SKIN,
                               axis='vertical through the remaining slab and the overlay')
        p['note'] += (' Rebuilt to sheet 9 (proposed typical section, Overlay at Deck Drain Details, Section D-D) as the '
                      'open 2 in core straight down through the 7 1/2 in remaining slab and the 2 in overlay at '
                      'mid-span next to the face of rail, shown as a 3 mm display skin lining the core (cut from deck '
                      'and overlay); was a closed rod 16 mm below the slab, sloping 0.35 m outward. The overlay taper '
                      'to the drain edge is not modelled (known_deviations).')
        p['pdf_pages'] = sorted(set(p['pdf_pages']) | {9})
    for pid in ('deck', 'overlay'):
        parts[pid]['note'] += ' The two 2 in mid-span drain cores are cut through it (sheet 9).'
    for pid, p in parts.items():
        p['note'] = (p.get('note', '') + ' ' + ORIENT_NOTE).strip()
        extras = meshes[pid]['extras']
        if pid in rebuilt:
            extras.update(p)
        else:
            extras.update({k: p[k] for k in extras if k in p})

    for item in manifest.get('detail_coverage', []):
        if item.get('feature') == 'Whole retained box-beam crossing':
            item['detail'] += (' North is +Y, left of increasing station, and the north end of each abutment is '
                               'down-station (sheets 7, 8; reflected in revision 1.2).')
        elif item.get('feature') == '2026 exterior repair design':
            item['detail'] += (' TFC sections follow sheet 12 C-C to F-F; mid-span drains are open 2 in cores through '
                               'the slab (sheet 9; revision 1.2).')

    deviations = []
    for d in manifest.get('known_deviations', []):
        if d.get('id') == 'acute-corner-wings':
            d = dict(d, deviation=d['deviation'].replace(
                'with the top about El. 831.1-831.3 at the tip.',
                'with the top at about El. 831.15 (A) / 830.96 (D) at the tip, 1.15 / 1.12 m above the drawn tips.'))
        if d.get('id') not in ('obtuse-wing-roots', 'midspan-drain-overlay-taper'):
            deviations.append(d)
    deviations += [
        dict(id='obtuse-wing-roots', parts='wing_0_1, wing_1_-1',
             source='1985 sheets 5-7 (B-16317, existing_plans_9548292.pdf); primary sheet 8',
             deviation='Wings B (southwest) and C (northeast) start at the generator\'s abutment-cap end, 0.15 m '
                       'outside the coping line; at 60 deg to the abutment their 0.40 m wall stands 50 mm clear of the '
                       'deck edge at the root. 1985 sheet 5 (plan) starts the wing\'s inner face at the coping corner on '
                       'the abutment front face, and the wall is 1 ft thick at the top, battered to 1 ft 9 1/2 in '
                       '(End Elevation B-B).',
             reason='Placing the root needs the wing/abutment junction rebuilt with the historical cap outline, as '
                    'for the acute-corner wings; a shift to close the gap alone would not follow the drawings.'),
        dict(id='midspan-drain-overlay-taper', parts='overlay, midspan_drain_-1, midspan_drain_1',
             source='sheet 9 (Overlay at Deck Drain Details, Section D-D)',
             deviation='The overlay keeps its full surface up to the 2 in drain cores; sheet 9 tapers the surface down '
                       'to the existing drain edge over 1 ft 0 in toward the drain (a 1 ft x 2 ft area at each drain).',
             reason='The depth of the taper ("to Ex. Drain Edge") is not dimensioned.')]
    manifest['known_deviations'] = deviations

    while len(binary) % 4:
        binary.append(0)
    gltf['buffers'][0]['byteLength'] = len(binary)
    encoded = json.dumps(gltf, ensure_ascii=True, separators=(',', ':')).encode()
    encoded += b' ' * ((-len(encoded)) % 4)
    out = (struct.pack('<III', 0x46546c67, 2, 28 + len(encoded) + len(binary)) +
           struct.pack('<II', len(encoded), 0x4e4f534a) + encoded + struct.pack('<II', len(binary), 0x004e4942) + binary)
    backup.mkdir(parents=True, exist_ok=True)
    (backup / f'{BID}_before_review_correction_2.glb').write_bytes(original)
    (backup / f'{BID}_manifest_before_review_correction_2.json').write_bytes(raw_manifest)
    path.write_bytes(out)

    manifest['drawing_review_correction_2'] = TAG
    manifest['revision'] = REVISION
    manifest['drawing_review_correction_2_record'] = dict(
        source_pdf_pages=[7, 8, 9, 12], printed_sheets=[7, 8, 9, 12],
        supplementary_source=dict(document_id='9548292', local_file='sources/existing_plans_9548292.pdf',
                                  pdf_pages=[5, 7]),
        previous_revision=PREVIOUS_REVISION,
        native_axes='X along increasing station (east), Y positive to the left of increasing station (north), Z up, '
                    'Z = 0 at El. 817.00; bearing lines X = u - tan(30 deg) Y',
        frame_note='Coordinates quoted in drawing_review_correction_record (revision 1.1) and in the notes of that '
                   'revision are in the previous, mirrored frame (north at Y < 0, X = u + tan(30 deg) Y); negate Y to '
                   'compare them with this revision. manifest skew_deg keeps the generator value.',
        findings={
            'H1': 'confirmed - the whole model was the mirror image of the drawings (north at Y < 0, north abutment '
                  'ends up-station); every vertex reflected (X, Y, Z) -> (X, -Y, Z), winding reversed (sheets 7, 8, 12)',
            'N1 TFC sections': 'confirmed - sheet 12 C-C/D-D/E-E/F-F: base 1 ft 4 in with 2 1/2 in toe narrowing to '
                               'the 9 in F-F wall (was 1 ft 4 in base and 7 in toe throughout)',
            'N2 drains': 'confirmed in part - vertical 2 in open cores through slab and overlay (was a closed sloping '
                         'rod below the slab); overlay taper deferred (depth not dimensioned)',
            'F1': 'unchanged (A/D deferred); acute-corner-wings entry corrected to the measured tip El. 831.15 / 830.96',
            'F2': 'wing-root gap deferred (obtuse-wing-roots)',
            'F3': 'mudwall item unchanged (floor-end-over-mudwall)',
            'F4': 'NW/SE stations unchanged (transition-railing-stations)'},
        part_side_suffixes='Part ids keep their geographic meaning: suffix -1 = north member (now Y > 0), suffix 1 = '
                           'south member (now Y < 0); beam_0_0 and B*_bearing_1 are the north beam line.',
        values=dict(tfc_sections_in=dict(C_C=SECTION_C, D_D=[(round(a, 4), b) for a, b in SECTION_D], F_F=SECTION_F,
                                         anchors_from_bridge_end_in=[t for t, _ in ANCHORS]),
                    measured_tfc_sections=measured, parts=records),
        reflected_parts=sorted(final), rebuilt_parts=sorted(rebuilt),
        before_glb_sha256=before, after_glb_sha256=hashlib.sha256(out).hexdigest())
    text = json.dumps(manifest, indent=2)
    if b'\r\n' in raw_manifest:
        text = text.replace('\n', '\r\n')
    if raw_manifest.endswith(b'\n'):
        text += '\r\n' if b'\r\n' in raw_manifest else '\n'
    mp.write_bytes(text.encode('utf-8'))
    print(json.dumps({k: v for k, v in manifest['drawing_review_correction_2_record'].items()
                      if k not in ('findings', 'reflected_parts')}, indent=1))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--base', type=Path, default=BASE, help='bridge folder (default: the repository copy)')
    parser.add_argument('--backup', type=Path, default=BACKUP, help='backup folder')
    args = parser.parse_args()
    correct(args.base, args.backup)

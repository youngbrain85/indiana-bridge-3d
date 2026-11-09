"""Fourth correction of US 224 over Eight Mile Creek (us224-eight-mile): finding S01 of the 3D model review.
Runs after scripts/correct_us224_eight_mile_review.py, _review_2.py and _review_3.py (revision 1.3-deviations) and
keeps every GLB buffer it does not replace.

    python scripts/correct_us224_eight_mile_3d_review.py [--base DIR] [--backup DIR]

Primary set: INDOT B-44532 / Des 2200957 (drawings.pdf, document 9683628); printed sheet number = PDF page number.
Supplementary: 1985 plans B-16317 (sources/existing_plans_9548292.pdf), cited as "1985 sheet N" (its PDF page N).
Native axes (revision 1.2 frame): X along increasing station (east), Y positive to the LEFT of increasing station
(north), Z up, Z = 0 at El. 817.00. Bearing lines X = u - tan(30 deg) Y; u = station offset along Line "A".
Distances "normal" are measured square to the skewed abutment: normal = along-u x cos 30 deg.

S01 (RESOLVE). Both approach slabs started 25 mm (along u; 21.7 mm normal) behind the mudwall back face with nothing
under their roots: the existing pavement ledge was missing.
  - Sheet 11 (mudwall plan: "Ex. 6 in Pav't Ledge" along the whole mudwall behind it; Section C-C) and sheet 15
    (Typical Section Through Approach) show the 2026 RCBA bearing on the existing 6 in ledge behind the mudwall, its
    end thickened ("Varies") down to the ledge top over the 6 in ledge and 1 ft 6 in beyond it, then returning at
    45 deg (drawn on both sheets) to its 1 ft 0 in soffit; the reconstructed mudwall portion stops at the same level.
  - 1985 sheet 5 Section A-A dimensions the ledge: 6 in wide, 1 ft 0 in deep, on the rear face of the 1 ft mudwall
    (whose rear face is flush with the 2 ft 6 in cap's), top "Varies" below the mudwall top. The 1985 elevations give
    its top: "Pvmt. Ledge El. 830.51" (Abut. 1, 1985 sheet 5) and "Pvmt. Ledge El. 830.49" (Abut. 2, 1985 sheet 6), one
    elevation per abutment, drawn as a straight line: the ledge is level.
  - Sheets 8 (scope: "new RCBA on Lean Concrete Base") and 15: a 9 in lean concrete base under the RCBA (BOM: as many
    square yards as the slab), from the back face of the ledge to the slab's far end; its bottom is parallel to the
    slab, 9 in below the 1 ft 0 in soffit, so it is thinner under the thickened end.
  Now: pavement_ledge_1 / _2 (6 in normal x 1 ft 0 in, top El. 830.51 / 830.49, from the obtuse-corner mudwall end to
  the acute wing's root leg at 22 ft 1 in, which occupies the corner); approach_-1 / approach_1 thickened to the ledge
  top from the root to 2 ft 0 in (normal) behind the mudwall back face and returning at 45 deg (end depth 13.6 to
  18.8 in, the slab top is crowned and the ledge level); approach_base_-1 / _1, 9 in lean concrete base.
  Decisions: the written 1985 ledge elevations govern over the undimensioned "Varies" of sheets 11 and 15; the 1985
  rectangular ledge section governs over the 45 deg underside the 2026 reference linework sketches below it (sheet 8
  general note 2: existing details are based on the existing plans and are for reference only).
  Kept: the generator's 25 mm open joint at the slab root (sheet 15 Type I-A joint and preformed fillers; Standard
  E 609-RCBA, not in the set) - known_deviations "rcba-root-joint". The 1 ft NE RCBA extension end passes 53 mm over
  the back corner of pavement_ledge_2 (E 609-TBAE, not in the set) - added to "ne-corner-wingwall-root".

Requires numpy, trimesh and manifold3d, plus the three earlier correction scripts (helpers).
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
import correct_us224_eight_mile_review_3 as third  # noqa: E402

BID = first.BID
BASE = ROOT / 'data/bridges' / BID
BACKUP = ROOT / 'data/fem_research'
TAG = '3d-review-pavement-ledges-rcba-ends-lean-base'
PREVIOUS_REVISION = third.REVISION                 # '1.3-deviations'
REVISION = '1.4-3d-review'
EXPECTED_BEFORE_SHA = 'fca5059995d5bca8d5e66dda9ece8f761e4b1679960443246361daf038ddc9e6'
EXPECTED_DEVIATIONS = {'midspan-drain-overlay-taper', 'bearing-pad-plan', 'ne-corner-wingwall-root'}

FT, IN, K = first.FT, first.IN, first.K
COS = np.cos(np.radians(30))
L2 = third.L2                                      # floor end = mudwall back face, u = +-6.86435 (sheet 8)
W2 = third.W2                                      # 23 ft 4 in, mudwall ends (rev. 1.3)
ROOT_FRONT = third.ROOT_FRONT                      # 22 ft 1 in, acute wing root leg inner face (rev. 1.3)
ROOT_GAP = .025                                    # generator Type I-A joint gap along u (kept, known_deviations)
LEDGE_W, LEDGE_D = 6 * IN, 1 * FT                  # 1985 sheet 5 Section A-A; sheet 11 "Ex. 6 in Pav't Ledge"
LEDGE_EL = {1: 830.51, 2: 830.49}                  # 1985 sheet 5 / sheet 6 elevations, "Pvmt. Ledge El."
FLAT = (6 + 18) * IN                               # sheets 11 C-C and 15: 6 in ledge + 1 ft 6 in, normal
SLAB_T = 1 * FT                                    # 12 in RCBA (sheet 15)
BASE_T = 9 * IN                                    # 9 in lean concrete base (sheet 15)
SLABS = {  # pid: (end, abutment, Y south edge, Y north edge at the root, base id, ledge id)  sheets 13-14
    'approach_-1': (-1, 1, -(22 + 4 / 12) * FT, 22 * FT, 'approach_base_-1', 'pavement_ledge_1'),
    'approach_1': (1, 2, -22 * FT, 22 * FT, 'approach_base_1', 'pavement_ledge_2')}
X_FAR = 20.5 * FT + float(third.sx(L2 + ROOT_GAP, -22 * FT))   # square far end, 20 ft 6 in on the 22 ft edge
LEDGE_Y = {1: (-W2, ROOT_FRONT), 2: (-ROOT_FRONT, W2)}   # obtuse mudwall end to the acute wing root leg
BASE_COLOR = '#a9b1ad'


def surface(x, y):
    return float(first.surface(x, y))


def sx(u, y):
    return float(third.sx(u, y))


def z_el(el):
    return (el - 817) * FT


def u_at(end, n):
    """u of the line n (normal) behind the mudwall back face of the abutment at `end`."""
    return end * (L2 + n / COS)


def soffit(end, n, y):
    u = u_at(end, n)
    return surface(sx(u, y), y) - SLAB_T


def taper_n(end, ab, y):
    """Normal distance where the 45 deg return from the ledge level meets the 1 ft soffit (soffit linear in n)."""
    z = z_el(LEDGE_EL[ab])
    s0, s1 = soffit(end, FLAT, y), soffit(end, FLAT + 1., y)
    return FLAT + (s0 - z) / (1. - (s1 - s0))


def loft(sections, what):
    """Closed solid through sections at constant Y (same vertex count); end caps are exact vertical polygons."""
    secs = [np.asarray(s, float) for s in sections]
    n, count = len(secs[0]), len(secs)
    faces = []
    for k in range(count - 1):
        for j in range(n):
            a, b = k * n + j, k * n + (j + 1) % n
            faces += [(a, b, b + n), (a, b + n, a + n)]
    faces += [tuple(q[::-1]) for q in first.triangulate([(p[0], p[2]) for p in secs[0]])]
    faces += [tuple(q + (count - 1) * n) for q in first.triangulate([(p[0], p[2]) for p in secs[-1]])]
    return third.solid(trimesh.Trimesh(np.concatenate(secs), np.array(faces), process=True), what)


def rcba(end, ab, y):
    """Section (constant Y) of the slab rebuilt with its thickened end: top on the finished surface from the root
    (25 mm joint, kept) to the square far end, 1 ft soffit back to the 45 deg return, ledge level to the root."""
    z = z_el(LEDGE_EL[ab])
    n_root, n_t = ROOT_GAP * COS, taper_n(end, ab, y)
    xr, xf = sx(u_at(end, n_root), y), end * X_FAR
    return [(xr, y, surface(xr, y)), (xf, y, surface(xf, y)), (xf, y, surface(xf, y) - SLAB_T),
            (sx(u_at(end, n_t), y), y, soffit(end, n_t, y)), (sx(u_at(end, FLAT), y), y, z), (xr, y, z)]


def strip(x0, x1, y0, y1):
    """Square-ended 1 ft slab strip, top on the finished surface (the 4 in north step of approach_1, sheet 13)."""
    return loft([[(x0, y, surface(x0, y)), (x1, y, surface(x1, y)), (x1, y, surface(x1, y) - SLAB_T),
                  (x0, y, surface(x0, y) - SLAB_T)] for y in (y0, y1)], 'approach_1 step strip')


def lean_base(end, ab, y):
    """Section (constant Y) of the 9 in lean concrete base: from the back face of the ledge, top on the slab soffit
    (ledge level, 45 deg return, 1 ft soffit) to the square far end, bottom 9 in below the 1 ft soffit."""
    z = z_el(LEDGE_EL[ab])
    n_t = taper_n(end, ab, y)
    pts = [(sx(u_at(end, n), y), y, h) for n, h in ((LEDGE_W, z), (FLAT, z), (n_t, soffit(end, n_t, y)))]
    xf = end * X_FAR
    pts += [(xf, y, surface(xf, y) - SLAB_T), (xf, y, surface(xf, y) - SLAB_T - BASE_T)]
    u6 = u_at(end, LEDGE_W)
    pts.append((sx(u6, y), y, surface(sx(u6, y), y) - SLAB_T - BASE_T))
    return pts


def ledge(end, ab):
    z = z_el(LEDGE_EL[ab])
    secs = []
    for y in LEDGE_Y[ab]:
        x0, x1 = sx(u_at(end, 0.), y), sx(u_at(end, LEDGE_W), y)
        secs.append([(x0, y, z - LEDGE_D), (x1, y, z - LEDGE_D), (x1, y, z), (x0, y, z)])
    return loft(secs, f'pavement_ledge_{ab}')


def correct(base=BASE, backup=BACKUP):
    mp = base / 'model_manifest.json'
    raw_manifest = mp.read_bytes()
    manifest = json.loads(raw_manifest)
    if manifest.get('review_correction_3d') == TAG:
        print('Already corrected.')
        return
    path = base / 'model.glb'
    original = path.read_bytes()
    before = hashlib.sha256(original).hexdigest()

    def expect(ok, what):
        if not ok:
            raise ValueError(f'{BID}: unexpected state ({what})')

    expect(manifest.get('review_correction_3') == third.TAG and manifest.get('revision') == PREVIOUS_REVISION,
           'revision 1.3 not applied')
    expect(before == EXPECTED_BEFORE_SHA == manifest['review_correction_record_3']['after_glb_sha256'],
           'GLB differs from revision 1.3')
    expect({d['id'] for d in manifest.get('known_deviations', [])} == EXPECTED_DEVIATIONS, 'known_deviations')
    length = struct.unpack_from('<I', original, 12)[0]
    gltf = json.loads(original[20:20 + length])
    binary = bytearray(original[28 + length:])
    parts = {p['id']: p for p in manifest['parts']}
    meshes = {m['name']: m for m in gltf['meshes']}
    expect(set(parts) == set(meshes) and len(meshes) == 94, 'part list')
    new_ids = {'pavement_ledge_1', 'pavement_ledge_2', 'approach_base_-1', 'approach_base_1'}
    expect(not new_ids & set(parts), 'new part ids already present')
    world = gltf['nodes'][0]
    expect(world.get('name') == 'world' and len(world['children']) == 94 and
           not any(k in nd for nd in gltf['nodes'] for k in ('matrix', 'rotation', 'translation', 'scale')),
           'scene nodes')

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

    old = {}
    for pid, m in meshes.items():
        prim = m['primitives'][0]
        g = read(prim['attributes']['POSITION']).astype(np.float64)
        old[pid] = trimesh.Trimesh(np.column_stack([g[:, 0], -g[:, 2], g[:, 1]]), read(prim['indices']).reshape(-1, 3),
                                   process=False)

    # ---- Starting state: slab roots 25 mm behind the mudwall back face, 1 ft thick, no seat; mudwall/cap faces. ----
    tol = 2e-4
    for pid, (end, ab, y_s, y_n, _, _) in SLABS.items():
        v = old[pid].vertices
        uu = v[:, 0] + K * v[:, 1]
        depth = np.array([surface(p[0], p[1]) - p[2] for p in v])
        expect(abs(np.abs(uu).min() - (L2 + ROOT_GAP)) < tol, f'{pid} root at the generator joint gap')
        expect(np.all((np.abs(depth) < tol) | (np.abs(depth - SLAB_T) < tol)), f'{pid} 1 ft thick, top on the surface')
        far = v[:, 0].max() if end > 0 else -v[:, 0].min()
        expect(abs(v[:, 1].min() - y_s) < tol and abs(far - X_FAR) < tol, f'{pid} south edge / far end')
        root = v[np.abs(np.abs(uu) - (L2 + ROOT_GAP)) < tol]
        expect(abs(root[:, 1].max() - y_n) < tol, f'{pid} north edge at the root')
        mw = old[f'mudwall_{ab}'].vertices
        mu = mw[:, 0] + K * mw[:, 1]
        expect(abs(np.abs(mu).max() - L2) < tol and abs(mw[:, 1].max() - W2) < tol, f'mudwall_{ab} back face')
        cv = old[f'cap_{ab}'].vertices
        expect(abs(np.abs(cv[:, 0] + K * cv[:, 1]).max() - L2) < tol, f'cap_{ab} rear face')
        expect(old[f'mudwall_{ab}'].bounds[0][2] < z_el(LEDGE_EL[ab]) - LEDGE_D, f'mudwall_{ab} reaches below the ledge')
    v = old['approach_1'].vertices
    wide = v[np.abs(v[:, 1] - (22 * FT + 4 * IN)) < tol][:, 0]
    ne_step_x = float(wide.min())                  # rev. 1.3: north edge 22 ft 0 in up to the extension far end
    expect(abs(ne_step_x - float(old['extension_1_-1'].bounds[1][0])) < tol, 'approach_1 NE step at the extension end')

    new, added, info = {}, {}, {}
    # ---- Pavement ledges (1985 sheet 5 Section A-A; sheet 11 plan; elevations 1985 sheets 5-6). ----
    for end, ab in ((-1, 1), (1, 2)):
        lid = f'pavement_ledge_{ab}'
        added[lid] = ledge(end, ab)
        info[lid] = dict(top_el_ft=LEDGE_EL[ab], top_z_m=round(z_el(LEDGE_EL[ab]), 6),
                         u_m=sorted([round(u_at(end, 0.), 6), round(u_at(end, LEDGE_W), 6)]),
                         y_m=[round(y, 6) for y in LEDGE_Y[ab]])

    # ---- RCBA ends thickened onto the ledge; 9 in lean concrete base (sheets 11 C-C, 15). ----
    for pid, (end, ab, y_s, y_n, bid, lid) in SLABS.items():
        ys = (y_s, 0., y_n)
        slab = loft([rcba(end, ab, y) for y in ys], pid)
        if pid == 'approach_1':                    # rev. 1.3 / sheet 13: 22 ft 4 in edge beyond the NE extension end
            slab = third.solid(third.boolean('union', [slab, strip(ne_step_x, X_FAR, y_n, 22 * FT + 4 * IN)]), pid)
        # The rebuild contains the revision 1.3 slab exactly (same top, edges, ends and 1 ft soffit) and only adds the
        # thickened end below it.
        dist = np.abs(trimesh.proximity.signed_distance(slab, old[pid].vertices))
        expect(dist.max() < 2e-5, f'{pid} rebuild passes through the old slab vertices ({dist.max():.2e} m)')
        outside = third.boolean('difference', [old[pid], slab])
        expect(not len(outside.faces) or abs(outside.volume) < 2e-5, f'{pid} old slab inside the rebuild')
        gained = slab.volume - old[pid].volume
        expect(0 < gained < 2. and np.isclose(slab.bounds[0][2], z_el(LEDGE_EL[ab]), atol=1e-6) and
               np.allclose(slab.bounds[1], old[pid].bounds[1], atol=2e-5) and
               np.allclose(slab.bounds[0][:2], old[pid].bounds[0][:2], atol=2e-5), f'{pid} rebuild extent')
        new[pid] = slab
        y_top = 22 * FT + 4 * IN if pid == 'approach_1' else y_n
        b = loft([lean_base(end, ab, y) for y in (y_s, 0., y_top)], bid)
        if pid == 'approach_1':                    # rev. 1.3 / sheet 13: 22 ft 0 in edge up to the NE extension end
            box = trimesh.creation.box([ne_step_x + 1., 1., 12.])
            box.apply_translation([(ne_step_x - 1.) / 2, 22 * FT + .5, 4.])
            b = third.solid(third.boolean('difference', [b, box]), bid)
        added[bid] = b
        depths = [surface(sx(u_at(end, ROOT_GAP * COS), y), y) - z_el(LEDGE_EL[ab]) for y in ys]
        info[pid] = dict(thickening_volume_m3=round(gained, 6), ledge_top_z_m=round(z_el(LEDGE_EL[ab]), 6),
                         end_depth_m={f'y={y:+.4f}': round(d, 6) for y, d in zip(ys, depths)},
                         return_end_normal_m={f'y={y:+.4f}': round(taper_n(end, ab, y), 6) for y in ys})
        info[bid] = dict(start_u_m=round(u_at(end, LEDGE_W), 6), far_end_x_m=round(end * X_FAR, 6),
                         y_m=[round(y_s, 6), round(y_top, 6)], volume_m3=round(float(b.volume), 6))

    # ---- Checks: closed solids, no overlaps with any other part, bearing on the ledges. ----
    final = {**old, **new, **added}
    for pid, m in {**new, **added}.items():
        expect(m.is_watertight and m.is_winding_consistent and m.volume > 0, f'{pid} final solid')
    clashes, contact_noise = [], {}
    face_contacts = {tuple(sorted([p, SLABS[p][4]])) for p in SLABS}   # ~125 m2 slab soffit on its base
    for pid in sorted({**new, **added}):
        for other, m in final.items():
            if other == pid or (other in new or other in added) and other < pid:
                continue
            v = third.overlap(final[pid], m)
            pair = tuple(sorted([pid, other]))
            if v > 1e-7:
                contact_noise['|'.join(pair)] = round(v, 8)
            if v > (2e-5 if pair in face_contacts else 5e-6):   # float32 noise of coplanar contact (rev. 1.3 rule)
                clashes.append((pid, other, v))
    expect(not clashes, f'overlaps {clashes}')

    def ray_bottom(mesh, x, y):
        hits, _, _ = mesh.ray.intersects_location([[x, y, 20.]], [[0., 0., -1.]])
        return float(hits[:, 2].min()) if len(hits) else None

    def ray_top(mesh, x, y):
        hits, _, _ = mesh.ray.intersects_location([[x, y, -5.]], [[0., 0., 1.]])
        return float(hits[:, 2].max()) if len(hits) else None

    contacts = {}
    for pid, (end, ab, y_s, y_n, bid, lid) in SLABS.items():
        rows = []
        for y in (y_s + .05, 0., y_n - .05):
            for n in (.03, .09, .15):              # over the 6 in ledge, behind the 21.7 mm (normal) root gap
                u = u_at(end, n)
                x = sx(u, y)
                s, t = ray_bottom(final[pid], x, y), ray_top(final[lid], x, y)
                expect(s is not None and t is not None and abs(s - t) < 1e-5, f'{pid} on {lid} at ({x:.3f}, {y:.3f})')
                rows.append(round(s - t, 7))
            for n in (.3, .6, 1.5, 4.):            # base top on the slab soffit
                x = sx(u_at(end, n), y)
                s, t = ray_bottom(final[pid], x, y), ray_top(final[bid], x, y)
                expect(s is not None and t is not None and abs(s - t) < 1e-5, f'{pid} on {bid} at ({x:.3f}, {y:.3f})')
        contacts[pid] = dict(max_gap_slab_ledge_m=max(rows),
                             bearing_strip_normal_m=round(LEDGE_W - ROOT_GAP * COS, 6),
                             bearing_strip_length_m=round((y_n - y_s) / COS, 6),
                             bearing_area_m2=round((LEDGE_W - ROOT_GAP * COS) * (y_n - y_s) / COS, 4))

    # ---- Write meshes. ----
    def hex_rgba(h):
        h = h.lstrip('#')
        return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)] + [255], 'u1')

    def put(m, prim, color):
        v = np.asarray(m.vertices)
        prim['attributes'] = {
            'POSITION': append(np.column_stack([v[:, 0], v[:, 2], -v[:, 1]]).astype('<f4'), 'VEC3', 5126),
            'COLOR_0': append(np.tile(color, (len(v), 1)).astype('u1'), 'VEC4', 5121)}
        gltf['accessors'][prim['attributes']['COLOR_0']]['normalized'] = True
        prim['indices'] = append(np.asarray(m.faces).reshape(-1, 1).astype('<u4'), 'SCALAR', 5125)
        prim['mode'] = 4

    for pid in sorted(new):
        prim = meshes[pid]['primitives'][0]
        put(new[pid], prim, read(prim['attributes']['COLOR_0'])[0])
        parts[pid]['bounds_m'] = np.round(new[pid].bounds, 6).tolist()
        parts[pid]['volume_m3'] = round(float(new[pid].volume), 9)

    supp = lambda pages, detail: [dict(document_id='9548292', local_file='sources/existing_plans_9548292.pdf',  # noqa
                                       pdf_pages=pages, detail=detail)]
    for end, ab in ((-1, 1), (1, 2)):
        lid = f'pavement_ledge_{ab}'
        m = added[lid]
        acute = 'north (Wing A)' if ab == 1 else 'south (Wing D)'
        obtuse = 'south' if ab == 1 else 'north'
        part = dict(
            id=lid, name=f'Abutment {ab} existing pavement ledge', layer='abutments', color=parts['mudwall_1']['color'],
            pdf_pages=[11, 15], basis='Dimensioned section and elevation (1985 plans); existing, retained',
            note=(f'Existing 6 in pavement ledge on the back face of the Abutment {ab} mudwall, on which the 2026 RCBA '
                  'bears (sheet 11 mudwall plan "Ex. 6 in Pav\'t Ledge" and Section C-C; sheet 15 Typical Section '
                  'Through Approach). 1985 sheet 5 Section A-A: 6 in wide (normal to the abutment) and 1 ft 0 in deep '
                  'behind the 1 ft mudwall, whose rear face is flush with the cap; top level at '
                  f'"Pvmt. Ledge El. {LEDGE_EL[ab]}" (1985 sheet {5 if ab == 1 else 6} elevation). It runs from the '
                  f'{obtuse} end of the mudwall (23 ft 4 in) to the inner face of the acute-corner {acute} root leg '
                  '(22 ft 1 in), which occupies the corner. The 2026 sheets sketch a 45 deg underside below it '
                  '(undimensioned reference linework); the 1985 construction section, a rectangle, is used. The '
                  'reinforcement and the 1/2 in x 2 in preformed filler on its top (sheet 15) are not modelled.'),
            dimensions=dict(width_normal_m=round(LEDGE_W, 6), depth_m=round(LEDGE_D, 6), top_el_ft=LEDGE_EL[ab],
                            top_z_m=round(z_el(LEDGE_EL[ab]), 6), front_face='mudwall back face (floor end), u = '
                            f'{u_at(end, 0.):+.6f}', y_extent_m=[round(y, 6) for y in LEDGE_Y[ab]]),
            bounds_m=np.round(m.bounds, 6).tolist(), volume_m3=round(float(m.volume), 9), approximation=True,
            supplementary_sources=supp([5, 6], '1985 sheet 5 Section A-A (6 in x 1 ft 0 in ledge) and the "Pvmt. Ledge '
                                       'El." of the sheet 5 (Abut. 1, 830.51) and sheet 6 (Abut. 2, 830.49) elevations.'))
        manifest['parts'].append(part)
        parts[lid] = part
    for pid, (end, ab, y_s, y_n, bid, lid) in SLABS.items():
        m = added[bid]
        side = 'West' if end < 0 else 'East'
        part = dict(
            id=bid, name=f'{side} approach lean concrete base', layer='approaches', color=BASE_COLOR,
            pdf_pages=[8, 13, 14, 15], basis='Dimensioned thickness (sheet 15); plan of the RCBA',
            note=(f'9 in lean concrete base under the {side.lower()} RCBA (sheet 8 scope: "new RCBA on Lean Concrete '
                  'Base on Geotextiles for Pavement, Type 2B"; sheet 15 Typical Section Through Approach and bill of '
                  'materials: Lean Concrete Base, 9 In., the same area as the 12 in RCBA). From the back face '
                  'of the existing pavement ledge to the square far end of the slab, under the slab plan of sheets '
                  f'13-14 ({"22 ft 0 in north / 22 ft 4 in south" if end < 0 else "22 ft 4 in north, 22 ft 0 in under the NE extension, / 22 ft 0 in south"} '
                  'of Line "A"). Top on the slab soffit, including the thickened end over the ledge and its 45 deg '
                  'return; bottom parallel to the slab, 9 in below its 1 ft 0 in soffit, so it is thinner under the '
                  'thickened end as sheet 15 draws it. Geotextile and polyethylene layers are not modelled; not under '
                  'the RCBA extensions.'),
            dimensions=dict(thickness_below_normal_soffit_m=round(BASE_T, 6),
                            start='back face of the pavement ledge, ' + f'u = {u_at(end, LEDGE_W):+.6f}',
                            far_end_x_m=round(end * X_FAR, 6), crossfall=.015625, grade=-.002),
            bounds_m=np.round(m.bounds, 6).tolist(), volume_m3=round(float(m.volume), 9))
        manifest['parts'].append(part)
        parts[bid] = part
    for pid in ['pavement_ledge_1', 'pavement_ledge_2', 'approach_base_-1', 'approach_base_1']:
        prim = {}
        put(added[pid], prim, hex_rgba(parts[pid]['color']))
        gltf['meshes'].append(dict(name=pid, extras=dict(processed=True, **parts[pid]), primitives=[prim]))
        gltf['nodes'].append(dict(name=pid, mesh=len(gltf['meshes']) - 1))
        world['children'].append(len(gltf['nodes']) - 1)

    # ---- Manifest notes and dimensions. ----
    def note(pid, text, pages=()):
        p = parts[pid]
        p['note'] = (p.get('note', '') + ' ' + text).strip()
        p['pdf_pages'] = sorted(set(p['pdf_pages']) | set(pages))

    for pid, (end, ab, y_s, y_n, bid, lid) in SLABS.items():
        d = info[pid]['end_depth_m']
        parts[pid]['dimensions'].update(
            end_bearing=f'{lid}, top El. {LEDGE_EL[ab]} (level)',
            end_flat_normal_m=round(FLAT, 6), end_return='45 deg to the 1 ft 0 in soffit',
            end_depth_range_m=[round(min(d.values()), 6), round(max(d.values()), 6)])
        parts[pid].setdefault('supplementary_sources', supp([5, 6], 'Pvmt. Ledge El. 830.51 (Abut. 1, 1985 sheet 5) / '
                                                             '830.49 (Abut. 2, 1985 sheet 6): the RCBA end bearing level.'))
        note(pid, f'Rev. 1.4: the end bears on the existing 6 in pavement ledge ({lid}; sheet 11 Section C-C, sheet 15): '
                  f'thickened down to the ledge top, El. {LEDGE_EL[ab]} (1985 sheet {5 if ab == 1 else 6}), from the '
                  'root to 2 ft 0 in (6 in ledge + 1 ft 6 in, normal) behind the mudwall back face, then returning at '
                  '45 deg to the 1 ft 0 in soffit; the ledge is level and the top crowned, so the end is '
                  f'{min(d.values()) / IN:.1f} to {max(d.values()) / IN:.1f} in deep ("Varies" on sheets 11 and 15). '
                  f'It sits on the 9 in lean concrete base {bid}. Was 1 ft 0 in throughout with nothing under the root. '
                  'The 25 mm open joint at the root is kept (known_deviations rcba-root-joint).', [11, 15])
    for ab in (1, 2):
        note(f'mudwall_{ab}', f'Rev. 1.4: the existing 6 in pavement ledge on its back face is a separate part, '
                              f'pavement_ledge_{ab} (1985 sheet 5 Section A-A); this mesh is unchanged.', [])
        parts[f'mudwall_{ab}']['note'] = parts[f'mudwall_{ab}']['note'].replace(
            'Lower retained portion, ledge and local top return simplify', 'Lower retained portion and local top return '
            'simplify')

    for p in parts.values():
        if p['id'] in new or p['id'] in added or p['id'] in ('mudwall_1', 'mudwall_2'):
            mesh = next(m for m in gltf['meshes'] if m['name'] == p['id'])
            mesh['extras'] = dict(processed=True, **p)

    for item in manifest.get('detail_coverage', []):
        if item.get('feature') == '2026 exterior repair design':
            item['part_ids'] = item['part_ids'] + ['approach_base_-1', 'approach_base_1']
            item['detail'] += (' Rev. 1.4: the RCBA ends bear on the existing 6 in pavement ledges, thickened to the '
                               'ledge top with a 45 deg return, on 9 in lean concrete bases (sheets 11, 15).')
        elif item.get('feature') == 'Historical support and framing topology':
            item['part_ids'] = item['part_ids'] + ['pavement_ledge_1', 'pavement_ledge_2']
            item['detail'] += (' Rev. 1.4: existing 6 in x 1 ft 0 in pavement ledges behind both mudwalls, tops El. '
                               '830.51 / 830.49 (1985 sheets 5-6).')
            if 'Primary PDF p.15' not in item['sources']:
                item['sources'].append('Primary PDF p.15')

    ne = next(d for d in manifest['known_deviations'] if d['id'] == 'ne-corner-wingwall-root')
    ne['parts'] += ', pavement_ledge_2'
    ne['deviation'] += (' Rev. 1.4: the square end of the RCBA extension also passes 53 mm over the back corner of '
                        'pavement_ledge_2 (a 0.03 m2 triangle in plan); the main slab beside it is thickened onto the '
                        'ledge (sheet 15), the 1 ft extension is not.')
    ne['reason'] += (' Whether the extension end is thickened onto the ledge like the RCBA is on Standard Drawing '
                     'E 609-TBAE (sheet 15 note 4), which is not in the set either.')
    manifest['known_deviations'].append(dict(
        id='rcba-root-joint', parts='approach_-1, approach_1, mudwall_1, mudwall_2, pavement_ledge_1, pavement_ledge_2',
        source='sheet 15 Typical Section Through Approach (Type I-A joint, preformed fillers; note 3: Standard E '
               '609-RCBA); sheet 11 Section C-C',
        deviation='Each slab root keeps the generator\'s 25 mm open joint along Line "A" (21.7 mm normal) to the '
                  'mudwall back face and bears on the ledge from there; sheet 15 draws the RCBA end against the '
                  'mudwall with a 1/2 in x 4 in preformed expansion joint filler at its foot, the Type I-A joint at '
                  'the top and a 1/2 in x 2 in preformed filler on the back edge of the ledge, none of them modelled.',
        reason='Sheet 15 is a typical section (1/2 in = 1 ft) that gives the filler sizes but not the joint opening or '
               'where each filler sits; those are on Standard Drawing E 609-RCBA (sheet 15 note 3), which is not in '
               'the set. E 609-RCBA would settle the joint; the slab lengths and the RCBA extensions measured from '
               'the root are unaffected either way.'))

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

    manifest['review_correction_3d'] = TAG
    manifest['revision'] = REVISION
    manifest['review_correction_record_3d'] = dict(
        review='3D model review, finding S01 (physical plausibility of the assembled model)',
        source_pdf_pages=[8, 11, 13, 14, 15], printed_sheets=[8, 11, 13, 14, 15],
        supplementary_source=dict(document_id='9548292', local_file='sources/existing_plans_9548292.pdf',
                                  pdf_pages=[5, 6]),
        previous_revision=PREVIOUS_REVISION,
        findings={'S01': 'RESOLVE - pavement ledges added; RCBA ends thickened onto them (sheets 11 C-C, 15); 9 in lean '
                         'concrete bases added (sheet 15)'},
        decisions=[
            dict(id='ledge-elevation', reading='written 1985 "Pvmt. Ledge El." 830.51 (Abut. 1, 1985 sheet 5) and 830.49 '
                 '(Abut. 2, 1985 sheet 6), one level per abutment',
                 rejected='depth scaled from the 2026 sections: sheet 11 Section C-C draws 1 ft 4 1/2 in at the cut '
                          '(about 1 in less than El. 830.51 gives there), sheet 15 about 1 ft 2 in (typical)',
                 reasoning='The 2026 sheets mark the depth "Varies" and give no value (C-C draws its 1 ft 6 in as 1 ft 5 in) '
                           'and their existing details are based on the existing plans (sheet 8 general note 2); the '
                           '1985 elevations are the only written values for the existing ledge the 2026 RCBA bears on.'),
            dict(id='ledge-section', reading='1985 sheet 5 Section A-A: 6 in x 1 ft 0 in rectangle',
                 rejected='45 deg underside sketched below the ledge in the existing (grey) linework of sheets 11 C-C and 15',
                 reasoning='Section A-A is the construction drawing of the ledge and dimensions it; the 2026 linework '
                           'is undimensioned and, by sheet 8 general note 2, based on the existing plans and for '
                           'reference only.')],
        kept_deviations=['rcba-root-joint'],
        values=dict(ledge_width_normal_m=round(LEDGE_W, 6), ledge_depth_m=round(LEDGE_D, 6),
                    rcba_flat_end_normal_m=round(FLAT, 6), lean_base_m=round(BASE_T, 6), root_gap_u_m=ROOT_GAP,
                    root_gap_normal_m=round(ROOT_GAP * COS, 6), parts=info, contacts=contacts,
                    contact_overlaps_m3=contact_noise),
        changed_parts=sorted(new), added_parts=sorted(added), removed_parts=[],
        notes_updated=['mudwall_1', 'mudwall_2', 'known_deviations: ne-corner-wingwall-root'],
        source_ledger_change=None,
        frame='revision 1.2 frame: X east, Y north (left of increasing station), Z up, Z = 0 at El. 817.00',
        before_glb_sha256=before, after_glb_sha256=hashlib.sha256(out).hexdigest())
    text = json.dumps(manifest, indent=2)
    if b'\r\n' in raw_manifest:
        text = text.replace('\n', '\r\n')
    if raw_manifest.endswith(b'\n'):
        text += '\r\n' if b'\r\n' in raw_manifest else '\n'
    mp.write_bytes(text.encode('utf-8'))
    print(json.dumps({k: manifest['review_correction_record_3d'][k] for k in
                      ('changed_parts', 'added_parts', 'before_glb_sha256', 'after_glb_sha256')}, indent=1))
    print(json.dumps(contacts, indent=1))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--base', type=Path, default=BASE, help='bridge folder (default: the repository copy)')
    parser.add_argument('--backup', type=Path, default=BACKUP, help='backup folder')
    args = parser.parse_args()
    correct(args.base, args.backup)

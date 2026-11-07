"""Second round of drawing-confirmed corrections for Virginia Avenue over I-65 NB / I-70 EB, preserving unrelated GLB
buffers.

    python scripts/correct_virginia_avenue_review_2.py

Runs after scripts/correct_virginia_avenue_review.py (manifest review_correction
'transverse-mirror-crown-rails-approaches-end-frames', revision 1.1-review-corrections). It rebuilds that corrected
geometry with the first script's build(True), requires every GLB part to match it, and then replaces five meshes. Part
ids are unchanged; no part is added or removed.

Primary set: INDOT B-44576 (document 9683637, drawings.pdf); printed sheet numbers equal PDF page numbers. Historical
set: existing plans 9548460 (2013 Girder 1 replacement; printed sheet 14 = PDF 32). Native axes: X increasing station
(X = 0 at 13+48.31 "Vir"), Y positive to the left looking up-station (south side, Girder 1 at Y = +9.2964), Z up.

N1 / F5, sheets 31 and 37 (crown on Line "Vir") and sheets 36 / 37 (fillet reinforcing detail: the fillet is cast with
the deck): after the crown moved to Y = 0 it sits over Girder 5, but haunch_5's top was still one straight line between
its flange edges (Y = +/-0.254), 5.08 mm below the crowned soffit at the crown. The top now has a vertex at Y = 0 and
follows the soffit (Z = grade(X) - 0.02 |Y| - 8 in); the flat bottom on the girder is unchanged.

N2, sheet 38 (Elevations Abutment No. 1 / No. 2 and Typical Sections: "1 in PEJF (Adhered to top of mudwall)" across
the whole width under the deck): the mudwall tops were straight lines between the two deck edges, so they cut 65.7 mm
into the deck at the south curb and 47.5 mm at the north curb and left 55.4 mm at the crown. They now follow the deck
soffit with breaks at the north curb (Y = -7.620), the crown (Y = 0) and the south curb (Y = +4.572), 1 in below it for
the joint filler (the filler itself is not modelled). Footprints and bottoms (seat datum) are unchanged.

F2, existing sheet 14 (PDF 32, End Cross-Frame Details, northbound structure: "Cope Flange Adjacent to Connection
(Typ.)", W16x45 end "1 in Min. (Typ.)" clear): on the 44 deg 19 min 06 sec skewed bearing line the square-cut W16x45
flange corners passed through the Girder 1 and Girder 2 webs (33.8-38.7 cm3 per connection). The W16x45 ends are now
coped parallel to the girder webs, 1 in clear of the web faces. The bearing stiffeners and connection plates the
1 in is measured from on sheet 14 are not modelled, so it is applied to the nearest modelled steel, the 5/8 in web.
The L5x5x3/8 diagonals and bottom strut are unchanged.

Not changed (minor, outside this round): the roadway drain at Abutment 2 is at Sta. 13+88.30 instead of 13+87.50
(sheet 36); recorded in known_deviations.

Requires numpy, trimesh, shapely and manifold3d.
"""
import hashlib
import json
import struct
import sys
from pathlib import Path

import manifold3d as mf
import numpy as np
import trimesh as tm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import correct_virginia_avenue_review as first  # noqa: E402  (also installs its triangulation / graph fallbacks)
from bridge_geometry import IN, sweep, concat, iform  # noqa: E402

BID = first.BID
BASE = ROOT / 'data/bridges' / BID
TAG = 'haunch-crown-mudwall-pejf-end-frame-copes'
REVISION = '1.2-review-corrections-2'
CHANGED = ['haunch_5', 'mudwall_1', 'mudwall_2', 'end_cross_frame_B1_1', 'end_cross_frame_B2_1']

SLAB, SPAN, WIDTH = first.SLAB, first.SPAN, first.WIDTH
CLEAR = .05                      # model rule: girder top 50 mm below the deck soffit (haunch depth)
SOUTH_CURB, NORTH_CURB = 15 * 12 * IN, -25 * 12 * IN    # sheets 31, 37: curbs 15 ft left / 25 ft right of Line "Vir"
PEJF = 1 * IN                    # sheet 38: 1 in preformed expansion joint filler on top of the mudwall
COPE_CLEAR = 1 * IN              # existing sheet 14: W16x45 end 1 in min. clear of the connection
WEB = .625 * IN                  # model girder web (existing sheets 10, 14: 54 x 5/8 in web)
G1_Y, G2_Y = float(-first.GIRDER_Y_OLD[0]), float(-first.GIRDER_Y_OLD[1])   # +9.2964, +7.2390 after review 1.1


def build_new(m):
    """Corrected meshes for the five affected parts, from the review-1.1 model m (first.build(True))."""
    surface, sx = m.surface, m.sx
    out = {}

    # N1: haunch_5 with a top vertex on the crown. The cap is triangulated on the true section shape (top vertices at
    # their depth), so the crowned top cannot fold; fn then puts top vertices on the soffit and bottom ones on the girder.
    half = 10 * IN                                       # Girder 5: 20 in flanges (first script, girders 2-9)
    depth = lambda v: CLEAR - .02 * abs(v)               # noqa: E731  roadway crossfall 2 % either side of the crown
    prof = [(-half, 0.0), (half, 0.0), (half, depth(half)), (0.0, depth(0.0)), (-half, depth(-half))]

    def haunch(u, v, w):
        x = sx(u, v)
        return (x, v, surface(x, v) - SLAB if w > 0 else surface(x, 0.0) - SLAB - CLEAR)
    out['haunch_5'] = sweep(prof, [-SPAN / 2, SPAN / 2], haunch)

    # N2: mudwall tops 1 in below the soffit, with the soffit's breaks at the north curb, crown and south curb.
    for bi, u in enumerate([-SPAN / 2, SPAN / 2]):
        end = -1 if bi == 0 else 1
        a, b = u + end * .65 - .15, u + end * .65 + .15
        seat = min(c['seat_m'] for c in m.contacts if c['id'].startswith(f'B{bi + 1}_'))
        top = lambda x, y: surface(x, y) - SLAB - PEJF   # noqa: E731
        ys = [-WIDTH / 2, NORTH_CURB, 0.0, SOUTH_CURB, WIDTH / 2]
        mid = (a + b) / 2
        prof = [(ys[0], 0.0), (ys[-1], 0.0)] + [(y, float(top(sx(mid, y), y) - seat)) for y in reversed(ys)]

        def wall(uu, y, w, seat=seat, top=top):
            x = sx(uu, y)
            return (x, y, top(x, y) if w > 0 else seat)
        out[f'mudwall_{bi + 1}'] = sweep(prof, [a, b], wall)

    # F2: the review-1.1 end cross-frame pieces, then the W16x45 coped parallel to the girder webs.
    k = first.W16X45
    g1_depth = (54 + 2 * 1.25) * IN                      # Girder 1 end zone: 54 in web, 16 x 1 1/4 in flanges (existing sheet 10)
    keep = (G2_Y + WEB / 2 + COPE_CLEAR, G1_Y - WEB / 2 - COPE_CLEAR)
    for bi, u in enumerate([-SPAN / 2, SPAN / 2]):
        ya, yb = G1_Y - .02, G2_Y + .02                  # first script: frame ends 0.02 m off the girder centres
        pa = np.array([sx(u, ya), ya, 0.0])
        pb = np.array([sx(u, yb), yb, 0.0])
        top_a = surface(sx(u, G1_Y), G1_Y) - SLAB - CLEAR
        top_b = surface(sx(u, G2_Y), G2_Y) - SLAB - CLEAR
        line = pb - pa
        normal = np.array([-line[1], line[0], 0.0]) / np.linalg.norm(line[:2])

        def strut(s, v, z, pa=pa, line=line, normal=normal, top_a=top_a, top_b=top_b):
            p = pa + s * line
            zt = top_a + s * (top_b - top_a) - 3 * IN
            return (p[0] + v * normal[0], p[1] + v * normal[1], zt - k['d'] + z)
        w16 = sweep(iform(k['d'], k['bf'], k['tw'], k['tf']), [0.0, 1.0], strut)
        chord = g1_depth - 6 * IN - first.ANGLE_LEG / 2
        lo_a = np.array([pa[0], pa[1], top_a - chord])
        lo_b = np.array([pb[0], pb[1], top_b - chord])
        rest = [first.oriented_bar(lo_a, lo_b, [0, 0, 1], first.ANGLE_LEG, first.ANGLE_T)]
        mid = (lo_a + lo_b) / 2
        for e, t in ((pa, top_a), (pb, top_b)):
            start = np.array([e[0], e[1], t - 3 * IN - k['d']])
            start[:2] += (mid[:2] - start[:2]) * (6 * IN / np.linalg.norm(mid[:2] - start[:2]))
            rest.append(first.oriented_bar(start, mid, normal, first.ANGLE_LEG, first.ANGLE_T))
        out[f'_review_1_1_end_cross_frame_B{bi + 1}_1'] = concat([w16] + rest)        # starting-state check only
        out[f'end_cross_frame_B{bi + 1}_1'] = concat([cope(w16, *keep)] + rest)
    return out


def cope(mesh, y_min, y_max):
    """Keep the part of a closed mesh with y_min <= Y <= y_max (two vertical planes parallel to the girder webs)."""
    mm = mesh.copy()
    mm.merge_vertices()
    solid = mf.Manifold(mf.Mesh64(vert_properties=np.asarray(mm.vertices, np.float64),
                                  tri_verts=np.asarray(mm.faces, np.uint32)))
    solid = solid.trim_by_plane((0.0, 1.0, 0.0), y_min).trim_by_plane((0.0, -1.0, 0.0), -y_max)
    r = solid.to_mesh64()
    out = tm.Trimesh(np.asarray(r.vert_properties)[:, :3], np.asarray(r.tri_verts), process=True)
    out.fix_normals(multibody=True)
    if not out.is_watertight or out.volume <= 0:
        raise ValueError('cope produced an invalid solid')
    return out


def z_hits(mesh, x, y):
    """Z values where the vertical line through (x, y) crosses the mesh."""
    t = mesh.triangles
    a = t[:, 0]
    v0, v1, v2 = t[:, 1, :2] - a[:, :2], t[:, 2, :2] - a[:, :2], np.array([x, y]) - a[:, :2]
    den = v0[:, 0] * v1[:, 1] - v1[:, 0] * v0[:, 1]
    ok = np.abs(den) > 1e-14
    den = np.where(ok, den, 1.0)
    l1 = (v2[:, 0] * v1[:, 1] - v1[:, 0] * v2[:, 1]) / den
    l2 = (v0[:, 0] * v2[:, 1] - v2[:, 0] * v0[:, 1]) / den
    hit = ok & (l1 >= -1e-9) & (l2 >= -1e-9) & (1 - l1 - l2 >= -1e-9)
    return np.sort(((1 - l1 - l2) * a[:, 2] + l1 * t[:, 1, 2] + l2 * t[:, 2, 2])[hit])


def overlap_cm3(a, b):
    """Intersection volume of two closed meshes in cm3, body by body."""
    def bodies(m):
        mm = m.copy()
        mm.merge_vertices()
        return mf.Manifold(mf.Mesh64(vert_properties=np.asarray(mm.vertices, np.float64),
                                     tri_verts=np.asarray(mm.faces, np.uint32))).decompose()
    return sum((p ^ q).volume() for p in bodies(a) for q in bodies(b)) * 1e6


def interfaces(mesh_of):
    """The three reviewed interfaces, measured on actual triangles (metres / cm3)."""
    deck = mesh_of('deck')
    res = {}
    h = mesh_of('haunch_5')
    gaps = [z_hits(deck, x, y).min() - z_hits(h, x, y).max() for x in (-15.0, 0.0, 15.0) for y in (-.2, -.1, 0.0, .1, .2)]
    res['haunch_5_soffit_gap_m'] = dict(at_crown_X0=round(float(z_hits(deck, 0, 0).min() - z_hits(h, 0, 0).max()), 6),
                                        max=round(float(max(gaps)), 6), min=round(float(min(gaps)), 6))
    for bi in (1, 2):
        w = mesh_of(f'mudwall_{bi}')
        u = (-1 if bi == 1 else 1) * (SPAN / 2 + .65)
        clear = {}
        for label, y in (('north_edge', -9.8), ('north_curb', NORTH_CURB), ('crown', 0.0), ('south_curb', SOUTH_CURB),
                         ('south_edge', 9.8)):
            x = u - np.tan(np.radians(first.SKEW)) * y
            clear[label] = round(float(z_hits(deck, x, y).min() - z_hits(w, x, y).max()), 6)
        res[f'mudwall_{bi}_soffit_clearance_m'] = clear
    for bi in (1, 2):
        f = mesh_of(f'end_cross_frame_B{bi}_1')
        res[f'end_cross_frame_B{bi}_1_overlap_cm3'] = {g: round(overlap_cm3(f, mesh_of(g)), 3) for g in ('beam_1', 'beam_2')}
    return res


def to_gltf(v):
    return np.column_stack([v[:, 0], v[:, 2], -v[:, 1]])


NOTES = {
    'haunch_5': ' Review correction 1.2: top split at the crown (Line "Vir", Y = 0) so the fillet follows the crowned deck '
                'soffit; the 5.08 mm air gap at the crown is closed (sheets 31, 37 crown; sheets 36, 37 fillet detail).',
    'mudwall': ' Review correction 1.2: top follows the deck soffit with breaks at the north curb, crown and south curb, '
               '1 in below it for the 1 in PEJF adhered to the top of the mudwall (sheet 38); previously a straight line '
               'between the deck edges that cut up to 65.7 mm into the deck at the curbs and left 55.4 mm at the crown.',
    'end_cross_frame': ' Review correction 1.2: W16x45 ends coped parallel to the girder webs, 1 in clear of the Girder 1 '
                       'and Girder 2 web faces (existing sheet 14: "Cope flange adjacent to connection", "1 in Min. '
                       '(Typ.)"); the square-cut flange corners no longer pass through the webs. The 1 in is applied to '
                       'the web face because bearing stiffeners and connection plates are not modelled.',
}


def correct():
    mp = BASE / 'model_manifest.json'
    manifest = json.loads(mp.read_text(encoding='utf-8'))
    if manifest.get('review_correction_2') == TAG:
        print('Already corrected.')
        return
    if manifest.get('review_correction') != first.TAG or manifest.get('revision') != first.REVISION:
        raise ValueError('Run scripts/correct_virginia_avenue_review.py first (expected revision 1.1-review-corrections).')
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

    def glb_mesh(pid):
        prim = meshes[pid]['primitives'][0]
        v = read(prim['attributes']['POSITION']).astype(np.float64)
        return tm.Trimesh(np.column_stack([v[:, 0], -v[:, 2], v[:, 1]]), read(prim['indices']).reshape(-1, 3), process=False)

    # Starting state: every part must be the review-1.1 reconstruction.
    current, m = first.build(True)
    new = build_new(m)
    if set(current) != set(meshes) or set(current) != set(parts):
        raise ValueError('Unexpected part set; the model is not the expected revision.')
    for pid, (mesh, _) in current.items():
        if not first_same(glb_mesh(pid).vertices, mesh.vertices):
            raise ValueError(f'{pid}: GLB geometry differs from the review-1.1 reconstruction')
        if abs(parts[pid]['volume_m3'] - mesh.volume) > 1e-6 * max(1.0, abs(mesh.volume)):
            raise ValueError(f'{pid}: unexpected manifest volume')
    for bi in (1, 2):   # this script's own rebuild of the old end frames must reproduce them
        if not first_same(new.pop(f'_review_1_1_end_cross_frame_B{bi}_1').vertices, current[f'end_cross_frame_B{bi}_1'][0].vertices):
            raise ValueError('end-frame reconstruction does not reproduce review 1.1')
    measured_before = interfaces(glb_mesh)
    expected = [(measured_before['haunch_5_soffit_gap_m']['at_crown_X0'], .00508),
                (measured_before['mudwall_1_soffit_clearance_m']['south_curb'], -.065743),
                (measured_before['mudwall_1_soffit_clearance_m']['north_curb'], -.047502),
                (measured_before['mudwall_2_soffit_clearance_m']['crown'], .055397)]
    if any(abs(v - e) > 2e-4 for v, e in expected) or min(min(d.values()) for k, d in measured_before.items()
                                                          if k.endswith('overlap_cm3')) < 30:
        raise ValueError(f'unexpected starting interfaces: {measured_before}')

    cache = {}

    def append(array, kind, component):
        data = array.tobytes()
        key = (kind, component, len(array), hashlib.sha256(data).hexdigest())
        if key in cache:
            return cache[key]
        while len(binary) % 4:
            binary.append(0)
        view = len(gltf['bufferViews'])
        gltf['bufferViews'].append(dict(buffer=0, byteOffset=len(binary), byteLength=len(data)))
        binary.extend(data)
        a = dict(bufferView=view, componentType=component, count=len(array), type=kind)
        if kind == 'VEC3':
            a.update(min=array.min(axis=0).tolist(), max=array.max(axis=0).tolist())
        gltf['accessors'].append(a)
        cache[key] = len(gltf['accessors']) - 1
        return cache[key]

    for ai, a in enumerate(gltf['accessors']):      # reuse identical colour / index arrays
        if a['type'] in ('SCALAR', 'VEC4'):
            arr = read(ai)
            cache.setdefault((a['type'], a['componentType'], len(arr), hashlib.sha256(arr.tobytes()).hexdigest()), ai)

    meta_keys = ('id', 'name', 'layer', 'color', 'pdf_pages', 'basis', 'note', 'dimensions')
    old_meta = {pid: dict(bounds_m=parts[pid]['bounds_m'], volume_m3=parts[pid]['volume_m3']) for pid in CHANGED}
    for pid in CHANGED:
        mesh = new[pid]
        mesh.remove_unreferenced_vertices()
        mesh.fix_normals(multibody=True)
        if not mesh.is_watertight or mesh.volume <= 0:
            raise ValueError(f'{pid}: invalid corrected solid')
        p = parts[pid]
        rgb = [int(p['color'][n:n + 2], 16) for n in (1, 3, 5)] + [255]
        prim = dict(attributes=dict(POSITION=append(to_gltf(mesh.vertices).astype('<f4'), 'VEC3', 5126),
                                    COLOR_0=append(np.tile(np.array(rgb, 'u1'), (len(mesh.vertices), 1)), 'VEC4', 5121)),
                    indices=append(mesh.faces.reshape(-1, 1).astype('<u4'), 'SCALAR', 5125), mode=4)
        gltf['accessors'][prim['attributes']['COLOR_0']]['normalized'] = True
        if meshes[pid]['primitives'][0].get('material') is not None:
            prim['material'] = meshes[pid]['primitives'][0]['material']
        meshes[pid]['primitives'] = [prim]
        kind = pid.rsplit('_', 1)[0] if pid.startswith('mudwall') else ('end_cross_frame' if pid.startswith('end') else pid)
        p['note'] = p['note'] + NOTES[kind]
        dims = dict(p.get('dimensions') or {})
        if pid == 'haunch_5':
            dims.update(crown_vertex_y_m=0.0, depth_at_crown_m=CLEAR, depth_at_flange_edges_m=round(depth_edge(), 6))
        elif pid.startswith('mudwall'):
            dims.update(top_below_deck_soffit_m=round(PEJF, 4), top_breaks_y_m=[round(NORTH_CURB, 4), 0.0, round(SOUTH_CURB, 4)])
        else:
            dims.update(w16_end_clearance_to_girder_web_m=round(COPE_CLEAR, 4), w16_end_cut='parallel to girder webs (coped)')
        p['dimensions'] = dims
        p['bounds_m'] = np.round(mesh.bounds, 6).tolist()
        p['volume_m3'] = round(float(mesh.volume), 9)
        meshes[pid].setdefault('extras', {}).update({k: p[k] for k in meta_keys})

    gltf['buffers'][0]['byteLength'] = len(binary)
    while len(binary) % 4:
        binary.append(0)
    encoded = json.dumps(gltf, ensure_ascii=True, separators=(',', ':')).encode()
    encoded += b' ' * ((-len(encoded)) % 4)
    out = (struct.pack('<III', 0x46546c67, 2, 28 + len(encoded) + len(binary)) +
           struct.pack('<II', len(encoded), 0x4e4f534a) + encoded + struct.pack('<II', len(binary), 0x004e4942) + binary)

    def out_mesh(pid):
        return new[pid] if pid in new else glb_mesh(pid)
    measured_after = interfaces(out_mesh)
    after_ok = (abs(measured_after['haunch_5_soffit_gap_m']['max']) < 1e-6 and
                abs(measured_after['haunch_5_soffit_gap_m']['min']) < 1e-6 and
                all(abs(v - PEJF) < 1e-6 for k, d in measured_after.items() if k.startswith('mudwall') for v in d.values()) and
                all(v < 1e-6 for k, d in measured_after.items() if k.endswith('overlap_cm3') for v in d.values()))
    if not after_ok:
        raise ValueError(f'corrected interfaces not as intended: {measured_after}')

    backup = ROOT / 'data/fem_research'
    backup.mkdir(exist_ok=True)
    (backup / 'virginia_avenue_before_review_correction_2.glb').write_bytes(original)
    (backup / 'virginia_avenue_manifest_before_review_correction_2.json').write_bytes(mp.read_bytes())
    path.write_bytes(out)

    manifest['review_correction_2'] = TAG
    manifest['revision'] = REVISION
    manifest['review_correction_record_2'] = dict(
        source='Independent second check of revision 1.1 (F2 and F5 partial, new issues N1-N3), each item re-read '
               'against the drawings',
        source_pdf_pages=[31, 36, 37, 38], printed_sheets=[31, 36, 37, 38],
        historical_source=dict(source_id='9548460', pdf_pages=[32], printed_sheets=[14]),
        findings={
            'N1 (F5 partial)': 'haunch_5 top split at the crown Y = 0; soffit gap at X = Y = 0 0.00508 m -> 0. '
                               'Sheets 31, 36, 37.',
            'N2': 'mudwall_1/2 tops follow the deck soffit with breaks at Y = -7.620, 0, +4.572, 1 in (0.0254 m) below it '
                  'for the PEJF; soffit clearance south curb -0.0657 -> +0.0254 m, north curb -0.0475 -> +0.0254 m, crown '
                  '+0.0554 -> +0.0254 m. Sheet 38.',
            'F2 (partial)': 'W16x45 ends of both end cross-frames coped parallel to the girder webs, 1 in clear of the '
                            'Girder 1 / Girder 2 web faces; web overlaps 33.8-38.7 cm3 per connection -> 0. Existing sheet 14.',
            'N3 (minor, deferred)': 'Abutment 2 drain at Sta. 13+88.30 vs 13+87.50 (sheet 36) left unchanged; see '
                                    'known_deviations.'},
        changed_parts=CHANGED, added_parts=[], removed_parts=[],
        before=dict(old_meta, interfaces=measured_before),
        after=dict({pid: dict(bounds_m=parts[pid]['bounds_m'], volume_m3=parts[pid]['volume_m3']) for pid in CHANGED},
                   interfaces=measured_after),
        before_glb_sha256=before, after_glb_sha256=hashlib.sha256(out).hexdigest())
    deviations = [d for d in manifest.get('known_deviations', []) if d.get('id') != 'drain-station-abutment-2']
    deviations.append(dict(
        id='drain-station-abutment-2', parts='drain_abutment_2', source='sheet 36 (plan: Roadway Drain Type SQ-A, +87.50)',
        deviation='The SQ-A inlet centre is at X = +12.190 m (Sta. 13+88.30) instead of Sta. 13+87.50 (X = +11.945 m), '
                  '0.245 m up-station; the downpipe and collector follow the inlet.',
        reason='Minor item from the second check, outside the second correction round; to be moved with the drainage '
               'routing in a later revision.'))
    manifest['known_deviations'] = deviations
    mp.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(changed=CHANGED, before=before, after=manifest['review_correction_record_2']['after_glb_sha256'],
                          interfaces_before=measured_before, interfaces_after=measured_after), indent=1))


def depth_edge():
    return CLEAR - .02 * 10 * IN


def first_same(a, b):
    """Same vertex set within float32 GLB precision (order-independent fallback, as in the first script)."""
    if a.shape != b.shape:
        return False
    if np.abs(a - b).max() <= 1e-5:
        return True
    ka, kb = np.round(a, 4), np.round(b, 4)
    return np.abs(ka[np.lexsort(ka.T[::-1])] - kb[np.lexsort(kb.T[::-1])]).max() <= 2e-4


if __name__ == '__main__':
    correct()

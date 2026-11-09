"""Fourth correction, from the 3D placement review (runs after correct_sr1_six_mile_review_3.py): the approach slabs
bear on their end walls through two added, explicitly hypothetical approach seats. Preserves unrelated GLB buffers.

    python scripts/correct_sr1_six_mile_3d_review.py

Finding S01 (approach slabs do not bear on the end-wall shelf), RESOLVED inside the hypothetical scaffold.

- Measured on revision 1.3: the approach_0 / approach_1 undersides are flat at Z = 5.587963 m (the assumed 0.30 m
  slab under the deck-edge top, 6.0 - 0.0156 x 7.18185 - 0.30). The end walls support_0 / support_3 (assumed
  0.80 m thick, centred 0.15 m inside the deck ends) project 0.275671 m along the station (0.259046 m normal to the
  skew) beyond the deck end, under the approach slab, but their whole top follows the deck soffit,
  Z = 5.55 - 0.0156 |Y|. That left 37.963 mm (crown) to 150.000 mm (deck edges) of air under each approach slab:
  no part supported it.
- Drawing evidence (contract B-44532, drawings.pdf; printed sheet numbers equal PDF page numbers): this is a thin
  deck overlay contract. Sheet 3 (general notes) says only that the approach slabs exist and are patched and
  overlaid. Sheet 4 is the location table (72'-7 1/4" x 47'-1 1/2", 3 spans). Sheet 7 shows the RCBA plan outline,
  the Type 1-A joints (Joint in PCCP, Filled) at the bridge ends and a deck-only typical section. Sheet 8 lists
  quantities. No sheet shows an end bent, an approach seat or paving notch, or an approach slab section. The end
  walls, the 0.45 m deck and the 0.30 m approach slab are all assumptions of build_sr1_six_mile.py, and the manifest
  already declares them hypothetical.
- Fix: two new parts, seat_0 and seat_1 ("End N | hypothetical approach seat", abutments layer). Each fills the end
  wall's projection beyond the deck end (station u from the wall back face to the deck end, the full 47'-1 1/2"
  width) from the wall top (the deck soffit level) up to the flat approach underside. No new dimension is
  introduced: the seat level is the existing approach underside and the seat plan is the existing wall projection.
  The seat sits on the wall top, carries the approach slab and its 38-150 mm riser lies in the deck end face plane,
  so it touches all three without overlapping them. The end walls themselves are unchanged, so the FEM wall
  inputs read from their bounds (top_z_m = 5.55) stay as they are.

Wing / end-wall overlap (found while verifying S01; fixed at the lead's request), RESOLVED.

- Measured on revision 1.3: each hypothetical wing (build_sr1_six_mile.py: 2 m along the station from the support
  line, |Y| = 6.88185 .. 7.33185 m, Z = 1.25 .. 5.40 m) starts at the support line, so its first 0.425671 m (half
  the skewed 0.80 m wall) lies inside the end wall over |Y| = 6.88185 .. 7.18185 m and its full height (the wall top
  there is 5.438-5.443 m). Overlap 0.425671 x 0.300 x 4.15 = 0.529960 m3 per wing, 2.12 m3 counted twice.
- No sheet shows the wings or how they meet the end walls (sheet 7 is a plan of the overlay areas only). The wing
  is therefore trimmed at the end-wall faces: the 0.425671 m x 0.300 m corner inside the wall is cut out, so the
  wing stops at the wall's back face and runs on past the wall's end face (|Y| = 7.18185 m) to the support line,
  as before. Each removed volume stays in the wall only. Nothing else about the wing changes.

No other mesh geometry changes. Two meshes and scene nodes are added (new POSITION and index accessors appended;
the abutment colour accessor of the walls is shared). The four wings get new POSITION and index accessors (8 -> 12
vertices) and share the same colour accessor. support_0 / support_3 and approach_0 / approach_1 get a note only.
All existing accessors and the original binary chunk are kept byte for byte.

Requires numpy, trimesh and manifold3d (boolean overlap checks).
"""
import hashlib
import json
import struct
from pathlib import Path

import numpy as np
import trimesh

FT = .3048

ROOT = Path(__file__).resolve().parents[1]
BID = 'sr1-six-mile'
BASE = ROOT / 'data/bridges' / BID
TAG_KEY = 'review_correction_3d'
TAG = 'approach-seats-on-end-walls'
RECORD_KEY = 'review_correction_record_3d'
REVISION = '1.4-3d-review'
PREVIOUS_TAG = 'known-deviations-joint-seals-44ft-roadway'   # correct_sr1_six_mile_review_3.py
PREVIOUS_REVISION = '1.3-deviations'
EXPECTED_GLB_SHA256 = '1c4e8e0a463e20ce0fc038383d94a221630e897325a70649de4031985b0806d6'

# Values of build_sr1_six_mile.py (unchanged by the three drawing-review rounds).
LENGTH = (72 + 7.25 / 12) * FT            # sheet 4, out to out
WIDTH = (47 + 1.5 / 12) * FT              # sheets 4 and 7, out to out of copings
SKEW, CROSSFALL, GRADE = 20, .0156, 6.0   # NBI skew magnitude, sheet 7 crossfall, assumed local elevation
DECK_T = .45                              # assumed slab thickness
EDGE = .15                                # assumed end overhang: support line 0.15 m inside the deck end
WALL_T = .80                              # assumed end-wall thickness, normal to the skew
WALL_BASE = 1.25                          # assumed wall base
APPROACH_T = .30                          # assumed approach slab thickness at the deck edges
WING_IN, WING_OUT = .3, .15               # assumed wing faces: 0.30 m inside / 0.15 m outside the deck edge
WING_LEN, WING_TOP = 2.0, 5.4             # assumed wing length from the support line and top elevation
ENDS = (('seat_0', 'support_0', 'approach_0', -1), ('seat_1', 'support_3', 'approach_1', 1))
WINGS = (('wing_0_-1', 'support_0', -1, -1), ('wing_0_1', 'support_0', -1, 1),
         ('wing_1_-1', 'support_3', 1, -1), ('wing_1_1', 'support_3', 1, 1))
TOL = 2e-5


def to_native(v):
    """glTF Y-up vertices (as stored, no node matrix) -> native X station, Y transverse, Z up."""
    return np.column_stack([v[:, 0], -v[:, 2], v[:, 1]])


def to_gltf(v):
    return np.column_stack([v[:, 0], v[:, 2], -v[:, 1]])


def correct():
    mp = BASE / 'model_manifest.json'
    raw_manifest = mp.read_bytes()
    manifest = json.loads(raw_manifest)
    if manifest.get(TAG_KEY) == TAG:
        print('Already corrected.')
        return
    if manifest.get('review_correction_3') != PREVIOUS_TAG or manifest.get('revision') != PREVIOUS_REVISION:
        raise ValueError('Run scripts/correct_sr1_six_mile_review_3.py first (expected revision '
                         f'{PREVIOUS_REVISION}, found {manifest.get("revision")}).')
    path = BASE / 'model.glb'
    original = path.read_bytes()
    before = hashlib.sha256(original).hexdigest()
    if before != EXPECTED_GLB_SHA256:
        raise ValueError(f'Unexpected model.glb SHA-256 {before}; expected the revision 1.3 output '
                         f'{EXPECTED_GLB_SHA256}.')
    length = struct.unpack_from('<I', original, 12)[0]
    gltf = json.loads(original[20:20 + length])
    binary = bytearray(original[28 + length:])
    parts = {p['id']: p for p in manifest['parts']}
    meshes = {m['name']: m for m in gltf['meshes']}
    if any('matrix' in n or 'rotation' in n or 'translation' in n or 'scale' in n for n in gltf['nodes']):
        raise ValueError('Unexpected node transform; this model stores glTF-axis vertices without node matrices.')
    if gltf['nodes'][0].get('name') != 'world' or len(gltf['nodes'][0]['children']) != len(manifest['parts']):
        raise ValueError('Unexpected scene layout')

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
        else:
            a.update(min=[int(array.min())], max=[int(array.max())])
        gltf['accessors'].append(a)
        return len(gltf['accessors']) - 1

    k = -np.tan(np.radians(SKEW))           # X = u + k*Y, as in bridge_geometry.Model.sx
    cos = np.cos(np.radians(SKEW))
    half_u = WALL_T / 2 / cos
    seat = GRADE - CROSSFALL * WIDTH / 2 - APPROACH_T

    def soffit(y):
        return GRADE - CROSSFALL * np.abs(y) - DECK_T

    def native(pid):
        prim = meshes[pid]['primitives'][0]
        return (to_native(read(prim['attributes']['POSITION']).astype(np.float64)),
                read(prim['indices']).reshape(-1, 3))

    added, annotated, values = [], [], {}
    for sid, wid, aid, e in ENDS:
        if sid in parts or sid in meshes:
            raise ValueError(f'{sid}: id already used')
        # --- check the starting geometry: the end wall as built, the approach slab with its flat underside ---
        wv, wf = native(wid)
        wall = trimesh.Trimesh(vertices=wv, faces=wf, process=False)
        centre = e * (LENGTH / 2 - EDGE)
        x, y, z = wv.T
        u = x - k * y
        if (len(wv) != 12 or not wall.is_watertight or wall.volume <= 0
                or not np.all(np.abs(np.abs(u - centre) - half_u) < TOL)
                or not np.all(np.min(np.abs(y[:, None] - [-WIDTH / 2, 0, WIDTH / 2]), axis=1) < TOL)
                or not np.all((np.abs(z - WALL_BASE) < TOL) | (np.abs(z - soffit(y)) < TOL))):
            raise ValueError(f'{wid}: unexpected original end-wall geometry')
        av, _ = native(aid)
        au = av[:, 0] - k * av[:, 1]
        under = av[:, 2] < seat + .05
        if (abs(av[:, 2].min() - seat) > TOL or not np.all(np.abs(av[under, 2] - seat) < TOL)
                or abs(np.abs(au).min() - LENGTH / 2) > TOL or under.sum() != 4):
            raise ValueError(f'{aid}: unexpected approach slab underside')
        dv, _ = native('deck')
        du = dv[:, 0] - k * dv[:, 1]
        if abs(np.abs(du).max() - LENGTH / 2) > TOL or abs(dv[:, 2].min() - soffit(WIDTH / 2)) > TOL:
            raise ValueError('deck: unexpected end station or soffit')
        old_gap = (seat - soffit(np.array([0, WIDTH / 2]))) * 1000

        # --- the seat (float64): wall projection beyond the deck end, wall top up to the approach underside ---
        back, deck_end = centre + e * half_u, e * LENGTH / 2
        stations = np.array([-WIDTH / 2, 0.0, WIDTH / 2])
        verts = []
        for yy in stations:
            for uu, zz in ((back, soffit(yy)), (deck_end, soffit(yy)), (deck_end, seat), (back, seat)):
                verts.append((uu + k * yy, yy, zz))
        verts = np.array(verts)
        n = 4
        tri = []
        for i in range(len(stations) - 1):
            for j in range(n):
                a, b = i * n + j, i * n + (j + 1) % n
                tri += [(a, b, b + n), (a, b + n, a + n)]
        tri += [(2, 1, 0), (3, 2, 0)]
        tri += [(8, 9, 10), (8, 10, 11)]
        mesh = trimesh.Trimesh(vertices=verts, faces=np.array(tri), process=False)
        mesh.fix_normals()
        seat_u = abs(back - deck_end)
        exact = seat_u * ((seat - GRADE + DECK_T) * WIDTH + CROSSFALL * (WIDTH / 2) ** 2)
        if (not mesh.is_watertight or not mesh.is_winding_consistent or mesh.volume <= 0
                or abs(mesh.volume - exact) > 1e-9):
            raise ValueError(f'{sid}: invalid seat ({mesh.volume} vs {exact})')

        glv = to_gltf(mesh.vertices).astype('<f4')
        # Float32 contact checks, as stored: the seat top equals the approach underside and the seat bottom
        # corners at the wall back face equal the wall's top corners there.
        if not np.all(glv[np.abs(mesh.vertices[:, 2] - seat) < TOL, 1] == np.float32(av[under, 2][0])):
            raise ValueError(f'{sid}: seat top does not equal the approach underside in float32')
        wall_gl = to_gltf(wv).astype('<f4')
        for v in glv[(np.abs(mesh.vertices[:, 0] - k * mesh.vertices[:, 1] - back) < TOL)
                     & (mesh.vertices[:, 2] < seat - TOL)]:
            if not (wall_gl == v).all(axis=1).any():
                raise ValueError(f'{sid}: seat bottom corner is not a wall top corner')

        wall_prim = meshes[wid]['primitives'][0]
        colour = read(wall_prim['attributes']['COLOR_0'])
        if len(colour) != len(glv) or not (colour == colour[0]).all():
            raise ValueError(f'{wid}: unexpected colour accessor')
        prim = dict(attributes=dict(POSITION=append(glv, 'VEC3', 5126), COLOR_0=wall_prim['attributes']['COLOR_0']),
                    indices=append(mesh.faces.astype('<u4').reshape(-1), 'SCALAR', 5125), mode=4)
        wp = parts[wid]
        rise = [round(seat - soffit(0.0), 6), round(seat - soffit(WIDTH / 2), 6)]
        end_no = 1 if e < 0 else 2
        p = dict(
            id=sid, name=f'End {end_no} | hypothetical approach seat', layer=wp['layer'], color=wp['color'],
            pdf_pages=[3, 7],
            basis='Hypothetical approach seat, not drawn',
            note=(f'Seat on the back of {wid} that carries {aid}. It fills the part of the assumed 0.80 m end wall '
                  f'that projects beyond the deck end ({seat_u * cos:.3f} m normal to the skew, across the full '
                  f'47 ft 1 1/2 in width), from the wall top at the deck soffit level (Z = 5.55 - 0.0156 |Y|) up to '
                  f'the flat approach-slab underside (Z = {seat:.6f} m): {old_gap[0]:.0f} mm high at the crown, '
                  f'{old_gap[1]:.0f} mm at the deck edges. Added in the 3D review (revision {REVISION}) because '
                  'the approach slab had no bearing. No sheet shows an end bent, paving notch, seat or approach slab '
                  'section (sheets 3, 4, 7, 8): the seat level follows from the assumed 0.30 m approach and 0.45 m '
                  'deck, and it may be read as a monolithic part of the hypothetical end wall.'),
            dimensions=dict(
                top_elevation_m=round(seat, 6), height_m=rise, height_at=['crown', 'deck edges'],
                width_along_station_m=round(seat_u, 6), width_normal_m=round(seat_u * cos, 6),
                length_across_m=round(WIDTH, 6), station_range_u_m=sorted([round(back, 6), round(deck_end, 6)]),
                rests_on=wid, carries=aid, assumed=True),
            bounds_m=mesh.bounds.round(6).tolist(), volume_m3=round(float(mesh.volume), 9))
        gltf['meshes'].append(dict(name=sid, extras=dict(p), primitives=[prim]))
        gltf['nodes'].append(dict(name=sid, mesh=len(gltf['meshes']) - 1))
        gltf['nodes'][0]['children'].append(len(gltf['nodes']) - 1)
        manifest['parts'].append(p)
        parts[sid] = p
        meshes[sid] = gltf['meshes'][-1]
        added.append(sid)

        wp['note'] = (wp.get('note', '') + f' Its back projection beyond the deck end carries the hypothetical '
                      f'approach seat {sid}, on which {aid} bears (3D review, revision {REVISION}).').strip()
        meshes[wid]['extras'].update(wp)
        ap = parts[aid]
        ap['note'] = (ap.get('note', '') + f' Bears on the hypothetical approach seat {sid} on {wid}, a '
                      f'{seat_u * cos:.3f} m strip (normal to the skew) at this slab\'s flat underside, '
                      f'Z = {seat:.6f} m (3D review, revision {REVISION}); the seat is not drawn.').strip()
        meshes[aid]['extras'].update(ap)
        annotated += [wid, aid]

        values[sid] = dict(
            seat_top_z_m=round(seat, 6), seat_height_m=f'{rise[0]:.6f} (crown) to {rise[1]:.6f} (deck edges)',
            seat_station_range_u_m=p['dimensions']['station_range_u_m'],
            seat_width_m=f'{seat_u:.6f} along the station = {seat_u * cos:.6f} normal to the skew, x {WIDTH:.6f} '
                         'across',
            seat_area_m2=round(seat_u * WIDTH, 6),
            gap_under_approach_mm=f'{old_gap[0]:.3f} (crown) to {old_gap[1]:.3f} (deck edges) -> 0',
            contacts=f'bottom on {wid} top, top under {aid}, riser on the deck end face; no overlap',
            bounds=p['bounds_m'], volume_m3=p['volume_m3'])
        print(f'{sid}: on {wid} under {aid}, {rise[0]:.6f}-{rise[1]:.6f} m high, top Z = {seat:.6f} m, '
              f'u {min(back, deck_end):+.6f} .. {max(back, deck_end):+.6f}; volume {mesh.volume:.9f} m3')

    # --- wings: cut out the corner that lies inside the end wall, so each volume belongs to one part ---
    def overlap(a, b):
        with np.errstate(divide='ignore', invalid='ignore'):   # an empty intersection has no centre of mass
            i = trimesh.boolean.intersection([a, b], engine='manifold')
            return float(i.volume) if len(i.vertices) else 0.0

    changed = []
    s_in, s_out, s_wall = WIDTH / 2 - WING_IN, WIDTH / 2 + WING_OUT, WIDTH / 2
    for gid, wid, e, side in WINGS:
        gv, gf = native(gid)
        wing = trimesh.Trimesh(vertices=gv, faces=gf, process=False)
        wv, wf = native(wid)
        wall = trimesh.Trimesh(vertices=wv, faces=wf, process=False)
        u0 = e * (LENGTH / 2 - EDGE)
        back, far = u0 + e * half_u, u0 + e * WING_LEN
        gu = gv[:, 0] - k * gv[:, 1]
        if (len(gv) != 8 or not wing.is_watertight or wing.volume <= 0
                or not np.all(np.min(np.abs(gu[:, None] - [u0, far]), axis=1) < TOL)
                or not np.all(np.min(np.abs(gv[:, 1:2] - side * np.array([s_in, s_out])), axis=1) < TOL)
                or not np.all(np.min(np.abs(gv[:, 2:3] - [WALL_BASE, WING_TOP]), axis=1) < TOL)):
            raise ValueError(f'{gid}: unexpected original wing geometry')
        # The wall top over the wing's inner 0.30 m is above the wing top, so the overlap is a full-height corner.
        notch = half_u * (s_wall - s_in) * (WING_TOP - WALL_BASE)
        before_overlap = overlap(wing, wall)
        if soffit(s_wall) <= WING_TOP or abs(before_overlap - notch) > 1e-4:
            raise ValueError(f'{gid}: unexpected overlap with {wid} ({before_overlap} vs {notch})')
        # Plan ring (u, |Y|) of the trimmed wing, an L: starting at the far outer corner, a fan from vertex 0
        # triangulates it. The notch faces lie in the wall's back face (u = back) and end face (|Y| = 7.18185 m).
        ring = [(far, s_out), (far, s_in), (back, s_in), (back, s_wall), (u0, s_wall), (u0, s_out)]
        verts = np.array([(uu + k * side * ss, side * ss, zz) for zz in (WALL_BASE, WING_TOP) for uu, ss in ring])
        n = len(ring)
        tri = [(0, j + 1, j) for j in range(1, n - 1)] + [(n, n + j, n + j + 1) for j in range(1, n - 1)]
        for j in range(n):
            a, b = j, (j + 1) % n
            tri += [(a, b, b + n), (a, b + n, a + n)]
        mesh = trimesh.Trimesh(vertices=verts, faces=np.array(tri), process=False)
        mesh.fix_normals()
        built = WING_LEN * (WING_OUT + WING_IN) * (WING_TOP - WALL_BASE)
        if (not mesh.is_watertight or not mesh.is_winding_consistent or mesh.volume <= 0
                or abs(mesh.volume - (built - notch)) > 1e-9 or abs(wing.volume - built) > 1e-4):
            raise ValueError(f'{gid}: invalid trimmed wing ({mesh.volume} vs {built - notch})')
        after_overlap = overlap(mesh, wall)
        if after_overlap > 1e-6:
            raise ValueError(f'{gid}: still overlaps {wid} by {after_overlap} m3')
        glv = to_gltf(mesh.vertices).astype('<f4')
        # Unchanged corners stay bitwise where they were.
        kept = to_gltf(gv).astype('<f4')
        moved = (np.abs(gu - u0) < TOL) & (np.abs(np.abs(gv[:, 1]) - s_in) < TOL)
        for v in kept[~moved]:
            if not (glv == v).all(axis=1).any():
                raise ValueError(f'{gid}: an unchanged wing corner moved')
        wall_prim = meshes[wid]['primitives'][0]
        if gltf['accessors'][wall_prim['attributes']['COLOR_0']]['count'] != len(glv) or not np.array_equal(
                read(wall_prim['attributes']['COLOR_0'])[0], read(meshes[gid]['primitives'][0]['attributes']['COLOR_0'])[0]):
            raise ValueError(f'{gid}: cannot share the wall colour accessor')
        prim = meshes[gid]['primitives'][0]
        prim['attributes'] = dict(POSITION=append(glv, 'VEC3', 5126), COLOR_0=wall_prim['attributes']['COLOR_0'])
        prim['indices'] = append(mesh.faces.astype('<u4').reshape(-1), 'SCALAR', 5125)

        p = parts[gid]
        old_bounds, old_volume = p['bounds_m'], p['volume_m3']
        p['bounds_m'] = mesh.bounds.round(6).tolist()
        p['volume_m3'] = round(float(mesh.volume), 9)
        p['dimensions'].update(
            trimmed_at=f'{wid} back face and end face (3D review)',
            notch_along_station_m=round(half_u, 6), notch_across_m=round(s_wall - s_in, 6),
            overlap_removed_m3=round(notch, 6))
        p['note'] = (p.get('note', '') + f' Trimmed at the faces of {wid} in the 3D review (revision {REVISION}): '
                     f'the wing started at the support line, so its {half_u:.3f} m (along the station) by '
                     f'{s_wall - s_in:.3f} m corner lay inside the end wall over its full height '
                     f'({notch:.3f} m3 counted twice). That corner is cut out; the wing now stops at the wall\'s back '
                     'face and runs past the wall\'s end face to the support line. No sheet shows the wings or how '
                     'they meet the end wall, so this division at the wall faces is a modelling choice.').strip()
        meshes[gid]['extras'].update(p)
        changed.append(gid)
        values[gid] = dict(
            overlap_with_wall_m3=f'{before_overlap:.6f} -> {after_overlap:.9f}',
            notch_m=f'{half_u:.6f} along the station x {s_wall - s_in:.6f} across (|Y| {s_in:.6f} .. {s_wall:.6f}) '
                    f'x {WING_TOP - WALL_BASE:.2f} high',
            contacts=f'wall back face (u = {back:+.6f}) over |Y| {s_in:.6f} .. {s_wall:.6f}; wall end face '
                     f'(|Y| = {s_wall:.6f}) over u {min(back, u0):+.6f} .. {max(back, u0):+.6f}',
            vertices='8 -> 12', bounds_before=old_bounds, bounds_after=p['bounds_m'],
            volume_m3=f'{old_volume} -> {p["volume_m3"]}')
        print(f'{gid}: overlap with {wid} {before_overlap:.6f} -> {after_overlap:.9f} m3; volume '
              f'{wing.volume:.9f} -> {mesh.volume:.9f} m3')

    for d in manifest.get('detail_coverage', []):
        if d.get('feature') == 'Hypothetical load-bearing scaffold':
            d['detail'] = (d['detail'] + ' Hypothetical approach seats seat_0 and seat_1 sit on the end walls\' back '
                           'projections beyond the deck ends (0.259 m normal to the skew) and reach the flat '
                           'approach-slab underside, so approach_0 and approach_1 bear on support_0 and support_3. No '
                           'sheet shows an end bent, seat or approach slab section. The wings stop at the end-wall '
                           'faces, so walls and wings share no volume; that division is not drawn either.')
            d['part_ids'] = d['part_ids'] + [s for s in added if s not in d['part_ids']]

    gltf['buffers'][0]['byteLength'] = len(binary)
    while len(binary) % 4:
        binary.append(0)
    encoded = json.dumps(gltf, ensure_ascii=True, separators=(',', ':')).encode()
    encoded += b' ' * ((-len(encoded)) % 4)
    out = (struct.pack('<III', 0x46546c67, 2, 28 + len(encoded) + len(binary)) +
           struct.pack('<II', len(encoded), 0x4e4f534a) + encoded + struct.pack('<II', len(binary), 0x004e4942) + binary)
    backup = ROOT / 'data/fem_research'
    backup.mkdir(exist_ok=True)
    (backup / f'{BID}_before_3d_review.glb').write_bytes(original)
    (backup / f'{BID}_manifest_before_3d_review.json').write_bytes(raw_manifest)
    path.write_bytes(out)
    manifest[TAG_KEY] = TAG
    manifest['revision'] = REVISION
    manifest[RECORD_KEY] = dict(
        review='3D placement review, round 4',
        source_pdf_pages=[3, 4, 7, 8], printed_sheets=[3, 4, 7, 8], previous_revision=PREVIOUS_REVISION,
        findings=[dict(id='S01', verdict='resolve', hypothetical=True,
                       summary='approach slabs did not bear on the end-wall shelf (38-150 mm air gap); explicitly '
                               'hypothetical approach seats now carry them on the end walls'),
                  dict(id='wing-wall-overlap', verdict='resolve', hypothetical=True,
                       source='found while verifying S01; fixed at the lead\'s request',
                       summary='each wing overlapped its end wall by 0.529960 m3 (2.12 m3 counted twice); the wings '
                               'are trimmed at the end-wall faces, a division no sheet shows')],
        changed_parts=changed, annotated_parts=annotated, added_parts=added, removed_parts=[],
        values=dict(values, basis='no sheet shows the end bent, a seat, the wings or the approach slab section '
                                  '(sheet 3 general notes, sheet 4 location table, sheet 7 plan and deck-only typical '
                                  'section, sheet 8 quantities); seat level = assumed approach underside 6.0 - 0.0156 x '
                                  '7.18185 - 0.30 = 5.587963 m; seat plan = the projection of the assumed 0.80 m end '
                                  'wall beyond the deck end; wings trimmed at the end-wall back and end faces'),
        kept_deviations=[], decisions=[],
        before_glb_sha256=before, after_glb_sha256=hashlib.sha256(out).hexdigest())
    text = json.dumps(manifest, indent=2)
    if b'\r\n' in raw_manifest:
        text = text.replace('\n', '\r\n')
    if raw_manifest.endswith(b'\n'):
        text += '\r\n' if b'\r\n' in raw_manifest else '\n'
    mp.write_bytes(text.encode('utf-8'))
    print(json.dumps(manifest[RECORD_KEY]))


if __name__ == '__main__':
    correct()

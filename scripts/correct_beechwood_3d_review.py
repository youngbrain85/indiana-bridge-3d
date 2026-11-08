"""Fourth correction of Beechwood Road over Little Blue River (beechwood), from the 3D review of the assembled model:
the deck underside is crowned like its top, so the deck is 8 in thick everywhere. Runs after
scripts/correct_beechwood_columns.py and scripts/correct_beechwood_wings.py and keeps every GLB buffer it does not
replace.

    python scripts/correct_beechwood_3d_review.py

Source: drawings.pdf; PDF page = printed sheet + 1. Native axes: X increasing station (north), +Y to the left looking
up-station (west), Z up from El. 390 ft (model_manifest.json orientation).

S1 deck soffit (RESOLVED). Printed sheet 45 (PDF 46) BRIDGE TYPICAL SECTION and printed sheet 46 (PDF 47) BRIDGE
TYPICAL SECTION and Detail "A" draw the deck top and underside parallel, both falling 2 % from the crown on the
centre line to the copings, with "8" Deck" dimensioned at mid-width and "8" (Typ.)" at the coping; the beam top
flanges are level and the haunch fills between the flange and the crowned underside ("Varies" in sections A-A and
B-B, sheet 46). The model's deck cross-section had the crowned top and, outside the 3/4 in half-round drip grooves
(6 in from each coping), the crowned underside, but joined the inner edges of the two drip grooves
(Y = -/+4.867275 m) with one straight, flat chord. The deck was therefore 8 in thick only at the drip grooves and
8 in + 2 % x 4.867 m = 11.83 in (300.5 mm) at the crown, and it filled the space that the haunches, beam tops,
pier diaphragms and end-bent concrete occupy: all of those are already fitted to the crowned underside
(top - 8 in). This script replaces the chord by the crowned underside (Z = top - 0.2032 m, i.e. chord +
2 % x (4.867275 - |Y|)): it adds a crown vertex on the centre line at each of the deck's own stations (the -4.269 %
tangent and the vertical-curve stations), replaces each chord strip by two planar strips meeting at the crown, and
re-triangulates the end-face triangles that reached into the removed wedge. No other vertex moves: the top, the saw
grooves, the drip grooves, the copings and the deck ends are unchanged. No other part moves: the
haunch tops, the pier diaphragm tops and the Pour B tops now meet the deck underside, and the beam tops stay under
the haunches.

Requires numpy, trimesh, shapely, mapbox_earcut (trimesh earcut engine) and manifold3d (overlap checks).
"""
import hashlib
import json
import struct
from pathlib import Path

import numpy as np
import trimesh
from shapely.geometry import Polygon
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[1]

BID = 'beechwood'
BASE = ROOT / 'data/bridges' / BID
IN = 0.0254
TAG_KEY = 'review_correction_3d'
TAG = 'deck-underside-crowned-8in'
RECORD_KEY = 'review_correction_record_3d'
REVISION = '2.3-3d-review'
PREVIOUS_TAG = 'wing-profile-straight-12ft-11ft'            # scripts/correct_beechwood_wings.py
PREVIOUS_REVISION = '2.2-wing-profile'
EXPECTED_GLB_SHA256 = '4ae98985d7c34cb74533dfb73170679169cf1dd75d1ecd214baa518d21945803'   # revision 2.2 output

DECK_T = 8 * IN                                  # sheets 45, 46: 8" deck
CROSSFALL = 0.02                                 # sheets 45, 46: 2 % each side of the crown
Y_DRIP = (16.5 * 12 - 6 - 0.375) * IN            # inner edge of the 3/4" drip groove, 6" from the 16'-6" coping
FITTED = ([f'haunch_{s}{i}' for s in 'ABC' for i in (1, 2, 3, 4)] + [f'girder_{s}{i}' for s in 'ABC' for i in (1, 2, 3, 4)]
          + ['b2_diaphragm', 'b3_diaphragm', 'b1_integral', 'b4_integral'])


def expect(ok, message):
    if not ok:
        raise ValueError(message)


def rays(mesh, pts, down=True):
    """Z of every crossing of vertical rays through (x, y), sorted, one array per point."""
    pts = np.asarray(pts, dtype=float)
    z0 = mesh.bounds[1][2] + 1.0 if down else mesh.bounds[0][2] - 1.0
    origins = np.c_[pts, np.full(len(pts), z0)]
    dirs = np.tile([0.0, 0.0, -1.0 if down else 1.0], (len(pts), 1))
    loc, idx, _ = mesh.ray.intersects_location(origins, dirs, multiple_hits=True)
    return [np.unique(np.round(loc[idx == k, 2], 7)) for k in range(len(pts))]


def correct():
    mp = BASE / 'model_manifest.json'
    raw_manifest = mp.read_bytes()
    manifest = json.loads(raw_manifest)
    if manifest.get(TAG_KEY) == TAG:
        print('Already corrected.')
        return
    expect(manifest.get('wing_profile_correction') == PREVIOUS_TAG and manifest.get('revision') == PREVIOUS_REVISION,
           f'run scripts/correct_beechwood_wings.py first (revision {manifest.get("revision")})')
    path = BASE / 'model.glb'
    original = path.read_bytes()
    before = hashlib.sha256(original).hexdigest()
    expect(before == EXPECTED_GLB_SHA256 == manifest['wing_profile_correction_record']['after_glb_sha256'],
           f'model.glb SHA-256 {before} is not the revision {PREVIOUS_REVISION} output')
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

    def solid(pid):
        prim = meshes[pid]['primitives'][0]
        return trimesh.Trimesh(vertices=read(prim['attributes']['POSITION']).astype(np.float64),
                               faces=read(prim['indices']).reshape(-1, 3), process=False)

    prim = meshes['deck']['primitives'][0]
    deck = solid('deck')
    expect(deck.is_watertight and deck.volume > 0, 'deck: not a closed solid')
    v, f = deck.vertices, deck.faces

    # The flat chord: down-facing faces whose corners all lie on the inner edges of the two drip grooves.
    on_edge = np.isclose(np.abs(v[:, 1]), Y_DRIP, atol=2e-6)
    chord = np.where(np.all(on_edge[f], axis=1) & (deck.face_normals[:, 2] < -0.999))[0]
    corners = np.unique(f[chord])
    xs = np.unique(v[corners, 0])
    expect(len(xs) >= 2 and len(corners) == 2 * len(xs) and len(chord) == 2 * (len(xs) - 1),
           f'deck: unexpected soffit chord ({len(chord)} faces, {len(corners)} corners)')
    A, B = [], []                                  # chord corners at each station, -Y (east) and +Y (west)
    for x in xs:
        at = corners[v[corners, 0] == x]
        expect(len(at) == 2 and v[at[0], 2] == v[at[1], 2] and v[at[0], 1] == -v[at[1], 1],
               f'deck: chord not level across at X = {x}')
        A.append(at[v[at, 1] < 0][0])
        B.append(at[v[at, 1] > 0][0])
    zs = v[A, 2]
    y_e = float(v[B[0], 1])
    expect(np.allclose(v[B, 1], y_e) and abs(y_e - Y_DRIP) < 1e-6, 'deck: drip-groove edge not at 6 3/8 in')
    expect(xs[0] == deck.bounds[0][0] and xs[-1] == deck.bounds[1][0], 'deck: chord does not run the full deck length')

    # Starting state: flat underside at the crown, 8 in + 2 % x Y_DRIP thick; crowned 8 in outside the drip grooves.
    probe_x = np.array([12.0, 38.1, 64.0, 74.5])
    t0 = [np.ptp(z) for z in rays(deck, np.c_[probe_x, np.zeros(len(probe_x))])]
    expect(np.allclose(t0, DECK_T + CROSSFALL * Y_DRIP, atol=2e-4), f'deck: unexpected crown thickness {t0}')

    # New underside: a crown vertex C on the centre line at each chord station, 2 % x y_e above the chord, and two
    # planar strips A-C and C-B per segment in place of the chord strip.
    rise = CROSSFALL * y_e
    crown = np.c_[xs, np.zeros(len(xs)), zs + rise].astype(np.float32).astype(np.float64)
    C = list(range(len(v), len(v) + len(xs)))
    verts = np.vstack([v, crown])

    def down(tri):
        a, b, c = verts[list(tri)]
        return tri if np.cross(b - a, c - a)[2] < 0 else tri[::-1]

    soffit_faces = []
    for k in range(len(xs) - 1):
        for p0, p1 in ((A, C), (C, B)):
            soffit_faces += [down((p0[k], p1[k], p1[k + 1])), down((p0[k], p1[k + 1], p0[k + 1]))]

    # End faces: the end-face triangles that reach into the removed wedge are re-triangulated around A-C-B.
    cap_old, cap_new = [], []
    for k, sign in ((0, -1.0), (len(xs) - 1, 1.0)):
        x_e = xs[k]
        at_end = np.all(v[f][:, :, 0] == x_e, axis=1) & (np.abs(deck.face_normals[:, 0]) > 0.999)
        wedge = Polygon([(-y_e, zs[k]), (y_e, zs[k]), (0.0, crown[k, 2])])
        hit = [i for i in np.where(at_end)[0] if Polygon(v[f[i]][:, 1:]).intersection(wedge).area > 1e-12]
        region = unary_union([Polygon(v[f[i]][:, 1:]) for i in hit])
        kept = region.difference(wedge)
        expect(isinstance(kept, Polygon) and not kept.interiors and kept.is_valid,
               f'deck: end face at X = {x_e} does not leave one simple region')
        lookup = {(verts[i, 1], verts[i, 2]): i for i in np.r_[np.unique(f[at_end]), C[k]]}
        tv, tf = trimesh.creation.triangulate_polygon(kept, engine='earcut')
        index = []
        for y, z in tv:
            key = (float(y), float(z))
            expect(key in lookup, f'deck: end face at X = {x_e}: unexpected vertex ({y}, {z})')
            index.append(lookup[key])
        for t in tf:
            tri = tuple(index[j] for j in t)
            a, b, c = verts[list(tri)]
            cap_new.append(tri if np.cross(b - a, c - a)[0] * sign > 0 else tri[::-1])
        cap_old += hit
        expect(abs(region.area - kept.area - wedge.area) < 1e-9, f'deck: end face at X = {x_e}: area check')

    drop = np.zeros(len(f), bool)
    drop[chord] = True
    drop[cap_old] = True
    new = trimesh.Trimesh(verts, np.vstack([f[~drop], soffit_faces, cap_new]), process=False)
    new.remove_unreferenced_vertices()
    removed = deck.volume - new.volume
    nominal = y_e * rise * (xs[-1] - xs[0])
    expect(new.is_watertight and new.is_winding_consistent and new.volume > 0, 'deck: result is not a closed solid')
    # The crown vertices are stored as float32 (about 1 um in Z), so the removed volume matches to 1e-4 m3.
    expect(abs(removed - nominal) < 5e-4, f'deck: removed {removed:.6f} m3, expected {nominal:.6f} m3')
    expect(len(new.split(only_watertight=False)) == 1, 'deck: result is not one body')
    expect(np.allclose(new.bounds, deck.bounds, atol=1e-6), 'deck: bounds changed')

    # Thickness check on a grid inside the drip grooves: 8 in, or 8 in less a 3/16 in saw groove.
    gx, gy = np.meshgrid(np.r_[np.linspace(xs[0] + 0.05, xs[-1] - 0.05, 41), [72.3, 74.0, 76.3]],
                         np.linspace(-Y_DRIP + 0.005, Y_DRIP - 0.005, 61))
    grid = np.c_[gx.ravel(), gy.ravel()]
    hits = rays(new, grid)
    thick = np.array([np.ptp(z) if len(z) == 2 else np.nan for z in hits])
    expect(np.isfinite(thick).all(), 'deck: a grid ray does not cross the deck exactly twice')
    groove = 0.1875 * IN
    ok = np.isclose(thick, DECK_T, atol=5e-5) | np.isclose(thick, DECK_T - groove, atol=5e-5)
    expect(ok.all(), f'deck: thickness outside 8 in at {grid[~ok][:5]} ({thick[~ok][:5]})')
    soffit = np.array([z[0] for z in hits])
    expect(np.allclose(soffit, np.interp(grid[:, 0], xs, zs) + CROSSFALL * (Y_DRIP - np.abs(grid[:, 1])), atol=5e-5),
           'deck: underside is not the crowned profile')

    # Parts fitted to the crowned underside: no shared volume left; their tops touch the deck.
    overlaps = {}
    for pid in FITTED:
        part = solid(pid)
        was = trimesh.boolean.intersection([deck, part], engine='manifold').volume
        now = trimesh.boolean.intersection([new, part], engine='manifold').volume
        overlaps[pid] = dict(before_m3=round(float(was), 6), after_m3=round(float(now), 6))
        # What is left is a film of at most 0.05 mm: float32 vertices and the deck's straight segments between its
        # vertical-curve stations against the parts' own stations (b4_integral: 0.042 mm at X = 76.21 m, the same
        # as outside the drip grooves before this correction).
        expect(now < 2e-4, f'{pid}: still shares {now:.6f} m3 with the deck')
        lo, hi = part.bounds
        gx, gy = np.meshgrid(np.linspace(max(lo[0], xs[0]) + 0.01, min(hi[0], xs[-1]) - 0.01, 41),
                             np.linspace(max(lo[1], -Y_DRIP) + 0.003, min(hi[1], Y_DRIP) - 0.003, 9))
        pts = np.c_[gx.ravel(), gy.ravel()]
        pairs = [(a[-1], b[0]) for a, b in zip(rays(part, pts), rays(new, pts)) if len(a) and len(b)]
        gap = np.array([b - a for a, b in pairs])
        expect(len(gap) and gap.min() > -5e-5, f'{pid}: reaches {-gap.min():.6f} m into the deck')
        if pid.startswith('haunch_'):
            expect(gap.max() < 5e-5, f'{pid}: top is {gap.max():.6f} m below the deck')
        overlaps[pid]['max_penetration_mm'] = round(float(max(0.0, -gap.min())) * 1000, 3)
        if pid.startswith('haunch_'):
            overlaps[pid]['max_gap_to_soffit_mm'] = round(float(max(0.0, gap.max())) * 1000, 3)
        elif pid.startswith('girder_'):
            overlaps[pid]['min_clearance_to_soffit_mm'] = round(float(gap.min()) * 1000, 3)

    # Write the deck primitive (new accessors appended; every other buffer unchanged).
    color = read(prim['attributes']['COLOR_0'])[0]
    prim['attributes'] = {'POSITION': append(new.vertices.astype('<f4'), 'VEC3', 5126),
                          'COLOR_0': append(np.tile(color, (len(new.vertices), 1)).astype('u1'), 'VEC4', 5121)}
    gltf['accessors'][prim['attributes']['COLOR_0']]['normalized'] = True
    prim['indices'] = append(new.faces.reshape(-1, 1).astype('<u4'), 'SCALAR', 5125)
    stored = solid('deck')
    welded = stored.copy()
    welded.merge_vertices(digits_vertex=5)
    expect(welded.is_watertight and welded.volume > 0, 'deck: stored mesh is not watertight')

    p = parts['deck']
    old_volume = p['volume_m3']
    p['bounds_m'] = stored.bounds.round(6).tolist()
    p['volume_m3'] = round(float(stored.volume), 6)
    p['dimensions']['underside_crossfall_pct'] = 2
    p['note'] = (p.get('note', '') + f' Underside crowned 2 % parallel to the top, 8 in thick throughout (sheets 45, 46);'
                 f' it was a flat chord between the drip grooves, 11.83 in thick at the crown (3D review, revision '
                 f'{REVISION}).').strip()
    extras = meshes['deck']['extras']
    extras.update({k: p[k] for k in extras if k in p})

    while len(binary) % 4:
        binary.append(0)
    gltf['buffers'][0]['byteLength'] = len(binary)
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
        source_pdf_pages=[46, 47], printed_sheets=[45, 46], previous_revision=PREVIOUS_REVISION,
        changed_parts=['deck'], added_parts=[], removed_parts=[],
        resolved={'S1': 'Deck underside crowned 2 % parallel to the top: 8 in (0.2032 m) thick across the whole width, '
                        'was a flat chord between the drip-groove inner edges (Y = -/+4.867275 m), 0.3005 m thick at '
                        'the crown; it no longer fills the haunches, beam tops, pier diaphragm tops or Pour B tops, '
                        'which were already fitted to the crowned underside (sheets 45, 46).'},
        decisions=[], kept=[],
        values=dict(
            crown_thickness_m=dict(before=round(float(np.mean(t0)), 6), after=DECK_T),
            removed_volume_m3=round(float(removed), 6),
            deck_volume_m3=dict(before=old_volume, after=p['volume_m3']),
            chord_stations=len(xs), overlaps_with_deck=overlaps),
        before_glb_sha256=before, after_glb_sha256=hashlib.sha256(out).hexdigest())
    mp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    record = manifest[RECORD_KEY]
    print(json.dumps({k: v for k, v in record.items() if k != 'values'}, indent=1))
    print(json.dumps({k: v for k, v in record['values'].items() if k != 'overlaps_with_deck'}))
    for pid, o in overlaps.items():
        print(f'{pid:14s} shared with deck {o["before_m3"]:.6f} -> {o["after_m3"]:.6f} m3')


if __name__ == '__main__':
    correct()

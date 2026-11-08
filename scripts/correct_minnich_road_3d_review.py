"""Fourth-round correction of Minnich Road (3D review): cross-frame connections and duplicate stiffeners.

    python scripts/correct_minnich_road_3d_review.py

Runs after scripts/correct_minnich_road_review_3.py (revision 1.3-deviations). INDOT B-44533; in this set the printed
sheet number equals the PDF page number. Findings S1 and S2 of the 3D review of the assembled model.

S1 (all 84 ordinary X frames stood about 51 mm clear of both girders). Each frame now hangs on the connection plates
the sheets draw for cross frames, and its two diagonals lap onto those plates.
  - Connection plates (sheets 25, 27, 28, 30, 31, 33): PL 1" x 8" on the web face of each girder, on the bay side,
    the full web height between the flanges (sheet 33 PL 1" x 8" x 5'-6" for the 66 in web), with the 1 1/2" x
    2 1/2" corner clips of the sheet 25 Typical Stiffener or Connection Plate details. The plate is centred on the
    frame plane. Its top and bottom follow the flange faces of the girder mesh at the plate, and its inner face is the
    web face, so it bears on the web and both flanges.
  - Diagonals: the representative 100 x 12 mm flat bars (the section the FEM demonstration assumes), now flat in the
    frame plane, one on each face of the plates, as sheet 33 implies (1" x 12" filler between the crossing diagonals,
    the plate thickness). Each ends square 1 3/4" from the web face, as the sheet 33 Typical Frame Bolted Connection
    Detail places the angle end (1 3/4" + 3" + 1 1/2" in from the plate edge), so it laps 6 1/4" onto the plate.
  - frame_0_1_* and frame_3_0_* are the drawn Cross-Frame Detail - Span A / Span D nearest Bents 2 and 4. Their
    generator station put one end inside the field-splice plates, so they move to the drawn station: on the new
    girder at its bottom taper, 12'-0" from the Bent 2 / Bent 4 bearing line (sheets 27-28, 30-31: 1" x 8" plate,
    one each side, the bay-side one the cross-frame connection plate), and 1'-6" past the bent on the existing girder.
    The model skew (9'-0" x tan 56 deg 17' 55" = 13.494 ft, not the 13'-6" the elevations use) puts that second end
    1.8 mm short of 1'-6"; the new-girder end is kept exact. Work points per sheet 33 (dimensioned at the web centre
    lines): 1 3/4" below the lower girder's top flange and 10 1/4" above the higher girder's bottom flange; the drawn
    3 1/2" / 1 3/4" and 10 1/4" / 12" pairs describe a level frame between girders 1 3/4" apart, and are read so
    (decision). The drawn L 3 1/2 x 3 1/2 x 3/8 angles, bottom strut, filler plate and bolts are not modelled.
  - The 72 frames of the retained main spans B and C keep their generator stations and work-point levels (0.12 m
    from the top and bottom of steel at mid-bay); only the work points move from 0.24 m off the girder centre lines
    to the web centre lines, so the bars reach the plates without touching the flanges. Their own members and
    connections are on the original plans, which are not in this set; the drawn typical connection stands in for
    them (known deviation existing-main-span-cross-frames).

S2 (stiffener_j_2 and stiffener_j_12 identical for every girder). The generator sampled the Bent 3 station twice: as a
support and as the middle of np.linspace(bs[1] + 4, bs[3] - 4, 15). The eight copies stiffener_j_12 are removed;
stiffener_j_2 stays. No FEM id is affected. source_ledger.json lists the removed ids in its part lists; they are
dropped there too.

The script checks the starting revision, GLB SHA-256 and deviation list, and that the generator formulas reproduce
the 84 frames it rebuilds. Only new accessors are appended; the earlier binary chunk is kept. Every new mesh is
checked as stored (float32, welded at 10 um, each body closed). Requires numpy, trimesh and manifold3d.
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
# Generator and third-correction geometry (the same formulas that built the current model).
from correct_minnich_road_review_3 import (BS, CLEAR, FT, IN, K, SLAB, WEB_T, YS, close, depth,  # noqa: E402
                                           dz, loft, old_frame, surface, sx)
from refresh_geometry_verification import bodies  # noqa: E402  (its closed-mesh test, read only)

BID = 'minnich-road'
TAG_KEY, TAG = 'review_correction_3d', '3d-review-frame-connection-plates-duplicate-stiffeners'
REVISION, PREVIOUS_REVISION = '1.4-3d-review', '1.3-deviations'
PREVIOUS_TAG = 'known-deviations-pvi-end-bent-stack-mudwall-channel-diaphragms'
START_GLB = '31ee7adbabcc6b381f12861611d775a1fe59ecbdab952682fcb296ca9ef46b68'
START_PARTS = 466
DEVIATIONS = {'existing-wingwalls'}

CP_T, CP_W = 1 * IN, 8 * IN                    # PL 1" x 8" cross-frame connection plate (sheets 27-28, 30-31, 33)
CLIP_H, CLIP_V = 1.5 * IN, 2.5 * IN            # corner clips at the web (sheet 25 typical details, sheet 33)
BAR_W, BAR_T = .10, .012                       # representative flat diagonals (generator; FEM rect(.10, .012))
BAR_END = 1.75 * IN                            # angle end from the web face: 8" - (1 3/4" + 3" + 1 1/2") (sheet 33)
TOP_WP, BOTTOM_WP = 1.75 * IN, 10.25 * IN      # sheet 33 work points: 1 3/4" below the lower top flange, 10 1/4"
                                               # (5" + 5 1/4") above the higher bottom flange
DRAWN_STATION = 12 * FT                        # new-girder end at the bottom taper, from the Bent 2 / 4 bearing line
EXISTING_END = 1.5 * FT                        # the other end, past the bent on the existing girder (sheets 27-31)
ROWS = {i: np.linspace(a + .8, b - .8, max(2, int((b - a) / 7))) for i, (a, b) in enumerate(zip(BS[:-1], BS[1:]))}
DRAWN = {(0, 1), (3, 0)}                       # (span, row) of the drawn Cross-Frame Detail - Span A / Span D
FRAMES = [(i, r, j) for i, rows in ((0, [1]), (1, range(6)), (2, range(6)), (3, [0])) for r in rows
          for j in (0, 1, 2, 4, 5, 6)]
DUPLICATES = [(f'stiffener_{j}_2', f'stiffener_{j}_12') for j in range(8)]


def rounded(**dims):
    return {k: round(float(v), 6) for k, v in dims.items()}


def heights_at(mesh, x, y):
    """Z of every face of `mesh` above (x, y) (vertical line through the triangles' XY projections)."""
    v = mesh.vertices[mesh.faces]
    a, b, c = v[:, 0, :2], v[:, 1, :2], v[:, 2, :2]
    p = np.array([x, y])

    def cross(u, w):
        return u[..., 0] * w[..., 1] - u[..., 1] * w[..., 0]
    d = cross(b - a, c - a)
    ok = np.abs(d) > 1e-12
    d = np.where(ok, d, 1.0)
    l1, l2 = cross(b - p, c - p) / d, cross(c - p, a - p) / d
    l3 = 1 - l1 - l2
    inside = ok & (l1 >= -1e-9) & (l2 >= -1e-9) & (l3 >= -1e-9)
    z = l1 * v[:, 0, 2] + l2 * v[:, 1, 2] + l3 * v[:, 2, 2]
    return np.unique(np.round(z[inside], 7))


class Girder:
    """The four span meshes of one girder line, as stored (float32 positions in native axes)."""

    def __init__(self, line, meshes):
        self.y, self.parts = YS[line], meshes

    def part_at(self, x, side):
        probe = self.y + side * (WEB_T / 2 + .1)              # over the flange overhang, clear of the web
        for name, m in self.parts:
            z = heights_at(m, x, probe)
            if len(z):
                if len(z) != 4:
                    raise ValueError(f'girder line {self.y}: {len(z)} faces at x={x}')
                return name, m, z
        raise ValueError(f'no girder at x={x}, y={self.y}')

    def flanges(self, x, side):
        """(top of the bottom flange, underside of the top flange) at x."""
        z = self.part_at(x, side)[2]
        return float(z[1]), float(z[2])

    def web_face(self, x, side):
        """Y of the web face as stored, so the plate face coincides with it exactly."""
        name, m, _ = self.part_at(x, side)
        target = self.y + side * WEB_T / 2
        vy = m.vertices[:, 1]
        y = float(vy[np.argmin(np.abs(vy - target))])
        if abs(y - target) > 1e-5:
            raise ValueError(f'{name}: web face not found')
        return name, y

    def stations(self, x0, x1):
        """Ring stations of the girder strictly inside (x0, x1), so the plate follows any break of the flanges."""
        xs = set()
        for _, m in self.parts:
            xs |= {float(v) for v in np.unique(np.round(m.vertices[:, 0], 6)) if x0 + 1e-4 < v < x1 - 1e-4}
        return sorted(xs)


def connection_plate(girder, xc, side):
    """PL 1" x 8" on the web face toward `side` (+1: +Y), full web height, clipped at the web; centred on x = xc."""
    x0, x1 = xc - CP_T / 2, xc + CP_T / 2
    name, yw = girder.web_face(xc, side)
    rings = []
    for x in [x0] + girder.stations(x0, x1) + [x1]:
        zb, zt = girder.flanges(x, side)
        outline = [(0, zb + CLIP_V), (CLIP_H, zb), (CP_W, zb), (CP_W, zt), (CLIP_H, zt), (0, zt - CLIP_V)]
        rings.append([(x, yw + side * d, z) for d, z in outline])
    return name, loft(rings, axes=(1, 2))


def flat_bar(p0, p1, x0, x1):
    """Flat bar BAR_W wide in the frame plane between axis points p0, p1 (y, z), square ends, from x0 to x1."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    a = (p1 - p0) / np.linalg.norm(p1 - p0)
    n = np.array([-a[1], a[0]]) * BAR_W / 2
    corners = [p0 - n, p1 - n, p1 + n, p0 + n]
    return loft([[(x, y, z) for y, z in corners] for x in (x0, x1)], axes=(1, 2))


def frame_geometry(i, row, j, girders):
    """Plates and diagonals of frame_{i}_{row}_{j}; bay j lies between girder lines j (west) and j + 1 (east)."""
    west, east = girders[j], girders[j + 1]
    yw, ye, ym = west.y, east.y, (west.y + east.y) / 2
    if (i, row) in DRAWN:
        # New-girder end at the bottom taper: the west girder in Span A, the east girder in Span D (sheets 27-31).
        xc = sx(BS[1] - DRAWN_STATION, yw) if i == 0 else sx(BS[3] + DRAWN_STATION, ye)
        (bw, tw), (be, te) = west.flanges(xc, 1), east.flanges(xc, -1)
        top, bottom = min(tw, te) - TOP_WP, max(bw, be) + BOTTOM_WP
    else:
        # Generator rule (scripts/build_indiana_batch2.py minnich(), re-graded in revision 1.3).
        u = ROWS[i][row]
        xc = sx(u, ym)
        top = float(surface(xc, ym)) - SLAB - CLEAR - .12
        bottom = top - depth(u) + .24
    plate_names, plates = zip(connection_plate(west, xc, 1), connection_plate(east, xc, -1))
    ya, yb = yw + WEB_T / 2 + BAR_END, ye - WEB_T / 2 - BAR_END
    bars = []
    for (z_west, z_east), face in (((bottom, top), 1), ((top, bottom), -1)):      # one diagonal on each plate face
        wa, wb = np.array([yw, z_west]), np.array([ye, z_east])
        p0, p1 = (wa + (y - yw) / (ye - yw) * (wb - wa) for y in (ya, yb))
        x0 = xc + face * CP_T / 2
        bars.append(flat_bar(p0, p1, min(x0, x0 + face * BAR_T), max(x0, x0 + face * BAR_T)))
    info = dict(xc=xc, top=top, bottom=bottom, plates=plate_names, bar_length=float(np.hypot(yb - ya, top - bottom)))
    return list(plates), bars, info


def stored_closed(mesh):
    """scripts/refresh_geometry_verification.py's test on the mesh as stored: float32 positions, split into the
    index-connected bodies, welded at 10 um, each body closed with positive volume."""
    v32 = np.asarray(mesh.vertices, np.float32).astype(np.float64)
    parts = list(bodies(v32, np.asarray(mesh.faces)))
    return all(b.is_watertight and b.volume > 0 for b in parts), len(parts)


def correct(base, backup):
    mp = base / 'model_manifest.json'
    raw_manifest = mp.read_bytes()
    manifest = json.loads(raw_manifest)
    if manifest.get(TAG_KEY) == TAG:
        print('Already corrected.')
        return
    path = base / 'model.glb'
    original = path.read_bytes()
    before = hashlib.sha256(original).hexdigest()
    lp = base / 'source_ledger.json'
    raw_ledger = lp.read_bytes()

    def expect(ok, message):
        if not ok:
            raise ValueError(message)

    expect(manifest.get('review_correction_3') == PREVIOUS_TAG and manifest.get('revision') == PREVIOUS_REVISION,
           'Manifest is not the third-correction revision 1.3.')
    expect(before == START_GLB == manifest['review_correction_record_3']['after_glb_sha256'],
           'GLB differs from the third correction.')
    expect({d['id'] for d in manifest.get('known_deviations', [])} == DEVIATIONS, 'Unexpected known_deviations.')
    length = struct.unpack_from('<I', original, 12)[0]
    gltf = json.loads(original[20:20 + length])
    binary = bytearray(original[28 + length:])
    parts = {p['id']: p for p in manifest['parts']}
    meshes = {m['name']: m for m in gltf['meshes']}
    expect(set(parts) == set(meshes) and len(parts) == START_PARTS, 'Unexpected part set.')

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
        v = read(meshes[pid]['primitives'][0]['attributes']['POSITION']).astype(np.float64)
        return np.c_[v[:, 0], -v[:, 2], v[:, 1]]          # glTF (X, Z, -Y) -> native (X, Y, Z)

    def stored(pid):
        prim = meshes[pid]['primitives'][0]
        return trimesh.Trimesh(native(pid), read(prim['indices']).reshape(-1, 3).astype(np.int64), process=False)

    def to_gl(v):
        return np.c_[v[:, 0], v[:, 2], -v[:, 1]].astype('<f4')

    # ---- Starting state: the frames are the generator's X frames, re-graded rigidly in revision 1.3 -----------------
    for i, row, j in FRAMES:
        pid = f'frame_{i}_{row}_{j}'
        m = old_frame(i, row, j)
        v = np.asarray(m.vertices, float).copy()
        v[:, 2] += dz((v[:, 0].min() + v[:, 0].max()) / 2)
        expect(close(native(pid), v, 2e-5), f'{pid}: current mesh is not the generator X frame')
    # ---- S2 starting state: eight exact duplicate meshes --------------------------------------------------------
    for keep, dup in DUPLICATES:
        a, b = meshes[keep]['primitives'][0], meshes[dup]['primitives'][0]
        expect(np.array_equal(read(a['attributes']['POSITION']), read(b['attributes']['POSITION'])) and
               np.array_equal(read(a['indices']), read(b['indices'])), f'{dup} is not an exact copy of {keep}')

    # ---- S1: frames on their connection plates ---------------------------------------------------------------
    girders = [Girder(k, [(f'plate_{s}_{k}', stored(f'plate_{s}_{k}')) for s in range(4)]) for k in range(8)]
    rgba_cache, new_bounds, new_volume, frame_info = {}, {}, {}, {}
    for i, row, j in FRAMES:
        pid = f'frame_{i}_{row}_{j}'
        plates, bars, info = frame_geometry(i, row, j, girders)
        for p in plates:
            expect(p.is_watertight and p.is_winding_consistent and p.volume > 0, f'{pid}: connection plate')
        for b in bars:
            expect(b.is_watertight and b.is_winding_consistent and b.volume > 0, f'{pid}: diagonal')
        mesh = trimesh.util.concatenate(plates + bars)               # touching bodies, as the channel diaphragms
        ok, count = stored_closed(mesh)
        expect(ok and count == 4, f'{pid}: not four closed bodies as stored')
        prim = meshes[pid]['primitives'][0]
        rgba = read(prim['attributes']['COLOR_0'])[0]
        gl = to_gl(mesh.vertices)
        colour = append(np.tile(np.asarray(rgba, 'u1'), (len(gl), 1)), 'VEC4', 5121)
        gltf['accessors'][colour]['normalized'] = True
        meshes[pid]['primitives'][0] = dict(attributes={'POSITION': append(gl, 'VEC3', 5126), 'COLOR_0': colour},
                                            indices=append(mesh.faces.reshape(-1, 1).astype('<u4'), 'SCALAR', 5125),
                                            mode=4)
        new_bounds[pid] = mesh.bounds
        new_volume[pid] = float(sum(p.volume for p in plates + bars))
        info['plate_volume'] = float(plates[0].volume + plates[1].volume)
        info['plate_heights'] = [float(p.bounds[1, 2] - p.bounds[0, 2]) for p in plates]
        frame_info[pid] = info

    # ---- S2: remove the duplicate stiffener assemblies; rebuild the node list ----------------------------------------
    removed = sorted(dup for _, dup in DUPLICATES)
    keep = [m for m in gltf['meshes'] if m['name'] not in removed]
    gltf['meshes'] = keep
    world = dict(name='world', children=list(range(1, len(keep) + 1)))
    gltf['nodes'] = [world] + [dict(name=m['name'], mesh=k) for k, m in enumerate(keep)]
    gltf['scenes'] = [dict(nodes=[0])]
    gltf['scene'] = 0
    meshes = {m['name']: m for m in keep}

    # ---- manifest ---------------------------------------------------------------------------------------------
    manifest['parts'] = [p for p in manifest['parts'] if p['id'] not in removed]
    parts = {p['id']: p for p in manifest['parts']}
    expect(set(parts) == set(meshes) and len(parts) == START_PARTS - len(removed), 'part set after removal')
    for pid, info in frame_info.items():
        i, row, j = (int(s) for s in pid.split('_')[1:])
        p = parts[pid]
        p['bounds_m'] = np.round(new_bounds[pid], 6).tolist()
        p['volume_m3'] = round(new_volume[pid], 9)
        west_girder, east_girder = 8 - j, 7 - j
        common = ('Connection plates PL 1 in x 8 in on the web face of each girder, the full web height between the '
                  'flanges with 1 1/2 x 2 1/2 in clips at the web (sheets 25 and 33), bearing on the web and both flanges. '
                  'The two diagonals are the representative 100 x 12 mm flat bars (the section the FEM demonstration '
                  'assumes), one on each face of the plates as sheet 33 implies (1 in x 12 in filler between the crossing '
                  'diagonals), each ending 1 3/4 in from the web face (sheet 33 Typical Frame Bolted Connection Detail).')
        if (i, row) in DRAWN:
            span, bent = ('A', 2) if i == 0 else ('D', 4)
            new_girder, old_girder = (west_girder, east_girder) if i == 0 else (east_girder, west_girder)
            p['name'] = f'Span {span} | cross frame nearest Bent {bent}, bay {7 - j} (girders {7 - j}-{8 - j})'
            p['pdf_pages'] = [25, 27, 28, 33] if i == 0 else [26, 30, 31, 33]
            p['basis'] = (f'Dimensioned: sheet 33 Cross-Frame Detail - Span {span} (PL 1 x 8 in x 5 ft 6 in connection plates, '
                          f'work points); station 12 ft 0 in from the Bent {bent} bearing line at the girder {new_girder} '
                          f'bottom taper and 1 ft 6 in across the bent on girder {old_girder} '
                          f'(sheets {"25, 27-28" if i == 0 else "26, 30-31"})')
            p['note'] = (f'The drawn Span {span} cross frame nearest Bent {bent} (revision 1.4; it stood 0.8 m from the bent, '
                         'with one end inside the field-splice plates). ' + common +
                         ' Work points on the web centre lines: 1 3/4 in below the lower top flange and 10 1/4 in above the '
                         'higher bottom flange, the level frame of sheet 33 (3 1/2 / 1 3/4 in and 10 1/4 / 12 in between '
                         'girders 1 3/4 in apart). The model skew puts the existing-girder end 1.8 mm short of 1 ft 6 in. The '
                         'drawn L 3 1/2 x 3 1/2 x 3/8 angles, bottom strut, filler plate and bolts are not modelled. The FEM '
                         'demonstration analyses this id as an assumed diagonal pair at its own station (fem/minnich.json).')
            p['dimensions'] = rounded(station_new_girder_from_bearing_line_m=DRAWN_STATION,
                                      station_existing_girder_from_bearing_line_m=-K * (YS[j + 1] - YS[j]) - DRAWN_STATION,
                                      top_work_point_below_lower_top_flange_m=TOP_WP,
                                      bottom_work_point_above_higher_bottom_flange_m=BOTTOM_WP)
        else:
            p['pdf_pages'] = [20, 25, 33]
            p['basis'] = ('Representative X-frame topology of the retained main span; connection after the drawn typical '
                          'cross-frame connection (sheets 25, 33)')
            p['note'] = ('Existing main-span cross frame, retained (sheet 20). Generator station and work-point levels, 0.12 m '
                         'below the top and above the bottom of steel at mid-bay; revision 1.4 puts the work points on the '
                         'web centre lines so the diagonals reach the plates. ' + common + ' The existing frame members and '
                         'connections are on the original plans, which are not in this set; the drawn new cross-frame '
                         'connection stands in for them (known deviation existing-main-span-cross-frames). The FEM '
                         'demonstration analyses this id as an assumed diagonal pair (fem/minnich.json).')
            p['dimensions'] = {}
        p['dimensions'].update(rounded(bar_width_m=BAR_W, bar_thickness_m=BAR_T, bar_length_m=info['bar_length'],
                                       bar_end_from_web_face_m=BAR_END, connection_plate_thickness_m=CP_T,
                                       connection_plate_width_m=CP_W, connection_plate_clip_along_web_m=CLIP_V,
                                       connection_plate_clip_across_m=CLIP_H,
                                       connection_plate_height_west_m=info['plate_heights'][0],
                                       connection_plate_height_east_m=info['plate_heights'][1]))
        extras = meshes[pid]['extras']
        for key in ('name', 'note', 'dimensions', 'basis', 'pdf_pages'):
            extras[key] = p[key]

    for c in manifest['detail_coverage']:
        c['part_ids'] = [p for p in c['part_ids'] if p not in removed]
        if c['feature'] == 'Variable-depth steel and connections':
            c['detail'] += (' Revision 1.4: every X frame hangs on PL 1 x 8 in connection plates on the girder webs (sheets 25, '
                            '33) and its diagonals lap onto them; frame_0_1_* and frame_3_0_* are the drawn cross frames nearest '
                            'Bents 2 and 4 at the drawn stations (sheets 27-28, 30-31, 33); the main-span frames stay '
                            'representative. The duplicate Bent 3 stiffener assemblies stiffener_*_12 were removed.')
            c['sources'] = sorted(set(c['sources']) | {'Primary PDF p.20'}, key=lambda s: int(s.split('.')[-1]))
    main_span = [f'frame_{i}_{r}_{j}' for i, r, j in FRAMES if i in (1, 2)]
    manifest['known_deviations'].append(dict(
        id='existing-main-span-cross-frames', parts='frame_1_*_*, frame_2_*_* (72 ids)',
        source='sheet 20 (main-span steel retained), sheets 25 and 33 (new cross-frame connection, used as stand-in)',
        deviation='The cross frames of the retained main spans B and C are the generator\'s representative X frames: six rows '
                  'per span at even spacing from 0.8 m off the bents, two 100 x 12 mm flat diagonals each. They hang on 1 in '
                  'x 8 in connection plates of the drawn new cross-frame detail; the existing members, stations and '
                  'connections may differ.',
        reason='This set retains the main-span steel ("Remaining existing steel superstructure in the main spans to be cleaned '
               'and coated", sheet 20) without drawing its cross frames. They are on the original plans (bridge file '
               'I469-18-07027 NB & SB, sheet 19 general note), which are not in this set.'))

    gltf['buffers'][0]['byteLength'] = len(binary)
    while len(binary) % 4:
        binary.append(0)
    gltf['buffers'][0]['byteLength'] = len(binary)
    encoded = json.dumps(gltf, ensure_ascii=True, separators=(',', ':')).encode()
    encoded += b' ' * ((-len(encoded)) % 4)
    out = (struct.pack('<III', 0x46546c67, 2, 28 + len(encoded) + len(binary)) +
           struct.pack('<II', len(encoded), 0x4e4f534a) + encoded + struct.pack('<II', len(binary), 0x004e4942) + binary)

    # source_ledger.json lists the part ids per feature; drop the removed duplicates.
    ledger = json.loads(raw_ledger)
    ledger_change = []
    for check in ledger.get('verified_source_checks', []):
        ids = check.get('part_ids', [])
        gone = [p for p in ids if p in removed]
        if gone:
            check['part_ids'] = [p for p in ids if p not in removed]
            ledger_change.append(f'verified_source_checks "{check["feature"]}": removed {len(gone)} ids ({", ".join(gone)})')

    drawn_ids = sorted(f'frame_{i}_{r}_{j}' for i, r, j in FRAMES if (i, r) in DRAWN)
    manifest[TAG_KEY] = TAG
    manifest['revision'] = REVISION
    manifest['review_correction_record_3d'] = dict(
        review='3D review of the assembled model: findings S1 and S2 (structure)',
        source_pdf_pages=[20, 25, 26, 27, 28, 30, 31, 33],
        printed_sheets=[20, 25, 26, 27, 28, 30, 31, 33],
        findings={
            'S1': 'resolved: all 84 X frames hang on PL 1 x 8 in connection plates that bear on the web and both flanges '
                  '(sheets 25, 33); the diagonals lap 6 1/4 in onto the plates (sheet 33). frame_0_1_* and frame_3_0_* move to '
                  'the drawn cross-frame station 12 ft 0 in / 1 ft 6 in from Bents 2 and 4 (sheets 27-28, 30-31) with the '
                  'sheet 33 work points; the 72 main-span frames keep their stations (known deviation '
                  'existing-main-span-cross-frames).',
            'S2': 'resolved: stiffener_j_12 (j = 0..7) were exact copies of stiffener_j_2 at Bent 3 (generator station '
                  'sampled twice); removed.'},
        decisions=[
            'Connection plate 1 in thick: the Cross-Frame Details (sheet 33) and the girder elevations (sheets 27-28, 30-31: '
            '"1" x 8" Connection Plate (See Cross-Frame Detail)") govern over the generic "PL 1/2" x 8"" label of the '
            'Typical Frame Bolted Connection Detail, which also serves the 1/2 in diaphragm plates.',
            'Work points: sheet 33 dimensions 3 1/2 / 1 3/4 in below the top flanges and 10 1/4 / 12 in above the bottom '
            'flanges of two girders 1 3/4 in apart (crossfall), i.e. a level frame; applied as 1 3/4 in below the lower top '
            'flange and 10 1/4 in above the higher bottom flange in every bay, whichever girder is new.',
            'Drawn-frame station: the new-girder end is kept at the drawn 12 ft 0 in (the bottom taper, where its plate is '
            'the drawn "1" x 8" Plate (One Each Side)"); the model skew gives 13.494 ft of stagger over 9 ft against the '
            '13 ft 6 in of the elevations, so the existing-girder end is 1.8 mm short of 1 ft 6 in.',
            'Diagonal faces: sheet 33 does not show which diagonal is on which face of the plates; the diagonal rising to the '
            'east girder is on the +X face.',
            'Main-span frames (B, C): the drawn new cross-frame connection stands in for the undrawn existing one; their '
            'work points move from 0.24 m off the girder centre lines to the web centre lines (same levels), because an '
            'extension along the generator axis would run into the top flange before reaching the plate.'],
        changed_part_count=len(frame_info), changed_parts=sorted(frame_info), relocated_parts=drawn_ids,
        added_parts=[], removed_parts=removed, part_count_before=START_PARTS, part_count_after=len(parts),
        frame_volume_m3=dict(before_each=parts_volume_before(raw_manifest, 'frame_1_0_0'),
                             after_main_span_each=round(new_volume['frame_1_0_0'], 9),
                             connection_plates_each_frame=round(frame_info['frame_1_0_0']['plate_volume'], 9)),
        source_ledger_change=ledger_change,
        before_glb_sha256=before, after_glb_sha256=hashlib.sha256(out).hexdigest(),
        before_manifest_sha256=hashlib.sha256(raw_manifest).hexdigest(),
        before_source_ledger_sha256=hashlib.sha256(raw_ledger).hexdigest())

    backup.mkdir(parents=True, exist_ok=True)
    (backup / f'{BID}_before_3d_review.glb').write_bytes(original)
    (backup / f'{BID}_manifest_before_3d_review.json').write_bytes(raw_manifest)
    (backup / f'{BID}_source_ledger_before_3d_review.json').write_bytes(raw_ledger)
    path.write_bytes(out)
    mp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if ledger_change:                                       # the ledger's own format: indent 2, CRLF, no final newline
        text = json.dumps(ledger, ensure_ascii=False, indent=2)
        if b'\r\n' in raw_ledger:
            text = text.replace('\n', '\r\n')
        if raw_ledger.endswith(b'\n'):
            text += '\r\n' if b'\r\n' in raw_ledger else '\n'
        lp.write_bytes(text.encode('utf-8'))
    print(json.dumps({k: (v if not isinstance(v, list) or len(v) < 20 else f'{len(v)} ids')
                      for k, v in manifest['review_correction_record_3d'].items() if k != 'decisions'}, indent=1))


def parts_volume_before(raw_manifest, pid):
    return next(p['volume_m3'] for p in json.loads(raw_manifest)['parts'] if p['id'] == pid)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--base', type=Path, default=ROOT / 'data/bridges' / BID, help='bridge folder (default: the repository)')
    parser.add_argument('--backup', type=Path, default=ROOT / 'data/fem_research', help='backup folder')
    args = parser.parse_args()
    correct(args.base, args.backup)

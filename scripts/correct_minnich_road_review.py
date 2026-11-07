"""One-time, drawing-confirmed corrections from the external model review of Minnich Road, preserving unrelated GLB
buffers.

    python scripts/correct_minnich_road_review.py

INDOT B-44533 (July 31 2026); in this set the printed sheet number equals the PDF page number.

F1, sheets 44-45 (Floor Details): both end bents get a cast-in-place concrete end diaphragm that encases the girder ends.
Section X-X: 2 ft 0 in thick measured perpendicular to the bent, its back face 1 ft 1 3/4 in behind the centre line of
bearing (3 in joint to the mudwall), its top at the deck (8 in deck + 2 in fillet) and its bottom at the top of the
girder bottom flanges. Plan and front elevation: 105 ft 10 5/8 in along the bearing line, i.e. from the centre line of
Girder 1 to that of Girder 8 (6 x 16 ft 2 5/8 in + 8 ft 6 3/4 in). The front-elevation levels agree: El. 820.06 top of
deck / 816.31 bottom at Girder 8, Bent 1 = 8 + 2 + 36 - 1 = 45 in; Bent 5: 820.15 / 816.55 = 8 + 2 + 34 1/4 - 1 1/8 in.
The model had no diaphragm. Two parts are added (end_diaphragm_0, end_diaphragm_4) on the model's own deck soffit and
girder lines; girder ends and bearing stiffeners are embedded, not subtracted.

F3, sheets 27-28 and 30-31 (girder elevations): every new end-span girder ends 7 1/2 in beyond the end-bearing centre
line (flange plates 57 ft 0 1/2 in = 7 1/2 in + 56 ft 5 in in Span A, 47 ft 0 1/2 in = 7 1/2 in + 46 ft 5 in in Span D).
The model stopped all sixteen girders at the bearing centre line. Each Span A / Span D girder gets one extra section
0.1905 m beyond the bearing (constant end section, model grade), and its haunch follows.

F6, sheets 30-31: in Span D the bottom flange of the shallow segment (39 ft 0 1/2 in from the end of the taper to the
girder end) is PL 22 x 1 1/8 in on a PL 32 1/8 x 1/2 in web; the taper keeps PL 18 x 1 in. The model used 18 x 1 in
throughout, with a 34 1/4 in total depth. The underside (and the Bent 5 bearing contact) is kept, the flange is widened
to 22 in and its top raised 1/8 in (web 32 1/8 in); the width and thickness change is a step at the end of the taper.

F5, sheet 49 (east) and sheet 52 (west), Section C-C, Type FC railing: 1 ft 4 in base, 2 ft 9 in high, vertical back
face, 9 in top; traffic face 3 in vertical toe, 7 in slope to a break 11 in from the back face, then 1 ft 11 in to the
top. The model went straight up 10 in at the full 16 in width. The eight rail panels are re-swept with the six-point
section on the same stations; back face, base and top are unchanged.

F4, sheet 25 (framing plan, Span A) with sheet 19: Girder No. 1 is on the top edge of the plan, the edge where every
bent line has its lowest station; in the model that is +Y (east). The generator numbered girders from -Y, so every
label that carries a girder or bay number is reversed: part index j (0..7, Y = -8.9535 .. +8.9535) is plan Girder 8-j,
and frame bay j+1 is plan bay 7-j. Only names change; part ids are kept.

Not changed, recorded in known_deviations: F2, the twelve end-bent X frames (frame_0_0_*, frame_3_1_*) have no
counterpart on sheets 25-26, but fem/minnich.json lists them as analysed components and deleting part ids is outside a
correction; F7, the grade puts the PVI at X = 0 instead of Bent 3 (sheet 16: PVI 15+26.77, X = +1.524 m), a 21 mm tilt
at the end bearings that only a regeneration of every mesh can remove; and the end-bent mudwall faces, which sit 4 in
closer to the bearing than Section X-X.

The script rebuilds the original sections with the generator's formulas (scripts/build_indiana_batch2.py, minnich())
and refuses to run unless they reproduce the current GLB vertices. Requires numpy, trimesh and manifold3d.
"""
import hashlib
import json
import re
import struct
from pathlib import Path

import manifold3d
import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'data/bridges/minnich-road'
TAG = 'review-end-diaphragms-girder-ends-flange-rail-face-girder-numbers'
FT, IN = .3048, .0254

# Generator geometry (scripts/build_indiana_batch2.py, minnich()).
LENGTH, WIDTH = (414 + 11.5 / 12) * FT, 63 * FT
SKEW = 56 + 17 / 60 + 55 / 3600
K, C = -np.tan(np.radians(SKEW)), np.cos(np.radians(SKEW))
SPANS = np.array([65 + 5 / 12, 145, 145, 55 + 5 / 12]) * FT
BS = np.r_[0, np.cumsum(SPANS)] - SPANS.sum() / 2
YS = np.array([-29.375, -20.375, -11.375, -2.375, 2.375, 11.375, 20.375, 29.375]) * FT
SLAB, CLEAR = 8 * IN, .08
FLANGE_W, FLANGE_T, WEB_T = .4572, .0254, .0127

END_PROJECTION = 7.5 * IN                  # girder end beyond the end-bearing centre line, sheets 27-28, 30-31
SHALLOW_START = BS[3] + 17 * FT            # end of the Span D bottom taper (3 ft + 5 ft from the splice), sheet 30
SPAN_D_FLANGE = (22 * IN, 1.125 * IN)      # PL 22 x 1 1/8, sheets 30-31
DIAPHRAGM_BACK, DIAPHRAGM_FRONT = 13.75 * IN, 10.25 * IN   # normal to the bent, from the bearing line, sheet 45
RAIL_OLD = [(0, 0), (16 * IN, 0), (16 * IN, .254), (9 * IN, 33 * IN), (0, 33 * IN)]
RAIL_NEW = [(0, 0), (16 * IN, 0), (16 * IN, 3 * IN), (11 * IN, 10 * IN), (9 * IN, 33 * IN), (0, 33 * IN)]
CONCRETE = '#d1d5d0'                       # deck colour: the diaphragm is poured with the deck


def grade(x):
    return 10.45 - .00005 * np.asarray(x) - .0625 * np.asarray(x) ** 2 / (2 * 940 * FT)


def surface(x, y):
    return grade(x) - .0156 * np.abs(y)


def sx(u, y):
    return u + K * y


def depth(u):
    if u < BS[1]:
        return np.interp(u, [BS[0], BS[0] + 48.4167 * FT, BS[0] + 53.4167 * FT, BS[1]], [36 * IN, 36 * IN, 68 * IN, 68 * IN])
    if u > BS[3]:
        return np.interp(u, [BS[3], BS[3] + 12 * FT, BS[3] + 17 * FT, BS[4]], [68 * IN, 68 * IN, 34.25 * IN, 34.25 * IN])
    return 68 * IN


def section(d, bottom_w=FLANGE_W, bottom_t=FLANGE_T):
    """Plate girder outline (v, height above underside) in the generator's iform vertex order."""
    b, t, w, tw = bottom_w / 2, bottom_t, FLANGE_W / 2, WEB_T / 2
    return [(-b, 0), (b, 0), (b, t), (tw, t), (tw, d - FLANGE_T), (w, d - FLANGE_T),
            (w, d), (-w, d), (-w, d - FLANGE_T), (-tw, d - FLANGE_T), (-tw, t), (-b, t)]


def loft(rings, axes=(1, 2)):
    """Closed solid through equal-size planar rings (the generator's sweep topology); axes span the ring planes."""
    rings = np.asarray(rings, float)
    count, n = rings.shape[:2]

    def cap(ring):
        pts = ring[:, list(axes)]
        ccw = (np.roll(pts[:, 0], -1) - pts[:, 0]) @ (np.roll(pts[:, 1], -1) + pts[:, 1]) < 0
        tri = manifold3d.triangulate([pts if ccw else pts[::-1]]).astype(np.int64)
        return tri if ccw else (n - 1 - tri)[:, ::-1]      # triangles follow the ring's own vertex order

    faces = []
    for k in range(count - 1):
        for j in range(n):
            a, b = k * n + j, k * n + (j + 1) % n
            faces += [(a, b, b + n), (a, b + n, a + n)]
    faces += [tuple(q[::-1]) for q in cap(rings[0])] + [tuple(q + (count - 1) * n) for q in cap(rings[-1])]
    mesh = trimesh.Trimesh(rings.reshape(-1, 3), np.array(faces), process=False)
    if mesh.volume < 0:
        mesh.invert()
    return mesh


def plate_stations(i):
    a, b = BS[i], BS[i + 1]
    breaks = [BS[0] + 48.4167 * FT, BS[0] + 53.4167 * FT, BS[3] + 12 * FT, BS[3] + 17 * FT]
    return np.unique(np.r_[np.linspace(a, b, max(3, int((b - a) / .5))), [t for t in breaks if a < t < b]])


def plate_ring(u, y, shallow_flange=False):
    d = depth(u)
    pts = section(d, *SPAN_D_FLANGE) if shallow_flange else section(d)
    x = sx(u, y)
    bottom = surface(x, y) - SLAB - CLEAR - d
    return [(x, y + v, bottom + h) for v, h in pts]


def haunch_stations(i):
    a, b = BS[i], BS[i + 1]
    return np.linspace(a, b, max(3, int((b - a) / .7)))


def haunch_ring(u, y):
    x = sx(u, y)
    return [(x, y + v, (1 - t) * (surface(x, y) - SLAB - CLEAR) + t * (surface(x, y + v) - SLAB))
            for v, t in [(-FLANGE_W / 2, 0), (FLANGE_W / 2, 0), (FLANGE_W / 2, 1), (-FLANGE_W / 2, 1)]]


def rail_mesh(side, i, profile):
    edges = np.linspace(-LENGTH / 2, LENGTH / 2, 5)
    a, b = edges[i], edges[i + 1]
    edge = side * (WIDTH / 2 - .05)
    rings = []
    for u in np.linspace(a, b, max(2, int((b - a) / .6) + 1)):
        ring = []
        for v, z in profile:
            y = edge - side * v
            ring.append((sx(u, y), y, surface(sx(u, y), y) + z))
        rings.append(ring)
    return loft(rings)


def diaphragm_mesh(bent):
    """Concrete end diaphragm between the Girder 1 and Girder 8 centre lines, swept across the girder lines."""
    u_brg, sign = BS[bent], (-1 if bent == 0 else 1)          # sign points from the span towards the mudwall
    q_back, q_front = u_brg + sign * DIAPHRAGM_BACK / C, u_brg - sign * DIAPHRAGM_FRONT / C
    d, tf = (36 * IN, FLANGE_T) if bent == 0 else (34.25 * IN, SPAN_D_FLANGE[1])
    rings = []
    for y in sorted(set(YS.tolist()) | {0.0}):
        ring = []
        for q, top in [(q_back, 0), (q_front, 0), (q_front, 1), (q_back, 1)]:
            x = sx(q, y)
            soffit = surface(x, y) - SLAB
            ring.append((x, y, soffit if top else soffit - CLEAR - d + tf))
        rings.append(ring)
    return loft(rings, axes=(0, 2)), dict(q_back=q_back, q_front=q_front, depth=d, tf=tf)


def union(a, b):
    def to_manifold(m):
        return manifold3d.Manifold(manifold3d.Mesh(vert_properties=np.asarray(m.vertices, np.float32),
                                                   tri_verts=np.asarray(m.faces, np.uint32)))
    result = to_manifold(a) + to_manifold(b)
    if len(result.decompose()) != 1:
        raise ValueError('flange step union did not give one solid')
    out = result.to_mesh()
    return trimesh.Trimesh(np.asarray(out.vert_properties[:, :3], np.float64), np.asarray(out.tri_verts), process=False)


def relabel(pid, name):
    """Plan girder numbers (sheet 25): part index j is Girder 8-j; frame bay j+1 is plan bay 7-j."""
    rules = [
        (r'plate_(\d)_(\d)', lambda i, j: (f'Span {chr(65 + i)} | plate girder {j + 1}', f'Span {chr(65 + i)} | plate girder {8 - j}')),
        (r'haunch_(\d)_(\d)', lambda i, j: (f'haunch {i} {j}', f'Span {chr(65 + i)} | haunch, girder {8 - j}')),
        (r'Bent_(\d)_bearing_(\d)', lambda b, n: (f'Bent {b} bearing {n}', f'Bent {b} | bearing, girder {9 - n}')),
        (r'ped_(\d)_(\d)', lambda b, j: (f'Bent {b + 1} | pedestal {j + 1}', f'Bent {b + 1} | pedestal, girder {8 - j}')),
        (r'splice_(\d)_(\d)', lambda j, s: (f'splice {j} {s}', f'Girder {8 - j} | field splice, Span {"AD"[s]}')),
        (r'splice_(\d)_(\d)_bolts', lambda j, s: (f'splice {j} {s} web bolts', f'Girder {8 - j} | field splice web bolts, Span {"AD"[s]}')),
        (r'stiffener_(\d)_(\d+)', lambda j, q: (f'Girder {j + 1} | transverse stiffener pair {q + 1}', f'Girder {8 - j} | transverse stiffener pair {q + 1}')),
        (r'frame_(\d)_(\d)_(\d)', lambda i, r, j: (f'Span {chr(65 + i)} | cross frame row {r + 1}, bay {j + 1}',
                                                   f'Span {chr(65 + i)} | cross frame row {r + 1}, bay {7 - j} (girders {7 - j}-{8 - j})')),
    ]
    for pattern, rule in rules:
        m = re.fullmatch(pattern, pid)
        if m:
            old, new = rule(*map(int, m.groups()))
            if name != old:
                raise ValueError(f'{pid}: unexpected original name {name!r}')
            return new
    return None


def correct():
    mp = BASE / 'model_manifest.json'
    manifest = json.loads(mp.read_text(encoding='utf-8'))
    if manifest.get('drawing_review_correction') == TAG:
        print('Already corrected.')
        return
    if 'revision' in manifest or any(p['layer'] == 'diaphragms' for p in manifest['parts']):
        raise ValueError('Manifest is not the original generator revision.')
    path = BASE / 'model.glb'
    original = path.read_bytes()
    length = struct.unpack_from('<I', original, 12)[0]
    gltf = json.loads(original[20:20 + length])
    binary = bytearray(original[28 + length:])
    before = hashlib.sha256(original).hexdigest()
    parts = {p['id']: p for p in manifest['parts']}
    meshes = {m['name']: m for m in gltf['meshes']}
    if set(parts) != set(meshes) or len(parts) != 474:
        raise ValueError('Unexpected part set.')

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

    def expect(pid, rings):
        v, r = native(pid), np.asarray(rings, float).reshape(-1, 3)
        if v.shape != r.shape or np.abs(v - r).max() > 1e-4:
            raise ValueError(f'{pid}: current mesh does not match the generator geometry this correction assumes')

    def primitive(mesh, rgba):
        if not mesh.is_watertight or mesh.volume <= 0:
            raise ValueError('invalid corrected solid')
        gl = np.c_[mesh.vertices[:, 0], mesh.vertices[:, 2], -mesh.vertices[:, 1]].astype('<f4')
        attrs = {'POSITION': append(gl, 'VEC3', 5126),
                 'COLOR_0': append(np.tile(np.asarray(rgba, 'u1'), (len(gl), 1)), 'VEC4', 5121)}
        gltf['accessors'][attrs['COLOR_0']]['normalized'] = True
        return dict(attributes=attrs, indices=append(mesh.faces.reshape(-1, 1).astype('<u4'), 'SCALAR', 5125), mode=4)

    def replace(pid, mesh, note, **dims):
        prim = meshes[pid]['primitives'][0]
        color = read(prim['attributes']['COLOR_0'])[0]
        meshes[pid]['primitives'][0] = primitive(mesh, color)
        p = parts[pid]
        p['bounds_m'] = np.round(mesh.bounds, 6).tolist()
        if 'volume_m3' in p:
            p['volume_m3'] = round(float(mesh.volume), 9)
        p['dimensions'].update({k: round(float(v), 6) for k, v in dims.items()})
        p['note'] = (p.get('note', '') + ' ' + note).strip()
        changes.append(pid)

    changes, added, renamed = [], [], {}

    # F3 + F6: end-span girders and their haunches.
    for i in (0, 3):
        for j, y in enumerate(YS):
            xs = plate_stations(i)
            expect(f'plate_{i}_{j}', [plate_ring(u, y) for u in xs])
            expect(f'haunch_{i}_{j}', [haunch_ring(u, y) for u in haunch_stations(i)])
            if i == 0:
                girder = loft([plate_ring(u, y) for u in np.r_[BS[0] - END_PROJECTION, xs]])
                note = 'North end extended 7 1/2 in beyond the Bent 1 bearing centre line, sheets 27-28.'
                dims = dict(end_projection_beyond_bearing_m=END_PROJECTION)
            else:
                xs = np.r_[xs, BS[4] + END_PROJECTION]
                taper = loft([plate_ring(u, y) for u in xs[xs <= SHALLOW_START + 1e-9]])
                shallow = loft([plate_ring(u, y, True) for u in xs[xs >= SHALLOW_START - 1e-9]])
                girder = union(taper, shallow)
                note = ('South end extended 7 1/2 in beyond the Bent 5 bearing centre line; shallow-segment bottom flange '
                        'PL 22 x 1 1/8 in over 39 ft 0 1/2 in on a 32 1/8 in web, underside kept, sheets 30-31.')
                dims = dict(end_projection_beyond_bearing_m=END_PROJECTION, shallow_bottom_flange_width_m=SPAN_D_FLANGE[0],
                            shallow_bottom_flange_thickness_m=SPAN_D_FLANGE[1], shallow_web_depth_m=round(32.125 * IN, 6),
                            shallow_bottom_flange_length_m=round(BS[4] + END_PROJECTION - SHALLOW_START, 6))
            replace(f'plate_{i}_{j}', girder, note, **dims)
            hs = haunch_stations(i)
            hs = np.r_[BS[0] - END_PROJECTION, hs] if i == 0 else np.r_[hs, BS[4] + END_PROJECTION]
            replace(f'haunch_{i}_{j}', loft([haunch_ring(u, y) for u in hs]),
                    'Extended with the girder end (7 1/2 in beyond the end bearing).')

    # F5: Type FC rail traffic face.
    for side in (-1, 1):
        for i in range(4):
            pid = f'rail_{side}_{i}'
            expect(pid, rail_mesh(side, i, RAIL_OLD).vertices)
            replace(pid, rail_mesh(side, i, RAIL_NEW),
                    'Traffic face per Section C-C, sheets 49 and 52: 3 in toe, break 11 in from the back face at 10 in, 9 in top.',
                    toe_height_m=3 * IN, face_break_height_m=10 * IN, face_break_width_m=11 * IN, top_width_m=9 * IN)

    # F1: concrete end diaphragms (new parts).
    world = gltf['nodes'][gltf['scenes'][gltf.get('scene', 0)]['nodes'][0]]
    for bent in (0, 4):
        pid = f'end_diaphragm_{bent}'
        mesh, k = diaphragm_mesh(bent)
        p = dict(id=pid, name=f'Bent {bent + 1} | concrete end diaphragm', layer='diaphragms', color=CONCRETE,
                 pdf_pages=[44, 45],
                 basis='Dimensioned: sheets 44-45, 2 ft normal to the bent, back face 1 ft 1 3/4 in behind the bearing '
                       'line, Girder 1 to Girder 8 centre lines (105 ft 10 5/8 in along the bearing line)',
                 note='Poured with the deck and encasing the girder ends. Top on the modelled deck soffit, bottom at the top '
                      'of the girder bottom flanges (Section X-X); the steel inside is embedded, not cut out. Construction '
                      'joint, chamfers, shear studs and reinforcement are not modelled.',
                 dimensions=dict(thickness_normal_to_bent_m=round(24 * IN, 6), back_face_behind_bearing_line_m=DIAPHRAGM_BACK,
                                 length_along_bearing_line_m=round(2 * YS[-1] / C, 6),
                                 depth_below_deck_soffit_m=round(CLEAR + k['depth'] - k['tf'], 6)),
                 bounds_m=np.round(mesh.bounds, 6).tolist(), volume_m3=round(float(mesh.volume), 9))
        r, g, b = (int(CONCRETE[n:n + 2], 16) for n in (1, 3, 5))
        gltf['meshes'].append(dict(name=pid, extras=dict(processed=True, **{x: p[x] for x in (
            'id', 'name', 'layer', 'color', 'pdf_pages', 'basis', 'note', 'dimensions')}),
            primitives=[primitive(mesh, (r, g, b, 255))]))
        gltf['nodes'].append(dict(name=pid, mesh=len(gltf['meshes']) - 1))
        world['children'].append(len(gltf['nodes']) - 1)
        manifest['parts'].append(p)
        parts[pid] = p
        added.append(pid)
        print(f'{pid}: {mesh.volume:.3f} m3, q {k["q_back"]:.4f} .. {k["q_front"]:.4f}')

    # F4: plan girder numbers in labels only.
    for pid, p in parts.items():
        new = relabel(pid, p['name'])
        if new:
            renamed[pid] = new
            p['name'] = new
    if len(renamed) != 427:
        raise ValueError(f'expected 427 relabelled parts, got {len(renamed)}')

    for pid in set(changes) | set(renamed):
        extras = meshes[pid]['extras']
        for key in ('name', 'note', 'dimensions', 'bounds_m', 'volume_m3'):
            if key in extras or key in ('name', 'note', 'dimensions'):
                extras[key] = parts[pid][key]

    gltf['buffers'][0]['byteLength'] = len(binary)
    while len(binary) % 4:
        binary.append(0)
    encoded = json.dumps(gltf, ensure_ascii=True, separators=(',', ':')).encode()
    encoded += b' ' * ((-len(encoded)) % 4)
    out = (struct.pack('<III', 0x46546c67, 2, 28 + len(encoded) + len(binary)) +
           struct.pack('<II', len(encoded), 0x4e4f534a) + encoded + struct.pack('<II', len(binary), 0x004e4942) + binary)
    backup = ROOT / 'data/fem_research'
    backup.mkdir(exist_ok=True)
    (backup / 'minnich-road_before_review_correction.glb').write_bytes(original)
    (backup / 'minnich-road_manifest_before_review_correction.json').write_bytes(mp.read_bytes())
    path.write_bytes(out)

    layers = manifest['layers']
    order = ['deck', 'girders', 'haunches', 'steel', 'diaphragms']
    manifest['layers'] = {**{k: layers[k] for k in order if k in layers}, 'diaphragms': 'Diaphragms',
                          **{k: v for k, v in layers.items() if k not in order}}
    manifest['detail_coverage'].insert(2, dict(
        feature='Concrete end diaphragms', status='modeled_with_simplifications',
        detail='Cast-in-place end diaphragms at Bents 1 and 5, 2 ft normal to the bent, Girder 1 to Girder 8, encasing '
               'the girder ends. Construction joint, chamfers, shear studs and reinforcement are not modelled.',
        sources=['Primary PDF p.44', 'Primary PDF p.45'], part_ids=added))
    manifest['drawing_review_correction'] = TAG
    manifest['revision'] = '1.1-drawing-review'
    manifest['drawing_review_correction_record'] = dict(
        source_pdf_pages=[16, 19, 25, 27, 28, 30, 31, 44, 45, 49, 52],
        printed_sheets=[16, 19, 25, 27, 28, 30, 31, 44, 45, 49, 52],
        findings={
            'F1': 'added end_diaphragm_0 / end_diaphragm_4 (sheets 44-45)',
            'F3': 'sixteen end-span girders extended 0.1905 m beyond the end-bearing centre line, haunches follow (sheets 27-28, 30-31)',
            'F4': 'labels use plan girder numbers: part index j is Girder 8-j, frame bay j+1 is bay 7-j (sheet 25); ids unchanged',
            'F5': 'Type FC rail traffic face, six-point Section C-C (sheets 49, 52)',
            'F6': 'Span D shallow-segment bottom flange 22 x 1 1/8 in, underside kept (sheets 30-31)',
            'F2': 'not changed: see known_deviations end-bent-x-frames',
            'F7': 'not changed: see known_deviations vertical-curve-pvi'},
        changed_parts=changes, added_parts=added, relabelled_part_count=len(renamed),
        before_glb_sha256=before, after_glb_sha256=hashlib.sha256(out).hexdigest())
    deviations = [d for d in manifest.get('known_deviations', [])
                  if d.get('id') not in ('end-bent-x-frames', 'vertical-curve-pvi', 'end-bent-mudwall-face')]
    deviations += [
        dict(id='end-bent-x-frames', parts='frame_0_0_0-2, frame_0_0_4-6, frame_3_1_0-2, frame_3_1_4-6',
             source='sheets 25-26 and 44 (PDF 25-26, 44)',
             deviation='Twelve representative X frames at the end bents are square to the girders and lie 1.05 m beyond the '
                       '(extended) end of one of their two girders, so each meets one girder only, and they pass through the '
                       'concrete end diaphragm; the framing plans show no steel frame there, the girder ends being encased in '
                       'the end diaphragm.',
             reason='The part ids are analysed components of the Minnich FEM demonstration (fem/minnich.json); remove them '
                    'together with a reconciled ledger.'),
        dict(id='vertical-curve-pvi', parts='all graded parts', source='sheet 16 (PVI 15+26.77, El. 828.77, 940 ft VC); '
             'sheet 19 bent elevations',
             deviation='The grade function puts the PVI at X = 0 (Sta. 15+21.77) instead of Bent 3 (X = +1.524 m): relative '
                       'elevations tilt by up to 21 mm at the end bearings and 26 mm at the deck ends.',
             reason='Every part is graded from this function, so the fix is a regeneration (grade evaluated at X - 1.524 m), '
                    'not a correction; the model has no elevation datum.'),
        dict(id='end-bent-mudwall-face', parts='mudwall_0_0, mudwall_0_1, mudwall_4_0, mudwall_4_1',
             source='sheet 45 Section X-X (PDF 45)',
             deviation='The span face of the mudwall is 0.319 m normal to the bent from the bearing line; Section X-X gives '
                       '1 ft 1 3/4 in + 3 in joint = 0.425 m, so the mudwall overlaps the deck end and the end diaphragm '
                       'by 30 mm.',
             reason='Outside the reviewed findings; left for a separate correction.')]
    manifest['known_deviations'] = deviations
    mp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in manifest['drawing_review_correction_record'].items() if k != 'changed_parts'}))


if __name__ == '__main__':
    correct()

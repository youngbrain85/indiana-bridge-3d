"""Second drawing-confirmed correction of US 421 over South Fork Wildcat Creek (us421-wildcat). Runs after
scripts/correct_us421_wildcat_review.py and preserves unrelated GLB buffers.

    python scripts/correct_us421_wildcat_review_2.py

Source: drawings.pdf (INDOT 2020 rehabilitation plans, 30 sheets); printed sheet numbers equal PDF page numbers.
Native axes: X = station from Sta. 42+54.00, Y = transverse (+Y = left of increasing station = southwest = X-truss
and Beam No. 1 side, sheets 5, 16, 20), Z = elevation - 778 ft.

1. Pavement ledges and approach seats (sheet 24 Sections B-B and C-C; sheets 10 and 14 Sections A-A and B-B). The
   6 in pavement ledge projects from the back face of the end-bent diaphragm toward the approach, 1 ft 0 in deep, its
   top 1 ft 2 in below the approach/deck top. The reinforced concrete bridge approach is 12 in thick (sheet 28 bill
   of materials, "R.C. Bridge Approach, 12 in") and is thickened to 1 ft 2 in where it bears on the ledge: in all
   three sections the thickened bottom runs 1 ft 6 in behind the ledge and rises to the 12 in bottom over a 2 in x
   2 in taper (both scaled from the 3/4 in = 1 ft 0 in sections). The model had a 4 in deep block inside the
   diaphragm (its back 6 in), which the first correction had cut out of the diaphragm, and a 12 in slab with no
   seat. The ledges are rebuilt outside the diaphragm over their existing length (28 ft 0 in, |Y| <= 14 ft), parallel
   to the approach crown and grade; the diaphragm notch is filled; the approaches get the seat over the ledge length.
2. Box-beam top corners (sheet 21, "Typical section thru box beam" and "... thru end of box beam"; sheet 20 beam
   fillet detail). The 1 in chamfers are at the two bottom corners only; the top corners are square and the fillet
   sits on the full 4 ft top. The model chamfered all four corners, leaving 1 in triangular voids under the fillets
   and in the diaphragm and edge-beam pockets. The eight beams get square top corners; their voids, camber, length
   and bottom chamfers are unchanged.

Part ids are unchanged; no part is added or removed. Requires numpy, trimesh and manifold3d.
"""
import hashlib
import json
import struct
from pathlib import Path

import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'data/bridges/us421-wildcat'
FT = 0.3048
IN = FT / 12
TAG = 'ledge-seat-square-beam-tops'
PREV_TAG = 'edgebeam-diaphragm-riser-fc-drain-approach-names'
REVISION = '1.2-drawing-review-2'

LEDGE_PROJECTION = 6 * IN        # "6 in Pvm't. Ledge" (sheets 10, 14, 24)
LEDGE_DEPTH = 12 * IN            # "1'-0"" (sheet 24 B-B, C-C; 54 pt at 3/4 in = 1 ft on sheets 10, 14)
SEAT_DEPTH = 14 * IN             # "1'-2"" approach top to ledge top (sheets 10, 14, 24)
APPROACH_DEPTH = 12 * IN         # sheet 28 bill of materials
SEAT_LENGTH = 24 * IN            # 6 in on the ledge + 1 ft 6 in behind it (scaled, sheets 10, 14, 24)
SEAT_TAPER = 2 * IN              # 2 in x 2 in taper back to the 12 in bottom (scaled, sheets 10, 14, 24)
LEDGE_HALF = 14 * FT             # existing ledge length 28 ft 0 in (pavement width, sheet 28)
EPS = 0.5 * IN                   # expanded polystyrene under the diaphragm (sheet 24 Section C-C)
BEAM_HALF, CHAMFER, BEAM_DEPTH = 24 * IN, 1 * IN, 17 * IN    # CB 17 x 48 (sheet 21)


def to_native(v):
    return np.column_stack([v[:, 0], -v[:, 2], v[:, 1]])


def to_glb(v):
    return np.column_stack([v[:, 0], v[:, 2], -v[:, 1]])


def box(x0, x1, y0, y1, z0, z1):
    b = trimesh.creation.box(extents=[x1 - x0, y1 - y0, z1 - z0])
    b.apply_translation([(x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2])
    return b


def oriented(mesh):
    if mesh.volume < 0:
        mesh.invert()
    return mesh


def grid_solid(xs, ys, top, bottom):
    """Watertight solid between two height fields on an xs x ys grid (top/bottom: f(x, y) -> z)."""
    nx, ny = len(xs), len(ys)
    pts = [(x, y, f(x, y)) for f in (top, bottom) for x in xs for y in ys]
    t = lambda i, j: i * ny + j
    b = lambda i, j: nx * ny + i * ny + j
    faces = []
    for i in range(nx - 1):
        for j in range(ny - 1):
            faces += [(t(i, j), t(i + 1, j), t(i + 1, j + 1)), (t(i, j), t(i + 1, j + 1), t(i, j + 1)),
                      (b(i, j), b(i + 1, j + 1), b(i + 1, j)), (b(i, j), b(i, j + 1), b(i + 1, j + 1))]
    rim = ([(i, 0) for i in range(nx)] + [(nx - 1, j) for j in range(1, ny)] +
           [(i, ny - 1) for i in range(nx - 2, -1, -1)] + [(0, j) for j in range(ny - 2, 0, -1)])
    for k in range(len(rim)):
        p, q = rim[k], rim[(k + 1) % len(rim)]
        faces += [(t(*p), b(*q), t(*q)), (t(*p), b(*p), b(*q))]
    solid = oriented(trimesh.Trimesh(np.array(pts, float), np.array(faces), process=False))
    if not solid.is_watertight:
        raise ValueError('grid solid not watertight')
    return solid


def loft(sections, closed_caps=True):
    """Watertight loft through equal-length rings of 3-D points (convex rings; caps fanned from ring vertex 0)."""
    n = len(sections[0])
    pts = np.array([p for ring in sections for p in ring], float)
    faces = []
    for i in range(len(sections) - 1):
        for j in range(n):
            a, b2 = i * n + j, i * n + (j + 1) % n
            faces += [(a, b2, b2 + n), (a, b2 + n, a + n)]
    last = (len(sections) - 1) * n
    for k in range(1, n - 1):
        faces += [(0, k + 1, k), (last, last + k, last + k + 1)]
    solid = oriented(trimesh.Trimesh(pts, np.array(faces), process=False))
    if not solid.is_watertight or not solid.is_winding_consistent:
        raise ValueError('loft not watertight')
    return solid


def shells(mesh):
    """Face index arrays of the face-connected shells (union-find; scipy is not required)."""
    parent = list(range(len(mesh.vertices)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    for a, b, c in mesh.faces:
        ra = find(a)
        parent[find(b)] = ra
        parent[find(c)] = ra
    roots = np.array([find(f[0]) for f in mesh.faces])
    return [np.where(roots == r)[0] for r in np.unique(roots)]


def submesh(mesh, faces):
    used, inverse = np.unique(mesh.faces[faces], return_inverse=True)
    return trimesh.Trimesh(mesh.vertices[used], inverse.reshape(-1, 3), process=False)


def vertical_hits(mesh, x, y):
    """Z of every crossing of the vertical line through (x, y) with the mesh surface."""
    tri = mesh.vertices[mesh.faces]
    a, b, c = tri[:, 0, :2], tri[:, 1, :2], tri[:, 2, :2]
    v0, v1, v2 = b - a, c - a, np.array([x, y]) - a
    den = v0[:, 0] * v1[:, 1] - v1[:, 0] * v0[:, 1]
    ok = np.abs(den) > 1e-14
    den = np.where(ok, den, 1.0)
    u = (v2[:, 0] * v1[:, 1] - v1[:, 0] * v2[:, 1]) / den
    w = (v0[:, 0] * v2[:, 1] - v2[:, 0] * v0[:, 1]) / den
    hit = ok & (u >= -1e-9) & (w >= -1e-9) & (u + w <= 1 + 1e-9)
    t = tri[hit]
    return np.sort(t[:, 0, 2] + u[hit] * (t[:, 1, 2] - t[:, 0, 2]) + w[hit] * (t[:, 2, 2] - t[:, 0, 2]))


def overlap(a, b):
    if np.any(a.bounds[0] > b.bounds[1] + 1e-6) or np.any(b.bounds[0] > a.bounds[1] + 1e-6):
        return 0.0
    i = trimesh.boolean.intersection([a, b], engine='manifold')
    with np.errstate(divide='ignore', invalid='ignore'):     # touching parts give empty, zero-volume results
        return float(i.volume) if len(i.faces) else 0.0


def correct():
    mp = BASE / 'model_manifest.json'
    manifest = json.loads(mp.read_text(encoding='utf-8'))
    newline = '\r\n' if b'\r\n' in mp.read_bytes() else '\n'
    if manifest.get('review_correction_2') == TAG:
        print('Already corrected.')
        return
    if manifest.get('review_correction_2'):
        raise ValueError(f'unexpected second correction {manifest["review_correction_2"]}')
    if manifest.get('review_correction') != PREV_TAG:
        raise ValueError('run scripts/correct_us421_wildcat_review.py first')
    path = BASE / 'model.glb'
    original = path.read_bytes()
    length = struct.unpack_from('<I', original, 12)[0]
    gltf = json.loads(original[20:20 + length])
    binary = bytearray(original[28 + length:])
    before = hashlib.sha256(original).hexdigest()
    if manifest['review_correction_record'].get('after_glb_sha256') != before:
        raise ValueError('model.glb is not the output of the first correction')
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
        v = to_native(read(prim['attributes']['POSITION']).astype(np.float64))
        return trimesh.Trimesh(v, read(prim['indices']).reshape(-1, 3), process=False)

    def write_solid(pid, mesh):
        prim = meshes[pid]['primitives'][0]
        color = read(prim['attributes']['COLOR_0'])[0]
        prim['attributes'] = {'POSITION': append(to_glb(mesh.vertices).astype('<f4'), 'VEC3', 5126),
                              'COLOR_0': append(np.tile(color, (len(mesh.vertices), 1)).astype('u1'), 'VEC4', 5121)}
        gltf['accessors'][prim['attributes']['COLOR_0']]['normalized'] = True
        prim['indices'] = append(mesh.faces.reshape(-1, 1).astype('<u4'), 'SCALAR', 5125)

    orig = {m['name']: solid(m['name']) for m in gltf['meshes']}
    changed, new = [], {}

    def record(pid, mesh, note, dims=None, drop=(), pages=None, basis=None, shells_expected=1, replace=None):
        if not mesh.is_watertight or not mesh.is_winding_consistent or mesh.volume <= 0 or \
                len(shells(mesh)) != shells_expected:
            raise ValueError(f'{pid}: invalid corrected solid')
        p = parts[pid]
        p['bounds_m'] = mesh.bounds.round(6).tolist()
        p['volume_m3'] = round(float(mesh.volume), 6)
        for k in drop:
            p['dimensions'].pop(k, None)
        if dims:
            p['dimensions'].update(dims)
        if pages:
            p['pdf_pages'] = sorted(set(p['pdf_pages']) | set(pages))
            p['sheets'] = sorted(set(p.get('sheets', [])) | set(pages))
        if basis:
            p['basis'] = basis
        text = p.get('note', '')
        for old, rep in (replace or {}).items():
            if old not in text:
                raise ValueError(f'{pid}: note text {old!r} not found')
            text = text.replace(old, rep)
        p['note'] = (text + ' ' + note).strip()
        meshes[pid]['extras'].update(name=p['name'], note=p['note'], basis=p['basis'], pdf_pages=p['pdf_pages'],
                                     bounds_m=p['bounds_m'], volume_m3=p['volume_m3'], dimensions=p['dimensions'])
        changed.append(pid)
        new[pid] = mesh

    def soffit_fn(deck):
        """Deck soffit z(x, y): the deck is a prism of 3-point crowned sections (Y = -W, 0, W)."""
        v = deck.vertices
        xs = np.unique(np.round(v[:, 0], 6))
        half = np.abs(v[:, 1]).max()
        rows = []
        for x in xs:
            s = v[np.isclose(v[:, 0], x, atol=1e-6)]
            row = []
            for y in (-half, 0.0, half):
                z = s[np.isclose(s[:, 1], y, atol=1e-5), 2]
                if len(z) != 2:
                    raise ValueError('unexpected deck section')
                row.append(z.min())
            rows.append(row)
        rows = np.array(rows)

        def f(x, y):
            zy = [np.interp(x, xs, rows[:, k]) for k in range(3)]
            return float(np.interp(y, [-half, 0.0, half], zy))
        return f, xs

    # 2. Box beams: square top corners, bottom chamfers, camber and internal voids unchanged (sheet 21).
    beams = {}
    for s in 'AC':
        for i in range(1, 5):
            pid = f'box_{s}{i}'
            m = orig[pid]
            groups = shells(m)
            vols = [submesh(m, g).volume for g in groups]
            outer = submesh(m, groups[int(np.argmax(vols))])
            voids = [submesh(m, g) for k, g in enumerate(groups) if k != int(np.argmax(vols))]
            if len(voids) != 2 or any(v.volume >= 0 for v in voids):
                raise ValueError(f'{pid}: expected an outer shell and two voids')
            v = outer.vertices
            yc = (v[:, 1].min() + v[:, 1].max()) / 2
            if abs(v[:, 1].max() - v[:, 1].min() - 2 * BEAM_HALF) > 1e-4:
                raise ValueError(f'{pid}: unexpected width')
            xs = np.unique(np.round(v[:, 0], 5))
            rings = []
            for x in xs:
                sec = v[np.abs(v[:, 0] - x) < 1e-5]
                dy = np.round(sec[:, 1] - yc, 4)
                inner = sec[np.isclose(np.abs(dy), round(BEAM_HALF - CHAMFER, 4))]
                side = sec[np.isclose(np.abs(dy), round(BEAM_HALF, 4))]
                if len(sec) != 8 or len(inner) != 4 or len(side) != 4:
                    raise ValueError(f'{pid}: unexpected section at x={x}')
                top, bot = inner[:, 2].max(), inner[:, 2].min()
                if abs(top - bot - BEAM_DEPTH) > 2e-4 or abs(side[:, 2].max() - (top - CHAMFER)) > 2e-4 or \
                        abs(side[:, 2].min() - (bot + CHAMFER)) > 2e-4:
                    raise ValueError(f'{pid}: top corners are not chamfered as expected at x={x}')
                x0 = float(sec[:, 0].mean())
                rings.append([(x0, yc - BEAM_HALF, top), (x0, yc - BEAM_HALF, bot + CHAMFER),
                              (x0, yc - BEAM_HALF + CHAMFER, bot), (x0, yc + BEAM_HALF - CHAMFER, bot),
                              (x0, yc + BEAM_HALF, bot + CHAMFER), (x0, yc + BEAM_HALF, top)])
            shell = loft(rings)
            if abs(shell.volume - outer.volume - (CHAMFER ** 2) * np.ptp(xs)) > 1e-6:
                raise ValueError(f'{pid}: unexpected added corner volume')
            beam = trimesh.util.concatenate([shell] + voids)
            beam = trimesh.Trimesh(beam.vertices, beam.faces, process=False)
            beams[pid] = beam
            write_solid(pid, beam)
            record(pid, beam, 'Top corners squared per sheet 21 (the 1 in chamfers are at the bottom corners only); '
                              'the fillet bears on the full 4 ft top. Voids, camber and bottom chamfers unchanged.',
                   dims=dict(chamfer_in=1, chamfered_corners='bottom only'), pages=[21], shells_expected=3)
            print(f'{pid}: volume {m.volume:.6f} -> {beam.volume:.6f} m3')

    # 1. Pavement ledges, end diaphragms and approach seats (sheets 10, 14, 24, 28).
    seat_profile = [(0.0, 0.20), (0.0, SEAT_DEPTH), (LEDGE_PROJECTION, SEAT_DEPTH), (SEAT_LENGTH, SEAT_DEPTH),
                    (SEAT_LENGTH + SEAT_TAPER + 0.02, APPROACH_DEPTH - 0.02),
                    (SEAT_LENGTH + SEAT_TAPER + 0.02, 0.20)]       # (distance behind the face, depth below top)
    for abut, side, page, span in ((1, -1, 10, 'A'), (4, 1, 14, 'C')):
        ledge_id, dia_id, app_id = f'ledge{abut}', f'diaphragm{abut}', f'approach{abut}'
        ledge, dia, app = orig[ledge_id], orig[dia_id], orig[app_id]
        cap, step = orig[f'abut{abut}_cap'], orig[f'abut{abut}_step']
        face = dia.bounds[0][0] if side < 0 else dia.bounds[1][0]          # back face of the diaphragm
        app_face = app.bounds[1][0] if side < 0 else app.bounds[0][0]
        led_face = ledge.bounds[0][0] if side < 0 else ledge.bounds[1][0]
        if abs(face - app_face) > 1e-5 or abs(face - led_face) > 1e-5 or len(ledge.vertices) != 8 or \
                abs(ledge.extents[0] - LEDGE_PROJECTION) > 1e-4 or abs(ledge.extents[2] - 4 * IN) > 3e-4 or \
                abs(ledge.bounds[1][1] - LEDGE_HALF) > 1e-4:
            raise ValueError(f'{ledge_id}: unexpected original ledge (inside the diaphragm, 4 in deep)')
        inside = face - side * 0.07
        gap = vertical_hits(dia, inside, 0.0)
        if not np.any(np.isclose(gap, ledge.bounds[0][2], atol=1e-4)):
            raise ValueError(f'{dia_id}: expected the ledge notch')
        probe = face + side * 1e-6

        def top_fn(x, y, app=app, face=face):
            xx = face + side * max(abs(x - face), 1e-6)
            z = vertical_hits(app, xx, y)
            if len(z) < 2:
                raise ValueError('approach top not found')
            return float(z.max())
        if abs(np.ptp(vertical_hits(app, probe, 0.0)) - APPROACH_DEPTH) > 1e-4:
            raise ValueError(f'{app_id}: approach is not 12 in deep at the bridge end')

        # Diaphragm rebuilt as in the first correction, without the ledge cutter (fills the notch).
        x0, x1 = cap.bounds[0][0], cap.bounds[1][0]
        soffit, deck_xs = soffit_fn(orig[f'deck_{span}'])
        half = dia.bounds[1][1]
        cap_top, step_top, step_half = cap.bounds[1][2], step.bounds[1][2], step.bounds[1][1]
        xs = sorted({x0, x1} | {x for x in deck_xs if x0 + 1e-4 < x < x1 - 1e-4})
        prism = grid_solid(xs, [-half, 0.0, half], soffit, lambda x, y: cap_top + EPS)
        cutters = [box(x0 - 0.05, x1 + 0.05, -step_half, step_half, cap_top - 0.05, step_top + EPS)]
        for i in range(1, 5):
            b = beams[f'box_{span}{i}']
            cx = (b.bounds[0][0], x1 + 0.05) if abut == 1 else (x0 - 0.05, b.bounds[1][0])
            cutters.append(box(cx[0], cx[1], b.bounds[0][1], b.bounds[1][1], 3.0, 9.0))
        new_dia = trimesh.boolean.difference([prism] + cutters, engine='manifold')
        notch = ledge.extents[0] * ledge.extents[1] * ledge.extents[2]
        if abs(new_dia.volume - dia.volume - notch) > 2e-4:
            raise ValueError(f'{dia_id}: rebuilt diaphragm differs from the original by more than the notch')

        # Ledge: 6 in outside the back face, top 1 ft 2 in below the approach top, 1 ft 0 in deep.
        lx = sorted([face, face + side * LEDGE_PROJECTION])
        new_ledge = grid_solid(lx, [-LEDGE_HALF, 0.0, LEDGE_HALF], lambda x, y: top_fn(x, y) - SEAT_DEPTH,
                               lambda x, y: top_fn(x, y) - SEAT_DEPTH - LEDGE_DEPTH)

        # Approach seat: 1 ft 2 in deep over 2 ft 0 in from the face, 2 in x 2 in taper, over the ledge length.
        rings = []
        for y in (-LEDGE_HALF, 0.0, LEDGE_HALF):
            ring = []
            for dist, depth in seat_profile:
                x = face + side * dist
                ring.append((x, y, top_fn(x, y) - depth))
            rings.append(ring)
        seat = loft(rings)
        new_app = trimesh.boolean.union([app, seat], engine='manifold')
        added = (SEAT_LENGTH * (SEAT_DEPTH - APPROACH_DEPTH) + 0.5 * SEAT_TAPER ** 2) * 2 * LEDGE_HALF
        if abs(new_app.volume - app.volume - added) > 5e-4:
            raise ValueError(f'{app_id}: unexpected seat volume {new_app.volume - app.volume}')

        write_solid(dia_id, new_dia)
        record(dia_id, new_dia, 'The 6 in pavement ledge projects outside the back face (sheets 10, 14, 24), so the '
                                'diaphragm is solid over its full 2 ft 6 in (ledge notch filled).',
               replace={'beam pockets and the pavement-ledge part excluded.': 'beam pockets excluded.'})
        write_solid(ledge_id, new_ledge)
        record(ledge_id, new_ledge,
               f'Rebuilt per sheet {page} Sections A-A and B-B and sheet 24 Sections B-B and C-C: projects 6 in from '
               'the back face of the diaphragm toward the approach, top 1 ft 2 in below the approach top, 1 ft 0 in '
               'deep, parallel to the approach crown and grade; 28 ft 0 in long as before. It was a 4 in block inside '
               'the diaphragm.',
               dims=dict(projection_in=6, depth_in=12, top_below_approach_top_in=14), pages=[page, 24],
               basis=f'Dimensioned (sheets {page}, 24)')
        write_solid(app_id, new_app)
        record(app_id, new_app,
               'Bridge-end seat per sheets 10, 14 and 24: thickened to 1 ft 2 in over the 6 in pavement ledge and '
               '1 ft 6 in behind it, with a 2 in x 2 in taper to the 12 in slab (lengths scaled), over the 28 ft 0 in '
               'ledge length; 12 in depth from the sheet 28 bill of materials.',
               dims=dict(depth_in=12, seat_depth_in=14, seat_length_in=24, seat_taper_in=2),
               drop=('assumed_depth_in',), pages=[page, 24],
               basis='Dimensioned footprint (sheet 28); 12 in depth from the sheet 28 bill of materials; bridge-end '
                     'seat per sheets 10, 14, 24 (seat length and taper scaled)')
        print(f'{ledge_id}: X {lx[0]:.4f}-{lx[1]:.4f}, Z {new_ledge.bounds[0][2]:.4f}-{new_ledge.bounds[1][2]:.4f}; '
              f'{dia_id} {dia.volume:.4f} -> {new_dia.volume:.4f} m3; {app_id} {app.volume:.4f} -> '
              f'{new_app.volume:.4f} m3')

    # Interfaces: no rebuilt part may overlap a neighbour more than it did before (pre-existing embedded parts,
    # such as the socket rims in the beam tops, are unchanged).
    for pid in changed:
        for other, mesh in orig.items():
            if other == pid or not mesh.is_watertight:
                continue
            after = overlap(new[pid], new.get(other, mesh))
            if after > 1e-6 and after > overlap(orig[pid], mesh) + 1e-6:
                raise ValueError(f'{pid} overlaps {other} by {after:.6f} m3')

    while len(binary) % 4:
        binary.append(0)
    gltf['buffers'][0]['byteLength'] = len(binary)
    encoded = json.dumps(gltf, ensure_ascii=True, separators=(',', ':')).encode()
    encoded += b' ' * ((-len(encoded)) % 4)
    out = (struct.pack('<III', 0x46546c67, 2, 28 + len(encoded) + len(binary)) +
           struct.pack('<II', len(encoded), 0x4e4f534a) + encoded + struct.pack('<II', len(binary), 0x004e4942) + binary)
    backup = ROOT / 'data/fem_research'
    backup.mkdir(exist_ok=True)
    (backup / 'us421-wildcat_before_review_correction_2.glb').write_bytes(original)
    (backup / 'us421-wildcat_manifest_before_review_correction_2.json').write_bytes(mp.read_bytes())
    path.write_bytes(out)

    for item in manifest.get('detail_coverage', []):
        if item.get('feature') == 'Eight concrete box beams':
            if 'external chamfered sections' not in item['detail']:
                raise ValueError('unexpected box-beam coverage text')
            item['detail'] = item['detail'].replace('external chamfered sections',
                                                    'sections with 1 in bottom chamfers and square top corners')
        elif item.get('feature') == 'Rails and approaches':
            item['detail'] = ('New FC barriers use the p27 section; 20 ft 6 in approach footprint with 4 ft 1 in x '
                              '1 ft 6 in corner cutbacks (p28), 12 in slab (p28 bill of materials) thickened to '
                              '1 ft 2 in on the 6 in pavement ledge (pp10, 14, 24); TFC envelopes reuse the FC section '
                              'and end with their 16 ft 5 in RCBA extension; retained metal rail profile and the '
                              'extension seat are inferred without referenced standards.')
            item['sources'] = sorted(set(item['sources']) | {10, 14, 24})
    manifest['review_correction_2'] = TAG
    manifest['revision'] = REVISION
    manifest['review_correction_2_record'] = dict(
        follows=PREV_TAG,
        source_pdf_pages=[10, 14, 20, 21, 24, 28], printed_sheets=[10, 14, 20, 21, 24, 28],
        corrections={
            'pavement_ledges': '6 in projection outside the diaphragm back face, top 1 ft 2 in below the approach top, '
                               '1 ft 0 in deep, 28 ft 0 in long (sheets 10, 14, 24); diaphragm notch filled',
            'approach_seats': '12 in slab thickened to 1 ft 2 in over the ledge and 1 ft 6 in behind it, 2 in x 2 in '
                              'taper (sheets 10, 14, 24 scaled; 12 in per sheet 28 bill of materials)',
            'box_beam_top_corners': 'square top corners; 1 in chamfers at the bottom corners only (sheet 21)'},
        changed_parts=changed, before_glb_sha256=before, after_glb_sha256=hashlib.sha256(out).hexdigest())
    deviations = [d for d in manifest.get('known_deviations', []) if d.get('id') != 'approach-extension-seat']
    deviations.append(dict(
        id='approach-extension-seat', parts='approach1, approach4, ledge1, ledge4',
        source='sheets 10, 14, 24, 28',
        deviation='The ledge and the thickened approach seat are modelled over the 28 ft 0 in pavement only; the 1 ft '
                  '6 in RCBA extensions under the TFC transitions keep the plain 12 in slab with no seat.',
        reason='Standard E 609-TBAE-01 (RCBA extension) is referenced on sheet 28 but not supplied.'))
    manifest['known_deviations'] = deviations
    text = json.dumps(manifest, ensure_ascii=False, indent=2) + '\n'
    mp.write_bytes(text.replace('\n', newline).encode('utf-8'))      # keep the file's own line endings
    print(json.dumps({k: v for k, v in manifest['review_correction_2_record'].items() if k != 'corrections'}))
    print(f'{len(changed)} parts changed')


if __name__ == '__main__':
    correct()

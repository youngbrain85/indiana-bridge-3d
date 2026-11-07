"""Third drawing-confirmed correction of US 421 over South Fork Wildcat Creek (us421-wildcat): the known deviations
left by the first two reviews. Runs after scripts/correct_us421_wildcat_review_2.py and preserves unrelated GLB
buffers.

    python scripts/correct_us421_wildcat_review_3.py

Source: drawings.pdf (INDOT 2020 rehabilitation plans, 30 sheets); printed sheet numbers equal PDF page numbers.
Native axes: X = station from Sta. 42+54.00, Y = transverse (+Y = left of increasing station = X-truss and Beam No. 1
side, sheets 5, 16, 20), Z = elevation - 778 ft.

1. Abutment inner bearing step (known deviation abutment-inner-step-width; sheets 10 and 14). The plans at Abutments
   No. 1 and No. 4 dimension the step edge 2 ft 6 in (Typ.) outside C Beam No. 3 / No. 2, which are 4 ft 2 in from
   Line "A": the step runs 6 ft 8 in each side of the centre line (13 ft 4 in). The vector plans and elevations place
   the step edges 79.98-80.00 in from Line "A" on both sheets, and the sheet 24 typical bent diaphragm agrees
   (80.5 in, scaled). The model had +/-8 ft 6 in. The two steps are shortened; the end diaphragms, whose bottom is
   1/2 in (EPS) above the cap and the step, are rebuilt with the first correction's construction and gain the 2 in
   between 6 ft 9 in and 8 ft 6 in. The step faces get the 1 in vertical EPS of the note "1/2 in on horizontal faces,
   1 in on vertical faces" (sheet 10 Section B-B, sheet 24 Section C-C): the written note governs over the about
   1/2 in offset drafted on the elevations, and matches the 1 in EPS at the wing faces. No bearing pad moves: the inner
   pads end at 6 ft 0 in, the outer ones start at 10 ft 8 in.
2. Pavement ledge and approach seat under the RCBA extensions (known deviation approach-extension-seat; sheets 24 and
   28). The sheet 24 typical bent diaphragm draws the ledge (hidden top and bottom lines, 1 ft 2 in and 2 ft 2 in
   below the deck top, parallel to the crown) over the full diaphragm length, to within one dash of its ends at the
   1 in EPS against the wings; the 4-#7 x 30 ft 9 in rear-face bars in it are "continuous". The sheet 28 plan
   (top reinforcement) draws the ledge edge 6 in inside the slab end across the full 31 ft 0 in, extensions
   included, and its bill of materials pays the 1 ft 6 in x 16 ft 5 in extensions as 12 in "R.C. Bridge Approach"
   (69.3 SYS = 28 ft x 20 ft 6 in + 2 x 1 ft 6 in x 16 ft 5 in). The model stopped the ledge and the approach seat
   at 28 ft 0 in. Both now run the full 31 ft 0 in (|Y| <= 15 ft 6 in, like the diaphragm); the seat keeps the
   section scaled from sheets 10, 14 and 24 (1 ft 2 in deep over 2 ft 0 in from the face, 2 in x 2 in taper). The
   approach is rebuilt whole from its own top surface (checked to reproduce the current slab to 3e-6 m) rather than
   unioned onto the old seat, which would join nearly coincident float32 faces.
3. Type TFC transition envelopes (known deviation tfc-transition-envelope, kept and narrowed; sheets 27 and 28). The
   sheet 27 railing elevation (no scale) draws the TFC top as one level line with the FC top over the whole
   transition and its far end at full height. The envelopes had an illustrative taper to 0.72 of the FC section
   (9.3 in lower at the far end), which no sheet shows. They now keep the sheet 27 FC section (2 ft 9 in) over their
   16 ft 5 in RCBA extension, on the same bottom line. The transition face and end details (E 706-TTFC-01 to -03)
   are still not supplied.
4. Railing bases (sheet 27 Section A-A; 2 % crown, sheets 6, 7). The FC railings and TFC envelopes are cast on the
   deck / approach slab at a Type "A" construction joint, but their bottoms were level across the crossfall, 0.32 in
   (8.1 mm) above the slab at the rear face. Their rear bottom edges are set on the slab; the toe and the profile
   above it are unchanged.

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
TAG = 'abutment-step-ledge-extension-tfc-height'
PREV_TAG = 'ledge-seat-square-beam-tops'
PREV_REVISION = '1.2-drawing-review-2'
REVISION = '1.3-deviations'

STEP_HALF = 4 * FT + 2 * IN + 2 * FT + 6 * IN    # C Beam No. 3 at 4'-2" + 2'-6" (Typ.) = 6'-8" (sheets 10, 14 plans)
OLD_STEP_HALF = 8.5 * FT
EPS = 0.5 * IN                   # expanded polystyrene under the diaphragm (sheets 10, 14, 24)
EPS_VERTICAL = 1 * IN            # EPS on vertical faces (sheet 10 Section B-B, sheet 24 Section C-C note)
DIA_HALF = 15.5 * FT             # diaphragm, ledge and seat length 31 ft 0 in (1 in EPS at the wing faces)
OLD_LEDGE_HALF = 14 * FT
LEDGE_PROJECTION = 6 * IN        # sheets 10, 14, 24
LEDGE_DEPTH = 12 * IN            # sheet 24 Sections B-B, C-C
SEAT_DEPTH = 14 * IN             # approach top to ledge top (sheets 10, 14, 24)
APPROACH_DEPTH = 12 * IN         # sheet 28 bill of materials
SEAT_LENGTH = 24 * IN            # scaled, sheets 10, 14, 24 (as in the second correction)
SEAT_TAPER = 2 * IN
APPROACH_LENGTH = 20.5 * FT       # sheet 28
EXT_LENGTH = 16 * FT + 5 * IN     # RCBA extension for the TFC transition (sheet 28)
FC_HEIGHT = 33 * IN              # sheet 27 Section A-A
RAIL_TOE_Y = 14 * FT             # FC/TFC traffic-face toe (28 ft 0 in roadway, sheets 22, 27)
RAIL_REAR_Y = 15.5 * FT - 2 * IN  # rear face 2 in inside the 31 ft deck edge (sheet 27)
CROSSFALL = 0.02                 # 2 % crown (sheets 6, 7)


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
    if manifest.get('review_correction_3') == TAG:
        print('Already corrected.')
        return
    if manifest.get('review_correction_3'):
        raise ValueError(f'unexpected third correction {manifest["review_correction_3"]}')
    if manifest.get('review_correction_2') != PREV_TAG or manifest.get('revision') != PREV_REVISION:
        raise ValueError('run scripts/correct_us421_wildcat_review.py and _review_2.py first')
    path = BASE / 'model.glb'
    original = path.read_bytes()
    length = struct.unpack_from('<I', original, 12)[0]
    gltf = json.loads(original[20:20 + length])
    binary = bytearray(original[28 + length:])
    before = hashlib.sha256(original).hexdigest()
    if manifest['review_correction_2_record'].get('after_glb_sha256') != before:
        raise ValueError('model.glb is not the output of the second correction')
    deviations = {d['id']: d for d in manifest.get('known_deviations', [])}
    if set(deviations) != {'abutment-inner-step-width', 'tfc-transition-envelope', 'approach-extension-seat'}:
        raise ValueError(f'unexpected known deviations {sorted(deviations)}')
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

    def write_positions(pid, vertices):
        """Same topology and colours; only the vertex positions are replaced."""
        prim = meshes[pid]['primitives'][0]
        prim['attributes']['POSITION'] = append(to_glb(vertices).astype('<f4'), 'VEC3', 5126)

    orig = {m['name']: solid(m['name']) for m in gltf['meshes']}
    changed, new = [], {}

    def record(pid, mesh, note, dims=None, pages=None, basis=None, replace=None, extras=None):
        # measure the solid as stored (float32 GLB positions), so the manifest matches the file
        mesh = trimesh.Trimesh(to_native(to_glb(mesh.vertices).astype('<f4').astype(np.float64)), mesh.faces,
                               process=False)
        if not mesh.is_watertight or not mesh.is_winding_consistent or mesh.volume <= 0 or len(shells(mesh)) != 1:
            raise ValueError(f'{pid}: invalid corrected solid')
        p = parts[pid]
        p['bounds_m'] = mesh.bounds.round(6).tolist()
        p['volume_m3'] = round(float(mesh.volume), 6)
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
        ex = meshes[pid]['extras']
        ex.update(name=p['name'], note=p['note'], basis=p['basis'], pdf_pages=p['pdf_pages'],
                  bounds_m=p['bounds_m'], volume_m3=p['volume_m3'], dimensions=p['dimensions'])
        if extras:
            ex.update(extras)
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

    for abut, side, page, span in ((1, -1, 10, 'A'), (4, 1, 14, 'C')):
        step_id, dia_id, ledge_id, app_id = f'abut{abut}_step', f'diaphragm{abut}', f'ledge{abut}', f'approach{abut}'
        cap, step, dia, ledge, app = (orig[k] for k in (f'abut{abut}_cap', step_id, dia_id, ledge_id, app_id))

        # 1. Inner bearing step: +/-8 ft 6 in -> +/-6 ft 8 in (sheets 10, 14).
        v = step.vertices.copy()
        if len(v) != 8 or not np.allclose(np.unique(np.round(np.abs(v[:, 1]), 4)), [round(OLD_STEP_HALF, 4)]):
            raise ValueError(f'{step_id}: unexpected original step')
        pads_inner = [m.bounds for k, m in orig.items() if k.startswith(f'pad_{span}') and
                      m.bounds[0][0] < cap.bounds[1][0] and m.bounds[1][0] > cap.bounds[0][0]]
        if len(pads_inner) != 8 or any(OLD_STEP_HALF > abs(b[0][1]) > STEP_HALF - 0.05 or
                                       OLD_STEP_HALF > abs(b[1][1]) > STEP_HALF - 0.05 for b in pads_inner):
            raise ValueError(f'{step_id}: a bearing pad sits near the new step edge')
        v[:, 1] = np.sign(v[:, 1]) * STEP_HALF
        new_step = trimesh.Trimesh(v, step.faces, process=False)
        write_positions(step_id, v)
        record(step_id, new_step,
               f'Shortened to 6 ft 8 in each side of Line "A" (13 ft 4 in) per sheet {page}: the step edge is 2 ft 6 in '
               '(Typ.) outside C Beam No. 3 / No. 2, 4 ft 2 in from Line "A" (plan and elevation agree, sheet 24 '
               'typical bent diaphragm too). It was +/-8 ft 6 in.',
               dims=dict(length_ft=round(2 * STEP_HALF / FT, 4)), pages=[page, 24], basis=f'Dimensioned (sheet {page})',
               extras=dict(extents=new_step.extents.round(6).tolist()))

        # 1a. Diaphragm rebuilt with the first correction's construction (bottom 1/2 in above cap and step).
        x0, x1 = cap.bounds[0][0], cap.bounds[1][0]
        soffit, deck_xs = soffit_fn(orig[f'deck_{span}'])
        half = dia.bounds[1][1]
        if abs(half - DIA_HALF) > 1e-5:
            raise ValueError(f'{dia_id}: unexpected length')
        cap_top, step_top = cap.bounds[1][2], step.bounds[1][2]
        xs = sorted({x0, x1} | {x for x in deck_xs if x0 + 1e-4 < x < x1 - 1e-4})

        def build_dia(step_half, eps_side):
            prism = grid_solid(xs, [-half, 0.0, half], soffit, lambda x, y: cap_top + EPS)
            cutters = [box(x0 - 0.05, x1 + 0.05, -(step_half + eps_side), step_half + eps_side, cap_top - 0.05,
                           step_top + EPS)]
            for i in range(1, 5):
                b = orig[f'box_{span}{i}']
                cx = (b.bounds[0][0], x1 + 0.05) if abut == 1 else (x0 - 0.05, b.bounds[1][0])
                cutters.append(box(cx[0], cx[1], b.bounds[0][1], b.bounds[1][1], 3.0, 9.0))
            return trimesh.boolean.difference([prism] + cutters, engine='manifold')
        if abs(build_dia(OLD_STEP_HALF, 0.0).volume - dia.volume) > 2e-5:
            raise ValueError(f'{dia_id}: construction does not reproduce the current diaphragm')
        new_dia = build_dia(STEP_HALF, EPS_VERTICAL)       # 1 in EPS against the vertical step faces
        fill = 2 * (x1 - x0) * (OLD_STEP_HALF - STEP_HALF - EPS_VERTICAL) * (step_top - cap_top)
        if abs(new_dia.volume - dia.volume - fill) > 2e-5:
            raise ValueError(f'{dia_id}: unexpected volume change {new_dia.volume - dia.volume}')
        write_solid(dia_id, new_dia)
        record(dia_id, new_dia, f'Bottom follows the 13 ft 4 in inner step (sheet {page}): 1/2 in EPS above the step '
                                'and 1 in EPS against its vertical faces (note "1/2 in on horizontal faces, 1 in on '
                                'vertical faces", sheet 10 Section B-B, sheet 24 Section C-C), so the step pocket '
                                'reaches 6 ft 9 in from Line "A"; 1/2 in above the outer cap beyond.')

        # 2. Ledge over the full 31 ft 0 in diaphragm length (sheets 24, 28).
        face = dia.bounds[0][0] if side < 0 else dia.bounds[1][0]
        if abs((app.bounds[1][0] if side < 0 else app.bounds[0][0]) - face) > 1e-5 or \
                abs(ledge.bounds[1][1] - OLD_LEDGE_HALF) > 1e-4 or abs(ledge.extents[0] - LEDGE_PROJECTION) > 1e-4 or \
                abs(app.bounds[1][1] - DIA_HALF) > 1e-4:
            raise ValueError(f'{ledge_id}: unexpected starting ledge/approach')

        far = app.bounds[0][0] if side < 0 else app.bounds[1][0]
        edge = app.vertices[np.isclose(np.abs(app.vertices[:, 1]), DIA_HALF, atol=1e-5)]
        ext_end = edge[:, 0].min() if side < 0 else edge[:, 0].max()
        if abs(abs(ext_end - face) - EXT_LENGTH) > 1e-4 or abs(abs(far - face) - APPROACH_LENGTH) > 1e-4:
            raise ValueError(f'{app_id}: unexpected footprint')
        lo, hi = min(face, far), max(face, far)
        cache = {}

        def surface(x, y, app=app):
            z = vertical_hits(app, min(max(x, lo + 1e-6), hi - 1e-6), y)
            if len(z) < 2:
                raise ValueError('approach top not found')
            return float(z.max())

        def top_fn(x, y):
            """Approach top; planar on each side of the crown (checked below), so it is evaluated at Y = 0 and
            +/-4 m and extended linearly to the slab edges."""
            if (x, y) not in cache:
                z0 = surface(x, 0.0)
                cache[(x, y)] = z0 if y == 0 else z0 + (surface(x, np.sign(y) * 4.0) - z0) * abs(y) / 4.0
            return cache[(x, y)]
        for x in np.linspace(lo + 0.01, hi - 0.01, 9):
            for y in (-4.6, -2.0, 2.0, 4.2):
                if abs(x - face) > EXT_LENGTH and abs(y) > OLD_LEDGE_HALF:
                    continue
                if abs(surface(x, y) - top_fn(x, y)) > 3e-6:
                    raise ValueError(f'{app_id}: approach top is not planar across the half width')
        lx = sorted([face, face + side * LEDGE_PROJECTION])
        old_check = grid_solid(lx, [-OLD_LEDGE_HALF, 0.0, OLD_LEDGE_HALF], lambda x, y: top_fn(x, y) - SEAT_DEPTH,
                               lambda x, y: top_fn(x, y) - SEAT_DEPTH - LEDGE_DEPTH)
        if abs(old_check.volume - ledge.volume) > 1e-5 or np.abs(old_check.bounds - ledge.bounds).max() > 1e-5:
            raise ValueError(f'{ledge_id}: construction does not reproduce the current ledge')
        new_ledge = grid_solid(lx, [-DIA_HALF, 0.0, DIA_HALF], lambda x, y: top_fn(x, y) - SEAT_DEPTH,
                               lambda x, y: top_fn(x, y) - SEAT_DEPTH - LEDGE_DEPTH)
        if abs(new_ledge.volume - ledge.volume * DIA_HALF / OLD_LEDGE_HALF) > 1e-5:
            raise ValueError(f'{ledge_id}: unexpected volume')
        write_solid(ledge_id, new_ledge)
        record(ledge_id, new_ledge,
               'Extended to the full 31 ft 0 in diaphragm length (1 in EPS at the wing faces): the sheet 24 typical '
               'bent diaphragm draws the ledge to the diaphragm ends with continuous rear-face bars, and the sheet 28 '
               'plan draws its edge 6 in inside the slab end across the RCBA extensions.',
               replace={'; 28 ft 0 in long as before. It was': '. It was'},
               dims=dict(length_ft=31), pages=[24, 28], basis=f'Dimensioned (sheets {page}, 24, 28)')

        # 2a. Approach rebuilt from its own top surface: 12 in slab, 1 ft 2 in seat over 2 ft 0 in, 2 in x 2 in taper
        # (second correction), over the 28 ft pavement and, now, also under the two 1 ft 6 in RCBA extensions.
        # A union onto the existing seat would join nearly coincident float32 faces, so the slab is rebuilt whole.
        up = app.face_normals[:, 2] > 0.9
        rows = {float(x) for x in app.vertices[np.unique(app.faces[up])][:, 0]}
        fixed = [face, far, ext_end] + [face + side * d for d in (LEDGE_PROJECTION, SEAT_LENGTH,
                                                                  SEAT_LENGTH + SEAT_TAPER)]
        xs_app = sorted(set(fixed) | {x for x in rows if lo + 1e-5 < x < hi - 1e-5 and
                                      min(abs(x - f) for f in fixed) > 1e-5})
        xs_ext = [x for x in xs_app if abs(x - face) <= EXT_LENGTH + 1e-6]

        def depth(x, seat):
            d = abs(x - face)
            if seat and d <= SEAT_LENGTH + 1e-9:
                return SEAT_DEPTH
            if seat and d <= SEAT_LENGTH + SEAT_TAPER + 1e-9:
                return SEAT_DEPTH - (d - SEAT_LENGTH)
            return APPROACH_DEPTH

        def build_app(seat_ext):
            pieces = [grid_solid(xs_app, [-OLD_LEDGE_HALF, 0.0, OLD_LEDGE_HALF], top_fn,
                                 lambda x, y: top_fn(x, y) - depth(x, True))]
            for s in (-1, 1):
                pieces.append(grid_solid(xs_ext, sorted([s * OLD_LEDGE_HALF, s * DIA_HALF]), top_fn,
                                         lambda x, y: top_fn(x, y) - depth(x, seat_ext)))
            shift = np.array([face, 0.0, 6.0])               # boolean near the origin (float32 inside manifold)
            local = [trimesh.Trimesh(p.vertices - shift, p.faces, process=False) for p in pieces]
            u = trimesh.boolean.union(local, engine='manifold')
            return trimesh.Trimesh(u.vertices + shift, u.faces, process=False)
        old_app = build_app(False)
        if abs(old_app.volume - app.volume) > 2e-5 or np.abs(old_app.bounds - app.bounds).max() > 1e-5:
            raise ValueError(f'{app_id}: construction does not reproduce the current approach')
        for x in np.linspace(lo + 0.003, hi - 0.003, 23):
            for y in np.linspace(-DIA_HALF + 0.003, DIA_HALF - 0.003, 13):
                a, b = vertical_hits(app, x, y), vertical_hits(old_app, x, y)
                if len(a) != len(b) or (len(a) and np.abs(a - b).max() > 3e-6):
                    raise ValueError(f'{app_id}: rebuilt surfaces differ from the current approach at {x}, {y}')
        new_app = build_app(True)
        added = (SEAT_LENGTH * (SEAT_DEPTH - APPROACH_DEPTH) + 0.5 * SEAT_TAPER ** 2) * 2 * (DIA_HALF - OLD_LEDGE_HALF)
        if abs(new_app.volume - old_app.volume - added) > 2e-6:
            raise ValueError(f'{app_id}: unexpected seat volume {new_app.volume - old_app.volume}')
        write_solid(app_id, new_app)
        record(app_id, new_app,
               'The seat continues under both 1 ft 6 in RCBA extensions over the full 31 ft 0 in ledge (sheets 24, 28); '
               'the extensions are 12 in R.C. Bridge Approach (sheet 28 bill of materials, 69.3 SYS).',
               replace={'over the 28 ft 0 in ledge length; ': 'over the ledge length; '},
               dims=dict(seat_width_ft=31), pages=[24, 28])
        print(f'{step_id}: +/-{OLD_STEP_HALF:.4f} -> +/-{STEP_HALF:.4f} m; {dia_id} {dia.volume:.4f} -> '
              f'{new_dia.volume:.4f} m3; {ledge_id} {ledge.volume:.4f} -> {new_ledge.volume:.4f} m3; '
              f'{app_id} {app.volume:.4f} -> {new_app.volume:.4f} m3')

    # 3. Railing bases (sheet 27 Section A-A): the FC and TFC railings are cast on the deck / approach slab (Type "A"
    # construction joint); their bottoms were level across the 2 % crossfall, 0.32 in above the slab at the rear
    # face. The rear bottom edge is set on the slab; the toe and every upper vertex stay (heights per sheet 27 are
    # measured at the traffic face).
    def slab_top(support, x, y):
        lo, hi = support.bounds[0][0], support.bounds[1][0]
        z = vertical_hits(support, min(max(x, lo + 1e-6), hi - 1e-6), y)
        if len(z) < 2:
            raise ValueError('slab top not found')
        return float(z.max())

    def rail_rings(pid):
        v = orig[pid].vertices
        if len(v) % 6:
            raise ValueError(f'{pid}: unexpected loft')
        rings = v.reshape(-1, 6, 3).copy()
        if np.ptp(rings[:, :, 0], axis=1).max() > 1e-5:
            raise ValueError(f'{pid}: rings are not stations')
        return rings

    def fit_base(pid, rings, support):
        out = rings.copy()
        for ring in out:
            toe, rear = ring[0], ring[1]
            if abs(abs(toe[1]) - RAIL_TOE_Y) > 1e-4 or abs(abs(rear[1]) - RAIL_REAR_Y) > 1e-4 or \
                    abs(toe[2] - rear[2]) > 1e-6 or ring[:, 2].min() < toe[2] - 1e-9:
                raise ValueError(f'{pid}: unexpected rail section')
            if abs(slab_top(support, toe[0], toe[1]) - toe[2]) > 2e-5:
                raise ValueError(f'{pid}: toe is not on the slab')
            ring[1, 2] = slab_top(support, rear[0], rear[1])
        drop = rings[:, 1, 2] - out[:, 1, 2]
        if np.abs(drop - CROSSFALL * (RAIL_REAR_Y - RAIL_TOE_Y)).max() > 2e-5:
            raise ValueError(f'{pid}: unexpected base gap {drop.min()}..{drop.max()}')
        return out
    base_note = ('Base set on the slab per sheet 27 Section A-A (cast on it at a Type "A" construction joint): the rear '
                 'bottom edge is lowered 0.32 in onto the 2 % crossfall, closing the gap under the level base; the toe '
                 'and the section heights at the traffic face are unchanged.')
    fc_ends = {}
    for span, deck in (('A', 'deck_A'), ('C', 'deck_C')):
        for s in (-1, 1):
            pid = f'FC_{span}_{s}'
            m, rings = orig[pid], rail_rings(pid)
            out = fit_base(pid, rings, orig[deck])
            new_fc = trimesh.Trimesh(out.reshape(-1, 3), m.faces, process=False)
            wedge = 0.5 * (RAIL_REAR_Y - RAIL_TOE_Y) ** 2 * CROSSFALL * m.extents[0]
            if abs(new_fc.volume - m.volume - wedge) > 2e-5:
                raise ValueError(f'{pid}: unexpected volume change {new_fc.volume - m.volume}')
            write_positions(pid, out.reshape(-1, 3))
            record(pid, new_fc, base_note, dims=dict(rear_face_height_in=round(FC_HEIGHT / IN + 0.32, 2)), pages=[27])
            fc_ends[pid] = {round(float(r[0, 0]), 4): r for r in out}
            print(f'{pid}: rear base lowered {np.mean(rings[:, 1, 2] - out[:, 1, 2]) * 1000:.3f} mm; volume '
                  f'{m.volume:.4f} -> {new_fc.volume:.4f} m3')

    # 4. TFC envelopes: the sheet 27 FC section over the whole transition (no illustrative taper), base on the slab.
    for abut, span in ((1, 'A'), (4, 'C')):
        for s in (-1, 1):
            pid, fc = f'TFC{abut}_{s}', orig[f'FC_{span}_{s}']
            m, rings = orig[pid], rail_rings(pid)
            end = int(np.argmax(np.abs(rings[:, 1, 1])))          # bridge end: full section
            fc_x = fc.bounds[0][0] if abut == 1 else fc.bounds[1][0]
            if abs(rings[end, 0, 0] - fc_x) > 1e-5 or end not in (0, len(rings) - 1):
                raise ValueError(f'{pid}: bridge end does not meet the FC railing')
            fc_ring = fc.vertices[np.abs(fc.vertices[:, 0] - fc_x) < 1e-5]
            for p in rings[end]:
                if np.linalg.norm(fc_ring - p, axis=1).min() > 1e-4:
                    raise ValueError(f'{pid}: bridge-end section differs from the FC section')
            far = len(rings) - 1 - end
            if abs(np.ptp(rings[end, :, 2]) - FC_HEIGHT) > 2e-4 or np.ptp(rings[far, :, 2]) > FC_HEIGHT - 0.1:
                raise ValueError(f'{pid}: expected the tapered envelope')
            level = rings.copy()
            for i in range(len(rings)):
                level[i] = rings[end] + np.array([0.0, 0.0, rings[i, 0, 2] - rings[end, 0, 2]])
                level[i, :, 0] = rings[i, 0, 0]
            area = abs(trimesh.Trimesh(fc.vertices, fc.faces).volume / fc.extents[0])
            if abs(trimesh.Trimesh(level.reshape(-1, 3), m.faces).volume - area * m.extents[0]) > 2e-4:
                raise ValueError(f'{pid}: unexpected volume of the level envelope')
            out = fit_base(pid, level, new[f'approach{abut}'])
            butt = fc_ends[f'FC_{span}_{s}'][round(float(fc_x), 4)]
            if abs(out[end, 1, 2] - butt[1, 2]) > 2e-5:
                raise ValueError(f'{pid}: deck and approach disagree at the butt joint')
            out[end, 1, 2] = butt[1, 2]                           # identical butt-joint sections
            out = out.reshape(-1, 3)
            new_tfc = trimesh.Trimesh(out, m.faces, process=False)
            write_positions(pid, out)
            record(pid, new_tfc,
                   'Height corrected per the sheet 27 railing elevation: the TFC top runs level with the FC top over the '
                   'whole transition and its far end is full height, so the envelope keeps the sheet 27 FC section '
                   '(2 ft 9 in) over its 16 ft 5 in RCBA extension, on the same bottom line; the illustrative taper to '
                   '0.72 of the section is removed. Transition face and end details (E 706-TTFC) are not supplied. '
                   + base_note,
                   replace={'taper is illustrative. ': 'its section is an envelope. ',
                            ' (taper unchanged)': ''},
                   dims=dict(height_in=33, base_width_in=16, top_width_in=9,
                             rear_face_height_in=round(FC_HEIGHT / IN + 0.32, 2)), pages=[27, 28],
                   basis='Footprint dimensioned (sheet 28); FC section and level top per sheet 27; transition face '
                         'inferred')
            print(f'{pid}: far-end top {rings[far, :, 2].max():.4f} -> {out.reshape(-1, 6, 3)[far, :, 2].max():.4f}; '
                  f'volume {m.volume:.4f} -> {new_tfc.volume:.4f} m3')

    # Interfaces: no corrected part may overlap a neighbour more than it did before.
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
    (backup / 'us421-wildcat_before_review_correction_3.glb').write_bytes(original)
    (backup / 'us421-wildcat_manifest_before_review_correction_3.json').write_bytes(mp.read_bytes())
    path.write_bytes(out)

    for item in manifest.get('detail_coverage', []):
        if item.get('feature') == 'Bearings and substructure':
            if 'stepped replacement caps/seats' not in item['detail']:
                raise ValueError('unexpected substructure coverage text')
            item['detail'] = item['detail'].replace(
                'stepped replacement caps/seats', 'stepped replacement caps/seats (13 ft 4 in abutment steps)')
        elif item.get('feature') == 'Rails and approaches':
            item['detail'] = ('New FC barriers use the p27 section; 20 ft 6 in approach footprint with 4 ft 1 in x '
                              '1 ft 6 in corner cutbacks (p28), 12 in slab including the RCBA extensions (p28 bill of '
                              'materials) thickened to 1 ft 2 in on the 6 in pavement ledge over the full 31 ft '
                              '(pp10, 14, 24, 28); FC and TFC bases follow the 2 % crossfall; TFC envelopes keep the '
                              'FC section and level top (p27) along their 16 ft 5 in RCBA extension; retained metal '
                              'rail profile and the TFC transition face are '
                              'inferred without referenced standards.')
            item['sources'] = sorted(set(item['sources']) | {10, 14, 24, 27, 28})
    manifest['review_correction_3'] = TAG
    manifest['revision'] = REVISION
    manifest['review_correction_3_record'] = dict(
        follows=PREV_TAG,
        source_pdf_pages=[6, 7, 10, 14, 22, 24, 27, 28], printed_sheets=[6, 7, 10, 14, 22, 24, 27, 28],
        corrections={
            'abutment_inner_steps': 'inner bearing step 13 ft 4 in (6 ft 8 in each side of Line "A" = 4 ft 2 in + '
                                    '2 ft 6 in, sheets 10, 14 plans; elevations and sheet 24 agree); was +/-8 ft 6 in. '
                                    'End-diaphragm bottoms follow the step (1/2 in EPS)',
            'ledge_and_seat_length': 'pavement ledge and approach seat over the full 31 ft 0 in diaphragm length, '
                                     'under the RCBA extensions (sheet 24 typical bent diaphragm; sheet 28 plan and '
                                     'bill of materials); was 28 ft 0 in',
            'step_face_eps': 'end-diaphragm step pockets 1 in wider than the step each side (1 in EPS on the vertical '
                             'step faces, 1/2 in on the horizontal; sheet 10 Section B-B, sheet 24 Section C-C)',
            'tfc_height': 'TFC envelopes keep the sheet 27 FC section and level top over the 16 ft 5 in transition '
                          '(sheet 27 elevation, no scale); the illustrative 0.72 taper is removed',
            'rail_bases': 'FC and TFC railing bottoms set on the 2 % deck / approach crossfall (rear bottom edge '
                          'lowered 0.32 in, sheet 27 Section A-A); toe and upper profile unchanged'},
        decisions={
            'step_face_eps': 'The EPS note on sheet 10 Section B-B and sheet 24 Section C-C reads "1/2 in on horizontal '
                             'faces, 1 in on vertical faces"; the sheet 10 and 24 elevations draft the step-face offset '
                             'at about 1/2 in (scaled 0.51-0.53 in). The written note governs: 1 in, as at the wing '
                             'faces ("1 in Expanded Polystyrene", sheets 10, 14).',
            'tfc_transition_face': 'Kept as a known deviation: only the level top and the length are settled by the '
                                   'sheets; the face and end details need E 706-TTFC-01 to -03.'},
        resolved_deviations=['abutment-inner-step-width', 'approach-extension-seat'],
        kept_deviations=['tfc-transition-envelope'],
        changed_parts=changed, added_parts=[], removed_parts=[],
        before_glb_sha256=before, after_glb_sha256=hashlib.sha256(out).hexdigest())
    tfc = deviations['tfc-transition-envelope']
    tfc.update(
        source='sheets 27, 28',
        deviation='The Type TFC transitions are envelopes: the sheet 27 FC section (2 ft 9 in) carried unchanged over '
                  'the 16 ft 5 in RCBA extension, with the level top drawn on the sheet 27 elevation. The elevation (no '
                  'scale) also shows the lower face changing along the transition (the FC knee line runs down to the '
                  'toe, then the toe ends before the far end); that change is not modelled.',
        reason='The transition face geometry, its stations and the end shape are given only in INDOT Standard Drawings '
               'E 706-TTFC-01 to -03, referenced on sheets 27 and 28 but not supplied; the sheet 27 elevation is not '
               'to scale and carries no dimension for them.')
    manifest['known_deviations'] = [tfc]
    text = json.dumps(manifest, ensure_ascii=False, indent=2) + '\n'
    mp.write_bytes(text.replace('\n', newline).encode('utf-8'))      # keep the file's own line endings
    print(json.dumps({k: v for k, v in manifest['review_correction_3_record'].items()
                      if k not in ('corrections', 'decisions')}))
    print(f'{len(changed)} parts changed')


if __name__ == '__main__':
    correct()

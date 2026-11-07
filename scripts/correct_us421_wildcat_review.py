"""One-time, drawing-confirmed correction of US 421 over South Fork Wildcat Creek (us421-wildcat), preserving
unrelated GLB buffers.

    python scripts/correct_us421_wildcat_review.py

Source: drawings.pdf (INDOT 2020 rehabilitation plans, 30 sheets); the printed sheet numbers equal the PDF page
numbers. Native axes: X = station from Sta. 42+54.00, Y = transverse (+Y = X-truss side), Z = elevation - 778 ft.

1. Joint edge beams (sheet 25, Section D-D and "Typical concrete edge beam"; sheet 22 plan). At Piers 2 and 3 the end
   spans end in a concrete edge beam 2 ft 6 in long from the joint face, poured with the deck. Its bottom is 6 in
   below the box-beam tops (Section D-D measures the 6 in from the beam top, the haunch "varies" above it) and runs
   parallel to the 2 % crown; the drop spans between the outer faces of the exterior beams and the slab overhangs
   stay 8 in thick. The model had a 6 in long, level 9 in block whose top met the soffit only at the deck edges
   (3.7 in gap at the crown). Rebuilt with the deck soffit as top, excluding the box beams and their fillets.
2. Semi-integral end diaphragms (sheets 10, 14, 24; Sections A-A/B-B/C-C and the abutment elevations). The diaphragm
   is 2 ft 6 in wide, centred on the bent (1 ft 3 in each side), poured with the deck from the soffit down to the
   cap, on 1/2 in expanded polystyrene over the cap and the inner step. The model stopped 6 in past the bent centre
   line (1 ft 9 in), had a level top (3.7 in gap at the crown) and a level bottom 2 1/2 in (Abutment 1) and about
   3 in (Abutment 4) above the outer cap.
   Rebuilt over the cap width; beam pockets (beam, fillet, bearing pads/EPS below the beam) and the pavement ledge
   part are excluded.
3. Pier pedestal risers (sheets 12, 13, elevations). The three risers are 3 in + 3 ft 8 in + 3 in = 4 ft 2 in wide,
   centred at 0 and +/-8 ft 4 in (El. 797.042 / 797.007); the inner seat (El. 796.542 / 796.507) runs between them
   and the outer seat (El. 796.375 / 796.340) outside them. The model's risers were 4 ft wide and the inner seat
   stopped at the outer risers' centre lines, leaving a 2 in slot under their outer halves. Risers widened to
   4 ft 2 in; inner seat extended to the outer risers' outer faces (+/-10 ft 5 in). Elevations unchanged.
4. Type FC railing (sheet 27, Section A-A): 2 ft 9 in high, 1 ft 4 in base, rear face 2 in inside the deck edge,
   9 in top, traffic face 2 in batter over the upper 1 ft 11 in, 5 in over the next 7 in, then a 3 in vertical toe.
   The model had a 7 in top and the batters shifted 2 in back behind an extra 2 in shelf at the toe. The four FC
   railings are rebuilt with the sheet 27 section. The Type TFC transition envelopes (standard E 706-TTFC not
   supplied) are scaled copies of that section; they take the corrected section with their taper unchanged and are
   cut at the end of their RCBA extension (item 8), 16 ft 5 in from the bridge.
5. Main-span deck drains 1-3 (sheet 26, "Drain Section"): the roadway drain extension pipe ends 6 in below the
   existing bottom chord. The model's pipes ended level with the chord bottom; their outlets are lowered 6 in.
6. Truss identification (sheet 16, outside truss elevation and plan; sheets 2 and 5). The Y-truss panel points are
   numbered from Pier 3: L0-Y/U1-Y are at Pier 3 and L9-Y at Pier 2, so the Y node at the station of node j of the
   X truss is node 9-j. Y-truss names are remapped j -> 9-j (M4 stays M4). Line "A" runs N 47 deg 15 min W with
   increasing station (sheet 5) and Pier 3 is the northwest end (sheet 2, bench mark on Pier Cap No. 3, "northwest
   corner"), so the end-gusset and end-post repairs labelled "west" (Pier 2) and "east" (Pier 3) are renamed to the
   southeast (Pier 2) and northwest (Pier 3) ends.
7. Box-beam numbering (sheet 20 framing plan; sheets 10, 14 abutment plans): Beam No. 1 is on the X-truss side (+Y),
   Beam No. 4 on the Y-truss side. Beams and their fillets, pads, plates and socket rims were numbered 1-4 from -Y;
   names are renumbered 5-i. Part ids are unchanged everywhere.
8. Approach slabs (sheet 28, Plan @ Abutment No. 1, Abutment No. 4 by 180 deg rotation): 28 ft 0 in wide for the
   4 ft 1 in farthest from the bridge, with 1 ft 6 in RCBA extensions for the TFC transitions along the 16 ft 5 in
   next to the bridge (31 ft 0 in). The model was 31 ft wide throughout; the outer 4 ft 1 in x 1 ft 6 in corners
   are removed.

Not changed: the abutment inner step (model +/-8 ft 6 in, sheets 10/14 elevations about +/-6 ft 8 in) was not part of
the review; the diaphragm bottom follows the modelled step and the discrepancy is recorded as a known deviation.

Requires numpy, trimesh and manifold3d.
"""
import hashlib
import json
import re
import struct
from pathlib import Path

import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'data/bridges/us421-wildcat'
FT = 0.3048
IN = FT / 12
TAG = 'edgebeam-diaphragm-riser-fc-drain-approach-names'

EDGE_BEAM_LENGTH = 30 * IN               # 2 ft 6 in from the joint face (sheet 25)
EDGE_BEAM_DROP = 6 * IN                  # below the box-beam top (sheet 25 Section D-D)
EPS = 0.5 * IN                           # expanded polystyrene under the diaphragm (sheet 24 Section C-C)
RISER_HALF = 25 * IN                     # 4 ft 2 in risers (sheets 12-13)
RISER_PITCH = 100 * IN                   # 8 ft 4 in
DRAIN_DROP = 6 * IN                      # below the bottom chord (sheet 26)
APPROACH_NARROW = 49 * IN                # 4 ft 1 in at 28 ft 0 in (sheet 28)
EXTENSION_LENGTH = 197 * IN              # 16 ft 5 in RCBA extension (sheet 28)
ROADWAY_HALF = 14 * FT                   # 28 ft 0 in approach slab between the extensions
FC_TOE, FC_BACK = 4.2672, 4.6736         # |Y| of the FC toe and rear face (15 ft 6 in less 2 in, less 1 ft 4 in)
OLD_FC = [(FC_TOE, 0.0), (FC_BACK, 0.0), (FC_BACK, 0.8382), (4.4958, 0.8382), (4.445, 0.254), (4.318, 0.0762),
          (FC_TOE, 0.0762)]
NEW_FC = [(FC_TOE, 0.0), (FC_BACK, 0.0), (FC_BACK, 33 * IN), (FC_BACK - 9 * IN, 33 * IN),
          (FC_BACK - 11 * IN, 10 * IN), (FC_TOE, 3 * IN)]

# GLB vertices are glTF Y-up: [x, y, z] = [native X, native Z, -native Y].
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


def bodies(mesh):
    """Number of face-connected bodies (union-find over shared vertices; scipy is not required)."""
    parent = list(range(len(mesh.vertices)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    for a, b, c in mesh.faces:
        ra, rb, rc = find(a), find(b), find(c)
        parent[rb] = ra
        parent[find(rc)] = ra
    return len({find(i) for i in np.unique(mesh.faces)})


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


def ear_clip(poly):
    """Triangulate a simple counter-clockwise polygon given as a list of 2-D points."""
    idx = list(range(len(poly)))
    tris = []
    cross = lambda o, a, b: (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    while len(idx) > 3:
        for k in range(len(idx)):
            i0, i1, i2 = idx[k - 1], idx[k], idx[(k + 1) % len(idx)]
            a, b, c = poly[i0], poly[i1], poly[i2]
            if cross(a, b, c) <= 1e-12:
                continue
            if any(cross(a, b, poly[m]) >= 0 and cross(b, c, poly[m]) >= 0 and cross(c, a, poly[m]) >= 0
                   for m in idx if m not in (i0, i1, i2)):
                continue
            tris.append((i0, i1, i2))
            idx.pop(k)
            break
        else:
            raise ValueError('ear clipping failed')
    tris.append(tuple(idx))
    return tris


def profile_solid(stations, profile, sign):
    """Prism through stations [(x, base_z, scale)] of a railing profile [(|Y|, h)], scaled about the toe."""
    n = len(profile)
    pts = []
    for x, base, k in stations:
        for ay, h in profile:
            pts.append((x, sign * (FC_TOE + k * (ay - FC_TOE)), base + k * h))
    faces = []
    for i in range(len(stations) - 1):
        for j in range(n):
            a, b2 = i * n + j, i * n + (j + 1) % n
            faces += [(a, b2, b2 + n), (a, b2 + n, a + n)]
    poly = [(ay, h) for ay, h in profile]
    area = sum(poly[i][0] * poly[(i + 1) % n][1] - poly[(i + 1) % n][0] * poly[i][1] for i in range(n))
    order = list(range(n)) if area > 0 else list(range(n))[::-1]
    tris = [tuple(order[v] for v in tri) for tri in ear_clip([poly[o] for o in order])]
    last = (len(stations) - 1) * n
    faces += [tri[::-1] for tri in tris] + [tuple(last + v for v in tri) for tri in tris]
    solid = oriented(trimesh.Trimesh(np.array(pts, float), np.array(faces), process=False))
    if not solid.is_watertight or not solid.is_winding_consistent or solid.volume <= 0:
        raise ValueError('railing solid invalid')
    return solid


def correct():
    mp = BASE / 'model_manifest.json'
    manifest = json.loads(mp.read_text(encoding='utf-8'))
    newline = '\r\n' if b'\r\n' in mp.read_bytes() else '\n'
    if manifest.get('review_correction') == TAG:
        print('Already corrected.')
        return
    if manifest.get('review_correction'):
        raise ValueError(f'unexpected earlier correction {manifest["review_correction"]}')
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
        prim = meshes[pid]['primitives'][0]
        prim['attributes']['POSITION'] = append(to_glb(vertices).astype('<f4'), 'VEC3', 5126)

    changed = []

    def record(pid, mesh, note, dims=None, pages=None, basis=None, extras=None):
        if not mesh.is_watertight or mesh.volume <= 0 or bodies(mesh) != 1:
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
        p['note'] = (p.get('note', '') + ' ' + note).strip()
        ex = meshes[pid]['extras']
        ex.update(name=p['name'], note=p['note'], basis=p['basis'], pdf_pages=p['pdf_pages'],
                  bounds_m=p['bounds_m'], volume_m3=p['volume_m3'], dimensions=p['dimensions'])
        if extras:
            ex.update(extras)
        changed.append(pid)

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

    beams = {s: [solid(f'box_{s}{i}') for i in range(1, 5)] for s in 'AC'}
    for s in 'AC':
        centres = [round(float(b.bounds[:, 1].mean()), 4) for b in beams[s]]
        if centres != [-3.81, -1.27, 1.27, 3.81]:
            raise ValueError(f'span {s}: unexpected beam lines {centres}')

    # 1. Joint edge beams at Piers 2 and 3 (sheet 25).
    for s, pid in (('A', 'edgebeam_A'), ('C', 'edgebeam_C')):
        old = solid(pid)
        ext = old.extents
        if len(old.vertices) != 8 or abs(ext[0] - 6 * IN) > 5e-4 or abs(ext[2] - 9 * IN) > 5e-4:
            raise ValueError(f'{pid}: unexpected original edge beam')
        deck = solid(f'deck_{s}')
        soffit, deck_xs = soffit_fn(deck)
        if s == 'A':
            face = deck.bounds[1][0]
            x0, x1 = face - EDGE_BEAM_LENGTH, face
            beam_end = max(b.bounds[1][0] for b in beams[s])
            probe = beam_end - 0.005
        else:
            face = deck.bounds[0][0]
            x0, x1 = face, face + EDGE_BEAM_LENGTH
            beam_end = min(b.bounds[0][0] for b in beams[s])
            probe = beam_end + 0.005
        if abs((old.bounds[1][0] if s == 'A' else old.bounds[0][0]) - face) > 1e-4:
            raise ValueError(f'{pid}: joint face mismatch')
        # Haunch at the beam centre lines at the beam end; the bottom is 6 in below the beam tops, parallel to the crown.
        haunches = []
        for b in beams[s]:
            yc = float(b.bounds[:, 1].mean())
            top = b.vertices[np.abs(b.vertices[:, 0] - probe) < 0.2, 2].max()
            haunches.append(soffit(probe, yc) - top)
        haunch = float(np.mean(haunches))
        if not 0.03 < haunch < 0.05 or np.ptp(haunches) > 0.004:
            raise ValueError(f'{pid}: unexpected fillet at the beam ends {haunches}')
        depth = haunch + EDGE_BEAM_DROP
        half = max(b.bounds[1][1] for b in beams[s])
        xs = sorted({x0, x1} | {x for x in deck_xs if x0 + 1e-4 < x < x1 - 1e-4})
        prism = grid_solid(xs, [-half, 0.0, half], soffit, lambda x, y: soffit(x, y) - depth)
        cutters = []
        for b in beams[s]:
            ya, yb = b.bounds[0][1], b.bounds[1][1]
            ya -= 0.05 if abs(ya + half) < 1e-6 else 0.0
            yb += 0.05 if abs(yb - half) < 1e-6 else 0.0
            cx = (x0 - 0.05, beam_end) if s == 'A' else (beam_end, x1 + 0.05)
            cutters.append(box(cx[0], cx[1], ya, yb, 3.0, 9.0))
        new = trimesh.boolean.difference([prism] + cutters, engine='manifold')
        write_solid(pid, new)
        record(pid, new,
               f'Rebuilt per sheet 25: 2 ft 6 in from the joint face, top on the deck soffit, bottom 6 in below the '
               f'box-beam tops ({depth / IN:.1f} in below the soffit) parallel to the 2% crown, between the exterior '
               f'beam faces; box beams and fillets excluded.',
               dims=dict(length_ft=2.5, width_ft=round(2 * half / FT, 3), depth_below_beam_top_in=6,
                         depth_below_deck_soffit_in=round(depth / IN, 2)), pages=[22, 25],
               basis='Dimensioned (sheet 25 Section D-D and typical edge beam)')
        parts[pid]['dimensions'].pop('depth_below_deck_in', None)
        meshes[pid]['extras']['dimensions'] = parts[pid]['dimensions']
        print(f'{pid}: X {x0:.4f}-{x1:.4f}, depth below soffit {depth:.4f} m, volume {new.volume:.4f} m3')

    # 2. Semi-integral end diaphragms (sheets 10, 14, 24).
    for pid, deck_id, cap_id, step_id, ledge_id, span, old_x in (
            ('diaphragm1', 'deck_A', 'abut1_cap', 'abut1_step', 'ledge1', 'A', (-0.381, 0.1524)),
            ('diaphragm4', 'deck_C', 'abut4_cap', 'abut4_step', 'ledge4', 'C', (58.3692, 58.9026))):
        old = solid(pid)
        if not np.allclose(old.bounds[:, 0], old_x, atol=1e-4):
            raise ValueError(f'{pid}: unexpected original extent {old.bounds[:, 0]}')
        cap, step, ledge = solid(cap_id), solid(step_id), solid(ledge_id)
        x0, x1 = cap.bounds[0][0], cap.bounds[1][0]
        if abs(x1 - x0 - 30 * IN) > 1e-4:
            raise ValueError(f'{cap_id}: cap is not 2 ft 6 in wide')
        soffit, deck_xs = soffit_fn(solid(deck_id))
        half = old.bounds[1][1]
        cap_top, step_top, step_half = cap.bounds[1][2], step.bounds[1][2], step.bounds[1][1]
        xs = sorted({x0, x1} | {x for x in deck_xs if x0 + 1e-4 < x < x1 - 1e-4})
        prism = grid_solid(xs, [-half, 0.0, half], soffit, lambda x, y: cap_top + EPS)
        cutters = [box(x0 - 0.05, x1 + 0.05, -step_half, step_half, cap_top - 0.05, step_top + EPS)]
        abut1 = pid == 'diaphragm1'
        for b in beams[span]:
            cx = (b.bounds[0][0], x1 + 0.05) if abut1 else (x0 - 0.05, b.bounds[1][0])
            cutters.append(box(cx[0], cx[1], b.bounds[0][1], b.bounds[1][1], 3.0, 9.0))
        lx0, lx1 = ledge.bounds[0][0], ledge.bounds[1][0]
        lx0, lx1 = (lx0 - 0.05, lx1) if abut1 else (lx0, lx1 + 0.05)
        cutters.append(box(lx0, lx1, ledge.bounds[0][1], ledge.bounds[1][1], ledge.bounds[0][2], ledge.bounds[1][2]))
        new = trimesh.boolean.difference([prism] + cutters, engine='manifold')
        write_solid(pid, new)
        record(pid, new,
               'Rebuilt per sheets 10, 14 and 24: 2 ft 6 in wide over the cap (1 ft 3 in each side of the bent), top '
               'on the deck soffit, bottom 1/2 in (expanded polystyrene) above the cap and inner step; beam pockets '
               'and the pavement-ledge part excluded.',
               dims=dict(length_ft=2.5, eps_over_cap_in=0.5), pages=[10, 14, 24],
               basis='Dimensioned (sheets 10, 14, 24); beam pockets fitted to the beam envelopes')
        print(f'{pid}: X {x0:.4f}-{x1:.4f}, volume {old.volume:.4f} -> {new.volume:.4f} m3')

    # 3. Pier pedestal risers and inner seats (sheets 12, 13).
    for pier, page in ((2, 12), (3, 13)):
        pid = f'pier{pier}_innerstep'
        m = solid(pid)
        v = m.vertices.copy()
        if not np.allclose(np.unique(np.round(v[:, 1], 4)), [-2.542, 2.542]):
            raise ValueError(f'{pid}: unexpected original width')
        outer = RISER_PITCH + RISER_HALF
        v[:, 1] = np.sign(v[:, 1]) * outer
        new = trimesh.Trimesh(v, m.faces, process=False)
        write_positions(pid, v)
        record(pid, new, f'Extended to the outer faces of the outer risers (+/-10 ft 5 in), sheet {page}; no slot '
                         'under the risers.', dims=dict(width_ft=round(2 * outer / FT, 4)), pages=[page],
               extras=dict(extents=new.extents.round(6).tolist()))
        for k, centre in enumerate((-RISER_PITCH, 0.0, RISER_PITCH)):
            pid = f'pier{pier}_key{k}'
            m = solid(pid)
            v = m.vertices.copy()
            if not np.allclose(np.unique(np.round(v[:, 1], 4)), np.round([centre - 0.6096, centre + 0.6096], 4)):
                raise ValueError(f'{pid}: unexpected original riser')
            v[:, 1] = np.where(v[:, 1] > centre, centre + RISER_HALF, centre - RISER_HALF)
            new = trimesh.Trimesh(v, m.faces, process=False)
            write_positions(pid, v)
            record(pid, new, f'Widened to 4 ft 2 in (3 in + 3 ft 8 in + 3 in), sheet {page}.',
                   dims=dict(width_ft=round(2 * RISER_HALF / FT, 4)), pages=[page],
                   extras=dict(extents=new.extents.round(6).tolist()))

    # 4. Type FC railings (sheet 27) and the TFC transition envelopes that reuse the section.
    def stations_of(m, profile_check):
        v = m.vertices
        out = []
        for x in np.unique(np.round(v[:, 0], 6)):
            sec = v[np.isclose(v[:, 0], x, atol=1e-6)]
            base = sec[:, 2].min()
            k = (np.abs(sec[:, 1]).max() - FC_TOE) / (FC_BACK - FC_TOE)
            expect = np.array([(FC_TOE + k * (ay - FC_TOE), k * h) for ay, h in profile_check])
            got = np.column_stack([np.abs(sec[:, 1]), sec[:, 2] - base])
            if len(sec) != len(expect) or max(np.min(np.abs(expect - g).sum(axis=1)) for g in got) > 3e-4:
                raise ValueError('unexpected railing section')
            out.append((float(x), float(base), float(k)))
        return out

    for pid in ('FC_A_-1', 'FC_A_1', 'FC_C_-1', 'FC_C_1'):
        m = solid(pid)
        sign = np.sign(m.vertices[:, 1].mean())
        st = stations_of(m, OLD_FC)
        if any(abs(k - 1) > 1e-4 for _, _, k in st):
            raise ValueError(f'{pid}: unexpected scaled section')
        new = profile_solid(st, NEW_FC, sign)
        write_solid(pid, new)
        record(pid, new, 'Section corrected to sheet 27 Section A-A: 9 in top, 2 in upper batter over 1 ft 11 in, '
                         '5 in lower batter over 7 in, 3 in toe (the extra 2 in toe shelf removed).',
               dims=dict(top_width_in=9, toe_height_in=3, knee_height_in=10, rear_setback_from_deck_edge_in=2),
               pages=[27])

    for pid, bridge_end in (('TFC1_-1', -0.381), ('TFC1_1', -0.381), ('TFC4_-1', 58.9026), ('TFC4_1', 58.9026)):
        m = solid(pid)
        sign = np.sign(m.vertices[:, 1].mean())
        st = sorted(stations_of(m, OLD_FC), key=lambda s_: abs(s_[0] - bridge_end))
        if abs(st[0][0] - bridge_end) > 1e-4 or abs(st[0][2] - 1) > 1e-4 or abs(abs(st[-1][0] - bridge_end) - 20.5 * FT) > 1e-3:
            raise ValueError(f'{pid}: unexpected original transition')
        cut = bridge_end + np.sign(st[-1][0] - bridge_end) * EXTENSION_LENGTH
        keep = [s_ for s_ in st if abs(s_[0] - bridge_end) < EXTENSION_LENGTH - 1e-4]
        dist = [abs(s_[0] - bridge_end) for s_ in st]
        keep.append((float(cut), float(np.interp(EXTENSION_LENGTH, dist, [s_[1] for s_ in st])),
                     float(np.interp(EXTENSION_LENGTH, dist, [s_[2] for s_ in st]))))
        keep.sort(key=lambda s_: s_[0])
        new = profile_solid(keep, NEW_FC, sign)
        write_solid(pid, new)
        record(pid, new, 'Takes the corrected sheet 27 FC section (taper unchanged) and ends with the 16 ft 5 in '
                         'RCBA extension that carries it (sheet 28).',
               dims=dict(length_ft=round(EXTENSION_LENGTH / FT, 4)), pages=[27, 28])

    # 5. Main-span deck drains 1-3 (sheet 26).
    drain_targets = {}
    for n in (1, 2, 3):
        for side in ('X', 'Y'):
            pid = f'drain{n}_{side}_drop'
            m = solid(pid)
            v = m.vertices.copy()
            xc = float(v[:, 0].mean())
            chord = next(c for c in (solid(f'{side}_LC{j}') for j in range(9))
                         if c.bounds[0][0] <= xc <= c.bounds[1][0])
            # Bottom of the chord at the drain station: lowest surface crossing of vertical lines across its width.
            bottom = min(z.min() for z in (vertical_hits(chord, xc, y) for y in
                                           np.linspace(chord.bounds[0][1], chord.bounds[1][1], 11)[1:-1]) if len(z))
            zs = np.unique(np.round(v[:, 2], 5))
            if len(zs) != 2 or abs(zs[0] - bottom) > 2e-4:
                raise ValueError(f'{pid}: outlet not at the chord bottom ({zs[0]} vs {bottom})')
            low = np.isclose(v[:, 2], v[:, 2].min(), atol=1e-5)
            if low.sum() != 48:
                raise ValueError(f'{pid}: unexpected outlet ring')
            target = bottom - DRAIN_DROP
            v[low, 2] = target
            new = trimesh.Trimesh(v, m.faces, process=False)
            write_positions(pid, v)
            record(pid, new, 'Outlet lowered to 6 in below the bottom chord, sheet 26 drain section.',
                   dims=dict(outlet_below_bottom_chord_in=6), pages=[26])
            drain_targets[pid] = round(float(target), 6)
    print('drain outlets:', drain_targets)

    # 8. Approach slab corners (sheet 28).
    for pid, far in (('approach1', -6.6294), ('approach4', 65.151)):
        m = solid(pid)
        if not np.isclose(m.bounds[0][0] if far < 0 else m.bounds[1][0], far, atol=1e-4) or \
                abs(m.bounds[1][1] - 15.5 * FT) > 1e-4 or abs(m.extents[0] - 20.5 * FT) > 1e-3:
            raise ValueError(f'{pid}: unexpected original approach slab')
        xa, xb = (far - 0.05, far + APPROACH_NARROW) if far < 0 else (far - APPROACH_NARROW, far + 0.05)
        cutters = [box(xa, xb, ROADWAY_HALF, 15.5 * FT + 0.05, 5.0, 7.0),
                   box(xa, xb, -15.5 * FT - 0.05, -ROADWAY_HALF, 5.0, 7.0)]
        new = trimesh.boolean.difference([m] + cutters, engine='manifold')
        write_solid(pid, new)
        record(pid, new, 'Outer 4 ft 1 in x 1 ft 6 in corners removed: 28 ft 0 in wide for the 4 ft 1 in farthest from '
                         'the bridge, 31 ft 0 in along the 16 ft 5 in RCBA extensions (sheet 28).',
               dims=dict(width_far_end_ft=28, extension_length_ft=round(EXTENSION_LENGTH / FT, 4)), pages=[28])
        print(f'{pid}: volume {m.volume:.4f} -> {new.volume:.4f} m3')

    # 6-7. Names (manifest names, labels and mesh extras only; part ids unchanged).
    renamed = []

    def rename(pid, name, note=None):
        p = parts[pid]
        p['name'] = name
        if note:
            p['note'] = (p.get('note', '') + ' ' + note).strip()
        meshes[pid]['extras'].update(name=p['name'], note=p['note'])
        renamed.append(pid)

    def y_label(match):
        letter, j = match.group(1), int(match.group(2))
        return f'{letter}{9 - j}' if letter in 'UL' else match.group(0)

    for pid, p in parts.items():
        if not pid.startswith('Y_') or not re.search(r'\b[UL]\d\b', p['name']):
            continue
        name = re.sub(r'\b([ULM])(\d)\b', y_label, p['name'])
        name = re.sub(r'\b([UL])(\d)-([UL])(\d)\b',     # chord pairs in ascending order, as on the X truss
                      lambda mt: (f'{mt.group(3)}{mt.group(4)}-{mt.group(1)}{mt.group(2)}'
                                  if mt.group(1) == mt.group(3) and mt.group(4) < mt.group(2) else mt.group(0)), name)
        rename(pid, name, 'Y-truss panel points numbered from Pier 3 (sheet 16).')
    if parts['Y_V1']['name'] != 'Y-truss vertical U8-L8' or parts['Y_D0']['name'] != 'Y-truss diagonal U8-L7' or \
            parts['Y_LC0']['name'] != 'Y-truss lower chord L8-L9' or parts['Y_L1_gusset-1']['name'] != 'Y L8 existing gusset (-1)':
        raise ValueError('unexpected Y-truss renaming')
    ends = {('X', 'west'): 'X-truss southeast end (Pier 2, L0-X)', ('Y', 'west'): 'Y-truss southeast end (Pier 2, L9-Y)',
            ('X', 'east'): 'X-truss northwest end (Pier 3, L9-X)', ('Y', 'east'): 'Y-truss northwest end (Pier 3, L0-Y)'}
    for pid, p in parts.items():
        mt = re.match(r'repair_(gusset|cover)_([XY])_(west|east)', pid)
        if not mt:
            continue
        truss, end = mt.group(2), mt.group(3)
        xc = sum(p['bounds_m'][k][0] for k in range(2)) / 2
        if (end == 'west') != (xc < 20) or not p['name'].startswith(f'{truss} {end} '):
            raise ValueError(f'{pid}: unexpected end assembly')
        rename(pid, ends[truss, end] + ' ' + p['name'][len(f'{truss} {end} '):],
               'Pier 2 is the southeast end, Pier 3 the northwest end (Line "A" N 47 deg 15 min W, sheet 5; '
               'Pier Cap No. 3 at the northwest corner, sheet 2).')
    note = parts['diagonal_repair_plate']['note']
    if 'west-side diagonal' not in note:
        raise ValueError('diagonal_repair_plate: unexpected note')
    parts['diagonal_repair_plate']['note'] = note.replace('west-side diagonal',
                                                          'diagonal at the southeast (Pier 2) end')
    meshes['diagonal_repair_plate']['extras']['note'] = parts['diagonal_repair_plate']['note']
    renamed.append('diagonal_repair_plate')
    for pid, p in parts.items():
        mt = re.match(r'(box|haunch|pad|plate)_([AC])([1-4])', pid)
        if not mt:
            continue
        span, i = mt.group(2), int(mt.group(3))
        beam_y = beams[span][i - 1].bounds[:, 1]
        if p['bounds_m'][0][1] < beam_y[0] - 1e-3 or p['bounds_m'][1][1] > beam_y[1] + 1e-3:
            raise ValueError(f'{pid}: not on the line of beam {span}{i}')
        name = re.sub(rf'\b{span}{i}\b', f'{span}{5 - i}', p['name'])
        name = re.sub(rf'\bbeam {i}\b', f'Beam No. {5 - i}', name)
        if name == p['name']:
            raise ValueError(f'{pid}: beam number not found in name')
        rename(pid, name, f'Beam No. {5 - i} per sheets 10, 14 and 20 (Beam No. 1 on the X-truss side); the part id '
                          'keeps the original index.')
    if parts['box_A1']['name'] != 'Span A Beam No. 4: CB 17 x 48' or parts['pad_C4_end_2']['name'] != 'C1 end bearing pad 2':
        raise ValueError('unexpected beam renaming')

    while len(binary) % 4:
        binary.append(0)
    gltf['buffers'][0]['byteLength'] = len(binary)
    encoded = json.dumps(gltf, ensure_ascii=True, separators=(',', ':')).encode()
    encoded += b' ' * ((-len(encoded)) % 4)
    out = (struct.pack('<III', 0x46546c67, 2, 28 + len(encoded) + len(binary)) +
           struct.pack('<II', len(encoded), 0x4e4f534a) + encoded + struct.pack('<II', len(binary), 0x004e4942) + binary)
    backup = ROOT / 'data/fem_research'
    backup.mkdir(exist_ok=True)
    (backup / 'us421-wildcat_before_review_correction.glb').write_bytes(original)
    (backup / 'us421-wildcat_manifest_before_review_correction.json').write_bytes(mp.read_bytes())
    path.write_bytes(out)

    for item in manifest.get('detail_coverage', []):
        if item.get('feature') == 'Rails and approaches':
            item['detail'] = ('New FC barriers use the p27 section; 20 ft 6 in approach footprint with 4 ft 1 in x '
                              '1 ft 6 in corner cutbacks (p28); TFC envelopes reuse the FC section and end with their '
                              '16 ft 5 in RCBA extension; slab depth and retained metal rail profile are inferred '
                              'without referenced standards.')
        elif item.get('feature') == 'Bearings and substructure':
            item['sources'] = sorted(set(item['sources']) | {24})
    manifest['review_correction'] = TAG
    manifest['revision'] = '1.1-drawing-review'
    manifest['review_correction_record'] = dict(
        source_pdf_pages=[2, 5, 10, 12, 13, 14, 16, 20, 22, 24, 25, 26, 27, 28],
        printed_sheets=[2, 5, 10, 12, 13, 14, 16, 20, 22, 24, 25, 26, 27, 28],
        corrections={
            'joint_edge_beams': '2 ft 6 in long, bottom 6 in below the box-beam tops parallel to the crown, top on the '
                                'deck soffit, between the exterior beam faces (sheet 25)',
            'end_diaphragms': '2 ft 6 in over the cap, deck soffit to 1/2 in above the cap and step (sheets 10, 14, 24)',
            'pier_risers': 'risers 4 ft 2 in wide at 0 and +/-8 ft 4 in; inner seat to +/-10 ft 5 in (sheets 12, 13)',
            'fc_railing_section': '9 in top, 2 in / 5 in batters, 3 in toe (sheet 27); TFC envelopes take the section',
            'deck_drains': 'drains 1-3 extended to 6 in below the bottom chord (sheet 26)',
            'approach_slabs': '4 ft 1 in x 1 ft 6 in outer corners removed; TFC envelopes end at 16 ft 5 in (sheet 28)',
            'y_truss_numbering': 'Y-truss node labels j -> 9-j (sheet 16)',
            'end_orientation': 'Pier 2 end southeast, Pier 3 end northwest (sheets 2, 5)',
            'beam_numbering': 'Beam No. 1 on the X-truss (+Y) side (sheets 10, 14, 20); names only'},
        drain_outlet_z_m=drain_targets, changed_parts=changed, renamed_parts=renamed,
        before_glb_sha256=before, after_glb_sha256=hashlib.sha256(out).hexdigest())
    deviations = [d for d in manifest.get('known_deviations', [])
                  if d.get('id') not in ('abutment-inner-step-width', 'tfc-transition-envelope')]
    deviations += [
        dict(id='abutment-inner-step-width', parts='abut1_step, abut4_step, diaphragm1, diaphragm4',
             source='sheets 10, 14 (PDF 10, 14) elevations',
             deviation='The raised inner bearing step is modelled +/-8 ft 6 in from the centre line; the abutment '
                       'elevations draw it about 13 ft 4 in long (+/-6 ft 8 in).',
             reason='Not part of the 2026 review; the end diaphragms follow the modelled step.'),
        dict(id='tfc-transition-envelope', parts='TFC1_-1, TFC1_1, TFC4_-1, TFC4_1', source='sheets 27, 28',
             deviation='Type TFC transitions are scaled FC sections tapering to 0.72 of full size over the 16 ft 5 in '
                       'RCBA extension.',
             reason='Standard E 706-TTFC is referenced but not supplied; the envelope is illustrative.')]
    manifest['known_deviations'] = deviations
    text = json.dumps(manifest, ensure_ascii=False, indent=2) + '\n'
    mp.write_bytes(text.replace('\n', newline).encode('utf-8'))      # keep the file's own line endings
    print(json.dumps({k: v for k, v in manifest['review_correction_record'].items()
                      if k not in ('renamed_parts', 'changed_parts')}))
    print(f'{len(changed)} parts changed, {len(renamed)} renamed')


if __name__ == '__main__':
    correct()

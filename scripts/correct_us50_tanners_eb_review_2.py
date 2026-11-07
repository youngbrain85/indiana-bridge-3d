"""Second drawing-confirmed correction of US 50 EB over Tanners Creek (us50-tanners-eb): rectangular interior caps,
tie-beam haunches and the end-bent pavement ledges. Runs after scripts/correct_us50_tanners_eb_review.py and keeps
the GLB buffers of the parts it does not change.

    python scripts/correct_us50_tanners_eb_review_2.py [--base DIR] [--backup DIR]

Source: drawings.pdf, 2014 B-29709 reconstruction. Printed sheet N is PDF page N + 86 (sheet 34 = PDF 120).
Native axes (unchanged by this correction): X along Line "A" stations, Y to the LEFT of increasing station (north),
Z = El. - 450 ft in metres; support lines X = u - tan20 Y (north end at the lower station). Plan coordinates along a
bent are p (along the support line, toward north) and q (normal to it, toward +X), as in the first script.

1. Interior caps, Bents 2-5 (second check, new issue; sheet 34 PLAN): the 74 ft 3 in x 4 ft 6 in caps are drawn as
   rectangles whose ends are square to the bent; the beam lines and coping lines cross them on the skew. The model
   cut the ends parallel to the roadway (constant Y), giving 70/110 degree plan corners that were up to 0.250 m
   off. cap_1 ... cap_4 are rebuilt as rectangles p = -11.165986 ... +11.465414 m (centre-line ends unchanged: beam 1
   3 ft 6 3/4 in from the north end) by q = +/-0.6858 m, between the same soffit and seat levels.
2. Tie beams, Bents 3 and 4 (second check, F5 partial; sheet 39 ELEVATION and detail): the 2 ft 9 in x 4 ft core
   (El. 453.42-457.42) has a 2 ft 0 in radius haunch at each column face, top and bottom: tangent to the core 2 ft
   from the face and to the face at El. 459.42 (3 in below the El. 459.67 column step) and El. 451.42. Clear bays
   20 ft 6 in, 20 ft 6 in and 7 ft 0 in (2 ft 0 in + 3 ft 0 in + 2 ft 0 in). The twelve haunches per tie are added
   to tie_2 / tie_3 at the 2 ft 9 in tie width; the core still runs between the outer column centres.
3. Pavement ledges, Bents 1 and 6 (second check, new issue; sheet 32 PAVEMENT LEDGE DETAIL and SECTION B-B): the
   approach slab is 1 ft 0 in thick, 1 ft 2 in thick over the 1 ft 6 in next to the end-bent back face, and it
   bears on the 6 in ledge at 1 ft 2 1/2 in below the slab top; the back face is 1 ft 10 1/2 in from the bent centre
   line (3 ft 9 in end bent). The model carried the 1 ft 0 in slab onto a ledge 1 ft 0 in below the top, so the
   ledge was 0.0635 m high and the slab 0.0508-0.0635 m thin there. approach_-1 / approach_1 get the 1 ft 2 1/2 in
   ledge strip and the 1 ft 2 in strip (the undimensioned 2 in taper beyond it is a vertical step); cap_0 / cap_5
   are regenerated with the first script's end-bent rule and the thickened slab as the pocket cutter, so the ledge
   drops 0.0635 m and nothing else changes. The 1/2 in polystyrene strips are not modelled (the slab bears on the
   ledge).

Not changed (recorded as known deviations): the east terminal-joint station callout (Sta. 391+92.68 on sheet 60,
391+92.86 on sheet 22) disagrees with the dimensioned slab edges, which agree with each other and with the west
callout (386+34.06); the model keeps the dimensioned edges. The deck ends are 9.5 mm short of the 492 ft 0 7/8 in
length (sheets 20-22) at each end. The wingwalls, interior support diaphragms and bearing-seat schedule keep their
earlier known deviations.

Requires numpy, trimesh, manifold3d and shapely, plus scripts/correct_us50_tanners_eb_review.py (rules and helpers).
"""
import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

import manifold3d
import numpy as np
import shapely.geometry as sg
import shapely.ops as so
import trimesh

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import correct_us50_tanners_eb_review as first  # noqa: E402

BID = first.BID
BASE = ROOT / 'data/bridges' / BID
BACKUP = ROOT / 'data/fem_research'
TAG = 'review-2026-11-2-rectangular-caps-tie-haunches-pavement-ledges'
PREVIOUS_REVISION = first.REVISION
REVISION = '1.2-drawing-review-2'

FT, IN, C, K, T = first.FT, first.IN, first.C, first.K, first.T
BS, L, W = first.BS, first.L, first.W
CAP_HALF_WIDTH = 4.5 * FT / 2              # sheet 34: interior caps 4 ft 6 in
TIE_WIDTH = 2.75 * FT                      # sheet 39: 2 ft 9 in
HAUNCH_R = 2 * FT                          # sheet 39: 2 ft 0 in haunch radius, top and bottom
LOWER_COLUMN = 4.5 * FT                    # sheet 39: Bents 3/4 columns 4 ft 6 in square below El. 459.67
ARC_SEGMENTS = 12
BACK_FACE = (1 + 10.5 / 12) * FT           # sheet 32: end-bent back face 1 ft 10 1/2 in from the bent centre line
THICK_ZONE = 1.5 * FT                      # sheet 32: 1 ft 6 in thickened slab behind the back face
LEDGE_DEPTH = (1 + 2.5 / 12) * FT          # sheet 32: ledge 1 ft 2 1/2 in below the slab top
THICK_DEPTH = (1 + 2 / 12) * FT            # sheet 32: 1 ft 2 in slab next to the ledge
SLAB_DEPTH = FT                            # sheet 32: 1 ft 0 in approach slab
SOURCE_PAGES = [106, 108, 118, 120, 125, 144, 146]
PRINTED_SHEETS = [p - 86 for p in SOURCE_PAGES]


# ---- Geometry rules. ----
def rect_cap(bi, z0, z1):
    """Interior cap: rectangle in plan, ends square to the bent (sheet 34)."""
    y0, y1 = first.cap_extent(bi)
    p0, p1 = y0 / C, y1 / C
    return first.loft([(p0, z0), (p1, z0), (p1, z1), (p0, z1)], [-CAP_HALF_WIDTH, CAP_HALF_WIDTH],
                      lambda q, p, z: (*first.bent_point(bi, p, q), z))


def cap_plan(bi):
    y0, y1 = first.cap_extent(bi)
    return sg.Polygon([first.bent_point(bi, p, q) for p, q in ((y0 / C, -CAP_HALF_WIDTH), (y0 / C, CAP_HALF_WIDTH),
                                                                 (y1 / C, CAP_HALF_WIDTH), (y1 / C, -CAP_HALF_WIDTH))])


def clip_to_cap(bi, mesh):
    """A flat-topped seat pedestal cut back to the square cap end (it represents a step of the cap top); None if it
    already lies within the cap."""
    v = np.asarray(mesh.vertices)
    z0, z1 = v[:, 2].min(), v[:, 2].max()
    plan = sg.MultiPoint([tuple(c) for c in v[:, :2]]).convex_hull
    kept = plan.intersection(cap_plan(bi))
    if kept.area > plan.area - 1e-9:
        return None
    if kept.geom_type != 'Polygon' or kept.area < .5 * plan.area:
        raise ValueError(f'cap_{bi}: pedestal mostly beyond the cap end')
    profile = [tuple(map(float, c)) for c in sg.polygon.orient(kept.simplify(0)).exterior.coords[:-1]]
    return first.loft(profile, [z0, z1], lambda z, x, y: (x, y, z))


def tie_profile(bi):
    """(p, z) outline of the tie along the bent: core between the outer column centres plus a 2 ft radius haunch at
    every column face that bounds a bay, top and bottom (sheet 39)."""
    pc = np.sort(first.new_column_ys(bi) / C)[::-1]                    # north to south
    z0, z1 = map(float, first.z_el(first.TIE_EL))
    a, r = LOWER_COLUMN / 2, HAUNCH_R
    shapes = [sg.box(pc[-1], z0, pc[0], z1)]
    for j in range(3):
        for face, d in ((pc[j] - a, -1.0), (pc[j + 1] + a, 1.0)):      # d points from the face into the bay
            for zc, zs in ((z1 + r, z1), (z0 - r, z0)):
                start = np.arctan2(0.0, -d)                            # (face, zc) seen from the arc centre
                stop = np.arctan2(zs - zc, 0.0)                        # (face + d r, zs) seen from the centre
                if stop - start > np.pi:
                    stop -= 2 * np.pi
                elif start - stop > np.pi:
                    stop += 2 * np.pi
                th = np.linspace(start, stop, ARC_SEGMENTS + 1)
                arc = [(face + d * r + r * np.cos(t), zc + r * np.sin(t)) for t in th]
                arc[0], arc[-1] = (face, zc), (face + d * r, zs)
                shapes.append(sg.Polygon([(face, zs)] + arc))
    outline = so.unary_union(shapes)
    if outline.geom_type != 'Polygon' or len(outline.interiors):
        raise ValueError(f'tie_{bi}: haunch outline is not a single polygon')
    return [tuple(map(float, c)) for c in outline.exterior.coords[:-1]], len(shapes) - 1


def tie(bi):
    profile, n = tie_profile(bi)
    if n != 12:
        raise ValueError(f'tie_{bi}: expected 12 haunches')
    return first.loft(profile, [-TIE_WIDTH / 2, TIE_WIDTH / 2], lambda q, p, z: (*first.bent_point(bi, p, q), z))


def loft_sections(sections):
    """Closed solid through planar sections at constant Y (same vertex count each), caps triangulated per end."""
    k = len(sections[0])
    vertices = np.vstack(sections)
    side = []
    for i in range(len(sections) - 1):
        a0, b0 = i * k, (i + 1) * k
        for j in range(k):
            jj = (j + 1) % k
            side += [(a0 + j, a0 + jj, b0 + jj), (a0 + j, b0 + jj, b0 + j)]
    caps = []
    for idx, outward in ((0, -1.0), (len(sections) - 1, 1.0)):
        pts = np.asarray(sections[idx])[:, [0, 2]]
        tri = np.asarray(manifold3d.triangulate([pts if _area(pts) > 0 else pts[::-1]]), dtype=np.int64)
        if _area(pts) <= 0:
            tri = k - 1 - tri
        tri = tri + idx * k
        p = vertices[tri]
        normal_y = ((p[:, 1] - p[:, 0])[:, [2, 0]] * (p[:, 2] - p[:, 0])[:, [0, 2]]).dot([1, -1])  # (z1 x2 - x1 z2)
        caps.append(np.where((normal_y * outward < 0)[:, None], tri[:, ::-1], tri))
    caps = np.vstack(caps)
    for faces in (np.array(side), np.array(side)[:, ::-1]):
        mesh = trimesh.Trimesh(vertices=vertices, faces=np.vstack([faces, caps]), process=False)
        if mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0:
            return mesh
    raise ValueError('invalid section loft')


def _area(pts):
    return 0.5 * np.sum(pts[:, 0] * np.roll(pts[:, 1], -1) - np.roll(pts[:, 0], -1) * pts[:, 1])


def approach(g, side, ledge_back=BACK_FACE):
    """Approach slab of the first correction (same top vertices, square terminal joint) with the sheet 32 pavement
    ledge: 1 ft 2 1/2 in over the ledge up to the back face, 1 ft 2 in for 1 ft 6 in behind it, then 1 ft 0 in.
    ledge_back > BACK_FACE gives the cutter for the end-bent pocket (the ledge level carried past the back face)."""
    bi = 0 if side < 0 else 5
    start = side * (L / 2 + .025)
    terminal = side * (L / 2 + .025 + T * W / 2 + first.APPROACH_SHORT)
    longest = abs(terminal - g.sx(start, side * W / 2))
    s_top = first.bars(0, 1, step=.6 / longest)

    def s_at(n, y):                          # slab parameter of the line n from the bent centre line
        x0 = g.sx(start, y)
        return (BS[bi] + side * n / C + K * y - x0) / (terminal - x0)
    ys = [-W / 2, g.crown, W / 2]
    s_far = max(s_at(ledge_back + THICK_ZONE, y) for y in ys)
    s_bottom = [s for s in s_top[::-1] if s > s_far + .02]
    sections = []
    for y in ys:
        x0 = g.sx(start, y)
        n1, n2 = s_at(ledge_back, y), s_at(ledge_back + THICK_ZONE, y)
        if not 0 < n1 < n2 < s_bottom[-1]:
            raise ValueError('approach: ledge strips out of order')
        pts = [(s, 0.0) for s in s_top] + [(s, -SLAB_DEPTH) for s in s_bottom] + \
              [(n2, -SLAB_DEPTH), (n2, -THICK_DEPTH), (n1, -THICK_DEPTH), (n1, -LEDGE_DEPTH), (0.0, -LEDGE_DEPTH)]
        sec = []
        for s, b in pts:
            x = x0 + s * (terminal - x0)
            sec.append((x, y, float(g.surf(x, y)) + b))
        sections.append(np.array(sec))
    return loft_sections(sections)


def end_bent(g, bi, approach_cutter):
    """The first script's semi-integral end bent with the given approach slab as the pocket cutter."""
    i, e = (0, 'start') if bi == 0 else (4, 'end')
    peds = first.peds(g, bi)
    groups = []
    for j in range(7):
        pad = first.bearing(g, i, j, e).bounds
        grp = [first.beam(g, i, j), first.haunch(g, i, j, lift=.05, drop=.02),
               first.box(*pad[:, 0], *pad[:, 1], pad[0, 2], pad[1, 2] + .01)]
        if f'ped_{bi}_{j}_0' in peds:
            ped = peds[f'ped_{bi}_{j}_0'].copy()
            ped.vertices[np.isclose(ped.vertices[:, 2], ped.vertices[:, 2].max()), 2] += .005
            grp.append(ped)
        groups.append(grp)
    groups.append([approach_cutter])
    return first.end_body(g, bi, groups)


def overlap(a, b):
    origin = np.asarray(a.vertices).min(axis=0)
    return (first.to_manifold(a, origin) ^ first.to_manifold(b, origin)).volume()


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
    expect(before == manifest['drawing_review_correction_record']['after_glb_sha256'],
           'GLB differs from the first correction')
    length = struct.unpack_from('<I', original, 12)[0]
    gltf = json.loads(original[20:20 + length])
    binary = bytearray(original[28 + length:])
    parts = {p['id']: p for p in manifest['parts']}
    meshes = {m['name']: m for m in gltf['meshes']}
    expect(set(parts) == set(meshes) and len(parts) == 283, 'part list')

    def read(ai):
        a = gltf['accessors'][ai]
        view = gltf['bufferViews'][a['bufferView']]
        dtype = {5126: '<f4', 5125: '<u4', 5123: '<u2', 5121: 'u1'}[a['componentType']]
        count = {'SCALAR': 1, 'VEC3': 3, 'VEC4': 4}[a['type']]
        return np.frombuffer(binary, dtype=dtype, count=a['count'] * count,
                             offset=view.get('byteOffset', 0) + a.get('byteOffset', 0)).copy().reshape(-1, count)

    def stored(pid):
        prim = meshes[pid]['primitives'][0]
        v = read(prim['attributes']['POSITION']).astype(np.float64)
        return trimesh.Trimesh(vertices=np.c_[v[:, 0], -v[:, 2], v[:, 1]],
                               faces=read(prim['indices']).reshape(-1, 3).astype(np.int64), process=False)

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

    g = first.Geom(True)
    seats = {bi: first.seat(g, bi) for bi in range(1, 5)}
    soffit = {bi: float(first.z_el(first.SOFFIT_EL[bi])) for bi in range(6)}

    # ---- The stored parts must be exactly what the first correction produced. ----
    current = {f'cap_{bi}': first.transverse(g, BS[bi], 4.5 * FT, *first.cap_extent(bi), soffit[bi], seats[bi])
               for bi in range(1, 5)}
    current.update({f'tie_{bi}': first.new_tie(bi) for bi in (2, 3)})
    current.update({f'approach_{s}': first.approach(g, s) for s in (-1, 1)})
    for bi in range(1, 5):
        current.update(first.peds(g, bi))
    current.update({f'cap_{bi}': end_bent(g, bi, current[f'approach_{s}']) for bi, s in ((0, -1), (5, 1))})
    for pid, mesh in current.items():
        expect(first.same_shape(mesh, stored(pid)), f'{pid} is not the first-correction geometry')

    # ---- Corrected geometry. ----
    out = {f'cap_{bi}': rect_cap(bi, soffit[bi], seats[bi]) for bi in range(1, 5)}
    for bi in range(1, 5):
        for pid, ped in first.peds(g, bi).items():
            clipped = clip_to_cap(bi, ped)
            if clipped is not None:
                out[pid] = clipped
    out.update({f'tie_{bi}': tie(bi) for bi in (2, 3)})
    out.update({f'approach_{s}': approach(g, s) for s in (-1, 1)})
    for bi, s in ((0, -1), (5, 1)):
        out[f'cap_{bi}'] = end_bent(g, bi, approach(g, s, ledge_back=BACK_FACE + .15))
    for pid, m in out.items():
        expect(m.is_watertight and m.is_winding_consistent and m.volume > 0, f'{pid} corrected mesh invalid')

    # Interfaces: slab on the ledge without overlap; caps still carry the columns, bearings and pedestals.
    checks = {}
    for bi, s in ((0, -1), (5, 1)):
        v = overlap(out[f'cap_{bi}'], out[f'approach_{s}'])
        expect(v < 1e-5, f'cap_{bi} overlaps approach_{s} by {v:.2e} m3')
        checks[f'cap_{bi}/approach_{s} overlap m3'] = round(v, 9)
    cap_y0, cap_y1 = first.cap_extent(1)
    for bi in range(1, 5):
        for j in range(4):
            col = stored(f'column_{bi}_{j}')
            ztop = col.vertices[:, 2].max()
            top = col.vertices[np.isclose(col.vertices[:, 2], ztop, atol=1e-4)]
            p = (top[:, 0] - BS[bi]) * K * C + top[:, 1] * C
            q = ((top[:, 0] - BS[bi]) - K * top[:, 1]) * C
            expect(abs(ztop - soffit[bi]) < 1e-4 and np.all(np.abs(q) < CAP_HALF_WIDTH) and
                   np.all((p > cap_y0 / C) & (p < cap_y1 / C)), f'column_{bi}_{j} top not under cap_{bi}')
    worst = {'ped': 0.0, 'Span': 0.0}
    for pid in parts:
        if not pid.startswith(('Span_', 'ped_')):
            continue
        if pid.startswith('ped_'):
            bi = int(pid.split('_')[1])
        else:
            i, e = ord(pid[5]) - 65, pid.split('_')[-2]
            bi = i if e == 'start' else i + 1
        if bi in (0, 5):
            continue
        v = np.asarray((out[pid] if pid in out else stored(pid)).vertices)
        beyond = sg.MultiPoint([tuple(c) for c in v[:, :2]]).convex_hull.difference(cap_plan(bi))
        reach = max((cap_plan(bi).exterior.distance(sg.Point(c)) for c in beyond.exterior.coords),
                    default=0.0) if beyond.geom_type == 'Polygon' and not beyond.is_empty else 0.0
        key = pid.split('_')[0]
        worst[key] = max(worst[key], reach)
    expect(worst['ped'] < 1e-6, f'a pedestal overhangs a cap end by {worst["ped"]:.4f} m')
    expect(worst['Span'] < .03, f'a bearing corner overhangs a cap end by {worst["Span"]:.4f} m')
    checks['largest bearing-pad corner overhang beyond an interior cap end m'] = round(worst['Span'], 4)

    # ---- Manifest notes and dimensions. ----
    def note(pid, text):
        p = parts[pid]
        p['note'] = (p.get('note', '') + ' ' + text).strip()

    def add_pages(pid, *pages):
        parts[pid]['pdf_pages'] = sorted(set(parts[pid].get('pdf_pages', [])) | set(pages))

    y0, y1 = first.cap_extent(1)
    for bi in range(1, 5):
        pid = f'cap_{bi}'
        parts[pid]['dimensions'].update(width_m=round(2 * CAP_HALF_WIDTH, 6), plan_shape='rectangle, ends square to the bent',
                                        p_range_along_bent_m=[round(y0 / C, 6), round(y1 / C, 6)])
        parts[pid]['basis'] = 'Dimensioned 74 ft 3 in x 4 ft 6 in rectangular cap (sheet 34); flat seat at the lowest bearing'
        note(pid, 'Rev. 1.2: ends square to the bent, rectangular in plan (sheet 34 PLAN); were cut parallel to the '
                  'roadway (70/110 degree corners, up to 0.250 m off).')
        add_pages(pid, 120)
    for bi in (2, 3):
        pid = f'tie_{bi}'
        parts[pid]['dimensions'].update(haunch_radius_m=round(HAUNCH_R, 6), haunch_count=12,
                                        haunch_top_el_ft=round(first.TIE_EL[1] + 2, 2),
                                        haunch_bottom_el_ft=round(first.TIE_EL[0] - 2, 2))
        parts[pid]['basis'] = 'Dimensioned tie beam with 2 ft radius haunches at the column faces (sheet 39)'
        note(pid, 'Rev. 1.2: 2 ft 0 in radius haunches added at every column face, top and bottom, reaching El. '
                  '459.42 / 451.42 at the faces (sheet 39 elevation and detail).')
    for pid in sorted(p for p in out if p.startswith('ped_')):
        parts[pid]['basis'] = 'Derived contact envelope, cut back to the square cap end'
        note(pid, 'Rev. 1.2: cut back to the square end of the rectangular cap (sheet 34).')
        add_pages(pid, 120)
    for s in (-1, 1):
        pid = f'approach_{s}'
        parts[pid]['dimensions'].update(ledge_thickness_m=round(LEDGE_DEPTH, 6), thickened_thickness_m=round(THICK_DEPTH, 6),
                                        thickened_length_m=round(THICK_ZONE, 6))
        parts[pid]['note'] = parts[pid]['note'].replace('End transitions and local pavement ledges are not resolved. ',
                                                        'End transitions are not resolved. ')
        note(pid, 'Rev. 1.2: sheet 32 pavement ledge: 1 ft 2 1/2 in thick over the end-bent ledge, 1 ft 2 in for 1 ft '
                  '6 in behind the back face (2 in taper as a step), 1 ft 0 in beyond; was 1 ft 0 in throughout.')
        add_pages(pid, 118)
    for bi in (0, 5):
        pid = f'cap_{bi}'
        parts[pid]['dimensions']['pavement_ledge_below_slab_top_m'] = round(LEDGE_DEPTH, 6)
        note(pid, 'Rev. 1.2: 6 in pavement ledge lowered 0.0635 m to 1 ft 2 1/2 in below the approach-slab top (sheet 32).')
        add_pages(pid, 118)

    # ---- Write the changed meshes. ----
    for pid, m in out.items():
        prim = meshes[pid]['primitives'][0]
        color = read(prim['attributes']['COLOR_0'])[0]
        v = np.asarray(m.vertices, dtype=np.float64)
        prim['attributes'] = {'POSITION': append(np.c_[v[:, 0], v[:, 2], -v[:, 1]].astype('<f4'), 'VEC3', 5126),
                              'COLOR_0': append(np.tile(color, (len(v), 1)).astype('u1'), 'VEC4', 5121)}
        gltf['accessors'][prim['attributes']['COLOR_0']]['normalized'] = True
        prim['indices'] = append(np.asarray(m.faces).reshape(-1, 1).astype('<u4'), 'SCALAR', 5125)
        p = parts[pid]
        p['bounds_m'] = np.round(m.bounds, 6).tolist()
        p['volume_m3'] = round(float(m.volume), 9)
        meshes[pid]['extras'].update({k: p[k] for k in ('name', 'basis', 'note', 'dimensions', 'pdf_pages')})

    while len(binary) % 4:
        binary.append(0)
    gltf['buffers'][0]['byteLength'] = len(binary)
    encoded = json.dumps(gltf, ensure_ascii=True, separators=(',', ':')).encode()
    encoded += b' ' * ((-len(encoded)) % 4)
    result = (struct.pack('<III', 0x46546c67, 2, 28 + len(encoded) + len(binary)) +
              struct.pack('<II', len(encoded), 0x4e4f534a) + encoded + struct.pack('<II', len(binary), 0x004e4942) + binary)
    backup.mkdir(parents=True, exist_ok=True)
    (backup / f'{BID}_before_review_correction_2.glb').write_bytes(original)
    (backup / f'{BID}_manifest_before_review_correction_2.json').write_bytes(raw_manifest)
    path.write_bytes(result)

    manifest['drawing_review_correction_2'] = TAG
    manifest['revision'] = REVISION
    manifest['drawing_review_correction_2_record'] = dict(
        source_pdf_pages=SOURCE_PAGES, printed_sheets=PRINTED_SHEETS, previous_revision=PREVIOUS_REVISION,
        native_axes='Unchanged: X along Line "A" stations, Y left of increasing station (north), Z = El. - 450 ft (m)',
        findings={
            'interior caps (new)': 'confirmed - cap_1..cap_4 rectangular, ends square to the bent, p = '
                                   f'{y0 / C:.6f} .. {y1 / C:.6f} m by q = +/-0.6858 m (sheet 34)',
            'F5 tie haunches': 'confirmed - 2 ft 0 in radius haunches at the column faces, top and bottom (sheet 39)',
            'pavement ledges (new)': 'confirmed - ledge 1 ft 2 1/2 in below the slab top (was 1 ft 0 in), slab '
                                     '1 ft 2 1/2 in / 1 ft 2 in / 1 ft 0 in (sheet 32)',
            'F6 terminal station': 'rejected - the dimensioned edges (20 ft 6 in, 46 ft 9 1/4 in, 36 ft 5 7/8 in at '
                                   'the construction joint) and the west callout 386+34.06 agree; the east callout '
                                   '391+92.68 (sheet 60) / 391+92.86 (sheet 22) does not (known deviation)',
            'deck length (minor)': 'not changed - 9.5 mm short at each end (known deviation)',
            'F2 wingwalls, F4 support diaphragms, F7 seat schedule': 'unchanged known deviations'},
        checks=checks, changed_parts=sorted(out),
        before_glb_sha256=before, after_glb_sha256=hashlib.sha256(result).hexdigest())
    new_ids = ('approach-east-terminal-station', 'deck-end-length')
    deviations = [d for d in manifest.get('known_deviations', []) if d.get('id') not in new_ids]
    deviations += [
        dict(id='approach-east-terminal-station', parts='approach_1', source='sheets 22, 58, 60 (PDF 108, 144, 146)',
             deviation='The east terminal joint is at Sta. 391+93.46 "A" against the callout 391+92.68 (sheet 60) / '
                       '391+92.86 (sheet 22).',
             reason='The callouts disagree with each other and with the dimensioned slab (20 ft 6 in and 46 ft 9 1/4 in '
                    'edges, 36 ft 5 7/8 in at the construction joint 3 ft 3 in north of Line "A"), which the model '
                    'follows; the west terminal matches its callout 386+34.06 within 0.05 ft.'),
        dict(id='deck-end-length', parts='deck, sidewalk, ft_rail, ps1_*, joint_-1, joint_1',
             source='sheets 20-22, 32 (PDF 106-108, 118)',
             deviation='The deck is 492 ft 0 1/8 in long (149.9648 m) against 492 ft 0 7/8 in; each end is 9.5 mm '
                       'short of the 1 ft 4 1/2 in from the end-bent centre line.',
             reason='Below modelling tolerance; correcting it would move eight parts by 9.5 mm.')]
    manifest['known_deviations'] = deviations
    text = json.dumps(manifest, ensure_ascii=False, indent=2) + '\n'
    mp.write_bytes(text.encode('utf-8'))
    print(json.dumps({k: v for k, v in manifest['drawing_review_correction_2_record'].items() if k != 'findings'},
                     indent=1))
    print(f'{len(out)} parts changed: {sorted(out)}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--base', type=Path, default=BASE, help='bridge folder (default: the repository copy)')
    parser.add_argument('--backup', type=Path, default=BACKUP, help='backup folder')
    args = parser.parse_args()
    correct(args.base, args.backup)

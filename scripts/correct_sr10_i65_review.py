"""One-time, drawing-confirmed corrections of SR 10 over I-65 (sr10-i65) from the external model review, preserving
unrelated GLB buffers.

    python scripts/correct_sr10_i65_review.py

Source: drawings.pdf, the local review binder. PDF pages 21-40 are the 1998 B-23753 rehabilitation plans, printed
sheet n = PDF page n + 20. Local Z = plan elevation - 210.000 m (the deck and stem elevations confirm this datum).

1. Pier 3 seat stack (sheets 12, 13, 14, 16 / PDF 32, 33, 34, 36). Sheet 12 elevation: cap top El. 215.835 at the
   new cap ends and the outer existing cap, El. 215.879 on the raised central part of the existing hammerhead (not
   dimensioned; it scales 5.31 m, the 5.334 m central width dimensioned for Piers 2/4 on sheet 11 is used), 915 mm
   deep cap ends, 5257 mm columns from El. 209.663, so the column tops are at El. 214.920. Sheet 14: the fixed shoe
   assembly is 260 mm (50 mm base plate and 155 mm block, 55 mm top shoe) at both the existing and the new beams,
   with a shim plate between the top shoe and the beam; sheet 16 shim table, Pier 3, beam lines 1-9: 49, 13, 32, 13,
   26, 13, 32, 13, 49 mm. Sheet 13 beam elevations show the splice cover plate under the bottom flange at the Pier 3
   centre line, and sheet 14 notes the open holes in the splice plates for attaching the top shoes, so the shim bears
   on the 13 mm cover plate of the model's splice envelope. The model had its cap 181 mm low (Z 5.654), 460 mm shoes
   at the outer beams and derived seat risers. The cap, cap ends, column tops and the nine shoes are rebuilt to the
   drawing; the seven seat risers B3_seat_1..7 become the shim plates of beam lines 2-8 and two parts are added for
   lines 1 and 9 (B3_seat_0, B3_seat_8, following the B2_seat_0 id pattern). The beam bottoms at Pier 3 then sit
   2-47 mm higher than the model's nominal profile (1998 grade less a constant 75 mm haunch); spans B and C beams,
   haunch bottoms, splices and diaphragm rows are raised by that amount at Pier 3 (constant over the 1.13 m splice),
   tapering linearly to zero at Piers 2 and 4, which are not changed (their own seat stack mismatch is recorded as a
   known deviation).
2. Pier 3 splice location (sheet 13 / PDF 33): "C/L Pier No. 3 & C/L Splice"; the 457 mm on the framing plan locates
   the diaphragm row west of the pier. The nine centre splices and their fasteners move from X = +0.457 to X = 0.
3. Span C diaphragm rows (sheet 13): the chain 457 + 7061 + 6604 + 6833 = 20 955 mm starts at the diaphragm 457 mm
   west of Pier 3, so the rows are at 6.604 m and 13.208 m east of Pier 3 (mirror of Span B), not 7.061 / 13.665 m.
4. Integral end-bent tops (sheet 9 / PDF 29): the bent elevation is crowned (El. 217.153 at the edges, 217.307 at the
   crown) and section A-A closes the bent concrete against the floor slab; the model's top ran straight between the
   edges, leaving a gap of up to 160 mm under the crowned deck. The top now follows the deck soffit with a crown
   crease; the outer 150 mm beyond the deck end (sheet 9 section A-A, 150 mm to the Type IA joint; 2026 sheet 13 /
   PDF 61, 6 in pavement ledge) is the pavement ledge, closed to the soffit of the 1'-2" approach slab (2026 sheet 13).
   The 1998 ledge El. 216.850 is about 0.10 m below that soffit; the 2026 approach slab governs the model.
5. Wingwalls (sheet 9 plan of Bent 5, north to the left): each 3.7 m wing extends 1600 mm toward the approach and
   2100 mm toward the span from the bent centre line. The model had them reversed; they move 0.5 m spanward.
6. Pier 3 collision walls (sheet 12 elevation and footing plan): 4980 mm walls projecting 300 mm beyond the outer
   column face, with a 25 mm preformed joint against the 5716 mm stem: Y = 2.883-7.863 m (model 3.000-7.620 m).
7. End-span diaphragms (sheets 13, 15 / PDF 33, 35): "New MC460x63.5 Diaphragm (Typ.) (Span A & D)"; the model had
   two bays of every row as 380 mm channels. Bays 2 and 7 of the six Span A/D rows (incl. the Pier 2/4 rows) are
   deepened to 460 mm, downward from their unchanged tops, like the other channels of the row.
8. Bridge railing (sheet 19 / PDF 39 section A-A; "Existing Concrete Barrier Railing" on 2026 sheet 11 / PDF 59):
   400 mm base, 100 mm vertical toe, break 125 mm in at 280 mm, 225 mm top at 840 mm. The model had a 254 mm toe,
   no break and a 240 mm top.

Requires numpy, trimesh and shapely (2.1 or later); uses box/concat from scripts/bridge_geometry.py.
"""
import hashlib
import json
import struct
import sys
from pathlib import Path

import numpy as np
import shapely
import trimesh

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from bridge_geometry import box, concat  # noqa: E402

BID = 'sr10-i65'
BASE = ROOT / 'data/bridges' / BID
TAG = 'pier3-stack-splices-diaphragms-endbents-wings-walls-rails'
REVISION = '1.1-drawing-review'

FT, IN = .3048, .0254
SPANS = np.array([39 + .5 / 12, 65.75, 65.75, 39 + .5 / 12]) * FT     # as built by build_indiana_batch3.sr10
BS = np.r_[0, np.cumsum(SPANS)] - SPANS.sum() / 2                     # support centre lines
LENGTH = (211 + 2.75 / 12) * FT
WIDTH = (50 + 3.625 / 12) * FT
SLAB, CLEAR = .2, .075
YS = np.array([-7.113, -5.080, -3.556, -1.778, 0, 1.778, 3.556, 5.080, 7.113])
DEPTH = np.array([.84] + [.92] * 7 + [.84])
APPROACH_T = 14 * IN                                                  # 2026 sheet 13 (PDF 61), 1'-2" approach


def sweep(profile, stations, fn):
    """Closed prism through `stations`, like bridge_geometry.sweep but without its earcut/graph dependencies.

    Profile points (a, b) are mapped by fn(station, a, b) -> (x, y, z); the caps use a constrained Delaunay
    triangulation of the profile and the solid is oriented by its signed volume.
    """
    pts = [(float(a), float(b)) for a, b in profile]
    poly = shapely.Polygon(pts)
    if not poly.is_valid or poly.area <= 0:
        raise ValueError('invalid sweep profile')
    sign = 1 if poly.exterior.is_ccw else -1
    caps = []
    for tri in shapely.get_parts(shapely.constrained_delaunay_triangles(poly)):
        ring = list(tri.exterior.coords)[:3]
        q = [int(np.argmin([(x - a) ** 2 + (y - b) ** 2 for a, b in pts])) for x, y in ring]
        (ux, uy), (vx, vy) = np.subtract(pts[q[1]], pts[q[0]]), np.subtract(pts[q[2]], pts[q[0]])
        area = ux * vy - uy * vx
        caps.append(q if area * sign > 0 else q[::-1])
    caps = np.array(caps)
    n, last = len(pts), (len(stations) - 1) * len(pts)
    vertices = np.array([fn(float(s), a, b) for s in stations for a, b in pts], dtype=np.float64)
    sides = []
    for k in range(len(stations) - 1):
        for j in range(n):
            a, b = k * n + j, k * n + (j + 1) % n
            sides += [(a, b, b + n), (a, b + n, a + n)]
    for flip in (False, True):
        c = caps[:, ::-1] if flip else caps
        mesh = trimesh.Trimesh(vertices, np.vstack([sides, c[:, ::-1], c + last]), process=False)
        if mesh.is_winding_consistent:
            break
    if mesh.volume < 0:
        mesh.invert()
    if not (mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0):
        raise ValueError('sweep did not produce a closed solid')
    return mesh


def grade(x):
    return 7.371 - .00394 * np.asarray(x) ** 2 / 65


def surface(x, y):
    return grade(x) - .02 * np.abs(y)


# Pier 3, sheet 12 (local Z = El. - 210.000)
P3 = BS[2]
CAP_OUTER, CAP_CENTRAL, CENTRAL_HALF = 5.835, 5.879, 5.334 / 2
CAP_DEPTH = .915
COLUMN_TOP = CAP_OUTER - CAP_DEPTH                                    # El. 214.920 = 209.663 + 5.257
STEM_TOP, STEM_HALF, HAMMER_HALF, CAP_HALF = 3.549, 2.858, 5.601, 7.621
WALL_BASE, WALL_TOP = -.337, 1.643
COLUMN_HALF = .45
WALL_Y = (STEM_HALF + .025, YS[-1] + COLUMN_HALF + .300)              # 2.883 .. 7.863
# Sheet 14 fixed shoe and sheet 16 shim table
BASE_PLAN, BASE_H = (.400, .510), .205
TOP_SHOE_PLAN, TOP_SHOE_H = (.230, .310), .055
SHOE = BASE_H + TOP_SHOE_H                                            # 260 mm
SHIMS = np.array([49, 13, 32, 13, 26, 13, 32, 13, 49]) / 1000
SPLICE_PLATE = .013                                                   # model splice cover plate under the flange
SPLICE_HALF = 1.13 / 2
OLD_SPLICE_OFFSET = .457
L_SPAN = BS[2] - BS[1]
# Railing, sheet 19 section A-A: (inboard of the outer face, above the deck)
RAIL_OLD = [(0, 0), (.4, 0), (.4, .254), (.24, .84), (0, .84)]
RAIL_NEW = [(0, 0), (.4, 0), (.4, .100), (.275, .280), (.225, .840), (0, .840)]


def cap_top(y):
    return CAP_CENTRAL if abs(y) < CENTRAL_HALF else CAP_OUTER


def taper(x):
    """Share of the Pier 3 seat correction: 1 over the Pier 3 splice, 0 at Piers 2/4 and beyond."""
    return np.clip((L_SPAN - np.abs(np.asarray(x) - P3)) / (L_SPAN - SPLICE_HALF), 0, 1)


def to_gltf(v):
    return np.c_[v[:, 0], v[:, 2], -v[:, 1]]


def rail_mesh(side, i, profile):
    edges = np.linspace(-LENGTH / 2, LENGTH / 2, 5)
    a, b = edges[i], edges[i + 1]
    edge = side * (WIDTH / 2 - .05)
    return sweep(profile, np.linspace(a, b, max(2, int((b - a) / .6) + 1)),
                 lambda u, v, z: (u, edge - side * v, surface(u, edge - side * v) + z))


def end_bent_mesh(u, end):
    """Integral bent: deck-soffit top with crown crease, pavement ledge at the approach-slab soffit beyond the deck."""
    span_face, back_face, deck_end, base = u - end * .4, u + end * .4, end * LENGTH / 2, 5.443
    ref_ledge = float(grade(u)) - APPROACH_T - base
    ref_soffit = float(grade(u)) - SLAB - base

    def point(y, x, b):
        levels = [base, float(surface(x, y)) - APPROACH_T, float(surface(x, y)) - SLAB]
        return x, y, float(np.interp(b, [0, ref_ledge, ref_soffit], levels))
    profile = [(span_face, 0), (back_face, 0), (back_face, ref_ledge), (deck_end, ref_ledge),
               (deck_end, ref_soffit), (span_face, ref_soffit)]
    return sweep(profile, [-7.991, 0, 7.991], point)


def correct():
    mp = BASE / 'model_manifest.json'
    manifest = json.loads(mp.read_text(encoding='utf-8'))
    if manifest.get('review_correction') == TAG:
        print('Already corrected.')
        return
    if 'revision' in manifest or 'review_correction' in manifest:
        raise ValueError('Manifest is not the original generator revision.')
    path = BASE / 'model.glb'
    original = path.read_bytes()
    length = struct.unpack_from('<I', original, 12)[0]
    gltf = json.loads(original[20:20 + length])
    binary = bytearray(original[28 + length:])
    before = hashlib.sha256(original).hexdigest()
    parts = {p['id']: p for p in manifest['parts']}
    meshes = {m['name']: m for m in gltf['meshes']}
    if any(k in n for n in gltf['nodes'] for k in ('matrix', 'rotation', 'translation', 'scale')):
        raise ValueError('Unexpected node transform; this model stores glTF-axis vertices without node matrices.')

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
        prim = meshes[pid]['primitives'][0]
        g = read(prim['attributes']['POSITION']).astype(np.float64)
        return np.c_[g[:, 0], -g[:, 2], g[:, 1]], read(prim['indices']).reshape(-1, 3)

    changed = []

    def store(pid, vertices, faces=None, dims=None, note='', replace_note=False, name=None, basis=None, pages=()):
        prim = meshes[pid]['primitives'][0]
        old_faces = read(prim['indices']).reshape(-1, 3)
        new_faces = old_faces if faces is None else np.asarray(faces)
        solid = trimesh.Trimesh(vertices=vertices, faces=new_faces, process=False)
        if not solid.is_watertight or solid.volume <= 0:
            raise ValueError(f'{pid}: corrected mesh is not a valid solid')
        same = (len(vertices) == gltf['accessors'][prim['attributes']['POSITION']]['count']
                and np.array_equal(new_faces, old_faces))
        prim['attributes']['POSITION'] = append(to_gltf(vertices).astype('<f4'), 'VEC3', 5126)
        if not same:
            color = read(prim['attributes']['COLOR_0'])[0]
            prim['attributes']['COLOR_0'] = append(np.tile(color, (len(vertices), 1)).astype('u1'), 'VEC4', 5121)
            gltf['accessors'][prim['attributes']['COLOR_0']]['normalized'] = True
            prim['indices'] = append(new_faces.reshape(-1, 1).astype('<u4'), 'SCALAR', 5125)
        p = parts[pid]
        p['bounds_m'] = np.round(solid.bounds, 6).tolist()
        p['volume_m3'] = round(float(solid.volume), 9)
        if dims is not None:
            p['dimensions'].update(dims)
        if name:
            p['name'] = name
        if basis:
            p['basis'] = basis
        p['pdf_pages'] = sorted(set(p['pdf_pages']) | set(pages))
        p['note'] = note if replace_note else (p.get('note', '') + ' ' + note).strip()
        extras = meshes[pid]['extras']
        extras.update({k: p[k] for k in ('name', 'layer', 'color', 'pdf_pages', 'basis', 'note', 'dimensions')})
        if pid not in changed:
            changed.append(pid)
        return solid

    def store_mesh(pid, mesh, **kw):
        mesh.remove_unreferenced_vertices()
        if mesh.volume < 0:
            mesh.invert()
        return store(pid, np.asarray(mesh.vertices, dtype=np.float64), np.asarray(mesh.faces), **kw)

    def expect(cond, message):
        if not cond:
            raise ValueError('Model is not in the expected original state: ' + message)

    def bounds(pid):
        v, _ = native(pid)
        return v.min(axis=0), v.max(axis=0)

    # ---------------------------------------------------------------- original-state checks (Pier 3)
    old_bottom = surface(P3, YS) - SLAB - CLEAR - DEPTH
    for j in range(9):
        lo, hi = bounds(f'B3_bearing_{j + 1}')
        stack = .46 if j in (0, 8) else .26
        expect(np.allclose([lo[2], hi[2]], [old_bottom[j] - stack, old_bottom[j]], atol=2e-5), f'B3_bearing_{j + 1}')
        for i in (1, 2):
            v, _ = native(f'beam_{i}_{j}')
            at = np.isclose(v[:, 0], P3, atol=1e-5)
            expect(np.isclose(v[at, 2].min(), old_bottom[j], atol=2e-5), f'beam_{i}_{j} bottom at Pier 3')
        lo, hi = bounds(f'beam_{j + 1}_splice_2')
        expect(np.isclose((lo[0] + hi[0]) / 2, P3 + OLD_SPLICE_OFFSET, atol=1e-4), f'beam_{j + 1}_splice_2 station')
    old_cap = float(np.min(old_bottom - np.array([.46] + [.26] * 7 + [.46])))
    for pid, top in [('pier_3_hammerhead', old_cap), ('pier_3_cap_-1', old_cap), ('pier_3_cap_1', old_cap),
                     ('pier_3_column_-1', old_cap - CAP_DEPTH), ('pier_3_column_1', old_cap - CAP_DEPTH)]:
        expect(np.isclose(bounds(pid)[1][2], top, atol=2e-5), f'{pid} top')
    for j in range(1, 8):
        lo, hi = bounds(f'B3_seat_{j}')
        expect(np.allclose([lo[2], hi[2]], [old_cap, old_bottom[j] - .26], atol=2e-5), f'B3_seat_{j}')
    expect('B3_seat_0' not in parts and 'B3_seat_8' not in parts, 'outer seat parts already exist')

    # ---------------------------------------------------------------- 1. Pier 3 seat stack and beam fit
    contact = np.array([cap_top(y) for y in YS]) + SHOE + SHIMS + SPLICE_PLATE    # beam bottom-flange underside
    delta = contact - old_bottom
    expect(np.all(np.abs(delta) < .06), 'unexpected beam elevation at Pier 3')
    lift_mm = ', '.join(f'{d * 1000:+.0f}' for d in delta)
    span_note = ('Pier 3 end fitted to the sheet 12/14/16 seat stack (cap El. 215.835 / 215.879 + 260 mm shoe + shim '
                 '+ 13 mm splice plate): {:+.0f} mm at Pier 3, tapering linearly to zero at Pier {}. Review '
                 'correction, rev. 1.1.')
    for j in range(9):
        d = delta[j]
        for i in (1, 2):
            pid = f'beam_{i}_{j}'
            v, _ = native(pid)
            v[:, 2] += d * taper(v[:, 0])
            store(pid, v, note=span_note.format(d * 1000, 2 if i == 1 else 4), pages=[32, 36])
            pid = f'haunch_{i}_{j}'
            v, _ = native(pid)
            bottom = np.isclose(v[:, 2], surface(v[:, 0], YS[j]) - SLAB - CLEAR, atol=2e-5)
            expect(bottom.sum() * 2 == len(v), f'{pid} bottom vertices')
            v[bottom, 2] += d * taper(v[bottom, 0])
            thickness = surface(v[:, 0], v[:, 1]) - SLAB - v[:, 2]
            if thickness[bottom].min() <= .02:
                raise ValueError(f'{pid}: haunch too thin after the fit')
            store(pid, v, dims=dict(minimum_thickness_m=round(float(thickness[bottom].min()), 4)),
                  note=f'Bottom follows the beam fitted at Pier 3 ({d * 1000:+.0f} mm there), review correction.',
                  pages=[32, 36])
        for q in (1, 3):
            for suffix in ('', '_bolts'):
                pid = f'beam_{j + 1}_splice_{q}{suffix}'
                v, _ = native(pid)
                v[:, 2] += d * taper(v[:, 0])
                store(pid, v, note=f'Follows the beam fitted at Pier 3 ({d * taper(v[:, 0]).mean() * 1000:+.1f} mm '
                                   'here), review correction.')
        # 2. Centre splices on the Pier 3 centre line (sheet 13).
        for suffix in ('', '_bolts'):
            pid = f'beam_{j + 1}_splice_2{suffix}'
            v, _ = native(pid)
            v[:, 0] -= OLD_SPLICE_OFFSET
            expect(np.abs(v[:, 0] - P3).max() <= SPLICE_HALF + 1e-6, f'{pid} extent')
            v[:, 2] += float(surface(P3, YS[j]) - surface(P3 + OLD_SPLICE_OFFSET, YS[j])) + d
            store(pid, v, note=f'On the Pier 3 centre line (sheet 13: "C/L Pier No. 3 & C/L Splice"), moved '
                               f'457 mm west and {d * 1000:+.0f} mm with the beam; review correction.',
                  dims=dict(station_from_pier_3_m=0.0), pages=[33, 36])

    # Fixed shoes (sheet 14) and shim plates (sheet 16).
    shoe_note = ('Fixed shoe assembly, sheet 14: fixed base (PL 50x400x510 and 155 mm block) and 55 mm top shoe, '
                 '260 mm above the cap at both existing and new beams; anchor bolts, studs and side details omitted. '
                 'The shim plate is part B3_seat_{}. Review correction (was 460 mm at the outer beams).')
    for j in range(9):
        y, base = YS[j], cap_top(YS[j])
        bx, by = BASE_PLAN
        tx, ty = TOP_SHOE_PLAN
        shoe = concat([box(P3 - bx / 2, P3 + bx / 2, y - by / 2, y + by / 2, base, base + BASE_H),
                       box(P3 - tx / 2, P3 + tx / 2, y - ty / 2, y + ty / 2, base + BASE_H, base + SHOE)])
        store_mesh(f'B3_bearing_{j + 1}', shoe, replace_note=True, note=shoe_note.format(j),
                   basis='Dimensioned fixed shoe assembly, sheets 12, 14 and 16',
                   dims=dict(pad_thickness_m=BASE_H, load_plate_thickness_m=TOP_SHOE_H, shoe_height_m=SHOE,
                             seat_elevation_m=round(base + 210, 3)), pages=[32, 34, 36])
    world = gltf['nodes'][gltf['scenes'][gltf.get('scene', 0)]['nodes'][0]]
    added = []
    for j in range(9):
        y, base = YS[j], cap_top(YS[j])
        tx, ty = TOP_SHOE_PLAN
        shim = box(P3 - tx / 2, P3 + tx / 2, y - ty / 2, y + ty / 2, base + SHOE, base + SHOE + SHIMS[j])
        pid = f'B3_seat_{j}'
        meta = dict(name=f'Pier 3 | shim plate, beam line {j + 1}',
                    basis='Sheet 16 shim table (Pier 3); plan size taken as the 230 x 310 mm top shoe '
                          '(not dimensioned)',
                    note=f'{SHIMS[j] * 1000:.0f} mm shim between the top shoe and the bottom splice cover plate of '
                         'the beam (sheets 13, 14 and 16). Replaces the derived seat riser of the original model; '
                         'review correction.',
                    dims=dict(thickness_m=float(SHIMS[j]), plan_x_m=tx, plan_y_m=ty))
        if pid in parts:
            store_mesh(pid, shim, replace_note=True, note=meta['note'], name=meta['name'], basis=meta['basis'],
                       dims=meta['dims'], pages=[32, 33, 34, 36])
            continue
        color = parts['B3_seat_1']['color']
        p = dict(id=pid, name=meta['name'], layer='bearings', color=color, pdf_pages=[32, 33, 34, 36],
                 basis=meta['basis'], note=meta['note'], dimensions=meta['dims'],
                 bounds_m=np.round(shim.bounds, 6).tolist(), volume_m3=round(float(shim.volume), 9))
        rgba = np.tile([int(color[k:k + 2], 16) for k in (1, 3, 5)] + [255], (len(shim.vertices), 1)).astype('u1')
        prim = dict(attributes=dict(POSITION=append(to_gltf(np.asarray(shim.vertices)).astype('<f4'), 'VEC3', 5126),
                                    COLOR_0=append(rgba, 'VEC4', 5121)),
                    indices=append(np.asarray(shim.faces).reshape(-1, 1).astype('<u4'), 'SCALAR', 5125), mode=4)
        gltf['accessors'][prim['attributes']['COLOR_0']]['normalized'] = True
        gltf['meshes'].append(dict(name=pid, extras=dict(processed=True, **{k: p[k] for k in (
            'id', 'name', 'layer', 'color', 'pdf_pages', 'basis', 'note', 'dimensions')}), primitives=[prim]))
        gltf['nodes'].append(dict(name=pid, mesh=len(gltf['meshes']) - 1))
        world['children'].append(len(gltf['nodes']) - 1)
        meshes[pid] = gltf['meshes'][-1]
        position = manifest['parts'].index(parts['B3_seat_7' if j == 8 else 'B3_seat_1']) + (1 if j == 8 else 0)
        manifest['parts'].insert(position, p)
        parts[pid] = p
        added.append(pid)

    # Cap, cap ends and columns (sheet 12).
    head = sweep([(-HAMMER_HALF, CAP_OUTER), (-CENTRAL_HALF, CAP_OUTER), (-CENTRAL_HALF, CAP_CENTRAL),
                  (CENTRAL_HALF, CAP_CENTRAL), (CENTRAL_HALF, CAP_OUTER), (HAMMER_HALF, CAP_OUTER),
                  (HAMMER_HALF, COLUMN_TOP), (STEM_HALF, STEM_TOP), (-STEM_HALF, STEM_TOP), (-HAMMER_HALF, COLUMN_TOP)],
                 [-.305, .305], lambda x, y, z: (P3 + x, y, z))
    store_mesh('pier_3_hammerhead', head, replace_note=True, pages=[32],
               note='Sheet 12: top El. 215.835, raised to El. 215.879 over the central 5.334 m (scaled 5.31 m; '
                    'width as dimensioned for Piers 2/4, sheet 11) under beam lines 4-6; 915 mm deep at the cap ends, '
                    'tapering to the stem at El. 213.549. Chamfers simplified. Review correction (top was 181 mm low).',
               dims=dict(top_elevation_m=215.835, central_top_elevation_m=215.879, central_width_m=5.334,
                         end_depth_m=CAP_DEPTH))
    for side in (-1, 1):
        ya, yb = sorted([side * HAMMER_HALF, side * CAP_HALF])
        store_mesh(f'pier_3_cap_{side}', box(P3 - .305, P3 + .305, ya, yb, COLUMN_TOP, CAP_OUTER), pages=[32],
                   note='Sheet 12: top El. 215.835, 915 mm deep. Review correction (was 181 mm low).',
                   dims=dict(top_elevation_m=215.835, depth_m=CAP_DEPTH))
        y = side * YS[-1]
        store_mesh(f'pier_3_column_{side}',
                   box(P3 - .305, P3 + .305, y - COLUMN_HALF, y + COLUMN_HALF, WALL_BASE, COLUMN_TOP), pages=[32],
                   note='Sheet 12: 5257 mm from El. 209.663 to the cap soffit at El. 214.920. Review correction.',
                   dims=dict(height_m=round(COLUMN_TOP - WALL_BASE, 3), top_elevation_m=214.920))

    # Diaphragm rows of spans B and C follow the beams; 3. Span C rows move 457 mm west (sheet 13).
    rows = {}
    for q in range(11):
        lo, hi = bounds(f'diaphragm_{q}_0')
        rows[q] = (lo[0] + hi[0]) / 2
    expect(np.allclose([rows[5], rows[6], rows[7]], [BS[1] + 19.584, P3 + 7.061, P3 + 13.665], atol=1e-4),
           'diaphragm row stations')
    for q in range(3, 8):
        shift = {6: -.457, 7: -.457}.get(q, 0.0)
        for j in range(8):
            pid = f'diaphragm_{q}_{j}'
            v, _ = native(pid)
            old_x = rows[q]
            if shift:
                v[:, 0] += shift
                v[:, 2] += float(grade(old_x + shift) - grade(old_x))
            v[:, 2] += taper(v[:, 0]) * np.interp(v[:, 1], YS, delta)
            note = 'Follows the beams fitted at Pier 3, review correction.'
            if shift:
                note = (f'Row moved to {old_x + shift - P3:.3f} m east of Pier 3: the sheet 13 chain 457 + 7061 + 6604 '
                        '+ 6833 starts at the diaphragm 457 mm west of the pier. ' + note)
            store(pid, v, note=note, pages=[33],
                  dims=dict(station_from_pier_3_m=round(float(old_x + shift - P3), 3)) if shift else None)

    # 7. End-span MC460 channels (sheets 13, 15).
    for q in (0, 1, 2, 8, 9, 10):
        for j in (1, 6):
            pid = f'diaphragm_{q}_{j}'
            v, _ = native(pid)
            zmin, zmax = v[:, 2].min(), v[:, 2].max()
            expect(np.isclose(zmax - zmin, .38, atol=1e-5), f'{pid} depth')
            low = v[:, 2] < (zmin + zmax) / 2
            v[low, 2] -= .08
            store(pid, v, dims=dict(depth_m=.46), pages=[35],
                  note='MC460x63.5 (Span A & D), sheets 13 and 15: deepened from 380 to 460 mm, top unchanged; review '
                       'correction.')

    # 4. Integral end-bent tops (sheet 9).
    for bi, u, end in ((1, BS[0], -1), (5, BS[4], 1)):
        pid = f'end_bent_{bi}'
        v, _ = native(pid)
        top = v[:, 2] > 6
        expect(len(v) == 8 and np.allclose(np.abs(v[:, 1]), 7.991, atol=1e-5)
               and np.allclose(v[top, 2], surface(v[top, 0], 7.991) - SLAB, atol=2e-5), f'{pid} straight top')
        bent = end_bent_mesh(u, end)
        store_mesh(pid, bent, pages=[29, 61],
                   note='Top follows the crowned deck soffit (sheet 9 elevation El. 217.153 at the edges, 217.307 at '
                        'the crown; section A-A); the outer 150 mm beyond the deck end is the pavement ledge under the '
                        '1\'-2" approach slab (1998 sheet 9; 2026 sheet 13, PDF 61). Review correction: the straight '
                        'top left up to 160 mm open under the crown.',
                   dims=dict(ledge_width_m=round(abs(u + end * .4 - end * LENGTH / 2), 4)))

    # 5. Wingwalls (sheet 9).
    for bi, u, end in ((0, BS[0], -1), (4, BS[4], 1)):
        for side in (-1, 1):
            pid = f'wing_{bi}_{side}'
            v, _ = native(pid)
            expect(np.allclose([v[:, 0].min(), v[:, 0].max()], sorted([u - end * 1.6, u + end * 2.1]), atol=1e-4),
                   f'{pid} station')
            v[:, 0] -= end * .5
            store(pid, v, pages=[29],
                  note='Sheet 9 plan: 1600 mm toward the approach and 2100 mm toward the span from the bent centre '
                       'line; moved 0.5 m spanward, review correction.',
                  dims=dict(approachward_m=1.6, spanward_m=2.1))

    # 6. Collision walls (sheet 12).
    for side in (-1, 1):
        pid = f'pier_3_crash_{side}'
        lo, hi = bounds(pid)
        expect(np.allclose(sorted([abs(lo[1]), abs(hi[1])]), [3.0, 7.62], atol=1e-5), f'{pid} extent')
        ya, yb = sorted([side * WALL_Y[0], side * WALL_Y[1]])
        store_mesh(pid, box(P3 - .305, P3 + .305, ya, yb, WALL_BASE, WALL_TOP), pages=[32],
                   note='Sheet 12: 4980 mm wall, 300 mm beyond the outer column face, 25 mm preformed joint against '
                        'the stem; review correction (was 3.000-7.620 m).',
                   dims=dict(length_m=round(WALL_Y[1] - WALL_Y[0], 3), stem_joint_m=.025,
                             projection_beyond_column_m=.3))

    # 8. Bridge railing (sheet 19).
    for side in (-1, 1):
        for i in range(4):
            pid = f'rail_{side}_{i}'
            v, _ = native(pid)
            old = rail_mesh(side, i, RAIL_OLD)
            ov = np.asarray(old.vertices)
            expect(len(v) == len(ov) and np.allclose(np.sort(v, axis=0), np.sort(ov, axis=0), atol=2e-5),
                   f'{pid} original section')
            store_mesh(pid, rail_mesh(side, i, RAIL_NEW), pages=[39],
                       note='Sheet 19 section A-A: 100 mm toe, break 125 mm in at 280 mm, 225 mm top at 840 mm; review '
                            'correction (was 254 mm toe, single slope, 240 mm top).',
                       dims=dict(toe_height_m=.1, break_height_m=.28, top_width_m=.225))

    # ---------------------------------------------------------------- write
    gltf['buffers'][0]['byteLength'] = len(binary)
    while len(binary) % 4:
        binary.append(0)
    gltf['buffers'][0]['byteLength'] = len(binary)
    encoded = json.dumps(gltf, ensure_ascii=True, separators=(',', ':')).encode()
    encoded += b' ' * ((-len(encoded)) % 4)
    out = (struct.pack('<III', 0x46546c67, 2, 28 + len(encoded) + len(binary)) +
           struct.pack('<II', len(encoded), 0x4e4f534a) + encoded +
           struct.pack('<II', len(binary), 0x004e4942) + binary)
    backup = ROOT / 'data/fem_research'
    backup.mkdir(exist_ok=True)
    (backup / f'{BID}_before_review_correction.glb').write_bytes(original)
    (backup / f'{BID}_manifest_before_review_correction.json').write_bytes(mp.read_bytes())
    path.write_bytes(out)

    for item in manifest.get('detail_coverage', []):
        if item.get('feature') == 'Steel connections and support topology':
            item['part_ids'] += [p for p in added if p not in item['part_ids']]
            item['detail'] = ('Channel diaphragm rows, field splice envelopes and 27 pier shoes/bearings. Pier 3 fixed '
                              'shoes and shim plates follow sheets 12, 14 and 16. Both end bents are integral, with no '
                              'invented end bearings.')
        elif item.get('feature') == 'Retained and widened piers':
            item['detail'] = ('Piers 2/4 reconstructed side-wall stems; Pier 3 retained hammerhead (El. 215.835 / '
                              '215.879), added outer columns and low collision walls per sheet 12. Footing offsets and '
                              'Pier 2/4 seats remain approximate.')
    manifest['review_correction'] = TAG
    manifest['revision'] = REVISION
    manifest['review_correction_record'] = dict(
        source_pdf_pages=[29, 31, 32, 33, 34, 35, 36, 39, 59, 61], printed_sheets_1998=[9, 11, 12, 13, 14, 15, 16, 19],
        printed_sheets_2026=[11, 13],
        corrections={
            'pier_3_seat_stack': 'cap El. 215.835 / 215.879 (central 5.334 m), column tops El. 214.920, 260 mm fixed '
                                 'shoes, sheet 16 shims as B3_seat_0..8; beam bottoms at Pier 3 = seat + shoe + shim + '
                                 '13 mm splice plate, changes of ' + lift_mm + ' mm for lines 1-9, tapered to zero '
                                 'at Piers 2 and 4',
            'pier_3_splices': 'nine centre splices and fasteners moved from X = +0.457 m to the Pier 3 centre line',
            'span_c_diaphragm_rows': 'rows at 6.604 m and 13.208 m east of Pier 3 (were 7.061 / 13.665 m)',
            'end_bent_tops': 'crowned deck-soffit top with the 150 mm pavement ledge beyond the deck end',
            'wingwalls': '1600 mm approachward / 2100 mm spanward of the bent centre line (were reversed)',
            'collision_walls': 'Y = 2.883-7.863 m (were 3.000-7.620 m)',
            'end_span_diaphragms': 'bays 2 and 7 of the six Span A/D rows deepened to MC460 (460 mm)',
            'bridge_railing': 'sheet 19 section: 100 mm toe, break at 280 mm, 225 mm top'},
        beam_fit_at_pier_3_m=dict(zip([f'line_{j + 1}' for j in range(9)], np.round(delta, 5).tolist())),
        changed_parts=changed, added_parts=added,
        renamed_parts={f'B3_seat_{j}': dict(before=f'Bent 3 | seat riser {j + 1}',
                                            after=f'Pier 3 | shim plate, beam line {j + 1}') for j in range(1, 8)},
        before_glb_sha256=before, after_glb_sha256=hashlib.sha256(out).hexdigest())
    deviations = [d for d in manifest.get('known_deviations', [])
                  if d.get('id') not in ('pier-2-4-seat-stack', 'pier-3-beam-taper')]
    deviations += [
        dict(id='pier-2-4-seat-stack', parts='pier_2_widening, pier_4_widening, B2_*, B4_*, beams at Piers 2/4',
             source='sheets 11, 14, 16 (PDF 31, 34, 36)',
             deviation='Pier 2/4 cap tops are at Z 5.925 (El. 215.925) against plan El. 215.972 / 216.016, and the '
                       'beam bottoms are 15-60 mm below the plan seat + 125 mm elastomeric bearing + sheet 16 shim; '
                       'derived seat risers remain.',
             reason='The girder profile is nominal (1998 grade less a constant 75 mm haunch). Refitting it at '
                    'Piers 2/4 and the end bents is a girder-elevation rebuild beyond this review correction.'),
        dict(id='pier-3-beam-taper', parts='beam_1_*, beam_2_*, haunch_1_*, haunch_2_*, splices, diaphragm rows 4-8',
             source='sheets 12, 14, 16 (PDF 32, 34, 36)',
             deviation='The Pier 3 beam fit (+2 to +47 mm) tapers linearly to zero at Piers 2 and 4; haunches at '
                       'Pier 3 are 28-73 mm at the beam centre lines instead of the nominal 75 mm.',
             reason='The plans give no top-of-steel or screed elevations between supports.')]
    manifest['known_deviations'] = deviations
    mp.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in manifest['review_correction_record'].items()
                      if k not in ('changed_parts', 'renamed_parts')}, indent=1))
    print(len(changed), 'parts changed,', len(added), 'added')


if __name__ == '__main__':
    correct()

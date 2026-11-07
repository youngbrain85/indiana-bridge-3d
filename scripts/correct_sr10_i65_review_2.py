"""Second drawing-confirmed correction of SR 10 over I-65 (sr10-i65), run after correct_sr10_i65_review.py.

    python scripts/correct_sr10_i65_review_2.py

Source: drawings.pdf, the local review binder. PDF 1-20 are the 1964 original plans (drawing S n of 12), PDF 21-40 the
1998 B-23753 rehabilitation (printed sheet n = PDF page n + 20), PDF 49-62 the 2026 R-43918 approach plans (printed
sheet n = PDF page n - 48) and PDF 63-74 the 2026 revision notice. Local Z = plan elevation - 210.000 m.

Handedness. Sheets 4 and 13 (PDF 24, 33) and 2026 sheet 11 (PDF 59) are drawn with north up and stations increasing
to the east (Bent 1 at Sta. 1+492.059 on the west); the 2026 plan shows S.R. 10 W.B.L. on the north half. Native +Y is
left of increasing station (right-handed X, Y, Z; the generator also names the +Y rail "left"), so +Y is north. The
sheet 13 framing plan has Beam Line No. 1 on the north edge, so drawing beam line n lies at native Y = YS[9 - n]. The
generator numbered its beam, splice, bearing and shim ids from the south edge (index 0 at Y = -7.113 m). The geometry
is symmetric except for the C380 bay below, which is placed on the drawing side; ids and names are kept and the
numbering is recorded as a known deviation.

1. Pier 3 splice cover plates and beam fit. The first correction put the beam bottoms at Pier 3 on cap + 260 mm shoe
   + shim + a 13 mm splice plate. The plates are thicker: lines 1 and 9 have the new Type I splice, flange plates
   PL 16x292x1130 top and bottom (sheet 14, PDF 34); lines 2-8 keep the 1964 field splice at the Pier 3 centre line
   ("C/L Exist. Splice", sheet 13), flange plates PL 12 in x 15/16 in, 111 in long (1.5 + 36 + 3 + 12 + 3 + 3 + 12
   + 3 + 36 + 1.5 in, and 1.5 + 30 + 3 + 18 + 3 + 3 + 18 + 3 + 30 + 1.5 in for the 1964 exterior beams), "bottom
   flange material same as top" (1964 S9, PDF 11). The 1964 Pier 3 shoe assembly (same sheet) stacks the splice plate
   on the shim. Spans B and C beams, haunch bottoms and the Pier 2/4-side splices are raised by a further 3.0 mm
   (lines 1, 9) / 10.8125 mm (lines 2-8) at Pier 3 with the first correction's taper (constant over the 1.13 m
   splice, linear to zero at Piers 2 and 4). The nine centre splice envelopes are rebuilt: web plates and bolts move
   with the beam, and the flange plates get the drawing thickness, width and length and follow the fitted beam
   (piecewise linear) so that shim, plate and flange stay in contact.
2. Diaphragm sections and elevations (sheets 13 and 15, PDF 33 and 35; 1964 S8 and S10, PDF 10 and 12). Exterior bays
   (beam lines 1-2 and 8-9) are new MC460x63.5 whose bottom is 200 mm above the bottom of the W840x193 outer beam
   (both sheet 15 interior diaphragm details); the model had 280 mm. Interior bays of spans A/D (incl. the Pier 2/4
   rows) are new MC460x63.5 centred between the beam flanges ("Dimensions A are to be equal +/-25 mm", sheet 15); the
   model had their tops 100 mm below the beam top. In spans B/C the interior bays keep the existing W460x68 (18WF45
   on 1964 S8), centred ("A dimensions are equal +/-1 in", 1964 S10 Section A-A), except the bay between drawing
   beam lines 6 and 7, where the sheet 13 note replaces them with C380x74 bolted to the stubs of the old diaphragms
   (sheet 15 Detail "B" / Section C-C, centred on the stub). That bay is native Y -3.556 to -1.778 m (model bay
   index 2). The model had C380-depth channels in bay indices 1 and 6 of spans B/C and channels everywhere else.
   Channels keep the generator's nominal channel profile; the W460x68 uses its catalog 154 x 15.4 mm flanges and
   9.1 mm web with the nominal 460 mm depth. Diaphragms stay horizontal at their row stations and Y extents.
3. Approach slabs (2026 sheet 14, PDF 62, pay item "Reinf. Conc. Bridge Appr., 12"", 114 SYS per bent; revision
   notice PDF 67 "Reinforced concrete bridge approach, 12 in."): 12 in deep, not 14 in (the 1'-2" on sheet 13 /
   PDF 61 section C-C is the curb width, 2 + 5 + 7 in). Approach soffits are raised 50.8 mm; the end-bent pavement
   ledges, which the first correction closed to the approach soffit, follow.
4. Pier 3 widened footings (sheet 12 footing plan, PDF 32): 5000 mm = 300 (beyond the collision wall) + 300 (to the
   column) + 900 (column) + 3500 mm, with the column on beam line 1/9 (7.113 m), so |Y| = 3.163-8.163 m; the inner
   end is 305 mm outboard of the 5716 mm stem (2.858 m). The model had 2.8-7.8 m, so the walls (2.883-7.863 m after the
   first correction) overhung the footing by 63 mm. X and Z are unchanged.

Requires numpy, trimesh and shapely (2.1 or later); uses box/concat/iform from scripts/bridge_geometry.py.
Optional arguments for a dry run on a copy: --base DIR (bridge folder) and --backup DIR.
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
from bridge_geometry import box, concat, iform  # noqa: E402

BID = 'sr10-i65'
PREVIOUS_TAG = 'pier3-stack-splices-diaphragms-endbents-wings-walls-rails'
PREVIOUS_REVISION = '1.1-drawing-review'
TAG = 'splice-plates-diaphragm-sections-approaches-footings'
REVISION = '1.2-drawing-review-2'
TOL = 3e-5                                                            # float32 vertex tolerance (m)

FT, IN = .3048, .0254
SPANS = np.array([39 + .5 / 12, 65.75, 65.75, 39 + .5 / 12]) * FT     # as built by build_indiana_batch3.sr10
BS = np.r_[0, np.cumsum(SPANS)] - SPANS.sum() / 2                     # support centre lines
LENGTH = (211 + 2.75 / 12) * FT
SLAB, CLEAR = .2, .075
YS = np.array([-7.113, -5.080, -3.556, -1.778, 0, 1.778, 3.556, 5.080, 7.113])   # model index 0 = drawing line 9
DEPTH = np.array([.84] + [.92] * 7 + [.84])
P3 = BS[2]
SPLICE_HALF = 1.13 / 2                                                # taper plateau of the first correction
L_SPAN = BS[2] - BS[1]

# 1. Splice cover plates at Pier 3 (index j = model beam index; lines 1/9 Type I, lines 2-8 retained 1964 splice).
OLD_PLATE = .013
PLATE_T = np.array([.016] + [15 / 16 * IN] * 7 + [.016])
PLATE_W = np.array([.292] + [12 * IN] * 7 + [.292])
PLATE_L = np.array([1.13] + [111 * IN] * 7 + [1.13])
LIFT = PLATE_T - OLD_PLATE                                            # +3.0 / +10.8125 mm

# 2. Diaphragms.
CH_B, CH_TW, CH_TF = .105, .011, .017                                 # generator's nominal channel profile
W460 = dict(d=.46, bf=.154, tw=.0091, tf=.0154)                       # W460x68 (catalog flange/web, nominal depth)
EXT_BOTTOM = .200                                                     # sheet 15: MC460 bottom above W840 bottom
C380_BAY = 2                                                          # drawing beam lines 6-7 = Y -3.556..-1.778
BC_ROWS = range(3, 8)

# 3. Approach slab.
OLD_APPROACH_T, APPROACH_T = 14 * IN, 12 * IN

# 4. Pier 3 footings.
OLD_FOOTING_Y = (2.8, 7.8)
FOOTING_OUT = YS[-1] + .45 + .300 + .300                              # 8.163
FOOTING_Y = (FOOTING_OUT - 5.0, FOOTING_OUT)                          # 3.163 .. 8.163


def sweep(profile, stations, fn):
    """Closed prism through `stations` (as in correct_sr10_i65_review.py, without earcut/graph dependencies)."""
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


def taper(x):
    """Share of the Pier 3 seat correction: 1 over the Pier 3 splice, 0 at Piers 2/4 and beyond (first correction)."""
    return np.clip((L_SPAN - np.abs(np.asarray(x) - P3)) / (L_SPAN - SPLICE_HALF), 0, 1)


def to_gltf(v):
    return np.c_[v[:, 0], v[:, 2], -v[:, 1]]


def end_bent_mesh(u, end, approach_t):
    """Integral bent of the first correction: deck-soffit top with crown crease, ledge at the approach soffit."""
    span_face, back_face, deck_end, base = u - end * .4, u + end * .4, end * LENGTH / 2, 5.443
    ref_ledge = float(grade(u)) - approach_t - base
    ref_soffit = float(grade(u)) - SLAB - base

    def point(y, x, b):
        levels = [base, float(surface(x, y)) - approach_t, float(surface(x, y)) - SLAB]
        return x, y, float(np.interp(b, [0, ref_ledge, ref_soffit], levels))
    profile = [(span_face, 0), (back_face, 0), (back_face, ref_ledge), (deck_end, ref_ledge),
               (deck_end, ref_soffit), (span_face, ref_soffit)]
    return sweep(profile, [-7.991, 0, 7.991], point)


def channel(h):
    return [(-CH_B / 2, 0), (CH_B / 2, 0), (CH_B / 2, CH_TF), (-CH_B / 2 + CH_TW, CH_TF), (-CH_B / 2 + CH_TW, h - CH_TF),
            (CH_B / 2, h - CH_TF), (CH_B / 2, h), (-CH_B / 2, h)]


def correct(base_dir=None, backup_dir=None):
    base = Path(base_dir) if base_dir else ROOT / 'data/bridges' / BID
    mp = base / 'model_manifest.json'
    raw_manifest = mp.read_bytes()
    manifest = json.loads(raw_manifest.decode('utf-8'))
    if manifest.get('review_correction_2') == TAG:
        print('Already corrected.')
        return
    if manifest.get('review_correction') != PREVIOUS_TAG or manifest.get('revision') != PREVIOUS_REVISION:
        raise ValueError('Run scripts/correct_sr10_i65_review.py first (expected revision 1.1-drawing-review).')
    if 'review_correction_2' in manifest:
        raise ValueError('Manifest carries an unknown second correction.')
    path = base / 'model.glb'
    original = path.read_bytes()
    before = hashlib.sha256(original).hexdigest()
    if manifest['review_correction_record']['after_glb_sha256'] != before:
        raise ValueError('model.glb is not the output of the first review correction.')
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

    current = {}                                                      # native vertices of meshes changed so far

    def native(pid):
        if pid in current:
            return current[pid][0].copy(), current[pid][1]
        prim = meshes[pid]['primitives'][0]
        g = read(prim['attributes']['POSITION']).astype(np.float64)
        return np.c_[g[:, 0], -g[:, 2], g[:, 1]], read(prim['indices']).reshape(-1, 3)

    changed = []

    def store(pid, vertices, faces=None, dims=None, note='', replace_note=False, basis=None, pages=()):
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
        stored = read(prim['attributes']['POSITION']).astype(np.float64)
        current[pid] = (np.c_[stored[:, 0], -stored[:, 2], stored[:, 1]], new_faces)
        p = parts[pid]
        p['bounds_m'] = np.round(solid.bounds, 6).tolist()
        p['volume_m3'] = round(float(solid.volume), 9)
        if dims is not None:
            p['dimensions'].update(dims)
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
            raise ValueError('Model is not in the expected state after the first correction: ' + message)

    def bounds(pid):
        v, _ = native(pid)
        return v.min(axis=0), v.max(axis=0)

    def profile(i, j):
        """Station x, bottom-flange underside and top-flange top of beam_i_j (piecewise linear between stations)."""
        v, _ = native(f'beam_{i}_{j}')
        xs = np.unique(np.round(v[:, 0], 5))
        lo = np.array([v[np.abs(v[:, 0] - x) < 1e-4, 2].min() for x in xs])
        hi = np.array([v[np.abs(v[:, 0] - x) < 1e-4, 2].max() for x in xs])
        return xs, lo, hi

    def beam_at(j, x):
        i = int(np.clip(np.searchsorted(BS, x, side='right') - 1, 0, 3))
        xs, lo, hi = profile(i, j)
        return float(np.interp(x, xs, lo)), float(np.interp(x, xs, hi))

    # ---------------------------------------------------------------- expected starting state
    expect(manifest['review_correction_record']['added_parts'] == ['B3_seat_0', 'B3_seat_8'], 'added parts')
    for j in range(9):
        sh_lo, sh_hi = bounds(f'B3_seat_{j}')
        xs, lo, _ = profile(1, j)
        expect(np.isclose(lo[-1], sh_hi[2] + OLD_PLATE, atol=TOL), f'beam line index {j}: shim + 13 mm plate stack')
        lo2, hi2 = bounds(f'beam_{j + 1}_splice_2')
        expect(np.allclose([lo2[0], hi2[0]], [P3 - SPLICE_HALF, P3 + SPLICE_HALF], atol=TOL)
               and np.isclose(lo2[2], sh_hi[2], atol=TOL), f'beam_{j + 1}_splice_2 envelope')
    for end in (-1, 1):
        v, _ = native(f'approach_{end}')
        d = surface(v[:, 0], v[:, 1]) - v[:, 2]
        expect(np.all((np.abs(d) < TOL) | (np.abs(d - OLD_APPROACH_T) < TOL)), f'approach_{end} 14 in deep')
    for bi, u, end in ((1, BS[0], -1), (5, BS[4], 1)):
        v, _ = native(f'end_bent_{bi}')
        old = np.asarray(end_bent_mesh(u, end, OLD_APPROACH_T).vertices)
        expect(len(v) == len(old) and np.allclose(np.sort(v, axis=0), np.sort(old, axis=0), atol=TOL),
               f'end_bent_{bi} ledge at the 14 in approach soffit')
    for side in (-1, 1):
        lo, hi = bounds(f'pier_3_footing_{side}')
        expect(np.allclose(sorted([abs(lo[1]), abs(hi[1])]), OLD_FOOTING_Y, atol=1e-5), f'pier_3_footing_{side}')
        lo, hi = bounds(f'pier_3_crash_{side}')
        expect(np.allclose(sorted([abs(lo[1]), abs(hi[1])]), [2.883, 7.863], atol=1e-5), f'pier_3_crash_{side}')
    rows = {}
    for q in range(11):
        lo, hi = bounds(f'diaphragm_{q}_0')
        rows[q] = (lo[0] + hi[0]) / 2
    expect(np.allclose([rows[q] for q in range(11)],
                       np.r_[BS[0] + np.array([1.7, 6.8, 11.9]), BS[1] + np.array([6.833, 13.437, 19.584]),
                             P3 + np.array([6.604, 13.208, 20.041]), BS[3] + np.array([5.1, 10.2])], atol=1e-4),
           'diaphragm row stations')
    for q in range(11):
        for j in range(8):
            lo, hi = bounds(f'diaphragm_{q}_{j}')
            expect(np.allclose([lo[1], hi[1]], [YS[j] + .16, YS[j + 1] - .16], atol=1e-5)
                   and np.isclose(hi[0] - lo[0], CH_B, atol=1e-5), f'diaphragm_{q}_{j} channel envelope')

    # ---------------------------------------------------------------- 1. splice plates and beam fit at Pier 3
    for j in range(9):
        d = float(LIFT[j])
        for i in (1, 2):
            pid = f'beam_{i}_{j}'
            v, _ = native(pid)
            v[:, 2] += d * taper(v[:, 0])
            store(pid, v, pages=[11, 34],
                  note=f'Raised a further {d * 1000:+.1f} mm at Pier 3 (same taper) for the '
                       f'{PLATE_T[j] * 1000:.1f} mm splice cover plate on the shim ('
                       + ('Type I PL 16x292x1130, sheet 14' if j in (0, 8) else 'retained PL 12 in x 15/16 in, 1964 S9 '
                                                                               '/ PDF 11') + '); review correction 2.')
            pid = f'haunch_{i}_{j}'
            v, _ = native(pid)
            top = np.abs(v[:, 2] - (surface(v[:, 0], v[:, 1]) - SLAB)) < TOL
            expect(top.sum() * 2 == len(v), f'{pid} top vertices')
            v[~top, 2] += d * taper(v[~top, 0])
            thickness = surface(v[:, 0], v[:, 1]) - SLAB - v[:, 2]
            if thickness[~top].min() <= .01:
                raise ValueError(f'{pid}: haunch thinner than 10 mm after the fit')
            store(pid, v, dims=dict(minimum_thickness_m=round(float(thickness[~top].min()), 4)), pages=[11, 34],
                  note=f'Bottom raised a further {d * 1000:+.1f} mm at Pier 3 with the beam (splice plate '
                       'thickness), review correction 2.')
        for q in (1, 3):
            for suffix in ('', '_bolts'):
                pid = f'beam_{j + 1}_splice_{q}{suffix}'
                v, _ = native(pid)
                v[:, 2] += d * taper(v[:, 0])
                store(pid, v, note=f'Raised {d * taper(v[:, 0]).mean() * 1000:+.1f} mm with the beam, review '
                                   'correction 2.')

    embed = {}
    for j in range(9):
        d, t, w, half = float(LIFT[j]), float(PLATE_T[j]), float(PLATE_W[j]), float(PLATE_L[j]) / 2
        y = YS[j]
        pid = f'beam_{j + 1}_splice_2'
        v, _ = native(pid)
        web = np.abs(v[:, 0] - P3) < .3
        expect(web.sum() == 16 and np.allclose(np.abs(v[web, 0] - P3), .24, atol=TOL), f'{pid} web plates')
        pieces = []
        for side in (v[web, 1] < y, v[web, 1] > y):
            wv = v[web][side]
            lo, hi = wv.min(axis=0), wv.max(axis=0)
            pieces.append(box(lo[0], hi[0], lo[1], hi[1], lo[2] + d, hi[2] + d))
        xs1, lo1, hi1 = profile(1, j)
        xs2, lo2, hi2 = profile(2, j)
        xs, lo, hi = np.r_[xs1, xs2[1:]], np.r_[lo1, lo2[1:]], np.r_[hi1, hi2[1:]]
        expect(np.isclose(xs1[-1], P3, atol=1e-5) and np.isclose(xs2[0], P3, atol=1e-5)
               and np.isclose(lo1[-1], lo2[0], atol=TOL), f'beam line index {j} continuous at Pier 3')
        stations = np.r_[P3 - half, xs[np.abs(xs - P3) < half - 1e-3], P3 + half]
        bottom, top = np.interp(stations, xs, lo), np.interp(stations, xs, hi)
        for level, z0, z1 in ((bottom, -t, 0.0), (top, 0.0, t)):
            pieces.append(sweep([(y - w / 2, z0), (y + w / 2, z0), (y + w / 2, z1), (y - w / 2, z1)], stations,
                                lambda s, a, b, level=level: (s, a, float(np.interp(s, stations, level)) + b)))
        if j in (0, 8):
            text = ('Type I splice (sheet 14): flange plates PL 16x292x1130 top and bottom (were 13 mm); the bottom '
                    'plate bears on the shim.')
        else:
            text = ('Retained 1964 field splice ("C/L Exist. Splice", sheet 13; 1964 S9 / PDF 11): flange plates '
                    'PL 12 in x 15/16 in x 111 in (2.819 m) top and bottom (were 13 mm x 1.13 m); the bottom plate '
                    'bears on the shim (1964 Pier 3 shoe assembly).')
        store_mesh(pid, concat(pieces), pages=[11, 33, 34],
                   note=text + f' Flange plates follow the fitted beam; web plates raised {d * 1000:+.1f} mm with it; '
                               'review correction 2.',
                   dims=dict(flange_plate_thickness_m=round(t, 7), flange_plate_width_m=round(w, 4),
                             flange_plate_length_m=round(2 * half, 4)))
        tv = current[pid][0]
        tv = tv[tv[:, 2] > float(np.interp(P3, xs, hi)) - .01]
        embed[j] = float((tv[:, 2] - (surface(tv[:, 0], tv[:, 1]) - SLAB)).max())
        pid = f'beam_{j + 1}_splice_2_bolts'
        v, _ = native(pid)
        expect(np.all(taper(v[:, 0]) == 1), f'{pid} inside the taper plateau')
        v[:, 2] += d
        store(pid, v, note=f'Raised {d * 1000:+.1f} mm with the beam, review correction 2.')

    # ---------------------------------------------------------------- 2. diaphragm sections and elevations
    span_rows = {q: 'A/D' for q in (0, 1, 2, 8, 9, 10)}
    span_rows.update({q: 'B/C' for q in BC_ROWS})
    sections = {}
    for q in range(11):
        u = rows[q]
        bot = np.array([beam_at(j, u)[0] for j in range(9)])
        top = np.array([beam_at(j, u)[1] for j in range(9)])
        mid = (bot + top) / 2
        for j in range(8):
            pid = f'diaphragm_{q}_{j}'
            ya, yb = YS[j] + .16, YS[j + 1] - .16
            if j in (0, 7):
                kind, h, outer = 'MC460x63.5', .46, 0 if j == 0 else 8
                z0 = bot[outer] + EXT_BOTTOM
                note = ('New MC460x63.5 in the exterior bay (sheet 13); bottom 200 mm above the bottom of the W840x193 '
                        'outer beam (sheet 15 interior diaphragm details, spans A/D and B/C). Review correction 2: the '
                        'bottom was 280 mm above it.')
                pages = [33, 35]
            elif q in BC_ROWS and j == C380_BAY:
                kind, h = 'C380x74', .38
                z0 = (mid[j] + mid[j + 1]) / 2 - h / 2
                note = ('Replacement C380x74 in the bay between drawing beam lines 6 and 7 (sheet 13 note: existing '
                        'W460x68 removed in this bay), bolted to the stubs of the old diaphragms and centred on them '
                        '(sheet 15 Detail "B" and Section C-C); the old W460x68 were centred between the beam flanges '
                        '(1964 S10 / PDF 12). Drawing beam line 1 is the north edge (+Y), so this bay is Y -3.556 to '
                        '-1.778 m. Review correction 2: the model had C380-depth channels in the bays between its '
                        'lines 2-3 and 7-8 instead.')
                pages = [12, 33, 35]
            elif q in BC_ROWS:
                kind, h = 'W460x68', W460['d']
                z0 = (mid[j] + mid[j + 1]) / 2 - h / 2
                note = ('Retained W460x68 intermediate diaphragm (sheet 13 framing plan; 18WF45 on 1964 S8 / PDF 10), '
                        'centred between the beam flanges ("A dimensions are equal +/-1 in", 1964 S10 Section A-A, '
                        'PDF 12). I-section with the nominal 460 mm depth and catalog 154 x 15.4 mm flanges, 9.1 mm '
                        'web. Review correction 2: was modelled as a 380 or 460 mm channel with its top 100 mm below the '
                        'beam top.')
                pages = [10, 12, 33, 35]
            else:
                kind, h = 'MC460x63.5', .46
                z0 = (mid[j] + mid[j + 1]) / 2 - h / 2
                note = ('New MC460x63.5 (Span A & D, sheet 13), centred between the beam flanges ("Dimensions A are to '
                        'be equal +/-25 mm", sheet 15 interior diaphragm detail, spans A and D). Review correction 2: '
                        'the top was 100 mm below the beam top (100 / 360 mm clearances).')
                pages = [33, 35]
            pr = iform(W460['d'], W460['bf'], W460['tw'], W460['tf']) if kind == 'W460x68' else channel(h)
            mesh = sweep(pr, [ya, yb], lambda s, a, b, z0=z0, u=u: (u + a, s, z0 + b))
            if q in (6, 7):
                note = (f'Row at {u - P3:.3f} m east of Pier 3 (sheet 13 chain from the diaphragm 457 mm west of the '
                        'pier; review correction). ' + note)
            z1 = z0 + h
            if not (z0 > max(bot[j], bot[j + 1]) + .05 and z1 < min(top[j], top[j + 1]) - .05):
                raise ValueError(f'{pid}: diaphragm not inside the beam depth')
            a_top = (top[j] + top[j + 1]) / 2 - z1
            a_bottom = z0 - (bot[j] + bot[j + 1]) / 2
            sections[pid] = (kind, round(float(a_top), 4), round(float(a_bottom), 4))
            if j in (0, 7):
                dims = dict(depth_m=h, section=kind, bottom_above_outer_beam_bottom_m=EXT_BOTTOM)
            else:
                dims = dict(depth_m=h, section=kind, clear_top_m=round(float(a_top), 4),
                            clear_bottom_m=round(float(a_bottom), 4))
            store_mesh(pid, mesh, replace_note=True, note=note, pages=pages, dims=dims,
                       basis='Sheets 13 and 15 framing and diaphragm details' + (
                           '; 1964 S8/S10 for the retained W460x68' if q in BC_ROWS and j not in (0, 7) else ''))

    # ---------------------------------------------------------------- 3. approach slabs and end-bent ledges
    for end in (-1, 1):
        pid = f'approach_{end}'
        v, _ = native(pid)
        low = surface(v[:, 0], v[:, 1]) - v[:, 2] > OLD_APPROACH_T / 2
        v[low, 2] += OLD_APPROACH_T - APPROACH_T
        store(pid, v, replace_note=True, pages=[61, 62, 67],
              note='20 ft 6 in long, 12 in deep (pay item "Reinf. Conc. Bridge Appr., 12 in", 2026 sheet 14 / PDF 62; '
                   'revision notice PDF 67). Existing deck and 2019 overlay remain distinct from the replacement '
                   'approach. Review correction 2: was 14 in; the 1\'-2" on sheet 13 / PDF 61 is the curb width.',
              dims=dict(thickness_m=round(APPROACH_T, 4)))
    for bi, u, end in ((1, BS[0], -1), (5, BS[4], 1)):
        pid = f'end_bent_{bi}'
        note = parts[pid]['note'].replace('under the 1\'-2" approach slab (1998 sheet 9; 2026 sheet 13, PDF 61)',
                                          'under the 12 in approach slab (1998 sheet 9; 2026 sheets 13-14, PDF 61-62)')
        expect('12 in approach slab' in note, f'{pid} note')
        store_mesh(pid, end_bent_mesh(u, end, APPROACH_T), replace_note=True, pages=[62],
                   note=note + ' Review correction 2: ledge raised 50.8 mm to the 12 in approach soffit.')

    # ---------------------------------------------------------------- 4. Pier 3 footings
    for side in (-1, 1):
        pid = f'pier_3_footing_{side}'
        v, _ = native(pid)
        v[:, 1] += side * (FOOTING_Y[0] - OLD_FOOTING_Y[0])
        store(pid, v, replace_note=True, pages=[32],
              basis='Sheet 12 footing plan and elevation: 5000 x 1800 x 610 mm',
              note='Sheet 12 footing plan: 300 mm beyond the collision wall, 300 mm to the column face, 900 mm column on '
                   'beam line 1/9 (7.113 m) and 3500 mm, so |Y| = 3.163-8.163 m, 305 mm outboard of the stem end; '
                   'El. 209.053-209.663. The inner 280 mm of the collision wall bears on the existing footing, which is '
                   'not modelled. Review correction 2 (was 2.8-7.8 m; the wall overhung it by 63 mm).',
              dims=dict(length_m=5.0, width_m=1.8, thickness_m=.61, projection_beyond_wall_m=.3))

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
    backup = Path(backup_dir) if backup_dir else ROOT / 'data/fem_research'
    backup.mkdir(exist_ok=True)
    (backup / f'{BID}_before_review_correction_2.glb').write_bytes(original)
    (backup / f'{BID}_manifest_before_review_correction_2.json').write_bytes(raw_manifest)
    path.write_bytes(out)

    for item in manifest.get('detail_coverage', []):
        if item.get('feature') == 'Steel connections and support topology':
            item['detail'] = ('Diaphragm rows per sheets 13/15: MC460x63.5 in spans A/D and the exterior bays, retained '
                              'W460x68 and one C380x74 bay in spans B/C; field splice envelopes (Pier 3 cover plates per '
                              'sheet 14 and 1964 S9) and 27 pier shoes/bearings. Pier 3 fixed shoes and shim plates '
                              'follow sheets 12, 14 and 16. Both end bents are integral, with no invented end bearings.')
        elif item.get('feature') == 'Retained and widened piers':
            item['detail'] = ('Piers 2/4 reconstructed side-wall stems; Pier 3 retained hammerhead (El. 215.835 / '
                              '215.879), added outer columns, low collision walls and widened footings per sheet 12. '
                              'Pier 2/4 footing offsets and seats remain approximate.')
        elif item.get('feature') == 'Rails, approaches and drainage':
            item['detail'] = item['detail'].replace('2026 14 in approach slabs', '2026 12 in approach slabs')
    manifest['review_correction_2'] = TAG
    manifest['revision'] = REVISION
    counts = {}
    for kind, _, _ in sections.values():
        counts[kind] = counts.get(kind, 0) + 1
    manifest['review_correction_2_record'] = dict(
        source='Independent second check of the corrected model (2026-11), items verified against the drawings',
        source_pdf_pages=[10, 11, 12, 24, 32, 33, 34, 35, 59, 61, 62, 67],
        printed_sheets_1964=['S8', 'S9', 'S10'], printed_sheets_1998=[4, 12, 13, 14, 15], printed_sheets_2026=[11, 13, 14],
        handedness='North up, stations increasing east (sheets 4, 13; 2026 sheet 11). Native +Y = left of increasing '
                   'station = north. Drawing Beam Line No. 1 is the north edge (Y = +7.113 m); model ids number from '
                   'the south edge (index 0 at Y = -7.113 m), see known deviation beam-line-numbering.',
        corrections={
            'pier_3_splice_plates': 'flange cover plates 13 mm x 1.13 m -> PL 16x292x1130 (lines 1/9, sheet 14) and '
                                    'PL 12 in x 15/16 in x 111 in (lines 2-8, 1964 S9 / PDF 11), top and bottom',
            'pier_3_beam_fit': 'spans B/C beams, haunch bottoms and splices raised a further +3.0 mm (lines 1/9) / '
                               '+10.8 mm (lines 2-8) at Pier 3 with the first correction taper',
            'diaphragms': 'all 88 rebuilt: exterior bays MC460 with bottom 200 mm above the W840 bottom (was 280 mm); '
                          'spans A/D interior bays MC460 centred (sheet 15 equal A); spans B/C interior bays retained '
                          'W460x68 centred (1964 S10), C380x74 between drawing beam lines 6-7 (Y -3.556..-1.778) '
                          '(sheet 13, sheet 15 Detail B)',
            'approach_slabs': '14 in -> 12 in deep (2026 sheet 14 / PDF 62, revision PDF 67); soffit raised 50.8 mm',
            'end_bent_ledges': 'pavement ledge raised 50.8 mm to the 12 in approach soffit',
            'pier_3_footings': '|Y| 2.8-7.8 m -> 3.163-8.163 m (sheet 12 footing plan)'},
        additional_beam_fit_at_pier_3_m=dict(zip([f'model_index_{j}' for j in range(9)], np.round(LIFT, 7).tolist())),
        diaphragm_sections=counts,
        top_splice_plate_above_slab_soffit_mm={f'model_index_{j}': round(embed[j] * 1000, 1) for j in range(9)},
        changed_parts=changed, added_parts=[], removed_parts=[],
        before_glb_sha256=before, after_glb_sha256=hashlib.sha256(out).hexdigest())
    fit = np.array(list(manifest['review_correction_record']['beam_fit_at_pier_3_m'].values())) + LIFT
    hmin = min(parts[f'haunch_{i}_{j}']['dimensions']['minimum_thickness_m'] for i in (1, 2) for j in range(9))
    ids = ('pier-3-beam-taper', 'beam-line-numbering', 'pier-3-top-splice-plate-embedment', 'pier-2-4-splice-plates',
           'approach-ledge-detail')
    deviations = [d for d in manifest.get('known_deviations', []) if d.get('id') not in ids]
    deviations += [
        dict(id='pier-3-beam-taper', parts='beam_1_*, beam_2_*, haunch_1_*, haunch_2_*, splices, diaphragm rows 4-8',
             source='sheets 12, 14, 16 (PDF 32, 34, 36); 1964 S9 (PDF 11)',
             deviation=f'The Pier 3 beam fit (+{fit.min() * 1000:.0f} to +{fit.max() * 1000:.0f} mm: seat + shoe + '
                       'shim + splice plate) tapers linearly to zero at Piers 2 and 4; haunches at Pier 3 are as thin '
                       f'as {hmin * 1000:.1f} mm at the flange edges instead of the nominal 75 mm.',
             reason='The plans give no top-of-steel or screed elevations between supports, and the model uses the '
                    'nominal 920 mm depth for the W920 beams.'),
        dict(id='beam-line-numbering',
             parts='beam_*_*, haunch_*_*, beam_N_splice_*, B2/B3/B4_bearing_N, B2/B3/B4_seat_*, diaphragm bays',
             source='sheets 4, 13 (PDF 24, 33); 2026 sheet 11 (PDF 59)',
             deviation='Drawing Beam Line No. 1 is the north edge (native +Y = 7.113 m, left of increasing station). '
                       'Model ids and names number the beam lines from the south edge: model index j (beam j+1, '
                       'B3_seat_j, bay j+1) is drawing beam line 9-j (bay between drawing lines 8-j and 9-j). The '
                       'geometry follows the drawing (it is symmetric except the C380x74 bay, placed between drawing '
                       'lines 6 and 7 at Y -3.556..-1.778 m).',
             reason='Part ids are stable keys and are not renamed by a review correction.'),
        dict(id='pier-3-top-splice-plate-embedment', parts='beam_2..beam_8_splice_2',
             source='1964 S9 (PDF 11); sheets 12, 14, 16',
             deviation=f'The 15/16 in top cover plates of the retained Pier 3 splices reach up to '
                       f'{max(embed.values()) * 1000:.1f} mm into the deck slab soffit at model indices '
                       f'{", ".join(str(j) for j in range(9) if embed[j] > 0)} (drawing beam lines '
                       f'{", ".join(str(9 - j) for j in range(9) if embed[j] > 0)}); the other plates clear it.',
             reason='The beams use the nominal 920 mm depth; W920x223 (36WF150) is about 911 mm deep, which would leave '
                    'the plates just below the soffit.'),
        dict(id='pier-2-4-splice-plates', parts='beam_N_splice_1, beam_N_splice_3 and their bolts',
             source='sheet 14 (PDF 34)',
             deviation='The field splices 900 mm into spans B and C keep the generic envelope (13 mm flange plates, '
                       '1.13 m long). Sheet 14 gives Type I PL 16x292x1130 at beam lines 1/9 and Type II PL 13x305x980 '
                       'with 4 mm fillers at lines 2-8.',
             reason='Not part of the reviewed findings; envelope only.'),
        dict(id='approach-ledge-detail', parts='end_bent_1, end_bent_5, approach_-1, approach_1',
             source='1998 sheet 9 (PDF 29); 2026 sheets 13-14 (PDF 61-62)',
             deviation='The pavement ledge is closed to the soffit of the 12 in approach slab; the 1998 ledge is drawn '
                       'at El. 216.850, about 0.15 m lower, with the old approach thickened onto it.',
             reason='The 2026 approach end over the ledge is on standard drawings E609-RCBA-01 to -04, which are not in '
                    'the set.')]
    manifest['known_deviations'] = deviations
    text = json.dumps(manifest, indent=2) + ('\n' if raw_manifest.endswith(b'\n') else '')
    mp.write_text(text, encoding='utf-8')
    print(json.dumps({k: v for k, v in manifest['review_correction_2_record'].items() if k != 'changed_parts'},
                     indent=1))
    print(len(changed), 'parts changed, 0 added, 0 removed')


if __name__ == '__main__':
    args = dict(zip(sys.argv[1::2], sys.argv[2::2]))
    correct(args.get('--base'), args.get('--backup'))

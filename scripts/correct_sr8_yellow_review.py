"""One-time, drawing-confirmed corrections from the SR 8 / Yellow River model review; unrelated GLB buffers are kept.

    python scripts/correct_sr8_yellow_review.py

Source: INDOT B-23076 (1997), data/bridges/sr8-yellow/drawings.pdf. PDF pages 1-20 are printed sheets 1-20; PDF 25 is
shop sheet M1. Native axes: X station (east), Y transverse (north positive), Z = elevation - 210.000 m. Support lines
are skewed 49 deg: X = u - tan(49 deg) Y; u = -40.147 / -29.609 / +29.609 / +40.147 at Bents 1 / 2 / 5 / 6.
Deck top D(X, Y) = 8.257 - X^2/15240 - 0.02|Y| (sheet 5, 152.4 m vertical curve; sheet 14, 2 % crossfall).

F1  Integral end bents (sheets 8 and 9, Elevation and Section A-A). The bent is one 760 mm wide (380 + 380 about the
    bearing/pile line) wall from "Bottom of Bent El. 216.100" up to the deck soffit: Pour 1 (737-810 mm) plus Pour 2,
    which encases the beam ends. The outer 150 mm on the approach side is the pavement ledge under the 300 mm approach
    slab end. The model had only an 0.8 m block at El. 215.953-216.753. cap_0 / cap_5 are rebuilt from El. 216.100 to
    the deck soffit (D - 0.200), the ledge at D - 0.300, with the beam ends cut out; the wings (sheet 9, Wing A/B
    elevations, bottom El. 216.100) get the same bottom.
F2  End-bent piles (sheet 8, Piling Plan, offsets along the pile line from the structure centre line): existing piles at
    +/-7.493 and +/-1.499 m and new 355 mm piles at +/-5.421 m continue into the bent; the existing battered piles at
    +/-4.496 m are cut off at El. 215.800 (also sheet 5 notes). The model repeated the nine-pile Bent 2 layout of
    sheet 10. Eight stubs are rebuilt at these positions (battered piles drawn vertical below the cut-off; their
    batter is not dimensioned in the bundle); pile_stub_0_4 / pile_stub_5_4 (no plan pile) are removed.
F3  Approach slabs (sheet 18, Plan - East Approach; west same by 180 deg rotation): the pavement end is square, 18.467
    and 6.250 m from the end of the bridge floor along the 10.620 m core edges (Y = +/-5.310), so X = +/-52.856; the
    slab is 10.920 m wide (5.460 + 5.460) with 450 mm curb strips (Y = +/-5.460 to 5.910) 5.030 m long from the same
    reference. The model had a 6.250 m skew parallelogram over the full 11.820 m.
F4  End-span diaphragms (sheet 11 Framing Plan; shop sheet M1: 16 M1H + 8 M1J = 24 MC460 channels): two channels per
    bay, not three. Per span, one row stands on the Bent 2 / Bent 5 bearing line; the other is 3.000 m from the end-bent
    bearing along each exterior beam with 1.870 + 3 @ 2.045 m between the bays (X = -/+31.362, 33.232, 35.277,
    37.322, 39.367 and 42.932). The model had three rows per end span (3.0 and 6.0 m from the west support, 1.0 m from
    the east support); the middle row (diaphragm_0_1_*, diaphragm_4_1_*) is removed and the other two are moved.
F5  Bents 2 and 5 (sheet 10, Elevation): "Bott./Cap Elev. = 215.585"; the model cap bottom was El. 215.509. The cap
    bottom, and the tops of the nine existing piles under each cap, move to El. 215.585. The dimensioned seats
    (El. 216.900 / 216.940 / 216.870) lie 6-62 mm above the modelled bearing bottoms, which hang from girders set at a
    nominal 90 mm haunch; reseating them needs the girder grade reconciled with the bearing stack and shim table
    (sheets 11, 13). That part is recorded as a known deviation, not changed.
F6  Bridge rail (sheet 14 Half Section: 10.920 clear roadway, 400 rail + 50 coping; sheet 17 Section D-D): toe at
    |Y| = 5.460, 100 mm vertical, then 125 x 180 and 50 x 560 slopes to an 840 mm top 225 mm wide; outer face at
    5.860. The model had a 450 mm base, a 254 mm vertical toe and a 10.820 m clear width. All ten panels are rebuilt.
F7  Beam numbering (sheet 11 Framing Plan, north arrow and circled lines 1-7; consistent with the sheet 11 shim table):
    Beam 1 is the north exterior line. The model named the south line "beam 1". Names only: beam_s_j is Beam 7-j and
    bearing n is the bearing under Beam 8-n; part ids are unchanged.

Requires numpy, trimesh, shapely and manifold3d (no mapbox_earcut).
"""
import hashlib
import json
import struct
from pathlib import Path

import numpy as np
import trimesh
from shapely.geometry import Polygon
from shapely.geometry.polygon import orient

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'data/bridges/sr8-yellow'
TAG = 'sr8-yellow-review-2026-11'
TAN, COS, SIN = np.tan(np.radians(49)), np.cos(np.radians(49)), np.sin(np.radians(49))
SPANS = [10.538, 18.636, 21.946, 18.636, 10.538]
BS = np.r_[0, np.cumsum(SPANS)] - sum(SPANS) / 2          # support stations at Y = 0
YS = [-5.029, -3.556, -1.778, 0.0, 1.778, 3.556, 5.029]   # beam lines, south to north
DECK_END_U = 40.498                                        # skew deck end planes
APPROACH_START_U = 40.523                                  # model approach start (24 mm joint strip kept)
BENT_BOTTOM_Z = 216.100 - 210                              # sheets 8, 9
CUTOFF_Z = 215.800 - 210                                   # sheets 5, 8
PILE_LOW_Z = 4.5                                           # modelled display cut of the end-bent piles
CAP_BOTTOM_Z = {1: 215.585 - 210, 4: 215.585 - 210}        # sheet 10
PAVEMENT_END_X = DECK_END_U + 5.310 * TAN + 6.250          # sheet 18: 52.856
# Sheet 8 piling plan: offset along the pile line (north positive), kind, top. Mapped onto pile_stub_b_j, j south->north.
PILES = [(-7.493, 'existing', 'e'), (-5.421, 'new', 'e'), (-4.496, 'cut', 'c'), (-1.499, 'existing', 'e'),
         (1.499, 'existing', 'e'), (4.496, 'cut', 'c'), (5.421, 'new', 'e'), (7.493, 'existing', 'e')]
PILE_SLOTS = [0, 1, 2, 3, 5, 6, 7, 8]


def sweep(profile, xs, fn):
    """bridge_geometry.sweep without its optional dependencies (mapbox_earcut for the end caps, a graph engine for
    fix_normals): the profile ring is oriented counter-clockwise, the caps are triangulated with manifold3d and the
    closed solid is inverted if its volume is negative."""
    ring = np.asarray(orient(Polygon(profile), 1.0).exterior.coords)[:-1]
    assert Polygon(ring).is_valid and Polygon(ring).area > 0
    vv, ff = trimesh.creation.triangulate_polygon(Polygon(ring), engine='manifold')
    if len(vv) != len(ring) or not np.allclose(vv, ring):
        raise ValueError('Cap triangulation reordered the profile')
    ff = np.asarray(ff)
    e1, e2 = vv[ff[:, 1]] - vv[ff[:, 0]], vv[ff[:, 2]] - vv[ff[:, 0]]
    area = e1[:, 0] * e2[:, 1] - e1[:, 1] * e2[:, 0]
    ff = np.where((area < 0)[:, None], ff[:, ::-1], ff)
    n = len(vv)
    v = [fn(float(x), float(a), float(b)) for x in xs for a, b in vv]
    f = []
    for k in range(len(xs) - 1):
        for j in range(n):
            a = k * n + j
            b = k * n + (j + 1) % n
            f.extend([(a, b, b + n), (a, b + n, a + n)])
    f.extend(tuple(q[::-1]) for q in ff)
    f.extend(tuple(q + (len(xs) - 1) * n) for q in ff)
    m = trimesh.Trimesh(v, f, process=True)
    if m.volume < 0:
        m.invert()
    return m


def rod(a, b, r, sections=12):
    """Vertical pile stub, as bridge_geometry.rod."""
    m = trimesh.creation.cylinder(r, b[2] - a[2], sections=sections)
    m.apply_translation([a[0], a[1], (a[2] + b[2]) / 2])
    return m


def grade(x):
    return 8.257 - np.asarray(x) ** 2 / 15240


def deck(x, y):
    return grade(x) - 0.02 * np.abs(y)


def sx(u, y):
    return u - TAN * y


def plan_beam(j):
    n = 7 - j
    return f'Beam {n}' + (' (north exterior)' if n == 1 else ' (south exterior)' if n == 7 else '')


def correct():
    mp = BASE / 'model_manifest.json'
    manifest = json.loads(mp.read_text(encoding='utf-8'))
    if manifest.get('review_correction') == TAG:
        print('Already corrected.')
        return
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

    def native(pid):
        """Mesh of a part in native axes; GLB stores (X, Z, -Y)."""
        prim = meshes[pid]['primitives'][0]
        s = read(prim['attributes']['POSITION']).astype(np.float64)
        return trimesh.Trimesh(np.c_[s[:, 0], -s[:, 2], s[:, 1]], read(prim['indices']).reshape(-1, 3), process=False)

    changes = []

    def store(pid, solid, note, name=None, **dims):
        if not solid.is_watertight or solid.volume <= 0:
            raise ValueError(f'{pid}: invalid corrected solid')
        prim = meshes[pid]['primitives'][0]
        color = read(prim['attributes']['COLOR_0'])[0]
        v = np.asarray(solid.vertices, dtype=np.float64)
        prim['attributes'] = {'POSITION': append(np.c_[v[:, 0], v[:, 2], -v[:, 1]].astype('<f4'), 'VEC3', 5126),
                              'COLOR_0': append(np.tile(color, (len(v), 1)).astype('u1'), 'VEC4', 5121)}
        gltf['accessors'][prim['attributes']['COLOR_0']]['normalized'] = True
        prim['indices'] = append(np.asarray(solid.faces).reshape(-1, 1).astype('<u4'), 'SCALAR', 5125)
        p = parts[pid]
        p['bounds_m'] = np.round(solid.bounds, 6).tolist()
        p['volume_m3'] = round(float(solid.volume), 9)
        p['dimensions'].update(dims)
        label(pid, note, name)

    def label(pid, note, name=None):
        p = parts[pid]
        if name:
            p['name'] = name
        p['note'] = (p.get('note', '') + ' ' + note).strip()
        if pid not in changes:
            changes.append(pid)

    def expect(cond, what):
        if not cond:
            raise ValueError('Model is not in the expected original state: ' + what)

    # ---- Original-state checks -------------------------------------------------------------------------------
    for b in (0, 5):
        c = native(f'cap_{b}')
        expect(np.allclose(c.bounds[:, 2], [5.952984, 6.752984], atol=2e-6) and len(c.vertices) == 8, f'cap_{b}')
        piles = [pid for pid in parts if pid.startswith(f'pile_stub_{b}_')]
        expect(len(piles) == 9, f'nine piles at bent {b + 1}')
        for j in range(9):
            m = native(f'pile_stub_{b}_{j}')
            expect(abs(m.bounds.mean(axis=0)[1] - (-5.2 + 1.3 * j)) < 1e-4 and abs(m.bounds[1, 2] - 5.952984) < 2e-6,
                   f'pile_stub_{b}_{j}')
        for side in (-1, 1):
            expect(abs(native(f'wing_{b}_{side}').bounds[0, 2] - 5.952984) < 2e-6, f'wing_{b}_{side}')
    for b in (1, 4):
        expect(np.allclose(native(f'cap_{b}').bounds[:, 2], [5.509219, 6.809219], atol=2e-6), f'cap_{b}')
        for j in range(9):
            expect(abs(native(f'pile_stub_{b}_{j}').bounds[1, 2] - 5.509219) < 2e-6, f'pile_stub_{b}_{j}')
    for i in (0, 4):
        for row in range(3):
            for j in range(6):
                expect(f'diaphragm_{i}_{row}_{j}' in parts, f'diaphragm_{i}_{row}_{j}')
    rail = native('rail_-1_0')
    expect(np.allclose(np.unique(rail.vertices[:, 1].round(4)), [-5.86, -5.62, -5.41]), 'rail section')
    app = native('approach_1').vertices
    expect(np.allclose(np.unique((app[:, 0] + TAN * app[:, 1]).round(3))[[0, -1]], [40.523, 46.773]), 'approach')
    expect(parts['beam_0_0']['name'] == 'Span A | W840x193 beam 1' and parts['beam_0_0']['bounds_m'][1][1] < -4.8,
           'beam numbering')

    # ---- F1: integral end bents and wing bottoms ---------------------------------------------------------------
    half_t, deck_t = 0.38 / COS, DECK_END_U - BS[5]           # X-offsets of the bent faces and of the deck end
    for b, k in ((0, -1), (5, 1)):                             # k: approach side (west of Bent 1, east of Bent 6)
        u = BS[b]
        # Profile (t, code): code 0 bottom, 1 approach ledge (D - 0.300), 2 deck soffit (D - 0.200).
        if k < 0:
            prof = [(-half_t, 0), (half_t, 0), (half_t, 2), (-deck_t, 2), (-deck_t, 1), (-half_t, 1)]
        else:
            prof = [(-half_t, 0), (half_t, 0), (half_t, 1), (deck_t, 1), (deck_t, 2), (-half_t, 2)]

        def at(y, t, code, u=u):
            x = sx(u + t, y)
            return (x, y, BENT_BOTTOM_Z if code == 0 else deck(x, y) - (0.3 if code == 1 else 0.2))

        body = sweep(prof, np.linspace(-5.91, 5.91, 25), at)
        span = 0 if b == 0 else 4
        beams = [native(f'beam_{span}_{j}') for j in range(7)]
        bent = trimesh.boolean.difference([body] + beams, engine='manifold')
        if not bent.is_watertight or not body.volume - 0.2 < bent.volume < body.volume:
            raise ValueError(f'cap_{b}: invalid beam-end cut')
        old = native(f'cap_{b}').volume
        store(f'cap_{b}', bent,
              'Rebuilt as the integral end bent of sheets 8-9: 760 mm wide from Bottom of Bent El. 216.100 to the deck '
              'soffit (Pour 1 + Pour 2 encasing the beam ends; beam ends cut out), with the 150 mm approach-slab '
              'pavement ledge 300 mm below the deck surface. Bearings and pedestals are now encased.',
              name=f'Bent {b + 1} | integral end bent (Pours 1 and 2)',
              bottom_el_m=216.1, normal_width_m=0.76, top='deck soffit (deck surface - 0.200 m)',
              approach_ledge_width_m=0.15, approach_ledge_below_deck_m=0.3)
        parts[f'cap_{b}']['pdf_pages'] = [8, 9]
        parts[f'cap_{b}']['basis'] = 'Dimensioned end-bent section and bottom elevation; reinforcement and keyways omitted'
        print(f'cap_{b}: {old:.3f} -> {bent.volume:.3f} m3')
        for side in (-1, 1):
            pid = f'wing_{b}_{side}'
            w = native(pid)
            v = w.vertices.copy()
            low = np.isclose(v[:, 2], 5.952984, atol=2e-6)
            expect(low.sum() == 4, pid)
            v[low, 2] = BENT_BOTTOM_Z
            store(pid, trimesh.Trimesh(v, w.faces, process=False),
                  'Bottom raised to El. 216.100 with the bent (sheet 9 wing elevations).', bottom_el_m=216.1)

    # ---- F2: end-bent piles ----------------------------------------------------------------------------------
    removed = []
    for b in (0, 5):
        u = BS[b]
        for (a, kind, top), j in zip(PILES, PILE_SLOTS):
            pid = f'pile_stub_{b}_{j}'
            x, y = u - a * SIN, a * COS
            z1 = BENT_BOTTOM_Z if top == 'e' else CUTOFF_Z
            where = f'{abs(a):.3f} m {"N" if a > 0 else "S"} of the structure centre line along the pile line'
            if kind == 'cut':
                name = f'Bent {b + 1} | existing battered pile, cut off at El. 215.800 ({where})'
                note = ('Abandoned existing battered pile cut off at El. 215.800, sheets 5 and 8; batter not dimensioned '
                        'in the bundle, drawn vertical below the cut-off.')
            else:
                name = f'Bent {b + 1} | {"new 355 mm steel-encased" if kind == "new" else "existing 355 mm"} pile ({where})'
                note = ('Repositioned to the sheet 8 piling plan; continues into the bent above Bottom of Bent '
                        'El. 216.100.')
            store(pid, rod([x, y, PILE_LOW_Z], [x, y, z1], .1775), note, name=name,
                  offset_along_pile_line_m=a, top_el_m=round(z1 + 210, 3),
                  status={'existing': 'existing, retained', 'new': 'new', 'cut': 'existing battered, cut off'}[kind])
            parts[pid]['pdf_pages'] = [5, 8]
        removed.append(f'pile_stub_{b}_4')

    # ---- F3: approach slabs ----------------------------------------------------------------------------------
    for s in (-1, 1):
        pid = f'approach_{s}'
        x_end = s * PAVEMENT_END_X

        def slab(y0, y1, xe, n):
            yy = sorted({y0, y1} | ({0.0} if y0 < 0 < y1 else set()))
            prof = [(y, -0.3) for y in yy] + [(y, 0.0) for y in reversed(yy)]

            def at(q, y, z):
                xs = s * APPROACH_START_U - TAN * y
                x = xs + q * (xe - xs)
                return (x, y, deck(x, y) + z)
            return sweep(prof, np.linspace(0, 1, n), at)

        pieces = [slab(-5.46, 5.46, x_end, 33)]
        for g in (-1, 1):
            xc = s * DECK_END_U - TAN * g * 5.31 + s * 5.03
            pieces.append(slab(*sorted((g * 5.46, g * 5.91)), xc, 11))
        merged = trimesh.boolean.union(pieces, engine='manifold')
        if not merged.is_watertight or abs(merged.volume - sum(p.volume for p in pieces)) > 1e-4:
            raise ValueError(pid + ': invalid union')
        store(pid, merged,
              'Plan corrected to sheet 18: square pavement end at X = +/-52.856 (18.467 / 6.250 m along the 10.620 m core '
              'edges), 10.920 m slab plus 450 mm curb strips 5.030 m long. Skew start kept at the modelled joint; '
              'the squared corners at |Y| > 5.310 and the pavement support are not modelled.',
              pavement_end_x_m=round(x_end, 6), long_edge_m=18.467, short_edge_m=6.25, slab_width_m=10.92,
              curb_strip_m=[0.45, 5.03])
        parts[pid]['pdf_pages'] = [7, 18, 19]
        parts[pid]['basis'] = 'Dimensioned plan outline; thickened end and pavement support simplified'
        parts[pid]['dimensions'].pop('length_m', None)

    # ---- F4: end-span diaphragms -----------------------------------------------------------------------------
    for i, end_u, inner_u, sign in ((0, BS[0], BS[1], 1), (4, BS[5], BS[4], -1)):
        span = 'ABCDE'[i]
        end_bent, inner_bent = (1, 2) if i == 0 else (6, 5)
        # Row near the end bent (sheet 11): 3.000 m from the bearing on each exterior beam, 1.870 + 3 @ 2.045 between.
        south = sx(end_u, YS[0]) + sign * 3.0
        north = sx(end_u, YS[6]) + sign * 3.0
        # Chain from the acute-corner exterior bay towards the other exterior bay (south first in Span A).
        chain = (south if i == 0 else north) - sign * np.r_[0, 1.870, 1.870 + 2.045 * np.arange(1, 4)]
        stations = {}
        if i == 0:
            stations.update({j: chain[j] for j in range(5)}); stations[5] = north
        else:
            stations.update({5 - k: chain[k] for k in range(5)}); stations[0] = south
        for row, target in ((0 if i == 0 else 2, 'end'), (2 if i == 0 else 0, 'inner')):
            for j in range(6):
                pid = f'diaphragm_{i}_{row}_{j}'
                d = native(pid)
                ym = (YS[j] + YS[j + 1]) / 2
                x_old = d.bounds[0, 0]
                if target == 'end':
                    x_new = stations[j] - 0.065
                    where = f'near Bent {end_bent}'
                    note = (f'Moved to the sheet 11 station {stations[j]:+.3f} m (3.000 m from the Bent {end_bent} bearing '
                            'on the exterior beam, 1.870 + 3 @ 2.045 m between bays).')
                else:
                    xb = sx(inner_u, ym)
                    x_new = xb - 0.13 if i == 0 else xb
                    where = f'at Bent {inner_bent}'
                    note = (f'Moved to the Bent {inner_bent} bearing line on the Span {span} side (sheet 11; the small '
                            'offset from the bearing line is not dimensioned).')
                v = d.vertices.copy()
                v[:, 0] += x_new - x_old
                v[:, 2] += deck(x_new, ym) - deck(x_old, ym)
                store(pid, trimesh.Trimesh(v, d.faces, process=False), note,
                      name=f'Span {span} | MC460 channel diaphragm {where}, between Beams {7 - j} and {6 - j}',
                      station_x_m=round(float(x_new + 0.065), 4))
                parts[pid]['basis'] = 'Channel envelope at dimensioned framing-plan station'
        removed += [f'diaphragm_{i}_1_{j}' for j in range(6)]

    # ---- F5: Bent 2 / Bent 5 cap bottom and pile tops ----------------------------------------------------------
    for b in (1, 4):
        z = CAP_BOTTOM_Z[b]
        for pid, old in [(f'cap_{b}', 5.509219)] + [(f'pile_stub_{b}_{j}', 5.509219) for j in range(9)]:
            m = native(pid)
            v = m.vertices.copy()
            hit = np.isclose(v[:, 2], old, atol=2e-6)
            expect(hit.any(), pid)
            v[hit, 2] = z
            if pid.startswith('cap'):
                store(pid, trimesh.Trimesh(v, m.faces, process=False),
                      'Bottom corrected to Bott./Cap Elev. 215.585 (sheet 10). Seat steps El. 216.900 / 216.940 / '
                      '216.870 are not reproduced; see known_deviations.', bottom_el_m=215.585)
            else:
                store(pid, trimesh.Trimesh(v, m.faces, process=False),
                      'Top follows the cap bottom, El. 215.585 (sheet 10).')

    # ---- F6: bridge rails ------------------------------------------------------------------------------------
    prof = [(0, 0), (.4, 0), (.4, .1), (.275, .28), (.225, .84), (0, .84)]   # (inward from outer face, height)
    stations = np.linspace(-DECK_END_U, DECK_END_U, 6)
    for side in (-1, 1):
        edge = side * 5.86
        for i, (a, b) in enumerate(zip(stations[:-1], stations[1:])):
            pid = f'rail_{side}_{i}'

            def at(u, v, h):
                y = edge - side * v
                x = sx(u, y)
                return (x, y, deck(x, y) if h == 0 else grade(x) - 0.02 * 5.46 + h)

            store(pid, sweep(prof, np.linspace(a, b, max(2, int((b - a) / .6) + 1)), at),
                  'Section rebuilt to sheet 17 Section D-D and sheet 14: 400 mm base with toe at |Y| = 5.460 '
                  '(10.920 m clear roadway), 100 mm vertical toe, faces through (5.585, 0.280) and (5.635, 0.840), '
                  '225 mm top, 50 mm coping outside.',
                  base_width_m=0.4, top_width_m=0.225, toe_height_m=0.1, clear_roadway_m=10.92)
            parts[pid]['pdf_pages'] = [6, 14, 16, 17]

    # ---- F7: plan beam numbering (names only) -------------------------------------------------------------------
    rule = 'Plan numbering per sheet 11: Beam 1 is the north exterior line.'
    for pid, p in parts.items():
        bits = pid.split('_')
        if pid.startswith('beam_'):
            i, j = int(bits[1]), int(bits[2])
            expect(p['name'] == f'Span {"ABCDE"[i]} | W840x193 beam {j + 1}', pid)
            label(pid, rule, f'Span {"ABCDE"[i]} | W840x193 {plan_beam(j)}')
        elif pid.startswith(('Bent_', 'Pier_')) and '_bearing_' in pid:
            n = int(bits[-1])
            label(pid, rule, f'{bits[0]} {bits[1]} | bearing under {plan_beam(n - 1)}')
        elif pid.startswith('ped_'):
            j = int(bits[2])
            label(pid, rule, p['name'].replace(f'pedestal {j + 1}', f'pedestal under {plan_beam(j)}'))
        elif pid.startswith('diaphragm_') and int(bits[1]) in (1, 2, 3):
            i, row, j = map(int, bits[1:])
            label(pid, rule, f'Span {"ABCDE"[i]} | diaphragm row {row + 1}, between Beams {7 - j} and {6 - j}')

    # ---- Remove the parts with no plan counterpart -----------------------------------------------------------
    gone = set(removed)
    expect(len(gone) == 14 and gone <= set(parts), 'parts to remove')
    keep = [m for m in gltf['meshes'] if m['name'] not in gone]
    index = {id(m): k for k, m in enumerate(keep)}
    old_meshes = gltf['meshes']
    nodes = [gltf['nodes'][0]]
    for node in gltf['nodes'][1:]:
        if node['name'] in gone:
            continue
        node['mesh'] = index[id(old_meshes[node['mesh']])]
        nodes.append(node)
    nodes[0]['children'] = list(range(1, len(nodes)))
    gltf['nodes'], gltf['meshes'] = nodes, keep
    manifest['parts'] = [p for p in manifest['parts'] if p['id'] not in gone]
    for item in manifest.get('detail_coverage', []):
        item['part_ids'] = [x for x in item['part_ids'] if x not in gone]
    changes = [c for c in changes if c not in gone]
    for pid in changes:
        meshes[pid]['extras'].update(parts[pid])

    # ---- Write ---------------------------------------------------------------------------------------------------
    gltf['buffers'][0]['byteLength'] = len(binary)
    while len(binary) % 4:
        binary.append(0)
    encoded = json.dumps(gltf, ensure_ascii=True, separators=(',', ':')).encode()
    encoded += b' ' * ((-len(encoded)) % 4)
    out = (struct.pack('<III', 0x46546c67, 2, 28 + len(encoded) + len(binary)) +
           struct.pack('<II', len(encoded), 0x4e4f534a) + encoded + struct.pack('<II', len(binary), 0x004e4942) + binary)
    backup = ROOT / 'data/fem_research'
    backup.mkdir(exist_ok=True)
    (backup / 'sr8_yellow_before_review_correction.glb').write_bytes(original)
    (backup / 'sr8_yellow_manifest_before_review_correction.json').write_bytes(mp.read_bytes())
    path.write_bytes(out)
    manifest['review_correction'] = TAG
    manifest['revision'] = '1.1-drawing-review'
    manifest['review_correction_record'] = dict(
        source_pdf_pages=[5, 8, 9, 10, 11, 13, 14, 17, 18, 19, 25],
        printed_sheets='PDF pages 1-20 are printed sheets 1-20; PDF 25 is shop sheet M1',
        findings={
            'F1': 'End bents 1/6: integral bent El. 216.100 to deck soffit, 150 mm ledge at deck - 0.300 (sheets 8, 9)',
            'F2': 'End-bent piles: 4 existing + 2 new continuing, 2 battered cut off at El. 215.800 (sheet 8)',
            'F3': 'Approach slabs: square end X = +/-52.856, 10.920 m slab + 450 x 5030 curb strips (sheet 18)',
            'F4': 'End-span MC460 diaphragms: 24 (two per bay) at sheet 11 stations; middle rows removed (sheet 11, M1)',
            'F5': 'Bents 2/5 cap bottom El. 215.585 and pile tops (sheet 10); seat steps deferred',
            'F6': 'Bridge rail section per sheet 17 D-D, 10.920 m clear roadway (sheet 14)',
            'F7': 'Names: Beam 1 north (sheet 11); ids unchanged'},
        changed_parts=changes, removed_parts=sorted(gone),
        before_glb_sha256=before, after_glb_sha256=hashlib.sha256(out).hexdigest())
    deviations = [d for d in manifest.get('known_deviations', [])
                  if d.get('id') not in ('bent-2-5-seat-steps', 'approach-corner-squares')]
    deviations += [
        dict(id='bent-2-5-seat-steps', parts='cap_1, cap_4, ped_1_*, ped_4_*, Bent_2_bearing_*, Bent_5_bearing_*',
             source='sheet 10 (Elevation), sheets 11 and 13 (shim table, Type B bearing)',
             deviation='Cap tops stay at the derived seat El. 216.809; the dimensioned seats are El. 216.900 / 216.940 / '
                       '216.870 (steps 1.830 / 10.605 / 4.315 m from the south end of Bent 2), 6-62 mm above the '
                       'modelled bearing bottoms.',
             reason='Bearings hang from girders set at a nominal 90 mm haunch; reseating them needs the girder grade '
                    'reconciled with the 135 mm bearing stack and the shim table, beyond this correction.'),
        dict(id='approach-corner-squares', parts='approach_-1, approach_1, deck',
             source='sheet 18 (Plan - East Approach), sheet 14 (Half Plan)',
             deviation='The approach slabs keep the modelled skew start at the deck-end joint across the full width; '
                       'the plan squares the slab and bridge-floor corners outside the 10.620 m core (|Y| > 5.310) '
                       'and adds a 300 mm pavement support at the far end.',
             reason='The deck corner details are not part of this correction; the core plan outline controls.')]
    manifest['known_deviations'] = deviations
    mp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in manifest['review_correction_record'].items() if k != 'changed_parts'}))
    print(len(changes), 'parts changed,', len(gone), 'removed')


if __name__ == '__main__':
    correct()

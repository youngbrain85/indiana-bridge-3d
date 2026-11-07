"""Third drawing-confirmed correction of SR 8 over Yellow River (sr8-yellow): the two known deviations left by the first
two corrections. Runs after correct_sr8_yellow_review.py (revision 1.1) and correct_sr8_yellow_review_2.py (1.2).

    python scripts/correct_sr8_yellow_review.py      # revision 1.1
    python scripts/correct_sr8_yellow_review_2.py    # revision 1.2
    python scripts/correct_sr8_yellow_review_3.py    # this one (revision 1.3-deviations)

Source: INDOT B-23076 (1997), data/bridges/sr8-yellow/drawings.pdf; PDF pages 1-20 are printed sheets 1-20. Native axes
as before: X station (east), Y north, Z = El. - 210.000; support lines X = u - tan(49 deg) Y; deck top
D(X, Y) = 8.257 - X^2/15240 - 0.02|Y| (sheet 5 P.G. elevations 218.151 / 218.200 / 218.249 / 218.257 check it).

1. bent-2-5-seat-steps (RESOLVE). Sheet 10 (Elevation and Plan - Bent No. 2; Bent 5 by 180 deg rotation): the cap is
   16.750 x 0.760 m with ends and step lines square to the bent, bottom El. 215.585 and seats El. 216.900 / 216.940 /
   216.870 over 1.830 / 10.605 / 4.315 m from the south end (heights 1315 / 1355 / 1285; 16.96 m3 against the bill's
   17.0 m3). There are no pedestals: the bearings stand on the cap. Sheet 13 Type "B": 75 mm pad (230 x 355) and 60 mm
   top plate (260 x 405) = 135 mm on the seat, then the shim plate (260 x 290, sheet 11 shim table) and the 290 x 12
   splice plate under the beam flange. Sheet 15 Table of Fillet Dimensions gives the girder grade: Dim "A" (deck
   surface to top of beam flange at the beam centre line) = 203 / 204 / 217 / 240 / 217 / 204 / 203 mm for Beams 1-7.
   With the W840 depth the three sources close within 0.8 mm at all 14 Bent 2 / 5 bearings (seat + 0.135 + shim +
   0.012 + 0.840 = D - Dim "A"), and at Bents 1 / 6 they give Pour 1 heights of 737-811 mm (sheet 9: 737 min, 810 max).
   The model had every girder top at D - 0.290 (a nominal 90 mm haunch), so the steel stood 50-87 mm low and the seats
   were replaced by a flat cap at El. 216.809 and 45-125 mm pedestals. Now:
   - beams, field splices and their bolts rise by 0.290 - Dim "A" per beam line (87 / 86 / 73 / 50 mm);
   - haunch bottoms follow the flanges (fillet = Dim "A" - 200 mm at the centre line); haunch tops stay on the soffit;
   - diaphragms follow both beams (channels sheared between the two beam lines, connection angles moved rigidly);
   - cap_1 / cap_4 are rebuilt as drawn; ped_1_* / ped_4_* (12 parts) are removed;
   - the field splices (and their bolts) are sheared to the beam grade, so the 12 mm splice plate follows the flange;
   - Bent 2 / 5 bearings are rebuilt as the Type "B" stack on the seat; the shim closes to the splice plate at the
     bearing centre line, within -0.8 / +0.7 mm of the shim table (the 1 mm rounding of the four sources; known
     deviation bent-2-5-shim-rounding), its top on the beam grade;
   - Bent 1 / 6 bearings are rebuilt as drawn (they had the Type "B" pad and plate, 135 mm): Type "A" = PL 230 x 25 x
     600, S75 x 11 (76 mm, 400 long), PL 150 x 25 x 400 and the sheet 11 shim (11-50 mm) under the beam; the Pour 1
     seat takes the closure (737-811 mm above El. 216.100; sheet 9: 737 min, 810 max);
   - final pass: the new end-span beams (beam_0_*, beam_4_*) extend 150 mm past the end-bent bearing centre line with a
     square end (sheet 11 New and Existing Beam Elevation 150 + 10538 + 234 = 10922; shop sheets 1-3, PDF 26-28), with
     the 125 x 110 mm top-flange corner notch (Views "A" / "B"); their haunches run to the new end and the end-bent
     pockets are cut for them, so the whole 150 mm Type "A" shim bears on the flange. The Type "A" shims are 150 x 321
     (approved shop sheet S1, PDF 24, revises sheet 13's 350);
   - Pier 3 / 4 bearings move up with their beams; the pedestals under the Bent 1 / 6 and Pier 3 / 4 bearings (derived
     contact envelopes) follow, and the two bearings that stood directly on the retained pier caps (Pier 3 Beam 1,
     Pier 4 Beam 7) get pedestals ped_2_6 / ped_3_0 (the retained pier seats are not in the bundle; the pier caps are
     unchanged; known deviation pier-3-4-seats);
   - the beam-end pockets in the integral end bents cap_0 / cap_5 are recut.
2. approach-corner-squares (RESOLVE). Sheet 14 Half Plan (46607 = 34389 + 12218, the 600 mm strips squared) and sheet
   18 Plan (approach start squared over the 150 + 450 mm strips): outside the 10.620 m core (|Y| > 5.310) the bridge
   floor end and the approach start are square to the roadway at the core-edge crossing of the skew line
   (X = -/+46.607 and -/+34.389). Sheet 16 Rail Plan: Panel "B" 80996 on each side ends square there. Sheet 19
   Section "C-C" and sheet 18 Plan: an L-shaped pavement support 750 x 300 under the far end of the 260 mm slab (400 mm
   under the slab), a 50 mm expansion joint and a 300 mm upstand to the surface, 10.920 m long (0.303 m2 x 10.92 =
   3.31 m3; bill 3.3 m3). Changed: deck, joint_-1 / joint_1, approach_-1 / approach_1, the four end rail panels and
   the end bents (the bent top follows the squared floor end: deck soffit under the floor, slab bearing level under
   the approach). Added: pavement_support_-1 / pavement_support_1. The joint strips now fill the modelled 25 mm
   separation between the floor end and the approach (sheets 9 / 18 Section A-A: Type 1A joint at that interface)
   instead of reaching 12 mm into the deck; the joint opening and depth (Bridge Std. 724-BJTS-01) are not in the bundle
   (known deviation deck-joint-type-1a).

The end bents, deck, joints and approach slabs are built as single closed solids over plan regions (terraced, as in the
second correction); only the beam-end pockets are cut with manifold3d. Requires numpy, trimesh, shapely, manifold3d and
the two earlier scripts in the same folder.
"""
import hashlib
import json
import struct
import sys
from pathlib import Path

import numpy as np
import trimesh
from shapely.geometry import Polygon
from shapely.ops import unary_union

sys.path.insert(0, str(Path(__file__).resolve().parent))
from correct_sr8_yellow_review import (APPROACH_START_U, BASE, BS, COS, DECK_END_U, PAVEMENT_END_X, ROOT,  # noqa: E402
                                       SIN, TAN, YS, deck, grade, sweep, sx)
from correct_sr8_yellow_review_2 import (BENT_BOTTOM_Z, BENT_SEAT, SLAB_T, bent_plan, bodies, rot,  # noqa: E402
                                         split_crown, strips, terraced)
from correct_sr8_yellow_review_2 import REVISION as SECOND_REVISION  # noqa: E402
from correct_sr8_yellow_review_2 import TAG as SECOND_TAG  # noqa: E402

TAG = 'sr8-yellow-review-3-2026-11'
REVISION = '1.3-deviations'
BEFORE_SHA = 'b36087a19c0ac603912d3f30026e12fd5265b92ed4bc9e5e4034528c28c51e69'   # after the second correction

OLD_TOP = 0.290                                    # model girder top below the deck surface before this correction
FILLET_A = {1: 0.203, 2: 0.204, 3: 0.217, 4: 0.240, 5: 0.217, 6: 0.204, 7: 0.203}   # sheet 15, Dim "A" by Beam No.
RAISE = [round(OLD_TOP - FILLET_A[7 - j], 3) for j in range(7)]                     # beam line j (south -> north)
W840 = 0.840
SHIM_MM = {1: {1: 11, 2: 50, 3: 11, 4: 35, 5: 32, 6: 20, 7: 30},                    # sheet 11 shim table, Beam No.
           2: {1: 14, 2: 50, 3: 11, 4: 32, 5: 28, 6: 12, 7: 30},
           5: {1: 30, 2: 12, 3: 28, 4: 32, 5: 11, 6: 50, 7: 14},
           6: {1: 30, 2: 20, 3: 32, 4: 35, 5: 11, 6: 50, 7: 11}}
SEATS = ((1.830, 216.900), (10.605, 216.940), (4.315, 216.870))                    # sheet 10, from the south end
CAP_HALF_L, CAP_HALF_W, CAP_BOTTOM_Z = 8.375, 0.380, 215.585 - 210                 # sheet 10 (16750 x 760)
PAD, PLATE, SHIM_PLAN, SPLICE_T = (0.230, 0.355, 0.075), (0.260, 0.405, 0.060), (0.260, 0.290), 0.012   # sheet 13
# Type "A" (sheet 13, Bents 1 / 6), bottom to top: PL 230 x 25 x 600, S75 x 11 (76 deep, 400 long across the beam),
# PL 150 x 25 x 400, shim PL 150 x 321 (thickness: sheet 11): 126 mm + shim. (along X, across Y, thickness)
A_BASE, A_TOP, A_SHIM, A_S_LEN, A_S_DEPTH = (0.230, 0.600, 0.025), (0.150, 0.400, 0.025), (0.150, 0.321), 0.400, 0.076
# Shim width 321 (was 350): approved shop sheet S1 (PDF 24, "Shim PL 150 x 321", edge distances 14 / 15, shim list).
S75 = (0.064, 0.0066, 0.0089)                      # S75 x 11 (S3 x 7.5) flange width, flange and web thickness
BEAM_END = 0.150                                   # new beams extend 150 mm past the end-bent bearing (sheet 11; PDF 26-28)
NOTCH = (0.125, 0.110)                             # top-flange corner notch at that end (PDF 26-28 Views "A" / "B")
CORE_Y = 5.310                                     # 10620 core (sheets 14, 18)
SUPPORT = [(-0.40, -0.56), (0.35, -0.56), (0.35, 0.0), (0.05, 0.0), (0.05, -SLAB_T), (-0.40, -SLAB_T)]  # sheet 19 C-C
SUPPORT_Y = 5.46                                   # 10920 (sheet 18)
JOINT_DEPTH = 0.08                                 # the model's visual joint strip depth, kept (schematic)


def beam_no(j):
    return 7 - j


def beam_label(j):
    n = beam_no(j)
    return f'Beam {n}' + (' (north exterior)' if n == 1 else ' (south exterior)' if n == 7 else '')


def end_line(u, y):
    """Bridge-floor end / joint line: skew across the core, square to the roadway outside it (sheets 14, 18)."""
    return sx(u, np.clip(y, -CORE_Y, CORE_Y))


def seat_z(b, y):
    """Sheet 10 seat level at a point of the Bent 2 (b = 1) or Bent 5 (b = 4, 180 deg rotation) bearing line."""
    s = (y if b == 1 else -y) / COS + CAP_HALF_L          # along the bent from the Bent 2 south end
    edge = 0.0
    for length, el in SEATS:
        edge += length
        if s <= edge + 1e-9:
            return el - 210
    raise ValueError('outside the cap')


def raise_at(j, y):
    """Raise of a diaphragm point in bay j (between beam lines j and j + 1), linear between the two beams."""
    t = (y - YS[j]) / (YS[j + 1] - YS[j])
    return RAISE[j] + (RAISE[j + 1] - RAISE[j]) * t


def shells(mesh):
    """Vertex index sets of the closed shells of a mesh (union-find over faces)."""
    parent = np.arange(len(mesh.vertices))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    for a, b, c in mesh.faces:
        for q in (b, c):
            ra, rq = find(a), find(q)
            if ra != rq:
                parent[rq] = ra
    roots = np.array([find(v) for v in range(len(parent))])
    used = np.unique(mesh.faces)
    return [np.intersect1d(np.nonzero(roots == r)[0], used) for r in np.unique(roots[used])]


def tbox(x0, x1, y0, y1, z0, z1):
    return trimesh.creation.box(bounds=[[x0, y0, z0], [x1, y1, z1]])


def correct():
    mp = BASE / 'model_manifest.json'
    manifest = json.loads(mp.read_text(encoding='utf-8'))
    if manifest.get('review_correction_3') == TAG:
        print('Already corrected.')
        return
    if manifest.get('review_correction_2') != SECOND_TAG or manifest.get('revision') != SECOND_REVISION:
        raise ValueError('run scripts/correct_sr8_yellow_review_2.py first (revision 1.2 expected)')
    path = BASE / 'model.glb'
    original = path.read_bytes()
    before = hashlib.sha256(original).hexdigest()
    if before != BEFORE_SHA or manifest['review_correction_2_record']['after_glb_sha256'] != BEFORE_SHA:
        raise ValueError('model.glb is not the output of the second correction')
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

    def native(pid):
        """Mesh of a part in native axes; GLB stores (X, Z, -Y)."""
        prim = meshes[pid]['primitives'][0]
        s = read(prim['attributes']['POSITION']).astype(np.float64)
        return trimesh.Trimesh(np.c_[s[:, 0], -s[:, 2], s[:, 1]], read(prim['indices']).reshape(-1, 3), process=False)

    def primitive(solid, color):
        v = np.asarray(solid.vertices, dtype=np.float64)
        prim = {'POSITION': append(np.c_[v[:, 0], v[:, 2], -v[:, 1]].astype('<f4'), 'VEC3', 5126),
                'COLOR_0': append(np.tile(color, (len(v), 1)).astype('u1'), 'VEC4', 5121)}
        gltf['accessors'][prim['COLOR_0']]['normalized'] = True
        return dict(attributes=prim, indices=append(np.asarray(solid.faces).reshape(-1, 1).astype('<u4'), 'SCALAR', 5125),
                    mode=4)

    changes, added = [], []

    def check(pid, solid):
        if not solid.is_watertight or solid.volume <= 0:
            raise ValueError(f'{pid}: invalid corrected solid')

    def store(pid, solid, note, name=None, pages=None, basis=None, **dims):
        check(pid, solid)
        prim = meshes[pid]['primitives'][0]
        color = read(prim['attributes']['COLOR_0'])[0]
        meshes[pid]['primitives'] = [primitive(solid, color)]
        p = parts[pid]
        p['bounds_m'] = np.round(solid.bounds, 6).tolist()
        p['volume_m3'] = round(float(solid.volume), 9)
        p['dimensions'].update(dims)
        if name:
            p['name'] = name
        if pages:
            p['pdf_pages'] = pages
        if basis:
            p['basis'] = basis
        p['note'] = (p.get('note', '') + ' ' + note).strip()
        if pid not in changes:
            changes.append(pid)

    def add(pid, solid, like, anchor, note, name, pages, basis, dims, before=False):
        """New part: manifest entry with the fields of a similar part, mesh with its colour, node in the scene."""
        check(pid, solid)
        if pid in parts:
            raise ValueError(pid + ' exists')
        entry = dict(id=pid, name=name, layer=parts[like]['layer'], color=parts[like]['color'], pdf_pages=pages,
                     basis=basis, note=note, dimensions=dims, bounds_m=np.round(solid.bounds, 6).tolist(),
                     volume_m3=round(float(solid.volume), 9))
        color = read(meshes[like]['primitives'][0]['attributes']['COLOR_0'])[0]
        meshes[pid] = dict(name=pid, extras=dict(processed=True), primitives=[primitive(solid, color)])
        parts[pid] = entry
        k = [p['id'] for p in manifest['parts']].index(anchor)
        manifest['parts'].insert(k if before else k + 1, entry)
        added.append(pid)

    def moved(pid, dz):
        m = native(pid)
        v = m.vertices.copy()
        v[:, 2] += dz
        return trimesh.Trimesh(v, m.faces, process=False)

    def expect(cond, what):
        if not cond:
            raise ValueError('Model is not in the expected state after the second correction: ' + what)

    def beam_end(pid, bm, j, i):
        """Extend a new end-span beam 150 mm past the end-bent bearing centre line with a square end (sheet 11 New and
        Existing Beam Elevation: 150 + 10538 + 234 = 10922; shop sheets 1-3, PDF 26-28) and clip the top-flange corner
        125 x 110 (Views "A" / "B", "notch top flange only") on the side nearest the skewed bridge-floor end."""
        n = beam_no(j)
        v = bm.vertices
        xs = np.unique(np.round(v[:, 0], 6))
        x_end = xs[0] if i == 0 else xs[-1]
        sec = v[np.abs(v[:, 0] - x_end) < 1e-6]
        yr = np.round(sec[:, 1] - YS[j], 5)
        h_end = sec[:, 2] - (deck(x_end, YS[j]) - FILLET_A[n])
        hr = np.round(h_end, 4)
        bf, tw = float(yr.max()), float(np.unique(np.abs(yr))[0])
        d, tf = float(-hr.min()), float(-np.unique(hr)[-2])
        ring = [(-bf, -d), (bf, -d), (bf, -d + tf), (tw, -d + tf), (tw, -tf), (bf, -tf), (bf, 0), (-bf, 0), (-bf, -tf),
                (-tw, -tf), (-tw, -d + tf), (-bf, -d + tf)]
        expect(len(sec) == 12 and {(round(a, 5), round(b, 4)) for a, b in ring} == set(zip(yr, hr)),
               pid + ' end section')
        for x in xs:                                                    # same section at every station
            q = v[np.abs(v[:, 0] - x) < 1e-6]
            expect(len(q) == 12 and np.allclose(np.sort(q[:, 2] - deck(x, YS[j]) + FILLET_A[n]), np.sort(h_end),
                                                atol=3e-5), pid + ' sections')
        sgn = -1 if i == 0 else 1                                       # outward along X at this end
        x_new = x_end + sgn * BEAM_END
        stations = np.sort(np.r_[xs, x_new])
        beam = sweep(ring, stations, lambda x, a, h: (x, YS[j] + a, deck(x, YS[j]) - FILLET_A[n] + h))
        expect(abs(beam.volume - bm.volume - Polygon(ring).area * BEAM_END) < 2e-5, pid + ' extension')
        # notch: Bent 1 (west end) clips the south corner, Bent 6 (east end) the north corner (180 deg rotation)
        side = -sgn                                                     # +1: corner at YS - bf (Bent 1)
        ye = YS[j] - side * bf
        # (a, b): a inward from the end along the beam, b inward from the flange edge; clip line (125, 0) - (0, 110)
        a1, b1, a2, b2 = NOTCH[0], 0.0, 0.0, NOTCH[1]
        t = 0.2
        p1, p2 = (a1 + t * (a1 - a2), b1 + t * (b1 - b2)), (a2 + t * (a2 - a1), b2 + t * (b2 - b1))
        local = [p1, p2, (-0.03, p2[1]), (-0.03, -0.03), (p1[0], -0.03)]        # outside the beam beyond the clip line
        plan = [(x_new - sgn * a, ye + side * b) for a, b in local]
        z_top = deck(x_new, YS[j]) - FILLET_A[n]
        prism = sweep(plan, [z_top - tf - 0.03, z_top + 0.01], lambda z, x, y: (x, y, z))
        notched = trimesh.boolean.difference([beam, prism], engine='manifold')
        cut = beam.volume - notched.volume
        if not notched.is_watertight or bodies(notched) != 1 or abs(cut - 0.5 * NOTCH[0] * NOTCH[1] * tf) > 2e-6:
            raise ValueError(pid + f': invalid notch ({cut:.6f} m3)')
        bent = 1 if i == 0 else 6
        note = (f' Final pass: extended {BEAM_END * 1000:.0f} mm past the Bent {bent} bearing centre line to the square '
                f'beam end of sheet 11 (New and Existing Beam Elevation: 150 + 10538 + 234 = 10922 mm new beam) and shop '
                f'sheets 1-3 (PDF 26-28), with the 125 x 110 mm top-flange corner notch (Views "A" / "B") on the '
                f'{"south" if side > 0 else "north"} corner, nearest the skewed bridge-floor end.')
        return notched, dict(note=note, length_m=round(float(np.ptp(notched.bounds[:, 0])), 3),
                             end_past_bearing_m=BEAM_END, top_flange_notch_m=list(NOTCH))

    # ---- Starting-state checks ------------------------------------------------------------------------------
    for i in range(5):
        for j in range(7):
            v = native(f'beam_{i}_{j}').vertices
            gap = deck(v[:, 0], YS[j]) - v[:, 2]
            gap = gap[gap < 0.30]                                       # top face of the top flange
            expect(len(gap) > 10 and np.allclose(gap, OLD_TOP, atol=2e-4), f'beam_{i}_{j} top at deck - 0.290')
    for b in (1, 4):
        c = native(f'cap_{b}')
        expect(len(c.vertices) == 8 and np.allclose(c.bounds[:, 2], [CAP_BOTTOM_Z, 6.809219], atol=2e-6), f'cap_{b}')
    removed = [f'ped_{b}_{j}' for b in (1, 4) for j in range(7) if f'ped_{b}_{j}' in parts]
    expect(len(removed) == 12, 'twelve Bent 2 / 5 pedestals')
    for b, name in ((0, 'Bent_1'), (1, 'Bent_2'), (2, 'Pier_3'), (3, 'Pier_4'), (4, 'Bent_5'), (5, 'Bent_6')):
        for j in range(7):
            bb = native(f'{name}_bearing_{j + 1}').bounds
            expect(np.allclose(bb.mean(axis=0)[:2], [sx(BS[b], YS[j]), YS[j]], atol=1e-3), f'{name}_bearing_{j + 1}')
            if f'ped_{b}_{j}' in parts:
                expect(abs(native(f'ped_{b}_{j}').bounds[1, 2] - bb[0, 2]) < 1e-5, f'ped_{b}_{j} under its bearing')
    expect(set(d['id'] for d in manifest.get('known_deviations', [])) >= {'bent-2-5-seat-steps', 'approach-corner-squares'},
           'known deviations')
    expect(np.allclose(native('deck').bounds[:, 0], [-47.296677, 47.296677], atol=1e-5), 'deck skew ends')
    for s in (-1, 1):
        v = native(f'joint_{s}').vertices
        expect(np.allclose(np.unique(np.round(s * (v[:, 0] + TAN * v[:, 1]), 4)), [40.486, 40.51]), f'joint_{s}')
        a = native(f'approach_{s}').vertices
        expect(abs(np.min(s * (a[:, 0] + TAN * a[:, 1])) - APPROACH_START_U) < 1e-4, f'approach_{s} skew start')
        for i in (0, 4):
            r = native(f'rail_{s}_{i}').vertices
            expect(abs(np.max(np.abs(r[:, 0] + TAN * r[:, 1])) - DECK_END_U) < 1e-4, f'rail_{s}_{i} skew end')
    expect('pavement_support_1' not in parts and 'ped_2_6' not in parts and 'ped_3_0' not in parts, 'new ids free')

    # ---- 1a: girder grade from the sheet 15 fillet table --------------------------------------------------------
    splice_plane = {}
    for j in range(7):
        n, dz = beam_no(j), RAISE[j]
        for i in range(5):
            pid = f'beam_{i}_{j}'
            bm = moved(pid, dz)
            extra = {}
            if i in (0, 4):                         # new end-span beam: 150 mm past the end-bent bearing, notched
                bm, extra = beam_end(pid, bm, j, i)
            store(pid, bm,
                  f'Third correction: raised {dz * 1000:.0f} mm to the sheet 15 fillet table (top of flange = deck surface '
                  f'- Dim "A" {FILLET_A[n] * 1000:.0f} mm at the beam centre line), which closes with the sheet 10 seats, '
                  f'sheet 13 Type B stack and sheet 11 shims within 0.8 mm.' + extra.pop('note', ''),
                  pages=sorted(set(parts[pid]['pdf_pages']) | {10, 13, 15} | ({26, 27, 28} if extra else set())),
                  top_below_deck_m=FILLET_A[n], **extra)
            hid = f'haunch_{i}_{j}'
            h = native(hid)
            v = h.vertices.copy()
            low = v[:, 2] < deck(v[:, 0], v[:, 1]) - 0.25
            expect(low.sum() * 2 == len(v), hid + ' bottom vertices')
            v[low, 2] += dz
            hm = trimesh.Trimesh(v, h.faces, process=False)
            if j == 3 or i in (0, 4):
                # crown beam: the top follows the soffit ridge at Y = 0 (the old top ran straight across);
                # end spans: the haunch runs over the full flange length, to the extended beam end
                (x0, y0, _), (x1, y1, _) = h.bounds
                bx0, bx1 = bm.bounds[:, 0]
                hm = terraced([(q, ('flange', lambda x, y, j=j, n=n: deck(x, YS[j]) - FILLET_A[n]),
                                ('soffit', lambda x, y: deck(x, y) - 0.2))
                               for q in strips(Polygon([(bx0, y0), (bx1, y0), (bx1, y1), (bx0, y1)]))])
                if bodies(hm) != 1 or not (abs(bx1 - x1) < 1e-6 if i == 0 else abs(bx0 - x0) < 1e-6 if i == 4 else
                                           abs(bx0 - x0) + abs(bx1 - x1) < 1e-6):
                    raise ValueError(hid + ': invalid solid')
            store(hid, hm,
                  f'Third correction: bottom raised {dz * 1000:.0f} mm with the flange; fillet {FILLET_A[n] * 1000 - 200:.0f} mm '
                  f'at the beam centre line (sheet 15 Dim "A" - 200 mm deck), top on the deck soffit.',
                  name=f'Span {"ABCDE"[i]} | haunch (fillet) over {beam_label(j)}', pages=[14, 15],
                  basis='Sheet 15 fillet depth over the flange width; the 100 mm fillet extension beyond the flange '
                        '(Detail "A") is not modelled',
                  fillet_at_centre_line_m=round(FILLET_A[n] - 0.2, 3))
            parts[hid]['dimensions'].pop('nominal_thickness_m', None)
            parts[hid]['note'] = parts[hid]['note'].replace(
                'Haunch follows modeled grade, not a construction screed or camber table. ', '')
        for e in (0, 1):
            sp = f'field_splice_{j}_{e}'
            first = moved(sp, dz)
            xc = first.bounds.mean(axis=0)[0]
            slope = -2 * xc / 15240                     # grade of the beam (dD/dX) at the splice centre
            splice_plane[(j, e)] = (first.bounds[0, 2], slope, xc)    # bottom of the 12 mm splice plate: z(x)
            for pid in (sp, sp + '_bolts'):
                m = moved(pid, dz)
                v = m.vertices.copy()
                v[:, 2] += slope * (v[:, 0] - xc)
                store(pid, trimesh.Trimesh(v, m.faces, process=False),
                      f'Third correction: raised {dz * 1000:.0f} mm with the beam (sheet 15 fillet table) and sheared to '
                      f'the beam grade ({slope * 100:.2f} %), so the plates follow the flanges they are bolted to '
                      f'(they were level boxes).')

    # ---- 1b: diaphragms follow both beams ----------------------------------------------------------------------
    for pid in [p for p in parts if p.startswith('diaphragm_')]:
        j = int(pid.split('_')[-1])
        m = native(pid)
        v = m.vertices.copy()
        groups = shells(m)
        span = max(groups, key=lambda g: np.ptp(v[g, 1]))
        for g in groups:
            if g is span:
                v[g, 2] += raise_at(j, v[g, 1])                         # channel: sheared between the beam lines
            else:                                                       # connection angle: moved with its web
                y0, y1 = v[g, 1].min(), v[g, 1].max()
                yw = y0 if abs(y0 - YS[j]) < abs(y1 - YS[j + 1]) else y1
                v[g, 2] += raise_at(j, yw)
        store(pid, trimesh.Trimesh(v, m.faces, process=False),
              f'Third correction: follows Beams {beam_no(j)} and {beam_no(j + 1)} raised {RAISE[j] * 1000:.0f} / '
              f'{RAISE[j + 1] * 1000:.0f} mm (sheet 15 fillet table).')

    # ---- 1c: Bent 2 / 5 caps as drawn, Type B bearings on the seats ---------------------------------------------
    edges = np.cumsum([0.0] + [s for s, _ in SEATS]) - CAP_HALF_L
    prof = [(-CAP_HALF_L, CAP_BOTTOM_Z), (CAP_HALF_L, CAP_BOTTOM_Z)]
    for k in (2, 1, 0):                                                 # top, north to south
        prof += [(edges[k + 1], SEATS[k][1] - 210), (edges[k], SEATS[k][1] - 210)]
    for b in (1, 4):
        cap = sweep(prof, [-CAP_HALF_W, CAP_HALF_W],
                    lambda t, s, z: (BS[1] - s * SIN + t * COS, s * COS + t * SIN, z))
        if b == 4:                                                      # Bent 5 = Bent 2 by 180 deg rotation
            v = cap.vertices.copy()
            v[:, :2] *= -1
            cap = trimesh.Trimesh(v, cap.faces, process=False)
        old = native(f'cap_{b}').volume
        pid = f'cap_{b}'
        store(pid, cap, '', pages=[10],
              basis='Dimensioned cap outline, bottom elevation and seat steps; reinforcement and pile encasement omitted',
              length_m=16.75, width_m=0.76, seat_el_m=[216.9, 216.94, 216.87],
              seat_steps_m=[1.83, 10.605, 4.315], seat_steps_from='south end' if b == 1 else 'north end')
        parts[pid]['note'] = ('Third correction: rebuilt as drawn on sheet 10 (Plan and Elevation - Bent No. 2' +
                              ('' if b == 1 else '; Bent 5 by 180 deg rotation') +
                              '): 16.750 x 0.760 m with ends and step lines square to the bent, Bott./Cap Elev. 215.585, '
                              'Seat El. 216.900 / 216.940 / 216.870 over 1.830 / 10.605 / 4.315 m from the ' +
                              ('south' if b == 1 else 'north') + ' end (bill 17.0 m3). The bearings stand on the seats; '
                              'the separate pedestals of the earlier model are removed.')
        print(f'cap_{b}: {old:.3f} -> {cap.volume:.3f} m3')
        bent = 2 if b == 1 else 5
        for j in range(7):
            n = beam_no(j)
            pid = f'Bent_{bent}_bearing_{j + 1}'
            xb, yb = sx(BS[b], YS[j]), YS[j]
            z0 = seat_z(b, yb)
            sb = native(f'field_splice_{j}_{0 if b == 1 else 1}').bounds      # raised and sheared with the beam
            expect(sb[0, 0] < xb - PLATE[0] / 2 and sb[1, 0] > xb + PLATE[0] / 2, pid + ' under the splice plate')
            zf, slope, xc = splice_plane[(j, 0 if b == 1 else 1)]
            z_top = lambda x, zf=zf, slope=slope, xc=xc: zf + slope * (x - xc)  # splice-plate bottom on the grade
            shim = z_top(xb) - z0 - PAD[2] - PLATE[2]                           # at the bearing centre line
            table = SHIM_MM[bent][n] / 1000
            if abs(shim - table) > 0.001:
                raise ValueError(f'{pid}: shim {shim:.4f} does not close with the table {table:.3f}')
            pad = tbox(xb - PAD[0] / 2, xb + PAD[0] / 2, yb - PAD[1] / 2, yb + PAD[1] / 2, z0, z0 + PAD[2])
            plate = tbox(xb - PLATE[0] / 2, xb + PLATE[0] / 2, yb - PLATE[1] / 2, yb + PLATE[1] / 2,
                         z0 + PAD[2], z0 + PAD[2] + PLATE[2])
            shp = tbox(xb - SHIM_PLAN[0] / 2, xb + SHIM_PLAN[0] / 2, yb - SHIM_PLAN[1] / 2, yb + SHIM_PLAN[1] / 2,
                       z0 + PAD[2] + PLATE[2], z0 + PAD[2] + PLATE[2] + shim)
            sv = shp.vertices.copy()
            up = sv[:, 2] > z0 + PAD[2] + PLATE[2] + 1e-6
            sv[up, 2] = z_top(sv[up, 0])                                        # top on the flange grade
            shp = trimesh.Trimesh(sv, shp.faces, process=False)
            assembly = trimesh.util.concatenate([pad, plate, shp])
            if not assembly.is_watertight or bodies(assembly) != 3:
                raise ValueError(pid + ': invalid bearing assembly')
            store(pid, assembly,
                  f'Third correction: Type B stack of sheet 13 on the sheet 10 seat El. {z0 + 210:.3f}: 75 mm pad '
                  f'230 x 355, 60 mm top plate 260 x 405 and shim 260 x 290, {shim * 1000:.1f} mm at the bearing centre '
                  f'line (sheet 11 table {SHIM_MM[bent][n]} mm; see known_deviations bent-2-5-shim-rounding), its top on '
                  f'the beam grade under the 290 x 12 splice plate (field splice part). Three closed shells.',
                  pages=[10, 11, 13], basis='Dimensioned Type B stack on the drawn seat; laminations, bolts and anchors omitted',
                  seat_el_m=round(z0 + 210, 3), shim_thickness_m=round(shim, 4), shim_table_mm=SHIM_MM[bent][n],
                  shim_plan_m=list(SHIM_PLAN))

    # ---- 1d: other bearings and pedestals follow the beams -------------------------------------------------------
    for b, name in ((0, 'Bent_1'), (2, 'Pier_3'), (3, 'Pier_4'), (5, 'Bent_6')):
        for j in range(7):
            pid = f'{name}_bearing_{j + 1}'
            if b in (2, 3):
                bm = moved(pid, RAISE[j])
                store(pid, bm, f'Third correction: raised {RAISE[j] * 1000:.0f} mm with the beam (sheet 15 fillet table).')
            else:                                   # Type A at the integral end bents, rebuilt as drawn
                n, bent = beam_no(j), b + 1
                xb, yb = sx(BS[b], YS[j]), YS[j]
                beam = native(f'beam_{0 if b == 0 else 4}_{j}')                 # already raised
                end = beam.vertices[np.isclose(beam.vertices[:, 0], xb, atol=1e-4)]
                z_beam = deck(xb, yb) - FILLET_A[n] - W840
                expect(len(end) and abs(end[:, 2].min() - z_beam) < 2e-5, f'beam end at Bent {bent}')
                slope = -2 * xb / 15240
                shim = SHIM_MM[bent][n] / 1000
                z0 = z_beam - A_BASE[2] - A_S_DEPTH - A_TOP[2] - shim
                if not 0.736 <= z0 - BENT_BOTTOM_Z <= 0.812:                    # sheet 9 A-A: Pour 1 737 min / 810 max
                    raise ValueError(f'{pid}: Pour 1 height {z0 - BENT_BOTTOM_Z:.4f}')
                base = tbox(xb - A_BASE[0] / 2, xb + A_BASE[0] / 2, yb - A_BASE[1] / 2, yb + A_BASE[1] / 2,
                            z0, z0 + A_BASE[2])
                bf, tf, tw = S75
                prof = [(-bf / 2, 0), (bf / 2, 0), (bf / 2, tf), (tw / 2, tf), (tw / 2, A_S_DEPTH - tf),
                        (bf / 2, A_S_DEPTH - tf), (bf / 2, A_S_DEPTH), (-bf / 2, A_S_DEPTH), (-bf / 2, A_S_DEPTH - tf),
                        (-tw / 2, A_S_DEPTH - tf), (-tw / 2, tf), (-bf / 2, tf)]
                zs = z0 + A_BASE[2]
                s75 = sweep(prof, [yb - A_S_LEN / 2, yb + A_S_LEN / 2],
                            lambda y, xr, zr, xb=xb, zs=zs: (xb + xr, y, zs + zr))
                zt = zs + A_S_DEPTH
                top = tbox(xb - A_TOP[0] / 2, xb + A_TOP[0] / 2, yb - A_TOP[1] / 2, yb + A_TOP[1] / 2, zt, zt + A_TOP[2])
                shp = tbox(xb - A_SHIM[0] / 2, xb + A_SHIM[0] / 2, yb - A_SHIM[1] / 2, yb + A_SHIM[1] / 2,
                           zt + A_TOP[2], zt + A_TOP[2] + shim)
                sv = shp.vertices.copy()
                up = sv[:, 2] > zt + A_TOP[2] + 1e-6
                sv[up, 2] = z_beam + slope * (sv[up, 0] - xb)                   # top on the beam grade
                assembly = trimesh.util.concatenate([base, s75, top, trimesh.Trimesh(sv, shp.faces, process=False)])
                if not assembly.is_watertight or bodies(assembly) != 4:
                    raise ValueError(pid + ': invalid bearing assembly')
                bm = assembly
                store(pid, assembly,
                      f'Third correction: rebuilt as the Type A assembly of sheet 13 (it had the Type B pad and plate, '
                      f'135 mm): PL 230 x 25 x 600, S75 x 11 76 mm deep and 400 mm long across the beam (flange width '
                      f'64, flange 6.6 and web 8.9 mm thick from the S75 x 11 section), PL 150 x 25 x 400 and shim PL '
                      f'150 x 321 x {SHIM_MM[bent][n]} mm (width 321, not 350: approved shop sheet S1, PDF 24; thickness: '
                      f'sheet 11 table), 126 mm + shim, under the beam raised to the sheet 15 grade and extended 150 mm '
                      f'past the bearing, so the whole 150 mm shim length bears on the flange; the shim top follows the '
                      f'beam grade. The bottom, El. {z0 + 210:.3f}, is the Pour 1 seat '
                      f'({(z0 - BENT_BOTTOM_Z) * 1000:.0f} mm above El. 216.100; sheet 9: 737 min, 810 max). '
                      f'Four closed shells, encased in the integral bent.',
                      pages=[9, 11, 13, 24],
                      basis='Dimensioned Type A assembly (sheet 13, shop sheet S1); anchor bolts, welds and stiffeners '
                            'omitted',
                      bearing_type='A', stack_m=0.126, shim_thickness_m=shim, shim_table_mm=SHIM_MM[bent][n],
                      base_plate_m=[0.23, 0.6, 0.025], top_plate_m=[0.15, 0.4, 0.025], shim_plan_m=list(A_SHIM),
                      pour_1_seat_el_m=round(z0 + 210, 4))
                for k in ('pad_length_m', 'pad_width_m', 'pad_thickness_m', 'load_plate_thickness_m'):
                    parts[pid]['dimensions'].pop(k, None)
                parts[pid]['note'] = parts[pid]['note'].replace(
                    'Type B pad/top plate at intermediate bents; Type A end shoe simplified to an envelope. ', '')
            ped = f'ped_{b}_{j}'
            bottom = bm.bounds[0, 2]
            if ped in parts:
                m = native(ped)
                v = m.vertices.copy()
                top = np.isclose(v[:, 2], v[:, 2].max(), atol=1e-6)
                v[top, 2] = bottom
                store(ped, trimesh.Trimesh(v, m.faces, process=False),
                      f'Third correction: top moved to the bearing bottom, El. {bottom + 210:.3f}, under the beam raised '
                      f'{RAISE[j] * 1000:.0f} mm to the sheet 15 girder grade' +
                      (' and the Type A assembly (sheets 11, 13).' if b in (0, 5) else '.'))
            elif b in (2, 3):                       # bearing stood directly on the retained pier cap
                like = f'ped_{b}_{5 if j == 6 else 1}'
                jl = 5 if j == 6 else 1
                m = native(like)
                v = m.vertices.copy()
                v[:, 0] += sx(BS[b], YS[j]) - sx(BS[b], YS[jl])
                v[:, 1] += YS[j] - YS[jl]
                top = np.isclose(v[:, 2], v[:, 2].max(), atol=1e-6)
                v[top, 2] = bottom
                cap_top = native(f'cap_{b}').bounds[1, 2]
                expect(np.allclose(v[~top, 2], cap_top, atol=1e-5), like + ' on the pier cap')
                add(ped, trimesh.Trimesh(v, m.faces, process=False), like, like,
                    'Third correction: added because the bearing, raised with the beam to the sheet 15 girder grade, no '
                    'longer stands on the retained pier cap envelope; the retained pier seat levels are not in the bundle. '
                    'Plan numbering per sheet 11: Beam 1 is the north exterior line.',
                    f'Bent {b + 1} | pedestal under {beam_label(j)}', [5, 11, 15], 'Derived contact envelope', {},
                    before=j == 0)

    # ---- 2a: bent plans with the squared floor end, end bents with recut beam pockets ---------------------------
    def bent_regions(b):
        """(low, high) plans of an end bent: high = under the bridge floor (top at the soffit), low = under the
        approach (top at the slab bearing level). Bent 6 = Bent 1 by 180 deg rotation."""
        low, high = bent_plan(0)
        total = unary_union([low, high])
        lw = lambda y: end_line(-DECK_END_U, y)
        floor = Polygon([(lw(-9), -9), (lw(-CORE_Y), -CORE_Y), (lw(CORE_Y), CORE_Y), (lw(9), 9), (0, 9), (0, -9)])
        hi, lo = total.intersection(floor), total.difference(floor)
        if not (isinstance(hi, Polygon) and isinstance(lo, Polygon) and hi.is_valid and lo.is_valid and
                abs(hi.area + lo.area - total.area) < 1e-9):
            raise ValueError('invalid bent regions')
        return (rot(lo), rot(hi)) if b == 5 else (lo, hi)

    bottom = ('bottom', lambda x, y: BENT_BOTTOM_Z)
    seat = ('seat', lambda x, y: deck(x, y) - BENT_SEAT)
    soffit = ('soffit', lambda x, y: deck(x, y) - 0.2)
    low_plan = {}
    for b in (0, 5):
        low, high = bent_regions(b)
        low_plan[b] = low
        solid = terraced([(q, bottom, seat) for q in split_crown(low)] + [(q, bottom, soffit) for q in split_crown(high)])
        if bodies(solid) != 1:
            raise ValueError(f'cap_{b}: invalid solid')
        span = 0 if b == 0 else 4
        bent = trimesh.boolean.difference([solid] + [native(f'beam_{span}_{j}') for j in range(7)], engine='manifold')
        old = native(f'cap_{b}').volume
        if not bent.is_watertight or not solid.volume - 0.2 < bent.volume < solid.volume:
            raise ValueError(f'cap_{b}: invalid beam-end cut')
        store(f'cap_{b}', bent,
              'Third correction: beam-end pockets recut for the girders raised to the sheet 15 fillet table; the top '
              'follows the bridge-floor end squared outside the 10.620 m core (sheets 14, 18): deck soffit under the '
              'floor, slab bearing level (deck - 0.300) under the approach.', pages=[8, 9, 14, 18])
        print(f'cap_{b}: {old:.3f} -> {bent.volume:.3f} m3')

    # ---- 2b: deck and joints with the squared corners -----------------------------------------------------------
    ys = [-5.91, -CORE_Y, CORE_Y, 5.91]
    plan = Polygon([(end_line(-DECK_END_U, y), y) for y in ys] + [(end_line(DECK_END_U, y), y) for y in ys[::-1]])
    old_deck = native('deck')
    surface = ('surface', lambda x, y: deck(x, y))
    floor = terraced([(q, ('soffit', lambda x, y: deck(x, y) - 0.2), surface) for q in strips(plan)])
    if bodies(floor) != 1 or abs(floor.volume - plan.area * 0.2) > 1e-6 or abs(plan.area - 80.996 * 11.82) > 1e-6:
        raise ValueError('deck: invalid solid')
    store('deck', floor,
          'Third correction: corners squared outside the 10.620 m core (sheet 14 Half Plan: 46607 = 34389 + 12218 with '
          'the 600 mm strips square to the roadway; sheet 18): the floor ends at X = -/+46.607 and -/+34.389 for '
          '|Y| > 5.310 instead of continuing the skew to the copings. Plan area unchanged (80.996 x 11.820 m).',
          pages=[5, 6, 14, 16, 18], end_corners='squared outside |Y| = 5.310 (600 mm strips)')
    print(f'deck: {old_deck.volume:.3f} -> {floor.volume:.3f} m3')
    for s in (-1, 1):
        pid = f'joint_{s}'
        ends = [(end_line(s * DECK_END_U, y), end_line(s * APPROACH_START_U, y)) for y in ys]
        band = Polygon([(min(e), y) for e, y in zip(ends, ys)] + [(max(e), y) for e, y in zip(ends[::-1], ys[::-1])])
        joint = terraced([(q, ('base', lambda x, y: deck(x, y) - JOINT_DEPTH), surface) for q in split_crown(band)])
        if bodies(joint) != 1 or abs(joint.volume - band.area * JOINT_DEPTH) > 1e-8:
            raise ValueError(pid + ': invalid solid')
        store(pid, joint, 'Third correction: fills the modelled 25 mm separation between the bridge-floor end and the '
                          'approach slab (sheets 9 and 18 Section A-A put the Type 1A joint at that interface; the strip '
                          'no longer reaches 12 mm into the deck), squared outside the 10.620 m core (sheets 14, 18). '
                          'Opening and depth are schematic: known_deviations deck-joint-type-1a.', pages=[7, 9, 14, 18],
              width_along_x_m=round(APPROACH_START_U - DECK_END_U, 3), depth_m=JOINT_DEPTH)
        parts[pid]['note'] = parts[pid]['note'].replace('24 mm visual joint strip; ', 'Visual joint strip; ')

    # ---- 2c: approach slabs with the squared start; pavement supports -------------------------------------------
    for s in (-1, 1):
        pid = f'approach_{s}'
        x_end = s * PAVEMENT_END_X
        start = lambda y, s=s: end_line(s * APPROACH_START_U, y)
        core = Polygon([(start(-5.46), -5.46), (x_end, -5.46), (x_end, 5.46), (start(5.46), 5.46),
                        (start(CORE_Y), CORE_Y), (start(-CORE_Y), -CORE_Y)])
        slab = core
        for g in (-1, 1):                              # 450 mm curb strips, 5.030 m from the core-edge floor end
            xc = s * DECK_END_U - TAN * g * CORE_Y + s * 5.03
            y0, y1 = sorted((g * 5.46, g * 5.91))
            slab = slab.union(Polygon([(start(y0), y0), (xc, y0), (xc, y1), (start(y1), y1)]))
        if not isinstance(slab, Polygon) or not slab.is_valid:
            raise ValueError(pid + ': invalid plan')
        low = low_plan[0 if s < 0 else 5]
        on_bent, rest = slab.intersection(low), slab.difference(low)
        regions = [(q, seat, surface) for q in strips(on_bent)] + \
                  [(q, ('base', lambda x, y: deck(x, y) - SLAB_T), surface) for q in strips(rest)]
        merged = terraced(regions)
        expected = slab.area * SLAB_T + on_bent.area * (BENT_SEAT - SLAB_T)
        if bodies(merged) != 1 or abs(merged.volume - expected) > 1e-6:
            raise ValueError(pid + ': invalid slab')
        old = native(pid).volume
        store(pid, merged,
              'Third correction: start squared to the roadway outside the 10.620 m core (sheet 18: the 150 + 450 mm '
              'strips start square at the core-edge end of the bridge floor), thickened over the end-bent bearing area '
              'as before; the pavement support at the far end is the separate part pavement_support_' + str(s) + '.',
              pages=[7, 9, 18, 19], basis='Dimensioned plan outline and thickness; bottom chamfer at the bent simplified',
              start='skew across the core, square outside |Y| = 5.310')
        p = parts[pid]
        p['note'] = p['note'].replace(' Skew start kept at the modelled joint; the squared corners at |Y| > 5.310 and the '
                                      'pavement support are not modelled.', '')
        print(f'{pid}: {old:.3f} -> {merged.volume:.3f} m3 (plan {slab.area:.3f} m2, on the bent {on_bent.area:.3f} m2)')

        sid = f'pavement_support_{s}'
        sup = sweep(SUPPORT, [-SUPPORT_Y, 0.0, SUPPORT_Y],
                    lambda y, r, zr, s=s, x_end=x_end: (x_end + s * r, y, deck(x_end + s * r, y) + zr))
        area = Polygon(SUPPORT).area
        if bodies(sup) != 1 or abs(sup.volume - area * 2 * SUPPORT_Y) > 2e-4:
            raise ValueError(sid + ': invalid solid')
        add(sid, sup, pid, pid,
            'L-shaped pavement support under the far end of the approach slab (sheet 19 Section "C-C", sheet 18 Plan): '
            '750 mm wide and 300 mm deep below the 260 mm slab, 400 mm of it under the slab end, then the 50 mm expansion '
            'joint and a 300 mm upstand to the pavement surface; 10.920 m long across the slab. The joint sealing system, '
            'felt paper and the bituminous wedge beyond are not modelled. Bill: 3.3 m3 per approach.',
            ('Start' if s < 0 else 'End') + ' pavement support', [18, 19],
            'Dimensioned section and length; reinforcement, felt paper and joint seal omitted',
            dict(length_m=2 * SUPPORT_Y, width_m=0.75, depth_below_slab_m=0.3, upstand_width_m=0.3,
                 total_height_m=0.56, under_slab_m=0.4, joint_gap_m=0.05))
        print(f'{sid}: {sup.volume:.3f} m3')

    # ---- 2d: rail end panels square at the squared floor end ---------------------------------------------------
    rail_prof = [(0, 0), (.4, 0), (.4, .1), (.275, .28), (.225, .84), (0, .84)]   # as the first correction (D-D)
    stations = np.linspace(-DECK_END_U, DECK_END_U, 6)
    for side in (-1, 1):
        edge = side * 5.86
        for i in (0, 4):
            pid = f'rail_{side}_{i}'
            a, b = stations[i], stations[i + 1]
            n = max(2, int((b - a) / .6) + 1)

            def at(q, v, h, a=a, b=b, i=i, edge=edge, side=side):
                y = edge - side * v
                x0 = end_line(a, y) if i == 0 else sx(a, y)
                x1 = end_line(b, y) if i == 4 else sx(b, y)
                x = x0 + q * (x1 - x0)
                return (x, y, deck(x, y) if h == 0 else grade(x) - 0.02 * 5.46 + h)
            old = native(pid)
            rail = sweep(rail_prof, np.linspace(0, 1, n), at)
            store(pid, rail, 'Third correction: bridge end of the panel square to the roadway at the squared floor end '
                             '(sheet 16 Rail Plan, Panel "B" 80996 per side; sheets 14, 18).', pages=[6, 14, 16, 17])
            print(f'{pid}: {old.volume:.4f} -> {rail.volume:.4f} m3')

    for pid in changes:
        meshes[pid]['extras'].update(parts[pid])
    for pid in added:
        meshes[pid]['extras'].update(parts[pid])

    # ---- Remove the Bent 2 / 5 pedestals; rebuild the mesh and node lists in manifest order ---------------------
    gone = set(removed)
    manifest['parts'] = [p for p in manifest['parts'] if p['id'] not in gone]
    order = [p['id'] for p in manifest['parts']]
    if len(set(order)) != len(order) or set(order) != (set(meshes) - gone):
        raise ValueError('part list mismatch')
    gltf['meshes'] = [meshes[pid] for pid in order]
    world = gltf['nodes'][0]
    gltf['nodes'] = [world] + [dict(name=pid, mesh=k) for k, pid in enumerate(order)]
    world['children'] = list(range(1, len(gltf['nodes'])))
    changes = [c for c in changes if c not in gone]
    for item in manifest.get('detail_coverage', []):
        ids = [x for x in item['part_ids'] if x not in gone]
        if item['feature'] == 'Connections and bearings':
            ids += ['ped_2_6', 'ped_3_0']
        if item['feature'] == 'Rails and approach slabs':
            ids += ['pavement_support_-1', 'pavement_support_1']
        item['part_ids'] = ids

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
    (backup / 'sr8_yellow_before_review_correction_3.glb').write_bytes(original)
    (backup / 'sr8_yellow_manifest_before_review_correction_3.json').write_bytes(mp.read_bytes())
    path.write_bytes(out)
    manifest['review_correction_3'] = TAG
    manifest['revision'] = REVISION
    manifest['review_correction_record_3'] = dict(
        source_pdf_pages=[5, 9, 10, 11, 13, 14, 15, 16, 18, 19, 24, 26, 27, 28],
        printed_sheets='PDF pages 1-20 are printed sheets 1-20; PDF 24 is shop sheet S1 (bearings) and PDF 26-28 are '
                       'shop sheets 1-3 (new beams), all approved as noted 7/15/97',
        resolved={
            'bent-2-5-seat-steps': 'Bent 2 / 5 caps as drawn (16.750 x 0.760, seats El. 216.900 / 216.940 / 216.870, '
                                   'bottom El. 215.585; sheet 10); Type B bearings on the seats with the sheet 11 shims '
                                   '(sheet 13); girder grade from the sheet 15 fillet table (top of flange = deck - Dim "A" '
                                   '203-240 mm), raising beams, splices (sheared to the grade), haunch bottoms, '
                                   'diaphragms and the other bearings 50-87 mm; Bent 1 / 6 bearings rebuilt as Type A '
                                   '(126 mm + sheet 11 shim, 150 x 321 shims per shop sheet S1, sheet 13); new end-span '
                                   'beams extended 150 mm past the end-bent bearings with the 125 x 110 top-flange notch '
                                   '(sheet 11, PDF 26-28), haunches and end-bent pockets following; Bent 2 / 5 pedestals '
                                   'removed',
            'approach-corner-squares': 'Bridge floor, joints, approach starts and end rail panels square to the roadway '
                                       'outside the 10.620 m core (sheets 14, 16, 18); end-bent top follows; L-shaped '
                                       'pavement supports added (sheet 19 C-C, sheet 18)'},
        decisions={
            'girder grade': 'Sheet 15 Dim "A" sets the girders: it is the only reading that clears the 200 mm deck at '
                            'the exterior flange tips (3 mm fillet). The sheet 10 seat + sheet 13 stack + sheet 11 shim '
                            '+ splice plate close on it within -0.8 / +0.7 mm, so the modelled Bent 2 / 5 shims take that '
                            'rounding (known_deviations bent-2-5-shim-rounding). Splice plates follow the beam grade.',
            'end bearings': 'Bents 1 / 6: Type A assembly of sheet 13 with the sheet 11 shims exactly; the Pour 1 seat '
                            'takes the closure (737-811 mm above El. 216.100; sheet 9 gives 737 min, 810 max). The '
                            'approved shop sheet S1 (PDF 24) revises the shim width to 321 mm (edge distances 14 / 15, '
                            'modelled centred) and governs the fabricated plate over contract sheet 13 (350).',
            'end-span beam ends': 'Sheet 11 and shop sheets 1-3 give 150 mm past the end-bent bearing with a square end; '
                                  'the 125 x 110 top-flange notch (Views "A" / "B", typical) is placed on the corner '
                                  'nearest the skewed floor end (south at Bent 1, north at Bent 6), which is also where '
                                  'View "A" draws it with the end on the left.',
            'deck joints': 'The joint strip fills the modelled slab separation at the interface shown on sheets 9 / 18 '
                           'A-A; its opening and depth stay schematic (known_deviations deck-joint-type-1a).',
            'retained piers': 'Pier 3 / 4 caps (approximate, sheet 5) are unchanged because no seat level is given; the '
                              'derived pedestals are extended and two are added so every bearing keeps contact.',
            'end-bent corners': 'Where the squared floor end moves, the bent top follows the existing rule of sheet 9 '
                                'A-A: deck soffit under the floor, slab bearing level under the approach.'},
        raise_m_by_beam_line_south_to_north=RAISE,
        changed_parts=changes, removed_parts=sorted(gone), added_parts=added,
        before_glb_sha256=before, after_glb_sha256=hashlib.sha256(out).hexdigest())
    shims = {pid: parts[pid]['dimensions']['shim_thickness_m'] - parts[pid]['dimensions']['shim_table_mm'] / 1000
             for pid in parts if pid.startswith(('Bent_2_bearing', 'Bent_5_bearing'))}
    lo, hi = min(shims.values()) * 1000, max(shims.values()) * 1000
    manifest['known_deviations'] = [d for d in manifest.get('known_deviations', [])
                                    if d.get('id') not in ('bent-2-5-seat-steps', 'approach-corner-squares')] + [
        dict(id='bent-2-5-shim-rounding', parts='Bent_2_bearing_*, Bent_5_bearing_*',
             source='sheet 10 (seats), sheet 11 (shim table), sheet 13 (Type B stack, splice plate), sheet 15 (fillet table)',
             deviation=f'The modelled shims differ from the sheet 11 table by {lo:+.1f} to {hi:+.1f} mm at the bearing '
                       f'centre line. Seat + 135 mm stack + shim + 12 mm splice plate and deck - Dim "A" - 840 mm give '
                       f'the beam soffit two values that differ by that much; the girders follow Dim "A", the only '
                       f'reading that clears the deck at the exterior flange tips, and the shims close the gap.',
             reason='All four inputs are rounded to 1 mm. The as-set bearing or top-of-beam elevations would settle it; '
                    'sheet 13 (screed note: "Elevations will be furnished upon request") and sheet 14 ("Screed Data will '
                    'be furnished upon request") refer to data that are not in the bundle.'),
        dict(id='pier-3-4-seats', parts='cap_2, cap_3, ped_2_*, ped_3_*, Pier_3_bearing_*, Pier_4_bearing_*',
             source='sheet 5 (general elevation), sheet 11 (top shoes at Piers 3 and 4), sheet 15 (girder grade)',
             deviation='The retained pier caps keep their derived top (El. 216.848) and the retained shoes keep a 160 mm '
                       'envelope; the pedestals between them (87-161 mm, two of them added) are derived so that the '
                       'shoes reach the sheet 15 girder grade.',
             reason='The 1997 bundle and the 2026 reference do not dimension the retained pier seats or shoes. The '
                    'original pier drawings or a survey of the seats would settle it.'),
        dict(id='deck-joint-type-1a', parts='joint_-1, joint_1, deck, approach_-1, approach_1',
             source='sheet 9 (note: "For Type 1A Joint, See Bridge Std. 724-BJTS-01"; Section A-A), sheet 18 Section A-A',
             deviation='The joint is a schematic strip 25 mm along X and 80 mm deep filling the modelled separation '
                       'between the bridge-floor end and the approach slab; the sections show the slabs abutting with '
                       'the Type 1A joint at the surface, without dimensions.',
             reason='Bridge Std. 724-BJTS-01 (Type 1A joint) is not in the bundle.')]
    mp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in manifest['review_correction_record_3'].items()
                      if k not in ('changed_parts', 'resolved', 'decisions')}))
    print(len(changes), 'parts changed,', len(added), 'added,', len(gone), 'removed')


if __name__ == '__main__':
    correct()

"""Third correction of US 52 over Mud Creek (us52-mud): the known deviations left by the first two reviews.

    python scripts/correct_us52_mud_review.py      # first correction (revision 1.1)
    python scripts/correct_us52_mud_review_2.py    # second correction (revision 1.2)
    python scripts/correct_us52_mud_review_3.py    # this one (revision 1.3-deviations)

Source: drawings.pdf (2020-03-27 Stage 3 draft); the printed sheet numbers equal the PDF page numbers. Native axes:
X along the bridge (0 at sta. 458+17.00, +X = increasing station = east), Y across it (+Y = north), Z up
(0 = El. 910.80 ft), metres. Handedness is unchanged.

1. End-bent datum (decision; known deviation end-bent-absolute-elevation). The roadway profile is the same on
   sheets 9 (PVI 458+17.00 El. 932.00, 135 ft vertical curve), 21 (El. 931.76 at both bents, 931.82 at both piers)
   and 62-64 (P.G. elevations), and the pier sheet 28 is consistent with it: crown El. 929.95 + 1 in UHPC bed
   (written, sheet 28) + 1 ft 8 in slab + 1 1/2 in overlay = El. 931.825. The precast end-bent module has written
   depths on sheet 24 (elevation: 8 in ledge over 3 ft 0 in at its outer end and 3 ft 4 3/4 in at its inner end;
   sections: "varies 3 ft 0 in min."), which the sheet 23 elevations repeat as differences (929.21 - 926.21 = 3.00 ft).
   Only the five absolute sheet 23 elevations (929.21 / 929.61 seat, 929.88 / 930.28 ledge, 926.21 bottom) disagree:
   all lie a uniform 0.27 ft below the profile less the same 22 1/2 in build-up (a 4 1/4 in bed would be needed
   instead of the 1 in drawn on sheets 23, 24, 28 and 53). The model kept the seat on the profile and the bottom at
   El. 926.21, which made each module 3.3 in deeper than its written depth. Decision: the profile and the written
   depths govern. The seat stays; the bottoms of the six cap parts rise 0.0836 m to El. 926.48 (seat at the deck
   edge less 3 ft 0 in), giving 3 ft 0 in / 3 ft 4 3/4 in as written.
2. Wingwalls (decision, same datum; known deviation wingwall-top-elevation). Sheet 24 section A-A draws the
   3 ft 8 in wingwall (sheets 24, 27) flush with the cap bottom and with the ledge top; the precast wing module is a
   flat-topped 9 ft x 3 ft x 3 ft 8 in block (sheet 27). The four wings and their 1 ft UHPC closure pours move up
   with the cap bottom, to El. 926.48..930.15, so their tops equal the ledge top at the deck edge.
3. Wingwall beds (added; sheet 53 section A-A "1 in UHPC bed (typ.)" between each wing and the approach slab, also
   drawn on sheet 24 section A-A over the wing and its closure pour). Four new parts wing_bed_{1,2}_{-1,1} fill from
   the flat wing top to the approach slab soffit over the wing and its closure pour (|X| 14.1732..17.2212,
   |Y| 5.2324..6.1468). They are 1 in nominal; because the precast wing top is flat while the slab follows the 2%
   crossfall and the vertical curve, the fill is 0.48..1.66 in thick.
4. Railing neoprene joints (added; known deviation railing-neoprene-joint). Sheet 51 plan and elevation show a
   1/2 in neoprene expansion joint, full railing height, between the 91 ft 6 in bridge railing and each TFC
   transition. Four new parts rail_joint_{1,2}_{-1,1} fill |X| 13.9446..13.9573 with the sheet 51 FC section,
   standing on the approach slab top, flush with both railing ends.
5. Barrier delineators (sheet 51 sections A-A and B-B, 1 in = 1 ft; sheet 22 typical section; known deviation
   railing-delineator-position). Both sections draw the delineator on the upper front (traffic) face: a block 3 in
   long on the batter, 2 in proud of it, its top 5.4 in below the railing top (scaled; the drawings give no
   dimension). The six markers sat across the railing top, mostly inside it. They are rebuilt in that position at
   their X stations (40 ft spacing, sheets 22, 51); the 0.2 ft length along the railing is the previous
   visualisation value, as no view shows it.
6. TFC transition length (decision; known deviation tfc-transition-length-sheet-9). Sheets 53 and 55 draw the
   transition 15 ft 8 in long (scaled), and sheet 51 note 4 and sheet 52 send the TFC details to INDOT standard
   E 706-TTFC-01..03, whose sheet 01 writes "15'-8" - Pay Limits of Concrete Bridge Railing Transition, TFC". The
   sheet 9 roadway station callouts (13.17 ft) conflict with both. The model keeps 15 ft 8 in.
7. TFC transition shape (final check; decision). The transitions kept the constant FC section. Standard E 706-TTFC-02
   writes the sections (2 ft 9 in high, 9 in top, rear face 2 in inside the deck edge): A-A at the joint = FC section
   (16 in base); B-B at 7 ft 2 in, 11 5/8 in base, single 2 5/8 in batter over 2 ft 6 in on a 3 in toe; C-C at
   8 ft 1 in, 11 in base, 2 in batter; D-D at 11 ft 5 in, a 9 in vertical wall to the 15 ft 8 in end. E 706-TTFC-01
   (plan and elevation) runs the FC batter break from 11 in / 10 in up at A-A to the toe top (11 5/8 in / 3 in) at
   B-B. The project sheets 54 and 55 (3/4 in = 1 ft) draw the same toe line in plan: 16 in at the joint, 11.64 in at
   7 ft 2 in, 9 in at 11 ft 5 in. Sheet 53 section A-A draws the FC outline ("typ.") at a cut about 13 ft from the
   joint; the referenced standard and sheets 54/55 govern. The four approach_rail parts are rebuilt to those
   sections (3/4 in chamfers omitted). The approach LMC overlay ends at the railing toe (sheet 53 section A-A), so
   its edge now follows the tapering toe up to the transition end (approach_overlay_1, approach_overlay_2).
8. End-bent closure tops and beds (final check). Sheet 23 draws the bent top as one 2% crossfall each side of the
   crown at the central closure, but the closures were flat (3.05 mm proud at their edges), and the 1 in beds kept
   the slope of the deck soffit along X while the precast tops are level along X (gaps to 1.5 mm, interference to
   4.6 mm). The closures are rebuilt with the crown at Y = 0 and the bed bottoms are fitted to the cap tops; the bed
   tops (deck and approach soffits) are unchanged, so the beds are 0.94..1.06 in thick.
9. Pier closure tops and beds (final check, same defect). Sheet 28 draws the pier top as one 2% crossfall from
   El. 929.95 at the crown; the 8 in UHPC closures were flat (up to 2.0 mm proud) and the beds kept the soffit slope
   along X. The closure tops now follow the crossfall (closure 4 with its crown ridge) and the bed bottoms sit on the
   pier tops. The beds were rectangles over the whole 3 ft x 40 ft 4 in; the 1 in bed lies on the wall top (sheet 28
   typical section, sheet 29 module section) and the outer modules end in R = 1 ft 6 in semicircles (sheet 29 plan),
   so each bed is trimmed to the pier top footprint (about 0.18 m2 of unsupported corners removed per bed).

Requires numpy, trimesh and manifold3d, and the two earlier scripts (same folder).
"""
import hashlib
import json
import struct
import sys
from pathlib import Path

import numpy as np
import trimesh
from manifold3d import CrossSection
from shapely.geometry import Polygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

sys.path.insert(0, str(Path(__file__).resolve().parent))
from correct_us52_mud_review import (BACK_X, BASE, BENT_X, DECK_EDGE, FT, IN, JOINT_X, LEDGE, ROOT,  # noqa: E402
                                     STEP_X, TAG as FIRST_TAG, loft, rail_mesh, slab_top)
from correct_us52_mud_review_2 import REVISION as REVISION_BEFORE, TAG as SECOND_TAG  # noqa: E402

TAG = 'endbent-datum-wing-beds-neoprene-joints-delineators-tfc-decision'
REVISION = '1.3-deviations'
SHA_BEFORE = '8017ea02b0c13d6c5a1f527003204a2432bfbc34dd8fd7246e854c70797d2ecc'
EXPECTED_DEVIATIONS = {'end-bent-absolute-elevation', 'wingwall-top-elevation', 'railing-neoprene-joint',
                       'tfc-transition-length-sheet-9', 'railing-delineator-position'}

DATUM = 910.80                                       # local Z 0 = El. 910.80 ft
OLD_BOTTOM = (926.21 - DATUM) * FT                   # sheet 23 bent bottom, kept by revisions 1.0-1.2
DEPTH_OUTER = 3 * FT                                 # sheet 24: 3 ft 0 in at the module's outer end
DEPTH_INNER = (3 * 12 + 4.75) * IN                   # sheet 24: 3 ft 4 3/4 in at its inner end
WING_H = (3 + 8 / 12) * FT                           # sheets 24, 27: 3 ft 8 in wingwall
WING_JOINT_X = BACK_X + 1 * FT                       # 1 ft wingwall closure pour, sheets 23, 24: 14.478 m
WING_END_X = WING_JOINT_X + 9 * FT                   # 9 ft wingwall module, sheet 27: 17.2212 m
WING_IN_Y = DECK_EDGE - 3 * FT                       # 3 ft wide, flush with the deck edge: 5.2324 m
SLAB_BUILDUP = 20 * IN + 1 * IN                      # 1 ft 8 in slab + 1 in bed under the seat (sheets 23, 24, 28)
NEOPRENE = 0.5 * IN                                  # sheet 51
# Delineator, sheet 51 sections A-A / B-B at 1 in = 1 ft (6 pt per inch), scaled from the vector drawing.
DEL_TOP_DROP = 5.4 * IN                              # top of the block below the railing top (vertical)
DEL_FACE = 3 * IN                                    # length on the upper batter
DEL_PROUD = 2 * IN                                   # projection normal to the batter
DEL_LENGTH = 0.2 * FT                                # along the railing: previous visualisation value
FRONT_TOP_Y = DECK_EDGE - 11 * IN                    # FC section front top, 5.8674 m
BREAK_Y = DECK_EDGE - 13 * IN                        # FC section batter break, 5.8166 m

JOINT_COLOR = '#3b4044'                              # neoprene
BED_COLOR = '#465e66'                                # as the existing UHPC bedding layers
TTFC_URL = ('https://www.in.gov/dot/div/contracts/standards/drawings/sep20/e/700e/e700%20combined%20pdfs/'
            'E706-TTFC.pdf')
TTFC_SHA256 = '3a46124fe3803d3b019c2865897c49303252fbcc25567b087229b5af335c6e0a'

OLD_TFC_NOTE = 'Standard transition curvature and section variation are unavailable.'
OLD_TFC_NOTE_KO = '표준도의 전이 곡률·단면 변화는 미확보입니다.'
TFC_NOTE = ('TFC railing transition, precast with the edge panel and standing on it (sheet 53 section A-A), starting '
            'at the 1/2 in neoprene joint and 15 ft 8 in long, ending 9 in short of the 4 ft 1 in corner cutback. '
            'Sections of standard E 706-TTFC-01/-02, which sheet 51 note 4 makes governing and sheets 54 and 55 draw '
            'in plan: 2 ft 9 in high, rear face 2 in inside the deck edge, 9 in top; the FC section at the joint '
            '(A-A); the lower batter fades out by 7 ft 2 in (B-B: 11 5/8 in base, 2 5/8 in batter on a 3 in toe); '
            '11 in base at 8 ft 1 in (C-C); a 9 in vertical wall from 11 ft 5 in (D-D) to the end. 3/4 in chamfers '
            'omitted. Length decision (third review): 15 ft 8 in as drawn on sheets 53 and 55 and written as the pay '
            'limits on E 706-TTFC-01; the 13.17 ft of the sheet 9 station callouts is not followed. Shape decision: '
            'the standard and sheets 54/55 govern over the typical FC outline of sheet 53 section A-A.')
TFC_NOTE_KO = ('TFC 전이 난간으로 가장자리 패널과 일체로 프리캐스트되어 그 위에 놓입니다(도면 53 단면 A-A). ½ in 네오프렌 '
               '줄눈에서 시작해 길이 15 ft 8 in이며 4 ft 1 in 모서리 절취부보다 9 in 앞에서 끝납니다. 단면은 도면 51 주기 '
               '4가 지정하고 도면 54·55 평면에 작도된 표준도 E 706-TTFC-01/-02를 따릅니다: 높이 2 ft 9 in, 후면은 데크 '
               '가장자리에서 2 in 안쪽, 상단 폭 9 in; 줄눈에서 FC 단면(A-A); 하부 경사면은 7 ft 2 in에서 사라짐(B-B: 하단 '
               '폭 11 5/8 in, 3 in 하단 수직부 위 2 5/8 in 경사); 8 ft 1 in에서 하단 폭 11 in(C-C); 11 ft 5 in(D-D)부터 '
               '끝까지 폭 9 in 수직벽. 3/4 in 모따기는 생략했습니다. 길이 결정(3차 검토): 도면 53·55의 작도와 '
               'E 706-TTFC-01의 지급 한계 15 ft 8 in를 따르며 도면 9 측점 표기의 13.17 ft는 따르지 않습니다. 형상 결정: '
               '도면 53 단면 A-A의 대표 FC 외형보다 표준도와 도면 54·55를 따릅니다.')
# E 706-TTFC-01/-02: stations of sections A-A, B-B, C-C, D-D and the end (inches from the joint) and the base width
# (rear face to toe, inches) at each; the batter break runs from (11 in, 10 in up) at A-A to the toe top at B-B.
TFC_T = (0.0, 86.0, 97.0, 137.0, 188.0)
TFC_BASE = (16.0, 11.625, 11.0, 9.0, 9.0)
TFC_B_X = JOINT_X + 86 * IN                          # 16.1417 m
TFC_END_X = JOINT_X + 188 * IN                       # 18.7325 m
OVERLAY = 1.5 * IN                                   # LMC-VE overlay, sheets 23, 24, 53
PIER_X = 18 * FT                                     # pier centre lines at +/-5.4864 m (sta. 457+99 / 458+35)


def el(z):
    return DATUM + z / FT


def zhits(mesh, x, y):
    """Z of every facet of `mesh` crossed by the vertical line through (x, y) (no rtree needed)."""
    t = mesh.triangles
    a, b, c = t[:, 0], t[:, 1], t[:, 2]
    v0, v1, v2 = b[:, :2] - a[:, :2], c[:, :2] - a[:, :2], np.array([x, y]) - a[:, :2]
    den = v0[:, 0] * v1[:, 1] - v1[:, 0] * v0[:, 1]
    ok = np.abs(den) > 1e-12
    den = np.where(ok, den, 1.0)
    u = (v2[:, 0] * v1[:, 1] - v1[:, 0] * v2[:, 1]) / den
    w = (v0[:, 0] * v2[:, 1] - v2[:, 0] * v0[:, 1]) / den
    inside = ok & (u >= -1e-9) & (w >= -1e-9) & (u + w <= 1 + 1e-9)
    z = (a[:, 2] + u * (b[:, 2] - a[:, 2]) + w * (c[:, 2] - a[:, 2]))[inside]
    return np.unique(np.round(z, 7))                 # facets sharing an edge give one value


def same_points(a, b, tol=2e-6):
    """True when the two point sets coincide (every point of each has a partner in the other)."""
    d = np.linalg.norm(a[:, None, :] - b[None, :, :], axis=2)
    return len(a) == len(b) and d.min(axis=1).max() < tol and d.min(axis=0).max() < tol


def rgba(hex_color):
    return [int(hex_color[i:i + 2], 16) for i in (1, 3, 5)] + [255]


def raw_loft(sections):
    """Side quads between equal-length loops and fan caps from vertex 0, without validity checks."""
    k = len(sections[0])
    v = np.vstack([np.asarray(s, dtype=np.float64) for s in sections])
    faces = []
    for s in range(len(sections) - 1):
        a, b = s * k, (s + 1) * k
        for i in range(k):
            j = (i + 1) % k
            faces += [(a + i, a + j, b + j), (a + i, b + j, b + i)]
    last = (len(sections) - 1) * k
    for i in range(1, k - 1):
        faces += [(0, i + 1, i), (last, last + i, last + i + 1)]
    return trimesh.Trimesh(vertices=v, faces=np.array(faces), process=False)


def solid(mesh, what):
    if mesh.volume < 0:
        mesh.invert()
    if not (mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0):
        raise ValueError(f'{what}: not a valid solid')
    return mesh


def tfc_loop(t, six):
    """E 706-TTFC section at t inches from the joint, as (inches inboard of the deck edge, inches above the slab)."""
    toe = 2 + float(np.interp(t, TFC_T, TFC_BASE))
    loop = [(toe, 3), (toe, 0), (2, 0), (2, 33), (11, 33)]
    if six:                                          # the FC batter break, A-A to B-B
        f = min(t, 86.0) / 86.0
        loop = [(13 + 0.625 * f, 10 - 7 * f)] + loop
    return loop


def tfc_mesh(stations, s, side):
    """TFC transition through the given |X| stations (both B-B and the end included)."""
    def section(x, six):
        return [(s * x, side * (DECK_EDGE - i * IN), slab_top(x, DECK_EDGE - i * IN) + u * IN)
                for i, u in tfc_loop((x - JOINT_X) / IN, six)]
    first = [x for x in stations if x <= TFC_B_X + 1e-9]
    second = [x for x in stations if x >= TFC_B_X - 1e-9]
    a = raw_loft([section(x, True) for x in first])     # the break meets the toe top at B-B: merge, drop slivers
    a.merge_vertices(digits_vertex=9)
    a.update_faces(a.nondegenerate_faces(height=1e-10))
    a.remove_unreferenced_vertices()
    a = solid(a, 'TFC A-A..B-B')
    b = solid(raw_loft([section(x, False) for x in second]), 'TFC B-B..end')
    return solid(trimesh.boolean.union([a, b], engine='manifold'), 'TFC transition')


def overlay_mesh(main, tail, s, half):
    """Overlay band on the slab top: 1 1/2 in thick, crowned at Y = 0, half-width `half(x)` over the `main` stations
    and 5.6896 m over the `tail` stations beyond the transition end."""
    def section(x, h):
        pts = []
        for y, up in ((0, 0), (h, 0), (h, OVERLAY), (0, OVERLAY), (-h, OVERLAY), (-h, 0)):
            pts.append((s * x, y, slab_top(x, y) + up))
        return pts
    a = loft([section(x, half(x)) for x in main])
    b = loft([section(x, DECK_EDGE - 18 * IN) for x in tail])
    return solid(trimesh.boolean.union([a, b], engine='manifold'), 'approach overlay')


def correct():
    mp = BASE / 'model_manifest.json'
    manifest = json.loads(mp.read_text(encoding='utf-8'))
    if manifest.get('review_correction_3') == TAG:
        print('Already corrected.')
        return
    if (manifest.get('review_correction') != FIRST_TAG or manifest.get('review_correction_2') != SECOND_TAG
            or manifest.get('revision') != REVISION_BEFORE):
        raise ValueError('run scripts/correct_us52_mud_review.py and _review_2.py first (revision 1.2 expected)')
    if {d['id'] for d in manifest.get('known_deviations', [])} != EXPECTED_DEVIATIONS:
        raise ValueError('unexpected known_deviations')
    path = BASE / 'model.glb'
    original = path.read_bytes()
    before = hashlib.sha256(original).hexdigest()
    if before != SHA_BEFORE:
        raise ValueError(f'unexpected model.glb (SHA-256 {before})')
    length = struct.unpack_from('<I', original, 12)[0]
    gltf = json.loads(original[20:20 + length])
    binary = bytearray(original[28 + length:])
    parts = {p['id']: p for p in manifest['parts']}
    meshes = {m['name']: m for m in gltf['meshes']}
    changed, added, notes_only = [], [], []

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

    def current_mesh(pid):
        prim = meshes[pid]['primitives'][0]
        return trimesh.Trimesh(vertices=read(prim['attributes']['POSITION']).astype(np.float64),
                               faces=read(prim['indices']).reshape(-1, 3), process=False)

    def valid(pid, mesh):
        if not mesh.is_watertight or not mesh.is_winding_consistent or mesh.volume <= 0:
            raise ValueError(f'{pid}: mesh is not a valid closed solid')

    def store(pid, mesh, dims, note, note_ko, pages, basis=None, basis_ko=None, extras=None, retopo=False):
        """New positions; indices and colours are kept for an unchanged topology, else appended (retopo=True)."""
        prim = meshes[pid]['primitives'][0]
        valid(pid, mesh)
        same = (len(mesh.vertices) == gltf['accessors'][prim['attributes']['POSITION']]['count']
                and np.array_equal(mesh.faces, read(prim['indices']).reshape(-1, 3)))
        if not same and not retopo:
            raise ValueError(f'{pid}: topology changed unexpectedly')
        attributes = {'POSITION': append(mesh.vertices.astype('<f4'), 'VEC3', 5126)}
        if same:
            attributes['COLOR_0'] = prim['attributes']['COLOR_0']
        else:
            color = read(prim['attributes']['COLOR_0'])[0]
            attributes['COLOR_0'] = append(np.tile(color, (len(mesh.vertices), 1)).astype('u1'), 'VEC4', 5121)
            gltf['accessors'][attributes['COLOR_0']]['normalized'] = True
            prim['indices'] = append(mesh.faces.reshape(-1, 1).astype('<u4'), 'SCALAR', 5125)
        prim['attributes'] = attributes
        p, ex = parts[pid], meshes[pid]['extras']
        p['bounds_m'] = mesh.bounds.round(6).tolist()
        p['volume_m3'] = round(float(mesh.volume), 6)
        p['dimensions'].update(dims)
        p['pdf_pages'] = sorted(set(p.get('pdf_pages', [])) | set(pages))
        p['note'] = note
        if basis:
            p['basis'], ex['basis'] = basis, basis_ko
        ex.update(bounds_m=p['bounds_m'], volume_m3=p['volume_m3'], dimensions=p['dimensions'],
                  pdf_pages=p['pdf_pages'], note=note_ko)
        if extras:
            ex.update(extras)
        changed.append(pid)

    def add(pid, mesh, name, name_ko, layer, color, pages, basis, basis_ko, note, note_ko, dims):
        """A new part: mesh with POSITION / COLOR_0 / indices, a node like the others, a manifest entry."""
        if pid in parts or pid in meshes:
            raise ValueError(f'{pid}: part already exists')
        valid(pid, mesh)
        v = mesh.vertices.astype('<f4')
        attributes = {'POSITION': append(v, 'VEC3', 5126),
                      'COLOR_0': append(np.tile(np.array(rgba(color), dtype='u1'), (len(v), 1)), 'VEC4', 5121)}
        gltf['accessors'][attributes['COLOR_0']]['normalized'] = True
        indices = append(mesh.faces.reshape(-1, 1).astype('<u4'), 'SCALAR', 5125)
        bounds = mesh.bounds.round(6).tolist()
        volume = round(float(mesh.volume), 6)
        pages = sorted(pages)
        gltf['meshes'].append(dict(name=pid, primitives=[dict(attributes=attributes, indices=indices, mode=4)],
                                   extras=dict(processed=True, id=pid, name=name_ko, layer=layer, color=color,
                                               pdf_pages=pages, basis=basis_ko, note=note_ko, dimensions=dims,
                                               bounds_m=bounds, volume_m3=volume)))
        meshes[pid] = gltf['meshes'][-1]
        gltf['nodes'].append(dict(name=pid, mesh=len(gltf['meshes']) - 1, matrix=list(gltf['nodes'][1]['matrix'])))
        gltf['nodes'][0]['children'].append(len(gltf['nodes']) - 1)
        entry = dict(id=pid, name=name, layer=layer, color=color, pdf_pages=pages, basis=basis, note=note,
                     dimensions=dims, bounds_m=bounds, volume_m3=volume)
        manifest['parts'].append(entry)
        parts[pid] = entry
        added.append(pid)

    world = gltf['nodes'][0]
    if world.get('name') != 'world' or len(world['children']) != len(gltf['nodes']) - 1 or len(gltf['meshes']) != 164:
        raise ValueError('unexpected scene layout')
    matrix = gltf['nodes'][1]['matrix']
    if any(n.get('matrix') != matrix for n in gltf['nodes'][1:]):
        raise ValueError('unexpected node transforms')

    # --- 1. End-bent caps: precast depth as written on sheet 24, seat on the profile ------------------------
    new_bottom = {}
    for b, s in ((1, -1), (2, 1)):
        seat_profile = slab_top(BENT_X, DECK_EDGE) - SLAB_BUILDUP
        for pid in (f'bent_{b}_0', f'bent_{b}_1', f'bent_{b}_closure'):
            mesh = current_mesh(pid)
            v = mesh.vertices.copy()
            low = np.isclose(v[:, 2], OLD_BOTTOM, atol=2e-6)
            if len(v) != 12 or low.sum() != 4 or not np.allclose(sorted(set(np.round(v[low, 0], 4))),
                                                                  sorted((round(s * BACK_X, 4),
                                                                          round(s * (BENT_X - 1.5 * FT), 4)))):
                raise ValueError(f'{pid}: unexpected cap bottom (already raised?)')
            if pid != f'bent_{b}_closure':
                at_edge = np.isclose(np.abs(v[:, 1]), DECK_EDGE, atol=1e-5) & ~low
                seat = v[at_edge, 2].min()
                if not np.isclose(seat, seat_profile, atol=2e-5):
                    raise ValueError(f'{pid}: seat {seat:.6f} is not on the profile ({seat_profile:.6f})')
                bottom = seat - DEPTH_OUTER
                if b in new_bottom and not np.isclose(new_bottom[b], bottom, atol=1e-6):
                    raise ValueError(f'{pid}: modules disagree on the bottom')
                new_bottom[b] = bottom
                inner = np.isclose(np.abs(v[:, 1]), 0.5 * FT, atol=1e-5) & ~low
                depth_inner = v[inner, 2].min() - bottom
                if abs(depth_inner - DEPTH_INNER) > 1 / 16 * IN:
                    raise ValueError(f'{pid}: inner-end depth {depth_inner / IN:.3f} in, not 3 ft 4 3/4 in')
            closure = pid.endswith('closure')
            crown = slab_top(BENT_X, 0) - SLAB_BUILDUP
            if closure:
                # flat top at the crown value on both faces (sheet 23 draws the 2% crossfall through the crown)
                tops = np.round(v[~low, 2], 5)
                if not np.allclose(sorted(set(tops)), sorted({round(crown, 5), round(crown + LEDGE, 5)}), atol=2e-5):
                    raise ValueError(f'{pid}: unexpected closure top')
                back, step, front = s * BACK_X, s * STEP_X, s * (BENT_X - 1.5 * FT)
                sections = []
                for y in (-0.5 * FT, 0.0, 0.5 * FT):
                    zt = crown - 0.02 * abs(y)
                    sections.append([(step, y, zt), (step, y, zt + LEDGE), (back, y, zt + LEDGE),
                                     (back, y, new_bottom[b]), (front, y, new_bottom[b]), (front, y, zt)])
                new = loft(sections)
            else:
                v[low, 2] = new_bottom[b]
                new = trimesh.Trimesh(vertices=v, faces=mesh.faces, process=False)
            p = parts[pid]
            store(pid, new, dict(bottom_el_ft=round(el(new_bottom[b]), 2)) if closure else
                  dict(depth_outer_end_ft=3, depth_inner_end_in=40.75, bottom_el_ft=round(el(new_bottom[b]), 2)),
                  p['note'] + ' Bottom raised 3.29 in to El. 926.48 (decision, third review): the precast depth is the '
                  'written 3 ft 0 in at the outer end and 3 ft 4 3/4 in at the inner end of each module (sheet 24) with '
                  'the seat on the roadway profile less the 1 1/2 in overlay, 1 ft 8 in slab and 1 in bed (sheets 9, '
                  '21, 28); the sheet 23 elevations lie a uniform 0.27 ft lower and are not followed.' +
                  (' Top crowned at the centre line, continuing the 2% crossfall of both modules (sheet 23 elevation).'
                   if closure else ''),
                  meshes[pid]['extras'].get('note', '') + ' 하단을 3.29 in 올려 El. 926.48로 했습니다(3차 검토 결정): '
                  '교좌면은 종단 계획고에서 포장 1 1/2 in·슬래브 1 ft 8 in·받침층 1 in를 뺀 높이로 두고, 프리캐스트 '
                  '모듈 높이를 도면 24에 기입된 바깥 끝 3 ft 0 in, 안쪽 끝 3 ft 4 3/4 in로 맞췄습니다(도면 9·21·28). '
                  '도면 23의 표고는 일률적으로 0.27 ft 낮아 따르지 않습니다.' +
                  (' 상면은 중심선에서 정점을 이루며 양쪽 모듈의 2% 횡단경사를 잇습니다(도면 23 입면).' if closure else ''),
                  [9, 21, 24, 28], retopo=closure)
            print(f'{pid}: bottom El. {el(OLD_BOTTOM):.3f} -> {el(new_bottom[b]):.3f} '
                  f'({(new_bottom[b] - OLD_BOTTOM) / IN:+.2f} in), {mesh.volume:.4f} -> {new.volume:.4f} m3')

    # --- 1b. End-bent and pier UHPC beds sit on the precast tops (level along X, 2% crossfall) ----------------
    def fit_bed(pid, crown, ledge_x=None):
        """Bed bottom vertices onto the support top crown - 2%|Y| (+ the ledge beyond |X| ledge_x); tops kept."""
        mesh = current_mesh(pid)
        v = mesh.vertices.copy()
        shells = len(v) // 12
        if len(v) % 12 or any(set(np.unique(f // 12)) != {f[0] // 12} for f in mesh.faces):
            raise ValueError(f'{pid}: unexpected bed layout')
        moved = []
        for sh in range(shells):
            idx = np.arange(sh * 12, sh * 12 + 12)
            for i in idx:
                pair = idx[np.isclose(v[idx, 0], v[i, 0], atol=1e-6) & np.isclose(v[idx, 1], v[i, 1], atol=1e-6)]
                if len(pair) != 2:
                    raise ValueError(f'{pid}: unexpected bed vertex pairing')
                if v[i, 2] < v[pair, 2].max():
                    ledge = ledge_x is not None and np.abs(v[idx, 0]).max() > ledge_x + 1e-4
                    target = crown - 0.02 * abs(v[i, 1]) + (LEDGE if ledge else 0)
                    if abs(target - v[i, 2]) > 2.5e-3:
                        raise ValueError(f'{pid}: bed bottom far from the support top ({target - v[i, 2]:+.4f} m)')
                    moved.append(target - v[i, 2])
                    v[i, 2] = target
        new = trimesh.Trimesh(vertices=v, faces=mesh.faces, process=False)
        thickness = []
        for sh in range(shells):
            idx = np.arange(sh * 12, sh * 12 + 12)
            for i in idx:
                pair = idx[np.isclose(v[idx, 0], v[i, 0], atol=1e-6) & np.isclose(v[idx, 1], v[i, 1], atol=1e-6)]
                thickness.append(np.ptp(v[pair, 2]))
        return mesh, new, min(moved), max(moved), min(thickness), max(thickness)

    for b, s in ((1, -1), (2, 1)):
        pid = f'bent_{b}_bed'
        old, new, m0, m1, t0, t1 = fit_bed(pid, slab_top(BENT_X, 0) - SLAB_BUILDUP, ledge_x=STEP_X)
        p = parts[pid]
        store(pid, new, dict(thickness_min_in=round(t0 / IN, 2), thickness_max_in=round(t1 / IN, 2)),
              p['note'] + f' Bottom fitted to the cap top, level along X with the 2% crossfall through the crown '
              f'(sheets 23, 24); top unchanged on the deck and approach slab soffits, so the bed is {t0 / IN:.2f} to '
              f'{t1 / IN:.2f} in thick (third review).',
              meshes[pid]['extras'].get('note', '') + f' 하면을 교대 상면(X 방향 수평, 정점 기준 2% 횡단경사)에 맞췄고 '
              f'상면은 데크·접속 슬래브 하면 그대로 두어 두께 {t0 / IN:.2f}~{t1 / IN:.2f} in입니다(도면 23·24, 3차 검토).',
              [23, 24])
        print(f'{pid}: bottom moved {m0 * 1000:+.2f}..{m1 * 1000:+.2f} mm, now {t0 / IN:.3f}..{t1 / IN:.3f} in thick')

    for pier, s in ((2, -1), (3, 1)):
        crown = slab_top(PIER_X, 0) - SLAB_BUILDUP
        top4 = current_mesh(f'pier_{pier}_module_4').vertices
        if not np.isclose(top4[:, 2].max(), crown - 0.02 * np.abs(top4[np.argmax(top4[:, 2]), 1]), atol=2e-5):
            raise ValueError(f'pier_{pier}: module tops are not on the 2% crossfall from the crown')
        for k in range(1, 8):
            pid = f'pier_{pier}_closure_{k}'
            mesh = current_mesh(pid)
            v = mesh.vertices.copy()
            top = v[:, 2] > 1.0
            ys = np.unique(np.round(v[:, 1], 6))
            if len(v) != 8 or top.sum() != 4 or len(ys) != 2 or np.ptp(v[top, 2]) > 1e-6:
                raise ValueError(f'{pid}: unexpected closure (already sloped?)')
            if k == 4:
                x0, x1 = sorted(set(np.round(v[:, 0], 6)))
                zb = v[:, 2].min()
                sections = [[(x0, y, zb), (x1, y, zb), (x1, y, crown - 0.02 * abs(y)), (x0, y, crown - 0.02 * abs(y))]
                            for y in (ys[0], 0.0, ys[1])]
                new = loft(sections)
            else:
                v[top, 2] = crown - 0.02 * np.abs(v[top, 1])
                new = trimesh.Trimesh(vertices=v, faces=mesh.faces, process=False)
            p = parts[pid]
            store(pid, new, {}, (p.get('note', '') + ' Top follows the 2% crossfall of the pier top' +
                                 (', crowned at the centre line' if k == 4 else '') +
                                 ' (sheet 28 elevation, El. 929.95 at the crown); it was flat (third review).').strip(),
                  (meshes[pid]['extras'].get('note', '') + ' 상면이 교각 상면의 2% 횡단경사를 따르도록 했습니다' +
                   ('(중심선에서 정점)' if k == 4 else '') + '(도면 28 입면, 정점 El. 929.95; 3차 검토).').strip(),
                  [28], retopo=k == 4)
        pid = f'pier_{pier}_bed'
        old, new, m0, m1, t0, t1 = fit_bed(pid, crown)
        # Outline: the bed lies on the 3 ft wall top (sheet 28 typical section, sheet 29 module section), whose outer
        # modules end in R = 1 ft 6 in semicircles (sheet 29 plan); clip the rectangular bed to the pier top footprint.
        tris = [t[:, :2] for q in [f'pier_{pier}_module_{j}' for j in range(1, 9)] +
                [f'pier_{pier}_closure_{j}' for j in range(1, 8)] for t in current_mesh(q).triangles]
        footprint = unary_union([Polygon(t) for t in tris if Polygon(t).area > 1e-10]).buffer(0)
        if footprint.geom_type != 'Polygon' or len(footprint.interiors):
            raise ValueError(f'pier_{pier}: unexpected top footprint')
        footprint = orient(footprint.simplify(1e-7), 1.0)
        bed_area = np.ptp(new.vertices[:, 0]) * np.ptp(new.vertices[:, 1])
        z0, z1 = new.bounds[0][2] - 0.1, new.bounds[1][2] + 0.1
        prism = CrossSection([list(footprint.exterior.coords)[:-1]]).extrude(z1 - z0).translate((0, 0, z0)).to_mesh()
        prism = trimesh.Trimesh(vertices=np.asarray(prism.vert_properties)[:, :3], faces=np.asarray(prism.tri_verts),
                                process=False)
        clipped = solid(trimesh.boolean.intersection([new, prism], engine='manifold'), pid)
        cut_area, cut_volume = bed_area - footprint.area, new.volume - clipped.volume
        if not (0.17 < cut_area < 0.19 and 0 < cut_volume < 0.006):
            raise ValueError(f'{pid}: unexpected corner trim ({cut_area:.6f} m2, {cut_volume:.6f} m3)')
        p = parts[pid]
        store(pid, clipped, dict(thickness_min_in=round(t0 / IN, 2), thickness_max_in=round(t1 / IN, 2),
                                 end_radius_ft=1.5),
              (p.get('note', '') + f' Bottom fitted to the pier top, level along X with the 2% crossfall (sheet 28); '
               f'top unchanged on the deck soffit, so the bed is {t0 / IN:.2f} to {t1 / IN:.2f} in thick. Outline '
               f'trimmed to the 3 ft wall top with its R = 1 ft 6 in ends (sheet 28 typical section, sheet 29 plan and '
               f'section); the rectangular corners ({cut_area:.4f} m2) had no support (third review).').strip(),
              (meshes[pid]['extras'].get('note', '') + f' 하면을 교각 상면(X 방향 수평, 2% 횡단경사)에 맞췄고 상면은 데크 '
               f'하면 그대로 두어 두께 {t0 / IN:.2f}~{t1 / IN:.2f} in입니다(도면 28). 평면 외곽은 R = 1 ft 6 in 끝단을 가진 '
               f'3 ft 벽체 상면에 맞춰 받침 없는 직사각형 모서리({cut_area:.4f} m2)를 잘라냈습니다(도면 28 표준 단면, '
               f'도면 29 평면·단면; 3차 검토).').strip(), [28, 29], retopo=True)
        print(f'pier_{pier}: closures sloped; bed bottom moved {m0 * 1000:+.2f}..{m1 * 1000:+.2f} mm, '
              f'{t0 / IN:.3f}..{t1 / IN:.3f} in thick; corners trimmed {cut_area:.6f} m2 / {cut_volume:.6f} m3')

    # --- 2. Wingwalls and wingwall closure pours move with the cap bottom -----------------------------------
    for b, s in ((1, -1), (2, 1)):
        dz = new_bottom[b] - OLD_BOTTOM
        ledge_top = slab_top(BENT_X, DECK_EDGE) - SLAB_BUILDUP + LEDGE
        for side in (-1, 1):
            for pid in (f'wing_{b}_{side}', f'wing_joint_{b}_{side}'):
                mesh = current_mesh(pid)
                lo, hi = mesh.bounds
                if not (len(mesh.vertices) == 8 and np.isclose(lo[2], OLD_BOTTOM, atol=2e-6)
                        and np.isclose(hi[2] - lo[2], WING_H, atol=2e-6)
                        and np.isclose(max(abs(lo[1]), abs(hi[1])), DECK_EDGE, atol=1e-5)
                        and np.isclose(min(abs(lo[1]), abs(hi[1])), WING_IN_Y, atol=1e-5)):
                    raise ValueError(f'{pid}: unexpected wingwall box (already raised?)')
                new = trimesh.Trimesh(vertices=mesh.vertices + [0, 0, dz], faces=mesh.faces, process=False)
                if not np.isclose(new.bounds[1][2], ledge_top, atol=2e-6):
                    raise ValueError(f'{pid}: top is not flush with the ledge top')
                joint = 'joint' in pid
                store(pid, new, dict(bottom_el_ft=round(el(new.bounds[0][2]), 2),
                                     top_el_ft=round(el(new.bounds[1][2]), 2)),
                      (('1 ft UHPC wingwall closure pour (sheets 23, 24), full wingwall height. ' if joint else '') +
                       'Raised 3.29 in with the end-bent bottom (decision, third review): 3 ft 8 in high (sheets 24, 27), '
                       'flush with the cap bottom and with the ledge top at the deck edge (sheet 24 section A-A), '
                       'El. 926.48 to 930.15; the approach slab bears on it through the 1 in UHPC bed (sheet 53 '
                       'section A-A).'),
                      (('날개벽 1 ft UHPC 연결 타설부(도면 23·24)로 날개벽 전체 높이입니다. ' if joint else '') +
                       '교대 하단과 함께 3.29 in 올렸습니다(3차 검토 결정): 높이 3 ft 8 in(도면 24·27), 하단은 교대 하단, '
                       '상단은 데크 가장자리의 받침턱 상단과 같으며(도면 24 단면 A-A) El. 926.48~930.15입니다. 접속 '
                       '슬래브는 1 in UHPC 받침층을 거쳐 얹힙니다(도면 53 단면 A-A).'), [24, 27, 53])
                print(f'{pid}: El. {el(lo[2]):.3f}..{el(hi[2]):.3f} -> {el(new.bounds[0][2]):.3f}..'
                      f'{el(new.bounds[1][2]):.3f}')

    # --- 3. Wingwall UHPC beds (new parts) -------------------------------------------------------------------
    for b, s in ((1, -1), (2, 1)):
        for side in (-1, 1):
            panel_id = f'approach_{b}_{1 if side == -1 else 6}'
            panel = current_mesh(panel_id)
            top_of_wing = current_mesh(f'wing_{b}_{side}').vertices[:, 2].max()     # already raised in step 2
            if not np.isclose(top_of_wing, new_bottom[b] + WING_H, atol=2e-6):
                raise ValueError(f'wing_{b}_{side}: not raised')
            px = np.unique(np.round(np.abs(panel.vertices[:, 0]), 6))
            xs = [BACK_X] + [x for x in px if BACK_X + 1e-3 < x < WING_END_X - 1e-3] + [WING_END_X]
            sections, gaps = [], []
            for x in xs:
                loop = []
                for y in (DECK_EDGE, WING_IN_Y):
                    # probe just inside the panel so the line cannot miss the edge facets
                    hx = s * min(max(x, BACK_X + 1e-6), WING_END_X)
                    hy = side * (y - 1e-6 if y == DECK_EDGE else y)
                    hits = zhits(panel, hx, hy)
                    if len(hits) != 2:
                        raise ValueError(f'{panel_id}: no soffit at x={x}, y={y}')
                    gaps.append(hits[0] - top_of_wing)
                    loop.append((s * x, side * y, hits[0]))
                sections.append([(s * x, side * DECK_EDGE, top_of_wing), (s * x, side * WING_IN_Y, top_of_wing),
                                 loop[1], loop[0]])
            if min(gaps) <= 0:
                raise ValueError(f'wing_bed_{b}_{side}: approach soffit below the wing top')
            mesh = loft(sections)
            t0, t1 = min(gaps) / IN, max(gaps) / IN
            bent = 'End Bent 1' if b == 1 else 'End Bent 4'
            add(f'wing_bed_{b}_{side}', mesh, f'{bent} Wingwall {side} 1 in UHPC bedding layer',
                f'교대 {b} 날개벽 {side} 1 in UHPC 받침층', 'bearings', BED_COLOR, [24, 27, 53],
                'Drawing dimensions; thickness follows the flat wing top', '도면 치수 · 두께는 평탄한 날개벽 상단에 따름',
                f'UHPC bed between the wingwall (and its 1 ft closure pour) and the approach slab: "1 in UHPC bed (typ.)", '
                f'sheet 53 section A-A, also drawn on sheet 24 section A-A. The precast wing top is flat (sheet 27) while '
                f'the slab follows the 2% crossfall and the vertical curve, so the fill is {t0:.2f} to {t1:.2f} in thick.',
                f'날개벽(및 1 ft 연결 타설부)과 접속 슬래브 사이의 UHPC 받침층입니다(도면 53 단면 A-A "1 in UHPC BED '
                f'(TYP.)", 도면 24 단면 A-A). 프리캐스트 날개벽 상단은 평탄하고(도면 27) 슬래브는 2% 횡단경사와 종단곡선을 '
                f'따르므로 두께는 {t0:.2f}~{t1:.2f} in입니다.',
                dict(thickness_in=1, thickness_min_in=round(t0, 2), thickness_max_in=round(t1, 2),
                     length_ft=10, width_ft=3))
            print(f'wing_bed_{b}_{side}: added, {t0:.2f}..{t1:.2f} in, {mesh.volume:.5f} m3')

    # --- 4. Railing 1/2 in neoprene expansion joints (new parts) ---------------------------------------------
    for b, s, k in ((1, -1, 0), (2, 1, 3)):
        for side in (-1, 1):
            closure, transition = current_mesh(f'rail_closure_{k}_{side}'), current_mesh(f'approach_rail_{b}_{side}')
            mesh = rail_mesh([s * STEP_X, s * JOINT_X], side)
            near = mesh.vertices[np.isclose(mesh.vertices[:, 0], s * STEP_X)]
            far = mesh.vertices[np.isclose(mesh.vertices[:, 0], s * JOINT_X)]
            for face, other, x in ((near, closure, STEP_X), (far, transition, JOINT_X)):
                end = other.vertices[np.isclose(other.vertices[:, 0], s * x, atol=1e-5)]
                if len(end) != 6 or not same_points(end, face):
                    raise ValueError(f'rail_joint_{b}_{side}: does not meet its neighbour at |X| = {x}')
            bent = 'End Bent 1' if b == 1 else 'End Bent 4'
            n = 1 if side == 1 else 2
            add(f'rail_joint_{b}_{side}', mesh, f'{bent} railing ½ in neoprene expansion joint {n}',
                f'교대 {b} 난간 ½ in 네오프렌 신축줄눈 {n}', 'joints', JOINT_COLOR, [51],
                'Drawing dimensions', '도면 치수',
                '1/2 in neoprene expansion joint between the 91 ft 6 in bridge railing and the TFC transition, '
                'full railing height (sheet 51 plan and elevation); filler through the FC section of sheet 51, '
                'standing on the approach slab top.',
                '91 ft 6 in 교량 난간과 TFC 전이 난간 사이의 ½ in 네오프렌 신축줄눈입니다(도면 51 평면·입면, 난간 전체 '
                '높이). 도면 51 FC 단면 전체를 채우며 접속 슬래브 상면 위에 놓입니다.',
                dict(length_in=0.5, height_ft=2.75, base_width_ft=round(16 / 12, 4), deck_edge_to_toe_ft=1.5,
                     rear_setback_in=2, top_width_in=9, toe_height_in=3))
            print(f'rail_joint_{b}_{side}: added, |X| {STEP_X:.4f}..{JOINT_X:.4f}, {mesh.volume:.6f} m3')

    # --- 5. Barrier delineators on the upper front face (sheet 51 sections A-A / B-B) ----------------------
    rails = {f'rail_{i}_{side}': current_mesh(f'rail_{i}_{side}') for i in (1, 2, 3) for side in (-1, 1)}
    for side in (-1, 1):
        for k in range(3):
            pid = f'delineator_{side}_{k}'
            old = current_mesh(pid)
            lo, hi = old.bounds
            x0 = float(np.mean([lo[0], hi[0]]))
            if not (np.allclose(hi - lo, [DEL_LENGTH, 0.06 * FT, 0.2 * FT], atol=2e-6)
                    and np.isclose(np.mean([lo[1], hi[1]]), side * 6.04012, atol=1e-5)
                    and np.isclose(x0, (k - 1) * 40 * FT, atol=1e-5)):
                raise ValueError(f'{pid}: unexpected delineator (already moved?)')
            v = old.vertices
            order = [(v[i, 0] > x0, v[i, 1] > np.mean([lo[1], hi[1]]), v[i, 2] > np.mean([lo[2], hi[2]]))
                     for i in range(8)]
            if order != [(ix, iy, iz) for ix in (False, True) for iy in (False, True) for iz in (False, True)]:
                raise ValueError(f'{pid}: unexpected vertex order')
            rid = next(r for r, m in rails.items() if r.endswith(f'_{side}') and
                       m.bounds[0][0] < x0 - DEL_LENGTH < x0 + DEL_LENGTH < m.bounds[1][0])
            rv = rails[rid].vertices
            st = np.unique(np.round(rv[:, 0], 6))
            j = np.searchsorted(st, x0)
            xa, xb = st[j - 1], st[j]
            if not xa < x0 - DEL_LENGTH / 2 < x0 + DEL_LENGTH / 2 < xb:
                raise ValueError(f'{pid}: straddles a railing station')
            sec_a, sec_b = rv[np.isclose(rv[:, 0], xa, atol=1e-6)], rv[np.isclose(rv[:, 0], xb, atol=1e-6)]

            def corner(sec, y, top):
                at = sec[np.isclose(np.abs(sec[:, 1]), y, atol=1e-5)]
                return at[np.argmax(at[:, 2]) if top else 0]
            new = np.zeros((8, 3))
            for ix, xe in enumerate((x0 - DEL_LENGTH / 2, x0 + DEL_LENGTH / 2)):
                t = (xe - xa) / (xb - xa)
                top = (1 - t) * corner(sec_a, FRONT_TOP_Y, True) + t * corner(sec_b, FRONT_TOP_Y, True)
                brk = (1 - t) * corner(sec_a, BREAK_Y, True) + t * corner(sec_b, BREAK_Y, True)
                u = (brk - top) / np.linalg.norm(brk - top)               # down the upper batter
                nrm = np.array([0.0, -side * abs(u[2]), abs(u[1])])        # out of the face, toward the roadway
                p_top = top + u * (DEL_TOP_DROP / abs(u[2]))
                p_bot = p_top + u * DEL_FACE
                back = {True: p_top, False: p_bot}
                for iy in (False, True):
                    outward = (iy if side == -1 else not iy)              # the roadway side has the smaller |Y|
                    for iz in (False, True):
                        pt = back[iz] + (nrm * DEL_PROUD if outward else 0)
                        new[ix * 4 + iy * 2 + iz] = [xe, pt[1], pt[2]]
            mesh = trimesh.Trimesh(vertices=new, faces=old.faces, process=False)
            if not np.isclose(mesh.volume, DEL_FACE * DEL_PROUD * DEL_LENGTH, rtol=1e-6):
                raise ValueError(f'{pid}: unexpected delineator volume')
            store(pid, mesh, dict(face_height_in=3, projection_in=2, top_below_rail_top_in=5.4,
                                  length_along_rail_ft=0.2),
                  'Spacing does not exceed 40 ft (sheets 22, 51). Mounted on the upper front (traffic) face as drawn '
                  'in sheet 51 sections A-A and B-B: 3 in on the batter, 2 in proud of it, top 5.4 in below the railing '
                  'top (scaled at 1 in = 1 ft; not dimensioned). The 0.2 ft length along the railing is a '
                  'visualisation value.',
                  '40 ft 이하 간격입니다(도면 22·51). 도면 51 단면 A-A·B-B의 작도대로 난간 전면(차도 측) 상부 경사면에 '
                  '붙였습니다: 경사면 길이 3 in, 돌출 2 in, 상단은 난간 상단보다 5.4 in 아래(1 in = 1 ft 축척 측정, '
                  '치수 기입 없음). 난간 방향 길이 0.2 ft는 시각화용입니다.', [22, 51],
                  basis='Drawing position and size scaled from sheet 51 sections; length along the railing estimated',
                  basis_ko='도면 51 단면에서 축척 측정한 위치·크기 · 난간 방향 길이 추정',
                  extras=dict(extents=[0.2, round(2 / 12, 6), 0.25]))
            print(f'{pid}: centre Y {np.mean([lo[1], hi[1]]):+.4f} Z {np.mean([lo[2], hi[2]]):.4f} -> '
                  f'Y {mesh.vertices[:, 1].mean():+.4f} Z {mesh.vertices[:, 2].mean():.4f} on {rid}')

    # --- 6. TFC transitions: 15 ft 8 in (decision) with the E 706-TTFC sections; overlay edge on the toe --------
    key_x = [JOINT_X + t * IN for t in TFC_T]                                  # A-A, B-B, C-C, D-D, end
    for b, s in ((1, -1), (2, 1)):
        panel = current_mesh(f'approach_{b}_1')
        px = np.unique(np.round(np.abs(panel.vertices[:, 0]), 6))
        stations = sorted(key_x + [float(x) for x in px if JOINT_X + 0.02 < x < TFC_END_X - 0.02
                                   and all(abs(x - k) > 0.02 for k in key_x)])
        for side in (-1, 1):
            pid = f'approach_rail_{b}_{side}'
            p, ex = parts[pid], meshes[pid]['extras']
            if OLD_TFC_NOTE not in p['note'] or OLD_TFC_NOTE_KO not in ex.get('note', ''):
                raise ValueError(f'{pid}: unexpected transition note')
            old = current_mesh(pid)
            xs = np.unique(np.round(np.abs(old.vertices[:, 0]), 6))
            if not (len(old.vertices) == 36 and np.isclose(xs[0], JOINT_X, atol=1e-5)
                    and np.isclose(xs[-1], TFC_END_X, atol=1e-5)
                    and np.allclose(rail_mesh([s * x for x in xs], side).vertices, old.vertices, atol=2e-5)):
                raise ValueError(f'{pid}: not the constant FC section of revision 1.2')
            mesh = tfc_mesh(stations, s, side)
            store(pid, mesh, dict(length_ft=round((TFC_END_X - JOINT_X) / FT, 4), base_width_ft=round(16 / 12, 4),
                                  base_width_end_in=9, taper_length_ft=round(137 / 12, 4), top_width_in=9,
                                  toe_height_in=3, rear_setback_in=2, height_ft=2.75,
                                  sections_from_joint_in=dict(A=0, B=86, C=97, D=137)),
                  TFC_NOTE, TFC_NOTE_KO, [51, 52, 53, 54, 55],
                  basis='Drawing dimensions (standard E 706-TTFC-01/-02 sections; taper drawn on sheets 54, 55)',
                  basis_ko='도면 치수(표준도 E 706-TTFC-01/-02 단면, 도면 54·55 평면의 경사 변화)', retopo=True)
            print(f'{pid}: TFC sections, {old.volume:.4f} -> {mesh.volume:.4f} m3, {len(mesh.vertices)} vertices')
        pid = f'approach_overlay_{b}'
        old = current_mesh(pid)
        v = old.vertices
        ox = np.unique(np.round(np.abs(v[:, 0]), 6))
        if not (len(v) == 66 and np.isclose(np.abs(v[:, 1]).max(), DECK_EDGE - 18 * IN, atol=1e-5)
                and np.allclose(v[:, 2] - [slab_top(x, y) for x, y, _ in v], np.where(
                    v[:, 2] - [slab_top(x, y) for x, y, _ in v] > OVERLAY / 2, OVERLAY, 0), atol=2e-5)):
            raise ValueError(f'{pid}: unexpected approach overlay')

        def half(x):
            return DECK_EDGE - (2 + float(np.interp((x - JOINT_X) / IN, TFC_T, TFC_BASE))) * IN if x > JOINT_X \
                else DECK_EDGE - 18 * IN
        main = [STEP_X] + stations
        tail = [TFC_END_X] + [x for x in ox if x > TFC_END_X + 0.02]
        mesh = overlay_mesh(main, tail, s, half)
        store(pid, mesh, dict(edge_follows_tfc_toe=True),
              'LMC-VE overlay, 1 1/2 in (sheets 23, 24, 53), on the approach slab top up to the railing toe (sheet 53 '
              'section A-A). Along the TFC transitions its edge follows the tapering toe of standard E 706-TTFC-01/-02 '
              '(sheets 54, 55): 1 ft 6 in from the deck edge at the joint, 11 in from 11 ft 5 in to the transition end '
              '(third review).',
              '접속 슬래브 상면의 1 1/2 in LMC-VE 포장(도면 23·24·53)으로 난간 하단까지 덮습니다(도면 53 단면 A-A). TFC 전이 '
              '난간 구간에서는 표준도 E 706-TTFC-01/-02(도면 54·55)의 하단선을 따라 줄눈에서 데크 가장자리로부터 1 ft 6 in, '
              '11 ft 5 in부터 전이 끝까지 11 in입니다(3차 검토).', [54, 55], retopo=True)
        print(f'{pid}: edge on the TFC toe, {old.volume:.5f} -> {mesh.volume:.5f} m3')

    # --- Write --------------------------------------------------------------------------------------------------
    while len(binary) % 4:
        binary.append(0)
    gltf['buffers'][0]['byteLength'] = len(binary)
    encoded = json.dumps(gltf, ensure_ascii=True, separators=(',', ':')).encode()
    encoded += b' ' * ((-len(encoded)) % 4)
    out = (struct.pack('<III', 0x46546c67, 2, 28 + len(encoded) + len(binary)) +
           struct.pack('<II', len(encoded), 0x4e4f534a) + encoded + struct.pack('<II', len(binary), 0x004e4942) + binary)

    lo = np.array([p['bounds_m'][0] for p in manifest['parts']]).min(axis=0)
    hi = np.array([p['bounds_m'][1] for p in manifest['parts']]).max(axis=0)
    old_lo, old_hi = (np.array(b, dtype=float) for b in manifest['bounds_m'])
    lo = np.where(np.isclose(lo, old_lo, atol=1e-5), old_lo, lo)
    hi = np.where(np.isclose(hi, old_hi, atol=1e-5), old_hi, hi)
    manifest['bounds_m'] = [lo.tolist(), hi.tolist()]
    manifest['glb_bounds_m'] = [[lo[0], lo[2], -hi[1]], [hi[0], hi[2], -lo[1]]]
    for item in manifest.get('detail_coverage', []):
        if item.get('feature') == 'Piers, abutments and wingwalls':
            item['detail'] = ('Includes 8 modules per pier with vertical UHPC, rounded wall ends, segmented end bents with '
                              'the 9 in pavement ledge and 4 wingwalls on 1 in UHPC beds. End-bent seats follow the '
                              'roadway profile and the precast depths of sheet 24 (bottom El. 926.48; the sheet 23 '
                              'elevations are 0.27 ft lower and not followed). Pier and end-bent tops, closures included, '
                              'follow the 2% crossfall, and the beds sit on them. Internal pile pockets are shown as '
                              'filled envelopes.')
            item['sources'] = sorted(set(item['sources']) | {9, 24, 27, 53})
        elif item.get('feature') == 'Approach slabs and railings':
            item['detail'] = ('Each approach includes 6 panels and connections, with the 4 ft 1 in x 1 ft 6 in outer '
                              'corner cutbacks. FC railing sections follow sheet 51 (top corner radii omitted); the '
                              'TFC transitions are 15 ft 8 in long and follow the sections of standard E 706-TTFC-01/-02 '
                              '(taper drawn on sheets 54, 55; 3/4 in chamfers omitted), with the approach overlay edge on '
                              'their toe. The 1/2 in neoprene railing joints and the barrier delineators on the upper '
                              'front face are modelled (sheet 51). The 6 ft sleeper slabs sit as in sheet 59 section '
                              'B-B; their 2 ft lug step is simplified.')
            item['sources'] = sorted(set(item['sources']) | {52, 54})
    manifest['review_correction_3'] = TAG
    manifest['revision'] = REVISION
    manifest['review_correction_record_3'] = dict(
        source_pdf_pages=[9, 21, 22, 23, 24, 27, 28, 29, 51, 52, 53, 54, 55, 62, 63, 64],
        printed_sheets=[9, 21, 22, 23, 24, 27, 28, 29, 51, 52, 53, 54, 55, 62, 63, 64],
        external_references=[dict(document='INDOT Standard Drawings E 706-TTFC-01 and -02 (Sept. 2013), referenced by '
                                           'sheet 51 note 4 and sheet 52', url=TTFC_URL, sha256=TTFC_SHA256,
                                  used_for='15 ft 8 in pay limits (-01) and the transition sections A-A to D-D (-01, -02)')],
        corrections={
            'end_bent_bottom': 'cap bottoms raised 0.0836 m (3.29 in) from El. 926.21 to 926.48: precast depth 3 ft 0 in '
                               'at the outer end and 3 ft 4 3/4 in at the inner end as written on sheet 24; seat unchanged',
            'wingwalls': 'wingwalls and wingwall closure pours raised 3.29 in with the cap bottom: El. 926.48..930.15, '
                         'top flush with the ledge top at the deck edge (sheet 24 section A-A)',
            'wingwall_beds': 'four 1 in UHPC beds added between the wings and the approach slab (sheet 53 section A-A)',
            'railing_neoprene_joints': 'four 1/2 in neoprene joint fillers added between the bridge railing and the '
                                       'TFC transitions, FC section (sheet 51)',
            'barrier_delineators': 'six delineators moved from the railing top to the upper front face as drawn in '
                                   'sheet 51 sections A-A and B-B (scaled)',
            'tfc_transition_sections': 'the four TFC transitions rebuilt from the constant FC section to the sections '
                                       'of standard E 706-TTFC-01/-02 (16 in base at the joint, 11 5/8 in at 7 ft 2 in, '
                                       '11 in at 8 ft 1 in, 9 in vertical wall from 11 ft 5 in), as drawn in plan on '
                                       'sheets 54 and 55',
            'approach_overlay_edges': 'approach overlay edges follow the TFC toe (sheet 53 section A-A: overlay to the '
                                      'railing toe)',
            'end_bent_closures_and_beds': 'central closures crowned with the 2% crossfall (sheet 23); bed bottoms '
                                          'fitted to the level, crowned cap tops (were up to 1.5 mm off and 4.6 mm into '
                                          'the closures)',
            'pier_closures_and_beds': 'pier closure tops on the 2% crossfall, closure 4 crowned (sheet 28); bed '
                                      'bottoms fitted to the pier tops and bed outlines trimmed to the wall top with '
                                      'its R = 1 ft 6 in ends (sheets 28, 29)'},
        decisions=[
            dict(id='end-bent-absolute-elevation', reading='roadway profile (sheets 9, 21, 62-64) less the 22 1/2 in '
                 'build-up for the seat, and the written precast depths of sheet 24 for the bottom',
                 rejected='the absolute elevations of sheet 23 (seat 929.21 / 929.61, bottom 926.21)',
                 reasoning='The profile appears on four sheets, and the pier sheet 28 (crown 929.95 + written 1 in bed '
                           '+ 1 ft 8 in slab + 1 1/2 in overlay = 931.825 against 931.82) agrees with it. Sheet 24 '
                           'writes the module depths (3 ft 0 in / 3 ft 4 3/4 in), and the sheet 23 elevation '
                           'differences repeat them. All five sheet 23 elevations sit a uniform 0.27 ft below that '
                           'datum, which would need a 4 1/4 in bed against the 1 in drawn on sheets 23, 24, 28 and 53. '
                           'Keeping El. 926.21 made the modules 3.3 in deeper than written.'),
            dict(id='wingwall-top-elevation', reading='same datum: 3 ft 8 in wing flush with the cap bottom and the '
                 'ledge top (sheets 24, 27)', rejected='sheet 23 El. 929.88 at the bent ends',
                 reasoning='Follows from the end-bent decision; sheet 24 section A-A draws the wing bottom on the cap '
                           'bottom and its top on the ledge top, under the 1 in bed of sheet 53 section A-A.'),
            dict(id='tfc-transition-length-sheet-9', reading='15 ft 8 in (sheets 53 and 55, standard E 706-TTFC-01 '
                 'pay limits)', rejected='13.17 ft from the sheet 9 station callouts',
                 reasoning='The structural detail sheets draw 15 ft 8 in, and the standard that sheets 51 (note 4) and '
                           '52 make governing for the TFC details writes 15 ft 8 in as its pay limits. The sheet 9 '
                           'callouts are a 1 in = 50 ft roadway plan and agree with neither.'),
            dict(id='tfc-transition-section', reading='sections A-A to D-D of standard E 706-TTFC-01/-02, drawn in plan '
                 'on sheets 54 and 55', rejected='the constant FC outline of sheet 53 section A-A',
                 reasoning='Sheet 51 note 4 and sheet 52 make the standard governing for the TFC details, and it '
                           'writes every section dimension. The Type IA/IB module plans (sheets 54, 55, 3/4 in = 1 ft) '
                           'draw the same toe line: 16 in at the joint, 11.64 in at 7 ft 2 in, 9 in at 11 ft 5 in. '
                           'Sheet 53 section A-A is a typical 3/8 in = 1 ft section cut about 13 ft from the joint, '
                           'where both of these give a 9 in vertical wall.')],
        resolved_deviations=['railing-neoprene-joint', 'railing-delineator-position'],
        decided_deviations=['end-bent-absolute-elevation', 'wingwall-top-elevation', 'tfc-transition-length-sheet-9'],
        changed_parts=changed, added_parts=added, removed_parts=[], note_only_parts=notes_only,
        before_glb_sha256=before, after_glb_sha256=hashlib.sha256(out).hexdigest())
    manifest['known_deviations'] = []

    backup = ROOT / 'data/fem_research'
    backup.mkdir(exist_ok=True)
    (backup / 'us52-mud_before_review_correction_3.glb').write_bytes(original)
    (backup / 'us52-mud_manifest_before_review_correction_3.json').write_bytes(mp.read_bytes())
    path.write_bytes(out)
    mp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: manifest['review_correction_record_3'][k]
                      for k in ('changed_parts', 'added_parts', 'note_only_parts', 'before_glb_sha256',
                                'after_glb_sha256')}))


if __name__ == '__main__':
    correct()

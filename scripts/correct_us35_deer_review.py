"""One-time, drawing-confirmed correction of US 35 over Deer Creek (us35-deer), preserving unrelated GLB buffers.

    python scripts/correct_us35_deer_review.py

Source: drawings.pdf (INDOT B-45063 / Des 1900048, document 9721578); the printed sheet numbers equal the PDF page
numbers. Native axes: X along increasing station (X = 0 at Sta. 1271+60, the structure centre line), Y transverse
toward the south (Beam 1 / the north side is Y < 0), Z up from El. 837.11; q = X + tan(15 deg) Y is constant along
a bent line.

1. End-bent offset (sheet 13, END BENT DETAILS SHEET 1, plan view "Bent No. 1 shown, Bent 2 (similar)"): the 7 in
   dimension between "CL End Bent" and "CL Bridge", and the chain 5'-1 5/8" + 3 spa. @ 10'-6 1/4" = 31'-6 7/8" +
   6'-3 5/8" = 43'-0" (Bent 1: Beam 4 at the short end, Beam 1 at the long end; Bent 2 labels reversed). The 43 ft
   bent is centred 7 in along its own line from the bridge centre line, toward Beam 1 (north) at Bent 1 and toward
   Beam 4 (south) at Bent 2. Sheet 11 confirms it: the wing outer faces lie about 2 ft 2 in beyond the coping at
   Wings B and C and about 1 ft at Wings A and D. The piles (2'-1 1/2" + 5 @ 7'-9" + 2'-1 1/2", sheets 13-14), the
   wings at the bent ends, the upper integral concrete and the drain run move with the bent; beams, bearings and seat
   risers stay on the girder lines. The model had both bents centred on the bridge centre line.
2. Upper integral concrete (sheet 15, sections A-A at beams, B-B and C-C between beams; sheet 14 elevations): the
   concrete placed around the beam ends is the full 3'-10" width of the bent, 9" + 1'-2" + 1'-11", with its span face
   flush with the span face of the lower cap, up to the deck soffit. The model's integral closure bays stopped 0.38 m
   (along X) from the bent centre line, 0.2248 m behind that face, leaving a false shelf on the cap. Their span faces
   move to the cap face; their backs, tops and transverse limits are kept (outer bays follow item 1).
3. Wingwalls (sheet 13 plan; sheet 17 WINGWALL DETAILS and bill of materials): each wing is 1 ft thick and 12'-0"
   long measured parallel to the roadway from its tip to the span-face corner of the bent, its outer face continuing
   the bent end; bottom level at the cap bottom (El. 841.88 Wings A and B, 844.59 Wings C and D). The 5.7 CY of
   Class C concrete for the two wingwalls corresponds to the 8 ft that project beyond the back face, not 12 ft. The
   model ran the 12 ft from the bearing line, so each tip was 0.6048 m too far into the approach fill. Each wing now
   runs from the span face to the tip; the top keeps the model's rule (0.09 m below the extended deck surface).
4. FC railing section (sheet 23 section A-A; sheet 22 typical section): 2'-9" high, rear face 2" inside the coping,
   9" top, traffic face 2" over the upper 1'-11", 5" over the next 7", then a 3" vertical toe 1'-6" from the coping
   (17'-8" from the centre line, the 35'-4" clear roadway). The model had a 7 in toe and a single slope (face up to
   0.106 m off at the break). The rails keep their length (102'-4 3/8") and skewed ends.
5. Approach slabs (sheet 25 plans; sheet 11 plan and stations; sheet 3 typical sections): the 35'-11" slabs are
   split by the structure centre line into 18'-3" north / 17'-8" south at the west end and 17'-8" north / 18'-3"
   south at the east end (sheet 11 coping/RCBA lines agree), and their square ends are at Sta. 1270+76.06 and
   1272+43.94 (sheets 3 and 11), 20'-6" from the joint along the 17'-8" edge. The pavement and the deck both carry
   the 2% crown (sheets 3, 12, 22) and the slab top is flush with the deck at the Type IA joint (sheet 25 pavement
   ledge detail). The model centred both slabs (Y = +/-5.4737), put the square ends at X = +/-25.6344 and gave
   the slab a flat top between its edges (0.11 m below the profile grade at the centre line). The slabs are rebuilt
   with the plan edges and stations and a crowned top; the near (skewed) edge keeps the model's 25 mm display joint.
   The nominal transition-slab extensions, whose inner edge is by construction the slab edge, are refitted to it.

Not changed: the TFC transition envelopes (their shape is in INDOT standard drawings E706-TTFC, not in this plan
set; recorded as a known deviation), and all parts not listed in the record.

Requires numpy and trimesh.
"""
import hashlib
import json
import struct
from pathlib import Path

import numpy as np
import trimesh

FT, IN = .3048, .0254

ROOT = Path(__file__).resolve().parents[1]
BID = 'us35-deer'
BASE = ROOT / 'data/bridges' / BID
TAG = 'endbent-offset-integral-face-wings-fc-rail-approach-limits'
REVISION = '1.1-drawing-review'
TOL = 5e-5

TAN, COS, SIN = np.tan(np.radians(15)), np.cos(np.radians(15)), np.sin(np.radians(15))
LENGTH = (117 + 5 / 12) * FT              # sheet 11, out-out bridge floor
WIDTH = (38 + 4 / 12) * FT                # sheets 11, 12, 22, out-out coping
SLAB = 8 * IN
HALF_THICK = 46 * IN / 2 / COS            # half of the 3'-10" bent, along X: 0.604808
CAP_HALF_Y = 43 * FT * COS / 2            # 43 ft bent ends at Y = +/-6.329905 (end faces parallel to the roadway)
OFFSET = 7 * IN                           # sheet 13
WING_LEN, WING_T, WING_DROP = 12 * FT, FT, .09
INFILL_BACK, BACKWALL = .38, (.39, .60)   # model limits behind the bent centre line, kept
BEAMS_Y = np.linspace(-15.25 * FT, 15.25 * FT, 4)
FLANGE_HALF = 24.5 * IN
RAIL_LEN = (102 + 4.375 / 12) * FT        # sheet 23, out to out bridge railing
OLD_RAIL_EDGE, NEW_RAIL_EDGE = WIDTH / 2 - .05, WIDTH / 2 - 2 * IN
# FC section, sheet 23 section A-A: (inches from the rear face toward traffic, inches above the deck top).
FC_SECTION = [(0, 0), (16, 0), (16, 3), (11, 10), (9, 33), (0, 33)]
APPROACH_W = (35 + 11 / 12) * FT
APPROACH_T = FT
APPROACH_NEAR = LENGTH / 2 + .025         # model display joint, kept
APPROACH_EDGES = {-1: (-(18 + 3 / 12) * FT, (17 + 8 / 12) * FT),     # west: 18'-3" north, 17'-8" south
                  1: (-(17 + 8 / 12) * FT, (18 + 3 / 12) * FT)}      # east: 17'-8" north, 18'-3" south
APPROACH_FAR = {-1: (127076.06 - 127160) * FT, 1: (127243.94 - 127160) * FT}   # Sta. 1270+76.06 / 1272+43.94
EXT_FAR = RAIL_LEN / 2 + 15.667 * FT      # model extension length, kept

# Bent centre lines at Sta. 1271+02.5 / 1272+17.5 (q = u); `end` points to the approach fill, `span` to the span.
# The 7 in shift runs along the bent line (dq = 0): Bent 1 toward -Y (north), Bent 2 toward +Y (south).
BENTS = {0: dict(u=-57.5 * FT, end=-1, span=1, bottom=(841.88 - 837.11) * FT, toward='Beam 1 (north)',
                 shift=np.array([OFFSET * SIN, -OFFSET * COS, 0.0]), wings={-1: 'Wing B', 1: 'Wing A'}),
         1: dict(u=57.5 * FT, end=1, span=-1, bottom=(844.59 - 837.11) * FT, toward='Beam 4 (south)',
                 shift=np.array([-OFFSET * SIN, OFFSET * COS, 0.0]), wings={-1: 'Wing D', 1: 'Wing C'})}


def surface(x, y):
    return (853.07 - 837.11) * FT + .0235 * np.asarray(x) - .02 * np.abs(np.asarray(y))


def sx(u, y):
    return u - TAN * y


def to_native(v):
    """glTF Y-up vertices (as stored, no node matrix) -> native X station, Y transverse, Z up."""
    return np.column_stack([v[:, 0], -v[:, 2], v[:, 1]])


def to_gltf(v):
    return np.column_stack([v[:, 0], v[:, 2], -v[:, 1]])


def prism(stations, profile, fn, caps=None):
    """Closed solid: a counter-clockwise profile swept over stations through fn(s, a, b) -> xyz. Caps are fans from
    profile vertex 0 (star-shaped profiles) unless triangles are given in profile order."""
    n = len(profile)
    v = np.array([fn(s, a, b) for s in stations for a, b in profile], dtype=np.float64)
    f = []
    for k in range(len(stations) - 1):
        for j in range(n):
            a, b = k * n + j, k * n + (j + 1) % n
            f += [(a, b, b + n), (a, b + n, a + n)]
    caps = caps or [(0, j, j + 1) for j in range(1, n - 1)]
    last = (len(stations) - 1) * n
    f += [(i, k, j) for i, j, k in caps] + [(last + i, last + j, last + k) for i, j, k in caps]
    mesh = trimesh.Trimesh(vertices=v, faces=np.array(f), process=False)
    if not mesh.is_winding_consistent:
        raise ValueError('inconsistent prism winding')
    if mesh.volume < 0:
        mesh.invert()
    if not mesh.is_watertight or mesh.volume <= 0:
        raise ValueError('invalid prism')
    return mesh


def q_of(v):
    return v[:, 0] + TAN * v[:, 1]


def near(a, b):
    return abs(a - b) <= TOL


def correct():
    mp = BASE / 'model_manifest.json'
    raw_manifest = mp.read_bytes()
    manifest = json.loads(raw_manifest)
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

    def native_mesh(pid):
        prim = meshes[pid]['primitives'][0]
        if len(meshes[pid]['primitives']) != 1:
            raise ValueError(f'{pid}: expected one primitive')
        v = to_native(read(prim['attributes']['POSITION']).astype(np.float64))
        mesh = trimesh.Trimesh(vertices=v, faces=read(prim['indices']).reshape(-1, 3), process=False)
        if not mesh.is_watertight:
            raise ValueError(f'{pid}: not watertight')
        return mesh

    changes = []

    def store(pid, mesh, note, pages=(), dims=None, moved_only=False):
        prim = meshes[pid]['primitives'][0]
        if moved_only:                    # same topology: new positions only
            prim['attributes']['POSITION'] = append(to_gltf(mesh.vertices).astype('<f4'), 'VEC3', 5126)
        else:
            color = read(prim['attributes']['COLOR_0'])[0]
            prim['attributes'] = {
                'POSITION': append(to_gltf(mesh.vertices).astype('<f4'), 'VEC3', 5126),
                'COLOR_0': append(np.tile(color, (len(mesh.vertices), 1)).astype('u1'), 'VEC4', 5121)}
            gltf['accessors'][prim['attributes']['COLOR_0']]['normalized'] = True
            prim['indices'] = append(mesh.faces.reshape(-1, 1).astype('<u4'), 'SCALAR', 5125)
        if not mesh.is_watertight or mesh.volume <= 0:
            raise ValueError(f'{pid}: invalid corrected mesh')
        p = parts[pid]
        p['bounds_m'] = mesh.bounds.round(6).tolist()
        p['volume_m3'] = round(float(mesh.volume), 9)
        p['pdf_pages'] = sorted(set(p['pdf_pages']) | set(pages))
        if dims:
            p['dimensions'].update(dims)
        p['note'] = (p.get('note', '') + ' ' + note).strip()
        meshes[pid]['extras'].update(p)
        changes.append(pid)

    record = {}

    # --- 1-3. End bents: 7 in offset along the bent, full-width integral concrete, wings from the span face. ---
    for b, k in BENTS.items():
        u, end, span, bottom, shift = k['u'], k['end'], k['span'], k['bottom'], k['shift']
        cap = native_mesh(f'cap_{b + 1}')
        cv = cap.vertices
        seat = cv[:, 2].max()
        if (not near(cv[:, 1].min(), -CAP_HALF_Y) or not near(cv[:, 1].max(), CAP_HALF_Y)
                or not near(q_of(cv).min(), u - HALF_THICK) or not near(q_of(cv).max(), u + HALF_THICK)
                or not near(cv[:, 2].min(), bottom)):
            raise ValueError(f'cap_{b + 1}: unexpected original position')
        y_lo, y_hi = -CAP_HALF_Y + shift[1], CAP_HALF_Y + shift[1]
        side_note = (f'Centred 7 in along the bent from the bridge centre line, toward {k["toward"]}, sheet 13 '
                     f'(5\'-1 5/8" and 6\'-3 5/8" from the exterior beams to the bent ends).')

        moved = trimesh.Trimesh(vertices=cv + shift, faces=cap.faces, process=False)
        store(f'cap_{b + 1}', moved, side_note, [11, 13],
              dict(along_bent_center_offset_m=round(OFFSET, 4), along_bent_center_offset_toward=k['toward']),
              moved_only=True)

        for j in range(6):
            pid = f'pile_stub_{b}_{j}'
            pile = native_mesh(pid)
            pv = pile.vertices
            yc = (pv[:, 1].min() + pv[:, 1].max()) / 2
            xc = (pv[:, 0].min() + pv[:, 0].max()) / 2
            expected = np.linspace(-19.375 * FT * COS, 19.375 * FT * COS, 6)[j]
            if not near(yc, expected) or not near(xc, sx(u, expected)):
                raise ValueError(f'{pid}: unexpected original pile position')
            store(pid, trimesh.Trimesh(vertices=pv + shift, faces=pile.faces, process=False),
                  'Moved with the bent 7 in along its line; 2\'-1 1/2" from the bent ends, sheets 13-14.', [13],
                  moved_only=True)

        pid = f'end_bent_drain_{b}'
        drain = native_mesh(pid)
        dv = drain.vertices
        if not near(dv[:, 1].min(), -CAP_HALF_Y) or not near(dv[:, 1].max(), CAP_HALF_Y):
            raise ValueError(f'{pid}: unexpected original drain run')
        store(pid, trimesh.Trimesh(vertices=dv + shift, faces=drain.faces, process=False),
              'Schematic run moved with the bent (7 in along its line), sheet 13.', [13], moved_only=True)

        # Integral closure bays: span face to the cap face (sheet 15); outer bays to the moved bent ends.
        edges = [-CAP_HALF_Y] + [v for y in BEAMS_Y for v in (y - FLANGE_HALF, y + FLANGE_HALF)] + [CAP_HALF_Y]
        t_old = sorted([-INFILL_BACK, INFILL_BACK])
        t_new = sorted([end * INFILL_BACK, span * HALF_THICK])
        for j in range(0, len(edges) - 1, 2):
            pid = f'integral_infill_{b}_{j}'
            old = native_mesh(pid)
            ov = old.vertices
            y0, y1 = edges[j], edges[j + 1]
            if (not near(ov[:, 1].min(), y0) or not near(ov[:, 1].max(), y1)
                    or not near(q_of(ov).min(), u + t_old[0]) or not near(q_of(ov).max(), u + t_old[1])
                    or not near(ov[:, 2].min(), seat)
                    or abs((ov[:, 2] - surface(ov[:, 0], ov[:, 1]))[ov[:, 2] > seat + .1] + SLAB).max() > TOL):
                raise ValueError(f'{pid}: unexpected original closure bay')
            y0 = y_lo if j == 0 else y0
            y1 = y_hi if j == len(edges) - 2 else y1
            mesh = prism([u + t for t in t_new], [(y0, 0), (y1, 0), (y1, 1), (y0, 1)],
                         lambda s, y, h: (sx(s, y), y, seat * (1 - h) + (surface(sx(s, y), y) - SLAB) * h))
            store(pid, mesh, 'Span face brought flush with the span face of the 3\'-10" bent (it stopped 0.2248 m '
                  'short along X), sheet 15 sections A-A, B-B and C-C.' + (' Outer end follows the bent, '
                  'moved 7 in along its line, sheet 13.' if j in (0, len(edges) - 2) else ''), [13, 15])

        pid = f'backwall_{b}'
        old = native_mesh(pid)
        ov = old.vertices
        tb = sorted([u + end * BACKWALL[0], u + end * BACKWALL[1]])
        if (not near(ov[:, 1].min(), -CAP_HALF_Y) or not near(ov[:, 1].max(), CAP_HALF_Y)
                or not near(q_of(ov).min(), tb[0]) or not near(q_of(ov).max(), tb[1])):
            raise ValueError(f'{pid}: unexpected original back face')
        mesh = prism(tb, [(y_lo, 0), (y_hi, 0), (y_hi, 1), (y_lo, 1)],
                     lambda s, y, h: (sx(s, y), y, seat * (1 - h) + (surface(sx(s, y), y) - SLAB) * h))
        store(pid, mesh, 'Ends moved with the bent, 7 in along its line, sheet 13.', [13])

        # Wings: outer face on the bent end, 12 ft from the span-face corner to the tip (sheets 13, 17).
        q_face = u + span * HALF_THICK
        tq = sorted([q_face, q_face + end * WING_LEN])
        for side in (-1, 1):
            pid = f'wing_{b}_{side}'
            old = native_mesh(pid)
            ov = old.vertices
            yc_old = side * (CAP_HALF_Y - WING_T / 2)
            if (not near(ov[:, 1].min(), yc_old - WING_T / 2) or not near(ov[:, 1].max(), yc_old + WING_T / 2)
                    or not near(q_of(ov).min(), min(u, u + end * WING_LEN))
                    or not near(q_of(ov).max(), max(u, u + end * WING_LEN)) or not near(ov[:, 2].min(), bottom)):
                raise ValueError(f'{pid}: unexpected original wing')
            yc = (y_hi if side > 0 else y_lo) - side * WING_T / 2
            mesh = prism(tq, [(-WING_T / 2, 0), (WING_T / 2, 0), (WING_T / 2, 1), (-WING_T / 2, 1)],
                         lambda s, v, h: (sx(s, yc + v), yc + v,
                                          bottom * (1 - h) + (surface(sx(s, yc + v), yc + v) - WING_DROP) * h))
            store(pid, mesh, f'{k["wings"][side]}: 12 ft measured from the span-face corner of the bent to the tip '
                  '(the model had started the 12 ft at the bearing line, 0.6048 m too long); outer face on the bent '
                  'end, moved with the bent 7 in along its line. Sheets 13 and 17.', [13, 17],
                  dict(length_m=round(WING_LEN, 6), length_basis='tip to span-face corner of the bent, parallel to '
                       'the roadway', projection_beyond_back_face_m=round(WING_LEN - 2 * HALF_THICK, 6),
                       plan_name=k['wings'][side]))
        record[f'bent_{b + 1}'] = dict(
            shift_m=[round(float(c), 6) for c in shift[:2]], cap_y_m=[round(y_lo, 6), round(y_hi, 6)],
            integral_span_face_q_m=round(q_face, 6), wing_q_m=[round(t, 6) for t in tq])
        print(f'bent {b + 1}: shift {shift[:2].round(6)}, span face q={q_face:.6f}, wings q={np.round(tq, 6)}')

    # --- 4. FC railing section (sheet 23 section A-A). ---
    stations = np.linspace(-RAIL_LEN / 2, RAIL_LEN / 2, max(3, int(RAIL_LEN / .5)))
    for side in (-1, 1):
        pid = f'FC_rail_{side}'
        old = native_mesh(pid)
        ov = old.vertices
        rel = np.column_stack([np.abs(ov[:, 1]), ov[:, 2] - surface(ov[:, 0], ov[:, 1])])
        expected = [(OLD_RAIL_EDGE, 0), (OLD_RAIL_EDGE - 16 * IN, 0), (OLD_RAIL_EDGE - 16 * IN, 7 * IN),
                    (OLD_RAIL_EDGE - 9 * IN, 33 * IN), (OLD_RAIL_EDGE, 33 * IN)]
        if (len(ov) != 5 * len(stations) or not near(q_of(ov).min(), -RAIL_LEN / 2)
                or not near(q_of(ov).max(), RAIL_LEN / 2)
                or any(np.min(np.abs(rel - e).max(axis=1)) > TOL for e in expected)
                or any(np.min([np.abs(r - e).max() for e in expected]) > TOL for r in rel)):
            raise ValueError(f'{pid}: unexpected original FC section')
        edge = side * NEW_RAIL_EDGE
        section = [(v * IN, z * IN) for v, z in FC_SECTION]
        mesh = prism(stations, section, lambda s, v, z: (sx(s, edge - side * v), edge - side * v,
                                                         surface(sx(s, edge - side * v), edge - side * v) + z))
        store(pid, mesh, 'Section corrected to sheet 23 section A-A: 2\'-9" high, rear face 2" inside the coping, '
              '9" top, traffic face 2" over the upper 1\'-11", 5" over the next 7" and a 3" vertical toe 17\'-8" from '
              'the centre line (the model had a 7 in toe and one slope).', [22, 23],
              dict(height_m=round(33 * IN, 6), base_width_m=round(16 * IN, 6), top_width_m=round(9 * IN, 6),
                   toe_height_m=round(3 * IN, 6), rear_setback_m=round(2 * IN, 6),
                   section_profile_from_rear_m=[[round(a, 6), round(c, 6)] for a, c in section]))

    # --- 5. Approach slabs and their transition extensions (sheets 3, 11, 25). ---
    for end in (-1, 1):
        pid = f'approach_{end}'
        old = native_mesh(pid)
        ov = old.vertices
        q_near = end * APPROACH_NEAR
        if (not near(ov[:, 1].min(), -APPROACH_W / 2) or not near(ov[:, 1].max(), APPROACH_W / 2)
                or not near(np.abs(ov[:, 0]).max(), APPROACH_NEAR + TAN * APPROACH_W / 2 + 20.5 * FT)
                or not near(np.abs(q_of(ov)).min(), APPROACH_NEAR)):
            raise ValueError(f'{pid}: unexpected original approach slab')
        y0, y1 = APPROACH_EDGES[end]
        far = APPROACH_FAR[end]
        profile = [(y0, 0), (0.0, 0), (y1, 0), (y1, 1), (0.0, 1), (y0, 1)]
        mesh = prism(np.linspace(0, 1, 24), profile,
                     lambda t, y, h: ((1 - t) * sx(q_near, y) + t * far, y,
                                      surface((1 - t) * sx(q_near, y) + t * far, y) - APPROACH_T + h * APPROACH_T),
                     caps=[(0, 1, 4), (0, 4, 5), (1, 2, 3), (1, 3, 4)])
        north, south = -y0, y1
        label = {-1: ('18\'-3"', '17\'-8"'), 1: ('17\'-8"', '18\'-3"')}[end]
        store(pid, mesh, f'Plan limits corrected: {label[0]} north and {label[1]} south of the '
              f'structure centre line (35\'-11", sheet 25 and sheet 11), square end at Sta. '
              f'{"1270+76.06" if end < 0 else "1272+43.94"} (sheets 3 and 11); top follows the 2% crown, flush with '
              'the deck at the joint (sheets 3, 12, 25). The skewed edge keeps the 25 mm display joint.',
              [3, 11, 25],
              dict(north_width_m=round(north, 6), south_width_m=round(south, 6),
                   square_end_station='1270+76.06' if end < 0 else '1272+43.94', square_end_x_m=round(far, 6),
                   crowned_top=True))
        for side in (-1, 1):
            pid = f'extension_{end}_{side}'
            old = native_mesh(pid)
            ov = old.vertices
            yy_old = sorted([side * APPROACH_W / 2, side * WIDTH / 2])
            qq = sorted([end * LENGTH / 2, end * EXT_FAR])
            if (not near(ov[:, 1].min(), yy_old[0]) or not near(ov[:, 1].max(), yy_old[1])
                    or not near(q_of(ov).min(), qq[0]) or not near(q_of(ov).max(), qq[1])):
                raise ValueError(f'{pid}: unexpected original extension')
            yy = sorted([y0 if side < 0 else y1, side * WIDTH / 2])
            st = np.linspace(qq[0], qq[1], max(2, int((qq[1] - qq[0]) / .6) + 1))
            mesh = prism(st, [(yy[0], -APPROACH_T), (yy[1], -APPROACH_T), (yy[1], 0), (yy[0], 0)],
                         lambda s, y, z: (sx(s, y), y, surface(sx(s, y), y) + z))
            store(pid, mesh, 'Inner edge refitted to the corrected approach-slab edge (sheet 25); outer edge and '
                  'length unchanged.', [25])
        print(f'approach_{end}: Y [{y0:.4f}, {y1:.4f}], far X {far:.6f}')

    for item in manifest.get('detail_coverage', []):
        if item.get('feature') == 'Integral support topology':
            item['detail'] += (' Bents centred 7 in along their lines from the bridge centre line (sheet 13); integral '
                               'concrete flush with the cap span face (sheet 15); wings 12 ft from the span-face '
                               'corner to the tip (sheets 13, 17).')
        elif item.get('feature') == 'External rails and approaches':
            item['detail'] += (' FC section per sheet 23 section A-A; approach slabs 18\'-3"/17\'-8" either side of '
                               'the centre line, square ends at Sta. 1270+76.06 / 1272+43.94, crowned top.')
            for s in ('Primary PDF p.3', 'Primary PDF p.22'):
                if s not in item['sources']:
                    item['sources'].append(s)

    while len(binary) % 4:
        binary.append(0)
    gltf['buffers'][0]['byteLength'] = len(binary)
    encoded = json.dumps(gltf, ensure_ascii=True, separators=(',', ':')).encode()
    encoded += b' ' * ((-len(encoded)) % 4)
    out = (struct.pack('<III', 0x46546c67, 2, 28 + len(encoded) + len(binary)) +
           struct.pack('<II', len(encoded), 0x4e4f534a) + encoded + struct.pack('<II', len(binary), 0x004e4942) + binary)
    backup = ROOT / 'data/fem_research'
    backup.mkdir(exist_ok=True)
    (backup / f'{BID}_before_review_correction.glb').write_bytes(original)
    (backup / f'{BID}_manifest_before_review_correction.json').write_bytes(raw_manifest)
    path.write_bytes(out)

    manifest['review_correction'] = TAG
    previous = manifest.get('revision')
    manifest['revision'] = REVISION
    manifest['review_correction_record'] = dict(
        source_pdf_pages=[3, 11, 13, 14, 15, 17, 22, 23, 25], printed_sheets=[3, 11, 13, 14, 15, 17, 22, 23, 25],
        previous_revision=previous,
        corrections={
            'end_bent_offset': '43 ft bents centred 7 in along their lines from the bridge centre line, toward Beam 1 '
                               '(north) at Bent 1 and Beam 4 (south) at Bent 2; caps, piles, wings, back faces, outer '
                               'closure bays and drain runs moved with them (sheets 11, 13, 14)',
            'integral_concrete_span_face': 'closure bays extended 0.224808 m along X to the span face of the '
                                           '3\'-10" bent, q = -/+16.921192 m (sheet 15)',
            'wingwalls': '12 ft from the span-face corner of the bent to the tip, q = [-20.578792, -16.921192] and '
                         '[16.921192, 20.578792] m (was from the bearing line, 0.604808 m longer; sheets 13, 17)',
            'fc_railing_section': '3 in toe, 5 in over 7 in, 2 in over 23 in, 9 in top, 2 ft 9 in, rear face 2 in '
                                  'inside the coping; was 7 in toe and one slope (sheets 22, 23)',
            'approach_slabs': 'west Y = [-5.5626, 5.3848], east Y = [-5.3848, 5.5626] m (was +/-5.4737); square ends '
                              'at Sta. 1270+76.06 / 1272+43.94, X = -/+25.584912 m (was -/+25.634373); crowned top '
                              '(was flat between the edges, 0.11 m low at the centre line); extensions refitted '
                              '(sheets 3, 11, 25)'},
        values=record, changed_parts=changes,
        before_glb_sha256=before, after_glb_sha256=hashlib.sha256(out).hexdigest())
    deviations = [d for d in manifest.get('known_deviations', []) if d.get('id') != 'tfc-transition-section']
    deviations.append(dict(
        id='tfc-transition-section', parts='TFC_transition_*', source='sheets 11, 23 (PDF 11, 23)',
        deviation='The four TFC transitions keep the generic envelope (7 in toe, one sloped face, height easing to '
                  '0.70 m); at the butt joints with the corrected FC railing the traffic faces differ by up to about '
                  '0.1 m.',
        reason='The TFC shape is given by INDOT standard drawings E706-TTFC-01 to -03 and E706-CBRT, which are not '
               'part of this plan set.'))
    manifest['known_deviations'] = deviations
    text = json.dumps(manifest, indent=2)
    if b'\r\n' in raw_manifest:
        text = text.replace('\n', '\r\n')
    if raw_manifest.endswith(b'\n'):
        text += '\r\n' if b'\r\n' in raw_manifest else '\n'
    mp.write_bytes(text.encode('utf-8'))
    print(json.dumps({k: v for k, v in manifest['review_correction_record'].items() if k != 'values'}))


if __name__ == '__main__':
    correct()

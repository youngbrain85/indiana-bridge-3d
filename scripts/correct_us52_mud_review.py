"""One-time, drawing-confirmed correction of US 52 over Mud Creek (us52-mud), preserving unrelated GLB buffers.

    python scripts/correct_us52_mud_review.py

Source: drawings.pdf (2020-03-27 Stage 3 draft); the printed sheet numbers equal the PDF page numbers.

1. End-bent pavement ledge (sheets 21, 23, 24). Section A-A on sheets 23 and 24 shows the 3 ft precast bent with a
   9 in pavement ledge on its approach side, 8 in above the deck seat: plan El. 929.88 / 929.21 at the edges and
   930.28 / 929.61 at the centre (sheet 23 elevation), "9 in PVMT. LEDGE" and the 8 in step (sheet 24), and the
   sheet 21 note that the ledge was increased to 9 in. The 1 ft approach slab rests on the ledge and the 1 ft 8 in
   deck slab on the seat, both on a 1 in bed. The model's caps were flat at seat level, leaving the approach slab
   8 in (0.2032 m) above the bedding over the ledge. The outer 9 in of each cap module, the central closure and the
   bedding is raised 8 in; the seat, the cap bottoms and the bent position are unchanged.
2. Approach slab corner cutbacks (sheets 53-55, 58). The exterior modules IA/IB are 4 ft 8 in wide for 16 ft 5 in
   and 3 ft 2 in wide for the last 4 ft 1 in, so each outer corner of the 20 ft 6 in approach slab is cut back
   4 ft 1 in x 1 ft 6 in; the railing transition stops at the cutback, and the sleeper slab under it is 37 ft 4 in
   wide (sheet 58), flush with the cut-back edge (sheet 53 plan).
3. FC railing section (sheet 51, sections A-A and B-B): 2 ft 9 in high from the structural slab top; rear face 2 in
   inside the deck edge; 9 in top; front face 2 in batter over the upper 1 ft 11 in, 5 in over the next 7 in, and a
   3 in vertical toe at the deck-overlay edge (1 ft 6 in from the deck edge). The model had a 7 in toe, no rear
   setback and an 8 in top. Sheet 53 section A-A draws the approach transition with the same section, so the
   approach railings, already approximated with the FC section, take it as well.
4. Approach railing base (sheet 53 section A-A): the TFT transition is precast with the edge panel and stands on
   the 1 ft slab, the overlay abutting it. The model had it 1 1/2 in (the overlay) above the slab.
5. Railing joints (sheet 51 plan and elevation): the 1 ft 1 in (end bent) and 1 ft (pier) railing closure pours
   fill the whole gap between the precast railing segments over the deck closure pours, and the only railing joint
   is a 1/2 in neoprene expansion joint outside the 91 ft 6 in out-to-out bridge railing, between the bridge railing
   and the approach transition. The model had 1/4 in gaps at both ends of every closure. The neoprene filler is
   left as an open 1/2 in joint (no new part).
6. Support names (sheet 21): the supports are Bent No. 1, Pier No. 2, Pier No. 3 and Bent No. 4 ("END BENT
   DETAILS", sheet 23). The manifest called the east end bent "Abutment 2"; both end bents become "End Bent 1" /
   "End Bent 4". Part ids are unchanged.

The absolute end-bent datum is not changed: sheet 23 seat El. 929.61 at the centre conflicts with the roadway profile
(sheet 21 El. 931.76 at the bent less 1 1/2 in overlay, 20 in slab and 1 in bed = El. 929.885). The model keeps the
seat on the profile and the bent bottom at El. 926.21; this and the wingwall tops are recorded as known deviations.

Requires numpy, trimesh and manifold3d.
"""
import hashlib
import json
import struct
from pathlib import Path

import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'data/bridges/us52-mud'
FT = 0.3048
IN = FT / 12
TAG = 'ledge-cutback-fc-rail-joints-endbent4'

DECK_EDGE = 20 * FT + 2 * IN              # 40 ft 4 in out-to-out coping, half width 6.1468 m
TOE_Y = DECK_EDGE - 18 * IN               # front toe / overlay edge, 5.6896 m
BENT_X = 45 * FT                          # end-bent centre lines at +/-13.716 m (sta. 457+72 / 458+62)
BACK_X = BENT_X + 1.5 * FT                # approach face of the 3 ft cap, 14.1732 m
STEP_X = BACK_X - 9 * IN                  # end of the 9 in pavement ledge, 13.9446 m
FRONT_X = BENT_X - 1.5 * FT               # span face of the cap, 13.2588 m
LEDGE = 8 * IN                            # ledge above the seat, 0.2032 m
APPROACH_END_X = STEP_X + 20.5 * FT       # 20 ft 6 in approach slab, 20.193 m
CUT_X = STEP_X + (16 + 5 / 12) * FT       # 16 ft 5 in full width, then the 4 ft 1 in cutback, 18.9484 m
JOINT_X = STEP_X + 0.5 * IN               # approach transition end beyond the 1/2 in neoprene joint, 13.9573 m
SLEEPER_HALF = (37 + 4 / 12) * FT / 2     # 37 ft 4 in sleeper slab, 5.6896 m
# FC railing section, sheet 51: (inches inboard of the deck edge, inches above the structural slab top), in order
# front base, rear base, rear top, front top, batter break, toe top.
FC_SECTION = [(18, 0), (2, 0), (2, 33), (11, 33), (13, 10), (18, 3)]
# Structural slab top of the model's deck and approach slabs: finished grade El. 931.8375 at the structure centre
# line (local Z 0 = El. 910.80), 135 ft vertical curve between +/-0.5% tangents (x^2/27000 ft), 1 1/2 in overlay,
# 2% crossfall.
Z_SLAB_CL = (931.8375 - 910.80) * FT - 1.5 * IN

# Rail closure intervals (= transverse deck closure pours) and their deck closure part ids.
CLOSURES = {0: 'transverse_closure_0', 1: 'transverse_closure_1', 2: 'transverse_closure_2', 3: 'transverse_closure_3'}


def slab_top(x, y):
    return Z_SLAB_CL - x * x / (27000 * FT) - 0.02 * np.abs(y)


def loft(sections):
    """Closed solid through equal-length point loops; caps are fans from vertex 0 of each loop."""
    sections = [np.asarray(s, dtype=np.float64) for s in sections]
    k = len(sections[0])
    v = np.vstack(sections)
    faces = []
    for s in range(len(sections) - 1):
        a, b = s * k, (s + 1) * k
        for i in range(k):
            j = (i + 1) % k
            faces += [(a + i, a + j, b + j), (a + i, b + j, b + i)]
    last = (len(sections) - 1) * k
    for i in range(1, k - 1):
        faces += [(0, i + 1, i), (last, last + i, last + i + 1)]
    mesh = trimesh.Trimesh(vertices=v, faces=np.array(faces), process=False)
    if not mesh.is_winding_consistent:
        raise ValueError('inconsistent loft winding')
    if mesh.volume < 0:
        mesh.invert()
    if not mesh.is_watertight or mesh.volume <= 0:
        raise ValueError('invalid loft')
    return mesh


def rail_mesh(stations, sign):
    """FC railing from the sheet 51 section along the given X stations, standing on the structural slab top."""
    sections = []
    for x in stations:
        loop = []
        for inboard, up in FC_SECTION:
            y = DECK_EDGE - inboard * IN
            loop.append((x, sign * y, slab_top(x, y) + up * IN))
        sections.append(loop[4:] + loop[:4])          # start the cap fans at the batter break (the reflex vertex)
    return loft(sections)


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

    def original_mesh(pid):
        prim = meshes[pid]['primitives'][0]
        return trimesh.Trimesh(vertices=read(prim['attributes']['POSITION']).astype(np.float64),
                               faces=read(prim['indices']).reshape(-1, 3), process=False)

    def store(pid, mesh, dims, note_en, note_ko, pages, replace_note=False, basis=None, basis_ko=None):
        prim = meshes[pid]['primitives'][0]
        if not mesh.is_watertight or mesh.volume <= 0:
            raise ValueError(f'{pid}: corrected mesh is not a valid solid')
        old_count = gltf['accessors'][prim['attributes']['POSITION']]['count']
        attributes = {'POSITION': append(mesh.vertices.astype('<f4'), 'VEC3', 5126)}
        if len(mesh.vertices) == old_count and np.array_equal(mesh.faces, read(prim['indices']).reshape(-1, 3)):
            attributes['COLOR_0'] = prim['attributes']['COLOR_0']
        else:
            color = read(prim['attributes']['COLOR_0'])[0]
            attributes['COLOR_0'] = append(np.tile(color, (len(mesh.vertices), 1)).astype('u1'), 'VEC4', 5121)
            gltf['accessors'][attributes['COLOR_0']]['normalized'] = True
            prim['indices'] = append(mesh.faces.reshape(-1, 1).astype('<u4'), 'SCALAR', 5125)
        prim['attributes'] = attributes
        p = parts[pid]
        p['bounds_m'] = mesh.bounds.round(6).tolist()
        p['volume_m3'] = round(float(mesh.volume), 6)
        p['dimensions'].update(dims)
        p['pdf_pages'] = sorted(set(p.get('pdf_pages', [])) | set(pages))
        p['note'] = note_en if replace_note else (p.get('note', '') + ' ' + note_en).strip()
        if basis:
            p['basis'] = basis
        extras = meshes[pid]['extras']
        extras.update(bounds_m=p['bounds_m'], volume_m3=p['volume_m3'], dimensions=p['dimensions'],
                      pdf_pages=p['pdf_pages'])
        extras['note'] = note_ko if replace_note else (extras.get('note', '') + ' ' + note_ko).strip()
        if basis_ko:
            extras['basis'] = basis_ko
        changed.append(pid)
        return p

    changed = []

    def check_old_rail(pid, ov, lift):
        """The original railing section: 1 ft 6 in base flush with the deck edge, 7 in toe, base `lift` above the slab."""
        for x in np.unique(np.round(ov[:, 0], 6)):
            at = ov[np.isclose(ov[:, 0], x, atol=1e-5)]
            if len(at) != 6 or not np.isclose(np.abs(at[:, 1]).max(), DECK_EDGE, atol=1e-5):
                raise ValueError(f'{pid}: unexpected railing section')
            toe = np.sort(at[np.isclose(np.abs(at[:, 1]), TOE_Y, atol=1e-5), 2])
            if len(toe) != 2 or not np.isclose(toe[1] - toe[0], 0.176784, atol=1e-4):
                raise ValueError(f'{pid}: railing toe is not the expected original 7 in')
            if not np.isclose(toe[0] - slab_top(x, TOE_Y), lift, atol=1e-4):
                raise ValueError(f'{pid}: railing base is not {lift:.4f} m above the slab top as expected')

    # --- 1. End-bent pavement ledge -------------------------------------------------------------------------
    for b, s in ((1, -1), (2, 1)):
        back, step, front = s * BACK_X, s * STEP_X, s * FRONT_X
        for pid in (f'bent_{b}_0', f'bent_{b}_1', f'bent_{b}_closure'):
            body = original_mesh(pid)
            v = body.vertices
            if len(v) != 8 or not np.allclose(sorted(set(np.round(v[:, 0], 4))), sorted((round(back, 4), round(front, 4)))):
                raise ValueError(f'{pid}: unexpected original cap')
            bottom = v[:, 2].min()
            if not np.isclose(bottom, (926.21 - 910.80) * FT, atol=1e-4):
                raise ValueError(f'{pid}: unexpected cap bottom')
            ys = sorted(set(np.round(v[:, 1], 6)))
            tops = {}
            for y in ys:
                zs = sorted(set(np.round(v[np.isclose(v[:, 1], y, atol=1e-6), 2], 6)))
                if len(zs) != 2 or not 0.9 < zs[1] - zs[0] < 1.2:   # flat-topped box: no ledge yet
                    raise ValueError(f'{pid}: unexpected cap top (ledge already present?)')
                tops[y] = v[np.isclose(v[:, 1], y, atol=1e-6), 2].max()
            sections = []
            for y in ys:
                zt = tops[y]
                sections.append([(step, y, zt), (step, y, zt + LEDGE), (back, y, zt + LEDGE),
                                 (back, y, bottom), (front, y, bottom), (front, y, zt)])
            mesh = loft(sections)
            added = mesh.volume - body.volume
            if not np.isclose(added, 9 * IN * LEDGE * (ys[-1] - ys[0]), rtol=1e-4):
                raise ValueError(f'{pid}: unexpected ledge volume')
            store(pid, mesh, dict(ledge_width_in=9, ledge_height_above_seat_in=8),
                  'Approach-side 9 in pavement ledge, 8 in above the seat, added (sheets 21, 23, 24).',
                  '접속 슬래브 측 9 in 포장 받침턱(교좌면보다 8 in 높음)을 반영했습니다(도면 21·23·24).', [21, 23, 24])
            print(f'{pid}: ledge added, +{added:.4f} m3')
        # Bedding: the strip over the ledge rises with it; the seat strip is unchanged.
        pid = f'bent_{b}_bed'
        bed = original_mesh(pid)
        v, f = bed.vertices, bed.faces
        if len(v) != 12 or not bed.is_watertight:
            raise ValueError(f'{pid}: unexpected original bedding')
        end_a, end_b = v[:6], v[6:]                       # the two X ends, vertex i of one paired with i of the other
        if not (np.allclose(end_a[:, 0], end_a[0, 0]) and np.allclose(end_b[:, 0], end_b[0, 0])
                and np.allclose(end_a[:, 1], end_b[:, 1])
                and np.allclose(sorted((end_a[0, 0], end_b[0, 0])), sorted((back, front)), atol=1e-4)):
            raise ValueError(f'{pid}: unexpected bedding layout')
        if np.ptp(v[np.isclose(np.abs(v[:, 1]), DECK_EDGE, atol=1e-4), 2]) > 0.05:
            raise ValueError(f'{pid}: bedding already stepped')
        t = (step - end_a[0, 0]) / (end_b[0, 0] - end_a[0, 0])
        mid = end_a + t * (end_b - end_a)                 # the bedding is planar along X between its two ends
        first, second = np.vstack([end_a, mid]), np.vstack([mid, end_b])
        ledge_piece, seat_piece = (first, second) if np.isclose(end_a[0, 0], back, atol=1e-4) else (second, first)
        ledge_piece = ledge_piece + [0, 0, LEDGE]
        mesh = trimesh.Trimesh(vertices=np.vstack([ledge_piece, seat_piece]), faces=np.vstack([f, f + 12]), process=False)
        if mesh.volume < 0:
            mesh.invert()
        if not np.isclose(mesh.volume, bed.volume, rtol=1e-4):
            raise ValueError(f'{pid}: bedding volume changed')
        store(pid, mesh, dict(ledge_step_in=8),
              'The 9 in strip over the pavement ledge is raised 8 in with the ledge (sheets 23, 24).',
              '포장 받침턱 위 9 in 구간의 받침층을 받침턱과 함께 8 in 올렸습니다(도면 23·24).', [23, 24])

    # --- 2/4/5. Approach slab corner cutbacks, sleeper slab, approach railings ------------------------------
    for a, s in ((1, -1), (2, 1)):
        for side in (-1, 1):
            pid = f'approach_{a}_{1 if side == -1 else 6}'
            slab = original_mesh(pid)
            lo, hi = slab.bounds
            if not (np.isclose(abs(lo[0] if s == -1 else hi[0]), APPROACH_END_X, atol=1e-4)
                    and np.isclose(max(abs(lo[1]), abs(hi[1])), DECK_EDGE, atol=1e-4) and slab.is_watertight):
                raise ValueError(f'{pid}: unexpected approach panel')
            x0, x1 = sorted((s * CUT_X, s * (APPROACH_END_X + 1)))
            y0, y1 = sorted((side * TOE_Y, side * (DECK_EDGE + 1)))
            box = trimesh.creation.box(bounds=[[x0, y0, lo[2] - 1], [x1, y1, hi[2] + 1]])
            mesh = trimesh.boolean.difference([slab, box], engine='manifold')
            removed = slab.volume - mesh.volume
            if not np.isclose(removed, (APPROACH_END_X - CUT_X) * (DECK_EDGE - TOE_Y) * 12 * IN, rtol=2e-3):
                raise ValueError(f'{pid}: unexpected cutback volume {removed}')
            store(pid, mesh, dict(corner_cutback_ft=[round(49 / 12, 4), 1.5]),
                  'Outer corner cut back 4 ft 1 in x 1 ft 6 in at the sleeper-slab end (sheets 53-55).',
                  '슬리퍼 슬래브 쪽 바깥 모서리를 4 ft 1 in × 1 ft 6 in 절취했습니다(도면 53~55).', [53, 54, 55],
                  basis='Drawing dimensions', basis_ko='도면 치수')
            print(f'{pid}: corner cut back, -{removed:.4f} m3')
        pid = f'sleeper_{a}'
        sleeper = original_mesh(pid)
        v = sleeper.vertices.copy()
        edge = np.isclose(np.abs(v[:, 1]), DECK_EDGE, atol=1e-4)
        if edge.sum() != 16 or not np.allclose(v[~edge, 1], 0, atol=1e-6):
            raise ValueError(f'{pid}: unexpected sleeper slab')
        v[edge, 1] = np.sign(v[edge, 1]) * SLEEPER_HALF
        v[edge, 2] += 0.02 * (DECK_EDGE - SLEEPER_HALF)   # stay on the 2% crowned top and bottom planes
        mesh = trimesh.Trimesh(vertices=v, faces=sleeper.faces, process=False)
        store(pid, mesh, dict(length_ft=round(37 + 4 / 12, 4)),
              'Width corrected to 37 ft 4 in, flush with the approach slab cutbacks (sheets 53, 58).',
              '슬리퍼 슬래브 폭을 37 ft 4 in로 수정했습니다(도면 53·58).', [53, 58])
        for side in (-1, 1):
            pid = f'approach_rail_{a}_{side}'
            ov = original_mesh(pid).vertices
            check_old_rail(pid, ov, 1.5 * IN)
            xs = np.unique(np.round(np.abs(ov[:, 0]), 6))
            if not (np.isclose(xs[0], STEP_X, atol=1e-4) and np.isclose(xs[-1], APPROACH_END_X, atol=1e-4)):
                raise ValueError(f'{pid}: unexpected approach railing extent')
            stations = [JOINT_X] + [x for x in xs if JOINT_X + 0.05 < x < CUT_X - 0.05] + [CUT_X]
            mesh = rail_mesh([s * x for x in stations], side)
            store(pid, mesh, dict(length_ft=round((CUT_X - JOINT_X) / FT, 4), base_width_ft=round(16 / 12, 4),
                                  deck_edge_to_toe_ft=1.5, rear_setback_in=2, top_width_in=9, toe_height_in=3),
                  'Stands on the precast edge panel (no overlay under it), ends at the 4 ft 1 in corner cutback and '
                  '1/2 in short of the bridge railing at the neoprene expansion joint; FC section of sheets 51 and '
                  '53 (section A-A).',
                  '프리캐스트 가장자리 패널 위에 일체로 놓이고, 4 ft 1 in 모서리 절취부에서 끝나며 교량 난간과 '
                  '½ in 네오프렌 신축줄눈만큼 떨어집니다. 단면은 도면 51·53(단면 A-A)의 FC 형상입니다.', [51, 53, 55])
            print(f'{pid}: {stations[0]:.4f}..{stations[-1]:.4f} m, lowered to the slab top')

    # --- 3/5. Bridge railings and railing closure pours ---------------------------------------------------
    for span in (1, 2, 3):
        for side in (-1, 1):
            pid = f'rail_{span}_{side}'
            ov = original_mesh(pid).vertices
            check_old_rail(pid, ov, 0.0)
            mesh = rail_mesh(np.unique(np.round(ov[:, 0], 6)), side)
            store(pid, mesh, dict(base_width_ft=round(16 / 12, 4), deck_edge_to_toe_ft=1.5, rear_setback_in=2,
                                  top_width_in=9, toe_height_in=3),
                  'Section rebuilt to sheet 51: 2 in rear setback, 9 in top, 3 in toe.',
                  '도면 51 단면(후면 2 in 후퇴, 상단 폭 9 in, 하단 수직부 3 in)으로 재작성했습니다.', [51])
    for k, deck_pid in CLOSURES.items():
        dx = original_mesh(deck_pid).bounds[:, 0]
        width_in = 13 if k in (0, 3) else 12
        if not np.isclose(dx[1] - dx[0], width_in * IN, atol=1e-4):
            raise ValueError(f'{deck_pid}: unexpected deck closure width')
        for side in (-1, 1):
            pid = f'rail_closure_{k}_{side}'
            ov = original_mesh(pid).vertices
            check_old_rail(pid, ov, 0.0)
            ox = ov[:, 0].min(), ov[:, 0].max()
            if not np.isclose(ox[1] - ox[0], (width_in - 0.5) * IN, atol=1e-4):
                raise ValueError(f'{pid}: closure is not the expected {width_in} in less 1/2 in')
            mesh = rail_mesh(dx, side)
            store(pid, mesh, dict(length_in=width_in, base_width_ft=round(16 / 12, 4), deck_edge_to_toe_ft=1.5,
                                  rear_setback_in=2, top_width_in=9, toe_height_in=3),
                  f'UHPC railing closure pour filling the full {width_in} in over the deck closure pour, bonded to '
                  'both railing segments; FC section of sheet 51.' +
                  (' The 1/2 in neoprene expansion joint lies outside it, against the approach transition.'
                   if k in (0, 3) else ''),
                  f'데크 연결부 위 {width_in} in 전체를 채우고 양쪽 난간 부재와 일체로 타설되는 UHPC 난간 연결부입니다'
                  '(도면 51 FC 단면).' + (' ½ in 네오프렌 신축줄눈은 그 바깥, 접속 전이 난간 쪽에 있습니다.'
                                          if k in (0, 3) else ''), [51],
                  replace_note=True, basis='Drawing dimensions', basis_ko='도면 치수')
        print(f'rail closures {k}: {dx[0]:.4f}..{dx[1]:.4f} m')

    # --- 6. Support names (manifest only) ---------------------------------------------------------------
    renamed = {}
    for p in manifest['parts']:
        name = p.get('name', '')
        new = name.replace('Abutment 1 ', 'End Bent 1 ').replace('Abutment 2 ', 'End Bent 4 ')
        if p['id'] == 'transverse_closure_0':
            new = 'End Bent 1 transverse UHPC joint'
        elif p['id'] == 'transverse_closure_3':
            new = 'End Bent 4 transverse UHPC joint'
        if new != name:
            renamed[p['id']] = dict(before=name, after=new)
            p['name'] = new
    if len(renamed) != 14 or any('Abutment' in p.get('name', '') for p in manifest['parts']):
        raise ValueError('unexpected support names')

    while len(binary) % 4:
        binary.append(0)
    gltf['buffers'][0]['byteLength'] = len(binary)
    encoded = json.dumps(gltf, ensure_ascii=True, separators=(',', ':')).encode()
    encoded += b' ' * ((-len(encoded)) % 4)
    out = (struct.pack('<III', 0x46546c67, 2, 28 + len(encoded) + len(binary)) +
           struct.pack('<II', len(encoded), 0x4e4f534a) + encoded + struct.pack('<II', len(binary), 0x004e4942) + binary)
    backup = ROOT / 'data/fem_research'
    backup.mkdir(exist_ok=True)
    (backup / 'us52-mud_before_review_correction.glb').write_bytes(original)
    (backup / 'us52-mud_manifest_before_review_correction.json').write_bytes(mp.read_bytes())
    path.write_bytes(out)

    for item in manifest.get('detail_coverage', []):
        if item.get('feature') == 'Approach slabs and railings':
            item['detail'] = ('Each approach includes 6 panels and connections, with the 4 ft 1 in x 1 ft 6 in outer '
                              'corner cutbacks. FC railing sections follow sheet 51 (top corner radii omitted); the '
                              'TFC transitions use the FC section of sheet 53 section A-A, their curvature is omitted.')
            item['sources'] = sorted(set(item['sources']) | {51, 53, 54, 55, 58})
        elif item.get('feature') == 'Piers, abutments and wingwalls':
            item['detail'] = item['detail'].replace('segmented abutments', 'segmented end bents with the 9 in '
                                                                           'pavement ledge')
            item['sources'] = sorted(set(item['sources']) | {21, 24})
    manifest['review_correction'] = TAG
    manifest['revision'] = '1.1-drawing-review'
    manifest['review_correction_record'] = dict(
        source_pdf_pages=[21, 23, 24, 51, 53, 54, 55, 58], printed_sheets=[21, 23, 24, 51, 53, 54, 55, 58],
        corrections={
            'end_bent_pavement_ledge': '9 in ledge 8 in above the seat on the approach side of both end bents; '
                                       'bedding over the ledge raised with it',
            'approach_corner_cutbacks': '4 ft 1 in x 1 ft 6 in at the four outer corners; approach railings end at '
                                        'the cutback; sleeper slabs 37 ft 4 in wide',
            'fc_railing_section': '2 ft 9 in high, 2 in rear setback, 9 in top, 3 in toe (sheet 51); also used for '
                                  'the approach transitions (sheet 53 section A-A)',
            'approach_railing_base': 'lowered 1 1/2 in onto the precast edge panels',
            'railing_joints': 'closure pours fill 13 in / 12 in; 1/2 in neoprene joint outside the 91 ft 6 in '
                              'bridge railing, modelled as an open joint',
            'support_names': 'Abutment 1 / Abutment 2 renamed End Bent 1 / End Bent 4 (manifest names only)'},
        changed_parts=changed, renamed_parts=renamed,
        before_glb_sha256=before, after_glb_sha256=hashlib.sha256(out).hexdigest())
    deviations = [d for d in manifest.get('known_deviations', [])
                  if d.get('id') not in ('end-bent-absolute-elevation', 'wingwall-top-elevation',
                                         'railing-neoprene-joint')]
    deviations += [
        dict(id='end-bent-absolute-elevation', parts='bent_1_*, bent_2_*', source='sheets 21, 23 (PDF 21, 23)',
             deviation='Seat El. 929.48 at the edges and 929.89 at the centre (ledge 8 in higher) against plan '
                       'El. 929.21 / 929.61 (ledge 929.88 / 930.28); the bottom is at plan El. 926.21, so the cap is '
                       'about 3.3 in deeper than drawn.',
             reason='The draft plans conflict: the sheet 23 seat plus 1 in bed, 20 in slab and 1 1/2 in overlay gives '
                    'El. 931.485 at the bent, the sheet 21 profile El. 931.76. The model keeps the deck on the profile '
                    'and the cap bottom on sheet 23.'),
        dict(id='wingwall-top-elevation', parts='wing_*, wing_joint_*', source='sheets 23, 24, 53 (PDF 23, 24, 53)',
             deviation='Wingwall tops at El. 929.88 (3 ft 8 in high, sheets 23-24) are about 2.8-3.9 in below the '
                       'approach slab soffit less the 1 in UHPC bed of sheet 53 section A-A, and about 3.3 in below '
                       'the corrected end-bent ledge.',
             reason='Same datum conflict as end-bent-absolute-elevation; not resolved from the draft plans.'),
        dict(id='railing-neoprene-joint', parts='approach_rail_*, rail_closure_0_*, rail_closure_3_*',
             source='sheet 51 (PDF 51)',
             deviation='The 1/2 in neoprene expansion joint between the bridge railing and each approach transition '
                       'is an open 1/2 in gap; the filler is not a separate part.',
             reason='Joint filler, not a structural member.')]
    manifest['known_deviations'] = deviations
    mp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in manifest['review_correction_record'].items() if k != 'renamed_parts'}))


if __name__ == '__main__':
    correct()

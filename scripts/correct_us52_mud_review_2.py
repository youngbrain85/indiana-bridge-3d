"""Second drawing-confirmed correction of US 52 over Mud Creek (us52-mud); runs after correct_us52_mud_review.py.

    python scripts/correct_us52_mud_review.py      # first correction (revision 1.1)
    python scripts/correct_us52_mud_review_2.py    # this one (revision 1.2)

Source: drawings.pdf (2020-03-27 Stage 3 draft); the printed sheet numbers equal the PDF page numbers. Native axes:
X along the bridge (0 at sta. 458+17.00, +X = increasing station = east), Y across it (+Y = left of increasing station
= north: sheet 21 plan, north arrow and the westbound lane on the top side), Z up (0 = El. 910.80 ft), metres.

1. Approach railing transitions (sheets 53, 55; sheets 51 and 52 note 4 refer to standard E 706-TTFC-01 to -03).
   The approach slab plan (sheet 53, 3/8 in = 1 ft) draws the TFC transition over the edge panel 15 ft 8 in long from
   the end of the 91 ft 6 in bridge railing, ending 9 in before the 4 ft 1 in corner cutback; the Type IB module plan
   (sheet 55, 3/4 in = 1 ft) draws it 15 ft 8 in long, starting about 1/2 in (the neoprene joint of sheet 51) from the
   slab's bridge end. The first correction ran the transitions on to the cutback, 16 ft 4 1/2 in. They now run from
   the joint (|X| = 13.9573 m) for 15 ft 8 in to |X| = 18.7325 m, with the same sheet 51 / 53 A-A section.
   The roadway plan (sheet 9, item 1) gives the transition as sta. 457+58.08 to 457+71.25 and 458+62.75 to 458+75.92,
   13.17 ft; the structural detail sheets govern the precast element and the conflict is recorded.
2. Sleeper slabs (sheet 59 section B-B, sheet 53 plan, sheet 58). The 6 ft sleeper slab carries a 2 ft concrete lug at
   its outer end; the 20 ft 6 in approach slab ends 2 1/2 in (pre-compressed foam joint) short of the lug, so the slab
   bears on the inner 3 ft 9 1/2 in of the sleeper. The sheet 53 plan scales the same (sleeper 16 ft 8 1/2 in to
   22 ft 8 1/2 in from the ledge face). The model had the sleeper centred on the approach slab end (3 ft under it,
   3 ft beyond), 9 1/2 in too far out. Both sleepers move 0.2413 m toward the bridge, to |X| = 19.0373..20.8661 m,
   and each vertex is regraded on the 135 ft vertical curve (dz = (x_old^2 - x_new^2) / (27000 ft)) so the top stays
   on the approach slab soffit. The lug step stays simplified as before.
3. End Bent 4 module labels (sheet 23). The Bent No. 1 plan has wingwalls (west) at the top and the north arrow to
   the right, so module IA is on the south side (-Y) and IB on the north side (+Y); the model's End Bent 1 labels
   agree. Bent No. 4 is "same by 180 deg rotation", which puts IA on the north (+Y) and IB on the south (-Y). The
   model labelled bent_2_0 (-Y) "module A" and bent_2_1 (+Y) "module B"; the labels are swapped (manifest names and
   the A/B letter of the GLB extras names). Geometry and part ids are unchanged.

Deferred and recorded in known_deviations: the barrier delineators (sheet 51 shows them on the upper front face; the
mounting position is not dimensioned) and the sheet 9 / sheets 53, 55 transition-length conflict.

Requires numpy and trimesh, and correct_us52_mud_review.py (same folder) for the railing section.
"""
import hashlib
import json
import struct
import sys
from pathlib import Path

import numpy as np
import trimesh

sys.path.insert(0, str(Path(__file__).resolve().parent))
from correct_us52_mud_review import (BASE, CUT_X, FT, IN, JOINT_X, ROOT, SLEEPER_HALF, STEP_X,  # noqa: E402
                                     TAG as FIRST_TAG, APPROACH_END_X, rail_mesh)

TAG = 'tfc-transition-length-sleeper-position-bent4-labels'
REVISION_BEFORE = '1.1-drawing-review'
REVISION = '1.2-drawing-review-2'

TRANSITION = (15 + 8 / 12) * FT                    # 15 ft 8 in TFC transition, sheets 53 and 55
TRANSITION_END_X = JOINT_X + TRANSITION            # 18.7325 m
SLEEPER_W = 6 * FT                                 # 6 ft sleeper slab, sheets 53, 58, 59
LUG_W = 2 * FT                                     # 2 ft concrete lug, sheets 58, 59
SLEEPER_JOINT = 2.5 * IN                           # 2 1/2 in pre-compressed foam joint, sheet 59
SLEEPER_OUT_X = APPROACH_END_X + SLEEPER_JOINT + LUG_W      # 20.8661 m
SLEEPER_IN_X = SLEEPER_OUT_X - SLEEPER_W                    # 19.0373 m
OLD_SLEEPER_X = [19.2786, 19.8882, 20.4978, 21.1074]        # model stations before this correction
VC = 27000 * FT                                    # 135 ft vertical curve: z = z0 - x^2 / VC (x in m)

OLD_RAIL_NOTE = 'ends at the 4 ft 1 in corner cutback and 1/2 in short of the bridge railing at the neoprene expansion joint'
NEW_RAIL_NOTE = ('starts 1/2 in short of the bridge railing at the neoprene expansion joint and is 15 ft 8 in long, '
                 'ending 9 in short of the 4 ft 1 in corner cutback (sheets 53, 55)')
OLD_RAIL_NOTE_KO = '4 ft 1 in 모서리 절취부에서 끝나며 교량 난간과 ½ in 네오프렌 신축줄눈만큼 떨어집니다.'
NEW_RAIL_NOTE_KO = ('교량 난간과 ½ in 네오프렌 신축줄눈만큼 떨어져 시작하고, 길이 15 ft 8 in로 4 ft 1 in 모서리 절취부보다 '
                    '9 in 앞에서 끝납니다(도면 53·55).')

LABELS = {'bent_2_0': ('End Bent 4 module A', 'End Bent 4 module B', '교대 2 모듈 A', '교대 2 모듈 B', -1),
          'bent_2_1': ('End Bent 4 module B', 'End Bent 4 module A', '교대 2 모듈 B', '교대 2 모듈 A', 1)}


def correct():
    mp = BASE / 'model_manifest.json'
    manifest = json.loads(mp.read_text(encoding='utf-8'))
    if manifest.get('review_correction_2') == TAG:
        print('Already corrected.')
        return
    if manifest.get('review_correction') != FIRST_TAG or manifest.get('revision') != REVISION_BEFORE:
        raise ValueError('run scripts/correct_us52_mud_review.py first (revision 1.1 expected)')
    path = BASE / 'model.glb'
    original = path.read_bytes()
    length = struct.unpack_from('<I', original, 12)[0]
    gltf = json.loads(original[20:20 + length])
    binary = bytearray(original[28 + length:])
    before = hashlib.sha256(original).hexdigest()
    parts = {p['id']: p for p in manifest['parts']}
    meshes = {m['name']: m for m in gltf['meshes']}
    changed = []

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

    def store(pid, mesh, dims, note, note_ko, pages):
        """New positions for an unchanged topology; indices and colours are kept."""
        prim = meshes[pid]['primitives'][0]
        if not mesh.is_watertight or not mesh.is_winding_consistent or mesh.volume <= 0:
            raise ValueError(f'{pid}: corrected mesh is not a valid solid')
        if not np.array_equal(mesh.faces, read(prim['indices']).reshape(-1, 3)):
            raise ValueError(f'{pid}: topology changed unexpectedly')
        prim['attributes']['POSITION'] = append(mesh.vertices.astype('<f4'), 'VEC3', 5126)
        p = parts[pid]
        p['bounds_m'] = mesh.bounds.round(6).tolist()
        p['volume_m3'] = round(float(mesh.volume), 6)
        p['dimensions'].update(dims)
        p['pdf_pages'] = sorted(set(p.get('pdf_pages', [])) | set(pages))
        p['note'] = note
        extras = meshes[pid]['extras']
        extras.update(bounds_m=p['bounds_m'], volume_m3=p['volume_m3'], dimensions=p['dimensions'],
                      pdf_pages=p['pdf_pages'], note=note_ko)
        changed.append(pid)

    # --- 1. Approach railing transitions: 15 ft 8 in from the neoprene joint -------------------------------------
    for a, s in ((1, -1), (2, 1)):
        for side in (-1, 1):
            pid = f'approach_rail_{a}_{side}'
            old = current_mesh(pid)
            xs = np.unique(np.round(np.abs(old.vertices[:, 0]), 6))
            if not (len(old.vertices) == 36 and np.isclose(xs[0], JOINT_X, atol=1e-4)
                    and np.isclose(xs[-1], CUT_X, atol=1e-4)):
                raise ValueError(f'{pid}: unexpected approach railing extent')
            redo = rail_mesh([s * x for x in xs], side)            # the first correction's section and stations
            if not np.allclose(redo.vertices, old.vertices, atol=2e-5):
                raise ValueError(f'{pid}: railing is not the expected sheet 51 / 53 A-A section')
            stations = [x for x in xs if x < TRANSITION_END_X - 0.05] + [TRANSITION_END_X]
            mesh = rail_mesh([s * x for x in stations], side)
            p = parts[pid]
            note_ko = meshes[pid]['extras'].get('note', '')
            if OLD_RAIL_NOTE not in p['note'] or OLD_RAIL_NOTE_KO not in note_ko:
                raise ValueError(f'{pid}: unexpected railing note')
            store(pid, mesh, dict(length_ft=round(TRANSITION / FT, 4)),
                  p['note'].replace(OLD_RAIL_NOTE, NEW_RAIL_NOTE), note_ko.replace(OLD_RAIL_NOTE_KO, NEW_RAIL_NOTE_KO),
                  [53, 55])
            print(f'{pid}: |X| {xs[0]:.4f}..{xs[-1]:.4f} -> {stations[0]:.4f}..{stations[-1]:.4f} m, '
                  f'{old.volume:.4f} -> {mesh.volume:.4f} m3')

    # --- 2. Sleeper slabs: 2 ft lug beyond the 2 1/2 in joint, 3 ft 9 1/2 in under the approach slab --------------
    new_x = [SLEEPER_IN_X + k * 2 * FT for k in range(4)]
    for a, s in ((1, -1), (2, 1)):
        pid = f'sleeper_{a}'
        old = current_mesh(pid)
        v = old.vertices.copy()
        xs = np.unique(np.round(np.abs(v[:, 0]), 4))
        if not (len(v) == 24 and np.allclose(xs, OLD_SLEEPER_X, atol=1e-4)
                and np.isclose(np.abs(v[:, 1]).max(), SLEEPER_HALF, atol=1e-5)):
            raise ValueError(f'{pid}: unexpected sleeper slab position')
        for x_old, x_new in zip(OLD_SLEEPER_X, new_x):
            at = np.isclose(np.abs(v[:, 0]), x_old, atol=1e-4)
            v[at, 2] += (x_old ** 2 - x_new ** 2) / VC                # stay on the vertical curve
            v[at, 0] = s * x_new
        mesh = trimesh.Trimesh(vertices=v, faces=old.faces, process=False)
        p = parts[pid]
        store(pid, mesh, dict(width_ft=6, lug_width_ft=2, joint_to_lug_in=2.5, under_approach_slab_in=45.5),
              p['note'] + ' Moved 9 1/2 in toward the bridge: the approach slab bears on the inner 3 ft 9 1/2 in and '
              'the 2 ft lug lies beyond the 2 1/2 in joint at the slab end (sheet 59 section B-B, sheet 53 plan); the '
              'lug step itself is not modelled.',
              meshes[pid]['extras'].get('note', '') + ' 교량 쪽으로 9 1/2 in 옮겼습니다. 접속 슬래브가 안쪽 3 ft 9 1/2 in에 '
              '얹히고 2 ft 러그는 슬래브 끝 2 1/2 in 줄눈 바깥에 있습니다(도면 59 단면 B-B, 도면 53 평면). 러그 단차는 '
              '모델링하지 않았습니다.', [53, 58, 59])
        print(f'{pid}: |X| {xs[0]:.4f}..{xs[-1]:.4f} -> {new_x[0]:.4f}..{new_x[-1]:.4f} m')

    # --- 3. End Bent 4 module labels (Bent 1 rotated 180 deg) ---------------------------------------------------
    renamed = {}
    if not (parts['bent_1_0']['name'] == 'End Bent 1 module A' and np.mean(parts['bent_1_0']['bounds_m'], axis=0)[1] < 0
            and parts['bent_1_1']['name'] == 'End Bent 1 module B'):
        raise ValueError('unexpected End Bent 1 labels')
    for pid, (old_name, new_name, old_ko, new_ko, ysign) in LABELS.items():
        p, extras = parts[pid], meshes[pid]['extras']
        if p['name'] != old_name or extras.get('name') != old_ko or np.sign(np.mean(p['bounds_m'], axis=0)[1]) != ysign:
            raise ValueError(f'{pid}: unexpected label or side')
        p['name'], extras['name'] = new_name, new_ko
        renamed[pid] = dict(before=old_name, after=new_name, before_ko=old_ko, after_ko=new_ko)

    # --- Write --------------------------------------------------------------------------------------------------
    while len(binary) % 4:
        binary.append(0)
    gltf['buffers'][0]['byteLength'] = len(binary)
    encoded = json.dumps(gltf, ensure_ascii=True, separators=(',', ':')).encode()
    encoded += b' ' * ((-len(encoded)) % 4)
    out = (struct.pack('<III', 0x46546c67, 2, 28 + len(encoded) + len(binary)) +
           struct.pack('<II', len(encoded), 0x4e4f534a) + encoded + struct.pack('<II', len(binary), 0x004e4942) + binary)

    # Overall bounds: recompute from the parts, keeping the stored value of every component that did not move.
    lo = np.array([p['bounds_m'][0] for p in manifest['parts']]).min(axis=0)
    hi = np.array([p['bounds_m'][1] for p in manifest['parts']]).max(axis=0)
    old_lo, old_hi = (np.array(b, dtype=float) for b in manifest['bounds_m'])
    lo = np.where(np.isclose(lo, old_lo, atol=1e-5), old_lo, lo)
    hi = np.where(np.isclose(hi, old_hi, atol=1e-5), old_hi, hi)
    manifest['bounds_m'] = [lo.tolist(), hi.tolist()]
    manifest['glb_bounds_m'] = [[lo[0], lo[2], -hi[1]], [hi[0], hi[2], -lo[1]]]
    for item in manifest.get('detail_coverage', []):
        if item.get('feature') == 'Approach slabs and railings':
            item['detail'] = ('Each approach includes 6 panels and connections, with the 4 ft 1 in x 1 ft 6 in outer '
                              'corner cutbacks. FC railing sections follow sheet 51 (top corner radii omitted); the '
                              'TFC transitions are 15 ft 8 in long (sheets 53, 55) and use the FC section of sheet 53 '
                              'section A-A, their curvature is omitted. The 6 ft sleeper slabs sit as in sheet 59 '
                              'section B-B; their 2 ft lug step is simplified.')
            item['sources'] = sorted(set(item['sources']) | {59})
    manifest['review_correction_2'] = TAG
    manifest['revision'] = REVISION
    manifest['review_correction_2_record'] = dict(
        source_pdf_pages=[9, 21, 23, 51, 52, 53, 55, 58, 59], printed_sheets=[9, 21, 23, 51, 52, 53, 55, 58, 59],
        corrections={
            'tfc_transition_length': '15 ft 8 in from the 1/2 in neoprene joint (|X| 13.9573..18.7325 m), ending 9 in '
                                     'short of the corner cutback (sheets 53, 55); was 16 ft 4 1/2 in to the cutback',
            'sleeper_slab_position': '6 ft sleeper with the 2 ft lug beyond the 2 1/2 in joint at the approach slab '
                                     'end: |X| 19.0373..20.8661 m (sheet 59 section B-B, sheet 53 plan); was '
                                     '19.2786..21.1074 m',
            'end_bent_4_module_labels': 'Bent 4 = Bent 1 rotated 180 deg (sheet 23): module A on the north (+Y) side, '
                                        'module B on the south (-Y) side; labels only'},
        changed_parts=changed, renamed_parts=renamed,
        before_glb_sha256=before, after_glb_sha256=hashlib.sha256(out).hexdigest())
    deviations = [d for d in manifest.get('known_deviations', [])
                  if d.get('id') not in ('tfc-transition-length-sheet-9', 'railing-delineator-position')]
    deviations += [
        dict(id='tfc-transition-length-sheet-9', parts='approach_rail_*', source='sheets 9, 53, 55 (PDF 9, 53, 55)',
             deviation='The TFC transitions are 15 ft 8 in long as drawn on sheets 53 and 55; the sheet 9 roadway plan '
                       '(item 1) gives sta. 457+58.08 to 457+71.25 and 458+62.75 to 458+75.92, 13.17 ft.',
             reason='The draft plans conflict; the structural detail sheets of the precast edge panel are followed.'),
        dict(id='railing-delineator-position', parts='delineator_*',
             source='sheet 51 (PDF 51), sections A-A and B-B',
             deviation='The six barrier delineators sit across the railing top, mostly embedded in it; sheet 51 draws '
                       'them on the upper front (traffic) face.',
             reason='Visualisation markers; their size and mounting height are not dimensioned on the drawings.')]
    manifest['known_deviations'] = deviations

    backup = ROOT / 'data/fem_research'
    backup.mkdir(exist_ok=True)
    (backup / 'us52-mud_before_review_correction_2.glb').write_bytes(original)
    (backup / 'us52-mud_manifest_before_review_correction_2.json').write_bytes(mp.read_bytes())
    path.write_bytes(out)
    mp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in manifest['review_correction_2_record'].items() if k != 'renamed_parts'}))


if __name__ == '__main__':
    correct()

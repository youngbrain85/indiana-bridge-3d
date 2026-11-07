"""Second drawing-confirmed correction (runs after correct_sr1_six_mile_review.py): square approach-slab far ends,
preserving unrelated GLB buffers.

    python scripts/correct_sr1_six_mile_review_2.py

Drawing evidence (contract B-44532, drawings.pdf; printed sheet numbers equal PDF page numbers):

- Sheet 7, plan: each RCBA polymer-overlay hatch ends in a line square to S.R. 1 (drawn within 0.5 deg of 90 deg to
  the roadway edges). The 20.5' and 36.5' RCBA dimensions run along the hatch edges, which the 10' + 12' dimensions
  place 22 ft either side of S.R. 1, i.e. along the edges of the 44 ft roadway. The two lengths close on the skewed
  bridge end: 36.5 - 20.5 = 16 ft = 44 ft x tan 20 deg (16.01 ft). The same plan is dimensioned 20.5' at the top
  left and bottom right, as in the model, so the model is not mirrored.
- Sheet 8, quantities: 279 SYS polymer overlay on the approaches = 2 x 44 ft x 28.5 ft / 9 (278.7), 28.5 ft being
  the mean of the 20.5 and 36.5 ft edges, i.e. the length on the S.R. 1 line.

The original build (build_sr1_six_mile.py) spread the 16 ft difference across the full 47'-1 1/2" deck width, so
the far ends were 1.40 deg off square, the 20.5/36.5 ft lengths fell on the deck edges and the roadway-edge lengths
were 21.03/35.97 ft. Here every far-end vertex of approach_0 / approach_1 moves along X to X = -/+(deck half length
+ 28.5 ft) = -/+19.751675 m; Y, Z and the bridge-end vertices are unchanged. The roadway-edge lengths become
20.493 and 36.507 ft (20.5 and 36.5 ft to the drawing's precision); the largest move is 0.17558 m at the deck-edge
corners. The slab volume is unchanged (the length on the centreline is unchanged and the far end stays straight).

Not changed (recorded in known_deviations): the approach polymer overlay has no thickness on any sheet and the
model shows one colour per closed part, so it stays a note; the joint-seal envelopes (minor second-review item)
still span the full deck width.

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
BID = 'sr1-six-mile'
BASE = ROOT / 'data/bridges' / BID
TAG = 'approach-far-ends-square-to-sr1'
REVISION = '1.2-approach-far-ends-square'
PREVIOUS_TAG = 'clear-roadway-44ft-overlay-limits'      # correct_sr1_six_mile_review.py
PREVIOUS_REVISION = '1.1-clear-roadway-overlay-limits'

LENGTH = (72 + 7.25 / 12) * FT            # sheet 4, out to out (as built by build_sr1_six_mile.py)
WIDTH = (47 + 1.5 / 12) * FT              # sheets 4 and 7, out to out of copings
SKEW, CROSSFALL, GRADE = 20, .0156, 6.0   # model skew (NBI), sheet 7 crossfall, assumed local elevation
APPROACH_T = .3                           # assumed slab thickness of the original build
SHORT, LONG = 20.5 * FT, 36.5 * FT        # sheet 7 RCBA lengths along the roadway edges
MEAN = (SHORT + LONG) / 2                 # 28.5 ft on the S.R. 1 line (sheet 8: 279 SYS = 2 x 44 x 28.5 / 9)
ROADWAY_HALF = 22 * FT                    # sheet 7: 10 + 12 ft each side, 44 ft clear roadway
FAR_X = LENGTH / 2 + MEAN                 # 19.751675 m
APPROACHES = (('approach_0', -1), ('approach_1', 1))
TOL = 2e-5


def to_native(v):
    """glTF Y-up vertices (as stored, no node matrix) -> native X station, Y transverse, Z up."""
    return np.column_stack([v[:, 0], -v[:, 2], v[:, 1]])


def to_gltf(v):
    return np.column_stack([v[:, 0], v[:, 2], -v[:, 1]])


def correct():
    mp = BASE / 'model_manifest.json'
    raw_manifest = mp.read_bytes()
    manifest = json.loads(raw_manifest)
    if manifest.get('approach_end_correction') == TAG:
        print('Already corrected.')
        return
    if manifest.get('clear_roadway_correction') != PREVIOUS_TAG or manifest.get('revision') != PREVIOUS_REVISION:
        raise ValueError('Run scripts/correct_sr1_six_mile_review.py first (expected revision '
                         f'{PREVIOUS_REVISION}, found {manifest.get("revision")}).')
    path = BASE / 'model.glb'
    original = path.read_bytes()
    length = struct.unpack_from('<I', original, 12)[0]
    gltf = json.loads(original[20:20 + length])
    binary = bytearray(original[28 + length:])
    before = hashlib.sha256(original).hexdigest()
    parts = {p['id']: p for p in manifest['parts']}
    meshes = {m['name']: m for m in gltf['meshes']}
    if any('matrix' in n or 'rotation' in n or 'translation' in n or 'scale' in n for n in gltf['nodes']):
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

    k = -np.tan(np.radians(SKEW))           # station u = X - k*Y, as in bridge_geometry.Model.sx

    def surface(y):
        return GRADE - CROSSFALL * np.abs(y)

    changes, values = [], {}
    for pid, e in APPROACHES:
        prim = meshes[pid]['primitives'][0]
        stored = to_native(read(prim['attributes']['POSITION']).astype(np.float64))
        faces = read(prim['indices']).reshape(-1, 3)
        old = trimesh.Trimesh(vertices=stored, faces=faces, process=False)
        y, z = stored[:, 1], stored[:, 2]
        near_x = e * LENGTH / 2 + k * y                                     # skewed bridge end line
        old_far_x = near_x + e * (MEAN + e * 8 * FT * (2 * y / WIDTH))     # original build: 28.5 +/- 8 ft at deck edges
        near = np.abs(stored[:, 0] - near_x) < TOL
        far = np.abs(stored[:, 0] - old_far_x) < TOL
        dz = z - surface(y)
        if (not old.is_watertight or near.sum() != 5 or far.sum() != 5 or (near & far).any()
                or not np.allclose(np.sort(np.unique(np.round(y, 5))), [-WIDTH / 2, 0, WIDTH / 2], atol=TOL)
                or not np.all((np.abs(dz) < TOL) | (np.abs(dz + APPROACH_T) < TOL))):
            raise ValueError(f'{pid}: unexpected original approach geometry')
        # Rebuild the vertices exactly (float64) from the verified original layout, then square the far end.
        ye = np.where(np.abs(y) < TOL, 0.0, np.sign(y) * WIDTH / 2)
        exact = np.column_stack([np.where(near, e * LENGTH / 2 + k * ye, e * FAR_X), ye,
                                 surface(ye) + np.where(dz < -APPROACH_T / 2, -APPROACH_T, 0.0)])
        new = trimesh.Trimesh(vertices=exact, faces=faces, process=False)
        if not new.is_watertight or not new.is_winding_consistent or new.volume <= 0:
            raise ValueError(f'{pid}: invalid squared approach')
        move = np.abs(exact[:, 0] - stored[:, 0]).max()

        def edge_length(yy):
            return abs(e * FAR_X - (e * LENGTH / 2 + k * yy))

        road = sorted([edge_length(-ROADWAY_HALF), edge_length(ROADWAY_HALF)])
        deck = sorted([edge_length(-WIDTH / 2), edge_length(WIDTH / 2)])
        if abs(road[0] - SHORT) > .005 * FT * 2 or abs(road[1] - LONG) > .005 * FT * 2 or abs(move - .17558) > 1e-4:
            raise ValueError(f'{pid}: squared far end does not reproduce the 20.5/36.5 ft roadway-edge lengths')
        prim['attributes']['POSITION'] = append(to_gltf(exact).astype('<f4'), 'VEC3', 5126)
        p = parts[pid]
        old_bounds, old_volume = p['bounds_m'], p['volume_m3']
        p['bounds_m'] = new.bounds.round(6).tolist()
        p['volume_m3'] = round(float(new.volume), 9)
        p['pdf_pages'] = sorted(set(p['pdf_pages']) | {7, 8})
        p['dimensions'].update(
            edge_lengths_ft=[20.5, 36.5], edge_lengths_measured_on='44 ft roadway edges, 22 ft from S.R. 1 (sheet 7)',
            roadway_edge_lengths_m=[round(r, 6) for r in road], deck_edge_lengths_m=[round(d, 6) for d in deck],
            centreline_length_ft=28.5, far_end='square to S.R. 1', far_end_x_m=round(e * FAR_X, 6))
        p['note'] = (p.get('note', '') + ' Far end squared to S.R. 1, 28.5 ft from the bridge end on the S.R. 1 line, so '
                     'that the 20.5 ft and 36.5 ft lengths fall on the 44 ft roadway edges as dimensioned on sheet 7 '
                     '(was 1.40 deg off square with those lengths at the deck edges).').strip()
        meshes[pid]['extras'].update(p)
        changes.append(pid)
        values[pid] = dict(
            far_end=f'X = {e * FAR_X:+.6f} m, square to S.R. 1; was X = {e * FAR_X:+.6f} {k + 16 * FT / WIDTH:+.9f} Y '
                    f'({np.degrees(np.arctan(abs(k + 16 * FT / WIDTH))):.2f} deg off square)',
            roadway_edge_lengths_ft=f'{road[0] / FT:.3f} / {road[1] / FT:.3f}; was 21.031 / 35.969',
            deck_edge_lengths_ft=f'{deck[0] / FT:.3f} / {deck[1] / FT:.3f}; was 20.500 / 36.500',
            max_vertex_move_m=round(float(move), 6), bounds_before=old_bounds, bounds_after=p['bounds_m'],
            volume_m3=f'{old_volume} -> {p["volume_m3"]}')
        print(f'{pid}: far end X={e * FAR_X:+.6f}, roadway edges {road[0] / FT:.3f}/{road[1] / FT:.3f} ft, '
              f'deck edges {deck[0] / FT:.3f}/{deck[1] / FT:.3f} ft, max move {move:.5f} m, '
              f'volume {old.volume:.6f} -> {new.volume:.6f} m3')

    for d in manifest.get('detail_coverage', []):
        if d.get('feature') == 'Drawing envelope and proposed overlay':
            d['detail'] = (d['detail'] + ' Approach far ends are square to S.R. 1, with the 20.5/36.5 ft lengths on the '
                           '44 ft roadway edges (sheet 7 plan).')
    deviations = manifest.setdefault('known_deviations', [])
    known = {d.get('id') for d in deviations}
    for entry in (
            dict(id='approach-polymer-overlay', parts='approach_0, approach_1', source='sheets 3, 7 and 8 (PDF 3, 7, 8)',
                 deviation='The non-warranted polymer overlay on both RCBAs (44 ft roadway, 279 SYS for both) is '
                           'recorded in the approach notes and dimensions only; it is not shown as a layer or as a '
                           'separate finish on the approach top faces.',
                 reason='No sheet gives its thickness, and each part is one closed solid shown in one manifest colour '
                        '(the viewer ignores vertex colours and needs one mesh per part), so a face-level finish '
                        'would need a new part of invented thickness.'),
            dict(id='joint-seal-length', parts='joint_0, joint_1', source='sheet 7 plan, sheet 8 (PDF 7, 8)',
                 deviation='Each 30 mm seal envelope spans the full 47 ft 1 1/2 in deck (Y = +/-7.18185 m, 50.15 ft '
                           'along the skew) and passes under the barrier ends; sheet 7 dimensions each joint 47 ft '
                           'along the skew across the 44 ft roadway hatch (44 ft / cos 20 deg = 46.8 ft) and sheet 8 '
                           'gives 94 lft for both.',
                 reason='Minor item of the second review, outside the scope of revision 1.2; trimming each seal to '
                        '|Y| <= 6.7056 m is left for a later correction.')):
        if entry['id'] not in known:
            deviations.append(entry)

    gltf['buffers'][0]['byteLength'] = len(binary)
    while len(binary) % 4:
        binary.append(0)
    encoded = json.dumps(gltf, ensure_ascii=True, separators=(',', ':')).encode()
    encoded += b' ' * ((-len(encoded)) % 4)
    out = (struct.pack('<III', 0x46546c67, 2, 28 + len(encoded) + len(binary)) +
           struct.pack('<II', len(encoded), 0x4e4f534a) + encoded + struct.pack('<II', len(binary), 0x004e4942) + binary)
    backup = ROOT / 'data/fem_research'
    backup.mkdir(exist_ok=True)
    (backup / f'{BID}_before_review_correction_2.glb').write_bytes(original)
    (backup / f'{BID}_manifest_before_review_correction_2.json').write_bytes(raw_manifest)
    path.write_bytes(out)
    manifest['approach_end_correction'] = TAG
    manifest['revision'] = REVISION
    manifest['approach_end_correction_record'] = dict(
        source_pdf_pages=[7, 8], printed_sheets=[7, 8], previous_revision=PREVIOUS_REVISION, changed_parts=changes,
        values=dict(values, basis='sheet 7 plan: RCBA far ends square to S.R. 1, 20.5/36.5 ft along the 44 ft roadway '
                                  'edges (36.5 - 20.5 = 16 ft = 44 ft x tan 20 deg); sheet 8: 279 SYS = '
                                  '2 x 44 x 28.5 / 9'),
        deferred=['approach polymer overlay (known_deviations: approach-polymer-overlay)',
                  'joint seal length (known_deviations: joint-seal-length)'],
        before_glb_sha256=before, after_glb_sha256=hashlib.sha256(out).hexdigest())
    text = json.dumps(manifest, indent=2)
    if b'\r\n' in raw_manifest:
        text = text.replace('\n', '\r\n')
    if raw_manifest.endswith(b'\n'):
        text += '\r\n' if b'\r\n' in raw_manifest else '\n'
    mp.write_bytes(text.encode('utf-8'))
    print(json.dumps(manifest['approach_end_correction_record']))


if __name__ == '__main__':
    correct()

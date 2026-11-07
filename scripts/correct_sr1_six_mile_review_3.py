"""Third drawing-confirmed correction (runs after correct_sr1_six_mile_review_2.py): resolve the known deviations,
preserving unrelated GLB buffers.

    python scripts/correct_sr1_six_mile_review_3.py

Drawing evidence (contract B-44532, drawings.pdf; printed sheet numbers equal PDF page numbers):

- joint-seal-length, RESOLVED. Sheet 7 plan: each "Clean & install New Silicone Sealant in Exist. Type 1-A Joints
  (Joint in PCCP, Filled)" line runs from one edge of the 44 ft roadway hatch to the other (the 10' + 12' dimensions
  put those edges 22 ft either side of S.R. 1). Its "47'" dimension has extension lines at the hatch edges; the
  drawn lines measure 46.8 / 47.1 ft along the skew and 44.0 ft square to S.R. 1 at the plan's 72 ft scale.
  44 ft / cos 20 deg = 46.82 ft. Sheet 8: "Joints in PCCP, Filled" 94 lft = 2 x 47 ft. The model's 30 mm seal
  envelopes spanned the full 47'-1 1/2" deck (50.15 ft along the skew) and ran 1 mm into the barrier bases. Each seal
  is rebuilt with the same station range, 25 mm depth, 1 mm proud top, crown and crossfall, but between the barrier
  toes, |Y| <= 22 ft = 6.7056 m (the round-1 toe line, sheets 4 and 7). Length along the skew 14.2719 m = 46.82 ft.
- approach-polymer-overlay, KEPT. Sheets 3, 7 and 8 fix its plan extent, but no sheet gives the thickness of the
  non-warranted polymer; the 3/8 in of sheet 3 is for the warranted deck overlay only. The known_deviations reason
  is rewritten to say exactly that and what source would settle it. No geometry is added.

Only joint_0 and joint_1 change. Their 12-vertex layout and the shared index and colour accessors are kept; one new
POSITION accessor is appended per joint. All other meshes, accessors and the original binary chunk are kept byte
for byte. No parts are added or removed.

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
TAG_KEY = 'review_correction_3'
TAG = 'known-deviations-joint-seals-44ft-roadway'
REVISION = '1.3-deviations'
PREVIOUS_TAG = 'approach-far-ends-square-to-sr1'        # correct_sr1_six_mile_review_2.py
PREVIOUS_REVISION = '1.2-approach-far-ends-square'
EXPECTED_GLB_SHA256 = 'e73cf93a482cc3f0f8a67ecbefd0941100d56078c5c2b253548bf63058b2effe'

LENGTH = (72 + 7.25 / 12) * FT            # sheet 4, out to out (as built by build_sr1_six_mile.py)
WIDTH = (47 + 1.5 / 12) * FT              # sheets 4 and 7, out to out of copings
SKEW, CROSSFALL, GRADE = 20, .0156, 6.0   # model skew (NBI), sheet 7 crossfall, assumed local elevation
ROADWAY_HALF = 22 * FT                    # sheet 7: 10 + 12 ft each side of S.R. 1, 44 ft clear roadway (= barrier toe)
SEAL_HALF_WIDTH = .015                    # existing 30 mm display width (build_sr1_six_mile.py), unchanged
SEAL_TOP, SEAL_BOTTOM = .001, -.024       # existing display envelope: 1 mm proud, 25 mm deep, unchanged
DRAWN_LENGTH_FT, QUANTITY_LFT = 47, 94    # sheet 7 joint dimension; sheet 8 "Joints in PCCP, Filled"
JOINTS = (('joint_0', -1), ('joint_1', 1))
TOL = 2e-5


def to_native(v):
    """glTF Y-up vertices (as stored, no node matrix) -> native X station, Y transverse, Z up."""
    return np.column_stack([v[:, 0], -v[:, 2], v[:, 1]])


def to_gltf(v):
    return np.column_stack([v[:, 0], v[:, 2], -v[:, 1]])


APPROACH_REASON = (
    'Only the thickness is missing. Sheets 3, 7 and 8 fix the plan extent: the 44 ft roadway between the hatch edges '
    '22 ft either side of S.R. 1, 20.5 ft and 36.5 ft along those edges, the far end square to S.R. 1, and 279 SYS for '
    'both approaches (2 x 44 x 28.5 / 9). No sheet gives the thickness or application rate of the non-warranted '
    'polymer: the 3/8 in in general note 2 (sheet 3) applies to the warranted thin deck overlay only, and the sheet 7 '
    'typical section covers the deck only. The viewer shows one manifest colour per closed part and ignores vertex '
    'colours, so a visible finish needs its own part, which would need an invented thickness. Settled by the contract '
    'special provision or pay-item specification for "Polymer Overlay, Bridge Deck Approaches" (proposal book for '
    'contract B-44532) or a revised sheet that states the approach overlay thickness.')


def correct():
    mp = BASE / 'model_manifest.json'
    raw_manifest = mp.read_bytes()
    manifest = json.loads(raw_manifest)
    if manifest.get(TAG_KEY) == TAG:
        print('Already corrected.')
        return
    if manifest.get('approach_end_correction') != PREVIOUS_TAG or manifest.get('revision') != PREVIOUS_REVISION:
        raise ValueError('Run scripts/correct_sr1_six_mile_review_2.py first (expected revision '
                         f'{PREVIOUS_REVISION}, found {manifest.get("revision")}).')
    path = BASE / 'model.glb'
    original = path.read_bytes()
    before = hashlib.sha256(original).hexdigest()
    if before != EXPECTED_GLB_SHA256:
        raise ValueError(f'Unexpected model.glb SHA-256 {before}; expected the revision 1.2 output '
                         f'{EXPECTED_GLB_SHA256}.')
    known = {d.get('id') for d in manifest.get('known_deviations', [])}
    if known != {'approach-polymer-overlay', 'joint-seal-length'}:
        raise ValueError(f'Unexpected known_deviations {sorted(known)}')
    length = struct.unpack_from('<I', original, 12)[0]
    gltf = json.loads(original[20:20 + length])
    binary = bytearray(original[28 + length:])
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
    for pid, e in JOINTS:
        prim = meshes[pid]['primitives'][0]
        stored = to_native(read(prim['attributes']['POSITION']).astype(np.float64))
        faces = read(prim['indices']).reshape(-1, 3)
        old = trimesh.Trimesh(vertices=stored, faces=faces, process=False)
        x, y, z = stored.T
        u = x - k * y
        centre = e * LENGTH / 2
        dz = z - surface(y)
        side = np.where(np.abs(y) < TOL, 0.0, np.sign(y))
        if (len(stored) != 12 or not old.is_watertight or old.volume <= 0
                or not np.allclose(np.abs(y)[side != 0], WIDTH / 2, atol=TOL) or (side == 0).sum() != 4
                or not np.all(np.abs(np.abs(u - centre) - SEAL_HALF_WIDTH) < TOL)
                or not np.all((np.abs(dz - SEAL_TOP) < TOL) | (np.abs(dz - SEAL_BOTTOM) < TOL))):
            raise ValueError(f'{pid}: unexpected original joint-seal geometry')
        # Rebuild exactly (float64) from the verified layout: same stations, depth and profile; the deck-edge
        # vertices move along the skewed joint line to the barrier toes, |Y| = 22 ft.
        ue = centre + np.sign(u - centre) * SEAL_HALF_WIDTH
        ye = side * ROADWAY_HALF
        exact = np.column_stack([ue + k * ye, ye,
                                 surface(ye) + np.where(dz > (SEAL_TOP + SEAL_BOTTOM) / 2, SEAL_TOP, SEAL_BOTTOM)])
        new = trimesh.Trimesh(vertices=exact, faces=faces, process=False)
        if not new.is_watertight or not new.is_winding_consistent or new.volume <= 0:
            raise ValueError(f'{pid}: invalid trimmed seal')
        along = 2 * ROADWAY_HALF / np.cos(np.radians(SKEW))
        if abs(along / FT - DRAWN_LENGTH_FT) > .5 or abs(2 * along / FT - QUANTITY_LFT) > 1:
            raise ValueError(f'{pid}: trimmed length does not reproduce sheet 7 / sheet 8')
        prim['attributes']['POSITION'] = append(to_gltf(exact).astype('<f4'), 'VEC3', 5126)
        p = parts[pid]
        old_bounds, old_volume = p['bounds_m'], p['volume_m3']
        p['bounds_m'] = new.bounds.round(6).tolist()
        p['volume_m3'] = round(float(new.volume), 9)
        p['pdf_pages'] = sorted(set(p['pdf_pages']) | {7, 8})
        p['basis'] = 'Joint type, location and sealant length drawn and scheduled; assumed seal width and depth'
        p['dimensions'].update(
            sealant_limits='between the barrier toes, across the 44 ft clear roadway (sheet 7 plan hatch)',
            transverse_limit_m=round(ROADWAY_HALF, 6), width_square_to_sr1_ft=44,
            length_along_skew_m=round(along, 6), length_along_skew_ft=round(along / FT, 3),
            drawn_length_ft=DRAWN_LENGTH_FT, quantity_both_joints_lft=QUANTITY_LFT,
            display_width_m=2 * SEAL_HALF_WIDTH, display_depth_m=SEAL_TOP - SEAL_BOTTOM)
        p['note'] = (p.get('note', '') + ' Limited to the 44 ft roadway between the barrier toes (|Y| <= 6.7056 m): '
                     'sheet 7 draws each resealed Type 1-A joint across the roadway hatch only and dimensions it 47 ft '
                     'along the skew (44 ft / cos 20 deg = 46.82 ft); sheet 8 schedules 94 lft for both. Was the full '
                     '47 ft 1 1/2 in deck width (50.15 ft along the skew), running 1 mm into the barrier bases. The '
                     '25 mm depth is also a display value.').strip()
        meshes[pid]['extras'].update(p)
        changes.append(pid)
        values[pid] = dict(
            transverse_limits_m=f'|Y| <= {ROADWAY_HALF:.6f} (barrier toe); was |Y| <= {WIDTH / 2:.6f} (deck edge)',
            length_along_skew=f'{along:.6f} m = {along / FT:.3f} ft; was {WIDTH / np.cos(np.radians(SKEW)):.6f} m = '
                              f'{WIDTH / np.cos(np.radians(SKEW)) / FT:.3f} ft',
            station_range_m=f'u = {centre - SEAL_HALF_WIDTH:+.6f} .. {centre + SEAL_HALF_WIDTH:+.6f}, unchanged',
            bounds_before=old_bounds, bounds_after=p['bounds_m'], volume_m3=f'{old_volume} -> {p["volume_m3"]}')
        print(f'{pid}: |Y| <= {ROADWAY_HALF:.6f} m, {along:.6f} m = {along / FT:.3f} ft along the skew, '
              f'volume {old.volume:.9f} -> {new.volume:.9f} m3')

    for d in manifest.get('detail_coverage', []):
        if d.get('feature') == 'Drawing envelope and proposed overlay':
            d['detail'] = (d['detail'] + ' The resealed Type 1-A joint envelopes span the 44 ft roadway between the '
                           'barrier toes, 47 ft along the skew per joint (sheet 7 plan; sheet 8: 94 lft).')
    removed = [d['id'] for d in manifest['known_deviations'] if d['id'] == 'joint-seal-length']
    manifest['known_deviations'] = [d for d in manifest['known_deviations'] if d['id'] != 'joint-seal-length']
    for d in manifest['known_deviations']:
        if d['id'] == 'approach-polymer-overlay':
            d['deviation'] = ('The non-warranted polymer overlay on both RCBAs is recorded in the approach notes and '
                              'dimensions only; it is not shown as a layer or a separate finish on the approach top '
                              'faces.')
            d['reason'] = APPROACH_REASON

    gltf['buffers'][0]['byteLength'] = len(binary)
    while len(binary) % 4:
        binary.append(0)
    encoded = json.dumps(gltf, ensure_ascii=True, separators=(',', ':')).encode()
    encoded += b' ' * ((-len(encoded)) % 4)
    out = (struct.pack('<III', 0x46546c67, 2, 28 + len(encoded) + len(binary)) +
           struct.pack('<II', len(encoded), 0x4e4f534a) + encoded + struct.pack('<II', len(binary), 0x004e4942) + binary)
    backup = ROOT / 'data/fem_research'
    backup.mkdir(exist_ok=True)
    (backup / f'{BID}_before_review_correction_3.glb').write_bytes(original)
    (backup / f'{BID}_manifest_before_review_correction_3.json').write_bytes(raw_manifest)
    path.write_bytes(out)
    manifest[TAG_KEY] = TAG
    manifest['revision'] = REVISION
    manifest['review_correction_record_3'] = dict(
        source_pdf_pages=[3, 7, 8], printed_sheets=[3, 7, 8], previous_revision=PREVIOUS_REVISION,
        changed_parts=changes, added_parts=[], removed_parts=[],
        resolved_deviations=removed,
        values=dict(values, basis='sheet 7 plan: each resealed Type 1-A joint drawn across the 44 ft roadway hatch only '
                                  '(hatch edges 10 + 12 ft from S.R. 1), dimensioned 47 ft along the skew; '
                                  '44 ft / cos 20 deg = 46.82 ft; sheet 8: Joints in PCCP, Filled, 94 lft = 2 x 47'),
        kept_deviations=[dict(id='approach-polymer-overlay', verdict='keep',
                              missing='thickness of the non-warranted approach polymer overlay (no sheet gives it; '
                                      'the 3/8 in of sheet 3 is for the warranted deck overlay)',
                              settled_by='special provision or pay-item specification for "Polymer Overlay, Bridge '
                                         'Deck Approaches" in the contract B-44532 proposal, or a revised sheet')],
        decisions=[],
        before_glb_sha256=before, after_glb_sha256=hashlib.sha256(out).hexdigest())
    text = json.dumps(manifest, indent=2)
    if b'\r\n' in raw_manifest:
        text = text.replace('\n', '\r\n')
    if raw_manifest.endswith(b'\n'):
        text += '\r\n' if b'\r\n' in raw_manifest else '\n'
    mp.write_bytes(text.encode('utf-8'))
    print(json.dumps(manifest['review_correction_record_3']))


if __name__ == '__main__':
    correct()

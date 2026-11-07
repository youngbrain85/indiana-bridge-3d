"""Second drawing-confirmed correction (runs after correct_21st_street_i465_review.py): Bent 2 diaphragm width,
preserving unrelated GLB buffers.

    python scripts/correct_21st_street_i465_review_2.py [--dry-run]

Drawing evidence (contract IB-30026, drawings.pdf; printed sheets 41-62 are PDF pages 41-62):

- Sheet 57 (PDF 57), SECTION V-V "SECTION THRU BENT #2 DIAPHRAGM": the diaphragm faces are dimensioned 2'-0" either
  side of CL Bent No. 2, 4'-0" overall, and continue in one line into the faces of the 4 ft cap (sheet 45, PLAN OF
  CAP: 2'-0" + 2'-0"). The section is cut on the TYPICAL SECTION @ BENT #2 DIAPHRAGM (ALONG SKEW), so it is normal to
  the bent, and the cap it shows is 4'-0", its width normal to the bent.
- The model built the diaphragm 4 ft along Line M, i.e. 4 ft x cos 18 deg = 3.804 ft (1.159529 m) normal to the
  bent, with each face 0.029836 m (1.17 in) inside the cap face.

Each face is moved out to n = +/-0.6096 m (n = X cos 18 deg + Y sin 18 deg, native metres). The added 0.029836 m
strips are the existing diaphragm cross-section carried on along Line M (the beams, end blocks, haunch zone and
deck soffit are prismatic along X here), minus the unchanged beam and end-block envelopes and the deck, with the
first correction's underside re-applied: 1 in preformed joint material on the cap between seats and 4 1/2 in on the
seats (pad top), so pads, seats and cap stay free. The rest of the diaphragm is unchanged.

Not changed (recorded in known_deviations): the sheet 54 (PDF 54) BEAM END DETAIL AT BENT #2 draws the "Edge of
Diaphragm and Preformed Expansion Joint Material Under Diaphragm" about 3 in inside the "Face of Bent Cap"; that
line is not dimensioned (its 4'-0" dimension is between the cap faces), so the dimensioned section V-V governs.

Part ids and mesh names are unchanged; only diaphragm_pier is re-meshed (new accessors appended).

Requires numpy, trimesh and manifold3d.
"""
import hashlib
import json
import struct
import sys
from pathlib import Path

import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[1]
BID = '21st-street-i465'
BASE = ROOT / 'data/bridges' / BID
FT = 0.3048
IN = FT / 12
TAG = 'bent2-diaphragm-4ft-normal-to-bent'
REVISION = '1.2-review-corrections-2'
PREVIOUS_TAG = 'pier-seat-joints-railing-2ft10-approach-square-end'   # correct_21st_street_i465_review.py
PREVIOUS_REVISION = '1.1-review-corrections'

SKEW = np.radians(18.0)
C, S = float(np.cos(SKEW)), float(np.sin(SKEW))
N = np.array([C, S, 0.0])                 # normal to Bent 2 (native X east along Line M, Y north)
T = np.array([-S, C, 0.0])                # along Bent 2
HALF_OLD = 2.0 * FT * C                   # 4 ft along Line M, as built: 0.579764 m normal to the bent
HALF_NEW = 2.0 * FT                       # sheet 57 V-V: 2'-0" either side of CL Bent No. 2
CAP_JOINT = 1.0 * IN                      # sheet 57 V-V (first correction)
SEAT_JOINT = 4.5 * IN                     # sheet 57 W-W, sheet 54 pad table (first correction)
SEATS = ('A1', 'A2', 'A3')
BEAMS = [f'beam_{s}{i}' for s in 'AB' for i in (1, 2, 3)]
END_BLOCKS = [f'beam_A{i}_endblock_2' for i in (1, 2, 3)] + [f'beam_B{i}_endblock_1' for i in (1, 2, 3)]
EPS = 1e-3                                # overlap of the added strip into the old body, for a robust union
TOL = 1e-5
CLASH = 1e-7                              # m3


def oriented_box(n0, n1, t0, t1, z0, z1):
    """Box in (n, t, z) bent coordinates, returned in native coordinates."""
    box = trimesh.creation.box(bounds=[[n0, t0, z0], [n1, t1, z1]])
    m = np.eye(4)
    m[:3, 0], m[:3, 1], m[:3, 2] = N, T, (0.0, 0.0, 1.0)
    box.apply_transform(m)
    return box


def boolean(op, meshes):
    return getattr(trimesh.boolean, op)(meshes, engine='manifold')


def correct(dry_run=False):
    mp = BASE / 'model_manifest.json'
    raw_manifest = mp.read_bytes()
    manifest = json.loads(raw_manifest)
    if manifest.get('review_geometry_correction_2') == TAG:
        print('Already corrected.')
        return
    if manifest.get('review_geometry_correction') != PREVIOUS_TAG or manifest.get('revision') != PREVIOUS_REVISION:
        raise ValueError('Run scripts/correct_21st_street_i465_review.py first (expected revision '
                         f'{PREVIOUS_REVISION}, found {manifest.get("revision")}).')
    path = BASE / 'model.glb'
    original = path.read_bytes()
    before = hashlib.sha256(original).hexdigest()
    if before != manifest['review_geometry_correction_record']['after_glb_sha256']:
        raise ValueError('model.glb differs from the output of the first correction')
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

    def prim(pid):
        ps = meshes[pid]['primitives']
        if len(ps) != 1:
            raise ValueError(f'{pid}: expected one primitive')
        return ps[0]

    def solid(pid):
        p = prim(pid)
        return trimesh.Trimesh(vertices=read(p['attributes']['POSITION']).astype(np.float64),
                               faces=read(p['indices']).reshape(-1, 3), process=False)

    def overlap(a, b):
        return float(boolean('intersection', [a, b]).volume)

    # ---------------------------------------------------------------- expected starting state
    cap = solid('pier_cap')
    cap_top = float(cap.bounds[1][2])
    cn = cap.vertices @ N
    if abs(cap_top - 9.6012) > TOL or abs(cn.min() + HALF_NEW) > TOL or abs(cn.max() - HALF_NEW) > TOL:
        raise ValueError('pier_cap: expected the 4 ft cap (n = +/-0.6096 m) with its top at El. 761.50')
    dia = solid('diaphragm_pier')
    dn = dia.vertices @ N
    y_end = float(np.abs(dia.vertices[:, 1]).max())
    if (not dia.is_watertight or abs(dn.min() + HALF_OLD) > TOL or abs(dn.max() - HALF_OLD) > TOL
            or abs(dia.bounds[0][2] - (cap_top + CAP_JOINT)) > TOL or abs(y_end - 22.0 * FT) > TOL):
        raise ValueError('diaphragm_pier: expected the first-correction diaphragm, 4 ft along Line M '
                         '(n = +/-0.579764 m), underside 1 in above the cap')
    seat_cutters, seat_levels = [], []
    for sid in SEATS:
        ped = solid(f'pedestal_{sid}')
        pn, pt = ped.vertices @ N, ped.vertices @ T
        top = float(ped.bounds[1][2])
        if (len(ped.vertices) != 8 or abs(pn.min() + HALF_NEW) > TOL or abs(pn.max() - HALF_NEW) > TOL
                or len(np.unique(pt.round(4))) != 2):
            raise ValueError(f'pedestal_{sid}: expected a 4 ft x 6 ft seat across the cap')
        # Seat footprint, carried past both faces so it never shares a face plane with the strip.
        seat_cutters.append(oriented_box(-HALF_NEW - 0.1, HALF_NEW + 0.1, pt.min(), pt.max(),
                                         cap_top - 0.3, top + SEAT_JOINT))
        seat_levels.append(top + SEAT_JOINT)
    lo, hi = dia.bounds
    cap_cutter = trimesh.creation.box(bounds=[[lo[0] - 0.5, lo[1] - 0.5, cap_top - 0.3],
                                              [hi[0] + 0.5, hi[1] + 0.5, cap_top + CAP_JOINT]])
    envelopes = [solid(pid) for pid in BEAMS + END_BLOCKS + ['deck']]

    # Interfaces before (for the guards and the record)
    near = [p['id'] for p in manifest['parts'] if p['id'] != 'diaphragm_pier'
            and np.all(np.array(p['bounds_m'])[0] <= hi + 0.1) and np.all(np.array(p['bounds_m'])[1] >= lo - 0.1)]
    near_solids = {pid: solid(pid) for pid in near}
    near_solids = {pid: m for pid, m in near_solids.items() if m.is_watertight}
    before_overlap = {pid: overlap(dia, m) for pid, m in near_solids.items()}

    # ---------------------------------------------------------------- widen to 4 ft normal to the bent
    strips = []
    for sign in (1, -1):
        shifted = dia.copy()
        shifted.apply_translation([sign * (HALF_NEW - HALF_OLD) / C, 0.0, 0.0])
        n0, n1 = sorted([sign * (HALF_OLD - EPS), sign * HALF_NEW])
        slab = oriented_box(n0, n1, -9.0, 9.0, cap_top - 0.5, hi[2] + 1.0)
        # Fill below the pad tops: the shifted copy carries its seat cut-outs 9.7 mm along the bent.
        fill = boolean('intersection', [slab, trimesh.creation.box(
            bounds=[[lo[0] - 1, -y_end, cap_top - 0.3], [hi[0] + 1, y_end, max(seat_levels)]])])
        strip = boolean('intersection', [boolean('union', [shifted, fill]), slab])
        strip = boolean('difference', [strip, cap_cutter] + seat_cutters + envelopes)
        if not strip.is_watertight or strip.volume <= 0:
            raise ValueError('diaphragm_pier: invalid widening strip')
        strips.append(strip)
    new_dia = boolean('union', [dia] + strips)
    added = new_dia.volume - dia.volume
    nn = new_dia.vertices @ N
    expected = 2 * (HALF_NEW - HALF_OLD) * (dia.volume / (2 * HALF_OLD))
    if (not new_dia.is_watertight or abs(nn.min() + HALF_NEW) > TOL or abs(nn.max() - HALF_NEW) > TOL
            or abs(new_dia.bounds[0][2] - (cap_top + CAP_JOINT)) > TOL or not 0.9 < added / expected < 1.1):
        raise ValueError('diaphragm_pier: invalid widened diaphragm')

    after_overlap = {pid: overlap(new_dia, m) for pid, m in near_solids.items()}
    for pid, v in after_overlap.items():
        if pid.startswith('haunch_') or pid == 'deck':
            continue                       # existing concrete interfaces, reported below
        if v > CLASH:
            raise ValueError(f'diaphragm_pier overlaps {pid} ({v:.3e} m3)')
    if after_overlap['deck'] > before_overlap['deck'] + 1e-6:
        raise ValueError('diaphragm_pier: new overlap with the deck')
    haunch = [round(sum(v for k, v in o.items() if k.startswith('haunch_')), 6)
              for o in (before_overlap, after_overlap)]
    deck = [round(before_overlap['deck'], 6), round(after_overlap['deck'], 6)]

    # ---------------------------------------------------------------- write the mesh and the manifest entry
    p = prim('diaphragm_pier')
    color = read(p['attributes']['COLOR_0'])[0]
    vertices = new_dia.vertices.astype('<f4')
    p['attributes'] = {'POSITION': append(vertices, 'VEC3', 5126),
                       'COLOR_0': append(np.tile(color, (len(vertices), 1)).astype('u1'), 'VEC4', 5121)}
    gltf['accessors'][p['attributes']['COLOR_0']]['normalized'] = True
    p['indices'] = append(new_dia.faces.reshape(-1, 1).astype('<u4'), 'SCALAR', 5125)
    stored = trimesh.Trimesh(vertices=vertices.astype(np.float64), faces=new_dia.faces, process=False)
    if not stored.is_watertight:
        raise ValueError('diaphragm_pier: not watertight after float32 storage')
    part = parts['diaphragm_pier']
    part['bounds_m'] = stored.bounds.round(6).tolist()
    part['volume_m3'] = round(float(stored.volume), 8)
    part.setdefault('dimensions', {}).update(width_normal_to_bent_ft=4.0)
    part['note'] += (' Width corrected to 4 ft normal to the bent, faces flush with the cap faces 2 ft either side '
                     'of CL Bent 2 (sheet 57 section V-V); previously 4 ft along Line M, 3.80 ft normal to the bent '
                     f'(+{added:.3f} m3).')
    meshes['diaphragm_pier']['extras'].update(part)
    print(f'diaphragm_pier: faces n = +/-{HALF_OLD:.6f} -> +/-{HALF_NEW:.6f} m, '
          f'volume {dia.volume:.4f} -> {stored.volume:.4f} m3')

    b = np.array([q['bounds_m'] for q in manifest['parts']])
    lo, hi = b[:, 0].min(axis=0), b[:, 1].max(axis=0)
    manifest['bounds_m'] = [lo.round(6).tolist(), hi.round(6).tolist()]
    manifest['glb_bounds_m'] = [[round(lo[0], 6), round(lo[2], 6), round(-hi[1], 6)],
                                [round(hi[0], 6), round(hi[2], 6), round(-lo[1], 6)]]
    for d in manifest['detail_coverage']:
        if d['feature'] == 'Beam end blocks and concrete diaphragms':
            d['detail'] += (' Bent 2 diaphragm 4 ft wide normal to the bent, flush with the cap faces '
                            '(sheet 57 section V-V).')
    deviations = [d for d in manifest.get('known_deviations', []) if d.get('id') != 'bent2-diaphragm-edge-setback']
    deviations.append(dict(
        id='bent2-diaphragm-edge-setback',
        parts='diaphragm_pier',
        source='sheet 54 (PDF 54) BEAM END DETAIL AT BENT #2; sheet 57 (PDF 57) section V-V',
        deviation='The diaphragm faces are flush with the cap faces, 2 ft either side of CL Bent 2, as dimensioned '
                  'in section V-V. The sheet 54 plan draws the "Edge of Diaphragm and Preformed Expansion Joint '
                  'Material Under Diaphragm" about 3 in inside the "Face of Bent Cap" (3 ft 6 in between edges, '
                  'scaled at 3/4 in = 1 ft); that line carries no dimension.',
        reason='The two sheets conflict; the dimensioned section governs over a scaled plan line.'))
    manifest['known_deviations'] = deviations

    gltf['buffers'][0]['byteLength'] = len(binary)
    while len(binary) % 4:
        binary.append(0)
    encoded = json.dumps(gltf, ensure_ascii=True, separators=(',', ':')).encode()
    encoded += b' ' * ((-len(encoded)) % 4)
    out = (struct.pack('<III', 0x46546c67, 2, 28 + len(encoded) + len(binary)) +
           struct.pack('<II', len(encoded), 0x4e4f534a) + encoded + struct.pack('<II', len(binary), 0x004e4942) + binary)
    manifest['review_geometry_correction_2'] = TAG
    manifest['revision'] = REVISION
    manifest['review_geometry_correction_2_record'] = dict(
        source_pdf_pages=[45, 54, 57], printed_sheets=[45, 54, 57], previous_revision=PREVIOUS_REVISION,
        corrections={
            'diaphragm_pier': f'Faces moved from n = +/-{HALF_OLD:.6f} m (4 ft along Line M) to n = +/-{HALF_NEW:.6f} '
                              'm, 4 ft normal to the bent and flush with the cap faces (n = X cos 18 deg + Y sin 18 '
                              'deg); underside unchanged (1 in above the cap between seats, pad top over the seats); '
                              f'volume +{added:.6f} m3; sheet 57 section V-V, sheet 45 plan of cap.'},
        interfaces={'haunch_overlap_m3_before_after': haunch, 'deck_overlap_m3_before_after': deck,
                    'pads_seats_cap_beams_end_blocks': f'no overlap above {CLASH:g} m3'},
        changed_parts=['diaphragm_pier'],
        before_glb_sha256=before, after_glb_sha256=hashlib.sha256(out).hexdigest())
    record = manifest['review_geometry_correction_2_record']
    if dry_run:
        print(json.dumps(record, indent=1))
        print('Dry run, nothing written.')
        return
    backup = ROOT / 'data/fem_research'
    backup.mkdir(exist_ok=True)
    (backup / f'{BID}_before_review_correction_2.glb').write_bytes(original)
    (backup / f'{BID}_manifest_before_review_correction_2.json').write_bytes(raw_manifest)
    path.write_bytes(out)
    mp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(record))


if __name__ == '__main__':
    correct(dry_run='--dry-run' in sys.argv)

"""One-time, drawing-confirmed corrections from the external model review, preserving unrelated GLB buffers.

    python scripts/correct_21st_street_i465_review.py [--dry-run]

1. Bent 2 diaphragm on its joint material (printed sheet 57 = PDF 57, sections V-V and W-W; sheet 54 = PDF 54,
   BEAM END DETAIL AT BENT #2 and the BENT #2 bearing-pad table). Between the bearing seats the diaphragm sits on
   1 in preformed expansion joint material on the top of the cap; at the beams it sits on 4 1/2 in preformed joint
   material on the 6 ft seat, beside the 4 1/2 in elastomeric pads, and its underside is level with the beam soffit.
   The model ran the diaphragm down to the cap top (El. 761.50) over the whole 4 ft width, so it filled 99.3-99.5 %
   of all 12 Bent 2 pads and about 95 % of the three seats. This script cuts the underside to cap top + 1 in and,
   over each 4 ft x 6 ft seat footprint, to seat top + 4 1/2 in (the pad top). Pads, seats and cap are unchanged.

2. Concrete "C" railing, modified (sheets 41, 56 and 59 = PDF 41, 56 and 59): the railing top is 2'-10" above the
   sidewalk at the railing face on all three sheets (sheet 59: 8 in head + 2'-2" stem above the level construction
   joint at the sidewalk surface). The model's railing was 22.56 in above the sidewalk at every station. The head
   (8 in, with its 1 in chamfers) is raised 11.44 in by lengthening the stem, and every ornamental-railing part that
   stands on the railing top (posts, base plates, anchor-bolt nuts, caps, pipe and tube rails, pickets, arches,
   rings and stars; sheets 60-62) is raised by the same amount. The recess indication planes are left as they are.

3. R.C. approach slabs (printed sheet 74 = PDF 73, PLAN, west approach shown, east rotated 180 deg): the pavement
   end is square to Line "M"; the slab is 20'-6" (minimum) at its short edge and 32'-3 1/2" at its long edge (the
   south edge of the west slab, the north edge of the east slab). The model used a 20'-6" parallelogram with both
   ends skewed. The pavement end is moved to X = -/+43.737 m so the long edge is 32'-3 1/2" (short edge 20'-7 1/8",
   which satisfies the 20'-6" minimum); the bridge end, the 36 ft width and the 12 in thickness are kept. The 6'-10"
   sidewalk moment slabs end on the same square line (1 in expansion joint on the plan). Elevations are recomputed on
   the existing profile (PVI 13+00.00, El. 773.72, L = 600 ft, +3.728 % / -3.994 %), 2 % crown, 8 in curb and 2 %
   sidewalk slope, which reproduce the original vertices.

Mesh topology is kept for the railings and the approach slabs (vertices move, faces unchanged); the diaphragm is
re-meshed by a boolean difference. Part ids and mesh names are unchanged.

Requires numpy, trimesh and manifold3d.
"""
import hashlib
import json
import re
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
TAG = 'pier-seat-joints-railing-2ft10-approach-square-end'
REVISION = '1.1-review-corrections'

# Bent 2 (sheets 54, 57)
CAP_JOINT = 1.0 * IN              # 1 in preformed joint on the cap between seats (V-V)
SEAT_JOINT = 4.5 * IN             # 4 1/2 in joint on the seats = 4 1/2 in pad thickness (W-W, pad table)
SEATS = {1: 'A1', 2: 'A2', 3: 'A3'}   # pedestal_<A k> carries pad_A<k>_2_* and pad_B<k>_1_*

# Railing (sheets 41, 56, 59)
RAIL_ABOVE_SIDEWALK = 34.0 * IN   # 2'-10"
RAIL_BEFORE = 0.573024            # measured, every station, both railings
ORNAMENT = re.compile(r'(railpost|railbase|railcap|railbolt|railpipe|railtube|picket|railarch|railring|starring|star)_')

# Approach slabs (sheet 74 / PDF 73) and profile (sheet 40/56 and manifest assumptions)
SKEW_K = float(np.tan(np.radians(18.0)))
BRIDGE_END_C = 35.677475          # bridge end of the approach slabs: X + k*Y = -/+C (unchanged)
ROAD_HALF = 18.0 * FT             # 36 ft slab
WALK_OUT = 5.4864 + 82.0 * IN     # 6'-10" moment slab
LONG_EDGE = (32.0 + 3.5 / 12) * FT
SHORT_MIN = 20.5 * FT
OLD_LENGTH = 20.5 * FT            # original parallelogram length along X
SLAB_T = 12.0 * IN
CURB = 8.0 * IN
PVI_STA, PVI_EL, VC_L, G1, G2 = 1300.00, 773.72, 600.0, 0.03728, -0.03994
X0_STA = 1300.08                  # Bent 2 station at X = 0
APPROACHES = {'west': -1, 'east': 1}


def grade_z(x):
    """Profile grade on Line M (native Z, m) at native X (m)."""
    s = X0_STA + np.asarray(x) / FT
    bvc = PVI_STA - VC_L / 2
    u = s - bvc
    el = PVI_EL - G1 * VC_L / 2 + G1 * u + (G2 - G1) / (2 * VC_L) * u ** 2
    return (el - 730.0) * FT


def road_top(x, y):
    return grade_z(x) - 0.02 * np.abs(y)


def walk_top(x, y):
    return grade_z(x) - 0.02 * ROAD_HALF + CURB + 0.02 * (np.abs(y) - ROAD_HALF)


def correct(dry_run=False):
    mp = BASE / 'model_manifest.json'
    manifest = json.loads(mp.read_text(encoding='utf-8'))
    if manifest.get('review_geometry_correction') == TAG:
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

    def prim(pid):
        ps = meshes[pid]['primitives']
        if len(ps) != 1:
            raise ValueError(f'{pid}: expected one primitive')
        return ps[0]

    def solid(pid):
        p = prim(pid)
        return trimesh.Trimesh(vertices=read(p['attributes']['POSITION']).astype(np.float64),
                               faces=read(p['indices']).reshape(-1, 3), process=False)

    def set_vertices(pid, v, faces):
        """Same faces, moved vertices: only a new POSITION accessor."""
        prim(pid)['attributes']['POSITION'] = append(v.astype('<f4'), 'VEC3', 5126)
        return trimesh.Trimesh(vertices=v.astype('<f4').astype(np.float64), faces=faces, process=False)

    def finish(pid, mesh, note, dims=None, **extra):
        p = parts[pid]
        p['bounds_m'] = mesh.bounds.round(6).tolist()
        if 'volume_m3' in p:
            p['volume_m3'] = round(float(mesh.volume), 8)
        if dims:
            p.setdefault('dimensions', {}).update(dims)
        p.update(extra)
        p['note'] = note
        meshes[pid]['extras'].update(p)
        changes.append(pid)

    changes = []

    # ---------------------------------------------------------------- 1. Bent 2 diaphragm underside
    cap = solid('pier_cap')
    cap_top = float(cap.bounds[1][2])
    dia = solid('diaphragm_pier')
    if not dia.is_watertight or abs(dia.bounds[0][2] - cap_top) > 1e-5 or abs(cap_top - 9.6012) > 1e-5:
        raise ValueError('diaphragm_pier: expected a watertight diaphragm down to the cap top El. 761.50')
    lo, hi = dia.bounds
    cutters = [trimesh.creation.box(bounds=[[lo[0] - 0.5, lo[1] - 0.5, cap_top - 0.3],
                                            [hi[0] + 0.5, hi[1] + 0.5, cap_top + CAP_JOINT]])]
    guarded = ['pier_cap']
    seat_levels = {}
    for k, sid in SEATS.items():
        ped = solid(f'pedestal_{sid}')
        top = float(ped.bounds[1][2])
        zs = np.unique(ped.vertices[:, 2].round(6))
        if len(ped.vertices) != 8 or len(zs) != 2 or abs(zs[0] - cap_top) > 1e-5:
            raise ValueError(f'pedestal_{sid}: expected a level box seat on the cap')
        pads = [f'pad_A{k}_2_1', f'pad_A{k}_2_2', f'pad_B{k}_1_1', f'pad_B{k}_1_2']
        for pad in pads:
            pm = solid(pad)
            if abs(pm.bounds[0][2] - top) > 1e-5 or abs(pm.bounds[1][2] - (top + SEAT_JOINT)) > 1e-5:
                raise ValueError(f'{pad}: expected a 4 1/2 in pad on seat {sid}')
            overlap = trimesh.boolean.intersection([dia, pm], engine='manifold').volume
            if overlap < 0.9 * pm.volume:
                raise ValueError(f'{pad}: expected the original diaphragm to encase the pad')
        cv = ped.vertices.copy()
        cv[np.isclose(cv[:, 2], top, atol=1e-5), 2] = top + SEAT_JOINT
        cv[np.isclose(cv[:, 2], cap_top, atol=1e-5), 2] = cap_top - 0.3
        cutter = trimesh.Trimesh(vertices=cv, faces=ped.faces, process=False)
        if cutter.volume < 0:
            cutter.invert()
        cutters.append(cutter)
        guarded += [f'pedestal_{sid}'] + pads
        seat_levels[f'pedestal_{sid}'] = round(top + SEAT_JOINT, 6)
    new_dia = trimesh.boolean.difference([dia] + cutters, engine='manifold')
    if not new_dia.is_watertight or not 0 < new_dia.volume < dia.volume:
        raise ValueError('diaphragm_pier: invalid boolean result')
    for g in guarded:
        if trimesh.boolean.intersection([new_dia, solid(g)], engine='manifold').volume > 1e-7:
            raise ValueError(f'diaphragm_pier still overlaps {g}')
    p = prim('diaphragm_pier')
    color = read(p['attributes']['COLOR_0'])[0]
    p['attributes'] = {'POSITION': append(new_dia.vertices.astype('<f4'), 'VEC3', 5126),
                       'COLOR_0': append(np.tile(color, (len(new_dia.vertices), 1)).astype('u1'), 'VEC4', 5121)}
    gltf['accessors'][p['attributes']['COLOR_0']]['normalized'] = True
    p['indices'] = append(new_dia.faces.reshape(-1, 1).astype('<u4'), 'SCALAR', 5125)
    removed = dia.volume - new_dia.volume
    finish('diaphragm_pier', new_dia,
           parts['diaphragm_pier']['note'] + ' Underside corrected to the preformed joint material of sheet 57 '
           '(sections V-V, W-W) and sheet 54: 1 in above the cap between seats and 4 1/2 in above each 6 ft seat '
           '(level with the pad tops), so the bearing pads and seats are no longer encased '
           f'(-{removed:.3f} m3).',
           dims=dict(joint_on_cap_in=1.0, joint_on_seats_in=4.5))
    print(f'diaphragm_pier: underside cut, -{removed:.3f} m3')

    # ---------------------------------------------------------------- 2. Railing height and ornamental railing
    deltas = []
    railing = {}
    for side in (1, -1):
        rid, sid = f'parapet_{side}', f'sidewalk_{side}'
        rail, walk = solid(rid), solid(sid)
        if len(rail.vertices) % 8 or len(walk.vertices) % 4:
            raise ValueError(f'{rid}: unexpected ring structure')
        rings = rail.vertices.reshape(-1, 8, 3)
        wrings = walk.vertices.reshape(-1, 4, 3)
        if len(rings) != len(wrings) or not np.allclose(rings[:, 5, :2], rings[:, 0, :2], atol=1e-6):
            raise ValueError(f'{rid}: unexpected ring structure')
        rel = rings[:, :, 2] - rings[:, [0], 2]
        if not (np.abs(rel[:, :2]).max() < 0.01 and rel[:, 2:].min() > 0.55):
            raise ValueError(f'{rid}: unexpected cross-section')
        face = np.isclose(np.abs(wrings[:, :, 1]), 7.3152, atol=1e-5)
        wtop = np.where(face, wrings[:, :, 2], -np.inf).max(axis=1)
        wx = np.array([wrings[i, face[i], 0].mean() for i in range(len(wrings))])
        if not np.allclose(wx, rings[:, 5, 0], atol=1e-5):
            raise ValueError(f'{rid}: railing and sidewalk stations differ')
        height = rings[:, 5, 2] - wtop
        if np.abs(height - RAIL_BEFORE).max() > 2e-5:
            raise ValueError(f'{rid}: railing is not 22.56 in above the sidewalk as expected')
        deltas.append(RAIL_ABOVE_SIDEWALK - height.mean())
        railing[side] = (rail, rings)
    delta = round(float(np.mean(deltas)), 6)
    for side, (rail, rings) in railing.items():
        rid = f'parapet_{side}'
        moved = rings.copy()
        moved[:, 2:, 2] += delta
        mesh = set_vertices(rid, moved.reshape(-1, 3), rail.faces)
        if not mesh.is_watertight or mesh.volume <= rail.volume:
            raise ValueError(f'{rid}: invalid corrected railing')
        overall = (rings[0, 5, 2] - rings[0, 0, 2] + delta) / IN
        finish(rid, mesh,
               'Top 2 ft 10 in (34 in) above the sidewalk at the railing face, sheets 41, 56 and 59, with an 8-in '
               f'thickened head; corrected from 22.56 in by lengthening the stem {delta / IN:.2f} in. Fine side '
               'recess bevels and edge radii omitted.',
               dims=dict(overall_height_in=round(overall, 2), height_above_sidewalk_in=34, head_height_in=8))
    ornaments = [pid for pid in parts if ORNAMENT.match(pid)]
    if len(ornaments) != 1656:
        raise ValueError(f'expected 1656 ornamental-railing parts, found {len(ornaments)}')
    tops = {side: (r[1][:, 5, 0], (r[1][:, 4, 2] + r[1][:, 5, 2]) / 2) for side, r in railing.items()}
    for pid in ornaments:
        m = solid(pid)
        v = m.vertices.copy()
        side = 1 if v[:, 1].mean() > 0 else -1
        if pid.startswith('railbase_'):
            x, z = tops[side]
            order = np.argsort(x)
            seat = np.interp(v[:, 0].mean(), x[order], z[order])
            if abs(v[:, 2].min() - seat) > 0.003:
                raise ValueError(f'{pid}: base plate does not sit on the original railing top')
        v[:, 2] += delta
        mesh = set_vertices(pid, v, m.faces)
        finish(pid, mesh, (parts[pid].get('note', '') + f' Raised {delta / IN:.2f} in with the corrected railing '
                           'top (2 ft 10 in above the sidewalk, sheets 41, 56 and 59).').strip())
    print(f'railings: +{delta:.6f} m ({delta / IN:.2f} in); {len(ornaments)} ornamental parts raised')

    # ---------------------------------------------------------------- 3. Approach slabs and moment slabs
    approach_dims = {}
    for name, sign in APPROACHES.items():
        # Long edge: south of the west slab, north of the east slab (rotated 180 deg).
        y_long = sign * ROAD_HALF
        x_long_bridge = sign * BRIDGE_END_C - SKEW_K * y_long
        x_pave = x_long_bridge + sign * LONG_EDGE
        short = abs(x_pave - (sign * BRIDGE_END_C - SKEW_K * -y_long))
        if short < SHORT_MIN - 1e-6:
            raise ValueError(f'{name}: short edge below the 20 ft 6 in minimum')
        approach_dims[name] = (x_pave, short)
        for pid, ring_n, top_fn in [(f'approach_{name}', 6, road_top),
                                    (f'approach_walk_{name}_1', 4, walk_top),
                                    (f'approach_walk_{name}_-1', 4, walk_top)]:
            m = solid(pid)
            if not m.is_watertight or len(m.vertices) % ring_n:
                raise ValueError(f'{pid}: unexpected mesh')
            rings = m.vertices.reshape(-1, ring_n, 3)
            on_bridge = [np.allclose(r[:, 0] + SKEW_K * r[:, 1], sign * BRIDGE_END_C, atol=2e-5)
                         for r in (rings[0], rings[-1])]
            if on_bridge.count(True) != 1:
                raise ValueError(f'{pid}: bridge-end ring not found')
            if on_bridge[0]:
                rings = rings[::-1]
            old_pave = rings[0, :, 0] + SKEW_K * rings[0, :, 1]
            if not np.allclose(old_pave, sign * (BRIDGE_END_C + OLD_LENGTH), atol=2e-5):
                raise ValueError(f'{pid}: expected a skewed 20 ft 6 in parallelogram')
            top_z = top_fn(rings[:, :, 0], rings[:, :, 1])
            is_top = np.abs(rings[:, :, 2] - top_z) < 2e-4
            is_bot = np.abs(rings[:, :, 2] - (top_z - SLAB_T)) < 2e-4
            if not np.all(is_top ^ is_bot):
                raise ValueError(f'{pid}: elevations do not follow the expected profile')
            frac = np.linspace(0.0, 1.0, len(rings))[:, None]
            x_bridge = sign * BRIDGE_END_C - SKEW_K * rings[:, :, 1]
            new = rings.copy()
            new[:, :, 0] = x_pave + (x_bridge - x_pave) * frac
            new[:, :, 2] = top_fn(new[:, :, 0], new[:, :, 1]) - np.where(is_top, 0.0, SLAB_T)
            if on_bridge[0]:
                new = new[::-1]
            mesh = set_vertices(pid, new.reshape(-1, 3), m.faces)
            if not mesh.is_watertight or mesh.volume <= 0:
                raise ValueError(f'{pid}: invalid corrected slab')
            if pid == f'approach_{name}':
                finish(pid, mesh,
                       'Square pavement end and skewed bridge end per the sheet 74 (PDF 73) plan: 32 ft 3-1/2 in '
                       f'along the long edge and {short / FT:.3f} ft along the short edge (20 ft 6 in minimum); '
                       'corrected from a 20 ft 6 in parallelogram. Elevations on the Line M profile with 2% crown.',
                       dims=dict(long_edge_ft=round(LONG_EDGE / FT, 4), short_edge_ft=round(short / FT, 4),
                                 pavement_end='square to Line M'),
                       basis='Dimensioned plan')
            else:
                finish(pid, mesh,
                       'Nominal 6-ft-10 moment slab from the skewed bridge end to the square pavement-end line '
                       '(1 in expansion joint), sheet 74 (PDF 73) plan; corrected from a 20 ft 6 in parallelogram. '
                       'Adjoining roadway moment slabs and tie-bar details excluded.',
                       basis='Dimensioned width and end lines')
    print('approach slabs: pavement ends square at X = ' +
          ', '.join(f'{v[0]:+.6f}' for v in approach_dims.values()))

    # ---------------------------------------------------------------- manifest-level bookkeeping
    b = np.array([p['bounds_m'] for p in manifest['parts']])
    lo, hi = b[:, 0].min(axis=0), b[:, 1].max(axis=0)
    manifest['bounds_m'] = [lo.round(6).tolist(), hi.round(6).tolist()]
    manifest['glb_bounds_m'] = [[round(lo[0], 6), round(lo[2], 6), round(-hi[1], 6)],
                                [round(hi[0], 6), round(hi[2], 6), round(-lo[1], 6)]]
    for d in manifest['detail_coverage']:
        if d['feature'] == 'Beam end blocks and concrete diaphragms':
            d['detail'] += (' Bent 2 diaphragm underside on 1-in (cap) and 4-1/2-in (seat) preformed joint '
                            'material; bearing pads and seats are not encased.')
            d['sources'] = sorted(set(d['sources']) | {54})
        elif d['feature'] == 'Sidewalks and concrete parapets':
            d['detail'] = ('Two 6-ft sidewalks, raised 8 in and pitched toward roadway; modified C parapets 2 ft 10 in '
                           'above the sidewalk with thickened tops, approximate exterior recess indications.')
        elif d['feature'] == 'Approach slabs and joints':
            d['detail'] = ('36-ft-wide, 12-in road slabs with square pavement ends: 32 ft 3-1/2 in long edge and '
                           '20 ft 7-1/8 in short edge (20 ft 6 in minimum); adjoining 6-ft-10 moment slabs to the '
                           'same pavement-end line and Type 1A joint locations.')

    gltf['buffers'][0]['byteLength'] = len(binary)
    while len(binary) % 4:
        binary.append(0)
    encoded = json.dumps(gltf, ensure_ascii=True, separators=(',', ':')).encode()
    encoded += b' ' * ((-len(encoded)) % 4)
    out = (struct.pack('<III', 0x46546c67, 2, 28 + len(encoded) + len(binary)) +
           struct.pack('<II', len(encoded), 0x4e4f534a) + encoded + struct.pack('<II', len(binary), 0x004e4942) + binary)
    manifest['review_geometry_correction'] = TAG
    previous_revision = manifest.get('revision')
    manifest['revision'] = REVISION
    manifest['review_geometry_correction_record'] = dict(
        source_pdf_pages=[41, 54, 56, 57, 59, 60, 61, 62, 73], printed_sheets=[41, 54, 56, 57, 59, 60, 61, 62, 74],
        previous_revision=previous_revision,
        corrections={
            'diaphragm_pier': 'Underside 1 in above the cap between seats (El. 761.583) and 4 1/2 in above each seat '
                              '(pad top): ' + ', '.join(f'{k} {v:.6f} m' for k, v in seat_levels.items()) +
                              '; sheet 57 sections V-V/W-W, sheet 54.',
            'railings': f'Top raised {delta:.6f} m ({delta / IN:.2f} in) to 2 ft 10 in above the sidewalk; '
                        f'{len(ornaments)} ornamental-railing parts raised by the same amount; sheets 41, 56, 59.',
            'approach_slabs': 'Pavement ends square at X = ' +
                              ', '.join(f'{k} {v[0]:+.6f} m' for k, v in approach_dims.items()) +
                              '; long edge 32 ft 3-1/2 in, short edge ' +
                              ', '.join(f'{k} {v[1] / FT:.4f} ft' for k, v in approach_dims.items()) +
                              '; moment slabs end on the same line; sheet 74 (PDF 73).'},
        changed_parts=changes,
        before_glb_sha256=before, after_glb_sha256=hashlib.sha256(out).hexdigest())
    if dry_run:
        print(json.dumps({k: v for k, v in manifest['review_geometry_correction_record'].items()
                          if k != 'changed_parts'}, indent=1))
        print(f'{len(changes)} parts would change (dry run, nothing written).')
        return
    backup = ROOT / 'data/fem_research'
    backup.mkdir(exist_ok=True)
    (backup / f'{BID}_before_review_correction.glb').write_bytes(original)
    (backup / f'{BID}_manifest_before_review_correction.json').write_bytes(mp.read_bytes())
    path.write_bytes(out)
    mp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    record = manifest['review_geometry_correction_record']
    print(json.dumps({k: (v if k != 'changed_parts' else f'{len(v)} parts') for k, v in record.items()}))


if __name__ == '__main__':
    correct(dry_run='--dry-run' in sys.argv)

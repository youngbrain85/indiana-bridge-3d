"""Second drawing-confirmed correction of SR 44 over the Branch of Little Blue River: the steel guardrail connections
at the four TFC ends. Runs after scripts/correct_sr44_little_blue_review.py and preserves unrelated GLB buffers.

    python scripts/correct_sr44_little_blue_review_2.py

Drawing evidence (INDOT B-44483, drawings.pdf; printed sheet numbers equal PDF page numbers). Sheet 18 North and South
Railing Elevations are drawn at 1/4 in = 1 ft (18 PDF points per foot, 1.5 points per inch); the values below are
scaled from their vectors, with "Top of Deck" (the deck / approach top line at the TFC end) as the reference.

- At every TFC end the guardrail transition (MGS Without Curb at NW, SW and SE; Type TGB at NE) ends in a thrie-beam
  terminal connector drawn on the TFC, i.e. bolted to the TFC end face, not stopping short of it:
    NW: TFC end x = 231.0 pt, connector 231.0-276.0 pt -> laps 45.0 pt = 2'-6" onto the TFC
    SW: TFC end x = 231.0 pt, connector 231.0-276.0 pt -> 2'-6"
    SE: TFC end x = 1368.9 pt, connector 1323.9-1368.9 pt -> 2'-6"
    NE: TFC end x = 1076.0 pt, connector 1040.0-1076.0 pt -> 36.0 pt = 2'-0"
- The rail element is an upright thrie beam, 30.0 pt = 20 in deep:
    NW/SW/SE: top 46.5 pt and bottom 16.5 pt above Top of Deck = 31 in / 11 in
    NE (Type TGB): top 45.4 pt and bottom 15.4 pt above Top of Deck = 30.27 in / 10.27 in
  The full-depth thrie beam continues beyond the 2 m representative run at every corner (NE: 3.9 m before the
  W-beam transition), so the whole representative rail element is 20 in deep.
- Sheet 12 plan: the rail element runs on the roadway side of the posts, in line with the TFC end face. The TFC end
  face is vertical at 9 in from the rail back (sheet 18 plan taper, first correction) over the last 4'-3" of each TFC,
  so the 2'-6" lap lies on a flat face at |Y| = 6.5024 - 0.2286 = 6.2738 m.

Model change (second-check findings F5 residual, N1, N2): in each of the four representative guardrail runs the flat
0.30 m wide, 0.06 m high strip, which lay horizontally and stopped 105.8 mm short of its TFC, is replaced by an upright
rail element (thickness 0.06 m, as built) with its back on the TFC end face plane, lapping onto the TFC by the drawn
length and running to the end of the as-built run, from S + h_bottom to S + h_top, with S the corrected roadway
surface on that plane. The four posts are unchanged (byte-identical vertices). Part ids are unchanged.

Requires numpy and trimesh, plus scripts/correct_sr44_little_blue_review.py (constants and surface).
"""
import hashlib
import json
import struct
import sys
from pathlib import Path

import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import correct_sr44_little_blue_review as first  # noqa: E402
from bridge_geometry import box  # noqa: E402

BID = first.BID
BASE = ROOT / 'data/bridges' / BID
BACKUP = ROOT / 'data/fem_research'
TAG = 'drawing-review-2-guardrail-connections'
PREVIOUS_REVISION = first.REVISION
REVISION = '1.2-drawing-review-2'
FT, IN = first.FT, first.IN
PT = FT / 18                                       # sheet 18 elevations, 1/4 in = 1 ft

# Sheet 18 railing elevations: (TFC end, connector far edge, beam top, beam bottom, Top of Deck), PDF points.
SHEET18 = {(1, -1): (231.0, 276.0, 795.9, 825.9, 842.4),       # North Railing Elevation, west (MGS Without Curb)
           (1, 1): (1076.0, 1040.0, 797.0, 827.0, 842.4),      # North Railing Elevation, east (Type TGB)
           (-1, -1): (231.0, 276.0, 1155.9, 1185.9, 1202.4),   # South Railing Elevation, west
           (-1, 1): (1368.9, 1323.9, 1155.9, 1185.9, 1202.4)}  # South Railing Elevation, east
FACE_Y = first.RAIL_BACK - 9 * IN                  # TFC end face, 9 in from the rail back: 6.2738 m
RAIL_T = .06                                       # as-built strip thickness, kept
OLD_GAP = first.EXTENSION + .055                   # as built: the strip started 2 in + 55 mm beyond the TFC end
NAMES = {(1, -1): 'north-west', (1, 1): 'north-east', (-1, -1): 'south-west', (-1, 1): 'south-east'}


def connection(side, end):
    tfc_end_pt, far_pt, top_pt, bottom_pt, deck_pt = SHEET18[(side, end)]
    return dict(lap=abs(far_pt - tfc_end_pt) * PT, top=(deck_pt - top_pt) * PT, bottom=(deck_pt - bottom_pt) * PT)


def tfc_end(side, end):
    return first.CHAINS[side][0] if end < 0 else first.CHAINS[side][3]


def posts(side, end):
    """The four as-built posts of the representative run (correct_sr44_little_blue_review.guardrail)."""
    start = tfc_end(side, end) + end * first.EXTENSION
    edge = side * (first.COPING - .20)
    first_x = start + end * .055
    out = []
    for x in np.linspace(first_x, first_x + end * 2.0, 4):
        z = float(first.surface(x, edge))
        out.append(box(x - .055, x + .055, edge - .05, edge + .05, z - .25, z + .7))
    return out, first_x + end * 2.0


def rail_element(side, end, outer_x):
    """Upright rail element on the TFC end face plane, from the drawn lap to the end of the as-built run."""
    c = connection(side, end)
    x_in = tfc_end(side, end) - end * c['lap']
    y_back, y_front = side * FACE_Y, side * (FACE_Y - RAIL_T)
    s_at = lambda x: float(first.surface(x, y_back))  # noqa: E731
    xs = first.stations(x_in, outer_x)
    v = []
    for x in xs:
        s = s_at(x)
        v += [(x, y_back, s + c['bottom']), (x, y_front, s + c['bottom']),
              (x, y_front, s + c['top']), (x, y_back, s + c['top'])]
    faces = []
    for k in range(len(xs) - 1):
        for j in range(4):
            a, b = 4 * k + j, 4 * k + (j + 1) % 4
            faces += [[a, b, b + 4], [a, b + 4, a + 4]]
    last = 4 * (len(xs) - 1)
    faces += [[0, 2, 1], [0, 3, 2], [last, last + 1, last + 2], [last, last + 2, last + 3]]
    m = trimesh.Trimesh(np.array(v), np.array(faces), process=False)
    if m.volume < 0:
        m.invert()
    if not m.is_watertight or not m.is_winding_consistent or m.volume <= 0:
        raise ValueError('invalid rail element')
    return m, x_in


def correct():
    mp = BASE / 'model_manifest.json'
    raw_manifest = mp.read_bytes().decode('utf-8')
    newline = '\r\n' if '\r\n' in raw_manifest else '\n'
    final_newline = raw_manifest.endswith('\n')
    manifest = json.loads(raw_manifest)
    if manifest.get('review_correction_2') == TAG:
        print('Already corrected.')
        return
    path = BASE / 'model.glb'
    original = path.read_bytes()
    before = hashlib.sha256(original).hexdigest()

    def expect(ok, what):
        if not ok:
            raise ValueError(f'{BID}: unexpected starting model ({what})')

    expect(manifest.get('review_correction') == first.TAG and manifest.get('revision') == PREVIOUS_REVISION,
           'first review correction not applied')
    expect(before == manifest['review_correction_record']['after_glb_sha256'], 'GLB differs from the first correction')

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
        prim = meshes[pid]['primitives'][0]
        v = read(prim['attributes']['POSITION']).astype(np.float64)
        return trimesh.Trimesh(np.c_[v[:, 0], -v[:, 2], v[:, 1]], read(prim['indices']).reshape(-1, 3), process=False)

    # --- Starting state: TFC ends on the chains, guardrail runs exactly as the first correction built them. ---
    for (side, end) in SHEET18:
        b = native(f'TFC_{side}_{end}').bounds
        expect(abs(b[0 if end < 0 else 1, 0] - tfc_end(side, end)) < 1e-5, f'TFC_{side}_{end} end')
        old = native(f'guardrail_{side}_{end}')
        ref = first.guardrail(side, end)
        expect(len(old.vertices) == len(ref.vertices) and np.allclose(old.vertices, ref.vertices, atol=1e-5)
               and np.array_equal(old.faces, ref.faces), f'guardrail_{side}_{end} as built')
        strip = old.vertices[32:]
        gap = (strip[:, 0].min() - tfc_end(side, end)) if end > 0 else (tfc_end(side, end) - strip[:, 0].max())
        expect(abs(gap - OLD_GAP) < 5e-4, f'guardrail_{side}_{end} strip gap')
        expect(abs(np.ptp(strip[:, 1]) - .30) < 1e-4, f'guardrail_{side}_{end} flat strip')

    # --- New geometry. ---
    solids, records = {}, {}
    for (side, end) in SHEET18:
        pid = f'guardrail_{side}_{end}'
        old = native(pid)
        post_meshes, outer_x = posts(side, end)
        expect(np.allclose(np.vstack([p.vertices for p in post_meshes]), old.vertices[:32], atol=1e-5),
               f'{pid} posts')
        rail, x_in = rail_element(side, end, outer_x)
        m = trimesh.util.concatenate(post_meshes + [rail])
        if not m.is_watertight or not m.is_winding_consistent or m.volume <= 0:
            raise ValueError(f'{pid}: invalid corrected run')
        solids[pid] = m
        c = connection(side, end)
        records[pid] = dict(rail_x_m=sorted([round(x_in, 6), round(outer_x, 6)]), lap_on_tfc_m=round(c['lap'], 6),
                            top_above_deck_m=round(c['top'], 6), bottom_above_deck_m=round(c['bottom'], 6),
                            back_face_y_m=round(side * FACE_Y, 6))

    # --- GLB: replace only the four guardrail primitives with appended accessors. ---
    for pid, solid in solids.items():
        prim = meshes[pid]['primitives'][0]
        color = read(prim['attributes']['COLOR_0'])[0]
        v = np.asarray(solid.vertices, np.float64)
        glb = np.c_[v[:, 0], v[:, 2], -v[:, 1]].astype('<f4')
        prim['attributes'] = {'POSITION': append(glb, 'VEC3', 5126),
                              'COLOR_0': append(np.tile(color, (len(v), 1)).astype('u1'), 'VEC4', 5121)}
        gltf['accessors'][prim['attributes']['COLOR_0']]['normalized'] = True
        prim['indices'] = append(np.asarray(solid.faces).reshape(-1, 1).astype('<u4'), 'SCALAR', 5125)
        side, end = (int(k) for k in pid.split('_')[1:])
        c = connection(side, end)
        lap_txt = '2\'-0"' if abs(c['lap'] - 2 * FT) < 1e-9 else '2\'-6"'
        p = parts[pid]
        p['note'] = (
            f'Representative 2 m {NAMES[(side, end)]} run: four posts as built, and an upright rail element standing in '
            f'for the 20 in thrie beam and its terminal connector, back on the TFC end face (Y = {side * FACE_Y:+.4f} '
            f'm), lapping {lap_txt} onto the TFC, {c["bottom"] / IN:.2f} to {c["top"] / IN:.2f} in above the deck '
            '(sheet 18 north/south railing elevations, scaled). Corrugations, blockouts, bolts, the post layout and '
            'the rest of the ' + ('Type TGB guardrail transition, with its W-beam transition and curved terminal, '
                                  if (side, end) == (1, 1) else 'Type MGS Without Curb guardrail transition ') +
            'are not modelled.')
        p['basis'] = 'Sheet 18 railing elevations (terminal connector lap, thrie-beam depth and height); representative run'
        p['dimensions'].update(dict(rail_element_depth_m=round(c['top'] - c['bottom'], 6),
                                    rail_element_thickness_m=RAIL_T,
                                    rail_element_bottom_above_deck_m=round(c['bottom'], 6),
                                    rail_element_top_above_deck_m=round(c['top'], 6),
                                    lap_on_tfc_m=round(c['lap'], 6), back_face_y_m=round(side * FACE_Y, 6)))
        p['bounds_m'] = np.round(solid.bounds, 6).tolist()
        p['volume_m3'] = round(float(solid.volume), 9)
        meshes[pid]['extras'].update(p)

    gltf['buffers'][0]['byteLength'] = len(binary)
    while len(binary) % 4:
        binary.append(0)
    encoded = json.dumps(gltf, ensure_ascii=True, separators=(',', ':')).encode()
    encoded += b' ' * ((-len(encoded)) % 4)
    out = (struct.pack('<III', 0x46546c67, 2, 28 + len(encoded) + len(binary)) +
           struct.pack('<II', len(encoded), 0x4e4f534a) + encoded + struct.pack('<II', len(binary), 0x004e4942) + binary)
    BACKUP.mkdir(exist_ok=True)
    (BACKUP / f'{BID}_before_review_correction_2.glb').write_bytes(original)
    (BACKUP / f'{BID}_manifest_before_review_correction_2.json').write_bytes(mp.read_bytes())
    path.write_bytes(out)

    manifest['review_correction_2'] = TAG
    manifest['revision'] = REVISION
    manifest['review_correction_2_record'] = dict(
        source_pdf_pages=[12, 18], printed_sheets=[12, 18],
        findings={'F5': 'residual confirmed - steel guardrail connections stopped 105.8 mm short of the TFC ends',
                  'N1': 'confirmed - rail element laps onto each TFC end face (2 ft 6 in; NE 2 ft 0 in)',
                  'N2': 'confirmed - rail element upright, 20 in deep (11-31 in; NE 10.27-30.27 in above the deck)'},
        sheet18_points=dict(scale='1/4 in = 1 ft, 18 pt/ft', tfc_end_connector_far_beam_top_bottom_top_of_deck=
                            {NAMES[k]: list(v) for k, v in SHEET18.items()}),
        guardrail_rail_elements=records, previous_revision=PREVIOUS_REVISION,
        changed_parts=list(solids), before_glb_sha256=before, after_glb_sha256=hashlib.sha256(out).hexdigest())
    deviations = [d for d in manifest.get('known_deviations', []) if d.get('id') != 'guardrail-representative-runs']
    deviations.append(dict(
        id='guardrail-representative-runs', parts=', '.join(solids), source='sheets 12 and 18',
        deviation='Each guardrail transition is a representative 2 m run: four as-built 0.11 x 0.10 m posts at '
                  '0.667 m spacing, 29 mm behind the rail element with no blockouts, and a flat 0.06 m upright plate '
                  'for the thrie beam and terminal connector. The drawn post spacing, corrugations, bolts, the rest '
                  'of each transition and the NE Type TGB W-beam transition and curved terminal are not modelled.',
        reason='Guardrail transitions are standard roadway items (sheet 12, sheet 18 elevations); only their '
               'connection to the bridge railing is modelled to the drawings.'))
    manifest['known_deviations'] = deviations
    text = json.dumps(manifest, ensure_ascii=False, indent=2)
    mp.write_bytes(text.replace('\n', newline).encode('utf-8') + (newline.encode() if final_newline else b''))
    print(json.dumps({k: v for k, v in manifest['review_correction_2_record'].items()
                      if k not in ('findings', 'sheet18_points')}, indent=1))


if __name__ == '__main__':
    correct()

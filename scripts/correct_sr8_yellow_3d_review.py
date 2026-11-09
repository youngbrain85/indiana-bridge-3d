"""Fourth correction of SR 8 over Yellow River (sr8-yellow), from the 3D review of the assembled model. Runs after the
three drawing-review corrections:

    python scripts/correct_sr8_yellow_review.py      # revision 1.1
    python scripts/correct_sr8_yellow_review_2.py    # revision 1.2
    python scripts/correct_sr8_yellow_review_3.py    # revision 1.3-deviations
    python scripts/correct_sr8_yellow_3d_review.py   # this one (revision 1.4-3d-review)

Source: INDOT B-23076 (1997), data/bridges/sr8-yellow/drawings.pdf; PDF pages 1-20 are printed sheets 1-20. Native
axes as before: X station (east), Y north, Z = El. - 210.000; beam lines YS (south to north); deck top
D(X, Y) = 8.257 - X^2/15240 - 0.02|Y|.

SR8-S01 (RESOLVE, with a known deviation for the undetailed connection). The 54 retained diaphragms of Spans B, C and
D (diaphragm_1_*, diaphragm_2_*, diaphragm_3_*) are 460 x 130 mm channel envelopes that the generator stopped 150 mm
from each beam centre line: 142.65 mm short of both girder webs and 51-85 mm clear of the flanges, so none of them
touched a girder. The first three corrections rebuilt only the 24 new end-span MC460 diaphragms (shop sheet M1,
sheet 12 Detail "B"). The third correction sheared all 78 diaphragms with the beams it raised (the retained ones keep
their +83 / +117 mm offset from the girder mid-depth, as before), so the gap is not a by-product of that raise: it
is the generator's 150 mm setback, never corrected for the retained framing.
- Sheet 11 Framing Plan: "Exist. W460x67 Diaphragm (Typ.)" in Spans B, C and D, drawn framing beam line to beam line;
  "Exist. W840 x 193" girders (sheet 14 Half Section: "Existing W840 x 193 (Spans B, C & D)"). The W840x193 web is
  14.7 mm (the model's beams have their web faces at YS +/- 7.35 mm).
- No sheet of the bundle details the retained W460x67 diaphragms or their web connection. Sheet 12 Detail "B" and
  shop sheet M1 (PDF 25) cover only the new end-span MC460 diaphragms and are not applied here. Sheet 6 General Notes:
  "Plans for the existing structure are on file in the Central Office as Bridge File 8-75-4883 and 8-75-4883A".
- Each envelope is extended along its own axis (it is sheared with the beams, so its ends move along that line) to
  the web faces of the two girders it frames into: F/F 1458 mm (1473 bays) and 1763 mm (1778 bays). Its section,
  height and row station are unchanged. The extended ends stand for the undetailed connection; they are recorded as
  known deviation retained-diaphragm-connections.

54 parts change; none is added or removed; part ids are unchanged. Only the 54 meshes get new accessors; all other
buffers are kept. Requires numpy, trimesh and the earlier SR 8 correction scripts in the same folder.
"""
import hashlib
import json
import struct
import sys
from pathlib import Path

import numpy as np
import trimesh

sys.path.insert(0, str(Path(__file__).resolve().parent))
from correct_sr8_yellow_review import BASE, ROOT, YS, deck  # noqa: E402
from correct_sr8_yellow_review_3 import FILLET_A, beam_label, beam_no, shells  # noqa: E402
from correct_sr8_yellow_review_3 import REVISION as THIRD_REVISION  # noqa: E402
from correct_sr8_yellow_review_3 import TAG as THIRD_TAG  # noqa: E402

TAG = 'sr8-yellow-3d-review-2026-11'
REVISION = '1.4-3d-review'
BEFORE_SHA = 'c2440e9ecd63c29278648ec83f8a9c972d72f4d72c505a94e75ed49ff90b834a'   # after the third correction
SETBACK = 0.150                     # generator: retained diaphragm ends 150 mm from the beam centre lines
WEB_HALF = 0.00735                  # W840x193 web 14.7 mm (sheets 11, 14; the model's beams)
FLANGE_T = 0.022                    # model W840x193 flange thickness (web clear height check only)
W840 = 0.840
SPANS = (1, 2, 3)                   # Spans B, C, D: retained framing
DEVIATION_ID = 'retained-diaphragm-connections'


def correct():
    mp = BASE / 'model_manifest.json'
    manifest = json.loads(mp.read_text(encoding='utf-8'))
    if manifest.get('review_correction_3d') == TAG:
        print('Already corrected.')
        return
    if manifest.get('review_correction_3') != THIRD_TAG or manifest.get('revision') != THIRD_REVISION:
        raise ValueError('run scripts/correct_sr8_yellow_review_3.py first (revision 1.3-deviations expected)')
    path = BASE / 'model.glb'
    original = path.read_bytes()
    before = hashlib.sha256(original).hexdigest()
    if before != BEFORE_SHA or manifest['review_correction_record_3']['after_glb_sha256'] != BEFORE_SHA:
        raise ValueError('model.glb is not the output of the third correction')
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

    def expect(cond, what):
        if not cond:
            raise ValueError('Model is not in the expected state after the third correction: ' + what)

    def web_face(beam, y):
        """Exact (stored) Y of the beam web face nearest y."""
        ys = np.unique(beam.vertices[:, 1])
        k = np.argmin(np.abs(ys - y))
        expect(abs(ys[k] - y) < 2e-6, 'web face at Y = %.5f' % y)
        return float(ys[k])

    changes, measured = [], {}
    for i in SPANS:
        for row in range(3):
            for j in range(6):
                pid = f'diaphragm_{i}_{row}_{j}'
                expect(pid in parts and pid in meshes, pid)
                m = native(pid)
                v = m.vertices.copy()
                expect(len(v) == 16 and len(shells(m)) == 1 and m.is_watertight, pid + ' single channel envelope')
                y0, y1 = v[:, 1].min(), v[:, 1].max()
                expect(abs(y0 - (YS[j] + SETBACK)) < 2e-6 and abs(y1 - (YS[j + 1] - SETBACK)) < 2e-6,
                       pid + ' ends 150 mm from the beam centre lines')
                beams = (native(f'beam_{i}_{j}'), native(f'beam_{i}_{j + 1}'))
                wl, wr = web_face(beams[0], YS[j] + WEB_HALF), web_face(beams[1], YS[j + 1] - WEB_HALF)
                e0, e1 = np.nonzero(np.isclose(v[:, 1], y0, atol=1e-6))[0], np.nonzero(np.isclose(v[:, 1], y1, atol=1e-6))[0]
                expect(len(e0) == 8 and len(e1) == 8, pid + ' two end sections')

                def keys(idx):
                    z0 = v[idx, 2].min()
                    return {(round(v[k, 0], 5), round(v[k, 2] - z0, 4)): k for k in idx}
                k0, k1 = keys(e0), keys(e1)
                expect(set(k0) == set(k1) and len(k0) == 8, pid + ' prismatic (same section at both ends)')
                span = y1 - y0
                new = v.copy()
                for key in k0:                       # extend along the envelope's own (sheared) axis
                    a, b = k0[key], k1[key]
                    d = v[a] - v[b]
                    new[a] = v[a] + d * (y0 - wl) / span
                    new[b] = v[b] - d * (wr - y1) / span
                    new[a, 1], new[b, 1] = wl, wr
                solid = trimesh.Trimesh(new, m.faces, process=False)
                if not solid.is_watertight or solid.volume <= 0 or \
                        abs(solid.volume - m.volume * (wr - wl) / span) > 1e-9:
                    raise ValueError(pid + ': invalid extended envelope')
                # each end face must lie on the web between the flanges and within the beam's length
                for beam, k, idx in ((beams[0], j, e0), (beams[1], j + 1, e1)):
                    n = beam_no(k)
                    face = new[idx]
                    top = deck(face[:, 0], YS[k]) - FILLET_A[n]
                    if not (np.all(face[:, 2] < top - FLANGE_T - 0.02) and np.all(face[:, 2] > top - W840 + FLANGE_T + 0.02)
                            and beam.bounds[0, 0] + 0.1 < face[:, 0].min() and face[:, 0].max() < beam.bounds[1, 0] - 0.1):
                        raise ValueError(f'{pid}: end face not on the web of beam_{i}_{k}')
                    mid = deck(face[:, 0].mean(), YS[k]) - FILLET_A[n] - W840 / 2
                    measured.setdefault(pid, []).append(round(float(face[:, 2].mean() - mid), 4))
                prim = meshes[pid]['primitives'][0]
                meshes[pid]['primitives'] = [primitive(solid, read(prim['attributes']['COLOR_0'])[0])]
                ff = round(wr - wl, 4)
                p = parts[pid]
                p['bounds_m'] = np.round(solid.bounds, 6).tolist()
                p['volume_m3'] = round(float(solid.volume), 9)
                p['dimensions'].update(length_m=ff, ends='girder web faces (schematic connection)')
                p['pdf_pages'] = [6, 11, 14]
                p['basis'] = ('Representative 460 x 130 mm channel envelope spanning web face to web face at a simplified '
                              'row station; the W460x67 section and its web connection are not detailed in the bundle')
                p['note'] = (p['note'] + ' Fourth correction (3D review SR8-S01): the envelope stopped 150 mm from each '
                             f'beam centre line, 143 mm short of the webs of {beam_label(j)} and {beam_label(j + 1)}, and '
                             f'touched neither girder. It is extended along its own axis to both web faces (W840x193 web '
                             f'14.7 mm; existing W840x193 in Spans B, C and D per sheets 11 and 14), {ff * 1000:.0f} mm face '
                             f'to face (was {span * 1000:.0f} mm). Sheet 11 shows the existing W460x67 diaphragms (Typ.) '
                             f'framing beam to beam but no connection detail; sheet 12 Detail "B" and shop sheet M1 cover '
                             f'only the new end-span MC460 diaphragms. The extended ends stand for that undetailed '
                             f'connection: known_deviations {DEVIATION_ID}.').strip()
                meshes[pid]['extras'].update(p)
                changes.append(pid)
    expect(len(changes) == 54, '54 retained diaphragms')
    others = [pid for pid in parts if pid.startswith('diaphragm_') and pid not in changes]
    expect(len(others) == 24 and all(pid.split('_')[1] in ('0', '4') for pid in others), '24 end-span diaphragms')
    offs = np.array([o for pair in measured.values() for o in pair])

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
    (backup / 'sr8_yellow_before_3d_review.glb').write_bytes(original)
    (backup / 'sr8_yellow_manifest_before_3d_review.json').write_bytes(mp.read_bytes())
    path.write_bytes(out)
    manifest['review_correction_3d'] = TAG
    manifest['revision'] = REVISION
    manifest['review_correction_record_3d'] = dict(
        source_pdf_pages=[6, 11, 12, 14, 25],
        printed_sheets='PDF pages 1-20 are printed sheets 1-20; PDF 25 is shop sheet M1 (new end-span diaphragms only)',
        findings={
            'SR8-S01': 'RESOLVE: the 54 retained diaphragms of Spans B, C and D stopped 150 mm from the beam centre lines '
                       '(142.65 mm short of both webs, 51-85 mm clear of the flanges) and touched no girder. Each channel '
                       'envelope is extended along its own axis to the two web faces it frames into (F/F 1458 / 1763 mm), '
                       'so both ends bear on the webs over the full 460 mm depth. The 24 end-span MC460 assemblies '
                       'already touched both webs through their M1H1 angles and are unchanged.'},
        decisions={
            'connection': 'Sheet 11 shows the existing W460x67 diaphragms framing beam line to beam line but no sheet '
                          'details their web connection; the shop-sheet MC460 angles (M1, sheet 12 Detail "B") belong to '
                          'the new end spans and are not copied. The envelope runs to the web faces and its ends stand '
                          'for the undetailed connection (known_deviations retained-diaphragm-connections).',
            'third correction': 'Not the cause: the third correction sheared every diaphragm with the beams it raised '
                                '(about 2 mm less than the beams at the old ends, which lay 150 mm inside the beam lines). '
                                'The retained envelopes keep their level section %+.0f to %+.0f mm above the girder '
                                'mid-depth, as generated; height, section and row stations are not changed.'
                                % (offs.min() * 1000, offs.max() * 1000)},
        changed_parts=changes, removed_parts=[], added_parts=[],
        before_glb_sha256=before, after_glb_sha256=hashlib.sha256(out).hexdigest())
    manifest['known_deviations'] = [d for d in manifest.get('known_deviations', []) if d.get('id') != DEVIATION_ID] + [
        dict(id=DEVIATION_ID, parts='diaphragm_1_*, diaphragm_2_*, diaphragm_3_* (54 retained diaphragms)',
             source='sheet 11 Framing Plan ("Exist. W460x67 Diaphragm (Typ.)", diaphragm spacing), sheet 14 Half Section '
                    '("Existing W840 x 193 (Spans B, C & D)"), sheet 6 General Notes',
             deviation='The retained W460x67 diaphragms are a 460 x 130 mm channel envelope (14 mm web and flanges) that '
                       'runs from girder web face to web face (F/F 1458 / 1763 mm), level across each bay %.0f-%.0f mm '
                       'above the girder mid-depth, at the simplified row stations. The extended ends stand for the web '
                       'connection; the W460x67 section, its connection plates or angles, bolts or welds, copes and its '
                       'height on the web are not modelled.' % (offs.min() * 1000, offs.max() * 1000),
             reason='The 1997 bundle details only the new end-span framing (sheet 12 Detail "B", shop sheet M1); no sheet '
                    'details the retained diaphragms or their connections, and the 2026 reference (B-43353) is a deck '
                    'overlay with no steel details. Sheet 6 General Notes point to the plans of the existing structure, '
                    'Bridge File 8-75-4883 and 8-75-4883A, which are not in the bundle; they (or a field survey) would '
                    'settle the section, connection and height.')]
    mp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in manifest['review_correction_record_3d'].items()
                      if k not in ('changed_parts', 'findings', 'decisions')}))
    print(f'{len(changes)} parts changed, 0 added, 0 removed; retained diaphragm offsets from the girder mid-depth '
          f'{offs.min() * 1000:+.1f} to {offs.max() * 1000:+.1f} mm')


if __name__ == '__main__':
    correct()

"""Second drawing-confirmed correction of US 35 over Deer Creek (us35-deer): handedness, wing tops and crowned
closure tops. Runs after scripts/correct_us35_deer_review.py and keeps the GLB buffers it does not replace.

    python scripts/correct_us35_deer_review_2.py [--base DIR] [--backup DIR]

Source: drawings.pdf (INDOT B-45063 / Des 1900048, document 9721578); printed sheet numbers equal PDF page numbers.
Native axes after this correction: X along increasing station (east, X = 0 at Sta. 1271+60), Y transverse and
positive to the LEFT of increasing station (north), Z up from El. 837.11. This is the right-handed frame that the
manifest's glb_axes mapping (native X, native Z, -native Y) assumes. The bent lines are q = X - tan(15 deg) Y.

1. Handedness (second-check N1; completes F3 and F5). Sheet 11 GENERAL PLAN: the north arrow points up the sheet,
   stations increase to the right (Sta. 1270+76.06 ... 1272+43.94), so north is left of increasing station (+Y).
   Wings B and D are on the north side, A and C on the south side. The bent lines run up-station toward the north:
   the north end of each bent is at the higher station. Sheet 13 (plan, with north arrows for Bent 1 and Bent 2):
   Beam 1 is on the north side, next to Wing B at Bent 1 and Wing D at Bent 2. Sheets 14 and 17 confirm the sense
   of the skew on the +2.35 % grade: at Bent 1 the north wing top (Wing B, El. 851.45) and the Beam 1 seat (846.08)
   are higher than the south ones (Wing A, 851.21; Beam 4, 845.88); at Bent 2 the same holds (Wing D 854.16 against
   Wing C 853.91; Beam 1 seat 848.78 against Beam 4 848.59). The model was built with north at Y < 0 (Beam 1 at
   Y = -4.6482) and bent lines X = q - tan(15) Y, so in the right-handed frame it was the exact mirror image of the
   drawings: both the transverse layout and the skew sense were reversed. Every vertex is reflected,
   (X, Y, Z) -> (X, -Y, Z), and every triangle's winding is reversed. Grade, crown, stations, elevations and all
   dimensions are unchanged. Part ids are unchanged and keep their geographic meaning: beam_0_0 / B*_bearing_1 are
   still Beam 1 (north); suffix -1 still names the north member (wing_0_-1 = Wing B, wing_1_-1 = Wing D,
   FC_rail_-1, TFC_transition_*_-1, extension_*_-1) and suffix 1 the south member, now at Y > 0 and Y < 0
   respectively.
2. Wing tops (second-check N2). Sheets 14 and 17 (WINGWALL DETAILS elevation, T/El.): the top of each wing on the
   centre line of the bent is El. 851.21 (Wing A), 851.45 (Wing B), 853.91 (Wing C) and 854.16 (Wing D), and at the
   tip it is "Match Top of RCBA Elevation". The model's wings followed the deck surface extended past the coping,
   less 0.09 m, so they were 0.093-0.101 m low. Each wing top is now straight and level across the 1 ft wall: it
   passes through the T/El. at the bent centre line (wall mid-thickness) and runs parallel to the +2.35 % grade
   (sheet 11) to the tip, so that it meets the approach slab and its extension at the coping line (sheets 11, 25).
   Plan outline and bottom (El. 841.88 / 844.59, sheet 17) are unchanged.
3. Crowned closure tops (second-check N3; completes F1). The two closure bays that straddle the bridge centre line,
   integral_infill_0_4 and integral_infill_1_4, had a flat top between the flanges of Beams 2 and 3, which left an
   18.5 mm wedge below the crowned deck soffit at the centre line (sheets 12, 14, 15: the integral concrete is
   placed up to the deck). Their tops now carry a vertex at the centre line and follow the soffit (deck top - 8 in).
   The two back faces backwall_0 / backwall_1 had the same flat top across the full bent: under the approach slabs,
   which revision 1.1 gave the 2 % crown, it left a gap of up to 25 mm over the centre 2.5 m (sheet 25 PAVEMENT
   LEDGE DETAIL: the RCBA bears on the end bent). Their tops get the same centre-line vertex and the model's rule
   (soffit level, crowned), as before revision 1.1 they overlapped the slab everywhere.

Deferred (known deviation added): the 25 mm display gap at the Type IA joint between the deck end and the approach
slab (the joint is given by INDOT Standard Drawing E 609-BRJT-01, not in this plan set). Not changed: everything
else; the TFC transition envelopes keep their known deviation.

Requires numpy and trimesh, plus scripts/correct_us35_deer_review.py (constants and helpers).
"""
import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import correct_us35_deer_review as first  # noqa: E402

BID = first.BID
BASE = ROOT / 'data/bridges' / BID
BACKUP = ROOT / 'data/fem_research'
TAG = 'drawing-review-2-handedness-wing-tops-crowned-closures'
PREVIOUS_REVISION = first.REVISION
REVISION = '1.2-drawing-review-2'
FT, IN, TAN, SLAB, TOL = first.FT, first.IN, first.TAN, first.SLAB, first.TOL
DATUM_EL = 837.11                          # Z = 0, flowline (sheet 11)
GRADE = .0235                              # sheet 11, structure built on grade +2.35 %
WING_TOP_EL = {'Wing A': 851.21, 'Wing B': 851.45, 'Wing C': 853.91, 'Wing D': 854.16}    # sheets 14, 17 T/El.
# Corrected frame: north (+Y) wings and their part ids (sheet 11 plan, sheet 13 plan).
WINGS = {'wing_0_-1': ('Wing B', 0, 1), 'wing_0_1': ('Wing A', 0, -1),
         'wing_1_-1': ('Wing D', 1, 1), 'wing_1_1': ('Wing C', 1, -1)}
# Approach-slab edges in the corrected frame (sheets 11, 25): west 18'-3" north / 17'-8" south, east reversed.
RCBA_EDGE = {(0, 1): (18 + 3 / 12) * FT, (0, -1): (17 + 8 / 12) * FT,
             (1, 1): (17 + 8 / 12) * FT, (1, -1): (18 + 3 / 12) * FT}
ORIENT_NOTE = 'Rev. 1.2: reflected to the drawn side, north (Beam 1, Wings B and D) = +Y, left of increasing station ' \
              '(sheets 11, 13, 14).'


def surface(x, y):
    return first.surface(x, y)


def q_new(v):
    """Bent-line coordinate in the corrected frame: constant along a bent line."""
    return v[:, 0] - TAN * v[:, 1]


def sx_new(u, y):
    return u + TAN * np.asarray(y)


def el(z):
    return DATUM_EL + z / FT


def top_z(mesh, xy):
    """Highest Z of a closed mesh above each XY point (upward-facing triangles, barycentric), NaN outside."""
    tri = mesh.triangles
    up = mesh.face_normals[:, 2] > 1e-9
    tri = tri[up]
    out = np.full(len(xy), np.nan)
    a, b, c = tri[:, 0], tri[:, 1], tri[:, 2]
    det = (b[:, 1] - c[:, 1]) * (a[:, 0] - c[:, 0]) + (c[:, 0] - b[:, 0]) * (a[:, 1] - c[:, 1])
    for i, (x, y) in enumerate(xy):
        l1 = ((b[:, 1] - c[:, 1]) * (x - c[:, 0]) + (c[:, 0] - b[:, 0]) * (y - c[:, 1])) / det
        l2 = ((c[:, 1] - a[:, 1]) * (x - c[:, 0]) + (a[:, 0] - c[:, 0]) * (y - c[:, 1])) / det
        l3 = 1 - l1 - l2
        inside = (l1 >= -1e-9) & (l2 >= -1e-9) & (l3 >= -1e-9)
        if inside.any():
            out[i] = (l1 * a[:, 2] + l2 * b[:, 2] + l3 * c[:, 2])[inside].max()
    return out


def bottom_z(mesh, xy):
    flipped = trimesh.Trimesh(vertices=mesh.vertices * [1, 1, -1], faces=mesh.faces[:, ::-1], process=False)
    return -top_z(flipped, xy)


def correct(base=BASE, backup=BACKUP):
    mp = base / 'model_manifest.json'
    raw_manifest = mp.read_bytes()
    manifest = json.loads(raw_manifest)
    if manifest.get('review_correction_2') == TAG:
        print('Already corrected.')
        return
    path = base / 'model.glb'
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
    expect(set(parts) == set(meshes) and len(meshes) == 72, 'part list')
    expect(not any(k in n for n in gltf['nodes'] for k in ('matrix', 'rotation', 'translation', 'scale')),
           'node transforms')

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

    # ---- Read every part in the old (mirrored) frame and check the starting state. ----
    old = {}
    for pid, m in meshes.items():
        expect(len(m['primitives']) == 1 and set(m['primitives'][0]['attributes']) == {'POSITION', 'COLOR_0'},
               f'{pid} primitive')
        prim = m['primitives'][0]
        mesh = trimesh.Trimesh(vertices=first.to_native(read(prim['attributes']['POSITION']).astype(np.float64)),
                               faces=read(prim['indices']).reshape(-1, 3), process=False)
        expect(mesh.is_watertight and mesh.volume > 0, f'{pid} not a closed solid')
        old[pid] = mesh

    def centre(pid):
        return old[pid].vertices.min(axis=0) / 2 + old[pid].vertices.max(axis=0) / 2

    expect(abs(centre('beam_0_0')[1] + 15.25 * FT) < TOL, 'Beam 1 not at Y = -4.6482 (old frame)')
    expect(abs(centre('beam_0_3')[1] - 15.25 * FT) < TOL, 'Beam 4 not at Y = +4.6482 (old frame)')
    expect(centre('B1_bearing_1')[0] > centre('B1_bearing_4')[0] and
           centre('B1_bearing_1')[2] > centre('B1_bearing_4')[2], 'bearing order')
    for b, k in first.BENTS.items():
        cv = old[f'cap_{b + 1}'].vertices
        expect(abs(np.ptp(first.q_of(cv)) - 2 * first.HALF_THICK) < TOL, f'cap_{b + 1} not on q = X + tan15 Y')
        expect(abs(cv[:, 1].min() + first.CAP_HALF_Y - k['shift'][1]) < TOL, f'cap_{b + 1} offset')
    for name, (plan, b, _) in WINGS.items():
        expect(parts[name]['dimensions'].get('plan_name') == plan, f'{name} plan name')
        v = old[name].vertices
        top = v[:, 2] > v[:, 2].min() + .5
        expect(len(v) == 8 and top.sum() == 4, f'{name} topology')
        expect(np.abs(v[top, 2] - (surface(v[top, 0], v[top, 1]) - first.WING_DROP)).max() < TOL, f'{name} top rule')
        expect((v[:, 1].mean() < 0) == (plan in ('Wing B', 'Wing D')), f'{name} side (old frame)')
    for pid in ('integral_infill_0_4', 'integral_infill_1_4', 'backwall_0', 'backwall_1'):
        v = old[pid].vertices
        top = v[:, 2] > v[:, 2].min() + .5
        expect(len(v) == 8 and np.abs(v[top, 2] - (surface(v[top, 0], v[top, 1]) - SLAB)).max() < TOL,
               f'{pid} flat top at the soffit')
    expect(np.abs(np.unique(old['deck'].vertices[:, 1].round(4))).tolist() == [5.842, 0.0, 5.842], 'deck crown')

    # ---- 1. Reflect every part: (X, Y, Z) -> (X, -Y, Z), winding reversed. ----
    new = {pid: trimesh.Trimesh(vertices=m.vertices * [1, -1, 1], faces=m.faces[:, [0, 2, 1]], process=False)
           for pid, m in old.items()}
    for pid, m in new.items():
        expect(m.is_watertight and m.is_winding_consistent and abs(m.volume - old[pid].volume) < 1e-9,
               f'{pid} reflection')

    rebuilt, records = {}, {}
    # ---- 2. Wing tops: T/El. at the bent centre line, parallel to the +2.35 % grade (sheets 11, 14, 17). ----
    for pid, (plan, b, side) in WINGS.items():
        m = new[pid]
        v = m.vertices.copy()
        expect(np.sign(v[:, 1].mean()) == side, f'{pid} not on the drawn side after reflection')
        u = first.BENTS[b]['u']
        yc = (v[:, 1].min() + v[:, 1].max()) / 2
        x_cl = float(sx_new(u, yc))
        z_cl = (WING_TOP_EL[plan] - DATUM_EL) * FT
        top = v[:, 2] > v[:, 2].min() + .5
        old_top_cl = z_cl - (surface(x_cl, yc) - first.WING_DROP)
        v[top, 2] = z_cl + GRADE * (v[top, 0] - x_cl)
        wing = trimesh.Trimesh(vertices=v, faces=m.faces, process=False)
        expect(wing.is_watertight and wing.volume > 0, f'{pid} rebuilt')
        q = q_new(v)
        tip_q = q.min() if b == 0 else q.max()
        x_tip = float(sx_new(tip_q, yc))
        z_tip = z_cl + GRADE * (x_tip - x_cl)
        rcba = float(surface(x_tip, side * RCBA_EDGE[(b, side)]))
        coping = float(surface(x_tip, side * first.WIDTH / 2))
        rebuilt[pid] = wing
        records[pid] = dict(plan_name=plan, top_el_at_bent_cl_ft=WING_TOP_EL[plan], bent_cl_x_m=round(x_cl, 6),
                            top_el_at_tip_ft=round(el(z_tip), 3), tip_x_m=round(x_tip, 6),
                            raised_at_bent_cl_m=round(float(old_top_cl), 6),
                            rcba_edge_top_el_at_tip_ft=round(el(rcba), 3),
                            approach_top_at_coping_el_at_tip_ft=round(el(coping), 3))
        parts[pid]['dimensions'].update(top_el_at_bent_cl_ft=WING_TOP_EL[plan], top_el_at_tip_ft=round(el(z_tip), 3),
                                        top_grade='+2.35 % along the roadway, level across the wall')
        parts[pid]['note'] += (f' Top El. {WING_TOP_EL[plan]} at the bent centre line (sheets 14, 17 T/El.; was '
                               f'{old_top_cl:.3f} m lower), straight at +2.35 % to El. {el(z_tip):.3f} at the tip, '
                               'where it meets the approach slab and extension at the coping line ("Match Top of RCBA '
                               'Elevation", sheets 11, 17, 25).')
        parts[pid]['pdf_pages'] = sorted(set(parts[pid]['pdf_pages']) | {11, 14, 17, 25})
        print(f'{pid} ({plan}): Y [{v[:, 1].min():.6f}, {v[:, 1].max():.6f}], top El. {WING_TOP_EL[plan]} at '
              f'X={x_cl:.4f} (+{old_top_cl:.4f} m), El. {el(z_tip):.3f} at the tip (RCBA edge {el(rcba):.3f}, '
              f'coping line {el(coping):.3f})')

    # ---- 3. Crowned closure tops: add the centre-line vertex (sheets 12, 14, 15, 25). ----
    crown_caps = [(0, 1, 4), (0, 4, 5), (1, 2, 3), (1, 3, 4)]
    for pid in ('integral_infill_0_4', 'integral_infill_1_4', 'backwall_0', 'backwall_1'):
        m = new[pid]
        v = m.vertices
        y0, y1 = v[:, 1].min(), v[:, 1].max()
        q0, q1 = q_new(v).min(), q_new(v).max()
        seat = v[:, 2].min()
        expect(y0 < 0 < y1 and np.ptp(q_new(v)) > .1, f'{pid} limits')
        solid = first.prism([q0, q1], [(y0, 0), (0.0, 0), (y1, 0), (y1, 1), (0.0, 1), (y0, 1)],
                            lambda s, y, h: (sx_new(s, y), y,
                                             seat * (1 - h) + (surface(sx_new(s, y), y) - SLAB) * h),
                            caps=crown_caps)
        kept = np.array([np.abs(solid.vertices - p).max(axis=1).min() for p in v])
        expect(kept.max() < TOL and len(solid.vertices) == 12, f'{pid} perimeter not kept')
        lift = float(surface(sx_new(q0, 0.0), 0.0) - SLAB - (np.interp(0.0, [y0, y1], [
            surface(sx_new(q0, y0), y0), surface(sx_new(q0, y1), y1)]) - SLAB))
        rebuilt[pid] = solid
        records[pid] = dict(y_m=[round(float(y0), 6), round(float(y1), 6)], q_m=[round(float(q0), 6), round(float(q1), 6)],
                            centre_line_rise_m=round(lift, 6))
        parts[pid]['dimensions'].update(crowned_top=True)
        if pid.startswith('integral'):
            parts[pid]['note'] += (f' Top crowned with a centre-line vertex to follow the deck soffit (the flat top '
                                   f'left a {lift * 1000:.1f} mm wedge below it at the centre line), sheets 12, 14, 15.')
        else:
            slab = new[f'approach_{-1 if pid.endswith("0") else 1}']
            xy = np.array([(x, y) for x in np.linspace(v[:, 0].min(), v[:, 0].max(), 30)
                           for y in np.linspace(-5.3, 5.3, 41)])
            t, s = top_z(m, xy), bottom_z(slab, xy)
            gap = float(np.nanmax(s - t))
            records[pid]['gap_below_approach_slab_before_m'] = round(gap, 6)
            parts[pid]['note'] += (f' Top crowned with a centre-line vertex, at soffit level as before revision 1.1 '
                                   f'(the flat top left a gap of up to {gap * 1000:.1f} mm below the crowned approach '
                                   'slab), sheets 12, 25.')
        parts[pid]['pdf_pages'] = sorted(set(parts[pid]['pdf_pages']) | ({12, 25} if pid.startswith('back')
                                                                          else {12, 14, 15}))
        print(f'{pid}: Y [{y0:.6f}, {y1:.6f}], q [{q0:.6f}, {q1:.6f}], centre line raised {lift:.6f} m')

    # ---- Checks in the corrected frame. ----
    final = {**new, **rebuilt}
    for pid in ('integral_infill_0_4', 'integral_infill_1_4'):
        lo, hi = final[pid].bounds
        xs = np.linspace(lo[0] + .05, hi[0] - .05, 25)
        ys = np.linspace(lo[1] + .01, hi[1] - .01, 25)
        xy = np.array([(x, y) for x in xs for y in ys])
        t, s = top_z(final[pid], xy), bottom_z(final['deck'], xy)
        ok = ~np.isnan(t) & ~np.isnan(s)
        expect(ok.sum() > 50 and np.abs(t[ok] - s[ok]).max() < 1e-4, f'{pid} roof does not meet the soffit')
    for b, pid in ((0, 'backwall_0'), (1, 'backwall_1')):
        lo, hi = final[pid].bounds
        xy = np.array([(x, y) for x in np.linspace(lo[0], hi[0], 30) for y in np.linspace(-5.3, 5.3, 41)])
        t, s = top_z(final[pid], xy), bottom_z(final[f'approach_{2 * b - 1}'], xy)
        ok = ~np.isnan(t) & ~np.isnan(s)
        expect(ok.sum() > 50 and (s[ok] - t[ok]).max() < 1e-6, f'{pid} leaves a gap under the approach slab')
    expect(abs(final['beam_0_0'].bounds.mean(axis=0)[1] - 15.25 * FT) < TOL
           and abs(final['beam_0_3'].bounds.mean(axis=0)[1] + 15.25 * FT) < TOL, 'Beam 1 not north (+Y)')
    for end, (b, north) in ((-1, (0, 18.25 * FT)), (1, (1, (17 + 8 / 12) * FT))):
        expect(abs(final[f'approach_{end}'].bounds[1][1] - north) < TOL, f'approach_{end} north edge')
    for b in (1, 2):
        cv = final[f'cap_{b}'].vertices
        expect(abs(np.ptp(q_new(cv)) - 2 * first.HALF_THICK) < TOL, f'cap_{b} not on q = X - tan15 Y')
    for pid, m in final.items():
        expect(m.is_watertight and m.is_winding_consistent and m.volume > 0, f'{pid} final solid')

    # ---- Write: reflected positions and reversed indices for every part, rebuilt parts in full. ----
    pos_map, idx_map = {}, {}
    for pid, m in final.items():
        prim = meshes[pid]['primitives'][0]
        a_pos, a_idx, a_col = prim['attributes']['POSITION'], prim['indices'], prim['attributes']['COLOR_0']
        if pid in rebuilt:
            prim['attributes']['POSITION'] = append(first.to_gltf(m.vertices).astype('<f4'), 'VEC3', 5126)
            if len(m.vertices) != gltf['accessors'][a_col]['count']:
                color = read(a_col)[0]
                prim['attributes']['COLOR_0'] = append(np.tile(color, (len(m.vertices), 1)).astype('u1'), 'VEC4', 5121)
                gltf['accessors'][prim['attributes']['COLOR_0']]['normalized'] = True
            prim['indices'] = append(m.faces.reshape(-1, 1).astype('<u4'), 'SCALAR', 5125)
        else:
            if a_pos not in pos_map:          # float32 negation is exact
                stored = read(a_pos)
                pos_map[a_pos] = append((stored * np.array([1, 1, -1], dtype='<f4')).astype('<f4'), 'VEC3', 5126)
            if a_idx not in idx_map:          # shared index accessors are reversed once
                idx_map[a_idx] = append(read(a_idx).reshape(-1, 3)[:, [0, 2, 1]].reshape(-1, 1).astype('<u4'),
                                        'SCALAR', 5125)
            prim['attributes']['POSITION'], prim['indices'] = pos_map[a_pos], idx_map[a_idx]
        p = parts[pid]
        if pid in rebuilt:
            p['bounds_m'] = m.bounds.round(6).tolist()
            p['volume_m3'] = round(float(m.volume), 9)
        else:
            (x0, y0, z0), (x1, y1, z1) = p['bounds_m']
            p['bounds_m'] = [[x0, round(-y1, 6) + 0.0, z0], [x1, round(-y0, 6) + 0.0, z1]]
            expect(np.abs(np.array(p['bounds_m']) - m.bounds).max() < 2e-5, f'{pid} manifest bounds')
        p['note'] = (p.get('note', '') + ' ' + ORIENT_NOTE).strip()
        extras = meshes[pid]['extras']
        if pid in rebuilt:
            extras.update(p)
        else:
            extras.update({k: p[k] for k in extras if k in p})

    for item in manifest.get('detail_coverage', []):
        if item.get('feature') == 'Whole proposed Bulb-T crossing':
            item['detail'] += (' North (Beam 1) is +Y, left of increasing station, and the north end of each bent '
                               'is up-station (sheets 11, 13, 14; reflected in revision 1.2).')
        elif item.get('feature') == 'Integral support topology':
            item['detail'] += (' Wing tops at the sheet 17 T/El. on the bent centre line, parallel to the grade; '
                               'centre closure bays and back faces crowned (revision 1.2).')
        for s in ('Primary PDF p.13', 'Primary PDF p.14'):
            if item.get('feature') == 'Whole proposed Bulb-T crossing' and s not in item['sources']:
                item['sources'].append(s)

    while len(binary) % 4:
        binary.append(0)
    gltf['buffers'][0]['byteLength'] = len(binary)
    encoded = json.dumps(gltf, ensure_ascii=True, separators=(',', ':')).encode()
    encoded += b' ' * ((-len(encoded)) % 4)
    out = (struct.pack('<III', 0x46546c67, 2, 28 + len(encoded) + len(binary)) +
           struct.pack('<II', len(encoded), 0x4e4f534a) + encoded + struct.pack('<II', len(binary), 0x004e4942) + binary)
    backup.mkdir(parents=True, exist_ok=True)
    (backup / f'{BID}_before_review_correction_2.glb').write_bytes(original)
    (backup / f'{BID}_manifest_before_review_correction_2.json').write_bytes(raw_manifest)
    path.write_bytes(out)

    manifest['review_correction_2'] = TAG
    manifest['revision'] = REVISION
    manifest['review_correction_2_record'] = dict(
        source_pdf_pages=[11, 12, 13, 14, 15, 17, 25], printed_sheets=[11, 12, 13, 14, 15, 17, 25],
        previous_revision=PREVIOUS_REVISION,
        native_axes='X along increasing station (east, X = 0 at Sta. 1271+60), Y positive to the left of increasing '
                    'station (north), Z up from El. 837.11; bent lines q = X - tan(15 deg) Y',
        frame_note='Coordinates quoted in review_correction_record (revision 1.1) are in the previous, mirrored frame '
                   '(north at Y < 0, q = X + tan(15 deg) Y); negate Y to compare them with this revision.',
        findings={
            'N1': 'confirmed - the whole model was the mirror image of the drawings (north at Y < 0 and north bent '
                  'ends down-station); every vertex reflected (X, Y, Z) -> (X, -Y, Z), winding reversed (sheets 11, '
                  '13, 14, 17)',
            'F3': 'completed by N1 - the 7 in bent offset now lies toward Beam 1 on the north (+Y) side at Bent 1 and '
                  'toward Beam 4 on the south side at Bent 2',
            'F5': 'sides completed by N1 (west slab 18\'-3" north = +Y); the 25 mm display joint at the Type IA joint '
                  'is deferred (known deviation approach-display-joint)',
            'N2': 'confirmed - wing tops raised 0.089-0.105 m to the sheet 17 T/El. at the bent centre line, straight '
                  'at +2.35 % to the tip',
            'N3 / F1': 'confirmed - centre closure bays crowned to the deck soffit (were 18.5 mm low at the centre '
                       'line); the back faces get the same crown vertex (were up to 25 mm below the approach slab '
                       'crowned in revision 1.1)'},
        part_side_suffixes='Part ids keep their geographic meaning: suffix -1 = north member (now Y > 0), suffix 1 = '
                           'south member (now Y < 0); beam_0_0 and B*_bearing_1 are Beam 1 (north).',
        values=records, reflected_parts=sorted(final), rebuilt_parts=sorted(rebuilt),
        before_glb_sha256=before, after_glb_sha256=hashlib.sha256(out).hexdigest())
    deviations = [d for d in manifest.get('known_deviations', []) if d.get('id') != 'approach-display-joint']
    deviations.append(dict(
        id='approach-display-joint', parts='approach_-1, approach_1, joint_-1, joint_1',
        source='sheets 11, 25 (PDF 11, 25)',
        deviation='The skewed near edge of each approach slab is 25 mm beyond the deck end (q = -/+17.9193 m against '
                  '-/+17.8943 m), a display joint; the Type IA joint itself has no width in the plan set.',
        reason='The Type IA joint is detailed in INDOT Standard Drawing E 609-BRJT-01 (sheet 25 note 4), which is not '
               'part of this plan set.'))
    manifest['known_deviations'] = deviations
    text = json.dumps(manifest, indent=2)
    if b'\r\n' in raw_manifest:
        text = text.replace('\n', '\r\n')
    if raw_manifest.endswith(b'\n'):
        text += '\r\n' if b'\r\n' in raw_manifest else '\n'
    mp.write_bytes(text.encode('utf-8'))
    print(json.dumps({k: v for k, v in manifest['review_correction_2_record'].items()
                      if k not in ('findings', 'values', 'reflected_parts')}, indent=1))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--base', type=Path, default=BASE, help='bridge folder (default: the repository copy)')
    parser.add_argument('--backup', type=Path, default=BACKUP, help='backup folder')
    args = parser.parse_args()
    correct(args.base, args.backup)

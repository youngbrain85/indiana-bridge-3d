"""One-time, drawing-confirmed corrections from the external model review of Virginia Avenue over I-65 NB / I-70 EB,
preserving unrelated GLB buffers.

    python scripts/correct_virginia_avenue_review.py

Primary set: INDOT B-44576 (document 9683637, drawings.pdf); printed sheet numbers equal PDF page numbers.
Historical set: existing plans 9548460 (2013 Girder 1 replacement, printed sheets 10 and 14 = PDF 28 and 32;
1971 framing plan S-7 = PDF 65).

The model is built in skew coordinates: X = u - tan(44 deg 19 min 06 sec) * Y, X increasing station (X = 0 at
13+48.31 "Vir"), Y transverse and positive to the LEFT looking up-station (right-handed, Z up). Each corrected part is
regenerated with the reconstruction rules of scripts/build_remaining_virginia_slab.py (girders 50 mm below the deck
soffit, bearings under the girders, abutment seat at the lowest bearing, and so on); only the inputs below change.
This script first rebuilds the uncorrected geometry with the same rules and requires it to match the GLB, so it raises
if the model is not in the expected state.

F1, sheets 31, 36 and 37 (plan, typical sections, fillet reinforcing detail) and existing sheet 10 (PDF 28, framing
plan): stations increase to the right, so plan-top is the left side looking up-station. The 16'-1" shared-use path
(south side, north arrow tip to the lower right), Girder No. 1 (the 2013 54" replacement, "G: place shear studs, Beam
No. 1 only") and the Type TX rail with the ornamental top rail are at plan-top / section-left; Girder No. 9 and the
6'-1" north sidewalk are at plan-bottom. The abutment lines run from plan-top-left to plan-bottom-right, so at
Abutment 1 the Girder 1 bearing is 18.156 m behind (lower station than) the Girder 9 bearing. The model had the
transverse arrangement mirrored (south path and Girder 1 at Y < 0) while its skewed bearing lines were right. Every
transversely placed part is regenerated at the mirrored offset in skew coordinates, (u, Y) -> (u, -Y), so the
bearing lines X = +/-17.3736 - 0.976484 Y and all station/elevation rules are unchanged; parts keep their identity
(beam_1 is still Girder 1, walk_-1 still the south path, TX_rail_-1_* still the south rail, wing_*_-1 still the south
wing).

F5, sheets 31 and 37 (typical sections): "Proposed P.G." is on Line "Vir", which is 7'-0" right of the 8'-0" south
shoulder line and 4'-0" from the phased construction joint, i.e. on the bridge centre line (17'-3" + 8' + 7' =
32'-3" = 64'-6" / 2); the deck falls 2 % to each curb from there. The model put the crown on the centre of the 40 ft
roadway, 5 ft off Line "Vir". The crown moves to Y = 0; the model's linear profile grade (8.4 m local datum at X = 0,
0.54 ft fall over the 114 ft span) stays the elevation of the crown, as before. The roadway runs from the south curb
15'-0" left to the north curb 25'-0" right of Line "Vir"; the 6 in / 8 in curbs and 1.9 % / 1.5 % sidewalk slopes are
unchanged. Girders, haunches, bearings, seats, frames and abutment tops follow the corrected deck by the model's rules.

F3, sheet 39 (Type TX typical section) and sheets 31 / 37: the concrete rail is 3'-6" above the top of sidewalk
(the model used 32 in, the 2'-8" dimension of the same section). On the south coping the rail stands on the deck
concrete and the 2 3/4 in pavers and setting bed abut its traffic face (sheet 37), so the south panels extend 2 3/4 in
below the top of sidewalk and close the former gap above walk_-1. The nominal window openings are unchanged.

F7, sheet 39: the reset ornamental aluminium rail (south coping only) is anchored on top of the 12 in rail, centred
on it ("Embed 4 - 1/2 in x 6 in anchor bolts at each post"). The model placed it 6 in outside the rail's outer face.
Its centre line moves to the rail centre line (2 in + 6 in inside the coping edge) and its posts stand on the
corrected rail top.

F4, sheet 41 (plan at Abutments No. 1 and 2): the square terminal edges of the R.C. bridge approaches are at
Sta. 12+41.89 and 14+53.54 (14'-7 3/8" and 13'-5" beyond the bridge-floor corners at 12+56.50 and 14+40.12). The model
had measured 15'-9" and 20'-6" from those corners (12+40.75, 14+60.62). The approach slabs keep their skewed inner
edges and 12 in depth.

F6, sheets 41 and 43 (approach plans and Sections A-A to D-D): the 16'-1" south sidewalk (6 in curb, 1.9 %, reset
pavers) and the 6'-1" north sidewalk (8 in curb, 1.5 %) continue over the approach slabs. The model's approach slabs
had no curb step. The curb step and raised sidewalks (paver layer included on the south) are added to the
approach-slab envelopes; no new parts.

F2, existing sheets 10 and 14 (PDF 28, 32), 2013 Girder 1 replacement: an end cross-frame between Proposed Girder
No. 1 and Existing Girder No. 2 on each bearing line (framing plan, the line between Details "A" and "B" and its
counterpart at Abutment 2; End Cross-Frame Details, northbound structure): W16x45 top strut 3 in below the top of the
girder, L5x5x3/8 V diagonals and L5x5x3/8 bottom strut 6 in above the bottom flange. The model had none. Two parts
are added on the bearing lines, end_cross_frame_B1_1 and end_cross_frame_B2_1. The W16x45 envelope uses the AISC
nominal shape (d 16.13 in, bf 7.04 in, tf 0.565 in, tw 0.345 in); angles are strips like the other frames.

Derived seat risers follow the corrected bearings: Girder 8 (next to the north gutter) is now the lowest bearing and
sits on the abutment seat datum, so seat_1_8 / seat_2_8 are removed (zero height) and seat_1_3 / seat_2_3 are added.

Unchanged: the 1971 end struts E.S.1 / E.S.2 of bays 2-8 (existing S-7, PDF 65) are not in the review and are not
added; footings are symmetric and keep their buffers. source_ledger.json (FEM input) is not edited here; its
transverse values were mirrored to match afterwards (Girder 1 at Y +9.2964).

Requires numpy, trimesh and shapely.
"""
import hashlib
import json
import struct
import sys
from pathlib import Path

import numpy as np
import trimesh as tm
from shapely.geometry import Polygon

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from bridge_geometry import Model, FT, IN, box, sweep, rod, rectangular_bar, concat, iform  # noqa: E402

try:                                                  # the generator used mapbox-earcut; without it, triangulate the
    import mapbox_earcut  # noqa: F401                # same rings with manifold3d (identical vertices, other caps)
except ImportError:
    _triangulate = tm.creation.triangulate_polygon

    def _triangulate_fallback(polygon, triangle_args=None, engine=None, **kwargs):
        return _triangulate(polygon, triangle_args, engine='manifold' if engine in (None, 'earcut') else engine, **kwargs)
    tm.creation.triangulate_polygon = _triangulate_fallback

try:                                                  # trimesh needs scipy or networkx for connected components
    import scipy  # noqa: F401                        # (fix_normals(multibody=True)); fall back to label propagation
except ImportError:
    def _components(edges, min_len=1, nodes=None, engine=None):
        edges = np.asarray(edges, dtype=np.int64).reshape(-1, 2)
        nodes = np.unique(edges) if nodes is None else np.asarray(nodes, dtype=np.int64)
        if len(nodes) == 0:
            return []
        n = int(max(edges.max() if len(edges) else 0, nodes.max())) + 1
        keep = np.zeros(n, bool)
        keep[nodes] = True
        edges = edges[keep[edges].all(axis=1)]
        labels = np.arange(n)
        while True:
            low = np.minimum(labels[edges[:, 0]], labels[edges[:, 1]])
            new = labels.copy()
            np.minimum.at(new, edges[:, 0], low)
            np.minimum.at(new, edges[:, 1], low)
            new = new[new]
            if np.array_equal(new, labels):
                break
            labels = new
        lab = labels[nodes]
        order = np.argsort(lab, kind='stable')
        cuts = np.nonzero(np.diff(lab[order]))[0] + 1
        return [g for g in np.split(nodes[order], cuts) if len(g) >= min_len]
    tm.graph.connected_components = _components
    tm.repair.connected_components = _components

BID = 'virginia-avenue'
BASE = ROOT / 'data/bridges' / BID
TAG = 'transverse-mirror-crown-rails-approaches-end-frames'
REVISION = '1.1-review-corrections'

SPAN, LENGTH, WIDTH, SLAB = 114 * FT, (120 + 7.625 / 12) * FT, 64.5 * FT, 8 * IN
SKEW = 44 + 19 / 60 + 6 / 3600
U0, U1 = -LENGTH / 2, LENGTH / 2
STATION_0 = 1348.31                                   # sheet 31, centre line of structure "Vir", X = 0
TERMINAL_X = {1: (1241.89 - STATION_0) * FT,          # sheet 41, Sta. 12+41.89
              2: (1453.54 - STATION_0) * FT}          # sheet 41, Sta. 14+53.54
RAIL_H = {False: 32 * IN, True: 42 * IN}              # sheet 39: 3'-6" above top of sidewalk
PAVER = 2.75 * IN
GIRDER_Y_OLD = np.array([-30.5, -23.75, -15.833333333333, -7.916666666667, 0, 7.916666666667, 15.833333333333,
                         23.75, 30.5]) * FT
W16X45 = dict(d=16.13 * IN, bf=7.04 * IN, tf=.565 * IN, tw=.345 * IN)   # AISC nominal shape
ANGLE_LEG, ANGLE_T = 5 * IN, .375 * IN                                # L5x5x3/8, existing sheet 14


def grade(x):
    return 8.4 - (.54 / 114) * np.asarray(x)


def oriented_bar(a, b, wdir, width, thick):
    """Closed strip from a to b, `width` along wdir (made normal to b - a), `thick` across both."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    e1 = (b - a) / np.linalg.norm(b - a)
    e2 = np.asarray(wdir, float) - np.dot(wdir, e1) * e1
    e2 /= np.linalg.norm(e2)
    e3 = np.cross(e1, e2)
    frame = np.eye(4)
    frame[:3, :3] = np.column_stack([e1, e2, e3])
    frame[:3, 3] = (a + b) / 2
    return tm.creation.box(extents=[np.linalg.norm(b - a), width, thick], transform=frame)


def build(corrected):
    """Regenerate the exterior geometry with the rules of build_remaining_virginia_slab.virginia().

    corrected=False reproduces the published model; corrected=True applies F1-F7. Returns {id: (mesh, meta)}."""
    S = -1.0 if corrected else 1.0                     # F1: transverse mirror in skew coordinates
    Y = lambda y: S * np.asarray(y)                    # noqa: E731  original-frame offset -> model Y
    crown = 0.0 if corrected else 5 * FT               # F5
    south_curb, north_curb = Y(-15 * FT), Y(25 * FT)
    lo, hi = sorted([float(south_curb), float(north_curb)])
    rail_h = RAIL_H[corrected]
    m = Model(BID, LENGTH, WIDTH, SKEW, grade, crossfall=.02, crown=crown)

    def surface(x, y):
        y = np.asarray(y)
        if not corrected:
            curbs = (-15 * FT, 25 * FT)
            return grade(x) - .02 * np.abs(np.clip(y, *curbs) - crown) + np.where(
                y < curbs[0], .019 * (curbs[0] - y), np.where(y > curbs[1], .015 * (y - curbs[1]), 0))
        return grade(x) - .02 * np.abs(np.clip(y, lo, hi) - crown) + np.where(
            y > south_curb, .019 * (y - south_curb), np.where(y < north_curb, .015 * (north_curb - y), 0))

    m.surface = surface
    m.colors.update(girders='#748c95', steel='#8499a0', bracing='#83949b', rails='#dcd2b8', ornament='#829292')
    breaks = sorted([float(south_curb), crown, float(north_curb)])

    def slab_with_breaks(a, b, y0, y1, thick, brk=(), offset=0):
        yy = sorted(set([y0, y1] + [y for y in brk if y0 < y < y1]))
        pr = [(y, -thick) for y in yy] + [(y, 0) for y in reversed(yy)]
        return sweep(pr, np.linspace(a, b, max(2, int((b - a) / .5) + 1)),
                     lambda u, y, z: (m.sx(u, y), y, m.surface(m.sx(u, y), y) + z + offset))

    def level_prism(a, b, y0, y1, bottom, top):
        return sweep([(y0, 0), (y1, 0), (y1, 1), (y0, 1)], [a, b],
                     lambda u, y, t: (m.sx(u, y), y, (1 - t) * bottom(m.sx(u, y), y) + t * top(m.sx(u, y), y)))

    def span_y(ya, yb):
        """Original-frame interval -> sorted model interval."""
        return tuple(sorted([float(Y(ya)), float(Y(yb))]))

    m.add('deck', 'Proposed 2026 deck | single skew span', 'deck', slab_with_breaks(U0, U1, -WIDTH / 2, WIDTH / 2, SLAB, breaks),
          [31, 36, 37], 'Dimensioned proposed floor; nominal crossfall and reconstructed grade',
          '7.5 in structural depth plus 0.5 in integral wearing surface. Removed deck and overlay are excluded.',
          thickness_m=SLAB, structural_thickness_m=7.5 * IN)
    for side, ya, yb, h in [(-1, -WIDTH / 2, -15 * FT, 6 * IN), (1, 25 * FT, WIDTH / 2, 8 * IN)]:
        paver = PAVER if side < 0 else 0
        a, b = span_y(ya, yb)
        m.add(f'walk_{side}', f'{"South shared-use path" if side < 0 else "North sidewalk"} supporting concrete', 'sidewalks',
              slab_with_breaks(U0, U1, a, b, h - paver, offset=h - paver), [31, 37, 43], 'Dimensioned sidewalk and curb envelope',
              'South nominal 16 ft 1 in clear path and north 6 ft 1 in clear sidewalk; rail and edge margins excluded from clear widths.',
              clear_width_m=(16 + 1 / 12 if side < 0 else 6 + 1 / 12) * FT)
        if paver:
            a, b = span_y(ya + 14 * IN, yb)
            m.add('trail_pavers', 'Reset Cultural Trail pavers and setting bed envelope', 'sidewalks',
                  slab_with_breaks(U0, U1, a, b, paver, offset=h), [37, 43], '2.75 in paver and setting-bed envelope',
                  'Individual paver pattern is not fabricated.', thickness_m=paver)
    span = SPAN
    sections = {}
    clear = .05
    for j, yo in enumerate(GIRDER_Y_OLD):
        y = float(Y(yo))
        zones, pieces = [], []
        for q, (a, b) in enumerate([(-span / 2 - .375 * FT, -span / 2 + 20 * FT), (-span / 2 + 20 * FT, span / 2 - 20 * FT),
                                    (span / 2 - 20 * FT, span / 2 + .375 * FT)]):
            web = (54 if j == 0 else 60) * IN
            tw = .625 * IN
            bf = (18 if q == 1 else 16) * IN if j == 0 else 20 * IN
            tf = (2 if q == 1 else 1.25) * IN if j == 0 else (1.75 if q == 1 else 1.25) * IN
            d = web + 2 * tf
            pieces.append(sweep(iform(d, bf, tw, tf), np.linspace(a, b, max(3, int((b - a) / .5))),
                                lambda u, v, z, y=y, d=d: (m.sx(u, y), y + v, surface(m.sx(u, y), y) - SLAB - clear - d + z)))
            zones.append(dict(u0_m=max(a, -span / 2), u1_m=min(b, span / 2), web_depth_m=web, web_thickness_m=tw,
                              flange_width_m=bf, flange_thickness_m=tf, total_depth_m=d))
        key = f'beam_{j + 1}'
        m.add(key, f'Girder {j + 1} | ' + ('2013 replacement exterior member' if j == 0 else 'retained original plate girder'),
              'girders', concat(pieces), [31, 34, 36], 'Source piecewise welded I-section; straight nominal grade envelope',
              'Exact fabrication camber, small flange tapers and corrosion are not reconstructed.', y_m=y, section_zones=zones)
        sections[j] = zones
        maxbf = max(z['flange_width_m'] for z in zones)
        m.add(f'haunch_{j + 1}', f'Girder {j + 1} | nominal deck haunch', 'haunches',
              level_prism(-span / 2, span / 2, y - maxbf / 2, y + maxbf / 2, lambda x, v, y=y: surface(x, y) - SLAB - clear,
                          lambda x, v: surface(x, v) - SLAB), [36, 37], 'Derived contact envelope',
              '50 mm nominal haunch; source minimum fillet is 3/4 in. Actual variable screed and camber are unresolved.')
        for bi, u in enumerate([-span / 2, span / 2]):
            depth = zones[0 if bi == 0 else -1]['total_depth_m']
            bottom = surface(m.sx(u, y), y) - SLAB - clear - depth
            m.bearing(f'B{bi + 1}_bearing_{j + 1}', u, y, bottom, depth, [35] if bi == 0 else [31, 32],
                      pad=(.45, .51, .12 if bi == 0 else .10), plate=(.48, .56, .34 if bi == 0 else .22),
                      note='Abutment 1: proposed elastomer pad and HP14x89 bolster, simplified as stack. Abutment 2: retained '
                           'fixed shoe envelope. Field dimension A and anchor hardware unresolved.')
        for q, u in enumerate([-span / 2 + 20 * FT, span / 2 - 20 * FT]):
            x = m.sx(u, y)
            dep = zones[1]['total_depth_m']
            zt = surface(x, y) - SLAB - clear
            plates = []
            for side in [-1, 1]:
                vv = y + side * (tw / 2 + .008)
                plates.append(box(x - .60, x + .60, vv - .008, vv + .008, zt - dep + .08, zt - .08))
            m.add(f'splice_{j + 1}_{q + 1}', f'Girder {j + 1} | splice {q + 1} web cover plates', 'steel', concat(plates), [34],
                  'Source 20/74/20 ft splice positions; representative cover plate envelope',
                  'Plate layers, fabrication bolt holes, exact 2013/1971 patterns and inner flange bars omitted.')
    for j, (yao, ybo) in enumerate(zip(GIRDER_Y_OLD[:-1], GIRDER_Y_OLD[1:])):
        ya, yb = float(Y(yao)), float(Y(ybo))
        for q, u in enumerate(np.linspace(-span / 2 + 15.25 * FT, span / 2 - 10.75 * FT, 5)):
            x = m.sx(u, (ya + yb) / 2)
            z = min(surface(x, ya), surface(x, yb)) - SLAB - clear - .14
            bottom = z - 4 * FT
            a = np.array([x, float(Y(yao + .02)), z])
            b = np.array([x, float(Y(ybo - .02)), z])
            c = a.copy()
            c[2] = bottom
            d = b.copy()
            d[2] = bottom
            pieces = [rectangular_bar(c, d, .10, .10)]
            if j == 0:
                mid = (c + d) / 2
                pieces.extend([rectangular_bar(a, mid, .127, .014), rectangular_bar(b, mid, .127, .014)])
            else:
                pieces.extend([rectangular_bar(a, b, .102, .0127), rectangular_bar(a, d, .102, .0127), rectangular_bar(b, c, .102, .0127)])
            m.add(f'cross_frame_{j + 1}_{q + 1}', f'Bay {j + 1} | ' + ('V' if j == 0 else 'X') + f' cross frame {q + 1}', 'bracing',
                  concat(pieces), [31, 36], 'Historical frame type and nominal 22 ft rows',
                  'Exact stagger varies by bay and is approximated. Angle legs are represented by rectangular strips; no '
                  'structural area is inferred from mesh volume.')
    if corrected:   # F2: 2013 end cross-frames between Girders 1 and 2 on both bearing lines
        y1, y2 = float(Y(GIRDER_Y_OLD[0])), float(Y(GIRDER_Y_OLD[1]))
        g1_depth = sections[0][0]['total_depth_m']
        for bi, u in enumerate([-span / 2, span / 2]):
            ya, yb = float(Y(GIRDER_Y_OLD[0] + .02)), float(Y(GIRDER_Y_OLD[1] - .02))
            pa = np.array([m.sx(u, ya), ya, 0.0])
            pb = np.array([m.sx(u, yb), yb, 0.0])
            top_a = surface(m.sx(u, y1), y1) - SLAB - clear            # top of Girder 1 / Girder 2 at the bearing
            top_b = surface(m.sx(u, y2), y2) - SLAB - clear
            line = pb - pa
            normal = np.array([-line[1], line[0], 0.0]) / np.linalg.norm(line[:2])
            k = W16X45

            def strut(s, v, z):
                p = pa + s * line
                zt = top_a + s * (top_b - top_a) - 3 * IN
                return (p[0] + v * normal[0], p[1] + v * normal[1], zt - k['d'] + z)
            pieces = [sweep(iform(k['d'], k['bf'], k['tw'], k['tf']), [0.0, 1.0], strut)]
            chord = g1_depth - 6 * IN - ANGLE_LEG / 2           # chord centre below the girder top (6 in above G1 bottom)
            lo_a = np.array([pa[0], pa[1], top_a - chord])
            lo_b = np.array([pb[0], pb[1], top_b - chord])
            pieces.append(oriented_bar(lo_a, lo_b, [0, 0, 1], ANGLE_LEG, ANGLE_T))
            mid = (lo_a + lo_b) / 2
            for end, top in ((pa, top_a), (pb, top_b)):
                start = np.array([end[0], end[1], top - 3 * IN - k['d']])
                start[:2] += (mid[:2] - start[:2]) * (6 * IN / np.linalg.norm(mid[:2] - start[:2]))
                pieces.append(oriented_bar(start, mid, normal, ANGLE_LEG, ANGLE_T))
            m.add(f'end_cross_frame_B{bi + 1}_1', f'Bay 1 | Abutment {bi + 1} end cross frame (2013, Girders 1-2)', 'bracing',
                  concat(pieces), [31, 36], 'Existing plans 9548460 sheets 10 and 14 (PDF 28, 32): W16x45 top strut, '
                  'L5x5x3/8 V diagonals and bottom strut on the bearing line',
                  'W16x45 uses the AISC nominal shape, 3 in below the girder top; bottom strut 6 in above the Girder 1 bottom '
                  'flange (sheet 14 minimums). Gussets, bolts and stiffener connections omitted; angles are strips.',
                  top_strut='W16x45', angles='L5x5x3/8', along_bearing_line_m=round(float(np.linalg.norm(line)), 6))
    for bi, u in enumerate([-span / 2, span / 2]):
        contacts = [c for c in m.contacts if c['id'].startswith(f'B{bi + 1}_')]
        seat = min(c['seat_m'] for c in contacts)
        m.add(f'abutment_{bi + 1}', f'Abutment {bi + 1} | retained wall', 'abutments', m.transverse(u, 4 * FT, -WIDTH / 2, WIDTH / 2, .65, seat),
              [31, 32, 33, 38], 'Retained 4 ft wall envelope with constructed bearing-seat datum',
              'Historical abutment wall and footing are retained; exact batter, wing angles and seat steps simplified.',
              normal_thickness_m=4 * FT)
        for j, (yo, c) in enumerate(zip(GIRDER_Y_OLD, contacts)):
            y = float(Y(yo))
            if c['seat_m'] > seat + 1e-6:
                m.add(f'seat_{bi + 1}_{j + 1}', f'Abutment {bi + 1} | bearing seat riser {j + 1}', 'abutments',
                      m.transverse(u, .65, y - .36, y + .36, seat, c['seat_m']), [35, 38], 'Derived seat riser',
                      'Reconstructed to contact nominal shoe stack; not field survey.')
        m.add(f'footing_{bi + 1}', f'Abutment {bi + 1} | hidden spread footing envelope', 'foundations',
              m.transverse(u, 17 * FT, -WIDTH / 2 - .65, WIDTH / 2 + .65, 0, .65), [31, 32], 'Historical nominal footing envelope',
              'Exact eccentricity, toe and wing footing geometry omitted.')
        end = -1 if bi == 0 else 1
        m.add(f'mudwall_{bi + 1}', f'Abutment {bi + 1} | reconstructed mudwall and ledge', 'abutments',
              level_prism(u + end * .65 - .15, u + end * .65 + .15, -WIDTH / 2, WIDTH / 2, lambda x, y: seat,
                          lambda x, y: surface(x, y) - SLAB), [38], 'Source reconstructed mudwall topology; simplified ledge')
        for side in [-1, 1]:
            edge = float(Y(side * WIDTH / 2))
            x = m.sx(u, edge)
            a, b = sorted([x, x + end * 20 * FT])
            label = f'retained {"south" if side < 0 else "north"} wing envelope' if corrected else f'retained wing envelope {side}'
            m.add(f'wing_{bi + 1}_{side}', f'Abutment {bi + 1} | {label}', 'abutments',
                  box(a, b, edge - .18, edge + .18, .65, seat - .25), [31, 32],
                  'Historical wing presence; approximate 20 ft parallel envelope',
                  'Source wings are splayed and battered. Their exact plan and top profile remain incomplete.')
    for side in [-1, 1]:
        sgn = float(Y(side))                            # model sign of this coping
        edge = sgn * (WIDTH / 2 - 2 * IN)
        walkh = (6 if side < 0 else 8) * IN
        zb = -PAVER if (corrected and side < 0) else 0.0   # F3: south panels stand on the concrete below the pavers
        for panel, (a, b) in enumerate(zip(np.linspace(U0, U1, 6)[:-1], np.linspace(U0, U1, 6)[1:])):
            poly = Polygon([(a, zb), (b, zb), (b, rail_h), (a, rail_h)],
                           holes=[[(v - .13, .18), (v + .13, .18), (v + .13, .59), (v, .68), (v - .13, .59)]
                                  for v in np.arange(a + .5, b - .25, 1.5 * FT)])
            g = tm.creation.extrude_polygon(poly, 12 * IN, engine='earcut')
            vv = g.vertices.copy()
            uu, zz = vv[:, 0], vv[:, 1]
            yy = edge - sgn * vv[:, 2]
            xx = m.sx(uu, yy)
            g.vertices = np.column_stack([xx, yy, surface(xx, yy) + walkh + zz])
            label = f'{"south" if side < 0 else "north"} coping' if corrected else f'side {side}'
            m.add(f'TX_rail_{side}_{panel}', f'Type TX rail | {label} panel {panel + 1}', 'rails', g, [31, 37, 39],
                  'Dimensioned rail extent and window rhythm; nominal window profile',
                  ('42 in concrete rail above sidewalk' if corrected else '32 in nominal concrete rail above sidewalk') +
                  '. Exact mold recesses, fillets, pilasters and window curves simplified.')
        if side < 0:
            members = []
            yy = edge - sgn * 6 * IN if corrected else edge - 6 * IN      # F7: centred on the 12 in rail
            for u in np.linspace(U0 + .25, U1 - .25, 25):
                x = m.sx(u, yy)
                z = surface(x, yy) + walkh + rail_h
                members.append(rod([x, yy, z], [x, yy, z + .23], .025))
            xx = [m.sx(u, yy) for u in [U0, U1]]
            zz = [surface(x, yy) + walkh + rail_h + .23 for x in xx]
            members.append(rod([xx[0], yy, zz[0]], [xx[1], yy, zz[1]], .025))
            m.add('ornamental_rail', 'Reset south aluminum ornamental top rail', 'ornament', concat(members), [39],
                  'Source south-only rail; simplified round members',
                  '25 post locations follow the 24-space elevation rhythm approximately; exact metal profile and anchorage omitted.')
    for bi, end, alen in [(1, -1, 15.75 * FT), (2, 1, 20.5 * FT)]:
        inner = end * LENGTH / 2
        if corrected:   # F4: sheet 41 terminal stations
            xouter = TERMINAL_X[bi]
        else:
            xouter = (min(m.sx(inner, -WIDTH / 2), m.sx(inner, WIDTH / 2)) - alen if end < 0
                      else max(m.sx(inner, -WIDTH / 2), m.sx(inner, WIDTH / 2)) + alen)
        yy = sorted([-WIDTH / 2, *breaks, WIDTH / 2])
        if corrected:   # F6: raised sidewalks (south 6 in incl. pavers, north 8 in) on the approach slab
            def lift(y):
                return 6 * IN if y > south_curb + 1e-9 else (8 * IN if y < north_curb - 1e-9 else 0.0)
            top = []
            for y in reversed(yy):
                if abs(y - south_curb) < 1e-9:
                    top += [(y, 6 * IN), (y, 0.0)]
                elif abs(y - north_curb) < 1e-9:
                    top += [(y, 0.0), (y, 8 * IN)]
                else:
                    top.append((y, lift(y)))
            profile = [(y, -12 * IN) for y in yy] + top
        else:
            profile = [(y, -12 * IN) for y in yy] + [(y, 0) for y in reversed(yy)]
        g = sweep(profile, np.linspace(0, 1, 45), lambda t, y, z: (m.sx(inner, y) * (1 - t) + xouter * t, y,
                                                                    surface(m.sx(inner, y) * (1 - t) + xouter * t, y) + z))
        dims = dict(minimum_length_m=alen, thickness_m=12 * IN)
        if corrected:
            dims = dict(terminal_x_m=round(xouter, 6), terminal_station='12+41.89' if bi == 1 else '14+53.54',
                        thickness_m=12 * IN, south_curb_m=6 * IN, north_curb_m=8 * IN)
        m.add(f'approach_{bi}', f'Abutment {bi} | proposed reinforced approach slab', 'approaches', g, [31, 41, 43],
              'Sheet 41 terminal station with square terminal edge; sheet 43 curb and sidewalk sections' if corrected
              else 'Source minimum approach length with square terminal edge',
              '12 in nominal depth; exact local transition extensions and terminal joint shapes simplified.', **dims)
        m.add(f'joint_{bi}', f'Abutment {bi} | Type IA joint line', 'joints',
              slab_with_breaks(inner - .012, inner + .012, -WIDTH / 2, WIDTH / 2, .06, breaks), [38, 41],
              'Schematic 24 mm joint strip; installation gap unresolved')
    y = float(Y(-15 * FT - 2.5 * FT))
    for i, u in enumerate(np.linspace(U0 + .8, U1 - .8, 6)):
        x = m.sx(u, y)
        z = surface(x, y) + 6 * IN
        g = concat([rod([x, y, z], [x, y, z + .9], .08, 16), rod([x, y, z + .9], [x, y, z + 1.03], .13, 16)])
        m.add(f'bollard_{i + 1}', f'Reset Cultural Trail light bollard {i + 1}', 'accessories', g, [31, 37],
              'Source six-count; nominal housing and evenly distributed positions',
              'Exact source lighting station offsets and fixture product geometry unresolved.')
    u = span / 2 - 3 * FT
    y = float(Y(-15 * FT + .2))
    x = m.sx(u, y)
    z = surface(x, y)
    far = float(Y(WIDTH / 2))
    drain = [box(x - .22, x + .22, y - .18, y + .18, z - .15, z + .015), rod([x, y, z - .1], [x, y, z - 2.0], 3 * IN),
             rod([x, y, z - 2], [m.sx(span / 2, far), far, z - 2.10], 3 * IN)]
    m.add('drain_abutment_2', 'Abutment 2 | SQ-A drain and 6 in collector envelope', 'drainage', concat(drain), [36, 39],
          'Source drain/collector routing; nominal fittings',
          'Collector is a straight visual run below the girders; elbows, hangers, cleanouts and deck penetrations are simplified.')
    return {p['id']: (m.meshes[p['id']], p) for p in m.parts}, m


def to_gltf(v):
    return np.column_stack([v[:, 0], v[:, 2], -v[:, 1]])


def to_native(v):
    return np.column_stack([v[:, 0], -v[:, 2], v[:, 1]])


F1 = ('Review correction 1.1: moved to the plan side (Girder 1 and the south path at plan-left looking up-station, '
      'sheets 31, 36, 37; existing sheet 10) and re-seated on the deck crowned at Line "Vir" (sheets 31, 37).')
F5 = ('Review correction 1.1: crown moved to Line "Vir" (Y = 0), 2 % to the south curb 15 ft left and the north curb '
      '25 ft right of it (sheets 31, 37); transverse arrangement mirrored to the plan side (sheets 31, 36).')
ABUT = ('Review correction 1.1: seat datum / top re-derived from the corrected deck and bearings (plan side and crown on '
        'Line "Vir", sheets 31, 36, 37).')
NOTES = {
    'TX_rail': F1 + ' F3: 3\'-6" above the top of sidewalk (sheet 39 typical section); south panels stand on the deck '
               'concrete 2 3/4 in below the paver top (sheet 37).',
    'ornamental_rail': F1 + ' F7: centred on the 12 in TX rail and anchored on its top (sheet 39).',
    'approach': F5 + ' F4: square terminal at the sheet 41 station; F6: 6 in south curb with pavers and 8 in north '
                'curb, 1.9 % / 1.5 % sidewalks continued over the slab (sheets 41, 43).',
}


def rail_height(v):
    """Largest vertical extent over one plan point of a rail panel (base to top at the faces)."""
    xy = np.round(v[:, :2], 4)
    _, inverse = np.unique(xy, axis=0, return_inverse=True)
    inverse = inverse.ravel()
    top = np.full(inverse.max() + 1, -np.inf)
    bottom = np.full(inverse.max() + 1, np.inf)
    np.maximum.at(top, inverse, v[:, 2])
    np.minimum.at(bottom, inverse, v[:, 2])
    return float((top - bottom).max())


def note_for(pid):
    if pid.startswith('TX_rail'):
        return NOTES['TX_rail']
    if pid == 'ornamental_rail':
        return NOTES['ornamental_rail']
    if pid.startswith('approach'):
        return NOTES['approach']
    if pid in ('deck', 'joint_1', 'joint_2'):
        return F5
    if pid.split('_')[0] in ('abutment', 'mudwall', 'footing'):
        return ABUT
    return F1


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

    cache = {}            # identical arrays share one accessor, as in the trimesh export (colours, frame indices)

    def append(array, kind, component):
        data = array.tobytes()
        key = (kind, component, len(array), hashlib.sha256(data).hexdigest())
        if key in cache:
            return cache[key]
        while len(binary) % 4:
            binary.append(0)
        view = len(gltf['bufferViews'])
        gltf['bufferViews'].append(dict(buffer=0, byteOffset=len(binary), byteLength=len(data)))
        binary.extend(data)
        a = dict(bufferView=view, componentType=component, count=len(array), type=kind)
        if kind == 'VEC3':
            a.update(min=array.min(axis=0).tolist(), max=array.max(axis=0).tolist())
        gltf['accessors'].append(a)
        cache[key] = len(gltf['accessors']) - 1
        return cache[key]

    for ai, a in enumerate(gltf['accessors']):      # reuse the existing colour and index arrays where identical
        if a['type'] in ('SCALAR', 'VEC4'):
            arr = read(ai)
            cache.setdefault((a['type'], a['componentType'], len(arr), hashlib.sha256(arr.tobytes()).hexdigest()), ai)

    def native(pid):
        prim = meshes[pid]['primitives'][0]
        return to_native(read(prim['attributes']['POSITION']).astype(np.float64))

    def same_vertices(a, b, tol):
        if a.shape != b.shape:
            return False
        if np.abs(a - b).max() <= tol:
            return True
        ka, kb = np.round(a, 4), np.round(b, 4)
        return np.abs(ka[np.lexsort(ka.T[::-1])] - kb[np.lexsort(kb.T[::-1])]).max() <= 2e-4

    old, _ = build(False)
    new, _ = build(True)

    # The published model must be the uncorrected reconstruction, part by part.
    if set(old) != set(meshes) or set(old) != set(parts):
        raise ValueError('Unexpected part set; the model is not the expected revision.')
    for pid, (mesh, meta) in old.items():
        if not same_vertices(native(pid), mesh.vertices, 1e-5):
            raise ValueError(f'{pid}: GLB geometry differs from the expected uncorrected reconstruction')
        if abs(parts[pid]['volume_m3'] - mesh.volume) > 1e-6 * max(1.0, abs(mesh.volume)):
            raise ValueError(f'{pid}: unexpected manifest volume')
    checks = {   # the reviewed values (native X, Y, Z)
        'Girder 1 centre Y': (np.mean(parts['beam_1']['bounds_m'], axis=0)[1], -9.2964),
        'Girder 9 centre Y': (np.mean(parts['beam_9']['bounds_m'], axis=0)[1], 9.2964),
        'south path inner edge Y': (parts['walk_-1']['bounds_m'][1][1], -4.572),
        'TX rail height above the north sidewalk': (rail_height(native('TX_rail_1_0')), 32 * IN),
        'ornamental rail centre Y': (np.mean(parts['ornamental_rail']['bounds_m'], axis=0)[1], -9.9314),
        'approach 1 terminal X': (parts['approach_1']['bounds_m'][0][0], -32.784080),
        'approach 2 terminal X': (parts['approach_2']['bounds_m'][1][0], 34.231880),
    }
    deck_top = native('deck')
    ridge = deck_top[np.argmax(deck_top[:, 2] + (.54 / 114) * deck_top[:, 0])]
    checks['crown Y'] = (ridge[1], 5 * FT)
    for label, (value, expected) in checks.items():
        if abs(value - expected) > 1e-3:
            raise ValueError(f'{label}: {value:.6f}, expected {expected:.6f}')

    world = gltf['nodes'][gltf['scenes'][gltf.get('scene', 0)]['nodes'][0]]
    changed, added, removed, kept = [], [], [], []
    meta_keys = ('id', 'name', 'layer', 'color', 'pdf_pages', 'basis', 'note', 'dimensions')
    for pid, (mesh, meta) in new.items():
        if pid in old and same_vertices(old[pid][0].vertices, mesh.vertices, 1e-9):
            kept.append(pid)
            continue
        if not mesh.is_watertight or mesh.volume <= 0:
            raise ValueError(f'{pid}: invalid corrected solid')
        rgb = [int(meta['color'][n:n + 2], 16) for n in (1, 3, 5)] + [255]
        prim = dict(attributes=dict(POSITION=append(to_gltf(mesh.vertices).astype('<f4'), 'VEC3', 5126),
                                    COLOR_0=append(np.tile(np.array(rgb, 'u1'), (len(mesh.vertices), 1)), 'VEC4', 5121)),
                    indices=append(mesh.faces.reshape(-1, 1).astype('<u4'), 'SCALAR', 5125), mode=4)
        gltf['accessors'][prim['attributes']['COLOR_0']]['normalized'] = True
        if pid in parts:
            p = parts[pid]
            if meshes[pid]['primitives'][0].get('material') is not None:
                prim['material'] = meshes[pid]['primitives'][0]['material']
            meshes[pid]['primitives'] = [prim]
            p.update(name=meta['name'], basis=meta['basis'], dimensions=meta['dimensions'],
                     note=(meta['note'] + ' ' + note_for(pid)).strip())
            changed.append(pid)
        else:
            p = {k: meta[k] for k in meta_keys}
            p['note'] = (meta['note'] + ' Review correction 1.1: added from existing sheets 10 and 14 (PDF 28, 32).'
                         if pid.startswith('end_cross_frame') else
                         meta['note'] + ' Review correction 1.1: added because Girder 3 is no longer the lowest bearing '
                         'after the plan-side and crown corrections (Girder 8 now sits on the seat datum).')
            p['source_refs'] = [dict(source_id='9683637', pdf_pages=meta['pdf_pages'])]
            if pid.startswith('end_cross_frame'):
                p['source_refs'].append(dict(source_id='9548460', pdf_pages=[28, 32]))
            gltf['meshes'].append(dict(name=pid, extras=dict(processed=True), primitives=[prim]))
            meshes[pid] = gltf['meshes'][-1]
            gltf['nodes'].append(dict(name=pid, mesh=len(gltf['meshes']) - 1))
            world['children'].append(len(gltf['nodes']) - 1)
            manifest['parts'].append(p)
            parts[pid] = p
            added.append(pid)
        p['bounds_m'] = np.round(mesh.bounds, 6).tolist()
        p['volume_m3'] = round(float(mesh.volume), 9)
        meshes[pid]['extras'].update({k: p[k] for k in meta_keys})

    # Seat risers that the corrected derivation no longer needs (zero height) are removed with their node and mesh.
    for pid in [k for k in old if k not in new]:
        if not pid.startswith('seat_'):
            raise ValueError(f'{pid}: unexpected removal')
        node = next(i for i, n in enumerate(gltf['nodes']) if n.get('name') == pid)
        mesh_index = gltf['nodes'][node]['mesh']
        del gltf['nodes'][node]
        for n in gltf['nodes']:
            if 'children' in n:
                n['children'] = [c - (c > node) for c in n['children'] if c != node]
            if 'mesh' in n and n['mesh'] > mesh_index:
                n['mesh'] -= 1
        for sc in gltf['scenes']:
            sc['nodes'] = [c - (c > node) for c in sc['nodes'] if c != node]
        del gltf['meshes'][mesh_index]
        manifest['parts'] = [p for p in manifest['parts'] if p['id'] != pid]
        removed.append(pid)
    if sorted(removed) != ['seat_1_8', 'seat_2_8'] or sorted(added) != sorted(
            ['end_cross_frame_B1_1', 'end_cross_frame_B2_1', 'seat_1_3', 'seat_2_3']) or kept != ['footing_1', 'footing_2']:
        raise ValueError(f'unexpected change set: added {added}, removed {removed}, kept {kept}')

    # Coverage lists follow the part set: removed ids out, new ids into the entries that list their layer.
    by_layer = {p['id']: p['layer'] for p in manifest['parts']}
    for cov in manifest.get('detail_coverage', []):
        ids = [i for i in cov['part_ids'] if i not in removed]
        layers = {by_layer[i] for i in ids if i in by_layer}
        ids += [i for i in added if by_layer[i] in layers and i not in ids]
        cov['part_ids'] = ids
        if cov['feature'] == 'Retained steel and bearings':
            cov['detail'] += ' 2013 Girder 1-2 end cross-frames on both bearing lines (existing sheets 10, 14).'

    gltf['buffers'][0]['byteLength'] = len(binary)
    while len(binary) % 4:
        binary.append(0)
    encoded = json.dumps(gltf, ensure_ascii=True, separators=(',', ':')).encode()
    encoded += b' ' * ((-len(encoded)) % 4)
    out = (struct.pack('<III', 0x46546c67, 2, 28 + len(encoded) + len(binary)) +
           struct.pack('<II', len(encoded), 0x4e4f534a) + encoded + struct.pack('<II', len(binary), 0x004e4942) + binary)
    backup = ROOT / 'data/fem_research'
    backup.mkdir(exist_ok=True)
    (backup / 'virginia_avenue_before_review_correction.glb').write_bytes(original)
    (backup / 'virginia_avenue_manifest_before_review_correction.json').write_bytes(mp.read_bytes())
    path.write_bytes(out)

    t1 = new['TX_rail_-1_0'][0]
    manifest['review_correction'] = TAG
    manifest['revision'] = REVISION
    manifest['review_correction_record'] = dict(
        source='External model review (findings F1-F7), each finding re-read against the drawings',
        source_pdf_pages=[31, 36, 37, 39, 41, 43], printed_sheets=[31, 36, 37, 39, 41, 43],
        historical_source=dict(source_id='9548460', pdf_pages=[28, 32], printed_sheets=[10, 14]),
        findings={
            'F1': 'Transverse arrangement mirrored to the plan side in skew coordinates (u, Y) -> (u, -Y): Girder 1 '
                  'Y -9.2964 -> +9.2964 (B1 bearing X -8.2958 -> -26.4514), south path Y -9.8298..-4.572 -> '
                  '+4.572..+9.8298; bearing lines X = +/-17.3736 - 0.976484 Y unchanged. Sheets 31, 36, 37; existing 10.',
            'F2': 'Added 2013 end cross-frames Girders 1-2 on both bearing lines: W16x45 strut 3 in below the girder '
                  'top, L5x5x3/8 V and bottom strut 6 in above the Girder 1 bottom flange. Existing sheets 10, 14.',
            'F3': 'TX rail top 32 in -> 42 in (3\'-6") above the top of sidewalk; south panels extended 2 3/4 in down '
                  'to the deck concrete under the pavers (gap closed). Sheets 37, 39.',
            'F4': 'Approach terminals X -32.784081 -> -32.436816 (Sta. 12+41.89) and +34.231880 -> +32.074104 '
                  '(Sta. 14+53.54). Sheet 41.',
            'F5': 'Crown Y +1.524 -> 0 (Line "Vir"); profile grade 8.4 m - 0.004737 X (local datum) kept at the crown; '
                  'roadway -7.620 <= Y <= +4.572. Sheets 31, 37.',
            'F6': 'Approach slabs carry the 6 in south (with pavers, 1.9 %) and 8 in north (1.5 %) curbs and sidewalks. '
                  'Sheets 41, 43.',
            'F7': 'Ornamental rail centre line Y -9.9314 -> +9.6266 (TX rail centre), posts on the 42 in rail top. '
                  'Sheet 39.'},
        derived_elevations='Girders 50 mm below the corrected soffit, bearings, seats, abutment tops, mudwalls, wings '
                           'and frames re-derived with the reconstruction rules of build_remaining_virginia_slab.py.',
        changed_parts=changed, added_parts=added, removed_parts=removed, unchanged_parts=kept,
        renamed_labels='TX_rail_* and wing_* names now say south / north; part ids unchanged.',
        rail_height_above_sidewalk_m=dict(before=round(32 * IN, 4), after=round(42 * IN, 4),
                                          south_panel_base_to_top=round(rail_height(t1.vertices), 4)),
        before_glb_sha256=before, after_glb_sha256=hashlib.sha256(out).hexdigest())
    deviations = [d for d in manifest.get('known_deviations', []) if d.get('id') not in ('end-struts-bays-2-8', 'fem-ledger-girder-offsets')]
    deviations.append(dict(
        id='end-struts-bays-2-8', parts='(not modelled)', source='existing plans 9548460 S-7 (PDF 65)',
        deviation='The 1971 end struts E.S.1 / E.S.2 along both bearing lines of bays 2-8 are not modelled; only the '
                  '2013 Girder 1-2 end cross-frames are.',
        reason='Outside the reviewed findings; their member sizes are on historical detail sheets not yet read.'))
    manifest['known_deviations'] = deviations
    mp.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(changed=len(changed), added=added, removed=removed, kept=kept,
                          before=before, after=manifest['review_correction_record']['after_glb_sha256'])))


if __name__ == '__main__':
    correct()

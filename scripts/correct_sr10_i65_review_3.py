"""Third drawing-confirmed correction of SR 10 over I-65 (sr10-i65): the known deviations left by rounds 1 and 2.

    python scripts/correct_sr10_i65_review_3.py

Runs after correct_sr10_i65_review.py and correct_sr10_i65_review_2.py. Source: drawings.pdf, the local review binder.
PDF 1-20 are the 1964 plans (S1-S12), PDF 21-40 the 1998 B-23753 plans (printed sheet n = PDF page n + 20), PDF 49-62
the 2026 R-43918 approach plans. Local Z = plan elevation - 210.000 m. Model index j = drawing beam line 9 - j (the
geometry is symmetric about Y = 0, so the drawing values below apply to index j and 8 - j alike).

1. Pier 2/4 seat stack (known deviation pier-2-4-seat-stack). Sheet 11 (PDF 31) elevation: cap top El. 215.972, raised
   to El. 216.016 over the central 5334 mm (4954 + 5334 + 4954 = 15 242). Sheet 14 (PDF 34): Type I elastomeric
   expansion bearing, 250 x 350 x 67 mm elastomer under PL 58x280x405 = 125 mm, with a shim plate between the plate
   and the bottom flange ("Section @ Pier 2 or 4"). Sheet 16 (PDF 36) shim table, Piers 2 and 4: 38, 13, 32, 13, 26,
   13, 32, 13, 38 mm. The model had a flat cap at El. 215.925 with derived seat risers, and the beams 15-60 mm below
   cap + 125 mm + shim. The caps get the stepped drawing top, the bearings stand on the cap, the seven risers per pier
   become the shim plates and the missing shims of lines 2 and 8 are added (B2/B4_seat_1, _7). Shim plan size is not
   dimensioned: 280 mm along the beam (drawn flush with the 280 mm plate) by the bottom-flange width (drawn flush with
   the flange in Section A-A).
2. Girder profile at every support (pier-2-4-seat-stack, pier-3-beam-taper). Beam bottom-flange undersides:
   - Bents 1/5: pile cutoff El. 216.078 / .053 / .084 / .120 / .155 / .120 / .084 / .053 / .078 (sheet 9, PDF 29)
     + PL 19x150x500 cap plate under the flange (sheet 10 Detail A, PDF 30);
   - Piers 2/4: cap + 125 mm bearing + shim (item 1);
   - Pier 3: cap + 260 mm shoe + shim + flange cover plate (rounds 1-2, unchanged).
   The model's nominal profile (1998 grade - 200 mm slab - 75 mm haunch - depth) is raised by the drawing offsets at
   each support, linearly between supports and constant over the 1.13 m Pier 3 splice (as in round 1). Decision: the
   linear interpolation between support elevations replaces the round-1 taper to zero at Piers 2/4. Sheet 16 "No Load
   Camber & Blocking Diagram" gives the chord ordinates above the bent-to-bent line A = 38 (Pier 2 splice), B = 63
   (Pier 3), C = 38 mm; the drawing stacks of lines 1/9 give 38 mm at Pier 2 and 63 mm at Pier 3, and the camber less
   the dead-load deflection (same sheet) is about the 6 mm sag of the vertical curve, so the steel follows the grade
   between supports. No screed or top-of-steel elevations are given between supports.
3. Beam depths (pier-3-top-splice-plate-embedment, pier-3-beam-taper). Decision: the beams use the depths of their
   drawn designations (ASTM A6/A6M) instead of the nominal 920 mm: W920x201 903 mm, W920x223 (36WF150 retained) 911 mm,
   W840x193 840 mm (unchanged). Evidence: sheet 14 Type II splice fills the W920x201 side with PL 4x305x485 top and
   bottom, i.e. (911 - 903) / 2; with 903 mm the bent pile cutoffs give a uniform 31-33 mm haunch on lines 2-8 (30 mm
   on the W840 lines), while 920 mm would leave about 15 mm. Flange widths and thicknesses keep the generator values. The
   new W920x201 extends 900 mm into spans B and C to the Type II splice (sheet 13, "Existing beams to be cut off 900 mm
   from C/L Pier"); beam_1_j / beam_2_j (j = 1..7) carry that stub with the 903 mm section, centred on the 911 mm
   W920x223 at the splice (4 mm step at the top and bottom flange, filled by the fillers).
4. Pier 2/4-side field splices (pier-2-4-splice-plates), sheet 14 (PDF 34), located by sheet 13 beam elevations
   ("C/L New Type I Splice" lines 1/9, "C/L New Type II Splice" lines 2-8, 900 mm into spans B/C):
   - Type I (lines 1/9): flange plates PL 16x292x1130 outside, 2 bars 13x102x1130 inside each flange on the 190 mm
     bolt gauge, web plates 2-PL 13x480x710, web bolts 6 columns (40, 2 @ 75, 50 | 50, 2 @ 75, 40) x 7 rows @ 105 mm;
   - Type II (lines 2-8): flange plates PL 13x305x980, bars 10x115x980, fillers PL 4x305x485 on the W920x201 side,
     web plates 2-PL 13x480x770, web bolts 6 columns x 7 rows @ 115 mm.
   The same Type I detail is applied to the Pier 3 splices of lines 1/9 (sheet 13 "C/L New Type I Splice"), which had
   the plates but not the bars or the drawing bolt grid. The retained 1964 Pier 3 splices of lines 2-8 keep their
   round-2 plates, which follow the refitted beams; web plates and bolts move with the 911 mm beam centre.
5. Everything that rests on the beams follows: haunch bottoms (on the beam top), all 88 diaphragms (re-placed by the
   round-2 rules: exterior bottoms 200 mm above the W840 bottom, interior bays centred), splice plates and bolts.
   Deck, Pier 3 stack and all other parts are unchanged.

Items from the independent check of this round (each verified against the sheets):
6. End beams (sheet 10 Detail A, PDF 30): the span A/D beams end 150 mm beyond the bent centre line (were cut at it).
7. Splice fasteners. Sheet 14 flange bolts: 2 rows on the 190 mm gauge, 7 (Type I) / 6 (Type II) per side at 76 + n x 75
   mm from the splice centre line, through outer plate, flange (and filler) and inner bar; the inner pair of the
   bottom flange are "26 mm open holes for attachment of top shoes", so no bolts there. Retained 1964 Pier 3 splices
   (1964 S9, PDF 11): web plates 2 PL 31 x 1/2 in (787.4 x 12.7 mm; were 770 x 13 mm), web rivets 6 columns at 2 @ 3 in
   each side of a 4 1/8 in centre gap x 10 rows at 4 @ 3 in each side of a 4 in centre gap (60; were 35). The plate
   length along the beam is not dimensioned and keeps the 480 mm envelope.
8. Diaphragm ends (sheet 15, PDF 35). New MC460x63.5 stop 25 mm off the beam web face ("25 (Typ.)", both interior
   diaphragm details); the retained W460x68 run web to web (sheet 15 removal plan, 1964 S10 Section A-A); the
   replacement C380x74 lap 130 mm over 200 mm stubs of the removed W460x68 left on each beam web ("200 (Typ.)" removal
   line, Detail "B": 130 lap, bolt line 65 from the stub end), so they stop 70 mm off the web face, back to back with
   the stub web. Ten stubs are added (diaphragm_q_2_stub_k, q = 3..7, k = model beam index 2, 3). The model had every
   diaphragm 160 mm short of the beam centre lines. Detail "B" and Section C-C carry no orientation, so the channel is
   placed on the +X side of the stub web (known deviation c380-stub-side).
9. Pavement ledge (sheet 9 elevation, PDF 29): the retained ledge is level at El. 216.850 (the model had it crowned on
   the 12 in approach soffit, up to El. 217.003). The 2026 approach slab end bears on it (2026 sheet 13 Section B-B),
   so its soffit over the 134 mm seat is lowered to the ledge; the thickened end beyond the bent back face is on
   standard drawings E609-RCBA-01 to -04, not in the set (known deviation approach-ledge-detail).
10. Display names use the drawing beam-line numbering (drawing line = 9 - model index); ids are unchanged.
11. Final pass. Beam flanges get the catalog thickness of the drawn sections (W840x193 21.7, W920x201 20.1, W920x223
    23.9 mm; were 25.4 / 23 / 27), outer faces kept, so the splice bars and fastener grips follow. Haunches follow the
    sheet 17 Typical Beam Haunch Detail (PDF 37): 100 mm (+/-25) shoulders beyond each flange edge down to the
    underside of the top flange, the top on the deck soffit with the crown ridge on line 5; the span A/D haunches start
    at the span face of the integral bents; over the field splices they sit on the top splice plates (built at the
    plate stations) with pockets for the fastener heads (manifold3d difference with cutters run 3 mm into the plates,
    so no faces coincide). Dimension "A" of the sheet 17 Beam Haunch Table is measured to the flange underside and then agrees
    with the pier stacks to about 2 mm. Retained 1964 Pier 3 splices (1964 S9, PDF 11): inner bars PL 4 1/2 x 3/8 in x
    33 in (interior beams) and 4 1/2 x 5/8 in x 45 in (exterior beams = drawing lines 2/8), centred on the 7 1/2 in
    gauge and ending 1 1/2 in beyond the last rivet of the inner group; flange rivets 18 per side per gauge line at
    3 in, 72 top and 68 bottom (the 4 under the top shoe are left out).

Not settled by the drawings (known deviations): the sheet 17 haunch table at the bents (no stations); the bottom-flange
rivets under the Pier 3 top shoe; the C380 side; the approach end beyond the ledge; the id numbering.

Requires numpy, trimesh and shapely (2.1 or later); uses box/concat/iform/bolt from scripts/bridge_geometry.py.
Optional arguments for a dry run on a copy: --base DIR (bridge folder) and --backup DIR.
"""
import hashlib
import json
import struct
import sys
from pathlib import Path

import manifold3d as mf
import numpy as np
import shapely
import trimesh

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from bridge_geometry import bolt, box, concat, iform  # noqa: E402

BID = 'sr10-i65'
PREVIOUS_TAG = 'splice-plates-diaphragm-sections-approaches-footings'
PREVIOUS_REVISION = '1.2-drawing-review-2'
TAG = 'pier24-seats-support-profile-catalog-depths-splices'
REVISION = '1.3-deviations'
TOL = 3e-5                                                            # float32 vertex tolerance (m)

FT, IN = .3048, .0254
SPANS = np.array([39 + .5 / 12, 65.75, 65.75, 39 + .5 / 12]) * FT     # as built by build_indiana_batch3.sr10
BS = np.r_[0, np.cumsum(SPANS)] - SPANS.sum() / 2                     # support centre lines
B1, P2, P3, P4, B5 = BS
SLAB, CLEAR = .2, .075
YS = np.array([-7.113, -5.080, -3.556, -1.778, 0, 1.778, 3.556, 5.080, 7.113])   # model index 0 = drawing line 9
OLD_DEPTH = np.array([.84] + [.92] * 7 + [.84])
PLATEAU = 1.13 / 2                                                    # flat fit over the Pier 3 splice (round 1)
EPS = .001                                                            # length of the W920x201/W920x223 step

# Catalog depth and flange thickness of the drawn designations (ASTM A6/A6M); flange width and web keep the
# generator's nominal values (within 1 mm of the catalog).
W840 = dict(label='W840x193', d=.840, bf=.292, tw=.014, tf=.0217)
W201 = dict(label='W920x201', d=.903, bf=.305, tw=.015, tf=.0201)
W223 = dict(label='W920x223 retained', d=.911, bf=.305, tw=.016, tf=.0239)
OLD_TF = {'W840x193': .0254, 'W920x201': .023, 'W920x223 retained': .027}
STEP = (W223['d'] - W201['d']) / 2                                    # 4 mm = sheet 14 Type II filler

# Support elevations (local Z).
PILE_CUTOFF = np.array([216.078, 216.053, 216.084, 216.120, 216.155, 216.120, 216.084, 216.053, 216.078]) - 210
BENT_PLATE = .019                                                     # sheet 10 Detail A, PL 19x150x500
CAP24_OUTER, CAP24_CENTRAL, CENTRAL_HALF = 5.972, 6.016, 5.334 / 2    # sheet 11
OLD_CAP24 = 5.925055
ELASTOMER, LOAD_PLATE = (.250, .350, .067), (.280, .405, .058)        # sheet 14 Type I bearing, 125 mm
BEARING24 = ELASTOMER[2] + LOAD_PLATE[2]
SHIM24 = np.array([38, 13, 32, 13, 26, 13, 32, 13, 38]) / 1000        # sheet 16, Piers 2 and 4
CAP3_OUTER, CAP3_CENTRAL = 5.835, 5.879                               # sheet 12 (round 1)
SHOE3 = .26
SHIM3 = np.array([49, 13, 32, 13, 26, 13, 32, 13, 49]) / 1000
PLATE3 = np.array([.016] + [15 / 16 * IN] * 7 + [.016])               # round 2
PIER24_BASE, PIER24_MID, PIER24_HALF, STEM24_HALF = -.267, 3.391, 7.621, 2.5575

# Splices 900 mm into spans B and C (sheet 13) and their sheet 14 details.
XS = {1: P2 + .9, 3: P4 - .9}
TYPE_I = dict(name='Type I', plate=(.016, .292, 1.13), bar=(.013, .102, 1.13), web=(.013, .48, .71), pitch=.105,
              filler=None, flange_cols=7)
TYPE_II = dict(name='Type II', plate=(.013, .305, .98), bar=(.010, .115, .98), web=(.013, .48, .77), pitch=.115,
               filler=(.004, .305, .485), flange_cols=6)
FLANGE_X0, FLANGE_PITCH = .076, .075                                  # sheet 14 plans: 76 | 76 at the splice, @ 75
RET_WEB_H, RET_WEB_T = 31 * IN, .5 * IN                               # 1964 S9: 2 PL 31 x 1/2 in
RET_COLS = np.array([-8.0625, -5.0625, -2.0625, 2.0625, 5.0625, 8.0625]) * IN
RET_ROWS = np.array([-14, -11, -8, -5, -2, 2, 5, 8, 11, 14]) * IN
RET_FLANGE_X = np.arange(1, 19) * 3 * IN                              # 1964 S9: 18 per side at 3 in from the C/L
RET_GAUGE = 3.75 * IN                                                 # 7 1/2 in gauge
RET_BAR_W = 4.5 * IN                                                  # inner bars, centred on the gauge lines
RET_BAR = {'interior': (3 / 8 * IN, 33 * IN), 'exterior': (5 / 8 * IN, 45 * IN)}   # thickness, length (1 1/2 in ends)
SHOE_HALF_X = .115                                                    # 230 mm top shoe / shim (sheet 14, round 1)
SHOULDER = .100                                                       # sheet 17 typical beam haunch, 100 (+/-25)
PLATE_RAMP = .0005                                                    # haunch steps down 0.5 mm beyond a plate end
END_EXT = .150                                                        # sheet 10 Detail A: beam end beyond bent C/L
HAUNCH_TABLE = np.array([50, 50, 62, 73, 95, 73, 62, 50, 50]) / 1000  # sheet 17, by model index (symmetric)
LENGTH = (211 + 2.75 / 12) * FT
LEDGE = 216.850 - 210                                                 # sheet 9: retained pavement ledge, level
APPROACH_T = 12 * IN
APPROACH_HALF = (50 + 4.125 / 12) * FT / 2
GAUGE = .095                                                          # half of the 190 mm flange bolt gauge
BOLT_X = np.array([-.2, -.125, -.05, .05, .125, .2])                  # 40 + 2 @ 75 + 50 | 50 + 2 @ 75 + 40 in 480
BOLT_R = .011
OLD_P3_HALF = np.array([.565] + [111 * IN / 2] * 7 + [.565])          # round-2 Pier 3 flange plate half lengths
P3_PLATE_W = np.array([.292] + [12 * IN] * 7 + [.292])

# Diaphragms (round 2 rules and profiles; sheet 15 end gaps).
EXT_BOTTOM = .200
BC_ROWS = range(3, 8)
C380_BAY = 2                                                          # drawing beam lines 6-7 = Y -3.556..-1.778
CH_B, CH_TW, CH_TF = .105, .011, .017                                 # generator's nominal channel profile
W460 = dict(d=.46, bf=.154, tw=.0091, tf=.0154)
MC_GAP, C380_GAP, STUB_L = .025, .070, .200
SPAN = 'ABCD'


def channel(h):
    return [(-CH_B / 2, 0), (CH_B / 2, 0), (CH_B / 2, CH_TF), (-CH_B / 2 + CH_TW, CH_TF), (-CH_B / 2 + CH_TW, h - CH_TF),
            (CH_B / 2, h - CH_TF), (CH_B / 2, h), (-CH_B / 2, h)]


def sweep(profiles, stations, fn):
    """Closed prism through `stations`; `profiles` is one point list per station (same point count and order).

    Points (a, b) map by fn(station, a, b) -> (x, y, z). The end caps use a constrained Delaunay triangulation of the
    first and last profiles; the solid is oriented by its signed volume (as in the round 1-2 scripts, which avoid the
    earcut/graph dependencies of bridge_geometry.sweep).
    """
    if not isinstance(profiles[0][0], (tuple, list)):
        profiles = [profiles] * len(stations)
    profiles = [[(float(a), float(b)) for a, b in p] for p in profiles]
    n = len(profiles[0])

    def cap(pts):
        poly = shapely.Polygon(pts)
        if not poly.is_valid or poly.area <= 0:
            raise ValueError('invalid sweep profile')
        sign = 1 if poly.exterior.is_ccw else -1
        out = []
        for tri in shapely.get_parts(shapely.constrained_delaunay_triangles(poly)):
            ring = list(tri.exterior.coords)[:3]
            q = [int(np.argmin([(x - a) ** 2 + (y - b) ** 2 for a, b in pts])) for x, y in ring]
            (ux, uy), (vx, vy) = np.subtract(pts[q[1]], pts[q[0]]), np.subtract(pts[q[2]], pts[q[0]])
            out.append(q if (ux * vy - uy * vx) * sign > 0 else q[::-1])
        return np.array(out)
    first, last_cap = cap(profiles[0]), cap(profiles[-1])
    last = (len(stations) - 1) * n
    vertices = np.array([fn(float(s), a, b) for s, p in zip(stations, profiles) for a, b in p], dtype=np.float64)
    sides = []
    for k in range(len(stations) - 1):
        for j in range(n):
            a, b = k * n + j, k * n + (j + 1) % n
            sides += [(a, b, b + n), (a, b + n, a + n)]
    for flip in (False, True):
        c0, c1 = (first[:, ::-1], last_cap[:, ::-1]) if flip else (first, last_cap)
        mesh = trimesh.Trimesh(vertices, np.vstack([sides, c0[:, ::-1], c1 + last]), process=False)
        if mesh.is_winding_consistent:
            break
    if mesh.volume < 0:
        mesh.invert()
    if not (mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0):
        raise ValueError('sweep did not produce a closed solid')
    return mesh


def grade(x):
    return 7.371 - .00394 * np.asarray(x) ** 2 / 65


def surface(x, y):
    return grade(x) - .02 * np.abs(y)


def soffit(x, y):
    return surface(x, y) - SLAB


def nominal_bottom(j, x):
    return surface(x, YS[j]) - SLAB - CLEAR - OLD_DEPTH[j]


def cap24(y):
    return CAP24_CENTRAL if abs(y) < CENTRAL_HALF else CAP24_OUTER


def cap3(y):
    return CAP3_CENTRAL if abs(y) < CENTRAL_HALF else CAP3_OUTER


BENT_BOTTOM = PILE_CUTOFF + BENT_PLATE
P24_BOTTOM = np.array([cap24(y) for y in YS]) + BEARING24 + SHIM24
P3_BOTTOM = np.array([cap3(y) for y in YS]) + SHOE3 + SHIM3 + PLATE3
D_BENT = np.array([BENT_BOTTOM[j] - nominal_bottom(j, B1) for j in range(9)])
D_P24 = np.array([P24_BOTTOM[j] - nominal_bottom(j, P2) for j in range(9)])
D_P3 = np.array([P3_BOTTOM[j] - nominal_bottom(j, P3) for j in range(9)])


def stub_line(j):
    return j not in (0, 8)


def section(i, j, x):
    """Section of model beam segment i on line j at station x."""
    if j in (0, 8):
        return W840
    if i in (0, 3):
        return W201
    if (i == 1 and x < XS[1]) or (i == 2 and x > XS[3]):
        return W201
    return W223


def lift(i, j, x, kind):
    """Raise of the bottom-flange underside above the nominal profile; kind is the section label at x."""
    if i == 0:
        return float(np.interp(x, [B1, P2], [D_BENT[j], D_P24[j]]))
    if i == 3:
        return float(np.interp(x, [P4, B5], [D_P24[j], D_BENT[j]]))
    u = x if i == 1 else 2 * P3 - x                                   # mirror span C onto span B
    knots, values = [P2, P3 - PLATEAU, P3], [D_P24[j], D_P3[j], D_P3[j]]
    if not stub_line(j) or kind == W201['label']:
        return float(np.interp(u, knots, values))
    at_splice = float(np.interp(XS[1], knots, values))
    return float(np.interp(u, [XS[1], P3 - PLATEAU, P3], [at_splice - STEP, D_P3[j], D_P3[j]]))


def bottom(i, j, x, kind=None):
    kind = kind or section(i, j, x)['label']
    return float(nominal_bottom(j, x)) + lift(i, j, x, kind)


def beam_stations(i, j):
    a, b = BS[i], BS[i + 1]
    st = list(np.linspace(a, b, max(3, int((b - a) / .6) + 1)))
    if i in (1, 2):
        st.append(P3 - PLATEAU if i == 1 else P3 + PLATEAU)
    if i in (0, 3):                                                   # sheet 10 Detail A: end 150 mm beyond the C/L
        st.append(B1 - END_EXT if i == 0 else B5 + END_EXT)
    st = sorted(set(np.round(st, 9)))
    if stub_line(j) and i in (1, 2):
        xs = XS[1 if i == 1 else 3]
        st = [s for s in st if abs(s - xs) > .01] + [xs - EPS / 2, xs + EPS / 2]
    return sorted(st)


def env(i, j, x, side=None):
    """Bottom, top, mid-depth and flange undersides of the beam at x; side picks the section at a step station."""
    sec = section(i, j, x) if side is None else side
    z0 = bottom(i, j, x, sec['label'])
    return dict(bottom=z0, top=z0 + sec['d'], mid=z0 + sec['d'] / 2, top_under=z0 + sec['d'] - sec['tf'],
                bottom_over=z0 + sec['tf'], sec=sec)


def to_gltf(v):
    return np.c_[v[:, 0], v[:, 2], -v[:, 1]]


def plate_sweep(y0, y1, stations, level, z0, z1):
    """Plate between y0..y1 whose underside is level(x) + z0 and top level(x) + z1 (piecewise linear)."""
    lv = [float(level(s)) for s in stations]
    return sweep([(y0, z0), (y1, z0), (y1, z1), (y0, z1)], stations,
                 lambda s, a, b: (s, a, float(np.interp(s, stations, lv)) + b))


def end_bent_mesh(u, end, ledge=None):
    """Integral bent of rounds 1-2 (deck-soffit top with crown crease); ledge None = on the 12 in approach soffit."""
    span_face, back_face, deck_end, base = u - end * .4, u + end * .4, end * LENGTH / 2, 5.443
    ref_ledge = float(grade(u)) - APPROACH_T - base
    ref_soffit = float(grade(u)) - SLAB - base

    def point(y, x, b):
        lv = float(surface(x, y)) - APPROACH_T if ledge is None else ledge
        levels = [base, lv, float(surface(x, y)) - SLAB]
        return x, y, float(np.interp(b, [0, ref_ledge, ref_soffit], levels))
    profile = [(span_face, 0), (back_face, 0), (back_face, ref_ledge), (deck_end, ref_ledge),
               (deck_end, ref_soffit), (span_face, ref_soffit)]
    return sweep(profile, [-7.991, 0, 7.991], point)


def approach_mesh(end, seat=None):
    """2026 approach slab (generator stations, 12 in); with seat, its soffit over the bent ledge is at that level."""
    a, b = sorted([end * (LENGTH / 2 + .015), end * (LENGTH / 2 + .015 + 20.5 * FT)])
    st = [float(s) for s in np.linspace(a, b, max(2, int((b - a) / .6) + 1))]
    back = BS[4] + .4 if end > 0 else BS[0] - .4                      # back face of the bent
    if seat is not None:
        st = sorted(set(st) | {back, back + end * EPS})
    on_seat = (lambda s: seat is not None and (s <= back + 1e-9 if end > 0 else s >= back - 1e-9))

    def point(s, y, k):
        top = float(surface(s, y))
        return s, y, (top if k else (seat if on_seat(s) else top - APPROACH_T))
    return sweep([(-APPROACH_HALF, 0), (0, 0), (APPROACH_HALF, 0), (APPROACH_HALF, 1), (0, 1), (-APPROACH_HALF, 1)],
                 st, point)


def correct(base_dir=None, backup_dir=None):
    base = Path(base_dir) if base_dir else ROOT / 'data/bridges' / BID
    mp = base / 'model_manifest.json'
    raw_manifest = mp.read_bytes()
    manifest = json.loads(raw_manifest.decode('utf-8'))
    if manifest.get('review_correction_3') == TAG:
        print('Already corrected.')
        return
    if manifest.get('review_correction_2') != PREVIOUS_TAG or manifest.get('revision') != PREVIOUS_REVISION:
        raise ValueError('Run scripts/correct_sr10_i65_review_2.py first (expected revision 1.2-drawing-review-2).')
    if 'review_correction_3' in manifest or 'review_correction_record_3' in manifest:
        raise ValueError('Manifest carries an unknown third correction.')
    path = base / 'model.glb'
    original = path.read_bytes()
    before = hashlib.sha256(original).hexdigest()
    if manifest['review_correction_2_record']['after_glb_sha256'] != before:
        raise ValueError('model.glb is not the output of the second review correction.')
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

    current = {}

    def native(pid):
        if pid in current:
            return current[pid][0].copy(), current[pid][1]
        prim = meshes[pid]['primitives'][0]
        g = read(prim['attributes']['POSITION']).astype(np.float64)
        return np.c_[g[:, 0], -g[:, 2], g[:, 1]], read(prim['indices']).reshape(-1, 3)

    changed, renamed = [], {}

    def store(pid, vertices, faces=None, dims=None, drop_dims=(), note='', replace_note=False, name=None, basis=None,
              pages=()):
        prim = meshes[pid]['primitives'][0]
        old_faces = read(prim['indices']).reshape(-1, 3)
        new_faces = old_faces if faces is None else np.asarray(faces)
        solid = trimesh.Trimesh(vertices=vertices, faces=new_faces, process=False)
        if not solid.is_watertight or solid.volume <= 0:
            raise ValueError(f'{pid}: corrected mesh is not a valid solid')
        same = (len(vertices) == gltf['accessors'][prim['attributes']['POSITION']]['count']
                and np.array_equal(new_faces, old_faces))
        prim['attributes']['POSITION'] = append(to_gltf(vertices).astype('<f4'), 'VEC3', 5126)
        if not same:
            color = read(prim['attributes']['COLOR_0'])[0]
            prim['attributes']['COLOR_0'] = append(np.tile(color, (len(vertices), 1)).astype('u1'), 'VEC4', 5121)
            gltf['accessors'][prim['attributes']['COLOR_0']]['normalized'] = True
            prim['indices'] = append(new_faces.reshape(-1, 1).astype('<u4'), 'SCALAR', 5125)
        stored = read(prim['attributes']['POSITION']).astype(np.float64)
        current[pid] = (np.c_[stored[:, 0], -stored[:, 2], stored[:, 1]], new_faces)
        p = parts[pid]
        p['bounds_m'] = np.round(solid.bounds, 6).tolist()
        p['volume_m3'] = round(float(solid.volume), 9)
        for k in drop_dims:
            p['dimensions'].pop(k, None)
        if dims is not None:
            p['dimensions'].update(dims)
        if name and name != p['name']:
            renamed[pid] = dict(before=p['name'], after=name)
            p['name'] = name
        if basis:
            p['basis'] = basis
        p['pdf_pages'] = sorted(set(p['pdf_pages']) | set(pages))
        p['note'] = note if replace_note else (p.get('note', '') + ' ' + note).strip()
        extras = meshes[pid]['extras']
        for k in drop_dims:
            extras.get('dimensions', {}).pop(k, None)
        extras.update({k: p[k] for k in ('name', 'layer', 'color', 'pdf_pages', 'basis', 'note', 'dimensions')})
        if pid not in changed:
            changed.append(pid)
        return solid

    def store_mesh(pid, mesh, **kw):
        mesh.remove_unreferenced_vertices()
        if mesh.volume < 0:
            mesh.invert()
        return store(pid, np.asarray(mesh.vertices, dtype=np.float64), np.asarray(mesh.faces), **kw)

    world = gltf['nodes'][gltf['scenes'][gltf.get('scene', 0)]['nodes'][0]]
    added, added_after = [], {}

    def add_part(pid, mesh, like, after, name, layer, pages, basis, note, dims):
        mesh.remove_unreferenced_vertices()
        if mesh.volume < 0:
            mesh.invert()
        if pid in parts or pid in meshes:
            raise ValueError(f'{pid} already exists')
        if not (mesh.is_watertight and mesh.volume > 0):
            raise ValueError(f'{pid}: new mesh is not a valid solid')
        color = parts[like]['color']
        p = dict(id=pid, name=name, layer=layer, color=color, pdf_pages=sorted(pages), basis=basis, note=note,
                 dimensions=dims, bounds_m=np.round(mesh.bounds, 6).tolist(), volume_m3=round(float(mesh.volume), 9))
        v = np.asarray(mesh.vertices, dtype=np.float64)
        rgba = np.tile([int(color[k:k + 2], 16) for k in (1, 3, 5)] + [255], (len(v), 1)).astype('u1')
        prim = dict(attributes=dict(POSITION=append(to_gltf(v).astype('<f4'), 'VEC3', 5126),
                                    COLOR_0=append(rgba, 'VEC4', 5121)),
                    indices=append(np.asarray(mesh.faces).reshape(-1, 1).astype('<u4'), 'SCALAR', 5125), mode=4)
        gltf['accessors'][prim['attributes']['COLOR_0']]['normalized'] = True
        gltf['meshes'].append(dict(name=pid, extras=dict(processed=True, **{k: p[k] for k in (
            'id', 'name', 'layer', 'color', 'pdf_pages', 'basis', 'note', 'dimensions')}), primitives=[prim]))
        gltf['nodes'].append(dict(name=pid, mesh=len(gltf['meshes']) - 1))
        world['children'].append(len(gltf['nodes']) - 1)
        meshes[pid] = gltf['meshes'][-1]
        manifest['parts'].insert(manifest['parts'].index(parts[after]) + 1, p)
        parts[pid] = p
        stored = read(prim['attributes']['POSITION']).astype(np.float64)
        current[pid] = (np.c_[stored[:, 0], -stored[:, 2], stored[:, 1]], np.asarray(mesh.faces))
        added.append(pid)
        added_after[pid] = after

    def expect(cond, message):
        if not cond:
            raise ValueError('Model is not in the expected state after the second correction: ' + message)

    def bounds(pid):
        v, _ = native(pid)
        return v.min(axis=0), v.max(axis=0)

    def mesh_profile(i, j):
        v, _ = native(f'beam_{i}_{j}')
        xs = np.unique(np.round(v[:, 0], 5))
        lo = np.array([v[np.abs(v[:, 0] - x) < 1e-4, 2].min() for x in xs])
        hi = np.array([v[np.abs(v[:, 0] - x) < 1e-4, 2].max() for x in xs])
        return xs, lo, hi

    def beam_at(j, x):
        i = int(np.clip(np.searchsorted(BS, x, side='right') - 1, 0, 3))
        xs, lo, hi = mesh_profile(i, j)
        return float(np.interp(x, xs, lo)), float(np.interp(x, xs, hi))

    # ---------------------------------------------------------------- expected starting state
    for j in range(9):
        for i in range(4):
            xs, lo, hi = mesh_profile(i, j)
            expect(np.allclose(hi - lo, OLD_DEPTH[j], atol=TOL), f'beam_{i}_{j} nominal depth')
        for i, x in ((0, B1), (0, P2), (1, P2), (2, P4), (3, P4), (3, B5)):
            xs, lo, _ = mesh_profile(i, j)
            at = int(np.argmin(np.abs(xs - x)))
            expect(abs(xs[at] - x) < 1e-4 and abs(lo[at] - nominal_bottom(j, x)) < TOL,
                   f'beam_{i}_{j} nominal bottom at X {x:.3f}')
        for i in (1, 2):
            xs, lo, _ = mesh_profile(i, j)
            at = int(np.argmin(np.abs(xs - P3)))
            expect(abs(lo[at] - P3_BOTTOM[j]) < TOL, f'beam_{i}_{j} on the Pier 3 stack')
        expect(abs(bounds(f'B3_seat_{j}')[1][2] + PLATE3[j] - P3_BOTTOM[j]) < TOL, f'B3_seat_{j} top')
        for q in (1, 3):
            lo, hi = bounds(f'beam_{j + 1}_splice_{q}')
            expect(np.allclose([lo[0], hi[0]], [XS[q] - .565, XS[q] + .565], atol=1e-4), f'splice_{q} station')
        lo, hi = bounds(f'beam_{j + 1}_splice_2')
        expect(np.allclose([lo[0], hi[0]], [P3 - OLD_P3_HALF[j], P3 + OLD_P3_HALF[j]], atol=1e-4), 'Pier 3 splice')
        for bi, x in ((2, P2), (4, P4)):
            lo, hi = bounds(f'B{bi}_bearing_{j + 1}')
            expect(abs(hi[2] - nominal_bottom(j, x)) < TOL and abs(hi[2] - lo[2] - BEARING24) < TOL
                   and np.allclose([hi[0] - lo[0], hi[1] - lo[1]], [LOAD_PLATE[0], LOAD_PLATE[1]], atol=1e-5),
                   f'B{bi}_bearing_{j + 1}')
    for bi in (2, 4):
        expect(np.isclose(bounds(f'pier_{bi}_widening')[1][2], OLD_CAP24, atol=TOL), f'pier_{bi}_widening top')
        seats = sorted(k for k in parts if k.startswith(f'B{bi}_seat_'))
        expect(seats == [f'B{bi}_seat_{j}' for j in (0, 2, 3, 4, 5, 6, 8)], f'B{bi} seat risers')
        for k in seats:
            expect(np.isclose(bounds(k)[0][2], OLD_CAP24, atol=TOL), f'{k} on the old cap')
    rows = {}
    for q in range(11):
        lo, hi = bounds(f'diaphragm_{q}_0')
        rows[q] = (lo[0] + hi[0]) / 2
    expect(np.allclose([rows[q] for q in range(11)],
                       np.r_[B1 + np.array([1.7, 6.8, 11.9]), P2 + np.array([6.833, 13.437, 19.584]),
                             P3 + np.array([6.604, 13.208, 20.041]), P4 + np.array([5.1, 10.2])], atol=1e-4),
           'diaphragm row stations')
    sections_before = manifest['review_correction_2_record']['diaphragm_sections']
    expect(sections_before == {'MC460x63.5': 58, 'W460x68': 25, 'C380x74': 5}, 'diaphragm sections')
    for q in range(11):
        for j in range(8):
            lo, hi = bounds(f'diaphragm_{q}_{j}')
            expect(np.allclose([lo[1], hi[1]], [YS[j] + .16, YS[j + 1] - .16], atol=1e-5), f'diaphragm_{q}_{j} ends')
    for bi, u, end in ((1, B1, -1), (5, B5, 1)):
        v, _ = native(f'end_bent_{bi}')
        old = np.asarray(end_bent_mesh(u, end).vertices)
        expect(len(v) == len(old) and np.allclose(np.sort(v, axis=0), np.sort(old, axis=0), atol=TOL),
               f'end_bent_{bi} ledge on the 12 in approach soffit')
        v, _ = native(f'approach_{end}')
        old = np.asarray(approach_mesh(end).vertices)
        expect(len(v) == len(old) and np.allclose(np.sort(v, axis=0), np.sort(old, axis=0), atol=TOL),
               f'approach_{end} 12 in slab')
    for j in range(9):
        lo, hi = bounds(f'beam_0_{j}')
        expect(np.isclose(lo[0], B1, atol=1e-5) and np.isclose(bounds(f'beam_3_{j}')[1][0], B5, atol=1e-5),
               f'end beams of line index {j} stop at the bent centre lines')

    # ---------------------------------------------------------------- 1-3. beams and haunches
    beam_note = ('Depth {d:.0f} mm and flange thickness {tf:.1f} mm ({label}, ASTM A6 values of the drawn '
                 'designation); flange width and web nominal, fillets omitted. Interior end beams splice 900 mm inside the middle spans; the model divides '
                 'selectable members at supports. Bottom flange on the drawing support elevations: Bents 1/5 pile cutoff '
                 '+ PL 19 mm (sheets 9-10), Piers 2/4 cap El. 215.972 / 216.016 + 125 mm Type I bearing + shim (sheets '
                 '11, 14, 16), Pier 3 cap + 260 mm shoe + shim + flange cover plate (sheets 12, 14, 16; 1964 S9); '
                 'linear between supports on the grade-parallel profile (sheet 16 blocking diagram), constant over the '
                 '1.13 m Pier 3 splice. Raise above the nominal profile (1998 grade - 200 mm slab - 75 mm - 920/840 mm): '
                 '{lift}. Review correction 3 (rounds 1-2 fitted Pier 3 only and tapered to zero at Piers 2/4; the '
                 'nominal depth was 920 mm).')
    hmin, hdata = {}, {}

    def make_haunch(i, j, plates=()):
        """Sheet 17 haunch on the beam, exactly on its piecewise-linear top flange, seated on the top splice plates.

        plates: (x_lo, x_hi, stations, top levels) of the top splice plates on this line; over them the haunch bottom is
        the plate top (the plates cover the flange width), with a 0.5 mm ramp down to the flange beyond each plate end.
        """
        st, sides, z0, y = hdata[(i, j)]
        bx = np.array(st, dtype=float)
        btop = np.array([z0[float(s)] + sec['d'] for s, sec in zip(st, sides)])
        bund = np.array([z0[float(s)] + sec['d'] - sec['tf'] for s, sec in zip(st, sides)])
        lo_x, hi_x = float(st[0]), float(st[-1])
        if i in (0, 3):                                               # concrete of the integral bent beyond its face
            face = B1 + .4 if i == 0 else B5 - .4
            lo_x, hi_x = (face, hi_x) if i == 0 else (lo_x, face)
        hst = {float(s) for s in st if lo_x - 1e-9 <= s <= hi_x + 1e-9} | {lo_x, hi_x}
        for plo, phi, pxs, ptop in plates:
            hst |= {float(s) for s in pxs if lo_x - 1e-9 <= s <= hi_x + 1e-9}
        for plo, phi, pxs, ptop in plates:
            for edge, out in ((plo, plo - PLATE_RAMP), (phi, phi + PLATE_RAMP)):
                if lo_x < out < hi_x:
                    hst = {s for s in hst if not (min(edge, out) < s < max(edge, out))} | {float(out)}
        merged = []
        for s_ in sorted(hst):                                        # drop near-duplicates (float32 plate stations)
            if merged and s_ - merged[-1] < 2e-5:
                if any(abs(s_ - float(b)) < 1e-9 for b in bx):        # keep the beam station
                    merged[-1] = s_
                continue
            merged.append(s_)
        hst = merged

        def level(s):
            for plo, phi, pxs, ptop in plates:
                if plo - 1e-9 <= s <= phi + 1e-9:
                    return float(np.interp(s, pxs, ptop))
            return float(np.interp(s, bx, btop))
        tops = {s: level(s) for s in hst}
        unders = {s: float(np.interp(s, bx, bund)) for s in hst}
        w = sides[0]['bf']
        wide = w / 2 + SHOULDER
        rep = ([(-wide, -1), (-w / 2, -1), (-w / 2, 0), (w / 2, 0), (w / 2, -1), (wide, -1), (wide, 2)]
               + ([(0, 2.05)] if y == 0 else []) + [(-wide, 2)])

        def hpoint(s, v, b):
            z = unders[s] if b < -.5 else tops[s] if b < .5 else float(soffit(s, y + v))
            return s, y + v, z
        haunch = sweep(rep, hst, hpoint)
        hv = np.asarray(haunch.vertices)
        role = np.array([b for _ in hst for _, b in rep])
        flange_top, soffit_pts = role == 0, role > 1
        expect(np.allclose(hv[soffit_pts, 2], soffit(hv[soffit_pts, 0], hv[soffit_pts, 1]), atol=1e-9)
               and np.allclose(hv[flange_top, 2], [tops[float(x)] for x in hv[flange_top, 0]], atol=1e-9),
               f'haunch_{i}_{j} faces')
        over = np.array([not any(plo - 1e-9 <= x <= phi + 1e-9 for plo, phi, _, _ in plates) for x in hv[:, 0]])
        thick = soffit(hv[flange_top & over, 0], hv[flange_top & over, 1]) - hv[flange_top & over, 2]
        hmin[(i, j)] = float(thick.min())
        if hmin[(i, j)] < .01:
            raise ValueError(f'haunch_{i}_{j}: thinner than 10 mm')
        dim_a = np.array([float(soffit(s, y)) - unders[s] for s in hst])
        info = dict(minimum_thickness_m=round(hmin[(i, j)], 4), maximum_thickness_m=round(float(thick.max()), 4),
                    width_m=round(2 * wide, 4), shoulder_m=SHOULDER,
                    dimension_a_m=[round(float(dim_a.min()), 4), round(float(dim_a.max()), 4)])
        note = ('Concrete between the deck soffit and the top flange of the fitted beam. Sheet 17 Typical Beam Haunch '
                'Detail: 100 mm (+/-25) wider than the flange each side, the shoulders down to the underside of the top '
                'flange, so it encases the flange edges; Dimension "A" (soffit to the flange underside) follows from the '
                'support elevations. Top on the deck soffit' + (', with the crown ridge' if y == 0 else '') +
                (f'; starts at the span face of the integral Bent {1 if i == 0 else 5}' if i in (0, 3) else '') +
                ('; over the field splices it sits on the top splice plates, with pockets for the fastener heads'
                 if plates else '') + '. Review correction 3: was the flange width only, on the flange top, over a '
                'nominal 75 mm.')
        return haunch, info, note, level

    def store_haunch(i, j, haunch, info, note):
        store_mesh(f'haunch_{i}_{j}', haunch, drop_dims=('nominal_thickness_m',), dims=info, replace_note=True,
                   pages=[29, 30, 31, 36, 37], note=note,
                   basis='Sheet 17 typical beam haunch detail; deck soffit to the drawing-fitted beam')

    for j in range(9):
        y = YS[j]
        for i in range(4):
            st = beam_stations(i, j)
            sides = []
            for s in st:
                if stub_line(j) and i in (1, 2) and abs(s - XS[1 if i == 1 else 3]) < EPS:
                    left = W201 if i == 1 else W223
                    sides.append(left if s < XS[1 if i == 1 else 3] else (W223 if i == 1 else W201))
                else:
                    sides.append(section(i, j, s))
            profiles = [iform(sec['d'], sec['bf'], sec['tw'], sec['tf']) for sec in sides]
            z0 = {float(s): bottom(i, j, s, sec['label']) for s, sec in zip(st, sides)}
            mesh = sweep(profiles, st, lambda s, a, b: (s, y + a, z0[s] + b))
            main = sides[len(sides) // 2]
            dims = dict(depth_m=main['d'], flange_thickness_m=main['tf'], length_m=round(float(st[-1] - st[0]), 4))
            pid = f'beam_{i}_{j}'
            ends = {0: ('Bent 1', D_BENT[j], 'Pier 2', D_P24[j]), 1: ('Pier 2', D_P24[j], 'Pier 3', D_P3[j]),
                    2: ('Pier 3', D_P3[j], 'Pier 4', D_P24[j]), 3: ('Pier 4', D_P24[j], 'Bent 5', D_BENT[j])}[i]
            note = beam_note.format(d=main['d'] * 1000, tf=main['tf'] * 1000, label=main['label'],
                                    lift=f'{ends[1] * 1000:+.1f} mm at {ends[0]}, {ends[3] * 1000:+.1f} mm at {ends[2]}')
            if stub_line(j) and i in (1, 2):
                dims.update(stub_section='W920x201', stub_depth_m=W201['d'], stub_length_m=.9)
                note += (' The first 900 mm from Pier {} is the new W920x201 (903 mm), centred on the W920x223 at the '
                         'Type II splice (sheet 13 "Existing beams to be cut off 900 mm from C/L Pier"; sheet 14 4 mm '
                         'fillers); the step is 4 mm at each flange.').format(2 if i == 1 else 4)
            if i in (0, 3):
                note += (' The end extends 150 mm beyond the Bent {} centre line into the integral bent (sheet 10 Detail A; '
                         'was cut at the centre line).').format(1 if i == 0 else 5)
            store_mesh(pid, mesh, dims=dims, note=note, replace_note=True, pages=[29, 30, 31, 33, 34, 36],
                       basis='Drawing section designation with its catalog depth and flange thickness; support '
                             'elevations from sheets 9-12, 14 and 16')
            hdata[(i, j)] = (st, sides, z0, y)
            if i in (0, 3):
                store_haunch(i, j, *make_haunch(i, j)[:3])

    # ---------------------------------------------------------------- 4. Pier 2/4-side splices (sheet 14)
    def splice_pieces(i, j, xs, kind, pid_note):
        y = YS[j]
        pt, pw, pl = kind['plate']
        bt, bw, bl = kind['bar']
        wt, ww, wh = kind['web']
        half = pl / 2
        stub_side = (lambda s: s < xs) if i == 1 else (lambda s: s > xs)
        two = stub_line(j) and xs not in (P3,)

        def e(s, side=None):
            if not two:
                return env(i, j, s)
            if side is None:
                side = 'stub' if stub_side(s) else 'main'
            return env(i, j, s, W201 if side == 'stub' else W223)

        def outer_top(s):                                             # W920x223 flange level (fillers on the stub)
            r = e(s, 'main' if two and abs(s - xs) < 1e-9 else None)
            return r['top'] + (STEP if two and r['sec'] is W201 else 0)

        def outer_bottom(s):
            r = e(s, 'main' if two and abs(s - xs) < 1e-9 else None)
            return r['bottom'] - (STEP if two and r['sec'] is W201 else 0)

        def under(s):                                                 # bars bear on the lower flange face
            if two:                                                   # (the two inner faces differ by 0.2 mm)
                return min(env(i, j, s, W201)['top_under'], env(i, j, s, W223)['top_under'])
            return e(s)['top_under']

        def over(s):
            if two:
                return max(env(i, j, s, W201)['bottom_over'], env(i, j, s, W223)['bottom_over'])
            return e(s)['bottom_over']

        def mid(s):
            return e(s, 'main' if two and abs(s - xs) < 1e-9 else None)['mid']
        st = [xs - half, xs, xs + half]
        pieces = [plate_sweep(y - pw / 2, y + pw / 2, st, outer_top, 0, pt),
                  plate_sweep(y - pw / 2, y + pw / 2, st, outer_bottom, -pt, 0)]
        for sgn in (-1, 1):
            ya, yb = sorted([y + sgn * (GAUGE - bw / 2), y + sgn * (GAUGE + bw / 2)])
            pieces += [plate_sweep(ya, yb, st, under, -bt, 0), plate_sweep(ya, yb, st, over, 0, bt)]
        tw = W223['tw'] if two else e(xs)['sec']['tw']
        wst = [xs - ww / 2, xs, xs + ww / 2]
        for sgn in (-1, 1):
            ya, yb = sorted([y + sgn * tw / 2, y + sgn * (tw / 2 + wt)])
            pieces.append(plate_sweep(ya, yb, wst, mid, -wh / 2, wh / 2))
        if kind['filler'] and two:
            ft, fw, fl = kind['filler']
            fst = sorted([xs, xs - fl if i == 1 else xs + fl])
            fst = [fst[0], fst[1]]

            def stub_top(s):
                return env(i, j, s, W201)['top']

            def stub_bottom(s):
                return env(i, j, s, W201)['bottom']
            pieces += [plate_sweep(y - fw / 2, y + fw / 2, fst, stub_top, 0, ft),
                       plate_sweep(y - fw / 2, y + fw / 2, fst, stub_bottom, -ft, 0)]
        fasteners = []
        for dx in BOLT_X:
            zc = mid(xs + dx)
            for k in range(-3, 4):
                z = zc + k * kind['pitch']
                fasteners.append(bolt([xs + dx, y - tw / 2 - wt, z], [xs + dx, y + tw / 2 + wt, z], BOLT_R))
        n_flange = 0
        for n in range(kind['flange_cols']):
            for sx in (-1, 1):
                x = xs + sx * (FLANGE_X0 + n * FLANGE_PITCH)
                for yg in (y - GAUGE, y + GAUGE):
                    # top flange: head on the outer plate, nut under the inner bar
                    fasteners.append(bolt([x, yg, outer_top(x) + pt], [x, yg, under(x) - bt], BOLT_R))
                    n_flange += 1
                    if n:                                             # inner pair: open holes for the top shoes
                        fasteners.append(bolt([x, yg, outer_bottom(x) - pt], [x, yg, over(x) + bt], BOLT_R))
                        n_flange += 1
        return concat(pieces), concat(fasteners), tw, n_flange

    clear_top = {}
    for j in range(9):
        kind = TYPE_I if j in (0, 8) else TYPE_II
        for q, i in ((1, 1), (3, 2)):
            xs = XS[q]
            plates, fasteners, tw, n_flange = splice_pieces(i, j, xs, kind, '')
            pid = f'beam_{j + 1}_splice_{q}'
            pt, pw, pl = kind['plate']
            bt, bw, bl = kind['bar']
            wt, ww, wh = kind['web']
            text = (f'New {kind["name"]} beam splice, sheet 14 (located by sheet 13 beam elevations, 900 mm from the '
                    f'Pier {2 if q == 1 else 4} centre line): flange plates PL {pt * 1000:.0f}x{pw * 1000:.0f}x'
                    f'{pl * 1000:.0f} top and bottom, 2 bars {bt * 1000:.0f}x{bw * 1000:.0f}x{bl * 1000:.0f} inside '
                    f'each flange on the 190 mm bolt gauge, web plates 2-PL {wt * 1000:.0f}x{ww * 1000:.0f}x'
                    f'{wh * 1000:.0f}')
            if kind['filler']:
                text += ('; fillers PL 4x305x485 top and bottom on the W920x201 side, between its flanges and the '
                         'plates (W920x201 903 mm centred on the W920x223 911 mm)')
            text += ('. Plates follow the fitted beam. Review correction 3: was a generic envelope of 13 mm x 1.13 m '
                     'flange plates without bars. Fabrication holes omitted.')
            dims = dict(splice_type=kind['name'], flange_plate_thickness_m=pt, flange_plate_width_m=pw,
                        flange_plate_length_m=pl, inner_bar_thickness_m=bt, inner_bar_width_m=bw,
                        web_plate_width_m=ww, web_plate_height_m=wh)
            if kind['filler']:
                dims.update(filler_thickness_m=kind['filler'][0], filler_length_m=kind['filler'][2])
            solid = store_mesh(pid, plates, replace_note=True, note=text, dims=dims, pages=[33, 34],
                               basis='Sheet 14 dimensioned splice detail; sheet 13 splice locations')
            tv = current[pid][0]
            tv = tv[tv[:, 2] > env(i, j, xs, W223 if stub_line(j) else None)['top'] - .001]   # top plate
            clear_top[pid] = float((soffit(tv[:, 0], tv[:, 1]) - tv[:, 2]).min())
            store_mesh(pid + '_bolts', fasteners, replace_note=True, pages=[33, 34],
                       basis='Sheet 14 web and flange bolt patterns',
                       note=f'Bolts of the {kind["name"]} splice per sheet 14, 22 mm A325: web 6 columns (40, 2 @ 75, '
                            f'50 | 50, 2 @ 75, 40 mm in the 480 mm plate) x 7 rows @ {kind["pitch"] * 1000:.0f} mm; '
                            f'flange 2 rows on the 190 mm gauge, {kind["flange_cols"]} per side at 76 + n x 75 mm, '
                            'through plate, flange and bar; the inner pair of the bottom flange are open holes for the '
                            'top shoes (sheet 14 note), so no bolts there. Review correction 3: was a representative '
                            '5 x 7 web grid without flange bolts.',
                       dims=dict(visual_bolt_count=len(BOLT_X) * 7 + n_flange, web_bolts=len(BOLT_X) * 7,
                                 flange_bolts=n_flange, bolt_rows=7, bolt_columns=len(BOLT_X),
                                 row_pitch_m=kind['pitch']))

    # Pier 3 splices: Type I (lines 1/9) rebuilt to the full sheet 14 detail; retained 1964 splices follow the beams.
    for j in range(9):
        pid = f'beam_{j + 1}_splice_2'
        y, half, w, t = YS[j], float(OLD_P3_HALF[j]), float(P3_PLATE_W[j]), float(PLATE3[j])
        st = sorted({P3 - half, P3 + half} | {float(s) for i in (1, 2) for s in beam_stations(i, j)
                                               if abs(s - P3) < half - 1e-3})

        def e3(s, j=j):
            return env(1 if s <= P3 else 2, j, s)
        if j in (0, 8):
            plates, fasteners, tw, n_flange = splice_pieces(1, j, P3, TYPE_I, '')
            # the Type I web plates and bolts use the span B section; both spans are W840 at Pier 3
            store_mesh(pid, plates, replace_note=True, pages=[33, 34],
                       note='On the Pier 3 centre line (sheet 13 "C/L New Type I Splice"). Full sheet 14 Type I detail: '
                            'flange plates PL 16x292x1130 top and bottom (the bottom plate bears on the shim), 2 bars '
                            '13x102x1130 inside each flange, web plates 2-PL 13x480x710. Review correction 3 added the '
                            'inner bars (round 2 had the plates only).',
                       dims=dict(splice_type='Type I', inner_bar_thickness_m=.013, inner_bar_width_m=.102))
            store_mesh(pid + '_bolts', fasteners, replace_note=True, pages=[33, 34],
                       basis='Sheet 14 web and flange bolt patterns',
                       note='Bolts of the Type I splice per sheet 14, 22 mm A325: web 6 columns x 7 rows @ 105 mm; flange '
                            '2 rows on the 190 mm gauge, 7 per side at 76 + n x 75 mm; the inner pair of the bottom '
                            'flange are the open holes through which the top shoe is attached (sheet 14 note). Review '
                            'correction 3: was a representative 5 x 7 web grid.',
                       dims=dict(visual_bolt_count=42 + n_flange, web_bolts=42, flange_bolts=n_flange, bolt_rows=7,
                                 bolt_columns=6, row_pitch_m=.105))
        else:
            v, _ = native(pid)
            web = np.isclose(np.abs(v[:, 0] - P3), .24, atol=1e-5)          # the two 480 mm web plate boxes
            expect(web.sum() == 16, f'{pid} web plates')
            wx = float(np.abs(v[web, 0] - P3).max())
            zc, half_tw = e3(P3)['mid'], W223['tw'] / 2
            pieces = [box(P3 - wx, P3 + wx, y - half_tw - RET_WEB_T, y - half_tw, zc - RET_WEB_H / 2, zc + RET_WEB_H / 2),
                      box(P3 - wx, P3 + wx, y + half_tw, y + half_tw + RET_WEB_T, zc - RET_WEB_H / 2, zc + RET_WEB_H / 2)]
            pieces += [plate_sweep(y - w / 2, y + w / 2, st, lambda s: e3(s)['bottom'], -t, 0),
                       plate_sweep(y - w / 2, y + w / 2, st, lambda s: e3(s)['top'], 0, t)]
            beam_kind = 'exterior' if j in (1, 7) else 'interior'     # 1964 beams 1 and 7 = drawing lines 2 and 8
            bt, bl = RET_BAR[beam_kind]
            bst = sorted({P3 - bl / 2, P3 + bl / 2} | {s for s in st if abs(s - P3) < bl / 2 - 1e-3})
            for sgn in (-1, 1):
                ya, yb = sorted([y + sgn * (RET_GAUGE - RET_BAR_W / 2), y + sgn * (RET_GAUGE + RET_BAR_W / 2)])
                pieces += [plate_sweep(ya, yb, bst, lambda s: e3(s)['top_under'], -bt, 0),
                           plate_sweep(ya, yb, bst, lambda s: e3(s)['bottom_over'], 0, bt)]
            store_mesh(pid, concat(pieces), pages=[11, 33, 34],
                       note='Review correction 3: flange plates follow the refitted 911 mm beam; web plates 2 PL 31 x 1/2 '
                            'in (787.4 x 12.7 mm, 1964 S9; were 770 x 13 mm) centred on the beam, 480 mm long (length '
                            'not dimensioned on S9, envelope kept); inner bars PL 4 1/2 x ' +
                            ('5/8 in x 45 in (exterior 1964 beam)' if beam_kind == 'exterior' else
                             '3/8 in x 33 in (interior 1964 beam)') +
                            ' each side of the web under the top flange and over the bottom flange, centred on the 7 1/2 '
                            'in rivet gauge, ending 1 1/2 in beyond the last rivet of the inner group (1964 S9 plans).',
                       dims=dict(web_plate_height_m=round(RET_WEB_H, 4), web_plate_thickness_m=round(RET_WEB_T, 4),
                                 web_plate_width_m=round(2 * wx, 4), inner_bar_thickness_m=round(bt, 4),
                                 inner_bar_width_m=round(RET_BAR_W, 4), inner_bar_length_m=round(bl, 4)))
            rivets = [bolt([P3 + dx, y - half_tw - RET_WEB_T, zc + dz], [P3 + dx, y + half_tw + RET_WEB_T, zc + dz],
                           BOLT_R) for dx in RET_COLS for dz in RET_ROWS]
            n_web, n_top, n_bottom = len(rivets), 0, 0
            for dx in np.r_[-RET_FLANGE_X[::-1], RET_FLANGE_X]:
                x = P3 + dx
                r = e3(x)
                bar = bt if abs(dx) < bl / 2 else 0.0
                for yg in (y - RET_GAUGE, y + RET_GAUGE):
                    rivets.append(bolt([x, yg, r['top'] + t], [x, yg, r['top_under'] - bar], BOLT_R))
                    n_top += 1
                    if abs(dx) + 1.55 * BOLT_R > SHOE_HALF_X:        # not under the top shoe (treatment not drawn)
                        rivets.append(bolt([x, yg, r['bottom'] - t], [x, yg, r['bottom_over'] + bar], BOLT_R))
                        n_bottom += 1
            store_mesh(pid + '_bolts', concat(rivets), replace_note=True, pages=[11, 33],
                       basis='1964 S9 web and flange splice rivet patterns',
                       note='Rivets of the retained 1964 field splice (1964 S9, interior and exterior beam details), 7/8 '
                            'in as 22 mm visual fasteners. Web: 6 columns, 2 @ 3 in each side of a 4 1/8 in centre gap, '
                            'x 10 rows, 4 @ 3 in each side of a 4 in centre gap. Flanges: 2 gauge lines 7 1/2 in apart, 18 '
                            'per side at 3 in from 3 in to 54 in off the splice centre line, through plate, flange and '
                            'inner bar; top flange all 72; bottom flange without the 4 rivets 3 in off the centre line, '
                            'which lie under the 230 mm top shoe (their treatment is not drawn; known deviation '
                            'pier-3-retained-splice-flange-fasteners). Review correction 3: was a representative 5 x 7 '
                            'web grid.',
                       dims=dict(visual_bolt_count=len(rivets), web_rivets=n_web, top_flange_rivets=n_top,
                                 bottom_flange_rivets=n_bottom, bolt_rows=len(RET_ROWS), bolt_columns=len(RET_COLS),
                                 row_pitch_m=round(3 * IN, 4)))
        tv = current[pid][0]
        top = e3(P3)['top']
        tv = tv[tv[:, 2] > top - .001]
        clear_top[pid] = float((soffit(tv[:, 0], tv[:, 1]) - tv[:, 2]).min())

    # ---------------------------------------------------------------- haunches of spans B/C, on the splice plates
    def manifold(vertices, faces):
        return mf.Manifold(mf.Mesh64(vert_properties=np.ascontiguousarray(vertices, dtype=np.float64),
                                     tri_verts=np.ascontiguousarray(faces, dtype=np.uint64)))

    def welded_closed(mesh):
        """The check of scripts/refresh_geometry_verification.py: every index-connected body, welded at 10 um, is a
        closed 2-manifold with positive volume."""
        faces = np.asarray(mesh.faces)
        parent = np.arange(len(mesh.vertices))

        def find(k):
            while parent[k] != k:
                parent[k] = parent[parent[k]]
                k = parent[k]
            return k
        for a, b, c in faces:
            ra = find(a)
            parent[find(b)] = ra
            parent[find(c)] = ra
        roots = np.array([find(k) for k in faces[:, 0]])
        for root in np.unique(roots):
            body = trimesh.Trimesh(np.asarray(mesh.vertices), faces[roots == root], process=False)
            body.remove_unreferenced_vertices()
            body.merge_vertices(digits_vertex=5)
            if not (body.is_watertight and body.volume > 0):
                return False
        return True

    pockets = {}
    for j in range(9):
        seats, plate_tops, cut_plates = [], [], []
        for q in (1, 2, 3):
            sv, sf = native(f'beam_{j + 1}_splice_{q}')
            top_plate = max((b for b in trimesh.Trimesh(sv, sf, process=False).split(only_watertight=False)
                             if b.extents[0] > .9), key=lambda b: b.bounds[1][2])
            tv = np.asarray(top_plate.vertices)
            pxs = np.unique(np.round(tv[:, 0], 7))
            ptop = np.array([tv[np.abs(tv[:, 0] - x) < 1e-6, 2].max() for x in pxs])
            plate = (float(pxs[0]), float(pxs[-1]), pxs, ptop)
            plate_tops.append(plate)
            if q == 2 and stub_line(j):
                # retained 1964 plate, 304.8 mm on the 305 mm flange: cut out of the haunch with the cutter run 3 mm
                # into the flange, which no haunch face touches (at lines 2/8 its outer edge rises above the soffit,
                # so the haunch cannot sit on it)
                v = tv.copy()
                low = v[:, 2] < np.interp(v[:, 0], pxs, ptop) - float(PLATE3[j]) / 2
                v[low, 2] -= .003
                # its interior stations are beam (and haunch) stations: move them 50 um along the beam so that no
                # cutter edge lies in a haunch station plane (the plate top is straight between them, so the cutter
                # top stays on the plate top to well under 1 nm)
                inner = (v[:, 0] > pxs[0] + 1e-6) & (v[:, 0] < pxs[-1] - 1e-6)
                v[inner, 0] += 5e-5
                v[inner & ~low, 2] = np.interp(v[inner & ~low, 0], pxs, ptop)
                cut_plates.append(manifold(v, top_plate.faces))
            else:
                seats.append(plate)                                   # Type I / II plates cover the flange width

        def on_plate(x):
            for plo, phi, pxs, ptop in plate_tops:
                if plo - 1e-9 <= x <= phi + 1e-9:
                    return float(np.interp(x, pxs, ptop))
            return None
        for i in (1, 2):
            haunch, info, note, level = make_haunch(i, j, seats)
            hv = np.asarray(haunch.vertices)
            lo_x, hi_x = hv[:, 0].min(), hv[:, 0].max()
            cutters = [c for c, (plo, phi, _, _) in zip(cut_plates, [p for k, p in enumerate(plate_tops)
                                                                      if k == 1 and stub_line(j)])
                       if plo < hi_x and phi > lo_x]
            heads = 0
            for q in (1, 2, 3):
                bv, bf_ = native(f'beam_{j + 1}_splice_{q}_bolts')
                for body in trimesh.Trimesh(bv, bf_, process=False).split(only_watertight=False):
                    lo, hi = body.bounds
                    xc = float(body.centroid[0])
                    top_here = on_plate(xc)
                    if not (lo_x < xc < hi_x) or body.extents[2] > .0125 or top_here is None \
                            or abs(lo[2] - top_here) > 5e-5:
                        continue                                      # only the heads standing on a top plate
                    v = np.asarray(body.vertices).copy()
                    v[v[:, 2] < lo[2] + 1e-7, 2] -= .003              # run the cutter 3 mm into the plate
                    cutters.append(manifold(v, body.faces))
                    heads += 1
            out_m = (manifold(hv, haunch.faces) - mf.Manifold.batch_boolean(cutters, mf.OpType.Add)).to_mesh64()
            cut = trimesh.Trimesh(np.asarray(out_m.vert_properties)[:, :3], np.asarray(out_m.tri_verts), process=False)
            if not (cut.is_watertight and cut.is_winding_consistent and cut.volume > 0 and welded_closed(cut)):
                raise ValueError(f'haunch_{i}_{j}: cut haunch is not a closed solid after welding')
            cutters = [None] * heads
            pockets[f'haunch_{i}_{j}'] = len(cutters)
            info.update(fastener_head_pockets=len(cutters))
            store_haunch(i, j, cut, info, note)

    # deck slab: trim out the steel that reaches above its soffit (cast-in fastener heads, plate edges at lines 2/8)
    deck_cutters = []
    for j in range(9):
        for q in (1, 2, 3):
            for sid in (f'beam_{j + 1}_splice_{q}', f'beam_{j + 1}_splice_{q}_bolts'):
                sv, sf = native(sid)
                for body in trimesh.Trimesh(sv, sf, process=False).split(only_watertight=False):
                    bv = np.asarray(body.vertices)
                    if np.any(bv[:, 2] > soffit(bv[:, 0], bv[:, 1]) + 1e-7):
                        deck_cutters.append(manifold(body.vertices, body.faces))
    deck_trim = 0.0
    if deck_cutters:
        dv, df = native('deck')
        before_volume = trimesh.Trimesh(dv, df, process=False).volume
        out_m = (manifold(dv, df) - mf.Manifold.batch_boolean(deck_cutters, mf.OpType.Add)).to_mesh64()
        cut = trimesh.Trimesh(np.asarray(out_m.vert_properties)[:, :3], np.asarray(out_m.tri_verts), process=False)
        if not (cut.is_watertight and cut.is_winding_consistent and cut.volume > 0 and welded_closed(cut)):
            raise ValueError('deck: trimmed slab is not a closed solid')
        deck_trim = round(float(before_volume - cut.volume), 9)
        store_mesh('deck', cut, pages=[11, 34, 37],
                   note=f'Review correction 3: {len(deck_cutters)} splice steel bodies that reach above the slab soffit are '
                        'trimmed out (rivet and bolt heads on the top flange plates, cast into the deck concrete, and the '
                        'edges of the 15/16 in Pier 3 plates at drawing lines 2/8, which meet the soffit), '
                        f'{deck_trim * 1e6:.0f} cm3 in all.',
                   dims=dict(trimmed_steel_volume_m3=deck_trim))

    # ---------------------------------------------------------------- 5. diaphragms
    span_rows = {q: 'A/D' for q in (0, 1, 2, 8, 9, 10)}
    span_rows.update({q: 'B/C' for q in BC_ROWS})
    sections, moved = {}, {}
    for q in range(11):
        u = rows[q]
        bot = np.array([beam_at(j, u)[0] for j in range(9)])
        top = np.array([beam_at(j, u)[1] for j in range(9)])
        mid = (bot + top) / 2
        seg = int(np.clip(np.searchsorted(BS, u, side='right') - 1, 0, 3))
        web = np.array([section(seg, k, u)['tw'] / 2 for k in range(9)])
        for j in range(8):
            pid = f'diaphragm_{q}_{j}'
            p = parts[pid]
            kind, h = p['dimensions']['section'], p['dimensions']['depth_m']
            v, _ = native(pid)
            z_old = v[:, 2].min()
            expect(np.isclose(v[:, 2].max() - z_old, h, atol=TOL), f'{pid} depth')
            expect(kind == ('C380x74' if q in BC_ROWS and j == C380_BAY else 'W460x68' if q in BC_ROWS and j not in (0, 7)
                            else 'MC460x63.5'), f'{pid} section')
            if j in (0, 7):
                z0 = bot[0 if j == 0 else 8] + EXT_BOTTOM
            else:
                z0 = (mid[j] + mid[j + 1]) / 2 - h / 2
            z1 = z0 + h
            if not (z0 > max(bot[j], bot[j + 1]) + .05 and z1 < min(top[j], top[j + 1]) - .05):
                raise ValueError(f'{pid}: diaphragm not inside the beam depth')
            gap, dx = {'MC460x63.5': (MC_GAP, 0.0), 'W460x68': (0.0, 0.0),
                       'C380x74': (C380_GAP, W460['tw'] / 2 + CH_B / 2)}[kind]
            ya, yb = YS[j] + web[j] + gap, YS[j + 1] - web[j + 1] - gap
            pr = iform(W460['d'], W460['bf'], W460['tw'], W460['tf']) if kind == 'W460x68' else channel(h)
            mesh = sweep(pr, [ya, yb], lambda s, a, b, z0=z0, u=u, dx=dx: (u + dx + a, s, z0 + b))
            moved[pid] = z0 - z_old
            a_top = (top[j] + top[j + 1]) / 2 - z1
            a_bottom = z0 - (bot[j] + bot[j + 1]) / 2
            sections[pid] = kind
            dims = dict(end_gap_to_web_m=gap, length_m=round(float(yb - ya), 4))
            if j not in (0, 7):
                dims.update(clear_top_m=round(float(a_top), 4), clear_bottom_m=round(float(a_bottom), 4))
            if kind == 'MC460x63.5':
                text = ('Ends 25 mm off the beam web faces ("25 (Typ.)", sheet 15 interior diaphragm details; the '
                        'connection angles are not modelled).')
            elif kind == 'W460x68':
                text = ('Retained 1964 diaphragm, web to web (sheet 15 removal plan; 1964 S10 Section A-A); end '
                        'connections not modelled.')
            else:
                text = ('Laps 130 mm over the 200 mm stubs of the removed W460x68 left on both beam webs (sheet 15 removal '
                        'detail and Detail "B": bolt line 65 mm from the stub end), so it ends 70 mm off the web faces; '
                        'channel back against the stub web on its +X side (Detail "B" / Section C-C give no '
                        'orientation; known deviation c380-stub-side). Stubs diaphragm_{q}_2_stub_2 and _3.'.format(q=q))
            mesh_note = (f'Moved {(z0 - z_old) * 1000:+.1f} mm with the beams refitted to the drawing support elevations '
                         f'and catalog depths (same placement rule). {text} Review correction 3: ended 160 mm from the beam '
                         'centre lines.')
            store_mesh(pid, mesh, dims=dims, pages=[12, 29, 31, 35, 36], note=mesh_note)
            if kind == 'C380x74':
                for k, sgn in ((j, 1), (j + 1, -1)):
                    y0, y1 = sorted([YS[k] + sgn * web[k], YS[k] + sgn * (web[k] + STUB_L)])
                    zs = (mid[j] + mid[j + 1]) / 2 - W460['d'] / 2
                    stub = sweep(iform(W460['d'], W460['bf'], W460['tw'], W460['tf']), [y0, y1],
                                 lambda s, a, b, zs=zs, u=u: (u + a, s, zs + b))
                    add_part(f'diaphragm_{q}_{j}_stub_{k}', stub, like=pid,
                             after=pid if k == j else f'diaphragm_{q}_{j}_stub_{j}',
                             name=f'Diaphragm row {q + 1} | retained W460x68 stub at beam line {9 - k}',
                             layer='diaphragms', pages=[12, 33, 35],
                             basis='Sheet 15 removal detail ("200 (Typ.)" to the removal line) and Detail "B"',
                             note='200 mm end of the removed W460x68 diaphragm left on the beam web "to prevent damage to '
                                  'the exist. beam webs during removal" (sheet 15), centred like the original diaphragm '
                                  '(1964 S10); the C380x74 replacement is bolted to it (4 field-drilled holes, 3 @ 75). '
                                  'Review correction 3: added.',
                             dims=dict(section='W460x68', depth_m=W460['d'], length_m=STUB_L))
                    sections[f'diaphragm_{q}_{j}_stub_{k}'] = 'W460x68 stub'

    # ---------------------------------------------------------------- 1. Pier 2/4 caps, bearings and shims
    for bi, u in ((2, P2), (4, P4)):
        pid = f'pier_{bi}_widening'
        prof = [(-PIER24_HALF, PIER24_BASE), (-STEM24_HALF, PIER24_BASE), (-STEM24_HALF, PIER24_MID),
                (STEM24_HALF, PIER24_MID), (STEM24_HALF, PIER24_BASE), (PIER24_HALF, PIER24_BASE),
                (PIER24_HALF, CAP24_OUTER), (CENTRAL_HALF, CAP24_OUTER), (CENTRAL_HALF, CAP24_CENTRAL),
                (-CENTRAL_HALF, CAP24_CENTRAL), (-CENTRAL_HALF, CAP24_OUTER), (-PIER24_HALF, CAP24_OUTER)]
        store_mesh(pid, sweep(prof, [-.305, .305], lambda x, y, z, u=u: (u + x, y, z)), replace_note=True, pages=[31],
                   note='15.242 m cap extent and 610 mm wall (sheet 11). Top El. 215.972, raised to El. 216.016 over the '
                        'central 5334 mm (beam lines 4-6); the Type I bearings stand on it. New side concrete closes '
                        'against the retained 5.115 m stem; construction seams and keyways simplified. Review correction '
                        '3: the top was flat at El. 215.925 with derived seat risers.',
                   dims=dict(top_elevation_m=215.972, central_top_elevation_m=216.016, central_width_m=5.334))
        for j in range(9):
            y, c = YS[j], cap24(YS[j])
            px, py, ph = ELASTOMER
            lx, ly, lh = LOAD_PLATE
            bearing = concat([box(u - px / 2, u + px / 2, y - py / 2, y + py / 2, c, c + ph),
                              box(u - lx / 2, u + lx / 2, y - ly / 2, y + ly / 2, c + ph, c + ph + lh)])
            store_mesh(f'B{bi}_bearing_{j + 1}', bearing, replace_note=True, pages=[31, 34, 36],
                       basis='Dimensioned Type I elastomeric expansion bearing, sheet 14',
                       note=f'Type I elastomeric expansion bearing (sheet 14): 250 x 350 x 67 mm elastomer under PL '
                            f'58x280x405, 125 mm, on the cap at El. {c + 210:.3f} (sheet 11); shim plate B{bi}_seat_{j} '
                            'above. Internal laminations, anchor bolts and side retainers omitted. Review correction 3: '
                            'stood on derived seat risers above a cap at El. 215.925.',
                       dims=dict(seat_elevation_m=round(c + 210, 3), bearing_height_m=BEARING24))
        for j in range(9):
            y, c = YS[j], cap24(YS[j])
            bf = (W840 if j in (0, 8) else W201)['bf']
            west, east = (0, 1) if bi == 2 else (2, 3)

            def shim_point(s, a, b, c=c, j=j, west=west, east=east, u=u):
                return s, a, (c + BEARING24 if b == 0 else bottom(west if s <= u else east, j, s))
            # level on the bearing plate; the top follows the beam underside, which falls 0.24 % toward the bent
            shim = sweep([(y - bf / 2, 0), (y + bf / 2, 0), (y + bf / 2, 1), (y - bf / 2, 1)],
                         [u - LOAD_PLATE[0] / 2, u, u + LOAD_PLATE[0] / 2], shim_point)
            expect(abs(bottom(west, j, u) - (c + BEARING24 + SHIM24[j])) < 1e-9, f'B{bi}_seat_{j} stack')
            pid = f'B{bi}_seat_{j}'
            name = f'Pier {bi} | shim plate, beam line {9 - j}'
            basis = ('Sheet 16 shim table (Pier {}); plan size not dimensioned, taken as the 280 mm bearing plate length '
                     '(Section @ Pier 2 or 4) by the bottom-flange width (Section A-A), sheet 14').format(bi)
            note = (f'{SHIM24[j] * 1000:.0f} mm shim (at the bearing centre line) between the PL 58x280x405 of the Type I '
                    'bearing and the bottom flange (sheets 14 and 16); its top follows the beam underside, which falls '
                    'about 0.3 mm over the 140 mm half toward the bent. Review correction 3: ')
            dims = dict(thickness_m=float(SHIM24[j]), plan_x_m=LOAD_PLATE[0], plan_y_m=bf)
            if pid in parts:
                store_mesh(pid, shim, replace_note=True, name=name, basis=basis, pages=[31, 34, 36],
                           note=note + 'replaces the derived seat riser of the original model.', dims=dims)
            else:
                add_part(pid, shim, like=f'B{bi}_seat_0', after=f'B{bi}_seat_{j - 1}', name=name, layer='bearings',
                         pages=[31, 34, 36], basis=basis, dims=dims,
                         note=note + 'added; the original model had no riser at this line.')

    # ---------------------------------------------------------------- 9. pavement ledge and approach seats (sheet 9)
    for bi, u, end in ((1, B1, -1), (5, B5, 1)):
        pid = f'end_bent_{bi}'
        note = parts[pid]['note']
        cut = note.find('the outer 150 mm beyond the deck end is the pavement ledge')
        expect(cut > 0, f'{pid} note')
        note = (note[:cut] + 'the outer 150 mm beyond the deck end is the retained pavement ledge, level at El. 216.850 '
                '(sheet 9 elevation, "Pvm\'t Ledge El. 216.850"; 150 mm in section A-A), on which the 2026 approach slab '
                'end bears (2026 sheet 13 Section B-B). Review correction 3: the ledge followed the crowned 12 in approach '
                'soffit (up to El. 217.003).')
        store_mesh(pid, end_bent_mesh(u, end, LEDGE), replace_note=True, pages=[29, 61], note=note,
                   dims=dict(ledge_elevation_m=216.85))
        old = native(f'approach_{end}')[0]
        mesh = approach_mesh(end, LEDGE)
        store_mesh(f'approach_{end}', mesh, pages=[29, 61],
                   note='Review correction 3: over the 134 mm seat on the retained bent ledge (El. 216.850, sheet 9) the '
                        'slab end is thickened down to the ledge (2026 sheet 13 Section B-B shows the end bearing on it), '
                        'with a vertical step at the bent back face; the length and taper of the thickened end are on '
                        'standard drawings E609-RCBA-01 to -04, not in the set (known deviation approach-ledge-detail).',
                   dims=dict(end_seat_length_m=round(abs((BS[4] + .4) - (LENGTH / 2 + .015)), 4),
                             end_thickness_at_crown_m=round(float(surface(end * (LENGTH / 2 + .015), 0) - LEDGE), 4)))

    # ---------------------------------------------------------------- 10. display names in the drawing numbering
    def set_name(pid, name):
        p = parts[pid]
        if p['name'] != name:
            if pid not in added:
                renamed.setdefault(pid, dict(before=p['name']))['after'] = name
            p['name'] = name
            meshes[pid]['extras']['name'] = name
    for j in range(9):
        n = 9 - j
        for i in range(4):
            label = parts[f'beam_{i}_{j}']['name'].split('|')[-1].strip()
            set_name(f'beam_{i}_{j}', f'Span {SPAN[i]} | beam line {n} | {label}')
            set_name(f'haunch_{i}_{j}', f'Span {SPAN[i]} | haunch, beam line {n}')
        kind = 'Type I' if j in (0, 8) else 'Type II'
        for q, text in ((1, f'{kind} field splice, span B 900 mm from Pier 2'),
                        (2, 'field splice at Pier 3 (' + ('Type I' if j in (0, 8) else 'retained 1964') + ')'),
                        (3, f'{kind} field splice, span C 900 mm from Pier 4')):
            set_name(f'beam_{j + 1}_splice_{q}', f'Beam line {n} | {text}')
            set_name(f'beam_{j + 1}_splice_{q}_bolts', f'Beam line {n} | {text} | fasteners')
        for bi, text in ((2, 'Type I elastomeric bearing'), (3, 'fixed shoe'), (4, 'Type I elastomeric bearing')):
            set_name(f'B{bi}_bearing_{j + 1}', f'Pier {bi} | {text}, beam line {n}')
            set_name(f'B{bi}_seat_{j}', f'Pier {bi} | shim plate, beam line {n}')
    for q in range(11):
        for j in range(8):
            set_name(f'diaphragm_{q}_{j}', f'Diaphragm row {q + 1} | bay between beam lines {8 - j} and {9 - j}')

    # ---------------------------------------------------------------- write
    gltf['buffers'][0]['byteLength'] = len(binary)
    while len(binary) % 4:
        binary.append(0)
    gltf['buffers'][0]['byteLength'] = len(binary)
    encoded = json.dumps(gltf, ensure_ascii=True, separators=(',', ':')).encode()
    encoded += b' ' * ((-len(encoded)) % 4)
    out = (struct.pack('<III', 0x46546c67, 2, 28 + len(encoded) + len(binary)) +
           struct.pack('<II', len(encoded), 0x4e4f534a) + encoded +
           struct.pack('<II', len(binary), 0x004e4942) + binary)
    backup = Path(backup_dir) if backup_dir else ROOT / 'data/fem_research'
    backup.mkdir(exist_ok=True)
    (backup / f'{BID}_before_review_correction_3.glb').write_bytes(original)
    (backup / f'{BID}_manifest_before_review_correction_3.json').write_bytes(raw_manifest)
    path.write_bytes(out)

    for item in manifest.get('detail_coverage', []):
        if item.get('feature') == 'Steel connections and support topology':
            for pid in added:
                item['part_ids'].insert(item['part_ids'].index(added_after[pid]) + 1, pid)
            item['detail'] = ('Diaphragm rows per sheets 13/15: MC460x63.5 in spans A/D and the exterior bays, retained '
                              'W460x68 and one C380x74 bay in spans B/C lapping the retained W460x68 stubs; connection '
                              'angles omitted. Field splices per sheet 14 (Type I / Type II plates, bars, fillers, web and '
                              'flange bolts) and the retained 1964 Pier 3 splices (plates, bars, web and flange rivets). '
                              'Haunches per the sheet 17 typical detail. 27 pier '
                              'bearings: Pier 3 fixed shoes and Pier 2/4 Type I elastomeric bearings with the sheet 16 '
                              'shims. Beams fitted to the drawing support elevations with catalog depths. Both end bents '
                              'are integral, with no invented end bearings.')
        elif item.get('feature') == 'Retained and widened piers':
            item['detail'] = ('Piers 2/4 reconstructed side-wall stems with the sheet 11 cap top (El. 215.972 / 216.016); '
                              'Pier 3 retained hammerhead (El. 215.835 / 215.879), added outer columns, low collision '
                              'walls and widened footings per sheet 12. Pier 2/4 footing offsets remain approximate.')
    manifest['review_correction_3'] = TAG
    manifest['revision'] = REVISION
    hm = {f'haunch_{i}_{j}': round(hmin[(i, j)] * 1000, 1) for i in range(4) for j in range(9)}
    # sheet 17 beam haunch table against the model haunch (soffit to top flange at the beam centre line)
    haunch_cmp = {}
    for j in range(9):
        model = {}
        for name, i, x in (('bents', 0, B1), ('piers_2_4', 0, P2), ('pier_3', 1, P3)):
            model[name] = round(float((soffit(x, YS[j]) - env(i, j, x)['top_under']) * 1000), 1)
        haunch_cmp[f'model_index_{j}'] = dict(drawing_line=9 - j, sheet_17_dimension_a_mm=round(HAUNCH_TABLE[j] * 1000),
                                              model_mm=model)
    diffs = [haunch_cmp[f'model_index_{j}']['model_mm'][k] - HAUNCH_TABLE[j] * 1000 for j in range(9)
             for k in ('piers_2_4', 'pier_3')]
    bent_diffs = {9 - j: round(HAUNCH_TABLE[j] * 1000 - haunch_cmp[f'model_index_{j}']['model_mm']['bents'], 1)
                  for j in range(9)}
    bolts_top = {}
    for pid in [f'beam_{j + 1}_splice_{q}_bolts' for j in range(9) for q in (1, 2, 3)]:
        bv = current[pid][0]
        bolts_top[pid] = round(float((soffit(bv[:, 0], bv[:, 1]) - bv[:, 2]).min()) * 1000, 1)
    counts = {}
    for k in sections.values():
        counts[k] = counts.get(k, 0) + 1
    manifest['review_correction_record_3'] = dict(
        source='Known deviations of revision 1.2 resolved against the drawings (2026-11), with the items of the '
               'independent check of this round verified against the sheets',
        source_pdf_pages=[10, 11, 12, 29, 30, 31, 33, 34, 35, 36, 37, 61],
        printed_sheets_1964=['S8', 'S9', 'S10'], printed_sheets_1998=[9, 10, 11, 13, 14, 15, 16, 17],
        printed_sheets_2026=[13],
        resolved_deviations=['pier-2-4-seat-stack', 'pier-3-beam-taper', 'pier-3-top-splice-plate-embedment',
                             'pier-2-4-splice-plates'],
        kept_deviations=['beam-line-numbering (ids only; names now follow the drawing)',
                         'approach-ledge-detail (ledge fixed; thickened approach end beyond the seat remains)'],
        new_deviations=['haunch-table-vs-support-stacks', 'pier-3-retained-splice-flange-fasteners', 'c380-stub-side'],
        corrections={
            'pier_2_4_caps': 'flat top El. 215.925 -> El. 215.972, central 5334 mm at El. 216.016 (sheet 11)',
            'pier_2_4_bearings': 'Type I 125 mm bearings on the cap (sheet 14), were on derived risers',
            'pier_2_4_shims': '38/13/32/13/26/13/32/13/38 mm (sheet 16); 14 risers became shims, 4 shims added',
            'beam_support_elevations': 'beam bottoms at the Bents = pile cutoff + 19 mm plate (sheets 9-10), at Piers '
                                       '2/4 = cap + 125 mm + shim, at Pier 3 unchanged; linear between supports',
            'beam_depths': 'W920x201 920 -> 903 mm, W920x223 920 -> 911 mm (W840x193 840 mm unchanged); W920x201 stub '
                           '900 mm into spans B/C centred on the W920x223 at the Type II splice',
            'end_beams': 'span A/D beams and haunches extended 150 mm beyond the bent centre lines (sheet 10 Detail A)',
            'pier_2_4_splices': 'generic 13 mm x 1.13 m envelopes -> sheet 14 Type I (lines 1/9) / Type II (lines 2-8) '
                                'plates, inner bars, fillers, 6 x 7 web bolts and the flange bolts',
            'pier_3_type_i_splices': 'inner bars 13x102x1130, the sheet 14 web bolt grid and the flange bolts added '
                                     '(lines 1/9)',
            'pier_3_retained_splices': 'flange plates follow the refitted beams; web plates 2 PL 31 x 1/2 in (787.4 x '
                                       '12.7 mm, were 770 x 13) and the 6 x 10 web rivet grid of 1964 S9 (60, were 35); '
                                       'inner bars PL 4 1/2 x 3/8 x 33 in (interior) / 4 1/2 x 5/8 x 45 in (exterior '
                                       'beams, drawing lines 2/8) and the flange rivets, 72 top and 68 bottom (the 4 under '
                                       'the top shoe omitted)',
            'beam_flanges': 'flange thickness to the catalog of the drawn sections with the outer faces kept: W840x193 '
                            '25.4 -> 21.7 mm, W920x201 23.0 -> 20.1 mm, W920x223 27.0 -> 23.9 mm; splice bars and '
                            'fastener grips follow',
            'deck': 'splice steel reaching above the slab soffit (top fastener heads cast into the deck, plate edges at '
                    'lines 2/8) trimmed out of the slab',
            'haunches': 'sheet 17 typical haunch: 100 mm shoulders beyond each flange edge down to the flange underside, '
                        'top on the deck soffit with the crown ridge on line 5 (was 3.05 mm below it), spans A/D '
                        'haunches start at the bent span face, over the splices seated on the top plates with pockets for the '
                        'fastener heads (nominal 75 mm '
                        'dropped)',
            'pier_3_top_plates': 'the retained 15/16 in top plates at lines 2/8 (model indices 1, 7) now meet the slab '
                                 'soffit (their edges reach 0.3 mm above it, below the 1 mm resolution of the plan '
                                 'elevations, and are trimmed out of the slab; was 9.3 mm into it); all other top plates '
                                 'clear it',
            'diaphragms': 'all 88 re-placed by the round-2 rules on the refitted beams; ends per sheet 15: MC460 25 mm '
                          'off the web faces, retained W460x68 web to web, C380x74 70 mm off the web faces lapping 130 mm '
                          'over 10 added W460x68 stubs (200 mm); were 160 mm short of the beam centre lines',
            'pavement_ledge': 'end-bent ledge level at El. 216.850 (sheet 9), was on the crowned approach soffit (up to '
                              'El. 217.003); approach slab end lowered onto it over the 134 mm seat',
            'display_names': 'beam-line parts named in the drawing numbering (drawing line = 9 - model index); ids '
                             'unchanged'},
        decisions=[
            dict(item='girder profile between supports', decision='follow the written support elevations (caps, '
                 'bearings, shims, pile cutoffs) with the lift linear between supports (constant over the Pier 3 splice) '
                 'on the grade-parallel nominal profile',
                 reasoning='No screed or top-of-steel elevations are given. The support stacks are written on sheets '
                           '9-12, 14 and 16 and agree with the sheet 16 blocking chords (A 38 / B 63 / C 38 mm equal the '
                           'lines 1/9 stacks). The sheet 17 haunch table, read as drawn (Dimension "A" from the slab '
                           f'soffit to the underside of the top flange), agrees with them at all three piers on every line '
                           f'({min(diffs):+.1f} to {max(diffs):+.1f} mm) and confirms a constant haunch along spans B/C; '
                           'at the bents the written pile cutoffs govern (known deviation haunch-table-vs-support-stacks).'),
            dict(item='beam flange thickness', decision='ASTM A6/A6M flange thickness of the drawn designations: W840x193 '
                 '21.7 mm, W920x201 20.1 mm, W920x223 23.9 mm, outer faces kept',
                 reasoning='Same source as the depths; with them the sheet 17 Dimension "A" (to the flange underside) '
                           'agrees with the pier stacks to about 2 mm. Flange widths and webs stay nominal (within 1 mm).'),
            dict(item='beam depths', decision='ASTM A6/A6M depths of the drawn designations: W920x201 903 mm, W920x223 '
                 '911 mm',
                 reasoning='Sheet 14 Type II fillers PL 4x305x485 fill (911 - 903) / 2 on the W920x201 side; with 903 mm '
                           'the bent pile cutoffs give a uniform 31-33 mm haunch on lines 2-8 (30 mm on the W840 lines), '
                           'with the nominal 920 mm about 15 mm.'),
            dict(item='Pier 2/4 shim plan size', decision='280 mm x bottom-flange width',
                 reasoning='Not dimensioned; drawn flush with the 280 mm bearing plate along the beam and with the '
                           'flange across it (sheet 14 sections).'),
            dict(item='1964 web rivet columns', decision='4 1/8 in centre gap (columns at 2 1/16, 5 1/16, 8 1/16 in)',
                 reasoning='1964 S9 interior and exterior details read "2@3=6 | 4 1/8 | 2@3=6" above the web plate; the '
                           'drawn gap scales about 3.9 in, nearer 4 1/8 than 4 1/2 in.'),
            dict(item='C380x74 stub geometry', decision='stubs 200 mm from the web face, C380 lapping 130 mm, i.e. '
                 'ending 70 mm off the web face',
                 reasoning='Sheet 15 removal detail dimensions 200 (Typ.) from the web to the removal line; Detail "B" '
                           'dimensions 130 from the stub end to the channel end and 65 from the stub end to the bolt '
                           'line (centred in the lap).'),
            dict(item='C380x74 side of the stub web', decision='+X side',
                 reasoning='Detail "B" and Section C-C carry no orientation (recorded as known deviation c380-stub-side).'),
            dict(item='approach slab end', decision='soffit lowered to the ledge over the 134 mm seat only, vertical step '
                 'at the bent back face',
                 reasoning='The ledge elevation is fixed (sheet 9) and the slab end bears on it (2026 Section B-B, not to '
                           'scale); the thickened end beyond the seat is on E609-RCBA-01 to -04, not in the set.')],
        support_bottom_elevations_m={
            'bents_1_5': {f'model_index_{j}': round(float(BENT_BOTTOM[j] + 210), 3) for j in range(9)},
            'piers_2_4': {f'model_index_{j}': round(float(P24_BOTTOM[j] + 210), 3) for j in range(9)},
            'pier_3': {f'model_index_{j}': round(float(P3_BOTTOM[j] + 210), 4) for j in range(9)}},
        beam_lift_above_nominal_m={
            'bents_1_5': {f'model_index_{j}': round(float(D_BENT[j]), 5) for j in range(9)},
            'piers_2_4': {f'model_index_{j}': round(float(D_P24[j]), 5) for j in range(9)},
            'pier_3': {f'model_index_{j}': round(float(D_P3[j]), 5) for j in range(9)}},
        haunch_table_comparison=haunch_cmp,
        haunch_fastener_head_pockets=pockets,
        deck_trimmed_steel_volume_m3=deck_trim,
        minimum_haunch_mm=hm,
        splice_top_plate_clearance_below_soffit_mm={k: round(v * 1000, 1) for k, v in sorted(clear_top.items())},
        splice_fastener_clearance_below_soffit_mm=bolts_top,
        diaphragm_vertical_moves_mm={k: round(v * 1000, 1) for k, v in moved.items()},
        diaphragm_sections=counts,
        name_mapping='model index j (ids beam_i_j, haunch_i_j, B*_seat_j, beam_{j+1}_splice_q, B*_bearing_{j+1}) = '
                     'drawing beam line 9 - j; diaphragm bay j = between drawing lines 8 - j and 9 - j',
        changed_parts=changed, added_parts=added, removed_parts=[], renamed_parts=renamed,
        before_glb_sha256=before, after_glb_sha256=hashlib.sha256(out).hexdigest())
    keep = {d['id']: d for d in manifest.get('known_deviations', [])}
    deviations = [d for d in manifest.get('known_deviations', [])
                  if d.get('id') not in ('pier-2-4-seat-stack', 'pier-3-beam-taper', 'pier-3-top-splice-plate-embedment',
                                         'pier-2-4-splice-plates', 'beam-line-numbering', 'approach-ledge-detail')]
    numbering = dict(keep['beam-line-numbering'])
    numbering['parts'] = ('ids of beam_*_*, haunch_*_*, beam_N_splice_*, B2/B3/B4_bearing_N, B2/B3/B4_seat_*, '
                          'diaphragm_q_j and diaphragm_q_2_stub_k')
    numbering['deviation'] = ('Drawing Beam Line No. 1 is the north edge (native +Y = 7.113 m). The display names follow '
                              'the drawing numbering since revision 1.3, but the ids keep the model index from the south '
                              'edge: model index j (beam_i_j, haunch_i_j, B*_seat_j, beam_{j+1}_splice_q, '
                              'B*_bearing_{j+1}, stub _k) is drawing beam line 9 - j, and diaphragm bay j lies between '
                              'drawing lines 8 - j and 9 - j. The geometry follows the drawing.')
    numbering['reason'] = ('Not a drawing question: sheet 13 settles the mapping. The ids are stable keys shared with the '
                           'viewer, the FEM collection and inspection data, so renaming them is a data-migration decision '
                           'for the data owner, not a geometry correction.')
    ledge = dict(keep['approach-ledge-detail'])
    ledge['deviation'] = ('The retained ledge is level at El. 216.850 (sheet 9) and the 12 in approach slab end is '
                          'lowered onto it over the 134 mm seat only, with a vertical step at the bent back face; at the '
                          'crown the slab end is 0.458 m deep over the seat and 0.305 m beyond it. 2026 Section B-B shows '
                          'a thickened end continuing beyond the ledge with a sloped transition.')
    ledge['reason'] = ('2026 sheet 13 (PDF 61) refers the section through the approach slab end to standard drawings '
                       'E609-RCBA-01 to -04, which are not in the set; its Section B-B is not to scale and has no '
                       'dimensions. The length and taper of the thickened end are settled only by those standard '
                       'drawings (the edition cited by R-43918) or an as-built survey of the bent ends.')
    table = dict(id='haunch-table-vs-support-stacks', parts='beam_0_*, beam_3_*, haunch_0_*, haunch_3_*',
                 source='1998 sheet 17 beam haunch table (PDF 37); sheets 9-10 (PDF 29-30)',
                 deviation='The sheet 17 table gives one Dimension "A" per beam line (soffit to the underside of the top '
                           'flange, 50/50/62/73/95 mm for drawing lines 1-5, symmetric) and no stations. The model agrees '
                           f'with it at Piers 2, 3 and 4 ({min(diffs):+.1f} to {max(diffs):+.1f} mm). At the bents the '
                           'written pile cutoffs + 19 mm plate give about 50-53 mm on every line, so the span A/D haunches '
                           'of drawing lines 3-7 taper from the table value at the piers to that at the bents (table minus '
                           'model at the bents: ' + ', '.join(f'line {n} {d:+.0f} mm' for n, d in sorted(bent_diffs.items())
                                                              if n <= 5) + ').',
                 reason='The table carries no stations and conflicts with the written pile cutoff elevations at the bents '
                        '(sheet 9), which agree with the blocking diagram; the model follows the elevations. Settled by a '
                        'haunch or screed table by station, or a top-of-steel survey at the end bents.')
    rivets = dict(id='pier-3-retained-splice-flange-fasteners', parts='beam_2..beam_8_splice_2_bolts',
                  source='1964 S9 (PDF 11); sheet 14 (PDF 34)',
                  deviation='The 4 bottom-flange rivets 3 in off the centre line of each retained Pier 3 splice (28 in '
                            'all) are omitted: they lie inside the 230 x 310 mm top shoe and shim footprint. All other '
                            'web and flange rivets and the inner bars are modelled.',
                  reason='S9 does not show how those rivet heads are treated under the shoe (countersunk, or cleared by '
                         'the shim), next to the separate 1 in holes for the 1964 shoe studs, and the 1998 shoe (sheet 14) '
                         'does not say either. Settled by the 1964 shop drawings or a field inspection of the Pier 3 '
                         'bearings.')
    side = dict(id='c380-stub-side', parts='diaphragm_3_2 .. diaphragm_7_2',
                source='1998 sheet 15 Detail "B" and Section C-C (PDF 35)',
                deviation='The C380x74 replacement diaphragms are placed on the +X (east) side of the W460x68 stub webs, '
                          'back to back with them.',
                reason='Detail "B" and Section C-C show the channel on one side of the stub web but carry no north arrow '
                       'or station direction. Settled by the 1998 shop drawings or a field inspection.')
    manifest['known_deviations'] = deviations + [numbering, ledge, table, rivets, side]
    text = json.dumps(manifest, indent=2) + ('\n' if raw_manifest.endswith(b'\n') else '')
    mp.write_text(text, encoding='utf-8')
    rec = manifest['review_correction_record_3']
    print(json.dumps({k: rec[k] for k in ('support_bottom_elevations_m', 'beam_lift_above_nominal_m',
                                          'splice_top_plate_clearance_below_soffit_mm', 'added_parts',
                                          'before_glb_sha256', 'after_glb_sha256')}, indent=1))
    print('minimum haunch mm', min(hm.values()), 'renamed', len(renamed))
    print(len(changed), 'parts changed,', len(added), 'added, 0 removed')


if __name__ == '__main__':
    args = dict(zip(sys.argv[1::2], sys.argv[2::2]))
    correct(args.get('--base'), args.get('--backup'))

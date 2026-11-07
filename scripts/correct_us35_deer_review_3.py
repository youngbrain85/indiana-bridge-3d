"""Third drawing-confirmed correction of US 35 over Deer Creek (us35-deer): the two known deviations of revision 1.2
and what closing them exposed at the end bents and the obtuse corners. Runs after scripts/correct_us35_deer_review.py
and scripts/correct_us35_deer_review_2.py and keeps every GLB buffer it does not replace.

    python scripts/correct_us35_deer_review_3.py [--base DIR] [--backup DIR]

Source: drawings.pdf (INDOT B-45063 / Des 1900048, document 9721578); printed sheet numbers equal PDF page numbers.
Native axes (revision 1.2): X along increasing station (east, X = 0 at Sta. 1271+60), Y positive to the left of
increasing station (north), Z up from El. 837.11; bent and deck-end lines q = X - tan(15 deg) Y. The deck ends are at
q = -/+17.8943 m (117'-5" out-out bridge floor, sheet 11). The obtuse deck corners are north-west and south-east,
the acute ones north-east and south-west.

1. tfc-transition-section: partly RESOLVED, partly DECIDED, the remainder KEPT (narrowed).
   - Rail layout (sheet 23 elevations; sheet 11 plan, whose CAD linework is drawn at 1/8" = 1'-0" = 9 pt per ft:
     the 117'-5" dimension line is 1056.8 pt long). Each FC railing is 102'-4 3/8" (sheet 23, written) with square
     butt joints (sheet 11: butt-joint lines square to the rail). At the acute corners the butt joint is at the deck
     end, on the 17'-8" toe line, and the TFC stands on the approach slab extension; at the obtuse corners the TFC
     stands on the deck (sheet 23 north and south elevations: "Bridge Deck" under the TFC at the west end of the
     north side and the east end of the south side, "Approach Slab Extension" under the other two). Sheet 11
     measures the north FC toe from X = -38.92 to +63.44 ft and the south one from -63.44 to +38.93 ft; 63.44 ft is
     the deck end on the toe line. The model had both rails centred on the structure with skewed ends at
     q = -/+15.6004 m, so every TFC straddled the deck end. Each rail moves 2.2939 m along X (north rail east,
     south rail west) and gets square ends; section and length are unchanged.
   - TFC length, ends and plan (sheet 11 CAD; sheet 23 elevations): all four transitions are 141.0 pt = 15'-8" long
     with square ends; the rear face continues the FC rear face 2" inside the coping. The traffic-face toe recedes
     5" over the first 7'-2 1/2" (64.8-64.9 pt), 2" more over the next 4'-3" (38.2-38.3 pt), and then runs 7" behind
     the FC toe, under the FC top edge, for the last 4'-2 1/2": a vertical face, 9" wall. The 5" and 2" equal the
     runs of the FC's lower slope and upper batter (sheet 23 section A-A), so the face is taken as the FC face with
     the lower slope removed first and then the upper batter, keeping the 3" and 10" break heights.
   - Height (sheet 23 elevations): the top line runs level from the FC across both TFCs to the guardrail, so the
     TFC is 2'-9" high throughout. The model eased it to 0.70 m at the outer end.
   - Butt joint (sheet 23): the TFC starts with the FC section, so the faces now match exactly (they differed by up
     to about 0.1 m).
   - Extensions (sheet 25 plan and bill of materials; sheet 11; sheet 23): the slab extension under each acute-corner
     TFC is 15'-10" x 1'-6" ("RCBA Extension 2 x 2.6 Sys"), from the slab corner on the 17'-8" edge, with a square
     outer end (sheet 11 draws it at X = -/+79.28 ft, 2" beyond the TFC end). The model's 2.48 m skewed envelopes
     extension_-1_1 (south-west) and extension_1_-1 (north-east) are rebuilt; they keep the 1 ft RCBA thickness
     and their inner end on the deck end, against which the RCBA is cast (sheets 15, 25).
   - DECISION, TFC end at the obtuse corners: sheet 6 (roadway sheet, not to scale) puts the guardrail-transition
     ends at Sta. 1271+05.91 (north-west) and 1272+14.07 (south-east), about 0.5 ft short of a 15'-8" TFC. The
     bridge sheets govern the bridge railing: sheet 11 draws all four TFCs 15'-8", sheet 23 draws them equal and
     bills "4 Each" of one standard item, sheet 6 agrees with the 15'-8" TFC within 0.05 ft at the acute corners
     (1270+80.83, 1272+39.16), and sheet 25 starts the obtuse-corner curb 9 1/4" from the slab corner, which is the
     15'-8" TFC end (within 0.1 mm). The north-west and south-east TFCs therefore end 0.235 m (front of the vertical
     end) to 0.296 m (rear) beyond the deck end.
   - KEPT (narrowed): the face between the butt joint and the vertical end is an interpolation, the terminal
     connector recesses, anchorage, chamfers and end details are not modelled, and nothing is drawn under the
     obtuse-corner TFC ends beyond the deck end; these are in INDOT Standard Drawings E706-TTFC-01 to -03 and
     E706-CBRT-01 (sheet 23 notes 4 and 5), which are not in this plan set.
2. approach-display-joint: RESOLVED. Sheet 15 sections A-A, B-B and C-C and the sheet 25 pavement ledge detail draw
   the reinforced concrete bridge approach cast against the deck end: one interface line, the Type IA joint
   (sealed saw cut) at its top and 1/2" x 4" expanded polystyrene only over its lowest 4". There is no gap. The
   skewed near edge of each approach slab moves 25 mm from q = -/+17.9193 m onto the deck end, q = -/+17.8943 m;
   its top stays flush with the deck (sheet 25).
   - End-bent ledge (sheet 15 sections A-A to C-C: 9" from the back face of the bent to the deck end, 1'-2" to the
     bent centre line; sheet 25 pavement ledge detail): the slab bears on the bent in that 9" strip, and the bent
     top there is at the slab soffit. The model's back faces backwall_0 / backwall_1 ran from 0.39 to 0.60 m behind
     the bent centre line with their top at the deck soffit, so the slab penetrated them by 101.6 mm (0.230 m3 each
     before this correction, 0.234 m3 with the slab on the deck end). They are rebuilt over the drawn ledge strip,
     from the back face of the bent (the cap back face, q = u -/+ 0.604808 m) to the deck end, with their top at the
     slab soffit under the slab, its extension and the corner curb, and at the deck soffit (the model's rule,
     unchanged) beyond them toward the bent ends; crowned at the centre line.
   - Slab thickening (sheet 25 pavement ledge detail, CAD linework at 3/4" = 1'-0"): the RCBA is 2" deeper, 14", from
     the deck end over the 9" ledge and 1'-6" beyond it, then returns at 45 deg (2" over 2") to its 12". The slabs
     and the acute-corner extensions (sheet 23 draws the extension deeper next to the deck too) get that band across
     their full width; distances are taken normal to the deck end like the 9" ledge of sheet 15 (0.7100 and
     0.7626 m along X). The ledge tops are at the 14" soffit, 0.3556 m below the surface.
   - Closure bays (sheet 15: the integral concrete above the ledge stops at the deck end line): the end-side faces of
     the ten integral_infill_* bays were 0.38 m behind the bent centre line, 11.7 mm beyond the deck end, and now cut
     0.0071 m3 per bent out of the slab. They move to the deck end; nothing else changes.
   - Joint strips: joint_-1 / joint_1 keep their station range (centred on the deck end, 24 mm x 60 mm display
     size; the saw cut is detailed in E 609-BRJT-01, sheet 25 note 4) but now span only the drawn interface: the slab
     and its extension (west: Y = -19'-2" to +18'-3", east: -18'-3" to +19'-2"). They lie 12 mm into the deck and
     12 mm into the slab.
3. Obtuse corners (sheet 25 plans, curb detail and bill of materials; sheet 11 plan): REMOVED / ADDED. The plan set
   has slab extensions only at the two acute corners ("RCBA Extension 2 x 2.6 Sys"); at the obtuse corners it draws
   the 11 ft Integral Concrete Curb Type B (Modified). The model's 2.56 m envelopes extension_-1_-1 (north-west) and
   extension_1_1 (south-east) have no drawing counterpart and are removed. The curbs curb_-1_-1 and curb_1_1 are
   added in their glTF node and mesh slots: 8" wide outside the 18'-3" slab edge, from the slab bottom to 4" above
   its top, 7" flat top and 1" batter with a 2" radius on the traffic side (sheet 25 detail), 11'-0" long from the TFC
   end face, which is 9 1/4" beyond the slab corner as sheet 25 dimensions the curb start (within 0.02 mm),
   following the 2 % crown like the slab.

4. Beam-end copes (sheet 19 BEAM PLAN: the top flange stops 6" short of each square beam end; sheet 20 END SECTION:
   "Area to be coped at beam end" is the flange outside the 8" web, down to the web 11" below the top). The four
   beams had full square ends whose acute top-flange corners reached 27 mm beyond the deck end, into the slab and
   the ledge. The flange wings are removed over the last 6" at both ends: each beam is rebuilt as one closed
   2-manifold (full section on its original stations between the cope lines, web and bottom flange over the last 6",
   wing faces at the cope lines); the haunches, which followed the square ends, are trimmed at the deck ends
   (manifold boolean intersection).

Rebuilt (32): FC_rail_-1, FC_rail_1, TFC_transition_-1_-1, TFC_transition_1_-1, TFC_transition_-1_1,
TFC_transition_1_1, extension_-1_1, extension_1_-1, approach_-1, approach_1, backwall_0, backwall_1, joint_-1,
joint_1, beam_0_0 .. beam_0_3, haunch_0_0 .. haunch_0_3 and the ten integral_infill_* bays (positions only). Removed (2): extension_-1_-1, extension_1_1. Added (2):
curb_-1_-1, curb_1_1. New POSITION and index accessors, and COLOR_0 where the vertex count or colour changes; every
other mesh, accessor and the existing binary data are kept byte for byte. source_ledger.json: the two removed ids are
dropped from approximate_part_ids.

Requires numpy and trimesh, plus scripts/correct_us35_deer_review.py and scripts/correct_us35_deer_review_2.py.
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
import correct_us35_deer_review_2 as second  # noqa: E402

BID = first.BID
BASE = ROOT / 'data/bridges' / BID
BACKUP = ROOT / 'data/fem_research'
TAG_KEY = 'review_correction_3'
TAG = 'known-deviations-rail-layout-tfc-approach-joint-ledge-curbs'
REVISION = '1.3-deviations'
PREVIOUS_TAG, PREVIOUS_REVISION = second.TAG, second.REVISION
EXPECTED_GLB_SHA256 = '31cde8954bd0ea6daf7373fac2d009b84a861f7bd5a375af09a067286d5c8fb1'   # revision 1.2 output
FT, IN, TAN, TOL, SLAB = first.FT, first.IN, first.TAN, first.TOL, first.SLAB

HALF = first.LENGTH / 2                    # deck end, q = 17.8943 m (sheet 11, 117'-5" out-out bridge floor)
REAR = first.NEW_RAIL_EDGE                 # FC rear face 2" inside the coping, |Y| = 5.7912 (sheet 23)
TOE = REAR - 16 * IN                       # FC toe 17'-8" from the centre line, |Y| = 5.3848 (sheet 23)
COPING = first.WIDTH / 2                   # 19'-2" (sheets 11, 12, 22)
RCBA_WIDE = (18 + 3 / 12) * FT             # 18'-3" slab edge at the obtuse corners (sheets 11, 25)
RAIL_LEN = first.RAIL_LEN                  # 102'-4 3/8" out to out bridge railing (sheet 23)
OLD_RAIL_Q = RAIL_LEN / 2                  # model: rails centred, skewed ends at q = +/-15.6004
OLD_EXT_Q = first.EXT_FAR                  # model: TFC and extension outer ends at q = +/-20.3757
OLD_NEAR_Q = first.APPROACH_NEAR           # model: approach near edge at q = +/-17.9193 (25 mm display joint)
TFC_LEN = (15 + 8 / 12) * FT               # sheet 11 CAD, 141.0 pt at 9 pt/ft, all four transitions
# Toe recession (inches behind the FC toe) along the TFC from the butt joint (sheet 11 CAD linework).
TFC_PLAN = [(0.0, 0.0), ((7 + 2.5 / 12) * FT, 5.0), ((11 + 5.5 / 12) * FT, 7.0), (TFC_LEN, 7.0)]
TFC_H = 33 * IN                            # 2'-9", level top across the TFC (sheet 23 elevations)
EXT_LEN, EXT_T = (15 + 10 / 12) * FT, first.APPROACH_T     # 15'-10" (sheet 25); 1 ft RCBA thickness kept
RAIL_STATIONS = 62                         # station count of the existing FC prisms, kept
CURB_LEN, CURB_SETBACK, CURB_W, CURB_UP = 11 * FT, 9.25 * IN, 8 * IN, 4 * IN    # sheet 25 plans and curb detail
JOINT_HALF, JOINT_DEPTH = .012, .06        # existing display strip, unchanged
COS = np.cos(np.radians(15))
# Sheet 25 PAVEMENT LEDGE DETAIL: the 12 in RCBA is 2 in deeper (14 in) from the deck end over the 9 in ledge and
# 1'-6" beyond it, then returns at 45 deg (2 in over 2 in). Distances normal to the deck end, as the 9 in ledge of
# sheet 15; along X (q) they are d / cos 15. Rows: (distance from the deck end along q, slab thickness).
THICK = first.APPROACH_T + 2 * IN          # 0.3556 m over the ledge
BAND = [(0.0, THICK), ((9 + 18) * IN / COS, THICK), ((9 + 18 + 2) * IN / COS, first.APPROACH_T)]
COPE_LEN, WEB_HALF, FLANGE_DEPTH = 6 * IN, 4 * IN, 11 * IN   # sheet 19 plan 6"; sheet 20 end section (8" web, 11")
BEAM_HALF_LEN = 116.5 / 2 * FT             # sheet 19, 116'-6" beam length, square ends
OLD_BACKWALL, OLD_INFILL_BACK = first.BACKWALL, first.INFILL_BACK      # model limits (0.39-0.60, 0.38 m)
# Sheet 6 guardrail-transition ends (TFC outer end faces), Sta. -> X.
SHEET6 = {'TFC_transition_-1_-1': 127105.91, 'TFC_transition_-1_1': 127080.83,
          'TFC_transition_1_-1': 127239.16, 'TFC_transition_1_1': 127214.07}
ORIENT_NOTE = second.ORIENT_NOTE
ENVELOPES = {'extension_-1_-1': ('curb_-1_-1', -1, 1), 'extension_1_1': ('curb_1_1', 1, -1)}   # obtuse corners


def surface(x, y):
    return first.surface(x, y)


def station(x):
    s = 127160 + x / FT
    return f'{int(s // 100)}+{s % 100:05.2f}'


def q_of(v):
    return v[:, 0] - TAN * v[:, 1]


def sx(u, y):
    return u + TAN * np.asarray(y)


def fc_profile(t):
    """FC section (sheet 23 section A-A) with the traffic-face toe moved t inches back (0 <= t <= 7): the 5 in lower
    slope goes first, then the 2 in upper batter. (inches from the rear face toward traffic, inches above the deck)."""
    lower = 11 - max(0.0, t - 5)
    return [(0, 0), (16 - t, 0), (16 - t, 3), (lower, 10), (9, 33), (0, 33)]


def corner(end, side):
    """end -1 west / +1 east, side +1 north / -1 south. Returns the part-id suffix and whether the corner is acute."""
    return f'{end}_{-side}', end * side > 0


def rail_limits(side):
    """Square FC rail ends: the acute-corner butt joint is at the deck end on the toe line."""
    acute_x = side * (HALF + TAN * TOE)
    return sorted([acute_x, acute_x - side * RAIL_LEN])


def build_rail(side):
    x0, x1 = rail_limits(side)
    section = [(v * IN, z * IN) for v, z in first.FC_SECTION]
    return first.prism(np.linspace(x0, x1, RAIL_STATIONS), section,
                       lambda x, v, z: (x, side * (REAR - v), surface(x, side * (REAR - v)) + z))


def tfc_start(end, side):
    x0, x1 = rail_limits(side)
    return x1 if end > 0 else x0


def build_tfc(end, side):
    xb = tfc_start(end, side)
    stations = [d for d, _ in TFC_PLAN]
    recess = dict(TFC_PLAN)

    def point(s, k, _):
        v, z = fc_profile(recess[s])[k]
        x, y = xb + end * s, side * (REAR - v * IN)
        return x, y, surface(x, y) + z * IN

    return first.prism(stations, [(k, 0) for k in range(6)], point)


def slab_rows(end, n):
    """Station rows of a slab cast against the deck end: three rows parallel to the deck end over the thickened band
    (sheet 25), then n rows to the square far end. Each row is (kind, parameter, thickness)."""
    return [('q', d, t) for d, t in BAND] + [('t', t, first.APPROACH_T) for t in np.linspace(0, 1, n + 1)[1:]]


def slab_x(end, row, y, far):
    kind, a, _ = row
    if kind == 'q':
        return float(sx(end * (HALF + a), y))
    return (1 - a) * float(sx(end * (HALF + BAND[-1][0]), y)) + a * far


def build_extension(end, side):
    yy = sorted([side * TOE, side * COPING])
    x_far = end * (HALF + TAN * TOE + EXT_LEN)
    rows = slab_rows(end, 8)

    def point(k, y, h):
        x = slab_x(end, rows[k], y, x_far)
        return x, y, surface(x, y) - rows[k][2] * (1 - h)

    return first.prism(range(len(rows)), [(yy[0], 0), (yy[1], 0), (yy[1], 1), (yy[0], 1)], point), x_far


def build_approach(end, north, south):
    far = first.APPROACH_FAR[end]
    rows = slab_rows(end, 21)
    profile = [(north, 0), (0.0, 0), (-south, 0), (-south, 1), (0.0, 1), (north, 1)]

    def point(k, y, h):
        x = slab_x(end, rows[k], y, far)
        return x, y, surface(x, y) - rows[k][2] * (1 - h)

    return first.prism(range(len(rows)), profile, point, caps=[(0, 1, 4), (0, 4, 5), (1, 2, 3), (1, 3, 4)])


# BT 48 x 49 section as modelled (inches from the beam axis, inches below the top), counter-clockwise in (Y, Z), with
# the two web-top points of the cope (+/-4, 0) inserted on the top edge.
BEAM_SECTION = [(20, -48), (20, -42.5), (6, -35.5), (4, -33.5), (4, -11), (7, -8), (24.5, -5), (24.5, 0), (4, 0),
                (-4, 0), (-24.5, 0), (-24.5, -5), (-7, -8), (-4, -11), (-4, -33.5), (-6, -35.5), (-20, -42.5),
                (-20, -48)]
COPED = [0, 1, 2, 3, 4, 8, 9, 13, 14, 15, 16, 17]          # web and bottom flange (sheet 20 end section)
WINGS = [[4, 5, 6, 7, 8], [9, 10, 11, 12, 13]]             # removed over the 6" cope (counter-clockwise)
COPED_CAP = [(0, 1, 2), (0, 2, 3), (0, 3, 8), (0, 8, 9), (0, 9, 10), (0, 10, 11), (3, 4, 7), (3, 7, 8), (4, 5, 6),
             (4, 6, 7)]                                    # triangles of COPED, by position in that list


def cope_beam(beam):
    """Sheet 19 BEAM PLAN: the top flange stops 6" short of each square beam end; sheet 20 END SECTION: the area to
    be coped is the flange outside the 8" web, down to the web (11" below the top). The beam is rebuilt as one closed
    2-manifold: the full section between the cope lines (on the original stations), the web and bottom flange over
    the last 6", and the two wing faces at each cope line, so that every edge has exactly two faces."""
    v = beam.vertices
    yb = (v[:, 1].min() + v[:, 1].max()) / 2
    xs = np.unique(v[:, 0].round(6))
    tops = np.array([v[np.abs(v[:, 0] - x) < 1e-5, 2].max() for x in xs])
    slope, z0 = np.polyfit(xs, tops, 1)
    x0, x1 = float(v[:, 0].min()), float(v[:, 0].max())
    xa, xb = x0 + COPE_LEN, x1 - COPE_LEN
    mid = [xa] + [float(x) for x in xs if xa + 1e-6 < x < xb - 1e-6] + [xb]
    n = len(BEAM_SECTION)

    def ring(x, idx):
        return [(x, yb + BEAM_SECTION[k][0] * IN, z0 + slope * x + BEAM_SECTION[k][1] * IN) for k in idx]

    verts = [p for x in mid for p in ring(x, range(n))]
    west = len(verts)
    verts += ring(x0, COPED)
    east = len(verts)
    verts += ring(x1, COPED)
    faces = []

    def strip(a, b, ia, ib, m):          # side quads between rings a (smaller X) and b, outward for CCW sections
        for k in range(m):
            p0, p1, q0, q1 = a + ia[k], a + ia[(k + 1) % m], b + ib[k], b + ib[(k + 1) % m]
            faces.extend([(p0, p1, q1), (p0, q1, q0)])

    full = list(range(n))
    for k in range(len(mid) - 1):
        strip(k * n, (k + 1) * n, full, full, n)
    last = (len(mid) - 1) * n
    strip(west, 0, list(range(len(COPED))), COPED, len(COPED))
    strip(last, east, COPED, list(range(len(COPED))), len(COPED))
    for a, b, c in COPED_CAP:
        faces.append((west + a, west + c, west + b))         # west end faces -X
        faces.append((east + a, east + b, east + c))         # east end faces +X
    for w in WINGS:
        for k in range(1, len(w) - 1):
            faces.append((w[0], w[k + 1], w[k]))             # wing faces at the west cope line face -X
            faces.append((last + w[0], last + w[k], last + w[k + 1]))
    out = trimesh.Trimesh(vertices=np.array(verts), faces=np.array(faces), process=False)
    return out, dict(beam_y_m=round(float(yb), 6), ends_x_m=[round(x0, 6), round(x1, 6)], top_slope=round(float(slope), 6),
                     full_section_rows=len(mid))


def trim_to_deck(mesh):
    """Keep the part between the deck ends, q in [-17.8943, +17.8943] (manifold boolean intersection)."""
    region = first.prism([-HALF, HALF], [(-8.0, 0), (8.0, 0), (8.0, 1), (-8.0, 1)],
                         lambda q, y, h: (float(sx(q, y)), y, -20 + 60 * h))
    return trimesh.boolean.intersection([mesh, region], engine='manifold')


def curb_profile():
    """Sheet 25 INTEGRAL CONCRETE CURB TYPE B Modified: (inches from the outer face toward traffic, inches above the
    slab bottom). 8 in wide, 12 in slab + 4 in, 7 in flat top, 1 in batter, 2 in radius (four chords)."""
    d = np.array([1.0, -4.0]) / np.sqrt(17.0)
    half = np.arccos(-1 / np.sqrt(17.0)) / 2
    t = 2 / np.tan(half)
    centre = np.array([7 - t, 14.0])
    a0 = np.arctan2(*(np.array([7.0, 16.0]) + t * d - centre)[::-1])
    arc = [tuple(centre + 2 * np.array([np.cos(a), np.sin(a)])) for a in np.linspace(a0, np.pi / 2, 5)]
    return [(0.0, 0.0), (8.0, 0.0), (8.0, 12.0)] + arc + [(0.0, 16.0)]


def curb_limits(end, side):
    """The curb starts at the TFC end face, which is 9 1/4" beyond the slab corner (sheet 25) within 0.02 mm."""
    x0 = tfc_start(end, side) + end * TFC_LEN
    return x0, x0 + end * CURB_LEN


def build_curb(end, side):
    x0, x1 = curb_limits(end, side)
    edge = side * RCBA_WIDE
    return first.prism(np.linspace(x0, x1, max(2, int(CURB_LEN / .6) + 1)),
                       [(v * IN, z * IN) for v, z in curb_profile()],
                       lambda x, v, z: (x, edge + side * (CURB_W - v), surface(x, edge + side * (CURB_W - v))
                                        - first.APPROACH_T + z))


def ledge_zone(b):
    """Y range under the slab, its acute-corner extension and the obtuse-corner curb at bent b (0 west, 1 east)."""
    return (-COPING, RCBA_WIDE + CURB_W) if b == 0 else (-(RCBA_WIDE + CURB_W), COPING)


def build_backwall(b, y0, y1, seat):
    """Bent back strip over the drawn 9 in ledge (back face of the bent to the deck end), stepped top."""
    u, end = first.BENTS[b]['u'], first.BENTS[b]['end']
    qq = sorted([u + end * first.HALF_THICK, end * HALF])
    lo, hi = ledge_zone(b)
    profile = [(y0, 0), (lo, 0), (0.0, 0), (hi, 0), (y1, 0), (y1, 1), (hi, 1), (hi, 2), (0.0, 2), (lo, 2), (lo, 1),
               (y0, 1)]
    caps = [(0, 1, 9), (0, 9, 10), (0, 10, 11), (1, 2, 8), (1, 8, 9), (2, 3, 7), (2, 7, 8), (7, 3, 4), (7, 4, 5),
            (7, 5, 6)]

    def point(s, y, lev):
        x = float(sx(s, y))
        return x, y, (seat, surface(x, y) - SLAB, surface(x, y) - THICK)[lev]

    return first.prism(qq, profile, point, caps=caps)


def build_joint(end, north, south):
    qq = [end * HALF - JOINT_HALF, end * HALF + JOINT_HALF]
    return first.prism(qq, [(north, 0), (0.0, 0), (-south, 0), (-south, 1), (0.0, 1), (north, 1)],
                       lambda s, y, h: (sx(s, y), y, surface(sx(s, y), y) - JOINT_DEPTH + h * JOINT_DEPTH),
                       caps=[(0, 1, 4), (0, 4, 5), (1, 2, 3), (1, 3, 4)])


def correct(base=BASE, backup=BACKUP):
    mp = base / 'model_manifest.json'
    raw_manifest = mp.read_bytes()
    manifest = json.loads(raw_manifest)
    if manifest.get(TAG_KEY) == TAG:
        print('Already corrected.')
        return
    path = base / 'model.glb'
    original = path.read_bytes()
    before = hashlib.sha256(original).hexdigest()

    def expect(ok, what):
        if not ok:
            raise ValueError(f'{BID}: unexpected starting model ({what})')

    expect(manifest.get('review_correction_2') == PREVIOUS_TAG and manifest.get('revision') == PREVIOUS_REVISION,
           f'run scripts/correct_us35_deer_review_2.py first (revision {manifest.get("revision")})')
    expect(before == EXPECTED_GLB_SHA256 == manifest['review_correction_2_record']['after_glb_sha256'],
           f'model.glb SHA-256 {before} is not the revision 1.2 output')
    expect({d.get('id') for d in manifest.get('known_deviations', [])} == {'tfc-transition-section',
                                                                          'approach-display-joint'},
           'known_deviations')

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

    def native(pid):
        m = meshes[pid]
        expect(len(m['primitives']) == 1, f'{pid} primitive')
        prim = m['primitives'][0]
        mesh = trimesh.Trimesh(vertices=first.to_native(read(prim['attributes']['POSITION']).astype(np.float64)),
                               faces=read(prim['indices']).reshape(-1, 3), process=False)
        expect(mesh.is_watertight and mesh.volume > 0, f'{pid} not a closed solid')
        return mesh

    # ---- Starting state. ----
    deck = native('deck')
    expect(abs(np.abs(q_of(deck.vertices)).max() - HALF) < TOL, 'deck end not at q = +/-17.8943')
    old = {}
    for side in (1, -1):
        pid = f'FC_rail_{-side}'
        m = old[pid] = native(pid)
        v = m.vertices
        rel = np.column_stack([(REAR - side * v[:, 1]) / IN, (v[:, 2] - surface(v[:, 0], v[:, 1])) / IN])
        expect(len(v) == 6 * RAIL_STATIONS and abs(q_of(v).min() + OLD_RAIL_Q) < TOL
               and abs(q_of(v).max() - OLD_RAIL_Q) < TOL
               and all(np.abs(rel - e).max(axis=1).min() < 1e-3 for e in first.FC_SECTION),
               f'{pid}: not the centred, skew-ended sheet 23 section')
        for end in (-1, 1):
            sfx, acute = corner(end, side)
            pid = f'TFC_transition_{sfx}'
            m = old[pid] = native(pid)
            q, v = q_of(m.vertices), m.vertices
            h = v[:, 2] - surface(v[:, 0], v[:, 1])
            expect(len(v) == 45 and abs(np.abs(q).min() - OLD_RAIL_Q) < TOL and abs(np.abs(q).max() - OLD_EXT_Q) < TOL
                   and np.sign(q.mean()) == end and np.sign(v[:, 1].mean()) == side
                   and abs(h.max() - TFC_H) < 1e-3 and h[np.abs(q) > OLD_EXT_Q - TOL].max() < .71,
                   f'{pid}: not the generic envelope (skewed, easing to 0.70 m)')
            pid = f'extension_{sfx}'
            m = old[pid] = native(pid)
            q, v = q_of(m.vertices), m.vertices
            inner = TOE if acute else RCBA_WIDE
            expect(len(v) == 20 and abs(np.abs(q).min() - HALF) < TOL and abs(np.abs(q).max() - OLD_EXT_Q) < TOL
                   and abs(np.abs(v[:, 1]).min() - inner) < TOL and abs(np.abs(v[:, 1]).max() - COPING) < TOL
                   and np.sign(v[:, 1].mean()) == side, f'{pid}: not the nominal 2.48-2.56 m envelope')
            expect(acute or ENVELOPES[pid][1:] == (end, side), f'{pid} corner')
    widths = {}
    for end in (-1, 1):
        pid = f'approach_{end}'
        m = old[pid] = native(pid)
        v = m.vertices
        near = np.abs(q_of(v) - end * OLD_NEAR_Q) < TOL
        expect(len(v) == 144 and near.sum() == 6 and abs(np.abs(q_of(v)).min() - OLD_NEAR_Q) < TOL
               and abs(np.abs(v[:, 0]).max() - abs(first.APPROACH_FAR[end])) < TOL, f'{pid}: near edge not at 25 mm')
        north, south = v[:, 1].max(), -v[:, 1].min()
        expect(abs(north - second.RCBA_EDGE[(0 if end < 0 else 1, 1)]) < TOL
               and abs(south - second.RCBA_EDGE[(0 if end < 0 else 1, -1)]) < TOL, f'{pid} edges')
        top = v[v[:, 2] > surface(v[:, 0], v[:, 1]) - .1]
        expect(len(top) == 72 and np.abs(top[:, 2] - surface(top[:, 0], top[:, 1])).max() < TOL,
               f'{pid} top not on the crowned surface')
        widths[end] = (north, south)
        pid = f'joint_{end}'
        m = old[pid] = native(pid)
        jq, v = q_of(m.vertices), m.vertices
        expect(len(v) == 12 and abs(jq.min() - (end * HALF - JOINT_HALF)) < TOL
               and abs(jq.max() - (end * HALF + JOINT_HALF)) < TOL and abs(np.abs(v[:, 1]).max() - COPING) < TOL
               and abs(v[:, 1].min() + COPING) < TOL, f'{pid} not the full-width strip centred on the deck end')
    seats = {}
    for b, k in first.BENTS.items():
        u, end = k['u'], k['end']
        cap = native(f'cap_{b + 1}').vertices
        seats[b] = seat = cap[:, 2].max()
        expect(abs(q_of(cap).min() - (u - first.HALF_THICK)) < TOL and abs(q_of(cap).max() - (u + first.HALF_THICK))
               < TOL, f'cap_{b + 1} limits')
        pid = f'backwall_{b}'
        m = old[pid] = native(pid)
        v = m.vertices
        topv = v[:, 2] > seat + .1
        expect(len(v) == 12 and abs(np.abs(q_of(v) - u).min() - OLD_BACKWALL[0]) < TOL
               and abs(np.abs(q_of(v) - u).max() - OLD_BACKWALL[1]) < TOL and abs(v[:, 2].min() - seat) < TOL
               and np.abs(v[topv, 2] - surface(v[topv, 0], v[topv, 1]) + SLAB).max() < TOL
               and abs(v[:, 1].min() - cap[:, 1].min()) < TOL and abs(v[:, 1].max() - cap[:, 1].max()) < TOL,
               f'{pid}: not the 0.39-0.60 m strip with its top at the deck soffit')
        for j in range(0, 10, 2):
            pid = f'integral_infill_{b}_{j}'
            m = old[pid] = native(pid)
            v = m.vertices
            back = np.abs(q_of(v) - (u + end * OLD_INFILL_BACK)) < TOL
            topv = v[:, 2] > seat + .1
            expect(back.sum() == len(v) // 2 and abs(v[:, 2].min() - seat) < TOL
                   and np.abs(v[topv, 2] - surface(v[topv, 0], v[topv, 1]) + SLAB).max() < TOL,
                   f'{pid}: end-side face not 0.38 m behind the bent centre line')
    for j in range(4):
        for pid, n in ((f'beam_0_{j}', 1136), (f'haunch_0_{j}', 284)):
            m = old[pid] = native(pid)
            v = m.vertices
            yb = (v[:, 1].min() + v[:, 1].max()) / 2
            expect(len(v) == n and abs(v[:, 0].min() - (TAN * yb - BEAM_HALF_LEN)) < TOL
                   and abs(v[:, 0].max() - (TAN * yb + BEAM_HALF_LEN)) < TOL
                   and abs(np.ptp(v[:, 1]) - 2 * first.FLANGE_HALF) < TOL, f'{pid}: not the full square-ended member')

    # ---- Rebuild. ----
    new, values = {}, {}
    wing = np.array([(4, 0), (24.5, 0), (24.5, -5), (7, -8), (4, -11)]) * IN      # model section, one flange wing
    wing_area = 0.5 * abs(np.dot(wing[:, 0], np.roll(wing[:, 1], -1)) - np.dot(wing[:, 1], np.roll(wing[:, 0], -1)))
    for j in range(4):
        pid = f'beam_0_{j}'
        new[pid], info = cope_beam(old[pid])
        ov, nv = old[pid].vertices, new[pid].vertices
        inner = ov[(ov[:, 0] > ov[:, 0].min() + COPE_LEN + 1e-6) & (ov[:, 0] < ov[:, 0].max() - COPE_LEN - 1e-6)]
        expect(max(np.abs(nv - p).max(axis=1).min() for p in inner) < 2e-5, f'{pid}: rebuilt section off the original')
        e = np.sort(new[pid].faces[:, [0, 1, 1, 2, 2, 0]].reshape(-1, 2), axis=1)
        expect((np.unique(e, axis=0, return_counts=True)[1] == 2).all() and new[pid].is_winding_consistent,
               f'{pid}: cope not a closed 2-manifold')
        removed = float(old[pid].volume - new[pid].volume)
        expect(abs(removed - 4 * wing_area * COPE_LEN) < 3e-5, f'{pid}: cope volume {removed:.6f}')
        values[pid] = dict(info, cope_length_m=round(COPE_LEN, 6), kept_web_width_m=round(2 * WEB_HALF, 6),
                           cope_depth_m=round(FLANGE_DEPTH, 6), removed_m3=round(removed, 6))
        pid = f'haunch_0_{j}'
        new[pid] = trim_to_deck(old[pid])
        values[pid] = dict(trimmed_at_q_m=[-round(HALF, 6), round(HALF, 6)],
                           removed_m3=round(float(old[pid].volume - new[pid].volume), 7),
                           was_q_m=[round(float(q_of(old[pid].vertices).min()), 6),
                                    round(float(q_of(old[pid].vertices).max()), 6)])
    for side in (1, -1):
        pid = f'FC_rail_{-side}'
        new[pid] = build_rail(side)
        x0, x1 = rail_limits(side)
        values[pid] = dict(x_limits_m=[round(x0, 6), round(x1, 6)], stations=[station(x0), station(x1)],
                           moved_along_x_m=round(side * (abs(x1 if side > 0 else x0) - (OLD_RAIL_Q + TAN * TOE)), 6),
                           was='centred, skewed ends at q = %+.6f / %+.6f m' % (-OLD_RAIL_Q, OLD_RAIL_Q))
        for end in (-1, 1):
            sfx, acute = corner(end, side)
            pid = f'TFC_transition_{sfx}'
            new[pid] = build_tfc(end, side)
            xb = tfc_start(end, side)
            x_out = xb + end * TFC_LEN
            de_front = float(sx(end * HALF, side * (TOE + 7 * IN)))
            de_rear = float(sx(end * HALF, side * REAR))
            values[pid] = dict(corner=('acute' if acute else 'obtuse'), butt_joint_x_m=round(xb, 6),
                               outer_end_x_m=round(x_out, 6), outer_end_station=station(x_out),
                               sheet6_station=station((SHEET6[pid] - 127160) * FT),
                               sheet6_difference_m=round(x_out - (SHEET6[pid] - 127160) * FT, 4),
                               beyond_deck_end_m=[round(end * (x_out - de_front), 4), round(end * (x_out - de_rear), 4)]
                               if not acute else None,
                               stands_on='approach slab extension (sheet 23)' if acute else
                               'bridge deck (sheet 23); the last 0.235-0.296 m beyond the deck end are not supported '
                               'by any drawn part')
            if acute:
                pid = f'extension_{sfx}'
                new[pid], x_far = build_extension(end, side)
                values[pid] = dict(y_m=sorted([round(side * TOE, 6), round(side * COPING, 6)]),
                                   inner_end='deck end, q = %+.4f m' % (end * HALF), outer_end_x_m=round(x_far, 6),
                                   length_on_toe_line_m=round(EXT_LEN, 6),
                                   was='q %+.4f to %+.4f m, skewed outer end' % (end * HALF, end * OLD_EXT_Q))
    for end in (-1, 1):
        pid = f'approach_{end}'
        new[pid] = build_approach(end, *widths[end])
        values[pid] = dict(near_edge_q_m=round(end * HALF, 6), was_q_m=round(end * OLD_NEAR_Q, 6),
                           volume_m3=[round(float(old[pid].volume), 6), round(float(new[pid].volume), 6)])
        north, south = (RCBA_WIDE, COPING) if end < 0 else (COPING, RCBA_WIDE)
        pid = f'joint_{end}'
        new[pid] = build_joint(end, north, south)
        values[pid] = dict(y_m=[round(-south, 6), round(north, 6)], was_y_m=[-COPING, COPING],
                           q_m=[round(end * HALF - JOINT_HALF, 6), round(end * HALF + JOINT_HALF, 6)])
    added = {}
    for env, (pid, end, side) in ENVELOPES.items():
        added[pid] = build_curb(end, side)
        x0, x1 = curb_limits(end, side)
        values[pid] = dict(replaces=env, x_m=sorted([round(x0, 6), round(x1, 6)]),
                           y_m=sorted([round(side * RCBA_WIDE, 6), round(side * (RCBA_WIDE + CURB_W), 6)]),
                           start_setback_from_slab_corner_m=round(end * (x0 - float(sx(end * HALF, side * RCBA_WIDE))), 6),
                           sheet25_setback_m=round(CURB_SETBACK, 6))
    for b, k in first.BENTS.items():
        u, end = k['u'], k['end']
        pid = f'backwall_{b}'
        ov = old[pid].vertices
        new[pid] = build_backwall(b, ov[:, 1].min(), ov[:, 1].max(), seats[b])
        lo, hi = ledge_zone(b)
        values[pid] = dict(q_m=sorted([round(u + end * first.HALF_THICK, 6), round(end * HALF, 6)]),
                           was_q_m=sorted([round(u + end * OLD_BACKWALL[0], 6), round(u + end * OLD_BACKWALL[1], 6)]),
                           ledge_top='14 in slab soffit (top - 0.3556 m) for Y in [%.4f, %.4f]' % (lo, hi),
                           elsewhere='deck soffit (top - 0.2032 m), unchanged')
        for j in range(0, 10, 2):
            pid = f'integral_infill_{b}_{j}'
            v = old[pid].vertices.copy()
            back = np.abs(q_of(v) - (u + end * OLD_INFILL_BACK)) < TOL
            v[back, 0] += end * HALF - q_of(v[back])
            topv = back & (v[:, 2] > seats[b] + .1)
            v[topv, 2] = surface(v[topv, 0], v[topv, 1]) - SLAB
            new[pid] = trimesh.Trimesh(vertices=v, faces=old[pid].faces, process=False)
            values[pid] = dict(end_side_face_q_m=round(end * HALF, 6), was_q_m=round(u + end * OLD_INFILL_BACK, 6))

    # ---- Checks on the rebuilt solids. ----
    for pid, m in {**new, **added}.items():
        expect(m.is_watertight and m.is_winding_consistent and m.volume > 0, f'{pid} rebuilt solid')
    for side in (1, -1):
        r = new[f'FC_rail_{-side}']
        expect(abs(np.ptp(r.vertices[:, 0]) - RAIL_LEN) < 1e-6
               and abs(r.volume - old[f'FC_rail_{-side}'].volume) < 1e-4, 'FC rail length or volume')
        for end in (-1, 1):
            sfx, acute = corner(end, side)
            t = new[f'TFC_transition_{sfx}'].vertices
            xb = tfc_start(end, side)
            joint = t[np.abs(t[:, 0] - xb) < 1e-9]
            face = r.vertices[np.abs(r.vertices[:, 0] - xb) < 1e-9]
            expect(len(joint) == 6 and len(face) == 6
                   and max(np.abs(face - p).max(axis=1).min() for p in joint) < 1e-9,
                   f'TFC_transition_{sfx} butt joint section')
            h = t[:, 2] - surface(t[:, 0], t[:, 1])
            expect((h > .5).sum() == 8 and np.abs(h[h > .5] - TFC_H).max() < 1e-9, f'TFC {sfx} height')
            if acute:
                expect(abs(xb - sx(end * HALF, side * TOE)) < 1e-9, f'TFC {sfx} butt joint not at the deck end')
            else:
                expect(abs(values[f'curb_{sfx}']['start_setback_from_slab_corner_m'] - CURB_SETBACK) < 1e-4,
                       f'curb_{sfx}: the TFC end is not 9 1/4" beyond the slab corner')
    for end in (-1, 1):
        v = new[f'approach_{end}'].vertices
        expect(np.abs(np.abs(q_of(v)).min() - HALF) < 1e-9 and (np.abs(q_of(v)) >= HALF - 1e-9).all(),
               f'approach_{end} near edge')
    for j in range(4):
        for pid in (f'beam_0_{j}', f'haunch_0_{j}'):
            expect(np.abs(q_of(new[pid].vertices)).max() <= HALF + 1e-5, f'{pid} reaches beyond the deck end')
    for b in (0, 1):
        v = new[f'backwall_{b}'].vertices
        expect(abs(np.abs(q_of(v)).min() - HALF) < 1e-9 and len(v) == 24, f'backwall_{b} front not on the deck end')
        for j in range(0, 10, 2):
            v = new[f'integral_infill_{b}_{j}'].vertices
            expect(abs(np.abs(q_of(v)).max() - HALF) < 1e-9, f'integral_infill_{b}_{j} back not on the deck end')

    # ---- Write rebuilt meshes; remove the obtuse-corner envelopes and add the curbs in their slots. ----
    def write(pid, m, color=None):
        prim = meshes[pid]['primitives'][0]
        a_col = prim['attributes']['COLOR_0']
        prim['attributes']['POSITION'] = append(first.to_gltf(m.vertices).astype('<f4'), 'VEC3', 5126)
        if color is not None or len(m.vertices) != gltf['accessors'][a_col]['count']:
            rgba = read(a_col)[0] if color is None else np.array(color, dtype='u1')
            prim['attributes']['COLOR_0'] = append(np.tile(rgba, (len(m.vertices), 1)).astype('u1'), 'VEC4', 5121)
            gltf['accessors'][prim['attributes']['COLOR_0']]['normalized'] = True
        if pid.startswith('integral_infill'):
            pass                              # same topology: index accessor kept
        else:
            prim['indices'] = append(m.faces.reshape(-1, 1).astype('<u4'), 'SCALAR', 5125)

    for pid, m in new.items():
        write(pid, m)
        parts[pid]['bounds_m'] = m.bounds.round(6).tolist()
        parts[pid]['volume_m3'] = round(float(m.volume), 9)

    slab = parts['approach_-1']['color']
    rgb = [int(slab[i:i + 2], 16) for i in (1, 3, 5)] + [255]
    node_of = {gltf['meshes'][n['mesh']]['name']: n for n in gltf['nodes'] if 'mesh' in n}
    order = [p['id'] for p in manifest['parts']]
    for env, (pid, end, side) in ENVELOPES.items():
        m = added[pid]
        mesh = meshes.pop(env)
        mesh['name'] = pid
        node_of[env]['name'] = pid
        meshes[pid] = mesh
        write(pid, m, rgb)
        x0, x1 = sorted(curb_limits(end, side))
        where = 'north-west' if side > 0 else 'south-east'
        entry = dict(
            id=pid, name=f'Integral concrete curb Type B (Modified), {where}', layer='approaches', color=slab,
            pdf_pages=[11, 25], basis='Dimensioned section, 11 ft length and 9 1/4 in setback (sheet 25)',
            note=(f'11 ft Integral Concrete Curb Type B (Modified) on the 18\'-3" edge of the '
                  f'{"west" if end < 0 else "east"} approach slab at the obtuse {where} corner (sheets 11, 25): 8" '
                  'wide outside the slab edge, from the slab bottom to 4" above its top, 7" flat top and 1" batter '
                  'with a 2" radius on the traffic side (sheet 25 curb detail), from the TFC end face, 9 1/4" beyond '
                  'the slab corner (sheet 25 plans; the two agree within 0.02 mm), for 11\'-0" along the slab. '
                  'Follows the 2 % crown like the '
                  'slab; #5 x 3\'-0" bars at 1\'-6" not modelled. Rev. 1.3: replaces the undocumented 2.56 m corner '
                  f'envelope {env}, which had no drawing counterpart (sheet 25 bills extensions at the two acute '
                  'corners only).'),
            dimensions=dict(length_m=round(CURB_LEN, 6), width_m=round(CURB_W, 6),
                            height_above_slab_top_m=round(CURB_UP, 6), depth_m=round(first.APPROACH_T + CURB_UP, 6),
                            top_flat_m=round(7 * IN, 6), batter_m=round(IN, 6), top_radius_m=round(2 * IN, 6),
                            x_limits_m=[round(x0, 6), round(x1, 6)],
                            setback_from_slab_corner_m=values[pid]['start_setback_from_slab_corner_m']),
            bounds_m=m.bounds.round(6).tolist(), volume_m3=round(float(m.volume), 9))
        manifest['parts'][order.index(env)] = entry
        parts.pop(env)
        parts[pid] = entry
        mesh['extras'] = dict(processed=True, **entry)

    def pages(pid, extra):
        parts[pid]['pdf_pages'] = sorted(set(parts[pid]['pdf_pages']) | set(extra))

    for side in (1, -1):
        pid = f'FC_rail_{-side}'
        x0, x1 = rail_limits(side)
        acute_end = 'east' if side > 0 else 'west'
        parts[pid]['note'] += (
            f' Rev. 1.3: square butt joints at X = {x0:.4f} / {x1:.4f} m (sheet 11 plan); the {acute_end} end is at the '
            'deck end on the 17\'-8" toe line, at the acute corner, and the other end 102\'-4 3/8" from it, where the '
            'TFC on the deck begins (sheet 23 elevations, sheet 11). The model had centred the rail with skewed ends at '
            f'q = -/+{OLD_RAIL_Q:.4f} m; moved {abs(values[pid]["moved_along_x_m"]):.4f} m '
            f'{"east" if side > 0 else "west"}, section and length unchanged.')
        parts[pid]['dimensions'].update(length_m=round(RAIL_LEN, 6), x_limits_m=[round(x0, 6), round(x1, 6)],
                                        square_ends=True)
        pages(pid, [11, 23])
        for end in (-1, 1):
            sfx, acute = corner(end, side)
            pid = f'TFC_transition_{sfx}'
            xb = tfc_start(end, side)
            p = parts[pid]
            p['basis'] = ('Sheet 11 plan outline and 15\'-8" length (CAD linework), sheet 23 height, butt joint and '
                          'FC section; face between the joint and the vertical end interpolated')
            p['note'] = (
                f'Concrete bridge railing transition Type TFC at the {"acute" if acute else "obtuse"} '
                f'{"north" if side > 0 else "south"}-{"east" if end > 0 else "west"} corner, on the '
                f'{"approach slab extension" if acute else "deck"} (sheet 23 elevations). 15\'-8" long with square '
                f'ends, from the FC butt joint at X = {xb:.4f} m (sheet 11); 2\'-9" high throughout (sheet 23); rear '
                'face continuous with the FC, 2" inside the coping. It starts with the FC section (sheet 23 section '
                'A-A, butt joint); the traffic-face toe recedes 5" over the first 7\'-2 1/2" and 2" over the next '
                '4\'-3", then the face is vertical, 7" behind the FC toe (a 9" wall), for the last 4\'-2 1/2" (sheet '
                '11). Between the joint and the vertical end the lower 5" slope is removed first and then the 2" '
                'upper batter, keeping the 3" and 10" break heights (interpretation of the plan line). Terminal '
                'connector recesses, anchorage, chamfers and end details are not modelled (E706-TTFC, E706-CBRT). '
                + ('' if acute else
                   'Its outer end is 15\'-8" from the butt joint (sheet 11) and 9 1/4" beyond the slab corner, where '
                   'the curb starts (sheet 25): 0.235-0.296 m beyond the deck end, with nothing drawn under that part '
                   '(known deviation); sheet 6 puts the guardrail end about 0.5 ft shorter, the bridge sheets govern. ')
                + 'Rev. 1.3 (was a generic envelope straddling the deck end, easing to 0.70 m). ' + ORIENT_NOTE)
            p['dimensions'] = dict(height_m=round(TFC_H, 6), base_width_m=round(16 * IN, 6),
                                   end_width_m=round(9 * IN, 6), length_m=round(TFC_LEN, 6),
                                   butt_joint_x_m=round(xb, 6), outer_end_x_m=round(xb + end * TFC_LEN, 6),
                                   toe_recession_from_joint_m=[[round(d, 6), round(t * IN, 6)] for d, t in TFC_PLAN],
                                   corner='acute' if acute else 'obtuse')
            pages(pid, [6, 11, 23] + ([] if acute else [25]))
            if acute:
                pid = f'extension_{sfx}'
                p = parts[pid]
                p['basis'] = ('Dimensioned plan (15\'-10" x 1\'-6", sheet 25); thickness taken equal to the 12 in RCBA, '
                              'with its 2 in thickening at the bent')
                p['note'] = (
                    'Approach slab extension under the TFC at the acute corner (sheet 23 elevations): 15\'-10" from '
                    'the slab corner on the 17\'-8" edge to a square outer end, 1\'-6" wide to the coping line (sheet '
                    '25 plan, "RCBA Extension 2 x 2.6 Sys"; sheet 11 draws the end 2" beyond the TFC). Inner end on '
                    'the deck end, against which the RCBA is cast (sheets 15, 25); top on the crowned surface. Taken '
                    'as the RCBA: 1 ft thick, 14 in over the first 2\'-3" from the deck end with a 45 deg return '
                    '(sheet 25 pavement ledge detail; sheet 23 draws the extension deeper next to the deck); its own '
                    'thickness and reinforcing are in E 609-TBAE-01 to -03 (sheet 25 note 3), not in this plan set. '
                    'Rev. 1.3 (was a 2.48 m nominal envelope with a skewed end). ' + ORIENT_NOTE)
                p['dimensions'] = dict(length_on_toe_line_m=round(EXT_LEN, 6), width_m=round(COPING - TOE, 6),
                                       thickness_m=round(EXT_T, 6), thickness_at_bent_m=round(THICK, 6),
                                       outer_end_x_m=values[pid]['outer_end_x_m'], inner_end='deck end')
                pages(pid, [11, 23, 25])
    for end in (-1, 1):
        pid = f'approach_{end}'
        p = parts[pid]
        for old_text, new_text in ((' The skewed edge keeps the 25 mm display joint.', ''),
                                   ('Narrow corner curb and transition extensions are separate approximate envelopes.',
                                    'The obtuse-corner curb and the acute-corner extension are separate parts.')):
            expect(old_text in p['note'], f'{pid} note')
            p['note'] = p['note'].replace(old_text, new_text)
        p['note'] += (f' Rev. 1.3: the skewed near edge is cast against the deck end, q = {end * HALF:+.4f} m, with '
                      'no gap (sheet 15 sections A-A to C-C and sheet 25 pavement ledge detail: one interface line '
                      'with the Type IA joint at its top); the 25 mm display gap is removed. Sheet 25 pavement ledge '
                      'detail: 2" deeper (14") from the deck end over the 9" ledge and 1\'-6" beyond, then a 45 deg '
                      'return to the 12" slab (distances normal to the deck end; 0.7100 and 0.7626 m along X). It '
                      'bears on the ledge of the bent (backwall), whose top is at that 14" soffit.')
        p['dimensions'].update(near_edge_q_m=round(end * HALF, 6), joint_gap_m=0.0, thickness_at_bent_m=round(THICK, 6),
                               thickening_q_m=[round(BAND[1][0], 6), round(BAND[2][0], 6)])
        pages(pid, [15])
        pid = f'joint_{end}'
        lo, hi = values[pid]['y_m']
        parts[pid]['note'] += (
            ' Rev. 1.3: the approach slab now abuts the deck end (sheets 15, 25), so this strip, centred on the '
            f'interface, lies 12 mm into the deck and 12 mm into the slab; it spans the slab and its extension only, '
            f'Y = {lo:.4f} to {hi:.4f} m (was the full coping width; beyond the 18\'-3" slab edge at the obtuse corner '
            'there is no slab joint). It marks the sealed saw-cut Type IA joint; its 24 mm x 60 mm size is a display '
            'size (E 609-BRJT-01, sheet 25 note 4).')
        parts[pid]['pdf_pages'] = sorted(set(parts[pid]['pdf_pages']) | {11, 15, 25})
    for b, k in first.BENTS.items():
        u, end = k['u'], k['end']
        pid = f'backwall_{b}'
        lo, hi = ledge_zone(b)
        parts[pid]['basis'] = ('Drawn 9 in pavement ledge strip (sheet 15 sections A-A to C-C, sheet 25 pavement '
                               'ledge detail); top at the 14 in slab soffit under the slab and extension')
        parts[pid]['note'] += (
            f' Rev. 1.3: rebuilt over the drawn 9" pavement ledge, from the back face of the bent (q = '
            f'{u + end * first.HALF_THICK:+.6f}, flush with the cap) to the deck end (q = {end * HALF:+.4f}), where '
            'the closure bays now stop (sheet 15: 9" + 1\'-2" + 1\'-11"). Its top is the ledge at the soffit of '
            f'the 14" slab (12" + 2" over the ledge), 0.3556 m below the crowned surface, for Y = {lo:.4f} to {hi:.4f} '
            'm under the approach slab, its extension and the curb, so the slab bears on it instead of cutting into '
            'it (sheet 25 pavement ledge detail); beyond that toward the bent ends it stays at the deck soffit (the '
            'model\'s rule). Was 0.39-0.60 m behind the bent centre line with its top at the deck soffit '
            'throughout. The 1/2" expanded polystyrene fillers are not modelled.')
        parts[pid]['dimensions'].update(q_limits_m=values[pid]['q_m'], ledge_top_y_m=[round(lo, 6), round(hi, 6)],
                                        ledge_width_normal_m=round(9 * IN, 6))
        pages(pid, [15, 25])
        for j in range(0, 10, 2):
            pid = f'integral_infill_{b}_{j}'
            parts[pid]['note'] += (
                f' Rev. 1.3: end-side face moved from {OLD_INFILL_BACK} m behind the bent centre line to the deck end '
                f'(q = {end * HALF:+.4f}), 11.7 mm, so the closure concrete stops at the face against which the '
                'approach slab is cast (sheet 15 sections A-A to C-C).')
            pages(pid, [15])
    for j in range(4):
        pid = f'beam_0_{j}'
        expect('end copes and actual camber omitted.' in parts[pid]['note'], f'{pid} note')
        parts[pid]['note'] = parts[pid]['note'].replace('end copes and actual camber omitted.', 'actual camber omitted.')
        parts[pid]['note'] += (
            ' Rev. 1.3: end copes per sheet 19 BEAM PLAN (the top flange stops 6" short of each square beam end) and '
            'sheet 20 END SECTION (the area to be coped is the flange outside the 8" web, down to the web, 11" below '
            'the top): the flange wings are removed over the last 6" at both ends, the web and bottom flange are '
            'kept. The beam now ends inside the deck end (it reached 27 mm beyond it at the acute flange corner).')
        parts[pid]['dimensions'] = dict(parts[pid].get('dimensions', {}), end_cope_length_m=round(COPE_LEN, 6),
                                        end_cope_web_width_m=round(2 * WEB_HALF, 6),
                                        end_cope_depth_m=round(FLANGE_DEPTH, 6))
        pages(pid, [19, 20])
        pid = f'haunch_0_{j}'
        parts[pid]['note'] += (
            ' Rev. 1.3: trimmed at the deck ends, q = -/+17.8943 m, where the approach slab is cast against the deck '
            '(sheets 15, 25); it followed the square beam end up to 27 mm beyond them.')
        pages(pid, [15, 25])
    for pid in new:
        meshes[pid]['extras'].update(parts[pid])

    for item in manifest.get('detail_coverage', []):
        if item.get('feature') == 'External rails and approaches':
            item['detail'] += (' Revision 1.3: FC rails square-ended at the drawn butt joints (at the deck end at the '
                               'acute corners); TFCs 15\'-8", 2\'-9" high, on the sheet 11 plan taper; acute-corner '
                               'extensions 15\'-10" x 1\'-6"; 11 ft integral curbs at the obtuse corners; approach '
                               'slabs cast against the deck end.')
            item['part_ids'] = [ENVELOPES[p][0] if p in ENVELOPES else p for p in item['part_ids']]
            for s in ('Primary PDF p.6', 'Primary PDF p.15'):
                if s not in item['sources']:
                    item['sources'].append(s)
        elif item.get('feature') == 'Integral support topology':
            item['detail'] += (' Back strips over the 9 in pavement ledge with the slab bearing on them; closure bays '
                               'stop at the deck end (sheets 15, 25; revision 1.3).')

    expect(set(parts) == set(meshes) == {p['id'] for p in manifest['parts']} and len(parts) == 72, 'final part list')
    for pid, m in {**new, **added}.items():
        expect(np.abs(np.array(parts[pid]['bounds_m']) - m.bounds).max() < 1e-6, f'{pid} bounds')

    while len(binary) % 4:
        binary.append(0)
    gltf['buffers'][0]['byteLength'] = len(binary)
    encoded = json.dumps(gltf, ensure_ascii=True, separators=(',', ':')).encode()
    encoded += b' ' * ((-len(encoded)) % 4)
    out = (struct.pack('<III', 0x46546c67, 2, 28 + len(encoded) + len(binary)) +
           struct.pack('<II', len(encoded), 0x4e4f534a) + encoded + struct.pack('<II', len(binary), 0x004e4942) + binary)
    backup.mkdir(parents=True, exist_ok=True)
    (backup / f'{BID}_before_review_correction_3.glb').write_bytes(original)
    (backup / f'{BID}_manifest_before_review_correction_3.json').write_bytes(raw_manifest)
    path.write_bytes(out)

    kept = dict(
        id='tfc-transition-section', parts='TFC_transition_*', source='sheets 11, 23, 25 (PDF 11, 23, 25)',
        deviation='The TFC plan outline, 15\'-8" length, square ends, 2\'-9" height and the FC section at the butt '
                  'joint follow sheets 11 and 23, but the face between the butt joint and the vertical end is an '
                  'interpolation: the sheet 11 toe line is followed exactly, with the 5 in lower slope removed first '
                  'and then the 2 in upper batter, at the FC break heights of 3 in and 10 in. Terminal connector '
                  'recesses, anchor bolts, chamfers and the end details are not modelled. At the obtuse corners '
                  '(TFC_transition_-1_-1, TFC_transition_1_1) the last 0.235-0.296 m of the TFC lie beyond the deck '
                  'end, over the bent ledge and partly beyond the back face of the bent, with no part under them '
                  '(about 0.06 m2 of base each).',
        reason='The plan set gives only the plan outline (sheet 11 linework), the length and the height (sheets 11, '
               '23), the butt-joint section (sheet 23 section A-A) and the curb starting at the TFC end (sheet 25). '
               'The transition\'s own sections, break heights, end details and its support beyond the deck end at '
               'the obtuse corners are in INDOT Standard Drawings E706-TTFC-01 to -03 and E706-CBRT-01 (sheet 23 '
               'notes 4 and 5), which are not part of this plan set; those standard drawings would settle it.')
    manifest['known_deviations'] = [kept]
    manifest[TAG_KEY] = TAG
    manifest['revision'] = REVISION
    changed = sorted(new)
    manifest['review_correction_record_3'] = dict(
        source_pdf_pages=[6, 11, 15, 19, 20, 23, 25], printed_sheets=[6, 11, 15, 19, 20, 23, 25],
        previous_revision=PREVIOUS_REVISION,
        native_axes='as revision 1.2: X along increasing station (east, X = 0 at Sta. 1271+60), Y positive to the left '
                    'of increasing station (north), Z up from El. 837.11; q = X - tan(15 deg) Y',
        changed_parts=changed, added_parts=sorted(added), removed_parts=sorted(ENVELOPES),
        slot_reuse={env: pid for env, (pid, _, _) in ENVELOPES.items()},
        resolved_deviations=['approach-display-joint'],
        partly_resolved_deviations={'tfc-transition-section': 'rail layout, TFC length, square ends, plan taper, '
                                    'level 2\'-9" top, butt-joint section and acute-corner extensions resolved; face '
                                    'interpolation, end details and the obtuse-corner end support kept'},
        new_deviations=[],
        resolved={
            'rail_layout': 'FC rails 102\'-4 3/8" with square butt joints, the acute-corner joint at the deck end on '
                           'the 17\'-8" toe line: north X = [-11.8636, 19.3372], south [-19.3372, 11.8636] m (sheet 11 '
                           'plan, sheet 23 elevations); were centred with skewed ends at q = -/+15.6004 m',
            'tfc': 'four 15\'-8" square-ended transitions, 2\'-9" high, starting with the FC section, toe receding 5" '
                   'over 7\'-2 1/2" and 2" over 4\'-3", then vertical 7" behind the FC toe (sheets 11, 23); were '
                   'generic envelopes straddling the deck end and easing to 0.70 m',
            'extensions': 'extension_-1_1 and extension_1_-1: 15\'-10" x 1\'-6", square outer end at X = -/+24.1632 '
                          'm (sheets 11, 23, 25); were 2.48 m with a skewed end',
            'approach_joint': 'approach slab near edges on the deck end, q = -/+17.8943 m (were -/+17.9193 m, a 25 mm '
                              'display gap); sheets 15 and 25 draw the RCBA cast against the deck end',
            'bent_ledge': 'backwall_0 / backwall_1 over the drawn 9" ledge (back face to deck end), top at the slab '
                          'soffit under the slab, extension and curb; the slab no longer cuts 101.6 mm into them '
                          '(0.230 m3 each before, 0.234 m3 with the moved slab) (sheets 15, 25)',
            'closure_faces': 'ten integral_infill_* end-side faces moved 11.7 mm to the deck end; they had cut '
                             '0.0071 m3 per bent out of the moved slab (sheet 15)',
            'joint_strips': 'joint_-1 / joint_1 limited to the drawn slab and extension interface (were the full '
                            'coping width); station range and display size unchanged',
            'obtuse_corners': 'extension_-1_-1 and extension_1_1 removed (no drawing counterpart: sheet 25 bills two '
                              'extensions, at the acute corners); curb_-1_-1 and curb_1_1 added, the drawn 11 ft '
                              'Integral Concrete Curb Type B (Modified) (sheets 11, 25)',
            'slab_thickening': 'approach slabs and acute-corner extensions 14 in thick over the first 2\'-3" (normal) '
                               'from the deck end with a 45 deg return to 12 in; ledge tops lowered to that soffit '
                               '(sheet 25 pavement ledge detail)',
            'beam_end_copes': 'beam_0_0 .. beam_0_3: top-flange wings outside the 8 in web removed over the last 6 in '
                              'at both ends (sheet 19 beam plan, sheet 20 end section); haunch_0_0 .. haunch_0_3 '
                              'trimmed at the deck ends; the beams no longer reach the slab or the ledge'},
        decisions=[
            dict(id='tfc-obtuse-corner-length', verdict='DECIDE', parts=['TFC_transition_-1_-1', 'TFC_transition_1_1'],
                 decision='15\'-8" at all four corners; the north-west and south-east TFCs end 0.235 m (front of the '
                          'vertical end) to 0.296 m (rear) beyond the deck end.',
                 reasoning='Sheet 6 (roadway, not to scale) gives the guardrail-transition ends at Sta. 1271+05.91 and '
                           '1272+14.07, about 0.5 ft short of a 15\'-8" TFC at those corners. The bridge sheets govern '
                           'the bridge railing: sheet 11 draws all four transitions 141.0 pt = 15\'-8", sheet 23 draws '
                           'them equal and bills 4 each of one standard item, sheet 6 matches the 15\'-8" TFC within '
                           '0.05 ft at the acute corners (1270+80.83, 1272+39.16), and sheet 25 starts the curb 9 1/4" '
                           'beyond the slab corner, at the 15\'-8" TFC end within 0.1 mm.'),
            dict(id='extension-inner-end', verdict='DECIDE', parts=['extension_-1_1', 'extension_1_-1'],
                 decision='Inner end on the skewed deck end.',
                 reasoning='Sheet 25 draws the 15\'-10" x 1\'-6" extension as a rectangle from the slab corner; a square '
                           'inner end there would run into the deck triangle beyond the corner. Sheets 15 and 25 draw '
                           'the RCBA cast against the deck end, so the extension is too.'),
            dict(id='joint-strip-kept', verdict='DECIDE', parts=['joint_-1', 'joint_1'],
                 decision='The schematic Type IA joint strips keep their station range and display size, centred on the '
                          'deck end, and now lie 12 mm into the deck and 12 mm into the approach slab.',
                 reasoning='The joint is a sealed saw cut at the top of the contact face (sheets 15, 25); its size is in '
                           'E 609-BRJT-01, not in this plan set. The strip only marks the joint line, which does not '
                           'move.'),
            dict(id='ledge-fillers', verdict='DECIDE', parts=['backwall_0', 'backwall_1'],
                 decision='The 1/2" x 4" and 1/2" x 2" expanded polystyrene are not modelled; the 14 in slab bears '
                          'directly on the ledge.',
                 reasoning='The polystyrene is joint filler (bond breaker), not a void; its 13 mm thickness would only '
                           'add sliver parts.'),
            dict(id='thickening-direction', verdict='DECIDE', parts=['approach_-1', 'approach_1', 'extension_-1_1',
                                                                    'extension_1_-1', 'backwall_0', 'backwall_1'],
                 decision='The 9 in + 1\'-6" thickened length and the 2 in 45 deg return of the sheet 25 pavement '
                          'ledge detail are taken normal to the deck end, 0.7100 m and 0.7626 m along X.',
                 reasoning='The detail\'s "9 in Min." ledge is the 9 in normal ledge of the 3\'-10" bent (sheet 15), so '
                           'the detail is drawn normal to the joint; the thickening runs across the full slab and '
                           'extension width. The obtuse-corner curbs keep the 12 in slab bottom of their own sheet 25 '
                           'detail.')],
        kept_deviations=[dict(id=kept['id'], verdict='keep', missing=kept['deviation'], settled_by=
                              'INDOT Standard Drawings E706-TTFC-01 to -03 and E706-CBRT-01')],
        values=values, before_glb_sha256=before, after_glb_sha256=hashlib.sha256(out).hexdigest())
    text = json.dumps(manifest, indent=2)
    if b'\r\n' in raw_manifest:
        text = text.replace('\n', '\r\n')
    if raw_manifest.endswith(b'\n'):
        text += '\r\n' if b'\r\n' in raw_manifest else '\n'
    mp.write_bytes(text.encode('utf-8'))

    # source_ledger.json lists the approximate part ids; drop the two removed envelopes.
    lp = base / 'source_ledger.json'
    if lp.exists():
        raw = lp.read_bytes()
        ledger = json.loads(raw)
        ids = ledger.get('approximate_part_ids', [])
        if any(env in ids for env in ENVELOPES):
            ledger['approximate_part_ids'] = [i for i in ids if i not in ENVELOPES]
            t = json.dumps(ledger, indent=2)
            if b'\r\n' in raw:
                t = t.replace('\n', '\r\n')
            if raw.endswith(b'\n'):
                t += '\r\n' if b'\r\n' in raw else '\n'
            lp.write_bytes(t.encode('utf-8'))
            print('source_ledger.json: removed', sorted(ENVELOPES), 'from approximate_part_ids')
    print(json.dumps({k: v for k, v in manifest['review_correction_record_3'].items()
                      if k not in ('decisions', 'resolved', 'kept_deviations')}, indent=1))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--base', type=Path, default=BASE, help='bridge folder (default: the repository copy)')
    parser.add_argument('--backup', type=Path, default=BACKUP, help='backup folder')
    args = parser.parse_args()
    correct(args.base, args.backup)

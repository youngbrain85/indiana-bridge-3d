"""Third drawing-confirmed correction of SR 44 over the Branch of Little Blue River: the known deviations left by
the first two reviews. Runs after scripts/correct_sr44_little_blue_review_2.py and preserves unrelated GLB buffers.

    python scripts/correct_sr44_little_blue_review_3.py [--dry-run]

Drawing evidence (INDOT B-44483, drawings.pdf; printed sheet numbers equal PDF page numbers). Plans are at
1/4 in = 1 ft (18 PDF points per foot); details and wing elevations at 1/2 in = 1 ft (36 points per foot). Values
not written as a dimension are scaled from the vectors and agree with the written dimensions to about 1 mm.

- Sheet 15 PLAN (Bent 1) and sheet 18 RAILING PLAN, Wings A and B; sheet 16 PLAN (Bent 2) and sheet 18, Wing C.
  Each wing is a 12'-0" x 1'-0" wall whose inner face is 1" outside the coping (the 1" PEJF of the Wing Typical
  Section, "Except Wing D"). The 12'-0" is measured on the outer face from the bent front face.
    Wing A (Bent 1 north) and Wing C (Bent 2 south): both bent faces run on at 45 degrees to the wing faces, so the
      bent end fills the corner. Sheet 18 vectors: Wing A outer face X -14.5029..-10.8453, inner face to -11.7360;
      Wing C outer face 10.8455..14.5031, inner face from 11.7605. Sheet 15/16 vectors give the same to 1 mm.
    Wing B (Bent 1 south): the bent end is square to the roadway. The front face turns square at the roadway face
      ("2'-7"" to the wing outer face) and the back face 6" further out ("1'-1"" to the wing inner face); the outer
      face is 8'-5 7/8" + 3'-6 1/8" = 12'-0". Sheet 18 vectors: Wing B X -1.5235..2.1341, back face square at 1.0656.
- Wing tops slope from the bent end (Section A-A / Section D-D) to the tip (wing elevations): Wing A 878.25 ->
  878.26, Wing B 878.10 -> 878.15, Wing C 877.91 -> 877.85; bottoms El. 870.97 (Bent 1) and 870.83 (Bent 2).
  Wing Typical Section (sheet 15): the wall is 1'-0" thick over its full height; the 4:1 slope behind it bounds the
  removable flowable backfill, not the concrete.
- Sheet 17 END BENT DETAIL (BETWEEN WINGWALLS), 1/2 in = 1 ft: bent 2'-10" wide; the bridge floor (1'-8") is cast
  on the bent and ends 9" from the back face ("9" Pavement Ledge"); the ledge top and the approach slab end are
  1'-2" below the top of deck. Scaled: the approach slab is 1'-2" deep from its end to 18" beyond the bent back
  face, then a 2" x 2" chamfer to the 12" slab. The 1'-2" zone in the sheet 15 / 16 wing elevations is 38.1" long
  along the skew (27" normal = 9" + 18"), which confirms the 18". Sheet 18's railing elevations draw 15", but they
  are schematic (the slab is drawn 18" deep, the bent at its 2'-10" normal width).
- Sheets 15 and 16 PLAN: the pavement-ledge line (9" from the back face) is the skewed slab end; at the rail-zone
  corners it ends square at the square slab ends, i.e. the ledge is the part of each bent not under the bridge
  floor (Bent 1: X -10.9552 north, 1.2364 south; Bent 2: X 10.9552 south, -1.3705 north from Y 6.2299).

- Guardrails. Sheet 11 profile legend: pay limits on Line "PR-PR" - Type OS end treatments 506+33.37-506+83.37 (Lt.),
  505+85.87-506+35.87 and 508+66.63-509+16.63 (Rt.); MGS Without Curb transitions to the railing at 506+83.37,
  507+23.37 and 508+66.63; 87.50 lft MGS W-beam (6'-3" spacing) 506+35.87-507+23.37 (Rt.); Type TGB 507+69.74-507+94.74
  and the Curved W-Beam Terminal, Type 1, 507+94.74-508+09.49 (Lt.). Revision notice 9710491 p. 5 confirms the pay
  items (601-12292 x 3, 601-94689 x 3, 601-01522, 601-01700, 601-12281 88 lft). Sheet 12 plan (1/8 in = 1 ft) and
  elevation: MGS transition posts 11.47 in beyond the TFC end, then 9 x 1'-6 3/4", 6 x 3'-1 1/2", 1 x 6'-3" (the 17th
  on the pay limit; sheet 18 draws the first three, 7'-0" long); TGB posts 11.47 in, 5 x 1'-6 3/4", 3 x 3'-1 1/2",
  1 x 6'-3" (sheet 11 agrees for the last two); W6 posts 4 x 6 in 12 in (MGS) / 7 in (TGB) behind the rail, 7'-0"
  long with 52 in below grade (sheet 18; the sheets 23-28 cross sections draw every post 7.01 ft long, sheet 3 a
  6'-0" post); TGB posts 1-8 level at 31.4 in above grade, 9-10 at 27.4 in (sheet 18); rail back
  6.272-6.276 m, rail depth 2.5 pt; thrie beam to 18.67 ft, thrie-W piece to 23.87 ft (MGS). Sheet 18 NE elevation:
  TGB thrie 10.27-30.27 in to 12.92 ft, W-beam 14.13-26.40 in from 18.13 ft. Sheets 11/12: the curved terminal runs
  straight to X 7.918 m, turns through a quarter circle of 8'-6" face radius and runs north to Y 16.57 m, on 6 x 8 in
  posts (6'-3" on the leg); its ground follows the drive cross fall of the sheet 26 section Sta. 508+11.44. Sheet 11
  plan: Type OS posts at 7 x 6'-3" then 5'-0". Sheet 3 typical section: rail face on the 20'-4" shoulder edge (2 %
  cross slope); its 8 x 14 in blockout and W-beam profile are undimensioned cells. Sheet 19 Section E-E dimensions
  the approach slab end: 1'-6" + 9" with a 2" step at 45 degrees. The sheet 11 profile also
  gives the grade beyond the vertical curve: +0.730 % west of the BVC, +0.006 % east of P.V.I. 508+50 (El. 878.13).

Model changes:
- RESOLVE wings-a-b-c-plan: Wings A, B and C rebuilt to the drawn outline and sloping tops.
- RESOLVE bent-pavement-ledge (with a DECIDE on the 18" thickened approach end): both bents get the 9" ledge at
  1'-2" below the top of deck wherever the approach slab, not the bridge floor, is above; Bent 1's south end is
  square as drawn; both approach slabs get the 1'-2" end over the ledge and 18" beyond the back face with the 2"
  chamfer, so they bear on the ledge.
- guardrail-representative-runs: the drawn layout is RESOLVED (DECIDE: TGB posts at the plan positions, which the
  sheet 18 elevation draws 6 in further out; 7'-0" posts per sheets 18 and 23-28, not the 6'-0" of sheet 3; MGS run
  87.50 ft per the stations, not the 88 lft pay quantity). The
  four representative runs become the four transitions, and five parts are added: the MGS W-beam run, three Type OS
  end treatments and the curved terminal (envelope sections). KEEP only the standard-drawing details.
Part ids of existing parts are unchanged; 5 parts are added (42 in all), none removed.

Requires numpy, trimesh, shapely and manifold3d, plus the two earlier correction scripts (constants and surface).
"""
import hashlib
import json
import struct
import sys
from pathlib import Path

import numpy as np
import trimesh
from shapely.geometry import LineString, MultiLineString, Polygon
from shapely.geometry.polygon import orient
from shapely.ops import split

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import correct_sr44_little_blue_review as first  # noqa: E402
import correct_sr44_little_blue_review_2 as second  # noqa: E402

BID = first.BID
BASE = ROOT / 'data/bridges' / BID
BACKUP = ROOT / 'data/fem_research'
TAG = 'drawing-review-3-wings-ledge-guardrails'
PREVIOUS_TAG = second.TAG
PREVIOUS_REVISION = second.REVISION
REVISION = '1.3-deviations'
FT, IN = first.FT, first.IN
COPING, FACE, SLAB, APPROACH_T = first.COPING, first.FACE, first.SLAB, first.APPROACH_T
SEC45 = 1 / np.cos(np.radians(45))
skew_x = first.skew_x
surface = first.surface

# Bent faces as u (= X + Y) values: 2'-10" normal width about C/L Bent at u = -/+15 ft (sheets 14, 17).
B1_BACK, B1_FRONT = -first.BENT_U - first.BENT_HALF, -first.BENT_U + first.BENT_HALF
B2_FRONT, B2_BACK = first.BENT_U - first.BENT_HALF, first.BENT_U + first.BENT_HALF
LEDGE_TOP = 14 * IN                      # sheet 17: ledge top and approach end 1'-2" below the top of deck
LEDGE_W = 9 * IN                         # sheet 17: "9" Pavement Ledge"
THICK_BEYOND, CHAMFER = 18 * IN, 2 * IN  # sheet 17, scaled; confirmed by the sheet 15/16 wing elevations
WING_IN = COPING + 1 * IN                # 1" PEJF between the coping and the wing (sheet 15 plan, typical section)
WING_OUT = WING_IN + 1 * FT
WING_L = 12 * FT
SW_BACK_Y = -(FACE + 6 * IN)             # sheet 15 Wing B: back face turns square 1'-1" from the wing inner face
WINGS = {
    'wing_1_1': dict(letter='A', bent=1, top=(878.25, 878.26), bottom=870.97, sheet=15,
                     section='Section A-A', pages=[15, 18]),
    'wing_1_-1': dict(letter='B', bent=1, top=(878.10, 878.15), bottom=870.97, sheet=15,
                      section='Section A-A', pages=[15, 18]),
    'wing_2_-1': dict(letter='C', bent=2, top=(877.91, 877.85), bottom=870.83, sheet=16,
                      section='Section D-D', pages=[16, 18]),
}
BOTTOM_EL = {1: 870.97, 2: 870.83}       # sheets 15, 16 (bent and wing bottoms, level)


def wing_plan(pid):
    """Plan outline beyond the coping (shared face with the bent end), x of the 12'-0" start and of the tip."""
    if pid == 'wing_1_1':                # Wing A: bent faces run on at 45 degrees to the wing faces
        start = skew_x(B1_FRONT, WING_OUT)
        tip = start - WING_L
        return [(tip, WING_IN), (skew_x(B1_BACK, WING_IN), WING_IN), (skew_x(B1_BACK, COPING), COPING),
                (skew_x(B1_FRONT, COPING), COPING), (start, WING_OUT), (tip, WING_OUT)], start, tip
    if pid == 'wing_2_-1':               # Wing C: the same, point-symmetric
        start = skew_x(B2_FRONT, -WING_OUT)
        tip = start + WING_L
        return [(tip, -WING_IN), (tip, -WING_OUT), (start, -WING_OUT), (skew_x(B2_FRONT, -COPING), -COPING),
                (skew_x(B2_BACK, -COPING), -COPING), (skew_x(B2_BACK, -WING_IN), -WING_IN)], start, tip
    xf, xb = skew_x(B1_FRONT, -FACE), skew_x(B1_BACK, SW_BACK_Y)   # Wing B: square bent end
    tip = xf - WING_L
    return [(tip, -WING_OUT), (xf, -WING_OUT), (xf, -COPING), (xb, -COPING), (xb, -WING_IN), (tip, -WING_IN)], xf, tip


def bent_plan(i):
    if i == 1:                           # south end square to the roadway (sheets 15, 18)
        xf, xb = skew_x(B1_FRONT, -FACE), skew_x(B1_BACK, SW_BACK_Y)
        return [(skew_x(B1_BACK, COPING), COPING), (skew_x(B1_FRONT, COPING), COPING), (xf, -FACE), (xf, -COPING),
                (xb, -COPING), (xb, SW_BACK_Y)]
    return first.parallelogram(B2_FRONT, B2_BACK, -COPING, COPING)


def approach_bottom(i):
    """Soffit: 12 in slab, 1'-2" from 18 in beyond the bent back face onto the ledge, 2 in chamfer between."""
    back, sign = (B1_BACK, -1) if i == 1 else (B2_BACK, 1)
    u14, u12 = back + sign * THICK_BEYOND * SEC45, back + sign * (THICK_BEYOND + CHAMFER) * SEC45

    def bottom(x, y):
        u = np.asarray(x, float) + np.asarray(y, float)
        t = np.clip((u - u12) / (u14 - u12), 0, 1)
        return surface(x, y) - APPROACH_T - (LEDGE_TOP - APPROACH_T) * t
    return bottom, (u14, u12)


# --- Guardrail runs (sheets 3, 11, 12, 18; revision notice 9710491 p. 5) --------------------------------------------
GR_BACK = second.FACE_Y                   # rail back on the TFC end-face plane, |Y| = 6.2738 m (sheet 12 plan 6.272-6.276)
GR_DEPTH = 2.5 * FT / 9                   # sheet 12 plan: rail face and back lines 2.5 pt apart at 9 pt/ft (0.0847 m)
QUARTER, HALF_SP, FULL_SP = 1.5625 * FT, 3.125 * FT, 6.25 * FT   # 1'-6 3/4", 3'-1 1/2", 6'-3" post spacings
FIRST_POST = 8.6 * FT / 9                 # first post 11.47 in beyond the TFC end (sheet 12 elevation; sheet 18 17.2 pt)
MGS_POSTS = ([FIRST_POST + QUARTER * k for k in range(10)] +            # sheet 12 plan/elevation, sheet 18 (3 posts)
             [FIRST_POST + 9 * QUARTER + HALF_SP * k for k in range(1, 7)])
MGS_POSTS.append(MGS_POSTS[-1] + FULL_SP)                                # 17th post on the transition pay limit
TGB_POSTS = ([FIRST_POST + QUARTER * k for k in range(6)] +             # sheet 12 plan (sheet 11 posts 9-10)
             [FIRST_POST + 5 * QUARTER + HALF_SP * k for k in range(1, 4)])
TGB_POSTS.append(TGB_POSTS[-1] + FULL_SP)                                # 10th post on the 507+94.74 pay limit
# Rail heights above the shoulder grade (in), distances from the TFC end (ft).
S12 = dict(tfc_end=534.5, thrie_end=366.5, w_start=319.7)                 # sheet 12 elevation, MGS W/O Curb, 9 pt/ft
S18 = dict(tfc_end=1076.0, thrie_end=1308.5, w_start=1402.3, w_top=802.8, w_bottom=821.2, deck=842.4)  # NE, 18 pt/ft
_mgs, _tgb = second.connection(1, -1), second.connection(1, 1)
RAIL = {'mgs': dict(thrie_end=(S12['tfc_end'] - S12['thrie_end']) / 9 * FT, w_start=(S12['tfc_end'] - S12['w_start']) / 9 * FT,
                    thrie=(_mgs['bottom'], _mgs['top']), w=(_mgs['top'] - 12 * IN, _mgs['top'])),
        'tgb': dict(thrie_end=(S18['thrie_end'] - S18['tfc_end']) / 18 * FT, w_start=(S18['w_start'] - S18['tfc_end']) / 18 * FT,
                    thrie=(_tgb['bottom'], _tgb['top']),
                    w=((S18['deck'] - S18['w_bottom']) / 1.5 * IN, (S18['deck'] - S18['w_top']) / 1.5 * IN))}
POST = {'mgs': dict(offset=(6.5634 - GR_BACK), depth=6 * IN, width=4 * IN),   # sheet 12 plan W6 post behind a 12 in block
        'tgb': dict(offset=(6.4550 - GR_BACK), depth=6 * IN, width=4 * IN),   # posts 1-8 behind 7 in blocks
        'tgb_w': dict(offset=(6.4753 - GR_BACK), depth=6 * IN, width=4 * IN),  # posts 9-10 behind 6 x 8 in blocks
        'crt': dict(offset=0.0, depth=8 * IN, width=6 * IN)}                   # curved terminal: 6 x 8 in posts, no block
ARC_X = (1052.8 - 819.0) / 9 * FT        # sheet 12 plan: start of the curved terminal arc (sheet 11: 7.912 m)
ARC_R = 8.5 * FT                         # face radius, sheet 11 (20.4 pt at 2.4 pt/ft) and sheet 12 (76.5 pt at 9 pt/ft)
ARC_C = (ARC_X, GR_BACK - GR_DEPTH + ARC_R)
LEG_END_Y = (385.2 - 254.7) / 2.4 * FT   # sheet 11: end of the terminal's north leg (anchor end)
# Sheet 26 cross section Sta. 508+11.44 (1 in = 5 ft, 14.4 pt/ft), Mod. Class II Drive and Grading north of the
# shoulder edge, the nearest section to the terminal (its north leg is at 508+09.49): finished-grade fall (ft) below
# the shoulder edge at the left offsets (ft), scaled from the section vectors.
DRIVE_1144 = ((20.42, 0.0), (21.42, -.0556), (22.92, -.125), (24.35, -.1806), (27.26, -.25), (28.91, -.2708),
              (31.09, -.3125), (34.09, -.375), (37.09, -.4236), (40.09, -.4653), (43.09, -.5), (46.09, -.5208),
              (49.09, -.5417), (52.17, -.5486), (55.26, -.5556))
SECTION_PAGES = {'guardrail_1_-1': [24], 'guardrail_end_1_-1': [23], 'guardrail_1_1': [25], 'guardrail_terminal_1_1': [26],
                 'guardrail_-1_-1': [24, 25], 'guardrail_run_-1_-1': [23, 24], 'guardrail_end_-1_-1': [23],
                 'guardrail_-1_1': [27], 'guardrail_end_-1_1': [28]}    # cross sections drawing each run's posts
EMBED = 52 * IN                          # posts 7'-0": 52 in below grade (sheet 18 dashed posts; sheets 23-28 sections)
TGB_POST_TOP = ((S18['deck'] - 795.3) / 1.5 * IN, (S18['deck'] - 801.3) / 1.5 * IN)   # sheet 18: posts 1-8 / 9
CRT_POSTS = [('line', ARC_X), ('arc', (9.577, 7.034)), ('arc', (10.324, 8.656)), ('leg', 10.687),
             ('leg', 10.687 + FULL_SP), ('leg', 10.687 + 2 * FULL_SP)]   # sheet 12 plan centres; sheet 11 6'-3" on the leg
OS_POSTS_FT = [6.25 * k for k in range(1, 8)] + [48.75]                  # sheet 11: 7 x 6'-3", then 5'-0" (1'-3" from end)
TFC_END = {(1, -1): first.CHAINS[1][0], (1, 1): first.CHAINS[1][3], (-1, -1): first.CHAINS[-1][0],
           (-1, 1): first.CHAINS[-1][3]}
CORNER = {(1, -1): 'north-west', (1, 1): 'north-east', (-1, -1): 'south-west', (-1, 1): 'south-east'}
# Pay limits on Line "PR-PR" (sheet 11 profile legend items 1-5).
GUARDRAILS = [
    # id, corner, kind, rail from / to (station, or 'lap'), posts
    ('guardrail_1_-1', (1, -1), 'mgs', 'lap', 50683.37, 'transition'),
    ('guardrail_end_1_-1', (1, -1), 'os', 50683.37, 50633.37, 'os'),
    ('guardrail_1_1', (1, 1), 'tgb', 'lap', 50794.74, 'transition'),
    ('guardrail_terminal_1_1', (1, 1), 'crt', 50794.74, None, 'crt'),
    ('guardrail_-1_-1', (-1, -1), 'mgs', 'lap', 50723.37, 'transition'),
    ('guardrail_run_-1_-1', (-1, -1), 'run', 50723.37, 50635.87, 'run'),
    ('guardrail_end_-1_-1', (-1, -1), 'os', 50635.87, 50585.87, 'os'),
    ('guardrail_-1_1', (-1, 1), 'mgs', 'lap', 50866.63, 'transition'),
    ('guardrail_end_-1_1', (-1, 1), 'os', 50866.63, 50916.63, 'os'),
]


def sta_x(sta):
    return (sta - first.STA0) * FT


def gr_grade_ft(x):
    """Sheet 11 profile over the guardrail limits: the corrected grade, the +0.730 % tangent west of the BVC at
    506+25, and +0.006 % east of P.V.I. 508+50 (El. 878.13)."""
    sta = first.STA0 + np.asarray(x, float) / FT
    e = np.where(sta < first.BVC, first.E_BVC - .0073 * (first.BVC - sta), first.pg_ft(x))
    e850 = first.E_EVC - .00622 * (50850 - first.EVC)
    return np.where(sta > 50850, e850 + .00006 * (sta - 50850), e)


def gr_ground(x):
    """Shoulder grade on the rail back plane (2 % cross slope to the 20'-4" shoulder edge, sheet 3)."""
    return float(first.z_el(gr_grade_ft(x))) - .02 * GR_BACK


def drive_ground(x, y):
    """Terminal ground: the shoulder grade at x plus the sheet 26 drive cross fall at the offset |y| (zero on the
    rail back plane, so the terminal joins the TGB transition without a step)."""
    off, ref = np.array(DRIVE_1144).T
    return gr_ground(x) + FT * (np.interp(abs(y) / FT, off, ref) - np.interp(GR_BACK / FT, off, ref))


def rail_heights(kind, d):
    """(bottom, top) above the grade at d metres from the TFC end: thrie beam, thrie-W transition piece, W-beam."""
    r = RAIL['tgb' if kind in ('tgb', 'crt') else 'mgs']
    t = np.clip((d - r['thrie_end']) / (r['w_start'] - r['thrie_end']), 0, 1)
    return tuple(a + (b - a) * t for a, b in zip(r['thrie'], r['w']))


def rail_loft(samples):
    """Closed rail element from sections (back x, back y, unit normal toward the traffic face, z bottom, z top)."""
    v = []
    for x, y, nx, ny, zb, zt in samples:
        fx, fy = x + nx * GR_DEPTH, y + ny * GR_DEPTH
        v += [(x, y, zb), (fx, fy, zb), (fx, fy, zt), (x, y, zt)]
    faces = []
    for k in range(len(samples) - 1):
        for j in range(4):
            a, b = 4 * k + j, 4 * k + (j + 1) % 4
            faces += [[a, b, b + 4], [a, b + 4, a + 4]]
    last = 4 * (len(samples) - 1)
    faces += [[0, 2, 1], [0, 3, 2], [last, last + 1, last + 2], [last, last + 2, last + 3]]
    m = trimesh.Trimesh(np.array(v), np.array(faces), process=False)
    if m.volume < 0:
        m.invert()
    if not m.is_watertight or not m.is_winding_consistent or m.volume <= 0:
        raise ValueError('invalid rail element')
    return m


def post_box(bx, by, tx, ty, nx, ny, spec, z0, z1, extra=0.0):
    """Post behind the rail: near face spec['offset'] (+extra) behind the rail back, across the normal (nx, ny)."""
    off = spec['offset'] + extra + spec['depth'] / 2
    cx, cy = bx - nx * off, by - ny * off
    T = np.eye(4)
    T[:3, 0], T[:3, 1], T[:3, 2], T[:3, 3] = (tx, ty, 0), (-ty, tx, 0), (0, 0, 1), (cx, cy, (z0 + z1) / 2)
    return trimesh.creation.box(extents=[spec['width'], spec['depth'], z1 - z0], transform=T)


def guardrail_part(entry):
    """Posts and rail element of one pay item, with the layout record."""
    pid, (side, end), kind, a, b, posts = entry
    xt = TFC_END[(side, end)]
    lap = second.connection(side, end)['lap']
    d_of = lambda x: end * (x - xt)  # noqa: E731
    members, post_d, post_xy = [], [], []
    if kind != 'crt':
        x0 = xt - end * lap if a == 'lap' else sta_x(a)
        x1 = sta_x(b)
        r = RAIL['tgb' if kind == 'tgb' else 'mgs']
        xs = first.stations(x0, x1, breaks=[xt + end * r['thrie_end'], xt + end * r['w_start']])
        by, n = side * GR_BACK, -side
        samples = []
        for x in xs:
            lo, hi = rail_heights(kind, d_of(x))
            g = gr_ground(x)
            samples.append((x, by, 0.0, n, g + lo, g + hi))
        members.append(rail_loft(samples))
        if posts == 'transition':
            ds = MGS_POSTS if kind == 'mgs' else TGB_POSTS
            pxs = [xt + end * d for d in ds]
        elif posts == 'run':
            pxs = [sta_x(a - FULL_SP / FT * k) for k in range(1, 15)]
        else:
            sgn = 1 if b > a else -1
            pxs = [sta_x(a + sgn * f) for f in OS_POSTS_FT]
        for k, x in enumerate(pxs):
            if kind == 'tgb':
                spec = POST['tgb'] if k < 8 else POST['tgb_w']
            else:
                spec = POST['mgs']
            g = gr_ground(x)
            if kind == 'tgb':                                # sheet 18 NE: posts 1-8 level at 31.4 in, then 27.4 in
                top = g + TGB_POST_TOP[0 if k < 8 else 1]
            else:                                            # sheets 12, 18: 1 in above the rail top (32 in)
                top = g + rail_heights(kind, d_of(x))[1] + IN
            bottom = g - EMBED                               # 7'-0" posts (sheets 18, 23-28)
            members.append(post_box(x, by, 1.0, 0.0, 0.0, n, spec, bottom, top))
            post_d.append(round(d_of(x), 4))
            post_xy.append([round(x, 4), round(by - n * (spec['offset'] + spec['depth'] / 2), 4)])
        extent = dict(rail_x_m=sorted([round(x0, 6), round(x1, 6)]))
    else:
        cx, cy = ARC_C
        rb = ARC_R - GR_DEPTH
        lo, hi = rail_heights('crt', 99.0)
        path = [(x, GR_BACK, 0.0, -1.0) for x in first.stations(sta_x(a), ARC_X)]
        for phi in np.radians(np.linspace(-90, 0, 31))[1:]:
            c, s = np.cos(phi), np.sin(phi)
            path.append((cx + rb * c, cy + rb * s, c, s))
        path += [(cx + rb, y, 1.0, 0.0) for y in first.stations(cy, LEG_END_Y)[1:]]
        samples = []
        for x, y, nx, ny in path:
            g = drive_ground(x, y)
            samples.append((x, y, nx, ny, g + lo, g + hi))
        members.append(rail_loft(samples))
        for where, val in CRT_POSTS:
            if where == 'line':
                bx, by, t, n, extra = val, GR_BACK, (1.0, 0.0), (0.0, -1.0), 0.0
            elif where == 'arc':
                phi = np.arctan2(val[1] - cy, val[0] - cx)
                c, s = np.cos(phi), np.sin(phi)
                bx, by, t, n, extra = cx + rb * c, cy + rb * s, (-s, c), (c, s), 0.002
            else:
                bx, by, t, n, extra = cx + rb, val, (0.0, 1.0), (1.0, 0.0), 0.0
            spec = POST['crt']
            off = spec['offset'] + extra + spec['depth'] / 2
            g = drive_ground(bx, by)                     # grade under the rail at the post
            members.append(post_box(bx, by, *t, *n, spec, g - EMBED, g + hi + IN, extra))
            post_xy.append([round(bx - n[0] * off, 4), round(by - n[1] * off, 4)])
        extent = dict(rail_x_m=[round(sta_x(a), 6), round(cx + rb + GR_DEPTH, 6)],
                      arc_start_x_m=round(ARC_X, 6), arc_face_radius_m=round(ARC_R, 6),
                      north_leg_end_y_m=round(LEG_END_Y, 6))
    m = trimesh.util.concatenate(members)
    if not m.is_watertight or not m.is_winding_consistent or m.volume <= 0:
        raise ValueError(f'{pid}: invalid guardrail solid')
    return m, dict(extent, post_count=len(post_xy), post_xy_m=post_xy, **({'post_d_from_tfc_m': post_d} if post_d else {}))


def _pieces(geom):
    return [g for g in getattr(geom, 'geoms', [geom]) if g.area > 1e-9]


def terrace(regions, bottom, step=.5, ylines=(0.0,), ulines=()):
    """Closed solid over plan regions [(polygon, top(x, y))] that share a bottom(x, y). Vertical faces close the
    outline and the steps between neighbouring regions; every vertex lies on its region's top or on the bottom."""
    polys = [orient(p if isinstance(p, Polygon) else Polygon(p), 1.0) for p, _ in regions]
    for p in polys:
        if not p.is_valid or p.area <= 0:
            raise ValueError('invalid plan region')
    x0 = min(p.bounds[0] for p in polys)
    y0 = min(p.bounds[1] for p in polys)
    x1 = max(p.bounds[2] for p in polys)
    y1 = max(p.bounds[3] for p in polys)
    cuts = []
    if step:
        cuts += [LineString([(x, y0 - 1), (x, y1 + 1)]) for x in np.arange(np.ceil(x0 / step) * step, x1, step)
                 if x0 + 1e-6 < x < x1 - 1e-6]
    cuts += [LineString([(x0 - 1, y), (x1 + 1, y)]) for y in ylines if y0 + 1e-6 < y < y1 - 1e-6]
    cuts += [LineString([(u - (y0 - 1), y0 - 1), (u - (y1 + 1), y1 + 1)]) for u in ulines]
    key, xy, tris = {}, [], []

    def vid(p):
        k = (round(float(p[0]), 7), round(float(p[1]), 7))
        if k not in key:
            key[k] = len(xy)
            xy.append(k)
        return key[k]

    for r, poly in enumerate(polys):
        for piece in (_pieces(split(poly, MultiLineString(cuts))) if cuts else [poly]):
            vv, ff = trimesh.creation.triangulate_polygon(orient(piece, 1.0), engine='manifold')
            for f in ff:
                ids = [vid(vv[i]) for i in f]
                if len(set(ids)) < 3:
                    continue
                a, b, c = (np.array(xy[i]) for i in ids)
                area = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
                if abs(area) < 1e-12:
                    continue
                tris.append((ids if area > 0 else ids[::-1], r))
    xy = np.array(xy)
    n = len(xy)
    z_bottom = np.asarray(bottom(xy[:, 0], xy[:, 1]), float) + 0 * xy[:, 0]
    vertices = [np.c_[xy, z_bottom]]
    at = [set() for _ in range(n)]
    for t, r in tris:
        for i in t:
            at[i].add(r)
    top_id, z_top, count = {}, {}, n
    for r, (_, top) in enumerate(regions):
        ids = [i for i in range(n) if r in at[i]]
        z = np.asarray(top(xy[ids, 0], xy[ids, 1]), float) + 0 * xy[ids, 0]
        if np.any(z - z_bottom[ids] <= 0):
            raise ValueError('non-positive depth')
        for i, zi in zip(ids, z):
            top_id[i, r], z_top[i, r] = count, float(zi)
            count += 1
        vertices.append(np.c_[xy[ids], z])
    faces = [[top_id[a, r], top_id[b, r], top_id[c, r]] for (a, b, c), r in tris]
    faces += [[c, b, a] for (a, b, c), _ in tris]
    edges = {}
    for t, r in tris:
        for a, b in zip(t, t[1:] + t[:1]):
            edges.setdefault(frozenset((a, b)), []).append((a, b, r))

    def chain(i, r):                     # vertical run at point i from the bottom to region r's top
        mid = sorted((z_top[i, s], top_id[i, s]) for s in at[i] if s != r and z_top[i, s] < z_top[i, r])
        return [i] + [v for _, v in mid] + [top_id[i, r]]

    zv = np.vstack(vertices)[:, 2]
    for uses in edges.values():
        if len(uses) == 1:               # outline: wall from the bottom to the region top, zipped up both sides
            a, b, r = uses[0]
            left, right = chain(a, r), chain(b, r)
            i = j = 0
            while i < len(left) - 1 or j < len(right) - 1:
                if j < len(right) - 1 and (i == len(left) - 1 or zv[right[j + 1]] - zv[right[0]]
                                           <= zv[left[i + 1]] - zv[left[0]]):
                    faces.append([left[i], right[j], right[j + 1]])
                    j += 1
                else:
                    faces.append([left[i], right[j], left[i + 1]])
                    i += 1
        elif len(uses) == 2 and uses[0][2] != uses[1][2]:     # step between two regions
            a, b, ra = uses[0]
            rb = uses[1][2]
            if min(abs(z_top[a, ra] - z_top[a, rb]), abs(z_top[b, ra] - z_top[b, rb])) < 1e-6:
                raise ValueError('flat step between regions')
            faces += [[top_id[b, ra], top_id[a, ra], top_id[a, rb]], [top_id[b, ra], top_id[a, rb], top_id[b, rb]]]
        elif len(uses) != 2:
            raise ValueError('non-manifold plan triangulation')
    solid = trimesh.Trimesh(np.vstack(vertices), np.array(faces), process=False)
    if not solid.is_watertight or not solid.is_winding_consistent or solid.volume <= 0:
        raise ValueError('terrace produced an invalid solid')
    return solid


def correct(dry_run=False):
    mp = BASE / 'model_manifest.json'
    raw = mp.read_bytes()
    raw_manifest = raw.decode('utf-8')
    newline = '\r\n' if '\r\n' in raw_manifest else '\n'
    final_newline = raw_manifest.endswith('\n')
    manifest = json.loads(raw_manifest)
    if manifest.get('review_correction_3') == TAG:
        print('Already corrected.')
        return
    path = BASE / 'model.glb'
    original = path.read_bytes()
    before = hashlib.sha256(original).hexdigest()

    def expect(ok, what):
        if not ok:
            raise ValueError(f'{BID}: unexpected starting model ({what})')

    expect(manifest.get('review_correction_2') == PREVIOUS_TAG and manifest.get('revision') == PREVIOUS_REVISION,
           'second review correction not applied')
    expect(before == manifest['review_correction_2_record']['after_glb_sha256'], 'GLB differs from the second correction')
    expect([d['id'] for d in manifest['known_deviations']] ==
           ['wings-a-b-c-plan', 'bent-pavement-ledge', 'guardrail-representative-runs'], 'known deviations')

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

    # --- Starting state: level-topped box wings, flat-ledge bents, 12 in approaches (revision 1.2). ---
    for pid, w in WINGS.items():
        m = native(pid)
        expect(len(m.vertices) == 8 and np.allclose(m.bounds, parts[pid]['bounds_m'], atol=2e-6), f'{pid} box')
        top = m.vertices[:, 2] > m.bounds[0, 2] + 1
        expect(np.ptp(m.vertices[top, 2]) < 1e-6 and abs(m.bounds[0, 2] - first.z_el(w['bottom'])) < 1e-5,
               f'{pid} level top and bottom')
        y = m.bounds[:, 1]
        expect(np.allclose(np.abs(y[::-1] if y[0] < 0 else y), [COPING, COPING + FT], atol=1e-5), f'{pid} at the coping')
    for i in (1, 2):
        m = native(f'integral_bent_{i}')
        v = m.vertices
        on_top = np.isclose(v[:, 2], surface(v[:, 0], v[:, 1]) - SLAB, atol=2e-5)
        expect(np.all(on_top | np.isclose(v[:, 2], first.z_el(BOTTOM_EL[i]), atol=1e-5)), f'integral_bent_{i} top')
        expect(np.allclose(m.bounds[:, :2], np.array(parts[f'integral_bent_{i}']['bounds_m'])[:, :2], atol=2e-6),
               f'integral_bent_{i} plan')
    for i in (1, 2):
        v = native(f'approach_{i}').vertices
        s = surface(v[:, 0], v[:, 1])
        expect(np.all(np.isclose(v[:, 2], s, atol=2e-5) | np.isclose(v[:, 2], s - APPROACH_T, atol=2e-5)),
               f'approach_{i} 12 in slab')
    for (side, end) in TFC_END:
        pid = f'guardrail_{side}_{end}'
        m = native(pid)
        expect(len(m.vertices) >= 40 and np.allclose(m.bounds, parts[pid]['bounds_m'], atol=2e-6) and
               abs(parts[pid]['dimensions'].get('lap_on_tfc_m', 0) - second.connection(side, end)['lap']) < 1e-6,
               f'{pid} representative run (revision 1.2)')
    expect(not any(e[0] in meshes for e in GUARDRAILS if e[0] not in parts), 'new guardrail ids already present')

    # --- New geometry. ---
    deck_plan = orient(Polygon(first.plans()[0]), 1.0)
    solids, records = {}, {}
    for pid, w in WINGS.items():
        plan, start, tip = wing_plan(pid)
        el0, el1 = w['top']
        top = (lambda x, y, s=start, t=tip, a=el0, b=el1:  # noqa: E731
               first.z_el(a + (b - a) * (np.asarray(x, float) - s) / (t - s)))
        solids[pid] = terrace([(plan, top)], lambda x, y, z=float(first.z_el(w['bottom'])): z + 0 * x, step=None,
                              ylines=())
        records[pid] = dict(plan_xy_m=[[round(a, 6), round(b, 6)] for a, b in plan],
                            outer_face_x_m=sorted([round(start, 6), round(tip, 6)]),
                            top_el_ft_bent_end_tip=[el0, el1], bottom_el_ft=w['bottom'])
    for i in (1, 2):
        bent = orient(Polygon(bent_plan(i)), 1.0)
        under_deck, ledge = bent.intersection(deck_plan), bent.difference(deck_plan)
        regions = [(p, lambda x, y: surface(x, y) - SLAB) for p in _pieces(under_deck)]
        regions += [(p, lambda x, y: surface(x, y) - LEDGE_TOP) for p in _pieces(ledge)]
        expect(abs(sum(p.area for p, _ in regions) - bent.area) < 1e-9, f'bent {i} regions')
        bottom = float(first.z_el(BOTTOM_EL[i]))
        solids[f'integral_bent_{i}'] = terrace(regions, lambda x, y, b=bottom: b + 0 * x)
        v = solids[f'integral_bent_{i}'].vertices
        soffit = v[np.isclose(v[:, 2], surface(v[:, 0], v[:, 1]) - SLAB, atol=1e-9), 2].max()
        records[f'integral_bent_{i}'] = dict(
            slab_soffit_max_z_m=round(float(soffit), 6), depth_bottom_to_slab_soffit_m=round(float(soffit - bottom), 6),
            plan_xy_m=[[round(a, 6), round(b, 6)] for a, b in bent_plan(i)],
            ledge_area_m2=round(sum(p.area for p in _pieces(ledge)), 6),
            ledge_top_below_deck_top_m=round(LEDGE_TOP, 6), slab_soffit_below_deck_top_m=round(SLAB, 6))
    approach_plans = first.plans()[1:]
    for i in (1, 2):
        bottom, ulines = approach_bottom(i)
        solids[f'approach_{i}'] = terrace([(approach_plans[i - 1], surface)], bottom, ulines=ulines)
        records[f'approach_{i}'] = dict(thickened_to_u_m=round(ulines[0], 6), chamfer_to_u_m=round(ulines[1], 6),
                                        end_depth_m=round(LEDGE_TOP, 6), slab_depth_m=round(APPROACH_T, 6))

    gr_records = {}
    for entry in GUARDRAILS:
        solids[entry[0]], gr_records[entry[0]] = guardrail_part(entry)
    records['guardrails'] = gr_records

    # --- Manifest text. ---
    el = lambda z: round(first.DATUM_EL + (float(z) - 3) / FT, 3)  # noqa: E731
    notes = {}
    for pid, w in WINGS.items():
        plan, start, tip = wing_plan(pid)
        corner = ('the bent end is square to the roadway: the front face turns square at the roadway face (2\'-7" '
                  'to the wing face) and the back face 6" further out (1\'-1" to the wing), so the outer face is '
                  '8\'-5 7/8" + 3\'-6 1/8"' if w['letter'] == 'B' else
                  'both bent faces run on at 45 degrees to the wing faces')
        notes[pid] = (
            f'Third review: Wing {w["letter"]} per the sheet {w["sheet"]} plan and the sheet 18 railing plan - a '
            f'12\'-0" x 1\'-0" wall with its inner face 1" outside the coping (1" PEJF), the 12\'-0" measured on the '
            f'outer face from the bent front face; {corner}. Top El. {w["top"][0]:.2f} at the bent end '
            f'({w["section"]}) to {w["top"][1]:.2f} at the tip (Wing {w["letter"]} elevation), bottom El. '
            f'{w["bottom"]:.2f}. Constant 1\'-0" thickness (Wing Typical Section; the 4:1 slope behind the wall '
            'bounds the removable flowable backfill, which is not modelled). The 1" PEJF is a gap.',
            dict(length_m=round(WING_L, 6), top_thickness_m=round(FT, 6),
                 inner_face_y_m=round(np.sign(plan[0][1]) * WING_IN, 6),
                 outer_face_y_m=round(np.sign(plan[0][1]) * WING_OUT, 6),
                 outer_face_x_m=sorted([round(start, 6), round(tip, 6)]),
                 top_el_at_bent_end_ft=w['top'][0], top_el_at_tip_ft=w['top'][1], bottom_el_ft=w['bottom']),
            w['pages'], f'Sheet {w["sheet"]} plan, {w["section"]}, Wing {w["letter"]} elevation and Wing Typical '
                        'Section; sheet 18 railing plan')
    ledge_ends = {1: 'X = -10.9553 at the north (sheet 15) and X = 1.2367 at the south (sheets 15, 18)',
                  2: 'X = 10.9553 at the south and X = -1.3700 from Y = 6.2294 at the north (sheet 16)'}
    for i in (1, 2):
        notes[f'integral_bent_{i}'] = (
            'Integral slab-to-bent connection; no discrete bearings. Third review (sheet 17 End Bent Detail): top on '
            'the crowned slab soffit (S - 1\'-8") under the bridge floor, and the 9" pavement ledge along the back '
            'face at 1\'-2" below the top of deck, carrying the approach slab end; the step is the slab end. At the '
            f'rail-zone corners the ledge ends square at the square slab ends, {ledge_ends[i]}. ' +
            ('South end square to the roadway as drawn (sheets 15 and 18): front face square from the roadway face, '
             'back face from 20\'-6" (Wing B). ' if i == 1 else 'Ends on the 45 degree bent faces (sheet 16). ') +
            'The 1 1/2" front-face fillet is not modelled.',
            dict(top='slab soffit (S - 20 in) under the bridge floor; ledge S - 14 in under the approach slab',
                 ledge_width_normal_m=round(LEDGE_W, 6), ledge_top_below_deck_top_m=round(LEDGE_TOP, 6),
                 slab_soffit_max_z_m=records[f'integral_bent_{i}']['slab_soffit_max_z_m'],
                 depth_bottom_to_slab_soffit_m=records[f'integral_bent_{i}']['depth_bottom_to_slab_soffit_m']) |
            (dict(south_end_square_x_m=[round(skew_x(B1_BACK, SW_BACK_Y), 6), round(skew_x(B1_FRONT, -FACE), 6)])
             if i == 1 else {}),
            [14, 15, 17, 18] if i == 1 else [14, 16, 17], None)
    for i, end in ((1, 'west'), (2, 'east')):
        p = parts[f'approach_{i}']
        notes[f'approach_{i}'] = (
            f'Review correction: outer end skewed 45 degrees, parallel to the bents, 20\'-6" beyond the {end} slab end '
            '(sheet 12 stations, sheet 11 paving exception); slab between the roadway faces, with the Type TFC '
            'extension under each TFC ending 2" beyond it (sheet 18). Third review: the end over the bent is 1\'-2" '
            'deep, on the 9" pavement ledge and 18" beyond the bent back face, with a 2" chamfer to the 12" slab '
            '(sheet 17 End Bent Detail; the wing elevations on sheets 15 and 16 show the same 1\'-2" zone). Terminal '
            'asphalt joints are not modelled.',
            dict(end_thickness_m=round(LEDGE_TOP, 6), thickened_beyond_bent_back_face_m=round(THICK_BEYOND, 6),
                 end_chamfer_m=round(CHAMFER, 6)),
            sorted(set(p['pdf_pages']) | {15, 16}), None)

    ft_in = lambda m: f"{int(m / FT + 1e-9)}'-{(m / FT - int(m / FT + 1e-9)) * 12:.2f}\""  # noqa: E731
    sta_txt = lambda sta: f'{int(sta // 100)}+{sta % 100:05.2f}'  # noqa: E731
    env = ('Envelopes: the rail element is a flat 0.085 m plate (the 2.5 pt rail depth of the sheet 12 plan) with its '
           'back on |Y| = 6.2738 m, heights measured from the shoulder grade on that plane (sheet 11 profile, 2 % '
           'cross slope of the sheet 3 typical section); posts are solid rectangles of the drawn W6 or timber size. ')
    std = ('Not modelled: the W-beam and thrie-beam corrugation shapes and the blockouts, which sheet 3 and the '
           'cross sections draw only as an undimensioned 8 x 14 in cell (against the 12 in MGS and 7 in TGB blocks of '
           'the sheet 12 plan), and the splices, bolts, post plates and connector hardware; they are defined by the '
           'INDOT Standard Drawings for pay item {item} ({title}), which the contract set does not include.')
    for pid, (side, end), kind, a, b, posts in GUARDRAILS:
        rec = gr_records[pid]
        corner = CORNER[(side, end)]
        if kind == 'mgs':
            r = RAIL['mgs']
            name = f'Guardrail transition, Type MGS Without Curb | {corner}'
            note = (f'Third review: Guardrail Transition, Type MGS Without Curb from the TFC end to the sheet 11 pay limit '
                    f'Sta. {sta_txt(b)} "PR-PR" (40.02 ft). 17 posts as drawn on the sheet 12 plan and elevation (sheet '
                    '18 for the first three): the first 11.47 in beyond the TFC end, then 9 at 1\'-6 3/4", 6 at '
                    '3\'-1 1/2" and 1 at 6\'-3", the last on the pay limit; W6 posts 4 x 6 in, 12 in behind the rail '
                    '(sheet 12 plan blockout), 7\'-0" long, 52 in below grade with the top 1 in above the rail '
                    '(sheets 12, 18, 23-28). Rail: thrie beam 11-31 in above grade lapping 2\'-6" onto the TFC, '
                    f'to {r["thrie_end"] / FT:.2f} ft from the TFC end; thrie-to-W transition piece to '
                    f'{r["w_start"] / FT:.2f} ft; W-beam 19-31 in beyond (sheet 12 elevation, sheet 18). ' + env +
                    std.format(item='601-12292', title='Guardrail Transition, MGS Without Curb'))
            dims = dict(pay_item='601-12292', pay_limit_station=sta_txt(b), length_from_tfc_end_m=round(40.02 * FT, 6),
                        post_count=rec['post_count'], post_spacings_ft='0.956, 9 x 1.5625, 6 x 3.125, 1 x 6.25',
                        thrie_beam_above_grade_m=[round(v, 6) for v in r['thrie']],
                        w_beam_above_grade_m=[round(v, 6) for v in r['w']],
                        thrie_end_from_tfc_m=round(r['thrie_end'], 6), w_beam_from_tfc_m=round(r['w_start'], 6),
                        lap_on_tfc_m=round(second.connection(side, end)['lap'], 6),
                        rail_element_depth_m=round(GR_DEPTH, 6), back_face_y_m=round(side * GR_BACK, 6))
            pages, basis = [3, 11, 12, 18], 'Sheet 11 pay limits; sheet 12 plan and elevation post layout; sheet 18'
        elif kind == 'tgb':
            r = RAIL['tgb']
            name = f'Guardrail transition, Type TGB | {corner}'
            note = (f'Third review: Guardrail Transition, Type TGB from the TFC end to the sheet 11 pay limit Sta. '
                    f'{sta_txt(b)} "PR-PR". 10 posts at the sheet 12 plan positions (sheet 11 agrees for the last two): '
                    'the first 11.47 in beyond the TFC end, then 5 at 1\'-6 3/4", 3 at 3\'-1 1/2" and 1 at 6\'-3" on '
                    'the pay limit; W6 posts 4 x 6 in behind 7 in blocks (6 x 8 in blocks at the last two); tops level '
                    'at 31.4 in above grade for posts 1-8 and 27.4 in for 9-10 (sheet 18); 52 in below grade, as the '
                    'sheets 25-26 cross sections draw the 7\'-0" posts here. Rail (sheet 18 north railing '
                    f'elevation): thrie beam {r["thrie"][0] / IN:.2f}-{r["thrie"][1] / IN:.2f} in above grade lapping '
                    f'2\'-0" onto the TFC, to {r["thrie_end"] / FT:.2f} ft; transition piece to {r["w_start"] / FT:.2f} '
                    f'ft; W-beam {r["w"][0] / IN:.2f}-{r["w"][1] / IN:.2f} in beyond. ' + env +
                    std.format(item='601-01522', title='Guardrail Transition, Type TGB'))
            dims = dict(pay_item='601-01522', pay_limit_station=sta_txt(b), post_count=rec['post_count'],
                        post_spacings_ft='0.956, 5 x 1.5625, 3 x 3.125, 1 x 6.25',
                        thrie_beam_above_grade_m=[round(v, 6) for v in r['thrie']],
                        w_beam_above_grade_m=[round(v, 6) for v in r['w']],
                        thrie_end_from_tfc_m=round(r['thrie_end'], 6), w_beam_from_tfc_m=round(r['w_start'], 6),
                        lap_on_tfc_m=round(second.connection(side, end)['lap'], 6),
                        rail_element_depth_m=round(GR_DEPTH, 6), back_face_y_m=round(side * GR_BACK, 6))
            pages, basis = [11, 12, 18], 'Sheets 11 and 12 plan post layout and pay limit; sheet 18 rail heights'
        elif kind == 'run':
            name = f'Guardrail, MGS W-beam, 6 ft 3 in spacing | {corner}'
            note = (f'Third review: Guardrail, MGS W-Beam, 6\'-3" Spa., Sta. {sta_txt(b)} to {sta_txt(a)} "PR-PR" '
                    '(87.50 ft, sheet 11; the revision 1 pay quantity is 88 lft). 14 W6 posts at 6\'-3" (sheet 11 '
                    'legend, sheet 12 plan), the last on the end-treatment pay limit, 12 in behind the rail, 7\'-0" '
                    'long, 52 in below grade with the top 1 in above the rail (sheets 18, 23, 24). W-beam 19-31 in above grade. ' + env +
                    std.format(item='601-12281', title='Guardrail, MGS W-Beam, 6 ft 3 in. Spacing'))
            dims = dict(pay_item='601-12281', station_limits=[sta_txt(b), sta_txt(a)], length_m=round(87.5 * FT, 6),
                        post_count=rec['post_count'], post_spacing_m=round(FULL_SP, 6),
                        w_beam_above_grade_m=[round(v, 6) for v in RAIL['mgs']['w']],
                        rail_element_depth_m=round(GR_DEPTH, 6), back_face_y_m=round(side * GR_BACK, 6))
            pages, basis = [3, 11, 12], 'Sheet 11 stations and legend; sheet 12 plan; sheet 3 typical section'
        elif kind == 'os':
            lo, hi = sorted([a, b])
            name = f'Guardrail end treatment, Type OS | {corner}'
            note = (f'Third review: Guardrail End Treatment, Type OS, Sta. {sta_txt(lo)} to {sta_txt(hi)} "PR-PR" (50 '
                    'ft, sheet 11), straight on the rail line. 8 W6 posts scaled from the sheet 11 plan: 7 at 6\'-3" '
                    'from the inner pay limit, then 5\'-0", 1\'-3" short of the end; 12 in behind the rail, 7\'-0" '
                    'long, 52 in below grade with the top 1 in above the rail (sheets 18, 23, 28). W-beam 19-31 in above grade to the end. The '
                    'impact head, anchor and cable at the end are not modelled. ' + env +
                    std.format(item='601-94689', title='Guardrail End Treatment, Type OS'))
            dims = dict(pay_item='601-94689', station_limits=[sta_txt(lo), sta_txt(hi)], length_m=round(50 * FT, 6),
                        post_count=rec['post_count'], post_offsets_from_inner_limit_ft=OS_POSTS_FT,
                        w_beam_above_grade_m=[round(v, 6) for v in RAIL['mgs']['w']],
                        rail_element_depth_m=round(GR_DEPTH, 6), back_face_y_m=round(side * GR_BACK, 6))
            pages, basis = [3, 11], 'Sheet 11 plan and pay limits; sheet 3 typical section'
        else:
            name = f'Curved W-beam guardrail terminal system, Type 1 | {corner}'
            note = (f'Third review: Curved W-Beam Guardrail Terminal System, Type 1 from Sta. {sta_txt(a)} "PR-PR" '
                    f'(sheet 11): straight to X = {ARC_X:.3f} m (sheet 12 plan), a quarter circle of 8\'-6" face '
                    f'radius (sheets 11, 12) and a north leg along the drive to Y = {LEG_END_Y:.2f} m (sheet 11, the '
                    'anchor end). 6 timber posts 6 x 8 in directly behind the rail at the sheet 12 plan positions (the '
                    'last two at 6\'-3" on the sheet 11 plan), the top 1 in above the rail and 52 in below grade, as the '
                    'sheet 26 section Sta. 508+00 draws the 7\'-0" post here. The grade follows the sheet 11 profile plus the drive cross fall of the sheet 26 '
                    'section Sta. 508+11.44 (Mod. Class II Drive and Grading, up to 0.55 ft below the shoulder edge on '
                    'the north leg). The terminal rail height is not drawn: the W-beam continues at the TGB height of '
                    'sheet 18. ' + env +
                    std.format(item='601-01700', title='Guardrail Terminal System, W-Beam, Curved, Type 1'))
            dims = dict(pay_item='601-01700', start_station=sta_txt(a), arc_start_x_m=round(ARC_X, 6),
                        arc_face_radius_m=round(ARC_R, 6), north_leg_end_y_m=round(LEG_END_Y, 6),
                        post_count=rec['post_count'], w_beam_above_grade_m=[round(v, 6) for v in RAIL['tgb']['w']],
                        rail_element_depth_m=round(GR_DEPTH, 6))
            pages, basis = [11, 12, 18], 'Sheet 11 and 12 plans (terminal layout and posts); sheet 18 rail height'
        if kind == 'tgb':
            dims.update(post_top_above_grade_m=[round(v, 6) for v in TGB_POST_TOP])
        elif kind == 'crt':
            dims.update(post_top_above_grade_m=round(RAIL['tgb']['w'][1] + IN, 6))
        else:
            dims.update(post_length_m=round(7 * FT, 6))
        dims.update(post_embedment_m=round(EMBED, 6))
        pages = sorted(set(pages) | set(SECTION_PAGES[pid]))
        notes[pid] = (note, dims, pages, basis, name)

    # --- GLB: replace only the changed primitives with appended accessors. ---
    changes, added = [], []
    gr_color = read(meshes['guardrail_1_1']['primitives'][0]['attributes']['COLOR_0'])[0]
    for pid, solid in solids.items():
        if pid not in parts:                         # new part: manifest entry, mesh and node in the scene
            template = parts['guardrail_1_1']
            parts[pid] = dict(id=pid, name='', layer=template['layer'], color=template['color'], pdf_pages=[],
                              basis='', note='', dimensions={}, bounds_m=[], volume_m3=0.0,
                              source_refs=[dict(source_id='9683606', pdf_pages=[])])
            manifest['parts'].append(parts[pid])
            meshes[pid] = dict(name=pid, extras={}, primitives=[dict(attributes={}, mode=4)])
            gltf['meshes'].append(meshes[pid])
            gltf['nodes'].append(dict(name=pid, mesh=len(gltf['meshes']) - 1))
            gltf['nodes'][0]['children'].append(len(gltf['nodes']) - 1)
            color = gr_color
            added.append(pid)
        else:
            color = read(meshes[pid]['primitives'][0]['attributes']['COLOR_0'])[0]
            changes.append(pid)
        prim = meshes[pid]['primitives'][0]
        v = np.asarray(solid.vertices, np.float64)
        glb = np.c_[v[:, 0], v[:, 2], -v[:, 1]].astype('<f4')
        prim['attributes'] = {'POSITION': append(glb, 'VEC3', 5126),
                              'COLOR_0': append(np.tile(color, (len(v), 1)).astype('u1'), 'VEC4', 5121)}
        gltf['accessors'][prim['attributes']['COLOR_0']]['normalized'] = True
        prim['indices'] = append(np.asarray(solid.faces).reshape(-1, 1).astype('<u4'), 'SCALAR', 5125)
        p = parts[pid]
        note, dims, pages, basis, *name = notes[pid]
        if name:
            p['name'] = name[0]
            p['dimensions'] = {}                     # guardrail dimensions are rewritten as a whole
        p['bounds_m'] = np.round(solid.bounds, 6).tolist()
        p['volume_m3'] = round(float(solid.volume), 9)
        p['note'] = note
        p['dimensions'].update(dims)
        if basis:
            p['basis'] = basis
        p['pdf_pages'] = pages
        for ref in p.get('source_refs', []):
            if ref.get('source_id') == '9683606':
                ref['pdf_pages'] = pages
        if name and not any(r.get('source_id') == '9710491' for r in p['source_refs']):
            p['source_refs'].append(dict(source_id='9710491', pdf_pages=[5]))
        if name:                                     # rebuilt guardrail: drop the stale primitive 'shape' key
            meshes[pid]['extras'] = dict(p)
        else:
            meshes[pid]['extras'].update(p)
    for pid in ('integral_bent_1', 'integral_bent_2'):
        parts[pid]['basis'] = ('Source 2 ft 10 in normal bent width and bottom elevation; top on the slab soffit and '
                               'the 9 in pavement ledge (sheet 17)')
        meshes[pid]['extras'].update(parts[pid])

    gltf['buffers'][0]['byteLength'] = len(binary)
    while len(binary) % 4:
        binary.append(0)
    encoded = json.dumps(gltf, ensure_ascii=True, separators=(',', ':')).encode()
    encoded += b' ' * ((-len(encoded)) % 4)
    out = (struct.pack('<III', 0x46546c67, 2, 28 + len(encoded) + len(binary)) +
           struct.pack('<II', len(encoded), 0x4e4f534a) + encoded + struct.pack('<II', len(binary), 0x004e4942) + binary)

    # --- Manifest: coverage, record, deviations, revision. ---
    gr_ids = [e[0] for e in GUARDRAILS]
    for c in manifest.get('detail_coverage', []):
        if c['feature'] == 'Unresolved geometry':
            c['detail'] = c['detail'].replace(
                'wing batter, pavement ledge details, ',
                'flowable backfill behind the wings and bents, the 1 1/2 in bent fillet, the 1 in PEJF, ').replace(
                'roadway terminals', 'guardrail hardware (standard drawings)')
        if c['feature'] == 'Rails and visible accessories':
            c['detail'] = c['detail'].replace(
                'representative guardrail attachment runs',
                'the guardrail runs to the sheet 11 limits (three MGS Without Curb transitions, the Type TGB '
                'transition, the 87.5 ft MGS W-beam run, three Type OS end treatments and the curved Type 1 '
                'terminal) with drawn post positions and envelope sections')
            c['part_ids'] += [pid for pid in gr_ids if pid not in c['part_ids']]
            c['sources'] = sorted(set(c['sources']) | {'Primary PDF p.3', 'Primary PDF p.11'}, key=lambda t: int(t.split('.')[-1]))
    decisions = [dict(
        id='bent-pavement-ledge', verdict='DECIDE', parts=['approach_1', 'approach_2'],
        decision='Approach slab end 1\'-2" deep from 18 in beyond the bent back face onto the 9 in ledge, 2 in '
                 'chamfer to the 12 in slab.',
        reasoning='Sheet 19 Section E-E dimensions it: 1\'-6" beyond the bent plus the 9 in ledge, with a 2 in step '
                  'at 45 degrees. Sheet 17 End Bent Detail (depths 1\'-0", 1\'-2", 1\'-8" dimensioned) scales the '
                  'same 18 in + 2 in, and the wing elevations on sheets 15 and 16 draw the 1\'-2" zone 38.1 in long '
                  'along the skew (27 in normal). Sheet 18 railing elevations scale 15 in but are schematic there: '
                  'they draw the slab 18 in deep against the dimensioned 1\'-8".',
        rejected_reading='Sheet 18 north/south railing elevations: 1\'-2" zone 15 in beyond the bent back face.',
        sources='sheet 19 Section E-E; sheet 17 End Bent Detail; sheets 15, 16 wing elevations; sheet 18'), dict(
        id='guardrail-representative-runs', verdict='DECIDE', parts=gr_ids,
        decision='Guardrail posts 7\'-0" long with 52 in below grade.',
        reasoning='Every cross section through the runs (sheets 23-28, Sta. 505+99 to 509+00) draws the post 7.01 '
                  'ft long with about 52.7 in below the ground, and the sheet 18 railing elevations draw the posts '
                  'next to the TFCs 7\'-0" long, 52 in below the deck line. Only the sheet 3 typical section draws a '
                  '6\'-0" post. Post tops follow sheets 12 and 18 (1 in above the rail; TGB posts 1-8 at 31.4 in and '
                  '9-10 at 27.4 in), so the TGB and terminal posts are up to 4.6 in shorter than 7 ft.',
        rejected_reading='Sheet 3 typical sections: 6\'-0" post, about 41 in below grade.',
        sources='sheets 23-28 cross sections; sheet 18 railing elevations; sheet 3'), dict(
        id='guardrail-representative-runs', verdict='DECIDE', parts=['guardrail_1_1'],
        decision='Type TGB posts at the sheet 12 plan positions: first post 11.47 in beyond the TFC end, 5 x '
                 '1\'-6 3/4", 3 x 3\'-1 1/2", 1 x 6\'-3" to the post on the 507+94.74 pay limit.',
        reasoning='The sheet 11 and sheet 12 plans agree (posts 9 and 10 at X 4.10/4.11 and 6.01/6.015 m), and the '
                  'last 6\'-3" bay lands on the sheet 11 pay limit 507+94.74 (X 6.017 m). The sheet 18 north railing '
                  'elevation and the sheet 12 elevation draw the same spacings but start 1\'-5 1/2" from the TFC '
                  'end, 6 in further out, which leaves a 5\'-9" last bay that matches neither plan.',
        rejected_reading='Sheet 18 north railing elevation (east): first TGB post 1\'-5 1/2" beyond the TFC end.',
        sources='sheet 11 plan and profile; sheet 12 plan; sheet 12 elevation; sheet 18 north railing elevation'), dict(
        id='guardrail-representative-runs', verdict='DECIDE', parts=['guardrail_run_-1_-1'],
        decision='MGS W-beam run 87.50 ft, 506+35.87 to 507+23.37.',
        reasoning='The sheet 11 stations and legend give 87.50 lft; the revision 1 schedule of pay items lists 88 lft '
                  '(601-12281), a quantity rounded for payment.',
        rejected_reading='Revision notice 9710491 p. 5: 88.000 lft.',
        sources='sheet 11 profile legend; revision notice 9710491 p. 5')]
    kept_deviation = dict(
        id='guardrail-representative-runs', parts=', '.join(gr_ids), source='sheets 3, 11, 12, 18 and 23-28',
        deviation='The guardrail runs follow the drawn layout (pay limits, post positions, spacing and 7 ft posts, '
                  'rail line, curved terminal path, thrie/W-beam heights, drive grade), but the rail is a flat '
                  '0.085 m plate instead of the W-beam and thrie-beam corrugations, the posts are solid '
                  'rectangles, and blockouts, splices, bolts, post plates, connector hardware, the Type OS impact '
                  'heads and the terminal anchor and cable are not modelled. The curved terminal keeps the TGB '
                  'rail height.',
        reason='The plans draw these items only as undimensioned schematic cells: the W-beam profile and an 8 x 14 '
               'in blockout in the sheet 3 typical section and the sheets 23-28 cross sections (the same cell at '
               'thrie-beam stations), which conflicts with the 12 in MGS and 7 in TGB blocks of the sheet 12 plan; '
               'sheet 11 shows the end heads and the anchor only as outlines; no sheet gives the terminal rail '
               'height. They are defined by the INDOT Standard Drawings and Standard Specifications Section 601 for '
               'the pay items 601-12292 Guardrail Transition, MGS Without Curb; 601-01522 Guardrail Transition, '
               'Type TGB; 601-12281 Guardrail, MGS W-Beam, 6 ft 3 in. Spacing; 601-94689 Guardrail End Treatment, '
               'Type OS; and 601-01700 Guardrail Terminal System, W-Beam, Curved, Type 1 (revision notice 9710491 '
               'p. 5), which the contract set neither includes nor cites by drawing number.')
    manifest['known_deviations'] = [kept_deviation]
    manifest['review_correction_3'] = TAG
    manifest['revision'] = REVISION
    manifest['review_correction_record_3'] = dict(
        source_pdf_pages=[3, 11, 12, 15, 16, 17, 18, 19, 23, 24, 25, 26, 27, 28],
        printed_sheets=[3, 11, 12, 15, 16, 17, 18, 19, 23, 24, 25, 26, 27, 28],
        secondary_sources={'9710491': [5]}, previous_revision=PREVIOUS_REVISION,
        resolved_deviations=['wings-a-b-c-plan', 'bent-pavement-ledge'],
        decided_deviations=['bent-pavement-ledge', 'guardrail-representative-runs'],
        partly_resolved_deviations=['guardrail-representative-runs'],
        kept_deviations=['guardrail-representative-runs'], decisions=decisions,
        findings={'wings-a-b-c-plan': 'resolved - Wings A, B, C to the sheet 15/16/18 outline (1 in outside the '
                                      'coping, 12 ft on the outer face from the bent front face; Bent 1 south end '
                                      'square) and the sloping drawn tops',
                  'bent-pavement-ledge': 'resolved - 9 in ledge at 1 ft 2 in below the top of deck under the '
                                         'approach slabs; approach ends 1 ft 2 in deep bearing on it',
                  'guardrail-representative-runs': 'layout resolved (sheet 11 pay limits, sheet 11/12 post layout, '
                                                   'sheet 12/18 rail and post heights, 7 ft posts per sheets 18 and '
                                                   '23-28, curved terminal path, sheet 26 drive grade); corrugations, '
                                                   'blockouts and hardware kept as envelopes'},
        geometry=records, changed_parts=changes, added_parts=added, removed_parts=[], part_count=len(manifest['parts']),
        before_glb_sha256=before, after_glb_sha256=hashlib.sha256(out).hexdigest(),
        before_manifest_sha256=hashlib.sha256(raw).hexdigest())
    record = manifest['review_correction_record_3']
    if dry_run:
        print(json.dumps({k: v for k, v in record.items() if k != 'geometry'}, indent=1))
        print('Dry run, nothing written.')
        return
    BACKUP.mkdir(exist_ok=True)
    (BACKUP / f'{BID}_before_review_correction_3.glb').write_bytes(original)
    (BACKUP / f'{BID}_manifest_before_review_correction_3.json').write_bytes(raw)
    path.write_bytes(out)
    text = json.dumps(manifest, ensure_ascii=False, indent=2)
    mp.write_bytes(text.replace('\n', newline).encode('utf-8') + (newline.encode() if final_newline else b''))
    print(json.dumps({k: v for k, v in record.items() if k not in ('geometry', 'decisions', 'findings')}, indent=1))


if __name__ == '__main__':
    correct(dry_run='--dry-run' in sys.argv)

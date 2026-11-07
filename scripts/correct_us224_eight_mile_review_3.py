"""Third correction of US 224 over Eight Mile Creek (us224-eight-mile): the known deviations left by revision 1.2.
Runs after scripts/correct_us224_eight_mile_review.py and _review_2.py and keeps the GLB buffers it does not replace.

    python scripts/correct_us224_eight_mile_review_3.py [--base DIR] [--backup DIR]

Primary set: INDOT B-44532 / Des 2200957 (drawings.pdf, document 9683628); printed sheet number = PDF page number.
Supplementary: 1985 plans B-16317 (sources/existing_plans_9548292.pdf), cited as "1985 sheet N" (its PDF page N).
Native axes (revision 1.2): X along increasing station (east), Y positive to the LEFT of increasing station (north),
Z up, Z = 0 at El. 817.00. Bearing lines X = u - tan(30 deg) Y; u = station offset along Line "A".

1. floor-end-over-mudwall (RESOLVE). Sheet 11 Section C-C (1" = 1'-0", cut normal to the abutment), sheet 10
   Section E-E and sheet 15: the deck ends at the Type PCF joint; between that joint and the Type I-A joint at the
   45 ft 0 1/2 in floor end (sheet 8: 2 ft 0 1/4 in beyond CL bearing on Line "A") is the 1 ft 0 in reconstructed
   mudwall, whose top is the bridge-deck overlay surface. Joint opening W = 2 in (Abut. 1) / 1 5/8 in (Abut. 2),
   sheet 11 note 3. Section C-C scales 21.0 in (normal) from CL bearing to the mudwall back face = 2 ft 0 1/4 in on
   Line "A", so the mudwall back face is the floor end. The model ran deck, overlay and copings to the floor end over
   a 1 ft (along u, 0.87 ft normal) mudwall with a flat top 111 mm below the crown and a 50 mm schematic joint strip
   centred on the floor end. Now: mudwalls 1 ft 0 in normal, from the floor end to the span face, crowned top on
   the finished surface; PCF strips fill the opening W, curb to curb (sheet 11 "PCF joint end at railing"); deck,
   overlay, copings and the retained rails end at the deck-side face of the joint. The mid-span drain cores are
   re-cut through the shortened deck and overlay exactly as in revision 1.2.

2. transition-railing-stations (RESOLVE). Sheet 12 railing elevations, sheet 10 removal plan, sheets 13-14:
   NW (SE similar): existing railing on the deck, the PCF joint opening, a new 5 ft 9 5/8 in Type FC railing on the
   existing wingwall (sheet 10: 5 ft 10 in from the existing open joint at the mudwall span face to the limit of
   wingwall removal), a 1/4 in open joint, then the 15 ft 8 in TFC on the RCBA extension. The TFC start is 4 ft 8 in
   from the slab's skew corner on the 22 ft 0 in edge (sheets 13-14, scaled), which agrees with the chain within
   1 mm (the model's 25 mm Type I-A joint gap aside). NE: the new 7 ft 10 5/8 in FC railing replaces the last part
   of the existing railing on the deck (sheet 10, 6 ft 9 in), crosses the PCF joint and the mudwall and ends at the
   1/4 in joint at the start of the TFC, which the model already has at the floor end (rev. 1.1 finding F4).
   FC section (sheet 12 Sections A-A, B-B, G-G, the same as TFC Section C-C): 1 ft 4 in base, back face vertical,
   9 in top at 2 ft 7 1/2 in above the finished surface, knee 11 in from the back at 9 1/2 in, toe vertical below
   2 1/2 in. The NW/SE TFCs and RCBA extensions move outward with square ends (sheets 13-14: the extension ends are
   square); the extensions run to the slab's far end (sheets 13-14). The retained rails end at the deck end;
   retained_rail_-1 ends at the NE saw cut.
   Decision: the NE removal is 6 ft 9 in on sheet 10 and the new railing 7 ft 10 5/8 in on sheet 12 = 6 ft 9 in +
   1 ft 0 in mudwall + 1 5/8 in joint measured normal to the joint; along the railing the mudwall and the joint
   measure 1 ft 3 3/4 in, and the 1/4 in open joint follows. The written railing length and the TFC start govern;
   the cut falls 6 ft 7 1/8 in from the deck end along the toe.

3. acute-corner-wings (RESOLVE). Wings A (NW, wing_0_-1) and D (SE, wing_1_1). 1985 sheet 7 Elevation F-F and End
   Elevation G-G, 1985 sheets 5-6 plan, sheet 10 removal plan and Sections A-A/B-B, sheet 12 Section A-A and the NW
   railing elevation, sheets 13-14:
   - root leg under the railing: 1 ft 3 in wall (sheet 10 Sections A-A, B-B) from 22 ft 1 in to 23 ft 4 in off
     Line "A" (back face on the railing line; 1 in preformed filler to the 22 ft 0 in RCBA edge, sheets 12 A-A,
     13-14), from the floor end, top level at El. 831.65 (A) / 831.47 (D) for 4 ft 10 3/4 in (F-F) to the kink;
   - main wing at 30 deg to the abutment (bisector of the 60 deg corner), front face 18 ft 11 3/4 in from the kink
     (F-F; sheet 10 traces the same 18.98 ft), top falling to El. 827.38 / 827.30 at the tip; 1 ft 0 in thick at the
     top, rear face battered to 1 ft 8 in at the base (G-G, "Batter Varies": constant base width under the sloping
     top), end square;
   - 2026 removal under the RCBA extension (sheet 10 limits of wingwall removal, Section B-B: 1 ft 0 1/2 in below
     the old railing base; sheet 12 NW elevation: 1 ft RCBA on 2 in polystyrene): wing top at the finished surface
     less 1 ft 2 in within the extension footprint, west of the new railing's end.
   The base stays at the model's Z = 0.05 m (the 1985 tip footing top is El. 817.03; the retained lower wall below
   El. 825.59 / 825.51 is not dimensioned).

4. obtuse-wing-roots (DECIDE). Wings B (SW, wing_0_1) and C (NE, wing_1_-1). 1985 sheet 5 (plan) starts the wing's
   front face at the coping corner on the abutment front face; 1985 sheet 5 Section A-A puts the front face 9 in
   span-side of CL bearing (cap 2 ft 6 in: 9 in + 9 in seat, 1 ft 0 in mudwall). The 2026 removal plan (sheet 10)
   traces the face from about the railing toe instead (1.2 ft inside the coping line), but sheet 10 is a reference
   tracing (general note 2: existing details are for reference only) whose transverse scale is about 1 % off; the
   1985 construction plan governs. 60 deg to the abutment, 11 ft 7 3/8 in, top El. 831.54 / 831.50 for 1 ft 1 3/8 in
   then falling to El. 826.58 / 826.50 (revision 1.1), 1 ft 0 in top, rear face battered to 1 ft 9 1/2 in at the
   base (End Elevation B-B). The wing begins at the coping line (under the deck corner the junction belongs to the
   abutment end) and is clipped to the model cap and stem, which stay centred on CL bearing.

5. Final pass after the independent check (check3):
   - PCF joint upturns: each PCF strip turns up at 45 deg 6 in over 6 in into the railing toe at both ends (sheet 11
     "Type PCF Bridge Expansion Joint End at Railing Detail"); the NE railing, continuous over the joint, is recessed.
   - NE corner square: TFC_transition_1_-1, extension_1_-1 and the NE FC railing end are square at the floor end on
     the 22 ft 0 in line (sheet 13 draws the extension's square end at the slab corner); approach_1's 4 in step is
     squared with the extension far end (sheet 13).
   - RCBA extensions: outer edge 2 in beyond the TFC back face (sheet 12 Sections C-C to F-F, written), |Y| = 7.1628.
   - Abutment outline, 1985 sheet 5 Section A-A: caps 9 in span-side / 1 ft 9 in behind CL bearing (rear face flush
     with the mudwall back face at the floor end); stems with a vertical front face 5 1/4 in span-side, 1 ft 6 1/4 in
     under the cap, rear face battered to 2 ft 2 3/4 in at the footing; footings 2 ft 7 in toe and 2 ft 2 1/4 in heel
     about the stem base. The acute wing roots now meet the cap rear face. FEM supports use CL bearing and the part
     Y/Z bounds, which do not change.
   - Bearing pads: turned 30 deg to lie along the bearing line (1985 sheet 9 Detail A); size and count stay.
   - Retained rails: re-swept to the existing barrier drawn on sheet 9, the FC section dimensioned on sheet 12 G-G,
     so the retained and new NE railing faces coincide at the saw cut.

   - Overlay dam (sheet 11 Section C-C): 1 ft 0 in from each deck end the overlay reaches 5 5/8 in below the finished
     surface (1 1/2 in grade raise, sheet 9; 2 1/2 in top cover, 1985 sheet 4 notes; #5 top bar, 1985 sheet 9; 1 in
     clear), returning at 45 deg to the milled surface; the deck is notched to match, curb to curb.
   - Footings 2 ft 0 in thick with tops at El. 817.03 / 816.95 (1985 sheet 5 A-A, sheet 7 B-B and G-G); the stems and
     all four wings stand on them (were Z = 0.05, footings 0.65 m thick).
   - Wings B and C: rear face batter 1:12 (1985 sheet 7 Section D-D; 1 ft 9 1/2 in at the tip as End Elevation B-B).

Kept (known_deviations): midspan-drain-overlay-taper (depth of "Taper Surface to Ex. Drain Edge" undetermined),
bearing-pad-plan (12 pads per abutment in pairs, 1985 sheets 5 and 9, but their size is on Standard PB11),
ne-corner-wingwall-root (existing wingwall behind the NE mudwall, not dimensioned).

Requires numpy, trimesh and manifold3d, plus scripts/correct_us224_eight_mile_review.py and _review_2.py (helpers).
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
import correct_us224_eight_mile_review as first  # noqa: E402
import correct_us224_eight_mile_review_2 as second  # noqa: E402

BID = first.BID
BASE = ROOT / 'data/bridges' / BID
BACKUP = ROOT / 'data/fem_research'
TAG = 'review-3-floor-end-mudwall-fc-railings-tfc-stations-wing-outlines'
PREVIOUS_REVISION = second.REVISION
REVISION = '1.3-deviations'
EXPECTED_BEFORE_SHA = 'f17de4574e3b36acd99294fe7814195c81d44c163aae8e492cb9d7fb02336d50'
EXPECTED_DEVIATIONS = {'acute-corner-wings', 'transition-railing-stations', 'floor-end-over-mudwall',
                       'obtuse-wing-roots', 'midspan-drain-overlay-taper'}

FT, IN, K = first.FT, first.IN, first.K
L2 = first.LENGTH / 2                      # 22 ft 6 1/4 in, CL bridge to the floor end (sheet 8)
W2 = first.WIDTH / 2                       # 23 ft 4 in, coping / railing back face (sheet 9)
TOE = 22 * FT                              # 22 ft 0 in, railing toe / RCBA edge (sheets 9, 13-14)
BRG = 20.5 * FT                            # CL bearing, 41 ft 0 in span (sheet 8)
COS = np.cos(np.radians(30))
REMAINING, OVERLAY, COPING_DROP = second.REMAINING, second.OVERLAY, 1.5 * IN
MUDWALL = 1 * FT / COS                     # 1 ft 0 in normal (sheet 11), along u
JOINT = {1: 2 * IN / COS, 2: 1.625 * IN / COS}   # PCF opening W normal (sheet 11 note 3), along u
U_M = {1: -L2 + MUDWALL, 2: L2 - MUDWALL}        # mudwall span face
U_D = {1: U_M[1] + JOINT[1], 2: U_M[2] - JOINT[2]}  # deck end = deck-side face of the PCF joint
PCF_DEPTH = .08                            # schematic depth, unchanged
NW_RAIL = (5 + 9.625 / 12) * FT            # sheet 12 NW/SE railing elevation
NE_RAIL = (7 + 10.625 / 12) * FT           # sheet 12 NE railing elevation
OPEN_JOINT = .25 * IN                      # sheet 12, 1/4 in open joint before the TFC
TFC_LEN = 188 * IN                         # 15 ft 8 in
FC = [(0, None), (16, None), (16, 2.5), (11, 9.5), (9, 31.5), (0, 31.5)]  # sheet 12 A-A/B-B/G-G (in; None = base)
RAIL_PROFILE = [(0, 0), (.4064, 0), (.4064, .1778), (.2286, 1.), (0, 1.)]  # retained rail (generator envelope)
RAIL_HEIGHT = 33 * IN
EXT_DEPTH = 1 * FT
WING_BOTTOM = .05                          # generator value (checked in the starting state only)
FOOTING_TOP = {1: (817.03 - 817) * FT, 2: (816.95 - 817) * FT}   # 1985 sheet 5 A-A, sheet 7 B-B, G-G: El. 817.03 / 816.95
FOOTING_T = 2 * FT                         # 2 ft 0 in footings (1985 sheet 5 A-A, sheet 7 B-B, G-G)
OBTUSE_BATTER = 1 / 12                     # 1985 sheet 7 Section D-D, rear face batter 1:12
DAM_RUN = 1 * FT                           # sheet 11 Section C-C overlay dam, 1 ft 0 in from the deck end, 45 deg return
DAM_DEPTH = (1.5 + 2.5 + .625 + 1.0) * IN  # surface to dam bottom: 1 1/2 in grade raise (sheet 9) + 2 1/2 in top cover
                                           # (1985 sheet 4 notes, sheet 9 A-A) + #5 top bar + 1 in clear (sheet 11)
MILLED = 2 * IN                            # milled deck surface below the finished surface (sheet 9)
WING_CUT = 14 * IN                         # RCBA 1 ft 0 in + 2 in polystyrene (sheet 10 B-B, sheet 12 elevation)
ROOT_FRONT = (22 + 1 / 12) * FT            # root leg traffic-side face (1 ft 3 in wall, back on the railing line)
ACUTE = {  # wing id: (abutment, side, level top El., tip El.)  1985 sheet 7 Elevation F-F
    'wing_0_-1': (1, 1, 831.65, 827.38), 'wing_1_1': (2, -1, 831.47, 827.30)}
OBTUSE = {  # 1985 sheet 7 Elevation C-C / End Elevation B-B (tops as revision 1.1)
    'wing_0_1': (1, -1, 831.54, 826.58), 'wing_1_-1': (2, 1, 831.50, 826.50)}
LEVEL_ACUTE, LEN_ACUTE = (4 + 10.75 / 12) * FT, (18 + 11.75 / 12) * FT
TOP_T, BASE_ACUTE, BASE_OBTUSE = 1 * FT, (1 + 8 / 12) * FT, (1 + 9.5 / 12) * FT
FRONT_FACE = .75 * FT / COS                # abutment front face 9 in span-side of CL bearing (1985 sheet 5 A-A)
DRAIN_R, SEGMENTS = second.DRAIN_R, second.SEGMENTS
EXT_OUT = W2 + 2 * IN                      # RCBA extension 2 in beyond the TFC back face (sheet 12 C-C to F-F)
UPTURN = 6 * IN                            # PCF joint end at railing: 6 in rise over 6 in (sheet 11 detail)
CAP_FRONT, CAP_REAR = 9 * IN, 21 * IN      # 1985 sheet 5 Section A-A: cap 9 in span-side, 1 ft 9 in behind CL brg
STEM_FRONT, STEM_REAR_TOP, STEM_REAR_BOT = 5.25 * IN, 13 * IN, 21.5 * IN   # 1985 A-A: 3 3/4 in / 8 in / 2 ft 2 3/4 in
FOOTING_SHIFT = 5.75 * IN                  # 1985 A-A footing 2 ft 7 in + 2 ft 2 3/4 in + 2 ft 2 1/4 in about the stem
PAD_ROTATION = np.radians(30)              # 1985 sheet 9 Detail A: pads parallel to the bearing line



def sx(u, y):
    """Revision 1.2 frame: X of the point at u on Line "A" moved along the skew to Y."""
    return u - K * np.asarray(y)


def surface(x, y):
    return first.surface(x, y)


def z_el(el):
    return (el - 817) * FT


def solid(m, what):
    raw = trimesh.Trimesh(np.asarray(m.vertices, float), np.asarray(m.faces), process=False)
    m = raw if raw.is_watertight else trimesh.Trimesh(raw.vertices, raw.faces, process=True)
    if m.volume < 0:
        m.invert()
    if not (m.is_watertight and m.is_winding_consistent and m.volume > 0):
        raise ValueError(f'invalid solid: {what}')
    return m


def slab(u0, u1, y0, y1, thick, offset=0., crown=True):
    """bridge_geometry.Model.slab in the revision 1.2 frame (crown vertex at Y = 0)."""
    yy = sorted(set([y0, y1] + ([0.] if crown and y0 < 0 < y1 else [])))
    profile = [(y, -thick) for y in yy] + [(y, 0.) for y in reversed(yy)]
    return first.sweep(profile, np.linspace(u0, u1, max(2, int((u1 - u0) / .6) + 1)),
                       lambda u, y, z: (float(sx(u, y)), y, float(surface(sx(u, y), y)) + offset + z))


def x_slab(x0, x1, y0, y1, thick):
    """Square-ended strip on one side of Line "A", top on the finished surface (RCBA extension)."""
    return first.sweep([(y0, -thick), (y1, -thick), (y1, 0.), (y0, 0.)],
                       np.linspace(x0, x1, max(2, int((x1 - x0) / .6) + 1)),
                       lambda x, y, z: (x, y, float(surface(x, y)) + z))


def ruled(profile, x0, x1, side, fn_z, n):
    """Sweep a railing profile (offset from the back face, code) between plan ends x0(y) and x1(y)."""
    def xyz(t, v, h):
        y = side * (W2 - v)
        x = (1 - t) * x0(y) + t * x1(y)
        return x, y, fn_z(x, y, h)
    return solid(first.sweep(profile, np.linspace(0, 1, n), xyz), 'ruled sweep')


def retained_rail(x0, x1, side):
    """Generator envelope (7 in toe, single slope) - only used to check the starting state."""
    n = max(3, int(abs(x1(side * W2) - x0(side * W2)) / .5))
    return ruled(RAIL_PROFILE, x0, x1, side,
                 lambda x, y, h: float(surface(x, y)) - COPING_DROP + (RAIL_HEIGHT if h == 1. else h), n)


def retained_fc(x0, x1, side):
    """Existing barrier as drawn on sheet 9 (same FC section as sheet 12 G-G), base on the coping."""
    return fc_railing(x0, x1, side, lambda x, y: float(surface(x, y)) - COPING_DROP)


def pcf_strip(u0, u1, depth):
    """PCF joint envelope curb to curb with the 6 in x 6 in upturn into the railing toe at each end (sheet 11)."""
    t, r, e = TOE, UPTURN, depth / 2
    profile = [(-t, -depth), (0., -depth), (t, -depth), (t + r + e, r - e), (t + r, r), (t, 0.), (0., 0.), (-t, 0.),
               (-t - r, r), (-t - r - e, r - e)]      # 45 deg legs, as thick (vertically) as the strip
    return first.sweep(profile, [u0, u1], lambda u, y, h: (
        float(sx(u, y)), y, float(surface(sx(u, y), y)) + h))


def shifted(mesh, dx):
    return trimesh.Trimesh(np.asarray(mesh.vertices) + [dx, 0., 0.], np.asarray(mesh.faces), process=False)


def battered_stem(u_brg, rear, y0, y1, z0, z1):
    """1985 sheet 5 Section A-A stem: front face vertical, rear face battered; skew section like Model.transverse."""
    prof = [(-STEM_FRONT, z0), (STEM_REAR_BOT, z0), (STEM_REAR_TOP, z1), (-STEM_FRONT, z1)]
    return first.sweep([(a / COS, z) for a, z in prof], [y0, y1],
                       lambda y, a, z: (float(sx(u_brg + rear * a, y)), y, z))


def rotated_pad(mesh):
    v = np.asarray(mesh.vertices, float)
    c = (v.min(axis=0) + v.max(axis=0)) / 2
    ca, sa = np.cos(PAD_ROTATION), np.sin(PAD_ROTATION)
    x, y = v[:, 0] - c[0], v[:, 1] - c[1]
    out = np.column_stack([c[0] + ca * x - sa * y, c[1] + sa * x + ca * y, v[:, 2]])
    return trimesh.Trimesh(out, np.asarray(mesh.faces), process=False)


def fc_railing(x0, x1, side, base):
    """Sheet 12 FC section; heights above the finished surface, bottom on base(x, y)."""
    profile = [(v * IN, -1. if h is None else h * IN) for v, h in FC]
    n = max(3, int(abs(x1(side * W2) - x0(side * W2)) / .3) + 1)
    return ruled(profile, x0, x1, side, lambda x, y, h: base(x, y) if h < 0 else float(surface(x, y)) + h, n)


def tfc(x_start, direction, side):
    """Sheet 12 TFC (second.section_at) with square ends, from x_start outward (direction = -1 west, +1 east)."""
    ts = np.unique(np.r_[np.linspace(0, 188, 9), [86, 97, 137]])
    xs = [x_start + direction * t * IN for t in ts]

    def xyz(x, a, b):
        y = side * (W2 - a)
        return x, y, float(surface(x, y)) + b
    return second.variable_sweep(xs, [second.section_at(t) for t in ts], xyz), ts


def mudwall(end, seat):
    u0, u1 = sorted([end * L2, U_M[1 if end < 0 else 2]])
    profile = [(-W2, 0.), (0., 0.), (W2, 0.), (W2, 1.), (0., 1.), (-W2, 1.)]
    return first.sweep(profile, [u0, u1], lambda u, y, h: (
        float(sx(u, y)), y, seat * (1 - h) + float(surface(sx(u, y), y)) * h))


def core_cutters():
    out = []
    for y in (22 * FT - .03, -(22 * FT - .03)):   # rev. 1.2 drain axes: mid-span, 30 mm inside the face of rail
        cx, cy = float(sx(0., y)), y
        poly = [tuple(p) for p in second.ring(cx, cy, DRAIN_R)]
        z = float(surface(cx, cy))
        out.append(first.sweep(poly, [z - OVERLAY - REMAINING - .1, z + .1], lambda zz, px, py: (px, py, zz)))
    return out


def prism(outline, z_top, z_bottom):
    """Vertical prism over a plan polygon, flat top."""
    return solid(first.sweep([tuple(map(float, p)) for p in outline], [0., 1.],
                             lambda h, px, py: (px, py, z_bottom + h * (z_top - z_bottom))), 'prism')


def battered_wall(origin, d, n, stations, z_top, base_t, z_bottom):
    """Wall with a vertical front face on origin + s d, top width TOP_T, rear face battered to base_t(s) at the base."""
    def xyz(s, v, h):
        b = v * (TOP_T if h else base_t(s))
        p = origin + s * d + b * n
        return float(p[0]), float(p[1]), z_top(s) if h else z_bottom
    return solid(first.sweep([(0., 0.), (1., 0.), (1., 1.), (0., 1.)], stations, xyz), 'wing wall')


def boolean(kind, meshes):
    f = trimesh.boolean.difference if kind == 'difference' else (
        trimesh.boolean.union if kind == 'union' else trimesh.boolean.intersection)
    return f(meshes, engine='manifold')


def overlap(a, b):
    if not (np.all(a.bounds[0] < b.bounds[1] - 1e-9) and np.all(b.bounds[0] < a.bounds[1] - 1e-9)):
        return 0.
    try:
        r = boolean('intersection', [a, b])
    except Exception:
        return 0.
    return float(abs(r.volume)) if len(r.faces) else 0.


def clip(mesh, neighbours, what):
    """Remove the parts of mesh that other solids already occupy (junction of a wing with the abutment end)."""
    hits = {k: n for k, n in neighbours.items() if overlap(mesh, n) > 1e-7}
    if hits:
        mesh = boolean('difference', [mesh] + list(hits.values()))
    return solid(mesh, what), sorted(hits)


def correct(base=BASE, backup=BACKUP):
    mp = base / 'model_manifest.json'
    raw_manifest = mp.read_bytes()
    manifest = json.loads(raw_manifest)
    if manifest.get('review_correction_3') == TAG:
        print('Already corrected.')
        return
    path = base / 'model.glb'
    original = path.read_bytes()
    before = hashlib.sha256(original).hexdigest()

    def expect(ok, what):
        if not ok:
            raise ValueError(f'{BID}: unexpected state ({what})')

    expect(manifest.get('drawing_review_correction_2') == second.TAG and manifest.get('revision') == PREVIOUS_REVISION,
           'revision 1.2 not applied')
    expect(before == EXPECTED_BEFORE_SHA == manifest['drawing_review_correction_2_record']['after_glb_sha256'],
           'GLB differs from revision 1.2')
    expect({d['id'] for d in manifest.get('known_deviations', [])} == EXPECTED_DEVIATIONS, 'known_deviations')
    length = struct.unpack_from('<I', original, 12)[0]
    gltf = json.loads(original[20:20 + length])
    binary = bytearray(original[28 + length:])
    parts = {p['id']: p for p in manifest['parts']}
    meshes = {m['name']: m for m in gltf['meshes']}
    expect(set(parts) == set(meshes) and len(meshes) == 91, 'part list')
    world = gltf['nodes'][0]
    expect(world.get('name') == 'world' and len(world['children']) == 91 and
           not any(k in nd for nd in gltf['nodes'] for k in ('matrix', 'rotation', 'translation', 'scale')),
           'scene nodes')

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
        if kind in ('VEC3', 'SCALAR'):
            a.update(min=array.min(axis=0).tolist(), max=array.max(axis=0).tolist())
        gltf['accessors'].append(a)
        return len(gltf['accessors']) - 1

    old = {}
    for pid, m in meshes.items():
        prim = m['primitives'][0]
        g = read(prim['attributes']['POSITION']).astype(np.float64)
        old[pid] = trimesh.Trimesh(np.column_stack([g[:, 0], -g[:, 2], g[:, 1]]), read(prim['indices']).reshape(-1, 3),
                                   process=False)

    # ---- Starting state: the generator/rev. 1.2 geometry this script replaces. ----
    def same(a, b, what, tol=2e-4):
        expect(first.same_vertices(a, np.asarray(b.vertices), tol), what)

    seats = {}
    for end, pid in ((-1, 'mudwall_1'), (1, 'mudwall_2')):
        v = old[pid].vertices
        seats[pid] = float(v[:, 2].min())
        expect(abs(v[:, 0].min() - (sx(-L2, W2) if end < 0 else sx(L2 - FT, W2))) < 2e-4 and
               abs(v[:, 0].max() - (sx(-L2 + FT, -W2) if end < 0 else sx(L2, -W2))) < 2e-4, f'{pid} extent')
    for side, pid in ((1, 'retained_coping_-1'), (-1, 'retained_coping_1')):
        y0, y1 = sorted([side * TOE, side * W2])
        same(slab(-L2, L2, y0, y1, .5 * IN, -COPING_DROP, crown=False), old[pid], pid)
    for side, pid in ((1, 'retained_rail_-1'), (-1, 'retained_rail_1')):
        same(retained_rail(lambda y: sx(-L2, y), lambda y: sx(L2, y), side), old[pid], pid)
    for end, pid in ((-1, 'PCF_joint_-1'), (1, 'PCF_joint_1')):
        same(slab(end * L2 - .025, end * L2 + .025, -W2, W2, PCF_DEPTH), old[pid], pid)
    for end, side, pid in ((-1, 1, 'extension_-1_-1'), (1, -1, 'extension_1_1'), (1, 1, 'extension_1_-1')):
        a, b = sorted([end * L2, end * (L2 + first.TFC_LEN)])
        y0, y1 = sorted([side * TOE, side * W2])
        same(slab(a, b, y0, y1, FT, crown=False), old[pid], pid)
    for pid in ('deck', 'overlay'):
        lo, hi = old[pid].bounds
        expect(abs(hi[0] - sx(L2, -(W2 if pid == 'deck' else TOE))) < 2e-4, f'{pid} extent')
    for pid in ('TFC_transition_-1_-1', 'TFC_transition_1_1', 'TFC_transition_1_-1', 'wing_0_-1', 'wing_1_1',
                'wing_0_1', 'wing_1_-1'):
        expect(abs(old[pid].volume - parts[pid]['volume_m3']) < 1e-5, f'{pid} volume')
    for ab in (1, 2):                                    # generator transverse(): centred on CL bearing
        u_brg = (-1 if ab == 1 else 1) * BRG
        for pid, half in ((f'cap_{ab}', 1.25 * FT), (f'stem_{ab}', .35), (f'footing_{ab}', 3.5 * FT)):
            v = old[pid].vertices
            uu = v[:, 0] + K * v[:, 1]
            expect(abs(uu.min() - (u_brg - half / COS)) < 2e-4 and abs(uu.max() - (u_brg + half / COS)) < 2e-4,
                   f'{pid} centred on CL bearing')
        for j in range(1, 7):
            lo, hi = old[f'B{ab}_bearing_{j}'].bounds
            expect(abs(hi[0] - lo[0] - .23) < 1e-4 and abs(hi[1] - lo[1] - 1.05) < 1e-4, f'B{ab}_bearing_{j} axis-aligned')

    new, info = {}, {}
    # ---- 1. Floor end: deck, overlay, copings to the PCF joint; mudwalls; PCF strips. ----
    cutters = core_cutters()
    area = .5 * SEGMENTS * DRAIN_R ** 2 * np.sin(2 * np.pi / SEGMENTS)
    # Overlay dam (sheet 11 Section C-C): the overlay deepens to DAM_DEPTH over 1 ft 0 in from each deck end, then
    # returns at 45 deg to the milled surface; profile in (u, height above the finished surface), swept curb to curb.
    a_, b_ = U_D[1], U_D[2]
    r1, r2 = DAM_RUN / COS, (DAM_RUN + DAM_DEPTH - MILLED) / COS
    mid = list(np.linspace(a_ + r2, b_ - r2, max(2, int((b_ - a_ - 2 * r2) / .6) + 1)))
    top = list(np.linspace(a_, b_, max(2, int((b_ - a_) / .6) + 1)))
    dam_overlay = ([(a_, -DAM_DEPTH), (a_ + r1, -DAM_DEPTH)] + [(u, -MILLED) for u in mid] +
                   [(b_ - r1, -DAM_DEPTH), (b_, -DAM_DEPTH)] + [(u, 0.) for u in reversed(top)])

    def across(profile, y0, y1):
        # stations every <= 0.6 m like Model.slab (manifold cuts of long slender faces lose accuracy)
        ys = sorted(set(np.r_[np.linspace(y0, y1, max(2, int((y1 - y0) / .6) + 1)), 0.].round(9)))
        return first.sweep(profile, ys, lambda y, u, h: (float(sx(u, y)), y, float(surface(sx(u, y), y)) + h))
    overlay_full = solid(across(dam_overlay, -TOE, TOE), 'overlay')
    deck_cut = []
    for a0, sgn in ((a_, 1), (b_, -1)):                       # deck notch = the dam, run past the joint and the top
        deck_cut.append(across([(a0 - sgn * .05, -DAM_DEPTH), (a0 + sgn * r1, -DAM_DEPTH),
                                (a0 + sgn * (DAM_RUN + DAM_DEPTH + .05) / COS, .05), (a0 - sgn * .05, .05)],
                               -TOE, TOE))
    deck_full = solid(slab(U_D[1], U_D[2], -W2, W2, REMAINING, -OVERLAY), 'deck')
    deck_dam = solid(boolean('difference', [deck_full] + deck_cut), 'deck')
    dam_volume = deck_full.volume - deck_dam.volume
    plain_overlay = 2 * TOE * (U_D[2] - U_D[1]) * OVERLAY
    expect(abs((overlay_full.volume - plain_overlay) - dam_volume) < 1e-4, 'overlay dam volume balance')
    for pid, full, thick in (('deck', deck_dam, REMAINING), ('overlay', overlay_full, OVERLAY)):
        cut = solid(boolean('difference', [full] + cutters), pid)
        removed = full.volume - cut.volume
        expect(abs(removed - 2 * area * thick) < 2e-6, f'{pid} drain cores ({removed:.7f} vs {2 * area * thick:.7f})')
        new[pid] = cut
        info[pid] = dict(end_u_m=[round(U_D[1], 6), round(U_D[2], 6)], drain_core_volume_m3=round(removed, 7))
    info['overlay']['dam'] = dict(depth_below_surface_m=round(DAM_DEPTH, 6), run_normal_m=DAM_RUN,
                                  volume_both_ends_m3=round(dam_volume, 6))
    for side, pid in ((1, 'retained_coping_-1'), (-1, 'retained_coping_1')):
        y0, y1 = sorted([side * TOE, side * W2])
        new[pid] = solid(slab(U_D[1], U_D[2], y0, y1, .5 * IN, -COPING_DROP, crown=False), pid)
    for end, ab, pid in ((-1, 1, 'mudwall_1'), (1, 2, 'mudwall_2')):
        new[pid] = solid(mudwall(end, seats[pid]), pid)
    for end, ab, pid in ((-1, 1, 'PCF_joint_-1'), (1, 2, 'PCF_joint_1')):
        u0, u1 = sorted([U_M[ab], U_D[ab]])
        new[pid] = solid(pcf_strip(u0, u1, PCF_DEPTH), pid)
        info[pid] = dict(u_m=[round(u0, 6), round(u1, 6)], opening_normal_in=2.0 if ab == 1 else 1.625)

    # ---- 1b. Abutment outline (1985 sheet 5 Section A-A) and pad orientation (1985 sheet 9 Detail A). ----
    for ab in (1, 2):
        rear = -1 if ab == 1 else 1                          # away from the span
        u_brg = rear * BRG
        cap_shift = rear * ((CAP_REAR - CAP_FRONT) / 2) / COS
        new[f'cap_{ab}'] = solid(shifted(old[f'cap_{ab}'], cap_shift), f'cap_{ab}')
        ft = shifted(old[f'footing_{ab}'], rear * FOOTING_SHIFT / COS)
        zv = ft.vertices[:, 2]
        expect(np.allclose(np.sort(np.unique(zv.round(6))), [-.6, .05]), f'footing_{ab} levels')
        ft.vertices[:, 2] = np.where(zv > 0, FOOTING_TOP[ab], FOOTING_TOP[ab] - FOOTING_T)
        new[f'footing_{ab}'] = solid(ft, f'footing_{ab}')
        (x0, y0, z0), (x1, y1, z1) = old[f'stem_{ab}'].bounds
        new[f'stem_{ab}'] = solid(battered_stem(u_brg, rear, y0, y1, FOOTING_TOP[ab], z1), f'stem_{ab}')
        info[f'cap_{ab}'] = dict(u_m=[r for r in sorted([round(u_brg - rear * CAP_FRONT / COS, 6),
                                                        round(u_brg + rear * CAP_REAR / COS, 6)])])
        for j in range(1, 7):
            new[f'B{ab}_bearing_{j}'] = solid(rotated_pad(old[f'B{ab}_bearing_{j}']), f'B{ab}_bearing_{j}')

    # ---- 2. Railings and transition stations (sheet 12; sheets 10, 13, 14). ----
    x_ne = float(sx(L2, TOE))                                 # NE TFC / extension start, square (sheet 13)
    x_cut = x_ne - OPEN_JOINT - NE_RAIL                       # NE saw cut of the retained north rail (square)
    new['retained_rail_-1'] = retained_fc(lambda y: sx(U_D[1], y), lambda y: x_cut, 1)
    new['retained_rail_1'] = retained_fc(lambda y: sx(U_D[1], y), lambda y: sx(U_D[2], y), -1)
    approach_far = {-1: float(old['approach_-1'].vertices[:, 0].min()), 1: float(old['approach_1'].vertices[:, 0].max())}
    expect(abs(approach_far[-1] - (sx(-L2 - .025, TOE) - 20.5 * FT)) < 2e-4 and
           abs(approach_far[1] - (sx(L2 + .025, -TOE) + 20.5 * FT)) < 2e-4, 'approach far ends')
    added = {}
    stations = {}
    for end, side, ab, rid, tid, eid, el in ((-1, 1, 1, 'FC_railing_-1_-1', 'TFC_transition_-1_-1', 'extension_-1_-1', 831.65),
                                             (1, -1, 2, 'FC_railing_1_1', 'TFC_transition_1_1', 'extension_1_1', 831.47)):
        x_face_toe = float(sx(U_M[ab], side * TOE))          # mudwall span face at the toe line
        x_end = x_face_toe + end * NW_RAIL                    # square outer end of the new railing
        x_tfc = x_end + end * OPEN_JOINT
        zb = z_el(el)
        raw = fc_railing(lambda y: sx(U_M[ab], y), lambda y: x_end, side, lambda x, y: zb)
        added[rid] = raw
        stations[rid] = dict(x_mudwall_face_toe=x_face_toe, x_outer=x_end, base_z=zb, el=el)
        new[tid], ts = tfc(x_tfc, end, side)
        stations[tid] = dict(x_start=x_tfc, x_end=x_tfc + end * TFC_LEN)
        x0, x1 = sorted([x_tfc, approach_far[end]])
        y0, y1 = sorted([side * TOE, side * EXT_OUT])
        new[eid] = solid(x_slab(x0, x1, y0, y1, EXT_DEPTH), eid)
        stations[eid] = dict(x=[x0, x1])
    new['TFC_transition_1_-1'], _ = tfc(x_ne, 1, 1)
    stations['TFC_transition_1_-1'] = dict(x_start=x_ne, x_end=x_ne + TFC_LEN)
    new['extension_1_-1'] = solid(x_slab(x_ne, x_ne + first.TFC_LEN, TOE, EXT_OUT, EXT_DEPTH), 'extension_1_-1')
    stations['extension_1_-1'] = dict(x=[x_ne, x_ne + first.TFC_LEN])
    # Sheet 13: the 4 in step of the east slab edge (22 ft 0 in under the NE extension, 22 ft 4 in beyond) is square
    # with the extension's far end; rev. 1.1 started the 22 ft 4 in strip on the old skewed extension end.
    a1 = solid(boolean('difference', [old['approach_1'], new['extension_1_-1']]), 'approach_1')
    info['approach_1'] = dict(step_trimmed_m3=round(float(old['approach_1'].volume - a1.volume), 7))
    expect(0 < info['approach_1']['step_trimmed_m3'] < .002, 'approach_1 step trim')
    new['approach_1'] = a1
    ne_east = lambda y: x_ne - OPEN_JOINT                     # noqa: E731  square, 1/4 in before the NE TFC
    added['FC_railing_1_-1'] = fc_railing(lambda y: x_cut, ne_east, 1,
                                          lambda x, y: float(surface(x, y)) - COPING_DROP)
    stations['FC_railing_1_-1'] = dict(x_west=x_cut, x_east=float(ne_east(TOE)))
    # Seat the new railings: notch them over the reconstructed mudwalls (top on the finished surface, sheet 12 B-B);
    # the NE railing, continuous over the joint, takes the PCF upturn recess (sheet 11 detail).
    for rid, mw in (('FC_railing_-1_-1', 'mudwall_1'), ('FC_railing_1_1', 'mudwall_2')):
        added[rid] = solid(boolean('difference', [added[rid], new[mw]]), rid)
    t, r, e = TOE, UPTURN, PCF_DEPTH / 2                      # the PCF upturn leg, run 2 cm into the roadway and
    leg = [(t - .02, -2 * e - .02), (t + r + e, r - e), (t + r, r), (t - .02, -.02)]   # 3 mm past the joint face
    recess = first.sweep(leg, [U_D[2], U_M[2] + .003], lambda u, y, h: (
        float(sx(u, y)), y, float(surface(sx(u, y), y)) + h))
    added['FC_railing_1_-1'] = solid(boolean('difference', [added['FC_railing_1_-1'],
                                                            boolean('union', [new['mudwall_2'], recess])]),
                                     'FC_railing_1_-1')

    # ---- 3. Acute-corner wings A and D: root leg + main wing, 2026 removal under the extension. ----
    final_others = {**old, **new, **added}
    wing_records = {}
    for pid, (ab, side, el_top, el_tip) in ACUTE.items():
        end = -1 if ab == 1 else 1
        y_b, y_f = side * W2, side * ROOT_FRONT
        x_fe = lambda y: float(sx(end * L2, y))               # noqa: E731  floor end (mudwall back face)
        k1 = np.array([x_fe(y_b) + end * LEVEL_ACUTE, y_b])   # kink on the outer face
        d = np.array([end * COS, side * .5])                  # 30 deg to the abutment, away from the bridge
        n = np.array([-side * .5, end * COS])                 # towards the fill
        s_cross = (y_f - (k1[1] + TOP_T * n[1])) / d[1]       # rear top line meets the root leg's inner face
        k2 = k1 + TOP_T * n + s_cross * d
        z_top, z_tip = z_el(el_top), z_el(el_tip)
        root = prism([(x_fe(y_f), y_f), (x_fe(y_b), y_b), tuple(k1), tuple(k2)], z_top, FOOTING_TOP[ab])
        main = battered_wall(k1, d, n, [s_cross, 0., LEN_ACUTE],
                             lambda s: z_top if s <= 0 else z_top + (z_tip - z_top) * s / LEN_ACUTE,
                             lambda s: BASE_ACUTE, FOOTING_TOP[ab])
        wing = solid(boolean('union', [root, main]), pid)
        # 2026 removal: within the RCBA extension footprint, west/east of the new railing's outer end.
        x_step = stations['FC_railing_-1_-1' if ab == 1 else 'FC_railing_1_1']['x_outer']
        xa, xb = sorted([x_step, x_step + end * 8.])
        ya, yb = sorted([side * (TOE - .05), side * EXT_OUT])
        cutter = first.sweep([(ya, 0.), (yb, 0.), (yb, 1.), (ya, 1.)], np.linspace(xa, xb, 15),
                             lambda x, y, h: (x, y, float(surface(x, y)) - WING_CUT if h == 0 else 12.))
        before_cut = wing.volume
        wing = solid(boolean('difference', [wing, cutter]), pid)
        removed_cut = before_cut - wing.volume
        wing, hits = clip(wing, {k: m for k, m in final_others.items() if not k.startswith('wing_')}, pid)
        new[pid] = wing
        tip = k1 + LEN_ACUTE * d
        wing_records[pid] = dict(kink_xy_m=np.round(k1, 4).tolist(), tip_xy_m=np.round(tip, 4).tolist(),
                                 removed_under_extension_m3=round(removed_cut, 4), clipped_by=hits)

    # ---- 4. Obtuse-corner wings B and C: root at the coping corner on the abutment front face. ----
    for pid, (ab, side, el_top, el_tip) in OBTUSE.items():
        end = -1 if ab == 1 else 1
        u_front = end * (BRG - FRONT_FACE)
        p = np.array([float(sx(u_front, side * W2)), side * W2])
        d = np.array([end * .5, side * COS])                  # 60 deg to the abutment, bisector of the 120 deg corner
        n = np.array([end * COS, -side * .5])                 # towards the fill
        z_top, z_tip = z_el(el_top), z_el(el_tip)
        lvl, ln = first.WING_LEVEL, first.WING_LEN
        top_at = lambda s: z_top if s <= lvl else z_top + (z_tip - z_top) * (s - lvl) / (ln - lvl)  # noqa: E731
        wing = battered_wall(p, d, n, [-.02, 0., lvl, ln], top_at,
                             lambda s: TOP_T + (top_at(s) - FOOTING_TOP[ab]) * OBTUSE_BATTER, FOOTING_TOP[ab])
        # The wing begins at the coping line: below the deck corner the junction belongs to the abutment end.
        inner = trimesh.creation.box([8., W2, 12.])
        inner.apply_translation([p[0], side * W2 / 2, 5.])
        abut = [new[f'cap_{ab}'], new[f'stem_{ab}']]
        wing = solid(boolean('difference', [wing, boolean('union', [inner] + abut)]), pid)
        wing, hits = clip(wing, {k: m for k, m in {**old, **new, **added}.items() if not k.startswith('wing_')}, pid)
        new[pid] = wing
        wing_records[pid] = dict(root_xy_m=np.round(p, 4).tolist(), tip_xy_m=np.round(p + ln * d, 4).tolist(),
                                 clipped_by=[f'cap_{ab}', f'stem_{ab}'] + hits)

    # ---- Checks: closed solids, no overlaps with any other part. ----
    final = {**old, **new, **added}
    for pid, m in {**new, **added}.items():
        expect(m.is_watertight and m.is_winding_consistent and m.volume > 0, f'{pid} final solid')
    clashes, pad_contacts = [], {}
    for pid in sorted({**new, **added}):
        for other, m in final.items():
            if other == pid or (other in new or other in added) and other < pid:
                continue
            v = overlap(final[pid], m)
            pair = sorted([pid, other])
            if pair[0].startswith(('B1_bearing_', 'B2_bearing_')) and pair[1].startswith(('beam_0_', 'beam_wrap_')):
                if v > 1e-7:                              # pad top on the beam soffit / under the 3 mm wrap skin
                    pad_contacts['|'.join(pair)] = round(v, 7)
            elif v > (2e-5 if pair == ['deck', 'overlay'] else 5e-6):   # coplanar-contact noise (180 m2 deck/overlay)
                clashes.append((pid, other, v))
    expect(not clashes, f'overlaps {clashes}')

    # ---- Write meshes. ----
    def hex_rgba(h):
        h = h.lstrip('#')
        return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)] + [255], 'u1')

    def put(pid, m, prim, color):
        v = np.asarray(m.vertices)
        prim['attributes'] = {
            'POSITION': append(np.column_stack([v[:, 0], v[:, 2], -v[:, 1]]).astype('<f4'), 'VEC3', 5126),
            'COLOR_0': append(np.tile(color, (len(v), 1)).astype('u1'), 'VEC4', 5121)}
        gltf['accessors'][prim['attributes']['COLOR_0']]['normalized'] = True
        prim['indices'] = append(np.asarray(m.faces).reshape(-1, 1).astype('<u4'), 'SCALAR', 5125)
        prim['mode'] = 4

    for pid in sorted(new):
        prim = meshes[pid]['primitives'][0]
        put(pid, new[pid], prim, read(prim['attributes']['COLOR_0'])[0])
        parts[pid]['bounds_m'] = np.round(new[pid].bounds, 6).tolist()
        parts[pid]['volume_m3'] = round(float(new[pid].volume), 9)

    tfc_color = parts['TFC_transition_-1_-1']['color']
    names = {'FC_railing_-1_-1': 'Northwest 5 ft 9 5/8 in FC railing on Wing A',
             'FC_railing_1_1': 'Southeast 5 ft 9 5/8 in FC railing on Wing D',
             'FC_railing_1_-1': 'Northeast 7 ft 10 5/8 in FC railing'}
    for rid in ('FC_railing_-1_-1', 'FC_railing_1_-1', 'FC_railing_1_1'):
        m = added[rid]
        st = stations[rid]
        if rid == 'FC_railing_1_-1':
            dims = dict(length_m=round(NE_RAIL, 6), height_above_surface_m=round(31.5 * IN, 6),
                        base_width_m=round(16 * IN, 6), top_width_m=round(9 * IN, 6),
                        back_face_offset_m=round(W2, 6), traffic_toe_offset_m=round(TOE, 6),
                        section='sheet 12 Section G-G / B-B: back vertical, 9 in top, knee 11 in from the back at '
                                '9 1/2 in, toe vertical below 2 1/2 in above the finished surface',
                        seat='retained coping (1 1/2 in below the finished surface) on the deck, open over the PCF '
                             'joint, reconstructed mudwall top on the finished surface')
            note = ('New 2026 7 ft 10 5/8 in Type FC railing at the northeast corner (sheet 12 Northeast Transition '
                    'railing elevation, Sections B-B and G-G; removal sheet 10). It replaces the end of the existing '
                    'railing on the deck (saw cut square, 6 ft 7 1/8 in from the deck end at the toe: sheet 10 gives '
                    '6 ft 9 in, which with the 1 ft mudwall and the 1 5/8 in joint measured normal to the joint makes '
                    'the written 7 ft 10 5/8 in), crosses the PCF joint and the mudwall and stops square at the 1/4 in '
                    'open joint at the start of the TFC (sheets 12-13). It is recessed where the PCF joint turns up into '
                    'its toe (sheet 11 detail; 3 mm clearance past the joint). Bond breaker, anchorage and reinforcement '
                    'are not modelled.')
            pages = [10, 11, 12]
        else:
            dims = dict(length_m=round(NW_RAIL, 6), height_above_surface_m=round(31.5 * IN, 6),
                        base_width_m=round(16 * IN, 6), top_width_m=round(9 * IN, 6),
                        back_face_offset_m=round(W2, 6), traffic_toe_offset_m=round(TOE, 6),
                        seat_el_ft=st['el'],
                        section='sheet 12 Section A-A: back vertical, 9 in top, knee 11 in from the back at 9 1/2 in, '
                                'toe vertical below 2 1/2 in above the finished surface',
                        seat='reconstructed mudwall top (finished surface), then the existing wingwall root at '
                             f'El. {st["el"]} (1985 sheet 7 Elevation F-F)')
            corner = 'northwest' if rid == 'FC_railing_-1_-1' else 'southeast'
            note = (f'New 2026 5 ft 9 5/8 in Type FC railing at the {corner} corner (sheet 12 railing elevation and '
                    'Section A-A; sheet 10: 5 ft 10 in from the existing open joint to the limit of wingwall removal). '
                    'From the mudwall side of the PCF joint opening (skewed with the joint) over the mudwall and the '
                    'existing wingwall root to a square end at the 1/4 in open joint before the TFC. Anchorage and '
                    'reinforcement are not modelled.')
            pages = [10, 12, 13, 14]
        part = dict(id=rid, name=names[rid], layer='rails', color=tfc_color, pdf_pages=pages,
                    basis='Approximate external envelope', note=note, dimensions=dims,
                    bounds_m=np.round(m.bounds, 6).tolist(), volume_m3=round(float(m.volume), 9), approximation=True)
        manifest['parts'].append(part)
        parts[rid] = part
        prim = {}
        put(rid, m, prim, hex_rgba(tfc_color))
        gltf['meshes'].append(dict(name=rid, extras=dict(processed=True, **part), primitives=[prim]))
        gltf['nodes'].append(dict(name=rid, mesh=len(gltf['meshes']) - 1))
        world['children'].append(len(gltf['nodes']) - 1)

    # ---- Manifest notes and dimensions. ----
    def note(pid, text, pages=()):
        p = parts[pid]
        p['note'] = (p.get('note', '') + ' ' + text).strip()
        p['pdf_pages'] = sorted(set(p['pdf_pages']) | set(pages))

    for pid in ('deck', 'overlay'):
        parts[pid]['dimensions'].update(end_u_m=[round(U_D[1], 6), round(U_D[2], 6)],
                                        length_on_line_a_m=round(U_D[2] - U_D[1], 6))
        note(pid, 'Rev. 1.3: ends at the deck-side face of the PCF joint (sheet 11 Section C-C, sheet 10 Section E-E), '
                  '1 ft 0 in mudwall + 2 in (Abut. 1) / 1 5/8 in (Abut. 2) joint opening inside the 45 ft 0 1/2 in floor '
                  'end, measured normal to the abutment; was run to the floor end over the mudwall. Drain cores re-cut '
                  'as in rev. 1.2. Overlay dam (sheet 11 Section C-C): over 1 ft 0 in (normal) from each deck end the '
                  'overlay reaches 5 5/8 in below the finished surface (1 1/2 in grade raise, sheet 9; 2 1/2 in top '
                  'cover, 1985 sheet 4 notes and sheet 9 A-A; #5 top bar; 1 in clear, sheet 11), returning at 45 deg '
                  'to the milled surface; the deck is notched to match, curb to curb.', [10, 11])
    for pid in ('retained_coping_-1', 'retained_coping_1'):
        parts[pid]['dimensions'].update(end_u_m=[round(U_D[1], 6), round(U_D[2], 6)])
        note(pid, 'Rev. 1.3: ends at the PCF joint with the deck (sheets 10-11).', [10, 11])
    for pid, ab in (('mudwall_1', 1), ('mudwall_2', 2)):
        parts[pid]['dimensions'].update(normal_width_m=FT, top='finished surface, crowned 1.5625 % (flush with the '
                                        'overlay and the RCBA)', span_face_u_m=round(U_M[ab], 6))
        note(pid, 'Rev. 1.3: rebuilt to sheet 11 (Section C-C, mudwall construction details) and sheet 15: 1 ft 0 in '
                  'normal to the abutment from the Type I-A joint at the floor end to the span face at the PCF joint, '
                  'top on the finished (overlay) surface with the crown; was 1 ft along Line "A" (0.87 ft normal) with '
                  'a flat top 111 mm below the crown, under the deck end.', [10, 11, 15])
    for pid, ab in (('PCF_joint_-1', 1), ('PCF_joint_1', 2)):
        parts[pid]['dimensions'].update(opening_normal_m=round((2 if ab == 1 else 1.625) * IN, 6),
                                        schematic_depth_m=PCF_DEPTH, upturn_rise_and_run_m=round(UPTURN, 6),
                                        extent='curb to curb, turned up 6 in x 6 in into each railing toe')
        note(pid, f'Rev. 1.3: fills the {"2 in" if ab == 1 else "1 5/8 in"} opening (sheet 11 note 3) between the deck '
                  'end and the mudwall span face, curb to curb, and turns up at 45 deg 6 in over 6 in into the railing '
                  'toe at both ends (sheet 11 Type PCF Bridge Expansion Joint End at Railing Detail); was a 50 mm strip '
                  'centred on the floor end over the full width. The leg keeps the schematic depth; the gland is not '
                  'modelled.', [11])
    note('retained_rail_-1', 'Rev. 1.3: west end at the deck end (PCF joint, sheets 11-12); east end at the square saw '
                             'cut where the new 7 ft 10 5/8 in NE railing begins (sheets 10, 12).', [10, 11, 12])
    note('retained_rail_1', 'Rev. 1.3: both ends at the deck ends (PCF joints, sheets 11-12); the new SE railing '
                            'begins beyond the joint.', [11, 12])
    for pid in ('retained_rail_-1', 'retained_rail_1'):
        parts[pid]['dimensions'].update(height_m=round(33 * IN, 6), toe_height_m=round(4 * IN, 6),
                                        section='sheet 9 existing barrier as drawn, the FC section of sheet 12 G-G: '
                                                '16 in base on the coping, 4 in vertical toe, knee 11 in from the back '
                                                'at 11 in, 9 in top at 2 ft 9 in')
        note(pid, 'Rev. 1.3: section re-swept to the existing barrier drawn on sheet 9 (1 ft 4 in x 2 ft 9 in, the FC '
                  'section that sheet 12 G-G dimensions for the new NE railing); was the generator envelope with a 7 in '
                  'toe and one slope, 0.10 m off the new railing face at the NE joint.', [9, 12])
    for ab in (1, 2):
        rear = 'west' if ab == 1 else 'east'
        parts[f'cap_{ab}']['dimensions'].update(front_face_from_cl_bearing_m=round(CAP_FRONT, 6),
                                                rear_face_from_cl_bearing_m=round(CAP_REAR, 6))
        note(f'cap_{ab}', f'Rev. 1.3: moved 6 in (normal) {rear}ward to 1985 sheet 5 Section A-A and sheet 9 Detail A: '
                          'front face 9 in span-side of CL bearing, rear face 1 ft 9 in behind it, flush with the '
                          'mudwall back face at the floor end; was centred on CL bearing.', [11])
        parts[f'stem_{ab}']['dimensions'].update(front_face_from_cl_bearing_m=round(STEM_FRONT, 6),
                                                 rear_face_top_m=round(STEM_REAR_TOP, 6),
                                                 rear_face_bottom_m=round(STEM_REAR_BOT, 6),
                                                 top_width_m=round(STEM_FRONT + STEM_REAR_TOP, 6),
                                                 bottom_width_m=round(STEM_FRONT + STEM_REAR_BOT, 6))
        note(f'stem_{ab}', 'Rev. 1.3: rebuilt to 1985 sheet 5 Section A-A: front face vertical 5 1/4 in span-side of CL '
                           'bearing (3 3/4 in behind the cap front), 1 ft 6 1/4 in wide under the cap, rear face '
                           'battered to 2 ft 2 3/4 in at the footing, bottom on the footing top (El. 817.03 / '
                           '816.95); was a 0.70 m wall centred on CL bearing, bottom Z = 0.05 m.')
        parts[f'footing_{ab}']['dimensions'].update(toe_from_cl_bearing_m=round(36.25 * IN, 6),
                                                    heel_from_cl_bearing_m=round(47.75 * IN, 6),
                                                    thickness_m=round(FOOTING_T, 6),
                                                    top_el_ft=817.03 if ab == 1 else 816.95)
        note(f'footing_{ab}', f'Rev. 1.3: moved 5 3/4 in (normal) {rear}ward with the stem: 2 ft 7 in toe and 2 ft 2 1/4 in '
                              'heel about the 2 ft 2 3/4 in stem base (1985 sheet 5 Section A-A, 7 ft 0 in), 2 ft 0 in '
                              f'thick with its top at El. {817.03 if ab == 1 else 816.95} (1985 sheet 5 A-A, sheet 7 '
                              'B-B, G-G); was centred on CL bearing, Z -0.60 to +0.05 (0.65 m).')
        for j in range(1, 7):
            pid = f'B{ab}_bearing_{j}'
            parts[pid]['dimensions'].update(plan_orientation='long side parallel to the 30 deg bearing line')
            note(pid, 'Rev. 1.3: pad envelope turned 30 deg about its centre to lie along the bearing line (1985 sheet 9 '
                      'Detail A); was axis-aligned, reaching 0.42 m behind CL bearing into the mudwall. Size and the '
                      'two pads per beam end of Detail A are not modelled (Standard PB11, known_deviations).')
    parts['approach_1']['dimensions'].update(step_under_ne_extension='square with the extension far end')
    note('approach_1', 'Rev. 1.3: the 4 in step of the north edge (22 ft 0 in under the NE extension, 22 ft 4 in beyond) '
                       'is square with the extension far end, as drawn on sheet 13; was on the old skewed end.', [13])
    parts['TFC_transition_1_-1']['dimensions'].update(start_x_m=round(x_ne, 6), end_x_m=round(x_ne + TFC_LEN, 6),
                                                      ends='square')
    note('TFC_transition_1_-1', 'Rev. 1.3: square ends from the floor end at the 22 ft 0 in line, where sheet 13 puts the '
                                'square end of the NE extension at the slab corner; the start at the toe is unchanged '
                                '(rev. 1.1 F4), the back face starts 0.235 m later than the skewed end.', [12, 13])
    parts['extension_1_-1']['dimensions'].update(start_x_m=round(x_ne, 6), end_x_m=round(x_ne + first.TFC_LEN, 6),
                                                 ends='square', outer_edge_offset_m=round(EXT_OUT, 6))
    note('extension_1_-1', 'Rev. 1.3: square ends (sheet 13), starting at the slab corner on the 22 ft 0 in edge; outer '
                           'edge 2 in beyond the TFC back face (sheet 12 Sections C-C to F-F). Length 15 ft 8 in kept '
                           '(sheet 13 scales 16 ft 0 in; not dimensioned).', [12, 13])
    for tid, eid, rid in (('TFC_transition_-1_-1', 'extension_-1_-1', 'FC_railing_-1_-1'),
                          ('TFC_transition_1_1', 'extension_1_1', 'FC_railing_1_1')):
        st = stations[tid]
        parts[tid]['dimensions'].update(start_x_m=round(st['x_start'], 6), end_x_m=round(st['x_end'], 6), ends='square')
        note(tid, 'Rev. 1.3: moved outward behind the new 5 ft 9 5/8 in FC railing and the 1/4 in open joint (sheet 12 '
                  'railing elevation; sheet 10 5 ft 10 in; sheets 13-14 4 ft 8 in from the slab corner), square ends; '
                  'was from the floor end with skewed ends.', [10, 12, 13, 14])
        x0, x1 = stations[eid]['x']
        parts[eid]['dimensions'].update(start_x_m=round(x0, 6), end_x_m=round(x1, 6), ends='square',
                                        length_m=round(x1 - x0, 6), outer_edge_offset_m=round(EXT_OUT, 6))
        note(eid, 'Rev. 1.3: square ends from the TFC start to the approach slab far end (sheets 13-14); outer edge 2 in '
                  'beyond the TFC back face as written on sheet 12 Sections C-C to F-F (the plans draw it 2 in inside); '
                  'was from the floor end, 15 ft 8 in, skewed ends, flush with the TFC back. Its length is 4.850 m '
                  'against 15 ft 10 in scaled because the model keeps a 25 mm Type I-A joint gap before the approach '
                  'slab.', [12, 13, 14])
    for pid, (ab, side, el_top, el_tip) in ACUTE.items():
        r = wing_records[pid]
        letter = 'A (northwest)' if ab == 1 else 'D (southeast)'
        parts[pid]['name'] = f'Abutment {ab} Wing {letter[:-1]}, acute corner)'
        parts[pid]['dimensions'] = dict(root_leg_width_m=round(15 * IN, 6), root_leg_offsets_m=[round(ROOT_FRONT, 6),
                                        round(W2, 6)], level_top_length_m=round(LEVEL_ACUTE, 6),
                                        main_wing_length_m=round(LEN_ACUTE, 6), angle_to_abutment_deg=30,
                                        top_el_level_ft=el_top, top_el_at_tip_ft=el_tip, top_thickness_m=TOP_T,
                                        base_thickness_m=round(BASE_ACUTE, 6), bottom_z_m=round(FOOTING_TOP[ab], 6),
                                        removal_top='finished surface - 1 ft 2 in within the RCBA extension',
                                        kink_xy_m=r['kink_xy_m'], tip_xy_m=r['tip_xy_m'])
        note(pid, f'Rev. 1.3: Wing {letter} rebuilt to 1985 sheet 7 Elevation F-F / End Elevation G-G and sheets 5-6 '
                  '(plan), with the 2026 removal of sheet 10: a 1 ft 3 in root leg under the railing (sheet 10 Sections '
                  f'A-A, B-B) from the floor end, top level at El. {el_top} for 4 ft 10 3/4 in to the kink; the main wing '
                  f'at 30 deg to the abutment, 18 ft 11 3/4 in, top falling to El. {el_tip}, 1 ft 0 in at the top with '
                  'the rear face battered to 1 ft 8 in at the base (G-G "Batter Varies", read as a constant base width); '
                  'top lowered to the finished surface less 1 ft 2 in under the RCBA extension (sheet 10 Section B-B, '
                  'sheet 12 elevation: 1 ft RCBA on 2 in polystyrene). Was a straight 4.70 m, 0.40 m wall with the top '
                  f'about 1.1 m too high at the tip. Base on the footing top, El. {817.03 if ab == 1 else 816.95} '
                  '(1985 sheet 7 G-G, sheet 5 A-A); the lower retained wall is not dimensioned.', [5, 10, 12, 13, 14])
    for pid, (ab, side, el_top, el_tip) in OBTUSE.items():
        r = wing_records[pid]
        letter = 'B (southwest)' if ab == 1 else 'C (northeast)'
        parts[pid]['name'] = f'Abutment {ab} Wing {letter[:-1]}, obtuse corner)'
        parts[pid]['dimensions'].update(root_xy_m=r['root_xy_m'], tip_xy_m=r['tip_xy_m'], top_thickness_m=TOP_T,
                                        base_thickness_at_tip_m=round(TOP_T + (z_el(el_tip) - FOOTING_TOP[ab]) / 12, 6),
                                        rear_batter='1:12', bottom_z_m=round(FOOTING_TOP[ab], 6),
                                        root='coping corner on the abutment front face, 9 in span-side of CL bearing')
        parts[pid]['dimensions'].pop('nominal_thickness_m', None)
        note(pid, f'Rev. 1.3: Wing {letter} root moved to the coping corner on the abutment front face (1985 sheet 5 '
                  'plan; front face 9 in span-side of CL bearing, 1985 sheet 5 Section A-A); was the model cap end, '
                  '0.15 m outside the coping, 50 mm clear of the deck. 1 ft 0 in at the top, rear face battered 1:12 '
                  '(1985 sheet 7 Section D-D; 1 ft 9 1/2 in at the tip, End Elevation B-B), base on the 2 ft footing '
                  f'top at El. {817.03 if ab == 1 else 816.95}; direction, length and top profile as rev. 1.1. The '
                  'wing begins at the coping line and is clipped to the model cap and stem where it meets the abutment '
                  'end. The 2026 removal plan (sheet 10) traces the face from about the railing toe; the 1985 plan '
                  'governs (decision).', [5])

    for p in parts.values():
        if p['id'] in new or p['id'] in added:
            mesh = next(m for m in gltf['meshes'] if m['name'] == p['id'])
            mesh['extras'] = dict(processed=True, **p)

    for item in manifest.get('detail_coverage', []):
        if item.get('feature') == '2026 exterior repair design':
            item['part_ids'] = item['part_ids'] + [k for k in added if k not in item['part_ids']]
            item['detail'] += (' Rev. 1.3: deck and overlay end at the PCF joints with the 1 ft mudwall top flush between '
                               'the joints; new FC railings (5 ft 9 5/8 in NW/SE, 7 ft 10 5/8 in NE) and the NW/SE TFCs '
                               'and extensions at the sheet 12 stations (sheets 10-14).')
        elif item.get('feature') == 'Historical support and framing topology':
            item['detail'] += (' Rev. 1.3: acute wings A/D with the root leg, kink and F-F top and the 2026 removal; '
                               'obtuse wings B/C rooted at the coping corner on the abutment front face, battered '
                               '(1985 sheets 5-7, sheet 10).')
        elif item.get('feature') == 'Unresolved details':
            item['detail'] = item['detail'].replace('wing outlines, ', 'wing footings and the retained lower wing walls, ')

    manifest['known_deviations'] = [
        dict(id='midspan-drain-overlay-taper', parts='overlay, midspan_drain_-1, midspan_drain_1',
             source='sheet 9 (Overlay at Deck Drain Details, Section D-D, typical sections); sheet 8 note 7',
             deviation='The overlay keeps its full surface up to the 2 in drain cores; sheet 9 tapers the surface toward '
                       'each mid-span drain over 1 ft 0 in (a 1 ft x 2 ft area along the face of rail).',
             reason='The taper area is dimensioned but its depth is not. "Taper Surface to Ex. Drain Edge" points to the '
                    'existing drain edge, whose elevation is not given: it can be the milled slab (2 in below the '
                    'finished surface, overlay feathered out), the unmilled deck ("Ex. Profile Grade + 1 1/2 in", '
                    '1 1/2 in below) or the drafted taper (about 1 in at 1 in = 1 ft in Section D-D). The Special '
                    'Provision for Deck Drain Clean and Fill (sheet 8 note 7, not in the set) or a survey of the '
                    'existing drain edges would settle it.'),
        dict(id='bearing-pad-plan', parts='B1_bearing_1..6, B2_bearing_1..6',
             source='1985 sheet 9 Detail A and Section B-B (Type 7B); Standard PB11 (not in the set)',
             deviation='Each beam end has one 0.23 m x 1.05 m x 50 mm pad envelope (generator assumption), parallel to '
                       'the bearing line. 1985 sheet 5 calls for 12 Type 7B pads per abutment and Detail A (1985 sheet 9) '
                       'draws them in pairs, one under each edge of the beam end.',
             reason='The pad length, width and thickness are on Standard PB11 (referenced on 1985 sheet 5), which is not '
                    'in the set, and Detail A gives no pad dimensions or offsets (its 1/2 in = 1 ft scan is not reliable '
                    'to scale for a pad), so the pairs cannot be placed without inventing their size; PB11 would settle '
                    'it.'),
        dict(id='ne-corner-wingwall-root', parts='FC_railing_1_-1, wing_1_-1, extension_1_-1',
             source='sheet 12 Section B-B and NE railing elevation; sheet 13; sheet 10 removal plan; 1985 sheet 6',
             deviation='At the NE corner the square TFC and RCBA extension start at the floor end on the 22 ft 0 in line '
                       '(sheet 13), so between the skewed mudwall back face and that square end (up to 0.23 m along the '
                       'railing back face) the new 7 ft 10 5/8 in railing has nothing under its back half. Sheet 12 '
                       'Section B-B shows the existing wingwall there, and sheet 10 traces Wing C back to the floor end, '
                       'but the 1985 plan (which the model follows for Wing C) starts the wing at the coping line.',
             reason='The outline of the existing wingwall root behind the mudwall at the NE corner is not dimensioned '
                    'on either set; a field survey of the NE corner (or the pre-1985 plans) would settle it.')]

    # ---- Ledger: the deck slab now ends at the PCF joints. ----
    ledger_path = base / 'source_ledger.json'
    ledger_change = None
    if ledger_path.exists():
        raw_ledger = ledger_path.read_bytes()
        ledger = json.loads(raw_ledger)
        if abs(ledger.get('deck_length_m', 0) - first.LENGTH) < 1e-4:
            ledger['floor_length_out_to_out_m'] = ledger['deck_length_m']
            ledger['deck_length_m'] = round(U_D[2] - U_D[1], 6)
            ledger['deck_slab_end_u_m'] = [round(U_D[1], 6), round(U_D[2], 6)]
            ledger_change = dict(deck_length_m=[round(first.LENGTH, 6), ledger['deck_length_m']],
                                 added=['floor_length_out_to_out_m', 'deck_slab_end_u_m'])
            text = json.dumps(ledger, indent=2)
            if b'\r\n' in raw_ledger:
                text = text.replace('\n', '\r\n')
            if raw_ledger.endswith(b'\n'):
                text += '\r\n' if b'\r\n' in raw_ledger else '\n'
            backup.mkdir(parents=True, exist_ok=True)
            (backup / f'{BID}_source_ledger_before_review_correction_3.json').write_bytes(raw_ledger)
            ledger_path.write_bytes(text.encode('utf-8'))

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

    def r6(v):
        return round(float(v), 6)
    manifest['review_correction_3'] = TAG
    manifest['revision'] = REVISION
    manifest['review_correction_record_3'] = dict(
        source_pdf_pages=[8, 9, 10, 11, 12, 13, 14, 15], printed_sheets=[8, 9, 10, 11, 12, 13, 14, 15],
        supplementary_source=dict(document_id='9548292', local_file='sources/existing_plans_9548292.pdf',
                                  pdf_pages=[5, 6, 7, 9]),
        previous_revision=PREVIOUS_REVISION,
        resolved_deviations=['floor-end-over-mudwall', 'transition-railing-stations', 'acute-corner-wings'],
        decided_deviations=['obtuse-wing-roots'],
        kept_deviations=['midspan-drain-overlay-taper'],
        resolved_in_final_pass=dict(
            pcf_upturns='6 in x 6 in 45 deg legs at all four railing ends (sheet 11 detail)',
            ne_square_ends='TFC_transition_1_-1, extension_1_-1 and FC_railing_1_-1 square (sheet 13); approach_1 step '
                           'squared with it',
            rcba_extension_outer_edge='2 in beyond the TFC back face, |Y| = 7.1628 m (sheet 12 C-C to F-F)',
            abutment_outline='caps 9 in / 1 ft 9 in about CL bearing, stems battered, footings 2 ft 7 in toe / '
                             '2 ft 2 1/4 in heel (1985 sheet 5 Section A-A); acute wing roots now meet the cap rear face',
            pad_orientation='pads parallel to the bearing line (1985 sheet 9 Detail A)',
            retained_rail_section='existing barrier as drawn on sheet 9 = sheet 12 G-G FC section',
            overlay_dam='5 5/8 in below the surface over 1 ft 0 in at each deck end, 45 deg return (sheet 11 C-C; 1985 '
                        'sheet 4 notes 2 1/2 in top cover)',
            footings='2 ft 0 in thick, tops El. 817.03 / 816.95; stems and wings based on them (1985 sheet 5 A-A, sheet 7 '
                     'B-B, G-G)',
            obtuse_wing_batter='rear face 1:12 (1985 sheet 7 Section D-D)'),
        new_deviations=['bearing-pad-plan', 'ne-corner-wingwall-root'],
        pad_beam_contact_overlaps_m3=pad_contacts,
        decisions=[
            dict(id='obtuse-wing-roots', reading='1985 sheet 5 plan: wing front face from the coping corner on the '
                 'abutment front face (9 in span-side of CL bearing, 1985 sheet 5 Section A-A)',
                 rejected='sheet 10 tracing, which starts the face about at the railing toe (1.2 ft inside the coping)',
                 reasoning='The 1985 plan is the construction drawing of these wings; sheet 10 is a 1 in = 5 ft '
                           'reference tracing (general note 2: existing details for reference only) whose transverse '
                           'scale is about 1 % off (44 ft 0 in roadway drawn 43 ft 6.8 in).'),
            dict(id='ne-railing-cut', reading='new railing 7 ft 10 5/8 in (sheet 12) ending at the TFC start; cut '
                 '6 ft 7 1/8 in from the deck end along the toe', rejected='6 ft 9 in removal (sheet 10) along the toe',
                 reasoning='7 ft 10 5/8 in = 6 ft 9 in + 1 ft 0 in mudwall + 1 5/8 in joint measured normal to the '
                           'joint; along the railing those two measure 1 ft 3 3/4 in and the 1/4 in open joint follows, so the cut is 1 7/8 in '
                           'nearer the bridge end than 6 ft 9 in. The fabricated railing length and the TFC '
                           'start (rev. 1.1 F4) govern.'),
            dict(id='wing-batter', reading='rear face battered from 1 ft 0 in at the top to the End Elevation base '
                 'width (1 ft 8 in A/D, 1 ft 9 1/2 in B/C) along the whole wall',
                 rejected='the 0.40 m nominal vertical wall', reasoning='G-G marks the batter "Varies" under the '
                 'sloping top, i.e. a constant base width; it is the only dimensioned wall section.')],
        values=dict(
            mudwall_normal_width_m=FT, pcf_opening_normal_m={'abutment_1': r6(2 * IN), 'abutment_2': r6(1.625 * IN)},
            u_floor_end_m=r6(L2), u_mudwall_span_face_m=[r6(U_M[1]), r6(U_M[2])], u_deck_end_m=[r6(U_D[1]), r6(U_D[2])],
            nw_se_fc_railing_m=r6(NW_RAIL), ne_fc_railing_m=r6(NE_RAIL), open_joint_m=r6(OPEN_JOINT),
            ne_saw_cut_x_m=r6(x_cut), stations={k: {a: (r6(b) if not isinstance(b, list) else [r6(c) for c in b])
                                                    for a, b in v.items()} for k, v in stations.items()},
            wings=wing_records, parts=info),
        changed_parts=sorted(new), added_parts=sorted(added), removed_parts=[],
        source_ledger_change=ledger_change,
        frame='revision 1.2 frame: X east, Y north (left of increasing station), Z up, Z = 0 at El. 817.00',
        before_glb_sha256=before, after_glb_sha256=hashlib.sha256(out).hexdigest())
    text = json.dumps(manifest, indent=2)
    if b'\r\n' in raw_manifest:
        text = text.replace('\n', '\r\n')
    if raw_manifest.endswith(b'\n'):
        text += '\r\n' if b'\r\n' in raw_manifest else '\n'
    mp.write_bytes(text.encode('utf-8'))
    print(json.dumps({k: manifest['review_correction_record_3'][k] for k in
                      ('changed_parts', 'added_parts', 'source_ledger_change', 'before_glb_sha256',
                       'after_glb_sha256')}, indent=1))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--base', type=Path, default=BASE, help='bridge folder (default: the repository copy)')
    parser.add_argument('--backup', type=Path, default=BACKUP, help='backup folder')
    args = parser.parse_args()
    correct(args.base, args.backup)

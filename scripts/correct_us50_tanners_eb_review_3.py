"""Third drawing-confirmed correction of US 50 EB over Tanners Creek (us50-tanners-eb): the known deviations left by
the first two review rounds. Runs after scripts/correct_us50_tanners_eb_review.py and ..._review_2.py and keeps the
GLB buffers of the parts it does not change.

    python scripts/correct_us50_tanners_eb_review_3.py [--base DIR] [--backup DIR]

Source: drawings.pdf, 2014 B-29709 reconstruction. Printed sheet N is PDF page N + 86 (sheet 26 = PDF 112).
Native axes (unchanged): X along Line "A" stations, Y to the LEFT of increasing station (north), Z = El. - 450 ft in
metres; support lines X = u - tan20 Y (north end at the lower station). p runs along a support line, q normal to it.

1. Bearing-seat schedule (known deviation `bearing-seat-schedule`; seat tables on sheets 26, 29, 35, 39). Seats are
   set to the scheduled elevations. Interior bents: the Type T1 elastomeric pad is 3 11/16 in from seat to beam soffit
   (sheet 54 SECTION E-E AT BEAMS), so the beam soffit at each bearing is seat + 3 11/16 in. The cap tops are the
   seat terraces of sheets 35/39 ("Seat Dim's" 9'-3 3/4", 5 x 11'-6 1/4", 7'-4" from the north end; the lowest
   terrace closes on the 5'-1 1/8" / 5'-1 1/2" cap depths of sheets 35/39 within 0.005 ft), each at its beam's seat
   for both bearing rows, with a 3 in x 1 ft 0 in x 8 ft 9 in keyway centred on each step, 3 in below each terrace
   (sheets 35, 39, 54). The 52 separate interior pedestals are removed. End bents: the seat is the beam soffit, which
   bears on the 6 in x 1 in anchor bar (sheet 32
   ANCHOR PLATE DETAIL; the 1/2 in plate is cast flush in the beam, sheet 45): the sheet 32 SECTION B-B chain soffit +
   2'-8 1/4" (2'-7 7/8" at Bent 6) + 7" closes on the lowest seats 482.965 / 483.010 within 0.004 ft (DECISION: its
   1 3/8 in fillet is read as a minimum, as on sheet 54 where it is labelled Min.). Beams are no
   longer parallel to the profile with a uniform 0.10 m haunch: each beam soffit runs on the chord between its
   bearings plus the sheet 45 residual camber at midspan (A, E 0.46 in; B, D 1.79 in; C 1.54 in), distributed as a
   parabola (the sheets give only the midspan value). Haunches fill from the beam top to the slab soffit. Interior
   bearings become single 3 11/16 in pads; end-bent bearings become the 6 in x 2 ft 7 in x 1 in anchor bars (bulb
   2 ft 1 in + 3 in minimum each side). X frames move with their beams. Beam ends stay square, as drawn (sheet 43
   BEARING DETAIL AT BENTS NO.2 THRU NO.5, sheet 45 BEAM END DETAILS).
2. Interior support diaphragms, Bents 2-5 (known deviation `interior-support-diaphragms`; sheet 54 SECTION E-E,
   sheet 43 BEARING DETAIL, sheet 53 SECTION A-A "End Diaphragm at Int. Bents"). New parts diaphragm_1 ... diaphragm_4:
   3 ft 0 in normal to the bent (1 ft 6 in each side of the centre line, 9 in inside the cap faces), from the slab
   soffit down to the beam soffits, stepping at mid-bay between the adjacent beam levels (sheet 53), between the inner
   faces of beams 1 and 7 and filling the 6 in gap between all beam ends within the beam outline. The soffit stays
   3 11/16 in (the polystyrene of SECTION E-E BETWEEN BEAMS) above the cap terraces, stepping on the terrace lines,
   and a 10 in x 8 ft 7 in key drops into each cap keyway to 1/2 in above its bottom (1 in clearance at the sides
   and ends, sheet 54). The polystyrene itself is left as gaps.
3. Wingwalls (known deviation `end-bent-wingwalls`; sheets 26, 29 PLAN, sheets 28, 31 WINGWALL ELEVATIONS and SECTION
   "C-C"). New parts wing_0_-1 (southwest), wing_0_1 (northwest), wing_5_1 (northeast), wing_5_-1 (southeast):
   1 ft 3 in thick, outer face continuing the end-bent end (parallel to the roadway, 2 in inside the coping), from the
   end-bent back face to a square end 14 ft 0 in (SW, NE) or 13 ft 6 1/2 in (NW, SE) from the front face along the
   outer face (10 ft 0 1/8 in / 9 ft 6 5/8 in beyond the back face). Bottom at the end-bent soffit El. 479.69 /
   479.77. SECTION C-C: the approach slab, 1 ft 2 1/2 in thick over the wall (its underside continuing the sheet 32
   ledge level), sits on 1 in polystyrene on the wall top, 1 ft 3 1/2 in below the slab top, with a 5 in tongue in a
   3 in x 6 in keyway centred in the wall top (1/2 in and 1 in polystyrene). The approach slabs get these strips and
   tongues over the four wings. DECISION: C-C governs the stack; the four written top-of-wing elevations (488.15,
   488.08, 488.28, 488.20) equal the written end-of-bent slab tops (489.40, 489.32, 489.53, 489.44) + grade - 1 ft
   2 1/2 in within 0.006 ft, i.e. the slab underside, and those slab tops put the crown on the structure centre line,
   while sheets 23/53 and all 42 seat elevations put it on Line "A" (as modelled).
4. Deck length (known deviation `deck-end-length`; sheets 20-22: 492 ft 0 7/8 in out to out, 1 ft 5 1/2 in from the
   end-bent centre lines along Line "A"; sheet 32: 1 ft 4 1/2 in normal). The deck ends move out 9.525 mm each; the
   sidewalk, FT barrier, PS-1 base and rails are stretched with them, and the end PS-1 posts, the joint strips and the
   approach slabs move with the deck ends.
5. Approach terminal joints (known deviation `approach-east-terminal-station`; sheets 22, 58, 60). DECISION: the slab
   edges are dimensioned from the End of Bridge Floor (20 ft 6 in, 46 ft 9 1/4 in, 36 ft 5 7/8 in / 30 ft 9 3/8 in at
   the construction joints); measured from the corrected floor end they put the west terminal at Sta. 386+34.07, on
   the callout 386+34.06, and the east terminal at 391+93.41. The two east callouts (391+92.68 sheet 60, 391+92.86
   sheet 22) disagree with each other and with these dimensions, so the dimensions govern. The model had measured the
   edges from the far side of the 24 mm visual joint; the terminal joints now sit at floor end + dimension.

6. End-bent flange notches (sheets 46-48 BEAM ELEVATION and BEAM PLANS; raised by the third check): at the end-bent
   end of the span A and E beams the top flange is set back 6 in and its acute half (south at Bent 1, north at Bent
   6) is cut parallel to the bent, 10 7/8 in more at the flange edge. The haunches are cut with them and the end
   bents fill the notches. The flanges now stop 0.35 m inside the End of Bridge Floor and no longer reach the
   approach slabs.

Kept (known deviation `end-bent-beam-notch-depth`): the notch depth is not dimensioned (the elevations are not to
scale); the cut is taken through the top flange and its fillet, the 11 in above the web of the sheet 45 section.

Requires numpy, trimesh and manifold3d, plus the two earlier correction scripts (rules and helpers).
"""
import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

import manifold3d
import numpy as np
import shapely.geometry as sg
import shapely.ops
import trimesh

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import bridge_geometry  # noqa: E402  (colours and layer labels only)
import refresh_geometry_verification  # noqa: E402  (its closed-mesh test, read only)
import correct_us50_tanners_eb_review as first  # noqa: E402
import correct_us50_tanners_eb_review_2 as second  # noqa: E402

BID = first.BID
BASE = ROOT / 'data/bridges' / BID
BACKUP = ROOT / 'data/fem_research'
TAG = 'review-2026-11-3-seat-schedule-diaphragms-wings-deck-ends'
PREVIOUS_REVISION = second.REVISION
REVISION = '1.3-deviations'

FT, IN, C, K, T = first.FT, first.IN, first.C, first.K, first.T
BS, W, D, SLAB = first.BS, first.W, first.D, first.SLAB
YS = first.YS                                # beam 1 (north, +Y) ... beam 7
L_OLD = first.L
L_NEW = (492 + 0.875 / 12) * FT              # sheets 20-22: 492'-0 7/8" out to out
DL = (L_NEW - L_OLD) / 2                     # 0.009525 m at each end

# Seat elevations (ft), beam 1 ... 7: sheet 26 (Bent 1), 35 (Bents 2, 5), 39 (Bents 3, 4), 29 (Bent 6).
SEAT_EL = {0: [483.100, 483.325, 483.555, 483.580, 483.375, 483.170, 482.965],
           1: [483.010, 483.240, 483.460, 483.490, 483.280, 483.070, 482.870],
           2: [483.220, 483.440, 483.660, 483.680, 483.470, 483.250, 483.040],
           3: [483.270, 483.490, 483.700, 483.710, 483.490, 483.270, 483.050],
           4: [483.150, 483.360, 483.570, 483.570, 483.350, 483.120, 482.900],
           5: [483.285, 483.490, 483.695, 483.695, 483.465, 483.235, 483.010]}
SEAT_SHEET = {0: 26, 1: 35, 2: 39, 3: 39, 4: 35, 5: 29}
PAD_T1 = (3 + 11 / 16) * IN                  # sheet 54 SECTION E-E AT BEAMS, Type T1 pad
PAD_X, PAD_Y = 22 * IN, 23.5 * IN            # plan size of the existing bearing envelopes (kept)
ANCHOR_ALONG, ANCHOR_T = 6 * IN, 1 * IN      # sheet 32 ANCHOR PLATE DETAIL: bar 6 in x 1 in
ANCHOR_ACROSS = (2 + 1 / 12) * FT + 2 * 3 * IN   # 2'-1" bulb + 3 in minimum each side
CAMBER = np.array([0.46, 1.79, 1.54, 1.79, 0.46]) * IN   # sheet 45 DEFLECTIONS AT MIDSPAN, residual camber
CAP_HALF = second.CAP_HALF_WIDTH
DIAPH_HALF = 1.5 * FT                        # sheet 54 / sheet 43: 3'-0" diaphragm
GAP = 3 * IN                                 # beam ends 3 in from the interior bent centre lines (sheet 43)
END_FACE = 3.75 * FT / 2 / C                 # end-bent faces, u offset from the bent line
WING_T = 1.25 * FT                           # sheets 26, 28, 29, 31: 1'-3"
# (bent index, side): plan name, outer-face length from the front face, written top of wing, written top of slab.
WINGS = {(0, -1): ('southwest', 14 * FT, 488.15, 489.40), (0, 1): ('northwest', (13 + 6.5 / 12) * FT, 488.08, 489.32),
         (5, 1): ('northeast', 14 * FT, 488.28, 489.53), (5, -1): ('southeast', (13 + 6.5 / 12) * FT, 488.20, 489.44)}
WING_PAGES = {0: [112, 114], 5: [115, 117]}
# Sheets 35, 39 ELEVATION "Seat Dim's": seat terraces from the north cap end (ft). The 1'-1 3/4" + 10'-4 1/2" pair is
# beam 4's 11'-6 1/4" terrace split by the construction joint; beam 7's terrace is the last 7'-4".
TERRACE_STEPS_FT = np.cumsum([9 + 3.75 / 12, 11 + 6.25 / 12, 11 + 6.25 / 12, 1 + 1.75 / 12 + 10 + 4.5 / 12,
                              11 + 6.25 / 12, 11 + 6.25 / 12])
KEYWAY_L, KEYWAY_W, KEYWAY_D = 8.75 * FT, 1.0 * FT, 3 * IN    # sheets 35, 39, 54: 3 in x 1 ft 0 in x 8 ft 9 in
KEY_FOAM_BOTTOM, KEY_FOAM_SIDE, KEY_FOAM_END = .5 * IN, 1 * IN, 1 * IN   # sheet 54 polystyrene in the keyway
WING_TOP_DEPTH = (1 + 3.5 / 12) * FT         # sheets 28, 31 C-C: 1'-2 1/2" to the slab underside + 1" polystyrene
WING_FOAM = 1 * IN
WING_KEY_W, WING_KEY_D = 6 * IN, 3 * IN       # C-C: 3 in x 6 in keyway in the wall top
WING_KEY_SIDE, WING_KEY_BOTTOM = .5 * IN, 1 * IN   # C-C polystyrene: 1/2 in each side, 1 in in the bottom
NOTCH_SETBACK = 6 * IN                        # sheets 46-48: top flange set back 6 in at the end-bent ends
NOTCH_SKEW = 30 * IN * T                      # acute half cut parallel to the bent: 2'-6" x tan 20 = 10 7/8 in
NOTCH_Z = 55 * IN                             # flange (with fillet) above the web, sheet 45 section: 55 in to 66 in
SOURCE_PAGES = [106, 107, 108, 109, 112, 114, 115, 117, 118, 121, 125, 129, 131, 132, 133, 134, 139, 140, 144, 146]
PRINTED_SHEETS = [p - 86 for p in SOURCE_PAGES]

g = first.Geom(True)


# ---- Seats, beams, haunches, bearings and pedestals. ----
def seat(bi, j):
    return float(first.z_el(SEAT_EL[bi][j]))


def bearing_level(bi, j):
    """Beam soffit at a bearing: the seat at the end bents, seat + T1 pad at the interior bents."""
    return seat(bi, j) + (0.0 if bi in (0, 5) else PAD_T1)


def soffit(i, j, u):
    """Beam soffit along span i, beam j: chord between the bearings plus the parabolic residual camber."""
    ua, ub = first.bearing_u(i, 'start'), first.bearing_u(i, 'end')
    za, zb = bearing_level(i, j), bearing_level(i + 1, j)
    s = (np.asarray(u, dtype=float) - ua) / (ub - ua)
    return za + (zb - za) * s + 4 * CAMBER[i] * s * (1 - s)


def beam(i, j):
    ga, gb = first.beam_ends(i, True)
    y = YS[j]
    return first.loft(np.array(first.PROFILE) * IN, np.linspace(ga, gb, max(3, int((gb - ga) / .6) + 1)),
                      lambda u, v, z: (g.sx(u, y), y + v, float(soffit(i, j, u)) + z))


def haunch(i, j, lift=0.0, drop=0.0):
    """Beam top to slab soffit on the beam's own stations. lift / drop enlarge the solid upward / downward; used only
    for boolean cutters."""
    ga, gb = first.beam_ends(i, True)
    y, w = YS[j], 60 * IN
    return first.loft([(-w / 2, 0), (w / 2, 0), (w / 2, 1), (-w / 2, 1)], np.linspace(ga, gb, max(3, int((gb - ga) / .6) + 1)),
                      lambda u, v, t: (g.sx(u, y), y + v, (1 - t) * (float(soffit(i, j, u)) + D - drop)
                                       + t * (float(g.surf(g.sx(u, y), y + v)) - SLAB + lift)))


def bearing(i, j, end):
    u, y = first.bearing_u(i, end), YS[j]
    bi = i if end == 'start' else i + 1
    x, top = g.sx(u, y), float(soffit(i, j, u))
    if bi in (0, 5):
        m = first.box(x - ANCHOR_ALONG / 2, x + ANCHOR_ALONG / 2, y - ANCHOR_ACROSS / 2, y + ANCHOR_ACROSS / 2,
                      top - ANCHOR_T, top)
    else:
        m = first.box(x - PAD_X / 2, x + PAD_X / 2, y - PAD_Y / 2, y + PAD_Y / 2, top - PAD_T1, top)
    # The top follows the beam soffit along the beam (thickness exact at the bearing centre line, +/-2 mm at the ends);
    # where a pad reaches past the beam end into the 6 in gap it stays at or below the bearing level (diaphragm above).
    v = np.asarray(m.vertices, dtype=float).copy()
    upper = np.isclose(v[:, 2], top)
    uu = v[upper, 0] - K * y
    zz = soffit(i, j, uu)
    ga, gb = first.beam_ends(i, True)
    beyond = (uu < ga) | (uu > gb)
    v[upper, 2] = np.where(beyond, np.minimum(zz, top), zz)
    return trimesh.Trimesh(vertices=v, faces=np.asarray(m.faces), process=False)


def qbox(bi, q0, q1, y0, y1, z0, z1):
    """Box between normal offsets q0..q1 from the bent line, constant-Y sides."""
    return first.loft([(y0, z0), (y1, z0), (y1, z1), (y0, z1)], [q0 / C, q1 / C],
                      lambda t, y, z: (g.sx(BS[bi] + t, y), y, z))


def ped_top(bi, j):
    return seat(bi, j) - (ANCHOR_T if bi in (0, 5) else 0.0)


def peds(bi):
    """End bents: seat steps under the anchor bars above the lowest one (encased in the end bent). Interior bents: none;
    the seats are the terraces of the cap itself (sheets 35, 39)."""
    tops = [ped_top(bi, j) for j in range(7)]
    flat = min(tops)
    out = {}
    if bi not in (0, 5):
        return out, flat
    for j, y in enumerate(YS):
        if tops[j] > flat + 1e-9:
            out[f'ped_{bi}_{j}_0'] = first.transverse(g, BS[bi], .65, y - .34, y + .34, flat, tops[j])
    return out, flat


def pqbox(bi, p0, p1, q0, q1, z0, z1):
    """Box in the bent frame: p0..p1 along the bent, q0..q1 normal to it."""
    return first.loft([(p0, z0), (p1, z0), (p1, z1), (p0, z1)], [q0, q1],
                      lambda q, p, z: (*first.bent_point(bi, p, q), z))


def terrace_p(bi):
    """Terrace boundaries along an interior bent: step k between beam k and beam k + 1 (sheets 35, 39)."""
    p_north = first.cap_extent(bi)[1] / C
    return [p_north - d * FT for d in TERRACE_STEPS_FT]


def snap(mesh, sources, tol=2e-5):
    """Put result vertices that are float32 copies of input vertices back on the exact inputs (manifold3d works in
    float32), so faces shared with neighbouring parts stay coincident."""
    ref = np.vstack([np.asarray(m.vertices, dtype=float) for m in sources])
    v = np.asarray(mesh.vertices, dtype=float).copy()
    for k in range(0, len(v), 256):
        d = ((v[k:k + 256, None, :] - ref[None, :, :]) ** 2).sum(-1)
        n = d.argmin(axis=1)
        close = d[np.arange(len(n)), n] < tol ** 2
        v[k:k + 256][close] = ref[n[close]]
    out = trimesh.Trimesh(vertices=v, faces=np.asarray(mesh.faces), process=False)
    return out if out.is_watertight and out.is_winding_consistent and out.volume > 0 else mesh


def boolean(pieces, cutters, origin, snap_to=None):
    body = manifold3d.Manifold.batch_boolean([first.to_manifold(m, origin) for m in pieces], manifold3d.OpType.Add)
    if cutters:
        body = body - manifold3d.Manifold.batch_boolean([first.to_manifold(m, origin) for m in cutters],
                                                        manifold3d.OpType.Add)
    parts = [c for c in body.decompose() if abs(c.volume()) > 1e-8]     # drop zero-volume slivers
    body = parts[0] if len(parts) == 1 else manifold3d.Manifold.batch_boolean(parts, manifold3d.OpType.Add)
    m = first.from_manifold(body, origin)
    if not (m.is_watertight and m.is_winding_consistent and m.volume > 0):
        raise ValueError('boolean result invalid')
    return snap(m, snap_to) if snap_to else m


def stepped_slot(bi, pk, z_north, z_south, half_len, half_w, depth, top, riser_shift=0.0):
    """One solid along the bent: p = pk -/+ half_len, |q| <= half_w, bottom `depth` below z_south (p < pk) and
    z_north (p > pk), up to `top`. One loft, so no face lies on the terrace step plane (clean booleans). riser_shift
    moves the riser of the bottom step that far into the lower side (the key's clearance to the keyway riser)."""
    if abs(z_north - z_south) >= KEYWAY_D:
        raise ValueError('terrace step deeper than a keyway')
    pr = pk + (riser_shift if z_north < z_south else -riser_shift)
    prof = [(pk - half_len, z_south - depth), (pr, z_south - depth)]
    if abs(z_north - z_south) > 1e-9:
        prof.append((pr, z_north - depth))
    prof += [(pk + half_len, z_north - depth), (pk + half_len, top), (pk - half_len, top)]
    return first.loft(prof, [-half_w, half_w], lambda q, p, z: (*first.bent_point(bi, p, q), z))


def terraced_cap(bi):
    """Interior cap: the sheet 34 rectangle with the sheet 35/39 seat terraces (each at its beam's scheduled seat) and
    a 3 in x 1 ft 0 in x 8 ft 9 in keyway centred on each terrace step (sheets 35, 39, 54), 3 in below each terrace."""
    y0, y1 = first.cap_extent(bi)
    pk, z = terrace_p(bi), [seat(bi, j) for j in range(7)]
    soff = float(first.z_el(first.SOFFIT_EL[bi]))
    prof = [(y0 / C, soff), (y1 / C, soff), (y1 / C, z[0])]
    for k in range(6):
        prof.append((pk[k], z[k]))
        if abs(z[k + 1] - z[k]) > 1e-9:
            prof.append((pk[k], z[k + 1]))
    prof.append((y0 / C, z[6]))
    cap = first.loft(prof, [-CAP_HALF, CAP_HALF], lambda q, p, zz: (*first.bent_point(bi, p, q), zz))
    cuts = [stepped_slot(bi, pk[k], z[k], z[k + 1], KEYWAY_L / 2, KEYWAY_W / 2, KEYWAY_D, max(z[k], z[k + 1]) + .05)
            for k in range(6)]
    return boolean([cap], cuts, np.array([BS[bi], 0.0, soff]))


def notch_cutter(i, j):
    """Sheets 46-48: at the end-bent end of the span A / E beams the top flange is set back 6 in and its acute half is
    cut parallel to the bent (10 7/8 in more at the flange edge). The cut runs through the flange and its fillet, the
    11 in above the web (sheet 45 section; the notch depth itself is not dimensioned)."""
    ga, gb = first.beam_ends(i, True)
    y = YS[j]
    ue, dirn, acute = (ga, 1.0, -1.0) if i == 0 else (gb, -1.0, 1.0)     # acute half: south at Bent 1, north at Bent 6
    xe, e = g.sx(ue, y), 30 * IN + .05
    poly = [(xe - dirn * .05, y - acute * e), (xe + dirn * NOTCH_SETBACK, y - acute * e), (xe + dirn * NOTCH_SETBACK, y),
            (xe + dirn * (NOTCH_SETBACK + e * T), y + acute * e), (xe - dirn * .05, y + acute * e)]

    def fn(s, px, py):
        z0 = float(soffit(i, j, px - K * y)) + NOTCH_Z
        z1 = float(g.surf(px, py)) - SLAB + .1
        return px, py, (1 - s) * z0 + s * z1
    return first.loft(poly, [0.0, 1.0], fn)


def notched(i, j, mesh):
    """Apply the end-bent flange notch to a span A / E beam or haunch (other spans unchanged)."""
    if i not in (0, 4):
        return mesh
    return boolean([mesh], [notch_cutter(i, j)], np.asarray(mesh.vertices).min(axis=0), snap_to=[mesh])


# ---- Deck ends and approach slabs. ----
def approach(side, length, from_floor_end, ledge_back=second.BACK_FACE):
    """Script 2's approach slab (sheet 32 ledge strips) for a deck of the given length. from_floor_end: the terminal
    joint is at the End of Bridge Floor + the dimensioned edge (sheets 58, 60); otherwise at the joint far side + the
    dimensioned edge (the rule of the first two corrections)."""
    bi = 0 if side < 0 else 5
    start = side * (length / 2 + .025)
    terminal = side * (length / 2 + (0 if from_floor_end else .025) + T * W / 2 + first.APPROACH_SHORT)
    longest = abs(terminal - g.sx(start, side * W / 2))
    s_top = first.bars(0, 1, step=.6 / longest)

    def s_at(n, y):
        x0 = g.sx(start, y)
        return (BS[bi] + side * n / C + K * y - x0) / (terminal - x0)
    ys = [-W / 2, g.crown, W / 2]
    s_far = max(s_at(ledge_back + second.THICK_ZONE, y) for y in ys)
    s_bottom = [s for s in s_top[::-1] if s > s_far + .02]
    sections = []
    for y in ys:
        x0 = g.sx(start, y)
        n1, n2 = s_at(ledge_back, y), s_at(ledge_back + second.THICK_ZONE, y)
        if not 0 < n1 < n2 < s_bottom[-1]:
            raise ValueError('approach: ledge strips out of order')
        pts = [(s, 0.0) for s in s_top] + [(s, -second.SLAB_DEPTH) for s in s_bottom] + \
              [(n2, -second.SLAB_DEPTH), (n2, -second.THICK_DEPTH), (n1, -second.THICK_DEPTH),
               (n1, -second.LEDGE_DEPTH), (0.0, -second.LEDGE_DEPTH)]
        sec = []
        for s, b in pts:
            x = x0 + s * (terminal - x0)
            sec.append((x, y, float(g.surf(x, y)) + b))
        sections.append(np.array(sec))
    return second.loft_sections(sections), terminal


def terminal_station(terminal_x):
    """Station on Line "A" of a square terminal joint at X."""
    return first.CENTRE_STA + (terminal_x + T * first.CROWN) / FT


def stretch(mesh, posts=False, rigid=False, side=0):
    """Deck-end extension by DL: end vertices (u = +/-L/2) move out along X; posts: the end 8-vertex boxes move;
    rigid: every vertex moves (joint strips at one end). Z follows the profile grade."""
    v = np.asarray(mesh.vertices, dtype=float).copy()
    x0 = v[:, 0].copy()
    if rigid:
        v[:, 0] += side * DL
        moved = len(v)
    elif posts:
        moved = 0
        for blk in np.arange(len(v)).reshape(-1, 8):
            uc = (v[blk, 0] - K * v[blk, 1]).mean()
            for sgn in (-1, 1):
                if abs(uc - sgn * L_OLD / 2) < 1e-3:
                    v[blk, 0] += sgn * DL
                    moved += 1
    else:
        u = v[:, 0] - K * v[:, 1]
        moved = 0
        for sgn in (-1, 1):
            sel = np.isclose(u, sgn * L_OLD / 2, atol=1e-4)
            v[sel, 0] += sgn * DL
            moved += int(sel.sum())
    v[:, 2] += first.grade(v[:, 0]) - first.grade(x0)
    return trimesh.Trimesh(vertices=v, faces=np.asarray(mesh.faces), process=False), moved


# ---- New parts: wingwalls and interior support diaphragms. ----
def wing_frame(bi, side):
    sgn = -1.0 if bi == 0 else 1.0             # approach side
    y0, y1 = first.cap_extent(bi)
    y_out = y1 if side > 0 else y0
    y_in = y_out - side * WING_T
    x_end = g.sx(BS[bi] - sgn * END_FACE, y_out) + sgn * WINGS[(bi, side)][1]
    n = max(2, int(abs(x_end - g.sx(BS[bi] + sgn * END_FACE, y_out)) / .6) + 1)

    def along(s, y):                          # from the end-bent back face (s = 0) to the square wing end (s = 1)
        xb = g.sx(BS[bi] + sgn * END_FACE, y)
        return xb + s * (x_end - xb)
    return sgn, y_out, y_in, x_end, np.linspace(0, 1, n), along


def wing(bi, side):
    """Sheets 28/31 SECTION C-C: wall top 1'-2 1/2" + 1" (polystyrene) below the approach-slab top, with a 3 in x 6 in
    keyway centred in the wall top along the wing."""
    sgn, y_out, y_in, x_end, stations, along = wing_frame(bi, side)
    soffit_z = float(first.z_el(first.SOFFIT_EL[bi]))
    ya, yb = sorted((y_in, y_out))
    yc = (y_in + y_out) / 2
    prof = [(ya, 0), (yb, 0), (yb, 1), (yc + WING_KEY_W / 2, 1), (yc + WING_KEY_W / 2, .9), (yc - WING_KEY_W / 2, .9),
            (yc - WING_KEY_W / 2, 1), (ya, 1)]

    def fn(s, y, f):
        x = along(s, y)
        if f == 0:
            return x, y, soffit_z
        return x, y, float(g.surf(x, y)) - WING_TOP_DEPTH - (WING_KEY_D if f < .95 else 0.0)
    return first.loft(prof, stations, fn), x_end, y_out, y_in


def wing_strip(bi, side):
    """Approach slab over a wing (sheets 28/31 C-C): underside 1'-2 1/2" below the top from the wall's inner face to the
    slab edge, with a 5 in tongue into the wall keyway (1/2 in and 1 in polystyrene clearances), from the end-bent
    back face to the wing end. Its top lies 3 mm inside the 1 ft 0 in slab, for the union."""
    sgn, y_out, y_in, x_end, stations, along = wing_frame(bi, side)
    ya, yb = sorted((y_in, side * W / 2))
    yc, tw = (y_in + y_out) / 2, WING_KEY_W / 2 - WING_KEY_SIDE
    prof = [(ya, .5), (yc - tw, .5), (yc - tw, 0), (yc + tw, 0), (yc + tw, .5), (yb, .5), (yb, 1), (ya, 1)]
    depth = {1: second.SLAB_DEPTH - .003, .5: second.LEDGE_DEPTH,
             0: WING_TOP_DEPTH + WING_KEY_D - WING_KEY_BOTTOM}
    s0 = .001 / abs(x_end - along(0.0, y_out))      # start 1 mm beyond the back face: no face on the ledge step plane

    def fn(s, y, f):
        x = along(s0 + (1 - s0) * s, y)
        return x, y, float(g.surf(x, y)) - depth[f]
    return first.loft(prof, stations, fn)


def approach_slab(side):
    """Corrected approach slab: script 2's slab from the corrected floor end plus the C-C strips over its two wings."""
    base, terminal = approach(side, L_NEW, True)
    bi = 0 if side < 0 else 5
    strips = [wing_strip(bi, wside) for wside in (-1, 1)]
    return boolean([base] + strips, [], np.asarray(base.vertices).min(axis=0)), terminal


def diaphragm(bi, out):
    """Sheets 43, 53, 54: 3 ft concrete between the bent faces q = +/-1 ft 6 in, slab soffit to the beam soffits, from
    beam 1 to beam 7, filling the beam-end gaps; beams and haunches subtracted. The soffit stays 3 11/16 in (the
    polystyrene of SECTION E-E BETWEEN BEAMS) above the cap terraces, so it steps on the terrace lines (sheets 35, 39),
    and a key 2 in shorter, 2 in narrower and 1/2 in shallower than each cap keyway drops into it (sheet 54)."""
    zb = [bearing_level(bi, j) for j in range(7)]
    pk = terrace_p(bi)
    mids = [(YS[j] + YS[j + 1]) / 2 for j in range(6)]
    bottom, steps = [(YS[6], zb[6])], set()
    for k in range(5, -1, -1):
        ys = C * pk[k]                        # the terrace line at q = 0; it moves with q (fn)
        pts = [(ys, zb[k + 1]), (ys, zb[k])] if abs(zb[k + 1] - zb[k]) > 1e-9 else [(ys, zb[k])]
        bottom += pts
        steps |= {(round(y, 9), round(z, 9)) for y, z in pts}
    bottom.append((YS[0], zb[0]))
    top_y = sorted(set([float(y) for y in YS] + mids + [g.crown]), reverse=True)
    top0 = [(y, float(g.surf(g.sx(BS[bi], y), y)) - SLAB) for y in top_y]
    split = (max(zb) + min(z for _, z in top0)) / 2

    def fn(t, y, z0):
        if z0 < split and (round(y, 9), round(z0, 9)) in steps:
            y = y - C * K * (t * C)           # constant-p terrace line: y = C (p - K q), q = t C
        x = g.sx(BS[bi] + t, y)
        return x, y, (float(g.surf(x, y)) - SLAB) if z0 > split else z0
    prism = first.loft(bottom + top0, [-DIAPH_HALF / C, DIAPH_HALF / C], fn)
    pieces = [prism]
    for k in range(6):
        # The key's deeper part stops 1 in short of the keyway riser, as at the keyway's other vertical faces (sheet 54
        # polystyrene: 1 in at the sides and ends, 1/2 in under the key).
        pieces.append(stepped_slot(bi, pk[k], seat(bi, k), seat(bi, k + 1), KEYWAY_L / 2 - KEY_FOAM_END,
                                   KEYWAY_W / 2 - KEY_FOAM_SIDE, KEYWAY_D - KEY_FOAM_BOTTOM, max(zb[k], zb[k + 1]) + .002,
                                   riser_shift=KEY_FOAM_END))
    w = 60 * IN
    for j in (0, 6):                         # end gaps of the exterior beams, within their outline
        y = YS[j]
        us = [BS[bi] - GAP - .005, BS[bi] + GAP + .005]
        pieces.append(first.loft(np.array(first.PROFILE) * IN, us, lambda u, v, z, y=y, j=j: (g.sx(u, y), y + v, zb[j] + z)))
        pieces.append(first.loft([(-w / 2, 0), (w / 2, 0), (w / 2, 1), (-w / 2, 1)], us,
                                 lambda u, v, t, y=y, j=j: (g.sx(u, y), y + v, (1 - t) * (zb[j] + D - .005)
                                                            + t * (float(g.surf(g.sx(u, y), y + v)) - SLAB - .001))))
    cutters = []
    for i in (bi - 1, bi):
        ga, gb = first.beam_ends(i, True)
        for j in range(7):
            cutters += [out[f'bulbt_{i}_{j}'], out[f'haunch_{i}_{j}']]
            # Nothing of the diaphragm below a beam soffit (no slivers where the cambered soffit leaves the level).
            u0, u1 = (ga, ga + .6) if i == bi else (gb - .6, gb)
            y = YS[j]
            cutters.append(first.loft([(-12.5 * IN, -.2), (12.5 * IN, -.2), (12.5 * IN, .0005), (-12.5 * IN, .0005)],
                                      np.linspace(u0, u1, 4), lambda u, v, z, i=i, j=j, y=y:
                                      (g.sx(u, y), y + v, float(soffit(i, j, u)) + z)))
    return boolean(pieces, cutters, np.array([BS[bi], 0.0, min(zb)]))


def section_area(cross_section):
    """Shapely area of a manifold3d slice: counter-clockwise contours are outlines, clockwise ones holes."""
    solid, holes = [], []
    for c in cross_section.to_polygons():
        poly = sg.Polygon(c)
        (solid if sg.polygon.orient(poly).exterior.coords[:] == poly.exterior.coords[:] else holes).append(poly.buffer(0))
    area = shapely.ops.unary_union(solid) if solid else sg.Polygon()
    return area.difference(shapely.ops.unary_union(holes)) if holes else area


def stored_closed(mesh):
    """scripts/refresh_geometry_verification.py's test on the mesh as it will be stored: float32 glTF positions, split
    into index-connected bodies, welded at 1e-5 m, each body watertight."""
    v = np.asarray(mesh.vertices, dtype=np.float64)
    stored32 = np.c_[v[:, 0], v[:, 2], -v[:, 1]].astype('<f4').astype(np.float64)
    return all(b.is_watertight for b in refresh_geometry_verification.bodies(stored32, np.asarray(mesh.faces)))


def z_hits(mesh, x, y):
    """Heights where the vertical line through (x, y) crosses the mesh triangles."""
    tri = np.asarray(mesh.vertices)[np.asarray(mesh.faces)]
    a, b, c = tri[:, 0], tri[:, 1], tri[:, 2]
    v0, v1, v2 = c[:, :2] - a[:, :2], b[:, :2] - a[:, :2], np.array([x, y]) - a[:, :2]
    d00, d01, d11 = (v0 * v0).sum(1), (v0 * v1).sum(1), (v1 * v1).sum(1)
    d20, d21 = (v2 * v0).sum(1), (v2 * v1).sum(1)
    den = d00 * d11 - d01 * d01
    ok = np.abs(den) > 1e-9 * d00 * d11            # skip vertical faces (degenerate in plan)
    den = np.where(ok, den, 1.0)
    u, w = (d11 * d20 - d01 * d21) / den, (d00 * d21 - d01 * d20) / den
    sel = ok & (u >= -1e-9) & (w >= -1e-9) & (u + w <= 1 + 1e-9)
    return a[sel, 2] + u[sel] * (c[sel, 2] - a[sel, 2]) + w[sel] * (b[sel, 2] - a[sel, 2])


def overlap(a, b):
    origin = np.asarray(a.vertices).min(axis=0)
    return (first.to_manifold(a, origin) ^ first.to_manifold(b, origin)).volume()


def dump_like(obj, raw, **kw):
    """JSON text with the line endings and final newline of the file it replaces."""
    text = json.dumps(obj, **kw)
    if raw.rstrip(b' \t').endswith(b'\n'):
        text += '\n'
    if b'\r\n' in raw:
        text = text.replace('\n', '\r\n')
    return text.encode('utf-8')


def hex_rgba(color):
    return [int(color[k:k + 2], 16) for k in (1, 3, 5)] + [255]


def correct(base=BASE, backup=BACKUP):
    mp = base / 'model_manifest.json'
    raw_manifest = mp.read_bytes()
    manifest = json.loads(raw_manifest)
    if manifest.get('drawing_review_correction_3') == TAG:
        print('Already corrected.')
        return
    path = base / 'model.glb'
    original = path.read_bytes()
    before = hashlib.sha256(original).hexdigest()
    ledger_path = base / 'source_ledger.json'
    raw_ledger = ledger_path.read_bytes()

    def expect(ok, what):
        if not ok:
            raise ValueError(f'{BID}: {what}')

    expect(manifest.get('drawing_review_correction') == first.TAG and
           manifest.get('drawing_review_correction_2') == second.TAG and manifest.get('revision') == PREVIOUS_REVISION,
           'unexpected starting model (the two earlier corrections are not both applied)')
    expect(before == manifest['drawing_review_correction_2_record']['after_glb_sha256'],
           'unexpected starting model (GLB differs from the second correction)')
    length = struct.unpack_from('<I', original, 12)[0]
    gltf = json.loads(original[20:20 + length])
    binary = bytearray(original[28 + length:])
    parts = {p['id']: p for p in manifest['parts']}
    meshes = {m['name']: m for m in gltf['meshes']}
    expect(set(parts) == set(meshes) and len(parts) == 283, 'unexpected starting model (part list)')

    def read(ai):
        a = gltf['accessors'][ai]
        view = gltf['bufferViews'][a['bufferView']]
        dtype = {5126: '<f4', 5125: '<u4', 5123: '<u2', 5121: 'u1'}[a['componentType']]
        count = {'SCALAR': 1, 'VEC3': 3, 'VEC4': 4}[a['type']]
        return np.frombuffer(binary, dtype=dtype, count=a['count'] * count,
                             offset=view.get('byteOffset', 0) + a.get('byteOffset', 0)).copy().reshape(-1, count)

    def stored(pid):
        prim = meshes[pid]['primitives'][0]
        v = read(prim['attributes']['POSITION']).astype(np.float64)
        return trimesh.Trimesh(vertices=np.c_[v[:, 0], -v[:, 2], v[:, 1]],
                               faces=read(prim['indices']).reshape(-1, 3).astype(np.int64), process=False)

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

    # ---- The rules of this script reproduce the stored parts they replace (old rules / old inputs). ----
    sample = {f'bulbt_{i}_{j}': first.beam(g, i, j) for i in (0, 2, 4) for j in (0, 6)}
    sample.update({f'haunch_{i}_{j}': first.haunch(g, i, j) for i in (1, 3) for j in (0, 3)})
    sample.update({f'approach_{s}': approach(s, L_OLD, False)[0] for s in (-1, 1)})
    for pid, mesh in sample.items():
        expect(first.same_shape(mesh, stored(pid)), f'unexpected starting model ({pid} is not the second-correction geometry)')
    old_peds = {bi: {p for p in parts if p.startswith(f'ped_{bi}_')} for bi in range(6)}

    # ---- 1. Seat schedule: beams, haunches, bearings, pedestals, caps, X frames. ----
    out, removed, decisions, checks = {}, [], {}, {}
    for i in range(5):
        for j in range(7):
            out[f'bulbt_{i}_{j}'] = notched(i, j, beam(i, j))
            out[f'haunch_{i}_{j}'] = notched(i, j, haunch(i, j))
            for e in ('start', 'end'):
                out[f'Span_{chr(65 + i)}_beam_{j + 1}_{e}_bearing'] = bearing(i, j, e)
    flats = {}
    for bi in range(6):
        new_peds, flats[bi] = peds(bi)
        expect(set(new_peds) <= old_peds[bi], f'ped_{bi}_*: the schedule needs a pedestal the model lacks')
        out.update(new_peds)
        removed += sorted(old_peds[bi] - set(new_peds))
    # Depth chains that tie the seats to the drawn bent geometry (lowest seat of each bent).
    chains = {1: (5 + 1.125 / 12, 'sheet 35 END ELEVATION Bent 2 5\'-1 1/8"'),
              4: (5 + 1.5 / 12, 'sheet 35 END ELEVATION Bent 5 5\'-1 1/2"'),
              0: (2 + 8.25 / 12 + 7 / 12, 'sheet 32 SECTION B-B 2\'-8 1/4" + 7" at Bent 1'),
              5: (2 + 7.875 / 12 + 7 / 12, 'sheet 32 SECTION B-B 2\'-7 7/8" + 7" at Bent 6')}
    for bi, (depth_ft, label) in chains.items():
        err = min(SEAT_EL[bi]) - (first.SOFFIT_EL[bi] + depth_ft)
        expect(abs(err) < .006, f'{label} does not close on the lowest seat ({err:+.4f} ft)')
        checks[f'lowest seat minus ({label}) ft'] = round(err, 4)
    for bi in range(1, 5):
        out[f'cap_{bi}'] = terraced_cap(bi)
    for i in range(5):
        for j in range(6):
            pid = f'xframe_{i}_{j}'
            m = stored(pid)
            lo, hi = m.bounds
            expect(YS[j + 1] < lo[1] and hi[1] < YS[j], f'{pid}: not between beams {j + 1} and {j + 2}')
            uc = (lo[0] + hi[0]) / 2 - K * (lo[1] + hi[1]) / 2
            dz = np.mean([float(soffit(i, jj, uc)) - float(g.beam_bottom(uc, YS[jj])) for jj in (j, j + 1)])
            out[pid] = trimesh.Trimesh(vertices=m.vertices + [0, 0, dz], faces=m.faces, process=False)

    # ---- 4. Deck ends and 5. approach terminals. ----
    moved = {}
    for pid in ('deck', 'sidewalk', 'ft_rail', 'ps1_base', 'ps1_beam_0', 'ps1_beam_1'):
        out[pid], moved[pid] = stretch(stored(pid))
    out['ps1_posts'], moved['ps1_posts'] = stretch(stored('ps1_posts'), posts=True)
    for s in (-1, 1):
        out[f'joint_{s}'], moved[f'joint_{s}'] = stretch(stored(f'joint_{s}'), rigid=True, side=s)
    expect(moved == {'deck': 12, 'sidewalk': 8, 'ft_rail': 10, 'ps1_base': 8, 'ps1_beam_0': 8, 'ps1_beam_1': 8,
                     'ps1_posts': 2, 'joint_-1': 12, 'joint_1': 12}, f'unexpected deck-end vertices {moved}')
    terminals = {}
    for s in (-1, 1):
        out[f'approach_{s}'], terminals[s] = approach_slab(s)
    for bi, s in ((0, -1), (5, 1)):
        i, e = (0, 'start') if bi == 0 else (4, 'end')
        groups = []
        for j in range(7):
            pad = out[f'Span_{chr(65 + i)}_beam_{j + 1}_{e}_bearing'].bounds
            grp = [out[f'bulbt_{i}_{j}'], notched(i, j, haunch(i, j, lift=.05, drop=.02)),
                   first.box(*pad[:, 0], *pad[:, 1], pad[0, 2], pad[1, 2] + .01)]
            if f'ped_{bi}_{j}_0' in out:
                ped = out[f'ped_{bi}_{j}_0'].copy()
                ped.vertices[np.isclose(ped.vertices[:, 2], ped.vertices[:, 2].max()), 2] += .005
                grp.append(ped)
            groups.append(grp)
        groups.append([approach(s, L_NEW, True, ledge_back=second.BACK_FACE + .15)[0]])
        out[f'cap_{bi}'] = first.end_body(g, bi, groups)

    # ---- 2. Diaphragms and 3. wingwalls (new parts). ----
    added, wing_info = {}, {}
    for bi in range(1, 5):
        added[f'diaphragm_{bi}'] = diaphragm(bi, out)
    for (bi, side) in WINGS:
        m, x_end, y_out, y_in = wing(bi, side)
        added[f'wing_{bi}_{side}'] = m
        wing_info[(bi, side)] = (x_end, y_out, y_in)
    for pid, m in {**out, **added}.items():
        expect(m.is_watertight and m.is_winding_consistent and m.volume > 0, f'{pid}: corrected mesh invalid')
        expect(stored_closed(m), f'{pid}: not a closed 2-manifold as stored (refresh_geometry_verification check)')

    # ---- Interfaces. ----
    worst = dict(bearing_top=0.0, ped_top=0.0, ped_bottom=0.0, seat=0.0)
    for i in range(5):
        for j in range(7):
            for e in ('start', 'end'):
                bi = i if e == 'start' else i + 1
                b = out[f'Span_{chr(65 + i)}_beam_{j + 1}_{e}_bearing']
                u = first.bearing_u(i, e)
                v = b.vertices
                up = v[v[:, 2] > b.bounds[0, 2] + ANCHOR_T / 2]
                uu = up[:, 0] - K * YS[j]
                ga, gb = first.beam_ends(i, True)
                want = soffit(i, j, uu)
                want = np.where((uu < ga) | (uu > gb), np.minimum(want, bearing_level(bi, j)), want)
                worst['bearing_top'] = max(worst['bearing_top'], float(np.abs(up[:, 2] - want).max()))
                # Interior: pad bottom on the seat. End bents: beam soffit (bar top at its centre line) on the seat.
                top_c = float(soffit(i, j, u))
                worst['seat'] = max(worst['seat'], abs((top_c if bi in (0, 5) else b.bounds[0, 2]) - seat(bi, j)))
    for bi in range(6):
        for pid in (p for p in out if p.startswith(f'ped_{bi}_')):
            j = int(pid.split('_')[2])
            worst['ped_top'] = max(worst['ped_top'], abs(out[pid].bounds[1, 2] - ped_top(bi, j)))
            worst['ped_bottom'] = max(worst['ped_bottom'], abs(out[pid].bounds[0, 2] - flats[bi]))
    expect(max(worst.values()) < 1e-6, f'seat stack not closed {worst}')
    checks['seat stack closure m'] = {k: float(f'{v:.2e}') for k, v in worst.items()}
    # Haunch depth at the beam centre line and at the flange edges (sheet 23: top of beam 3/4 in min below the slab).
    hmin_c, hmin_e = 9.0, 9.0
    for i in range(5):
        ga, gb = first.beam_ends(i, True)
        us = np.linspace(ga, gb, 120)
        for j in range(7):
            y = YS[j]
            topb = soffit(i, j, us) + D
            x = g.sx(us, y)
            hmin_c = min(hmin_c, float((g.surf(x, y) - SLAB - topb).min()))
            hmin_e = min(hmin_e, float((np.minimum(g.surf(x, y - 30 * IN), g.surf(x, y + 30 * IN)) - SLAB - topb).min()))
    expect(hmin_e > .75 * IN, 'a beam comes closer than 3/4 in to the slab')
    checks['minimum haunch at beam centre line in'] = round(hmin_c / IN, 3)
    checks['minimum haunch at flange edge in'] = round(hmin_e / IN, 3)
    # Overlaps of the new and changed solids with their neighbours.
    deck = out['deck']
    ov = {}
    for bi in range(1, 5):
        dpid = f'diaphragm_{bi}'
        nb = [f'bulbt_{i}_{j}' for i in (bi - 1, bi) for j in range(7)] + \
             [f'haunch_{i}_{j}' for i in (bi - 1, bi) for j in range(7)] + [f'cap_{bi}']
        ov[dpid] = max(overlap(added[dpid], out[p]) for p in nb)
        ov[f'{dpid}/deck'] = overlap(added[dpid], deck)
    for (bi, side) in WINGS:
        wpid = f'wing_{bi}_{side}'
        ov[wpid] = max(overlap(added[wpid], out[p]) for p in (f'cap_{bi}', f'approach_{-1 if bi == 0 else 1}'))
    terrace_gap = 0.0
    for bi in range(1, 5):
        cap = out[f'cap_{bi}']
        for i, e in ((bi - 1, 'end'), (bi, 'start')):
            for j in range(7):
                pad = out[f'Span_{chr(65 + i)}_beam_{j + 1}_{e}_bearing']
                ov['pad / terraced cap'] = max(ov.get('pad / terraced cap', 0.0), overlap(pad, cap))
                c = pad.vertices.mean(axis=0)
                for dx, dy in ((0, 0), (.25, .25), (-.25, -.25), (.25, -.25), (-.25, .25)):
                    zt = z_hits(cap, c[0] + dx, c[1] + dy)                         # cap top under the pad
                    terrace_gap = max(terrace_gap, abs(zt.max() - pad.bounds[0, 2]))
    checks['pad bottom minus cap terrace top under it m'] = float(f'{terrace_gap:.2e}')
    # Key-to-keyway clearances, measured on horizontal slices of the solids: plan gap at levels inside the keyway (sides,
    # ends and the riser of the stepped bottom) and the vertical gap under the key.
    plan_gap, under_gap = 9.0, 9.0
    for bi in range(1, 5):
        origin = np.array([BS[bi], 0.0, 0.0])
        dm, cm = first.to_manifold(added[f'diaphragm_{bi}'], origin), first.to_manifold(out[f'cap_{bi}'], origin)
        pk = terrace_p(bi)
        for k in range(6):
            lo, hi = sorted((seat(bi, k), seat(bi, k + 1)))
            centre = sg.Point(*(first.bent_point(bi, pk[k], 0.0) - origin[:2]))
            for z in np.linspace(lo - KEYWAY_D + KEY_FOAM_BOTTOM + .001, hi - .001, 6):
                key = section_area(dm.slice(z)).intersection(centre.buffer(KEYWAY_L))
                cap = section_area(cm.slice(z))
                if not key.is_empty:
                    plan_gap = min(plan_gap, key.distance(cap))
            for side, j in ((.3, k), (-.3, k + 1)):
                px, py = first.bent_point(bi, pk[k] + side, 0.0)
                under_gap = min(under_gap, float(z_hits(added[f'diaphragm_{bi}'], px, py).min() - z_hits(out[f'cap_{bi}'], px, py).max()))
    expect(plan_gap > KEY_FOAM_SIDE - 1e-4 and under_gap > KEY_FOAM_BOTTOM - 1e-4,
           f'key clearances {plan_gap:.4f} / {under_gap:.4f} m')
    checks['diaphragm key to cap keyway: least plan clearance (sides, ends, riser) in'] = round(plan_gap / IN, 3)
    checks['diaphragm key to cap keyway: least clearance under the key in'] = round(under_gap / IN, 3)
    expect(terrace_gap < 1e-6, f'pads not on the cap terraces ({terrace_gap:.2e} m)')
    for bi, s in ((0, -1), (5, 1)):
        ov[f'cap_{bi}/approach_{s}'] = overlap(out[f'cap_{bi}'], out[f'approach_{s}'])
        ov[f'cap_{bi}/deck'] = overlap(out[f'cap_{bi}'], deck)
    for i in range(5):
        for j in range(7):
            b = out[f'bulbt_{i}_{j}']
            ov['haunch / beam'] = max(ov.get('haunch / beam', 0.0), overlap(out[f'haunch_{i}_{j}'], b))
            for e in ('start', 'end'):
                ov['bearing / beam'] = max(ov.get('bearing / beam', 0.0),
                                           overlap(out[f'Span_{chr(65 + i)}_beam_{j + 1}_{e}_bearing'], b))
    xf_old, xf_new = 0.0, 0.0
    for i in range(5):
        for j in range(6):
            for jj in (j, j + 1):
                xf_old = max(xf_old, overlap(stored(f'xframe_{i}_{j}'), stored(f'bulbt_{i}_{jj}')))
                xf_new = max(xf_new, overlap(out[f'xframe_{i}_{j}'], out[f'bulbt_{i}_{jj}']))
    ov['X frame / beam'] = xf_new
    checks['X frame / beam overlap before m3'] = float(f'{xf_old:.2e}')
    limit = {k: (2e-3 if k.endswith('/deck') else 1.05 * xf_old if k == 'X frame / beam' else 2e-5) for k in ov}
    expect(all(ov[k] <= limit[k] for k in ov), f'overlaps {ov}, X frame before {xf_old:.2e}')
    checks['largest overlap m3'] = {k: float(f'{v:.2e}') for k, v in ov.items()}
    # End-bent flange notches: the top flange now stops inside the End of Bridge Floor (1'-4 1/2" from the bent).
    reach, ov_beam, ov_haunch = -9.0, 0.0, 0.0
    for bi, i, s in ((0, 0, -1), (5, 4, 1)):
        for j in range(7):
            v = out[f'bulbt_{i}_{j}'].vertices
            top = v[v[:, 2] > soffit(i, j, v[:, 0] - K * YS[j]) + NOTCH_Z + .005]
            q = (top[:, 0] - BS[bi] - K * top[:, 1]) * C
            reach = max(reach, float((s * q).max()) - (1 + 4.5 / 12) * FT)
            ov_beam = max(ov_beam, overlap(out[f'bulbt_{i}_{j}'], out[f'approach_{s}']))
            ov_haunch = max(ov_haunch, overlap(out[f'haunch_{i}_{j}'], out[f'approach_{s}']))
    expect(reach < 0 and max(ov_beam, ov_haunch) < 1e-6, f'end-bent flanges still reach the approach ({reach:.4f} m)')
    checks['end-bent top flange beyond the End of Bridge Floor m (negative = inside)'] = round(reach, 4)
    checks['end-bent beam / haunch overlap with the approach slab m3'] = [float(f'{ov_beam:.2e}'), float(f'{ov_haunch:.2e}')]

    # Wing contacts and top levels against the written elevations.
    wing_rows = {}
    for (bi, side), (x_end, y_out, y_in) in wing_info.items():
        m = added[f'wing_{bi}_{side}']
        v = m.vertices
        tip = v[np.isclose(v[:, 0], x_end, atol=1e-6) & np.isclose(v[:, 1], y_out, atol=1e-6)]
        top_el = 450 + tip[:, 2].max() / FT
        name, length_w, top_written, slab_written = WINGS[(bi, side)]
        # The written top of wing equals the written slab top + grade to the wing end - 1'-2 1/2", i.e. the slab underside
        # over the wall (top of the 1 in polystyrene) of SECTION C-C.
        derived = (slab_written + (float(first.grade(x_end)) - float(first.grade(g.sx(BS[bi], y_out)))) / FT
                   - second.LEDGE_DEPTH / FT)
        back = v[np.isclose(v[:, 0] - K * v[:, 1], BS[bi] + (-1 if bi == 0 else 1) * END_FACE, atol=1e-6)]
        wing_rows[f'wing_{bi}_{side}'] = dict(
            plan_name=name, top_el_at_end_ft=round(top_el, 3), written_top_el_ft=top_written,
            written_minus_model_ft=round(top_written - top_el, 3),
            written_slab_relation_error_ft=round(top_written - derived, 3), back_face_vertices=int(len(back)),
            beyond_back_face_m=round(abs(x_end - g.sx(BS[bi] + (-1 if bi == 0 else 1) * END_FACE, y_out)), 6))
        expect(abs(top_written - derived) < .01, f'wing_{bi}_{side}: written relation to the slab top broken')
        expect(len(back) == 8, f'wing_{bi}_{side}: back face not on the end-bent back face')
    checks['wingwalls'] = wing_rows
    stations = {s: round(terminal_station(terminals[s]), 3) for s in (-1, 1)}
    expect(abs(stations[-1] - 38634.06) < .02, f'west terminal {stations[-1]}')
    checks['terminal joint stations on Line A'] = {'west (callout 386+34.06)': stations[-1],
                                                    'east (callouts 391+92.68 / 391+92.86)': stations[1]}

    # ---- Manifest. ----
    def note(pid, text):
        p = parts[pid]
        p['note'] = (p.get('note', '') + ' ' + text).strip()

    def add_pages(pid, *pages):
        parts[pid]['pdf_pages'] = sorted(set(parts[pid].get('pdf_pages', [])) | set(pages))

    seat_note = ('Rev. 1.3: seat schedule imposed (sheets 26, 29, 35, 39): beam soffit on the chord between the scheduled '
                 'bearings (seat + 3 11/16 in T1 pad at Bents 2-5, sheet 54; seat at the end bents, sheet 32) plus the '
                 'sheet 45 residual camber at midspan as a parabola; was parallel to the profile 0.10 m below the slab.')
    for i in range(5):
        for j in range(7):
            pid = f'bulbt_{i}_{j}'
            parts[pid]['dimensions'].update(residual_camber_midspan_m=round(float(CAMBER[i]), 6),
                                            soffit_start_el_ft=round(450 + bearing_level(i, j) / FT, 4),
                                            soffit_end_el_ft=round(450 + bearing_level(i + 1, j) / FT, 4))
            parts[pid]['basis'] = ('Dimensioned 66 in Bulb-T section (sheet 45) on the scheduled seats; residual camber '
                                   'parabolic between bearings (midspan value, sheet 45); square ends (sheets 43, 45)')
            parts[pid]['note'] = parts[pid]['note'].replace('Camber and threaded inserts omitted.', 'Threaded inserts omitted.')
            note(pid, seat_note)
            add_pages(pid, 112, 115, 121, 125, 131)
            hid = f'haunch_{i}_{j}'
            ga, gb = first.beam_ends(i, True)
            us = np.linspace(ga, gb, 120)
            hc = g.surf(g.sx(us, YS[j]), YS[j]) - SLAB - soffit(i, j, us) - D
            parts[hid]['dimensions'].pop('nominal_thickness_m', None)
            parts[hid]['dimensions'].update(thickness='variable: beam top to slab soffit',
                                            thickness_at_beam_centre_line_min_m=round(float(hc.min()), 6),
                                            thickness_at_beam_centre_line_max_m=round(float(hc.max()), 6))
            parts[hid]['basis'] = 'Derived from the scheduled beam seats and the slab soffit'
            parts[hid]['note'] = parts[hid]['note'].replace(
                'Haunch follows modeled grade, not a construction screed or camber table. ', '')
            note(hid, 'Rev. 1.3: from the corrected beam top to the slab soffit (variable fillet, sheet 23 SEAT '
                      'ELEVATIONS note); was a uniform 0.10 m.')
            add_pages(hid, 109)
            for e in ('start', 'end'):
                bi = i if e == 'start' else i + 1
                pid = f'Span_{chr(65 + i)}_beam_{j + 1}_{e}_bearing'
                p = parts[pid]
                if bi in (0, 5):
                    p['dimensions'] = dict(bar_length_along_beam_m=round(ANCHOR_ALONG, 6),
                                           bar_width_across_beam_m=round(ANCHOR_ACROSS, 6),
                                           bar_thickness_m=round(ANCHOR_T, 6), seat_el_ft=SEAT_EL[bi][j])
                    p['basis'] = 'Anchor bar 6 in x 1 in under the beam (sheet 32 ANCHOR PLATE DETAIL); studs omitted'
                    note(pid, f'Rev. 1.3: replaced the 2.5 in pad envelope by the end-bent anchor bar; beam soffit on '
                              f'the scheduled seat El. {SEAT_EL[bi][j]:.3f} (sheet {SEAT_SHEET[bi]}), encased in the '
                              'end bent; bar length 2 ft 1 in bulb + 3 in minimum each side.')
                    add_pages(pid, 112 if bi == 0 else 115, 118, 131)
                else:
                    p['dimensions'] = dict(pad_length_m=round(PAD_X, 6), pad_width_m=round(PAD_Y, 6),
                                           pad_thickness_m=round(PAD_T1, 6), seat_el_ft=SEAT_EL[bi][j])
                    p['basis'] = 'Type T1 elastomeric pad envelope, 3 11/16 in (sheet 54); laminations omitted'
                    note(pid, f'Rev. 1.3: on the scheduled seat El. {SEAT_EL[bi][j]:.3f} (sheet {SEAT_SHEET[bi]}), '
                              '3 11/16 in Type T1 pad (sheet 54 SECTION E-E AT BEAMS); was a 2.5 in pad and plate '
                              'under the profile-parallel beam.')
                    add_pages(pid, 121 if bi in (1, 4) else 125, 140)
    for bi in range(6):
        for pid in (p for p in out if p.startswith(f'ped_{bi}_')):
            j = int(pid.split('_')[2])
            parts[pid]['dimensions'] = dict(seat_el_ft=SEAT_EL[bi][j], step_height_m=round(ped_top(bi, j) - flats[bi], 6))
            if bi in (0, 5):
                parts[pid]['basis'] = 'Derived seat step under the anchor bar, encased in the end bent'
                note(pid, f'Rev. 1.3: top at the scheduled seat El. {SEAT_EL[bi][j]:.3f} less the 1 in anchor bar '
                          f'(sheets {SEAT_SHEET[bi]}, 32).')
            else:
                parts[pid]['basis'] = 'Seat step of the cap top, half the cap width (one bearing row)'
                note(pid, f'Rev. 1.3: scheduled seat El. {SEAT_EL[bi][j]:.3f} for both rows (sheet {SEAT_SHEET[bi]}); '
                          'spans its half of the 4 ft 6 in cap, meeting the other row at the bent centre line (the two '
                          'rows had overlapped there).')
            add_pages(pid, 112 if bi == 0 else 115 if bi == 5 else 121 if bi in (1, 4) else 125)
    for bi in range(1, 5):
        pid = f'cap_{bi}'
        parts[pid]['dimensions'].pop('seat_top_el_ft', None)
        parts[pid]['dimensions'].update(
            terrace_top_el_ft_beam_1_to_7=SEAT_EL[bi],
            terrace_steps_from_north_end_ft=[round(float(d), 4) for d in TERRACE_STEPS_FT],
            keyways='6 x 3 in deep x 1 ft 0 in x 8 ft 9 in, centred on the terrace steps, 3 in below each terrace')
        parts[pid]['basis'] = ('Dimensioned 74 ft 3 in x 4 ft 6 in rectangular cap (sheet 34) with the seat terraces '
                               '(sheets 35, 39) and keyways (sheets 35, 39, 54)')
        note(pid, f'Rev. 1.3: top terraced to the scheduled seats El. {min(SEAT_EL[bi]):.3f}-{max(SEAT_EL[bi]):.3f} with '
                  'the sheet 35/39 "Seat Dim\'s" steps (9 ft 3 3/4 in, 5 x 11 ft 6 1/4 in, 7 ft 4 in from the north end; '
                  'the lowest terrace closes on the 5 ft 1 1/8 in / 5 ft 1 1/2 in cap depths of sheets 35, 39) and a '
                  '3 in x 1 ft 0 in x 8 ft 9 in keyway centred on each step (sheets 35, 39, 54); the bearing pads sit on '
                  'the terraces. Was flat at the lowest bearing with separate pedestals.')
        add_pages(pid, 121 if bi in (1, 4) else 125, 140)
    for bi in (0, 5):
        pid = f'cap_{bi}'
        parts[pid]['note'] = parts[pid]['note'].replace(' Wingwalls not modelled.', '')
        note(pid, 'Rev. 1.3: pockets re-cut for the beams on the scheduled seats (beam soffit = seat, sheets 26, 29, '
                  '32) and the corrected deck end; wingwalls are the separate parts wing_' + str(bi) + '_-1 / wing_'
                  + str(bi) + '_1.')
    for i in range(5):
        for j in range(6):
            note(f'xframe_{i}_{j}', 'Rev. 1.3: moved vertically with the beams on the scheduled seats.')
    for i in (0, 4):
        for j in range(7):
            pid = f'bulbt_{i}_{j}'
            parts[pid]['dimensions'].update(end_bent_flange_setback_m=round(NOTCH_SETBACK, 6),
                                            end_bent_acute_half_extra_cut_m=round(NOTCH_SKEW, 6),
                                            end_bent_notch_depth_m=round(D - NOTCH_Z, 6))
            parts[pid]['basis'] = parts[pid]['basis'].replace('square ends (sheets 43, 45)',
                                                              'square ends with the end-bent flange notch (sheets 43, 45-48)')
            note(pid, f'Rev. 1.3: at the {"Bent 1" if i == 0 else "Bent 6"} end the top flange is set back 6 in and its '
                      f'acute ({"south" if i == 0 else "north"}) half is cut parallel to the bent, 10 7/8 in more at the '
                      'flange edge (sheets 46-48); the cut is taken through the flange and fillet (11 in, sheet 45 '
                      'section; depth not dimensioned). The flange now stops inside the End of Bridge Floor.')
            add_pages(pid, 132, 133 if i == 0 else 134)
            note(f'haunch_{i}_{j}', 'Rev. 1.3: cut back with the end-bent flange notch (sheets 46-48).')
            add_pages(f'haunch_{i}_{j}', 132, 133 if i == 0 else 134)
    parts['deck']['dimensions']['length_m'] = round(L_NEW, 6)
    note('deck', 'Rev. 1.3: ends moved out 9.525 mm to 492 ft 0 7/8 in, 1 ft 5 1/2 in from the end-bent centre lines '
                 'along Line "A" (sheets 20-22, 32); was 492 ft 0 1/8 in.')
    add_pages('deck', 106, 118)
    for pid in ('sidewalk', 'ft_rail', 'ps1_base', 'ps1_beam_0', 'ps1_beam_1'):
        note(pid, 'Rev. 1.3: stretched 9.525 mm at each end with the corrected deck ends (sheets 20-22).')
    note('ps1_posts', 'Rev. 1.3: the two end posts moved 9.525 mm with the corrected deck ends (sheets 20-22).')
    for s in (-1, 1):
        note(f'joint_{s}', 'Rev. 1.3: moved 9.525 mm with the corrected deck end (sheets 20-22).')
        pid = f'approach_{s}'
        parts[pid]['dimensions'].update(edges_measured_from='End of Bridge Floor (the first 25 mm is the visual joint)',
                                        terminal_station_line_a=stations[s])
        note(pid, 'Rev. 1.3: over each wingwall the underside is 1 ft 2 1/2 in below the top, from the wall inner face to '
                  'the slab edge and from the end-bent back face to the wing end, with a 5 in tongue into the 3 in x 6 in '
                  'wall keyway (sheets 28/31 SECTION C-C); the 1 in, 1/2 in and 1 in polystyrene layers are left as gaps, '
                  'and the strips start 1 mm beyond the end-bent back face (keeps the solid clean).')
        note(pid, f'Rev. 1.3: edges measured from the End of Bridge Floor (sheets 58, 60), the first 25 mm taken by the '
                  f'visual joint; terminal joint at Sta. {int(stations[s] // 100)}+{stations[s] % 100:05.2f} "A" '
                  f'(callout {"386+34.06" if s < 0 else "391+92.68 sheet 60 / 391+92.86 sheet 22"}).')
        add_pages(pid, 106 if s < 0 else 108)

    new_parts = {}
    color_d, color_w = bridge_geometry.COLORS['diaphragms'], bridge_geometry.COLORS['abutments']
    for bi in range(1, 5):
        pid = f'diaphragm_{bi}'
        zb = [bearing_level(bi, j) for j in range(7)]
        new_parts[pid] = dict(
            id=pid, name=f'Bent {bi + 1} | concrete support diaphragm', layer='diaphragms', color=color_d,
            pdf_pages=[121 if bi in (1, 4) else 125, 129, 139, 140],
            basis='Dimensioned 3 ft diaphragm with keys (sheets 43, 53, 54); polystyrene left as gaps',
            note=('Pours over continuous supports include diaphragms (sheet 54 FLOOR NOTES). 3 ft 0 in normal to the bent, '
                  '1 ft 6 in each side of the centre line and 9 in inside the cap faces (sheet 43 BEARING DETAIL, sheet '
                  '54 SECTION E-E); from the slab soffit down to the beam soffits, between the inner faces of beams 1 and 7 '
                  '(sheet 53 SECTION A-A), encasing the beam ends and filling the 6 in gap between them. The soffit stays '
                  '3 11/16 in above the cap terraces (the polystyrene of SECTION E-E BETWEEN BEAMS), stepping on the '
                  'terrace lines; six 10 in x 8 ft 7 in keys drop into the cap keyways to 1/2 in above their bottoms '
                  '(1 in clearance at the sides and ends, sheet 54). Outside the exterior beams the end-gap fill stops 1 mm '
                  'below the slab soffit (keeps the solid clean).'),
            dimensions=dict(thickness_normal_to_bent_m=round(2 * DIAPH_HALF, 6),
                            soffit_el_ft_beam_1_to_7=[round(450 + z / FT, 4) for z in zb],
                            keys='6 x 10 in x 8 ft 7 in, bottom 2 1/2 in below the terrace tops',
                            extent='inner faces of beams 1 and 7; beam-end gaps filled within the beam outline'))
    for (bi, side), (x_end, y_out, y_in) in wing_info.items():
        pid = f'wing_{bi}_{side}'
        name, length_w, top_written, slab_written = WINGS[(bi, side)]
        row = wing_rows[pid]
        new_parts[pid] = dict(
            id=pid, name=f'Bent {bi + 1} | {name} wingwall', layer='abutments', color=color_w,
            pdf_pages=WING_PAGES[bi] + [118],
            basis='Dimensioned 1 ft 3 in wingwall with top keyway (sheets 26/29 plan, 28/31 elevation and section C-C)',
            note=(f'{name.capitalize()} wing: 1 ft 3 in thick, outer face continuing the end-bent end parallel to the '
                  f'roadway (2 in inside the coping), {"14 ft 0 in" if length_w > 13.9 * FT else "13 ft 6 1/2 in"} from '
                  f'the end-bent front face to the square end along the outer face, i.e. '
                  f'{"10 ft 0 1/8 in" if length_w > 13.9 * FT else "9 ft 6 5/8 in"} beyond the back face (sheets '
                  f'{"26, 28" if bi == 0 else "29, 31"}). Bottom at the end-bent soffit El. {first.SOFFIT_EL[bi]}. '
                  'SECTION C-C: the approach slab, thickened to 1 ft 2 1/2 in over the wall, sits on 1 in polystyrene on '
                  'the wall top, which is therefore 1 ft 3 1/2 in below the slab top, with a 3 in x 6 in keyway centred '
                  'in it for the slab tongue (polystyrene left as gaps). The written top of wing El. '
                  f'{top_written:.2f} equals the written slab top El. {slab_written:.2f} + grade - 1 ft 2 1/2 in, i.e. the '
                  'slab underside, and those slab values place the crown on the structure centre line instead of Line "A"; '
                  f'the modelled wall top is {row["written_minus_model_ft"]:+.2f} ft from the written value.'),
            dimensions=dict(thickness_m=round(WING_T, 6), outer_face_length_from_front_face_m=round(length_w, 6),
                            projection_beyond_back_face_m=row['beyond_back_face_m'], outer_face_y_m=round(y_out, 6),
                            bottom_el_ft=first.SOFFIT_EL[bi], top_below_approach_top_m=round(WING_TOP_DEPTH, 6),
                            keyway='3 in deep x 6 in, centred in the wall top, full length beyond the back face',
                            top_el_at_end_ft=row['top_el_at_end_ft'], written_top_el_at_end_ft=top_written,
                            plan_name=f'{name} wing'))

    # ---- Write the GLB: changed meshes re-pointed, new meshes and nodes appended, removed ones dropped. ----
    def write_mesh(prim, m, rgba):
        v = np.asarray(m.vertices, dtype=np.float64)
        prim['attributes'] = {'POSITION': append(np.c_[v[:, 0], v[:, 2], -v[:, 1]].astype('<f4'), 'VEC3', 5126),
                              'COLOR_0': append(np.tile(rgba, (len(v), 1)).astype('u1'), 'VEC4', 5121)}
        gltf['accessors'][prim['attributes']['COLOR_0']]['normalized'] = True
        prim['indices'] = append(np.asarray(m.faces).reshape(-1, 1).astype('<u4'), 'SCALAR', 5125)

    for pid, m in out.items():
        prim = meshes[pid]['primitives'][0]
        write_mesh(prim, m, read(prim['attributes']['COLOR_0'])[0])
        p = parts[pid]
        p['bounds_m'] = np.round(m.bounds, 6).tolist()
        p['volume_m3'] = round(float(m.volume), 9)
        meshes[pid]['extras'].update({k: p[k] for k in ('name', 'basis', 'note', 'dimensions', 'pdf_pages')})
    world = gltf['nodes'][0]
    for pid, m in added.items():
        p = new_parts[pid]
        p['bounds_m'] = np.round(m.bounds, 6).tolist()
        p['volume_m3'] = round(float(m.volume), 9)
        prim = dict(attributes={}, mode=4)
        write_mesh(prim, m, hex_rgba(p['color']))
        gltf['meshes'].append(dict(name=pid, extras=dict(processed=True, **{k: p[k] for k in (
            'id', 'name', 'layer', 'color', 'pdf_pages', 'basis', 'note', 'dimensions')}), primitives=[prim]))
        gltf['nodes'].append(dict(name=pid, mesh=len(gltf['meshes']) - 1))
        world['children'].append(len(gltf['nodes']) - 1)
    gone = set(removed)
    mesh_map, kept_meshes = {}, []
    for k, m in enumerate(gltf['meshes']):
        if m['name'] not in gone:
            mesh_map[k] = len(kept_meshes)
            kept_meshes.append(m)
    node_map, kept_nodes = {}, []
    for k, n in enumerate(gltf['nodes']):
        if n.get('name') in gone and 'mesh' in n:
            continue
        node_map[k] = len(kept_nodes)
        if 'mesh' in n:
            n['mesh'] = mesh_map[n['mesh']]
        kept_nodes.append(n)
    for n in kept_nodes:
        if 'children' in n:
            n['children'] = [node_map[c] for c in n['children'] if c in node_map]
    gltf['meshes'], gltf['nodes'] = kept_meshes, kept_nodes
    gltf['scenes'] = [dict(s, nodes=[node_map[c] for c in s['nodes']]) for s in gltf['scenes']]

    while len(binary) % 4:
        binary.append(0)
    gltf['buffers'][0]['byteLength'] = len(binary)
    encoded = json.dumps(gltf, ensure_ascii=True, separators=(',', ':')).encode()
    encoded += b' ' * ((-len(encoded)) % 4)
    result = (struct.pack('<III', 0x46546c67, 2, 28 + len(encoded) + len(binary)) +
              struct.pack('<II', len(encoded), 0x4e4f534a) + encoded + struct.pack('<II', len(binary), 0x004e4942) + binary)
    backup.mkdir(parents=True, exist_ok=True)
    (backup / f'{BID}_before_review_correction_3.glb').write_bytes(original)
    (backup / f'{BID}_manifest_before_review_correction_3.json').write_bytes(raw_manifest)
    (backup / f'{BID}_source_ledger_before_review_correction_3.json').write_bytes(raw_ledger)
    path.write_bytes(result)

    # Parts list: new parts after their bent's cap, removed pedestals dropped.
    plist = []
    for p in manifest['parts']:
        if p['id'] in gone:
            continue
        plist.append(p)
        if p['id'].startswith('cap_'):
            bi = int(p['id'][4:])
            plist += [new_parts[k] for k in ([f'diaphragm_{bi}'] if 1 <= bi <= 4 else [f'wing_{bi}_-1', f'wing_{bi}_1'])]
    manifest['parts'] = plist
    used = {p['layer'] for p in plist}
    manifest['layers'] = {k: v for k, v in bridge_geometry.LABELS.items() if k in used}
    manifest['deck_length_m'] = round(L_NEW, 6)
    for c in manifest.get('detail_coverage', []):
        c['part_ids'] = [x for x in c['part_ids'] if x not in gone]
        if c['feature'] == 'Bents and bearings':
            c['part_ids'] += sorted(added)
            c['detail'] += (' Rev. 1.3: scheduled seats on terraced caps with keyways, T1 pads / anchor bars, keyed 3 ft '
                            'concrete support diaphragms at Bents 2-5 and the four end-bent wingwalls added.')
        if c['feature'] == 'Missing exterior details':
            c['detail'] = ('Drainage, lighting, local sidewalk ramps, concrete surface recesses, expanded polystyrene '
                           'fillers and shop camber remain unresolved (beams carry the sheet 45 residual camber only).')
    manifest['drawing_review_correction_3'] = TAG
    manifest['revision'] = REVISION
    decisions.update({
        'wingwall top': 'SECTION C-C (sheets 28, 31) governs the stack: slab top - 1\'-2 1/2" slab underside over the '
                        'wall - 1" polystyrene - wall top (1\'-3 1/2" below the slab top), the slab underside continuing '
                        'the 1\'-2 1/2" pavement-ledge level of sheet 32. The written top-of-wing elevations equal the '
                        'written end-of-bent slab tops + grade - 1\'-2 1/2" (the slab underside) and those slab tops place '
                        'the crown on the structure centre line, whereas sheets 23/53 and all 42 seat elevations put it '
                        'on Line "A" (written minus model wall top: ' + ', '.join(
                            f'{r["plan_name"]} {r["written_minus_model_ft"]:+.3f} ft' for r in wing_rows.values()) + ').',
        'end-bent notch depth': 'Sheets 46-48 dimension the flange setback (6 in) and the acute-half cut (10 7/8 in) in '
                                'plan; the notch depth is not dimensioned (the elevations are not to scale), so the cut '
                                'is taken through the top flange and its fillet, the 11 in above the web of the sheet 45 '
                                'section.',
        'east terminal joint': 'The dimensioned slab edges from the End of Bridge Floor govern (they reproduce the west '
                               f'callout 386+34.06 at {stations[-1]:.2f}); the east callouts 391+92.68 (sheet 60) and '
                               f'391+92.86 (sheet 22) disagree with each other and with the dimensions ({stations[1]:.2f}).',
        'end-bent seat': 'The seat at Bents 1 and 6 is the beam soffit, on top of the 1 in anchor bar: the sheet 32 '
                         'SECTION B-B chain soffit + 2\'-8 1/4" / 2\'-7 7/8" (lower cap, min.) + 7" (bar and 6 in studs, '
                         'min.) equals the lowest seats 482.965 / 483.010 within 0.004 ft at both bents. The 1 3/8 in '
                         'fillet shown in SECTION B-B is read as a minimum, as in sheet 54 SECTION E-E where it is '
                         'labelled Min.; the schedule gives about 2.9 in at the end bents and 3.1-3.3 in at Bents 2-5.',
        'camber distribution': 'Sheet 45 gives the residual camber at midspan only; the model distributes it as a '
                               'parabola between the bearings.'})
    manifest['review_correction_record_3'] = dict(
        source_pdf_pages=SOURCE_PAGES, printed_sheets=PRINTED_SHEETS, previous_revision=PREVIOUS_REVISION,
        native_axes='Unchanged: X along Line "A" stations, Y left of increasing station (north), Z = El. - 450 ft (m)',
        resolved={
            'bearing-seat-schedule': 'seats at the scheduled elevations; T1 pads 3 11/16 in (sheet 54), anchor bars at '
                                     'the end bents (sheet 32); beams on the chord plus residual camber (sheet 45); '
                                     'haunches variable; beam ends square as drawn (sheets 43, 45)',
            'interior-support-diaphragms': 'diaphragm_1..diaphragm_4, 3 ft thick (sheets 43, 53, 54)',
            'end-bent-wingwalls': 'wing_0_-1, wing_0_1, wing_5_1, wing_5_-1 (sheets 26, 28, 29, 31)',
            'deck-end-length': 'deck ends 9.525 mm out to 492 ft 0 7/8 in (sheets 20-22, 32)',
            'cap terraces and keyways (check 3)': 'cap_1..cap_4 terraced to the seats (sheets 35, 39 Seat Dim\'s), six '
                                                  '3 in x 1 ft x 8 ft 9 in keyways each (sheets 35, 39, 54); the 52 '
                                                  'interior pedestals they replace are removed',
            'diaphragm keys (check 3)': 'six 10 in x 8 ft 7 in keys per diaphragm, 1/2 in and 1 in clearances (sheet 54)',
            'wing C-C stack (check 3)': 'wall top 1 ft 3 1/2 in below the slab top with a 3 in x 6 in keyway; approach '
                                        'slab 1 ft 2 1/2 in thick over the walls with a 5 in tongue (sheets 28, 31)',
            'end-bent-beam-corners (check 3)': 'span A / E top flanges set back 6 in, acute half cut 10 7/8 in more '
                                               '(sheets 46-48)'},
        decided={'approach-east-terminal-station': decisions['east terminal joint'],
                 'end-bent-wingwalls (top level)': decisions['wingwall top'],
                 'bearing-seat-schedule (end-bent seat)': decisions['end-bent seat']},
        decisions=decisions,
        kept={'end-bent-beam-notch-depth': 'the notch depth of the resolved end-bent flange cut is not dimensioned'},
        checks=checks,
        changed_parts=sorted(out), added_parts=sorted(added), removed_parts=sorted(removed),
        before_glb_sha256=before, after_glb_sha256=hashlib.sha256(result).hexdigest())
    manifest['known_deviations'] = [d for d in manifest.get('known_deviations', []) if d.get('id') not in (
        'bearing-seat-schedule', 'interior-support-diaphragms', 'end-bent-wingwalls', 'deck-end-length',
        'approach-east-terminal-station', 'end-bent-beam-corners', 'end-bent-beam-notch-depth')]
    manifest['known_deviations'].append(dict(
        id='end-bent-beam-notch-depth', parts='bulbt_0_*, bulbt_4_*, haunch_0_*, haunch_4_*',
        source='sheets 45-48 (PDF 131-134)',
        deviation='The end-bent top-flange notch (6 in setback, acute half cut 10 7/8 in more) is cut 11 in deep, through '
                  'the flange and its fillet down to the web.',
        reason='Sheets 46-48 dimension the notch in plan only and their elevations are not to scale; no sheet gives its '
               'depth. The beam shop drawings would settle it.'))
    mp.write_bytes(dump_like(manifest, raw_manifest, ensure_ascii=False, indent=2))

    # Source ledger: the deck length it records and the part lists of its checks.
    ledger = json.loads(raw_ledger)
    ledger['whole_bridge_dimensions']['deck_length_m'] = round(L_NEW, 6)
    for c in ledger.get('verified_source_checks', []):
        c['part_ids'] = [x for x in c['part_ids'] if x not in gone]
        if c['feature'] == 'Bents and bearings':
            c['part_ids'] += sorted(added)
        if c['feature'] == 'Missing exterior details':
            c['detail'] = c['detail'].replace('End-bent wings, complete support diaphragms, drainage',
                                              'Drainage').replace('remain unresolved.', 'remain unresolved; end-bent '
                                                                  'wings and support diaphragms added in revision 1.3.')
    ledger_path.write_bytes(dump_like(ledger, raw_ledger, indent=2))

    rec = manifest['review_correction_record_3']
    print(json.dumps({k: rec[k] for k in ('checks', 'added_parts', 'removed_parts', 'before_glb_sha256',
                                          'after_glb_sha256')}, indent=1))
    print(f'{len(out)} parts changed, {len(added)} added, {len(removed)} removed; {len(plist)} parts')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--base', type=Path, default=BASE, help='bridge folder (default: the repository copy)')
    parser.add_argument('--backup', type=Path, default=BACKUP, help='backup folder')
    args = parser.parse_args()
    correct(args.base, args.backup)

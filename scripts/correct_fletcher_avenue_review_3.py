"""Third round of drawing-confirmed corrections of Fletcher Avenue over I-65 / I-70 (fletcher-avenue): the known
deviations left by scripts/correct_fletcher_avenue_review.py and scripts/correct_fletcher_avenue_review_2.py. Unrelated
GLB buffers are kept; new accessors, meshes and nodes are appended.

    python scripts/correct_fletcher_avenue_review_3.py [--dry-run]

Source: drawings.pdf (printed sheet n = PDF page n for the 2026 contract sheets 33-73; S8 = PDF 99, S9 = PDF 100,
S10 = PDF 101, S12 = PDF 103 of the 1971 I-65-3(106)111 plans). Native axes: X increasing station, Y transverse (+Y
south, girder 1 at +Y), Z up; Z = (El. - 698.59 ft) x 0.3048; U = X + tan(skew) Y along each girder line.

1. Type TTX modified railing transitions and RCBA slab extensions (known deviation `ttx-transitions`; sheets 66, 67,
   68, 69, 70, 71). Sheet 66: each R.C. bridge approach is 66 ft 2 in wide; the 68 ft 6 in coping width is reached
   only by 1 ft 2 in slab extensions under the four transitions (68 ft 6 in = 66 ft 2 in + 2 x 1 ft 2 in). Section C-C
   (sheet 70) puts the transition 2 in inside the extension edge, 1 ft 0 in wide, with the 6 ft 1 in sidewalk inside
   it; the sidewalk concrete runs under the rail to the edge. Extension lengths (sheet 66): Wing A 30 ft 10 1/2 in from
   the north deck-end corner at Abut. 1, Wing B the south short edge plus 12 ft 2 1/2 in x 7 ft 3 in beyond the square
   end (sheet 67), Wing C the north short edge at Abut. 3, Wing D 21 ft 1 1/2 in from the south corner at Abut. 3.
   Transitions (sheets 68, 69): pay limits A 30 ft 2 in, B 29 ft 4 in, C 17 ft 2 in, D 20 ft 5 1/2 in from the centre
   line of the 1/2 in open joint at the end bent, measured along the traffic face (decision: this is the only reading
   that reproduces the sheet 66 edge lengths, see the record); north 3 ft 6 in, south 4 ft 6 in with the 1 ft taller
   base (sections D-D to G-G); end-bent pilaster 1 ft 4 1/2 in long, 2 in taller over its first 1 ft 1 1/2 in; six
   windows at 1 ft 6 in, the first 10 in beyond the pilaster, 6 in clear and 1 ft 4 in high with the sill 1 ft 0 in
   (north) / 2 ft 0 in (south) above the sidewalk (window detail, section E-E), heads of two R 1 ft 0 in arcs (rise
   1 1/2 in scaled). The far end is square. The approach slabs and walks were 66 ft 6 in wide (generator value); they
   are narrowed to the sheet 66 width so the extensions sit beside them. The bridge TX end pilasters stop 1/4 in short
   of the deck-end line (sheets 63/64 pay limits to the end of the bridge floor), leaving the 1/2 in open joint. The
   retained wing envelopes move out so their inner faces sit 1 in outside the extensions (sheet 70 section C-C).
   Face recesses, chamfers and notches are not dimensioned in elevation (known deviation ttx-face-recesses).
2. Field-splice web plates, inner splice bars and bolts (known deviation `splice-web-plates`; S9, S10, S8 notes). The
   web plates become the drawn 19 in x 5/8 in x 4 ft 6 in plates on both faces of the web, centred on the web and on
   the splice; web bolts 18 rows at 3 in (17 spaces = 4 ft 3 in) in 6 columns 2 in, 5 in and 8 in either side of the
   splice line. Inner 10 in x 1 in x 6 ft 3 in (S9) / 6 ft 9 in (S10) splice bars, two under each flange, flush with the
   flange edges (3 in, 4 in, 3 in bolt gauges). Flange bolts in four lines (S9: 6 in and 10 in, S10: 5 in and 9 in from
   the web), 12 (S9) / 13 (S10) per line either side of the splice at 3 in, the first 3 in from the splice line, top
   and bottom flanges; 7/8 in high-strength bolts (S8 structural steel notes). The flange splice plates and fillers of
   the second round are unchanged. The lateral bracing envelopes ran into the new splice bars and nuts; S11 cross
   frame XF-1 puts the lateral gussets 5 in above the bottom flange and details C-E end the WT 6 x 18 laterals on
   them outside the flange tips, so the 36 laterals move there and seat on 39 new 3/8 in gusset plates (one per
   panel point, from the web face to the 12 in bolted ends of the tees, notched around stiffeners, splice plates and
   cross-frame members).

Kept (reasons rewritten in known_deviations): `pier2-shoe-stack` and `haunch-thickness`. S7 + S12 + S13 fix the Pier
2 stacks, but the 2026 top-of-steel elevations are in the screed data of the Letting Documents (sheets 59/60 notes),
not in the plans, and the 1971 elevations (S7, S9, S13) only fit the 2026 grade, 8 in deck and the 2 3/16 in minimum
haunch (sheet 65, slab soffit to the underside of the top flange) with a datum relation no sheet gives. New kept items: `ttx-face-recesses` (panel outline in
E 706-TTTX, not in the binder) and `retained-wing-envelopes` (S3-S6 wings, deferred).

Requires numpy, trimesh, shapely and manifold3d; reuses the helpers of the first two review scripts.
"""
import hashlib
import json
import struct
import sys
from pathlib import Path

import manifold3d
import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import correct_fletcher_avenue_review as R1  # noqa: E402
import correct_fletcher_avenue_review_2 as R2  # noqa: E402
from bridge_geometry import bolt, box, concat, rectangular_bar  # noqa: E402

BID = 'fletcher-avenue'
BASE = ROOT / 'data/bridges' / BID
TAG_KEY = 'review_correction_3'
TAG = 'ttx-transitions-rcba-extensions-drawn-field-splice-webs-bolts'
REVISION = '1.3-deviations'
EXPECTED_DEVIATIONS = {'pier2-shoe-stack', 'haunch-thickness', 'ttx-transitions', 'splice-web-plates'}

FT, IN = R1.FT, R1.IN
K, SPAN, YS = R1.K, R1.SPAN, R1.YS
SLAB, ROAD, HALF = R1.SLAB, R1.ROAD, R1.HALF
U_END = {-1: R1.U0, 1: R1.U1}

# ------------------------------------------------------------------ sheets 66-70: approaches and TTX transitions
APPROACH_W = (66 + 2 / 12) * FT              # sheet 66: R.C. bridge approach 66 ft 2 in (99 spa. @ 8 in + 2 x 3 in)
EXT = 14 * IN                                # sheet 66: 68 ft 6 in = 66 ft 2 in + 2 x 1 ft 2 in slab extensions
RAIL_OUT = 2 * IN                            # sheets 68-70: rail 2 in inside the slab-extension edge
JOINT = .5 * IN                              # sheets 68/69: 1/2 in open joint at the end bent
PILASTER, RAISED, RISE = 16.5 * IN, 13.5 * IN, 2 * IN   # end-bent pilaster 1'-4 1/2", 3'-8" over 1'-1 1/2" (3" step)
WINDOW_FIRST, WINDOW_PITCH, WINDOWS = 16.5 * IN + 10 * IN, 18 * IN, 6    # 1'-4 1/2" + 10", 5 spa. @ 1'-6"
WINDOW_W, WINDOW_H, WINDOW_SILL = 6 * IN, 16 * IN, 12 * IN               # window detail, section E-E
HEAD_R, HEAD_RISE = 12 * IN, 1.5 * IN        # window detail: R 1'-0" (typ.) head arcs; rise scaled (not dimensioned)
WING_GAP = 1 * IN                            # sheet 70 section C-C: 1 in expanded polystyrene between slab and wing
WINGS = {   # (end, side): letter, sheet, rail height, pay limit, base plinth, extension (sheet 66/67)
    (-1, -1): dict(letter='A', sheet=68, h=3.5 * FT, plinth=0.0, length=(30 + 2 / 12) * FT,
                   ext=('corner', (30 + 10.5 / 12) * FT), coping='north coping Abut. No. 1'),
    (-1, 1): dict(letter='B', sheet=69, h=4.5 * FT, plinth=FT, length=(29 + 4 / 12) * FT,
                  ext=('square', (12 + 2.5 / 12) * FT), coping='south coping Abut. No. 1'),
    (1, -1): dict(letter='C', sheet=68, h=3.5 * FT, plinth=0.0, length=(17 + 2 / 12) * FT,
                  ext=('square', 0.0), coping='north coping Abut. No. 3'),
    (1, 1): dict(letter='D', sheet=69, h=4.5 * FT, plinth=FT, length=(20 + 5.5 / 12) * FT,
                 ext=('corner', (21 + 1.5 / 12) * FT), coping='south coping Abut. No. 3')}

# ------------------------------------------------------------------ S9 / S10 / S8: field splices
WEB_PLATE = (19 * IN, .625 * IN, 54 * IN)    # 19 in x 5/8 in x 4 ft 6 in, one each side of the web
WEB_COLUMNS = np.array([-8, -5, -2, 2, 5, 8]) * IN          # 1 1/2, 3, 3, 2 | 2, 3, 3, 1 1/2 in across 19 in
WEB_ROWS = (np.arange(18) * 3 - 25.5) * IN                  # 17 spa. @ 3 in = 4 ft 3 in, 1 1/2 in edges
BAR = (10 * IN, 1 * IN)                                      # 10 in x 1 in inner splice bars (2 top & 2 bottom)
GAUGE = {True: np.array([6, 10]) * IN, False: np.array([5, 9]) * IN}      # S9 3/4/1'-0"/4/3, S10 3/4/10/4/3
PER_SIDE = {True: 12, False: 13}             # S9 11 spa. @ 3 in, S10 12 spa. @ 3 in, first bolt 3 in from the splice
BOLT_R = 7 / 8 * IN / 2                      # S8 structural steel notes: high strength bolts 7/8 in unless noted
# S11 cross frame XF-1: 3/8 in gusset plates at the point of lateral bracing only, 5 in (min.) above the bottom
# flange; details C-E: the WT 6 x 18 laterals bolt to those gussets outside the flange tips.
GUSSET_UP, GUSSET_T = 5 * IN, 3 / 8 * IN
LAT_W, LAT_T = .12, .016                     # generator's lateral envelope (rectangular_bar .12 x .016)
# S13 shim thickness table, Pier 2 "T" (girders 1-8)
PIER_SHIM = {1: 7 / 8, 2: .5, 3: .5, 4: 1.125, 5: 11 / 16, 6: 11 / 16, 7: .5, 8: .5}


def ftin(m):
    """Length in metres as feet and inches to 1/8 in, e.g. '30 ft 10 1/2 in'."""
    eighths = int(round(m / IN * 8))
    ft, rest = divmod(eighths, 96)
    whole, frac = divmod(rest, 8)
    frac_txt = {0: '', 1: ' 1/8', 2: ' 1/4', 3: ' 3/8', 4: ' 1/2', 5: ' 5/8', 6: ' 3/4', 7: ' 7/8'}[frac]
    return f'{ft} ft {whole}{frac_txt} in'


def approach_meshes(width):
    """The first-round approach slab and walk sweeps (R1 section 4) at a given slab width."""
    out = {}
    for end in (-1, 1):
        u, outer = U_END[end], R1.SQUARE_END[end]

        def at(t, y, u=u, outer=outer):
            return (1 - t) * R1.sx(u, y) + t * outer

        prof = [(-width / 2, 0), (-ROAD, 0), (0, 0), (width / 2, 0), (width / 2, 1), (0, 1), (-ROAD, 1),
                (-width / 2, 1)]
        out[f'approach_{end}'] = R1.sweep(prof, np.linspace(0, 1, 45),
                                          lambda t, y, h, at=at: (at(t, y), y, R1.surface(at(t, y), y) - (1 - h) * FT))
        for side in (-1, 1):
            y0, y1 = sorted([side * ROAD, side * width / 2])
            out[f'approach_walk_{end}_{side}'] = R1.sweep(
                [(y0, 0), (y1, 0), (y1, 1), (y0, 1)], np.linspace(0, 1, 25),
                lambda t, y, h, at=at: (at(t, y), y, (1 - h) * R1.surface(at(t, y), y) + h * R1.walk(at(t, y), y)))
    return out


def extension_end(end, side):
    """Far (square) end X of the 1 ft 2 in strip along the coping, and the Wing B extension beyond the square end."""
    kind, length = WINGS[(end, side)]['ext']
    if kind == 'corner':                      # dimensioned from the deck-end corner at the coping line (sheet 66)
        return R1.sx(U_END[end], side * HALF) + end * length, None
    beyond = None
    if length:                                # Wing B: 12 ft 2 1/2 in beyond the square end, 7 ft 3 in wide (67)
        beyond = sorted([R1.SQUARE_END[end], R1.SQUARE_END[end] + end * length])
    return R1.SQUARE_END[end], beyond


def extension_pieces(end, side, zfun):
    """Closed prisms (strip along the coping, plus the Wing B piece beyond the square end) between zfun(x, y, 0)
    and zfun(x, y, 1)."""
    u = U_END[end]
    x_end, beyond = extension_end(end, side)
    y0, y1 = sorted([side * (HALF - EXT), side * HALF])

    def at(t, y):
        return (1 - t) * R1.sx(u, y) + t * x_end

    n = max(3, int(np.ceil(abs(x_end - R1.sx(u, side * HALF)) / .4)) + 1)
    pieces = [R1.sweep([(y0, 0), (y1, 0), (y1, 1), (y0, 1)], np.linspace(0, 1, n),
                       lambda t, y, h: (at(t, y), y, zfun(at(t, y), y, h)))]
    if beyond:
        b0, b1 = sorted([side * ROAD, side * HALF])
        xs = np.linspace(beyond[0], beyond[1], max(3, int(np.ceil((beyond[1] - beyond[0]) / .4)) + 1))
        pieces.append(R1.sweep([(b0, 0), (b1, 0), (b1, 1), (b0, 1)], xs,
                               lambda x, y, h: (x, y, zfun(x, y, h))))
    return pieces


def window(c, sill):
    """6 in clear opening (window detail), apex 1 ft 4 in above the sill (section E-E), pointed head of two R 1 ft 0 in
    arcs (window detail) from the jamb tops to the apex; the head rise (1 1/2 in) is scaled from the window detail."""
    hw, apex = WINDOW_W / 2, sill + WINDOW_H
    chord = np.hypot(hw, HEAD_RISE)
    mid = np.array([hw / 2, HEAD_RISE / 2])
    centre = mid + np.sqrt(HEAD_R ** 2 - (chord / 2) ** 2) * np.array([-HEAD_RISE, -hw]) / chord
    a0, a1 = np.arctan2(-centre[1], hw - centre[0]), np.arctan2(HEAD_RISE - centre[1], -centre[0])
    arc = [centre + HEAD_R * np.array([np.cos(a), np.sin(a)]) for a in np.linspace(a0, a1, 7)]
    right = [(c + q[0], apex - HEAD_RISE + q[1]) for q in arc]
    left = [(c - q[0], apex - HEAD_RISE + q[1]) for q in arc[-2::-1]]
    return np.array([(c - hw, sill), (c + hw, sill)] + right + left)


def ttx_mesh(end, side):
    """Transition in local (s along the traffic face from the joint centre line, h above the sidewalk, w across):
    a 1 ft 0 in x h prism subdivided along s so that it follows the grade, the raised end-bent pilaster added, the
    six windows cut through, and the near end trimmed on the skew joint line 1/4 in from its centre line."""
    w = WINGS[(end, side)]
    h, length = w['h'], w['length']
    y_t = side * (HALF - EXT)                 # traffic face (sheet 70 C-C: 2 in + 1 ft 0 in from the edge)
    x0 = R1.sx(U_END[end], y_t)               # centre line of the open joint on the deck-end line
    s_min = -.3
    stations = np.unique(np.r_[np.linspace(s_min, length, int(np.ceil((length - s_min) / .3)) + 1), RAISED])
    body = R1.sweep([(0, 0), (FT, 0), (FT, h), (0, h)], stations, lambda q, ww, hh: (q, hh, ww))

    def solid(mesh):
        return manifold3d.Manifold(manifold3d.Mesh(np.asarray(mesh.vertices, np.float32),
                                                   np.asarray(mesh.faces, np.uint32)))

    man = solid(body)
    pil = R1.sweep([(0, h - .05), (FT, h - .05), (FT, h + RISE), (0, h + RISE)], [s_min, RAISED],
                   lambda q, ww, hh: (q, hh, ww))
    man = man + solid(pil)
    holes = [window(WINDOW_FIRST + k * WINDOW_PITCH, WINDOW_SILL + w['plinth']) for k in range(WINDOWS)]
    cut = manifold3d.Manifold.extrude(manifold3d.CrossSection(holes, manifold3d.FillRule.EvenOdd), FT + .02)
    man = man - cut.translate((0, 0, -.01))
    normal = np.array([1.0, 0.0, end * side * K])               # keep the approach side of the skew joint line,
    man = man.trim_by_plane(normal.tolist(), (JOINT / 2) / np.linalg.norm(normal))   # 1/4 in off its centre line
    mesh = R1.from_manifold(man)
    s, hh, ww = mesh.vertices.T
    x, y = x0 + end * s, y_t + side * ww
    mesh = trimesh.Trimesh(np.c_[x, y, R1.walk(x, y) + hh], mesh.faces, process=False)
    if mesh.volume < 0:
        mesh.invert()
    if not (mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0):
        raise ValueError(f'ttx_{end}_{side}: not a closed solid')
    return mesh, x0


def flange_top(u, j):
    """Top of the bottom flange of model line j at girder station u (girders as left by the second round)."""
    return R2.top_new(u, j) - R1.depth_new(u, j) + R1.tf_new(u, j)


def lateral_old(bay, i):
    """Generator lateral envelope (build_indiana_batch3.fletcher): 0.14 m below the girder tops, girder line to girder
    line between cross-frame rows i and i + 1, zig-zag."""
    a, b = R1.CF_ROWS[i], R1.CF_ROWS[i + 1]
    y0, y1 = (YS[bay], YS[bay + 1]) if i % 2 == 0 else (YS[bay + 1], YS[bay])
    z0 = float(R1.surface_old(R1.sx(a, y0), y0)) - SLAB - R1.CLEAR - .14
    z1 = float(R1.surface_old(R1.sx(b, y1), y1)) - SLAB - R1.CLEAR - .14
    return rectangular_bar([R1.sx(a, y0), y0, z0], [R1.sx(b, y1), y1, z1], LAT_W, LAT_T)


BOLTED = 12 * IN                             # S11 details C-E: 4 bolts at 3 in (3 spa.) plus 1 1/2 in edges per tee


def node_girder(bay, r):
    """Girder line of the lateral panel point on cross-frame row r (zig-zag: even rows on `bay`, odd on `bay + 1`)."""
    return bay if r % 2 == 0 else bay + 1


def gusset_top(u, j):
    """Top of the 3/8 in lateral gusset of girder j at station(s) u: 5 in above the bottom flange (S11 XF-1)."""
    if np.ndim(u):
        return np.array([flange_top(float(q), j) for q in np.asarray(u)]) + GUSSET_UP + GUSSET_T
    return flange_top(float(u), j) + GUSSET_UP + GUSSET_T


def lateral_ends(bay, i):
    """Plan ends of panel i: on the brace line between the two panel points, cut at the flange tips (S11 C-E)."""
    j0, j1 = node_girder(bay, i), node_girder(bay, i + 1)
    p0 = np.array([R1.sx(R1.CF_ROWS[i], YS[j0]), YS[j0]])
    p1 = np.array([R1.sx(R1.CF_ROWS[i + 1], YS[j1]), YS[j1]])
    dy = abs(YS[j1] - YS[j0])
    half = {j: (26 if R1.exterior(j) else 24) * IN / 2 for j in (j0, j1)}
    return p0 + half[j0] / dy * (p1 - p0), p1 - half[j1] / dy * (p1 - p0), j0, j1


def node_plane(bay, r):
    """Flat 3/8 in gusset at panel point r: its top 5 in + 3/8 in above the bottom flange at the panel point
    (S11 XF-1), sloping with the girder there; returns (girder line, station, top elevation, slope along the girder)."""
    j = node_girder(bay, r)
    u = R1.CF_ROWS[r]
    slope = (gusset_top(u + .05, j) - gusset_top(u - .05, j)) / .1
    return j, u, gusset_top(u, j), slope


def plane_top(plane, x):
    j, u, z, slope = plane
    return z + slope * (np.asarray(x) + K * YS[j] - u)


def bar_clearance(mesh, a, b, plane):
    """Lowest clearance above the gusset plane of the bar's edges over the bolted length at end `a`."""
    v = mesh.vertices
    d = b - a
    s = (v - a) @ d / (d @ d)
    corners = v[s < .5]                        # the four corners at end a; their mates are corner + d
    step = BOLTED / np.linalg.norm(d[:2])
    q = (corners[:, None, :] + np.linspace(0, step, 9)[None, :, None] * d[None, None, :]).reshape(-1, 3)
    return float((q[:, 2] - plane_top(plane, q[:, 0])).min())


def lateral_new(bay, i):
    """S11: WT envelope seated on the lateral gussets 5 in above the bottom flange (XF-1), ends at the flange tips
    (details C-E); each end is raised or lowered until its lowest edge touches its gusset over the bolted length."""
    q0, q1, j0, j1 = lateral_ends(bay, i)
    p0, p1 = node_plane(bay, i), node_plane(bay, i + 1)
    z0, z1 = float(plane_top(p0, q0[0])) + LAT_W / 2, float(plane_top(p1, q1[0])) + LAT_W / 2
    for _ in range(12):
        a, b = np.r_[q0, z0], np.r_[q1, z1]
        mesh = rectangular_bar(a, b, LAT_W, LAT_T)
        c0, c1 = bar_clearance(mesh, a, b, p0), bar_clearance(mesh, b, a, p1)
        if max(abs(c0), abs(c1)) < 1e-8:
            break
        z0, z1 = z0 - c0, z1 - c1
    else:
        raise ValueError(f'lateral_{bay}_{i}: could not seat on its gussets')
    return mesh, (j0, j1)


def gusset_mesh(bay, r, braces, cuts, pad=0.0):
    """Flat 3/8 in lateral gusset at panel point r from the web face to the bolted ends of the tees meeting there
    (S11 XF-1, details C-E), minus `cuts` (plan footprints of stiffeners, splice pieces and cross-frame members)."""
    import shapely
    plane = node_plane(bay, r)
    j = plane[0]
    y = YS[j]
    other = YS[bay + 1] if j == bay else YS[bay]
    face = y + np.sign(other - y) * R1.TW / 2
    pts = []
    for mesh, a, b in braces:                  # bar mesh, its end at this panel point, its other end
        v = mesh.vertices
        d = b - a
        corners = v[(v - a) @ d / (d @ d) < .5]
        step = BOLTED / np.linalg.norm(d[:2])
        pts += [tuple(q[:2]) for q in corners] + [tuple((q + step * d)[:2]) for q in corners]
    us = [q[0] + K * q[1] for q in pts]
    pts += [(R1.sx(min(us), face), face), (R1.sx(max(us), face), face)]
    poly = shapely.MultiPoint(pts).convex_hull
    for cut in cuts:
        poly = poly.difference(cut)
    poly = poly.buffer(-.0005, join_style=2).buffer(.0005, join_style=2)      # no slivers under 1 mm
    pieces = [g for g in getattr(poly, 'geoms', [poly]) if g.area > 1e-4]
    rings = []
    for g in pieces:
        g = shapely.geometry.polygon.orient(g, 1)
        rings.append(np.array(g.exterior.coords)[:-1])
        rings += [np.array(h.coords)[:-1] for h in g.interiors]
    man = manifold3d.Manifold.extrude(manifold3d.CrossSection(rings, manifold3d.FillRule.EvenOdd), 1.0)
    mesh = R1.from_manifold(man)
    v = mesh.vertices.copy()
    v[:, 2] = plane_top(plane, v[:, 0]) + pad - (1 - v[:, 2]) * (GUSSET_T + 2 * pad)
    out = trimesh.Trimesh(v, mesh.faces, process=False)
    if out.volume < 0:
        out.invert()
    if not (out.is_watertight and out.volume > 0):
        raise ValueError(f'lateral_gusset_{bay}_{r}: not a closed solid')
    return out, shapely.MultiPolygon(pieces) if len(pieces) > 1 else pieces[0]


def r2_splice(j, si):
    """The second-round field splice part (R2 section 1) for model line j, splice index si."""
    y, ext = YS[j], R1.exterior(j)
    us = (-R2.SPLICE, R2.SPLICE)[si]
    cw, ct, cl = R2.COVER[ext]
    fw, ft, fl = R2.FILLER[ext]
    x, z = R1.sx(us, y), R2.top_pier(us, j) - R1.depth_new(us, j) / 2
    webw, webh, plate = 1.2, 1.37, .0159
    old_web = [box(x - webw / 2, x + webw / 2, y + q * (R1.TW / 2 + plate / 2) - plate / 2,
                   y + q * (R1.TW / 2 + plate / 2) + plate / 2, z - webh / 2, z + webh / 2) for q in (-1, 1)]
    field = np.sign(us)

    def plate_on(u0, u1, width, zfun):
        st = np.linspace(min(u0, u1), max(u0, u1), 9)
        return R1.sweep([(-width / 2, 0), (width / 2, 0), (width / 2, 1), (-width / 2, 1)], st,
                        lambda u, dy, t: (R1.sx(u, y), y + dy, zfun(u, t)))

    lo, hi = us - cl / 2, us + cl / 2
    f0, f1 = us + field * (cl / 2 - fl), us + field * cl / 2
    flange = [plate_on(lo, hi, cw, lambda u, t: R2.top_pier(u, j) + t * ct),
              plate_on(lo, hi, cw, lambda u, t: R2.bottom_pier(u, j) - ct + t * ct),
              plate_on(f0, f1, fw, lambda u, t: R2.top_pier(u, j) - ft + t * ft),
              plate_on(f0, f1, fw, lambda u, t: R2.bottom_pier(u, j) + t * ft)]
    return old_web, flange


def splice_new(j, si):
    """S9/S10 field splice: R2 flange splice plates and fillers, drawn web plates and inner splice bars; bolts."""
    y, ext = YS[j], R1.exterior(j)
    us = (-R2.SPLICE, R2.SPLICE)[si]
    _, flange = r2_splice(j, si)
    cw, ct, cl = R2.COVER[ext]
    tf = R1.tf_pier(j)

    def web_top(u):
        return R2.top_pier(u, j) - tf

    def web_bottom(u):
        return R2.bottom_pier(u, j) + tf

    def prism(u0, u1, a0, a1, zfun, n=9):
        st = np.linspace(u0, u1, n)
        return R1.sweep([(a0, 0), (a1, 0), (a1, 1), (a0, 1)], st,
                        lambda u, a, t: (R1.sx(u, y), y + a, zfun(u, t)))

    pw, pt, ph = WEB_PLATE
    pieces = []
    for q in (-1, 1):                                          # web plates on both faces, centred on the web
        a0, a1 = sorted([q * R1.TW / 2, q * (R1.TW / 2 + pt)])
        pieces.append(prism(us - pw / 2, us + pw / 2, a0, a1,
                            lambda u, t: (web_top(u) + web_bottom(u)) / 2 + (t - .5) * ph, n=5))
    bw, bt = BAR
    b = (26 if ext else 24) * IN
    for q in (-1, 1):                                          # inner splice bars, flush with the flange edges
        a0, a1 = sorted([q * (b / 2 - bw), q * b / 2])
        pieces.append(prism(us - cl / 2, us + cl / 2, a0, a1, lambda u, t: web_top(u) - bt + t * bt))
        pieces.append(prism(us - cl / 2, us + cl / 2, a0, a1, lambda u, t: web_bottom(u) + t * bt))
    plates = concat(flange + pieces)

    fasteners = []
    for c in WEB_COLUMNS:                                      # web bolts through both web plates
        u = us + c
        mid = (web_top(u) + web_bottom(u)) / 2
        for r in WEB_ROWS:
            fasteners.append(bolt([R1.sx(u, y), y - R1.TW / 2 - pt, mid + r],
                                  [R1.sx(u, y), y + R1.TW / 2 + pt, mid + r], BOLT_R))
    along = us + np.r_[-(3 + 3 * np.arange(PER_SIDE[ext]))[::-1], 3 + 3 * np.arange(PER_SIDE[ext])] * IN
    for u in along:                                            # flange bolts: splice plate, (filler,) flange, bar
        for g in np.r_[-GAUGE[ext][::-1], GAUGE[ext]]:
            x = R1.sx(u, y)
            fasteners.append(bolt([x, y + g, R2.top_pier(u, j) + ct], [x, y + g, web_top(u) - bt], BOLT_R))
            fasteners.append(bolt([x, y + g, R2.bottom_pier(u, j) - ct], [x, y + g, web_bottom(u) + bt], BOLT_R))
    counts = dict(web=len(WEB_COLUMNS) * len(WEB_ROWS), flange=len(along) * 4 * 2)
    return plates, concat(fasteners), counts


# ------------------------------------------------------------------------------------------ correction
def correct(base=BASE, backup=ROOT / 'data/fem_research', dry_run=False):
    mp = base / 'model_manifest.json'
    raw_manifest = mp.read_bytes()
    manifest = json.loads(raw_manifest.decode('utf-8'))
    if manifest.get(TAG_KEY) == TAG:
        print('Already corrected.')
        return None
    if manifest.get('review_geometry_correction_2') != R2.TAG or manifest.get('revision') != R2.REVISION:
        raise ValueError('run scripts/correct_fletcher_avenue_review_2.py first '
                         f'(expected revision {R2.REVISION}, found {manifest.get("revision")})')
    path = base / 'model.glb'
    original = path.read_bytes()
    before = hashlib.sha256(original).hexdigest()
    if before != manifest['review_geometry_correction_2_record']['after_glb_sha256']:
        raise ValueError('model.glb is not the output of the second review correction')
    known = {d.get('id') for d in manifest.get('known_deviations', [])}
    if known != EXPECTED_DEVIATIONS:
        raise ValueError(f'unexpected known_deviations {sorted(known)}')
    length = struct.unpack_from('<I', original, 12)[0]
    gltf = json.loads(original[20:20 + length])
    binary = bytearray(original[28 + length:])
    if any(k in n for n in gltf['nodes'] for k in ('matrix', 'rotation', 'translation', 'scale')):
        raise ValueError('unexpected node transforms')
    world = gltf['nodes'][gltf['scenes'][gltf.get('scene', 0)]['nodes'][0]]
    parts = {p['id']: p for p in manifest['parts']}
    meshes = {m['name']: m for m in gltf['meshes']}
    changed, added, renamed = [], [], {}

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
        f = read(prim['indices']).reshape(-1, 3)
        return trimesh.Trimesh(np.c_[v[:, 0], -v[:, 2], v[:, 1]], f, process=False)

    def primitive(mesh, color):
        v = mesh.vertices
        glb = np.c_[v[:, 0], v[:, 2], -v[:, 1]].astype('<f4')
        prim = {'attributes': {'POSITION': append(glb, 'VEC3', 5126),
                               'COLOR_0': append(np.tile(color, (len(v), 1)).astype('u1'), 'VEC4', 5121)},
                'indices': append(np.asarray(mesh.faces).reshape(-1, 1).astype('<u4'), 'SCALAR', 5125), 'mode': 4}
        gltf['accessors'][prim['attributes']['COLOR_0']]['normalized'] = True
        return prim

    def check_solid(pid, mesh):
        if not (mesh.is_watertight and mesh.volume > 0):
            raise ValueError(f'{pid}: not watertight with positive volume')

    def store(pid, mesh, note=None, dims=None, replace_dims=False, basis=None, name=None, new_topology=False):
        """Write a corrected native-axes mesh; update the manifest part and the mesh extras."""
        check_solid(pid, mesh)
        prim = meshes[pid]['primitives'][0]
        if new_topology:
            color = read(prim['attributes']['COLOR_0'])[0]
            meshes[pid]['primitives'][0] = primitive(mesh, color)
        else:
            old = native(pid)
            if len(mesh.vertices) != len(old.vertices) or not np.array_equal(np.asarray(mesh.faces), old.faces):
                raise ValueError(f'{pid}: topology changed without new_topology')
            v = mesh.vertices
            prim['attributes']['POSITION'] = append(np.c_[v[:, 0], v[:, 2], -v[:, 1]].astype('<f4'), 'VEC3', 5126)
        p = parts[pid]
        p['bounds_m'] = np.round(mesh.bounds, 6).tolist()
        p['volume_m3'] = round(float(mesh.volume), 9)
        if dims is not None:
            if replace_dims:
                p['dimensions'] = dict(dims)
            else:
                p.setdefault('dimensions', {}).update(dims)
        if note:
            p['note'] = note
        if basis:
            p['basis'] = basis
        if name and name != p['name']:
            renamed[pid] = dict(before=p['name'], after=name)
            p['name'] = name
        meshes[pid]['extras'].update(p)
        if pid not in changed:
            changed.append(pid)

    def add(pid, mesh, like, name, layer, pages, basis, note, dims):
        """New part: manifest entry with the fields of similar parts, mesh with extras, node in the scene."""
        if pid in parts or pid in meshes:
            raise ValueError(f'{pid}: already present')
        check_solid(pid, mesh)
        color = read(meshes[like]['primitives'][0]['attributes']['COLOR_0'])[0]
        part = dict(id=pid, name=name, layer=layer, color=parts[like]['color'], pdf_pages=pages, basis=basis,
                    note=note, dimensions=dims, bounds_m=np.round(mesh.bounds, 6).tolist(),
                    volume_m3=round(float(mesh.volume), 9))
        manifest['parts'].append(part)
        parts[pid] = part
        extras = {'processed': True}
        extras.update(part)
        gltf['meshes'].append(dict(name=pid, primitives=[primitive(mesh, color)], extras=extras))
        meshes[pid] = gltf['meshes'][-1]
        gltf['nodes'].append(dict(name=pid, mesh=len(gltf['meshes']) - 1))
        world['children'].append(len(gltf['nodes']) - 1)
        added.append(pid)

    # ------------------------------------------------------------------ expected starting state
    for pid, mesh in approach_meshes(R1.APPROACH_W).items():
        old = native(pid)
        if len(old.vertices) != len(mesh.vertices) or np.abs(old.vertices - mesh.vertices).max() > 2e-5:
            raise ValueError(f'{pid}: not the first-round 66 ft 6 in approach')
    for j in range(8):
        for si in range(2):
            pid = f'girder_{j + 1}_splice_{si + 1}'
            old_web, flange = r2_splice(j, si)
            us = (-R2.SPLICE, R2.SPLICE)[si]
            if not R1.same_points(concat(old_web + flange).vertices, native(pid).vertices):
                raise ValueError(f'{pid}: second-round splice not reproduced')
            bolts = R1.splice_meshes(us, j, R1.depth_new(us, j), R1.TW)[1]
            if not R1.same_points(bolts.vertices, native(pid + '_bolts').vertices):
                raise ValueError(f'{pid}_bolts: first-round bolt grid not reproduced')
    for end, side in WINGS:
        for pid in (f'ttx_{end}_{side}', f'approach_ext_{end}_{side}', f'approach_walk_ext_{end}_{side}'):
            if pid in parts or pid in meshes:
                raise ValueError(f'{pid}: already present')
    for bay in (0, 3, 6):
        for i in range(12):
            if not R1.same_points(lateral_old(bay, i).vertices, native(f'lateral_{bay}_{i}').vertices):
                raise ValueError(f'lateral_{bay}_{i}: generator lateral not reproduced')
    for side in (-1, 1):
        for pid, u in ((f'txpost_{side}_0_0', R1.U0), (f'txpost_{side}_1_5', R1.U1)):
            v = native(pid).vertices
            if (np.abs(v[:, 0] + K * v[:, 1] - u) < 1e-4).sum() != 4:
                raise ValueError(f'{pid}: end face not on the deck-end line')
    for pid in ('wing_1_-1', 'wing_1_1', 'wing_3_-1', 'wing_3_1'):
        v = native(pid).vertices
        if len(v) != 8 or not np.isclose(np.abs(v[:, 1]).min(), HALF - .08, atol=2e-5):
            raise ValueError(f'{pid}: unexpected generator wing envelope')

    # ------------------------------------------------------------------ 1. approaches 66 ft 2 in (sheet 66)
    for pid, mesh in approach_meshes(APPROACH_W).items():
        p = parts[pid]
        if pid.startswith('approach_walk_'):
            store(pid, mesh, dims=dict(width_m=round((APPROACH_W / 2 - ROAD), 6)),
                  note='Extended to the corrected square end; 1.5 % walk on the corrected slab. Outer edge on the sheet '
                       '66 slab edge (66 ft 2 in slab, 6 ft 1 in sidewalk; sheet 70 section C-C); under the TTX '
                       'transitions the sidewalk continues over the slab extension (approach_walk_ext_*).',
                  basis='Main approach sidewalk envelope; sheet 66 width')
        else:
            store(pid, mesh, dims=dict(width_m=round(APPROACH_W, 6)),
                  basis='Source main plan geometry (sheet 66); TTX slab extensions are separate parts',
                  note=p['note'].replace('Manholes, wing-side walkway extensions and exact terminal curb details',
                                         'Manholes and exact terminal curb details') +
                       ' Width 66 ft 2 in (sheet 66; was the generator\'s 66 ft 6 in); the 1 ft 2 in RCBA slab '
                       'extensions under the TTX transitions bring it to the 68 ft 6 in coping width '
                       '(approach_ext_*).')

    # ------------------------------------------------------------------ 1. TTX transitions and extensions
    ttx_record = {}
    for (end, side), w in WINGS.items():
        abut = 1 if end < 0 else 3
        letter, sheet = w['letter'], w['sheet']
        compass = 'north' if side < 0 else 'south'
        x_end, beyond = extension_end(end, side)
        slab = concat(extension_pieces(end, side, lambda x, y, h: R1.surface(x, y) - (1 - h) * FT))
        walk_ext = concat(extension_pieces(end, side, lambda x, y, h: (1 - h) * R1.surface(x, y) +
                                           h * R1.walk(x, y)))
        rail, x0 = ttx_mesh(end, side)
        far = x0 + end * w['length']
        overhang = end * ((beyond[1] if end > 0 else beyond[0]) if beyond else x_end) - end * far
        if not -1e-3 < overhang < 1.0 * IN:
            raise ValueError(f'ttx_{end}_{side}: rail end {overhang / IN:.2f} in from the extension end')
        outer_len = abs(x_end - R1.sx(U_END[end], side * HALF)) + ((beyond[1] - beyond[0]) if beyond else 0)
        ext_dims = dict(width_m=round(EXT, 6), thickness_m=FT, length_at_coping_m=round(outer_len, 6))
        if beyond:
            ext_dims.update(beyond_square_end_m=[round(beyond[1] - beyond[0], 6), round(HALF - ROAD, 6)])
        add(f'approach_ext_{end}_{side}', slab, f'approach_{end}',
            f'Abutment {abut} | Wing {letter} RCBA slab extension ({compass})', 'approaches', [66, 67, 70, 71],
            'Sheet 66/67 plans and sheet 70 section C-C; 1 ft slab as the R.C. bridge approach',
            f'1 ft 2 in strip outside the 66 ft 2 in slab along the {compass} coping from the deck end, '
            + (f'{ftin(w["ext"][1])} long at the coping line ' if w['ext'][0] == 'corner' else 'to the square end ')
            + ('plus the 12 ft 2 1/2 in x 7 ft 3 in extension beyond the square end under the walk and the transition '
               if beyond else '')
            + f'(sheet 66 Wing "{letter}" and RCBA slab extension); top on the approach section, 1 ft thick '
              '(sheet 70 section C-C). Bears on the existing wing with 1 in expanded polystyrene (not modelled).',
            ext_dims)
        add(f'approach_walk_ext_{end}_{side}', walk_ext, f'approach_walk_{end}_{side}',
            f'Abutment {abut} | Wing {letter} sidewalk on the RCBA extension ({compass})', 'sidewalks',
            [66, sheet, 70],
            'Sheet 70 section C-C and sheet 68/69 sections D-D to G-G; walk surface as the approach sidewalk',
            'Sidewalk concrete over the slab extension, running under the transition to the slab edge (2 in ledge '
            'outside the rail, Type A construction joint at the rail base); top 1.5 % above an 8 in curb as the '
            'approach sidewalk' + (', and the full 7 ft 3 in walk beyond the square end (sheet 66).' if beyond else '.'),
            dict(width_m=round(EXT, 6)) | (dict(beyond_square_end_width_m=round(HALF - ROAD, 6)) if beyond else {}))
        windows = [round(WINDOW_FIRST + k * WINDOW_PITCH, 6) for k in range(WINDOWS)]
        add(f'ttx_{end}_{side}', rail, f'tx_{side}_0_0',
            f'Abutment {abut} | Wing {letter} modified TTX railing transition ({compass} coping)', 'rails',
            [66, sheet, 70, 71],
            f'Sheet {sheet} Wing "{letter}" elevation, sections D-D to G-G and window detail; sheet 66 plan',
            f'Concrete bridge railing transition, Type TTX, modified ({w["coping"]}): '
            f'{ftin(w["length"])} pay limits from the centre line of the 1/2 in '
            f'open joint at the end bent, measured along the traffic face; {ftin(w["h"])} high above the '
            'sidewalk' + (' with the 1 ft taller base' if w['plinth'] else '') + ', 1 ft 0 in wide, 2 in inside '
            'the slab-extension edge. End-bent pilaster 1 ft 4 1/2 in long, 2 in taller over its first 1 ft 1 1/2 in; '
            'six 6 in x 1 ft 4 in windows at 1 ft 6 in, the first 10 in beyond the pilaster, sill '
            f'{(WINDOW_SILL + w["plinth"]) / IN:.0f} in above the sidewalk, head of two R 1 ft 0 in arcs (rise 1 1/2 '
            'in scaled); square far end. Face recesses, the recessed panel taper, chamfers and pilaster notches are '
            'omitted (known_deviations ttx-face-recesses).',
            dict(pay_limit_length_m=round(w['length'], 6), height_m=round(w['h'], 6), window_head_radius_m=HEAD_R,
                 end_pilaster_height_m=round(w['h'] + RISE, 6), end_pilaster_length_m=round(PILASTER, 6),
                 width_m=FT, window_count=WINDOWS, window_spacing_m=round(WINDOW_PITCH, 6),
                 window_centres_from_joint_m=windows, window_sill_m=round(WINDOW_SILL + w['plinth'], 6)))
        ttx_record[f'Wing {letter}'] = dict(
            ttx=f'ttx_{end}_{side}', pay_limit=ftin(w['length']),
            rail_end_inside_extension_in=round(overhang / IN, 2), extension_length_at_coping_m=round(outer_len, 4))

    # ------------------------------------------------------------------ 2. field splices (S9, S10)
    bolt_counts = {}
    for j in range(8):
        ext = R1.exterior(j)
        src = 'S9' if ext else 'S10'
        cw, ct, cl = R2.COVER[ext]
        fw, ft, fl = R2.FILLER[ext]
        for si in range(2):
            pid = f'girder_{j + 1}_splice_{si + 1}'
            plates, fasteners, counts = splice_new(j, si)
            bolt_counts[pid] = counts
            label = ftin(cl)
            store(pid, plates, new_topology=True, replace_dims=True,
                  basis=f'{src} field splice (A & B) elevation and top view; S8 notes',
                  dims=dict(splice_plate_m=[cw, ct, cl], filler_plate_m=[fw, ft, fl],
                            web_plate_m=list(WEB_PLATE), splice_bar_m=[BAR[0], BAR[1], cl]),
                  note=f'{src} field splice: {cw / IN:.0f} in x {"7/8" if ext else "1"} in x {label} splice plates '
                       f'top and bottom on the outer faces of the pier flanges and of {cw / IN:.0f} in x '
                       f'{"1" if ext else "1/2"} in x {"3 ft 0 in" if ext else "3 ft 3 in"} fillers on the field '
                       'flanges, following the girder grade; webs aligned. Two 19 in x 5/8 in x 4 ft 6 in web plates '
                       f'centred on the web and the splice; 10 in x 1 in x {label} inner splice bars, two under each '
                       'flange, flush with the flange edges (3 in / 4 in / 3 in gauges). Fabrication holes omitted.')
            store(pid + '_bolts', fasteners, new_topology=True, replace_dims=True,
                  name=parts[pid + '_bolts']['name'].replace('visible web fasteners', 'web and flange bolts'),
                  basis=f'{src} field splice bolt pattern; S8 high-strength bolts 7/8 in',
                  dims=dict(bolt_count=counts['web'] + counts['flange'], web_bolt_count=counts['web'],
                            flange_bolt_count=counts['flange'], bolt_diameter_m=round(2 * BOLT_R, 6)),
                  note=f'{src}: web bolts 18 rows at 3 in (4 ft 3 in) in 6 columns 2 in, 5 in and 8 in either side of '
                       'the splice through both web plates; flange bolts in four lines '
                       f'({"6 in and 10 in" if ext else "5 in and 9 in"} from the web), {PER_SIDE[ext]} per line '
                       'either side of the splice at 3 in from 3 in, through the splice plate, filler, flange and '
                       'splice bar, top and bottom. 7/8 in bolts (S8 notes); heads and nuts are visual envelopes.')

    # ------------------------------------------------------------------ 1. bridge TX end pilasters (sheets 63, 64, 68, 69)
    # Sheet 63/64: the TX railing pay limits run to the end of the bridge floor, i.e. to the centre line of the 1/2 in
    # open joint (E 706-BRTX-01: pay limits centre line to centre line of joint); the railing ends 1/4 in short of it.
    for side in (-1, 1):
        for pid, u, sgn in ((f'txpost_{side}_0_0', R1.U0, 1), (f'txpost_{side}_1_5', R1.U1, -1)):
            mesh = native(pid)
            v = mesh.vertices.copy()
            face = np.abs(v[:, 0] + K * v[:, 1] - u) < 1e-4
            rise = v[face, 2] - R1.walk(v[face, 0], v[face, 1])
            v[face, 0] = R1.sx(u + sgn * JOINT / 2, v[face, 1])
            v[face, 2] = R1.walk(v[face, 0], v[face, 1]) + rise
            store(pid, trimesh.Trimesh(v, mesh.faces, process=False),
                  note=parts[pid]['note'] + ' End face 1/4 in short of the deck end, half the 1/2 in open joint to the '
                                            'TTX transition (sheets 63/64 pay limits to the end of the bridge floor, '
                                            'sheets 68/69).')

    # ------------------------------------------------------------------ 2. lateral bracing at its drawn connection (S11)
    braces = {}
    for bay in (0, 3, 6):
        for i in range(12):
            pid = f'lateral_{bay}_{i}'
            mesh, _ = lateral_new(bay, i)
            q0, q1, _, _ = lateral_ends(bay, i)
            v = mesh.vertices
            ends = [v[np.argsort(np.linalg.norm(v[:, :2] - q, axis=1))[:4]].mean(axis=0) for q in (q0, q1)]
            braces[(bay, i)] = (mesh, ends[0], ends[1])
            old = native(pid)
            same = len(mesh.vertices) == len(old.vertices) and np.array_equal(mesh.faces, old.faces)
            store(pid, mesh, new_topology=not same,
                  name=parts[pid]['name'].replace('Top lateral bracing', 'Bottom lateral bracing'),
                  basis='S8 framing plan (WT 6 x 18 laterals) and S11 cross frame XF-1, details C-E; envelope',
                  note='Representative WT 6 x 18 envelope (S8) on the 3/8 in lateral gusset plates, 5 in above the '
                       'bottom flange (S11 cross frame XF-1: gussets at the point of lateral bracing only), ending at '
                       'the flange tips where the tee bolts to the gusset (S11 details C-E). Gussets not modelled; '
                       'the generator had the laterals 0.14 m below the girder tops, running to the webs.')
    # S11 XF-1 / details C-E: one 3/8 in gusset per panel point, from the web face to the bolted ends of the tees;
    # notched (1 mm clear) around stiffeners, splice plates and bolts and cross-frame members it would otherwise cut
    import shapely
    gussets = {}
    for bay in (0, 3, 6):
        for r in range(13):
            here = [(braces[(bay, r - 1)][0], braces[(bay, r - 1)][2], braces[(bay, r - 1)][1])] if r else []
            here += [(braces[(bay, r)][0], braces[(bay, r)][1], braces[(bay, r)][2])] if r < 12 else []
            probe, poly = gusset_mesh(bay, r, here, [], pad=.002)      # the plain gusset, 2 mm thicker each way
            j = node_girder(bay, r)
            probe_m = manifold3d.Manifold(manifold3d.Mesh(np.asarray(probe.vertices, np.float32),
                                                          np.asarray(probe.faces, np.uint32)))
            cuts = []
            for name, m in meshes.items():
                if name in (f'girder_0_{j}', f'girder_1_{j}') or name.startswith('lateral_') or name not in parts:
                    continue
                part = native(name)
                if not ((part.bounds[0] < probe.bounds[1]).all() and (part.bounds[1] > probe.bounds[0]).all()):
                    continue
                for body in part.split(only_watertight=False):
                    if not ((body.bounds[0] < probe.bounds[1]).all() and (body.bounds[1] > probe.bounds[0]).all()):
                        continue
                    hit = (probe_m ^ manifold3d.Manifold(manifold3d.Mesh(np.asarray(body.vertices, np.float32),
                                                                          np.asarray(body.faces, np.uint32)))).to_mesh()
                    pts = np.asarray(hit.vert_properties)[:, :2]
                    if len(pts) >= 3:
                        cuts.append(shapely.MultiPoint([tuple(q) for q in pts]).convex_hull.buffer(.001))
            mesh, poly = gusset_mesh(bay, r, here, cuts)
            pid = f'lateral_gusset_{bay}_{r}'
            gussets[pid] = (mesh, poly, j, [f'lateral_{bay}_{i}' for i in (r - 1, r) if 0 <= i <= 11], len(cuts))

    # ------------------------------------------------------------------ 1. wing inner faces (sheet 70 section C-C)
    for pid in ('wing_1_-1', 'wing_1_1', 'wing_3_-1', 'wing_3_1'):
        mesh = native(pid)
        v = mesh.vertices.copy()
        side = np.sign(v[:, 1].mean())
        v[:, 1] += side * (HALF + WING_GAP - np.abs(v[:, 1]).min())
        store(pid, trimesh.Trimesh(v, mesh.faces, process=False),
              note=parts[pid]['note'] + ' Inner face 1 in outside the RCBA slab-extension edge (sheet 70 section C-C, '
                                        '1 in expanded polystyrene); plan, length and top are still the approximate '
                                        'envelope (see known_deviations retained-wing-envelopes).')

    for pid, (mesh, poly, j, lats, ncut) in gussets.items():
        bay, r = (int(q) for q in pid.split('_')[2:])
        add(pid, mesh, 'lateral_0_0',
            f'Bottom lateral bracing | gusset at girder {R1.plan_girder(j)}, cross-frame row {r + 1}', 'bracing', [99, 102],
            'S11 cross frame XF-1 and details C-E; plan outline fitted to the modelled lateral ends',
            '3/8 in gusset plate at the point of lateral bracing, 5 in above the bottom flange (S11 cross frame XF-1), '
            'from the web face to the bolted ends of the WT 6 x 18 laterals (12 in: four bolts at 3 in, S11 details '
            'C-E) that seat on it' + (f'; notched around {ncut} stiffener, splice or cross-frame '
                                      f'{"piece" if ncut == 1 else "pieces"}' if ncut else '') +
            '. Connection plates, welds and bolts are not modelled.',
            dict(thickness_m=round(GUSSET_T, 6), underside_above_bottom_flange_m=round(GUSSET_UP, 6),
                 bolted_length_m=round(BOLTED, 6), laterals=lats, plan_area_m2=round(float(poly.area), 4)))

    # ------------------------------------------------------------------ Pier 2 shoe stacks: drawn values recorded (S12, S13)
    metadata_only = []
    for j in range(8):
        pid = f'B2_bearing_{j + 1}'
        g = R1.plan_girder(j)
        mark = R1.SHOES[2][g - 1]
        p = parts[pid]
        p['dimensions'].update(drawn_shim_m=round(PIER_SHIM[g] * IN, 6),
                               drawn_stack_m=round(R1.SHOE_H[mark] + PIER_SHIM[g] * IN, 6))
        p['note'] += (f' S13 shim thickness table: {PIER_SHIM[g]:g} in at Pier 2, so the drawn stack is '
                      f'{(R1.SHOE_H[mark] + PIER_SHIM[g] * IN):.3f} m (see known_deviations pier2-shoe-stack).')
        meshes[pid]['extras'].update(p)
        metadata_only.append(pid)

    # ------------------------------------------------------------------ checks across parts
    soffit = []
    for j, y in enumerate(YS):
        for si in (1, 2):
            for pid in (f'girder_{j + 1}_splice_{si}', f'girder_{j + 1}_splice_{si}_bolts'):
                v = native(pid).vertices
                gap = float((R1.surface(v[:, 0], v[:, 1]) - SLAB - v[:, 2]).min())
                if gap <= 0:
                    raise ValueError(f'{pid} reaches the deck soffit')
                soffit.append(gap)
    for end, side in WINGS:
        rail = native(f'ttx_{end}_{side}').vertices
        foot = rail[np.abs(rail[:, 2] - R1.walk(rail[:, 0], rail[:, 1])) < 2e-5]
        if len(foot) < 4:
            raise ValueError(f'ttx_{end}_{side}: base not on the sidewalk surface')
        post = native(f'txpost_{side}_{0 if end < 0 else 1}_{0 if end < 0 else 5}').vertices
        gap = float(np.min(end * (rail[:, 0] - R1.sx(U_END[end], rail[:, 1]))))
        post_gap = float(np.min(-end * (post[:, 0] - R1.sx(U_END[end], post[:, 1]))))
        if gap < JOINT / 2 - 2e-5 or post_gap < JOINT / 2 - 2e-5:
            raise ValueError(f'ttx_{end}_{side}: open joint at the end bent not kept')
    for bay in (0, 3, 6):
        for i in range(12):
            v = native(f'lateral_{bay}_{i}').vertices
            near = np.min(np.abs(v[:, 1][:, None] - YS[None, :]), axis=1)
            if near.min() < 12 * IN - .01:
                raise ValueError(f'lateral_{bay}_{i}: reaches inside the flange tips')
    seat_gaps = []
    for pid, (mesh, poly, j, lats, ncut) in gussets.items():
        y = YS[j]
        for piece in getattr(poly, 'geoms', [poly]):
            if min(piece.distance(shapely.LineString([(-100, y + q * R1.TW / 2), (100, y + q * R1.TW / 2)]))
                   for q in (-1, 1)) > 1e-7:
                raise ValueError(f'{pid}: a piece is not on the web face')
        bay, r = (int(q) for q in pid.split('_')[2:])
        for i, lat in zip([q for q in (r - 1, r) if 0 <= q <= 11], lats):
            _, e0, e1 = braces[(bay, i)]
            a_end, b_end = (e1, e0) if i == r - 1 else (e0, e1)
            v = native(lat).vertices
            d = b_end - a_end
            corners = v[(v - a_end) @ d / (d @ d) < .5]
            q = (corners[:, None, :] + np.linspace(0, BOLTED / np.linalg.norm(d[:2]), 25)[None, :, None] *
                 d[None, None, :]).reshape(-1, 3)
            inside = np.array([poly.buffer(1e-4).contains(shapely.Point(x, yy)) for x, yy, _ in q])
            gap = q[inside, 2] - plane_top(node_plane(bay, r), q[inside, 0]) if inside.any() else np.array([np.inf])
            if not (-2e-5 < gap.min() < 2e-5):
                raise ValueError(f'{lat}: not seated on {pid} (gap {gap.min() * 1000:.3f} mm)')
            seat_gaps.append(float(gap.min()))

    # ------------------------------------------------------------------ manifest bookkeeping
    new_ids = {'rails': [], 'approaches': []}
    for pid in added:
        new_ids['rails' if pid.startswith('ttx_') else 'approaches'].append(pid)
    for d in manifest['detail_coverage']:
        if d['feature'] == 'Retained steel details':
            d['detail'] = d['detail'].replace('field-splice envelopes, visible web bolts',
                                              'field splices, splice bolts')
            d['detail'] += (' Splice web plates 19 in x 5/8 in x 4 ft 6 in with 108 web bolts, 10 in x 1 in inner '
                            'splice bars and four-line flange bolt patterns per S9/S10; bottom lateral bracing on the '
                            'S11 gusset level.')
        elif d['feature'] == 'Proposed architectural rails and walks':
            d['detail'] += (' Four modified TTX railing transitions (Wings A-D, sheets 68/69) on the approach-slab '
                            'extensions, six windows each; face recesses simplified.')
            d['part_ids'] += new_ids['rails']
        elif d['feature'] == 'Approaches, drainage and interfaces':
            d['detail'] = ('Both skew-to-square approach slabs, 66 ft 2 in wide with a 54 ft 2 in long edge at the '
                           'coping line (sheet 66), their walks, the four 1 ft 2 in RCBA slab extensions with the '
                           'sidewalk over them (Wing B also beyond the square end) and four drain envelopes. Drain '
                           'routing, slab penetrations, terminal joints, roadside terminals and traffic equipment are '
                           'not reconstructed.')
            d['part_ids'] += new_ids['approaches']
        elif d['feature'] == 'Unresolved exterior details':
            d['detail'] = d['detail'].replace('full transition geometry', 'TTX face recesses and notches')
    previous = {d['id']: d for d in manifest['known_deviations']}
    stack_text, short = [], []
    for j in range(8):
        pid = f'B2_bearing_{j + 1}'
        dm = parts[pid]['dimensions']
        stack_text.append(f'{pid} (girder {R1.plan_girder(j)}) {dm["derived_stack_m"]:.3f} / {dm["drawn_stack_m"]:.3f} m')
        short.append(dm['drawn_stack_m'] - dm['derived_stack_m'])
    under = []                                   # deck soffit to the underside of the top flange (sheet 65 Y-Y)
    for j, y in enumerate(YS):
        for u in np.linspace(-SPAN - R2.END_EXT, SPAN + R2.END_EXT, 601):
            under.append(float(R1.surface(R1.sx(u, y), y)) - SLAB - (R2.top_new(u, j) - R1.tf_new(u, j)))
    hmin = min(parts[k]['dimensions']['minimum_thickness_m'] for k in parts if k.startswith('haunch_'))
    hmax = max(parts[k]['dimensions']['maximum_thickness_m'] for k in parts if k.startswith('haunch_'))
    manifest['known_deviations'] = [
        dict(previous['pier2-shoe-stack'], source='S7, S8, S9, S12, S13 (PDF 98, 99, 100, 103, 104); sheets 52, 56, 59, '
                                                  '60, 65; S1 (PDF 92)',
             deviation='Envelopes run from the S7 seat steps to the girder bottoms. Modelled / drawn stack (S12 shoe '
                       'ES-1/ES-2 1 ft 6 in, ES-3 1 ft 4 in, plus the S13 Pier 2 shim): ' + ', '.join(stack_text) +
                       f'; every envelope is {min(short) * 1000:.0f}-{max(short) * 1000:.0f} mm short.',
             reason='The stack itself is drawn: sheet 56 keeps the Pier 2 shoes, S12 gives the shoe heights and S13 the '
                    'shims. Closing it means raising the girders at Pier 2 by the shortfall, and the plans do not give '
                    'the 2026 girder elevations that would allow that. On one datum, girder 1 would rise 28 mm into the '
                    '8 in slab on the sheet 52 grade. With the sheet 65 minimum (2 3/16 in from the slab soffit to the '
                    'underside of the top flange), the 1971 elevations (S7 seats with the S12/S13 stacks, and the S9 '
                    'top-of-splice table less the sheet 65 dead-load deflections) fit the 2026 deck only if they read '
                    '0.05-0.17 ft above the 2026 datum. Sheet 52 existing-deck elevations against the S1 profile '
                    'suggest about 0.20 ft, which would fit, but no sheet states the relation. Settled by '
                    'the 2026 screed (top-of-steel) elevations in the Letting Documents "Additional Information" '
                    '(sheet 59/60 notes) or a survey of the Pier 2 seats and girders.'),
        dict(previous['haunch-thickness'], source='sheets 52, 55, 59, 60, 65; S9, S10, S12, S18 (PDF 109)',
             deviation=f'With the 2 % deck over the retained girder tops the haunches are {hmin * 1000:.0f}-'
                       f'{hmax * 1000:.0f} mm thick above the top flange, and the slab soffit stands '
                       f'{min(under) * 1000:.0f}-{max(under) * 1000:.0f} mm above the underside of the top flange, '
                       'which meets the sheet 65 section Y-Y minimum of 2 3/16 in (55.6 mm, measured to the underside '
                       'of the top flange). The haunch profile itself is derived: the field segments sit 1 in (girders '
                       '1, 8) / 1/2 in lower than the pier segments, as the S9/S10 splices require, and the girder tops '
                       'follow the proposed grade less the deck and a nominal haunch.',
             reason='The haunch is the 2026 deck soffit minus the 2026 top of steel. The plans give the deck (sheets '
                    '52, 55, 60), the 2026 concrete dead-load deflections and the minimum haunch (sheet 65). For the '
                    'steel they give only 1971 data: the S9 top-of-splice elevations (steel dead load only), the S12 '
                    'no-load camber and the S18 deflections of the old deck. They give neither the 2026 top of steel nor '
                    'the 1971-to-2026 datum relation, and on one datum the 1971 steel stands above the 2026 soffit '
                    '(see pier2-shoe-stack). Settled by the 2026 screed elevations ("Additional Information", sheets '
                    '59/60) or a survey.'),
        dict(id='ttx-face-recesses', parts='ttx_*', source='sheets 68, 69 (sections D-D to G-G); E 706-BRTX-02',
             deviation='The transitions are the 1 ft 0 in (0.3048 m) envelope with through windows. Drawn but not '
                       'modelled: 1 in (25.4 mm) recesses on both faces leaving a 10 in (0.254 m) stem between 4 1/2 in '
                       'top and bottom bulbs (sections D-D, E-E, F-F, stem height 2 ft 7 1/2 in in D-D); the recess '
                       'tapering out ("Varies", F-F) over the segment that ends 16 ft 5 1/2 in (5.0165 m, Wings A, B, '
                       'D) or 15 ft 2 in (4.6228 m, Wing C) from the joint, beyond which section G-G is solid 1 ft 0 in '
                       'with 3/4 in chamfers (its 3 in - 6 in - 3 in are bar positions); the end-pilaster notches '
                       '(1 1/2 in). The bridge TX panels are simplified the same way.',
             reason='Still missing: the recessed panel outline in elevation. Sheets 68/69 do not dimension where the '
                    'recess starts at the end-bent pilaster, its corner radii, or the recess height at the end of the '
                    'taper (F-F says only "Varies"), and they refer the TTX details to Standard Drawing E 706-TTTX-01/-02, '
                    'which is not in the binder. That standard (or dimensioned elevations) would settle it.'),
        dict(id='retained-wing-envelopes', parts='wing_1_-1, wing_1_1, wing_3_-1, wing_3_1',
             source='S3-S6 (PDF 94-97); sheet 70 section C-C',
             deviation='The retained wings are 0.4 m x 5.2 m boxes parallel to the girders, with tops near the bridge '
                       'seat. S3-S6 dimension splayed wings 31 ft 0 in (9.4488 m) long at Abutment 1 and 23 ft 0 in '
                       '(7.0104 m) at Abutment 3, with stepped tops rising to El. 727.98 / 728.10 (Wing A, S4) at the '
                       'abutment, and sheet 70 section C-C draws the wing beside the slab extension up to about the '
                       'sidewalk. Only the inner face was moved, to 1 in outside the extension (C-C).',
             reason='The 1971 lengths, splays and top elevations are dimensioned (S3-S6), so the shape is not missing; '
                    'rebuilding it means four new splayed solids joined to the approximate abutment stems, which this '
                    'round does not attempt. Still missing for the 2026 state: the wing tops after the mudwall '
                    'removal (sheet 55 note), which no 2026 sheet dimensions; sheet 70 C-C shows the wing only '
                    'schematically. Settled by a 2026 wing detail or a survey; deferred to a generator rebuild.')]

    gltf['buffers'][0]['byteLength'] = len(binary)
    while len(binary) % 4:
        binary.append(0)
    gltf['buffers'][0]['byteLength'] = len(binary)
    encoded = json.dumps(gltf, ensure_ascii=True, separators=(',', ':')).encode()
    encoded += b' ' * ((-len(encoded)) % 4)
    out = (struct.pack('<III', 0x46546c67, 2, 28 + len(encoded) + len(binary)) +
           struct.pack('<II', len(encoded), 0x4e4f534a) + encoded + struct.pack('<II', len(binary), 0x004e4942) + binary)
    previous_revision = manifest.get('revision')
    manifest[TAG_KEY] = TAG
    manifest['revision'] = REVISION
    manifest['review_correction_record_3'] = dict(
        source_pdf_pages=[52, 56, 59, 60, 63, 64, 65, 66, 67, 68, 69, 70, 71, 92, 94, 95, 96, 97, 98, 99, 100, 101,
                          102, 103, 104, 109, 119, 120, 122],
        printed_sheets=['52', '56', '59', '60', '63', '64', '65', '66', '67', '68', '69', '70', '71', 'S1', 'S3',
                        'S4', 'S5', 'S6', 'S7', 'S8', 'S9', 'S10', 'S11', 'S12', 'S13', 'S18', 'E 706-BRTX-01',
                        'E 706-BRTX-02', 'E 706-BRTX-04'],
        previous_revision=previous_revision,
        corrections={
            'ttx-transitions': 'Resolved. Four modified TTX transitions (sheets 68/69: A 30 ft 2 in, B 29 ft 4 in, '
                               'C 17 ft 2 in, D 20 ft 5 1/2 in; 3 ft 6 in north, 4 ft 6 in south) on 1 ft 2 in RCBA '
                               'slab extensions with sidewalk concrete (sheets 66, 67, 70); Wing B extension 12 ft '
                               '2 1/2 in x 7 ft 3 in beyond the square end. Rail ends inside the extensions: ' +
                               ', '.join(f'{k} {v["rail_end_inside_extension_in"]} in' for k, v in
                                         ttx_record.items()) + '.',
            'approach_width': 'Approach slabs 66 ft 6 in -> 66 ft 2 in and approach walks 6 ft 3 in -> 6 ft 1 in '
                              '(sheet 66; sheet 70 section C-C), so the slab extensions sit beside them.',
            'splice-web-plates': 'Resolved. S9/S10: two 19 in x 5/8 in x 4 ft 6 in web plates, 10 in x 1 in inner '
                                 'splice bars (6 ft 3 in S9, 6 ft 9 in S10), 108 web bolts and 192 (S9) / 208 (S10) '
                                 'flange bolts per splice, 7/8 in (S8); flange splice plates and fillers unchanged.',
            'lateral_bracing': 'S11: the 36 lateral envelopes move to the gussets 5 in above the bottom flange, end '
                               'at the flange tips, and seat on 39 new 3/8 in gusset plates (one per panel point) '
                               'that run from the web face to the 12 in bolted ends of the tees; clear of the '
                               'splice bars and bolts.',
            'tx_end_pilasters': 'The four bridge TX end pilasters stop 1/4 in short of the deck-end line, giving the '
                                'full 1/2 in open joint to the transitions (sheets 63, 64, 68, 69).',
            'wings': 'Wing inner faces 1 in outside the slab extensions (sheet 70 section C-C), was 80 mm inside.',
            'pier2_shoe_records': 'B2 shoe envelopes record the S13 Pier 2 shims and the drawn stacks (metadata only).'},
        decisions={
            'TTX pay limit line': 'Sheets 68/69 dimension the pay limits on the elevation, not in plan, and the deck-end '
                                  'joint is skewed. Measured along the traffic face from the joint centre line, Wing C '
                                  '(17 ft 2 in) equals the sheet 66 short edge at that line (17 ft 2.0 in in the model) '
                                  'and Wing B (29 ft 4 in) leaves 12 ft 2 in beyond the square end, 1/2 in inside the '
                                  'drawn 12 ft 2 1/2 in extension, as the elevations show; the coping-line reading '
                                  'would overrun the Wing C slab by 6.6 in.',
            'Approach slab width': 'Sheet 66 writes 66 ft 2 in (99 spa. @ 8 in + 2 x 3 in) and 68 ft 6 in only with '
                                   'the 1 ft 2 in extensions; the generator\'s 66 ft 6 in has no source.',
            'End-bent joint': 'Sheets 63/64 run the bridge TX pay limits to the end of the bridge floor and sheets '
                              '68/69 start the TTX pay limits at the centre line of the 1/2 in open joint, so the '
                              'joint centre line is the deck-end line: the bridge end pilasters stop 1/4 in short of '
                              'it and the transitions start 1/4 in beyond it.',
            'Transition end margins': 'Sheets 68/69 draw the slab 1/2 in beyond each pay limit. The written pay '
                                      'limits (68/69) and the written extension lengths of sheet 66 (30 ft 10 1/2 '
                                      'in, 12 ft 2 1/2 in, the 17 ft 2 in short edge, 21 ft 1 1/2 in; plan '
                                      'dimensions to the inch) are kept, which leaves margins of 20.5, 13.4, 0.7 and '
                                      '7.8 mm at Wings A-D. Wing C cannot meet the 1/2 in without moving the sheet '
                                      '66 square end (54 ft 2 in long edge) or shortening the 17 ft 2 in pay limit; '
                                      'neither sheet governs the other, so both written values are kept.',
            'Window head': 'Window detail: R 1 ft 0 in arcs; the head rise is not dimensioned on sheets 68/69 or E '
                           '706-BRTX-02 and is scaled from the window detail (1 1/2 in).',
            'Lateral bracing level': 'S11 cross frame XF-1 places the 3/8 in gussets at the point of lateral '
                                     'bracing 5 in above the bottom flange, and details C-E end the WT 6 x 18 '
                                     'laterals on them outside the flange tips. The generator had top laterals, '
                                     'which ran into the new splice bars and nuts.'},
        kept={d['id']: d['reason'] for d in manifest['known_deviations']},
        changed_parts=changed, added_parts=added, removed_parts=[], renamed_parts=renamed,
        metadata_only_parts=metadata_only,
        before_glb_sha256=before, after_glb_sha256=hashlib.sha256(out).hexdigest())
    record = manifest['review_correction_record_3']
    print(json.dumps({k: (v if k not in ('changed_parts', 'added_parts', 'renamed_parts') else f'{len(v)} parts')
                      for k, v in record.items()}, indent=1))
    print(f'splice clearance to the deck soffit >= {min(soffit) * 1000:.1f} mm; bolts '
          f'{sum(c["web"] + c["flange"] for c in bolt_counts.values())}')
    if dry_run:
        print('Dry run, nothing written.')
        return out, manifest
    backup.mkdir(exist_ok=True)
    (backup / f'{BID}_before_review_correction_3.glb').write_bytes(original)
    (backup / f'{BID}_manifest_before_review_correction_3.json').write_bytes(raw_manifest)
    path.write_bytes(out)
    mp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return out, manifest


if __name__ == '__main__':
    correct(dry_run='--dry-run' in sys.argv)

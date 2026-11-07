"""One-time, drawing-confirmed correction of US 50 EB over Tanners Creek (us50-tanners-eb), preserving the GLB
buffers of the parts it does not change.

    python scripts/correct_us50_tanners_eb_review.py

Source: drawings.pdf, 2014 B-29709 reconstruction. Printed sheet N is PDF page N + 86 (sheet 20 = PDF 106).
Native axes: X along Line "A" stations (X = 0 is the midpoint of Bents 1 and 6 on the structure centre line),
Y to the LEFT of increasing station (north), Z = El. - 450 ft in metres. The GLB stores its vertices already turned
to glTF Y-up, (X, Z, -Y); the script converts both ways.

1. Orientation (sheets 20-22 plans with north arrow, sheet 23 section A-A looking up-station, sheets 26/29/34/43):
   stations increase to the east; the FT barrier, beam 1 and Line "A" (4 ft 7 in from the structure centre line)
   are on the north (left, +Y) side and the 13 ft 8 in sidewalk with the PS-1 railing on the south (right, -Y)
   side. The north end of every support is at the lower station ("Skew 20 deg Lt."); the bent-1 seat schedule
   (483.100 ... 482.965 for beams 1 ... 7) closes to 0.003 ft only with that skew sense. The model had the support
   skew right (X = u - tan20 Y) but the whole transverse layout mirrored: sidewalk, PS-1, crown and beam 7 on +Y.
   Every part is mirrored about Y = 0 and re-skewed, (x, y) -> (x + 2 tan20 y, -y), so the supports keep their plan
   lines while the transverse layout moves to the correct side; beams, bearings, X frames and PS-1 posts are moved
   as rigid bodies (x + 2 tan20 y_centre) so their sections are not sheared. Part ids keep their meaning
   (beam 1 / column 1 stay the north members).
2. Profile grade (sheet 7 profile, sheets 20-22: P.I. Sta. 389+40.58 El. 490.90, +0.30 % / -0.32 %, 430 ft
   vertical curve; P.G. at Bents 1-6 490.08, 490.32, 490.52, 490.56, 490.42, 490.21): the model used the PVI
   elevation as the curve elevation (0.333 ft high) and continued the parabola past the PVC/PVT, so the deck was
   0.100-0.107 m high at every bent. All grade-following geometry is re-referenced to the true profile.
3. Bent caps (sheets 26, 29, 34, 35, 39): soffits El. 479.69 (Bent 1), 477.78 (2, 5), 477.92 (3, 4), 479.77 (6);
   end-bent caps 76 ft 5 1/2 in, beam 1 4 ft 1 7/8 in from the north end; interior caps 74 ft 3 in, beam 1
   3 ft 6 3/4 in from the north end (so they sit 0.141 m north of the deck centre line). The end bents are
   semi-integral: sheets 26/29 (section along the bent) and 32 (section B-B) show the 3 ft 9 in end-bent concrete
   carried up to the slab soffit around the beam ends; cap_0 / cap_5 become that body with beam pockets.
4. Columns (sheets 26, 29, 35, 39): end bents 3 ft square at 23 ft 3 in, 23 ft 3 in, 10 ft 6 in, the first
   10 ft 10 3/4 in from the north cap end; interior bents 4 ft square at 25, 25, 11 ft 6 in, the first 8 ft 6 in
   from the north cap end; Bents 3 and 4 widen to 4 ft 6 in square below El. 459.67. Square sections are aligned
   with the bent (the model had 70/110 degree parallelograms and the interior-bent spacing at the end bents).
   Bases on the footing tops El. 468.75, 456.75, 436.25, 436.25, 456.75, 469.50; footing bottoms 464.25, 450.25,
   429.25 (the hidden footing envelopes keep their plan size; their levels follow the same sheets).
5. Tie beams, Bents 3 and 4 (sheet 39): 4 ft deep, 2 ft 9 in wide, El. 453.42 to 457.42 (the model used El. 457.42
   as the bottom, 2 ft 3 in deep and 4 ft 6 in wide). The end haunches up to El. 459.67 stay omitted.
6. Bulb-T beams (sheets 43, 45): beam ends 3 in from the interior bent centre lines and 9 in beyond the end-bent
   bearing centre lines (model: 0.15 m short of the interior bents and 0.01 m short of the end bents); section
   8 in bulb, 9 in taper, 3 ft 2 in web, 3 in fillet, 4 in flange taper and 4 in flange edge (the model had an
   8 in flange edge). Haunches follow the beam ends. Beam ends stay square to the beam.
7. Sidewalk (sheet 23 section A-A, sheet 53): 8 in curb, top rising 2 % toward the PS-1 railing (the model fell
   2 % outward). The PS-1 parapet keeps 2 ft 0 in above the corrected sidewalk and now sits on the deck slab
   (the model left it 0.2 m above the deck); the PS-1 rails and posts rise 0.169824 m with it.
8. Approach slabs (sheets 58, 60): square terminal joints; 20 ft 6 in on the north edge of the west slab and the
   south edge of the east slab, 46 ft 9 1/4 in on the other edges (the model had 20 ft 6 in parallelograms).

Deferred (recorded as known deviations): the four wingwalls (sheets 26, 28, 29) and the 3 ft concrete support
diaphragms at Bents 2-5 (sheets 43, 54) need new components with their own part ids; the bearing-seat schedule is
not imposed (beams keep a uniform 0.10 m haunch, so seats are within 0.03 m at the interior bents and about 0.09 m
low at the encased end-bent bearings); beam ends stay square; tie-beam end haunches stay omitted.

Requires numpy, trimesh and manifold3d.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

import manifold3d
import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'data/bridges/us50-tanners-eb'
BID = 'us50-tanners-eb'
TAG = 'review-2026-11-orientation-grade-bents-beams-walk-approaches'
REVISION = '1.1-drawing-review'

FT, IN = 0.3048, 0.0254
T = np.tan(np.radians(20.0))
K = -T                                    # support lines X = u + K Y (north end at the lower station)
C = np.cos(np.radians(20.0))
SPANS_FT = np.array([82 + 2.125 / 12, 105 + 7.5 / 12, 113.75, 105 + 7.5 / 12, 81 + 11.75 / 12])
BS = np.r_[0, np.cumsum(SPANS_FT * FT)] - SPANS_FT.sum() * FT / 2      # bent u at Y = 0
L = (492 + .125 / 12) * FT                # deck length along u (model value, kept)
W = (72 + 2 / 12) * FT
SLAB, CLEAR, D = 8 * IN, 0.10, 66 * IN
CROWN_OLD = -(4 + 7 / 12) * FT
CROWN = -CROWN_OLD                        # Line "A" 4 ft 7 in north of the structure centre line
YS_OLD = -W / 2 + (4 + 1 / 12) * FT + np.arange(7) * (10 + 10 / 12) * FT
YS = -YS_OLD                              # beam 1 north (+Y) ... beam 7 south
CENTRE_STA = 38667.49 + SPANS_FT.sum() / 2

# Bulb-T outline (half-width, height) in inches.
PROFILE_OLD = [(-12.5, 0), (12.5, 0), (12.5, 8), (3.5, 17), (3.5, 54), (27, 58), (30, 58), (30, 66), (-30, 66),
               (-30, 58), (-27, 58), (-3.5, 54), (-3.5, 17), (-12.5, 8)]
PROFILE = [(-12.5, 0), (12.5, 0), (12.5, 8), (3.5, 17), (3.5, 55), (6.5, 58), (30, 62), (30, 66), (-30, 66),
           (-30, 62), (-6.5, 58), (-3.5, 55), (-3.5, 17), (-12.5, 8)]

SOFFIT_EL = [479.69, 477.78, 477.92, 477.92, 477.78, 479.77]
FOOT_TOP_EL = [468.75, 456.75, 436.25, 436.25, 456.75, 469.50]
FOOT_BOTTOM_EL = [464.25, 450.25, 429.25, 429.25, 450.25, 464.25]
STEP_EL = 459.67                          # Bents 3/4 columns widen to 4 ft 6 in below this level
TIE_EL = (453.42, 457.42)
# North cap end (Y) and column centres measured along the bent from it (ft).
END_NORTH = YS[0] + (4 + 1.875 / 12) * FT * C
END_LENGTH_FT = 76 + 5.5 / 12
END_COLUMNS_FT = np.cumsum([9 + 4.75 / 12 + 1.5, 23.25, 23.25, 10.5])
INT_NORTH = YS[0] + (3 + 6.75 / 12) * FT * C
INT_LENGTH_FT = 74.25
INT_COLUMNS_FT = np.cumsum([8.5, 25, 25, 11.5])
WALK_IN, WALK_OUT = (21 + 5 / 12) * FT, W / 2 - FT          # sidewalk |Y| 6.5278 .. 10.6934
CURB = 8 * IN
PS1_RISE = 2 * 0.02 * (WALK_OUT - WALK_IN) + CURB - 0.2      # 0.169824
APPROACH_SHORT = 20.5 * FT
SOURCE_PAGES = [93, 106, 107, 108, 109, 112, 115, 118, 120, 121, 125, 129, 131, 139, 144, 146]
PRINTED_SHEETS = [p - 86 for p in SOURCE_PAGES]


def z_el(el):
    return (np.asarray(el, dtype=float) - 450.0) * FT


def grade_old(x):
    pvi = (38940.58 - CENTRE_STA) * FT
    x = np.asarray(x, dtype=float)
    return 12.47 - .0001 * (x - pvi) - .0062 * (x - pvi) ** 2 / (2 * 430 * FT)


def grade(x):
    """Profile grade on Line "A" (sheet 7): P.I. 389+40.58 El. 490.90, +0.30 % / -0.32 %, L = 430 ft."""
    sta = CENTRE_STA + (np.asarray(x, dtype=float) + T * CROWN) / FT    # station of Line "A" at this X
    s = sta - (38940.58 - 215.0)
    el = 490.90 - .003 * 215 + .003 * s - .0062 / 860 * np.clip(s, 0, 430) ** 2 - .0062 * np.maximum(s - 430, 0)
    return z_el(el)


class Geom:
    """The original builder's construction rules for one state (old: as modelled, new: corrected)."""

    def __init__(self, new):
        self.new = new
        self.crown = CROWN if new else CROWN_OLD
        self.grade = grade if new else grade_old
        self.ys = YS if new else YS_OLD

    def sx(self, u, y):
        return u + K * y

    def surf(self, x, y):
        return self.grade(x) - 0.02 * np.abs(np.asarray(y) - self.crown)

    def beam_bottom(self, u, y):
        return self.surf(self.sx(u, y), y) - SLAB - CLEAR - D


def loft(profile, stations, fn):
    """Closed solid: the 2-D profile (a, b) placed at each station s by fn(s, a, b) -> (x, y, z)."""
    pr = np.asarray(profile, dtype=float)
    if np.sum(pr[:, 0] * np.roll(pr[:, 1], -1) - np.roll(pr[:, 0], -1) * pr[:, 1]) < 0:
        pr = pr[::-1]
    k = len(pr)
    vertices = np.array([fn(float(s), a, b) for s in stations for a, b in pr], dtype=float)
    faces = []
    for i in range(len(stations) - 1):
        a0, b0 = i * k, (i + 1) * k
        for j in range(k):
            jj = (j + 1) % k
            faces += [(a0 + j, a0 + jj, b0 + jj), (a0 + j, b0 + jj, b0 + j)]
    tri = np.asarray(manifold3d.triangulate([pr]), dtype=np.int64)
    p = pr[tri]
    area = (p[:, 1, 0] - p[:, 0, 0]) * (p[:, 2, 1] - p[:, 0, 1]) - (p[:, 2, 0] - p[:, 0, 0]) * (p[:, 1, 1] - p[:, 0, 1])
    tri = np.where((area < 0)[:, None], tri[:, ::-1], tri)
    faces = np.vstack([np.array(faces), tri[:, ::-1], tri + (len(stations) - 1) * k])
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
    if not (mesh.is_watertight and mesh.is_winding_consistent):
        raise ValueError('invalid loft')
    if mesh.volume < 0:
        mesh.invert()
    return mesh


def bars(u0, u1, step=.6, minimum=2):
    return np.linspace(u0, u1, max(minimum, int((u1 - u0) / step) + 1))


def slab(g, u0, u1, y0, y1, thick, offset=0.0):
    yy = sorted(set([y0, y1] + ([g.crown] if y0 < g.crown < y1 else [])))
    profile = [(y, -thick) for y in yy] + [(y, 0) for y in reversed(yy)]
    return loft(profile, bars(u0, u1), lambda u, y, z: (g.sx(u, y), y, g.surf(g.sx(u, y), y) + offset + z))


def transverse(g, u, thick, y0, y1, z0, z1):
    """Box along the support line u, thickness measured normal to the skew (the builder's m.transverse)."""
    return loft([(y0, z0), (y1, z0), (y1, z1), (y0, z1)], [-thick / 2 / C, thick / 2 / C],
                lambda t, y, z: (g.sx(u + t, y), y, z))


def box(x0, x1, y0, y1, z0, z1):
    m = trimesh.creation.box(extents=[x1 - x0, y1 - y0, z1 - z0])
    m.apply_translation([(x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2])
    return m


def beam_ends(i, new):
    a, b = BS[i], BS[i + 1]
    if new:
        return a + (-9 * IN if i == 0 else 3 * IN), b + (9 * IN if i == 4 else -3 * IN)
    return a + (.01 if i == 0 else .15), b - (.01 if i == 4 else .15)


def beam(g, i, j):
    ga, gb = beam_ends(i, g.new)
    y = g.ys[j]
    pr = np.array(PROFILE if g.new else PROFILE_OLD) * IN
    return loft(pr, np.linspace(ga, gb, max(3, int((gb - ga) / .6) + 1)),
                lambda u, v, z: (g.sx(u, y), y + v, g.surf(g.sx(u, y), y) - SLAB - CLEAR - D + z))


def haunch(g, i, j, lift=0.0, drop=0.0):
    """lift / drop enlarge the solid upward / downward; used only for boolean cutters."""
    ga, gb = beam_ends(i, g.new)
    y, w = g.ys[j], 60 * IN
    return loft([(-w / 2, 0), (w / 2, 0), (w / 2, 1), (-w / 2, 1)], np.linspace(ga, gb, max(3, int((gb - ga) / .7))),
                lambda u, v, t: (g.sx(u, y), y + v, (1 - t) * (g.surf(g.sx(u, y), y) - SLAB - CLEAR - drop)
                                 + t * (g.surf(g.sx(u, y), y + v) - SLAB + lift)))


def bearing_u(i, end):
    return BS[i] + (0 if i == 0 else FT) if end == 'start' else BS[i + 1] - (0 if i == 4 else FT)


def bearing(g, i, j, end):
    u, y = bearing_u(i, end), g.ys[j]
    x, bottom = g.sx(u, y), g.beam_bottom(u, y)
    px, py = 22 * IN, 23.5 * IN
    return trimesh.util.concatenate([box(x - px / 2, x + px / 2, y - py / 2, y + py / 2, bottom - 2.5 * IN, bottom - .5 * IN),
                                     box(x - px / 2, x + px / 2, y - py / 2, y + py / 2, bottom - .5 * IN, bottom)])


def rows(bi):
    return [BS[bi]] if bi in (0, 5) else [BS[bi] - FT, BS[bi] + FT]


def seat(g, bi):
    return min(g.beam_bottom(ur, y) - 2.5 * IN for ur in rows(bi) for y in g.ys)


def peds(g, bi):
    out = {}
    s = seat(g, bi)
    for j, y in enumerate(g.ys):
        for ri, ur in enumerate(rows(bi)):
            ss = g.beam_bottom(ur, y) - 2.5 * IN
            if ss > s:
                out[f'ped_{bi}_{j}_{ri}'] = transverse(g, ur, .65, y - .34, y + .34, s, ss)
    return out


def old_column_ys():
    ys = np.array([-25, 0, 25, 36.5]) * FT * C
    return ys - np.mean([ys[0], ys[-1]])


OLD_FOOT_BOTTOM = [4.5, .0762, -6.3246, -6.3246, .0762, 4.3434]


def old_cap(g, bi):
    end = bi in (0, 5)
    s = seat(g, bi)
    half = (75 if end else 74.25) * FT * C / 2
    return transverse(g, BS[bi], (3.75 if end else 4.5) * FT, -half, half, s - (1.1 if end else 1.4), s)


def old_column(g, bi, j):
    end = bi in (0, 5)
    w = (3 if end else 4) * FT
    y = old_column_ys()[j]
    top = seat(g, bi) - (1.1 if end else 1.4)
    return transverse(g, BS[bi], w, y - w * C / 2, y + w * C / 2, OLD_FOOT_BOTTOM[bi] + (1.6 if end else 2.13), top)


def new_column_ys(bi):
    end = bi in (0, 5)
    north, chain = (END_NORTH, END_COLUMNS_FT) if end else (INT_NORTH, INT_COLUMNS_FT)
    return north - chain * FT * C


AXIS_BENT = np.array([K, 1.0]) * C        # unit plan vector along the support line (toward +Y)
AXIS_NORMAL = np.array([1.0, -K]) * C     # unit plan vector normal to the support line (toward +X)


def bent_point(bi, p, q):
    """Plan point p along the support line from its Y = 0 point and q normal to it."""
    return np.array([BS[bi], 0.0]) + p * AXIS_BENT + q * AXIS_NORMAL


def square_prism(bi, yc, side, z0, z1):
    pc = yc / C                           # distance along the bent from Y = 0
    return loft([(-side / 2, -side / 2), (side / 2, -side / 2), (side / 2, side / 2), (-side / 2, side / 2)], [z0, z1],
                lambda z, p, q: (*bent_point(bi, pc + p, q), z))


def new_column(bi, j):
    yc = new_column_ys(bi)[j]
    base, top = float(z_el(FOOT_TOP_EL[bi])), float(z_el(SOFFIT_EL[bi]))
    if bi in (0, 5):
        return square_prism(bi, yc, 3 * FT, base, top)
    if bi in (1, 4):
        return square_prism(bi, yc, 4 * FT, base, top)
    step = float(z_el(STEP_EL))
    origin = np.array([*bent_point(bi, yc / C, 0.0), step])
    lower, upper = square_prism(bi, yc, 4.5 * FT, base, step), square_prism(bi, yc, 4 * FT, step, top)
    m = from_manifold(to_manifold(lower, origin) + to_manifold(upper, origin), origin)
    if not m.is_watertight:
        raise ValueError('invalid stepped column')
    return m


def new_tie(bi):
    ys = new_column_ys(bi)
    p0, p1 = ys[-1] / C, ys[0] / C
    z0, z1 = map(float, z_el(TIE_EL))
    w = (2 + 9 / 12) * FT
    return loft([(p0, z0), (p1, z0), (p1, z1), (p0, z1)], [-w / 2, w / 2], lambda q, p, z: (*bent_point(bi, p, q), z))


def cap_extent(bi):
    end = bi in (0, 5)
    north = END_NORTH if end else INT_NORTH
    return north - (END_LENGTH_FT if end else INT_LENGTH_FT) * FT * C, north


def sidewalk(g):
    if not g.new:
        return slab(g, -L / 2, L / 2, WALK_IN, WALK_OUT, .2032, .2)
    y_out, y_in = -WALK_OUT, -WALK_IN

    def fn(u, y, t):
        x = g.sx(u, y)
        bottom = g.surf(x, y)
        top = g.surf(x, y_in) + CURB + 0.02 * (y_in - y)
        return x, y, bottom + t * (top - bottom)
    return loft([(y_out, 0), (y_in, 0), (y_in, 1), (y_out, 1)], bars(-L / 2, L / 2), fn)


def ps1_base(g):
    if not g.new:
        return slab(g, -L / 2, L / 2, WALK_OUT, W / 2, .61, .81)

    def fn(u, y, t):
        x = g.sx(u, y)
        return x, y, g.surf(x, y) + t * (.81 + PS1_RISE)
    return loft([(-W / 2, 0), (-WALK_OUT, 0), (-WALK_OUT, 1), (-W / 2, 1)], bars(-L / 2, L / 2), fn)


def approach(g, side):
    if not g.new:
        a, b = sorted([side * (L / 2 + .025), side * (L / 2 + .025 + APPROACH_SHORT)])
        return slab(g, a, b, -W / 2, W / 2, FT)
    terminal = side * (L / 2 + .025 + T * W / 2 + APPROACH_SHORT)     # square joint: 20 ft 6 in at the short edge
    longest = abs(terminal - g.sx(side * (L / 2 + .025), side * W / 2))
    yy = [-W / 2, g.crown, W / 2]
    profile = [(y, -FT) for y in yy] + [(y, 0) for y in reversed(yy)]

    def fn(s, y, z):
        x0 = g.sx(side * (L / 2 + .025), y)
        x = x0 + s * (terminal - x0)
        return x, y, g.surf(x, y) + z
    return loft(profile, bars(0, 1, step=.6 / longest), fn)


def end_body(g, bi, groups):
    """Semi-integral end bent: 3 ft 9 in concrete from the cap soffit to the slab soffit, minus a pocket for each
    beam (beam, haunch, bearing and pedestal as one cutter) and the approach-slab seat."""
    y0, y1 = cap_extent(bi)
    soffit = float(z_el(SOFFIT_EL[bi]))
    h = 3.75 * FT / 2 / C

    def fn(t, y, f):
        x = g.sx(BS[bi] + t, y)
        return x, y, soffit if f == 0 else float(g.surf(x, y)) - SLAB
    origin = np.array([BS[bi], 0.0, soffit])    # booleans in local coordinates (manifold3d works in float32)
    body = to_manifold(loft([(y0, 0), (y1, 0), (y1, 1), (g.crown, 1), (y0, 1)], [-h, h], fn), origin)
    cutters = [to_manifold(c, origin) for grp in groups for c in grp]
    result = body - manifold3d.Manifold.batch_boolean(cutters, manifold3d.OpType.Add)
    left = max((result ^ c).volume() for c in cutters)
    if left > 1e-6:
        raise ValueError(f'end-bent body still overlaps a cutter by {left:.6f} m3')
    m = from_manifold(result, origin)
    if not m.is_watertight or m.volume <= 0:
        raise ValueError('invalid end-bent body')
    return m


def to_manifold(mesh, origin):
    return manifold3d.Manifold(manifold3d.Mesh(vert_properties=np.asarray(mesh.vertices - origin, dtype=np.float32),
                                               tri_verts=np.asarray(mesh.faces, dtype=np.uint32)))


def from_manifold(solid, origin):
    out = solid.to_mesh()
    return trimesh.Trimesh(vertices=np.asarray(out.vert_properties, dtype=np.float64)[:, :3] + origin,
                           faces=np.asarray(out.tri_verts, dtype=np.int64), process=False)


def mirror(v, rigid_blocks=None, lift=0.0):
    """(x, y, z) -> (x + 2 tan20 y, -y, z + grade change); rigid blocks of vertices move with their centre."""
    v = np.asarray(v, dtype=float)
    out = np.empty_like(v)
    if rigid_blocks is None:
        out[:, 0] = v[:, 0] + 2 * T * v[:, 1]
        out[:, 2] = v[:, 2] + grade(out[:, 0]) - grade_old(v[:, 0]) + lift
    else:
        for blk in rigid_blocks:
            lo, hi = v[blk].min(axis=0), v[blk].max(axis=0)
            xc, yc = (lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2
            out[blk, 0] = v[blk, 0] + 2 * T * yc
            out[blk, 2] = v[blk, 2] + grade(xc + 2 * T * yc) - grade_old(xc) + lift
    out[:, 1] = -v[:, 1]
    return out


def same_shape(a, b, tol=2e-4):
    """Same vertex count, vertex sets within tol both ways and equal volume: the generator reproduces the part."""
    va, vb = np.asarray(a.vertices, dtype=float), np.asarray(b.vertices, dtype=float)
    if len(va) != len(vb):
        return False

    def reach(p, q):
        return max(np.sqrt(((p[i:i + 256, None, :] - q[None, :, :]) ** 2).sum(-1)).min(axis=1).max()
                   for i in range(0, len(p), 256))
    return max(reach(va, vb), reach(vb, va)) < tol and abs(a.volume - b.volume) < 1e-3 * max(1.0, abs(b.volume))


def correct(base=BASE, backup_dir=ROOT / 'data/fem_research'):
    mp = base / 'model_manifest.json'
    manifest = json.loads(mp.read_text(encoding='utf-8'))
    if manifest.get('drawing_review_correction') == TAG:
        print('Already corrected.')
        return
    if 'revision' in manifest:
        raise ValueError('Manifest is not the original generator revision.')
    path = base / 'model.glb'
    original = path.read_bytes()
    length = struct.unpack_from('<I', original, 12)[0]
    gltf = json.loads(original[20:20 + length])
    binary = bytearray(original[28 + length:])
    before = hashlib.sha256(original).hexdigest()
    parts = {p['id']: p for p in manifest['parts']}
    meshes = {m['name']: m for m in gltf['meshes']}
    if set(parts) != set(meshes) or len(parts) != 283:
        raise ValueError('Unexpected part inventory.')

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

    old, new = Geom(False), Geom(True)

    # ---- The model must be in the generator state this script was written against. ----
    checks = {f'bulbt_{i}_{j}': beam(old, i, j) for i in range(5) for j in (0, 3, 6)}
    checks.update({f'haunch_{i}_{j}': haunch(old, i, j) for i in (0, 2, 4) for j in (0, 6)})
    checks.update({f'Span_{chr(65 + i)}_beam_{j + 1}_{e}_bearing': bearing(old, i, j, e)
                   for i in (0, 4) for j in (0, 6) for e in ('start', 'end')})
    checks.update({f'cap_{bi}': old_cap(old, bi) for bi in range(6)})
    checks.update({f'column_{bi}_{j}': old_column(old, bi, j) for bi in (0, 2) for j in range(4)})
    for bi in (0, 2):
        checks.update(peds(old, bi))
    checks.update(sidewalk=sidewalk(old), ps1_base=ps1_base(old))
    checks.update({f'approach_{s}': approach(old, s) for s in (-1, 1)})
    for pid, mesh in checks.items():
        if not same_shape(mesh, stored(pid)):
            raise ValueError(f'{pid}: stored geometry is not the expected original')
    tie = stored('tie_2').bounds
    if not np.allclose(tie[:, 2], [z_el(457.42), z_el(457.42) + 2.25 * FT], atol=1e-4):
        raise ValueError('tie_2: unexpected original elevations')
    if not np.allclose(stored('ft_rail').bounds[:, 1], [-W / 2, -W / 2 + 1.5 * FT], atol=1e-4):
        raise ValueError('ft_rail: expected on -Y before the correction')
    for bi in range(6):
        ids = {p for p in parts if p.startswith(f'ped_{bi}_')}
        if ids != set(peds(old, bi)):
            raise ValueError(f'ped_{bi}_*: unexpected pedestal set')

    # ---- Corrected geometry. ----
    out = {}
    for i in range(5):
        for j in range(7):
            out[f'bulbt_{i}_{j}'] = beam(new, i, j)
            out[f'haunch_{i}_{j}'] = haunch(new, i, j)
            for e in ('start', 'end'):
                out[f'Span_{chr(65 + i)}_beam_{j + 1}_{e}_bearing'] = bearing(new, i, j, e)
    seats = {}
    for bi in range(6):
        new_peds = peds(new, bi)
        if set(new_peds) != {p for p in parts if p.startswith(f'ped_{bi}_')}:
            raise ValueError(f'ped_{bi}_*: corrected pedestal set differs')
        out.update(new_peds)
        seats[bi] = seat(new, bi)
        for j in range(4):
            out[f'column_{bi}_{j}'] = new_column(bi, j)
        if bi in (2, 3):
            out[f'tie_{bi}'] = new_tie(bi)
    for s in (-1, 1):
        out[f'approach_{s}'] = approach(new, s)
    for bi in (1, 2, 3, 4):
        y0, y1 = cap_extent(bi)
        if seats[bi] - float(z_el(SOFFIT_EL[bi])) < 1.0:
            raise ValueError(f'cap_{bi}: corrected cap too shallow')
        out[f'cap_{bi}'] = transverse(new, BS[bi], 4.5 * FT, y0, y1, float(z_el(SOFFIT_EL[bi])), seats[bi])
    for bi, i, e, s in ((0, 0, 'start', -1), (5, 4, 'end', 1)):
        groups = []
        for j in range(7):
            pad = out[f'Span_{chr(65 + i)}_beam_{j + 1}_{e}_bearing'].bounds     # pad + plate: one plan box
            # Cutters overlap their neighbours slightly so the union leaves no float32 slivers in the pockets.
            grp = [out[f'bulbt_{i}_{j}'], haunch(new, i, j, lift=.05, drop=.02),
                   box(*pad[:, 0], *pad[:, 1], pad[0, 2], pad[1, 2] + .01)]
            if f'ped_{bi}_{j}_0' in out:
                ped = out[f'ped_{bi}_{j}_0'].copy()
                ped.vertices[np.isclose(ped.vertices[:, 2], ped.vertices[:, 2].max()), 2] += .005
                grp.append(ped)
            groups.append(grp)
        groups.append([out[f'approach_{s}']])
        out[f'cap_{bi}'] = end_body(new, bi, groups)
    out['sidewalk'] = sidewalk(new)
    out['ps1_base'] = ps1_base(new)
    for pid in ['deck', 'ft_rail', 'joint_-1', 'joint_1', 'ps1_beam_0', 'ps1_beam_1'] + \
               [f'xframe_{i}_{j}' for i in range(5) for j in range(6)] + ['ps1_posts']:
        m = stored(pid)
        if pid.startswith('xframe'):
            v = mirror(m.vertices, [np.arange(len(m.vertices))])
        elif pid == 'ps1_posts':
            if len(m.vertices) % 8:
                raise ValueError('ps1_posts: expected 8-vertex boxes')
            v = mirror(m.vertices, np.arange(len(m.vertices)).reshape(-1, 8), lift=PS1_RISE)
        else:
            v = mirror(m.vertices, lift=PS1_RISE if pid.startswith('ps1_beam') else 0.0)
        out[pid] = trimesh.Trimesh(vertices=v, faces=m.faces[:, ::-1], process=False)
    for bi in range(6):
        m = stored(f'footing_{bi}')
        v = m.vertices.copy()
        zb, zt = v[:, 2].min(), v[:, 2].max()
        if not np.allclose(sorted({round(z, 4) for z in v[:, 2]}), [round(OLD_FOOT_BOTTOM[bi], 4),
                           round(OLD_FOOT_BOTTOM[bi] + (1.6 if bi in (0, 5) else 2.13), 4)]):
            raise ValueError(f'footing_{bi}: unexpected original levels')
        v[:, 2] = np.where(np.isclose(v[:, 2], zt), z_el(FOOT_TOP_EL[bi]), z_el(FOOT_BOTTOM_EL[bi]))
        if np.allclose(v, m.vertices, atol=5e-5):
            continue
        out[f'footing_{bi}'] = trimesh.Trimesh(vertices=v, faces=m.faces, process=False)
    for pid, m in out.items():
        if not m.is_watertight or m.volume <= 0:
            raise ValueError(f'{pid}: corrected mesh invalid')
    untouched = sorted(set(parts) - set(out))
    if any(not p.startswith('footing_') for p in untouched):
        raise ValueError(f'unexpected untouched parts: {untouched}')

    # ---- Manifest notes and dimensions. ----
    def note(pid, text):
        p = parts[pid]
        p['note'] = (p.get('note', '') + ' ' + text).strip()

    orient = 'Mirrored to the drawn side (Y left of increasing station = north) and re-skewed, sheets 20-23, 43.'
    grade_note = 'Re-referenced to the sheet 7 profile (P.I. 389+40.58 El. 490.90, 430 ft curve); was 0.10 m high.'
    for pid in out:
        if not pid.startswith(('column_', 'tie_', 'footing_')):
            note(pid, orient + ' ' + grade_note if not pid.startswith('cap_') else orient)
    parts['deck']['dimensions']['crown_offset_m'] = round(CROWN, 6)
    for i in range(5):
        ga, gb = beam_ends(i, True)
        for j in range(7):
            pid = f'bulbt_{i}_{j}'
            parts[pid]['dimensions'].update(length_m=round(gb - ga, 6), flange_edge_thickness_m=round(4 * IN, 6))
            parts[pid]['basis'] = 'Dimensioned 66 in Bulb-T section (sheet 45); camber and end skew cut omitted'
            note(pid, 'Ends 3 in from interior bent centre lines and 9 in past end-bent bearings (sheets 43, 45); '
                      'flange edge 4 in, taper 4 in, fillet 3 in (sheet 45).')
            note(f'haunch_{i}_{j}', 'Extended with the corrected beam ends.')
    for bi in range(6):
        y0, y1 = cap_extent(bi)
        pid = f'cap_{bi}'
        end = bi in (0, 5)
        parts[pid]['dimensions'].update(
            cap_length_along_skew_m=round((END_LENGTH_FT if end else INT_LENGTH_FT) * FT, 6),
            soffit_el_ft=SOFFIT_EL[bi], north_end_y_m=round(y1, 6), south_end_y_m=round(y0, 6))
        if end:
            parts[pid]['name'] = f'Bent {bi + 1} | semi-integral end bent (cap and end diaphragm)'
            parts[pid]['basis'] = 'Dimensioned 3 ft 9 in end bent carried to the slab soffit; beam pockets cut'
            note(pid, f'Soffit El. {SOFFIT_EL[bi]}, 76 ft 5 1/2 in along the bent; end-bent concrete raised to the '
                      'slab soffit around the beam ends (sheets 26, 29, 32). Wingwalls not modelled.')
        else:
            parts[pid]['dimensions']['seat_top_el_ft'] = round(450 + seats[bi] / FT, 3)
            note(pid, f'Soffit El. {SOFFIT_EL[bi]}; 74 ft 3 in cap with beam 1 3 ft 6 3/4 in from the north end '
                      f'(sheets 34, 35, 39).')
        for j, yc in enumerate(new_column_ys(bi)):
            cid = f'column_{bi}_{j}'
            side = 3 if end else 4
            parts[cid]['dimensions'].update(
                section_width_m=round(side * FT, 6), centre_y_m=round(float(yc), 6),
                base_el_ft=FOOT_TOP_EL[bi], top_el_ft=SOFFIT_EL[bi],
                along_bent_from_north_cap_end_ft=round(float((END_COLUMNS_FT if end else INT_COLUMNS_FT)[j]), 4))
            if bi in (2, 3):
                parts[cid]['dimensions']['lower_section_width_m'] = round(4.5 * FT, 6)
                parts[cid]['dimensions']['section_step_el_ft'] = STEP_EL
            parts[cid]['basis'] = 'Dimensioned square column aligned with the bent'
            note(cid, f'{side} ft square aligned with the bent' + (', 4 ft 6 in below El. 459.67' if bi in (2, 3) else '')
                 + f'; El. {FOOT_TOP_EL[bi]} to {SOFFIT_EL[bi]} (sheets {"26, 29" if end else "35, 39"}).')
        fid = f'footing_{bi}'
        if fid in out:
            note(fid, f'Levels El. {FOOT_BOTTOM_EL[bi]} to {FOOT_TOP_EL[bi]} (sheets 26, 29, 35, 39).')
    for bi in (2, 3):
        pid = f'tie_{bi}'
        parts[pid]['dimensions'].update(depth_m=round(4 * FT, 6), width_m=round(2.75 * FT, 6),
                                        bottom_el_ft=TIE_EL[0], top_el_ft=TIE_EL[1])
        parts[pid]['basis'] = 'Dimensioned tie-beam core; end haunches omitted'
        note(pid, '2 ft 9 in x 4 ft core, El. 453.42 to 457.42, between the corrected column centres (sheet 39).')
    parts['sidewalk']['dimensions'].update(curb_height_m=round(CURB, 6), cross_slope='2 % rising toward PS-1')
    note('sidewalk', '8 in curb, top rising 2 % toward the PS-1 railing (sheet 23).')
    note('ps1_base', 'Sits on the deck slab, 2 ft 0 in above the corrected sidewalk at the rail face (sheet 23).')
    for pid in ('ps1_posts', 'ps1_beam_0', 'ps1_beam_1'):
        note(pid, f'Raised {PS1_RISE:.6f} m with the corrected sidewalk (sheet 23).')
    for s in (-1, 1):
        pid = f'approach_{s}'
        parts[pid]['dimensions'].update(length_m=round(APPROACH_SHORT, 6), long_edge_m=round(APPROACH_SHORT + 2 * T * W / 2, 6))
        parts[pid]['basis'] = 'Dimensioned approach slab with square terminal joint'
        parts[pid]['note'] = parts[pid]['note'].replace(', local pavement ledges and nonparallel plan edges',
                                                        ' and local pavement ledges')
        note(pid, 'Square terminal joint; 20 ft 6 in to 46 ft 9 1/4 in (sheets 58, 60).')

    # ---- Write the changed meshes. ----
    for pid, m in out.items():
        prim = meshes[pid]['primitives'][0]
        color = read(prim['attributes']['COLOR_0'])[0]
        v = np.asarray(m.vertices, dtype=np.float64)
        prim['attributes'] = {'POSITION': append(np.c_[v[:, 0], v[:, 2], -v[:, 1]].astype('<f4'), 'VEC3', 5126),
                              'COLOR_0': append(np.tile(color, (len(v), 1)).astype('u1'), 'VEC4', 5121)}
        gltf['accessors'][prim['attributes']['COLOR_0']]['normalized'] = True
        prim['indices'] = append(np.asarray(m.faces).reshape(-1, 1).astype('<u4'), 'SCALAR', 5125)
        p = parts[pid]
        p['bounds_m'] = np.round(m.bounds, 6).tolist()
        p['volume_m3'] = round(float(m.volume), 9)
        meshes[pid]['extras'].update({k: p[k] for k in ('name', 'basis', 'note', 'dimensions')})

    gltf['buffers'][0]['byteLength'] = len(binary)
    while len(binary) % 4:
        binary.append(0)
    encoded = json.dumps(gltf, ensure_ascii=True, separators=(',', ':')).encode()
    encoded += b' ' * ((-len(encoded)) % 4)
    result = (struct.pack('<III', 0x46546c67, 2, 28 + len(encoded) + len(binary)) +
              struct.pack('<II', len(encoded), 0x4e4f534a) + encoded + struct.pack('<II', len(binary), 0x004e4942) + binary)
    backup_dir.mkdir(parents=True, exist_ok=True)
    (backup_dir / f'{BID}_before_review_correction.glb').write_bytes(original)
    (backup_dir / f'{BID}_manifest_before_review_correction.json').write_bytes(mp.read_bytes())
    path.write_bytes(result)

    manifest['drawing_review_correction'] = TAG
    manifest['revision'] = REVISION
    manifest['drawing_review_correction_record'] = dict(
        source_pdf_pages=SOURCE_PAGES, printed_sheets=PRINTED_SHEETS,
        native_axes='X along Line "A" stations, Y left of increasing station (north), Z = El. - 450 ft (m)',
        corrections={
            'orientation': 'Transverse layout mirrored to the drawn side (sidewalk/PS-1 south = -Y, FT barrier, '
                           'beam 1 and Line "A" north = +Y); support skew kept: north end at the lower station.',
            'profile': 'P.I. Sta. 389+40.58 El. 490.90, +0.30 % / -0.32 %, 430 ft curve; deck lowered '
                       '0.083-0.107 m.',
            'bent_caps': 'Soffits El. 479.69 / 477.78 / 477.92 / 477.92 / 477.78 / 479.77; end caps 76 ft 5 1/2 in, '
                         'interior caps 74 ft 3 in offset 0.141 m north; end bents carried to the slab soffit.',
            'columns': 'Square, aligned with the bent; end bents 3 ft at 23.25/23.25/10.5 ft, interior 4 ft at '
                       '25/25/11.5 ft, Bents 3-4 4 ft 6 in below El. 459.67; bases on the footing tops.',
            'tie_beams': '2 ft 9 in x 4 ft, El. 453.42-457.42.',
            'beams': 'Ends 3 in from interior bents, 9 in past end-bent bearings; 4 in flange edge.',
            'sidewalk': '8 in curb, top rising 2 % to PS-1; PS-1 raised 0.169824 m and seated on the deck.',
            'approach_slabs': 'Square terminal joints, 20 ft 6 in to 46 ft 9 1/4 in.'},
        bent_seat_tops_el_ft={f'Bent {bi + 1}': round(450 + seats[bi] / FT, 3) for bi in range(6)},
        changed_parts=sorted(out), before_glb_sha256=before, after_glb_sha256=hashlib.sha256(result).hexdigest())
    deviations = [d for d in manifest.get('known_deviations', [])
                  if d.get('id') not in ('end-bent-wingwalls', 'interior-support-diaphragms', 'bearing-seat-schedule')]
    deviations += [
        dict(id='end-bent-wingwalls', parts='cap_0, cap_5', source='sheets 26, 28, 29 (PDF 112, 114, 115)',
             deviation='The four 15 in wingwalls (NW/SE 13 ft 6 1/2 in, SW/NE 14 ft) are not modelled.',
             reason='They need new components with their own part ids; deferred from the 2026-11 drawing review.'),
        dict(id='interior-support-diaphragms', parts='bulbt_*, cap_1-cap_4', source='sheets 43, 54 (PDF 129, 140)',
             deviation='The 3 ft concrete diaphragms over Bents 2-5 that encase the beam ends are not modelled; '
                       'the 6 in gap between beam ends is open.',
             reason='They need new components with their own part ids; deferred from the 2026-11 drawing review.'),
        dict(id='bearing-seat-schedule', parts='Span_*_bearing, ped_*, cap_*',
             source='seat elevation tables, sheets 26, 29, 35, 39',
             deviation='Seats follow the beams, which keep a uniform 0.10 m haunch under the corrected deck: within '
                       'about 0.03 m of the schedule at Bents 2-5 and about 0.09 m low at the encased end-bent '
                       'bearings. Beam ends are square, not cut on the skew.',
             reason='Imposing the schedule needs straight beams on scheduled seats with variable haunches, a '
                    'superstructure rebuild beyond this correction.')]
    manifest['known_deviations'] = deviations
    mp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in manifest['drawing_review_correction_record'].items() if k != 'changed_parts'}))
    print(f'{len(out)} parts changed, {len(untouched)} unchanged: {untouched}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--base', type=Path, default=BASE, help='bridge folder (default: the repository copy)')
    parser.add_argument('--backup', type=Path, default=ROOT / 'data/fem_research', help='backup folder')
    args = parser.parse_args()
    correct(args.base, args.backup)

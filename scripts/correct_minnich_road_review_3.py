"""Third-round correction of Minnich Road: the four known deviations of revision 1.1, resolved from the drawings.

    python scripts/correct_minnich_road_review_3.py

Runs after scripts/correct_minnich_road_review.py (revision 1.1). Minnich Road has no second correction script: the
second check changed nothing. INDOT B-44533; in this set the printed sheet number equals the PDF page number.

vertical-curve-pvi (sheets 16, 19, 44, 23). The profile is a 940 ft crest curve with its PVI at Sta. 15+26.77, which is
the Bent 3 centre line (X = +1.524 m), not the structure midpoint (X = 0). Every part is re-graded with
grade(X - 1.524). The change is exactly linear, dz = 0.000332447 X - 0.000177 m. Parts whose vertices were graded at
their own X (deck, girders, haunches, rails, diaphragms) get dz per vertex. Parts placed at one point (bearings,
stiffeners, splices, bolts, frames) move rigidly by dz at that point. The substructure is rebuilt with the generator's
rules: cap top at the lowest seat, pedestals to each seat, columns from the fixed 1.2 m base.

end-bent-fillet-depth (sheets 45, 44, 34, 23). Section X-X gives an 8 in deck and a 2 in fillet at the end bents. The
end-span girders are raised 29.2 mm at the end bearing line (0.08 m generator haunch -> 2 in). Decision: the raise
falls linearly to zero at the field splice, where the new girder meets the retained girder. Sheet 53 says the existing
top-of-girder elevations are unknown and the fillet between is set by the screed procedure. Haunches, end
diaphragms and end-bearing stiffeners follow. The deck is rebuilt on the same stations with transverse vertices at
every flange edge, rail base and a 0.5 m grid (it had three), so the soffit carries the drawn profile and crossfall
where the haunches, diaphragms and rails bear and the fillet is 2 in on the faces, not only on the formula. The end bearings get the drawn stack of sheet 34: S5-B pad
1'-0" x 1'-4" x 3 5/8", the bearing top plate (1 1/2" Bent 1, 3/4" Bent 5), the tabulated shim plate and the 1 1/2"
flange connection plate. The resulting seats match the sheet 23 end-bent elevations within 0.01 ft at all 16 bearings,
and the diaphragm bottoms match the four sheet 44 levels within 0.012 ft.

end-bent-mudwall-face (sheets 24, 45, 23, 60). The new mudwall of Section A-A sits 3 in behind the deck end: its front
face is 1'-4 3/4" behind the bearing line, normal to the bent. Its top is 1'-0" wide and flush with the deck and RCBA.
A 9 in RCBA ledge lies 1'-2" below the top. The lower part is 1'-9" thick and hangs 1'-8" behind the existing cap,
whose back face is 9 in behind the mudwall front face. The bank lengths are 54'-0 1/4" and 53'-0 3/4" along the
bent, either side of a 1 3/4" joint.
  - The existing end-bent caps are therefore 3'-6" wide normal to the bent: 1'-4 1/4" ahead of and 2'-1 3/4" behind
    the bearing line (sheet 23 plan, Section A-A, sheet 19 bent stations).
  - Their tops are at the bearing seats: flat on the long bank, and four steps on the short bank (sheet 23). The
    step positions are scaled from the sheet 23 vector linework.
  - The 14 end-bent pedestals are replaced by the stepped cap tops and removed.
  - The RCBA inner edge moves to the rear of the mudwall top, on the ledge, with the 2 in seat thickening over
    2'-3" and the 45 degree chamfer (sheet 60). The road ends follow the sheet 56/58 chain measured from the mudwall
    (Sections Y-Y, Z-Z): 20'-6" at the 8 ft band lines and 32'-6 3/8" further for the corner panel.
  - The mudwall ends return toward the wingwalls as the sheet 23 plan draws them: 1'-0" thick (2'-3 1/4" along Y)
    at the short banks, 2'-2 1/2" thick (1'-8 3/4") at the long banks, the ledge closed 2'-6 5/8" / 1'-4 1/4" from
    the turn. The RCBA corners turn onto the return inner faces (sheets 56/58: 1'-0 5/8" and 3" inboard, giving
    21'-7 5/8" and 53'-1 3/8"), and the four RCBA extensions along the wingwalls are added (19'-9" / 18'-6 5/8" long,
    1'-9" wide, 1'-2" thick; sheets 56/58, 60). The existing wingwalls under them are not modelled (known deviation).
  - Bent 5 bearing stiffeners: 2'-8 1/8" between the flanges (sheet 26); their bottoms rise 1/8 in off the
    1 1/8 in Span D flange.

end-bent-x-frames (sheets 25-28, 30-31, 33). The framing plans show no steel frame at the end bents: the girder ends
are encased in the concrete end diaphragm. The twelve ids (frame_0_0_*, frame_3_1_*) are analysed components of the
FEM demonstration, which generates them itself, so they are kept and reshaped. Each becomes the drawn MC 18x42.7 channel
diaphragm nearest the end bent in its bay, between PL 1/2" x 8" connection plates (Diaphragm Detail, sheet 33).
  - Span A: 26'-5" from the east girder's Bent 1 bearing and 12'-11" from the west girder's (sheets 25, 27-28).
  - Span D: 4'-5" from the east girder's Bent 5 bearing and 17'-11" from the west girder's (sheets 26, 30-31).
    Decision: sheet 31 and the Girders 4 & 8 view print 4'-4" / 17'-10". Those chains sum to 55'-4", against their
    own 55'-5" bearing-to-bearing dimension. The Girders 1 & 5 chain (4'-5") closes.
  - The channel heights follow the clear distances written on sheet 33 at each web: 7 1/8" below the top flange at
    the outer girder and 8 7/8" (Span A) or 7" (Span D) at the inner one. fem/minnich.json gets a matching assumption
    note, and its support_geometry is refreshed from the corrected caps and columns.

The script checks the starting revision, GLB SHA-256 and deviation list. It refuses to run unless the generator and
first-correction formulas reproduce the current meshes of every part it rebuilds. Only new accessors are appended; the
earlier binary chunk is kept. Requires numpy, trimesh, manifold3d and shapely.
"""
import argparse
import hashlib
import json
import re
import struct
import sys
from pathlib import Path

import manifold3d
import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from bridge_geometry import box, concat, rectangular_bar, rod, sweep  # noqa: E402  (generator primitives, unchanged)

BID = 'minnich-road'
TAG_KEY, TAG = 'review_correction_3', 'known-deviations-pvi-end-bent-stack-mudwall-channel-diaphragms'
REVISION, PREVIOUS_REVISION = '1.3-deviations', '1.1-drawing-review'
PREVIOUS_TAG = 'review-end-diaphragms-girder-ends-flange-rail-face-girder-numbers'
START_GLB = '68b64b3d55fd56255990d500fe7c0bda3ef54a740fcf02f5c64c4b921ac9d3e1'
DEVIATIONS = {'end-bent-x-frames', 'vertical-curve-pvi', 'end-bent-mudwall-face', 'end-bent-fillet-depth'}
FT, IN = .3048, .0254

# Generator geometry (scripts/build_indiana_batch2.py, minnich()) and first correction (correct_minnich_road_review.py).
LENGTH, WIDTH = (414 + 11.5 / 12) * FT, 63 * FT
SKEW = 56 + 17 / 60 + 55 / 3600
K, C = -np.tan(np.radians(SKEW)), np.cos(np.radians(SKEW))
SPANS = np.array([65 + 5 / 12, 145, 145, 55 + 5 / 12]) * FT
BS = np.r_[0, np.cumsum(SPANS)] - SPANS.sum() / 2
YS = np.array([-29.375, -20.375, -11.375, -2.375, 2.375, 11.375, 20.375, 29.375]) * FT
SLAB, CLEAR = 8 * IN, .08
FLANGE_W, FLANGE_T, WEB_T = .4572, .0254, .0127
END_PROJECTION = 7.5 * IN
SHALLOW_START = BS[3] + 17 * FT
SPAN_D_FLANGE = (22 * IN, 1.125 * IN)
DIAPHRAGM_BACK, DIAPHRAGM_FRONT = 13.75 * IN, 10.25 * IN
OLD_PAD = {0: (FT, 16 * IN, 3.625 * IN), 4: (FT, 16 * IN, 3.625 * IN), 'pier': (.4, .5, .08)}
OLD_PLATE = {0: (13 * IN, 22 * IN, 3 * IN), 4: (13 * IN, 24 * IN, 2.25 * IN), 'pier': (.5, .65, .12)}

# Third round.
XPVI = BS[2]                                   # sheet 16 PVI Sta. 15+26.77 = Bent 3 centre line (sheet 19)
FILLET = 2 * IN                                # sheet 45 Section X-X
RAISE = CLEAR - FILLET                         # 0.0292 m at the end bearing line
SPLICE = {0: BS[1] - 9 * FT, 3: BS[3] + 9 * FT}  # field splices, sheets 25-31 (generator stations)
END_BEARING = {0: BS[0], 3: BS[4]}
TOP_PLATE = {0: 1.5 * IN, 4: .75 * IN}         # sheet 34 bearing top plate
FLANGE_PLATE = 1.5 * IN                        # sheet 34 flange connection plate
SHIM = {0: [1 + 1 / 16, 1 + 1 / 8, 1 + 7 / 16, 1 + 5 / 16, 1 + 7 / 16, 1 + 7 / 8, 2 + 3 / 16, 2 + 3 / 8],
        4: [3 / 4, 11 / 16, 7 / 16, 1 / 16, 7 / 8, 5 / 8, 0, 3 / 16]}   # sheet 34 shim table, beam lines 1..8, inches
CAP_FRONT, CAP_BACK = 16.25 * IN, 25.75 * IN   # existing end bent faces from the bearing line (sheets 23, 24)
MUD_FRONT, MUD_TOP, MUD_LEDGE = 16.75 * IN, 12 * IN, 9 * IN      # sheet 24 Section A-A
LEDGE_DROP, HANG = 14 * IN, 20 * IN            # ledge 1'-2" below the top; bottom 1'-8" below the cap top
MUD_JOINT = 1.75 * IN                          # joint between the banks, along the bent (sheet 23)
MUD_LONG, MUD_SHORT = (54 * 12 + .25) * IN, (53 * 12 + .75) * IN  # bank lengths along the bent (sheet 23)
STEPS_ALONG_BENT = np.array([10.88, 27.10, 43.32]) * FT  # scaled from sheet 23 (1/4 in = 1 ft), from the joint
RCBA_T, RCBA_SEAT, RCBA_THICK, RCBA_CHAMFER = FT, 14 * IN, 27 * IN, 2 * IN   # sheet 60 pavement ledge detail
MC = dict(d=18 * IN, bf=3.95 * IN, tw=.45 * IN, tf=.625 * IN)    # MC 18x42.7 (sheet 33), AISC nominal dimensions
CONN_T, CONN_W, CHANNEL_GAP = .5 * IN, 8 * IN, 1.75 * IN          # sheet 33: PL 1/2 x 8; channel end 1 3/4 in from web
CHANNEL_STATION = {0: (26 + 5 / 12) * FT, 3: (4 + 5 / 12) * FT}  # from the east girder's end bearing (sheets 27, 30)
# Sheet 33 clear distance from the underside of the top flange to the channel top: (outer girder, inner girder)
CHANNEL_CLEAR = {0: (7.125 * IN, 8.875 * IN), 3: (7.125 * IN, 7 * IN)}
RCBA_MIN, RCBA_STEP = 20.5 * FT, (32 + 6.375 / 12) * FT   # sheets 56, 58: 20'-6" at the band lines; 32'-6 3/8" road-end step
# Mudwall returns at the bank ends (sheet 23 plan; return thickness along X also in sheet 60 Sections X-X and W-W):
# short bank (wings A, D): 1'-0" thick, outer face 2'-3 1/4" along Y, rear face turned 2'-6 5/8" along X;
# long bank (wings B, C): 2'-2 1/2" thick, outer face 1'-8 3/4" along Y.
RET_SHORT, RET_SHORT_LEN, LEDGE_END_SHORT = 12 * IN, 27.25 * IN, 30.625 * IN
RET_LONG, RET_LONG_LEN = 26.5 * IN, 20.75 * IN
EXT_LEN = {'short': 19.75 * FT, 'long': (18 + 6.625 / 12) * FT}   # RCBA extensions, sheets 56/58 and 60 X-X / W-W
EXT_W, EXT_T = 21 * IN, 14 * IN                                    # 1'-9" wide (sheets 56/58), 1'-2" thick (sheet 60)
RCBA_EDGE_Y = 30 * FT                                              # RCBA outer edges, 60'-0" wide (sheets 56/58)
SPAN_D_STIFFENER = 32.125 * IN   # sheet 26 Bearing Stiffener Detail: PL 5/8 x 8 1/2 x 2'-8 1/8" (Span D)


def grade(x, pvi=True):
    x = np.asarray(x, float) - (XPVI if pvi else 0)
    return 10.45 - .00005 * x - .0625 * x ** 2 / (2 * 940 * FT)


def surface(x, y, pvi=True):
    return grade(x, pvi) - .0156 * np.abs(y)


def dz(x):
    """Re-grading shift; exactly linear in X."""
    return grade(x) - grade(x, False)


def sx(u, y):
    return u + K * y


def depth(u):
    if u < BS[1]:
        return np.interp(u, [BS[0], BS[0] + 48.4167 * FT, BS[0] + 53.4167 * FT, BS[1]], [36 * IN, 36 * IN, 68 * IN, 68 * IN])
    if u > BS[3]:
        return np.interp(u, [BS[3], BS[3] + 12 * FT, BS[3] + 17 * FT, BS[4]], [68 * IN, 68 * IN, 34.25 * IN, 34.25 * IN])
    return 68 * IN


def lift(u, span):
    """End-span girder raise: RAISE at the end bearing line, straight to zero at the field splice (decision)."""
    if span not in (0, 3):
        return 0.0
    ub, us = END_BEARING[span], SPLICE[span]
    return float(RAISE * max((us - u) / (us - ub), 0.0))


def section(d, bottom_w=FLANGE_W, bottom_t=FLANGE_T):
    b, t, w, tw = bottom_w / 2, bottom_t, FLANGE_W / 2, WEB_T / 2
    return [(-b, 0), (b, 0), (b, t), (tw, t), (tw, d - FLANGE_T), (w, d - FLANGE_T),
            (w, d), (-w, d), (-w, d - FLANGE_T), (-tw, d - FLANGE_T), (-tw, t), (-b, t)]


def loft(rings, axes=(1, 2)):
    """Closed solid through equal-size planar rings (first correction's topology); axes span the ring planes."""
    rings = np.asarray(rings, float)
    count, n = rings.shape[:2]

    def cap(ring):
        pts = ring[:, list(axes)]
        ccw = (np.roll(pts[:, 0], -1) - pts[:, 0]) @ (np.roll(pts[:, 1], -1) + pts[:, 1]) < 0
        tri = manifold3d.triangulate([pts if ccw else pts[::-1]]).astype(np.int64)
        return tri if ccw else (n - 1 - tri)[:, ::-1]

    faces = []
    for k in range(count - 1):
        for j in range(n):
            a, b = k * n + j, k * n + (j + 1) % n
            faces += [(a, b, b + n), (a, b + n, a + n)]
    faces += [tuple(q[::-1]) for q in cap(rings[0])] + [tuple(q + (count - 1) * n) for q in cap(rings[-1])]
    mesh = trimesh.Trimesh(rings.reshape(-1, 3), np.array(faces), process=False)
    if mesh.volume < 0:
        mesh.invert()
    return mesh


def to_manifold(m, precise=True):
    if precise:
        return manifold3d.Manifold(manifold3d.Mesh64(vert_properties=np.asarray(m.vertices, np.float64),
                                                     tri_verts=np.asarray(m.faces, np.uint64)))
    return manifold3d.Manifold(manifold3d.Mesh(vert_properties=np.asarray(m.vertices, np.float32),
                                               tri_verts=np.asarray(m.faces, np.uint32)))


def union(meshes, precise=True):
    """Boolean union, one solid required. New geometry uses double precision (Mesh64); precise=False reproduces the
    first correction's single-precision union for the starting-state check."""
    result = to_manifold(meshes[0], precise)
    for m in meshes[1:]:
        result = result + to_manifold(m, precise)
    solids = [r for r in result.decompose() if abs(r.volume()) > 1e-9]    # drop zero-volume slivers of touching faces
    if len(solids) != 1:
        raise ValueError('union did not give one solid')
    result = solids[0]
    out = result.to_mesh64() if precise else result.to_mesh()
    return trimesh.Trimesh(np.asarray(out.vert_properties[:, :3], np.float64), np.asarray(out.tri_verts, np.int64), process=False)


def plate_stations(i):
    a, b = BS[i], BS[i + 1]
    breaks = [BS[0] + 48.4167 * FT, BS[0] + 53.4167 * FT, BS[3] + 12 * FT, BS[3] + 17 * FT]
    return np.unique(np.r_[np.linspace(a, b, max(3, int((b - a) / .5))), [t for t in breaks if a < t < b]])


def haunch_stations(i):
    a, b = BS[i], BS[i + 1]
    return np.linspace(a, b, max(3, int((b - a) / .7)))


def plate_ring(u, y, span, shallow=False, new=True):
    d = depth(u)
    pts = section(d, *SPAN_D_FLANGE) if shallow else section(d)
    x = sx(u, y)
    bottom = surface(x, y, new) - SLAB - CLEAR + (lift(u, span) if new else 0) - d
    return [(x, y + v, bottom + h) for v, h in pts]


def haunch_ring(u, y, span, new=True):
    x, bottom = sx(u, y), CLEAR - (lift(u, span) if new else 0)
    return [(x, y + v, (1 - t) * (surface(x, y, new) - SLAB - bottom) + t * (surface(x, y + v, new) - SLAB))
            for v, t in [(-FLANGE_W / 2, 0), (FLANGE_W / 2, 0), (FLANGE_W / 2, 1), (-FLANGE_W / 2, 1)]]


def girder_mesh(span, y, new=True):
    xs = plate_stations(span)
    if span == 0:
        xs = np.r_[BS[0] - END_PROJECTION, xs]
        return loft([plate_ring(u, y, span, new=new) for u in (np.unique(np.r_[xs, SPLICE[0]]) if new else xs)])
    xs = np.r_[xs, BS[4] + END_PROJECTION]
    if new:
        xs = np.unique(np.r_[xs, SPLICE[3]])
    taper = loft([plate_ring(u, y, span, new=new) for u in xs[xs <= SHALLOW_START + 1e-9]])
    shallow = loft([plate_ring(u, y, span, True, new) for u in xs[xs >= SHALLOW_START - 1e-9]])
    return union([taper, shallow], precise=new)


def haunch_mesh(span, y, new=True):
    hs = haunch_stations(span)
    hs = np.r_[BS[0] - END_PROJECTION, hs] if span == 0 else np.r_[hs, BS[4] + END_PROJECTION]
    if new:
        hs = np.unique(np.r_[hs, SPLICE[span]])
    return loft([haunch_ring(u, y, span, new) for u in hs])


def diaphragm_mesh(bent, new=True):
    u_brg, sign, span = BS[bent], (-1 if bent == 0 else 1), (0 if bent == 0 else 3)
    q_back, q_front = u_brg + sign * DIAPHRAGM_BACK / C, u_brg - sign * DIAPHRAGM_FRONT / C
    d, tf = (36 * IN, FLANGE_T) if bent == 0 else (34.25 * IN, SPAN_D_FLANGE[1])
    rings = []
    ys = set(YS.tolist()) | {0.0}
    if new:                                      # top on the deck soffit: ring at every deck station between the girders
        ys |= {y for y in deck_stations() if YS[0] < y < YS[-1]}
    for y in sorted(ys):
        ring = []
        for q, top in [(q_back, 0), (q_front, 0), (q_front, 1), (q_back, 1)]:
            x = sx(q, y)
            soffit = surface(x, y, new) - SLAB
            ring.append((x, y, soffit if top else soffit - CLEAR + (lift(q, span) if new else 0) - d + tf))
        rings.append(ring)
    return loft(rings, axes=(0, 2))


def deck_stations():
    """Transverse vertex rows of the rebuilt deck: edges, crown, both edges of every top flange and haunch, the rail
    bases and a 0.5 m grid, so that haunch tops, rails and diaphragms bear on the deck faces."""
    keys = {-WIDTH / 2, WIDTH / 2, 0.0} | {y + s * FLANGE_W / 2 for y in YS for s in (-1, 1)}
    keys |= {s * (WIDTH / 2 - .05 - v) for s in (-1, 1) for v in (0.0, 16 * IN)}
    grid = [g for g in np.arange(-19, 20) * .5 if -WIDTH / 2 < g < WIDTH / 2 and min(abs(g - k) for k in keys) > .05]
    return np.array(sorted(keys | set(grid)))


def deck_mesh(new=True):
    us = np.linspace(-LENGTH / 2, LENGTH / 2, max(2, int(LENGTH / .6) + 1))
    if not new:                                  # generator Model.slab: three transverse vertices
        profile = [(-WIDTH / 2, -SLAB), (0, -SLAB), (WIDTH / 2, -SLAB), (WIDTH / 2, 0), (0, 0), (-WIDTH / 2, 0)]
        return sweep(profile, us, lambda u, y, z: (sx(u, y), y, surface(sx(u, y), y, False) + z))
    # Deck-edge corners (sheet 60 Sections X-X and W-W: the deck stops at the mudwall return with the 3 in joint of the
    # front face). At the acute (short-bank) corners the skewed end is cut back to the joint, at the obtuse (long-bank)
    # corners it is carried to it. The end rings take the new plan; the change fades over the next two rings.
    joint = 3 * IN
    xa, xo = END['xF'] + joint, END['xF2'] + joint
    y_ac, y_ob = (xa + LENGTH / 2) / K, (xo + LENGTH / 2) / K

    def north_end(y):
        x = -LENGTH / 2 + K * y
        return xa if y > y_ac else xo if y < y_ob else x

    ys = np.array(sorted(set(deck_stations().tolist()) | {y_ac, y_ob, -y_ac, -y_ob}))
    pts = [(y, -SLAB) for y in ys] + [(y, 0.0) for y in ys[::-1]]
    n, blend = len(us) - 1, 3
    rings = []
    for k, u in enumerate(us):
        ring = []
        for y, z in pts:
            x = u + K * y
            x += max(0.0, 1 - k / blend) * (north_end(y) - (us[0] + K * y))
            x += max(0.0, 1 - (n - k) / blend) * (-north_end(-y) - (us[-1] + K * y))
            ring.append((x, y, surface(x, y) + z))
        rings.append(ring)
    return loft(rings, axes=(1, 2))


def transverse(u, thick, y0, y1, z0, z1):
    """Generator Model.transverse: thickness normal to the skew support line."""
    return sweep([(y0, z0), (y1, z0), (y1, z1), (y0, z1)], [-thick / 2 / C, thick / 2 / C],
                 lambda t, y, z: (sx(u + t, y), y, z))


def bearing_mesh(x, y, top, pad, plate):
    px, py, ph = pad
    lx, ly, lh = plate
    return concat([box(x - px / 2, x + px / 2, y - py / 2, y + py / 2, top - ph - lh, top - lh),
                   box(x - lx / 2, x + lx / 2, y - ly / 2, y + ly / 2, top - lh, top)])


def old_frame(i, row, j):
    a, b = BS[i], BS[i + 1]
    u = np.linspace(a + .8, b - .8, max(2, int((b - a) / 7)))[row]
    y0, y1 = YS[j] + .24, YS[j + 1] - .24
    x = sx(u, (y0 + y1) / 2)
    z1 = surface(x, (y0 + y1) / 2, False) - SLAB - CLEAR - .12
    z0 = z1 - depth(u) + .24
    return concat([rectangular_bar([x, y0, z0], [x, y1, z1], .10, .012), rectangular_bar([x, y0, z1], [x, y1, z0], .10, .012)])


def old_rcba(side, lane):
    u = side * (LENGTH / 2 + .03)
    y0, y1 = [(-30 * FT, -8 * FT), (-8 * FT, 8 * FT), (8 * FT, 30 * FT)][lane]
    outer = side * max(side * sx(u, y0), side * sx(u, y1)) + side * 20.5 * FT
    profile = [(y0, 0), (y1, 0), (y1, 1), (y0, 1)]
    return sweep(profile, np.linspace(0, 1, 30),
                 lambda t, y, h: ((1 - t) * sx(u, y) + t * outer, y, surface((1 - t) * sx(u, y) + t * outer, y, False) - (1 - h) * FT)), outer


def rounded(**dims):
    return {k: round(float(v), 6) for k, v in dims.items()}


def inches(value):
    """Shim thickness in sixteenths, as printed on sheet 34."""
    whole, rest = int(value), round((value - int(value)) * 16)
    if not rest:
        return str(whole)
    g = np.gcd(rest, 16)
    return (f'{whole} ' if whole else '') + f'{rest // g}/{16 // g}'


def bank_range(bank):
    return (-WIDTH / 2, -.01) if bank == 0 else (.01, WIDTH / 2)


# Mudwalls and RCBA panels touch on the ledge: both are sampled across the bridge at the same Y stations (a 0.5 m grid
# plus every lane, bank, joint and step edge), so their faceted top and seat surfaces coincide.
LANES = [(-30 * FT, -8 * FT), (-8 * FT, 8 * FT), (8 * FT, 30 * FT)]
def rear(n, y):
    """X of the line n behind the Bent 1 bearing line, normal to the bent (Bent 5 follows by the 180 degree symmetry)."""
    return BS[0] - n / C + K * y


def y_at(n, x):
    return (x - BS[0] + n / C) / K


def end_geometry():
    """Bent 1 mudwall ends (sheet 23 plan). Short bank +Y (Wing A), long bank -Y (Wing B); Bent 5 is (-x, -y)."""
    g = dict(yj=MUD_JOINT / 2 * C)
    g['yF'] = (MUD_JOINT / 2 + MUD_SHORT) * C
    g['xF'] = rear(MUD_FRONT, g['yF'])
    g['xT'] = g['xF'] - RET_SHORT                                  # return inner face, where the X-X RCBA corner bears
    g['yT'] = y_at(MUD_FRONT + MUD_TOP, g['xT'])
    g['y25'] = y_at(CAP_BACK, g['xT'])
    g['yE'] = g['yF'] + RET_SHORT_LEN
    g['yR'] = y_at(MUD_FRONT + MUD_TOP + MUD_LEDGE, g['xT'] - LEDGE_END_SHORT)
    g['yF2'] = -(MUD_JOINT / 2 + MUD_LONG) * C
    g['xF2'] = rear(MUD_FRONT, g['yF2'])
    g['xH'] = g['xF2'] - RET_LONG                                  # return inner face, where the W-W RCBA corner bears
    g['yG'] = g['yF2'] - RET_LONG_LEN
    g['yT2'] = y_at(MUD_FRONT + MUD_TOP, g['xH'])
    g['y252'] = y_at(CAP_BACK, g['xH'])
    return g


END = end_geometry()
Y_BREAKS = sorted({0.0, *[e for lane in LANES for e in lane]} |
                  {s * v for s in (-1, 1) for v in [MUD_JOINT / 2 * C, (MUD_JOINT / 2 + MUD_LONG) * C,
                                                     (MUD_JOINT / 2 + MUD_SHORT) * C, *(STEPS_ALONG_BENT * C),
                                                     *[abs(END[k]) for k in ('yT', 'y25', 'yE', 'yR', 'yG', 'yT2', 'y252')],
                                                     RCBA_EDGE_Y + EXT_W]})


def end_regions(bank_short):
    """Plan polygons of one Bent 1 mudwall bank: A front part and return (full height, on the cap), B behind the cap
    under the top (hangs 1'-8"), C the RCBA ledge (hangs 1'-8")."""
    g, L = END, rear
    f, b25, b28, b37 = MUD_FRONT, CAP_BACK, MUD_FRONT + MUD_TOP, MUD_FRONT + MUD_TOP + MUD_LEDGE
    if bank_short:
        yj, xF, xT = g['yj'], g['xF'], g['xT']
        a = [(L(f, yj), yj), (xF, g['yF']), (xF, g['yE']), (xT, g['yE']), (xT, g['y25']), (L(b25, yj), yj)]
        bb = [(L(b25, yj), yj), (xT, g['y25']), (xT, g['yT']), (L(b28, yj), yj)]
        c = [(L(b28, yj), yj), (xT, g['yT']), (xT, g['yR']), (L(b37, g['yR']), g['yR']), (L(b37, yj), yj)]
    else:
        yj, xF, xH = -g['yj'], g['xF2'], g['xH']
        a = [(L(f, yj), yj), (L(b25, yj), yj), (xH, g['y252']), (xH, g['yG']), (xF, g['yG']), (xF, g['yF2'])]
        bb = [(L(b25, yj), yj), (L(b28, yj), yj), (xH, g['yT2']), (xH, g['y252'])]
        c = [(L(b28, yj), yj), (L(b37, yj), yj), (L(b37, g['yT2']), g['yT2']), (xH, g['yT2'])]
    return a, bb, c


def prism(points, z_bottom, z_top):
    """Closed solid over a simple plan polygon; edges are split at every Y station (the shared mudwall/RCBA grid) so
    neighbouring solids share vertices; top and bottom follow the given functions of (x, y)."""
    pts = [tuple(p) for p in points]
    area = sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]))
    if area < 0:
        pts = pts[::-1]
    stations = y_stations(min(p[1] for p in pts) - 1, max(p[1] for p in pts) + 1)
    ring = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
        ring.append((x0, y0))
        if abs(y1 - y0) > 1e-6:
            cut = sorted((y for y in stations if min(y0, y1) + 1e-6 < y < max(y0, y1) - 1e-6), reverse=y1 < y0)
            ring += [(x0 + (y - y0) / (y1 - y0) * (x1 - x0), y) for y in cut]
        else:
            k = int(np.ceil(abs(x1 - x0) / .5))
            ring += [(x0 + t * (x1 - x0), y0) for t in np.arange(1, k) / k]
    ring = np.array(ring)
    tri = manifold3d.triangulate([ring]).astype(np.int64)
    n = len(ring)
    verts = [(x, y, z_bottom(x, y)) for x, y in ring] + [(x, y, z_top(x, y)) for x, y in ring]
    faces = [tuple(t[::-1]) for t in tri] + [tuple(t + n) for t in tri]
    for i in range(n):
        j = (i + 1) % n
        faces += [(i, j, j + n), (i, j + n, i + n)]
    mesh = trimesh.Trimesh(np.array(verts), np.array(faces), process=False)
    if mesh.volume < 0:
        mesh.invert()
    if not (mesh.is_watertight and mesh.volume > 0):
        raise ValueError('invalid prism')
    return mesh


def y_stations(lo, hi):
    grid = [g for g in np.arange(np.ceil(lo / .5), np.floor(hi / .5) + 1) * .5 if lo + .01 < g < hi - .01]
    inner = [b for b in Y_BREAKS if lo + 1e-9 < b < hi - 1e-9]
    pts = sorted(set([lo, hi] + inner + [g for g in grid if min(abs(g - b) for b in inner + [lo, hi]) > .01]))
    return np.array(pts)


def close(a, b, tol=1e-4):
    """Every vertex of a is within tol of a vertex of b and vice versa (order-independent)."""
    a, b = np.asarray(a, float), np.asarray(b, float)

    def one_way(p, q):
        worst = 0.0
        for s in range(0, len(p), 2048):
            d = np.sqrt(((p[s:s + 2048, None, :] - q[None, :, :]) ** 2).sum(-1)).min(1)
            worst = max(worst, float(d.max()))
        return worst
    return max(one_way(a, b), one_way(b, a)) <= tol


def correct(base, fem_path, backup):
    mp = base / 'model_manifest.json'
    raw_manifest = mp.read_bytes()
    manifest = json.loads(raw_manifest)
    if manifest.get(TAG_KEY) == TAG:
        print('Already corrected.')
        return
    path = base / 'model.glb'
    original = path.read_bytes()
    before = hashlib.sha256(original).hexdigest()
    fem_raw, fem_ledger = read_fem_ledger(fem_path)          # validated before anything is written

    def expect(ok, message):
        if not ok:
            raise ValueError(message)

    expect(manifest.get('drawing_review_correction') == PREVIOUS_TAG and manifest.get('revision') == PREVIOUS_REVISION,
           'Manifest is not the first-correction revision 1.1.')
    expect(before == START_GLB == manifest['drawing_review_correction_record']['after_glb_sha256'],
           'GLB differs from the first correction.')
    expect({d['id'] for d in manifest.get('known_deviations', [])} == DEVIATIONS, 'Unexpected known_deviations.')
    length = struct.unpack_from('<I', original, 12)[0]
    gltf = json.loads(original[20:20 + length])
    binary = bytearray(original[28 + length:])
    parts = {p['id']: p for p in manifest['parts']}
    meshes = {m['name']: m for m in gltf['meshes']}
    expect(set(parts) == set(meshes) and len(parts) == 476, 'Unexpected part set.')

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
        v = read(meshes[pid]['primitives'][0]['attributes']['POSITION']).astype(np.float64)
        return np.c_[v[:, 0], -v[:, 2], v[:, 1]]          # glTF (X, Z, -Y) -> native (X, Y, Z)

    def check(pid, mesh):
        expect(close(native(pid), mesh.vertices if hasattr(mesh, 'vertices') else mesh),
               f'{pid}: current mesh does not match the generator geometry this correction assumes')

    def to_gl(v):
        return np.c_[v[:, 0], v[:, 2], -v[:, 1]].astype('<f4')

    new_bounds, new_volume, reshaped, moved = {}, {}, [], []

    def reshape(pid, mesh):
        """New topology: positions, colours and indices."""
        if not (mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0):
            raise ValueError(f'{pid}: invalid solid')
        prim = meshes[pid]['primitives'][0]
        rgba = read(prim['attributes']['COLOR_0'])[0]
        gl = to_gl(mesh.vertices)
        colour = append(np.tile(np.asarray(rgba, 'u1'), (len(gl), 1)), 'VEC4', 5121)
        gltf['accessors'][colour]['normalized'] = True
        meshes[pid]['primitives'][0] = dict(attributes={'POSITION': append(gl, 'VEC3', 5126), 'COLOR_0': colour},
                                            indices=append(mesh.faces.reshape(-1, 1).astype('<u4'), 'SCALAR', 5125),
                                            mode=4)
        new_bounds[pid] = mesh.bounds
        new_volume[pid] = float(mesh.volume)
        reshaped.append(pid)

    def move(pid, vertices, volume=None):
        """Same topology, new positions (indices and colours kept)."""
        prim = meshes[pid]['primitives'][0]
        expect(len(vertices) == gltf['accessors'][prim['attributes']['POSITION']]['count'], f'{pid}: vertex count')
        prim['attributes']['POSITION'] = append(to_gl(vertices), 'VEC3', 5126)
        new_bounds[pid] = np.array([vertices.min(0), vertices.max(0)])
        if volume is not None:
            new_volume[pid] = volume
        moved.append(pid)

    # ---- Starting-state checks for every part rebuilt from formulas ----------------------------------------------
    for span in (0, 3):
        for j, y in enumerate(YS):
            check(f'plate_{span}_{j}', girder_mesh(span, y, new=False))
            check(f'haunch_{span}_{j}', haunch_mesh(span, y, new=False))
    for bent in (0, 4):
        check(f'end_diaphragm_{bent}', diaphragm_mesh(bent, new=False))
    check('deck', deck_mesh(new=False))
    old_seat = {}
    for bi, u in enumerate(BS):
        kind = bi if bi in (0, 4) else 'pier'
        for j, y in enumerate(YS):
            x = sx(u, y)
            top = surface(x, y, False) - SLAB - CLEAR - depth(u)
            check(f'Bent_{bi + 1}_bearing_{j + 1}', bearing_mesh(x, y, top, OLD_PAD[kind], OLD_PLATE[kind]))
            old_seat[bi, j] = top - OLD_PAD[kind][2] - OLD_PLATE[kind][2]
        seat = min(old_seat[bi, j] for j in range(8))
        for bank in (0, 1):
            y0, y1 = bank_range(bank)
            check(f'cap_{bi}_{bank}', transverse(u, .84, y0, y1, seat - .95, seat))
            if bi in (0, 4):
                face = u + (-1 if bi == 0 else 1) * .8
                ym = (y0 + y1) / 2
                check(f'mudwall_{bi}_{bank}', transverse(face, .25, y0, y1, seat - .95, surface(sx(face, ym), ym, False) - SLAB))
            else:
                for k, y in enumerate(np.linspace(y0 + .9, y1 - .9, 3)):
                    check(f'column_{bi}_{bank}_{k}', rod([sx(u, y), y, 1.2], [sx(u, y), y, seat - .95], .45, 24))
        for j, y in enumerate(YS):
            pid = f'ped_{bi}_{j}'
            expect((pid in parts) == (old_seat[bi, j] > seat + .001), f'{pid}: unexpected pedestal set')
            if pid in parts:
                check(pid, transverse(u, .75, y - .38, y + .38, seat, old_seat[bi, j]))
    for side in (-1, 1):
        for lane in range(3):
            check(f'rcba_{side}_{lane}', old_rcba(side, lane)[0])
    for i, row in ((0, 0), (3, 1)):
        for j in (0, 1, 2, 4, 5, 6):
            check(f'frame_{i}_{row}_{j}', old_frame(i, row, j))

    # ---- vertical-curve-pvi: re-grade every part not rebuilt below ------------------------------------------------
    rebuilt = ({'deck'} | {f'plate_{s}_{j}' for s in (0, 3) for j in range(8)} | {f'haunch_{s}_{j}' for s in (0, 3) for j in range(8)}
               | {'end_diaphragm_0', 'end_diaphragm_4'} | {f'Bent_{b}_bearing_{n}' for b in (1, 5) for n in range(1, 9)}
               | {f'cap_{b}_{k}' for b in (0, 4) for k in (0, 1)} | {f'mudwall_{b}_{k}' for b in (0, 4) for k in (0, 1)}
               | {f'rcba_{s}_{k}' for s in (-1, 1) for k in range(3)}
               | {f'frame_{i}_{r}_{j}' for i, r in ((0, 0), (3, 1)) for j in (0, 1, 2, 4, 5, 6)})
    removed = sorted(p for p in parts if re.fullmatch(r'ped_[04]_\d', p))
    expect(len(removed) == 14, 'expected 14 end-bent pedestals')
    substructure = re.compile(r'(cap|ped|column)_[123]_.*')
    rigid = re.compile(r'(Bent_\d_bearing_\d|stiffener_\d_\d+|splice_\d_\d(_bolts)?|frame_\d_\d_\d)')
    graded = re.compile(r'(plate_\d_\d|haunch_\d_\d|rail_-?1_\d)')
    for pid in parts:
        if pid in rebuilt or pid in removed or substructure.fullmatch(pid):
            continue
        v = native(pid)
        v2 = v.copy()
        if graded.fullmatch(pid):
            v2[:, 2] += dz(v[:, 0])                                   # graded at each vertex's own X
        elif rigid.fullmatch(pid):
            xc = (v[:, 0].min() + v[:, 0].max()) / 2                  # placed at one point: rigid shift
            shift = dz(xc)
            m = re.fullmatch(r'stiffener_(\d)_(\d+)', pid)
            if m and int(m.group(2)) in (0, 4):                       # end-bearing stiffeners rise with the girder
                shift += RAISE
            v2[:, 2] += shift
            if m and int(m.group(2)) == 4:
                # Bent 5 bearing stiffeners: 2'-8 1/8" between the flanges (sheet 26); the generator assumed a 1 in
                # bottom flange, the Span D flange is 1 1/8 in (sheets 30-31), so the bottoms rise 1/8 in.
                low = v2[:, 2] < v2[:, 2].min() + 1e-4
                h0 = v2[:, 2].max() - v2[:, 2].min()
                v2[low, 2] += SPAN_D_FLANGE[1] - FLANGE_T
                expect(abs(v2[:, 2].max() - v2[:, 2].min() - SPAN_D_STIFFENER) < 1e-6, f'{pid}: stiffener height')
                move(pid, v2, parts[pid]['volume_m3'] * SPAN_D_STIFFENER / h0)
                continue
        else:
            raise ValueError(f'{pid}: unclassified part')
        if pid in ('rail_1_0', 'rail_-1_3'):
            # Rail ends at the acute corners stop at the cut-back deck edge, 3 in from the mudwall return (deck_mesh).
            flip = 1 if pid == 'rail_1_0' else -1
            faces = read(meshes[pid]['primitives'][0]['indices']).reshape(-1, 3).astype(np.int64)
            cut = to_manifold(trimesh.Trimesh(v2, faces, process=False)).trim_by_plane((flip, 0, 0), END['xF'] + 3 * IN)
            out_mesh = cut.to_mesh64()
            reshape(pid, trimesh.Trimesh(np.asarray(out_mesh.vert_properties[:, :3], np.float64),
                                         np.asarray(out_mesh.tri_verts, np.int64), process=False))
            continue
        move(pid, v2, parts[pid].get('volume_m3'))

    # Intermediate bents: generator rules with the re-graded seats.
    for bi in (1, 2, 3):
        new_seat = {j: old_seat[bi, j] + dz(sx(BS[bi], YS[j])) for j in range(8)}
        s0, s1 = min(old_seat[bi, j] for j in range(8)), min(new_seat.values())
        expect(all((new_seat[j] > s1 + .001) == (old_seat[bi, j] > s0 + .001) for j in range(8)),
               f'Bent {bi + 1}: pedestal set would change')
        for bank in (0, 1):
            v = native(f'cap_{bi}_{bank}')
            v[:, 2] += s1 - s0
            move(f'cap_{bi}_{bank}', v, parts[f'cap_{bi}_{bank}']['volume_m3'])
            for k in range(3):
                pid = f'column_{bi}_{bank}_{k}'
                v = native(pid)
                v[:, 2] = 1.2 + (v[:, 2] - 1.2) * (s1 - .95 - 1.2) / (s0 - .95 - 1.2)
                move(pid, v, parts[pid]['volume_m3'] * (s1 - .95 - 1.2) / (s0 - .95 - 1.2))
        for j in range(8):
            pid = f'ped_{bi}_{j}'
            if pid in parts:
                v = native(pid)
                v[:, 2] = s1 + (v[:, 2] - s0) * (new_seat[j] - s1) / (old_seat[bi, j] - s0)
                move(pid, v, parts[pid]['volume_m3'] * (new_seat[j] - s1) / (old_seat[bi, j] - s0))

    # ---- end-bent-fillet-depth: deck faceting, end-span girders, haunches, diaphragms -------------------------------
    reshape('deck', deck_mesh())
    for span in (0, 3):
        for j, y in enumerate(YS):
            reshape(f'plate_{span}_{j}', girder_mesh(span, y))
            reshape(f'haunch_{span}_{j}', haunch_mesh(span, y))
    for bent in (0, 4):
        reshape(f'end_diaphragm_{bent}', diaphragm_mesh(bent))

    # End bearings: drawn stack (sheet 34), seats from the girder underside.
    seats, stacks = {}, {}
    for bi in (0, 4):
        span = 0 if bi == 0 else 3
        for j, y in enumerate(YS):
            x, line = sx(BS[bi], y), 8 - j                                # part index j is beam line 8 - j (sheet 25)
            top = surface(x, y) - SLAB - CLEAR + lift(BS[bi], span) - depth(BS[bi])
            plate_t = TOP_PLATE[bi] + SHIM[bi][line - 1] * IN + FLANGE_PLATE
            stacks[bi, j] = (plate_t, SHIM[bi][line - 1] * IN)
            pad = OLD_PAD[bi]
            reshape(f'Bent_{bi + 1}_bearing_{j + 1}', bearing_mesh(x, y, top, pad, OLD_PLATE[bi][:2] + (plate_t,)))
            seats[bi, j] = top - pad[2] - plate_t

    # ---- end-bent-mudwall-face: caps with the drawn seat levels, Section A-A mudwalls, RCBA seats -------------------
    cap_levels = {}
    for bi in (0, 4):
        u_b, span_sign = BS[bi], (1 if bi == 0 else -1)                   # +1: the span lies at larger u
        capbot = min(seats[bi, j] for j in range(8)) - .95
        u_front, u_back = u_b + span_sign * CAP_FRONT / C, u_b - span_sign * CAP_BACK / C
        for bank in (0, 1):
            js = [j for j in range(8) if (YS[j] > 0) == (bank == 1)]
            inner_out = sorted(js, key=lambda j: abs(YS[j]))              # from the centre line outward
            levels = [seats[bi, j] for j in inner_out]
            stepped = max(levels) - min(levels) > .05
            expect(stepped or max(levels) - min(levels) < .003, f'Bent {bi + 1} bank {bank}: seats neither flat nor stepped')
            expect(stepped == ((bi == 0) == (bank == 1)), f'Bent {bi + 1}: stepped bank is not the sheet 23 short bank')
            y0, y1 = bank_range(bank)
            sgn = 1 if bank == 1 else -1
            if stepped:
                steps = STEPS_ALONG_BENT * C
                expect(all(abs(YS[inner_out[k]]) < steps[k] < abs(YS[inner_out[k + 1]]) for k in range(3)),
                       'step outside its girder pair')
                outline = [(0.01, levels[0])] + [p for k in range(3) for p in [(steps[k], levels[k]), (steps[k], levels[k + 1])]]
                outline += [(WIDTH / 2, levels[3])]
                cap_levels[bi, bank] = (levels, steps)
            else:
                flat = float(min(levels))                                # shim rounding (1/16 in) leaves gaps, not overlaps
                outline = [(0.01, flat), (WIDTH / 2, flat)]
                cap_levels[bi, bank] = ([flat] * 4, None)
            top = [(sgn * a, z) for a, z in outline]
            poly = [(y0, capbot), (y1, capbot)] + (top[::-1] if bank == 1 else top)
            rings = [[(sx(u_t, y), y, z) for y, z in poly] for u_t in (u_front, u_back)]
            reshape(f'cap_{bi}_{bank}', loft(rings, axes=(1, 2)))

    import shapely.geometry as sg                               # noqa: E402  (bridge_geometry already requires shapely)
    mud_lengths = {}
    for bi in (0, 4):
        flip = 1 if bi == 0 else -1                                 # Bent 5 is Bent 1 turned 180 degrees in plan
        for bank in (0, 1):
            short = (bank == 1) if bi == 0 else (bank == 0)          # right (short) bank of the sheet 23 plan
            levels, steps = cap_levels[bi, bank]
            edges = [0.0] + ([] if steps is None else list(steps)) + [1e3]
            pieces = []
            ra, rb, rc = (sg.Polygon(r) for r in end_regions(short))
            span_side = sg.Polygon([(rear(CAP_BACK, -100), -100), (rear(CAP_BACK, 100), 100),
                                    (rear(CAP_BACK, 100) + 1e3, 100), (rear(CAP_BACK, -100) + 1e3, -100)])
            # A front part and returns on the cap or wingwall top; B behind the cap; C the ledge, which hangs only
            # behind the cap (near the short-bank return it lies over the cap).
            regions = [(ra, 0, 0), (rb, 0, HANG), (rc.intersection(span_side), LEDGE_DROP, 0),
                       (rc.difference(span_side), LEDGE_DROP, HANG)]
            for region, top_drop, hang in regions:
                if region.is_empty:
                    continue
                poly = sg.Polygon([(flip * x, flip * y) for x, y in region.exterior.coords])
                for k, (lo, hi) in enumerate(zip(edges, edges[1:])):
                    strip = sg.box(-1e3, lo, 1e3, hi) if (bank == 1) else sg.box(-1e3, -hi, 1e3, -lo)
                    part = poly.intersection(strip)
                    for geom in getattr(part, 'geoms', [part]):
                        if geom.geom_type != 'Polygon' or geom.area < 1e-8:
                            continue
                        lvl = levels[k]
                        pieces.append(prism(list(geom.exterior.coords)[:-1], lambda x, y, z0=lvl - hang: z0,
                                            lambda x, y, d=top_drop: float(surface(x, y)) - d))
            mud_lengths[bi, bank] = MUD_SHORT if short else MUD_LONG
            # Touching closed bodies (front part and returns, the part behind the cap, the ledge), as other multi-body
            # parts of the model; a boolean union of their coplanar faces leaves zero-width seams.
            reshape(f'mudwall_{bi}_{bank}', trimesh.util.concatenate(pieces))

    rcba_edges = {}
    for side in (-1, 1):
        bi, span_sign = (0, 1) if side < 0 else (4, -1)
        u_in = BS[bi] - span_sign * (MUD_FRONT + MUD_TOP) / C
        for lane in range(3):
            y0, y1 = LANES[lane]
            corner = lane == (2 if side < 0 else 0)                       # the panel cut by the deck-edge corner
            if corner:
                m0, m1 = LANES[1]
                outer = side * max(side * sx(u_in, m0), side * sx(u_in, m1)) + side * (RCBA_MIN + RCBA_STEP)
            else:
                outer = side * max(side * sx(u_in, y0), side * sx(u_in, y1)) + side * RCBA_MIN

            ys = y_stations(y0, y1)
            g, flip = END, (1 if side < 0 else -1)

            def inner(y, lane=lane):
                """RCBA bridge-end edge: the mudwall line, turned at the deck-edge corners onto the return inner faces
                (sheets 56/58: X-X corner turns 1'-0 5/8" and W-W 3" inboard; sheet 23 returns)."""
                yy = flip * y
                if lane == (2 if side < 0 else 0) and yy > g['yT']:              # X-X corner (short-bank return)
                    return flip * g['xT']
                if lane == (0 if side < 0 else 2) and yy < g['yT2']:             # W-W corner (long-bank return)
                    return flip * g['xH']
                return sx(u_in, y)

            def ring(x_of, thick):
                # Top and bottom follow the profile grade and crown across the lane, as the mudwall ledge does.
                pts = [(y, 0) for y in ys] + [(y, 1) for y in ys[::-1]]
                return [(x_of(y), y, surface(x_of(y), y) - (1 - h) * thick) for y, h in pts]

            rings = [ring(lambda y, d=d: inner(y) + side * d / C, RCBA_SEAT) for d in (0, MUD_LEDGE, RCBA_THICK)]
            start = lambda y: inner(y) + side * (RCBA_THICK + RCBA_CHAMFER) / C  # noqa: E731
            rings += [ring(lambda y, t=t: (1 - t) * start(y) + t * outer, RCBA_T) for t in np.linspace(0, 1, 28)]
            expect(all(side * (outer - start(y)) > 1 for y in (y0, y1)), 'RCBA too short')
            rcba_edges[f'rcba_{side}_{lane}'] = sorted(abs(outer - inner(y)) for y in (y0, y1))
            reshape(f'rcba_{side}_{lane}', loft(rings, axes=(1, 2)))

    # ---- end-bent-x-frames: the drawn channel diaphragms nearest the end bents --------------------------------------
    channel_info = {}
    for i, row in ((0, 0), (3, 1)):
        bi, s = (0, 1) if i == 0 else (4, -1)                            # s: towards midspan
        for j in (0, 1, 2, 4, 5, 6):
            yw, ye = YS[j], YS[j + 1]
            xc = sx(BS[bi], ye) + s * CHANNEL_STATION[i]

            def web(yg):
                """Top of the bottom flange and underside of the top flange of the (raised) girder at the channel."""
                u = xc - K * yg
                bottom = surface(xc, yg) - SLAB - CLEAR + lift(u, i) - depth(u)
                return bottom + (FLANGE_T if i == 0 else SPAN_D_FLANGE[1]), bottom + depth(u) - FLANGE_T

            (wb, wt), (eb, et) = web(yw), web(ye)
            ya, yb = yw + WEB_T / 2 + CHANNEL_GAP, ye - WEB_T / 2 - CHANNEL_GAP
            west_outer = abs(yw) > abs(ye)
            clear_w, clear_e = CHANNEL_CLEAR[i] if west_outer else CHANNEL_CLEAR[i][::-1]
            # Sheet 33 clear distances from each top flange to the channel top, taken at the channel ends.
            mid_w, mid_e = wt - clear_w - MC['d'] / 2, et - clear_e - MC['d'] / 2

            def zc(y):
                return mid_w + (mid_e - mid_w) * (y - ya) / (yb - ya)

            xb, h, bf, tw, tf = xc + s * CONN_T / 2, MC['d'] / 2, s * MC['bf'], s * MC['tw'], MC['tf']
            outline = [(xb, -h), (xb + bf, -h), (xb + bf, -h + tf), (xb + tw, -h + tf), (xb + tw, h - tf),
                       (xb + bf, h - tf), (xb + bf, h), (xb, h)]
            channel = loft([[(x, y, zc(y) + z) for x, z in outline] for y in (ya, yb)], axes=(0, 2))
            plates = [box(xc - CONN_T / 2, xc + CONN_T / 2, yw + WEB_T / 2, yw + WEB_T / 2 + CONN_W, wb, wt),
                      box(xc - CONN_T / 2, xc + CONN_T / 2, ye - WEB_T / 2 - CONN_W, ye - WEB_T / 2, eb, et)]
            for p in plates:
                expect(p.is_watertight and p.volume > 0, 'connection plate')
            expect(channel.is_watertight and channel.volume > 0, 'channel')
            for z_end, (lo, hi) in ((zc(ya), (wb, wt)), (zc(yb), (eb, et))):
                expect(lo + .05 < z_end - h and z_end + h < hi - .05, 'channel outside the web')
            mesh = trimesh.util.concatenate([channel] + plates)
            pid = f'frame_{i}_{row}_{j}'
            channel_info[pid] = dict(east=(xc - sx(BS[bi], ye)) * s, west=(xc - sx(BS[bi], yw)) * s, length=yb - ya)
            reshape(pid, mesh)

    # ---- RCBA extensions along the wingwalls (new parts) -------------------------------------------------------------
    rgba = read(meshes['rcba_-1_0']['primitives'][0]['attributes']['COLOR_0'])[0]
    template = parts['rcba_-1_0']
    added, new_meshes, new_parts = [], [], []
    for bi in (0, 4):
        side, flip = (-1, 1) if bi == 0 else (1, -1)
        for bank in (0, 1):
            short = (bank == 1) if bi == 0 else (bank == 0)
            x0 = flip * (END['xT'] if short else END['xH'])           # the return inner face
            x1 = x0 + side * EXT_LEN['short' if short else 'long']
            y0, y1 = (RCBA_EDGE_Y, RCBA_EDGE_Y + EXT_W) if bank == 1 else (-RCBA_EDGE_Y - EXT_W, -RCBA_EDGE_Y)
            mesh = prism([(min(x0, x1), y0), (max(x0, x1), y0), (max(x0, x1), y1), (min(x0, x1), y1)],
                         lambda x, y: float(surface(x, y)) - EXT_T, lambda x, y: float(surface(x, y)))
            pid = f'rcba_ext_{side}_{bank}'
            wing = {(0, 1): 'A', (0, 0): 'B', (4, 1): 'C', (4, 0): 'D'}[bi, bank]
            sec = 'X-X' if short else 'W-W'
            meta = dict(id=pid, name=f'{"North" if side < 0 else "South"} approach | RCBA extension along Wing {wing}',
                        layer='approaches', color=template['color'], pdf_pages=[56 if bi == 0 else 58, 60],
                        basis=f'Dimensioned: sheet {56 if bi == 0 else 58} RCBA plan ({"19 ft 9 in" if short else "18 ft 6 5/8 in"} '
                              f'long, 1 ft 9 in wide beside the panel) and sheet 60 Section {sec} (1 ft 2 in thick)',
                        note='From the mudwall return inner face along the wingwall; top on the profile grade. It bears on the '
                             'existing wingwall, which is not modelled (known deviation existing-wingwalls). Dowels, joint '
                             'and reinforcement are not modelled.',
                        dimensions=rounded(length_m=EXT_LEN['short' if short else 'long'], width_m=EXT_W, thickness_m=EXT_T))
            gl = to_gl(mesh.vertices)
            colour = append(np.tile(np.asarray(rgba, 'u1'), (len(gl), 1)), 'VEC4', 5121)
            gltf['accessors'][colour]['normalized'] = True
            prim = dict(attributes={'POSITION': append(gl, 'VEC3', 5126), 'COLOR_0': colour},
                        indices=append(mesh.faces.reshape(-1, 1).astype('<u4'), 'SCALAR', 5125), mode=4)
            new_meshes.append(dict(name=pid, extras=dict(processed=True, **meta), primitives=[prim]))
            new_parts.append(dict(meta, bounds_m=np.round(mesh.bounds, 6).tolist(), volume_m3=round(float(mesh.volume), 9)))
            new_bounds[pid], new_volume[pid] = mesh.bounds, float(mesh.volume)
            added.append(pid)

    # ---- remove the end-bent pedestals; rebuild the node list -------------------------------------------------------
    keep = [m for m in gltf['meshes'] if m['name'] not in removed] + new_meshes
    gltf['meshes'] = keep
    world = dict(name='world', children=list(range(1, len(keep) + 1)))
    gltf['nodes'] = [world] + [dict(name=m['name'], mesh=k) for k, m in enumerate(keep)]
    gltf['scenes'] = [dict(nodes=[0])]
    gltf['scene'] = 0
    meshes = {m['name']: m for m in keep}
    expect(len(set(moved) | set(reshaped)) == len(moved) + len(reshaped) == 476 - 14, 'every remaining part must change')

    # ---- manifest -------------------------------------------------------------------------------------------------
    manifest['parts'] = [p for p in manifest['parts'] if p['id'] not in removed] + new_parts
    parts = {p['id']: p for p in manifest['parts']}
    for pid in parts:
        parts[pid]['bounds_m'] = np.round(new_bounds[pid], 6).tolist()
        if pid in new_volume and 'volume_m3' in parts[pid]:
            parts[pid]['volume_m3'] = round(float(new_volume[pid]), 9)

    def note(pid, text, **dims):
        p = parts[pid]
        p['note'] = (p.get('note', '') + ' ' + text).strip()
        p.setdefault('dimensions', {}).update(rounded(**dims))

    note('deck', 'Revision 1.3: graded with the PVI at Bent 3 (sheet 16); transverse vertices at every flange edge, rail base '
         'and a 0.5 m grid, so the soffit follows the profile and crossfall where haunches, diaphragms and rails bear. At the '
         'four deck-edge corners the end stops 3 in from the mudwall return (sheet 60 Sections X-X, W-W; sheet 23).')
    for pid in ('rail_1_0', 'rail_-1_3'):
        note(pid, 'Revision 1.3: the end at the acute deck corner is cut at the deck edge, 3 in from the mudwall return.')
    for span in (0, 3):
        bent = 1 if span == 0 else 5
        for j in range(8):
            note(f'plate_{span}_{j}', f'Raised so the fillet at the Bent {bent} bearing line is 2 in (sheet 45), falling '
                 'linearly to the generator haunch at the field splice (revision 1.3).', end_fillet_m=FILLET,
                 raise_at_end_bearing_m=RAISE)
            note(f'haunch_{span}_{j}', f'2 in at the Bent {bent} bearing line (sheet 45 Section X-X), {CLEAR} m from the '
                 'field splice on.', end_fillet_m=FILLET)
    for j in range(8):
        for q in (0, 4):
            note(f'stiffener_{j}_{q}', 'Raised with the girder end (2 in fillet, revision 1.3).')
        note(f'stiffener_{j}_4', 'Bottom raised 1/8 in onto the 1 1/8 in Span D bottom flange: 2 ft 8 1/8 in between the '
             'flanges (sheet 26 Bearing Stiffener Detail).', height_m=SPAN_D_STIFFENER)
    for bent, (d, tf) in ((0, (36 * IN, FLANGE_T)), (4, (34.25 * IN, SPAN_D_FLANGE[1]))):
        note(f'end_diaphragm_{bent}', 'Revision 1.3: bottom follows the raised girders, 2 in fillet (sheet 45), so the '
             'diaphragm is 45 in / 43 1/8 in from top of deck as the sheet 44 levels give.',
             depth_below_deck_soffit_m=FILLET + d - tf)
    for bi in (0, 4):
        for j in range(8):
            pid, line = f'Bent_{bi + 1}_bearing_{j + 1}', 8 - j
            p = parts[pid]
            p['basis'] = 'Dimensioned: sheet 34 elastomeric bearing assembly and shim plate table'
            p['pdf_pages'] = [23, 34]
            p['note'] = (f'S5-B pad 1 ft 0 in x 1 ft 4 in x 3 5/8 in under one 13 x {22 if bi == 0 else 24} in plate stack: '
                         f'{"1 1/2" if bi == 0 else "3/4"} in bearing top plate, {inches(SHIM[bi][line - 1])} in shim (beam line {line}) and '
                         '1 1/2 in flange connection plate (sheet 34). The seat matches the sheet 23 end-bent elevation within '
                         '0.01 ft. Side retainers, anchor bolts and studs are not modelled.')
            p['dimensions'].update(rounded(load_plate_thickness_m=stacks[bi, j][0], shim_plate_thickness_m=stacks[bi, j][1],
                                           bearing_top_plate_thickness_m=TOP_PLATE[bi], flange_connection_plate_thickness_m=FLANGE_PLATE))
            meshes[pid]['extras']['basis'] = p['basis']
            meshes[pid]['extras']['pdf_pages'] = p['pdf_pages']
    for bi in (0, 4):
        for bank in (0, 1):
            levels, steps = cap_levels[bi, bank]
            p = parts[f'cap_{bi}_{bank}']
            p['basis'] = ('Existing end bent, dimensioned: 3 ft 6 in normal to the bent, 1 ft 4 1/4 in ahead of and 2 ft 1 3/4 in '
                          'behind the bearing line (sheet 23 plan, sheet 24 Section A-A, sheet 19 bent stations); top at the '
                          'bearing seats (sheet 23 elevations with the sheet 34 stack)')
            p['note'] = ('Top ' + ('flat on this bank' if steps is None else
                                    'in four steps, one per bearing; step positions scaled from sheet 23 (not dimensioned)') +
                         '. Depth below the lowest seat of the bent (0.95 m) and the length under the wingwalls are the '
                         'generator envelope; the existing end-bent plans were not supplied.')
            p['dimensions'].update(rounded(width_normal_to_bent_m=CAP_FRONT + CAP_BACK, front_face_ahead_of_bearing_m=CAP_FRONT,
                                           back_face_behind_bearing_m=CAP_BACK), top_step_count=0 if steps is None else 3)
            p['pdf_pages'] = [19, 23, 24, 34]
            pid = f'mudwall_{bi}_{bank}'
            p = parts[pid]
            short = (bank == 1) if bi == 0 else (bank == 0)
            p['basis'] = ('Dimensioned: sheet 24 Section A-A and sheet 45 Section X-X (front face 1 ft 4 3/4 in behind the bearing '
                          'line, 1 ft 0 in top, 9 in RCBA ledge 1 ft 2 in down, 1 ft 9 in lower part hanging 1 ft 8 in behind '
                          'the existing cap); bank length, end return and bottom levels from sheet 23; return thickness also '
                          'sheet 60 Section ' + ('X-X' if short else 'W-W'))
            p['note'] = ('New mudwall (sheet 20 note 8). Top flush with the deck and RCBA on the profile grade; front 9 in bears '
                         'on the existing cap. The end return (' + ('1 ft 0 in thick, 2 ft 3 1/4 in along Y' if short else
                         '2 ft 2 1/2 in thick, 1 ft 8 3/4 in along Y') + ', sheet 23) runs to the wingwall; its bottom is at the '
                         'cap-top level, as scaled from sheet 60, and bears on the existing wingwall, which is not modelled. '
                         'Chamfers, coatings and reinforcement are not modelled.')
            p['dimensions'] = rounded(front_face_behind_bearing_line_m=MUD_FRONT, top_width_m=MUD_TOP, ledge_width_m=MUD_LEDGE,
                                      ledge_depth_below_top_m=LEDGE_DROP, lower_width_m=MUD_TOP + MUD_LEDGE,
                                      depth_below_cap_top_m=HANG, length_along_bent_m=mud_lengths[bi, bank],
                                      return_thickness_m=RET_SHORT if short else RET_LONG,
                                      return_length_m=RET_SHORT_LEN if short else RET_LONG_LEN)
            p['pdf_pages'] = [23, 24, 45, 60]
    for side in (-1, 1):
        for lane in range(3):
            pid = f'rcba_{side}_{lane}'
            v = new_bounds[pid]
            note(pid, 'Revision 1.3: inner edge on the mudwall ledge, 2 ft 4 3/4 in behind the bearing line, with the 2 in seat '
                 'thickening over 2 ft 3 in and a 45 degree chamfer (sheets 24, 60); top and bottom follow the profile grade and '
                 'crown across the panel. Road end per the sheet 56/58 chain: 20 ft 6 in from the mudwall at the 8 ft band lines, '
                 'the corner panel 32 ft 6 3/8 in beyond the middle one. At the deck-edge corners the edge turns onto the '
                 'mudwall return (1 ft 0 5/8 in / 3 in inboard, sheets 56/58, 23).',
                 inner_edge_behind_bearing_line_m=MUD_FRONT + MUD_TOP, seat_thickening_m=RCBA_SEAT - RCBA_T,
                 shortest_edge_m=rcba_edges[pid][0], longest_edge_m=rcba_edges[pid][1])
            parts[pid]['basis'] = 'Dimensioned: sheets 56 and 58 RCBA plans, sheet 60 sections and pavement ledge detail'
            parts[pid]['pdf_pages'] = sorted(set(parts[pid]['pdf_pages']) | {24, 58, 60})
    for pid, k in channel_info.items():
        i, j = int(pid[6]), int(pid[-1])
        span, bent = ('A', 1) if i == 0 else ('D', 5)
        p = parts[pid]
        p['name'] = f'Span {span} | MC 18x42.7 channel diaphragm nearest Bent {bent}, bay {7 - j} (girders {7 - j}-{8 - j})'
        p['pdf_pages'] = [25, 27, 28, 33] if i == 0 else [26, 30, 31, 33]
        east, west = ('26 ft 5 in', '12 ft 11 in') if i == 0 else ('4 ft 5 in', '17 ft 11 in')
        p['basis'] = (f'Dimensioned: sheet 33 Diaphragm Detail - Span {span} (MC 18x42.7 between PL 1/2 x 8 in connection plates, '
                      f'channel end 1 3/4 in from the web); station {east} from girder {7 - j} and {west} from girder {8 - j} '
                      f'at the Bent {bent} bearing line (sheets {"25, 27-28" if i == 0 else "26, 30-31"})')
        p['note'] = ('Replaces the representative X frame that stood 0.8 m from the end bearing line, where the framing plans '
                     'show no steel frame (the girder ends are encased in the end diaphragm). AISC nominal MC 18x42.7: '
                     'd 18 in, bf 3.95 in, tw 0.45 in, tf 0.625 in; flange slope, fillets and bolts omitted. '
                     + ('Clear distance below the top flange as written on sheet 33 Span A: 7 1/8 in at the outer girder, '
                        '8 7/8 in at the inner one (so 8 7/8 / 7 1/8 in above the bottom flanges). ' if i == 0 else
                        'Clear distance below the top flange as written on sheet 33 Span D: 7 1/8 in at the outer girder, 7 in '
                        'at the inner one. ') +
                     'Sheet 33 does not show which face of the connection plate the channel web bears on; the span-side face '
                     'is used. The FEM demonstration analyses this id as an assumed diagonal pair (fem/minnich.json).')
        p['dimensions'] = rounded(channel_depth_m=MC['d'], channel_flange_width_m=MC['bf'], channel_web_thickness_m=MC['tw'],
                                  channel_flange_thickness_m=MC['tf'], channel_length_m=k['length'],
                                  connection_plate_thickness_m=CONN_T, connection_plate_width_m=CONN_W,
                                  station_from_east_girder_bearing_m=k['east'], station_from_west_girder_bearing_m=k['west'])
    for pid in parts:
        extras = meshes[pid]['extras']
        for key in ('name', 'note', 'dimensions', 'basis', 'pdf_pages'):
            if key in parts[pid]:
                extras[key] = parts[pid][key]

    for c in manifest['detail_coverage']:
        c['part_ids'] = [p for p in c['part_ids'] if p not in removed]
        if c['feature'] == 'Variable-depth steel and connections':
            c['detail'] += (' Revision 1.3: the end-row frames frame_0_0_* and frame_3_1_* are the drawn MC 18x42.7 channel '
                            'diaphragms nearest the end bents (sheets 25-28, 30-31, 33); the other end-span diaphragms, K-frames '
                            'and cross-frames are represented by one X frame per bay near Bents 2 and 4.')
        if c['feature'] == 'Bearings':
            c['detail'] = ('Forty bearing envelopes. The sixteen end-bent bearings follow sheet 34 (S5-B pad, bearing top plate, '
                           'tabulated shim, flange connection plate) and sit on the end-bent caps at the sheet 23 levels; the 21 '
                           'pedestals are at the intermediate bents. Retained intermediate shoes are envelopes only.')
            c['sources'] = sorted(set(c['sources']) | {'Primary PDF p.23'}, key=lambda s: int(s.split('.')[-1]))
        if c['feature'] == 'Existing intermediate piers':
            c['part_ids'] = [p for p in c['part_ids'] if not re.fullmatch(r'(cap|mudwall)_[04]_\d', p)]
        if c['feature'] == 'Rails and stepped approaches':
            c['detail'] += (' RCBA inner edges rest on the mudwall ledge with the 2 in seat thickening and turn onto the mudwall '
                            'returns at the deck-edge corners; the four RCBA extensions along the wingwalls are modelled, the '
                            'wingwalls are not (sheets 23, 24, 56, 58, 60).')
            c['part_ids'] += added
    at = next(k for k, c in enumerate(manifest['detail_coverage']) if c['feature'] == 'Existing intermediate piers')
    manifest['detail_coverage'].insert(at, dict(
        feature='End bents (Bents 1 and 5)', status='modeled_with_simplifications',
        detail='Existing end-bent caps 3 ft 6 in wide with tops at the drawn seat levels (flat on the long bank, four steps on '
               'the short bank) and the new mudwalls of Section A-A, 3 in behind the deck end. Cap depth and length, wingwalls, '
               'coatings and reinforcement are not drawn or not modelled.',
        sources=['Primary PDF p.19', 'Primary PDF p.23', 'Primary PDF p.24', 'Primary PDF p.34', 'Primary PDF p.45'],
        part_ids=[f'{k}_{b}_{n}' for b in (0, 4) for n in (0, 1) for k in ('cap', 'mudwall')]))
    manifest['detail_coverage'][at]['detail'] += (' The mudwall ends return toward the wingwalls as sheet 23 draws them; the '
                                                  'existing wingwalls are not modelled.')

    gltf['buffers'][0]['byteLength'] = len(binary)
    while len(binary) % 4:
        binary.append(0)
    gltf['buffers'][0]['byteLength'] = len(binary)
    encoded = json.dumps(gltf, ensure_ascii=True, separators=(',', ':')).encode()
    encoded += b' ' * ((-len(encoded)) % 4)
    out = (struct.pack('<III', 0x46546c67, 2, 28 + len(encoded) + len(binary)) +
           struct.pack('<II', len(encoded), 0x4e4f534a) + encoded + struct.pack('<II', len(binary), 0x004e4942) + binary)

    changed = sorted(reshaped)
    regraded = sorted(moved)
    decisions = [
        'Fillet: 2 in at the end bearing lines (sheet 45, confirmed by the sheet 44 levels and the sheet 23 seats); the raise '
        'falls linearly to zero at the field splice because the haunch between is set in the field (sheet 53) and the new '
        'girder must meet the retained one there.',
        'Span D channel stations: 4 ft 5 in / 17 ft 11 in from the Bent 5 bearings (sheet 30 Girders 1 & 5 chain, which closes '
        'on 55 ft 5 in) over the 4 ft 4 in / 17 ft 10 in printed on sheet 31 and for Girders 4 & 8, whose chains sum to 55 ft 4 in.',
        'End-bent cap step positions are scaled from the sheet 23 vector linework (not dimensioned): 10.88, 27.10 and 43.32 ft '
        'from the joint along the bent.',
        'Sheet 44 right-end top-of-deck levels (818.75 / 818.89) are 0.08 ft below the sheet 16 profile, while the other two top '
        'levels, all four bottom levels and all sixteen sheet 23 seat levels agree with it; the profile governs.',
        'Channel heights: the clear distances written on sheet 33 (7 1/8 / 8 7/8 in in Span A, 7 1/8 / 7 in in Span D) govern '
        'at each web over the level appearance of the detail; the channels slope by at most 0.34 in over 8 ft 8 in.',
        'RCBA road ends: the sheet 56/58 chain (20 ft 6 in at the 8 ft band lines, 32 ft 6 3/8 in step to the corner panel) '
        'measured from the mudwall, as Sections Y-Y and Z-Z (sheet 60) dimension the RCBA length.']
    manifest[TAG_KEY] = TAG
    manifest['revision'] = REVISION
    manifest['review_correction_record_3'] = dict(
        source_pdf_pages=[16, 19, 20, 22, 23, 24, 25, 26, 27, 28, 30, 31, 33, 34, 44, 45, 53, 56, 58, 60],
        printed_sheets=[16, 19, 20, 22, 23, 24, 25, 26, 27, 28, 30, 31, 33, 34, 44, 45, 53, 56, 58, 60],
        deviations={
            'vertical-curve-pvi': 'resolved: all parts re-graded with the PVI at Bent 3, dz = 0.000332447 X - 0.000177 m (sheet 16)',
            'end-bent-fillet-depth': 'decided: 2 in fillet at the end bearing lines, linear to the field splices; drawn bearing '
                                     'stacks with shims; deck rebuilt with vertices at every flange edge so the fillet is 2 in '
                                     'on the faces (sheets 34, 44, 45)',
            'end-bent-mudwall-face': 'resolved: Section A-A mudwalls with the sheet 23 returns, 3 ft 6 in end-bent caps at '
                                     'the drawn seat levels, RCBA seats, road ends, corners and wingwall extensions; 14 '
                                     'end-bent pedestals removed (sheets 23, 24, 45, 56, 58, 60)',
            'end-bent-x-frames': 'resolved: the twelve ids are the drawn MC 18x42.7 channel diaphragms nearest the end bents '
                                 '(sheets 25-28, 30-31, 33); FEM ids kept'},
        decisions=decisions,
        grade_shift_m=dict(slope=round(float(dz(1) - dz(0)), 9), at_x0=round(float(dz(0)), 9)),
        end_bearing_raise_m=round(RAISE, 6),
        changed_part_count=len(changed) + len(regraded), reshaped_parts=changed, moved_parts=regraded, added_parts=added,
        removed_parts=removed,
        before_glb_sha256=before, after_glb_sha256=hashlib.sha256(out).hexdigest(),
        before_manifest_sha256=hashlib.sha256(raw_manifest).hexdigest())
    manifest['known_deviations'] = [dict(
        id='existing-wingwalls', parts='rcba_ext_-1_0, rcba_ext_-1_1, rcba_ext_1_0, rcba_ext_1_1; mudwall_0_0, mudwall_4_1 '
                                       '(long-bank returns)',
        source='sheets 19 and 21 (plan outlines), 22 (wingwall elevations), 23 and 60 (existing wingwall shown dashed)',
        deviation='The existing wingwalls A-D are not modelled, so the four RCBA extensions and the 2 ft 2 1/2 in mudwall '
                  'returns at the long-bank ends, which stand behind the end-bent caps, have nothing under them in the model; '
                  'the short-bank returns overhang the cap ends by 0.07 m.',
        reason='The existing wingwalls are drawn only dashed and in elevation (sheet 22 tops and bottoms); their plan '
               'thickness, batter and footing are on the original plans (bridge file I469-18-07027 NB & SB, sheet 19 '
               'general note), which are not in this set.')]

    backup.mkdir(parents=True, exist_ok=True)
    (backup / f'{BID}_before_review_correction_3.glb').write_bytes(original)
    (backup / f'{BID}_manifest_before_review_correction_3.json').write_bytes(raw_manifest)
    path.write_bytes(out)
    mp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if fem_ledger is not None:
        (backup / 'minnich_fem_ledger_before_review_correction_3.json').write_bytes(fem_raw)
        fem_ledger['assumptions'][fem_ledger['assumptions'].index(FEM_OLD)] = FEM_NEW
        fem_ledger['assumptions'][fem_ledger['assumptions'].index(FEM_CAPS_OLD)] = FEM_CAPS_NEW
        for e in fem_ledger['evidence']:
            if e['fields'] == ['support_geometry']:
                e['note'] = FEM_SUPPORT_NOTE
        geometry = fem_ledger['values']['support_geometry']
        for pid in geometry:                                   # supports follow the corrected caps and columns
            geometry[pid] = parts[pid]['bounds_m']
        fem_ledger['revision'] = FEM_REVISION[1]
        fem_path.write_text(json.dumps(fem_ledger, indent=2) + '\n', encoding='utf-8')   # the ledger's own format
    print(json.dumps({k: (v if not isinstance(v, list) or len(v) < 20 else f'{len(v)} ids')
                      for k, v in manifest['review_correction_record_3'].items()}, indent=1))


FEM_OLD = ('Cross frames use two 100 x 12 mm rectangular elastic diagonals per displayed frame, aligned with skew support '
           'lines. Neither their sections nor their connections are verified. Reported frame stress is nominal for this '
           'assumed section.')
FEM_NEW = FEM_OLD + (' The twelve end-row ids frame_0_0_* and frame_3_1_* are displayed (model revision 1.3) as the drawn '
                     'MC 18x42.7 channel diaphragms nearest the end bents, 4 to 8 m from the end bearings (sheets 25-28, '
                     '30-31, 33); the analysis keeps its assumed diagonal pair 0.8 m from the end bearing lines under those '
                     'ids, standing in for the concrete end diaphragms, which are not modelled.')
FEM_CAPS_OLD = ('Caps are assumed 0.84 x 0.95 m rectangles. Eighteen columns use the visual scaffold positions and nominal '
                '0.9 m diameter; none is verified from original substructure drawings. Changed diameter changes FE stiffness only.')
FEM_CAPS_NEW = FEM_CAPS_OLD + (' Cap and column heights come from model revision 1.3, where the end-bent caps are 3 ft 6 in '
                               'wide with the drawn stepped seat levels (sheets 23-24); the analysis keeps 0.84 x 0.95 m '
                               'rectangles at the mid-height of each cap envelope.')
FEM_SUPPORT_NOTE = ('Cap and column bounding envelopes of model revision 1.3 (end-bent caps from sheets 23-24, intermediate '
                    'supports still unverified envelopes). The full values are frozen in each run JSON.')
FEM_REVISION = ('2026-10-15-assumed-demo-1', '2026-11-07-assumed-demo-2')


def read_fem_ledger(path):
    """fem/minnich.json keeps its ids; support_geometry follows the corrected caps and columns, and two assumptions
    and the revision are updated.
    Returns (raw, ledger to update) or (raw, None) when it is already updated."""
    raw = path.read_bytes()
    ledger = json.loads(raw)
    if ledger.get('revision') == FEM_REVISION[1] and FEM_NEW in ledger['assumptions']:
        return raw, None
    if (ledger.get('revision') != FEM_REVISION[0] or FEM_OLD not in ledger['assumptions'] or
            FEM_CAPS_OLD not in ledger['assumptions']):
        raise ValueError('fem/minnich.json is not the expected demonstration ledger')
    ids = ledger['analyzed_component_ids']
    if not all(f'frame_{i}_{r}_{j}' in ids for i, r in ((0, 0), (3, 1)) for j in (0, 1, 2, 4, 5, 6)):
        raise ValueError('fem/minnich.json does not list the twelve end-row frames')
    return raw, ledger


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--base', type=Path, default=ROOT / 'data/bridges' / BID, help='bridge folder (default: the repository)')
    parser.add_argument('--fem', type=Path, default=ROOT / 'fem/minnich.json', help='FEM demonstration ledger')
    parser.add_argument('--backup', type=Path, default=ROOT / 'data/fem_research', help='backup folder')
    args = parser.parse_args()
    correct(args.base, args.fem, args.backup)

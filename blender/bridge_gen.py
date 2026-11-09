#!/usr/bin/env python3
"""
Parametric Blender/Cycles bridge builder for the three INDOT structures (from their NBI inspection reports).

    python3 bridge_gen.py --build 07620            # -> blender/out/07620/bridge.blend
    python3 bridge_gen.py --render 07620 [preview|medium|final] [view ...]
    python3 bridge_gen.py --export 07620 [--lite]
    python3 bridge_gen.py --pano 07620

Coordinates (feet): X = along the bridge (station, increasing in the direction of travel), Y = left, Z = up.
Deck top at the centreline is Z = 0. Skewed supports run along (sin s, cos s) where s is the skew angle.
"""
import os, sys, math, json, random, time, argparse
import numpy as np
import bpy, bmesh
from mathutils import Vector, Matrix, Euler
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
from common import mesh_from_arrays, prism, box, cylinder, extrude_profile, coll, box_uv, T

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
OUT = os.path.join(HERE, 'out'); os.makedirs(OUT, exist_ok=True)

# ----------------------------------------------------------------------------- bridge definitions
# Everything dimensional comes from bridges/<id>/bridge.json; the entries below add the modelling assumptions
# (member sizes, ground levels, what sits under the bridge) read off the inspection photos.
BRIDGES = {
    '19027': dict(
        folder='19027_sagamore_pkwy', kind='girder', spans=[32, 92, 101, 101, 101, 92], W=43.0, Wr=39.8, skew=0.0,
        parapet='nj', deck_t=0.75, girder=dict(depth=3.0, bf=1.0, tf=0.09, tw=0.06, lines=8, overhang=3.0, haunch=0.15, paint='steel_green'),
        conc_span=0,                               # span A: 6 concrete beams
        piers=[dict(type='abutment_slopewall'), dict(type='wall', L=44.0), dict(type='wall', L=43.5),
               dict(type='hammerhead', L=43.5, col_d=3.5, col_off=10.0), dict(type='hammerhead', L=43.5, col_d=3.5, col_off=10.0),
               dict(type='hammerhead', L=43.5, col_d=3.5, col_off=10.0), dict(type='abutment_fill')],
        ground=dict(kind='viaduct', z_nat=-18.6, roads=[dict(x=78, width=48, type='street', name='9th St'), dict(x=473, width=26, type='ramp', name='ramp', angle=12)],
                    railroad=dict(x=176, tracks=1, z=-19.2), fill_top=-0.3, berm=-5.0, side_slope=2.0, spill_slope=2.0, half_w=36.0),
        twin=dict(offset=-67.0), markings='oneway2', pavement='deck_concrete.jpg', approach_pavement='asphalt.jpg', fence_span=2, guardrail='both',
        trees=dict(density=0.0022, zones=[(-220, 760, -260, -95), (-220, 760, 95, 260)], avoid_roads=True, h=(28, 55)),
        cameras=dict(
            elevation=((120, 92, -10), (215, 0, -7), 24), under=((60, -14, -14), (200, 4, -8), 24), deck=((-40, -6, 5.5), (200, -2, 0), 32),
            pier=((300, -40, -14), (378, 0, -5), 28), ramp=((448, -120, -14), (473, 0, -8), 28), aerial=((-80, -420, 220), (260, -20, -10), 28),
            street=((78, -110, -16), (78, 40, -10), 30), rail=((176, 120, -16), (176, -30, -8), 30)),
        panos={'street': (78, -40, -13), 'deck': (120, 0, 5.5), 'pier5': (360, -30, -14), 'rr': (176, 60, -14)},
    ),
    '07620': dict(
        folder='07620_sr28_little_wea', kind='slab', spans=[22.25, 27.0, 22.25], W=39.0, Wr=36.0, skew=20.0,
        parapet='vertical', slab_t=1.67, coping=dict(w=1.33, d=0.9),
        piers=[dict(type='abutment_spill', exposed=3.0), dict(type='pile_bent', n=9, d=1.17), dict(type='pile_bent', n=9, d=1.17), dict(type='abutment_spill', exposed=3.0)],
        ground=dict(kind='creek', z_nat=-7.0, water=-12.95, bed=-14.0, bed_w=12.0, bank_slope=3.2, fill_top=-0.3, berm=-5.0, side_slope=2.5, spill_slope=2.0, half_w=24.0, riprap=True, season='winter'),
        twin=None, markings='twoway2', pavement='deck_concrete.jpg', approach_pavement='asphalt.jpg', guardrail='wbeam', drains=True,
        trees=dict(density=0.0010, zones=[(-400, 400, -400, -60), (-400, 400, 60, 400)], avoid_roads=True, h=(30, 55), lines=[(-380, 380, 140), (-380, 380, -170)]),
        cameras=dict(
            elevation=((-14, -78, -2), (40, 0, -5), 30), under=((-12, 30, -9), (60, -6, -8), 24), deck=((-70, -8, 5.0), (60, 0, 0), 32),
            pier=((20, -36, -10), (24, 0, -6), 35), approach=((-120, 12, 4.5), (40, 0, 0), 35), aerial=((-120, -140, 90), (36, 0, -6), 32),
            channel=((36, -120, -8), (36, 0, -6), 28)),
        panos={'bank': (-10, -40, -3), 'deck': (36, 0, 5.5), 'under': (36, 0, -9)},
    ),
    '41750': dict(
        folder='41750_i70_bayliss', kind='slab', spans=[25.0, 32.0, 25.0], W=43.0, Wr=39.5, skew=15.0,
        parapet='nj', slab_t=1.83, coping=dict(w=1.5, d=1.2),
        piers=[dict(type='abutment_spill', exposed=2.2), dict(type='wall', L=46.5, thick=2.75, batter=False, round_ends=True),
               dict(type='wall', L=46.5, thick=2.75, batter=False, round_ends=True), dict(type='abutment_spill', exposed=2.2)],
        ground=dict(kind='creek', z_nat=-11.0, water=-15.0, bed=-16.0, bed_w=8.0, bank_slope=3.0, fill_top=-0.3, berm=-4.2, side_slope=2.5, spill_slope=2.0, half_w=28.0, riprap=False, season='summer', fields=True),
        twin=dict(offset=72.0), markings='interstate2', pavement='deck_concrete.jpg', approach_pavement='deck_concrete.jpg', guardrail='wbeam', approach_slabs=(20.5, 31.08),
        trees=dict(density=0.00025, zones=[(-500, 500, -500, -120), (-500, 500, 120, 500)], avoid_roads=True, h=(30, 50), clumps=[(300, -260, 6), (-260, 300, 5)]),
        cameras=dict(
            elevation=((-45, -135, 1), (45, 0, -6), 32), under=((44, -54, -8), (12, 0, -6), 28), deck=((-90, -8, 5.0), (80, 0, 0), 32),
            pier=((44, -46, -13), (30, 0, -8), 28), approach=((-150, 14, 4.5), (40, 0, 0), 35), aerial=((-140, -170, 110), (41, 20, -6), 32),
            channel=((41, -150, -9), (41, 0, -6), 28)),
        panos={'bank': (-20, -50, -6), 'deck': (41, 0, 5.5), 'under': (41, 0, -12)},
    ),
}

# ----------------------------------------------------------------------------- helpers
def profile_parapet(kind, h=None):
    """(u, w) points, u measured inward (+) from the outer face, CCW when viewed from +x... returns list for extrude_profile."""
    if kind == 'nj':   # New Jersey safety shape: 32" high, 15" base, 6" top
        h = h or 2.67
        return [(0, 0), (1.25, 0), (1.25, 0.25), (1.0, 0.83), (0.5, 2.3), (0.5, h), (0, h), (-0.05, h), (-0.05, 0)]
    else:               # vertical parapet with chamfered top
        h = h or 2.75
        return [(0, 0), (1.08, 0), (1.08, h - 0.15), (0.95, h), (0.12, h), (0, h - 0.15)]

def iprofile(depth, bf, tf, tw):
    h2 = depth / 2; b2 = bf / 2; w2 = tw / 2
    return [(-b2, -h2), (b2, -h2), (b2, -h2 + tf), (w2, -h2 + tf), (w2, h2 - tf), (b2, h2 - tf), (b2, h2), (-b2, h2), (-b2, h2 - tf), (-w2, h2 - tf), (-w2, -h2 + tf), (-b2, -h2 + tf)]

def wbeam_profile():
    """W-beam guardrail section (12.25" tall, 3.25" deep), u = depth toward the road (+), w = height."""
    d = 0.27
    return [(0, 0), (d, 0.13), (d, 0.33), (0, 0.46), (0, 0.56), (d, 0.69), (d, 0.89), (0, 1.02), (-0.02, 1.02), (-0.02, 0)]

class Frame:
    """bridge geometry helper"""
    def __init__(self, B):
        self.B = B; self.spans = B['spans']; self.L = sum(self.spans); self.W = B['W']; self.Wr = B['Wr']
        self.s = math.radians(B['skew']); self.tan = math.tan(self.s); self.dir = (math.sin(self.s), math.cos(self.s))   # support line direction
        self.stations = [0.0]
        for sp in self.spans: self.stations.append(self.stations[-1] + sp)
        self.pw = (self.W - self.Wr) / 2
        if B['kind'] == 'slab':
            self.t = B['slab_t']; self.soffit = -self.t
        else:
            g = B['girder']; self.t = B['deck_t']; self.soffit = -(self.t + g['haunch'] + g['depth'])
    def para(self, x0, x1, y0, y1):
        t = self.tan
        return [(x0 + y0 * t, y0), (x1 + y0 * t, y0), (x1 + y1 * t, y1), (x0 + y1 * t, y1)]
    def on_line(self, x0, a):
        """point at distance a along the skewed support line through station x0 (a>0 to the left)"""
        return (x0 + a * self.dir[0], a * self.dir[1])
    def dist_to_line(self, x0, x, y):
        """signed perpendicular distance from (x,y) to the skewed support line at station x0 (+ = ahead)"""
        return (x - x0) * math.cos(self.s) - y * math.sin(self.s)

# ----------------------------------------------------------------------------- terrain
class Ground:
    def __init__(self, F, rng):
        self.F = F; self.B = F.B; self.g = F.B['ground']; self.rng = rng
        self.noise_seed = 7
    def z_nat(self, x, y):
        g = self.g; z = g['z_nat']
        # gentle undulation
        z += 0.6 * math.sin(x * 0.021 + 1.3) * math.cos(y * 0.017) + 0.35 * math.sin(x * 0.071 + y * 0.053)
        if g['kind'] == 'creek':
            # channel: runs along the support-line direction through the middle of the centre span, meandering a little
            F = self.F; xc = F.L / 2
            d = F.dist_to_line(xc, x, y) - self.meander(y)
            bw = g['bed_w'] / 2; s = g['bank_slope']
            depth = g['z_nat'] - g['bed']
            if abs(d) < bw: z = g['bed'] + 0.3 * math.sin(y * 0.3)
            elif abs(d) < bw + depth * s: z = min(z, g['bed'] + (abs(d) - bw) / s)
            if g.get('fields'):  # ditch sits in a swale 3 ft below the field level
                sw = 60.0
                if abs(d) < sw: z = min(z, g['z_nat'] - 3.0 * (1 - (abs(d) / sw) ** 2))
        return z
    def meander(self, y):
        """perpendicular offset of the channel centreline (ft) as a function of the across coordinate"""
        return 4.0 * math.sin(y * 0.035) + 1.5 * math.sin(y * 0.11 + 1)
    def channel_pts(self, a0=-330, a1=331, step=10):
        """(x, y) points of the channel centreline (used for the water ribbon)"""
        F = self.F; xc = F.L / 2; pts = []
        for a in np.arange(a0, a1, step):
            x, y = F.on_line(xc, a); m = self.meander(y)
            pts.append((x + m * math.cos(F.s), y - m * math.sin(F.s)))
        return pts
    def z_fill(self, x, y):
        """embankment surface: approach fill at fill_top (side slopes beyond half_w) retained by the abutment stem and
        wingwalls; ahead of each abutment the fill spills under the bridge from the berm level at spill_slope:1; around
        the wingwall ends it comes down as a spill_slope:1 cone, so beside the bridge the natural ground shows.
        Twin structures: the median between the decks is retained behind the abutments (median wall) and slopes down
        as a valley ahead of them."""
        g = self.g; F = self.F; half = g['half_w']; W = F.W; sp = g['spill_slope']; Lw = 9.0
        twin = self.B.get('twin'); gap = False
        if twin:
            off = twin['offset']; lo, hi = min(0, off), max(0, off)
            if lo <= y <= hi:
                yy = y if abs(y) <= abs(y - off) else y - off          # relative to the nearest centreline
                gap = abs(yy) > W / 2 + 0.5
            else: yy = y - hi if y > hi else y - lo
        else: yy = y
        ay = abs(yy)
        approach = g['fill_top'] - (max(0.0, ay - half) / g['side_slope'])
        # support lines are the same skewed lines for both twins, so the distance uses the true y
        d0 = F.dist_to_line(0.0, x, y); d1 = -F.dist_to_line(F.L, x, y); d = min(d0, d1)      # >0 only between the abutments
        if d <= -2.2 and (ay <= W / 2 + 0.5 or gap):   # retained by the abutment stem (+ median wall) and wingwalls; the step sits inside the 4.5 ft stem
            return approach
        if d <= 0 and (ay <= W / 2 + 0.5 or gap): d = 0.0   # inside the stem thickness: treat as the under-bridge level
        under = g['berm'] - d / sp
        if d >= 0 and ay <= W / 2 + 0.5:           # directly under the bridge (or inside the stem thickness)
            return under
        if gap:                                    # median valley between the twin decks
            lat = ay - (W / 2 + 0.5)
            return min(approach, under + lat / sp)
        lateral = max(0.0, ay - (W / 2 + 2.75))
        cone = g['fill_top'] - math.hypot(lateral, max(0.0, Lw + d)) / sp     # slope coming round the wingwall end
        top = min(approach, cone)
        if d > 0: top = min(top, under + max(0.0, ay - (W / 2 + 0.5)) / sp)
        return top
    def z(self, x, y):
        return max(self.z_nat(x, y), self.z_fill(x, y))
    def build(self, M, extent, step_near=2.0, step_far=6.0, near=(-80, None, -110, 110)):
        F = self.F
        x0, x1, y0, y1 = extent
        def grid(step, bx0, bx1, by0, by1, skip=None, name='Terrain'):
            xs = np.arange(bx0, bx1 + 1e-6, step); ys = np.arange(by0, by1 + 1e-6, step)
            X, Y = np.meshgrid(xs, ys); Z = np.vectorize(self.z)(X, Y)
            ny, nx = X.shape; Vv = np.stack([X.ravel(), Y.ravel(), Z.ravel()], 1)
            idx = np.arange(ny * nx).reshape(ny, nx)
            a = idx[:-1, :-1]; b = idx[:-1, 1:]; c = idx[1:, 1:]; d = idx[1:, :-1]
            Fq = np.stack([a.ravel(), b.ravel(), c.ravel(), d.ravel()], 1)
            if skip is not None:
                sx0, sx1, sy0, sy1 = skip
                ins = ((X > sx0) & (X < sx1) & (Y > sy0) & (Y < sy1)).ravel()
                keep = ~(ins[Fq[:, 0]] & ins[Fq[:, 1]] & ins[Fq[:, 2]] & ins[Fq[:, 3]]); Fq = Fq[keep]
            ob = mesh_from_arrays(name, Vv, Fq, box_uv(Vv, Fq, 0.05), 'Terrain', M, smooth=True)
            return ob
        nx0 = near[0]; nx1 = near[1] if near[1] is not None else F.L + 80; ny0, ny1 = near[2], near[3]
        inner = grid(step_near, nx0, nx1, ny0, ny1, None, 'TerrainInner')
        outer = grid(step_far, x0, x1, y0, y1, (nx0 + 0.1, nx1 - 0.1, ny0 + 0.1, ny1 - 0.1), 'TerrainOuter')
        return inner, outer

# ----------------------------------------------------------------------------- superstructure
def build_superstructure(F, M, G):
    B = F.B; L = F.L; W = F.W
    objs = []
    # riding surface with lane markings (own UVs: u along, v across)
    deck_mat = C.lane_marking_material('DeckSurface_' + B['folder'][:5], W, F.Wr, B['markings'], T(B['pavement']), tile_len=40.0)
    poly = F.para(0, L, -W / 2 + F.pw, W / 2 - F.pw)
    V = [(x, y, 0.02) for x, y in poly]; UV = [(x / 40.0, (y + W / 2) / W) for x, y in poly]
    objs.append(mesh_from_arrays('DeckSurface', V, [[0, 1, 2, 3]], UV, 'Superstructure', deck_mat))
    if B['kind'] == 'slab':
        t = B['slab_t']; cp = B['coping']
        objs.append(prism('Slab', F.para(0, L, -W / 2, W / 2), -t, 0.0, 'Superstructure', M['concrete_new'], 0.1))
        # coping: deep edge beam under the parapet with a 45° chamfer inside
        for side in (-1, 1):
            ye = side * W / 2; yi = side * (W / 2 - cp['w'])
            prof = [(0, -t), (0, -t - cp['d']), (cp['w'] - 0.3, -t - cp['d']), (cp['w'], -t - cp['d'] + 0.3), (cp['w'], -t)]
            prof = [(u * side, w) for u, w in prof]   # u inward from the edge
            objs.append(extrude_profile(f'Coping_{"L" if side > 0 else "R"}', prof, [(ye * F.tan, ye, 0), (L + ye * F.tan, ye, 0)], M['concrete_new'], 'Superstructure', uvscale=0.1))
    else:
        g = B['girder']; t = B['deck_t']
        objs.append(prism('DeckSlab', F.para(0, L, -W / 2, W / 2), -t, 0.0, 'Superstructure', M['concrete_new'], 0.1))
        # small edge beam
        for side in (-1, 1):
            ye = side * W / 2
            prof = [(u * side, w) for u, w in [(0, -t), (0, -t - 0.6), (1.0, -t - 0.6), (1.0, -t)]]
            objs.append(extrude_profile(f'EdgeBeam_{"L" if side > 0 else "R"}', prof, [(ye * F.tan, ye, 0), (L + ye * F.tan, ye, 0)], M['concrete_new'], 'Superstructure', uvscale=0.1))
        # steel girders over the steel spans, concrete beams over span A
        n = g['lines']; sp = (W - 2 * g['overhang']) / (n - 1)
        prof = iprofile(g['depth'], g['bf'], g['tf'], g['tw']); zc = -(t + g['haunch'] + g['depth'] / 2)
        cs = B.get('conc_span')
        xs_steel0 = F.stations[cs + 1] if cs is not None else 0.0
        girders = []
        for i in range(n):
            y = -W / 2 + g['overhang'] + i * sp
            girders.append(extrude_profile(f'Girder_{i}', prof, [(xs_steel0 + 0.4 + y * F.tan, y, zc), (L - 0.4 + y * F.tan, y, zc)], M[g['paint']], 'Superstructure', uvscale=0.3))
            # haunch (concrete strip on the top flange)
            objs.append(box(f'Haunch_{i}', (xs_steel0 + L) / 2, y, -t - g['haunch'] / 2, L - xs_steel0 - 0.8, g['bf'] + 0.3, g['haunch'], M['concrete_new'], 'Superstructure'))
        # cross frames (X-braces) every ~22 ft and at supports
        xf = [];
        for a, b in zip(F.stations[cs + 1:-1], F.stations[cs + 2:]):
            nb = max(2, round((b - a) / 22)); xf += [a + (b - a) * k / nb for k in range(nb + 1)]
        xf = sorted(set(round(v, 2) for v in xf))
        braces = []
        d = g['depth'] - 2 * g['tf'] - 0.2
        for x in xf:
            for i in range(n - 1):
                ya = -W / 2 + g['overhang'] + i * sp + g['bf'] / 2; yb = ya + sp - g['bf']
                zt = -(t + g['haunch'] + g['tf'] + 0.1); zb = zt - d
                braces.append(C.cylinder(f'XF_{x:.0f}_{i}a', (x, ya, zt), (x, yb, zb), 0.12, M[g['paint']], 'Superstructure', seg=4))
                braces.append(C.cylinder(f'XF_{x:.0f}_{i}b', (x, ya, zb), (x, yb, zt), 0.12, M[g['paint']], 'Superstructure', seg=4))
                braces.append(box(f'XF_{x:.0f}_{i}c', x, (ya + yb) / 2, zb + 0.08, 0.25, yb - ya, 0.16, M[g['paint']], 'Superstructure'))
                braces.append(box(f'XF_{x:.0f}_{i}d', x, (ya + yb) / 2, zt - 0.08, 0.25, yb - ya, 0.16, M[g['paint']], 'Superstructure'))
        objs.append(C.join(braces, 'CrossFrames'))
        # bearing stiffeners at supports
        st = []
        for x in F.stations[cs + 1:]:
            for i in range(n):
                y = -W / 2 + g['overhang'] + i * sp
                for sgn in (-1, 1):
                    st.append(box(f'Stiff_{x:.0f}_{i}{sgn}', x, y + sgn * (g['bf'] / 4 + g['tw'] / 2), zc, 0.08, g['bf'] / 2 - g['tw'] / 2, g['depth'] - 2 * g['tf'], M[g['paint']], 'Superstructure'))
        objs.append(C.join(st, 'Stiffeners'))
        objs += girders
        # bearings: rocker at piers, fixed at pier 4 (modelled identically: sole plate + block + masonry plate)
        brg = []
        for x in F.stations[cs + 1:]:
            for i in range(n):
                y = -W / 2 + g['overhang'] + i * sp; zb = zc - g['depth'] / 2
                brg.append(box(f'Brg_{x:.0f}_{i}_s', x, y, zb - 0.08, 1.6, 1.2, 0.16, M['steel_green'], 'Superstructure'))
                brg.append(C.cylinder(f'Brg_{x:.0f}_{i}_r', (x, y - 0.5, zb - 0.55), (x, y + 0.5, zb - 0.55), 0.38, M['steel_green'], 'Superstructure', seg=16))
                brg.append(box(f'Brg_{x:.0f}_{i}_m', x, y, zb - 1.0, 2.0, 1.6, 0.16, M['steel_green'], 'Superstructure'))
        objs.append(C.join(brg, 'Bearings'))
        # concrete approach span beams (span A): 6 rectangular beams 1.5 x 2.6
        if cs is not None:
            a, b = F.stations[cs], F.stations[cs + 1]; nb = 6; spc = (W - 2 * 3.5) / (nb - 1)
            cb = []
            for i in range(nb):
                y = -W / 2 + 3.5 + i * spc
                cb.append(box(f'CBeam_{i}', (a + b) / 2, y, -t - 1.3, b - a - 0.5, 1.5, 2.6, M['concrete'], 'Superstructure'))
            objs.append(C.join(cb, 'ConcreteBeams'))
    # parapets
    prof = profile_parapet(B['parapet'])
    for side in (-1, 1):
        ye = side * W / 2
        pp = [(u * side, w) for u, w in prof]
        objs.append(extrude_profile(f'Parapet_{"L" if side > 0 else "R"}', pp, [(ye * F.tan, ye, 0), (L + ye * F.tan, ye, 0)], M['concrete'], 'Superstructure', uvscale=0.12))
    # chain-link fence on the parapets over the railroad span (19027)
    if B.get('fence_span') is not None:
        a, b = F.stations[B['fence_span']], F.stations[B['fence_span'] + 1]
        ph = prof[-4][1] if B['parapet'] == 'nj' else prof[2][1]
        fence = []
        for side in (-1, 1):
            ye = side * (W / 2 - 0.3); n = int((b - a) / 8)
            for k in range(n + 1):
                x = a + (b - a) * k / n
                fence.append(C.cylinder(f'FP_{side}_{k}', (x, ye, ph), (x, ye, ph + 6.0), 0.1, M['galv'], 'Superstructure', seg=8))
            fence.append(C.cylinder(f'FR_{side}', (a, ye, ph + 6.0), (b, ye, ph + 6.0), 0.07, M['galv'], 'Superstructure', seg=6))
            V = [(a, ye, ph + 0.1), (b, ye, ph + 0.1), (b, ye, ph + 6.0), (a, ye, ph + 6.0)]
            fab = mesh_from_arrays(f'Fabric_{side}', V, [[0, 1, 2, 3]], [(0, 0), ((b - a) / 2, 0), ((b - a) / 2, 3), (0, 3)], 'Superstructure', M['chain'])
            fence.append(fab)
        objs += fence
    # deck drains (slab bridges): 4" PVC spouts near the copings
    if B.get('drains'):
        for x in np.arange(12, L - 8, 16):
            for side in (-1, 1):
                y = side * (W / 2 - 2.2)
                objs.append(C.cylinder(f'Drain_{x:.0f}_{side}', (x + y * F.tan, y, -F.t + 0.2), (x + y * F.tan, y, -F.t - 0.5), 0.17, M['galv_dark'], 'Superstructure', seg=10))
    return objs

# ----------------------------------------------------------------------------- substructure
def build_substructure(F, M, G):
    B = F.B; W = F.W; objs = []
    for k, p in enumerate(B['piers']):
        x0 = F.stations[k]; typ = p['type']
        # ground at the support line centre and at the ends
        zg_c = G.z(*F.on_line(x0, 0)); zg = min(zg_c, G.z(*F.on_line(x0, -W / 2 + 2)), G.z(*F.on_line(x0, W / 2 - 2)))
        rot = math.pi / 2 - F.s
        if typ in ('abutment_fill', 'abutment_slopewall', 'abutment_spill', 'abutment_wall'):
            exposed = p.get('exposed', 5.0)
            seat = F.soffit - 0.1                       # bearing seat / slab bearing level
            zb = min(zg - 3.0, seat - exposed - 2.0)    # footing level (buried)
            ahead = 1 if k == 0 else -1                 # direction toward the bridge
            cx, cy = F.on_line(x0, 0)
            # stem wall 4.5 ft thick, its front face at the station line (thick enough to hide the terrain step, see Ground.z_fill)
            wall_c = (cx - ahead * 2.25 * math.cos(F.s), cy + ahead * 2.25 * math.sin(F.s))
            objs.append(box(f'Abut{k}_stem', wall_c[0], wall_c[1], (seat + zb) / 2, W + 1.0, 4.5, seat - zb, M['concrete'], 'Substructure', rot_z=rot))
            if B.get('twin'):   # median wall joining the two abutments across the gap between the decks
                off = B['twin']['offset']; mx, my = F.on_line(x0, off / 2)
                mc = (mx - ahead * 2.25 * math.cos(F.s), my + ahead * 2.25 * math.sin(F.s))
                objs.append(box(f'Abut{k}_median', mc[0], mc[1], (seat + zb) / 2, abs(off) - W + 1.0, 4.5, seat - zb, M['concrete'], 'Substructure', rot_z=rot))
                objs.append(box(f'Abut{k}_medianback', mc[0] - ahead * 1.0 * math.cos(F.s), mc[1] + ahead * 1.0 * math.sin(F.s), (0.0 - 0.1 + seat) / 2, abs(off) - W + 1.0, 2.5, (0.0 - 0.1) - seat, M['concrete'], 'Substructure', rot_z=rot))
            # backwall up to the deck (2.5 ft thick, on the back of the stem)
            bw_c = (cx - ahead * 3.25 * math.cos(F.s), cy + ahead * 3.25 * math.sin(F.s))
            objs.append(box(f'Abut{k}_backwall', bw_c[0], bw_c[1], (0.0 - 0.1 + seat) / 2, W + 1.0, 2.5, (0.0 - 0.1) - seat, M['concrete'], 'Substructure', rot_z=rot))
            # wingwalls: parallel to the roadway, 14 ft long, stepping down
            for side in (-1, 1):
                # wingwall outer face at W/2 + 2.75 so it hides the terrain step at the edge of the retained fill (see Ground.z_fill)
                ex, ey = F.on_line(x0, side * (W / 2 + 1.5))
                wl = 14.0 if typ in ('abutment_wall', 'abutment_fill', 'abutment_slopewall') else 9.0
                wc = (ex - ahead * (wl / 2 - 1.0), ey)
                ztop = 0.0 - 0.1
                objs.append(box(f'Abut{k}_wing{side}', wc[0], wc[1], (ztop + zb) / 2, wl, 2.5, ztop - zb, M['concrete'], 'Substructure', rot_z=0))
            if typ == 'abutment_slopewall':
                # concrete slope paving under span A, from the berm down at 2:1 to the street level
                a, b = x0, x0 + ahead * 34
                pts = []
                for y in np.linspace(-W / 2 - 4, W / 2 + 4, 9):
                    for xx in np.linspace(a, b, 12):
                        pts.append((xx, y, G.z(xx, y) + 0.15))
                V = pts; F2 = []
                for j in range(8):
                    for i in range(11):
                        q = j * 12 + i; F2.append([q, q + 1, q + 13, q + 12])
                objs.append(mesh_from_arrays(f'SlopeWall{k}', V, F2, box_uv(V, F2, 0.08), 'Substructure', M['concrete_new'], smooth=True))
        elif typ == 'wall':
            Lp = p['L']; ztop = F.soffit - (0.9 if B['kind'] == 'girder' else 0.0); H = ztop - zg
            th0 = p.get('thick', 3.0) / 2
            def to_xy(a, b):
                px, py = F.on_line(x0, a); return (px + b * math.cos(F.s), py - b * math.sin(F.s))
            if p.get('round_ends'):
                # solid wall with semicircular ends (stadium plan), straight sides, cap integral with the slab
                pts = []; n = 12
                for i in range(n + 1): ang = -math.pi / 2 + math.pi * i / n; pts.append(to_xy(Lp / 2 - th0 + th0 * math.cos(ang), th0 * math.sin(ang)))
                for i in range(n + 1): ang = math.pi / 2 + math.pi * i / n; pts.append(to_xy(-(Lp / 2 - th0) + th0 * math.cos(ang), th0 * math.sin(ang)))
                objs.append(prism(f'Pier{k}_wall', pts, zg - 3.0, ztop, 'Substructure', M['concrete'], 0.1))
            else:
                # battered ends: trapezoid in elevation (plan length grows toward the base), 4 ft thick at base, 3 ft at top
                batter = p.get('batter', True)
                def wall_pts(z):
                    f = (ztop - z) / max(H, 1) if batter else 0.0; half = Lp / 2 + 0.5 * H * f * 0.6; th = th0 + 0.5 * f
                    return half, th
                V = []; Fq = []
                for zi, z in enumerate((zg - 3.0, ztop)):
                    half, th = wall_pts(z)
                    for (a, b) in ((-half, -th), (half, -th), (half, th), (-half, th)):
                        V.append(to_xy(a, b) + (z,))
                Fq = [[3, 2, 1, 0], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]
                objs.append(mesh_from_arrays(f'Pier{k}_wall', V, Fq, box_uv(V, Fq, 0.1), 'Substructure', M['concrete']))
            if B['kind'] == 'girder':
                # cap / bearing seat
                cxp, cyp = F.on_line(x0, 0)
                objs.append(box(f'Pier{k}_cap', cxp, cyp, ztop + 0.45, Lp + 0.5, 4.6, 0.9, M['concrete'], 'Substructure', rot_z=rot))
            if B['kind'] == 'girder':  # pedestals under the bearings
                g = B['girder']; n = g['lines']; sp = (W - 2 * g['overhang']) / (n - 1)
                for i in range(n):
                    y = -W / 2 + g['overhang'] + i * sp
                    objs.append(box(f'Pier{k}_ped{i}', x0, y, F.soffit - 0.5, 2.2, 2.0, 0.4, M['concrete'], 'Substructure'))
        elif typ in ('hammerhead', 'frame'):
            Lp = p['L']; cd = p['col_d']; off = p['col_off']
            cap_w = p.get('cap_w', 4.0); cap_d = p.get('cap_d', 4.5)
            ztop = F.soffit - (0.9 if B['kind'] == 'girder' else 0.0)
            cxp, cyp = F.on_line(x0, 0)
            if typ == 'hammerhead':
                # cap with tapered ends: full depth between the columns, half depth at the tips
                half = Lp / 2; taper_from = off + cd / 2 + 1.0
                pts = [(-half, ztop), (half, ztop), (half, ztop - cap_d * 0.5), (taper_from, ztop - cap_d), (-taper_from, ztop - cap_d), (-half, ztop - cap_d * 0.5)]
                V = [];
                for sgn in (-1, 1):
                    for (a, z) in pts:
                        px, py = F.on_line(x0, a); px += sgn * cap_w / 2 * math.cos(F.s); py -= sgn * cap_w / 2 * math.sin(F.s); V.append((px, py, z))
                n = len(pts); Fq = [list(range(n))[::-1], list(range(n, 2 * n))]
                for i in range(n):
                    j = (i + 1) % n; Fq.append([i, j, n + j, n + i])
                objs.append(mesh_from_arrays(f'Pier{k}_cap', V, Fq, box_uv(V, Fq, 0.1), 'Substructure', M['concrete']))
            else:
                objs.append(box(f'Pier{k}_cap', cxp, cyp, ztop - cap_d / 2, Lp, cap_w, cap_d, M['concrete'], 'Substructure', rot_z=rot))
            for sgn in (-1, 1):
                px, py = F.on_line(x0, sgn * off); zgc = G.z(px, py)
                objs.append(C.cylinder(f'Pier{k}_col{sgn}', (px, py, zgc - 4.0), (px, py, ztop - cap_d + 0.2), cd / 2, M['concrete'], 'Substructure', seg=32))
            if B['kind'] == 'girder':
                g = B['girder']; n = g['lines']; sp = (W - 2 * g['overhang']) / (n - 1)
                for i in range(n):
                    y = -W / 2 + g['overhang'] + i * sp
                    objs.append(box(f'Pier{k}_ped{i}', x0, y, F.soffit - 0.5, 2.2, 2.0, 0.4, M['concrete'], 'Substructure'))
        elif typ == 'pile_bent':
            n = p['n']; d = p['d']; cap_w, cap_d = 2.6, 1.6
            cxp, cyp = F.on_line(x0, 0); Lp = W - 1.0
            objs.append(box(f'Pier{k}_cap', cxp, cyp, F.soffit - cap_d / 2, Lp, cap_w, cap_d, M['concrete'], 'Substructure', rot_z=rot))
            spc = (Lp - 2.0) / (n - 1)
            for i in range(n):
                a = -(Lp - 2.0) / 2 + i * spc; px, py = F.on_line(x0, a); zgc = G.z(px, py)
                objs.append(C.cylinder(f'Pier{k}_pile{i}', (px, py, zgc - 6.0), (px, py, F.soffit - cap_d + 0.1), d / 2, M['steel_black'], 'Substructure', seg=20))
    return objs

# ----------------------------------------------------------------------------- approaches, roads, railroad, water
def ribbon(name, pts, width, mat, zfun, lift=0.1, uv_along=40.0, uv_mode='road'):
    """pavement strip along a polyline of (x, y) points; UV u = distance/uv_along, v across 0..1"""
    V = []; UV = []; s = 0.0
    for i, p in enumerate(pts):
        a = pts[max(0, i - 1)]; b = pts[min(len(pts) - 1, i + 1)]
        tx, ty = b[0] - a[0], b[1] - a[1]; l = math.hypot(tx, ty) or 1; tx /= l; ty /= l; nx, ny = -ty, tx
        if i: s += math.hypot(p[0] - a[0], p[1] - a[1])
        for k, w in enumerate((-width / 2, width / 2)):
            x, y = p[0] + nx * w, p[1] + ny * w
            V.append((x, y, zfun(x, y) + lift)); UV.append((s / uv_along, float(k)))
    Fq = [[2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2] for i in range(len(pts) - 1)]
    UVl = [UV[v] for f in Fq for v in f]
    return mesh_from_arrays(name, V, Fq, UVl, 'Site', mat, smooth=True)

def build_site(F, M, G, rng):
    B = F.B; W = F.W; L = F.L; g = B['ground']; objs = []
    # approach pavement + approach slabs + guardrail, both ends
    pav_mat = C.lane_marking_material('Approach_' + B['folder'][:5], W, F.Wr, B['markings'], T(B.get('approach_pavement', B['pavement'])), tile_len=40.0, tint=(0.95, 0.94, 0.9, 1))
    for end in (0, 1):
        ahead = -1 if end == 0 else 1; x0 = 0.0 if end == 0 else L
        xs = [x0 + ahead * d for d in np.arange(0, 320, 10)]
        pts = [(x + 0.0, 0.0) for x in xs]
        # approach pavement: flush with the deck riding surface (z = 0); the fill top below it is the subgrade
        objs.append(ribbon(f'Approach{end}', pts, F.Wr + 0.4, pav_mat, lambda x, y: 0.0, lift=0.0))
        # paved shoulder each side, falling 0.3 ft to the grass edge
        for side in (-1, 1):
            spts = [(x, side * (F.Wr / 2 + 2.7)) for x in xs]
            objs.append(ribbon(f'Shoulder{end}{side}', spts, 5.4, M['asphalt'], lambda x, y: -0.02 - 0.25 * max(0.0, (abs(y) - F.Wr / 2) / 5.4), lift=0.0))
        # approach slab (concrete), length per end from the report (default 20.5 ft), top slightly proud of the asphalt
        asl = B.get('approach_slabs', (20.5, 20.5))[end]
        sl = prism(f'ApproachSlab{end}', F.para(x0 + (ahead * asl if ahead < 0 else 0), x0 + (ahead * asl if ahead > 0 else 0), -F.Wr / 2, F.Wr / 2), g['fill_top'] - 0.5, 0.03, 'Site', M['concrete_new'], 0.1)
        objs.append(sl)
        # guardrail
        if B.get('guardrail'):
            for side in (-1, 1):
                ye = side * (W / 2 - 0.6)
                xa = x0 + ahead * 1.0; xb = x0 + ahead * 110.0
                npost = int(abs(xb - xa) / 6.25)
                posts = []
                zp = -0.25                                   # grass/shoulder level at the post line
                for k in range(npost + 1):
                    x = xa + (xb - xa) * k / npost
                    posts.append(box(f'GRpost{end}{side}_{k}', x, ye, zp + 0.35, 0.5, 0.5, 5.2, M['galv_dark'], 'Site'))
                    posts.append(box(f'GRblk{end}{side}_{k}', x, ye - side * 0.45, zp + 2.35, 0.5, 0.55, 1.1, M['wood_post'], 'Site'))
                objs.append(C.join(posts, f'GRposts{end}{side}'))
                prof = [(u * side, w) for u, w in wbeam_profile()]
                zr = zp + 1.8                                 # rail top ~2.8 ft above grade (31 in)
                yr = ye - side * 0.75
                path = [(xa, yr, zr), (xb, yr, zr), (xb + ahead * 12, yr + side * 1.5, zr - 0.6), (xb + ahead * 25, yr + side * 3.0, zr - 1.75)]
                objs.append(extrude_profile(f'WBeam{end}{side}', prof, path, M['galv'], 'Site', uvscale=0.3))
    # what the bridge crosses
    if g['kind'] == 'viaduct':
        for r in g['roads']:
            ang = math.radians(r.get('angle', 0)); xr = r['x']
            pts = [(xr + math.sin(ang) * d, d) for d in np.arange(-320, 321, 10)]
            zr = lambda x, y: g['z_nat'] + 0.5
            mat = C.lane_marking_material('Road_' + r['name'].replace(' ', ''), r['width'] + 2, r['width'] - 2, 'twoway2' if r['type'] == 'street' else 'oneway2', T('asphalt.jpg'), tile_len=40.0, tint=(0.9, 0.9, 0.9, 1))
            objs.append(ribbon('Road_' + r['name'].replace(' ', ''), pts, r['width'], mat, zr, lift=0.0))
            if r['type'] == 'street':   # curbs and sidewalks
                for side in (-1, 1):
                    cpts = [(x + side * (r['width'] / 2 + 3.0) * math.cos(ang), y - side * (r['width'] / 2 + 3.0) * math.sin(ang)) for x, y in pts]
                    objs.append(ribbon(f'Sidewalk{side}', cpts, 6.0, M['concrete_new'], lambda x, y: g['z_nat'] + 0.95, lift=0.0))
        rr = g.get('railroad')
        if rr:
            xr = rr['x']; ztop = rr['z']
            pts = [(xr, d) for d in np.arange(-320, 321, 10)]
            # ballast prism: crown 14 ft wide, 1.5 ft above ground with 1.5:1 shoulders -> two ribbons
            objs.append(ribbon('Ballast', pts, 14.0, M['ballast'], lambda x, y: ztop, lift=0.0))
            for side in (-1, 1):
                spts = [(x + side * 8.5, y) for x, y in pts]
                objs.append(ribbon(f'BallastShoulder{side}', spts, 3.5, M['ballast'], lambda x, y: ztop - 0.75, lift=0.0))
            ties = []
            for d in np.arange(-318, 319, 1.65):
                ties.append(box(f'Tie_{d:.0f}', xr, d, ztop + 0.3, 8.5, 0.75, 0.6, M['tie'], 'Site'))
            objs.append(C.join(ties, 'Ties'))
            for side in (-1, 1):
                y_rail = side * 2.36
                objs.append(extrude_profile(f'Rail{side}', [(-0.22, 0), (0.22, 0), (0.22, 0.08), (0.05, 0.1), (0.05, 0.45), (0.12, 0.5), (0.12, 0.6), (-0.12, 0.6), (-0.12, 0.5), (-0.05, 0.45), (-0.05, 0.1), (-0.22, 0.08)],
                                            [(xr + y_rail, -320, ztop + 0.6), (xr + y_rail, 320, ztop + 0.6)], M['rail'], 'Site', uvscale=0.3))
    else:
        # creek water and bed
        wz = g['water']
        pts = G.channel_pts()
        ww = g['bed_w'] + 2 * (wz - g['bed']) * g['bank_slope'] + 6.0      # wide enough to always cut into both banks
        objs.append(ribbon('Water', pts, ww, M['water'], lambda x, y: wz, lift=0.0))
        # muddy bed under the water so the bottom is not grass
        objs.append(ribbon('CreekBed', pts, g['bed_w'] - 1.0, M['mud'], lambda x, y: g['bed'] + 0.05, lift=0.0))   # flat bed strip, always under water
        if g.get('riprap'):
            # riprap revetment on the spill slopes under the bridge (+6 ft beyond the copings), from the berm down to the water
            def on_slope(x, y):
                z = G.z(x, y)
                return (-6 < x - y * F.tan < L + 6) and abs(y) < W / 2 + 8 and z < g['berm'] + 0.4 and z > wz - 1.2
            V = []; Fq = []; keep = {}
            xs = np.linspace(-8, L + 8, 46); ys = np.linspace(-W / 2 - 10, W / 2 + 10, 40)
            for y in ys:
                for x in xs:
                    xx = x + y * F.tan; V.append((xx + rng.uniform(-0.3, 0.3), y + rng.uniform(-0.3, 0.3), G.z(xx, y) + 0.45 + rng.uniform(-0.25, 0.35)))
            flags = [on_slope(v[0], v[1]) for v in V]
            for j in range(len(ys) - 1):
                for i in range(len(xs) - 1):
                    q = j * len(xs) + i; quad = [q, q + 1, q + len(xs) + 1, q + len(xs)]
                    if sum(flags[v] for v in quad) >= 3: Fq.append(quad)
            # boundary vertices (off the slope) are tucked under the grass so the sheet never pokes above the embankment
            used = {v for f in Fq for v in f}
            V = [(v[0], v[1], v[2] if flags[k] else G.z(v[0], v[1]) - 0.5) if k in used else v for k, v in enumerate(V)]
            objs.append(mesh_from_arrays('Riprap', V, Fq, box_uv(V, Fq, 0.1), 'Site', M['riprap'], smooth=True))
            # loose stones on the revetment
            rock = bmesh.new(); bmesh.ops.create_icosphere(rock, subdivisions=2, radius=1.0)
            me = bpy.data.meshes.new('RockBase'); rock.to_mesh(me); rock.free(); me.materials.append(M['riprap']); me.shade_smooth()
            uv = me.uv_layers.new(name='UVMap'); Vv = np.array([v.co for v in me.vertices]); Fv = [p.vertices[:] for p in me.polygons]; uv.data.foreach_set('uv', box_uv(Vv, Fv, 0.5).ravel())
            n = 0
            for k in range(9000):
                x = rng.uniform(-6, L + 6); y = rng.uniform(-W / 2 - 8, W / 2 + 8); xx = x + y * F.tan; z = G.z(xx, y)
                if not on_slope(xx, y): continue
                ob = bpy.data.objects.new(f'Rock_{k}', me); coll('Rocks').objects.link(ob); s = rng.uniform(0.3, 0.75)
                ob.location = (xx, y, z + 0.3 * s); ob.scale = (s, s * rng.uniform(0.7, 1.1), s * 0.6); ob.rotation_euler = (rng.uniform(0, 3), rng.uniform(0, 3), rng.uniform(0, 3))
                n += 1
                if n >= 1800: break
    return objs

# ----------------------------------------------------------------------------- vegetation
def build_vegetation(F, M, G, rng, terrain_inner):
    B = F.B; tcfg = B['trees']; g = B['ground']
    if g.get('season') == 'winter':
        variants = [C.make_tree_variant(0, M, ncards=0), C.make_tree_variant(1, M, ncards=0), C.make_tree_variant(2, M, ncards=90)]
        for n in M['leaf2'].node_tree.nodes:
            if n.type == 'HUE_SAT': n.inputs['Saturation'].default_value = 0.35; n.inputs['Value'].default_value = 0.6
    else:
        variants = [C.make_tree_variant(i, M) for i in range(3)]
    pos = []
    def blocked(x, y):
        if g['kind'] == 'viaduct':
            for r in g['roads']:
                ang = math.radians(r.get('angle', 0)); d = (x - r['x']) * math.cos(ang) - y * math.sin(ang)
                if abs(d) < r['width'] / 2 + 12: return True
            if g.get('railroad') and abs(x - g['railroad']['x']) < 22: return True
        # roadway corridor and under the deck
        if abs(y) < g['half_w'] + 6 and (x < 0 or x > F.L): return True
        if -2 < x < F.L + 2 and abs(y) < F.W / 2 + 6: return True
        if B.get('twin'):
            off = B['twin']['offset']
            if -2 < x < F.L + 2 and abs(y - off) < F.W / 2 + 6: return True
            if abs(y - off) < g['half_w'] + 6 and (x < 0 or x > F.L): return True
        if g['kind'] == 'creek':
            if G.z_nat(x, y) < g['z_nat'] - 1.0: return True   # channel
        for (pos, tgt, lens) in B['cameras'].values():       # keep the foreground of every camera clear
            if math.hypot(x - pos[0], y - pos[1]) < 16: return True
            # and the sight line to the target
            vx, vy = tgt[0] - pos[0], tgt[1] - pos[1]; L2 = vx * vx + vy * vy or 1.0
            t = max(0.0, min(1.0, ((x - pos[0]) * vx + (y - pos[1]) * vy) / L2))
            if t < 0.6 and math.hypot(x - pos[0] - t * vx, y - pos[1] - t * vy) < 10 + 20 * t: return True
        return False
    for (x0, x1, y0, y1) in tcfg['zones']:
        n = int((x1 - x0) * (y1 - y0) * tcfg['density'])
        for _ in range(n):
            x = rng.uniform(x0, x1); y = rng.uniform(y0, y1)
            if blocked(x, y): continue
            pos.append((x, y, rng.uniform(*tcfg['h']), rng.uniform(0, 6.28)))
    for (x0, x1, y) in tcfg.get('lines', []):     # hedgerow / field edge tree line
        for x in np.arange(x0, x1, 14):
            xx = x + rng.uniform(-4, 4); yy = y + rng.uniform(-8, 8)
            if not blocked(xx, yy): pos.append((xx, yy, rng.uniform(*tcfg['h']), rng.uniform(0, 6.28)))
    for (cx, cy, n) in tcfg.get('clumps', []):
        for _ in range(n):
            xx = cx + rng.uniform(-30, 30); yy = cy + rng.uniform(-30, 30)
            if not blocked(xx, yy): pos.append((xx, yy, rng.uniform(*tcfg['h']), rng.uniform(0, 6.28)))
    C.place_trees(variants, pos, G.z, rng)
    clumps = C.grass_clump_collection(M)
    def weight(x, y, z):
        if g['kind'] == 'viaduct':
            if blocked(x, y) and not (abs(y) < F.W / 2 + 6 and -2 < x < F.L + 2): return 0.0
            return 0.8 if abs(y) < 160 else 0.0
        if z < g['water'] + 0.3: return 0.0
        if abs(y) < F.Wr / 2 + 7.6 and (x < 0 or x > F.L): return 0.0   # pavement + shoulders (+1 grid cell so no clump pokes through)
        if B.get('twin') and abs(y - B['twin']['offset']) < F.Wr / 2 + 7.6 and (x < 0 or x > F.L): return 0.0
        if g.get('riprap') and -14 < x - y * F.tan < F.L + 14 and abs(y) < F.W / 2 + 10 and z < g['berm'] + 1: return 0.1
        return 0.9 if abs(y) < 160 and -120 < x < F.L + 120 else 0.0
    C.scatter_grass(terrain_inner, clumps, 60000 if g['kind'] != 'viaduct' else 45000, weight, size=0.6 if g.get('season') != 'winter' else 0.5)
    if g.get('season') == 'winter':
        M['grass_clump'].node_tree.nodes['ALBEDO'].image  # keep; tint dry
        for n in M['grass_clump'].node_tree.nodes:
            if n.type == 'MIX' and n.data_type == 'RGBA': n.inputs[7].default_value = (0.78, 0.66, 0.42, 1)
    return len(pos)

# ----------------------------------------------------------------------------- build / render / export
def build(bid):
    B = BRIDGES[bid]; t0 = time.time()
    sc = C.reset_scene(); rng = random.Random(1)
    M = C.standard_materials()
    M['chain'] = C.pbr('ChainLink', T('chainlink.png'), rough=0.45, metal=0.85, alpha_from_albedo=True, tint=(0.75, 0.78, 0.8, 1))
    F = Frame(B); G = Ground(F, rng)
    if B['ground'].get('season') == 'winter':
        M['grass'] = M['dry_grass']
    ext = (-420, F.L + 420, -420, 420) if B['kind'] == 'slab' else (-300, F.L + 300, -330, 330)
    inner, outer = G.build(M['grass'], ext, step_near=2.0, step_far=6.0, near=(-90, F.L + 90, -120, 120))
    print('terrain', round(time.time() - t0, 1), flush=True)
    sup = build_superstructure(F, M, G); sub = build_substructure(F, M, G)
    print('structure', round(time.time() - t0, 1), flush=True)
    site = build_site(F, M, G, rng)
    print('site', round(time.time() - t0, 1), flush=True)
    # twin structure: collection instance of superstructure + substructure, offset across
    if B.get('twin'):
        tc = bpy.data.collections.new('TwinSource'); bpy.context.scene.collection.children.link(tc)
        for o in sup + sub:
            if o is None: continue
            dup = o.copy(); dup.data = o.data; tc.objects.link(dup)
        bpy.context.scene.collection.children.unlink(tc)
        inst = bpy.data.objects.new('TwinBridge', None); inst.instance_type = 'COLLECTION'; inst.instance_collection = tc
        inst.location = (B['twin']['offset'] * F.tan, B['twin']['offset'], 0); coll('Twin').objects.link(inst)
        # twin approaches (pavement only)
        pav = next(o for o in site if o.name.startswith('Approach0'))
        for o in site:
            if o.name.startswith('Approach') and o.name[8:9].isdigit() or o.name.startswith('Shoulder'):
                d = o.copy(); d.data = o.data; d.location.y += B['twin']['offset']; d.location.x += B['twin']['offset'] * F.tan; coll('Twin').objects.link(d)
    ntrees = build_vegetation(F, M, G, rng, inner)
    print('vegetation', ntrees, 'trees', round(time.time() - t0, 1), flush=True)
    # far ground
    zf = B['ground']['z_nat'] - 1.2                      # far plane just under the outer terrain edge, as a frame so it never covers the creek
    x0, x1, y0, y1 = ext; R = 9000
    Vf = [(-R, -R, zf), (R, -R, zf), (R, R, zf), (-R, R, zf), (x0, y0, zf), (x1, y0, zf), (x1, y1, zf), (x0, y1, zf)]
    Ff = [[0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]
    far = mesh_from_arrays('FarGround', Vf, Ff, box_uv(Vf, Ff, 0.01), 'Terrain', M['grass'])
    C.setup_world(sc, sun_elev=42 if B['ground'].get('season') != 'winter' else 28, sun_rot=200)
    for name, (pos, tgt, lens) in B['cameras'].items():
        C.add_camera(sc, name, pos, tgt, lens, zfun=G.z)
    sc.camera = bpy.data.objects['Cam_elevation']
    od = os.path.join(OUT, bid); os.makedirs(od, exist_ok=True)
    blend = os.path.join(od, 'bridge.blend')
    bpy.ops.wm.save_as_mainfile(filepath=blend, compress=True)
    print('saved', blend, 'objects', len(bpy.data.objects), round(time.time() - t0, 1), 's')

def render_panos(bid, width=3072, samples=64):
    B = BRIDGES[bid]; blend = os.path.join(OUT, bid, 'bridge.blend')
    bpy.ops.wm.open_mainfile(filepath=blend); sc = bpy.context.scene
    sc.render.resolution_x = width; sc.render.resolution_y = width // 2; sc.cycles.samples = samples
    od = os.path.join(OUT, bid, 'panos'); os.makedirs(od, exist_ok=True)
    cd = bpy.data.cameras.new('PanoCam'); cd.type = 'PANO'; cd.panorama_type = 'EQUIRECTANGULAR'; cd.clip_end = 20000
    cam = bpy.data.objects.new('PanoCam', cd); sc.collection.objects.link(cam); sc.camera = cam
    meta = {}
    for name, (x, y, z) in B['panos'].items():
        if os.path.exists(os.path.join(od, name + '.png')): continue
        cam.location = (x, y, z); cam.rotation_euler = Vector((1, 0, 0)).to_track_quat('-Z', 'Y').to_euler()
        sc.render.filepath = os.path.join(od, name + '.png'); t = time.time(); bpy.ops.render.render(write_still=True)
        meta[name] = {'pos': [x, y, z], 'forward': [1, 0]}; print(f'pano {name}: {time.time() - t:.0f}s', flush=True)
    json.dump(meta, open(os.path.join(od, 'panos.json'), 'w'), indent=1)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--build'); ap.add_argument('--render', nargs='+'); ap.add_argument('--export'); ap.add_argument('--lite', action='store_true'); ap.add_argument('--pano')
    a = ap.parse_args()
    if a.build: build(a.build)
    if a.render:
        bid = a.render[0]; q = a.render[1] if len(a.render) > 1 else 'preview'; names = a.render[2:] or list(BRIDGES[bid]['cameras'].keys())
        C.render_views(os.path.join(OUT, bid, 'bridge.blend'), names, q, os.path.join(OUT, bid, 'renders_' + q))
    if a.export:
        bid = a.export; folder = BRIDGES[bid]['folder']; od = os.path.join(ROOT, 'bridges', folder, 'model'); os.makedirs(od, exist_ok=True)
        C.export_glb(os.path.join(OUT, bid, 'bridge.blend'), os.path.join(od, f'bridge_{bid}{"_lite" if a.lite else ""}.glb'), lite=a.lite)
    if a.pano: render_panos(a.pano)

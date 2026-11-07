"""Build inspection sheets (2D defect-mapping drawings) from a bridge's source model.

    python scripts/build_inspection_sheets.py beechwood

Each sheet is an A3 landscape SVG made of true orthographic views of model.glb. sheets.json ties every view back
to the model. A sheet point (u, v) inside a view (both 0..1, v pointing down the sheet) is the world point

    P = origin + u * extent_m[0] * U + v * extent_m[1] * V          (glTF world axes, metres)

and the inspected surface is the first surface hit by a ray from P along -normal. The origin lies on the face of
the view nearest the viewer, so the ray starts in front of every surface in the view. Each view also stores the
visible region of every inspectable part (hidden parts already subtracted), so the inspection app can name the
element under a sketch without loading the 3D model.

Visibility is exact to the model's triangles: where two parts overlap on the sheet, each pair of overlapping
triangles is compared on its depth planes and the overlap is split along the line where the planes cross. Crease
lines are kept only where they are not hidden by any surface in 3D. Members, views and labels use the plans' names
(Beam Line No. 1-4 west to east, Wing A-D, Pour A and B).

Recorded defects are stored in view coordinates, so view frames never move under an existing view id: a view whose
frame would change gets a new id, the old frame is kept under `retired_views` with the view that replaces it, and
the app and the 3D viewer map old defects through it.

Requires numpy and shapely (requirements-sheets.txt). The output is committed; rebuild it whenever model.glb or the
sheet set changes. test_manager.py checks that sheets.json names the current model.glb.
"""
import argparse
import datetime as dt
import hashlib
import json
import math
import multiprocessing
import os
import pickle
import re
import struct
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import shapely
import shapely.affinity
from shapely.geometry import LineString, MultiLineString, Polygon, box
from shapely.ops import linemerge

ROOT = Path(__file__).resolve().parents[1]
FT = 0.3048
CANVAS = (420.0, 297.0)                 # A3 landscape, mm
MAIN = (12.0, 13.0, 396.0, 244.0)       # x, y, w, h of the drawing area above the title block
DENOMS = (20, 25, 30, 40, 50, 60, 75, 100, 125, 150, 175, 200, 250, 300, 400, 500)
FEATURE_DEG = 22.0                      # crease angle drawn as an edge line
DEPTH_EPS = 2e-4                        # m: a surface this much nearer is in front
TIDY = 5e-4                             # m: artefacts of the overlays narrower than 1 mm are removed
GRID = 1e-6                             # m: precision of the polygon overlays (snap rounding, robust)
FRAME_TOL = 1e-3                        # m: a view frame closer than this to the published one keeps it exactly


# ---------------------------------------------------------------- model
def load_glb(path):
    """Mesh triangles per node name, in the model's native axes (X station, Y transverse left, Z up)."""
    data = path.read_bytes()
    length = struct.unpack_from('<I', data, 12)[0]
    gltf = json.loads(data[20:20 + length])
    offset = 20 + length
    blob = data[offset + 8:offset + 8 + struct.unpack_from('<I', data, offset)[0]]
    kinds = {5120: 'i1', 5121: 'u1', 5122: 'i2', 5123: 'u2', 5125: 'u4', 5126: 'f4'}
    width = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}

    def accessor(i):
        acc = gltf['accessors'][i]
        view = gltf['bufferViews'][acc['bufferView']]
        dtype = np.dtype('<' + kinds[acc['componentType']])
        n, w = acc['count'], width[acc['type']]
        start = view.get('byteOffset', 0) + acc.get('byteOffset', 0)
        stride = view.get('byteStride') or dtype.itemsize * w
        raw = np.frombuffer(blob, dtype=np.uint8, count=stride * (n - 1) + dtype.itemsize * w, offset=start)
        rows = np.lib.stride_tricks.as_strided(raw, shape=(n, dtype.itemsize * w), strides=(stride, 1))
        return np.ascontiguousarray(rows).view(dtype).reshape(n, w).astype(np.float64)

    parts = {}

    def walk(index, parent):
        node = gltf['nodes'][index]
        if any(k in node for k in ('translation', 'rotation', 'scale')):
            raise SystemExit(f'{node.get("name")}: TRS node transforms are not supported')
        matrix = parent @ (np.array(node['matrix'], dtype=np.float64).reshape(4, 4).T if 'matrix' in node else np.eye(4))
        if 'mesh' in node:
            tris = []
            for prim in gltf['meshes'][node['mesh']]['primitives']:
                if prim.get('mode', 4) != 4:
                    continue
                pos = accessor(prim['attributes']['POSITION'])
                idx = accessor(prim['indices']).astype(np.int64).ravel() if 'indices' in prim else np.arange(len(pos))
                world = pos @ matrix[:3, :3].T + matrix[:3, 3]
                tris.append(world[idx].reshape(-1, 3, 3))
            glb = np.concatenate(tris)
            # glTF Y-up world (X, Z, -Y) back to the native axes.
            parts[node['name']] = np.stack([glb[..., 0], -glb[..., 2], glb[..., 1]], axis=-1)
        for child in node.get('children', []):
            walk(child, matrix)

    for root in gltf['scenes'][gltf.get('scene', 0)]['nodes']:
        walk(root, np.eye(4))
    return parts


def to_glb(vec):
    """Native (X, Y left, Z up) vector to glTF world axes (X, Z, -Y)."""
    x, y, z = vec
    return [round(float(x), 6), round(float(z), 6), round(float(-y), 6) + 0.0]


def to_native(g):
    return np.array([g[0], -g[2], g[1]], float)


def clip_triangles(tris, lo, hi):
    """Clip triangles to an axis-aligned box. Triangles that straddle a plane are cut and re-fanned."""
    lo, hi = np.asarray(lo, float), np.asarray(hi, float)
    inside = np.all((tris >= lo - 1e-9) & (tris <= hi + 1e-9), axis=(1, 2))
    outside = np.any(np.all(tris < lo - 1e-9, axis=1) | np.all(tris > hi + 1e-9, axis=1), axis=1)
    keep = [tris[inside]]
    for tri in tris[~inside & ~outside]:
        poly = list(tri)
        for axis in range(3):
            for bound, sign in ((lo[axis], 1), (hi[axis], -1)):
                out, n = [], len(poly)
                for i in range(n):
                    a, b = poly[i], poly[(i + 1) % n]
                    da, db = sign * (a[axis] - bound), sign * (b[axis] - bound)
                    if da >= 0:
                        out.append(a)
                    if (da >= 0) != (db >= 0):
                        out.append(a + (b - a) * (da / (da - db)))
                poly = out
                if len(poly) < 3:
                    break
            if len(poly) < 3:
                break
        if len(poly) >= 3:
            keep.append(np.array([[poly[0], poly[i], poly[i + 1]] for i in range(1, len(poly) - 1)]))
    # Close the cuts: a solid cut by the box gets a cap on each cut plane, so a member cut off in front of a face
    # (a beam stub in front of an end bent) still hides that face.
    for axis in range(3):
        for bound, sign in ((lo[axis], -1), (hi[axis], 1)):
            cap = section_cap(tris, axis, bound, sign, lo, hi)
            if cap is not None:
                keep.append(cap)
    return np.concatenate(keep) if keep else np.zeros((0, 3, 3))


def section_cap(tris, axis, c, sign, lo, hi):
    """Triangles closing the section of a closed mesh by the plane (axis = c), inside the box, facing `sign`."""
    d = tris[..., axis] - c
    if not ((d.min(axis=1) < 0) & (d.max(axis=1) > 0)).any():
        return None
    c = c + 1e-7 * (1 if np.isclose(d, 0).any() else 0)     # keep vertices off the plane
    d = tris[..., axis] - c
    crossing = (d.min(axis=1) < 0) & (d.max(axis=1) > 0)
    others = [k for k in range(3) if k != axis]
    segs = []
    for tri, dd in zip(tris[crossing], d[crossing]):
        pts = []
        for i, j in ((0, 1), (1, 2), (2, 0)):
            if (dd[i] < 0) != (dd[j] < 0):
                a, b = (tri[i], tri[j]) if tuple(tri[i]) < tuple(tri[j]) else (tri[j], tri[i])   # same point from both sides
                da, db = a[axis] - c, b[axis] - c
                q = a + (b - a) * (da / (da - db))
                pts.append((round(q[others[0]], 7), round(q[others[1]], 7)))
        if len(pts) == 2 and pts[0] != pts[1]:
            segs.append(pts)
    if not segs:
        return None
    rings = [g for g in lines_of(linemerge(MultiLineString(segs))) if g.is_ring and len(g.coords) > 3]
    if not rings:
        return None
    area = Polygon()
    for ring in rings:                                    # even-odd: nested loops are holes
        area = area.symmetric_difference(Polygon(ring).buffer(0))
    area = area.intersection(box(lo[others[0]], lo[others[1]], hi[others[0]], hi[others[1]]))
    out = []
    for poly in pieces(area):
        for t in shapely.get_parts(shapely.constrained_delaunay_triangles(poly)):
            xy = np.asarray(t.exterior.coords)[:3]
            tri = np.zeros((3, 3))
            tri[:, axis] = c
            tri[:, others[0]], tri[:, others[1]] = xy[:, 0], xy[:, 1]
            n = np.cross(tri[1] - tri[0], tri[2] - tri[0])
            if n[axis] * sign < 0:
                tri = tri[[0, 2, 1]]
            out.append(tri)
    return np.array(out) if out else None


def ray_hit(tris, origin, direction):
    """Distance along the ray to the nearest triangle (inf when missed). Moller-Trumbore, vectorised."""
    e1, e2 = tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0]
    p = np.cross(direction, e2)
    det = np.einsum('ij,ij->i', e1, p)
    ok = np.abs(det) > 1e-12
    inv = np.where(ok, 1.0 / np.where(ok, det, 1.0), 0.0)
    t0 = origin - tris[:, 0]
    u = np.einsum('ij,ij->i', t0, p) * inv
    q = np.cross(t0, e1)
    v = (q @ direction) * inv
    t = np.einsum('ij,ij->i', e2, q) * inv
    hit = ok & (u >= 0) & (v >= 0) & (u + v <= 1) & (t > 1e-6)
    return t[hit].min() if hit.any() else np.inf


def top_z(tris, x, y):
    """Highest surface of a part above a plan point (native), or None."""
    t = ray_hit(tris, np.array([x, y, 500.0]), np.array([0.0, 0.0, -1.0]))
    return None if not np.isfinite(t) else 500.0 - t


def bottom_z(tris, x, y):
    t = ray_hit(tris, np.array([x, y, -500.0]), np.array([0.0, 0.0, 1.0]))
    return None if not np.isfinite(t) else -500.0 + t


# ---------------------------------------------------------------- views
@dataclass
class View:
    id: str
    label: str
    U: tuple
    V: tuple
    N: tuple                       # towards the viewer; U x V = -N (a true, unmirrored view)
    parts: list                    # inspectable parts, in hit-test priority order
    refs: list = field(default_factory=list)   # context parts: drawn grey, occlude, not inspectable
    clip: tuple = None             # ((xmin, ymin, zmin), (xmax, ymax, zmax)) in native axes
    edges: bool = True             # draw crease lines (off for grooved deck surfaces)
    ends: tuple = None             # words at the left and right ends, e.g. ('SOUTH', 'NORTH')
    sides: tuple = None            # words at the top and bottom edges of a plan view, e.g. ('WEST', 'EAST')
    bents: bool = False            # draw bent centre lines (views whose U is +-X)
    overlays: list = field(default_factory=list)  # thin surface items (pavement markings): drawn, never occlude
    key: bool = False              # explanatory view (key plan): drawn, not published for recording
    scale: float = 1.0             # drawing scale relative to the sheet scale (key plans are smaller)
    notes: list = field(default_factory=list)     # annotation callbacks f(ctx)
    labels: dict = field(default_factory=dict)    # part -> label text inside its region (default: the part's short label)
    room: tuple = (0.0, 0.0)       # mm kept free left and right of the view for callouts
    band: bool = False             # a label band above the view (leaders to small parts, centre-line names)
    match: tuple = ()              # native X of match lines (where a member is cut between two views)


class Projected:
    def __init__(self, name, tris, view):
        self.name = name
        U, V, N = (np.asarray(a, float) for a in (view.U, view.V, view.N))
        self.N = N
        self.uv = np.stack([tris @ U, tris @ V], axis=-1)
        self.depth = tris @ N
        self.dmin, self.dmax = self.depth.min(axis=1), self.depth.max(axis=1)
        e1, e2 = tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0]
        normals = np.cross(e1, e2)
        area2 = np.linalg.norm(normals, axis=1)
        self.tris = tris
        self.front = (normals @ N) > 1e-9 * np.maximum(area2, 1e-12)
        self.normals = normals / np.maximum(area2, 1e-15)[:, None]
        d1, d2 = self.uv[:, 1] - self.uv[:, 0], self.uv[:, 2] - self.uv[:, 0]
        self.flat = np.abs(d1[:, 0] * d2[:, 1] - d1[:, 1] * d2[:, 0]) > 1e-10   # not seen edge-on
        rings = np.concatenate([self.uv, self.uv[:, :1]], axis=1)
        self.polys = np.full(len(tris), None, dtype=object)
        self.polys[self.flat] = shapely.polygons(rings[self.flat])
        live = self.polys[self.flat]
        self.sil = clean(tidy(close_gaps(union(live))), 1e-6) if len(live) else Polygon()
        self.bounds = self.sil.bounds if not self.sil.is_empty else None
        self.visible = self.sil
        self._tree = None
        self._planes = None

    @property
    def tree(self):
        if self._tree is None:
            self._index = np.flatnonzero(self.flat)
            self._tree = shapely.STRtree(self.polys[self._index])
        return self._tree

    @property
    def planes(self):
        """Depth as a plane over the sheet for every triangle: d = a*u + b*v + c."""
        if self._planes is None:
            A = np.concatenate([self.uv, np.ones(self.uv.shape[:2] + (1,))], axis=2)
            out = np.zeros((len(self.uv), 3))
            ok = self.flat
            out[ok] = np.linalg.solve(A[ok], self.depth[ok][..., None])[..., 0]
            self._planes = out
        return self._planes

    def depth_at(self, pts):
        """Nearest-to-viewer depth of this part under each 2D point (-inf where it has no surface)."""
        pts = np.atleast_2d(np.asarray(pts, float))
        out = np.full(len(pts), -np.inf)
        if not len(pts) or not self.flat.any():
            return out
        # Within 20 um: points on region outlines are snapped to the 1 um overlay grid, just off the triangle edges.
        pi, ti = self.tree.query(shapely.points(pts), predicate='dwithin', distance=2e-5)
        if len(pi):
            ti = self._index[ti]
            pl = self.planes[ti]
            d = pl[:, 0] * pts[pi, 0] + pl[:, 1] * pts[pi, 1] + pl[:, 2]
            np.maximum.at(out, pi, d)
        return out

    def crease_segments(self):
        """Candidate crease and open-boundary edges (3D, native), seen from the front."""
        verts = self.tris.reshape(-1, 3)
        key = np.round(verts / 1e-5).astype(np.int64)
        welded, ids = np.unique(key, axis=0, return_inverse=True)
        ids = ids.ravel()
        faces = ids.reshape(-1, 3)
        edges = np.sort(faces[:, [[0, 1], [1, 2], [2, 0]]].reshape(-1, 2), axis=1)
        owner = np.repeat(np.arange(len(faces)), 3)
        uniq, inverse, counts = np.unique(edges, axis=0, return_inverse=True, return_counts=True)
        order = np.argsort(inverse.ravel(), kind='stable')
        starts = np.concatenate([[0], np.cumsum(counts)[:-1]])
        first, second = owner[order[starts]], owner[order[np.minimum(starts + 1, len(order) - 1)]]
        two = counts == 2
        cosang = np.einsum('ij,ij->i', self.normals[first], self.normals[second])
        crease = two & (cosang < math.cos(math.radians(FEATURE_DEG)))
        seen = self.front[first] | (two & self.front[second])
        pick = (crease | (counts == 1) | (counts > 2)) & seen
        xyz = np.zeros((len(welded), 3))
        xyz[ids] = verts
        return xyz[uniq[pick]]


def union(geoms):
    """Union on a 1 micrometre grid. Unions of many small, nearly coincident triangles in floating point can silently
    drop pieces; snap-rounding overlay on a fixed grid is robust."""
    geoms = polygonal([g for g in geoms if g is not None])
    return shapely.union_all(geoms, grid_size=GRID) if len(geoms) else Polygon()


def polygonal(arr):
    """Keep only the areas of overlay results (triangles that touch along an edge or at a corner also give lines and
    points, which the snap-rounding overlay refuses to mix with areas). None entries stay None."""
    arr = np.asarray(arr, dtype=object).copy()
    kind = shapely.get_type_id(arr)
    for i in np.flatnonzero(~np.isin(kind, (-1, 3, 6))):
        polys = [g for g in shapely.get_parts(arr[i]) if g.geom_type in ('Polygon', 'MultiPolygon')]
        arr[i] = shapely.union_all(polys) if polys else Polygon()
    return arr


def pieces(geom):
    if geom is None or geom.is_empty:
        return []
    if isinstance(geom, Polygon):
        return [geom]
    return [g for g in getattr(geom, 'geoms', []) if isinstance(g, Polygon)]


def clean(geom, min_area=1e-4):
    """Drop slivers and pinholes left by unioning many small triangles (pieces and holes under min_area m2)."""
    out = []
    for poly in pieces(geom):
        if poly.area < min_area:
            continue
        holes = [r for r in poly.interiors if Polygon(r).area >= min_area]
        out.append(Polygon(poly.exterior, holes))
    return union(out) if out else Polygon()


def half_planes(planes, centres, eps):
    """For each depth-difference plane e (e0 + eu*u + ev*v), the region where e >= -eps, as a polygon around the
    triangle centre it is used with (None: the whole triangle qualifies, False: none of it does)."""
    out = np.full(len(planes), None, dtype=object)
    g = np.hypot(planes[:, 0], planes[:, 1])
    at_c = planes[:, 0] * centres[:, 0] + planes[:, 1] * centres[:, 1] + planes[:, 2] + eps
    flat = g < 1e-9
    out[flat & (at_c < 0)] = False
    tilt = ~flat
    n = np.zeros((len(planes), 2))
    n[tilt] = planes[tilt, :2] / g[tilt, None]
    dist = np.zeros(len(planes))
    dist[tilt] = at_c[tilt] / g[tilt]                   # signed distance of the centre from the boundary line
    far = tilt & (np.abs(dist) > 200.0)                 # triangles are far smaller than 200 m: all or nothing
    out[far & (dist < 0)] = False
    cut = tilt & ~far
    if cut.any():
        nn, p0 = n[cut], centres[cut] - n[cut] * dist[cut, None]
        t = np.stack([-nn[:, 1], nn[:, 0]], axis=1)
        L = 400.0
        quad = np.stack([p0 + L * t, p0 - L * t, p0 - L * t + L * nn, p0 + L * t + L * nn, p0 + L * t], axis=1)
        out[cut] = shapely.polygons(quad)
    return out


def occluded_by(a, b):
    """Exact part of a's silhouette that b hides: the points where a surface of b is nearer than every surface of a.
    For each triangle of b over a, the parts where some triangle of a is at least as near (each pair cut along the
    line where their depth planes cross) are removed; what is left of the triangle is hidden."""
    fb = np.flatnonzero(b.flat)
    if not len(fb) or not a.flat.any():
        return Polygon()
    sil = a.sil
    shapely.prepare(sil)
    cand = fb[shapely.intersects(b.polys[fb], sil)]
    if not len(cand):
        return Polygon()
    over = polygonal(shapely.intersection(b.polys[cand], sil))
    keep = shapely.area(over) > 1e-10
    cand, over = cand[keep], over[keep]
    if not len(cand):
        return Polygon()
    ib, ia = a.tree.query(b.polys[cand], predicate='intersects')
    ta, tb = a._index[ia], cand[ib]
    # Pairs where a's triangle lies wholly behind b's cannot protect anything; where it lies wholly in front, all of
    # the overlap is protected. Only pairs whose depth ranges overlap are cut along the crossing line.
    behind = a.dmax[ta] < b.dmin[tb] - DEPTH_EPS
    ib, ta, tb = ib[~behind], ta[~behind], tb[~behind]
    inter = polygonal(shapely.intersection(a.polys[ta], b.polys[tb]))
    ok = shapely.area(inter) > 1e-12
    ib, ta, tb, inter = ib[ok], ta[ok], tb[ok], inter[ok]
    wins = inter.copy()
    cross = a.dmin[ta] < b.dmax[tb] - DEPTH_EPS
    if cross.any():
        halves = half_planes(a.planes[ta[cross]] - b.planes[tb[cross]], a.uv[ta[cross]].mean(axis=1), DEPTH_EPS)
        part = wins[cross]
        lost = np.array([h is False for h in halves])
        cut = np.array([h is not None and h is not False for h in halves])
        part[lost] = None
        if cut.any():
            part[cut] = polygonal(shapely.intersection(part[cut], np.array(list(halves[cut]), dtype=object)))
        wins[cross] = part
    hidden = list(over)
    order = np.argsort(ib, kind='stable')
    groups, starts = np.unique(ib[order], return_index=True)
    bounds = list(starts[1:]) + [len(order)]
    for g, s0, s1 in zip(groups, starts, bounds):
        shield = [w for w in wins[order[s0:s1]] if w is not None and not w.is_empty]
        if shield:
            hidden[g] = shapely.difference(over[g], union(shield), grid_size=GRID)
    hidden = [h for h in hidden if not h.is_empty and h.area > 1e-10]
    if not hidden:
        return Polygon()
    out = union(hidden)
    return open_slivers(out)


def close_gaps(geom, r=TIDY):
    """Morphological closing: fills slits and pinholes narrower than 2r. Used on a part's own silhouette and on the
    area hidden in front of it, where such gaps can only be overlay artefacts (it never uncovers anything)."""
    if geom.is_empty:
        return geom
    with np.errstate(divide='ignore', invalid='ignore'):
        out = geom.buffer(r, join_style='mitre').buffer(-r, join_style='mitre')
    return out if out.is_valid and not out.is_empty and np.all(np.isfinite(out.bounds)) else geom


def tidy(geom, r=TIDY):
    """Remove overlay artefacts narrower than 2r: an opening drops slivers and spikes, and holes thinner than 2r (by
    twice their area over their perimeter) are filled. Snap-rounding overlays of long, thin triangles can leave such
    artefacts, a fraction of a millimetre wide. Gaps open to the outside are kept: a thin member in front is real."""
    if geom.is_empty:
        return geom
    with np.errstate(divide='ignore', invalid='ignore'):
        out = geom.buffer(-r, join_style='mitre').buffer(r, join_style='mitre')
    if not out.is_valid or (not out.is_empty and not np.all(np.isfinite(out.bounds))):
        out = geom
    polys = []
    for poly in pieces(out):
        holes = [h for h in poly.interiors if 2 * Polygon(h).area / max(h.length, 1e-12) >= 2 * r]
        polys.append(Polygon(poly.exterior, holes))
    return union(polys) if polys else Polygon()


def open_slivers(geom, r=2e-6):
    """Remove slivers a few micrometres wide (left where neighbouring triangles meet) by a morphological opening."""
    with np.errstate(divide='ignore', invalid='ignore'):
        opened = geom.buffer(-r, join_style='mitre').buffer(r, join_style='mitre')
    if opened.is_empty:
        return opened                       # nothing but slivers
    if not opened.is_valid or not np.all(np.isfinite(opened.bounds)):
        return geom
    return opened


def resolve_occlusion(items):
    """Subtract from each part everything in front of it."""
    for a in items:
        cover = []
        for b in items:
            if b is a or a.bounds is None or b.bounds is None:
                continue
            if b.bounds[0] > a.bounds[2] or b.bounds[2] < a.bounds[0] or b.bounds[1] > a.bounds[3] or b.bounds[3] < a.bounds[1]:
                continue
            if not a.sil.intersects(b.sil):
                continue
            hidden = occluded_by(a, b)
            if not hidden.is_empty:
                cover.append(hidden)
        if cover:
            a.visible = clean(tidy(shapely.difference(a.sil, close_gaps(union(cover)), grid_size=GRID)))


def visible_creases(p, items, step=0.02):
    """Crease edges of p that no surface in the view hides, as 2D lines (sheet uv, metres)."""
    segs = p.crease_segments()
    if not len(segs):
        return []
    U = np.asarray(VIEW_AXES['U']); V = np.asarray(VIEW_AXES['V'])
    a, b = segs[:, 0], segs[:, 1]
    la, lb = np.stack([a @ U, a @ V], 1), np.stack([b @ U, b @ V], 1)
    lengths = np.linalg.norm(lb - la, axis=1)
    keep = lengths > 0.01
    a, b, la, lb, lengths = a[keep], b[keep], la[keep], lb[keep], lengths[keep]
    n = np.maximum(1, np.ceil(lengths / step).astype(int))
    seg_id = np.repeat(np.arange(len(n)), n)
    k = np.concatenate([np.arange(m) for m in n])
    t0, t1 = k / n[seg_id], (k + 1) / n[seg_id]
    tm = (t0 + t1) / 2
    mid3 = a[seg_id] + (b - a)[seg_id] * tm[:, None]
    mid2 = np.stack([mid3 @ U, mid3 @ V], 1)
    depth = mid3 @ p.N
    near = np.full(len(mid2), -np.inf)
    for q in items:
        if q.bounds is None:
            continue
        inside = (mid2[:, 0] >= q.bounds[0] - 1e-6) & (mid2[:, 0] <= q.bounds[2] + 1e-6) & (mid2[:, 1] >= q.bounds[1] - 1e-6) & (mid2[:, 1] <= q.bounds[3] + 1e-6)
        if inside.any():
            near[inside] = np.maximum(near[inside], q.depth_at(mid2[inside]))
    vis = depth >= near - 3e-3
    lines, cur = [], None
    for i in range(len(seg_id)):
        s = seg_id[i]
        p_start = la[s] + (lb[s] - la[s]) * t0[i]
        p_end = la[s] + (lb[s] - la[s]) * t1[i]
        if vis[i]:
            if cur is not None and cur[0] == s:
                cur[1].append(tuple(p_end))
            else:
                if cur is not None and len(cur[1]) > 1:
                    lines.append(cur[1])
                cur = [s, [tuple(p_start), tuple(p_end)]]
        else:
            if cur is not None and len(cur[1]) > 1:
                lines.append(cur[1])
            cur = None
    if cur is not None and len(cur[1]) > 1:
        lines.append(cur[1])
    return [LineString(l) for l in lines if LineString(l).length > 0.008]


VIEW_AXES = {}


def project_view(model, view):
    items, inspect = [], set(view.parts)
    for name in view.parts + view.refs:
        tris = model[name]
        if view.clip:
            tris = clip_triangles(tris, *view.clip)
        if len(tris):
            proj = Projected(name, tris, view)
            if not proj.sil.is_empty:
                proj.inspect = name in inspect and not view.key
                items.append(proj)
    resolve_occlusion(items)
    VIEW_AXES.update(U=view.U, V=view.V)
    for p in items:
        p.creases = visible_creases(p, items) if (view.edges and p.inspect) else []
    overlays = []
    for name in view.overlays:
        tris = clip_triangles(model[name], *view.clip) if view.clip else model[name]
        if len(tris):
            overlays.append(Projected(name, tris, view))
    view.overlay_items = [o for o in overlays if not o.sil.is_empty]
    return items


# ---------------------------------------------------------------- names from the plans
# Plan sheets 32-37 (End Bent 1/4, Bent 2/3): Beam Line No. 1 is the west beam, No. 4 the east beam. The model numbers
# its girders 1-4 from east to west, so model girder i is Beam Line 5 - i. Wings: End Bent 1 Wing A east, B west;
# End Bent 4 Wing C west, D east. Pour A is the pile cap, Pour B the integral end-bent concrete above it.
def beam_line(i):
    return 5 - int(i)


WINGS = {'b1_wing_R': 'A', 'b1_wing_L': 'B', 'b4_wing_L': 'C', 'b4_wing_R': 'D'}
SPAN_SIDE = {(2, -1): 'A', (2, 1): 'B', (3, -1): 'B', (3, 1): 'C'}

# AASHTO Manual for Bridge Element Inspection (2019) National Bridge Elements used on Beechwood.
ELEMENTS = {
    12: ('Reinforced Concrete Deck', 'sq ft'),
    109: ('Prestressed Concrete Open Girder/Beam', 'ft'),
    205: ('Reinforced Concrete Column', 'each'),
    210: ('Reinforced Concrete Pier Wall', 'ft'),
    215: ('Reinforced Concrete Abutment', 'ft'),
    234: ('Reinforced Concrete Pier Cap', 'ft'),
    310: ('Elastomeric Bearing', 'each'),
    331: ('Reinforced Concrete Bridge Railing', 'ft'),
}


def beechwood_parts(manifest):
    """Inspectable parts: NBE element, plan name, short sheet label, measuring axis (native) and element quantity."""
    out = {}
    for p in manifest['parts']:
        pid, (lo, hi) = p['id'], p['bounds_m']
        span = [hi[i] - lo[i] for i in range(3)]
        rec = None
        if pid == 'deck':
            rec = dict(element=12, label='Deck', short='DECK', quantity=manifest['deck_length_ft'] * manifest['deck_width_ft'])
        elif pid.startswith('girder_'):
            bl = beam_line(pid[-1])
            rec = dict(element=109, label=f'Span {pid[-2]} · Beam Line {bl}', short=f'BL {bl}', axis=(1, 0, 0),
                       quantity=p['dimensions']['length_ft'])
        elif pid.endswith('_cap') and pid[:2] in ('b2', 'b3'):
            rec = dict(element=234, label=f'Bent {pid[1]} · cap', short='CAP', axis=(0, 1, 0), quantity=p['dimensions']['length_ft'])
        elif '_column_' in pid:
            side = 'west' if pid.endswith('L') else 'east'
            rec = dict(element=205, label=f'Bent {pid[1]} · {side} column', short=f'{side.upper()} COLUMN', quantity=1)
        elif pid.endswith('_wall'):
            rec = dict(element=210, label=f'Bent {pid[1]} · debris wall', short='DEBRIS WALL', axis=(0, 1, 0), quantity=span[1] / FT)
        elif pid in ('b1_cap', 'b4_cap'):
            rec = dict(element=215, label=f'End Bent {pid[1]} · Pour A (pile cap)', short='POUR A · PILE CAP', axis=(0, 1, 0), quantity=span[1] / FT)
        elif pid in ('b1_integral', 'b4_integral'):
            rec = dict(element=215, label=f'End Bent {pid[1]} · Pour B (end diaphragm)', short='POUR B · INTEGRAL END-BENT CONCRETE',
                       axis=(0, 1, 0), quantity=0)
        elif pid in WINGS:
            rec = dict(element=215, label=f'End Bent {pid[1]} · Wing {WINGS[pid]}', short=f'WING {WINGS[pid]}', axis=(1, 0, 0), quantity=span[0] / FT)
        elif 'elastomeric' in p['name']:
            parts_ = pid.split('_')
            bl, side = beam_line(parts_[2]), int(parts_[3])
            rec = dict(element=310, label=f'Bent {pid[1]} · Beam Line {bl} · Span {SPAN_SIDE[(int(pid[1]), side)]} bearing',
                       short=f'BL {bl}', quantity=1)
        elif pid.startswith('rail_'):
            side = 'West' if pid.endswith('L') else 'East'
            rec = dict(element=331, label=f'{side} barrier', short=f'{side.upper()} BARRIER', axis=(1, 0, 0), quantity=span[0] / FT)
        if rec:
            rec['name'] = p['name']
            if 'axis' in rec:
                rec['axis'] = to_glb(rec['axis'])
            rec['quantity'] = round(rec['quantity'], 1)
            out[pid] = rec
    return out


def datum(manifest):
    """Station and elevation of the model origin, from the manifest's native-axes note."""
    note = manifest['native_axes']
    sta = re.search(r'station (\d+)\+(\d+(?:\.\d+)?) at X\s*=\s*0', note)
    el = re.search(r'elevation (\d+(?:\.\d+)?) ft at Z\s*=\s*0', note)
    if not sta or not el:
        raise SystemExit('native_axes does not give the station and elevation of the origin')
    return {'station_ft_at_origin': int(sta[1]) * 100 + float(sta[2]), 'elevation_ft_at_origin': float(el[1]),
            'note': 'glTF X = native X (station increasing), glTF Y = elevation, glTF Z = -native Y (left of centre line is -Z)'}


DATUM = {}


def station(x_m):
    ft = DATUM['station_ft_at_origin'] + x_m / FT
    return f'STA {int(ft // 100)}+{ft % 100:05.2f}'


def elevation(z_m):
    return f'EL. {DATUM["elevation_ft_at_origin"] + z_m / FT:.2f}'


# ---------------------------------------------------------------- Beechwood sheet set
def beechwood_views(model, manifest):
    parts = {p['id']: p for p in manifest['parts']}
    X, Y, Z = (1, 0, 0), (0, 1, 0), (0, 0, 1)
    nX, nY, nZ = (-1, 0, 0), (0, -1, 0), (0, 0, -1)
    bent_x = {i: sum(parts[f'b{i}_cap']['bounds_m'][k][0] for k in (0, 1)) / 2 for i in (1, 2, 3, 4)}
    spans = [('A', 1, 2), ('B', 2, 3), ('C', 3, 4)]
    deck = parts['deck']['bounds_m']
    x0, x1 = deck[0][0], deck[1][0]
    cuts = [x0, bent_x[2], bent_x[3], x1]
    sheets = []
    support = {1: ['b1_integral', 'b1_cap'], 2: ['b2_diaphragm', 'b2_cap', 'b2_pad_filler'],
               3: ['b3_diaphragm', 'b3_cap', 'b3_pad_filler'], 4: ['b4_integral', 'b4_cap']}

    # Deck top and underside: one band per span, cut at the bent centre lines (match lines, not joints).
    top = []
    for k, (span, _, _) in enumerate(spans):
        top.append(View(f'DK1-{span}', f'SPAN {span} · DECK TOP · LOOKING DOWN', X, nY, Z, ['deck'], ['rail_L', 'rail_R'],
                        clip=((cuts[k], -9, -50), (cuts[k + 1], 9, 50)), edges=False, ends=('SOUTH', 'NORTH'),
                        sides=('WEST', 'EAST'), bents=True, overlays=['marking_center', 'marking_edge_L', 'marking_edge_R'],
                        match=(cuts[1], cuts[2])))
    sheets.append(dict(id='DK-1', title='Deck top surface', subtitle='Wearing surface of the concrete deck, spans A to C; bands meet at match lines', rows=[[v] for v in top]))
    under = []
    for k, (span, _, _) in enumerate(spans):
        girders = [f'girder_{span}{i}' for i in (1, 2, 3, 4)]
        refs = ['b1_cap', 'b1_integral', 'b2_cap', 'b2_diaphragm', 'b3_cap', 'b3_diaphragm', 'b4_cap', 'b4_integral',
                'rail_L', 'rail_R'] + [n for n in model if n.startswith(('steel_diaphragm', 'clip_'))]
        steel = sorted(n for n in model if n.startswith('steel_diaphragm') and cuts[k] < parts[n]['bounds_m'][0][0] < cuts[k + 1])

        def steel_note(ctx, steel=steel):
            if steel:
                lo_, hi_ = parts[steel[len(steel) // 2]]['bounds_m']
                ctx.leader(((lo_[0] + hi_[0]) / 2, (lo_[1] + hi_[1]) / 2, lo_[2]), 'STEEL CROSS DIAPHRAGMS · CONTEXT ONLY')

        under.append(View(f'DK2-{span}', f'SPAN {span} · DECK UNDERSIDE AND BEAM SOFFITS · LOOKING UP', X, Y, nZ,
                          girders + ['deck'], refs, clip=((cuts[k], -9, -50), (cuts[k + 1], 9, 50)), ends=('SOUTH', 'NORTH'),
                          sides=('EAST', 'WEST'), bents=True, match=(cuts[1], cuts[2]), notes=[steel_note] if steel else []))
    sheets.append(dict(id='DK-2', title='Deck underside', subtitle='Deck soffit between beams and beam bottom flanges, '
                       'seen from below (east at the top)', rows=[[v] for v in under]))

    # Beam elevations: both faces of each beam line, two beam lines per sheet, one scale for all. The supporting
    # bents are drawn in front of the beam ends, so the embedded ends are not offered for recording.
    for span, s0, s1 in spans:
        for half, lines in (('1', (1, 2)), ('2', (3, 4))):
            rows = []
            for bl in lines:
                g = f'girder_{span}{5 - bl}'
                gb = parts[g]['bounds_m']
                clip = ((gb[0][0] - 0.6, -9, -50), (gb[1][0] + 0.6, 9, 50))
                refs = support[s0] + support[s1]
                west = 'FASCIA' if bl == 1 else 'INTERIOR'
                east = 'FASCIA' if bl == 4 else 'INTERIOR'
                rows.append([View(f'{span}-BL{bl}-W', f'SPAN {span} · BEAM LINE NO. {bl} · WEST FACE ({west}) · LOOKING EAST',
                                  nX, nZ, Y, [g], refs, clip=clip, ends=('NORTH', 'SOUTH'), bents=True)])
                rows.append([View(f'{span}-BL{bl}-E', f'SPAN {span} · BEAM LINE NO. {bl} · EAST FACE ({east}) · LOOKING WEST',
                                  X, nZ, nY, [g], refs, clip=clip, ends=('SOUTH', 'NORTH'), bents=True)])
            sheets.append(dict(id=f'GR-{span}{half}', title=f'Span {span} beams · Beam Lines {lines[0]} and {lines[1]}',
                               subtitle='Both web faces of each beam; the beam ends inside the bents are not recorded here',
                               rows=rows, scale_group='beams'))

    # Interior bents: both faces and both cap ends.
    for b in (2, 3):
        cx = bent_x[b]
        inspect = [f'b{b}_cap', f'b{b}_column_L', f'b{b}_column_R', f'b{b}_wall']
        bear = lambda side: [f'b{b}_bearing_{i}_{side:+d}' for i in (1, 2, 3, 4)]
        refs = [f'b{b}_diaphragm', f'b{b}_pad_filler', 'deck'] + [n for n in model if n.startswith(('girder_', 'haunch_'))]
        clip = ((cx - 1.6, -9, -0.5), (cx + 1.6, 9, 50))
        cap = model[f'b{b}_cap']
        col = model[f'b{b}_column_L']
        cap_bottom = bottom_z(cap, cx, 0.0)
        beam_y = {beam_line(i): sum(parts[f'girder_A{i}']['bounds_m'][k][1] for k in (0, 1)) / 2 for i in (1, 2, 3, 4)}
        seat_outer, seat_inner = top_z(cap, cx, beam_y[1]), top_z(cap, cx, beam_y[2])   # stepped cap, plan sheet 37
        col_base = bottom_z(col, cx, (parts[f'b{b}_column_L']['bounds_m'][0][1] + parts[f'b{b}_column_L']['bounds_m'][1][1]) / 2)

        def bent_notes(ctx, cap_bottom=cap_bottom, seat_outer=seat_outer, seat_inner=seat_inner, col_base=col_base, cx=cx,
                       levels=True):
            if levels:
                ctx.elev(seat_inner, 'left', f'CAP AT BL 2, 3 {elevation(seat_inner)}', dy=-0.7)
                ctx.elev(seat_outer, 'left', f'CAP AT BL 1, 4 {elevation(seat_outer)}', dy=2.6)
                ctx.elev(cap_bottom, 'left', f'BOTTOM OF CAP {elevation(cap_bottom)}')
                ctx.elev(col_base, 'left', f'TOP OF CASING {elevation(col_base)}')
            ctx.centre_line((cx, 0.0, col_base), '℄ STRUCTURE')
            ctx.note_below('COLUMNS 4\'-6" DIAMETER, ROUND')

        def end_notes(ctx, cap_bottom=cap_bottom, cx=cx):
            ctx.centre_line((cx, 0.0, cap_bottom - 0.5), '℄ BENT')

        sheets.append(dict(id=f'BT-{b}', title=f'Bent No. {b}', subtitle=f'{station(cx)} · cap, columns, debris wall and bearings: both faces and both cap ends',
                           rows=[[View(f'B{b}-SOUTH', f'BENT NO. {b} · SOUTH FACE · LOOKING NORTH', nY, nZ, nX,
                                       bear(-1) + inspect, refs, clip=clip, ends=('WEST', 'EAST'), notes=[bent_notes],
                                       room=(46.0, 0.0), band=True),
                                  View(f'B{b}-NORTH', f'BENT NO. {b} · NORTH FACE · LOOKING SOUTH', Y, nZ, X,
                                       bear(1) + inspect, refs, clip=clip, ends=('EAST', 'WEST'),
                                       notes=[lambda ctx, f=bent_notes: f(ctx, levels=False)], band=True),
                                  View(f'B{b}-WEST', 'WEST END · LOOKING EAST', nX, nZ, Y,
                                       [f'b{b}_cap', f'b{b}_column_L'] + bear(-1) + bear(1), refs, clip=clip, ends=('N', 'S'),
                                       notes=[end_notes], band=True),
                                  View(f'B{b}-EAST', 'EAST END · LOOKING WEST', X, nZ, nY,
                                       [f'b{b}_cap', f'b{b}_column_R'] + bear(-1) + bear(1), refs, clip=clip, ends=('S', 'N'),
                                       notes=[end_notes], band=True)]]))

    # End bents: view 1 the face towards the span (Pour A and Pour B), views 2 and 3 the complete wing elevations
    # (wing return and the end of the bent body, 12 ft or 11 ft), and a key plan with the view arrows.
    for b, span in ((1, 'A'), (4, 'C')):
        cx = bent_x[b]
        sgn = 1 if b == 1 else -1                    # +1: the span lies at +X (End Bent 1)
        integral, cap = model[f'b{b}_integral'], model[f'b{b}_cap']
        ib = parts[f'b{b}_integral']['bounds_m']
        half_w = ib[1][1]
        face_x = ib[1][0] if b == 1 else ib[0][0]
        approach_x = cx - sgn * 3.6
        lo, hi = sorted((approach_x, face_x + sgn * 0.6))
        beams = [f'girder_{span}{i}' for i in (1, 2, 3, 4)]
        back_x = ib[0][0] if b == 1 else ib[1][0]    # face towards the approach
        # Plan control point: the end of the bent on the line of the 6 in pavement ledge (sheets 32 and 33).
        top_end = top_z(integral, back_x + sgn * 0.5 * FT, half_w - 0.05)
        cap_bottom = bottom_z(cap, cx, 0.0)
        pour_a_end, pour_a_mid = top_z(cap, cx, half_w - 0.05), top_z(cap, cx, 0.0)
        wing_names = {side: WINGS[f'b{b}_wing_{side}'] for side in ('L', 'R')}
        if b == 1:   # looking south from span A: east (Wing A) on the left
            front_axes, left_wing, right_wing = (Y, nZ, X), 'R', 'L'
        else:        # looking north from span C: west (Wing C) on the left
            front_axes, left_wing, right_wing = (nY, nZ, nX), 'L', 'R'

        def front_notes(ctx, sgn=sgn, face_x=face_x, top_end=top_end, cap_bottom=cap_bottom, pour_a_end=pour_a_end,
                        pour_a_mid=pour_a_mid, beams=beams):
            ctx.centre_line((face_x, 0.0, cap_bottom - 0.3), '℄ STRUCTURE')
            ctx.elev(top_end, 'left', f'TOP OF POUR B AT END {elevation(top_end)}')
            ctx.elev(pour_a_end, 'left', f'TOP OF POUR A {elevation(pour_a_end)}')
            ctx.elev(cap_bottom, 'left', f'BOTTOM OF POUR A {elevation(cap_bottom)}')
            ctx.elev(pour_a_mid, 'right', f'POUR A AT ℄ {elevation(pour_a_mid)}')
            for g in beams:
                gb = parts[g]['bounds_m']
                ctx.below_label((face_x, (gb[0][1] + gb[1][1]) / 2, 0.0), f'BEAM LINE {beam_line(g[-1])}')

        def wing_notes(ctx, side, b=b, sgn=sgn, cx=cx, face_x=face_x, cap_bottom=cap_bottom, integral=integral):
            w = model[f'b{b}_wing_{side}']
            wb = parts[f'b{b}_wing_{side}']['bounds_m']
            y = wb[1][1] - 0.02 if side == 'L' else wb[0][1] + 0.02
            tip_x = wb[0][0] if b == 1 else wb[1][0]
            ztip = top_z(w, tip_x + sgn * 0.02, y)
            zspan = top_z(integral, face_x - sgn * 0.02, y)
            ctx.centre_line((cx, y, cap_bottom - 0.3), '℄ BENT')
            ctx.end_label((tip_x, y, ztip), elevation(ztip))
            ctx.end_label((face_x, y, zspan), elevation(zspan))
            ctx.end_label((tip_x, y, cap_bottom), elevation(cap_bottom))

        front = View(f'E{b}-FRONT', f'VIEW 1 · END BENT NO. {b} · FACE TOWARDS SPAN {span} · LOOKING {"SOUTH" if b == 1 else "NORTH"}',
                     *front_axes, [f'b{b}_integral', f'b{b}_cap'], beams + [f'haunch_{span}{i}' for i in (1, 2, 3, 4)] + ['deck'],
                     # A short stub of each beam and of the deck in front of the face, cut 0.6 m out.
                     clip=((min(face_x - sgn * 1.0, face_x + sgn * 0.6), -9, 0), (max(face_x - sgn * 1.0, face_x + sgn * 0.6), 9, 50)),
                     ends=('WEST', 'EAST') if b == 4 else ('EAST', 'WEST'), notes=[front_notes], room=(46.0, 46.0), band=True,
                     labels={f'b{b}_integral': 'POUR B\nINTEGRAL CONCRETE', f'b{b}_cap': 'POUR A\nPILE CAP'})
        wing_views = []
        for n_view, side in ((2, left_wing), (3, right_wing)):
            outside = Y if side == 'L' else nY
            looking = 'EAST' if side == 'L' else 'WEST'
            u = nX if side == 'L' else X
            wb = parts[f'b{b}_wing_{side}']['bounds_m']
            yclip = ((wb[0][1] - 0.01, 9) if side == 'L' else (-9, wb[1][1] + 0.01))
            ends = ('SPAN END', 'APPROACH END') if (u == X) == (b == 4) else ('APPROACH END', 'SPAN END')
            wing_views.append(View(f'E{b}-WING-{wing_names[side]}', f'VIEW {n_view} · WING {wing_names[side]} · OUTSIDE FACE · LOOKING {looking}',
                                   u, nZ, outside, [f'b{b}_wing_{side}', f'b{b}_integral', f'b{b}_cap'], [],
                                   clip=((lo - 0.2, yclip[0], 0), (hi + 0.2, yclip[1], 50)), ends=ends,
                                   notes=[lambda ctx, side=side, f=wing_notes: f(ctx, side)], room=(15.0, 15.0), band=True,
                                   labels={f'b{b}_wing_{side}': f'WING {wing_names[side]}', f'b{b}_integral': 'POUR B',
                                           f'b{b}_cap': 'POUR A'}))
        if b == 1:   # plan as on sheet 32: approach (south) at the top, east on the left
            key_axes = (Y, X, Z)
        else:        # plan as on sheet 33: approach (north) at the top, west on the left
            key_axes = (nY, nX, Z)

        def key_notes(ctx, b=b, sgn=sgn, cx=cx, face_x=face_x, half_w=half_w, beams=beams, wing_names=wing_names,
                      left_wing=left_wing, right_wing=right_wing):
            zt = 60.0
            ctx.centre_line((cx, half_w + 0.6, zt), '℄ BENT', start=(cx, -half_w - 0.6, zt))
            for g in beams:
                gb = parts[g]['bounds_m']
                ctx.point_label((face_x + sgn * 2.4, (gb[0][1] + gb[1][1]) / 2, zt), f'BL {beam_line(g[-1])}', above=False)
            ctx.arrow((face_x + sgn * 2.9, 0.0, zt), (face_x + sgn * 0.8, 0.0, zt), '1')
            for n_view, side in ((2, left_wing), (3, right_wing)):
                sy = 1 if side == 'L' else -1
                ctx.arrow((cx - sgn * 1.8, sy * (half_w + 1.7), zt), (cx - sgn * 1.8, sy * (half_w + 0.25), zt), str(n_view))
                ctx.point_label((cx - sgn * 2.1, sy * (half_w - 1.4), zt), f'WING {wing_names[side]}', above=False)
            ctx.north_arrow((cx - sgn * 1.9, 0.0, zt))
            wing_ft = 12 if b == 1 else 11
            ctx.note_below(f'BENT 35\'-2" x 3\'-0" · BEAMS AT 8\'-9" · WINGS {wing_ft}\'-0" x 1\'-0"')

        key = View(f'E{b}-KEY', 'KEY PLAN', *key_axes, [], [f'b{b}_integral', f'b{b}_cap', f'b{b}_wing_L', f'b{b}_wing_R'] + beams,
                   clip=((min(approach_x, face_x + sgn * 3.4), -9, -50), (max(approach_x, face_x + sgn * 3.4), 9, 50)),
                   edges=False, key=True, scale=0.42, notes=[key_notes], room=(24.0, 24.0),
                   sides=('APPROACH', f'SPAN {span}'))
        sheets.append(dict(id=f'EB-{b}', title=f'End Bent No. {b}', subtitle=f'{station(cx)} · views 1 to 3 on the key plan · beam and deck stubs are reference only', rows=[[front], wing_views + [key]]))

    # Barriers: both faces of both barriers, each in two bands that meet at mid-length (a match line).
    mid = (x0 + x1) / 2
    rows = []
    for rail, side in (('rail_L', 'WEST'), ('rail_R', 'EAST')):
        outer = Y if rail == 'rail_L' else nY
        inner = nY if rail == 'rail_L' else Y
        for face, n, tag in (('OUTSIDE', outer, 'O'), ('TRAFFIC', inner, 'T')):
            for half, (lo_, hi_) in (('1', (x0 - 1, mid)), ('2', (mid, x1 + 1))):
                looking_west = n == nY
                u = X if looking_west else nX
                ends = ('SOUTH', 'NORTH') if looking_west else ('NORTH', 'SOUTH')
                label = f'{side} BARRIER · {face} FACE · {"SOUTH" if half == "1" else "NORTH"} HALF · LOOKING {"WEST" if looking_west else "EAST"}'
                rows.append([View(f'R{rail[-1]}{tag}-{half}', label, u, nZ, n, [rail], clip=((lo_, -9, -50), (hi_, 9, 50)),
                                  ends=ends, bents=True, match=(mid,))])
    sheets.append(dict(id='RL-1', title='Barriers', subtitle='Outside and traffic faces of both FC barriers; '
                       'each face in two halves that meet at a match line', rows=rows))
    return sheets, bent_x


# ---------------------------------------------------------------- drawing
class Svg:
    def __init__(self):
        self.out = []

    def add(self, s):
        self.out.append(s)

    def text(self, x, y, s, cls='t', anchor='start', extra=''):
        s = s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        self.add(f'<text x="{x:.2f}" y="{y:.2f}" class="{cls}" text-anchor="{anchor}"{extra}>{s}</text>')


def path_d(lines):
    out = []
    for line in lines:
        pts = list(line.coords)
        if len(pts) < 2:
            continue
        out.append('M' + ' '.join(f'{x:.2f},{y:.2f}' for x, y in pts))
    return ''.join(out)


def poly_d(poly):
    out = []
    for ring in [poly.exterior, *poly.interiors]:
        pts = list(ring.coords)[:-1]
        out.append('M' + ' '.join(f'{x:.2f},{y:.2f}' for x, y in pts) + 'Z')
    return ''.join(out)


def lines_of(geom):
    if geom is None or geom.is_empty:
        return []
    if isinstance(geom, LineString):
        return [geom]
    return [g for g in getattr(geom, 'geoms', []) if isinstance(g, LineString)]


ROW_GAP, COL_GAP = 6.0, 16.0
TITLE_W, SMALL_W = 1.85, 1.35          # mm per character of the view titles and of the small direction words


def ends_text(v):
    return f'{v.ends[0]} ← · → {v.ends[1]}' if v.ends and not v.key else ''


def head(v, w):
    """Height (mm) of the header above a view: its title, the direction words (beside the title when they fit,
    otherwise on a second row) and an optional band for leader labels and centre-line names."""
    h = 7.0
    if ends_text(v) and len(v.label) * TITLE_W + len(ends_text(v)) * SMALL_W + 6 > w:
        h += 4.4
    return h + (5.0 if v.band else 0.0)


def foot(v):
    """Room (mm) under a view for beam-line callouts, notes and the names of bent lines inside the view."""
    return 5.0 if v.notes or v.bents else 0.0


def layout(sheet, scale_mm):
    """Row-by-row placement at one scale. Returns ([(view, x, y, w, h)], height, width)."""
    placed, y, widest = [], 0.0, 0.0
    for row in sheet['rows']:
        sizes = [(v.extent[0] * scale_mm * v.scale, v.extent[1] * scale_mm * v.scale) for v in row]
        total = sum(w + v.room[0] + v.room[1] for v, (w, _) in zip(row, sizes)) + COL_GAP * (len(row) - 1)
        top = max(head(v, w) for v, (w, _) in zip(row, sizes))
        x = (MAIN[2] - total) / 2
        for v, (w, h) in zip(row, sizes):
            x += v.room[0]
            placed.append((v, x, y + top, w, h))
            x += w + v.room[1] + COL_GAP
        widest = max(widest, total)
        y += top + max(h + foot(v) for v, (_, h) in zip(row, sizes)) + ROW_GAP
    return placed, y - ROW_GAP, widest


def pick_scale(sheet, denom=None):
    margin = 56 if any(v.bents for row in sheet['rows'] for v in row) else 0   # bent labels beside the views
    for d in ([denom] if denom else DENOMS):
        placed, height, width = layout(sheet, 1000.0 / d)
        if denom or (height <= MAIN[3] and width + margin <= MAIN[2]):
            return d, placed, height
    raise SystemExit(f'{sheet["id"]}: does not fit at 1:{DENOMS[-1]}')


STYLE = ('<style>text{font-family:"IBM Plex Sans",Arial,Helvetica,sans-serif;fill:#1d2124}'
         '.t{font-size:2.6px}.s{font-size:2.4px;fill:#4f565b}.h{font-size:3px;font-weight:600;letter-spacing:.04px}'
         '.big{font-size:5.4px;font-weight:600}.mid{font-size:3.4px;font-weight:600}.lbl{font-size:2.5px;fill:#2f363b;font-weight:600}'
         '.ann{font-size:2.5px;fill:#1d2124}'
         '.j{fill:none;stroke:#1d2124;stroke-width:.16;stroke-dasharray:1.1 .7}'
         '.o{fill:none;stroke:#1d2124;stroke-width:.32;stroke-linejoin:round;stroke-linecap:round}'
         '.e{fill:none;stroke:#1d2124;stroke-width:.16;stroke-linecap:round}'
         '.r{fill:none;stroke:#9aa2a7;stroke-width:.16;stroke-linejoin:round}'
         '.m{fill:#e3e7ea;stroke:#9aa2a7;stroke-width:.1}.f{fill:#eef2f4;stroke:none}.rf{fill:#fafbfb;stroke:none}'
         '.c{fill:none;stroke:#4f565b;stroke-width:.18;stroke-dasharray:4 1 .6 1}.ld{fill:none;stroke:#4f565b;stroke-width:.15}'
         '.ar{fill:#1d2124}.k{fill:none;stroke:#1d2124;stroke-width:.25}.thin{fill:none;stroke:#1d2124;stroke-width:.15}</style>')


class NoteCtx:
    """Drawing helpers for one view's annotations, in native model coordinates."""

    def __init__(self, svg, v, x, y, w, h, s):
        self.svg, self.v, self.x, self.y, self.w, self.h, self.s = svg, v, x, y, w, h, s * v.scale
        self.U, self.V = np.asarray(v.U, float), np.asarray(v.V, float)

    def pt(self, p):
        p = np.asarray(p, float)
        return self.x + (p @ self.U - self.v.range[0]) * self.s, self.y + (p @ self.V - self.v.range[1]) * self.s

    def elev(self, z, side, text, dy=0.8):
        """Elevation callout at the left or right edge of an elevation view (z native); dy moves the text off the line."""
        anchor_pt = np.zeros(3)
        anchor_pt[2] = z
        sy = self.y + (anchor_pt @ self.V - self.v.range[1]) * self.s
        if side == 'left':
            self.svg.add(f'<path class="ld" d="M{self.x - 1:.2f},{sy:.2f}H{self.x - 4:.2f}"/>')
            self.svg.text(self.x - 4.6, sy + dy, text, 'ann', 'end')
        else:
            self.svg.add(f'<path class="ld" d="M{self.x + self.w + 1:.2f},{sy:.2f}H{self.x + self.w + 4:.2f}"/>')
            self.svg.text(self.x + self.w + 4.6, sy + dy, text, 'ann', 'start')

    def centre_line(self, bottom, text, start=None):
        """A centre line. Vertical: from the top of the view (named in the label band) down to `bottom`.
        With `start`: from `start` to `bottom`, named beyond its end (plans)."""
        bx, by = self.pt(bottom)
        if start is None:
            top = self.y - (1.2 if self.v.band else 0.0)
            self.svg.add(f'<path class="c" d="M{bx:.2f},{top:.2f}L{bx:.2f},{by:.2f}"/>')
            self.svg.text(bx, self.y - 2.2 if self.v.band else self.y - 0.8, text, 'ann', 'middle')
        else:
            ax, ay = self.pt(start)
            self.svg.add(f'<path class="c" d="M{ax:.2f},{ay:.2f}L{bx:.2f},{by:.2f}"/>')
            self.svg.text(bx + (1.0 if bx >= ax else -1.0), by + 0.8, text, 'ann', 'start' if bx >= ax else 'end')

    def end_label(self, p, text):
        """A label beside whichever end of the view the point is on, at the point's height."""
        px, py = self.pt(p)
        if px < self.x + self.w / 2:
            self.svg.text(self.x - 1.5, py + 0.9, text, 'ann', 'end')
        else:
            self.svg.text(self.x + self.w + 1.5, py + 0.9, text, 'ann', 'start')

    def leader(self, p, text):
        """A context label under the view with a leader to the point."""
        px, py = self.pt(p)
        self.svg.add(f'<path class="ld" d="M{px:.2f},{py:.2f}V{self.y + self.h + 1.2:.2f}"/>')
        self.svg.text(px, self.y + self.h + 3.6, text, 's', 'middle')

    def below_label(self, p, text):
        px, _ = self.pt(p)
        self.svg.text(px, self.y + self.h + 3.6, text, 'lbl', 'middle')

    def point_label(self, p, text, above=True):
        px, py = self.pt(p)
        self.svg.text(px, py - 1.4 if above else py + 3.2, text, 'ann', 'middle')

    def arrow(self, a, b, text):
        (ax, ay), (bx, by) = self.pt(a), self.pt(b)
        dx, dy = bx - ax, by - ay
        L = math.hypot(dx, dy) or 1
        ux, uy = dx / L, dy / L
        hx, hy = bx - ux * 2.2, by - uy * 2.2
        self.svg.add(f'<path class="thin" d="M{ax:.2f},{ay:.2f}L{hx:.2f},{hy:.2f}"/>')
        self.svg.add(f'<path class="ar" d="M{bx:.2f},{by:.2f}L{hx - uy * 1.1:.2f},{hy + ux * 1.1:.2f}L{hx + uy * 1.1:.2f},{hy - ux * 1.1:.2f}Z"/>')
        self.svg.add(f'<circle cx="{ax - ux * 2.4:.2f}" cy="{ay - uy * 2.4:.2f}" r="2.1" class="thin" fill="#fff"/>')
        self.svg.text(ax - ux * 2.4, ay - uy * 2.4 + 0.9, text, 'lbl', 'middle')

    def north_arrow(self, at):
        # Station increases towards the north on this bridge (the plans' N 0°35' E alignment).
        north = np.array([1.0, 0.0, 0.0])
        d = np.array([north @ self.U, north @ self.V])
        d = d / (np.linalg.norm(d) or 1)
        cx, cy = self.pt(at)
        tip = (cx + d[0] * 3, cy + d[1] * 3)
        tail = (cx - d[0] * 3, cy - d[1] * 3)
        self.svg.add(f'<path class="thin" d="M{tail[0]:.2f},{tail[1]:.2f}L{tip[0]:.2f},{tip[1]:.2f}"/>')
        self.svg.add(f'<path class="ar" d="M{tip[0]:.2f},{tip[1]:.2f}L{tip[0] - d[0] * 2 - d[1] * 1.2:.2f},{tip[1] - d[1] * 2 + d[0] * 1.2:.2f}'
                     f'L{tip[0] - d[0] * 2 + d[1] * 1.2:.2f},{tip[1] - d[1] * 2 - d[0] * 1.2:.2f}Z"/>')
        self.svg.text(tip[0] + d[0] * 2.4, tip[1] + d[1] * 2.4 + 0.9, 'N', 'lbl', 'middle')

    def note_below(self, text):
        self.svg.text(self.x, self.y + self.h + 3.6, text, 'ann', 'start')


def member_limits(p, others, later, edge, gap=3e-4, flush=0.01):
    """Split a part's outline into its own edges and the limits where it meets a later part flush (on the same face,
    within 10 mm of depth): those are drawn thin and dashed, so a limit between two recorded members on one surface
    (a wing and the end of the bent body) does not read as a joint or an edge in the concrete."""
    near = [q for q in others if q.bounds is not None and p.bounds is not None and q.visible.distance(p.visible) < gap]
    if not near:
        return edge, []
    first = {id(q) for q in later}
    joints, keep = [], []
    shared = edge.intersection(union([q.visible.buffer(gap) for q in near]))
    rest = edge.difference(union([q.visible.buffer(gap) for q in near]))
    segs = [(a, b) for line in lines_of(shared) for a, b in zip(np.asarray(line.coords)[:-1], np.asarray(line.coords)[1:])]
    if segs:
        mids = np.array([(a + b) / 2 for a, b in segs])
        dp = p.depth_at(mids)
        depth = np.array([q.depth_at(mids) for q in near])
        flushq = np.abs(depth - dp[None]) < flush
        mine_ = np.array([id(q) in first for q in near])
        for k, (a, b) in enumerate(segs):
            if not flushq[:, k].any():
                keep.append(LineString([a, b]))          # a real edge: one part stands in front of the other
            elif (flushq[:, k] & mine_).any():
                joints.append(LineString([a, b]))        # drawn once, from the earlier of the two parts
    edge = MultiLineString(lines_of(rest) + keep) if (lines_of(rest) or keep) else MultiLineString()
    return edge, joints


def draw_sheet(sheet, info, index, count, bent_x, manifest, denom=None):
    denom, placed, height = pick_scale(sheet, denom)
    s = 1000.0 / denom
    top = MAIN[1] + max(0.0, (MAIN[3] - height) / 2)
    svg = Svg()
    svg.add('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 297" width="420mm" height="297mm">')
    svg.add(STYLE)
    svg.add('<rect width="420" height="297" fill="#fff"/>')
    svg.add('<rect x="5" y="5" width="410" height="287" class="k"/>')
    views = []
    for v, x, y, w, h in placed:
        x += MAIN[0]
        y += top
        sv = s * v.scale
        umin, vmin = v.range[0], v.range[1]
        T = lambda g, x=x, y=y, umin=umin, vmin=vmin, sv=sv: shapely.affinity.affine_transform(g, [sv, 0, 0, sv, x - umin * sv, y - vmin * sv])
        hd = head(v, w)
        svg.text(x, y - hd + 4.6, v.label, 'h')
        if ends_text(v):
            two_rows = hd - (5.0 if v.band else 0.0) > 7.0
            svg.text(x + w, y - hd + 4.6 + (4.4 if two_rows else 0.0), ends_text(v), 's', 'end')
        if v.sides:
            svg.text(x - 1.5, y + 2.6, v.sides[0], 's', 'end')
            svg.text(x - 1.5, y + h - 0.6, v.sides[1], 's', 'end')
        svg.add(f'<g id="view-{v.id}">')
        refs = [p for p in v.items if not p.inspect]
        mine = [p for p in v.items if p.inspect]
        for p in refs:
            for poly in pieces(T(p.visible.simplify(0.006))):
                svg.add(f'<path class="rf" d="{poly_d(poly)}"/>')
        for p in mine:
            for poly in pieces(T(p.visible.simplify(0.002))):
                svg.add(f'<path class="f" d="{poly_d(poly)}"/>')
        for o in getattr(v, 'overlay_items', []):
            for poly in pieces(T(o.sil.simplify(0.002))):
                svg.add(f'<path class="m" d="{poly_d(poly)}"/>')
        for group, cls, tol in ((refs, 'r', 0.006), (mine, 'o', 0.002)):
            for k, p in enumerate(group):
                outline = []
                for poly in pieces(p.visible):
                    outline += lines_of(poly.exterior) + [LineString(r.coords) for r in poly.interiors]
                if not outline:
                    continue
                edge = MultiLineString(outline)
                if cls == 'o':
                    edge, joints = member_limits(p, [q for q in group if q is not p], group[k + 1:], edge)
                    if joints:
                        svg.add(f'<path class="j" d="{path_d(lines_of(T(MultiLineString(joints).simplify(tol))))}"/>')
                if not edge.is_empty:
                    svg.add(f'<path class="{cls}" d="{path_d(lines_of(T(edge.simplify(tol))))}"/>')
                if cls == 'o' and p.creases:
                    d = path_d(lines_of(T(linemerge(MultiLineString(p.creases)).simplify(0.002))))
                    if d:
                        svg.add(f'<path class="e" d="{d}"/>')
        svg.add('</g>')
        # Bent centre lines (and stations) on views whose horizontal axis runs along the bridge.
        if v.bents:
            ux = v.U[0]
            at_bent = lambda x_: any(abs(x_ - bx) < 1e-3 for bx in bent_x.values())
            marks = [(bx, f'END BENT {b}' if b in (1, 4) else f'BENT {b}', any(abs(bx - mx) < 1e-3 for mx in v.match))
                     for b, bx in bent_x.items()]
            marks += [(mx, 'MATCH LINE', False) for mx in v.match if not at_bent(mx)]
            for bx, name, matched in marks:
                u = bx * ux
                if umin - 1e-6 <= u <= umin + v.extent[0] + 1e-6:
                    sx = x + (u - umin) * sv
                    svg.add(f'<path class="c" d="M{sx:.2f},{y - 0.6:.2f}V{y + h + 0.8:.2f}"/>')
                    at = (u - umin) / v.extent[0]
                    if at < 0.06 or at > 0.94:   # at an end of the view: name beside it
                        left = at < 0.5
                        tx, anchor = (min(sx, x) - 1.6, 'end') if left else (max(sx, x + w) + 1.6, 'start')
                        svg.text(tx, y + h / 2 - 0.6, name, 'lbl', anchor)
                        svg.text(tx, y + h / 2 + 2.4, station(bx), 's', anchor)
                        if matched:
                            svg.text(tx, y + h / 2 + 5.2, 'MATCH LINE', 's', anchor)
                    else:                        # inside the view: name under the line
                        svg.text(sx, y + h + 3.6, f'{name} · {station(bx)}', 's', 'middle')
        # Element labels on inspectable regions where they fit (a second line in smaller type); small regions get a
        # leader to a label in the band above the view, or under it.
        leader_x, boxes = [], []
        for p in mine:
            big = max(pieces(p.visible), key=lambda g: g.area, default=None)
            if big is None or (len(mine) == 1 and p.name not in v.labels):
                continue
            lines = v.labels.get(p.name, info[p.name]['short']).split('\n')
            tw = max([len(lines[0]) * 1.45] + [len(t) * 1.25 for t in lines[1:]]) + 1.5
            th = 3.2 + 2.8 * (len(lines) - 1)
            inner = big.buffer(-0.5 * th / sv)
            spot = None
            if not inner.is_empty:
                c = big.centroid
                x0_, y0_, x1_, y1_ = inner.bounds
                grid = [inner.representative_point()] + [shapely.Point(gx, gy) for gx in np.linspace(x0_, x1_, 25)
                                                         for gy in np.linspace(y0_, y1_, 7)]
                for pt in sorted(grid[1:], key=lambda q: q.distance(c)) if not inner.contains(c) else [c] + grid:
                    lab = box(pt.x - tw / 2 / sv, pt.y - th / 2 / sv, pt.x + tw / 2 / sv, pt.y + th / 2 / sv)
                    if big.contains(lab) and not any(lab.intersects(q) for q in boxes):
                        spot = pt
                        boxes.append(lab)
                        break
            if spot is not None:
                lx, ly = x + (spot.x - umin) * sv, y + (spot.y - vmin) * sv - th / 2
                svg.text(lx, ly + 2.5, lines[0], 'lbl', 'middle')
                for k, t in enumerate(lines[1:], 1):
                    svg.text(lx, ly + 2.5 + 2.8 * k, t, 's', 'middle')
            elif big.area * sv * sv > 1.0:
                text = ' · '.join(lines)
                c = big.centroid
                px, py = x + (c.x - umin) * sv, y + (c.y - vmin) * sv
                ly = y - 2.2 if (v.band and (py - y) < h / 2) else y + h + 3.6
                if any(abs(px - q) < len(text) * 0.8 for q in leader_x):
                    continue
                leader_x.append(px)
                svg.add(f'<path class="ld" d="M{px:.2f},{py:.2f}L{px:.2f},{ly + (0.9 if ly < y else -2.5):.2f}"/>')
                svg.text(px, ly, text, 'lbl', 'middle')
        ctx = NoteCtx(svg, v, x, y, w, h, s)
        for note in v.notes:
            note(ctx)
        if v.key:
            svg.add(f'<rect x="{x - 3:.2f}" y="{y - 1.5:.2f}" width="{w + 6:.2f}" height="{h + 3:.2f}" class="ld"/>')
        else:
            views.append((v, [x / CANVAS[0], y / CANVAS[1], w / CANVAS[0], h / CANVAS[1]]))

    # Title block.
    y0 = 262.0
    svg.add(f'<path class="k" d="M5,{y0}H415M120,{y0}V292M250,{y0}V292M308,{y0}V292M355,{y0}V292"/>')
    svg.text(9, y0 + 7, 'BEECHWOOD ROAD OVER LITTLE BLUE RIVER', 'mid')
    svg.text(9, y0 + 12.5, f'Structure {manifest["structure_id"]} · Des. {manifest["designation"]} · Crawford County, Indiana', 's')
    svg.text(9, y0 + 17, f'{len(manifest["spans_ft"])} spans {"-".join(str(s_) for s_ in manifest["spans_ft"])} ft · '
             f'prestressed concrete bulb-tee beams · {manifest["deck_width_ft"]} ft deck', 's')
    svg.text(9, y0 + 25.5, 'INSPECTION SHEET · RECORD DEFECTS ON THE SHADED SURFACES', 's')
    svg.text(124, y0 + 7, sheet['title'].upper(), 'mid')
    svg.text(124, y0 + 12.5, sheet['subtitle'], 's')
    # Legend: what each fill and line means.
    ly = y0 + 16.2
    svg.add(f'<rect x="124" y="{ly}" width="5" height="2.6" class="f"/><rect x="124" y="{ly}" width="5" height="2.6" class="o"/>')
    svg.text(130.5, ly + 2.3, 'Surface to inspect', 's')
    svg.add(f'<rect x="153" y="{ly}" width="5" height="2.6" class="rf"/><rect x="153" y="{ly}" width="5" height="2.6" class="r"/>')
    svg.text(159.5, ly + 2.3, 'Context only', 's')
    svg.add(f'<path class="j" d="M178,{ly + 1.3}h6"/>')
    svg.text(185.5, ly + 2.3, 'Limit between members', 's')
    svg.add(f'<path class="c" d="M215,{ly + 1.3}h7"/>')
    svg.text(223.5, ly + 2.3, 'Centre line', 's')
    svg.text(124, y0 + 23, 'Beam Line No. 1 is the west beam; names follow the plans (sheets 32-37).', 's')
    svg.text(124, y0 + 27, 'Elevations in feet, sampled from the 3D model. Key plans are not to scale.', 's')
    svg.text(254, y0 + 6, 'SCALE', 's')
    svg.text(254, y0 + 12.5, f'1:{denom}', 'mid')
    feet = next(f for f in (100, 50, 20, 10, 5) if f * FT * s <= 46)
    bar = feet * FT * s
    for i in range(5):
        svg.add(f'<rect x="{254 + i * bar / 5:.2f}" y="{y0 + 16}" width="{bar / 5:.2f}" height="1.3" '
                f'fill="{"#1d2124" if i % 2 == 0 else "#fff"}" stroke="#1d2124" stroke-width=".1"/>')
    svg.text(254, y0 + 21.5, '0', 's')
    svg.text(254 + bar, y0 + 21.5, f'{feet} ft', 's', 'middle')
    svg.text(254, y0 + 26.5, f'{feet} ft = {feet * FT:.2f} m', 's')
    svg.text(312, y0 + 6, 'SOURCE', 's')
    svg.text(312, y0 + 11.5, f'3D model rev {manifest.get("revision", "")}', 's')
    svg.text(312, y0 + 16, f'Plans Des. {manifest["designation"]}', 's')
    svg.text(312, y0 + 20.5, f'Generated {dt.date.today().isoformat()}', 's')
    svg.text(359, y0 + 6, 'SHEET', 's')
    svg.text(385, y0 + 17, sheet['id'], 'big', 'middle')
    svg.text(385, y0 + 25, f'{index} of {count}', 's', 'middle')
    svg.add('</svg>')
    return '\n'.join(svg.out), denom, views


def region_json(p, v):
    """Visible region of a part in view-normalised coordinates (u, v in 0..1)."""
    out = []
    umin, vmin = v.range[0], v.range[1]
    clampu = lambda c: min(1.0, max(0.0, c))
    for poly in pieces(p.visible.simplify(0.003)):
        if poly.area < 2e-4:
            continue
        rings = []
        for ring in [poly.exterior, *poly.interiors]:
            rings.append([[round(clampu((x - umin) / v.extent[0]), 5), round(clampu((y - vmin) / v.extent[1]), 5)]
                          for x, y in list(ring.coords)[:-1]])
        out.append(rings)
    return out


def frame_of(v):
    U, V, N = (np.asarray(a, float) for a in (v.U, v.V, v.N))
    origin = U * v.range[0] + V * v.range[1] + N * v.nmax
    return {'origin': to_glb(origin), 'u': to_glb(U), 'v': to_glb(V), 'normal': to_glb(N),
            'extent_m': [round(v.extent[0], 4), round(v.extent[1], 4)]}


def view_json(v, placement):
    frame = frame_of(v)
    regions = [{'part': p.name, 'polygons': region_json(p, v)} for p in v.items if p.inspect]
    return {'id': v.id, 'label': v.label.title().replace('No. ', 'No. ').replace(' · ', ' · '), **frame,
            'placement': [round(c, 6) for c in placement],
            'parts': [p.name for p in v.items if p.inspect],
            'regions': [r for r in regions if r['polygons']]}


def frame_distance(a, b):
    """Largest difference (m) between two published frames, over origin, axes (x extent) and extent."""
    d = max(abs(x - y) for x, y in zip(a['origin'], b['origin']))
    d = max(d, max(abs(x - y) for x, y in zip(a['extent_m'], b['extent_m'])))
    for k in ('u', 'v', 'normal'):
        d = max(d, max(abs(x - y) for x, y in zip(a[k], b[k])) * 100.0)
    return d


def keep_published_frame(v, old):
    """Reuse a published frame exactly when the rebuilt one is within FRAME_TOL, so recorded defects stay put."""
    if old is None:
        return False
    new = frame_of(v)
    gap = frame_distance(new, old)
    if gap > FRAME_TOL:
        raise SystemExit(f'{v.id}: its frame moved by {gap * 1000:.1f} mm since the last build. Give the view a new id '
                         f'(the old one is then retired and its defects are mapped to the new view).')
    U, V, N = (np.asarray(a, float) for a in (v.U, v.V, v.N))
    o = to_native(old['origin'])
    v.range = (float(o @ U), float(o @ V), float(o @ U) + old['extent_m'][0], float(o @ V) + old['extent_m'][1])
    v.extent = tuple(old['extent_m'])
    v.nmax = float(o @ N)
    return True


def match_replacement(old_id, old, new_views):
    """The new view that best replaces a retired one: same viewing direction, most shared parts, nearest centre."""
    best, score = None, None
    on = np.asarray(old['normal'])
    oc = np.asarray(old['origin']) + np.asarray(old['u']) * old['extent_m'][0] / 2 + np.asarray(old['v']) * old['extent_m'][1] / 2
    for nid, nv in new_views.items():
        if float(np.dot(on, nv['normal'])) < 0.999:
            continue
        shared = len(set(old.get('parts', [])) & set(nv['parts']))
        if not shared:
            continue
        nc = np.asarray(nv['origin']) + np.asarray(nv['u']) * nv['extent_m'][0] / 2 + np.asarray(nv['v']) * nv['extent_m'][1] / 2
        s = (shared, -float(np.linalg.norm(oc - nc)))
        if score is None or s > score:
            best, score = nid, s
    return best


def self_check(model, sheet, views):
    """Map sample points of every region through the published formula and cast the ray into the model:
    the first surface hit must belong to the region's part. Samples include points near region boundaries."""
    checked = bad = 0
    for vj, v in views:
        O, U, V, N = (to_native(vj[k]) for k in ('origin', 'u', 'v', 'normal'))
        ex, ey = vj['extent_m']
        tris = {p.name: p.tris for p in v.items}
        for region in vj['regions']:
            for poly in region['polygons']:
                shape = Polygon([(x * ex, y * ey) for x, y in poly[0]], [[(x * ex, y * ey) for x, y in r] for r in poly[1:]])
                samples = []
                inner = pieces(shape.buffer(-0.01))
                for g in inner:
                    samples += [tuple(p) for p in sample_points(g, 6)]
                    ring = g.exterior
                    samples += [ring.interpolate(t, normalized=True).coords[0] for t in np.linspace(0, 1, 9)[:-1]]
                if not inner:                      # a small piece: it must still be the part's own surface
                    q = shape.buffer(-0.002)
                    samples.append((q if not q.is_empty else shape).representative_point().coords[0])
                for px, py in samples:
                    P = O + px * U + py * V
                    dist = {name: ray_hit(t, P, -N) for name, t in tris.items()}
                    first = min(dist, key=dist.get)
                    checked += 1
                    # Surfaces within DEPTH_EPS of each other are flush (a joint face): either part is right.
                    if not np.isfinite(dist[first]) or dist[region['part']] > dist[first] + DEPTH_EPS:
                        bad += 1
                        if bad <= 12:
                            print(f'    {sheet["id"]}/{vj["id"]}: point in {region["part"]} hits {first}')
    if bad:
        raise SystemExit(f'{sheet["id"]}: {bad} of {checked} mapped points do not land on their part')
    return checked


def sample_points(poly, n):
    """Up to n points well inside a polygon (grid points, falling back to the representative point)."""
    inner = poly.buffer(-min(0.002, 0.2 * math.sqrt(poly.area)))
    pts = []
    if n > 1 and not inner.is_empty:
        x0, y0, x1, y1 = inner.bounds
        k = int(math.ceil(math.sqrt(n))) + 1
        for gx in np.linspace(x0, x1, k + 2)[1:-1]:
            for gy in np.linspace(y0, y1, k + 2)[1:-1]:
                if inner.contains(shapely.Point(gx, gy)):
                    pts.append((gx, gy))
    pts = pts[:n] or [(lambda q: (q.x, q.y))((inner if not inner.is_empty else poly).representative_point())]
    return np.array(pts)


_WORK = {}


def _project(i):
    v = _WORK['views'][i]
    items = project_view(_WORK['model'], v)
    for p in items + v.overlay_items:
        p._tree = None                      # rebuilt on demand; not sent back to the parent
    return items, v.overlay_items


def build(bridge, cache=None):
    base = ROOT / 'data' / 'bridges' / bridge
    if bridge != 'beechwood':
        raise SystemExit('Only the Beechwood pilot sheet set is defined so far.')
    glb = base / 'model.glb'
    manifest = json.loads((base / 'model_manifest.json').read_text())
    DATUM.update(datum(manifest))
    model = load_glb(glb)
    sha = hashlib.sha256(glb.read_bytes()).hexdigest()
    out_dir = base / 'inspection'
    previous = json.loads((out_dir / 'sheets.json').read_text()) if (out_dir / 'sheets.json').is_file() else {}
    published = {vw['id']: {**vw, 'sheet_id': s['id']} for s in previous.get('sheets', []) for vw in s['views']}
    retired = dict(previous.get('retired_views', {}))
    sheets, bent_x = beechwood_views(model, manifest)
    info = beechwood_parts(manifest)
    kept = 0
    every = [v for sheet in sheets for row in sheet['rows'] for v in row]
    for v in every:
        missing = [n for n in v.parts + v.refs + v.overlays if n not in model]
        if missing:
            raise SystemExit(f'{v.id}: parts not in model.glb: {missing}')
        if v.id in retired:
            raise SystemExit(f'{v.id}: this id was retired; use a new one')
    # Views are projected in parallel; the workers inherit the model and the view list when they are forked.
    # --cache reuses the projection of every view whose definition and model are unchanged (for working on the
    # drawing code); the others are projected again.
    keys = {v.id: hashlib.sha256(repr((sha, v.U, v.V, v.N, v.parts, v.refs, v.clip, v.overlays, v.edges, v.key)).encode()).hexdigest()
            for v in every}
    stored = {}
    if cache and Path(cache).is_file():
        with open(cache, 'rb') as f:
            stored = pickle.load(f)
    todo = []
    for i, v in enumerate(every):
        if keys[v.id] in stored:
            v.items, v.overlay_items = stored[keys[v.id]]
        else:
            todo.append(i)
    if todo:
        _WORK.update(model=model, views=every)
        if 'fork' in multiprocessing.get_all_start_methods():
            pool = multiprocessing.get_context('fork').Pool(min(len(todo), os.cpu_count() or 1))
            results = pool.imap(_project, todo)
        else:                                       # Windows: no fork, one view after another
            pool, results = None, map(_project, todo)
        for i, (items, overlays) in zip(todo, results):
            every[i].items, every[i].overlay_items = items, overlays
            print(f'  projected {every[i].id}', flush=True)
        if pool:
            pool.close()
            pool.join()
    if cache:
        with open(cache, 'wb') as f:
            pickle.dump({keys[v.id]: (v.items, v.overlay_items) for v in every}, f)
        print(f'  {len(every) - len(todo)} projections reused from {cache}')
    for sheet in sheets:
        for row in sheet['rows']:
            for v in row:
                if not v.key and not any(p.inspect for p in v.items):
                    raise SystemExit(f'{v.id}: no inspectable surface in view')
                allb = np.array([p.sil.bounds for p in v.items])
                v.range = (allb[:, 0].min(), allb[:, 1].min(), allb[:, 2].max(), allb[:, 3].max())
                v.extent = (v.range[2] - v.range[0], v.range[3] - v.range[1])
                v.nmax = max(float(p.depth.max()) for p in v.items) + 0.05
                if not v.key and keep_published_frame(v, published.get(v.id)):
                    kept += 1
                print(f'  {v.id}: {len(v.items)} parts, {v.extent[0]:.2f} x {v.extent[1]:.2f} m', flush=True)
    # One scale for every sheet of a group (the beam sheets), the smallest any of them needs.
    groups = {}
    for sheet in sheets:
        if sheet.get('scale_group'):
            groups.setdefault(sheet['scale_group'], []).append(pick_scale(sheet)[0])
    out_dir.mkdir(exist_ok=True)
    for old in out_dir.glob('*.svg'):
        old.unlink()
    catalogue = []
    for index, sheet in enumerate(sheets, 1):
        forced = max(groups[sheet['scale_group']]) if sheet.get('scale_group') else None
        text, denom, views = draw_sheet(sheet, info, index, len(sheets), bent_x, manifest, forced)
        (out_dir / f'{sheet["id"]}.svg').write_text(text)
        pub = [view_json(v, pl) for v, pl in views]
        checked = self_check(model, sheet, list(zip(pub, [v for v, _ in views])))
        catalogue.append({'id': sheet['id'], 'title': sheet['title'], 'subtitle': sheet['subtitle'], 'svg': f'{sheet["id"]}.svg',
                          'scale': f'1:{denom}', 'views': pub})
        print(f'{sheet["id"]}: 1:{denom}, {len(views)} views, {checked} mapped points land on their part', flush=True)
    new_views = {vw['id']: {**vw, 'sheet_id': s['id']} for s in catalogue for vw in s['views']}
    for old_id, old in published.items():
        if old_id in new_views:
            continue
        retired[old_id] = {k: old[k] for k in ('origin', 'u', 'v', 'normal', 'extent_m', 'parts', 'sheet_id')}
        retired[old_id]['label'] = old.get('label', '')
        retired[old_id]['replaced_by'] = match_replacement(old_id, old, new_views)
        retired[old_id]['retired'] = dt.date.today().isoformat()
    for rid, r in retired.items():
        if r.get('replaced_by') and r['replaced_by'] not in new_views:
            r['replaced_by'] = match_replacement(rid, r, new_views)
    used = {p for s in catalogue for v in s['views'] for p in v['parts']}
    elements = []
    for code, (name, unit) in ELEMENTS.items():
        members = [pid for pid, r in info.items() if r['element'] == code and pid in used]
        total = sum(info[pid]['quantity'] for pid in members)
        elements.append({'code': code, 'name': name, 'unit': unit, 'total': round(total, 1), 'parts': members})
    result = {
        'bridge': bridge, 'title': 'Beechwood Road over Little Blue River',
        'structure_id': manifest['structure_id'], 'designation': manifest['designation'],
        'source': {'glb': 'model.glb', 'sha256': sha, 'revision': manifest.get('revision')},
        'canvas_mm': list(CANVAS),
        'datum': datum(manifest),
        'mapping': 'P = origin + u * extent_m[0] * u_axis + v * extent_m[1] * v_axis (glTF world, metres; u, v in 0..1 '
                   'from the top-left of the view, v down). The surface is the first hit of a ray from P along -normal.',
        'naming': 'Plan names: Beam Line No. 1 is the west beam (model girder 4); Wing A/B at End Bent 1 (east/west), '
                  'Wing C/D at End Bent 4 (west/east); Pour A pile cap, Pour B integral end-bent concrete.',
        'elements_standard': 'AASHTO Manual for Bridge Element Inspection, 2nd edition (2019)',
        'elements': elements,
        'parts': {pid: r for pid, r in info.items() if pid in used},
        'sheets': catalogue,
        'retired_views': dict(sorted(retired.items())),
    }
    (out_dir / 'sheets.json').write_text(json.dumps(result, indent=1) + '\n')
    print(f'Wrote {len(catalogue)} sheets to {out_dir.relative_to(ROOT)}; {kept} views kept their published frames, '
          f'{len(retired)} retired views mapped to their replacements')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('bridge')
    parser.add_argument('--cache', help='file to keep the projected views in, reused while the model and the view '
                        'definitions are unchanged (for working on the drawing code)')
    args = parser.parse_args()
    build(args.bridge, args.cache)

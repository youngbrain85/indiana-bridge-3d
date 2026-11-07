"""Build inspection sheets (2D defect-mapping drawings) from a bridge's source model.

    python scripts/build_inspection_sheets.py beechwood

Each sheet is an A3 landscape SVG made of true orthographic views of model.glb. sheets.json ties every view back
to the model. A sheet point (u, v) inside a view (both 0..1, v pointing down the sheet) is the world point

    P = origin + u * extent_m[0] * U + v * extent_m[1] * V          (glTF world axes, metres)

and the inspected surface is the first surface hit by a ray from P along -normal. The origin lies on the face of
the view nearest the viewer, so the ray starts in front of every surface in the view. Each view also stores the
visible region of every inspectable part (hidden parts already subtracted), so the inspection app can name the
element under a sketch without loading the 3D model.

Requires numpy and shapely (requirements-sheets.txt). The output is committed; rebuild it whenever model.glb or the
sheet set changes. test_manager.py checks that sheets.json names the current model.glb.
"""
import argparse
import datetime as dt
import hashlib
import json
import math
import struct
import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import shapely
import shapely.affinity
from shapely.geometry import LineString, MultiLineString, MultiPolygon, Polygon, box
from shapely.ops import linemerge

ROOT = Path(__file__).resolve().parents[1]
FT = 0.3048
CANVAS = (420.0, 297.0)                 # A3 landscape, mm
MAIN = (12.0, 14.0, 396.0, 244.0)       # x, y, w, h of the drawing area above the title block
DENOMS = (20, 25, 30, 40, 50, 60, 75, 100, 125, 150, 175, 200, 250, 300, 400, 500)
FEATURE_DEG = 22.0                      # crease angle drawn as an edge line


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
    return np.concatenate(keep) if keep else np.zeros((0, 3, 3))


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
    ends: tuple = None             # direction words at the left and right ends, e.g. ('SOUTH', 'NORTH')
    bents: bool = False            # draw bent centre lines (views whose U is +-X)
    overlays: list = field(default_factory=list)  # thin surface items (pavement markings): drawn, never occlude


class Projected:
    def __init__(self, name, tris, view):
        self.name = name
        U, V, N = (np.asarray(a, float) for a in (view.U, view.V, view.N))
        self.uv = np.stack([tris @ U, tris @ V], axis=-1)
        self.depth = tris @ N
        e1, e2 = tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0]
        normals = np.cross(e1, e2)
        area2 = np.linalg.norm(normals, axis=1)
        self.tris = tris
        self.front = (normals @ N) > 1e-9 * np.maximum(area2, 1e-12)
        self.normals = normals / np.maximum(area2, 1e-15)[:, None]
        d1, d2 = self.uv[:, 1] - self.uv[:, 0], self.uv[:, 2] - self.uv[:, 0]
        flat = np.abs(d1[:, 0] * d2[:, 1] - d1[:, 1] * d2[:, 0]) > 1e-10
        rings = np.concatenate([self.uv[flat], self.uv[flat][:, :1]], axis=1)
        polys = shapely.polygons(rings)
        self.sil = shapely.union_all(polys, grid_size=1e-4).buffer(0) if len(polys) else Polygon()
        self.bounds = self.sil.bounds if not self.sil.is_empty else None
        self.visible = self.sil

    def depth_at(self, pts):
        """Nearest-to-viewer depth of this part under each 2D point (-inf where it has no surface)."""
        pts = np.atleast_2d(pts)
        a, b, c = self.uv[:, 0], self.uv[:, 1], self.uv[:, 2]
        out = np.full(len(pts), -np.inf)
        for k, p in enumerate(pts):
            v0, v1, v2 = b - a, c - a, p - a
            den = v0[:, 0] * v1[:, 1] - v1[:, 0] * v0[:, 1]
            ok = np.abs(den) > 1e-14
            den = np.where(ok, den, 1.0)
            s = (v2[:, 0] * v1[:, 1] - v1[:, 0] * v2[:, 1]) / den
            t = (v0[:, 0] * v2[:, 1] - v2[:, 0] * v0[:, 1]) / den
            hit = ok & (s >= -1e-7) & (t >= -1e-7) & (s + t <= 1 + 1e-7)
            if hit.any():
                d = self.depth[hit]
                out[k] = np.max(d[:, 0] + s[hit] * (d[:, 1] - d[:, 0]) + t[hit] * (d[:, 2] - d[:, 0]))
        return out

    def crease_lines(self):
        """Visible crease and open-boundary edges, projected to 2D."""
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
        uv_vert = np.zeros((len(welded), 2))
        uv_vert[ids] = self.uv.reshape(-1, 2)
        segs = uv_vert[uniq[pick]]
        long = np.linalg.norm(segs[:, 1] - segs[:, 0], axis=1) > 0.01
        return segs[long]


def pieces(geom):
    if geom.is_empty:
        return []
    if isinstance(geom, Polygon):
        return [geom]
    return [g for g in getattr(geom, 'geoms', []) if isinstance(g, Polygon)]


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


def b_ahead(a, b, pts):
    da, db = a.depth_at(pts), b.depth_at(pts)
    return (db > da + 1e-4) & np.isfinite(db)


def resolve_occlusion(items):
    """Subtract from each part the parts in front of it (decided per overlap piece by sampled depth)."""
    for a in items:
        cover = []
        for b in items:
            if b is a or a.bounds is None or b.bounds is None:
                continue
            if b.bounds[0] > a.bounds[2] or b.bounds[2] < a.bounds[0] or b.bounds[1] > a.bounds[3] or b.bounds[3] < a.bounds[1]:
                continue
            for piece in pieces(a.sil.intersection(b.sil)):
                if piece.area < 1e-6:
                    continue
                ahead = b_ahead(a, b, sample_points(piece, 9))
                if ahead.all():
                    cover.append(piece)
                elif ahead.any():
                    # Partly in front (a slab end over a backwall, grooves): decide cell by cell.
                    # Cells follow the piece's own proportions, so thin bands (a sloping slab edge) resolve too.
                    x0, y0, x1, y1 = piece.bounds
                    sx, sy = (x1 - x0) / 32, (y1 - y0) / 32
                    gx, gy = np.meshgrid(x0 + sx * (np.arange(32) + 0.5), y0 + sy * (np.arange(32) + 0.5))
                    centres = np.stack([gx.ravel(), gy.ravel()], axis=1)
                    inside = shapely.contains_xy(piece, centres[:, 0], centres[:, 1])
                    ahead = np.zeros(len(centres), bool)
                    ahead[inside] = b_ahead(a, b, centres[inside])
                    cells = [box(cx - sx / 2, cy - sy / 2, cx + sx / 2, cy + sy / 2) for cx, cy in centres[ahead]]
                    if cells:
                        cover.append(shapely.union_all(cells).intersection(piece))
        if cover:
            a.visible = a.sil.difference(shapely.union_all(cover, grid_size=1e-4)).buffer(0)


def project_view(model, view):
    items, inspect = [], set(view.parts)
    for name in view.parts + view.refs:
        tris = model[name]
        if view.clip:
            tris = clip_triangles(tris, *view.clip)
        if len(tris):
            proj = Projected(name, tris, view)
            if not proj.sil.is_empty:
                proj.inspect = name in inspect
                items.append(proj)
    resolve_occlusion(items)
    for p in items:
        p.visible = clean(p.visible)
    overlays = []
    for name in view.overlays:
        tris = clip_triangles(model[name], *view.clip) if view.clip else model[name]
        if len(tris):
            overlays.append(Projected(name, tris, view))
    view.overlay_items = [o for o in overlays if not o.sil.is_empty]
    return items


def clean(geom):
    """Drop slivers and pinholes left by unioning thousands of small triangles."""
    out = []
    for poly in pieces(geom):
        if poly.area < 0.002:
            continue
        holes = [r for r in poly.interiors if Polygon(r).area >= 0.02]
        out.append(Polygon(poly.exterior, holes))
    return shapely.union_all(out) if out else Polygon()


# ---------------------------------------------------------------- Beechwood sheet set
def beechwood_views(model, manifest):
    parts = {p['id']: p for p in manifest['parts']}
    X, Y, Z = (1, 0, 0), (0, 1, 0), (0, 0, 1)
    nX, nY, nZ = (-1, 0, 0), (0, -1, 0), (0, 0, -1)
    bent_x = {i: sum(parts[f'b{i}_cap']['bounds_m'][k][0] for k in (0, 1)) / 2 for i in (1, 2, 3, 4)}
    spans = [('A', bent_x[1], bent_x[2]), ('B', bent_x[2], bent_x[3]), ('C', bent_x[3], bent_x[4])]
    deck = parts['deck']['bounds_m']
    x0, x1 = deck[0][0], deck[1][0]
    cuts = [x0] + [bent_x[2], bent_x[3]] + [x1]
    sheets = []

    # Deck top and underside: one band per span, cut at the bent centre lines.
    top = []
    for k, (span, _, _) in enumerate(spans):
        lo, hi = cuts[k], cuts[k + 1]
        top.append(View(f'DK1-{span}', f'SPAN {span} · DECK TOP · LOOKING DOWN', X, nY, Z, ['deck'], ['rail_L', 'rail_R'],
                        clip=((lo, -9, -50), (hi, 9, 50)), edges=False, ends=('SOUTH', 'NORTH'), bents=True,
                        overlays=['marking_center', 'marking_edge_L', 'marking_edge_R']))
    sheets.append(dict(id='DK-1', title='Deck top surface', subtitle='Wearing surface of the concrete deck, spans A to C',
                       rows=[[v] for v in top]))
    under = []
    for k, (span, _, _) in enumerate(spans):
        lo, hi = cuts[k], cuts[k + 1]
        girders = [f'girder_{span}{i}' for i in (1, 2, 3, 4)]
        refs = ['b1_cap', 'b1_integral', 'b2_cap', 'b2_diaphragm', 'b3_cap', 'b3_diaphragm', 'b4_cap', 'b4_integral',
                'rail_L', 'rail_R'] + [n for n in model if n.startswith(('steel_diaphragm', 'clip_'))]
        under.append(View(f'DK2-{span}', f'SPAN {span} · DECK UNDERSIDE AND GIRDER SOFFITS · LOOKING UP', X, Y, nZ,
                          girders + ['deck'], refs, clip=((lo, -9, -50), (hi, 9, 50)), ends=('SOUTH', 'NORTH'), bents=True))
    sheets.append(dict(id='DK-2', title='Deck underside', subtitle='Deck soffit between girders and girder bottom flanges',
                       rows=[[v] for v in under]))

    # Girder elevations: both faces of every girder of a span, each girder alone (inspected from its own bay).
    for span, _, _ in spans:
        rows = []
        for i in (1, 2, 3, 4):
            g = f'girder_{span}{i}'
            side = 'EXTERIOR' if i in (1, 4) else 'INTERIOR'
            east = 'FASCIA' if i == 1 else side
            west = 'FASCIA' if i == 4 else side
            rows.append([View(f'G{span}{i}-E', f'GIRDER {span}{i} · EAST FACE ({east}) · LOOKING WEST', X, nZ, nY, [g],
                              ends=('SOUTH', 'NORTH'), bents=True)])
            rows.append([View(f'G{span}{i}-W', f'GIRDER {span}{i} · WEST FACE ({west}) · LOOKING EAST', nX, nZ, Y, [g],
                              ends=('NORTH', 'SOUTH'), bents=True)])
        sheets.append(dict(id=f'GR-{span}', title=f'Span {span} girders', subtitle='Both web faces of girders 1 to 4 '
                           '(girder 1 east, girder 4 west)', rows=rows))

    # Interior bents: south and north faces of cap, columns, debris wall and the bearings on that side.
    for b in (2, 3):
        cx = bent_x[b]
        inspect = [f'b{b}_cap', f'b{b}_column_L', f'b{b}_column_R', f'b{b}_wall']
        south = [f'b{b}_bearing_{i}_-1' for i in (1, 2, 3, 4)]
        north = [f'b{b}_bearing_{i}_+1' for i in (1, 2, 3, 4)]
        refs = [f'b{b}_diaphragm', f'b{b}_pad_filler'] + [n for n in model if n.startswith('girder_')] + ['deck', 'rail_L', 'rail_R']
        clip = ((cx - 1.6, -9, -0.5), (cx + 1.6, 9, 50))
        sheets.append(dict(id=f'BT-{b}', title=f'Bent {b}', subtitle='Pier cap, columns, debris wall and elastomeric bearings',
                           rows=[[View(f'B{b}-S', f'BENT {b} · SOUTH FACE · LOOKING NORTH', nY, nZ, nX, south + inspect, refs,
                                       clip=clip, ends=('WEST', 'EAST')),
                                  View(f'B{b}-N', f'BENT {b} · NORTH FACE · LOOKING SOUTH', Y, nZ, X, north + inspect, refs,
                                       clip=clip, ends=('EAST', 'WEST'))]]))

    # End bents: the face towards the span, and the outside face of each wing return.
    for b, face in ((1, X), (4, nX)):
        cx = bent_x[b]
        inspect = [f'b{b}_integral', f'b{b}_cap', f'b{b}_wing_L', f'b{b}_wing_R']
        refs = [n for n in model if n.startswith('girder_')] + ['deck', 'rail_L', 'rail_R'] + \
               [n for n in model if n.startswith(f'b{b}_bearing_') or n.startswith('sole_')]
        lo, hi = (cx - 3.6, cx + 2.0) if b == 1 else (cx - 2.0, cx + 3.6)
        if b == 1:
            front = View('E1-F', 'END BENT 1 · FACE TOWARDS SPAN A · LOOKING SOUTH', Y, nZ, X, inspect, refs,
                         clip=((lo, -9, 0), (hi, 9, 50)), ends=('EAST', 'WEST'))
            wl = View('E1-WL', 'WING L · OUTSIDE FACE · LOOKING EAST', nX, nZ, Y, [f'b{b}_wing_L'], clip=((lo, 4.9, 0), (hi, 9, 50)), ends=('NORTH', 'SOUTH'))
            wr = View('E1-WR', 'WING R · OUTSIDE FACE · LOOKING WEST', X, nZ, nY, [f'b{b}_wing_R'], clip=((lo, -9, 0), (hi, -4.9, 50)), ends=('SOUTH', 'NORTH'))
        else:
            front = View('E4-F', 'END BENT 4 · FACE TOWARDS SPAN C · LOOKING NORTH', nY, nZ, nX, inspect, refs,
                         clip=((lo, -9, 0), (hi, 9, 50)), ends=('WEST', 'EAST'))
            wl = View('E4-WL', 'WING L · OUTSIDE FACE · LOOKING EAST', nX, nZ, Y, [f'b{b}_wing_L'], clip=((lo, 4.9, 0), (hi, 9, 50)), ends=('NORTH', 'SOUTH'))
            wr = View('E4-WR', 'WING R · OUTSIDE FACE · LOOKING WEST', X, nZ, nY, [f'b{b}_wing_R'], clip=((lo, -9, 0), (hi, -4.9, 50)), ends=('SOUTH', 'NORTH'))
        sheets.append(dict(id=f'EB-{b}', title=f'End bent {b}', subtitle='Integral end diaphragm, pile cap and wing returns',
                           rows=[[front], [wl, wr]]))

    # Barriers: both faces of both barriers, each in two bands split at mid-length.
    mid = (x0 + x1) / 2
    rows = []
    for rail, side in (('rail_L', 'LEFT (WEST)'), ('rail_R', 'RIGHT (EAST)')):
        outer = Y if rail == 'rail_L' else nY
        inner = nY if rail == 'rail_L' else Y
        for face, n, tag in (('OUTSIDE', outer, 'O'), ('TRAFFIC', inner, 'T')):
            for half, (lo, hi) in (('1', (x0 - 1, mid)), ('2', (mid, x1 + 1))):
                looking_west = n == nY
                u = X if looking_west else nX
                ends = ('SOUTH', 'NORTH') if looking_west else ('NORTH', 'SOUTH')
                label = f'{side} BARRIER · {face} FACE · {"SOUTH" if half == "1" else "NORTH"} HALF · LOOKING {"WEST" if looking_west else "EAST"}'
                rows.append([View(f'R{rail[-1]}{tag}-{half}', label, u, nZ, n, [rail], clip=((lo, -9, -50), (hi, 9, 50)),
                                  ends=ends, bents=True)])
    sheets.append(dict(id='RL-1', title='Barriers', subtitle='Outside and traffic faces of both FC barriers', rows=rows))
    return sheets, bent_x


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
    """Inspectable parts: NBE element, measuring axis (native) and element quantity."""
    out = {}
    for p in manifest['parts']:
        pid, (lo, hi) = p['id'], p['bounds_m']
        span = [hi[i] - lo[i] for i in range(3)]
        rec = None
        if pid == 'deck':
            rec = dict(element=12, label='Deck', quantity=manifest['deck_length_ft'] * manifest['deck_width_ft'])
        elif pid.startswith('girder_'):
            rec = dict(element=109, label=f'Girder {pid[-2:]}', axis=(1, 0, 0), quantity=p['dimensions']['length_ft'])
        elif pid.endswith('_cap') and pid[:2] in ('b2', 'b3'):
            rec = dict(element=234, label=f'Bent {pid[1]} cap', axis=(0, 1, 0), quantity=p['dimensions']['length_ft'])
        elif '_column_' in pid:
            rec = dict(element=205, label=f'Bent {pid[1]} column {pid[-1]}', quantity=1)
        elif pid.endswith('_wall'):
            rec = dict(element=210, label=f'Bent {pid[1]} debris wall', axis=(0, 1, 0), quantity=span[1] / FT)
        elif pid in ('b1_cap', 'b4_cap'):
            rec = dict(element=215, label=f'End bent {pid[1]} pile cap', axis=(0, 1, 0), quantity=span[1] / FT)
        elif pid in ('b1_integral', 'b4_integral'):
            rec = dict(element=215, label=f'End bent {pid[1]} end diaphragm', axis=(0, 1, 0), quantity=0)
        elif '_wing_' in pid:
            rec = dict(element=215, label=f'End bent {pid[1]} wing {pid[-1]}', axis=(1, 0, 0), quantity=span[0] / FT)
        elif 'elastomeric' in p['name']:
            rec = dict(element=310, label=f'Bent {pid[1]} bearing {pid.split("_")[2]}{"S" if pid.endswith("-1") else "N"}', quantity=1)
        elif pid.startswith('rail_'):
            rec = dict(element=331, label=f'Barrier {"left" if pid.endswith("L") else "right"}', axis=(1, 0, 0), quantity=span[0] / FT)
        if rec:
            rec['name'] = p['name']
            if 'axis' in rec:
                rec['axis'] = to_glb(rec['axis'])
            rec['quantity'] = round(rec['quantity'], 1)
            out[pid] = rec
    return out


def datum(manifest):
    """Station and elevation of the model origin, from the manifest's native-axes note."""
    import re
    note = manifest['native_axes']
    sta = re.search(r'station (\d+)\+(\d+(?:\.\d+)?) at X\s*=\s*0', note)
    el = re.search(r'elevation (\d+(?:\.\d+)?) ft at Z\s*=\s*0', note)
    if not sta or not el:
        raise SystemExit('native_axes does not give the station and elevation of the origin')
    return {'station_ft_at_origin': int(sta[1]) * 100 + float(sta[2]), 'elevation_ft_at_origin': float(el[1]),
            'note': 'glTF X = native X (station increasing), glTF Y = elevation, glTF Z = -native Y (left of centre line is -Z)'}


def station(x_m, manifest):
    """Station label for a native X (station 104+96 at X = 0, from the manifest's native axes note)."""
    ft = datum(manifest)['station_ft_at_origin'] + x_m / FT
    return f'STA {int(ft // 100)}+{ft % 100:05.2f}'


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
    if geom.is_empty:
        return []
    if isinstance(geom, LineString):
        return [geom]
    return [g for g in getattr(geom, 'geoms', []) if isinstance(g, LineString)]


def layout(sheet, scale_mm):
    """Row-by-row placement at one scale. Returns ([(view, x, y, w, h)], height)."""
    label, gap, hgap = 6.0, 5.0, 14.0
    placed, y = [], 0.0
    for row in sheet['rows']:
        widths = [(v.extent[0] * scale_mm, v.extent[1] * scale_mm) for v in row]
        total = sum(w for w, _ in widths) + hgap * (len(row) - 1)
        x = (MAIN[2] - total) / 2
        height = max(h for _, h in widths)
        for v, (w, h) in zip(row, widths):
            placed.append((v, x, y + label, w, h))
            x += w + hgap
        y += label + height + gap
    return placed, y - gap


def pick_scale(sheet):
    for d in DENOMS:
        placed, height = layout(sheet, 1000.0 / d)
        width = max(x + w for _, x, _, w, _ in placed) - min(x for _, x, _, _, _ in placed)
        margin = 52 if any(v.bents for row in sheet['rows'] for v in row) else 0   # bent labels beside the views
        if height <= MAIN[3] and width + margin <= MAIN[2]:
            return d, placed, height
    raise SystemExit(f'{sheet["id"]}: does not fit at 1:{DENOMS[-1]}')


def draw_sheet(sheet, info, index, count, bent_x, manifest):
    denom, placed, height = pick_scale(sheet)
    s = 1000.0 / denom
    top = MAIN[1] + (MAIN[3] - height) / 2
    svg = Svg()
    svg.add('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 297" width="420mm" height="297mm">')
    svg.add('<style>text{font-family:"IBM Plex Sans",Arial,Helvetica,sans-serif;fill:#1d2124}'
            '.t{font-size:2.2px}.s{font-size:1.8px;fill:#5a5f63}.h{font-size:2.6px;font-weight:600;letter-spacing:.06px}'
            '.big{font-size:4.6px;font-weight:600}.mid{font-size:3px;font-weight:600}.lbl{font-size:1.9px;fill:#3d454b;font-weight:600}'
            '.o{fill:none;stroke:#1d2124;stroke-width:.3;stroke-linejoin:round;stroke-linecap:round}'
            '.e{fill:none;stroke:#1d2124;stroke-width:.15;stroke-linecap:round}'
            '.r{fill:none;stroke:#a3abb0;stroke-width:.15;stroke-linejoin:round}'
            '.m{fill:#e3e7ea;stroke:#a3abb0;stroke-width:.1}.f{fill:#f2f5f6;stroke:none}.rf{fill:#fafbfb;stroke:none}'
            '.c{fill:none;stroke:#6b7378;stroke-width:.15;stroke-dasharray:4 1 .6 1}'
            '.k{fill:none;stroke:#1d2124;stroke-width:.25}.thin{fill:none;stroke:#1d2124;stroke-width:.15}</style>')
    svg.add('<rect width="420" height="297" fill="#fff"/>')
    svg.add('<rect x="5" y="5" width="410" height="287" class="k"/>')
    views = []
    for v, x, y, w, h in placed:
        x += MAIN[0]
        y += top
        umin, vmin = v.range[0], v.range[1]
        T = lambda g, x=x, y=y, umin=umin, vmin=vmin: shapely.affinity.affine_transform(g, [s, 0, 0, s, x - umin * s, y - vmin * s])
        svg.text(x, y - 2.0, v.label, 'h')
        if v.ends:
            svg.text(x + w, y - 2.0, f'{v.ends[0]} ← · → {v.ends[1]}', 's', 'end')
        svg.add(f'<g id="view-{v.id}">')
        refs = [p for p in v.items if not p.inspect]
        mine = [p for p in v.items if p.inspect]
        for p in refs:
            for poly in pieces(T(p.visible.simplify(0.002))):
                svg.add(f'<path class="rf" d="{poly_d(poly)}"/>')
        for p in mine:
            for poly in pieces(T(p.visible.simplify(0.002))):
                svg.add(f'<path class="f" d="{poly_d(poly)}"/>')
        for o in getattr(v, 'overlay_items', []):
            for poly in pieces(T(o.sil.simplify(0.002))):
                svg.add(f'<path class="m" d="{poly_d(poly)}"/>')
        for group, cls in ((refs, 'r'), (mine, 'o')):
            for p in group:
                outline = []
                for poly in pieces(p.visible):
                    outline += lines_of(poly.exterior) + [LineString(r.coords) for r in poly.interiors]
                if outline:
                    svg.add(f'<path class="{cls}" d="{path_d(lines_of(T(MultiLineString(outline).simplify(0.002))))}"/>')
                if v.edges and cls == 'o':
                    segs = p.crease_lines()
                    if len(segs):
                        ml = linemerge(MultiLineString([s_.tolist() for s_ in segs]))
                        vis = ml.intersection(p.visible.buffer(0.004))
                        d = path_d(lines_of(T(vis.simplify(0.002))))
                        if d:
                            svg.add(f'<path class="e" d="{d}"/>')
        svg.add('</g>')
        # Bent centre lines (and stations) on views whose horizontal axis runs along the bridge.
        if v.bents:
            ux = v.U[0]
            for b, bx in bent_x.items():
                u = bx * ux
                if umin - 1e-6 <= u <= umin + v.extent[0] + 1e-6:
                    sx = x + (u - umin) * s
                    svg.add(f'<path class="c" d="M{sx:.2f},{y - 0.6:.2f}V{y + h + 0.8:.2f}"/>')
                    at = (u - umin) / v.extent[0]
                    if at < 0.04 or at > 0.96:   # at an end of the view: label beside it
                        left = at < 0.5
                        tx, anchor = (min(sx, x) - 1.4, 'end') if left else (max(sx, x + w) + 1.4, 'start')
                        svg.text(tx, y + h / 2 - 0.4, f'BENT {b}', 'lbl', anchor)
                        svg.text(tx, y + h / 2 + 2.0, station(bx, manifest), 's', anchor)
                    else:                        # inside the view: label in the title row, on the line
                        svg.text(sx, y - 2.0, f'BENT {b} · {station(bx, manifest)}', 's', 'middle')
        # Element labels on inspectable regions (only where the text fits inside the region).
        for p in mine if len(mine) > 1 else []:
            big = max(pieces(p.visible), key=lambda g: g.area, default=None)
            if big is None:
                continue
            label = info[p.name]['label']
            short = label.replace('Girder ', 'G-').replace(f'Bent {p.name[1]} ', '').replace(f'End bent {p.name[1]} ', '')
            for text in (label, short):
                tw, th = len(text) * 1.15 + 1, 2.6
                inner = big.buffer(-0.5 * th / s)
                pt = inner.representative_point() if not inner.is_empty else None
                if pt is None:
                    continue
                cx, cy = pt.x, pt.y
                if big.contains(box(cx - tw / 2 / s, cy - th / 2 / s, cx + tw / 2 / s, cy + th / 2 / s)):
                    svg.text(x + (cx - umin) * s, y + (cy - vmin) * s + 0.7, text.upper(), 'lbl', 'middle')
                    break
        views.append((v, [x / CANVAS[0], y / CANVAS[1], w / CANVAS[0], h / CANVAS[1]]))

    # Title block.
    y0 = 262.0
    svg.add(f'<path class="k" d="M5,{y0}H415M120,{y0}V292M250,{y0}V292M300,{y0}V292M355,{y0}V292"/>')
    svg.text(9, y0 + 7, 'BEECHWOOD ROAD BRIDGE OVER LITTLE BLUE RIVER', 'mid')
    svg.text(9, y0 + 12.5, f'Structure {manifest["structure_id"]} · Des. {manifest["designation"]} · Crawford County, Indiana', 's')
    svg.text(9, y0 + 17, f'{len(manifest["spans_ft"])} spans {"-".join(str(s_) for s_ in manifest["spans_ft"])} ft · '
             f'prestressed concrete bulb-tee girders · {manifest["deck_width_ft"]} ft deck', 's')
    svg.text(9, y0 + 25.5, 'INSPECTION SHEET · DRAW DEFECTS ON THE SHADED SURFACES', 's')
    svg.text(124, y0 + 7, sheet['title'].upper(), 'mid')
    svg.text(124, y0 + 12.5, sheet['subtitle'], 's')
    svg.text(124, y0 + 17, 'True orthographic views of the 3D model. Shaded: inspectable element surface.', 's')
    svg.text(124, y0 + 21, 'Grey outline: context, not inspected on this sheet. Dash-dot: bent centre line.', 's')
    svg.text(124, y0 + 25.5, 'Units: feet and inches (AASHTO MBEI element quantities).', 's')
    svg.text(254, y0 + 6, 'SCALE', 's')
    svg.text(254, y0 + 13, f'1:{denom}', 'mid')
    metres = next(m for m in (20, 10, 5, 2, 1) if m * s <= 42)
    bar = metres * s
    for i in range(5):
        svg.add(f'<rect x="{254 + i * bar / 5:.2f}" y="{y0 + 17}" width="{bar / 5:.2f}" height="1.2" '
                f'fill="{"#1d2124" if i % 2 == 0 else "#fff"}" stroke="#1d2124" stroke-width=".1"/>')
    svg.text(254, y0 + 22.5, '0', 's')
    svg.text(254 + bar, y0 + 22.5, f'{metres} m', 's', 'middle')
    svg.text(254 + bar * 0.5, y0 + 26.5, f'{metres} m ≈ {metres / FT:.1f} ft', 's', 'middle')
    svg.text(304, y0 + 6, 'MODEL', 's')
    svg.text(304, y0 + 11, f'model.glb · rev {manifest.get("revision", "")}', 't')
    svg.text(304, y0 + 15.5, f'SHA-256 {info["_sha"][:12]}…', 's')
    svg.text(304, y0 + 20, 'X station, Y up (glTF), metres', 's')
    svg.text(304, y0 + 24.5, f'Generated {dt.date.today().isoformat()}', 's')
    svg.text(359, y0 + 6, 'SHEET', 's')
    svg.text(385, y0 + 17, sheet['id'], 'big', 'middle')
    svg.text(385, y0 + 25, f'{index} of {count}', 's', 'middle')
    svg.add('</svg>')
    return '\n'.join(svg.out), denom, views


def region_json(p, v):
    """Visible region of a part in view-normalised coordinates (u, v in 0..1)."""
    out = []
    umin, vmin = v.range[0], v.range[1]
    for poly in pieces(p.visible.simplify(0.004)):
        if poly.area < 2e-4:
            continue
        rings = []
        for ring in [poly.exterior, *poly.interiors]:
            rings.append([[round((x - umin) / v.extent[0], 5), round((y - vmin) / v.extent[1], 5)] for x, y in list(ring.coords)[:-1]])
        out.append(rings)
    return out


def view_json(v, placement):
    U, V, N = (np.asarray(a, float) for a in (v.U, v.V, v.N))
    umin, vmin = v.range[0], v.range[1]
    origin = U * umin + V * vmin + N * v.nmax
    return {'id': v.id, 'label': v.label.title().replace(' · ', ' · '),
            'origin': to_glb(origin), 'u': to_glb(U), 'v': to_glb(V), 'normal': to_glb(N),
            'extent_m': [round(v.extent[0], 4), round(v.extent[1], 4)],
            'placement': [round(c, 6) for c in placement],
            'parts': [p.name for p in v.items if p.inspect],
            'regions': [{'part': p.name, 'polygons': region_json(p, v)} for p in v.items if p.inspect and region_json(p, v)]}


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


def self_check(model, sheet, views):
    """Map sample points of every region through the published formula and cast the ray into the model:
    the first surface hit must belong to the region's part."""
    native = lambda g: np.array([g[0], -g[2], g[1]], float)
    checked = bad = 0
    for vj, v in views:
        O, U, V, N = (native(vj[k]) for k in ('origin', 'u', 'v', 'normal'))
        ex, ey = vj['extent_m']
        tris = {p.name: p.tris for p in v.items}
        for region in vj['regions']:
            for poly in region['polygons'][:4]:
                # Region rings are normalised; sample in metres so the inset is the same on both axes.
                shape = Polygon([(x * ex, y * ey) for x, y in poly[0]], [[(x * ex, y * ey) for x, y in r] for r in poly[1:]])
                for g in pieces(shape.buffer(-0.01)):
                    for px, py in sample_points(g, 6):
                        P = O + px * U + py * V
                        dist = {name: ray_hit(t, P, -N) for name, t in tris.items()}
                        first = min(dist, key=dist.get)
                        checked += 1
                        # Coplanar neighbours (a bearing flush with its filler) tie; either answer is the same surface.
                        if not np.isfinite(dist[first]) or dist[region['part']] > dist[first] + 1e-4:
                            bad += 1
                            print(f'    {sheet["id"]}/{vj["id"]}: point in {region["part"]} hits {first}')
    if bad:
        raise SystemExit(f'{sheet["id"]}: {bad} of {checked} mapped points do not land on their part')
    return checked


def build(bridge):
    base = ROOT / 'data' / 'bridges' / bridge
    if bridge != 'beechwood':
        raise SystemExit('Only the Beechwood pilot sheet set is defined so far.')
    glb = base / 'model.glb'
    manifest = json.loads((base / 'model_manifest.json').read_text())
    model = load_glb(glb)
    sha = hashlib.sha256(glb.read_bytes()).hexdigest()
    sheets, bent_x = beechwood_views(model, manifest)
    info = beechwood_parts(manifest)
    info['_sha'] = sha
    for sheet in sheets:
        for row in sheet['rows']:
            for v in row:
                missing = [n for n in v.parts + v.refs if n not in model]
                if missing:
                    raise SystemExit(f'{v.id}: parts not in model.glb: {missing}')
                v.items = project_view(model, v)
                mine = [p for p in v.items if p.inspect]
                if not mine:
                    raise SystemExit(f'{v.id}: no inspectable surface in view')
                allb = np.array([p.sil.bounds for p in v.items])
                v.range = (allb[:, 0].min(), allb[:, 1].min(), allb[:, 2].max(), allb[:, 3].max())
                v.extent = (v.range[2] - v.range[0], v.range[3] - v.range[1])
                v.nmax = max(float(p.depth.max()) for p in v.items) + 0.05
                print(f'  {v.id}: {len(v.items)} parts, {v.extent[0]:.2f} x {v.extent[1]:.2f} m', flush=True)
    out_dir = base / 'inspection'
    out_dir.mkdir(exist_ok=True)
    catalogue = []
    for index, sheet in enumerate(sheets, 1):
        text, denom, views = draw_sheet(sheet, info, index, len(sheets), bent_x, manifest)
        (out_dir / f'{sheet["id"]}.svg').write_text(text)
        published = [view_json(v, pl) for v, pl in views]
        checked = self_check(model, sheet, list(zip(published, [v for v, _ in views])))
        catalogue.append({'id': sheet['id'], 'title': sheet['title'], 'subtitle': sheet['subtitle'], 'svg': f'{sheet["id"]}.svg',
                          'scale': f'1:{denom}', 'views': published})
        print(f'{sheet["id"]}: 1:{denom}, {len(views)} views, {checked} mapped points land on their part', flush=True)
    used = {p for s in catalogue for v in s['views'] for p in v['parts']}
    del info['_sha']
    elements = []
    for code, (name, unit) in ELEMENTS.items():
        members = [pid for pid, r in info.items() if r['element'] == code and pid in used]
        total = sum(info[pid]['quantity'] for pid in members)
        elements.append({'code': code, 'name': name, 'unit': unit, 'total': round(total, 1), 'parts': members})
    result = {
        'bridge': bridge, 'title': 'Beechwood Road Bridge over Little Blue River',
        'structure_id': manifest['structure_id'], 'designation': manifest['designation'],
        'source': {'glb': 'model.glb', 'sha256': sha, 'revision': manifest.get('revision')},
        'canvas_mm': list(CANVAS),
        'datum': datum(manifest),
        'mapping': 'P = origin + u * extent_m[0] * u_axis + v * extent_m[1] * v_axis (glTF world, metres; u, v in 0..1 '
                   'from the top-left of the view, v down). The surface is the first hit of a ray from P along -normal.',
        'elements_standard': 'AASHTO Manual for Bridge Element Inspection, 2nd edition (2019)',
        'elements': elements,
        'parts': {pid: r for pid, r in info.items() if pid in used},
        'sheets': catalogue,
    }
    (out_dir / 'sheets.json').write_text(json.dumps(result, indent=1) + '\n')
    print(f'Wrote {len(catalogue)} sheets to {out_dir.relative_to(ROOT)}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('bridge')
    build(parser.parse_args().bridge)

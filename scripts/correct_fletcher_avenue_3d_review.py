"""Fourth round (3D review) of Fletcher Avenue over I-65 / I-70 (fletcher-avenue): the cross frames must not float.
Runs after scripts/correct_fletcher_avenue_review_3.py. Unrelated GLB buffers are kept; new accessors, meshes and
nodes are appended.

    python scripts/correct_fletcher_avenue_3d_review.py [--dry-run]

Source: drawings.pdf (local review binder; S8 = PDF 99, S9 = PDF 100, S10 = PDF 101, S11 = PDF 102 of the 1971
I-65-3(106)111 plans). Native axes: X increasing station, Y transverse (+Y south, girder 1 at +Y), Z up;
U = X + tan(skew) Y along each girder line.

Finding S01 of the 3D review: the 91 cross-frame envelopes (two X-diagonal bars per bay, generator) end 0.306 m from
the web centre lines with nothing between them and the girders (measured 0.0764 m from crossframe_3_2 to girder_0_2).

What the sheets give. S8 framing plan: cross frames XF-1 (typ.) square to the girders in 13 rows. S11 cross frame
XF-1: L 5 x 5 x 3/8 top and bottom chords, L 3 x 3 x 3/8 diagonals, 4 ft 0 in deep (typ.), 3 in min. below the top
flange; the members are welded (1/4 in fillet, typ.) to 3/8 in gusset plates at the four corners, and each gusset is
bolted to a connection plate on the girder web ("Conn. PL (typ.)", drawn from flange to flange) with four bolts,
"3 spa. @ 3 in = 9 in (typ.)"; 7/8 in high-strength bolts (S8 structural steel notes).

What is modelled (new parts crossframe_gusset_{row}_{bay}, one per cross frame, four plates each):
- 3/8 in gusset plates (S11) in the frame plane, square to the girders, at the four ends of the modelled diagonals.
- At the web each plate is 12 in high: the 9 in bolt line of XF-1 plus 1 1/2 in end distances, the end distance of
  the S9/S10 bolted splice plates with the same 7/8 in bolts (the gusset also scales to about 12 in on XF-1). Its top
  (bottom) is level with the highest (lowest) point of the diagonal's end.
- Each plate holds the last 6 in of its diagonal (lap scaled from XF-1, 5 1/2 to 7 1/2 in at the four drawn corners;
  not dimensioned) and is the convex hull of that lap and the 12 in web edge. The diagonal sits in a notch cut to its
  own faces (contact, no overlap). Where a bottom lateral gusset (S11, 5 in above the bottom flange) crosses a bottom
  corner plate, the plate is cut to the lateral gusset's faces (contact).
- The connection plate is drawn but not sized (S8-S11): its width scales to about 4 1/2 in on XF-1 and its thickness
  cannot be scaled. It is not modelled; the gusset reaches the web face in its place, as the lateral gussets of
  revision 1.3 do. Bolts and welds are not modelled.
- The diagonals keep their generator envelope (0.10 m x 0.012 m bars); the XF-1 chords are not modelled. Recorded in
  known_deviations as `crossframe-xf1-envelope`.

Requires numpy, trimesh, shapely and manifold3d; reuses the helpers of the first review script.
"""
import hashlib
import json
import struct
import sys
from pathlib import Path

import manifold3d
import numpy as np
import shapely
import trimesh

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import correct_fletcher_avenue_review as R1  # noqa: E402
import correct_fletcher_avenue_review_2 as R2  # noqa: E402
import correct_fletcher_avenue_review_3 as R3  # noqa: E402

BID = 'fletcher-avenue'
BASE = ROOT / 'data/bridges' / BID
TAG_KEY = 'review_correction_3d'
TAG = 'crossframe-corner-gussets'
REVISION = '1.4-3d-review'
EXPECTED_DEVIATIONS = {'pier2-shoe-stack', 'haunch-thickness', 'ttx-face-recesses', 'retained-wing-envelopes'}

FT, IN = R1.FT, R1.IN
K, YS, TW = R1.K, R1.YS, R1.TW
ROWS, BAYS = 13, 7
GUSSET_T = 3 / 8 * IN                         # S11 XF-1: 3/8 in gusset PL (typ.)
WEB_EDGE = 9 * IN + 2 * 1.5 * IN              # S11 XF-1: 3 spa. @ 3 in = 9 in; S9/S10: 1 1/2 in end distances
LAP = 6 * IN                                  # scaled from S11 XF-1 (5 1/2 - 7 1/2 in); not dimensioned
TOUCH = 2e-5                                  # contact tolerance (float32 storage at 50 m is about 4 um)
NO_OVERLAP = 1e-9                             # m3


def frame_x(i, j):
    """X of the plane of cross frame (row i, bay j): the generator's frame station (R1.crossframe_mesh)."""
    return R1.sx(R1.CF_ROWS[i], (YS[j] + YS[j + 1]) / 2)


def web_limits(x, j):
    """Underside of the top flange and top of the bottom flange of model line j at plan X (after rounds 1-2)."""
    u = x + K * YS[j]
    top = R2.top_new(u, j)
    tf = R1.tf_new(u, j)
    return top - tf, top - tf - R1.web(u)


def girder_part(x, j):
    """Span A (girder_0_j) or Span B (girder_1_j) segment carrying plan X on model line j."""
    return f'girder_{0 if x + K * YS[j] < 0 else 1}_{j}'


def to_manifold(mesh):
    return manifold3d.Manifold(manifold3d.Mesh(np.asarray(mesh.vertices, np.float32),
                                               np.asarray(mesh.faces, np.uint32)))


def from_manifold(man):
    out = man.to_mesh()
    mesh = trimesh.Trimesh(np.asarray(out.vert_properties)[:, :3].astype(np.float64), np.asarray(out.tri_verts),
                           process=False)
    if not (mesh.is_watertight and mesh.volume > 0):
        raise ValueError('manifold result is not a closed solid')
    return mesh


def weld(mesh):
    """The plate as the GLB stores it (float32), welded the way a reader welds it (within 10 um, as
    scripts/refresh_geometry_verification.py does): the boolean can leave two vertices a few um apart where cut faces
    nearly meet. Faces that the weld collapses, or folds onto each other, are dropped; the result must be closed."""
    out = trimesh.Trimesh(np.asarray(mesh.vertices, np.float32).astype(np.float64), np.asarray(mesh.faces),
                          process=False)
    out.merge_vertices(digits_vertex=5)
    f = np.asarray(out.faces)
    f = f[(f[:, 0] != f[:, 1]) & (f[:, 1] != f[:, 2]) & (f[:, 0] != f[:, 2])]
    _, first, counts = np.unique(np.sort(f, axis=1), axis=0, return_index=True, return_counts=True)
    f = f[np.sort(first[counts == 1])]                       # a face folded onto another leaves with it
    out = trimesh.Trimesh(out.vertices, f, process=False)
    out.remove_unreferenced_vertices()
    again = out.copy()
    again.merge_vertices(digits_vertex=5)
    if not (out.is_watertight and out.is_winding_consistent and out.volume > 0 and again.is_watertight and
            len(again.vertices) == len(out.vertices)):
        raise ValueError('welded plate is not a closed solid')
    return out


def bar_end(bar, j):
    """End of a diagonal bar at model line j: its four end vertices, unit axis into the bay, top/bottom corner."""
    v = np.asarray(bar.vertices, dtype=np.float64)
    if len(v) != 8:
        raise ValueError('cross-frame bar is not a box')
    order = np.argsort(np.abs(v[:, 1] - YS[j]))
    end, far = v[order[:4]], v[order[4:]]
    axis = far.mean(axis=0) - end.mean(axis=0)
    axis /= np.linalg.norm(axis)
    if abs(axis[0]) > 1e-6:
        raise ValueError('cross-frame bar is not in its frame plane')
    return end, axis, end.mean(axis=0)[2] > far.mean(axis=0)[2]


def corner_plate(bar, j, x0):
    """3/8 in gusset at the end of `bar` on model line j: in-plane outline (y, z) and the prism x0 +- T/2, with the
    bar cut out of it."""
    end, axis, top = bar_end(bar, j)
    side = np.sign(end[:, 1].mean() - YS[j])
    face = YS[j] + side * TW / 2
    z_edge = end[:, 2].max() if top else end[:, 2].min()
    pts = [(face, z_edge), (face, z_edge - WEB_EDGE if top else z_edge + WEB_EDGE)]
    for q in end:
        pts += [(q[1], q[2]), (q[1] + LAP * axis[1], q[2] + LAP * axis[2])]
    poly = shapely.MultiPoint(pts).convex_hull
    if not (poly.is_valid and poly.area > 0) or min(side * (c[0] - face) for c in poly.exterior.coords) < -1e-12:
        raise ValueError('gusset outline crosses the web face')
    ring = np.array(shapely.geometry.polygon.orient(poly, 1).exterior.coords)[:-1]
    local = from_manifold(manifold3d.Manifold.extrude(manifold3d.CrossSection([ring]), GUSSET_T))
    v = local.vertices                                         # (y, z, t): cyclic, keeps the orientation
    prism = trimesh.Trimesh(np.c_[x0 - GUSSET_T / 2 + v[:, 2], v[:, 0], v[:, 1]], local.faces, process=False)
    if not (prism.is_watertight and prism.volume > 0):
        raise ValueError('gusset prism is not a closed solid')
    return poly, prism, to_manifold(prism) - to_manifold(bar), top, face


def overlap(a, b):
    return (to_manifold(a) ^ to_manifold(b)).volume()


def boxes_meet(a, b, pad=0.0):
    return bool((a[0] < b[1] + pad).all() and (a[1] > b[0] - pad).all())


def surface_gap(points, mesh):
    """Smallest distance from points to the surface of mesh."""
    _, dist, _ = trimesh.proximity.closest_point(mesh, points)
    return float(np.min(dist))


# ------------------------------------------------------------------------------------------ correction
def correct(base=BASE, backup=ROOT / 'data/fem_research', dry_run=False):
    mp = base / 'model_manifest.json'
    raw_manifest = mp.read_bytes()
    manifest = json.loads(raw_manifest.decode('utf-8'))
    if manifest.get(TAG_KEY) == TAG:
        print('Already corrected.')
        return None
    if manifest.get(R3.TAG_KEY) != R3.TAG or manifest.get('revision') != R3.REVISION:
        raise ValueError('run scripts/correct_fletcher_avenue_review_3.py first '
                         f'(expected revision {R3.REVISION}, found {manifest.get("revision")})')
    path = base / 'model.glb'
    original = path.read_bytes()
    before = hashlib.sha256(original).hexdigest()
    if before != manifest['review_correction_record_3']['after_glb_sha256']:
        raise ValueError('model.glb is not the output of the third review correction')
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
    added, metadata_only = [], []

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

    cache = {}

    def native(pid):
        if pid not in cache:
            prim = meshes[pid]['primitives'][0]
            v = read(prim['attributes']['POSITION']).astype(np.float64)
            f = read(prim['indices']).reshape(-1, 3)
            cache[pid] = trimesh.Trimesh(np.c_[v[:, 0], -v[:, 2], v[:, 1]], f, process=False)
        return cache[pid]

    def primitive(mesh, color):
        v = mesh.vertices
        glb = np.c_[v[:, 0], v[:, 2], -v[:, 1]].astype('<f4')
        prim = {'attributes': {'POSITION': append(glb, 'VEC3', 5126),
                               'COLOR_0': append(np.tile(color, (len(v), 1)).astype('u1'), 'VEC4', 5121)},
                'indices': append(np.asarray(mesh.faces).reshape(-1, 1).astype('<u4'), 'SCALAR', 5125), 'mode': 4}
        gltf['accessors'][prim['attributes']['COLOR_0']]['normalized'] = True
        return prim

    def add(pid, mesh, like, name, layer, pages, basis, note, dims):
        """New part: manifest entry with the fields of similar parts, mesh with extras, node in the scene."""
        if pid in parts or pid in meshes:
            raise ValueError(f'{pid}: already present')
        if not (mesh.is_watertight and mesh.volume > 0):
            raise ValueError(f'{pid}: not watertight with positive volume')
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
        cache[pid] = mesh
        added.append(pid)

    # ------------------------------------------------------------------ expected starting state
    for i in range(ROWS):
        for j in range(BAYS):
            pid = f'crossframe_{i}_{j}'
            if not R1.same_points(native(pid).vertices, R1.crossframe_mesh(i, j, R1.depth_new).vertices):
                raise ValueError(f'{pid}: generator / first-round cross frame not reproduced')
            if f'crossframe_gusset_{i}_{j}' in parts or f'crossframe_gusset_{i}_{j}' in meshes:
                raise ValueError(f'crossframe_gusset_{i}_{j}: already present')
    all_bounds = {n: native(n).bounds for n in meshes}

    # ------------------------------------------------------------------ S01: corner gussets (S8, S9/S10, S11)
    built, clear_top, clear_bottom, depth = {}, [], [], []
    for i in range(ROWS):
        for j in range(BAYS):
            frame = f'crossframe_{i}_{j}'
            x0 = frame_x(i, j)
            bars = native(frame).split(only_watertight=False)
            if len(bars) != 2:
                raise ValueError(f'{frame}: expected two diagonal bars')
            plates, met, info = [], [], []
            for g in (j, j + 1):
                ends = []
                for bar in bars:
                    poly, prism, cut, top, face = corner_plate(bar, g, x0)
                    # S11: the bottom lateral gusset at the point of lateral bracing meets this plate; cut the
                    # plate to its faces. Anything else in the way is an error.
                    pb = prism.bounds
                    for name, bb in all_bounds.items():
                        if name in (frame, girder_part(x0, g)) or not boxes_meet(pb, bb):
                            continue
                        if overlap(prism, native(name)) <= NO_OVERLAP:
                            continue
                        if not name.startswith('lateral_gusset_'):
                            raise ValueError(f'{frame}: corner gusset at girder {R1.plan_girder(g)} runs into {name}')
                        cut = cut - to_manifold(native(name))
                        met.append(name)
                    plate = weld(from_manifold(cut))
                    if len(plate.split(only_watertight=False)) != 1:
                        raise ValueError(f'{frame}: corner gusset at girder {R1.plan_girder(g)} split')
                    hi, lo = web_limits(x0, g)
                    if top:
                        clear_top.append(hi - plate.bounds[1][2])
                    else:
                        clear_bottom.append(plate.bounds[0][2] - lo)
                    end, _, _ = bar_end(bar, g)
                    ends.append(end.mean(axis=0)[2])
                    plates.append(plate)
                    info.append(dict(g=g, girder=R1.plan_girder(g), corner='top' if top else 'bottom', face=face,
                                     bar=bar, area=float(poly.area), plate=plate))
                depth.append(abs(ends[0] - ends[1]))
            mesh = trimesh.util.concatenate(plates)
            built[(i, j)] = (mesh, sorted(set(met)), info, bars)

    # ------------------------------------------------------------------ checks before writing
    bar_gap, web_gap, lateral_gap, worst = [], [], [], 0.0
    new_meshes = {f'crossframe_gusset_{i}_{j}': v[0] for (i, j), v in built.items()}
    for (i, j), (mesh, met, info, bars) in built.items():
        frame = f'crossframe_{i}_{j}'
        x0 = frame_x(i, j)
        for k in info:
            plate, bar, g = k['plate'], k['bar'], k['g']
            # diagonal seated: its faces bound the notch, nothing overlaps either diagonal
            gap = surface_gap(plate.vertices, bar)
            ov = max(overlap(plate, b) for b in bars)
            if gap > TOUCH or ov > NO_OVERLAP:
                raise ValueError(f'{frame}: diagonal not seated at girder {k["girder"]} ({gap:.2e} m, {ov:.2e} m3)')
            bar_gap.append(gap)
            worst = max(worst, ov)
            # web face: a face of the plate lies on the web face of its girder, inside the web depth
            on_web = plate.vertices[np.abs(plate.vertices[:, 1] - k['face']) < 1e-5]
            girder = native(girder_part(x0, g))
            hi, lo = web_limits(x0, g)
            if len(on_web) < 4 or not (lo < on_web[:, 2].min() and on_web[:, 2].max() < hi):
                raise ValueError(f'{frame}: gusset at girder {k["girder"]} not on the web face')
            gap = surface_gap(on_web, girder)
            ov = overlap(plate, girder)
            if gap > TOUCH or ov > NO_OVERLAP:
                raise ValueError(f'{frame}: gusset at girder {k["girder"]} off the web ({gap:.2e} m, {ov:.2e} m3)')
            web_gap.append(gap)
            worst = max(worst, ov)
        for name in met:
            gap = surface_gap(mesh.vertices, native(name))
            if gap > TOUCH:
                raise ValueError(f'{frame}: cut against {name} but not touching it')
            lateral_gap.append(gap)
        # nothing else overlaps the new plates (including the other new parts)
        for name, other in list(new_meshes.items()) + [(n, None) for n in all_bounds]:
            bb = other.bounds if other is not None else all_bounds[name]
            if name in (frame, f'crossframe_gusset_{i}_{j}') or not boxes_meet(mesh.bounds, bb):
                continue
            ov = overlap(mesh, other if other is not None else native(name))
            if ov > NO_OVERLAP:
                raise ValueError(f'{frame}: corner gussets overlap {name} ({ov:.2e} m3)')
            worst = max(worst, ov)

    # ------------------------------------------------------------------ new parts and metadata
    for (i, j), (mesh, met, info, _) in built.items():
        frame = f'crossframe_{i}_{j}'
        ga, gb = R1.plan_girder(j + 1), R1.plan_girder(j)
        lat = ''
        if met:
            nodes = ', '.join(f'{n} ({parts[n]["name"].split("| gusset at ")[1].split(",")[0]})' for n in met)
            lat = (f' The bottom plate is cut to the faces of the lateral gusset it meets ({nodes}; S11: gussets '
                   'at the point of lateral bracing 5 in above the bottom flange).')
        add(f'crossframe_gusset_{i}_{j}', mesh, frame,
            f'Cross frame row {i + 1} | bay between girders {ga} and {gb} | corner gussets', 'bracing', [99, 100, 101, 102],
            'S11 cross frame XF-1 (3/8 in corner gussets bolted to the girder connection plates, 4 bolts at 3 in); '
            'outline fitted to the modelled diagonals',
            f'Four 3/8 in gusset plates (S11 cross frame XF-1) in the frame plane, square to the girders (S8), joining '
            f'the ends of the modelled diagonals ({frame}) to the webs of girders {ga} and {gb}. At the web each is '
            '12 in high: the 9 in XF-1 bolt line (3 spa. @ 3 in) plus 1 1/2 in end distances as on the S9/S10 bolted '
            'plates; its top (bottom) is level with the end of the diagonal, which it holds over its last 6 in (lap '
            'scaled from XF-1, not dimensioned) in a notch cut to the bar faces.' + lat + ' The XF-1 connection plate '
            'welded to the web is not sized on S8-S11; the gusset reaches the web face in its place. Bolts and welds '
            'are not modelled (see known_deviations crossframe-xf1-envelope).',
            dict(thickness_m=round(GUSSET_T, 6), plate_count=len(info), web_edge_height_m=round(WEB_EDGE, 6),
                 diagonal_lap_m=round(LAP, 6), girders=[ga, gb], diagonals=frame,
                 plate_areas_m2=[round(k['area'], 4) for k in info], lateral_gussets_met=met))
        p = parts[frame]
        p['note'] = ('Source 22 ft 9 in rows (S8). Representative X-diagonal envelope of S11 cross frame XF-1; both '
                     f'diagonals end on the 3/8 in corner gussets of crossframe_gusset_{i}_{j}, which reach the girder '
                     'webs. The XF-1 L 5 x 5 x 3/8 chords, its 4 ft 0 in depth and the connection plates are not '
                     'modelled (known_deviations crossframe-xf1-envelope).' +
                     (' Diagonals extended with the corrected S10 girder depth at Pier 2.'
                      if 'Pier 2' in p['note'] else ''))
        p['basis'] = 'Source framing topology (S8) and S11 cross frame XF-1; member profiles simplified'
        meshes[frame]['extras'].update(p)
        metadata_only.append(frame)

    for d in manifest['detail_coverage']:
        if d['feature'] == 'Retained steel details':
            d['detail'] += (' Cross-frame X envelopes seated on 3/8 in corner gussets (S11 XF-1) that reach the girder '
                            'webs.')
            d['part_ids'] += added
    tops, bots = (min(clear_top), max(clear_top)), (min(clear_bottom), max(clear_bottom))
    deviation = dict(
        id='crossframe-xf1-envelope', parts='crossframe_*, crossframe_gusset_*',
        source='S8, S9, S10, S11 (PDF 99-102)',
        deviation='Each cross frame is the generator\'s representative X: two 0.10 m x 0.012 m diagonal bars whose '
                  f'ends lie 0.33 m from the web centre lines, {min(depth):.3f}-{max(depth):.3f} m apart vertically, '
                  f'their ends {tops[0] * 1000:.0f}-{tops[1] * 1000:.0f} mm below the top flange and '
                  f'{bots[0] * 1000:.0f}-{bots[1] * 1000:.0f} mm above the bottom flange. S11 cross frame XF-1 draws '
                  'L 5 x 5 x 3/8 top and bottom chords and L 3 x 3 x 3/8 diagonals with a 3/8 in plate at the '
                  'crossing, 4 ft 0 in deep (typ.), at least 3 in below the top flange; the chords are not modelled. '
                  'The 3/8 in corner gussets are modelled (crossframe_gusset_*), with an outline fitted to the '
                  'modelled diagonals: 12 in high at the web (9 in bolt line, 1 1/2 in end distances) and holding the '
                  'last 6 in of each diagonal (scaled from XF-1). XF-1 bolts each gusset to a connection plate '
                  'welded to the web ("Conn. PL (typ.)", drawn flange to flange); that plate is not modelled and the '
                  'gusset reaches the web face in its place.',
        reason='The connection plate is drawn but not sized: S11 gives neither its width (it scales to about '
               '4 1/2 in on XF-1) nor its thickness, and the S9/S10 girder elevations do not show it. The 1971 shop '
               'drawings (S8 structural steel notes) or a field measurement would settle it. The XF-1 chords, depth '
               'and member sizes are drawn; re-laying the 91 frames on them replaces the accepted frame envelope and '
               'is deferred to a generator rebuild.')
    manifest['known_deviations'].append(deviation)

    # ------------------------------------------------------------------ write
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
    n_met = sum(1 for v in built.values() for _ in v[1])
    manifest['review_correction_record_3d'] = dict(
        source_pdf_pages=[99, 100, 101, 102], printed_sheets=['S8', 'S9', 'S10', 'S11'],
        previous_revision=previous_revision,
        findings={'S01': 'Resolved. The 91 cross-frame X envelopes floated 59-85 mm from the girders (crossframe_3_2 '
                         'to girder_0_2: 76.4 mm). 91 new parts crossframe_gusset_{row}_{bay} hold 364 3/8 in corner '
                         'gussets (S11 XF-1) that seat every diagonal end (notch cut to the bar faces, largest gap '
                         f'{max(bar_gap) * 1000:.4f} mm) and lie on the web face of their girder (largest gap '
                         f'{max(web_gap) * 1000:.4f} mm); {n_met} bottom plates are cut to the lateral gusset they '
                         f'meet (largest gap {max(lateral_gap) * 1000:.4f} mm). Largest overlap with any part '
                         f'{worst:.1e} m3. Plate tops {tops[0] * 1000:.0f}-{tops[1] * 1000:.0f} mm below the top '
                         f'flange, bottoms {bots[0] * 1000:.0f}-{bots[1] * 1000:.0f} mm above the bottom flange.'},
        decisions={
            'Connection plate': 'S11 XF-1 bolts each corner gusset to a connection plate welded to the web, but no '
                                'sheet sizes it (width scales to about 4 1/2 in, thickness cannot be scaled). The '
                                'gusset reaches the web face in its place, as the revision 1.3 lateral gussets do.',
            'Gusset outline': 'Not dimensioned. 12 in at the web from the drawn bolt line (3 spa. @ 3 in = 9 in) '
                              'and the 1 1/2 in end distance of the S9/S10 bolted plates (it also scales to about '
                              '12 in on XF-1); the lap on the diagonal (6 in) is scaled from XF-1, where the '
                              'diagonals run 5 1/2 to 7 1/2 in onto the gussets. The outline is the convex hull of '
                              'the web edge and the lap of the modelled diagonal.',
            'Diagonal envelopes kept': 'The X bars are not moved or resized: the plates are fitted to them, and the '
                                       'XF-1 chords and working points are left to a generator rebuild '
                                       '(known_deviations crossframe-xf1-envelope).'},
        kept={deviation['id']: deviation['reason']},
        changed_parts=[], added_parts=added, removed_parts=[], renamed_parts={}, metadata_only_parts=metadata_only,
        before_glb_sha256=before, after_glb_sha256=hashlib.sha256(out).hexdigest())
    record = manifest['review_correction_record_3d']
    print(json.dumps({k: (v if k not in ('added_parts', 'metadata_only_parts') else f'{len(v)} parts')
                      for k, v in record.items()}, indent=1))
    if dry_run:
        print('Dry run, nothing written.')
        return out, manifest
    backup.mkdir(exist_ok=True)
    (backup / f'{BID}_before_3d_review.glb').write_bytes(original)
    (backup / f'{BID}_manifest_before_3d_review.json').write_bytes(raw_manifest)
    path.write_bytes(out)
    mp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return out, manifest


if __name__ == '__main__':
    correct(dry_run='--dry-run' in sys.argv)

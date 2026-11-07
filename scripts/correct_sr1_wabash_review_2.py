"""Second drawing-confirmed correction of SR 1 over the Wabash River (sr1-wabash), run after
correct_sr1_wabash_review.py; it preserves unrelated GLB buffers and appends new accessors.

    python scripts/correct_sr1_wabash_review.py      # first pass (tag review-2026-11-floor-ends-...)
    python scripts/correct_sr1_wabash_review_2.py    # this pass

Source: drawings.pdf (2004 B-25747 roadway reconstruction of the 1933 arches); printed sheets 6-15 are PDF pages
23-32, sheet 15-1 is PDF 33 and sheets 16-18 are PDF 34-36; PDF 9 is the 1933 arch, pier and joint sheet.
Native axes as in the first pass: X along the centre line from Pier 3, +Y = west (left of increasing station),
Z = El. - 240 m; the GLB stores (X, Z, -Y).

1. Rail pilasters (sheet 14 / PDF 31 "Typical concrete bracket at abutment and pier pilasters": 1836 from the curb
   face to the coping, against 1761 at a typical bracket; sheet 18 / PDF 36 plan-section: rail 380, rail face to
   coping 75, pilaster body 485 starting 30 inside the rail, outer body face 75 inside the coping line, which steps
   out 75 mm for 75 mm beyond each pilaster face). The coping is widened locally to |Y| 8.736 and the pilaster body
   stands at |Y| 8.176-8.661; the first pass had put it at 8.101-8.586, 75 mm too far in. The sidewalks get the
   1217 x 75 mm local coping projections (190 mm fascia, continuing the 2 % sidewalk slope); the plan chamfers at
   their ends are not modelled.
2. Rail joints (sheet 18 plan, plan-section and elevation "13 Open Joint (Typ.)", "One side only at Abutment";
   sheet 17 / PDF 35 elevation): 13 mm open joints between the rail and the pilaster on both sides of the pier
   pilasters and on the span side of the abutment pilasters. The rails stopped at the pilaster faces. The sheet-17
   152 mm end borders are measured from the pilaster face, so the joint is taken out of the border.
3. Spandrel-wall closures (sheet 18 elevation "13 Open Joint (Typ.) w/ Preformed Joint Filler in Spandrel Wall
   (One side only at Abutment)"; 1933 sheet PDF 9, pier plan and section S-S: the walls run into the pilaster with
   a 1/2 in. bituminous joint "from bottom of sidewalk slab to top Ar. Rg."). The model's spandrel walls and
   end-floor walls stopped on the skew pier and abutment faces, leaving 20 open slots of 59-176 mm between the
   wall ends and the square pilasters, from the pier or abutment top to the wall top. The walls now run on to
   13 mm from the pilaster faces (the joint; its filler is not modelled); on the wing side of the abutment
   pilasters, where there is no joint, the end-floor walls run up to the pilaster face.
4. Gas line (sheet 15 / PDF 32 section A-A, 1:30, "Gas Line to be reinstalled by others", "Anchor for Gas Line
   Hanger", pipe hanger detail). The model's 200 mm envelope at |Y| 7.400, Z 7.920 ran through all five east
   spandrel pilasters (|Y| up to 7.360) by 60 mm. The pipe hangs from the bracket soffits clear of the walls; its
   position and size are not dimensioned, so they are scaled from the 1:30 section against the 1574 and 381
   dimensions: centre 0.958 m outside the spandrel face (|Y| 8.045, 0.616 m inside the coping), 0.942 m below the
   sidewalk top at the coping (Z 8.113), diameter 350 mm. It stays on the east fascia (-Y) between the floor ends.

Deferred: the matching 13 mm joints through the sidewalks (sheet 9 plan and sheet 18 elevation) would split each
sidewalk into nine bodies, and the joint path across the coping ledge (45-degree kink in the sheet 18 plan-section)
is not dimensioned; recorded as a known deviation. The sidewalk brackets of sheets 11-14 remain deferred.

Requires numpy, trimesh, manifold3d and the first-pass script (imported for its geometry helpers).
"""
import hashlib
import json
import struct
import sys
from pathlib import Path

import manifold3d
import numpy as np
import trimesh

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import correct_sr1_wabash_review as r1  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'data/bridges/sr1-wabash'
TAG = 'review-2-2026-11-rail-pilasters-joints-wall-closures-gas-line'
REVISION_BEFORE, REVISION = '1.1-drawing-review', '1.2-drawing-review-2'

T15 = r1.T15
U = np.array([1.0, T15, 0.0])
JOINT = 0.013                               # 13 mm open joints, sheet 18
LOCAL_COPING_Y = r1.CURB_Y + 1.836          # 8.736, sheet 14 bracket at pier and abutment pilasters
POST_OUT = LOCAL_COPING_Y - 0.075           # 8.661, body face 75 mm inside the local coping (sheets 14, 18)
POST_IN = POST_OUT - 0.485                  # 8.176, 485 mm body (30 mm inside the rail face 8.206)
OLD_POST_IN, OLD_POST_OUT = r1.POST_IN, r1.RAIL_OUT       # 8.101 / 8.586 after the first pass
COPING_RUN = 0.075                          # local coping runs 75 mm past each pilaster face (sheet 18)
SUPPORT_HALF = 0.6475                       # pier / abutment faces at u = support -/+ 0.6475 (1295 mm, sheet 6)
GAS_Y, GAS_Z, GAS_R = -(r1.SPANDREL_Y + 0.958), 8.113, 0.175   # scaled from sheet 15 section A-A (1:30)
OLD_GAS = (-7.400, 7.920, 0.100)
SOURCE_PAGES = [9, 26, 27, 31, 32, 35, 36]
PRINTED_SHEETS = [9, 10, 14, 15, 17, 18]


def mf(mesh):
    return manifold3d.Manifold(manifold3d.Mesh64(vert_properties=np.array(mesh.vertices, np.float64, order='C'),
                                                 tri_verts=np.array(mesh.faces, np.uint64, order='C')))


def union(base, extras):
    """Boolean union with manifold3d; returns a trimesh with float32-representable vertices."""
    out = mf(base)
    for e in extras:
        out = out + mf(e)
    if out.status() != manifold3d.Error.NoError:
        raise ValueError(f'union failed: {out.status()}')
    m = out.to_mesh64()
    v = np.asarray(m.vert_properties)[:, :3].astype(np.float32).astype(np.float64)
    mesh = trimesh.Trimesh(vertices=v, faces=np.asarray(m.tri_verts).astype(np.int64), process=False)
    if not (mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0):
        raise ValueError('union produced an invalid solid')
    return mesh


def prism(poly, z_bottom, z_top):
    """Convex prism over the plan polygon `poly` [(x, y)], flat bottom, top z_top(y) (planar in y)."""
    pts = [(x, y, z_bottom) for x, y in poly] + [(x, y, z_top(y)) for x, y in poly]
    m = manifold3d.Manifold.hull_points(np.array(pts, dtype=np.float64)).to_mesh64()
    hull = trimesh.Trimesh(vertices=np.asarray(m.vert_properties)[:, :3],
                           faces=np.asarray(m.tri_verts).astype(np.int64), process=False)
    if not hull.is_watertight or hull.volume <= 0:
        raise ValueError('invalid closure prism')
    return hull


def correct():
    mp = BASE / 'model_manifest.json'
    manifest = json.loads(mp.read_text(encoding='utf-8'))
    if manifest.get('review_correction_2') == TAG:
        print('Already corrected.')
        return
    if manifest.get('review_correction') != r1.TAG or manifest.get('revision') != REVISION_BEFORE:
        raise ValueError('Run scripts/correct_sr1_wabash_review.py first: expected revision 1.1-drawing-review.')
    path = BASE / 'model.glb'
    original = path.read_bytes()
    length = struct.unpack_from('<I', original, 12)[0]
    gltf = json.loads(original[20:20 + length])
    binary = bytearray(original[28 + length:])
    before = hashlib.sha256(original).hexdigest()
    parts = {p['id']: p for p in manifest['parts']}
    meshes = {m['name']: m for m in gltf['meshes']}
    if any('matrix' in n or 'rotation' in n for n in gltf['nodes']):
        raise ValueError('Unexpected node transforms: this script expects baked Y-up vertices.')

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
        return trimesh.Trimesh(vertices=r1.to_native(read(prim['attributes']['POSITION']).astype(np.float64)),
                               faces=read(prim['indices']).reshape(-1, 3), process=False)

    changed = []

    def store(pid, mesh, dims, note, pages):
        if not mesh.is_watertight or not mesh.is_winding_consistent or mesh.volume <= 0:
            raise ValueError(f'{pid}: corrected mesh is not a valid solid')
        prim = meshes[pid]['primitives'][0]
        old_faces = read(prim['indices']).reshape(-1, 3)
        attributes = {'POSITION': append(r1.to_gltf(mesh.vertices).astype('<f4'), 'VEC3', 5126)}
        if len(mesh.faces) == len(old_faces) and np.array_equal(mesh.faces, old_faces):
            attributes['COLOR_0'] = prim['attributes']['COLOR_0']
        else:
            color = read(prim['attributes']['COLOR_0'])[0]
            attributes['COLOR_0'] = append(np.tile(color, (len(mesh.vertices), 1)).astype('u1'), 'VEC4', 5121)
            gltf['accessors'][attributes['COLOR_0']]['normalized'] = True
            prim['indices'] = append(mesh.faces.reshape(-1, 1).astype('<u4'), 'SCALAR', 5125)
        prim['attributes'] = attributes
        p = parts[pid]
        p['bounds_m'] = mesh.bounds.round(6).tolist()
        p['volume_m3'] = round(float(mesh.volume), 6)
        p['dimensions'].update(dims)
        p['note'] = (p.get('note', '') + ' ' + note).strip()
        p['pdf_pages'] = sorted(set(p['pdf_pages']) | set(pages))
        meshes[pid]['extras'].update(p)
        changed.append(pid)

    M = {pid: native(pid) for pid in meshes}
    pil = {(i, s): M[f'pilaster_{i}_{s}'].bounds for i in range(5) for s in (-1, 1)}

    # ---- Expected starting state (first pass applied, nothing else) ------------------------------------------
    edges = {}
    for s in (1, -1):
        e = [r1.RAIL_ENDS[s][0]]
        for i in range(5):
            cx = r1.post_x(i, s)
            e += [cx - r1.POST_HALF, cx + r1.POST_HALF]
            b = M[f'railpost_{s}_{i}'].bounds
            if not (np.allclose(sorted(np.abs(b[:, 1])), [OLD_POST_IN, OLD_POST_OUT], atol=1e-4)
                    and np.allclose(b[:, 0], [cx - r1.POST_HALF, cx + r1.POST_HALF], atol=1e-4)
                    and np.isclose(b[0, 2], r1.walk_top(cx, OLD_POST_IN), atol=1e-4)):
                raise ValueError(f'railpost_{s}_{i}: unexpected first-pass position')
        e.append(r1.RAIL_ENDS[s][1])
        edges[s] = e
        for i in range(6):
            if not np.allclose(M[f'parapet_{s}_{i}'].bounds[:, 0], e[2 * i:2 * i + 2], atol=1e-4):
                raise ValueError(f'parapet_{s}_{i}: unexpected first-pass ends')
        if not np.isclose(np.abs(M[f'walk_{s}'].bounds[:, 1]).max(), r1.COPING_Y, atol=1e-5):
            raise ValueError(f'walk_{s}: unexpected coping')
    gas = M['gas_line']
    if not (np.isclose(gas.vertices[:, 1].mean(), OLD_GAS[0], atol=1e-3)
            and np.isclose(gas.vertices[:, 2].mean(), OLD_GAS[1], atol=1e-3)
            and np.isclose(np.ptp(gas.vertices[:, 2]), 2 * OLD_GAS[2], atol=1e-3)):
        raise ValueError('gas_line: unexpected first-pass envelope')
    for s in (-1, 1):
        for i in range(4):
            u = M[f'spandrel_{i}_{s}'].vertices @ U
            if not np.allclose([u.min(), u.max()], [r1.SUPPORTS_U[i] + SUPPORT_HALF,
                                                    r1.SUPPORTS_U[i + 1] - SUPPORT_HALF], atol=1e-3):
                raise ValueError(f'spandrel_{i}_{s}: unexpected wall ends')
        for end, i in ((-1, 0), (1, 4)):
            u = M[f'endwall_{end}_{s}'].vertices @ U
            inner = u.max() if end < 0 else u.min()
            if not np.isclose(inner, r1.SUPPORTS_U[i] + end * SUPPORT_HALF, atol=1e-3):
                raise ValueError(f'endwall_{end}_{s}: unexpected inner end')

    # ---- 1. Rail pilasters 75 mm further out, on the locally widened coping -----------------------------------
    for s in (1, -1):
        for i in range(5):
            cx = r1.post_x(i, s)
            base = r1.walk_top(cx, POST_IN)
            store(f'railpost_{s}_{i}', r1.block(cx - r1.POST_HALF, cx + r1.POST_HALF, s * POST_IN, s * POST_OUT,
                                                base, base + r1.POST_HEIGHT),
                  dict(body_abs_y_m=[round(POST_IN, 3), round(POST_OUT, 3)],
                       local_coping_abs_y_m=round(LOCAL_COPING_Y, 3)),
                  'Corrected (second drawing review 2026-11): body at |Y| 8.176-8.661, 75 mm inside the locally '
                  'widened coping |Y| 8.736 (sheet 14: 1836 mm from the curb face; sheet 18 plan-section), was '
                  '8.101-8.586; reseated on the sidewalk at its inner face.',
                  [31, 36])

    for s in (1, -1):
        walk = M[f'walk_{s}']
        v = walk.vertices
        rim = np.isclose(np.abs(v[:, 1]), r1.COPING_Y, atol=1e-5)
        xs = np.unique(v[rim, 0])
        top = np.array([v[rim & (v[:, 0] == x), 2].max() for x in xs])
        bottom = np.array([v[rim & (v[:, 0] == x), 2].min() for x in xs])
        y_rim = float(np.abs(v[rim, 1]).mean())
        blocks = []
        for i in range(5):
            cx = r1.post_x(i, s)
            a, b = cx - r1.POST_HALF - COPING_RUN, cx + r1.POST_HALF + COPING_RUN
            st = np.unique(np.r_[a, xs[(xs > a) & (xs < b)], b])

            def loop(x):
                zt, zb = np.interp(x, xs, top), np.interp(x, xs, bottom)
                rise = 0.02 * (LOCAL_COPING_Y - y_rim)
                return [(s * y_rim, zt), (s * LOCAL_COPING_Y, zt + rise), (s * LOCAL_COPING_Y, zt + rise - r1.WALK_SLAB),
                        (s * y_rim, zb)]
            blocks.append(r1.loft(st, loop))
        side = 'west' if s > 0 else 'east'
        store(f'walk_{s}', union(walk, blocks),
              dict(local_coping_abs_y_m=round(LOCAL_COPING_Y, 3),
                   local_coping_length_m=round(2 * (r1.POST_HALF + COPING_RUN), 3)),
              f'Second drawing review 2026-11: coping widened locally to |Y| 8.736 under the five {side} rail '
              'pilasters, 1217 mm long (75 mm past each pilaster face), 190 mm fascia (sheets 14, 18); end chamfers '
              'and the 13 mm sidewalk joints are not modelled.',
              [31, 36])

    # ---- 2. 13 mm rail joints at the pilasters (both sides at piers, span side at abutments) -----------------
    for s in (1, -1):
        side = 'west' if s > 0 else 'east'
        e = edges[s]
        for i in range(1, 5):
            a_face, b_face = e[2 * i], e[2 * i + 1]
            a, b = a_face + JOINT, b_face - JOINT

            def rail_loop(x, s=s):
                base = r1.walk_top(x, r1.RAIL_IN)
                return [(s * (r1.RAIL_OUT - inset), base + h) for inset, h in r1.RAIL_SECTION]
            store(f'parapet_{s}_{i}', r1.loft(r1.stations(a, b), rail_loop),
                  dict(length_m=round(b - a, 4), joint_at_pilasters_m=JOINT),
                  'Second drawing review 2026-11: 13 mm open joints to the pilaster faces at both ends (sheet 18 plan '
                  'and elevation, sheet 17; one side only at the abutments, the span side).',
                  [35, 36])
            boxes, x = [], a_face
            faces_r = [(r1.RAIL_OUT - r1.RECESS_INSET, r1.RAIL_OUT - r1.STEM_INSET),
                       (r1.RAIL_IN + r1.STEM_INSET, r1.RAIL_IN + r1.RECESS_INSET)]
            for j, seg in enumerate(r1.panel_layout(b_face - a_face)):
                if j % 2 == 0:
                    x0, x1 = max(x, a), min(x + seg, b)
                    base = r1.walk_top((x0 + x1) / 2, r1.RAIL_IN)
                    for q0, q1 in faces_r:
                        boxes.append(r1.block(x0, x1, s * q0, s * q1, base + r1.RECESS_Z[0], base + r1.RECESS_Z[1]))
                x += seg
            if not np.isclose(x, b_face, atol=1e-6):
                raise ValueError('panel layout does not close')
            store(f'panels_{s}_{i}', trimesh.util.concatenate(boxes), dict(joint_at_pilasters_m=JOINT),
                  f'Second drawing review 2026-11: end borders shortened by the 13 mm rail joints; the sheet-17 152 mm '
                  f'end borders are measured from the pilaster faces ({side} rail).',
                  [35, 36])

    # ---- 3. Spandrel and end-floor walls closed to the pilasters ---------------------------------------------
    def closure(wall, at_max_u, xj):
        """Prism between the wall's skew end face and the square joint line X = xj."""
        v = wall.vertices
        u = v @ U
        sel = np.isclose(u, u.max() if at_max_u else u.min(), atol=1e-4)
        end = v[sel]
        if len(end) != 4:
            raise ValueError('unexpected wall end face')
        ys = np.unique(end[:, 1])
        xe = {y: end[end[:, 1] == y, 0].mean() for y in ys}
        zt = {y: end[end[:, 1] == y, 2].max() for y in ys}
        zb = end[:, 2].min()
        ya, yb = ys
        d = 1.0 if at_max_u else -1.0
        gap = {y: d * (xj - xe[y]) for y in ys}
        if min(gap.values()) <= -1e-9 and max(gap.values()) <= 1e-9:
            raise ValueError('joint line inside the wall')
        if min(gap.values()) > 1e-9:
            poly = [(xe[ya], ya), (xj, ya), (xj, yb), (xe[yb], yb)]
        else:  # the skew end crosses the joint line within the wall thickness: triangular closure
            yo = ya if gap[ya] > 0 else yb
            yi = yb if yo == ya else ya
            yc = yo + (yi - yo) * gap[yo] / (gap[yo] - gap[yi])
            poly = [(xe[yo], yo), (xj, yo), (xj, yc)]
        z_top = lambda y: zt[ya] + (zt[yb] - zt[ya]) * (y - ya) / (yb - ya)
        return prism(poly, zb, z_top)

    for s in (-1, 1):
        for i in range(4):
            pid = f'spandrel_{i}_{s}'
            wall = M[pid]
            start = closure(wall, False, pil[(i, s)][1, 0] + JOINT)
            finish = closure(wall, True, pil[(i + 1, s)][0, 0] - JOINT)
            new = union(wall, [start, finish])
            if not np.isclose(new.volume, wall.volume + start.volume + finish.volume, rtol=1e-6):
                raise ValueError(f'{pid}: closure overlaps the wall')
            store(pid, new, dict(joint_to_pilasters_m=JOINT),
                  'Second drawing review 2026-11: wall ends carried from the skew pier/abutment faces to 13 mm from '
                  'the spandrel pilaster faces (sheet 18 "13 Open Joint w/ Preformed Joint Filler in Spandrel Wall"; '
                  '1933 pier plan PDF 9), closing the open slots; joint filler not modelled.',
                  [9, 36])
        for end, i in ((-1, 0), (1, 4)):
            pid = f'endwall_{end}_{s}'
            m = M[pid]
            v = m.vertices.copy()
            u = v @ U
            inner = np.isclose(u, u.max() if end < 0 else u.min(), atol=1e-4)
            if inner.sum() != 4:
                raise ValueError(f'{pid}: unexpected inner end')
            xface = pil[(i, s)][0, 0] if end < 0 else pil[(i, s)][1, 0]
            v[inner, 0] = xface
            store(pid, trimesh.Trimesh(vertices=v, faces=m.faces, process=False),
                  dict(inner_end_x_m=round(float(xface), 4)),
                  'Second drawing review 2026-11: inner end carried from the skew abutment face to the spandrel '
                  'pilaster face; no joint on the wing side of the abutment pilaster (sheet 18 "One side only at '
                  'Abutment").',
                  [9, 36])

    # ---- 4. Gas line hung clear of the spandrel pilasters ---------------------------------------------------
    pipe = trimesh.creation.cylinder(radius=GAS_R, height=r1.X1 - r1.X0, sections=20)
    pipe.apply_transform(trimesh.geometry.align_vectors([0, 0, 1], [1, 0, 0]))
    pipe.apply_translation([(r1.X0 + r1.X1) / 2, GAS_Y, GAS_Z])
    store('gas_line', pipe,
          dict(scaled_diameter_m=2 * GAS_R, center_y_m=round(GAS_Y, 3), center_z_m=GAS_Z),
          'Second drawing review 2026-11: the 200 mm envelope at Y -7.400, Z 7.920 ran 60 mm into the five east '
          'spandrel pilasters. Re-hung clear of them at the position scaled from sheet 15 section A-A (1:30): centre '
          '0.958 m outside the spandrel face (Y -8.045) and 0.942 m below the sidewalk top at the coping (Z 8.113), '
          'diameter 350 mm. Not dimensioned on the plans; hangers not modelled.',
          [32])
    parts['gas_line']['dimensions'].pop('assumed_diameter_m', None)
    meshes['gas_line']['extras']['dimensions'].pop('assumed_diameter_m', None)
    if 'radius' in meshes['gas_line']['extras']:  # primitive metadata from the original build
        meshes['gas_line']['extras']['radius'] = GAS_R

    # ---- Write ------------------------------------------------------------------------------------------------
    while len(binary) % 4:
        binary.append(0)
    gltf['buffers'][0]['byteLength'] = len(binary)
    encoded = json.dumps(gltf, ensure_ascii=True, separators=(',', ':')).encode()
    encoded += b' ' * ((-len(encoded)) % 4)
    out = (struct.pack('<III', 0x46546c67, 2, 28 + len(encoded) + len(binary)) +
           struct.pack('<II', len(encoded), 0x4e4f534a) + encoded + struct.pack('<II', len(binary), 0x004e4942) + binary)
    backup = ROOT / 'data/fem_research'
    backup.mkdir(exist_ok=True)
    (backup / 'sr1-wabash_before_review_correction_2.glb').write_bytes(original)
    (backup / 'sr1-wabash_manifest_before_review_correction_2.json').write_bytes(mp.read_bytes())
    path.write_bytes(out)

    for item in manifest.get('detail_coverage', []):
        if item.get('feature') == 'Architectural parapets':
            item['detail'] = ('915 mm rails with the sheet-18 section (380 mm cap and base, 290 mm stem, 19 mm recessed '
                              'panels in the sheet-17 layout), 13 mm open joints to the pier pilasters and to the span '
                              'side of the abutment pilasters, and 960 mm pilasters centred on the support lines at the '
                              'arch-ring face, 75 mm inside the locally widened coping. Rail end flare, wing-end '
                              'pilasters, pilaster caps and the sidewalk joints are omitted. Separate pedestrian-bridge '
                              'sheets 40-50 were excluded.')
        elif item.get('feature') == 'Four concrete arches':
            item['detail'] = ('Four whole arch barrels, spandrel walls closed to 13 mm joints at the spandrel '
                              'pilasters, and hidden fill envelopes. Exact original multi-radius curve and spring haunch '
                              'thickness remain unresolved.')
            item['sources'] = sorted(set(item['sources']) | {'Primary PDF p.36'})
    manifest['review_correction_2'] = TAG
    manifest['revision'] = REVISION
    manifest['review_correction_2_record'] = dict(
        source_pdf_pages=SOURCE_PAGES, printed_sheets=PRINTED_SHEETS,
        corrections={
            'rail_pilasters': 'Body |Y| 8.176-8.661 (was 8.101-8.586), 75 mm inside a coping widened locally to |Y| '
                              '8.736 over 1217 mm (sheet 14: 1836 mm from the curb face; sheet 18 plan-section)',
            'rail_joints': '13 mm open joints between rails and pilasters, both sides at piers, span side at abutments '
                           '(sheets 17, 18); end panel borders shortened accordingly',
            'wall_closures': 'Spandrel walls carried to 13 mm from the spandrel pilaster faces and end-floor walls to '
                             'the abutment pilaster faces, closing 20 open slots of 59-176 mm (sheet 18; 1933 PDF 9)',
            'gas_line': 'Re-hung clear of the east spandrel pilasters (was 60 mm inside them): centre Y -8.045, Z 8.113, '
                        'diameter 350 mm, scaled from sheet 15 section A-A (1:30); not dimensioned'},
        deferred={'sidewalk_joints': '13 mm open joints through the sidewalks at the pilaster faces (sheets 9, 18)',
                  'sidewalk_brackets': 'Unchanged from the first pass'},
        changed_parts=changed,
        before_glb_sha256=before, after_glb_sha256=hashlib.sha256(out).hexdigest())
    deviations = [d for d in manifest.get('known_deviations', []) if d.get('id') != 'sidewalk-joints-not-modelled']
    deviations.append(dict(
        id='sidewalk-joints-not-modelled', parts='walk_-1, walk_1',
        source='sheets 9, 18 (PDF 26, 36)',
        deviation='The 13 mm open joints through the sidewalks in line with the rail joints (both sides of the pier '
                  'pilasters, span side of the abutment pilasters) are not cut; each sidewalk is one continuous body. '
                  'The coping projections at the pilasters omit their plan chamfers.',
        reason='Cutting them splits each sidewalk into nine bodies and the joint path across the coping ledge is not '
               'dimensioned; deferred from the second 2026-11 drawing review.'))
    manifest['known_deviations'] = deviations
    mp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in manifest['review_correction_2_record'].items()
                      if k not in ('changed_parts', 'corrections', 'deferred')}))
    print(f'{len(changed)} parts changed')


if __name__ == '__main__':
    correct()

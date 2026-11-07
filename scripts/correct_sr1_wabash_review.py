"""One-time, drawing-confirmed correction of SR 1 over the Wabash River (sr1-wabash), preserving unrelated GLB buffers.

    python scripts/correct_sr1_wabash_review.py

Source: drawings.pdf (2004 B-25747 roadway reconstruction of the 1933 arches); printed sheets 6-15 are PDF pages
23-32, sheet 15-1 is PDF 33 and sheets 16-18 are PDF 34-36.
Native axes: X along the structure centre line from Pier 3 (Sta. 2+014.728), Y to the left of increasing station,
Z = El. - 240 m (interior springline El. 244.715 at Z 4.715). This GLB stores its vertices already turned to glTF
Y-up, (X, Z, -Y); the script converts both ways.

1. Floor ends (sheets 9-10, PDF 26-27, plan of sidewalk and deck reinforcement): the roadway slab ends square to the
   centre line, 53 156 mm before and 55 328 mm after the Pier 3 centre line (108 484 mm overall). The model's deck
   ended on two skew lines at u = X + tan15 Y = -/+54.242 (up to 2.93 m off at the gutters). Both sidewalks, the
   gas line and the four end-floor retaining-wall envelopes (whose length the model ties to the floor limit) end at
   the same square floor ends.
2. Roadway slab (sheet 7 / PDF 24 and sheet 15 / PDF 32, section A-A): "New 300 Slab", top at the centre line
   "Original P.G. + 49", 2 % crossfall. Original profile (sheet 6 / PDF 23): 0.00 % grade at El. 248.829 after a
   30.480 m vertical curve from -3.10 %, P.I. Sta. 1+950.720, so the end of the curve is at Sta. 1+965.960
   (X -48.768) and the first 4.388 m of the floor rise up to 10 mm. The model had a 200 mm slab on a flat El. 248.829.
3. Orientation (sheet 6 / PDF 23 north arrow and plan; 2026 reference sheet 11 survey control, sheet 13 "Ex. Gas Line
   on East Fascia"): stations increase to the north and the left (+Y) side of the model is west. Section A-A (looking
   up-station) puts Phase II and the plain fascia on the left and Phase I with the reinstalled gas line on the right.
   The sidewalk names were swapped (walk_1 = +Y was "East") and the gas line hung on the west fascia. The names are
   swapped in the manifest; the gas line moves to Y = -7.400 (its height and assumed 200 mm envelope are unchanged).
4. Abutment faces (sheet 6 / PDF 23): Face Abut. No. 1 Sta. 1+968.894 and No. 5 Sta. 2+060.563, i.e. the arch
   springing faces u = -/+45.8345 of the 21 946 + 1 295 chain. The abutment envelopes were centred like piers and
   stood 0.5715 m into the end openings; their span faces are moved back to the springing.
5. Sidewalks and curb (sheets 7, 14, 15 / PDF 24, 31, 32, revised 4-6-04): 280 mm curb above the gutter, sidewalk
   sloping 2 % down toward the roadway, 190 mm slab at the fascia, 1 574 mm cantilever beyond the 381 mm spandrel
   wall. The model's sidewalks fell 2 % outward on a 228 mm step and floated 38 mm above the gutter. Each sidewalk
   is rebuilt with the dimensioned top and fascia; between the curb face and the spandrel face the curb unit is
   carried down onto the model's existing spandrel-wall top (sheets 11, 14, 15 show the curb and bracket concrete
   cast onto the cut spandrel walls along the whole span).
6. Railing (sheets 17-18 / PDF 35-36, sheets 9-10): typical rail section 915 mm high, 380 mm base (180 mm face,
   25 mm chamfer) and cap (125 mm face, 25 mm top chamfer), 290 mm stem, 19 mm recessed panels 310 mm high starting
   125 mm above the stem base; outer face 75 mm inside the coping, so faces at |Y| 8.206 / 8.586 (the model had a
   37.5 mm setback and a plain 380 mm block). Panel layout between pilasters (sheet 17): 152 | 2400 | 305 | 2095 |
   305 | 2095 | 152+152 | 2084 | 305 | 2084 | 305 | 2084 | 152+152 | 2095 | 305 | 2095 | 305 | 2400 | 152.
   Pilasters (1067 x 485 mm, 960 mm high, outer face 75 mm inside the coping) are centred on the pier and abutment
   centre lines at the face of the arch ring, |Y| 7.131 (sheet 17 "C Pier No. 2 or No. 4 @ Face of Arch Ring",
   closing with the sheet 9-10 sidewalk dimensions within 1 mm); the model had centred them on the rail line,
   0.349 m off along X, and 90 mm too far out. The rails end at the floor end on the west side at Abutment 1 and on
   the east side at Abutment 5, and 3 823 mm inside it at the other two corners (sheets 9-10). All rail parts sit on
   the corrected sidewalk top. Plan flare, wing-end pilasters and the 45 mm pilaster cap projection stay omitted.
7. Arch rings (sheet 15 / PDF 32 and sheet 9 plan): 14 262 mm out to out of arch ring against 14 174 mm out to out of
   spandrel wall, so each barrel face projects 44 mm beyond the spandrel face; the barrels were flush. They are
   widened to |Y| 7.131 along the skew, keeping u and Z.

Deferred: the concrete sidewalk brackets of sheets 11-14 (10 typical per span and side, plus pier, abutment and end
brackets) need new components with their own part ids; they are recorded as a known deviation.

Requires numpy, trimesh and manifold3d.
"""
import hashlib
import json
import struct
from pathlib import Path

import manifold3d
import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'data/bridges/sr1-wabash'
TAG = 'review-2026-11-floor-ends-300mm-slab-orientation-rails'

T15 = np.tan(np.radians(15.0))
OLD_HALF = (355 + 11 / 12) * 0.3048 / 2   # old skew floor limit u = +/-54.2417
X0, X1 = -53.156, 55.328                  # square floor ends, sheets 9-10
X_EVC, VC_LENGTH = 1965.960 - 2014.728, 30.480
G_TANGENT = 248.829 + 0.049 - 240.0       # original P.G. + 49 mm, Z datum El. 240
CURB_Y, SPANDREL_Y, COPING_Y = 6.900, 7.087, 8.661
RING_Y = 7.131                            # 14 262 mm out to out of arch ring
CURB, WALK_SLAB = 0.280, 0.190
DECK_SLAB = 0.300
SUPPORTS_U = [-46.482, -23.241, 0.0, 23.241, 46.482]  # pier/abutment pilaster centre lines (u at the ring face)
ABUT_FACE_U = 45.8345
OLD_ABUT_FACE_U = 45.263
RAIL_IN, RAIL_OUT = COPING_Y - 0.075 - 0.380, COPING_Y - 0.075     # 8.206 / 8.586
POST_IN = RAIL_OUT - 0.485                # 8.101
POST_HALF, POST_HEIGHT = 1.067 / 2, 0.960
# Rail ends: west (+Y) rail from the Abutment 1 floor end to 3 823 mm short of the Abutment 5 floor end; east rail
# the other way round (sheets 9-10 sidewalk dimensions).
RAIL_ENDS = {1: (X0, X1 - 3.823), -1: (X0 + 3.823, X1)}
# Sheet 18 typical rail section, (inset from the outer rail face, height above the rail base); the recess band
# 0.330-0.640 is cut 19 mm deep along the whole rail and closed again by the panel borders (the panels_* parts).
RAIL_SECTION = [(0.000, 0.000), (0.000, 0.180), (0.045, 0.205), (0.045, 0.330), (0.064, 0.330), (0.064, 0.640),
                (0.045, 0.640), (0.045, 0.765), (0.000, 0.765), (0.000, 0.890), (0.025, 0.915), (0.355, 0.915),
                (0.380, 0.890), (0.380, 0.765), (0.335, 0.765), (0.335, 0.640), (0.316, 0.640), (0.316, 0.330),
                (0.335, 0.330), (0.335, 0.205), (0.380, 0.180), (0.380, 0.000)]
RECESS_Z = (0.330, 0.640)
STEM_INSET, RECESS_INSET = 0.045, 0.064
# Sheet 17 panel layout between pilaster faces: border, panel, border, ... (metres).
SPAN_LAYOUT = [0.152, 2.400, 0.305, 2.095, 0.305, 2.095, 0.304, 2.084, 0.305, 2.084, 0.305, 2.084, 0.304, 2.095,
               0.305, 2.095, 0.305, 2.400, 0.152]
GAS_Y, GAS_Z, GAS_R = -7.400, 7.920, 0.100
SOURCE_PAGES = [23, 24, 26, 27, 28, 31, 32, 35, 36]
PRINTED_SHEETS = [6, 7, 9, 10, 11, 14, 15, 17, 18]


def grade(x):
    """Top of the roadway slab at the centre line: 0 % tangent plus the 30.48 m vertical curve before X -48.768."""
    return G_TANGENT + 0.031 * np.maximum(X_EVC - np.asarray(x, dtype=float), 0.0) ** 2 / (2 * VC_LENGTH)


def walk_top(x, r):
    """Sidewalk top at |Y| = r: 280 mm above the gutter at the curb face, rising 2 % toward the coping."""
    return grade(x) - 0.02 * CURB_Y + CURB + 0.02 * (r - CURB_Y)


def seat(r):
    """The model's existing spandrel-wall / end-wall top envelope (old flat surface El. 248.829 less 200 mm)."""
    return 8.629 - 0.02 * r


def stations(a, b, step=0.6):
    """X stations from a to b, at most `step` apart, including the end of the vertical curve when inside."""
    xs = np.linspace(a, b, max(2, int(np.ceil((b - a) / step)) + 1))
    if a < X_EVC < b:
        xs = np.unique(np.r_[xs, X_EVC])
    return xs


def loft(xs, loop):
    """Closed solid through the (y, z) loops loop(x) at the X stations; caps triangulated with manifold3d."""
    loops = [np.asarray(loop(float(x)), dtype=np.float64) for x in xs]
    k = len(loops[0])
    vertices = np.vstack([np.c_[np.full(k, x), lp] for x, lp in zip(xs, loops)])
    faces = []
    for s in range(len(xs) - 1):
        a, b = s * k, (s + 1) * k
        for i in range(k):
            j = (i + 1) % k
            faces += [(a + i, a + j, b + j), (a + i, b + j, b + i)]
    sides = np.array(faces)
    for flip in (False, True):
        caps = []
        for s, reverse in ((0, True), (len(xs) - 1, False)):
            lp = loops[s]
            ccw = np.sum(lp[:, 0] * np.roll(lp[:, 1], -1) - np.roll(lp[:, 0], -1) * lp[:, 1]) > 0
            order = np.arange(k) if ccw else np.arange(k)[::-1]
            tri = order[np.asarray(manifold3d.triangulate([lp[order]]))]
            if reverse != flip:
                tri = tri[:, ::-1]
            caps.append(tri + s * k)
        mesh = trimesh.Trimesh(vertices=vertices, faces=np.vstack([sides] + caps), process=False)
        if mesh.is_winding_consistent and mesh.is_watertight:
            break
    if not (mesh.is_winding_consistent and mesh.is_watertight):
        raise ValueError('invalid loft')
    if mesh.volume < 0:
        mesh.invert()
    return mesh


def block(x0, x1, y0, y1, z0, z1):
    y0, y1 = sorted((y0, y1))
    m = trimesh.creation.box(extents=[x1 - x0, y1 - y0, z1 - z0])
    m.apply_translation([(x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2])
    return m


def to_gltf(v):
    return np.c_[v[:, 0], v[:, 2], -v[:, 1]]


def to_native(v):
    return np.c_[v[:, 0], -v[:, 2], v[:, 1]]


def post_x(i, s):
    return SUPPORTS_U[i] - T15 * s * RING_Y


def panel_layout(length):
    """Sheet 17 layout for a 22.174 m bay; elsewhere equal panels of at most 2.4 m with 152 / 305 mm borders."""
    if abs(length - 22.174) < 2e-3:
        return SPAN_LAYOUT
    n = max(1, int(np.ceil((length - 0.304 + 0.305) / (2.400 + 0.305))))
    panel = (length - 0.304 - 0.305 * (n - 1)) / n
    out = [0.152]
    for j in range(n):
        out += [panel, 0.305 if j < n - 1 else 0.152]
    return out


def correct():
    mp = BASE / 'model_manifest.json'
    manifest = json.loads(mp.read_text(encoding='utf-8'))
    if manifest.get('review_correction') == TAG:
        print('Already corrected.')
        return
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
        return trimesh.Trimesh(vertices=to_native(read(prim['attributes']['POSITION']).astype(np.float64)),
                               faces=read(prim['indices']).reshape(-1, 3), process=False)

    changed = []

    def store(pid, mesh, dims, note, pages, name=None, basis=None):
        if not mesh.is_watertight or mesh.volume <= 0:
            raise ValueError(f'{pid}: corrected mesh is not a valid solid')
        prim = meshes[pid]['primitives'][0]
        old_faces = read(prim['indices']).reshape(-1, 3)
        attributes = {'POSITION': append(to_gltf(mesh.vertices).astype('<f4'), 'VEC3', 5126)}
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
        if name:
            p['name'] = name
        if basis:
            p['basis'] = basis
        meshes[pid]['extras'].update(p)
        changed.append(pid)

    # ---- Expected original state ----------------------------------------------------------------------------
    deck = native('deck')
    if not (np.allclose(deck.bounds, [[-56.090549, -6.9, 8.491], [56.090549, 6.9, 8.829]], atol=1e-4)
            and parts['deck']['dimensions'].get('thickness_m') == 0.2):
        raise ValueError('deck: unexpected original 200 mm skew-ended slab')
    for s, name in ((1, 'East sidewalk and cantilever'), (-1, 'West sidewalk and cantilever')):
        m = native(f'walk_{s}')
        r = np.abs(m.vertices[:, 1])
        if parts[f'walk_{s}']['name'] != name or not np.isclose(m.vertices[np.isclose(r, CURB_Y), 2].max(), 8.919,
                                                                   atol=1e-4):
            raise ValueError(f'walk_{s}: unexpected original sidewalk')
    gas = native('gas_line')
    if not np.allclose(gas.vertices[:, 1].mean(), 7.4, atol=1e-3):
        raise ValueError('gas_line: expected on +Y')
    for i in range(4):
        if not np.allclose(np.abs(native(f'arch_{i}').vertices[:, 1]), 7.087, atol=1e-4):
            raise ValueError(f'arch_{i}: expected 14.174 m barrel')
    u0 = native('pier_0').vertices @ np.array([1.0, T15, 0.0])
    u4 = native('pier_4').vertices @ np.array([1.0, T15, 0.0])
    if not (np.isclose(u0.max(), -OLD_ABUT_FACE_U, atol=1e-3) and np.isclose(u4.min(), OLD_ABUT_FACE_U, atol=1e-3)):
        raise ValueError('pier_0 / pier_4: unexpected abutment span faces')
    for s in (1, -1):
        for i in range(6):
            m = native(f'parapet_{s}_{i}')
            if not (np.allclose(sorted(np.abs(m.bounds[:, 1])), [8.2435, 8.6235], atol=1e-4)
                    and np.isclose(m.bounds[0, 2], 8.88833, atol=1e-4)):
                raise ValueError(f'parapet_{s}_{i}: unexpected original rail')
        for i in range(5):
            m = native(f'railpost_{s}_{i}')
            cx = m.vertices[:, 0].mean()
            if not np.isclose(cx, SUPPORTS_U[i] - T15 * s * (COPING_Y - 0.2275), atol=1e-3):
                raise ValueError(f'railpost_{s}_{i}: unexpected original position')
    for end in (-1, 1):
        for s in (-1, 1):
            u = native(f'endwall_{end}_{s}').vertices @ np.array([1.0, T15, 0.0])
            if not np.isclose(np.abs(u).max(), OLD_HALF, atol=1e-3):
                raise ValueError(f'endwall_{end}_{s}: unexpected floor limit')

    # ---- F1, F2: roadway slab -----------------------------------------------------------------------------
    deck_loop = lambda x: [(-CURB_Y, grade(x) - 0.02 * CURB_Y), (0.0, grade(x)), (CURB_Y, grade(x) - 0.02 * CURB_Y),
                           (CURB_Y, grade(x) - 0.02 * CURB_Y - DECK_SLAB), (0.0, grade(x) - DECK_SLAB),
                           (-CURB_Y, grade(x) - 0.02 * CURB_Y - DECK_SLAB)]
    store('deck', loft(stations(X0, X1), deck_loop),
          dict(thickness_m=DECK_SLAB, length_m=round(X1 - X0, 3), end_x_m=[X0, X1],
               top_at_centre_line_el_m=round(G_TANGENT + 240, 3), crossfall_pct=2),
          'Corrected (drawing review 2026-11): 300 mm slab, top at the centre line original P.G. + 49 mm '
          '(El. 248.878, rising to 248.888 at the Abutment 1 end on the 30.48 m vertical curve), square floor ends '
          '53.156 m before and 55.328 m after the Pier 3 centre line, sheets 6, 7, 9, 10, 15.',
          [23, 24, 26, 27, 32], name='2004 roadway slab | 300 mm',
          basis='Dimensioned roadway cross-section and square floor ends, sheets 7, 9, 10 and 15')

    # ---- F4, F6, F1: sidewalks ----------------------------------------------------------------------------
    for s in (1, -1):
        def walk_loop(x, s=s):
            pts = [(CURB_Y, seat(CURB_Y)), (CURB_Y, walk_top(x, CURB_Y)), (COPING_Y, walk_top(x, COPING_Y)),
                   (COPING_Y, walk_top(x, COPING_Y) - WALK_SLAB), (SPANDREL_Y, walk_top(x, SPANDREL_Y) - WALK_SLAB),
                   (SPANDREL_Y, seat(SPANDREL_Y))]
            return [(s * r, z) for r, z in pts]
        side = 'West' if s > 0 else 'East'
        store(f'walk_{s}', loft(stations(X0, X1), walk_loop),
              dict(curb_height_m=CURB, cross_slope_pct_toward_roadway=2, length_m=round(X1 - X0, 3)),
              f'Corrected (drawing review 2026-11): {side.lower()} side (+Y is west, sheet 6 north arrow); top 280 mm '
              'above the gutter at the curb face, falling 2 % toward the roadway; 190 mm slab at the fascia; curb '
              'unit carried down onto the spandrel-wall top; square ends at the floor ends, sheets 7, 9, 10, 14, 15. '
              'Brackets, plan flare and curb rounding are not modelled.',
              [23, 26, 27, 28, 31], name=f'{side} sidewalk and cantilever',
              basis='Dimensioned curb, sidewalk slope and fascia, sheets 7, 14 and 15; brackets and end flare omitted')

    # ---- F6, F7 (+ pilaster positions): rails ----------------------------------------------------------------
    for s in (1, -1):
        side = 'west' if s > 0 else 'east'
        edges = [RAIL_ENDS[s][0]]
        for i in range(5):
            cx = post_x(i, s)
            edges += [cx - POST_HALF, cx + POST_HALF]
        edges.append(RAIL_ENDS[s][1])
        for i in range(6):
            a, b = edges[2 * i], edges[2 * i + 1]

            def rail_loop(x, s=s):
                base = walk_top(x, RAIL_IN)
                return [(s * (RAIL_OUT - inset), base + h) for inset, h in RAIL_SECTION]
            store(f'parapet_{s}_{i}', loft(stations(a, b), rail_loop),
                  dict(height_m=0.915, body_width_m=0.380, stem_width_m=0.290, coping_setback_m=0.075,
                       length_m=round(b - a, 4)),
                  f'Corrected (drawing review 2026-11): sheet-18 rail section (380 mm cap and base, 290 mm stem, 19 mm '
                  f'recessed panel band), faces at |Y| 8.206-8.586 (75 mm setback), standing on the corrected '
                  f'{side} sidewalk; ends at the pilaster faces and at the sheet 9-10 rail ends.',
                  [24, 26, 27, 35, 36],
                  basis='Dimensioned sheet-18 section and sheet-17 layout; rail end flare and wing-end pilasters omitted')
            boxes, x = [], a
            layout = panel_layout(b - a)
            # Border strips fill the recess band back to the stem face on the outer (8.522-8.541) and the
            # sidewalk (8.251-8.270) face.
            faces_r = [(RAIL_OUT - RECESS_INSET, RAIL_OUT - STEM_INSET), (RAIL_IN + STEM_INSET, RAIL_IN + RECESS_INSET)]
            for j, seg in enumerate(layout):
                if j % 2 == 0:  # border
                    base = walk_top(x + seg / 2, RAIL_IN)
                    for r0, r1 in faces_r:
                        boxes.append(block(x, x + seg, s * r0, s * r1, base + RECESS_Z[0], base + RECESS_Z[1]))
                x += seg
            if not np.isclose(x, b, atol=1e-6):
                raise ValueError('panel layout does not close')
            standard = abs(b - a - 22.174) < 2e-3
            store(f'panels_{s}_{i}', trimesh.util.concatenate(boxes),
                  dict(relief_m=0.019, panel_height_m=0.310, panel_count=(len(layout) - 1) // 2),
                  'Corrected (drawing review 2026-11): borders of the 19 mm deep, 310 mm high recessed panels in the '
                  '290 mm stem, both faces, ' + ('sheet-17 panel layout.' if standard else
                                                'representative layout (152 / 305 mm borders, panels up to 2.4 m).'),
                  [35, 36])
        for i in range(5):
            cx = post_x(i, s)
            base = walk_top(cx, POST_IN)
            store(f'railpost_{s}_{i}', block(cx - POST_HALF, cx + POST_HALF, s * POST_IN, s * RAIL_OUT,
                                             base, base + POST_HEIGHT),
                  dict(center_x_m=round(cx, 4), coping_setback_m=0.075),
                  'Corrected (drawing review 2026-11): centred on the support centre line at the face of the arch ring '
                  '(|Y| 7.131, sheet 17), outer face 75 mm inside the coping (sheet 18), on the corrected sidewalk. '
                  'The 45 mm cap projection and recessed panel are not modelled.',
                  [26, 27, 35, 36])

    # ---- F4, F1: gas line on the east fascia ------------------------------------------------------------------
    pipe = trimesh.creation.cylinder(radius=GAS_R, height=X1 - X0, sections=20)
    pipe.apply_transform(trimesh.geometry.align_vectors([0, 0, 1], [1, 0, 0]))
    pipe.apply_translation([(X0 + X1) / 2, GAS_Y, GAS_Z])
    store('gas_line', pipe, dict(center_y_m=GAS_Y, length_m=round(X1 - X0, 3)),
          'Corrected (drawing review 2026-11): moved to the east fascia (-Y; sheet 7 / 15 section A-A, 2026 sheet 13); '
          'runs between the square floor ends. Height and diameter remain an envelope.',
          [24, 32])

    # ---- F1: end-floor retaining-wall envelopes follow the square floor ends -------------------------------
    for end in (-1, 1):
        for s in (-1, 1):
            pid = f'endwall_{end}_{s}'
            m = native(pid)
            v = m.vertices.copy()
            outer = np.isclose(np.abs(v @ np.array([1.0, T15, 0.0])), OLD_HALF, atol=1e-3)
            if outer.sum() != 4:
                raise ValueError(f'{pid}: unexpected outer end')
            v[outer, 0] = X0 if end < 0 else X1
            store(pid, trimesh.Trimesh(vertices=v, faces=m.faces, process=False),
                  dict(floor_end_x_m=X0 if end < 0 else X1),
                  'Outer end moved to the square floor end (drawing review 2026-11, sheets 9-10).', [26, 27])

    # ---- F5: abutment span faces at the springing -------------------------------------------------------------
    for pid, sign in (('pier_0', -1), ('pier_4', 1)):
        m = native(pid)
        v = m.vertices.copy()
        face = np.isclose(v @ np.array([1.0, T15, 0.0]), sign * OLD_ABUT_FACE_U, atol=1e-3)
        if face.sum() != 4:
            raise ValueError(f'{pid}: unexpected span face')
        v[face, 0] += sign * (ABUT_FACE_U - OLD_ABUT_FACE_U)
        store(pid, trimesh.Trimesh(vertices=v, faces=m.faces, process=False),
              dict(span_face_u_m=sign * ABUT_FACE_U),
              'Span face moved back 0.5715 m to the arch springing, Face Abut. Sta. '
              + ('1+968.894' if sign < 0 else '2+060.563') + ' (drawing review 2026-11, sheet 6).', [23])

    # ---- F8: arch ring faces 44 mm outside the spandrel faces --------------------------------------------------
    for i in range(4):
        pid = f'arch_{i}'
        m = native(pid)
        v = m.vertices.copy()
        y_new = np.sign(v[:, 1]) * RING_Y
        v[:, 0] -= T15 * (y_new - v[:, 1])
        v[:, 1] = y_new
        store(pid, trimesh.Trimesh(vertices=v, faces=m.faces, process=False), dict(barrel_width_m=2 * RING_Y),
              'Barrel widened to 14.262 m out to out of arch ring, 44 mm beyond each spandrel face '
              '(drawing review 2026-11, sheets 9 and 15).', [26, 32])

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
    (backup / 'sr1-wabash_before_review_correction.glb').write_bytes(original)
    (backup / 'sr1-wabash_manifest_before_review_correction.json').write_bytes(mp.read_bytes())
    path.write_bytes(out)

    for item in manifest.get('detail_coverage', []):
        if item.get('feature') == '2004 deck and sidewalks':
            item['detail'] = ('13.8 m roadway on a 300 mm slab (top at original P.G. + 49 mm, 2 % crossfall, 30.48 m '
                              'vertical curve at the Abutment 1 end), 17.322 m out to out, square floor ends 53.156 m / '
                              '55.328 m from Pier 3, 280 mm curbs and sidewalks falling 2 % to the roadway. Sidewalk '
                              'brackets, plan flare and drains are not modelled.')
            item['sources'] = sorted(set(item['sources']) | {'Primary PDF p.26', 'Primary PDF p.27',
                                                             'Primary PDF p.31'})
        elif item.get('feature') == 'Architectural parapets':
            item['detail'] = ('915 mm rails with the sheet-18 section (380 mm cap and base, 290 mm stem, 19 mm recessed '
                              'panels in the sheet-17 layout) and 960 mm pilasters centred on the support lines at the '
                              'arch-ring face. Rail end flare, wing-end pilasters and pilaster caps are omitted. Separate '
                              'pedestrian-bridge sheets 40-50 were excluded.')
        elif item.get('feature') == 'Remaining exterior features':
            item['detail'] = item['detail'].replace('Exact arch setting-out,',
                                                    'Exact arch setting-out, sidewalk concrete brackets (sheets 11-14),')
    renamed = {'walk_1': 'East sidewalk and cantilever -> West sidewalk and cantilever',
               'walk_-1': 'West sidewalk and cantilever -> East sidewalk and cantilever',
               'deck': '2004 roadway slab | 200 mm -> 2004 roadway slab | 300 mm'}
    manifest['review_correction'] = TAG
    manifest['revision'] = '1.1-drawing-review'
    manifest['review_correction_record'] = dict(
        source_pdf_pages=SOURCE_PAGES, printed_sheets=PRINTED_SHEETS,
        reference_2026_sheets=[11, 13],
        corrections={
            'floor_ends': 'Roadway slab, sidewalks, gas line and end-floor wall envelopes end square at X -53.156 / '
                          '+55.328 (sheets 9-10), not on skew lines at u -/+54.242',
            'roadway_slab': '300 mm slab, top original P.G. + 49 mm with the 30.48 m vertical curve (sheets 6, 7, 15)',
            'orientation': '+Y is west: walk_1 named West, walk_-1 East; gas line moved to the east fascia, Y -7.400 '
                           '(sheet 6 north arrow, sheet 7 section A-A, 2026 sheets 11 and 13)',
            'abutment_faces': 'pier_0 / pier_4 span faces at u -/+45.8345 (Face Abut. stations, sheet 6), 0.5715 m back',
            'sidewalks': '280 mm curb, 2 % fall toward the roadway, 190 mm fascia; curb unit down to the spandrel top '
                         '(sheets 7, 14, 15)',
            'rails': 'Sheet-18 rail section with 75 mm coping setback (faces |Y| 8.206-8.586) and the sheet-17 panel '
                     'layout; rail ends per sheets 9-10',
            'rail_pilasters': 'Centred on the support lines at the arch-ring face |Y| 7.131 (sheet 17), 0.349 m along X '
                              'from the old position, outer face 75 mm inside the coping (sheet 18)',
            'arch_rings': '14.262 m barrels, 44 mm beyond each spandrel face (sheets 9, 15)'},
        deferred={'sidewalk_brackets': 'Concrete brackets of sheets 11-14 (10 typical per span and side, plus pier, '
                                       'abutment and end brackets) need new components with new part ids'},
        changed_parts=changed, renamed_parts=renamed,
        before_glb_sha256=before, after_glb_sha256=hashlib.sha256(out).hexdigest())
    deviations = [d for d in manifest.get('known_deviations', [])
                  if d.get('id') not in ('sidewalk-brackets-not-modelled', 'deck-soffit-in-fill-envelope')]
    deviations += [
        dict(id='sidewalk-brackets-not-modelled', parts='walk_-1, walk_1', source='sheets 11-14 (PDF 28-31)',
             deviation='The concrete sidewalk brackets (typical 300 mm thick with R 1778 mm soffit, 10 per span and '
                       'side; pier, abutment and end brackets) are not modelled; the 1.574 m cantilever is shown as a '
                       'plain 190 mm slab.',
             reason='They are new components that need their own part ids; deferred from the 2026-11 drawing review.'),
        dict(id='deck-soffit-in-fill-envelope', parts='deck, fill_*, spandrel_*',
             source='sheets 7, 15 (PDF 24, 32)',
             deviation='The 300 mm slab soffit lies about 51 mm below the top of the hidden fill envelopes and the '
                       'inner 0.19 m of the spandrel-wall envelopes, which still follow the old surface less 200 mm.',
             reason='Fill and spandrel tops are approximate envelopes; the overlap is concealed.')]
    manifest['known_deviations'] = deviations
    mp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in manifest['review_correction_record'].items()
                      if k not in ('changed_parts', 'renamed_parts', 'corrections')}))
    print(f'{len(changed)} parts changed')


if __name__ == '__main__':
    correct()

"""Fifth review (second 3D placement review; runs after correct_21st_street_i465_3d_review.py): the MSE walls as
drawn. The walls wrap around both end bents: end walls 54A / 56A in front of the bents and side walls 54, 55, 56 and 57
along the approach embankment, with the monuments standing against the outer face of the side walls. Unrelated GLB
buffers are preserved.

    python scripts/correct_21st_street_i465_3d_review_2.py [--dry-run]

Drawing evidence (contract IB-30026, drawings.pdf; printed sheets 1-62 are PDF pages 1-62, printed sheets 64 and 73 are
PDF pages 63 and 72):

S03. The MSE walls were two straight 0.6 ft panel envelopes across the bridge width only (mse_west / mse_east, square
     ends at Y = +/-7.80 m) with 2 ft box copings; nothing retained the sides of the approach embankment, the
     monuments stood inside the wall line and overlapped the envelopes and copings (0.41-0.47 m3 and 0.12 m3 each),
     and two monument footings overlapped the outer end-bent piles -> RESOLVE.
   - Sheets 12-13 (roadway profile): 480.83 ft of MSE wall left (Wall 54) and 746.66 ft right (Wall 55) on the west
     approach, 846.5 ft left (Wall 56) and 954.67 ft right (Wall 57) on the east approach. Sheet 40 (general plan)
     draws MSE walls along both sides of both approaches with Monuments A-D at the four corners.
   - Sheets 20 and 22 (plans) and 24 (elevations of walls 54A / 56A): the side walls run at 24'-4 1/4" left / right of
     Line M (rear face; sheet 24 note: all wall stations and offsets are at the rear face) and end at the end walls,
     whose rear faces join them at STA 11+80.83 L / 11+96.66 R (west) and 14+03.50 L / 14+19.33 R (east): 51'-2 5/8"
     along the 18 deg skew. Section B-B: CL Bent to rear face of end wall 4'-5 1/4" (3'-0" cap, 2'-6" berm, 5 1/4" coping
     leg), panel 8 1/2" max., precast coping 1'-7" wide and 2'-0" high with the panel top 9" below the coping top.
     The stations reproduce CL Bent 1 / 3 (11+84.08 / 14+16.08) plus or minus 4'-5 1/4" / cos 18 deg within 0.003 ft.
   - Sheet 24 elevations: coping top El. 759.11 (N) to 759.28 (S) on 54A and 758.98 (N) to 758.79 (S) on 56A; top of
     leveling pad 740.47 for the south 30'-0" of 54A and 740.24 for the rest, 737.93 for the north 30'-0" of 56A and
     737.67 for the rest (equal to the monument base elevations G of the sheet 73 table, 740.25 / 740.47 / 737.93 /
     737.67, where the strip footing meets the monument footing on sheet 64).
   - Sheets 20-23 (elevations of walls 54-57): top of wall El. 765.84 at 11+78.00, 765.56 at 11+60, 765.38 at 11+50
     (Wall 54); 766.06 at 11+95.00, 765.86 at 11+80, 765.37 at 11+50 (Wall 55); 765.76 at 14+06.00, 765.53 at 14+20,
     765.18 at 14+40, 764.30 at 14+80 (Wall 56); 765.51 at 14+22.00, 765.36 at 14+30, 764.98 at 14+50 (Wall 57). The last
     2'-10" / 1'-8" / 2'-6" / 2'-8" to each corner stand only to the end-wall coping top (759.11 / 759.28 / 758.98 /
     758.79). Leveling pads step at 11+60 (Wall 54), 11+80 (Wall 55), 14+20 and 14+40 (Wall 56) and 14+30 (Wall 57);
     their labels there give the pad bottom (the 6" pad is drawn as a double line 4.56 pt = 0.51 ft apart at
     1/8" = 1'-0"; measured on the vector drawing, the labelled line is the lower one), so the panel bottoms are label +
     0.50 ft: 748.50 (54), 749.00 (55), 746.14 and 753.50 (56), 743.50 (57); at the corners the labels 739.74 / 739.97 /
     737.43 / 737.17 are the pad bottoms under the sheet 24 pad tops.
   - Sheet 64 (PDF 63) front elevation and sheet 73 (PDF 72) Section E-E: each monument is cast against the outer face
     of the side wall panel (1/4" bond breaker), 1'-6" thick against the 8 1/2" panel and 1'-9" against 5 1/2"
     (2'-2 1/2" together), so its rusticated face is 26'-6 3/4" from Line M; the end-wall coping terminates flush against
     the monument with a 1/2" joint. Sheet 73 footing offset table: footing edge 23'-10" from Line M (stations P to
     Q); sheet 64 draws the footing 1'-6" outside the monument face and under the wall panel (W = 4'-3").
   Correction:
   - mse_west / mse_east rebuilt as end walls 54A / 56A: rear face 4'-5 1/4" from CL Bent (normal), 8 1/2" panel, ends
     on the side walls' rear-face planes (Y = +/-24'-4 1/4"), bottom on the stepped leveling-pad tops, top at the coping
     underside (the 15" of panel inside the coping legs is counted in the coping, as before).
   - mse_coping_west / mse_coping_east rebuilt as the 1'-7" x 2'-0" precast coping straddling the panel (5 1/4" each
     side), top on the drawn slope, ends 1/2" short of the monuments (Y = +/-(25'-0 3/4" - 1/2")).
   - Added mse_return_west_1 / _-1 (walls 54 / 55) and mse_return_east_1 / _-1 (walls 56 / 57): 8 1/2" panels, rear face
     at Y = +/-24'-4 1/4", from the approach-slab pavement-end line (X = +/-43.737 m, the model's approach extent) to
     the end walls' front face, drawn top-of-wall profile and pad steps; the low corner piece is cut under the coping.
   - monument_A-D moved out to the drawn position: inner face on the panel's outer face (25'-0 3/4"), rusticated face at
     26'-6 3/4" (thickness 1'-6", was 1'-9" at 24'-2 3/4"-25'-11 3/4"); stations, elevations and taper unchanged.
   - monument_*_footing placed by the sheet 73 table: inner edge 23'-10" from Line M, stations P to Q (were centred on
     the shaft at 21'-8 1/2"-25'-11 1/2"); size and elevations unchanged. This also clears the outer end-bent piles.

Part ids of existing parts are unchanged; four parts are added. Requires numpy, trimesh and manifold3d.
"""
import hashlib
import json
import struct
import sys
from pathlib import Path

import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[1]
BID = '21st-street-i465'
BASE = ROOT / 'data/bridges' / BID
FT = 0.3048
IN = FT / 12
TAG = 'mse-walls-wrap-monuments-on-wall-face'
TAG_KEY = 'review_geometry_correction_3d_2'
RECORD_KEY = 'review_correction_record_3d_2'
REVISION = '1.5-3d-review-2'
PREVIOUS_TAG_KEY, PREVIOUS_TAG = 'review_geometry_correction_3d', 'parapet-on-deck-railing-posts-sheet60'
PREVIOUS_REVISION = '1.4-3d-review'
EXPECTED_GLB_SHA256 = '46eca999e7737c6677c275c8dc99ab22ebfab25d43e0d74f328e2bba45b34562'   # revision 1.4 output
NODE_MATRIX = [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0]   # native -> GLB

SKEW = np.radians(18.0)
TAN, COS, SIN = float(np.tan(SKEW)), float(np.cos(SKEW)), float(np.sin(SKEW))
STA0 = 1300.08                                   # CL Bent 2 = model X origin (manifest assumptions)
EL0 = 730.0                                      # native Z datum (manifest assumptions)
SPAN = 116.0                                     # ft, CL Bent 1 / 3 to CL Bent 2 (sheet 40)
CL_TO_REAR = 4 * 12 + 5.25                       # in, CL Bent to rear face of end wall, normal (sheet 24 B-B)
PANEL = 8.5                                      # in, MSE panel (sheet 24 B-B max.; sheet 73 E-E)
LEG = 5.25                                       # in, coping leg either side of the panel (sheet 24 B-B)
COPING_H = 24.0                                  # in, precast coping height (sheet 24 B-B)
JOINT = 0.5                                      # in, coping end to monument (sheet 64)
Y_REAR = 24 * 12 + 4.25                          # in, side-wall rear face from Line M (sheets 20, 22, 24 A-A)
Y_FRONT = Y_REAR + PANEL                         # in
Y_MON_OUT = Y_REAR + 26.5                        # in, panel + monument = 2'-2 1/2" (sheet 73 E-E)
Y_FOOT_IN = 23 * 12 + 10                         # in, monument footing edge (sheet 73 offset table)
ALONG_STEP = 30.0                                # ft along skew to the end-wall leveling-pad step (sheet 24)
PAD = 0.50                                       # ft, side-wall pad labels at the steps are pad bottoms

# sheet 24 (end walls) and sheets 20-23 (side walls). Elevations in ft; stations in ft (Line M, rear face).
ENDS = {
    -1: dict(name='west', bent=1, wall='54A', cl_bent_sta=1184.08,
             corners={1: 1180.83, -1: 1196.66},
             coping_top={1: 759.11, -1: 759.28},
             pad_near=dict(side=-1, el=740.47), pad_rest=740.25, pad_rest_sheet=740.24,
             walls={1: dict(wall='54', tall_sta=1178.00, top=[(1150.00, 765.38), (1160.00, 765.56), (1178.00, 765.84)],
                            pads=[(1160.00, 740.25), (1150.00, 748.00 + PAD)], pages=[12, 20, 24]),
                    -1: dict(wall='55', tall_sta=1195.00, top=[(1150.00, 765.37), (1180.00, 765.86), (1195.00, 766.06)],
                             pads=[(1180.00, 740.47), (1150.00, 748.50 + PAD)], pages=[12, 20, 21, 24])}),
    1: dict(name='east', bent=3, wall='56A', cl_bent_sta=1416.08,
            corners={1: 1403.50, -1: 1419.33},
            coping_top={1: 758.98, -1: 758.79},
            pad_near=dict(side=1, el=737.93), pad_rest=737.67, pad_rest_sheet=737.67,
            walls={1: dict(wall='56', tall_sta=1406.00, top=[(1406.00, 765.76), (1420.00, 765.53), (1440.00, 765.18),
                                                            (1480.00, 764.30)],
                           pads=[(1420.00, 737.93), (1440.00, 745.64 + PAD), (1480.00, 753.00 + PAD)], pages=[13, 22, 24]),
                   -1: dict(wall='57', tall_sta=1422.00, top=[(1422.00, 765.51), (1430.00, 765.36), (1450.00, 764.98)],
                            pads=[(1430.00, 737.67), (1450.00, 743.00 + PAD)], pages=[13, 22, 23, 24])}),
}
# sheet 73 (PDF 72): monument stations / elevations and footing offset table
MONUMENTS = {'A': dict(end=-1, side=1, G=740.25, P=1173.70, Q=1186.03),
             'B': dict(end=-1, side=-1, G=740.47, P=1189.20, Q=1201.53),
             'C': dict(end=1, side=1, G=737.93, P=1411.18, Q=1398.43),
             'D': dict(end=1, side=-1, G=737.67, P=1426.66, Q=1413.91)}
WALL_COLOR = [181, 175, 163, 255]                # '#b5afa3', the existing MSE wall parts
FIT = 1e-6                                       # m3, float32 residue of the manifold booleans
TOL = 2e-6


def boolean(op, meshes):
    return getattr(trimesh.boolean, op)(meshes, engine='manifold')


def X(sta):
    return (sta - STA0) * FT


def fmt_sta(sta):
    return f'{int(sta // 100)}+{sta - 100 * int(sta // 100):05.2f}'


def Z(el):
    return (el - EL0) * FT


def EL(z):
    return z / FT + EL0


def prism(plan, z_bottom, z_top):
    """Convex solid over a convex plan polygon [(x, y)], between planes given as functions z(x, y)."""
    pts = [(x, y, z_bottom(x, y)) for x, y in plan] + [(x, y, z_top(x, y)) for x, y in plan]
    mesh = trimesh.convex.convex_hull(np.array(pts, float))
    if not mesh.is_watertight or mesh.volume <= 0:
        raise ValueError('prism: invalid solid')
    return mesh


def surface_z(mesh, xy, top=True):
    """Z of the upper (top=True) or lower surface of a mesh on vertical lines through xy (brute force)."""
    tri = mesh.triangles
    a, b, c = tri[:, 0], tri[:, 1], tri[:, 2]
    d = (b[:, 1] - c[:, 1]) * (a[:, 0] - c[:, 0]) + (c[:, 0] - b[:, 0]) * (a[:, 1] - c[:, 1])
    ok = np.abs(d) > 1e-12
    dd = np.where(ok, d, 1.0)
    out = []
    for x, y in np.atleast_2d(xy):
        l1 = ((b[:, 1] - c[:, 1]) * (x - c[:, 0]) + (c[:, 0] - b[:, 0]) * (y - c[:, 1])) / dd
        l2 = ((c[:, 1] - a[:, 1]) * (x - c[:, 0]) + (a[:, 0] - c[:, 0]) * (y - c[:, 1])) / dd
        l3 = 1 - l1 - l2
        hit = ok & (l1 >= -1e-9) & (l2 >= -1e-9) & (l3 >= -1e-9)
        zs = (l1 * a[:, 2] + l2 * b[:, 2] + l3 * c[:, 2])[hit]
        out.append(np.nan if len(zs) == 0 else (zs.max() if top else zs.min()))
    return np.array(out)


def correct(dry_run=False):
    mp = BASE / 'model_manifest.json'
    raw_manifest = mp.read_bytes()
    manifest = json.loads(raw_manifest)
    if manifest.get(TAG_KEY) == TAG:
        print('Already corrected.')
        return
    path = BASE / 'model.glb'
    original = path.read_bytes()
    before = hashlib.sha256(original).hexdigest()

    def expect(ok, what):
        if not ok:
            raise ValueError(f'{BID}: unexpected starting model ({what})')

    expect(manifest.get(PREVIOUS_TAG_KEY) == PREVIOUS_TAG and manifest.get('revision') == PREVIOUS_REVISION,
           f'run scripts/correct_21st_street_i465_3d_review.py first (revision {manifest.get("revision")})')
    expect(TAG_KEY not in manifest and RECORD_KEY not in manifest, f'{TAG_KEY} already holds {manifest.get(TAG_KEY)}')
    expect(before == EXPECTED_GLB_SHA256 == manifest['review_correction_record_3d']['after_glb_sha256'],
           f'model.glb SHA-256 {before} is not the revision 1.4 output')
    expect(manifest.get('known_deviations') == [], 'known deviations')

    length = struct.unpack_from('<I', original, 12)[0]
    gltf = json.loads(original[20:20 + length])
    binary = bytearray(original[28 + length:])
    parts = {p['id']: p for p in manifest['parts']}
    meshes = {m['name']: m for m in gltf['meshes']}
    world = gltf['nodes'][0]
    expect(set(parts) == set(meshes) and len(parts) == 1944, 'part list')
    expect(world.get('name') == 'world' and len(world['children']) == 1944 and gltf['scenes'] == [{'nodes': [0]}],
           'scene nodes')
    expect(all(n.get('matrix') == NODE_MATRIX for n in gltf['nodes'][1:]), 'node transforms')
    expect(all(len(m['primitives']) == 1 for m in gltf['meshes']), 'one primitive per mesh')
    expect(not any(p['id'].startswith('mse_return_') for p in manifest['parts']), 'side walls already present')

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

    def solid(pid):
        if pid not in cache:
            p = meshes[pid]['primitives'][0]
            cache[pid] = trimesh.Trimesh(vertices=read(p['attributes']['POSITION']).astype(np.float64),
                                         faces=read(p['indices']).reshape(-1, 3), process=False)
        return cache[pid]

    def stored(mesh):
        return trimesh.Trimesh(mesh.vertices.astype('<f4').astype(np.float64), mesh.faces, process=False)

    def overlap(a, b):
        if np.any(a.bounds[0] > b.bounds[1] + 1e-6) or np.any(b.bounds[0] > a.bounds[1] + 1e-6):
            return 0.0
        return float(boolean('intersection', [a, b]).volume)

    r6 = lambda v: round(float(v), 6)
    old, new = {}, {}
    values = {}

    # ---------------------------------------------------------------- datum and starting geometry
    datum = {}
    for pid, el, axis in (('bent_1_cap', 758.87, 'bottom'), ('bent_3_cap', 758.55, 'bottom'),
                          ('monument_A', 765.83, 'top'), ('monument_A', 740.25, 'bottom'),
                          ('monument_C', 737.93, 'bottom'), ('monument_D_footing', 736.17, 'bottom')):
        z = solid(pid).bounds[0 if axis == 'bottom' else 1][2]
        expect(abs(z - Z(el)) < 2e-5, f'datum: {pid} {axis} {EL(z):.4f} vs El. {el}')
        datum[f'{pid}_{axis}'] = dict(drawn_el_ft=el, model_z_m=r6(z), model_el_ft=round(EL(z), 4))
    for end, cfg in ENDS.items():
        cap = solid(f'bent_{cfg["bent"]}_cap')
        xc = (cap.bounds[0][0] + cap.bounds[1][0]) / 2
        expect(abs(xc - X(cfg['cl_bent_sta'])) < 1e-4, f'CL Bent {cfg["bent"]} at {xc}')
        datum[f'cl_bent_{cfg["bent"]}'] = dict(drawn_sta_ft=cfg['cl_bent_sta'], model_x_m=r6(xc),
                                                 model_sta_ft=round(STA0 + xc / FT, 4))
    values['datum_check'] = datum
    pe = solid('approach_west').bounds[0][0], solid('approach_east').bounds[1][0]
    for wid in ('approach_walk_west_1', 'approach_walk_west_-1'):
        expect(abs(solid(wid).bounds[0][0] - pe[0]) < 1e-6, f'{wid}: pavement end')
    for wid in ('approach_walk_east_1', 'approach_walk_east_-1'):
        expect(abs(solid(wid).bounds[1][0] - pe[1]) < 1e-6, f'{wid}: pavement end')
    X_PE = {-1: float(pe[0]), 1: float(pe[1])}
    expect(abs(X_PE[-1] + X_PE[1]) < 1e-6 and abs(X_PE[1] - 43.737335) < 1e-5, 'pavement-end lines')
    for pid in ('mse_west', 'mse_east', 'mse_coping_west', 'mse_coping_east'):
        m = solid(pid)
        expect(len(m.vertices) == 8 and m.is_watertight and np.abs(np.abs(m.bounds[:, 1]) - (7.800657 if 'coping' not in pid
                                                                                              else 7.846966)).max() < 1e-5,
               f'{pid}: expected the 8-vertex box envelope')
        old[pid] = m
    mons = {}
    for k, cfg in MONUMENTS.items():
        m = solid(f'monument_{k}')
        ay = np.abs(m.vertices[:, 1])
        expect(np.all(np.sign(m.vertices[:, 1]) == cfg['side']), f'monument_{k}: side')
        expect(abs(ay.min() - 7.38378) < 1e-5 and abs(ay.max() - ay.min() - 1.75 * FT) < 1e-5, f'monument_{k}: section')
        expect(abs(m.bounds[0][2] - Z(cfg['G'])) < 2e-5, f'monument_{k}: base El. G')
        f = solid(f'monument_{k}_footing')
        expect(len(f.vertices) == 8 and abs(f.bounds[1][2] - Z(cfg['G'])) < 2e-5, f'monument_{k}_footing: box at G')
        expect(abs(np.abs(f.bounds[:, 1]).min() - 21.708333 * FT) < 1e-5, f'monument_{k}_footing: Y')
        old[f'monument_{k}'], old[f'monument_{k}_footing'] = m, f
        mons[k] = m


    # ---------------------------------------------------------------- geometry of the walls
    yr, yf = Y_REAR * IN, Y_FRONT * IN
    geo = {}
    for end, cfg in ENDS.items():
        d = -end                                   # +1: front face toward +X (west end), -1: toward -X (east end)
        x_rear0 = X(cfg['cl_bent_sta']) + d * CL_TO_REAR * IN / COS

        def x_rear(y, x0=x_rear0):
            return x0 - TAN * y

        def x_front(y, x0=x_rear0, d=d):
            return x0 - TAN * y + d * PANEL * IN / COS

        ct = cfg['coping_top']

        def coping_top(x, y, ct=ct):               # linear in Y between the rear-face corners (sheet 24)
            return Z(ct[-1] + (ct[1] - ct[-1]) * (y + yr) / (2 * yr))

        def coping_bottom(x, y, f=coping_top):
            return f(x, y) - COPING_H * IN

        corner_sta = {s: STA0 + x_rear(s * yr) / FT for s in (1, -1)}
        for s in (1, -1):
            expect(abs(corner_sta[s] - cfg['corners'][s]) < 0.006, f'{cfg["name"]} corner {s}: {corner_sta[s]:.3f}')
        geo[end] = dict(x_rear=x_rear, x_front=x_front, coping_top=coping_top, coping_bottom=coping_bottom, d=d,
                        corner_sta={str(s): round(corner_sta[s], 4) for s in (1, -1)})

    # ---------------------------------------------------------------- copings and end walls
    build = {}
    for end, cfg in ENDS.items():
        G = geo[end]
        d, xr, xf = G['d'], G['x_rear'], G['x_front']
        leg = d * LEG * IN / COS
        ye = yf - JOINT * IN
        plan = [(xr(-ye) - leg, -ye), (xf(-ye) + leg, -ye), (xf(ye) + leg, ye), (xr(ye) - leg, ye)]
        build[f'mse_coping_{cfg["name"]}'] = prism(plan, G['coping_bottom'], G['coping_top'])
        # cutter for the side walls' corner piece: the coping band past the side wall's outer face
        yc = yf + 0.05
        plan_c = [(xr(-yc) - leg, -yc), (xf(-yc) + leg, -yc), (xf(yc) + leg, yc), (xr(yc) - leg, yc)]
        G['cutter'] = prism(plan_c, G['coping_bottom'], lambda x, y: 50.0)
        # end wall: two pieces split at the pad step, 30'-0" along the skew from the near corner (normal joint)
        s0 = cfg['pad_near']['side']
        ys = s0 * yr - s0 * ALONG_STEP * FT * COS
        p_rear = np.array([xr(ys), ys])
        normal = np.array([COS, SIN]) * d          # rear face -> front face
        p_front = p_rear + normal * PANEL * IN
        expect(abs(p_front[0] - xf(p_front[1])) < 1e-9, 'joint on the front face')
        near = [(xr(s0 * yr), s0 * yr), (xf(s0 * yr), s0 * yr), tuple(p_front), tuple(p_rear)]
        rest = [tuple(p_rear), tuple(p_front), (xf(-s0 * yr), -s0 * yr), (xr(-s0 * yr), -s0 * yr)]
        pieces = []
        for plan_p, el in ((near, cfg['pad_near']['el']), (rest, cfg['pad_rest'])):
            pieces.append(prism(plan_p, lambda x, y, z=Z(el): z, G['coping_bottom']))
        wall = boolean('union', pieces)
        expect(abs(wall.volume - sum(p.volume for p in pieces)) < 2e-4, f'{cfg["name"]} end wall union')
        build[f'mse_{cfg["name"]}'] = wall
        G['step'] = dict(rear_point_m=[r6(v) for v in p_rear], along_skew_from_corner_ft=ALONG_STEP)
        # previous envelope: its two long faces as X at Y = 0 (X + tan(skew) Y is constant on each)
        c = np.unique(np.round(old[f'mse_{cfg["name"]}'].vertices[:, 0] + TAN * old[f'mse_{cfg["name"]}'].vertices[:, 1], 3))
        expect(len(c) == 2, f'mse_{cfg["name"]}: faces')
        c_rear = c.min() if d > 0 else c.max()
        G['rear_shift_m'] = abs(float(c_rear) - xr(0.0))
        G['rear_face_x_at_y0_m'] = [r6(c_rear), r6(xr(0.0))]

    # ---------------------------------------------------------------- side walls (54, 55, 56, 57)
    side_rec = {}
    for end, cfg in ENDS.items():
        G = geo[end]
        for s, w in cfg['walls'].items():
            pid = f'mse_return_{cfg["name"]}_{s}'
            y_in, y_out = s * yr, s * yf
            top_pts = sorted(w['top'])
            top_el = lambda sta, tp=top_pts: float(np.interp(sta, [p[0] for p in tp], [p[1] for p in tp]))
            pads = w['pads']                       # [(station of the far end of the segment, pad top)], from the corner
            corner = cfg['corners'][s]
            # stations from the pavement end to the end of the tall part, with breaks at the drawn stations between
            sta_pe = STA0 + X_PE[end] / FT
            lo_s, hi_s = sorted((sta_pe, w['tall_sta']))
            inner = sorted({sta for sta, _ in w['top']} | {sta for sta, _ in pads})
            inner = [v for v in inner if lo_s + 1e-6 < v < hi_s - 1e-6]
            stations = [sta_pe] + sorted(inner, key=lambda v: abs(v - sta_pe)) + [w['tall_sta']]
            expect((w['tall_sta'] - sta_pe) * end < 0 and (corner - w['tall_sta']) * end < 0, f'{pid}: stations')

            def pad_at(sta, pads=pads, corner=corner):
                # pad top of the segment containing sta: segments run from the corner outwards
                lo = corner
                for far_sta, el in pads:
                    if min(lo, far_sta) - 1e-9 <= sta <= max(lo, far_sta) + 1e-9:
                        return el
                    lo = far_sta
                raise ValueError(f'{pid}: no pad at {sta}')

            segs, rec_segs = [], []
            for a, b in zip(stations[:-1], stations[1:]):
                xa, xb = X(a), X(b)
                el_pad = pad_at((a + b) / 2)
                za, zb = Z(top_el(a)), Z(top_el(b))
                top = lambda x, y, xa=xa, xb=xb, za=za, zb=zb: za + (zb - za) * (x - xa) / (xb - xa)
                plan = [(xa, y_in), (xb, y_in), (xb, y_out), (xa, y_out)]
                segs.append(prism(plan, lambda x, y, z=Z(el_pad): z, top))
                rec_segs.append(dict(stations=[round(a, 3), round(b, 3)], top_el=[round(top_el(a), 3), round(top_el(b), 3)],
                                     panel_bottom_el=el_pad))
            # corner piece: tall-part end to the end wall's front face, up to the coping top
            xt = X(w['tall_sta'])
            plan = [(xt, y_in), (G['x_front'](y_in), y_in), (G['x_front'](y_out), y_out), (xt, y_out)]
            el_corner = pads[0][1]
            segs.append(prism(plan, lambda x, y, z=Z(el_corner): z, G['coping_top']))
            rec_segs.append(dict(stations=[w['tall_sta'], round(STA0 + G['x_front'](y_in) / FT, 3)],
                                 top='end-wall coping top', panel_bottom_el=el_corner))
            raw = boolean('union', segs)
            expect(abs(raw.volume - sum(p.volume for p in segs)) < 2e-4, f'{pid}: union of segments')
            mesh = boolean('difference', [raw, G['cutter']])
            cut = raw.volume - mesh.volume
            expect(0.02 < cut < 0.08, f'{pid}: coping cut {cut}')
            build[pid] = mesh
            side_rec[pid] = dict(wall=w['wall'], segments=rec_segs, cut_under_coping_m3=r6(cut),
                                 pavement_end_sta=round(sta_pe, 3), rear_face_y_m=r6(y_in), front_face_y_m=r6(y_out))

    # ---------------------------------------------------------------- monuments and footings
    mon_rec = {}
    scale = (Y_MON_OUT - Y_FRONT) / (1.75 * 12)
    for k, cfg in MONUMENTS.items():
        s = cfg['side']
        m = mons[k]
        v = m.vertices.copy()
        v[:, 1] = s * (yf + (np.abs(v[:, 1]) - 7.38378) * scale)
        build[f'monument_{k}'] = trimesh.Trimesh(v, m.faces, process=False)
        f = old[f'monument_{k}_footing']
        v = f.vertices.copy()
        xs = sorted((X(cfg['P']), X(cfg['Q'])))
        L = f.extents[0]
        xc = (xs[0] + xs[1]) / 2
        lo_x, hi_x = f.bounds[0][0], f.bounds[1][0]
        v[:, 0] = np.where(np.abs(v[:, 0] - lo_x) < 1e-9, xc - L / 2, xc + L / 2)
        lo_y = np.abs(f.vertices[:, 1]).min()
        v[:, 1] = np.where(np.abs(np.abs(f.vertices[:, 1]) - lo_y) < 1e-9, s * Y_FOOT_IN * IN,
                           s * (Y_FOOT_IN * IN + f.extents[1]))
        build[f'monument_{k}_footing'] = trimesh.Trimesh(v, f.faces, process=False)
        mon_rec[k] = dict(shaft_y_ft_before=[round(float(np.abs(m.vertices[:, 1]).min() / FT), 4),
                                            round(float(np.abs(m.vertices[:, 1]).max() / FT), 4)],
                          shaft_y_ft_after=[round(Y_FRONT / 12, 4), round(Y_MON_OUT / 12, 4)],
                          footing_y_ft_before=[round(float(np.abs(f.vertices[:, 1]).min() / FT), 4),
                                               round(float(np.abs(f.vertices[:, 1]).max() / FT), 4)],
                          footing_y_ft_after=[round(Y_FOOT_IN / 12, 4), round(Y_FOOT_IN / 12 + f.extents[1] / FT, 4)],
                          footing_sta_before=[round(STA0 + lo_x / FT, 3), round(STA0 + hi_x / FT, 3)],
                          footing_sta_after=[round(STA0 + (xc - L / 2) / FT, 3), round(STA0 + (xc + L / 2) / FT, 3)],
                          table_P_Q=[cfg['P'], cfg['Q']], length_ft=round(L / FT, 4))
        if abs(L / FT - abs(cfg['Q'] - cfg['P'])) > 0.01:
            raise ValueError(f'monument_{k}_footing: length {L / FT} vs P-Q {abs(cfg["Q"] - cfg["P"])}')

    for pid, m in build.items():
        st = stored(m)
        if not st.is_watertight or not st.is_winding_consistent or st.volume <= 0:
            raise ValueError(f'{pid}: not a closed solid after float32 storage')
        new[pid] = st
    added = sorted(p for p in new if p.startswith('mse_return_'))
    changed = sorted(p for p in new if p not in added)

    # ---------------------------------------------------------------- verification
    # every pair of a changed or added part with a part whose box (before or after) comes within 2 mm of it
    before_b = {p['id']: np.array(p['bounds_m']) for p in manifest['parts']}
    after_b = dict(before_b)
    for pid, m in new.items():
        after_b[pid] = m.bounds
    pairs = set()
    for pid in new:
        for boxes in (before_b, after_b):
            if pid not in boxes:
                continue
            lo, hi = boxes[pid]
            for qid, b in boxes.items():
                if qid != pid and not (np.any(b[0] > hi + 0.002) or np.any(b[1] < lo - 0.002)):
                    pairs.add(tuple(sorted((pid, qid))))
    clashes, kept, reduced, neighbours = {}, {}, {}, {}
    for pid, qid in sorted(pairs):
        after = overlap(new[pid] if pid in new else solid(pid), new[qid] if qid in new else solid(qid))
        before_v = overlap(solid(pid), solid(qid)) if pid in meshes and qid in meshes else 0.0
        key = f'{pid}_x_{qid}'
        for a_, b_ in ((pid, qid), (qid, pid)):
            if a_ in new:
                neighbours.setdefault(a_, []).append(b_)
        if after > before_v + FIT:
            clashes[key] = [r6(before_v), r6(after)]
        elif after > 1e-9:
            kept[key] = [r6(before_v), r6(after)]
        if before_v > 1e-9 and after < before_v - 1e-9:
            reduced[key] = [r6(before_v), r6(after)]
    if clashes:
        raise ValueError(f'new or grown overlaps: {clashes}')
    values['overlap_pairs_checked'] = len(pairs)
    values['overlap_neighbours_checked'] = {k: sorted(v) for k, v in sorted(neighbours.items())}
    values['overlaps_m3_removed_before_after'] = reduced
    values['overlaps_m3_remaining_before_after'] = kept

    def face_points(mesh, axis, value, tol=1e-6):
        """Centroids of the triangles of mesh lying in the plane axis = value, with their areas."""
        tri = mesh.triangles
        sel = np.all(np.abs(tri[:, :, axis] - value) < tol, axis=1)
        return tri[sel].mean(axis=1), mesh.area_faces[sel]

    contacts = {}
    for end, cfg in ENDS.items():
        G = geo[end]
        wall, cop = new[f'mse_{cfg["name"]}'], new[f'mse_coping_{cfg["name"]}']
        for s in (1, -1):
            sw = new[f'mse_return_{cfg["name"]}_{s}']
            # the end wall's end face lies on the side wall's rear face
            c, a = face_points(wall, 1, s * yr, 2e-5)
            dist = trimesh.proximity.closest_point(sw, c)[1]
            # the side wall's outer face backs the monument's inner face where they meet
            mk = [k for k, mc in MONUMENTS.items() if mc['end'] == end and mc['side'] == s][0]
            mon = new[f'monument_{mk}']
            cm, am = face_points(mon, 1, s * yf, 2e-5)
            dm = trimesh.proximity.closest_point(sw, cm)[1]
            backed = float(am[dm < 1e-4].sum() / am.sum())
            joint = float(abs(np.abs(cop.vertices[:, 1]).max() - yf))
            foot = new[f'monument_{mk}_footing']
            fy = sorted(np.abs(foot.bounds[:, 1]))
            under = [(x, s * y) for x in np.linspace(foot.bounds[0][0] + 0.05, foot.bounds[1][0] - 0.05, 9)
                     for y in np.linspace(max(fy[0], yr) + 0.01, yf - 0.01, 3)]
            under = [p for p in under if (p[0] - G['x_front'](p[1])) * G['d'] < -0.01]
            gap = surface_z(sw, np.array(under), top=False) - foot.bounds[1][2]
            contacts[f'{cfg["name"]}_{s}'] = dict(
                end_wall_end_face_on_side_wall_rear_face_max_mm=round(float(dist.max()) * 1e3, 4),
                end_wall_end_face_area_m2=round(float(a.sum()), 4),
                monument=f'monument_{mk}', monument_inner_face_on_side_wall_fraction=round(backed, 4),
                monument_inner_face_gap_max_mm=round(float(dm[dm < 0.05].max()) * 1e3, 4) if np.any(dm < 0.05) else None,
                coping_end_to_monument_mm=round(joint * 1e3, 3),
                side_wall_bottom_minus_footing_top_mm=[round(float(np.nanmin(gap)) * 1e3, 3),
                                                       round(float(np.nanmax(gap)) * 1e3, 3)])
            if dist.max() > 1e-4 or backed < 0.25 or abs(joint - JOINT * IN) > 1e-4 or np.nanmax(np.abs(gap)) > 1e-4:
                raise ValueError(f'{cfg["name"]} {s}: walls / monument do not meet as drawn {contacts}')
    values['contacts'] = contacts

    # clearances under the superstructure and the moment slabs
    clear = {}
    for pid in added:
        sw = new[pid]
        xs = np.linspace(sw.bounds[0][0] + 0.02, sw.bounds[1][0] - 0.02, 160)
        ys = np.sign(sw.bounds[0][1] + sw.bounds[1][1]) * np.array([yr + 0.01, (yr + yf) / 2, yf - 0.01])
        pts = np.array([(x, y) for x in xs for y in ys])
        top = surface_z(sw, pts)
        res = {}
        for qid in ('deck', 'approach_walk_west_1', 'approach_walk_west_-1', 'approach_walk_east_1',
                    'approach_walk_east_-1'):
            under = surface_z(solid(qid), pts, top=False)
            ok = ~np.isnan(under) & ~np.isnan(top)
            if ok.any():
                res[qid] = round(float((under[ok] - top[ok]).min()) * 1e3, 2)
        clear[pid] = res
        if min(res.values()) < 5:
            raise ValueError(f'{pid}: less than 5 mm under {res}')
    values['side_wall_top_clearance_mm'] = clear
    for pid in ('monument_A', 'monument_B', 'monument_C', 'monument_D'):
        m = new[pid]
        pts = np.array([(x, y) for x in np.linspace(m.bounds[0][0] + .02, m.bounds[1][0] - .02, 40)
                        for y in np.linspace(m.bounds[0][1] + .01, m.bounds[1][1] - .01, 5)])
        under, top = surface_z(solid('deck'), pts, top=False), surface_z(m, pts)
        ok = ~np.isnan(under) & ~np.isnan(top)
        clear[pid] = dict(deck=round(float((under[ok] - top[ok]).min()) * 1e3, 2) if ok.any() else None)
    print(json.dumps(dict(contacts=contacts, clearance_mm=clear), indent=1))

    # ---------------------------------------------------------------- write meshes
    for pid in changed:
        p = meshes[pid]['primitives'][0]
        m = new[pid]
        if pid.startswith('monument_'):            # same faces and colours, vertices moved
            expect(len(m.vertices) == gltf['accessors'][p['attributes']['POSITION']]['count'], f'{pid}: vertex count')
            p['attributes']['POSITION'] = append(m.vertices.astype('<f4'), 'VEC3', 5126)
        else:
            color = read(p['attributes']['COLOR_0'])[0]
            vertices = m.vertices.astype('<f4')
            p['attributes'] = {'POSITION': append(vertices, 'VEC3', 5126),
                               'COLOR_0': append(np.tile(color, (len(vertices), 1)).astype('u1'), 'VEC4', 5121)}
            gltf['accessors'][p['attributes']['COLOR_0']]['normalized'] = True
            p['indices'] = append(m.faces.reshape(-1, 1).astype('<u4'), 'SCALAR', 5125)
            meshes[pid]['extras'].pop('shape', None)
            meshes[pid]['extras'].pop('extents', None)
    for pid in added:
        m = new[pid]
        vertices = m.vertices.astype('<f4')
        prim = {'attributes': {'POSITION': append(vertices, 'VEC3', 5126),
                               'COLOR_0': append(np.tile(WALL_COLOR, (len(vertices), 1)).astype('u1'), 'VEC4', 5121)},
                'indices': append(m.faces.reshape(-1, 1).astype('<u4'), 'SCALAR', 5125), 'mode': 4}
        gltf['accessors'][prim['attributes']['COLOR_0']]['normalized'] = True
        gltf['meshes'].append(dict(name=pid, extras={}, primitives=[prim]))
        meshes[pid] = gltf['meshes'][-1]
        gltf['nodes'].append(dict(name=pid, mesh=len(gltf['meshes']) - 1, matrix=list(NODE_MATRIX)))
        world['children'].append(len(gltf['nodes']) - 1)

    # ---------------------------------------------------------------- manifest entries
    vol = {pid: new[pid].volume for pid in new}
    vol_old = {pid: old[pid].volume for pid in old}
    for end, cfg in ENDS.items():
        n, G = cfg['name'], geo[end]
        ct = cfg['coping_top']
        p = parts[f'mse_{n}']
        p['name'] = f'{n.capitalize()} MSE end wall {cfg["wall"]} | panel envelope'
        p['pdf_pages'] = sorted(set(p['pdf_pages']) | {20 if end < 0 else 22, 24, 40, 63, 72})
        p['basis'] = 'Dimensioned plan, panel and elevations (sheet 24); panel joints and texture not modelled'
        near = cfg['pad_near']
        p['dimensions'] = dict(
            panel_thickness_in=PANEL, rear_face_from_cl_bent_normal_in=CL_TO_REAR,
            length_along_skew_ft=round(2 * Y_REAR / 12 / COS, 4), ends_at_side_wall_rear_face_y_ft=round(Y_REAR / 12, 6),
            top_of_wall_el_ft={'north': round(ct[1] - 0.75, 2), 'south': round(ct[-1] - 0.75, 2)},
            top_of_leveling_pad_el_ft={('south' if near['side'] < 0 else 'north') + '_30ft': near['el'],
                                       'rest': cfg['pad_rest']},
            modelled_top='coping underside (coping top - 2 ft)')
        rest_note = ('' if cfg['pad_rest'] == cfg['pad_rest_sheet'] else
                     f'; sheet 24 gives {cfg["pad_rest_sheet"]:.2f} there, and the sheet 73 base El. G of the monument, '
                     f'{cfg["pad_rest"]:.2f}, is used because the panels stand on the monument footing')
        p['note'] = (f'MSE Wall {cfg["wall"]} in front of End Bent {cfg["bent"]} as drawn on sheet 24 (elevation and '
                     f'Section B-B) and the sheet {20 if end < 0 else 22} plan: rear face 4\'-5 1/4" from CL Bent '
                     f'{cfg["bent"]} (normal), 8 1/2" panel, 51\'-2 5/8" along the skew between the side walls\' rear '
                     f'faces (STA {fmt_sta(cfg["corners"][1])} Lt. to {fmt_sta(cfg["corners"][-1])} Rt.), bottom on the top of the '
                     f'leveling pad (El. {near["el"]:.2f} for the {"south" if near["side"] < 0 else "north"} 30\'-0", '
                     f'{cfg["pad_rest"]:.2f} for the rest{rest_note}). Top at the coping underside; the 15" of panel '
                     'inside the coping legs is counted in the coping. Leveling pad, panel joints and architectural '
                     'texture not modelled. Rev. 1.5 (3D review 2): replaces the square-ended 0.6 ft envelope across '
                     f'+/-7.80 m, whose rear face stood {G["rear_shift_m"]:.3f} m nearer the bent, which ran into the '
                     f'monuments and had no side walls ({vol[f"mse_{n}"] - vol_old[f"mse_{n}"]:+.3f} m3).')
        p = parts[f'mse_coping_{n}']
        p['name'] = f'{n.capitalize()} MSE wall {cfg["wall"]} precast coping'
        p['pdf_pages'] = sorted(set(p['pdf_pages']) | {24, 63})
        p['basis'] = 'Dimensioned coping section and elevations (sheets 24, 64)'
        p['dimensions'] = dict(height_ft=2, width_in=19, legs_in=LEG, panel_top_below_coping_top_in=9,
                               top_el_ft={'north': ct[1], 'south': ct[-1]}, end_joint_to_monument_in=JOINT)
        p['note'] = (f'Precast coping on Wall {cfg["wall"]} (sheet 24 Section B-B): 1\'-7" wide, 2\'-0" high, straddling '
                     'the 8 1/2" panel with 5 1/4" legs; modelled as a solid block on the panel envelope (the panel '
                     f'stops at its underside). Top El. {ct[1]:.2f} north to {ct[-1]:.2f} south at the rear-face corners, '
                     'linear along the skew; ends terminate flush against the monuments with a 1/2" joint (sheet 64). '
                     f'Rev. 1.5 (3D review 2): was a box at El. {EL(old[f"mse_coping_{n}"].bounds[0][2]):.1f}-'
                     f'{EL(old[f"mse_coping_{n}"].bounds[1][2]):.1f} across +/-7.85 m, '
                     f'1.3-1.5 ft too high and into the monuments ({vol[f"mse_coping_{n}"] - vol_old[f"mse_coping_{n}"]:+.3f} m3).')
    new_parts = []
    for end, cfg in ENDS.items():
        n = cfg['name']
        for s, w in cfg['walls'].items():
            pid = f'mse_return_{n}_{s}'
            rec = side_rec[pid]
            tops = ', '.join(f'{el:.2f} at {fmt_sta(sta)}' for sta, el in sorted(w['top']))
            pads = ', '.join(f'{el:.2f}' for _, el in w['pads'])
            hand = 'north (left)' if s > 0 else 'south (right)'
            corner_top = cfg['coping_top'][s]
            pe_sta = rec['pavement_end_sta']
            new_parts.append(dict(
                id=pid, name=f'MSE wall {w["wall"]}, {hand} side of the {n} approach | panel envelope', layer='walls',
                color='#b5afa3', pdf_pages=sorted(set(w['pages']) | {24, 40, 63, 72}),
                basis='Dimensioned offset and elevations (sheets 20-24); truncated at the model\'s approach extent',
                note=(f'MSE Wall {w["wall"]} on the {hand} side of the {n} approach embankment, as drawn on sheets '
                      f'{", ".join(str(q) for q in w["pages"] if q not in (12, 13))}: rear face 24\'-4 1/4" '
                      f'{"left" if s > 0 else "right"} of Line M, 8 1/2" panel. Top of wall {tops} (linear between); '
                      f'the last {abs(w["tall_sta"] - cfg["corners"][s]):.2f} ft to the corner stand only to the end-wall '
                      f'coping top El. {corner_top:.2f} and are cut under the coping. Panel bottom on the top of the '
                      f'leveling pad, El. {pads} from the corner outwards (the sheet labels at the steps are the pad '
                      'bottoms, 0.50 ft lower). Modelled from the end wall\'s front face to the approach-slab '
                      f'pavement-end line (STA {fmt_sta(pe_sta)}); the wall continues beyond the model '
                      f'({"480.83" if w["wall"] == "54" else "746.66" if w["wall"] == "55" else "846.5" if w["wall"] == "56" else "954.67"} '
                      'ft in all, sheets 12-13). The concrete barrier on the moment slab, which covers the wall top on '
                      'the drawn Section A-A, the leveling pad, panel joints and texture are not modelled. Added in Rev. '
                      '1.5 (3D review 2).'),
                dimensions=dict(panel_thickness_in=PANEL, rear_face_offset_ft=round(Y_REAR / 12, 6),
                                front_face_offset_ft=round(Y_FRONT / 12, 6), wall_length_drawn_ft=
                                {'54': 480.83, '55': 746.66, '56': 846.5, '57': 954.67}[w['wall']],
                                modelled_from_sta=round(STA0 + new[pid].bounds[0 if end < 0 else 1][0] / FT, 3),
                                top_of_wall_el_ft={f'{sta:.2f}': el for sta, el in sorted(w['top'])},
                                corner_piece_top_el_ft=corner_top, corner_piece_from_sta=w['tall_sta'],
                                top_of_leveling_pad_el_ft=[[sta, el] for sta, el in w['pads']]),
                bounds_m=new[pid].bounds.round(6).tolist(), volume_m3=round(float(vol[pid]), 8)))
    for k, cfg in MONUMENTS.items():
        p = parts[f'monument_{k}']
        p['pdf_pages'] = sorted(set(p['pdf_pages']) | {20, 22, 24})
        p['basis'] = ('Dimensioned elevation, longitudinal taper and transverse position against the MSE wall '
                      '(sheets 64, 73); simplified transverse section')
        p['dimensions']['nominal_thickness_ft'] = 1.5
        p['dimensions']['inner_face_offset_ft'] = round(Y_FRONT / 12, 6)
        p['dimensions']['outer_face_offset_ft'] = round(Y_MON_OUT / 12, 6)
        p['note'] = p['note'].replace(
            'Transverse thickness held at 1 ft 9 in; actual section varies 1 ft 6 in to 1 ft 9 in.',
            'Transverse thickness 1 ft 6 in against the 8 1/2 in panel envelope of the MSE wall (drawn 1 ft 6 in to '
            '1 ft 9 in against the textured 8 1/2 in to 5 1/2 in panels, 2 ft 2 1/2 in together, sheet 73 Section E-E).')
        expect('1 ft 6 in against' in p['note'], f'monument_{k}: note')
        p['note'] += (' Rev. 1.5 (3D review 2): moved out to the drawn position, cast against the outer face of the side '
                      f'wall (inner face {Y_FRONT / 12:.4f} ft, rusticated face {Y_MON_OUT / 12:.4f} ft from Line M; sheet '
                      '64 front elevation, sheet 73 Section E-E); it stood at 24.23-25.98 ft inside the wall line. '
                      'Stations, elevations and taper unchanged.')
        f = parts[f'monument_{k}_footing']
        f['pdf_pages'] = sorted(set(f['pdf_pages']) | {63})
        f['basis'] = 'Dimensioned size, elevation and position (sheet 73 footing offset table)'
        f['dimensions']['inner_edge_offset_ft'] = round(Y_FOOT_IN / 12, 6)
        f['dimensions']['station_p_q_ft'] = [cfg['P'], cfg['Q']]
        f['note'] = (f'Placed by the sheet 73 footing offset table: edge 23\'-10" from Line M toward the bridge, stations '
                     f'P {fmt_sta(cfg["P"])} to Q {fmt_sta(cfg["Q"])}; it reaches 1\'-6" outside the monument face and under the '
                     'MSE wall panel (sheet 64 front elevation). Rev. 1.5 (3D review 2): was centred under the shaft at '
                     '21.71-25.96 ft from Line M, where it overlapped the outer end-bent pile.')
    for pid in changed:
        parts[pid]['bounds_m'] = new[pid].bounds.round(6).tolist()
        parts[pid]['volume_m3'] = round(float(vol[pid]), 8)
    order = [p['id'] for p in manifest['parts']]
    at = order.index('mse_coping_east') + 1
    manifest['parts'][at:at] = new_parts
    for p in new_parts:
        parts[p['id']] = p
    for pid in changed + added:
        meshes[pid]['extras'].update(parts[pid])
    expect(set(parts) == set(meshes) == {p['id'] for p in manifest['parts']} and len(parts) == 1948, 'final part list')
    expect(all(gltf['nodes'][c]['name'] == gltf['meshes'][gltf['nodes'][c]['mesh']]['name'] for c in world['children']),
           'node names')

    b = np.array([q['bounds_m'] for q in manifest['parts']])
    lo, hi = b[:, 0].min(axis=0), b[:, 1].max(axis=0)
    manifest['bounds_m'] = [lo.round(6).tolist(), hi.round(6).tolist()]
    manifest['glb_bounds_m'] = [[round(lo[0], 6), round(lo[2], 6), round(-hi[1], 6)],
                                [round(hi[0], 6), round(hi[2], 6), round(-lo[1], 6)]]
    for d in manifest['detail_coverage']:
        if d['feature'] == 'MSE wall context':
            d['feature'] = 'MSE walls'
            d['detail'] = ('End walls 54A and 56A (51 ft 2-5/8 in along the skew, rear face 4 ft 5-1/4 in from CL Bent, '
                           '8-1/2 in panels, 19 x 24 in precast coping, stepped leveling-pad tops) and the bridge ends of '
                           'side walls 54, 55, 56 and 57 (rear face 24 ft 4-1/4 in from Line M, drawn top-of-wall profile '
                           'and leveling-pad steps), modelled to the approach-slab pavement-end line; the side walls '
                           'continue 300-800 ft beyond the model. Panel joints and texture, leveling pads, ground '
                           'reinforcement, retained earth, berm slopewall and the barrier on the approach moment slabs '
                           'are not modelled.')
            d['sources'] = sorted(set(d['sources']) | {12, 13, 20, 21, 22, 23, 24, 72})
        elif d['feature'] == 'Four monuments':
            d['detail'] = d['detail'].replace(
                'variable transverse section and small asymmetric footing offsets simplified.',
                'shafts against the outer face of the MSE side walls, 1 ft 6 in thick against the 8-1/2 in panel '
                'envelope (variable 1 ft 6 in to 1 ft 9 in section against the textured panels simplified); footings '
                'by the sheet 73 offset table.')
            expect('offset table' in d['detail'], 'monument coverage')
            d['sources'] = sorted(set(d['sources']) | {24})
    for i, a in enumerate(manifest['assumptions']):
        if a.startswith('MSE walls, pile positioning'):
            manifest['assumptions'][i] = a.replace(
                'MSE walls, pile positioning,',
                'MSE wall panels (envelopes without joints or texture, side walls truncated at the approach-slab '
                'pavement-end line), pile positioning,')
    expect(any(a.startswith('MSE wall panels (envelopes') for a in manifest['assumptions']), 'assumptions')
    expect(manifest['layers'].get('walls') == 'MSE wall context and coping', 'walls layer label')
    manifest['layers']['walls'] = 'MSE walls and coping'
    manifest[TAG_KEY] = TAG
    manifest['revision'] = REVISION

    gltf['buffers'][0]['byteLength'] = len(binary)
    while len(binary) % 4:
        binary.append(0)
    gltf['buffers'][0]['byteLength'] = len(binary)
    encoded = json.dumps(gltf, ensure_ascii=True, separators=(',', ':')).encode()
    encoded += b' ' * ((-len(encoded)) % 4)
    out = (struct.pack('<III', 0x46546c67, 2, 28 + len(encoded) + len(binary)) +
           struct.pack('<II', len(encoded), 0x4e4f534a) + encoded + struct.pack('<II', len(binary), 0x004e4942) + binary)

    values['geometry_read'] = dict(
        corners_rear_face_sta={ENDS[e]['name']: geo[e]['corner_sta'] for e in ENDS},
        end_wall_pad_step={ENDS[e]['name']: geo[e]['step'] for e in ENDS},
        end_wall_rear_face_x_at_line_m_before_after={ENDS[e]['name']: geo[e]['rear_face_x_at_y0_m'] for e in ENDS},
        pavement_end_x_m={ENDS[e]['name']: r6(X_PE[e]) for e in ENDS},
        side_walls=side_rec, monuments=mon_rec)
    values['volumes_m3'] = {pid: [r6(vol_old.get(pid, 0.0)), r6(vol[pid])] for pid in sorted(vol)}
    manifest[RECORD_KEY] = dict(
        source_pdf_pages=[12, 13, 20, 21, 22, 23, 24, 40, 41, 63, 72],
        printed_sheets=[12, 13, 20, 21, 22, 23, 24, 40, 41, 64, 73],
        previous_revision=PREVIOUS_REVISION,
        native_axes='X = Line M station from 13+00.08 (CL Bent 2), Y = left of Line M looking up-station (north), '
                    'Z = elevation - 730 ft; GLB (X, Z, -Y)',
        resolved=[dict(
            id='S03', finding='The MSE walls were two straight 0.6 ft envelopes across the bridge width only, with '
                              'square ends and 2 ft box copings 1.3-1.5 ft too high; nothing retained the sides of the '
                              'approach embankment; the monuments stood inside the wall line, overlapping the '
                              'envelopes (0.41-0.47 m3) and copings (0.12 m3), and the monument A, B, C and D footings '
                              'overlapped the outer end-bent piles or the end wall.',
            verdict='RESOLVE', parts=changed + added,
            correction='End walls 54A / 56A rebuilt as drawn (rear face 4\'-5 1/4" from CL Bent, 8 1/2" panel, '
                       'stepped pad tops, top at the coping underside); copings rebuilt 1\'-7" x 2\'-0" on the drawn '
                       'top slope, ending 1/2" from the monuments; side walls 54, 55, 56 and 57 added (rear face '
                       '24\'-4 1/4" from Line M, drawn top of wall and pad steps, low corner pieces under the coping) '
                       'from the end walls to the approach-slab pavement-end line; monuments moved out against the '
                       'side walls\' outer face (1\'-6" thick, rusticated face 26\'-6 3/4" from Line M); footings placed '
                       'by the sheet 73 offset table.',
            sources='sheets 12-13 (MSE wall lengths), 20-23 (wall plans and elevations), 24 (walls 54A / 56A '
                    'elevations, Sections A-A and B-B, notes), 40 (general plan), 41 (longitudinal section), 64 (PDF '
                    '63, monument front and side elevations), 73 (PDF 72, monument table, footing offset table, '
                    'Section E-E)',
            verification=dict(overlap_pairs_checked=values['overlap_pairs_checked'], contacts=values['contacts'],
                              side_wall_top_clearance_mm=values['side_wall_top_clearance_mm']))],
        decisions=[
            dict(id='S03-extent', decision='The side walls are modelled from the end walls to the approach-slab '
                                          'pavement-end line (X = +/-43.737 m), the model\'s approach extent; the '
                                          'drawn walls continue to STA 7+00 / 4+50 (west) and 22+50 / 23+74 (east).',
                 reasoning='The approach slabs and moment slabs, which the walls carry, end there; the roadway beyond '
                           'is outside the model.'),
            dict(id='S03-pads', decision='Panel bottoms on the top of the leveling pad: the sheet 24 values for the '
                                        'end walls, and the side-wall labels at the pad steps plus 0.50 ft.',
                 reasoning='The 6 in pads are drawn as double lines; measured on the vector drawing (1/8" = 1\'-0", 9 '
                           'pt per ft) the step labels on sheets 20-23 point to the lower line (e.g. 11+60-11+50 on '
                           'Wall 54: lines at El. 748.50 and 748.00, label 748.00; 11+20-10+90: 752.50 / 752.00 labelled '
                           'at either end). At the corners the side-wall labels 739.74 / 739.97 / 737.43 / 737.17 are '
                           'exactly 0.50 ft under the sheet 24 values 740.24 / 740.47 / 737.93 / 737.67, which equal the '
                           'monument base elevations G of the sheet 73 table (top of the strip footing on sheet 64).'),
            dict(id='S03-NW-pad', decision='North-west corner pad top El. 740.25 (monument A, G) instead of 740.24 '
                                          '(sheet 24).',
                 reasoning='The panels stand on the monument A footing there; 0.01 ft (3 mm).'),
            dict(id='S03-coping', decision='Coping modelled as a solid 19 x 24 in block with the panel stopping at its '
                                          'underside.',
                 reasoning='Same outside shape and total volume as the drawn U-section straddling the panel top (5 1/4" '
                           'legs + 8 1/2" panel = 1\'-7"); the panel inside the legs is counted in the coping, as in the '
                           'previous model.'),
            dict(id='S03-corner-tops', decision='The low corner pieces of the side walls (2\'-10", 1\'-8", 2\'-6", '
                                               '2\'-8") are set to the end-wall coping top labelled at the corner '
                                               '(759.11, 759.28, 758.98, 758.79) and cut under the coping band.',
                 reasoning='The wall elevations label these tops with the end-wall coping-top values but draw them 0.4-1.1 '
                           'ft higher; the labels control. The monuments cover the corner pieces on the outside.'),
            dict(id='S03-monuments', decision='Monuments moved out against the side walls (inner face 25\'-0 3/4", '
                                             'rusticated face 26\'-6 3/4" from Line M, 1\'-6" thick); footings by the '
                                             'sheet 73 offset table (edge 23\'-10" from Line M toward the bridge, P to '
                                             'Q).',
                 reasoning='Sheet 64 and Section E-E place the monument on the outer face of the side-wall panel '
                           '(2\'-2 1/2" for panel and monument); the coping terminates against it. The previous position '
                           '(24\'-2 3/4"-25\'-11 3/4") is the side-wall panel itself. Reading the footing offset 23\'-10" '
                           'as the inner edge (W = 4\'-3" = 1\'-6" outside the monument + monument + panel + 6 1/4") '
                           'matches the sheet 64 front elevation and clears the end-bent piles; read as the centre (the '
                           'previous model) the footing ran under the piles and the monument overhung it.'),
            dict(id='S03-sources', decision='No source_refs added.',
                 reasoning='This bridge has a single source (drawings.pdf, no source_index.json); its parts carry '
                           'pdf_pages only.'),
        ],
        kept_deviations=[],
        changed_parts=changed, added_parts=added, removed_parts=[],
        values=values,
        before_glb_sha256=before, after_glb_sha256=hashlib.sha256(out).hexdigest(),
        before_manifest_sha256=hashlib.sha256(raw_manifest).hexdigest())
    print(f'{len(changed)} parts changed, {len(added)} added; {len(manifest["parts"])} parts')
    print(json.dumps(values['volumes_m3']))
    print(json.dumps(values['overlaps_m3_removed_before_after']))
    print(json.dumps(values['overlaps_m3_remaining_before_after']))
    if dry_run:
        print('Dry run, nothing written.')
        return
    backup = ROOT / 'data/fem_research'
    backup.mkdir(exist_ok=True)
    (backup / f'{BID}_before_3d_review_2.glb').write_bytes(original)
    (backup / f'{BID}_manifest_before_3d_review_2.json').write_bytes(raw_manifest)
    path.write_bytes(out)
    text = json.dumps(manifest, ensure_ascii=False, indent=2) + '\n'
    if b'\r\n' in raw_manifest:                    # keep the file's existing CRLF line endings
        text = text.replace('\n', '\r\n')
    mp.write_bytes(text.encode('utf-8'))
    print(json.dumps({k: v for k, v in manifest[RECORD_KEY].items()
                      if k not in ('resolved', 'decisions', 'changed_parts', 'values')}))


if __name__ == '__main__':
    correct(dry_run='--dry-run' in sys.argv)

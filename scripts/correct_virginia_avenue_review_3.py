"""Third round for Virginia Avenue over I-65 NB / I-70 EB: the two known deviations left after the second review round,
preserving unrelated GLB buffers.

    python scripts/correct_virginia_avenue_review_3.py

Runs after scripts/correct_virginia_avenue_review.py and scripts/correct_virginia_avenue_review_2.py (manifest
review_correction_2 'haunch-crown-mudwall-pejf-end-frame-copes', revision 1.2-review-corrections-2, GLB SHA-256
a7efc0e5...). It requires that exact GLB, rebuilds the affected geometry with the first script's build(True) (which the
second round left unchanged for these parts) and checks it against the GLB, then replaces one mesh and adds fourteen.

Primary set: INDOT B-44576 (document 9683637, drawings.pdf); printed sheet numbers equal PDF page numbers. Historical
set: existing plans 9548460 (1971 Indiana State Highway Commission set: Framing Plan S-7 = PDF 65, Steel Details S-8 =
PDF 66, Steel Details S-9 = PDF 67). Native axes: X increasing station (X = 0 at 13+48.31 "Vir"), Y positive to the left
looking up-station (south side, Girder 1 at Y = +9.2964), Z up.

end-struts-bays-2-8 (existing S-7, S-8, S-9; primary sheets 31, 38): the labels E.S.1 / E.S.2 (Abutment 1, "Exp.") and
F.S.1 / F.S.2 (Abutment 2, "Fixed") on the S-7 framing plan bracket girder groups (1-2 and 8-9 = type 2, 3-7 = type 1);
they are the expansion and fixed SHOES detailed on S-9 (ES-1, ES-2 rockers, FS-1, FS-2), not end struts, and they are
already represented by the bearing envelopes. The members that do lie on both bearing lines of bays 2-8 are the jacking
frames: S-7 labels "J.F.1 (Typ.)" in the 7 ft 11 in bays and "J.F.2" in the 6 ft 9 in bay 8 at both abutments, and the
S-8 "Conn. PL Detail - J.F.1, 2 & E.D.1" puts the frame centre line on the centre line of the top shoes. S-8 "Jacking
Frame J.F.1 & 2": built-up I with a PL 1/2 in x 42 in web and PL 5/8 in x 9 in top and bottom flanges, bolted through a
1/2 in bent connection plate that runs 3 in (Typ.) off the girder web and is welded to the 7/8 in bearing stiffener. Bay
1 held E.D.1, which the 2013 Girder 1 replacement superseded with the end cross-frames already modelled. Primary sheet 38
(typical sections at Abutments 1 and 2) still shows the existing frame under the 2026 deck, and sheet 31 jacks the
beams at Abutment 1 without removing it. Fourteen parts are added, jacking_frame_B{1,2}_{2..8}.
DECISION: no sheet dimensions the frame's height on the girder web. The S-8 elevation, drawn with the frame-to-girder
depth ratio of 43.25 / 62.5 in to within 1 %, scales the frame top 4.9-5.5 in below the girder top and the bottom
13.3-14.0 in above the girder bottom; the frame is modelled 5 1/4 in below the top of each girder (14 in above the
bottom). Sheet 38 shows the existing steel only as a background sketch (girder drawn 60 in instead of 62.5 in overall);
it scales about 7.8 in and is not used. The frame ends are cut parallel to the girder webs 3 in from the web centre line,
at the S-8 offset of the connection-plate leg along the web. That is an envelope of the frame and its bent connection
plates: S-8 does not dimension where the frame itself ends, so this stays a known deviation
(jacking-frame-end-connections). Like the 2013 end frames, the frame follows the girder tops between its two girders.
Each frame mesh also carries the two S-8 centre stiffeners ("7/8 x 4 1/4 in Stiff. PL (Ea. Side)" on the jacking-frame
centre line, midway between the girders), one each side of the web between the flanges (28 plates, no new part ids);
4 1/4 in = (9 - 1/2) / 2 reaches the flange edges, which settles the hard-to-read fraction. Not added: the bent
1/2 x 7 in connection plates and their bolts (S-8 gives the plate size, the 3 in offset and the 3 in bolt spacing but
not the leg lengths, bend or height) and the 7/8 x 9 5/8 in bearing stiffeners (located on the bearing centre line, but
they would pass through the frame-end envelope, 61.7 cm3 per frame end, and through the 2013 end-frame W16 copes,
56.3 cm3 at Girder 2, whose real copes are measured from those stiffeners and are not dimensioned for the 1971 frames).

drain-station-abutment-2 (sheet 36 plan, "Roadway Drain Type SQ-A +87.50"; the CAD plan scales the grate centre at
Sta. 13+87.50 to 0.01 ft): the SQ-A inlet centre moves from X = +12.190 m (Sta. 13+88.30, the generator's 3 ft from the
bearing line) to X = +11.945 m. The transverse offset (0.2 m off the south curb) and the nominal inlet box are kept.

Drain routing (independent check of round 3; sheet 39, Bridge Drainage System Elevation and Details - Abutment No. 2):
the generator's straight visual collector ran from the downpipe to the north end of the bearing line, through
B2_bearing_6-9, at a 0.484 % fall. Sheet 39 hangs the 6 in downpipe from the inlet to a reducer and elbow just under the
top of the abutment wall, runs the 6 in RTRP collector on pipe support straps along the face of the abutment wall at
0.5 % min. to the north end, and drops it down the wall face to existing grade; Section K-K draws downpipe, reducer and
collector on one centre line. The drain is rebuilt that way. Sheet 39 is not to scale, so three values are decisions:
the collector centre line is the downpipe's (0.220 m normal to the face of the abutment_2 envelope, set by the inlet),
the pipe top is at the top of the wall at the south elbow and the run falls exactly 0.5 %, and the north drop ends at the
foot of the wall envelope (z 0.65 m), because the model has no existing grade.

source_ledger.json records neither value, so it is unchanged.

Requires numpy, trimesh, shapely and manifold3d.
"""
import hashlib
import json
import struct
import sys
from pathlib import Path

import numpy as np
import trimesh as tm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import correct_virginia_avenue_review as first  # noqa: E402  (also installs its triangulation / graph fallbacks)
import correct_virginia_avenue_review_2 as second  # noqa: E402
from bridge_geometry import FT, IN, box, rod, sweep, concat, iform  # noqa: E402

BID = first.BID
BASE = ROOT / 'data/bridges' / BID
TAG = 'jacking-frames-drain-station'
REVISION = '1.3-deviations'
BEFORE_SHA = 'a7efc0e5de68331cc9390ae8ebd024acdd82e9611a153881eeddf774630b142b'
RESOLVED = ['end-struts-bays-2-8', 'drain-station-abutment-2']

SLAB, SPAN, WIDTH = first.SLAB, first.SPAN, first.WIDTH
CLEAR = .05                                  # model rule: girder top 50 mm below the deck soffit
GIRDER_Y = [float(-y) for y in first.GIRDER_Y_OLD]          # +9.2964 (Girder 1) ... -9.2964 (Girder 9)
GIRDER_WEB = .625 * IN                       # 60 x 5/8 in web, girders 2-9 (existing S-7)

JF_WEB_T, JF_WEB_D = .5 * IN, 42 * IN        # existing S-8 Jacking Frame J.F.1 & 2: PL 1/2 x 42 in web
JF_FLANGE_B, JF_FLANGE_T = 9 * IN, .625 * IN  # PL 5/8 x 9 in, top and bottom
JF_DEPTH = JF_WEB_D + 2 * JF_FLANGE_T        # 43.25 in
JF_TOP_DROP = 5.25 * IN                      # decision: scaled from the S-8 elevation (not dimensioned)
JF_END = 3 * IN                              # S-8 Conn. PL detail: bent 1/2 in plate 3 in (Typ.) off the girder web
JF_STIFF_T, JF_STIFF_W = .875 * IN, 4.25 * IN  # S-8: 7/8 x 4 1/4 in Stiff. PL (Ea. Side) on the jacking-frame centre line
JF_BAYS = range(2, 9)                        # S-7: J.F.1 bays 2-7 (7 ft 11 in), J.F.2 bay 8 (6 ft 9 in)
JF_IDS = [f'jacking_frame_B{bi}_{b}' for bi in (1, 2) for b in JF_BAYS]

DRAIN_STATION = 1387.50                      # sheet 36: Roadway Drain Type SQ-A, +87.50
DRAIN_X = (DRAIN_STATION - first.STATION_0) * FT
DRAIN_X_OLD = 12.190012                      # generator: 3 ft from the Abutment 2 bearing line (Sta. 13+88.30)
COLLECTOR_CLASH_BEFORE = {'deck', 'B2_bearing_6', 'B2_bearing_7', 'B2_bearing_8', 'B2_bearing_9'}
PIPE_R = 3 * IN                              # sheet 39: 6 in dia. RTRP (downpipe and collector)
COLLECTOR_SLOPE = .005                       # sheet 39: 0.5 % min. fall to the north
WALL_FACE_U = SPAN / 2 - 2 * FT / np.cos(np.radians(first.SKEW))   # front face of the 4 ft abutment_2 envelope (skew u)
WALL_FOOT = .65                              # bottom of the abutment_2 envelope (top of the footing envelope)
JF_END_ID = 'jacking-frame-end-connections'


def b2_seat(m):
    """Abutment 2 seat datum = top of the abutment_2 wall envelope (first script: lowest B2 bearing)."""
    return min(c['seat_m'] for c in m.contacts if c['id'].startswith('B2_'))


def drain(m, x=None, wall_route=False):
    """drain_abutment_2. x = inlet centre station X (None: the generator's 3 ft rule).

    wall_route=False: the first script's straight visual collector. wall_route=True: sheet 39 routing; the downpipe drops
    from the inlet to an elbow under the top of the abutment wall, the 6 in collector runs along the wall face on the
    downpipe centre line (Section K-K) falling 0.5 % to the north end, then drops down the wall face to its foot."""
    y = 15 * FT - .2                         # first script: Y(-15 ft + 0.2 m) after the transverse mirror
    if x is None:
        x = m.sx(SPAN / 2 - 3 * FT, y)
    z = m.surface(x, y)
    inlet = box(x - .22, x + .22, y - .18, y + .18, z - .15, z + .015)
    if not wall_route:
        far = -WIDTH / 2
        return concat([inlet, rod([x, y, z - .1], [x, y, z - 2.0], PIPE_R),
                       rod([x, y, z - 2], [m.sx(SPAN / 2, far), far, z - 2.10], PIPE_R)])
    u_pipe = x - m.k * y                                     # pipe centre line parallel to the skewed wall face
    zs = b2_seat(m) - PIPE_R                                 # decision: pipe top at the top of the wall at the elbow
    yn = -WIDTH / 2                                          # north end: the generator's end (north deck edge)
    xn = m.sx(u_pipe, yn)
    zn = zs - COLLECTOR_SLOPE * float(np.hypot(xn - x, yn - y))
    return concat([inlet, rod([x, y, z - .1], [x, y, zs], PIPE_R), rod([x, y, zs], [xn, yn, zn], PIPE_R),
                   rod([xn, yn, zn], [xn, yn, WALL_FOOT], PIPE_R)])


def collector_geometry(m, x):
    """Plan/elevation facts of the wall-face route, for the record."""
    y = 15 * FT - .2
    u_pipe = x - m.k * y
    zs = b2_seat(m) - PIPE_R
    yn = -WIDTH / 2
    xn = m.sx(u_pipe, yn)
    length = float(np.hypot(xn - x, yn - y))
    return dict(south_elbow_centre_m=[round(x, 6), round(y, 6), round(zs, 6)],
                north_elbow_centre_m=[round(xn, 6), round(yn, 6), round(zs - COLLECTOR_SLOPE * length, 6)],
                run_length_m=round(length, 6), fall_m=round(COLLECTOR_SLOPE * length, 6), slope=COLLECTOR_SLOPE,
                centre_line_to_wall_face_normal_m=round((WALL_FACE_U - u_pipe) * float(np.cos(np.radians(first.SKEW))), 6),
                drop_foot_z_m=WALL_FOOT, wall_top_z_m=round(b2_seat(m), 6))


def jacking_frame(m, bi, b):
    """J.F. on bearing line bi (1, 2) in bay b, between Girder b and Girder b + 1."""
    u = (-1 if bi == 1 else 1) * SPAN / 2
    ya, yb = GIRDER_Y[b - 1], GIRDER_Y[b]
    pa = np.array([m.sx(u, ya), ya, 0.0])
    pb = np.array([m.sx(u, yb), yb, 0.0])
    top_a = m.surface(m.sx(u, ya), ya) - SLAB - CLEAR          # tops of the two girders at the bearing line
    top_b = m.surface(m.sx(u, yb), yb) - SLAB - CLEAR
    line = pb - pa
    normal = np.array([-line[1], line[0], 0.0]) / np.linalg.norm(line[:2])

    def fn(s, v, z):
        p = pa + s * line
        zt = top_a + s * (top_b - top_a) - JF_TOP_DROP
        return (p[0] + v * normal[0], p[1] + v * normal[1], zt - JF_DEPTH + z)
    raw = sweep(iform(JF_DEPTH, JF_FLANGE_B, JF_WEB_T, JF_FLANGE_T), [-.1, 1.1], fn)   # overrun, then cut at the webs
    lo, hi = sorted([ya, yb])
    frame = second.cope(raw, lo + JF_END, hi - JF_END)
    # S-8: a 7/8 x 4 1/4 in stiffener plate each side of the web on the frame centre line (the jacking point, midway
    # between the girders), between the flanges; the 4 1/4 in reaches the 9 in flange edges from the 1/2 in web.
    half = JF_STIFF_T / 2 / float(np.linalg.norm(line[:2]))        # parameter s per plan metre along the frame
    stiffeners = [sweep([(v0, JF_FLANGE_T), (v1, JF_FLANGE_T), (v1, JF_DEPTH - JF_FLANGE_T), (v0, JF_DEPTH - JF_FLANGE_T)],
                        [.5 - half, .5 + half], fn)
                  for v0, v1 in ((JF_WEB_T / 2, JF_WEB_T / 2 + JF_STIFF_W), (-JF_WEB_T / 2 - JF_STIFF_W, -JF_WEB_T / 2))]
    plate = JF_STIFF_T * JF_STIFF_W * (JF_DEPTH - 2 * JF_FLANGE_T)
    if any(abs(st.volume - plate) > 1e-9 for st in stiffeners) or frame.volume <= 0:
        raise ValueError('jacking-frame stiffener not as intended')
    mesh = concat([frame] + stiffeners)
    spacing = abs(ya - yb)
    dims = dict(frame='J.F.1' if b < 8 else 'J.F.2', web='PL 1/2 x 42 in', flanges='PL 5/8 x 9 in top and bottom',
                total_depth_m=round(JF_DEPTH, 5), top_below_girder_top_m=round(JF_TOP_DROP, 5),
                top_below_girder_top_basis='scaled from existing S-8 (not dimensioned)',
                end_cut='parallel to girder webs', end_offset_from_girder_web_centre_m=round(JF_END, 4),
                centre_stiffeners='2 x PL 7/8 x 4 1/4 in, one each side of the web on the frame centre line, '
                                  'between the flanges (S-8)',
                centre_stiffener_m=dict(thickness=round(JF_STIFF_T, 6), projection=round(JF_STIFF_W, 5),
                                        height=round(JF_DEPTH - 2 * JF_FLANGE_T, 5)),
                girder_spacing_m=round(spacing, 6),
                along_bearing_line_m=round((spacing - 2 * JF_END) * float(np.hypot(1.0, m.k)), 6))
    return mesh, dims, (ya, yb, top_a, top_b)


def inlet_centre(mesh):
    """Plan centre of the SQ-A inlet box: its top face is the highest part of the drain mesh."""
    v = mesh.vertices
    top = v[v[:, 2] > v[:, 2].max() - 1e-5]
    return top[:, :2].mean(axis=0)


def frame_checks(mesh_of, geometry):
    """Measured on actual triangles: girder tops at the bearing line, frame top drop below the line joining them and
    frame depth 1 in inside each end cut (on the frame centre line), and end clearance to the girder web faces."""
    tan = np.tan(np.radians(first.SKEW))
    res = {}
    for pid in JF_IDS:
        f = mesh_of(pid)
        ya, yb, _, _ = geometry[pid]
        bi = int(pid.split('_B')[1][0])
        b = int(pid.rsplit('_', 1)[1])
        u = (-1 if bi == 1 else 1) * SPAN / 2
        tops = {yg: float(second.z_hits(mesh_of(f'beam_{g}'), u - tan * yg, yg).max()) for g, yg in ((b, ya), (b + 1, yb))}
        out = {}
        for g, yg, yo in ((b, ya, yb), (b + 1, yb, ya)):
            yp = yg + np.sign(yo - yg) * (JF_END + 1 * IN)
            zf = second.z_hits(f, u - tan * yp, yp)
            girder_line = tops[ya] + (yp - ya) / (yb - ya) * (tops[yb] - tops[ya])
            out[f'girder_{g}'] = dict(girder_top_m=round(tops[yg], 6),
                                      frame_top_below_girder_tops_m=round(float(girder_line - zf.max()), 6),
                                      frame_depth_m=round(float(zf.max() - zf.min()), 6))
        v = f.vertices
        out['end_clearance_to_web_face_m'] = [round(float(np.abs(v[:, 1] - yg).min() - GIRDER_WEB / 2), 6) for yg in (ya, yb)]
        res[pid] = out
    return res


def correct():
    mp = BASE / 'model_manifest.json'
    raw_manifest = mp.read_bytes()
    manifest = json.loads(raw_manifest.decode('utf-8'))
    newline = '\r\n' if b'\r\n' in raw_manifest else '\n'     # keep the working-tree line endings
    if manifest.get('review_correction_3') == TAG:
        print('Already corrected.')
        return
    if manifest.get('review_correction_2') != second.TAG or manifest.get('revision') != second.REVISION:
        raise ValueError('Run scripts/correct_virginia_avenue_review_2.py first (expected revision 1.2-review-corrections-2).')
    path = BASE / 'model.glb'
    original = path.read_bytes()
    before = hashlib.sha256(original).hexdigest()
    if before != BEFORE_SHA:
        raise ValueError(f'model.glb is not the expected revision 1.2 artifact (SHA-256 {before})')
    length = struct.unpack_from('<I', original, 12)[0]
    gltf = json.loads(original[20:20 + length])
    binary = bytearray(original[28 + length:])
    parts = {p['id']: p for p in manifest['parts']}
    meshes = {m['name']: m for m in gltf['meshes']}
    if len(parts) != 148 or set(parts) != set(meshes) or any(pid in parts for pid in JF_IDS):
        raise ValueError('Unexpected part set; the model is not the expected revision.')
    have = {d.get('id') for d in manifest.get('known_deviations', [])}
    if not set(RESOLVED) <= have:
        raise ValueError(f'expected known_deviations {RESOLVED}, found {sorted(have)}')

    def read(ai):
        a = gltf['accessors'][ai]
        view = gltf['bufferViews'][a['bufferView']]
        dtype = {5126: '<f4', 5125: '<u4', 5123: '<u2', 5121: 'u1'}[a['componentType']]
        count = {'SCALAR': 1, 'VEC3': 3, 'VEC4': 4}[a['type']]
        return np.frombuffer(binary, dtype=dtype, count=a['count'] * count,
                             offset=view.get('byteOffset', 0) + a.get('byteOffset', 0)).copy().reshape(-1, count)

    def glb_mesh(pid):
        prim = meshes[pid]['primitives'][0]
        v = read(prim['attributes']['POSITION']).astype(np.float64)
        return tm.Trimesh(np.column_stack([v[:, 0], -v[:, 2], v[:, 1]]), read(prim['indices']).reshape(-1, 3), process=False)

    # Starting state: the parts this round builds on must be the review-1.1 reconstruction (round 2 did not touch them).
    current, m = first.build(True)
    for pid in ['drain_abutment_2', 'deck'] + [f'beam_{j}' for j in range(1, 10)]:
        if not second.first_same(glb_mesh(pid).vertices, current[pid][0].vertices):
            raise ValueError(f'{pid}: GLB geometry differs from the review-1.1 reconstruction')
    if not second.first_same(drain(m).vertices, current['drain_abutment_2'][0].vertices):
        raise ValueError('drain reconstruction does not reproduce the GLB')
    c_before = inlet_centre(glb_mesh('drain_abutment_2'))
    if abs(c_before[0] - DRAIN_X_OLD) > 1e-4 or abs(c_before[1] - (15 * FT - .2)) > 1e-4:
        raise ValueError(f'unexpected drain inlet centre {c_before}')
    wall = glb_mesh('abutment_2').vertices                       # the wall face, top and foot the new route follows
    wall_u = wall[:, 0] - m.k * wall[:, 1]
    if (abs(wall_u.min() - WALL_FACE_U) > 1e-5 or abs(wall[:, 2].min() - WALL_FOOT) > 1e-5 or
            abs(wall[:, 2].max() - b2_seat(m)) > 1e-5):
        raise ValueError('abutment_2 face / foot / top not as the first script builds them')

    new, dims, geometry = {}, {}, {}
    new['drain_abutment_2'] = drain(m, DRAIN_X, wall_route=True)
    route = collector_geometry(m, DRAIN_X)
    for bi in (1, 2):
        for b in JF_BAYS:
            pid = f'jacking_frame_B{bi}_{b}'
            new[pid], dims[pid], geometry[pid] = jacking_frame(m, bi, b)

    # Contacts, measured with manifold3d intersections against every part whose bounds touch the new mesh.
    def neighbours(mesh, pool, skip=()):
        lo, hi = mesh.bounds
        for pid in pool:
            if pid in skip:
                continue
            b = np.array(parts[pid]['bounds_m'])
            if (b[0] <= hi + 1e-6).all() and (b[1] >= lo - 1e-6).all():
                yield pid
    overlaps_before = {p: round(second.overlap_cm3(glb_mesh('drain_abutment_2'), glb_mesh(p)), 3)
                       for p in neighbours(glb_mesh('drain_abutment_2'), parts, ('drain_abutment_2',))}
    overlaps_after = {}
    for pid in ['drain_abutment_2'] + JF_IDS:
        mesh = new[pid]
        mesh.remove_unreferenced_vertices()
        mesh.fix_normals(multibody=True)
        if not mesh.is_watertight or mesh.volume <= 0:
            raise ValueError(f'{pid}: invalid solid')
        found = {}
        for q in neighbours(mesh, parts, (pid,)):
            found[q] = round(second.overlap_cm3(mesh, glb_mesh(q)), 3)
        for q in [p for p in JF_IDS if p != pid and p in new]:
            if (new[q].bounds[0] <= mesh.bounds[1]).all() and (new[q].bounds[1] >= mesh.bounds[0]).all():
                found[q] = round(second.overlap_cm3(mesh, new[q]), 3)
        overlaps_after[pid] = {q: v for q, v in found.items()
                               if v > 0 or q.split('_')[0] in ('beam', 'abutment', 'B2', 'footing', 'wing', 'seat')}
    # Starting drain: embedded in the deck (the inlet box stands in the slab) and its straight collector through
    # B2_bearing_6-9. After: the jacking frames touch nothing; the re-routed drain keeps only the deck embedment.
    if set(q for q, v in overlaps_before.items() if v > 1e-3) != COLLECTOR_CLASH_BEFORE:
        raise ValueError(f'unexpected starting drain overlaps {overlaps_before}')
    for pid in JF_IDS:
        bad = {q: v for q, v in overlaps_after[pid].items() if v > 1e-3}
        if bad:
            raise ValueError(f'{pid} overlaps {bad}')
    after_drain = {q: v for q, v in overlaps_after['drain_abutment_2'].items() if v > 1e-3}
    if set(after_drain) != {'deck'} or abs(after_drain['deck'] - overlaps_before['deck']) > 5.0:
        raise ValueError(f'drain overlaps not as expected: {after_drain}')

    cache = {}

    def append(array, kind, component):
        data = array.tobytes()
        key = (kind, component, len(array), hashlib.sha256(data).hexdigest())
        if key in cache:
            return cache[key]
        while len(binary) % 4:
            binary.append(0)
        view = len(gltf['bufferViews'])
        gltf['bufferViews'].append(dict(buffer=0, byteOffset=len(binary), byteLength=len(data)))
        binary.extend(data)
        a = dict(bufferView=view, componentType=component, count=len(array), type=kind)
        if kind == 'VEC3':
            a.update(min=array.min(axis=0).tolist(), max=array.max(axis=0).tolist())
        gltf['accessors'].append(a)
        cache[key] = len(gltf['accessors']) - 1
        return cache[key]

    for ai, a in enumerate(gltf['accessors']):      # reuse identical colour / index arrays
        if a['type'] in ('SCALAR', 'VEC4'):
            arr = read(ai)
            cache.setdefault((a['type'], a['componentType'], len(arr), hashlib.sha256(arr.tobytes()).hexdigest()), ai)

    def primitive(mesh, color):
        rgb = [int(color[n:n + 2], 16) for n in (1, 3, 5)] + [255]
        prim = dict(attributes=dict(POSITION=append(second.to_gltf(mesh.vertices).astype('<f4'), 'VEC3', 5126),
                                    COLOR_0=append(np.tile(np.array(rgb, 'u1'), (len(mesh.vertices), 1)), 'VEC4', 5121)),
                    indices=append(mesh.faces.reshape(-1, 1).astype('<u4'), 'SCALAR', 5125), mode=4)
        gltf['accessors'][prim['attributes']['COLOR_0']]['normalized'] = True
        return prim

    meta_keys = ('id', 'name', 'layer', 'color', 'pdf_pages', 'basis', 'note', 'dimensions')
    old_drain = dict(bounds_m=parts['drain_abutment_2']['bounds_m'], volume_m3=parts['drain_abutment_2']['volume_m3'],
                     inlet_centre_xy_m=np.round(c_before, 6).tolist(), inlet_station='13+88.30')

    # Changed: drain_abutment_2 (mesh replaced in place, node unchanged).
    p = parts['drain_abutment_2']
    mesh = new['drain_abutment_2']
    prim = primitive(mesh, p['color'])
    if meshes['drain_abutment_2']['primitives'][0].get('material') is not None:
        prim['material'] = meshes['drain_abutment_2']['primitives'][0]['material']
    meshes['drain_abutment_2']['primitives'] = [prim]
    old_sentence = ('Collector is a straight visual run below the girders; elbows, hangers, cleanouts and deck penetrations '
                    'are simplified.')
    if old_sentence not in p['note']:
        raise ValueError('drain note not as expected')
    p['note'] = p['note'].replace(old_sentence, 'Downpipe, collector and north drop follow the sheet 39 routing along the '
                                  'Abutment 2 wall face; reducer, elbows, cleanout, straps, brackets and the deck '
                                  'penetration are simplified.')
    p['note'] += (' Review correction 1.3: SQ-A inlet centre moved to Sta. 13+87.50 (X = +11.945 m), the station on the '
                  'sheet 36 plan (was Sta. 13+88.30, 3 ft from the bearing line). Re-routed as sheet 39 draws it: the 6 in '
                  'downpipe drops from the inlet to an elbow under the top of the abutment wall, the 6 in RTRP collector '
                  'runs along the wall face on the downpipe centre line (Section K-K) to the north end at 0.5 % (the sheet '
                  'minimum), then drops down the wall face. Sheet 39 is not to scale, so by decision: centre line '
                  f'{route["centre_line_to_wall_face_normal_m"]:.3f} m off the wall face (set by the inlet position), pipe top '
                  'at the top of the wall at the south elbow, drop to the foot of the wall envelope (existing grade is not '
                  'modelled). The straight collector it replaces passed through B2_bearing_6-9.')
    p['dimensions'] = dict(p.get('dimensions') or {}, inlet_station='13+87.50', inlet_centre_x_m=round(DRAIN_X, 6),
                           inlet_centre_y_m=round(15 * FT - .2, 6), pipe_diameter_m=round(2 * PIPE_R, 4),
                           collector_slope=COLLECTOR_SLOPE, collector_run_length_m=route['run_length_m'],
                           collector_fall_m=route['fall_m'],
                           collector_centre_line_to_wall_face_m=route['centre_line_to_wall_face_normal_m'],
                           south_elbow_centre_z_m=route['south_elbow_centre_m'][2],
                           north_elbow_centre_z_m=route['north_elbow_centre_m'][2], north_drop_foot_z_m=WALL_FOOT)
    p['bounds_m'] = np.round(mesh.bounds, 6).tolist()
    p['volume_m3'] = round(float(mesh.volume), 9)
    meshes['drain_abutment_2'].setdefault('extras', {}).update({k: p[k] for k in meta_keys})

    # Added: fourteen jacking frames (new mesh, node under the scene root, manifest part).
    world = gltf['nodes'][gltf['scenes'][gltf.get('scene', 0)]['nodes'][0]]
    template = parts['end_cross_frame_B1_1']
    for pid in JF_IDS:
        mesh = new[pid]
        bi = int(pid.split('_B')[1][0])
        b = int(pid.rsplit('_', 1)[1])
        d = dims[pid]
        p = dict(
            id=pid, name=f'Bay {b} | Abutment {bi} jacking frame {d["frame"]} (1971, Girders {b}-{b + 1})',
            layer=template['layer'], color=template['color'], pdf_pages=[31, 38],
            basis='Existing plans 9548460 S-7 and S-8 (PDF 65, 66): Jacking Frame J.F.1 & 2 on the centre line of the top '
                  'shoes (bearing line), PL 1/2 x 42 in web and PL 5/8 x 9 in flanges; retained under the 2026 deck '
                  '(sheet 38 typical sections)',
            note='Top 5 1/4 in below the girder top, scaled from the S-8 elevation (the height on the web is not '
                 'dimensioned; the sheet 38 background sketch scales about 7.8 in); follows the two girder tops along the '
                 'bearing line. The ends are an envelope of the frame and its bent 1/2 x 7 in connection plates: the '
                 'section stops on vertical planes parallel to the girder webs 3 in from the web centre lines, the S-8 '
                 'offset of the plate leg along the web; S-8 does not dimension where the frame itself ends (see '
                 'known_deviations). Includes the two S-8 centre stiffeners, PL 7/8 x 4 1/4 in each side of the web on the '
                 'frame centre line between the flanges. Bent connection plates, bolts and the girder bearing stiffeners '
                 'are omitted. Review correction 1.3: added; the S-7 E.S.1 / E.S.2 and F.S.1 / F.S.2 labels on the bearing '
                 'lines are the expansion and fixed shoes of S-9, already represented by the bearings.',
            dimensions=d,
            source_refs=[dict(source_id='9683637', pdf_pages=[31, 38]), dict(source_id='9548460', pdf_pages=[65, 66])],
            bounds_m=np.round(mesh.bounds, 6).tolist(), volume_m3=round(float(mesh.volume), 9))
        gltf['meshes'].append(dict(name=pid, extras=dict(processed=True, **{k: p[k] for k in meta_keys}),
                                   primitives=[primitive(mesh, p['color'])]))
        meshes[pid] = gltf['meshes'][-1]
        gltf['nodes'].append(dict(name=pid, mesh=len(gltf['meshes']) - 1))
        world['children'].append(len(gltf['nodes']) - 1)
        manifest['parts'].append(p)
        parts[pid] = p

    by_layer = {q['id']: q['layer'] for q in manifest['parts']}
    for cov in manifest.get('detail_coverage', []):
        layers = {by_layer[i] for i in cov['part_ids'] if i in by_layer}
        if template['layer'] in layers:
            cov['part_ids'] += [i for i in JF_IDS if i not in cov['part_ids']]
        if cov['feature'] == 'Retained steel and bearings':
            cov['detail'] += (' 1971 jacking frames J.F.1 / J.F.2 on both bearing lines of bays 2-8 (existing S-7, S-8; '
                              'height on the web scaled; centre stiffeners included).')

    gltf['buffers'][0]['byteLength'] = len(binary)
    while len(binary) % 4:
        binary.append(0)
    encoded = json.dumps(gltf, ensure_ascii=True, separators=(',', ':')).encode()
    encoded += b' ' * ((-len(encoded)) % 4)
    out = (struct.pack('<III', 0x46546c67, 2, 28 + len(encoded) + len(binary)) +
           struct.pack('<II', len(encoded), 0x4e4f534a) + encoded + struct.pack('<II', len(binary), 0x004e4942) + binary)

    def out_mesh(pid):
        return new[pid] if pid in new else glb_mesh(pid)
    frames = frame_checks(out_mesh, geometry)
    for pid, r in frames.items():
        ends = [v for k, v in r.items() if k.startswith('girder_')]
        if (abs(min(r['end_clearance_to_web_face_m']) - (JF_END - GIRDER_WEB / 2)) > 1e-5 or
                any(abs(e['frame_top_below_girder_tops_m'] - JF_TOP_DROP) > 1e-4 or abs(e['frame_depth_m'] - JF_DEPTH) > 1e-4
                    for e in ends)):
            raise ValueError(f'{pid}: frame not as intended {r}')
    c_after = inlet_centre(new['drain_abutment_2'])
    if abs(c_after[0] - DRAIN_X) > 1e-6:
        raise ValueError(f'drain inlet centre {c_after}')

    backup = ROOT / 'data/fem_research'
    backup.mkdir(exist_ok=True)
    (backup / 'virginia_avenue_before_review_correction_3.glb').write_bytes(original)
    (backup / 'virginia_avenue_manifest_before_review_correction_3.json').write_bytes(mp.read_bytes())
    path.write_bytes(out)

    manifest['review_correction_3'] = TAG
    manifest['revision'] = REVISION
    manifest['review_correction_record_3'] = dict(
        source='Third round: the two known_deviations left after revision 1.2, each re-read against the drawings',
        source_pdf_pages=[31, 36, 38], printed_sheets=[31, 36, 38],
        historical_source=dict(source_id='9548460', pdf_pages=[65, 66, 67], printed_sheets=['S-7', 'S-8', 'S-9']),
        findings={
            'end-struts-bays-2-8': 'Resolved as jacking frames. E.S.1 / E.S.2 and F.S.1 / F.S.2 on S-7 are the expansion '
                                   'and fixed shoes of S-9 (already the bearing envelopes). Added J.F.1 (bays 2-7) and '
                                   'J.F.2 (bay 8) on both bearing lines: PL 1/2 x 42 in web, PL 5/8 x 9 in flanges, on the '
                                   'centre line of the top shoes (S-7, S-8), retained in 2026 (sheet 38). 14 parts, each '
                                   'with its two S-8 centre stiffeners PL 7/8 x 4 1/4 in (28 plates, part of the frame '
                                   'meshes).',
            'drain-station-abutment-2': 'SQ-A inlet centre X +12.190012 -> +11.945112 m (Sta. 13+88.30 -> 13+87.50, sheet '
                                        '36); the downpipe follows (-0.244900 m in X).',
            'drain collector routing (independent check of round 3)': 'Straight visual collector through B2_bearing_6-9 '
                                        '(30-11091 cm3 each) at a 0.484 % fall -> sheet 39 routing: downpipe to an elbow '
                                        'under the top of the wall, 6 in collector along the Abutment 2 wall face on the '
                                        'downpipe centre line, 0.5 % fall to the north end, drop down the wall face. '
                                        'Overlaps with bearings 0; only the inlet embedment in the deck remains.'},
        decisions={
            'jacking frame height on the girder web': 'Not dimensioned on any sheet. Modelled with the top 5 1/4 in below '
                                                      'the girder top (bottom 14 in above the girder bottom), scaled from '
                                                      'the S-8 Jacking Frame J.F.1 & 2 elevation, which is the member\'s '
                                                      'own detail and is drawn with the frame-to-girder depth ratio to '
                                                      'within 1 % (scaled 4.9-5.5 in / 13.3-14.0 in). Not used: the sheet '
                                                      '38 background sketch (about 7.8 in), which draws the girder 60 in '
                                                      'deep instead of 62.5 in. Expected uncertainty about +/-2.5 in.',
            'jacking frame ends': 'Kept as an envelope (see known_deviations jacking-frame-end-connections): the '
                                  'section stops on planes parallel to the girder webs 3 in from the web centre lines. On '
                                  'S-8 the 3 in (Typ.) locates the leg of the bent 1/2 in connection plate along the web, '
                                  'not the frame end; where the frame ends is not dimensioned.',
            'jacking frame centre stiffeners': 'S-8 "7/8 x 4 1/4 in Stiff. PL (Ea. Side)" at the jacking-frame centre line, '
                                               'read 4 1/4 in (not 4 1/2): (9 - 1/2) / 2 = 4 1/4 reaches the flange edges. '
                                               'Placed at mid-frame between the girder centre lines, the drawn centre line, '
                                               'full height between the flanges; built into each frame mesh.',
            'connection parts not added': 'The bent 1/2 x 7 in plates and bolts have no leg lengths, bend or height on S-8. '
                                          'The 7/8 x 9 5/8 in bearing stiffeners are located (bearing centre line, both '
                                          'sides of the web) but would intersect the frame-end envelope (61.7 cm3 per '
                                          'frame end) and the 2013 end-frame W16 at Girder 2 (56.3 cm3 per bearing line); '
                                          'fitting them needs the frame and end-frame copes, which no sheet dimensions. '
                                          'Kept in known_deviations jacking-frame-end-connections.',
            'drain collector offset from the wall face': 'Not dimensioned (sheet 39 not to scale). Section K-K draws the '
                                                         'downpipe, reducer and collector on one centre line against the '
                                                         'wall face, so the collector runs parallel to the skewed wall face '
                                                         'on the downpipe centre line: '
                                                         f'{route["centre_line_to_wall_face_normal_m"]:.4f} m normal to the '
                                                         'face of the abutment_2 envelope, set by the inlet position.',
            'drain collector elevation': 'Not dimensioned. Sheet 39 draws the elbow and run just under the top of the '
                                         'wall and below the girders; the pipe top is put at the top of the wall '
                                         f'(z {route["wall_top_z_m"]:.4f} m) at the south elbow, falling exactly 0.5 % (the '
                                         'minimum) to the north end.',
            'drain north drop': 'Sheet 39 drops the pipe down the wall face to existing grade, which the model does not '
                                'have; the drop ends at the foot of the abutment_2 envelope (z 0.65 m, top of the footing '
                                'envelope).'},
        changed_parts=['drain_abutment_2'], added_parts=JF_IDS, removed_parts=[],
        before=dict(drain_abutment_2=old_drain, drain_overlaps_cm3=overlaps_before),
        after=dict(drain_abutment_2=dict(bounds_m=parts['drain_abutment_2']['bounds_m'],
                                         volume_m3=parts['drain_abutment_2']['volume_m3'],
                                         inlet_centre_xy_m=np.round(c_after, 6).tolist(), inlet_station='13+87.50'),
                   collector=route, overlaps_cm3=overlaps_after, jacking_frames=frames),
        before_glb_sha256=before, after_glb_sha256=hashlib.sha256(out).hexdigest())
    deviations = [d for d in manifest.get('known_deviations', []) if d.get('id') not in RESOLVED + [JF_END_ID]]
    deviations.append(dict(
        id=JF_END_ID, parts=', '.join(JF_IDS),
        source='existing plans 9548460 S-8 (PDF 66): Jacking Frame J.F.1 & 2; Conn. PL Detail - J.F.1, 2 & E.D.1',
        deviation='The jacking-frame ends are an envelope. The I-section runs to vertical planes parallel to the girder '
                  'webs, 3 in (0.0762 m) from the web centre lines. The bent 1/2 x 7 in connection plates, their bolts '
                  '(two rows 3 in apart, 12 spa. @ 3 in) and the 7/8 x 9 5/8 in bearing stiffeners they are welded to are '
                  'not modelled. On S-8 the 3 in (Typ.) locates the plate leg along the girder web; the frame web is '
                  'bolted to the skewed leg of the plate, and where the frame itself ends is not shown.',
        reason='S-8 gives no dimension for the frame end along the bearing line, the plate leg lengths, bend or plate '
               'height, and the detail does not scale consistently (its 3 in, 4 1/2 in and bolt spacings scale '
               'differently). The bearing stiffeners are located on the bearing centre line, but they cannot be added '
               'alone: they would pass through the modelled frame ends (61.7 cm3 per frame end) and the 2013 end-frame '
               'W16 at Girder 2 (56.3 cm3 per bearing line), whose real copes are not dimensioned. Shop drawings or a '
               'field measurement of the end connection would settle it. The S-8 centre stiffeners are modelled.'))
    manifest['known_deviations'] = deviations
    mp.write_bytes((json.dumps(manifest, indent=2) + '\n').replace('\n', newline).encode('utf-8'))
    print(json.dumps(dict(changed=['drain_abutment_2'], added=JF_IDS, before=before,
                          after=manifest['review_correction_record_3']['after_glb_sha256'],
                          drain_inlet=dict(before=c_before.round(6).tolist(), after=c_after.round(6).tolist()),
                          collector=route, overlaps_after=overlaps_after, frames=frames), indent=1))


if __name__ == '__main__':
    correct()

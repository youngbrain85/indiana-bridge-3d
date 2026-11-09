"""Fourth round (3D review) of Virginia Avenue over I-65 NB / I-70 EB (virginia-avenue): the bay 1 intermediate
cross frames must not pass through Girder 1's bottom flange. Runs after scripts/correct_virginia_avenue_review_3.py
(manifest review_correction_3 'jacking-frames-drain-station', revision 1.3-deviations). Unrelated GLB buffers are
kept; new accessors are appended and five meshes are replaced. Part ids are unchanged; no part is added or removed.

    python scripts/correct_virginia_avenue_3d_review.py [--dry-run]

Sources: existing plans 9548460 (2013 Girder 1 replacement, northbound structure): printed sheet 10 = PDF 28 (Framing
Plan - N.B. and Girder Elevation) and printed sheet 14 = PDF 32 (Structural Steel Details: Intermediate Cross-Frame
Details, northbound structure). Native axes: X increasing station (X = 0 at 13+48.31 "Vir"), Y positive to the left
looking up-station (south side, Girder 1 at Y = +9.2964, Girder 2 at Y = +7.2390), Z up.

Finding VA-07 of the 3D review: the five bay 1 V frames (cross_frame_1_1..5, generator rule: common lower strut 4 ft
below a top 0.14 m under the lower girder top, 0.10 x 0.10 m bar) put the lower strut through Girder 1's bottom flange
(549-590 cm3 per frame; at frame 1 the strut runs from 13.2 mm below the flange soffit to 63 mm above it). Measured on
the same GLB, the twisted diagonal bars also cut 7.9 cm3 into the Girder 2 web at every frame, and frame 1 lay inside
the Splice "A" web cover plates of Girder 1 (38.3 cm3).

What the sheets draw, and what is modelled:
- Sheet 10 framing plan: the bay 1 frames are "4 Spaces @ 22'-0" = 88'-0" (Proposed Cross Frame Spacing)", 15'-3"
  from C/L bearing Abutment 1 and 10'-9" from C/L bearing Abutment 2, dimensioned along New Girder No. 1, square to the
  girders. The generator put them 15'-3" from the bearing line at mid-bay, 1.0045 m up-station of those stations, so
  frame 1 sat in the Splice "A" cover plates (sheet 10: 4'-9" ahead of the splice). The five frames move to the sheet 10
  stations.
- Sheet 14: L5x5x3/8 V diagonals and L5x5x3/8 bottom strut, bolted to a "7 in x 5/8 in Conn. PL" on each girder; the
  sheet 10 girder elevation draws the "5/8 in Cross Frame Connection PL (Typ.)" from flange to flange, and sheet 14
  welds it to both flanges (5/16 in fillets). Ten plates are modelled, two per frame and part of the frame mesh: 7 in
  from the web face, 5/8 in thick, centred on the frame station, from the top of the bottom flange to the underside of
  the top flange of each girder. The sheet 10 plan draws the frame line on the up-station side of the plate ticks, so
  the angles bear on the up-station face of the plates.
- Sheet 14: bottom strut "3 in Min." above the top of the bottom flange (dimensioned to Girder 2, the higher flange as
  drawn; in the model Girder 1's bottom flange is higher, so it governs) and top of the diagonals "6 in Min." below the
  underside of the top flange (dimensioned to Girder 1, the lower flange as drawn; in the model Girder 2's is lower).
  The detail is drawn at both minima and the frame is built to them, as the 2013 end frames were (revision 1.1).
- The angles are represented by their connected 5 in legs as 3/8 in strips in the frame plane (the existing
  convention "angle legs are represented by rectangular strips"); outstanding legs, bolts and welds are omitted. The
  member ends keep the generator's offset, vertical planes 0.02 m from the girder centre lines (12.06 mm clear of the
  5/8 in webs; sheet 14 does not dimension the angle ends, which scale about 1 in off the webs), so every member laps
  onto both connection plates.
- The 3/8 in gusset at the foot of the V is drawn but not dimensioned. It is not modelled: the two diagonals are carried
  down to the top of the bottom strut, where their centre lines meet at the bay centre (drawn within about 1 in of the
  strut top), and they meet each other on the bay centre plane, as one V-shaped body standing on the strut. Recorded in
  known_deviations bay1-intermediate-frame-gussets.

All new solids touch (connection plate on web and flanges, angles on plate faces, V on the strut); the largest
intersection with any part is about 1 mm3, the float32 rounding of those touching faces.
source_ledger.json (FEM input) records no cross-frame value and FEM excludes these parts, so neither is changed.

Requires numpy, trimesh, shapely and manifold3d; reuses the helpers of the earlier Virginia Avenue review scripts.
"""
import hashlib
import json
import struct
import sys
from pathlib import Path

import manifold3d as mf
import numpy as np
import trimesh as tm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import correct_virginia_avenue_review as first  # noqa: E402  (also installs its triangulation / graph fallbacks)
import correct_virginia_avenue_review_2 as second  # noqa: E402
import correct_virginia_avenue_review_3 as third  # noqa: E402
from bridge_geometry import FT, IN, box, sweep, concat  # noqa: E402
from refresh_geometry_verification import bodies  # noqa: E402  (its closed-mesh test, read only)
from shapely.geometry import Polygon  # noqa: E402
from shapely.ops import unary_union  # noqa: E402

BID = first.BID
BASE = ROOT / 'data/bridges' / BID
TAG_KEY = 'review_correction_3d'
TAG = 'bay1-intermediate-frames-conn-plates'
REVISION = '1.4-3d-review'
BEFORE_SHA = 'd802db50c458c6f6084c3f852e5ad35e3c837954a9f0481e9618be1a7811e2b0'   # revision 1.3 GLB
EXPECTED_DEVIATIONS = {third.JF_END_ID}
DEV_ID = 'bay1-intermediate-frame-gussets'
CHANGED = [f'cross_frame_1_{q}' for q in range(1, 6)]

SLAB, SPAN = first.SLAB, first.SPAN
CLEAR = .05                                  # model rule: girder top 50 mm below the deck soffit (haunch depth)
G_Y = (third.GIRDER_Y[0], third.GIRDER_Y[1])   # Girder 1 +9.2964, Girder 2 +7.2390 (after review 1.1)
WEB = .625 * IN                              # 5/8 in webs (existing sheets 10, 14; first script)
STATIONS_FT = [15.25 + 22 * q for q in range(5)]   # sheet 10: 15'-3" + 4 spa. @ 22'-0" from C/L brg. Abut. 1 (Girder 1)
LAST_TO_BRG_2_FT = 10.75                     # sheet 10: 10'-9" to C/L brg. Abut. 2 (Girder 1)
ANGLE_LEG, ANGLE_T = first.ANGLE_LEG, first.ANGLE_T   # sheet 14: L5x5x3/8 diagonals and bottom strut
CONN_W, CONN_T = 7 * IN, .625 * IN           # sheet 14: 7 in x 5/8 in Conn. PL; sheet 10: 5/8 in Cross Frame Conn. PL
BOTTOM_CLEAR = 3 * IN                        # sheet 14: bottom strut 3 in Min. above the top of the bottom flange
TOP_CLEAR = 6 * IN                           # sheet 14: top of diagonals 6 in Min. below the underside of the top flange
END = .02                                    # generator: member ends 0.02 m from the girder centre lines (kept)
OLD_PROBE = (-20.798676, 9.2)                # review VA-07 probe (viewer x, -z) through the frame 1 strut and flange
TOUCH = 2e-5                                 # contact tolerance (float32 storage near X = 25 m is about 2 um)
NO_OVERLAP_CM3 = .01                         # float32 slack on a touching face: < 1 um x 0.003 m2 = 0.003 cm3


# ------------------------------------------------------------------------------------------------- geometry
def zones(manifest_part):
    return manifest_part['dimensions']['section_zones']


def flange_faces(m, beam, j, x):
    """(top of bottom flange, underside of top flange) of Girder j + 1 at plan X, by the first script's rules: the
    top 50 mm below the deck soffit at the girder centre line, the section of the zone that holds u = X - k Y."""
    y = G_Y[j]
    u = x - m.k * y
    z = [q for q in zones(beam) if q['u0_m'] - 1e-9 <= u <= q['u1_m'] + 1e-9]
    if len(z) != 1:
        raise ValueError(f'frame station u = {u} is on a section-zone boundary of girder {j + 1}')
    top = m.surface(x, y) - SLAB - CLEAR
    return top - z[0]['total_depth_m'] + z[0]['flange_thickness_m'], top - z[0]['flange_thickness_m']


def v_angle(h, v, w):
    """Slope angle of the diagonal centre lines: the centre line passes through the work point (0, 0) and the upper
    edge (offset w / 2) through the top corner (h, v)."""
    r, a = np.hypot(h, v), np.arctan2(h, v)
    t = np.arccos(w / (2 * r)) - a
    if not 0 < t < np.pi / 2 or abs(v * np.cos(t) - h * np.sin(t) - w / 2) > 1e-12:
        raise ValueError('diagonal geometry')
    return t


def frame(m, beams, q):
    """Frame q (0..4): connection plates, bottom strut and V diagonals, plus the facts the record keeps."""
    x = m.sx(-SPAN / 2, G_Y[0]) + STATIONS_FT[q] * FT              # along Girder 1 from its Abutment 1 bearing
    xa, xb = x + CONN_T / 2, x + CONN_T / 2 + ANGLE_T              # angles on the up-station face of the plates
    faces = {j: [flange_faces(m, beams[j], j, xx) for xx in (xa, xb)] for j in (0, 1)}
    z_strut = max(f[0] for j in (0, 1) for f in faces[j]) + BOTTOM_CLEAR
    z_top = min(f[1] for j in (0, 1) for f in faces[j]) - TOP_CLEAR
    z_work = z_strut + ANGLE_LEG                                   # V work point: bay centre on the strut top
    y_mid = (G_Y[0] + G_Y[1]) / 2
    ends = (G_Y[0] - END, G_Y[1] + END)
    pieces = []
    for j, side in ((0, -1), (1, 1)):                               # plates on the bay 1 face of each web
        yw = G_Y[j] + side * WEB / 2
        y0, y1 = sorted([yw, yw + side * CONN_W])

        def plate(xx, yy, t, j=j):
            bot, top = flange_faces(m, beams[j], j, xx)
            return (xx, yy, (1 - t) * bot + t * top)
        pieces.append(sweep([(y0, 0.0), (y1, 0.0), (y1, 1.0), (y0, 1.0)], [x - CONN_T / 2, x + CONN_T / 2], plate))
    pieces.append(box(xa, xb, ends[1], ends[0], z_strut, z_strut + ANGLE_LEG))
    h, v = ends[0] - y_mid, z_top - z_work
    th = v_angle(h, v, ANGLE_LEG)
    foot = ANGLE_LEG / (2 * np.sin(th))
    low = z_top - ANGLE_LEG / np.cos(th)
    notch = z_work + ANGLE_LEG / (2 * np.cos(th))
    if abs((z_top - notch) / h - np.tan(th)) > 1e-9 or abs((low - z_work) / (h - foot) - np.tan(th)) > 1e-9:
        raise ValueError('diagonal edges are not parallel')
    outline = [(y_mid + foot, z_work), (ends[0], low), (ends[0], z_top), (y_mid, notch), (ends[1], z_top),
               (ends[1], low), (y_mid - foot, z_work)]
    pieces.append(sweep(outline, [xa, xb], lambda xx, yy, zz: (xx, yy, zz)))
    info = dict(x=x, xa=xa, xb=xb, z_strut=z_strut, z_top=z_top, z_work=z_work, theta=th, ends=ends, y_mid=y_mid,
                faces=faces)
    return pieces, info


# ------------------------------------------------------------------------------------------------- checks
def man(mesh):
    mm = mesh.copy()
    mm.merge_vertices()
    return mf.Manifold(mf.Mesh64(vert_properties=np.asarray(mm.vertices, np.float64),
                                 tri_verts=np.asarray(mm.faces, np.uint32)))


def overlap_m3(a, b):
    """Intersection volume of two closed meshes, body by body (bodies = index-connected pieces)."""
    pa = [man(p) for p in a.split(only_watertight=False)]
    pb = [man(p) for p in b.split(only_watertight=False)]
    return sum((p ^ r).volume() for p in pa for r in pb)


def boxes_meet(a, b, pad=1e-3):
    return bool((a.bounds[0] <= b.bounds[1] + pad).all() and (a.bounds[1] >= b.bounds[0] - pad).all())


def stored(mesh):
    """The mesh as the GLB stores it (float32 positions)."""
    return tm.Trimesh(np.asarray(mesh.vertices, np.float32).astype(np.float64), np.asarray(mesh.faces), process=False)


def stored_closed(mesh):
    """scripts/refresh_geometry_verification.py's test on the stored mesh: index-connected bodies welded at 10 um,
    each closed with positive volume."""
    v32 = np.asarray(mesh.vertices, np.float32).astype(np.float64)
    parts = list(bodies(v32, np.asarray(mesh.faces)))
    return all(b.is_watertight and b.volume > 0 for b in parts), len(parts)


def hits(mesh, x, y):
    """Distinct Z values where the vertical line through (x, y) crosses the mesh (a line through a shared triangle
    edge is reported once)."""
    z = second.z_hits(mesh, x, y)
    return z[np.r_[True, np.diff(z) > 1e-7]] if len(z) else z


def projection_yz(mesh):
    """Outline of a frame-plane body seen along X: union of its faces that face along X."""
    t = mesh.triangles
    keep = np.abs(mesh.face_normals[:, 0]) > .99
    return unary_union([Polygon(tri[:, 1:]) for tri in t[keep] if Polygon(tri[:, 1:]).area > 1e-12])


def measure(mesh_of, ids, parts_bounds, infos=None):
    """Measured on actual triangles: overlaps with every part whose bounds meet the frame, and (for rebuilt frames)
    the contacts and clearances of the connection plates and angles."""
    out = {}
    for pid in ids:
        f = mesh_of(pid)
        ov = {}
        for q in parts_bounds:
            if q == pid:
                continue
            g = mesh_of(q)
            if boxes_meet(f, g):
                vol = overlap_m3(f, g)
                if vol > 1e-9 or q.startswith(('beam', 'splice')):
                    ov[q] = round(vol * 1e6, 4) + 0.0
        r = dict(overlaps_cm3=ov, centre_x_m=round(float(f.bounds.mean(axis=0)[0]), 6))
        if infos is None:
            out[pid] = r
            continue
        info = infos[pid]
        x, xa = info['x'], info['xa']
        pieces = f.split(only_watertight=False)
        plates = sorted([p for p in pieces if p.bounds[1][0] - p.bounds[0][0] < CONN_T + 1e-4 and
                         p.bounds[0][0] < x], key=lambda p: -p.bounds.mean(axis=0)[1])
        members = [p for p in pieces if p.bounds[0][0] > x]
        if len(plates) != 2 or len(members) != 2:
            raise ValueError(f'{pid}: unexpected bodies')
        r['internal_overlap_cm3'] = round(sum(overlap_m3(a, b) for i, a in enumerate(pieces) for b in pieces[i + 1:])
                                          * 1e6, 4) + 0.0
        r['members_to_plate_face_gap_m'] = round(float(min(p.bounds[0][0] for p in members) -
                                                       max(p.bounds[1][0] for p in plates)), 7) + 0.0
        for j, p in enumerate(plates):
            beam = mesh_of(f'beam_{j + 1}')
            side = -1 if j == 0 else 1
            web_face = G_Y[j] + side * WEB / 2
            bv = beam.vertices[np.abs(beam.vertices[:, 1] - web_face) < 1e-4]
            if not len(bv):
                raise ValueError('web face not found')
            near = p.bounds[1][1] if j == 0 else p.bounds[0][1]
            yc = web_face + side * CONN_W / 2
            zb, zp = hits(beam, x, yc), hits(p, x, yc)
            r[f'girder_{j + 1}_plate'] = dict(
                web_face_gap_m=round(float(abs(near - bv[:, 1].mean())), 7),
                bottom_flange_gap_m=round(float(zp.min() - zb[1]), 7) + 0.0,
                top_flange_gap_m=round(float(zb[2] - zp.max()), 7) + 0.0,
                height_m=round(float(zp.max() - zp.min()), 6), projection_m=round(float(p.extents[1]), 6))
        strut = min(members, key=lambda p: p.bounds[0][2])
        vee = max(members, key=lambda p: p.bounds[0][2])
        for j in (0, 1):                                               # least clearance over the angles' X extent
            side = -1 if j == 0 else 1
            beam = mesh_of(f'beam_{j + 1}')
            zb = [hits(beam, xx, G_Y[j] + side * (WEB / 2 + .05)) for xx in (info['xa'], info['xb'])]
            r[f'girder_{j + 1}_clearances_m'] = dict(
                strut_bottom_above_bottom_flange=round(float(strut.bounds[0][2] - max(z[1] for z in zb)), 6),
                diagonal_top_below_top_flange=round(float(min(z[2] for z in zb) - vee.bounds[1][2]), 6))
        mid = info['y_mid']
        r['v_on_strut_gap_m'] = round(float(hits(vee, xa + 1e-4, mid + 1e-3).min() - hits(strut, xa + 1e-4, mid + 1e-3).max()),
                                      7) + 0.0
        r['lap_on_connection_plates_m2'] = {
            f'{name}_girder_{j + 1}': round(float(projection_yz(body).intersection(projection_yz(plates[j])).area), 6)
            for name, body in (('strut', strut), ('diagonal', vee)) for j in (0, 1)}
        r['diagonal_slope_deg'] = round(float(np.degrees(info['theta'])), 3)
        r['frame_height_m'] = round(float(vee.bounds[1][2] - strut.bounds[0][2]), 6)
        out[pid] = r
    return out


NOTE_OLD = 'Exact stagger varies by bay and is approximated. '
NOTE = (' 3D review correction 1.4: rebuilt as existing sheets 10 and 14 (PDF 28, 32) draw the 2013 intermediate frame, '
        'northbound structure. Station {st} along Girder 1 from C/L bearing Abutment 1 (sheet 10: 15 ft 3 in + 4 spa. @ '
        '22 ft 0 in; the generator had it 1.0045 m up-station). L5x5x3/8 bottom strut 3 in above the top of the higher '
        'bottom flange (Girder 1 in the model) and V diagonals with their top 6 in below the underside of the lower top '
        'flange (Girder 2), the sheet 14 minima at which the detail is drawn; the strut no longer passes through the '
        'Girder 1 bottom flange. Adds the two 7 x 5/8 in connection plates (sheet 14; sheet 10 girder elevation: flange to '
        'flange), on the bay 1 face of the Girder 1 and Girder 2 webs, centred on the station; the angles (connected 5 in '
        'legs as 3/8 in strips) bear on their up-station face and end 0.02 m from the web centre lines. The 3/8 in gusset at '
        'the foot of the V is not dimensioned and not modelled: the diagonals stand on the strut at the bay centre (see '
        'known_deviations). Bolts, welds and outstanding legs omitted.')


def to_gltf(v):
    return np.column_stack([v[:, 0], v[:, 2], -v[:, 1]])


# ------------------------------------------------------------------------------------------------- correction
def correct(base=BASE, backup=ROOT / 'data/fem_research', dry_run=False):
    mp = base / 'model_manifest.json'
    raw_manifest = mp.read_bytes()
    manifest = json.loads(raw_manifest.decode('utf-8'))
    newline = '\r\n' if b'\r\n' in raw_manifest else '\n'     # keep the stored line endings
    if manifest.get(TAG_KEY) == TAG:
        print('Already corrected.')
        return None
    if manifest.get('review_correction_3') != third.TAG or manifest.get('revision') != third.REVISION:
        raise ValueError('Run scripts/correct_virginia_avenue_review_3.py first '
                         f'(expected revision {third.REVISION}, found {manifest.get("revision")}).')
    path = base / 'model.glb'
    original = path.read_bytes()
    before = hashlib.sha256(original).hexdigest()
    if before != BEFORE_SHA or before != manifest['review_correction_record_3']['after_glb_sha256']:
        raise ValueError(f'model.glb is not the revision 1.3 artifact (SHA-256 {before})')
    known = {d.get('id') for d in manifest.get('known_deviations', [])}
    if known != EXPECTED_DEVIATIONS:
        raise ValueError(f'unexpected known_deviations {sorted(known)}')
    length = struct.unpack_from('<I', original, 12)[0]
    gltf = json.loads(original[20:20 + length])
    binary = bytearray(original[28 + length:])
    if any(k in n for n in gltf['nodes'] for k in ('matrix', 'rotation', 'translation', 'scale')):
        raise ValueError('unexpected node transforms')
    parts = {p['id']: p for p in manifest['parts']}
    meshes = {m['name']: m for m in gltf['meshes']}
    if len(parts) != 162 or set(parts) != set(meshes):
        raise ValueError('Unexpected part set; the model is not the expected revision.')

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

    # Starting state: the frames, girders and splices are the review-1.1 reconstruction (rounds 2 and 3 left them).
    current, m = first.build(True)
    for pid in CHANGED + ['beam_1', 'beam_2', 'splice_1_1', 'splice_1_2', 'splice_2_1', 'splice_2_2']:
        if not second.first_same(glb_mesh(pid).vertices, current[pid][0].vertices):
            raise ValueError(f'{pid}: GLB geometry differs from the review-1.1 reconstruction')
    beams = (parts['beam_1'], parts['beam_2'])
    if any(abs(b['dimensions']['y_m'] - y) > 1e-9 for b, y in zip(beams, G_Y)):
        raise ValueError('girder lines not as expected')
    bounds = {pid: p['bounds_m'] for pid, p in parts.items()}
    measured_before = measure(glb_mesh, CHANGED, bounds)
    g1 = [measured_before[p]['overlaps_cm3'].get('beam_1', 0) for p in CHANGED]
    if min(g1) < 500 or measured_before['cross_frame_1_1']['overlaps_cm3'].get('splice_1_1', 0) < 30:
        raise ValueError(f'unexpected starting overlaps {measured_before}')
    f1 = glb_mesh('cross_frame_1_1')
    zf, zb = hits(f1, *OLD_PROBE), hits(glb_mesh('beam_1'), *OLD_PROBE)
    probe_before = dict(point_x_y_m=list(OLD_PROBE), strut_z_m=[round(float(zf[0]), 6), round(float(zf[1]), 6)],
                        girder_1_bottom_flange_z_m=[round(float(zb[0]), 6), round(float(zb[1]), 6)],
                        strut_below_flange_soffit_m=round(float(zb[0] - zf[0]), 6))

    # New frames.
    new, infos = {}, {}
    for q, pid in enumerate(CHANGED):
        pieces, info = frame(m, beams, q)
        for piece in pieces:
            if not piece.is_watertight or piece.volume <= 0:
                raise ValueError(f'{pid}: invalid piece')
        mesh = concat(pieces)
        mesh.remove_unreferenced_vertices()
        mesh.fix_normals(multibody=True)
        ok, n = stored_closed(mesh)
        if not ok or n != 4:
            raise ValueError(f'{pid}: not four closed bodies as stored')
        new[pid], infos[pid] = mesh, info
    last = m.sx(SPAN / 2, G_Y[0]) - infos[CHANGED[-1]]['x']
    if abs(last - LAST_TO_BRG_2_FT * FT) > 1e-9:
        raise ValueError(f'last frame {last} m from C/L bearing Abutment 2')

    def out_mesh(pid):
        return stored(new[pid]) if pid in new else glb_mesh(pid)
    measured_after = measure(out_mesh, CHANGED, bounds, infos)
    for pid, r in measured_after.items():
        bad = {q: v for q, v in r['overlaps_cm3'].items() if v > NO_OVERLAP_CM3}
        gaps = [r['members_to_plate_face_gap_m'], r['v_on_strut_gap_m']] + [
            r[f'girder_{j}_plate'][k] for j in (1, 2) for k in ('web_face_gap_m', 'bottom_flange_gap_m', 'top_flange_gap_m')]
        clear = r['girder_1_clearances_m']['strut_bottom_above_bottom_flange']
        top = r['girder_2_clearances_m']['diagonal_top_below_top_flange']
        if (bad or r['internal_overlap_cm3'] > NO_OVERLAP_CM3 or min(r['lap_on_connection_plates_m2'].values()) < .005 or max(abs(g) for g in gaps) > TOUCH or
                abs(clear - BOTTOM_CLEAR) > TOUCH or abs(top - TOP_CLEAR) > TOUCH or
                r['girder_2_clearances_m']['strut_bottom_above_bottom_flange'] < BOTTOM_CLEAR or
                r['girder_1_clearances_m']['diagonal_top_below_top_flange'] < TOP_CLEAR):
            raise ValueError(f'{pid}: frame not as intended {r}')

    # ------------------------------------------------------------------ write the GLB
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

    meta_keys = ('id', 'name', 'layer', 'color', 'pdf_pages', 'basis', 'note', 'dimensions')
    old_meta = {pid: dict(bounds_m=parts[pid]['bounds_m'], volume_m3=parts[pid]['volume_m3']) for pid in CHANGED}
    for q, pid in enumerate(CHANGED):
        mesh, info, p = new[pid], infos[pid], parts[pid]
        if not mesh.is_watertight or mesh.volume <= 0:
            raise ValueError(f'{pid}: invalid corrected solid')
        rgb = [int(p['color'][n:n + 2], 16) for n in (1, 3, 5)] + [255]
        prim = dict(attributes=dict(POSITION=append(to_gltf(mesh.vertices).astype('<f4'), 'VEC3', 5126),
                                    COLOR_0=append(np.tile(np.array(rgb, 'u1'), (len(mesh.vertices), 1)), 'VEC4', 5121)),
                    indices=append(mesh.faces.reshape(-1, 1).astype('<u4'), 'SCALAR', 5125), mode=4)
        gltf['accessors'][prim['attributes']['COLOR_0']]['normalized'] = True
        if meshes[pid]['primitives'][0].get('material') is not None:
            prim['material'] = meshes[pid]['primitives'][0]['material']
        meshes[pid]['primitives'] = [prim]
        if NOTE_OLD not in p['note'] or p['basis'] != 'Historical frame type and nominal 22 ft rows':
            raise ValueError(f'{pid}: note / basis not as expected')
        st = STATIONS_FT[q]
        p['basis'] = ('Existing plans 9548460 sheets 10 and 14 (PDF 28, 32): 2013 intermediate cross frame, northbound '
                      'structure; L5x5x3/8 V diagonals and bottom strut on 7 x 5/8 in connection plates at the sheet 10 '
                      'stations')
        p['note'] = p['note'].replace(NOTE_OLD, '') + NOTE.format(st=f'{int(st)} ft {round((st % 1) * 12)} in')
        r = measured_after[pid]
        p['dimensions'] = dict(
            frame='2013 intermediate V cross frame (northbound structure)', angles='L5x5x3/8',
            angle_representation='connected 5 in legs as 3/8 in strips on the up-station face of the connection plates',
            connection_plates='2 x PL 7 x 5/8 in (Girder 1 and Girder 2), flange to flange, centred on the station',
            station_from_girder_1_bearing_abutment_1_ft=st, station_x_m=round(info['x'], 6),
            strut_bottom_above_top_of_bottom_flange_m=dict(girder_1=r['girder_1_clearances_m']['strut_bottom_above_bottom_flange'],
                                                          girder_2=r['girder_2_clearances_m']['strut_bottom_above_bottom_flange']),
            diagonal_top_below_underside_of_top_flange_m=dict(girder_1=r['girder_1_clearances_m']['diagonal_top_below_top_flange'],
                                                             girder_2=r['girder_2_clearances_m']['diagonal_top_below_top_flange']),
            clearance_basis='sheet 14: 3 in Min. (bottom strut) and 6 in Min. (diagonals), built to the minima',
            member_end_offset_from_web_centre_m=END, diagonal_slope_deg=r['diagonal_slope_deg'],
            frame_height_m=r['frame_height_m'],
            connection_plate_m=dict(thickness=round(CONN_T, 6), projection=round(CONN_W, 6),
                                    height_girder_1=r['girder_1_plate']['height_m'],
                                    height_girder_2=r['girder_2_plate']['height_m']),
            gusset='3/8 in gusset at the foot of the V not dimensioned; not modelled (known_deviations)')
        p['bounds_m'] = np.round(mesh.bounds, 6).tolist()
        p['volume_m3'] = round(float(mesh.volume), 9)
        meshes[pid].setdefault('extras', {}).update({k: p[k] for k in meta_keys})

    by_id = {c['feature']: c for c in manifest.get('detail_coverage', [])}
    cov = by_id.get('Retained steel and bearings')
    if cov is None or not set(CHANGED) <= set(cov['part_ids']):
        raise ValueError('detail_coverage not as expected')
    cov['detail'] += (' 2013 bay 1 intermediate V frames at the sheet 10 stations with their 7 x 5/8 in connection plates '
                      '(existing sheets 10, 14; gusset at the foot of the V omitted).')

    deviation = dict(
        id=DEV_ID, parts=', '.join(CHANGED),
        source='existing plans 9548460 sheet 14 (PDF 32): Intermediate Cross-Frame Details, northbound structure; sheet 10 '
               '(PDF 28): Framing Plan - N.B.',
        deviation='The 3/8 in gusset plate at the foot of the V is not modelled. The two L5x5x3/8 diagonals are carried '
                  'down to the top of the bottom strut, where their centre lines meet at the bay centre, and meet each '
                  'other on the bay centre plane (one V-shaped body standing on the strut); on sheet 14 they stop short '
                  'of the strut and of each other and are bolted to the gusset, with the work point drawn within about '
                  '1 in of the strut top. The angles are their connected 5 in legs as 3/8 in strips; outstanding legs, '
                  'the 7/8 in bolts (slotted holes at Girder 1) and the welds are omitted. The members end 0.02 m from '
                  'the web centre lines (the generator\'s offset); sheet 14 draws the angle ends about 1 in off the webs.',
        reason='Sheet 14 draws the gusset and the angle ends but dimensions neither (the gusset scales about 14 1/2 x '
               '12 in, which is not used). Which face of the connection plate the angles bear on is not dimensioned '
               'either; the sheet 10 framing plan draws the frame lines on the up-station side of the plate ticks, '
               'which is used. Shop drawings of the 2013 Girder 1 replacement or a field measurement would settle them.')
    manifest['known_deviations'].append(deviation)

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
    o1 = measured_before['cross_frame_1_1']['overlaps_cm3']
    worst = max(v for r in measured_after.values() for v in r['overlaps_cm3'].values())
    manifest['review_correction_record_3d'] = dict(
        source='Second 3D review of revision 1.3 (finding VA-07), re-measured on the GLB and re-read against the drawings',
        previous_revision=previous_revision,
        source_pdf_pages=[31, 36], printed_sheets=[31, 36],
        historical_source=dict(source_id='9548460', pdf_pages=[28, 32], printed_sheets=[10, 14]),
        findings={
            'VA-07': 'Resolved. The five bay 1 intermediate frames are rebuilt as existing sheets 10 and 14 draw them. '
                     'Before: the 0.10 m lower strut crossed the Girder 1 bottom flange in every frame (overlap '
                     f'{min(g1):.1f}-{max(g1):.1f} cm3; at the review probe {probe_before["strut_below_flange_soffit_m"] * 1000:.1f} '
                     'mm below the flange soffit), the twisted diagonals cut '
                     f'{measured_before["cross_frame_1_1"]["overlaps_cm3"]["beam_2"]:.1f} cm3 into the Girder 2 web and frame 1 '
                     f'lay in the Girder 1 Splice "A" cover plates ({o1.get("splice_1_1", 0):.1f} cm3). After: frames at the '
                     'sheet 10 stations (15 ft 3 in + 4 spa. @ 22 ft along Girder 1; 1.0045 m down-station), bottom strut '
                     '3 in above the Girder 1 bottom flange, diagonal tops 6 in below the Girder 2 top flange (sheet 14 '
                     'minima), ten 7 x 5/8 in connection plates on the webs, flange to flange (sheets 10, 14); every '
                     f'member laps both plates; largest overlap with any part {worst:.4f} cm3 (float32 rounding of the '
                     'touching faces).'},
        decisions={
            'Frame stations': 'Sheet 10 dimensions the bay 1 frames along New Girder No. 1 from C/L bearing (15 ft 3 in, '
                              '4 spa. @ 22 ft 0 in, 10 ft 9 in); the generator measured the 15 ft 3 in at mid-bay. The '
                              'frames move 1.0045 m down-station; at the old station frame 1 and its Girder 1 '
                              'connection plate would lie in the Splice "A" cover plates.',
            'Strut and diagonal levels': 'Sheet 14 gives minima: bottom strut 3 in above the top of the bottom flange, '
                                         'diagonals 6 in below the underside of the top flange, and draws the detail at '
                                         'both. Applied to the governing girder of the model (Girder 1 bottom flange is '
                                         'the higher, Girder 2 top flange the lower; the 2013 sheet draws the girders '
                                         'the other way round, "Varies").',
            'Connection plate side': 'Not dimensioned. Centred on the frame station with the angles on its up-station '
                                     'face, as the sheet 10 framing plan draws the frame line beside the plate ticks.',
            'Member ends': 'Kept at the generator\'s 0.02 m from the web centre lines (12.06 mm clear of the webs); sheet '
                           '14 does not dimension them.',
            'Gusset': 'Drawn, not dimensioned: not modelled; the diagonals stand on the strut at the bay centre '
                      f'(known_deviations {DEV_ID}).'},
        kept={DEV_ID: deviation['reason']},
        changed_parts=CHANGED, added_parts=[], removed_parts=[],
        before=dict(old_meta, interfaces=measured_before, va07_probe=probe_before),
        after=dict({pid: dict(bounds_m=parts[pid]['bounds_m'], volume_m3=parts[pid]['volume_m3']) for pid in CHANGED},
                   interfaces=measured_after),
        before_glb_sha256=before, after_glb_sha256=hashlib.sha256(out).hexdigest())
    record = manifest['review_correction_record_3d']
    print(json.dumps(dict(changed=CHANGED, before=before, after=record['after_glb_sha256'], probe_before=probe_before,
                          interfaces_before=measured_before, interfaces_after=measured_after), indent=1))
    if dry_run:
        print('Dry run, nothing written.')
        return out, manifest
    backup.mkdir(exist_ok=True)
    (backup / f'{BID}_before_3d_review.glb').write_bytes(original)
    (backup / f'{BID}_manifest_before_3d_review.json').write_bytes(raw_manifest)
    path.write_bytes(out)
    mp.write_bytes((json.dumps(manifest, indent=2) + '\n').replace('\n', newline).encode('utf-8'))
    return out, manifest


if __name__ == '__main__':
    correct(dry_run='--dry-run' in sys.argv)

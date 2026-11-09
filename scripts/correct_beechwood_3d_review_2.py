"""Fifth correction of Beechwood Road over Little Blue River (beechwood), from the second 3D review: the end-bent drain
outlets. Runs after scripts/correct_beechwood_3d_review.py and keeps every GLB buffer it does not replace.

    python scripts/correct_beechwood_3d_review_2.py [--base DIR] [--backup DIR]

Source: drawings.pdf; PDF page = printed sheet + 1. Native axes: X increasing station (north), +Y to the left looking
up-station (west), Z up from El. 390 ft; the GLB stores native positions and each node's matrix maps them to (X, Z, -Y)
(model_manifest.json orientation).

D1 end-bent drain outlets (RESOLVED). Each end bent's 6 in drain ran 34 ft along the back of the bent at 1 % from an end
cap on the west (+Y) side to a 90 degree elbow on the east (-Y) side, then 24 ft (End Bent 1) / 22 ft (End Bent 4)
straight back from the bent at 1 %, at Y = -5.1816 m, and stopped in the approach embankment: about 2.2 m (south) and
1.6 m (north) of fill over the mouth (on the viewer's terrain). Both ends of each collector, the cap, the elbow and the
first 2.3 m (south) / 2.0 m (north) of each outlet also lay inside the wing returns: the wings stand at 16'-7" to 17'-7"
from the centre line (Y = +-5.0546 to +-5.3594 m) with their bottoms at the bent bottom, El. 424.34 / 413.64, and the
pipe crown was up to 9.2 in above that level.
  What the drawings say about the drain:
  - Sheets 32 and 33 (PDF 33, 34) Section A-A: "Pipe, End Bent Drain, 6 in." behind the bent at the foot of the 4:1
    "Aggregate for End Bent Backfill" wedge, in "Geotextile for Underdrain, Type 1A"; 3'-0" berm in front of the bent,
    then 2:1. Sheet 35 (PDF 36): wing bottoms El. 424.34 / 413.64, as the bents. No outlet is drawn.
  - Sheet 30 (PDF 31) Layout and sheet 51 (PDF 52) summary: 58 LFT (End Bent 1) and 56 LFT (End Bent 4) of "Pipe, End
    Bent Drain, 6 in."; no outlet protector or other outlet item. Sheet 31 (PDF 32) general plan: berms El. 426.72 /
    416.16, 2:1 spill slopes with 24 in Class 1 riprap, and Class 1 riprap limits that wrap round the wings to about
    26-31 ft right (east) of the centre line at both ends.
  - Standard drawing E 211-BFIL-04 (Backfill Placement Behind End Bent, Beam or Girder Structure; dated September 2003,
    September 2022 archive), the typical backfill detail the notes cite: PLAN - END BENT and ELEVATION - END BENT draw
    the pipe along the back of the bent from an End Cap, "End bent drain pipe exits under wingwall. Slope to drain.",
    6 in (min.) between the wing bottom and the pipe, and outside the wing a "45 (max.) Bend, If Required" turned toward
    the front of the bent.
  - Sheets 58 and 60 (PDF 59, 61), cross sections 105+00 and 107+50: on the east side 2:1 slopes from the berm (El.
    426.8 at 16.5 ft right) to the toe (El. 422.6 at 25 ft) and from Wing D (El. 418.9 at 17.5 ft) to existing ground
    (El. 412.9 at 29.7 ft). At End Bent 1 the east side is the low side (existing ground about 422 against 431 to the
    west); at End Bent 4 the west fill slope falls further (to El. 400.5 at 55 ft left). The plans do not say which
    side the drains outlet; the modelled east side is kept at both bents (see the record's decisions).
  The INDOT 2022 Standard Specifications make the end bent drain a perforated thermoplastic pipe (715.02(h)) paid by
  the foot (715.13); outlet protectors (718.06, E 718-UNDR-04 to -07) belong to underdrain outlets, and neither the
  plans nor E 211-BFIL-04 give one for this drain, so none is added.
  Each drain is re-routed as E 211-BFIL-04 draws it:
  - collector b*_drain_0: from the end cap, set 1/2 in inside the west wing, along the back of the bent on the modelled
    line (X = -0.9144 / 77.1144 m, 1'-6" behind the back face) and level at the cap end, falling straight to pass under
    the east wing with its crown 6 in below the wing bottom at the wing's inner face (3.81 % fall), and on to a 45 degree
    bend 5 ft beyond the wing's outer face;
  - b*_drain_elbow: a 45 degree socket elbow there (6 in centreline radius, 2 in sockets; selected envelope);
  - outlet b*_drain_1: 45 degrees in plan toward the span (north-east at End Bent 1, south-east at End Bent 4) at 1 %,
    to daylight on the spill slope in front of the bent, beside the riprap envelope.
  The bend position and the outlet length are not dimensioned: the bend is 5 ft beyond the wing (E 211-BFIL-04 draws it
  just outside the wing, not to scale) and the outlet runs until its invert meets the represented spill slope. The
  routed lengths stay within the drawn 58 / 56 ft.

Changed (8): b1_drain_0, b1_drain_1, b1_drain_elbow, b1_drain_cap, b4_drain_0, b4_drain_1, b4_drain_elbow,
b4_drain_cap. Added: none. Removed: none. Other meshes, accessors and the original binary data are kept byte for byte
(replaced accessors stay unreferenced).

Requires numpy, trimesh and manifold3d.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[1]

BID = 'beechwood'
BASE = ROOT / 'data/bridges' / BID
BACKUP = ROOT / 'data/fem_research'
FT = 0.3048
IN = 0.0254
TAG_KEY = 'review_correction_3d_2'
TAG = 'end-bent-drains-exit-under-east-wings'
RECORD_KEY = 'review_correction_record_3d_2'
REVISION = '2.4-3d-review-2'
PREVIOUS_TAG_KEY, PREVIOUS_TAG = 'review_correction_3d', 'deck-underside-crowned-8in'   # correct_beechwood_3d_review.py
PREVIOUS_REVISION = '2.3-3d-review'
EXPECTED_GLB_SHA256 = '3d87af59b10ddfe9021a3c4dff47f3c282aae37684440e96bafc5dc2c47ddf1b'   # revision 2.3 output

R_IN, R_OUT = 3 * IN, 3.2 * IN              # 6 in inside diameter, 0.2 in selected wall (as modelled)
SEG = 48                                    # sides of the modelled pipe sections (as the existing pipes)
WING_IN, WING_OUT = (16 + 7 / 12) * FT, (17 + 7 / 12) * FT     # wing faces from the centre line (sheets 32, 33)
UNDER_WING = 6 * IN                         # E 211-BFIL-04: 6 in (min.) from the wing bottom to the pipe
CAP_T, CAP_GAP = 0.25 * IN, 0.5 * IN        # end cap (as modelled) and its clearance to the west wing (selected)
BEND_OUT = 5 * FT                           # 45 degree bend beyond the east wing's outer face (selected)
BEND_R = 6 * IN                             # elbow centreline radius (selected fitting envelope)
SOCKET, SOCKET_R = 2 * IN, 0.0851           # elbow sockets: length (selected) and outer radius (as the old elbow)
OUTLET_FALL = 0.01                          # outlet grade (as modelled)
# Outlet plan length from the bend to the mouth: run until the invert meets the represented spill slope (selected).
OUTLET_LEN = {1: 147 * IN, 4: 180 * IN}
DRAWN_LFT = {1: 58, 4: 56}                  # sheet 30 / sheet 51 quantities
# Bent: collector line X, old collector axis Z at Y = 0 (1 % fall to -Y), wing bottom elevation (sheets 32, 33, 35),
# outlet plan direction along X (toward the span), east (low) and west (high) wing ids and names.
BENTS = {1: dict(x=-0.9144, z0=10.56742, bottom_el=424.34, toward_span=1.0, low_wing='b1_wing_R',
                 high_wing='b1_wing_L', wing_names=('Wing A', 'Wing B')),
         4: dict(x=77.1144, z0=7.30606, bottom_el=413.64, toward_span=-1.0, low_wing='b4_wing_R',
                 high_wing='b4_wing_L', wing_names=('Wing D', 'Wing C'))}
PAGES = dict(collector=[33, 34, 36, 31, 52], outlet=[31, 32, 33, 34, 36, 52, 59, 61], fitting=[33, 34, 36])


def el(z):
    return round(390 + z / FT, 3)


def expect(ok, message):
    if not ok:
        raise ValueError(f'{BID}: {message}')


def unit(v):
    v = np.asarray(v, dtype=float)
    return v / np.linalg.norm(v)


def frame(t):
    """Two unit vectors normal to t (the first horizontal), right-handed with t."""
    t = unit(t)
    u = unit(np.cross(t, [0.0, 0.0, 1.0]))
    return u, np.cross(t, u)


def sweep(rings):
    """Closed annular solid through rings (centre, u, v, inner radius, outer radius), SEG sides each."""
    ang = np.linspace(0, 2 * np.pi, SEG, endpoint=False)
    ca, sa = np.cos(ang), np.sin(ang)
    verts = []
    for c, u, v, ri, ro in rings:
        verts += [c + ro * (np.outer(ca, u) + np.outer(sa, v)), c + ri * (np.outer(ca, u) + np.outer(sa, v))]
    O = lambda k, j: 2 * k * SEG + j % SEG                                  # noqa: E731
    I = lambda k, j: (2 * k + 1) * SEG + j % SEG                            # noqa: E731
    faces = []
    for k in range(len(rings) - 1):
        for j in range(SEG):
            faces += [(O(k, j), O(k + 1, j + 1), O(k + 1, j)), (O(k, j), O(k, j + 1), O(k + 1, j + 1)),
                      (I(k, j), I(k + 1, j), I(k + 1, j + 1)), (I(k, j), I(k + 1, j + 1), I(k, j + 1))]
    for k, first in ((0, True), (len(rings) - 1, False)):
        for j in range(SEG):
            q = [(O(k, j), I(k, j), I(k, j + 1)), (O(k, j), I(k, j + 1), O(k, j + 1))]
            faces += q if first else [t[::-1] for t in q]
    m = trimesh.Trimesh(np.vstack(verts), np.array(faces), process=False)
    if m.volume < 0:
        m.invert()
    return m


def pipe(p0, p1):
    u, v = frame(p1 - p0)
    return sweep([(p0, u, v, R_IN, R_OUT), (p1, u, v, R_IN, R_OUT)])


def cap(p0, p1):
    """Closed disc of the pipe's outer radius from p0 to p1."""
    u, v = frame(p1 - p0)
    ang = np.linspace(0, 2 * np.pi, SEG, endpoint=False)
    ring = np.outer(np.cos(ang), u) + np.outer(np.sin(ang), v)
    verts = np.vstack([p0 + R_OUT * ring, p1 + R_OUT * ring, p0, p1])
    faces = []
    for j in range(SEG):
        a, b = j, (j + 1) % SEG
        faces += [(a, SEG + b, SEG + a), (a, b, SEG + b), (2 * SEG, b, a), (2 * SEG + 1, SEG + a, SEG + b)]
    m = trimesh.Trimesh(verts, np.array(faces), process=False)
    if m.volume < 0:
        m.invert()
    return m


def elbow(T1, d1, T2, d2):
    """Socket elbow: an annular arc (pipe bore, socket outer radius) from T1 (tangent d1) to T2 (tangent d2) and two
    sockets over the pipe ends (bore = pipe outer radius), unioned into one solid."""
    phi = np.arccos(np.clip(d1 @ d2, -1.0, 1.0))
    n1 = unit(d2 - (d1 @ d2) * d1)
    b = np.cross(d1, n1)
    centre = T1 + BEND_R * n1
    rings = []
    for th in np.linspace(0.0, phi, 13):
        q = -np.cos(th) * n1 + np.sin(th) * d1
        rings.append((centre + BEND_R * q, q, b, R_IN, SOCKET_R))
    expect(np.allclose(rings[-1][0], T2, atol=1e-9), 'elbow arc does not end at its tangent point')
    u1, v1 = frame(d1)
    u2, v2 = frame(d2)
    lap = 0.001                                   # the sockets reach 1 mm into the arc so the union is one body
    parts = [sweep(rings),
             sweep([(T1 - SOCKET * d1, u1, v1, R_OUT, SOCKET_R), (T1 + lap * d1, u1, v1, R_OUT, SOCKET_R)]),
             sweep([(T2 - lap * d2, u2, v2, R_OUT, SOCKET_R), (T2 + SOCKET * d2, u2, v2, R_OUT, SOCKET_R)])]
    return trimesh.boolean.union(parts, engine='manifold'), float(np.degrees(phi))


def box_overlaps(a, b, pad=1e-6):
    return not (np.any(a.bounds[0] > b.bounds[1] + pad) or np.any(b.bounds[0] > a.bounds[1] + pad))


def overlap(a, b):
    if not box_overlaps(a, b):
        return 0.0
    shared = trimesh.boolean.intersection([a, b], engine='manifold')
    return float(shared.volume) if len(shared.faces) else 0.0


def ft_in(m):
    inches = int(round(m / IN))
    return f'{inches // 12} ft {inches % 12} in'


def correct(base=BASE, backup=BACKUP):
    mp = base / 'model_manifest.json'
    raw_manifest = mp.read_bytes()
    manifest = json.loads(raw_manifest)
    if manifest.get(TAG_KEY) == TAG:
        print('Already corrected.')
        return
    expect(manifest.get(PREVIOUS_TAG_KEY) == PREVIOUS_TAG and manifest.get('revision') == PREVIOUS_REVISION,
           f'run scripts/correct_beechwood_3d_review.py first (revision {manifest.get("revision")})')
    expect(TAG_KEY not in manifest, f'{TAG_KEY} already holds {manifest.get(TAG_KEY)}')
    path = base / 'model.glb'
    original = path.read_bytes()
    before = hashlib.sha256(original).hexdigest()
    expect(before == EXPECTED_GLB_SHA256 == manifest['review_correction_record_3d']['after_glb_sha256'],
           f'model.glb SHA-256 {before} is not the revision {PREVIOUS_REVISION} output')

    length = struct.unpack_from('<I', original, 12)[0]
    gltf = json.loads(original[20:20 + length])
    binary = bytearray(original[28 + length:])
    parts = {p['id']: p for p in manifest['parts']}
    meshes = {m['name']: m for m in gltf['meshes']}
    expect(set(parts) == set(meshes) and len(parts) == 622, 'part list')
    expect(all(len(m['primitives']) == 1 for m in gltf['meshes']), 'one primitive per mesh')
    native_matrix = [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0]
    expect(all(n.get('matrix') == native_matrix for n in gltf['nodes'] if 'mesh' in n), 'node matrices')
    expect(all(n.get('name') == gltf['meshes'][n['mesh']]['name'] for n in gltf['nodes'] if 'mesh' in n), 'node names')

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
            prim = meshes[pid]['primitives'][0]
            cache[pid] = trimesh.Trimesh(read(prim['attributes']['POSITION']).astype(np.float64),
                                         read(prim['indices']).reshape(-1, 3), process=False)
        return cache[pid]

    new = {}

    def write(pid, mesh):
        mesh = trimesh.Trimesh(mesh.vertices, mesh.faces, process=False)
        prim = meshes[pid]['primitives'][0]
        color = read(prim['attributes']['COLOR_0'])[0]
        prim['attributes'] = {'POSITION': append(mesh.vertices.astype('<f4'), 'VEC3', 5126),
                              'COLOR_0': append(np.tile(color, (len(mesh.vertices), 1)).astype('u1'), 'VEC4', 5121)}
        gltf['accessors'][prim['attributes']['COLOR_0']]['normalized'] = True
        prim['indices'] = append(mesh.faces.reshape(-1, 1).astype('<u4'), 'SCALAR', 5125)
        stored = trimesh.Trimesh(mesh.vertices.astype('<f4').astype(np.float64), mesh.faces, process=False)
        expect(stored.is_watertight and stored.is_winding_consistent and stored.volume > 0,
               f'{pid}: not a closed solid')
        new[pid] = stored

    others = [pid for pid, p in parts.items() if p['layer'] != 'drainage']
    values, routes = {}, {}

    for k, bent in BENTS.items():
        b = f'b{k}'
        ids = dict(collector=f'{b}_drain_0', outlet=f'{b}_drain_1', elbow=f'{b}_drain_elbow', cap=f'{b}_drain_cap')
        olds = {key: solid(pid) for key, pid in ids.items()}
        low, high = solid(bent['low_wing']), solid(bent['high_wing'])
        z_bottom = (bent['bottom_el'] - 390) * FT
        # Starting state: the 1 % collector at Y = +-5.1816 m on the modelled line, the outlet straight back from it.
        oc, oo = olds['collector'].bounds, olds['outlet'].bounds
        expect(np.allclose(oc.mean(axis=0)[:2], [bent['x'], 0.0], atol=1e-4) and abs(oc[1][1] - 17 * FT) < 1e-3,
               f'{ids["collector"]}: not the 34 ft collector')
        expect(abs(oc.mean(axis=0)[2] - bent['z0']) < 1e-4, f'{ids["collector"]}: collector level')
        expect(abs(oo.mean(axis=0)[1] + 17 * FT) < 1e-3 and abs(oo[1][1] - oo[0][1] - 2 * R_OUT) < 1e-4,
               f'{ids["outlet"]}: not the straight outlet at Y = -5.1816 m')
        for wing in (low, high):
            expect(abs(wing.bounds[0][2] - z_bottom) < 1e-4, f'wing bottom is not El. {bent["bottom_el"]}')
            expect(abs(abs(wing.bounds[0][1] if wing is low else wing.bounds[1][1]) - WING_OUT) < 1e-4 and
                   abs(abs(wing.bounds[1][1] if wing is low else wing.bounds[0][1]) - WING_IN) < 1e-4, 'wing faces')
        mouth_old_x = oo[0][0] if bent['toward_span'] > 0 else oo[1][0]
        ring = olds['outlet'].vertices[np.abs(olds['outlet'].vertices[:, 0] - mouth_old_x) < 0.01]
        old_mouth = dict(x_m=round(float(np.mean(ring[:, 0])), 4), y_m=round(float(np.mean(ring[:, 1])), 4),
                         invert_z_m=round(float(ring[:, 2].min() + (R_OUT - R_IN)), 4),
                         crown_z_m=round(float(ring[:, 2].max()), 4))
        old_mouth.update(invert_el_ft=el(old_mouth['invert_z_m']), crown_el_ft=el(old_mouth['crown_z_m']))
        old_lengths = {key: parts[ids[key]]['dimensions']['length_ft'] for key in ('collector', 'outlet')}
        clashes_before = {}
        for key, pid in ids.items():
            for o in others:
                v = overlap(olds[key], solid(o))
                if v > 1e-9:
                    clashes_before[f'{pid} / {o}'] = round(v, 7)

        # New route (axis points): cap end H, low point L under the wing's inner face, bend PI, mouth M.
        yh = WING_IN - CAP_GAP - CAP_T
        H = np.array([bent['x'], yh, bent['z0'] + 0.01 * yh])
        L = np.array([bent['x'], -WING_IN, z_bottom - UNDER_WING - R_OUT])
        grade = (H[2] - L[2]) / (H[1] - L[1])
        PI = np.array([bent['x'], -(WING_OUT + BEND_OUT), L[2] - grade * (WING_OUT + BEND_OUT - WING_IN)])
        plan = np.array([bent['toward_span'], -1.0]) / np.sqrt(2)
        M = np.array([PI[0] + plan[0] * OUTLET_LEN[k], PI[1] + plan[1] * OUTLET_LEN[k],
                      PI[2] - OUTLET_FALL * OUTLET_LEN[k]])
        d1, d2 = unit(PI - H), unit(M - PI)
        tangent = BEND_R * np.tan(np.arccos(np.clip(d1 @ d2, -1, 1)) / 2)
        T1, T2 = PI - tangent * d1, PI + tangent * d2
        fitting, deflection = elbow(T1, d1, T2, d2)
        write(ids['collector'], pipe(H, T1))
        write(ids['elbow'], fitting)
        write(ids['outlet'], pipe(T2, M))
        write(ids['cap'], cap(H, H - CAP_T * d1))
        for key, pid in ids.items():
            expect(len(new[pid].split(only_watertight=False)) == 1, f'{pid}: not one body')

        # Checks: the crown passes 6 in under the east wing; nothing of the drain enters a wing or other structure.
        crown_at_wing = L[2] + R_OUT / np.cos(np.arctan(grade))
        expect(abs(z_bottom - crown_at_wing - UNDER_WING) < 2e-3, 'crown under the wing')
        # The 6 in layer under each wing (its plan box, from the bottom down 6 in less 2 mm) holds no drain.
        for wing in (low, high):
            lo, hi = wing.bounds
            layer = trimesh.creation.box(bounds=[[lo[0], lo[1], z_bottom - UNDER_WING + 0.002], [hi[0], hi[1], hi[2]]])
            for pid in ids.values():
                expect(overlap(new[pid], layer) < 1e-12, f'{pid}: within 6 in of a wing bottom')
        expect(new[ids['cap']].bounds[1][1] < WING_IN - 0.009, 'cap within 9 mm of the west wing')
        clashes_after = {}
        for key, pid in ids.items():
            for o in others:
                v = overlap(new[pid], solid(o))
                if v > 1e-9:
                    clashes_after[f'{pid} / {o}'] = v
        expect(not clashes_after, f'drain enters structure: {clashes_after}')
        among = {}
        keys = list(ids.values())
        for i, a in enumerate(keys):
            for c in keys[i + 1:]:
                v = overlap(new[a], new[c])
                if v > 1e-9:
                    among[f'{a} / {c}'] = round(v, 9)
        expect(all(v < 1e-6 for v in among.values()), f'drain fittings overlap the pipes: {among}')
        # Falls: the collector falls all the way from the cap to the bend, the outlet 1 % to the mouth.
        expect(grade > OUTLET_FALL and abs((PI[2] - M[2]) / np.hypot(*(M - PI)[:2]) - OUTLET_FALL) < 1e-9, 'falls')

        def axis_length(p, q):
            return float(np.linalg.norm(q - p))

        routed = axis_length(H, PI) + axis_length(PI, M)
        expect(routed / FT <= DRAWN_LFT[k], f'End Bent {k}: routed {routed / FT:.2f} ft > drawn {DRAWN_LFT[k]} ft')
        mouth = dict(x_m=round(float(M[0]), 4), y_m=round(float(M[1]), 4),
                     station=f'{(10496 + M[0] / FT) // 100:.0f}+{(10496 + M[0] / FT) % 100:05.2f}',
                     offset_ft_right=round(float(-M[1] / FT), 2),
                     invert_z_m=round(float(M[2] - R_IN), 4), crown_z_m=round(float(M[2] + R_OUT), 4))
        mouth.update(invert_el_ft=el(mouth['invert_z_m']), crown_el_ft=el(mouth['crown_z_m']))
        routes[k] = dict(ids=ids, H=H, L=L, PI=PI, M=M, T1=T1, T2=T2, grade=grade, deflection=deflection)
        values[f'end_bent_{k}'] = dict(
            route_axis_points_m=dict(cap_end=np.round(H, 4).tolist(), under_wing_inner_face=np.round(L, 4).tolist(),
                                     bend=np.round(PI, 4).tolist(), mouth=np.round(M, 4).tolist()),
            collector_fall_pct=round(grade * 100, 3), outlet_fall_pct=OUTLET_FALL * 100,
            elbow_deflection_deg=round(deflection, 3),
            crown_below_wing_bottom_in=dict(before=round((z_bottom - (bent['z0'] - 0.01 * WING_IN + R_OUT)) / IN, 2),
                                            after=round((z_bottom - crown_at_wing) / IN, 2)),
            routed_centreline_ft=dict(before=round(sum(old_lengths.values()), 3), after=round(routed / FT, 3),
                                      drawn=DRAWN_LFT[k],
                                      after_parts=dict(collector_to_bend=round(axis_length(H, PI) / FT, 3),
                                                       bend_to_mouth=round(axis_length(PI, M) / FT, 3))),
            mouth=dict(before=old_mouth, after=mouth),
            clashes_with_structure_m3=dict(before=clashes_before, after={}),
            socket_overlaps_m3=among)

    # ---------------------------------------------------------------- manifest entries and mesh extras.
    def update(pid, name, basis, note, dims, pages, refs):
        p = parts[pid]
        m = new[pid]
        p.update(name=name, basis=basis, note=note, dimensions=dims, pdf_pages=sorted(set(pages)),
                 sheets=sorted({q - 1 for q in pages}), external_references=refs,
                 bounds_m=m.bounds.round(6).tolist(), volume_m3=round(float(m.volume), 6))
        extras = meshes[pid]['extras']
        if 'height' in extras:
            extras['height'] = float(dims['length_ft'] * FT) if 'length_ft' in dims else extras['height']
        extras.update({key: p[key] for key in ('id', 'name', 'layer', 'sheets', 'pdf_pages', 'basis', 'note',
                                               'dimensions', 'external_references')})

    std = ['E211-BFIL-04']
    for k, r in routes.items():
        bent, ids, v = BENTS[k], r['ids'], values[f'end_bent_{k}']
        low_name, high_name = bent['wing_names']
        span_dir = 'north-east' if bent['toward_span'] > 0 else 'south-east'
        c_len = float(np.linalg.norm(r['T1'] - r['H']))
        o_len = float(np.linalg.norm(r['M'] - r['T2']))
        update(ids['collector'], '6 in end-bent drain collector', 'Drawing diameter and quantity; E 211-BFIL-04 route',
               f'Rev. {REVISION} (3D review 2): along the back of End Bent {k} from the end cap 1/2 in inside '
               f'{high_name} and under {low_name} (crown 6 in below its bottom, El. {bent["bottom_el"]}, at its inner '
               f'face; E 211-BFIL-04 "exits under wingwall", 6 in (min.)) to a 45 degree bend 5 ft beyond the wing, '
               f'falling {v["collector_fall_pct"]:.2f} % (the cap end kept at the modelled level beside the bent, sheet '
               f'32 Section A-A). It ran 34 ft at 1 % with both ends 5 in into the wings. Routed with the outlet: '
               f'{v["routed_centreline_ft"]["after"]:.1f} ft against {DRAWN_LFT[k]} LFT drawn (sheets 30, 51). Pipe '
               'product (perforated PVC or Type SP tubing, 2022 Standard Specifications 715.02(h)) and wall selected.',
               dict(inside_diameter_in=6, selected_wall_in=0.2, length_ft=c_len / FT,
                    fall_pct=round(v['collector_fall_pct'], 3), crown_below_wing_bottom_in=6,
                    bend_beyond_wing_ft=BEND_OUT / FT), PAGES['collector'], std)
        update(ids['outlet'], '6 in end-bent drain outlet', 'Drawing diameter and quantity; E 211-BFIL-04 route; '
               'outlet length selected', f'Rev. {REVISION} (3D review 2): from the 45 degree bend 5 ft beyond '
               f'{low_name} toward the span ({span_dir}) at 1 %, to daylight on the spill slope in front of the bent, '
               f'beside the riprap envelope (mouth at Sta. {v["mouth"]["after"]["station"]}, '
               f'{v["mouth"]["after"]["offset_ft_right"]:.1f} ft right, invert El. '
               f'{v["mouth"]["after"]["invert_el_ft"]:.2f}); the plans wrap the Class 1 riprap round the wing to about '
               f'26-31 ft right (sheet 31). It ran {parts[ids["outlet"]]["dimensions"]["length_ft"]:.0f} ft straight back '
               f'into the approach fill (crown El. {v["mouth"]["before"]["crown_el_ft"]:.2f} at the mouth). The bend '
               'position and the outlet length are not dimensioned; no outlet protector is given for end bent drains.',
               dict(inside_diameter_in=6, selected_wall_in=0.2, length_ft=o_len / FT, fall_pct=OUTLET_FALL * 100,
                    plan_angle_to_bent_deg=45, mouth_invert_el_ft=v['mouth']['after']['invert_el_ft']),
               PAGES['outlet'], std)
        update(ids['elbow'], 'Drain socket elbow, 45 degree', 'Selected fitting envelope; E 211-BFIL-04 bend',
               f'Rev. {REVISION} (3D review 2): the "45 (max.) Bend, If Required" of E 211-BFIL-04, 5 ft beyond '
               f'{low_name}; it was a 90 degree corner fitting inside the wing. Socket envelope (6 in centreline '
               'radius, 2 in sockets, 6.7 in outside) selected; the shape depends on the pipe supplier.',
               dict(plan_deflection_deg=45, deflection_deg=round(r['deflection'], 3), centreline_radius_in=6,
                    socket_length_in=2, socket_outside_diameter_in=round(2 * SOCKET_R / IN, 3)),
               PAGES['fitting'], std)
        update(ids['cap'], 'Upstream drain cap', 'Selected fitting envelope; E 211-BFIL-04 end cap',
               f'Rev. {REVISION} (3D review 2): on the collector\'s high end 1/2 in inside {high_name} (E 211-BFIL-04 '
               'End Cap); it lay inside the wing. 1/4 in disc, normal to the pipe.',
               dict(thickness_in=0.25, clearance_to_wing_in=0.5), PAGES['fitting'], std)
    for pid in new:
        expect(np.abs(np.array(parts[pid]['bounds_m']) - new[pid].bounds).max() < 1e-6, f'{pid} bounds')

    for item in manifest.get('detail_coverage', []):
        if item.get('feature') == 'Abutment drain pipe':
            item['status'] = 'Standard route (E 211-BFIL-04); bend position and outlet length selected'
            item['sources'] = ['30-33,35,51,58,60', 'E211-BFIL-04', 'INDOT 2022 Standard Specifications 715, 718']
            item['detail'] = ('6 in pipe along the back of each end bent from an end cap inside the west wing, exiting '
                              'under the east wing with its crown 6 in below the wing bottom, then a 45 degree bend '
                              'toward the span and a 1 % outlet to daylight on the spill slope (E 211-BFIL-04). '
                              f'Routed {values["end_bent_1"]["routed_centreline_ft"]["after"]:.1f} / '
                              f'{values["end_bent_4"]["routed_centreline_ft"]["after"]:.1f} ft against 58 / 56 LFT '
                              'drawn. No grading plan fixes the mouth; no outlet protector applies.')
            item['part_ids'] = [f'b{k}_drain_{s}' for k in BENTS for s in ('0', '1', 'elbow', 'cap')]
    for source in (dict(id='INDOT 2022 Standard Specifications',
                        url='https://www.in.gov/dot/div/contracts/standards/book/sep21/2022%20Standard%20Specifications.pdf',
                        edition='2022'),
                   dict(id='E718-UNDR',
                        url='https://www.in.gov/dot/div/contracts/standards/drawings/sep22/700e/e700%20combined%20pdfs/'
                            'E718-UNDR.pdf', edition='September 2022 archive')):
        if not any(s.get('id') == source['id'] for s in manifest['external_sources']):
            manifest['external_sources'].append(source)

    while len(binary) % 4:
        binary.append(0)
    gltf['buffers'][0]['byteLength'] = len(binary)
    encoded = json.dumps(gltf, ensure_ascii=True, separators=(',', ':')).encode()
    encoded += b' ' * ((-len(encoded)) % 4)
    out = (struct.pack('<III', 0x46546c67, 2, 28 + len(encoded) + len(binary)) +
           struct.pack('<II', len(encoded), 0x4e4f534a) + encoded + struct.pack('<II', len(binary), 0x004e4942) + binary)
    backup.mkdir(parents=True, exist_ok=True)
    (backup / f'{BID}_before_3d_review_2.glb').write_bytes(original)
    (backup / f'{BID}_manifest_before_3d_review_2.json').write_bytes(raw_manifest)
    path.write_bytes(out)

    changed = sorted(new)
    manifest[TAG_KEY] = TAG
    manifest['revision'] = REVISION
    manifest[RECORD_KEY] = dict(
        review='3D review, round 2', follows=PREVIOUS_TAG, previous_revision=PREVIOUS_REVISION,
        source_pdf_pages=[31, 32, 33, 34, 36, 52, 59, 61], printed_sheets=[30, 31, 32, 33, 35, 51, 58, 60],
        external_sources=['E211-BFIL-04', 'INDOT 2022 Standard Specifications 715.02(h), 715.13, 718.06',
                          'E718-UNDR-01 to -07'],
        native_axes='X station increasing (north), +Y left looking up-station (west), Z up from El. 390 ft; GLB (X, Z, '
                    '-Y) through the node matrices',
        findings=[dict(
            id='D1', verdict='resolve',
            summary='The two 6 in end-bent drain outlets ran 24 ft / 22 ft straight back from the bents at Y = -5.1816 m '
                    'and stopped in the approach embankment (about 2.2 m / 1.6 m of fill over the mouths); the cap, '
                    'both collector ends, the elbows and the first 2.3 m / 2.0 m of the outlets lay inside the wings. '
                    'Now each drain exits under the east wing with its crown 6 in below the wing bottom, turns 45 '
                    'degrees toward the span 5 ft beyond the wing and runs at 1 % to daylight on the spill slope',
            basis='E 211-BFIL-04 PLAN and ELEVATION - END BENT ("End bent drain pipe exits under wingwall. Slope to '
                  'drain.", 6 in (min.), "45 (max.) Bend, If Required", End Cap); sheets 32, 33 Section A-A (pipe '
                  'behind the bent in the backfill aggregate); sheet 35 (wing bottoms); sheets 30, 51 (58 / 56 LFT); '
                  'sheet 31 (berms, 2:1 spill slopes, Class 1 riprap round the wings); sheets 58, 60 (2:1 east side '
                  'slopes at 105+00 and 107+50)')],
        decisions=[
            'Outlet on the east (-Y, downstream) side and cap on the west side at both bents, as modelled; the plans '
            'do not fix the side. At End Bent 1 the east side is the low side (section 105+00: existing ground about '
            'El. 422 east, 431 west). End Bent 4 could also drain west: section 107+50 draws a 2:1 riprapped fill slope '
            'west of Wing C falling to El. 400.5 at 55 ft left, which a straight outlet under Wing C would meet about '
            '31 ft left without a bend. The east side is kept there because its route also reaches the outlet level '
            'on the drawings (existing ground at the mouth within about 0.1 ft of the invert, see below) and the '
            'viewer\'s terrain has no valley west of the bent (it would cover a west mouth by about 0.5 m).',
            'The collector keeps its modelled line (1 ft 6 in behind the back face) and its level at the cap end (6.1 '
            'in above the bent bottom; sheet 32 Section A-A draws the pipe beside the bent above its bottom) and falls '
            'straight to the crown 6 in below the east wing bottom at the wing\'s inner face (E 211-BFIL-04 6 in '
            '(min.)): 3.81 % at both bents. E 211-BFIL-04 only says "Slope to drain"; the 1 % of the old route is kept '
            'for the outlet.',
            'The cap end is 1/2 in inside the west wing (selected); E 211-BFIL-04 draws the End Cap just inside the '
            'wing.',
            'The 45 degree bend is 5 ft beyond the east wing\'s outer face (E 211-BFIL-04 draws it just outside the '
            'wing, not to scale; selected) and turns toward the front of the bent, as the standard plan draws it. It '
            'is required: going straight on, the pipe stays under the approach fill (behind End Bent 1 the ground '
            'rises to the approach, section 104+50) or meets ground above its invert (section 107+50: El. 412.9 and '
            'higher east of Wing D). With the bend 1 ft 6 in out, the outlet\'s plan centre would lie in front of the '
            'bent face, where the viewer\'s illustrative terrain (terrain.js) treats drainage parts as hanging and cuts '
            'the ground under them.',
            f'The outlet runs {ft_in(OUTLET_LEN[1])} (End Bent 1) / {ft_in(OUTLET_LEN[4])} (End Bent 4) in plan from the '
            'bend, to where its invert meets the spill slope represented in front of the bent, beside the riprap '
            'envelope (selected; no grading plan or outlet location is drawn). On the terrain the viewer builds from '
            'the model the ground at the mouths is El. 422.90 / 412.18 and the inverts are 0.02 m above it. No '
            'grading is drawn at the bent corners: interpolated between the drawn sections the existing ground at the '
            f'mouths is about El. 422.3 (section 105+00, {values["end_bent_1"]["mouth"]["after"]["offset_ft_right"]:.0f} '
            f'ft right; invert El. {values["end_bent_1"]["mouth"]["after"]["invert_el_ft"]:.2f}) and El. 412.4 '
            f'(sections 107+00 and 107+50, {values["end_bent_4"]["mouth"]["after"]["offset_ft_right"]:.0f} ft right; '
            f'invert El. {values["end_bent_4"]["mouth"]["after"]["invert_el_ft"]:.2f}); on section 105+00 the 2:1 '
            'slope east of the berm reaches the south invert level 24 ft right of the centre line, about 7 ft short of '
            'the modelled mouth. The model\'s riprap envelope stops 24 ft right, where the plan limits wrap round the '
            'wings to about 26-31 ft.',
            'Routed lengths stay below the drawn 58 / 56 LFT; the plans do not show where the remainder goes.',
            'No outlet protector, headwall or splash pad: neither the plans (no pay item) nor E 211-BFIL-04 give one '
            'for end bent drains; outlet protectors (2022 Standard Specifications 718.06, E 718-UNDR-04 to -07) are '
            'for underdrain outlets.',
            'Elbow envelope (6 in centreline radius, 2 in sockets, 6.7 in outside diameter as the old elbow) and the '
            '1/4 in cap are selected fitting envelopes; pipe wall 0.2 in as modelled.'],
        kept=['Pipe diameter, wall, collector line, cap-end level, outlet side and the 1 % outlet grade.'],
        changed_parts=changed, added_parts=[], removed_parts=[],
        values=values, before_glb_sha256=before, after_glb_sha256=hashlib.sha256(out).hexdigest())
    text = json.dumps(manifest, ensure_ascii=False, indent=2) + '\n'
    if b'\r\n' in raw_manifest:
        text = text.replace('\n', '\r\n')
    mp.write_bytes(text.encode('utf-8'))
    record = manifest[RECORD_KEY]
    print(json.dumps({k: v for k, v in record.items() if k not in ('values', 'findings', 'decisions')}, indent=1))
    for k in BENTS:
        v = values[f'end_bent_{k}']
        print(f'End Bent {k}: routed {v["routed_centreline_ft"]["before"]:.2f} -> {v["routed_centreline_ft"]["after"]:.2f} '
              f'ft (drawn {DRAWN_LFT[k]}); collector fall {v["collector_fall_pct"]:.2f} %; mouth invert El. '
              f'{v["mouth"]["before"]["invert_el_ft"]:.2f} -> {v["mouth"]["after"]["invert_el_ft"]:.2f}, crown El. '
              f'{v["mouth"]["before"]["crown_el_ft"]:.2f} -> {v["mouth"]["after"]["crown_el_ft"]:.2f}; '
              f'structure clashes {len(v["clashes_with_structure_m3"]["before"])} -> 0')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--base', type=Path, default=BASE, help='bridge folder (default: the repository copy)')
    parser.add_argument('--backup', type=Path, default=BACKUP, help='backup folder')
    args = parser.parse_args()
    correct(args.base, args.backup)

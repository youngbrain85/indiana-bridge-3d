"""Second round of drawing-confirmed corrections of Fletcher Avenue over I-65 / I-70 (fletcher-avenue), run after
scripts/correct_fletcher_avenue_review.py. Unrelated GLB buffers are kept; new accessors are appended.

    python scripts/correct_fletcher_avenue_review_2.py [--dry-run]

Source: drawings.pdf (local review binder; printed sheet n = PDF page n for the 2026 contract sheets 33-73;
S9 = PDF 100, S10 = PDF 101 of the 1971 I-65-3(106)111 plans). Native axes: X increasing station, Y transverse
(+Y south, girder 1 at +Y), Z up; Z = (El. - 698.59 ft) x 0.3048; U = X + tan(skew) Y along each girder line.

1. Field splices A/B (S9 for girders 1 and 8, S10 for girders 2-7, "(A & B)" elevation details). The 60 in x 5/8 in
   web is continuous through the splice and the thinner field flanges are packed out with fillers on the outside,
   top and bottom: S9 26 in x 2 3/4 in pier flanges, 26 in x 1 3/4 in field flanges, 26 in x 1 in x 3 ft 0 in
   fillers and 26 in x 7/8 in x 6 ft 3 in splice plates; S10 24 in x 2 1/4 in / 24 in x 1 3/4 in flanges,
   24 in x 1/2 in x 3 ft 3 in fillers and 24 in x 1 in x 6 ft 9 in splice plates. The model kept the top of steel
   continuous, so the field webs sat 1 in / 1/2 in above the pier webs, the bottom flange stepped 2 in / 1 in at the
   splice and the flat bottom splice plates stood 25-54 mm clear of the field flanges. The field segments (beyond
   40 ft from Pier 2) are lowered by the flange-thickness difference so the webs align; the splice plates now follow
   the girder grade on the outer faces of the pier flanges and of the fillers. Fillers sit flush with the field end of
   the splice plate (1 1/2 in end distance either side of the 3 in bolt pitch on the S9/S10 top views). The web splice
   plates and web bolts do not move (the pier web is the reference). Consequences: the haunches over the field
   segments thicken by the same amount, the abutment bearing stiffeners move down with the girder and the abutment
   bearing envelopes (derived stacks) lose the same height in their load-plate block.
2. Girder ends (S9 and S10 girder elevations): each girder ends 4 1/2 in beyond the centre line of its abutment
   bearing (T.S. Abut. 1 / T.S. Abut. 3). The model stopped at the bearing centre lines. The end rings move out by
   0.1143 m along the girder and the haunches follow; the bearing stiffeners stay on the bearing lines. With the girder
   now continuing over the whole abutment bearing, the top face of each abutment bearing envelope follows the girder
   bottom along the grade (sheet 58 shows tapered top plates at Abutment 3) instead of cutting into it.
3. Abutment backwall tops (sheets 61-62, Abutment 3 elevation and sections C-C / D-D; sheet 56, typical sections
   Abut. No. 1 and No. 3): the concrete closes against the slab across the full width. The backwalls had only the two
   coping corners on their top, so they stood up to 188 mm below the crowned deck soffit at the crown line. The tops
   are remeshed on the corrected deck soffit with the deck section's breaks: crown (Y = 0) and north curb line
   (Y = -27 ft; the south deck continues at 2 % under the walk, so it has no break there). The Abutment 3 wall runs
   0.17 m past the deck end; there its top steps down to the soffit of the 1 ft approach slab instead of cutting into
   it.

Not changed: S10 Span B field flanges stay 24 in (the S10 splice "(A & B)" detail gives 24 in x 1 3/4 in flanges and
24 in splice plates and fillers; the elevation label reads 24 in). The TTX railing transitions stay deferred.

Requires numpy, trimesh, shapely and manifold3d; reuses the helpers of scripts/correct_fletcher_avenue_review.py.
"""
import hashlib
import json
import struct
import sys
from pathlib import Path

import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import correct_fletcher_avenue_review as R1  # noqa: E402
from bridge_geometry import box, concat  # noqa: E402

BID = 'fletcher-avenue'
BASE = ROOT / 'data/bridges' / BID
TAG = 'splice-web-alignment-fillers-girder-end-extensions-backwall-crown'
REVISION = '1.2-review-corrections-2'

FT, IN = R1.FT, R1.IN
K, SPAN, YS = R1.K, R1.SPAN, R1.YS
SLAB, CLEAR, ROAD, HALF = R1.SLAB, R1.CLEAR, R1.ROAD, R1.HALF
SPLICE = 40 * FT                                                 # S9/S10: splices 40 ft from Pier 2
SLIVER = 1e-5                                                    # generator's duplicate ring at a plate change
WEB = 60 * IN
END_EXT = 4.5 * IN                                               # S9/S10: girder end beyond the bearing centre line
# S9 (girders 1, 8) and S10 (girders 2-7) splice "(A & B)" details: (width, thickness, length)
COVER = {True: (26 * IN, 7 / 8 * IN, (6 + 3 / 12) * FT), False: (24 * IN, 1 * IN, (6 + 9 / 12) * FT)}
FILLER = {True: (26 * IN, 1 * IN, 3 * FT), False: (24 * IN, .5 * IN, (3 + 3 / 12) * FT)}


def dtf(j):
    """Pier-minus-field flange thickness: S9 2 3/4 - 1 3/4 = 1 in; S10 2 1/4 - 1 3/4 = 1/2 in (= filler)."""
    d = R1.tf_pier(j) - R1.TF_FIELD
    if not np.isclose(d, FILLER[R1.exterior(j)][1]):
        raise ValueError('filler thickness does not match the flange step')
    return d


def top_pier(u, j):
    """Top of steel of the pier segment (the model's continuous top before this correction)."""
    return R1.girder_top(u, j)


def top_new(u, j):
    """Top of steel: field segments lowered by the flange step so the webs align (S9/S10)."""
    return R1.girder_top(u, j) - (dtf(j) if abs(u) > SPLICE + SLIVER / 2 else 0.0)


def bottom_pier(u, j):
    return top_pier(u, j) - WEB - 2 * R1.tf_pier(j)


# ------------------------------------------------------------------------------------------ correction
def correct(base=BASE, backup=ROOT / 'data/fem_research', dry_run=False):
    mp = base / 'model_manifest.json'
    manifest = json.loads(mp.read_text(encoding='utf-8'))
    if manifest.get('review_geometry_correction_2') == TAG:
        print('Already corrected.')
        return None
    if manifest.get('review_geometry_correction') != R1.TAG or manifest.get('revision') != R1.REVISION:
        raise ValueError('run scripts/correct_fletcher_avenue_review.py first')
    path = base / 'model.glb'
    original = path.read_bytes()
    before = hashlib.sha256(original).hexdigest()
    if before != manifest['review_geometry_correction_record']['after_glb_sha256']:
        raise ValueError('model.glb is not the output of the first review correction')
    length = struct.unpack_from('<I', original, 12)[0]
    gltf = json.loads(original[20:20 + length])
    binary = bytearray(original[28 + length:])
    parts = {p['id']: p for p in manifest['parts']}
    meshes = {m['name']: m for m in gltf['meshes']}
    geometry = []

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
        v = read(prim['attributes']['POSITION']).astype(np.float64)
        f = read(prim['indices']).reshape(-1, 3)
        return trimesh.Trimesh(np.c_[v[:, 0], -v[:, 2], v[:, 1]], f, process=False)

    def store(pid, mesh, note=None, dims=None, new_topology=False, replace=False, basis=None):
        """Write a corrected native-axes mesh and update the manifest part and the mesh extras."""
        prim = meshes[pid]['primitives'][0]
        old = native(pid)
        if old.is_watertight and not mesh.is_watertight:
            raise ValueError(f'{pid}: corrected mesh is not watertight')
        if mesh.volume <= 0:
            raise ValueError(f'{pid}: corrected mesh has no positive volume')
        v = mesh.vertices
        glb = np.c_[v[:, 0], v[:, 2], -v[:, 1]].astype('<f4')
        if new_topology:
            color = read(prim['attributes']['COLOR_0'])[0]
            prim['attributes'] = {'POSITION': append(glb, 'VEC3', 5126),
                                  'COLOR_0': append(np.tile(color, (len(v), 1)).astype('u1'), 'VEC4', 5121)}
            gltf['accessors'][prim['attributes']['COLOR_0']]['normalized'] = True
            prim['indices'] = append(np.asarray(mesh.faces).reshape(-1, 1).astype('<u4'), 'SCALAR', 5125)
        else:
            if len(v) != len(old.vertices) or not np.array_equal(np.asarray(mesh.faces), np.asarray(old.faces)):
                raise ValueError(f'{pid}: topology changed without new_topology')
            prim['attributes']['POSITION'] = append(glb, 'VEC3', 5126)
        p = parts[pid]
        p['bounds_m'] = np.round(mesh.bounds, 6).tolist()
        if 'volume_m3' in p:
            p['volume_m3'] = round(float(mesh.volume), 9)
        if dims:
            p.setdefault('dimensions', {}).update(dims)
        if note:
            p['note'] = note if replace else (p.get('note', '') + ' ' + note).strip()
        if basis:
            p['basis'] = basis
        meshes[pid]['extras'].update(p)
        if pid not in geometry:
            geometry.append(pid)

    # ------------------------------------------------------------------ 1+2. girders (S9, S10)
    record_girders = {}
    for j, y in enumerate(YS):
        for i in range(2):
            pid = f'girder_{i}_{j}'
            mesh = native(pid)
            v = mesh.vertices.copy()
            xs = np.unique(v[:, 0])
            end_x = xs[0] if i == 0 else xs[-1]
            if not np.isclose(end_x + K * y, (-1 if i == 0 else 1) * SPAN, atol=2e-5):
                raise ValueError(f'{pid}: end ring not on the bearing centre line')
            field_rings = 0
            for x in xs:
                ring = np.flatnonzero(v[:, 0] == x)
                if len(ring) != 12:
                    raise ValueError(f'{pid}: unexpected ring at X={x}')
                u = x + K * y
                z = v[ring, 2]
                levels = np.unique(np.round(z, 5))
                if len(levels) != 4:
                    raise ValueError(f'{pid}: unexpected section levels')
                tf_bot, web, tf_top = np.diff(levels)
                if not np.isclose(z.max(), top_pier(u, j), atol=2e-5):
                    raise ValueError(f'{pid}: top of steel at u={u:.4f} is not the continuous first-round top')
                field = np.isclose(tf_top, R1.TF_FIELD, atol=2e-5)
                if not (np.isclose(tf_top, tf_bot, atol=2e-5) and np.isclose(web, R1.web(u), atol=2e-5) and
                        (field or np.isclose(tf_top, R1.tf_pier(j), atol=2e-5))):
                    raise ValueError(f'{pid}: unexpected section at u={u:.4f}')
                if field != (abs(u) > SPLICE + SLIVER / 2):
                    raise ValueError(f'{pid}: plate change not at the splice (u={u:.6f})')
                if not field:
                    continue
                field_rings += 1
                if x == end_x:
                    # S9/S10: girder end 4 1/2 in beyond the bearing centre line, same field section
                    un = (-1 if i == 0 else 1) * (SPAN + END_EXT)
                    top = top_new(un, j)
                    new = np.array([top - 2 * R1.TF_FIELD - WEB, top - R1.TF_FIELD - WEB, top - R1.TF_FIELD, top])
                    v[ring, 2] = new[np.searchsorted(levels, np.round(z, 5))]
                    v[ring, 0] = R1.sx(un, y)
                else:
                    v[ring, 2] -= dtf(j)
            store(pid, trimesh.Trimesh(v, mesh.faces, process=False), replace=True,
                  note='S9/S10 plate schedule: 60 in x 5/8 in web, 80 in at Pier 2 on the S10 typical haunch (57 ft '
                       '7 1/2 in and 57 ft 5 1/2 in radii to 20 ft from the pier); pier-segment flanges '
                       f'{R1.exterior(j) and "26 in x 2 3/4 in" or "24 in x 2 1/4 in"} to the field splices 40 ft from '
                       'the pier, field flanges 1 3/4 in. The web is continuous through the splices (S9/S10 splice '
                       f'details), so the field segments sit {dtf(j) / IN:g} in lower than the pier segment and the '
                       'fillers take up the step. Girder end 4 1/2 in beyond the abutment bearing centre line '
                       '(S9/S10 elevations); the Abutment 3 end cope of the top flange and web is not modelled. Top '
                       'of steel over the pier segment follows the proposed grade less the deck and a nominal haunch; '
                       'camber and cross-girder top elevations are not reconciled.',
                  dims=dict(end_extension_beyond_bearing_m=END_EXT, overall_length_m=round(SPAN + END_EXT, 6),
                            field_segment_drop_m=dtf(j)))
            record_girders[pid] = field_rings

    # haunches: regenerated on the stepped girder top and the extended ends (sheet 60 deck soffit unchanged)
    haunch_range = []
    for j, y in enumerate(YS):
        b = (26 if R1.exterior(j) else 24) * IN
        for i in range(2):
            pid = f'haunch_{i}_{j}'
            old = native(pid)
            v = old.vertices
            top = np.abs(v[:, 2] - (R1.surface(v[:, 0], v[:, 1]) - SLAB)) < 2e-5
            bot = np.abs(v[:, 2] - (R1.surface_old(v[:, 0], y) - SLAB - CLEAR)) < 2e-5
            a, e = (-SPAN, 0.0) if i == 0 else (0.0, SPAN)
            stations = np.linspace(a, e, max(3, int((e - a) / .7)))
            on_station = np.abs((v[:, 0] + K * y)[:, None] - stations[None, :]).min(axis=1) < 2e-5
            if not ((top ^ bot).all() and len(v) == 4 * len(stations) and on_station.all()):
                raise ValueError(f'{pid}: unexpected first-round haunch')
            s = -1 if i == 0 else 1
            stations = np.unique(np.r_[stations, s * (SPAN + END_EXT), s * SPLICE, s * (SPLICE + SLIVER)])
            new = R1.sweep([(-b / 2, 0), (b / 2, 0), (b / 2, 1), (-b / 2, 1)], stations,
                           lambda u, dy, t, y=y, j=j: (R1.sx(u, y), y + dy,
                                                       (1 - t) * top_new(u, j) +
                                                       t * (float(R1.surface(R1.sx(u, y), y + dy)) - SLAB)))
            nv = new.vertices
            upper = nv[:, 2] > np.array([top_new(x + K * y, j) for x in nv[:, 0]]) + 1e-6
            thick = nv[upper, 2] - np.array([top_new(x + K * y, j) for x in nv[upper, 0]])
            if thick.min() < .02:
                raise ValueError(f'{pid}: haunch thinner than 20 mm')
            haunch_range.append((thick.min(), thick.max()))
            store(pid, new, new_topology=True, replace=True,
                  note='Haunch follows modeled grade, not a construction screed or camber table. Top on the corrected '
                       '2 % deck soffit; bottom on the girder top, stepping down at the field splices where the field '
                       'segments are lower (S9/S10) and running out to the girder end 4 1/2 in beyond the bearing.',
                  dims=dict(minimum_thickness_m=round(float(thick.min()), 4),
                            maximum_thickness_m=round(float(thick.max()), 4)))

    # field splices A/B: web plates unchanged, flange splice plates and fillers per S9/S10
    for j, y in enumerate(YS):
        ext = R1.exterior(j)
        cw, ct, cl = COVER[ext]
        fw, ft, fl = FILLER[ext]
        for si, us in enumerate([-SPLICE, SPLICE]):
            pid = f'girder_{j + 1}_splice_{si + 1}'
            plates, bolts = R1.splice_meshes(us, j, R1.depth_new(us, j), R1.TW)
            if not (R1.same_points(plates.vertices, native(pid).vertices) and
                    R1.same_points(bolts.vertices, native(pid + '_bolts').vertices)):
                raise ValueError(f'{pid}: first-round splice not reproduced')
            # web splice plates exactly as before (centred on the pier web, which is the reference)
            x, z = R1.sx(us, y), top_pier(us, j) - R1.depth_new(us, j) / 2
            webw, webh, plate = 1.2, 1.37, .0159
            pieces = [box(x - webw / 2, x + webw / 2, y + q * (R1.TW / 2 + plate / 2) - plate / 2,
                          y + q * (R1.TW / 2 + plate / 2) + plate / 2, z - webh / 2, z + webh / 2) for q in (-1, 1)]
            if not np.isclose(z, top_new(us, j) - R1.tf_pier(j) - WEB / 2, atol=1e-9):
                raise ValueError(f'{pid}: web plates off the web')
            field = np.sign(us)                                    # field side: away from Pier 2

            def plate_on(u0, u1, width, zfun, j=j, y=y):
                st = np.linspace(min(u0, u1), max(u0, u1), 9)
                return R1.sweep([(-width / 2, 0), (width / 2, 0), (width / 2, 1), (-width / 2, 1)], st,
                                lambda u, dy, t: (R1.sx(u, y), y + dy, zfun(u, t)))

            lo, hi = us - cl / 2, us + cl / 2
            pieces += [plate_on(lo, hi, cw, lambda u, t: top_pier(u, j) + t * ct),               # top splice plate
                       plate_on(lo, hi, cw, lambda u, t: bottom_pier(u, j) - ct + t * ct)]       # bottom splice plate
            f0, f1 = us + field * (cl / 2 - fl), us + field * cl / 2
            pieces += [plate_on(f0, f1, fw, lambda u, t: top_pier(u, j) - ft + t * ft),          # top filler
                       plate_on(f0, f1, fw, lambda u, t: bottom_pier(u, j) + t * ft)]            # bottom filler
            mesh = concat(pieces)
            src = 'S9' if ext else 'S10'
            store(pid, mesh, new_topology=True, replace=True,
                  basis=f'{src} field splice (A & B) detail; plate envelope reconstruction',
                  dims=dict(splice_plate_m=[cw, ct, cl], filler_plate_m=[fw, ft, fl],
                            web_plate_width_m=webw, web_plate_height_m=webh),
                  note=f'{src} field splice: {cw / IN:.0f} in x {"7/8" if ext else "1"} in x '
                       f'{"6 ft 3 in" if ext else "6 ft 9 in"} splice plates top and bottom on the outer faces of the '
                       f'pier flanges and of {cw / IN:.0f} in x {"1" if ext else "1/2"} in x '
                       f'{"3 ft 0 in" if ext else "3 ft 3 in"} fillers on the field flanges, following the girder '
                       'grade; webs aligned. Web plates on the 5/8 in web remain the representative 1.2 m x 1.37 m '
                       f'envelope ({src}: 19 in x 5/8 in x 4 ft 6 in); inner 10 in splice bars, flange bolts and '
                       'fabrication holes omitted.')

    # abutment bearing stiffeners (on the bearing lines) move down with the field segments
    for j, y in enumerate(YS):
        for si, u in ((0, -SPAN), (8, SPAN)):
            pid = f'stiffener_{j}_{si}'
            mesh = native(pid)
            v = mesh.vertices.copy()
            zt, zb = top_pier(u, j) - R1.TF_FIELD, top_pier(u, j) - R1.TF_FIELD - WEB
            hi, lo = np.isclose(v[:, 2], zt, atol=2e-5), np.isclose(v[:, 2], zb, atol=2e-5)
            if not (hi | lo).all():
                raise ValueError(f'{pid}: unexpected first-round bearing stiffener')
            v[:, 2] -= dtf(j)
            store(pid, trimesh.Trimesh(v, mesh.faces, process=False),
                  note='Lowered with the field segment (webs aligned at the S9/S10 field splices).')

    # abutment bearing envelopes: the load-plate block now ends on the lowered girder bottom and, with the girder
    # running past the bearing, its top face follows the girder grade (sheet 58: tapered top plates at Abutment 3)
    for bi, u in ((1, -SPAN), (3, SPAN)):
        for j, y in enumerate(YS):
            pid = f'B{bi}_bearing_{j + 1}'
            mesh = native(pid)
            v = mesh.vertices.copy()
            bottom = top_pier(u, j) - R1.TF_FIELD * 2 - WEB
            hi = np.isclose(v[:, 2], bottom, atol=2e-5)
            if hi.sum() != 4 or len(np.unique(np.round(v[:, 2], 5))) != 3:
                raise ValueError(f'{pid}: unexpected first-round bearing envelope')
            v[hi, 2] = [top_new(x + K * y, j) - R1.TF_FIELD * 2 - WEB for x in v[hi, 0]]
            lh = parts[pid]['dimensions']['load_plate_thickness_m']
            store(pid, trimesh.Trimesh(v, mesh.faces, process=False),
                  dims=dict(load_plate_thickness_m=round(lh - dtf(j), 6)),
                  note=f'Load-plate block {dtf(j) / IN:g} in shorter at the bearing centre line, to the field segment '
                       'lowered at the S9/S10 splices; top face on the girder bottom along the grade (derived stack).')

    # ------------------------------------------------------------------ 3. backwall tops (sheets 56, 61, 62)
    backwall_gap = {}
    for bi, u in ((1, -SPAN), (3, SPAN)):
        pid = f'abut_{bi}_backwall'
        old = native(pid)
        v = old.vertices
        st = [u - .78, u - .48] if bi == 1 else [u + .48, u + .78]
        seat = v[:, 2].min()
        top = np.abs(v[:, 2] - (R1.surface(v[:, 0], v[:, 1]) - SLAB)) < 2e-5
        on_station = np.abs((v[:, 0] + K * v[:, 1])[:, None] - np.array(st)[None, :]).min(axis=1) < 2e-5
        if not (len(v) == 8 and top.sum() == 4 and np.allclose(v[~top, 2], seat) and on_station.all() and
                np.allclose(np.abs(v[:, 1]), HALF, atol=2e-5)):
            raise ValueError(f'{pid}: unexpected first-round backwall')
        mid = (st[0] + st[1]) / 2
        backwall_gap[pid] = round(float(R1.surface(R1.sx(mid, 0), 0) - SLAB -
                                        ((R1.surface(R1.sx(mid, -HALF), -HALF) + R1.surface(R1.sx(mid, HALF), HALF)) / 2
                                         - SLAB)), 4)
        ys = [-HALF, -ROAD, 0.0, HALF]                          # the deck section's breaks (level north walk zone)
        prof = [(q, 0) for q in ys] + [(q, 1) for q in ys[::-1]]
        # Abutment 3: the wall runs 0.17 m past the deck end (U1) under the 1 ft approach slab; it steps down to the
        # approach soffit there (sheet 62 sections C-C / D-D: deck and approach slab both bear on the end bent)
        under_approach = bi == 3 and st[0] < R1.U1 < st[1]
        stations = [st[0], R1.U1, R1.U1 + 1e-4, st[1]] if under_approach else st

        def soffit(a, yy):
            return float(R1.surface(R1.sx(a, yy), yy)) - (FT if a > R1.U1 + 1e-6 else SLAB)

        new = R1.sweep(prof, stations, lambda a, yy, t, seat=seat: (R1.sx(a, yy), yy,
                                                                     (1 - t) * seat + t * soffit(a, yy)))
        store(pid, new, new_topology=True, replace=True,
              note='Semi-integral end detail and local pavement ledges are simplified. Top on the corrected deck '
                   'soffit across the full width, breaking at the crown and the north curb line like the deck section '
                   f'(sheets 56, 61-62); the two-corner top had left about {backwall_gap[pid] * 1000:.0f} mm open '
                   'under the crown.' + (' Beyond the deck end the top steps down to the 1 ft approach-slab soffit.'
                                         if under_approach else ''))

    # ------------------------------------------------------------------ checks across parts
    for j, y in enumerate(YS):
        for i in range(2):
            g = native(f'girder_{i}_{j}').vertices
            if (R1.surface(g[:, 0], g[:, 1]) - SLAB - g[:, 2]).min() <= 0:
                raise ValueError(f'girder_{i}_{j} penetrates the deck')
        for si in (1, 2):
            sp = native(f'girder_{j + 1}_splice_{si}').vertices
            if (R1.surface(sp[:, 0], sp[:, 1]) - SLAB - sp[:, 2]).min() <= 0:
                raise ValueError(f'girder_{j + 1}_splice_{si} reaches the deck soffit')
        for bi, u in ((1, -SPAN), (3, SPAN)):
            bear = native(f'B{bi}_bearing_{j + 1}')
            g = native(f'girder_{0 if bi == 1 else 1}_{j}').vertices
            near = np.unique(g[np.abs(g[:, 0] + K * y - u) < .6, 0])
            ring_bottom = np.array([g[g[:, 0] == x, 2].min() for x in near])
            ring_fn = np.array([top_new(x + K * y, j) - 2 * R1.TF_FIELD - WEB for x in near])
            tops = bear.vertices[bear.vertices[:, 2] > bear.vertices[:, 2].min() + .2]
            top_fn = np.array([top_new(x + K * y, j) - 2 * R1.TF_FIELD - WEB for x in tops[:, 0]])
            if len(tops) != 4 or np.abs(tops[:, 2] - top_fn).max() > 1e-5 or np.abs(ring_bottom - ring_fn).max() > 1e-5:
                raise ValueError(f'B{bi}_bearing_{j + 1}: not under the girder bottom')

    # ------------------------------------------------------------------ manifest bookkeeping
    for d in manifest['detail_coverage']:
        if d['feature'] == 'Retained steel details':
            d['detail'] += (' Field splices per S9/S10: webs aligned, 1 in / 1/2 in fillers and 26 in x 7/8 in / '
                            '24 in x 1 in splice plates; girder ends 4 1/2 in beyond the abutment bearings.')
    hmin, hmax = min(a for a, _ in haunch_range), max(b for _, b in haunch_range)
    replacements = [
        dict(id='haunch-thickness', parts='haunch_*', source='sheets 52, 55, 60; S9, S10',
             deviation=f'With the 2 % deck over the retained girder tops the haunches are {hmin * 1000:.0f}-'
                       f'{hmax * 1000:.0f} mm thick (the model had a nominal 90 mm): the field segments sit 1 in '
                       '(girders 1, 8) / 1/2 in lower than the pier segments, as the S9/S10 splices require, and near '
                       'Abutment 1 the sheet 52 vertical curve west of Sta. 13+40 raises the deck by up to 15 mm over '
                       'the original profile function.',
             reason='Girder elevations are retained from the original model; no screed or camber table is '
                    'reconstructed (screed data is in the contract documents, not in the plans).'),
        dict(id='splice-web-plates', parts='girder_*_splice_*, girder_*_splice_*_bolts', source='S9, S10',
             deviation='Web splice plates are the representative 1.2 m long x 1.37 m envelope with a 12 x 10 visual '
                       'bolt grid; S9/S10 give two 19 in x 5/8 in x 4 ft 6 in web plates. Inner 10 in x 1 in splice '
                       'bars and flange bolts are omitted.',
             reason='Bolt pattern not reconstructed; the flange splice plates and fillers are modelled to S9/S10.')]
    deviations = list(manifest.get('known_deviations', []))
    for rep in replacements:
        ids = [d.get('id') for d in deviations]
        if rep['id'] in ids:
            deviations[ids.index(rep['id'])] = rep
        else:
            deviations.append(rep)
    manifest['known_deviations'] = deviations

    gltf['buffers'][0]['byteLength'] = len(binary)
    while len(binary) % 4:
        binary.append(0)
    encoded = json.dumps(gltf, ensure_ascii=True, separators=(',', ':')).encode()
    encoded += b' ' * ((-len(encoded)) % 4)
    out = (struct.pack('<III', 0x46546c67, 2, 28 + len(encoded) + len(binary)) +
           struct.pack('<II', len(encoded), 0x4e4f534a) + encoded + struct.pack('<II', len(binary), 0x004e4942) + binary)
    previous_revision = manifest.get('revision')
    manifest['review_geometry_correction_2'] = TAG
    manifest['revision'] = REVISION
    manifest['review_geometry_correction_2_record'] = dict(
        source_pdf_pages=[56, 61, 62, 100, 101], printed_sheets=['56', '61', '62', 'S9', 'S10'],
        previous_revision=previous_revision,
        corrections={
            'field_splices': 'S9/S10 splice details (A & B): web continuous, field segments lowered by the flange '
                             'step (1 in girders 1, 8; 1/2 in girders 2-7); splice plates 26 x 7/8 in x 6 ft 3 in '
                             '(S9) / 24 x 1 in x 6 ft 9 in (S10) on the pier flanges and on 26 x 1 in x 3 ft 0 in / '
                             '24 x 1/2 in x 3 ft 3 in fillers; haunches, abutment bearing stiffeners and abutment '
                             'bearing load-plate blocks follow the lowered field segments.',
            'girder_ends': 'S9/S10 elevations: girder ends 4 1/2 in (0.1143 m) beyond the abutment bearing centre '
                           'lines; haunches extended with them.',
            'backwall_tops': 'Sheets 56, 61-62: backwall tops on the deck soffit with the crown and north curb-line '
                             'breaks of the deck section; '
                             'gap at the crown before: ' + ', '.join(f'{k} {v * 1000:.0f} mm'
                                                                     for k, v in backwall_gap.items()) + '.'},
        rejected={'S10 Span B field flange width': 'The S10 splice (A & B) detail gives 24 in x 1 3/4 in field flanges '
                                                   'and 24 in splice plates and fillers for both splices; the Span B '
                                                   'elevation labels read 24 in (the same hand-lettered 4 as the '
                                                   '24 in x 2 1/4 in labels), not 20 in. Unchanged.'},
        deferred={'F4 TTX transitions': 'Unchanged: see known_deviations ttx-transitions.'},
        changed_parts=geometry, before_glb_sha256=before, after_glb_sha256=hashlib.sha256(out).hexdigest())
    record = manifest['review_geometry_correction_2_record']
    print(json.dumps({k: (v if k != 'changed_parts' else f'{len(v)} parts') for k, v in record.items()}, indent=1))
    print(f'haunch thickness {hmin * 1000:.1f}-{hmax * 1000:.1f} mm')
    if dry_run:
        print('Dry run, nothing written.')
        return out, manifest
    backup.mkdir(exist_ok=True)
    (backup / f'{BID}_before_review_correction_2.glb').write_bytes(original)
    (backup / f'{BID}_manifest_before_review_correction_2.json').write_bytes(mp.read_bytes())
    path.write_bytes(out)
    mp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return out, manifest


if __name__ == '__main__':
    correct(dry_run='--dry-run' in sys.argv)

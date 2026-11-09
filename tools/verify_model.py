#!/usr/bin/env python3
"""
Dimensional verification of a generated bridge model against bridges/<folder>/bridge.json.

Works on the exported GLB without Blender (pure Python + numpy), or on the .blend when bpy is importable.

    python3 tools/verify_model.py --all                      # every bridge that has a model/bridge_<id>.glb
    python3 tools/verify_model.py 07620                      # one bridge (GLB)
    python3 tools/verify_model.py 07620 --blend              # same checks on blender/out/07620/bridge.blend (needs bpy)
    python3 tools/verify_model.py 07620 --json out.json      # machine-readable report

Exit code 0 = no FAIL, 1 = at least one FAIL, 2 = model missing.

Model conventions (see blender/bridge_gen.py): feet; X = along the bridge (station), Y = left, Z = up, deck top at Z = 0.
The GLB is exported Y-up (glTF convention) and converted back here. Node names are stable and are what the checks key on:
  DeckSurface, Slab | DeckSlab, Parapet_L/R, Coping_L/R, Girder_<i>, ConcreteBeams, Fabric_<side>,
  Abut<k>_stem/_backwall/_wing<side>, Pier<k>_cap/_wall/_col<sgn>/_pile<i>, ApproachSlab<0|1>, Water, Road_<name>, Ballast.
"""
import argparse, json, math, os, struct, sys
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRIDGES_DIR = os.path.join(ROOT, 'bridges')

# ----------------------------------------------------------------------------------------------------------- loaders
def _node_world_matrices(gltf):
    nodes = gltf.get('nodes', [])
    def local(n):
        if 'matrix' in n:
            return np.array(n['matrix'], dtype=float).reshape(4, 4).T
        T = np.eye(4)
        s = n.get('scale', [1, 1, 1]); r = n.get('rotation', [0, 0, 0, 1]); t = n.get('translation', [0, 0, 0])
        x, y, z, w = r
        R = np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                      [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                      [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
        T[:3, :3] = R * np.array(s)[None, :]; T[:3, 3] = t
        return T
    world = [None] * len(nodes)
    parent = {}
    for i, n in enumerate(nodes):
        for c in n.get('children', []): parent[c] = i
    def W(i):
        if world[i] is None:
            L = local(nodes[i]); world[i] = L if i not in parent else W(parent[i]) @ L
        return world[i]
    for i in range(len(nodes)): W(i)
    return world

def load_glb(path):
    """-> list of dict(name, min, max) with axis-aligned bounds in Blender coordinates (X along, Y left, Z up)."""
    with open(path, 'rb') as f:
        magic, version, length = struct.unpack('<4sII', f.read(12))
        assert magic == b'glTF', 'not a GLB file'
        clen, ctype = struct.unpack('<II', f.read(8)); gltf = json.loads(f.read(clen).decode('utf-8'))
    world = _node_world_matrices(gltf)
    acc = gltf.get('accessors', []); meshes = gltf.get('meshes', [])
    nodes = gltf.get('nodes', []); parent = {}
    for i, n in enumerate(nodes):
        for c in n.get('children', []): parent[c] = i
    def in_twin(i):
        while i is not None:
            if nodes[i].get('name', '').startswith(('TwinBridge', 'TwinSource')): return True
            i = parent.get(i)
        return False
    out = []
    for i, n in enumerate(nodes):
        if 'mesh' not in n or in_twin(i): continue
        m = meshes[n['mesh']]; corners = []
        for p in m.get('primitives', []):
            a = acc[p['attributes']['POSITION']]
            if 'min' not in a or 'max' not in a: continue
            lo, hi = np.array(a['min'], float), np.array(a['max'], float)
            for cx in (lo[0], hi[0]):
                for cy in (lo[1], hi[1]):
                    for cz in (lo[2], hi[2]): corners.append((cx, cy, cz, 1.0))
        if not corners: continue
        P = (world[i] @ np.array(corners).T).T[:, :3]
        # glTF Y-up -> Blender Z-up:  bx = gx, by = -gz, bz = gy
        B = np.stack([P[:, 0], -P[:, 2], P[:, 1]], 1)
        out.append(dict(name=n.get('name', f'node{i}'), min=B.min(0), max=B.max(0)))
    return out

def load_blend(path):
    import bpy
    from mathutils import Vector
    bpy.ops.wm.open_mainfile(filepath=path)
    out = []
    for ob in bpy.data.objects:
        if ob.type != 'MESH': continue
        if any(c.name.startswith(('TwinSource', 'Twin')) for c in ob.users_collection): continue   # twin copies
        P = np.array([ob.matrix_world @ Vector(c) for c in ob.bound_box])
        out.append(dict(name=ob.name, min=P.min(0), max=P.max(0)))
    return out

# ----------------------------------------------------------------------------------------------------------- checks
class Report:
    def __init__(self): self.rows = []
    def add(self, check, expected, actual, tol, unit='ft', note=''):
        if expected is None or actual is None:
            status = 'WARN' if actual is None else 'INFO'
        else:
            try: status = 'PASS' if abs(float(actual) - float(expected)) <= tol else 'FAIL'
            except (TypeError, ValueError): status = 'PASS' if actual == expected else 'FAIL'
        self.rows.append(dict(check=check, expected=expected, actual=actual, tolerance=tol, unit=unit, status=status, note=note))
    def info(self, check, actual, note=''):
        self.rows.append(dict(check=check, expected=None, actual=actual, tolerance=None, unit='', status='INFO', note=note))
    @property
    def failed(self): return any(r['status'] == 'FAIL' for r in self.rows)
    def markdown(self, title):
        s = [f'## {title}', '', '| Check | Expected | Model | Tol. | Status | Note |', '|---|---|---|---|---|---|']
        fmt = lambda v: '' if v is None else (f'{v:.2f}' if isinstance(v, float) else str(v))
        for r in self.rows:
            s.append(f"| {r['check']} | {fmt(r['expected'])} | {fmt(r['actual'])} | {fmt(r['tolerance'])} | **{r['status']}** | {r['note']} |")
        n = {k: sum(1 for r in self.rows if r['status'] == k) for k in ('PASS', 'FAIL', 'WARN', 'INFO')}
        s += ['', f"PASS {n['PASS']} · FAIL {n['FAIL']} · WARN {n['WARN']} · INFO {n['INFO']}", '']
        return '\n'.join(s)

def find(nodes, prefix=None, exact=None):
    if exact is not None: return [n for n in nodes if n['name'] == exact]
    return [n for n in nodes if n['name'].startswith(prefix)]

def union(ns):
    if not ns: return None
    return dict(min=np.min([n['min'] for n in ns], 0), max=np.max([n['max'] for n in ns], 0))

def ext(b, axis): return None if b is None else float(b['max'][axis] - b['min'][axis])
def centre(b, axis): return None if b is None else float((b['max'][axis] + b['min'][axis]) / 2)

def verify(folder, nodes, rep):
    J = json.load(open(os.path.join(BRIDGES_DIR, folder, 'bridge.json')))
    g = J['geometry_ft']; spans = [s['length'] for s in g['spans']]; L = sum(spans); W = g['deck_width_out_to_out']; Wr = g['roadway_width']
    skew = math.radians(g.get('skew_deg', 0)); stations = np.cumsum([0] + spans)
    names = {n['name'] for n in nodes}
    rep.info('nodes in model', len(nodes))
    # --- deck / slab
    slab = union(find(nodes, exact='Slab') or find(nodes, exact='DeckSlab'))
    if slab is None: rep.add('slab / deck slab present', True, False, 0, '')
    else:
        rep.add('deck width out-to-out (slab Y extent)', W, ext(slab, 1), 0.25, note='NBI item 52')
        xext = ext(slab, 0)
        rep.add('length between abutment lines (slab X extent minus skew offset)', L, xext - W * abs(math.tan(skew)), 0.5, note=f"sum of spans; NBI item 49 structure length = {g['structure_length']} (includes backwalls)")
        if abs(skew) > 1e-6:
            rep.add('skew angle derived from slab footprint', math.degrees(skew), math.degrees(math.atan2(xext - L, W)), 1.0, unit='deg', note='NBI item 34')
        rep.add('deck top at Z = 0', 0.0, float(slab['max'][2]), 0.1)
    ds = union(find(nodes, exact='DeckSurface'))
    rep.add('roadway width curb-to-curb (DeckSurface Y extent)', Wr, ext(ds, 1), 0.25, note='NBI item 51')
    # --- parapets
    for side in 'LR':
        p = union(find(nodes, exact=f'Parapet_{side}'))
        kind = g.get('railing', {}).get('type', '')
        h_exp = 2.67 if 'safety' in kind.lower() or 'nj' in kind.lower() else 2.75
        rep.add(f'parapet {side} height', h_exp, ext(p, 2), 0.15, note=kind[:50])
        if p is not None:
            rep.add(f'parapet {side} runs full length', L, ext(p, 0), 1.0, note='between abutment lines')
    # --- substructure
    sub = g['substructure']
    units = {n['name'].split('_')[0] for n in nodes if (n['name'].startswith('Abut') and n['name'][4:5].isdigit()) or (n['name'].startswith('Pier') and n['name'][4:5].isdigit())}
    rep.add('number of substructure units', len(sub), len(units), 0, '')
    for k, s in enumerate(sub):
        x_exp = float(stations[k]); typ = s['type'].lower()
        if 'abutment' in typ:
            stem = union(find(nodes, exact=f'Abut{k}_stem'))
            ahead = 1 if k == 0 else -1
            rep.add(f"{s['id']} stem centre (4.5 ft stem behind the support line)", x_exp - ahead * 2.25 * math.cos(skew), centre(stem, 0), 0.5)
            if stem is not None: rep.add(f"{s['id']} length", s.get('length'), (ext(stem, 1) - 4.5 * math.sin(abs(skew))) / math.cos(skew), 2.5, note="stem is W+1 ft long in the model (4.5 ft thick box rotated by the skew)")
            wings = find(nodes, prefix=f'Abut{k}_wing')
            rep.add(f"{s['id']} wingwalls", 2, len(wings), 0, '')
        else:
            cap = union(find(nodes, exact=f'Pier{k}_cap'))
            rep.add(f"{s['id']} cap centred on station", x_exp, centre(cap, 0), 0.75)
            if 'length' in s and cap is not None:
                Lcap = ext(cap, 1) / max(math.cos(skew), 1e-6) if abs(skew) > 1e-6 else ext(cap, 1)
                rep.add(f"{s['id']} length", s['length'], Lcap, 2.0, note=s['type'][:60])
            if 'columns' in s:
                rep.add(f"{s['id']} round columns", s['columns'], len(find(nodes, prefix=f'Pier{k}_col')), 0, '')
            if 'piles' in s:
                rep.add(f"{s['id']} piles", s['piles'], len(find(nodes, prefix=f'Pier{k}_pile')), 0, '')
            if 'wall' in typ and 'frame' not in typ and 'column' not in typ:
                rep.add(f"{s['id']} solid wall present", True, f'Pier{k}_wall' in names, 0, '')
    # --- superstructure members
    st = g.get('steel')
    if st:
        girders = find(nodes, prefix='Girder_')
        rep.add('steel girder lines', st['beam_lines'], len(girders), 0, '')
        gb = union(girders)
        if gb is not None:
            steel_from = next((stations[i] for i, sp in enumerate(g['spans']) if 'steel' in sp['type'].lower()), 0.0)
            rep.add('steel girders start at first steel span', float(steel_from), float(gb['min'][0]), 1.0)
            rep.add('steel girders end at last abutment', L, float(gb['max'][0]), 1.0)
            rep.add('girder depth (W36 ~ 3.0 ft)', 3.0, ext(girders[0], 2), 0.2)
    cs = [sp for sp in g['spans'] if 'concrete beam' in sp['type'].lower()]
    if cs:
        cb = union(find(nodes, exact='ConcreteBeams'))
        rep.add('concrete approach-span beams present', True, cb is not None, 0, '')
        if cb is not None: rep.add('concrete beams span length', cs[0]['length'], ext(cb, 0), 1.0)
    fence = g.get('railing', {}).get('fence')
    if fence:
        fab = union(find(nodes, prefix='Fabric_'))
        rr_span = next((i for i, sp in enumerate(g['spans']) if 'rail' in sp.get('over', '').lower()), None)
        if rr_span is not None:
            rep.add('chain-link fence over the railroad span (start)', float(stations[rr_span]), None if fab is None else float(fab['min'][0]), 1.0)
            rep.add('chain-link fence over the railroad span (end)', float(stations[rr_span + 1]), None if fab is None else float(fab['max'][0]), 1.0)
    # --- clearances / water
    ch = g.get('channel')
    if ch and 'water_level_below_deck' in ch:
        water = union(find(nodes, exact='Water'))
        rep.add('water surface below deck', ch['water_level_below_deck'], None if water is None else -float(water['max'][2]), 0.2, note='NBI channel profile')
    if 'min_vertical_underclearance' in g:
        girders = union(find(nodes, prefix='Girder_')); road = union([n for n in nodes if n['name'].startswith('Road_')])
        if girders is not None and road is not None:
            rep.add('vertical under-clearance to the street', g['min_vertical_underclearance'], float(girders['min'][2] - road['max'][2]), 0.5, note='NBI item 54')
    # --- approach slabs
    apr = g.get('approach_slabs')
    if apr:
        for e in (0, 1):
            a = union(find(nodes, exact=f'ApproachSlab{e}'))
            exp = apr.get('length') or (apr.get('lengths') or [20.5])[min(e, len(apr.get('lengths', [1])) - 1)]
            wr = apr.get('width', Wr)
            rep.add(f'approach slab {e} length', float(exp), None if a is None else ext(a, 0) - wr * abs(math.tan(skew)), 1.0, note='both modelled 20.5 ft' if apr.get('lengths') else '')
    core = [n for n in nodes if not n['name'].startswith(('FarGround', 'Terrain', 'Tree', 'Road', 'Approach', 'Shoulder', 'Water', 'CreekBed', 'Ballast', 'Rail', 'Ties', 'Sidewalk', 'WBeam', 'GRposts'))]
    if core:
        rep.info('structure bounding box X (ft)', f"{min(n['min'][0] for n in core):.1f} .. {max(n['max'][0] for n in core):.1f}")
        rep.info('structure bounding box Z (ft)', f"{min(n['min'][2] for n in core):.1f} .. {max(n['max'][2] for n in core):.1f}")
    return J

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('ids', nargs='*', help='bridge id(s), e.g. 07620 19027 41750')
    ap.add_argument('--all', action='store_true'); ap.add_argument('--blend', action='store_true', help='check blender/out/<id>/bridge.blend with bpy')
    ap.add_argument('--json', help='write the combined report here'); ap.add_argument('--md', help='write a markdown report here')
    a = ap.parse_args()
    folders = sorted(d for d in os.listdir(BRIDGES_DIR) if os.path.isdir(os.path.join(BRIDGES_DIR, d)) and d[:5].isdigit())
    if not a.all and a.ids: folders = [f for f in folders if f[:5] in a.ids or f[:5].lstrip('0') in [i.lstrip('0') for i in a.ids]]
    if not folders: print('no bridge folders matched'); return 2
    all_rows = {}; md = ['# Model verification report', '']; failed = False; missing = False
    for f in folders:
        bid = f[:5]
        path = os.path.join(ROOT, 'blender', 'out', bid, 'bridge.blend') if a.blend else os.path.join(BRIDGES_DIR, f, 'model', f'bridge_{bid}.glb')
        if not os.path.exists(path):
            print(f'[{bid}] model not found: {path}'); missing = True; continue
        nodes = load_blend(path) if a.blend else load_glb(path)
        rep = Report(); J = verify(f, nodes, rep)
        title = f"{J['name']} ({f}) — {os.path.relpath(path, ROOT)}"
        print(rep.markdown(title)); md.append(rep.markdown(title))
        all_rows[f] = rep.rows; failed |= rep.failed
        od = os.path.join(BRIDGES_DIR, f, 'verification'); os.makedirs(od, exist_ok=True)
        json.dump(rep.rows, open(os.path.join(od, 'dimension_report.json'), 'w'), indent=1, default=float)
        open(os.path.join(od, 'dimension_report.md'), 'w').write(rep.markdown(title))
    if a.json: json.dump(all_rows, open(a.json, 'w'), indent=1, default=float)
    if a.md: open(a.md, 'w').write('\n'.join(md))
    if missing and not all_rows: return 2
    return 1 if failed else 0

if __name__ == '__main__':
    sys.exit(main())

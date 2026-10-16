"""Frozen assumed-input frame/shell demonstrations for the Indiana collection.

SI units, native X/Y/Z, linear elastic pressure increments. Display geometry is
never used as an FE mesh. Every section and support is explicit in the ledger.
Run in an isolated process: OpenSees owns a process-global domain.
"""
import math
import platform
from collections import defaultdict

from fem.global_model import Domain, read_domain, rect, circle, steel_shape, global_benchmarks, lin
from fem.solver import benchmarks, polygon_properties

CASES = {'demo_uniform': 'Assumed model: full-deck pressure increment',
         'demo_eccentric': 'Assumed model: left-half pressure increment'}
PARAMETERS = {
    'pressure_kPa': dict(label='Pressure (kPa)', default=1, min=.1, max=20, step=.1),
    'steel_E_GPa': dict(label='Assumed steel E (GPa)', default=200, min=100, max=250, step=5),
    'concrete_E_GPa': dict(label='Assumed concrete E (GPa)', default=30, min=10, max=50, step=1),
    'bearing_kz_MNpm': dict(label='Assumed bearing stiffness (MN/m per bearing; MN/m² for line beds)', default=800, min=100, max=3000, step=100),
    'load_factor': dict(label='Load multiplier', default=1, min=.1, max=5, step=.1),
}


def parameters_for_ledger(ledger):
    """Hide a control if no analyzed element uses that material or connection."""
    values=ledger['values']; out=dict(PARAMETERS)
    steel=any(b.get('material')=='steel' for b in values['beams']) or any(c.get('material')=='steel' for s in values['supports'] for c in s.get('columns',[]))
    flexible=any(any(not b.get('integral') for b in s['bearings']) or s.get('line_connection') and not s['line_connection'].get('integral') for s in values['supports'])
    if not steel: out.pop('steel_E_GPa')
    if not flexible: out.pop('bearing_kz_MNpm')
    return out


def settings(raw):
    if not isinstance(raw, dict) or set(raw) - (set(PARAMETERS) | {'case', 'foundation'}):
        raise ValueError('Unknown collection demonstration setting.')
    out = {key: raw.get(key, p['default']) for key, p in PARAMETERS.items()}
    for key, value in out.items():
        p = PARAMETERS[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not p['min'] <= value <= p['max']:
            raise ValueError(f'{p["label"]}: enter a finite number from {p["min"]} to {p["max"]}.')
    out['case'] = raw.get('case', 'demo_uniform')
    out['foundation'] = raw.get('foundation', 'fixed')
    if not isinstance(out['case'], str) or out['case'] not in CASES:
        raise ValueError('Unknown collection demonstration load case.')
    if out['foundation'] not in ('fixed', 'elastic'):
        raise ValueError('Select fixed or elastic assumed foundations.')
    return out


def section(spec):
    kind = spec['kind']
    if kind == 'I': return steel_shape(*spec['dimensions_m'])
    if kind == 'rectangle': return rect(*spec['dimensions_m'])
    if kind == 'circle': return circle(spec['diameter_m'])
    if kind == 'pipe':
        diameter=spec['diameter_m']; inner=diameter-2*spec['thickness_m']
        if inner<=0: raise ValueError('Pipe wall must leave an open interior.')
        out=circle(diameter)
        out.update(A=math.pi*(diameter**2-inner**2)/4,
                   Iy=math.pi*(diameter**4-inner**4)/64,
                   Iz=math.pi*(diameter**4-inner**4)/64,
                   J=math.pi*(diameter**4-inner**4)/32)
        return out
    if kind == 'polygon':
        p = spec['profile_yz_m']
        def properties(points):
            a,z,iy=polygon_properties(points); _,y,iz=polygon_properties([[z,y] for y,z in points])
            return a,y,z,iy,iz
        rings=[(1,properties(p))]+[(-1,properties(h)) for h in spec.get('void_profiles_yz_m',[])]
        area=sum(sign*v[0] for sign,v in rings)
        if area<=0: raise ValueError('Void exceeds outer section area.')
        cy=sum(sign*v[0]*v[1] for sign,v in rings)/area
        cz=sum(sign*v[0]*v[2] for sign,v in rings)/area
        iy=sum(sign*(v[3]+v[0]*(v[2]-cz)**2) for sign,v in rings)
        iz=sum(sign*(v[4]+v[0]*(v[1]-cy)**2) for sign,v in rings)
        return dict(A=area, Iy=iy, Iz=iz, J=spec['torsion_J_m4'],
                    fibers=[(y-cy, z-cz) for y, z in p])
    raise ValueError('Unsupported explicit section: '+kind)


def rounded(x): return round(float(x), 7)


def subdivide(points, step):
    points = sorted(set(rounded(x) for x in points))
    result = []
    for a, b in zip(points, points[1:]):
        if b-a > 1e-7:
            result.extend(lin(a, b, max(1, math.ceil((b-a)/step)))[:-1])
    return [rounded(x) for x in result+[points[-1]]]


def tributary(points, i):
    return ((points[i]-points[i-1])/2 if i else 0)+((points[i+1]-points[i])/2 if i+1 < len(points) else 0)


def create(ledger, options, density=1):
    v = ledger['values']; deck = v['deck']; d = Domain()
    d.extra_springs = []; d.support_nodes = defaultdict(list); d.base_supports={}
    ec = options['concrete_E_GPa']*1e9; es = options['steel_E_GPa']*1e9
    k = v['skew_dx_dy']; midpoint = (deck['y0_m']+deck['y1_m'])/2
    def xyz(u, y, z): return [u+k*y, y, z]
    def spring(a, b, stiffness):
        mats = []
        for value in stiffness:
            d.mat += 1; d.o.uniaxialMaterial('Elastic', d.mat, value); mats.append(d.mat)
        d.e += 1; d.o.element('zeroLength', d.e, a, b, '-mat', *mats, '-dir', 1, 2, 3, 4, 5, 6)
        d.extra_springs.append([a, b])
    def foundation(n, scale=1, retained=False):
        if options['foundation'] == 'fixed' and not retained:
            d.fix(n); d.base_supports[n]=si
        else:
            g = d.node(d.nodes[n]); d.fix(g)
            d.base_supports[g]=si
            stiffness=v['fixed_reference_stiffness_Npm_Nm'] if options['foundation']=='fixed' else v['foundation_stiffness_Npm_Nm']
            spring(g, n, [value*scale for value in stiffness])
    units = v['continuity_units']
    mesh_decks = {}; beam_nodes = {}
    for ui, unit in enumerate(units):
        segments = [b for b in v['beams'] if b['unit'] == ui]
        bearings = [b for s in v['supports'] for b in s['bearings'] if b['unit'] == ui]
        ubreaks = [unit['u0_m'], unit['u1_m']]
        ubreaks += [q for b in segments for q in [b['u0_m'], b['u1_m']]]
        ubreaks += [b['u_m'] for b in bearings]
        ubreaks += [s['u_m'] for s in v['supports'] if s.get('line_connection') and unit['u0_m'] <= s['u_m'] <= unit['u1_m']]
        ubreaks += [q for p in deck['patches'] for q in [p['u0_m'], p['u1_m']] if unit['u0_m'] < q < unit['u1_m']]
        ybreaks = [deck['y0_m'], deck['y1_m'], midpoint]+[b['y_m'] for b in segments]
        ybreaks += [q for p in deck['patches'] for q in [p['y0_m'], p['y1_m']]]
        us = subdivide(ubreaks, v.get('mesh_step_u_m', 3)/density)
        ys = subdivide(ybreaks, v.get('mesh_step_y_m', 1.5)/density)
        if us[0] < unit['u0_m']-1e-6 or us[-1] > unit['u1_m']+1e-6:
            raise ValueError('Beam/bearing station outside its declared continuity unit.')
        grid = {(u,y): d.node(xyz(u,y,deck['midplane_z_m'])) for u in us for y in ys}
        mesh_decks[ui] = (grid, us, ys)
        for a,b in zip(us,us[1:]):
            for c,e in zip(ys,ys[1:]):
                um, ym = (a+b)/2, (c+e)/2
                patches = [p for p in deck['patches'] if p['u0_m']-1e-6 <= um <= p['u1_m']+1e-6 and p['y0_m']-1e-6 <= ym <= p['y1_m']+1e-6]
                if len(patches) != 1: raise ValueError('Deck patch partition has a gap or overlap.')
                ns = [grid[a,c],grid[b,c],grid[b,e],grid[a,e]]
                d.shell(ns, ec, .2, deck['thickness_m'], patches[0]['cid'], 'deck')
                q = options['pressure_kPa']*1000*options['load_factor']
                if options['case'] == 'demo_eccentric' and ym >= midpoint: q = 0
                for n in ns: d.force(n,[0,0,-q*(b-a)*(e-c)/4])
        for b in segments:
            y = rounded(b['y_m'])
            chain = [u for u in us if b['u0_m']-1e-6 <= u <= b['u1_m']+1e-6]
            for u in chain:
                key = (ui,u,y)
                if key not in beam_nodes: beam_nodes[key] = d.offset(grid[u,y],xyz(u,y,b['centroid_z_m']))
            for a,c in zip(chain,chain[1:]):
                sec = section(b['section'])
                d.beam(beam_nodes[ui,a,y],beam_nodes[ui,c,y],sec,es if b['material']=='steel' else ec,
                       .3 if b['material']=='steel' else .2,b['cid'],'girder')
    # Cap/column/wall coordinates are explicit source-specific ledger inputs.
    for si,s in enumerate(v['supports']):
        cap = s.get('cap'); walls = s.get('walls',[]); columns = s.get('columns',[])
        bearing_ys = [b['y_m'] for b in s['bearings']]
        line_grids = [(ui,grid,ys) for ui,(grid,us,ys) in mesh_decks.items()
                      if s.get('line_connection') and rounded(s['u_m']) in us]
        ybreaks = bearing_ys+[q for _,_,ys in line_grids for q in ys]
        ybreaks += [q for w in walls for q in [w['y0_m'],w['y1_m']]]+[c['y_m'] for c in columns]
        if cap: ybreaks += [cap['y0_m'],cap['y1_m']]
        if not ybreaks: raise ValueError('Support has no connections.')
        ys = subdivide(ybreaks, 1.5/density)
        top = {y:d.node(xyz(s['u_m'],y,s['top_z_m'])) for y in ys}
        if cap:
            for a,b in zip(ys,ys[1:]): d.beam(top[a],top[b],section(cap['section']),ec,.2,cap['cid'],'cap')
        for wall in walls:
            wy = [y for y in ys if wall['y0_m']-1e-6 <= y <= wall['y1_m']+1e-6]
            zs = subdivide([wall['bottom_z_m'],s['top_z_m']],1.5/density)
            grid = {(y,z):top[y] if z==zs[-1] else d.node(xyz(s['u_m'],y,z)) for y in wy for z in zs}
            for a,b in zip(wy,wy[1:]):
                for c,e in zip(zs,zs[1:]):
                    d.shell([grid[a,c],grid[b,c],grid[b,e],grid[a,e]],ec,.2,wall['thickness_m'],wall['cid'],'wall')
            for i,y in enumerate(wy): foundation(grid[y,zs[0]],tributary(wy,i)*math.sqrt(1+k*k))
        for col in columns:
            y = rounded(col['y_m']); zs = subdivide([col['bottom_z_m'],s['top_z_m']],2/density)
            ns = [d.node(xyz(s['u_m'],y,z)) for z in zs[:-1]]+[top[y]]
            for a,b in zip(ns,ns[1:]): d.beam(a,b,section(col['section']),es if col.get('material')=='steel' else ec,.3 if col.get('material')=='steel' else .2,col['cid'],col.get('family','column'))
            foundation(ns[0])
        if not walls and not columns:
            for i,y in enumerate(ys): foundation(top[y],max(tributary(ys,i),.01),retained=True)
        # If no cap exists, every top node must belong to a structural wall.
        if not cap and walls and any(not any(w['y0_m']-1e-6 <= y <= w['y1_m']+1e-6 for w in walls) for y in ys):
            raise ValueError('Unsupported gap in a wall support.')
        for b in s['bearings']:
            ui = b['unit']; grid,us,dy = mesh_decks[ui]
            u, y, by = rounded(b['u_m']),rounded(b['y_m']),rounded(b.get('beam_y_m',b['y_m']))
            upper = d.offset(grid[u,by],xyz(u,y,b['z_m']))
            lower = d.offset(top[y],d.nodes[upper])
            stiff = [v['bearing_horizontal_Npm']]*2+[options['bearing_kz_MNpm']*1e6]+[v['bearing_rotation_Nm']]*3
            if b.get('integral'):
                spring(lower,upper,v['integral_connection_stiffness_Npm_Nm'])
            else: d.pad(lower,upper,stiff,b['cid'],b['area_m2'])
            d.support_nodes[si].append(lower)
        for ui,grid,dy in line_grids:
            for i,y in enumerate(dy):
                # This grid may have support subdivisions that differ from deck y.
                upper = grid[rounded(s['u_m']),y]
                lower = d.offset(top[y],d.nodes[upper]); scale = tributary(dy,i)*math.sqrt(1+k*k)
                if s['line_connection'].get('integral'):
                    spring(lower,upper,[value*scale for value in v['integral_connection_stiffness_Npm_Nm']])
                else:
                    stiff = [v['bearing_horizontal_Npm']*scale]*2+[options['bearing_kz_MNpm']*1e6*scale]+[v['bearing_rotation_Nm']*scale]*3
                    d.pad(lower,upper,stiff,s['line_connection']['cid'],s['line_connection']['width_m']*scale)
                d.support_nodes[si].append(lower)
    edges = [b['nodes'] for b in d.beams]+[s['nodes'] for s in d.shells]+[p['nodes'] for p in d.pads]+d.links+d.extra_springs
    neighbors = defaultdict(set)
    for ns in edges:
        for n in ns: neighbors[n].update(set(ns)-{n})
    seen=set(d.fixed); todo=list(seen)
    while todo:
        for n in neighbors[todo.pop()]-seen: seen.add(n); todo.append(n)
    if seen != set(d.nodes): raise RuntimeError('Collection model has disconnected FE nodes.')
    if set(d.groups) != set(ledger['analyzed_component_ids']):
        raise RuntimeError('Collection component coverage mismatch: '+str(set(d.groups)^set(ledger['analyzed_component_ids'])))
    return d


def run_model(ledger, options, density=1):
    d = create(ledger, options, density); out = read_domain(d); bid=ledger['bridge_id']
    for m in out['members']:
        m['component_id']=bid+':'+m['component_id'].split(':',1)[1]; m.pop('raw_beam',None)
    for e in out['mesh']['beams']+out['mesh']['shells']:
        e['component_id']=bid+':'+e['component_id'].split(':',1)[1]
    out['mesh']['springs']=[p['nodes'] for p in d.pads]+d.extra_springs
    out['max_stress_MPa']=max(m['peak']['stress_MPa'] for m in out['members'])
    out['max_deflection_mm']=max(abs(n['displacement_m'][2])*1000 for n in out['mesh']['nodes'])
    out['family_summary']={f:dict(member_count=sum(m['family']==f for m in out['members']),
        max_stress_MPa=max(m['peak']['stress_MPa'] for m in out['members'] if m['family']==f),
        max_deflection_mm=max(m['max_deflection_mm'] for m in out['members'] if m['family']==f)) for f in sorted(set(d.groups.values()))}
    v=ledger['values']; deck=v['deck']; q=options['pressure_kPa']*options['load_factor']
    expected=(deck['u1_m']-deck['u0_m'])*(deck['y1_m']-deck['y0_m'])*q
    if options['case']=='demo_eccentric': expected/=2
    if abs(out['total_load_kN']-expected)>1e-6*expected: raise RuntimeError('Pressure resultant does not match the declared deck area.')
    # Characteristic length is bridge-specific, unlike the historical shared recovery normalization.
    scale=max(deck['u1_m']-deck['u0_m'],deck['y1_m']-deck['y0_m'],1)
    residual=[a+b for a,b in zip(out['load_vector_N_Nm'],out['reaction_vector_N_Nm'])]
    force=max(abs(a) for a in residual[:3])/(expected*1000)
    moment=max(abs(a) for a in residual[3:])/(expected*1000*scale)
    if max(force,moment)>1e-6: raise RuntimeError('Bridge-specific force/moment equilibrium failed.')
    out['equilibrium']=[dict(force_error=force,moment_error=moment,characteristic_length_m=scale)]
    out['all_nodes_connected_to_supports']=True
    out['mesh_density']=density
    out['support_lines_m']=[s['u_m'] for s in v['supports']]
    out['support_reactions']=[dict(support_index=i,station_u_m=s['u_m'],
        vertical_kN=sum(r['forces_N_Nm'][2] for r in out['reactions'] if d.base_supports[r['node']]==i)/1000)
        for i,s in enumerate(v['supports'])]
    return out


def solve_demo(snapshot):
    import openseespy.opensees as ops
    ledger=snapshot['ledger']; options=settings(snapshot['settings'])
    tests=benchmarks()+global_benchmarks()
    coarse=run_model(ledger,options,1); fine=run_model(ledger,options,2)
    refinements=[]
    def compare(label,a,b):
        change=abs(a-b)/max(abs(b),1e-9)
        refinements.append(dict(quantity=label,coarse=a,fine=b,relative_change=change,tolerance=.05,passed=change<.05))
    compare('Global nodal vertical displacement',coarse['max_deflection_mm'],fine['max_deflection_mm'])
    if not refinements[0]['passed']:
        coarse,fine=fine,run_model(ledger,options,3)
        refinements=[]
        compare('Global nodal vertical displacement',coarse['max_deflection_mm'],fine['max_deflection_mm'])
    if not refinements[0]['passed']: raise RuntimeError('Global displacement mesh change exceeds 5%; result rejected.')
    for family in fine['family_summary']:
        for field in ['max_stress_MPa','max_deflection_mm']:
            compare(family+'.'+field,coarse['family_summary'][family][field],fine['family_summary'][family][field])
    warnings=[r['quantity'] for r in refinements if not r['passed']]
    fine.update(schema_version=3,bridge_id=ledger['bridge_id'],case=options['case'],case_title=CASES[options['case']],settings=options,
        scope='assumed_collection_frame_shell_increment',demonstration=True,display_mapping='native_coordinates',
        solver=dict(name='OpenSees',version=ops.version(),python=platform.python_version(),platform=platform.platform()),
        units=dict(length='m',force='kN',stress='MPa',displacement='mm'),
        verification=dict(passed=True,field_validated=False,all_local_peaks_converged=not warnings,mesh_warnings=warnings,
            benchmarks=tests,mesh_refinement=refinements,equilibrium_tolerance=1e-6,
            coarse_mesh_density=coarse['mesh_density'],fine_mesh_density=fine['mesh_density']),
        assumptions=ledger['assumptions'],snapshot=snapshot,sensitivity=[],
        displacement_note='Assumed-input linear pressure increment only. No self-weight, prestress history, cracking, load rating or present-day validation. Native analytical geometry is flattened and idealized as recorded in the ledger.',
        stress_measures=dict(beam='Signed axial plus biaxial nominal fiber normal stress; no section torsional shear recovery',
            shell='Principal surface normal stresses at four integration points; unaveraged element envelopes',
            bearing='Signed mean normal pressure in bilateral springs; no uplift/contact nonlinearity'))
    return fine

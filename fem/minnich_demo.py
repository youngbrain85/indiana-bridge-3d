"""Hypothetical Minnich Road frame/shell demonstration, SI units, native Z up.

The visual reconstruction supplies identifiers and a geometric scaffold, not
verified structural inputs. Assumptions are explicit, editable and snapshotted.
"""
import math
import platform
from collections import defaultdict

from fem.global_model import Domain, circle, rect, steel_shape, lin, read_domain, global_benchmarks
from fem.solver import FT, IN, benchmarks

CASES = {
    'demo_uniform': 'Assumed model: full-deck pressure increment',
    'demo_eccentric': 'Assumed model: left-half pressure increment',
}
PARAMETERS = {
    'pressure_kPa': dict(label='Pressure (kPa)', default=1, min=.1, max=20, step=.1),
    'steel_E_GPa': dict(label='Assumed steel E (GPa)', default=200, min=100, max=250, step=5),
    'concrete_E_GPa': dict(label='Assumed concrete E (GPa)', default=30, min=10, max=50, step=1),
    'bearing_kz_MNpm': dict(label='Assumed bearing vertical stiffness (MN/m)', default=800, min=100, max=3000, step=100),
    'column_diameter_m': dict(label='Assumed column diameter (m)', default=.9, min=.5, max=1.5, step=.05),
    'load_factor': dict(label='Load multiplier', default=1, min=.1, max=5, step=.1),
}


def settings(raw):
    if not isinstance(raw, dict) or set(raw) - (set(PARAMETERS) | {'case', 'foundation'}):
        raise ValueError('Unknown demonstration setting.')
    result = {k: raw.get(k, p['default']) for k, p in PARAMETERS.items()}
    for key, value in result.items():
        p = PARAMETERS[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not p['min'] <= value <= p['max']:
            raise ValueError(f'{p["label"]}: enter a finite number from {p["min"]} to {p["max"]}.')
    result['case'] = raw.get('case', 'demo_uniform')
    result['foundation'] = raw.get('foundation', 'fixed')
    if not isinstance(result['case'], str) or result['case'] not in CASES:
        raise ValueError('Unknown demonstration load case.')
    if result['foundation'] not in ('fixed', 'elastic'):
        raise ValueError('Select fixed or elastic assumed foundations.')
    return result


def subdivide(breaks, step):
    result = []
    for a, b in zip(breaks, breaks[1:]):
        result += lin(a, b, max(1, math.ceil((b-a)/step)))[:-1]
    return result + [breaks[-1]]


def create(ledger, options, density=1):
    v = ledger['values']; d = Domain(); d.foundation_springs = []
    es = options['steel_E_GPa'] * 1e9; ec = options['concrete_E_GPa'] * 1e9
    width = v['deck_width_m']; length = v['deck_length_m']; h = v['deck_thickness_m']
    skew = -math.tan(math.radians(v['skew_deg']))
    bs = [-sum(v['spans_m'])/2]
    for s in v['spans_m']: bs.append(bs[-1] + s)
    ys = v['girder_y_m']; zdeck = v['flat_deck_top_m'] - h/2
    def xyz(u, y, z): return [u+skew*y, y, z]
    def depth(u):
        if u < bs[1]:
            a, b = bs[0]+48.4167*FT, bs[0]+53.4167*FT
            return (36 + 32*min(1, max(0, (u-a)/(b-a))))*IN
        if u > bs[3]:
            a, b = bs[3]+12*FT, bs[3]+17*FT
            return (68 - 33.75*min(1, max(0, (u-a)/(b-a))))*IN
        return 68*IN
    def zbeam(u): return zdeck - h/2 - v['haunch_m'] - depth(u)/2
    # Deliberately skew-aligned X-frame stations; topology is an assumption.
    rows = {i: lin(a+.8, b-.8, max(2, int((b-a)/7))-1) for i, (a,b) in enumerate(zip(bs, bs[1:]))}
    breaks = sorted(set([-length/2, length/2]+bs+[u for row in rows.values() for u in row]+
                        [bs[0]+48.4167*FT, bs[0]+53.4167*FT, bs[3]+12*FT, bs[3]+17*FT]))
    us = subdivide(breaks, 4/density)
    ty = subdivide(sorted(set([-width/2, width/2, 0]+ys)), 1.4/density)
    deck = {(u,y):d.node(xyz(u,y,zdeck)) for u in us for y in ty}
    for a,b in zip(us,us[1:]):
        for c,e in zip(ty,ty[1:]):
            ns = [deck[a,c],deck[b,c],deck[b,e],deck[a,e]]
            d.shell(ns,ec,.2,h,'deck','deck')
            q = options['pressure_kPa']*1000*options['load_factor']
            if options['case']=='demo_eccentric' and (c+e)/2 >= 0: q = 0
            for n in ns: d.force(n,[0,0,-q*(b-a)*(e-c)/4])
    girders = {}
    for j,y in enumerate(ys):
        for u in us:
            if bs[0]-1e-9 <= u <= bs[-1]+1e-9:
                girders[u,j] = d.offset(deck[u,y],xyz(u,y,zbeam(u)))
        for i,(a,b) in enumerate(zip(bs,bs[1:])):
            chain = [u for u in us if a-1e-9 <= u <= b+1e-9]
            for lo,hi in zip(chain,chain[1:]):
                sec = steel_shape(depth((lo+hi)/2),v['flange_width_m'],v['web_thickness_m'],v['flange_thickness_m'])
                d.beam(girders[lo,j],girders[hi,j],sec,es,.3,f'plate_{i}_{j}','girder')
    for i,row in rows.items():
        for r,u in enumerate(row):
            for j in [0,1,2,4,5,6]:
                for sense in [-1,1]:
                    ns = []
                    for side,k in enumerate([j,j+1]):
                        z = zbeam(u) + sense*(1 if side==0 else -1)*(depth(u)/2-.12)
                        ns.append(d.offset(deck[u,ys[k]],xyz(u,ys[k],z)))
                    d.beam(*ns,rect(.10,.012),es,.3,f'frame_{i}_{r}_{j}','cross_frame')
    def support(n):
        if options['foundation']=='fixed':
            d.fix(n)
        else:
            ground = d.node(d.nodes[n]); d.fix(ground)
            mats = []
            for value in v['foundation_stiffness_Npm_Nm']:
                d.mat += 1; d.o.uniaxialMaterial('Elastic',d.mat,value); mats.append(d.mat)
            d.e += 1
            d.o.element('zeroLength',d.e,ground,n,'-mat',*mats,'-dir',1,2,3,4,5,6)
            d.foundation_springs.append([ground,n])
    for bi,u in enumerate(bs):
        for bank,(y0,y1) in enumerate([(-width/2,-.01),(.01,width/2)]):
            cap_id = f'cap_{bi}_{bank}'
            bounds = v['support_geometry'][cap_id]
            zcap = (bounds[0][2]+bounds[1][2])/2
            colys = lin(y0+.9,y1-.9,2)
            beam_js = list(range(4*bank,4*bank+4))
            cy = subdivide(sorted(set([y0,y1]+colys+[ys[j] for j in beam_js])),2/density)
            capnodes = {y:d.node(xyz(u,y,zcap)) for y in cy}
            for a,b in zip(cy,cy[1:]):
                d.beam(capnodes[a],capnodes[b],rect(.84,.95),ec,.2,cap_id,'cap')
            for j,y in enumerate(colys):
                if bi in [0,4]:
                    support(capnodes[y])
                else:
                    cid = f'column_{bi}_{bank}_{j}'
                    bottom = v['support_geometry'][cid][0][2]
                    ns = [d.node(xyz(u,y,z)) for z in lin(bottom,zcap,max(2,math.ceil((zcap-bottom)/(2/density))))[:-1]]+[capnodes[y]]
                    for a,b in zip(ns,ns[1:]): d.beam(a,b,circle(options['column_diameter_m']),ec,.2,cid,'column')
                    support(ns[0])
            for j in beam_js:
                upper = girders[u,j]
                lower = d.offset(capnodes[ys[j]],d.nodes[upper])
                d.pad(lower,upper,[v['bearing_horizontal_Npm']]*2+[options['bearing_kz_MNpm']*1e6]+[v['bearing_rotation_Nm']]*3,
                      f'Bent_{bi+1}_bearing_{j+1}',v['bearing_area_m2'])
    edges = [b['nodes'] for b in d.beams]+[s['nodes'] for s in d.shells]+[p['nodes'] for p in d.pads]+d.links+d.foundation_springs
    neighbors = defaultdict(set)
    for ns in edges:
        for n in ns: neighbors[n].update(set(ns)-{n})
    seen = set(d.fixed); todo = list(seen)
    while todo:
        for n in neighbors[todo.pop()]-seen: seen.add(n); todo.append(n)
    if seen != set(d.nodes): raise RuntimeError('Disconnected FE nodes found.')
    if set(d.groups) != set(ledger['analyzed_component_ids']): raise RuntimeError('Demonstration component coverage mismatch.')
    return d


def run_model(ledger, options, density=1):
    d = create(ledger,options,density)
    result = read_domain(d)
    # Reuse the tested recovery routines with this bridge's identity.
    for m in result['members']:
        m['component_id'] = 'minnich-road:'+m['component_id'].split(':',1)[1]
        m.pop('raw_beam',None)
    for e in result['mesh']['beams']+result['mesh']['shells']:
        e['component_id'] = 'minnich-road:'+e['component_id'].split(':',1)[1]
    result['mesh']['springs'] = [p['nodes'] for p in d.pads]+d.foundation_springs
    result['max_stress_MPa'] = max(m['peak']['stress_MPa'] for m in result['members'])
    # Shell samples are at element centers: use nodal displacement for global peak.
    result['max_deflection_mm'] = max(abs(n['displacement_m'][2])*1000 for n in result['mesh']['nodes'])
    result['family_summary'] = {f:dict(member_count=sum(m['family']==f for m in result['members']),
        max_stress_MPa=max(m['peak']['stress_MPa'] for m in result['members'] if m['family']==f),
        max_deflection_mm=max(m['max_deflection_mm'] for m in result['members'] if m['family']==f))
        for f in sorted({m['family'] for m in result['members']})}
    expected = ledger['values']['deck_length_m']*ledger['values']['deck_width_m']*options['pressure_kPa']*options['load_factor']
    if options['case']=='demo_eccentric': expected /= 2
    if abs(result['total_load_kN']-expected)>1e-6*expected: raise RuntimeError('Applied pressure resultant is incorrect.')
    result['all_nodes_connected_to_supports'] = True
    return result


def solve_demo(snapshot):
    import openseespy.opensees as ops
    ledger = snapshot['ledger']; options = settings(snapshot['settings'])
    tests = benchmarks()+global_benchmarks()
    coarse = run_model(ledger,options,1); fine = run_model(ledger,options,2)
    refinement = []
    def compare(label,a,b):
        change = abs(a-b)/max(abs(b),1e-9)
        refinement.append(dict(quantity=label,coarse=a,fine=b,relative_change=change,tolerance=.05,passed=change<.05))
    compare('Global nodal vertical displacement',coarse['max_deflection_mm'],fine['max_deflection_mm'])
    if not refinement[-1]['passed']: raise RuntimeError('Global displacement mesh change exceeds 5%; no result accepted.')
    for family in fine['family_summary']:
        for field in ['max_stress_MPa','max_deflection_mm']:
            compare(family+'.'+field,coarse['family_summary'][family][field],fine['family_summary'][family][field])
    warnings = [r['quantity'] for r in refinement if not r['passed']]
    other = dict(options,foundation='elastic' if options['foundation']=='fixed' else 'fixed')
    sensitivity = run_model(ledger,other,2)
    fine.update(schema_version=3,bridge_id='minnich-road',case=options['case'],case_title=CASES[options['case']],settings=options,
        scope='hypothetical_connected_frame_shell_demo',demonstration=True,display_mapping='native_coordinates',
        solver=dict(name='OpenSees',version=ops.version(),python=platform.python_version(),platform=platform.platform()),
        units=dict(length='m',force='kN',stress='MPa',displacement='mm'),
        verification=dict(passed=True,field_validated=False,all_local_peaks_converged=not warnings,mesh_warnings=warnings,
            benchmarks=tests,mesh_refinement=refinement,equilibrium_tolerance=1e-6),
        assumptions=ledger['assumptions'],snapshot=snapshot,
        sensitivity=[dict(label='Assumed '+other['foundation']+' support bases',settings=other,
            max_stress_MPa=sensitivity['max_stress_MPa'],max_deflection_mm=sensitivity['max_deflection_mm'])],
        displacement_note='Pressure increment only; no self-weight, traffic rating, construction history or present-day condition. Editable assumptions change the analytical model, not the GLB geometry.',
        stress_measures=dict(beam='Nominal axial + biaxial fiber normal stress',shell='Principal surface stress at integration points',bearing='Signed mean normal pressure; tension is possible in the bilateral spring idealization'))
    return fine

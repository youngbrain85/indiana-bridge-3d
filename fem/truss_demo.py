"""Dedicated US421 open-top truss frame/shell pressure demonstration, SI.

All rotational connection restraint is an explicit rigid-frame assumption.
No overhead braces, support clamps on upper nodes, or display-box sections.
"""
import math
import platform
from collections import defaultdict
from fem.collection_demo import settings, PARAMETERS, subdivide
from fem.global_model import Domain, read_domain, steel_shape, global_benchmarks, lin
from fem.solver import benchmarks

CASES={'demo_uniform':'Main truss and complete main deck: full-width pressure increment',
       'demo_eccentric':'Main truss and complete main deck: left-half pressure increment'}


def parameters_for_ledger(ledger):
    out={key:dict(value) for key,value in PARAMETERS.items()}
    out['bearing_kz_MNpm']['label']='Assumed truss-shoe vertical stiffness (MN/m per shoe)'
    out['pressure_kPa']['label']='Pressure on the complete main deck, including end overhangs (kPa)'
    return out


def plate_section(plates):
    """Nonoverlapping (width,depth,y,z) rectangles; open-section Saint-Venant J."""
    area=sum(b*h for b,h,y,z in plates)
    cy=sum(b*h*y for b,h,y,z in plates)/area
    cz=sum(b*h*z for b,h,y,z in plates)/area
    iy=sum(b*h**3/12+b*h*(z-cz)**2 for b,h,y,z in plates)
    iz=sum(h*b**3/12+b*h*(y-cy)**2 for b,h,y,z in plates)
    fibers=[(y+dy-cy,z+dz-cz) for b,h,y,z in plates for dy in [-b/2,b/2] for dz in [-h/2,h/2]]
    return dict(A=area,Iy=iy,Iz=iz,J=sum(max(b,h)*min(b,h)**3/3 for b,h,y,z in plates),fibers=fibers)


def section(spec):
    if spec['kind']=='I':return steel_shape(*spec['dimensions_m'])
    if spec['kind']=='angle':
        b,t=spec['leg_m'],spec['wall_m']
        return plate_section([(t,b,t/2,b/2),(b-t,t,(b+t)/2,t/2)])
    if spec['kind']=='twin_channels':
        d,b,f,t,c=[spec[k] for k in ['depth_m','width_m','flange_m','wall_m','cover_m']]
        plates=[]
        for sign in [-1,1]:
            plates.append((t,d-2*t,sign*(b/2-t/2),0))
            for zz in [-1,1]:plates.append((f,t,sign*(b/2-f/2),zz*(d/2-t/2)))
        if c:plates.append((b,c,0,d/2+c/2))
        return plate_section(plates)
    raise ValueError('Unsupported assumed truss section.')


def create(ledger,options,density=1):
    if ledger.get('analytical_family')!='truss':raise ValueError('Dedicated truss ledger required.')
    if density not in [1,2,3,4]:raise ValueError('Mesh density must be 1, 2, 3 or 4.')
    v=ledger['values'];deck=v['deck'];d=Domain();es=options['steel_E_GPa']*1e9;ec=options['concrete_E_GPa']*1e9
    d.extra_springs=[];d.base_supports={};d.top_braces=[];d.truss_upper_nodes=[]
    px=v['panel_x_m'];zs=v['lower_chord_z_m'];ty=abs(v['truss_y_m'][0]);oy=v['floorbeam_outer_y_m']
    rnd=lambda a:round(float(a),7)
    # Preserve bearing/panel stations and refine the two slab-only cantilevers.
    breaks=px+[(px[a]+px[b])/2 for a,b in [(0,2),(2,4),(4,5),(5,7),(7,9)]]
    breaks+=lin(deck['u0_m'],px[0],density)+lin(px[-1],deck['u1_m'],density)
    xs=subdivide(breaks,min(b-a for a,b in zip(px,px[1:]))/(v['mesh_panel_subdivisions']*density))
    ys=subdivide([deck['y0_m'],deck['y1_m'],0]+v['stringer_y_m'],v['mesh_transverse_step_m']/density)
    grid={(x,y):d.node([x,y,deck['midplane_z_m']]) for x in xs for y in ys}
    for a,b in zip(xs,xs[1:]):
        for c,e in zip(ys,ys[1:]):
            ns=[grid[a,c],grid[b,c],grid[b,e],grid[a,e]]
            d.shell(ns,ec,.2,deck['thickness_m'],'deck_B','deck')
            q=options['pressure_kPa']*1000*options['load_factor']
            if options['case']=='demo_eccentric' and (c+e)/2>=0:q=0
            for n in ns:d.force(n,[0,0,-q*(b-a)*(e-c)/4])
    lower={};upper={}
    for side,sign in [('X',1),('Y',-1)]:
        for i,x in enumerate(px):
            lower[side,i]=d.node([x,sign*ty,zs])
            upper[side,i]=lower[side,i] if i in [0,9] else d.node([x,sign*ty,zs+v['upper_heights_m'][i]])
            if i not in [0,9]:d.truss_upper_nodes.append(upper[side,i])
    # Offset floorbeams and stringers always use shell masters, not chained slaves.
    floor={};stringer={}
    fy=subdivide([-oy,-ty,ty,oy]+ys,v['mesh_transverse_step_m']/density)
    for i,x in enumerate(px):
        xx=rnd(x)
        for y in fy:
            if abs(abs(y)-ty)<1e-6:
                n=d.offset(lower['X' if y>0 else 'Y',i],[x,y,v['floorbeam_z_m']])
            elif y in ys:n=d.offset(grid[xx,y],[x,y,v['floorbeam_z_m']])
            else:n=d.node([x,y,v['floorbeam_z_m']])
            floor[i,y]=n
    for j,y in enumerate(v['stringer_y_m']):
        for x in xs:
            if rnd(px[0])<=x<=rnd(px[-1]):stringer[j,x]=d.offset(grid[x,rnd(y)],[x,y,v['stringer_z_m']])
    secs={name:section(s) for name,s in v['sections'].items()}
    def chain(a,b,spec,cid,family,segments=None):
        n=segments or v['mesh_member_subdivisions']*density
        aa=d.nodes[a];bb=d.nodes[b]
        ns=[a]+[d.node([p+(q-p)*k/n for p,q in zip(aa,bb)]) for k in range(1,n)]+[b]
        for p,q in zip(ns,ns[1:]):d.beam(p,q,secs[spec],es,.3,cid,family)
    middle={side:d.node([(px[4]+px[5])/2,sign*ty,zs+v['upper_heights_m'][4]/2]) for side,sign in [('X',1),('Y',-1)]}
    lateral_mid={}
    for a,b in [(0,2),(2,4),(4,5),(5,7),(7,9)]:
        xx=rnd((px[a]+px[b])/2)
        # Source diamond centers connect to floor system; central single-panel
        # crossing also shares a node, assumed tied to deck through its stringer.
        lateral_mid[a,b]=d.offset(grid[xx,0],[xx,0,zs-.3*.3048])
    for m in v['beams']:
        family=m['family'];cid=m['cid'];sec=m['section_name']
        if family=='lower_chord':chain(lower[m['side'],m['i']],lower[m['side'],m['i']+1],sec,cid,family)
        elif family=='upper_chord':chain(upper[m['side'],m['i']],upper[m['side'],m['i']+1],sec,cid,family)
        elif family=='vertical':chain(lower[m['side'],m['i']],upper[m['side'],m['i']],sec,cid,family)
        elif family=='diagonal':
            a=upper[m['side'],m['upper_index']];b=lower[m['side'],m['lower_index']]
            if {m['upper_index'],m['lower_index']}=={4,5}:
                mid=middle[m['side']];chain(a,mid,sec,cid,family);chain(mid,b,sec,cid,family)
            else:chain(a,b,sec,cid,family)
        elif family=='raker':
            sign=1 if m['side']=='X' else -1;i=m['i']
            a=d.offset(floor[i,rnd(sign*oy)],[px[i],sign*oy,zs+.25*.3048])
            b=d.offset(upper[m['side'],i],[px[i],sign*ty,zs+v['upper_heights_m'][i]-.5*.3048])
            chain(a,b,sec,cid,family)
        elif family=='floorbeam':
            for ya,yb in zip(fy,fy[1:]):chain(floor[m['i'],ya],floor[m['i'],yb],sec,cid,family,1)
        elif family=='stringer':
            pts=[x for x in xs if rnd(px[m['i']])<=x<=rnd(px[m['i']+1])]
            for a,b in zip(pts,pts[1:]):chain(stringer[m['j'],a],stringer[m['j'],b],sec,cid,family,1)
        elif family=='lower_lateral':
            i,j,sign=m['i'],m['j'],m['sign'];side='X' if sign>0 else 'Y';other='Y' if sign>0 else 'X'
            a=d.offset(lower[side,i],[px[i],sign*ty,zs-.3*.3048]);b=d.offset(lower[other,j],[px[j],-sign*ty,zs-.3*.3048]);mid=lateral_mid[i,j]
            chain(a,mid,sec,cid,family);chain(mid,b,sec,cid,family)
    def foundation_spring(a,b):
        mats=[]
        for value in v['foundation_stiffness_Npm_Nm']:
            d.mat+=1;d.o.uniaxialMaterial('Elastic',d.mat,value);mats.append(d.mat)
        d.e+=1;d.o.element('zeroLength',d.e,a,b,'-mat',*mats,'-dir',1,2,3,4,5,6);d.extra_springs.append([a,b])
    for si,s in enumerate(v['supports']):
        a=lower[s['side'],s['i']];xyz=[s['u_m'],s['y_m'],zs-6*.0254];up=d.offset(a,xyz);lo=d.node(xyz)
        if options['foundation']=='fixed':d.fix(lo);d.base_supports[lo]=si
        else:
            ground=d.node(xyz);d.fix(ground);d.base_supports[ground]=si;foundation_spring(ground,lo)
        b=s['bearings'][0];d.pad(lo,up,s['horizontal_Npm']+[options['bearing_kz_MNpm']*1e6]+s['rotation_Nm'],b['cid'],b['area_m2'])
    edges=[b['nodes'] for b in d.beams]+[s['nodes'] for s in d.shells]+[p['nodes'] for p in d.pads]+d.links+d.extra_springs
    adjacent=defaultdict(set)
    for ns in edges:
        for n in ns:adjacent[n].update(set(ns)-{n})
    seen=set(d.fixed);todo=list(seen)
    while todo:
        for n in adjacent[todo.pop()]-seen:seen.add(n);todo.append(n)
    if seen!=set(d.nodes):raise RuntimeError('Disconnected main-truss FE nodes.')
    if set(d.groups)!=set(ledger['analyzed_component_ids']):raise RuntimeError('Truss result/display coverage mismatch.')
    if {b for a,b in d.links}&{a for a,b in d.links}:raise RuntimeError('Chained rigid constraints found.')
    return d


def run_model(ledger,options,density=1):
    d=create(ledger,options,density);out=read_domain(d);bid=ledger['bridge_id']
    for member in out['members']:
        member['component_id']=bid+':'+member['component_id'].split(':',1)[1];member.pop('raw_beam',None)
    for e in out['mesh']['beams']+out['mesh']['shells']:e['component_id']=bid+':'+e['component_id'].split(':',1)[1]
    out['mesh']['springs']=[p['nodes'] for p in d.pads]+d.extra_springs
    out['max_stress_MPa']=max(m['peak']['stress_MPa'] for m in out['members'])
    out['max_deflection_mm']=max(abs(n['displacement_m'][2])*1000 for n in out['mesh']['nodes'])
    out['family_summary']={f:dict(member_count=sum(m['family']==f for m in out['members']),max_stress_MPa=max(m['peak']['stress_MPa'] for m in out['members'] if m['family']==f),max_deflection_mm=max(m['max_deflection_mm'] for m in out['members'] if m['family']==f)) for f in sorted(set(d.groups.values()))}
    deck=ledger['values']['deck'];expected=deck['loaded_area_m2']*options['pressure_kPa']*options['load_factor']/(2 if options['case']=='demo_eccentric' else 1)
    if abs(out['total_load_kN']-expected)>expected*1e-6:raise RuntimeError('Main-span pressure resultant does not match declared area.')
    length=deck['u1_m']-deck['u0_m'];residual=[a+b for a,b in zip(out['load_vector_N_Nm'],out['reaction_vector_N_Nm'])]
    force=max(abs(a) for a in residual[:3])/(expected*1000);moment=max(abs(a) for a in residual[3:])/(expected*1000*length)
    if max(force,moment)>1e-6:raise RuntimeError('Truss global force/moment equilibrium failed.')
    mean_x=(deck['u0_m']+deck['u1_m'])/2
    mean_y=(deck['y0_m']+deck['y1_m'])/2 if options['case']=='demo_uniform' else deck['y0_m']/2
    load_moment=[-expected*1000*mean_y,expected*1000*mean_x,0]
    centroid_error=max(abs(a-b) for a,b in zip(out['load_vector_N_Nm'][3:],load_moment))/(expected*1000*length)
    if centroid_error>1e-9:raise RuntimeError('Complete main-deck pressure centroid is incorrect.')
    out.update(equilibrium=[dict(force_error=force,moment_error=moment,characteristic_length_m=length,load_centroid_moment_error=centroid_error)],all_nodes_connected_to_supports=True,mesh_density=density,
        loaded_area_m2=deck['loaded_area_m2']/(2 if options['case']=='demo_eccentric' else 1),display_scope=ledger['display_scope'],top_cross_brace_count=0,
        load_centroid_xy_m=[mean_x,mean_y],
        support_reactions=[dict(support_index=i,station_u_m=s['u_m'],side=s['side'],end=s['end'],vertical_kN=sum(r['forces_N_Nm'][2] for r in out['reactions'] if d.base_supports[r['node']]==i)/1000) for i,s in enumerate(ledger['values']['supports'])])
    return out


def truss_benchmarks():
    """Independent pin-jointed V benchmark exercises axial force and compliance."""
    import openseespy.opensees as o
    o.wipe();o.model('basic','-ndm',2,'-ndf',2)
    o.node(1,-3,0);o.node(2,3,0);o.node(3,0,4);o.fix(1,1,1);o.fix(2,1,1)
    E=200e9;A=.01;P=10000;o.uniaxialMaterial('Elastic',1,E)
    o.element('truss',1,1,3,A,1);o.element('truss',2,2,3,A,1)
    o.timeSeries('Constant',1);o.pattern('Plain',1,1);o.load(3,0,-P)
    o.constraints('Plain');o.numberer('RCM');o.system('UmfPack');o.algorithm('Linear');o.integrator('LoadControl',1);o.analysis('Static')
    if o.analyze(1):raise RuntimeError('Independent axial truss benchmark failed.')
    actual=[-o.nodeDisp(3,2),abs(o.eleResponse(1,'axialForce')[0])];expected=[P*5/(2*E*A*.8**2),P/(2*.8)]
    tests=[]
    for label,a,b in zip(['Pin-jointed V truss displacement','Pin-jointed V truss axial force'],actual,expected):
        error=abs(a-b)/b;tests.append(dict(name=label,actual=a,expected=b,relative_error=error,tolerance=1e-9,passed=error<1e-9))
    if not all(c['passed'] for c in tests):raise RuntimeError('Truss benchmark exceeds tolerance.')
    return tests


def solve_demo(snapshot):
    import openseespy.opensees as ops
    ledger=snapshot['ledger'];options=settings(snapshot['settings']);tests=benchmarks()+global_benchmarks()+truss_benchmarks()
    if not all(t['passed'] for t in tests):raise RuntimeError('Benchmark check failed.')
    coarse=run_model(ledger,options,1);fine=run_model(ledger,options,2)
    refinement=[]
    def compare(label,a,b):
        change=abs(a-b)/max(abs(b),1e-9);refinement.append(dict(quantity=label,coarse=a,fine=b,relative_change=change,tolerance=.05,passed=change<.05))
    compare('Global nodal vertical displacement',coarse['max_deflection_mm'],fine['max_deflection_mm'])
    if not refinement[0]['passed']:
        coarse,fine=fine,run_model(ledger,options,3);refinement=[];compare('Global nodal vertical displacement',coarse['max_deflection_mm'],fine['max_deflection_mm'])
    if not refinement[0]['passed']:raise RuntimeError('Main-truss vertical displacement refinement exceeds 5%.')
    for family in fine['family_summary']:
        for field in ['max_stress_MPa','max_deflection_mm']:compare(family+'.'+field,coarse['family_summary'][family][field],fine['family_summary'][family][field])
    warnings=[r['quantity'] for r in refinement if not r['passed']]
    fine.update(schema_version=3,bridge_id=ledger['bridge_id'],case=options['case'],case_title=CASES[options['case']]+' | APPROACH SPANS EXCLUDED',settings=options,
        scope='assumed_main_truss_frame_shell_increment',analytical_family='truss',demonstration=True,field_validated=False,display_mapping='native_coordinates',
        solver=dict(name='OpenSees',version=ops.version(),python=platform.python_version(),platform=platform.platform()),units=dict(length='m',force='kN',stress='MPa',displacement='mm'),
        verification=dict(passed=True,field_validated=False,all_local_peaks_converged=not warnings,mesh_warnings=warnings,benchmarks=tests,mesh_refinement=refinement,equilibrium_tolerance=1e-6,coarse_mesh_density=coarse['mesh_density'],fine_mesh_density=fine['mesh_density']),
        assumptions=ledger['assumptions'],snapshot=snapshot,sensitivity=[],
        displacement_note='MAIN TRUSS AND DECK ONLY: 125 ft bearing-to-bearing truss plus the complete 126 ft 10.25 in main deck, including loaded shell cantilevers beyond both bearing lines. Assumed rigid frame joints and full composite deck/floor system. Open top, actual raker/lower-brace topology. Approach decks are excluded. No second-order buckling, self-weight history or load rating.',
        stress_measures=dict(beam='Signed axial plus biaxial nominal elastic fiber normal stress for assumed sections; no torsional shear, warping, buckling or connection stress.',shell='Unaveraged principal surface normal stresses at four shell integration points.',bearing='Signed nominal mean pressure from assumed bilateral spring and reference sole-plate area.'))
    return fine

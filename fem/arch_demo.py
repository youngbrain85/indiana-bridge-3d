"""Four curved arch barrels with explicit projected pressure and springing beds.

This module consumes a frozen ledger only. No GLB, PDF or source metadata is read
during a solve. Run in an isolated process because OpenSees owns a global domain.
"""
import math
import platform
from collections import defaultdict

from fem.collection_demo import PARAMETERS, settings
from fem.global_model import Domain, read_domain, global_benchmarks, lin

CASES={'demo_uniform':'Assumed arch model: full projected barrel pressure',
       'demo_eccentric':'Assumed arch model: left-half projected barrel pressure'}


def parameters_for_ledger(ledger):
    out={k:dict(v) for k,v in PARAMETERS.items() if k!='steel_E_GPa'}
    for k,v in out.items():
        v['label']=ledger.get('parameter_labels',{}).get(k,v['label'])
    return out


def curve(arch,u):
    length=arch['u1_m']-arch['u0_m']; r=(u-arch['u0_m'])/length
    a=arch['spring_intrados_z0_m']; b=arch['spring_intrados_z1_m']
    rise=arch['quadratic_crown_reference_z_m']-(a+b)/2
    intr=a+(b-a)*r+4*rise*r*(1-r)
    thick=arch['crown_vertical_thickness_m']+arch['haunch_extra_vertical_thickness_m']*(2*r-1)**2
    slope=((b-a)+4*rise*(1-2*r)+2*arch['haunch_extra_vertical_thickness_m']*(2*r-1))/length
    return intr+thick/2,thick,slope


def tributary(points,i):
    return ((points[i]-points[i-1])/2 if i else 0)+((points[i+1]-points[i])/2 if i+1<len(points) else 0)


def create(ledger,options,density=1):
    if ledger.get('analytical_family')!='arch': raise ValueError('Dedicated arch ledger required.')
    if isinstance(density,bool) or density not in (1,2,3): raise ValueError('Arch mesh density must be 1, 2 or 3.')
    v=ledger['values']; arches=v['arches']; k=v['skew_dx_dy']
    if len(arches)!=4: raise ValueError('SR 1/Wabash requires all four arch barrels.')
    d=Domain(); d.extra_springs=[]; d.base_supports={}; d.springing_info=[]; d.arch_nodes={}
    d.projected_area=0.;d.normal_thickness_range=[float('inf'),0.]
    E=options['concrete_E_GPa']*1e9; nu=v['concrete_poisson']; q=options['pressure_kPa']*1000*options['load_factor']
    nx=int(v['mesh_segments_u'])*density;ny=int(v['mesh_segments_y'])*density
    if nx<4 or ny<2 or ny%2: raise ValueError('Arch mesh must include the transverse half-load split.')
    for ai,arch in enumerate(arches):
        if arch['u1_m']<=arch['u0_m'] or arch['y1_m']<=arch['y0_m']: raise ValueError('Invalid arch extent.')
        if abs((arch['y0_m']+arch['y1_m'])/2-v['pressure_projection']['y_split_m'])>1e-10:
            raise ValueError('Half-load split must match symmetric barrel transverse limits.')
        us=lin(arch['u0_m'],arch['u1_m'],nx);ys=lin(arch['y0_m'],arch['y1_m'],ny)
        grid={(i,j):d.node([u+k*y,y,curve(arch,u)[0]]) for i,u in enumerate(us) for j,y in enumerate(ys)}
        d.arch_nodes[arch['cid']]=list(grid.values())
        for i,(a,b) in enumerate(zip(us,us[1:])):
            mid,vertical_t,slope=curve(arch,(a+b)/2)
            t=vertical_t/math.sqrt(1+(1+k*k)*slope*slope)
            if not math.isfinite(t) or t<=0: raise ValueError('Nonpositive shell thickness.')
            d.normal_thickness_range=[min(d.normal_thickness_range[0],t),max(d.normal_thickness_range[1],t)]
            for j,(c,e) in enumerate(zip(ys,ys[1:])):
                ns=[grid[i,j],grid[i+1,j],grid[i+1,j+1],grid[i,j+1]]
                d.shell(ns,E,nu,t,arch['cid'],'arch')
                loaded=options['case']=='demo_uniform' or (c+e)/2<v['pressure_projection']['y_split_m']
                if loaded:
                    area=(b-a)*(e-c);d.projected_area+=area
                    for n in ns:d.force(n,[0,0,-q*area/4])
        for end,i in enumerate([0,nx]):
            support_index=len(d.springing_info)
            d.springing_info.append(dict(arch_index=ai,component_id=arch['cid'],end='start' if end==0 else 'end',
                station_u_m=us[i],type=options['foundation'],support_index=support_index))
            for j,y in enumerate(ys):
                n=grid[i,j]
                if options['foundation']=='fixed':
                    d.fix(n);d.base_supports[n]=support_index
                else:
                    g=d.node(d.nodes[n]);d.fix(g);d.base_supports[g]=support_index
                    line=tributary(ys,j)*math.sqrt(1+k*k)
                    kz=options['bearing_kz_MNpm']*1e6;spec=v['springing']
                    stiffness=[kz*spec['horizontal_x_ratio_to_kz'],kz*spec['horizontal_y_ratio_to_kz'],kz]
                    stiffness+=spec['rotational_line_stiffness_Nm_per_rad_per_m']
                    mats=[]
                    for stiffness_value in stiffness:
                        if not math.isfinite(stiffness_value) or stiffness_value<=0:raise ValueError('Spring stiffness must be positive.')
                        d.mat+=1;d.o.uniaxialMaterial('Elastic',d.mat,stiffness_value*line);mats.append(d.mat)
                    d.e+=1;d.o.element('zeroLength',d.e,g,n,'-mat',*mats,'-dir',1,2,3,4,5,6)
                    d.extra_springs.append([g,n])
    if set(d.groups)!=set(ledger['analyzed_component_ids']):raise ValueError('Arch component mapping mismatch.')
    adjacency=defaultdict(set)
    for ns in [s['nodes'] for s in d.shells]+d.extra_springs:
        for n in ns:adjacency[n].update(set(ns)-{n})
    seen=set(d.fixed);todo=list(seen)
    while todo:
        n=todo.pop()
        for nxt in adjacency[n]-seen:seen.add(nxt);todo.append(nxt)
    if seen!=set(d.nodes):raise RuntimeError('An arch node is disconnected from springing restraints.')
    return d


def run_model(ledger,options,density=1):
    options=settings(options);d=create(ledger,options,density);out=read_domain(d);bid=ledger['bridge_id']
    for member in out['members']:
        member['component_id']=bid+':'+member['component_id'].split(':',1)[1]
        member.pop('raw_beam',None)
        member['span']=member['component_id'].split('_')[-1]
    for element in out['mesh']['shells']:
        element['component_id']=bid+':'+element['component_id'].split(':',1)[1]
    out['mesh']['springs']=d.extra_springs
    out['max_stress_MPa']=max(m['peak']['stress_MPa'] for m in out['members'])
    out['max_deflection_mm']=max(abs(n['displacement_m'][2])*1000 for n in out['mesh']['nodes'])
    # Nodal peaks, not averages at element centers, govern displacement refinement.
    disp={n['id']:n['displacement_m'] for n in out['mesh']['nodes']}
    out['arch_nodal_deflections_mm']={bid+':'+cid:max(abs(disp[n][2])*1000 for n in ns) for cid,ns in d.arch_nodes.items()}
    out['family_summary']={'arch':dict(member_count=4,max_stress_MPa=out['max_stress_MPa'],max_deflection_mm=out['max_deflection_mm'])}
    projection=ledger['values']['pressure_projection'];area=projection['full_area_m2' if options['case']=='demo_uniform' else 'left_half_area_m2']
    expected=area*options['pressure_kPa']*options['load_factor']
    if abs(d.projected_area-area)>1e-9*area or abs(out['total_load_kN']-expected)>1e-9*expected:
        raise RuntimeError('Arch load resultant does not match frozen projected pressure area.')
    characteristic=max(ledger['values']['arches'][-1]['u1_m']-ledger['values']['arches'][0]['u0_m'],1)
    residual=[a+b for a,b in zip(out['load_vector_N_Nm'],out['reaction_vector_N_Nm'])]
    force=max(abs(a) for a in residual[:3])/(expected*1000)
    moment=max(abs(a) for a in residual[3:])/(expected*1000*characteristic)
    if max(force,moment)>1e-6:raise RuntimeError('Arch force/moment equilibrium failed.')
    # The force resultant must also act at the exact intended transverse centroid.
    mean_y=0 if options['case']=='demo_uniform' else ledger['values']['arches'][0]['y0_m']/2
    mean_x=ledger['values']['skew_dx_dy']*mean_y
    expected_m=[-expected*1000*mean_y,expected*1000*mean_x,0]
    load_moment_error=max(abs(a-b) for a,b in zip(out['load_vector_N_Nm'][3:],expected_m))/(expected*1000*characteristic)
    if load_moment_error>1e-9:raise RuntimeError('Arch projected pressure centroid is incorrect.')
    springings=[]
    for info in d.springing_info:
        rs=[r for r in out['reactions'] if d.base_supports[r['node']]==info['support_index']]
        forces=[sum(r['forces_N_Nm'][i] for r in rs)/1000 for i in range(3)]
        springings.append(dict(info,horizontal_x_kN=forces[0],horizontal_y_kN=forces[1],vertical_kN=forces[2]))
    thrusts=[]
    for i in range(4):
        a,b=springings[2*i:2*i+2]
        inward=min(a['horizontal_x_kN'],-b['horizontal_x_kN'])
        if inward<1e-5*expected:raise RuntimeError('Expected compressive arch thrust was not developed at every arch.')
        thrusts.append(dict(arch_id=bid+':'+ledger['values']['arches'][i]['cid'],
            inward_horizontal_thrust_kN=inward,has_compressive_arch_action=True))
    out.update(equilibrium=[dict(force_error=force,moment_error=moment,characteristic_length_m=characteristic,
            load_centroid_moment_error=load_moment_error)],
        all_nodes_connected_to_supports=True,structural_barrels=4,independently_restrained_barrels=True,
        mesh_density=density,loaded_projected_area_m2=area,loaded_projection=projection,
        load_centroid_xy_m=[mean_x,mean_y],springing_reactions=springings,arch_thrust=thrusts,
        support_lines_m=[s['station_u_m'] for s in springings],support_reactions=springings,
        normal_shell_thickness_range_m=d.normal_thickness_range)
    return out


def arch_benchmarks():
    """Statically determinate three-hinged barrel: H=q L^2/(8 f).

    This independent curved-shell fixture has no shared code with create/curve.
    nu=0 and lateral strip constraints produce cylindrical bending. Independent
    rotations on duplicated crown nodes form the third hinge; translations tie.
    """
    d=Domain();o=d.o;L=10.;rise=2.;width=1.;q=1000.;n=24;ny=2
    crowns=[]
    for half in [0,1]:
        grid={}
        for i in range(n+1):
            x=L*(half/2+i/(2*n));z=4*rise*x*(L-x)/(L*L)
            for j in range(ny+1):
                tag=d.node([x,width*j/ny,z]);grid[i,j]=tag
                end=(half==0 and i==0) or (half==1 and i==n)
                slave=half==1 and i==0
                if not slave:o.fix(tag,int(end),1,int(end),1,0,1)
                if end:d.fixed.append(tag)
        for i in range(n):
            for j in range(ny):
                ns=[grid[i,j],grid[i+1,j],grid[i+1,j+1],grid[i,j+1]]
                d.shell(ns,30e9,0,.10,'benchmark_arch','arch')
                for tag in ns:d.force(tag,[0,0,-q*(L/(2*n))*(width/ny)/4])
        crowns.append([grid[n if half==0 else 0,j] for j in range(ny+1)])
    for a,b in zip(*crowns):o.equalDOF(a,b,1,2,3,4,6)
    result=read_domain(d)
    left=[r for r in result['reactions'] if abs(r['xyz_m'][0])<1e-10]
    actual_h=sum(r['forces_N_Nm'][0] for r in left)
    actual_v=sum(r['forces_N_Nm'][2] for r in left)
    expected_h=q*width*L*L/(8*rise);expected_v=q*width*L/2
    checks=[]
    for name,a,b in [('Three-hinged curved-shell arch horizontal thrust',actual_h,expected_h),
                     ('Three-hinged curved-shell arch vertical reaction',actual_v,expected_v)]:
        error=abs(a-b)/abs(b)
        checks.append(dict(name=name,actual=a,expected=b,relative_error=error,tolerance=1e-6,passed=error<1e-6))
    if not all(c['passed'] for c in checks):raise RuntimeError('Independent curved-arch benchmark failed: '+str(checks))
    return checks


def solve_demo(snapshot):
    import openseespy.opensees as ops
    ledger=snapshot['ledger'];options=settings(snapshot['settings'])
    tests=global_benchmarks()+arch_benchmarks()
    if not all(t['passed'] for t in tests):raise RuntimeError('Arch solver benchmark failure.')
    coarse=run_model(ledger,options,1);fine=None;refinements=[]
    max_density=min(3,int(ledger['values'].get('max_mesh_density',3)))
    for density in range(2,max_density+1):
        fine=run_model(ledger,options,density);refinements=[]
        def compare(label,a,b,required=False):
            change=abs(a-b)/max(abs(b),1e-12)
            refinements.append(dict(quantity=label,coarse=a,fine=b,relative_change=change,tolerance=.05,passed=change<.05,required_for_acceptance=required))
        compare('Global arch nodal vertical displacement',coarse['max_deflection_mm'],fine['max_deflection_mm'],True)
        for cid,disp in fine['arch_nodal_deflections_mm'].items():
            compare(cid+'.nodal_vertical_displacement',coarse['arch_nodal_deflections_mm'][cid],disp,True)
        for a,b in zip(coarse['members'],fine['members']):
            if a['component_id']!=b['component_id']:raise RuntimeError('Arch refinement member mapping changed.')
            compare(b['component_id']+'.local_shell_stress_peak',a['peak']['stress_MPa'],b['peak']['stress_MPa'])
        if all(r['passed'] for r in refinements if r['required_for_acceptance']):break
        if density<max_density:coarse=fine
    if fine is None or any(not r['passed'] for r in refinements if r['required_for_acceptance']):
        raise RuntimeError('Arch displacement mesh refinement exceeds 5% at the bounded maximum density; result rejected.')
    warnings=[r['quantity'] for r in refinements if not r['passed']]
    fine.update(schema_version=3,bridge_id=ledger['bridge_id'],case=options['case'],case_title=CASES[options['case']],settings=options,
        scope='assumed_four_arch_barrel_shell_increment',analytical_family='arch',demonstration=True,display_mapping='native_coordinates',
        solver=dict(name='OpenSees',version=ops.version(),python=platform.python_version(),platform=platform.platform()),
        units=dict(length='m',force='kN',stress='MPa',displacement='mm'),
        verification=dict(passed=True,field_validated=False,all_local_peaks_converged=not warnings,mesh_warnings=warnings,
            benchmarks=tests,mesh_refinement=refinements,equilibrium_tolerance=1e-6,
            coarse_mesh_density=coarse['mesh_density'],fine_mesh_density=fine['mesh_density'],
            all_four_arches_have_compressive_thrust=True,all_four_arch_displacements_converged=True,
            local_peak_check_scope='Maximum unaveraged shell stress envelope per arch; this does not prove convergence of every integration-point field.',
            local_stress_warnings=['Linear shell surface envelopes are not full solid stresses or reinforcement stresses.',
                'Fixed/free edge peaks and thickness transitions remain physically unvalidated even if this mesh comparison passes.']),
        assumptions=ledger['assumptions'],snapshot=snapshot,sensitivity=[],
        displacement_note='Four independently restrained curved arch barrels only. Direct vertical pressure on projected barrel footprints; no deck/fill/pier interaction, self-weight or cracking. No displacement is assigned to excluded display components.',
        stress_measures=dict(shell='Unaveraged four-integration-point principal surface normal-stress envelopes from elastic membrane and bending resultants; no transverse-shear/solid-tensor recovery.',
            beam='Not applicable: no frame beams in the bridge model.',bearing='Not applicable: springing beds transfer forces but have no claimed physical bearing area or stress.'))
    return fine

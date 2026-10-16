"""Connected 3D frame/shell model. SI, Z up; research idealizations are frozen inputs.

No GLB vertices are used as finite elements. All constraints are one-level
master/slave links; shell nodes are masters, offset beam nodes are slaves.
"""
import math
from collections import defaultdict
from fem.solver import FT, IN, LBF, PSI, PSF, section, concrete_E, polygon_properties


def lin(a, b, n):
    return [a]+[a+(b-a)*i/n for i in range(1,n)]+[b]


def cross(a, b):
    return [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]]


def rect(b, h):
    big, small = max(b,h), min(b,h)
    return dict(A=b*h, Iy=b*h**3/12, Iz=h*b**3/12,
                J=big*small**3*(1/3-.21*small/big*(1-small**4/(12*big**4))),
                fibers=[(y,z) for y in [-b/2,b/2] for z in [-h/2,h/2]])


def circle(d):
    return dict(A=math.pi*d*d/4, Iy=math.pi*d**4/64, Iz=math.pi*d**4/64,
                J=math.pi*d**4/32, fibers=[(d/2*math.cos(i*math.pi/16), d/2*math.sin(i*math.pi/16)) for i in range(32)])


def steel_shape(d, b, tw, tf):
    # Symmetric I approximation for HP; channel is used with a documented
    # symmetric flange approximation, not claimed to reproduce warping.
    a=2*b*tf+(d-2*tf)*tw
    return dict(A=a, Iy=(b*d**3-(b-tw)*(d-2*tf)**3)/12,
                Iz=(2*tf*b**3+(d-2*tf)*tw**3)/12,
                J=(2*b*tf**3+(d-2*tf)*tw**3)/3,
                fibers=[(y,z) for y in [-b/2,b/2] for z in [-d/2,d/2]])


def principal(resultants, t):
    """Both shell surfaces; no averaging across elements or different materials."""
    values=[]
    for sign in [-1,1]:
        sx,sy,tau=[resultants[i]/t+sign*6*resultants[i+3]/t**2 for i in range(3)]
        mid=(sx+sy)/2; radius=math.hypot((sx-sy)/2,tau)
        values.extend([(mid+radius)/1e6,(mid-radius)/1e6])
    return max(values), min(values)


class Domain:
    def __init__(self):
        import openseespy.opensees as ops
        self.o=ops; ops.wipe(); ops.model('basic','-ndm',3,'-ndf',6)
        self.nodes={}; self.beams=[]; self.shells=[]; self.pads=[]; self.fixed=[]
        self.loads=defaultdict(lambda:[0.0]*6); self.links=[]; self.e=0; self.mat=0
        self.groups={}; self.sections={}; self.dead=defaultdict(float)
        ops.geomTransf('Linear',1,0,0,1)
        ops.geomTransf('Linear',2,1,0,0)

    def node(self, xyz):
        tag=len(self.nodes)+1; self.nodes[tag]=list(xyz); self.o.node(tag,*xyz); return tag

    def fix(self,n):
        self.o.fix(n,1,1,1,1,1,1); self.fixed.append(n)

    def rigid(self,a,b):
        # Never let a constrained node retain another node.
        if a in {pair[1] for pair in self.links}: raise ValueError('Chained rigid constraints are not allowed.')
        self.o.rigidLink('beam',a,b); self.links.append((a,b))

    def offset(self,master,xyz):
        n=self.node(xyz); self.rigid(master,n); return n

    def force(self,n,vector):
        for i,v in enumerate(vector): self.loads[n][i]+=v

    def beam(self,a,b,sec,E,nu,cid,family,weight=0):
        self.e+=1; xyz=self.nodes[a]; uvw=self.nodes[b]
        delta=[v-u for u,v in zip(xyz,uvw)]; length=math.sqrt(sum(x*x for x in delta))
        vertical=abs(delta[2])/length>.99
        self.o.element('elasticBeamColumn',self.e,a,b,sec['A'],E,E/(2*(1+nu)),sec['J'],sec['Iy'],sec['Iz'],2 if vertical else 1)
        ex=[x/length for x in delta]; ref=[1,0,0] if vertical else [0,0,1]
        ey=cross(ref,ex); norm=math.sqrt(sum(v*v for v in ey)); ey=[v/norm for v in ey]; ez=cross(ex,ey)
        item=dict(tag=self.e,nodes=[a,b],section=sec,E=E,cid=cid,family=family,axis=[ex,ey,ez],length=length)
        self.beams.append(item); self.groups[cid]=family
        if weight:
            f=weight*sec['A']*length/2
            self.force(a,[0,0,-f]); self.force(b,[0,0,-f]); self.dead[family]+=2*f
        return item

    def shell(self,ns,E,nu,t,cid,family,weight=0):
        key=(E,nu,t)
        if key not in self.sections:
            sid=len(self.sections)+1; self.sections[key]=sid
            self.o.section('ElasticMembranePlateSection',sid,E,nu,t)
        self.e+=1; self.o.element('ShellMITC4',self.e,*ns,self.sections[key])
        a,b,c=[self.nodes[n] for n in ns[:3]]
        area=math.sqrt(sum(v*v for v in cross([v-u for u,v in zip(a,b)],[v-u for u,v in zip(b,c)])))
        self.shells.append(dict(tag=self.e,nodes=ns,t=t,cid=cid,family=family,area=area)); self.groups[cid]=family
        if weight:
            for n in ns: self.force(n,[0,0,-area*t*weight/4])
            self.dead[family]+=area*t*weight

    def pad(self,a,b,k,cid,area):
        mats=[]
        for value in k:
            self.mat+=1; self.o.uniaxialMaterial('Elastic',self.mat,value); mats.append(self.mat)
        self.e+=1
        self.o.element('zeroLength',self.e,a,b,'-mat',*mats,'-dir',1,2,3,4,5,6)
        self.pads.append(dict(tag=self.e,nodes=[a,b],cid=cid,area=area)); self.groups[cid]='bearing'

    def analyze(self):
        o=self.o; o.timeSeries('Constant',1); o.pattern('Plain',1,1)
        for n,f in self.loads.items(): o.load(n,*f)
        o.constraints('Transformation'); o.numberer('RCM'); o.system('UmfPack')
        o.algorithm('Linear'); o.integrator('LoadControl',1); o.analysis('Static')
        if o.analyze(1): raise RuntimeError('Connected bridge system did not solve.')
        o.reactions()
        load=[0.0]*6; reaction=[0.0]*6
        for n,f in self.loads.items():
            m=cross(self.nodes[n],f[:3])
            for i in range(3): load[i]+=f[i]; load[i+3]+=f[i+3]+m[i]
        reactions=[]
        for n in self.fixed:
            f=o.nodeReaction(n); m=cross(self.nodes[n],f[:3])
            for i in range(3): reaction[i]+=f[i]; reaction[i+3]+=f[i+3]+m[i]
            reactions.append(dict(node=n,xyz_m=self.nodes[n],forces_N_Nm=f))
        force_scale=max(sum(abs(f[2]) for f in self.loads.values()),1)
        force_error=max(abs(load[i]+reaction[i]) for i in range(3))/force_scale
        moment_error=max(abs(load[i]+reaction[i]) for i in range(3,6))/(force_scale*80)
        if max(force_error,moment_error)>1e-6: raise RuntimeError(f'Global equilibrium failed: {force_error}, {moment_error}')
        return load,reaction,reactions,dict(force_error=force_error,moment_error=moment_error)


def create(ledger, options, density=1, stage='post'):
    v=ledger['values']; g=ledger['global']['values']; d=Domain(); o=d.o
    pre=stage=='pre'; total=options['case']=='global_staged'; factor=options['load_factor']
    wc=v['concrete_unit_weight_pcf']*LBF/FT**3; ws=g['steel_weight_pcf']*LBF/FT**3
    eg=concrete_E(v['girder_fc_psi'],v); ed=concrete_E(v['deck_fc_psi'],v); ep=concrete_E(v['pier_fc_psi'],v)
    es=v['rebar_E_ksi']*1000*PSI; nu=v['concrete_poisson']; base=section(v)
    gs=dict(A=base['girder_area_m2'],Iy=base['girder_I_m4'],Iz=polygon_properties([[z*IN,y*IN] for y,z in v['girder_profile_in']])[2],
            J=g['girder_torsion_J_m4'],fibers=[(y*IN,z*IN-base['girder_centroid_m']) for y,z in v['girder_profile_in']])
    h=v['deck_structural_thickness_in']*IN; zb=-h/2-v['haunch_in']*IN-base['girder_top_m']; zg=zb+base['girder_centroid_m']
    ys=[y*FT for y in v['girder_y_ft']]; bents=[x*FT for x in v['bent_x_ft']]
    target=FT*8/density
    # All bearing, end and pier stations are exact mesh breakpoints.
    breaks=sorted(set([-FT,251*FT]+bents+[g['channel_station_ft']*FT]+[x*FT for row in v['beam_extents_ft']+v['bearing_x_ft'] for x in row]))
    breaks=sorted(set(breaks+[p*FT for (lo,hi),dist in zip(v['beam_extents_ft'],g['depress_distance_ft']) for p in [lo+dist,hi-dist]]))
    xs=[]
    for a,b in zip(breaks,breaks[1:]): xs+=lin(a,b,max(1,math.ceil((b-a)/target)))[:-1]
    xs.append(breaks[-1])
    # Cap, column, shaft, socket, pile and debris-wall network.
    caps=[]
    for k,x in enumerate(bents):
        inner=k in (1,2); depth=(g['cap_depth_ft'] if inner else g['end_cap_depth_ft'])*FT
        width=(g['cap_width_ft'] if inner else g['end_cap_width_ft'])*FT
        length=(g['cap_length_ft'] if inner else g['end_cap_length_ft'])*FT
        zcap=zb-g['seat_offset_m']-depth/2
        supports=[y*FT for y in (g['column_y_ft'] if inner else g['pile_y_ft'])]
        cap_ys=sorted(set([-length/2,length/2]+ys+supports)); capnodes={}
        for a,b in zip(cap_ys,cap_ys[1:]):
            for y in lin(a,b,max(1,math.ceil((b-a)/target)))[:-1]: capnodes[y]=d.node([x,y,zcap])
        capnodes[cap_ys[-1]]=d.node([x,cap_ys[-1],zcap])
        entries=list(capnodes.items())
        for (_,a),(_,b) in zip(entries,entries[1:]): d.beam(a,b,rect(width,depth),ep if inner else ed,nu,f'b{k+1}_cap','cap',wc*factor if pre and total else 0)
        caps.append((capnodes,zcap))
        if inner:
            idx=k-1; col_top=g['column_top_el_ft'][idx]
            # Analytical cap reference shifted to the flattened superstructure.
            zshaft=zcap-depth/2-(col_top-g['shaft_top_el_ft'])*FT
            zrock=zshaft-(g['shaft_top_el_ft']-g['rock_el_ft'][idx])*FT
            ztip=zshaft-(g['shaft_top_el_ft']-g['socket_tip_el_ft'][idx])*FT
            zwall=zshaft+(g['debris_wall_top_el_ft']-g['shaft_top_el_ft'])*FT
            wallzs=lin(zshaft,zwall,max(2,math.ceil((zwall-zshaft)/target)))
            columnlines=[]
            for side,y in zip(['R','L'],supports):
                top=capnodes[y]; chain={zcap:top}
                ranges=[(ztip,zrock,'socket',g['socket_diameter_ft']*FT), (zrock,zshaft,'shaft',g['shaft_concrete_diameter_in']*IN), (zshaft,zcap,'column',g['column_diameter_ft']*FT)]
                for a,b,label,diameter in ranges:
                    zs=sorted(set(lin(a,b,max(1,math.ceil((b-a)/target)))+([z for z in wallzs if a<=z<=b] if label=='column' else [])))
                    for z in zs:
                        if z not in chain: chain[z]=d.node([x,y,z])
                    for z0,z1 in zip(zs,zs[1:]): d.beam(chain[z0],chain[z1],circle(diameter),ep,nu,f'b{k+1}_{label}_{side}',label,wc*factor if pre and total else 0)
                d.fix(chain[ztip])
                if options.get('foundation','tip')=='rock': d.fix(chain[zrock])
                columnlines.append(chain)
            # Clear wall length between circular-column inside faces; rigid ends.
            wy=lin(supports[0]+g['column_diameter_ft']*FT/2,supports[1]-g['column_diameter_ft']*FT/2,4*density)
            wall={}
            for iz,z in enumerate(wallzs):
                for iy,y in enumerate(wy):
                    n=d.node([x,y,z]); wall[iz,iy]=n
                    if iy in (0,len(wy)-1): d.rigid(columnlines[0 if iy==0 else 1][z],n)
            for iz in range(len(wallzs)-1):
                for iy in range(len(wy)-1): d.shell([wall[iz,iy],wall[iz,iy+1],wall[iz+1,iy+1],wall[iz+1,iy]],ep,nu,g['debris_wall_thickness_ft']*FT,f'b{k+1}_wall','wall',wc*factor if pre and total else 0)
        else:
            idx=0 if k==0 else 1
            pile_sec=steel_shape(*[g[n]*IN for n in ['pile_depth_in','pile_flange_in','pile_web_in','pile_thickness_in']])
            length=(g['end_cap_bottom_el_ft'][idx]+g['end_cap_depth_ft']/2-g['pile_tip_el_ft'][idx])*FT
            for j,y in enumerate(supports):
                ns=[d.node([x,y,z]) for z in lin(zcap-length,zcap,max(2,math.ceil(length/target)))[:-1]]+[capnodes[y]]
                for a,b in zip(ns,ns[1:]): d.beam(a,b,pile_sec,es,g['steel_poisson'],f'b{k+1}_pile_{j+1}','pile',ws*factor if pre and total else 0)
                d.fix(ns[0])
    deck={}; deckys=[]
    if not pre:
        ybreaks=sorted(set([-v['deck_width_ft']*FT/2,v['deck_width_ft']*FT/2,-v['roadway_width_ft']*FT/2,v['roadway_width_ft']*FT/2,0]+ys))
        for a,b in zip(ybreaks,ybreaks[1:]): deckys+=lin(a,b,max(1,math.ceil((b-a)/(2.5*FT/density))))[:-1]
        deckys.append(ybreaks[-1])
        for x in xs:
            for y in deckys: deck[x,y]=d.node([x,y,0])
        for a,b in zip(xs,xs[1:]):
            for c,e in zip(deckys,deckys[1:]):
                ns=[deck[a,c],deck[b,c],deck[b,e],deck[a,e]]
                d.shell(ns,ed,nu,h,'deck','deck')
                q=1000 if options['case']=='global_uniform' else 1000 if options['case']=='global_eccentric' and (c+e)/2<0 else 0
                if total and abs((c+e)/2)<v['roadway_width_ft']*FT/2: q=v['wearing_psf']*PSF
                for n in ns: d.force(n,[0,0,-q*(b-a)*(e-c)/4*factor])
        if total:
            q=g['barrier_volume_cyd_per_side']*(3*FT)**3*wc/(252*FT)*factor
            for a,b in zip(xs,xs[1:]):
                for y in [deckys[0],deckys[-1]]:
                    d.force(deck[a,y],[0,0,-q*(b-a)/2]); d.force(deck[b,y],[0,0,-q*(b-a)/2])
    girder={}
    widths=[7.75,8.75,8.75,7.75]
    for span in range(3):
        lo,hi=[a*FT for a in v['beam_extents_ft'][span]]
        points=[x for x in xs if lo-1e-8<=x<=hi+1e-8]
        for j,y in enumerate(ys):
            cid=f'girder_{"ABC"[span]}{j+1}'; ns=[]
            for x in points:
                n=d.node([x,y,zg]); girder[span,j,x]=n; ns.append(n)
                if not pre: d.rigid(deck[x,y],n)
            for a,b in zip(ns,ns[1:]):
                d.beam(a,b,gs,eg,nu,cid,'girder',wc*factor if total and pre else 0)
                if pre and total:
                    length=d.nodes[b][0]-d.nodes[a][0]
                    # Full deck area including end overhangs assigned proportionally.
                    wet=(v['deck_total_thickness_in']*IN*wc+v['forms_psf']*PSF)*widths[j]*FT
                    wet+=v['haunch_in']*IN*49*IN*wc
                    wet*=252/sum(q-p for p,q in v['beam_extents_ft'])
                    d.force(a,[0,0,-wet*length*factor/2]); d.force(b,[0,0,-wet*length*factor/2])
            for end,xb in enumerate(v['bearing_x_ft'][span]):
                x=min(points,key=lambda p:abs(p-xb*FT)); n=girder[span,j,x]; bent=span+end
                capmap,zcap=caps[bent]; master=capmap[y]
                # Connect through the deck master in post stage, avoiding chained MPs.
                upper=d.offset(n if pre else deck[x,y],[x,y,zb])
                lower=d.offset(master,[x,y,zb])
                interior=bent in (1,2)
                if interior:
                    area=g['pad_length_in']*g['pad_width_in']*IN**2
                    kh=g['pad_G_MPa']*1e6*area/(g['pad_rubber_in']*IN)
                    kv=g['pad_E_compression_MPa']*1e6*area/(g['pad_rubber_in']*IN)
                    cidpad=f'b{bent+1}_bearing_{j+1}_{-1 if end else 1:+d}'
                else:
                    area=9*6*IN**2; kh=g['end_bearing_horizontal_Npm']; kv=g['end_bearing_vertical_Npm']; cidpad=f'b{bent+1}_bearing_{j+1}_+0_top'
                rotational=g['released_rotation_Nm'] if interior or pre else g['end_connection_rotation_Nm']
                d.pad(lower,upper,[g['construction_slide_Npm'] if pre else kh, kh,kv,rotational,rotational,rotational],cidpad,area)
            if pre and total:
                # Concrete-only equivalent tendon loads. End anchor forces and
                # slope-change deviator forces form a self-equilibrated system.
                count=v['strand_count_B' if span==1 else 'strand_count_AC']
                force=count*v['strand_jacking_lbf']*LBF*options.get('prestress_factor',g['prestress_retained_fraction'])*factor
                straight=(17*2+(8 if span==1 else 4)*4+2*34)*IN
                def ecc(x):
                    dist=min(x-lo,hi-x); ramp=min(1,max(0,dist/(g['depress_distance_ft'][span]*FT)))
                    z=(straight+3*(31-27*ramp)*IN)/count
                    return z-base['girder_centroid_m']
                # Each straight tendon segment supplies equal/opposite anchor
                # vectors; interior axial and eccentric moments cancel exactly.
                for a,b in zip(ns,ns[1:]):
                    xa,xb=d.nodes[a][0],d.nodes[b][0]; ea,eb=ecc(xa),ecc(xb)
                    slope=(eb-ea)/(xb-xa)
                    d.force(a,[force,0,force*slope,0,force*ea,0])
                    d.force(b,[-force,0,-force*slope,0,-force*eb,0])
    # Intermediate steel diaphragm; transverse coupling exists even before cure.
    xc=g['channel_station_ft']*FT
    channel=steel_shape(*[g[n]*IN for n in ['channel_depth_in','channel_width_in','channel_web_in','channel_flange_in']])
    for j in range(3): d.beam(girder[1,j,xc],girder[1,j+1,xc],channel,es,g['steel_poisson'],f'steel_diaphragm_{j+1}','crossbeam',ws*factor if pre and total else 0)
    if not pre:
        for k in (1,2):
            x=bents[k]
            ds=rect(g['diaphragm_width_ft']*FT,g['diaphragm_height_ft']*FT)
            ns=[d.offset(deck[x,y],[x,y,zg]) for y in ys]
            for a,b in zip(ns,ns[1:]): d.beam(a,b,ds,ed,nu,f'b{k+1}_diaphragm','diaphragm',wc*factor if total else 0)
            # Concrete continuity through the short gap between precast ends.
            for j,y in enumerate(ys):
                xl=v['beam_extents_ft'][k-1][1]*FT; xr=v['beam_extents_ft'][k][0]*FT
                d.beam(girder[k-1,j,xl],ns[j],rect(49*IN,36*IN),ed,nu,f'b{k+1}_diaphragm','diaphragm')
                d.beam(ns[j],girder[k,j,xr],rect(49*IN,36*IN),ed,nu,f'b{k+1}_diaphragm','diaphragm')
    return d


def read_domain(d):
    load,reaction,reactions,equilibrium=d.analyze(); o=d.o
    samples=defaultdict(list); raw=defaultdict(list)
    disps={n:o.nodeDisp(n) for n in d.nodes}
    for b in d.beams:
        f=o.eleResponse(b['tag'],'localForce'); sec=b['section']
        for end,n in enumerate(b['nodes']):
            sign=-1 if end==0 else 1; off=end*6
            N,My,Mz=sign*f[off],sign*f[off+4],sign*f[off+5]
            vals=[(N/sec['A']+My*z/sec['Iy']-Mz*y/sec['Iz'])/1e6 for y,z in sec['fibers']]
            xyz=d.nodes[n]; u=disps[n]
            samples[b['cid']].append(dict(x_m=xyz[0],xyz_m=xyz,displacement_m=u[:3],deflection_mm=-u[2]*1000,
                top_MPa=max(vals),bottom_MPa=min(vals),tension_MPa=max(0,max(vals)),compression_MPa=max(0,-min(vals)),
                stress_MPa=max(abs(v) for v in vals),moment_kNm=My/1000))
            raw[b['cid']].append(dict(xyz_m=xyz,normal_N=N,My_Nm=My,Mz_Nm=Mz,section=sec))
    for s in d.shells:
        stress=o.eleResponse(s['tag'],'stresses')
        if len(stress)!=32: raise RuntimeError('Unexpected shell resultant schema.')
        xyz=[sum(d.nodes[n][i] for n in s['nodes'])/4 for i in range(3)]
        u=[sum(disps[n][i] for n in s['nodes'])/4 for i in range(3)]
        # Preserve GP values; display per-element max, never smoothed nodal stress.
        principal_pairs=[principal(stress[i:i+8],s['t']) for i in range(0,32,8)]
        tension=max(0,max(a for a,b in principal_pairs)); compression=max(0,-min(b for a,b in principal_pairs))
        samples[s['cid']].append(dict(x_m=xyz[0],xyz_m=xyz,displacement_m=u,deflection_mm=-u[2]*1000,
            top_MPa=tension,bottom_MPa=-compression,tension_MPa=tension,compression_MPa=compression,
            stress_MPa=max(tension,compression),moment_kNm=0,
            gp_resultants_Npm_N=stress,element_nodes=[d.nodes[n] for n in s['nodes']],thickness_m=s['t']))
    for p in d.pads:
        f=o.eleResponse(p['tag'],'force'); n=p['nodes'][1]; u=disps[n]
        normal=-f[2]/p['area']/1e6; stress=abs(normal)
        samples[p['cid']].append(dict(x_m=d.nodes[n][0],xyz_m=d.nodes[n],displacement_m=u[:3],deflection_mm=-u[2]*1000,
            top_MPa=max(0,normal),bottom_MPa=min(0,normal),tension_MPa=max(0,normal),compression_MPa=max(0,-normal),stress_MPa=stress,moment_kNm=0,
            bearing_vertical_N=f[2],bearing_area_m2=p['area']))
    members=[]
    for cid,ps in samples.items():
        members.append(dict(component_id='beechwood:'+cid,family=d.groups[cid],span='global',line=0,samples=ps,
                            raw_beam=raw.get(cid,[]),peak=max(ps,key=lambda p:p['stress_MPa']),max_deflection_mm=max(abs(p['deflection_mm']) for p in ps)))
    # Mesh is an independently inspectable analytical geometry, not the GLB.
    mesh=dict(nodes=[dict(id=n,xyz_m=xyz,displacement_m=disps[n][:3]) for n,xyz in d.nodes.items()],
              beams=[dict(nodes=b['nodes'],component_id='beechwood:'+b['cid'],family=b['family']) for b in d.beams],
              shells=[dict(nodes=s['nodes'],component_id='beechwood:'+s['cid'],family=s['family']) for s in d.shells],
              links=[list(p) for p in d.links],supports=d.fixed)
    return dict(members=members,total_load_kN=-load[2]/1000,total_reaction_kN=reaction[2]/1000,
                reactions=reactions,equilibrium=[equilibrium],node_count=len(d.nodes),element_count=d.e,mesh=mesh,
                load_vector_N_Nm=load,reaction_vector_N_Nm=reaction)


def global_run(ledger, options, density=1):
    post=read_domain(create(ledger,options,density,'post'))
    if options['case']=='global_staged':
        pre=read_domain(create(ledger,options,density,'pre'))
        before={m['component_id']:m for m in pre['members']}
        for m in post['members']:
            old=before.get(m['component_id'])
            if not old: continue
            if len(old['samples'])!=len(m['samples']): raise RuntimeError('Stage sample mapping differs.')
            for i,(p,q) in enumerate(zip(m['samples'],old['samples'])):
                if math.dist(p['xyz_m'],q['xyz_m'])>1e-7: raise RuntimeError('Stage coordinates differ.')
                p['displacement_m']=[a+b for a,b in zip(p['displacement_m'],q['displacement_m'])]
                p['deflection_mm']+=q['deflection_mm']
                if m['raw_beam']:
                    a=m['raw_beam'][i]; b=old['raw_beam'][i]; sec=a['section']
                    for k in ['normal_N','My_Nm','Mz_Nm']: a[k]+=b[k]
                    values=[(a['normal_N']/sec['A']+a['My_Nm']*z/sec['Iy']-a['Mz_Nm']*y/sec['Iz'])/1e6 for y,z in sec['fibers']]
                    p.update(top_MPa=max(values),bottom_MPa=min(values),tension_MPa=max(0,max(values)),compression_MPa=max(0,-min(values)),stress_MPa=max(abs(v) for v in values),moment_kNm=a['My_Nm']/1000)
                elif 'gp_resultants_Npm_N' in p:
                    stress=[a+b for a,b in zip(p['gp_resultants_Npm_N'],q['gp_resultants_Npm_N'])]; p['gp_resultants_Npm_N']=stress
                    pairs=[principal(stress[j:j+8],p['thickness_m']) for j in range(0,32,8)]
                    t=max(0,max(a for a,b in pairs)); c=max(0,-min(b for a,b in pairs))
                    p.update(top_MPa=t,bottom_MPa=-c,tension_MPa=t,compression_MPa=c,stress_MPa=max(t,c))
                else:
                    p['bearing_vertical_N']+=q['bearing_vertical_N']; normal=-p['bearing_vertical_N']/p['bearing_area_m2']/1e6
                    p.update(top_MPa=max(0,normal),bottom_MPa=min(0,normal),tension_MPa=max(0,normal),compression_MPa=max(0,-normal),stress_MPa=abs(normal))
            m['peak']=max(m['samples'],key=lambda p:p['stress_MPa']); m['max_deflection_mm']=max(abs(p['deflection_mm']) for p in m['samples'])
        # Post-cure deck is stress free at activation. Its displayed displacement
        # remains the post-cure increment; do not invent a wet-slab displacement.
        post['stage_results']=[dict(name='Bare girders + retained prestress + wet deck + substructure gravity',total_load_kN=pre['total_load_kN'],total_reaction_kN=pre['total_reaction_kN']),dict(name='Composite barriers + wearing + idealized diaphragm weight',total_load_kN=post['total_load_kN'],total_reaction_kN=post['total_reaction_kN'])]
        for k in ['total_load_kN','total_reaction_kN']: post[k]+=pre[k]
        post['equilibrium']+=pre['equilibrium']
        post['reactions_pre']=pre['reactions']
        post['reactions_post']=[dict(r) for r in post['reactions']]
        for a,b in zip(post['reactions'],pre['reactions']):
            if a['xyz_m']!=b['xyz_m']: raise RuntimeError('Stage support mapping differs.')
            a['forces_N_Nm']=[x+y for x,y in zip(a['forces_N_Nm'],b['forces_N_Nm'])]
        for k in ['load_vector_N_Nm','reaction_vector_N_Nm']: post[k]=[x+y for x,y in zip(post[k],pre[k])]
        # Preserve both independently inspectable meshes; no incompatible
        # displacement fields are silently assigned to the newly cast deck.
        post['mesh_pre']=pre['mesh']
    for m in post['members']: m.pop('raw_beam',None)
    post['max_stress_MPa']=max(m['peak']['stress_MPa'] for m in post['members'])
    post['max_deflection_mm']=max(m['max_deflection_mm'] for m in post['members'])
    post['family_summary']={f:dict(member_count=sum(m['family']==f for m in post['members']),max_stress_MPa=max(m['peak']['stress_MPa'] for m in post['members'] if m['family']==f),max_deflection_mm=max(m['max_deflection_mm'] for m in post['members'] if m['family']==f)) for f in sorted({m['family'] for m in post['members']})}
    return post


def global_benchmarks():
    """Independent 3D frame, MP constraint and shell analytical checks."""
    checks=[]
    def check(name,a,b,tol=1e-6):
        err=abs(a-b)/max(abs(b),1e-12)
        checks.append(dict(name=name,actual=a,expected=b,relative_error=err,tolerance=tol,passed=err<tol))
    d=Domain(); E=30e9; sec=rect(.6,1.0); a=d.node([0,0,0]); b=d.node([8,0,0]); d.fix(a)
    beam=d.beam(a,b,sec,E,.2,'test','girder'); d.force(b,[10000,20000,-30000]); r=read_domain(d)
    check('3D cantilever axial displacement',d.o.nodeDisp(b,1),10000*8/(E*sec['A']))
    check('3D cantilever vertical displacement',d.o.nodeDisp(b,3),-30000*8**3/(3*E*sec['Iy']))
    check('3D cantilever transverse displacement',d.o.nodeDisp(b,2),20000*8**3/(3*E*sec['Iz']))
    vals=[(10000/sec['A']+240000*z/sec['Iy']-160000*y/sec['Iz'])/1e6 for y,z in sec['fibers']]
    check('3D biaxial fiber stress',r['members'][0]['peak']['stress_MPa'],max(abs(v) for v in vals))
    d=Domain(); a=d.node([0,0,0]); b=d.node([8,0,0]); d.fix(a); d.beam(a,b,sec,E,.2,'offset','girder')
    c=d.offset(b,[8,0,1]); d.force(c,[10000,0,0]); read_domain(d)
    check('Rigid offset transfers moment',d.o.nodeReaction(a,5),-10000)
    # Affine membrane patch: prescribed exact deformation, no recovery averaging.
    d=Domain(); o=d.o; ns=[d.node(p) for p in [[0,0,0],[2,0,0],[2,1,0],[0,1,0]]]
    d.shell(ns,E,.2,.15,'patch','deck'); o.timeSeries('Linear',1); o.pattern('Plain',1,1)
    for n in ns:
        x,y,z=d.nodes[n]
        for dof,val in enumerate([1e-4*x+2e-5*y,3e-5*y,0,0,0,0],1): o.sp(n,dof,val)
    o.constraints('Penalty',1e20,1e20); o.numberer('RCM'); o.system('BandGeneral'); o.algorithm('Linear'); o.integrator('LoadControl',1); o.analysis('Static')
    # A second iteration updates section state after prescribed displacements;
    # Linear's first call can leave a zero trial section with all DOFs prescribed.
    o.algorithm('Newton'); o.test('NormDispIncr',1e-12,10)
    if o.analyze(1): raise RuntimeError('Shell patch failed.')
    stress=o.eleResponse(1,'stresses')
    check('Shell membrane Nx',stress[0],E*.15/(1-.2**2)*(1e-4+.2*3e-5),1e-7)
    check('Shell membrane Ny',stress[1],E*.15/(1-.2**2)*(3e-5+.2*1e-4),1e-7)
    check('Shell membrane Nxy',stress[2],E*.15/(2*1.2)*2e-5,1e-7)
    # Thin simply-supported square plate (Navier double series).
    d=Domain(); o=d.o; n=16; L=4; t=.04; q=1000; grid={}
    for i in range(n+1):
        for j in range(n+1):
            tag=d.node([L*i/n,L*j/n,0]); grid[i,j]=tag
            # In-plane translations and drilling fixed; boundary w=0,
            # normal edge rotation remains free (simply supported plate).
            o.fix(tag,1,1,int(i in (0,n) or j in (0,n)),0,0,1)
    for i in range(n):
        for j in range(n):
            ns=[grid[i,j],grid[i+1,j],grid[i+1,j+1],grid[i,j+1]]
            d.shell(ns,E,.2,t,'plate','deck')
            for tag in ns: d.force(tag,[0,0,-q*(L/n)**2/4])
    o.timeSeries('Constant',1); o.pattern('Plain',1,1)
    for tag,f in d.loads.items(): o.load(tag,*f)
    o.constraints('Plain'); o.numberer('RCM'); o.system('UmfPack'); o.algorithm('Linear'); o.integrator('LoadControl',1); o.analysis('Static')
    if o.analyze(1): raise RuntimeError('Plate benchmark failed.')
    D=E*t**3/(12*(1-.2**2))
    expected=sum(16*q*L**4/(math.pi**6*D)*math.sin(i*math.pi/2)*math.sin(j*math.pi/2)/(i*j*(i*i+j*j)**2) for i in range(1,80,2) for j in range(1,80,2))
    check('Simply supported plate center deflection',-o.nodeDisp(grid[n//2,n//2],3),expected,.02)
    # Prestress sign / eccentricity on a free-to-shorten simple beam.
    d=Domain(); o=d.o; a=d.node([0,0,0]); b=d.node([8,0,0]); o.fix(a,1,1,1,1,0,0); o.fix(b,0,1,1,1,0,0)
    d.fixed=[a,b]; d.beam(a,b,sec,E,.2,'prestress','girder'); P=1e6; e=-.2
    d.force(a,[P,0,0,0,P*e,0]);d.force(b,[-P,0,0,0,-P*e,0]); r=read_domain(d)
    check('Prestress axial compression',r['members'][0]['raw_beam'][0]['normal_N'],-P)
    check('Prestress eccentric section moment',r['members'][0]['raw_beam'][0]['My_Nm'],-P*e)
    if not all(c['passed'] for c in checks): raise RuntimeError('Global benchmarks failed: '+str([c for c in checks if not c['passed']]))
    o.wipe(); return checks


def solve_global(snapshot):
    import platform
    import importlib.metadata
    import openseespy.opensees as ops
    from fem.solver import settings,CASES,benchmarks
    ledger=snapshot['ledger']; options=settings(snapshot['settings'])
    tests=benchmarks()+global_benchmarks()
    coarse=global_run(ledger,options,1); fine=global_run(ledger,options,2)
    refinement=[]
    for family in fine['family_summary']:
        for field in ['max_stress_MPa','max_deflection_mm']:
            a=coarse['family_summary'][family][field]; b=fine['family_summary'][family][field]
            rel=abs(a-b)/max(b,1e-9)
            refinement.append(dict(quantity=family+'.'+field,coarse=a,fine=b,relative_change=rel,tolerance=.05,passed=rel<.05))
    warnings=[c['quantity'] for c in refinement if not c['passed']]
    # Result remains inspectable, but never label a failed local peak converged.
    displacement_change=abs(coarse['max_deflection_mm']-fine['max_deflection_mm'])/max(fine['max_deflection_mm'],1e-9)
    if displacement_change>.05: raise RuntimeError('Global displacement mesh change exceeds 5%; no result accepted.')
    variants=[]
    alternative=dict(options,foundation='rock' if options['foundation']=='tip' else 'tip')
    candidates=[('Foundation: '+alternative['foundation'],alternative)]
    if options['case']=='global_staged':
        candidates += [('Retained prestress: '+str(p),dict(options,prestress_factor=p)) for p in [.7,.8,.9] if p!=options['prestress_factor']]
    for label,opts in candidates:
        r=global_run(ledger,opts,2)
        variants.append(dict(label=label,settings=opts,max_stress_MPa=r['max_stress_MPa'],max_deflection_mm=r['max_deflection_mm'],family_summary=r['family_summary']))
    fine.update(schema_version=2,bridge_id='beechwood',case=options['case'],case_title=CASES[options['case']],settings=options,
        scope='connected_frame_shell_staged_research' if options['case']=='global_staged' else 'connected_frame_shell_increment',
        solver=dict(name='OpenSees',version=ops.version(),python=platform.python_version(),platform=platform.platform(),packages={'openseespy':importlib.metadata.version('openseespy')}),
        units=dict(length='m',force='kN',stress='MPa',displacement='mm'),
        verification=dict(passed=True,field_validated=False,all_local_peaks_converged=not warnings,mesh_warnings=warnings,benchmarks=tests,mesh_refinement=refinement,equilibrium_tolerance=1e-6),
        assumptions=ledger['global']['assumptions'],sensitivity=variants,snapshot=snapshot,
        stress_measures=dict(beam='Axial plus biaxial nominal fiber normal stress',shell='Principal stress at both surfaces from integration-point membrane and bending resultants',bearing='Mean normal pressure, not local contact stress'),
        displacement_note='Staged member values accumulate pre/post increments for existing members; newly cast deck and diaphragms show post-cure displacement only. Analytical mesh shows each stage independently.' if options['case']=='global_staged' else 'Increment from the selected pressure only.')
    return fine

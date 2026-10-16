"""Build auditable assumed-input FEM ledgers; never infer section area from a GLB.

Each bridge recipe below explicitly selects design state, topology, dimensions,
profile idealization and support members. Manifest bounds locate member axes and
vertical datums only; structural cross sections are separately specified.
"""
import hashlib
import json
import math
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FT=.3048; IN=.0254
EXISTING=['21st-street-i465','us52-mud','sr44-mud','sr8-yellow','us50-tanners-eb','fletcher-avenue','sr10-i65']
NEW=['us35-deer','us224-eight-mile','virginia-avenue','sr44-little-blue','sr1-six-mile']


def load(path): return json.loads(path.read_text(encoding='utf-8'))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def mid(part,axis): return sum(p[axis] for p in part['bounds_m'])/2
def rectangle(b,h): return dict(kind='rectangle',dimensions_m=[b,h])
def ishape(d,b,tw,tf): return dict(kind='I',dimensions_m=[d,b,tw,tf])
def stations(spans):
    bs=[-sum(spans)/2]
    for s in spans: bs.append(bs[-1]+s)
    return bs


class Recipe:
    def __init__(self,bid,spans,length,width,thickness,skew_sign=-1,simple=False):
        self.bid=bid; self.base=ROOT/'data/bridges'/bid; self.manifest=load(self.base/'model_manifest.json')
        self.parts={p['id']:p for p in self.manifest['parts']}; self.bs=stations(spans)
        self.k=skew_sign*math.tan(math.radians(self.manifest.get('skew_deg',0)))
        decks=[p for p in self.parts.values() if p['layer']=='deck' and p['id']!='overlay']
        z=max(p['bounds_m'][1][2] for p in decks)-thickness/2
        self.v=dict(deck=dict(u0_m=-length/2,u1_m=length/2,y0_m=-width/2,y1_m=width/2,
            midplane_z_m=z,thickness_m=thickness,patches=[]),spans_m=spans,skew_dx_dy=self.k,
            beams=[],supports=[],bearing_horizontal_Npm=1e7,bearing_rotation_Nm=1e3,
            foundation_stiffness_Npm_Nm=[2e8,2e8,8e8,2e8,2e8,2e8],
            fixed_reference_stiffness_Npm_Nm=[1e13]*6,
            integral_connection_stiffness_Npm_Nm=[1e11]*3+[1e10]*3,
            mesh_step_u_m=3.0,mesh_step_y_m=1.4)
        self.notes=[
            'Assumed-input OpenSees linear elastic incremental demonstration; not an as-built model, load rating, field validation or full physical stress history.',
            'Pressure acts on the full declared structural deck envelope, including sidewalk zones. Left half means native Y below the geometric deck centerline.',
            'Concrete E=30 GPa, steel E=200 GPa, Poisson ratios 0.20/0.30 are editable assumptions. No cracking, reinforcement, prestress initial stress, creep, shrinkage or self-weight is included.',
            'All deck nodes are placed on the declared flat midplane. Crossfall, vertical curvature and fabrication camber are omitted. Girder centroids are flattened; native X/Y station and skew are preserved.',
            'Full beam/deck composite action is assumed through rigid offsets. Haunch stiffness, barriers, walks, diaphragms, cross frames, bolts, local bearing plates and nonstructural pieces are omitted unless expressly listed as analyzed.',
            'Bearing springs are bilateral with assumed horizontal 10 MN/m and rotational 1 kNm/rad stiffness. Vertical stiffness is editable. Springs may report tension; uplift/contact is not modeled.',
            'Fixed bases mean fixed at the explicitly modeled wall/column/pile bottom; elastic bases add the frozen six stiffnesses per column or per metre of wall. Soil, buried footing flexibility and actual pile fixity are unverified.',
            'Integral links use the frozen 100 GN/m translations and 10 GNm/rad rotations, distributed by tributary width for line connections. Cap-only fixed reference supports use 10 TN/m springs to separate the reaction node from its rigid constraint; this is a numerical fixed-base approximation.',
            'Cap/column/wall sections are explicit idealizations. Shell wall heights extend to the cap reference axis where a cap exists; cap embedment and taper are simplified. Local peaks are nominal, not connection design stresses.',
        ]
        if simple:
            limits=[-length/2]+self.bs[1:-1]+[length/2]
            self.v['continuity_units']=[dict(u0_m=a,u1_m=b) for a,b in zip(limits,limits[1:])]
            self.notes.append('Independent simply supported span demonstration: separate deck and beam nodes at intermediate bent cuts release longitudinal continuity. This is an explicit approximation to the physical continuous deck; no unintended beam continuity is introduced at precast girder ends.')
        else:
            self.v['continuity_units']=[dict(u0_m=-length/2,u1_m=length/2)]
            self.notes.append('Deck and longitudinal beams are continuous across intermediate supports. Selectable fabrication/span divisions do not create structural hinges. Integral end connections, where specified, use stiff six-direction links to the modeled end wall/cap.')
        self.simple=simple

    def patch(self,cid,u0=None,u1=None,y0=None,y1=None):
        d=self.v['deck']; self.v['deck']['patches'].append(dict(cid=cid,u0_m=d['u0_m'] if u0 is None else u0,
            u1_m=d['u1_m'] if u1 is None else u1,y0_m=d['y0_m'] if y0 is None else y0,y1_m=d['y1_m'] if y1 is None else y1))

    def beam(self,cid,i,y,sec,material='steel',u0=None,u1=None,depth=None,centroid_from_bottom=None):
        a=self.bs[i] if u0 is None else u0; b=self.bs[i+1] if u1 is None else u1
        if depth is None: depth=sec['dimensions_m'][0]
        below=depth-(centroid_from_bottom if centroid_from_bottom is not None else depth/2)
        d=self.v['deck']; self.v['beams'].append(dict(cid=cid,unit=i if self.simple else 0,u0_m=a,u1_m=b,y_m=y,
            material=material,section=sec,centroid_z_m=d['midplane_z_m']-d['thickness_m']/2-.08-below))

    def support(self,i,cap_id=None,cap_width=None,cap_depth=None,top=None):
        s=dict(u_m=self.bs[i],bearings=[],walls=[],columns=[])
        if cap_id:
            p=self.parts[cap_id]
            # Only reference-axis location and explicit envelope endpoints come from bounds.
            h=cap_depth if cap_depth else p['bounds_m'][1][2]-p['bounds_m'][0][2]
            s['top_z_m']=mid(p,2) if top is None else top
            s['cap']=dict(cid=cap_id,y0_m=p['bounds_m'][0][1],y1_m=p['bounds_m'][1][1],section=rectangle(cap_width,h))
        else: s['top_z_m']=top
        self.v['supports'].append(s); return s

    def wall(self,s,cid,t,y0=None,y1=None,bottom=None):
        p=self.parts[cid]
        s['walls'].append(dict(cid=cid,thickness_m=t,y0_m=p['bounds_m'][0][1] if y0 is None else y0,
            y1_m=p['bounds_m'][1][1] if y1 is None else y1,
            bottom_z_m=p['bounds_m'][0][2] if bottom is None else bottom))

    def column(self,s,cid,sec,material='concrete',family='column'):
        p=self.parts[cid]; s['columns'].append(dict(cid=cid,y_m=mid(p,1),bottom_z_m=p['bounds_m'][0][2],
            section=sec,material=material,family=family))

    def bearing(self,s,cid,i,y,unit=None,u=None,beam_y=None,integral=False):
        if integral:
            z=self.v['deck']['midplane_z_m']-.5; area=1
        else:
            p=self.parts[cid]; dims=p['dimensions']; z=mid(p,2)
            a=dims.get('pad_length_m',dims.get('length_in',12)*IN)
            b=dims.get('pad_width_m',dims.get('width_in',16)*IN); area=a*b
        s['bearings'].append(dict(cid=cid,unit=(i if self.simple else 0) if unit is None else unit,
            u_m=s['u_m'] if u is None else u,y_m=y,beam_y_m=y if beam_y is None else beam_y,
            z_m=z,area_m2=area,integral=integral))

    def save(self):
        ids={p['cid'] for p in self.v['deck']['patches']}|{b['cid'] for b in self.v['beams']}
        for s in self.v['supports']:
            if s.get('cap'): ids.add(s['cap']['cid'])
            ids.update(p['cid'] for p in s['walls']+s['columns'])
            ids.update(p['cid'] for p in s['bearings'] if not p.get('integral'))
            if s.get('line_connection',{}).get('cid'): ids.add(s['line_connection']['cid'])
        if not ids<=set(self.parts): raise ValueError((self.bid,ids-set(self.parts)))
        manifest=self.manifest
        pages=sorted(set(p for cid in ids for p in self.parts[cid].get('pdf_pages',[]) if isinstance(p,int)))
        sources={'drawing':dict(title=manifest.get('source_note',manifest['title']),url=f'/assets/{self.bid}/drawing'),
                 'demonstration':dict(title='Explicit assumed inputs',url='/analysis-guide#collection-demo')}
        ledger=dict(schema_version=1,engine='collection_demo',bridge_id=self.bid,title=manifest['title'],
            modeled_state=manifest.get('source_note',manifest['title']),demonstration=True,
            display_scope='Explicit assumed deck, beam, bearing and selected substructure model; omitted physical components carry no claimed FE stress.',
            coordinate_system='Native metres: X longitudinal, Y transverse, Z up. x=u+skew_dx_dy*y. Flat analytical elevations are explicit.',
            source_pdf=f'data/bridges/{self.bid}/drawings.pdf',drawing_sha256=sha(self.base/'drawings.pdf'),
            source_hashes={kind:sha(self.base/name) for kind,name in [('drawing','drawings.pdf'),('manifest','model_manifest.json'),('model','model.glb')]},
            sources=sources,evidence=[
                dict(fields=['deck','spans_m','beams','supports'],status='source-based geometry with explicit idealizations',source='drawing',pdf_pages=pages,note='Source-specific recipe transcribes manifest/source-ledger dimensions and original modeling script callouts. Native bounding-box centers locate axes only; bounding rectangles are not used as girder cross sections.'),
                dict(fields=['bearing_horizontal_Npm','bearing_rotation_Nm','foundation_stiffness_Npm_Nm','integral_connection_stiffness_Npm_Nm','fixed_reference_stiffness_Npm_Nm','continuity_units'],status='assumed',source='demonstration',note='All assumptions are frozen in values and assumptions; no test-based material certification is asserted.')],
            values=self.v,assumptions=self.notes,analyzed_component_ids=sorted(ids),
            excluded_component_ids=sorted(set(self.parts)-ids),
            excluded_component_reason='Outside this explicitly scoped analytical idealization; no stress or displacement assigned to these display members.')
        out=ROOT/'fem/collection'/f'{self.bid}.json';out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps(ledger,indent=2)+'\n',encoding='utf-8')
        print(self.bid,len(ids),'analyzed components',flush=True)
        return ledger


def existing(bid):
    m=load(ROOT/'data/bridges'/bid/'model_manifest.json')
    spans=m.get('spans_m') or [s*FT for s in m['spans_ft']]
    length=m.get('deck_length_m') or m['deck_length_ft']*FT
    width=m.get('deck_width_m') or m['deck_width_ft']*FT
    t=.508 if bid=='us52-mud' else .2 if bid in ['sr8-yellow','sr10-i65'] else 8*IN
    r=Recipe(bid,spans,length,width,t,skew_sign=1 if bid=='sr44-mud' else -1,
             simple=bid in ['21st-street-i465','us50-tanners-eb'])
    if bid!='us52-mud': r.patch('deck')
    if bid=='sr44-mud':
        ys=[a*FT for a in [21,14,7,0,-7,-14,-21]]
        sec=ishape(*[a*IN for a in [26.92,9.990,.490,.745]])
        for j,y in enumerate(ys,1):
            for i,(a,b) in enumerate([(-75.25,-11.75),(-11.75,11.75),(11.75,75.25)],1):
                r.beam(f'beam_{j}_segment_{i}',0,y,sec,u0=a*FT,u1=b*FT)
        for i,u in enumerate(r.bs):
            s=r.support(i,f'cap_{i+1}',(2.5 if i in [0,3] else 3)*FT)
            if i in [1,2]: r.wall(s,f'pier_{i+1}_wall',2*FT)
            else:
                # Fixed/elastic foundation at documented cap bottom (pile tips unverified).
                r.notes.append(f'End bent {i+1}: cap base restrained along its width. Retained design piles have unknown driven lengths and are excluded; no pile stresses are claimed.')
            for j,y in enumerate(ys,1): r.bearing(s,f'bearing_{i+1}_{j}',0,y)
        r.notes.append('Continuous W27x94 section uses manifest/catalog d=26.92, b=9.990, tw=.490, tf=.745 inches with fillets omitted. Splice gaps are analytically closed; nominal unspliced stiffness is retained.')
    elif bid=='sr8-yellow':
        ys=[-5.029,-3.556,-1.778,0,1.778,3.556,5.029]
        for j,y in enumerate(ys):
            for i in range(5):r.beam(f'beam_{i}_{j}',i,y,ishape(.840,.292,.0147,.022))
        labels=['Bent_1','Bent_2','Pier_3','Pier_4','Bent_5','Bent_6']
        for i in range(6):
            s=r.support(i,f'cap_{i}',1.3 if i in [2,3] else .76)
            if i in [2,3]:r.wall(s,f'wall_{i}',1.15)
            else:
                for j in range(9):r.column(s,f'pile_stub_{i}_{j}',dict(kind='circle',diameter_m=.355),family='pile')
            for j,y in enumerate(ys):r.bearing(s,f'{labels[i]}_bearing_{j+1}',0,y)
        r.notes += ['W840x193 is the explicit nominal I idealization d=.840, b=.292, tw=.0147, tf=.022 m, not an exact rolled catalog section.',
            'Retained center walls use the geometric reconstruction assumptions t=1.15 m. Round .355 m pile stubs are equivalent elastic columns, fixed/elastic at their displayed cut bottoms; driven lengths and soil embedment are unknown.']
    elif bid=='us50-tanners-eb':
        ys=[-width/2+(4+1/12)*FT+j*(10+10/12)*FT for j in range(7)]
        pr=[[-12.5,0],[12.5,0],[12.5,8],[3.5,17],[3.5,54],[27,58],[30,58],[30,66],[-30,66],[-30,58],[-27,58],[-3.5,54],[-3.5,17],[-12.5,8]]
        sec=dict(kind='polygon',profile_yz_m=[[y*IN,z*IN] for y,z in pr],torsion_J_m4=.025)
        from fem.collection_demo import section
        from fem.solver import polygon_properties
        cz=polygon_properties(sec['profile_yz_m'])[1]
        for i in range(5):
            for j,y in enumerate(ys):r.beam(f'bulbt_{i}_{j}',i,y,sec,'concrete',depth=66*IN,centroid_from_bottom=cz)
        for i in range(6):
            s=r.support(i,f'cap_{i}',(3.75 if i in [0,5] else 4.5)*FT)
            for j in range(4):r.column(s,f'column_{i}_{j}',rectangle((3 if i in [0,5] else 4)*FT,(3 if i in [0,5] else 4)*FT))
            for span,end,offset in ([(i-1,'end',-FT if i<5 else 0)] if i else [])+([(i,'start',FT if i else 0)] if i<5 else []):
                for j,y in enumerate(ys):r.bearing(s,f'Span_{chr(65+span)}_beam_{j+1}_{end}_bearing',span,y,u=r.bs[i]+offset)
        r.notes += ['66 in Bulb-T section is the explicit 14-vertex source-derived flange/web polygon, not a solid bounding rectangle. Saint-Venant J=.025 m4 is an assumed torsion property; prestress is omitted.',
            'Interior bearing rows remain at bent center +/-1 ft. Deep-bent tie beams are omitted from this incremental model; actual column fixity and coupled tie-beam response are not established.']
    elif bid=='21st-street-i465':
        ys=[-18.5*FT,0,18.5*FT]
        pr=[[-28,0],[28,0],[49.75,54],[30.75,54],[23,8],[-23,8],[-30.75,54],[-49.75,54]]
        sec=dict(kind='polygon',profile_yz_m=[[y*IN,z*IN] for y,z in pr],torsion_J_m4=.011)
        from fem.solver import polygon_properties
        cz=polygon_properties(sec['profile_yz_m'])[1]
        for i in range(2):
            for j,y in enumerate(ys):r.beam(f'beam_{chr(65+i)}{j+1}',i,y,sec,'concrete',depth=54*IN,centroid_from_bottom=cz)
        ss=[r.support(0,'bent_1_cap',3*FT),r.support(1,'pier_cap',4*FT,4*FT),r.support(2,'bent_3_cap',3*FT)]
        for i in [0,2]:
            for j in range(1,12):r.column(ss[i],f'b{1 if i==0 else 3}_pile_{j:02}',ishape(.3556,.3556,.016,.016),'steel','pile')
        for j in range(1,4):r.column(ss[1],f'pier_column_{j}',rectangle(6.4166667*FT,3.5*FT))
        for span in range(2):
            for j,y in enumerate(ys):
                for end in [1,2]:
                    for pad in [1,2]:
                        cid=f'pad_{chr(65+span)}{j+1}_{end}_{pad}';p=r.parts[cid];py=mid(p,1)
                        u=round(mid(p,0)-r.k*py,4)
                        r.bearing(ss[span+end-1],cid,span,py,u=u,beam_y=y)
        r.notes += ['U54 is an open U polygon with source outer depth54in, top99.5in, bottom56in and opening61.5in. Interior bottom thickness8in and sloping inner web corners are explicit assumptions; J=.011m4 is assumed. Cavities are retained; solid bounding-section stiffness is never used.',
            'Tapered pier columns use constant average transverse width6ft5in and thickness3ft6in; connecting low walls are omitted. HP14 piles use assumed .3556m flanges/depth and16mm web/flanges; tips fixed/elastic at source design lengths54/55ft, not verified driven tips.',
            'Pairs of actual pad centers are retained and rigidly coupled to each U beam line. End-bent integral restraint is simplified to the specified bearing-supported independent-span model.']
    elif bid=='fletcher-avenue':
        ys=[(j-3.5)*9*FT for j in range(8)]
        # Asymmetric 2 ft 6.75 in / 2 ft deck overhangs preserve the source station origin.
        r.v['deck']['u0_m']=-r.bs[-1]-(2+6.75/12)*FT;r.v['deck']['u1_m']=r.bs[-1]+2*FT
        r.v['continuity_units']=[dict(u0_m=r.v['deck']['u0_m'],u1_m=r.v['deck']['u1_m'])]
        r.v['deck']['patches']=[];r.patch('deck')
        for j,y in enumerate(ys):
            for i in range(2):r.beam(f'girder_{i}_{j}',i,y,ishape(64*IN,(26 if j in [0,7] else 24)*IN,.375*IN,2*IN))
        for i,cid,t in [(0,'abut_1',3.75*FT),(1,'pier_2_wall',3.5*FT),(2,'abut_3',3.75*FT)]:
            s=r.support(i,top=r.parts[cid]['bounds_m'][1][2]);r.wall(s,cid,t)
            for j,y in enumerate(ys):r.bearing(s,f'B{i+1}_bearing_{j+1}',0,y)
        r.notes.append('Haunched retained plate girders use a documented constant nominal64in total depth,2in flanges,3/8in web and24/26in flange widths. Variable60-72in webs and flange schedules are omitted; this is an assumed stiffness approximation, not original fabrication properties.')
    elif bid=='sr10-i65':
        ys=[-7.113,-5.08,-3.556,-1.778,0,1.778,3.556,5.08,7.113]
        for j,y in enumerate(ys):
            for i in range(4):
                sec=ishape(.840,.292,.014,.0254) if j in [0,8] else ishape(.920,.305,.015 if i in [0,3] else .016,.023 if i in [0,3] else .027)
                r.beam(f'beam_{i}_{j}',i,y,sec)
        for i in range(5):
            if i in [0,4]:
                cid=f'end_bent_{i+1}';s=r.support(i,top=mid(r.parts[cid],2));r.wall(s,cid,.8)
            elif i in [1,3]:
                cid=f'pier_{i+1}_widening';s=r.support(i,top=r.parts[cid]['bounds_m'][1][2]);
                # Two outer walls and central retained stem form the documented full plane.
                r.wall(s,cid,.61,y1=-2.5575);r.wall(s,cid,.61,y0=2.5575)
                r.wall(s,f'pier_{i+1}_retained',.61)
            else:
                s=r.support(i,'pier_3_hammerhead',.61,1.2,top=5.2)
                # Explicitly extend an effective cap to the outer added columns; not a source section claim.
                s['cap']['y0_m']=-7.621;s['cap']['y1_m']=7.621
                r.wall(s,'pier_3_stem',.61)
                for side in [-1,1]:r.column(s,f'pier_3_column_{side}',rectangle(.9,.61))
            for j,y in enumerate(ys):r.bearing(s,f'B{i+1}_bearing_{j+1}' if i in [1,2,3] else None,0,y,integral=i in [0,4])
        r.notes += ['Nominal I properties use explicit W840/W920 d,b,tw,tf dimensions from the geometry recipe, marked assumed rather than catalog-certified. Retained beams remain continuous; separate span IDs do not create hinges.',
            'Piers2/4 use continuous .610m shell walls partitioned into widened and retained component IDs; joint details omitted. Pier3 hammerhead is a .610x1.2m effective cap extended to added outer columns, with central wall and outer columns. Crash walls and detailed variable cap geometry are omitted.']
    elif bid=='us52-mud':
        # Module boundary midlines assign homogenized UHPC closure strips to neighboring panels.
        ub=[-length/2,r.bs[1],r.bs[2],length/2]
        yb=[-width/2]+[(j-4)*5*FT for j in range(1,8)]+[width/2]
        for i in range(3):
            for j in range(8):r.patch(f'deck_{i+1}_{j+1}',ub[i],ub[i+1],yb[j],yb[j+1])
        for i in range(4):
            if i in [1,2]:
                p=r.parts[f'pier_{i+1}_module_4'];s=r.support(i,top=p['bounds_m'][1][2])
                for j in range(8):r.wall(s,f'pier_{i+1}_module_{j+1}',3*FT,y0=yb[j],y1=yb[j+1])
                bed=f'pier_{i+1}_bed'
            else:
                end=1 if i==0 else 2;p=r.parts[f'bent_{end}_0'];s=r.support(i,top=p['bounds_m'][1][2])
                r.wall(s,f'bent_{end}_0',3*FT,y0=-width/2,y1=0);r.wall(s,f'bent_{end}_1',3*FT,y0=0,y1=width/2)
                bed=f'bent_{end}_bed'
            s['line_connection']=dict(cid=bed,width_m=3*FT)
        r.notes += ['Whole slab: no invented longitudinal girders. Twenty-inch structural slab modules are represented by continuous ShellMITC4 panels; UHPC closure strips are homogenized to adjacent panel concrete stiffness and reported under panel IDs.',
            'The 24 source modules are retained as result groups. Module/pier joints are assumed perfectly bonded, with no slip, interface cracking or special UHPC constitutive behavior. Pier and end-bent module walls participate in the load path.']
    return r.save()


def additional(bid):
    base=ROOT/'data/bridges'/bid;m=load(base/'model_manifest.json'); source=load(base/'source_ledger.json')
    if bid=='sr1-six-mile':
        spans=[6.664875,8.5,6.664875];r=Recipe(bid,spans,22.12975,14.3637,.45)
        r.v['mesh_step_u_m']=1.0;r.v['mesh_step_y_m']=.7
        r.patch('deck')
        for i in range(4):
            cid=f'support_{i}';s=r.support(i,top=r.parts[cid]['bounds_m'][1][2]);r.wall(s,cid,.8,y0=-14.3637/2,y1=14.3637/2)
            s['line_connection']=dict(integral=True)
        r.notes += ['Original structural drawings are absent. Source plans/NBI establish three continuous concrete slab spans; exact6.664875+8.5+6.664875m arrangement, .45m thickness, .8m walls and base fixity are hypothetical structural assumptions.',
            'No original bearing/foundation details are available. The displayed hypothetical support walls are included; their bases are fixed/elastic. This response is not a reconstruction of original measured support stiffness.']
        return r.save()
    if bid in ['us35-deer','us224-eight-mile']:
        r=Recipe(bid,source['spans_m'],source['deck_length_m'],source['deck_width_m'],source['structural_deck_thickness_m'])
        r.patch('deck'); sdef=source['girder_section'];ys=source['girder_y_m']
        sec=dict(kind='polygon',profile_yz_m=sdef['outer_profile_yz_m'],
                 void_profiles_yz_m=sdef['inner_void_profiles_yz_m'],torsion_J_m4=.018 if bid=='us35-deer' else .0185)
        # Independent signed area moments produce the centroid, including the CB21 void.
        from fem.solver import polygon_properties
        a,z,_=polygon_properties(sec['profile_yz_m']); az=a*z
        for hole in sec['void_profiles_yz_m']:
            ah,zh,_=polygon_properties(hole);a-=ah;az-=ah*zh
        for j,y in enumerate(ys):r.beam(f'beam_0_{j}',0,y,sec,'concrete',u0=sdef['beam_end_u_m'][0],u1=sdef['beam_end_u_m'][1],depth=sdef['depth_m'],centroid_from_bottom=az/a)
        for i in range(2):
            cid=f'cap_{i+1}';s=r.support(i,cid,r.parts[cid]['dimensions']['normal_width_m'])
            if bid=='us35-deer':
                for j in range(6):r.column(s,f'pile_stub_{i}_{j}',ishape(.3048,.3048,.010,.010),'steel','pile')
            else:r.wall(s,f'stem_{i+1}',.7112)
            for j,y in enumerate(ys):r.bearing(s,f'B{i+1}_bearing_{j+1}',0,y,integral=bid=='us35-deer')
        if bid=='us35-deer':r.notes += ['BT48x49 uses the dimensioned polygon from source ledger p20; no solid bounding rectangle. J=.018m4 is assumed; prestress and strand/reinforcement stresses are excluded.',
            'Integral end bents transfer translations and rotations through stiff links. Source steel bearing assemblies are embedded connection geometry and receive no elastomer-pressure claim. HP12x53 pile stubs use an assumed .3048m I profile with10mm plates, fixed/elastic at the1.5m display cut; no soil restraint or full driven pile response is claimed.']
        else:r.notes += ['CB21 properties subtract the dimensioned octagonal internal void from the48x21in outer rectangle. J=.0185m4 is assumed; solid end blocks, prestress and repaired/wrapped beam-end stiffness are omitted.',
            'Only the retained7.5in structural slab is composite. Proposed2in overlay contributes neither stiffness nor this pressure-only gravity. .7112m abutment wall thickness is the explicit source-reconstruction idealization.',
            'Fixed versus expansion bearing horizontal behavior is homogenized to10MN/m for this vertical-pressure demonstration; thermal movements and anchor forces are not evaluated.']
        return r.save()
    if bid in ['virginia-avenue','sr44-little-blue']:
        r=Recipe(bid,source['spans_m'],source['deck_length_m'],source['deck_width_m'],source['structural_deck_thickness_m'])
        r.patch('deck')
        if bid=='virginia-avenue':
            for girder in source['girder_sections']:
                depth=max(z['total_depth_m'] for z in girder['zones'])
                for zone in girder['zones']:
                    r.beam(girder['part_id'],0,girder['y_m'],ishape(zone['total_depth_m'],zone['flange_width_m'],zone['web_thickness_m'],zone['flange_thickness_m']),
                           u0=zone['u0_m'],u1=zone['u1_m'],depth=depth)
            for i in range(2):
                cid=f'abutment_{i+1}';s=r.support(i,top=r.parts[cid]['bounds_m'][1][2]);r.wall(s,cid,4*FT)
                for j,y in enumerate(source['girder_y_m']):r.bearing(s,f'B{i+1}_bearing_{j+1}',0,y)
            r.notes += ['Nine retained welded I girder profiles use the source ledger flange zones. Girder1 retains its distinct2013 replacement dimensions. Each line has a constant flattened centroid at maximum depth; flange step centroid shifts, end copes and camber are omitted.',
                'Only7.5in of the8in deck is structural; integral wearing allowance is excluded from stiffness. Abutment walls participate; footings and soil are replaced by fixed/elastic wall-base restraints.',
                'The source single span uses expansion and fixed bearings. Vertical load response uses the common assumed horizontal spring stiffness; thermal movements and true anchor forces are outside scope.']
        else:
            r.v['mesh_step_u_m']=1.0;r.v['mesh_step_y_m']=.7
            for i in range(2):
                cid=f'integral_bent_{i+1}';s=r.support(i,cid,r.parts[cid]['dimensions']['normal_thickness_m'])
                for j in range(1,9):
                    pcid=f'pile_{i+1}_{j}';dim=r.parts[pcid]['dimensions']
                    r.column(s,pcid,dict(kind='pipe',diameter_m=dim['diameter_m'],thickness_m=dim['wall_thickness_m']),'steel','pile')
                s['line_connection']=dict(integral=True)
            r.notes += ['Single structural slab shell with no invented girders or elastomeric bearings.19.5in structural thickness excludes the0.5in wearing allowance. Integral slab-to-bent six-direction links transfer moments into both cap and pipe-pile groups.',
                'Integral bents use average-depth beam caps.14in pipe piles retain source .25in wall thickness and estimated tip elevations; the hollow steel section is used, not the solid display cylinder. Tips fixed/elastic and no distributed soil springs are assumed; source design lengths are not verified as-driven embedment.']
        return r.save()
    raise ValueError('No reviewed source-specific recipe yet for '+bid)


def main():
    sys.path.insert(0,str(ROOT))
    ids=sys.argv[1:] or EXISTING+NEW
    for bid in ids:
        if not (ROOT/'data/bridges'/bid/'model_manifest.json').exists():continue
        existing(bid) if bid in EXISTING else additional(bid)


if __name__=='__main__':main()

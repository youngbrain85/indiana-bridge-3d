"""Fletcher Avenue and SR 10: drawing-backed exterior visualization models.

Requires the documented source binders in data/bridges/<id>/drawings.pdf.
Does not import the database or change existing models. Not an FE mesh generator.
"""
from pathlib import Path
import json
import numpy as np
import trimesh as tm
from shapely.geometry import Polygon
from bridge_geometry import Model, FT, IN, box, sweep, rod, rectangular_bar, concat, iform, bolt, sha
from build_indiana_batch2 import COMMON, haunch, beam

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'data/bridges'


def sources(out):
    index = json.loads((out/'source_index.json').read_text(encoding='utf8'))
    return [dict(id=s['title'], **{k:v for k,v in s.items() if k!='title'}) for s in index['source_documents']]


def finish(m, out, meta, ledger):
    index=json.loads((out/'source_index.json').read_text(encoding='utf8'))
    meta.update(external_sources=sources(out), source_binder=index,
        source_note=meta['source_note']+' Drawing download is a local review binder; original source files and page offsets are recorded in source_index.json.')
    for part in m.parts:
        assert part['pdf_pages'] and all(1<=p<=index['pages'] for p in part['pdf_pages'])
    (out/'source_ledger.json').write_text(json.dumps(ledger,indent=2),encoding='utf8')
    return m.save(out,meta)


def seat_steps(m, bi, u, ys, thickness, layer, pages):
    contacts=[c for c in m.contacts if c['id'].startswith(f'B{bi}_bearing_')]
    seat=min(c['seat_m'] for c in contacts)
    for j,(y,c) in enumerate(zip(ys,contacts)):
        if c['seat_m']>seat+.0001:
            m.add(f'B{bi}_seat_{j}',f'Bent {bi} | seat riser {j+1}',layer,
                m.transverse(u,thickness,y-.38,y+.38,seat,c['seat_m']),pages,
                'Derived bearing contact elevation','Seat tops fit the reconstructed girder profile; original survey and shim elevations are not asserted.')
    return seat


def splices(m,key,u,y,top,d,b,tw,pages,webw=.48,webh=.71,plate=.013,flangew=1.13,grid=(5,7)):
    x=m.sx(u,y);z=top-d/2
    plates=[box(x-webw/2,x+webw/2,y+s*(tw/2+plate/2)-plate/2,y+s*(tw/2+plate/2)+plate/2,z-webh/2,z+webh/2) for s in [-1,1]]
    plates += [box(x-flangew/2,x+flangew/2,y-b/2,y+b/2,zz,zz+plate) for zz in [top-d-plate,top]]
    m.add(key,key.replace('_',' '),'steel',concat(plates),pages,
        'Source splice positions; plate envelope reconstruction','Inner cover strips, fabrication holes and precise flange transitions omitted.',web_plate_width_m=webw,web_plate_height_m=webh)
    nx,nz=grid;fast=[]
    for dx in np.linspace(-webw/2+.05,webw/2-.05,nx):
        for dz in np.linspace(-webh/2+.05,webh/2-.05,nz):
            fast.append(bolt([x+dx,y-tw/2-plate,z+dz],[x+dx,y+tw/2+plate,z+dz],.011))
    m.add(key+'_bolts',key.replace('_',' ')+' | visible web fasteners','fasteners',concat(fast),pages,
        'Representative fastener grid','22 mm visual bolt envelopes; exact source pattern and flange bolts are not reconstructed.',visual_bolt_count=len(fast))


def drain(m,key,u,y,pages,drop=1.3):
    x=m.sx(u,y);z=m.surface(x,y)
    grate=[box(x-.19,x+.19,y-.15,y+.15,z+.002,z+.018)]
    # Individual grate bars are raised; no Boolean hole is falsely implied in the deck.
    for dx in np.linspace(-.16,.16,8):grate.append(box(x+dx-.009,x+dx+.009,y-.13,y+.13,z+.018,z+.031))
    grate.append(rod([x,y,z-.03],[x,y,z-drop],.075,16))
    m.add(key,key.replace('_',' '),'drainage',concat(grate),pages,
        'Drain positions from plans; simplified external casting and outlet','Visible envelope only. Local slab/curb penetrations, clamps, elbows and drain interiors are not resolved.',outlet_diameter_m=.15)


def fletcher():
    out=BASE/'fletcher-avenue';span=147*FT;u0=-span-(2+6.75/12)*FT;u1=span+2*FT
    width=68.5*FT;length=u1-u0;slab=8*IN;clear=.09;skew=28+47/60+15/3600
    def grade(x):
        station=1485.98+np.asarray(x)/FT
        # Source roadway profile, piecewise vertical curves. Feet converted after evaluation.
        s=station;t=s-1340;e=727.61+.0142*t+(.0009-.0142)*t*t/(2*90)
        t=s-1430;e=np.where(s>=1430,728.29+.0009*t+(-.02-.0009)*t*t/(2*140),e)
        e=np.where(s>=1570,726.95-.02*(s-1570),e)
        t=s-1620;e=np.where(s>=1620,725.95-.02*t+(.0154)*t*t/(2*50),e)
        return (e-698.59)*FT
    m=Model('fletcher-avenue',length,width,skew,grade,crossfall=.015)
    roadhalf=27*FT
    # South sidewalk has a level supporting deck cross-slope, per sheet 60.
    m.surface=lambda x,y:grade(x)-.015*np.minimum(np.abs(y),roadhalf)-.015*np.maximum(np.asarray(y)-roadhalf,0)
    m.colors.update(girders='#657d85',steel='#72888f',bracing='#70858a',rails='#ddd5bf')
    m.add('deck','Proposed 2026 deck | two continuous spans','deck',m.slab(u0,u1,-width/2,width/2,slab),[55,59,60],
        'Dimensioned proposed deck envelope','298 ft 6.75 in overall floor; asymmetric 2 ft 6.75 in / 2 ft bearing overhangs. No existing removed deck is retained.',thickness_m=slab,width_m=width,length_m=length)
    def walktop(x,y):return grade(x)-.015*roadhalf+8*IN+.02*(np.abs(y)-roadhalf)
    for side in [-1,1]:
        y0,y1=sorted([side*roadhalf,side*width/2])
        m.add(f'walk_{side}',f'{"South" if side<0 else "North"} sidewalk | 6 ft 1 in clear','sidewalks',
            sweep([(y0,0),(y1,0),(y1,1),(y0,1)],np.linspace(u0,u1,151),lambda u,y,t:(m.sx(u,y),y,(1-t)*m.surface(m.sx(u,y),y)+t*walktop(m.sx(u,y),y))),[55,60],
            'Dimensioned clear width and nominal curb; crossfall reconstructed','Both walks rise away from the road at 2%; the south supporting deck is level under the walk.',clear_width_m=(6+1/12)*FT,nominal_curb_height_m=8*IN)
    ys=(np.arange(8)-3.5)*9*FT
    def web(u):
        t=np.clip(1-abs(u)/(19.5*FT),0,1)
        return (60+12*t*t*(3-2*t))*IN
    def tf(u,j):return ((2.5 if j in [0,7] else 2.25) if abs(u)<=40*FT else 1.75)*IN
    def depth(u,j):return web(u)+2*tf(u,j)
    for j,y in enumerate(ys):
        b=(26 if j in [0,7] else 24)*IN;tw=.375*IN
        for i,(a,bend) in enumerate([(-span,0),(0,span)]):
            # Add duplicate station limits just around plate schedule changes to retain steps.
            xs=np.unique(np.r_[np.linspace(a,bend,101),[v for v in [-40*FT-.00001,-40*FT,40*FT,40*FT+.00001] if a<v<bend]])
            pr=iform(1,b,tw,.1)
            def point(u,v,t):
                d=depth(u,j);f=tf(u,j);z=t*f/.1 if t<=.1 else d-(1-t)*f/.1 if t>=.9 else f+(t-.1)*web(u)/.8
                return m.sx(u,y),y+v,m.surface(m.sx(u,y),y)-slab-clear-d+z
            m.add(f'girder_{i}_{j}',f'Span {chr(65+i)} | retained plate girder {j+1}','girders',sweep(pr,xs,point),[55,57,99,100,101],
                'Historical nominal section and support haunch; reconstructed profile',
                '60 in web increasing to 72 in at the pier. Smooth haunch approximation replaces the original multi-radius setting-out. Flange schedule, camber and cross-girder top elevations need reconciliation.',flange_width_m=b,web_thickness_m=tw,span_m=span)
            haunch(m,f'haunch_{i}_{j}',a,bend,y,b,clear,slab,[59,60,65])
        for bi,u in enumerate([-span,0,span],1):
            bottom=m.surface(m.sx(u,y),y)-slab-clear-depth(u,j)
            m.bearing(f'B{bi}_bearing_{j+1}',u,y,bottom,depth(u,j),[58] if bi==3 else [99,103,104],
                pad=(.4064,.508,.105 if bi==3 else .10),plate=(.47,.584,.255 if bi==3 else .22),
                note='2026 S6-A/PTFE assembly envelope at Abutment 3; retained steel shoes at other supports. S6-A laminations, HP14x89 bolster, seat shims and retainers are simplified; stack elevations are derived.')
        for si,u in enumerate([-40*FT,40*FT]):
            splices(m,f'girder_{j+1}_splice_{si+1}',u,y,m.surface(m.sx(u,y),y)-slab-clear,depth(u,j),b,tw,[100,101],webw=1.2,webh=1.37,plate=.0159,flangew=1.53,grid=(12,10))
        for si,u in enumerate([-span,-15*FT,-10*FT,-5*FT,0,5*FT,10*FT,15*FT,span]):
            x=m.sx(u,y);top=m.surface(x,y)-slab-clear;f=tf(u,j)
            pieces=[box(x-.008,x+.008,y+s*.14-.13,y+s*.14+.13,top-depth(u,j)+f,top-f) for s in [-1,1]]
            m.add(f'stiffener_{j}_{si}',f'Girder {j+1} | bearing or haunch stiffener {si+1}','steel',concat(pieces),[100,101],
                'Selected support/haunch stiffeners','Plate widths and selected stations approximate; full source stiffener schedule is not represented.')
    # Cross frames are transverse in space; plan stations are staggered by skew.
    rows=-span+(8+10.875/12)*FT+np.arange(13)*(22+9/12)*FT
    for i,u in enumerate(rows):
        for j in range(7):
            ya,yb=ys[j]+.33,ys[j+1]-.33;x=m.sx(u,(ya+yb)/2)
            za=m.surface(x,ya)-slab-clear-.16;zb=m.surface(x,yb)-slab-clear-.16;d=min(depth(x-m.k*ya,j),depth(x-m.k*yb,j+1))-.32
            bars=[rectangular_bar([x,ya,za],[x,yb,zb-d],.10,.012),rectangular_bar([x,ya,za-d],[x,yb,zb],.10,.012)]
            m.add(f'crossframe_{i}_{j}',f'Cross frame row {i+1} | bay {j+1}','bracing',concat(bars),[99,102],
                'Source framing topology; member profiles simplified','Source 22 ft 9 in rows; full skew end brackets, gussets and end-frame offsets remain approximate.')
    for bay in [0,3,6]:
        for i,(a,b) in enumerate(zip(rows[:-1],rows[1:])):
            yy0,yy1=(ys[bay],ys[bay+1]) if i%2==0 else (ys[bay+1],ys[bay]);ua=a;ub=b;z0=m.surface(m.sx(a,yy0),yy0)-slab-clear-.14;z1=m.surface(m.sx(b,yy1),yy1)-slab-clear-.14
            m.add(f'lateral_{bay}_{i}',f'Top lateral bracing | bay {bay+1}, panel {i+1}','bracing',
                rectangular_bar([m.sx(ua,yy0),yy0,z0],[m.sx(ub,yy1),yy1,z1],.12,.016),[99,102],
                'Representative lateral-brace envelope','Source tee sections, zig-zag directions and connections simplified.')
    for bi,u in enumerate([-span,0,span],1):
        seat=seat_steps(m,bi,u,ys,1.0,'bearings',[94,96,98]);end=bi!=2
        if not end:
            yhalf=79*FT*m.c/2
            m.add('pier_2_wall','Pier 2 | retained solid wall','piers',m.transverse(u,3.5*FT,-yhalf,yhalf,2*FT,seat),[98],
                'Source solid-wall topology and width','The source has a wall pier, not a row of columns. Rounded ends and original seat steps are simplified.',normal_thickness_m=3.5*FT,skew_length_m=79*FT)
            m.add('pier_2_footing','Pier 2 | spread footing','foundations',m.transverse(u,13*FT,-40.5*FT*m.c,40.5*FT*m.c,0,2*FT),[98],thickness_m=2*FT)
        else:
            sign=-1 if bi==1 else 1;bottom=(705.1-698.59)*FT
            m.add(f'abut_{bi}',f'Abutment {bi} | retained stem','abutments',m.transverse(u,3.75*FT,-width/2-.25,width/2+.25,bottom+2*FT,seat),[94,96],
                'Historical abutment envelope','Taper, exact footing offsets and patched concrete boundaries are simplified.')
            m.add(f'abut_{bi}_footing',f'Abutment {bi} | footing envelope','foundations',m.transverse(u,12*FT,-width/2-.5,width/2+.5,bottom,bottom+2*FT),[94,96], 'Historical footing nominal envelope')
            m.add(f'abut_{bi}_backwall',f'Abutment {bi} | reconstructed backwall','abutments',
                sweep([(-width/2,0),(width/2,0),(width/2,1),(-width/2,1)],[u+sign*.48,u+sign*.78] if sign>0 else [u-.78,u-.48],
                    lambda a,y,t:(m.sx(a,y),y,(1-t)*seat+t*(m.surface(m.sx(a,y),y)-slab))),[56],
                '2026 reconstructed interface envelope','Semi-integral end detail and local pavement ledges are simplified.')
            for side in [-1,1]:
                y=side*(width/2+.12);a,b=sorted([m.sx(u,y),m.sx(u,y)+sign*5.2])
                m.add(f'wing_{bi}_{side}',f'Abutment {bi} | retained wing {side}','abutments',box(a,b,y-.20,y+.20,bottom+FT,seat+.3),[94,95,96,97],
                    'Approximate wing envelope','Original splayed plan and individual wing lengths require further reconciliation; this is not a surveyed boundary.')
    # Architectural TX railing: genuine open windows (not solid panels).
    window_total=0
    for side in [-1,1]:
        h=(4.5 if side<0 else 3.5)*FT;plinth=FT if side<0 else 0;y=side*(width/2-8*IN)
        for span_i,(aa,bb) in enumerate([(u0,0),(0,u1)]):
            cuts=np.linspace(aa,bb,6)
            for panel,(a,b) in enumerate(zip(cuts[:-1],cuts[1:])):
                lo=a+FT;hi=b-FT;holes=[]
                for c in (lo+hi)/2+(np.arange(18)-8.5)*1.5*FT:
                    zb=plinth+.30;zt=plinth+.30+16*IN;hw=3*IN
                    holes.append([(c-hw,zb),(c-hw,zt-.055),(c-.035,zt+.005),(c,zt+.025),(c+.035,zt+.005),(c+hw,zt-.055),(c+hw,zb)])
                poly=Polygon([(lo,0),(hi,0),(hi,h),(lo,h)],holes)
                rail=tm.creation.extrude_polygon(poly,FT,engine='earcut');v=rail.vertices.copy();yy=y+v[:,2]-FT/2
                rail.vertices=np.c_[v[:,0]+m.k*yy,yy,walktop(v[:,0]+m.k*yy,yy)+v[:,1]]
                m.add(f'tx_{side}_{span_i}_{panel}',f'{"South modified" if side<0 else "North"} TX rail | span {chr(65+span_i)}, panel {panel+1}','rails',rail,[63,64,65,119,120],
                    'Source height and 18 open windows per panel; simplified opening profile','10 panels per side; 17 spaces at 18 in per panel. Window throat width 6 in; molded splays, curved heads and pilaster recesses simplified.',height_m=h,window_count=18,window_spacing_m=1.5*FT)
                window_total+=18
            for i,u in enumerate(cuts):
                a=max(aa,u-FT);b=min(bb,u+FT)
                m.add(f'txpost_{side}_{span_i}_{i}',f'TX rail | span {chr(65+span_i)} pilaster {side}-{i}','rails',
                    sweep([(y-.18,0),(y+.18,0),(y+.18,h),(y-.18,h)],np.linspace(a,b,3),lambda q,v,z:(m.sx(q,v),v,walktop(m.sx(q,v),v)+z)),[63,64,65,121,122],
                    'Solid pilaster envelope; molded recesses omitted')
    # Skew-to-square RCBA plans: overall 66 ft 6 in width, 20 ft 6 in at centerline.
    for end,u in [(-1,u0),(1,u1)]:
        w=(66+6/12)*FT;outer=u+end*20.5*FT
        m.add(f'approach_{end}',f'Abutment {1 if end<0 else 3} | proposed skew-to-square RCBA','approaches',
            sweep([(-w/2,0),(w/2,0),(w/2,1),(-w/2,1)],np.linspace(0,1,45),
                lambda t,y,h:((1-t)*m.sx(u,y)+t*outer,y,m.surface((1-t)*m.sx(u,y)+t*outer,y)-(1-h)*FT)),[66,67,68,69],
            'Source main plan geometry; local extensions simplified','Square roadway end and skew bridge end; centerline length 20 ft 6 in. Manholes, wing-side walkway extensions and exact terminal curb details remain incomplete.',centerline_length_m=20.5*FT,thickness_m=FT)
        for side in [-1,1]:
            y0,y1=sorted([side*roadhalf,side*w/2]);mesh=sweep([(y0,0),(y1,0),(y1,1),(y0,1)],np.linspace(0,1,25),
                lambda t,y,h:((1-t)*m.sx(u,y)+t*outer,y,(1-h)*m.surface((1-t)*m.sx(u,y)+t*outer,y)+h*walktop((1-t)*m.sx(u,y)+t*outer,y)))
            m.add(f'approach_walk_{end}_{side}',f'Abutment {1 if end<0 else 3} | approach sidewalk {side}','sidewalks',mesh,[66,68], 'Main approach sidewalk envelope; corner extensions omitted')
        m.add(f'joint_{end}',f'Abutment {1 if end<0 else 3} | visual joint strip','joints',m.slab(u-.009,u+.009,-width/2,width/2,.06),[56,61],
            'Schematic joint strip','Opening temperature, seals and sidewalk sliding plates are not resolved.')
    for side in [-1,1]:
        for end in [-1,1]:drain(m,f'OS_drain_{side}_{end}',end*(span-8*FT),side*(roadhalf-.20),[55,59,65],1.7)
    m.cover('Whole two-span structure','modeled_with_simplifications','Eight retained haunched plate-girder lines, both spans, skew deck, two walks, 24 bearing envelopes and all three supports.',[55,60,98,99,100,101],['deck','girders','haunches','piers','abutments','bearings','foundations'])
    m.cover('Retained steel details','modeled_with_simplifications','Support haunches, field-splice envelopes, visible web bolts, selected stiffeners and bracing. Exact plate schedule, curved haunch radii, camber, gussets and shoe assemblies remain incomplete.',[57,58,99,100,101,102,103,104],['steel','fasteners','bracing'])
    m.cover('Proposed architectural rails and walks','modeled_with_simplifications','North 3 ft 6 in TX rail and south 4 ft 6 in modified TX rail, 360 actual window openings and raised walks. Molded window splays and recesses remain simplified.',[60,63,64,65,119,120],['rails','sidewalks'])
    m.cover('Approaches, drainage and interfaces','modeled_with_simplifications','Both skew-to-square approach slabs and four drain envelopes. TTX transitions, corner walkway extensions, drain routing, slab penetrations, roadside terminals and traffic equipment are not reconstructed.',[55,56,66,67,68,69],['approaches','joints','drainage'])
    m.cover('Unresolved exterior details','not_modeled','Exact field bearing/shim elevations, wing splay, fabrication holes, rail moldings, full transition geometry, complete drainage, utility fittings and site surfaces.',[55,58,65,66,94,96],[])
    m.checks=dict(spans_m=[span,span],support_lines=3,girder_lines=8,girder_segments=16,bearings=24,tx_window_openings=window_total,skew_deg=skew,solid_wall_pier=True)
    return finish(m,out,dict(title='Fletcher Avenue over I-65 / I-70 | proposed 2026 deck replacement',structure_id='I65-110-05723B',designation='2200723',spans_m=[span,span],deck_thickness_m=slab,
        source_note='INDOT B-44576 proposed 2026 Fletcher deck/rail/bearing work over retained 1971-73 steel and substructure. Old I-65-112-5723 alias is matched by crossing, 2 x 147 ft spans, eight lines and identical skew. Construction completion is not established.',
        assumptions=COMMON+['Historical station numbers and proposed roadway grades differ. Nominal reconstructed girder/seat interfaces fit the proposed grade; fabrication camber and exact retained elevations are unresolved.','The local origin is near Pier 2; vertical zero uses the old pier-footing bottom as a display datum. No surveyed geographic placement.','Source review binder also contains Virginia Avenue and traffic/site sheets; those structures are not part of this GLB.']),
        dict(modeled_state='Proposed 2026 Fletcher deck replacement over retained steel/substructure',deck_length_m=length,deck_width_m=width,spans_m=[span,span],girder_lines=8,spacing_m=9*FT,skew_deg=skew,primary_binder_pages=dict(general=55,section=60,steel=[99,100,101],pier=98,rails=[63,64,65,119,120]),limitations=[c for c in m.coverage if c['status']!='modeled']))


def sr10():
    out=BASE/'sr10-i65';spans=np.array([39+.5/12,65.75,65.75,39+.5/12])*FT;bs=np.r_[0,np.cumsum(spans)]-sum(spans)/2
    length=(211+2.75/12)*FT;width=(50+3.625/12)*FT;slab=.2;clear=.075
    m=Model('sr10-i65',length,width,0,lambda x:7.371-.00394*np.asarray(x)**2/65,crossfall=.02)
    m.colors.update(girders='#6c858c',steel='#7c9194')
    ys=np.array([-7.113,-5.080,-3.556,-1.778,0,1.778,3.556,5.080,7.113])
    m.add('deck','Retained widened deck | 1998 reconstruction geometry','deck',m.slab(-length/2,length/2,-width/2,width/2,slab),[24,37,59],
        'Dimensioned 200 mm slab; 2026 floor envelope','Metric 1998 and rounded 2026 imperial callouts differ slightly. Latest general-plan overall limits control; no original removed concrete end-span girders remain.',length_m=length,width_m=width,thickness_m=slab)
    m.add('overlay','Retained polymeric wearing surface | 2019 overlay design','deck',m.slab(-length/2,length/2,-(width/2-.45),width/2-.45,.375*IN,.375*IN),[46,47],
        'Nominal 3/8 in overlay from 2019 plans','Separate nonstructural surface layer; actual remaining field thickness is unknown.',thickness_m=.375*IN)
    def section(i,j):
        if j in [0,8]:return (.840,.292,.014,.0254,'W840x193')
        if i in [0,3]:return (.920,.305,.015,.023,'W920x201')
        return (.920,.305,.016,.027,'W920x223 retained')
    for j,y in enumerate(ys):
        for i,(a,b) in enumerate(zip(bs[:-1],bs[1:])):
            d,bf,tw,tf,label=section(i,j)
            beam(m,f'beam_{i}_{j}',f'Span {chr(65+i)} | beam {j+1} | {label}',a,b,y,iform(d,bf,tw,tf),slab,clear,[24,33,34],
                'Drawing section designation; nominal visualization profile','Rolled-section fillets and exact catalog dimensions approximated. Interior end beams splice 900 mm inside middle spans; the model divides selectable members at supports.')
            haunch(m,f'haunch_{i}_{j}',a,b,y,bf,clear,slab,[36,37])
        for bi,u in enumerate(bs):
            if bi in [0,4]:continue # Integral end bents: no fictitious discrete bearings.
            d=section(min(bi,3),j)[0];bottom=m.surface(u,y)-slab-clear-d
            if bi==2:
                m.bearing(f'B{bi+1}_bearing_{j+1}',u,y,bottom,d,[34],pad=(.4,.510,.205 if j not in [0,8] else .405),plate=(.230,.310,.055),
                    note='Fixed steel shoe/base envelope, not elastomer. Source stack 260 mm at retained beams / 460 mm at new outer beams; curvature and anchor hardware simplified.')
            else:
                m.bearing(f'B{bi+1}_bearing_{j+1}',u,y,bottom,d,[34],pad=(.250,.350,.067),plate=(.280,.405,.058),note='Type I 125 mm elastomer/plate stack. Internal laminations and side retainers omitted.')
        for q,u in enumerate([bs[1]+.9,bs[2]+.457,bs[3]-.9]):
            d,bf,tw,tf,_=section(1,j)
            splices(m,f'beam_{j+1}_splice_{q+1}',u,y,m.surface(u,y)-slab-clear,d,bf,tw,[33,34],webh=.710 if j in [0,8] else .770,grid=(5,7))
    # Transverse channel diaphragm rows follow source framing stations.
    rows=np.r_[bs[0]+np.array([1.7,6.8,11.9]),bs[1]+np.array([6.833,13.437,19.584]),bs[2]+np.array([7.061,13.665,20.041]),bs[3]+np.array([5.1,10.2])]
    for q,u in enumerate(np.unique(np.round(rows,6))):
        for j,(ya,yb) in enumerate(zip(ys[:-1],ys[1:])):
            height=.38 if j in [1,6] else .46;top=min(m.surface(u,ya),m.surface(u,yb))-slab-clear-.10
            b=.105;tw=.011;tf=.017;pr=[(-b/2,0),(b/2,0),(b/2,tf),(-b/2+tw,tf),(-b/2+tw,height-tf),(b/2,height-tf),(b/2,height),(-b/2,height)]
            m.add(f'diaphragm_{q}_{j}',f'Diaphragm row {q+1} | bay {j+1}','diaphragms',
                sweep(pr,[ya+.16,yb-.16],lambda y,x,z:(u+x,y,top-height+z)),[33,35],
                'Source channel topology and framing rows; nominal profile','MC460/C380 channel envelopes; retained connections and precise channels within each bay require reconciliation.',depth_m=height)
    # Piers 2 and 4: wide upper wall with reconstructed side stems and retained central stem.
    for bi in [1,3]:
        u=bs[bi];seat=seat_steps(m,bi+1,u,ys,.61,'bearings',[31,34]);base=-.267;mid=3.391;top=seat
        profile=[(-7.621,base),(-2.5575,base),(-2.5575,mid),(2.5575,mid),(2.5575,base),(7.621,base),(7.621,top),(-7.621,top)]
        wall=sweep(profile,[-.305,.305],lambda x,y,z:(u+x,y,z))
        m.add(f'pier_{bi+1}_widening',f'Pier {bi+1} | reconstructed side stems and upper wall','piers',wall,[31],
            'Dimensioned pier reconstruction topology','15.242 m cap extent and 610 mm wall. Exact source seat steps replaced by derived risers. New side concrete closes against the retained 5.115 m stem; construction seams and keyways simplified.',wall_thickness_m=.610,cap_width_m=15.242)
        m.add(f'pier_{bi+1}_retained',f'Pier {bi+1} | retained central stem','piers',box(u-.305,u+.305,-2.5575,2.5575,base,mid),[28,31],
            'Retained central stem from reconstruction sheet','Interfaces meet the new concrete; no unsupported air gaps are inserted at the construction joints.',width_m=5.115,thickness_m=.610)
        for side in [-1,1]:
            ya,yb=sorted([side*3.22,side*7.983])
            m.add(f'footing_{bi+1}_{side}',f'Pier {bi+1} | widened footing {side}','foundations',box(u-1.295,u+1.295,ya,yb,base-.61,base),[31],
                'Source widened footing dimensions; exact offset simplified',width_m=2.59,length_m=4.763,thickness_m=.610)
    # Central pier retains the original hammerhead and receives two outside columns/crash walls.
    u=bs[2];seat=seat_steps(m,3,u,ys,.610,'bearings',[32,34]);base=-.337;stemtop=3.549;oldtop=seat
    cap=sweep([(-5.601,oldtop),(5.601,oldtop),(5.601,oldtop-.915),(2.858,stemtop),(-2.858,stemtop),(-5.601,oldtop-.915)],[-.305,.305],lambda x,y,z:(u+x,y,z))
    m.add('pier_3_hammerhead','Pier 3 | retained hammerhead cap','piers',cap,[32], 'Source retained hammerhead envelope','Nominal seat elevations fit the reconstructed beam and shoe stacks; cap steps and chamfers simplified.')
    m.add('pier_3_stem','Pier 3 | retained central wall stem','piers',box(u-.305,u+.305,-2.858,2.858,base,stemtop),[32], 'Retained stem envelope')
    for side in [-1,1]:
        y=side*7.113
        m.add(f'pier_3_column_{side}',f'Pier 3 | added outer rectangular column {side}','piers',box(u-.305,u+.305,y-.45,y+.45,base,oldtop-.915),[32],
            'Dimensioned rectangular column envelope',width_m=.9,thickness_m=.61)
        ya,yb=sorted([side*5.601,side*7.621])
        m.add(f'pier_3_cap_{side}',f'Pier 3 | widened cap end {side}','piers',box(u-.305,u+.305,ya,yb,oldtop-.915,oldtop),[32],
            'Source cap extension envelope; rounded corners omitted')
        ya,yb=sorted([side*3.0,side*7.62])
        m.add(f'pier_3_crash_{side}',f'Pier 3 | collision wall {side}','piers',box(u-.305,u+.305,ya,yb,base,1.643),[32],
            'Source collision-wall topology; exact end joint simplified',thickness_m=.61)
        ya,yb=sorted([side*2.8,side*7.8])
        m.add(f'pier_3_footing_{side}',f'Pier 3 | widened footing {side}','foundations',box(u-.9,u+.9,ya,yb,base-.61,base),[32],
            'Source 5.0 x 1.8 x 0.61 m footing envelope; exact plan offset simplified')
    # Integral ends enclose the steel. Do not put separate bearings under these ends.
    for bi,u in [(0,bs[0]),(4,bs[4])]:
        end=-1 if bi==0 else 1;zbase=5.443
        m.add(f'end_bent_{bi+1}',f'Bent {bi+1} | integral cap','abutments',
            sweep([(-7.991,0),(7.991,0),(7.991,1),(-7.991,1)],[u-.4,u+.4],lambda x,y,t:(x,y,zbase*(1-t)+t*(m.surface(x,y)-slab))),[29,30],
            'Dimensioned integral-bent envelope','Steel embeds into this cap. Pavement ledge, exact upper steps and buried HP310x79 piles are not reconstructed.',normal_width_m=.8,width_m=15.982)
        for side in [-1,1]:
            y=side*7.84;a,b=sorted([u-end*1.6,u+end*2.1])
            m.add(f'wing_{bi}_{side}',f'Bent {bi+1} | wingwall {side}','abutments',box(a,b,y-.15,y+.15,4.993,7.146),[29,30],
                'Dimensioned 3.7 m wing envelope; upper slope simplified',length_m=3.7,thickness_m=.3)
    m.barriers(-length/2,length/2,[39,59],height=.84,width=.4,top=.24,segments=4)
    for end in [-1,1]:
        a,b=sorted([end*(length/2+.015),end*(length/2+.015+20.5*FT)])
        m.add(f'approach_{end}',f'Bent {1 if end<0 else 5} | proposed 2026 approach slab','approaches',m.slab(a,b,-(50+4.125/12)*FT/2,(50+4.125/12)*FT/2,14*IN),[59,61],
            '2026 approach dimensions','20 ft 6 in long, 14 in deep. Existing deck and 2019 overlay remain distinct from the replacement approach.',length_m=20.5*FT,thickness_m=14*IN)
        m.add(f'joint_{end}',f'Bent {1 if end<0 else 5} | Type IA interface','joints',m.slab(end*length/2-.01,end*length/2+.01,-width/2,width/2,.06),[59,61], 'Schematic Type IA joint strip')
        for side in [-1,1]:
            y=side*(width/2-.23)
            # Main TFC transition envelope follows grade; final guardrail terminal omitted.
            pr=[(y-.2,0),(y+.2,0),(y+.2,1),(y-.2,1)]
            m.add(f'transition_{end}_{side}',f'Bent {1 if end<0 else 5} | TFC transition {side}','rails',
                sweep(pr,np.linspace(a,b,15),lambda x,v,t:(x,v,m.surface(x,v)+t*(.84-.28*abs(x-end*length/2)/(20.5*FT)))),[61],
                'TFC external transition envelope','Exact sloping curb, metal connections and roadway guardrail terminals omitted.')
            for offset in [2.5,4.5]:drain(m,f'drain_{end}_{side}_{int(offset*10)}',end*(sum(spans)/2-offset),side*(width/2-.65),[37,38],1.4)
    m.cover('Whole four-span steel bridge','modeled_with_simplifications','Nine nonuniformly spaced beam lines, all four spans, widened slab and a separate nominal retained overlay.',[24,33,37,46,59],['deck','girders','haunches'])
    m.cover('Steel connections and support topology','modeled_with_simplifications','Channel diaphragm rows, field splice envelopes and 27 pier shoes/bearings. Both end bents are integral, with no invented end bearings.',[29,33,34,35],['steel','fasteners','diaphragms','bearings'])
    m.cover('Retained and widened piers','modeled_with_simplifications','Piers 2/4 reconstructed side-wall stems; Pier 3 retained hammerhead, added outer columns and low collision walls. Footing offsets and seats remain approximate.',[28,31,32],['piers','foundations','abutments'])
    m.cover('Rails, approaches and drainage','modeled_with_simplifications','Existing barrier envelopes, both proposed 2026 14 in approach slabs, four transition envelopes and eight drain outlets. Drain piping and slab penetrations remain incomplete.',[38,39,59,61],['rails','approaches','joints','drainage'])
    m.cover('Unresolved details and site','not_modeled','Precise rolled sections, camber and field seats, buried pile tips, full slopewalls and drainage collectors, bolts/gussets and terminal hardware. Interchange roadways are outside this GLB.',[24,29,34,38,59],[])
    m.checks=dict(spans_m=spans.tolist(),support_lines=5,girder_lines=9,girder_segments=36,bearings=27,integral_end_bents=2,discrete_end_bearings=0,girder_y_m=ys.tolist())
    return finish(m,out,dict(title='SR 10 over I-65 | retained bridge with proposed 2026 approaches',structure_id='010-37-04888C / D',designation='2600080',spans_m=spans.tolist(),deck_thickness_m=slab,
        source_note='INDOT R-43918 proposed 2026 approaches over the retained 1998 B-23753 widened steel bridge, with the 2019 B-41210 nominal polymeric overlay retained. 2026 general/detail sheets use suffix C while the title uses D; both are preserved. Construction completion is not established.',
        assumptions=COMMON+['Metric structural dimensions and 2026 imperial general-plan dimensions are explicitly distinguished; small rounding differences remain.','1998 grade curve (65 m) governs the structural display; 2019 says 215 ft and 2026 says 213.25 ft. Current surveyed grades and bearing seats are not available.','Nominal W sections are visualization profiles, not verified section properties. No FEM analysis was generated for this bridge.']),
        dict(modeled_state='Retained 1998 bridge and nominal 2019 overlay with proposed 2026 approaches',spans_m=spans.tolist(),deck_length_m=length,deck_width_m=width,girder_y_m=ys.tolist(),support_bearings=27,integral_end_bents=2,source_pages=dict(structure=24,piers=[31,32],steel=[33,34],overlay=46,new_general=59,new_approaches=61),limitations=[c for c in m.coverage if c['status']!='modeled']))


if __name__=='__main__':
    import sys
    targets=dict(fletcher=fletcher,sr10=sr10)
    for name in sys.argv[1:] or targets:targets[name]()

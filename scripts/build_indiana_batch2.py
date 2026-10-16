"""Rebuild four whole-bridge exterior models from bundled INDOT drawings.

Run after drawings.pdf and reference PDFs have been placed in each output directory.
Individual source states and approximation boundaries are deliberately retained.
"""
from pathlib import Path
import json
import numpy as np
from bridge_geometry import Model, FT, IN, box, sweep, rod, rectangular_bar, concat, iform, bolt, sha

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'data/bridges'
COMMON=[
    'Exterior visualization reconstruction, not an as-built survey, load rating or validated FEM mesh.',
    'No internal reinforcement, prestressing strands, embedded studs, weld beads or fabrication holes. Material colors are visualization choices.',
    'Source pages mix historical removals and proposed work. Only the explicitly named design state is modeled; the separately stored later references do not alter that state.',
    'Buried foundations are hidden by default. Unknown driven pile lengths, terrain and approach-road terminal systems are omitted.',
    'Bearing contact checks verify constructed geometric attachment only; they do not establish surveyed bearing elevations or fabrication tolerances.'
]

def reference(doc,title,file=None):
    r=dict(id=title,url=f'https://erms12c.indot.in.gov/viewdocs/View12.aspx?Id={doc}')
    if file:r.update(local_file=file.name,sha256=sha(file))
    return r

def haunch(m,key,a,b,y,width,thick,slab,pages):
    m.add(key,key.replace('_',' '),'haunches',
        sweep([(-width/2,0),(width/2,0),(width/2,1),(-width/2,1)],np.linspace(a,b,max(3,int((b-a)/.7))),
        lambda u,v,t:(m.sx(u,y),y+v,(1-t)*(m.surface(m.sx(u,y),y)-slab-thick)+t*(m.surface(m.sx(u,y),y+v)-slab))),pages,
        'Derived contact envelope','Haunch follows modeled grade, not a construction screed or camber table.',nominal_thickness_m=thick)

def end_approaches(m,length,pages,thick=.3,width=None):
    w=width or m.width
    for side in [-1,1]:
        a,b=sorted([side*(m.length/2+.025),side*(m.length/2+.025+length)])
        m.add(f'approach_{side}',f'{"Start" if side<0 else "End"} approach slab','approaches',m.slab(a,b,-w/2,w/2,thick),pages,
            'Simplified skew approach envelope','End transitions, local pavement ledges and nonparallel plan edges are not resolved.',length_m=length,thickness_m=thick)
        m.add(f'joint_{side}',f'{"Start" if side<0 else "End"} deck joint','joints',m.slab(side*m.length/2-.012,side*m.length/2+.012,-w/2,w/2,.08),pages,
            'Schematic interface','24 mm visual joint strip; final opening depends on installation temperature.')

def beam(m,key,name,a,b,y,profile,slab,clear,pages,basis='',note=''):
    d=max(p[1] for p in profile)
    m.add(key,name,'girders',sweep(profile,np.linspace(a,b,max(3,int((b-a)/.6)+1)),
        lambda u,v,z:(m.sx(u,y),y+v,m.surface(m.sx(u,y),y)-slab-clear-d+z)),pages,
        basis or 'Dimensioned nominal section; rolled fillets and fabrication camber omitted',note,depth_m=d,length_m=b-a)

def steel_splice(m,key,u,y,z,depth,pages,width=.50,height=.64,plate=.012,flange_width=.292):
    x=m.sx(u,y);tw=.014
    pieces=[]
    for side in [-1,1]:
        v=side*(tw/2+plate/2)
        pieces.append(box(x-width/2,x+width/2,y+v-plate/2,y+v+plate/2,z-height/2,z+height/2))
    for zz in [z-depth/2-.012,z+depth/2]:
        pieces.append(box(x-.415,x+.415,y-flange_width/2,y+flange_width/2,zz,zz+.012))
    m.add(key,key.replace('_',' '),'steel',concat(pieces),pages,'Source plate envelopes; inner flange bars omitted',web_plate_width_m=width,web_plate_height_m=height)
    bolts=[]
    for dx in np.linspace(-width/2+.05,width/2-.05,6):
        for dz in np.linspace(-height/2+.05,height/2-.05,8):
            bolts.append(bolt([x+dx,y-.025,z+dz],[x+dx,y+.025,z+dz],.011))
    m.add(key+'_bolts',key.replace('_',' ')+' web bolts','fasteners',concat(bolts),pages,
        'Illustrative bolt grid','Bolt diameter follows source M22; placement simplified. Not a fabrication bolt schedule.',bolt_count=48,diameter_m=.022)

def yellow():
    out=BASE/'sr8-yellow';spans=np.array([10.538,18.636,21.946,18.636,10.538]);bs=np.r_[0,np.cumsum(spans)]-sum(spans)/2
    m=Model('sr8-yellow',80.996,11.820,49,lambda x:8.257-.01*np.asarray(x)**2/152.4)
    ys=np.array([-5.029,-3.556,-1.778,0,1.778,3.556,5.029]);slab=.2;clear=.09;d=.840
    m.add('deck','Continuous 1997 deck | 80.996 m x 11.820 m','deck',m.slab(-m.length/2,m.length/2,-m.width/2,m.width/2,slab),[5,6,14],length_m=m.length,width_m=m.width,thickness_m=slab,crossfall_pct=2)
    # New end-span steel and retained middle three-span beams are separate source objects.
    for j,y in enumerate(ys):
        for i,(a,b) in enumerate(zip(bs[:-1],bs[1:])):
            beam(m,f'beam_{i}_{j}',f'Span {chr(65+i)} | W840x193 beam {j+1}',a,b,y,iform(d,.292,.0147,.022),slab,clear,[6,11,12],
                'Drawing depth/width; nominal web and flange thickness approximated','W33x130 / W840x193. Seven lines; new end-span beams, retained middle three spans. Span boundaries are selection divisions, not invented deck joints.')
            haunch(m,f'haunch_{i}_{j}',a,b,y,.292,clear,slab,[6,14])
        for bi,u in enumerate(bs):
            bottom=m.surface(m.sx(u,y),y)-slab-clear-d
            if bi in [2,3]:
                seat=m.bearing(f'Pier_{bi+1}_bearing_{j+1}',u,y,bottom,d,[5,11],pad=(.23,.355,.04),plate=(.3,.45,.12),note='Retained fixed bearing: envelope only; original shoe details are missing.')
            else:seat=m.bearing(f'Bent_{bi+1}_bearing_{j+1}',u,y,bottom,d,[13],pad=(.23,.355,.075),plate=(.26,.405,.06),note='Type B pad/top plate at intermediate bents; Type A end shoe simplified to an envelope.')
        for si,u in enumerate([bs[1]+.234,bs[4]-.234]):steel_splice(m,f'field_splice_{j}_{si}',u,y,m.surface(m.sx(u,y),y)-slab-clear-d/2,d,[12,25])
    # MC460 channels in end spans, retained W460 diaphragms in middle spans.
    for i,(a,b) in enumerate(zip(bs[:-1],bs[1:])):
        rows=[a+3,a+6,b-1] if i in [0,4] else [a+(b-a)*q for q in [.25,.5,.75]]
        for row,u in enumerate(rows):
            for j in range(6):
                y0,y1=ys[j]+.15,ys[j+1]-.15
                x=m.sx(u,(y0+y1)/2);z=m.surface(x,(y0+y1)/2)-slab-clear-.55
                pr=[(0,0),(.13,0),(.13,.014),(.014,.014),(.014,.446),(.13,.446),(.13,.46),(0,.46)]
                m.add(f'diaphragm_{i}_{row}_{j}',f'Span {chr(65+i)} | diaphragm row {row+1}, bay {j+1}','diaphragms',
                    sweep(pr,[y0,y1],lambda y,v,h:(x+v,y,z+h)),[11,12,25],
                    'Channel envelope; row stations simplified','Actual framing has staggered rows and retained W460 diaphragms. This selectable layout preserves transverse connectivity, not a shop layout.',depth_m=.460)
    for bi,u in enumerate(bs):
        yend=5.91 if bi in [0,5] else 5.495
        seat=min(c['seat_m'] for c in m.contacts if c['id'].startswith(('Pier_' if bi in [2,3] else 'Bent_')+str(bi+1)+'_'))
        capbot=seat-(1.30 if bi in [1,4] else .8)
        layer='abutments' if bi in [0,5] else 'piers'
        m.add(f'cap_{bi}',f'Bent {bi+1} | skew cap','abutments' if bi in [0,5] else 'piers',m.transverse(u,.76 if bi not in [2,3] else 1.3,-yend,yend,capbot,seat),[8,10] if bi not in [2,3] else [5],
            'Source cap envelope with derived seat levels' if bi not in [2,3] else 'Approximate retained pier from general elevation',
            'Cap steps are replaced by separate bearing pedestals; field elevations and original central-pier details remain unresolved.')
        for j,y in enumerate(ys):
            bb=m.surface(m.sx(u,y),y)-slab-clear-d
            s=bb-(.16 if bi in [2,3] else .135)
            if s>seat+.001:m.add(f'ped_{bi}_{j}',f'Bent {bi+1} | pedestal {j+1}','bearings',m.transverse(u,.65,y-.27,y+.27,seat,s),[8,10,13], 'Derived contact envelope')
        if bi in [2,3]:
            m.add(f'wall_{bi}',f'Pier {bi+1} | retained solid wall','piers',m.transverse(u,1.15,-4.4,4.4,1.1,capbot),[5], 'Approximate retained wall envelope','Original wall and footing dimensions are not in the 1997 drawing bundle.')
            m.add(f'footing_{bi}',f'Pier {bi+1} | footing envelope','foundations',m.transverse(u,2.4,-4.9,4.9,.3,1.1),[5], 'Approximate; not a foundation design')
        else:
            for j,y in enumerate(np.linspace(-5.2,5.2,9)):
                x=m.sx(u,y);low=4.5 if bi in [0,5] else 3.9
                m.add(f'pile_stub_{bi}_{j}',f'Bent {bi+1} | exposed pile {j+1}','piers',rod([x,y,low],[x,y,capbot],.1775),[8,10],
                    'Source diameter; exposed length approximated','355 mm steel-encased pile; driven portion omitted.',diameter_m=.355)
        if bi in [0,5]:
            for side in [-1,1]:
                y=side*(m.width/2-.15);a,b=sorted([u,u+(-1 if bi==0 else 1)*3.75]);x0=m.sx(a,y);x1=m.sx(b,y)
                m.add(f'wing_{bi}_{side}',f'Bent {bi+1} | wing wall {side}','abutments',box(x0,x1,y-.15,y+.15,capbot,m.surface((x0+x1)/2,y)-.1),[9],
                    'Dimensioned wing length and thickness; end flare simplified',length_m=3.75,thickness_m=.3)
    m.barriers(-m.length/2,m.length/2,[6,16],height=.84,width=.45,top=.24,segments=5)
    end_approaches(m,6.25,[7,18],.3)
    m.cover('Whole five-span structure','modeled_with_simplifications','1997 metric spans and seven steel lines; 49-degree skew and 152.4 m crest profile. The 3 mm sum discrepancy between rounded span callouts and the total framing dimension is retained in the source ledger.',[5,6,11],['deck','girders','haunches'])
    m.cover('Connections and bearings','modeled_with_simplifications','Fourteen field-splice envelopes, 42 bearings and transverse diaphragm envelopes. Some diaphragm stations and old shoes remain approximate.',[11,12,13,25],['steel','fasteners','diaphragms','bearings'])
    m.cover('Retained supports','approximate','End/pile-bent envelopes from the 1997 sheets; central retained piers and unverified seat levels from general elevation only.',[5,8,9,10],['piers','abutments','foundations'])
    m.cover('Rails and approach slabs','modeled_with_simplifications','Concrete rails and both approaches. Wing flare, transition barriers, drain penetrations and steel guardrail terminals are not reconstructed.',[6,16,18],['rails','approaches','joints'])
    m.cover('Missing exterior details','not_modeled','Exact central pier/footing geometry, complete drainage, transition hardware and all retained-steel connection details need further source reconciliation.',[5,12,18],[])
    m.checks=dict(spans_m=spans.tolist(),support_lines=6,girder_lines=7,girder_segments=35,bearings=42,metric_units=True)
    return m.save(out,dict(title='SR 8 over Yellow River | 1997 rehabilitation design',structure_id='8-75-4883B',designation='8916700',spans_m=spans.tolist(),deck_thickness_m=slab,
        source_note='Primary: INDOT B-23076, 1997 rehabilitation and shop drawings (28-page existing-plans bundle). Later 2026 B-43353 overlay is reference only.',
        assumptions=COMMON+['1997 metric dimensions control. W840x193 root fillets, exact diaphragm rows, retained fixed shoes and central pier dimensions are simplified. No 2026 overlay thickness is added.'],
        external_sources=[reference('9549726','1997 rehabilitation and shop drawings'),reference('9683587','2026 overlay, reference only',out/'reference_2026.pdf')]))

def wabash():
    out=BASE/'sr1-wabash';length=(355+11/12)*FT;width=17.322
    m=Model('sr1-wabash',length,width,15,lambda x:np.zeros_like(np.asarray(x))+8.829)
    # 2004 retained main arches: four 21.946 m openings, three 1.295 m piers.
    opening=21.946;pw=1.295;total=opening*4+pw*3;left=-total/2
    starts=[left+i*(opening+pw) for i in range(4)]
    m.add('deck','2004 roadway slab | 200 mm','deck',m.slab(-length/2,length/2,-6.9,6.9,.2),[23,24,29,32],
        'Dimensioned roadway cross-section; end floor limits from 2026 general plan','355 ft 11 in is the floor envelope, not the 91.669 m arch opening/pier chain.',width_m=13.8,thickness_m=.2)
    for side in [-1,1]:
        a,b=sorted([side*6.9,side*width/2])
        m.add(f'walk_{side}',f'{"East" if side>0 else "West"} sidewalk and cantilever','sidewalks',m.slab(-length/2,length/2,a,b,.190,.228),[24,32],
            'Source widths and nominal slab; curb, bracket and end-flare geometry simplified',clear_width_m=1.306,slab_thickness_m=.190)
    for i,a in enumerate(starts):
        b=a+opening;spring0=4.715 if i else 3.191;spring1=4.715 if i<3 else 3.191
        crown=8.05;rise=crown-(spring0+spring1)/2
        def intr(u):
            t=(u-a)/opening;return spring0+(spring1-spring0)*t+4*rise*t*(1-t)
        def thick(u):
            t=(u-a)/opening;return .356+.65*(2*t-1)**2
        xs=np.linspace(a,b,97)
        ring=sweep([(-7.087,0),(7.087,0),(7.087,1),(-7.087,1)],xs,
            lambda u,y,t:(m.sx(u,y),y,intr(u)+t*thick(u)))
        m.add(f'arch_{i}',f'Span {chr(65+i)} | full-width concrete arch barrel','arches',ring,[9,23,24],
            'Dimensioned span/width; arch curve approximated',
            'Quadratic intrados fitted to the general elevation. 356 mm crown ring thickness from the cross-section. Haunch taper and exact original multi-radius setting-out are not reconstructed.',clear_span_m=opening,barrel_width_m=14.174,crown_thickness_m=.356)
        for side in [-1,1]:
            y0,y1=sorted([side*(7.087-.381),side*7.087])
            m.add(f'spandrel_{i}_{side}',f'Span {chr(65+i)} | spandrel wall {side}','walls',
                sweep([(y0,0),(y1,0),(y1,1),(y0,1)],xs,lambda u,y,t:(m.sx(u,y),y,(1-t)*(intr(u)+thick(u))+t*(m.surface(m.sx(u,y),y)-.2))),[9,24],
                'Source wall thickness; arch-dependent envelope approximated',thickness_m=.381)
        m.add(f'fill_{i}',f'Span {chr(65+i)} | concealed fill envelope','fill',
            sweep([(-6.706,0),(6.706,0),(6.706,1),(-6.706,1)],xs,
                lambda u,y,t:(m.sx(u,y),y,(1-t)*(intr(u)+thick(u))+t*(m.surface(m.sx(u,y),y)-.2))),[24],
            'Concealed fill envelope; not material quantities','Hidden by default. No inferred material calibration.')
    supports=[left-pw/2]+[starts[i]-pw/2 for i in [1,2,3]]+[starts[-1]+opening+pw/2]
    for end in [-1,1]:
        a,b=sorted([end*length/2,end*(total/2+pw)])
        for side in [-1,1]:
            y=side*7.087
            m.add(f'endwall_{end}_{side}',f'{"Start" if end<0 else "End"} floor | retaining wall {side}','abutments',
                sweep([(y-.19,0),(y+.19,0),(y+.19,1),(y-.19,1)],[a,b],
                    lambda u,v,t:(m.sx(u,v),v,3.2+t*(m.surface(m.sx(u,v),v)-.2-3.2))),[9,23],
                'Approximate end-floor retaining envelope','Length follows the later overall floor limit; original end flare, fill and ground level require reconciliation.')
    for i,u in enumerate(supports):
        end=i in [0,4];depth=2.438 if end else pw
        ztop=3.191 if end else 4.715
        m.add(f'pier_{i}',f'{"Abutment" if end else "Pier"} {i+1} | retained concrete support','abutments' if end else 'piers',
            m.transverse(u,depth*m.c,-7.087,7.087,.9,ztop+1.02),[8,9,23],
            'Retained support envelope','Support width follows clear-span chain; taper, cutwaters and foundation elevation remain approximate.')
        m.add(f'footing_{i}',f'Pier {i+1} | footing envelope','foundations',m.transverse(u,(depth+1.2)*m.c,-7.65,7.65,0,.9),[8,9], 'Approximate foundation envelope')
        for side in [-1,1]:
            y=side*7.12;x=m.sx(u,y)
            m.add(f'pilaster_{i}_{side}',f'Pier {i+1} | outer spandrel pilaster {side}','walls',box(x-.53,x+.53,y-.24,y+.24,ztop+.5,8.5),[23,30],
                'Pilaster envelope from elevation; projection simplified')
    # Solid architectural parapet, not open steel railing. Raised border strips form shallow recessed panels.
    rail_y=width/2-.2275;railbase=8.829-.02*rail_y+.228
    for side in [-1,1]:
        y=side*rail_y
        for i,(a,b) in enumerate(zip([-length/2]+supports,[*supports,length/2])):
            if b-a<.01:continue
            m.add(f'parapet_{side}_{i}',f'Architectural parapet {side}, section {i+1}','rails',
                m.transverse((a+b)/2,(b-a)*m.c,y-.19,y+.19,railbase,railbase+.915),[35,36,37],
                'Dimensioned height/width; rail end flare omitted',height_m=.915,body_width_m=.38)
            # Build a slab following the same station convention as the deck; remove transverse-box end shear.
            count=max(1,round((b-a)/2.35));orn=[]
            for n in range(count):
                ua=a+n*(b-a)/count+.08;ub=a+(n+1)*(b-a)/count-.08
                x0=m.sx(ua,y);x1=m.sx(ub,y)
                for face in [-1,1]:
                    yy=y+face*.1995
                    orn.extend([box(x0,x1,yy-.0095,yy+.0095,railbase+.13,railbase+.23),
                                box(x0,x1,yy-.0095,yy+.0095,railbase+.64,railbase+.74),
                                box(x0,x0+.1,yy-.0095,yy+.0095,railbase+.23,railbase+.64),
                                box(x1-.1,x1,yy-.0095,yy+.0095,railbase+.23,railbase+.64)])
            m.add(f'panels_{side}_{i}',f'Architectural parapet {side}, recessed-panel borders {i+1}','ornament',concat(orn),[35,36,37],
                'Simplified architectural relief','19 mm relief represented by solid panel borders; exact panel spacing, texture and chamfering omitted.',relief_m=.019)
        for i,u in enumerate(supports):
            x=m.sx(u,y)
            m.add(f'railpost_{side}_{i}',f'Pier {i+1} | parapet pilaster {side}','rails',box(x-.5335,x+.5335,y-.2425,y+.2425,railbase,railbase+.96),[37],width_m=1.067,height_m=.960)
    # Visible external gas line is shown in the 2004 cross-section; routing/diameter are not fully specified.
    y=7.4
    m.add('gas_line','East fascia gas-line envelope','accessories',rod([m.sx(-length/2,y),y,7.92],[m.sx(length/2,y),y,7.92],.10,20),[24,33],
        'Approximate external utility','Presence and side are documented; diameter, joints and hangers are not verified.',assumed_diameter_m=.20)
    m.cover('Four concrete arches','modeled_with_simplifications','Four whole arch barrels, spandrel walls and hidden fill envelopes. Exact original multi-radius curve and spring haunch thickness remain unresolved.',[9,23,24],['arches','walls','fill'])
    m.cover('2004 deck and sidewalks','modeled_with_simplifications','13.8 m roadway, 17.322 m overall width, 200 mm slab and both sidewalks. End floor limits follow the later general plan; plan flare and localized curb brackets are simplified.',[23,24,32],['deck','sidewalks'])
    m.cover('Architectural parapets','modeled_with_simplifications','Solid 915 mm parapets, 960 mm pilasters and shallow relief. Panel spacing and texture are representative. Separate pedestrian-bridge sheets 40-50 were excluded.',[35,36,37],['rails','ornament'])
    m.cover('Retained substructure','approximate','Three piers and two abutment envelopes. No foundation adequacy or current condition inferred.',[8,9,23],['piers','abutments','foundations'])
    m.cover('Remaining exterior features','not_modeled','Exact arch setting-out, cutwaters, decorative lighting supplied by the city, gauge-well hardware, drainage outlets, rail end flare and approach details remain incomplete.',[23,24,37],[])
    m.checks=dict(arch_openings=4,clear_span_m=opening,pier_width_chain_m=pw,arch_chain_length_m=total,deck_floor_envelope_m=length,roadway_width_m=13.8,overall_width_m=17.322,pedestrian_bridge_excluded=True)
    return m.save(out,dict(title='SR 1 over Wabash River | 2004 roadway reconstruction',structure_id='1-90-230B',designation='9406690',spans_m=[opening]*4,
        source_note='Primary: 50-page existing-plans bundle, original 1933 arch details plus 2004 B-25747 roadway reconstruction. Pages 40-50 concern a separate pedestrian bridge and are not used for this model. 2026 general plan cross-checks the overall floor envelope.',
        assumptions=COMMON+['Arch intrados and variable ring thickness are approximate, not original setting-out. 21.946 m clear arch openings differ from pier-center distances and overall floor length.','The 2026 overlay and repair operations are not modeled. The 2004 decorative lighting details supplied by the City of Bluffton are not available in this package.'],
        external_sources=[reference('9548291','Historical main-arch and 2004 deck plans'),reference('9683627','2026 rehabilitation general plan, reference',out/'reference_2026.pdf')]))

def tanners():
    out=BASE/'us50-tanners-eb';spans=np.array([82+2.125/12,105+7.5/12,113.75,105+7.5/12,81+11.75/12])*FT
    bs=np.r_[0,np.cumsum(spans)]-sum(spans)/2;length=(492+.125/12)*FT;width=(72+2/12)*FT
    pvi=(38940.58-(38667.49+sum(spans)/FT/2))*FT
    m=Model('us50-tanners-eb',length,width,20,lambda x:12.47-.0001*(np.asarray(x)-pvi)-.0062*(np.asarray(x)-pvi)**2/(2*430*FT),crown=-(4+7/12)*FT)
    m.colors['girders']='#b9b8ad'
    # 4 ft 1 in left overhang, 3 ft 1 in right overhang: beam lines are NOT centered on the deck.
    ys=-width/2+(4+1/12)*FT+np.arange(7)*(10+10/12)*FT
    slab=8*IN;clear=.10;d=66*IN
    pr=np.array([[-12.5,0],[12.5,0],[12.5,8],[3.5,17],[3.5,54],[27,58],[30,58],[30,66],[-30,66],[-30,58],[-27,58],[-3.5,54],[-3.5,17],[-12.5,8]])*IN
    m.add('deck','Continuous five-span deck | US 50 eastbound','deck',m.slab(-length/2,length/2,-width/2,width/2,slab),[107,108,109,139],
        'Dimensioned envelope; curve fitted to grade data',length_m=length,width_m=width,thickness_m=slab,crown_offset_m=m.crown)
    for i,(a,b) in enumerate(zip(bs[:-1],bs[1:])):
        for j,y in enumerate(ys):
            ga=a+(.01 if i==0 else .15);gb=b-(.01 if i==4 else .15)
            beam(m,f'bulbt_{i}_{j}',f'Span {chr(65+i)} | Bulb-T beam {j+1}',ga,gb,y,pr,slab,clear,[129,130,131,133],
                'Dimensioned 66 in Bulb-T envelope; local chamfers omitted','Top flange 60 in, bottom bulb 25 in, web 7 in. Span selections retain actual support separation. Camber and threaded inserts omitted.')
            haunch(m,f'haunch_{i}_{j}',ga,gb,y,60*IN,clear,slab,[109,139])
            for end,u in [('start',a+(.0 if i==0 else FT)),('end',b-(.0 if i==4 else FT))]:
                bottom=m.surface(m.sx(u,y),y)-slab-clear-d
                m.bearing(f'Span_{chr(65+i)}_beam_{j+1}_{end}_bearing',u,y,bottom,d,[129,131],pad=(22*IN,23.5*IN,2*IN),plate=(22*IN,23.5*IN,.5*IN),
                    note='Paired interior bearing rows at +/-1 ft from bent center. Pad thickness is a simplified envelope; end-bearing assembly differs from interior Type II.')
        # One staggered midspan X frame per bay, per erection plan; section sizes simplified.
        for j in range(6):
            y0,y1=ys[j]+.13,ys[j+1]-.13;u=(a+b)/2;x=m.sx(u,(y0+y1)/2)
            z0=m.surface(x,(y0+y1)/2)-slab-clear-d+.3;z1=z0+1.0
            bars=[rectangular_bar([x,y0,z0],[x,y1,z1],.10,.012),rectangular_bar([x,y0,z1],[x,y1,z0],.10,.012),
                  rectangular_bar([x,y0,z0],[x,y1,z0],.10,.012),rectangular_bar([x,y0,z1],[x,y1,z1],.10,.012)]
            m.add(f'xframe_{i}_{j}',f'Span {chr(65+i)} | X frame bay {j+1}','bracing',concat(bars),[129,132],
                'X-frame topology from drawings; angle section and stagger simplified')
    # Four-column bents: original three columns plus widening column. Interior bents 3/4 have a tie beam.
    for bi,u in enumerate(bs):
        end=bi in [0,5]
        rows=[u] if end else [u-FT,u+FT]
        seat=min(m.surface(m.sx(ur,y),y)-slab-clear-d-2.5*IN for ur in rows for y in ys)
        capbottom=seat-(1.4 if not end else 1.1)
        yy=sorted(ys);widthcap=74.25*FT if not end else 75*FT
        y0,y1=-widthcap*m.c/2,widthcap*m.c/2
        m.add(f'cap_{bi}',f'Bent {bi+1} | concrete cap','abutments' if end else 'piers',m.transverse(u,(4.5 if not end else 3.75)*FT,y0,y1,capbottom,seat),[113,117] if end else [121,125],
            'Source cap envelope; step levels fitted to modeled bearing bottoms',cap_length_along_skew_m=widthcap)
        for j,y in enumerate(ys):
            rows=[u] if end else [u-FT,u+FT]
            topmin=min(m.surface(m.sx(ur,y),y)-slab-clear-d-2.5*IN for ur in rows)
            # Lower the cap locally only via a pedestal; no gap under any bearing.
            for ri,ur in enumerate(rows):
                ss=m.surface(m.sx(ur,y),y)-slab-clear-d-2.5*IN
                if ss>seat:m.add(f'ped_{bi}_{j}_{ri}',f'Bent {bi+1} | bearing pedestal {j+1}-{ri+1}','bearings',m.transverse(ur,.65,y-.34,y+.34,seat,ss),[121,125,129], 'Derived contact envelope')
        footbottom=[4.5,.0762,-6.3246,-6.3246,.0762,4.3434][bi]
        foottop=footbottom+(1.6 if end else 2.13)
        colwidth=(3 if end else 4)*FT
        colys=np.array([-25,0,25,36.5])*FT*m.c
        # Align source column chain within the cap; datum is the original center column.
        colys-=np.mean([colys[0],colys[-1]])
        for j,y in enumerate(colys):
            m.add(f'column_{bi}_{j}',f'Bent {bi+1} | column {j+1}','piers',m.transverse(u,colwidth,y-colwidth*m.c/2,y+colwidth*m.c/2,foottop,capbottom),[117] if end else [121,125],
                'Dimensioned nominal columns; retained/widened positions approximated','Original three-column bent plus widening column. Cap and foundation interfaces are reconstructed envelopes.',section_width_m=colwidth)
        if bi in [2,3]:
            z=(457.42-450)*FT
            m.add(f'tie_{bi}',f'Bent {bi+1} | intermediate tie beam','piers',m.transverse(u,4.5*FT,min(colys),max(colys),z,z+2.25*FT),[125],
                'Source tie-beam elevation; end haunches simplified')
        m.add(f'footing_{bi}',f'Bent {bi+1} | combined footing envelope','foundations',m.transverse(u,(13 if bi in [2,3] else 10.5)*FT,min(colys)-1.5,max(colys)+1.5,footbottom,foottop),[117,121,125],
            'Source foundation level; retained/widened boundary simplified','No deep piles or construction seals modeled.')
    # Separate highway barrier and sidewalk rail, as drawn.
    for side in [-1,1]:
        edge=side*width/2
        if side<0:
            prail=[(0,0),(1.5*FT,0),(1.5*FT,.18),(10*IN,3.75*FT),(0,3.75*FT)]
            m.add('ft_rail','Highway-side concrete Type FT barrier','rails',sweep(prail,np.linspace(-length/2,length/2,160),
                lambda u,v,z:(m.sx(u,edge+v),edge+v,m.surface(m.sx(u,edge+v),edge+v)+z)),[109,139],height_m=3.75*FT)
        else:
            walkstart=(21+5/12)*FT;walkend=width/2-FT
            m.add('sidewalk','Wide sidewalk | 13 ft 8 in','sidewalks',m.slab(-length/2,length/2,walkstart,walkend,.2032,.2),[109,139],
                'Source width; local southeast 5 percent ramp not modeled',width_m=walkend-walkstart)
            m.add('ps1_base','Sidewalk-side PS-1 concrete parapet','rails',m.slab(-length/2,length/2,walkend,width/2,.61,.81),[139],
                'PS-1 base envelope',height_m=.61)
            posts=[];yy=width/2-.13
            for u in np.linspace(-length/2,length/2,int(length/1.524)+1):
                xx=m.sx(u,yy);zz=m.surface(xx,yy)+.81
                posts.append(box(xx-.045,xx+.045,yy-.045,yy+.045,zz,zz+.4572))
            m.add('ps1_posts','PS-1 upper rail posts','rails',concat(posts),[139,140], 'Simplified metal post envelopes; spacing approximated')
            for j,h in enumerate([.94,1.22]):
                m.add(f'ps1_beam_{j}',f'PS-1 horizontal rail {j+1}','rails',m.slab(-length/2,length/2,yy-.045,yy+.045,.075,h),[139], 'Simplified horizontal rail envelope')
    end_approaches(m,20.5*FT,[108,144,146],FT)
    m.cover('Five-span eastbound bridge','modeled_with_simplifications','35 individual 66 in Bulb-T beams, asymmetric 72 ft 2 in deck, 13 ft 8 in sidewalk and 20-degree skew. The adjacent westbound bridge is excluded.',[107,108,109,129,130,131],['deck','girders','haunches','sidewalks'])
    m.cover('Bents and bearings','modeled_with_simplifications','Six bents, four-column retained/widened envelopes, deep central bents with tie beams and paired interior bearing rows. Local seats, haunches and retained/widened seams are simplified.',[117,121,125,129],['piers','abutments','foundations','bearings'])
    m.cover('X frames and rails','modeled_with_simplifications','X frames, highway FT concrete barrier and distinct sidewalk PS-1 rail. Frame sections and PS-1 post details are approximate.',[132,139,140],['bracing','rails'])
    m.cover('Approaches','modeled_with_simplifications','Both 20 ft 6 in approach envelopes; transitions and the southeast sidewalk ramp remain incomplete.',[108,144,146],['approaches','joints'])
    m.cover('Missing exterior details','not_modeled','End-bent wings, complete support diaphragms, drainage, lighting, local sidewalk ramps, concrete surface recesses and shop camber remain unresolved.',[113,117,139,140],[])
    m.checks=dict(spans_m=spans.tolist(),support_lines=6,girder_lines=7,girder_segments=35,bearings=70,deck_width_m=width,beam_spacing_m=(10+10/12)*FT,westbound_excluded=True)
    return m.save(out,dict(title='US 50 EB over Tanners Creek | 2014 reconstruction design',structure_id='50-15-0210B',designation='0400285',spans_m=spans.tolist(),
        source_note='Primary: 149-page existing-plans bundle. This model uses the 2014 B-29709 Bulb-T reconstruction sheets (PDF pp.103-149), not the earlier concrete-arch/steel-era sheets. 2026 overlay and revision are references only.',
        assumptions=COMMON+['Seven beam lines have asymmetric overhangs (4 ft 1 in / 3 ft 1 in). The grade crown is offset 4 ft 7 in from the structure centerline.','No 2026 thin overlay or field patching is represented. Vertical geometry is a fitted grade envelope, not fabrication camber.'],
        external_sources=[reference('9548069','Historical bundle: 2014 reconstruction subset'),reference('9683599','2026 overlay reference',out/'reference_2026.pdf'),reference('9712271','2026 revised sheets reference',out/'reference_2026_revision.pdf')]))

def minnich():
    out=BASE/'minnich-road';spans=np.array([65+5/12,145,145,55+5/12])*FT
    bs=np.r_[0,np.cumsum(spans)]-sum(spans)/2;length=(414+11.5/12)*FT;width=63*FT
    m=Model('minnich-road',length,width,56+17/60+55/3600,lambda x:10.45-.00005*np.asarray(x)-.0625*np.asarray(x)**2/(2*940*FT),crossfall=.0156)
    ys=np.array([-29.375,-20.375,-11.375,-2.375,2.375,11.375,20.375,29.375])*FT
    slab=8*IN;clear=.08
    def depth(u):
        if u<bs[1]:return np.interp(u,[bs[0],bs[0]+48.4167*FT,bs[0]+53.4167*FT,bs[1]],[36*IN,36*IN,68*IN,68*IN])
        if u>bs[3]:return np.interp(u,[bs[3],bs[3]+12*FT,bs[3]+17*FT,bs[4]],[68*IN,68*IN,34.25*IN,34.25*IN])
        return 68*IN
    m.add('deck','Proposed continuous deck | former longitudinal joint eliminated','deck',m.slab(-length/2,length/2,-width/2,width/2,slab),[19,20,35,38],
        '2026 proposed deck envelope','Two separately inventoried directional structures share the proposed continuous slab. No invented central deck gap.',length_m=length,width_m=width,thickness_m=slab)
    for j,y in enumerate(ys):
        for i,(a,b) in enumerate(zip(bs[:-1],bs[1:])):
            xs=np.unique(np.r_[np.linspace(a,b,max(3,int((b-a)/.5))),[t for t in [bs[0]+48.4167*FT,bs[0]+53.4167*FT,bs[3]+12*FT,bs[3]+17*FT] if a<t<b]])
            # normalized profile preserves exact top/bottom flange thickness as web depth varies.
            pr=iform(1,.4572,.0127,.0254)
            def point(u,v,z):
                dd=depth(u)
                zz=z if z<=.0254 else dd-(1-z) if z>=.9746 else .0254+(z-.0254)*(dd-.0508)/.9492
                return (m.sx(u,y),y+v,m.surface(m.sx(u,y),y)-slab-clear-dd+zz)
            m.add(f'plate_{i}_{j}',f'Span {chr(65+i)} | plate girder {j+1}','girders',sweep(pr,xs,point),[25,26,27,28,30,32],
                'Source main dimensions; retained flange schedule simplified',
                'New end spans taper from about 34/36 in total depth to 68 in. Main spans retain 66 in webs. Detailed retained flange changes, exact Span D taper, upper-flange kink and camber are unresolved.',web_thickness_m=.0127,new_flange_width_m=.4572,new_flange_thickness_m=.0254)
            haunch(m,f'haunch_{i}_{j}',a,b,y,.4572,clear,slab,[20,38])
        for bi,u in enumerate(bs):
            bottom=m.surface(m.sx(u,y),y)-slab-clear-depth(u)
            if bi in [0,4]:
                m.bearing(f'Bent_{bi+1}_bearing_{j+1}',u,y,bottom,depth(u),[34],pad=(FT,16*IN,3.625*IN),plate=(13*IN,(22 if bi==0 else 24)*IN,3*IN if bi==0 else 2.25*IN),
                    note='S5-B exterior pad and load-plate stack. Source-specific shim elevations and side retainers remain to be reconciled.')
            else:m.bearing(f'Bent_{bi+1}_bearing_{j+1}',u,y,bottom,depth(u),[19],pad=(.4,.5,.08),plate=(.5,.65,.12),note='Retained intermediate bearing envelope only; original details unavailable.')
        for si,u in enumerate([bs[1]-9*FT,bs[3]+9*FT]):steel_splice(m,f'splice_{j}_{si}',u,y,m.surface(m.sx(u,y),y)-slab-clear-depth(u)/2,depth(u),[29],width=20.25*IN,height=60.75*IN,plate=.375*IN,flange_width=18*IN)
        # Source stiffener topology sampled at support/diaphragm stations; no hidden shear studs.
        for q,u in enumerate(np.r_[bs,np.linspace(bs[1]+4,bs[3]-4,15)]):
            x=m.sx(u,y);top=m.surface(x,y)-slab-clear;dd=depth(u)
            pieces=[box(x-.00635,x+.00635,y+side*.108-.1,y+side*.108+.1,top-dd+.0254,top-.0254) for side in [-1,1]]
            m.add(f'stiffener_{j}_{q}',f'Girder {j+1} | transverse stiffener pair {q+1}','steel',concat(pieces),[25,27,28],
                'Representative stiffener stations; plate envelopes','Exact existing middle-span stiffener schedule is not available.',thickness_m=.0127)
    for i,(a,b) in enumerate(zip(bs[:-1],bs[1:])):
        for row,u in enumerate(np.linspace(a+.8,b-.8,max(2,int((b-a)/7)))):
            for j in [0,1,2,4,5,6]:
                y0,y1=ys[j]+.24,ys[j+1]-.24;x=m.sx(u,(y0+y1)/2);dd=depth(u)
                z1=m.surface(x,(y0+y1)/2)-slab-clear-.12;z0=z1-dd+.24
                bars=[rectangular_bar([x,y0,z0],[x,y1,z1],.10,.012),rectangular_bar([x,y0,z1],[x,y1,z0],.10,.012)]
                m.add(f'frame_{i}_{row}_{j}',f'Span {chr(65+i)} | cross frame row {row+1}, bay {j+1}','bracing',concat(bars),[25,26,31,33],
                    'Representative X-frame topology','End-span K frames, channel diaphragms, skew stagger and old middle-span connections are simplified. No frame is invented between the two former directional girder banks.')
    for bi,u in enumerate(bs):
        contacts=[c for c in m.contacts if c['id'].startswith(f'Bent_{bi+1}_')];seat=min(c['seat_m'] for c in contacts);capbot=seat-.95
        for bank,(y0,y1) in enumerate([(-width/2,-.01),(.01,width/2)]):
            m.add(f'cap_{bi}_{bank}',f'Bent {bi+1} | directional cap {bank+1}','abutments' if bi in [0,4] else 'piers',m.transverse(u,.84,y0,y1,capbot,seat),[23,24] if bi in [0,4] else [19],
                'Retained cap envelope; intermediate dimensions estimated','End-bent profile is simplified. Original intermediate-pier and foundation plans were not supplied.')
            if bi not in [0,4]:
                for j,y in enumerate(np.linspace(y0+.9,y1-.9,3)):
                    x=m.sx(u,y)
                    m.add(f'column_{bi}_{bank}_{j}',f'Bent {bi+1} | retained column bank {bank+1}-{j+1}','piers',rod([x,y,1.2],[x,y,capbot],.45,24),[19],
                        'Approximate support envelope','Column count and 0.9 m diameter are visual assumptions pending original substructure plans; not verified design geometry.',assumed_diameter_m=.9)
            else:
                # Mudwall kept separate from the new superstructure, without intersecting bearings.
                face=u+(-1 if bi==0 else 1)*.8
                m.add(f'mudwall_{bi}_{bank}',f'Bent {bi+1} | mudwall {bank+1}','abutments',m.transverse(face,.25,y0,y1,capbot,m.surface(m.sx(face,(y0+y1)/2),(y0+y1)/2)-slab),[23,24],
                    'Source mudwall arrangement; local ledges simplified')
        for j,c in enumerate(contacts):
            y=ys[j]
            if c['seat_m']>seat+.001:m.add(f'ped_{bi}_{j}',f'Bent {bi+1} | pedestal {j+1}','bearings',m.transverse(u,.75,y-.38,y+.38,seat,c['seat_m']),[23,34], 'Derived contact envelope')
    m.barriers(-length/2,length/2,[47,48,49],height=33*IN,width=16*IN,top=9*IN,segments=4)
    # Heavily skewed RCBA has a stepped outer edge, not a rectangular full-width extension.
    for side in [-1,1]:
        u=side*(length/2+.03)
        for lane,(y0,y1) in enumerate([(-30*FT,-8*FT),(-8*FT,8*FT),(8*FT,30*FT)]):
            inner=lambda y:m.sx(u,y)
            outer=side*max(side*inner(y0),side*inner(y1))+side*20.5*FT
            profile=[(y0,0),(y1,0),(y1,1),(y0,1)]
            mesh=sweep(profile,np.linspace(0,1,30),lambda t,y,h:((1-t)*inner(y)+t*outer,y,m.surface((1-t)*inner(y)+t*outer,y)-(1-h)*FT))
            m.add(f'rcba_{side}_{lane}',f'{"North" if side<0 else "South"} approach | stepped panel {lane+1}','approaches',mesh,[56,57,59,60],
                'Source stepped topology; outer station positions approximated','12 in approach slab split into 22/16/22 ft bands. Precise edge offsets, corner extensions and drainage troughs require further reconciliation.',thickness_m=FT)
    m.cover('Whole four-span crossing','modeled_with_simplifications','Both directional girder banks, eight lines, 63 ft overall width and 56 deg 17 min 55 sec skew. Proposed deck removes the former center joint.',[19,20,25,26],['deck','girders','haunches'])
    m.cover('Variable-depth steel and connections','modeled_with_simplifications','End-span depth transitions, sixteen field-splice envelopes, stiffeners and representative bracing. Exact retained flange schedule, upper-flange kink, camber and K-frame detail remain incomplete.',[25,26,27,28,29,30,31,32,33],['steel','fasteners','bracing'])
    m.cover('Bearings','modeled_with_simplifications','Forty bearing envelopes; S5-B end pads represented. Retained intermediate shoes and exact source shim-seat reconciliation are incomplete.',[19,34],['bearings'])
    m.cover('Existing intermediate piers','approximate','Support envelopes only: original substructure plans were absent from the public package. Column arrangement and dimensions must not be used for analysis or quantity takeoff.',[19],['piers','abutments'])
    m.cover('Rails and stepped approaches','modeled_with_simplifications','FC rails and six RCBA panels. Detailed wingwall, TFC/guardrail transitions, stepped approach edge offsets and drainage are unfinished.',[47,56,57,59,60],['rails','approaches'])
    m.cover('Foundations and missing exterior details','not_modeled','Unknown foundations, road/site surfaces, drainage troughs, guardrail terminals, all connection holes and full retained substructure details.',[19,23,24],[])
    m.checks=dict(spans_m=spans.tolist(),support_lines=5,girder_lines=8,girder_segments=32,bearings=40,continuous_deck_across_former_joint=True,directional_nbi_records=2)
    return m.save(out,dict(title='Minnich Road NB / SB over I-469 | proposed 2026 rehabilitation',structure_id='I469-18-07027 ANB / ASB',designation='2200710 / 2200711',spans_m=spans.tolist(),
        source_note='INDOT B-44533, 62-sheet July 31 2026 proposed rehabilitation, November 2026 letting. This is a proposed design, not a completed construction or verified present-day model.',
        assumptions=COMMON+['Eight girder lines represent two NBI structures in one crossing; the new continuous deck intentionally eliminates the longitudinal joint (sheet 20).','Intermediate columns and caps are provisional envelopes. Original substructure plans are unavailable. No foundations were invented.','Middle-span flange changes and exact end-span taper/upper kink remain simplified; this model is not suitable for FEM without a separate source reconciliation.'],
        external_sources=[reference('9721535','2026 proposed rehabilitation drawings (62 sheets)')]))

if __name__=='__main__':
    import sys
    targets=dict(yellow=yellow,wabash=wabash,tanners=tanners,minnich=minnich)
    for name in sys.argv[1:] or targets:
        targets[name]()

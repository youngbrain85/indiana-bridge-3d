"""SR 44 / Mud Creek: whole-bridge exterior reconstruction, 2018 design state.

Run from any directory with numpy, trimesh, shapely and mapbox-earcut installed.
Primary evidence is data/bridges/sr44-mud/drawings.pdf (INDOT B-38321).
Coordinates: metres; X increasing station, Y transverse toward beam 1, Z up.
The model is a geometric reconstruction, not an FE mesh or an as-built survey.
"""
from pathlib import Path
import hashlib
import json
import math
import numpy as np
import trimesh as tm
from shapely.geometry import Polygon, LineString

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/bridges/sr44-mud'
FT, IN = .3048, .0254
K = math.tan(math.radians(15))
C, S = math.cos(math.radians(15)), math.sin(math.radians(15))
HALF = (151 + 1/12)/2*FT
BEARINGS = np.array([-74.75, -25, 25, 74.75])*FT
YS = np.array([21, 14, 7, 0, -7, -14, -21])*FT
D, BF, TW, TF = np.array([26.92, 9.990, .490, .745])*IN
COLORS = {'deck':'#d6d6cf','girders':'#89634e','haunches':'#b9b8aa',
 'diaphragms':'#99795f','steel':'#a17e62','fasteners':'#8d969b',
 'bearings':'#3b4850','piers':'#b6b0a1','abutments':'#c0b9aa',
 'foundations':'#8d999b','rails':'#d3cbb8','approaches':'#bec5c1',
 'joints':'#455157','accessories':'#b4c7cb'}
LAYERS = {'deck':'Crowned concrete deck','girders':'Continuous W27x94 steel beams',
 'haunches':'Deck haunches','diaphragms':'C15x33.9 diaphragms',
 'steel':'Splice plates and bearing stiffeners','fasteners':'Connection bolts',
 'bearings':'Elastomeric bearing assemblies','piers':'Retained wall piers',
 'abutments':'Semi-integral end bents and wings','foundations':'Retained footings and design piles',
 'rails':'FC barriers and TFC transitions','approaches':'Approach slabs and extensions',
 'joints':'Isolation interfaces','accessories':'Barrier delineators'}
parts, meshes, contacts = [], {}, []

def el(feet): return (np.asarray(feet)-885)*FT
def sx(u,y): return u+K*y
def grade(x):
    # PVI sta.617+95, elev.908.82; 200 ft curve; +0.82% / -0.29% (sheet 9).
    t=np.asarray(x)/FT+100
    inside=908.00+.0082*t+(-.0029-.0082)*t*t/400
    return el(np.where(t<0,908.00+.0082*t,np.where(t>200,908.53-.0029*(t-200),inside)))
def surface(x,y): return grade(x)-.02*np.abs(y)
def box(x0,x1,y0,y1,z0,z1):
    assert x1>x0 and y1>y0 and z1>z0,(x0,x1,y0,y1,z0,z1)
    m=tm.creation.box([x1-x0,y1-y0,z1-z0]);m.apply_translation([(x0+x1)/2,(y0+y1)/2,(z0+z1)/2]);return m
def sweep(profile, xs, fn):
    poly=Polygon(profile)
    assert poly.is_valid and poly.area>0
    vv,ff=tm.creation.triangulate_polygon(poly,engine='earcut')
    if np.allclose(vv[-1],vv[0]): ff=np.where(ff==len(vv)-1,0,ff);vv=vv[:-1]
    n=len(vv);v=[fn(float(x),float(a),float(b)) for x in xs for a,b in vv];f=[]
    for k in range(len(xs)-1):
        for j in range(n):
            a=k*n+j;b=k*n+(j+1)%n;f.extend([(a,b,b+n),(a,b+n,a+n)])
    f.extend(tuple(q[::-1]) for q in ff);f.extend(tuple(q+(len(xs)-1)*n) for q in ff)
    m=tm.Trimesh(v,f,process=True);m.fix_normals(multibody=True);return m
def rod(a,b,r,sections=12):
    a,b=np.asarray(a),np.asarray(b);v=b-a
    m=tm.creation.cylinder(r,np.linalg.norm(v),sections=sections)
    m.apply_transform(tm.geometry.align_vectors([0,0,1],v));m.apply_translation((a+b)/2);return m
def concat(ms): return tm.util.concatenate(ms)
def rot(m,u):
    t=np.eye(4);t[:2,:2]=[[C,S],[-S,C]];t[0,3]=u;m.apply_transform(t);return m
def add(key,name,layer,m,pages,basis='Dimensioned',note='',**dims):
    assert key not in meshes
    m.remove_unreferenced_vertices();m.fix_normals(multibody=True)
    assert m.is_watertight and m.volume>0 and np.isfinite(m.vertices).all(),key
    color=COLORS[layer];m.visual.vertex_colors=[int(color[j:j+2],16) for j in (1,3,5)]+[255]
    meta=dict(id=key,name=name,layer=layer,color=color,pdf_pages=pages,basis=basis,note=note,dimensions=dims)
    m.metadata.update(meta);meshes[key]=m
    parts.append(dict(**meta,bounds_m=np.round(m.bounds,6).tolist(),volume_m3=round(float(m.volume),9)))
    return m
def slab(u0,u1,y0,y1,thick):
    yy=sorted(set([y0,y1]+([0] if y0<0<y1 else [])))
    profile=[(y,-thick) for y in yy]+[(y,0) for y in reversed(yy)]
    return sweep(profile,np.linspace(u0,u1,max(3,int((u1-u0)/.35))),lambda u,y,z:(sx(u,y),y,surface(sx(u,y),y)+z))
def iform(d,b,tw,tf):
    return [(-b/2,0),(b/2,0),(b/2,tf),(tw/2,tf),(tw/2,d-tf),(b/2,d-tf),
     (b/2,d),(-b/2,d),(-b/2,d-tf),(-tw/2,d-tf),(-tw/2,tf),(-b/2,tf)]
def hexbolt(a,b,r):
    # Combined selectable fastener: shank, hex head and nut. Threads omitted.
    a,b=np.asarray(a),np.asarray(b);v=(b-a)/np.linalg.norm(b-a)
    return concat([rod(a,b,r),rod(a-v*.012,a,r*1.55,6),rod(b,b+v*.017,r*1.55,6)])

# One continuous deck with no invented expansion gaps over the piers.
add('deck','Continuous deck | 151 ft 1 in x 46 ft 6 in','deck',slab(-HALF,HALF,-23.25*FT,23.25*FT,8*IN),[9,10,11,27,29],
    'Dimensioned final-grade envelope','Screed-table construction deflection allowances are not the final road profile.',
    length_ft=151+1/12,width_ft=46.5,thickness_in=8,crossfall_pct=2,skew_deg=15)

# Source seat elevations use five retained steps, not one step per new beam.
SEAT = np.array([[904.36,904.36,904.51,904.65,904.46,904.27,904.27],
 [904.61,904.61,904.79,904.97,904.82,904.67,904.67],
 [904.79,904.79,904.96,905.13,904.97,904.81,904.81],
 [904.79,904.79,904.96,905.13,904.97,904.81,904.81]])
SHIM = np.array([[.75,2.375,2.125,2,2.375,2.75,1],
 [.125,1.75,1.5,1.375,1.625,2,.25],
 [0,1.5,1.25,1,1.25,1.625,0],
 [0,1.5,1.25,1,1.25,1.5,0]])*IN
PAD, LOAD = 3.03125*IN, 1.75*IN
SUPPORT_TOP = el(SEAT)+SHIM+PAD+LOAD+D
# Old cap elevations are approximate. At the south end b4 is shown from the opposite face.
# Cap/bearing/beam remain attached; local clearances are checked below before export.
def top(j,u):
    g=surface(sx(np.asarray(u),YS[j]),YS[j])-8*IN
    correction=SUPPORT_TOP[:,j]-(surface(sx(BEARINGS,YS[j]),YS[j])-8*IN)
    return g+np.interp(u,BEARINGS,correction)

for j,y in enumerate(YS):
    for seg,(a,b) in enumerate([(-75.25,-11.75),(-11.75,11.75),(11.75,75.25)],1):
        gap=.125*IN
        ua=a*FT+(gap if seg>1 else 0);ub=b*FT-(gap if seg<3 else 0)
        m=sweep(iform(D,BF,TW,TF),np.linspace(ua,ub,90),lambda u,v,z:(sx(u,y)+0*v,y+v,top(j,u)-D+z))
        add(f'beam_{j+1}_segment_{seg}',f'Beam {j+1} | continuous segment {seg}','girders',m,[17,18,19,22],
            'Dimensioned section; interpolated loaded geometry',
            'W27x94 nominal dimensions from Nucor-Yamato catalog p.21. Root fillets omitted. '
            'Support elevations and shim stacks anchor a smooth grade-based geometry; unloaded shop camber is not reproduced.',
            section='W27x94',depth_in=26.92,flange_width_in=9.990,web_in=.490,flange_in=.745,material='ASTM A709 Grade 50W',beam_line=j+1)
    # Haunch follows the actual beam top and crowned deck soffit; trim at diaphragms later.
    p=[(-BF/2,0),(BF/2,0),(BF/2,1),(-BF/2,1)]
    add(f'haunch_{j+1}',f'Beam {j+1} concrete haunch','haunches',sweep(p,np.linspace(-HALF,HALF,180),
        lambda u,v,t:(sx(u,y),y+v,top(j,u) if t==0 else surface(sx(u,y),y+v)-8*IN)),[27],
        'Derived from adjacent deck and beam surfaces','Haunch thickness varies with retained bearing-seat levels; field verification is required.')

    # Two field splices, 63 ft from the end bearing lines; 104 bolts per splice.
    for sp,u in enumerate([-11.75*FT,11.75*FT],1):
        x=sx(u,y);z=top(j,u);b=z-D
        plen=(3*12+2.375)*IN;webL=26*IN;webH=22*IN
        plates=[box(x-plen/2,x+plen/2,y-5*IN,y+5*IN,z,z+.5*IN),
                box(x-plen/2,x+plen/2,y-5*IN,y+5*IN,b-.5*IN,b)]
        for s in [-1,1]:
            aa,bb=sorted([y+s*TW/2,y+s*(TW/2+.4375*IN)])
            plates.append(box(x-webL/2,x+webL/2,aa,bb,b+(D-webH)/2,b+(D+webH)/2))
            ya,yb=sorted([y+s*(1.125*IN),y+s*(5*IN)])
            for z0,z1 in [(z-TF-.625*IN,z-TF),(b+TF,b+TF+.625*IN)]:
                plates.append(box(x-plen/2,x+plen/2,ya,yb,z0,z1))
        add(f'splice_{j+1}_{sp}',f'Beam {j+1} field splice {sp} | eight plates','steel',concat(plates),[18,19],
            plate_count=8,web_plate_in=[26,22,.4375],flange_outer_plate_in=[38.375,10,.5],field_gap_in=.25)
        bolts=[]
        for side in [-1,1]:
            for dx in [2,5,8,11,14,17]:
                for dy in [-2.8125,2.8125]:
                    for zz in [b,z-TF-.625*IN]:
                        lo,hi=(b-.5*IN,b+TF+.625*IN) if zz==b else (z-TF-.625*IN,z+.5*IN)
                        bolts.append(hexbolt([x+side*dx*IN,y+dy*IN,lo],[x+side*dx*IN,y+dy*IN,hi],.4375*IN))
            for dx in [2,5,8,11]:
                for dz in np.arange(-9,10,3):
                    bolts.append(hexbolt([x+side*dx*IN,y-TW/2-.4375*IN,b+D/2+dz*IN],
                                         [x+side*dx*IN,y+TW/2+.4375*IN,b+D/2+dz*IN],.4375*IN))
        assert len(bolts)==104
        add(f'splice_bolts_{j+1}_{sp}',f'Beam {j+1} field splice {sp} | 104 bolts','fasteners',concat(bolts),[19],
            'Dimensioned bolt layout; nominal hardware','Shanks, hex heads and nuts shown; threads, washers and drilled holes are omitted.',count=104,diameter_in=.875,grade='A325 Type 3')

# Four support lines, seven separate bearing assemblies per line.
for si,u in enumerate(BEARINGS):
    label=('End bent 1','Pier 2','Pier 3','End bent 4')[si]
    for j,y in enumerate(YS):
        x=sx(u,y);z0=float(el(SEAT[si,j]));zp=z0+PAD;zl=zp+LOAD;zt=zl+SHIM[si,j]
        pad=box(x-6*IN,x+6*IN,y-8*IN,y+8*IN,z0,zp)
        add(f'bearing_{si+1}_{j+1}',f'{label} bearing {j+1} | laminated elastomer','bearings',pad,[16,22,24],
            length_in=12,width_in=16,depth_in=3.03125,shore_A=55)
        stack=[box(x-6.5*IN,x+6.5*IN,y-8.5*IN,y+8.5*IN,zp,zl)]
        if zt>zl:stack.append(box(x-6.5*IN,x+6.5*IN,y-5*IN,y+5*IN,zl,zt))
        for dx in [-4,4]:
            for dy in [-2.5,2.5]:
                stack.append(hexbolt([x+dx*IN,y+dy*IN,zl-.7*IN],[x+dx*IN,y+dy*IN,zt+TF],.375*IN))
        if si in (1,2):
            for side in [-1,1]:
                yy=y+side*10.5*IN
                stack.extend([box(x-7.25*IN,x+7.25*IN,yy-2.375*IN,yy+2.375*IN,z0,z0+.5*IN),
                   box(x-7.25*IN,x+7.25*IN,yy-.25*IN,yy+.25*IN,z0+.5*IN,z0+6.5*IN)])
                for dx in [-3.25,3.25]:stack.append(hexbolt([x+dx*IN,yy,z0],[x+dx*IN,yy,z0+.8*IN],.625*IN))
        add(f'bearing_steel_{si+1}_{j+1}',f'{label} bearing {j+1} | load plate, shims and retainers','steel',concat(stack),[22],
            'Dimensioned main plates; simplified retainers','Retainer gussets, welds, washers, internal pad laminations and molded draft are omitted.',
            load_plate_in=[13,17,1.75],shim_stack_in=round(SHIM[si,j]/IN,4))
        contacts.append({'support':si+1,'beam':j+1,'beam_bearing_gap_m':float(top(j,u)-D-zt)})
        # Clipped bearing stiffeners either side of web, as detailed on sheet 22.
        wid=(4.75 if si in (0,3) else 7.25)*IN;th=(.5 if si in (0,3) else .6875)*IN
        pieces=[]
        for side in [-1,1]:
            profile=[(0,0),(wid,0),(wid,D-2*TF),(2.5*IN,D-2*TF),
                     (0,D-2*TF-1.25*IN)]
            pieces.append(sweep(profile,[-th/2,th/2],lambda t,v,h:(x+t,y+side*(TW/2+v),zt+TF+h)))
        add(f'stiffeners_{si+1}_{j+1}',f'{label} beam {j+1} bearing stiffeners','steel',concat(pieces),[18,22],thickness_in=th/IN)

# Caps: the five original elevation steps remain. Boundaries come from sheets 12,16.
for si,u in enumerate(BEARINGS):
    label=('End bent 1','Pier 2','Pier 3','End bent 4')[si]
    steps=[(-24,-12.5,6),(-12.5,-1.75,4),(-1.75,1.75,3),(1.75,12.5,2),(12.5,24,0)]
    bottom=float(el(901.77 if si==0 else 902.19 if si==3 else 901.62 if si==1 else 901.80))
    cap=[]
    width=(2.5 if si in (0,3) else 3)*FT
    for a,b,j in steps:
        # True skew-axis dimensions; concrete elevations are approximate existing values.
        cap.append(rot(box(-width/2,width/2,a*FT,b*FT,bottom,float(el(SEAT[si,j]))),u))
    add(f'cap_{si+1}',f'{label} retained stepped cap','abutments' if si in (0,3) else 'piers',concat(cap),[12,13,16,24],
        'Approximate retained geometry from existing drawings','Step boundaries and cap end corners are simplified. Primary plans explicitly call existing concrete dimensions approximate.',
        length_along_skew_ft=48,width_ft=width/FT)
    if si in (1,2):
        footbot=886.12 if si==1 else 886.30
        # Wall ends are rounded; 47-ft overall stem and 2-ft thickness (old plans sheet11).
        p=LineString([(0,-22.5*FT),(0,22.5*FT)]).buffer(FT,quad_segs=12)
        stem=tm.creation.extrude_polygon(p,bottom-float(el(footbot+3)),engine='earcut');stem.apply_translation([0,0,float(el(footbot+3))])
        add(f'pier_{si+1}_wall',f'Pier {si+1} rounded wall stem','piers',rot(stem,u),[16],
            'Retained geometry; historical source','Rounded 47 x 2 ft wall; original 1980 PDF p.11 supplies rounded ends and footing width. Elevations use 2017 adjusted levels.',
            thickness_ft=2,length_ft=47,historical_pdf_page=11)
        add(f'footing_{si+1}',f'Pier {si+1} retained pile footing','foundations',rot(box(-4*FT,4*FT,-24*FT,24*FT,float(el(footbot)),float(el(footbot+3))),u),[16],
            'Historical design dimensions','48 x 8 x 3 ft from original 1980 PDF p.11; final driven pile lengths are not verified.',length_ft=48,width_ft=8,depth_ft=3,historical_pdf_page=11)
        for row in [-1,1]:
            for n,v in enumerate(np.arange(-22.5,23,5),1):
                ztop=float(el(footbot))+FT
                # 4:1 battered outer pile rows; 20 ft design length along pile axis.
                direction=np.array([row/4,0,-1.]);direction/=np.linalg.norm(direction)
                a=np.array([row*2*FT,v*FT,ztop]);b=a+direction*20*FT
                add(f'pile_{si+1}_{row}_{n}',f'Pier {si+1} pile row {row:+d} position {n}','foundations',rot(rod(a,b,.5*FT,16),u),[16],
                    'Historical design length','1980 PDF p.11: 20 piles per pier, 12-in steel-encased concrete, 20-ft design length, 4:1 batter. Hidden by default; not verified as-built.',diameter_in=12,design_length_ft=20,batter='4:1')
    else:
        # Nine retained piles, 5 ft 5-5/8 in spacing, shown on 1980 sheet9.
        for n,v in enumerate(np.linspace(-21.875,21.875,9),1):
            a=np.array([0,v*FT,bottom+FT]);b=np.array([0,v*FT,float(el(872-.57))])
            add(f'endpile_{si+1}_{n}',f'{label} retained pile {n}','foundations',rot(rod(a,b,.5*FT,16),u),[12,24],
                'Historical estimated pile tip','Original 1980 PDF p.9 estimates tip elev.872; -0.57 ft datum adjustment follows 2017 removal notes. Driven tips are unknown.',diameter_in=12)
        # Semi-integral diaphragm surrounds each beam end, not an exposed backwall above road.
        depth=2.5*FT;direc=-1 if si==0 else 1
        uu0,uu1=sorted([u-direc*1.25*FT,u+direc*(HALF-abs(u))])
        prof=[(-23.25*FT,0),(23.25*FT,0),(23.25*FT,1),(0,1),(-23.25*FT,1)]
        dia=sweep(prof,[uu0,uu1],lambda t,y,f:(sx(t,y),y,
            np.interp(y,YS[::-1],el(SEAT[si,::-1]))+.5*IN if f==0 else surface(sx(t,y),y)-8*IN))
        add(f'end_diaphragm_{si+1}',f'{label} semi-integral concrete diaphragm','abutments',dia,[23,24],
            'Dimensioned envelope; embedded interfaces simplified','Concrete envelope includes embedded beam ends. Individual reinforcement, sleeves and internal voids are excluded.')
        # Reconstructed wings follow the 8 ft 3 in longitudinal extension, 11-in concrete + 1-in isolation.
        for side in [-1,1]:
            y=side*(23.25*FT+6*IN);xc=sx(u,y);length=8.25*FT
            xa,xb=xc-length/2,xc+length/2
            p=[(y-5.5*IN,0),(y+5.5*IN,0),(y+5.5*IN,1),(y-5.5*IN,1)]
            w=sweep(p,[xa,xb],lambda x,yy,f:(x,yy,bottom if f==0 else surface(x,yy)))
            add(f'wing_{si+1}_{side}',f'{label} wing {"north" if side>0 else "south"}','abutments',w,[14,23],
                'Dimensioned width and length; interpolated top','Wing station offsets and retained lower joint are simplified; 1-in separation from the deck fascia is retained.',length_ft=8.25,concrete_thickness_in=11)

# Six regular diaphragm rows plus two skew pier rows; each crosses six beam bays.
for row,uf in enumerate([-65,-44.75,-7.5,7.5,44.75,65,-25,25],1):
    skew=row>6
    for j in range(6):
        y0,y1=YS[j+1],YS[j];mid=(y0+y1)/2;u=uf*FT
        xmid=sx(u,mid)
        # Regular diaphragms perpendicular to beams; pier diaphragms follow skew line.
        xfun=lambda y:xmid+K*(y-mid) if skew else xmid
        z=float(min(top(j,u),top(j+1,u)))-5*IN
        # C15x33.9 envelope, 15 x 3.4, .4 web, .65 nominal flange; taper omitted.
        pr=np.array([(0,0),(3.4,0),(3.4,.65),(.4,.65),(.4,14.35),(3.4,14.35),(3.4,15),(0,15)])*IN
        channel=sweep(pr,[y0+TW/2,y1-TW/2],lambda y,a,b:(xfun(y)+a,y,z-15*IN+b))
        location=f'Pier {2 if uf==-25 else 3}' if skew else f'Span {"A" if uf<-25 else "C" if uf>25 else "B"}'
        add(f'diaphragm_{row}_{j+1}',f'{location} diaphragm row {row} bay {j+1}','diaphragms',channel,[17,20],
            'Dimensioned arrangement; nominal channel profile','Nominal section dimensions from Nucor p.47; flange taper, root fillets and skew bent-plate fold simplified.',section='C15x33.9',bay_ft=7)
        plateparts=[];bolts=[]
        for yy,sg,jj in [(y0,1,j+1),(y1,-1,j)]:
            xx=xfun(yy);tu=xx-K*yy;bt=float(top(jj,tu))-D
            plateparts.append(box(xx-.25*IN,xx+.25*IN,min(yy,yy+sg*7.25*IN),max(yy,yy+sg*7.25*IN),bt+TF,bt+D-TF))
            for h in [3,6,9,12]:
                for dist in [1.5,4.5]:
                    bolts.append(hexbolt([xx-.25*IN,yy+sg*dist*IN,z-h*IN],
                                         [xx+.4*IN,yy+sg*dist*IN,z-h*IN],.4375*IN))
        add(f'diaphragm_plates_{row}_{j+1}',f'{location} diaphragm {row}-{j+1} connection plates','steel',concat(plateparts),[18,20],
            'Dimensioned envelope; skew connection simplified','Two 1/2-in by 7-1/4-in plates. Pier bent-plate fold is represented by its connection envelope.')
        add(f'diaphragm_bolts_{row}_{j+1}',f'{location} diaphragm {row}-{j+1} bolts','fasteners',concat(bolts),[20],
            'Nominal hardware','Threads and holes omitted.',count=len(bolts),diameter_in=.875)

# FC profile is 33 in high and 16 in wide, with 2 in coping beyond its rear face.
fc=np.array([(0,0),(16,0),(16,3),(11,10),(9,33),(0,33)])*IN
for side in [-1,1]:
    edge=side*(23.25*FT-2*IN)
    def railcoord(u,v,z):
        yy=edge-side*v;xx=sx(u,edge);return(xx,yy,surface(xx,yy)+z)
    add(f'rail_{side}',f'{"North" if side>0 else "South"} continuous Type FC barrier','rails',sweep(fc,np.linspace(-HALF,HALF,180),railcoord),[27,31],
        'Dimensioned profile','Small edge chamfers, surface coating thickness and rebar omitted.',height_in=33,base_width_in=16)
    # Thickened outer fascia: 9-5/8 in at edge vs 8 in main slab.
    y0,y1=sorted([side*23.25*FT,side*(23.25*FT-8*IN)])
    prof=[(y0,0),(y1,0),(y1,1),(y0,1)]
    add(f'fascia_{side}',f'{"North" if side>0 else "South"} thickened deck fascia','haunches',sweep(prof,np.linspace(-HALF,HALF,180),
        lambda u,y,t:(sx(u,y),y,surface(sx(u,y),y)-8*IN-(1.625*IN if t==0 else 0))),[27,31],
        'Dimensioned outer depth; simplified width','Drip bead recess and interior taper are not cut.',edge_depth_in=9.625)
    for n,u in enumerate(np.linspace(-HALF,HALF,6),1):
        x=sx(u,edge);z=float(surface(x,edge))+33*IN
        add(f'delineator_{side}_{n}',f'{"North" if side>0 else "South"} barrier delineator {n}','accessories',
            box(x-.05,x+.05,edge-side*.08-.025,edge-side*.08+.025,z,z+.04),[31],
            'Count and maximum spacing; schematic product','12 total per quantity table, distributed evenly including ends. Manufacturer geometry and exact stations not given.',count_on_side=6)

# Approach slabs have one skew edge and one square road edge, NOT two parallel skew edges.
for end in [-1,1]:
    label='West' if end<0 else 'East';u=end*HALF
    outer=end*(HALF+K*21.75*FT+20.5*FT)
    profile=[(-21.75*FT,0),(0,0),(21.75*FT,0),(21.75*FT,1),(0,1),(-21.75*FT,1)]
    def ac(t,y,h):
        inner=sx(u,y);x=inner*(1-t)+outer*t
        return x,y,surface(x,y)-(12*IN if h==0 else 0)
    add(f'approach_{label.lower()}',f'{label} approach slab | 12 in','approaches',sweep(profile,np.linspace(0,1,65),ac),[32,33],
        thickness_in=12,width_ft=43.5,min_length_ft=20.5)
    for side in [-1,1]:
        yy=side*22.5*FT;x0=sx(u,side*21.75*FT);x1=x0+end*(16+5/12)*FT
        xa,xb=sorted([x0,x1])
        prof=[(yy-.75*FT,0),(yy+.75*FT,0),(yy+.75*FT,1),(yy-.75*FT,1)]
        add(f'extension_{end}_{side}',f'{label} {"north" if side>0 else "south"} approach railing extension','approaches',
            sweep(prof,np.linspace(xa,xb,30),lambda x,y,h:(x,y,surface(x,y)-(12*IN if h==0 else 0))),[32,33],length_ft=16+5/12,width_ft=1.5)
        # TFC sections A-B-C-D from INDOT 2013 standard; 15 ft 8 in long.
        length=(15+8/12)*FT;edge=side*(23.25*FT-2*IN);start=sx(u,edge)
        xs=np.unique(np.r_[np.linspace(0,length,50),np.array([7+2/12,8+1/12,11+5/12])*FT])
        def trans(t,v,z):
            width=np.interp(t,np.array([0,7+2/12,8+1/12,11+5/12,15+8/12])*FT,np.array([16,11.625,11,9,9])*IN)
            x=start+end*t
            # Preserve the 9-in top. Lower face changes from FC to a vertical 9-in end.
            if v==0: vv=0
            elif z>=33*IN-1e-8: vv=9*IN
            elif z>=10*IN-1e-8: vv=np.interp(t,xs[[0,-1]],[11*IN,9*IN])
            else: vv=width
            y=edge-side*vv
            return x,y,surface(x,y)+z
        add(f'tfc_{end}_{side}',f'{label} {"north" if side>0 else "south"} Type TFC transition','rails',sweep(fc,xs,trans),[31,32],
            'Standard sections; interpolated transition','INDOT E706-TTFC-01/02 (September 2013). Taper between sections approximated; guardrail attachment holes and steel TGB approach guardrail are not modeled.',length_ft=15+8/12,standard='E706-TTFC-01/02')

ASSUMPTIONS=[
 'Reconstruction of the 2018 B-38321 rehabilitation design (drawings approved 2017-08-22), not a current-condition or as-built survey.',
 '2026 B-44483 / 2200653 plans are supplementary evidence only; proposed deck-overlay work is not mixed into the 2018 geometric state.',
 'Existing cap elevations and concrete dimensions are approximate in the primary drawings. The beam surfaces interpolate support/grade geometry; fabrication camber and construction screed allowances are excluded. Combining these approximate seat levels with the shim table yields some haunch gaps below the nominal 3/4-in minimum. These interfaces remain unresolved and require surveyed seat/beam levels; the model is therefore marked needs detail.',
 'Original 1980 drawings supply retained wall ends, footing dimensions and design pile lengths. The 2017 drawings apply a -0.57-ft elevation adjustment. Actual driven pile tips are unknown; foundations are hidden by default.',
 'Steel member root fillets and channel flange taper are omitted. Connection threads, washers, drilled holes, weld beads, internal pad laminations, shear studs embedded in concrete and internal reinforcement are not modeled.',
 'Approach TGB steel guardrail, its terminal systems, drainage outlets, backfill, riprap/terrain and drip recesses remain outside the modeled scope. Wing and TFC transitions retain simplified envelope geometry.',
 'Material colors are visualization choices and are not evidence of the actual coating or surface condition.',
 'This GLB is not a validated FEM model. Joints, material calibration, loads and meshing require a separate engineering model.'
]
COVERAGE=[
 ('Whole bridge geometry','modeled','All three spans, 46 ft 6 in width, 15-degree skew and 200-ft crest profile.',[9,10,11,27,29],['deck']),
 ('Steel beams and field splices','modeled_with_simplifications','Seven continuous W27x94 lines in three fabrication segments; fourteen eight-plate splices with 104 bolts each. Loaded profile interpolated, fillets and holes omitted.',[17,18,19],['girders','steel','fasteners']),
 ('Diaphragms','modeled_with_simplifications','48 channel diaphragms in six regular and two skew support rows; connection plates and bolts. Skew folds and channel taper simplified.',[17,20],['diaphragms']),
 ('Bearings','modeled_with_simplifications','28 pads, load plates and source shim stacks; side retainers at piers. Internal rubber laminations, washers and welds excluded.',[22],['bearings']),
 ('Retained substructure','modeled_with_simplifications','Both wall piers and end bents. Stepped caps and wings are approximate existing envelopes, as stated on the plans.',[12,14,16,23,24],['piers','abutments']),
 ('Buried foundations','design_geometry_only','Retained footings and 58 design piles from 1980 sheets 9/11. Unknown driven pile tips; hidden by default.',[12,16],['foundations']),
 ('Barriers and approaches','modeled_with_simplifications','FC barriers, four TFC transitions, both skew-to-square approach slabs, four extensions and twelve schematic delineators.',[31,32,33],['rails','approaches','accessories']),
 ('Approach steel guardrail and terminals','not_modeled','TGB and terminal systems require additional standard details and exact station placement.',[9,10,31],[]),
 ('Drainage and site surfaces','not_modeled','Existing drain outlets, riprap and ground geometry not reconstructed. Drip-bead recesses and east approach curbs not modeled.',[9,24,31,32],[]),
 ('Internal reinforcement and construction equipment','excluded','No reinforcement cages, embedded shear studs, temporary detours or equipment.',[18,23,24,27],[])
]

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    # Independent geometric invariants, including the interfaces that caused earlier model issues.
    clearance=[]
    for j,y in enumerate(YS):
        for u in np.linspace(-75.25*FT,75.25*FT,301):
            clearance.append(float(min(surface(sx(u,y),y+v)-8*IN-top(j,u) for v in [-BF/2,BF/2])))
    if min(clearance)<=0:raise ValueError(f'Beam penetrates deck: minimum clearance {min(clearance)} m')
    assert max(abs(v['beam_bearing_gap_m']) for v in contacts)<1e-9
    assert len([p for p in parts if p['layer']=='girders'])==21
    assert len([p for p in parts if p['layer']=='bearings'])==28
    assert len([p for p in parts if p['layer']=='diaphragms'])==48
    scene=tm.Scene();transform=np.array([[1,0,0,0],[0,0,1,0],[0,-1,0,0],[0,0,0,1.]])
    for key,m in meshes.items():
        copy=m.copy();copy.apply_transform(transform);scene.add_geometry(copy,node_name=key,geom_name=key)
    (OUT/'model.glb').write_bytes(scene.export(file_type='glb'))
    coverage=[]
    for feature,status,detail,pages,layers in COVERAGE:
        coverage.append(dict(feature=feature,status=status,detail=detail,sources=[f'2017 rehabilitation PDF p.{p}' for p in pages],
            part_ids=[p['id'] for p in parts if p['layer'] in layers or p['id'] in layers]))
    sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
    manifest=dict(title='SR 44 over Mud Creek | 2018 rehabilitation design',structure_id='044-70-06634 A',designation='1500342',
        units='metres',spans_ft=[49.75,50,49.75],deck_length_ft=151+1/12,deck_width_ft=46.5,skew_deg=15,
        source_pdf='drawings.pdf',source_sha256=sha(OUT/'drawings.pdf'),
        source_note='INDOT B-38321, 34 sheets approved August 22, 2017. Models the 2018 rehabilitation design. Current inventory suffix B refers to later work; geometry here uses drawing suffix A.',
        assumptions=ASSUMPTIONS,layers=LAYERS,parts=parts,default_hidden_layers=['foundations'],
        native_axes='X increasing station from sta.617+95, Y transverse toward beam 1, Z elevation minus 885 ft; metres',
        glb_axes='Y up: (native X, native Z, -native Y); local coordinates, no world georeferencing transform',
        detail_coverage=coverage,external_sources=[
            dict(id='Primary rehabilitation drawings (34 pages)',url='https://erms12c.indot.in.gov/viewdocs/View12.aspx?Id=9552113'),
            dict(id='Original 1980 plans: retained substructure, pp.9 and 11',url='https://erms12c.indot.in.gov/viewdocs/View12.aspx?Id=9552112',local_file='original_1980_plans.pdf',sha256=sha(OUT/'original_1980_plans.pdf')),
            dict(id='2013 INDOT TFC transition standard, pp.1-2',url='https://www.in.gov/dot/div/contracts/standards/drawings/sep20/e/700e/e700%20combined%20pdfs/E706-TTFC.pdf',local_file='E706-TTFC.pdf',sha256=sha(OUT/'E706-TTFC.pdf')),
            dict(id='Nucor-Yamato nominal shape catalog, pp.21 and 47',url='https://www.nucoryamato.com/StaticData/catalog.pdf',local_file='nucor_structural_shapes.pdf',sha256=sha(OUT/'nucor_structural_shapes.pdf')),
            dict(id='2026 overlay plans: reference only, not modeled',url='https://erms12c.indot.in.gov/viewdocs/View12.aspx?Id=9683607')])
    (OUT/'model_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    verification=dict(component_count=len(parts),all_meshes_watertight=True,all_volumes_positive=True,
        minimum_deck_beam_clearance_m=min(clearance),maximum_bearing_contact_error_m=max(abs(v['beam_bearing_gap_m']) for v in contacts),
        girder_lines=7,girder_segments=21,bearings=28,diaphragms=48,splice_assemblies=14,splice_bolts=14*104,
        deck_dimensions_ft=[151+1/12,46.5],spans_ft=[49.75,50,49.75],source_pdf_sha256=manifest['source_sha256'],
        glb_sha256=sha(OUT/'model.glb'),contacts=contacts,
        limitations='Geometry checks only. Does not certify completeness, engineering capacity, fabrication tolerances or as-built condition.')
    (OUT/'geometry_verification.json').write_text(json.dumps(verification,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in verification.items() if k!='contacts'},indent=2))

if __name__=='__main__':main()

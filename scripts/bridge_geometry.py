"""Small geometric primitives for source-backed exterior reconstructions.

No bridge is generated on import. Coordinates are X station, Y transverse, Z up.
These meshes are visualization geometry, not connected finite elements.
"""
import hashlib
import json
import re
from pathlib import Path
import numpy as np
import trimesh as tm
from shapely.geometry import Polygon

FT, IN = .3048, .0254
COLORS = dict(deck='#d1d5d0', girders='#8e6c55', haunches='#b7b6aa',
    steel='#94745b', diaphragms='#8d9b9c', bracing='#8d9b9c', fasteners='#a2acb0',
    bearings='#414c54', piers='#b7b2a6', abutments='#beb8a8', foundations='#8f9b9b',
    rails='#d6cebd', approaches='#bbc4c0', joints='#39434a', drainage='#6c8389',
    sidewalks='#c9c8b8', arches='#b9ad92', walls='#c7baa0', ornament='#a79a7f',
    fill='#9b987f', accessories='#59676f')
LABELS = dict(deck='Concrete deck', girders='Longitudinal girders', haunches='Deck haunches',
    steel='Steel plates and stiffeners', diaphragms='Diaphragms', bracing='Cross frames',
    fasteners='Connection fastener assemblies', bearings='Bearings and pedestals',
    piers='Intermediate piers and bents', abutments='End bents and wing walls',
    foundations='Design foundation envelopes', rails='Bridge rails', approaches='Approach slabs',
    joints='Deck joints', drainage='Deck drainage', sidewalks='Sidewalks and curbs',
    arches='Concrete arch barrels', walls='Spandrel walls', ornament='Architectural rail panels',
    fill='Arch fill envelope', accessories='External accessories')

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def box(x0,x1,y0,y1,z0,z1):
    assert x1>x0 and y1>y0 and z1>z0, (x0,x1,y0,y1,z0,z1)
    m=tm.creation.box([x1-x0,y1-y0,z1-z0])
    m.apply_translation([(x0+x1)/2,(y0+y1)/2,(z0+z1)/2]);return m

def sweep(profile, xs, fn):
    poly=Polygon(profile)
    assert poly.is_valid and poly.area>0
    vv,ff=tm.creation.triangulate_polygon(poly,engine='earcut')
    if np.allclose(vv[-1],vv[0]):ff=np.where(ff==len(vv)-1,0,ff);vv=vv[:-1]
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

def rectangular_bar(a,b,width,depth):
    a,b=np.asarray(a),np.asarray(b);v=b-a
    m=tm.creation.box([width,depth,np.linalg.norm(v)])
    m.apply_transform(tm.geometry.align_vectors([0,0,1],v));m.apply_translation((a+b)/2);return m

def concat(ms): return tm.util.concatenate(ms)

def iform(d,b,tw,tf):
    return [(-b/2,0),(b/2,0),(b/2,tf),(tw/2,tf),(tw/2,d-tf),(b/2,d-tf),
        (b/2,d),(-b/2,d),(-b/2,d-tf),(-tw/2,d-tf),(-tw/2,tf),(-b/2,tf)]

def bolt(a,b,r):
    a,b=np.asarray(a),np.asarray(b);v=(b-a)/np.linalg.norm(b-a)
    return concat([rod(a,b,r),rod(a-v*.012,a,r*1.55,6),rod(b,b+v*.017,r*1.55,6)])

class Model:
    def __init__(self,bid,length,width,skew,grade,crossfall=.02,crown=0):
        self.bid,self.length,self.width=bid,length,width
        self.skew=skew;self.k=-np.tan(np.radians(skew));self.c=np.cos(np.radians(skew))
        self.grade,self.crossfall,self.crown=grade,crossfall,crown
        self.colors=COLORS.copy()
        self.parts=[];self.meshes={};self.coverage=[];self.checks={};self.contacts=[]

    def sx(self,u,y):return u+self.k*y
    def surface(self,x,y):return self.grade(x)-self.crossfall*np.abs(y-self.crown)

    def slab(self,u0,u1,y0,y1,thick,offset=0):
        yy=sorted(set([y0,y1]+([self.crown] if y0<self.crown<y1 else [])))
        profile=[(y,-thick) for y in yy]+[(y,0) for y in reversed(yy)]
        return sweep(profile,np.linspace(u0,u1,max(2,int((u1-u0)/.6)+1)),
            lambda u,y,z:(self.sx(u,y),y,self.surface(self.sx(u,y),y)+offset+z))

    def transverse(self,u,thick,y0,y1,z0,z1):
        # Thickness measured normal to the skew support line.
        return sweep([(y0,z0),(y1,z0),(y1,z1),(y0,z1)],[-thick/2/self.c,thick/2/self.c],
            lambda t,y,z:(self.sx(u+t,y),y,z))

    def add(self,key,name,layer,m,pages,basis='Dimensioned envelope; minor finishes simplified',note='',**dims):
        assert key not in self.meshes
        assert re.fullmatch(r'[A-Za-z0-9_-]+',key), 'IDs must survive GLTFLoader name sanitization: '+key
        m.remove_unreferenced_vertices();m.fix_normals(multibody=True)
        assert m.is_watertight and m.volume>0 and np.isfinite(m.vertices).all(),key
        color=self.colors[layer];m.visual.vertex_colors=[int(color[j:j+2],16) for j in (1,3,5)]+[255]
        meta=dict(id=key,name=name,layer=layer,color=color,pdf_pages=pages,basis=basis,note=note,dimensions=dims)
        m.metadata.update(meta);self.meshes[key]=m
        self.parts.append(dict(**meta,bounds_m=np.round(m.bounds,6).tolist(),volume_m3=round(float(m.volume),9)))

    def cover(self,feature,status,detail,pages,layers):
        self.coverage.append(dict(feature=feature,status=status,detail=detail,
            sources=[f'Primary PDF p.{p}' for p in pages],
            part_ids=[p['id'] for p in self.parts if p['layer'] in layers or p['id'] in layers]))

    def barriers(self,u0,u1,pages,height=.8382,width=.4064,top=.2286,segments=1):
        # Sloped traffic face; outer face vertical. Profile dimensions are supplied by caller.
        pr=[(0,0),(width,0),(width,.254),(top,height),(0,height)]
        for side in [-1,1]:
            for i,(a,b) in enumerate(zip(np.linspace(u0,u1,segments+1)[:-1],np.linspace(u0,u1,segments+1)[1:])):
                edge=side*(self.width/2-.05)
                self.add(f'rail_{side}_{i}',f'Bridge rail {"left" if side>0 else "right"} panel {i+1}','rails',
                    sweep(pr,np.linspace(a,b,max(2,int((b-a)/.6)+1)),lambda u,v,z:(self.sx(u,edge-side*v),edge-side*v,self.surface(self.sx(u,edge-side*v),edge-side*v)+z)),
                    pages,'Source section envelope; surface recesses and reinforcement omitted',height_m=height,base_width_m=width)

    def bearing(self,key,u,y,bottom,depth,pages,pad=(.23,.355,.075),plate=(.26,.405,.06),note=''):
        x=self.sx(u,y);px,py,ph=pad;lx,ly,lh=plate
        m=concat([box(x-px/2,x+px/2,y-py/2,y+py/2,bottom-ph-lh,bottom-lh),
                  box(x-lx/2,x+lx/2,y-ly/2,y+ly/2,bottom-lh,bottom)])
        self.add(key,key.replace('_',' '),'bearings',m,pages,'Bearing envelope; internal laminations and anchors omitted',note,
            pad_length_m=px,pad_width_m=py,pad_thickness_m=ph,load_plate_thickness_m=lh)
        self.contacts.append(dict(id=key,girder_bottom_m=float(bottom),bearing_top_m=float(m.bounds[1,2]),seat_m=float(m.bounds[0,2])))
        return bottom-ph-lh

    def save(self,out,meta):
        if 'bearings' in self.checks:assert len(self.contacts)==self.checks['bearings']
        if 'girder_segments' in self.checks:
            assert sum(p['layer']=='girders' for p in self.parts)==self.checks['girder_segments']
        # Check generated coordinates against the deck soffit, including flange edges.
        gaps=[]
        for p in self.parts:
            if p['layer']!='girders':continue
            vv=self.meshes[p['id']].vertices
            gaps.extend((self.surface(vv[:,0],vv[:,1])-meta.get('deck_thickness_m',.2032)-vv[:,2]).tolist())
        if gaps:
            assert min(gaps)>0, 'A girder penetrates the deck'
            self.checks['minimum_deck_girder_clearance_m']=float(min(gaps))
        out=Path(out);scene=tm.Scene();transform=np.array([[1,0,0,0],[0,0,1,0],[0,-1,0,0],[0,0,0,1.]])
        for key,m in self.meshes.items():
            cp=m.copy();cp.apply_transform(transform);scene.add_geometry(cp,node_name=key,geom_name=key)
        (out/'model.glb').write_bytes(scene.export(file_type='glb'))
        manifest=dict(meta,units='metres',deck_length_m=self.length,deck_width_m=self.width,skew_deg=self.skew,
            source_pdf='drawings.pdf',source_sha256=sha(out/'drawings.pdf'),parts=self.parts,
            layers={k:LABELS[k] for k in LABELS if any(p['layer']==k for p in self.parts)},
            default_hidden_layers=['foundations','fill'],native_axes='X increasing station, Y transverse, Z up; local metres',
            glb_axes='Y up: (native X, native Z, -native Y); no world georeferencing transform',detail_coverage=self.coverage)
        (out/'model_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
        # Reopen the actual artifact, not just in-memory source geometry.
        loaded=tm.load(out/'model.glb',force='scene',process=False)
        assert set(loaded.graph.nodes_geometry)==set(self.meshes)
        assert all(g.is_watertight and g.volume>0 for g in loaded.geometry.values())
        assert np.allclose(loaded.bounds,scene.bounds,atol=1e-4)
        error=max([abs(c['girder_bottom_m']-c['bearing_top_m']) for c in self.contacts]+[0])
        assert error<1e-8
        report=dict(component_count=len(self.parts),all_meshes_watertight=True,all_volumes_positive=True,
            exported_glb_reopened=True,mesh_names_match_manifest=True,maximum_bearing_contact_error_m=error,
            glb_sha256=sha(out/'model.glb'),source_pdf_sha256=manifest['source_sha256'],
            checks=self.checks,contacts=self.contacts,
            limitations='Geometry checks only. Approximate interfaces are geometric constructions, not surveyed fit or FEM validation.')
        (out/'geometry_verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
        print(self.bid,len(self.parts),'parts',round((out/'model.glb').stat().st_size/1e6,2),'MB',flush=True)
        return manifest

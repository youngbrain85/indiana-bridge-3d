"""Virginia Avenue and SR44: source-backed exterior assets, never FE meshes.

Run with the downloaded additional_20261015 candidate archive beside this repo.
Only writes the two assigned bridge directories. The primary drawing is an
unchanged original PDF; historical and revision PDFs remain separate originals.
"""
from pathlib import Path
import json
import shutil
import numpy as np
import trimesh as tm
import fitz
from shapely.geometry import Polygon
from bridge_geometry import Model, FT, IN, box, sweep, rod, rectangular_bar, concat, iform, sha

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parents[1]
ARCHIVE = WORKSPACE/'outputs/indiana_bridge_candidates/additional_20261015'
BASE = ROOT/'data/bridges'
COMMON = [
    'Whole-crossing exterior reconstruction of the stated proposed design, not an as-built survey or confirmation of construction completion.',
    'Amber / needs_detail: fabrication tolerances, exact field seats, local notches and transitions, small fittings, and terrain remain incomplete.',
    'Internal reinforcement, shear studs, embedded anchors and welds are omitted. No rendered component is a finite element or a solid-stress result.',
    'Any later FEM must freeze its own material, stiffness, connectivity and support assumptions. Visual mesh volume is not a section-property source.',
    'Foundations are hidden by default; foundation envelopes are design references and do not establish actual field embedment.'
]


def dump(path, data):
    path.write_text(json.dumps(data, indent=2), encoding='utf8')


def prepare(bid, candidate_id, primary_id, reviewed):
    candidate = next(c for c in json.loads((ARCHIVE/'candidates.json').read_text(encoding='utf8'))['candidates'] if c['id']==candidate_id)
    out=BASE/bid
    (out/'sources').mkdir(parents=True,exist_ok=True)
    docs=[]
    for d in candidate['documents']+candidate.get('revision_notices',[]):
        src=ARCHIVE/d['local_path']; dst=out/'sources'/src.name
        assert sha(src)==d['sha256'],src
        shutil.copy2(src,dst)
        with fitz.open(dst) as pdf: pages=len(pdf)
        assert pages==d['pages']
        docs.append(dict(id=d['document_id'],title=d['title'],local_file='sources/'+dst.name,url=d['url'],sha256=sha(dst),original_pages=pages,
            reviewed_pages=reviewed.get(d['document_id'],[]),role='primary_geometry' if d['document_id']==primary_id else ('revision_evidence' if d['kind']=='revision_notice' else 'historical_evidence')))
        if d['document_id']==primary_id:
            shutil.copy2(src,out/'drawings.pdf'); primary=docs[-1]
    index=dict(primary='drawings.pdf',binder='drawings.pdf',is_compilation=False,pages=primary['original_pages'],sha256=sha(out/'drawings.pdf'),
        primary_source_id=primary_id,page_numbering='Unchanged one-based original primary PDF pages. Secondary sources have independent original PDF page numbers.',source_documents=docs)
    dump(out/'source_index.json',index)
    return out,candidate,index


def refs(m, source_id, pages, part_ids=None):
    for p in m.parts if part_ids is None else [p for p in m.parts if p['id'] in part_ids]:
        p.setdefault('source_refs',[]).append(dict(source_id=source_id,pdf_pages=pages))


def slab_with_breaks(m,a,b,y0,y1,thick,breaks=(),offset=0):
    yy=sorted(set([y0,y1]+[y for y in breaks if y0<y<y1]))
    pr=[(y,-thick) for y in yy]+[(y,0) for y in reversed(yy)]
    return sweep(pr,np.linspace(a,b,max(2,int((b-a)/.5)+1)),lambda u,y,z:(m.sx(u,y),y,m.surface(m.sx(u,y),y)+z+offset))


def level_prism(m,a,b,y0,y1,bottom,top):
    return sweep([(y0,0),(y1,0),(y1,1),(y0,1)],[a,b],lambda u,y,t:(m.sx(u,y),y,(1-t)*bottom(m.sx(u,y),y)+t*top(m.sx(u,y),y)))


def preview(m,out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    fig=plt.figure(figsize=(12,7),dpi=160);ax=fig.add_subplot(111,projection='3d');fig.patch.set_facecolor('#eef2f3');ax.set_facecolor('#eef2f3')
    meshes=[(p,m.meshes[p['id']]) for p in m.parts if p['layer'] not in ['foundations','fill']]
    view=np.array([np.cos(np.radians(23))*np.cos(np.radians(-58)),np.cos(np.radians(23))*np.sin(np.radians(-58)),np.sin(np.radians(23))])
    for p,g in meshes:
        # Matplotlib has no z-buffer: hide back faces to avoid bottom-surface
        # triangles appearing through a coplanar top face in the thumbnail.
        keep=g.face_normals@view>1e-6
        triangles=g.vertices[g.faces[keep]]
        normals=g.face_normals[keep];light=np.clip(normals@np.array([.25,-.4,.9]),-.4,1);rgb=np.array([int(p['color'][k:k+2],16)/255 for k in [1,3,5]])
        shades=np.clip(rgb[None,:]*(.78+.22*light[:,None]),0,1)
        ax.add_collection3d(Poly3DCollection(triangles,facecolors=shades,edgecolors='none',linewidths=0))
    vertices=np.vstack([g.vertices for _,g in meshes]);mn=vertices.min(0);mx=vertices.max(0);ext=mx-mn
    ax.set_xlim(mn[0],mx[0]);ax.set_ylim(mn[1],mx[1]);ax.set_zlim(mn[2]-.2,mx[2]+.5);ax.set_box_aspect(ext)
    ax.view_init(elev=23,azim=-58);ax.set_axis_off();fig.subplots_adjust(0,0,1,1);fig.savefig(out/'preview.png',bbox_inches='tight',pad_inches=.03);plt.close(fig)


def finish(m,out,candidate,index,meta,ledger):
    for p in m.parts:
        assert p['pdf_pages'] and all(1<=i<=index['pages'] for i in p['pdf_pages'])
        p.setdefault('source_refs',[]).insert(0,dict(source_id=index['primary_source_id'],pdf_pages=p['pdf_pages']))
    meta.update(external_sources=index['source_documents'],source_binder=index,detail_status='needs_detail',status_color='amber',model_scope='whole_crossing_exterior',assumptions=COMMON+meta.get('assumptions',[]))
    ledger.update(schema_version=1,bridge_id=m.bid,units='metres',detail_status='needs_detail',status_color='amber',primary_source_id=index['primary_source_id'],
        source_documents=index['source_documents'],assumptions=meta['assumptions'],source_page_policy=index['page_numbering'],fem_generated=False)
    dump(out/'source_ledger.json',ledger)
    manifest=m.save(out,meta)
    preview(m,out)
    record=dict(id=m.bid,workspace_enabled=True,name=candidate['name'],county=candidate['county'],waterway=('I-65 NB / I-70 EB' if m.bid=='virginia-avenue' else 'Branch of Little Blue River'),
        structure_id=candidate['structure_file'],designation=' / '.join(candidate['designations']),structure_type=candidate['structural_type'],latitude=candidate['latitude'],longitude=candidate['longitude'],
        location_source=dict(document='2025 NBI inventory',url=candidate['ownership_source'],note=candidate['coordinate_basis']+' No surveyed placement transform is embedded in the model.'),
        owner='INDOT',maintenance='INDOT',ownership_data_year=2025,nbi_ids=candidate['nbi_ids'],
        model=dict(thumbnail=f'bridges/{m.bid}/preview.png',glb=f'bridges/{m.bid}/model.glb',deck_length_m=m.length,spans=len(ledger['spans_m']),components=len(m.parts),
            revision='Proposed 2026 design with documented historical retention v1' if m.bid=='virginia-avenue' else 'Proposed 2026 replacement exterior v1',
            scope='Whole-crossing exterior reconstruction with explicit source-state and approximation boundaries.',detail_status='needs_detail',detail_status_note=meta['status_note']))
    dump(out/'registry_record.json',record)
    checks=json.loads((out/'geometry_verification.json').read_text())
    checks.update(primary_pdf_is_byte_identical=True,all_original_hashes_verified=True,primary_pdf_pages=index['pages'],source_documents=len(index['source_documents']),preview='preview.png')
    dump(out/'geometry_verification.json',checks)
    return manifest


def virginia():
    reviewed={'9683637':[1,31,32,33,34,35,36,37,38,39,41,43,44,45], '9548460':[24,25,28,32,33,50,51,52,53,55,60,61,62,63,64,65,66,67], '9548461':[1,2], '9715471':[1,2,3,4,5], '9715512':[1,2]}
    out,candidate,index=prepare('virginia-avenue','virginia_avenue','9683637',reviewed)
    span=114*FT;length=(120+7.625/12)*FT;width=64.5*FT;slab=8*IN;skew=44+19/60+6/3600;u0=-length/2;u1=length/2
    crown=5*FT;curbs=(-15*FT,25*FT);grade=lambda x:8.4-(.54/114)*np.asarray(x)
    m=Model('virginia-avenue',length,width,skew,grade,crossfall=.02,crown=crown)
    def surface(x,y):
        y=np.asarray(y)
        return grade(x)-.02*np.abs(np.clip(y,*curbs)-crown)+np.where(y<curbs[0],.019*(curbs[0]-y),np.where(y>curbs[1],.015*(y-curbs[1]),0))
    m.surface=surface;m.colors.update(girders='#748c95',steel='#8499a0',bracing='#83949b',rails='#dcd2b8',ornament='#829292')
    breaks=[curbs[0],crown,curbs[1]]
    m.add('deck','Proposed 2026 deck | single skew span','deck',slab_with_breaks(m,u0,u1,-width/2,width/2,slab,breaks),[31,36,37],
        'Dimensioned proposed floor; nominal crossfall and reconstructed grade','7.5 in structural depth plus 0.5 in integral wearing surface. Removed deck and overlay are excluded.',thickness_m=slab,structural_thickness_m=7.5*IN)
    for side,ya,yb,h in [(-1,-width/2,curbs[0],6*IN),(1,curbs[1],width/2,8*IN)]:
        paver=2.75*IN if side<0 else 0
        m.add(f'walk_{side}',f'{"South shared-use path" if side<0 else "North sidewalk"} supporting concrete','sidewalks',slab_with_breaks(m,u0,u1,ya,yb,h-paver,offset=h-paver),[31,37,43],
            'Dimensioned sidewalk and curb envelope','South nominal 16 ft 1 in clear path and north 6 ft 1 in clear sidewalk; rail and edge margins excluded from clear widths.',clear_width_m=(16+1/12 if side<0 else 6+1/12)*FT)
        if paver:
            m.add('trail_pavers','Reset Cultural Trail pavers and setting bed envelope','sidewalks',slab_with_breaks(m,u0,u1,ya+14*IN,yb,paver,offset=h),[37,43],
                '2.75 in paver and setting-bed envelope','Individual paver pattern is not fabricated.',thickness_m=paver)
    ys=np.array([-30.5,-23.75,-15.833333333333,-7.916666666667,0,7.916666666667,15.833333333333,23.75,30.5])*FT
    sections=[];beam_ids=[];clear=.05
    for j,y in enumerate(ys):
        zones=[];pieces=[]
        for q,(a,b) in enumerate([(-span/2-.375*FT,-span/2+20*FT),(-span/2+20*FT,span/2-20*FT),(span/2-20*FT,span/2+.375*FT)]):
            web=(54 if j==0 else 60)*IN;tw=.625*IN
            bf=(18 if q==1 else 16)*IN if j==0 else 20*IN
            tf=(2 if q==1 else 1.25)*IN if j==0 else (1.75 if q==1 else 1.25)*IN
            d=web+2*tf
            pieces.append(sweep(iform(d,bf,tw,tf),np.linspace(a,b,max(3,int((b-a)/.5))),lambda u,v,z,y=y,d=d:(m.sx(u,y),y+v,surface(m.sx(u,y),y)-slab-clear-d+z)))
            zones.append(dict(u0_m=max(a,-span/2),u1_m=min(b,span/2),web_depth_m=web,web_thickness_m=tw,flange_width_m=bf,flange_thickness_m=tf,total_depth_m=d))
        key=f'beam_{j+1}';beam_ids.append(key)
        m.add(key,f'Girder {j+1} | '+('2013 replacement exterior member' if j==0 else 'retained original plate girder'),'girders',concat(pieces),[31,34,36],
            'Source piecewise welded I-section; straight nominal grade envelope','Exact fabrication camber, small flange tapers and corrosion are not reconstructed.',y_m=float(y),section_zones=zones)
        refs(m,'9548460',[28] if j==0 else [65,66],[key])
        sections.append(dict(part_id=key,y_m=float(y),section_type='welded_I',zones=zones,source_refs=[dict(source_id='9548460',pdf_pages=[28] if j==0 else [65,66])]))
        # Concrete haunch closes the deliberate gap above the flange.
        maxbf=max(z['flange_width_m'] for z in zones)
        m.add(f'haunch_{j+1}',f'Girder {j+1} | nominal deck haunch','haunches',level_prism(m,-span/2,span/2,y-maxbf/2,y+maxbf/2,
            lambda x,v,y=y:surface(x,y)-slab-clear,lambda x,v:surface(x,v)-slab),[36,37],
            'Derived contact envelope','50 mm nominal haunch; source minimum fillet is 3/4 in. Actual variable screed and camber are unresolved.')
        for bi,u in enumerate([-span/2,span/2]):
            depth=zones[0 if bi==0 else -1]['total_depth_m'];bottom=surface(m.sx(u,y),y)-slab-clear-depth
            m.bearing(f'B{bi+1}_bearing_{j+1}',u,y,bottom,depth,[35] if bi==0 else [31,32],pad=(.45,.51,.12 if bi==0 else .10),plate=(.48,.56,.34 if bi==0 else .22),
                note='Abutment 1: proposed elastomer pad and HP14x89 bolster, simplified as stack. Abutment 2: retained fixed shoe envelope. Field dimension A and anchor hardware unresolved.')
        # Splice plates are exterior only; exact bolt grids deliberately omitted.
        for q,u in enumerate([-span/2+20*FT,span/2-20*FT]):
            x=m.sx(u,y);dep=zones[1]['total_depth_m'];zt=surface(x,y)-slab-clear;plates=[]
            for side in [-1,1]:
                vv=y+side*(tw/2+.008)
                plates.append(box(x-.60,x+.60,vv-.008,vv+.008,zt-dep+.08,zt-.08))
            m.add(f'splice_{j+1}_{q+1}',f'Girder {j+1} | splice {q+1} web cover plates','steel',concat(plates),[34],
                'Source 20/74/20 ft splice positions; representative cover plate envelope','Plate layers, fabrication bolt holes, exact 2013/1971 patterns and inner flange bars omitted.')
            refs(m,'9548460',[28,33] if j==0 else [65,66],[f'splice_{j+1}_{q+1}'])
    # Retain all bays. Interior X frames and the 2013 outer V-frame topology differ.
    frame_count=0
    for j,(ya,yb) in enumerate(zip(ys[:-1],ys[1:])):
        for q,u in enumerate(np.linspace(-span/2+15.25*FT,span/2-10.75*FT,5)):
            x=m.sx(u,(ya+yb)/2);z=min(surface(x,ya),surface(x,yb))-slab-clear-.14;bottom=z-4*FT
            a=np.array([x,ya+.02,z]);b=np.array([x,yb-.02,z]);c=a.copy();c[2]=bottom;d=b.copy();d[2]=bottom
            pieces=[rectangular_bar(c,d,.10,.10)]
            if j==0:
                mid=(c+d)/2;pieces.extend([rectangular_bar(a,mid,.127,.014),rectangular_bar(b,mid,.127,.014)])
            else:pieces.extend([rectangular_bar(a,b,.102,.0127),rectangular_bar(a,d,.102,.0127),rectangular_bar(b,c,.102,.0127)])
            key=f'cross_frame_{j+1}_{q+1}';m.add(key,f'Bay {j+1} | '+('V' if j==0 else 'X')+f' cross frame {q+1}','bracing',concat(pieces),[31,36],
                'Historical frame type and nominal 22 ft rows','Exact stagger varies by bay and is approximated. Angle legs are represented by rectangular strips; no structural area is inferred from mesh volume.')
            refs(m,'9548460',[28,32] if j==0 else [65,66],[key]);frame_count+=1
    # Retained wall abutments and hidden spread footing envelopes.
    for bi,u in enumerate([-span/2,span/2]):
        contacts=[c for c in m.contacts if c['id'].startswith(f'B{bi+1}_')];seat=min(c['seat_m'] for c in contacts)
        m.add(f'abutment_{bi+1}',f'Abutment {bi+1} | retained wall','abutments',m.transverse(u,4*FT,-width/2,width/2,.65,seat),[31,32,33,38],
            'Retained 4 ft wall envelope with constructed bearing-seat datum','Historical abutment wall and footing are retained; exact batter, wing angles and seat steps simplified.',normal_thickness_m=4*FT)
        refs(m,'9548460',[61,62] if bi==0 else [63,64],[f'abutment_{bi+1}'])
        for j,(y,c) in enumerate(zip(ys,contacts)):
            if c['seat_m']>seat+1e-6:m.add(f'seat_{bi+1}_{j+1}',f'Abutment {bi+1} | bearing seat riser {j+1}','abutments',m.transverse(u,.65,y-.36,y+.36,seat,c['seat_m']),[35,38],
                'Derived seat riser','Reconstructed to contact nominal shoe stack; not field survey.')
        m.add(f'footing_{bi+1}',f'Abutment {bi+1} | hidden spread footing envelope','foundations',m.transverse(u,17*FT,-width/2-.65,width/2+.65,0,.65),[31,32],
            'Historical nominal footing envelope','Exact eccentricity, toe and wing footing geometry omitted.')
        refs(m,'9548460',[61,62] if bi==0 else [63,64],[f'footing_{bi+1}'])
        end=-1 if bi==0 else 1
        m.add(f'mudwall_{bi+1}',f'Abutment {bi+1} | reconstructed mudwall and ledge','abutments',level_prism(m,u+end*.65-.15,u+end*.65+.15,-width/2,width/2,
            lambda x,y:seat,lambda x,y:surface(x,y)-slab),[38],'Source reconstructed mudwall topology; simplified ledge')
        for side in [-1,1]:
            edge=side*width/2;x=m.sx(u,edge);a,b=sorted([x,x+end*20*FT])
            m.add(f'wing_{bi+1}_{side}',f'Abutment {bi+1} | retained wing envelope {side}','abutments',box(a,b,edge-.18,edge+.18,.65,seat-.25),[31,32],
                'Historical wing presence; approximate 20 ft parallel envelope','Source wings are splayed and battered. Their exact plan and top profile remain incomplete.')
    # Type TX rail panels with actual schematic window openings and south metal cap rail.
    for side in [-1,1]:
        edge=side*(width/2-2*IN);walkh=(6 if side<0 else 8)*IN
        for panel,(a,b) in enumerate(zip(np.linspace(u0,u1,6)[:-1],np.linspace(u0,u1,6)[1:])):
            h=32*IN;poly=Polygon([(a,0),(b,0),(b,h),(a,h)],holes=[[(v-.13,.18),(v+.13,.18),(v+.13,.59),(v,.68),(v-.13,.59)] for v in np.arange(a+.5,b-.25,1.5*FT)])
            g=tm.creation.extrude_polygon(poly,12*IN,engine='earcut');vv=g.vertices.copy();uu=vv[:,0];zz=vv[:,1];yy=edge-side*vv[:,2];xx=m.sx(uu,yy);g.vertices=np.column_stack([xx,yy,surface(xx,yy)+walkh+zz])
            m.add(f'TX_rail_{side}_{panel}',f'Type TX rail | side {side} panel {panel+1}','rails',g,[31,37,39],
                'Dimensioned rail extent and window rhythm; nominal window profile','32 in nominal concrete rail above sidewalk. Exact mold recesses, fillets, pilasters and window curves simplified.')
        if side<0:
            members=[];yy=edge-6*IN
            for u in np.linspace(u0+.25,u1-.25,25):
                x=m.sx(u,yy);z=surface(x,yy)+walkh+32*IN;members.append(rod([x,yy,z],[x,yy,z+.23],.025))
            xx=[m.sx(u,yy) for u in [u0,u1]];zz=[surface(x,yy)+walkh+32*IN+.23 for x in xx];members.append(rod([xx[0],yy,zz[0]],[xx[1],yy,zz[1]],.025))
            m.add('ornamental_rail','Reset south aluminum ornamental top rail','ornament',concat(members),[39], 'Source south-only rail; simplified round members','25 post locations follow the 24-space elevation rhythm approximately; exact metal profile and anchorage omitted.')
    # Both approach envelopes terminate square in station, matching the primary plan.
    for bi,end,alen in [(1,-1,15.75*FT),(2,1,20.5*FT)]:
        inner=end*length/2;outer=inner+end*alen;parts=[]
        # Use a transverse-variable end coordinate to retain a skew inner end and square outer end.
        xouter=min(m.sx(inner,-width/2),m.sx(inner,width/2))-alen if end<0 else max(m.sx(inner,-width/2),m.sx(inner,width/2))+alen
        yy=sorted([-width/2,*breaks,width/2]);profile=[(y,-12*IN) for y in yy]+[(y,0) for y in reversed(yy)]
        g=sweep(profile,np.linspace(0,1,45),lambda t,y,z:(m.sx(inner,y)*(1-t)+xouter*t,y,surface(m.sx(inner,y)*(1-t)+xouter*t,y)+z))
        m.add(f'approach_{bi}',f'Abutment {bi} | proposed reinforced approach slab','approaches',g,[31,41,43],
            'Source minimum approach length with square terminal edge','12 in nominal depth; exact local transition extensions and terminal joint shapes simplified.',minimum_length_m=alen,thickness_m=12*IN)
        m.add(f'joint_{bi}',f'Abutment {bi} | Type IA joint line','joints',slab_with_breaks(m,inner-.012,inner+.012,-width/2,width/2,.06,breaks),[38,41], 'Schematic 24 mm joint strip; installation gap unresolved')
    # Six source-count light bollards and a single illustrated abutment 2 drain system.
    y=curbs[0]-2.5*FT
    for i,u in enumerate(np.linspace(u0+.8,u1-.8,6)):
        x=m.sx(u,y);z=surface(x,y)+6*IN
        g=concat([rod([x,y,z],[x,y,z+.9],.08,16),rod([x,y,z+.9],[x,y,z+1.03],.13,16)])
        m.add(f'bollard_{i+1}',f'Reset Cultural Trail light bollard {i+1}','accessories',g,[31,37], 'Source six-count; nominal housing and evenly distributed positions','Exact source lighting station offsets and fixture product geometry unresolved.')
    u=span/2-3*FT;y=curbs[0]+.2;x=m.sx(u,y);z=surface(x,y)
    drain=[box(x-.22,x+.22,y-.18,y+.18,z-.15,z+.015),rod([x,y,z-.1],[x,y,z-2.0],3*IN),rod([x,y,z-2],[m.sx(span/2,width/2),width/2,z-2.10],3*IN)]
    m.add('drain_abutment_2','Abutment 2 | SQ-A drain and 6 in collector envelope','drainage',concat(drain),[36,39],
        'Source drain/collector routing; nominal fittings','Collector is a straight visual run below the girders; elbows, hangers, cleanouts and deck penetrations are simplified.')
    m.checks=dict(spans_m=[span],support_lines=2,girder_lines=9,girder_segments=9,bearings=18,cross_frames=frame_count,girder_y_m=ys.tolist(),support_u_m=[-span/2,span/2],primary_pages_valid=True)
    m.cover('Whole single-span steel crossing','modeled_with_simplifications','Nine girders, 2026 deck, broad south path, narrow north sidewalk, all bays, both wall abutments and approach slabs.',[31,36,37,38,41],['deck','girders','haunches','bracing','abutments','approaches'])
    m.cover('Retained steel and bearings','modeled_with_simplifications','Piecewise 2013 girder 1 and original girders 2-9; splice covers, V/X frames and 18 bearing envelopes. Historical original PDF references are stored per component.',[31,34,35],['girders','steel','bracing','bearings'])
    m.cover('Rails, path, lights and drain','modeled_with_simplifications','TX windowed rail, south ornamental top rail, paver envelope, six light bollards and source drain collector.',[37,39,43],['rails','ornament','sidewalks','accessories','drainage'])
    m.cover('Unresolved geometry','not_modeled','Exact field seats and camber, bolts/gussets, splayed wings and local abutment batter, transition rail terminals, paver pattern, exact rail molds, buried utilities and surrounding interstate.',[31,35,39,41],[])
    state='Proposed 2026 deck/rail/approach replacement on retained 1971 original steel and 2013 girder 1 replacement'
    return finish(m,out,candidate,index,dict(title='Virginia Avenue over I-65 NB / I-70 EB | proposed 2026 rehabilitation',structure_id=candidate['structure_file'],designation='2200722',spans_m=[span],deck_thickness_m=slab,
        source_note='INDOT B-44576 primary 2026 design. Retained original framing and 2013 northbound girder replacement are sourced only from identified pages of document 9548460. Separate southbound/I-70, cathodic-protection and lighting pages are not dimensional authority. Original files remain unchanged.',
        status_note='Whole crossing present; amber because field elevations, wingwall shape, connections, rail/approach transitions and small fittings remain approximate. Proposed 2026 work is not proof of completion.',
        assumptions=['Linear grade through the primary bearing profile elevations replaces the 90/96 ft vertical curves; deck height is a local visualization datum.','Historical 54/60 in labels are WEB depths; total I-section depths include both flanges. Plate schedules are source-backed, but fillets and taper details are simplified.','Source revisions 9715471 and 9715512 concern special provisions and inspection coordination; no replacement geometry sheets were identified.']),
        dict(modeled_state=state,spans_m=[span],deck_length_m=length,deck_width_m=width,deck_thickness_m=slab,structural_deck_thickness_m=7.5*IN,skew_deg=skew,
            support_u_m=[-span/2,span/2],girder_y_m=ys.tolist(),girder_sections=sections,beam_part_ids=beam_ids,deck_part_ids=['deck'],
            source_pages=dict(general=31,deck=[36,37],bearings=35,rails=39,approaches=[41,43]),
            fem_topology=dict(type='single_span_composite_steel_girder_deck',coordinate_rule='x = u - tan(skew)*y; z up in native geometry',support_lines=[dict(id='B1',u_m=-span/2,kind='expansion',part_ids=[f'B1_bearing_{i+1}' for i in range(9)]),dict(id='B2',u_m=span/2,kind='fixed',part_ids=[f'B2_bearing_{i+1}' for i in range(9)])],
                continuity='Single simply supported span; fixed/expansion bearing behavior must be explicitly idealized by analysis.',sections=sections,
                sources=[dict(source_id='9683637',pdf_pages=[31,35,36,37]),dict(source_id='9548460',pdf_pages=[28,32,65,66])],
                analysis_assumptions_required=['Concrete/steel moduli and effective stiffness','Composite action and deck-shell offset','Diaphragm properties and exact stagger','Bearing translational/rotational restraints','Exclude approach slabs, rails and foundations from default deck pressure area'])))


def sr44():
    reviewed={'9683606':[1,12,13,14,15,16,17,18],'9552139':[],'9710491':[1,2,3,4,5,6,7,8]}
    out,candidate,index=prepare('sr44-little-blue','sr44_little_blue_branch','9683606',reviewed)
    span=30*FT;length=(31+10.625/12)*FT;width=43*FT;slab=20*IN;skew=45;u0=-length/2;u1=length/2
    def grade(x):
        t=150+np.asarray(x)/FT
        f=.00730*t+(-.00622-.00730)*t*t/(2*170)
        f0=.00730*150+(-.00622-.00730)*150*150/(2*170)
        return 3+(f-f0)*FT
    m=Model('sr44-little-blue',length,width,skew,grade,crossfall=.02)
    m.colors.update(deck='#c9cec6',rails='#d4ccbb')
    m.add('deck','Proposed 2026 reinforced concrete slab | 30 ft span','deck',m.slab(u0,u1,-width/2,width/2,slab),[12,13,14],
        'Dimensioned 43 ft wide, 20 in slab envelope','19.5 in structural depth plus 0.5 in integral wearing surface. Local north coping end notch and 5.25 in edge-length difference simplified; old 1941 bridge is excluded.',thickness_m=slab,structural_thickness_m=19.5*IN)
    support_us=[-span/2,span/2];pile_ys=(np.arange(8)-3.5)*8*FT*np.cos(np.radians(skew))
    for bi,u in enumerate(support_us):
        bottom=(870.97 if bi==0 else 870.83)*FT-(878.64*FT-3)
        caphalf=(2+10/12)*FT/2/m.c
        m.add(f'integral_bent_{bi+1}',f'Bent {bi+1} | integral concrete wall','abutments',level_prism(m,u-caphalf,u+caphalf,-width/2,width/2,
            lambda x,y,bottom=bottom:bottom,lambda x,y:m.surface(x,y)-slab),[14,15+bi,17],
            'Source 2 ft 10 in normal bent width and bottom elevation; top derived to contact slab','Integral slab-to-bent connection. No discrete bearings exist. Upper pavement ledge and local fillet are simplified.',normal_thickness_m=(2+10/12)*FT,bottom_m=bottom)
        # 8 pipe exterior envelopes at 8 ft spacing ALONG the skew bent, never across roadway.
        for j,y in enumerate(pile_ys):
            x=m.sx(u,y);tip=(841.97 if bi==0 else 839.83)*FT-(878.64*FT-3)
            m.add(f'pile_{bi+1}_{j+1}',f'Bent {bi+1} | hidden 14 in pipe pile envelope {j+1}','foundations',rod([x,y,tip],[x,y,bottom+2*FT],7*IN,20),[12,13,15+bi],
                'Source count, diameter, spacing and estimated tip elevation','Exterior closed envelope only: not a solid steel section. Nominal pipe wall is 0.25 in; actual driven lengths and soil springs are unknown.',diameter_m=14*IN,wall_thickness_m=.25*IN,estimated_tip_m=tip)
        end=-1 if bi==0 else 1
        for side in [-1,1]:
            edge=side*width/2;x=m.sx(u,edge);a,b=sorted([x,x+end*12*FT])
            # Wing faces are parallel to the road in plan; a representative source batter is retained.
            depth=grade(x)-.02*abs(edge)-bottom
            profile=[(0,0),(.3048,0),(.3048,depth),(0,depth)]
            g=sweep(profile,[a,b],lambda xx,v,z:(xx,edge+side*v,bottom+z))
            m.add(f'wing_{bi+1}_{side}',f'Bent {bi+1} | 12 ft wingwall {side}','abutments',g,[12,15+bi],
                'Source wing length and nominal 1 ft wall; simplified constant top','Wing A-D top elevations, 1:4 rear batter and local joints are approximate.',length_m=12*FT,top_thickness_m=FT)
    # The north rail has shorter constant FC length and longer TFC transitions.
    for side in [-1,1]:
        a,b=(u0,u1) if side<0 else (-(15+7.375/12)*FT/2,(15+7.375/12)*FT/2)
        edge=side*(width/2-2*IN);pr=[(0,0),(16*IN,0),(16*IN,10*IN),(10*IN,33*IN),(0,33*IN)]
        m.add(f'FC_rail_{side}',f'{"South" if side<0 else "North"} Type FC concrete rail','rails',sweep(pr,np.linspace(a,b,30),lambda u,v,z:(m.sx(u,edge-side*v),edge-side*v,m.surface(m.sx(u,edge-side*v),edge-side*v)+z)),[18],
            'Source 2 ft 9 in FC rail section and asymmetric lengths','Corners and fillets simplified.',height_m=33*IN,length_m=b-a,base_width_m=16*IN)
        for end,u in [(-1,a),(1,b)]:
            lengtht=(15+8/12)*FT;t0,t1=sorted([u,u+end*lengtht])
            m.add(f'TFC_{side}_{end}',f'Type TFC transition | side {side} end {end}','rails',sweep([(0,0),(16*IN,0),(16*IN,1),(0,1)],np.linspace(t0,t1,25),
                lambda uu,v,t:(m.sx(uu,edge-side*v),edge-side*v,m.surface(m.sx(uu,edge-side*v),edge-side*v)+t*(33*IN-.55*abs(uu-u)/lengtht))),[18],
                'Source 15 ft 8 in transition extent; nominal sloped solid envelope','Precise TFC mold, tapered curb, guardrail end plate and bolts unresolved.',length_m=lengtht)
    for bi,end in [(1,-1),(2,1)]:
        inner=end*length/2;alen=20.5*FT;xouter=min(m.sx(inner,-width/2),m.sx(inner,width/2))-alen if end<0 else max(m.sx(inner,-width/2),m.sx(inner,width/2))+alen
        # Source minimum length is along coping; far edge squared off to highway.
        pr=[(-width/2,-12*IN),(0,-12*IN),(width/2,-12*IN),(width/2,0),(0,0),(-width/2,0)]
        g=sweep(pr,np.linspace(0,1,35),lambda t,y,z:(m.sx(inner,y)*(1-t)+xouter*t,y,m.surface(m.sx(inner,y)*(1-t)+xouter*t,y)+z))
        m.add(f'approach_{bi}',f'Bent {bi} | proposed 12 in approach slab','approaches',g,[12,17,18],
            'Source 20 ft 6 in minimum length; square terminal reconstruction','Exact TFC slab extensions and terminal asphalt joints unresolved.',minimum_length_m=alen,thickness_m=12*IN)
        m.add(f'joint_{bi}',f'Bent {bi} | Type IA slab interface','joints',m.slab(inner-.012,inner+.012,-width/2,width/2,.06),[12,17],'Schematic Type IA joint strip; no structural bearing implied')
    # Rail transition attachments: simple external W-beam end runs and posts, not terminals.
    for side in [-1,1]:
        edge=side*(width/2-.20)
        for end in [-1,1]:
            start=end*(length/2+3.5);stop=start+end*2.0;aa,bb=sorted([start,stop]);members=[]
            for u in np.linspace(aa,bb,4):
                x=m.sx(u,edge);z=m.surface(x,edge);members.append(box(x-.055,x+.055,edge-.05,edge+.05,z-.25,z+.7))
            xs=[m.sx(uu,edge) for uu in [aa,bb]];zs=[m.surface(xx,edge)+.65 for xx in xs]
            members.append(rectangular_bar([xs[0],edge,zs[0]],[xs[1],edge,zs[1]],.06,.30))
            m.add(f'guardrail_{side}_{end}',f'Guardrail connection envelope | side {side} end {end}','accessories',concat(members),[12,18],
                'Source guardrail connection presence; representative exterior run','North-east TGB alignment and curved terminal are not fully reconstructed. Flat strip stands in for W profile.')
    m.checks=dict(spans_m=[span],support_lines=2,girder_lines=0,discrete_bearings=0,integral_end_bents=2,pile_count=16,piles_per_bent=8,pile_spacing_along_skew_m=8*FT,pile_y_m=pile_ys.tolist(),support_u_m=support_us,primary_pages_valid=True)
    m.cover('Whole single-span slab replacement','modeled_with_simplifications','Proposed 30 ft span, 43 ft wide slab, both integral bents, four wings and both approach slabs. The removed 1941 structure is not retained.',[12,13,14,15,16,17],['deck','abutments','approaches'])
    m.cover('Rails and visible accessories','modeled_with_simplifications','Asymmetric FC rail lengths, four TFC transition envelopes, joint strips and representative guardrail attachment runs.',[12,18],['rails','joints','accessories'])
    m.cover('Design foundations','modeled_with_simplifications','Two rows of eight 14 in pipe pile exterior envelopes; 8 ft spacing is measured along the 45 degree support line. Hidden by default.',[12,13,15,16],['foundations'])
    m.cover('Unresolved geometry','not_modeled','Rebar and internal pile material, actual driven lengths, soil and rock, riprap, local slab notch, wing batter, pavement ledge details, exact FC/TFC fillets and roadway terminals.',[12,14,15,16,17,18],[])
    return finish(m,out,candidate,index,dict(title='SR 44 over Branch of Little Blue River | proposed 2026 slab replacement',structure_id='044-73-10858',designation='2200652',spans_m=[span],deck_thickness_m=slab,
        source_note='INDOT B-44483 proposed 2026 replacement, document 9683606. The separate 68-page old-plan bundle 9552139 is preserved for provenance but supplies no replacement dimensions. Revision 9710491 changes traffic-control pay quantities, not structural geometry.',
        status_note='Whole proposed replacement crossing present. Amber: local notches, wing batter, approach transitions, terrain and actual pile behavior remain incomplete. Not an as-built or completed-construction claim.',
        assumptions=['The source title calls the deck simple-span while the bents are explicitly integral; an FE boundary model must state its rotational idealization and may not silently invent discrete bearings.','Vertical curve uses the source 170 ft curve, +0.730%/-0.622% slopes and nominal PVI station 507+10; absolute height is shifted to a 3 m local datum.','Foundation cylinders show exterior envelopes only. Pipe wall thickness and estimated tip elevations are source values, not verified as-driven geometry.']),
        dict(modeled_state='Proposed 2026 replacement only',spans_m=[span],deck_length_m=length,deck_width_m=width,deck_thickness_m=slab,structural_deck_thickness_m=19.5*IN,skew_deg=skew,
            support_u_m=support_us,girder_y_m=[],girder_sections=[],beam_part_ids=[],deck_part_ids=['deck'],source_pages=dict(general=12,slab=[13,14],bents=[15,16,17],rails=18),
            fem_topology=dict(type='single_span_reinforced_concrete_slab',coordinate_rule='x = u - tan(45 deg)*y; z up in native geometry',
                deck=dict(part_id='deck',width_m=width,length_m=length,structural_thickness_m=19.5*IN,total_thickness_m=slab),
                support_lines=[dict(id=f'B{i+1}',u_m=u,kind='integral_bent',part_id=f'integral_bent_{i+1}',pile_y_m=pile_ys.tolist()) for i,u in enumerate(support_us)],
                continuity='Monolithic slab-to-bent connection in drawings; single-span title. Any simple-support deck-only demonstration is an explicit analytical approximation.',
                sources=[dict(source_id='9683606',pdf_pages=[12,13,14,15,16,17])],
                analysis_assumptions_required=['Concrete modulus, Poisson ratio and cracking/effective stiffness','Rotational restraint of integral bents','Pile and soil stiffness if included','No beam lines or discrete bearings in the source slab topology','Exclude approach slabs/rails from default deck pressure area'])))


if __name__=='__main__':
    import sys
    targets={'virginia':virginia,'sr44':sr44}
    for name in sys.argv[1:] or targets:targets[name]()

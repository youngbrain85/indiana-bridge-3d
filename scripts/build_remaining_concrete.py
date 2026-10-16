"""Whole-crossing visualization assets for the remaining two concrete bridges.

Sources are copied byte-for-byte from the October 15 local candidate collection.
No database, registry, shared helper or analytical solver is changed by this script.
Native geometry: X along increasing station/east, Y toward the drawing south,
Z up. Skew signs use bridge_geometry.Model; geographic rotation is not applied.
"""
from pathlib import Path
import json
import shutil
import numpy as np
import trimesh as tm
from shapely.geometry import Polygon
from bridge_geometry import Model, FT, IN, box, sweep, rod, concat, iform, sha

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parents[1]
SOURCE = WORKSPACE / 'outputs/indiana_bridge_candidates/additional_20261015'
BASE = ROOT / 'data/bridges'
AMBER = '#c59a54'
COMMON = [
    'Exterior visualization reconstruction of the named design state, not an as-built survey, structural rating or validated finite-element mesh.',
    'No internal reinforcement, prestressing strands, embedded anchors or fabrication holes. Colors identify visualization layers; amber parts identify explicit approximations.',
    'Source PDF page references always address drawings.pdf, an unchanged issued PDF. Supplemental historical pages are separately identified by document ID and local file.',
    'Constructed interfaces and bearing contact checks establish geometric attachment only. Surveyed seats, actual camber, shim thicknesses and installed tolerances remain unknown.',
    'Site terrain, channel solids, riprap individual stones, buried pile tips, full roadside guardrail terminals and nonstructural utility routing are omitted.',
]


def dump(path, data):
    path.write_text(json.dumps(data, indent=2), encoding='utf8')


def prepare(bid, candidate_id, primary_id):
    out = BASE / bid
    (out / 'sources').mkdir(parents=True, exist_ok=True)
    candidates = json.loads((SOURCE / 'candidates.json').read_text(encoding='utf8'))['candidates']
    candidate = next(c for c in candidates if c['id'] == candidate_id)
    docs = []
    for s in candidate['documents'] + candidate.get('revision_notices', []):
        src = SOURCE / s['local_path']
        dest = out / 'sources' / src.name
        shutil.copyfile(src, dest)
        assert sha(src) == sha(dest) == s['sha256']
        is_primary = s['document_id'] == primary_id
        if is_primary:
            shutil.copyfile(src, out / 'drawings.pdf')
            assert sha(out / 'drawings.pdf') == s['sha256']
        docs.append(dict(id=s['document_id'], title=s['title'], url=s['url'],
            local_file='sources/' + src.name, sha256=s['sha256'], original_pages=s['pages'],
            role='primary_issued_pdf' if is_primary else 'supplementary_original',
            primary_pdf_start_page=1 if is_primary else None))
    index = dict(primary_pdf='drawings.pdf', primary_document_id=primary_id,
        pages=next(s['original_pages'] for s in docs if s['id'] == primary_id),
        sha256=sha(out / 'drawings.pdf'), source_documents=docs,
        note='Primary drawings.pdf is byte-for-byte identical to the issued source; no combined or newly authored PDF. Supplemental page numbers do not address the primary PDF.')
    dump(out / 'source_index.json', index)
    return out, candidate, index


def approximate(m, key, name, layer, mesh, pages, note, **dims):
    original = m.colors[layer]
    m.colors[layer] = AMBER
    m.add(key, name, layer, mesh, pages, 'Approximate external envelope', note, **dims)
    m.colors[layer] = original
    m.parts[-1]['approximation'] = True


def supplementary(m, pages, note):
    m.parts[-1]['supplementary_sources'] = [dict(document_id='9548292',
        local_file='sources/existing_plans_9548292.pdf', pdf_pages=pages, detail=note)]


def haunch(m, key, a, b, y, width, slab, clear, pages, skew_ends=False):
    # Top precisely meets the soffit and bottom follows the modeled girder top.
    def xyz(u, v, t):
        x = m.sx(u, y+v if skew_ends else y)
        bot = m.surface(x, y)-slab-clear
        return (x, y+v, bot*(1-t)+(m.surface(x,y+v)-slab)*t)
    approximate(m, key, key.replace('_',' '), 'haunches',
        sweep([(-width/2,0),(width/2,0),(width/2,1),(-width/2,1)],
              np.linspace(a,b,max(3,int((b-a)/.5))), xyz), pages,
        'Derived contact envelope. Nominal clearance, camber and fabrication screed geometry are approximated.',
        nominal_center_clearance_m=clear, width_m=width)


def solid_beam(m, key, name, a, b, y, profile, slab, clear, pages, note, skew_ends=False):
    d = max(p[1] for p in profile)
    m.add(key, name, 'girders', sweep(profile,np.linspace(a,b,max(3,int((b-a)/.5))),
        lambda u,v,z:(m.sx(u,y+v if skew_ends else y), y+v,
            m.surface(m.sx(u,y+v if skew_ends else y),y)-slab-clear-d+z)), pages,
        'Dimensioned source section; nominal straight profile', note,
        depth_m=d, length_m=b-a, section_profile_yz_m=profile)


def ring_prism(outer, inner, a, b, fn):
    poly = Polygon(outer, [inner])
    geom = tm.creation.extrude_polygon(poly, b-a, engine='earcut')
    geom.vertices = np.array([fn(a+t,v,z) for v,z,t in geom.vertices])
    geom.fix_normals(multibody=True)
    return geom


def approach(m, end, width, min_length, thick, pages, key=None):
    # Drawing approach slabs transition from skew near edge to square far edge.
    key = key or f'approach_{end}'
    near = end*(m.length/2+.025)
    far = end*(m.length/2+.025+abs(m.k)*width/2+min_length)
    profile = [(-width/2,0),(width/2,0),(width/2,1),(-width/2,1)]
    mesh = sweep(profile,np.linspace(0,1,24),lambda t,y,h:(
        (1-t)*m.sx(near,y)+t*far,y,
        m.surface((1-t)*m.sx(near,y)+t*far,y)-thick+h*thick))
    m.add(key, f'{"West" if end<0 else "East"} approach slab', 'approaches',mesh,pages,
        'Dimensioned minimum length, width and thickness; skew-to-square plan',
        'Narrow corner curb and transition extensions are separate approximate envelopes.',
        min_length_m=min_length,width_m=width,thickness_m=thick)
    return near, far


def rail(m,key,a,b,side,pages,height=.8382,base=.4064,top=.2286,approx=False,end_height=None,start_height=None,vertical_offset=0):
    edge=side*(m.width/2-.05)
    profile=[(0,0),(base,0),(base,.1778),(top,height),(0,height)]
    def xyz(u,v,z):
        y=edge-side*v
        h0=height if start_height is None else start_height
        h1=height if end_height is None else end_height
        scale=(h0+(h1-h0)*(u-a)/(b-a))/height
        return m.sx(u,y),y,m.surface(m.sx(u,y),y)+vertical_offset+z*scale
    mesh=sweep(profile,np.linspace(a,b,max(3,int((b-a)/.5))),xyz)
    if approx:
        approximate(m,key,key.replace('_',' '),'rails',mesh,pages,
            'Source transition topology; nominal sloped barrier envelope. Moldings, recesses, anchorage and end hardware are unresolved.',height_m=height,base_width_m=base)
    else:
        m.add(key,key.replace('_',' '),'rails',mesh,pages,
            'Source nominal concrete barrier envelope; profile corners simplified',height_m=height,base_width_m=base)


def support_ledger(m, us, ys, support_type):
    result=[]
    for i,u in enumerate(us):
        result.append(dict(id=f'support_{i+1}',u_m=float(u),
            x_by_girder_m=[float(m.sx(u,y)) for y in ys],
            girder_y_m=[float(y) for y in ys],type=support_type[i],
            source_topology=True,
            analysis_caution='Geometric support station is source-backed; analytical restraints, rotational fixity and material stiffness require explicit assumed inputs.'))
    return result


def finish(m, out, candidate, index, meta, ledger):
    meta.update(external_sources=index['source_documents'],source_index=index,
        completeness='Whole crossing reconstructed with unresolved detail (amber)',
        detail_status='needs_detail',
        assumptions=COMMON+meta.get('assumptions',[]))
    for p in m.parts:
        assert p['pdf_pages'] and all(1<=q<=index['pages'] for q in p['pdf_pages'])
    ledger.update(units='metres',axes='X increasing station, Y drawing south, Z up; not geographically rotated',
        source_documents=index['source_documents'],primary_pdf_pages=index['pages'],
        detail_status='needs_detail',geometry_only=True,
        analytical_use='This ledger describes display geometry and source evidence. A solver must freeze its own materials, section assumptions, connectivity, boundary conditions and pressure cases.',
        member_ids=[p['id'] for p in m.parts if p['layer']=='girders'],
        approximate_part_ids=[p['id'] for p in m.parts if p.get('approximation')],
        omissions=[c for c in m.coverage if c['status']=='not_modeled'])
    section=ledger['girder_section']
    section_polygon=Polygon(section['outer_profile_yz_m'],section['inner_void_profiles_yz_m'])
    section['nominal_net_area_m2']=section_polygon.area
    section['profile_centroid_yz_m']=[section_polygon.centroid.x,section_polygon.centroid.y]
    dump(out/'source_ledger.json',ledger)
    manifest=m.save(out,meta)
    verification=json.loads((out/'geometry_verification.json').read_text())
    reopened=tm.load(out/'model.glb',force='scene',process=False)
    bearing_errors=[]
    for contact in verification['contacts']:
        bounds=reopened.geometry[contact['id']].bounds
        bearing_errors.extend([abs(float(bounds[1,1])-contact['bearing_top_m']),
            abs(float(bounds[0,1])-contact['seat_m'])])
    assert max(bearing_errors+[0])<1e-5
    verification.update(primary_pdf_unchanged=True,
        source_original_hashes_match=True,source_page_references_within_primary=True,
        approximate_component_count=len(ledger['approximate_part_ids']),
        actual_exported_bearing_bounds_max_error_m=max(bearing_errors+[0]),
        nominal_girder_section_net_area_m2=section_polygon.area,
        nominal_section_area_is_not_solid_bounding_rectangle=True,
        source_review='Key general, framing, section, bearing, support and approach sheets were rendered and visually read before construction. See source_ledger.json evidence entries.')
    dump(out/'geometry_verification.json',verification)
    record=dict(id=m.bid,workspace_enabled=True,name=candidate['name'],county=candidate['county'],
        waterway='Deer Creek' if m.bid=='us35-deer' else 'Eight Mile Creek',
        structure_id=candidate['structure_file'],designation=candidate['designations'][0],
        structure_type=candidate['structural_type'],latitude=candidate['latitude'],longitude=candidate['longitude'],
        location_source=dict(document='2025 FHWA NBI',url=candidate['ownership_source'],
            note=candidate['coordinate_basis']+' The GLB uses local axes and is not georeferenced.'),
        owner='INDOT',maintenance='INDOT',nbi_ids=candidate['nbi_ids'],ownership_data_year=2025,
        ownership_note=candidate['ownership_basis'],
        model=dict(glb=f'bridges/{m.bid}/model.glb',deck_length_m=m.length,deck_width_m=m.width,
            spans=1,components=len(m.parts),revision='Whole-crossing exterior geometry v1',
            scope=ledger['modeled_state'],detail_status='needs_detail',
            detail_status_note='Whole crossing is represented. Amber details use explicit approximations; field seats, exact camber, transition hardware and site geometry remain unresolved. Not an as-built model.'))
    dump(out/'registry_record.json',record)
    return manifest


def deer():
    out,candidate,index=prepare('us35-deer','us35_deer_creek','9721578')
    span=115*FT;length=(117+5/12)*FT;width=(38+4/12)*FT
    slab=8*IN;clear=.075;depth=48*IN
    us=np.array([-span/2,span/2]);ys=np.linspace(-15.25*FT,15.25*FT,4)
    m=Model('us35-deer',length,width,15,lambda x:(853.07-837.11)*FT+.0235*np.asarray(x),crossfall=.02)
    m.colors.update(girders='#b8b6a6',steel='#7b8993',bearings='#65727c')
    # BT48x49 dimensions transcribed from source p.20, without 3/4 in bottom chamfers.
    profile_in=[(-20,0),(20,0),(20,5.5),(6,12.5),(4,14.5),(4,37),(7,40),
        (24.5,43),(24.5,48),(-24.5,48),(-24.5,43),(-7,40),(-4,37),(-4,14.5),(-6,12.5),(-20,5.5)]
    profile=[(y*IN,z*IN) for y,z in profile_in]
    a,b=-(116.5*FT)/2,(116.5*FT)/2
    m.add('deck','Proposed 2026 continuous deck','deck',m.slab(-length/2,length/2,-width/2,width/2,slab),[11,12,21,22],
        'Dimensioned exterior slab; 7.5 in structural depth plus 0.5 in sacrificial surface',
        length_m=length,width_m=width,thickness_m=slab)
    for j,y in enumerate(ys):
        solid_beam(m,f'beam_0_{j}',f'BT48x49 beam {j+1} | proposed 2026',a,b,y,profile,slab,clear,[18,19,20],
            '48 in depth, 49 in top flange, 40 in bottom flange, 8 in web; 116 ft 6 in beam length. Bottom chamfers, end copes and actual camber omitted.')
        haunch(m,f'haunch_0_{j}',a,b,y,49*IN,slab,clear,[12,20,24])
        for bi,u in enumerate(us):
            bottom=m.surface(m.sx(u,y),y)-slab-clear-depth
            # p.17 steel plates/S3x7.5: displayed outside shape, with nominal leveling plate.
            stack=(7.375 if bi==0 else 7.125)*IN
            x=m.sx(u,y)
            pieces=[box(x-4.5*IN,x+4.5*IN,y-26*IN,y+26*IN,bottom-stack,bottom-stack+IN),
                box(x-3*IN,x+3*IN,y-22*IN,y+22*IN,bottom-(1.375 if bi==0 else 1.125)*IN,bottom),
                sweep(iform(3*IN,2.5*IN,.23*IN,.26*IN),[-20*IN,20*IN],lambda v,t,z:(x+t,y+v,bottom-stack+IN+z))]
            # A solid nominal leveling strip fills the unresolved steel-stack interface.
            pieces.append(box(x-3*IN,x+3*IN,y-22*IN,y+22*IN,bottom-stack+4*IN,bottom-(1.375 if bi==0 else 1.125)*IN))
            approximate(m,f'B{bi+1}_bearing_{j+1}',f'Bent {bi+1} steel bearing assembly {j+1}','bearings',concat(pieces),[17],
                'Dimensioned source plates and S3x7.5 concept, with nominal leveling envelope. Assembly is embedded in an integral end bent; it does not establish a free rotational analytical bearing.',
                stack_height_m=stack,base_plate_length_m=9*IN,base_plate_width_m=52*IN)
            m.contacts.append(dict(id=f'B{bi+1}_bearing_{j+1}',girder_bottom_m=float(bottom),bearing_top_m=float(bottom),seat_m=float(bottom-stack)))
    # One intermediate channel row; p.12 says MC18x42.7 while p.18 labels MC12x42.7.
    for j,(ya,yb) in enumerate(zip(ys[:-1],ys[1:])):
        u=0.;y0=ya+4*IN;y1=yb-4*IN
        x0=m.sx(u,(ya+yb)/2)
        pr=[(0,0),(.105,0),(.105,.016),(.011,.016),(.011,.441),(.105,.441),(.105,.4572),(0,.4572)]
        z=min(m.surface(x0,ya),m.surface(x0,yb))-slab-clear-.72
        approximate(m,f'diaphragm_0_{j}',f'Midspan steel diaphragm bay {j+1}','diaphragms',
            sweep(pr,[y0,y1],lambda y,v,h:(x0+v,y,z+h)),[12,18,22],
            'Source has one staggered midpoint row. 18 in channel depth follows typical section; framing label MC12x42.7 conflicts. Exact channel, attachments and stagger are unresolved.',depth_m=.4572)
    for bi,u in enumerate(us):
        end=-1 if bi==0 else 1
        contacts=[c for c in m.contacts if c['id'].startswith(f'B{bi+1}_')]
        seat=min(c['seat_m'] for c in contacts)
        bottom=((841.88 if bi==0 else 844.59)-837.11)*FT
        capy=43*FT*m.c/2
        m.add(f'cap_{bi+1}',f'Bent {bi+1} lower integral cap','abutments',m.transverse(u,46*IN,-capy,capy,bottom,seat),[13,14,15],
            'Dimensioned 43 ft skew cap length, 3 ft 10 in normal thickness and base elevation; nominal common seat',
            'Individual modeled bearing risers fit the nominal girder line; exact source seat stepping and upper infill shapes are simplified.',normal_width_m=46*IN,skew_length_m=43*FT)
        for j,(y,c) in enumerate(zip(ys,contacts)):
            if c['seat_m']>seat+1e-5:
                approximate(m,f'pedestal_{bi}_{j}',f'Bent {bi+1} derived seat riser {j+1}','bearings',
                    m.transverse(u,9*IN,y-27*IN,y+27*IN,seat,c['seat_m']),[14,17],
                    'Pedestal elevation derived to close the bearing-to-cap interface; not surveyed.')
        # Integral closure between flanges and outer beam lines, rather than a fictitious air gap.
        edges=[-capy]+[v for y in ys for v in [y-24.5*IN,y+24.5*IN]]+[capy]
        for j in range(0,len(edges)-1,2):
            y0,y1=edges[j],edges[j+1]
            mesh=sweep([(y0,0),(y1,0),(y1,1),(y0,1)],[-.38,.38],
                lambda t,y,h:(m.sx(u+t,y),y,seat*(1-h)+(m.surface(m.sx(u+t,y),y)-slab)*h))
            approximate(m,f'integral_infill_{bi}_{j}',f'Bent {bi+1} integral closure bay {j//2+1}','abutments',mesh,[14,15],
                'Source integral closure topology. Nominal vertical infill avoids false isolated end bearings; local flange copes and concrete keys are omitted.')
        # Back face of integral bent behind the square beam ends.
        mesh=sweep([(-capy,0),(capy,0),(capy,1),(-capy,1)], sorted([u+end*.39,u+end*.60]),
            lambda t,y,h:(m.sx(t,y),y,seat*(1-h)+(m.surface(m.sx(t,y),y)-slab)*h))
        approximate(m,f'backwall_{bi}',f'Bent {bi+1} integral back face','abutments',mesh,[13,15],
            'Nominal rear closure strip. Skew beam-end copes and ledge details are unresolved.')
        for j,y in enumerate(np.linspace(-19.375*FT*m.c,19.375*FT*m.c,6)):
            x=m.sx(u,y)
            approximate(m,f'pile_stub_{bi}_{j}',f'Bent {bi+1} HP12x53 pile stub {j+1}','foundations',
                sweep(iform(12*IN,12*IN,.435*IN,.435*IN),[bottom-1.5,bottom],lambda z,v,w:(x+v,y+w-6*IN,z)),[11,13,14],
                'Six source HP12x53 piles per bent. Nominal profile and 1.5 m display stub only; driven tip depth is not modeled.',display_length_m=1.5)
        for side in [-1,1]:
            y=side*(capy-.5*FT);aa,bb=sorted([u,u+end*12*FT])
            approximate(m,f'wing_{bi}_{side}',f'Bent {bi+1} wing wall {side}','abutments',
                sweep([(-.5*FT,0),(.5*FT,0),(.5*FT,1),(-.5*FT,1)],[aa,bb],
                    lambda t,v,h:(m.sx(t,y+v),y+v,bottom*(1-h)+(m.surface(m.sx(t,y+v),y+v)-.09)*h)),[13,17],
                '12 ft long, 1 ft thick source wings; plan flare and top elevation transitions simplified.',length_m=12*FT,thickness_m=FT)
        x=m.sx(u+end*.7,0)
        approximate(m,f'end_bent_drain_{bi}',f'Bent {bi+1} 6 in drain envelope','drainage',rod([x,-capy,seat-.4],[x,capy,seat-.4],3*IN),[11,15],
            'Source diameter; schematic transverse run. Outlets, bends and backfill collection are unresolved.',diameter_m=6*IN)
    main=(102+4.375/12)*FT
    for side in [-1,1]:
        rail(m,f'FC_rail_{side}',-main/2,main/2,side,[23],base=16*IN,top=9*IN)
        for end in [-1,1]:
            aa,bb=sorted([end*main/2,end*(main/2+15.667*FT)])
            rail(m,f'TFC_transition_{end}_{side}',aa,bb,side,[11,23,25],approx=True,
                start_height=.70 if end<0 else .8382,end_height=.70 if end>0 else .8382)
    for end in [-1,1]:
        approach(m,end,(35+11/12)*FT,20.5*FT,FT,[11,25])
        u=end*length/2
        m.add(f'joint_{end}','Type IA approach interface','joints',m.slab(u-.012,u+.012,-width/2,width/2,.06),[15,25],
            'Schematic 24 mm visual joint strip; not an installation opening')
        for side in [-1,1]:
            aa,bb=sorted([end*length/2,end*(main/2+15.667*FT)])
            yy=sorted([side*(35+11/12)*FT/2,side*(width/2)])
            approximate(m,f'extension_{end}_{side}',f'Approach transition slab extension {end}/{side}','approaches',
                m.slab(aa,bb,yy[0],yy[1],FT),[23,25],
                'Nominal local transition support extension. Exact corner extension limits and integral curb returns remain unresolved.')
    m.cover('Whole proposed Bulb-T crossing','modeled_with_simplifications','One 115 ft bearing span; all four dimensioned BT48x49 beams, 8 in deck, 15 degree right skew and full grade.',[11,12,18,20,22],['deck','girders','haunches'])
    m.cover('Integral support topology','approximate','Both integral bents, 8 embedded source steel bearing assemblies, infill, wings and 12 hidden pile display stubs. Seat attachment and end copes remain approximate.',[13,14,15,17],['abutments','bearings','foundations'])
    m.cover('External rails and approaches','modeled_with_simplifications','FC barrier, four approximate TFC transitions, skew-to-square approach slabs and nominal extension/drain envelopes.',[11,23,25],['rails','approaches','joints','drainage'])
    m.cover('Unresolved details','not_modeled','Actual girder camber, end copes, diaphragm designation conflict and exact stagger, buried pile tips, transition hardware, construction joints and site terrain.',[17,18,19,20,24,25],[])
    m.checks=dict(spans_m=[span],support_lines=2,girder_lines=4,girder_segments=4,bearings=8,
        integral_end_bents=2,source_piles_per_bent=6,girder_y_m=ys.tolist(),support_u_m=us.tolist(),skew_deg=15,
        beam_length_m=b-a,source_design_state='Proposed 2026 full replacement; construction not established')
    ledger=dict(modeled_state='Proposed 2026 full replacement, not the older NBI bridge and not asserted constructed',
        spans_m=[span],deck_length_m=length,deck_width_m=width,deck_thickness_m=slab,
        structural_deck_thickness_m=7.5*IN,wearing_surface_m=.5*IN,
        girder_y_m=ys.tolist(),girder_lines=4,spacing_m=(10+2/12)*FT,
        support_u_m=us.tolist(),skew_deg=15,skew_direction='right',grade=.0235,crossfall=.02,
        supports=support_ledger(m,us,ys,['integral_end_bent_with_embedded_steel_assemblies']*2),
        girder_section=dict(type='BT48x49',depth_m=48*IN,top_width_m=49*IN,bottom_width_m=40*IN,web_thickness_m=8*IN,
            outer_profile_yz_m=profile,inner_void_profiles_yz_m=[],profile_basis='Dimensioned p.20 polygon, bottom chamfers omitted; nominal straight beam without camber',
            beam_length_m=b-a,beam_end_u_m=[a,b],nominal_haunch_m=clear),
        source_evidence=[dict(pages=[11,12],facts='115 ft span, 117 ft 5 in deck length, 38 ft 4 in coping width, +2.35 percent grade, 15 degree right skew, 8 in deck.'),
            dict(pages=[18,19,20,22],facts='Four beams at 10 ft 2 in, BT48x49 dimensioned shape, 116 ft 6 in beam length; one intermediate diaphragm row.'),
            dict(pages=[13,14,15,17],facts='Integral bents with source steel bearing assemblies, six HP12x53 piles per bent, 43 ft skew cap and 12 ft wings.'),
            dict(pages=[23,25],facts='FC rail section and 102 ft 4 3/8 in main rail length; 12 in approaches, 20 ft 6 in minimum and 35 ft 11 in width.')],
        unresolved=['MC18x42.7 on typical section versus MC12x42.7 on framing. Modeled approximate 18 in channel envelope.',
            'No surveyed screed/camber/seat fit. Nominal 75 mm center haunch and derived seat risers.',
            'Actual integral rotational restraint requires a dedicated soil/pile/end-bent model or explicit analytical idealization.'],
        analytical_member_mapping=[dict(member_id=f'beam_0_{j}',line_index=j,span_index=0,y_m=float(y),support_indices=[0,1],section='BT48x49') for j,y in enumerate(ys)])
    return finish(m,out,candidate,index,dict(title='US 35 over Deer Creek | proposed 2026 replacement',structure_id='035-27-10469',designation='1900048',
        spans_m=[span],deck_thickness_m=slab,
        source_note='Primary INDOT B-45063 / Des 1900048 proposed 2026 replacement, document 9721578. Source cover and plans describe a 115 ft new crossing; the associated 2025 NBI record describes the older 1931 bridge.',
        assumptions=['Local Z datum is the source flowline elevation 837.11 ft; geometry is not surveyed or georeferenced.',
            'Straight nominal girder lines use a 75 mm center haunch. Nominal integral-bent seats are derived for visual contact; real support rotational restraint is not inferred from bearing display meshes.']),ledger)


def eight():
    out,candidate,index=prepare('us224-eight-mile','us224_eight_mile','9683628')
    span=41*FT;length=(45+.5/12)*FT;width=(46+8/12)*FT
    remaining=7.5*IN;overlay=2*IN;slab=remaining+overlay;clear=.025;depth=21*IN
    us=np.array([-span/2,span/2]);ys=np.linspace(-19.375*FT,19.375*FT,6)
    # Source proposed grade = old grade +1.5 in after 0.5 in milling and 2 in overlay.
    m=Model('us224-eight-mile',length,width,-30,lambda x:(831.91-817)*FT+1.5*IN-.002*np.asarray(x),crossfall=.015625)
    m.colors.update(girders='#b3b4a6',accessories='#777f79')
    m.add('deck','Retained deck after nominal 0.5 in milling','deck',m.slab(-length/2,length/2,-width/2,width/2,remaining,-overlay),[8,9],
        'Source 7.5 in remaining concrete envelope','Localized hydrodemolition depth and full-depth patches depend on field conditions and are not invented.',thickness_m=remaining)
    m.add('overlay','Proposed 2026 minimum 2 in concrete overlay','deck',m.slab(-length/2,length/2,-22*FT,22*FT,overlay),[8,9],
        'Source minimum overlay envelope','Structural participation requires an explicit analytical assumption; the visual surface alone does not establish composite stiffness.',thickness_m=overlay)
    # Milling/overlay terminates at the clear roadway; retained rail bases sit on old copings.
    for side in [-1,1]:
        ya,yb=sorted([side*22*FT,side*width/2])
        m.add(f'retained_coping_{side}',f'Retained unmilled coping {side}','deck',
            m.slab(-length/2,length/2,ya,yb,.5*IN,-1.5*IN),[9],
            'Retained 8 in coping section reconstructed from 8 in existing slab',
            'Half-inch residual coping strip above the milled interior slab. Existing barrier bears here; its visible height above overlay is reduced by 1.5 in.',thickness_m=.5*IN)
    # Dimensioned 1985 CB21 main section: 48 x 21 in with chamfered 38 in void.
    # Void top=18 in, bottom=5.5 in, corner cuts=3 in. Minor top ridges omitted.
    outer=[(-24*IN,0),(24*IN,0),(24*IN,21*IN),(-24*IN,21*IN)]
    inner=[(-16*IN,5.5*IN),(16*IN,5.5*IN),(19*IN,8.5*IN),(19*IN,15*IN),
           (16*IN,18*IN),(-16*IN,18*IN),(-19*IN,15*IN),(-19*IN,8.5*IN)]
    blen=(41+11.875/12)*FT;a,b=-blen/2,blen/2;endblock=2.75*FT
    for j,y in enumerate(ys):
        def fn(u,v,z):
            x=m.sx(u,y+v)
            return x,y+v,m.surface(x,y)-slab-clear-depth+z
        shell=ring_prism(outer,inner,a+endblock,b-endblock,fn)
        solids=[sweep(outer,[a,a+endblock],fn),shell,sweep(outer,[b-endblock,b],fn)]
        m.add(f'beam_0_{j}',f'Retained CB21 hollow box beam {j+1}','girders',concat(solids),[9,11],
            'Historical dimensioned CB21 profile and primary retained-beam identification',
            'Supplement 9548292 p.8 controls 48 x 21 in section and skew ends. Hollow central profile preserved; nominal 2 ft 9 in solid end blocks, top ridges/chamfers and void-end taper simplified.',
            depth_m=depth,width_m=48*IN,length_m=blen,void_profile_yz_m=inner,endblock_length_m=endblock)
        supplementary(m,[8,9],'CB21 section, beam plan, six-line transverse spacing and diaphragm topology. Primary p.9 identifies these retained beams.')
        haunch(m,f'haunch_0_{j}',a,b,y,48*IN,slab,clear,[9],skew_ends=True)
        supplementary(m,[8,9],'Historical beam/slab camber note allows varying interface; nominal modeled 25 mm haunch is an explicit assumption.')
        for bi,u in enumerate(us):
            bottom=m.surface(m.sx(u,y),y)-slab-clear-depth
            original=m.colors['bearings'];m.colors['bearings']=AMBER
            m.bearing(f'B{bi+1}_bearing_{j+1}',u,y,bottom,depth,[8,11],pad=(.23,1.05,.045),plate=(.23,1.05,.005),
                note='Retained Type 7B elastomeric bearing from historical pp.8-9. 50 mm total display thickness and pad plan dimensions are assumed; the thin top envelope is not a claimed added steel plate.')
            m.colors['bearings']=original;m.parts[-1]['approximation']=True
            supplementary(m,[5,8,9],'Retained bearing type 7B, expansion at abutment 1 and fixed at abutment 2. Standard PB11 dimensional sheet is not included.')
            # 2026 wrapped beam ends, source minimum 3 ft; thin skins for display only.
            aa,bb=(a,a+3*FT) if bi==0 else (b-3*FT,b)
            t=.003
            profiles=[[(v,z) for v,z in [(-24*IN-t,-t),(24*IN+t,-t),(24*IN+t,0),(-24*IN-t,0)]],
                [(-24*IN-t,0),(-24*IN,0),(-24*IN,depth),(-24*IN-t,depth)],
                [(24*IN,0),(24*IN+t,0),(24*IN+t,depth),(24*IN,depth)]]
            approximate(m,f'beam_wrap_{bi}_{j}',f'Proposed beam-end wrap {bi+1}/{j+1}','accessories',
                concat([sweep(pr,[aa,bb],fn) for pr in profiles]),[8,11],
                'Source minimum 3 ft external wrap envelope. 3 mm thickness is a display convention; repair limits and final composite properties are unknown.',display_thickness_m=t,min_length_m=3*FT)
    # Concrete diaphragms in 1985 section: 8 in thick, 15 in nominal depth.
    for ri,u in enumerate([a+.4,0,b-.4]):
        for j,(ya,yb) in enumerate(zip(ys[:-1],ys[1:])):
            y0,y1=ya+24*IN,yb-24*IN
            def f(t,y,h):
                x=m.sx(u+t,y)
                z=m.surface(x,y)-slab-clear
                return x,y,z-15*IN+h*15*IN
            approximate(m,f'diaphragm_{ri}_{j}',f'Concrete diaphragm row {ri+1} bay {j+1}','diaphragms',
                sweep([(y0,0),(y1,0),(y1,1),(y0,1)],[-4*IN,4*IN],f),[9],
                'Historical concrete diaphragm topology, nominal 8 in by 15 in section. Source plan staggering and exact ends are simplified.',width_m=8*IN,depth_m=15*IN)
            supplementary(m,[8,9,10],'Concrete end and interior diaphragms. Primary p.9 shows retained beam/deck system only.')
    for bi,u in enumerate(us):
        end=-1 if bi==0 else 1
        contacts=[c for c in m.contacts if c['id'].startswith(f'B{bi+1}_')]
        seat=min(c['seat_m'] for c in contacts);capbot=seat-.55
        capy=width/2+.15
        approximate(m,f'cap_{bi+1}',f'Abutment {bi+1} retained cap','abutments',m.transverse(u,2.5*FT,-capy,capy,capbot,seat),[8,11],
            'Historical 2 ft 6 in cap width; top steps replaced by derived bearing risers. Lateral limits and old/new construction seams approximated.',normal_width_m=2.5*FT)
        supplementary(m,[5,6,7,9],'Widened abutment cap, retained stem and reconstructed wings; source old/new seams are not display material boundaries.')
        for j,(y,c) in enumerate(zip(ys,contacts)):
            if c['seat_m']>seat+1e-5:
                approximate(m,f'pedestal_{bi}_{j}',f'Abutment {bi+1} derived bearing riser {j+1}','bearings',
                    m.transverse(u,.35,y-.55,y+.55,seat,c['seat_m']),[8,11],
                    'Constructed seat riser; actual camber and shim elevations unresolved.')
        approximate(m,f'stem_{bi+1}',f'Abutment {bi+1} retained/widened stem','abutments',m.transverse(u,.70,-capy,capy,.05,capbot),[8],
            'Historical solid-stem topology; nominal 700 mm thickness and simplified widened outline. Field dimensions and existing concrete repairs unresolved.')
        supplementary(m,[4,5,6,7],'Retained and widened abutments on continuous shallow footings, not piles.')
        approximate(m,f'footing_{bi+1}',f'Abutment {bi+1} footing envelope','foundations',m.transverse(u,7*FT,-capy-.3,capy+.3,-.60,.05),[8],
            'Historical 7 ft footing width and roughly 2 ft thickness; approximate plan extent/elevation. Hidden by default; not a foundation design.',normal_width_m=7*FT)
        supplementary(m,[4,5,6],'Shallow footing envelopes; retained and widened portions are simplified to one geometric solid.')
        # Source reconstructed 1 ft mudwall, behind girder end without obstructing beam bearing.
        mu=end*(length/2-.5*FT)
        wall=sweep([(-width/2,0),(width/2,0),(width/2,1),(-width/2,1)],[-.5*FT,.5*FT],
            lambda t,y,h:(m.sx(mu+t,y),y,seat*(1-h)+m.surface(m.sx(mu+t,y),y)*h))
        approximate(m,f'mudwall_{bi+1}',f'Abutment {bi+1} reconstructed mudwall','abutments',wall,[11],
            'Source 1 ft reconstructed mudwall. Lower retained portion, ledge and local top return simplify the source detail.',normal_width_m=FT)
        for side in [-1,1]:
            y=side*capy;x=m.sx(u,y)
            axy=np.array([x,y]);bxy=axy+np.array([end*4.1,side*2.3])
            v=bxy-axy;normal=np.array([-v[1],v[0]])/np.linalg.norm(v)*.20
            xy=[axy-normal,bxy-normal,bxy+normal,axy+normal]
            wing=sweep([(float(px),float(py)) for px,py in xy],[0,1],
                lambda h,px,py:(px,py,.05*(1-h)+(m.surface(px,py)-.15)*h))
            approximate(m,f'wing_{bi}_{side}',f'Abutment {bi+1} flared wing {side}','abutments',wing,[8,10,12],
                'Source flared wing topology. Nominal 4.7 m length and 400 mm wall thickness; actual irregular old/new outlines, footings and rail returns remain unresolved.')
            supplementary(m,[5,6,7],'Flared widened wings. Exact historical dimensions and later partial removals require further reconciliation.')
    for side in [-1,1]:
        rail(m,f'retained_rail_{side}',-length/2,length/2,side,[9,12],height=33*IN,base=16*IN,top=9*IN,vertical_offset=-1.5*IN)
        # Three proposed TFC transitions; southwest existing guardrail is retained.
        for end in [-1,1]:
            if end==-1 and side==1: continue
            aa,bb=sorted([end*length/2,end*(length/2+15.667*FT)])
            rail(m,f'TFC_transition_{end}_{side}',aa,bb,side,[8,12,13,14],height=31.5*IN,approx=True,
                start_height=.70 if end<0 else 31.5*IN,end_height=.70 if end>0 else 31.5*IN)
            yy=sorted([side*(44+4/12)*FT/2,side*width/2])
            approximate(m,f'extension_{end}_{side}',f'TFC approach extension {end}/{side}','approaches',m.slab(aa,bb,yy[0],yy[1],FT),[12,13,14],
                'Source three transition extensions; nominal corner width and skew end boundaries.')
    for end in [-1,1]:
        approach(m,end,(44+4/12)*FT,20.5*FT,FT,[13,14,15])
        u=end*length/2
        m.add(f'PCF_joint_{end}',f'Abutment {1 if end<0 else 2} PCF joint envelope','joints',m.slab(u-.025,u+.025,-width/2,width/2,.08),[11],
            'Schematic 50 mm strip','Source existing nominal opening is 2 in west and 1 5/8 in east; temperature movement, gland and actual gaps not resolved.')
    # Retained mid-span drains only; end drains are filled in the proposed design.
    for side in [-1,1]:
        y=side*(22*FT-.03);x=m.sx(0,y);z=m.surface(x,y)
        approximate(m,f'midspan_drain_{side}',f'Retained midspan drain outlet {side}','drainage',rod([x,y,z-.28],[x,y+side*.35,z-.45],IN),[8,9],
            'Source 2 in retained drain diameter; outlet route and slab penetration schematic. All other existing deck drains are filled and omitted.',diameter_m=2*IN)
    m.cover('Whole retained box-beam crossing','modeled_with_simplifications','One 41 ft bearing span, six hollow CB21 beams at 7 ft 9 in, 30 degree left skew; 7.5 in remaining slab and separate proposed 2 in overlay.',[8,9,11],['deck','girders','haunches'])
    m.cover('Historical support and framing topology','approximate','Twelve retained Type 7B bearing envelopes, end/interior concrete diaphragms, both solid abutments, shallow footings and four flared wings. Historical source is explicitly supplemental.',[8,9,11],['bearings','diaphragms','abutments','foundations'])
    m.cover('2026 exterior repair design','modeled_with_simplifications','All twelve beam ends receive nominal wrap skins; reconstructed mudwalls, PCF strips, two approaches, three TFC transition envelopes, and retained midspan drain outlets.',[8,9,11,12,13,14,15],['accessories','joints','rails','approaches','drainage'])
    m.cover('Unresolved details','not_modeled','Actual deterioration and patch boundaries, wrap properties, bearing standard PB11 dimensions, slab/beam camber, wing outlines, guardrail terminals, full drainage and site geometry.',[8,9,11,12],[])
    m.checks=dict(spans_m=[span],support_lines=2,girder_lines=6,girder_segments=6,bearings=12,
        girder_y_m=ys.tolist(),support_u_m=us.tolist(),skew_deg=-30,hollow_box_beams=6,
        discrete_shallow_footings=2,concrete_diaphragms=15,proposed_TFC_transitions=3,
        source_design_state='Retained 1985 superstructure and widened supports with proposed 2026 repairs')
    ledger=dict(modeled_state='Retained 1985 replacement/widening geometry with proposed 2026 overlay, beam-end repairs and approaches; completion not established',
        spans_m=[span],deck_length_m=length,deck_width_m=width,deck_thickness_m=slab,
        structural_deck_thickness_m=remaining,overlay_thickness_m=overlay,
        girder_y_m=ys.tolist(),girder_lines=6,spacing_m=7.75*FT,support_u_m=us.tolist(),skew_deg=-30,
        skew_direction='left',grade=-.002,crossfall=.015625,
        supports=support_ledger(m,us,ys,['expansion_elastomeric_bearing_on_abutment','fixed_bearing_on_abutment']),
        girder_section=dict(type='CB21 hollow prestressed box',depth_m=depth,width_m=48*IN,
            outer_profile_yz_m=outer,inner_void_profiles_yz_m=[inner],web_thickness_m=5*IN,
            nominal_top_wall_m=3*IN,nominal_bottom_wall_m=5.5*IN,
            profile_basis='Supplemental 9548292 p.8 dimensioned typical section. Small top ridges, bottom chamfers and local void taper omitted.',
            beam_length_m=blen,beam_end_u_m=[a,b],nominal_solid_endblock_m=endblock,nominal_haunch_m=clear),
        source_evidence=[dict(pages=[8,9],facts='41 ft bearing span, 45 ft 0.5 in floor length, 46 ft 8 in coping width, 44 ft clear roadway, -0.20 percent grade, 30 degree left skew, six CB21 beams at 7 ft 9 in.'),
            dict(pages=[9],facts='Existing 8 in slab milled 0.5 in; proposed minimum 2 in overlay; retained 2 in drains open at midspan only.'),
            dict(pages=[11,12,13,14,15],facts='Beam-end wrap minimum 3 ft, reconstructed mudwalls, PCF joints, 12 in approaches minimum 20 ft 6 in and three TFC transitions.'),
            dict(document_id='9548292',local_file='sources/existing_plans_9548292.pdf',pages=[4,5,6,7,8,9,10],
                facts='1985/1986 reconstruction and widening; retained substructure topology, Type7B pads, 48 x 21 in CB21 section with voids, skew beam ends and concrete diaphragms.'),
            dict(document_id='9707311',pages=[1,2],facts='Revision 1 changes closure time for Des2200957 to 70 calendar days, not structural geometry.')],
        unresolved=['Historical p.9 revised slab width 47 ft 1 in conflicts with latest 46 ft 8 in coping width. Latest primary dimensions control; historical beam spacing remains unchanged.',
            'Type7B standard PB11 sheet unavailable: 50 mm bearing display stack is assumed; fixed/expansion topology is sourced.',
            'Nominal 25 mm haunch, straight beams, simplified void-end blocks and support seats do not reproduce fabrication camber.',
            'Overlay composite action and concrete stiffness must be explicit analysis assumptions. No prestress force or condition-based section loss is inferred.'],
        analytical_member_mapping=[dict(member_id=f'beam_0_{j}',line_index=j,span_index=0,y_m=float(y),support_indices=[0,1],section='CB21') for j,y in enumerate(ys)])
    return finish(m,out,candidate,index,dict(title='US 224 over Eight Mile Creek | retained bridge with proposed 2026 repairs',structure_id='224-90-01545 B',designation='2200957',
        spans_m=[span],deck_thickness_m=slab,
        source_note='Primary INDOT B-44532 / Des2200957 proposed 2026 repair set, document 9683628. Retained CB21 section and supports are checked against unchanged supplementary 1985/1986 B-16317 plans, document 9548292. Revision9707311 changes closure time only.',
        assumptions=['Latest primary coping width controls the 5 in discrepancy with historical revised slab width.',
            'Native Z uses an illustrative 817 ft flowline datum; source grade and nominal beam contacts are reconstructed, not surveyed.',
            'Void geometry is included to prevent a solid rectangular visual section from being mistaken for a hollow box. FEM section properties still require independent explicit calculation.']),ledger)


if __name__ == '__main__':
    import sys
    targets={'deer':deer,'eight':eight}
    for name in sys.argv[1:] or targets: targets[name]()

"""Freeze US421 main-span truss inputs independently of display mesh volumes."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FT=.3048
IN=.0254


def build():
    bid='us421-wildcat'; base=ROOT/'data/bridges'/bid
    manifest=json.loads((base/'model_manifest.json').read_text(encoding='utf8'))
    ids={p['id'] for p in manifest['parts']}
    panels=[0,13+4/12,26+8/12,41,55+4/12,69+8/12,84,98+4/12,111+8/12,125]
    xs=[(33.5+p)*FT for p in panels]
    # Original display builder DECKS['B'], also dimensioned on PDF page 23.
    # These end coordinates describe the complete slab, not the bearing span.
    deck_start=(32+7/12)*FT;deck_end=(159+5.25/12)*FT
    loaded_area=(deck_end-deck_start)*29*FT
    display_deck=next(p for p in manifest['parts'] if p['id']=='deck_B')
    assert all(abs(a-b)<1e-7 for a,b in zip([deck_start,-14.5*FT,deck_end,14.5*FT],
        [display_deck['bounds_m'][0][0],display_deck['bounds_m'][0][1],display_deck['bounds_m'][1][0],display_deck['bounds_m'][1][1]]))
    heights=[h*FT for h in [0,12.5,15,16,16.5,16.5,16,15,12.5,0]]
    x0=33.5*FT
    u=4254+x0/FT-4050
    deck_top=(798.82+.0015*u+(-.0021-.0015)*u*u/1200-778)*FT
    bottom=(794.53-778+.5)*FT
    def ishape(d,b,tw,tf):return dict(kind='I',dimensions_m=[x*IN for x in [d,b,tw,tf]])
    sections=dict(
        lower_chord=dict(kind='twin_channels',depth_m=12*IN,width_m=17*IN,flange_m=4*IN,wall_m=.4375*IN,cover_m=0),
        upper_chord=dict(kind='twin_channels',depth_m=16*IN,width_m=17*IN,flange_m=4*IN,wall_m=.4375*IN,cover_m=.375*IN),
        vertical=ishape(9.73,7.96,.29,.435),diagonal=ishape(10.17,8,.35,.51),
        floorbeam=ishape(36,12,.625,.94),stringer=ishape(18,7.5,.375,.6),
        raker=ishape(6,4,.3,.4),lower_lateral=dict(kind='angle',leg_m=4*IN,wall_m=.375*IN))
    members=[]
    def member(cid,family,section_name,**kw):members.append(dict(cid=cid,family=family,section_name=section_name,material='steel',**kw))
    for side in ['X','Y']:
        for i in range(9):
            member(f'{side}_LC{i}','lower_chord','lower_chord',side=side,i=i)
            member(f'{side}_UC{i}','upper_chord','upper_chord',side=side,i=i)
        for i in range(1,9):
            member(f'{side}_V{i}','vertical','vertical',side=side,i=i)
            member(f'{side}_raker{i}','raker','raker',side=side,i=i)
        for k,(ui,li) in enumerate([(1,2),(2,3),(3,4),(4,5),(5,4),(6,5),(7,6),(8,7)]):
            member(f'{side}_D{k}','diagonal','diagonal',side=side,upper_index=ui,lower_index=li)
    for i in range(10):member(f'floorbeam{i}','floorbeam','floorbeam',i=i)
    for j in range(9):
        for i in range(9):member(f'stringer_{j}_{i}','stringer','stringer',i=i,j=j)
    for k,(a,b) in enumerate([(0,2),(2,4),(4,5),(5,7),(7,9)]):
        for sign in [-1,1]:member(f'lateral_{k}_{sign}','lower_lateral','lower_lateral',i=a,j=b,sign=sign)
    supports=[]
    for end,i in [('expansion',0),('fixed',9)]:
        for side,sign in [('X',1),('Y',-1)]:
            supports.append(dict(end=end,side=side,i=i,u_m=xs[i],y_m=sign*15.25*FT,
                bearings=[dict(cid=f'truss_bearing_{end}_{side}_sole',integral=False,area_m2=24*IN*22*IN)],
                horizontal_Npm=[1e5 if end=='expansion' else 1e9,1e9],rotation_Nm=[1e3]*3))
    analyzed={m['cid'] for m in members}|{'deck_B'}|{s['bearings'][0]['cid'] for s in supports}
    assert analyzed<=ids,analyzed-ids
    assumptions=[
        'Assumed-input linear elastic MAIN TRUSS AND DECK ONLY. The 125 ft truss and complete main-deck slab are analyzed. The two 31 ft 8.5 in box-beam approaches, their decks, piers, abutments, rails, repairs and connection hardware are excluded and carry no calculated stress.',
        f'Pressure acts over the complete 126 ft 10.25 in by 29 ft main-deck rectangle ({loaded_area:.9f} m2). The 11 in start and 11.25 in end slab overhangs are modeled as shell cantilevers beyond the unchanged bearing lines. Stringers stop at the bearing lines. Drain openings are homogenized within the gross loaded rectangle. Half loading means native Y < 0.',
        'The original 1939/1940 standard 1532 is absent. Upper-node elevations are scaled visual reconstructions; chord/channel, stringer, raker and lateral-brace sections are explicit hypothetical inputs, not verified fabrication properties.',
        'All truss, raker, lateral, floorbeam and stringer joints use an assumed rigid three-dimensional frame idealization, with no pin releases, gusset flexibility, slip or local joint stress. Frame bending stiffness and rakers provide lateral restraint; no overhead or top-plane cross-braces are invented.',
        'Source lower lateral crossed braces meet at explicit shared center nodes. Each lower-brace center is assumed rigidly connected to the center stringer/deck; the central single-panel crossing connection is unverified. The two central truss diagonals meet at the M4 node in each plane. Rakers connect the upper joints to floorbeam outriggers with explicit short rigid offsets.',
        'The deck and stringers/floorbeams are assumed fully composite by one-level rigid offsets. The source does not establish this full composite action for all retained members.',
        'Analytical deck and lower chords are flattened at the source-generation first-bearing datum. A nominal crown/crossfall offset sets floorbeam elevation; roadway grade and crossfall changes are excluded from analysis.',
        'Twin-channel chord area and moments are computed by explicit nonoverlapping plates plus optional top cover; torsion uses the open thin-wall strip approximation. Lacing/battens are omitted from section stiffness. No solid bounding-box section is used.',
        'The unsymmetric lateral angle is approximated by its centroidal orthogonal Iy/Iz; product-of-inertia coupling and warping are omitted. This is an explicit equivalent frame section, not a certified angle property.',
        'Four bilateral bearing springs use assumed stiffness; the expansion end is longitudinally softer. Fixed foundations mean prescribed lower bearing nodes. Elastic foundations add assumed six-degree spring beds at those same nodes; no pier/foundation stresses are claimed.',
        'Load is a pressure increment only: no self-weight, prestress, traffic load rating, construction history, cracking, yielding, fatigue, buckling or second-order stability calculation. Local unaveraged shell/joint peaks may not converge.'
    ]
    v=dict(deck=dict(cid='deck_B',u0_m=deck_start,u1_m=deck_end,y0_m=-14.5*FT,y1_m=14.5*FT,thickness_m=7.5*IN,total_thickness_m=8*IN,midplane_z_m=deck_top-7.5*IN/2,
        loaded_area_m2=loaded_area,bearing_u0_m=xs[0],bearing_u1_m=xs[-1],end_overhangs_m=[xs[0]-deck_start,deck_end-xs[-1]]),panel_x_m=xs,upper_heights_m=heights,lower_chord_z_m=bottom,
        truss_y_m=[15.25*FT,-15.25*FT],floorbeam_outer_y_m=18.6*FT,
        floorbeam_z_m=deck_top-.02*14*FT-27*IN,stringer_z_m=deck_top-18*IN,
        stringer_y_m=[v*FT for v in [-14,-10.375,-6.9166667,-3.4583333,0,3.4583333,6.9166667,10.375,14]],
        sections=sections,beams=members,supports=supports,foundation_stiffness_Npm_Nm=[2e8,2e8,8e8,2e8,2e8,2e8],
        mesh_panel_subdivisions=3,mesh_transverse_step_m=1.2,mesh_member_subdivisions=2,connection_idealization='rigid_frame',top_cross_braces=0)
    hashes={k:hashlib.sha256((base/f).read_bytes()).hexdigest() for k,f in [('drawing','drawings.pdf'),('manifest','model_manifest.json'),('model','model.glb')]}
    ledger=dict(schema_version=1,engine='collection_demo',analytical_family='truss',bridge_id=bid,title='US 421 Wildcat Creek | assumed main truss and complete main deck',
        modeled_state='2020 rehabilitation design geometry with retained open-top truss; hypothetical elastic structural inputs',demonstration=True,
        display_scope='MAIN TRUSS AND DECK ONLY: 125 ft bearing span plus the complete 126 ft 10.25 in x 29 ft loaded main deck, including both slab end cantilevers. Approach spans and their decks, substructure, rails and hardware are outside analysis.',
        coordinate_system='Native metres, X increasing station from Abutment 1, Y transverse, Z above source datum 778 ft; flattened analytical elevations.',
        source_pdf=f'data/bridges/{bid}/drawings.pdf',drawing_sha256=hashes['drawing'],source_hashes=hashes,
        sources=dict(drawing=dict(title='INDOT 2020 rehabilitation plans, 30 original PDF pages',url=f'/assets/{bid}/drawing',original_url='https://www.in.gov/indot/files/Design-Plans.pdf'),
            demonstration=dict(title='Explicit assumed main-span structural inputs',url='/analysis-guide#collection-demo')),
        evidence=[
            dict(fields=['panel_x_m','truss_y_m','beams','supports'],status='source topology; connection idealization assumed',source='drawing',pdf_pages=[7,16,20],note='Reviewed open-top truss, nine dimensioned panels, rakers, lower lateral braces and 125 ft bearing span. No overhead bracing.'),
            dict(fields=['deck','stringer_y_m'],status='source-based geometry; end support idealization assumed',source='drawing',pdf_pages=[7,23],note='Complete 126 ft 10.25 in x 29 ft main deck, nine stringer lines, 7.5 in structural slab plus 0.5 in sacrificial wearing surface. Eleven-inch and 11.25-inch end overhangs extend beyond the 125 ft bearing span as loaded slab-only cantilevers.'),
            dict(fields=['upper_heights_m','sections','connection_idealization'],status='assumed / reconstructed',source='demonstration',pdf_pages=[16,17,18,19],note='Upper heights and sections transcribed from original visual-generation assumptions; repair-location 10WF33, 10WF37 and 36WF150 labels do not certify every repeated member.'),
            dict(fields=['supports','foundation_stiffness_Npm_Nm','floorbeam_z_m','stringer_z_m'],status='assumed',source='demonstration',note='Explicit spring stiffness, flat member offsets and full composite/rigid joint idealizations; no section properties from mesh bounds.')],
        fields=[dict(key='main_span_length_m',value=125*FT,unit='m',status='source',source='drawing',pdf_pages=[16,20]),
            dict(key='loaded_main_deck_length_m',value=deck_end-deck_start,unit='m',status='source',source='drawing',pdf_pages=[23]),
            dict(key='loaded_width_m',value=29*FT,unit='m',status='source',source='drawing',pdf_pages=[7]),
            dict(key='loaded_area_m2',value=v['deck']['loaded_area_m2'],unit='m2',status='derived',source='drawing',pdf_pages=[7,23])],
        values=v,assumptions=assumptions,analyzed_component_ids=sorted(analyzed),excluded_component_ids=sorted(ids-analyzed),
        excluded_component_reason='Outside the main truss and complete main-deck analysis, or only connection/repair detail; displayed gray with no claimed FE stress. The analyzed deck_B shell footprint covers its complete displayed X/Y extent.')
    out=ROOT/'fem/collection/us421-wildcat.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(ledger,indent=2)+'\n',encoding='utf8')
    print(bid,len(analyzed),'analyzed members; loaded area',v['deck']['loaded_area_m2'],'m2')
    return ledger


if __name__=='__main__':build()

"""Overlay-plan envelope with an explicitly hypothetical continuous-slab scaffold.

No original structural plans were found in the researched contract. This model
does not turn the overlay drawing into an as-built substructure reconstruction.
"""
from pathlib import Path
import json
import shutil
import numpy as np
from bridge_geometry import Model, FT, IN, sweep, sha

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'data/bridges/sr1-six-mile'
RESEARCH = ROOT.parents[1]/'outputs/indiana_bridge_candidates/additional_20261015'


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(RESEARCH/'contracts/44532/contract_plans_9683625.pdf',OUT/'drawings.pdf')
    length=(72+(7.25/12))*FT
    width=(47+1.5/12)*FT
    thickness=.45
    # 8.5 m is the rounded maximum NBI span, not a measured pier-center spacing.
    # A symmetric three-span scaffold is deliberately assumed around that value.
    edge=.15
    end_span=(length-2*edge-8.5)/2
    spans=[end_span,8.5,end_span]
    supports=[-length/2+edge,-4.25,4.25,length/2-edge]
    m=Model('sr1-six-mile',length,width,20,lambda x:np.zeros_like(x)+6,crossfall=.0156)
    m.add('deck','Continuous slab | assumed 450 mm thickness','deck',m.slab(-length/2,length/2,-width/2,width/2,thickness),[4,7],
          'Drawing envelope; assumed structural thickness',
          '72 ft 7.25 in by 47 ft 1.5 in from location table; three-span continuous slab classification from NBI 201. No original structural slab section was supplied.',
          thickness_m=thickness,assumed_thickness_m=thickness,length_m=length,width_m=width,crossfall_percent=1.56)
    m.add('overlay','Proposed 2026 polymer overlay | nominal 3/8 in','deck',m.slab(-length/2,length/2,-width/2,width/2,3/8*IN,offset=3/8*IN),[3,7],
          'Overlay thickness stated in general notes','Existing overlay is removed before the proposed layer; no duplicated old layer.',thickness_m=3/8*IN)
    # There is no evidence of individual bearings or girder lines: none invented.
    for i,u in enumerate(supports):
        layer='abutments' if i in (0,3) else 'piers'
        stem_t=.65 if layer=='piers' else .8
        m.add(f'support_{i}',f'Support {i+1} | hypothetical concrete wall',layer,
              sweep([(-width/2,0),(0,0),(width/2,0),(width/2,1),(0,1),(-width/2,1)],
                    [-stem_t/2/m.c,stem_t/2/m.c],lambda off,y,t:(m.sx(u+off,y),y,1.25+t*(m.surface(m.sx(u+off,y),y)-thickness-1.25))),[4,7],
              'Hypothetical support geometry, not drawn',
              'Wall type, height, width, thickness and location are illustrative. Two interior support lines represent the stated three-span topology.',
              station_m=u,assumed_thickness_m=stem_t,assumed_base_elevation_m=1.25)
        m.add(f'footing_{i}',f'Support {i+1} | hypothetical buried footing','foundations',
              m.transverse(u,2.2,-width/2-.4,width/2+.4,.6,1.25),[4],
              'Hypothetical foundation envelope','Not an observed or drawing-confirmed foundation; hidden by default.',assumed_width_m=2.2,assumed_thickness_m=.65)
    for end,u in enumerate([supports[0],supports[-1]]):
        direction=-1 if end==0 else 1
        for side in [-1,1]:
            y0,y1=sorted([side*(width/2-.3),side*(width/2+.15)])
            a,b=sorted([u,u+direction*2])
            m.add(f'wing_{end}_{side}',f'End {end+1} | hypothetical wing {side}','abutments',
                  sweep([(y0,1.25),(y1,1.25),(y1,5.4),(y0,5.4)],[a,b],lambda t,y,z:(m.sx(t,y),y,z)),[7],
                  'Hypothetical wing envelope','Length, flare and elevation are unverified; shown only to explain a possible end-support arrangement.')
    m.barriers(-length/2,length/2,[7],height=.9,width=1.5*FT,top=.22,segments=3)
    for p in m.parts:
        if p['layer']=='rails':
            p['basis']='Source 18 in nominal base width; assumed height/profile'
            p['note']='Barrier wall and drip bead appear on overlay section. The 0.9 m height and tapered profile are assumptions; not verified from a barrier detail.'
    for end,edge_u in enumerate([-length/2,length/2]):
        sign=-1 if end==0 else 1
        def loc(t,y,z):
            approach=(28.5+sign*8*(2*y/width))*FT
            x=m.sx(edge_u,y)+sign*t*approach
            return x,y,m.surface(x,y)+z
        m.add(f'approach_{end}',f'Approach {end+1} | 20.5–36.5 ft edge lengths','approaches',
              sweep([(-width/2,-.3),(width/2,-.3),(width/2,0),(0,0),(-width/2,0)],[0,1],loc),[7],
              'Overlay-plan outline; assumed slab thickness',
              'Unequal approach edge lengths are shown in the schematic. Source is not to scale; exact corner setting-out and 0.30 m slab thickness are assumed.',assumed_thickness_m=.3,edge_lengths_ft=[20.5,36.5])
        m.add(f'joint_{end}',f'End {end+1} | Type 1-A joint seal envelope','joints',
              m.slab(edge_u-.015,edge_u+.015,-width/2,width/2,.025,offset=.001),[3,7],
              'Joint type/location stated; assumed seal width','30 mm display width, not a shop or survey dimension.')
    m.cover('Drawing envelope and proposed overlay','modeled_with_simplifications',
            'Deck length/width, clear roadway, crossfall and nominal replacement overlay are sourced. Approach edge lengths come from a not-to-scale schematic.',[3,4,7],['deck','approaches','joints'])
    m.cover('Hypothetical load-bearing scaffold','assumed_for_demonstration',
            f'450 mm structural slab, symmetric {end_span:.6f} / 8.5 / {end_span:.6f} m support spans, 150 mm end overhangs, wall piers, end walls and foundations are illustrative. NBI supplies three spans, continuous concrete slab type and 20-degree skew, not these details.',[4,7],['deck','piers','abutments','foundations'])
    m.cover('Barrier exterior','modeled_with_simplifications','General barrier envelope only. Height, tapered section and rail joints are assumed.',[7],['rails'])
    m.cover('Missing original structural detail','not_modeled','No original slab reinforcement, verified support section/positions, foundations, drainage, construction joints or exact rail details were obtained.',[4,7],[])
    assumptions=[
        'This is a schematic overlay-plan reconstruction with a deliberately hypothetical structural scaffold; it is not a detailed as-built model.',
        '2025 NBI item 43A=2 and 43B=01 identify continuous concrete slab, not concrete beams. The earlier research candidate type was corrected.',
        'Source p.4 incorrectly repeats structure 001-90-00230-B (Wabash). The cover identifies 001-90-07052-B, NBI 000370 and Six Mile Creek consistently; the cover identity is retained.',
        'Source p.4 overall 72 ft 7.25 in governs; p.7 labels a schematic 72 ft overlay length. NBI 22.2 m overall and 8.5 m maximum span are rounded inventory values.',
        'All supports, foundation envelopes and slab thickness are hypothetical. Original substructure geometry has not been established.',
        'Native X station, Y transverse and Z up. The 6 m local elevation, level longitudinal grade and skew direction are assumed; NBI gives skew magnitude only.',
        'No internal reinforcement, pile tips, traffic, observed defects or drainage details are invented.'
    ]
    meta=dict(title='SR 1 over Six Mile Creek | schematic with assumed supports',structure_id='001-90-07052-B',designation='2200542',
              spans_m=spans,deck_thickness_m=thickness,source_note='2026 thin-overlay drawing envelope plus 2025 NBI and explicitly hypothetical structural support geometry.',
              assumptions=assumptions,external_sources=[dict(id='2025 NBI Indiana record 000370',url='https://www.fhwa.dot.gov/BRIDGE/nbi/2025/delimited/IN25.txt'),dict(id='NBI structure type coding guide, item 43',url='https://www.fhwa.dot.gov/bridge/mtguide.pdf')])
    m.checks=dict(support_lines=4,spans_m=spans,girder_segments=0,bearings=0,continuous_slab=True,structural_thickness_assumed=True)
    manifest=m.save(OUT,meta)
    ledger=dict(modeled_state='Proposed 2026 overlay on schematic existing slab; hypothetical supports',deck_length_m=length,deck_width_m=width,
                spans_m=spans,support_u_m=supports,deck_thickness_m=thickness,structural_type='continuous_slab',skew_deg=20,
                girder_lines=0,deck_id='deck',overlay_id='overlay',slab_thickness_status='assumed',support_positions_status='assumed',
                primary_pages=[3,4,7],nbi_structure_type='201',nbi_max_span_m=8.5,assumptions=assumptions)
    (OUT/'source_ledger.json').write_text(json.dumps(ledger,indent=2),encoding='utf8')
    record=dict(id='sr1-six-mile',workspace_enabled=True,name='SR 1 over Six Mile Creek',county='Wells',waterway='Six Mile Creek',
                structure_id='001-90-07052-B',designation='2200542',structure_type='3-span continuous concrete slab | hypothetical support geometry',latitude=40.6233889,longitude=-85.1510194,
                location_source=dict(document='2025 NBI record 000370',url='https://www.fhwa.dot.gov/BRIDGE/nbi/2025/delimited/IN25.txt'),
                owner='INDOT',maintenance='INDOT',nbi_ids=['000370'],ownership_data_year=2025,
                model=dict(glb='bridges/sr1-six-mile/model.glb',thumbnail='bridges/sr1-six-mile/preview.png',deck_length_m=length,spans=3,components=len(m.parts),
                           revision='2026 overlay envelope / hypothetical structural scaffold v1',scope='Drawing-backed surface envelope with explicitly assumed structural thickness and supports.',
                           detail_status='needs_detail',detail_status_note='Schematic demonstration: original structural details unavailable. Slab thickness, support layout and substructure are hypothetical; see Coverage and FEM assumptions.'))
    (OUT/'registry_record.json').write_text(json.dumps(record,indent=2),encoding='utf8')
    (OUT/'source_index.json').write_text(json.dumps(dict(primary_pdf='drawings.pdf',pages=10,url='https://erms12c.indot.in.gov/viewdocs/View12.aspx?Id=9683625',sha256=sha(OUT/'drawings.pdf'),compiled_binder=False),indent=2),encoding='utf8')
    return manifest


if __name__=='__main__':build()

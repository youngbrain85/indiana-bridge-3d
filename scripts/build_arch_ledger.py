"""Freeze the four SR 1/Wabash arch-barrel demonstration inputs.

Reads source metadata only while building the ledger. Solves never read GLBs or
live source files. No bridge asset, database, registry or other ledger is edited.
"""
import hashlib
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BID='sr1-wabash'


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def build():
    base=ROOT/'data/bridges'/BID
    manifest=json.loads((base/'model_manifest.json').read_text(encoding='utf8'))
    ids={p['id'] for p in manifest['parts']}
    analyzed=[f'arch_{i}' for i in range(4)]
    assert set(analyzed)<=ids
    opening=21.946; pier_width=1.295; total=opening*4+3*pier_width
    arches=[]
    for i in range(4):
        a=-total/2+i*(opening+pier_width)
        arches.append(dict(cid=f'arch_{i}',label=f'Arch {chr(65+i)}',u0_m=a,u1_m=a+opening,
            y0_m=-7.087,y1_m=7.087,spring_intrados_z0_m=3.191 if i==0 else 4.715,
            spring_intrados_z1_m=3.191 if i==3 else 4.715,
            quadratic_crown_reference_z_m=8.05,crown_vertical_thickness_m=.356,
            haunch_extra_vertical_thickness_m=.650))
    footprint=4*opening*14.174
    assumptions=[
        'Assumed-input linear elastic arch-barrel pressure increment, not whole-bridge behavior, an as-built analysis, load rating, condition assessment or field validation.',
        'All four actual arch-barrel display members are represented by curved ShellMITC4 elements. Deck, sidewalks, spandrel walls, fill, counterforts, piers, abutments, foundations, parapets and utilities are excluded and receive no stress or displacement claim.',
        'Four barrels are independently restrained at their eight springing faces. Adjacent barrels are not coupled through a modeled pier. Shared-pier bending, thrust cancellation, foundation settlement and construction joints are outside this model.',
        'Uniform pressure acts vertically on the projected 4 x 21.946 m x 14.174 m arch footprints only. Left-half pressure means native Y < 0. Deck overhangs, pier gaps and the extended floor envelope carry no applied load; no redistribution through fill or deck is invented.',
        'The quadratic intrados and vertical thickness t=.356+.650*(2r-1)^2 exactly reproduce the current visualization recipe, but that recipe is itself approximate. Original multi-radius arch setting-out, true radial haunch thickness and construction tolerances are unresolved.',
        'The shell reference surface is the middle of the displayed vertical ring depth. Each element uses normal thickness equal to vertical depth divided by its surface metric, preserving the local vertical-slice volume to first order. This is an explicit shell idealization, not a surveyed ring profile.',
        'Fixed springings clamp all six degrees of freedom along each springing edge. Elastic springings use bilateral six-direction line springs, independently connected to ground. These brackets are illustrative support assumptions, not measured soil/pier behavior.',
        'Elastic springing Kz is the editable bearing_kz_MNpm compatibility parameter in MN/m2 of actual skew springing-line length. Kx=.25*Kz, Ky=.125*Kz; all rotational stiffnesses are frozen at 200 MN*m/rad per metre. Tributary line lengths make support stiffness independent of mesh density.',
        'Concrete E is editable, default 30 GPa; Poisson ratio is assumed 0.20. Steel E is not applicable and does not enter this concrete-only solve. The springing stiffness control applies only when foundation=elastic.',
        'No self-weight, prestress, reinforcement, cracking, creep, shrinkage, geometric nonlinearity, compression-only contact, fill confinement or actual damage is included. All reported fields are incremental linear-elastic shell response.',
        'Shell stress is an unaveraged surface principal normal-stress envelope recovered from membrane and bending resultants. It excludes transverse-shear stress, through-thickness normal stress, solid stress tensors and reinforcement stress.',
        'Local stresses near fixed edges, free edges and variable-thickness transitions may be mesh sensitive. Passing displacement refinement and equilibrium does not validate those local peaks or the physical support assumptions.',
    ]
    ledger=dict(schema_version=1,engine='collection_demo',analytical_family='arch',bridge_id=BID,
        title='SR 1 over Wabash River | four assumed curved arch barrels',
        modeled_state='Retained arch rings in the 2004 roadway reconstruction display; quadratic setting-out is approximate.',
        demonstration=True,display_scope='Four arch barrels only; the remaining whole-crossing display is excluded from analytical fields.',
        coordinate_system='Native metres: X longitudinal, Y transverse, Z up; x=u+skew_dx_dy*y. Curved shell reference surfaces follow the frozen arch equations.',
        source_pdf=f'data/bridges/{BID}/drawings.pdf',drawing_sha256=sha(base/'drawings.pdf'),
        source_hashes={key:sha(base/file) for key,file in [('drawing','drawings.pdf'),('manifest','model_manifest.json'),('model','model.glb')]},
        sources=dict(drawing=dict(title='Historical arch and 2004 roadway reconstruction drawings',url=f'/assets/{BID}/drawing'),
            demonstration=dict(title='Explicit arch-barrel assumptions',url='/analysis-guide#collection-demo'),
            shell=dict(title='OpenSees ShellMITC4 element documentation',url='https://opensees.berkeley.edu/OpenSees/manuals/usermanual/640.htm'),
            section=dict(title='OpenSees elastic membrane-plate section',url='https://opensees.berkeley.edu/OpenSees/manuals/usermanual/231.htm')),
        evidence=[dict(fields=['arches.u0_m','arches.u1_m','arches.y0_m','arches.y1_m'],status='source-based with explicit idealization',source='drawing',pdf_pages=[9,23,24],
                note='Four 21.946 m clear openings, three 1.295 m pier widths, 14.174 m barrel width and 356 mm minimum ring depth. Native skew follows the existing display coordinate transform.'),
            dict(fields=['arches.spring_intrados_z0_m','arches.spring_intrados_z1_m','arches.quadratic_crown_reference_z_m','arches.haunch_extra_vertical_thickness_m'],status='assumed reconstruction',source='demonstration',
                note='Exact numeric equations are frozen from scripts/build_indiana_batch2.py:wabash. The display builder expressly labels intrados/haunch geometry approximate; they are not original setting-out dimensions.'),
            dict(fields=['springing','pressure_projection','normal_thickness_conversion','concrete_poisson'],status='assumed',source='demonstration',
                note='Independent clamped/elastic springing lines, direct projected pressure and no deck/fill interaction. Concrete elasticity and all restraint stiffnesses are assumptions.'),
            dict(fields=['shell_element','stress_recovery'],status='solver formulation',source='shell',
                note='ShellMITC4 curved surface discretized by planar quads; 4 integration points and membrane/bending resultants. ElasticMembranePlateSection uses normal section thickness.')],
        values=dict(arches=arches,spans_m=[opening]*4,pier_gap_m=pier_width,
            skew_dx_dy=-math.tan(math.radians(manifest['skew_deg'])),concrete_poisson=.2,
            mesh_segments_u=24,mesh_segments_y=12,max_mesh_density=3,
            pressure_projection=dict(type='vertical_on_horizontal_projected_barrel_footprints',
                full_area_m2=footprint,left_half_area_m2=footprint/2,y_split_m=0,
                excluded='Pier gaps, deck overhangs and floor outside arch openings',
                loaded_ranges=[dict(cid=a['cid'],u0_m=a['u0_m'],u1_m=a['u1_m'],y0_m=a['y0_m'],y1_m=a['y1_m']) for a in arches]),
            springing=dict(fixed='all six DOFs clamped per edge node',elastic='independent six-direction bilateral line springs',
                horizontal_x_ratio_to_kz=.25,horizontal_y_ratio_to_kz=.125,
                rotational_line_stiffness_Nm_per_rad_per_m=[2e8,2e8,2e8],
                line_length_basis='actual skew edge length = dy*sqrt(1+skew_dx_dy^2)',
                no_shared_pier_coupling=True),
            normal_thickness_conversion='t_normal=t_vertical/sqrt(1+(1+k^2)*(d z_mid/d u)^2)'),
        parameter_labels=dict(pressure_kPa='Vertical pressure on projected arch footprint (kPa)',
            concrete_E_GPa='Assumed arch concrete E (GPa)',bearing_kz_MNpm='Elastic springing Kz (MN/m2 of support line)',
            steel_E_GPa='Not applicable: no steel in arch-barrel model'),
        parameter_notes=dict(bearing_kz_MNpm='Active only with elastic springings; Kx=.25 Kz and Ky=.125 Kz.',
            steel_E_GPa='Accepted for common-setting compatibility only; hidden because no steel stiffness is used.'),
        case_labels=dict(demo_uniform='Assumed arch model: full projected barrel pressure',demo_eccentric='Assumed arch model: left-half projected barrel pressure'),
        foundation_labels=dict(fixed='Clamped springings',elastic='Elastic springing lines'),
        assumptions=assumptions,analyzed_component_ids=analyzed,excluded_component_ids=sorted(ids-set(analyzed)),
        excluded_component_reason='Outside the four-barrel analytical scope. No FE stresses, displacements or load transfer are assigned to these display components.')
    out=ROOT/'fem/collection'/f'{BID}.json'
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(ledger,indent=2)+'\n',encoding='utf8')
    print(f'{BID}: four curved arch barrels, {footprint:.6f} m2 full projected pressure area')
    return ledger


if __name__=='__main__': build()

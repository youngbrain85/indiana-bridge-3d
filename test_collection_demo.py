"""Real OpenSees checks for collection topology, pressure and frozen assumptions."""
import hashlib
import json
import math
import unittest
from pathlib import Path

from fem.collection_demo import CASES, create, parameters_for_ledger, run_model, section, settings, solve_demo

ROOT=Path(__file__).parent
LEDGERS={p.stem:json.loads(p.read_text()) for p in (ROOT/'fem/collection').glob('*.json')}
LEDGERS={bid:ledger for bid,ledger in LEDGERS.items() if ledger.get('engine')=='collection_demo' and not ledger.get('analytical_family')}


class CollectionDemonstrationTests(unittest.TestCase):
    def test_reject_invalid_settings(self):
        for raw in [[],{'unknown':1},{'case':[]},{'steel_E_GPa':True},
                    {'pressure_kPa':float('nan')},{'foundation':'actual'},
                    {'bearing_kz_MNpm':-1},{'load_factor':100}]:
            with self.assertRaises(ValueError):settings(raw)

    def test_source_hashes_and_member_contract(self):
        self.assertEqual(len(LEDGERS),12)
        for bid,ledger in LEDGERS.items():
            with self.subTest(bridge=bid):
                parts={p['id'] for p in json.loads((ROOT/'data/bridges'/bid/'model_manifest.json').read_text())['parts']}
                self.assertEqual(set(ledger['analyzed_component_ids'])|set(ledger['excluded_component_ids']),parts)
                self.assertFalse(set(ledger['analyzed_component_ids'])&set(ledger['excluded_component_ids']))
                for key,name in [('drawing','drawings.pdf'),('manifest','model_manifest.json'),('model','model.glb')]:
                    self.assertEqual(ledger['source_hashes'][key],hashlib.sha256((ROOT/'data/bridges'/bid/name).read_bytes()).hexdigest())
                for row in ledger['evidence']:
                    self.assertIn(row['source'],ledger['sources'])
                    for field in row['fields']:self.assertIn(field,ledger['values'])

    def test_hollow_and_polygon_properties_against_closed_form(self):
        # Offset rectangular cavity independently exercises subtraction and centroid shift.
        outer=[[-2,0],[2,0],[2,4],[-2,4]]; hole=[[-1,1],[1,1],[1,2],[-1,2]]
        sec=section(dict(kind='polygon',profile_yz_m=outer,void_profiles_yz_m=[hole],torsion_J_m4=1))
        area=16-2; cz=(16*2-2*1.5)/area
        iy=4*4**3/12+16*(2-cz)**2-(2*1**3/12+2*(1.5-cz)**2)
        iz=4*4**3/12-1*2**3/12
        self.assertAlmostEqual(sec['A'],area);self.assertAlmostEqual(sec['Iy'],iy);self.assertAlmostEqual(sec['Iz'],iz)
        box=section(LEDGERS['us224-eight-mile']['values']['beams'][0]['section'])
        self.assertLess(box['A'],1.2192*.5334*.7)
        u=section(LEDGERS['21st-street-i465']['values']['beams'][0]['section'])
        self.assertLess(u['A'],99.5*.0254*54*.0254*.5)
        pipe=section(dict(kind='pipe',diameter_m=.4,thickness_m=.01))
        self.assertAlmostEqual(pipe['A'],math.pi*(.4**2-.38**2)/4)

    def test_actual_mesh_mapping_connectivity_and_each_support_loaded(self):
        for bid,ledger in LEDGERS.items():
            with self.subTest(bridge=bid):
                result=run_model(ledger,settings({}))
                self.assertEqual({m['component_id'] for m in result['members']},{bid+':'+cid for cid in ledger['analyzed_component_ids']})
                self.assertTrue(result['all_nodes_connected_to_supports'])
                self.assertTrue(result['mesh']['shells'])
                self.assertGreater(len(result['mesh']['nodes']),50)
                d=ledger['values']['deck'];area=(d['u1_m']-d['u0_m'])*(d['y1_m']-d['y0_m'])
                self.assertAlmostEqual(result['total_load_kN'],area,5)
                self.assertAlmostEqual(sum(s['vertical_kN'] for s in result['support_reactions']),area,5)
                for support in result['support_reactions']:
                    self.assertGreater(support['vertical_kN'],area*.01)
                for a,b in zip(result['load_vector_N_Nm'],result['reaction_vector_N_Nm']):self.assertLess(abs(a+b),.05)
                for member in result['members']:
                    self.assertTrue(all(math.isfinite(p['stress_MPa']) for p in member['samples']))
                if bid in ['us52-mud','sr44-little-blue','sr1-six-mile']:
                    self.assertNotIn('girder',result['family_summary'])

    def test_linear_scaling_and_eccentric_load_distribution(self):
        ledger=LEDGERS['us52-mud']
        a=run_model(ledger,settings({'case':'demo_eccentric'}),2)
        b=run_model(ledger,settings({'case':'demo_eccentric','pressure_kPa':2}),2)
        self.assertAlmostEqual(b['max_deflection_mm'],2*a['max_deflection_mm'],7)
        self.assertAlmostEqual(b['max_stress_MPa'],2*a['max_stress_MPa'],7)
        deck=ledger['values']['deck'];expected=(deck['u1_m']-deck['u0_m'])*(deck['y1_m']-deck['y0_m'])/2
        self.assertAlmostEqual(a['total_load_kN'],expected,6)
        m={m['component_id']:m for m in a['members']}
        self.assertGreater(m['us52-mud:deck_2_2']['max_deflection_mm'],m['us52-mud:deck_2_7']['max_deflection_mm'])
        uniform=run_model(ledger,settings({}),2)
        byxy={(round(n['xyz_m'][0],5),round(n['xyz_m'][1],5)):n['displacement_m'][2]
              for n in uniform['mesh']['nodes'] if abs(n['xyz_m'][2]-deck['midplane_z_m'])<1e-8}
        for (x,y),w in byxy.items():
            if (x,-y) in byxy:self.assertAlmostEqual(w,byxy[x,-y],8)

    def test_independent_spans_and_native_skew(self):
        for bid in ['21st-street-i465','us50-tanners-eb']:
            ledger=LEDGERS[bid];d=create(ledger,settings({}));k=ledger['values']['skew_dx_dy']
            for boundary in [u['u1_m'] for u in ledger['values']['continuity_units'][:-1]]:
                # Real duplicated deck nodes release rotations between units.
                cut=[n for n,xyz in d.nodes.items() if abs(xyz[0]-k*xyz[1]-boundary)<1e-6 and abs(xyz[2]-ledger['values']['deck']['midplane_z_m'])<1e-8]
                self.assertGreater(len(cut),2)
                for beam in d.beams:
                    if beam['family']=='girder':
                        stations=[d.nodes[n][0]-k*d.nodes[n][1] for n in beam['nodes']]
                        self.assertFalse(min(stations)<boundary-1e-6 and max(stations)>boundary+1e-6)
            self.assertFalse({a for a,b in d.links}&{b for a,b in d.links})
            for p in d.pads:self.assertLess(math.dist(*(d.nodes[n] for n in p['nodes'])),1e-12)
        for bid,sign in [('sr44-mud',1),('us224-eight-mile',1),('virginia-avenue',-1)]:
            self.assertEqual(math.copysign(1,LEDGERS[bid]['values']['skew_dx_dy']),sign)

    def test_editable_assumptions_change_response(self):
        ledger=LEDGERS['sr44-mud'];a=run_model(ledger,settings({}))
        for edit in [{'steel_E_GPa':100},{'concrete_E_GPa':10},{'bearing_kz_MNpm':100},{'foundation':'elastic'}]:
            b=run_model(ledger,settings(edit))
            self.assertGreater(b['max_deflection_mm'],a['max_deflection_mm'])
            self.assertAlmostEqual(b['total_load_kN'],a['total_load_kN'],6)
        self.assertNotIn('steel_E_GPa',parameters_for_ledger(LEDGERS['us52-mud']))
        self.assertNotIn('bearing_kz_MNpm',parameters_for_ledger(LEDGERS['sr1-six-mile']))

    def test_both_cases_pass_real_benchmarks_equilibrium_and_displacement_refinement(self):
        for bid,ledger in LEDGERS.items():
            for case in CASES:
                with self.subTest(bridge=bid,case=case):
                    snapshot=dict(ledger=ledger,settings=settings({'case':case}))
                    result=solve_demo(snapshot)
                    self.assertEqual(result['schema_version'],3);self.assertEqual(result['bridge_id'],bid)
                    self.assertTrue(result['demonstration']);self.assertFalse(result['verification']['field_validated'])
                    self.assertIs(result['snapshot'],snapshot)
                    self.assertTrue(result['verification']['passed'])
                    self.assertEqual(len(result['verification']['benchmarks']),21)
                    self.assertTrue(all(t['passed'] for t in result['verification']['benchmarks']))
                    self.assertTrue(result['verification']['mesh_refinement'][0]['passed'])
                    self.assertEqual(result['verification']['mesh_warnings'],[t['quantity'] for t in result['verification']['mesh_refinement'] if not t['passed']])


if __name__=='__main__':unittest.main()

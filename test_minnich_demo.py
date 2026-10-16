"""Real-solver checks for the deliberately hypothetical demonstration."""
import json
import math
import unittest
from pathlib import Path
from fem.minnich_demo import settings, run_model, solve_demo, create

LEDGER=json.loads((Path(__file__).parent/'fem/minnich.json').read_text())


class DemonstrationTests(unittest.TestCase):
    def test_reject_invalid_values(self):
        for raw in [[],{'unknown':1},{'case':[]},{'steel_E_GPa':True},
                    {'pressure_kPa':float('nan')},{'column_diameter_m':0},{'foundation':'real'},
                    {'bearing_kz_MNpm':-1},{'load_factor':100}]:
            with self.assertRaises(ValueError): settings(raw)

    def test_mapping_connectivity_and_pressure_resultant(self):
        r=run_model(LEDGER,settings({}))
        expected={'minnich-road:'+i for i in LEDGER['analyzed_component_ids']}
        self.assertEqual({m['component_id'] for m in r['members']},expected)
        self.assertEqual(len(expected),197)
        self.assertTrue(r['all_nodes_connected_to_supports'])
        self.assertAlmostEqual(r['total_load_kN'],126.4793*19.2024,6)
        for a,b in zip(r['load_vector_N_Nm'],r['reaction_vector_N_Nm']): self.assertLess(abs(a+b),.01)
        for family,v in r['family_summary'].items(): self.assertGreater(v['max_stress_MPa'],0,family)
        d=create(LEDGER,settings({}))
        self.assertFalse({b for a,b in d.links}&{a for a,b in d.links})
        for p in d.pads: self.assertLess(math.dist(*(d.nodes[n] for n in p['nodes'])),1e-12)

    def test_load_linearity_and_eccentric_response(self):
        a=run_model(LEDGER,settings({'case':'demo_eccentric'}))
        b=run_model(LEDGER,settings({'case':'demo_eccentric','pressure_kPa':2}))
        self.assertAlmostEqual(a['total_load_kN'],126.4793*19.2024/2,6)
        self.assertAlmostEqual(b['max_deflection_mm'],2*a['max_deflection_mm'],6)
        self.assertAlmostEqual(b['max_stress_MPa'],2*a['max_stress_MPa'],6)
        m={r['component_id']:r for r in a['members']}
        self.assertGreater(m['minnich-road:plate_1_0']['peak']['stress_MPa'],m['minnich-road:plate_1_7']['peak']['stress_MPa'])

    def test_assumptions_change_calculated_response(self):
        a=run_model(LEDGER,settings({}))
        for raw in [{'steel_E_GPa':100},{'concrete_E_GPa':10},{'bearing_kz_MNpm':100},{'column_diameter_m':.5},{'foundation':'elastic'}]:
            b=run_model(LEDGER,settings(raw))
            self.assertGreater(b['max_deflection_mm'],a['max_deflection_mm'],raw)
            self.assertAlmostEqual(b['total_load_kN'],a['total_load_kN'],6)

    def test_verified_result_keeps_demo_and_mesh_limits(self):
        r=solve_demo({'ledger':LEDGER,'settings':settings({})})
        self.assertTrue(r['demonstration'])
        self.assertTrue(r['verification']['passed'])
        self.assertFalse(r['verification']['field_validated'])
        self.assertEqual(len(r['verification']['benchmarks']),21)
        self.assertTrue(r['verification']['mesh_refinement'][0]['passed'])
        self.assertEqual(r['verification']['mesh_warnings'],[c['quantity'] for c in r['verification']['mesh_refinement'] if not c['passed']])
        self.assertEqual(len(r['sensitivity']),1)
        self.assertNotEqual(r['max_deflection_mm'],r['sensitivity'][0]['max_deflection_mm'])


if __name__=='__main__': unittest.main()

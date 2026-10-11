"""Physics regression tests, run with the optional FEM Python environment."""
import json
import math
import unittest
from pathlib import Path
from fem.solver import FT, PSF, benchmarks, polygon_properties, run_model, section, settings, solve

LEDGER = json.loads((Path(__file__).parent/'fem/beechwood.json').read_text(encoding='utf-8'))


class PhysicsTests(unittest.TestCase):
    def test_analytical_benchmarks(self):
        self.assertEqual(len(benchmarks()),10)

    def test_all_numeric_inputs_have_evidence(self):
        self.assertEqual(set(LEDGER['values']), {f for row in LEDGER['evidence'] for f in row['fields']})

    def test_transformed_section_and_profile_orientation(self):
        v = LEDGER['values']
        sec = section(v, 8.75)
        bare = section(v)
        self.assertGreater(sec['EI_Nm2'],bare['EI_Nm2'])
        self.assertGreater(sec['neutral_axis_m'],bare['neutral_axis_m'])
        points = v['girder_profile_in']
        for a,b in zip(polygon_properties(points),polygon_properties(list(reversed(points)))):
            self.assertAlmostEqual(a,b,places=8)

    def test_beechwood_cases_converge_and_balance(self):
        for case in ['uniform','wearing','girder_weight']:
            r = solve({'ledger':LEDGER, 'settings':{'case':case}})
            self.assertTrue(r['verification']['passed'])
            self.assertFalse(r['verification']['field_validated'])
            self.assertEqual(len(r['members']),12)
            self.assertEqual(len({m['component_id'] for m in r['members']}),12)
            self.assertAlmostEqual(r['total_load_kN'],r['total_reaction_kN'],places=5)
            if case == 'uniform':
                self.assertAlmostEqual(r['total_load_kN'],33*250*FT**2,places=7)
            if case == 'wearing':
                self.assertAlmostEqual(r['total_load_kN'],35*PSF*30*250*FT**2/1000,places=7)
            self.assertTrue(all(math.isfinite(p['stress_MPa']) for m in r['members'] for p in m['samples']))

    def test_stress_signs_symmetry_and_linear_scaling(self):
        a = run_model(LEDGER,settings({'case':'girder_weight'}),16)
        b = run_model(LEDGER,settings({'case':'girder_weight','load_factor':2}),16)
        self.assertAlmostEqual(b['max_stress_MPa'],2*a['max_stress_MPa'],places=7)
        self.assertAlmostEqual(b['max_deflection_mm'],2*a['max_deflection_mm'],places=7)
        for m in a['members']:
            p = m['peak']
            self.assertGreater(p['bottom_MPa'],0)
            self.assertLess(p['top_MPa'],0)
        u = run_model(LEDGER,settings({}),16)
        lookup = {m['component_id']:m for m in u['members']}
        self.assertAlmostEqual(lookup['beechwood:girder_A1']['peak']['stress_MPa'],lookup['beechwood:girder_C4']['peak']['stress_MPa'],places=6)
        fixed = run_model(LEDGER,settings({'end_restraint':'fixed'}),16)
        self.assertNotAlmostEqual(fixed['max_deflection_mm'],u['max_deflection_mm'],places=4)

    def test_reject_invalid_and_ambiguous_options(self):
        for raw in [None,[],{'case':'truck'},{'end_restraint':'spring'}, {'load_factor':True}, {'load_factor':float('nan')},{'load_factor':0}, {'load_factor':6}, {'command':'evil'}, {'case':'girder_weight','end_restraint':'fixed'}]:
            with self.assertRaises(ValueError):
                settings(raw)


if __name__ == '__main__':
    unittest.main()

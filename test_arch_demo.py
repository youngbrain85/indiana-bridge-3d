"""Real-solver validation of the deliberately limited four-arch model."""
import copy
import json
import math
import unittest
from pathlib import Path
from unittest.mock import patch

from fem.arch_demo import arch_benchmarks,create,curve,parameters_for_ledger,run_model,settings,solve_demo

LEDGER=json.loads((Path(__file__).parent/'fem/collection/sr1-wabash.json').read_text(encoding='utf8'))


class ArchDemonstrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.uniform=run_model(LEDGER,settings({}))
        cls.eccentric=run_model(LEDGER,settings({'case':'demo_eccentric'}))

    def test_independent_curved_shell_thrust_benchmark(self):
        checks=arch_benchmarks()
        self.assertEqual(len(checks),2)
        self.assertTrue(all(c['passed'] for c in checks))
        self.assertAlmostEqual(checks[0]['actual'],6250,6)

    def test_curved_source_equations_normal_thickness_and_scope(self):
        d=create(LEDGER,settings({}))
        self.assertEqual(set(d.groups),{f'arch_{i}' for i in range(4)})
        self.assertFalse(d.beams)
        self.assertEqual(len(d.springing_info),8)
        self.assertEqual(len(d.shells),4*24*12)
        for arch in LEDGER['values']['arches']:
            a,b=arch['u0_m'],arch['u1_m'];mid=(a+b)/2
            self.assertAlmostEqual(curve(arch,mid)[0],8.05+.356/2,10)
            for fraction in [.1,.3,.65,.9]:
                u=a+(b-a)*fraction;h=1e-5
                derivative=(curve(arch,u+h)[0]-curve(arch,u-h)[0])/(2*h)
                self.assertAlmostEqual(curve(arch,u)[2],derivative,8)
            # The crowned ring has distinct elevations; this is not a flat plate.
            zs=[d.nodes[n][2] for n in d.arch_nodes[arch['cid']]]
            self.assertGreater(max(zs)-min(zs),2.5)
        self.assertGreater(d.normal_thickness_range[0],.30)
        self.assertLess(d.normal_thickness_range[1],1.006)

    def test_all_arches_mapping_support_connectivity_and_equilibrium(self):
        r=self.uniform
        self.assertEqual({m['component_id'] for m in r['members']},{'sr1-wabash:'+x for x in LEDGER['analyzed_component_ids']})
        self.assertTrue(r['all_nodes_connected_to_supports'])
        self.assertEqual(len(r['support_reactions']),8)
        self.assertEqual(len(r['arch_thrust']),4)
        self.assertTrue(all(t['inward_horizontal_thrust_kN']>100 for t in r['arch_thrust']))
        self.assertAlmostEqual(r['total_load_kN'],4*21.946*14.174,6)
        for a,b in zip(r['load_vector_N_Nm'],r['reaction_vector_N_Nm']):self.assertLess(abs(a+b),1e-4)
        self.assertFalse(r['mesh']['beams'])
        self.assertTrue(all(e['family']=='arch' for e in r['mesh']['shells']))
        self.assertTrue(all(m['peak']['compression_MPa']>0 for m in r['members']))

    def test_pressure_linearity_and_transverse_eccentricity(self):
        a=self.eccentric;b=run_model(LEDGER,settings({'case':'demo_eccentric','pressure_kPa':2}))
        self.assertAlmostEqual(a['total_load_kN'],self.uniform['total_load_kN']/2,6)
        self.assertAlmostEqual(b['max_deflection_mm'],2*a['max_deflection_mm'],8)
        self.assertAlmostEqual(b['max_stress_MPa'],2*a['max_stress_MPa'],8)
        self.assertAlmostEqual(a['load_centroid_xy_m'][1],-14.174/4,10)
        self.assertGreater(abs(a['load_vector_N_Nm'][3]),1e6)
        left=max(abs(n['displacement_m'][2]) for n in a['mesh']['nodes'] if n['xyz_m'][1]<-1)
        right=max(abs(n['displacement_m'][2]) for n in a['mesh']['nodes'] if n['xyz_m'][1]>1)
        self.assertGreater(left,right*1.5)

    def test_material_and_elastic_springing_controls_change_solution(self):
        soft=run_model(LEDGER,settings({'concrete_E_GPa':15}))
        self.assertAlmostEqual(soft['max_deflection_mm'],2*self.uniform['max_deflection_mm'],8)
        elastic=run_model(LEDGER,settings({'foundation':'elastic'}))
        softer=run_model(LEDGER,settings({'foundation':'elastic','bearing_kz_MNpm':100}))
        self.assertGreater(elastic['max_deflection_mm'],self.uniform['max_deflection_mm'])
        self.assertGreater(softer['max_deflection_mm'],elastic['max_deflection_mm'])
        self.assertAlmostEqual(elastic['total_load_kN'],softer['total_load_kN'],8)
        self.assertTrue(elastic['mesh']['springs'])
        self.assertNotIn('steel_E_GPa',parameters_for_ledger(LEDGER))
        self.assertIn('springing',parameters_for_ledger(LEDGER)['bearing_kz_MNpm']['label'])

    def test_verified_frozen_result_has_both_cases_and_explicit_limits(self):
        for case in ['demo_uniform','demo_eccentric']:
            snapshot={'ledger':LEDGER,'settings':settings({'case':case})}
            r=solve_demo(snapshot)
            self.assertEqual(r['schema_version'],3)
            self.assertEqual(r['analytical_family'],'arch')
            self.assertTrue(r['demonstration'])
            self.assertIs(r['snapshot'],snapshot)
            self.assertFalse(r['verification']['field_validated'])
            self.assertTrue(r['verification']['passed'])
            self.assertTrue(r['verification']['all_four_arch_displacements_converged'])
            required=[c for c in r['verification']['mesh_refinement'] if c['required_for_acceptance']]
            self.assertEqual(len(required),5)
            self.assertTrue(all(c['relative_change']<.05 for c in required))
            self.assertEqual(r['verification']['mesh_warnings'],[c['quantity'] for c in r['verification']['mesh_refinement'] if not c['passed']])
            self.assertTrue(r['verification']['local_stress_warnings'])
            self.assertEqual(r['structural_barrels'],4)
            json.dumps(r,allow_nan=False)

    def test_reject_missing_arch_and_bounded_nonconvergence(self):
        missing=copy.deepcopy(LEDGER);missing['values']['arches'].pop()
        with self.assertRaises(ValueError):create(missing,settings({}))
        base=copy.deepcopy(self.uniform)
        def nonconvergent(ledger,options,density):
            r=copy.deepcopy(base);r['mesh_density']=density;r['max_deflection_mm']=float(density)
            r['arch_nodal_deflections_mm']={k:float(density) for k in r['arch_nodal_deflections_mm']}
            return r
        with patch('fem.arch_demo.run_model',side_effect=nonconvergent) as mocked,patch('fem.arch_demo.global_benchmarks',return_value=[]),patch('fem.arch_demo.arch_benchmarks',return_value=[]):
            with self.assertRaisesRegex(RuntimeError,'bounded maximum density'):
                solve_demo({'ledger':LEDGER,'settings':settings({})})
            self.assertEqual(mocked.call_count,3)


if __name__=='__main__':unittest.main()

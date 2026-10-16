"""Actual OpenSees verification of the explicitly scoped main-truss model."""
import json
import math
import unittest
from pathlib import Path
from fem.truss_demo import create,run_model,solve_demo,settings,section,truss_benchmarks,parameters_for_ledger

ROOT=Path(__file__).parent
LEDGER=json.loads((ROOT/'fem/collection/us421-wildcat.json').read_text())


class TrussDemonstrationTests(unittest.TestCase):
    def test_main_deck_shells_cover_display_overhangs_and_keep_bearings(self):
        manifest=json.loads((ROOT/'data/bridges/us421-wildcat/model_manifest.json').read_text())
        bounds=next(p['bounds_m'] for p in manifest['parts'] if p['id']=='deck_B')
        d=create(LEDGER,settings({}));v=LEDGER['values']
        shell_nodes={n for s in d.shells for n in s['nodes']}
        for axis in [0,1]:
            self.assertAlmostEqual(min(d.nodes[n][axis] for n in shell_nodes),bounds[0][axis],7)
            self.assertAlmostEqual(max(d.nodes[n][axis] for n in shell_nodes),bounds[1][axis],7)
        self.assertEqual([round(s['u_m'],7) for s in v['supports']],[10.2108,10.2108,48.3108,48.3108])
        self.assertAlmostEqual(v['panel_x_m'][-1]-v['panel_x_m'][0],125*.3048,10)
        for end,x in [('start',v['panel_x_m'][0]),('end',v['panel_x_m'][-1])]:
            ns=[n for n in shell_nodes if d.nodes[n][0]<x-1e-7] if end=='start' else [n for n in shell_nodes if d.nodes[n][0]>x+1e-7]
            self.assertTrue(ns)
            self.assertLess(sum(d.loads[n][2] for n in ns),0)
            self.assertFalse(set(ns)&set(d.fixed))
        for b in d.beams:
            if b['family']=='stringer':
                self.assertTrue(all(v['panel_x_m'][0]-1e-7<=d.nodes[n][0]<=v['panel_x_m'][-1]+1e-7 for n in b['nodes']))

    def test_open_top_connectivity_and_display_coverage(self):
        d=create(LEDGER,settings({}));v=LEDGER['values'];deck=v['deck']
        self.assertFalse(set(d.truss_upper_nodes)&set(d.fixed))
        self.assertFalse({b for a,b in d.links}&{a for a,b in d.links})
        self.assertEqual(d.top_braces,[])
        for b in d.beams:
            a,c=[d.nodes[n] for n in b['nodes']]
            self.assertFalse(min(a[2],c[2])>deck['midplane_z_m'] and a[1]*c[1]<0)
        self.assertEqual(set(d.groups),set(LEDGER['analyzed_component_ids']))
        self.assertEqual(len(d.pads),4)
        for p in d.pads:self.assertLess(math.dist(*(d.nodes[n] for n in p['nodes'])),1e-12)
        self.assertFalse(any(cid.startswith(('box_','deck_A','deck_C','pier','abut','guardrail')) for cid in d.groups))
        manifest=json.loads((ROOT/'data/bridges/us421-wildcat/model_manifest.json').read_text())
        self.assertLessEqual(set(d.groups),{p['id'] for p in manifest['parts']})

    def test_explicit_open_chord_sections_and_axial_benchmark(self):
        spec=LEDGER['values']['sections']['lower_chord'];s=section(spec)
        d,b,t,f=[spec[k] for k in ['depth_m','width_m','wall_m','flange_m']]
        self.assertAlmostEqual(s['A'],2*((d-2*t)*t+2*f*t),12)
        self.assertLess(s['A'],d*b/3)
        self.assertTrue(all(r['passed'] for r in truss_benchmarks()))

    def test_load_area_equilibrium_and_eccentric_distribution(self):
        uniform=run_model(LEDGER,settings({}));ecc=run_model(LEDGER,settings({'case':'demo_eccentric'}))
        area=(48.59655-9.9314)*(4.4196*2)
        self.assertAlmostEqual(uniform['total_load_kN'],area,6)
        self.assertAlmostEqual(ecc['total_load_kN'],area/2,6)
        for r in [uniform,ecc]:
            self.assertTrue(r['all_nodes_connected_to_supports'])
            self.assertLess(max(r['equilibrium'][0]['force_error'],r['equilibrium'][0]['moment_error']),1e-6)
            self.assertEqual({m['component_id'] for m in r['members']},{'us421-wildcat:'+i for i in LEDGER['analyzed_component_ids']})
            self.assertAlmostEqual(r['load_centroid_xy_m'][0],(48.59655+9.9314)/2,9)
            self.assertLess(r['equilibrium'][0]['load_centroid_moment_error'],1e-9)
        self.assertAlmostEqual(ecc['load_centroid_xy_m'][1],-4.4196/2,9)
        side=lambda r,s:sum(p['vertical_kN'] for p in r['support_reactions'] if p['side']==s)
        self.assertAlmostEqual(side(uniform,'X'),side(uniform,'Y'),5)
        self.assertGreater(side(ecc,'Y'),2*side(ecc,'X'))
        for family in ['upper_chord','lower_chord','diagonal','vertical','floorbeam','stringer','deck']:
            self.assertGreater(ecc['family_summary'][family]['max_stress_MPa'],0)

    def test_load_linearity_and_assumption_sensitivity(self):
        a=run_model(LEDGER,settings({}));b=run_model(LEDGER,settings({'pressure_kPa':2}))
        self.assertAlmostEqual(b['max_deflection_mm'],2*a['max_deflection_mm'],6)
        self.assertAlmostEqual(b['max_stress_MPa'],2*a['max_stress_MPa'],6)
        for raw in [{'steel_E_GPa':100},{'concrete_E_GPa':10},{'bearing_kz_MNpm':100},{'foundation':'elastic'}]:
            b=run_model(LEDGER,settings(raw))
            self.assertGreater(b['max_deflection_mm'],a['max_deflection_mm'],raw)
            self.assertAlmostEqual(b['total_load_kN'],a['total_load_kN'],6)
        self.assertEqual(set(parameters_for_ledger(LEDGER)),{'pressure_kPa','steel_E_GPa','concrete_E_GPa','bearing_kz_MNpm','load_factor'})

    def test_both_cases_have_real_refinement_and_scope(self):
        for case in ['demo_uniform','demo_eccentric']:
            r=solve_demo({'ledger':LEDGER,'settings':settings({'case':case})})
            self.assertTrue(r['demonstration']);self.assertFalse(r['verification']['field_validated'])
            self.assertTrue(r['verification']['passed']);self.assertEqual(len(r['verification']['benchmarks']),23)
            self.assertTrue(r['verification']['mesh_refinement'][0]['passed'])
            self.assertEqual(r['verification']['mesh_warnings'],[p['quantity'] for p in r['verification']['mesh_refinement'] if not p['passed']])
            self.assertEqual(r['scope'],'assumed_main_truss_frame_shell_increment')
            self.assertIn('MAIN TRUSS AND DECK ONLY',r['display_scope'])
            self.assertEqual(r['sensitivity'],[])
            self.assertEqual(r['top_cross_brace_count'],0)


if __name__=='__main__':unittest.main()

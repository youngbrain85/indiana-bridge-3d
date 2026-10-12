"""Connected load path, staged stress recovery and corrected drawing geometry."""
import json
import math
import struct
import unittest
from pathlib import Path
from fem.solver import settings, FT
from fem.global_model import global_benchmarks, global_run, solve_global, create

ROOT=Path(__file__).parent
LEDGER=json.loads((ROOT/'fem/beechwood.json').read_text())
LEDGER['global']=json.loads((ROOT/'fem/global.json').read_text())


class GlobalTests(unittest.TestCase):
    def test_independent_frame_shell_prestress_benchmarks(self):
        self.assertEqual(len(global_benchmarks()),11)

    def test_input_evidence_and_connections(self):
        g=LEDGER['global']
        self.assertEqual(set(g['values']),{f for r in g['evidence'] for f in r['fields']})
        for stage in ['pre','post']:
            d=create(LEDGER,settings({'case':'global_staged'}),1,stage)
            edges=[b['nodes'] for b in d.beams]+[s['nodes'] for s in d.shells]+[p['nodes'] for p in d.pads]+d.links
            neighbors={n:set() for n in d.nodes}
            for ns in edges:
                for n in ns: neighbors[n].update(set(ns)-{n})
            seen=set(d.fixed); pending=list(seen)
            while pending:
                for n in neighbors[pending.pop()]-seen: seen.add(n);pending.append(n)
            self.assertEqual(seen,set(d.nodes),'Every node must reach a foundation support; detect nearly coincident detached nodes.')
            self.assertFalse({b for a,b in d.links}&{a for a,b in d.links})

    def test_all_families_loaded_and_refinement_honest(self):
        r=solve_global({'ledger':LEDGER,'settings':{'case':'global_uniform'}})
        self.assertEqual(len(r['members']),72)
        self.assertEqual(len(r['family_summary']),11)
        self.assertAlmostEqual(r['total_load_kN'],252*33*FT**2,6)
        for f,v in r['family_summary'].items(): self.assertGreater(v['max_stress_MPa'],0,f)
        self.assertGreater(len(r['verification']['mesh_warnings']),0)
        self.assertFalse(r['verification']['all_local_peaks_converged'])
        self.assertTrue(r['verification']['passed'])

    def test_eccentric_load_distribution_and_linearity(self):
        a=global_run(LEDGER,settings({'case':'global_eccentric'}))
        b=global_run(LEDGER,settings({'case':'global_eccentric','load_factor':2}))
        self.assertAlmostEqual(a['total_load_kN'],252*16.5*FT**2,6)
        self.assertAlmostEqual(b['max_deflection_mm'],2*a['max_deflection_mm'],6)
        lookup={m['component_id']:m for m in a['members']}
        self.assertGreater(lookup['beechwood:girder_A1']['peak']['stress_MPa'],lookup['beechwood:girder_A4']['peak']['stress_MPa'])
        for i in range(6): self.assertLess(abs(a['load_vector_N_Nm'][i]+a['reaction_vector_N_Nm'][i]),.01)

    def test_stages_signs_equilibrium_and_retained_force_effect(self):
        low=global_run(LEDGER,settings({'case':'global_staged','prestress_factor':.7}))
        high=global_run(LEDGER,settings({'case':'global_staged','prestress_factor':.9}))
        self.assertGreater(low['max_deflection_mm'],high['max_deflection_mm'])
        self.assertAlmostEqual(low['total_load_kN'],high['total_load_kN'],6)
        self.assertAlmostEqual(sum(s['total_load_kN'] for s in low['stage_results']),low['total_load_kN'],7)
        self.assertAlmostEqual(sum(r['forces_N_Nm'][2] for r in low['reactions'])/1000,low['total_reaction_kN'],6)
        self.assertLess(max(abs(a+b) for a,b in zip(low['load_vector_N_Nm'],low['reaction_vector_N_Nm'])),.05)
        for m in low['members']:
            for p in m['samples']:
                self.assertTrue(math.isfinite(p['stress_MPa']))
                self.assertAlmostEqual(p['stress_MPa'],max(p['tension_MPa'],p['compression_MPa']),7)

    def test_corrected_glb_and_manifest_match_drawing(self):
        base=ROOT/'data/bridges/beechwood'; m=json.loads((base/'model_manifest.json').read_text(encoding='utf-8'))
        data=(base/'model.glb').read_bytes(); length=struct.unpack_from('<I',data,12)[0]; g=json.loads(data[20:20+length]); offset=28+length
        parts={p['id']:p for p in m['parts']}; meshes={p['name']:p for p in g['meshes']}
        for bent in (2,3):
            for side,sign in [('L',1),('R',-1)]:
                for family in ['column','shaft','socket','casing']:
                    cid=f'b{bent}_{family}_{side}'; p=parts[cid]
                    self.assertAlmostEqual(sum(b[1] for b in p['bounds_m'])/2,sign*11*FT,6)
                    a=g['accessors'][meshes[cid]['primitives'][0]['attributes']['POSITION']]; bv=g['bufferViews'][a['bufferView']]
                    values=struct.unpack_from('<'+'f'*a['count']*3,data,offset+bv.get('byteOffset',0)+a.get('byteOffset',0))[1::3]
                    self.assertAlmostEqual((max(values)+min(values))/2,sign*11*FT,5)
            self.assertEqual(parts[f'b{bent}_wall']['dimensions']['clear_width_at_centerline_ft'],17.5)
            self.assertGreater(parts[f'b{bent}_wall']['volume_m3'],11)


if __name__=='__main__': unittest.main()

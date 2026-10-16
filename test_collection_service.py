"""Real collection jobs, input provenance and preservation of the dedicated solvers."""
import copy
import json
import tempfile
import time
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch
from import_data import ROOT, import_all, connect
from fem.service import AnalysisService


class CollectionServiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory()
        cls.db=Path(cls.tmp.name)/'collection.sqlite3'
        import_all(cls.db)
        cls.service=AnalysisService(cls.db)

    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()

    def test_path_and_partial_models(self):
        for bid in ['../../solver','../minnich','sr62-carpentier']:
            self.assertFalse(self.service.info(bid)['available'])
            with self.assertRaises(ValueError):self.service.start(bid,{})

    def test_collection_provenance_and_stale_ledger_rejection(self):
        info=self.service.info('sr10-i65')
        self.assertTrue(info['available'] and info['demonstration'])
        frozen=self.service.freeze({},'sr10-i65')
        self.assertEqual(frozen['source_hashes'],frozen['ledger']['source_hashes'])
        for key in ['solver_code_sha256','global_code_sha256','collection_code_sha256','worker_code_sha256']:
            self.assertEqual(len(frozen[key]),64)
        wrong=copy.deepcopy(frozen['ledger']);wrong['source_hashes']['model']='0'*64
        with patch.object(self.service,'ledger',return_value=wrong):
            with self.assertRaises(ValueError):self.service.freeze({},'sr10-i65')
        wrong=copy.deepcopy(frozen['ledger']);wrong['analyzed_component_ids'].append('nonexistent')
        with patch.object(self.service,'ledger',return_value=wrong):
            with self.assertRaises(ValueError):self.service.freeze({},'sr10-i65')

    def test_dedicated_solver_snapshot_shapes_unchanged(self):
        beech=self.service.freeze({'case':'global_uniform'},'beechwood')
        minnich=self.service.freeze({},'minnich-road')
        self.assertNotIn('collection_code_sha256',beech)
        self.assertNotIn('collection_code_sha256',minnich)
        self.assertEqual(minnich['ledger']['bridge_id'],'minnich-road')
        self.assertIn('demo_code_sha256',minnich)

    def test_mutated_queued_input_cannot_replace_database_snapshot(self):
        with patch('fem.service.threading.Thread'):
            run=self.service.start('us52-mud',{'pressure_kPa':1})
        folder=self.service.run_root/run['id']
        altered=json.loads((folder/'input.json').read_text())
        altered['settings']['pressure_kPa']=2
        (folder/'input.json').write_text(json.dumps(altered),encoding='utf8')
        self.service.worker(run['id'],folder)
        run=self.service.get(run['id'])
        self.assertEqual(run['status'],'failed')
        self.assertIn('changed after it was frozen',run['error'])
        self.assertEqual(run['settings']['pressure_kPa'],1)
        with patch.object(self.service,'freeze',side_effect=FileNotFoundError('model.glb')):
            self.assertFalse(self.service.get(run['id'])['current_inputs'])
        with closing(connect(self.db)) as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM analysis_member_results WHERE run_id=?',(run['id'],)).fetchone()[0],0)

    def test_real_beam_and_slab_jobs_exports_and_mapping(self):
        if not (ROOT/'.venv-fem').exists():self.skipTest('Optional FEM runtime not installed')
        for bid in ['sr10-i65','us52-mud','sr1-wabash','us421-wildcat']:
            with self.subTest(bridge=bid):
                before=self._counts()
                run=self.service.start(bid,{'case':'demo_eccentric'})
                end=time.monotonic()+185
                while run['status'] in ('queued','running') and time.monotonic()<end:
                    time.sleep(.1);run=self.service.get(run['id'])
                self.assertEqual(run['status'],'completed',run.get('error'))
                self.assertTrue(run['current_inputs'])
                data=json.loads(self.service.result_path(run['id']).read_text())
                self.assertTrue(data['demonstration'])
                self.assertFalse(data['verification']['field_validated'])
                self.assertEqual({m['component_id'] for m in data['members']},
                                 {bid+':'+x for x in data['snapshot']['ledger']['analyzed_component_ids']})
                self.assertEqual(data['snapshot']['source_hashes'],data['snapshot']['ledger']['source_hashes'])
                self.assertTrue(data['mesh']['nodes'])
                self.assertAlmostEqual(data['total_load_kN'],data['total_reaction_kN'],5)
                exported=self.service.csv(run['id']).decode()
                self.assertIn('assumed_input_demo',exported)
                self.assertIn('demo_eccentric',exported)
                self.assertEqual(before,self._counts())

    def _counts(self):
        with closing(connect(self.db)) as db:
            return tuple(db.execute('SELECT COUNT(*) FROM '+t).fetchone()[0] for t in ['bridges','components','assets'])


if __name__=='__main__':unittest.main()

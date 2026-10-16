"""HTTP/job/snapshot checks using the real optional solver when installed."""
import importlib.util
import json
import tempfile
import threading
import time
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from import_data import ROOT, connect, import_all
from server import make_server


class AnalysisAPITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.db_path = Path(cls.temp.name)/'test.sqlite3'
        import_all(cls.db_path)
        with connect(cls.db_path) as db:
            cls.component_count=db.execute('SELECT COUNT(*) FROM components').fetchone()[0]
        cls.server = make_server(0,cls.db_path)
        cls.thread = threading.Thread(target=cls.server.serve_forever,daemon=True)
        cls.thread.start()
        cls.url = 'http://127.0.0.1:'+str(cls.server.server_port)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()
        cls.temp.cleanup()

    def request(self,path,body=None,headers=None):
        hdr={'Content-Type':'application/json','X-Bridge-Analysis':'1'}
        hdr.update(headers or {})
        return urlopen(Request(self.url+path,data=json.dumps(body).encode() if body is not None else None,headers=hdr),timeout=30)

    def test_reject_mutation_from_other_origin_and_bad_inputs(self):
        for body,headers,code in [({}, {'Origin':'https://example.com'},403),({}, {'X-Bridge-Analysis':''},403),
                                 ({'load_factor':100},{},400),({'load_factor':True},{},400),({'case':[]},{},400),({'path':'C:/private'},{},400),([],{},400)]:
            with self.assertRaises(HTTPError) as exc:
                self.request('/api/analysis/beechwood/runs',body,headers)
            self.assertEqual(exc.exception.code,code)
        with self.request('/api/analysis/sr62-carpentier') as r:
            self.assertFalse(json.load(r)['available'])
        with self.assertRaises(HTTPError) as exc:
            self.request('/api/analysis/sr62-carpentier/runs',{})
        self.assertEqual(exc.exception.code,400)

    def test_real_run_snapshot_export_and_catalog_preservation(self):
        optional = ROOT/'.venv-fem'
        if not optional.exists() and importlib.util.find_spec('openseespy') is None:
            self.skipTest('Optional OpenSees runtime not installed.')
        with self.request('/api/analysis/beechwood/runs',{'case':'uniform'}) as r:
            self.assertEqual(r.status,202)
            run=json.load(r)
        deadline=time.monotonic()+60
        while run['status'] in ('queued','running') and time.monotonic()<deadline:
            time.sleep(.05)
            with self.request('/api/analysis/runs/'+run['id']) as r:
                run=json.load(r)
        self.assertEqual(run['status'],'completed',run.get('error'))
        self.assertTrue(run['current_inputs'])
        with self.request('/api/analysis/runs/'+run['id']+'/result.json') as r:
            result=json.load(r)
        self.assertEqual(len(result['members']),12)
        self.assertTrue(result['verification']['passed'])
        self.assertEqual(result['snapshot']['ledger']['drawing_sha256'],result['snapshot']['source_hashes']['drawing'])
        with self.request('/api/analysis/runs/'+run['id']+'/samples.csv') as r:
            csv=r.read().decode()
            self.assertIn('top_or_max_MPa',csv)
            self.assertIn('beechwood:girder_B2',csv)
        with connect(self.db_path) as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM analysis_member_results WHERE run_id=?',(run['id'],)).fetchone()[0],12)
            self.assertEqual(db.execute('SELECT COUNT(*) FROM components').fetchone()[0],self.component_count)
        # Source reimport must preserve historical analysis snapshots and results.
        import_all(self.db_path)
        with connect(self.db_path) as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM analysis_member_results WHERE run_id=?',(run['id'],)).fetchone()[0],12)
        with self.request('/api/analysis/beechwood') as r:
            info=json.load(r)
            self.assertEqual(info['runs'][0]['id'],run['id'])
        # Do not serve a corrupted result as a verified run.
        path=self.server.analysis.result_path(run['id'])
        path.write_text('{}',encoding='utf-8')
        with self.assertRaises(HTTPError) as exc:
            self.request('/api/analysis/runs/'+run['id']+'/result.json')
        self.assertEqual(exc.exception.code,409)

    def test_restart_marks_interrupted_runs(self):
        from fem.service import AnalysisService, encode
        snapshot=self.server.analysis.freeze({})
        with connect(self.db_path) as db:
            db.execute('INSERT INTO analysis_inputs VALUES (?,?,?)',('interrupted-input','beechwood',encode(snapshot)))
            db.execute('INSERT INTO analysis_runs(id,bridge_id,input_hash,status,created_utc) VALUES (?,?,?,?,?)',
                       ('0'*32,'beechwood','interrupted-input','running','2000-01-01'))
        restarted=AnalysisService(self.db_path)
        self.assertEqual(restarted.get('0'*32)['status'],'failed')

    def test_minnich_demo_snapshot_mapping_and_inputs(self):
        with self.request('/api/analysis/minnich-road') as r:
            info=json.load(r)
        self.assertTrue(info['available'])
        self.assertTrue(info['demonstration'])
        for body in [{'pressure_kPa':False},{'concrete_E_GPa':1000},{'case':'global_uniform'},{'foundation':'rock'}]:
            with self.assertRaises(HTTPError) as exc:
                self.request('/api/analysis/minnich-road/runs',body)
            self.assertEqual(exc.exception.code,400)
        optional=ROOT/'.venv-fem'
        if not optional.exists() and importlib.util.find_spec('openseespy') is None:
            self.skipTest('Optional OpenSees runtime not installed.')
        with self.request('/api/analysis/minnich-road/runs',{'case':'demo_eccentric','pressure_kPa':2,'column_diameter_m':1.1}) as r:
            run=json.load(r)
        deadline=time.monotonic()+60
        while run['status'] in ('queued','running') and time.monotonic()<deadline:
            time.sleep(.05)
            with self.request('/api/analysis/runs/'+run['id']) as r: run=json.load(r)
        self.assertEqual(run['status'],'completed',run.get('error'))
        self.assertTrue(run['current_inputs'])
        with self.request('/api/analysis/runs/'+run['id']+'/result.json') as r: result=json.load(r)
        self.assertTrue(result['demonstration'])
        self.assertFalse(result['verification']['field_validated'])
        self.assertEqual(result['settings']['column_diameter_m'],1.1)
        self.assertEqual(len(result['members']),197)
        self.assertTrue(all(m['component_id'].startswith('minnich-road:') for m in result['members']))
        self.assertIn('demo_code_sha256',result['snapshot'])
        with self.request('/api/analysis/runs/'+run['id']+'/samples.csv') as r:
            self.assertIn('minnich-road:column_1_0_0',r.read().decode())
        with connect(self.db_path) as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM components').fetchone()[0],self.component_count)
        a=self.server.analysis.freeze({'pressure_kPa':1},'minnich-road')
        b=self.server.analysis.freeze({'pressure_kPa':2},'minnich-road')
        self.assertNotEqual(a,b)


if __name__=='__main__':
    unittest.main()

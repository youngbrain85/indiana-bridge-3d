"""Deployment regression tests against a copy of the saved catalog and run history."""
import os
import tempfile
import time
import unittest
from contextlib import closing
from pathlib import Path
from starlette.testclient import TestClient
from hosted import create_app, prepare_persistent_state
from import_data import connect


class HostedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.seed = Path(os.environ['BRIDGE_TEST_SEED'])
        cls.db = prepare_persistent_state(cls.seed, cls.tmp.name)
        cls.secret = 'test-only-secret-' + 'a' * 48
        cls.origin = 'https://bridge-test.example'
        cls.client = TestClient(create_app(db_path=cls.db, gateway_secret=cls.secret, site_origin=cls.origin))
        cls.client.__enter__()
        cls.headers = {'X-Bridge-Gateway': cls.secret}

    @classmethod
    def tearDownClass(cls):
        cls.client.__exit__(None, None, None)
        cls.tmp.cleanup()

    def test_access_boundary_and_read_routes(self):
        self.assertEqual(self.client.get('/healthz').status_code, 200)
        self.assertEqual(self.client.get('/api/catalog').status_code, 401)
        self.assertEqual(self.client.get('/api/catalog', headers={'X-Bridge-Gateway': 'wrong'}).status_code, 401)
        response = self.client.get('/api/catalog', headers=self.headers)
        self.assertEqual(response.json()['summary']['bridges'], 21)
        self.assertEqual(sum(b['workspace_enabled'] for b in response.json()['bridges']), 16)
        self.assertIn('text/html', self.client.get('/', headers=self.headers).headers['content-type'])
        ranged = self.client.get('/assets/beechwood/model', headers=self.headers | {'Range': 'bytes=0-3'})
        self.assertEqual((ranged.status_code, ranged.content), (206, b'glTF'))
        self.assertEqual(self.client.get('/assets/beechwood/drawing', headers=self.headers | {'Range': 'bytes=0-3'}).content, b'%PDF')
        self.assertEqual(self.client.get('/api/drawing/beechwood/1.png', headers=self.headers).status_code, 200)
        self.assertEqual(self.client.head('/assets/beechwood/model', headers=self.headers).content, b'')

    def test_mutation_rejects_foreign_origin_and_large_bodies(self):
        headers = self.headers | {'X-Bridge-Analysis': '1'}
        self.assertEqual(self.client.post('/api/analysis/sr1-six-mile/runs', headers=headers, json={}).status_code, 403)
        headers['Origin'] = 'https://unrelated.example'
        self.assertEqual(self.client.post('/api/analysis/sr1-six-mile/runs', headers=headers, json={}).status_code, 403)
        headers['Origin'] = self.origin
        self.assertEqual(self.client.post('/api/analysis/sr1-six-mile/runs', headers=headers, content='x' * 2049).status_code, 413)

    def test_saved_results_export_and_persistent_restart(self):
        with closing(connect(self.db)) as db:
            before = db.execute('SELECT COUNT(*) FROM analysis_runs').fetchone()[0]
            saved = db.execute("SELECT id FROM analysis_runs WHERE status='completed' ORDER BY created_utc DESC LIMIT 1").fetchone()[0]
        self.assertEqual(self.client.get('/api/analysis/runs/' + saved + '/result.json', headers=self.headers).status_code, 200)
        export = self.client.get('/export/database', headers=self.headers)
        self.assertEqual(export.status_code, 200)
        self.assertTrue(export.content.startswith(b'SQLite format 3'))
        prepare_persistent_state(self.seed, self.tmp.name)
        with closing(connect(self.db)) as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM analysis_runs').fetchone()[0], before)

    def test_real_native_fem_job(self):
        headers = self.headers | {'X-Bridge-Analysis': '1', 'Origin': self.origin}
        response = self.client.post('/api/analysis/sr1-six-mile/runs', headers=headers, json={'pressure_kPa': 1})
        self.assertEqual(response.status_code, 202, response.text)
        run_id = response.json()['id']
        deadline = time.monotonic() + 90
        while time.monotonic() < deadline:
            run = self.client.get('/api/analysis/runs/' + run_id, headers=self.headers).json()
            if run['status'] in ('completed', 'failed'):
                break
            time.sleep(.3)
        self.assertEqual(run['status'], 'completed', run)
        result = self.client.get('/api/analysis/runs/' + run_id + '/result.json', headers=self.headers).json()
        self.assertTrue(result['verification']['passed'])
        self.assertTrue(run['current_inputs'])

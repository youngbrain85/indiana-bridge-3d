import json
import sqlite3
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from import_data import import_all, connect, explicit_location, sync_presentation
from server import make_server, bridges


class CatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.db_path = Path(cls.temp.name) / 'test.sqlite3'
        cls.counts = import_all(cls.db_path)
        cls.server = make_server(0, cls.db_path)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()
        cls.temp.cleanup()

    def get(self, path, headers=None):
        return urlopen(Request(self.url + path, headers=headers or {}), timeout=30)

    def test_real_catalog_is_complete_and_idempotent(self):
        self.assertEqual(self.counts['bridges'], 9)
        self.assertEqual(self.counts['components'], 4012)
        self.assertEqual(import_all(self.db_path), self.counts)
        with connect(self.db_path) as db:
            self.assertEqual(db.execute('PRAGMA integrity_check').fetchone()[0], 'ok')
            self.assertEqual(db.execute('PRAGMA foreign_key_check').fetchall(), [])
            bad = db.execute('''SELECT COUNT(*) FROM component_documents d JOIN assets a ON a.id=d.asset_id
                WHERE d.pdf_page > a.page_count''').fetchone()[0]
            self.assertEqual(bad, 0)

    def test_api_all_bridges_and_stable_relations(self):
        with self.get('/api/catalog') as r:
            catalog = json.load(r)
        seen = set()
        for b in catalog['bridges']:
            with self.get('/api/bridges/' + b['id']) as r:
                data = json.load(r)
            self.assertEqual(len(data['parts']), b['component_count'])
            for part in data['parts']:
                self.assertNotIn(part['id'], seen)
                seen.add(part['id'])
                self.assertIn(part['group_id'], {g['id'] for g in data['groups']})
                self.assertEqual(part['mesh_name'], part['source_id'])
                self.assertGreater(len(part['basis']), 0)
        self.assertEqual(len(seen), 4012)

    def test_map_only_records_and_complete_first_order(self):
        with self.get('/api/catalog') as r:
            catalog = json.load(r)
        self.assertEqual(catalog['summary']['bridges'], 9)
        records = catalog['bridges']
        self.assertTrue(all(isinstance(b['workspace_enabled'], bool) for b in records))
        self.assertEqual([b['id'] for b in records if b['workspace_enabled']],
                         ['beechwood', '21st-street-i465', 'us421-wildcat', 'us52-mud'])
        self.assertEqual({b['id'] for b in records if not b['workspace_enabled']},
                         {'sr58-white', 'sr159-spencer', 'sr62-csx', 'sr62-tekoppel', 'sr62-carpentier'})
        with connect(self.db_path) as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM assets a JOIN bridges b ON b.id=a.bridge_id '
                                        'WHERE b.workspace_enabled=0').fetchone()[0], 20)
            # Ranking follows detail status, even when the complete record is not first in the source file.
            try:
                db.execute("UPDATE bridges SET detail_status='needs_detail' WHERE id='beechwood'")
                db.execute("UPDATE bridges SET detail_status='complete' WHERE id='us52-mud'")
                self.assertEqual(bridges(db)[0]['id'], 'us52-mud')
            finally:
                db.rollback()

    def test_existing_database_presentation_upgrade_preserves_rows(self):
        legacy = Path(self.temp.name) / 'legacy.sqlite3'
        registry = Path(self.temp.name) / 'presentation.json'
        with sqlite3.connect(legacy) as db:
            db.execute('CREATE TABLE bridges (id TEXT PRIMARY KEY, name TEXT NOT NULL)')
            db.executemany('INSERT INTO bridges VALUES (?,?)', [('kept', 'Kept bridge'), ('map-only', 'Map record')])
        registry.write_text(json.dumps({'bridges': [{'id': 'kept'}, {'id': 'map-only', 'workspace_enabled': False}]}), encoding='utf-8')
        sync_presentation(legacy, registry)
        sync_presentation(legacy, registry)
        with sqlite3.connect(legacy) as db:
            self.assertEqual(db.execute('SELECT id,name,workspace_enabled FROM bridges ORDER BY id').fetchall(),
                             [('kept', 'Kept bridge', 1), ('map-only', 'Map record', 0)])

    def test_pdf_range_suffix_and_invalid_range(self):
        with self.get('/assets/beechwood/drawing', {'Range': 'bytes=0-4'}) as r:
            self.assertEqual(r.status, 206)
            self.assertEqual(r.read(), b'%PDF-')
        with self.get('/assets/beechwood/drawing', {'Range': 'bytes=-9'}) as r:
            self.assertEqual(len(r.read()), 9)
        with self.assertRaises(HTTPError) as caught:
            self.get('/assets/beechwood/drawing', {'Range': 'bytes=999999999999-'})
        self.assertEqual(caught.exception.code, 416)

    def test_registered_files_only_and_missing_records(self):
        for path in ['/api/bridges/not-a-bridge', '/assets/unknown/drawing',
                     '/vendor/leaflet/%2e%2e/%2e%2e/%2e%2e/server.py', '/server.py',
                     '/api/drawing/beechwood/0.png', '/api/drawing/beechwood/9999.png']:
            with self.assertRaises(HTTPError) as caught:
                self.get(path)
            self.assertEqual(caught.exception.code, 404, path)
        with self.assertRaises(HTTPError) as caught:
            self.get('/api/catalog', {'Host': 'attacker.example'})
        self.assertEqual(caught.exception.code, 403)

    def test_source_drawing_and_database_exports(self):
        with self.get('/api/drawing/beechwood/38.png') as r:
            self.assertEqual(r.read(8), b'\x89PNG\r\n\x1a\n')
        with self.get('/export/database') as r:
            snapshot = Path(self.temp.name) / 'export.sqlite3'
            snapshot.write_bytes(r.read())
        with sqlite3.connect(snapshot) as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM components').fetchone()[0], 4012)

    def test_javascript_mime_ignores_windows_registry(self):
        for path in ['/app.js', '/viewer.bundle.js', '/vendor/leaflet/leaflet.js']:
            with self.get(path) as r:
                self.assertIn('javascript', r.headers['Content-Type'])

    def test_locations_not_guessed_from_mesh_ids(self):
        self.assertEqual(explicit_location({'id':'pier_2', 'name':'Pier footing envelope'}), (None, None))
        self.assertEqual(explicit_location({'id':'x', 'name':'Bent 2 · column L'})[0], 'Bent 2')
        self.assertEqual(explicit_location({'id':'x', 'name':'Span 1 deck module'})[0], 'Span 1')


if __name__ == '__main__':
    unittest.main(verbosity=2)

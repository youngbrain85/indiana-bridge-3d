import json
import math
import sqlite3
import struct
import tempfile
import threading
import unittest
from array import array
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from import_data import import_all, connect, explicit_location, mesh_names, render_model, sync_presentation
from server import make_server, bridges

ROOT = Path(__file__).resolve().parent


def glb_meshes(path):
    """Local triangles (in canonical order) and world matrix of every mesh node, read with the standard library."""
    data = path.read_bytes()
    length = struct.unpack_from('<I', data, 12)[0]
    doc, binary = json.loads(data[20:20 + length]), 28 + length
    def accessor(index):
        a = doc['accessors'][index]
        view = doc['bufferViews'][a['bufferView']]
        start = binary + view.get('byteOffset', 0) + a.get('byteOffset', 0)
        code, width = {5126: ('f', 4), 5125: ('I', 4), 5123: ('H', 2), 5121: ('B', 1)}[a['componentType']]
        size = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3}[a['type']] * a['count']
        return array(code, data[start:start + size * width])
    def local(node):
        if 'matrix' in node:
            return node['matrix']
        x, y, z, w = node.get('rotation', [0, 0, 0, 1])
        sx, sy, sz = node.get('scale', [1, 1, 1])
        tx, ty, tz = node.get('translation', [0, 0, 0])
        return [(1 - 2 * (y * y + z * z)) * sx, 2 * (x * y + z * w) * sx, 2 * (x * z - y * w) * sx, 0,
                2 * (x * y - z * w) * sy, (1 - 2 * (x * x + z * z)) * sy, 2 * (y * z + x * w) * sy, 0,
                2 * (x * z + y * w) * sz, 2 * (y * z - x * w) * sz, (1 - 2 * (x * x + y * y)) * sz, 0, tx, ty, tz, 1]
    def times(a, b):  # column-major 4x4 product a @ b
        return [sum(a[k * 4 + r] * b[c * 4 + k] for k in range(4)) for c in range(4) for r in range(4)]
    meshes = {}
    def visit(index, parent):
        node = doc['nodes'][index]
        world = times(parent, local(node))
        if 'mesh' in node:
            triangles = []
            for primitive in doc['meshes'][node['mesh']]['primitives']:
                xyz = accessor(primitive['attributes']['POSITION'])
                corners = accessor(primitive['indices']) if 'indices' in primitive else range(len(xyz) // 3)
                points = [tuple(xyz[i * 3:i * 3 + 3]) for i in corners]
                triangles += [tuple(sorted(points[i:i + 3])) for i in range(0, len(points), 3)]
            meshes[node['name']] = (sorted(triangles), world)
        for child in node.get('children', []):
            visit(child, world)
    identity = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
    for root in doc['scenes'][doc.get('scene', 0)]['nodes']:
        visit(root, identity)
    return meshes


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
        self.assertEqual(self.counts['bridges'], 21)
        self.assertEqual(self.counts['components'], 6622)
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
        self.assertEqual(len(seen), 6622)

    def test_map_only_records_and_complete_first_order(self):
        with self.get('/api/catalog') as r:
            catalog = json.load(r)
        self.assertEqual(catalog['summary']['bridges'], 21)
        records = catalog['bridges']
        self.assertTrue(all(isinstance(b['workspace_enabled'], bool) for b in records))
        self.assertEqual([b['id'] for b in records if b['workspace_enabled']],
                         ['beechwood', '21st-street-i465', 'us421-wildcat', 'us52-mud', 'sr44-mud', 'sr8-yellow', 'sr1-wabash', 'us50-tanners-eb', 'minnich-road', 'fletcher-avenue', 'sr10-i65', 'us35-deer', 'us224-eight-mile', 'virginia-avenue', 'sr44-little-blue', 'sr1-six-mile'])
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
            self.assertEqual(db.execute('SELECT COUNT(*) FROM components').fetchone()[0], 6622)

    def test_javascript_mime_ignores_windows_registry(self):
        for path in ['/app.js', '/viewer.bundle.js', '/vendor/leaflet/leaflet.js']:
            with self.get(path) as r:
                self.assertIn('javascript', r.headers['Content-Type'])

    def test_component_supplemental_evidence_keeps_original_page_numbers(self):
        for bid, cid, source_id, page in [('us224-eight-mile','beam_0_0','9548292',8),
                                          ('virginia-avenue','beam_1','9548460',28)]:
            with self.get('/api/bridges/'+bid) as response:
                detail=json.load(response)
            component=next(p for p in detail['parts'] if p['source_id']==cid)
            refs=component['source_refs']+component['supplementary_sources']
            evidence=next(r for r in refs if str(r.get('source_id',r.get('document_id')))==source_id)
            self.assertIn(page,evidence['pdf_pages'])
            reference=next(r for r in detail['references'] if r['metadata']['id']==source_id)
            with self.get(reference['local_url'],{'Range':'bytes=0-4'}) as response:
                self.assertEqual(response.status,206)
                self.assertEqual(response.read(),b'%PDF-')
        with self.assertRaises(HTTPError) as caught:
            self.get('/assets/us224-eight-mile/source/unregistered.pdf')
        self.assertEqual(caught.exception.code,404)

    def test_render_models_are_display_copies_of_their_source(self):
        registry = ROOT / 'data/registry.json'
        catalog = json.loads(registry.read_text(encoding='utf-8'))['bridges']
        rendered = [b for b in catalog if b['model'].get('render_glb')]
        self.assertTrue(rendered)
        for bridge in rendered:
            source, render = ROOT / 'data' / bridge['model']['glb'], ROOT / 'data' / bridge['model']['render_glb']
            self.assertEqual(render_model(bridge['id'], bridge, registry, source, mesh_names(source)), render.resolve())
            original, display = glb_meshes(source), glb_meshes(render)
            self.assertEqual(set(display), set(original))
            for name, (triangles, world) in original.items():
                # Same triangles in the same place: only texture coordinates and winding may differ.
                self.assertEqual(display[name][0], triangles, name)
                self.assertTrue(all(math.isclose(a, b, abs_tol=1e-6) for a, b in zip(display[name][1], world)), name)
            with self.get('/api/bridges/' + bridge['id']) as r:
                model = json.load(r)['model']
            self.assertEqual(model['render_url'], f'/assets/{bridge["id"]}/render')
            with self.get(model['render_url']) as r:
                self.assertEqual(r.read(), render.read_bytes())
        plain = next(b for b in catalog if not b['model'].get('render_glb'))
        with self.get('/api/bridges/' + plain['id']) as r:
            self.assertNotIn('render_url', json.load(r)['model'])

    def test_stale_render_model_is_ignored(self):
        source = ROOT / 'data/bridges/beechwood/model.glb'
        unstamped = {'model': {'render_glb': 'bridges/beechwood/model.glb'}}  # right meshes, no build stamp
        self.assertIsNone(render_model('beechwood', unstamped, ROOT / 'data/registry.json', source, mesh_names(source)))

    def test_locations_not_guessed_from_mesh_ids(self):
        self.assertEqual(explicit_location({'id':'pier_2', 'name':'Pier footing envelope'}), (None, None))
        self.assertEqual(explicit_location({'id':'x', 'name':'Bent 2 · column L'})[0], 'Bent 2')
        self.assertEqual(explicit_location({'id':'x', 'name':'Span 1 deck module'})[0], 'Span 1')


if __name__ == '__main__':
    unittest.main(verbosity=2)

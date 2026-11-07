import hashlib
import json
import math
import sqlite3
import struct
import tempfile
import threading
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from import_data import import_all, connect, explicit_location, mesh_names, render_model, sync_presentation
from server import make_server, bridges
from test_orientation import RuleTests, ModelTests  # noqa: F401  handedness rule, run with these tests (and in CI)

ROOT = Path(__file__).resolve().parent


def glb_outline(path):
    """Triangle count, world bounds and quantization step of every mesh node, from the GLB JSON alone.

    Display models are meshopt-compressed, so the standard library cannot read their vertices; the
    triangle-by-triangle comparison is scripts/check_render_models.mjs (run by `npm run build`).
    """
    data = path.read_bytes()
    doc = json.loads(data[20:20 + struct.unpack_from('<I', data, 12)[0]])
    scale_of = {5126: 1, 5122: 32767, 5123: 65535, 5120: 127, 5121: 255}
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
        m = times(parent, local(node))
        if 'mesh' in node:
            triangles, corners, step = 0, [], 0.0
            for primitive in doc['meshes'][node['mesh']]['primitives']:
                a = doc['accessors'][primitive['attributes']['POSITION']]
                divisor = scale_of[a['componentType']] if a.get('normalized') else 1
                low, high = [v / divisor for v in a['min']], [v / divisor for v in a['max']]
                corners += [[(low, high)[(k >> i) & 1][i] for i in range(3)] for k in range(8)]
                triangles += doc['accessors'][primitive['indices']]['count'] // 3 if 'indices' in primitive else a['count'] // 3
                step = max(step, max(math.hypot(*m[c * 4:c * 4 + 3]) for c in range(3)) / divisor if divisor > 1 else 0)
            world = [[sum(m[k * 4 + r] * p[k] for k in range(3)) + m[12 + r] for r in range(3)] for p in corners]
            meshes[node['name']] = (triangles, [min(w[i] for w in world) for i in range(3)],
                                    [max(w[i] for w in world) for i in range(3)], step)
        for child in node.get('children', []):
            visit(child, m)
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
        self.assertEqual(self.counts['components'], 6723)
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
        self.assertEqual(len(seen), 6723)

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
            self.assertEqual(db.execute('SELECT COUNT(*) FROM components').fetchone()[0], 6723)

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
            original, display = glb_outline(source), glb_outline(render)
            self.assertEqual(set(display), set(original), bridge['id'])
            for name, (triangles, low, high, _) in original.items():
                count, display_low, display_high, step = display[name]
                self.assertEqual(count, triangles, name)
                for a, b in zip(low + high, display_low + display_high):
                    self.assertLessEqual(abs(a - b), step + 1e-4, name)
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

    def test_inspection_sheets_match_the_model_and_are_served(self):
        base = ROOT / 'data/bridges/beechwood'
        sheets = json.loads((base / 'inspection/sheets.json').read_text(encoding='utf-8'))
        # The sheet set names the model it was generated from: rebuild it whenever model.glb changes.
        self.assertEqual(sheets['source']['sha256'], hashlib.sha256((base / 'model.glb').read_bytes()).hexdigest(),
                         'stale inspection sheets: run scripts/build_inspection_sheets.py beechwood')
        meshes = set(mesh_names(base / 'model.glb'))
        codes = {e['code'] for e in sheets['elements']}
        for pid, part in sheets['parts'].items():
            self.assertIn(pid, meshes)
            self.assertIn(part['element'], codes)
        for e in sheets['elements']:
            self.assertGreater(e['total'], 0, e)
            self.assertAlmostEqual(e['total'], sum(sheets['parts'][p]['quantity'] for p in e['parts']), places=1)
        self.assertEqual(next(e for e in sheets['elements'] if e['code'] == 12)['total'], 252 * 33)
        for sheet in sheets['sheets']:
            svg = ET.parse(base / 'inspection' / sheet['svg']).getroot()
            self.assertEqual(svg.get('viewBox'), '0 0 420 297')
            self.assertEqual(len({v['id'] for v in sheet['views']}), len(sheet['views']))
            for view in sheet['views']:
                x, y, w, h = view['placement']
                self.assertTrue(0 <= x and 0 <= y and x + w <= 1 and y + h <= 1, view['id'])
                for axis in ('u', 'v', 'normal'):
                    self.assertAlmostEqual(sum(c * c for c in view[axis]), 1, places=6)
                cross = [view['u'][1] * view['v'][2] - view['u'][2] * view['v'][1], view['u'][2] * view['v'][0] - view['u'][0] * view['v'][2],
                         view['u'][0] * view['v'][1] - view['u'][1] * view['v'][0]]
                self.assertEqual([round(-c, 6) + 0 for c in view['normal']], [round(c, 6) + 0 for c in cross], f'{view["id"]}: not a true view')
                self.assertTrue(view['regions'], view['id'])
                for region in view['regions']:
                    self.assertIn(region['part'], view['parts'])
                    for rings in region['polygons']:
                        for u, v in (p for ring in rings for p in ring):
                            self.assertTrue(-1e-6 <= u <= 1 + 1e-6 and -1e-6 <= v <= 1 + 1e-6, view['id'])
            with self.get(f'/inspection/beechwood/{sheet["svg"]}') as r:
                self.assertEqual(r.headers['Content-Type'], 'image/svg+xml')
        # Recorded defects keep the coordinates of the view they were drawn on: a view that changed was given a
        # new id, and the old frame is kept with the current view that replaces it.
        current = {v['id']: v for s in sheets['sheets'] for v in s['views']}
        for vid, old in sheets.get('retired_views', {}).items():
            self.assertNotIn(vid, current)
            for key in ('origin', 'u', 'v', 'normal', 'extent_m', 'parts', 'sheet_id'):
                self.assertIn(key, old, vid)
            self.assertIn(old['replaced_by'], current, vid)
            self.assertEqual(old['normal'], current[old['replaced_by']]['normal'], vid)
        with self.get('/api/bridges/beechwood') as r:
            self.assertEqual(json.load(r)['inspection'], {'sheets_url': '/inspection/beechwood/sheets.json', 'app_url': '/inspect#beechwood'})
        with self.get('/inspection/beechwood/sheets.json') as r:
            self.assertEqual(json.load(r)['source']['sha256'], sheets['source']['sha256'])
        with self.get('/api/bridges/us52-mud') as r:
            self.assertNotIn('inspection', json.load(r))
        for path in ('/inspect', '/inspect.bundle.js', '/inspect.css', '/inspect-sw.js', '/defects.js'):
            with self.get(path) as r:
                self.assertEqual(r.status, 200, path)
        for bad in ('/inspection/beechwood/model.glb', '/inspection/beechwood/..%2Fmodel.glb', '/inspection/beechwood/sheets.json.bak'):
            with self.assertRaises(HTTPError, msg=bad) as caught:
                self.get(bad)
            self.assertEqual(caught.exception.code, 404)

    def test_locations_not_guessed_from_mesh_ids(self):
        self.assertEqual(explicit_location({'id':'pier_2', 'name':'Pier footing envelope'}), (None, None))
        self.assertEqual(explicit_location({'id':'x', 'name':'Bent 2 · column L'})[0], 'Bent 2')
        self.assertEqual(explicit_location({'id':'x', 'name':'Span 1 deck module'})[0], 'Span 1')


if __name__ == '__main__':
    unittest.main(verbosity=2)

"""Local bridge asset service with isolated, optional structural analysis jobs."""
import argparse
import csv
import io
import json
import mimetypes
import re
import sqlite3
import tempfile
from contextlib import closing
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit

from import_data import ROOT, DEFAULT_DB, DEFAULT_REGISTRY, connect, import_all, sync_presentation
from fem.service import AnalysisService, BusyError


def decode(row):
    result = dict(row)
    if 'workspace_enabled' in result:
        result['workspace_enabled'] = bool(result['workspace_enabled'])
    for key in list(result):
        if key.endswith('_json'):
            result[key[:-5]] = json.loads(result.pop(key))
    return result


def summary(db):
    result = {'bridges': db.execute('SELECT COUNT(*) FROM bridges').fetchone()[0],
              'components': db.execute('SELECT COUNT(*) FROM components').fetchone()[0],
              'drawing_links': db.execute('SELECT COUNT(*) FROM component_documents').fetchone()[0],
              'drawings': db.execute("SELECT COUNT(*) FROM assets WHERE kind='drawing'").fetchone()[0],
              'complete': db.execute("SELECT COUNT(*) FROM bridges WHERE detail_status='complete'").fetchone()[0]}
    row = db.execute('SELECT completed_utc FROM import_log ORDER BY id DESC LIMIT 1').fetchone()
    result['imported_utc'] = row[0] if row else None
    return result


def bridges(db):
    rows = db.execute('''SELECT b.*, (SELECT COUNT(*) FROM components c WHERE c.bridge_id=b.id) component_count,
        (SELECT page_count FROM assets a WHERE a.bridge_id=b.id AND kind='drawing') drawing_pages
        FROM bridges b ORDER BY b.workspace_enabled DESC, (b.detail_status='complete') DESC, b.rowid''').fetchall()
    result = []
    for row in rows:
        b = decode(row)
        # Detail payload is loaded only when the bridge opens.
        for k in ('assumptions', 'source_metadata'):
            b.pop(k, None)
        b['thumbnail_url'] = f'/assets/{b["id"]}/thumbnail'
        result.append(b)
    return result


def bridge_detail(db, bid):
    row = db.execute('SELECT * FROM bridges WHERE id=?', (bid,)).fetchone()
    if row is None:
        return None
    b = decode(row)
    b['model'] = decode(db.execute('SELECT * FROM models WHERE bridge_id=?', (bid,)).fetchone())
    b['model']['url'] = f'/assets/{bid}/model'
    b['groups'] = [dict(r) for r in db.execute('SELECT * FROM member_groups WHERE bridge_id=? ORDER BY sort_order', (bid,))]
    b['parts'] = []
    for row in db.execute('SELECT * FROM components WHERE bridge_id=? ORDER BY rowid', (bid,)):
        part = decode(row)
        source = part.pop('source')
        part['layer'] = source['layer']
        for key in ('pdf_pages', 'sheets', 'dimensions', 'external_references'):
            part[key] = source.get(key, {} if key == 'dimensions' else [])
        b['parts'].append(part)
    b['documents'] = [dict(r) | {'url': f'/assets/{bid}/drawing'} for r in db.execute(
        "SELECT id,title,page_count,sha256,size_bytes FROM assets WHERE bridge_id=? AND kind='drawing'", (bid,))]
    b['coverage'] = [decode(r) for r in db.execute('SELECT * FROM coverage_items WHERE bridge_id=? ORDER BY rowid', (bid,))]
    b['coverage_links'] = [dict(r) for r in db.execute('''SELECT cc.* FROM component_coverage cc
        JOIN components c ON c.id=cc.component_id WHERE c.bridge_id=?''', (bid,))]
    b['references'] = [decode(r) for r in db.execute('SELECT * FROM reference_sources WHERE bridge_id=?', (bid,))]
    return b


class Handler(BaseHTTPRequestHandler):
    server_version = 'IndianaBridge/1.0'

    def log_message(self, fmt, *args):
        # Paths contain identifiers only; no query or credential logging.
        print(fmt % args, flush=True)

    def headers_for(self, status, mime, size, extra=None):
        self.send_response(status)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', str(size))
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('Cache-Control', 'no-cache')
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()

    def data(self, data, mime='application/json; charset=utf-8', status=200, extra=None):
        if not isinstance(data, bytes):
            data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.headers_for(status, mime, len(data), extra)
        if self.command != 'HEAD':
            self.wfile.write(data)

    def error(self, message, status=404):
        self.data({'error': message}, status=status)

    def file(self, path, mime=None, filename=None):
        if not path.is_file():
            return self.error('File not found')
        size = path.stat().st_size
        start, end, status = 0, size - 1, 200
        extra = {'Accept-Ranges': 'bytes'}
        byte_range = self.headers.get('Range')
        if byte_range:
            match = re.fullmatch(r'bytes=(\d*)-(\d*)', byte_range)
            try:
                if not match or not any(match.groups()):
                    raise ValueError()
                lo, hi = match.groups()
                if not lo:
                    suffix = int(hi)
                    if suffix <= 0:
                        raise ValueError()
                    start = max(0, size - suffix)
                else:
                    start = int(lo)
                    end = min(size - 1, int(hi)) if hi else size - 1
                if start > end or start >= size:
                    raise ValueError()
            except ValueError:
                self.headers_for(416, 'text/plain', 0, {'Content-Range': f'bytes */{size}'})
                return
            status = 206
            extra['Content-Range'] = f'bytes {start}-{end}/{size}'
        if filename:
            extra['Content-Disposition'] = "attachment; filename*=UTF-8''" + quote(filename)
        # Windows registry entries sometimes report .js as text/plain.
        known_types = {'.js': 'text/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8',
                       '.html': 'text/html; charset=utf-8', '.svg': 'image/svg+xml',
                       '.json': 'application/json', '.geojson': 'application/json'}
        content_type = mime or known_types.get(path.suffix.lower()) or mimetypes.guess_type(path.name)[0] or 'application/octet-stream'
        self.headers_for(status, content_type, end - start + 1, extra)
        if self.command == 'HEAD':
            return
        with path.open('rb') as stream:
            stream.seek(start)
            remaining = end - start + 1
            while remaining:
                chunk = stream.read(min(remaining, 1024 * 256))
                if not chunk:
                    break
                self.wfile.write(chunk)
                remaining -= len(chunk)

    def do_HEAD(self):
        self.do_GET()

    def do_POST(self):
        host = self.headers.get('Host', '')
        if host.split(':')[0] not in ('127.0.0.1', 'localhost'):
            return self.error('Localhost access only', 403)
        # Browser mutations must originate on this server, with JSON and a custom header.
        origin = self.headers.get('Origin')
        if (origin and origin != 'http://' + host) or self.headers.get('X-Bridge-Analysis') != '1':
            return self.error('Same-origin analysis requests only', 403)
        match = re.fullmatch(r'/api/analysis/([a-z0-9-]+)/runs', urlsplit(self.path).path)
        if not match:
            return self.error('Not found')
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if self.headers.get('Content-Type', '').split(';')[0] != 'application/json' or not 1 <= length <= 2048:
                return self.error('Send a JSON object smaller than 2048 bytes.', 400)
            options = json.loads(self.rfile.read(length))
            run = self.server.analysis.start(match[1], options)
            return self.data(run, status=202)
        except BusyError as exc:
            return self.error(str(exc), 409)
        except (ValueError, UnicodeDecodeError) as exc:
            return self.error(str(exc), 400)
        except Exception as exc:
            print(f'Analysis start failed: {type(exc).__name__}: {exc}', flush=True)
            return self.error('Analysis could not start. See local server log.', 500)

    def do_GET(self):
        host = self.headers.get('Host', '').split(':')[0]
        if host not in ('127.0.0.1', 'localhost'):
            return self.error('Localhost access only', 403)
        try:
            self.dispatch()
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            pass
        except Exception as exc:
            print(f'{type(exc).__name__}: {exc}', flush=True)
            self.error('The request could not be completed. See local server log.', 500)

    def dispatch(self):
        path = unquote(urlsplit(self.path).path)
        match = re.fullmatch(r'/api/analysis/([a-z0-9-]+)', path)
        if match:
            return self.data(self.server.analysis.info(match[1]))
        match = re.fullmatch(r'/api/analysis/runs/([0-9a-f]{32})(/result\.json|/samples\.csv)?', path)
        if match:
            try:
                if match[2] == '/result.json':
                    target = self.server.analysis.result_path(match[1])
                    return self.file(target, filename='beechwood_'+match[1]+'.json') if target else self.error('Completed run not found')
                if match[2] == '/samples.csv':
                    content = self.server.analysis.csv(match[1])
                    return self.data(content, 'text/csv; charset=utf-8', extra={'Content-Disposition':'attachment; filename="beechwood_fem_samples.csv"'}) if content is not None else self.error('Completed run not found')
                run = self.server.analysis.get(match[1])
                return self.data(run) if run else self.error('Run not found')
            except ValueError as exc:
                return self.error(str(exc), 409)
        with closing(connect(self.server.db_path)) as db:
            if path == '/api/health':
                return self.data({'app': 'indiana-bridge-manager', 'schema': 2})
            if path == '/api/catalog':
                return self.data({'summary': summary(db), 'bridges': bridges(db)})
            match = re.fullmatch(r'/api/bridges/([a-z0-9-]+)', path)
            if match:
                result = bridge_detail(db, match[1])
                return self.data(result) if result else self.error('Bridge not found')
            match = re.fullmatch(r'/assets/([a-z0-9-]+)/(model|drawing|manifest|thumbnail)', path)
            if match:
                row = db.execute('SELECT * FROM assets WHERE bridge_id=? AND kind=?', match.groups()).fetchone()
                if not row:
                    return self.error('Asset not found')
                return self.file(ROOT / row['relative_path'], row['mime'])
            match = re.fullmatch(r'/api/drawing/([a-z0-9-]+)/(\d+)\.png', path)
            if match:
                row = db.execute("SELECT * FROM assets WHERE bridge_id=? AND kind='drawing'", (match[1],)).fetchone()
                page = int(match[2])
                if not row or not 1 <= page <= row['page_count']:
                    return self.error('Drawing page not found')
                cache = ROOT / 'data' / 'page_cache' / (row['sha256'][:16] + f'_{page}.png')
                if not cache.exists():
                    import fitz
                    with fitz.open(ROOT / row['relative_path']) as pdf:
                        sheet = pdf[page - 1]
                        scale = min(2.5, 1800 / sheet.rect.width)
                        pixels = sheet.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
                        cache.parent.mkdir(parents=True, exist_ok=True)
                        # Atomic rename avoids two simultaneous requests reading a partial PNG.
                        with tempfile.NamedTemporaryFile(dir=cache.parent, suffix='.png', delete=False) as tmp:
                            tmp.write(pixels.tobytes('png'))
                            temp = Path(tmp.name)
                        temp.replace(cache)
                return self.file(cache, 'image/png')
            if path == '/export/database':
                with tempfile.TemporaryDirectory() as temp:
                    snapshot = Path(temp) / 'indiana_bridges.sqlite3'
                    destination = sqlite3.connect(snapshot)
                    db.backup(destination)
                    destination.close()
                    return self.file(snapshot, 'application/vnd.sqlite3', snapshot.name)
            match = re.fullmatch(r'/export/([a-z0-9-]+)\.csv', path)
            if match:
                rows = db.execute('''SELECT source_id,name,group_id,location_label,basis,note,volume_m3
                    FROM components WHERE bridge_id=? ORDER BY rowid''', (match[1],)).fetchall()
                if not rows:
                    return self.error('Bridge not found')
                stream = io.StringIO(newline='')
                writer = csv.writer(stream)
                writer.writerow(rows[0].keys())
                for row in rows:
                    writer.writerow(["'" + v if isinstance(v, str) and v.startswith(('=', '+', '-', '@')) else v for v in row])
                return self.data(stream.getvalue().encode('utf-8-sig'), 'text/csv; charset=utf-8', extra={
                    'Content-Disposition': f'attachment; filename="{match[1]}_components.csv"'})

        static = {'/': ROOT / 'web/index.html', '/index.html': ROOT / 'web/index.html',
                  '/app.css': ROOT / 'web/app.css', '/app.js': ROOT / 'web/app.js',
                  '/workspace.css': ROOT / 'web/workspace.css',
                  '/compact.css': ROOT / 'web/compact.css',
                  '/analysis.js': ROOT / 'web/analysis.js',
                  '/analysis.css': ROOT / 'web/analysis.css',
                  '/analysis-guide': ROOT / 'web/analysis-guide.html',
                  '/model-corrections': ROOT / 'web/model-corrections.html',
                  '/review': ROOT / 'web/ui_review.html',
                  '/viewer.bundle.js': ROOT / 'web/viewer.bundle.js',
                  '/map/counties.json': ROOT / 'web/vendor/indiana_counties.geojson',
                  '/map/states.json': ROOT / 'web/vendor/states.geojson',
                  '/favicon.svg': ROOT / 'web/favicon.svg'}
        if path in static:
            mime = 'application/json' if path.startswith('/map/') else None
            return self.file(static[path], mime)
        if path.startswith('/vendor/leaflet/'):
            base = (ROOT / 'web/vendor/leaflet').resolve()
            target = (base / path.removeprefix('/vendor/leaflet/')).resolve()
            if target.is_relative_to(base):
                return self.file(target)
        return self.error('Not found')


def make_server(port=8766, db_path=DEFAULT_DB, registry_path=DEFAULT_REGISTRY):
    sync_presentation(db_path, registry_path)
    server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    server.db_path = db_path
    server.analysis = AnalysisService(db_path)
    server.daemon_threads = True
    return server


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8766)
    args = parser.parse_args()
    if not DEFAULT_DB.exists():
        import_all()
    with make_server(args.port) as server:
        print(f'Indiana Bridge Atlas: http://127.0.0.1:{args.port}/', flush=True)
        server.serve_forever()

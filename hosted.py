"""Production ASGI adapter. Sites authenticates visitors; the engine requires its secret.

The local server and the production adapter share the same catalog, file routes,
and bounded FEM job service. Run exactly one worker against a persistent volume.
"""
import hashlib
import hmac
import io
import json
import mimetypes
import os
import shutil
import sqlite3
import tempfile
from contextlib import asynccontextmanager, closing
from pathlib import Path
from types import SimpleNamespace

from starlette.applications import Starlette
from starlette.background import BackgroundTask
from starlette.concurrency import run_in_threadpool
from starlette.datastructures import Headers
from starlette.responses import Response, FileResponse, JSONResponse
from starlette.routing import Route

from import_data import ROOT, DEFAULT_REGISTRY, connect, sync_presentation
from fem.service import AnalysisService
from server import Handler

SECURITY_HEADERS = {'X-Content-Type-Options': 'nosniff', 'Referrer-Policy': 'no-referrer',
                    'Cache-Control': 'private, no-cache'}


class HostedHandler(Handler):
    def __init__(self, request, state, body=b''):
        self.server = state
        self.command = request.method
        self.path = request.url.path
        # This adapter is called only after gateway authorization and origin checks.
        headers = dict(request.headers)
        headers['host'] = '127.0.0.1'
        headers.pop('origin', None)
        headers['content-length'] = str(len(body))
        self.headers = Headers(headers)
        self.rfile = io.BytesIO(body)

    def data(self, data, mime='application/json; charset=utf-8', status=200, extra=None):
        if not isinstance(data, bytes):
            data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        return Response(data, status_code=status, media_type=mime,
                        headers=SECURITY_HEADERS | (extra or {}))

    def file(self, path, mime=None, filename=None):
        if not path.is_file():
            return self.error('File not found')
        known = {'.js': 'text/javascript', '.css': 'text/css', '.html': 'text/html',
                 '.svg': 'image/svg+xml', '.json': 'application/json', '.geojson': 'application/json'}
        mime = mime or known.get(path.suffix.lower()) or mimetypes.guess_type(path.name)[0] or 'application/octet-stream'
        return FileResponse(path, media_type=mime, filename=filename, headers=SECURITY_HEADERS)


def prepare_persistent_state(seed_dir, runtime_dir):
    """Seed once, then preserve user-created runs across restarts and deploys."""
    seed_dir, runtime_dir = Path(seed_dir), Path(runtime_dir)
    runtime_dir.mkdir(parents=True, exist_ok=True)
    db_path = runtime_dir / 'bridges.sqlite3'
    if not db_path.exists():
        # Copy runs before the DB: an interrupted first boot can safely resume.
        shutil.copytree(seed_dir / 'analysis_runs', runtime_dir / 'analysis_runs', dirs_exist_ok=True)
        staged = runtime_dir / 'bridges.seed.sqlite3'
        shutil.copy2(seed_dir / 'bridges.sqlite3', staged)
        with closing(connect(staged)) as db:
            if db.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
                raise RuntimeError('Seed database integrity check failed')
        staged.replace(db_path)
    with closing(connect(db_path)) as db:
        for row in db.execute("SELECT id, result_path, result_sha256 FROM analysis_runs WHERE result_path IS NOT NULL").fetchall():
            target = runtime_dir / 'analysis_runs' / row['id'] / 'result.json'
            # Relocate metadata only. Frozen inputs and result bytes are unchanged.
            if not target.is_file():
                raise RuntimeError('Saved analysis result is missing: ' + row['id'])
            if hashlib.sha256(target.read_bytes()).hexdigest() != row['result_sha256']:
                raise RuntimeError('Saved analysis result hash mismatch: ' + row['id'])
            db.execute('UPDATE analysis_runs SET result_path=? WHERE id=?', (str(target.resolve()), row['id']))
        db.commit()
    return db_path


def database_download(state):
    folder = Path(tempfile.mkdtemp(prefix='bridge-export-'))
    path = folder / 'indiana_bridges.sqlite3'
    try:
        with closing(connect(state.db_path)) as source, closing(sqlite3.connect(path)) as destination:
            source.backup(destination)
        return FileResponse(path, media_type='application/vnd.sqlite3', filename=path.name,
                            headers=SECURITY_HEADERS, background=BackgroundTask(shutil.rmtree, folder))
    except Exception:
        shutil.rmtree(folder)
        raise


def create_app(*, db_path=None, gateway_secret=None, site_origin=None):
    @asynccontextmanager
    async def lifespan(app):
        secret = gateway_secret or os.environ.get('BRIDGE_GATEWAY_SECRET', '')
        origin = site_origin or os.environ.get('BRIDGE_SITE_ORIGIN', '')
        if len(secret) < 32 or not origin.startswith('https://'):
            raise RuntimeError('Configure BRIDGE_GATEWAY_SECRET and HTTPS BRIDGE_SITE_ORIGIN')
        if db_path is None:
            from hosted_assets import ensure_assets
            ensure_assets(ROOT, Path(os.environ.get('BRIDGE_STATE_DIR', '/persist')))
        selected_db = Path(db_path) if db_path else prepare_persistent_state(
            ROOT / 'seed', os.environ.get('BRIDGE_STATE_DIR', '/persist'))
        sync_presentation(selected_db, DEFAULT_REGISTRY)
        state = SimpleNamespace(db_path=selected_db, analysis=AnalysisService(selected_db),
                                secret=secret, origin=origin.rstrip('/'))
        app.state.bridge = state
        yield

    async def endpoint(request):
        state = request.app.state.bridge
        if request.url.path == '/healthz' and request.method in ('GET', 'HEAD'):
            with closing(connect(state.db_path)) as db:
                db.execute('SELECT 1 FROM bridges LIMIT 1').fetchone()
            return JSONResponse({'status': 'ok'}, headers={'Cache-Control': 'no-store'})
        if not hmac.compare_digest(request.headers.get('X-Bridge-Gateway', ''), state.secret):
            return JSONResponse({'error': 'Unauthorized gateway'}, status_code=401)
        body = b''
        if request.method == 'POST':
            if request.headers.get('Origin') != state.origin:
                return JSONResponse({'error': 'Same-origin analysis requests only'}, status_code=403)
            async for chunk in request.stream():
                body += chunk
                if len(body) > 2048:
                    return JSONResponse({'error': 'Request too large'}, status_code=413)
        if request.url.path == '/export/database' and request.method in ('GET', 'HEAD'):
            return await run_in_threadpool(database_download, state)
        adapter = HostedHandler(request, state, body)
        return await run_in_threadpool(adapter.do_POST if request.method == 'POST' else adapter.dispatch)

    return Starlette(routes=[Route('/{path:path}', endpoint, methods=['GET', 'HEAD', 'POST'])], lifespan=lifespan)


app = create_app()

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', '8080')),
                workers=1, proxy_headers=False, limit_concurrency=40, timeout_keep_alive=5)

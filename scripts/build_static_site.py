"""Export the local app as a read-only static site (for GitHub Pages).

The local server is started in-process, optionally used to precompute every
FEM baseline case, and then crawled. Every GET response the browser needs is
written under OUT_DIR with root-relative URLs rewritten so the site works from
a project sub-path such as https://<user>.github.io/indiana-bridge-3d/.

    python scripts/build_static_site.py _site [--run-fem]

New FEM calculations need the Python server; the static viewer shows the
precomputed runs and keeps their JSON/CSV downloads.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import server  # noqa: E402
import pymupdf  # noqa: E402

ASSET_EXT = {'model': '.glb', 'drawing': '.pdf', 'manifest': '.json', 'thumbnail': '.png'}
PAGES = {'/': 'index.html', '/analysis-guide': 'analysis-guide.html', '/collection-status': 'collection-status.html',
         '/model-corrections': 'model-corrections.html', '/review': 'review.html'}
STATIC_FILES = ['/ui.css', '/app.js', '/analysis.js', '/analysis.css',
                '/viewer.bundle.js', '/favicon.svg', '/map/counties.json', '/map/states.json']
PREFIX = (r'(?:api/|assets/|export/|map/|vendor/|analysis-guide|collection-status|model-corrections|review|'
          r'favicon\.svg|ui\.css|app\.js|analysis\.js|analysis\.css|viewer\.bundle\.js)')


def rewrite(text):
    """Make root-relative app URLs document-relative and give assets real extensions."""
    text = re.sub(r'/assets/([a-z0-9-]+)/(model|drawing|manifest|thumbnail)(?![\w/.-])',
                  lambda m: f'/assets/{m[1]}/{m[2]}{ASSET_EXT[m[2]]}', text)
    text = text.replace('/export/database', '/export/indiana_bridges.sqlite3')
    text = re.sub(r'(?<=["\'`(])/(?=' + PREFIX + r'|[?#])', './', text)
    text = text.replace('href="/"', 'href="./"')
    text = text.replace("+'.png'", "+'.jpg'")  # drawing pages are exported as JPEG
    text = re.sub(r'\./(analysis-guide|collection-status|model-corrections|review)(?=["\'?#])', r'./\1.html', text)
    return text


def local_path(url):
    """Map a server URL to the file it is stored as in the static site."""
    if url in PAGES:
        return PAGES[url]
    m = re.fullmatch(r'/assets/([a-z0-9-]+)/(model|drawing|manifest|thumbnail)', url)
    if m:
        return f'assets/{m[1]}/{m[2]}{ASSET_EXT[m[2]]}'
    if url == '/export/database':
        return 'export/indiana_bridges.sqlite3'
    if re.fullmatch(r'/api/analysis/runs/[0-9a-f]{32}', url):
        return url[1:] + '.json'  # avoids clashing with the runs/<id>/ directory
    return url[1:]


class Crawler:
    def __init__(self, base, out):
        self.base, self.out, self.done = base, out, set()
        self.lock = threading.Lock()

    def fetch(self, url):
        with urllib.request.urlopen(self.base + url, timeout=600) as r:
            return r.read()

    def save(self, url, transform=None):
        with self.lock:
            if url in self.done:
                return None
            self.done.add(url)
        body = self.fetch(url)
        target = self.out / local_path(url)
        target.parent.mkdir(parents=True, exist_ok=True)
        if transform:
            body = transform(body.decode('utf-8')).encode('utf-8')
        target.write_bytes(body)
        return body

    def json(self, url):
        body = self.save(url, rewrite)
        return json.loads(body if body is not None else (self.out / local_path(url)).read_bytes())


def render_pages(pdf_path, out_dir, quality=72):
    out_dir.mkdir(parents=True, exist_ok=True)
    with pymupdf.open(pdf_path) as pdf:
        for number, sheet in enumerate(pdf, 1):
            scale = min(2.5, 1800 / sheet.rect.width)
            pixels = sheet.get_pixmap(matrix=pymupdf.Matrix(scale, scale), alpha=False)
            (out_dir / f'{number}.jpg').write_bytes(pixels.tobytes('jpeg', jpg_quality=quality))
    return number


def source_viewer_url(bid, local_file):
    """Original source PDFs are large; link to GitHub's file viewer instead of copying them."""
    repo = os.environ.get('GITHUB_REPOSITORY', 'youngbrain85/indiana-bridge-3d')
    rev = os.environ.get('GITHUB_SHA') or subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT,
                                                        capture_output=True, text=True).stdout.strip() or 'HEAD'
    return f'https://github.com/{repo}/blob/{rev}/data/bridges/{bid}/{local_file}'


def post(base, path, body):
    request = urllib.request.Request(base + path, data=json.dumps(body).encode(), method='POST', headers={
        'Content-Type': 'application/json', 'X-Bridge-Analysis': '1', 'Origin': base})
    with urllib.request.urlopen(request) as r:
        return json.load(r)


def run_fem(base, bridge_ids):
    get = lambda p: json.load(urllib.request.urlopen(base + p))
    for bid in bridge_ids:
        info = get('/api/analysis/' + bid)
        if not info.get('available'):
            continue
        done = {r['settings'].get('case') for r in info.get('runs', []) if r['status'] == 'completed'}
        # The default case runs last so it is the 'latest' run the viewer opens with.
        for case in sorted(info['cases'], key=lambda c: c == info['defaults'].get('case')):
            if case in done:
                continue
            run = None
            for options in ({**info['defaults'], 'case': case}, {'case': case}):  # legacy cases reject whole-bridge options
                try:
                    run = post(base, f'/api/analysis/{bid}/runs', options)
                    break
                except urllib.error.HTTPError as exc:
                    error = exc.read().decode(errors='replace')
            if run is None:
                print(f'  FEM {bid} / {case}: skipped ({error})', flush=True)
                continue
            while run['status'] not in ('completed', 'failed'):
                time.sleep(0.5)
                run = get('/api/analysis/runs/' + run['id'])
            print(f'  FEM {bid} / {case}: {run["status"]}', run.get('error') or '', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('out', type=Path)
    parser.add_argument('--run-fem', action='store_true', help='precompute every baseline FEM case first')
    parser.add_argument('--port', type=int, default=8791)
    args = parser.parse_args()
    out = args.out.resolve()
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    state = Path(tempfile.mkdtemp(prefix='bridge-static-'))
    db_path = state / 'indiana_bridges.sqlite3'
    server.import_all(db_path)
    httpd = server.make_server(args.port, db_path=db_path)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    base = f'http://127.0.0.1:{args.port}'
    crawl = Crawler(base, out)
    try:
        catalog = json.loads(crawl.fetch('/api/catalog'))
        ids = [b['id'] for b in catalog['bridges']]
        if args.run_fem:
            print('Precomputing FEM cases…', flush=True)
            run_fem(base, ids)

        for url in PAGES:
            crawl.save(url, lambda t: rewrite(t).replace('<html lang="en">', '<html lang="en" data-static="1">', 1))
        for url in STATIC_FILES:
            crawl.save(url, rewrite if url.endswith(('.js', '.css', '.html')) else None)
        for f in sorted((ROOT / 'web/vendor/fonts').glob('*.woff2')):
            crawl.save('/vendor/fonts/' + f.name)
        leaflet = ROOT / 'web/vendor/leaflet'
        for f in leaflet.rglob('*'):
            if f.is_file():
                crawl.save('/vendor/leaflet/' + f.relative_to(leaflet).as_posix())
        crawl.json('/api/health')
        crawl.json('/api/catalog')
        crawl.save('/export/database')

        jobs = []
        for b in catalog['bridges']:
            bid = b['id']
            detail = json.loads(crawl.fetch('/api/bridges/' + bid))
            links = {r['local_url']: source_viewer_url(bid, r['metadata']['local_file'])
                     for r in detail.get('references', []) if r.get('local_url') and r.get('metadata', {}).get('local_file')}
            def detail_text(text, links=links):
                for local, remote in links.items():
                    text = text.replace('"' + local + '"', '"' + remote + '"')
                return rewrite(text)
            crawl.save('/api/bridges/' + bid, detail_text)
            crawl.save(f'/export/{bid}.csv')
            for kind in ASSET_EXT:
                try:
                    crawl.save(f'/assets/{bid}/{kind}')
                except urllib.error.HTTPError:
                    pass
            if detail.get("documents") and (out / local_path(f"/assets/{bid}/drawing")).exists():
                jobs.append(bid)
            info = crawl.json('/api/analysis/' + bid)
            for run in info.get('runs', []):
                crawl.json('/api/analysis/runs/' + run['id'])
                if run['status'] == 'completed':
                    crawl.json(f'/api/analysis/runs/{run["id"]}/result.json')
                    crawl.save(f'/api/analysis/runs/{run["id"]}/samples.csv')
        print(f'Rendering drawing pages for {len(jobs)} bridges…', flush=True)
        for bid in jobs:
            print(f'  {bid}: {render_pages(out / local_path(f"/assets/{bid}/drawing"), out / "api/drawing" / bid)} pages', flush=True)
        (out / '.nojekyll').write_text('')
        (out / '404.html').write_text('<!doctype html><meta charset="utf-8"><title>Not found</title>'
                                      '<p>Not available in the static viewer. <a href="./">Open Indiana Bridge 3D</a></p>')
    finally:
        httpd.shutdown()
        shutil.rmtree(state, ignore_errors=True)
    size = sum(f.stat().st_size for f in out.rglob('*') if f.is_file())
    print(f'Static site: {out} ({len(crawl.done)} URLs, {size / 2**20:.0f} MiB)')


if __name__ == '__main__':
    main()

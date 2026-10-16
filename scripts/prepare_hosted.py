"""Create a self-contained release without altering the live local database."""
import argparse
import hashlib
import json
import shutil
import sqlite3
import sys
from contextlib import closing
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from import_data import connect, sha


def prepare(destination):
    dest = Path(destination).resolve()
    if dest == ROOT or dest.is_relative_to(ROOT / 'data') or ROOT.is_relative_to(dest):
        raise ValueError('Choose a separate empty release directory')
    dest.mkdir(parents=True, exist_ok=True)
    if any(dest.iterdir()):
        raise ValueError('Release directory must be empty')
    for name in ['hosted.py', 'hosted_assets.py', 'server.py', 'import_data.py', 'schema.sql', 'requirements.txt',
                 'requirements-fem.txt', 'requirements-hosted.txt', 'Dockerfile', 'railway.json']:
        shutil.copy2(ROOT / name, dest / name)
    for name in ['fem', 'web']:
        shutil.copytree(ROOT / name, dest / name, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    (dest / 'data').mkdir()
    for name in ['registry.json', 'sources.json', 'collection-summary.json', 'map_sources.json']:
        shutil.copy2(ROOT / 'data' / name, dest / 'data' / name)
    shutil.copytree(ROOT / 'data/bridges', dest / 'data/bridges')
    seed = dest / 'seed'
    seed.mkdir()
    with closing(connect(ROOT / 'data/bridges.sqlite3')) as source, closing(connect(seed / 'bridges.sqlite3')) as target:
        if source.execute("SELECT COUNT(*) FROM analysis_runs WHERE status IN ('queued','running')").fetchone()[0]:
            raise RuntimeError('Wait for the active local FEM run before taking a release snapshot')
        source.backup(target)
        # The asset cache duplicates the source files. Use verified originals in this release.
        for row in target.execute('SELECT id,relative_path,original_path,sha256 FROM assets').fetchall():
            original = ROOT / row['original_path']
            if original.is_file() and original.resolve().is_relative_to(ROOT / 'data/bridges') and sha(original) == row['sha256']:
                relative = original.relative_to(ROOT).as_posix()
            else:
                relative = row['relative_path']
                asset = ROOT / relative
                if sha(asset) != row['sha256']:
                    raise RuntimeError('Asset hash mismatch: ' + row['id'])
                (dest / relative).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(asset, dest / relative)
            target.execute('UPDATE assets SET relative_path=?,original_path=? WHERE id=?', (relative, relative, row['id']))
        for row in target.execute('SELECT id,result_path,result_sha256 FROM analysis_runs').fetchall():
            folder = ROOT / 'data/analysis_runs' / row['id']
            if folder.exists():
                shutil.copytree(folder, seed / 'analysis_runs' / row['id'])
            if row['result_path']:
                result = seed / 'analysis_runs' / row['id'] / 'result.json'
                if sha(result) != row['result_sha256']:
                    raise RuntimeError('Result hash mismatch: ' + row['id'])
                target.execute('UPDATE analysis_runs SET result_path=? WHERE id=?',
                               ('analysis_runs/' + row['id'] + '/result.json', row['id']))
        target.commit()
        counts = {name: target.execute('SELECT COUNT(*) FROM ' + name).fetchone()[0]
                  for name in ['bridges', 'components', 'analysis_runs', 'analysis_member_results']}
        if target.execute('PRAGMA integrity_check').fetchone()[0] != 'ok' or target.execute('PRAGMA foreign_key_check').fetchall():
            raise RuntimeError('Database integrity check failed')
    files = {p.relative_to(dest).as_posix(): sha(p) for p in dest.rglob('*') if p.is_file()}
    inventory = {'counts': counts, 'files': files,
                 'release_hash': hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()}
    (dest / 'release.json').write_text(json.dumps(inventory, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'directory': str(dest), 'counts': counts, 'files': len(files), 'release_hash': inventory['release_hash']}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('destination')
    prepare(parser.parse_args().destination)

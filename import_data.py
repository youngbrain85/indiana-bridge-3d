"""Import existing source-backed bridge assets. Never synthesizes maintenance records."""
import argparse
import hashlib
import json
import re
import shutil
import sqlite3
import struct
from datetime import datetime, timezone
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parent
DEFAULT_REGISTRY = ROOT / 'data' / 'registry.json'
DEFAULT_DB = ROOT / 'data' / 'bridges.sqlite3'


def js(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'))


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def connect(path=DEFAULT_DB):
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON')
    return db


def mesh_names(path):
    with path.open('rb') as stream:
        magic, version, total = struct.unpack('<4sII', stream.read(12))
        if magic != b'glTF' or version != 2 or total != path.stat().st_size:
            raise ValueError(f'Invalid GLB: {path}')
        length, kind = struct.unpack('<II', stream.read(8))
        if kind != 0x4E4F534A:
            raise ValueError('Missing GLB JSON chunk')
        doc = json.loads(stream.read(length))
    return [n.get('name') for n in doc.get('nodes', []) if 'mesh' in n]


def explicit_location(part):
    """Only parse location text explicitly present in an existing component name."""
    name = part['name']
    patterns = [r'\bSpan\s+([A-Z]|\d+)\b', r'\bBent\s+(\d+)\b',
                r'\bPier\s+(\d+)\b', r'\bAbutment\s+(\d+)\b',
                r'\bAbutment\s+[A-Z]\b']
    for pattern in patterns:
        match = re.search(pattern, name, re.I)
        if match:
            return match.group(0), 'Original component name: ' + name
    return None, None


def put(db, table, values):
    columns = ','.join(values)
    db.execute(f'INSERT INTO {table} ({columns}) VALUES ({",".join("?" for _ in values)})', list(values.values()))


def import_all(db_path=DEFAULT_DB, registry_path=None):
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path = Path(registry_path or DEFAULT_REGISTRY).resolve()
    catalog = json.loads(registry_path.read_text(encoding='utf-8'))
    override_path = ROOT / 'source_overrides.json'
    overrides = json.loads(override_path.read_text(encoding='utf-8')) if override_path.exists() else {}
    prepared = []
    # Validate every source before touching the last successful catalog.
    for bridge in catalog['bridges']:
        bid = bridge['id']
        if not re.fullmatch(r'[a-z0-9-]+', bid):
            raise ValueError(f'Unsupported bridge id: {bid}')
        glb = (registry_path.parent / bridge['model']['glb']).resolve()
        manifest_path = glb.with_name('model_manifest.json')
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        source = Path(overrides.get(bid, {}).get('source_pdf', manifest['source_pdf']))
        if not source.is_absolute():
            source = manifest_path.parent / source
        source = source.resolve()
        if not source.is_file():
            raise FileNotFoundError(f'{bid}: missing drawing {source}')
        if manifest.get('source_sha256') and sha(source) != manifest['source_sha256']:
            raise ValueError(f'{bid}: PDF differs from model source hash')
        names = mesh_names(glb)
        ids = [p['id'] for p in manifest['parts']]
        if len(ids) != len(set(ids)) or set(ids) != set(names) or len(names) != len(ids):
            raise ValueError(f'{bid}: GLB and manifest are not one-to-one')
        with fitz.open(source) as pdf:
            pages = len(pdf)
        for part in manifest['parts']:
            for page in part.get('pdf_pages', []):
                if not isinstance(page, int) or not 1 <= page <= pages:
                    raise ValueError(f'{bid}/{part["id"]}: invalid PDF page {page}')
        prepared.append((bridge, manifest, manifest_path, glb, source, pages))

    db = connect(db_path)
    db.executescript((ROOT / 'schema.sql').read_text(encoding='utf-8'))
    with db:
        for bridge, manifest, manifest_path, glb, source, pages in prepared:
            bid, model = bridge['id'], bridge['model']
            db.execute('DELETE FROM bridges WHERE id=?', (bid,))
            put(db, 'bridges', dict(
                id=bid, name=bridge['name'], county=bridge['county'],
                structure_id=bridge.get('structure_id'), designation=bridge.get('designation'),
                structure_type=bridge.get('structure_type'), waterway=bridge.get('waterway'),
                latitude=bridge['latitude'], longitude=bridge['longitude'],
                owner=bridge.get('owner'), maintenance=bridge.get('maintenance'),
                ownership_data_year=bridge.get('ownership_data_year'), nbi_json=js(bridge.get('nbi_ids', [])),
                location_source_json=js(bridge.get('location_source', {})),
                detail_status=model['detail_status'], detail_note=model.get('detail_status_note'),
                revision=model.get('revision'), scope=model.get('scope'),
                deck_length_m=model.get('deck_length_m'), spans=model.get('spans'),
                assumptions_json=js(manifest.get('assumptions', [])), source_note=manifest.get('source_note'),
                source_metadata_json=js({k: v for k, v in manifest.items() if k not in ('parts', 'layers', 'detail_coverage')})))

            def asset(kind, src, filename, mime, count=None):
                # Content addressed files keep a failed import from replacing a live asset.
                digest = sha(src)
                rel = Path('data/assets') / bid / (digest[:16] + '_' + filename)
                target = ROOT / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                if not target.exists() or sha(target) != digest:
                    shutil.copyfile(src, target)
                aid = bid + ':' + kind
                put(db, 'assets', dict(id=aid, bridge_id=bid, kind=kind, title=src.name,
                    relative_path=rel.as_posix(), mime=mime, sha256=digest,
                    size_bytes=target.stat().st_size, page_count=count,
                    original_path=src.relative_to(ROOT).as_posix() if src.is_relative_to(ROOT) else src.name))
                return aid

            model_id = asset('model', glb, 'model.glb', 'model/gltf-binary')
            manifest_id = asset('manifest', manifest_path, 'manifest.json', 'application/json')
            pdf_id = asset('drawing', source, 'drawings.pdf', 'application/pdf', pages)
            thumb = (registry_path.parent / model.get('thumbnail', '')).resolve()
            if thumb.is_file():
                asset('thumbnail', thumb, 'preview.png', 'image/png')
            put(db, 'models', dict(bridge_id=bid, asset_id=model_id, manifest_asset_id=manifest_id,
                units=manifest.get('units', 'm'), axes_json=js({k: manifest[k] for k in ('native_axes', 'glb_axes', 'coordinate_system') if k in manifest}),
                hidden_layers_json=js(manifest.get('default_hidden_layers', []))))
            for order, (layer, label) in enumerate(manifest['layers'].items()):
                if isinstance(label, dict):
                    label = label.get('label', label.get('name', layer))
                put(db, 'member_groups', dict(id=bid + ':' + layer, bridge_id=bid,
                    source_layer=layer, label=label, sort_order=order))
            for part in manifest['parts']:
                cid = bid + ':' + part['id']
                location, location_basis = explicit_location(part)
                put(db, 'components', dict(id=cid, bridge_id=bid, group_id=bid + ':' + part['layer'],
                    source_id=part['id'], mesh_name=part['id'], name=part['name'], color=part.get('color'),
                    location_label=location, location_basis=location_basis, basis=part.get('basis'),
                    note=part.get('note'), bounds_json=js(part.get('bounds_m', [])),
                    volume_m3=part.get('volume_m3'), source_json=js(part)))
                for key, value in part.get('dimensions', {}).items():
                    put(db, 'component_dimensions', dict(component_id=cid, name=key, value_json=js(value)))
                for page in set(part.get('pdf_pages', [])):
                    put(db, 'component_documents', dict(component_id=cid, asset_id=pdf_id, pdf_page=page))
            for i, item in enumerate(manifest.get('detail_coverage', [])):
                cov_id = f'{bid}:coverage:{i}'
                put(db, 'coverage_items', dict(id=cov_id, bridge_id=bid, feature=item['feature'],
                    status=item.get('status'), detail=item.get('detail'), sources_json=js(item.get('sources', []))))
                for pid in set(item.get('part_ids', [])):
                    put(db, 'component_coverage', dict(component_id=bid + ':' + pid, coverage_id=cov_id))
            for i, reference in enumerate(manifest.get('external_sources', [])):
                put(db, 'reference_sources', dict(id=f'{bid}:ref:{i}', bridge_id=bid,
                    title=reference.get('id', reference.get('title', 'Reference')),
                    url=reference.get('url'), metadata_json=js(reference)))
        if db.execute('PRAGMA foreign_key_check').fetchall():
            raise ValueError('Foreign key integrity failed')
        counts = {table: db.execute('SELECT COUNT(*) FROM ' + table).fetchone()[0]
                  for table in ('bridges', 'components', 'member_groups', 'component_documents', 'component_dimensions', 'coverage_items', 'assets')}
        put(db, 'import_log', dict(completed_utc=datetime.now(timezone.utc).isoformat(), summary_json=js(counts)))
    db.close()
    return counts


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', type=Path, default=DEFAULT_DB)
    parser.add_argument('--registry', type=Path)
    args = parser.parse_args()
    print(js(import_all(args.db, args.registry)))

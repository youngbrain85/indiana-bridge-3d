"""Fetch an immutable private release into the persistent volume, once per version."""
import hashlib
import json
import os
import shutil
import tarfile
import tempfile
from pathlib import Path


def ensure_assets(root, state_dir):
    manifest = root / 'assets-release.json'
    if not manifest.is_file():
        return  # Self-contained local release, used by the deployment tests.
    release = json.loads(manifest.read_text())
    digest = release['sha256']
    if len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest):
        raise ValueError('Invalid release checksum')
    releases = state_dir / 'releases'
    releases.mkdir(parents=True, exist_ok=True)
    destination = releases / digest
    if not (destination / '.ready').is_file():
        import boto3
        from botocore.config import Config
        credentials = json.loads(os.environ['BRIDGE_STORAGE_JSON'])
        client = boto3.client('s3', endpoint_url=credentials['endpoint'],
            aws_access_key_id=credentials['accessKeyId'], aws_secret_access_key=credentials['secretAccessKey'],
            region_name=credentials['region'], config=Config(signature_version='s3v4',
                s3={'addressing_style': {'virtual-host':'virtual'}.get(credentials['urlStyle'], credentials['urlStyle'])}))
        staging = Path(tempfile.mkdtemp(prefix='release-', dir=releases))
        try:
            archive = staging / 'release.tar.gz'
            print('Downloading verified bridge release', flush=True)
            client.download_file(credentials['bucketName'], release['key'], str(archive))
            with archive.open('rb') as stream:
                checksum = hashlib.file_digest(stream, 'sha256').hexdigest()
            if checksum != digest:
                raise RuntimeError('Bridge release checksum mismatch')
            extracted = staging / 'content'
            extracted.mkdir()
            with tarfile.open(archive, 'r:gz') as package:
                for member in package.getmembers():
                    target = (extracted / member.name).resolve()
                    if not target.is_relative_to(extracted.resolve()) or not (member.isfile() or member.isdir()):
                        raise RuntimeError('Unsafe release archive entry')
                package.extractall(extracted, filter='data')
            (extracted / '.ready').write_text(digest)
            extracted.replace(destination)
        finally:
            shutil.rmtree(staging)
    for relative in ['data/bridges', 'data/assets', 'seed']:
        source = destination / relative
        target = root / relative
        if not source.exists():
            continue
        if target.is_symlink():
            if target.resolve() == source.resolve():
                continue
            target.unlink()
        elif target.exists():
            raise RuntimeError('Runtime asset path must be absent before mounting: ' + relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.symlink_to(source, target_is_directory=True)

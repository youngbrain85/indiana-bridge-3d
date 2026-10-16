"""Upload private release assets and configure the selected Railway engine via stdin."""
import argparse
import hashlib
import json
import shutil
import subprocess
import tarfile
from pathlib import Path
import boto3
from botocore.config import Config


def upload(release, output, cli, bucket):
    release, output = Path(release).resolve(), Path(output).resolve()
    if output.exists() and any(output.iterdir()):
        raise ValueError('Choose a new compact release directory')
    output.mkdir(parents=True, exist_ok=True)
    archive = output.parent / (output.name + '-assets.tar.gz')
    with tarfile.open(archive, 'w:gz', compresslevel=1) as package:
        for relative in ['data/bridges', 'data/assets', 'seed']:
            if (release / relative).exists():
                package.add(release / relative, arcname=relative)
    with archive.open('rb') as stream:
        checksum = hashlib.sha256()
        for chunk in iter(lambda: stream.read(1024*1024), b''):
            checksum.update(chunk)
    digest = checksum.hexdigest()
    credentials = json.loads(subprocess.run([cli, 'bucket', 'credentials', '--bucket', bucket, '--json'],
        capture_output=True, text=True, check=True).stdout)
    style = {'virtual-host': 'virtual'}.get(credentials['urlStyle'], credentials['urlStyle'])
    if style not in ('path', 'virtual', 'auto'):
        raise ValueError('Unsupported bucket URL style')
    client = boto3.client('s3', endpoint_url=credentials['endpoint'],
        aws_access_key_id=credentials['accessKeyId'], aws_secret_access_key=credentials['secretAccessKey'],
        region_name=credentials['region'], config=Config(signature_version='s3v4', s3={'addressing_style':style}))
    key = 'releases/' + digest + '.tar.gz'
    print(json.dumps({'upload_bytes': archive.stat().st_size, 'sha256': digest}), flush=True)
    client.upload_file(str(archive), credentials['bucketName'], key,
        ExtraArgs={'ContentType':'application/gzip', 'Metadata':{'sha256':digest}})
    if client.head_object(Bucket=credentials['bucketName'], Key=key)['ContentLength'] != archive.stat().st_size:
        raise RuntimeError('Uploaded archive size mismatch')
    result = subprocess.run([cli, 'variable', 'set', 'BRIDGE_STORAGE_JSON', '--stdin', '--skip-deploys', '--json'],
        input=json.dumps(credentials), text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError('Could not configure the private storage credential')
    for source in release.iterdir():
        if source.name in ('seed', 'data'):
            continue
        target = output / source.name
        shutil.copytree(source, target) if source.is_dir() else shutil.copy2(source, target)
    (output / 'data').mkdir()
    for source in (release / 'data').iterdir():
        if source.is_file():
            shutil.copy2(source, output / 'data' / source.name)
    (output / 'assets-release.json').write_text(json.dumps({'key':key,'sha256':digest}, indent=2) + '\n')
    print(json.dumps({'uploaded':True, 'compact_directory':str(output)}), flush=True)


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('release'); parser.add_argument('output')
    parser.add_argument('--cli', required=True); parser.add_argument('--bucket', required=True)
    args=parser.parse_args()
    upload(args.release, args.output, args.cli, args.bucket)

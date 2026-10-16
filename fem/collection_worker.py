"""Isolated collection solver entry point; preserves the existing solver snapshots."""
import argparse
import hashlib
import importlib
import json
from pathlib import Path


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--input',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    payload=json.loads(args.input.read_text(encoding='utf8'))
    if payload['ledger'].get('engine')!='collection_demo':
        raise ValueError('This worker accepts collection demonstration ledgers only.')
    for key,name in [('solver_code_sha256','solver.py'),('global_code_sha256','global_model.py'),
                     ('collection_code_sha256','collection_demo.py'),('worker_code_sha256','collection_worker.py')]:
        digest=hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
        if payload.get(key)!=digest:
            raise RuntimeError('Analytical source changed after input snapshot: '+name)
    name={'arch':'arch_demo','truss':'truss_demo'}.get(payload['ledger'].get('analytical_family'),'collection_demo')
    if name!='collection_demo':
        digest=hashlib.sha256(Path(__file__).with_name(name+'.py').read_bytes()).hexdigest()
        if payload.get('specialized_code_sha256')!=digest:
            raise RuntimeError('Specialized analytical source changed after input snapshot: '+name)
    result=importlib.import_module('fem.'+name).solve_demo(payload)
    temp=args.output.with_suffix('.tmp')
    temp.write_text(json.dumps(result,ensure_ascii=True,allow_nan=False,separators=(',',':')),encoding='utf8')
    temp.replace(args.output)
    print(json.dumps({k:result[k] for k in ['bridge_id','max_stress_MPa','max_deflection_mm','total_load_kN','total_reaction_kN']}))


if __name__=='__main__':main()

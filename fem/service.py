"""Local bounded jobs. Native OpenSees never runs inside the HTTP process."""
import csv
import hashlib
import io
import json
import os
import subprocess
import sys
import threading
import uuid
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

from import_data import ROOT, connect, sha
from fem.solver import CASES, concrete_E, settings


def utc():
    return datetime.now(timezone.utc).isoformat()


def encode(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False, separators=(',',':'))


class BusyError(ValueError):
    pass


class AnalysisService:
    def __init__(self, db_path, run_root=None):
        self.db_path = db_path
        self.run_root = Path(run_root or Path(db_path).parent/'analysis_runs')
        self.lock = threading.Lock()
        self.active = None
        self.current = None
        self.runtime = self.find_runtime()
        with closing(connect(db_path)) as db:
            db.executescript((ROOT/'fem/schema.sql').read_text(encoding='utf-8'))
            db.execute("UPDATE analysis_runs SET status='failed',finished_utc=?,error=? WHERE status IN ('queued','running')",
                       (utc(),'Server restarted before this run finished. Rerun the analysis.'))
            db.commit()

    @staticmethod
    def find_runtime():
        configured = os.environ.get('BRIDGE_FEM_PYTHON')
        if configured:
            return Path(configured).resolve()
        bundled = ROOT/'.venv-fem'/('Scripts/python.exe' if os.name=='nt' else 'bin/python')
        return bundled if bundled.is_file() else Path(sys.executable)

    def ledger(self):
        return json.loads((ROOT/'fem/beechwood.json').read_text(encoding='utf-8'))

    def freeze(self, options):
        ledger = self.ledger()
        source_hash = sha(ROOT/ledger['source_pdf'])
        if source_hash != ledger['drawing_sha256']:
            raise ValueError('The drawing changed. Recheck the material ledger before running.')
        # Ensure the current catalog agrees with the source files, not just the mesh names.
        manifest = ROOT/'data/bridges/beechwood/model_manifest.json'
        model = ROOT/'data/bridges/beechwood/model.glb'
        with closing(connect(self.db_path)) as db:
            assets = {r['kind']:r['sha256'] for r in db.execute('SELECT kind,sha256 FROM assets WHERE bridge_id=?',('beechwood',))}
            count = db.execute("SELECT COUNT(*) FROM components WHERE bridge_id='beechwood' AND source_id GLOB 'girder_[ABC][1234]'").fetchone()[0]
        hashes = {'drawing':source_hash, 'manifest':sha(manifest), 'model':sha(model)}
        if count != 12 or any(assets.get(k)!=v for k,v in hashes.items()):
            raise ValueError('Catalog/source mismatch. Reimport the bridge data before analysis.')
        return {'ledger':ledger, 'settings':settings(options), 'source_hashes':hashes,
                'solver_code_sha256':sha(ROOT/'fem/solver.py')}

    def info(self, bid):
        if bid != 'beechwood':
            return {'available':False, 'reason':'Structural inputs have not been reviewed for this bridge.'}
        ledger = self.ledger()
        with closing(connect(self.db_path)) as db:
            latest = db.execute("SELECT id FROM analysis_runs WHERE bridge_id=? ORDER BY created_utc DESC LIMIT 1",(bid,)).fetchone()
            history = [dict(r) for r in db.execute('''SELECT r.id,r.status,r.created_utc,i.snapshot_json FROM analysis_runs r
                JOIN analysis_inputs i ON i.input_hash=r.input_hash WHERE r.bridge_id=? ORDER BY r.created_utc DESC LIMIT 20''',(bid,))]
            for r in history:
                r['settings'] = json.loads(r.pop('snapshot_json'))['settings']
        return {'available':True, 'ledger':ledger, 'cases':CASES,
                'derived':{'girder_E_GPa':concrete_E(ledger['values']['girder_fc_psi'],ledger['values'])/1e9,
                           'deck_E_GPa':concrete_E(ledger['values']['deck_fc_psi'],ledger['values'])/1e9},
                'runs':history, 'latest':self.get(latest['id']) if latest else None}

    def get(self, run_id):
        with closing(connect(self.db_path)) as db:
            row = db.execute('SELECT * FROM analysis_runs WHERE id=?',(run_id,)).fetchone()
            if not row:
                return None
            out = dict(row)
            out.pop('result_path')
            out['summary'] = json.loads(out.pop('summary_json') or 'null')
            input_row = db.execute('SELECT snapshot_json FROM analysis_inputs WHERE input_hash=?',(out['input_hash'],)).fetchone()
            snapshot = json.loads(input_row[0])
            out['settings'] = snapshot['settings']
            try:
                out['current_inputs'] = hashlib.sha256(encode(self.freeze(snapshot['settings'])).encode()).hexdigest() == out['input_hash']
            except ValueError:
                out['current_inputs'] = False
            return out

    def start(self, bid, options):
        if bid != 'beechwood':
            raise ValueError('Only Beechwood has reviewed pilot inputs.')
        options = settings(options)
        if not self.runtime.is_file():
            raise ValueError('FEM Python runtime not found. Follow docs/fem.md to install the optional solver.')
        with self.lock:
            if self.active:
                raise BusyError('An analysis is already running. Wait for it to finish.')
            snapshot = self.freeze(options)
            payload = encode(snapshot)
            digest = hashlib.sha256(payload.encode()).hexdigest()
            run_id = uuid.uuid4().hex
            folder = self.run_root/run_id
            folder.mkdir(parents=True)
            (folder/'input.json').write_text(payload,encoding='utf-8')
            with closing(connect(self.db_path)) as db:
                db.execute('INSERT OR IGNORE INTO analysis_inputs VALUES (?,?,?)',(digest,bid,payload))
                db.execute('INSERT INTO analysis_runs(id,bridge_id,input_hash,status,created_utc) VALUES (?,?,?,?,?)',
                           (run_id,bid,digest,'queued',utc()))
                db.commit()
            self.active = run_id
            threading.Thread(target=self.worker, args=(run_id,folder),daemon=True).start()
        return self.get(run_id)

    def worker(self, run_id, folder):
        try:
            with closing(connect(self.db_path)) as db:
                db.execute("UPDATE analysis_runs SET status='running' WHERE id=?",(run_id,))
                db.commit()
            # No shell and no client-provided executable, arguments or file paths.
            args = [str(self.runtime),'-X','utf8','-m','fem.solver','--input',str(folder/'input.json'),'--output',str(folder/'result.json')]
            with (folder/'solver.log').open('w',encoding='utf-8') as log:
                self.current = subprocess.Popen(args,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
                try:
                    code = self.current.wait(timeout=180)
                except subprocess.TimeoutExpired:
                    self.current.kill()
                    self.current.wait()
                    raise RuntimeError('Solver exceeded the 180 second limit.')
            if code:
                tail = (folder/'solver.log').read_text(encoding='utf-8',errors='replace')[-2500:]
                if 'No module named' in tail:
                    raise RuntimeError('Optional solver is missing. Install requirements-fem.txt in .venv-fem using Python 3.12. See docs/fem.md.')
                raise RuntimeError('Solver failed; no result was accepted. Inspect the local run log.')
            result = json.loads((folder/'result.json').read_text(encoding='utf-8'))
            if not result['verification']['passed'] or len(result['members']) != 12:
                raise RuntimeError('Result verification failed.')
            summary = {k:result[k] for k in ('case_title','solver','max_stress_MPa','max_deflection_mm','total_load_kN','total_reaction_kN','node_count','element_count','verification')}
            with closing(connect(self.db_path)) as db:
                db.executemany('INSERT INTO analysis_member_results VALUES (?,?,?,?,?,?,?)',
                    [(run_id,m['component_id'],m['span'],m['line'],m['peak']['stress_MPa'],m['peak']['x_m'],m['max_deflection_mm']) for m in result['members']])
                db.execute("UPDATE analysis_runs SET status='completed',finished_utc=?,result_path=?,result_sha256=?,summary_json=? WHERE id=?",
                           (utc(),str(folder/'result.json'),sha(folder/'result.json'),encode(summary),run_id))
                db.commit()
        except Exception as exc:
            with closing(connect(self.db_path)) as db:
                db.execute("UPDATE analysis_runs SET status='failed',finished_utc=?,error=? WHERE id=?",(utc(),str(exc),run_id))
                db.commit()
        finally:
            self.current = None
            with self.lock:
                self.active = None

    def result_path(self, run_id):
        with closing(connect(self.db_path)) as db:
            row = db.execute("SELECT result_path,result_sha256 FROM analysis_runs WHERE id=? AND status='completed'",(run_id,)).fetchone()
        if not row:
            return None
        path = Path(row['result_path'])
        if not path.resolve().is_relative_to(self.run_root.resolve()) or not path.is_file() or sha(path)!=row['result_sha256']:
            raise ValueError('Stored result is missing or changed; rerun the analysis.')
        return path

    def csv(self, run_id):
        path = self.result_path(run_id)
        if path is None:
            return None
        result = json.loads(path.read_text(encoding='utf-8'))
        out = io.StringIO(newline='')
        writer = csv.writer(out)
        writer.writerow(['component_id','x_m','incremental_top_MPa','incremental_bottom_MPa','max_abs_fiber_MPa','downward_mm','sagging_kNm'])
        for m in result['members']:
            for p in m['samples']:
                writer.writerow([m['component_id'],p['x_m'],p['top_MPa'],p['bottom_MPa'],p['stress_MPa'],p['deflection_mm'],p['moment_kNm']])
        return out.getvalue().encode('utf-8')

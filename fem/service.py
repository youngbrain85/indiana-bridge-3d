"""Local bounded jobs. Native OpenSees never runs inside the HTTP process."""
import csv
import hashlib
import io
import importlib
import json
import os
import re
import subprocess
import sys
import threading
import uuid
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

from import_data import ROOT, connect, sha
from fem.solver import CASES, concrete_E, settings
from fem import minnich_demo


def utc():
    return datetime.now(timezone.utc).isoformat()


def encode(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False, separators=(',',':'))


class BusyError(ValueError):
    pass


def collection_engine(ledger):
    family = ledger.get('analytical_family', 'frame_shell')
    name = {'arch':'arch_demo', 'truss':'truss_demo'}.get(family, 'collection_demo')
    return name, importlib.import_module('fem.' + name)


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

    def ledger(self, bid='beechwood'):
        collection = self.collection_path(bid)
        if collection:
            return json.loads(collection.read_text(encoding='utf-8'))
        name = 'minnich.json' if bid == 'minnich-road' else 'beechwood.json'
        return json.loads((ROOT/'fem'/name).read_text(encoding='utf-8'))

    @staticmethod
    def collection_path(bid):
        if not isinstance(bid, str) or not re.fullmatch(r'[a-z0-9-]{1,80}', bid):
            return None
        path = ROOT/'fem/collection'/(bid+'.json')
        return path if path.is_file() else None

    def collection_registered(self, bid):
        if not self.collection_path(bid):
            return False
        with closing(connect(self.db_path)) as db:
            row = db.execute('SELECT workspace_enabled FROM bridges WHERE id=?',(bid,)).fetchone()
        return bool(row and row[0])

    def freeze(self, options, bid='beechwood'):
        if self.collection_registered(bid):
            from fem import collection_demo
            ledger = self.ledger(bid)
            hashes = {k:sha(ROOT/'data/bridges'/bid/name) for k,name in
                      [('drawing','drawings.pdf'),('manifest','model_manifest.json'),('model','model.glb')]}
            with closing(connect(self.db_path)) as db:
                assets = {r['kind']:r['sha256'] for r in db.execute('SELECT kind,sha256 FROM assets WHERE bridge_id=?',(bid,))}
                ids = {r[0] for r in db.execute('SELECT source_id FROM components WHERE bridge_id=?',(bid,))}
            expected = ledger.get('analyzed_component_ids',[])
            if (ledger.get('engine')!='collection_demo' or ledger.get('bridge_id')!=bid or
                ledger.get('source_hashes')!=hashes or any(assets.get(k)!=v for k,v in hashes.items()) or
                not expected or len(expected)!=len(set(expected)) or not set(expected)<=ids):
                raise ValueError('Drawing/model/catalog or analytical ledger changed. Reconcile the demonstration inputs first.')
            name, engine = collection_engine(ledger)
            snapshot = {'ledger':ledger,'settings':collection_demo.settings(options),'source_hashes':hashes,
                    'solver_code_sha256':sha(ROOT/'fem/solver.py'),'global_code_sha256':sha(ROOT/'fem/global_model.py'),
                    'collection_code_sha256':sha(ROOT/'fem/collection_demo.py'),'worker_code_sha256':sha(ROOT/'fem/collection_worker.py')}
            if name != 'collection_demo':
                snapshot['specialized_code_sha256'] = sha(ROOT/'fem'/(name+'.py'))
            return snapshot
        if bid == 'minnich-road':
            ledger = self.ledger(bid)
            hashes = {k:sha(ROOT/'data/bridges/minnich-road'/name) for k,name in
                      [('drawing','drawings.pdf'),('manifest','model_manifest.json'),('model','model.glb')]}
            with closing(connect(self.db_path)) as db:
                assets = {r['kind']:r['sha256'] for r in db.execute('SELECT kind,sha256 FROM assets WHERE bridge_id=?',(bid,))}
                ids = {r[0] for r in db.execute('SELECT source_id FROM components WHERE bridge_id=?',(bid,))}
            if hashes['drawing'] != ledger['drawing_sha256'] or any(assets.get(k)!=v for k,v in hashes.items()) or not set(ledger['analyzed_component_ids'])<=ids:
                raise ValueError('Minnich drawing/model/catalog changed. Reconcile the demonstration inputs first.')
            return {'ledger':ledger,'settings':minnich_demo.settings(options),'source_hashes':hashes,
                    'solver_code_sha256':sha(ROOT/'fem/solver.py'),'global_code_sha256':sha(ROOT/'fem/global_model.py'),
                    'demo_code_sha256':sha(ROOT/'fem/minnich_demo.py')}
        if bid != 'beechwood':
            raise ValueError('This bridge has no configured analysis model.')
        ledger = self.ledger()
        global_case=options.get('case','').startswith('global_')
        if global_case: ledger['global']=json.loads((ROOT/'fem/global.json').read_text(encoding='utf-8'))
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
        snapshot={'ledger':ledger, 'settings':settings(options), 'source_hashes':hashes,
                  'solver_code_sha256':sha(ROOT/'fem/solver.py')}
        if global_case: snapshot['global_code_sha256']=sha(ROOT/'fem/global_model.py')
        return snapshot

    def info(self, bid):
        collection = self.collection_registered(bid)
        if bid not in ('beechwood','minnich-road') and not collection:
            reasons = {
                'us421-wildcat':'The through-truss and box-beam approach require a dedicated truss/floor-system analytical model. A generic girder model would give the wrong load path.',
                'sr1-wabash':'The filled concrete arches require an arch/fill/spandrel analytical model and horizontal-thrust restraints. They are not assigned a generic girder calculation.'
            }
            return {'available':False, 'reason':reasons.get(bid,'Structural inputs have not been reviewed for this bridge. Partial map-only models are not whole-bridge FEM models.')}
        ledger = self.ledger(bid)
        with closing(connect(self.db_path)) as db:
            latest = db.execute("SELECT id FROM analysis_runs WHERE bridge_id=? ORDER BY created_utc DESC LIMIT 1",(bid,)).fetchone()
            history = [dict(r) for r in db.execute('''SELECT r.id,r.status,r.created_utc,i.snapshot_json FROM analysis_runs r
                JOIN analysis_inputs i ON i.input_hash=r.input_hash WHERE r.bridge_id=? ORDER BY r.created_utc DESC LIMIT 20''',(bid,))]
            for r in history:
                r['settings'] = json.loads(r.pop('snapshot_json'))['settings']
        if collection:
            from fem import collection_demo
            _, engine = collection_engine(ledger)
            return {'available':True,'demonstration':True,'engine':'collection_demo','ledger':ledger,'cases':getattr(engine,'CASES',collection_demo.CASES),
                    'defaults':collection_demo.settings({}),'parameters':engine.parameters_for_ledger(ledger),'default_family':'all',
                    'runs':history,'latest':self.get(latest['id']) if latest else None}
        if bid == 'minnich-road':
            return {'available':True,'demonstration':True,'ledger':ledger,'cases':minnich_demo.CASES,
                    'defaults':minnich_demo.settings({}),'parameters':minnich_demo.PARAMETERS,
                    'runs':history,'latest':self.get(latest['id']) if latest else None}
        ledger['global']=json.loads((ROOT/'fem/global.json').read_text(encoding='utf-8'))
        return {'available':True, 'ledger':ledger, 'cases':CASES,
                'defaults':settings({'case':'global_uniform'}),
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
                out['current_inputs'] = hashlib.sha256(encode(self.freeze(snapshot['settings'],out['bridge_id'])).encode()).hexdigest() == out['input_hash']
            except (ValueError, OSError, ImportError):
                out['current_inputs'] = False
            return out

    def start(self, bid, options):
        collection = self.collection_registered(bid)
        if bid not in ('beechwood','minnich-road') and not collection:
            raise ValueError('This bridge has no configured analysis model.')
        if collection:
            from fem import collection_demo
            options = collection_demo.settings(options)
        else:
            options = minnich_demo.settings(options) if bid=='minnich-road' else settings(options)
        if not self.runtime.is_file():
            raise ValueError('FEM Python runtime not found. Follow docs/fem.md to install the optional solver.')
        with self.lock:
            if self.active:
                raise BusyError('An analysis is already running. Wait for it to finish.')
            snapshot = self.freeze(options,bid)
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
                saved = db.execute('''SELECT r.input_hash, i.snapshot_json FROM analysis_runs r
                    JOIN analysis_inputs i ON i.input_hash=r.input_hash WHERE r.id=?''',(run_id,)).fetchone()
                if not saved:
                    raise RuntimeError('Registered analysis snapshot is missing.')
                frozen = json.loads(saved['snapshot_json'])
                frozen_hash = saved['input_hash']
                db.execute("UPDATE analysis_runs SET status='running' WHERE id=?",(run_id,))
                db.commit()
            def verify_input_file():
                payload = json.loads((folder/'input.json').read_text(encoding='utf-8'))
                if payload != frozen or hashlib.sha256(encode(payload).encode()).hexdigest() != frozen_hash:
                    raise RuntimeError('Run input changed after it was frozen in the database; result rejected.')
            verify_input_file()
            # No shell and no client-provided executable, arguments or file paths.
            module = 'fem.collection_worker' if frozen['ledger'].get('engine')=='collection_demo' else 'fem.solver'
            args = [str(self.runtime),'-X','utf8','-m',module,'--input',str(folder/'input.json'),'--output',str(folder/'result.json')]
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
            verify_input_file()
            bid = frozen['ledger']['bridge_id']
            ids=[m['component_id'] for m in result['members']]
            with closing(connect(self.db_path)) as db:
                registered={r[0] for r in db.execute('SELECT id FROM components WHERE bridge_id=?',(bid,))}
            demo = bid=='minnich-road' or frozen['ledger'].get('engine')=='collection_demo'
            expected=len(frozen['ledger']['analyzed_component_ids']) if demo else 72 if result['case'].startswith('global_') else 12
            if demo and set(ids)!={bid+':'+x for x in frozen['ledger']['analyzed_component_ids']}:
                raise RuntimeError('Demonstration member mapping failed.')
            if demo and (result.get('demonstration') is not True or result['verification'].get('field_validated') is not False):
                raise RuntimeError('Assumed-input result labels are missing.')
            if result['bridge_id']!=bid or result.get('snapshot')!=frozen or not result['verification']['passed'] or len(ids)!=len(set(ids)) or not set(ids)<=registered or len(ids)!=expected:
                raise RuntimeError('Result verification failed.')
            summary = {k:result[k] for k in ('case_title','solver','max_stress_MPa','max_deflection_mm','total_load_kN','total_reaction_kN','node_count','element_count','verification')}
            summary['demonstration'] = result.get('demonstration',False)
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
        writer.writerow(['component_id','x_m','top_or_max_MPa','bottom_or_min_MPa','absolute_stress_measure_MPa','downward_mm','moment_kNm','family','y_m','z_m','tension_MPa','compression_MPa',
                         'analysis_scope','assumed_input_demo','field_validated','load_case','pressure_kPa','load_factor'])
        for m in result['members']:
            for p in m['samples']:
                writer.writerow([m['component_id'],p['x_m'],p['top_MPa'],p['bottom_MPa'],p['stress_MPa'],p['deflection_mm'],p['moment_kNm'],m.get('family','girder'),*(p.get('xyz_m',[0,'',''])[1:]),p.get('tension_MPa',''),p.get('compression_MPa',''),
                                 result['scope'],str(result.get('demonstration',False)).lower(),str(result['verification'].get('field_validated',False)).lower(),result['case'],result['settings'].get('pressure_kPa',''),result['settings']['load_factor']])
        return out.getvalue().encode('utf-8')

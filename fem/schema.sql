-- Historical snapshots deliberately survive catalog reimports and component replacement.
CREATE TABLE IF NOT EXISTS analysis_inputs (
 input_hash TEXT PRIMARY KEY, bridge_id TEXT NOT NULL, snapshot_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS analysis_runs (
 id TEXT PRIMARY KEY, bridge_id TEXT NOT NULL,
 input_hash TEXT NOT NULL REFERENCES analysis_inputs(input_hash),
 status TEXT NOT NULL CHECK(status IN ('queued','running','completed','failed')),
 created_utc TEXT NOT NULL, finished_utc TEXT, error TEXT,
 result_path TEXT, result_sha256 TEXT, summary_json TEXT
);
CREATE TABLE IF NOT EXISTS analysis_member_results (
 run_id TEXT NOT NULL REFERENCES analysis_runs(id) ON DELETE CASCADE,
 component_id TEXT NOT NULL, span TEXT NOT NULL, line INTEGER NOT NULL,
 peak_abs_stress_mpa REAL NOT NULL, peak_x_m REAL NOT NULL,
 max_abs_deflection_mm REAL NOT NULL,
 PRIMARY KEY(run_id,component_id)
);
CREATE INDEX IF NOT EXISTS analysis_runs_bridge_created ON analysis_runs(bridge_id, created_utc DESC);

PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS bridges (
 id TEXT PRIMARY KEY, name TEXT NOT NULL, county TEXT NOT NULL,
 structure_id TEXT, designation TEXT, structure_type TEXT, waterway TEXT,
 latitude REAL NOT NULL, longitude REAL NOT NULL, owner TEXT, maintenance TEXT,
 ownership_data_year INTEGER, nbi_json TEXT NOT NULL, location_source_json TEXT NOT NULL,
 detail_status TEXT NOT NULL, detail_note TEXT, revision TEXT, scope TEXT,
 workspace_enabled INTEGER NOT NULL DEFAULT 1 CHECK(workspace_enabled IN (0,1)),
 deck_length_m REAL, spans INTEGER, assumptions_json TEXT NOT NULL,
 source_note TEXT, source_metadata_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS assets (
 id TEXT PRIMARY KEY, bridge_id TEXT NOT NULL REFERENCES bridges(id) ON DELETE CASCADE,
 kind TEXT NOT NULL, title TEXT NOT NULL, relative_path TEXT NOT NULL UNIQUE,
 mime TEXT NOT NULL, sha256 TEXT NOT NULL, size_bytes INTEGER NOT NULL,
 page_count INTEGER, original_path TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS models (
 bridge_id TEXT PRIMARY KEY REFERENCES bridges(id) ON DELETE CASCADE,
 asset_id TEXT NOT NULL REFERENCES assets(id), manifest_asset_id TEXT NOT NULL REFERENCES assets(id),
 units TEXT NOT NULL, axes_json TEXT NOT NULL, hidden_layers_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS member_groups (
 id TEXT PRIMARY KEY, bridge_id TEXT NOT NULL REFERENCES bridges(id) ON DELETE CASCADE,
 source_layer TEXT NOT NULL, label TEXT NOT NULL, sort_order INTEGER NOT NULL,
 UNIQUE(bridge_id, source_layer)
);
CREATE TABLE IF NOT EXISTS components (
 id TEXT PRIMARY KEY, bridge_id TEXT NOT NULL REFERENCES bridges(id) ON DELETE CASCADE,
 group_id TEXT NOT NULL REFERENCES member_groups(id), source_id TEXT NOT NULL,
 mesh_name TEXT NOT NULL, name TEXT NOT NULL, color TEXT,
 location_label TEXT, location_basis TEXT, basis TEXT, note TEXT,
 bounds_json TEXT NOT NULL, volume_m3 REAL, source_json TEXT NOT NULL,
 UNIQUE(bridge_id,source_id)
);
CREATE TABLE IF NOT EXISTS component_dimensions (
 component_id TEXT NOT NULL REFERENCES components(id) ON DELETE CASCADE,
 name TEXT NOT NULL, value_json TEXT NOT NULL, PRIMARY KEY(component_id,name)
);
CREATE TABLE IF NOT EXISTS component_documents (
 component_id TEXT NOT NULL REFERENCES components(id) ON DELETE CASCADE,
 asset_id TEXT NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
 pdf_page INTEGER NOT NULL CHECK(pdf_page > 0),
 PRIMARY KEY(component_id,asset_id,pdf_page)
);
CREATE TABLE IF NOT EXISTS coverage_items (
 id TEXT PRIMARY KEY, bridge_id TEXT NOT NULL REFERENCES bridges(id) ON DELETE CASCADE,
 feature TEXT NOT NULL, status TEXT, detail TEXT, sources_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS component_coverage (
 component_id TEXT NOT NULL REFERENCES components(id) ON DELETE CASCADE,
 coverage_id TEXT NOT NULL REFERENCES coverage_items(id) ON DELETE CASCADE,
 PRIMARY KEY(component_id,coverage_id)
);
CREATE TABLE IF NOT EXISTS reference_sources (
 id TEXT PRIMARY KEY, bridge_id TEXT NOT NULL REFERENCES bridges(id) ON DELETE CASCADE,
 title TEXT NOT NULL, url TEXT, metadata_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS import_log (
 id INTEGER PRIMARY KEY, completed_utc TEXT NOT NULL, summary_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS components_bridge_group ON components(bridge_id, group_id);
CREATE INDEX IF NOT EXISTS document_page ON component_documents(asset_id,pdf_page);

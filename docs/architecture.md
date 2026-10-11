# Architecture

The application is a local, read-only bridge review service. Python's `ThreadingHTTPServer` serves an allowlisted frontend, SQLite-backed JSON APIs and registered assets. PyMuPDF renders individual source PDF pages into a local cache. Three.js renders models; Leaflet provides the Indiana map.

## Relationships

`bridges` identifies each asset, source location, management information and detail status. `assets` stores relative file paths, SHA-256 hashes and page counts. `models` references the GLB and manifest. `member_groups` retains original source categories; `components` uses stable bridge-qualified IDs that match GLB mesh names.

`component_dimensions` stores original dimensional values and unit-bearing names. `component_documents` connects each component to actual PDF pages. `coverage_items` and `component_coverage` preserve explicitly supplied coverage links. `reference_sources` stores source citations. `import_log` records successful imports.

The five broad UI categories group existing source layers; they do not split, regenerate or rename geometric mesh identifiers. Specific locations are extracted only from explicit component names. Unknown locations remain unspecified.

`bridges.workspace_enabled` controls presentation. The registry supplies a boolean per bridge, defaulting to true. The importer persists it, and startup synchronizes registered settings and migrates older databases to schema 2. False hides the bridge from workspace selectors and all 3D links while preserving its map marker, basic attributes and every underlying source record. APIs and database exports retain the full collection. This flag is independent of geometric completeness or span count.

The catalog orders eligible records before map-only entries, and complete exterior models before incomplete models within each group. A fresh root visit opens the first eligible bridge. Explicit eligible deep links remain valid; a map-only `#bridge/<id>` link is replaced with `#map/<id>` before any detail or model request. Map location routes clear conflicting map filters and open a location popup.

## Portability and local state

The repository contains a portable registry and source assets. First launch creates SQLite and content-addressed runtime asset copies. Neither setup nor rebuilding depends on another checkout, an API key or the original author's filesystem.

Database and model APIs are read-only. New content is added through the validated importer. The service listens only on localhost, rejects non-local Host headers and serves registered paths only. PDF range requests and atomic preview generation support browser viewing without exposing arbitrary files.

The selected bridge is encoded in the URL; legacy last-selection browser storage is ignored so fresh visits consistently show a complete model first. The separate annotation page stores its notes in browser storage. API credentials, uploaded inspection data and operational maintenance histories are not part of this application.

## Source interpretation

Source uncertainties remain visible in coverage notes. A model marked complete is complete only within its stated exterior scope, not proof of as-built accuracy or bridge safety. The release translates metadata to English and retains the original dimensional values, PDF bytes and GLB bytes.

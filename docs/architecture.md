# Architecture

The application is a local, read-only bridge review service. Python's `ThreadingHTTPServer` serves an allowlisted frontend, SQLite-backed JSON APIs and registered assets. PyMuPDF renders individual source PDF pages into a local cache. Three.js renders models; Leaflet provides the Indiana map.

## Relationships

`bridges` identifies each asset, source location, management information and detail status. `assets` stores relative file paths, SHA-256 hashes and page counts. `models` references the GLB and manifest. `member_groups` retains original source categories; `components` uses stable bridge-qualified IDs that match GLB mesh names.

`component_dimensions` stores original dimensional values and unit-bearing names. `component_documents` connects each component to actual PDF pages. `coverage_items` and `component_coverage` preserve explicitly supplied coverage links. `reference_sources` stores source citations. `import_log` records successful imports.

The five broad UI categories group existing source layers; they do not split, regenerate or rename geometric mesh identifiers. Specific locations are extracted only from explicit component names. Unknown locations remain unspecified.

## Portability and local state

The repository contains a portable registry and source assets. First launch creates SQLite and content-addressed runtime asset copies. Neither setup nor rebuilding depends on another checkout, an API key or the original author's filesystem.

Database and model APIs are read-only. New content is added through the validated importer. The service listens only on localhost, rejects non-local Host headers and serves registered paths only. PDF range requests and atomic preview generation support browser viewing without exposing arbitrary files.

The UI stores the last selected bridge in browser storage. The separate annotation page stores its notes there as well. API credentials, uploaded inspection data and operational maintenance histories are not part of this application.

## Source interpretation

Source uncertainties remain visible in coverage notes. A model marked complete is complete only within its stated exterior scope, not proof of as-built accuracy or bridge safety. The release translates metadata to English and retains the original dimensional values, PDF bytes and GLB bytes.

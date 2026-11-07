# Third-party notices

## Software

- **Three.js 0.180.0** — MIT license. The bundled viewer retains legal comments. A copy of the license is in [web/vendor/THREE-LICENSE.txt](web/vendor/THREE-LICENSE.txt).
- **Leaflet 1.9.4** — BSD 2-Clause license. License text is included in [web/vendor/leaflet/LICENSE](web/vendor/leaflet/LICENSE).
- **PyMuPDF** — installed separately through `requirements.txt`; distributed under GNU AGPL v3 or a commercial license. See the package's own license and [licensing information](https://pymupdf.readthedocs.io/en/latest/about.html#license).
- **Supabase JavaScript client 2.117.3** (`@supabase/supabase-js` with its auth, PostgREST, storage, realtime and functions packages) — MIT license, bundled into `web/inspect.bundle.js` for the optional cloud sync of the inspection app. Copyright (c) Supabase. License texts are included in the packages under `node_modules/@supabase/`.
- **NumPy** and **Shapely** — BSD 3-Clause licenses; installed separately through `requirements-sheets.txt` to generate inspection sheets. They are not part of the shipped app.
- **esbuild** and **Playwright** are development dependencies installed separately. Their licenses are included in their packages.
- **IBM Plex Sans and IBM Plex Mono** (`web/vendor/fonts/`, Latin subset in WOFF2) — SIL Open Font License 1.1, Copyright © 2017 IBM Corp., Reserved Font Name "Plex". License text: [web/vendor/fonts/LICENSE.txt](web/vendor/fonts/LICENSE.txt).
- **taste-skill v2** (`.claude/skills/taste-skill/`, upstream commit `12af471`) — MIT license, Copyright (c) 2026 Leonxlnx. A Claude Code design skill used only as development tooling; it is not part of the shipped app. License text: [.claude/skills/taste-skill/LICENSE](.claude/skills/taste-skill/LICENSE). Source: https://github.com/leonxlnx/taste-skill
- **OpenSees / OpenSeesPy** — optional and installed separately using `requirements-fem.txt`; no solver binaries are bundled. Use is subject to the project's license, including its commercial redistribution terms. See the [official OpenSeesPy license notice](https://github.com/zhuminjie/OpenSeesPy/blob/openseespy/README.md).

## Source documents and maps

The project plan PDFs and standard drawing references are third-party engineering documents, not original software authored for this repository. Original titles, sheet notices and attribution are retained. Repository publication does not grant additional rights to those documents.

Plan provenance, source URLs where recorded, and hashes are in [data/sources.json](data/sources.json). The Beechwood plan set was supplied with the original project; its public download URL was not recorded. English metadata translations do not alter the source PDFs or GLB geometry.

State and county boundaries originate from the U.S. Census Bureau TIGERweb service. Retrieval provenance is retained in [data/map_sources.json](data/map_sources.json). Road tiles are requested from the USGS National Map transportation WMS; no road tile archive is bundled.

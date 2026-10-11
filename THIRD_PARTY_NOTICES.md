# Third-party notices

## Software

- **Three.js 0.180.0** — MIT license. The bundled viewer retains legal comments. A copy of the license is in [web/vendor/THREE-LICENSE.txt](web/vendor/THREE-LICENSE.txt).
- **Leaflet 1.9.4** — BSD 2-Clause license. License text is included in [web/vendor/leaflet/LICENSE](web/vendor/leaflet/LICENSE).
- **PyMuPDF** — installed separately through `requirements.txt`; distributed under GNU AGPL v3 or a commercial license. See the package's own license and [licensing information](https://pymupdf.readthedocs.io/en/latest/about.html#license).
- **esbuild** and **Playwright** are development dependencies installed separately. Their licenses are included in their packages.

## Source documents and maps

The project plan PDFs and standard drawing references are third-party engineering documents, not original software authored for this repository. Original titles, sheet notices and attribution are retained. Repository publication does not grant additional rights to those documents.

Plan provenance, source URLs where recorded, and hashes are in [data/sources.json](data/sources.json). The Beechwood plan set was supplied with the original project; its public download URL was not recorded. English metadata translations do not alter the source PDFs or GLB geometry.

State and county boundaries originate from the U.S. Census Bureau TIGERweb service. Retrieval provenance is retained in [data/map_sources.json](data/map_sources.json). Road tiles are requested from the USGS National Map transportation WMS; no road tile archive is bundled.

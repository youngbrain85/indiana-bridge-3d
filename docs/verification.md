# Release verification

## October 15, 2026: hosted deployment

- ChatGPT Sites publication succeeded at `https://indiana-bridge-3d.plumibex3.chatgpt.site`, with owner-private access. The separate Railway engine runs Python 3.12 and OpenSees 3.8.0 with persistent SQLite and private release storage.
- All 21 GLB range requests return the correct glTF header; all 16 workspace analysis endpoints return current completed results. Drawing-page rendering, original supplemental PDFs, CSV and SQLite exports work through the hosted gateway.
- Five actual cloud calculations passed numerical verification: Six Mile slab, Wabash arch, Wildcat truss, Beechwood whole bridge and Minnich frame/shell. Their completed results remained current after a new server deployment.
- The browser run form completed two further Six Mile calculations: doubling pressure from 1 to 2 kPa doubled displacement exactly, and restoring 1 kPa restored the baseline. The cloud catalog contains 82 runs after these seven verification runs, including all 75 seeded records.
- Desktop 3D, map navigation, Minnich's 197 mapped members with the All filter, mobile analysis controls and viewport fit pass without browser page errors. Existing family filters remain available.
- Requests directly to the engine without the gateway secret return 401; foreign-origin write requests return 403. The Site requires owner authentication. Runtime secrets are absent from Git and browser assets.
- Four hosted-adapter regression tests pass, including a real native FEM job. Raw solver/evidence bytes are preserved in Git and match the saved provenance fingerprints on Windows and Linux.

This verifies deployment and the existing numerical demonstrations; it does not add missing field information or validate the assumed structural inputs.

## October 15, 2026: complete researched collection and assumed-input FEM

- Live DB: 21 crossing records, 16 3D workspaces, 6,622 components, 248 groups, 11,728 primary page links, 9,499 dimensions, 137 coverage entries and 984 primary PDF pages. Five older partial models stay map-only.
- Five new GLBs and their source pages were independently reviewed; all 84 registered asset hashes match the live DB. Supplemental historical pages open their own original PDFs.
- Ten catalog/API tests, four legacy analysis API tests, five collection-service tests and four archived UI regressions pass. The 12 generic FEM ledgers pass eight dedicated tests (including all 24 default cases); arch passes seven tests and the revised truss passes six tests.
- All 16 workspaces pass the full browser regression. All 14 new FEM workspaces pass mapped-color, displacement, FE-mesh, export and input-control checks with no page errors. Five new drawing links and two supplemental PDFs were exercised. The load form doubles displacement at twice the pressure and then restores 1 kPa.
- The truss main-deck shell was extended to its complete display footprint, including end cantilevers. Revised uniform load is 341.768994 kN at 1 kPa; the old shorter-footprint runs remain archived.
- Both baseline cases are saved for all 14 new analytical models. An additional Beechwood global-uniform example is current, with 72 mapped components; the original Minnich example remains current.
- All original rows in every pre-update table are unchanged, including 41 analysis runs and 2,752 member results. The live database now has 74 runs and 4,872 member results. SQLite integrity and foreign keys pass. The three legacy solver source files are byte-for-byte unchanged from the pre-update snapshot.
- New result inputs are checked against the authoritative DB snapshot before launch and acceptance. Missing current source files mark results stale. Archived evidence and mesh return are regression tested.
- The generated `/collection-status` report has 5 model rows, 16 analytical-scope rows and 28 baseline-case rows. Desktop and 390 px mobile layout checks pass. Numerical convergence does not establish field validation or capacity.

## October 15, 2026: Fletcher Avenue and SR 10 additions

- Nine backend tests pass with a fresh 16-crossing database: 6,252 components, 196 groups, 10,986 page links, 9,014 dimensions and 117 coverage entries.
- The full browser regression loads all eleven workspace models, preserves the five map-only routes, and passes selection, visibility, source pages, mobile layouts, rapid switching and failed-road-service checks with no JavaScript page errors.
- `test_indiana_batch3_browser.cjs` additionally checks the 379-part Fletcher and 312-part SR 10 models, isolation of 16 and 36 girder segments, rendered source pages 98 and 59, amber coverage, unavailable FEM states, matching downloaded GLB bytes and county map thumbnails.
- Original source-file hashes, compiled binder hashes, model hashes and all new page references agree. Geometry reports record closed positive-volume meshes, GLB/manifest correspondence and constructed support contacts.
- Every row from the pre-import live database is preserved unchanged, including 41 existing analysis runs and 2,752 analysis member results. SQLite integrity and foreign-key checks pass. The saved Minnich demonstration remains available with current inputs.
- New models remain amber and are not FEM-ready. See [source states and limits](fletcher-sr10-models.md).

## Initial English release

The initial English release was checked against the then-existing nine-bridge collection.

- Fresh database creation from the bundled portable registry, without the original atlas directory.
- 9 bridges, 4,012 components, 106 source groups, 5,666 drawing-page links, 5,872 dimension records and 76 coverage items.
- Repeated imports, foreign keys, stable mesh IDs, PDF page bounds, registered asset routing, byte ranges and exports.
- All nine GLBs validated against manifests during import; browser loading and matching component counts for the four workspace models.
- Complete-first startup despite a previously saved incomplete/SR selection; selectors contain only the four eligible bridges.
- All five SR records retained on the map and in the database; old model links and collection links open map locations without loading their models.
- Presentation migration for existing databases, repeat synchronization, preserved source assets and status-based ordering.
- Group isolation, component search, real PDF page navigation, raycast selection, opacity and longitudinal sectioning.
- Mobile panel navigation, rapid bridge switching and graceful road-service failure.
- English interface and metadata scan, plus checks for private workstation paths and credentials before publication.
- PDF and GLB SHA-256 comparison with the existing source collection; geometry and plan content are unchanged.

Commands are documented in the README. Detailed test output and screenshots are generated under `data/` and are excluded from Git. No structural analysis or field validation is implied by these software checks.


## Beechwood FEM pilot

- Six physics tests include ten closed-form checks, transformed section sanity, all input evidence, three actual cases, force/moment balance, mesh refinement, symmetry, stress signs and linear load scaling.
- Three service tests cover real solver execution, frozen inputs, result hashes, persistence through catalog reimports, JSON/CSV export, rejected invalid/cross-origin requests and interrupted-job recovery.
- A separate browser test runs all three cases, reopens saved results, checks all twelve component mappings, deformation magnification, restoring original geometry/materials, member selection, mobile layout and clearing results on a bridge switch.
- The original nine backend tests and four-model browser regression still apply.

These checks verify the stated incremental beam model numerically. They do not validate actual bridge support stiffness, effective prestress, construction history, local stress concentrations or field condition. See [analysis scope](fem.md).

## Connected model and geometry correction

`test_global_fem.py` checks independent frame/shell/prestress benchmarks, complete foundation connectivity, all 11 loaded member families, eccentric transverse distribution, signed staged superposition, foundation reactions, local mesh warnings and actual GLB column-axis coordinates against PDF 38. `test_global_browser.cjs` executes all three whole-bridge cases and checks 72 mapped parts, family filtering, actual mesh display, deformation, exports and the correction report.

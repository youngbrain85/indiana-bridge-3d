# Release verification

The English release is checked against the existing nine-bridge collection.

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

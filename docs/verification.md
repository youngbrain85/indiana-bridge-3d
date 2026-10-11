# Release verification

The English release is checked against the existing nine-bridge collection.

- Fresh database creation from the bundled portable registry, without the original atlas directory.
- 9 bridges, 4,012 components, 106 source groups, 5,666 drawing-page links, 5,852 dimension records and 76 coverage items.
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

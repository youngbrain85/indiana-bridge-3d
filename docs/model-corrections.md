# Drawing-confirmed Beechwood geometry correction

The transverse spacing between the two columns at each interior bent was misread as **17 ft 6 in**. The dimensioned elevation on **PDF page 38 / printed sheet 37** specifies **22 ft between column centers**. The 33 ft cap is divided into 5 ft 6 in + 22 ft + 5 ft 6 in. The nearby 17 ft 6 in dimension describes the central cap step in plan, not column center spacing.

| Corrected objects | Count | Before | After | Evidence |
|---|---:|---|---|---|
| Bent 2 and 3 columns | 4 | Transverse centers ±8.75 ft | ±11 ft; 22 ft center spacing | PDF 38 elevation |
| Concrete drilled shafts | 4 | Aligned at ±8.75 ft | Moved with columns to ±11 ft | PDF 38 section/elevation |
| Rock sockets | 4 | Aligned at ±8.75 ft | Moved with columns to ±11 ft | PDF 38 section/elevation |
| Permanent steel casings | 4 | Aligned at ±8.75 ft | Moved with shaft cores to ±11 ft | PDF 38 section |
| Debris walls | 2 | Cut around the incorrectly spaced columns | Rebuilt with circular column intersections removed; 17.5 ft clear at the longitudinal centerline | PDF 38 elevation |

Each column/foundation line moves outward **2.25 ft (0.6858 m)**. The original diameters, vertical elevations and cap outline remain as dimensioned. The wall clear distance is 22 − 4.5 = 17.5 ft; it is different from center spacing.

The correction updates the actual downloadable GLB, component bounds and dimensions, embedded GLB metadata, SQLite catalog and preview. It is not a display-only translation. The component IDs remain stable, so drawing links and tree selections still identify the same objects. Old FEM runs are archived by changed asset hashes and are not automatically recolored onto the revised model.

The correction record, before/after SHA-256 and all 18 component IDs are embedded in `model_manifest.json`. `scripts/correct_beechwood_columns.py` reproduces the correction from the previous version and is idempotent on an already corrected version. Unrelated geometry buffers are preserved. Source drawing bytes are unchanged.

Verification checks actual GLB vertex bounds as well as the manifest. All four coaxial column/shaft/socket/casing assemblies are centered at ±11 ft. Both regenerated walls are watertight. The connected FEM model independently uses the same 22 ft spacing.

[Open source PDF at page 38](/assets/beechwood/drawing#page=38) · [Download corrected full GLB](/assets/beechwood/model) · [Open bridge](/#bridge/beechwood)

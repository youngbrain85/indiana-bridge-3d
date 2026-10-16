# Four additional Indiana crossings

Four whole multi-span crossings were added to the local application on October 15, 2026. All remain **More detail needed** (amber). Whole-crossing coverage does not mean every exterior detail is complete.

| Crossing | Modeled state | Whole structure | Selectable objects | Primary PDF |
|---|---|---|---:|---:|
| SR 8 / Yellow River | 1997 rehabilitation | Five spans, seven W840x193 beam lines, six supports | 331 | 28 pages |
| SR 1 / Wabash River | 2004 roadway reconstruction over retained arches | Four concrete arch barrels, spandrel walls, roadway and two sidewalks | 78 | 50 pages |
| US 50 EB / Tanners Creek | 2014 reconstruction design | Five spans, 35 Bulb-T beams, six bents, asymmetric sidewalk | 283 | 149 pages |
| Minnich Road NB/SB / I-469 | **Proposed 2026** rehabilitation | Four spans, eight girder lines, two directional inventories under a continuous proposed deck | 474 | 62 pages |

The object count includes grouped connections and architectural panels. It is not the number of fabricated pieces, bearings, or a material quantity takeoff. After this four-crossing batch, the library had 14 crossing records, nine 3D workspaces and five preserved map-only partial models. The subsequent [Fletcher / SR 10 addition](fletcher-sr10-models.md) increases those totals to 16 records and eleven workspaces. Minnich Road is one crossing record associated with two NBI structure IDs.

## Source and version boundaries

- **SR 8:** primary [INDOT existing-plans bundle 9549726](https://erms12c.indot.in.gov/viewdocs/View12.aspx?Id=9549726). PDF 5–6 establish the 1997 metric layout; 8–10 the bents; 11–13 the steel and bearings; 25 the shop details. The 2026 overlay is stored separately and is not added to the 1997 deck. The individual metric span callouts sum to 80.294 m; the framing total differs by 3 mm. The 80.996 m floor envelope is a separate dimension.
- **SR 1:** primary [historical bundle 9548291](https://erms12c.indot.in.gov/viewdocs/View12.aspx?Id=9548291). Original arch details at PDF 8–9 are distinguished from the 2004 reconstruction at 23–24, 29–38. PDF 40–50 describe a separate pedestrian bridge and were excluded. The 21.946 m clear arch spans are distinct from pier-center distances and the 108.4834 m later overall floor envelope. The 2026 overlay is not modeled.
- **US 50 EB:** primary [historical bundle 9548069](https://erms12c.indot.in.gov/viewdocs/View12.aspx?Id=9548069). The model uses the 2014 Bulb-T reconstruction subset, particularly PDF 107–109, 117, 121, 125, 129–133 and 139–140. Earlier construction eras and the adjacent westbound bridge are excluded. The 72 ft 2 in deck has seven beam lines with different outer overhangs, an offset crown and a 13 ft 8 in sidewalk. The 2026 overlay and revision are separate references.
- **Minnich Road:** primary [62-sheet package 9721535](https://erms12c.indot.in.gov/viewdocs/View12.aspx?Id=9721535). PDF 19–20 define the proposal, 25–33 the steel, 34 bearings, 47–52 rails and 56–61 approaches. Sheet 20 explicitly eliminates the existing longitudinal deck joint. The new end-span girders have tapered webs; the middle spans retain existing plate girders. These November 2026 letting plans are **not evidence of completed construction**.

Coordinates and state highway agency ownership/maintenance associations come from dated **2025 NBI** records. The local GLBs use local coordinates and do not contain a surveyed world placement transform.

## What still needs work

| Crossing | Principal unresolved items |
|---|---|
| SR 8 | Original central-pier and footing dimensions; fixed shoes; exact retained diaphragm rows; local seat levels; wing flare, transitions, drainage and terminals. |
| SR 1 | Original multi-radius arch setting-out and haunch thickness; end floor/abutment reconciliation; cutwaters; precise rail relief/spacing; municipal lighting, gauge well and drainage. The arch curve is a documented approximation. |
| US 50 EB | Exact cap steps and source seat elevations; retained/widened seams; end-bent wings and support diaphragms; drainage, lighting, sidewalk ramps and railing hardware. |
| Minnich Road | Original intermediate-pier/foundation plans are absent. Column arrangement and dimensions are provisional. Exact retained flange schedule, upper-flange kink, Span D section details, K frames, bearing shims, wingwalls, approach offsets, transitions and drainage need reconciliation. |

This geometry-import batch generated no FEM results, inspection records or condition ratings. A later [Minnich Road assumed-input FEM demonstration](minnich-fem-demo.md) is tracked separately. Approximate members are explicitly identified in each component's **Modeling basis** and notes. Unknown driven pile tips are omitted. Design foundation envelopes and concealed arch fill are hidden by default.

## Files and reproduction

Each `data/bridges/<id>/` directory contains:

- `model.glb`, `model_manifest.json` and an actual rendered `preview.png`.
- Unmodified `drawings.pdf`; supplementary PDFs retain their own filenames and hashes.
- `source_ledger.json`: design state, whole-bridge dimensions, source pages and limits.
- `geometry_verification.json`: exported-artifact checks, counts, contact and clearance measurements.

With NumPy, trimesh, Shapely and mapbox-earcut installed, regenerate the four GLBs and manifests with:

```sh
python scripts/build_indiana_batch2.py
```

Regeneration does not change the database automatically. Import only a registry subset containing the new bridge IDs when updating a populated local database: the normal importer replaces each included bridge and cascades its dependent records. Back up the database first. A fresh installation can continue to import the full bundled registry normally.

## Verification

The generated GLBs are reopened and checked for finite coordinates, closed positive-volume meshes, matching manifest names and bounds. IDs use characters that survive Three.js GLTFLoader name sanitization. Girder counts and bearing counts are checked, and girder vertices are compared with the modeled deck soffit. Constructed bearing-to-girder contacts are checked separately. These are geometry consistency checks, not verification of source completeness or physical fit.

Browser checks cover all four GLBs, component selection, original PDF page rendering, and isolation of the four Wabash arches as primary structure. The complete existing app regression suite also covers map-only behavior, complete-first ordering, visibility, drawings, clipping and offline map fallback. Existing database rows, including stored FEM records, are compared against the pre-import backup.

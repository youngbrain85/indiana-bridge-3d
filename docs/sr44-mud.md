# SR 44 over Mud Creek

Open `http://127.0.0.1:8766/#bridge/sr44-mud` with the local server running.

This is a reconstruction of the **2018 rehabilitation design**, based on INDOT contract B-38321 / designation 1500342, approved August 22, 2017. The drawing structure number is **044-70-06634 A**. The 2025 NBI and later 2026 overlay plans identify suffix B; the model does not claim to be a survey of that later state.

## Modeled geometry

| Element | Implementation | Main drawing pages |
|---|---|---|
| Bridge layout | 3 spans: 49 ft 9 in / 50 ft / 49 ft 9 in; 151 ft 1 in deck; 46 ft 6 in width; 15-degree right skew | 9–11 |
| Deck | Continuous 8-in slab, 2% crown and 200-ft crest vertical curve | 9, 27, 29 |
| Main steel | Seven W27x94 beam lines, each split at the two field splices | 17–19 |
| Field connections | 14 eight-plate splice assemblies; 104 nominal bolts per splice, 1,456 total | 19 |
| Diaphragms | 48 C15x33.9 channels; connection plates and nominal bolts | 17, 20 |
| Bearings | 28 elastomeric pads, load plates, varying shim stacks and pier side retainers | 22 |
| Substructure | Two wall piers, retained stepped caps, semi-integral end diaphragms and wings | 12–16, 23–24 |
| Foundations | Two footings and 58 design piles; hidden by default | Original 1980 PDF, 9 and 11 |
| Roadside concrete | FC barriers, four tapered TFC transitions, two skew-to-square approach slabs and extensions | 31–33; E706-TTFC |

The GLB contains **383 selectable mesh objects**, including grouped fastener assemblies. This is an object count, not the number of manufactured pieces. Units are metres. Native coordinates use X along station, Y toward beam 1, and Z upward from elevation 885 ft; GLB coordinates are Y-up.

## Remaining detail and source uncertainty

- **Seat/haunch reconciliation:** the retained concrete levels are explicitly approximate, and the shim table requires field verification. Their combination produces a minimum modeled deck-to-flange clearance of approximately 2.38 mm, below the nominal 19.05 mm (3/4 in) minimum haunch on the section. No beam passes through the deck, but these interfaces are not dimensionally resolved. Do not treat the model as a fabrication fit check or a validated FEM input.
- Loaded beam geometry is interpolated between supports using the road profile. Unloaded shop camber and screed construction-deflection allowances are not used as finished road elevations.
- Wing position, cap step boundaries, channel flange taper, root fillets and skew connection folds are simplified. Internal reinforcement, embedded shear studs, threads, washers, holes, weld beads and internal pad laminations are excluded.
- Approach TGB steel guardrail/terminals, drain outlets, drip-bead recesses, east approach curbs, riprap, backfill and terrain are not modeled.
- Historical pile lengths/tips are design indications, not verified driven values. Colors are visualization choices.

For these reasons, the bridge is **amber / more detail needed** on the map. Its three-span geometry is enabled in the workspace; the older five partial SR records retain their map-only behavior.

## Evidence and reproducibility

- [Primary 34-page rehabilitation plans](https://erms12c.indot.in.gov/viewdocs/View12.aspx?Id=9552113)
- [Original 1980 plans](https://erms12c.indot.in.gov/viewdocs/View12.aspx?Id=9552112), pp.9 and 11, for retained foundations and wall ends. Use the 2017 plan's -0.57 ft adjustment when interpreting the older levels.
- [INDOT E706-TTFC, September 2013](https://www.in.gov/dot/div/contracts/standards/drawings/sep20/e/700e/e700%20combined%20pdfs/E706-TTFC.pdf), pp.1–2, for barrier transitions.
- [Nucor-Yamato nominal shapes catalog](https://www.nucoryamato.com/StaticData/catalog.pdf), pp.21 and 47, for section dimensions; this does not identify the actual fabricator.
- [2026 overlay plan](https://erms12c.indot.in.gov/viewdocs/View12.aspx?Id=9683607), supplementary reference only.

The source PDFs are retained beside the model. Per-part links in the app refer to pages of the primary 34-page plan set; supplemental files and source hashes are listed in the manifest. `geometry_verification.json` records mesh checks, bearing contact checks and source/model hashes.

Regenerate with `python scripts/build_sr44_mud.py` after installing `numpy trimesh shapely mapbox-earcut`. This writes the GLB, manifest and geometry verification file; it does not import or replace the live database. The app itself needs only its normal runtime dependencies.

Integration used a registry containing only `sr44-mud`, with a SQLite backup first, preserving the other nine bridges and existing analysis records. A full `import_data.py` invocation rebuilds registry bridges and should be preceded by a database backup.

# Indiana collection completion and assumed-input FEM

All twelve crossings in the October 15 research register have been processed. The app now contains **21 crossing records, 16 3D workspaces and five older map-only fragments**. This is the researched collection, not the complete Indiana bridge inventory. Beechwood remains the only green exterior model; the new models remain amber.

Open the app at `http://127.0.0.1:8766/`. The generated [collection results report](http://127.0.0.1:8766/collection-status) links each workspace, both baseline pressure cases and frozen JSON/CSV results.

## Five final model additions

| Crossing | Modeled state | Main span(s), m | Display parts | Source and limitations |
|---|---|---:|---:|---|
| US 35 / Deer Creek | Proposed 2026 replacement | 35.052 | 72 | Issued 36-page plans; four BT48x49 profiles, integral end bents and embedded steel bearing assemblies. Pile cutoff, small connection/rail details and camber remain simplified. |
| US 224 / Eight Mile Creek | Retained CB21 structure with proposed 2026 overlay/repairs | 12.4968 | 91 | Current 17-page and historical 15-page PDFs. Six actual hollow CB21 profiles, supports, coping and overlays. Historical PDF 9548292 p.8 controls the box section. Small beam-end/repair details simplified. |
| Virginia Avenue / I-65 NB–I-70 EB | Proposed 2026 deck over retained welded steel | 34.7472 | 146 | Current 49-page and historical 81+23-page sources. Nine girders with distinct Girder 1 and flange zones, cross frames and bearings. Historical bundle also contains unrelated work; not all pages are bridge detail. |
| SR 44 / Branch of Little Blue River | Proposed 2026 integral slab replacement | 9.144 | 37 | Issued 29-page package; gross 20 in slab, two bents and 16 pipe piles. Wearing allowance excluded from analytical slab stiffness. Wing/rail/notch details simplified; pile restraint hypothetical. |
| SR 1 / Six Mile Creek | Overlay-era envelope with hypothetical structural scaffold | 6.664875 + 8.5 + 6.664875, assumed | 24 | Only a 10-page overlay package and NBI. Type 201 means continuous concrete slab, correcting the initial beam classification. The 450 mm slab, exact span split, support walls and foundations are assumptions. |

These five add **370 parts** and **141 primary PDF pages**. The complete database holds 6,622 components, 248 groups, 11,728 primary component-page links, 9,499 dimensions and 137 coverage entries. Primary PDF total: 984 pages. Supplemental original PDFs preserve independent numbering and are linked directly from component properties/drawings.

Six Mile's cover identifies `001-90-07052 B` / NBI `000370`. A copied identifier on p.4 points to the Wabash bridge. That conflict is recorded; it does not justify using Wabash geometry. Deck envelope dimensions are source based, while detailed structure remains hypothetical.

Source ledgers and geometry verification live in each `data/bridges/<id>` folder. Models are checked for GLB/manifest ID agreement, finite coordinates and valid closed display meshes. These checks establish data consistency, not complete detailing or structural validity.

## Analytical coverage

| Analytical model | Mapped components | Method and scope |
|---|---:|---|
| Beechwood | 72 global / 12 in preserved girder pilot | Existing dedicated connected beam/shell model with supports and foundations. A new full-bridge 1 kPa example is saved; original results remain. |
| Minnich Road | 197 | Existing assumed-input deck/girder/cross-frame/bearing/cap/column model; fixed or elastic bases. |
| 21st Street / I-465 | 59 | Bridge-specific connected deck/beam/support idealization. |
| US 52 / Mud Creek | 48 | Slab modules and support walls/beds; no invented longitudinal girders. |
| SR 44 / Mud Creek | 56 | Continuous steel/deck/support model for the selected rehabilitation state. |
| SR 8 / Yellow River | 122 | Continuous steel/deck/support model. |
| US 50 EB / Tanners Creek | 136 | Explicit Bulb-T section and support idealizations; selected span continuity assumption recorded. |
| Fletcher Avenue | 44 | Deck, source-based girder sections, intermediate wall pier and end supports. |
| SR 10 / I-65 | 74 | Four spans, explicit intermediate piers and integral end conditions. |
| US 35 / Deer Creek | 19 | Deck, four explicit BT profiles, integral caps and 12 assumed HP pile stubs. Embedded bearing assemblies are not assigned elastomer pressure. |
| US 224 / Eight Mile Creek | 23 | Structural slab, six hollow profiles with void subtraction, supports and bearings. Overlay stiffness is excluded. |
| Virginia Avenue | 30 | Deck, nine piecewise I-girder sections, abutment walls and 18 bearings. |
| SR 44 / Little Blue branch | 19 | Structural slab, two integral caps and 16 hollow pipe-pile sections. |
| SR 1 / Six Mile Creek | 5 | Hypothetical continuous slab and four walls. No original support/thickness validation. |
| SR 1 / Wabash River | 4 | Four curved ShellMITC4 arch barrels only. Eight independently restrained springing lines; deck/fill/shared-pier interaction excluded. |
| US 421 / Wildcat Creek | 190 | Main truss and complete main-deck footprint, floorbeams, stringers, rakers, lower bracing and four bearings. Approach spans/substructure excluded. |

All other displayed components are gray in the analysis overlay. Stress on a beam means axial plus biaxial nominal fiber stress; shell stress is a principal surface envelope recovered from membrane/bending resultants; bearing stress is mean pressure. These measures are not interchangeable strength checks.

Fourteen new models have **28 baseline cases**, full footprint and left half at 1 kPa. Materials default to assumed concrete E = 30 GPa and steel E = 200 GPa where applicable. Poisson ratios, sections, restraint stiffness, composite behavior and continuity assumptions are frozen in the ledgers. Parameters that do not affect a model are hidden. No self-weight, prestress history, traffic vehicle, cracking, fatigue, buckling or load rating is implied by these pressure increments.

Wabash's direct projected-barrel pressure is an isolated barrel study, not a deck-to-fill load-transfer model. Wildcat uses full main-deck shell cantilevers beyond the bearing lines; its truss remains 125 ft bearing-to-bearing. The original shorter-deck analytical results are preserved as archived snapshots, with newer complete-footprint results current.

## Numerical and UI verification

- Each accepted solve checks connectivity, force/moment equilibrium, analytical benchmarks and bounded displacement refinement. Nonconvergence beyond the required threshold rejects the result. Local peak comparisons exceeding 5% remain warnings.
- Generic collection tests execute all 24 beam/slab cases, plus load/material/support sensitivity, symmetry, explicit hollow sections and continuity checks. Dedicated arch/truss tests verify their respective footprints, thrust/axial behavior and load paths.
- All 16 3D workspaces load and match their DB components. Five map-only routes retain their prior behavior. New source pages, supplementary PDF routes, model selection, clipping, mobile layouts and model exports are checked.
- All 14 new FEM workspaces display mapped fields, actual FE meshes and CSV exports with no JavaScript page errors. The Six Mile browser form doubles computed displacement when pressure doubles, then restores the default 1 kPa example.
- API tests cover source hashes, member mapping, registered local document routes, invalid inputs and real isolated solver jobs. Mutating a queued run file cannot override its DB snapshot. Missing current source files mark saved results stale instead of breaking history.
- Archived UI views show their own frozen evidence, scope and source pages. Returning from an archived FE mesh clears the mesh legend and restores the current GLB without stale colors.

An equilibrium pass checks the equations that were solved. It does not verify real boundary conditions or material properties. The default fixed/elastic foundation scenarios are assumptions; local stress concentrations near restraints or thickness steps remain especially sensitive.

## Reproduction

Use the app's documented Python runtime and the optional Python 3.12 `.venv-fem` environment. No AI API key is needed for the OpenSees calculations.

```powershell
python scripts/build_remaining_concrete.py
python scripts/build_remaining_virginia_slab.py
python scripts/build_sr1_six_mile.py
python scripts/build_collection_ledgers.py
python scripts/build_arch_ledger.py
python scripts/build_truss_ledger.py
python import_data.py
python server.py --port 8766
```

Model rebuilding uses the locally acquired original sources documented by each builder. Import after rebuilding updates source hashes; old analysis snapshots remain historical. For the active collection update, only the five new records were imported, and the existing DB was backed up first.

```powershell
python -m unittest test_manager test_fem_service test_collection_service
.venv-fem/Scripts/python.exe -m unittest test_collection_demo test_arch_demo test_truss_demo
node test_collection_ui.cjs
node test_browser.cjs
node test_indiana_batch3_browser.cjs
node test_collection_browser.cjs
python scripts/build_collection_report.py
```

Browser tests need Playwright and can use `BROWSER_EXECUTABLE` to select a local browser. The collection browser test adds two labeled Six Mile demonstration runs, then leaves the default example current. Other report generation is read-only against the live API.

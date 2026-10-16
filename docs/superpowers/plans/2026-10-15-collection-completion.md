# Indiana Collection Completion Implementation Plan

> **For agentic workers:** Use the dispatching-parallel-agents workflow for the independent asset tasks, with root performing integration and review. Preserve the populated working directory and existing user changes.

**Goal:** Process all five remaining researched candidates and provide working, explicitly assumed-input FEM demonstrations wherever a defensible analytical topology can be constructed.

**Architecture:** Reuse the current GLB/manifest/import pipeline and OpenSees frame/shell infrastructure. New analytical ledgers freeze geometry, material, connectivity and support assumptions independently of display meshes. Existing Beechwood and Minnich models and runs remain preserved.

**Tech Stack:** Python, NumPy/trimesh, PyMuPDF, OpenSeesPy, SQLite, Three.js and Playwright.

**Spec:** User instruction of October 15, 2026: process all remaining bridges and run FEM where possible using approximate information. Prior constraints: English app; amber incomplete geometry; no invented observations; preserve existing models and FEM history.

## Global constraints

- Work in the existing authorized local application on codex/initial-release; do not commit, push or discard unrelated changes.
- Backup live SQLite before import; import only newly added candidate records.
- Model source-design eras explicitly. No proposed design is labeled completed construction.
- All approximation and material/support assumptions visible in English ledgers, UI and exports.
- Linear incremental pressure demonstrations, not load ratings or full stress histories. Do not assign solid stress to a rendered mesh without a real FE solve.
- Keep the five pre-existing map-only partial models as map-only. Do not represent incomplete fragments as whole-bridge FEM.
- Each modeling worker owns a disjoint build script and bridge directories; only root edits registry, service/UI and live DB.
- Uniform and left-half deck pressure cases, material/stiffness editing, frozen inputs, real equilibrium/convergence checks, saved results and actual FE mesh rendering.

## Tasks

- [x] 1. Model US 35 / Deer Creek and US 224 / Eight Mile Creek from current/historical sources. Deliver portable assets, provenance, source pages, geometry checks and summary JSON; no live DB edits.
- [x] 2. Model Virginia Avenue and SR 44 / Branch of Little Blue River from appropriate design states with the same deliverables.
- [x] 3. Review SR 1 / Six Mile Creek overlay and inventory data. Model only supported geometry plus an explicitly labeled hypothetical structural scaffold if original details remain absent; identify every assumed support/span arrangement.
- [x] 4. Add reusable assumed-input deck/beam FEM solver and per-bridge ledger builder, compatible with existing result schema. Preserve actual intermediate support locations and member identities. Exclude unreviewed arch/truss connectivity from the generic beam solver; record specific reasons unless a dedicated analytical model is implemented.
- [x] 5. Integrate models into registry and live DB; integrate new analysis ledgers into service, result verification, UI and explanation pages. Preserve Beechwood/Minnich snapshot compatibility where possible, or show honest stale-code status without removing runs.
- [x] 6. Run both pressure cases for every newly supported bridge; inspect equilibrium, displacement convergence, stress limitations, mesh display, exports and mappings. Repair failed topologies rather than reporting failed runs as successful results.
- [x] 7. Review final geometry/source links and all changed analysis paths, run existing relevant regression tests, compare old DB records to backup, update candidate register and write collection status/results report.

## Review focus

- Intermediate piers must participate in load path; simply-supported vs continuous behavior is explicit.
- Box/U/Bulb-T visual bounding boxes must not be mistaken for solid rectangular sections; structural sections need explicit assumptions or profile properties.
- Skew/local station offsets and multiple deck panels must map correctly to FE nodes and selected GLB members.
- Changed parameters must affect FE response; all saved exports retain assumed-input label and snapshots.
- Arch/truss and missing-original-plan cases must not silently receive inappropriate generic girder models.

## Outcome

All seven tasks are complete. Dedicated arch and main-truss analytical models were implemented in addition to the generic collection solver. The five new models were imported without changing any prior DB row. See docs/collection-completion.md and the live /collection-status report. Saved snapshots and local-stress limitations remain explicit. No commit or push was performed.

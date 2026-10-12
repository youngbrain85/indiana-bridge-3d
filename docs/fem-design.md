# Beechwood structural analysis pilot

The requested first implementation uses the existing bridge, its original drawings and official material references to calculate and display structural response. Drawing values take precedence; missing material properties are explicitly estimated. This implements the first global-analysis step of the previously reviewed feasibility study.

## Scope and interpretation

Four longitudinal beam lines represent the twelve BT 36x49 girders. OpenSees performs linear elastic Euler–Bernoulli analysis. There is no transverse grillage, shell mesh, soil model, capacity check or local stress concentration analysis in this pilot. Uniform transverse loading is distributed by tributary width. The visual GLB is only a component locator, never the finite-element mesh.

Three independent load cases are available:

1. Bare girder self-weight, on the drawing's individual bearing centers before composite action. Loads include the small girder end overhangs. Concrete stiffness uses the specified 28-day strength; this is a mature-beam gravity increment, not transfer-stage stress or net camber.
2. A 1 kPa uniform test pressure on the 33 ft deck width, after composite action.
3. The drawing's 35 psf future wearing surface, assumed over the 30 ft clear roadway, after composite action.

Cases 2 and 3 use full elastic continuity at the internal bent centerlines and either free or fully restrained end rotations. These are two idealized sensitivity scenarios, not confirmed integral-abutment stiffness or guaranteed response bounds. Vertical support movement is zero. Gross uncracked sections and full composite action are assumed. Effective deck width equals tributary width; structural deck thickness is 7.5 in. A uniform 2 in haunch is an explicit provisional assumption. The original profile is straightened for analysis; display positions use the original GLB.

All outputs are **increments from the selected load only**. Initial prestress, prestress losses, staged deck/diaphragm/barrier loads, creep, shrinkage, cracking and reinforcement stiffness are excluded. Therefore no total concrete stress, cracking/safety verdict, HL-93 load rating, fatigue assessment or field validation is claimed. The known strand data is retained in the input ledger for the next stage. Unanalyzed components are gray.

## Material/source ledger

Use Beechwood PDF 32 (sheet 31), 43–45 (sheets 42–44) and official FHWA/INDOT material guidance. Preserve source page, units, confidence, derivation and exclusions. Derive concrete E using the 2017-era equation reproduced in FHWA-HIF-22-025: E(ksi) = 120000 K1 wc(kcf)^2 fc(ksi)^0.33. Assume wc = 0.150 kcf and K1 = 1.0; these are not measured properties. Use 150 pcf for gravity, and INDOT's Poisson ratio 0.2 (recorded but unused by this beam formulation). Do not substitute compressive strength for E.

## Implementation plan

1. Freeze English input JSON with PDF hashes, numeric geometry, material evidence and scope notes; compute section properties from a documented polygon.
2. Add an optional isolated OpenSees runtime and deterministic CLI worker. Record solver/runtime versions, input and source hashes, units and geometry-to-component mappings.
3. Check section integrals, simple/fixed/continuous beam benchmarks, reaction and moment equilibrium, mesh refinement and support sensitivity before accepting a run.
4. Add SQLite analysis input/run/result records and a bounded localhost POST endpoint. Each run is a separate subprocess; the UI reports queued/running/completed/failed. A server restart marks interrupted runs failed.
5. Add a compact FEM tab to the existing fixed inspector. Show cases, assumptions, source links, numerical checks and downloads; use the existing 3D view for girder stress/deflection colors and an explicitly scaled deformation.
6. Run backend, physics and browser checks. Keep the four-bridge workspace and five map-only records unchanged. Publish English source once verified.

## Acceptance

Actual persisted runs must be reproducible from their frozen inputs. Force and moment equilibrium relative errors must be below 1e-7; 24 vs 48 elements per span must change sampled peak moment and deflection by less than 1%. Closed-form benchmarks must agree within 1e-6 relative error at matched positions. Colors must map to computed girder IDs and reset on bridge/model changes. A numerical verification pass is separate from field validation.

## Authorized whole-bridge extension

The next implementation replaces independent-line distribution with a connected ShellMITC4 deck and debris walls, 3D beams for girders/substructure and explicit bearing springs. The user requested correction of confirmed model errors; PDF 38 establishes 22 ft column center spacing. Update the actual GLB, metadata, DB and preview as well as the analytical model. Use the drawing-permitted alternative continuous deck pour for a two-stiffness staged scenario and assume retained prestress fractions explicitly. Preserve old cases and their history. Accept global equilibrium/benchmarks separately from family-level peak convergence; mesh-sensitive local peaks must remain visibly flagged. Whole-bridge display should include family filters, undeformed analytical mesh, stage-aware deformation and exports.

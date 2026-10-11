# Beechwood FEM pilot

Open the Beechwood model and click **FEM** in the view toolbar or details panel. Select a load case and end-rotation assumption, then **Run analysis**. Completed runs can be reopened from **Saved runs**. No AI API key or paid API call is needed.

This first implementation calculates **incremental nominal girder response**, using four independent longitudinal beam lines and the twelve girder component IDs. The color scale is the maximum absolute top/bottom girder fiber stress at each longitudinal section, or absolute vertical deflection. It is not a local 3D solid stress field, total prestressed-concrete stress or structural safety rating. Gray components have not been analyzed.

## Install the optional solver

The asset viewer still runs on Python 3.9+. Use Python **3.12** for the separate solver environment. Windows PowerShell, from the repository:

```powershell
py -3.12 -m venv .venv-fem
.\.venv-fem\Scripts\python.exe -m pip install -r requirements-fem.txt
python server.py
```

macOS/Linux:

```sh
python3.12 -m venv .venv-fem
.venv-fem/bin/python -m pip install -r requirements-fem.txt
python server.py
```

The server automatically discovers `.venv-fem`. Alternatively set `BRIDGE_FEM_PYTHON` to the absolute path of an existing Python executable with OpenSeesPy installed. The runtime and solver versions are recorded in every result. Other operating systems may need additional OpenSees runtime libraries; consult the solver's installation documentation. OpenSees has its own redistribution/commercial licensing terms; it is not bundled in this repository.

## Materials found in the original drawings

The original plan set is bundled at `data/bridges/beechwood/drawings.pdf`. PDF page numbers are one greater than the printed sheet labels.

| Item | Value | Evidence | Applied in this pilot |
|---|---|---|---|
| Girder concrete, 28 days | 8,000 psi = 55.158 MPa | PDF 45, beam note 3 | Strength input used to estimate E |
| Girder concrete at prestressing | 7,000 psi = 48.263 MPa | PDF 45, beam note 3 | Recorded only |
| Deck / end-bent Class C concrete | 4,000 psi = 27.579 MPa | PDF 32, design stresses and general note 2 | Deck/haunch E |
| Interior bent Class A concrete | 3,500 psi = 24.132 MPa | PDF 32 | Recorded only; substructure not solved |
| Reinforcement yield strength | 60 ksi = 413.685 MPa | PDF 32 and 45 | Recorded only; no capacity analysis |
| Prestressing strand | ASTM A416, 270 ksi, 0.6 in, 0.217 in² | PDF 45 | Recorded only |
| Strand jacking force | 43,943 lbf per strand | PDF 45 | **Not** effective prestress after losses; excluded |
| Strand count per girder | A/C: 26; B: 30 | PDF 43–44, section rows | Recorded only |

The material and input ledger is `fem/beechwood.json`. Every numeric input has an evidence record. Source files and solver code are hashed for each run.

## Reference estimates and explicit assumptions

Concrete E is derived as **E(ksi) = 120000 × K1 × wc(kcf)² × fc(ksi)^0.33**. This gives about **36.975 GPa** for the girder and **29.415 GPa** for the deck. Unit weight **150 pcf (23.563 kN/m³)** and aggregate factor **K1 = 1.0** are assumed reference values, not site measurements. The equation and an example using 0.150 kcf are in [FHWA-HIF-22-025, PDF page 79 / printed page 65](https://www.fhwa.dot.gov/bridge/loadrating/pubs/hif22025.pdf#page=79).

Poisson ratio **0.2** is recorded from [INDOT Chapter 406, section 406-4.02(02), PDF page 8](https://www.in.gov/dot/div/contracts/design/Part%204/Chapter%20406%20-%20Prestressed-Concrete%20Structure.pdf#page=8). It is not used by this Euler–Bernoulli element. Steel E values **29,000 ksi** for reinforcement and **28,500 ksi** for strand are recorded from FHWA-HIF-22-025, PDF page 127 / printed page 113; neither is applied in the current gross-concrete sections.

The dimensioned BT 36x49 polygon is integrated to obtain area, centroid and inertia. The typical midspan section is used throughout; local beam-end thickening, holes and steel are excluded. The deck has an 8 in total thickness but only **7.5 in structural thickness** is credited, as specified on PDF page 32. Composite effective width equals tributary width; a **constant 2 in haunch** is provisional. Actual haunch variation has not been verified for analysis. Nominal girder/deck quantities are included in JSON for traceability; they are not procurement takeoffs.

## Cases and boundaries

| Case | Included load | Section and support idealization |
|---|---|---|
| Full-width test | 1 kPa × 33 ft width × 250 ft between end-bent centers | Composite continuous beam, 80/90/80 ft spans; internal support at bent centerlines |
| Future wearing surface | Drawing's 35 psf × assumed 30 ft roadway × 250 ft | Same composite model; external girder load strips are narrower |
| Bare girder self-weight | Girder polygon area × 150 pcf; physical beam lengths including end overhangs | Individual simple bearings at 0/79, 81/169, 171/250 ft; girder extents −0.5/79.75, 80.25/169.75, 170.25/250.5 ft |

All load multipliers are **research scenario multipliers**, not prescribed code load factors. Composite cases enforce continuous rotation through interior supports. The two end-rotation choices compare free and fully restrained ends; neither is claimed to reproduce the integral-abutment stiffness. Vertical bearing displacement is zero. The opposite end-rotation case is also solved and its peak response shown as a sensitivity comparison. It is not a guaranteed upper/lower bound.

The FE model uses straight horizontal reference lines. Original grade/camber/crossfall remain in the visual mesh but do not alter the calculation. Deformation is mapped to the GLB's vertical Y axis, with the chosen display magnification stated in the legend. Stress and deflection remain in their physical units regardless of magnification.

## What the results do not establish

- Effective prestress, prestress losses and steel stiffness have not been included. Self-weight-only tensile increments must not be interpreted as actual concrete tension or cracking.
- There is no staged deck/diaphragm/barrier construction load history, creep, shrinkage, cracking or nonlinear contact.
- Transverse distribution is by tributary width. There is no grillage, shell mesh, truck positioning, HL-93 envelope, dynamic impact or load rating.
- Substructure, bearings, foundations, railings and local anchorage details are not analyzed. Solid stress concentrations and fatigue require a later validated local model.
- Numerical checks establish that these idealized equations are solved consistently. They do not validate the bridge assumptions or its field condition.

## Verification and reproducibility

Each accepted run includes 10 closed-form checks: simple and fixed beam deflection/moment/reaction, two-span support moment/reaction, and polygon area/inertia. Equilibrium relative errors must be below **1e−7**. A second mesh doubles the target density (24 to 48 elements over the longest interval); sampled peak moment/stress and deflection must change by less than **1%**. Very short overhangs are not excessively subdivided. Uniform-load moment recovery includes the shear-zero station; displacement recovery includes the distributed-load particular solution.

Run the checks:

```powershell
.\.venv-fem\Scripts\python.exe test_fem.py
python test_fem_service.py
python test_manager.py
npm run build
```

`test_fem_service.py` invokes the optional solver as a separate process and checks source hashes, persistence, CSV/JSON export, source reimports and result-tampering rejection. It skips the real-solver test if no optional runtime is installed. The CI FEM job installs and runs the real solver on Linux.

SQLite tables `analysis_inputs`, `analysis_runs` and `analysis_member_results` retain the input snapshot, status, software metadata and per-member peaks. Full samples, reactions and verification are in `data/analysis_runs/<run-id>/result.json`; download **Run JSON** and **Samples CSV** from the panel. Runtime files are ignored by Git. The database export contains run summaries and input snapshots; download the JSON separately for full sample data. Historical analysis rows survive catalog reimports.

A run executes in a separate subprocess with a 180-second limit and one active job at a time. The request is restricted to registered cases, end restraint and a 0.1–5 load multiplier. It cannot execute user-provided code. Interrupted runs are marked failed after a server restart. Changed source/model/code hashes mark historical results as archived and prevent automatic coloring of the current model.

To reproduce a downloaded run, save its `snapshot` object as `input.json` and run with the matching solver source version:

```powershell
.\.venv-fem\Scripts\python.exe -m fem.solver --input input.json --output result.json
```

The next structural step is a reviewed staged prestress/dead-load model, reinforcement-aware stiffness and support flexibility, followed by transverse grillage or shells. A local solid submodel comes after the global response is credible.

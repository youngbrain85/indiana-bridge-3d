# Beechwood whole-bridge FEM

Open Beechwood, click **FEM**, select a **Whole bridge** case and click **Run analysis**. Results are calculated locally with OpenSees; no AI API key or paid model call is used. Previously saved girder-only cases remain available.

## What is connected

The global model calculates 72 mapped components across 11 families: deck, girders, steel crossbeams, concrete diaphragms, bearings, caps, columns, debris walls, piles, drilled shafts and rock sockets. The deck and debris walls use ShellMITC4 plate/membrane elements. Other structural members use 3D elastic beam-column elements. Bearings use explicit translational springs; rigid offsets transfer forces between eccentric reference axes. The GLB is a visualization, not the finite-element mesh.

The original 17.5 ft column center spacing was an error. **The actual GLB and DB have been corrected to 22 ft**, including attached foundation members and rebuilt walls. See [the correction record](/model-corrections). The analysis independently uses the dimensioned 22 ft spacing.

## Cases and stages

| Case | Loads and stiffness | Interpretation |
|---|---|---|
| Whole bridge: full deck | 1 kPa across the 33 ft × 252 ft deck, after composite action | Load increment only |
| Whole bridge: left half | 1 kPa on the negative-transverse half of the deck | Demonstrates transverse distribution and torsion; increment only |
| Whole bridge: staged | Retained prestress, girder/substructure gravity, wet deck/forms/haunch; then hardened deck with barriers, wearing and idealized diaphragm gravity | A stated elastic construction scenario; not measured total service stress |

For the staged case, bare precast girders take their own weight, assumed retained prestress, wet 8 in deck, 2 in assumed haunch and 15 psf forms before composite action. A separate cured model receives barrier weight from the PDF 49 schedule and 35 psf future wearing over the 30 ft roadway. RC diaphragm weight is applied in the cured idealization. This uses the **alternative continuous pour permitted on PDF 48**. It does not reproduce the default A/B/C timed pour sequence. End diaphragm, wingwall, approach slab, soil, utility and small hardware weights are excluded.

Stress components are summed before computing maxima; absolute peaks are never added. Existing-member displacements accumulate pre/post increments. Newly cast deck and diaphragms show only post-cure displacement. Whole-model exaggerated deformation is disabled for the staged case to avoid implying a compatible cumulative displacement field for stress-free newly cast concrete. Each stage's actual FE mesh can be inspected separately.

The three older longitudinal-beam cases are documented in [the pilot reference](fem-pilot.md).

## Drawing values and estimates

| Input | Value / treatment | Source or status |
|---|---|---|
| Girder concrete | 8,000 psi at 28 days; 7,000 psi at transfer recorded | PDF 45 |
| Deck / end-bent concrete | 4,000 psi | PDF 32 |
| Interior bent concrete | 3,500 psi | PDF 32; also provisionally assigned to shafts |
| Concrete elastic modulus | Girder 36.975 GPa; deck 29.415 GPa | FHWA equation; assumes 150 pcf and K1 = 1 |
| Concrete Poisson ratio | 0.2 | INDOT Chapter 406 reference |
| Steel modulus | 29,000 ksi for piles and crossbeams | FHWA reference estimate |
| Strand force / count | 43,943 lbf per strand; 26 in A/C, 30 in B | PDF 43–45 |
| Strand path | Three draped strands from 31 in to 4 in above girder bottom; remaining strands straight | PDF 43–44 |
| Effective prestress | 70%, 80% or 90% of jacking force; default 80% | **Assumed retained force; losses are not calculated** |
| Bearings | TH1 12 × 36 in, total rubber 3.0625 in | PDF 45 |
| Bearing stiffness | G = 0.9 MPa, effective compression E = 450 MPa | Assumed, not supplier test results |
| Interior foundations | 54 in columns/sockets; 60 in outside casing; drawing rock/tip levels | PDF 38 |
| End foundations | Six HP12×84 per bent, drawing tip levels | PDF 32–34 |
| Structural deck | 7.5 in stiffness; 8 in gravity thickness | PDF 32 |

All numeric ledger values have evidence records in `fem/beechwood.json` and `fem/global.json`. The shell accounts for composite deck stiffness through offsets to the bare girder section; no transformed deck width is added a second time. Haunch rigidity is represented through the connection; its own section stiffness is omitted. Girder torsion constant, rectangular channel/HP section approximations and connection stiffness remain explicit research idealizations. All concrete remains gross and uncracked; reinforcement stiffness, creep, shrinkage, prestress transfer length and age-dependent losses are excluded.

Concrete E uses E(ksi) = 120000 K1 wc(kcf)^2 fc(ksi)^0.33, reproduced in [FHWA-HIF-22-025, PDF 79](https://www.fhwa.dot.gov/bridge/loadrating/pubs/hif22025.pdf#page=79). See also [INDOT Chapter 406](https://www.in.gov/dot/div/contracts/design/Part%204/Chapter%20406%20-%20Prestressed-Concrete%20Structure.pdf) and [FHWA refined-analysis guidance](https://www.fhwa.dot.gov/bridge/pubs/hif18046.pdf).

## Foundations and connections

Select fixed estimated tips or a rigid rock-line restraint. Both are idealized sensitivity cases. There are no calibrated soil springs, p-y curves, rock bond/slip or differential settlement. Neither scenario is a guaranteed bound. Column heights, shaft lengths and socket lengths follow the drawings; superstructure grade/crossfall/camber and cap steps are straightened. End connections use stiff finite springs after cure, nearly sliding longitudinal bearings before cure. Interior bearings release rotation. Shear-key contact, connection slip, uplift and nonlinear cracking are not solved.

The worker automatically compares the alternative foundation scenario. Staged cases also compare the other retained-prestress fractions. These comparisons report sensitivity to assumptions; they do not identify the true condition.

## Reading colors and peaks

| Family | Reported stress |
|---|---|
| Beam/column/pile | Axial + biaxial nominal fiber normal stress |
| Deck / debris wall | Principal stress on both shell surfaces, recovered from integration-point membrane and bending resultants |
| Bearings | Signed mean normal pressure; local contact stress is not calculated |

Use **Component family** to avoid comparing unrelated material/failure measures. Gray parts are excluded from the selected calculation/filter. Larger values locate candidates for further examination; colors are not a safety rating. Shell stress is not averaged across elements or materials. The display maps shell samples to the drawing model without claiming a solid stress field.

**Wall connection peaks are currently mesh-sensitive.** The UI explicitly lists unconverged family/quantity pairs. Such peaks require local mesh study and improved connection geometry; do not report them as converged stress concentrations. Local end-zone bursting, anchorage, weld/bolt, bearing-edge and concrete-contact solid submodels are not implemented.

## Numerical checks and reproducibility

Every accepted global run passes 21 analytical checks: the original beam/section checks plus 3D axial/biaxial bending, rigid-offset moment transfer, shell membrane patch, simply supported square plate and eccentric prestress checks. All six force/moment balances are checked; normalized error must be below 1e-6. Every node must connect to a foundation in regression tests. Two mesh densities are compared for each family's peak stress and displacement. Global maximum displacement must change by less than 5%; individual family peaks above 5% remain visibly flagged. Numerical checks are separate from field validation.

Runs freeze drawing/model/manifest hashes, both source-code hashes, parameters, solver version, samples, integration-point resultants, element connectivity, support reactions, stages and sensitivity results. Historical DB records survive imports. Changed geometry or code archives earlier results instead of recoloring the current model. JSON and CSV exports are available in the FEM tab.

## Installation and tests

The normal viewer runs on Python 3.9+. Install the optional solver using Python 3.12:

```powershell
py -3.12 -m venv .venv-fem
.\.venv-fem\Scripts\python.exe -m pip install -r requirements-fem.txt
python server.py
```

On macOS/Linux use `python3.12 -m venv .venv-fem` and `.venv-fem/bin/python`. Set `BRIDGE_FEM_PYTHON` only if using a different solver interpreter. OpenSees licensing is separate; see `THIRD_PARTY_NOTICES.md`.

```powershell
.\.venv-fem\Scripts\python.exe test_fem.py
.\.venv-fem\Scripts\python.exe test_global_fem.py
python test_fem_service.py
python test_manager.py
node test_global_browser.cjs
```

A failed equilibrium, benchmark or global displacement check rejects a run. A local mesh warning preserves the result for investigation while clearly identifying the unresolved quantity. Results do not establish capacity, code compliance, HL-93 rating or real-world structural safety.

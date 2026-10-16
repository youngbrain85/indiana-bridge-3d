# Minnich Road assumed-input FEM demonstration

Open `http://127.0.0.1:8766/?fem=1#bridge/minnich-road` and select **Run demonstration**. Results come from a real local OpenSees solve, not a fabricated heat map. The assumed structural model is deliberately hypothetical: it demonstrates the analysis workflow without claiming to reproduce the actual bridge.

## Inputs and scope

| Item | Treatment |
|---|---|
| Geometry scaffold | Four spans, 126.4793 m deck length, 19.2024 m width, eight girder lines, 56.2986° skew, based on the existing proposed-2026 visual reconstruction |
| Deck | 203.2 mm gross uncracked ShellMITC4, continuous across the former center joint; grade and crossfall flattened |
| Steel | Elastic beam-column members; approximate varying depths, uniform 457.2 mm flanges, 25.4 mm flange thickness and 12.7 mm web |
| Composite connection | Assumed full action, rigid offsets from shell midsurface to girder centroids |
| Cross frames | Two assumed 100 × 12 mm elastic rectangular diagonals per displayed X frame; skew-aligned and rigidly attached; not verified fabrication details |
| Substructure | Ten assumed caps, eighteen assumed columns; positions/heights from the visual scaffold. Original details remain unavailable |
| Bearings | Forty bilateral springs, default 800 MN/m vertical, 2 MN/m horizontal and 1 kNm/rad rotational stiffness; nominal 12 × 16 in pressure area for every bearing |
| Foundations | Fixed support bases or six-direction springs, not physical foundation members. Default elastic translational stiffness 100/100/1000 MN/m, rotational stiffness 200 MNm/rad |
| Load | Full-deck or negative-transverse half-deck pressure increment; default 1 kPa. No self-weight, traffic rating or construction stages |

The UI exposes pressure, load multiplier, steel E (default 200 GPa), concrete E (30 GPa), bearing vertical stiffness, column diameter (0.9 m), and support scenario. Values are bounded and validated by the API. They are demonstration assumptions, not measured properties or certified design values. Editing them changes the FE model; the GLB dimensions remain unchanged.

There are **197 mapped components**: one deck, 32 girder segments, 96 cross-frame groups, 40 bearings, ten caps and eighteen columns. Other parts are gray and are neither separate FE members nor dead loads. Spring foundations have no physical foundation stress output. The proposed design is not evidence of completed construction.

## Results and interpretation

The same FEM panel supports saved runs, family filtering, nominal stress and vertical-displacement colors, magnified deformation, actual FE mesh viewing, and JSON/CSV download. An **Assumed-input demonstration** notice stays visible in the panel and color legend. Changed controls are explicitly distinguished from the displayed run. Each result includes its actual input settings, assumptions and source/code hashes.

Beam output is axial plus biaxial nominal fiber normal stress. Deck output is principal surface stress from integration-point resultants. Bearing output is signed mean normal pressure, not contact-edge stress. Bilateral springs can carry tension; uplift release and friction are not implemented. These different measures should be compared within a selected family. Neither values nor colors imply a capacity or safety rating.

FE samples are projected to each matching GLB part using nearest native-coordinate samples. Flattened grade, skew-aligned analytical cross frames, and changed column diameter can differ from the visual geometry. The actual FE mesh is independently inspectable. No local solid stress, weld, bolt, fatigue, yielding, concrete cracking or soil-interaction analysis is claimed.

## Verification and reproducibility

Each solve checks 21 existing analytical benchmarks, connectivity of every node to a support, all six resultant force/moment balances, exact pressure resultant, and two mesh densities. The global maximum nodal vertical displacement must change by less than 5%. Family stress/displacement changes above 5% remain visible as **unconverged peaks**. An alternative support-base scenario is also solved. Numerical acceptance establishes internal calculation consistency, not physical validity.

Run:

```powershell
.\.venv-fem\Scripts\python.exe -m unittest test_minnich_demo -q
python -m unittest test_fem_service -q
node test_minnich_browser.cjs
```

The ledger is `fem/minnich.json`; the dedicated construction and solve code is `fem/minnich_demo.py`. It reuses the frame/shell recovery and benchmarks in `fem/global_model.py`. The service freezes all related source hashes and refuses changed/cross-bridge mappings. Existing analysis records are retained; results from changed solver code are archived until recomputed.

Element definitions: [elasticBeamColumn](https://openseespydoc.readthedocs.io/en/latest/src/elasticBeamColumn.html), [ShellMITC4](https://openseespydoc.readthedocs.io/en/latest/src/ShellMITC4.html), [zeroLength](https://openseespydoc.readthedocs.io/en/latest/src/ZeroLength.html). These references define the numerical elements, not Minnich Road's unknown inputs.

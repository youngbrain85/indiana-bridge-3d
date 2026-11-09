# Verification checklist

Run `bash tools/run_checks.sh` first (dimension checks + comparison sheets), then go through the visual items below with
the sheets in `bridges/<folder>/verification/`. Photo numbers refer to `photos/index.json`.

## 07620 — SR 28 over Little Wea Creek (3-span RC slab on pile bents, 20° skew, built 1989)

| # | Item | Source | Expect in model |
|---|---|---|---|
| 1 | Spans 22.25 + 27 + 22.25 = 71.5 ft, deck 39.0 o/o, 36.0 roadway | report span table, items 49/51/52 | `verify_model.py` PASS |
| 2 | Skew 20° | item 34 | bents and abutments run at 20° to the deck edge (aerial render) |
| 3 | Pile bents: 9 round black-coated steel-encased piles ~14 in, cap integral with slab | elements 227/225, photos 21-22, 27-28 | 9 piles per bent, black, no separate cap above the soffit |
| 4 | Slab edge = deep coping + vertical parapet, one flat face | photos 1-2, 6-7, 24 | elevation render shows a deep flat fascia with a small step |
| 5 | Riprap under the bridge, dry grass beyond, piles standing in shallow water | photos 1, 14, 22, 34 | riprap slopes from the abutments to the water, water 12.95 ft below deck |
| 6 | Two-lane road, double yellow, W-beam guardrail, concrete approach slabs | photos 3-5, 13 | approach render |
| 7 | 4 in PVC deck drains through the slab near the copings | photo 31, model_notes | small spouts under the slab |
| 8 | Winter: bare trees, bare/dry fields | photos 3-4, 25-26 | bare trees, dry grass tint |

## 41750 — I-70 EB over Bayliss State Ditch (3-span RC slab on 2-column frame bents, 15° skew, built 1966)

| # | Item | Source | Expect in model |
|---|---|---|---|
| 1 | Spans 25 + 32 + 25 = 82 ft, deck 43.0 o/o, 39.5 roadway | span table, items 49/51/52 | PASS |
| 2 | Skew 15° | item 34 | |
| 3 | Piers: two ~3 ft round columns + rectangular cap (reads as a 46.5 ft wall from the side) | photos 26-28, element list "pier wall 46.5" | `Pier2_col±`, `Pier2_cap` present, cap length ≈ 46 ft |
| 4 | Abutments: tall concrete walls with wingwalls parallel to the road | photos 19-20 | ~9 ft of exposed wall |
| 5 | Deep stepped coping with NJ safety-shape parapet on top | photos 16-18 | |
| 6 | Interstate markings: white skip, white right edge, yellow left edge; WB twin 30 ft north | photos 1-2, 12 | approach / aerial renders |
| 7 | Grass channel in a shallow swale, cornfields either side, water 15 ft below deck | photos 29-31 | |
| 8 | Summer (Sep 2021): green trees, blue sky | all photos | |

## 19027 — WB Sagamore Pkwy (US 52) over 9th St, CSX, ramp (steel multi-beam viaduct, 1971)

| # | Item | Source | Expect in model |
|---|---|---|---|
| 1 | 6 spans: 32 (6 concrete beams) + 92 + 101 + 101 + 101 + 92 (8 W36 lines); 525.2 ft total | span table, items 43/45/49 | PASS; `Girder_0..7` span stations 32–519, `ConcreteBeams` over span A |
| 2 | Deck 43.0 o/o, 39.8 roadway, NJ parapets, chain-link fence over the CSX span (C) | items 51/52, railing element, photo 30 | `Fabric_*` between stations 124 and 225 |
| 3 | Bent 1: abutment on concrete slope wall | photos 16-17, 20 | `SlopeWall0` under span A |
| 4 | Piers 2-3: solid pier walls with battered ends flanking 9th St (4 lanes) | photos 24-25, 29 | `Pier2_wall`, `Pier3_wall`; street with sidewalks between them |
| 5 | Piers 4-6: two 3.5 ft round columns + tapered hammerhead cap 43.5 ft | photos 34, 36, 38 | `Pier4_col±`, `Pier4_cap` tapered |
| 6 | Rocker bearings, X cross-frames, green paint with rust streaks | photos 21-26, 30-37 | |
| 7 | 14.17 ft vertical clearance over 9th St; CSX track under span C; ramp under span F | items 54/10, photos 30, 40 | `Road_9thSt` at 78 ft, `Ballast`/`Rail±` at 176 ft, `Road_ramp` at 473 ft |
| 8 | Parallel EB structure ~67 ft south (simplified twin) | photos 1-2, 27 | `TwinBridge` instance |

## Known simplifications (do not report as defects)

- Terrain, creek alignment, tree positions and the 9th St / ramp geometry are plausible reconstructions, not surveyed.
- Twin structures are instanced copies of the modelled bridge.
- Approach slabs for 41750 are both modelled at 20.5 ft (report: 20.5 and 31.08).
- Deterioration (cracks, spalls, patches) is suggested by textures only; it is not modelled per element.

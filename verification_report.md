# Model verification report

## SR 28 over Little Wea Creek (07620_sr28_little_wea) — bridges/07620_sr28_little_wea/model/bridge_07620.glb

| Check | Expected | Model | Tol. | Status | Note |
|---|---|---|---|---|---|
| nodes in model |  | 2675 |  | **INFO** |  |
| deck width out-to-out (slab Y extent) | 39.00 | 39.00 | 0.25 | **PASS** | NBI item 52 |
| length between abutment lines (slab X extent minus skew offset) | 71.50 | 71.50 | 0.50 | **PASS** | sum of spans; NBI item 49 structure length = 71.5 (includes backwalls) |
| skew angle derived from slab footprint | 20.00 | 20.00 | 1.00 | **PASS** | NBI item 34 |
| deck top at Z = 0 | 0.00 | 0.00 | 0.10 | **PASS** |  |
| roadway width curb-to-curb (DeckSurface Y extent) | 36.00 | 36.00 | 0.25 | **PASS** | NBI item 51 |
| parapet L height | 2.75 | 2.75 | 0.15 | **PASS** | reinforced concrete parapet on thick slab coping |
| parapet L runs full length | 71.50 | 71.50 | 1.00 | **PASS** | between abutment lines |
| parapet R height | 2.75 | 2.75 | 0.15 | **PASS** | reinforced concrete parapet on thick slab coping |
| parapet R runs full length | 71.50 | 71.50 | 1.00 | **PASS** | between abutment lines |
| number of substructure units | 4 | 4 | 0 | **PASS** |  |
| Bent 1 stem centre (4.5 ft stem behind the support line) | -2.11 | -2.11 | 0.50 | **PASS** |  |
| Bent 1 length | 39.00 | 40.00 | 2.50 | **PASS** | stem is W+1 ft long in the model (4.5 ft thick box rotated by the skew) |
| Bent 1 wingwalls | 2 | 2 | 0 | **PASS** |  |
| Pier 2 cap/wall centred on station | 22.25 | 22.25 | 0.75 | **PASS** |  |
| Pier 2 piles | 9 | 9 | 0 | **PASS** |  |
| Pier 3 cap/wall centred on station | 49.25 | 49.25 | 0.75 | **PASS** |  |
| Pier 3 piles | 9 | 9 | 0 | **PASS** |  |
| Bent 4 stem centre (4.5 ft stem behind the support line) | 73.61 | 73.61 | 0.50 | **PASS** |  |
| Bent 4 length | 39.00 | 40.00 | 2.50 | **PASS** | stem is W+1 ft long in the model (4.5 ft thick box rotated by the skew) |
| Bent 4 wingwalls | 2 | 2 | 0 | **PASS** |  |
| water surface below deck | 12.95 | 12.95 | 0.20 | **PASS** | NBI channel profile |
| approach slab 0 length | 20.50 | 20.50 | 1.00 | **PASS** |  |
| approach slab 1 length | 20.50 | 20.50 | 1.00 | **PASS** |  |
| structure bounding box X (ft) |  | -15.2 .. 86.7 |  | **INFO** |  |
| structure bounding box Z (ft) |  | -19.0 .. 2.8 |  | **INFO** |  |

PASS 23 · FAIL 0 · WARN 0 · INFO 3

## WB Sagamore Parkway (US 52) over 9th Street, CSX Railroad and ramp (19027_sagamore_pkwy) — bridges/19027_sagamore_pkwy/model/bridge_19027.glb

| Check | Expected | Model | Tol. | Status | Note |
|---|---|---|---|---|---|
| nodes in model |  | 1330 |  | **INFO** |  |
| deck width out-to-out (slab Y extent) | 43.00 | 43.00 | 0.25 | **PASS** | NBI item 52 |
| length between abutment lines (slab X extent minus skew offset) | 519.00 | 519.00 | 0.50 | **PASS** | sum of spans; NBI item 49 structure length = 525.2 (includes backwalls) |
| deck top at Z = 0 | 0.00 | 0.00 | 0.10 | **PASS** |  |
| roadway width curb-to-curb (DeckSurface Y extent) | 39.80 | 39.80 | 0.25 | **PASS** | NBI item 51 |
| parapet L height | 2.67 | 2.67 | 0.15 | **PASS** | reinforced concrete safety-shape parapet |
| parapet L runs full length | 519.00 | 519.00 | 1.00 | **PASS** | between abutment lines |
| parapet R height | 2.67 | 2.67 | 0.15 | **PASS** | reinforced concrete safety-shape parapet |
| parapet R runs full length | 519.00 | 519.00 | 1.00 | **PASS** | between abutment lines |
| number of substructure units | 7 | 7 | 0 | **PASS** |  |
| Bent 1 stem centre (4.5 ft stem behind the support line) | -2.25 | -2.25 | 0.50 | **PASS** |  |
| Bent 1 length | 45.17 | 44.00 | 2.50 | **PASS** | stem is W+1 ft long in the model (4.5 ft thick box rotated by the skew) |
| Bent 1 wingwalls | 2 | 2 | 0 | **PASS** |  |
| Pier 2 cap/wall centred on station | 32.00 | 32.00 | 0.75 | **PASS** |  |
| Pier 2 length | 44.00 | 44.50 | 2.00 | **PASS** | concrete pier wall, battered ends |
| Pier 2 solid wall present | True | True | 0 | **PASS** |  |
| Pier 3 cap/wall centred on station | 124.00 | 124.00 | 0.75 | **PASS** |  |
| Pier 3 length | 43.50 | 44.00 | 2.00 | **PASS** | concrete pier wall, battered ends |
| Pier 3 solid wall present | True | True | 0 | **PASS** |  |
| Pier 4 cap/wall centred on station | 225.00 | 225.00 | 0.75 | **PASS** |  |
| Pier 4 length | 43.50 | 43.50 | 2.00 | **PASS** | two round columns + hammerhead cap |
| Pier 4 round columns | 2 | 2 | 0 | **PASS** |  |
| Pier 5 cap/wall centred on station | 326.00 | 326.00 | 0.75 | **PASS** |  |
| Pier 5 length | 43.50 | 43.50 | 2.00 | **PASS** | two round columns + hammerhead cap |
| Pier 5 round columns | 2 | 2 | 0 | **PASS** |  |
| Pier 6 cap/wall centred on station | 427.00 | 427.00 | 0.75 | **PASS** |  |
| Pier 6 length | 43.50 | 43.50 | 2.00 | **PASS** | two round columns + hammerhead cap |
| Pier 6 round columns | 2 | 2 | 0 | **PASS** |  |
| Bent 7 stem centre (4.5 ft stem behind the support line) | 521.25 | 521.25 | 0.50 | **PASS** |  |
| Bent 7 length | 45.17 | 44.00 | 2.50 | **PASS** | stem is W+1 ft long in the model (4.5 ft thick box rotated by the skew) |
| Bent 7 wingwalls | 2 | 2 | 0 | **PASS** |  |
| steel girder lines | 8 | 8 | 0 | **PASS** |  |
| steel girders start at first steel span | 32.00 | 32.40 | 1.00 | **PASS** |  |
| steel girders end at last abutment | 519.00 | 518.60 | 1.00 | **PASS** |  |
| girder depth (W36 ~ 3.0 ft) | 3.00 | 3.00 | 0.20 | **PASS** |  |
| concrete approach-span beams present | True | True | 0 | **PASS** |  |
| concrete beams span length | 32.00 | 31.50 | 1.00 | **PASS** |  |
| chain-link fence over the railroad span (start) | 124.00 | 124.00 | 1.00 | **PASS** |  |
| chain-link fence over the railroad span (end) | 225.00 | 225.00 | 1.00 | **PASS** |  |
| vertical under-clearance to the street | 14.17 | 14.20 | 0.50 | **PASS** | NBI item 54 |
| approach slab 0 length | 20.50 | 20.50 | 1.00 | **PASS** |  |
| approach slab 1 length | 20.50 | 20.50 | 1.00 | **PASS** |  |
| structure bounding box X (ft) |  | -13.0 .. 532.0 |  | **INFO** |  |
| structure bounding box Z (ft) |  | -23.4 .. 8.7 |  | **INFO** |  |

PASS 41 · FAIL 0 · WARN 0 · INFO 3

## I-70 EB over Bayliss State Ditch (41750_i70_bayliss) — bridges/41750_i70_bayliss/model/bridge_41750.glb

| Check | Expected | Model | Tol. | Status | Note |
|---|---|---|---|---|---|
| nodes in model |  | 392 |  | **INFO** |  |
| deck width out-to-out (slab Y extent) | 43.00 | 43.00 | 0.25 | **PASS** | NBI item 52 |
| length between abutment lines (slab X extent minus skew offset) | 82.00 | 82.00 | 0.50 | **PASS** | sum of spans; NBI item 49 structure length = 82.0 (includes backwalls) |
| skew angle derived from slab footprint | 15.00 | 15.00 | 1.00 | **PASS** | NBI item 34 |
| deck top at Z = 0 | 0.00 | 0.00 | 0.10 | **PASS** |  |
| roadway width curb-to-curb (DeckSurface Y extent) | 39.50 | 39.50 | 0.25 | **PASS** | NBI item 51 |
| parapet L height | 2.75 | 2.67 | 0.15 | **PASS** | reinforced concrete parapet on deep slab coping |
| parapet L runs full length | 82.00 | 82.00 | 1.00 | **PASS** | between abutment lines |
| parapet R height | 2.75 | 2.67 | 0.15 | **PASS** | reinforced concrete parapet on deep slab coping |
| parapet R runs full length | 82.00 | 82.00 | 1.00 | **PASS** | between abutment lines |
| number of substructure units | 4 | 4 | 0 | **PASS** |  |
| Bent 1 stem centre (4.5 ft stem behind the support line) | -2.17 | -2.17 | 0.50 | **PASS** |  |
| Bent 1 length | 45.50 | 44.00 | 2.50 | **PASS** | stem is W+1 ft long in the model (4.5 ft thick box rotated by the skew) |
| Bent 1 wingwalls | 2 | 2 | 0 | **PASS** |  |
| Pier 2 cap/wall centred on station | 25.00 | 25.00 | 0.75 | **PASS** |  |
| Pier 2 length | 46.50 | 46.60 | 2.00 | **PASS** | solid concrete pier wall with rounded ends, cap integral wit |
| Pier 2 solid wall present | True | True | 0 | **PASS** |  |
| Pier 3 cap/wall centred on station | 57.00 | 57.00 | 0.75 | **PASS** |  |
| Pier 3 length | 46.50 | 46.60 | 2.00 | **PASS** | solid concrete pier wall with rounded ends, cap integral wit |
| Pier 3 solid wall present | True | True | 0 | **PASS** |  |
| Bent 4 stem centre (4.5 ft stem behind the support line) | 84.17 | 84.17 | 0.50 | **PASS** |  |
| Bent 4 length | 45.50 | 44.00 | 2.50 | **PASS** | stem is W+1 ft long in the model (4.5 ft thick box rotated by the skew) |
| Bent 4 wingwalls | 2 | 2 | 0 | **PASS** |  |
| water surface below deck | 15.00 | 15.00 | 0.20 | **PASS** | NBI channel profile |
| approach slab 0 length | 20.50 | 20.50 | 1.00 | **PASS** | per-end lengths from the report |
| approach slab 1 length | 31.08 | 31.08 | 1.00 | **PASS** | per-end lengths from the report |
| structure bounding box X (ft) |  | -14.0 .. 99.5 |  | **INFO** |  |
| structure bounding box Z (ft) |  | -16.9 .. 2.7 |  | **INFO** |  |

PASS 25 · FAIL 0 · WARN 0 · INFO 3

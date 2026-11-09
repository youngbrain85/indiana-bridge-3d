# Bridge inventory (from the INDOT / NBI inspection reports)

| Folder | NBI # | Facility / feature | Type | Spans (ft) | Deck (ft) | Skew | Built |
|---|---|---|---|---|---|---|---|
| `19027_sagamore_pkwy` | 019027 | WB Sagamore Pkwy (US 52) over 9th St, CSX RR, ramp – Lafayette | Steel continuous multi-beam (W36, 8 lines) + 1 concrete-beam approach span | 32 + 92 + 101 + 101 + 101 + 92 (525.2 total) | 43.0 o/o, 39.8 roadway | 0° | 1971 (rehab 1991, 2011, 2017) |
| `07620_sr28_little_wea` | 007620 | SR 28 over Little Wea Creek – Tippecanoe Co. | Concrete continuous slab on pile bents | 22.25 + 27 + 22.25 (71.5) | 39.0 o/o, 36.0 roadway | 20° | 1989 |
| `41750_i70_bayliss` | 041750 | I-70 EB over Bayliss State Ditch – Morgan Co. | Concrete continuous slab on 2-column frame bents | 25 + 32 + 25 (82) | 43.0 o/o, 39.5 roadway | 15° | 1966 (overlays 1980, 1995) |

Each folder holds `bridge.json` (everything the model is built from, with the NBI item numbers it came from),
the inspection photos extracted from the report (`photos/photo_NN.jpg` + `photos/index.json` with the report captions),
and the generated outputs (`renders/`, `model/`).

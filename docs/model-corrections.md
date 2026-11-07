# Drawing-confirmed Beechwood geometry corrections

## 1. Interior bent column spacing (revision 2.1)

The transverse spacing between the two columns at each interior bent was misread as **17 ft 6 in**. The dimensioned elevation on **PDF page 38 / printed sheet 37** specifies **22 ft between column centers**. The 33 ft cap is divided into 5 ft 6 in + 22 ft + 5 ft 6 in. The nearby 17 ft 6 in dimension describes the central cap step in plan, not column center spacing.

| Corrected objects | Count | Before | After | Evidence |
|---|---:|---|---|---|
| Bent 2 and 3 columns | 4 | Transverse centers ±8.75 ft | ±11 ft; 22 ft center spacing | PDF 38 elevation |
| Concrete drilled shafts | 4 | Aligned at ±8.75 ft | Moved with columns to ±11 ft | PDF 38 section/elevation |
| Rock sockets | 4 | Aligned at ±8.75 ft | Moved with columns to ±11 ft | PDF 38 section/elevation |
| Permanent steel casings | 4 | Aligned at ±8.75 ft | Moved with shaft cores to ±11 ft | PDF 38 section |
| Debris walls | 2 | Cut around the incorrectly spaced columns | Rebuilt with circular column intersections removed; 17.5 ft clear at the longitudinal centerline | PDF 38 elevation |

Each column/foundation line moves outward **2.25 ft (0.6858 m)**. The original diameters, vertical elevations and cap outline remain as dimensioned. The wall clear distance is 22 − 4.5 = 17.5 ft; it is different from center spacing.

The correction updates the actual downloadable GLB, component bounds and dimensions, embedded GLB metadata, SQLite catalog and preview. It is not a display-only translation. The component IDs remain stable, so drawing links and tree selections still identify the same objects. Old FEM runs are archived by changed asset hashes and are not automatically recolored onto the revised model.

The correction record, before/after SHA-256 and all 18 component IDs are embedded in `model_manifest.json`. `scripts/correct_beechwood_columns.py` reproduces the correction from the previous version and is idempotent on an already corrected version. Unrelated geometry buffers are preserved. Source drawing bytes are unchanged.

Verification checks actual GLB vertex bounds as well as the manifest. All four coaxial column/shaft/socket/casing assemblies are centered at ±11 ft. Both regenerated walls are watertight. The connected FEM model independently uses the same 22 ft spacing.

[Open source PDF at page 38](/assets/beechwood/drawing#page=38) · [Download corrected full GLB](/assets/beechwood/model) · [Open bridge](/#bridge/beechwood)

## 2. End-bent wing tops (revision 2.2)

**Printed sheet 35 (PDF 36)** shows each wing as one 1 ft thick wall, **12 ft** long at End Bent 1 and **11 ft** at
End Bent 4, measured from its approach-end tip to the span face of the bent, with a straight top: **El. 431.94 to
431.43** for Wings A and B and **El. 420.56 to 420.92** for Wings C and D. The model builds each wing from a 9 ft or
8 ft return plus the outer 1 ft strip of the 3 ft bent body. It had put the whole fall (or rise) of the top on the
return, so the return's bent end was 1.5 in (EB-1) or 1.2 in (EB-4) off the straight line, and it left that strip of
the bent body at deck-soffit level over its span-side 2 ft, about **8 in below** the wing top.

| Corrected objects | Count | Before | After | Evidence |
|---|---:|---|---|---|
| Wing returns `b1_wing_L/R`, `b4_wing_L/R` | 4 | Top at the bent end El. 431.43 / 420.92 | El. 431.56 / 420.82, on the straight wing profile | Sheet 35 wing elevations |
| Integral end-bent concrete (Pour B) `b1_integral`, `b4_integral` | 2 | Outer 1 ft strips at about El. 430.75 / 420.24 over their span-side 2 ft | Raised to the wing profile by a boolean union (+0.08 m³ per bent); beam pockets, ledge and seats unchanged | Sheets 32, 33 and 35 |

The end-bent bearing top plates are left as modelled and recorded as a known deviation in the manifest: they are
1 in thick at the centre where sheet 33 gives about 1⅛ in, because the bearing stack is closed between the seat
(El. 427.34 / 416.64) and the beam sole plate, both set from plan elevations, and the plates are encased in Pour B.

`scripts/correct_beechwood_wings.py` reproduces the correction from revision 2.1 and is idempotent; the record and
before/after SHA-256 are in `model_manifest.json`. The display model and the inspection sheets were rebuilt from the
corrected GLB.

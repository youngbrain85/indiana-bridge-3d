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

## 3. Drawing review of the other bridges (November 2026)

Each model below was reviewed against its drawings by an independent model review, every finding was checked against the drawings and the model before anything changed, and a second independent check reviewed the corrected model; the remaining confirmed items were corrected in a second script. Each correction is a one-time, idempotent script under `scripts/correct_<bridge>_review*.py`; the manifest of each bridge records the before/after SHA-256, the revision and the `known_deviations` left open.

A fourth round ("Fourth round: 3D review" under each bridge) followed a review of the assembled 3D models for physically implausible placement: parts that float, overlap, duplicate each other or stop short of what they connect to. Each fix is in `scripts/correct_<bridge>_3d_review.py` (revision `1.4-3d-review`), with a `review_correction_record_3d` in the manifest. The same review also covered the illustrative terrain; that is a viewer change, described in the README.

### 21st Street over I-465 (`21st-street-i465`)

#### 1. Bent 2 diaphragm, concrete railing height and approach slabs (revision 1.1)

An external review of the model found three faults, and the drawings confirm them.

**Bent 2 diaphragm.** **Printed sheet 57 (PDF 57)**, sections V-V and W-W, and the BEAM END DETAIL AT BENT #2 on
**sheet 54** put the cast-in-place diaphragm on preformed expansion joint material. It is **1 in** thick on the cap
between the bearing seats and **4 1/2 in** thick on the 6 ft seats, level with the 4 1/2 in elastomeric pads. The
model ran the diaphragm down to the cap top over its full width, so it encased 99 % of all 12 Bent 2 pads and about
95 % of the three seats.

**Concrete "C" railing, modified.** **Sheets 41, 56 and 59** all give **2'-10"** from the sidewalk to the railing top.
On sheet 59 that is an 8 in head plus a 2'-2" stem above the level construction joint. The model's railing was
**22.56 in** above the sidewalk.

**R.C. approach slabs.** The **sheet 74 (PDF 73)** plan shows a **square pavement end**, a **20'-6" minimum** short
edge and a **32'-3 1/2"** long edge. The model used a 20'-6" parallelogram with both ends skewed.

| Corrected objects | Count | Before | After | Evidence |
|---|---:|---|---|---|
| Bent 2 diaphragm `diaphragm_pier` | 1 | Underside at the cap top, El. 761.50; pads and seats encased | Underside 1 in above the cap between seats and 4 1/2 in above each seat (pad top); no overlap with pads, seats or cap | Sheet 57 V-V/W-W, sheet 54 |
| Concrete railings `parapet_1`, `parapet_-1` | 2 | Top 22.56 in above the sidewalk | 2'-10" (34 in) above the sidewalk; stem lengthened 11.44 in, 8 in head unchanged | Sheets 41, 56, 59 |
| Ornamental railing (posts, base plates, nuts, caps, pipe and tube rails, pickets, arches, rings, stars) | 1656 | On the old railing top | Raised 11.44 in with the railing top | Sheets 60-62 |
| Approach slabs `approach_west`, `approach_east` | 2 | 20'-6" parallelogram, skewed pavement end | Square pavement end; 32'-3 1/2" long edge, 20'-7 1/8" short edge | Sheet 74 plan |
| Sidewalk moment slabs `approach_walk_*` | 4 | Skewed pavement end | End on the same square pavement-end line (1 in joint) | Sheet 74 plan |

The two plan dimensions of the approach slab differ by 1 1/8 in for a 36 ft slab at 18 deg skew. The long-edge
dimension is used because it also satisfies the 20'-6" minimum. Slab and walk elevations are recomputed on the
unchanged Line M profile, crown and curb, which reproduce the original vertices. The railing recess indications are
unchanged.

`scripts/correct_21st_street_i465_review.py` reproduces the correction from the original model and is idempotent.
The record, before/after SHA-256 and all 1665 changed component IDs are in `model_manifest.json`. Unrelated geometry
buffers are preserved.

#### Second round

##### 2. Bent 2 diaphragm width (revision 1.2)

A second review found that the Bent 2 diaphragm was 4 ft wide along Line M, so only **3.80 ft (1.1595 m)** wide
normal to the bent, with each face 1.17 in inside the cap face. **Printed sheet 57 (PDF 57), section V-V**
dimensions the diaphragm faces **2'-0" either side of CL Bent No. 2**, flush with the faces of the 4'-0" cap
(**sheet 45**, plan of cap).

| Corrected object | Count | Before | After | Evidence |
|---|---:|---|---|---|
| Bent 2 diaphragm `diaphragm_pier` | 1 | 1.159529 m normal to the bent (faces n = +/-0.579764 m) | 1.219200 m (4'-0") normal to the bent, flush with the cap faces; +0.851 m3 | Sheet 57 V-V, sheet 45 |

The added strips continue the existing diaphragm section, so the beam, end-block and deck interfaces stay as they
were. They also keep the first correction's underside: 1 in joint material on the cap and 4 1/2 in on the seats,
so pads, seats and cap stay free. The sheet 54 bearing detail draws the diaphragm edge about 3 in inside the cap
face but gives no dimension for it. This conflict is recorded in `known_deviations`; the dimensioned section is
used.

`scripts/correct_21st_street_i465_review_2.py` reproduces the correction from revision 1.1 and is idempotent. The
record and the before/after SHA-256 are in `model_manifest.json`.

#### Third round: known deviations

One known deviation was left after the second round. The sheet 54 bearing detail draws the edge of the Bent 2
diaphragm 3 in inside the cap face. Section V-V on sheet 57 draws it flush. We kept the flush faces. The sheet 54 line
has no dimension, and sheet 58 gives a 3'-8" stirrup with 2 in of cover, which needs exactly the 4'-0" flush width.

Two independent checks then found faults at the end bents, and the drawings settle all of them.

- **Cap tops.** Sheet 42 gives each cap three level terraces with steps 9'-7 3/4" either side of CL Structure. The
  model had sloping tops, so pads floated or dug in by up to 14.6 mm.
- **Cap ends.** Sheet 42 draws the cap ends parallel to Line M. The model had them square.
- **Pads.** Sheet 54 gives the end-bent pads as 13/16 in thick, not 1 3/16 in. Sheet 42 places them 1'-1 1/2"
  either side of the beam centreline along the bent.
- **End diaphragms.** Sheet 58 gives them as 3'-0" wide, flush with the caps. In the model they were narrower,
  dipped into the caps, encased the pads and overlapped the approach slabs.

We rebuilt the caps and pads as drawn. The six beams now bear 3/8 in lower at the end bents, and the drop tapers to
nothing at the Bent 2 diaphragm. Their end blocks, cross frames and access doors moved with them. The haunches got
thicker, and the deck did not move. The end diaphragms were refitted: they are 3 ft wide, sit on the cap terraces,
leave the pad layer under each beam open, and carry the approach-slab ledge. Every end-bent pad now sits on level
concrete with no gap or overlap, and nothing at Bent 2 changed.

| Corrected object | Count | Before | After | Evidence |
|---|---:|---|---|---|
| End-bent caps `bent_1_cap`, `bent_3_cap` | 2 | Ridge tops, square ends | Level terraces 761.53/761.82/761.36 and 761.04/761.51/761.23, steps at 9'-7 3/4", ends parallel to Line M | Sheet 42 plan and elevation |
| End-bent pads | 12 | 1 3/16 in thick, 2'-4 3/8" apart along the bent | 13/16 in thick, 2'-3" apart along the bent | Sheet 54 pad table, sheet 42 plan |
| Span beams with end blocks, cross frames, access doors; haunch bottoms | 186 (6 beams) | Bearing at cap + 1 3/16 in | 3/8 in lower at the end bents, unchanged at Bent 2 | Sheet 54 |
| End diaphragms `diaphragm_west`, `diaphragm_east` | 2 | 2'-10 1/4" wide, 80-220 mm into the caps, pads encased | 3'-0" flush with the caps, on the terraces, pad layer open, approach ledge | Sheet 58 C-C, D-D; sheet 42 |
| Bent 2 diaphragm `diaphragm_pier` | 0 | Flush faces (open deviation) | Flush faces (decision recorded) | Sheets 45, 54, 57, 58 |

The model has no known deviations left. `scripts/correct_21st_street_i465_review_3.py` runs after the second script
and is idempotent.

#### Fourth round: 3D review

A review of the assembled 3D model found two faults in the railings, and the drawings settle both. First, both
concrete railings floated 37-45 mm above the deck along their whole length. An earlier height fix had lengthened the
stem but kept the old base. Sheet 59 shows the railing as one mass with the deck. We rebuilt the railing section as
drawn: the base sits on the deck top, and below the level construction joint the sidewalk-side face meets the
sidewalk. Above the joint that face stands 1 in behind the head. This also closes a 7 mm slit between the railing and
the sidewalk. The head and the 34 in height above the sidewalk did not change. Second, the outer ornamental-railing
posts stood on the railing ends, so half of each end base plate and two of its anchor nuts were over air. Sheet 60
gives every post station, so we set all 66 posts on those stations. The outer posts now stand 0.75-0.82 m inside the
railing ends, and every plate and nut is on concrete. The 4'-1 1/2" star bays are kept. The other 30 bays per side
follow the dimensioned totals, 110'-2 3/4" and 110'-6" over 15 bays each. Pickets, rails and graphics moved with
their posts. Two small conflicts were settled in favour of sheet 60. The south label 11+97.62 is read as 11+97.87.
Sheet 61's note about centring on the monuments does not fit the dimensioned chain. No part was added or removed. The
model has no known deviations. `scripts/correct_21st_street_i465_3d_review.py` runs after the third script and is
idempotent.

| Corrected object | Count | Before | After | Evidence |
|---|---:|---|---|---|
| Concrete railings `parapet_1`, `parapet_-1` | 2 | Base 36.7-45.2 mm above the deck; 7 mm slit at the sidewalk | On the deck top; flush with the sidewalk below the joint, 1 in behind the head above it | Sheet 59 typical section |
| Ornamental railing posts, caps, plates, nuts, rings, stars, pickets, rails, graphics | 1,656 | Outer posts on the railing ends; 30 equal 7'-6 3/8" bays | Sheet 60 stations; outer posts 0.75-0.82 m inside; bays 110'-2 3/4" / 15 and 110'-6" / 15 | Sheets 60, 61, 62 |

### US 421 over South Fork Wildcat Creek (`us421-wildcat`)

#### 1. External review corrections (revision 1.1)

An external model review was checked against the INDOT 2020 rehabilitation plans (printed sheet = PDF page). All
eight findings were confirmed. Geometry follows the drawings. For the edge beams this differs from the reviewer's
proposal: **sheet 25 Section D-D** measures the 6 in drop from the **box-beam top** (the haunch "varies"), not from
the slab.

| Corrected objects | Count | Before | After | Evidence |
|---|---:|---|---|---|
| Joint edge beams `edgebeam_A/C` | 2 | 6 in long, level 9 in block; 3.7 in gap under the soffit at the crown | 2 ft 6 in from the joint face; top on the soffit; bottom 6 in below the beam tops, parallel to the crown, between the exterior beam faces; beams and fillets excluded | Sheet 25 Section D-D and typical edge beam; sheet 22 |
| End diaphragms `diaphragm1/4` | 2 | 1 ft 9 in wide, level top (3.7 in gap) and level bottom 2.5-3.2 in above the outer cap | 2 ft 6 in over the cap; deck soffit to 1/2 in (EPS) above the cap and inner step; beam pockets kept | Sheets 10, 14, 24 |
| Pier risers and inner seats `pier2/3_key0-2`, `_innerstep` | 8 | Risers 4 ft wide; 2 in slot under the outer risers | Risers 4 ft 2 in at 0 and +/-8 ft 4 in; inner seat to +/-10 ft 5 in; elevations unchanged | Sheets 12, 13 |
| Type FC railings `FC_A/C_+-1` | 4 | 7 in top, batters 2 in back, extra 2 in toe shelf | 9 in top, 2 in / 5 in batters, 3 in toe, rear face 2 in inside the deck edge | Sheet 27 Section A-A |
| TFC transition envelopes `TFC1/4_+-1` | 4 | Old FC section, 20 ft 6 in long | Corrected FC section, same taper; end with the 16 ft 5 in RCBA extension | Sheets 27, 28 (E 706-TTFC not supplied) |
| Main-span drain extensions `drain1-3_X/Y_drop` | 6 | Outlet level with the bottom chord | Outlet 6 in below the bottom chord | Sheet 26 drain section |
| Approach slabs `approach1/4` | 2 | 31 ft wide over the full 20 ft 6 in | 28 ft for the far 4 ft 1 in; 31 ft along the 16 ft 5 in extensions | Sheet 28 |

Names (manifest and GLB labels only; part ids unchanged):

- **Y-truss panel points.** Renumbered j -> 9-j: L9-Y is at Pier 2 and L0-Y at Pier 3 (sheet 16). Y_V1 is now U8-L8.
- **End orientation.** Line "A" runs N 47 deg 15 min W (sheet 5) and Pier Cap No. 3 is at the northwest corner
  (sheet 2). The end-gusset and end-post repairs are therefore labelled southeast end (Pier 2) and northwest end
  (Pier 3), not west/east.
- **Box beams.** Numbered with Beam No. 1 on the X-truss side (sheets 10, 14, 20); box_A1 is "Span A Beam No. 4".

Not changed: the abutment inner step is modelled +/-8 ft 6 in against about +/-6 ft 8 in on the sheet 10/14
elevations. It is recorded as a known deviation; the diaphragms follow the modelled step.

`scripts/correct_us421_wildcat_review.py` reproduces the correction from the previous version and is idempotent. The
record, the changed and renamed parts and the before/after SHA-256 are in `model_manifest.json`. Unrelated GLB
buffers are preserved.

#### Second round

##### 2. Second review corrections (revision 1.2)

A second independent check confirmed all eight revision 1.1 corrections and raised two moderate interface defects,
both confirmed against the plans. **Pavement ledges** (sheets 10, 14 Sections A-A/B-B; sheet 24 Sections B-B/C-C):
the 6 in ledge now projects outside the end-bent diaphragm toward the approach, its top 1 ft 2 in below the approach
top and 1 ft 0 in deep, instead of a 4 in block inside the diaphragm; the diaphragm notch left by revision 1.1 is
filled. The 12 in approach slab (sheet 28 bill of materials) gets its drawn bridge-end seat: 1 ft 2 in deep over the
ledge and 1 ft 6 in behind it with a 2 in x 2 in taper (lengths scaled), over the 28 ft ledge length; the RCBA
extensions under the TFC transitions are unchanged (known deviation `approach-extension-seat`, E 609-TBAE-01 not
supplied). **Box beams** (sheet 21): the 1 in chamfers are at the bottom corners only, so the eight beams now have
square top corners and bear fully on their fillets; voids, camber and bottom chamfers are unchanged. Handedness was
re-checked (sheets 5, 16, 20: +Y is the southwest, X-truss, Beam No. 1 side); nothing is mirrored. Two minor items
(FC base clearance, delineator recess) were not addressed. `scripts/correct_us421_wildcat_review_2.py` reproduces the
change after the first script and is idempotent; part ids are unchanged and the record with before/after SHA-256 is
`review_correction_2_record` in `model_manifest.json`.

#### Third round: known deviations

The three deviations left after revision 1.2 were checked against the plans again. Two are resolved and one is
narrowed. **Abutment inner step** (sheets 10, 14): the plans put the step edge 2 ft 6 in beyond the inner beam
centre lines, which are 4 ft 2 in from Line "A". The step is therefore 13 ft 4 in long, not 17 ft. Both steps are
shortened, and the end diaphragms now drop 2 in onto the outer cap beyond the step. They keep 1 in of EPS against
the vertical step faces, as the EPS note "1/2 in on horizontal faces, 1 in on vertical faces" requires (the drafted
offset scales about 1/2 in; the written note governs). No bearing moves. **Ledge under
the rail transitions** (sheets 24, 28): the typical bent diaphragm draws the 6 in pavement ledge along the whole
diaphragm, and the approach plan draws it across the full 31 ft. The bill of materials pays the 1 ft 6 in
extensions as 12 in approach slab. The ledge and the 1 ft 2 in approach seat now run the full 31 ft. **TFC
transitions** (sheets 27, 28): the railing elevation draws the TFC top level with the FC top, so the envelopes keep
the full FC section over their 16 ft 5 in instead of an invented taper. The transition face is still unknown,
because standard E 706-TTFC is not supplied, so it stays a known deviation. **Rail bases** (sheet 27): the FC rails
and TFC envelopes are cast on the slab, so their level bottoms now follow the 2 % crossfall. This closes an 8 mm gap
at the rear face. Sixteen parts changed and none were added or removed. `scripts/correct_us421_wildcat_review_3.py` reproduces the change after the second script and is
idempotent. The record and the before/after SHA-256 are `review_correction_3_record` in `model_manifest.json`
(revision 1.3-deviations).

#### Fourth round: 3D review

A review of the assembled 3D model found four structural defects. All four are resolved in revision 1.4-3d-review.
- **Rail posts** (sheet 7). The 16 retained metal-rail posts stopped 57 mm short of the truss verticals. Each post now reaches the roadway face of its vertical's web. The 15 mm gap to the curb is drawn on the sheet and stays.
- **Floor-beam end angles** (sheets 17, 18). The 20 angle pairs stood 43 mm off the floor-beam web. They are now a back-to-back pair on the web, bearing on the inner end gusset at the end floor beams and on the vertical at the others. The bolts pass through both angles and the web. Where the modelled chord and diagonal ends reach into the joint, the angles are trimmed to them.
- **Drain brackets** (sheet 26). The 12 drain-pipe brackets pointed away from the piers and stopped 18 mm or 196 mm short of the concrete. They are now the drawn U-brackets, with feet on the cap or stem face and two 1/2 in anchors in concrete inserts.
- **Duplicate gussets** (sheet 16). Five lower-lateral centre plates existed twice. The five copies are removed.

Seventy-two parts changed, five were removed and none were added. `scripts/correct_us421_wildcat_3d_review.py` reproduces the change after the third script and is idempotent. The record and the before/after SHA-256 are `review_correction_record_3d` in `model_manifest.json`.

A second 3D review found one more defect. It is resolved in revision 1.5-3d-review-2.

- **Stringer framing** (sheets 16, 17, 18). The stringer end cleats did not reach the floor beams. Each stringer stopped at the floor-beam flange tips. Its cleats stood in that plane, off the stringer web, up to 27 mm below the flange. Sheet 17 (Section A-A at FB0) and sheet 18 (at FB1) draw the existing framing. They show two angles on the stringer web, bolted to the floor-beam web.
  - Each end now has two 4 x 4 x 3/8 in angles, 9 in long. 7/8 in fasteners pass through the angles, the floor-beam web and the stringer web.
  - The stringer web now runs to the floor-beam web, under the floor-beam top flange.
  - At FB0 and FB9 the two outer stringers keep only the inside angle. The floor-beam end angle leaves no room for the outside one. This is recorded as a known deviation.
- **Floor-beam stiffeners.** The 90 inferred floor-beam stiffeners sat where the drawn framing puts the stringer webs, so they are removed.

243 parts changed, 90 were removed and none were added. `scripts/correct_us421_wildcat_3d_review_2.py` reproduces the change after the fourth script and is idempotent. The record and the before/after SHA-256 are `review_correction_record_3d_2` in `model_manifest.json`.

### US 52 over Mud Creek (`us52-mud`)

##### US 52 over Mud Creek: end-bent ledge, approach corners and railings (revision 1.1)

The model was checked against the 2020 Stage 3 draft plans. On this set the printed sheet numbers equal the PDF
page numbers.

The end bents (**sheets 21, 23, 24**) carry a **9 in pavement ledge 8 in above the seat** on the approach side. The
1 ft approach slab rests on the ledge and the 1 ft 8 in deck slab on the seat, each on a 1 in bed. The model's caps
were flat, so the approach slab was 8 in clear of its bearing.

Each exterior approach module (**sheets 53-55**) is 4 ft 8 in wide for 16 ft 5 in and 3 ft 2 in wide for the last
4 ft 1 in. This cuts back each outer corner **4 ft 1 in x 1 ft 6 in**. The railing transition stops at the cutback,
and the sleeper slab is **37 ft 4 in** wide (**sheet 58**).

The FC railing (**sheet 51**) is 2 ft 9 in high. Its rear face is 2 in inside the deck edge, its top is 9 in wide,
and it has a 3 in toe. The model had a 7 in toe, no setback and an 8 in top.

The precast approach transitions stand on their edge panels (**sheet 53 section A-A**), not on the overlay.

The railing closure pours fill the full 1 ft 1 in and 1 ft over the deck closures. The only railing joint is the
**½ in neoprene expansion joint** outside the 91 ft 6 in bridge railing.

| Corrected objects | Count | Before | After | Evidence |
|---|---:|---|---|---|
| End-bent cap modules and central closures `bent_1_*`, `bent_2_*` | 6 | Flat top at seat level | 9 in ledge 8 in above the seat on the approach side (+0.278 m³ per module) | Sheets 21, 23, 24 |
| End-bent bedding `bent_1_bed`, `bent_2_bed` | 2 | 1 in bed at seat level over the full 3 ft | The 9 in strip over the ledge raised 8 in; approach slab now bears on it | Sheets 23, 24 |
| Exterior approach panels `approach_{1,2}_{1,6}` | 4 | Full 4 ft 8 in width over 20 ft 6 in | 4 ft 1 in x 1 ft 6 in corner cutback | Sheets 53-55 |
| Sleeper slabs `sleeper_1`, `sleeper_2` | 2 | 40 ft 4 in wide | 37 ft 4 in, flush with the cutbacks | Sheets 53, 58 |
| Bridge railings and closures `rail_*`, `rail_closure_*` | 14 | 7 in toe, no rear setback, 8 in top; ¼ in gaps at every closure end | Sheet 51 FC section; closures fill 13 in / 12 in with no gaps | Sheet 51 |
| Approach railing transitions `approach_rail_*` | 4 | 20 ft 6 in long, 1½ in above the slab, same section errors | 16 ft 4½ in, from the ½ in neoprene joint to the cutback, on the panel, FC section | Sheets 51, 53, 55 |
| Support names | 14 | "Abutment 1", "Abutment 2" | "End Bent 1", "End Bent 4" (names only; ids unchanged) | Sheets 21, 23 |

The absolute end-bent elevations are left as modelled and recorded as known deviations. The sheet 23 seat
(El. 929.61 at the centre) conflicts with the sheet 21 roadway profile less the slab build-up (El. 929.885). The
model keeps the deck on the profile and the cap bottom at El. 926.21. The wingwall tops share this conflict and sit
about 3 in below the approach slab bed. The neoprene joint is modelled as an open ½ in gap.

`scripts/correct_us52_mud_review.py` reproduces the correction from the previous version and is idempotent. The
record, the changed and renamed parts, and the before/after SHA-256 are in `model_manifest.json`. The display model,
catalogue and inspection data are rebuilt from the corrected GLB.

#### Second round

##### Second review: transition length, sleeper slabs, End Bent 4 labels (revision 1.2)

An independent check of revision 1.1 found three remaining errors at the approach ends. The precast TFC railing
transitions are **15 ft 8 in** long on sheets 53 and 55. They start at the ½ in neoprene joint and stop 9 in short
of the 4 ft 1 in corner cutback; revision 1.1 had run them to the cutback (16 ft 4½ in). Sheet 9's roadway station
callout (13.17 ft) conflicts with this and is recorded as a known deviation.

Section B-B on **sheet 59** places the 6 ft sleeper slab with its 2 ft lug beyond the 2½ in joint at the approach
slab end, so the slab bears on its inner 3 ft 9½ in. Both sleepers were 9½ in too far out. They now lie at
|X| = 19.04–20.87 m, regraded on the vertical curve.

Sheet 23 builds Bent No. 4 by rotating Bent No. 1 through 180°. Its module A is therefore on the north side and
module B on the south side; the labels were swapped. The barrier delineators remain schematic, because sheet 51
gives no mounting dimensions.

`scripts/correct_us52_mud_review_2.py` reproduces the change after `correct_us52_mud_review.py` and is idempotent.

#### Third round: known deviations

The five known deviations of revision 1.2 were closed; revision 1.3-deviations has none.

The end-bent elevations on **sheet 23** sit a uniform 0.27 ft below the roadway profile less the slab build-up. The
profile appears on sheets 9, 21 and 62-64, and the pier sheet 28 agrees with it. The model kept the seats on the
profile but left the bottoms at El. 926.21, so each precast module was 3.3 in deeper than drawn. **Sheet 24** writes
the module depth as 3 ft 0 in at the outer end and 3 ft 4 3/4 in at the inner end. The cap bottoms were raised
3.29 in to **El. 926.48** to match.

The four wingwalls and their closure pours moved up with the caps. They are 3 ft 8 in high, flush with the cap
bottom and with the ledge top (**sheets 24, 27**). The **1 in UHPC bed** between each wingwall and the approach slab
(**sheet 53** section A-A) is now modelled. It is 0.5-1.7 in thick, because the precast wing top is flat while the
slab follows the crossfall.

The **½ in neoprene railing joints** of **sheet 51** were open gaps; they are now filler parts with the FC section.
The six barrier delineators sat across the railing top. They now sit on the upper traffic face, as drawn in
**sheet 51** sections A-A and B-B (scaled; not dimensioned).

The TFC transitions stay **15 ft 8 in** long. Sheets 53 and 55 draw that length, and standard E 706-TTFC-01, which
sheet 51 references, writes it as the pay limits. The 13.17 ft from the sheet 9 stations is not followed.

The transitions had kept the constant FC section. They now follow the sections of standard **E 706-TTFC-01/-02**,
which **sheets 54 and 55** also draw in plan. The FC section at the joint loses its lower batter by 7 ft 2 in. The
base then narrows to 9 in at 11 ft 5 in, and a 9 in vertical wall runs on to the end. The approach overlay now runs
up to the tapering toe.

The central closures of the end bents had flat tops, and so did the UHPC closures of the piers. They now follow the
2% crossfall drawn on **sheets 23 and 28**. The 1 in bedding layers now sit on the precast tops instead of
overlapping them or leaving small gaps. The pier beds were also trimmed to the wall top. Its outer ends are
R = 1 ft 6 in (**sheet 29**), and the bed's rectangular corners had nothing under them.

Eight parts were added (four wingwall beds, four railing joints), and none were removed. The model has 172 parts.
`scripts/correct_us52_mud_review_3.py` reproduces the change after the first two scripts and is idempotent.

### SR 44 over Mud Creek (`sr44-mud`)

#### 1. External review: diaphragms, pier caps, coping and wings (revision 1.1)

An external review measured the GLB against the B-38321 plans; each finding was re-checked on the sheets (printed sheet
numbers equal PDF pages in this set) before correction.

**Regular diaphragm stations, sheet 17.** The framing-plan chain 9'-9", 20'-3", 37'-3", 15'-0", 37'-3", 20'-3", 9'-9"
runs along beam 7 from the Bent 1 bearing, and the diaphragms step 1'-10½" (7 ft × tan 15°) from bay to bay, so in
every bay the chain is measured along the higher-numbered beam. The model had measured it at the bay centre line, which
put all 36 regular diaphragms **0.286 m (3.5 ft × tan 15°) up-station**.

**Pier diaphragms, sheet 20.** Each is a C15x33.9 **5'-11"** long, joined at each end to the 7¼ in bearing stiffener
by a **PL 11/16 × 13½ × 15 in bent plate** (two 6¾ in legs) with 16 bolts, **32 per diaphragm**. The stiffener legs lie
on opposite faces of the two stiffeners, so the channel runs between the folds, about 19° to the beam normal as drawn.
The model had channels from web to web (2.196 m along the skew), straight ½ in plates and 16 bolts.

**Pier caps, sheet 16 and original 1980 sheet 11.** The 48 × 3 ft caps end in **1'-6" radius** semicircles (1'-6" +
22'-6" + 22'-6" + 1'-6"); the model had square ends.

**Coping, sheet 27.** The typical section gives **9⅛ in** at the deck edge. The model's 8 in deck plus its separate
thickened fascia part gave 9⅝ in; the fascia soffit is raised ½ in. Sheet 31 shows 9¼ in; this is recorded as a known
deviation.

**Wings, sheets 14 and 23.** A **1 in** expansion joint (Section C-C: 1 in polystyrene + 11 in concrete) separates each
wing from the end diaphragm; the model left ½ in.

| Corrected objects | Count | Before | After | Evidence |
|---|---:|---|---|---|
| Regular diaphragms `diaphragm_1..6_*` with plates and bolts | 108 | 0.286 m up-station (e.g. `diaphragm_1_6` X −21.241) | Sheet 17 stations (X −21.527, 9'-9" from the beam 7 bearing); plates refitted to the beam | Sheet 17 framing plan |
| Pier diaphragms `diaphragm_7/8_*` | 12 | 2.196 m channels along the skew | 5'-11" channels between the bent-plate folds | Sheet 20 plan and elevation |
| Pier connection plates `diaphragm_plates_7/8_*` | 12 | Two straight ½ × 7¼ in plates | Two PL 11/16 × 13½ × 15 in bent plates | Sheet 20 bent plate details |
| Pier diaphragm bolts `diaphragm_bolts_7/8_*` | 12 | 16 per diaphragm | 32 per diaphragm (8 per leg, four rows at 3 in) | Sheet 20 |
| Pier caps `cap_2`, `cap_3` | 2 | Square ends | 1'-6" radius ends | Sheet 16; 1980 sheet 11 |
| Thickened fascia `fascia_1`, `fascia_-1` | 2 | Coping 9⅝ in | 9⅛ in | Sheet 27 typical section |
| Wings `wing_1_±1`, `wing_4_±1` | 4 | ½ in joint (inner face \|Y\| 7.099 m) | 1 in joint (7.112 m); 11 in thickness unchanged | Sheets 14 and 23 |

The pier channels keep their elevation and up-station flange side, which the detail does not fix. The fold angle
follows the sheet 20 plan, which is drawn to scale, rather than the bent plate detail's 6 9/16 in / 2¼ in offsets. The
stiffener width is the elevation's 7¼ in (the plan label reads 7½ in). These choices are recorded in
`known_deviations`.

`scripts/correct_sr44_mud_review.py` reproduces the correction from the builder output and is idempotent. The record,
the 152 changed part ids and the before/after SHA-256 are in `model_manifest.json`. Unrelated geometry buffers are
preserved, and part ids are unchanged.

#### Second round

##### 2. Second check: diaphragm connections, end-bent underside and pavement ledge (revision 1.2)

An independent check of revision 1.1 raised three further discrepancies, each confirmed on the sheets.

- **Regular diaphragm connections (sheet 20, typical diaphragm detail).** The 1½ + 3 + 1¾ in chain inside the ½ × 7¼ in
  plate puts the C15x33.9 end 1 in off the beam web and the bolt columns 2½ and 5½ in off it. The model ran the channels
  from web to web, started the plates inside the web and had the columns at about 1¼ and 4¼ in. All 36 regular
  connections were rebuilt. The plates stay centred on the sheet 17 diaphragm line, and each channel moves ¼ in
  up-station so that its web bears on the plate.
- **End diaphragm underside (sheets 23 and 24).** The semi-integral diaphragms sit on ½ in of expanded polystyrene on the
  stepped existing caps. A builder profile with only two underside vertices had left a straight underside, up to 0.089 m
  inside the caps at mid-width. The underside now follows the cap steps + ½ in.
- **Pavement ledge (sheets 23, 24 and 33).** A 6 in ledge, 1'-2" below the road surface, was added along the rear face of
  each end diaphragm. The approach slabs are 2 in deeper over the first 2'-0" from the joint, with a 45° return.

The RCBA extensions under the TFC transitions keep 12 in; their end detail is on a standard drawing that is not in the
set. This is recorded in `known_deviations`. `scripts/correct_sr44_mud_review_2.py` runs after the first correction and
is idempotent. It changes 112 meshes; part ids are unchanged and unrelated buffers are kept. The before/after SHA-256 are
in `geometry_review_correction_2_record`.

#### Third round: known deviations

The known deviations of revision 1.2 were re-read on the sheets, and the round was then checked independently.

- **Overhang thickening (sheet 27).** The deck typical section draws the overhang soffit level from the deck edge to the
  outer tip of the exterior beam's top flange, 9⅛ in below the edge. The thickening now spans 22 in with a level
  soffit: 9⅛ in deep at the edge and 9.57 in at the flange tip. It stops at the end diaphragms, which are poured first.
  Sheet 31 shows 9¼ in, but it is a railing detail drawn without the crossfall or the beam, so sheet 27 governs.
- **Pier diaphragms (sheets 20 and 22).** The bent plate offsets give a 19° fold, which matches the plan geometry, so the
  fold is kept. The stiffener stays 7¼ in. Read in the framing-plan orientation, the plan puts the channel web on the
  down-station face of the bent legs. The 12 channels and their channel-leg bolts were moved to that side.
- **Square coping zones (sheets 23, 31 and 32).** Over the outer 1'-6" at each coping, the end-diaphragm faces, the
  pavement ledge and the bridge joint are square to the roadway. The deck corners, the barrier and transition ends and
  the overhang thickening now follow that square joint, so the extensions meet the bridge without overlaps or gaps.
- **RCBA extensions (sheets 31 and 33).** The extensions are 1'-2" deep for 2'-0" from the joint, with a 45° return, and
  bear on the pavement ledge.
- **Retained end-bent caps (1980 plans pages 9–10, sheet 12).** The caps now end at the wing faces. The front face
  splays 1'-0" × 1'-0" into each wing, and the rear face turns square to the roadway over the last 1'-3". The new
  diaphragm corners now sit on the cap, apart from strips under 1 in wide.
- **Bearing stiffeners (sheet 22).** The web corners are clipped 1¼ in along the flange and 2½ in along the web, at the
  top and the bottom.

One item stays open: the sloped outer corners of the pier stiffeners are drawn but not dimensioned.
`scripts/correct_sr44_mud_review_3.py` runs after the first two corrections and is idempotent. It changes 81 meshes,
adds or removes no parts (383 in all) and keeps unrelated buffers.

### SR 8 over Yellow River (`sr8-yellow`)

#### 1. End bents, piles, approaches, diaphragms, rails and beam numbering (revision 1.1)

An external model review was checked against INDOT B-23076 (1997). Printed sheets 1-20 are PDF pages 1-20, and shop
sheet M1 is PDF 25.

| Corrected objects | Count | Before | After | Evidence |
|---|---:|---|---|---|
| Integral end bents `cap_0`, `cap_5` | 2 | 0.80 m block, El. 215.953-216.753; beam ends and bearings exposed | 760 mm bent from Bottom of Bent El. 216.100 to the deck soffit, beam ends encased, 150 mm approach ledge 300 mm below the deck surface | Sheets 8-9, Elevation and Section A-A |
| End-bent wings | 4 | Bottom El. 215.953 | Bottom El. 216.100 | Sheet 9 wing elevations |
| End-bent piles `pile_stub_0_*`, `pile_stub_5_*` | 16 (2 removed) | Nine piles at 1.3 m transverse spacing (the Bent 2 layout) | Existing piles at ±7.493 and ±1.499 m, new piles at ±5.421 m along the pile line, into the bent; battered piles at ±4.496 m cut off at El. 215.800 | Sheet 8 Piling Plan, sheet 5 notes |
| Approach slabs `approach_-1`, `approach_1` | 2 | 6.250 m skew parallelogram over 11.820 m | Square pavement end at X = ±52.856 (18.467 / 6.250 m on the 10.620 m core edges); 10.920 m slab plus 450 × 5030 mm curb strips | Sheet 18 |
| End-span MC460 diaphragms | 24 (12 removed) | Three rows per span at undimensioned stations | Two per bay: on the Bent 2/5 bearing line, and 3.000 m from the end-bent bearing on each exterior beam with 1.870 + 3 @ 2.045 m between bays | Sheet 11 Framing Plan; M1 (16 M1H + 8 M1J) |
| Bent 2/5 caps and their 18 piles | 20 | Cap bottom El. 215.509 | El. 215.585 | Sheet 10 Elevation |
| Bridge rails `rail_*` | 10 | 450 mm base, 254 mm vertical toe, 10.820 m clear roadway | 400 mm base, 100 mm toe, faces through 125 × 180 and 50 × 560 mm slopes to an 840 mm top 225 mm wide; 10.920 m clear roadway | Sheet 14 Half Section, sheet 17 Section D-D |
| Beam, bearing, pedestal and diaphragm names | 167 | "Beam 1" on the south line | Beam 1 is the north exterior line; part ids unchanged | Sheet 11 Framing Plan and shim table |

The seat steps at Bents 2 and 5 (El. 216.900 / 216.940 / 216.870) are 6-62 mm above the modelled bearing bottoms.
They are recorded as a known deviation and not changed: the bearings hang from girders set at a nominal 90 mm haunch,
and reseating them needs the girder grade reconciled with the 135 mm Type B stack and the shim table (sheets 11, 13).
The approach slabs keep the modelled skew start at the deck-end joint. The squared slab and bridge-floor corners
outside the 10.620 m core, and the 300 mm pavement support (sheet 19), are not modelled.

`scripts/correct_sr8_yellow_review.py` reproduces the correction from the original model and is idempotent. The record
in `model_manifest.json` holds the before/after SHA-256 and the changed and removed parts. Part ids of kept objects
are unchanged; 14 objects with no plan counterpart were removed. The display model, catalogue, FEM ledger and
inspection sheets are rebuilt from the corrected GLB.

#### Second round

##### 2. End-bent sawtooth face, wing walls, approach-slab thickness and end-span diaphragms (revision 1.2)

A second, independent check of revision 1.1 was verified against INDOT B-23076 (sheets 8, 9, 11, 12, 18, 19 and shop
sheet M1, PDF 25). The model is not mirrored: Wing "A" is south at Bent 1 (sheet 8 north arrow, wing elevations and
tooth handedness), and Beam 1 is north (sheet 11).

| Corrected objects | Count | Before | After | Evidence |
|---|---:|---|---|---|
| Integral end bents `cap_0`, `cap_5` | 2 | Plain 760 mm approach face, ends at the 5.910 m coping | Sawtooth approach face: 11 triangular projections 755 mm deep (1150 mm sides parallel and 1000 mm sides square to the roadway, 1.000 m pitch; 557 / 313 mm from the wings), El. 216.100 to 300 mm below the deck, ends at the wing inner faces (|Y| = 5.935) | Sheet 8 Plan and Piling Plan; sheet 9 Detail D, Section E-E; Pour 1 bill 17.7 m³ |
| Wing walls `wing_0_±1`, `wing_5_±1` | 4 | Inside the coping (|Y| 5.61-5.91, overlapping the approach slab), wholly on the approach side, tops about 0.1 m low | 25 mm EPS + 300 mm wall at |Y| 5.935-6.235, straddling the bent line (Wing A 2.144 / 1.606 m, Wing B 1.454 / 2.296 m west / east), tops El. 218.056-218.072 (A) and 217.985-218.008 (B) | Sheet 8 plans; sheet 9 wing elevations |
| Approach slabs `approach_±1` | 2 | 300 mm throughout | 260 mm, thickened to 300 mm where it bears on the end-bent ledge and projections | Sheets 18-19 sections and bill (260 mm, 139.5 m²); sheet 9 A-A, E-E |
| End-span MC460 diaphragms | 24 | 1.478 / 1.173 m channels, 143 mm short of the webs, no angles, 0.100 m above the beam mid-depth | M1H 1748 / M1J 1433 mm channels with two L102 × 102 × 9.5 × 400 angles each, centred on the beam mid-depth | Shop sheet M1; sheet 12 Detail B |

The closure of the sawtooth beside Wing "B" is not dimensioned; it is scaled from both sheet 8 plans and ends on the
wing about 0.83 m along the roadway beyond the last valley. The slab's bottom chamfer at the bent and the pavement
support are not modelled. The Bent 2 / 5 seat steps remain a known deviation (`bent-2-5-seat-steps`).

`scripts/correct_sr8_yellow_review_2.py` runs after `correct_sr8_yellow_review.py` and is idempotent. The
`review_correction_2_record` in `model_manifest.json` holds the before and after SHA-256 and the 32 changed parts. No
part was added or removed, and part ids are unchanged. The display model, catalogue, FEM ledger and inspection sheets
are rebuilt from the corrected GLB.

#### Third round: known deviations

Both remaining known deviations were resolved from the drawings (revision 1.3-deviations). Sheet 15 gives the fillet
dimension of each beam, and it sets the girder top 203-240 mm below the deck surface. The sheet 10 seats, the sheet 13
bearings and the sheet 11 shim table agree with it within 0.8 mm. So the steel was raised 50-87 mm, together with the
haunches, splices, diaphragms and bearings.

The Bent 2 and 5 caps are now as drawn: stepped seats at El. 216.900, 216.940 and 216.870, with square ends, 16.96 m³
(bill 17.0 m³). The Type B bearings stand on the seats, and the 12 separate pedestals are removed. The Bent 1 and 6
bearings are now the Type A assembly of sheet 13: 126 mm plus the sheet 11 shim. Their shims are 150 × 321 mm, as the
approved shop sheet S1 revises them. The new end-span beams now run 150 mm past the end-bent bearings, with the
top-flange corner notch of the shop sheets. Their haunches and the end-bent pockets follow, so the whole shim bears on
the flange.

The deck, joints, approach slabs and end rail panels are now square to the roadway outside the 10.620 m core (sheets
14, 16 and 18). The L-shaped pavement support at the far end of each approach slab is added (sheet 19). The joint
strips now fill the gap between the deck and the approach slab.

Three items stay open as known deviations, each with the source that would settle it:
- shims that differ by up to 0.8 mm from the table (1 mm rounding);
- the retained pier seats, which are not dimensioned;
- the Type 1A joint size, which is in Bridge Std. 724-BJTS-01.

The model has 309 parts. `scripts/correct_sr8_yellow_review_3.py` reproduces the change and is idempotent. The
`review_correction_record_3` in `model_manifest.json` lists every changed, added and removed part.

#### Fourth round: 3D review

A review of the assembled 3D model found that the 54 retained diaphragms of Spans B, C and D did not touch the
girders. Each stopped 143 mm short of both webs. The third correction was not the cause: it moved the diaphragms with
the raised beams. The gap came from the first model and was fixed earlier only for the new end-span diaphragms.
Each retained diaphragm now runs from web face to web face, 1458 mm or 1763 mm (sheet 11 Framing Plan, sheet 14). Its
section, height and row station are unchanged. The bundle does not detail the existing W460x67 diaphragms or their
connections; sheet 6 points to the plans of the existing structure (Bridge File 8-75-4883 / 4883A). So the ends stand
for the connection, and this is recorded as the known deviation `retained-diaphragm-connections`. No part was added
or removed. `scripts/correct_sr8_yellow_3d_review.py` reproduces the change (revision 1.4-3d-review) and is
idempotent; the `review_correction_record_3d` in `model_manifest.json` lists the 54 changed parts.

### SR 1 over Wabash River (`sr1-wabash`)

#### SR 1 over the Wabash River: drawing review (revision 1.1)

An external review of the model was checked against the 2004 B-25747 plans. Printed sheets 6-15 are PDF pages 23-32;
sheets 17-18 are PDF 35-36, after sheet 15-1 on PDF 33. The model's +Y side is **west**. The sheet 6 north arrow points up-station, and the 2026 survey control places
"Lt." points to the west. Section A-A (sheets 7 and 15), looking up-station, has the reinstalled gas line on the
right, east fascia, which the 2026 general plan also names. The model had the two sidewalk names swapped and the gas line on the west fascia.

| Corrected objects | Count | Before | After | Evidence |
|---|---:|---|---|---|
| Roadway slab `deck` | 1 | 200 mm thick, top El. 248.829, ends on skew lines (up to 2.93 m off) | 300 mm, top original P.G. + 49 mm (El. 248.878) with the 30.48 m vertical curve, square ends 53.156 m before and 55.328 m after Pier 3 | Sheets 6, 7, 9, 10, 15 |
| Sidewalks `walk_±1` | 2 | Fell 2 % outward, 228 mm step, floating above the gutter; names swapped | 280 mm curb, 2 % fall to the roadway, 190 mm fascia, curb carried onto the spandrel walls; `walk_1` = West, `walk_-1` = East | Sheets 7, 14, 15 |
| Rails `parapet_*`, `panels_*` | 24 | Plain 380 mm block, 37.5 mm coping setback, representative panels | Sheet-18 section (380 base and cap, 290 stem, 19 mm recesses), 75 mm setback, sheet-17 panel layout, rail ends per sheets 9-10 | Sheets 9, 10, 17, 18 |
| Rail pilasters `railpost_*` | 10 | Centred on the rail line, 0.349 m out along X, 90 mm too far out | On the support lines at the arch-ring face (\|Y\| 7.131), outer face 75 mm inside the coping | Sheets 17, 18 |
| Gas line `gas_line` | 1 | West fascia, Y +7.40 | East fascia, Y −7.40, between the floor ends | Sheets 7, 15; 2026 sheet 13 |
| Abutments `pier_0`, `pier_4` | 2 | Span faces 0.5715 m into the end openings | At the springing, Face Abut. Sta. 1+968.894 / 2+060.563 | Sheet 6 |
| Arch barrels `arch_0..3` | 4 | 14.174 m, flush with the spandrel walls | 14.262 m, 44 mm beyond each spandrel face | Sheets 9, 15 |
| End-floor walls `endwall_*` | 4 | Ended on the old skew floor limit | End at the square floor ends | Sheets 9, 10 |

Rail heights changed because the parapets, panels and pilasters were reseated on the corrected sidewalk, about 0.16 m higher. The sidewalk concrete
brackets of sheets 11-14 are not modelled yet; they need new components and are recorded as a known deviation. A
second known deviation records that the 300 mm soffit lies about 51 mm inside the hidden fill envelopes, which still
follow the old surface. The gas line's height and diameter remain an undimensioned envelope, as its part note states.

`scripts/correct_sr1_wabash_review.py` reproduces the correction from revision 1.0 and is idempotent. Part ids are
unchanged, and the 30 unaffected meshes are byte-identical. The record and before/after SHA-256 are in
`model_manifest.json`.

#### Second round

##### Second review (revision 1.2)

An independent check of revision 1.1 found three more drawing discrepancies, plus a missing joint detail.
- **Rail pilasters:** they stand on a coping widened locally to 1836 mm from the curb face (sheet 14), with their 485 mm body 75 mm inside it (sheet 18). The pilasters (`railpost_*`) move 75 mm outward to |Y| 8.176-8.661, and each sidewalk gets five 1217 × 75 mm coping projections.
- **Rail joints:** the rails now stop at the 13 mm open joints of sheets 17-18: both sides of the pier pilasters, and only the span side of the abutment pilasters.
- **Wall slots:** the spandrel and end-floor walls had stopped on the skew pier and abutment faces, which left 20 open slots of 59-176 mm beside the square spandrel pilasters. The walls are now closed to the 13 mm filled joints of sheet 18, flush on the wing side of the abutments.
- **Gas line:** the envelope ran 60 mm into the five east spandrel pilasters. It is re-hung at the position and size scaled from the 1:30 section A-A on sheet 15: centre 0.958 m outside the spandrel face and 0.942 m below the sidewalk top at the coping, 350 mm diameter. It is not dimensioned on the plans.
- **Deferred:** the matching 13 mm sidewalk joints, recorded as `sidewalk-joints-not-modelled`, and the sheet 11-14 brackets.

`scripts/correct_sr1_wabash_review_2.py` reproduces revision 1.2 from 1.1 and is idempotent. It changes 41 parts without adding or removing any, and the 37 other meshes are byte-identical.

#### Third round: known deviations

The third pass closed most of the three known deviations of revision 1.2. An independent check then found four more problems, which were fixed or recorded.
- **Brackets:** revision 1.3 adds 90 concrete sidewalk brackets.
  - 80 are typical brackets, ten per span and side, at the sheet 11-12 spacing.
  - 10 sit under the rail pilasters.
- **Roadway slab:** it now stops at the longitudinal expansion joints, 779 mm inside the curbs. The joints are left 12.7 mm open, the existing width recorded on the 2026 plans.
- **Curb unit:** the sidewalk castings carry the curb unit drawn on sheets 14 and 15.
- **Walls and pilasters:** the spandrel walls, end-floor walls and spandrel pilasters are cut 610 mm below the sidewalk soffit. Each pilaster has a deeper 838 mm seat under its bracket.
- **Pilaster extent:** the pilasters now reach from the spandrel inner face to their drawn face 1421 mm inside the local coping, as sheet 14 gives. The spandrel walls stay 13 mm clear of them through the full wall thickness.
- **Fill:** the hidden fill meets the slab soffit.
- **Arch crowns:** near each crown the approximate arch ring rises above the cut. There the walls end and the new concrete stops on the ring.
- **Sidewalk joints:** each sidewalk has the 13 mm open joints of sheet 18, 13 mm wide on their 45-degree leg too.
- **Kept as known deviations:**
  - The brackets of the four floor-end zones. They need the flared end zones, end walls and wing-end pilasters, which are not modelled yet.
  - The top of the pilasters beside the brackets, which no sheet shows.

`scripts/correct_sr1_wabash_review_3.py` reproduces revision 1.3 from 1.2 and is idempotent. It changes 29 parts, adds 90 and removes none, for 168 parts in all. Every mesh passes the generic watertight check of `refresh_geometry_verification.py`.

### US 50 EB over Tanners Creek (`us50-tanners-eb`)

##### US 50 EB over Tanners Creek (revision 1.1)

The 2014 reconstruction drawings (B-29709, printed sheets 7-60 = PDF 93-146) were checked against the model after an
external review. **Sheets 20-23** put the FT barrier, beam 1 and Line "A" on the north side, which is the left side looking
up-station. They put the 13 ft 8 in sidewalk and the PS-1 railing on the south side, and the north end of every support at
the lower station ("Skew 20 deg Lt."). The model had the support skew right but the whole transverse layout mirrored.
**Sheet 7** gives the profile: P.I. Sta. 389+40.58, El. 490.90, +0.30 % / -0.32 %, 430 ft curve. The model had taken the
PVI elevation as the curve elevation, so the deck was 0.10 m high.

| Corrected objects | Count | Before | After | Evidence |
|---|---:|---|---|---|
| Whole transverse layout (all parts) | 283 | Sidewalk, PS-1, crown and beam 7 on the left (+Y) | Mirrored about the centre line and re-skewed; supports keep their plan lines; beams, bearings, X frames and posts move rigidly | Sheets 20-23, 26, 43 |
| Grade-following parts (deck, beams, haunches, bearings, pedestals, rails, sidewalk, approaches, joints, X frames) | 245 | Deck 0.100-0.107 m above the profile at the bents | P.G. 490.08 / 490.32 / 490.52 / 490.56 / 490.42 / 490.21 reproduced within 0.003 ft | Sheet 7, sheets 20-22 |
| End bents `cap_0`, `cap_5` | 2 | 75 ft cap, soffit El. 479.29 / 479.53, open between the beams | Semi-integral end bent, 76 ft 5 1/2 in, soffit El. 479.69 / 479.77, carried to the slab soffit with beam pockets | Sheets 26, 29, 32 |
| Interior caps `cap_1`-`cap_4` | 4 | Centred on the deck, soffits El. 478.58-478.86 | 74 ft 3 in, 0.141 m north of the centre line; soffits El. 477.78 / 477.92 | Sheets 34, 35, 39 |
| Columns `column_*` | 24 | 25 / 25 / 11.5 ft at every bent, skewed parallelograms, bases up to 1.26 ft high | Squares aligned with the bent: 3 ft at 23.25 / 23.25 / 10.5 ft (end bents), 4 ft at 25 / 25 / 11.5 ft (interior; 4 ft 6 in below El. 459.67 at Bents 3-4), on the footing tops | Sheets 26, 29, 35, 39 |
| Tie beams `tie_2`, `tie_3` | 2 | El. 457.42-459.67, 4 ft 6 in wide | El. 453.42-457.42, 2 ft 9 in wide | Sheet 39 |
| Bulb-T beams and haunches | 70 | Ends 0.15 m short of the interior bents and 0.01 m short of the end bents; 8 in flange edge | Ends 3 in from the interior bents and 9 in past the end-bent bearings; 4 in flange edge, 4 in taper, 3 in fillet | Sheets 43, 45 |
| Sidewalk and PS-1 | 5 | Top falling 2 % outward; parapet 0.2 m above the deck | 8 in curb, top rising 2 % to PS-1; PS-1 raised 0.170 m and seated on the deck | Sheet 23 |
| Approach slabs | 2 | 20 ft 6 in parallelograms | Square terminal joints, 20 ft 6 in to 46 ft 9 1/4 in | Sheets 58, 60 |
| Footing envelopes (hidden) | 6 | Tops El. 470.01 / 457.24 / 436.24 | Drawn levels El. 464.25-468.75, 450.25-456.75, 429.25-436.25, 464.25-469.50 | Sheets 26, 29, 35, 39 |

Three items are recorded as known deviations in the manifest:
- The four wingwalls and the 3 ft support diaphragms over Bents 2-5 need new components.
- The bearing-seat schedule is not imposed. The beams keep a uniform 0.10 m haunch, so seats are within 13 mm at Bents 2-5 and 91 mm low at the encased end-bent bearings.
- Beam ends stay square.

`scripts/correct_us50_tanners_eb_review.py` reproduces the correction from the generator output and is idempotent.
Before running, it regenerates a sample of the stored parts with the original builder rules and refuses to run if
they differ. Part ids and mesh names are unchanged. The record and the before/after SHA-256 are in `model_manifest.json`.

#### Second round

**Revision 1.2 (second review).** `scripts/correct_us50_tanners_eb_review_2.py` runs after the revision 1.1 script and changes 12 parts. Part ids are unchanged.
- **Sheet 34 PLAN:** the interior caps of Bents 2-5 are rectangles with ends square to the bent. They had been cut parallel to the roadway, giving 70/110 deg corners up to 0.25 m off. Two millimetre-thin seat pedestals for beam 7 are cut back to the new cap end.
- **Sheet 39:** each tie beam gets its twelve 2 ft 0 in radius haunches, reaching El. 459.42 / 451.42 at the column faces.
- **Sheet 32:** the approach slabs are 1 ft 2 1/2 in thick over the 6 in pavement ledge and 1 ft 2 in thick for 1 ft 6 in behind the end-bent back face. The end-bent ledge drops 0.0635 m to 1 ft 2 1/2 in below the slab top.

The east terminal-joint station callouts (391+92.68 on sheet 60, 391+92.86 on sheet 22) disagree with the dimensioned slab edges, which the model follows. The deck is 9.5 mm short at each end of the 492 ft 0 7/8 in. Both are recorded as known deviations, alongside the earlier wingwall, support-diaphragm and seat-schedule entries.

#### Third round: known deviations

**Revision 1.3.** `scripts/correct_us50_tanners_eb_review_3.py` runs after the two earlier scripts. It closes the known deviations of revision 1.2 and the items raised by the independent check.

- **Seats (sheets 26, 29, 35, 39).** The bearings now sit on the scheduled seats.
  - At Bents 2-5 each beam rests on a 3 11/16 in pad (sheet 54).
  - The caps are terraced to the seats, with 3 in keyways at the steps. The 52 separate pedestals are removed.
  - At Bents 1 and 6 each beam rests on a 1 in anchor bar, and its soffit is at the seat.
  - The beams follow their seats plus the sheet 45 camber. They rise 15 to 58 mm, and the haunch now varies.
- **Support diaphragms (sheets 43, 53, 54).** The 3 ft diaphragms over Bents 2-5 are new parts. Their keys drop into the cap keyways, with the drawn polystyrene space left all round.
- **Wingwalls (sheets 26, 28, 29, 31).** The four 1 ft 3 in wingwalls are new parts. Their tops are 1 ft 3 1/2 in below the approach slab, as in section C-C. The approach slabs are thickened over them, with a tongue in a wall keyway.
- **Deck ends (sheets 20-22).** The deck ends move out 9.5 mm each, to 492 ft 0 7/8 in.
- **Approach slabs (sheets 58, 60).** The approach slabs are measured from the end of the bridge floor.
- **Beam ends (sheets 46-48).** At the end bents the beam top flanges are set back and cut on the skew. They no longer reach into the approach slabs.

The model now has 239 parts. One small item remains as a known deviation: the depth of that flange notch is not dimensioned.

### Minnich Road NB / SB over I-469 (`minnich-road`)

#### 1. External review corrections (revision 1.1)

An external review of the Minnich Road model (proposed 2026 rehabilitation, INDOT B-44533) was checked against the
drawings; in this set the printed sheet number equals the PDF page number. Five findings were confirmed and corrected;
two are real but left for a regeneration and recorded as known deviations.

| Corrected objects | Count | Before | After | Evidence |
|---|---:|---|---|---|
| Concrete end diaphragms `end_diaphragm_0`, `end_diaphragm_4` (new) | 2 | Not modelled | 2 ft thick normal to the bent, back face 1 ft 1 3/4 in behind the bearing line, Girder 1 to Girder 8, deck soffit to the top of the bottom flanges | Sheets 44-45, Section X-X and front elevation |
| End-span girders `plate_0_*`, `plate_3_*` | 16 | Ended at the end-bearing centre line | End 7 1/2 in (0.1905 m) beyond it | Sheets 27-28, 30-31 girder elevations |
| Haunches `haunch_0_*`, `haunch_3_*` | 16 | Ended at the bearing line | Follow the girder ends | Derived from the girders |
| Span D shallow-segment bottom flanges `plate_3_*` | 8 | 18 x 1 in | PL 22 x 1 1/8 in over 39 ft 0 1/2 in, web 32 1/8 in, underside unchanged | Sheets 30-31 |
| Type FC rails `rail_-1_*`, `rail_1_*` | 8 | Traffic face vertical to 10 in at the full 16 in base | 3 in toe, break 11 in from the back face at 10 in, 9 in top | Sheets 49 and 52, Section C-C |
| Girder-numbered labels (plates, haunches, bearings, pedestals, splices, stiffeners, frames) | 427 | Girder 1 at -Y (west) | Plan numbering: Girder 1 at +Y (east); part index j is Girder 8-j, frame bay j+1 is bay 7-j | Sheet 25 framing plan with sheet 19 |

The diaphragms are poured with the deck and encase the girder ends; the steel inside is embedded, not cut out. The
plan levels (El. 820.06 / 816.31 at Girder 8, Bent 1 = 8 + 2 + 36 - 1 = 45 in) confirm the bottom at the top of the
bottom flange. Part ids are unchanged; only labels carry the plan girder numbers.

Known deviations recorded in the manifest: the twelve end-bent X frames (`frame_0_0_*`, `frame_3_1_*`) have no
counterpart on sheets 25-26 but are analysed components of the FEM demonstration, so they stay until that ledger is
reconciled; the grade places the PVI at the structure midpoint instead of Bent 3 (sheet 16, PVI 15+26.77), a tilt of
up to 21 mm at the end bearings that needs a regeneration of every part; and the end-bent mudwall faces sit 4 in
closer to the bearing line than Section X-X.

`scripts/correct_minnich_road_review.py` reproduces the correction from the generator revision and is idempotent; it
refuses to run unless the generator formulas reproduce the current meshes. The record and before/after SHA-256 are in
`model_manifest.json`. Unrelated geometry buffers are preserved.

#### Second round

##### Second check (revision 1.1 unchanged)

An independent second check of revision 1.1 confirmed F3-F6 and the F4 girder numbering: Girder 1 is on the east edge,
which is +Y and left of increasing station (north arrow and plan, sheets 19 and 25), and the model is not mirrored. It
raised three points on the end diaphragms and on the two deferred findings. None needed a change. The end diaphragms
are 29.2 mm deeper than Section X-X (sheet 45: 8 in deck, 2 in fillet). Their bottoms sit correctly on the top of the
bottom flanges; the excess comes from the generator's uniform 0.08 m haunch and needs a regeneration. The 1-5 mm
overlap of the diaphragm tops with the deck soffit is the chord error of the three-vertex deck soffit under the crest
curve, and all 32 haunches show it too (0.9-5.4 mm). The end-bent X frames and the PVI offset remain recorded known
deviations.

#### Third round: known deviations

Four known deviations of revision 1.1 were closed from the drawings in revision 1.3.

- **Grade.** The PVI is now at Bent 3, as sheet 16 shows. That moves every part by a straight-line amount of up to
  26 mm. The model matches the drawn elevations on sheets 23 and 44 within 0.01 ft.
- **Fillet.** At the end bents the girders sit 2 in below the deck, as Section X-X shows. The raise fades out at the
  field splices. That transition is our decision, because the drawings give the fillet only at the end bents.
- **Bearings and caps.** The end bearings use the sheet 34 plates and shims, so they land on the drawn cap levels. The
  end-bent caps are 3 ft 6 in wide, with the drawn flat and stepped tops. The 14 end-bent pedestals were removed.
- **Mudwalls and approach slabs.** The new mudwalls follow Section A-A and sit 3 in behind the deck. Their ends return
  toward the wingwalls as sheet 23 draws them. The approach slabs rest on the mudwall ledge, with their road ends at
  the drawn 20 ft 6 in and their corners turned onto the returns. The four approach-slab extensions along the
  wingwalls were added. The deck corners stop 3 in from the returns.
- **End-bent frames.** The twelve steel frames that stood inside the end diaphragms are now the drawn MC 18x42.7
  channel diaphragms nearest each end bent. Their heights follow sheet 33. They keep their ids for the FEM
  demonstration. Its supports now come from the corrected caps; this changes the results by less than 0.1 %.
- **Stiffeners.** The Bent 5 bearing stiffeners were 1/8 in too tall and now sit on their 1 1/8 in flange.
- **Still open.** One deviation is kept: the existing wingwalls, which carry the slab extensions, are not modelled,
  because their plans are not in this set.

The model has 466 parts. `scripts/correct_minnich_road_review_3.py` reproduces the change.

#### Fourth round: 3D review

A review of the assembled model found two problems. First, the 84 ordinary cross frames stood about 51 mm clear of the
girders, with nothing connecting them. Each frame now hangs on two 1 in x 8 in connection plates. The plates sit on the
web face and run the full web height between the flanges, with the drawn corner clips (sheets 25 and 33). The two
diagonals lie flat on opposite faces of the plates and end 1 3/4 in from the web (sheet 33). The twelve frames nearest
Bents 2 and 4 had one end inside the field-splice plates. They now sit at the drawn station: 12 ft 0 in from the bent at
the new girder's bottom taper, and 1 ft 6 in across it on the existing girder (sheets 27-28, 30-31). The main-span
frames keep their representative stations. Their own connections are not drawn in this set, so the new detail stands in
for them (known deviation). Second, eight stiffener assemblies at Bent 3 were exact duplicates, and they were removed.
The model now has 458 parts. `scripts/correct_minnich_road_3d_review.py` reproduces the change.

### Fletcher Avenue over I-65 / I-70 (`fletcher-avenue`)

#### Fletcher Avenue over I-65 / I-70 (revision 1.1)

On **sheet 55** the north arrow points to the lower right of the plan. **Sheet 52** puts TBM #2 on the "South Curb …
Lt." of Line "Fletcher", and the **S8 framing plan** and **sheet 59** number Girder 1 at the upper (+Y) edge. The −Y
side is therefore north. **Sheet 65** puts the 4'-6" Modified TX railing on the south coping and the 3'-6" TX railing
on the north. The model had the railings on the wrong sides and the side names and girder numbers reversed.

The retained steel follows **S9/S10** (PDF 100/101): a 60" × ⅝" web, deepening to **6'-8" (80")** at Pier 2 on the S10
typical haunch. The model had a 72" web. **S7** (PDF 98) gives the stepped Pier 2 bridge seat, El. 718.310 to 718.090,
where the model had a flat top at El. 719.12. **Sheet 66** dimensions each approach slab **54'-2"** at its long corner.
**Sheets 55/60** give a 2% roadway, a level deck under the north walk and 1.5% walks.

| Corrected objects | Count | Before | After | Evidence |
|---|---:|---|---|---|
| TX railing panels and pilasters `tx_*`, `txpost_*` | 44 | 4'-6" at −Y labelled south; 3'-6" at +Y | North (−Y) 3'-6" TX; south (+Y) 4'-6" modified TX, base 1 ft taller | Sheets 55, 60, 65 |
| Names of girders, stiffeners, splices, bearings, seats, bays, walks, drains, wings | 366 | Girders 1–8 from −Y; "South" at −Y | Plan girder = 8 − model line; S8 shoe marks; Wings A–D; ids unchanged | S8, sheets 52, 55, 59 |
| Girders `girder_*` | 16 | 72" web at the pier, ⅜" web, 2½" exterior pier flanges | 80" web on the S10 haunch (57'-7½" / 57'-5½" radii, 20 ft); ⅝" web; 2¾" / 2¼" pier flanges; tops unchanged | S9, S10 |
| Haunch stiffeners, field splices and bolts, Pier 2 cross frames | 96 | Fitted to the 72" web | Follow the corrected web and flanges | S9, S10 |
| Pier 2 wall and seat parts `pier_2_wall`, `B2_seat_1..7` | 8 | Top El. 719.12, isolated risers | Wall top El. 718.090; continuous steps El. 718.255–718.690 at the S7 riser spacing | S7 |
| Pier 2 shoe envelopes `B2_bearing_*` | 8 | 0.32 m | Seat step to girder bottom, 0.385–0.430 m (ES1/ES2 18", ES3 16" plus shims) | S8, S12 |
| Approach slabs and walks `approach_*`, `approach_walk_*` | 6 | Square ends at 20'-6" on the centre line | Square ends X −56.361 / +56.189 m: 54'-2" long edge, 35'-4" on the centre line | Sheets 55, 66, 71 |
| Deck, walks, haunch tops, joints, backwall tops, drains | 27 | 1.5% (1.18% north), 2% walks, 177 mm north curb | 2% roadway, level north deck, 1.5% walks, 8" curbs on the sheet 52 profile | Sheets 52, 55, 60 |

Several things are deliberately left as they are:

- The girder tops are not moved, so the haunches become 35–90 mm thick.
- The Pier 2 shoe envelopes are derived between plan seats and girders. They differ from the drawn shoe heights by
  −48 to +9 mm, which is recorded as a known deviation.
- The four Type TTX railing transitions and the RCBA slab extensions (sheets 66, 68, 69) are recorded as not modelled.

`scripts/correct_fletcher_avenue_review.py` reproduces the correction from the original model and is idempotent. The
record and the before/after SHA-256 are in `model_manifest.json`. The display model, the catalogue and the inspection
sheets still need to be rebuilt from the corrected GLB.

#### Second round

**Revision 1.2 (second review round).** The **S9/S10** field-splice details show a continuous 60" web with fillers
outside the thinner field flanges: 1" with 26"×⅞"×6'-3" splice plates on girders 1 and 8, and ½" with 24"×1"×6'-9"
splice plates on girders 2–7. The field segments beyond 40 ft from Pier 2 are therefore lowered by 1" or ½" so that
the webs align. The splice plates and fillers are rebuilt to those sizes along the girder grade, which closes bottom
gaps of up to 54 mm. The haunches, the abutment bearing stiffeners and the derived abutment bearing envelopes follow
the lowered segments; the haunches are now 35–102 mm thick. On the S9/S10 elevations the girders end **4½"** beyond
the abutment bearing centre lines, and the model now matches. Following **sheets 56 and 61–62**, both backwall tops
now meet the crowned deck soffit, where up to 188 mm had been open under the crown. At Abutment 3 the backwall steps
down to the approach-slab soffit beyond the deck end. A suggested 20" Span B flange was rejected: S10 gives 24". The
TTX transitions remain deferred, and the representative web splice plates are recorded as a known deviation.
`scripts/correct_fletcher_avenue_review_2.py` runs after the first-round script, is idempotent, and records the
before/after SHA-256 in `model_manifest.json`.

#### Third round: known deviations

**Revision 1.3.**

The four Type TTX modified railing transitions are modelled from **sheets 68 and 69**. Wings A and C are 3'-6" high
and Wings B and D 4'-6"; their pay limits are 30'-2", 29'-4", 17'-2" and 20'-5½". Each has the taller end-bent pilaster
and six windows with R 1'-0" heads. They stand on the 1'-2" RCBA slab extensions of **sheets 66 and 67**, with the
sidewalk concrete of **sheet 70**. The approach slabs are narrowed to the 66'-2" of sheet 66. The bridge rail end
pilasters stop ¼" short of the deck end, which leaves the drawn ½" open joint. The wing envelopes move out to 1" beyond
the extensions.

The field splices follow **S9 and S10**: 19" × ⅝" × 4'-6" web plates, 10" × 1" inner bars and 4,992 ⅞" bolts. The
lateral bracing is placed as **S11** draws it. Its 36 WT envelopes sit on 39 new ⅜" gusset plates 5" above the bottom
flange, which run from the web to the bolted ends of the tees.

The Pier 2 shoe stacks are drawn (S12 shoes, S13 shims) but are 19–70 mm taller than the model leaves room for. The
haunches meet the 2 3/16" minimum of **sheet 65**, which is measured to the underside of the top flange, but their
profile is derived. Both stay known deviations: the 2026 top-of-steel (screed) data is not in the plans, and the 1971
elevations fit the 2026 deck only with a datum relation that no sheet gives. The TTX face recesses and the splayed 1971
wings are also listed, with their drawn dimensions and what is still missing.

`scripts/correct_fletcher_avenue_review_3.py` runs after the second-round script and is idempotent.

#### Fourth round: 3D review

**Revision 1.4.** A review of the assembled model found that the cross frames floated. Each X stopped about 0.3 m from the girder webs, with nothing joining it to them. Sheet **S11** shows how cross frame XF-1 is connected. Its members end on 3/8 in gusset plates at the four corners. Each gusset is bolted with four bolts at 3 in to a connection plate on the girder web. The model now has these gussets: 364 plates in 91 new parts, one part per cross frame. Each plate is 12 in high at the web, which is the 9 in bolt line with 1 1/2 in end distances as on S9/S10. It holds the last 6 in of its diagonal, a length scaled from XF-1. Every diagonal end now sits on a plate, and every plate lies on its web face. Where a bottom lateral gusset crosses a plate, the plate is cut to it. The connection plate itself is not sized on any sheet, so the gusset runs to the web in its place. The X envelope is unchanged, so the XF-1 chords and the 4 ft 0 in depth are still not modelled. This is a new known deviation, `crossframe-xf1-envelope`. `scripts/correct_fletcher_avenue_3d_review.py` runs after the third-round script and is idempotent.

### SR 10 over I-65 (`sr10-i65`)

An external review of the model was checked against the 1998 B-23753 rehabilitation plans (binder PDF 21-40, printed
sheet = PDF - 20) and the 2026 approach plans; all eight findings were confirmed. Local Z = plan elevation - 210.000 m.

| Corrected objects | Count | Before | After | Evidence |
|---|---:|---|---|---|
| Pier 3 hammerhead, cap ends, columns | 5 | Cap top Z 5.654, column tops 4.739 (181 mm low) | Cap El. 215.835, central 5.334 m at El. 215.879; column tops El. 214.920 | Sheet 12 (PDF 32) elevation |
| Pier 3 fixed shoes `B3_bearing_1..9` | 9 | 460 mm at the outer beams, 260 mm inside | 260 mm fixed base + top shoe at every beam | Sheet 14 (PDF 34) |
| Pier 3 shims `B3_seat_0..8` | 7 + 2 new | Derived seat risers under the shoes | Shim plates 49/13/32/13/26/13/32/13/49 mm on the shoes | Sheet 16 (PDF 36) shim table |
| Span B/C beams, haunches, Pier 2/4-side splices, diaphragm rows | 112 | Nominal profile at Pier 3 | Beam bottoms at seat + shoe + shim + 13 mm splice plate (+2 to +47 mm), linear taper to zero at Piers 2/4 | Sheets 12-16 |
| Pier 3 splices and fasteners | 18 | 457 mm east of the pier | On the Pier 3 centre line | Sheet 13 (PDF 33) |
| Span C diaphragm rows 7-8 | 16 | 7.061 / 13.665 m east of Pier 3 | 6.604 / 13.208 m (chain from the diaphragm 457 mm west) | Sheet 13 |
| Integral end bents | 2 | Straight top, up to 160 mm under the crowned deck | Deck-soffit top with crown; 150 mm pavement ledge under the approach slab | Sheet 9 (PDF 29); 2026 sheet 13 (PDF 61) |
| Wingwalls | 4 | 2.1 m approachward / 1.6 m spanward | 1.6 m approachward / 2.1 m spanward | Sheet 9 plan |
| Pier 3 collision walls | 2 | Y 3.000-7.620 m | Y 2.883-7.863 m (25 mm joint, 300 mm beyond the column) | Sheet 12 |
| Span A/D diaphragms, bays 2 and 7 | 12 | 380 mm channels | MC460 (460 mm) | Sheets 13, 15 (PDF 33, 35) |
| Bridge railings | 8 | 254 mm toe, single slope, 240 mm top | 100 mm toe, break 125 mm in at 280 mm, 225 mm top | Sheet 19 (PDF 39) |

The Pier 3 seat stack could not be restored without refitting the beams. With the drawing cap, shoe and shim, beam
line 2 would sit 21 mm inside its shoe, because the girder profile is nominal (1998 grade less a constant 75 mm
haunch). The beams of spans B and C are therefore set to the drawing stack at Pier 3 and taper linearly back to the
unchanged profile at Piers 2 and 4. Piers 2 and 4 show the same nominal-profile mismatch (caps about 47 mm low, beams
15-60 mm below the plan seat stack). This is recorded as a known deviation and left for a girder-elevation rebuild.
The derived seat risers at Pier 3 keep their ids as the shim plates. B3_seat_0 and B3_seat_8 are new parts. Other
part ids are unchanged.

`scripts/correct_sr10_i65_review.py` reproduces the correction from the generator output and is idempotent. Unrelated
GLB buffers are preserved. The record, the before/after SHA-256 and the changed, added and renamed parts are in
`model_manifest.json`.

#### Second round

**Second review correction (revision 1.2).** An independent check of revision 1.1 was verified against the drawings,
and `scripts/correct_sr10_i65_review_2.py` applies the confirmed items. The drawings are north-up with stations
increasing east, and sheet 13 puts Beam Line No. 1 on the north edge (native +Y). The model's ids number the lines
from the south (model index j = drawing line 9 - j); the ids are kept and the mapping is a known deviation.

The Pier 3 splice cover plates now have their drawing sizes:
- lines 1/9: Type I PL 16x292x1130 (sheet 14);
- lines 2-8: the retained 1964 PL 12 in x 15/16 in x 111 in (S9, PDF 11).

The span B/C beams rise a further 3.0 / 10.8 mm at Pier 3, so shim, plate and flange stay in contact. All 88
diaphragms follow sheets 13 and 15:
- exterior bays: MC460x63.5 with the bottom 200 mm above the W840 bottom;
- span A/D interior bays: MC460 centred ("Dimensions A equal ±25 mm");
- span B/C interior bays: the retained W460x68, centred (1964 S10);
- the bay between drawing lines 6-7 (Y -3.556 to -1.778 m): C380x74.

Other corrections:
- The 2026 approach slabs are 12 in deep, not 14 in (pay item, PDF 62/67), and the end-bent ledges follow them.
- The Pier 3 widened footings move to |Y| 3.163-8.163 m (sheet 12 footing plan).

184 meshes changed; no parts were added or removed. The record and the before/after SHA-256 are in
`model_manifest.json` (`review_correction_2_record`). The known deviations record:
- the top-plate embedment of up to 9.3 mm at lines 2/8, caused by the nominal 920 mm beam depth;
- the unchanged Pier 2/4-side splices;
- the approach-ledge standard detail.

#### Third round: known deviations

`scripts/correct_sr10_i65_review_3.py` (revision 1.3-deviations) works through the known deviations and two
independent checks of this round. The beams now rest on the drawn supports at all five lines of support. At the end
bents they sit on the pile cutoff plus a 19 mm plate, and their ends run 150 mm past the bent centre line. At Piers
2/4 they sit on the cap (El. 215.972, 216.016 in the middle) plus a 125 mm bearing and the sheet 16 shim. Between
supports they follow the grade. The beams use the depth and flange thickness of their drawn sections: 840 x 21.7 mm,
903 x 20.1 mm and 911 x 23.9 mm. With these, the sheet 17 haunch table agrees with the pier elevations to about 2 mm;
the table is measured to the underside of the top flange.

The haunches follow the sheet 17 detail: they are 100 mm wider than the flange on each side and wrap its edges. The
splices follow their details. The new splices have the sheet 14 plates, bars, fillers and bolts. The 1964 Pier 3
splices have their web plates, inner bars and rivets. The diaphragms reach the drawn distance from the beam webs,
and the five C380 replacements lap onto ten added stubs of the old diaphragms. The end-bent ledges are level at El.
216.850, and the approach slab ends rest on them. Steel parts that reach into the concrete are cut out of the haunch
and the deck. Every contact was measured and closes to within 0.01 mm, and every mesh is a closed solid.

Display names use the drawing beam-line numbers; ids are unchanged. 253 parts changed and 14 were added (four shims
and ten stubs), for 328 parts in all. None were removed.

Five known deviations remain:
- the id numbering;
- the approach end beyond the ledge (on standard drawings not in the set);
- the haunch table at the end bents (it has no stations);
- four rivets under each Pier 3 shoe (their treatment is not drawn);
- the side of the stub on which each C380 sits.

The FEM recipe still uses the nominal 920 mm sections and must be updated and regenerated.

### US 35 over Deer Creek (`us35-deer`)

#### 1. End bents, wingwalls, FC railing and approach slabs (revision 1.1)

An external model review raised five discrepancies. All five were confirmed against the plan set (INDOT B-45063,
document 9721578; the printed sheet numbers equal the PDF page numbers).

**End-bent offset (sheet 13).** The plan view of the end bents dimensions **7 in** between the centre line of the end
bent and the centre line of the bridge. The 43 ft bent is divided 5'-1 5/8" + 3 @ 10'-6 1/4" + 6'-3 5/8", with
the long end at Beam 1 (north) at Bent 1 and at Beam 4 (south) at Bent 2. The general plan (sheet 11) shows the
same asymmetry: the wing outer faces lie about 2 ft 2 in beyond the coping at Wings B and C and about 1 ft at Wings A
and D. The model had both bents centred on the bridge centre line.

**Upper integral concrete (sheet 15).** Sections A-A, B-B and C-C show the concrete placed around the beam ends
across the full 3'-10" bent width, with its span face flush with the lower cap. The model's closure bays stopped
0.22 m behind that face, which left a false shelf on the cap.

**Wingwalls (sheets 13 and 17).** Each 1 ft wing is 12'-0" long from its tip to the span-face corner of the bent,
and its outer face continues the bent end. The 5.7 CY for two wingwalls matches the 8 ft that project beyond the back
face. The model started the 12 ft at the bearing line, so each tip reached 0.60 m too far into the fill.

**FC railing (sheet 23 section A-A).** The railing is 2'-9" high, with a 3" vertical toe, then 5" over 7", then 2"
over 23", a 9" top, and its rear face 2" inside the coping. The model had a 7 in toe and a single slope, with the
face up to 0.11 m off at the break. The corrected rails total 19.6 CY, as in the bill of materials.

**Approach slabs (sheets 3, 11 and 25).** The 35'-11" slabs extend 18'-3" north / 17'-8" south of the structure
centre line at the west end and 17'-8" / 18'-3" at the east end. Their square ends are at Sta. 1270+76.06 and
1272+43.94. The model had centred them and given them a flat top between the edges, 0.11 m below the crowned deck at
the centre line.

| Corrected objects | Count | Before | After | Evidence |
|---|---:|---|---|---|
| End-bent caps `cap_1`, `cap_2` | 2 | Centred on the bridge centre line | Moved 7 in (0.1778 m) along the bent, toward Beam 1 at Bent 1 and toward Beam 4 at Bent 2 | Sheets 11, 13 |
| Pile stubs, drain runs, back faces | 16 | Laid out about the bridge centre line | Moved with the bents; piles 2'-1 1/2" from the bent ends | Sheets 13, 14 |
| Integral closure bays `integral_infill_*` | 10 | Span face 0.2248 m (along X) behind the cap face | Flush with the cap span face; outer bays end at the moved bent ends | Sheets 14, 15 |
| Wingwalls `wing_*` | 4 | 12 ft from the bearing line (4.26 m including the bent end) | 12 ft from the span-face corner to the tip; outer face on the moved bent end | Sheets 13, 17 |
| FC railings `FC_rail_±1` | 2 | 7 in toe, single slope, 8.80 m³ each | Sheet 23 section; 7.50 m³ each (19.6 CY total) | Sheets 22, 23 |
| Approach slabs `approach_±1` | 2 | Y ±5.4737 m, ends X ∓25.634 m, flat top | 18'-3"/17'-8" split, ends at Sta. 1270+76.06 / 1272+43.94, 2% crown | Sheets 3, 11, 25 |
| Approach transition extensions `extension_*` | 4 | Inner edge at ±5.4737 m | Inner edge refitted to the corrected slab edge | Sheet 25 |

Beams, bearings and seat risers stay on the girder lines; part ids and mesh names are unchanged. The TFC transition
envelopes are left as modelled and recorded as a known deviation: their shape is in INDOT standard drawings that are
not part of this plan set, so at the butt joints their faces differ from the corrected FC section by up to about
0.1 m.

`scripts/correct_us35_deer_review.py` reproduces the correction from the previous version and is idempotent. The
record and the before/after SHA-256 are in `model_manifest.json`.

#### Second round

##### 2. Handedness, wing tops and crowned closure tops (revision 1.2)

A second, independent check of revision 1.1 found that the whole model was the mirror image of the drawings, and two
smaller defects. All three were confirmed against the plan set.

**Handedness (sheets 11, 13, 14 and 17).** The general plan's north arrow points up the sheet and stations increase to
the right, so north is left of increasing station: +Y in the model's right-handed native frame. Beam 1 and Wings B and
D are on the north side, and the north end of each bent is up-station (15° right skew). The higher north wing tops
and Beam 1 seats on the +2.35 % grade (Bent 1: 851.45 / 846.08 against 851.21 / 845.88) confirm this. The model had
Beam 1 at Y = −4.6482 m and its bent lines leaning the other way, so both layout and skew were reversed. Every vertex
is reflected, (X, Y, Z) → (X, −Y, Z), with triangle winding reversed. Part ids are unchanged and keep their meaning:
beam_0_0 is still Beam 1, and the suffix −1 still names the north member (wing_0_-1 = Wing B, FC_rail_-1), now at
Y > 0. The revision 1.1 bent offsets and approach-slab widths now lie on their drawn sides.

**Wing tops (sheets 14 and 17).** The tops are El. 851.21 / 851.45 / 853.91 / 854.16 (Wings A / B / C / D) at the
centre line of the bent, and match the approach slab at the tip. The model's tops followed the extended deck surface
less 0.09 m and were 0.09–0.10 m low. Each wing top now passes through its T/El. and runs at the +2.35 % grade to the
tip, where it meets the approach top at the coping line within 5 mm.

**Crowned closure tops (sheets 12, 14, 15 and 25).** The two closure bays between Beams 2 and 3 had flat tops that
left an 18.5 mm wedge under the crowned deck soffit. The end-bent back faces had the same flat top and left up to
25 mm under the approach slabs crowned in revision 1.1. All four now carry a centre-line vertex and follow the crown.

| Corrected objects | Count | Before | After | Evidence |
|---|---:|---|---|---|
| All parts | 72 | Mirror image: Beam 1 at Y = −4.6482 m, bent lines dX/dY = −tan 15° | Reflected: Beam 1 at +4.6482 m (north), dX/dY = +tan 15° | Sheets 11, 13, 14, 17 |
| Wingwalls `wing_*` | 4 | Top 0.09 m below the extended deck surface | El. 851.21 / 851.45 / 853.91 / 854.16 at the bent centre line, +2.35 % to the tip | Sheets 14, 17 |
| Centre closure bays `integral_infill_0_4`, `integral_infill_1_4` | 2 | Flat top, 18.5 mm below the soffit at the centre line | Crowned, on the soffit | Sheets 12, 14, 15 |
| Back faces `backwall_0`, `backwall_1` | 2 | Flat top, up to 25 mm below the crowned approach slab | Crowned, at soffit level | Sheets 12, 25 |

The 25 mm display gap between the deck end and each approach slab is kept and recorded as a known deviation: the
Type IA joint is detailed in INDOT Standard Drawing E 609-BRJT-01, which is not in this plan set.
`scripts/correct_us35_deer_review_2.py` reproduces the correction from revision 1.1 and is idempotent. The record and
before/after SHA-256 are in `model_manifest.json`. The display model and preview must be rebuilt from the corrected GLB.

#### Third round: known deviations

Revision 1.3 closes most of the two known deviations, and what closing them exposed. The bridge railing was laid out
wrongly. Sheets 11 and 23 put each 102'-4 3/8" FC railing with one end at the deck end, at the acute corner (north-east
and south-west). The TFC transition there stands on the approach slab extension. At the other end the TFC stands on
the deck. The model had centred both rails, so every TFC straddled the deck end. The rails now have square ends and
move 2.29 m along the bridge. The four TFCs follow the sheet 11 plan. Each is 15'-8" long and 2'-9" high throughout.
Each starts with the FC section and ends in a vertical 9 in wall. The acute-corner extensions are now the drawn
15'-10" x 1'-6" (sheet 25). Sheets 15 and 25 show the approach slab cast against the deck end, so the 25 mm display
gap is closed. The slab is 2 in deeper, 14 in, over the 9 in ledge of the bent and 1'-6" beyond, then returns at
45 degrees. It now bears on the ledge instead of cutting 101.6 mm into the bent, and the closure bays stop at the
deck end. The beams now have the drawn end copes: no top flange outside the 8 in web over the last 6 in (sheets 19
and 20). Their corners no longer reach past the deck end. The two obtuse-corner slab envelopes had no drawing
counterpart. They are replaced by the drawn 11 ft integral concrete curbs Type B (Modified). The joint strips now
run only along the slab. One deviation remains. The TFC face between the joint and the vertical end is interpolated.
Its end details, and what supports the obtuse-corner TFC ends beyond the deck end, are in INDOT Standard Drawings
E706-TTFC-01 to -03 and E706-CBRT-01. `scripts/correct_us35_deer_review_3.py` applies this after the first two
scripts and is idempotent. Two parts were removed and two added; the model has 72 parts.

#### Fourth round: 3D review

A 3D review found that the four wingwalls overlapped the end bents. Each wing started at the span face of the bent,
so its first 1.21 m lay inside the cap, the outer closure bay and the back strip. That counted 3.94 m3 of concrete
twice, and the coincident faces showed as stripes. The sheets split this concrete at the back face of the bent. Sheet
17 bills 5.7 CY for two wingwalls, which is the part beyond the back face (5.70 CY at Bent 2). Sheet 14 draws the bent
up to the wing top at its ends. Each wing part now starts at the back face of the bent and keeps its tip, faces and
top. The root inside the bent belongs to the bent. The outer closure bays and the back strips now rise to the wing top
in the 1 ft wing column. No volume is shared, the overall shape is unchanged, and each wing bears on the back face of
its bent. `scripts/correct_us35_deer_3d_review.py` applies this after the first three scripts and is idempotent. No
parts were added or removed; ten parts changed (revision 1.4-3d-review).

### US 224 over Eight Mile Creek (`us224-eight-mile`)

#### US 224 over Eight Mile Creek: review corrections (revision 1.1)

An external review of the model was checked against the 2026 repair plans (B-44532, printed sheet = PDF page) and the
1985 plans B-16317 (`sources/existing_plans_9548292.pdf`). Six exterior errors were confirmed and corrected:

| Corrected objects | Count | Before | After | Evidence |
|---|---:|---|---|---|
| Retained barriers `retained_rail_-1/1` and TFC transitions | 5 | Back face 50 mm inside the coping; toe 6.6556 m from Line A; clear roadway 13.311 m | Back face flush with the 46 ft 8 in coping; toe 22 ft 0 in; 44 ft 0 in clear roadway | Sheet 9 typical sections |
| TFC transitions `TFC_transition_*` | 3 | Top tapering from 2 ft 7 1/2 in to 0.70 m at the far end | 2 ft 7 1/2 in for 8 ft 1 in, rising to 2 ft 9 in at 11 ft 5 in, 2 ft 9 in to the 15 ft 8 in end | Sheet 12, Sections C-C to F-F and railing elevations |
| Approach slabs `approach_-1/1` | 2 | Centred, 22 ft 2 in each side; flat top 105 mm below the bridge floor at Line A | West 22 ft 0 in N / 22 ft 4 in S, east 22 ft 4 in N / 22 ft 0 in S (22 ft 0 in under the NE extension); top crowned 1.5625 % and flush with the bridge floor at the joint | Sheets 13-14 plans; sheets 3, 11, 15 |
| RCBA extensions `extension_*` | 3 | Inner edge 22 ft 2 in from Line A | Inner edge on the 22 ft 0 in slab edge | Sheets 13-14 |
| Wings B (SW) and C (NE) `wing_0_1`, `wing_1_-1` | 2 | 90.7 deg to the abutment, 4.70 m long, top about El. 831.1 | 60 deg to the abutment, 11 ft 7 3/8 in long, top El. 831.54 / 831.50 for 1 ft 1 3/8 in, then down to El. 826.58 / 826.50 | 1985 sheets 5-7 (plan, Elevation C-C, End Elevation B-B) |

The obtuse-corner wings B and C bisect the 120 deg corner (60 deg to the abutment). The acute-corner wings A and D bisect
the 60 deg corner (30 deg), which the model already had. The wing root points, their 0.40 m nominal thickness and the
cross-section shape of the TFC envelope are unchanged.

Three findings were not corrected and are recorded in `known_deviations`:

- Wings A and D (23 ft 10 1/2 in kinked walls falling from El. 831.65 / 831.47 to El. 827.38 / 827.30, partly removed
  under the 2026 RCBA extensions) still need a rebuild of their outline.
- At the NW and SE corners, a new 5 ft 9 5/8 in Type FC railing on the existing wingwall comes before each TFC. Those TFCs
  and their extensions therefore lie about 1.4 m farther from the bridge than modelled. The NE transition is placed
  correctly: its new 7 ft 10 5/8 in railing replaces the last 6 ft 9 in of the existing railing on the deck.
- The deck, overlay and copings run over the reconstructed mudwall to the floor end. The drawings place the PCF joint
  at the span face of the mudwall, and the mudwall top is part of the floor surface.

`scripts/correct_us224_eight_mile_review.py` reproduces the correction from revision 1. It refuses to run unless the
generator formulas reproduce the original parts, and it is idempotent. The record, the changed part ids and the
before/after SHA-256 are in `model_manifest.json`. The display model and the inspection sheets are rebuilt from the
corrected GLB.

#### Second round

##### Second review corrections (revision 1.2)

A second check of revision 1.1 was verified against the same drawings. The plans (sheets 7 and 8) put north up with stations increasing to the east, so north is to the left of increasing station. In the collection's right-handed frame that is +Y. The model had been built with north at -Y and the abutment lines skewed the other way, so it was the exact mirror image of the bridge. Every vertex was reflected across the centre line (Y -> -Y) and every triangle's winding reversed. Stations, grade, crown, elevations and all revision 1.1 dimensions are unchanged. Part ids keep their meaning: suffix -1 is still the north member.

| Corrected objects | Count | Before | After | Evidence |
|---|---:|---|---|---|
| All parts | 91 | Mirror image: north at -Y, north abutment ends up-station | North at +Y, north abutment ends down-station (30° Lt. skew) | Sheets 7, 8 plans, north arrow |
| TFC transitions `TFC_transition_*` | 3 | One section throughout: 1 ft 4 in base, 7 in toe, single slope | C-C (1 ft 4 in base, 2 1/2 in toe, knee) to 7 ft 2 in, through D-D (11 5/8 in) at 8 ft 1 in to the 9 in F-F wall at 11 ft 5 in | Sheet 12, Sections C-C to F-F |
| Mid-span drains `midspan_drain_*`, `deck`, `overlay` | 4 | Closed 2 in rod hanging below an unpierced slab | Open 2 in cores through slab and overlay, lined by a 3 mm display skin | Sheet 9, typical section, drain details |

Two items are deferred and recorded in `known_deviations`. The first is the overlay taper to the drain edge, whose depth is not dimensioned. The second is the root of the obtuse-corner Wings B and C, which stand 50 mm clear of the deck edge because their root is the model's cap end. The 1985 plan starts them at the coping corner. The `acute-corner-wings` entry now gives the measured tip elevations, El. 831.15 / 830.96.

`scripts/correct_us224_eight_mile_review_2.py` reproduces the correction from revision 1.1 and is idempotent. It refuses to run unless the model is the revision 1.1 GLB. The record, a note on the revision 1.1 coordinate frame and the before/after SHA-256 are in `model_manifest.json`. The display model and the inspection sheets must be rebuilt from the corrected GLB.

#### Third round: known deviations

Revision 1.3 resolves three of the five deviations left by revision 1.2 and decides one. Two independent checks
then led to two further passes.

- **Floor end.** The deck now ends at the PCF joint, as sheets 10 and 11 show. Between that joint and the Type I-A
  joint at the floor end is the 1 ft 0 in reconstructed mudwall, flush with the overlay. The joint is 2 in wide at
  Abutment 1 and 1 5/8 in at Abutment 2. It turns up 6 in into each railing toe. Over the last 1 ft of the deck the
  overlay dam reaches 5 5/8 in below the surface.
- **Railings.** Three new Type FC railings follow sheet 12. The northwest and southeast TFCs and their extensions
  move about 1.4 m outward. All three transitions have square ends. The extensions reach 2 in beyond the railing back
  face. The retained railings now have the drawn FC section.
- **Wings.** Wings A and D follow the 1985 Elevation F-F, with a root leg, a kink and a battered wall, and are cut
  down under the extensions. Wings B and C start at the coping corner on the abutment front face, as the 1985 plan
  shows. Their rear face has a 1:12 batter.
- **Abutments.** The caps, stems and footings now follow the 1985 Section A-A. The footings are 2 ft thick at
  El. 817.03 and 816.95, and the stems and wings stand on them. The bearing pads lie along the bearing line.

Three items are still recorded in `known_deviations`: the overlay taper at the mid-span drains, the size of the
paired bearing pads, and the old wingwall root behind the northeast mudwall. None of them is dimensioned in the set.
Three parts were added and 39 changed, for 94 parts. The source ledger deck length is now the 12.918 m slab between
the joints. `scripts/correct_us224_eight_mile_review_3.py` reproduces the change from revision 1.2 and is idempotent.

#### Fourth round: 3D review

Revision 1.4 fixes the one structural finding of the 3D review. The approach slabs had nothing under their roots.
The existing 6 in pavement ledge behind each mudwall was missing. It is now modelled as the 1985 Section A-A
draws it: 6 in wide and 1 ft 0 in deep. Its top is level, at El. 830.51 at Abutment 1 and 830.49 at Abutment 2,
as the 1985 elevations give. As sheets 11 and 15 show, each slab end is thickened down to the ledge top. The
thickening runs 2 ft 0 in behind the mudwall and then returns at 45 deg to the 1 ft soffit. The end is 13.6 to
18.8 in deep because the slab top is crowned. Each slab now sits on the 9 in lean concrete base of sheet 15. Four
parts were added and two changed, for 98 parts. The 25 mm open joint at each slab root is kept. Its fillers are
recorded in `known_deviations`, because Standard E 609-RCBA is not in the set.
`scripts/correct_us224_eight_mile_3d_review.py` reproduces the change from revision 1.3 and is idempotent.

### Virginia Avenue over I-65 NB / I-70 EB (`virginia-avenue`)

#### 1. Plan side, crown, rails, approaches and end cross-frames (revision 1.1)

An external review found the transverse layout mirrored. On the **General Plan (printed sheet 31 = PDF 31)**, the
**Superstructure Details (sheets 36, 37)** and the 2013 **Framing Plan (existing plans 9548460, sheet 10 = PDF 28)**,
stations increase to the right, so plan-top is the left side looking up-station. The **16'-1" south shared-use path**,
**Girder No. 1** (the 2013 54 in replacement) and the TX rail with the reset ornamental rail are at plan-top.
**Girder No. 9** and the **6'-1" north sidewalk** are at plan-bottom. The model had these on the opposite side,
although its 44°19'06" left-skew bearing lines were right. At Abutment 1 the Girder 1 bearing is now 18.156 m behind
the Girder 9 bearing, as drawn.

| Corrected objects | Count | Before | After | Evidence |
|---|---:|---|---|---|
| Girders, haunches, bearings, splices, cross frames, seat risers, walks, pavers, bollards, wings, drain | 122 (+2 new risers) | South path, Girder 1 and the south rail at native Y < 0 (Girder 1 B1 bearing X -8.30 m) | Mirrored about Line "Vir" in skew coordinates: Girder 1 at Y +9.2964 m, B1 bearing X -26.45 m (Sta. 12+61.53); bearing lines unchanged | Sheets 31, 36, 37; existing sheet 10 |
| Deck, joints, approach slabs | 5 | Crown on the roadway centre, 5 ft off Line "Vir" | Crown on Line "Vir" (bridge centre line), 2 % to the south curb 15 ft left and the north curb 25 ft right | Sheets 31, 37 ("Proposed P.G." on Line "Vir", 7'-0" from the shoulder line) |
| Type TX rail panels `TX_rail_*` | 10 | 32 in above the sidewalk; 2 3/4 in air gap under the south panels | 3'-6" (42 in) above the top of sidewalk; south panels stand on the deck concrete under the pavers | Sheet 39 typical section; sheet 37 |
| Reset ornamental rail | 1 | Centre line 6 in outside the rail's outer face | Centred on the 12 in rail and standing on its top | Sheet 39 |
| Approach slabs `approach_1/2` | 2 | Terminals at 12+40.75 and 14+60.62; no curb step | Square terminals at **Sta. 12+41.89** and **14+53.54**; 6 in south curb with pavers (1.9 %) and 8 in north curb (1.5 %) over the slabs | Sheet 41 plans; sheet 43 Sections A-A to D-D |
| End cross-frames `end_cross_frame_B1_1`, `_B2_1` (new) | 2 | Missing | W16x45 strut 3 in below the girder top, L5x5x3/8 V and bottom strut 6 in above the bottom flange, on each bearing line between Girders 1 and 2 | Existing plans sheets 10 and 14 (PDF 28, 32) |

Retained-steel elevations are not dimensioned in the plans, so they are re-derived on the corrected deck by the
model's own rules: girders 50 mm below the soffit, bearings under the girders, and the abutment seat at the lowest
bearing. The two abutment walls and mudwalls follow the new seat datum. Girder 8, beside the north gutter, is now the lowest bearing. The derived seat risers `seat_1_8` and
`seat_2_8` were therefore removed (zero height) and `seat_1_3` and `seat_2_3` added. The profile grade (local
datum 8.4 m at the centre of structure, linear 0.54 ft fall over the span) is now applied on Line "Vir", where the
plans put it.

The rail windows remain nominal. The 1971 end struts of bays 2–8 (existing S-7, PDF 65) are recorded as a known
deviation. Part ids are unchanged except for the four added and two removed seat/frame parts. The rail and wing labels
now say south/north. The transverse values in `source_ledger.json` (FEM input) were mirrored to match, so Girder 1 is
at Y = +9.2964 m there too.

`scripts/correct_virginia_avenue_review.py` reproduces the correction and is idempotent. It first rebuilds the
uncorrected geometry and requires it to match the published GLB. The record, the before/after SHA-256 and every
changed, added and removed part id are in `model_manifest.json`. Unrelated buffers are preserved, and the two
footings are untouched. Verification read the actual GLB triangles:

- Crown at Line "Vir" with 2.0 % to both gutters, and rail tops 42.00 in above the sidewalk with no gap.
- Approach terminals at the sheet 41 stations, and curb steps of 0.152 / 0.203 m.
- Bearing-to-girder contact within 2e-7 m.

[Open source PDF at page 31](/assets/virginia-avenue/drawing#page=31) · [Download corrected full GLB](/assets/virginia-avenue/model) · [Open bridge](/#bridge/virginia-avenue)

#### Second round

##### 2. Haunch at the crown, mudwall joint filler and end-frame copes (revision 1.2)

An independent check of revision 1.1 found three interface errors. It also confirmed the plan side again: sheet 36 and
existing sheet 10 show the north-arrow tip to the lower right and stations increasing to the right, with Girder No. 1
and the 16'-1" path at plan-top, which is the left side looking up-station.

| Part(s) | Before | After | Evidence |
|---|---|---|---|
| `haunch_5` | Top straight between its flange edges; 5.08 mm air gap under the crown once the crown moved to Line "Vir" over Girder 5 | Top follows the crowned soffit (vertex at Y = 0); bottom unchanged | Sheets 31, 37 (crown); sheets 36, 37 fillet detail |
| `mudwall_1`, `mudwall_2` | Top straight between the deck edges: 65.7 mm into the deck at the south curb, 47.5 mm at the north curb, 55.4 mm gap at the crown | Top follows the deck soffit (breaks at both curbs and the crown), 1 in below it for the 1 in PEJF adhered to the top of the mudwall | Sheet 38 elevations and typical sections |
| `end_cross_frame_B1_1`, `_B2_1` | Square-cut W16x45 flange corners passed through the Girder 1 / 2 webs on the skewed bearing line (34-39 cm³ each) | W16x45 ends coped parallel to the webs, 1 in clear of the web faces; angles unchanged | Existing plans 9548460 sheet 14 (PDF 32): "Cope flange adjacent to connection", "1 in Min. (Typ.)" |

Bearing stiffeners and connection plates are still not modelled, so the 1 in clearance on sheet 14 is applied to the
web face. The Abutment 2 drain is at Sta. 13+88.30 instead of 13+87.50 (sheet 36), 0.245 m up-station. This minor item
is recorded in `known_deviations` and was not changed. `scripts/correct_virginia_avenue_review_2.py` runs after the
first correction script and is idempotent. It requires the model to match revision 1.1 part by part and replaces only
the five meshes above. Part ids, the other 143 meshes and their buffers are unchanged. The record, with before/after
SHA-256 and measured interfaces, is `review_correction_record_2` in `model_manifest.json`. Verification read the
actual GLB triangles:

- The haunch meets the soffit within 0.001 mm.
- The mudwall tops are 25.4 mm below the soffit across the full width.
- The end frames have zero overlap with the girders.

#### Third round: known deviations

Two items were left after the second round. Both were re-read on the sheets and checked again independently.

The old note said the 1971 end struts "E.S.1 / E.S.2" of bays 2-8 were missing. That was a misreading. On the 1971
Framing Plan (existing plans 9548460, S-7 = PDF 65), E.S. and F.S. mark the expansion and fixed shoes. Sheet S-9
details them, and the bearings already stand for them. The members that do sit on both bearing lines of bays 2-8 are
the jacking frames J.F.1 and J.F.2. Sheet S-8 gives their size: a 1/2 x 42 in web and 5/8 x 9 in flanges, on the
centre line of the shoes. Sheet 38 of the 2026 plans still shows them at both abutments. Fourteen frames were added,
`jacking_frame_B1_2` to `_B1_8` and `jacking_frame_B2_2` to `_B2_8`. No sheet dimensions how high they sit on the
girder web. We scaled it from the S-8 detail: the top is 5 1/4 in below the girder top. This is recorded as a decision.
Each frame carries its two S-8 centre stiffeners: 7/8 x 4 1/4 in plates, one each side of the web, at the jacking
point. The frame ends stop 3 in from the girder webs and are cut parallel to them. That cut is an envelope of the frame
and its bent connection plate. S-8 does not show where the frame itself ends, or how long the plate legs are. The
girder bearing stiffeners are dimensioned, but they would pass through these ends and through the 2013 end frame,
whose copes are not dimensioned. So the end connections stay a known deviation.

The Abutment 2 roadway drain moved to Sta. 13+87.50, the station on sheet 36. Its pipes now follow sheet 39. The
downpipe drops to just under the top of the abutment wall. The 6 in collector runs along the wall face to the north
end and falls 0.5 %. It then drops down the wall face. Before, a straight run passed through four bearings. Sheet 39
is not to scale, so three values are decisions:
- the offset from the wall, set by the drain inlet;
- the pipe top, at the top of the wall;
- the end of the drop, at the foot of the wall.

`scripts/correct_virginia_avenue_review_3.py` makes these changes and is idempotent. It replaces one mesh and adds
fourteen. All other meshes and buffers are unchanged. The checks read the actual GLB triangles. The new frames and the
re-routed drain overlap no part, except the drain inlet seated in the deck as before. The collector falls exactly
0.5 %.

#### Fourth round: 3D review

**Revision 1.4.** A review of the assembled model found that the five intermediate cross frames of bay 1 ran their
bottom strut through the bottom flange of Girder 1. The generator set one strut level for both girders, and Girder 1 is
the shallower girder. The frames are now built as the 2013 sheets draw them (existing plans 9548460, sheets 10 and 14).
Sheet 10 dimensions them along Girder 1 from the bearing: 15 ft 3 in, then four spaces at 22 ft. The generator had
measured at mid-bay, so the frames move 1.0 m down-station; frame 1 had been sitting in the splice plates of Girder 1.
Sheet 14 bolts the L5x5x3/8 strut and V diagonals to a 7 x 5/8 in connection plate on each girder web, and sheet 10
draws that plate from flange to flange. The ten plates are now modelled, two in each frame. The strut sits 3 in above
the higher bottom flange and the diagonals stop 6 in below the lower top flange, the minimums at which sheet 14 draws the
frame. Every member laps both plates, and nothing overlaps the girders or splices. The gusset at the foot of the V is
drawn but not dimensioned, so the diagonals stand on the strut in its place; this is the new known deviation
`bay1-intermediate-frame-gussets`. No part was added or removed. `scripts/correct_virginia_avenue_3d_review.py` runs
after the third-round script and is idempotent.

### SR 44 over Branch of Little Blue River (`sr44-little-blue`)

#### 1. Datum, approaches, railings, bents and Wing D (revision 1.1)

An external review of the model against contract B-44483 (printed sheet numbers equal PDF page numbers) found
seven errors, and all seven are confirmed by the drawings.

- **Vertical datum.** The bent bottoms and pile tips used Z = 3 m at El. 878.64 (P.G. at Bent 1). The profile was
  anchored at Sta. 507+75 instead, where P.G. is 878.58. The deck, approaches and rails were therefore **18 mm high**
  against the substructure. The profile also kept curving past the end of the vertical curve. **Sheet 11** gives
  P.V.I. 507+10, El. 879.00, a 170 ft curve, and +0.730 % / −0.622 %.
- **Approach slabs.** They were built with square outer ends and 6.2 to 19.4 m coping lengths. **Sheet 12** shows
  skewed ends 20'-6" beyond the slab ends, crossing the roadway faces at 507+18.56, 507+58.56, 507+91.44 and
  508+31.44. **Sheet 18** shows each slab between the roadway faces, with a Type TFC extension under the
  transitions.
- **North railing.** It was 2.48 m east of its drawn position, and every railing end was skewed. **Sheet 18**
  gives 15'-8" TFC + 15'-7 3/8" FC + 15'-8" TFC from the west deck joint on the roadway face, all with square
  ends. The south rail is 15'-8" + 31'-10 5/8" + 15'-8".
- **TFC transitions.** Their height fell to 11 in at the outer ends. **Sheet 18** draws "Top of Railing" level at
  2'-9".
- **FC section.** The model had a 10 in vertical toe. The **sheet 18** typical section has a 3 in toe, a knee 11 in
  from the back at 10 in height, and a 9 in top.
- **Integral bents.** The bent tops ignored the deck crown and left a **138 mm wedge of air** under the slab at the
  centre line. **Sheet 17** shows the slab cast on the bent.
- **Wing D.** It was modelled as a straight wall against the coping. **Sheet 16** shows a 12 ft wall 2'-9" outside
  the coping, joined to the bent end by a 4'-1 1/8" × 3'-8" block, with top El. 878.12 to 878.06.

| Corrected objects | Count | Before | After | Evidence |
|---|---:|---|---|---|
| Deck `deck` | 1 | 18 mm high; parabola continued past 507+95; skewed ends through the rail zones | Z = 3 m at El. 878.64 (P.G. 878.64 / 878.50 at the bents); −0.622 % tangent east of 507+95; ends square under the rail ends (north coping 31'-5 3/8", south 31'-10 5/8") | Sheets 11, 12, 18 |
| Approach slabs `approach_1/2` | 2 | Square outer ends; 43 ft wide; 51.1 m³ each | Skewed ends 20'-6" beyond the slab ends; 40 ft between roadway faces plus TFC extensions 2" beyond each TFC; 24.6 / 23.9 m³ | Sheets 11, 12, 18 |
| Concrete railing `FC_rail_±1`, `TFC_±1_±1` | 6 | North assembly 2.48 m east; skewed ends; 10 in FC toe; TFC falling to 0.29 m | Square ends on the drawn chains (north 507+23.39 to 507+70.34, south 507+63.39 to 508+26.61); FC section 3 in toe / 11 in knee at 10 in / 9 in top; TFC level at 2'-9", face tapering to a 9 in end | Sheet 18 (plan, elevations, typical section); sheet 11 railing limits |
| Integral bents `integral_bent_1/2` | 2 | Flat tops, 138 mm below the crowned soffit at the centre line | Tops on the crowned slab soffit; bottoms El. 870.97 / 870.83 unchanged | Sheets 14, 17 |
| Wing D `wing_2_1` | 1 | 12 ft × 1 ft wall against the coping, level top El. 878.24 | 12 ft wall 2'-9" outside the coping plus a 4'-1 1/8" × 3'-8" block; top El. 878.12 → 878.06, bottom El. 870.83 | Sheet 16 (plan, Section D-D, Wing D elevation); sheet 18 |
| Joints, guardrail runs, Wings A–C tops | 9 | On the old datum; joint strips across the full width; guardrail runs inside the relocated TFCs | Moved to the corrected datum; joint strips across the roadway only; guardrail runs start at the slab end beyond each TFC | Consequential |

Two items are recorded as known deviations in the manifest.

- Wings A, B and C keep their simplified level-topped plan. Their tips are 0.15 to 0.28 m from the sheet 18 tips.
  They were not part of this review.
- The bents' 9 in pavement ledge remains at slab-soffit level.

`scripts/correct_sr44_little_blue_review.py` reproduces the correction from the as-built model and is idempotent.
The manifest holds the record: source pages, the datum, the railing chains, the Wing D outline, the 21 changed part
ids and the before/after SHA-256. Part ids are unchanged, the 16 pile envelopes are byte-identical, and the source
drawings are unchanged. The display model, catalogue and inspection sheets need rebuilding from the corrected GLB.

#### Second round

##### 2. Guardrail connections at the TFC ends (revision 1.2)

A second, independent check of revision 1.1 confirmed six of the seven corrections and the handedness (+Y = north =
left of increasing station; sheet 12 north arrow and stationing). It left one item open: the steel guardrail
connections. The four representative guardrail runs stopped 105.8 mm short of the concrete transitions. Their rail
element was also a 0.30 m wide strip lying flat at 0.06 m high. **Sheet 18**'s north and south railing elevations
draw a 20 in thrie beam with its terminal connector bolted onto each TFC end. The connector laps 2'-6" onto the TFC
(2'-0" at the north-east Type TGB) and sits 11 to 31 in above the deck (10.27 to 30.27 in at NE, scaled). Each run's
rail element is now an upright 20 in × 0.06 m plate on the TFC end face (|Y| = 6.2738 m), lapping the drawn length
and running to the end of the as-built run. The posts are unchanged, and no parts were added or removed.
`scripts/correct_sr44_little_blue_review_2.py` applies this after the first script and is idempotent. The manifest
`review_correction_2_record` holds the sheet 18 point values, the per-corner extents and the before/after SHA-256. A
new known deviation, `guardrail-representative-runs`, records what remains representative: posts without blockouts,
no corrugations, and the remainder of each transition.

#### Third round: known deviations

##### 3. Wings A–C, the pavement ledge, the approach slab ends and the guardrail layout (revision 1.3)

A third check settled the three known deviations. The wings and the ledge were resolved. The guardrail layout was
resolved, and only the standard-drawing details remain open.

- **Wings A, B and C.** They were level-topped boxes against the coping. **Sheets 15, 16 and 18** draw each wing as
  a 12'-0" × 1'-0" wall 1" outside the coping. Wings A and C join the bent along its 45° faces. At Wing B the end of
  Bent 1 is square. The tops now slope as drawn (El. 878.25 → 878.26, 878.10 → 878.15, 877.91 → 877.85).
- **Pavement ledge.** The bent tops were all at the slab soffit, 8 in below the approach slabs. **Sheet 17** shows a
  9" ledge 1'-2" below the top of deck. The approach slab ends are 1'-2" deep and rest on it, for 1'-6" beyond the
  bent with a 2" step at 45° (dimensioned on **sheet 19**, Section E-E). The schematic sheet 18 elevations show 15",
  and we did not use them.
- **Guardrails.** Each corner had only a 2 m stand-in run. The model now has every pay item to its **sheet 11**
  limits:
  - three MGS Without Curb transitions and the Type TGB transition;
  - the 87.5 ft MGS W-beam run;
  - three Type OS end treatments;
  - the curved Type 1 terminal.

  Posts sit at the **sheet 11 and 12** positions, within 2.4 mm of the drawn symbols. Next to the bridge they are at
  1'-6 3/4", then 3'-1 1/2", then 6'-3". They go 52 in into the ground, as the **sheets 23–28** cross sections and
  sheet 18 draw them (7'-0" posts). Rail and post heights come from **sheets 12 and 18**. The curved terminal
  follows the drive grade of **sheet 26**. For the north-east posts we used the plans, which put the last post on
  the pay limit. The sheet 18 elevation draws them 6 in further out. The sheet 3 typical section shows 6'-0" posts,
  but every cross section shows 7'-0" posts.

  Rails and posts are simple envelopes. Corrugations, blockouts, bolts, end heads and anchors are drawn only as
  undimensioned cells. They follow INDOT standard drawings that are not in the contract set.

| Corrected objects | Count | Before | After | Evidence |
|---|---:|---|---|---|
| Wings A–C | 3 | Level boxes against the coping, tips 0.15–0.28 m off | Drawn outline 1" outside the coping; sloping drawn tops | Sheets 15, 16, 18 |
| Integral bents | 2 | Whole top at the slab soffit; Bent 1 south end skewed | 9" ledge 1'-2" below the deck top under the approaches; Bent 1 south end square | Sheets 15–18 |
| Approach slabs | 2 | 12" thick up to the slab end | 1'-2" end on the ledge and 1'-6" beyond the bent, 2" step at 45° | Sheets 15, 16, 17, 19 |
| Guardrail transitions | 4 | 2 m runs, 4 posts at 0.667 m | Full transitions, 17 or 10 posts at the drawn spacing, 52 in embedment, thrie/W-beam heights | Sheets 11, 12, 18, 24, 25, 27 |
| New guardrail parts | 5 | None | MGS W-beam run, three Type OS end treatments, curved terminal on the drive grade | Sheets 3, 11, 12, 23, 26, 28 |

`scripts/correct_sr44_little_blue_review_3.py` applies this after the second script. It is idempotent. Five parts
were added and none removed, so the model now has 42 parts. The manifest `review_correction_record_3` holds the
decisions, the plan and post coordinates, and the before/after SHA-256.

### SR 1 over Six Mile Creek (`sr1-six-mile`)

#### SR 1 over Six Mile Creek: clear roadway and overlay limits (revision 1.1)

**Printed sheet 4 (PDF 4)** gives a curb-to-curb roadway width of **44 ft** and an out-to-out width of
**47'-1½"**. **Sheet 7** shows a **44'-0" Clear Roadway** (10 + 12 + 12 + 10 ft) between 1'-6" barriers, with the
polymeric overlay drawn between the barrier toes. **Sheet 8** schedules 352 SYS of deck overlay (44 ft × 72 ft) and
279 SYS of approach overlay (2 × 44 ft × 28.5 ft). The model had set each barrier 50 mm inside the deck edge, which
left a clear roadway of **13.349 m (43'-9.6")**. It had also run the 3/8 in overlay across the full deck, through
the barrier bases and over the bridge-side half of each Type 1-A joint seal that sheets 3 and 7 call for resealing.

| Corrected objects | Count | Before | After | Evidence |
|---|---:|---|---|---|
| Barrier panels `rail_±1_0..2` | 6 | Traffic-face toe at ±6.675 m, back at ±7.132 m; clear roadway 13.349 m | Toe at ±6.7056 m (22 ft), back at ±7.1628 m (¾" inside the coping); clear roadway 13.4112 m (44 ft) | Sheets 4 and 7 |
| Deck overlay `overlay` | 1 | Full 47'-1½" width, 317.9 m² in plan, ends at the joint centre lines | 44 ft between the barrier toes, 296.4 m²; ends at the edge of each 30 mm seal envelope, so the seals are exposed | Sheets 3, 7 and 8 |
| Approach slabs `approach_0`, `approach_1` | 2 | No overlay information | Notes record the non-warranted polymer overlay over the 44 ft roadway (279 SYS for both); not modelled because no thickness is given | Sheets 3, 7 and 8 |

The barriers move rigidly by 30.95 mm along their skewed end lines and down the 1.56 % crossfall, so their 18 in
base, assumed 0.9 m profile and skewed ends are unchanged. The overlay keeps its 3/8 in thickness, crown and
crossfall. The 15 mm cut-back at each end is half the model's assumed 30 mm seal display width, not a drawing
dimension.

`scripts/correct_sr1_six_mile_review.py` reproduces the correction from the original build and is idempotent. The
record and the before/after SHA-256 are in `model_manifest.json`.

#### Second round

**Revision 1.2: approach slab far ends.** On the **sheet 7** plan, each RCBA overlay area ends in a line square to
S.R. 1. Its **20.5 ft** and **36.5 ft** lengths run along the edges of the **44 ft roadway**, 22 ft either side of
the S.R. 1 line, and their 16 ft difference is 44 ft × tan 20°. **Sheet 8** schedules 279 SYS = 2 × 44 ft ×
28.5 ft. The model had spread the 16 ft over the full 47'-1½" deck instead. Its far ends were therefore 1.40° off
square, and the roadway-edge lengths were 21.03 and 35.97 ft. Every far-end vertex of `approach_0` and `approach_1`
now lies at X = ∓19.751675 m (the deck half-length plus 28.5 ft), with Y and Z unchanged. The roadway-edge lengths
are now 20.49 and 36.51 ft and the slab volume is unchanged. The largest move is 0.176 m, at the deck-edge corners.
Two items stay as known deviations:
- the approach polymer overlay, because no thickness is given and the model shows one colour per part;
- the joint seals, which span the full deck width where sheets 7 and 8 give about 47 ft per joint across the
  roadway.

`scripts/correct_sr1_six_mile_review_2.py` runs after `correct_sr1_six_mile_review.py` and is idempotent.

#### Third round: known deviations

**Revision 1.3: joint seals limited to the roadway.** On the **sheet 7** plan, each resealed Type 1-A joint runs
across the 44 ft roadway hatch only, and it is dimensioned **47 ft** along the skew (44 ft / cos 20° = 46.8 ft).
**Sheet 8** schedules **94 lft** for both joints. The model's seal envelopes ran the full 47'-1½" deck width,
50.15 ft along the skew. They also sat 1 mm into the barrier bases. `joint_0` and `joint_1` now stop at the barrier
toes, 22 ft (6.7056 m) from S.R. 1, and are 46.82 ft long. Their stations, depth and crossfall are unchanged. They
now touch the barriers and the deck overlay without overlapping them. No parts were added or removed. The approach
polymer overlay stays a known deviation: sheets 3, 7 and 8 give its plan extent but not its thickness. The contract
special provision for "Polymer Overlay, Bridge Deck Approaches" would settle it.
`scripts/correct_sr1_six_mile_review_3.py` runs after `correct_sr1_six_mile_review_2.py` and is idempotent.

#### Fourth round: 3D review

**Revision 1.4: approach seats and wing trims.** A 3D review found that neither approach slab bore on anything. The
slab undersides are flat at 5.588 m. The end walls under them stop at the deck soffit, 38 mm lower at the crown and
150 mm lower at the deck edges. No sheet of this overlay contract shows an end bent, a seat, the wings or an
approach slab section, and the deck, approach slabs, end walls and wings are all assumed. Two new parts, `seat_0`
and `seat_1`, now fill the part of each end wall that projects past the deck end, from the wall top up to the
approach underside. They are 0.26 m wide and run the full 47'-1½" width. They use only levels and widths that were
already in the model, and they are labelled hypothetical. Each approach slab now sits on its seat with no gap. The
check also found that each of the four wings started at the support line, so 0.53 m³ of it lay inside its end wall
(2.12 m³ counted twice). Each wing now stops at the wall faces, so every volume belongs to one part. Since no sheet
shows how the wings meet the walls, this split is a modelling choice. Nothing overlaps now except the 30 mm joint
display strips, as before. The end walls are unchanged. `scripts/correct_sr1_six_mile_3d_review.py` runs after
`correct_sr1_six_mile_review_3.py` and is idempotent.

## 4. Handedness rule (November 2026)

The drawing review found four models that were mirror images of their bridges: US 50 EB over Tanners Creek,
Virginia Avenue, US 35 over Deer Creek and US 224 over Eight Mile Creek. They were corrected in section 3. The cause was
in the generators, not in the drawings:

- `scripts/build_remaining_concrete.py` (US 35, US 224) traced the plans with +Y toward the drawing south. With
  stations increasing to the east, that frame is left-handed. The GLB export (X, Z, −Y) assumes a right-handed frame, so
  both models came out mirrored, skew included.
- `scripts/build_indiana_batch2.py` (US 50) and `scripts/build_remaining_virginia_slab.py` (Virginia Avenue) put the north
  side or Girder 1 at −Y. The US 50 code even calls its −Y overhang "left". Their skews were right, so the layout was
  mirrored and the skew was not.
- The shared library (`scripts/bridge_geometry.py`) said only "Y transverse". Nothing stated which side +Y is, so nothing
  could check it.

The same check found three more defects of this kind in generators whose published models had already been corrected:
`build_indiana_batch2.py` named the SR 1 Wabash sidewalks the wrong way round and put its gas line on the west side;
`build_indiana_batch3.py` put Fletcher Avenue's south walk, its 4 ft 6 in modified TX rail and the level deck under it on
the north side; and `build_sr44_mud.py` wrote `skew_deg = 15` for a 15° Rt. skew (its geometry was right). The SR 44 Mud
FEM recipe had compensated with its own skew sign.

**The rule** (`scripts/bridge_orientation.py`):

- Every model uses one frame: X increasing station, **+Y to the left looking up-station**, Z up. The GLB stores
  (X, Z, −Y), which is a proper rotation.
- **Skew sign:** `skew_deg > 0` is a left ("Lt.") skew. Looking up-station, the +Y end of each support line is
  down-station: x = u − tan(skew_deg)·y. A FEM ledger's `skew_dx_dy` is −tan(skew_deg). The drawn "Lt."/"Rt." callouts
  of nine bridges confirm this sign.
- A generator declares the plan orientation with `Model.orient(up_station, evidence, ...)`. `up_station` is the compass
  direction of increasing station, read from the plan and its north arrow. +Y is that direction turned 90° to the left.
  Sides then follow from compass names (`Model.side('north')`), not from habit.
- A generator that traces a plan in another frame says so (`built_plus_y='south'`). `Model.save()` then reflects the
  model once into the collection frame and reverses the skew sign. US 35, US 224, US 50 and Virginia Avenue now do
  this, so their generators produce the correct side.
- `Model.save()` refuses to write without an orientation. It checks the orientation against the parts and refuses on
  any mismatch: a named reference part (e.g. Beam 1 is north), every part name with a compass word, the skew sign
  against the drawn direction, and the support lines. It also refuses to overwrite a model whose manifest records
  corrections made after the generator ran, unless `BRIDGE_REBUILD_CORRECTED=1` is set.
- Every 3D-workspace manifest carries an `orientation` record (`scripts/record_orientation.py`): the up-station
  direction, the +Y and −Y compass sides, the drawn skew direction and the sheets that show them. SR 1 over Six Mile
  Creek has no north arrow, so its record says how +Y was fixed instead. `test_manager.py` checks every manifest, and
  each bridge's FEM ledger, against it.

**How the generator fixes were verified.** The generators were run into a scratch folder from the repository's
drawings. Their sources outside the repository were replaced by the copies in each bridge folder. The new output was
then compared in plan with the corrected models:

- US 50 EB: deck, rails, joints, bearings, pedestals, X frames, footings and sidewalk are identical to revision 1.1
  (the first correction). The remaining differences are parts that revision 1.1 rebuilt for other findings (beam
  lengths, columns, end-bent caps, tie beams and approaches).
- Virginia Avenue: girders, haunches, splices, bearings, seats, cross frames, rails, walks, wings and drains are
  identical to revision 1.1.
- US 35 and US 224: the ledgers equal the committed (mirrored) ledgers field for field. In plan, 32 of 72 and 75 of 91
  parts are identical to revision 1.2; the old generator matched 1 and 0.

`test_orientation.py` covers the rule and `Model`: reflection, refusal without an orientation, the check on save and the
overwrite guard.

## 5. Beechwood deck underside (revision 2.3, 3D review)

A review of the assembled 3D model found that the deck underside was flat between the drip grooves. Sheets 45 and
46 (PDF 46 and 47) draw an 8 in deck whose top and underside are parallel and both fall 2 % from the crown. The model
joined the inner edges of the two drip grooves with one straight line, so the deck was 300.5 mm thick at the crown
instead of 203.2 mm. It also filled the space of the haunches, the beam tops, the pier diaphragm tops and the tops
of the end-bent concrete (Pour B), which were already fitted to the crowned underside: up to 32 mm into the inner
beams, and the inner haunches lay entirely inside the deck. Revision 2.3 gives the deck a crowned underside 8 in
below the top across the whole width. Only the deck changed; no part was added or removed, and no other part moved.
The haunch tops now meet the deck, the beams stay under their haunches, and the deck no longer shares volume with
them (left-over films are below 0.05 mm). `scripts/correct_beechwood_3d_review.py` reproduces the correction from
revision 2.2 and is idempotent; the record and the before/after SHA-256 are in `model_manifest.json`.

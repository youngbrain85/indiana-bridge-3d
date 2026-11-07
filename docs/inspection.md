# Inspection app (pilot: Beechwood Road Bridge)

Inspectors draw defects on 2D inspection sheets, pick them from AASHTO element-inspection menus and add photos. Each
sketch is tied to the 3D model, so the defect appears on the real member in the 3D workspace. The app runs in a
browser (desktop, tablet with pen, phone) and keeps working offline.

- Open it from a bridge workspace with **Inspect** (top bar), or at `/inspect#beechwood`
  (`inspect.html#beechwood` on the static site).
- Back in the 3D workspace, **Defects** (or `D`) shows the defects saved on this device. Click a defect to see its
  card (element, condition state, quantity, location, measurements and photos) with a link back to the sheet.

## The screen

The sheet is the largest thing on the screen, with no toolbar over it: the sheet picker (tablets and phones) and
zoom float on it. The top bar holds only the bridge, the sync state, a link to the 3D model and Settings. The panel
belongs to the open inspection: its picker and two tabs, **Defects** and **Elements**. While a defect is being placed
or edited, the panel shows only that defect. The form puts what the inspector measures and decides first
(measurements, condition state, photos, notes) and folds what the sketch already settled (element, defect code,
quantity, sheet) under **Details**; **Save** stays in view at the foot of the panel.

## Recording a defect

1. **Start an inspection**: date, type (Routine, Initial, In-Depth, Damage, Special, Underwater, NSTM, Service),
   inspectors and notes. Defects always belong to an inspection.
2. **Choose a sheet** from the list (a picker floating on the sheet on tablets and phones).
3. **Add defect**, then pick what you found: cracking, delamination/spall/patch, exposed rebar or strand,
   efflorescence, abrasion, corrosion, the bearing defects, settlement, scour or impact damage.
4. **Draw it**: trace a crack or exposed bar, outline an area, or tap a point defect. A pen, a mouse or one
   finger draws; two fingers move and zoom. After the first pen stroke, fingers only move the sheet (palm rejection;
   it can be fixed on in Settings).
5. The app finds the **view and the element** from where you drew (shaded surfaces are inspectable; grey outlines are
   context). A sketch must stay inside one view and on a shaded surface. The element can be changed in the form.
6. Enter the **measurements**. The app suggests a **condition state** from them (below) and computes the **quantity**
   from the sketch. Both can be changed; a condition state different from the suggestion needs a reason. CS 4 marks
   the defect for structural review and reminds the inspector to report it as a critical finding.
7. Add **photos** (camera or files). They are resized on the device to 1920 px on the long edge (JPEG) and named
   `YYYYMMDD_HHMMSS_<sheet>_<defect code>_D<number>_<id>.jpg`.
8. **Save**. Defects are numbered D1, D2, … per inspection; numbers of deleted defects are not reused.

The **Elements** tab of the panel shows the AASHTO element table of the inspection: each element's total quantity split into CS 1–4,
with the defect rows under it, as in NBE inspection reports. CS 1 is the element total less the defect quantities.
**Download CSV** exports the table and the defect list; **Download backup** exports everything, photos included,
as one JSON file that **Settings → Import backup** restores.

## Inspection sheets

`scripts/build_inspection_sheets.py <bridge>` generates the sheets from `model.glb` (numpy and shapely,
`requirements-sheets.txt`). Beechwood has 13 A3 sheets of true orthographic views. Members carry the names used on
the plans (sheets 32–37): Beam Line No. 1 is the west beam and No. 4 the east beam, the end-bent wings are Wing A
(east) and B (west) at End Bent 1 and Wing C (west) and D (east) at End Bent 4, and each end bent is Pour A (the pile
cap) with Pour B (the integral end-bent concrete) above it.

| Sheet | Views |
|---|---|
| DK-1 Deck top surface | Spans A, B, C looking down (pavement markings shown); the bands meet at match lines on the bent centre lines |
| DK-2 Deck underside | Spans A, B, C looking up, east at the top: deck soffit and beam bottom flanges |
| GR-A1 … GR-C2 Beams | Both web faces of each beam line, two beam lines per sheet, all at one scale. The supporting bents are drawn as context, so the beam ends inside them are not offered for recording |
| BT-2, BT-3 Bents | South and north faces (cap, columns, debris wall and the bearings on that side) and both cap ends, with cap and casing elevations |
| EB-1, EB-4 End bents | View 1: the face towards the span (Pour A and Pour B) with beam lines and elevations; views 2 and 3: the complete outside elevation of each wing (wing return and the end of the bent body); a key plan marks the three views |
| RL-1 Barriers | Outside and traffic faces of the west and east barriers, south and north halves |

Each view is a true view (not mirrored): U × V = −normal. Visibility is exact to the model's triangles: where two
parts overlap on the sheet, every pair of overlapping triangles is compared on its depth planes and the overlap is
split along the line where the planes cross, so a shaded region is exactly the surface an inspector sees from that
side. Members cut by a view's clip box are capped at the cut, so a beam stub in front of an end bent hides the face
behind it. Polygon overlays run on a 1 µm grid (snap rounding), which keeps unions of many small triangles robust;
slivers and pinholes narrower than 1 mm that the overlays leave are then removed. Crease lines are drawn only where
no surface hides them in 3D. Where two recorded members meet flush on one face (a wing and the end of the bent body,
Pour A and Pour B), the limit between them is drawn thin and dashed, not as an edge. Bent centre lines carry their
stations, and band ends are marked as match lines. Elevations are in feet, sampled from the model at the plans'
control points; key plans are explanatory and not to the sheet scale.

`sheets.json` publishes, per view:

- `origin`, `u`, `v`, `normal` (glTF world axes, metres), `extent_m` and `placement` (fraction of the sheet, top-left);
- `parts` (inspectable meshes, in hit-test priority) and `regions` (their visible polygons in view coordinates);
- per part: AASHTO element, plan name, measuring axis and element quantity; and the element totals.

A sheet point `(u, v)` in a view (0–1 from the top-left, `v` down the sheet) is the world point

```
P = origin + u * extent_m[0] * U + v * extent_m[1] * V
```

and the defect lies on the first surface hit by a ray from `P` along `-normal`. The origin lies just in front of the
nearest surface of the view, so the ray always starts outside the model. The generator checks this on every build: it
samples points in every region and along its boundary (and one point in each small piece), maps them with the
published numbers and casts the ray into the model; every point must land on its own part. `test_manager.py` checks that `sheets.json` names the current
`model.glb` (SHA-256), and the unit tests check that every region resolves to its part.

### Stable view frames

Defects are stored in view coordinates, so a view's frame never changes under its id. On a rebuild, a view whose
frame is within 1 mm of the published one keeps the published frame exactly; a larger change stops the build. A view
that is redesigned gets a new id: the old frame is kept under `retired_views` with the current view that replaces it
(`replaced_by`, matched by viewing direction and shared parts). The app shows a defect drawn on a retired view on its
replacement, with the sketch mapped through the world plane (the stored record changes only when the defect is
saved again), and the 3D workspace places it with the frame it was drawn on.

Rebuild the sheets whenever the model changes:

```sh
python -m pip install -r requirements-sheets.txt
python scripts/build_inspection_sheets.py beechwood   # about 5 minutes on 4 cores (views in parallel; one by one on Windows)
```

## AASHTO elements, defects and condition states

Element and defect codes follow the AASHTO *Manual for Bridge Element Inspection*, 2nd edition (2019).

| Element | Unit | Beechwood total | Members |
|---|---|---|---|
| 12 Reinforced Concrete Deck | sq ft | 8,316 | deck (252 × 33 ft) |
| 109 Prestressed Concrete Open Girder/Beam | ft | 1,000 | 12 BT 36×49 girders |
| 205 Reinforced Concrete Column | each | 4 | bent columns |
| 210 Reinforced Concrete Pier Wall | ft | 35 | debris walls |
| 215 Reinforced Concrete Abutment | ft | 104 | end bents: Pour A pile caps, Pour B integral concrete, Wings A–D |
| 234 Reinforced Concrete Pier Cap | ft | 66 | bent caps |
| 310 Elastomeric Bearing | each | 16 | bent bearings |
| 331 Reinforced Concrete Bridge Railing | ft | 504 | FC barriers |

Suggested condition states (CS 4 is never suggested: it means the condition warrants a structural review):

| Defect | CS 1 | CS 2 | CS 3 |
|---|---|---|---|
| 1130 Cracking (RC) | width < 0.012 in or spacing > 3 ft | 0.012–0.05 in or 1–3 ft | > 0.05 in or < 1 ft |
| 1110 Cracking (PSC) | width < 0.004 in or spacing > 3 ft | 0.004–0.009 in or 1–3 ft | > 0.009 in or < 1 ft |
| 1080 Delamination/Spall/Patch | — | delamination; spall ≤ 1 in deep and ≤ 6 in across; sound patch | spall > 1 in deep or > 6 in across; unsound patch |
| 1090 / 1100 Exposed rebar / strand | — | no measurable section loss | measurable section loss |
| 1120 Efflorescence / rust staining | — | white, no build-up | heavy build-up or rust staining |
| 1190 Abrasion / wear | — | coarse aggregate exposed, secure | aggregate loose or popped out |
| 1000 Corrosion | — | freckled rust | section loss or pack rust |
| 2230 Bulging, splitting, tearing | — | bulging < 15 % of thickness | ≥ 15 %, splitting or tearing |
| 2240 Loss of bearing area | — | < 10 % | ≥ 10 % |

Width and spacing are both considered; the worse one governs. 2210, 2220 follow the inspector's choice of restriction or
alignment; 4000, 6000 and 7000 have no measured rule and need the inspector's condition state. Cracking defaults to
1110 on prestressed girders and 1130 elsewhere.

Quantities from the sketch, in the element's unit:

- **ft** (girders, caps, walls, abutments, railings): the length of member affected, i.e. the extent of the sketch along
  the member axis, at least 1 ft;
- **sq ft** (deck): the outlined area; a traced crack counts as its length × a 1 ft band;
- **each** (columns, bearings): 1.

## Data

Everything is saved on the device first, in the browser's IndexedDB (`bridge-inspection`: `inspections`, `defects`,
`photos`, `outbox`, `settings`). The 3D workspace reads the same database, so it shows what this device has.
Clearing the browser's site data deletes it: download a backup, or set up cloud sync.

A defect record holds the sheet, view and member, AASHTO element and defect codes, the sketch (`path`, view
coordinates), measurements, quantity and unit (and whether it was typed), the condition state with its suggestion,
basis and any reason for a change, the structural-review flag, location text (station, offset and elevation),
notes and timestamps. Deleting a defect or photo keeps the record with `deleted: true`.

The inspection page also registers a service worker (`inspect-sw.js`, scope `inspect`): once opened online it
loads offline, with every sheet of the bridge cached.

## Cloud sync (Supabase)

Optional. Without it the app works on one device, with backups.

1. Create a project at [supabase.com](https://supabase.com).
2. In **SQL Editor**, run [`supabase/schema.sql`](../supabase/schema.sql). It creates `inspections`, `defects` and
   `defect_photos`, a private `defect-photos` storage bucket, row-level security for signed-in users only, no deletes,
   the `element_condition` view and a check that a changed condition state has a reason. It can be run again safely.
3. In **Authentication**, turn off new sign-ups and add each inspector as a user (email and password).
4. In **Project Settings → API**, copy the **Project URL** and the **publishable (anon) key**. Enter them in the app
   under **Settings**, or put them in `web/inspect-config.js` so every device gets them. Never use the
   `service_role` / secret key in the browser; the app refuses one.
5. Sign in under **Settings** (the gear, or the sync state in the top bar). Clicking the sync state then syncs: it sends the outbox (inspections, then defects, then photos) and fetches
   newer rows from other devices. Local edits that are not sent yet win over the server copy; otherwise the newer
   `updated_at` wins. Photos taken on other devices download when first shown.

The schema is tested on PostgreSQL 16 with stand-ins for Supabase's `auth` and `storage` schemas, and the browser test
syncs against a stand-in for the Supabase API and checks that every column the app sends exists in `schema.sql`.

## Tests

```sh
node --test test_inspection_rules.mjs   # condition-state rules, geometry, quantities, element table, sheets
python test_manager.py                  # sheets match model.glb, routes, path checks
python server.py --port 8766            # then, in another terminal:
node test_inspection_browser.cjs        # draw three defects with a photo, reload, element table, backup, sync, 3D
```

## Limits

- Only Beechwood has inspection sheets so far. Other bridges need their sheet set defined in the generator.
- A filled area is triangulated between its outline points on the member surface, so a large area drawn across a
  corner is approximated in 3D (the outline itself follows the surface).
- Defect numbers are assigned on each device. Two inspectors working offline on the same inspection can create the same
  number; renumber after syncing.
- The app records element-level data. NBI component ratings, the inspection report itself and agency-specific
  (INDOT) element or defect extensions are not part of this pilot.

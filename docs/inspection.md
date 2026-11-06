# Inspection app (pilot: Beechwood Road Bridge)

Inspectors draw defects on 2D inspection sheets, pick them from AASHTO element-inspection menus and add photos. Each
sketch is tied to the 3D model, so the defect appears on the real member in the 3D workspace. The app runs in a
browser (desktop, tablet with pen, phone) and keeps working offline.

- Open it from a bridge workspace with **Inspect** (top bar), or at `/inspect#beechwood`
  (`inspect.html#beechwood` on the static site).
- Back in the 3D workspace, **Defects** (or `D`) shows the defects saved on this device. Click a defect to see its
  card (element, condition state, quantity, location, measurements and photos) with a link back to the sheet.

## Recording a defect

1. **Start an inspection**: date, type (Routine, Initial, In-Depth, Damage, Special, Underwater, NSTM, Service),
   inspectors and notes. Defects always belong to an inspection.
2. **Choose a sheet** from the list (a picker above the sheet on tablets and phones).
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

**Elements** shows the AASHTO element table of the inspection: each element's total quantity split into CS 1–4,
with the defect rows under it, as in NBE inspection reports. CS 1 is the element total less the defect quantities.
**Download CSV** exports the table and the defect list; **Download backup** exports everything, photos included,
as one JSON file that **Settings → Import backup** restores.

## Inspection sheets

`scripts/build_inspection_sheets.py <bridge>` generates the sheets from `model.glb` (numpy and shapely,
`requirements-sheets.txt`). Beechwood has 10 A3 sheets with 48 true orthographic views:

| Sheet | Views |
|---|---|
| DK-1 Deck top surface | Spans A, B, C looking down (pavement markings shown) |
| DK-2 Deck underside | Spans A, B, C looking up: deck soffit and girder bottom flanges |
| GR-A, GR-B, GR-C Girders | East and west web faces of girders 1–4 of each span, each girder on its own |
| BT-2, BT-3 Bents | South and north faces: cap, columns, debris wall and the elastomeric bearings on that side |
| EB-1, EB-4 End bents | Face towards the span (end diaphragm, pile cap, wing returns) and both wing outside faces |
| RL-1 Barriers | Outside and traffic faces of both barriers, south and north halves |

Each view is a true view (not mirrored): U × V = −normal. Other parts in front of a member are subtracted, so a shaded
region is the surface an inspector actually sees from that side. Bent centre lines carry their stations.

`sheets.json` publishes, per view:

- `origin`, `u`, `v`, `normal` (glTF world axes, metres), `extent_m` and `placement` (fraction of the sheet, top-left);
- `parts` (inspectable meshes, in hit-test priority) and `regions` (their visible polygons in view coordinates);
- per part: AASHTO element, label, measuring axis and element quantity; and the element totals.

A sheet point `(u, v)` in a view (0–1 from the top-left, `v` down the sheet) is the world point

```
P = origin + u * extent_m[0] * U + v * extent_m[1] * V
```

and the defect lies on the first surface hit by a ray from `P` along `-normal`. The origin lies just in front of the
nearest surface of the view, so the ray always starts outside the model. The generator checks this on every build: it
samples points in every region, maps them with the published numbers and casts the ray into the model; every point must
land on its own part (666 points for Beechwood). `test_manager.py` checks that `sheets.json` names the current
`model.glb` (SHA-256), and the unit tests check that every region resolves to its part. Rebuild the sheets whenever the
model changes:

```sh
python -m pip install -r requirements-sheets.txt
python scripts/build_inspection_sheets.py beechwood   # about 2 minutes
```

## AASHTO elements, defects and condition states

Element and defect codes follow the AASHTO *Manual for Bridge Element Inspection*, 2nd edition (2019).

| Element | Unit | Beechwood total | Members |
|---|---|---|---|
| 12 Reinforced Concrete Deck | sq ft | 8,316 | deck (252 × 33 ft) |
| 109 Prestressed Concrete Open Girder/Beam | ft | 1,000 | 12 BT 36×49 girders |
| 205 Reinforced Concrete Column | each | 4 | bent columns |
| 210 Reinforced Concrete Pier Wall | ft | 35 | debris walls |
| 215 Reinforced Concrete Abutment | ft | 104 | end-bent pile caps, end diaphragms, wing returns |
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
5. Sign in under **Settings**. **Sync now** sends the outbox (inspections, then defects, then photos) and fetches
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

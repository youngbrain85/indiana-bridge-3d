# Fletcher Avenue and SR 10 models

Two whole-crossing exterior reconstructions were added on October 15, 2026. Both remain **More detail needed** (amber): all spans are represented, but fabrication details and several interfaces remain approximate. Neither model establishes present-day construction or structural condition.

| Crossing | Modeled state | Spans | Overall floor | Beam lines | Selectable objects |
|---|---|---:|---:|---:|---:|
| Fletcher Avenue / I-65–I-70 | Proposed 2026 deck replacement over retained historical steel and substructure | 2 × 44.8056 m | 91.00185 × 20.8788 m | 8 | 379 |
| SR 10 / I-65 | Retained 1998 widened structure, nominal 2019 overlay and proposed 2026 approaches | 11.8999 + 20.0406 + 20.0406 + 11.8999 m | 64.38265 × 15.332075 m | 9 | 312 |

Object counts include grouped connections and architectural panels; they are not fabrication-piece counts or quantity takeoffs. The collection now contains 16 crossing records, eleven 3D workspaces and five existing map-only partial models. Beechwood remains the only green model, within its stated exterior scope. Subsequent completion work added assumed-input FEM for both: Fletcher maps 44 components and SR 10 maps 74. See [collection completion](collection-completion.md).

## Source documents and page references

Each `drawings.pdf` is a **local review binder**, not an original issued plan set. Its `source_index.json` records the original URL, SHA-256, page count and binder offsets. All original files remain byte-for-byte in `sources/`. App component links use one-based **binder pages**, which can differ from printed sheet numbers.

| Fletcher source | Original pages | Binder pages |
|---|---:|---:|
| [2026 contract part 1, 9683635](https://erms12c.indot.in.gov/viewdocs/View12.aspx?Id=9683635) | 32 | 1–32 |
| [2026 Fletcher part 2, 9683636](https://erms12c.indot.in.gov/viewdocs/View12.aspx?Id=9683636) | 41 | 33–73 |
| [Historical Fletcher bundle, 9548534](https://erms12c.indot.in.gov/viewdocs/View12.aspx?Id=9548534) | 38 | 74–111 |
| [Specification revision 1, 9715471](https://erms12c.indot.in.gov/viewdocs/View12.aspx?Id=9715471) | 5 | 112–116 |
| [Specification revision 2, 9715512](https://erms12c.indot.in.gov/viewdocs/View12.aspx?Id=9715512) | 2 | 117–118 |
| [INDOT TX railing standard](https://secure.in.gov/dot/div/contracts/standards/drawings/sep21/700e/e700%20combined%20pdfs/E706-BRTX.pdf) | 4 | 119–122 |

Fletcher's proposed general plan is binder p.55 (part 2 p.23). The retained solid wall pier is p.98 (historical p.25), with framing and steel at pp.99–101. The historical identifier I-65-112-5723 is associated with current I65-110-05723B through the crossing name, two 147 ft spans, eight girder lines and matching skew. Virginia Avenue sheets in the contract are excluded from Fletcher geometry. Revision notices are retained for provenance; they do not supply additional modeled geometry.

| SR 10 source | Original pages | Binder pages |
|---|---:|---:|
| [Historical original, rehabilitation and overlay sets, 9492246](https://erms12c.indot.in.gov/viewdocs/View12.aspx?Id=9492246) | 48 | 1–48 |
| [2026 approach replacement, 9683528](https://erms12c.indot.in.gov/viewdocs/View12.aspx?Id=9683528) | 14 | 49–62 |
| [Specification/pay-item revision, 9713634](https://erms12c.indot.in.gov/viewdocs/View12.aspx?Id=9713634) | 12 | 63–74 |

SR 10's retained structure is documented at p.24, piers at pp.31–32, framing and steel at pp.33–34, and overlay at p.46. Proposed 2026 general and approach sheets are pp.59 and 61. The new cover uses suffix D while detail sheets use C; the registry retains both as `010-37-04888C / D`. The separate 114-page roadway/cross-section package is retained in the research collection and is not included in this bridge binder.

Map positions and state highway agency ownership/maintenance come from the dated [2025 NBI Indiana inventory](https://www.fhwa.dot.gov/BRIDGE/nbi/2025/delimited/IN25.txt): Fletcher 036380, SR 10 002910. GLBs use local metres and contain no surveyed world-coordinate transform.

## Geometry and remaining detail

**Fletcher Avenue:** both skewed spans, eight haunched plate-girder lines (16 span segments), 24 bearing assembly envelopes, a solid central wall pier, retained abutment/footing envelopes, proposed 8 in deck, two sidewalks, cross frames, lateral bracing, representative field splices and web fasteners, two approaches and four drain envelopes. North TX railing is 3 ft 6 in high; the modified south rail is 4 ft 6 in. Twenty architectural panels contain 360 actual window openings. Through-openings follow the TX standard; project sheets govern the modified rail height.

Remaining Fletcher details include the original multi-radius girder haunch, complete flange schedule and camber, exact bearing shoes/shims, original seat and top-of-steel elevations, wing splay, bracing gussets, complete bolt patterns, molded rail splays, TTX transitions, corner sidewalk extensions, drainage routing and slab penetrations. The proposed roadway profile is applied to the reconstruction, and support seats are derived to make the approximate geometry meet; this is not verification of retained field levels.

**SR 10:** four spans and nine nonuniformly spaced beam lines (36 span segments), slab plus a separate nominal 3/8 in overlay, channel diaphragms, splice/fastener envelopes, three pier lines, widened side walls, a central hammerhead with outer columns and collision walls, two integral ends, approaches, rails, transitions and drain envelopes. There are **27 pier bearings and no separate end bearings**: the end bents are integral. Side-pier widened wall profiles meet the retained central stems.

Remaining SR 10 details include exact rolled-section fillets and flange tables, seat steps/shims, original-versus-widened construction interfaces, bolt patterns, complete slope walls, terminals and drain routing. The 1998 65 m vertical curve governs the local reconstruction; later 215 ft and 213.25 ft descriptions are not silently treated as identical field measurements. Buried pile tips and internal reinforcement are excluded from both models.

## Reproduction and validation

With NumPy, trimesh, Shapely and mapbox-earcut installed:

```sh
python scripts/build_indiana_batch3.py
python test_manager.py
node test_indiana_batch3_browser.cjs
node test_browser.cjs
```

The browser tests require the app to be running and a Playwright Chromium installation. Alternatively, set `BROWSER_EXECUTABLE` to an installed Edge/Chromium binary. Model regeneration uses the bundled source indexes and PDFs, writes only these two bridge directories, and does not update the database automatically.

For an existing populated database, back it up and import **only these two registry entries**, with correctly resolved asset paths. The importer replaces each included bridge and its dependent records, so a full import would also replace unrelated local records. A fresh installation may import the complete registry normally.

`geometry_verification.json` records reopened GLB/manifest correspondence, finite coordinates, positive closed mesh volumes, support counts, deck/girder clearance and constructed bearing contact. These are geometry consistency checks, not proof of dimensional completeness or structural validity. Browser verification covers component selection, girder isolation, actual source-page images, coverage notes, model exports and assumed-input FEM availability. The existing application regression suite exercises all sixteen current workspaces and the five map-only routes. Existing bridge and FEM database records are compared against the pre-import backup.

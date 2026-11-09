# Indiana Bridges 3D

Photoreal Blender/Cycles reconstructions of three INDOT bridges, built from nothing but their NBI inspection reports
(structure inventory data, element quantities and the inspection photographs). Each bridge is generated
parametrically from `bridges/<folder>/bridge.json`, rendered with Cycles, exported to glTF for the web viewer, and
checked back against the report with the scripts in `tools/`.

| Bridge | NBI # | Structure | Folder |
|---|---|---|---|
| SR 28 over Little Wea Creek, Tippecanoe Co. | 007620 | 3-span RC slab on 9-pile bents, 20° skew, 71.5 ft, 1989 | `bridges/07620_sr28_little_wea` |
| I-70 EB over Bayliss State Ditch, Morgan Co. | 041750 | 3-span RC slab on 2-column frame bents, 15° skew, 82 ft, 1966 | `bridges/41750_i70_bayliss` |
| WB Sagamore Pkwy (US 52) over 9th St, CSX RR and ramp, Lafayette | 019027 | 6-span steel W36 multi-beam viaduct + concrete-beam approach span, 525 ft, 1971 | `bridges/19027_sagamore_pkwy` |

**Live:** [gallery](https://youngbrain85.github.io/indiana-bridges-3d/) · [3D viewer](https://youngbrain85.github.io/indiana-bridges-3d/viewer/)

## What is in each bridge folder

- `bridge.json` — every dimension the model uses, with the NBI item or report table it came from, plus `model_notes`
  (assumptions read off the photos).
- `report_text.txt` — the inspection report as text (the primary source for verification).
- `photos/` — the inspection photos with the report captions (`index.json`).
- `renders/` — Cycles renders (1920×1080) from the cameras defined in `blender/bridge_gen.py`.
- `model/bridge_<id>.glb` (full) and `bridge_<id>_lite.glb` (meshopt-compressed, used by the viewer).
- `verification/` — render-vs-photo pairs, the dimensional report and comparison sheets.

## How the models are made

`blender/bridge_gen.py` runs inside Blender (as the `bpy` Python module) and builds the whole scene procedurally:
terrain with the channel or the streets/railroad under the bridge, approach embankments that spill around the
wingwalls, the superstructure (slab + deep coping + parapet, or deck + W36 girders with cross-frames, stiffeners and
rocker bearings), the substructure types found in the reports (pile bents, 2-column frame bents, hammerhead piers,
pier walls with battered ends, spill-through and wall abutments with wingwalls), approach pavement with lane markings,
W-beam guardrail, riprap, water, trees and scattered grass, and a Nishita sky. Materials are PBR with procedurally
generated textures (`blender/gen_textures.py`). Everything is rebuilt from scratch in a few seconds:

```bash
pip install -r requirements.txt          # bpy 5.2.x (CPython 3.13), numpy, pillow, scipy
cd blender
python3 bridge_gen.py --build 07620      # -> blender/out/07620/bridge.blend
python3 bridge_gen.py --render 07620 preview        # quick 960x540 renders of every camera
python3 bridge_gen.py --render 07620 final          # 1920x1080, 64 samples + OpenImageDenoise
python3 bridge_gen.py --export 07620 [--lite]       # GLB for the viewer
```

## Verification (for people and for coding agents)

`AGENTS.md` describes how an agent such as OpenAI Codex should verify this repository, `CODEX_PROMPT.md` is a ready-to-paste prompt for it, `VERIFY.md` is the human checklist and `bridges/REVIEW_TEMPLATE.md` the report form.

```bash
bash tools/run_checks.sh                 # dimensional checks of the GLBs against bridge.json + render-vs-photo sheets
python3 tools/verify_model.py 07620 --blend          # same checks on the .blend (needs bpy)
```

`tools/verify_model.py` reads the GLB node names and bounding boxes (no Blender needed) and compares span stations,
deck and roadway widths, skew, pier/pile/column/girder counts, parapet height, water level and clearances with the
report values; it exits non-zero on any FAIL. `tools/compare_photos.py` lays each render next to the inspection photo
it should resemble, with the points to check written on the sheet.

## Viewer

`viewer/` is a three.js page that loads the compressed GLB of any of the three bridges, with the same camera presets
as the Cycles renders, the inspection photos alongside, and toggles for trees, grass, the twin structure and shadows.
It runs from GitHub Pages or any static server (`npx http-server .`).

## Limitations

The reports give structure type, span lengths, widths, skew, clearances, element counts and the channel profile; they
do not give drawings. Member sizes, pier proportions, the exact creek alignment, terrain, street/ramp geometry and
vegetation are plausible reconstructions from the photographs and are flagged as such in `bridge.json → model_notes`.
Deterioration is only suggested by the weathered textures.

## License

Code: MIT. The inspection reports and photographs belong to INDOT and are included for reference.

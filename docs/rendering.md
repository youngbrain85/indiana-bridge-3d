# Textured display models

Every bridge with a 3D workspace has two models. `model.glb` is the source of record. `model_render.glb` is a
copy for the 3D viewer, built with Blender, with surface textures and baked ambient occlusion (AO).

```sh
npm ci                                             # compression and geometry check use Node.js
python -m pip install -r requirements-render.txt   # bpy 5.2 needs Python 3.13
python scripts/blender_render_model.py beechwood   # about 1-2 minutes per bridge on 4 CPU cores
python import_data.py
```

The script bakes, exports, compresses and then checks the result against `model.glb`. It stops with an error if
any check fails. `npm run build` (and `npm run check:render`) repeats the check for every registered display
model.

## What changes and what does not

| | `model.glb` (source of record) | `model_render.glb` (display copy) |
|---|---|---|
| Mesh names and count | as drawn | identical |
| Triangles | as drawn | same triangles, positions stored as 16-bit integers per mesh (see below) |
| Vertex colours | part colours | removed; the viewer tints textures with the part colour from the register |
| Texture coordinates | none | `TEXCOORD_0` box projection in metres, `TEXCOORD_1` AO atlas |
| Materials | none | concrete, steel and plain, each with and without AO |
| Compression | none | `EXT_meshopt_compression` with `KHR_mesh_quantization` |
| Used by | register, FEM, exports, downloads | 3D viewer only |

**Position precision.** Each mesh's positions are quantized to 16 bits over its own bounding box. The step is the
mesh size divided by 65 535. The largest step in the collection is 2.4 mm, on the 158 m US 50 Tanners Creek deck, so
no corner moves by more than about 1.2 mm. Most parts are below 1 mm. The source model keeps full precision.

## Checks

- `scripts/check_render_models.mjs` decodes each display model and compares it with `model.glb`. It checks that the
  build stamp names the current source (SHA-256) and that mesh names match one-to-one. Each mesh must have the same
  number of triangles. Every source triangle needs a display triangle with all corners within that mesh's
  quantization step, and every display triangle needs a matching source triangle. A part moved by 1 cm fails.
- `test_manager.py` reads the GLB JSON with the standard library. It checks the importer's stamp and name
  validation, per-mesh triangle counts and world bounds (within the quantization step), the API's `render_url` and
  the served bytes.

## Build steps

1. Import the source GLB into Blender (`bpy` in background mode) and check its meshes against the manifest one-to-one.
2. Classify parts the same way as the viewer: metal layers and names get a steel texture, bearings, lane paint and
   joint filler stay plain, and unresolved-detail markers get no AO.
3. Generate tileable textures from seeded periodic (Fourier-domain) noise: concrete colour and normal map at
   1024 px (one repeat per 2.4 m), painted steel at 512 px (one repeat per 1.2 m). No downloaded images are used.
4. Write `TEXCOORD_0` as a world-space box projection, so the texture scale is the same on every part.
5. Unwrap all AO receivers into one 2048 px atlas (Smart UV Project, equal texel density, packed with an 8 px
   margin). The texel size is between 2.6 cm (SR 44 over Little Blue River) and 14 cm (US 50 Tanners Creek, the
   largest bridge); Beechwood has 7 cm.
6. Bake AO with Cycles (256 samples, 2.5 m rays) on one joined copy of the assembly, so contact shading between
   deck, girders, bearings, caps and columns comes from the real neighbours. The result is softened slightly and
   never goes below 35 %.
7. Export GLB with JPEG textures and a scene `extras.render_source` stamp holding the SHA-256 of the source GLB.
8. Compress with `scripts/compress_render_model.mjs` (gltf-transform `meshopt`, 16-bit positions, 14-bit AO
   coordinates), then run the geometry check.

Some parts occlude their neighbours but receive no baked AO:

- the deck and approach slabs, which model their saw grooves (about 2 cm pitch) as geometry. That relief is far
  below an AO texel and aliases into moiré;
- bolts, nuts and washers, which are smaller than a texel;
- the riprap stones of the approximate site layer: hundreds of loose rocks would take most of the atlas.

## Sizes

| Bridge | `model.glb` MiB | `model_render.glb` MiB |
|---|---|---|
| Beechwood Road Bridge | 7.0 | 5.6 |
| 21st Street over I-465 | 3.1 | 5.6 |
| US 421 over South Fork Wildcat Creek | 5.2 | 7.6 |
| US 52 over Mud Creek | 0.3 | 1.0 |
| SR 44 over Mud Creek | 2.6 | 4.7 |
| SR 8 over Yellow River | 1.0 | 2.5 |
| SR 1 over Wabash River | 0.3 | 1.1 |
| US 50 EB over Tanners Creek | 0.9 | 2.1 |
| Minnich Road NB / SB over I-469 | 1.5 | 3.2 |
| Fletcher Avenue over I-65 / I-70 | 2.1 | 4.5 |
| SR 10 over I-65 | 1.2 | 2.4 |
| US 35 over Deer Creek | 0.2 | 1.0 |
| US 224 over Eight Mile Creek | 0.1 | 0.8 |
| Virginia Avenue over I-65 NB / I-70 EB | 0.4 | 1.3 |
| SR 44 over Branch of Little Blue River | 0.1 | 0.7 |
| SR 1 over Six Mile Creek | 0.0 | 0.6 |
| **Total** | **26.0** | **44.8** |

Small bridges carry a fixed cost of about 0.5 MiB for the embedded textures. Without compression the display
models total 88.8 MiB. The static site was about 611 MiB with only Beechwood textured, and these models add about
31 MiB to it.

## In the app

- The registry entry's `model.render_glb` names the file. `import_data.py` imports it as a `render` asset only if
  its stamp matches the current `model.glb` and its mesh names match; otherwise it prints a warning and the
  viewer uses the plain model.
- `/api/bridges/<id>` then includes `model.render_url` (`/assets/<id>/render`, `assets/<id>/render.glb` in the static site).
- The viewer registers the meshopt decoder and expands quantized positions to float on load. It keeps the colour
  map, normal map and AO map from the display GLB on its per-part materials. Analysis colours, deck opacity,
  sectioning and selection work as before. On software WebGL the normal maps are skipped.
- Rebuild a display model whenever its `model.glb` changes; a stale one is ignored on import.

## Limits

The textures are generic concrete and paint finishes, not a record of the real surfaces: they show no staining,
repairs or condition. AO is baked for the default assembly; hiding parts in the viewer does not re-bake it.

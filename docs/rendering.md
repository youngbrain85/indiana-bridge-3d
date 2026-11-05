# Textured display models

`scripts/blender_render_model.py` turns a bridge's `model.glb` into `model_render.glb`, a copy for the 3D viewer
with surface textures and baked ambient occlusion (AO). Beechwood is the pilot.

```sh
python -m pip install -r requirements-render.txt   # bpy 5.2 needs Python 3.13
python scripts/blender_render_model.py beechwood   # about one minute on 4 CPU cores
python import_data.py
```

## What changes and what does not

| | `model.glb` (source of record) | `model_render.glb` (display copy) |
|---|---|---|
| Mesh names and count | as drawn | identical |
| Triangles (local positions) and node placement | as drawn | identical; only the winding of inward triangles is made consistent |
| Vertex colours | part colours | removed; the viewer tints textures with the part colour from the register |
| Texture coordinates | none | `TEXCOORD_0` box projection in metres, `TEXCOORD_1` AO atlas |
| Materials | none | concrete, steel and plain, each with and without AO |
| Used by | register, FEM, exports, downloads | 3D viewer only |

`test_manager.py` checks every display model against its source triangle by triangle, together with the node
transforms, the build stamp and the served bytes.

## Build steps

1. Import the source GLB into Blender (`bpy` in background mode) and check its meshes against the manifest one-to-one.
2. Classify parts the same way as the viewer: metal layers and names get a steel texture, bearings, lane paint and
   joint filler stay plain, and unresolved-detail markers get no AO.
3. Generate tileable textures from seeded periodic (Fourier-domain) noise: concrete colour and normal map at
   1024 px (one repeat per 2.4 m), painted steel at 512 px (one repeat per 1.2 m). No downloaded images are used.
4. Write `TEXCOORD_0` as a world-space box projection, so the texture scale is the same on every part.
5. Unwrap all AO receivers into one 2048 px atlas (Smart UV Project, equal texel density, packed with an 8 px
   margin; about 7 cm per texel on Beechwood).
6. Bake AO with Cycles (256 samples, 2.5 m rays) on one joined copy of the assembly, so contact shading between
   deck, girders, bearings, caps and columns comes from the real neighbours. The result is softened slightly and
   never goes below 35 %.
7. Export GLB with JPEG textures and a scene `extras.render_source` stamp holding the SHA-256 of the source GLB.

Some parts occlude their neighbours but receive no baked AO:

- the deck and approach slabs, which model their saw grooves (about 2 cm pitch) as geometry. That relief is far
  below an AO texel and aliases into moiré;
- bolts, nuts and washers, which are smaller than a texel;
- the riprap stones of the approximate site layer: hundreds of loose rocks would take most of the atlas.

## In the app

- The registry entry's `model.render_glb` names the file. `import_data.py` imports it as a `render` asset only if
  its stamp matches the current `model.glb` and its mesh names match; otherwise it prints a warning and the
  viewer uses the plain model.
- `/api/bridges/<id>` then includes `model.render_url` (`/assets/<id>/render`, `assets/<id>/render.glb` in the static site).
- The viewer keeps the textures, normal map and AO map from the display GLB on its per-part materials. Analysis
  colours, deck opacity, sectioning and selection work as before. On software WebGL the normal maps are skipped.
- Beechwood's display model is about 14 MiB, compared with 7 MiB for the plain model. The textures are shared,
  so most of the increase is the two texture-coordinate sets.

## Limits

The textures are generic concrete and paint finishes, not a record of the real surfaces: they show no staining,
repairs or condition. AO is baked for the default assembly; hiding parts in the viewer does not re-bake it.

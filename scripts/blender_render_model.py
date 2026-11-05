"""Build a textured display copy of a bridge model with Blender.

    python scripts/blender_render_model.py beechwood [--ao-size 2048] [--samples 256]

Needs the `bpy` module (pip install bpy; it matches one Python version, see
requirements-render.txt). The source model.glb stays the authoritative
geometry for the register, FEM and downloads. This script writes
model_render.glb next to it, which the 3D viewer shows instead when present:

* every mesh keeps its node name and its triangles (positions unchanged; only
  the winding of inward-facing triangles is made consistent);
* TEXCOORD_0 is a world-space box projection, so the tileable surface
  textures keep the same scale on every part;
* TEXCOORD_1 is one shared atlas holding ambient occlusion baked with Cycles
  from the whole assembly (deck over girders, bearings under girders, ...).
  Grooved riding surfaces, fasteners and loose riprap stones only occlude:
  they are finer than an atlas texel;
* the surface textures are generated here from seeded periodic noise, so the
  build is reproducible and needs no downloaded image assets.

The scene extras record the SHA-256 of the source GLB; the importer and the
tests reject a display model that no longer matches its source.
"""
import argparse
import hashlib
import json
import math
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]

# Same classification as the viewer's surfaceFor(): metal layers and names get the steel texture.
METAL = re.compile(r'steel|w\d+\s*[x×]|hp\s?\d+|c\d+\s*[x×]|bolt|nut\b|washer|weld|plate|angle|channel|stiffener|splice|'
                   r'gusset|lacing|chord|truss|casing|guardrail|railing|pipe rail|bracket|anchor', re.I)
METAL_LAYERS = {'steel', 'truss_chords', 'truss_web', 'gussets', 'lacing', 'bracing', 'fasteners', 'casing', 'repairs'}
PLAIN_LAYERS = {'bearings', 'road_surface', 'joints'}        # elastomer, paint and filler: AO only, no texture
NO_AO_LAYERS = {'detail_markers'}                            # annotation markers: neither occlude nor receive AO
TILE_M = {'concrete': 2.4, 'steel': 1.2}                     # metres covered by one texture repeat
# Saw grooves (about 2 cm pitch) are far below an AO texel; baked onto them they only alias, so grooved
# riding surfaces still occlude their neighbours but receive no baked AO.
GROOVED = re.compile(r'\bgroove', re.I)
# Bolts, nuts and washers are smaller than an AO texel, and the loose riprap stones of the (approximate)
# site layer are hundreds of separate rocks: either would take most of the atlas for no visible gain.
OCCLUDE_ONLY_LAYERS = {'fasteners', 'site'}


def surface_class(part):
    if part['layer'] in NO_AO_LAYERS:
        return 'marker'
    if part['layer'] in PLAIN_LAYERS:
        return 'plain'
    if part['layer'] in METAL_LAYERS or METAL.search(part.get('name', '')):
        return 'steel'
    return 'concrete'


def receives_ao(part):
    if part['layer'] in OCCLUDE_ONLY_LAYERS:
        return False
    text = ' '.join(str(part.get(k) or '') for k in ('name', 'note', 'basis'))
    return not (GROOVED.search(text) or any('groove' in k for k in part.get('dimensions', {})))


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# ---------------------------------------------------------------- textures
def periodic_noise(n, beta, rng, stretch=(1.0, 1.0)):
    """Fractal noise with a 1/f^beta spectrum. Built in the Fourier domain, so it tiles exactly."""
    fx = np.fft.fftfreq(n)[:, None] * stretch[0]
    fy = np.fft.fftfreq(n)[None, :] * stretch[1]
    f = np.sqrt(fx * fx + fy * fy)
    f[0, 0] = 1
    spectrum = (rng.normal(size=(n, n)) + 1j * rng.normal(size=(n, n))) / f ** beta
    spectrum[0, 0] = 0
    x = np.real(np.fft.ifft2(spectrum))
    return (x - x.mean()) / x.std()


def normal_map(height, strength):
    """Tangent-space normal map (OpenGL convention, as glTF expects) from a periodic height field."""
    dx = (np.roll(height, -1, 1) - np.roll(height, 1, 1)) * 0.5 * strength
    dy = (np.roll(height, -1, 0) - np.roll(height, 1, 0)) * 0.5 * strength
    n = np.dstack([-dx, dy, np.ones_like(height)])
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    return (n * 0.5 + 0.5).clip(0, 1)


def to_image(rgb):
    return Image.fromarray((np.asarray(rgb).clip(0, 1) * 255 + 0.5).astype(np.uint8))


def concrete_textures(n=1024, seed=7):
    rng = np.random.default_rng(seed)
    mottling = periodic_noise(n, 1.7, rng)
    fines = periodic_noise(n, 0.35, rng)
    streaks = periodic_noise(n, 1.3, rng, stretch=(1.0, 7.0))   # elongated along V, which is "up" on walls
    pores = np.clip(periodic_noise(n, 0.15, rng) - 3.0, 0, None)
    value = 0.90 + 0.035 * mottling + 0.025 * fines - 0.03 * np.clip(streaks, 0, None) - 0.22 * np.clip(pores * 3, 0, 1)
    tint = np.dstack([value * 1.0, value * 0.99, value * 0.965])
    height = 0.35 * fines + 0.15 * mottling - 3.0 * np.clip(pores * 3, 0, 1)
    return to_image(tint), to_image(normal_map(height, 0.45))


def steel_textures(n=512, seed=11):
    rng = np.random.default_rng(seed)
    cloud = periodic_noise(n, 1.8, rng)
    peel = periodic_noise(n, 0.9, rng)                            # orange-peel of a paint film
    value = 0.93 + 0.03 * cloud + 0.01 * peel
    return to_image(np.dstack([value, value, value * 0.99])), to_image(normal_map(0.6 * peel, 0.6))


# ---------------------------------------------------------------- Blender steps
def world_box_uvs(obj, tile):
    """Per-loop UVs from a box projection of world positions, scaled to metres per repeat."""
    mesh = obj.data
    m = np.array(obj.matrix_world)
    co = np.empty(len(mesh.vertices) * 3)
    mesh.vertices.foreach_get('co', co)
    co = co.reshape(-1, 3) @ m[:3, :3].T + m[:3, 3]
    loop_vertex = np.empty(len(mesh.loops), dtype=np.int64)
    mesh.loops.foreach_get('vertex_index', loop_vertex)
    starts = np.empty(len(mesh.polygons), dtype=np.int64)
    totals = np.empty(len(mesh.polygons), dtype=np.int64)
    mesh.polygons.foreach_get('loop_start', starts)
    mesh.polygons.foreach_get('loop_total', totals)
    normals = np.empty(len(mesh.polygons) * 3)
    mesh.polygons.foreach_get('normal', normals)
    normals = normals.reshape(-1, 3) @ np.linalg.inv(m[:3, :3])   # normals transform by the inverse transpose
    axis = np.abs(normals).argmax(axis=1)
    loop_axis = np.repeat(axis, totals)
    p = co[loop_vertex] / tile
    # Blender world is Z-up: walls map (horizontal, Z) so V runs upwards, horizontal faces map (X, Y).
    uv = np.where(loop_axis[:, None] == 0, p[:, [1, 2]], np.where(loop_axis[:, None] == 1, p[:, [0, 2]], p[:, [0, 1]]))
    layer = mesh.uv_layers.new(name='Tile')
    layer.data.foreach_set('uv', uv.astype(np.float32).ravel())


def material(bpy, name, images, ao_image):
    mat = bpy.data.materials.new(name)
    if bpy.app.version < (5, 0, 0):
        mat.use_nodes = True                                      # node trees are always on from Blender 5
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    bsdf = nodes.get('Principled BSDF')
    bsdf.inputs['Roughness'].default_value = 0.85
    tile_uv = nodes.new('ShaderNodeUVMap')
    tile_uv.uv_map = 'Tile'
    if images:
        base = nodes.new('ShaderNodeTexImage')
        base.image = images[0]
        links.new(tile_uv.outputs['UV'], base.inputs['Vector'])
        links.new(base.outputs['Color'], bsdf.inputs['Base Color'])
        normal = nodes.new('ShaderNodeTexImage')
        normal.image = images[1]
        normal.image.colorspace_settings.name = 'Non-Color'
        links.new(tile_uv.outputs['UV'], normal.inputs['Vector'])
        nmap = nodes.new('ShaderNodeNormalMap')
        nmap.uv_map = 'Tile'
        links.new(normal.outputs['Color'], nmap.inputs['Color'])
        links.new(nmap.outputs['Normal'], bsdf.inputs['Normal'])
    if ao_image is None:
        return mat
    ao_uv = nodes.new('ShaderNodeUVMap')
    ao_uv.uv_map = 'AO'
    ao = nodes.new('ShaderNodeTexImage')
    ao.image = ao_image
    ao.image.colorspace_settings.name = 'Non-Color'
    links.new(ao_uv.outputs['UV'], ao.inputs['Vector'])
    # The exporter turns this group's Occlusion input into occlusionTexture (texCoord 1).
    group = bpy.data.node_groups.get('glTF Material Output') or bpy.data.node_groups.new('glTF Material Output', 'ShaderNodeTree')
    if 'Occlusion' not in group.interface.items_tree:
        group.interface.new_socket('Occlusion', in_out='INPUT', socket_type='NodeSocketFloat')
    output = nodes.new('ShaderNodeGroup')
    output.node_tree = group
    separate = nodes.new('ShaderNodeSeparateColor')
    links.new(ao.outputs['Color'], separate.inputs['Color'])
    links.new(separate.outputs['Red'], output.inputs['Occlusion'])
    nodes.active = ao                                             # the bake writes into the active image node
    return mat


def build(bid, ao_size, samples, distance):
    import bpy
    import bmesh

    base = ROOT / 'data/bridges' / bid
    source, out = base / 'model.glb', base / 'model_render.glb'
    manifest = json.loads((base / 'model_manifest.json').read_text(encoding='utf-8'))
    parts = {p['id']: p for p in manifest['parts']}
    started = time.time()
    log = lambda *a: print(f'[{time.time() - started:6.1f}s]', *a, flush=True)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(source))
    objects = [o for o in bpy.data.objects if o.type == 'MESH']
    names = {o.name for o in objects}
    if names != set(parts) or len(objects) != len(parts):
        raise SystemExit(f'{bid}: Blender import does not match the manifest one-to-one')
    log(f'imported {len(objects)} meshes')

    scratch = Path(tempfile.mkdtemp(prefix='bridge-render-'))
    textures = {'concrete': concrete_textures(), 'steel': steel_textures()}
    images = {}
    for key, pair in textures.items():
        loaded = []
        for suffix, img in zip(('color', 'normal'), pair):
            path = scratch / f'{key}_{suffix}.png'
            img.save(path)
            image = bpy.data.images.load(str(path))
            image.name = f'{key}_{suffix}'
            loaded.append(image)
        images[key] = loaded
    ao_image = bpy.data.images.new('ambient_occlusion', ao_size, ao_size, alpha=False, float_buffer=False)
    ao_image.colorspace_settings.name = 'Non-Color'
    ao_image.generated_color = (1, 1, 1, 1)
    materials = {(key, ao): material(bpy, f'render_{key}' + ('' if ao else '_no_ao'), images.get(key), ao_image if ao else None)
                 for key in ('concrete', 'steel', 'plain') for ao in (True, False)}
    materials['marker', False] = material(bpy, 'render_marker', None, None)

    baked, occluders = [], []
    for obj in objects:
        kind = surface_class(parts[obj.name])
        ao = kind != 'marker' and receives_ao(parts[obj.name])
        mesh = obj.data
        # Consistent outward winding: an inward triangle would bake as fully occluded.
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(mesh)
        bm.free()
        for attr in list(mesh.color_attributes):
            mesh.color_attributes.remove(attr)
        mesh.materials.clear()
        mesh.materials.append(materials[kind, ao])
        world_box_uvs(obj, TILE_M.get(kind, 2.0))
        if not ao:
            if kind != 'marker':
                occluders.append(obj)
            continue
        mesh.uv_layers.new(name='AO')
        mesh.uv_layers.active = mesh.uv_layers['AO']
        mesh.uv_layers['AO'].active_render = True                 # Cycles bakes through the render UV map
        baked.append(obj)
    log(f'box-projected UVs; {len(baked)} meshes receive AO, {len(occluders)} only occlude')

    # One atlas for the whole assembly: unwrap, equalise texel density, then pack.
    bpy.ops.object.select_all(action='DESELECT')
    for obj in baked:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = baked[0]
    bpy.ops.object.mode_set(mode='EDIT')
    # Without a UV editor the UV selection must follow the mesh selection, or packing sees no islands.
    bpy.context.scene.tool_settings.use_uv_select_sync = True
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=0.0, area_weight=0.0, correct_aspect=True,
                             scale_to_bounds=False)
    bpy.ops.uv.average_islands_scale()
    # A fixed added margin: 'FRACTION' and large 'SCALED' margins shrink or scatter the islands so badly
    # that almost nothing bakes.
    bpy.ops.uv.pack_islands(rotate=True, margin_method='ADD', margin=8 / ao_size, shape_method='CONCAVE')
    bpy.ops.object.mode_set(mode='OBJECT')
    # Guard: one uniform scale keeps the packed layout inside [0, 1] (with a 2 px border)
    # without changing its proportions or overlaps.
    layouts = []
    for obj in baked:
        data = np.empty(len(obj.data.loops) * 2, dtype=np.float32)
        obj.data.uv_layers['AO'].data.foreach_get('uv', data)
        layouts.append(data.reshape(-1, 2))
    low = np.concatenate(layouts).min(0)
    extent = float((np.concatenate(layouts).max(0) - low).max())
    pad = 2 / ao_size
    for obj, uv in zip(baked, layouts):
        obj.data.uv_layers['AO'].data.foreach_set('uv', ((uv - low) / extent * (1 - 2 * pad) + pad).ravel())
    log(f'packed the AO atlas (layout scaled by 1/{extent:.2f})')

    scene = bpy.context.scene
    scene.world = bpy.data.worlds.new('bake')
    scene.world.light_settings.distance = distance
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = samples
    scene.render.bake.margin = 16                                  # fills the gaps, so mipmaps and JPEG blocks stay clean
    scene.render.bake.margin_type = 'EXTEND'
    # Cycles bakes selected objects one by one, each over the whole image. A single joined copy
    # (same AO UVs) bakes in one pass. The originals leave the scene meanwhile: they coincide with the
    # copy and would occlude it completely (render visibility alone does not take them out of the bake).
    bpy.ops.object.select_all(action='DESELECT')
    homes = {obj: list(obj.users_collection) for obj in objects}
    copies = []
    for obj in baked:
        copy = obj.copy()
        copy.data = obj.data.copy()
        scene.collection.objects.link(copy)
        copy.select_set(True)
        copies.append(copy)
    for obj in objects:
        if obj not in occluders:
            for collection in homes[obj]:
                collection.objects.unlink(obj)
    bpy.context.view_layer.objects.active = copies[0]
    bpy.ops.object.join()
    joined = bpy.context.view_layer.objects.active
    log('joined a bake copy')
    bpy.ops.object.bake(type='AO', use_clear=True, target='IMAGE_TEXTURES')
    bpy.data.objects.remove(joined, do_unlink=True)
    for obj in objects:
        if obj not in occluders:
            for collection in homes[obj]:
                collection.objects.link(obj)
    log(f'baked AO {ao_size}px x {samples} samples, distance {distance} m')

    # Soften the bake noise a little, keep contact shadows, and never darken below 35%.
    pixels = np.empty(ao_size * ao_size * 4, dtype=np.float32)
    ao_image.pixels.foreach_get(pixels)
    grey = pixels.reshape(ao_size, ao_size, 4)[:, :, 0]
    log(f'raw AO min {grey.min():.3f} mean {grey.mean():.3f} max {grey.max():.3f}')
    blurred = (grey * 4 + np.roll(grey, 1, 0) + np.roll(grey, -1, 0) + np.roll(grey, 1, 1) + np.roll(grey, -1, 1)) / 8
    grey = 0.35 + 0.65 * blurred.clip(0, 1) ** 0.8
    rgba = np.dstack([grey, grey, grey, np.ones_like(grey)]).astype(np.float32)
    ao_image.pixels.foreach_set(rgba.ravel())
    ao_image.filepath_raw = str(scratch / 'ambient_occlusion.png')
    ao_image.file_format = 'PNG'
    ao_image.save()

    for obj in objects:
        obj.data.uv_layers.active = obj.data.uv_layers['Tile']
        obj.data.uv_layers['Tile'].active_render = True
    scene['render_source'] = json.dumps({'source': 'model.glb', 'sha256': sha256(source), 'builder': Path(__file__).name,
                                         'ao_size': ao_size, 'samples': samples, 'ao_distance_m': distance})
    bpy.ops.export_scene.gltf(filepath=str(out), export_format='GLB', export_yup=True, export_texcoords=True,
                              export_normals=False, export_vertex_color='NONE', export_materials='EXPORT',
                              export_image_format='JPEG', export_jpeg_quality=88, export_extras=True, export_apply=False)
    log(f'wrote {out.relative_to(ROOT)} ({out.stat().st_size / 2**20:.1f} MiB)')
    return out


def compress_and_check(bid, out):
    """Meshopt compression (needs Node.js and `npm ci`), then the geometry check against model.glb."""
    for command in (['node', 'scripts/compress_render_model.mjs', str(out)], ['node', 'scripts/check_render_models.mjs', bid]):
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        print(result.stdout.strip(), flush=True)
        if result.returncode:
            sys.exit(f'{command[1]} failed:\n{result.stderr.strip()}')
    print(f'compressed {out.relative_to(ROOT)} ({out.stat().st_size / 2**20:.1f} MiB)', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('bridge')
    parser.add_argument('--ao-size', type=int, default=2048)
    parser.add_argument('--samples', type=int, default=256)
    parser.add_argument('--ao-distance', type=float, default=2.5, help='AO ray length in metres')
    parser.add_argument('--no-compress', action='store_true', help='keep the uncompressed export (debugging only)')
    args = parser.parse_args()
    try:
        import bpy  # noqa: F401
    except ImportError:
        sys.exit('This script needs the bpy module: pip install -r requirements-render.txt')
    out = build(args.bridge, args.ao_size, args.samples, args.ao_distance)
    if not args.no_compress:
        compress_and_check(args.bridge, out)


if __name__ == '__main__':
    main()

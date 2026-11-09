"""Shared Blender helpers (mesh construction, PBR materials, sky, render, export) for the bridge models.
Units: feet. Coordinates: X along the bridge (increasing station), Y to the left looking ahead, Z up."""
import os, math, random, time, json
import numpy as np
import bpy, bmesh
from mathutils import Vector, Matrix, Euler

HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(HERE, 'tex')

# ----------------------------------------------------------------------------- scene / collections
COLS = {}
def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    COLS.clear(); IMG.clear()
    sc = bpy.context.scene
    sc.unit_settings.system = 'IMPERIAL'; sc.unit_settings.scale_length = 0.3048; sc.unit_settings.length_unit = 'FEET'
    return sc

def coll(name):
    if name in COLS: return COLS[name]
    c = bpy.data.collections.new(name); bpy.context.scene.collection.children.link(c); COLS[name] = c; return c

# ----------------------------------------------------------------------------- mesh construction
def mesh_from_arrays(name, V, F, UV=None, col='Structure', mat=None, smooth=False, uvscale=None):
    me = bpy.data.meshes.new(name)
    V = np.asarray(V, dtype=np.float64)
    loops = np.fromiter((v for f in F for v in f), dtype=np.int32)
    sizes = np.fromiter((len(f) for f in F), dtype=np.int32)
    loop_start = np.concatenate([[0], np.cumsum(sizes)[:-1]]).astype(np.int32) if len(F) else np.zeros(0, np.int32)
    me.vertices.add(len(V)); me.vertices.foreach_set('co', V.ravel())
    me.loops.add(len(loops)); me.loops.foreach_set('vertex_index', loops)
    me.polygons.add(len(F)); me.polygons.foreach_set('loop_start', loop_start)
    me.update(calc_edges=True); me.validate(verbose=False)
    if UV is None and uvscale is not None: UV = box_uv(V, F, uvscale)
    if UV is not None:
        uv = me.uv_layers.new(name='UVMap'); uv.data.foreach_set('uv', np.asarray(UV, dtype=np.float32).ravel())
    if smooth: me.shade_smooth()
    ob = bpy.data.objects.new(name, me); coll(col).objects.link(ob)
    if mat is not None: me.materials.append(mat)
    return ob

def box_uv(V, F, scale):
    V = np.asarray(V); out = []
    for f in F:
        p = V[list(f)]
        n = np.cross(p[1] - p[0], p[2] - p[0]); a = int(np.argmax(np.abs(n)))
        i, j = {0: (1, 2), 1: (0, 2), 2: (0, 1)}[a]
        for q in p: out.append((q[i] * scale, q[j] * scale))
    return np.asarray(out, dtype=np.float32)

def prism(name, pts2d, bottom, top, col='Structure', mat=None, uvscale=0.1, xy_axes='xy'):
    """polygon (CCW) in a horizontal plane extruded from bottom to top (z)."""
    n = len(pts2d)
    V = [(x, y, bottom) for x, y in pts2d] + [(x, y, top) for x, y in pts2d]
    F = [list(range(n))[::-1], list(range(n, 2 * n))]
    for i in range(n):
        j = (i + 1) % n; F.append([i, j, n + j, n + i])
    return mesh_from_arrays(name, V, F, box_uv(V, F, uvscale), col, mat)

def extrude_profile(name, profile, path, mat, col='Structure', uvscale=0.15, close=True, smooth=False):
    """profile: list of (u, w) in the section plane (u = horizontal to the left, w = up); path: list of (x, y, z) points.
    The section is swept along the path (frames from path tangent, keeping w vertical). Returns the object."""
    P = [Vector(p) for p in path]
    V = []; n = len(profile)
    for i, p in enumerate(P):
        a = P[max(0, i - 1)]; b = P[min(len(P) - 1, i + 1)]
        t = (b - a); t.z = 0
        if t.length < 1e-6: t = Vector((1, 0, 0))
        t.normalize(); left = Vector((-t.y, t.x, 0))
        for (u, w) in profile: V.append((p + left * u + Vector((0, 0, w)))[:])
    F = []
    for i in range(len(P) - 1):
        for k in range(n if close else n - 1):
            k2 = (k + 1) % n
            a = i * n + k; b = i * n + k2; c = (i + 1) * n + k2; d = (i + 1) * n + k
            F.append([a, d, c, b])
    # caps
    if close:
        F.append(list(range(n))); F.append([(len(P) - 1) * n + k for k in range(n)][::-1])
    return mesh_from_arrays(name, V, F, box_uv(V, F, uvscale), col, mat, smooth=smooth)

def cylinder(name, a, b, r, mat, col='Structure', seg=24, uvscale=0.2, r2=None):
    a = Vector(a); b = Vector(b); d = b - a; L = d.length
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r2 if r2 is not None else r, depth=L)
    q = d.normalized().to_track_quat('Z', 'Y')
    bmesh.ops.transform(bm, matrix=Matrix.Translation((a + b) / 2) @ q.to_matrix().to_4x4(), verts=bm.verts)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    uv = me.uv_layers.new(name='UVMap')
    V = np.array([v.co for v in me.vertices]); F = [p.vertices[:] for p in me.polygons]
    # cylindrical uv for the sides
    uvs = []
    axis = (b - a).normalized()
    for f in F:
        for vi in f:
            p = Vector(V[vi]) - a; h = p.dot(axis); rad = p - axis * h
            ang = math.atan2(rad.y, rad.x) if abs(axis.z) > 0.5 else math.atan2(rad.z, rad.x if abs(axis.y) > 0.5 else rad.y)
            uvs.append((ang / (2 * math.pi) * 2 * math.pi * r * uvscale, h * uvscale))
    uv.data.foreach_set('uv', np.asarray(uvs, np.float32).ravel())
    me.shade_smooth()
    for p in me.polygons:
        if abs(p.normal.dot(axis)) > 0.9: p.use_smooth = False
    ob = bpy.data.objects.new(name, me); coll(col).objects.link(ob); me.materials.append(mat); return ob

def box(name, cx, cy, cz, sx, sy, sz, mat, col='Structure', rot_z=0.0, uvscale=0.15):
    c, s = math.cos(rot_z), math.sin(rot_z)
    corners = [(cx + dx * c - dy * s, cy + dx * s + dy * c) for dx, dy in ((-sx / 2, -sy / 2), (sx / 2, -sy / 2), (sx / 2, sy / 2), (-sx / 2, sy / 2))]
    return prism(name, corners, cz - sz / 2, cz + sz / 2, col, mat, uvscale)

def join(objs, name):
    if not objs: return None
    for o in bpy.context.view_layer.objects: o.select_set(False)
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    with bpy.context.temp_override(active_object=objs[0], selected_editable_objects=objs, selected_objects=objs):
        bpy.ops.object.join()
    objs[0].name = name; objs[0].data.name = name
    return objs[0]

# ----------------------------------------------------------------------------- materials
IMG = {}
def img(path, srgb=True):
    if path in IMG: return IMG[path]
    im = bpy.data.images.load(path, check_existing=True)
    im.colorspace_settings.name = 'sRGB' if srgb else 'Non-Color'
    IMG[path] = im; return im
def T(name): return os.path.join(TEX, name)

def pbr(name, albedo=None, normal=None, rough_img=None, color=(0.8, 0.8, 0.8, 1), rough=0.8, metal=0.0, nstrength=0.5,
        alpha_from_albedo=False, translucent=0.0, tint=None, uv_scale=1.0, dirt=0.0, streaks=0.0, coords='UV', spec_ior=1.45, instance_var=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; nodes = nt.nodes; links = nt.links
    for n in list(nodes): nodes.remove(n)
    out = nodes.new('ShaderNodeOutputMaterial'); out.location = (900, 0)
    bsdf = nodes.new('ShaderNodeBsdfPrincipled'); bsdf.location = (600, 0)
    bsdf.inputs['Roughness'].default_value = rough; bsdf.inputs['Metallic'].default_value = metal
    bsdf.inputs['Base Color'].default_value = color; bsdf.inputs['IOR'].default_value = spec_ior
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    tc = nodes.new('ShaderNodeTexCoord'); tc.location = (-900, 0)
    mapn = nodes.new('ShaderNodeMapping'); mapn.location = (-700, 0); mapn.inputs['Scale'].default_value = (uv_scale, uv_scale, uv_scale)
    links.new(tc.outputs['UV' if coords == 'UV' else 'Object'], mapn.inputs['Vector'])
    col_out = None
    if albedo:
        t = nodes.new('ShaderNodeTexImage'); t.image = img(albedo); t.location = (-400, 200); t.name = 'ALBEDO'; t.projection = 'BOX' if coords != 'UV' else 'FLAT'; t.projection_blend = 0.3
        links.new(mapn.outputs['Vector'], t.inputs['Vector']); col_out = t.outputs['Color']
        if alpha_from_albedo: links.new(t.outputs['Alpha'], bsdf.inputs['Alpha'])
    if tint is not None and col_out is not None:
        mx = nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.location = (-150, 200)
        mx.inputs['Factor'].default_value = 1.0; mx.inputs[7].default_value = tint
        links.new(col_out, mx.inputs[6]); col_out = mx.outputs[2]
    if dirt > 0 and col_out is not None:
        nz = nodes.new('ShaderNodeTexNoise'); nz.location = (-400, -600); nz.inputs['Scale'].default_value = 0.12; nz.inputs['Detail'].default_value = 6
        links.new(tc.outputs['Object'], nz.inputs['Vector'])
        ramp = nodes.new('ShaderNodeValToRGB'); ramp.location = (-100, -600)
        ramp.color_ramp.elements[0].position = 0.35; ramp.color_ramp.elements[0].color = (1 - 0.45 * dirt, 1 - 0.47 * dirt, 1 - 0.5 * dirt, 1)
        ramp.color_ramp.elements[1].position = 0.65; ramp.color_ramp.elements[1].color = (1, 1, 1, 1)
        links.new(nz.outputs['Fac'], ramp.inputs['Fac'])
        mx = nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.location = (200, 100); mx.inputs['Factor'].default_value = 1.0
        links.new(col_out, mx.inputs[6]); links.new(ramp.outputs['Color'], mx.inputs[7]); col_out = mx.outputs[2]
    if streaks > 0 and col_out is not None:
        # vertical water streaks from the top of the object (object z)
        sep = nodes.new('ShaderNodeSeparateXYZ'); sep.location = (-600, -900); links.new(tc.outputs['Object'], sep.inputs['Vector'])
        comb = nodes.new('ShaderNodeCombineXYZ'); comb.location = (-450, -900)
        links.new(sep.outputs['X'], comb.inputs['X']); links.new(sep.outputs['Y'], comb.inputs['Y'])
        mp = nodes.new('ShaderNodeMapping'); mp.location = (-300, -900); mp.inputs['Scale'].default_value = (0.6, 0.6, 0.02)
        links.new(comb.outputs['Vector'], mp.inputs['Vector'])
        nz2 = nodes.new('ShaderNodeTexNoise'); nz2.location = (-100, -900); nz2.inputs['Scale'].default_value = 3.0; nz2.inputs['Detail'].default_value = 4
        links.new(mp.outputs['Vector'], nz2.inputs['Vector'])
        ramp2 = nodes.new('ShaderNodeValToRGB'); ramp2.location = (100, -900)
        ramp2.color_ramp.elements[0].position = 0.5; ramp2.color_ramp.elements[0].color = (1 - 0.5 * streaks, 1 - 0.5 * streaks, 1 - 0.5 * streaks, 1)
        ramp2.color_ramp.elements[1].position = 0.62; ramp2.color_ramp.elements[1].color = (1, 1, 1, 1)
        links.new(nz2.outputs['Fac'], ramp2.inputs['Fac'])
        mx = nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.location = (350, 100); mx.inputs['Factor'].default_value = 1.0
        links.new(col_out, mx.inputs[6]); links.new(ramp2.outputs['Color'], mx.inputs[7]); col_out = mx.outputs[2]
    if instance_var > 0 and col_out is not None:
        oi = nodes.new('ShaderNodeObjectInfo'); oi.location = (0, 500)
        hs = nodes.new('ShaderNodeHueSaturation'); hs.location = (400, 400)
        mr = nodes.new('ShaderNodeMapRange'); mr.location = (200, 500); mr.inputs['To Min'].default_value = 0.5 - 0.06 * instance_var; mr.inputs['To Max'].default_value = 0.5 + 0.06 * instance_var
        links.new(oi.outputs['Random'], mr.inputs['Value']); links.new(mr.outputs['Result'], hs.inputs['Hue'])
        mv = nodes.new('ShaderNodeMapRange'); mv.location = (200, 650); mv.inputs['To Min'].default_value = 1.0 - 0.3 * instance_var; mv.inputs['To Max'].default_value = 1.0 + 0.25 * instance_var
        links.new(oi.outputs['Random'], mv.inputs['Value']); links.new(mv.outputs['Result'], hs.inputs['Value'])
        links.new(col_out, hs.inputs['Color']); col_out = hs.outputs['Color']
    if col_out is not None: links.new(col_out, bsdf.inputs['Base Color'])
    if rough_img:
        tr = nodes.new('ShaderNodeTexImage'); tr.image = img(rough_img, srgb=False); tr.location = (-400, -100); tr.projection = 'BOX' if coords != 'UV' else 'FLAT'
        links.new(mapn.outputs['Vector'], tr.inputs['Vector']); links.new(tr.outputs['Color'], bsdf.inputs['Roughness'])
    if normal:
        tn = nodes.new('ShaderNodeTexImage'); tn.image = img(normal, srgb=False); tn.location = (-400, -400); tn.projection = 'BOX' if coords != 'UV' else 'FLAT'
        links.new(mapn.outputs['Vector'], tn.inputs['Vector'])
        nm = nodes.new('ShaderNodeNormalMap'); nm.location = (200, -400); nm.inputs['Strength'].default_value = nstrength
        if coords != 'UV': nm.space = 'OBJECT'
        links.new(tn.outputs['Color'], nm.inputs['Color']); links.new(nm.outputs['Normal'], bsdf.inputs['Normal'])
    if translucent > 0:
        tr = nodes.new('ShaderNodeBsdfTranslucent'); tr.location = (600, -300)
        if col_out is not None: links.new(col_out, tr.inputs['Color'])
        mix = nodes.new('ShaderNodeMixShader'); mix.location = (800, 0); mix.inputs['Fac'].default_value = translucent
        links.new(bsdf.outputs['BSDF'], mix.inputs[1]); links.new(tr.outputs['BSDF'], mix.inputs[2])
        if alpha_from_albedo:
            tp = nodes.new('ShaderNodeBsdfTransparent'); tp.location = (800, -200)
            mix2 = nodes.new('ShaderNodeMixShader'); mix2.location = (950, -100)
            links.new(nodes['ALBEDO'].outputs['Alpha'], mix2.inputs['Fac'])
            links.new(tp.outputs['BSDF'], mix2.inputs[1]); links.new(mix.outputs['Shader'], mix2.inputs[2])
            links.new(mix2.outputs['Shader'], out.inputs['Surface'])
            for l in list(bsdf.inputs['Alpha'].links): nt.links.remove(l)
        else:
            links.new(mix.outputs['Shader'], out.inputs['Surface'])
    m['export_albedo'] = albedo or ''; m['export_normal'] = normal or ''; m['export_rough'] = rough
    m['export_tint'] = list(tint) if tint is not None else [1.0, 1.0, 1.0, 1.0]; m['export_uvscale'] = uv_scale; m['export_coords'] = coords
    return m

def standard_materials():
    M = {}
    M['concrete'] = pbr('Concrete', T('concrete_weathered.jpg'), T('concrete_weathered_n.jpg'), rough=0.85, nstrength=0.6, dirt=0.6, streaks=0.5, coords='OBJ', uv_scale=0.08)
    M['concrete_new'] = pbr('ConcreteSmooth', T('concrete.jpg'), T('concrete_n.jpg'), T('concrete_r.jpg'), nstrength=0.4, dirt=0.3, coords='OBJ', uv_scale=0.06)
    M['deck'] = pbr('DeckConcrete', T('deck_concrete.jpg'), T('deck_concrete_n.jpg'), rough=0.9, nstrength=0.5, tint=(0.92, 0.9, 0.86, 1))
    M['asphalt'] = pbr('Asphalt', T('asphalt.jpg'), rough=0.92, tint=(0.85, 0.85, 0.85, 1), coords='OBJ', uv_scale=0.08)
    M['steel_green'] = pbr('SteelGreenPaint', T('steel_green.jpg'), T('steel_green_n.jpg'), T('steel_green_r.jpg'), metal=0.15, nstrength=0.5, coords='OBJ', uv_scale=0.12, instance_var=0.5)
    M['steel_black'] = pbr('SteelBlackCoated', color=(0.03, 0.03, 0.035, 1), rough=0.55, metal=0.3, dirt=0.4, streaks=0.3, coords='OBJ')
    M['galv'] = pbr('Galvanized', T('galvanized.jpg'), rough=0.42, metal=0.9, coords='OBJ', uv_scale=0.3)
    M['galv_dark'] = pbr('GalvanizedDark', color=(0.3, 0.31, 0.32, 1), rough=0.55, metal=0.85)
    M['ballast'] = pbr('Ballast', T('ballast.jpg'), T('ballast_n.jpg'), rough=0.95, nstrength=0.9, coords='OBJ', uv_scale=0.12)
    M['riprap'] = pbr('Riprap', T('limestone.jpg'), T('limestone_n.jpg'), rough=0.92, nstrength=1.0, dirt=0.6, coords='OBJ', uv_scale=0.22, tint=(0.78, 0.77, 0.72, 1))
    M['rail'] = pbr('RailSteel', color=(0.45, 0.42, 0.4, 1), rough=0.35, metal=0.9)
    M['tie'] = pbr('Tie', T('wood.jpg'), rough=0.9, tint=(0.35, 0.3, 0.26, 1), coords='OBJ', uv_scale=0.3)
    M['wood_post'] = pbr('WoodPost', T('wood.jpg'), T('wood_n.jpg'), rough=0.85, nstrength=0.6, tint=(0.6, 0.52, 0.42, 1), coords='OBJ', uv_scale=0.4)
    M['bark'] = pbr('Bark', T('bark.jpg'), T('bark_n.jpg'), rough=0.95, nstrength=1.0)
    for i in range(3):
        M[f'leaf{i}'] = pbr(f'Leaves{i}', T(f'leafcard{i}.png'), rough=0.55, alpha_from_albedo=True, translucent=0.3, spec_ior=1.4, instance_var=1.0)
    M['grass_clump'] = pbr('GrassClump', T('grassclump.png'), rough=0.8, alpha_from_albedo=True, translucent=0.1, tint=(0.55, 0.72, 0.42, 1))
    M['grass'] = pbr('Grass', T('grass_detail.jpg'), T('grass_n.jpg'), rough=0.95, nstrength=0.5, coords='OBJ', uv_scale=0.05, tint=(0.62, 0.72, 0.42, 1), dirt=0.5)
    M['dry_grass'] = pbr('DryGrass', T('grass_detail.jpg'), T('grass_n.jpg'), rough=0.95, nstrength=0.5, coords='OBJ', uv_scale=0.05, tint=(0.8, 0.68, 0.42, 1), dirt=0.5)
    M['mud'] = pbr('Mud', color=(0.22, 0.18, 0.13, 1), rough=0.8)
    M['sign_green'] = pbr('SignGreen', color=(0.0, 0.25, 0.1, 1), rough=0.4)
    # water
    w = bpy.data.materials.new('Water'); w.use_nodes = True
    nt = w.node_tree; nodes = nt.nodes; links = nt.links
    for n in list(nodes): nodes.remove(n)
    out = nodes.new('ShaderNodeOutputMaterial'); out.location = (800, 0)
    bsdf = nodes.new('ShaderNodeBsdfPrincipled'); bsdf.location = (400, 0)
    bsdf.inputs['Base Color'].default_value = (0.05, 0.06, 0.045, 1); bsdf.inputs['Roughness'].default_value = 0.1; bsdf.inputs['IOR'].default_value = 1.33
    tc = nodes.new('ShaderNodeTexCoord'); tc.location = (-800, 0)
    n1 = nodes.new('ShaderNodeTexNoise'); n1.location = (-500, -200); n1.inputs['Scale'].default_value = 0.4; n1.inputs['Detail'].default_value = 8
    links.new(tc.outputs['Object'], n1.inputs['Vector'])
    bump = nodes.new('ShaderNodeBump'); bump.location = (0, -200); bump.inputs['Strength'].default_value = 0.06; bump.inputs['Distance'].default_value = 0.3
    links.new(n1.outputs['Fac'], bump.inputs['Height']); links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    w['export_albedo'] = ''; w['export_rough'] = 0.1
    M['water'] = w
    return M

def lane_marking_material(name, width_ft, roadway_ft, pattern, base_mat_tex, tile_len=40.0, tint=(0.92, 0.9, 0.86, 1), n_res=(2048, 1024)):
    """Deck/pavement material: tined concrete (or asphalt) + painted lines. UV: u = x / tile_len, v = (y + width/2) / width.
    pattern: 'oneway2' (white edge lines, white skip centre), 'twoway2' (white edges, double yellow centre), 'interstate2' (white right edge, yellow left edge, white skip)"""
    from PIL import Image, ImageDraw
    W, H = n_res
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    pxft_y = H / width_ft; pxft_x = W / tile_len
    def hline(y_ft, col, w_in=4.0, dash=None):
        y = int((y_ft + width_ft / 2) * pxft_y); h = max(2, int(w_in / 12 * pxft_y))
        if dash is None: d.rectangle([0, y - h // 2, W, y + h // 2], fill=col)
        else:
            on, off = dash; x = 0
            while x < W: d.rectangle([int(x * pxft_x), y - h // 2, int((x + on) * pxft_x), y + h // 2], fill=col); x += on + off
    white = (235, 235, 230, 255); yellow = (225, 180, 40, 255)
    half = roadway_ft / 2
    if pattern == 'oneway2':
        hline(-half + 1.0, white, 6); hline(half - 1.0, white, 6); hline(0, white, 4, (10, 30))
    elif pattern == 'twoway2':
        hline(-half + 0.8, white, 4); hline(half - 0.8, white, 4); hline(-0.3, yellow, 4); hline(0.3, yellow, 4)
    elif pattern == 'interstate2':
        hline(-half + 1.0, white, 6); hline(half - 1.0, yellow, 6); hline(0, white, 4, (10, 30))
    path = os.path.join(HERE, 'out', f'markings_{name}.png'); os.makedirs(os.path.dirname(path), exist_ok=True); im.save(path)
    m = pbr(name, base_mat_tex, T('deck_concrete_n.jpg') if 'deck' in base_mat_tex else None, rough=0.9, nstrength=0.5, tint=tint)
    nt = m.node_tree; nodes = nt.nodes; links = nt.links
    bsdf = next(n for n in nodes if n.type == 'BSDF_PRINCIPLED'); tc = next(n for n in nodes if n.type == 'TEX_COORD')
    # base texture tiles: scale uv so that 1 tile = 12 ft along, 12 ft across (u is in units of tile_len, v in units of width)
    mapn = next(n for n in nodes if n.type == 'MAPPING'); mapn.inputs['Scale'].default_value = (tile_len / 12.0, width_ft / 12.0, 1)
    mk = nodes.new('ShaderNodeTexImage'); mk.image = img(path); mk.location = (-150, 500); mk.name = 'MARKINGS'; mk.extension = 'REPEAT'
    links.new(tc.outputs['UV'], mk.inputs['Vector'])
    base_link = bsdf.inputs['Base Color'].links[0]; src = base_link.from_socket
    mx = nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.location = (400, 300)
    links.new(mk.outputs['Alpha'], mx.inputs['Factor']); links.new(src, mx.inputs[6]); links.new(mk.outputs['Color'], mx.inputs[7])
    # worn paint: multiply alpha by noise
    nz = nodes.new('ShaderNodeTexNoise'); nz.location = (-150, 800); nz.inputs['Scale'].default_value = 0.5; nz.inputs['Detail'].default_value = 5
    links.new(tc.outputs['Object'], nz.inputs['Vector'])
    mr = nodes.new('ShaderNodeMapRange'); mr.location = (50, 800); mr.inputs['From Min'].default_value = 0.3; mr.inputs['From Max'].default_value = 0.7; mr.inputs['To Min'].default_value = 0.55; mr.inputs['To Max'].default_value = 1.0
    links.new(nz.outputs['Fac'], mr.inputs['Value'])
    mul = nodes.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'; mul.location = (250, 600)
    links.new(mk.outputs['Alpha'], mul.inputs[0]); links.new(mr.outputs['Result'], mul.inputs[1]); links.new(mul.outputs[0], mx.inputs['Factor'])
    nt.links.remove(base_link); links.new(mx.outputs[2], bsdf.inputs['Base Color'])
    m['markings'] = path
    return m

# ----------------------------------------------------------------------------- vegetation
def make_tree_variant(i, M, H=40.0, ncards=300):
    rng = random.Random(500 + i)
    c = bpy.data.collections.new(f'Tree{i}'); bpy.context.scene.collection.children.link(c)
    bm = bmesh.new()
    def seg(a, b, r0, r1, n=8):
        a = Vector(a); b = Vector(b); d = b - a
        if d.length < 0.1: return
        res = bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r0, radius2=r1, depth=d.length)
        q = d.normalized().to_track_quat('Z', 'Y')
        bmesh.ops.transform(bm, matrix=Matrix.Translation((a + b) / 2) @ q.to_matrix().to_4x4(), verts=res['verts'])
    trunk_h = H * rng.uniform(0.38, 0.5); r0 = H * 0.022
    seg((0, 0, -1), (rng.uniform(-0.5, 0.5), rng.uniform(-0.5, 0.5), trunk_h), r0, r0 * 0.55, 10)
    tips = []; nb = rng.randint(5, 7)
    for k in range(nb):
        a = (k / nb) * 2 * math.pi + rng.uniform(-0.4, 0.4); el = rng.uniform(0.45, 1.05); L = H * rng.uniform(0.28, 0.42)
        start = Vector((0, 0, trunk_h * rng.uniform(0.75, 1.0)))
        end = start + Vector((math.cos(a) * math.cos(el) * L, math.sin(a) * math.cos(el) * L, math.sin(el) * L))
        seg(start, end, r0 * 0.5, r0 * 0.18); tips.append(end)
        for m in range(rng.randint(2, 3)):
            a2 = a + rng.uniform(-1.0, 1.0); el2 = rng.uniform(0.2, 1.1); L2 = L * rng.uniform(0.4, 0.7)
            s2 = start + (end - start) * rng.uniform(0.5, 0.95)
            e2 = s2 + Vector((math.cos(a2) * math.cos(el2) * L2, math.sin(a2) * math.cos(el2) * L2, math.sin(el2) * L2))
            seg(s2, e2, r0 * 0.2, r0 * 0.07, 6); tips.append(e2)
            if ncards < 100:   # bare / sparse crown: add third-order twigs
                for t in range(3):
                    a3 = a2 + rng.uniform(-1.2, 1.2); el3 = rng.uniform(0.1, 1.2); L3 = L2 * rng.uniform(0.45, 0.8)
                    s3 = s2 + (e2 - s2) * rng.uniform(0.4, 1.0)
                    e3 = s3 + Vector((math.cos(a3) * math.cos(el3) * L3, math.sin(a3) * math.cos(el3) * L3, math.sin(el3) * L3))
                    seg(s3, e3, r0 * 0.07, r0 * 0.02, 4); tips.append(e3)
    me = bpy.data.meshes.new(f'TreeWood{i}'); bm.to_mesh(me); bm.free()
    uv = me.uv_layers.new(name='UVMap'); Vv = np.array([v.co for v in me.vertices]); Fv = [p.vertices[:] for p in me.polygons]
    uvs = [(math.atan2(Vv[vi][1], Vv[vi][0]) / (2 * math.pi) * 3.0, Vv[vi][2] * 0.08) for f in Fv for vi in f]
    uv.data.foreach_set('uv', np.asarray(uvs, np.float32).ravel()); me.shade_smooth(); me.materials.append(M['bark'])
    ob = bpy.data.objects.new(f'TreeWood{i}', me); c.objects.link(ob)
    V = []; F = []; UVl = []
    cz = trunk_h + H * 0.22; rx = H * 0.44; rz = H * 0.36; card = H * 0.125; ccen = Vector((0, 0, cz))
    for k in range(ncards):
        if k < len(tips) * 6:
            tip = tips[k % len(tips)]; ctr = tip + Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-0.5, 1))) * H * 0.07
        else:
            u = rng.uniform(0, 2 * math.pi); v = math.acos(rng.uniform(-1, 1)); rr = rng.uniform(0.55, 1.0)
            ctr = Vector((rx * rr * math.sin(v) * math.cos(u), rx * rr * math.sin(v) * math.sin(u), cz + rz * rr * math.cos(v)))
        if ctr.z < trunk_h * 0.55: continue
        nrm = (ctr - ccen); nrm.z *= 0.6
        if nrm.length < 1e-3: nrm = Vector((1, 0, 0))
        nrm.normalize()
        Mr = nrm.to_track_quat('Y', 'Z').to_matrix() @ Euler((rng.uniform(-0.6, 0.6), rng.uniform(0, 2 * math.pi), rng.uniform(-0.6, 0.6))).to_matrix()
        base = len(V)
        for (dx, dz) in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            p = Mr @ Vector((dx * card / 2, 0, dz * card / 2)); V.append((ctr + p)[:])
        F.append([base, base + 1, base + 2, base + 3]); UVl += [(0, 0), (1, 0), (1, 1), (0, 1)]
    if F:
        lo = mesh_from_arrays(f'TreeLeaves{i}', V, F, UVl, 'Vegetation', M[f'leaf{i}'])
        coll('Vegetation').objects.unlink(lo); c.objects.link(lo)
    bpy.context.scene.collection.children.unlink(c)
    c['base_height'] = H
    return c

def place_trees(variants, positions, zfun, rng, col='Trees'):
    """positions: list of (x, y, height, rot). zfun(x, y) -> ground z."""
    vc = coll(col)
    for k, (x, y, h, rot) in enumerate(positions):
        c = variants[k % 3]
        ob = bpy.data.objects.new(f'Tree_{k}', None); ob.instance_type = 'COLLECTION'; ob.instance_collection = c
        s = h / c['base_height']
        ob.location = (x, y, zfun(x, y) - 0.6); ob.rotation_euler = (0, 0, rot); ob.scale = (s * rng.uniform(0.85, 1.15), s * rng.uniform(0.85, 1.15), s)
        ob.empty_display_size = 1; vc.objects.link(ob)

def grass_clump_collection(M):
    c = bpy.data.collections.new('GrassClumps'); bpy.context.scene.collection.children.link(c)
    for i in range(3):
        rng = random.Random(700 + i); V = []; F = []; UV = []
        w = 2.4 * rng.uniform(0.8, 1.2); h = 1.5 * rng.uniform(0.8, 1.25)
        for k in range(3):
            a = k * math.pi / 3 + rng.uniform(-0.2, 0.2); cx, cy = math.cos(a), math.sin(a); base = len(V)
            V += [(-cx * w / 2, -cy * w / 2, -0.1), (cx * w / 2, cy * w / 2, -0.1), (cx * w / 2, cy * w / 2, h), (-cx * w / 2, -cy * w / 2, h)]
            F.append([base, base + 1, base + 2, base + 3]); UV += [(0, 0), (1, 0), (1, 1), (0, 1)]
        ob = mesh_from_arrays(f'GrassClump{i}', V, F, UV, 'Vegetation', M['grass_clump'])
        coll('Vegetation').objects.unlink(ob); c.objects.link(ob)
    bpy.context.scene.collection.children.unlink(c)
    return c

def scatter_grass(terrain, clumps, count, weight_fn, size=0.55):
    """hair particle system on `terrain` with a density vertex group from weight_fn(x, y, z) -> 0..1"""
    me = terrain.data; vg = terrain.vertex_groups.new(name='grass')
    co = np.empty(len(me.vertices) * 3); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
    for i, (x, y, z) in enumerate(co):
        w = weight_fn(x, y, z)
        if w > 0.02: vg.add([i], float(w), 'REPLACE')
    terrain.modifiers.new('Grass', 'PARTICLE_SYSTEM'); ps = terrain.particle_systems[-1]; ps.vertex_group_density = 'grass'
    st = ps.settings; st.type = 'HAIR'; st.count = count; st.hair_length = 1.0; st.use_advanced_hair = True
    st.render_type = 'COLLECTION'; st.instance_collection = clumps; st.use_collection_pick_random = True
    st.particle_size = size; st.size_random = 0.4; st.use_rotations = True; st.rotation_mode = 'NOR'; st.phase_factor_random = 2.0; st.rotation_factor_random = 0.08
    st.use_rotation_instance = True; st.emit_from = 'FACE'; st.distribution = 'RAND'; st.use_emit_random = True; st.display_percentage = 2

# ----------------------------------------------------------------------------- world, cameras, render
def setup_world(sc, sun_elev=38, sun_rot=215, exposure=-3.4):
    w = bpy.data.worlds.new('Sky'); sc.world = w; w.use_nodes = True
    nt = w.node_tree; nodes = nt.nodes
    for n in list(nodes): nodes.remove(n)
    out = nodes.new('ShaderNodeOutputWorld'); bg = nodes.new('ShaderNodeBackground'); sky = nodes.new('ShaderNodeTexSky')
    sky.sky_type = 'MULTIPLE_SCATTERING'; sky.sun_elevation = math.radians(sun_elev); sky.sun_rotation = math.radians(sun_rot)
    sky.sun_size = math.radians(0.6); sky.sun_intensity = 1.0; sky.altitude = 200; sky.air_density = 1.0; sky.aerosol_density = 2.2; sky.ozone_density = 1.5; sky.sun_disc = True
    nt.links.new(sky.outputs['Color'], bg.inputs['Color']); nt.links.new(bg.outputs['Background'], out.inputs['Surface'])
    sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'
    sc.cycles.use_denoising = True; sc.cycles.denoiser = 'OPENIMAGEDENOISE'; sc.cycles.denoising_prefilter = 'ACCURATE'; sc.cycles.denoising_use_gpu = False
    sc.cycles.use_adaptive_sampling = True; sc.cycles.adaptive_threshold = 0.02
    sc.cycles.max_bounces = 8; sc.cycles.diffuse_bounces = 3; sc.cycles.glossy_bounces = 3; sc.cycles.transparent_max_bounces = 48
    sc.cycles.caustics_reflective = False; sc.cycles.caustics_refractive = False; sc.cycles.sample_clamp_indirect = 8.0; sc.cycles.blur_glossy = 1.0
    sc.render.use_persistent_data = True
    sc.view_settings.view_transform = 'AgX'; sc.view_settings.exposure = exposure
    sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_depth = '8'
    sc.render.resolution_x = 1920; sc.render.resolution_y = 1080; sc.cycles.samples = 96

def add_camera(sc, name, pos, target, lens=28, zfun=None):
    cd = bpy.data.cameras.new('Cam_' + name); cd.lens = lens; cd.sensor_width = 36; cd.clip_end = 20000
    ob = bpy.data.objects.new('Cam_' + name, cd); coll('Cameras').objects.link(ob)
    p = Vector(pos); t = Vector(target)
    if zfun is not None: p.z = max(p.z, zfun(p.x, p.y) + 5.5)
    ob.location = p; ob.rotation_euler = (t - p).to_track_quat('-Z', 'Y').to_euler()
    return ob

def render_views(blend, names, quality, outdir):
    bpy.ops.wm.open_mainfile(filepath=blend)
    sc = bpy.context.scene
    if quality == 'preview': sc.render.resolution_x, sc.render.resolution_y, sc.cycles.samples = 960, 540, 24
    elif quality == 'medium': sc.render.resolution_x, sc.render.resolution_y, sc.cycles.samples = 1280, 720, 48
    else: sc.render.resolution_x, sc.render.resolution_y, sc.cycles.samples = 1920, 1080, 64
    os.makedirs(outdir, exist_ok=True)
    for name in names:
        cam = bpy.data.objects.get('Cam_' + name)
        if cam is None: print('no camera', name); continue
        if os.path.exists(os.path.join(outdir, name + '.png')) and os.environ.get('RENDER_SKIP_EXISTING'): print('skip', name); continue
        sc.camera = cam; sc.render.filepath = os.path.join(outdir, name + '.png')
        t = time.time(); bpy.ops.render.render(write_still=True); print(f'{name}: {time.time() - t:.0f}s', flush=True)

def _tinted_image(im, tint, cache):
    """copy of image `im` multiplied by tint (rgb) — the glTF exporter cannot export the tint/dirt node chains"""
    key = (im.name, tuple(round(t, 3) for t in tint[:3]))
    if key in cache: return cache[key]
    px = np.empty(im.size[0] * im.size[1] * 4, np.float32); im.pixels.foreach_get(px); px = px.reshape(-1, 4)
    px[:, :3] = np.clip(px[:, :3] * np.array(tint[:3], np.float32), 0, 1)
    out = bpy.data.images.new(im.name.rsplit('.', 1)[0] + '_tinted', im.size[0], im.size[1], alpha=True)
    out.colorspace_settings.name = im.colorspace_settings.name; out.pixels.foreach_set(px.ravel()); out.pack()
    cache[key] = out; return out

def export_glb(blend, path, lite=False):
    """Export the scene to GLB. Materials are simplified to what glTF can carry: albedo (tint baked in) + tangent
    normal map on the mesh UVs, constant roughness/metallic. Box-projected (object-space) textures are switched to
    the meshes' box UVs."""
    bpy.ops.wm.open_mainfile(filepath=blend)
    cache = {}
    for m in bpy.data.materials:
        if not m.use_nodes: continue
        nt = m.node_tree; bsdf = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
        if bsdf is None: continue
        out = next((n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL'), None); tc = next((n for n in nt.nodes if n.type == 'TEX_COORD'), None)
        alb = next((n for n in nt.nodes if n.type == 'TEX_IMAGE' and n.name == 'ALBEDO'), None)
        mk = next((n for n in nt.nodes if n.type == 'TEX_IMAGE' and n.name == 'MARKINGS'), None)
        for l in list(bsdf.inputs['Base Color'].links): nt.links.remove(l)
        if mk is not None:
            nt.links.new(mk.outputs['Color'], bsdf.inputs['Base Color'])
        elif alb is not None:
            tint = list(m.get('export_tint', [1, 1, 1, 1]))
            if any(abs(t - 1) > 0.01 for t in tint[:3]) and alb.image is not None: alb.image = _tinted_image(alb.image, tint, cache)
            nt.links.new(alb.outputs['Color'], bsdf.inputs['Base Color'])
            if m.get('export_albedo', '').endswith('.png'): nt.links.new(alb.outputs['Alpha'], bsdf.inputs['Alpha'])
            if tc is not None:
                for l in list(alb.inputs['Vector'].links): nt.links.remove(l)
                alb.projection = 'FLAT'; nt.links.new(tc.outputs['UV'], alb.inputs['Vector'])
        else:
            tint = list(m.get('export_tint', [1, 1, 1, 1])); col = bsdf.inputs['Base Color'].default_value
            bsdf.inputs['Base Color'].default_value = (col[0] * tint[0], col[1] * tint[1], col[2] * tint[2], 1.0)
        for l in list(bsdf.inputs['Roughness'].links): nt.links.remove(l)
        bsdf.inputs['Roughness'].default_value = float(m.get('export_rough', 0.8))
        if out is not None:
            for l in list(out.inputs['Surface'].links): nt.links.remove(l)
            nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
        nm = next((n for n in nt.nodes if n.type == 'NORMAL_MAP'), None)
        if nm is not None:
            tn = next((l.from_node for l in nm.inputs['Color'].links), None)
            if tn is not None and tc is not None:
                for l in list(tn.inputs['Vector'].links): nt.links.remove(l)
                tn.projection = 'FLAT'; nt.links.new(tc.outputs['UV'], tn.inputs['Vector']); nm.space = 'TANGENT'
    if lite:
        for ob in list(bpy.data.objects):
            if ob.name.startswith('Terrain') :
                md = ob.modifiers.new('Decimate', 'DECIMATE'); md.ratio = 0.3
        for im in bpy.data.images:
            if im.size[0] > 1024: im.scale(im.size[0] // 2, im.size[1] // 2)
    for ob in list(bpy.data.objects):
        if ob.name == 'FarGround': bpy.data.objects.remove(ob)
    bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', export_apply=True, export_materials='EXPORT', export_image_format='AUTO', export_jpeg_quality=80,
                              export_normals=True, export_texcoords=True, export_cameras=True, export_lights=False, export_yup=True, use_visible=True, export_extras=True)
    print('exported', path, os.path.getsize(path) / 1e6, 'MB')

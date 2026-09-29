# BDM Mechanical Reveal — production scene with Sketchfab CC BY V8
# Author attribution required: Pro_modeler (Tahminayeasminmony)

import bpy
import math
import os
from mathutils import Vector, Euler, Matrix

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
GLB = os.path.join(ROOT, "assets", "3d", "source", "v8-engine-pro_modeler-glb.glb")
HDRI = os.path.join(ROOT, "assets", "3d", "hdri", "autoshop_01_2k.hdr")
TEX = os.path.join(ROOT, "assets", "3d", "textures", "metal_plate")
BLEND = os.path.join(ROOT, "assets", "3d", "blender", "bdm_mechanical_reveal.blend")
OUT = os.path.join(ROOT, "assets", "3d", "renders")

BDM_GREEN = (0.0, 0.835, 0.388, 1.0)  # #00D563 brief
FPS = 24
FRAME_END = 144  # 6s


def clear():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def col(name, parent=None):
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if parent is None:
        if c.name not in bpy.context.scene.collection.children:
            bpy.context.scene.collection.children.link(c)
    else:
        if c.name not in parent.children:
            parent.children.link(c)
    return c


def link(obj, collection):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collection.objects.link(obj)


def import_engine(dest_col):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=GLB)
    new = [o for o in bpy.data.objects if o not in before]
    # Parent under empty
    root = bpy.data.objects.new("V8_Root", None)
    bpy.context.scene.collection.objects.link(root)
    link(root, dest_col)
    meshes = []
    for o in new:
        link(o, dest_col)
        o.parent = root
        if o.type == "MESH":
            meshes.append(o)
            for p in o.data.polygons:
                p.use_smooth = True

    # Compute bounds in world
    mn = Vector((1e9, 1e9, 1e9))
    mx = Vector((-1e9, -1e9, -1e9))
    for o in meshes:
        for corner in o.bound_box:
            w = o.matrix_world @ Vector(corner)
            mn = Vector((min(mn.x, w.x), min(mn.y, w.y), min(mn.z, w.z)))
            mx = Vector((max(mx.x, w.x), max(mx.y, w.y), max(mx.z, w.z)))
    center = (mn + mx) * 0.5
    size = mx - mn
    # Center on origin, sit on Z=0, scale to ~1.1m length
    target = 1.15
    scale = target / max(size.x, size.y, size.z)
    root.location = -center * scale
    root.location.z = -mn.z * scale
    root.scale = (scale, scale, scale)
    # Rotate for cinematic 3/4 view (model Y-up from glTF often)
    root.rotation_euler = Euler((0, 0, math.radians(-25)), "XYZ")
    bpy.context.view_layer.update()
    return root, meshes


def enhance_materials(meshes):
    """Keep mesh materials; boost metallic look + add discrete green emit accents."""
    # Soften existing materials toward automotive metal
    for mat in bpy.data.materials:
        if not mat.use_nodes:
            continue
        for n in mat.node_tree.nodes:
            if n.type == "BSDF_PRINCIPLED":
                # nudge toward metal without destroying textures
                met = n.inputs.get("Metallic")
                rough = n.inputs.get("Roughness")
                if met and met.default_value < 0.5:
                    met.default_value = min(1.0, met.default_value + 0.35)
                if rough:
                    rough.default_value = max(0.18, min(0.55, rough.default_value))

    emit = bpy.data.materials.new("MAT_BDM_Green_Emit")
    emit.use_nodes = True
    nt = emit.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (0.01, 0.01, 0.01, 1)
    bsdf.inputs["Emission Color"].default_value = BDM_GREEN
    bsdf.inputs["Emission Strength"].default_value = 2.0
    bsdf.inputs["Roughness"].default_value = 0.35
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    # Add small accent empties as emission spheres near turbos / high points — attached to root
    accents = []
    # Pick a few meshes with Material.013 (often housings) if present
    candidates = [o for o in meshes if any(m and "013" in m.name for m in o.data.materials)]
    if not candidates:
        candidates = sorted(meshes, key=lambda o: len(o.data.vertices), reverse=True)[:4]
    for i, o in enumerate(candidates[:3]):
        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.04, minor_radius=0.003,
            location=o.matrix_world.translation + Vector((0.02, 0, 0.05))
        )
        ring = bpy.context.active_object
        ring.name = f"Accent_Green_{i+1}"
        ring.data.materials.append(emit)
        accents.append(ring)
    return accents


def setup_world():
    world = bpy.data.worlds.new("BDM_World")
    bpy.context.scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.inputs["Strength"].default_value = 0.22
    env = nt.nodes.new("ShaderNodeTexEnvironment")
    if os.path.isfile(HDRI):
        env.image = bpy.data.images.load(HDRI, check_existing=True)
    mapn = nt.nodes.new("ShaderNodeMapping")
    mapn.inputs["Rotation"].default_value = (0, 0, math.radians(40))
    coord = nt.nodes.new("ShaderNodeTexCoord")
    dark = nt.nodes.new("ShaderNodeBackground")
    dark.inputs["Color"].default_value = (0.004, 0.004, 0.005, 1)
    mix = nt.nodes.new("ShaderNodeMixShader")
    fac = nt.nodes.new("ShaderNodeValue")
    fac.outputs[0].default_value = 0.5
    nt.links.new(coord.outputs["Generated"], mapn.inputs["Vector"])
    nt.links.new(mapn.outputs["Vector"], env.inputs["Vector"])
    nt.links.new(env.outputs["Color"], bg.inputs["Color"])
    nt.links.new(fac.outputs[0], mix.inputs["Fac"])
    nt.links.new(bg.outputs["Background"], mix.inputs[1])
    nt.links.new(dark.outputs["Background"], mix.inputs[2])
    nt.links.new(mix.outputs["Shader"], out.inputs["Surface"])


def setup_lights(lights_col):
    bpy.ops.object.light_add(type="AREA", location=(1.6, -1.8, 1.9))
    key = bpy.context.active_object
    key.name = "Light_Key_Soft"
    key.data.energy = 180
    key.data.size = 2.4
    key.data.color = (1.0, 0.98, 0.94)
    key.rotation_euler = Euler((math.radians(48), 0, math.radians(38)), "XYZ")
    link(key, lights_col)

    bpy.ops.object.light_add(type="AREA", location=(-1.2, 1.3, 1.5))
    fill = bpy.context.active_object
    fill.name = "Light_Fill_White"
    fill.data.energy = 45
    fill.data.size = 1.8
    fill.data.color = (1, 1, 1)
    fill.rotation_euler = Euler((math.radians(60), 0, math.radians(-40)), "XYZ")
    link(fill, lights_col)

    bpy.ops.object.light_add(type="AREA", location=(-1.0, -0.4, 0.6))
    rim = bpy.context.active_object
    rim.name = "Light_Rim_BDM_Green"
    rim.data.energy = 28
    rim.data.size = 0.7
    rim.data.color = (0.05, 0.85, 0.42)
    rim.rotation_euler = Euler((math.radians(90), 0, math.radians(-90)), "XYZ")
    link(rim, lights_col)

    bpy.ops.object.light_add(type="SPOT", location=(-1.8, -1.1, 1.6))
    sweep = bpy.context.active_object
    sweep.name = "Light_Sweep_Green"
    sweep.data.energy = 0
    sweep.data.color = (0.15, 0.95, 0.48)
    sweep.data.spot_size = math.radians(24)
    sweep.data.spot_blend = 0.75
    sweep.data.shadow_soft_size = 0.2
    tgt = bpy.data.objects.new("Sweep_Target", None)
    bpy.context.scene.collection.objects.link(tgt)
    tgt.location = (0.1, 0.1, 0.35)
    link(tgt, lights_col)
    track = sweep.constraints.new("TRACK_TO")
    track.target = tgt
    track.track_axis = "TRACK_NEGATIVE_Z"
    track.up_axis = "UP_Y"
    link(sweep, lights_col)

    for f, e, x in [
        (1, 0.0, -1.8),
        (24, 140.0, -0.6),
        (72, 220.0, 0.3),
        (120, 100.0, 1.0),
        (FRAME_END, 40.0, 1.2),
    ]:
        sweep.location = (x, -1.1 + 0.35 * f / FRAME_END, 1.6)
        sweep.keyframe_insert("location", frame=f)
        sweep.data.energy = e
        sweep.data.keyframe_insert("energy", frame=f)

    if sweep.animation_data and sweep.animation_data.action:
        for fc in sweep.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = "BEZIER"
                kp.handle_left_type = "AUTO_CLAMPED"
                kp.handle_right_type = "AUTO_CLAMPED"

    for f, e in [(1, 6.0), (36, 30.0), (FRAME_END, 34.0)]:
        rim.data.energy = e
        rim.data.keyframe_insert("energy", frame=f)


def setup_cameras(cams_col):
    # Desktop: engine right, copy left
    bpy.ops.object.camera_add(location=(-0.55, -2.15, 0.72))
    cam_d = bpy.context.active_object
    cam_d.name = "Camera_Desktop_Hero"
    cam_d.data.lens = 55
    cam_d.data.clip_start = 0.05
    cam_d.data.dof.use_dof = True
    cam_d.data.dof.focus_distance = 2.2
    cam_d.data.dof.aperture_fstop = 2.8
    cam_d.rotation_euler = Euler((math.radians(78), 0, math.radians(-20)), "XYZ")
    link(cam_d, cams_col)

    bpy.ops.object.camera_add(location=(0.05, -1.85, 1.05))
    cam_m = bpy.context.active_object
    cam_m.name = "Camera_Mobile_Hero"
    cam_m.data.lens = 40
    cam_m.data.clip_start = 0.05
    cam_m.data.dof.use_dof = True
    cam_m.data.dof.focus_distance = 1.9
    cam_m.data.dof.aperture_fstop = 3.2
    cam_m.rotation_euler = Euler((math.radians(68), 0, math.radians(5)), "XYZ")
    link(cam_m, cams_col)

    bpy.ops.object.camera_add(location=(-0.2, -2.0, 0.85))
    cam_f = bpy.context.active_object
    cam_f.name = "Camera_Feed_45"
    cam_f.data.lens = 48
    cam_f.rotation_euler = Euler((math.radians(74), 0, math.radians(-10)), "XYZ")
    link(cam_f, cams_col)

    bpy.ops.object.camera_add(location=(0.0, -1.7, 1.15))
    cam_s = bpy.context.active_object
    cam_s.name = "Camera_Story_916"
    cam_s.data.lens = 38
    cam_s.rotation_euler = Euler((math.radians(64), 0, math.radians(3)), "XYZ")
    link(cam_s, cams_col)

    # Short orbit
    start = cam_d.location.copy()
    start_rot = cam_d.rotation_euler.copy()
    for f, z_off, dolly in [(1, 0.0, 0.0), (72, math.radians(8), -0.08), (FRAME_END, math.radians(14), -0.12)]:
        cam_d.rotation_euler = Euler((start_rot.x, start_rot.y, start_rot.z + z_off), "XYZ")
        cam_d.location = Vector((start.x + dolly * 0.2, start.y - dolly, start.z + abs(dolly) * 0.1))
        cam_d.keyframe_insert("rotation_euler", frame=f)
        cam_d.keyframe_insert("location", frame=f)
    if cam_d.animation_data and cam_d.animation_data.action:
        for fc in cam_d.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = "BEZIER"
                kp.handle_left_type = "AUTO_CLAMPED"
                kp.handle_right_type = "AUTO_CLAMPED"

    bpy.context.scene.camera = cam_d
    return cam_d


def setup_env(env_col):
    bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
    floor = bpy.context.active_object
    floor.name = "ENV_Floor"
    mat = bpy.data.materials.new("MAT_Floor")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.008, 0.008, 0.01, 1)
    bsdf.inputs["Metallic"].default_value = 0.2
    bsdf.inputs["Roughness"].default_value = 0.45
    floor.data.materials.append(mat)
    link(floor, env_col)

    bpy.ops.mesh.primitive_plane_add(size=14, location=(0, 3.2, 2))
    wall = bpy.context.active_object
    wall.name = "ENV_BackWall"
    wall.rotation_euler = Euler((math.radians(90), 0, 0), "XYZ")
    wall.data.materials.append(mat)
    link(wall, env_col)


def setup_render(scene):
    scene.render.engine = "CYCLES"
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        prefs.compute_device_type = "METAL"
        prefs.get_devices()
        for d in prefs.devices:
            d.use = True
        scene.cycles.device = "GPU"
    except Exception:
        scene.cycles.device = "CPU"
    scene.cycles.samples = 128
    scene.cycles.use_denoising = True
    scene.view_settings.view_transform = "Filmic"
    scene.view_settings.look = "Medium High Contrast"
    scene.render.image_settings.file_format = "PNG"
    scene.render.fps = FPS
    scene.frame_start = 1
    scene.frame_end = FRAME_END
    scene.unit_settings.system = "METRIC"


def main():
    os.makedirs(os.path.dirname(BLEND), exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    clear()
    scene = bpy.context.scene
    scene.name = "BDM_Mechanical_Reveal"

    root_col = col("BDM_Mechanical_Reveal")
    eng = col("01_Engine", root_col)
    env = col("02_Environment", root_col)
    lights = col("03_Lights", root_col)
    cams = col("04_Cameras", root_col)

    root, meshes = import_engine(eng)
    accents = enhance_materials(meshes)
    for a in accents:
        link(a, eng)
        a.parent = root

    setup_env(env)
    setup_world()
    setup_lights(lights)
    setup_cameras(cams)
    setup_render(scene)

    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    bpy.ops.file.make_paths_relative()
    bpy.ops.wm.save_mainfile()
    print("SAVED", BLEND)
    print("MESHES", len(meshes))


if __name__ == "__main__":
    main()

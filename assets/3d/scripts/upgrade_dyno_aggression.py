# Dyno aggression upgrade — metal hard + wet floor + rim #00D563
# No text/CTA baked into render.

import bpy
import math
import os
from mathutils import Euler, Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
BLEND = os.path.join(ROOT, "assets", "3d", "blender", "bdm_mechanical_reveal.blend")
TEX = os.path.join(ROOT, "assets", "3d", "textures", "metal_plate")
BDM_GREEN = (0.0, 0.835, 0.388, 1.0)


def principled(mat):
    mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return nt, bsdf


def metal(name, base, metallic=1.0, roughness=0.22, maps=False, aniso=0.45, coat=0.0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    nt, bsdf = principled(mat)
    bsdf.inputs["Base Color"].default_value = base
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if "Anisotropic" in bsdf.inputs:
        bsdf.inputs["Anisotropic"].default_value = aniso
    if "Coat Weight" in bsdf.inputs and coat > 0:
        bsdf.inputs["Coat Weight"].default_value = coat
        if "Coat Roughness" in bsdf.inputs:
            bsdf.inputs["Coat Roughness"].default_value = 0.08
    if maps and os.path.isfile(os.path.join(TEX, "metal_plate_Rough_2k.jpg")):
        coord = nt.nodes.new("ShaderNodeTexCoord")
        mapping = nt.nodes.new("ShaderNodeMapping")
        mapping.inputs["Scale"].default_value = (4.2, 4.2, 4.2)
        nt.links.new(coord.outputs["Object"], mapping.inputs["Vector"])

        def tex(fname, cs="Non-Color"):
            img = bpy.data.images.load(os.path.join(TEX, fname), check_existing=True)
            img.colorspace_settings.name = cs
            n = nt.nodes.new("ShaderNodeTexImage")
            n.image = img
            nt.links.new(mapping.outputs["Vector"], n.inputs["Vector"])
            return n

        rough = tex("metal_plate_Rough_2k.jpg")
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = "FLOAT"
        mix.inputs["Factor"].default_value = 0.55
        mix.inputs["A"].default_value = roughness
        nt.links.new(rough.outputs["Color"], mix.inputs["B"])
        nt.links.new(mix.outputs["Result"], bsdf.inputs["Roughness"])
        nrm = tex("metal_plate_nor_gl_2k.jpg")
        nm = nt.nodes.new("ShaderNodeNormalMap")
        nm.inputs["Strength"].default_value = 0.35
        nt.links.new(nrm.outputs["Color"], nm.inputs["Color"])
        nt.links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def wet_floor(mat):
    nt, bsdf = principled(mat)
    bsdf.inputs["Base Color"].default_value = (0.01, 0.012, 0.014, 1)
    bsdf.inputs["Metallic"].default_value = 0.65
    bsdf.inputs["Roughness"].default_value = 0.08
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 1.0
    if "Coat Weight" in bsdf.inputs:
        bsdf.inputs["Coat Weight"].default_value = 1.0
        bsdf.inputs["Coat Roughness"].default_value = 0.02
    return mat


def green_emit(name, strength=6.0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    nt, bsdf = principled(mat)
    bsdf.inputs["Base Color"].default_value = (0.01, 0.01, 0.01, 1)
    bsdf.inputs["Metallic"].default_value = 0.3
    bsdf.inputs["Roughness"].default_value = 0.25
    bsdf.inputs["Emission Color"].default_value = BDM_GREEN
    bsdf.inputs["Emission Strength"].default_value = strength
    return mat


def assign_materials():
    chrome = metal("MAT_Chrome_Hard", (0.78, 0.79, 0.81, 1), roughness=0.08, aniso=0.55, coat=0.4)
    aluminum = metal("MAT_Aluminum_Machined", (0.42, 0.43, 0.45, 1), roughness=0.28, maps=True, aniso=0.5)
    cast = metal("MAT_Cast_Iron", (0.045, 0.046, 0.048, 1), metallic=0.7, roughness=0.52, maps=True, aniso=0.12)
    oil = metal("MAT_Oil_Steel", (0.12, 0.13, 0.14, 1), roughness=0.18, aniso=0.6, coat=0.55)
    anod = metal("MAT_Anodized_Dark", (0.02, 0.02, 0.022, 1), roughness=0.16, maps=False, aniso=0.2)
    emit = green_emit("MAT_BDM_Green_Emit_Hard", 7.5)

    for obj in bpy.data.objects:
        if obj.type != "MESH":
            continue
        if obj.name.startswith("ENV_"):
            continue
        if obj.name.startswith("Accent_"):
            obj.data.materials.clear()
            obj.data.materials.append(emit)
            continue

        names = " ".join(m.name if m else "" for m in obj.data.materials)
        nverts = len(obj.data.vertices)
        dims = obj.dimensions
        longest = max(dims)

        # Pipe / header heuristic: elongated mid-poly
        if nverts < 25000 and longest > 0.25 and min(dims) < 0.12:
            target = chrome
        elif "013" in names or nverts > 80000:
            target = cast
        elif "012" in names:
            target = oil
        elif nverts < 2500:
            target = anod
        else:
            target = aluminum

        obj.data.materials.clear()
        obj.data.materials.append(target)

    # Ensure accents exist with hard emit
    for mat in bpy.data.materials:
        if "Green" in mat.name and mat.use_nodes:
            for n in mat.node_tree.nodes:
                if n.type == "BSDF_PRINCIPLED":
                    n.inputs["Emission Color"].default_value = BDM_GREEN
                    n.inputs["Emission Strength"].default_value = 7.0


def upgrade_floor():
    floor = bpy.data.objects.get("ENV_Floor")
    if not floor:
        return
    mat = bpy.data.materials.get("MAT_Floor_Wet") or bpy.data.materials.new("MAT_Floor_Wet")
    wet_floor(mat)
    floor.data.materials.clear()
    floor.data.materials.append(mat)
    # Slightly larger footprint
    floor.scale = (1.4, 1.4, 1.0)


def upgrade_lights():
    key = bpy.data.objects.get("Light_Key_Soft")
    if key:
        key.data.energy = 420
        key.data.size = 1.4
        key.data.color = (1.0, 0.96, 0.9)
        key.location = (2.1, -2.2, 2.15)
        key.rotation_euler = Euler((math.radians(42), 0, math.radians(48)), "XYZ")

    fill = bpy.data.objects.get("Light_Fill_White")
    if fill:
        fill.data.energy = 28
        fill.data.size = 2.2
        fill.location = (-1.6, 1.6, 1.2)

    rim = bpy.data.objects.get("Light_Rim_BDM_Green")
    if rim:
        rim.data.energy = 95
        rim.data.size = 0.45
        rim.data.color = (0.05, 0.95, 0.45)
        rim.location = (-1.35, -0.15, 0.55)

    # Extra hard spot for dyno punch
    spot = bpy.data.objects.get("Light_Dyno_Hard")
    if not spot:
        bpy.ops.object.light_add(type="SPOT", location=(0.9, -2.4, 2.4))
        spot = bpy.context.active_object
        spot.name = "Light_Dyno_Hard"
    spot.data.energy = 650
    spot.data.color = (1.0, 0.97, 0.92)
    spot.data.spot_size = math.radians(28)
    spot.data.spot_blend = 0.35
    spot.data.shadow_soft_size = 0.05
    spot.rotation_euler = Euler((math.radians(55), 0, math.radians(18)), "XYZ")

    sweep = bpy.data.objects.get("Light_Sweep_Green")
    if sweep:
        # Keep animation but boost peaks
        if sweep.animation_data and sweep.animation_data.action:
            for fc in sweep.animation_data.action.fcurves:
                if fc.data_path == "energy" or "energy" in fc.data_path:
                    for kp in fc.keyframe_points:
                        kp.co.y = min(380.0, kp.co.y * 1.6)


def upgrade_cameras():
    cam_d = bpy.data.objects.get("Camera_Desktop_Hero")
    if cam_d:
        if cam_d.animation_data:
            cam_d.animation_data_clear()
        # Low aggressive 3/4 — engine right, copy left
        cam_d.location = (-0.95, -3.15, 0.72)
        cam_d.rotation_euler = Euler((math.radians(78), 0, math.radians(-18)), "XYZ")
        cam_d.data.lens = 48
        cam_d.data.dof.use_dof = True
        cam_d.data.dof.focus_distance = 3.2
        cam_d.data.dof.aperture_fstop = 2.4
        end = bpy.context.scene.frame_end
        start = cam_d.location.copy()
        start_rot = cam_d.rotation_euler.copy()
        for f, z_off, dolly in [(1, 0.0, 0.0), (72, math.radians(5), -0.08), (end, math.radians(9), -0.12)]:
            cam_d.rotation_euler = Euler((start_rot.x, start_rot.y, start_rot.z + z_off), "XYZ")
            cam_d.location = Vector((start.x + dolly * 0.12, start.y - dolly, start.z + abs(dolly) * 0.05))
            cam_d.keyframe_insert("rotation_euler", frame=f)
            cam_d.keyframe_insert("location", frame=f)

    cam_m = bpy.data.objects.get("Camera_Mobile_Hero")
    if cam_m:
        cam_m.location = (0.05, -2.55, 1.05)
        cam_m.rotation_euler = Euler((math.radians(70), 0, math.radians(2)), "XYZ")
        cam_m.data.lens = 36
        cam_m.data.dof.focus_distance = 2.5
        cam_m.data.dof.aperture_fstop = 2.8


def upgrade_world():
    world = bpy.context.scene.world
    if not world or not world.use_nodes:
        return
    for n in world.node_tree.nodes:
        if n.type == "BACKGROUND" and n.inputs[0].is_linked:
            n.inputs["Strength"].default_value = 0.55
        if n.type == "VALUE":
            # less pure black mix → more HDRI reflection for metal
            n.outputs[0].default_value = 0.28


def main():
    bpy.ops.wm.open_mainfile(filepath=BLEND)
    assign_materials()
    upgrade_floor()
    upgrade_lights()
    upgrade_cameras()
    upgrade_world()
    sc = bpy.context.scene
    sc.view_settings.view_transform = "Filmic"
    sc.view_settings.look = "High Contrast"
    sc.view_settings.exposure = 0.15
    bpy.ops.wm.save_mainfile()
    print("DYNO_AGGRESSION_UPGRADED")


if __name__ == "__main__":
    main()

# Fix materials + camera framing on existing blend
import bpy
import math
import os
from mathutils import Euler, Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
BLEND = os.path.join(ROOT, "assets", "3d", "blender", "bdm_mechanical_reveal.blend")
TEX = os.path.join(ROOT, "assets", "3d", "textures", "metal_plate")
BDM_GREEN = (0.0, 0.835, 0.388, 1.0)


def make_metal(name, base, metallic=1.0, roughness=0.28, use_maps=True, anisotropy=0.35):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = base
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if "Anisotropic" in bsdf.inputs:
        bsdf.inputs["Anisotropic"].default_value = anisotropy
    if use_maps and os.path.isfile(os.path.join(TEX, "metal_plate_Rough_2k.jpg")):
        coord = nt.nodes.new("ShaderNodeTexCoord")
        mapping = nt.nodes.new("ShaderNodeMapping")
        mapping.inputs["Scale"].default_value = (3.5, 3.5, 3.5)
        nt.links.new(coord.outputs["Object"], mapping.inputs["Vector"])

        def img(fname, cs="Non-Color"):
            path = os.path.join(TEX, fname)
            image = bpy.data.images.load(path, check_existing=True)
            image.colorspace_settings.name = cs
            n = nt.nodes.new("ShaderNodeTexImage")
            n.image = image
            nt.links.new(mapping.outputs["Vector"], n.inputs["Vector"])
            return n

        rough = img("metal_plate_Rough_2k.jpg")
        metal = img("metal_plate_Metal_2k.jpg")
        nrm = img("metal_plate_nor_gl_2k.jpg")
        mix_r = nt.nodes.new("ShaderNodeMix")
        mix_r.data_type = "FLOAT"
        mix_r.inputs["Factor"].default_value = 0.4
        mix_r.inputs["A"].default_value = roughness
        nt.links.new(rough.outputs["Color"], mix_r.inputs["B"])
        nt.links.new(mix_r.outputs["Result"], bsdf.inputs["Roughness"])
        nt.links.new(metal.outputs["Color"], bsdf.inputs["Metallic"])
        # force high metallic if map weak
        bsdf.inputs["Metallic"].default_value = metallic
        nm = nt.nodes.new("ShaderNodeNormalMap")
        nm.inputs["Strength"].default_value = 0.12
        nt.links.new(nrm.outputs["Color"], nm.inputs["Color"])
        nt.links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def main():
    bpy.ops.wm.open_mainfile(filepath=BLEND)

    aluminum = make_metal("MAT_Aluminum", (0.55, 0.56, 0.58, 1), roughness=0.26, anisotropy=0.4)
    steel = make_metal("MAT_Steel", (0.32, 0.33, 0.35, 1), roughness=0.34, anisotropy=0.5)
    cast = make_metal("MAT_Cast", (0.08, 0.08, 0.09, 1), metallic=0.55, roughness=0.48, anisotropy=0.15)
    anodized = make_metal("MAT_Anodized", (0.02, 0.02, 0.025, 1), metallic=0.9, roughness=0.2, use_maps=False)
    rubber = make_metal("MAT_Rubber", (0.02, 0.02, 0.02, 1), metallic=0.0, roughness=0.88, use_maps=False, anisotropy=0)

    # Assign by original material name / size heuristic
    for obj in bpy.data.objects:
        if obj.type != "MESH" or obj.name.startswith("ENV_") or obj.name.startswith("Accent_"):
            continue
        names = [m.name if m else "" for m in obj.data.materials]
        joined = " ".join(names)
        nverts = len(obj.data.vertices)
        if "013" in joined:
            target = cast
        elif "012" in joined:
            target = steel
        elif nverts > 40000:
            target = aluminum
        elif nverts < 3000:
            target = anodized
        else:
            target = aluminum
        obj.data.materials.clear()
        obj.data.materials.append(target)

    # Belts / thin dark parts: name heuristic for torus-like low poly
    for obj in bpy.data.objects:
        if obj.type != "MESH":
            continue
        if "belt" in obj.name.lower() or obj.name.startswith("Accent_"):
            continue
        # very flat dark rubber for tiny ring meshes
        if len(obj.data.vertices) < 800 and obj.dimensions.x < 0.15:
            # skip — leave metal bolts
            pass

    # Fix green accents emission
    for mat in bpy.data.materials:
        if "Green" in mat.name and mat.use_nodes:
            for n in mat.node_tree.nodes:
                if n.type == "BSDF_PRINCIPLED":
                    n.inputs["Emission Color"].default_value = BDM_GREEN
                    n.inputs["Emission Strength"].default_value = 1.6

    # Pull cameras back for full engine + copy space
    cam_d = bpy.data.objects.get("Camera_Desktop_Hero")
    if cam_d:
        # clear animation then set stronger framing
        if cam_d.animation_data:
            cam_d.animation_data_clear()
        cam_d.location = (-0.85, -2.85, 0.95)
        cam_d.rotation_euler = Euler((math.radians(74), 0, math.radians(-22)), "XYZ")
        cam_d.data.lens = 50
        cam_d.data.dof.focus_distance = 3.0
        # re-animate short orbit
        start = cam_d.location.copy()
        start_rot = cam_d.rotation_euler.copy()
        end = bpy.context.scene.frame_end
        for f, z_off, dolly in [(1, 0.0, 0.0), (72, math.radians(7), -0.1), (end, math.radians(12), -0.15)]:
            cam_d.rotation_euler = Euler((start_rot.x, start_rot.y, start_rot.z + z_off), "XYZ")
            cam_d.location = Vector((start.x + dolly * 0.15, start.y - dolly, start.z + abs(dolly) * 0.08))
            cam_d.keyframe_insert("rotation_euler", frame=f)
            cam_d.keyframe_insert("location", frame=f)
        if cam_d.animation_data and cam_d.animation_data.action:
            for fc in cam_d.animation_data.action.fcurves:
                for kp in fc.keyframe_points:
                    kp.interpolation = "BEZIER"
                    kp.handle_left_type = "AUTO_CLAMPED"
                    kp.handle_right_type = "AUTO_CLAMPED"

    cam_m = bpy.data.objects.get("Camera_Mobile_Hero")
    if cam_m:
        cam_m.location = (0.1, -2.45, 1.25)
        cam_m.rotation_euler = Euler((math.radians(66), 0, math.radians(4)), "XYZ")
        cam_m.data.lens = 38
        cam_m.data.dof.focus_distance = 2.6

    # Soften green lights — less wash
    rim = bpy.data.objects.get("Light_Rim_BDM_Green")
    if rim:
        rim.data.energy = 18
        rim.data.color = (0.08, 0.75, 0.4)
    key = bpy.data.objects.get("Light_Key_Soft")
    if key:
        key.data.energy = 220
        key.data.size = 2.8
    fill = bpy.data.objects.get("Light_Fill_White")
    if fill:
        fill.data.energy = 55

    # World HDRI a bit stronger for reflections
    world = bpy.context.scene.world
    if world and world.use_nodes:
        for n in world.node_tree.nodes:
            if n.type == "BACKGROUND" and n.inputs[0].is_linked:
                n.inputs["Strength"].default_value = 0.35
            if n.type == "VALUE":
                n.outputs[0].default_value = 0.35  # less pure black mix

    bpy.ops.wm.save_mainfile()
    print("MATERIALS_CAMERAS_FIXED")


if __name__ == "__main__":
    main()

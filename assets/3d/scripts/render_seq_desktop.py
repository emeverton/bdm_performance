import bpy, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
BLEND = os.path.join(ROOT, "assets", "3d", "blender", "bdm_mechanical_reveal.blend")
SEQ = os.path.join(ROOT, "assets", "3d", "renders", "video", "seq")
os.makedirs(SEQ, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=BLEND)
sc = bpy.context.scene
sc.render.engine = "CYCLES"
sc.cycles.samples = 14
sc.cycles.use_denoising = True
try:
    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type = "METAL"
    prefs.get_devices()
    for d in prefs.devices:
        d.use = True
    sc.cycles.device = "GPU"
except Exception:
    sc.cycles.device = "CPU"
sc.camera = bpy.data.objects["Camera_Desktop_Hero"]
sc.render.resolution_x = 1280
sc.render.resolution_y = 720
sc.render.resolution_percentage = 100
sc.render.image_settings.file_format = "PNG"
sc.render.filepath = os.path.join(SEQ, "frame_")
sc.frame_start = 1
sc.frame_end = 144
print("SEQ_RENDER_START", flush=True)
bpy.ops.render.render(animation=True)
print("SEQ_RENDER_DONE", flush=True)

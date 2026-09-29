import bpy
import os

ROOT = "/Users/veltrus/Projects/bdm_performance"
BLEND = os.path.join(ROOT, "assets", "3d", "blender", "bdm_mechanical_reveal.blend")
bpy.ops.wm.open_mainfile(filepath=BLEND)
sc = bpy.context.scene

try:
    sc.render.engine = "BLENDER_EEVEE_NEXT"
except Exception:
    sc.render.engine = "BLENDER_EEVEE"

ee = sc.eevee
if hasattr(ee, "taa_render_samples"):
    ee.taa_render_samples = 48
if hasattr(ee, "use_raytracing"):
    ee.use_raytracing = True

sc.render.image_settings.file_format = "FFMPEG"
sc.render.ffmpeg.format = "MPEG4"
sc.render.ffmpeg.codec = "H264"
sc.render.ffmpeg.constant_rate_factor = "HIGH"
sc.render.ffmpeg.ffmpeg_preset = "GOOD"
sc.render.ffmpeg.audio_codec = "NONE"
sc.frame_start = 1
sc.frame_end = 144

jobs = [
    ("Camera_Desktop_Hero", 1920, 1080, "video", "mechanical_reveal_1920x1080"),
    ("Camera_Feed_45", 1080, 1350, "feed", "mechanical_reveal_1080x1350"),
    ("Camera_Story_916", 1080, 1920, "story", "mechanical_reveal_1080x1920"),
]

for cam, w, h, folder, name in jobs:
    outdir = os.path.join(ROOT, "assets", "3d", "renders", folder)
    os.makedirs(outdir, exist_ok=True)
    # remove broken tiny files
    for f in os.listdir(outdir):
        p = os.path.join(outdir, f)
        if f.endswith(".mp4") and os.path.getsize(p) < 1024:
            os.remove(p)
    sc.camera = bpy.data.objects[cam]
    sc.render.resolution_x = w
    sc.render.resolution_y = h
    sc.render.filepath = os.path.join(outdir, name)
    print("START", name, sc.render.engine, flush=True)
    bpy.ops.render.render(animation=True)
    print("DONE", name, flush=True)

print("ALL_VIDEOS_DONE", flush=True)

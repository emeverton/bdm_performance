# Render BDM masters + LP hero sizes + playblast
import bpy
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
BLEND = os.path.join(ROOT, "assets", "3d", "blender", "bdm_mechanical_reveal.blend")
OUT = os.path.join(ROOT, "assets", "3d", "renders")


def gpu(scene, samples):
    scene.render.engine = "CYCLES"
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        prefs.compute_device_type = "METAL"
        prefs.get_devices()
        for d in prefs.devices:
            d.use = True
        scene.cycles.device = "GPU"
    except Exception:
        scene.cycles.device = "CPU"
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"


def still(path, w, h, frame, cam, samples=96):
    sc = bpy.context.scene
    gpu(sc, samples)
    sc.camera = bpy.data.objects[cam]
    sc.frame_set(frame)
    sc.render.resolution_x = w
    sc.render.resolution_y = h
    sc.render.resolution_percentage = 100
    sc.render.filepath = path
    print("STILL", path, w, h, cam, frame)
    bpy.ops.render.render(write_still=True)


def anim(path_prefix, w, h, cam, samples=24):
    sc = bpy.context.scene
    gpu(sc, samples)
    sc.camera = bpy.data.objects[cam]
    sc.render.resolution_x = w
    sc.render.resolution_y = h
    sc.render.image_settings.file_format = "FFMPEG"
    sc.render.ffmpeg.format = "MPEG4"
    sc.render.ffmpeg.codec = "H264"
    sc.render.ffmpeg.constant_rate_factor = "HIGH"
    sc.render.ffmpeg.ffmpeg_preset = "GOOD"
    sc.render.filepath = path_prefix
    print("ANIM", path_prefix)
    bpy.ops.render.render(animation=True)


def main():
    if not os.path.isfile(BLEND):
        print("missing blend", BLEND)
        sys.exit(1)
    bpy.ops.wm.open_mainfile(filepath=BLEND)
    end = bpy.context.scene.frame_end
    os.makedirs(os.path.join(OUT, "desktop"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "mobile"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "feed"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "story"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "video"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "review"), exist_ok=True)

    # Hero masters for LP (end frame = stable)
    still(os.path.join(OUT, "desktop", "hero_desktop_3840.png"), 3840, 2160, end, "Camera_Desktop_Hero", 120)
    still(os.path.join(OUT, "desktop", "hero_desktop_2560.png"), 2560, 1440, end, "Camera_Desktop_Hero", 100)
    still(os.path.join(OUT, "mobile", "hero_mobile_2160.png"), 2160, 3840, end, "Camera_Mobile_Hero", 100)
    still(os.path.join(OUT, "mobile", "hero_mobile_1440.png"), 1440, 1920, end, "Camera_Mobile_Hero", 90)

    # Social
    still(os.path.join(OUT, "feed", "feed_2160x2700.png"), 2160, 2700, end, "Camera_Feed_45", 90)
    still(os.path.join(OUT, "story", "story_2160x3840.png"), 2160, 3840, end, "Camera_Story_916", 90)

    # Review thumbnail mid-reveal
    still(os.path.join(OUT, "review", "thumbnail_1600.png"), 1600, 900, max(1, end // 2), "Camera_Desktop_Hero", 64)

    # Main video 1920 + playblast already covered by main
    anim(os.path.join(OUT, "video", "mechanical_reveal_1920x1080"), 1920, 1080, "Camera_Desktop_Hero", 28)
    anim(os.path.join(OUT, "feed", "mechanical_reveal_1080x1350"), 1080, 1350, "Camera_Feed_45", 22)
    anim(os.path.join(OUT, "story", "mechanical_reveal_1080x1920"), 1080, 1920, "Camera_Story_916", 22)

    print("RENDER_ALL_DONE")


if __name__ == "__main__":
    main()

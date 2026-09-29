# Render dyno-aggression hero stills (EEVEE — fast metals) + export hooks for WebP pipeline
import bpy
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
BLEND = os.path.join(ROOT, "assets", "3d", "blender", "bdm_mechanical_reveal.blend")
OUT = os.path.join(ROOT, "assets", "3d", "renders")


def setup_eevee(scene, samples=64):
    # Blender 4.2 LTS: EEVEE Next only
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    ee = getattr(scene, "eevee", None)
    if ee:
        if hasattr(ee, "taa_render_samples"):
            ee.taa_render_samples = samples
        if hasattr(ee, "use_raytracing"):
            ee.use_raytracing = True
        if hasattr(ee, "use_ssr"):
            ee.use_ssr = True
            ee.use_ssr_refraction = True
        if hasattr(ee, "use_bloom"):
            ee.use_bloom = True
            ee.bloom_threshold = 0.7
            ee.bloom_intensity = 0.12
            ee.bloom_color = (0.55, 1.0, 0.72)
        if hasattr(ee, "use_gtao"):
            ee.use_gtao = True
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.color_depth = "8"
    scene.view_settings.view_transform = "Filmic"
    scene.view_settings.look = "High Contrast"
    scene.view_settings.exposure = 0.12


def still(path, w, h, frame, cam, samples=64):
    sc = bpy.context.scene
    setup_eevee(sc, samples)
    sc.camera = bpy.data.objects[cam]
    sc.frame_set(frame)
    sc.render.resolution_x = w
    sc.render.resolution_y = h
    sc.render.resolution_percentage = 100
    sc.render.filepath = path
    print("STILL", path, w, h, cam, frame, flush=True)
    bpy.ops.render.render(write_still=True)


def main():
    if not os.path.isfile(BLEND):
        print("missing blend", BLEND)
        sys.exit(1)
    bpy.ops.wm.open_mainfile(filepath=BLEND)
    end = bpy.context.scene.frame_end
    os.makedirs(os.path.join(OUT, "desktop"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "mobile"), exist_ok=True)

    still(os.path.join(OUT, "desktop", "hero_desktop_1920.png"), 1920, 1080, end, "Camera_Desktop_Hero", 96)
    still(os.path.join(OUT, "desktop", "hero_desktop_3840.png"), 3840, 2160, end, "Camera_Desktop_Hero", 80)
    still(os.path.join(OUT, "mobile", "hero_mobile_1440.png"), 1440, 1920, end, "Camera_Mobile_Hero", 80)
    still(os.path.join(OUT, "mobile", "hero_mobile_2160.png"), 1080, 1920, end, "Camera_Mobile_Hero", 72)
    print("HERO_STILLS_DONE", flush=True)


if __name__ == "__main__":
    main()

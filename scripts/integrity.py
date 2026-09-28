"""Verify SHA-256 digests of the reviewed source and published assets."""

import hashlib
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "integrity.sha256"
FILES = (
    "index.html",
    "brand/index.html",
    "ads/index.html",
    "styles.css",
    "app.js",
    "styles/core.css",
    "styles/components.css",
    "styles/pages.css",
    "styles/responsive.css",
    "modules/navigation.js",
    "modules/testimonials.js",
    "modules/attribution.js",
    "modules/engagement.js",
    "modules/qualification.js",
    "robots.txt",
    "sitemap.xml",
    ".well-known/security.txt",
    ".nojekyll",
    ".github/workflows/verify.yml",
    ".github/workflows/pages.yml",
    ".github/dependabot.yml",
    "SECURITY.md",
    "scripts/build_brand_manual.py",
    "output/pdf/Manual_Identidade_Visual_BDM_CLevel.pdf",
    "assets/ads/fonts/Montserrat-Bold.ttf",
    "assets/ads/fonts/Montserrat-Regular.ttf",
    "assets/ads/logo-bdm-original.png",
    "assets/brand/simbolo-bdm.png",
    "assets/ads/final/bdm-engenharia-feed.png",
    "assets/ads/final/bdm-engenharia-story.png",
    "assets/ads/final/bdm-engenharia-paisagem.png",
    "assets/ads/final/bdm-oficina-feed.png",
    "assets/ads/final/bdm-oficina-story.png",
    "assets/ads/final/bdm-oficina-paisagem.png",
    "assets/ads/final/bdm-rede-feed.png",
    "assets/ads/final/bdm-rede-story.png",
    "assets/ads/final/bdm-rede-paisagem.png",
    "assets/bdm-hero-960.webp",
    "assets/bdm-hero-1920.webp",
    "assets/bdm-hero-3840.webp",
    "assets/bdm-hero-7680.webp",
    "assets/bdm-hero-mobile-720.webp",
    "assets/bdm-hero-mobile-1440.webp",
)

expected = "".join(
    f"{hashlib.sha256((ROOT / name).read_bytes()).hexdigest()}  {name}\n"
    for name in FILES
)

if "--write" in sys.argv:
    MANIFEST.write_text(expected, encoding="utf-8")
    print("Updated integrity.sha256")
elif not MANIFEST.is_file() or MANIFEST.read_text(encoding="utf-8") != expected:
    raise SystemExit("FAIL: integrity manifest differs from source or assets")
else:
    print("PASS: reviewed source and assets match SHA-256 manifest")

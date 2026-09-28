"""Verify SHA-256 digests of the reviewed source and published assets."""

import hashlib
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "integrity.sha256"
FILES = (
    "index.html",
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
    "robots.txt",
    "sitemap.xml",
    ".well-known/security.txt",
    ".nojekyll",
    ".github/workflows/verify.yml",
    ".github/dependabot.yml",
    "SECURITY.md",
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

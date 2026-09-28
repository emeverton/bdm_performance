"""Refresh content versions and SHA-384 SRI on production entrypoints."""

import base64
import hashlib
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
page = ROOT / "index.html"
html = page.read_text(encoding="utf-8")

for filename, pattern, attribute in (
    ("styles.css", r'<link rel="stylesheet" href="\./styles\.css(?:\?v=[^"]+)?"(?: integrity="[^"]+")?', "href"),
    ("app.js", r'<script type="module" src="\./app\.js(?:\?v=[^"]+)?"(?: integrity="[^"]+")?', "src"),
):
    content = (ROOT / filename).read_bytes()
    version = hashlib.sha256(content).hexdigest()[:12]
    digest = base64.b64encode(hashlib.sha384(content).digest()).decode("ascii")
    tag = "link rel=\"stylesheet\"" if filename == "styles.css" else "script type=\"module\""
    closing = "" if filename == "styles.css" else "></script>"
    replacement = f'<{tag} {attribute}="./{filename}?v={version}" integrity="sha384-{digest}"{closing}'
    html, count = re.subn(pattern + (r'></script>' if filename == "app.js" else ""), replacement, html)
    if count != 1:
        raise SystemExit(f"Expected exactly one {filename} entrypoint, found {count}")

page.write_text(html, encoding="utf-8")

css_version = hashlib.sha256((ROOT / "styles.css").read_bytes()).hexdigest()[:12]
for relative in ("404.html", "brand/index.html", "ads/index.html", "review/index.html"):
    target = ROOT / relative
    source = target.read_text(encoding="utf-8")
    prefix = "../" if "/" in relative else "./"
    source, count = re.subn(
        rf'href="{re.escape(prefix)}styles\.css(?:\?v=[^"]+)?"',
        f'href="{prefix}styles.css?v={css_version}"',
        source,
    )
    if count != 1:
        raise SystemExit(f"Expected exactly one stylesheet in {relative}, found {count}")
    target.write_text(source, encoding="utf-8")

print("Updated content versions and SHA-384 SRI attributes")

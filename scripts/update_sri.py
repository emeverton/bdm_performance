"""Refresh SHA-384 SRI on the two production entrypoints."""

import base64
import hashlib
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
page = ROOT / "index.html"
html = page.read_text(encoding="utf-8")

for filename, pattern in (
    ("styles.css", r'(<link rel="stylesheet" href="\./styles\.css\?v=[^"]+")(?: integrity="[^"]+")?'),
    ("app.js", r'(<script type="module" src="\./app\.js\?v=[^"]+")(?: integrity="[^"]+")?'),
):
    digest = base64.b64encode(hashlib.sha384((ROOT / filename).read_bytes()).digest()).decode("ascii")
    html, count = re.subn(pattern, lambda match: f'{match.group(1)} integrity="sha384-{digest}"', html)
    if count != 1:
        raise SystemExit(f"Expected exactly one {filename} entrypoint, found {count}")

page.write_text(html, encoding="utf-8")
print("Updated SHA-384 SRI attributes")

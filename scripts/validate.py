from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import re
root = Path(__file__).resolve().parents[1]
errors = []
class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.refs = []; self.h1 = 0; self.noindex = False
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "h1": self.h1 += 1
        if tag == "meta" and a.get("name") == "robots": self.noindex |= "noindex" in a.get("content", "")
        for key in ("src", "href"):
            if key in a: self.refs.append(a[key])
for path in [root / x for x in ("index.html", "brand/index.html", "ads/index.html", "review/index.html")]:
    doc = Page(); doc.feed(path.read_text())
    if doc.h1 != 1: errors.append(str(path) + ": expected one H1")
    if not doc.noindex: errors.append(str(path) + ": review noindex missing")
    for ref in doc.refs:
        url = urlsplit(ref)
        if url.scheme or url.netloc or not url.path: continue
        target = (path.parent / unquote(url.path)).resolve()
        if not target.is_relative_to(root): errors.append("Path outside site: " + ref); continue
        if target.is_dir(): target = target / "index.html"
        if not target.exists(): errors.append(str(path) + ": missing " + ref)
for ref in re.findall(r"url\(['\"]?([^)'"]+)", (root / "styles.css").read_text()):
    if not urlsplit(ref).scheme and not (root / ref).is_file(): errors.append("CSS asset missing: " + ref)
js = (root / "app.js").read_text()
if re.search(r"(?:push|track)\(\s*['\"]lead['\"]", js): errors.append("Review must not fire lead")
if errors: raise SystemExit("\n".join(errors))
print("PASS: four pages, local references, single H1 per page, noindex, CSS assets and no lead conversion.")

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import re
import base64
import hashlib

ROOT = Path(__file__).resolve().parents[1]
PAGES = ("index.html", "brand/index.html", "ads/index.html", "review/index.html", "404.html")
REQUIRED_ASSETS = (
    "assets/logo-bdm-original.webp",
    "assets/campanha-representante-vertical.webp",
    "assets/bdm-hero-960.webp",
    "assets/bdm-hero-1920.webp",
    "assets/bdm-hero-3840.webp",
    "assets/bdm-hero-7680.webp",
    "assets/bdm-hero-mobile-720.webp",
    "assets/bdm-hero-mobile-1440.webp",
    "assets/campanha-rede-quadrada.webp",
    "assets/campanha-ponto-de-apoio.webp",
    "assets/fonts/montserrat-regular.woff",
    "assets/fonts/montserrat-bold.woff",
)
ERRORS = []

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs, self.h1, self.noindex, self.title = [], 0, False, 0
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "h1": self.h1 += 1
        if tag == "title": self.title += 1
        if tag == "meta" and attrs.get("name") == "robots":
            self.noindex = "noindex" in attrs.get("content", "") and "nofollow" in attrs.get("content", "")
        for key in ("src", "href"):
            if key in attrs: self.refs.append(attrs[key])

for name in PAGES:
    path = ROOT / name
    if not path.is_file():
        ERRORS.append(f"Missing page: {name}")
        continue
    doc = Page()
    source = path.read_text(encoding="utf-8")
    doc.feed(source)
    if doc.h1 != 1: ERRORS.append(f"{name}: expected one H1")
    expected_noindex = name != "index.html"
    if doc.noindex != expected_noindex: ERRORS.append(f"{name}: unexpected robots indexability")
    if doc.title != 1: ERRORS.append(f"{name}: title missing or repeated")
    for ref in doc.refs:
        url = urlsplit(ref)
        if url.scheme or url.netloc or not url.path: continue
        if url.path.startswith("/bdm_performance/"):
            target = (ROOT / unquote(url.path.removeprefix("/bdm_performance/"))).resolve()
        elif url.path.startswith("/"):
            target = (ROOT / unquote(url.path.lstrip("/"))).resolve()
        else:
            target = (path.parent / unquote(url.path)).resolve()
        if not target.is_relative_to(ROOT):
            ERRORS.append(f"{name}: path escapes root: {ref}")
            continue
        if target.is_dir(): target /= "index.html"
        if not target.is_file(): ERRORS.append(f"{name}: missing local reference {ref}")

for asset in REQUIRED_ASSETS:
    if not (ROOT / asset).is_file(): ERRORS.append(f"Missing required asset: {asset}")


css = (ROOT / "styles.css").read_text(encoding="utf-8")
if "--green: #00ab58" not in css.lower(): ERRORS.append("Brand green token missing")
if "@keyframes hero-diagnostic-glow" not in css: ERRORS.append("Subtle desktop hero glow is missing")
if ".hero::after { display: none; }" not in css: ERRORS.append("Mobile hero glow must be disabled")
home = (ROOT / "index.html").read_text(encoding="utf-8")
if '<video' in home.lower() or 'class="hero-image"' not in home or 'bdm-hero-7680.webp 7680w' not in home or 'bdm-hero-mobile-1440.webp 1440w' not in home:
    ERRORS.append("Responsive image hero missing or video remains")
if "Criado por Veltrus" not in home: ERRORS.append("Veltrus production credit missing")
if "default-src 'none'; script-src 'self'" not in home or "object-src 'none'" not in home:
    ERRORS.append("Restrictive CSP missing")
for name in ("styles.css", "app.js"):
    digest = base64.b64encode(hashlib.sha384((ROOT / name).read_bytes()).digest()).decode("ascii")
    if f'integrity="sha384-{digest}"' not in home:
        ERRORS.append(f"SRI missing or mismatched for {name}")
if "@layer" not in css or "prefers-reduced-motion" not in css: ERRORS.append("CSS layer structure or reduced-motion support missing")
if css.count("{") != css.count("}"): ERRORS.append("CSS braces are unbalanced")
if "focus-visible" not in css: ERRORS.append("Visible keyboard focus styles missing")
for font in ("assets/fonts/montserrat-regular.woff", "assets/fonts/montserrat-bold.woff"):
    if not (ROOT / font).is_file(): ERRORS.append(f"Missing local font: {font}")
if re.search(r"#(?:e50000|ed1c24|e31b23)|--red|--v4-red", css, re.I): ERRORS.append("Legacy red brand token remains in CSS")
if "wa.me/5544988018242" not in (ROOT / "index.html").read_text(encoding="utf-8"): ERRORS.append("Official WhatsApp CTA missing")
js = (ROOT / "app.js").read_text(encoding="utf-8")
for module in ("modules/navigation.js", "modules/testimonials.js", "modules/attribution.js"):
    source = (ROOT / module).read_text(encoding="utf-8")
    if "fetch(" in source or "XMLHttpRequest" in source or "sendBeacon(" in source:
        ERRORS.append(f"Unexpected network transmission code in {module}")
if 'type="module"' not in home: ERRORS.append("Module entrypoint missing")
if (ROOT / "assets/hero-bdm-performance.avif").exists(): ERRORS.append("Conceptual AI hero asset remains in project")
if ERRORS: raise SystemExit("\n".join(ERRORS))
print("PASS: 5 pages, responsive 8K hero, credit, CSP, SRI, module entrypoint, identity and WhatsApp CTA.")

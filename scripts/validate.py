from html.parser import HTMLParser
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
ERRORS = []

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.h1 = 0
        self.title = 0
        self.img = 0
        self.picture = 0
        self.video = 0
        self.refs = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "h1":
            self.h1 += 1
        elif tag == "title":
            self.title += 1
        elif tag == "img":
            self.img += 1
        elif tag == "picture":
            self.picture += 1
        elif tag == "video":
            self.video += 1
        for key in ("src", "href"):
            if attrs.get(key):
                self.refs.append(attrs[key])

home_path = ROOT / "index.html"
css_path = ROOT / "styles.css"
js_path = ROOT / "app.js"

for path in (home_path, css_path, js_path, ROOT / "404.html", ROOT / "robots.txt", ROOT / "sitemap.xml"):
    if not path.is_file() or path.stat().st_size == 0:
        ERRORS.append(f"Missing or empty required file: {path.relative_to(ROOT)}")

if home_path.is_file():
    home = home_path.read_text(encoding="utf-8")
    page = Page()
    page.feed(home)

    if page.h1 != 1:
        ERRORS.append(f"Homepage must contain exactly one H1, found {page.h1}")
    if page.title != 1:
        ERRORS.append(f"Homepage must contain exactly one title, found {page.title}")
    if page.img or page.picture or page.video:
        ERRORS.append("Homepage must remain image-free and video-free")
    if "<svg" in home.lower() or "<canvas" in home.lower():
        ERRORS.append("Homepage must not use SVG or canvas artwork")

    required_html = (
        'id="partner-form"',
        'name="automotive_role"',
        'name="capital"',
        'name="lgpd"',
        'id="consent-banner"',
        'class="mobile-sticky-cta"',
        'href="#qualificacao"',
        "R$50 mil a R$150 mil",
        "Criado por Veltrus",
        "FAQPage",
        "img-src 'none'",
        "media-src 'none'",
    )
    for token in required_html:
        if token not in home:
            ERRORS.append(f"Missing homepage requirement: {token}")

    if home.count('href="#qualificacao"') < 4:
        ERRORS.append("Expected at least four qualification CTAs")

    schema_match = re.search(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', home, re.S)
    if not schema_match:
        ERRORS.append("Missing JSON-LD")
    else:
        try:
            schema = json.loads(schema_match.group(1))
            types = {item.get("@type") for item in schema.get("@graph", [])}
            if not {"Organization", "WebSite", "Service", "FAQPage"}.issubset(types):
                ERRORS.append("JSON-LD required types missing")
        except json.JSONDecodeError:
            ERRORS.append("Invalid JSON-LD")

if css_path.is_file():
    css = css_path.read_text(encoding="utf-8")
    required_css = (
        "--green:#57ff20",
        "@font-face",
        "prefers-reduced-motion",
        "focus-visible",
        ".benefit-grid",
        ".metric-rail",
        ".qualification-form",
    )
    compact = css.replace(" ", "").replace("\n", "")
    for token in required_css:
        target = token.replace(" ", "")
        if target not in compact and token not in css:
            ERRORS.append(f"Missing CSS requirement: {token}")

    forbidden = ("background-image:url(", "<svg", "data:image", ".hero-media", ".hero-image", ".fold-media")
    low = css.lower()
    for token in forbidden:
        if token.lower() in low:
            ERRORS.append(f"Legacy visual layer remains in CSS: {token}")

    if css.count("{") != css.count("}"):
        ERRORS.append("Unbalanced CSS braces")

if js_path.is_file():
    js = js_path.read_text(encoding="utf-8")
    for token in (
        "utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term",
        "gclid", "gbraid", "wbraid", "fbclid", "generate_lead", "bdm_partner_cta_click",
        "bdm_faq_open", "bdm_final_cta_view", "5518997553071", "bdm_measurement_consent",
    ):
        if token not in js:
            ERRORS.append(f"Missing conversion token in app.js: {token}")

    if "fetch(" in js or "XMLHttpRequest" in js or "sendBeacon(" in js:
        ERRORS.append("Unexpected network transmission code in app.js")

if ERRORS:
    raise SystemExit("\n".join(ERRORS))

print("PASS: clean image-free BDM landing page, conversion flow, SEO and responsive CSS validated.")

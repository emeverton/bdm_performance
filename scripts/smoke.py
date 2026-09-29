import os
import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

BASE = os.environ.get("BDM_BASE_URL", "https://emeverton.github.io/bdm_performance/").rstrip("/") + "/"
PATHS = ("", "styles.css", "app.js", "robots.txt", "sitemap.xml", "404.html")

def get(path):
    for attempt in range(6):
        try:
            req = Request(BASE + path, headers={"User-Agent": "BDM-Smoke/3.0"})
            with urlopen(req, timeout=15) as response:
                if response.status != 200:
                    raise RuntimeError(f"Unexpected HTTP {response.status}: {path}")
                body = response.read()
            if not body:
                raise RuntimeError(f"Empty response: {path}")
            print("HTTP 200:", BASE + path)
            return body
        except (HTTPError, URLError, RuntimeError) as error:
            if attempt == 5:
                raise SystemExit(str(error))
            time.sleep(4)

content = {path: get(path) for path in PATHS}
home = content[""].decode("utf-8")
css = content["styles.css"].decode("utf-8")
js = content["app.js"].decode("utf-8")

if home.lower().count("<h1") != 1:
    raise SystemExit("Homepage must contain exactly one H1")
if any(token in home.lower() for token in ("<img", "<picture", "<video", "<svg", "<canvas")):
    raise SystemExit("Published homepage is not image-free")
if "styles.css?v=clean2" not in home or "app.js?v=clean2" not in home:
    raise SystemExit("Published cache-busted entrypoints missing")
if 'id="partner-form"' not in home or home.count('href="#qualificacao"') < 4:
    raise SystemExit("Published conversion path missing")
if "img-src 'none'" not in home or "media-src 'none'" not in home:
    raise SystemExit("Published CSP does not enforce image-free presentation")
if "--green:#57ff20" not in css.replace(" ", "").replace("\n", ""):
    raise SystemExit("BDM neon token missing")
if ".hero-media" in css or ".hero-image" in css or ".fold-media" in css:
    raise SystemExit("Legacy visual CSS leaked into production")
for token in ("generate_lead", "bdm_partner_cta_click", "utm_source", "gclid", "5518997553071"):
    if token not in js:
        raise SystemExit("Conversion logic missing: " + token)

print("PASS: production serves the clean image-free BDM rebuild.")

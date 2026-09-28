import os
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

BASE = os.environ.get("BDM_BASE_URL", "https://emeverton.github.io/bdm_performance/").rstrip("/") + "/"
LOCAL_ROOT = Path(os.environ["BDM_LOCAL_ROOT"]).resolve() if os.environ.get("BDM_LOCAL_ROOT") else None
PAGES = ("", "brand/", "ads/", "review/")
ASSETS = (
    "styles.css", "app.js", "assets/logo-bdm-original.webp",
    "assets/campanha-representante-vertical.webp", "assets/campanha-rede-quadrada.webp",
    "assets/bdm-engine-hero.webp",
    "assets/campanha-ponto-de-apoio.webp",
    "assets/fonts/montserrat-regular.woff", "assets/fonts/montserrat-bold.woff",
    "assets/fonts/montserrat-regular.woff", "assets/fonts/montserrat-bold.woff",
)

def get(path):
    if LOCAL_ROOT:
        target = (LOCAL_ROOT / path / "index.html") if not path or path.endswith("/") else (LOCAL_ROOT / path)
        if not target.is_file(): raise SystemExit(f"Missing local resource: {path}")
        print("LOCAL 200:", path)
        return target.read_bytes()
    for attempt in range(6):
        try:
            req = Request(BASE + path, headers={"User-Agent": "BDM-Review-Smoke/2.0"})
            with urlopen(req, timeout=15) as response:
                if response.status != 200: raise RuntimeError(f"Unexpected HTTP {response.status}: {path}")
                data = response.read()
            if not data: raise RuntimeError(f"Empty response: {path}")
            print("HTTP 200:", BASE + path)
            return data
        except (HTTPError, URLError, RuntimeError) as error:
            if attempt == 5: raise SystemExit(str(error))
            time.sleep(5)

for path in PAGES:
    html = get(path).decode("utf-8")
    if path and "noindex,nofollow" not in html: raise SystemExit("Auxiliary route must remain noindex: " + path)
    if not path and "noindex,nofollow" in html: raise SystemExit("Homepage must remain indexable")
    if html.lower().count("<h1") != 1: raise SystemExit("Expected one H1: " + path)
for path in ASSETS:
    body = get(path)
    if path.endswith(".webp") and body[:4] != b"RIFF": raise SystemExit("Not a WebP asset: " + path)
css = get("styles.css").decode("utf-8").lower()
if "--green: #00ab58" not in css: raise SystemExit("BDM green token missing")
if "@layer" not in css or "prefers-reduced-motion" not in css: raise SystemExit("CSS structure or reduced-motion support missing")
if "bdm-engine-hero.webp" not in css: raise SystemExit("Landscape CGI hero background missing")
if "@keyframes engine-signal" not in css: raise SystemExit("Animated green engine signal missing")
if "<video" in get("").decode("utf-8").lower(): raise SystemExit("Hero video was not replaced by the landscape image")
if any(token in css for token in ("--red", "--v4-red", "#ed1c24", "#e31b23", "#e50000")):
    raise SystemExit("Legacy red brand token remains in published CSS")
js = get("app.js").decode("utf-8")
if "fetch(" in js or "XMLHttpRequest" in js or "sendBeacon(" in js: raise SystemExit("Unexpected network transmission")
print("PASS: public routes, indexability, BDM identity, responsive stylesheet and local asset delivery verified.")

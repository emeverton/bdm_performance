import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

BASE = "https://emeverton.github.io/bdm_performance/"
PAGES = ("", "brand/", "ads/", "review/")
ASSETS = (
    "styles.css", "app.js", "assets/logo-bdm-original.webp",
    "assets/campanha-representante-vertical.webp", "assets/campanha-rede-quadrada.webp",
    "assets/campanha-ponto-de-apoio.webp",
)

def get(path):
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
    if "noindex,nofollow" not in html: raise SystemExit("Review indexability guard missing: " + path)
    if html.lower().count("<h1") != 1: raise SystemExit("Expected one H1: " + path)
for path in ASSETS:
    body = get(path)
    if path.endswith(".webp") and body[:4] != b"RIFF": raise SystemExit("Not a WebP asset: " + path)
css = get("styles.css").decode("utf-8").lower()
if "--brand-green: #00ab58" not in css: raise SystemExit("BDM green token missing")
if any(token in css for token in ("--red", "--v4-red", "#ed1c24", "#e31b23", "#e50000")):
    raise SystemExit("Legacy red brand token remains in published CSS")
js = get("app.js").decode("utf-8")
if "fetch(" in js or "dataLayer" in js: raise SystemExit("Unexpected tracking/data transmission")
print("PASS: public routes, noindex, BDM green identity and original asset delivery verified.")

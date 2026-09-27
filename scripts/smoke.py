import hashlib
import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

BASE = 'https://emeverton.github.io/bdm_performance/'
PAGES = ('', 'brand/', 'ads/', 'review/')
ASSETS = {
    'assets/hero-bdm-performance.avif': '9be7235cc9abd132aec4ce43e300322b8751b69f81686c16a3733702176b47c9',
    'assets/logo-bdm-white.webp': 'e85f5ad270ed5335992a4bc761a40bb65007ade5c8d604f309871e58022f02cc',
}

def get(path):
    for attempt in range(6):
        try:
            request = Request(BASE + path, headers={'User-Agent': 'BDM-Deployment-Verification/1.0'})
            with urlopen(request, timeout=15) as response:
                if response.status != 200:
                    raise RuntimeError('Unexpected HTTP status')
                data = response.read()
            if not data:
                raise RuntimeError('Empty response')
            print('HTTP 200:', BASE + path)
            return data
        except (HTTPError, URLError, RuntimeError) as error:
            if attempt == 5:
                raise SystemExit(str(error))
            time.sleep(5)

for path in PAGES:
    html = get(path).decode('utf-8')
    if 'noindex,nofollow' not in html:
        raise SystemExit('Review indexability guard missing: ' + path)
    if html.lower().count('<h1') != 1:
        raise SystemExit('Expected one H1: ' + path)
css = get('styles.css')
js = get('app.js').decode('utf-8')
if 'preview_form_submit' not in js:
    raise SystemExit('Expected demo-only form')
for path, expected in ASSETS.items():
    if hashlib.sha256(get(path)).hexdigest() != expected:
        raise SystemExit('Deployed asset integrity mismatch: ' + path)
print('PASS: public HTTPS routes, CSS, JavaScript, noindex and asset integrity verified.')

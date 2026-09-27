from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import re

root = Path(__file__).resolve().parents[1]
errors = []

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []
        self.h1 = 0
        self.noindex = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'h1':
            self.h1 += 1
        if tag == 'meta' and attrs.get('name') == 'robots':
            self.noindex = 'noindex' in attrs.get('content', '')
        for key in ('src', 'href'):
            if key in attrs:
                self.refs.append(attrs[key])

for name in ('index.html', 'brand/index.html', 'ads/index.html', 'review/index.html'):
    path = root / name
    doc = Page()
    doc.feed(path.read_text(encoding='utf-8'))
    if doc.h1 != 1:
        errors.append(name + ': expected one H1')
    if not doc.noindex:
        errors.append(name + ': review noindex missing')
    for ref in doc.refs:
        url = urlsplit(ref)
        if url.scheme or url.netloc or not url.path:
            continue
        target = (path.parent / unquote(url.path)).resolve()
        if not target.is_relative_to(root):
            errors.append('Path outside site: ' + ref)
            continue
        if target.is_dir():
            target = target / 'index.html'
        if not target.is_file():
            errors.append(name + ': missing ' + ref)

for raw in re.findall(r'url\((.*?)\)', (root / 'styles.css').read_text()):
    ref = raw.strip().strip(chr(34)).strip(chr(39))
    if not urlsplit(ref).scheme and not (root / ref).is_file():
        errors.append('CSS asset missing: ' + ref)

js = (root / 'app.js').read_text()
for quote in (chr(34), chr(39)):
    if quote + 'lead' + quote in js:
        errors.append('Review must not emit a real lead conversion')
if errors:
    raise SystemExit('\n'.join(errors))
print('PASS: four pages, one H1 per page, noindex, local assets and demo conversion safety.')

from pathlib import Path
import base64, hashlib, json
root = Path(__file__).resolve().parents[1]
for item in json.loads((root / '.asset-import/manifest.json').read_text()):
    encoded = ''.join((root / part).read_text().strip() for part in item['parts'])
    data = base64.b64decode(encoded, validate=True)
    if hashlib.sha256(data).hexdigest() != item['sha256']:
        raise SystemExit('Asset checksum mismatch: ' + item['path'])
    destination = root / item['path']
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)
    print('Verified:', item['path'], len(data), 'bytes')

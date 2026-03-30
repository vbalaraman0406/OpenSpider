import requests

base = 'https://f1-dot-vish-cloud.wl.r.appspot.com'

# Check vendor chunk
url = base + '/f1/assets/vendor-react-Bz0when3.js'
print(f'=== CHECKING {url} ===')
r = requests.get(url, timeout=15)
print(f'Status: {r.status_code}')
print(f'Content-Type: {r.headers.get("Content-Type")}')
print(f'Content-Length: {len(r.text)}')
if '<!DOCTYPE' in r.text[:200] or '<html' in r.text[:200]:
    print('*** FATAL: VENDOR JS RETURNING HTML! React cannot load! ***')
    print(f'First 300 chars: {r.text[:300]}')
else:
    print('Content looks like JS')
    print(f'First 200 chars: {r.text[:200]}')
    if 'createElement' in r.text:
        print('Contains createElement: YES (React core present)')
    if 'createRoot' in r.text:
        print('Contains createRoot: YES (ReactDOM present)')

# Also check local dist for all files
import os
dist_dir = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai/frontend/dist/assets'
print(f'\n=== LOCAL DIST FILES ===')
for f in sorted(os.listdir(dist_dir)):
    fpath = os.path.join(dist_dir, f)
    size = os.path.getsize(fpath)
    print(f'{f} ({size} bytes)')
    # Check if each file is accessible on GCP
    url = base + '/f1/assets/' + f
    r2 = requests.get(url, timeout=10)
    ct = r2.headers.get('Content-Type', '')
    is_html = '<!DOCTYPE' in r2.text[:100] or '<html' in r2.text[:100]
    status = 'HTML(BROKEN!)' if is_html else 'OK'
    print(f'  GCP: {r2.status_code} {ct} {status} ({len(r2.text)} bytes)')

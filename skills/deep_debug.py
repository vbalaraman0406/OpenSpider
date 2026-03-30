import requests
import re

base = 'https://f1-dot-vish-cloud.wl.r.appspot.com'

# 1. Fetch raw HTML
print('=== RAW HTML ===')
r = requests.get(base + '/f1/', timeout=15)
print(r.text)

# 2. Extract JS and CSS URLs
js_files = re.findall(r'src="([^"]*\.js)"', r.text)
css_files = re.findall(r'href="([^"]*\.css)"', r.text)
print(f'\nJS files: {js_files}')
print(f'CSS files: {css_files}')

# 3. Check JS bundle content type and first 500 chars
for js in js_files:
    url = base + js if js.startswith('/') else base + '/' + js
    print(f'\n=== JS: {url} ===')
    r2 = requests.get(url, timeout=15)
    print(f'Status: {r2.status_code}')
    print(f'Content-Type: {r2.headers.get("Content-Type")}')
    print(f'Content-Length: {len(r2.text)}')
    # Check if it contains createRoot
    if 'createRoot' in r2.text:
        print('Contains createRoot: YES')
    else:
        print('Contains createRoot: NO')
    # Check for Pitwall.ai text
    if 'Pitwall.ai' in r2.text:
        print('Contains Pitwall.ai: YES')
    else:
        print('Contains Pitwall.ai: NO')
    # Check for error indicators
    if '<!DOCTYPE' in r2.text or '<html' in r2.text:
        print('*** FATAL: JS file contains HTML! ***')
    print(f'First 500 chars: {r2.text[:500]}')

# 4. Check CSS
for css in css_files:
    url = base + css if css.startswith('/') else base + '/' + css
    print(f'\n=== CSS: {url} ===')
    r3 = requests.get(url, timeout=15)
    print(f'Status: {r3.status_code}')
    print(f'Content-Type: {r3.headers.get("Content-Type")}')
    print(f'Content-Length: {len(r3.text)}')
    if '<!DOCTYPE' in r3.text or '<html' in r3.text:
        print('*** FATAL: CSS file contains HTML! ***')
    print(f'First 300 chars: {r3.text[:300]}')

# 5. Check local index.html for comparison
print('\n=== LOCAL INDEX.HTML ===')
try:
    with open('/Users/vbalaraman/OpenSpider/workspace/pitwall-ai/frontend/dist/index.html', 'r') as f:
        local_html = f.read()
    print(local_html)
except Exception as e:
    print(f'Error: {e}')

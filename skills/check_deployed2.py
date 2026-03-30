import requests
import re

base = 'https://f1-dot-vish-cloud.wl.r.appspot.com'

print('=== FETCHING /f1/ ===')
r = requests.get(base + '/f1/', timeout=15)
print(f'Status: {r.status_code}')
print(f'Content-Type: {r.headers.get("Content-Type")}')
html = r.text
css_files = re.findall(r'href="([^"]*\.css)"', html)
js_files = re.findall(r'src="([^"]*\.js)"', html)
print(f'CSS files: {css_files}')
print(f'JS files: {js_files}')
root_match = re.search(r'<div id="root">(.*?)</div>', html, re.DOTALL)
if root_match:
    print(f'#root content: "{root_match.group(1).strip()}" (len={len(root_match.group(1).strip())})')
else:
    print('#root div NOT FOUND')
print(f'HTML length: {len(html)}')
print('--- HTML (first 800) ---')
print(html[:800])

for f in css_files + js_files:
    url = base + f if f.startswith('/') else base + '/f1/' + f
    print(f'\n=== CHECKING {url} ===')
    r2 = requests.get(url, timeout=15)
    ct = r2.headers.get('Content-Type', '')
    print(f'Status: {r2.status_code}')
    print(f'Content-Type: {ct}')
    print(f'First 300 chars: {r2.text[:300]}')
    if 'text/html' in ct and (f.endswith('.js') or f.endswith('.css')):
        print('*** FATAL: Asset returning HTML instead of JS/CSS! SPA catch-all intercepting! ***')

print('\n=== CHECKING /f1/api/health ===')
r3 = requests.get(base + '/f1/api/health', timeout=15)
print(f'Status: {r3.status_code}')
print(f'Content-Type: {r3.headers.get("Content-Type")}')
print(f'Body: {r3.text[:500]}')

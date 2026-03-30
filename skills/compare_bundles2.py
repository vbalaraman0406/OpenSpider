import requests
import os
import re

# Fetch deployed index.html
url = 'https://f1-dot-vish-cloud.wl.r.appspot.com/f1/'
resp = requests.get(url, timeout=30)
deployed_html = resp.text

print('=== DEPLOYED index.html (first 500 chars) ===')
print(deployed_html[:500])

# Extract JS/CSS filenames
deployed_js = re.findall(r'index-[^"]+\.js', deployed_html)
deployed_css = re.findall(r'index-[^"]+\.css', deployed_html)
print(f'\nDeployed JS: {deployed_js}')
print(f'Deployed CSS: {deployed_css}')

# Local index.html
local_path = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai/frontend/dist/index.html'
with open(local_path) as f:
    local_html = f.read()
local_js = re.findall(r'index-[^"]+\.js', local_html)
local_css = re.findall(r'index-[^"]+\.css', local_html)
print(f'\nLocal JS: {local_js}')
print(f'Local CSS: {local_css}')

print(f'\nJS MATCH: {deployed_js == local_js}')
print(f'CSS MATCH: {deployed_css == local_css}')

# Fetch deployed JS bundle and check content
if deployed_js:
    js_url = f'https://f1-dot-vish-cloud.wl.r.appspot.com/f1/assets/{deployed_js[0]}'
    resp2 = requests.get(js_url, timeout=30)
    js_content = resp2.text
    print(f'\nDeployed JS size: {len(js_content)} chars')
    print(f'Contains MINIMAL_TEST: {"MINIMAL_TEST" in js_content}')
    print(f'Contains Dashboard: {"Dashboard" in js_content}')
    print(f'Contains Navbar: {"Navbar" in js_content}')
    print(f'Contains BrowserRouter: {"BrowserRouter" in js_content}')
    print(f'Contains basename: {"basename" in js_content}')
    print(f'Contains createBrowserRouter: {"createBrowserRouter" in js_content}')
    if 'MINIMAL_TEST' in js_content:
        idx = js_content.index('MINIMAL_TEST')
        print(f'\nMINIMAL_TEST context: ...{js_content[max(0,idx-100):idx+100]}...')

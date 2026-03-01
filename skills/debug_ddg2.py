import urllib.request
import urllib.parse
import ssl
import re

ssl._create_default_https_context = ssl._create_unverified_context

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

q = 'bathroom remodel contractors Vancouver WA 98662'
url = f'https://html.duckduckgo.com/html/?q={urllib.parse.quote(q)}'
req = urllib.request.Request(url, headers=headers)
resp = urllib.request.urlopen(req, timeout=15)
html = resp.read().decode('utf-8', errors='ignore')

# Save first 5000 chars
with open('ddg_debug.html', 'w') as f:
    f.write(html)

# Look for any links and patterns
print(f'HTML length: {len(html)}')
print(f'Contains "result": {"result" in html}')
print(f'Contains "web-result": {"web-result" in html}')
print(f'Contains "links_main": {"links_main" in html}')

# Find all href patterns
hrefs = re.findall(r'href="([^"]+)"', html)
print(f'\nTotal hrefs: {len(hrefs)}')
for h in hrefs[:30]:
    print(f'  {h[:120]}')

# Find class attributes
classes = re.findall(r'class="([^"]+)"', html)
unique_classes = list(set(classes))
print(f'\nUnique classes ({len(unique_classes)}):')
for c in sorted(unique_classes)[:40]:
    print(f'  {c}')

# Print a chunk around first occurrence of any contractor-like text
for keyword in ['contractor', 'remodel', 'bathroom', 'plumb']:
    idx = html.lower().find(keyword)
    if idx > 0:
        print(f'\nFound "{keyword}" at {idx}:')
        print(html[max(0,idx-100):idx+200])
        break

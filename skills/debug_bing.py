import urllib.request
import re

url = 'https://www.bing.com/search?q=bathroom+remodel+contractors+Vancouver+WA+98662+reviews'
req = urllib.request.Request(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'en-US,en;q=0.9'
})
resp = urllib.request.urlopen(req, timeout=15)
html = resp.read().decode('utf-8', errors='replace')

# Print all unique class names containing 'algo' or 'result' or 'li_'
classes = set(re.findall(r'class="([^"]*?)"', html))
for c in sorted(classes):
    if any(k in c.lower() for k in ['algo','result','item','snippet','title','link','caption','desc']):
        print(f'CLASS: {c}')

print('\n--- First 3000 chars of body ---')
body_match = re.search(r'<body[^>]*>(.*)', html, re.DOTALL)
if body_match:
    print(body_match.group(1)[:3000])
else:
    print(html[:3000])

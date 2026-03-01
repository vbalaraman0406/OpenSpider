import urllib.request
import re
import html
import json

url = 'https://www.instagram.com/reel/DVWEXdQEp-B/?igsh=MWloYWEzOG8zY2pvcQ=='

req = urllib.request.Request(url, headers={
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
})

try:
    resp = urllib.request.urlopen(req, timeout=15)
    page = resp.read().decode('utf-8', errors='replace')
except Exception as e:
    print(f'Error fetching: {e}')
    page = ''

if page:
    # Extract meta tags
    meta_pattern = re.compile(r'<meta\s+[^>]*?(?:property|name)=["\']([^"\']*)["\'\s][^>]*?content=["\']([^"\']*)["\']', re.IGNORECASE)
    meta_pattern2 = re.compile(r'<meta\s+[^>]*?content=["\']([^"\']*)["\']\s+[^>]*?(?:property|name)=["\']([^"\']*)["\']', re.IGNORECASE)
    
    metas = {}
    for m in meta_pattern.finditer(page):
        metas[m.group(1)] = html.unescape(m.group(2))
    for m in meta_pattern2.finditer(page):
        metas[m.group(2)] = html.unescape(m.group(1))
    
    print('=== META TAGS ===')
    for k, v in metas.items():
        print(f'{k}: {v}')
    
    # Extract title
    title_match = re.search(r'<title>([^<]+)</title>', page)
    if title_match:
        print(f'\n=== TITLE ===\n{html.unescape(title_match.group(1))}')
    
    # Look for JSON-LD
    jsonld = re.findall(r'<script type=["\']application/ld\+json["\']>([^<]+)</script>', page)
    if jsonld:
        print('\n=== JSON-LD ===')
        for j in jsonld:
            try:
                parsed = json.loads(j)
                print(json.dumps(parsed, indent=2)[:2000])
            except:
                print(j[:2000])
    
    # Look for additional data in scripts
    # Instagram sometimes embeds data in window._sharedData or similar
    shared = re.search(r'window\._sharedData\s*=\s*({.*?});', page)
    if shared:
        print('\n=== SHARED DATA (truncated) ===')
        try:
            data = json.loads(shared.group(1))
            print(json.dumps(data, indent=2)[:2000])
        except:
            print(shared.group(1)[:2000])
    
    # Also check for __additionalDataLoaded or similar
    additional = re.search(r'window\.__additionalDataLoaded\s*\([^,]+,\s*({.*?})\s*\)', page)
    if additional:
        print('\n=== ADDITIONAL DATA (truncated) ===')
        print(additional.group(1)[:2000])
    
    # Check page length
    print(f'\n=== Page length: {len(page)} chars ===')
    
    # If very little extracted, print a snippet of the page
    if len(metas) < 3:
        print('\n=== PAGE SNIPPET (first 3000 chars) ===')
        print(page[:3000])
else:
    print('No page content retrieved.')

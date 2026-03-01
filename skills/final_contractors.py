import urllib.request
import json
import re
from html.parser import HTMLParser

# Try multiple Thumbtack URLs with redirect following
urls = [
    'https://www.thumbtack.com/wa/vancouver/bathroom-remodeling/',
    'https://www.thumbtack.com/wa/vancouver/tile-installation/',
    'https://www.thumbtack.com/wa/vancouver/bathroom-remodeling/near-me/',
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

for url in urls:
    print(f'\n--- Trying: {url} ---')
    try:
        req = urllib.request.Request(url, headers=headers)
        # Create opener that follows redirects
        opener = urllib.request.build_opener(urllib.request.HTTPRedirectHandler)
        resp = opener.open(req, timeout=15)
        html = resp.read().decode('utf-8', errors='ignore')
        print(f'Status: {resp.status}, Length: {len(html)}')
        
        # Look for JSON-LD
        ld_matches = re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.DOTALL)
        if ld_matches:
            for i, m in enumerate(ld_matches):
                try:
                    data = json.loads(m)
                    print(f'JSON-LD block {i}: type={data.get("@type", "unknown")}')
                    if isinstance(data, dict) and data.get('@type') == 'ItemList':
                        items = data.get('itemListElement', [])
                        for item in items[:15]:
                            li = item.get('item', {})
                            name = li.get('name', 'N/A')
                            rating = li.get('aggregateRating', {}).get('ratingValue', 'N/A')
                            reviews = li.get('aggregateRating', {}).get('reviewCount', 'N/A')
                            url_c = li.get('url', 'N/A')
                            print(f'  - {name} | Rating: {rating} | Reviews: {reviews} | URL: {url_c}')
                    elif isinstance(data, list):
                        for d in data:
                            if d.get('@type') in ['LocalBusiness', 'HomeAndConstructionBusiness', 'Service']:
                                print(f'  - {d.get("name")} | Rating: {d.get("aggregateRating",{}).get("ratingValue","N/A")}')
                except json.JSONDecodeError:
                    print(f'JSON-LD block {i}: parse error')
        else:
            print('No JSON-LD found')
            # Try to find contractor names in page
            names = re.findall(r'"name"\s*:\s*"([^"]+)"', html)
            ratings = re.findall(r'"ratingValue"\s*:\s*"?([\d.]+)', html)
            print(f'Found {len(names)} names, {len(ratings)} ratings in raw JSON')
            for n in names[:20]:
                if len(n) > 3 and len(n) < 60:
                    print(f'  Name: {n}')
            # Also look for __NEXT_DATA__
            next_match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
            if next_match:
                print('Found __NEXT_DATA__, parsing...')
                try:
                    nd = json.loads(next_match.group(1))
                    # Navigate to find pros
                    props = nd.get('props', {}).get('pageProps', {})
                    print(f'pageProps keys: {list(props.keys())[:10]}')
                    # Look for any list of pros
                    for k, v in props.items():
                        if isinstance(v, list) and len(v) > 0:
                            print(f'  List key "{k}": {len(v)} items')
                            if isinstance(v[0], dict):
                                print(f'    First item keys: {list(v[0].keys())[:8]}')
                except:
                    print('Failed to parse __NEXT_DATA__')
        break  # Stop after first successful URL
    except Exception as e:
        print(f'Error: {e}')

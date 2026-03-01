import urllib.request
import json
import re
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

urls = {
    'bathroom': 'https://www.thumbtack.com/wa/vancouver/bathroom-remodeling/',
    'tile': 'https://www.thumbtack.com/wa/vancouver/tile-installation/'
}

all_contractors = {}

for label, url in urls.items():
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'identity',
            'Connection': 'keep-alive',
        })
        resp = urllib.request.urlopen(req, timeout=15)
        html = resp.read().decode('utf-8', errors='ignore')
        print(f'{label}: fetched {len(html)} bytes')
        
        # Extract JSON-LD
        ld_blocks = re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.DOTALL)
        for block in ld_blocks:
            try:
                data = json.loads(block)
                items = []
                if isinstance(data, list):
                    items = data
                elif isinstance(data, dict) and data.get('@type') == 'ItemList':
                    items = data.get('itemListElement', [])
                elif isinstance(data, dict):
                    items = [data]
                for item in items:
                    actual = item.get('item', item)
                    name = actual.get('name', '')
                    if not name:
                        continue
                    rating_obj = actual.get('aggregateRating', {})
                    rating = rating_obj.get('ratingValue', 'N/A')
                    reviews = rating_obj.get('reviewCount', 'N/A')
                    if name not in all_contractors:
                        all_contractors[name] = {
                            'rating': rating,
                            'reviews': reviews,
                            'hires': 'N/A',
                            'price': 'N/A',
                            'specialties': label
                        }
                    else:
                        if label not in all_contractors[name]['specialties']:
                            all_contractors[name]['specialties'] += f', {label}'
            except:
                pass
        
        # Try __NEXT_DATA__
        nd = re.search(r'<script[^>]*id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
        if nd:
            try:
                ndata = json.loads(nd.group(1))
                props = ndata.get('props', {}).get('pageProps', {})
                # Search for proListSection
                fd = props.get('frontDoorPage', {})
                pls = fd.get('proListSection', {})
                pros = pls.get('pros', [])
                print(f'{label}: found {len(pros)} pros in __NEXT_DATA__')
                for p in pros:
                    name = p.get('businessName', p.get('name', ''))
                    if not name:
                        continue
                    r = p.get('rating', p.get('averageRating', 'N/A'))
                    rc = p.get('numReviews', p.get('reviewCount', 'N/A'))
                    h = p.get('numHires', p.get('hireCount', 'N/A'))
                    pr = p.get('priceEstimate', p.get('startingCost', 'N/A'))
                    if name not in all_contractors:
                        all_contractors[name] = {'rating': r, 'reviews': rc, 'hires': h, 'price': pr, 'specialties': label}
                    else:
                        if h != 'N/A':
                            all_contractors[name]['hires'] = h
                        if pr != 'N/A':
                            all_contractors[name]['price'] = pr
            except Exception as e:
                print(f'NEXT_DATA parse error: {e}')
    except Exception as e:
        print(f'Failed {label}: {e}')

print(f'\nTotal: {len(all_contractors)} contractors\n')
print('| Company Name | Rating | Reviews | Hires | Price Range | Specialties |')
print('|---|---|---|---|---|---|')
for name, d in sorted(all_contractors.items(), key=lambda x: float(x[1]['rating']) if x[1]['rating'] not in ('N/A', None) else 0, reverse=True):
    print(f"| {name} | {d['rating']} | {d['reviews']} | {d['hires']} | {d['price']} | {d['specialties']} |")

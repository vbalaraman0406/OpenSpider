import requests
import json
import re

urls = [
    'https://www.thumbtack.com/wa/vancouver/bathroom-remodeling/',
    'https://www.thumbtack.com/wa/vancouver/tile-installation/'
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

all_contractors = {}

for url in urls:
    try:
        r = requests.get(url, headers=headers, timeout=30)
        print(f'URL: {url} -> Status: {r.status_code}, Length: {len(r.text)}')
        
        # Extract JSON-LD
        ld_matches = re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', r.text, re.DOTALL)
        for m in ld_matches:
            try:
                data = json.loads(m)
                if isinstance(data, dict) and data.get('@type') == 'ItemList':
                    items = data.get('itemListElement', [])
                    for item in items:
                        li = item.get('item', {})
                        name = li.get('name', 'Unknown')
                        rating = li.get('aggregateRating', {}).get('ratingValue', 'N/A')
                        reviews = li.get('aggregateRating', {}).get('reviewCount', 'N/A')
                        if name not in all_contractors:
                            all_contractors[name] = {'rating': rating, 'reviews': reviews, 'hires': 'N/A', 'price': 'N/A', 'specialties': 'N/A'}
            except:
                pass
        
        # Extract __NEXT_DATA__
        nd = re.search(r'<script[^>]*id="__NEXT_DATA__"[^>]*>(.*?)</script>', r.text, re.DOTALL)
        if nd:
            try:
                ndata = json.loads(nd.group(1))
                # Walk the JSON to find pro results
                def find_pros(obj, depth=0):
                    if depth > 15:
                        return
                    if isinstance(obj, dict):
                        # Check for numHires or hireCount
                        nm = obj.get('businessName') or obj.get('name') or obj.get('displayName')
                        hires = obj.get('numHires') or obj.get('hireCount') or obj.get('num_hires')
                        if nm and hires:
                            if nm in all_contractors:
                                all_contractors[nm]['hires'] = hires
                            else:
                                all_contractors[nm] = {'rating': 'N/A', 'reviews': 'N/A', 'hires': hires, 'price': 'N/A', 'specialties': 'N/A'}
                        # Check for price
                        price = obj.get('priceEstimate') or obj.get('startingCost') or obj.get('price')
                        if nm and price:
                            if nm in all_contractors:
                                all_contractors[nm]['price'] = price
                        # Check for specialties/services
                        specs = obj.get('services') or obj.get('specialties') or obj.get('categoryName')
                        if nm and specs:
                            if nm in all_contractors:
                                all_contractors[nm]['specialties'] = specs
                        for v in obj.values():
                            find_pros(v, depth+1)
                    elif isinstance(obj, list):
                        for item in obj:
                            find_pros(item, depth+1)
                find_pros(ndata)
            except Exception as e:
                print(f'NEXT_DATA parse error: {e}')
    except Exception as e:
        print(f'Error fetching {url}: {e}')

print(f'\nTotal contractors found: {len(all_contractors)}')
print('\n--- RESULTS ---')
for name, info in sorted(all_contractors.items()):
    print(f"{name} | {info['rating']} | {info['reviews']} | {info['hires']} | {info['price']} | {info['specialties']}")

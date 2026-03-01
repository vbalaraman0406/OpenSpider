import urllib.request
import json
import re
from html.parser import HTMLParser

urls = {
    'bathroom': 'https://www.thumbtack.com/wa/vancouver/bathroom-remodeling/',
    'tile': 'https://www.thumbtack.com/wa/vancouver/tile-installation/'
}

all_contractors = {}

for label, url in urls.items():
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'})
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        html = resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f'Failed to fetch {label}: {e}')
        continue

    # Extract JSON-LD
    jsonld_pattern = r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>'
    for m in re.finditer(jsonld_pattern, html, re.DOTALL):
        try:
            data = json.loads(m.group(1))
            if isinstance(data, dict) and data.get('@type') == 'ItemList':
                for item in data.get('itemListElement', []):
                    it = item.get('item', {})
                    name = it.get('name', 'Unknown')
                    rating = it.get('aggregateRating', {}).get('ratingValue', 'N/A')
                    reviews = it.get('aggregateRating', {}).get('reviewCount', 'N/A')
                    if name not in all_contractors:
                        all_contractors[name] = {'rating': rating, 'reviews': reviews, 'hires': 'N/A', 'price': 'N/A', 'specialties': label, 'source': label}
                    else:
                        all_contractors[name]['specialties'] += f', {label}'
        except:
            pass

    # Extract __NEXT_DATA__ for hires/price
    next_match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
    if next_match:
        try:
            nd = json.loads(next_match.group(1))
            props = nd.get('props', {}).get('pageProps', {})
            # Try to find proListSection
            fdp = props.get('frontDoorPage', {})
            pls = fdp.get('proListSection', {})
            pros = pls.get('pros', [])
            if not pros:
                # Try other paths
                for key in ['proList', 'results', 'professionals']:
                    pros = pls.get(key, [])
                    if pros:
                        break
            if not pros:
                # Recursive search for numHires
                def find_pros(obj, depth=0):
                    results = []
                    if depth > 8:
                        return results
                    if isinstance(obj, dict):
                        if 'numHires' in obj or 'hireCount' in obj:
                            results.append(obj)
                        for v in obj.values():
                            results.extend(find_pros(v, depth+1))
                    elif isinstance(obj, list):
                        for v in obj:
                            results.extend(find_pros(v, depth+1))
                    return results
                pros = find_pros(props)
            
            for p in pros:
                name = p.get('businessName', p.get('name', p.get('serviceName', '')))
                hires = p.get('numHires', p.get('hireCount', 'N/A'))
                price = p.get('instantBookPrice', p.get('price', p.get('priceEstimate', 'N/A')))
                if isinstance(price, dict):
                    price = price.get('formattedPrice', price.get('displayPrice', str(price)))
                if name and name in all_contractors:
                    all_contractors[name]['hires'] = hires
                    if price != 'N/A':
                        all_contractors[name]['price'] = price
                elif name:
                    rating_v = p.get('rating', p.get('averageRating', 'N/A'))
                    rev_c = p.get('numReviews', p.get('reviewCount', 'N/A'))
                    all_contractors[name] = {'rating': rating_v, 'reviews': rev_c, 'hires': hires, 'price': price, 'specialties': label, 'source': label}
        except Exception as e:
            print(f'NEXT_DATA parse error for {label}: {e}')

print(f'\nTotal unique contractors found: {len(all_contractors)}\n')
print('| Company Name | Rating | Reviews | Hires | Price Range | Specialties |')
print('|---|---|---|---|---|---|')
for name, info in sorted(all_contractors.items(), key=lambda x: float(x[1]['rating']) if str(x[1]['rating']).replace('.','').isdigit() else 0, reverse=True):
    print(f"| {name} | {info['rating']} | {info['reviews']} | {info['hires']} | {info['price']} | {info['specialties']} |")

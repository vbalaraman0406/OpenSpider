import json, re

with open('/tmp/thumbtack.html', 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

print(f'HTML length: {len(html)}')

# Extract JSON-LD
jsonld_matches = re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.DOTALL)
print(f'JSON-LD blocks found: {len(jsonld_matches)}')

contractors = []

for i, block in enumerate(jsonld_matches):
    try:
        data = json.loads(block)
        if isinstance(data, list):
            for item in data:
                if item.get('@type') == 'LocalBusiness' or item.get('@type') == 'HomeAndConstructionBusiness':
                    name = item.get('name', 'N/A')
                    rating = item.get('aggregateRating', {}).get('ratingValue', 'N/A')
                    reviews = item.get('aggregateRating', {}).get('reviewCount', 'N/A')
                    contractors.append({'name': name, 'rating': rating, 'reviews': reviews})
        elif isinstance(data, dict):
            if data.get('@type') in ['LocalBusiness', 'HomeAndConstructionBusiness']:
                name = data.get('name', 'N/A')
                rating = data.get('aggregateRating', {}).get('ratingValue', 'N/A')
                reviews = data.get('aggregateRating', {}).get('reviewCount', 'N/A')
                contractors.append({'name': name, 'rating': rating, 'reviews': reviews})
            elif data.get('@type') == 'ItemList':
                for elem in data.get('itemListElement', []):
                    item = elem.get('item', elem)
                    name = item.get('name', 'N/A')
                    ar = item.get('aggregateRating', {})
                    rating = ar.get('ratingValue', 'N/A') if ar else 'N/A'
                    reviews = ar.get('reviewCount', 'N/A') if ar else 'N/A'
                    contractors.append({'name': name, 'rating': rating, 'reviews': reviews})
            # Print raw for debug
            print(f'JSON-LD block {i} type: {data.get("@type", "unknown")}')
    except json.JSONDecodeError:
        print(f'JSON-LD block {i}: parse error')

print(f'\nContractors from JSON-LD: {len(contractors)}')
for c in contractors[:15]:
    print(f"  {c['name']} | Rating: {c['rating']} | Reviews: {c['reviews']}")

# Also try __NEXT_DATA__
next_match = re.search(r'<script[^>]*id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
if next_match:
    try:
        nd = json.loads(next_match.group(1))
        # Navigate to find pros
        props = nd.get('props', {}).get('pageProps', {})
        results = props.get('searchResults', props.get('results', props.get('pros', [])))
        if isinstance(results, list):
            print(f'\n__NEXT_DATA__ results: {len(results)}')
            for r in results[:3]:
                print(json.dumps(r, indent=2)[:500])
        elif isinstance(results, dict):
            # Try to find list inside
            for k, v in results.items():
                if isinstance(v, list) and len(v) > 0:
                    print(f'\n__NEXT_DATA__ key "{k}": {len(v)} items')
                    print(json.dumps(v[0], indent=2)[:500])
                    break
        else:
            print(f'\n__NEXT_DATA__ pageProps keys: {list(props.keys())[:20]}')
    except:
        print('__NEXT_DATA__ parse error')
else:
    print('No __NEXT_DATA__ found')

import json, re
from html.parser import HTMLParser

def extract_data(filepath, category):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        html = f.read()
    
    contractors = []
    
    # Extract JSON-LD
    jsonld_pattern = r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>'
    matches = re.findall(jsonld_pattern, html, re.DOTALL)
    for m in matches:
        try:
            data = json.loads(m)
            if isinstance(data, list):
                for item in data:
                    if item.get('@type') == 'LocalBusiness':
                        contractors.append({
                            'name': item.get('name',''),
                            'rating': item.get('aggregateRating',{}).get('ratingValue','N/A'),
                            'reviews': item.get('aggregateRating',{}).get('reviewCount','N/A'),
                            'category': category
                        })
            elif isinstance(data, dict) and data.get('@type') == 'LocalBusiness':
                contractors.append({
                    'name': data.get('name',''),
                    'rating': data.get('aggregateRating',{}).get('ratingValue','N/A'),
                    'reviews': data.get('aggregateRating',{}).get('reviewCount','N/A'),
                    'category': category
                })
        except: pass
    
    # Extract __NEXT_DATA__
    next_match = re.search(r'<script[^>]*id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
    if next_match:
        try:
            nd = json.loads(next_match.group(1))
            # Search for pro data recursively
            def find_pros(obj, path=''):
                if isinstance(obj, dict):
                    # Look for numHires or hireCount
                    if 'businessName' in obj or 'serviceName' in obj:
                        name = obj.get('businessName', obj.get('serviceName', obj.get('name', '')))
                        if name:
                            rating = obj.get('rating', obj.get('averageRating', obj.get('overallRating', '')))
                            if isinstance(rating, dict):
                                rating = rating.get('ratingValue', rating.get('average', ''))
                            reviews = obj.get('numReviews', obj.get('reviewCount', obj.get('numRatings', '')))
                            hires = obj.get('numHires', obj.get('hireCount', obj.get('instantBookCount', '')))
                            price = obj.get('startingCost', obj.get('priceEstimate', obj.get('price', '')))
                            if isinstance(price, dict):
                                price = price.get('formattedPrice', price.get('displayPrice', str(price)))
                            return [{'name': name, 'rating': rating, 'reviews': reviews, 'hires': hires, 'price': price, 'path': path}]
                    results = []
                    for k, v in obj.items():
                        results.extend(find_pros(v, f'{path}.{k}'))
                    return results
                elif isinstance(obj, list):
                    results = []
                    for i, v in enumerate(obj):
                        results.extend(find_pros(v, f'{path}[{i}]'))
                    return results
                return []
            
            pros = find_pros(nd)
            print(f'Found {len(pros)} pros in __NEXT_DATA__ for {category}')
            for p in pros[:3]:
                print(f"  Sample: {p}")
            
            # Merge with contractors
            for p in pros:
                found = False
                for c in contractors:
                    if c['name'] == p['name']:
                        if p.get('hires'): c['hires'] = p['hires']
                        if p.get('price'): c['price'] = p['price']
                        found = True
                        break
                if not found and p['name']:
                    contractors.append({
                        'name': p['name'],
                        'rating': p.get('rating', 'N/A'),
                        'reviews': p.get('reviews', 'N/A'),
                        'hires': p.get('hires', 'N/A'),
                        'price': p.get('price', 'N/A'),
                        'category': category
                    })
        except Exception as e:
            print(f'NEXT_DATA parse error: {e}')
    
    # Also try regex for hire counts in HTML
    hire_pattern = r'(\d+)\s+hire'
    price_pattern = r'\$(\d+[\d,]*)'
    
    return contractors

all_contractors = []
all_contractors.extend(extract_data('/tmp/tt_bathroom.html', 'Bathroom Remodeling'))
all_contractors.extend(extract_data('/tmp/tt_tile.html', 'Tile Installation'))

# Deduplicate by name
seen = {}
for c in all_contractors:
    name = c['name']
    if name not in seen:
        seen[name] = c
    else:
        # Merge data
        for k, v in c.items():
            if v and v != 'N/A' and (k not in seen[name] or seen[name][k] == 'N/A'):
                seen[name][k] = v

print(f'\n=== TOTAL UNIQUE CONTRACTORS: {len(seen)} ===')
for name, c in seen.items():
    print(f"{c.get('name','?')} | {c.get('rating','N/A')} | {c.get('reviews','N/A')} | {c.get('hires','N/A')} | {c.get('price','N/A')} | {c.get('category','?')}")

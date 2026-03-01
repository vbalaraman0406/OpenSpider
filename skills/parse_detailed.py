import requests, json, re
from html import unescape

urls = [
    ('https://www.thumbtack.com/wa/vancouver/bathroom-remodeling/', 'Bathroom Remodeling'),
    ('https://www.thumbtack.com/wa/vancouver/tile-installation/', 'Tile Installation')
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9'
}

all_contractors = []
seen = set()

for url, cat in urls:
    r = requests.get(url, headers=headers, timeout=30)
    html = r.text
    
    # Extract __NEXT_DATA__
    m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.DOTALL)
    if not m:
        continue
    
    data = json.loads(m.group(1))
    
    # Navigate to find service providers
    props = data.get('props', {}).get('pageProps', {})
    
    # Try multiple paths to find contractor data
    results = []
    
    # Path 1: searchResults
    sr = props.get('searchResults', [])
    if sr:
        results = sr
    
    # Path 2: initialResults
    ir = props.get('initialResults', [])
    if ir:
        results = ir
    
    # Path 3: dig into serverSideSearchResults
    ssr = props.get('serverSideSearchResults', {})
    if isinstance(ssr, dict):
        res = ssr.get('results', [])
        if res:
            results = res
    
    # Path 4: look for pros key
    if not results:
        for key in props:
            val = props[key]
            if isinstance(val, list) and len(val) > 0:
                if isinstance(val[0], dict) and ('serviceName' in val[0] or 'rating' in val[0] or 'businessName' in val[0]):
                    results = val
                    break
    
    # If still nothing, search recursively for arrays of objects with businessName
    if not results:
        def find_pros(obj, depth=0):
            if depth > 8:
                return []
            if isinstance(obj, list):
                if len(obj) > 2 and isinstance(obj[0], dict):
                    if any(k in obj[0] for k in ['businessName', 'name', 'displayName']):
                        return obj
                for item in obj:
                    r = find_pros(item, depth+1)
                    if r:
                        return r
            elif isinstance(obj, dict):
                for k, v in obj.items():
                    r = find_pros(v, depth+1)
                    if r:
                        return r
            return []
        results = find_pros(props)
    
    for pro in results:
        if not isinstance(pro, dict):
            continue
        name = pro.get('businessName') or pro.get('name') or pro.get('displayName', 'Unknown')
        name = unescape(str(name))
        
        if name in seen:
            continue
        seen.add(name)
        
        rating = pro.get('rating') or pro.get('averageRating') or pro.get('overallRating', 'N/A')
        if isinstance(rating, float):
            rating = round(rating, 2)
        
        num_reviews = pro.get('numReviews') or pro.get('reviewCount') or pro.get('numberOfReviews', 'N/A')
        num_hires = pro.get('numHires') or pro.get('hireCount') or pro.get('numberOfHires', 'N/A')
        
        # Price
        price = pro.get('instantBookPrice') or pro.get('priceEstimate') or pro.get('price', {})
        if isinstance(price, dict):
            low = price.get('min') or price.get('low', '')
            high = price.get('max') or price.get('high', '')
            if low and high:
                price = f'${low}-${high}'
            elif low:
                price = f'${low}+'
            else:
                price = 'N/A'
        elif price and price != 'N/A':
            price = f'${price}'
        else:
            price = 'N/A'
        
        # Specialties
        specs = pro.get('services') or pro.get('specialties') or pro.get('serviceNames', [])
        if isinstance(specs, list):
            specs = ', '.join([str(s) if isinstance(s, str) else s.get('name', '') for s in specs[:3]])
        else:
            specs = str(specs) if specs else cat
        
        if not specs:
            specs = cat
        
        all_contractors.append({
            'name': name,
            'rating': rating,
            'reviews': num_reviews,
            'hires': num_hires,
            'price': price,
            'specialties': specs,
            'category': cat
        })

# Print summary
print(f'Total unique contractors: {len(all_contractors)}')
print('---')
for c in all_contractors:
    print(json.dumps(c))

# Also dump the keys of the first result to understand structure
print('\n--- SAMPLE KEYS ---')
for url, cat in urls:
    r = requests.get(url, headers=headers, timeout=30)
    m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', r.text, re.DOTALL)
    if m:
        data = json.loads(m.group(1))
        props = data.get('props', {}).get('pageProps', {})
        print(f'\nTop-level keys for {cat}: {list(props.keys())[:15]}')
        # Find the results
        for key in props:
            val = props[key]
            if isinstance(val, list) and len(val) > 0 and isinstance(val[0], dict):
                print(f'  List key "{key}" has {len(val)} items, sample keys: {list(val[0].keys())[:20]}')
        break

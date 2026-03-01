import requests, json, re
from html.parser import HTMLParser

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

urls = {
    'Bathroom Remodeling': 'https://www.thumbtack.com/wa/vancouver/bathroom-remodeling/',
    'Tile Installation': 'https://www.thumbtack.com/wa/vancouver/tile-installation/'
}

all_contractors = []
seen = set()

for cat, url in urls.items():
    r = requests.get(url, headers=headers, timeout=15)
    m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', r.text)
    if not m:
        continue
    data = json.loads(m.group(1))
    props = data.get('props',{}).get('pageProps',{})
    layout = props.get('layoutViewModel',{})
    
    # Try to find pro cards in layout
    results = []
    def find_pros(obj, depth=0):
        if depth > 10: return
        if isinstance(obj, dict):
            # Look for pro-like objects
            if 'proName' in obj or 'businessName' in obj or 'serviceName' in obj:
                results.append(obj)
            if 'numHires' in obj or 'hireCount' in obj or 'numberOfHires' in obj:
                results.append(obj)
            for v in obj.values():
                find_pros(v, depth+1)
        elif isinstance(obj, list):
            for item in obj:
                find_pros(item, depth+1)
    
    find_pros(layout)
    
    # Also search for proCards, searchResults, etc
    def find_key(obj, target_keys, depth=0):
        if depth > 8: return []
        found = []
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k in target_keys:
                    found.append((k, v))
                found.extend(find_key(v, target_keys, depth+1))
        elif isinstance(obj, list):
            for item in obj:
                found.extend(find_key(item, target_keys, depth+1))
        return found
    
    keys_of_interest = ['proCards', 'searchResults', 'professionals', 'pros', 'listings', 'cards', 'numHires', 'hireCount', 'priceEstimate', 'startingCost', 'costEstimate', 'pricing']
    found_items = find_key(props, keys_of_interest)
    
    print(f"\n=== {cat} ===")
    print(f"Found {len(found_items)} matching keys")
    for k, v in found_items[:20]:
        val_str = json.dumps(v) if not isinstance(v, str) else v
        print(f"  KEY: {k} -> {val_str[:200]}")
    
    # Also check structured data for hire info
    sd = props.get('nextBaseProps', {}).get('structuredData', [])
    if sd:
        for item in sd:
            name = item.get('name', 'Unknown')
            if name in seen:
                continue
            seen.add(name)
            rating_obj = item.get('aggregateRating', {})
            rating = round(rating_obj.get('ratingValue', 0), 2) if rating_obj else 'N/A'
            reviews = rating_obj.get('reviewCount', 'N/A') if rating_obj else 'N/A'
            all_contractors.append({
                'name': name,
                'rating': rating,
                'reviews': reviews,
                'category': cat
            })

print(f"\n\nTotal contractors: {len(all_contractors)}")
for c in all_contractors:
    print(f"{c['name']} | {c['rating']} | {c['reviews']} | {c['category']}")

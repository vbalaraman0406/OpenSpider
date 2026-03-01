import requests, json, re
from html import unescape

urls = [
    'https://www.thumbtack.com/wa/vancouver/bathroom-remodeling/',
    'https://www.thumbtack.com/wa/vancouver/tile-installation/'
]

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

all_pros = {}

for url in urls:
    r = requests.get(url, headers=headers, timeout=30)
    m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', r.text)
    if not m:
        continue
    data = json.loads(m.group(1))
    
    # Navigate to find pro results
    props = data.get('props', {}).get('pageProps', {})
    
    # Try to find results in different paths
    def find_pros(obj, depth=0):
        if depth > 8:
            return
        if isinstance(obj, dict):
            # Look for numHires, hireCount, startingCost, etc.
            name = obj.get('businessName') or obj.get('name') or obj.get('displayName')
            if name and (obj.get('rating') or obj.get('numReviews') or obj.get('numHires')):
                key = unescape(str(name))
                if key not in all_pros:
                    all_pros[key] = {
                        'rating': obj.get('rating') or obj.get('averageRating'),
                        'reviews': obj.get('numReviews') or obj.get('reviewCount'),
                        'hires': obj.get('numHires') or obj.get('hireCount') or obj.get('numHired'),
                        'price': obj.get('startingCost') or obj.get('priceEstimate') or obj.get('instantBookPrice') or obj.get('price'),
                        'specialties': obj.get('services') or obj.get('categoryName') or obj.get('serviceName'),
                    }
                else:
                    # Update with non-None values
                    for k in ['hires','price','specialties']:
                        v = obj.get({'hires':'numHires','price':'startingCost','specialties':'services'}.get(k, k))
                        if v and not all_pros[key].get(k):
                            all_pros[key][k] = v
            for v in obj.values():
                find_pros(v, depth+1)
        elif isinstance(obj, list):
            for item in obj:
                find_pros(item, depth+1)
    
    find_pros(props)

print(f'Found {len(all_pros)} contractors with deep parse')
for name, info in sorted(all_pros.items()):
    print(f"{name} | {info.get('rating','N/A')} | {info.get('reviews','N/A')} | {info.get('hires','N/A')} | {info.get('price','N/A')} | {info.get('specialties','N/A')}")

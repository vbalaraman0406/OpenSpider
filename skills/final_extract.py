import requests, json, re
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

urls = {
    'Bathroom Remodeling': 'https://www.thumbtack.com/wa/vancouver/bathroom-remodeling/',
    'Tile Installation': 'https://www.thumbtack.com/wa/vancouver/tile-installation/'
}

all_contractors = {}

for category, url in urls.items():
    r = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, 'html.parser')
    script = soup.find('script', id='__NEXT_DATA__')
    if not script:
        print(f'No __NEXT_DATA__ for {category}')
        continue
    data = json.loads(script.string)
    
    # Navigate to search results
    props = data.get('props', {}).get('pageProps', {})
    
    # Try to find professional listings in various paths
    results = []
    
    # Check searchActiveServiceResults or similar
    def find_pros(obj, depth=0):
        if depth > 8:
            return
        if isinstance(obj, dict):
            # Look for professional-like objects with businessName
            if 'businessName' in obj and 'rating' in obj:
                results.append(obj)
                return
            for k, v in obj.items():
                find_pros(v, depth+1)
        elif isinstance(obj, list):
            for item in obj:
                find_pros(item, depth+1)
    
    find_pros(props)
    
    for pro in results:
        name = pro.get('businessName', 'Unknown')
        if name in all_contractors:
            # Merge categories
            all_contractors[name]['categories'].add(category)
            continue
        
        rating = pro.get('rating', pro.get('averageRating', 'N/A'))
        reviews = pro.get('numReviews', pro.get('reviewCount', 'N/A'))
        hires = pro.get('numHires', 'N/A')
        
        # Price
        price = 'N/A'
        price_est = pro.get('priceEstimate', pro.get('instantEstimate', {}))
        if isinstance(price_est, dict):
            lo = price_est.get('minPrice', price_est.get('low', ''))
            hi = price_est.get('maxPrice', price_est.get('high', ''))
            if lo or hi:
                price = f'${lo}-${hi}'
        elif price_est and price_est != {}:
            price = str(price_est)
        
        # Services/specialties
        services = pro.get('services', pro.get('serviceNames', []))
        if isinstance(services, list):
            specs = ', '.join(services[:3]) if services else 'N/A'
        else:
            specs = str(services) if services else 'N/A'
        
        # Also check for intro or headline
        intro = pro.get('introduction', pro.get('headline', ''))
        if not services or specs == 'N/A':
            specs = (intro[:80] + '...') if intro and len(intro) > 80 else (intro if intro else 'N/A')
        
        all_contractors[name] = {
            'rating': rating,
            'reviews': reviews,
            'hires': hires,
            'price': price,
            'specialties': specs,
            'categories': {category}
        }

print(f'Total unique contractors: {len(all_contractors)}')
print()
for name, info in all_contractors.items():
    cats = ' & '.join(info['categories'])
    print(f"NAME: {name}")
    print(f"  Rating: {info['rating']} | Reviews: {info['reviews']} | Hires: {info['hires']}")
    print(f"  Price: {info['price']} | Specialties: {info['specialties']}")
    print(f"  Found in: {cats}")
    print()

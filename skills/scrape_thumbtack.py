import requests
import json
import re
from html.parser import HTMLParser

urls = [
    'https://www.thumbtack.com/wa/vancouver/bathroom-remodeling/',
    'https://www.thumbtack.com/wa/vancouver/tile-installation/'
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
}

all_contractors = []
seen_names = set()

for url in urls:
    category = 'Bathroom Remodeling' if 'bathroom' in url else 'Tile Installation'
    print(f'\n--- Fetching: {url} ---')
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        print(f'Status: {resp.status_code}, Length: {len(resp.text)}')
        
        # Try to find JSON-LD data
        json_ld_matches = re.findall(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', resp.text, re.DOTALL)
        print(f'Found {len(json_ld_matches)} JSON-LD blocks')
        
        for jm in json_ld_matches:
            try:
                data = json.loads(jm)
                if isinstance(data, list):
                    for item in data:
                        if item.get('@type') in ['LocalBusiness', 'HomeAndConstructionBusiness', 'Service', 'ProfessionalService']:
                            name = item.get('name', 'Unknown')
                            if name not in seen_names:
                                seen_names.add(name)
                                rating_obj = item.get('aggregateRating', {})
                                all_contractors.append({
                                    'name': name,
                                    'rating': rating_obj.get('ratingValue', 'N/A'),
                                    'reviews': rating_obj.get('reviewCount', 'N/A'),
                                    'category': category,
                                    'url': item.get('url', '')
                                })
                elif isinstance(data, dict):
                    if data.get('@type') in ['LocalBusiness', 'HomeAndConstructionBusiness', 'Service', 'ProfessionalService', 'ItemList']:
                        if data.get('@type') == 'ItemList':
                            for elem in data.get('itemListElement', []):
                                item = elem.get('item', elem)
                                name = item.get('name', 'Unknown')
                                if name not in seen_names:
                                    seen_names.add(name)
                                    rating_obj = item.get('aggregateRating', {})
                                    all_contractors.append({
                                        'name': name,
                                        'rating': rating_obj.get('ratingValue', 'N/A'),
                                        'reviews': rating_obj.get('reviewCount', 'N/A'),
                                        'category': category,
                                        'url': item.get('url', '')
                                    })
            except json.JSONDecodeError:
                pass
        
        # Also try to find __NEXT_DATA__ or similar embedded JSON
        next_data = re.findall(r'<script[^>]*id=["\']__NEXT_DATA__["\'][^>]*>(.*?)</script>', resp.text, re.DOTALL)
        if next_data:
            print(f'Found __NEXT_DATA__ block, length: {len(next_data[0])}')
            try:
                nd = json.loads(next_data[0])
                # Try to navigate the structure
                props = nd.get('props', {}).get('pageProps', {})
                # Look for pro listings
                for key in ['pros', 'results', 'listings', 'searchResults', 'professionals']:
                    if key in props:
                        items = props[key]
                        if isinstance(items, list):
                            for item in items:
                                name = item.get('name', item.get('businessName', item.get('displayName', 'Unknown')))
                                if name and name not in seen_names:
                                    seen_names.add(name)
                                    rating = item.get('rating', item.get('averageRating', item.get('overallRating', 'N/A')))
                                    reviews = item.get('numReviews', item.get('reviewCount', item.get('numberOfReviews', 'N/A')))
                                    hires = item.get('numHires', item.get('hireCount', item.get('numberOfHires', 'N/A')))
                                    price = item.get('priceRange', item.get('price', item.get('startingCost', 'N/A')))
                                    all_contractors.append({
                                        'name': name,
                                        'rating': rating,
                                        'reviews': reviews,
                                        'hires': hires if hires != 'N/A' else 'N/A',
                                        'price': price if price != 'N/A' else 'N/A',
                                        'category': category
                                    })
                            print(f'  Found {len(items)} items in {key}')
                
                # Deep search for any pro data
                def find_pros(obj, depth=0):
                    if depth > 8:
                        return
                    if isinstance(obj, dict):
                        if 'businessName' in obj or ('name' in obj and 'rating' in obj):
                            name = obj.get('businessName', obj.get('name', 'Unknown'))
                            if name and name not in seen_names and len(name) > 2:
                                seen_names.add(name)
                                all_contractors.append({
                                    'name': name,
                                    'rating': obj.get('rating', obj.get('averageRating', 'N/A')),
                                    'reviews': obj.get('numReviews', obj.get('reviewCount', 'N/A')),
                                    'hires': obj.get('numHires', obj.get('hireCount', 'N/A')),
                                    'price': obj.get('priceRange', obj.get('startingCost', 'N/A')),
                                    'category': category
                                })
                        for v in obj.values():
                            find_pros(v, depth+1)
                    elif isinstance(obj, list):
                        for item in obj:
                            find_pros(item, depth+1)
                
                find_pros(nd)
            except json.JSONDecodeError as e:
                print(f'Failed to parse __NEXT_DATA__: {e}')
        
        # Fallback: try regex patterns for contractor names and ratings from HTML
        if len(all_contractors) == 0:
            # Look for common patterns
            name_patterns = re.findall(r'data-testid=["\']search-result-title["\'][^>]*>([^<]+)<', resp.text)
            if name_patterns:
                print(f'Found {len(name_patterns)} names via data-testid')
                for n in name_patterns:
                    if n not in seen_names:
                        seen_names.add(n)
                        all_contractors.append({'name': n, 'rating': 'N/A', 'reviews': 'N/A', 'category': category})
            
            # Try aria-label patterns
            aria_names = re.findall(r'aria-label=["\']([^"\']+ rated [\d.]+ out of 5[^"\']*)["\'\]', resp.text)
            if aria_names:
                print(f'Found {len(aria_names)} aria-label entries')
        
        # Save a snippet for debugging
        if len(all_contractors) == 0:
            print('No contractors found yet. Saving page snippet...')
            with open(f'thumbtack_debug_{category.replace(" ","_")}.txt', 'w') as f:
                f.write(resp.text[:5000])
                f.write('\n\n--- MIDDLE ---\n\n')
                f.write(resp.text[len(resp.text)//2:len(resp.text)//2+3000])
    except Exception as e:
        print(f'Error fetching {url}: {e}')

print(f'\n=== TOTAL CONTRACTORS FOUND: {len(all_contractors)} ===')
for c in all_contractors:
    print(json.dumps(c))

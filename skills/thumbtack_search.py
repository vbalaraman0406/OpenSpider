import urllib.request
import json
import re

# Try Thumbtack which worked before
url = 'https://www.thumbtack.com/wa/vancouver/bathroom-remodeling/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

req = urllib.request.Request(url, headers=headers)
try:
    resp = urllib.request.urlopen(req, timeout=15)
    html = resp.read().decode('utf-8', errors='ignore')
    print(f'Got {len(html)} bytes from Thumbtack')
    
    # Extract JSON-LD data
    jsonld_matches = re.findall(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html, re.DOTALL)
    print(f'Found {len(jsonld_matches)} JSON-LD blocks')
    
    contractors = []
    
    for jm in jsonld_matches:
        try:
            data = json.loads(jm)
            if isinstance(data, list):
                for item in data:
                    if item.get('@type') in ['LocalBusiness', 'HomeAndConstructionBusiness', 'Service']:
                        name = item.get('name', '')
                        rating = ''
                        reviews = ''
                        if 'aggregateRating' in item:
                            rating = item['aggregateRating'].get('ratingValue', '')
                            reviews = item['aggregateRating'].get('reviewCount', '')
                        phone = item.get('telephone', '')
                        website = item.get('url', '')
                        desc = item.get('description', '')[:100]
                        contractors.append({'name': name, 'rating': rating, 'reviews': reviews, 'phone': phone, 'website': website, 'notes': desc})
            elif isinstance(data, dict):
                if data.get('@type') in ['LocalBusiness', 'HomeAndConstructionBusiness', 'Service', 'ItemList']:
                    if 'itemListElement' in data:
                        for elem in data['itemListElement']:
                            item = elem.get('item', elem)
                            name = item.get('name', '')
                            rating = ''
                            reviews = ''
                            if 'aggregateRating' in item:
                                rating = item['aggregateRating'].get('ratingValue', '')
                                reviews = item['aggregateRating'].get('reviewCount', '')
                            phone = item.get('telephone', '')
                            website = item.get('url', '')
                            desc = item.get('description', '')
                            if desc:
                                desc = desc[:100]
                            contractors.append({'name': name, 'rating': rating, 'reviews': reviews, 'phone': phone, 'website': website, 'notes': desc})
        except json.JSONDecodeError:
            pass
    
    # Also try regex patterns for contractor names and ratings in HTML
    if not contractors:
        print('No JSON-LD contractors found, trying HTML patterns...')
        # Look for common patterns
        name_patterns = re.findall(r'"displayName"\s*:\s*"([^"]+)"', html)
        rating_patterns = re.findall(r'"rating"\s*:\s*([\d.]+)', html)
        review_patterns = re.findall(r'"numReviews"\s*:\s*(\d+)', html)
        
        print(f'Found {len(name_patterns)} names, {len(rating_patterns)} ratings')
        
        for i, name in enumerate(name_patterns[:15]):
            r = rating_patterns[i] if i < len(rating_patterns) else ''
            rv = review_patterns[i] if i < len(review_patterns) else ''
            contractors.append({'name': name, 'rating': r, 'reviews': rv, 'phone': '', 'website': '', 'notes': 'Thumbtack'})
    
    # Also try nextData pattern
    if not contractors:
        next_data = re.findall(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
        if next_data:
            print('Found __NEXT_DATA__, parsing...')
            try:
                nd = json.loads(next_data[0])
                # Navigate to find pros
                props = nd.get('props', {}).get('pageProps', {})
                results = props.get('results', props.get('pros', []))
                if isinstance(results, list):
                    for r in results[:15]:
                        name = r.get('name', r.get('businessName', ''))
                        rating = r.get('rating', r.get('averageRating', ''))
                        reviews = r.get('numReviews', r.get('reviewCount', ''))
                        contractors.append({'name': name, 'rating': rating, 'reviews': reviews, 'phone': '', 'website': '', 'notes': 'Thumbtack'})
            except:
                pass
    
    print(f'\nTotal contractors found: {len(contractors)}')
    for c in contractors:
        print(f"  {c['name']} | {c['rating']} | {c['reviews']} | {c['phone']} | {c['website']} | {c['notes']}")
        
except Exception as e:
    print(f'Error: {e}')

# Also try Houzz
print('\n--- Trying Houzz ---')
houzz_url = 'https://www.houzz.com/professionals/general-contractor/vancouver-wa-us-probr0-bo~t_11786~r_4956868'
req2 = urllib.request.Request(houzz_url, headers=headers)
try:
    resp2 = urllib.request.urlopen(req2, timeout=15)
    html2 = resp2.read().decode('utf-8', errors='ignore')
    print(f'Got {len(html2)} bytes from Houzz')
    
    # Extract JSON-LD
    jsonld2 = re.findall(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html2, re.DOTALL)
    print(f'Found {len(jsonld2)} JSON-LD blocks')
    
    for jm in jsonld2[:3]:
        try:
            data = json.loads(jm)
            print(f'Type: {data.get("@type", "unknown")}')
            if 'itemListElement' in data:
                for elem in data['itemListElement'][:10]:
                    item = elem.get('item', elem)
                    print(f"  Houzz: {item.get('name', 'N/A')}")
        except:
            pass
except Exception as e:
    print(f'Houzz error: {e}')

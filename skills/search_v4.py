import urllib.request
import json
import re

# Try Thumbtack with proper redirect handling and different URL patterns
urls = [
    ('Thumbtack', 'https://www.thumbtack.com/wa/vancouver/bathroom-remodeling/'),
    ('Thumbtack2', 'https://www.thumbtack.com/wa/vancouver/tile-installation/'),
    ('BBB', 'https://www.bbb.org/search?find_country=US&find_loc=Vancouver%2C%20WA%2098662&find_text=bathroom%20remodeling&find_type=Category&page=1'),
    ('Yelp', 'https://www.yelp.com/search?find_desc=bathroom+remodeling&find_loc=Vancouver%2C+WA+98662'),
]

for name, url in urls:
    print(f'\n=== {name} ===')
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })
        resp = urllib.request.urlopen(req, timeout=15)
        html = resp.read().decode('utf-8', errors='ignore')
        print(f'Status: {resp.status}, Length: {len(html)}')
        
        # Extract JSON-LD data
        jsonld = re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.DOTALL)
        if jsonld:
            for j in jsonld[:3]:
                try:
                    data = json.loads(j)
                    print(f'JSON-LD type: {data.get("@type", "unknown")}')
                    if isinstance(data, list):
                        for item in data[:5]:
                            print(f"  - {item.get('name','?')} | {item.get('aggregateRating',{}).get('ratingValue','?')} stars | {item.get('aggregateRating',{}).get('reviewCount','?')} reviews")
                    elif data.get('@type') in ['LocalBusiness', 'HomeAndConstructionBusiness']:
                        print(f"  - {data.get('name','?')} | Rating: {data.get('aggregateRating',{}).get('ratingValue','?')}")
                except:
                    print(f'  JSON parse error, snippet: {j[:200]}')
        
        # Try to find business names and ratings in HTML
        # Look for common patterns
        names = re.findall(r'"name"\s*:\s*"([^"]{5,60})"', html)
        ratings = re.findall(r'"ratingValue"\s*:\s*"?([\d.]+)"?', html)
        reviews = re.findall(r'"reviewCount"\s*:\s*"?(\d+)"?', html)
        
        if names:
            print(f'Found {len(names)} names: {names[:10]}')
        if ratings:
            print(f'Found {len(ratings)} ratings: {ratings[:10]}')
        if reviews:
            print(f'Found {len(reviews)} review counts: {reviews[:10]}')
            
        # Also look for business cards / listing patterns
        biz_patterns = re.findall(r'([A-Z][\w\s&]+(?:LLC|Inc|Co|Remodel|Construction|Tile|Bath|Home|Renovation))', html)
        if biz_patterns:
            unique = list(set(biz_patterns))[:15]
            print(f'Business name patterns: {unique}')
            
    except Exception as e:
        print(f'Error: {e}')

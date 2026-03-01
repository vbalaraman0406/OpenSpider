import subprocess
import json
import re
from urllib.request import Request, urlopen
from html.parser import HTMLParser

# Try multiple approaches to get contractor data
# Approach 1: Try Thumbtack search page with proper URL
urls_to_try = [
    'https://www.thumbtack.com/wa/vancouver/bathroom-remodeling/',
    'https://www.thumbtack.com/wa/vancouver/tile-installation/',
    'https://www.thumbtack.com/wa/vancouver/bathroom-remodeling/near-me/',
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

for url in urls_to_try:
    try:
        req = Request(url, headers=headers)
        resp = urlopen(req, timeout=15)
        html = resp.read().decode('utf-8', errors='ignore')
        
        # Look for JSON-LD data
        ld_matches = re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.DOTALL)
        if ld_matches:
            print(f"\n=== JSON-LD from {url} ===")
            for m in ld_matches:
                try:
                    data = json.loads(m)
                    if isinstance(data, list):
                        for item in data:
                            if item.get('@type') in ['LocalBusiness', 'HomeAndConstructionBusiness', 'Service']:
                                name = item.get('name', 'N/A')
                                rating = item.get('aggregateRating', {}).get('ratingValue', 'N/A')
                                reviews = item.get('aggregateRating', {}).get('reviewCount', 'N/A')
                                phone = item.get('telephone', 'N/A')
                                url_biz = item.get('url', 'N/A')
                                print(f"Name: {name} | Rating: {rating} | Reviews: {reviews} | Phone: {phone} | URL: {url_biz}")
                    elif isinstance(data, dict):
                        if data.get('@type') == 'ItemList':
                            for elem in data.get('itemListElement', []):
                                item = elem.get('item', elem)
                                name = item.get('name', 'N/A')
                                rating = item.get('aggregateRating', {}).get('ratingValue', 'N/A') if isinstance(item.get('aggregateRating'), dict) else 'N/A'
                                reviews = item.get('aggregateRating', {}).get('reviewCount', 'N/A') if isinstance(item.get('aggregateRating'), dict) else 'N/A'
                                url_biz = item.get('url', 'N/A')
                                print(f"Name: {name} | Rating: {rating} | Reviews: {reviews} | URL: {url_biz}")
                except json.JSONDecodeError:
                    pass
        
        # Also look for __NEXT_DATA__ or similar JSON blobs
        next_data = re.findall(r'<script[^>]*id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
        if next_data:
            print(f"\n=== __NEXT_DATA__ found at {url} ===")
            try:
                nd = json.loads(next_data[0])
                # Try to find pros/contractors in the data
                nd_str = json.dumps(nd)
                # Look for rating patterns
                ratings = re.findall(r'"ratingValue":\s*([\d.]+)', nd_str)
                names = re.findall(r'"businessName":\s*"([^"]+)"', nd_str)
                if names:
                    print(f"Found {len(names)} business names: {names[:15]}")
                if ratings:
                    print(f"Found {len(ratings)} ratings: {ratings[:15]}")
            except:
                pass
        
        if not ld_matches and not next_data:
            # Check page size and look for any contractor-related content
            print(f"\nPage from {url}: {len(html)} chars")
            # Look for phone numbers
            phones = re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', html)
            if phones:
                print(f"Phone numbers found: {phones[:10]}")
            
    except Exception as e:
        print(f"Error for {url}: {e}")

print("\nDone.")

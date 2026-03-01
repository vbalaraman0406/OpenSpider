import urllib.request
import json
import re

# Try SerpAPI-style or direct Google search via different approach
# Let's try scraping specific known contractor listing sites
urls = [
    ('https://www.angi.com/companylist/vancouver-wa/bathroom-remodeling.htm', 'Angi'),
    ('https://www.buildzoom.com/contractor/wa/vancouver/bathroom-remodeling', 'BuildZoom'),
    ('https://www.porch.com/vancouver-wa/bathroom-remodelers', 'Porch'),
]

for url, source in urls:
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml',
            'Accept-Language': 'en-US,en;q=0.9',
        })
        resp = urllib.request.urlopen(req, timeout=10)
        html = resp.read().decode('utf-8', errors='ignore')
        # Extract business names, ratings, phone numbers
        # Look for common patterns
        names = re.findall(r'(?:business[_-]?name|company[_-]?name|data-name)["\']?\s*[:=]\s*["\']([^"\'>]+)', html, re.I)
        ratings = re.findall(r'(\d\.\d)\s*(?:star|rating|out of)', html, re.I)
        phones = re.findall(r'\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}', html)
        print(f'\n=== {source} ===')
        print(f'Status: {resp.status}')
        print(f'Names found: {names[:10]}')
        print(f'Ratings found: {ratings[:10]}')
        print(f'Phones found: {phones[:10]}')
        # Also look for JSON-LD structured data
        ld_matches = re.findall(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html, re.S)
        for ld in ld_matches[:3]:
            try:
                data = json.loads(ld)
                print(f'JSON-LD: {json.dumps(data, indent=2)[:500]}')
            except:
                pass
        # Look for any contractor-like text blocks
        blocks = re.findall(r'([A-Z][A-Za-z\s&]+(?:Construction|Remodel|Tile|Plumbing|Renovation|Contracting|LLC|Inc|Co))', html)
        print(f'Business-like names: {list(set(blocks))[:15]}')
    except Exception as e:
        print(f'{source}: Error - {e}')

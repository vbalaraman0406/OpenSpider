import urllib.request
import re
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

# Try multiple approaches
urls = [
    ('Houzz', 'https://www.houzz.com/professionals/general-contractor/vancouver-wa-us'),
    ('Porch', 'https://porch.com/vancouver-wa/bathroom-remodelers'),
    ('Angi', 'https://www.angi.com/companylist/vancouver-wa/bathroom-remodel.htm'),
    ('Yelp-API', 'https://www.yelp.com/search?find_desc=bathroom+remodel&find_loc=Vancouver%2C+WA+98662'),
    ('Google-Maps', 'https://www.google.com/maps/search/bathroom+remodel+contractor+vancouver+wa+98662'),
    ('YP', 'https://www.yellowpages.com/vancouver-wa/bathroom-remodeling'),
]

for name, url in urls:
    print(f'\n=== {name} ===')
    try:
        req = urllib.request.Request(url, headers=headers)
        resp = urllib.request.urlopen(req, timeout=15, context=ctx)
        html = resp.read().decode('utf-8', errors='ignore')
        print(f'Status: {resp.status}, Length: {len(html)}')
        
        # Extract business names and ratings from common patterns
        # Look for JSON-LD
        ld_matches = re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.DOTALL)
        if ld_matches:
            print(f'Found {len(ld_matches)} JSON-LD blocks')
            for m in ld_matches[:3]:
                try:
                    data = json.loads(m)
                    print(json.dumps(data, indent=2)[:500])
                except:
                    pass
        
        # Look for business name patterns
        biz_names = re.findall(r'"name"\s*:\s*"([^"]+)"', html)
        ratings = re.findall(r'"ratingValue"\s*:\s*"?([\d.]+)"?', html)
        reviews = re.findall(r'"reviewCount"\s*:\s*"?(\d+)"?', html)
        
        if biz_names:
            print(f'Business names found: {biz_names[:10]}')
        if ratings:
            print(f'Ratings found: {ratings[:10]}')
        if reviews:
            print(f'Review counts: {reviews[:10]}')
            
        # Also try to find phone numbers
        phones = re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', html)
        if phones:
            print(f'Phones: {list(set(phones))[:10]}')
            
    except Exception as e:
        print(f'ERROR: {e}')

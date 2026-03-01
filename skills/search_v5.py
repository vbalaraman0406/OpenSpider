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

def fetch(url):
    try:
        req = urllib.request.Request(url, headers=headers)
        resp = urllib.request.urlopen(req, timeout=15, context=ctx)
        return resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return f'ERROR: {e}'

# Try Yelp search
print('=== YELP ===')
yelp_url = 'https://www.yelp.com/search?find_desc=bathroom+remodel&find_loc=Vancouver%2C+WA+98662'
html = fetch(yelp_url)
if not html.startswith('ERROR'):
    # Extract business names and ratings from Yelp
    # Look for JSON-LD or structured data
    json_ld = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL)
    for j in json_ld:
        try:
            data = json.loads(j)
            print('JSON-LD:', json.dumps(data, indent=2)[:500])
        except:
            pass
    # Try regex for business cards
    names = re.findall(r'class="css-19v1rkv"[^>]*>(.*?)</a>', html)
    if not names:
        names = re.findall(r'"name"\s*:\s*"([^"]+)"', html)
    ratings = re.findall(r'"ratingValue"\s*:\s*([\d.]+)', html)
    reviews = re.findall(r'"reviewCount"\s*:\s*(\d+)', html)
    print(f'Names found: {len(names)}')
    for i, n in enumerate(names[:15]):
        r = ratings[i] if i < len(ratings) else 'N/A'
        rc = reviews[i] if i < len(reviews) else 'N/A'
        print(f'  {n} | Rating: {r} | Reviews: {rc}')
    if not names:
        print('First 2000 chars:', html[:2000])
else:
    print(html)

# Try Thumbtack API
print('\n=== THUMBTACK ===')
tt_url = 'https://www.thumbtack.com/k/bathroom-remodeling/near-me/?zip_code=98662'
html = fetch(tt_url)
if not html.startswith('ERROR'):
    json_ld = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL)
    for j in json_ld:
        try:
            data = json.loads(j)
            if isinstance(data, list):
                for item in data:
                    if item.get('@type') == 'LocalBusiness' or item.get('@type') == 'HomeAndConstructionBusiness':
                        print(f"  {item.get('name','')} | Rating: {item.get('aggregateRating',{}).get('ratingValue','N/A')} | Reviews: {item.get('aggregateRating',{}).get('reviewCount','N/A')}")
            elif isinstance(data, dict):
                if 'itemListElement' in data:
                    for el in data['itemListElement']:
                        item = el.get('item', el)
                        print(f"  {item.get('name','')} | Rating: {item.get('aggregateRating',{}).get('ratingValue','N/A')}")
        except Exception as e:
            print(f'Parse error: {e}')
    if not json_ld:
        names = re.findall(r'"businessName"\s*:\s*"([^"]+)"', html)
        print(f'Business names from HTML: {names[:10]}')
        if not names:
            print('First 1500 chars:', html[:1500])
else:
    print(html)

# Try BuildZoom
print('\n=== BUILDZOOM ===')
bz_url = 'https://www.buildzoom.com/contractor/wa/vancouver/bathroom-remodeling'
html = fetch(bz_url)
if not html.startswith('ERROR'):
    names = re.findall(r'"name"\s*:\s*"([^"]+)"', html)
    print(f'Names: {names[:15]}')
    if not names:
        print('First 1500:', html[:1500])
else:
    print(html)

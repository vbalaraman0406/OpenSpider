import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Try Thumbtack search API
url = 'https://www.thumbtack.com/api/search?query=bathroom+remodeling&zipCode=98662'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json',
    'Referer': 'https://www.thumbtack.com/'
}

req = urllib.request.Request(url, headers=headers)
try:
    resp = urllib.request.urlopen(req, timeout=15, context=ctx)
    data = resp.read().decode('utf-8')[:3000]
    print(data)
except Exception as e:
    print(f'API Error: {e}')

# Also try Thumbtack page directly and look for JSON-LD
print('\n--- Trying Thumbtack page ---')
url2 = 'https://www.thumbtack.com/wa/vancouver/bathroom-remodeling/'
req2 = urllib.request.Request(url2, headers=headers)
try:
    resp2 = urllib.request.urlopen(req2, timeout=15, context=ctx)
    html = resp2.read().decode('utf-8')
    # Extract JSON-LD
    import re
    ld_blocks = re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.DOTALL)
    for i, block in enumerate(ld_blocks):
        print(f'\nJSON-LD Block {i}:')
        try:
            d = json.loads(block)
            print(json.dumps(d, indent=2)[:1500])
        except:
            print(block[:500])
    
    # Also try to find contractor names in the HTML
    names = re.findall(r'"name"\s*:\s*"([^"]+)"', html)
    ratings = re.findall(r'"ratingValue"\s*:\s*"?([\d.]+)"?', html)
    reviews = re.findall(r'"reviewCount"\s*:\s*"?(\d+)"?', html)
    print(f'\nFound {len(names)} names, {len(ratings)} ratings, {len(reviews)} review counts')
    for n in names[:20]:
        print(f'  Name: {n}')
except Exception as e:
    print(f'Page Error: {e}')
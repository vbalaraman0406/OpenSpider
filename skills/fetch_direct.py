import urllib.request
import urllib.parse
import re
import ssl
import time

ssl._create_default_https_context = ssl._create_unverified_context

def fetch(url):
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return f'ERROR: {e}'

# Try fetching the Yelp search page for bathroom remodel Vancouver WA
print('=== Yelp Search ===')
url = 'https://www.yelp.com/search?find_desc=bathroom+remodel&find_loc=Vancouver%2C+WA+98662'
html = fetch(url)
if not html.startswith('ERROR'):
    # Look for JSON-LD or structured data
    json_blocks = re.findall(r'"searchPageProps".*?"businesses":\[(.*?)\]', html, re.DOTALL)
    if json_blocks:
        print('Found business data block')
        print(json_blocks[0][:2000])
    else:
        # Try simpler regex for business names on Yelp
        biz = re.findall(r'"bizId":"[^"]+","name":"([^"]+)"', html)
        ratings = re.findall(r'"rating":([\d.]+)', html)
        reviews = re.findall(r'"reviewCount":(\d+)', html)
        phones = re.findall(r'"phone":"([^"]+)"', html)
        if biz:
            print(f'Found {len(biz)} businesses on Yelp')
            for i, b in enumerate(biz[:15]):
                r = ratings[i] if i < len(ratings) else 'N/A'
                rv = reviews[i] if i < len(reviews) else 'N/A'
                p = phones[i] if i < len(phones) else 'N/A'
                print(f'  {i+1}. {b} | Rating: {r} | Reviews: {rv} | Phone: {p}')
        else:
            # Look for any business-like data
            names2 = re.findall(r'alt="([^"]*?)"[^>]*class="[^"]*photo', html)
            names3 = re.findall(r'<a[^>]*href="/biz/([^"?]+)"', html)
            print(f'Alt approach - biz slugs found: {len(names3)}')
            seen = set()
            for slug in names3[:20]:
                clean = slug.replace('-', ' ').title()
                if clean not in seen:
                    seen.add(clean)
                    print(f'  - {clean} (yelp.com/biz/{slug})')
            print(f'\nPage length: {len(html)}')
            # Check if blocked
            if 'unusual traffic' in html.lower() or 'captcha' in html.lower():
                print('BLOCKED by Yelp CAPTCHA')
else:
    print(html)

time.sleep(2)

# Try Google search with lite approach
print('\n=== Google Search ===')
url = 'https://www.google.com/search?q=bathroom+tile+remodel+contractor+Vancouver+WA+98662+reviews&num=10'
html = fetch(url)
if not html.startswith('ERROR'):
    # Extract titles from h3 tags
    h3s = re.findall(r'<h3[^>]*>(.*?)</h3>', html)
    print(f'Found {len(h3s)} h3 tags')
    for h in h3s[:15]:
        clean = re.sub(r'<[^>]+>', '', h).strip()
        print(f'  - {clean}')
    # Also look for local pack / map results
    local = re.findall(r'"title":"([^"]+)".*?"rating":(\d\.\d)', html)
    for name, rating in local[:10]:
        print(f'  LOCAL: {name} - {rating}')
else:
    print(html)

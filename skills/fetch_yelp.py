import urllib.request
import urllib.parse
import re
import json
import time

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'en-US,en;q=0.9'
}

def fetch_url(url):
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return f'ERROR: {e}'

# 1. Yelp search
print("=== YELP: Bathroom Tile Contractors Vancouver WA ===")
yelp_url = 'https://www.yelp.com/search?find_desc=bathroom+tile+contractor&find_loc=Vancouver%2C+WA+98662'
html = fetch_url(yelp_url)
if not html.startswith('ERROR'):
    # Try JSON-LD or structured data
    biz_names = re.findall(r'"name":"([^"]{3,60})"', html)
    ratings = re.findall(r'"rating":([\d.]+)', html)
    review_counts = re.findall(r'"reviewCount":(\d+)', html)
    phones = re.findall(r'"phone":"([^"]+)"', html)
    
    # Also try alternate patterns
    if len(biz_names) < 3:
        biz_names2 = re.findall(r'class="css-19v1rkv"[^>]*>([^<]+)<', html)
        biz_names.extend(biz_names2)
    
    print(f"Found {len(biz_names)} business names")
    for i, name in enumerate(biz_names[:15]):
        r = ratings[i] if i < len(ratings) else 'N/A'
        rc = review_counts[i] if i < len(review_counts) else 'N/A'
        p = phones[i] if i < len(phones) else 'N/A'
        print(f"  {i+1}. {name} | Rating: {r} | Reviews: {rc} | Phone: {p}")
    print(f"  HTML length: {len(html)}")
else:
    print(html)

time.sleep(3)

# 2. Thumbtack
print("\n=== THUMBTACK: Tile Installation Vancouver WA ===")
tt_url = 'https://www.thumbtack.com/wa/vancouver/tile-installation/'
html = fetch_url(tt_url)
if not html.startswith('ERROR'):
    biz_names = re.findall(r'"name":"([^"]{3,60})"', html)
    ratings = re.findall(r'"ratingValue":"?([\d.]+)"?', html)
    review_counts = re.findall(r'"reviewCount":"?(\d+)"?', html)
    
    print(f"Found {len(biz_names)} business names")
    for i, name in enumerate(biz_names[:15]):
        r = ratings[i] if i < len(ratings) else 'N/A'
        rc = review_counts[i] if i < len(review_counts) else 'N/A'
        print(f"  {i+1}. {name} | Rating: {r} | Reviews: {rc}")
    print(f"  HTML length: {len(html)}")
else:
    print(html)

time.sleep(3)

# 3. Houzz
print("\n=== HOUZZ: Bathroom Remodeling Vancouver WA ===")
houzz_url = 'https://www.houzz.com/professionals/general-contractors/bathroom-remodeling/vancouver--wa'
html = fetch_url(houzz_url)
if not html.startswith('ERROR'):
    biz_names = re.findall(r'"name":"([^"]{3,60})"', html)
    ratings = re.findall(r'"ratingValue":"?([\d.]+)"?', html)
    review_counts = re.findall(r'"reviewCount":"?(\d+)"?', html)
    
    print(f"Found {len(biz_names)} business names")
    for i, name in enumerate(biz_names[:15]):
        r = ratings[i] if i < len(ratings) else 'N/A'
        rc = review_counts[i] if i < len(review_counts) else 'N/A'
        print(f"  {i+1}. {name} | Rating: {r} | Reviews: {rc}")
    print(f"  HTML length: {len(html)}")
else:
    print(html)

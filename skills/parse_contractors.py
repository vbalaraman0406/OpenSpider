import requests
import json
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

url = 'https://www.thumbtack.com/wa/vancouver/bathroom-remodeling/'
r = requests.get(url, headers=headers, allow_redirects=True, timeout=15)

# Extract all JSON-LD blocks
ld_matches = re.findall(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', r.text, re.DOTALL)

contractors = []
for m in ld_matches:
    try:
        data = json.loads(m)
        if data.get('@type') == 'ItemList':
            for item in data.get('itemListElement', []):
                biz = item.get('item', {})
                name = biz.get('name', 'N/A')
                url_path = biz.get('url', '')
                full_url = 'https://www.thumbtack.com' + url_path if url_path.startswith('/') else url_path
                price = biz.get('priceRange', 'N/A')
                agg = biz.get('aggregateRating', {})
                rating = agg.get('ratingValue', 'N/A')
                reviews = agg.get('reviewCount', 'N/A')
                review_body = ''
                rev = biz.get('review', {})
                if rev:
                    review_body = rev.get('reviewBody', '')[:100]
                contractors.append({
                    'position': item.get('position', ''),
                    'name': name,
                    'rating': rating,
                    'reviews': reviews,
                    'price': price,
                    'url': full_url,
                    'review_snippet': review_body
                })
    except Exception as e:
        pass

# Also try tile installation page
url2 = 'https://www.thumbtack.com/wa/vancouver/tile-installation/'
try:
    r2 = requests.get(url2, headers=headers, allow_redirects=True, timeout=15)
    ld2 = re.findall(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', r2.text, re.DOTALL)
    for m in ld2:
        try:
            data = json.loads(m)
            if data.get('@type') == 'ItemList':
                for item in data.get('itemListElement', []):
                    biz = item.get('item', {})
                    name = biz.get('name', 'N/A')
                    # Skip duplicates
                    if any(c['name'] == name for c in contractors):
                        continue
                    url_path = biz.get('url', '')
                    full_url = 'https://www.thumbtack.com' + url_path if url_path.startswith('/') else url_path
                    price = biz.get('priceRange', 'N/A')
                    agg = biz.get('aggregateRating', {})
                    rating = agg.get('ratingValue', 'N/A')
                    reviews = agg.get('reviewCount', 'N/A')
                    review_body = ''
                    rev = biz.get('review', {})
                    if rev:
                        review_body = rev.get('reviewBody', '')[:100]
                    contractors.append({
                        'position': item.get('position', ''),
                        'name': name,
                        'rating': rating,
                        'reviews': reviews,
                        'price': price,
                        'url': full_url,
                        'review_snippet': review_body,
                        'source': 'tile-installation'
                    })
        except:
            pass
except:
    pass

print(f'Total contractors found: {len(contractors)}')
for c in contractors:
    src = c.get('source', 'bathroom-remodeling')
    print(f"{c['position']}|{c['name']}|{c['rating']}|{c['reviews']}|{c['price']}|{src}|{c['url']}")

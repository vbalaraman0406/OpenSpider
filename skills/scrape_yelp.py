import urllib.request
import urllib.parse
import re

url = "https://www.yelp.com/search?find_desc=bathroom+remodel+contractor&find_loc=Vancouver%2C+WA+98662"

req = urllib.request.Request(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'en-US,en;q=0.9'
})

try:
    with urllib.request.urlopen(req, timeout=20) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
    
    # Save for debugging
    with open('yelp_results.html', 'w') as f:
        f.write(html)
    
    # Try to find business names and ratings
    # Look for business card patterns
    # Yelp uses various patterns, let's try JSON-LD or structured data
    
    # Try finding business names in links like /biz/company-name
    biz_links = re.findall(r'/biz/([a-z0-9\-]+(?:vancouver|wa)[a-z0-9\-]*)', html, re.IGNORECASE)
    biz_links = list(dict.fromkeys(biz_links))  # dedupe
    
    print(f"Found {len(biz_links)} business links")
    for b in biz_links[:15]:
        print(f"  - {b}")
    
    # Also try to extract from aria-labels or alt text
    names = re.findall(r'aria-label="([^"]*?)"', html)
    ratings = [n for n in names if 'star' in n.lower() or 'rating' in n.lower()]
    biz_names = [n for n in names if 'star' not in n.lower() and 'rating' not in n.lower() and len(n) > 5 and len(n) < 80]
    
    print(f"\nBusiness-like aria labels ({len(biz_names)}):")
    for n in biz_names[:20]:
        print(f"  - {n}")
    
    print(f"\nRating aria labels ({len(ratings)}):")
    for r in ratings[:20]:
        print(f"  - {r}")

except Exception as e:
    print(f"Error: {e}")

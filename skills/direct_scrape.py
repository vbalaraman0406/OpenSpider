import urllib.request
import re

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Language': 'en-US,en;q=0.5'}

# Try Yelp direct
print('=== YELP ===')
try:
    url = 'https://www.yelp.com/biz/fazzolari-custom-homes-and-renovations-vancouver'
    req = urllib.request.Request(url, headers=headers)
    resp = urllib.request.urlopen(req, timeout=15)
    html = resp.read().decode('utf-8', errors='ignore')
    # Look for rating
    rating = re.findall(r'"ratingValue"[:\s]*([\d.]+)', html)
    review_count = re.findall(r'"reviewCount"[:\s]*([\d]+)', html)
    alt_rating = re.findall(r'(\d+\.?\d*)\s*star\s*rating', html, re.IGNORECASE)
    alt_reviews = re.findall(r'(\d+)\s*review', html, re.IGNORECASE)
    print(f'Rating (schema): {rating}')
    print(f'Review count (schema): {review_count}')
    print(f'Rating (alt): {alt_rating}')
    print(f'Reviews (alt): {alt_reviews[:5]}')
except Exception as e:
    print(f'Error: {e}')

# Try BBB direct
print()
print('=== BBB ===')
try:
    url = 'https://www.bbb.org/us/wa/vancouver/profile/home-builders/fazzolari-custom-homes-renovations-llc-1296-1000059498'
    req = urllib.request.Request(url, headers=headers)
    resp = urllib.request.urlopen(req, timeout=15)
    html = resp.read().decode('utf-8', errors='ignore')
    bbb_rating = re.findall(r'BBB Rating[^A-F]*(A\+|A|A-|B\+|B|B-|C\+|C|C-|D\+|D|D-|F)', html)
    accredited = 'Accredited' if 'BBB Accredited' in html or 'accredited' in html.lower() else 'Not found'
    complaints = re.findall(r'(\d+)\s*complaint', html, re.IGNORECASE)
    print(f'BBB Rating: {bbb_rating}')
    print(f'Accredited: {accredited}')
    print(f'Complaints: {complaints}')
except Exception as e:
    print(f'Error: {e}')

# Try Google search via startpage or searx
print()
print('=== GOOGLE MAPS SEARCH ===')
try:
    query = urllib.parse.quote_plus('Fazzolari Custom Homes Vancouver WA reviews')
    url = f'https://www.google.com/search?q={query}'
    req = urllib.request.Request(url, headers=headers)
    resp = urllib.request.urlopen(req, timeout=15)
    html = resp.read().decode('utf-8', errors='ignore')
    # Look for rating in Google results
    g_rating = re.findall(r'(\d\.\d)\s*\(\s*(\d+)\s*\)', html)
    g_stars = re.findall(r'Rated\s*(\d\.\d)', html)
    print(f'Google rating matches: {g_rating[:5]}')
    print(f'Google stars: {g_stars[:5]}')
except Exception as e:
    print(f'Error: {e}')

import urllib.parse

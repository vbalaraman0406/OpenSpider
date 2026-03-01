import urllib.request
import json
import re

# Try searching for Fazzolari on Google via a different search engine
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

# Try Bing search for Google reviews
print('=== BING SEARCH: Google Reviews ===')
try:
    q = 'Fazzolari+Custom+Homes+Vancouver+WA+google+reviews+rating'
    url = f'https://www.bing.com/search?q={q}'
    req = urllib.request.Request(url, headers=headers)
    resp = urllib.request.urlopen(req, timeout=15)
    html = resp.read().decode('utf-8', errors='ignore')
    # Look for rating patterns
    rating_patterns = re.findall(r'(\d\.\d)\s*(?:out of 5|stars?|/5|rating)', html, re.IGNORECASE)
    review_patterns = re.findall(r'(\d+)\s*(?:reviews?|Google reviews?)', html, re.IGNORECASE)
    print(f'Rating matches: {rating_patterns[:5]}')
    print(f'Review count matches: {review_patterns[:5]}')
    # Also look for snippets mentioning Fazzolari
    snippets = re.findall(r'Fazzolari[^<]{0,200}', html)
    for s in snippets[:3]:
        print(f'Snippet: {s.strip()}')
except Exception as e:
    print(f'Error: {e}')

# Try Bing search for Yelp reviews
print('\n=== BING SEARCH: Yelp Reviews ===')
try:
    q = 'Fazzolari+Custom+Homes+Vancouver+WA+yelp+reviews'
    url = f'https://www.bing.com/search?q={q}'
    req = urllib.request.Request(url, headers=headers)
    resp = urllib.request.urlopen(req, timeout=15)
    html = resp.read().decode('utf-8', errors='ignore')
    rating_patterns = re.findall(r'(\d\.\d)\s*(?:star|rating)', html, re.IGNORECASE)
    review_patterns = re.findall(r'(\d+)\s*(?:reviews?)', html, re.IGNORECASE)
    print(f'Rating matches: {rating_patterns[:5]}')
    print(f'Review count matches: {review_patterns[:5]}')
    snippets = re.findall(r'Fazzolari[^<]{0,200}', html)
    for s in snippets[:3]:
        print(f'Snippet: {s.strip()}')
except Exception as e:
    print(f'Error: {e}')

# Try Houzz
print('\n=== HOUZZ ===')
try:
    url = 'https://www.houzz.com/professionals/general-contractors/fazzolari-custom-homes-and-renovations-pfvwus-pf~1533498709'
    req = urllib.request.Request(url, headers=headers)
    resp = urllib.request.urlopen(req, timeout=15)
    html = resp.read().decode('utf-8', errors='ignore')
    rating = re.findall(r'(\d\.\d)\s*(?:out of|stars?|average)', html, re.IGNORECASE)
    reviews = re.findall(r'(\d+)\s*(?:reviews?)', html, re.IGNORECASE)
    print(f'Rating: {rating[:5]}')
    print(f'Reviews: {reviews[:5]}')
except Exception as e:
    print(f'Error: {e}')

# Try Google Business search via startpage
print('\n=== STARTPAGE SEARCH ===')
try:
    q = 'Fazzolari+Custom+Homes+Renovations+Vancouver+WA+reviews'
    url = f'https://www.startpage.com/do/search?q={q}'
    req = urllib.request.Request(url, headers=headers)
    resp = urllib.request.urlopen(req, timeout=15)
    html = resp.read().decode('utf-8', errors='ignore')
    snippets = re.findall(r'Fazzolari[^<]{0,200}', html)
    for s in snippets[:3]:
        print(f'Snippet: {s.strip()}')
except Exception as e:
    print(f'Error: {e}')

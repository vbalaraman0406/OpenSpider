import requests
from bs4 import BeautifulSoup
import re
import json

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

# Try Yelp direct page
try:
    url = 'https://www.yelp.com/biz/beto-and-son-remodeling-vancouver'
    r = requests.get(url, headers=headers, timeout=10)
    print(f'=== Yelp Direct: {r.status_code} ===')
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, 'html.parser')
        # Look for rating in JSON-LD
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and 'aggregateRating' in data:
                    print(f"Rating: {data['aggregateRating']}")
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and 'aggregateRating' in item:
                            print(f"Rating: {item['aggregateRating']}")
            except: pass
        # Look for rating in meta tags
        for meta in soup.find_all('meta'):
            content = meta.get('content', '')
            if 'rating' in str(meta).lower() or 'review' in str(meta).lower():
                print(f"Meta: {meta}")
        # Title
        title = soup.find('title')
        if title:
            print(f"Title: {title.text[:200]}")
except Exception as e:
    print(f'Yelp error: {e}')

# Try Yelp search
try:
    url = 'https://www.yelp.com/search?find_desc=Beto+and+Son+Remodeling&find_loc=Vancouver+WA'
    r = requests.get(url, headers=headers, timeout=10)
    print(f'\n=== Yelp Search: {r.status_code} ===')
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, 'html.parser')
        # Find rating mentions
        text = soup.get_text()
        beto_idx = text.lower().find('beto')
        if beto_idx >= 0:
            snippet = text[max(0,beto_idx-50):beto_idx+300]
            print(f"Found Beto mention: {snippet[:400]}")
        else:
            print('No Beto mention found in search results')
except Exception as e:
    print(f'Yelp search error: {e}')

# Try Houzz
try:
    url = 'https://www.houzz.com/professionals/general-contractor/beto-and-son-remodeling-pfvwus-pf~1234567890'
    r = requests.get(url, headers=headers, timeout=10)
    print(f'\n=== Houzz: {r.status_code} ===')
except Exception as e:
    print(f'Houzz error: {e}')

# Try searching Brave for Yelp rating specifically
try:
    url = 'https://search.brave.com/search?q=Beto+Son+Remodeling+Vancouver+WA+yelp+rating+stars'
    r = requests.get(url, headers=headers, timeout=10)
    print(f'\n=== Brave Yelp Search: {r.status_code} ===')
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, 'html.parser')
        for item in soup.select('.snippet-description, .snippet-content, .result-snippet'):
            text = item.get_text(strip=True)
            if any(w in text.lower() for w in ['beto', 'rating', 'star', 'review']):
                print(f"Snippet: {text[:300]}")
        # Also check all text for rating patterns
        full = soup.get_text()
        for m in re.finditer(r'(\d\.\d)\s*(star|rating|out of)', full, re.I):
            start = max(0, m.start()-80)
            print(f"Rating match: {full[start:m.end()+50]}")
except Exception as e:
    print(f'Brave error: {e}')

import urllib.request
import re
import json

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# Try Yelp search
try:
    url = 'https://www.yelp.com/search?find_desc=Let%27s+Remodel&find_loc=Vancouver+WA+98662'
    req = urllib.request.Request(url, headers=headers)
    resp = urllib.request.urlopen(req, timeout=15)
    html = resp.read().decode('utf-8', errors='ignore')
    
    # Look for Let's Remodel on Yelp
    # Find rating patterns near "Let's Remodel" or "Lets Remodel"
    lower = html.lower()
    idx = lower.find("let's remodel")
    if idx == -1:
        idx = lower.find('lets remodel')
    if idx == -1:
        idx = lower.find('let&#39;s remodel')
    
    if idx > -1:
        snippet = html[max(0,idx-500):idx+1500]
        print('=== YELP SNIPPET ===')
        # Extract rating
        ratings = re.findall(r'(\d\.\d)\s*(?:star|rating)', snippet, re.IGNORECASE)
        reviews = re.findall(r'(\d+)\s*(?:review)', snippet, re.IGNORECASE)
        print(f'Ratings found: {ratings}')
        print(f'Reviews found: {reviews}')
        # Also look for aria-label with rating
        aria_ratings = re.findall(r'aria-label="(\d+\.?\d*)\s*star', snippet, re.IGNORECASE)
        print(f'Aria ratings: {aria_ratings}')
        # Print clean text snippet
        clean = re.sub(r'<[^>]+>', ' ', snippet)
        clean = re.sub(r'\s+', ' ', clean).strip()
        print(f'Clean text: {clean[:800]}')
    else:
        print('Let\'s Remodel not found on Yelp search page')
        # Save first 3000 chars for debugging
        clean = re.sub(r'<[^>]+>', ' ', html)
        clean = re.sub(r'\s+', ' ', clean).strip()
        print(f'Yelp page text (first 1000): {clean[:1000]}')
except Exception as e:
    print(f'Yelp error: {e}')

print('\n' + '='*50)

# Try Google Maps / Google Business search via DuckDuckGo
try:
    url = 'https://html.duckduckgo.com/html/?q=Let%27s+Remodel+Vancouver+WA+google+reviews+rating'
    req = urllib.request.Request(url, headers=headers)
    resp = urllib.request.urlopen(req, timeout=15)
    html = resp.read().decode('utf-8', errors='ignore')
    clean = re.sub(r'<[^>]+>', ' ', html)
    clean = re.sub(r'\s+', ' ', clean).strip()
    
    # Find relevant snippets
    lower = clean.lower()
    for term in ["let's remodel", 'lets remodel', 'letsremodel']:
        idx = lower.find(term)
        if idx > -1:
            print(f'\n=== DDG snippet for "{term}" ===')
            print(clean[max(0,idx-100):idx+400])
except Exception as e:
    print(f'DDG error: {e}')

print('\n' + '='*50)

# Try BBB
try:
    url = 'https://html.duckduckgo.com/html/?q=Let%27s+Remodel+Portland+OR+BBB+rating'
    req = urllib.request.Request(url, headers=headers)
    resp = urllib.request.urlopen(req, timeout=15)
    html = resp.read().decode('utf-8', errors='ignore')
    clean = re.sub(r'<[^>]+>', ' ', html)
    clean = re.sub(r'\s+', ' ', clean).strip()
    lower = clean.lower()
    for term in ["let's remodel", 'lets remodel', 'letsremodel']:
        idx = lower.find(term)
        if idx > -1:
            print(f'\n=== BBB snippet for "{term}" ===')
            print(clean[max(0,idx-100):idx+400])
except Exception as e:
    print(f'BBB error: {e}')

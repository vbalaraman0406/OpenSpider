import requests
from bs4 import BeautifulSoup
import re
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Get services pages
print('=== SERVICES ===')
for page in ['remodeling', 'new-homes', 'bathroom-remodel', 'kitchen-remodel']:
    url = f'https://www.mountainwoodhomes.com/{page}/'
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            title = soup.find('title')
            print(f'{page}: {title.get_text(strip=True) if title else "No title"}')
            # Get meta description
            meta = soup.find('meta', attrs={'name': 'description'})
            if meta:
                print(f'  Desc: {meta.get("content", "")[:200]}')
        else:
            print(f'{page}: HTTP {resp.status_code}')
    except Exception as e:
        print(f'{page}: Error - {e}')

# Try to find all service links from main nav
print('\n=== NAV LINKS ===')
resp = requests.get('https://www.mountainwoodhomes.com/', headers=headers, timeout=10)
soup = BeautifulSoup(resp.text, 'html.parser')
nav = soup.find('nav')
if nav:
    links = nav.find_all('a')
    seen = set()
    for link in links:
        href = link.get('href', '')
        text = link.get_text(strip=True)
        if href and text and href not in seen:
            seen.add(href)
            print(f'  {text}: {href}')

# Search for Google reviews
print('\n=== GOOGLE REVIEWS SEARCH ===')
search_url = 'https://www.google.com/search?q=Mountainwood+Homes+Vancouver+WA+reviews'
try:
    resp = requests.get(search_url, headers=headers, timeout=10)
    soup = BeautifulSoup(resp.text, 'html.parser')
    text = soup.get_text(separator='\n', strip=True)
    # Look for rating patterns
    ratings = re.findall(r'(\d\.\d)\s*(?:out of|/|stars?)\s*(?:5)?.*?(?:(\d+)\s*(?:reviews?|ratings?))', text, re.IGNORECASE)
    print('Rating matches:', ratings)
    # Also look for just star ratings
    stars = re.findall(r'(\d\.\d)\s*[★⭐]', text)
    print('Star matches:', stars)
    # Look for review count
    rev_count = re.findall(r'(\d+)\s*(?:Google\s*)?reviews?', text, re.IGNORECASE)
    print('Review count matches:', rev_count)
    # Print relevant snippets
    for line in text.split('\n'):
        if any(kw in line.lower() for kw in ['rating', 'review', 'star', '4.', '5.', 'out of']):
            print(f'  >> {line[:150]}')
except Exception as e:
    print(f'Error: {e}')

# Search Yelp
print('\n=== YELP SEARCH ===')
yelp_url = 'https://www.yelp.com/search?find_desc=Mountainwood+Homes&find_loc=Vancouver+WA'
try:
    resp = requests.get(yelp_url, headers=headers, timeout=10)
    soup = BeautifulSoup(resp.text, 'html.parser')
    text = soup.get_text(separator='\n', strip=True)
    for line in text.split('\n'):
        if 'mountainwood' in line.lower() or 'rating' in line.lower() or 'review' in line.lower():
            print(f'  >> {line[:150]}')
except Exception as e:
    print(f'Error: {e}')

# Search BBB
print('\n=== BBB SEARCH ===')
bbb_url = 'https://www.google.com/search?q=Mountainwood+Homes+BBB+rating'
try:
    resp = requests.get(bbb_url, headers=headers, timeout=10)
    soup = BeautifulSoup(resp.text, 'html.parser')
    text = soup.get_text(separator='\n', strip=True)
    for line in text.split('\n'):
        if any(kw in line.lower() for kw in ['bbb', 'better business', 'rating', 'accredited', 'a+', 'a-']):
            print(f'  >> {line[:150]}')
except Exception as e:
    print(f'Error: {e}')

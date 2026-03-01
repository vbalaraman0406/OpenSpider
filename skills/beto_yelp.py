import requests
from bs4 import BeautifulSoup
import re
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

# Try Yelp search
try:
    url = 'https://www.yelp.com/biz/beto-and-son-remodeling-vancouver'
    r = requests.get(url, headers=headers, timeout=15)
    print(f'Yelp status: {r.status_code}')
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # Look for rating in JSON-LD
    scripts = soup.find_all('script', type='application/ld+json')
    for s in scripts:
        try:
            data = json.loads(s.string)
            if isinstance(data, dict):
                if 'aggregateRating' in data:
                    print(f"Rating: {data['aggregateRating']}")
                if 'name' in data:
                    print(f"Name: {data['name']}")
                if 'telephone' in data:
                    print(f"Phone: {data['telephone']}")
                if 'address' in data:
                    print(f"Address: {data['address']}")
            elif isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and 'aggregateRating' in item:
                        print(f"Rating: {item['aggregateRating']}")
        except:
            pass
    
    # Look for rating in meta tags
    for meta in soup.find_all('meta'):
        content = meta.get('content', '')
        name = meta.get('name', '') or meta.get('property', '')
        if 'rating' in str(name).lower() or 'review' in str(name).lower():
            print(f"Meta {name}: {content}")
    
    # Title
    title = soup.find('title')
    if title:
        print(f"Title: {title.text[:200]}")
    
    # Look for rating patterns in text
    text = soup.get_text()[:3000]
    rating_matches = re.findall(r'(\d\.\d)\s*(?:star|rating)', text, re.I)
    review_matches = re.findall(r'(\d+)\s*review', text, re.I)
    if rating_matches:
        print(f"Rating matches: {rating_matches}")
    if review_matches:
        print(f"Review matches: {review_matches}")
        
except Exception as e:
    print(f'Yelp error: {e}')

# Try Google Maps search via Brave
try:
    url = 'https://search.brave.com/search?q=Beto+and+Son+Remodeling+Vancouver+WA+reviews+rating+google'
    r = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, 'html.parser')
    text = soup.get_text(' ', strip=True)[:2000]
    # Find rating patterns
    ratings = re.findall(r'(\d\.\d)\s*(?:star|rating|out of)', text, re.I)
    reviews = re.findall(r'(\d+)\s*(?:review|Google review)', text, re.I)
    print(f"\nBrave Google ratings: {ratings}")
    print(f"Brave Google reviews: {reviews}")
    # Print relevant snippet
    for line in text.split('\n'):
        if 'beto' in line.lower() and ('rating' in line.lower() or 'review' in line.lower() or 'star' in line.lower()):
            print(f"Relevant: {line[:300]}")
except Exception as e:
    print(f'Brave error: {e}')

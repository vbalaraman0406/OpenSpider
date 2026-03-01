import requests
from bs4 import BeautifulSoup
import re
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

url = 'https://www.yelp.com/biz/beto-and-son-remodeling-vancouver'
r = requests.get(url, headers=headers, timeout=15)
html = r.text

# Extract rating from JSON-LD
jsonld = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL)
for j in jsonld:
    try:
        data = json.loads(j)
        if isinstance(data, dict):
            if 'aggregateRating' in data:
                ar = data['aggregateRating']
                print(f"Rating: {ar.get('ratingValue')}")
                print(f"Review Count: {ar.get('reviewCount')}")
            if 'name' in data:
                print(f"Name: {data['name']}")
            if 'telephone' in data:
                print(f"Phone: {data['telephone']}")
            if 'address' in data:
                print(f"Address: {data['address']}")
            if 'url' in data:
                print(f"URL: {data['url']}")
    except:
        pass

# Fallback: search for rating in aria labels
rating_match = re.search(r'(\d+\.?\d*)\s*star rating', html)
if rating_match:
    print(f"Fallback Rating: {rating_match.group(1)}")

review_match = re.search(r'(\d+)\s*review', html)
if review_match:
    print(f"Fallback Reviews: {review_match.group(1)}")

# Check for categories
cat_match = re.findall(r'"category"\s*:\s*"([^"]+)"', html)
if cat_match:
    print(f"Categories: {cat_match}")

# Look for phone in page
phone_match = re.findall(r'\(\d{3}\)\s*\d{3}-\d{4}', html)
if phone_match:
    print(f"Phone numbers found: {list(set(phone_match))}")

print(f"\nPage length: {len(html)}")

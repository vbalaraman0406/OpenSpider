import requests
import re
import json
from html.parser import HTMLParser

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

contractors = []

# Try Thumbtack
try:
    url = 'https://www.thumbtack.com/wa/vancouver/bathroom-remodeling/'
    r = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
    print(f'Thumbtack status: {r.status_code}, length: {len(r.text)}')
    
    # Extract JSON-LD data
    ld_matches = re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', r.text, re.DOTALL)
    for m in ld_matches:
        try:
            data = json.loads(m)
            if isinstance(data, list):
                for item in data:
                    if item.get('@type') == 'LocalBusiness' or item.get('@type') == 'HomeAndConstructionBusiness':
                        name = item.get('name', '')
                        rating = item.get('aggregateRating', {}).get('ratingValue', 'N/A')
                        reviews = item.get('aggregateRating', {}).get('reviewCount', 'N/A')
                        phone = item.get('telephone', 'N/A')
                        website = item.get('url', 'N/A')
                        contractors.append({'name': name, 'rating': rating, 'reviews': reviews, 'phone': phone, 'website': website, 'source': 'Thumbtack'})
            elif isinstance(data, dict):
                if data.get('@type') in ['LocalBusiness', 'HomeAndConstructionBusiness']:
                    contractors.append({'name': data.get('name',''), 'rating': data.get('aggregateRating',{}).get('ratingValue','N/A'), 'reviews': data.get('aggregateRating',{}).get('reviewCount','N/A'), 'phone': data.get('telephone','N/A'), 'website': data.get('url','N/A'), 'source': 'Thumbtack'})
        except:
            pass
    
    # Also try regex patterns for contractor cards
    if not contractors:
        # Look for rating patterns
        names = re.findall(r'"name"\s*:\s*"([^"]+)"', r.text)
        ratings = re.findall(r'"ratingValue"\s*:\s*"?([\d.]+)"?', r.text)
        review_counts = re.findall(r'"reviewCount"\s*:\s*"?(\d+)"?', r.text)
        print(f'Found {len(names)} names, {len(ratings)} ratings, {len(review_counts)} review counts')
        for i, name in enumerate(names[:20]):
            if any(skip in name.lower() for skip in ['thumbtack', 'bathroom', 'remodel', 'vancouver']):
                continue
            c = {'name': name, 'rating': ratings[i] if i < len(ratings) else 'N/A', 'reviews': review_counts[i] if i < len(review_counts) else 'N/A', 'phone': 'N/A', 'website': 'N/A', 'source': 'Thumbtack'}
            contractors.append(c)
except Exception as e:
    print(f'Thumbtack error: {e}')

# Try Google
try:
    gurl = 'https://www.google.com/search?q=best+rated+bathroom+remodel+contractors+Vancouver+WA+98662&num=20'
    r = requests.get(gurl, headers=headers, timeout=15)
    print(f'Google status: {r.status_code}, length: {len(r.text)}')
    # Extract visible text snippets with contractor names and ratings
    # Look for patterns like "4.8 (123)" or "★" near business names
    text = re.sub(r'<[^>]+>', ' ', r.text)
    text = re.sub(r'\s+', ' ', text)
    # Print first 2000 chars for analysis
    print(text[:2000])
except Exception as e:
    print(f'Google error: {e}')

print(f'\n=== FOUND {len(contractors)} CONTRACTORS ===')
for c in contractors:
    print(f"{c['name']} | {c['rating']} | {c['reviews']} | {c['phone']} | {c['website']} | {c['source']}")

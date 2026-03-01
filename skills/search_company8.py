import urllib.request
import urllib.parse
import re
import json

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

# Try multiple Google queries
queries = [
    '"Let\'s Remodel" Vancouver WA bathroom contractor',
    '"Lets Remodel" Vancouver WA 98662',
    '"Let\'s Remodel" LLC Washington contractor',
    '"Let\'s Remodel" bathroom remodel Portland Vancouver',
    'site:yelp.com "Let\'s Remodel" Vancouver WA',
    'site:facebook.com "Let\'s Remodel" Vancouver WA bathroom',
    '"Let\'s Remodel" contractor reviews'
]

for q in queries:
    print(f'\n=== Query: {q} ===')
    try:
        url = 'https://www.google.com/search?q=' + urllib.parse.quote(q) + '&num=5'
        req = urllib.request.Request(url, headers=headers)
        resp = urllib.request.urlopen(req, timeout=10)
        html = resp.read().decode('utf-8', errors='ignore')
        
        # Extract titles and URLs from Google results
        # Google result links pattern
        links = re.findall(r'<a href="/url\?q=([^&"]+)', html)
        titles = re.findall(r'<h3[^>]*>(.*?)</h3>', html)
        phones = re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', html)
        ratings = re.findall(r'(\d\.\d)\s*(?:star|rating|out of)', html, re.I)
        reviews = re.findall(r'(\d+)\s*(?:review|rating)', html, re.I)
        
        # Clean titles
        clean_titles = [re.sub(r'<[^>]+>', '', t) for t in titles[:5]]
        
        print(f'Titles: {clean_titles}')
        print(f'Links: {links[:5]}')
        print(f'Phones: {phones[:3]}')
        print(f'Ratings: {ratings[:3]}')
        print(f'Reviews: {reviews[:3]}')
        
        # Also look for address patterns
        addresses = re.findall(r'\d+\s+[A-Z][a-zA-Z\s]+(?:St|Ave|Blvd|Dr|Rd|Way|Ln|Ct|Hwy)[^<]{0,50}(?:Vancouver|Portland)[^<]{0,30}(?:WA|OR)\s*\d{5}', html)
        if addresses:
            print(f'Addresses: {addresses[:3]}')
            
    except Exception as e:
        print(f'ERROR: {e}')

print('\nDone with search round 8')
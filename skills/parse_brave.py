import urllib.request
import re
import json

contractors = {}

queries = [
    'bathroom+remodeling+contractors+Vancouver+WA+98662+reviews+ratings',
    'bathroom+tile+contractor+Vancouver+WA+98662',
    'best+bathroom+renovation+contractor+Vancouver+Washington',
    'bathroom+vanity+installation+Vancouver+WA+reviews'
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'en-US,en;q=0.9'
}

for q in queries:
    url = f'https://search.brave.com/search?q={q}'
    try:
        req = urllib.request.Request(url, headers=headers)
        resp = urllib.request.urlopen(req, timeout=15)
        html = resp.read().decode('utf-8', errors='ignore')
        
        # Extract snippets with business info
        # Look for rating patterns like X.X stars, X.X/5, (XXX reviews)
        # Look for phone patterns
        # Look for business names in title tags
        
        titles = re.findall(r'<title[^>]*>(.*?)</title>', html, re.DOTALL)
        
        # Extract all text snippets
        text = re.sub(r'<[^>]+>', ' ', html)
        text = re.sub(r'\s+', ' ', text)
        
        # Find business names with ratings
        # Pattern: Company Name ... X.X ... stars/rating ... reviews
        rating_blocks = re.findall(r'([A-Z][A-Za-z&\' ]+(?:LLC|Inc|Co|Construction|Remodel(?:ing)?|Tile|Bath|Home|Kitchen|Renovation|Plumbing|Design|Services|Solutions|Improvement|Contracting)?[A-Za-z ]*?)\s*[\-\|·]?\s*(\d\.\d)\s*(?:stars?|rating|/5|out of)', text, re.IGNORECASE)
        
        for name, rating in rating_blocks:
            name = name.strip().strip('-|·').strip()
            if len(name) > 3 and len(name) < 60:
                if name not in contractors:
                    contractors[name] = {'rating': rating, 'reviews': '', 'contact': '', 'source': 'Brave Search'}
        
        # Find phone numbers near business context
        phones = re.findall(r'(\(\d{3}\)\s*\d{3}[\-.]\d{4}|\d{3}[\-.]\d{3}[\-.]\d{4})', text)
        
        # Find review counts
        review_matches = re.findall(r'(\d+)\s*(?:reviews?|ratings?)', text, re.IGNORECASE)
        
        # Try broader name extraction - look for known contractor patterns
        biz_patterns = re.findall(r'([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){0,3}\s+(?:Construction|Remodeling|Renovation|Tile|Contracting|Home\s*Improvement|Bath|Plumbing|Design|Services|Solutions|LLC|Inc))', text)
        
        for biz in biz_patterns:
            biz = biz.strip()
            if len(biz) > 5 and len(biz) < 60 and biz not in contractors:
                contractors[biz] = {'rating': '', 'reviews': '', 'contact': '', 'source': 'Brave Search'}
        
        print(f'Query: {q[:50]}... Found {len(rating_blocks)} rated, {len(biz_patterns)} businesses, {len(phones)} phones')
        
    except Exception as e:
        print(f'Error for query {q[:30]}: {e}')

print(f'\nTotal unique contractors found: {len(contractors)}')
for name, info in contractors.items():
    print(f'  {name} | Rating: {info["rating"]} | Reviews: {info["reviews"]} | Contact: {info["contact"]} | Source: {info["source"]}')

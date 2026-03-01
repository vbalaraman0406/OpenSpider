import urllib.request
import json
import re

url = 'https://www.thumbtack.com/wa/vancouver/bathroom-remodeling/'
req = urllib.request.Request(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9'
})
try:
    resp = urllib.request.urlopen(req, timeout=15)
    html = resp.read().decode('utf-8', errors='ignore')
    
    # Extract JSON-LD data
    jsonld_matches = re.findall(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html, re.DOTALL)
    contractors = []
    for jm in jsonld_matches:
        try:
            data = json.loads(jm)
            if isinstance(data, list):
                for item in data:
                    if item.get('@type') in ['LocalBusiness', 'HomeAndConstructionBusiness', 'Service', 'ProfessionalService']:
                        name = item.get('name', 'N/A')
                        rating = item.get('aggregateRating', {}).get('ratingValue', 'N/A')
                        reviews = item.get('aggregateRating', {}).get('reviewCount', 'N/A')
                        phone = item.get('telephone', 'N/A')
                        website = item.get('url', 'N/A')
                        contractors.append({'name': name, 'rating': rating, 'reviews': reviews, 'phone': phone, 'website': website})
            elif isinstance(data, dict):
                if data.get('@type') in ['LocalBusiness', 'HomeAndConstructionBusiness', 'Service', 'ProfessionalService']:
                    contractors.append({'name': data.get('name','N/A'), 'rating': data.get('aggregateRating',{}).get('ratingValue','N/A'), 'reviews': data.get('aggregateRating',{}).get('reviewCount','N/A'), 'phone': data.get('telephone','N/A'), 'website': data.get('url','N/A')})
        except:
            pass
    
    # Also try to find contractor cards in HTML
    # Look for patterns like rating and name
    name_matches = re.findall(r'"displayName"\s*:\s*"([^"]+)"', html)
    rating_matches = re.findall(r'"rating"\s*:\s*([\d.]+)', html)
    review_matches = re.findall(r'"numReviews"\s*:\s*(\d+)', html)
    
    if not contractors and name_matches:
        for i, name in enumerate(name_matches[:20]):
            r = rating_matches[i] if i < len(rating_matches) else 'N/A'
            rv = review_matches[i] if i < len(review_matches) else 'N/A'
            contractors.append({'name': name, 'rating': r, 'reviews': rv, 'phone': 'N/A', 'website': f'https://www.thumbtack.com (search {name})'})
    
    # Also try __NEXT_DATA__ JSON
    next_data = re.search(r'<script[^>]*id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
    if next_data and not contractors:
        try:
            nd = json.loads(next_data.group(1))
            # Try to navigate the structure
            props = nd.get('props', {}).get('pageProps', {})
            results = props.get('searchResults', props.get('results', []))
            if isinstance(results, list):
                for r in results[:20]:
                    name = r.get('name', r.get('displayName', r.get('businessName', 'N/A')))
                    rat = r.get('rating', r.get('averageRating', 'N/A'))
                    rev = r.get('numReviews', r.get('reviewCount', 'N/A'))
                    ph = r.get('phone', r.get('phoneNumber', 'N/A'))
                    contractors.append({'name': name, 'rating': rat, 'reviews': rev, 'phone': ph, 'website': 'Thumbtack'})
        except:
            pass
    
    print(f'Found {len(contractors)} contractors from Thumbtack')
    for c in contractors:
        print(f"{c['name']} | {c['rating']} | {c['reviews']} | {c['phone']} | {c['website']}")
    
    if not contractors:
        # Print first 2000 chars for debugging
        print('NO CONTRACTORS FOUND. HTML snippet:')
        print(html[:2000])
except Exception as e:
    print(f'Error: {e}')

import urllib.request
import re
import json

url = 'https://letsremodel.net'
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    resp = urllib.request.urlopen(req, timeout=15)
    html = resp.read().decode('utf-8', errors='ignore')
    
    # Title
    title = re.search(r'<title>(.*?)</title>', html, re.I|re.S)
    print('Title:', title.group(1).strip() if title else 'N/A')
    
    # Phone numbers
    phones = re.findall(r'(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})', html)
    unique_phones = list(set(phones))
    print('Phones:', unique_phones)
    
    # Ratings / reviews
    ratings = re.findall(r'(\d\.\d)\s*(?:out of|/|stars|rating)', html, re.I)
    print('Ratings:', ratings)
    
    # JSON-LD structured data
    jsonld = re.findall(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html, re.S|re.I)
    for j in jsonld:
        try:
            data = json.loads(j)
            print('JSON-LD:', json.dumps(data, indent=2)[:2000])
        except:
            pass
    
    # Look for address/location
    addresses = re.findall(r'Vancouver|Portland|WA|Oregon|OR|98\d{3}|97\d{3}', html)
    print('Location mentions:', list(set(addresses))[:10])
    
    # Look for review counts
    review_counts = re.findall(r'(\d+)\s*(?:reviews?|testimonials?)', html, re.I)
    print('Review counts:', review_counts)
    
    # Look for services mentioned
    services = re.findall(r'(?:bathroom|tile|vanity|floor|wall|remodel|renovation|kitchen)[^<]{0,100}', html, re.I)
    print('Services mentions:', services[:10])
    
    # Meta description
    meta = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\'>]+)', html, re.I)
    print('Meta desc:', meta.group(1) if meta else 'N/A')
    
except Exception as e:
    print(f'Error: {e}')

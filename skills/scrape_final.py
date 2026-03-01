import urllib.request
import re
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

urls = {
    'Reliable Men - BuildZoom': 'https://www.buildzoom.com/contractor/reliable-men-construction-llc',
    'Reliable Men - Angi': 'https://www.angi.com/companylist/us/wa/vancouver/reliable-men-construction-reviews-10825460.htm',
    'Lets Remodel - Thumbtack': 'https://www.thumbtack.com/wa/vancouver/bathroom-remodeling/lets-remodel/service/441227816498225179',
    'Beto Son - ExactSeek': 'https://local.exactseek.com/detail/beto-and-son-remodeling-llc-581938',
    'Beto Son - AllRatings': 'https://www.oneallratings.com/company/beto-son-remodeling-wa-vancouver',
    'Lets Remodel site': 'https://www.letsremodel.com',
}

for name, url in urls.items():
    print(f'\n=== {name} ===')
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        resp = urllib.request.urlopen(req, timeout=10, context=ctx)
        html = resp.read().decode('utf-8', errors='ignore')
        
        # Extract title
        t = re.search(r'<title[^>]*>(.*?)</title>', html, re.I|re.S)
        title = t.group(1).strip() if t else 'N/A'
        print(f'Title: {title}')
        
        # Extract phones
        phones = re.findall(r'[\(]?\d{3}[\)\-\.\s]?\s?\d{3}[\-\.\s]\d{4}', html)
        phones = list(set(phones))[:5]
        print(f'Phones: {phones}')
        
        # Extract ratings
        ratings = re.findall(r'(?:rating|score|stars?)[^>]*?([\d\.]+)\s*(?:out of|/)?\s*5', html, re.I)
        print(f'Ratings found: {ratings[:5]}')
        
        # JSON-LD
        jld = re.findall(r'"aggregateRating"\s*:\s*\{[^}]+\}', html)
        for j in jld[:2]:
            print(f'AggregateRating: {j}')
        
        # Review count
        revs = re.findall(r'(\d+)\s*(?:reviews?|ratings?)', html, re.I)
        print(f'Review counts: {revs[:5]}')
        
        # Address
        addrs = re.findall(r'Vancouver\s*,?\s*WA\s*\d{5}', html)
        print(f'Addresses: {list(set(addrs))[:3]}')
        
        # License
        lics = re.findall(r'(?:license|lic)[^<]{0,50}(?:RELIA|#)[^<]{0,30}', html, re.I)
        print(f'Licenses: {lics[:3]}')
        
        # First 500 chars of visible text for context
        text = re.sub(r'<[^>]+>', ' ', html)
        text = re.sub(r'\s+', ' ', text).strip()
        print(f'Text preview: {text[:500]}')
        
    except Exception as e:
        print(f'Error: {e}')

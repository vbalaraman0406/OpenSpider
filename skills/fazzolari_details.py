import urllib.request
import re
import html

urls = {
    'website': 'https://fazzhomes.com/',
    'buildzoom': 'https://www.buildzoom.com/contractor/fazzolari-custom-homes-inc',
}

for name, url in urls.items():
    print(f'\n=== {name.upper()} ===')
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        resp = urllib.request.urlopen(req, timeout=10)
        raw = resp.read().decode('utf-8', errors='replace')
        
        # Extract title
        title = re.search(r'<title>(.*?)</title>', raw, re.S)
        if title:
            print(f'Title: {html.unescape(title.group(1).strip())}')
        
        # Extract phone numbers
        phones = re.findall(r'[\(]?\d{3}[\)\-\.\s]?\s?\d{3}[\-\.\s]\d{4}', raw)
        if phones:
            print(f'Phones: {list(set(phones))}')
        
        # Extract ratings
        ratings = re.findall(r'(?:rating|score|stars?)[^>]*?([\d\.]+)\s*(?:/\s*5|out of|stars)', raw, re.I)
        if ratings:
            print(f'Ratings found: {ratings}')
        
        # Look for review count
        reviews = re.findall(r'(\d+)\s*(?:reviews?|ratings?)', raw, re.I)
        if reviews:
            print(f'Review counts: {reviews}')
        
        # Extract meta description
        meta = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)["\']', raw, re.I)
        if meta:
            print(f'Meta desc: {html.unescape(meta.group(1).strip())}')
        
        # Look for address
        addrs = re.findall(r'\d+\s+(?:NW|NE|SW|SE|N|S|E|W)?\s*[\w\s]+(?:Ave|St|Blvd|Dr|Ct|Rd|Way|Ln)[^<]{0,50}(?:WA|Washington)[^<]{0,20}\d{5}', raw, re.I)
        if addrs:
            print(f'Addresses: {addrs[:3]}')
        
        # Look for services/bathroom keywords
        bath_mentions = re.findall(r'[^.]*(?:bathroom|bath|tile|vanity|remodel)[^.]*\.', raw, re.I)
        if bath_mentions:
            print(f'Bathroom mentions ({len(bath_mentions)}):')
            for m in bath_mentions[:5]:
                clean = re.sub(r'<[^>]+>', '', m).strip()
                if len(clean) > 20:
                    print(f'  - {clean[:200]}')
        
        # BZ specific: score
        bz_score = re.findall(r'BZ\s*(?:Score|Rating)[^\d]*(\d+)', raw, re.I)
        if bz_score:
            print(f'BuildZoom Score: {bz_score}')
            
        # License info
        lic = re.findall(r'(?:license|lic|UBI|registration)[^<]{0,100}', raw, re.I)
        if lic:
            print(f'License info: {lic[:3]}')
            
    except Exception as e:
        print(f'Error: {e}')

# Also search for Google rating
print('\n=== GOOGLE RATING SEARCH ===')
try:
    url = 'https://html.duckduckgo.com/html/?q=Fazzolari+Custom+Homes+Renovations+Vancouver+WA+google+reviews+rating'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    resp = urllib.request.urlopen(req, timeout=10)
    raw = resp.read().decode('utf-8', errors='replace')
    results = re.findall(r'<a[^>]*class="result__a"[^>]*>(.*?)</a>.*?<a[^>]*class="result__snippet"[^>]*>(.*?)</a>', raw, re.S)
    for i, (t, s) in enumerate(results[:5]):
        t_clean = re.sub(r'<[^>]+>', '', t).strip()
        s_clean = re.sub(r'<[^>]+>', '', s).strip()
        print(f'\n--- Result {i+1} ---')
        print(f'Title: {html.unescape(t_clean)}')
        print(f'Snippet: {html.unescape(s_clean[:300])}')
except Exception as e:
    print(f'Error: {e}')

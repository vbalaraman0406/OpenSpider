import urllib.request
import urllib.parse
import re
import json
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

contractors = []

queries = [
    'best rated bathroom remodel contractors Vancouver WA 98662',
    'top bathroom tile vanity contractors Vancouver Washington',
    'bathroom renovation contractors Vancouver WA reviews'
]

for q in queries:
    try:
        url = 'https://html.duckduckgo.com/html/?q=' + urllib.parse.quote(q)
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        resp = urllib.request.urlopen(req, timeout=15)
        html = resp.read().decode('utf-8', errors='ignore')
        
        # Extract result snippets
        results = re.findall(r'class="result__snippet">(.*?)</a>', html, re.DOTALL)
        titles = re.findall(r'class="result__a"[^>]*>(.*?)</a>', html, re.DOTALL)
        urls = re.findall(r'class="result__url"[^>]*>(.*?)</a>', html, re.DOTALL)
        
        print(f'Query: {q}')
        print(f'Found {len(titles)} titles, {len(results)} snippets, {len(urls)} urls')
        
        for i in range(min(len(titles), 10)):
            t = re.sub(r'<[^>]+>', '', titles[i]).strip()
            s = re.sub(r'<[^>]+>', '', results[i]).strip() if i < len(results) else ''
            u = re.sub(r'<[^>]+>', '', urls[i]).strip() if i < len(urls) else ''
            print(f'  [{i}] {t}')
            print(f'       URL: {u}')
            print(f'       Snippet: {s[:200]}')
            
            # Extract phone numbers
            phones = re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', s)
            # Extract ratings
            ratings = re.findall(r'(\d\.\d)\s*(?:star|rating|/5|out of)', s, re.I)
            if not ratings:
                ratings = re.findall(r'(\d\.\d)/5', s)
            
            if phones:
                print(f'       Phone: {phones[0]}')
            if ratings:
                print(f'       Rating: {ratings[0]}')
    except Exception as e:
        print(f'Error for query {q}: {e}')

# Also try Thumbtack directly
try:
    turl = 'https://www.thumbtack.com/wa/vancouver/bathroom-remodeling/'
    req = urllib.request.Request(turl, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml'
    })
    resp = urllib.request.urlopen(req, timeout=15)
    html = resp.read().decode('utf-8', errors='ignore')
    
    # Try JSON-LD
    ld_blocks = re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.DOTALL)
    print(f'\nThumbtack: Found {len(ld_blocks)} JSON-LD blocks')
    for block in ld_blocks:
        try:
            data = json.loads(block)
            if isinstance(data, list):
                for item in data[:10]:
                    if item.get('@type') in ['LocalBusiness', 'HomeAndConstructionBusiness', 'Service']:
                        name = item.get('name', '')
                        rating = item.get('aggregateRating', {}).get('ratingValue', 'N/A')
                        reviews = item.get('aggregateRating', {}).get('reviewCount', 'N/A')
                        phone = item.get('telephone', 'N/A')
                        website = item.get('url', 'N/A')
                        print(f'  Thumbtack: {name} | Rating: {rating} | Reviews: {reviews} | Phone: {phone}')
            elif isinstance(data, dict) and data.get('@type') in ['ItemList']:
                for elem in data.get('itemListElement', [])[:10]:
                    item = elem.get('item', elem)
                    name = item.get('name', '')
                    print(f'  Thumbtack ItemList: {name}')
        except:
            pass
except Exception as e:
    print(f'Thumbtack error: {e}')

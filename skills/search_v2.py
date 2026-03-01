import urllib.request
import urllib.parse
import re
import json

def fetch(url):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml',
        'Accept-Language': 'en-US,en;q=0.9'
    })
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        return resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return f'ERROR: {e}'

# Try DuckDuckGo HTML search
queries = [
    'best rated bathroom remodel contractors Vancouver WA 98662',
    'bathroom tile vanity replacement contractors Vancouver Washington reviews',
    'top bathroom renovation companies Vancouver WA ratings'
]

all_segments = []
all_phones = []
all_companies = []

for q in queries:
    url = 'https://html.duckduckgo.com/html/?q=' + urllib.parse.quote(q)
    html = fetch(url)
    print(f'\nQuery: {q[:50]}... => {len(html)} chars')
    
    if 'ERROR' in html[:20]:
        print(html[:200])
        continue
    
    # Extract result snippets from DDG HTML
    # DDG uses class="result__snippet" and "result__title"
    titles = re.findall(r'class="result__a"[^>]*>(.*?)</a>', html, re.S)
    snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</(?:td|div|span)', html, re.S)
    urls_found = re.findall(r'class="result__url"[^>]*>(.*?)</a>', html, re.S)
    
    print(f'  Titles: {len(titles)}, Snippets: {len(snippets)}')
    
    for i in range(min(len(titles), 15)):
        t = re.sub(r'<[^>]+>', '', titles[i]).strip()
        s = re.sub(r'<[^>]+>', '', snippets[i]).strip() if i < len(snippets) else ''
        u = re.sub(r'<[^>]+>', '', urls_found[i]).strip() if i < len(urls_found) else ''
        print(f'  [{i}] {t}')
        print(f'      URL: {u}')
        print(f'      {s[:200]}')
        all_segments.append({'title': t, 'snippet': s, 'url': u})

# Also try Thumbtack with proper redirect following
thumb_url = 'https://www.thumbtack.com/wa/vancouver/bathroom-remodeling/'
html = fetch(thumb_url)
print(f'\nThumbtack: {len(html)} chars')
if 'ERROR' not in html[:20]:
    # Extract JSON-LD
    ld_matches = re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.S)
    for ld in ld_matches:
        try:
            data = json.loads(ld)
            if isinstance(data, list):
                for item in data[:10]:
                    if item.get('@type') in ['LocalBusiness', 'HomeAndConstructionBusiness']:
                        print(f"  TT: {item.get('name')} | Rating: {item.get('aggregateRating',{}).get('ratingValue')} | Reviews: {item.get('aggregateRating',{}).get('reviewCount')}")
            elif isinstance(data, dict) and data.get('@type') in ['LocalBusiness', 'HomeAndConstructionBusiness']:
                print(f"  TT: {data.get('name')} | Rating: {data.get('aggregateRating',{}).get('ratingValue')}")
        except:
            pass
    
    # Also try regex for contractor names and ratings in HTML
    names = re.findall(r'"name"\s*:\s*"([^"]+)"', html)
    ratings_found = re.findall(r'"ratingValue"\s*:\s*"?([\d.]+)', html)
    reviews_found = re.findall(r'"reviewCount"\s*:\s*"?(\d+)', html)
    print(f'  Names: {names[:10]}')
    print(f'  Ratings: {ratings_found[:10]}')
    print(f'  Reviews: {reviews_found[:10]}')

print('\n=== DONE ===')

import urllib.request
import re
from html import unescape

# Search for specific contractor details
queries = [
    'Elegant+Tile+and+Hardwood+Floors+Vancouver+WA+reviews+rating+phone',
    'Reliable+Men+Construction+Vancouver+WA+reviews+rating+phone',
    'Rapid+Bath+Construction+Vancouver+WA+reviews+rating+phone',
    'NW+Tub+Shower+Vancouver+WA+reviews+rating+phone',
    'Affordable+Contractor+Services+Vancouver+WA+reviews+rating+phone',
    'Allcraft+Home+Vancouver+WA+reviews+rating+phone',
    'Chase+Tile+Vancouver+WA+reviews+rating+phone'
]

for q in queries:
    url = f'https://html.duckduckgo.com/html/?q={q}'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        html = resp.read().decode('utf-8', errors='ignore')
        # Extract result snippets
        results = re.findall(r'<a[^>]*class="result__a"[^>]*>(.*?)</a>.*?<a[^>]*class="result__snippet"[^>]*>(.*?)</a>', html, re.DOTALL)
        company = q.split('+Vancouver')[0].replace('+', ' ')
        print(f'\n=== {company} ===')
        for i, (title, snippet) in enumerate(results[:3]):
            title_clean = unescape(re.sub(r'<[^>]+>', '', title)).strip()
            snippet_clean = unescape(re.sub(r'<[^>]+>', '', snippet)).strip()
            print(f'{i+1}. {title_clean}')
            print(f'   {snippet_clean[:300]}')
    except Exception as e:
        print(f'Error for {q}: {e}')

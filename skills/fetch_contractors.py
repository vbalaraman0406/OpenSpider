import urllib.request
import re
import json

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

# Try multiple search queries on DuckDuckGo
queries = [
    'best+bathroom+remodel+contractor+Vancouver+WA+98662+reviews+rating',
    'bathroom+tile+vanity+contractor+Vancouver+WA+98662+site:yelp.com',
    'bathroom+remodel+contractor+Vancouver+WA+reviews'
]

for q in queries:
    url = f'https://html.duckduckgo.com/html/?q={q}'
    req = urllib.request.Request(url, headers=headers)
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        html = resp.read().decode('utf-8', errors='ignore')
        # Extract result snippets
        results = re.findall(r'<a rel="nofollow" class="result__a" href="([^"]+)">(.+?)</a>', html)
        snippets = re.findall(r'<a class="result__snippet"[^>]*>(.+?)</a>', html)
        print(f'\n=== Query: {q} ===')
        for i, (link, title) in enumerate(results[:10]):
            clean_title = re.sub(r'<[^>]+>', '', title)
            snip = re.sub(r'<[^>]+>', '', snippets[i]) if i < len(snippets) else ''
            print(f'{i+1}. {clean_title}')
            print(f'   URL: {link}')
            print(f'   Snippet: {snip[:200]}')
    except Exception as e:
        print(f'Error for query {q}: {e}')

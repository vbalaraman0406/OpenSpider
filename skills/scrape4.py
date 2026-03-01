import urllib.request
import re
import json

# Try multiple targeted searches
urls = [
    'https://html.duckduckgo.com/html/?q=best+bathroom+tile+contractor+Vancouver+WA+98662+reviews',
    'https://html.duckduckgo.com/html/?q=bathroom+remodel+contractor+Vancouver+Washington+top+rated+2025',
    'https://html.duckduckgo.com/html/?q=site:bbb.org+bathroom+contractor+Vancouver+WA',
]

for url in urls:
    print(f'\n=== Searching: {url.split("q=")[1][:60]} ===')
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=10)
        html = resp.read().decode('utf-8', errors='ignore')
        # Extract result titles and snippets
        results = re.findall(r'class="result__a"[^>]*>(.*?)</a>.*?class="result__snippet"[^>]*>(.*?)</span>', html, re.DOTALL)
        if not results:
            # Try simpler pattern
            results = re.findall(r'class="result__a"[^>]*>(.*?)</a>', html, re.DOTALL)
            for i, r in enumerate(results[:10]):
                clean = re.sub(r'<[^>]+>', '', r).strip()
                print(f'  {i+1}. {clean}')
        else:
            for i, (title, snippet) in enumerate(results[:10]):
                t = re.sub(r'<[^>]+>', '', title).strip()
                s = re.sub(r'<[^>]+>', '', snippet).strip()
                print(f'  {i+1}. {t}')
                print(f'     {s[:200]}')
    except Exception as e:
        print(f'  Error: {e}')

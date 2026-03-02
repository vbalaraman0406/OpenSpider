import urllib.request
import json
import re

# Try DuckDuckGo HTML search
queries = [
    'https://html.duckduckgo.com/html/?q=stock+market+Iran+war+conflict+March+2026+oil+prices+gold',
    'https://html.duckduckgo.com/html/?q=S%26P+500+Iran+tensions+2026+defense+stocks'
]

for url in queries:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'})
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        html = resp.read().decode('utf-8', errors='ignore')
        # Extract result snippets
        results = re.findall(r'class="result__snippet">(.*?)</a>', html, re.DOTALL)
        titles = re.findall(r'class="result__a"[^>]*>(.*?)</a>', html, re.DOTALL)
        urls_found = re.findall(r'class="result__url"[^>]*>(.*?)</a>', html, re.DOTALL)
        print(f'\n=== Query: {url.split("q=")[1][:60]} ===')
        for i, (t, s) in enumerate(zip(titles[:8], results[:8])):
            t_clean = re.sub(r'<[^>]+>', '', t).strip()
            s_clean = re.sub(r'<[^>]+>', '', s).strip()
            u_clean = urls_found[i].strip() if i < len(urls_found) else ''
            print(f'{i+1}. {t_clean}')
            print(f'   URL: {u_clean}')
            print(f'   {s_clean}')
            print()
    except Exception as e:
        print(f'Error: {e}')

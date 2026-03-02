import urllib.request
import re

queries = [
    'stock+market+reaction+Iran+conflict+2025+oil+prices',
    'Iran+war+tensions+stock+market+defense+stocks+2025',
    'Iran+conflict+oil+prices+gold+S%26P+500+latest',
    'Iran+military+conflict+news+latest+2025+2026'
]

for q in queries:
    url = f'https://html.duckduckgo.com/html/?q={q}'
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        html = resp.read().decode('utf-8', errors='ignore')
        # Try multiple regex patterns
        # Pattern 1: result__snippet
        snippets = re.findall(r'class="result__snippet">(.*?)</a>', html, re.DOTALL)
        # Pattern 2: broader
        if not snippets:
            snippets = re.findall(r'result__snippet[^>]*>(.*?)</(?:a|td|div)', html, re.DOTALL)
        # Pattern 3: result blocks
        results = re.findall(r'<a rel="nofollow" class="result__a" href="([^"]+)">(.*?)</a>', html, re.DOTALL)
        
        print(f'\n=== {q[:50]} ===')
        print(f'Found {len(results)} results, {len(snippets)} snippets')
        
        for i, (href, title) in enumerate(results[:5]):
            t = re.sub(r'<[^>]+>', '', title).strip()
            s = re.sub(r'<[^>]+>', '', snippets[i]).strip() if i < len(snippets) else 'No snippet'
            print(f'{i+1}. {t}')
            print(f'   {href[:100]}')
            print(f'   {s[:200]}')
            print()
        
        if not results:
            # Debug: print first 2000 chars
            print(html[:2000])
    except Exception as e:
        print(f'Error: {e}')

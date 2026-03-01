import urllib.request
import re
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Try DuckDuckGo lite which is simpler
queries = [
    'bathroom+remodeling+contractor+Vancouver+WA+98662+reviews',
    'bathroom+tile+contractor+Vancouver+WA+98662+rated',
    'best+bathroom+renovation+contractor+Vancouver+WA'
]

all_results = []

for q in queries:
    url = f'https://lite.duckduckgo.com/lite/?q={q}'
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml',
        'Accept-Language': 'en-US,en;q=0.9'
    })
    try:
        resp = urllib.request.urlopen(req, timeout=15, context=ctx)
        html = resp.read().decode('utf-8', errors='ignore')
        # Extract snippets from DDG lite - results are in <td> tags with class="result-snippet"
        snippets = re.findall(r'class="result-snippet">(.*?)</td>', html, re.DOTALL)
        links = re.findall(r'class="result-link"[^>]*>(.*?)</a>', html, re.DOTALL)
        titles = re.findall(r'<a[^>]*class="result-link"[^>]*>(.*?)</a>', html, re.DOTALL)
        
        print(f'\nQuery: {q}')
        print(f'Snippets found: {len(snippets)}')
        print(f'Links found: {len(links)}')
        
        for i, s in enumerate(snippets[:10]):
            clean = re.sub(r'<[^>]+>', '', s).strip()
            title = re.sub(r'<[^>]+>', '', titles[i]).strip() if i < len(titles) else ''
            print(f'\n--- Result {i+1} ---')
            print(f'Title: {title}')
            print(f'Snippet: {clean[:300]}')
            all_results.append({'title': title, 'snippet': clean})
    except Exception as e:
        print(f'Query {q}: ERROR: {e}')

# Also try to directly access some known contractor websites in Vancouver WA
print('\n\n=== Trying known contractor sites ===')
known = [
    ('https://www.bfremodelingllc.com/', 'BF Remodeling'),
    ('https://www.nwrestore.com/', 'NW Restore'),
]
for url, name in known:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=10, context=ctx)
        html = resp.read().decode('utf-8', errors='ignore')
        phones = re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', html)
        print(f'{name}: Status {resp.status}, Phones: {phones[:3]}')
    except Exception as e:
        print(f'{name}: {e}')

print(f'\nTotal results collected: {len(all_results)}')

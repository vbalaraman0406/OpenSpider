import urllib.request
import urllib.parse
import re
import ssl
import json

ssl._create_default_https_context = ssl._create_unverified_context

def fetch(url):
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5'
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return f'ERROR: {e}'

# Try DuckDuckGo HTML search
queries = [
    'bathroom tile contractor Vancouver WA 98662 reviews',
    'best bathroom remodel contractor Vancouver Washington',
]

for q in queries:
    url = f'https://html.duckduckgo.com/html/?q={urllib.parse.quote(q)}'
    html = fetch(url)
    if html.startswith('ERROR'):
        print(f'Query "{q}": {html}')
        continue
    # Extract result snippets
    results = re.findall(r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL)
    snippets = re.findall(r'class="result__snippet">(.*?)</a>', html, re.DOTALL)
    print(f'\n=== Query: {q} ===')
    print(f'Found {len(results)} results')
    for i, (link, title) in enumerate(results[:10]):
        title_clean = re.sub(r'<[^>]+>', '', title).strip()
        snip = re.sub(r'<[^>]+>', '', snippets[i]).strip() if i < len(snippets) else ''
        # Extract actual URL from DDG redirect
        actual_url = re.search(r'uddg=([^&]+)', link)
        if actual_url:
            link = urllib.parse.unquote(actual_url.group(1))
        print(f'{i+1}. {title_clean}')
        print(f'   URL: {link}')
        print(f'   Snippet: {snip[:200]}')
        print()

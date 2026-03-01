import urllib.request
import re
import json

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

def fetch(url):
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return f'ERROR: {e}'

# Try multiple search queries
queries = [
    'Mountainwood+construction+Vancouver+WA',
    'Mountainwood+remodeling+Vancouver+WA',
    'Mountainwood+homes+Vancouver+WA+bathroom',
    'Mountainwood+LLC+Vancouver+WA+contractor',
]

for q in queries:
    print(f'\n=== Query: {q} ===')
    url = f'https://html.duckduckgo.com/html/?q={q}'
    html = fetch(url)
    if 'ERROR' in html:
        print(html)
        continue
    # Extract result titles and URLs
    links = re.findall(r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL)
    snippets = re.findall(r'class="result__snippet">(.*?)</td>', html, re.DOTALL)
    for i, (href, title) in enumerate(links[:5]):
        clean_title = re.sub(r'<[^>]+>', '', title).strip()
        clean_snippet = ''
        if i < len(snippets):
            clean_snippet = re.sub(r'<[^>]+>', '', snippets[i]).strip()[:200]
        # Extract actual URL from DDG redirect
        actual = re.search(r'uddg=([^&]+)', href)
        actual_url = urllib.request.unquote(actual.group(1)) if actual else href
        print(f'{i+1}. {clean_title}')
        print(f'   URL: {actual_url}')
        print(f'   Snippet: {clean_snippet}')
        print()

# Also try Bing
print('\n=== BING SEARCH ===')
bing_url = 'https://www.bing.com/search?q=Mountainwood+contractor+Vancouver+WA+bathroom+remodel'
html = fetch(bing_url)
if 'ERROR' not in html:
    results = re.findall(r'<li class="b_algo">(.*?)</li>', html, re.DOTALL)
    for i, r in enumerate(results[:5]):
        title = re.search(r'<a[^>]*>(.*?)</a>', r, re.DOTALL)
        href = re.search(r'href="([^"]+)"', r)
        snippet = re.search(r'<p[^>]*>(.*?)</p>', r, re.DOTALL)
        if title:
            print(f'{i+1}. {re.sub(r"<[^>]+>", "", title.group(1)).strip()}')
        if href:
            print(f'   URL: {href.group(1)}')
        if snippet:
            print(f'   Snippet: {re.sub(r"<[^>]+>", "", snippet.group(1)).strip()[:200]}')
        print()
else:
    print(html)

import urllib.request
import urllib.parse
import json
import re
import ssl
import time

ssl._create_default_https_context = ssl._create_unverified_context

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

def fetch(url):
    req = urllib.request.Request(url, headers=headers)
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        return resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return f'ERROR: {e}'

# Try DuckDuckGo HTML
queries = [
    'bathroom remodel contractors Vancouver WA 98662',
    'best bathroom tile contractors Orchards Vancouver WA',
    'bathroom renovation companies Clark County WA reviews',
]

all_results = []

for q in queries:
    url = f'https://html.duckduckgo.com/html/?q={urllib.parse.quote(q)}'
    html = fetch(url)
    if 'ERROR' in html[:20]:
        print(f'DDG failed for: {q} -> {html[:100]}')
        continue
    
    # Extract result titles and snippets
    # DDG HTML results are in <div class="result">
    results = re.findall(r'<a[^>]*class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>.*?<a[^>]*class="result__snippet"[^>]*>(.*?)</a>', html, re.DOTALL)
    if not results:
        # Try alternate pattern
        results = re.findall(r'<a[^>]*rel="nofollow"[^>]*class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL)
        snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</(?:a|div)', html, re.DOTALL)
        for i, (url_found, title) in enumerate(results):
            snip = snippets[i] if i < len(snippets) else ''
            clean_title = re.sub(r'<[^>]+>', '', title).strip()
            clean_snip = re.sub(r'<[^>]+>', '', snip).strip()
            all_results.append({'title': clean_title, 'url': url_found, 'snippet': clean_snip, 'query': q})
    else:
        for url_found, title, snippet in results:
            clean_title = re.sub(r'<[^>]+>', '', title).strip()
            clean_snip = re.sub(r'<[^>]+>', '', snippet).strip()
            all_results.append({'title': clean_title, 'url': url_found, 'snippet': clean_snip, 'query': q})
    
    print(f'Query: {q} -> {len(results)} results')
    time.sleep(2)

print(f'\nTotal results: {len(all_results)}')
for i, r in enumerate(all_results[:30]):
    print(f'\n--- Result {i+1} ---')
    print(f'Title: {r["title"][:100]}')
    print(f'URL: {r["url"][:150]}')
    print(f'Snippet: {r["snippet"][:200]}')

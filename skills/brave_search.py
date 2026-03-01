import urllib.request
import urllib.parse
import json
import re
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

queries = [
    'best rated bathroom remodel contractors Vancouver WA 98662',
    'bathroom tile vanity replacement contractors Vancouver Washington reviews',
    'top bathroom renovation companies Vancouver WA'
]

all_results = []

for q in queries:
    url = f'https://html.duckduckgo.com/html/?q={urllib.parse.quote(q)}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        html = resp.read().decode('utf-8', errors='ignore')
        # Extract result snippets
        # DDG HTML results have class="result__snippet" and "result__title"
        titles = re.findall(r'class="result__a"[^>]*>(.*?)</a>', html, re.DOTALL)
        snippets = re.findall(r'class="result__snippet">(.*?)</td>', html, re.DOTALL)
        urls = re.findall(r'class="result__url"[^>]*>(.*?)</a>', html, re.DOTALL)
        
        print(f'Query: {q[:50]}...')
        print(f'  Found {len(titles)} titles, {len(snippets)} snippets, {len(urls)} urls')
        
        for i in range(min(len(titles), len(snippets))):
            title = re.sub(r'<[^>]+>', '', titles[i]).strip()
            snippet = re.sub(r'<[^>]+>', '', snippets[i]).strip()
            u = re.sub(r'<[^>]+>', '', urls[i]).strip() if i < len(urls) else ''
            all_results.append({'title': title, 'snippet': snippet, 'url': u, 'query': q[:50]})
            
    except Exception as e:
        print(f'Error for query {q[:50]}: {e}')

print(f'\nTotal results: {len(all_results)}')
print('\n--- ALL RESULTS ---')
for r in all_results[:30]:
    print(f"Title: {r['title']}")
    print(f"URL: {r['url']}")
    print(f"Snippet: {r['snippet'][:200]}")
    print('---')

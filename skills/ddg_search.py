import requests
import re
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

queries = [
    'best rated bathroom remodel contractors Vancouver WA 98662',
    'bathroom tile vanity replacement contractors Vancouver Washington reviews',
    'top bathroom renovation companies Vancouver WA ratings'
]

all_results = []

for q in queries:
    try:
        url = f'https://html.duckduckgo.com/html/?q={requests.utils.quote(q)}'
        r = requests.get(url, headers=headers, timeout=15)
        # Extract result titles and snippets
        from html.parser import HTMLParser
        
        # Simple regex extraction
        titles = re.findall(r'class="result__a"[^>]*>(.*?)</a>', r.text, re.DOTALL)
        snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</td>', r.text, re.DOTALL)
        urls = re.findall(r'class="result__url"[^>]*>(.*?)</a>', r.text, re.DOTALL)
        
        for i in range(min(len(titles), len(snippets))):
            title = re.sub(r'<[^>]+>', '', titles[i]).strip()
            snippet = re.sub(r'<[^>]+>', '', snippets[i]).strip()
            link = re.sub(r'<[^>]+>', '', urls[i]).strip() if i < len(urls) else ''
            all_results.append({'title': title, 'snippet': snippet, 'url': link, 'query': q})
        print(f'Query "{q[:40]}...": {len(titles)} results')
    except Exception as e:
        print(f'Error for query: {e}')

print(f'\nTotal results: {len(all_results)}')
print('\n--- RESULTS ---')
for r in all_results:
    print(f"TITLE: {r['title']}")
    print(f"URL: {r['url']}")
    print(f"SNIPPET: {r['snippet'][:300]}")
    print('---')

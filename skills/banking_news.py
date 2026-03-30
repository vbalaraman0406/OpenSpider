import requests
import re

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}

queries = [
    'bank breach hack financial cybersecurity 2026 march',
    'OCC FFIEC banking cybersecurity regulation 2026',
    'financial sector fraud BEC wire fraud 2026'
]

for q in queries:
    print(f'\n=== QUERY: {q} ===')
    try:
        url = f'https://html.duckduckgo.com/html/?q={q.replace(" ", "+")}'
        resp = requests.get(url, headers=headers, timeout=10)
        html = resp.text
        links = re.findall(r'<a rel="nofollow" class="result__a" href="([^"]+)">(.+?)</a>', html)
        snippets = re.findall(r'<a class="result__snippet"[^>]*>(.+?)</a>', html)
        for i, (link, title) in enumerate(links[:5]):
            clean_title = re.sub(r'<[^>]+>', '', title)
            snip = re.sub(r'<[^>]+>', '', snippets[i]) if i < len(snippets) else ''
            print(f'TITLE: {clean_title}')
            print(f'URL: {link}')
            print(f'SNIPPET: {snip[:200]}')
            print('---')
    except Exception as e:
        print(f'ERROR: {e}')

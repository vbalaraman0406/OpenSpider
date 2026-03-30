import requests
import re

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

def clean(t):
    return re.sub(r'<[^>]+>', '', t).strip()

def search_ddg(query):
    url = 'https://html.duckduckgo.com/html/'
    data = {'q': query}
    try:
        r = requests.post(url, data=data, headers=headers, timeout=15)
        html = r.text
        titles = re.findall(r'class="result__a"[^>]*>(.*?)</a>', html)
        snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</a>', html)
        results = []
        for i in range(min(len(titles), len(snippets), 6)):
            results.append((clean(titles[i]), clean(snippets[i])))
        return results
    except Exception as e:
        return [(f'Error: {e}', '')]

queries = [
    'Tamil Nadu 2026 election opinion poll seat prediction',
    'Tamil Nadu 2026 election India Today DMK AIADMK BJP',
    'Tamil Nadu 2026 election Times of India TVK NTK',
    'Tamil Nadu election 2026 NDTV The Hindu latest news',
    'Tamil Nadu assembly election 2026 alliance parties',
    'Tamil Nadu election 2026 Vijay TVK BJP alliance prediction'
]

for q in queries:
    print(f'\n=== {q} ===')
    results = search_ddg(q)
    for title, snip in results:
        print(f'TITLE: {title}')
        print(f'SNIP: {snip}')
        print()

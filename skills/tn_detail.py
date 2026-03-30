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
        return [(str(e), '')]

queries = [
    'Tamil Nadu election 2026 date April 23 schedule',
    'Tamil Nadu 2026 opinion poll projected seats DMK AIADMK TVK numbers',
    'Loyola opinion poll Tamil Nadu 2026 TVK DMK seats',
    'Chanakyaa opinion poll Tamil Nadu 2026 EPS DMK seats numbers',
    'Tamil Nadu election 2026 BJP NDA alliance AIADMK seats',
    'Tamil Nadu election 2026 NTK Seeman Congress alliance'
]

for q in queries:
    print(f'\n=== {q} ===')
    results = search_ddg(q)
    for title, snip in results:
        print(f'T: {title}')
        print(f'S: {snip}')
        print()

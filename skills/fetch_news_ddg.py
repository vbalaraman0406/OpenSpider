import requests
from bs4 import BeautifulSoup
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

queries = [
    'Iran war latest news today',
    'Iran military conflict latest',
    'Iran US tensions latest',
    'Iran Israel conflict news'
]

all_results = []

for q in queries:
    try:
        url = f'https://html.duckduckgo.com/html/?q={q.replace(" ", "+")}'
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        for result in soup.find_all('div', class_='result')[:4]:
            title_el = result.find('a', class_='result__a')
            snippet_el = result.find('a', class_='result__snippet')
            title = title_el.get_text(strip=True) if title_el else ''
            snippet = snippet_el.get_text(strip=True) if snippet_el else ''
            link = ''
            if title_el and title_el.has_attr('href'):
                link = title_el['href']
            if title:
                all_results.append({'title': title, 'snippet': snippet[:250], 'url': link})
    except Exception as e:
        all_results.append({'title': f'Error: {q}', 'snippet': str(e), 'url': ''})

# Deduplicate
seen = set()
unique = []
for r in all_results:
    if r['title'] not in seen:
        seen.add(r['title'])
        unique.append(r)

for r in unique[:15]:
    print(f"TITLE: {r['title']}")
    print(f"SNIPPET: {r['snippet']}")
    print(f"URL: {r['url']}")
    print('---')

if not unique:
    print('NO RESULTS FOUND')
    # Debug: print first 500 chars of last response
    print('DEBUG HTML:', resp.text[:500] if resp else 'no response')

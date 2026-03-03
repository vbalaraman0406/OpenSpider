import requests
from bs4 import BeautifulSoup
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

queries = [
    'Iran war latest news today',
    'Iran military conflict latest',
    'Iran US tensions latest news',
    'Iran Israel conflict latest',
    'Iran strikes today'
]

all_results = []

for q in queries:
    try:
        url = f'https://www.google.com/search?q={q.replace(" ", "+")}&tbs=qdr:d&num=5'
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        for div in soup.find_all('div'):
            h3 = div.find('h3')
            if h3:
                title = h3.get_text(strip=True)
                # Get snippet from nearby text
                parent = h3.find_parent('div')
                snippet = ''
                if parent:
                    spans = parent.find_all('span')
                    for s in spans:
                        t = s.get_text(strip=True)
                        if len(t) > 40:
                            snippet = t
                            break
                link = ''
                a_tag = h3.find_parent('a')
                if a_tag and a_tag.has_attr('href'):
                    href = a_tag['href']
                    if href.startswith('/url?q='):
                        link = href.split('/url?q=')[1].split('&')[0]
                    elif href.startswith('http'):
                        link = href
                if title and len(title) > 5:
                    all_results.append({'title': title, 'snippet': snippet[:200], 'url': link})
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

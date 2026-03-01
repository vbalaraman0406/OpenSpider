import requests
from bs4 import BeautifulSoup
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

queries = [
    'best bathroom tile contractor Vancouver WA 98662 reviews',
    'bathroom remodel contractor Vancouver WA Google reviews',
    'bathroom vanity installation contractor Vancouver WA rated',
    'top rated bathroom renovation Vancouver Washington'
]

all_results = []

for q in queries:
    try:
        url = f'https://www.google.com/search?q={requests.utils.quote(q)}&num=10'
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        # Extract search result titles and snippets
        for div in soup.find_all('div', class_='tF2Cxc'):
            title_el = div.find('h3')
            snippet_el = div.find('div', class_='VwiC3b')
            link_el = div.find('a')
            title = title_el.get_text() if title_el else ''
            snippet = snippet_el.get_text() if snippet_el else ''
            link = link_el['href'] if link_el and link_el.has_attr('href') else ''
            all_results.append({'title': title, 'snippet': snippet, 'link': link})
        # Also try alternate div classes
        for div in soup.find_all('div', class_='g'):
            title_el = div.find('h3')
            snippet_el = div.find('span', class_='aCOpRe')
            if not snippet_el:
                snippet_el = div.find('div', {'data-sncf': True})
            if not snippet_el:
                snippet_el = div.find('div', class_='VwiC3b')
            link_el = div.find('a')
            title = title_el.get_text() if title_el else ''
            snippet = snippet_el.get_text() if snippet_el else ''
            link = link_el['href'] if link_el and link_el.has_attr('href') else ''
            if title and title not in [r['title'] for r in all_results]:
                all_results.append({'title': title, 'snippet': snippet, 'link': link})
    except Exception as e:
        print(f'Error on query "{q}": {e}')

print(f'Total results: {len(all_results)}')
for r in all_results[:30]:
    print(f"\nTITLE: {r['title']}")
    print(f"SNIPPET: {r['snippet'][:200]}")
    print(f"LINK: {r['link']}")

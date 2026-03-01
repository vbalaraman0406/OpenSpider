import requests
from bs4 import BeautifulSoup
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

queries = [
    'best bathroom remodel contractor Vancouver WA 98662 reviews',
    'bathroom tile vanity contractor Vancouver WA rated',
    'top rated bathroom renovation company Vancouver Washington',
]

all_results = []
for q in queries:
    try:
        url = f'https://www.bing.com/search?q={requests.utils.quote(q)}&count=20'
        r = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        # Try multiple selectors
        results = soup.select('li.b_algo')
        if not results:
            results = soup.select('div.b_algo')
        if not results:
            results = soup.find_all('li', class_=re.compile('algo'))
        print(f'Query: {q[:50]}... -> {len(results)} results')
        for res in results:
            title_el = res.find('h2') or res.find('h3')
            title = title_el.get_text(strip=True) if title_el else ''
            link_el = res.find('a', href=True)
            link = link_el['href'] if link_el else ''
            snippet_el = res.find('p') or res.find('div', class_='b_caption')
            snippet = snippet_el.get_text(strip=True) if snippet_el else ''
            if title:
                all_results.append({'title': title, 'url': link, 'snippet': snippet[:200]})
    except Exception as e:
        print(f'Error: {e}')

print(f'\nTotal results: {len(all_results)}')
for i, r in enumerate(all_results[:30]):
    print(f"\n--- Result {i+1} ---")
    print(f"Title: {r['title']}")
    print(f"URL: {r['url']}")
    print(f"Snippet: {r['snippet']}")

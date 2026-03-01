import requests
from bs4 import BeautifulSoup
import json
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9'
}

contractors = []

# Search 1: Google search via DuckDuckGo HTML
def search_ddg(query):
    results = []
    try:
        url = f'https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}'
        r = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        for result in soup.select('.result'):
            title_el = result.select_one('.result__title a')
            snippet_el = result.select_one('.result__snippet')
            if title_el:
                title = title_el.get_text(strip=True)
                link = title_el.get('href', '')
                snippet = snippet_el.get_text(strip=True) if snippet_el else ''
                results.append({'title': title, 'link': link, 'snippet': snippet})
    except Exception as e:
        print(f'DDG error: {e}')
    return results

print('=== Search 1: bathroom tile vanity contractor Vancouver WA ===')
results1 = search_ddg('best bathroom tile and vanity contractor Vancouver WA 98662 reviews 2025')
for r in results1[:15]:
    print(f"Title: {r['title']}")
    print(f"Snippet: {r['snippet'][:200]}")
    print(f"Link: {r['link']}")
    print('---')

print('\n=== Search 2: Google reviews bathroom remodel Vancouver WA ===')
results2 = search_ddg('Vancouver WA bathroom remodel contractor Google reviews rated')
for r in results2[:15]:
    print(f"Title: {r['title']}")
    print(f"Snippet: {r['snippet'][:200]}")
    print(f"Link: {r['link']}")
    print('---')

print('\n=== Search 3: Houzz bathroom contractors Vancouver WA ===')
results3 = search_ddg('site:houzz.com bathroom remodel contractors Vancouver WA')
for r in results3[:10]:
    print(f"Title: {r['title']}")
    print(f"Snippet: {r['snippet'][:200]}")
    print(f"Link: {r['link']}")
    print('---')

print('\n=== Search 4: Thumbtack bathroom Vancouver WA ===')
results4 = search_ddg('site:thumbtack.com bathroom tile contractor Vancouver WA')
for r in results4[:10]:
    print(f"Title: {r['title']}")
    print(f"Snippet: {r['snippet'][:200]}")
    print(f"Link: {r['link']}")
    print('---')

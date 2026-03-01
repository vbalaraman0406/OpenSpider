import requests
from bs4 import BeautifulSoup
import re
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
}

queries = [
    'best bathroom remodel contractor Vancouver WA 98662 reviews',
    'bathroom tile vanity contractor Vancouver WA rated',
    'top rated bathroom renovation Vancouver Washington',
]

all_results = []

for q in queries:
    try:
        url = f'https://www.google.com/search?q={requests.utils.quote(q)}&num=20'
        r = requests.get(url, headers=headers, timeout=15)
        print(f'Query: {q[:50]}... Status: {r.status_code}')
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Extract from search result divs
        for div in soup.find_all('div', class_='g'):
            title_el = div.find('h3')
            link_el = div.find('a')
            snippet_el = div.find('div', class_='VwiC3b') or div.find('span', class_='aCOpRe')
            if title_el:
                title = title_el.get_text()
                link = link_el['href'] if link_el and link_el.get('href') else ''
                snippet = snippet_el.get_text() if snippet_el else ''
                all_results.append({'title': title, 'link': link, 'snippet': snippet})
        
        # Also try extracting local pack results
        for div in soup.find_all('div', attrs={'data-attrid': True}):
            text = div.get_text()
            if 'rating' in text.lower() or 'review' in text.lower():
                all_results.append({'title': 'local_pack', 'link': '', 'snippet': text[:300]})
                
    except Exception as e:
        print(f'Error: {e}')

print(f'\nTotal results: {len(all_results)}')
for i, r in enumerate(all_results[:30]):
    print(f"\n--- Result {i+1} ---")
    print(f"Title: {r['title']}")
    print(f"Link: {r['link'][:100]}")
    print(f"Snippet: {r['snippet'][:200]}")

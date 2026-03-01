import requests
import re
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

queries = [
    'Mountainwood Homes Vancouver WA',
    'Mountainwood Construction Vancouver WA',
    'Mountainwood Remodeling Vancouver WA',
    'Mountainwood contractor Vancouver WA 98662',
    'Mountainwood LLC Washington contractor'
]

for q in queries:
    print(f'\n=== {q} ===')
    try:
        url = f'https://html.duckduckgo.com/html/?q={q.replace(" ", "+")}'
        r = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        results = soup.select('.result')
        for i, res in enumerate(results[:5]):
            title_el = res.select_one('.result__a')
            snip_el = res.select_one('.result__snippet')
            url_el = res.select_one('.result__url')
            title = title_el.get_text(strip=True) if title_el else 'N/A'
            snip = snip_el.get_text(strip=True)[:200] if snip_el else 'N/A'
            link = url_el.get_text(strip=True) if url_el else 'N/A'
            print(f'  {i+1}. {title}')
            print(f'     {snip}')
            print(f'     URL: {link}')
        if not results:
            print('  No results found')
    except Exception as e:
        print(f'  Error: {e}')

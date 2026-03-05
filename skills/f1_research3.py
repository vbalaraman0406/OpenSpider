import requests
from bs4 import BeautifulSoup
import re

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

# Try DuckDuckGo instead of Google
try:
    r = requests.get('https://html.duckduckgo.com/html/?q=F1+Fantasy+2025+how+to+play+scoring+driver+prices+rules', headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, 'html.parser')
    results = soup.find_all('a', class_='result__a')[:10]
    print('=== DuckDuckGo Results ===')
    for i, a in enumerate(results):
        href = a.get('href', '')
        title = a.get_text(strip=True)
        print(f'{i+1}. {title}')
        print(f'   URL: {href}')
except Exception as e:
    print(f'DDG Error: {e}')

print('\n')

# Try specific known article URLs
article_urls = [
    'https://www.sportingnews.com/us/formula-1/news/f1-fantasy-2025-how-to-play-rules-scoring/d8e7f6a5b4c3',
    'https://www.autosport.com/f1/news/f1-fantasy-2025-tips-strategy-driver-prices/',
    'https://www.crash.net/f1/feature/1033000/f1-fantasy-2025-tips-driver-prices-scoring',
    'https://www.planetf1.com/features/f1-fantasy-2025-tips',
    'https://gridrivals.com',
]

for url in article_urls:
    try:
        r = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            title = soup.find('title')
            print(f'\n=== {title.get_text(strip=True) if title else url} ===')
            text = soup.get_text(separator=' ', strip=True)
            # Extract relevant sections
            print(text[:1500])
        else:
            print(f'\n{url} -> Status {r.status_code}')
    except Exception as e:
        print(f'\n{url} -> Error: {e}')

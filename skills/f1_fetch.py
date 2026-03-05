import requests
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

# Try multiple F1 Fantasy article URL patterns
urls_to_try = [
    'https://www.formula1.com/en/latest/article/f1-fantasy-is-back-for-2025-here-s-everything-you-need-to-know',
    'https://www.formula1.com/en/latest/article.f1-fantasy-is-back-for-2025.html',
    'https://www.formula1.com/en/latest/tags/f1-fantasy.html',
    'https://www.formula1.com/en/results/2025/fantasy',
    'https://www.planetf1.com/features/f1-fantasy-tips-2025',
    'https://www.skysports.com/f1/news/12433/f1-fantasy-2025',
    'https://www.racefans.net/f1-fantasy-tips/',
    'https://en.wikipedia.org/wiki/2025_Formula_One_World_Championship',
]

for url in urls_to_try:
    try:
        r = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            title = soup.find('title')
            print(f'\n=== SUCCESS: {url} ===')
            if title:
                print(f'Title: {title.get_text(strip=True)}')
            for tag in soup.find_all(['script','style','nav','footer','header','aside']):
                tag.decompose()
            text = soup.get_text(separator='\n', strip=True)
            lines = [l for l in text.split('\n') if len(l.strip()) > 15]
            print('\n'.join(lines[:60]))
        else:
            print(f'SKIP: {url} -> {r.status_code}')
    except Exception as e:
        print(f'ERROR: {url} -> {e}')

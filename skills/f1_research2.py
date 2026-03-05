import requests
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

urls = [
    ('F1 Fantasy Official', 'https://fantasy.formula1.com/en/'),
    ('F1 Fantasy How to Play', 'https://fantasy.formula1.com/en/how-to-play'),
    ('F1 Fantasy Scoring', 'https://fantasy.formula1.com/en/scoring'),
    ('F1 News Fantasy', 'https://www.formula1.com/en/latest/article/f1-fantasy-2025'),
]

for name, url in urls:
    print(f'\n=== {name}: {url} ===')
    try:
        r = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        print(f'Status: {r.status_code}, Final URL: {r.url}')
        soup = BeautifulSoup(r.text, 'html.parser')
        # Get title
        title = soup.find('title')
        if title:
            print(f'Title: {title.get_text(strip=True)}')
        # Get main text content
        text = soup.get_text(separator=' ', strip=True)
        # Print first 800 chars
        print(text[:800])
    except Exception as e:
        print(f'Error: {e}')

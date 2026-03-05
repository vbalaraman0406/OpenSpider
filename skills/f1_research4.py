import requests
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

# Try specific working URLs for F1 Fantasy guides
urls = [
    'https://www.formula1.com/en/latest/article/f1-fantasy-is-back-here-s-everything-you-need-to-know',
    'https://www.formula1.com/en/latest/tags/f1-fantasy',
    'https://www.sportingnews.com/us/formula-1/news/f1-fantasy-tips-2025-best-team',
    'https://www.gpfans.com/en/f1-news/f1-fantasy-2025',
    'https://www.motorsport.com/f1/news/f1-fantasy-2025-tips/',
]

for url in urls:
    try:
        r = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        print(f'\n=== {url} -> {r.status_code} ===')
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            title = soup.find('title')
            if title:
                print(f'Title: {title.get_text(strip=True)}')
            # Get article text
            for tag in soup.find_all(['script','style','nav','footer','header']):
                tag.decompose()
            text = soup.get_text(separator='\n', strip=True)
            lines = [l for l in text.split('\n') if len(l) > 20]
            print('\n'.join(lines[:40]))
    except Exception as e:
        print(f'{url} -> Error: {e}')

# Also try Bing search
print('\n\n=== BING SEARCH ===')
try:
    r = requests.get('https://www.bing.com/search?q=F1+Fantasy+2025+scoring+rules+driver+prices+how+to+play', headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, 'html.parser')
    for li in soup.find_all('li', class_='b_algo')[:8]:
        h2 = li.find('h2')
        if h2:
            a = h2.find('a')
            if a:
                print(f'\nTitle: {h2.get_text(strip=True)}')
                print(f'URL: {a.get("href","")}')
                cite = li.find('p')
                if cite:
                    print(f'Snippet: {cite.get_text(strip=True)[:200]}')
except Exception as e:
    print(f'Bing Error: {e}')

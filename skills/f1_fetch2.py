import requests
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

# Get full Wikipedia 2025 F1 season data
print('=== WIKIPEDIA 2025 F1 ===')
try:
    r = requests.get('https://en.wikipedia.org/wiki/2025_Formula_One_World_Championship', headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, 'html.parser')
    # Find all tables with team/driver info
    tables = soup.find_all('table', class_='wikitable')
    for i, table in enumerate(tables[:5]):
        caption = table.find('caption')
        print(f'\nTable {i}: {caption.get_text(strip=True) if caption else "No caption"}')
        rows = table.find_all('tr')
        for row in rows[:25]:
            cells = row.find_all(['th','td'])
            cell_texts = [c.get_text(strip=True)[:40] for c in cells]
            if cell_texts:
                print(' | '.join(cell_texts))
except Exception as e:
    print(f'Error: {e}')

# Try fetching F1 Fantasy guide from various sites
print('\n\n=== F1 FANTASY GUIDES ===')
guide_urls = [
    'https://www.sportingnews.com/us/formula-1/news/f1-fantasy-tips-2025-best-team-picks-strategy',
    'https://www.givemesport.com/f1-fantasy-2025-tips/',
    'https://www.drivingline.com/articles/f1-fantasy-2025/',
    'https://www.techradar.com/gaming/f1-fantasy-2025',
    'https://www.tomsguide.com/news/f1-fantasy-2025',
]

for url in guide_urls:
    try:
        r = requests.get(url, headers=headers, timeout=8, allow_redirects=True)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            title = soup.find('title')
            print(f'\nSUCCESS: {url}')
            if title:
                print(f'Title: {title.get_text(strip=True)}')
            for tag in soup.find_all(['script','style','nav','footer','header','aside']):
                tag.decompose()
            text = soup.get_text(separator='\n', strip=True)
            lines = [l for l in text.split('\n') if len(l.strip()) > 20]
            print('\n'.join(lines[:40]))
        else:
            print(f'SKIP: {url} -> {r.status_code}')
    except Exception as e:
        print(f'ERROR: {url} -> {e}')

import requests
from bs4 import BeautifulSoup
import json

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

# Search 1: F1 Fantasy official platform
results = {}

try:
    r = requests.get('https://www.google.com/search?q=F1+Fantasy+2025+official+platform+how+to+play', headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, 'html.parser')
    snippets = []
    for div in soup.find_all('div', class_='BNeawe')[:8]:
        text = div.get_text(strip=True)
        if len(text) > 30:
            snippets.append(text[:200])
    results['search1'] = snippets
except Exception as e:
    results['search1_error'] = str(e)

# Search 2: F1 Fantasy scoring system 2025
try:
    r = requests.get('https://www.google.com/search?q=F1+Fantasy+2025+scoring+system+points+breakdown', headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, 'html.parser')
    snippets = []
    for div in soup.find_all('div', class_='BNeawe')[:8]:
        text = div.get_text(strip=True)
        if len(text) > 30:
            snippets.append(text[:200])
    results['search2'] = snippets
except Exception as e:
    results['search2_error'] = str(e)

# Search 3: F1 Fantasy driver prices 2025
try:
    r = requests.get('https://www.google.com/search?q=F1+Fantasy+2025+driver+prices+constructor+prices+budget+cap', headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, 'html.parser')
    snippets = []
    for div in soup.find_all('div', class_='BNeawe')[:8]:
        text = div.get_text(strip=True)
        if len(text) > 30:
            snippets.append(text[:200])
    results['search3'] = snippets
except Exception as e:
    results['search3_error'] = str(e)

# Search 4: F1 Fantasy strategy tips chips boosts
try:
    r = requests.get('https://www.google.com/search?q=F1+Fantasy+2025+strategy+tips+turbo+driver+chips+boosts', headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, 'html.parser')
    snippets = []
    for div in soup.find_all('div', class_='BNeawe')[:8]:
        text = div.get_text(strip=True)
        if len(text) > 30:
            snippets.append(text[:200])
    results['search4'] = snippets
except Exception as e:
    results['search4_error'] = str(e)

for key, val in results.items():
    print(f'\n=== {key} ===')
    if isinstance(val, list):
        for i, s in enumerate(val):
            print(f'{i+1}. {s}')
    else:
        print(val)

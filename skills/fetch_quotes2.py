import requests
from bs4 import BeautifulSoup
import json

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

# Try Google Finance pages for quotes
symbols_gf = {
    'SPY': 'NYSEARCA:SPY',
    'DIA': 'NYSEARCA:DIA', 
    'LMT': 'NYSE:LMT',
    'RTX': 'NYSE:RTX',
    'NOC': 'NYSE:NOC',
    'GLD': 'NYSEARCA:GLD',
    'USO': 'NYSEARCA:USO'
}

# Try finviz for quick quotes
print('=== FINVIZ QUOTES ===')
for sym in ['SPY', 'DIA', 'LMT', 'RTX', 'NOC', 'GLD', 'USO', 'XLE']:
    try:
        url = f'https://finviz.com/quote.ashx?t={sym}'
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        # Look for price
        price_el = soup.select_one('.quote-price_wrapper .quote-price')
        if not price_el:
            # Try alternative selectors
            price_el = soup.find('b', class_='quote-price_wrapper')
        if not price_el:
            # Try finding in snapshot table
            tables = soup.select('table.snapshot-table2')
            if tables:
                cells = tables[0].select('td')
                for i, cell in enumerate(cells):
                    txt = cell.get_text(strip=True)
                    if txt == 'Price':
                        print(f'{sym}: Price = {cells[i+1].get_text(strip=True)}')
                        break
                    if txt == 'Change':
                        print(f'{sym}: Change = {cells[i+1].get_text(strip=True)}')
                continue
        if price_el:
            print(f'{sym}: {price_el.get_text(strip=True)}')
        else:
            print(f'{sym}: Could not find price element')
    except Exception as e:
        print(f'{sym}: Error - {str(e)[:80]}')

# Also search for defense stocks Iran news
print('\n=== DEFENSE STOCKS NEWS ===')
try:
    url = f'https://html.duckduckgo.com/html/?q={requests.utils.quote("defense stocks LMT RTX NOC Iran war 2025")}'
    r = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, 'html.parser')
    for res in soup.select('.result')[:4]:
        t = res.select_one('.result__title')
        s = res.select_one('.result__snippet')
        if t: print(f'  {t.get_text(strip=True)[:120]}')
        if s: print(f'  {s.get_text(strip=True)[:200]}')
        print()
except Exception as e:
    print(f'Error: {e}')

# Gold news
print('\n=== GOLD NEWS ===')
try:
    url = f'https://html.duckduckgo.com/html/?q={requests.utils.quote("gold price Iran war safe haven 2025")}'
    r = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, 'html.parser')
    for res in soup.select('.result')[:3]:
        t = res.select_one('.result__title')
        s = res.select_one('.result__snippet')
        if t: print(f'  {t.get_text(strip=True)[:120]}')
        if s: print(f'  {s.get_text(strip=True)[:200]}')
        print()
except Exception as e:
    print(f'Error: {e}')

print('=== DONE ===')

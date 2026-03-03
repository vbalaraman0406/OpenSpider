import requests
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

symbols = ['SPY', 'DIA', 'LMT', 'RTX', 'NOC', 'GLD', 'USO', 'XLE', 'QQQ']

for sym in symbols:
    try:
        url = f'https://finviz.com/quote.ashx?t={sym}'
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        tables = soup.select('table.snapshot-table2')
        if tables:
            cells = tables[0].select('td')
            data = {}
            for i in range(0, len(cells)-1, 2):
                key = cells[i].get_text(strip=True)
                val = cells[i+1].get_text(strip=True)
                if key in ['Price', 'Change', 'Prev Close', 'Perf Week', 'Perf Day', 'Volatility']:
                    data[key] = val
            print(f'{sym}: {data}')
    except Exception as e:
        print(f'{sym}: Error - {str(e)[:80]}')

# Also get crude oil and gold futures info
print('\n=== COMMODITIES ===')
for query_name, query in [('Crude_Oil', 'crude oil price today'), ('Gold', 'gold price today')]:
    try:
        url = f'https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}'
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        for res in soup.select('.result')[:2]:
            s = res.select_one('.result__snippet')
            if s:
                print(f'{query_name}: {s.get_text(strip=True)[:200]}')
    except Exception as e:
        print(f'{query_name}: Error')

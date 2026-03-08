import requests
import json

sectors = {
    'XLK': 'Technology',
    'XLV': 'Health Care',
    'XLF': 'Financials',
    'XLY': 'Consumer Discretionary',
    'XLP': 'Consumer Staples',
    'XLE': 'Energy',
    'XLI': 'Industrials',
    'XLB': 'Materials',
    'XLRE': 'Real Estate',
    'XLU': 'Utilities',
    'XLC': 'Communication Services'
}

for ticker, name in sectors.items():
    try:
        url = f'https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range=1d&interval=1d'
        resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        data = resp.json()
        meta = data['chart']['result'][0]['meta']
        prev_close = meta.get('chartPreviousClose', meta.get('previousClose', 0))
        current = meta.get('regularMarketPrice', 0)
        change = current - prev_close
        pct = (change / prev_close * 100) if prev_close else 0
        print(f'{name}|{ticker}|{current:.2f}|{change:+.2f}|{pct:+.2f}%')
    except Exception as e:
        print(f'{name}|{ticker}|Error|{e}')

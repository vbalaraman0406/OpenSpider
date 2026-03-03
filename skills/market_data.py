import urllib.request
import json
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

# Try to get current market data from Yahoo Finance API
tickers = ['%5EGSPC', '%5EDJI', 'CL%3DF', 'GC%3DF', 'LMT', 'RTX', 'NOC']
names = ['S&P 500', 'Dow Jones', 'Crude Oil (WTI)', 'Gold', 'Lockheed Martin (LMT)', 'RTX Corp (RTX)', 'Northrop Grumman (NOC)']

results = []
for i, ticker in enumerate(tickers):
    try:
        url = f'https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=1d'
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read().decode())
        meta = data['chart']['result'][0]['meta']
        price = meta.get('regularMarketPrice', 'N/A')
        prev = meta.get('chartPreviousClose', meta.get('previousClose', None))
        change_pct = 'N/A'
        if prev and prev != 0 and price != 'N/A':
            change_pct = f"{((price - prev) / prev) * 100:+.2f}%"
        results.append(f"{names[i]}: ${price:,.2f} ({change_pct})")
    except Exception as e:
        results.append(f"{names[i]}: Error - {str(e)[:80]}")

print('\n'.join(results))

import requests
import re
import json

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
results = {}

# Yahoo Finance API v8 - direct JSON endpoints
symbols = {
    'WTI_Oil': 'CL=F',
    'Brent_Oil': 'BZ=F',
    'Gold': 'GC=F',
    'SP500': '%5EGSPC',
    'DowJones': '%5EDJI',
    'NASDAQ': '%5EIXIC',
    'LMT': 'LMT',
    'RTX': 'RTX',
    'NOC': 'NOC',
    'GD': 'GD'
}

for name, sym in symbols.items():
    try:
        url = f'https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range=5d&interval=1d'
        r = requests.get(url, headers=headers, timeout=15)
        data = r.json()
        meta = data['chart']['result'][0]['meta']
        price = meta.get('regularMarketPrice', 'N/A')
        prev_close = meta.get('previousClose', 'N/A')
        currency = meta.get('currency', 'USD')
        
        # Get timestamps and closes for 5-day history
        timestamps = data['chart']['result'][0].get('timestamp', [])
        closes = data['chart']['result'][0]['indicators']['quote'][0].get('close', [])
        
        results[name] = {
            'price': price,
            'prev_close': prev_close,
            'currency': currency,
            'change_pct': round((price - prev_close) / prev_close * 100, 2) if isinstance(price, (int, float)) and isinstance(prev_close, (int, float)) and prev_close != 0 else 'N/A',
            'recent_closes': [round(c, 2) if c else None for c in closes[-5:]]
        }
    except Exception as e:
        results[name] = {'error': str(e)[:200]}

# Also get more Iran news from DuckDuckGo
try:
    r = requests.get('https://html.duckduckgo.com/html/?q=iran+us+war+military+developments+march+5+2026', headers=headers, timeout=15)
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(r.text, 'html.parser')
    snippets = []
    for a in soup.find_all('a', class_='result__a'):
        snippets.append(a.get_text(strip=True))
    results['military_news'] = snippets[:10]
except Exception as e:
    results['military_news_err'] = str(e)

# Oil market analysis news
try:
    r = requests.get('https://html.duckduckgo.com/html/?q=oil+prices+iran+war+impact+march+2026+analyst', headers=headers, timeout=15)
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(r.text, 'html.parser')
    snippets = []
    for a in soup.find_all('a', class_='result__a'):
        snippets.append(a.get_text(strip=True))
    results['oil_analysis_news'] = snippets[:10]
except Exception as e:
    results['oil_analysis_err'] = str(e)

print(json.dumps(results, indent=2, default=str))

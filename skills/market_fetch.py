import urllib.request
import re
import json

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return f'ERROR: {e}'

# Google Finance tickers
tickers = [
    ('S&P 500', '.INX:INDEXSP'),
    ('Dow Jones', '.DJI:INDEXDJX'),
    ('LMT', 'LMT:NYSE'),
    ('RTX', 'RTX:NYSE'),
    ('NOC', 'NOC:NYSE'),
]

for name, ticker in tickers:
    url = f'https://www.google.com/finance/quote/{ticker}'
    html = fetch(url)
    if html.startswith('ERROR'):
        print(f'{name}: {html}')
        continue
    
    price = re.findall(r'data-last-price="([^"]+)"', html)
    change = re.findall(r'data-last-normal-market-change="([^"]+)"', html)
    pct = re.findall(r'data-last-normal-market-change-percent="([^"]+)"', html)
    
    p = price[0] if price else 'N/A'
    c = change[0] if change else 'N/A'
    pc = pct[0] if pct else 'N/A'
    print(f'{name}: Price=${p} | Change={c} | Pct={pc}%')

# Try commodities from Google Finance
commodities = [
    ('WTI Crude Oil', 'CL%3DF:NYMEX'),
    ('Brent Crude', 'BZ%3DF:NYMEX'),
    ('Gold', 'GC%3DF:COMEX'),
]

for name, ticker in commodities:
    url = f'https://www.google.com/finance/quote/{ticker}'
    html = fetch(url)
    if html.startswith('ERROR'):
        print(f'{name}: {html}')
        continue
    price = re.findall(r'data-last-price="([^"]+)"', html)
    change = re.findall(r'data-last-normal-market-change="([^"]+)"', html)
    pct = re.findall(r'data-last-normal-market-change-percent="([^"]+)"', html)
    p = price[0] if price else 'N/A'
    c = change[0] if change else 'N/A'
    pc = pct[0] if pct else 'N/A'
    print(f'{name}: Price=${p} | Change={c} | Pct={pc}%')

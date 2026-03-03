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

# Try Yahoo Finance v8 API for real-time quotes
symbols = ['%5EGSPC','%5EDJI','LMT','RTX','NOC','CL%3DF','BZ%3DF','GC%3DF']
names = ['S&P 500','Dow Jones','LMT','RTX','NOC','WTI Crude','Brent Crude','Gold']

# Try Yahoo Finance quote page
for sym, name in zip(symbols, names):
    url = f'https://finance.yahoo.com/quote/{sym}/'
    html = fetch(url)
    if html.startswith('ERROR'):
        print(f'{name}: {html}')
        continue
    # Look for regularMarketPrice in JSON data
    p = re.findall(r'"regularMarketPrice":\{"raw":([\d.]+)', html)
    c = re.findall(r'"regularMarketChange":\{"raw":([\-\d.]+)', html)
    pc = re.findall(r'"regularMarketChangePercent":\{"raw":([\-\d.]+)', html)
    price = p[0] if p else 'N/A'
    change = c[0] if c else 'N/A'
    pct = pc[0] if pc else 'N/A'
    print(f'{name}: ${price} | Chg: {change} | Pct: {pct}%')

# Also try Google search for quick answers
print('\n--- Google Search for Iran market impact ---')
html = fetch('https://www.google.com/search?q=stock+market+Iran+tensions+today+2026')
if not html.startswith('ERROR'):
    # Extract snippets
    snippets = re.findall(r'<span[^>]*>([^<]{50,300})</span>', html)
    for s in snippets[:5]:
        clean = re.sub(r'<[^>]+>', '', s).strip()
        if any(w in clean.lower() for w in ['iran','market','stock','oil','gold','tension','military']):
            print(f'  > {clean}')

print('\n--- Google Search for oil price Iran ---')
html = fetch('https://www.google.com/search?q=crude+oil+price+today+Iran+March+2026')
if not html.startswith('ERROR'):
    snippets = re.findall(r'<span[^>]*>([^<]{40,300})</span>', html)
    for s in snippets[:5]:
        clean = re.sub(r'<[^>]+>', '', s).strip()
        if any(w in clean.lower() for w in ['oil','crude','brent','wti','iran','price']):
            print(f'  > {clean}')

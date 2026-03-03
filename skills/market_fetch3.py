import urllib.request
import re
import json

def fetch(url):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml',
        'Accept-Language': 'en-US,en;q=0.9'
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return f'ERROR: {e}'

print('=== STOCK DATA FROM GOOGLE FINANCE ===')
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
        print(f'{name}: FETCH ERROR')
        continue
    prices = re.findall(r'data-last-price="([^"]+)"', html)
    # Try to find change info in different patterns
    # Look for percentage in aria-label or other attributes
    pct_patterns = [
        r'data-last-normal-market-change-percent="([^"]+)"',
        r'data-change-percent="([^"]+)"',
        r'aria-label="[^"]*?([\-+]?\d+\.\d+)%',
        r'([\-+]?\d+\.\d+)%\s*(?:today|1\s*day)',
    ]
    chg_patterns = [
        r'data-last-normal-market-change="([^"]+)"',
        r'data-change="([^"]+)"',
    ]
    price = prices[0] if prices else 'N/A'
    pct = 'N/A'
    chg = 'N/A'
    for pat in pct_patterns:
        m = re.findall(pat, html)
        if m:
            pct = m[0]
            break
    for pat in chg_patterns:
        m = re.findall(pat, html)
        if m:
            chg = m[0]
            break
    print(f'{name}: ${price} | Chg: {chg} | Pct: {pct}%')

print('\n=== COMMODITIES FROM ALTERNATIVE SOURCES ===')
# Try MarketWatch for commodities
commodity_urls = [
    ('WTI Crude', 'https://www.marketwatch.com/investing/future/cl00'),
    ('Gold', 'https://www.marketwatch.com/investing/future/gc00'),
    ('Brent Crude', 'https://www.marketwatch.com/investing/future/brn00'),
]
for name, url in commodity_urls:
    html = fetch(url)
    if html.startswith('ERROR'):
        print(f'{name}: FETCH ERROR')
        continue
    # MarketWatch patterns
    price = re.findall(r'class="value">\$?([\d,.]+)', html)
    chg = re.findall(r'class="change--point--q">([\-\d,.]+)', html)
    pct = re.findall(r'class="change--percent--q">([\-\d,.]+)%', html)
    p = price[0] if price else 'N/A'
    c = chg[0] if chg else 'N/A'
    pc = pct[0] if pct else 'N/A'
    print(f'{name}: ${p} | Chg: {c} | Pct: {pc}%')

print('\n=== IRAN NEWS ===')
# Try Google News RSS for Iran
html = fetch('https://news.google.com/rss/search?q=Iran+military+conflict+2026&hl=en-US&gl=US&ceid=US:en')
if not html.startswith('ERROR'):
    titles = re.findall(r'<title>([^<]+)</title>', html)
    for t in titles[1:8]:  # skip first (feed title)
        print(f'  > {t}')
else:
    print(f'  News fetch error: {html[:100]}')

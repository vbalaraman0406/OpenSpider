import urllib.request
import re

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

# Extract all data-price, data-percent, data-exchange from S&P 500 page
html = fetch('https://www.google.com/finance/quote/.INX:INDEXSP')
if not html.startswith('ERROR'):
    # Find all exchange-price-percent triplets
    exchanges = re.findall(r'data-exchange="([^"]+)"', html)
    prices = re.findall(r'data-price="([^"]+)"', html)
    percents = re.findall(r'data-percent="([^"]+)"', html)
    print('Exchanges:', exchanges[:15])
    print('Prices:', prices[:15])
    print('Percents:', percents[:15])

# Get individual stock change data
print('\n=== INDIVIDUAL STOCKS ===')
for name, ticker in [('LMT','LMT:NYSE'),('RTX','RTX:NYSE'),('NOC','NOC:NYSE')]:
    html = fetch(f'https://www.google.com/finance/quote/{ticker}')
    if html.startswith('ERROR'):
        print(f'{name}: ERROR')
        continue
    price = re.findall(r'data-last-price="([^"]+)"', html)
    # Look for change elements with class patterns
    changes = re.findall(r'class="[^"]*(?:P2Luy|YMlKec|JwB6zf|NprOob)[^"]*"[^>]*>([^<]+)', html)
    # Also get data-percent from the page
    percents = re.findall(r'data-percent="([^"]+)"', html)
    dprices = re.findall(r'data-price="([^"]+)"', html)
    p = price[0] if price else 'N/A'
    print(f'{name}: Last=${p} | Changes={changes[:5]} | Percents={percents[:3]} | DataPrices={dprices[:3]}')

# Brent crude from CNBC
print('\n=== BRENT CRUDE ===')
html = fetch('https://www.cnbc.com/quotes/@LCO.1')
if not html.startswith('ERROR'):
    price = re.findall(r'"last":"?([\d,.]+)', html)
    chg = re.findall(r'"change":"?([\-\d,.]+)', html)
    p = price[0] if price else 'N/A'
    c = chg[0] if chg else 'N/A'
    print(f'Brent: ${p} | Chg: {c}')
else:
    print(f'Brent: {html[:100]}')

# Get oil change percent from CNBC
print('\n=== WTI CHANGE PCT ===')
html = fetch('https://www.cnbc.com/quotes/@CL.1')
if not html.startswith('ERROR'):
    pct = re.findall(r'"change_pct":"?([\-\d,.]+)', html)
    last = re.findall(r'"last":"?([\d,.]+)', html)
    chg = re.findall(r'"change":"?([\-\d,.]+)', html)
    print(f'WTI: last={last[:2]} chg={chg[:2]} pct={pct[:2]}')

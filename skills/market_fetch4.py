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

# Get S&P 500 page and look for all percentage patterns with context
print('=== S&P 500 DETAILED PARSE ===')
html = fetch('https://www.google.com/finance/quote/.INX:INDEXSP')
if not html.startswith('ERROR'):
    # Find all data attributes
    attrs = re.findall(r'data-[a-z-]+="[^"]+"', html)
    for a in attrs:
        if 'price' in a or 'change' in a or 'percent' in a or 'previous' in a:
            print(f'  {a}')
    # Also look for YsWIf class (Google Finance change container)
    changes = re.findall(r'class="[^"]*(?:P2Luy|YMlKec|JwB6zf|NprOob)[^"]*"[^>]*>([^<]+)', html)
    print(f'  Change elements: {changes[:10]}')
    # Look for specific patterns near the price
    price_area = re.findall(r'6[,.]?881[^<]{0,200}', html)
    for p in price_area[:3]:
        clean = re.sub(r'<[^>]+>', ' ', p).strip()[:150]
        print(f'  Near price: {clean}')

print('\n=== COMMODITIES - TRY CNBC ===')
# Try CNBC for commodity data
for name, url in [('WTI Crude', 'https://www.cnbc.com/quotes/@CL.1'), ('Gold', 'https://www.cnbc.com/quotes/@GC.1')]:
    html = fetch(url)
    if html.startswith('ERROR'):
        print(f'{name}: FETCH ERROR')
        continue
    # CNBC JSON data
    price = re.findall(r'"last":"?([\d,.]+)', html)
    chg = re.findall(r'"change":"?([\-\d,.]+)', html)
    pct = re.findall(r'"change_pct":"?([\-\d,.]+)', html)
    p = price[0] if price else 'N/A'
    c = chg[0] if chg else 'N/A'
    pc = pct[0] if pct else 'N/A'
    print(f'{name}: ${p} | Chg: {c} | Pct: {pc}%')

print('\n=== TRY GOOGLE SEARCH FOR PRICES ===')
# Quick Google searches for current prices
for query in ['WTI+crude+oil+price+today', 'gold+price+today+per+ounce', 'brent+crude+price+today']:
    html = fetch(f'https://www.google.com/search?q={query}')
    if html.startswith('ERROR'):
        continue
    # Google often shows price in data-value or specific spans
    vals = re.findall(r'data-value="([\d,.]+)"', html)
    # Also look for price patterns like $XX.XX
    dollar = re.findall(r'\$([\d,]+\.\d{2})', html)
    print(f'{query}: data-values={vals[:3]} dollar={dollar[:5]}')

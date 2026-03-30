import json, sys
sys.path.insert(0, '.')
from market_movers import execute

result = execute({'category': 'all', 'limit': '15'})

# Print indices
print('## Market Indices')
print('| Index | Price | Change % |')
print('|-------|-------|----------|')
for idx in result.get('indices', []):
    print(f"| {idx['index']} | {idx['price']} | {idx['change_pct']}% |")

print()
print('## Top Gainers')
print('| # | Ticker | Company Name | Price | Change | Change % | Volume | Market Cap |')
print('|---|--------|-------------|-------|--------|----------|--------|------------|')
for i, s in enumerate(result.get('top_gainers', []), 1):
    vol = f"{s['volume']:,}"
    mc = f"${s['market_cap']/1e9:.1f}B"
    print(f"| {i} | {s['ticker']} | {s['name']} | ${s['price']:.2f} | {s['change']:+.2f} | {s['change_pct']:+.2f}% | {vol} | {mc} |")

print()
print('## Top Losers')
print('| # | Ticker | Company Name | Price | Change | Change % | Volume | Market Cap |')
print('|---|--------|-------------|-------|--------|----------|--------|------------|')
for i, s in enumerate(result.get('top_losers', []), 1):
    vol = f"{s['volume']:,}"
    mc = f"${s['market_cap']/1e9:.1f}B"
    print(f"| {i} | {s['ticker']} | {s['name']} | ${s['price']:.2f} | {s['change']:+.2f} | {s['change_pct']:+.2f}% | {vol} | {mc} |")

print()
print('## Most Active by Volume')
print('| # | Ticker | Company Name | Price | Change | Change % | Volume | Market Cap |')
print('|---|--------|-------------|-------|--------|----------|--------|------------|')
for i, s in enumerate(result.get('most_active', []), 1):
    vol = f"{s['volume']:,}"
    mc = f"${s['market_cap']/1e9:.1f}B"
    print(f"| {i} | {s['ticker']} | {s['name']} | ${s['price']:.2f} | {s['change']:+.2f} | {s['change_pct']:+.2f}% | {vol} | {mc} |")

print(f"\nScanned: {result.get('scanned')} tickers | Timestamp: {result.get('timestamp')}")

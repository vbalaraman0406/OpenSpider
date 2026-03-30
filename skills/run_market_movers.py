import json
import sys
sys.path.insert(0, '.')
from market_movers import execute

results = execute({'category': 'all', 'limit': 15})

def fmt_vol(v):
    if not v: return 'N/A'
    if v >= 1e9: return f'{v/1e9:.2f}B'
    if v >= 1e6: return f'{v/1e6:.2f}M'
    if v >= 1e3: return f'{v/1e3:.1f}K'
    return str(v)

def fmt_mcap(v):
    if not v: return 'N/A'
    if v >= 1e12: return f'${v/1e12:.2f}T'
    if v >= 1e9: return f'${v/1e9:.2f}B'
    if v >= 1e6: return f'${v/1e6:.2f}M'
    return str(v)

print(f"**Timestamp:** {results.get('timestamp', 'N/A')}")
print(f"**Stocks Scanned:** {results.get('scanned', 'N/A')}")
print(f"\n{results.get('disclaimer', '')}")

# Indices
if 'indices' in results:
    print('\n## 📈 Major Indices')
    print('| Index | Price | Change % |')
    print('|-------|------:|--------:|')
    for idx in results['indices']:
        sign = '+' if idx['change_pct'] >= 0 else ''
        print(f"| {idx['index']} | {idx['price']:,.2f} | {sign}{idx['change_pct']:.2f}% |")

# Gainers
if 'top_gainers' in results:
    print('\n## 🟢 Top Gainers')
    print('| # | Ticker | Company Name | Price | Change | Change % | Volume | Market Cap |')
    print('|---|--------|-------------|------:|-------:|---------:|-------:|-----------:|')
    for i, s in enumerate(results['top_gainers'], 1):
        print(f"| {i} | **{s['ticker']}** | {s['name']} | ${s['price']:.2f} | ${s['change']:+.2f} | {s['change_pct']:+.2f}% | {fmt_vol(s['volume'])} | {fmt_mcap(s.get('market_cap'))} |")

# Losers
if 'top_losers' in results:
    print('\n## 🔴 Top Losers')
    print('| # | Ticker | Company Name | Price | Change | Change % | Volume | Market Cap |')
    print('|---|--------|-------------|------:|-------:|---------:|-------:|-----------:|')
    for i, s in enumerate(results['top_losers'], 1):
        print(f"| {i} | **{s['ticker']}** | {s['name']} | ${s['price']:.2f} | ${s['change']:+.2f} | {s['change_pct']:+.2f}% | {fmt_vol(s['volume'])} | {fmt_mcap(s.get('market_cap'))} |")

# Most Active
if 'most_active' in results:
    print('\n## 🔥 Most Active by Volume')
    print('| # | Ticker | Company Name | Price | Change | Change % | Volume | Market Cap |')
    print('|---|--------|-------------|------:|-------:|---------:|-------:|-----------:|')
    for i, s in enumerate(results['most_active'], 1):
        print(f"| {i} | **{s['ticker']}** | {s['name']} | ${s['price']:.2f} | ${s['change']:+.2f} | {s['change_pct']:+.2f}% | {fmt_vol(s['volume'])} | {fmt_mcap(s.get('market_cap'))} |")

# Also dump raw JSON for downstream use
with open('market_movers_raw.json', 'w') as f:
    json.dump(results, f, indent=2)
print('\n[Raw data saved to market_movers_raw.json]')

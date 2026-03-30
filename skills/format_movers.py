import json
import sys
sys.path.insert(0, '.')
from market_movers import execute

result = execute({'category': 'all', 'limit': 15})

def fmt_cap(v):
    if v >= 1e12: return f'${v/1e12:.2f}T'
    if v >= 1e9: return f'${v/1e9:.2f}B'
    if v >= 1e6: return f'${v/1e6:.0f}M'
    return f'${v:,.0f}'

def fmt_vol(v):
    if v >= 1e6: return f'{v/1e6:.1f}M'
    if v >= 1e3: return f'{v/1e3:.0f}K'
    return str(v)

def print_table(title, data):
    print(f'\n### {title}')
    print(f'| # | Ticker | Company | Price | Change ($) | Change (%) | Volume | Market Cap |')
    print(f'|---|--------|---------|-------|-----------|-----------|--------|-----------|')
    for i, s in enumerate(data, 1):
        chg = f"+${s['change']:.2f}" if s['change'] >= 0 else f"-${abs(s['change']):.2f}"
        pct = f"+{s['change_pct']:.2f}%" if s['change_pct'] >= 0 else f"{s['change_pct']:.2f}%"
        print(f"| {i} | **{s['ticker']}** | {s['name']} | ${s['price']:.2f} | {chg} | {pct} | {fmt_vol(s['volume'])} | {fmt_cap(s['market_cap'])} |")

print('## INDICES')
print('| Index | Price | Change (%) |')
print('|-------|-------|-----------|')
for idx in result.get('indices', []):
    pct = f"+{idx['change_pct']:.2f}%" if idx['change_pct'] >= 0 else f"{idx['change_pct']:.2f}%"
    print(f"| **{idx['index']}** | {idx['price']:,.2f} | {pct} |")

print_table('🟢 TOP GAINERS', result.get('top_gainers', []))
print_table('🔴 TOP LOSERS', result.get('top_losers', []))
print_table('📊 MOST ACTIVE BY VOLUME', result.get('most_active', []))

print(f'\n---')
print(f'Scanned: {result["scanned"]} tickers | Timestamp: {result["timestamp"]}')
print(f'{result["disclaimer"]}')

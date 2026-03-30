import json

with open('/Users/vbalaraman/OpenSpider/skills/market_movers_raw.json', 'r') as f:
    data = json.load(f)

print(f"Timestamp: {data['timestamp']}")
print(f"Stocks Scanned: {data['scanned']}")

for category in ['top_gainers', 'top_losers', 'most_active']:
    items = data.get(category, [])
    print(f"\n=== {category.upper()} ({len(items)} stocks) ===")
    for s in items:
        print(f"{s['ticker']}|{s['name']}|${s['price']}|{'+' if s['change']>=0 else ''}{s['change']}|{'+' if s.get('change_pct',0)>=0 else ''}{s.get('change_pct',0)}%|Vol:{s['volume']:,}|MCap:{s['market_cap']:,}")
